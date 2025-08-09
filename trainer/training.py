#!/usr/bin/env python3
# trainer/training.py

import os
import json
from datetime import datetime
import logging
import sys

# Добавляем корень для поиска всех нужных модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    REAL_DIALOGS_PATH, REAL_DIALOGS_PATH,
    GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH,
    LOG_PATH  # если в config нет LOG_PATH — заведи!
)

from train_from_good import train_on_good_dialogs
from train_from_bad import train_on_bad_dialogs
from feedback_processor import process_feedbacks
from real_dialog_loader import load_real_dialogs_from_txt
from learner import learn_from_dialogs

# --- Логирование ---
LOGS_DIR = os.path.dirname(LOG_PATH)
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def log(message: str, level: str = "info"):
    getattr(logger, level)(message)
    print(f"{datetime.now():[%Y-%m-%d %H:%M:%S]} {message}")

def count_jsonl_lines(path: str) -> int:
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

# --- Обучение на real_dialogs.txt ---
def train_on_real():
    log("🔵 Старт навчання на real_dialogs.txt")
    dialogs = load_real_dialogs_from_txt(REAL_DIALOGS_PATH)
    total = len(dialogs)
    if total == 0:
        log("⚠️ real_dialogs.txt порожній або не знайдено жодного діалогу", "warning")
        return {"status": "warning", "source": "real", "count": 0}
    try:
        learn_from_dialogs(dialogs)
        log(f"✅ Навчено на {total} реальних діалогах")
        return {"status": "ok", "source": "real", "count": total}
    except Exception as e:
        log(f"❌ Помилка під час навчання на real: {e}", "error")
        return {"status": "error", "source": "real", "error": str(e)}

# --- Обучение на good/bad/feedback ---
def train_on_jsonl(source: str, path: str, train_fn):
    log(f"🟢 Старт навчання на {os.path.basename(path)}")
    if not os.path.exists(path):
        log(f"⚠️ Файл не знайдено: {path}", "warning")
        return {"status": "error", "source": source, "reason": "file not found"}
    count = count_jsonl_lines(path)
    try:
        train_fn()
        log(f"✅ Навчено на {count} записах з {source}")
        return {"status": "ok", "source": source, "count": count}
    except Exception as e:
        log(f"❌ Помилка навчання на {source}: {e}", "error")
        return {"status": "error", "source": source, "error": str(e)}

def train(source: str):
    """
    Главная функция: запускает обучение по источнику
    source = real / good / bad / feedback / all
    """
    if source == "real":
        return train_on_real()
    elif source == "good":
        return train_on_jsonl("good", GOOD_DIALOGS_PATH, train_on_good_dialogs)
    elif source == "bad":
        return train_on_jsonl("bad", BAD_DIALOGS_PATH, train_on_bad_dialogs)
    elif source == "feedback":
        return train_on_jsonl("feedback", FEEDBACK_LESSONS_PATH, process_feedbacks)
    elif source == "all":
        results = []
        for src in ["real", "good", "bad", "feedback"]:
            results.append(train(src))
        return results
    else:
        msg = f"Unknown source: {source}"
        log(f"❌ {msg}", "error")
        return {"status": "error", "reason": msg}

if __name__ == "__main__":
    result = train("all")
    print(json.dumps(result, ensure_ascii=False, indent=2))
