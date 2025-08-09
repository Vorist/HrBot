# trainer/learner.py

import os
import sys
import json
import hashlib
from typing import List, Dict, Optional

import numpy as np

# доступ к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    GOOD_DIALOGS_PATH,
    BAD_DIALOGS_PATH,
    REAL_DIALOGS_PATH,
    TRAINING_OUTPUT_PATH,
    FEEDBACK_COMMENTS_PATH,
)
from utils import split_dialog_into_chunks, log
from trainer.feedback_processor import extract_feedback_insights
from trainer.strategy_refiner import refine_bad_dialogs
from trainer.real_dialog_loader import load_real_dialogs_from_txt

# Эмбеддеры: батчевый предпочтительнее; если нет — падаем на поштучный
try:
    from knowledge_embeddings import embed_texts as _embed_batch  # type: ignore
except Exception:
    _embed_batch = None
from knowledge_embeddings import embed_text as _embed_single  # type: ignore


# --------- вспомогательные ------------

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _dialog_obj_to_lines(dialog_obj: Dict) -> List[str]:
    """
    Преобразует {"dialog":[{"role":"user"|"bot","text":"..."}]}
    -> список строк с эмодзи-ролями.
    """
    out: List[str] = []
    for x in dialog_obj.get("dialog", []):
        if isinstance(x, dict) and "role" in x and "text" in x and x["text"]:
            if x["role"] == "bot":
                out.append(f"🤖 {x['text']}")
            else:
                out.append(f"👤 {x['text']}")
    return out


def _load_text_dialogs_jsonl(path: str) -> List[str]:
    """
    Загружает диалоги из JSONL:
    - старый формат: {"text": "..."}
    - новый: {"dialog":[{"role":...,"text":...}, ...]}
    Возвращает список цельных диалогов (строк), разделённых \n.
    """
    if not os.path.exists(path):
        return []

    dialogs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    continue
                if "dialog" in obj and isinstance(obj["dialog"], list):
                    lines = _dialog_obj_to_lines(obj)
                    if lines:
                        dialogs.append("\n".join(lines))
                elif isinstance(obj.get("text"), str) and obj["text"].strip():
                    dialogs.append(obj["text"].strip())
            except Exception:
                # тихо пропускаем битые строки
                continue
    return dialogs


def _collect_all_chunks(
    dialogs_from_real: Optional[List[Dict]] = None,
) -> List[Dict]:
    """
    Собирает все чанки из good/bad/real/feedback/refined в единый список:
    каждый элемент: {"text": "...", "label": "good|bad|real|feedback|refined"}.
    """
    combined: List[Dict] = []

    # --- good / bad ---
    for text in _load_text_dialogs_jsonl(GOOD_DIALOGS_PATH):
        combined.extend(split_dialog_into_chunks(text, label="good"))
    for text in _load_text_dialogs_jsonl(BAD_DIALOGS_PATH):
        combined.extend(split_dialog_into_chunks(text, label="bad"))

    # --- real ---
    if dialogs_from_real is None:
        real_dialogs = load_real_dialogs_from_txt(REAL_DIALOGS_PATH, preview=False)
    else:
        real_dialogs = dialogs_from_real

    for obj in real_dialogs:
        lines = _dialog_obj_to_lines(obj)
        if lines:
            combined.extend(split_dialog_into_chunks("\n".join(lines), label="real"))

    # --- feedback -> рекомендации как отдельные чанки ---
    if os.path.exists(FEEDBACK_COMMENTS_PATH):
        try:
            with open(FEEDBACK_COMMENTS_PATH, "r", encoding="utf-8") as f:
                entries = [json.loads(l) for l in f if l.strip()]
            for fb in extract_feedback_insights(entries):
                rec = (fb.get("recommendation") or "").strip()
                if rec:
                    combined.append({"text": rec, "label": "feedback"})
        except Exception as e:
            log(f"⚠️ Не вдалося прочитати коментарі: {e}")

    # --- refined bad ---
    try:
        refined = refine_bad_dialogs()
        for item in refined:
            improved = item.get("improved", "")
            if isinstance(improved, dict):
                improved = improved.get("text", "")
            improved = (improved or "").strip()
            if improved:
                combined.append({"text": improved, "label": "refined"})
    except Exception as e:
        log(f"⚠️ Не вдалося покращити погані відповіді: {e}")

    return combined


