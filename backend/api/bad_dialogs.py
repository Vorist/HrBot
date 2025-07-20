from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Literal
import logging
from datetime import datetime

from config import BAD_DIALOGS_PATH, GOOD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH
from utils.jsonl_utils import load_jsonl, save_jsonl, append_jsonl

router = APIRouter()
logger = logging.getLogger(__name__)


# --- 📦 Моделі --- #

class DialogLine(BaseModel):
    role: Literal["user", "bot"]
    text: str


class DialogItem(BaseModel):
    user: str = "Кандидат"
    dialog: List[DialogLine]

    @validator("dialog")
    def validate_dialog_has_roles(cls, value):
        roles = [msg.role for msg in value]
        if "user" not in roles or "bot" not in roles:
            raise ValueError("Діалог повинен містити хоча б одного user і одного bot")
        return value


class FeedbackRequest(BaseModel):
    index: int
    comment: str


# --- 📥 Отримання всіх BAD діалогів --- #
@router.get("/api/bad_dialogs")
def get_bad_dialogs():
    logger.info("📥 Отримання списку bad-діалогів")
    return load_jsonl(BAD_DIALOGS_PATH)


# --- ➕ Додавання нового BAD діалогу --- #
@router.post("/api/bad_dialogs")
def add_bad_dialog(item: DialogItem):
    new_entry = {
        "user": item.user,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": [line.dict() for line in item.dialog]
    }

    existing = load_jsonl(BAD_DIALOGS_PATH)
    if any(d.get("dialog") == new_entry["dialog"] for d in existing):
        logger.warning("⚠️ Спроба додати дубльований діалог")
        raise HTTPException(status_code=409, detail="Duplicate dialog")

    append_jsonl(BAD_DIALOGS_PATH, new_entry)
    logger.info("✅ Новий bad-діалог успішно додано")
    return new_entry


# --- 🗑️ Видалення BAD діалогу за індексом --- #
@router.delete("/api/bad_dialogs/{index}")
def delete_bad_dialog(index: int):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)

    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(BAD_DIALOGS_PATH, dialogs)
        logger.info(f"🗑️ Видалено bad-діалог з індексом {index}")
        return {"deleted": deleted}

    logger.error(f"❌ Діалог з індексом {index} не знайдено")
    raise HTTPException(status_code=404, detail="Dialog not found")


# --- 🔁 Переміщення в GOOD + збереження фідбеку --- #
@router.post("/api/bad_dialogs/feedback")
def mark_as_good(req: FeedbackRequest):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)

    if not (0 <= req.index < len(dialogs)):
        logger.error(f"❌ Діалог з індексом {req.index} не знайдено")
        raise HTTPException(status_code=404, detail="Dialog not found")

    dialog = dialogs.pop(req.index)
    save_jsonl(BAD_DIALOGS_PATH, dialogs)
    append_jsonl(GOOD_DIALOGS_PATH, dialog)

    feedback_entry = {
        "from": "bad_dialogs",
        "comment": req.comment,
        "dialog": dialog,
        "status": "moved_to_good",
        "timestamp": datetime.now().isoformat()
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    logger.info("📤 Діалог перенесено з bad → good та збережено фідбек")
    return {"moved_to": "good", "feedback_saved": True}
