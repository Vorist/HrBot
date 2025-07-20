import os
import json
from datetime import datetime
from typing import List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import FEEDBACK_LESSONS_PATH

router = APIRouter()

# ---------- МОДЕЛІ ---------- #
class FeedbackItem(BaseModel):
    dialog: dict
    comment: str
    status: Literal["waiting", "applied", "rejected"] = "waiting"
    from_: Literal["good", "bad", "real", "refined", "manual"] = "manual"
    timestamp: str | None = None


class FeedbackUpdate(BaseModel):
    index: int
    comment: str | None = None
    status: Literal["waiting", "applied", "rejected"] | None = None


# ---------- ДОПОМІЖНІ ФУНКЦІЇ ---------- #
def load_feedback() -> List[dict]:
    """Завантажити список фідбеків із JSONL"""
    if not os.path.exists(FEEDBACK_LESSONS_PATH):
        return []
    with open(FEEDBACK_LESSONS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines if line.strip()]


def save_feedback(feedbacks: List[dict]):
    """Зберегти список фідбеків у JSONL"""
    with open(FEEDBACK_LESSONS_PATH, "w", encoding="utf-8") as f:
        for item in feedbacks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# ---------- API ---------- #

@router.get("/api/feedback")
def get_feedback():
    """Отримати всі фідбеки"""
    return load_feedback()


@router.post("/api/feedback")
def add_feedback(item: FeedbackItem):
    """Додати новий фідбек"""
    if not item.comment.strip():
        raise HTTPException(status_code=400, detail="Коментар не може бути порожнім")
    if not isinstance(item.dialog, dict) or "dialog" not in item.dialog:
        raise HTTPException(status_code=400, detail="Некоректна структура діалогу")

    item.timestamp = item.timestamp or datetime.now().isoformat()

    feedbacks = load_feedback()
    feedbacks.append(item.dict())
    save_feedback(feedbacks)

    return {
        "message": "✅ Фідбек збережено",
        "total": len(feedbacks)
    }


@router.delete("/api/feedback/{index}")
def delete_feedback(index: int):
    """Видалити фідбек за індексом"""
    feedbacks = load_feedback()
    if 0 <= index < len(feedbacks):
        deleted = feedbacks.pop(index)
        save_feedback(feedbacks)
        return {
            "message": "🗑️ Видалено",
            "deleted": deleted
        }
    raise HTTPException(status_code=404, detail="Фідбек не знайдено")


@router.post("/api/feedback/update")
def update_feedback(update: FeedbackUpdate):
    """Оновити коментар або статус фідбеку"""
    feedbacks = load_feedback()
    if not (0 <= update.index < len(feedbacks)):
        raise HTTPException(status_code=404, detail="Фідбек не знайдено")

    if update.comment is not None:
        feedbacks[update.index]["comment"] = update.comment.strip()

    if update.status is not None:
        feedbacks[update.index]["status"] = update.status

    save_feedback(feedbacks)
    return {"message": "✏️ Фідбек оновлено"}
