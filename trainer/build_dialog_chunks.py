# trainer/build_dialog_chunks.py

import os
import json
import sys
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import REAL_DIALOGS_PATH, DIALOG_CHUNKS_PATH

USED_DIALOGS_PATH = "data/used_real_dialogs.json"

# --- 🔐 Хешування для унікальності --- #
def hash_dialog(dialog_text):
    return hashlib.md5(dialog_text.encode("utf-8")).hexdigest()

# --- 🧼 Очищення тексту --- #
def format_text(text):
    return text.strip().replace("  ", " ")

# --- 📥 Визначення джерела діалогу --- #
def detect_source(dialog_text):
    first = dialog_text.strip().split("\n")[0]
    if first.startswith("📥 Джерело: "):
        return first.replace("📥 Джерело: ", "").strip()
    return "невідомо"

# --- 📁 Завантаження діалогів --- #
def load_real_dialogs():
    if not os.path.exists(REAL_DIALOGS_PATH):
        print(f"❌ Файл не знайдено: {REAL_DIALOGS_PATH}")
        return []
    with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    return [d.strip() for d in raw.split("\n\n") if d.strip()]

# --- 🧾 Завантаження використаних хешів --- #
def load_used_hashes():
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ Не вдалося завантажити used_real_dialogs.json: {e}")
    return set()

def save_used_hashes(hashes):
    os.makedirs(os.path.dirname(USED_DIALOGS_PATH), exist_ok=True)
    with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, ensure_ascii=False, indent=2)

# --- 🧩 Розбиття діалогу на фрагменти --- #
def split_dialog_into_chunks(dialog_text):
    source = detect_source(dialog_text)
    lines = dialog_text.strip().split("\n")[1:]  # пропускаємо перший рядок
    chunks = []

    for line in lines:
        clean = format_text(line)
        if clean:
            chunks.append({
                "text": clean,
                "source": source
            })
    return chunks

# --- 🧠 Основна функція --- #
def build_dialog_chunks():
    dialogs = load_real_dialogs()
    used_hashes = load_used_hashes()

    new_chunks = []
    new_hashes = set()

    for dialog in dialogs:
        h = hash_dialog(dialog)
        if h in used_hashes:
            continue
        new_chunks.extend(split_dialog_into_chunks(dialog))
        new_hashes.add(h)

    if not new_chunks:
        print("⚠️ Нових фрагментів не знайдено.")
        return

    os.makedirs(os.path.dirname(DIALOG_CHUNKS_PATH), exist_ok=True)
    with open(DIALOG_CHUNKS_PATH, "w", encoding="utf-8") as f:
        for chunk in new_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    save_used_hashes(used_hashes.union(new_hashes))
    print(f"✅ Додано {len(new_chunks)} нових фрагментів → {DIALOG_CHUNKS_PATH}")

# --- ▶️ Запуск ---
if __name__ == "__main__":
    build_dialog_chunks()
