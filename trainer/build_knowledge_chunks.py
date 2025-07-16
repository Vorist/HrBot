# build_knowledge_chunks.py

import os
import sys
import json
import numpy as np
import faiss
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import (
    CONDITIONS_PATH,
    FREQUENT_QUESTIONS_PATH,
    KNOWLEDGE_CHUNKS_PATH,
    KNOWLEDGE_INDEX_PATH,
    OPENAI_API_KEY,
)

client = OpenAI(api_key=OPENAI_API_KEY)

# === 🔐 Безпечний print (для emoji і юнікоду) ===
def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode())


# === 📚 Розбиття на чанки ===
def split_into_chunks(text, max_tokens=500):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current + para) > max_tokens:
            chunks.append(current.strip())
            current = para + "\n\n"
        else:
            current += para + "\n\n"
    if current:
        chunks.append(current.strip())
    return chunks


# === 🧽 Форматування тексту ===
def format_text(text):
    return text.replace("\n\n", "\n").strip()


# === 🧠 Генерація ембедінгів ===
def embed_texts(texts):
    if not texts:
        return []
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [np.array(obj.embedding, dtype=np.float32) for obj in response.data]
    except Exception as e:
        safe_print(f"❌ Помилка створення ембедінгів: {e}")
        return [np.zeros((1536,), dtype=np.float32) for _ in texts]


# === 📄 Завантаження умов ===
def load_conditions():
    if not os.path.exists(CONDITIONS_PATH):
        safe_print(f"❌ Не знайдено файл: {CONDITIONS_PATH}")
        return []
    try:
        with open(CONDITIONS_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
        return [{"type": "condition", "text": chunk} for chunk in split_into_chunks(text)]
    except Exception as e:
        safe_print(f"❌ Помилка читання умов: {e}")
        return []


# === ❓ Завантаження частих питань ===
def load_frequent_questions():
    if not os.path.exists(FREQUENT_QUESTIONS_PATH):
        safe_print(f"⚠️ Не знайдено файл: {FREQUENT_QUESTIONS_PATH}")
        return []
    try:
        with open(FREQUENT_QUESTIONS_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict):
            cleaned = {
                str(k): int(v) if isinstance(v, int) or str(v).isdigit() else 0
                for k, v in raw.items()
            }
            sorted_items = sorted(cleaned.items(), key=lambda x: x[1], reverse=True)
            data = [{"question": q, "answer": ""} for q, _ in sorted_items]
            with open(FREQUENT_QUESTIONS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif isinstance(raw, list):
            data = raw
        else:
            safe_print("⚠️ Формат frequent_questions.json не підтримується.")
            return []

        return [{
            "type": "faq",
            "text": format_text(f"❓ {item['question']}\n💬 {item.get('answer', '')}")
        } for item in data if "question" in item]

    except Exception as e:
        safe_print(f"❌ Помилка обробки {FREQUENT_QUESTIONS_PATH}: {e}")
        return []


# === 🔧 Побудова знань ===
def build_knowledge_chunks():
    chunks = load_conditions() + load_frequent_questions()
    safe_print(f"📥 Отримано {len(chunks)} фрагментів знань.")

    texts = [item["text"] for item in chunks]
    embeddings = embed_texts(texts)

    valid_chunks = []
    for chunk, vector in zip(chunks, embeddings):
        if isinstance(vector, np.ndarray) and vector.shape[0] == 1536:
            valid_chunks.append({**chunk, "vector": vector.tolist()})
        else:
            safe_print("⚠️ Пропущено chunk: некоректна розмірність ембедінгу")

    if not valid_chunks:
        safe_print("❌ Жодного валідного фрагменту для збереження.")
        return

    os.makedirs(os.path.dirname(KNOWLEDGE_CHUNKS_PATH), exist_ok=True)
    with open(KNOWLEDGE_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(valid_chunks, f, ensure_ascii=False, indent=2)

    dim = len(valid_chunks[0]["vector"])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array([chunk["vector"] for chunk in valid_chunks], dtype=np.float32))
    faiss.write_index(index, KNOWLEDGE_INDEX_PATH)

    safe_print(f"✅ Збережено {len(valid_chunks)} знань → {KNOWLEDGE_INDEX_PATH}")


# === ▶️ Точка входу ===
if __name__ == "__main__":
    build_knowledge_chunks()
