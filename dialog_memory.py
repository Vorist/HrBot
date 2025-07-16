# dialog_memory.py

import os
import json
from datetime import datetime
from config import MEMORY_PATH
from suspicion import is_suspicious, get_suspicion_reason

MAX_HISTORY = None
SUSPICION_LOG_PATH = "data/suspicion_log.jsonl"

# --- Завантаження памʼяті --- #
def load_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data or data == "null":
                    raise ValueError("Порожній файл")
                return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            print("⚠️ Файл memory.json пошкоджено або порожній — створюємо новий.")
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    return {}

# --- Збереження памʼяті --- #
def save_memory(memory):
    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Помилка при збереженні памʼяті: {e}")

# --- Логування підозрілих повідомлень --- #
def log_suspicion(chat_id, text, reason):
    try:
        record = {
            "chat_id": str(chat_id),
            "text": text.strip(),
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        with open(SUSPICION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ Не вдалося залогувати підозру: {e}")

# --- Додавання нового повідомлення до історії --- #
def append_to_memory(memory, chat_id, user_msg, bot_msg):
    str_id = str(chat_id)

    # Ініціалізація діалогу, якщо потрібно
    if str_id not in memory:
        memory[str_id] = {
            "history": [],
            "status": "новий",
            "meta": {}
        }

    if "history" not in memory[str_id]:
        memory[str_id]["history"] = []
    if "meta" not in memory[str_id]:
        memory[str_id]["meta"] = {}
    if "status" not in memory[str_id]:
        memory[str_id]["status"] = "новий"

    user_msg = str(user_msg or "")
    bot_msg = str(bot_msg or "")

    # --- Визначення мови RU --- #
    if any(x in user_msg.lower() for x in [
        "по-русски", "на русском", "можно по-русски", "перейди на русский", "давай на русском"
    ]):
        memory[str_id]["meta"]["lang"] = "ru"

    # --- Підозрілий текст --- #
    if is_suspicious(user_msg):
        memory[str_id]["meta"]["suspicion"] = True
        reason = get_suspicion_reason(user_msg)
        if reason:
            memory[str_id]["meta"]["suspicion_reason"] = reason
            log_suspicion(chat_id, user_msg, reason)

    # --- Додаємо в історію --- #
    memory[str_id]["history"].append({
        "from_user": user_msg,
        "from_ai": bot_msg
    })

    if MAX_HISTORY is not None:
        memory[str_id]["history"] = memory[str_id]["history"][-MAX_HISTORY:]

    save_memory(memory)

# --- Отримання історії --- #
def get_history(memory, chat_id):
    return memory.get(str(chat_id), {}).get("history", [])

# --- Статус діалогу --- #
def set_status(memory, chat_id, status):
    str_id = str(chat_id)
    if str_id not in memory:
        memory[str_id] = {"history": [], "status": status, "meta": {}}
    else:
        memory[str_id]["status"] = status
    save_memory(memory)

def get_status(memory, chat_id):
    return memory.get(str(chat_id), {}).get("status", "новий")

# --- Мета-дані --- #
def set_meta(memory, chat_id, key, value):
    str_id = str(chat_id)
    if str_id not in memory:
        memory[str_id] = {"history": [], "status": "новий", "meta": {}}
    memory[str_id]["meta"][key] = value
    save_memory(memory)

def get_meta(memory, chat_id):
    return memory.get(str(chat_id), {}).get("meta", {})

# --- Очистка памʼяті --- #
def reset_memory(memory, chat_id):
    str_id = str(chat_id)
    if str_id in memory:
        memory[str_id]["history"] = []
        memory[str_id]["meta"] = {}
        memory[str_id]["status"] = "новий"
        save_memory(memory)
