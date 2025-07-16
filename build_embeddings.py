# build_embeddings.py

import os
import json
import numpy as np
import faiss
from openai import OpenAI
from config import (
    OPENAI_API_KEY,
    CONDITIONS_PATH,
    KNOWLEDGE_CHUNKS_PATH,
    KNOWLEDGE_INDEX_PATH
)

# === Ініціалізація OpenAI клієнта ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Розбивка тексту на чанки ===
def split_into_chunks(text, max_chars=1000):
    paragraphs = text.split("\n\n")
    chunks, current = [], ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current + para) > max_chars:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"
        else:
            current += para + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks

# === Генерація ембедінгів ===
def embed_texts(texts):
    if not texts:
        return []

    embeddings = []
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        for item in response.data:
            vec = np.array(item.embedding, dtype=np.float32)
            if vec.shape[0] == 1536:
                embeddings.append(vec)
            else:
                print("⚠️ Некоректна довжина ембедінга, додаю zero-вектор.")
                embeddings.append(np.zeros((1536,), dtype=np.float32))
    except Exception as e:
        print(f"❌ Помилка під час отримання ембедінгів: {e}")
        embeddings = [np.zeros((1536,), dtype=np.float32) for _ in texts]

    return embeddings

# === Основна логіка ===
def main():
    print("📚 Створення embedding-індексу з файлу умов...")

    if not os.path.exists(CONDITIONS_PATH):
        print(f"❌ Файл умов не знайдено: {CONDITIONS_PATH}")
        return

    with open(CONDITIONS_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    if not raw_text:
        print("⚠️ Файл умов порожній!")
        return

    chunks = split_into_chunks(raw_text)
    if not chunks:
        print("❌ Не знайдено жодного валідного чанку.")
        return

    embeddings = embed_texts(chunks)
    if not embeddings or any(e.shape[0] == 0 for e in embeddings):
        print("❌ Не вдалося створити валідні ембедінги.")
        return

    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(np.array(embeddings, dtype=np.float32))

    with open(KNOWLEDGE_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump([{"text": chunk} for chunk in chunks], f, ensure_ascii=False, indent=2)

    faiss.write_index(index, KNOWLEDGE_INDEX_PATH)

    print(f"✅ Збережено {len(chunks)} знань у {KNOWLEDGE_INDEX_PATH}")

# === Запуск ===
if __name__ == "__main__":
    main()
