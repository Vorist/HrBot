import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# === Завантаження змінних середовища ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Ініціалізація клієнта OpenAI ===
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# === Шлях до уроків з фідбеку ===
FEEDBACK_LESSONS_PATH = "data/feedback_lessons.json"

# --- Завантаження уроків з фідбеків --- #
def load_feedback_lessons(path=FEEDBACK_LESSONS_PATH):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lessons = json.load(f)
            return [l["advice"] for l in lessons if "advice" in l]
    except Exception as e:
        print(f"⚠️ Не вдалося завантажити уроки фідбеку: {e}")
        return []

# --- Переформулювання поганої відповіді --- #
def improve_reply(original_reply: str, context: str = "") -> dict:
    """
    Повертає словник з полями:
    - old: початкова відповідь
    - new: покращена відповідь
    - comment: чому ця відповідь краща (опціонально)
    """
    if not client:
        return {
            "old": original_reply,
            "new": "",
            "comment": "⚠️ API ключ не знайдено. Перевірте .env файл."
        }

    lessons = load_feedback_lessons()
    lessons_text = "\n".join(f"• {l}" for l in lessons)

    system_msg = (
        "Ти редактор відповідей AI бота в HR-сфері. "
        "Покращуй відповіді так, щоб вони були ввічливими, структурованими та зрозумілими. "
        "Не вигадуй нової інформації, лише покращуй стиль.\n"
    )
    if lessons_text:
        system_msg += f"\nОсь уроки, які треба враховувати:\n{lessons_text}"

    user_msg = (
        "Ось відповідь бота, яка була недоречною або слабкою. "
        "Виправ її та поясни, чому твоя відповідь краща.\n"
    )
    if context:
        user_msg += f"\nКонтекст: {context.strip()}\n"
    user_msg += f"\nОригінал: {original_reply.strip()}\n\nНовий варіант:\n"

    user_msg += "\n---\nПісля нового варіанту обов’язково напиши короткий коментар, чому відповідь стала кращою.\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.4,
            max_tokens=400
        )

        full_output = response.choices[0].message.content.strip()

        # Розділення покращеної відповіді та коментаря
        if "\n\nПричина:" in full_output:
            new_text, comment = full_output.split("\n\nПричина:", 1)
        elif "\nПричина:" in full_output:
            new_text, comment = full_output.split("\nПричина:", 1)
        else:
            parts = full_output.strip().split("\n\n", 1)
            new_text = parts[0].strip()
            comment = parts[1].strip() if len(parts) > 1 else ""

        return {
            "old": original_reply.strip(),
            "new": new_text.strip(),
            "comment": comment.strip()
        }

    except Exception as e:
        return {
            "old": original_reply,
            "new": "",
            "comment": f"⚠️ Помилка: {e}"
        }

# --- Тестовий запуск --- #
if __name__ == "__main__":
    example_bad = "ну я хз, напевно ти тупий якщо не поняв"
    example_context = "Кандидат запитав про оплату праці."
    result = improve_reply(example_bad, context=example_context)
    print("📥 Стара:", result["old"])
    print("📤 Нова:", result["new"])
    print("📝 Коментар:", result["comment"])
