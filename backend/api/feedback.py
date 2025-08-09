# backend/api/feedback.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime
import hashlib
import logging

from config import FEEDBACK_COMMENTS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl, validate_dialog

router = APIRouter()
logger = logging.getLogger(__name__)

# --- 📦 Pydantic-моделі --- #
class FeedbackItem(BaseModel):
    dialog: dict
    comment: str
    status: Literal["waiting", "applied", "rejected"] = "waiting"
    from_: Literal["good", "bad", "real", "refined", "manual"] = "manual"
    timestamp: Optional[str] = None
    dialog_id: Optional[str] = None

class FeedbackUpdate(BaseModel):
    index: int
    comment: Optional[str] = None
    status: Optional[Literal["waiting", "applied", "rejected"]] = None

# --- 🔧 Утиліти --- #
def get_dialog_hash(dialog: dict) -> str:
    """MD5 хеш діалогу для ідентифікації."""
    return hashlib.md5(str(dialog).encode("utf-8")).hexdigest()

# --- 📡 API-маршрути --- #
@router.get("/", summary="Отримати всі фідбеки", response_model=List[dict])
def get_feedback():
    """Повернути всі фідбеки (або порожній список)."""
    try:
        feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
        if not isinstance(feedbacks, list):
            raise HTTPException(status_code=500, detail="Некоректний формат фідбеків")
        logger.info(f"📥 Завантажено {len(feedbacks)} фідбеків")
        return feedbacks
    except Exception:
        logger.exception("❌ Помилка при завантаженні фідбеків")
        raise HTTPException(status_code=500, detail="Не вдалося завантажити фідбеки")

@router.post("/", summary="Додати фідбек", status_code=201)
def add_feedback(item: FeedbackItem):
    """Додати новий фідбек до feedback_comments.jsonl."""
    if not item.comment.strip():
        raise HTTPException(status_code=400, detail="Коментар не може бути порожнім")
    if not isinstance(item.dialog, dict) or "dialog" not in item.dialog:
        raise HTTPException(status_code=400, detail="Некоректна структура діалогу")
    dialog_list = item.dialog["dialog"]
    if not isinstance(dialog_list, list) or not validate_dialog(dialog_list):
        raise HTTPException(status_code=422, detail="Діалог має містити чергування user → bot")

    item.timestamp = item.timestamp or datetime.now().isoformat()
    item.dialog_id = get_dialog_hash(item.dialog)

    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
    # Уникнуть дублей по dialog_id
    if any(fb.get("dialog_id") == item.dialog_id for fb in feedbacks):
        raise HTTPException(status_code=409, detail="Фідбек для цього діалогу вже існує")

    feedbacks.append(item.dict())
    save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
    logger.info("✅ Фідбек успішно додано")

    return {"success": True, "message": "Фідбек збережено", "total": len(feedbacks)}

@router.delete("/{index}", summary="Видалити фідбек за індексом")
def delete_feedback(index: int):
    """Видалити фідбек за індексом."""
    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
    if not isinstance(feedbacks, list):
        raise HTTPException(status_code=500, detail="Некоректний формат фідбеків")
    if index < 0 or index >= len(feedbacks):
        raise HTTPException(status_code=404, detail="Фідбек не знайдено")

    deleted = feedbacks.pop(index)
    save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
    logger.info(f"🗑️ Видалено фідбек з індексом {index}")
    return {"success": True, "deleted": deleted}

@router.post("/update", summary="Оновити фідбек")
def update_feedback(update: FeedbackUpdate):
    """Оновити запис фідбеку (коментар або статус)."""
    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
    if not isinstance(feedbacks, list):
        raise HTTPException(status_code=500, detail="Некоректний формат фідбеків")
    if update.index < 0 or update.index >= len(feedbacks):
        raise HTTPException(status_code=404, detail="Фідбек не знайдено")

    if update.comment is not None:
        feedbacks[update.index]["comment"] = update.comment.strip()
    if update.status is not None:
        feedbacks[update.index]["status"] = update.status

    save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
    logger.info(f"✏️ Оновлено фідбек з індексом {update.index}")
    return {"success": True, "message": "Фідбек оновлено"}
