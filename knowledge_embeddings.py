# knowledge_embeddings.py

import os
import json
import numpy as np
import faiss
import sys
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import (
    OPENAI_API_KEY,
    KNOWLEDGE_CHUNKS_PATH,
    KNOWLEDGE_INDEX_PATH,
    CONDITIONS_PATH,
    TOP_K_RESULTS
)

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Розбиття тексту на чанки --- #
def split_into_chunks(text):
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]

# --- Валідація тексту перед ембедінгом --- #
def is_valid_text(t):
    return isinstance(t, str) and t.strip() and len(t.encode("utf-8")) <= 20000

# --- Генерація ембедінгів для списку текстів --- #
def embed_texts(texts):
    if not texts:
        return []

    embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            for item in response.data:
                vec = np.array(item.embedding, dtype=np.float32)
                if vec.shape[0] == 1536:
                    embeddings.append(vec)
                else:
                    print("⚠️ Невірна розмірність ембедінга — записано нульовий вектор.")
                    embeddings.append(np.zeros((1536,), dtype=np.float32))
        except Exception as e:
            print(f"❌ Помилка в embed_texts: {e}")
            embeddings.extend([np.zeros((1536,), dtype=np.float32)] * len(batch))

    return embeddings

# --- Ембедінг одного запиту --- #
def embed_text(text):
    result = embed_texts([text])
    return result[0] if result else np.zeros((1536,), dtype=np.float32)

# --- Пошук релевантного знання --- #
def search_combined_context(query):
    try:
        q_vec = embed_text(query)
        index = faiss.read_index(KNOWLEDGE_INDEX_PATH)

        D, I = index.search(np.array([q_vec]), TOP_K_RESULTS)

        with open(KNOWLEDGE_CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        return [chunks[i] for i in I[0] if i < len(chunks)]
    except Exception as e:
        print(f"❌ Помилка під час пошуку знань: {e}")
        return []

# --- Побудова індексу знань --- #
def main():
    print("📚 Побудова векторного індексу для CONDITIONS...")

    if not os.path.exists(CONDITIONS_PATH):
        print(f"❌ Файл {CONDITIONS_PATH} не знайдено.")
        return

    with open(CONDITIONS_PATH, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        print("⚠️ Файл умов порожній — немає що обробляти.")
        return

    chunks = split_into_chunks(raw)
    valid_chunks = [c for c in chunks if is_valid_text(c)]

    if not valid_chunks:
        print("⚠️ Немає валідних чанків для індексації.")
        return

    embeddings = embed_texts(valid_chunks)
    if not embeddings:
        print("❌ Не вдалося згенерувати ембедінги.")
        return

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    enriched_chunks = [{"text": chunk} for chunk in valid_chunks]
    with open(KNOWLEDGE_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_chunks, f, ensure_ascii=False, indent=2)

    faiss.write_index(index, KNOWLEDGE_INDEX_PATH)

    print(f"✅ Збережено {len(valid_chunks)} знань у {KNOWLEDGE_INDEX_PATH}")

# --- Точка входу --- #
if __name__ == "__main__":
    main()
