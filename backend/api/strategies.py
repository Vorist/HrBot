# backend/api/strategies.py

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import REFINED_BAD_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import load_jsonl, save_jsonl, append_jsonl

router = APIRouter(
    prefix="/api/strategies",
    tags=["Strategies"]
)
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


# === 🔧 Функція для оновлення стратегії ===
def enrich_strategy(entry: dict, improved_text: str = "") -> dict:
    entry["improved"] = improved_text.strip()
    entry["timestamp"] = datetime.now().isoformat()
    entry["updated_by"] = "HR"
    entry["feedback_linked"] = True
    return entry


# === 📥 GET /api/strategies/ ===
@router.get("/", response_model=List[StrategyItem])
def get_strategies():
    """
    Повертає список стратегій із refined_bad_dialogs.jsonl
    """
    try:
        strategies = load_jsonl(REFINED_BAD_PATH)
        if not isinstance(strategies, list):
            logger.error("❌ Формат refined_bad_dialogs.jsonl некоректний")
            raise HTTPException(status_code=500, detail="Невірний формат файлу стратегій")
        logger.info(f"📥 Завантажено {len(strategies)} стратегій")
        return strategies
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при завантаженні стратегій")
        raise HTTPException(status_code=500, detail="Не вдалося завантажити стратегії")


# === ✏️ POST /api/strategies/update ===
@router.post("/update")
def update_strategy(payload: StrategyUpdate):
    """
    Оновлює поле `improved` у стратегії з індексом payload.index
    та зберігає копію в feedback_lessons.jsonl
    """
    try:
        strategies = load_jsonl(REFINED_BAD_PATH)
        if not (0 <= payload.index < len(strategies)):
            logger.error("❌ Невалідний індекс при оновленні")
            raise HTTPException(status_code=400, detail="Невалідний індекс")

        updated = enrich_strategy(strategies[payload.index], payload.improved)
        strategies[payload.index] = updated
        save_jsonl(REFINED_BAD_PATH, strategies)

        feedback_entry = {
            "from": "refined_bad_dialogs",
            "status": "improved",
            "comment": "Покращено вручну через інтерфейс",
            "dialog": updated,
            "timestamp": datetime.now().isoformat(),
        }
        append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

        logger.info("✅ Стратегію оновлено та збережено у фідбек")
        return {"message": "Стратегію оновлено та збережено у фідбек"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при оновленні стратегії")
        raise HTTPException(status_code=500, detail="Не вдалося оновити стратегію")


# === 🔃 POST /api/strategies/reorder ===
@router.post("/reorder")
def reorder_strategies(new_order: List[StrategyItem]):
    """
    Перезаписує весь список стратегій у новому порядку
    """
    try:
        ordered = [item.dict() for item in new_order]
        save_jsonl(REFINED_BAD_PATH, ordered)
        logger.info("🔃 Порядок стратегій оновлено")
        return {"message": "Порядок стратегій збережено"}
    except Exception:
        logger.exception("❌ Помилка при збереженні нового порядку стратегій")
        raise HTTPException(status_code=500, detail="Не вдалося зберегти порядок стратегій")
