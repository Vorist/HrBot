import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from config import FEEDBACK_LESSONS_PATH

router = APIRouter()

# --- Модель фідбеку --- #
class FeedbackItem(BaseModel):
    dialog: dict                      # Повний діалог (user/bot)
    comment: str                      # Коментар HR
    status: str = "waiting"           # ⏳ waiting / ✅ applied / ❌ rejected
    from_: str = "manual"             # Джерело: good/bad/real/refined
    timestamp: str = None             # Автоматично проставляється


# --- Завантажити всі фідбеки --- #
def load_feedback():
    if not os.path.exists(FEEDBACK_LESSONS_PATH):
        return []
    with open(FEEDBACK_LESSONS_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


# --- Зберегти всі фідбеки --- #
def save_feedback(feedbacks):
    with open(FEEDBACK_LESSONS_PATH, "w", encoding="utf-8") as f:
        for item in feedbacks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# --- Додати новий фідбек --- #
@router.post("/api/feedback")
def add_feedback(item: FeedbackItem):
    item.timestamp = item.timestamp or datetime.now().isoformat()
    data = load_feedback()
    data.append(item.dict())
    save_feedback(data)
    return {"message": "✅ Фідбек збережено", "total": len(data)}


# --- Отримати всі фідбеки --- #
@router.get("/api/feedback")
def get_feedback():
    return load_feedback()


# --- Видалити фідбек за індексом --- #
@router.delete("/api/feedback/{index}")
def delete_feedback(index: int):
    feedbacks = load_feedback()
    if 0 <= index < len(feedbacks):
        deleted = feedbacks.pop(index)
        save_feedback(feedbacks)
        return {"message": "🗑️ Видалено", "deleted": deleted}
    raise HTTPException(status_code=404, detail="Feedback not found")


# --- Оновити фідбек (статус або коментар) --- #
class FeedbackUpdate(BaseModel):
    index: int
    comment: str = None
    status: str = None

@router.post("/api/feedback/update")
def update_feedback(update: FeedbackUpdate):
    feedbacks = load_feedback()
    if 0 <= update.index < len(feedbacks):
        if update.comment is not None:
            feedbacks[update.index]["comment"] = update.comment
        if update.status is not None:
            feedbacks[update.index]["status"] = update.status
        save_feedback(feedbacks)
        return {"message": "✏️ Фідбек оновлено"}
    raise HTTPException(status_code=404, detail="Feedback not found")
