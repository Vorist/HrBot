# scripts/convert_real_dialogs.py

import os
import sys
import json
from datetime import datetime

# ✅ Додаємо корінь проєкту в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import REAL_DIALOGS_TXT_PATH, REAL_DIALOGS_PATH, USED_DIALOGS_PATH
from log import log


def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode())


def load_used_dialogs():
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            safe_print(f"⚠️ Помилка читання used_dialogs: {e}")
            return {}
    return {}


def save_used_dialogs(used):
    try:
        with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
            json.dump(used, f, ensure_ascii=False, indent=2)
    except Exception as e:
        safe_print(f"❌ Не вдалося зберегти used_dialogs: {e}")


def parse_dialog_block(block):
    lines = [line.strip() for line in block.split("\n") if line.strip()]
    if not lines or not lines[0].lower().startswith("source:"):
        return None

    source = lines[0].split(":", 1)[-1].strip()
    dialog_lines = lines[1:]

    formatted_dialog = f"📥 Джерело: {source}\n"
    for line in dialog_lines:
        if line.lower().startswith("bot"):
            text = line[3:].strip(" :")
            formatted_dialog += f"🤖 {text}\n"
        elif line.lower().startswith("user"):
            text = line[4:].strip(" :")
            formatted_dialog += f"👤 {text}\n"
        elif line.startswith("🤖") or line.startswith("👤"):
            formatted_dialog += line + "\n"  # already formatted

    return formatted_dialog.strip()


def load_real_dialogs_from_txt(path: str) -> list:
    dialogs = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    buffer = []
    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                dialogs.append("\n".join(buffer))
                buffer = []
            continue
        if line.lower().startswith("source:"):
            buffer.append(f"📥 Джерело: {line.split(':', 1)[1].strip()}")
        elif line.lower().startswith("bot"):
            buffer.append("🤖 " + line[3:].strip(" :"))
        elif line.lower().startswith("user"):
            buffer.append("👤 " + line[4:].strip(" :"))
        elif line.startswith("🤖") or line.startswith("👤"):
            buffer.append(line)

    if buffer:
        dialogs.append("\n".join(buffer))

    return dialogs


def convert():
    if not os.path.exists(REAL_DIALOGS_TXT_PATH):
        safe_print(f"❌ Файл {REAL_DIALOGS_TXT_PATH} не знайдено.")
        return

    try:
        with open(REAL_DIALOGS_TXT_PATH, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        safe_print(f"❌ Помилка читання TXT: {e}")
        return

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    used = load_used_dialogs()
    new_items = []

    for block in blocks:
        formatted = parse_dialog_block(block)
        if not formatted or formatted in used:
            continue

        new_items.append({"text": formatted})
        used[formatted] = True

    if not new_items:
        safe_print("⚠️ Нових фрагментів не знайдено.")
        return

    try:
        os.makedirs(os.path.dirname(REAL_DIALOGS_PATH), exist_ok=True)
        with open(REAL_DIALOGS_PATH, "a", encoding="utf-8") as f:
            for item in new_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        save_used_dialogs(used)
        safe_print(f"✅ Додано {len(new_items)} нових діалогів → {REAL_DIALOGS_PATH}")
    except Exception as e:
        safe_print(f"❌ Помилка запису JSONL: {e}")


if __name__ == "__main__":
    convert()
