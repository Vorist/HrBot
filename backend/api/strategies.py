# backend/api/strategies.py

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import REFINED_BAD_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import load_jsonl, save_jsonl, append_jsonl

router = APIRouter()
logger = logging.getLogger(__name__)

# === 📦 Pydantic-модели ===
class StrategyItem(BaseModel):
    context: str = Field(..., description="Контекст, в якому виникла проблема")
    original: str = Field(..., description="Початкова (погана) відповідь")
    improved: str = Field("", description="Покращена відповідь")
    strategy: str = Field("", description="Стратегія/прийом для покращення")
    feedback: List[str] = Field(default_factory=list, description="Коментарі менеджера")
    updated_by: str = Field("HR", description="Ким оновлено")
    timestamp: str = Field("", description="Дата останнього оновлення")
    feedback_linked: bool = Field(False, description="Чи пов'язано з фідбеком")

class StrategyUpdate(BaseModel):
    index: int
    improved: str

# === 🔧 Утиліта для оновлення стратегії ===
def enrich_strategy(entry: dict, improved_text: str = "") -> dict:
    entry["improved"] = improved_text.strip()
    entry["timestamp"] = datetime.now().isoformat()
    entry["updated_by"] = "HR"
    entry["feedback_linked"] = True
    return entry

# === 📥 GET /api/strategies ===
@router.get("/", response_model=List[StrategyItem], summary="Отримати всі стратегії")
def get_strategies():
    """
    Повертає список стратегій із refined_bad_dialogs.jsonl.
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
@router.post("/update", summary="Оновити покращену відповідь у стратегії")
def update_strategy(payload: StrategyUpdate):
    """
    Оновлює поле improved для стратегії за індексом
    та зберігає копію у feedback_lessons.jsonl для історії.
    """
    try:
        strategies = load_jsonl(REFINED_BAD_PATH)
        if not (0 <= payload.index < len(strategies)):
            logger.error("❌ Невалідний індекс при оновленні")
            raise HTTPException(status_code=400, detail="Невалідний індекс")

        updated_entry = enrich_strategy(strategies[payload.index], payload.improved)
        strategies[payload.index] = updated_entry
        save_jsonl(REFINED_BAD_PATH, strategies)

        feedback_entry = {
            "from": "refined_bad_dialogs",
            "status": "improved",
            "comment": "Покращено вручну через інтерфейс",
            "dialog": updated_entry,
            "timestamp": datetime.now().isoformat(),
        }
        append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

        logger.info(f"✅ Стратегію #{payload.index} оновлено та збережено у фідбек")
        return {"message": "Стратегію оновлено та збережено у фідбек"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при оновленні стратегії")
        raise HTTPException(status_code=500, detail="Не вдалося оновити стратегію")

# === 🔃 POST /api/strategies/reorder ===
@router.post("/reorder", summary="Змінити порядок стратегій")
def reorder_strategies(new_order: List[StrategyItem]):
    """
    Перезаписує весь список стратегій у файлі у новому порядку.
    """
    try:
        ordered_list = [item.dict() for item in new_order]
        save_jsonl(REFINED_BAD_PATH, ordered_list)
        logger.info(f"🔃 Порядок стратегій оновлено: {len(ordered_list)} шт.")
        return {"message": "Порядок стратегій збережено", "count": len(ordered_list)}
    except Exception:
        logger.exception("❌ Помилка при збереженні нового порядку стратегій")
        raise HTTPException(status_code=500, detail="Не вдалося зберегти порядок стратегій")