def _deduplicate_chunks(chunks: List[Dict], max_keep: Optional[int] = None) -> List[Dict]:
    """
    Дедуп по (label + text). Можно ограничить общий объём max_keep (env MAX_TRAIN_CHUNKS).
    """
    seen = set()
    out: List[Dict] = []
    for ch in chunks:
        text = (ch.get("text") or "").strip()
        label = ch.get("label", "unknown")
        if not text:
            continue
        h = _sha256(f"{label}|||{text}")
        if h in seen:
            continue
        seen.add(h)
        out.append({"text": text, "label": label})
        if max_keep and len(out) >= max_keep:
            break
    return out


def _embed_many(texts: List[str]) -> List[np.ndarray]:
    """
    Пытаемся эмбеддить батчами; если батчевый эмбеддер недоступен — поштучно.
    Возвращаем список numpy-векторов одинаковой размерности.
    """
    vectors: List[np.ndarray] = []

    if _embed_batch is not None:
        try:
            # батч одной порцией (если нужно — можно разбить на чанки по 256)
            batch_vecs = _embed_batch(texts)
            # ожидаем List[np.array]
            for v in batch_vecs:
                if isinstance(v, np.ndarray) and v.size > 0:
                    vectors.append(v)
                else:
                    vectors.append(np.zeros((1536,), dtype=np.float32))
            return vectors
        except Exception as e:
            log(f"⚠️ batch-embedding failed, fallback to single: {e}")

    # fallback — по одному
    for t in texts:
        try:
            v = _embed_single(t)
            if isinstance(v, np.ndarray) and v.size > 0:
                vectors.append(v)
            else:
                vectors.append(np.zeros((1536,), dtype=np.float32))
        except Exception:
            vectors.append(np.zeros((1536,), dtype=np.float32))

    return vectors


# --------- основная функция ------------

def learn_from_dialogs(dialogs_from_real: Optional[List[Dict]] = None) -> None:
    log("[📚] Навчання на основі good, bad, real, feedback, refined...")

    # 1) собираем
    combined_chunks = _collect_all_chunks(dialogs_from_real)

    # 2) дедуп + ограничение объёма (если нужно)
    max_keep_env = os.getenv("MAX_TRAIN_CHUNKS", "").strip()
    max_keep = int(max_keep_env) if max_keep_env.isdigit() else None
    unique_chunks = _deduplicate_chunks(combined_chunks, max_keep=max_keep)

    if not unique_chunks:
        log("⚠️ Порожній набір чанків після дедуплікації — нічого тренувати.")
        # всё равно создадим пустой файл, чтобы пайплайн не падал
        os.makedirs(os.path.dirname(TRAINING_OUTPUT_PATH), exist_ok=True)
        with open(TRAINING_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    # 3) эмбеддинг
    texts = [c["text"] for c in unique_chunks]
    vectors = _embed_many(texts)

    # 4) финальный пакет
    embedded = []
    for chunk, vec in zip(unique_chunks, vectors):
        if isinstance(vec, np.ndarray) and vec.size > 0:
            embedded.append({
                "text": chunk["text"],
                "label": chunk["label"],
                "vector": vec.tolist(),
            })

    # 5) сохранение
    os.makedirs(os.path.dirname(TRAINING_OUTPUT_PATH), exist_ok=True)
    with open(TRAINING_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded, f, ensure_ascii=False, indent=2)

    log(f"✅ Навчання завершено: {len(embedded)} ембедінгів збережено → {TRAINING_OUTPUT_PATH}")


if __name__ == "__main__":
    # обычный путь: real-диалоги берём из файла; можно передать список диалогов-объектов вручную
    learn_from_dialogs()
