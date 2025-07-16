import os
import sys
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# sys.path для config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config import REFINED_BAD_PATH, FEEDBACK_LESSONS_PATH

router = APIRouter()

# --- Моделі --- #
class StrategyUpdate(BaseModel):
    index: int
    improved: str

class StrategyItem(BaseModel):
    context: str
    original: str
    improved: str = ""
    strategy: str = ""
    feedback: List[str] = []
    updated_by: str = "HR"
    timestamp: str = ""
    feedback_linked: bool = False


# --- JSONL --- #
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


# --- GET: всі стратегії --- #
@router.get("/api/strategies")
def get_strategies():
    return load_jsonl(REFINED_BAD_PATH)


# --- POST: оновлення однієї стратегії --- #
@router.post("/api/strategies/update")
def update_strategy(payload: StrategyUpdate):
    strategies = load_jsonl(REFINED_BAD_PATH)

    if payload.index < 0 or payload.index >= len(strategies):
        raise HTTPException(status_code=400, detail="Недійсний індекс")

    # Оновлення
    strategies[payload.index]["improved"] = payload.improved.strip()
    strategies[payload.index]["timestamp"] = datetime.now().isoformat()
    strategies[payload.index]["updated_by"] = "HR"
    strategies[payload.index]["feedback_linked"] = True

    save_jsonl(REFINED_BAD_PATH, strategies)

    # Зберегти фідбек
    feedback_entry = {
        "from": "refined_bad_dialogs",
        "comment": "Покращено вручну через інтерфейс",
        "dialog": strategies[payload.index],
        "status": "improved",
        "timestamp": datetime.now().isoformat()
    }
    append_feedback(feedback_entry)

    return {"message": "✅ Покращено відповідь + записано у feedback_lessons"}


# --- POST: перезапис усіх у новому порядку --- #
@router.post("/api/strategies/reorder")
def reorder_strategies(new_order: List[StrategyItem]):
    clean_data = [item if isinstance(item, dict) else item.dict() for item in new_order]
    save_jsonl(REFINED_BAD_PATH, clean_data)
    return {"message": "✅ Порядок оновлено"}


# --- Допоміжна функція для запису фідбеку --- #
def append_feedback(entry):
    with open(FEEDBACK_LESSONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
