# build_dialog_index.py

import os
import json
import numpy as np
import faiss
from openai import OpenAI
from config import (
    OPENAI_API_KEY,
    DIALOG_CHUNKS_PATH,
    DIALOG_INDEX_PATH,
    REAL_DIALOGS_PATH
)

# === 🔐 Ініціалізація клієнта OpenAI ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Розбиття діалогу на фрагменти по 2–4 репліки ===
def split_dialog_into_chunks(dialog: str, min_len=2, max_len=4):
    lines = [line.strip() for line in dialog.splitlines() if line.strip()]
    chunks = []
    for i in range(0, len(lines) - min_len + 1):
        chunk = lines[i:i + max_len]
        if len(chunk) >= min_len:
            chunks.append("\n".join(chunk))
    return chunks

# === Генерація ембедінгів ===
def embed_texts(texts):
    if not texts:
        return []
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [np.array(item.embedding, dtype=np.float32) for item in response.data]
    except Exception as e:
        print(f"❌ Помилка під час створення ембедінгів: {e}")
        return [np.zeros((1536,), dtype=np.float32) for _ in texts]

# === Завантаження реальних діалогів ===
def load_real_dialogs(path):
    if not os.path.exists(path):
        print(f"❌ Файл {path} не знайдено.")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        return [d.strip() for d in raw.split("\n\n") if d.strip()]
    except Exception as e:
        print(f"❌ Помилка при зчитуванні {path}: {e}")
        return []

# === Основна функція ===
def main():
    dialogs = load_real_dialogs(REAL_DIALOGS_PATH)
    if not dialogs:
        print("⚠️ Немає валідних діалогів для обробки.")
        return

    all_chunks = []
    for dialog in dialogs:
        chunks = split_dialog_into_chunks(dialog)
        all_chunks.extend(chunks)

    all_chunks = [chunk for chunk in all_chunks if len(chunk.strip()) > 0]

    if not all_chunks:
        print("⚠️ Усі фрагменти пусті або невалідні.")
        return

    embeddings = embed_texts(all_chunks)
    if not embeddings or any(e.shape[0] == 0 for e in embeddings):
        print("❌ Помилка: не вдалося створити валідні ембедінги.")
        return

    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype=np.float32))

    with open(DIALOG_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump([{"text": chunk} for chunk in all_chunks], f, ensure_ascii=False, indent=2)

    faiss.write_index(index, DIALOG_INDEX_PATH)
    print(f"✅ Індекс з {len(all_chunks)} діалогів збережено → {DIALOG_INDEX_PATH}")

# === Запуск як скрипта ===
if __name__ == "__main__":
    main()
