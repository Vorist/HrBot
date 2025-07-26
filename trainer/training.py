import os
import json
from datetime import datetime

from train_from_good import train_on_good_dialogs
from train_from_bad import train_on_bad_dialogs
from feedback_processor import process_feedbacks
from real_dialog_loader import load_real_dialogs_from_txt
from learner import learn_from_dialogs

DATA_DIR = "data"
LOG_PATH = "logs/training_log.txt"


def log(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {message}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def count_lines(path: str) -> int:
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f if _.strip())


def train_on_real():
    path = os.path.join(DATA_DIR, "real_dialogs.txt")
    log("🔵 Навчання на real_dialogs.txt")

    dialogs = load_real_dialogs_from_txt(path)
    count = len(dialogs)

    if count == 0:
        log("⚠️ Немає валідних real-діалогів")
        return {"status": "warning", "source": "real", "count": 0}

    learn_from_dialogs()
    return {"status": "ok", "source": "real", "count": count}


def train_on_jsonl(source: str):
    path = os.path.join(DATA_DIR, f"{source}_dialogs.jsonl")
    log(f"🟢 Навчання на {source}_dialogs.jsonl")

    if not os.path.exists(path):
        log(f"⚠️ Файл {path} не знайдено")
        return {"status": "error", "source": source, "reason": "file not found"}

    count = count_lines(path)

    if source == "good":
        train_on_good_dialogs()
    elif source == "bad":
        train_on_bad_dialogs()
    elif source == "feedback":
        process_feedbacks()

    return {"status": "ok", "source": source, "count": count}


def train(source: str):
    if source == "real":
        return train_on_real()
    elif source in ["good", "bad", "feedback"]:
        return train_on_jsonl(source)
    elif source == "all":
        results = []
        for src in ["good", "bad", "feedback", "real"]:
            results.append(train(src))
        return results
    else:
        return {"status": "error", "reason": f"Unknown source: {source}"}


if __name__ == "__main__":
    result = train("all")
    print(json.dumps(result, indent=2, ensure_ascii=False))
