import os
import sys
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from config import REFINED_BAD_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl

router = APIRouter()
logger = logging.getLogger(__name__)


# === 📦 Pydantic-моделі ===
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


# === 🔧 Функція збагачення стратегії ===
def enrich_strategy(entry: dict, improved_text: str = "") -> dict:
    entry["improved"] = improved_text.strip()
    entry["timestamp"] = datetime.now().isoformat()
    entry["updated_by"] = "HR"
    entry["feedback_linked"] = True
    return entry


# === 📥 GET /api/strategies ===
@router.get("/api/strategies")
def get_strategies():
    logger.info("📥 Завантаження refined_bad_dialogs")
    return load_jsonl(REFINED_BAD_PATH)


# === ✏️ POST /api/strategies/update ===
@router.post("/api/strategies/update")
def update_strategy(payload: StrategyUpdate):
    strategies = load_jsonl(REFINED_BAD_PATH)

    if not (0 <= payload.index < len(strategies)):
        logger.error("❌ Невалідний індекс при оновленні")
        raise HTTPException(status_code=400, detail="Невалідний індекс")

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

    logger.info("✅ Стратегію оновлено та збережено у фідбек")
    return {"message": "✅ Стратегію оновлено та збережено у фідбек"}


# === 🔃 POST /api/strategies/reorder ===
@router.post("/api/strategies/reorder")
def reorder_strategies(new_order: List[StrategyItem]):
    try:
        ordered = [item.dict() if isinstance(item, StrategyItem) else item for item in new_order]
        save_jsonl(REFINED_BAD_PATH, ordered)
        logger.info("🔃 Порядок refined_bad_dialogs оновлено")
        return {"message": "✅ Порядок стратегій збережено"}
    except Exception as e:
        logger.exception("❌ Помилка при reorder")
        raise HTTPException(status_code=500, detail=f"Помилка при reorder: {str(e)}")
