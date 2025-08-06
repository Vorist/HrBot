# backend/api/bad_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Literal
from datetime import datetime
import logging

from config import BAD_DIALOGS_PATH, GOOD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl, validate_dialog

router = APIRouter()
logger = logging.getLogger(__name__)


# --- 📘 Моделі --- #
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


# --- 📥 Отримання BAD діалогів --- #
@router.get("", summary="Get all bad dialogs")
@router.get("/", include_in_schema=False)
def get_bad_dialogs():
    """
    Повертає список усіх bad-діалогів.
    """
    try:
        dialogs = load_jsonl(BAD_DIALOGS_PATH)
        if not isinstance(dialogs, list):
            raise HTTPException(status_code=500, detail="Неправильний формат bad_dialogs.jsonl")
        logger.info(f"📥 Завантажено {len(dialogs)} bad-діалогів")
        return dialogs
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при завантаженні bad-діалогів")
        raise HTTPException(status_code=500, detail="Не вдалося завантажити bad-діалоги")


# --- ➕ Додавання BAD діалогу --- #
@router.post("", summary="Add a new bad dialog", status_code=201)
@router.post("/", include_in_schema=False)
def add_bad_dialog(item: DialogItem):
    """
    Додає новий bad-діалог.
    """
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
    return new_entry


# --- 🗑️ Видалення BAD діалогу --- #
@router.delete("/{index}", summary="Delete bad dialog by index")
def delete_bad_dialog(index: int):
    """
    Видаляє bad-діалог за індексом.
    """
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if not (0 <= index < len(dialogs)):
        logger.error(f"❌ Індекс {index} поза межами")
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    deleted = dialogs.pop(index)
    save_jsonl(BAD_DIALOGS_PATH, dialogs)
    logger.info(f"🗑️ Видалено bad-діалог #{index}")
    return {"deleted": deleted}


# --- 🔁 Переміщення в GOOD + фідбек --- #
@router.post("/feedback", summary="Mark bad dialog as good with feedback")
def mark_bad_as_good(req: FeedbackRequest):
    """
    Переміщує bad-діалог у good-діалоги та зберігає фідбек.
    """
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if not (0 <= req.index < len(dialogs)):
        logger.error(f"❌ Індекс {req.index} невалідний")
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    dialog = dialogs.pop(req.index)
    save_jsonl(BAD_DIALOGS_PATH, dialogs)

    # Гарантуємо наявність полів user і date
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
    return {"moved_to": "good", "feedback_saved": True}
