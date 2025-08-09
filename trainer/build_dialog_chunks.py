# trainer/build_dialog_chunks.py

import os
import sys
import json
import hashlib
import logging
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import REAL_DIALOGS_PATH, DIALOG_CHUNKS_PATH, USED_DIALOGS_PATH

LOG_PATH = "logs/training_log.txt"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode())

def hash_dialog(dialog_text: str) -> str:
    """MD5-хеш для блока диалога или чанка (по ключевым полям)."""
    return hashlib.md5(dialog_text.encode("utf-8")).hexdigest()

def format_text(text: str) -> str:
    """Убирает лишние пробелы и спецсимволы."""
    return " ".join(text.strip().split())

def detect_source(dialog_lines: list[str]) -> str:
    """Определяет источник диалога по первой строке блока."""
    header = dialog_lines[0].strip() if dialog_lines else ""
    if header.lower().startswith("source:"):
        return header.split(":", 1)[1].strip()
    if header.startswith("📥"):
        # Поддержка разных вариантов "📥 Джерело:" или "📥 Джерело"
        line = header.lstrip("📥").replace("Джерело:", "").replace("Джерело", "").replace(":", "").strip()
        return line or "невідомо"
    return "невідомо"

def load_used_hashes() -> set[str]:
    """Загрузка обработанных хешей из USED_DIALOGS_PATH (универсально)."""
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Поддержка как списка, так и dict-хранения (на совместимость)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
        except Exception as e:
            log.warning(f"⚠️ Не удалось прочитать used hashes: {e}")
    return set()

def save_used_hashes(hashes: set[str]) -> None:
    """Сохраняет обработанные хеши (в формате списка)."""
    os.makedirs(os.path.dirname(USED_DIALOGS_PATH), exist_ok=True)
    with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(hashes)), f, ensure_ascii=False, indent=2)

def load_real_dialog_blocks() -> list[list[str]]:
    """Загружает диалоги из TXT, разбивает по \n\n (блоки), затем по строкам."""
    if not os.path.exists(REAL_DIALOGS_PATH):
        log.error(f"❌ Файл не найден: {REAL_DIALOGS_PATH}")
        return []
    with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    raw_blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    return [block.splitlines() for block in raw_blocks if block]

def split_dialog_into_chunks(dialog_lines: list[str]) -> list[dict]:
    """
    Делит блок на чанки, поддерживает:
    - 👤 ... или 🤖 ...
    - user ... или bot ...
    """
    source = detect_source(dialog_lines)
    chunks = []
    for line in dialog_lines:
        text = line.strip()
        if not text or text.lower().startswith("source:") or text.startswith("📥"):
            continue
        if text.startswith("👤"):
            content = format_text(text[1:])
            if content:
                chunks.append({"role": "user", "text": content, "source": source})
        elif text.startswith("🤖"):
            content = format_text(text[1:])
            if content:
                chunks.append({"role": "bot", "text": content, "source": source})
        elif text.lower().startswith("user"):
            content = format_text(text[4:].lstrip(": "))
            if content:
                chunks.append({"role": "user", "text": content, "source": source})
        elif text.lower().startswith("bot"):
            content = format_text(text[3:].lstrip(": "))
            if content:
                chunks.append({"role": "bot", "text": content, "source": source})
    return chunks

def build_dialog_chunks():
    log.info("🔨 Запуск build_dialog_chunks...")
    blocks = load_real_dialog_blocks()
    if not blocks:
        log.info("⚠️ Нет валидных блоков диалогов.")
        return

    used_hashes = load_used_hashes()
    new_hashes: set[str] = set()
    all_chunks: list[dict] = []

    # --- Генерация чанков из новых диалогов --- #
    for lines in blocks:
        full_text = "\n".join(lines)
        h = hash_dialog(full_text)
        if h in used_hashes:
            continue
        chunks = split_dialog_into_chunks(lines)
        if chunks:
            all_chunks.extend(chunks)
            new_hashes.add(h)

    if not all_chunks:
        log.info("⚠️ Новых фрагментов не найдено.")
        return

    # --- Повторная фильтрация на уровне чанков (уникальность) --- #
    existing = set()
    if os.path.exists(DIALOG_CHUNKS_PATH):
        with open(DIALOG_CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    chunk = json.loads(line)
                    key = (
                        str(chunk.get("source", "")).strip() + "|" +
                        str(chunk.get("role", "")).strip() + "|" +
                        str(chunk.get("text", "")).strip()
                    )
                    existing.add(hash_dialog(key))
                except Exception:
                    continue

    written = 0
    os.makedirs(os.path.dirname(DIALOG_CHUNKS_PATH), exist_ok=True)
    with open(DIALOG_CHUNKS_PATH, "a", encoding="utf-8") as f:
        for chunk in all_chunks:
            key = (
                str(chunk.get("source", "")).strip() + "|" +
                str(chunk.get("role", "")).strip() + "|" +
                str(chunk.get("text", "")).strip()
            )
            h = hash_dialog(key)
            if h in existing:
                continue
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            existing.add(h)
            written += 1

    save_used_hashes(used_hashes.union(new_hashes))
    log.info(f"✅ Добавлено {written} новых фрагментов → {DIALOG_CHUNKS_PATH}")

    if written == 0:
        safe_print("⚠️ Новых уникальных чанков не найдено. Всё уже в индексе.")
    else:
        safe_print(f"✅ Добавлено {written} новых чанков-реплик.")

if __name__ == "__main__":
    build_dialog_chunks()
