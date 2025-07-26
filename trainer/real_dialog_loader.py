import os
from datetime import datetime

LOG_PATH = "logs/training_log.txt"

def log_to_file(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")
    print(full_message)


def load_real_dialogs_from_txt(path: str) -> list:
    """
    Завантажує діалоги з real_dialogs.txt у форматі:
    📥 Джерело: Instagram
    🤖 Привіт!
    👤 Скільки заробіток?
    ...
    Кожен діалог — блок з кількох рядків, відокремлений порожнім рядком.
    """
    if not os.path.exists(path):
        log_to_file(f"❌ Файл {path} не знайдено.")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        log_to_file(f"❌ Помилка при зчитуванні {path}: {e}")
        return []

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    parsed_dialogs = []

    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue

        # --- Обов’язково має бути джерело --- #
        source_line = lines[0].strip()
        if not source_line.startswith("📥 Джерело:"):
            continue
        source = source_line.split(":", 1)[-1].strip()

        dialog = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("👤"):
                dialog.append({"role": "user", "text": line[1:].strip(" :")})
            elif line.startswith("🤖"):
                dialog.append({"role": "bot", "text": line[1:].strip(" :")})

        if dialog:
            parsed_dialogs.append({
                "source": source,
                "dialog": dialog
            })

    log_to_file(f"📥 Завантажено {len(parsed_dialogs)} real-діалог(ів) з {path}")
    return parsed_dialogs


if __name__ == "__main__":
    path = "data/real_dialogs.txt"
    data = load_real_dialogs_from_txt(path)
    if data:
        log_to_file(f"🧾 Приклад першого діалогу:\n{data[0]}")
    else:
        log_to_file("⚠️ Жодного діалогу не знайдено.")
