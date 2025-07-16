from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

from config import GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, FEEDBACK_LESSONS_PATH

router = APIRouter()

class DialogItem(BaseModel):
    user: str
    dialog: list[dict]  # [{"role": "user", "text": "..."}, {"role": "bot", "text": "..."}]

class FeedbackRequest(BaseModel):
    index: int
    comment: str


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def append_jsonl(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@router.get("/api/good_dialogs")
def get_good_dialogs():
    return load_jsonl(GOOD_DIALOGS_PATH)


@router.post("/api/good_dialogs")
def add_good_dialog(item: DialogItem):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    new_entry = {
        "user": item.user,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": item.dialog
    }

    # Уникнення дублікатів
    for d in dialogs:
        if d.get("dialog") == new_entry["dialog"]:
            raise HTTPException(status_code=400, detail="Duplicate dialog")

    append_jsonl(GOOD_DIALOGS_PATH, new_entry)
    return new_entry


@router.delete("/api/good_dialogs/{index}")
def delete_good_dialog(index: int):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if 0 <= index < len(dialogs):
        deleted = dialogs.pop(index)
        save_jsonl(GOOD_DIALOGS_PATH, dialogs)
        return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Dialog not found")


@router.post("/api/good_dialogs/feedback")
def mark_as_bad(req: FeedbackRequest):
    dialogs = load_jsonl(GOOD_DIALOGS_PATH)
    if req.index < 0 or req.index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Dialog not found")

    dialog = dialogs.pop(req.index)
    save_jsonl(GOOD_DIALOGS_PATH, dialogs)
    append_jsonl(BAD_DIALOGS_PATH, dialog)

    feedback_entry = {
        "from": "good_dialogs",
        "comment": req.comment,
        "dialog": dialog,
        "status": "moved_to_bad",
        "timestamp": datetime.now().isoformat()
    }
    append_jsonl(FEEDBACK_LESSONS_PATH, feedback_entry)

    return {"moved_to": "bad", "feedback_saved": True}
