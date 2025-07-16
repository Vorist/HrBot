# build_good_index.py

import os
import json
import numpy as np
import faiss
import sys
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import OPENAI_API_KEY, GOOD_DIALOGS_PATH, GOOD_INDEX_PATH

# --- 🔑 Ініціалізація OpenAI-клієнта ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 📥 Завантаження good-фрагментів ---
def load_good_chunks():
    if not os.path.exists(GOOD_DIALOGS_PATH):
        print(f"❌ Файл не знайдено: {GOOD_DIALOGS_PATH}")
        return []

    chunks = []
    with open(GOOD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                text = item.get("text", "").strip()
                if text:
                    chunks.append(text)
            except json.JSONDecodeError:
                print(f"⚠️ Некоректний JSON у рядку {i}")
    return chunks

# --- 🧠 Створення ембедінгів ---
def embed_texts(texts):
    try:
        print(f"📡 Генеруємо embedding-и для {len(texts)} good-фрагментів...")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        vectors = []
        for i, rec in enumerate(response.data):
            vec = np.array(rec.embedding, dtype=np.float32)
            if vec.shape[0] == 1536:
                vectors.append(vec)
            else:
                print(f"⚠️ Ембедінг {i+1} має некоректну розмірність — пропущено")
        return vectors
    except Exception as e:
        print(f"❌ Помилка генерації ембедінгів: {e}")
        return []

# --- 🧱 Побудова FAISS-індексу ---
def build_good_index():
    texts = load_good_chunks()
    if not texts:
        print("⚠️ Немає валідних good-фрагментів.")
        return

    embeddings = embed_texts(texts)
    if not embeddings:
        print("⚠️ Не вдалося створити ембедінги.")
        return

    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    os.makedirs(os.path.dirname(GOOD_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, GOOD_INDEX_PATH)
    print(f"✅ Збережено індекс з {len(embeddings)} good-фрагментів → {GOOD_INDEX_PATH}")

# --- 🚀 Запуск ---
if __name__ == "__main__":
    build_good_index()
