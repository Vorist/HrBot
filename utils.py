import json
import random
import numpy as np
import faiss
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import (
    SYSTEM_PROMPT_PATH,
    GOOD_DIALOGS_PATH,
    GOOD_INDEX_PATH,
    BAD_DIALOGS_PATH,
    BAD_INDEX_PATH,
    FEEDBACK_LESSONS_PATH,
    DIALOG_CHUNKS_PATH,
    REAL_INDEX_PATH,
    REAL_DIALOGS_TXT_PATH
)
from dialog_memory import get_history
from openai import OpenAI
from log import log
from scripts.convert_real_dialogs import load_real_dialogs_from_txt

client = OpenAI()

# --- 🧠 Завантаження системного промпту ---
with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# --- ✅ GOOD приклади ---
try:
    with open(GOOD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        good_chunks = [json.loads(line) for line in f if line.strip()]
    good_index = faiss.read_index(GOOD_INDEX_PATH)
    good_texts = [chunk["text"] for chunk in good_chunks if "text" in chunk]
except Exception as e:
    print(f"⚠️ Не вдалося завантажити good_dialogs: {e}")
    good_index = None
    good_texts = []

# --- ❌ BAD приклади ---
try:
    with open(BAD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        bad_chunks = [json.loads(line) for line in f if line.strip()]
    bad_index = faiss.read_index(BAD_INDEX_PATH)
    bad_texts = [chunk["text"] for chunk in bad_chunks if "text" in chunk]
except Exception as e:
    print(f"⚠️ Не вдалося завантажити bad_dialogs: {e}")
    bad_index = None
    bad_texts = []

# --- 📘 Уроки з фідбеку ---
try:
    with open(FEEDBACK_LESSONS_PATH, "r", encoding="utf-8") as f:
        feedback_lessons = json.load(f)
except Exception:
    feedback_lessons = []

# --- 🎯 Реальні діалоги (з txt напряму) ---
try:
    raw_texts = load_real_dialogs_from_txt(REAL_DIALOGS_TXT_PATH)

    # 🔍 Очищення: залишаємо лише непорожні рядки
    real_texts = [t.strip() for t in raw_texts if isinstance(t, str) and t.strip()]

    if not real_texts:
        raise ValueError("Список real_texts порожній після очищення.")

    if not os.path.exists(REAL_INDEX_PATH):
        print("⚠️ Індекс реальних діалогів не знайдено. Створюємо новий...")

        # 🧠 Генеруємо ембедінги батчами (OpenAI обмежує кількість символів)
        embeddings = client.embeddings.create(
            model="text-embedding-3-small",
            input=real_texts
        )
        vectors = np.array([e.embedding for e in embeddings.data], dtype=np.float32)
        real_index = faiss.IndexFlatL2(len(vectors[0]))
        real_index.add(vectors)
        faiss.write_index(real_index, REAL_INDEX_PATH)
    else:
        real_index = faiss.read_index(REAL_INDEX_PATH)

except Exception as e:
    print(f"⚠️ Не вдалося завантажити real_dialogs: {e}")
    real_texts = []
    real_index = None


# --- 🛠 Лог ---
def log(message):
    print(message)

# --- 🧩 Поділ діалогу на чанки ---
def split_dialog_into_chunks(dialog_text: str, label: str = "") -> list:
    lines = dialog_text.strip().split("\n")
    chunks = []
    buffer = []
    for line in lines:
        if line.strip():
            buffer.append(line)
        if len(buffer) >= 4:
            chunks.append({"text": "\n".join(buffer), "label": label})
            buffer = []
    if buffer:
        chunks.append({"text": "\n".join(buffer), "label": label})
    return chunks

# --- 🔍 Пошук прикладів ---
def search_good_examples(query, top_k=3):
    if not good_index or not good_texts:
        return []
    if not isinstance(query, str) or not query.strip():
        return []
    try:
        emb = client.embeddings.create(model="text-embedding-3-small", input=[query.strip()]).data[0].embedding
        emb_np = np.array([emb], dtype=np.float32)
        distances, indices = good_index.search(emb_np, top_k)
        return [good_texts[i] for i in indices[0] if i < len(good_texts)]
    except Exception as e:
        print(f"⚠️ Помилка пошуку good_examples: {e}")
        return []

def search_bad_examples(query, top_k=2):
    if not bad_index or not bad_texts:
        return []
    if not isinstance(query, str) or not query.strip():
        return []
    try:
        emb = client.embeddings.create(model="text-embedding-3-small", input=[query.strip()]).data[0].embedding
        emb_np = np.array([emb], dtype=np.float32)
        distances, indices = bad_index.search(emb_np, top_k)
        return [bad_texts[i] for i in indices[0] if i < len(bad_texts)]
    except Exception as e:
        print(f"⚠️ Помилка пошуку bad_examples: {e}")
        return []

def search_real_examples(query, top_k=2):
    if not real_index or not real_texts:
        return []
    if not isinstance(query, str) or not query.strip():
        return []
    try:
        emb = client.embeddings.create(model="text-embedding-3-small", input=[query.strip()]).data[0].embedding
        emb_np = np.array([emb], dtype=np.float32)
        distances, indices = real_index.search(emb_np, top_k)
        return [real_texts[i] for i in indices[0] if i < len(real_texts)]
    except Exception as e:
        print(f"⚠️ Помилка пошуку real_examples: {e}")
        return []

# --- 🧱 Побудова prompt для OpenAI ---
def build_messages(chat_id, user_input, context_chunks, memory):
    history = get_history(memory, chat_id)
    meta = memory.get(str(chat_id), {}).get("_meta", {})

    prompt_parts = [SYSTEM_PROMPT]
    if meta.get("suspicion"):
        prompt_parts.append("Кандидат поводиться підозріло, відповідай обережно.")
    if meta.get("lang") == "ru":
        prompt_parts.append("Кандидат просив перейти на російську. Відповідай російською.")
    if meta.get("tone") == "formal":
        prompt_parts.append("Використовуй більш офіційний стиль.")
    if meta.get("tone") == "casual":
        prompt_parts.append("Можна спілкуватись трохи неформально, по-дружньому.")
    if meta.get("humor"):
        prompt_parts.append("Дозволено трохи гумору або емодзі.")

    messages = [{"role": "system", "content": "\n".join(prompt_parts)}]

    for pair in history[-10:]:
        messages.append({"role": "user", "content": pair["from_user"]})
        messages.append({"role": "assistant", "content": pair["from_ai"]})

    for chunk in context_chunks:
        messages.append({"role": "system", "content": f"Контекст: {chunk['text']}"})

    for ex in search_good_examples(user_input):
        messages.append({"role": "system", "content": f"Приклад: {ex}"})

    for real_ex in search_real_examples(user_input):
        messages.append({"role": "system", "content": f"Реальний приклад: {real_ex}"})

    for bad_ex in search_bad_examples(user_input):
        messages.append({"role": "system", "content": f"Уникай таких відповідей: {bad_ex}"})

    for lesson in feedback_lessons:
        pattern = lesson.get("pattern", "").lower()
        if pattern in user_input.lower():
            messages.append({"role": "system", "content": f"Порада: {lesson['advice']}"})

    messages.append({"role": "user", "content": user_input})
    return messages

# --- 🤖 Отримання відповіді від OpenAI ---
def get_openai_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8,
            presence_penalty=0.3,
            frequency_penalty=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Вибач, сталася помилка: {e}"

# --- 🔧 Форматування тексту ---
def format_text(text):
    return text.replace("\n\n", "\n").strip()

# --- 🕵️‍♂️ Визначення джерела кандидата ---
def detect_source(dialog_text: str) -> str:
    text = dialog_text.lower()
    if any(word in text for word in ["телеграм", "тг", "канал", "оголошення в телеграмі"]):
        return "telegram"
    elif any(word in text for word in ["olx", "олх", "оголошення"]):
        return "olx"
    elif any(word in text for word in ["інстаграм", "instagram", "сторіс", "reels"]):
        return "instagram"
    elif any(word in text for word in ["tiktok", "тікток", "tt", "відео"]):
        return "tiktok"
    elif any(word in text for word in ["друг", "порадив", "рекомендував", "знайомий"]):
        return "other"
    return "unknown"

# --- 📥 Парсинг тексту діалогу ---
def parse_dialog_text(text):
    lines = text.strip().splitlines()
    parsed = []
    for line in lines:
        line = line.strip()
        if line.startswith("👤"):
            parsed.append({"role": "user", "text": line[1:].strip()})
        elif line.startswith("🤖"):
            parsed.append({"role": "bot", "text": line[1:].strip()})
    return parsed
