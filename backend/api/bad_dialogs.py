from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

from config import BAD_DIALOGS_PATH, GOOD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH

router = APIRouter()

class DialogItem(BaseModel):
    user: str = "Кандидат"
    dialog: list[dict]  # [{"role": "user", "text": "..."}, ...]

class FeedbackRequest(BaseModel):
    index: int
    comment: str


# --- JSONL --- #
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def append_jsonl(path, entry):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# --- GET: всі bad діалоги --- #
@router.get("/api/bad_dialogs")
def get_bad_dialogs():
    return load_jsonl(BAD_DIALOGS_PATH)


# --- POST: додати вручну bad-діалог --- #
@router.post("/api/bad_dialogs")
def add_bad_dialog(item: DialogItem):
    new_entry = {
        "user": item.user,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": item.dialog
    }

    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if any(d.get("dialog") == new_entry["dialog"] for d in dialogs):
        raise HTTPException(status_code=409, detail="Duplicate dialog")

    append_jsonl(BAD_DIALOGS_PATH, new_entry)
    return new_entry


# --- DELETE: видалити bad --- #
@router.delete("/api/bad_dialogs/{index}")
def delete_bad_dialog(index: int):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(BAD_DIALOGS_PATH, dialogs)
        return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Dialog not found")


# --- POST: позначити як good + зберегти фідбек --- #
@router.post("/api/bad_dialogs/feedback")
def mark_as_good(req: FeedbackRequest):
    dialogs = load_jsonl(BAD_DIALOGS_PATH)
    if req.index < 0 or req.index >= len(dialogs):
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

    return {"moved_to": "good", "feedback_saved": True}
