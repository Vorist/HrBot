import os
import sys
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# Додати корінь проєкту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config import REFINED_BAD_PATH, FEEDBACK_LESSONS_PATH

router = APIRouter()

# --- Pydantic моделі --- #
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

# --- JSONL утиліти --- #
def load_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def save_jsonl(path: str, data: list):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def append_jsonl(path: str, item: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def enrich_strategy(entry: dict, improved_text: str = "") -> dict:
    entry["improved"] = improved_text.strip()
    entry["timestamp"] = datetime.now().isoformat()
    entry["updated_by"] = "HR"
    entry["feedback_linked"] = True
    return entry

# --- GET /api/strategies --- #
@router.get("/api/strategies")
def get_strategies():
    return load_jsonl(REFINED_BAD_PATH)

# --- POST /api/strategies/update --- #
@router.post("/api/strategies/update")
def update_strategy(payload: StrategyUpdate):
    strategies = load_jsonl(REFINED_BAD_PATH)

    if payload.index < 0 or payload.index >= len(strategies):
        raise HTTPException(status_code=400, detail="❌ Недійсний індекс")

    strategy = enrich_strategy(strategies[payload.index], payload.improved)
    strategies[payload.index] = strategy
    save_jsonl(REFINED_BAD_PATH, strategies)

    feedback_entry = {
        "from": "refined_bad_dialogs",
        "status": "improved",
        "comment": "Покращено вручну через інтерфейс",
        "dialog": strategy,
        "timestamp": datetime.now().isoformat(),
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    return {"message": "✅ Стратегію оновлено + фідбек збережено"}

# --- POST /api/strategies/reorder --- #
@router.post("/api/strategies/reorder")
def reorder_strategies(new_order: List[StrategyItem]):
    try:
        ordered = [item.dict() if isinstance(item, StrategyItem) else item for item in new_order]
        save_jsonl(REFINED_BAD_PATH, ordered)
        return {"message": "✅ Порядок оновлено успішно"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Помилка при reorder: {str(e)}")
