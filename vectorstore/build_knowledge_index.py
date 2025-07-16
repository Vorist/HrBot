# build_knowledge_index.py

import os
import json
import numpy as np
import faiss
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import KNOWLEDGE_CHUNKS_PATH, KNOWLEDGE_INDEX_PATH

def build_index():
    if not os.path.exists(KNOWLEDGE_CHUNKS_PATH):
        print(f"❌ Файл знань не знайдено: {KNOWLEDGE_CHUNKS_PATH}")
        return

    try:
        with open(KNOWLEDGE_CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Помилка при зчитуванні JSON: {e}")
        return

    vectors = []
    for i, chunk in enumerate(chunks):
        vec = chunk.get("vector")
        if not isinstance(vec, list) or not vec:
            print(f"⚠️ Chunk #{i} не містить валідного вектору.")
            continue
        try:
            arr = np.array(vec, dtype=np.float32)
            if arr.ndim != 1:
                raise ValueError("Очікується 1-вимірний вектор")
            vectors.append(arr)
        except Exception as e:
            print(f"❌ Помилка при конвертації chunk #{i}: {e}")

    if not vectors:
        print("❌ Жодного валідного вектору не знайдено для індексації.")
        return

    dim = vectors[0].shape[0]
    if not all(vec.shape[0] == dim for vec in vectors):
        print("❌ У векторів різна розмірність — не можна створити індекс.")
        return

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors))

    os.makedirs(os.path.dirname(KNOWLEDGE_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, KNOWLEDGE_INDEX_PATH)

    print(f"✅ Успішно збережено FAISS-індекс з {len(vectors)} знань → {KNOWLEDGE_INDEX_PATH}")

if __name__ == "__main__":
    build_index()
