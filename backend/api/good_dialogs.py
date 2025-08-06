# backend/api/good_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Literal
from datetime import datetime
from hashlib import md5
import logging

from config import GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl, validate_dialog

router = APIRouter()
logger = logging.getLogger(__name__)


# 📦 Pydantic-моделі
class Replica(BaseModel):
    role: Literal["user", "bot"]
    text: str


class DialogItem(BaseModel):
    user: str = "Кандидат"
    dialog: List[Replica]

    @validator("dialog")
    def must_include_user_and_bot(cls, v):
        roles = {r.role for r in v}
        if not {"user", "bot"}.issubset(roles):
            raise ValueError("Діалог повинен містити принаймні одну user і одну bot репліку")
        return v


class FeedbackRequest(BaseModel):
    index: int
    comment: str


def _dialog_hash(dialog: List[dict]) -> str:
    """Stable hash of a dialog list."""
    sorted_serialized = str(sorted(dialog, key=lambda d: (d["role"], d["text"])))
    return md5(sorted_serialized.encode("utf-8")).hexdigest()


# 📡 API-маршрути

@router.get("/", summary="Get all good dialogs")
def get_good_dialogs():
    """📥 Отримати всі good-діалоги"""
    try:
        dialogs = load_jsonl(GOOD_DIALOGS_PATH)
        if not isinstance(dialogs, list):
            raise RuntimeError("Expected list of dialogs")
        logger.info(f"📥 Завантажено {len(dialogs)} good-діалогів")
        return dialogs
    except Exception:
        logger.exception("❌ Помилка при завантаженні good-діалогів")
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити хороші діалоги"
        )


@router.post("/", summary="Add a new good dialog", status_code=201)
def add_good_dialog(item: DialogItem):
    """➕ Додати новий good-діалог"""
    dialog_data = [r.dict() for r in item.dialog]

    if not validate_dialog(dialog_data):
        raise HTTPException(
            status_code=422,
            detail="Діалог має містити чергування user → bot → user → ..."
        )

    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    new_entry = {
        "user": item.user.strip() or "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": dialog_data
    }

    new_hash = _dialog_hash(new_entry["dialog"])
    existing_hashes = {_dialog_hash(d["dialog"]) for d in dialogs if "dialog" in d}
    if new_hash in existing_hashes:
        raise HTTPException(status_code=409, detail="Такий діалог вже існує")

    append_jsonl(GOOD_DIALOGS_PATH, new_entry)
    logger.info("✅ Додано новий good-діалог")
    return new_entry


@router.delete("/{index}", summary="Delete good dialog by index")
def delete_good_dialog(index: int):
    """🗑️ Видалити good-діалог за індексом"""
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу")
    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(GOOD_DIALOGS_PATH, dialogs)
        logger.info(f"🗑️ Видалено good-діалог #{index}")
        return {"deleted": deleted}
    else:
        raise HTTPException(status_code=404, detail="Діалог не знайдено")


@router.post("/feedback", summary="Mark a good dialog as bad")
def mark_as_bad(req: FeedbackRequest):
    """🔁 Позначити діалог як bad + зберегти фідбек"""
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу")

    if not (0 <= req.index < len(dialogs)):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    dialog = dialogs.pop(req.index)
    save_jsonl(GOOD_DIALOGS_PATH, dialogs)
    append_jsonl(BAD_DIALOGS_PATH, dialog)

    feedback_entry = {
        "from": "good_dialogs",
        "status": "moved_to_bad",
        "comment": req.comment.strip(),
        "dialog": dialog,
        "timestamp": datetime.now().isoformat()
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    logger.info("📤 Переміщено good → bad та збережено фідбек")
    return {"moved_to": "bad", "feedback_saved": True}
