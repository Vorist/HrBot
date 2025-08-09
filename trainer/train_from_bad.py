import os
import json
import faiss
import numpy as np
import sys
from hashlib import sha256
from datetime import datetime

# Добавляем корень проекта для корректных импортов
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    BAD_DIALOGS_PATH,
    BAD_INDEX_PATH,
    BAD_DIALOG_CHUNKS_PATH,
    EMBED_CACHE_PATH,
    LOG_PATH,
)
from utils import split_dialog_into_chunks, log
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

def dialog_to_text(dialog):
    """Преобразует структуру диалога из BAD_DIALOGS_PATH в многострочный текст для чанков."""
    return "\n".join([
        f"{'👤' if m['role'] == 'user' else '🤖'} {m['text']}".strip()
        for m in dialog if 'role' in m and 'text' in m
    ])

def train_on_bad_dialogs():
    log_to_file("🚫 Старт навчання на BAD діалогах...")

    if not os.path.exists(BAD_DIALOGS_PATH):
        log_to_file(f"❌ Файл {BAD_DIALOGS_PATH} не знайдено.")
        return

    cache = load_embed_cache()
    all_chunks = []
    hashes_seen = set()

    with open(BAD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                dialog = obj.get("dialog")
                if isinstance(dialog, list):
                    full_text = dialog_to_text(dialog)
                    chunks = split_dialog_into_chunks(full_text, label="bad")
                    for chunk in chunks:
                        h = sha256(chunk["text"].encode("utf-8")).hexdigest()
                        if h not in hashes_seen:
                            hashes_seen.add(h)
                            chunk["hash"] = h
                            all_chunks.append(chunk)
            except Exception as e:
                log_to_file(f"⚠️ Пропущено рядок через помилку: {e}")
                continue

    if not all_chunks:
        log_to_file("⚠️ Жодного валідного чанка не знайдено.")
        return

    log_to_file(f"🔢 Обробка {len(all_chunks)} bad-чанків...")

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

    # --- FAISS --- #
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype=np.float32))
    faiss.write_index(index, BAD_INDEX_PATH)
    log_to_file(f"✅ Збережено FAISS-індекс з {len(embeddings)} BAD-фрагментів → {BAD_INDEX_PATH}")

    # --- Збереження чанків --- #
    try:
        with open(BAD_DIALOG_CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        log_to_file(f"📁 Збережено чанки → {BAD_DIALOG_CHUNKS_PATH}")
    except Exception as e:
        log_to_file(f"❌ Помилка збереження чанків: {e}")

if __name__ == "__main__":
    train_on_bad_dialogs()
