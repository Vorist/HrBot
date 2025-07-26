from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime
import os
import json
import hashlib
import logging

from config import FEEDBACK_COMMENTS_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl, validate_dialog

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------- 📦 Моделі ---------- #

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

# ---------- 📁 Функції ---------- #

def get_dialog_hash(dialog: dict) -> str:
    return hashlib.md5(json.dumps(dialog, sort_keys=True).encode("utf-8")).hexdigest()

# ---------- 🔗 API ---------- #

@router.get("/")
def get_feedback():
    """📥 Отримати всі фідбеки (коментарі менеджера)"""
    logger.info("📥 Отримання всіх фідбеків")
    return load_jsonl(FEEDBACK_COMMENTS_PATH)

@router.post("/")
def add_feedback(item: FeedbackItem):
    """➕ Додати новий фідбек"""
    if not item.comment.strip():
        raise HTTPException(status_code=400, detail="Коментар не може бути порожнім")
    if not isinstance(item.dialog, dict) or "dialog" not in item.dialog:
        raise HTTPException(status_code=400, detail="Некоректна структура діалогу")

    dialog_list = item.dialog.get("dialog")
    if not isinstance(dialog_list, list) or not validate_dialog(dialog_list):
        raise HTTPException(status_code=422, detail="Діалог має містити чергування user → bot → user → ...")

    item.timestamp = item.timestamp or datetime.now().isoformat()
    item.dialog_id = get_dialog_hash(item.dialog)

    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)

    if any(fb.get("dialog_id") == item.dialog_id for fb in feedbacks):
        raise HTTPException(status_code=409, detail="Фідбек для цього діалогу вже існує")

    feedbacks.append(item.dict())
    save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
    logger.info("✅ Фідбек успішно додано")

    return {
        "message": "✅ Фідбек збережено",
        "total": len(feedbacks)
    }

@router.delete("/{index}")
def delete_feedback(index: int):
    """🗑️ Видалити фідбек за індексом"""
    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
    if 0 <= index < len(feedbacks):
        deleted = feedbacks.pop(index)
        save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
        logger.info(f"🗑️ Видалено фідбек з індексом {index}")
        return {"message": "🗑️ Видалено", "deleted": deleted}
    raise HTTPException(status_code=404, detail="Фідбек не знайдено")

@router.post("/update")
def update_feedback(update: FeedbackUpdate):
    """✏️ Оновити фідбек"""
    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)
    if not (0 <= update.index < len(feedbacks)):
        raise HTTPException(status_code=404, detail="Фідбек не знайдено")

    if update.comment is not None:
        feedbacks[update.index]["comment"] = update.comment.strip()

    if update.status is not None:
        feedbacks[update.index]["status"] = update.status

    save_jsonl(FEEDBACK_COMMENTS_PATH, feedbacks)
    logger.info(f"✏️ Оновлено фідбек з індексом {update.index}")
    return {"message": "✏️ Фідбек оновлено"}
