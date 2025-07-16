# backend/api/real_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

router = APIRouter()

REAL_DIALOGS_PATH = "data/real_dialogs.txt"
GOOD_DIALOGS_PATH = "data/good_dialogs.jsonl"
BAD_DIALOGS_PATH = "data/bad_dialogs.jsonl"

class DialogRequest(BaseModel):
    source: str  # наприклад: "OLX"
    dialog: str  # повний текст діалогу

class ConvertRequest(BaseModel):
    index: int
    target: str  # "good" або "bad"

def parse_dialog_block(block: str):
    lines = block.strip().split("\n")
    if not lines:
        return None
    source = "Невідомо"
    if lines[0].startswith("📥"):
        source = lines[0].replace("📥 Джерело:", "").strip()
        lines = lines[1:]

    dialog = []
    for line in lines:
        line = line.strip()
        if line.startswith("👤"):
            dialog.append({"role": "user", "text": line.replace("👤", "").strip()})
        elif line.startswith("🤖"):
            dialog.append({"role": "bot", "text": line.replace("🤖", "").strip()})
    return {"source": source, "dialog": dialog}

def format_dialog_block(source: str, dialog: str):
    return f"📥 Джерело: {source.strip()}\n{dialog.strip()}"

def load_real_dialogs():
    if not os.path.exists(REAL_DIALOGS_PATH):
        return []
    with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")
        results = []
        for block in blocks:
            parsed = parse_dialog_block(block)
            if parsed:
                results.append(parsed)
        return results

def save_real_dialogs(parsed_dialogs):
    blocks = []
    for item in parsed_dialogs:
        block = format_dialog_block(item["source"], "\n".join(
            [f'👤 {r["text"]}' if r["role"] == "user" else f'🤖 {r["text"]}' for r in item["dialog"]]
        ))
        blocks.append(block)
    with open(REAL_DIALOGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocks))

def append_to_jsonl(path, data):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

@router.get("/api/real_dialogs")
def get_real_dialogs():
    return load_real_dialogs()

@router.post("/api/real_dialogs")
def add_real_dialog(req: DialogRequest):
    if not req.source.strip() or not req.dialog.strip():
        raise HTTPException(status_code=400, detail="Джерело і діалог не можуть бути порожні")

    new_block = format_dialog_block(req.source, req.dialog)
    existing_raw = ""
    if os.path.exists(REAL_DIALOGS_PATH):
        with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
            existing_raw = f.read().strip()
    all_blocks = [existing_raw, new_block] if existing_raw else [new_block]
    with open(REAL_DIALOGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_blocks))
    return {"success": True}

@router.post("/api/real_dialogs/convert")
def convert_dialog(req: ConvertRequest):
    dialogs = load_real_dialogs()
    if req.index < 0 or req.index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    item = dialogs.pop(req.index)
    save_real_dialogs(dialogs)

    entry = {
        "user": item["dialog"][0]["text"] if item["dialog"] else "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": item["dialog"]
    }

    if req.target == "good":
        append_to_jsonl(GOOD_DIALOGS_PATH, entry)
    elif req.target == "bad":
        append_to_jsonl(BAD_DIALOGS_PATH, entry)
    else:
        raise HTTPException(status_code=400, detail="Тип має бути 'good' або 'bad'")

    return {"success": True}
