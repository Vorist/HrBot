# trainer/real_dialog_loader.py

import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional

# гарантируем доступ к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import REAL_DIALOGS_PATH  # используем путь из конфига

LOG_PATH = "logs/training_log.txt"


def log_to_file(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    msg = f"{timestamp} {message}"
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode())
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# --- нормализация строк ---
ROLE_USER_PAT = re.compile(r"^(?:👤|user\b)", re.IGNORECASE)
ROLE_BOT_PAT  = re.compile(r"^(?:🤖|bot\b)", re.IGNORECASE)
SOURCE_PATTERNS = [
    re.compile(r"^\s*📥\s*Джерело:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*📥\s*(.+)$"),               # 📥 Instagram / 📥 Telegram
    re.compile(r"^\s*source:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*джерело:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*источник:\s*(.+)$", re.IGNORECASE),
]

def _clean_text(s: str) -> str:
    # убираем лишние пробелы, двоеточия и тире у начала
    s = s.replace("\r\n", "\n").strip()
    s = re.sub(r"^[\s:–—-]+", "", s)  # ведущие : — –
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def parse_source(line: str) -> str:
    line = line.strip()
    for pat in SOURCE_PATTERNS:
        m = pat.match(line)
        if m:
            return _clean_text(m.group(1))
    return "невідомо"


def _extract_role_and_text(line: str) -> Optional[Dict[str, str]]:
    """Пытается распознать роль и вернуть {'role': 'user'|'bot', 'text': ...}."""
    raw = line.strip()
    if not raw:
        return None

    # emoji-формат
    if raw.startswith("👤"):
        return {"role": "user", "text": _clean_text(raw[1:])}
    if raw.startswith("🤖"):
        return {"role": "bot", "text": _clean_text(raw[1:])}

    # текстовый формат
    if ROLE_USER_PAT.match(raw):
        txt = ROLE_USER_PAT.sub("", raw, count=1)
        return {"role": "user", "text": _clean_text(txt)}
    if ROLE_BOT_PAT.match(raw):
        txt = ROLE_BOT_PAT.sub("", raw, count=1)
        return {"role": "bot", "text": _clean_text(txt)}

    # не распознали — пропускаем
    return None


def _split_blocks(raw_text: str) -> List[List[str]]:
    """
    Делим файл на блоки по пустым строкам. Учитываем \r\n и разные числа пустых строк.
    Возвращаем список блоков, каждый — список строк.
    """
    # нормализуем переносы и убираем BOM
    text = raw_text.replace("\r\n", "\n").replace("\ufeff", "").strip()
    # разбиваем по 1+ пустых строк (строки, содержащие только пробелы, тоже пустые)
    blocks = re.split(r"(?:\n\s*\n)+", text)
    return [b.strip().splitlines() for b in blocks if b.strip()]


def parse_dialog_block(lines: List[str], min_turns: int = 2) -> Optional[Dict]:
    """
    Парсит один блок в формат:
    {"source": "...", "dialog": [{"role":"user","text":"..."}, ...]}
    Отбрасывает, если источник неизвестен или меньше min_turns валидных реплик.
    """
    if not lines:
        return None

    source = parse_source(lines[0])
    dialog: List[Dict[str, str]] = []
    for line in lines[1:]:
        parsed = _extract_role_and_text(line)
        if parsed and parsed["text"]:
            dialog.append(parsed)

    if source == "невідомо" or len(dialog) < min_turns:
        return None

    return {"source": source, "dialog": dialog}


def load_real_dialogs_from_txt(path: str = REAL_DIALOGS_PATH,
                               min_turns: int = 2,
                               preview: bool = True) -> List[Dict]:
    """
    Загружает real_dialogs.txt и возвращает список диалогов.
    - min_turns: минимальное число реплик (user/bot суммарно), чтобы считать блок валидным
    - preview: печатать краткий превью первого диалога
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

    parsed_dialogs: List[Dict] = []
    for lines in _split_blocks(raw):
        obj = parse_dialog_block(lines, min_turns=min_turns)
        if obj:
            parsed_dialogs.append(obj)

    log_to_file(f"📥 Завантажено {len(parsed_dialogs)} real-діалог(ів) з {path}")

    if preview and parsed_dialogs:
        # компактный снэпшот первого диалога — максимум по 1 реплике каждой роли
        first = parsed_dialogs[0]
        first_lines = []
        for turn in first["dialog"]:
            first_lines.append({"role": turn["role"], "text": turn["text"]})
            if len(first_lines) >= 2:
                break
        log_to_file(f"🧾 Приклад першого діалогу: "
                    f"{{'source': '{first['source']}', 'first_lines': {first_lines}}}")
    elif not parsed_dialogs:
        log_to_file("⚠️ Жодного валідного діалогу не знайдено.")

    return parsed_dialogs


if __name__ == "__main__":
    dialogs = load_real_dialogs_from_txt()
