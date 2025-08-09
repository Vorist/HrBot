# trainer/build_knowledge_chunks.py

import os
import sys
import json
from typing import List, Dict, Any
import numpy as np
import faiss
from openai import OpenAI

# --- sys.path, чтобы скрипт стабильно видел корень проекта ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    CONDITIONS_PATH,
    FREQUENT_QUESTIONS_PUBLIC_PATH,   # читаем только public
    KNOWLEDGE_CHUNKS_PATH,
    KNOWLEDGE_INDEX_PATH,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,                  # берём из конфига
)

# =========================
#        УТИЛИТЫ
# =========================

def safe_print(message: str):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode())

def split_into_chunks(text: str, max_chars: int = 2000) -> List[str]:
    """
    Грубое порционное разбиение по абзацам, чтобы не кормить слишком длинные куски.
    max_chars — по символам (без токенайзера).
    """
    paragraphs = [p.strip() for p in text.split("\n\n")]
    chunks, current = [], ""
    for para in paragraphs:
        # +2 за добавляемые \n\n при склейке
        if len(current) + len(para) + 2 > max_chars:
            if current.strip():
                chunks.append(current.strip())
            current = para
        else:
            current = (current + "\n\n" + para).strip() if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks

def format_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\n\n", "\n").strip()

def batched(iterable: List[str], n: int):
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]

# =========================
#     OPENAI КЛИЕНТ
# =========================

if not OPENAI_API_KEY:
    safe_print("⚠️ OPENAI_API_KEY не задан — ембеддинги не будут созданы.")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def embed_texts(texts: List[str], batch_size: int = 64) -> List[np.ndarray]:
    """
    Батчим запросы к embeddings API.
    При ошибке — возвращаем нулевые векторы нужной размерности после первой удачной партии.
    """
    if not texts:
        return []

    if client is None:
        # вернём нули «условного» размера — определим позже, но начнём с 1536
        return [np.zeros((1536,), dtype=np.float32) for _ in texts]

    vectors: List[np.ndarray] = []
    dim_detected: int | None = None

    for chunk in batched(texts, batch_size):
        try:
            resp = client.embeddings.create(model=EMBEDDING_MODEL, input=chunk)
            batch_vecs = [np.array(obj.embedding, dtype=np.float32) for obj in resp.data]
            if batch_vecs and dim_detected is None:
                dim_detected = int(batch_vecs[0].shape[0])
            vectors.extend(batch_vecs)
        except Exception as e:
            safe_print(f"❌ Помилка створення ембедінгів (offset {len(vectors)}): {e}")
            dim = dim_detected or 1536
            vectors.extend([np.zeros((dim,), dtype=np.float32) for _ in chunk])

    return vectors

# =========================
#       ИСТОЧНИКИ
# =========================

def load_conditions() -> List[Dict[str, Any]]:
    if not os.path.exists(CONDITIONS_PATH):
        safe_print(f"❌ Не знайдено файл: {CONDITIONS_PATH}")
        return []
    try:
        with open(CONDITIONS_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
        return [{"type": "condition", "text": c} for c in split_into_chunks(text)]
    except Exception as e:
        safe_print(f"❌ Помилка читання умов: {e}")
        return []

def load_frequent_questions() -> List[Dict[str, Any]]:
    """
    Читаем только public-файл (списком).
    НИЧЕГО НЕ ПЕРЕЗАПИСЫВАЕМ.
    Поддерживаем аварийный случай, если вдруг там dict — конвертируем в list ТОЛЬКО в памяти.
    """
    path = FREQUENT_QUESTIONS_PUBLIC_PATH
    if not os.path.exists(path):
        safe_print(f"⚠️ Не знайдено файл: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, list):
            data = raw
        elif isinstance(raw, dict):
            # аварийная поддержка старого формата — только в памяти
            cleaned = {
                str(k): int(v) if isinstance(v, int) or (isinstance(v, str) and v.isdigit()) else 0
                for k, v in raw.items()
            }
            sorted_items = sorted(cleaned.items(), key=lambda x: x[1], reverse=True)
            data = [{"question": q, "answer": ""} for q, _ in sorted_items]
        else:
            safe_print("⚠️ frequent_questions (public) має невідомий формат — пропускаємо.")
            return []

        items = []
        for item in data:
            if not isinstance(item, dict):
                continue
            q = format_text(str(item.get("question", "")).strip())
            a = format_text(str(item.get("answer", "")).strip())
            if q:
                items.append({
                    "type": "faq",
                    "text": format_text(f"❓ {q}\n💬 {a}") if a else f"❓ {q}"
                })
        return items

    except Exception as e:
        safe_print(f"❌ Помилка обробки {path}: {e}")
        return []

# =========================
#       ПОСТРОЕНИЕ
# =========================

def build_knowledge_chunks():
    # собираем «знания»
    source_chunks = load_conditions() + load_frequent_questions()
    safe_print(f"📥 Отримано {len(source_chunks)} фрагментів знань (до дедуплікації).")

    # дедуп по полю text
    seen = set()
    uniq_chunks: List[Dict[str, Any]] = []
    for item in source_chunks:
        t = item.get("text", "").strip()
        if not t or t in seen:
            continue
        seen.add(t)
        uniq_chunks.append(item)

    safe_print(f"🧹 Після дедуплікації: {len(uniq_chunks)} фрагментів.")

    if not uniq_chunks:
        safe_print("❌ Немає валідних фрагментів для ембеддингу.")
        return

    batch_size = int(os.getenv("EMBED_BATCH", "64"))
    texts = [it["text"] for it in uniq_chunks]
    embeddings = embed_texts(texts, batch_size=batch_size)

    # отфильтруем те, у кого вектор пустой
    enriched: List[Dict[str, Any]] = []
    for item, vec in zip(uniq_chunks, embeddings):
        if isinstance(vec, np.ndarray) and vec.size > 0 and vec.any():
            item_with_vec = dict(item)
            item_with_vec["vector"] = vec.tolist()
            enriched.append(item_with_vec)
        else:
            safe_print("⚠️ Пропущено chunk: порожній або нульовий ембедінг")

    if not enriched:
        safe_print("❌ Жодного валідного фрагменту для збереження.")
        return

    os.makedirs(os.path.dirname(KNOWLEDGE_CHUNKS_PATH), exist_ok=True)
    with open(KNOWLEDGE_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    # размерность — из первого валидного вектора
    dim = len(enriched[0]["vector"])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array([c["vector"] for c in enriched], dtype=np.float32))
    faiss.write_index(index, KNOWLEDGE_INDEX_PATH)

    safe_print(f"✅ Збережено {len(enriched)} знань → {KNOWLEDGE_INDEX_PATH}")

# =========================
#        ENTRYPOINT
# =========================

if __name__ == "__main__":
    build_knowledge_chunks()
