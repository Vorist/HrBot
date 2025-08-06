#!/usr/bin/env python3
# build_dialog_chunks.py

import os
import json
import hashlib
import logging

from config import REAL_DIALOGS_TXT_PATH, DIALOG_CHUNKS_PATH, USED_DIALOGS_PATH

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

def hash_dialog(dialog_text: str) -> str:
    return hashlib.md5(dialog_text.encode("utf-8")).hexdigest()

def format_text(text: str) -> str:
    # Убираем лишние пробелы
    return " ".join(text.strip().split())

def detect_source(dialog_lines: list[str]) -> str:
    header = dialog_lines[0].strip()
    if header.lower().startswith("source:"):
        return header.split(":", 1)[1].strip()
    if header.startswith("📥"):
        # убрать "📥 Джерело:" или аналог
        return header.lstrip("📥").replace("Джерело:", "").strip()
    return "невідомо"

def load_used_hashes() -> set[str]:
    if os.path.exists(USED_DIALOGS_PATH):
        try:
            with open(USED_DIALOGS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            log.warning("⚠️ Не удалось прочитать used hashes, начнем с пустого набора")
    return set()

def save_used_hashes(hashes: set[str]) -> None:
    os.makedirs(os.path.dirname(USED_DIALOGS_PATH), exist_ok=True)
    with open(USED_DIALOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, ensure_ascii=False, indent=2)

def load_real_dialog_blocks() -> list[list[str]]:
    if not os.path.exists(REAL_DIALOGS_TXT_PATH):
        log.error(f"❌ Файл не найден: {REAL_DIALOGS_TXT_PATH}")
        return []
    with open(REAL_DIALOGS_TXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    # разделяем по двойному переносу строки на блоки
    raw_blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    return [block.splitlines() for block in raw_blocks]

def split_dialog_into_chunks(dialog_lines: list[str]) -> list[dict]:
    source = detect_source(dialog_lines)
    chunks: list[dict] = []
    for line in dialog_lines:
        text = line.strip()
        if not text or text.lower().startswith("source:") or text.startswith("📥"):
            continue
        # анализируем роль по префиксу
        if text.startswith("👤"):
            content = format_text(text[1:])
            chunks.append({"text": f"👤 {content}", "source": source})
        elif text.startswith("🤖"):
            content = format_text(text[1:])
            chunks.append({"text": f"🤖 {content}", "source": source})
        # также поддерживаем строки "user ..." или "bot ..."
        elif text.lower().startswith("user"):
            content = format_text(text[4:].lstrip(" :"))
            chunks.append({"text": f"👤 {content}", "source": source})
        elif text.lower().startswith("bot"):
            content = format_text(text[3:].lstrip(" :"))
            chunks.append({"text": f"🤖 {content}", "source": source})
    return chunks

def build_dialog_chunks():
    blocks = load_real_dialog_blocks()
    used_hashes = load_used_hashes()
    new_hashes: set[str] = set()
    all_chunks: list[dict] = []

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

    # Записываем в JSONL
    os.makedirs(os.path.dirname(DIALOG_CHUNKS_PATH), exist_ok=True)
    with open(DIALOG_CHUNKS_PATH, "a", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    save_used_hashes(used_hashes.union(new_hashes))
    log.info(f"✅ Добавлено {len(all_chunks)} фрагментов → {DIALOG_CHUNKS_PATH}")

if __name__ == "__main__":
    build_dialog_chunks()
