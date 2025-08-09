import os
import sys
import json
import hashlib

# ✅ Добавляем корень проекта (чтобы находил config)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import REAL_DIALOGS_PATH, USED_DIALOGS_PATH

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode())

def hash_dialog_block(lines):
    """Генерирует хеш блока для дубликат-контроля (без учета переводов строк)."""
    normalized = "\n".join([line.strip() for line in lines if line.strip()])
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def load_used_hashes():
    """Загружает множество ранее импортированных диалогов (по хешу)."""
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
        except Exception as e:
            safe_print(f"⚠️ Не удалось прочитать used hashes: {e}")
    return set()

def save_used_hashes(hashes: set):
    try:
        with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
            json.dump(list(hashes), f, ensure_ascii=False, indent=2)
    except Exception as e:
        safe_print(f"❌ Не удалось сохранить used hashes: {e}")

def parse_dialog_block(lines):
    """Парсит один диалог-блок, аккуратно восстанавливает формат для real_dialogs.txt."""
    source = None
    dialog = []

    for line in lines:
        l = line.strip()
        if not l:
            continue
        if l.lower().startswith("source:"):
            source = l.split(":", 1)[-1].strip()
        elif l.startswith("📥"):
            # подстраховка если уже с источником
            source = l.lstrip("📥").replace("Джерело:", "").replace(":", "").strip()
        elif l.lower().startswith("bot"):
            dialog.append(f"🤖 {l[3:].strip(' :')}")
        elif l.lower().startswith("user"):
            dialog.append(f"👤 {l[4:].strip(' :')}")
        elif l.startswith("🤖") or l.startswith("👤"):
            dialog.append(l)
    if not source or not dialog:
        return None
    block = [f"📥 Джерело: {source}"] + dialog
    return "\n".join(block)

def load_real_dialogs_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    # Разбить на блоки по двойному переводу строки
    blocks = [block.strip().splitlines() for block in raw.strip().split("\n\n") if block.strip()]
    return blocks

def convert():
    if not os.path.exists(REAL_DIALOGS_PATH):
        safe_print(f"❌ Файл не найден: {REAL_DIALOGS_PATH}")
        return

    blocks = load_real_dialogs_from_txt(REAL_DIALOGS_PATH)
    used_hashes = load_used_hashes()
    new_blocks = []

    for lines in blocks:
        block_hash = hash_dialog_block(lines)
        if block_hash in used_hashes:
            continue
        formatted = parse_dialog_block(lines)
        if not formatted:
            continue
        new_blocks.append(formatted)
        used_hashes.add(block_hash)

    if not new_blocks:
        safe_print("⚠️ Новых фрагментов не найдено.")
        return

    try:
        os.makedirs(os.path.dirname(REAL_DIALOGS_PATH), exist_ok=True)
        with open(REAL_DIALOGS_PATH, "a", encoding="utf-8") as f:
            f.write("\n\n".join(new_blocks) + "\n\n")
        save_used_hashes(used_hashes)
        safe_print(f"✅ Добавлено {len(new_blocks)} новых диалогов → {REAL_DIALOGS_PATH}")
    except Exception as e:
        safe_print(f"❌ Ошибка записи: {e}")

if __name__ == "__main__":
    convert()
