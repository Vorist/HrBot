import os
import sys
import json

# ✅ Додаємо корінь проєкту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import REAL_DIALOGS_TXT_PATH, REAL_DIALOGS_PATH, USED_DIALOGS_PATH

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

def parse_dialog_block(lines):
    source = None
    dialog_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("source:"):
            source = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("bot"):
            dialog_lines.append(f"🤖 {line[3:].strip(' :')}")
        elif line.lower().startswith("user"):
            dialog_lines.append(f"👤 {line[4:].strip(' :')}")
        elif line.startswith("🤖") or line.startswith("👤"):
            dialog_lines.append(line)

    if not source or not dialog_lines:
        return None

    return f"📥 Джерело: {source}\n" + "\n".join(dialog_lines)

def load_real_dialogs_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    blocks = [block.strip().splitlines() for block in raw.strip().split("\n\n") if block.strip()]
    return blocks

def convert():
    if not os.path.exists(REAL_DIALOGS_TXT_PATH):
        safe_print(f"❌ Файл не знайдено: {REAL_DIALOGS_TXT_PATH}")
        return

    blocks = load_real_dialogs_from_txt(REAL_DIALOGS_TXT_PATH)
    used = load_used_dialogs()
    new_items = []

    for lines in blocks:
        formatted = parse_dialog_block(lines)
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
