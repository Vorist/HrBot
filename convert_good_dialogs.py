# convert_good_dialogs.py

import json
import hashlib
from config import GOOD_DIALOGS_PATH

def hash_dialog(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def convert_dialogs():
    try:
        with open(GOOD_DIALOGS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Файл {GOOD_DIALOGS_PATH} не знайдено.")
        return

    seen_hashes = set()
    converted = []

    for i, line in enumerate(lines):
        try:
            data = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"⚠️ JSON-помилка у рядку {i+1}")
            continue

        dialog_text = None

        # Формат: {"text": "..."}
        if isinstance(data, dict) and "text" in data:
            dialog_text = data["text"].strip()

        # Формат: {"from_user": "...", "from_ai": "..."}
        elif isinstance(data, dict) and "from_user" in data and "from_ai" in data:
            dialog_text = f"👤 {data['from_user'].strip()}\n🤖 {data['from_ai'].strip()}"

        # Формат: {"history": [{"from_user": "...", "from_ai": "..."}]}
        elif isinstance(data, dict) and "history" in data and isinstance(data["history"], list):
            dialog_lines = []
            for pair in data["history"]:
                if "from_user" in pair and pair["from_user"]:
                    dialog_lines.append(f"👤 {pair['from_user'].strip()}")
                if "from_ai" in pair and pair["from_ai"]:
                    dialog_lines.append(f"🤖 {pair['from_ai'].strip()}")
            dialog_text = "\n".join(dialog_lines)

        if not dialog_text:
            print(f"⚠️ Пропущено рядок {i+1} — неможливо отримати текст.")
            continue

        dlg_hash = hash_dialog(dialog_text)
        if dlg_hash in seen_hashes:
            continue  # дубль

        seen_hashes.add(dlg_hash)
        converted.append({"text": dialog_text})

    # Перезаписуємо файл
    with open(GOOD_DIALOGS_PATH, "w", encoding="utf-8") as f:
        for item in converted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ Успішно конвертовано {len(converted)} унікальних good-діалогів у форматі {'text'}.")

if __name__ == "__main__":
    convert_dialogs()
