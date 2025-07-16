import json
import os
from config import GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH

BAD_DIALOGS_TXT = BAD_DIALOGS_PATH.replace(".jsonl", "_readable.txt")


def format_memory_as_dialog(chat_id, memory):
    """Форматує історію чату в текстовий діалог"""
    dialog = memory.get(str(chat_id), {}).get("dialog", [])
    lines = []
    for item in dialog:
        if "from_user" in item:
            lines.append(f"👤 {item['from_user'].strip()}")
        if "from_ai" in item:
            lines.append(f"🤖 {item['from_ai'].strip()}")
    return {"text": "\n".join(lines)} if lines else {}


def save_dialog(chat_id, memory, is_good=True):
    formatted = format_memory_as_dialog(chat_id, memory)

    if not formatted or not formatted.get("text"):
        print("⚠️ Порожній діалог, не зберігаємо.")
        return

    path = GOOD_DIALOGS_PATH if is_good else BAD_DIALOGS_PATH

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(formatted, ensure_ascii=False) + "\n")
        print(f"✅ Діалог збережено у {'GOOD' if is_good else 'BAD'}")
    except Exception as e:
        print(f"❌ Помилка при збереженні JSONL: {e}")

    # --- readable.txt для bad-діалогів --- #
    if not is_good:
        try:
            with open(BAD_DIALOGS_TXT, "a", encoding="utf-8") as f:
                f.write("─── BAD DIALOG ───\n")
                f.write(formatted["text"])
                f.write("\n\n")
        except Exception as e:
            print(f"❌ Помилка при збереженні readable-файлу: {e}")


def save_good(dialog):
    if isinstance(dialog, dict) and "chat_id" in dialog and "memory" in dialog:
        save_dialog(dialog["chat_id"], dialog["memory"], is_good=True)
    else:
        print("⚠️ Некоректний формат для save_good")


def save_bad(dialog):
    if isinstance(dialog, dict) and "chat_id" in dialog and "memory" in dialog:
        save_dialog(dialog["chat_id"], dialog["memory"], is_good=False)
    else:
        print("⚠️ Некоректний формат для save_bad")
