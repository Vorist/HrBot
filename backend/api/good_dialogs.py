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

# --- 📦 Pydantic-модели --- #
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
            raise ValueError("Діалог повинен містити принаймні одну репліку user і одну — bot")
        return v

class FeedbackRequest(BaseModel):
    index: int
    comment: str

def _dialog_hash(dialog: List[dict]) -> str:
    """
    Стабільний хеш списку реплік для проверки дубликатов.
    """
    # Для хеша не сортируем! Важно оставить порядок (может влиять на смысл)
    serialized = str(dialog)
    return md5(serialized.encode("utf-8")).hexdigest()


# --- 📡 API-маршрути --- #

@router.get("/", summary="Отримати всі good-діалоги")
def get_good_dialogs():
    try:
        dialogs = load_jsonl(GOOD_DIALOGS_PATH)
        if not isinstance(dialogs, list):
            raise HTTPException(status_code=500, detail="Файл не містить список діалогів")
        logger.info(f"📥 Завантажено {len(dialogs)} good-діалогів")
        return dialogs
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Помилка при завантаженні good-діалогів")
        raise HTTPException(status_code=500, detail="Не вдалося завантажити хороші діалоги")


@router.post("/", summary="Додати новий good-діалог", status_code=201)
def add_good_dialog(item: DialogItem):
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

    # Проверка на дубликат по хешу диалога
    new_hash = _dialog_hash(new_entry["dialog"])
    existing_hashes = {_dialog_hash(d["dialog"]) for d in dialogs if "dialog" in d}
    if new_hash in existing_hashes:
        raise HTTPException(status_code=409, detail="Такий діалог вже існує")

    append_jsonl(GOOD_DIALOGS_PATH, new_entry)
    logger.info("✅ Додано новий good-діалог")
    return new_entry


@router.delete("/{index}", summary="Видалити good-діалог за індексом")
def delete_good_dialog(index: int):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу діалогів")
    if index < 0 or index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    deleted = dialogs.pop(index)
    save_jsonl(GOOD_DIALOGS_PATH, dialogs)
    logger.info(f"🗑️ Видалено good-діалог #{index}")
    return {"deleted": deleted}


@router.post("/feedback", summary="Позначити good → bad і зберегти фідбек")
def mark_as_bad(req: FeedbackRequest):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if not isinstance(dialogs, list):
        raise HTTPException(status_code=500, detail="Неправильний формат файлу діалогів")
    if req.index < 0 or req.index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    # Переміщуємо діалог у bad
    dialog = dialogs.pop(req.index)
    save_jsonl(GOOD_DIALOGS_PATH, dialogs)
    append_jsonl(BAD_DIALOGS_PATH, dialog)

    # Запис фідбеку (источник good_dialogs, статус moved_to_bad)
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
