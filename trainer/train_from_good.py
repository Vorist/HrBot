import os
import json
import faiss
import numpy as np
from hashlib import sha256
from datetime import datetime
import sys

# Подключаем корень проекта для всех импортов
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    GOOD_DIALOGS_PATH,
    GOOD_INDEX_PATH,
    GOOD_DIALOG_CHUNKS_PATH,
    EMBED_CACHE_PATH,
    FEEDBACK_LESSONS_PATH,
    LOG_PATH,
)
from utils import log, split_dialog_into_chunks
from knowledge_embeddings import embed_texts

def log_to_file(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")
    print(full_message)

def load_embed_cache():
    if os.path.exists(EMBED_CACHE_PATH):
        try:
            with open(EMBED_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_embed_cache(cache):
    try:
        with open(EMBED_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_to_file(f"❌ Не вдалося зберегти кеш ембедінгів: {e}")

def load_feedback_lessons():
    if not os.path.exists(FEEDBACK_LESSONS_PATH):
        return []
    try:
        with open(FEEDBACK_LESSONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_to_file(f"⚠️ Помилка читання feedback_lessons: {e}")
        return []

def apply_feedback(chunk, feedback_lessons):
    text = chunk.get("text", "").lower()
    for lesson in feedback_lessons:
        if lesson.get("pattern") and lesson["pattern"].lower() in text:
            chunk["feedback"] = lesson.get("recommendation", "")
            break
    return chunk

def dialog_to_text(dialog):
    """Склеивает весь диалог в текст для разбивки на чанки"""
    return "\n".join([
        f"{'👤' if m['role'] == 'user' else '🤖'} {m['text']}".strip()
        for m in dialog if 'role' in m and 'text' in m
    ])

def train_on_good_dialogs():
    log_to_file("🌟 Старт навчання на GOOD діалогах...")

    if not os.path.exists(GOOD_DIALOGS_PATH):
        log_to_file(f"❌ Файл {GOOD_DIALOGS_PATH} не знайдено.")
        return

    feedback_lessons = load_feedback_lessons()
    cache = load_embed_cache()
    all_chunks = []
    hashes_seen = set()

    with open(GOOD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                dialog = obj.get("dialog")
                if isinstance(dialog, list):
                    full_text = dialog_to_text(dialog)
                    chunks = split_dialog_into_chunks(full_text, label="good")
                    for chunk in chunks:
                        h = sha256(chunk["text"].encode("utf-8")).hexdigest()
                        if h not in hashes_seen:
                            hashes_seen.add(h)
                            chunk["hash"] = h
                            chunk = apply_feedback(chunk, feedback_lessons)
                            all_chunks.append(chunk)
            except Exception as e:
                log_to_file(f"⚠️ Пропущено рядок через помилку: {e}")
                continue

    if not all_chunks:
        log_to_file("⚠️ Жодного валідного чанка не знайдено.")
        return

    log_to_file(f"🔢 Обробка {len(all_chunks)} good-чанків...")

    texts = [c["text"] for c in all_chunks]
    embeddings = []
    new_cache = dict(cache)

    for i, text in enumerate(texts):
        h = sha256(text.encode("utf-8")).hexdigest()
        if h in cache:
            emb = cache[h]
        else:
            emb = embed_texts([text])[0].tolist()
        embeddings.append(emb)
        new_cache[h] = emb

    save_embed_cache(new_cache)

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype=np.float32))
    faiss.write_index(index, GOOD_INDEX_PATH)
    log_to_file(f"✅ Збережено FAISS-індекс → {GOOD_INDEX_PATH} ({len(embeddings)} фрагментів)")

    try:
        with open(GOOD_DIALOG_CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        log_to_file(f"📁 Збережено чанки → {GOOD_DIALOG_CHUNKS_PATH}")
    except Exception as e:
        log_to_file(f"❌ Помилка збереження чанків: {e}")

if __name__ == "__main__":
    train_on_good_dialogs()
