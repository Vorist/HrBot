# backend/api/real_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import os
import logging

from config import REAL_DIALOGS_PATH, GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH
from backend.utils.jsonl_utils import append_jsonl

router = APIRouter()
logger = logging.getLogger(__name__)

# ---- 📦 Моделі ----
class RealDialog(BaseModel):
    source: str
    dialog: List[Dict[str, str]]  # [{"role": "bot", "text": ...}, {"role": "user", "text": ...}]

class AddDialogRequest(BaseModel):
    source: str
    dialog: str  # raw multi-line text ("🤖 ...\n👤 ...")

class ConvertRequest(BaseModel):
    index: int
    target: str  # "good" або "bad"

# ---- 📖 Утилита парсинга ----
def load_real_dialogs() -> List[Dict[str, Any]]:
    """
    Загружает все диалоги из real_dialogs.txt как [{source, dialog: [{"role", "text"}]}]
    """
    if not os.path.exists(REAL_DIALOGS_PATH):
        return []

    dialogs = []
    current = None

    with open(REAL_DIALOGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    dialogs.append(current)
                    current = None
                continue

            if line.startswith("📥 Джерело:") or line.startswith("📥 Джерело:"):
                if current:
                    dialogs.append(current)
                current = {
                    "source": line.replace("📥 Джерело:", "").strip(),
                    "dialog": []
                }
            elif current is not None:
                # 👤 або 🤖
                if line.startswith("👤"):
                    current["dialog"].append({"role": "user", "text": line[1:].strip()})
                elif line.startswith("🤖"):
                    current["dialog"].append({"role": "bot", "text": line[1:].strip()})
                else:
                    current["dialog"].append({"role": "system", "text": line.strip()})
        if current:
            dialogs.append(current)
    return dialogs

def save_real_dialogs(dialogs: List[Dict[str, Any]]):
    with open(REAL_DIALOGS_PATH, "w", encoding="utf-8") as f:
        for dialog in dialogs:
            f.write(f"📥 Джерело: {dialog['source']}\n")
            for line in dialog["dialog"]:
                icon = "👤" if line["role"] == "user" else "🤖"
                f.write(f"{icon} {line['text']}\n")
            f.write("\n")

# ---- GET ----
@router.get("/", response_model=List[RealDialog])
def get_real_dialogs():
    try:
        dialogs = load_real_dialogs()
        logger.info(f"📥 Загружено {len(dialogs)} реальних діалогів")
        return dialogs
    except Exception:
        logger.exception("❌ Ошибка чтения real_dialogs.txt")
        raise HTTPException(status_code=500, detail="Не удалось загрузить реальные диалоги")

# ---- POST ----
@router.post("/", status_code=201)
def add_real_dialog(req: AddDialogRequest):
    if not req.source.strip() or not req.dialog.strip():
        raise HTTPException(status_code=400, detail="Вкажіть джерело і текст діалогу")
    lines = req.dialog.strip().split("\n")
    dialog = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("👤"):
            dialog.append({"role": "user", "text": line[1:].strip()})
        elif line.startswith("🤖"):
            dialog.append({"role": "bot", "text": line[1:].strip()})
        else:
            dialog.append({"role": "system", "text": line})
    new_entry = {"source": req.source.strip(), "dialog": dialog}

    dialogs = load_real_dialogs()
    dialogs.append(new_entry)
    save_real_dialogs(dialogs)
    logger.info("✅ Додано новий реальний діалог")
    return new_entry

# ---- DELETE ----
@router.delete("/{index}")
def delete_real_dialog(index: int):
    dialogs = load_real_dialogs()
    if index < 0 or index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")
    deleted = dialogs.pop(index)
    save_real_dialogs(dialogs)
    logger.info(f"🗑️ Видалено діалог #{index}")
    return {"deleted": deleted}

# ---- CONVERT ----
@router.post("/convert")
def convert_real_dialog(req: ConvertRequest):
    dialogs = load_real_dialogs()
    if req.index < 0 or req.index >= len(dialogs):
        raise HTTPException(status_code=404, detail="Діалог не знайдено")
    dialog = dialogs.pop(req.index)
    save_real_dialogs(dialogs)

    # Перемещение в good/bad
    entry = {
        "user": "Кандидат",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dialog": dialog["dialog"],
        "source": dialog["source"]
    }
    if req.target == "good":
        append_jsonl(GOOD_DIALOGS_PATH, entry)
    elif req.target == "bad":
        append_jsonl(BAD_DIALOGS_PATH, entry)
    else:
        raise HTTPException(status_code=400, detail="target повинен бути good або bad")

    logger.info(f"🔁 Діалог переміщено в {req.target}")
    return {"moved": req.target, "dialog": entry}
