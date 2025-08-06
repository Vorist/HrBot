#!/usr/bin/env python3
# trainer/training.py

import os
import json
from datetime import datetime
import logging

from train_from_good import train_on_good_dialogs
from train_from_bad import train_on_bad_dialogs
from feedback_processor import process_feedbacks
from real_dialog_loader import load_real_dialogs_from_txt
from learner import learn_from_dialogs
from config import REAL_DIALOGS_TXT_PATH

# Папка для логів
LOG_PATH = os.path.join("logs", "training_log.txt")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def log(message: str, level: str = "info"):
    """Запис у файл логу та вивід в консоль."""
    getattr(logger, level)(message)
    print(f"{datetime.now():[%Y-%m-%d %H:%M:%S]} {message}")


def count_lines(path: str) -> int:
    """Порахує непусті строки у файлі."""
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def train_on_real():
    """
    Навчання на реальних діалогах з real_dialogs.txt.
    Кожен блок (параграф) в тексті — окремий діалог.
    """
    log("🔵 Старт навчання на real_dialogs.txt")
    # Завантажуємо блоки діалогів
    dialogs = load_real_dialogs_from_txt(REAL_DIALOGS_TXT_PATH)
    total = len(dialogs)
    if total == 0:
        log("⚠️ real_dialogs.txt порожній або не знайдено жодного діалогу", level="warning")
        return {"status": "warning", "source": "real", "count": 0}

    # Передаємо списком блоків у ваш механізм навчання
    try:
        learn_from_dialogs(dialogs)
        log(f"✅ Навчено на {total} реальних діалогах")
        return {"status": "ok", "source": "real", "count": total}
    except Exception as e:
        log(f"❌ Помилка під час навчання на real: {e}", level="error")
        return {"status": "error", "source": "real", "error": str(e)}


def train_on_jsonl(source: str):
    """
    Навчання на JSONL-файлах: good, bad або feedback.
    """
    path = os.path.join("data", f"{source}_dialogs.jsonl")
    log(f"🟢 Старт навчання на {source}_dialogs.jsonl")
    if not os.path.exists(path):
        log(f"⚠️ Файл не знайдено: {path}", level="warning")
        return {"status": "error", "source": source, "reason": "file not found"}

    count = count_lines(path)
    try:
        if source == "good":
            train_on_good_dialogs()
        elif source == "bad":
            train_on_bad_dialogs()
        elif source == "feedback":
            process_feedbacks()
        log(f"✅ Навчено на {count} записах з {source}", level="info")
        return {"status": "ok", "source": source, "count": count}
    except Exception as e:
        log(f"❌ Помилка навчання на {source}: {e}", level="error")
        return {"status": "error", "source": source, "error": str(e)}


def train(source: str):
    """
    Головна функція: обирає джерело.
    Якщо source == "all", послідовно запускає real, good, bad, feedback.
    """
    if source == "real":
        return train_on_real()
    elif source in ["good", "bad", "feedback"]:
        return train_on_jsonl(source)
    elif source == "all":
        results = []
        for src in ["real", "good", "bad", "feedback"]:
            results.append(train(src))
        return results
    else:
        msg = f"Unknown source: {source}"
        log(f"❌ {msg}", level="error")
        return {"status": "error", "reason": msg}


if __name__ == "__main__":
    result = train("all")
    print(json.dumps(result, ensure_ascii=False, indent=2))
