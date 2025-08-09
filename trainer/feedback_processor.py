# trainer/feedback_processor.py

import sys
import os
import json
import re
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import FEEDBACK_COMMENTS_PATH, FEEDBACK_LESSONS_PATH
from utils import log
from backend.utils.jsonl_utils import append_jsonl  # Используем append_jsonl!

LOG_PATH = "logs/training_log.txt"

def log_to_file(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")
    print(full_message)

STRATEGY_HINTS = [
    (re.compile(r"\b(слишком|очень)?\s*длинн.*|много текста|многослов|громоздк.*", re.IGNORECASE), "Скороти відповідь"),
    (re.compile(r"(сразу|моментально).*все.*(вывал|говор|расска|пиш|да|скид)", re.IGNORECASE), "Дозуй інформацію"),
    (re.compile(r"(жестко|агрессив|провокац|резко|грубо|неаккуратно)", re.IGNORECASE), "Пом’якши тон і подачу"),
    (re.compile(r"(формул|язык|стиль).*(неподход|странн|канцел|официал|нечеловеч)", re.IGNORECASE), "Пиши природніше, людяніше"),
    (re.compile(r"(уточн|выясн|по чём|в чём дело|спроси|контекст|чего хочет|относительно чего)", re.IGNORECASE), "Почни з питання — дізнайся інтерес"),
    (re.compile(r"(повтор|часто).*имя|имя.*повтор", re.IGNORECASE), "Не зловживай іменем кандидата"),
    (re.compile(r"(слабая обработка|не проработал|не ответил на|не прояснил|не переубедил|не снял|просто извинился|не работает с отказом)", re.IGNORECASE), "Працюй із запереченнями — не здавайся"),
    (re.compile(r"(перебор|много|перенасыщ|перегруз).*детал|инфо|ввод.*|всё сразу", re.IGNORECASE), "Не перевантажуй — зацікав, потім поясни"),
    (re.compile(r"(зачем|повторно).*представил", re.IGNORECASE), "Не повторюй представлення"),
]

def extract_hint(comment: str) -> str | None:
    if not comment or not isinstance(comment, str):
        return None
    comment = comment.strip().lower()
    for pattern, hint in STRATEGY_HINTS:
        if pattern.search(comment):
            return hint
    return None

def parse_feedback_line(line: str) -> dict | None:
    try:
        data = json.loads(line)
        if not isinstance(data, dict):
            return None
        return data
    except json.JSONDecodeError:
        log_to_file("⚠️ Пропущено некоректний JSON у фідбек-файлі.")
        return None

def extract_feedback_insights(entries: list) -> list:
    results = []
    for entry in entries:
        comment = entry.get("comment", "")
        if not comment:
            continue
        recommendation = extract_hint(comment)
        results.append({
            "pattern": comment.lower(),
            "recommendation": recommendation or "",
            "dialog_id": entry.get("dialog_id", ""),
            "status": entry.get("status", "unknown"),
            "source": entry.get("source", "unknown"),
            "timestamp": entry.get("timestamp", datetime.now().isoformat()),
            "label": "feedback"
        })
    return results

def process_feedbacks():
    log_to_file("[🧠] Обробка фідбек-коментарів...")

    if not os.path.exists(FEEDBACK_COMMENTS_PATH):
        log_to_file("⚠️ Файл з коментарями не знайдено.")
        return

    entries = []
    try:
        with open(FEEDBACK_COMMENTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parsed = parse_feedback_line(line.strip())
                if parsed and "comment" in parsed:
                    entries.append(parsed)
    except Exception as e:
        log_to_file(f"❌ Помилка при читанні: {e}")
        return

    insights = extract_feedback_insights(entries)
    if not insights:
        log_to_file("⚠️ Жодної валідної рекомендації не знайдено.")
        return

    # Сохраняем каждую рекомендацию отдельной строкой JSONL!
    try:
        os.makedirs(os.path.dirname(FEEDBACK_LESSONS_PATH), exist_ok=True)
        with open(FEEDBACK_LESSONS_PATH, "w", encoding="utf-8") as f:
            for insight in insights:
                f.write(json.dumps(insight, ensure_ascii=False) + "\n")
        log_to_file(f"✅ Додано {len(insights)} рекомендацій у {FEEDBACK_LESSONS_PATH}")
    except Exception as e:
        log_to_file(f"❌ Помилка при збереженні: {e}")

def get_feedback_comments_for_chat(chat_id: str) -> list:
    if not os.path.exists(FEEDBACK_COMMENTS_PATH):
        return []
    results = []
    try:
        with open(FEEDBACK_COMMENTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parsed = parse_feedback_line(line.strip())
                if parsed and parsed.get("dialog_id") == chat_id:
                    results.append(parsed)
    except Exception:
        return []
    return results

if __name__ == "__main__":
    process_feedbacks()
