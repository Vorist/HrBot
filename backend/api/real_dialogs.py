from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

router = APIRouter()

REAL_DIALOGS_PATH = "data/real_dialogs.txt"
GOOD_DIALOGS_PATH = "data/good_dialogs.jsonl"
BAD_DIALOGS_PATH = "data/bad_dialogs.jsonl"

# --- 📦 МОДЕЛІ --- #
class DialogRequest(BaseModel):
    source: str  # Наприклад: "Instagram"
    dialog: str  # Повний текст діалогу (з іконками)

class ConvertRequest(BaseModel):
    index: int
    target: str  # "good" або "bad"

# --- 🧩 ХЕЛПЕРИ --- #
def parse_dialog_block(block: str):
    lines = block.strip().split("\n")
    if not lines:
        return None

    source = "Невідоме джерело"
    if lines[0].startswith("📥"):
        source = lines[0].replace("📥", "").replace("Джерело:", "").strip()
        lines = lines[1:]

    dialog = []
    for line in lines:
        line = line.strip()
        if line.startswith("👤"):
            dialog.append({"role": "user", "text": line[1:].strip()})
        elif line.startswith("🤖"):
            dialog.append({"role": "bot", "text": line[1:].strip()})
    if not dialog:
        return None

    return {"source": source, "dialog": dialog}

def format_dialog_block(source: str, dialog: list[dict]):
    header = f"📥 Джерело: {source.strip()}"
    lines = [
        f"👤 {d['text']}" if d["role"] == "user" else f"🤖 {d['text']}"
        for d in dialog
    ]
    return header + "\n" + "\n".join(lines)

def load_real_dialogs():
    if not os.path.exists(REAL_DIALOGS_PATH):
        return []

    with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")

    return [parsed for block in blocks if (parsed := parse_dialog_block(block))]

def save_real_dialogs(dialogs: list[dict]):
    os.makedirs(os.path.dirname(REAL_DIALOGS_PATH), exist_ok=True)
    blocks = [format_dialog_block(d["source"], d["dialog"]) for d in dialogs]
    with open(REAL_DIALOGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocks))

def append_to_jsonl(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

# --- 📡 API РОУТИ --- #

# 🔹 GET: Повернути всі реальні діалоги
@router.get("/api/real_dialogs")
def get_real_dialogs():
    return load_real_dialogs()

# 🔹 POST: Додати новий діалог
@router.post("/api/real_dialogs")
def add_real_dialog(req: DialogRequest):
    if not req.source.strip() or not req.dialog.strip():
        raise HTTPException(status_code=400, detail="Обидва поля обов’язкові")

    parsed = parse_dialog_block(f"📥 Джерело: {req.source.strip()}\n{req.dialog.strip()}")
    if not parsed:
        raise HTTPException(status_code=400, detail="Невірний формат діалогу")

    existing = load_real_dialogs()
    if any(parsed["dialog"] == d["dialog"] and parsed["source"] == d["source"] for d in existing):
        raise HTTPException(status_code=409, detail="Такий діалог вже існує")

    existing.append(parsed)
    save_real_dialogs(existing)
    return parsed

# 🔹 DELETE: Видалити діалог за індексом
@router.delete("/api/real_dialogs/{index}")
def delete_real_dialog(index: int):
    dialogs = load_real_dialogs()
    if index < 0 or index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")

    removed = dialogs.pop(index)
    save_real_dialogs(dialogs)
    return {"deleted": removed}

# 🔹 POST: Перемістити діалог у good або bad
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

    return {"moved": req.target, "saved": True}
