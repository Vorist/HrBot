import os
import json
import numpy as np
import faiss
from openai import OpenAI
from config import BAD_DIALOGS_PATH, BAD_INDEX_PATH

client = OpenAI()

# --- Завантаження bad-діалогів --- #
try:
    with open(BAD_DIALOGS_PATH, "r", encoding="utf-8") as f:
        bad_texts = []
        for i, line in enumerate(f):
            try:
                obj = json.loads(line)
                if "text" in obj:
                    bad_texts.append(obj["text"])
            except json.JSONDecodeError:
                print(f"⚠️ Некоректний JSON у рядку {i+1}")
except Exception as e:
    print(f"⚠️ Не вдалося завантажити bad_dialogs: {e}")
    bad_texts = []

# --- Завантаження FAISS-індексу --- #
try:
    if os.path.exists(BAD_INDEX_PATH):
        bad_index = faiss.read_index(BAD_INDEX_PATH)
    else:
        raise FileNotFoundError("Індекс не знайдено.")
except Exception as e:
    print(f"⚠️ Не вдалося завантажити bad_index: {e}")
    bad_index = None


def compute_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"❌ Помилка embedding: {e}")
        return None


def check_similarity_with_bad(dialog_text, threshold=0.90):
    if not bad_index or not bad_texts:
        return False

    emb = compute_embedding(dialog_text)
    if emb is None:
        return False

    distances, indices = bad_index.search(np.array([emb]), k=1)
    similarity = 1 - distances[0][0]  # FAISS повертає L2-дистанцію

    return similarity > threshold


def evaluate_dialog(dialog_history: list) -> dict:
    """
    Оцінює діалог: евристика + схожість з поганими кейсами
    """
    dialog_text = format_dialog(dialog_history)
    score = heuristic_score(dialog_history)
    similar_bad = check_similarity_with_bad(dialog_text)

    return {
        "dialog_score": score,
        "similar_bad_case": similar_bad
    }


def heuristic_score(dialog: list) -> int:
    """
    Просте евристичне оцінювання:
    +1 за кожну відповідь користувача після першої
    -2, якщо менше 3 реплік
    -1, якщо остання репліка — негатив
    """
    user_replies = [m["from_user"] for m in dialog if "from_user" in m]
    score = len(user_replies) - 1  # перше повідомлення — не вважаємо індикатором діалогу

    if len(user_replies) < 3:
        score -= 2

    if user_replies:
        last = user_replies[-1].lower()
        if any(x in last for x in [
            "не цікаво", "не хочу", "до побачення", "відчепись", "розвод", "скам",
            "відстань", "відвали", "більше не пиши"
        ]):
            score -= 1

    return max(score, 0)


def format_dialog(dialog: list) -> str:
    """Форматує список {"from_user", "from_ai"} у текст для перевірки"""
    lines = []
    for msg in dialog:
        if "from_user" in msg:
            lines.append(f"👤 {msg['from_user']}")
        if "from_ai" in msg:
            lines.append(f"🤖 {msg['from_ai']}")
    return "\n".join(lines)
