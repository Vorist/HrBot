# backend/api/bad_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Literal
from datetime import datetime
import logging

from config import BAD_DIALOGS_PATH, GOOD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import (
    append_jsonl, load_jsonl, save_jsonl, validate_dialog
)

router = APIRouter()
logger = logging.getLogger(__name__)

# --- 📘 Модели --- #
class DialogLine(BaseModel):
    role: Literal["user", "bot"]
    text: str

class DialogItem(BaseModel):
    user: str = "Кандидат"
    dialog: List[DialogLine]

    @validator("dialog")
    def must_have_user_and_bot(cls, value):
        roles = {msg.role for msg in value}
        if not {"user", "bot"}.issubset(roles):
            raise ValueError("Діалог повинен містити хоча б одну репліку user і одну — bot")
        return value

class FeedbackRequest(BaseModel):
    index: int
    comment: str

# --- 📥 GET /api/bad_dialogs --- #
@router.get("/", summary="Отримати всі bad-діалоги")
def get_bad_dialogs():
    try:
        dialogs = load_jsonl(BAD_DIALOGS_PATH)
        if not isinstance(dialogs, list):
            raise HTTPException(status_code=500, detail="Неправильний формат файлу bad_dialogs.jsonl")
        logger.info(f"📥 Завантажено {len(dialogs)} bad-діалогів")
        return dialogs
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при завантаженні bad-діалогів")
        raise HTTPException(status_code=500, detail="Не вдалося завантажити bad-діалоги")

# --- ➕ POST /api/bad_dialogs --- #
@router.post("/", summary="Додати новий bad-діалог", status_code=201)
def add_bad_dialog(item: DialogItem):
    dialog_dict = [line.dict() for line in item.dialog]

    if not validate_dialog(dialog_dict):
        raise HTTPException(status_code=422, detail="Діалог має містити чергування user → bot → ...")

    new_entry = {
        "user": item.user.strip() or "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": dialog_dict
    }

    existing = load_jsonl(BAD_DIALOGS_PATH)
    if any(d.get("dialog") == new_entry["dialog"] for d in existing):
        logger.warning("⚠️ Дублювання bad-діалогу")
        raise HTTPException(status_code=409, detail="Такий діалог вже існує")

    append_jsonl(BAD_DIALOGS_PATH, new_entry)
    logger.info("✅ Додано bad-діалог")
    return {"success": True, "added": new_entry}

# --- 🗑️ DELETE /api/bad_dialogs/{index} --- #
@router.delete("/{index}", summary="Видалити bad-діалог за індексом")
def delete_bad_dialog(index: int):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу bad_dialogs.jsonl")
    if index < 0 or index >= len(dialogs):
        logger.error(f"❌ Індекс {index} поза межами")
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    deleted = dialogs.pop(index)
    save_jsonl(BAD_DIALOGS_PATH, dialogs)
    logger.info(f"🗑️ Видалено bad-діалог #{index}")
    return {"success": True, "deleted": deleted}

# --- 🔁 POST /api/bad_dialogs/feedback --- #
@router.post("/feedback", summary="Позначити bad → good і зберегти фідбек")
def mark_bad_as_good(req: FeedbackRequest):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу bad_dialogs.jsonl")
    if req.index < 0 or req.index >= len(dialogs):
        logger.error(f"❌ Індекс {req.index} невалідний")
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    dialog = dialogs.pop(req.index)
    save_jsonl(BAD_DIALOGS_PATH, dialogs)

    dialog.setdefault("user", "Кандидат")
    dialog.setdefault("date", datetime.now().strftime("%Y-%m-%d"))

    append_jsonl(GOOD_DIALOGS_PATH, dialog)

    feedback_entry = {
        "from": "bad_dialogs",
        "status": "moved_to_good",
        "comment": req.comment.strip(),
        "dialog": dialog,
        "timestamp": datetime.now().isoformat(),
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    logger.info("✅ Переміщено bad → good та збережено фідбек")
    return {"success": True, "moved_to": "good", "feedback_saved": True}
