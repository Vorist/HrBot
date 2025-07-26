from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Literal
from datetime import datetime
from hashlib import md5
import json
import logging

from config import GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH
from backend.utils.jsonl_utils import append_jsonl, load_jsonl, save_jsonl, validate_dialog

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------- 📦 Моделі ---------- #

class Replica(BaseModel):
    role: Literal["user", "bot"]
    text: str

class DialogItem(BaseModel):
    user: str = "Кандидат"
    dialog: List[Replica]

    @validator("dialog")
    def validate_roles(cls, value):
        roles = [r.role for r in value]
        if "user" not in roles or "bot" not in roles:
            raise ValueError("Діалог повинен містити хоча б одного user і одного bot")
        return value

class FeedbackRequest(BaseModel):
    index: int
    comment: str

# ---------- 🧰 Утиліти ---------- #

def dialog_hash(dialog):
    return md5(json.dumps(dialog, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# ---------- 🔗 API ---------- #

@router.get("/")
def get_good_dialogs():
    """📥 Отримати всі good-діалоги"""
    items = load_jsonl(GOOD_DIALOGS_PATH)
    logger.info(f"📥 Завантажено {len(items)} good-діалогів")
    return {"success": True, "items": items}

@router.post("/")
def add_good_dialog(item: DialogItem):
    """➕ Додати новий good-діалог"""
    dialog_data = [r.dict() for r in item.dialog]
    if not validate_dialog(dialog_data):
        raise HTTPException(status_code=422, detail="Діалог має містити чергування user → bot → user → ...")

    dialogs = load_jsonl(GOOD_DIALOGS_PATH)

    new_entry = {
        "user": item.user.strip() or "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": dialog_data
    }

    existing_hashes = {dialog_hash(d["dialog"]) for d in dialogs if "dialog" in d}
    if dialog_hash(new_entry["dialog"]) in existing_hashes:
        raise HTTPException(status_code=409, detail="⚠️ Діалог вже існує")

    append_jsonl(GOOD_DIALOGS_PATH, new_entry)
    logger.info("✅ Додано новий good-діалог")
    return {"success": True, "added": new_entry}

@router.delete("/{index}")
def delete_good_dialog(index: int):
    """🗑️ Видалити good-діалог"""
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(GOOD_DIALOGS_PATH, dialogs)
        logger.info(f"🗑️ Видалено good-діалог з індексом {index}")
        return {"success": True, "deleted": deleted}

    raise HTTPException(status_code=404, detail="Діалог не знайдено")

@router.post("/feedback")
def mark_as_bad(req: FeedbackRequest):
    """🔁 Позначити діалог як bad + зберегти фідбек"""
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)

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

    logger.info("📤 Діалог перенесено з good → bad та збережено фідбек")
    return {"success": True, "moved_to": "bad", "feedback_saved": True}
