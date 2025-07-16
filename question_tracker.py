import json
import os
import re
from collections import defaultdict
from config import FREQUENT_QUESTIONS_PATH


def clean_phrase(text: str) -> str:
    """Нормалізація фрази: нижній регістр, без зайвих знаків"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s?!-]", "", text)
    return text


# --- Завантаження запитань --- #
def load_questions() -> defaultdict:
    if not os.path.exists(FREQUENT_QUESTIONS_PATH):
        return defaultdict(int)
    try:
        with open(FREQUENT_QUESTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return defaultdict(int, data)
    except (json.JSONDecodeError, ValueError):
        print("⚠️ Файл з частими запитаннями пошкоджено. Створюю новий.")
        return defaultdict(int)


# --- Збереження запитань --- #
def save_questions(data: dict):
    try:
        # Сортуємо за кількістю згадувань
        sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        with open(FREQUENT_QUESTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Помилка при збереженні частих запитань: {e}")


# --- Додавання нової фрази --- #
def add_user_phrase(phrase: str):
    phrase = clean_phrase(phrase)
    if len(phrase) < 5:
        return

    questions = load_questions()
    questions[phrase] += 1
    save_questions(questions)


# --- (Опціонально) Отримати топ-запитання --- #
def get_top_questions(limit=10):
    questions = load_questions()
    return sorted(questions.items(), key=lambda x: x[1], reverse=True)[:limit]


# --- Тестовий запуск --- #
if __name__ == "__main__":
    add_user_phrase("Скільки платите?")
    add_user_phrase("Яка зарплата?")
    print("Топ запитань:")
    for q, count in get_top_questions():
        print(f"• {q} — {count}")
