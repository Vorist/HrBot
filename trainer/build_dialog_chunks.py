import os
import json
import hashlib

REAL_DIALOGS_TXT_PATH = "data/real_dialogs.txt"
DIALOG_CHUNKS_PATH = "data/dialog_chunks.json"
USED_DIALOGS_PATH = "data/used_real_dialogs.json"

def hash_dialog(dialog_text):
    return hashlib.md5(dialog_text.encode("utf-8")).hexdigest()

def format_text(text):
    return text.strip().replace("  ", " ")

def detect_source(dialog_lines):
    for line in dialog_lines:
        if line.lower().startswith("source:"):
            return line.split(":", 1)[-1].strip()
    return "невідомо"

def load_used_hashes():
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_used_hashes(hashes):
    os.makedirs(os.path.dirname(USED_DIALOGS_PATH), exist_ok=True)
    with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, ensure_ascii=False, indent=2)

def load_real_dialog_blocks():
    if not os.path.exists(REAL_DIALOGS_TXT_PATH):
        print(f"❌ Файл не знайдено: {REAL_DIALOGS_TXT_PATH}")
        return []

    with open(REAL_DIALOGS_TXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    return [block.splitlines() for block in blocks]

def split_dialog_into_chunks(dialog_lines):
    source = detect_source(dialog_lines)
    chunks = []

    for line in dialog_lines:
        line = line.strip()
        if line.lower().startswith("source:"):
            continue
        if line.lower().startswith("bot"):
            text = format_text(line[3:].strip(" :"))
            chunks.append({"text": f"🤖 {text}", "source": source})
        elif line.lower().startswith("user"):
            text = format_text(line[4:].strip(" :"))
            chunks.append({"text": f"👤 {text}", "source": source})

    return chunks

def build_dialog_chunks():
    dialog_blocks = load_real_dialog_blocks()
    used_hashes = load_used_hashes()

    new_chunks = []
    new_hashes = set()

    for lines in dialog_blocks:
        dialog_text = "\n".join(lines)
        h = hash_dialog(dialog_text)
        if h in used_hashes:
            continue
        new_chunks.extend(split_dialog_into_chunks(lines))
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

if __name__ == "__main__":
    build_dialog_chunks()
