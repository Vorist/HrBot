from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime
from hashlib import md5

from config import GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH

router = APIRouter()

# --- Pydantic моделі --- #
class Replica(BaseModel):
    role: str
    text: str

class DialogItem(BaseModel):
    user: str
    dialog: list[Replica]

class FeedbackRequest(BaseModel):
    index: int
    comment: str

# --- JSONL утиліти --- #
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Помилка при читанні {path}: {e}")
        return []

def save_jsonl(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def append_jsonl(path, record):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# --- Унікальність діалогу через хеш --- #
def dialog_hash(dialog):
    stringified = json.dumps(dialog, ensure_ascii=False)
    return md5(stringified.encode("utf-8")).hexdigest()


# --- API: Отримати всі good-діалоги --- #
@router.get("/api/good_dialogs")
def get_good_dialogs():
    items = load_jsonl(GOOD_DIALOGS_PATH)
    return {"success": True, "items": items}


# --- API: Додати новий good-діалог --- #
@router.post("/api/good_dialogs")
def add_good_dialog(item: DialogItem):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)

    new_entry = {
        "user": item.user.strip() or "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": [r.dict() for r in item.dialog]
    }

    new_hash = dialog_hash(new_entry["dialog"])
    existing_hashes = {dialog_hash(d["dialog"]) for d in dialogs if "dialog" in d}

    if new_hash in existing_hashes:
        raise HTTPException(status_code=409, detail="⚠️ Діалог вже існує")

    append_jsonl(GOOD_DIALOGS_PATH, new_entry)
    return {"success": True, "added": new_entry}


# --- API: Видалити good-діалог --- #
@router.delete("/api/good_dialogs/{index}")
def delete_good_dialog(index: int):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)

    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(GOOD_DIALOGS_PATH, dialogs)
        return {"success": True, "deleted": deleted}

    raise HTTPException(status_code=404, detail="Діалог не знайдено")


# --- API: Позначити як bad + зберегти фідбек --- #
@router.post("/api/good_dialogs/feedback")
def mark_as_bad(req: FeedbackRequest):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)

    if req.index < 0 or req.index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    dialog = dialogs.pop(req.index)
    save_jsonl(GOOD_DIALOGS_PATH, dialogs)
    append_jsonl(BAD_DIALOGS_PATH, dialog)

    feedback_entry = {
        "from": "good_dialogs",
        "status": "moved_to_bad",
        "comment": req.comment,
        "dialog": dialog,
        "timestamp": datetime.now().isoformat()
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    return {"success": True, "moved_to": "bad", "feedback_saved": True}
