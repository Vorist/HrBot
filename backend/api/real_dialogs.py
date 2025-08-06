# backend/api/real_dialogs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
import logging

from config import REAL_DIALOGS_PATH, GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH
from backend.utils.jsonl_utils import append_jsonl

router = APIRouter()
logger = logging.getLogger(__name__)

# Модель для POST-запроса: одна фраза менеджера
class DialogLine(BaseModel):
    text: str

# --- 📥 GET /api/real_dialogs/ ---
@router.get("/", response_model=List[str])
def get_real_dialogs():
    """
    Возвращает все непустые строки из файла real_dialogs.txt
    """
    path = REAL_DIALOGS_PATH
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f if line.strip()]
        logger.info(f"📥 Загружено {len(lines)} фраз менеджера")
        return lines
    except Exception:
        logger.exception("❌ Ошибка чтения real_dialogs.txt")
        raise HTTPException(status_code=500, detail="Не удалось загрузить реальные диалоги")

# --- ➕ POST /api/real_dialogs/ ---
@router.post("/", status_code=201)
def add_real_dialog(line: DialogLine):
    """
    Добавляет новую фразу менеджера в файл real_dialogs.txt
    """
    text = line.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Текст не может быть пустым")
    try:
        os.makedirs(os.path.dirname(REAL_DIALOGS_PATH), exist_ok=True)
        with open(REAL_DIALOGS_PATH, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        logger.info("✅ Добавлена новая фраза менеджера")
        return {"text": text}
    except Exception:
        logger.exception("❌ Ошибка записи в real_dialogs.txt")
        raise HTTPException(status_code=500, detail="Не удалось сохранить фразу")

# --- 🗑️ DELETE /api/real_dialogs/{index} ---
@router.delete("/{index}")
def delete_real_dialog(index: int):
    """
    Удаляет фразу менеджера по индексу из real_dialogs.txt
    """
    path = REAL_DIALOGS_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f if line.strip()]
        if index < 0 or index >= len(lines):
            raise HTTPException(status_code=404, detail="Индекс за пределами списка")
        deleted = lines.pop(index)
        with open(path, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")
        logger.info(f"🗑️ Удалена фраза менеджера #{index}")
        return {"deleted": deleted}
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Ошибка при удалении фразы")
        raise HTTPException(status_code=500, detail="Не удалось удалить фразу")

# --- 🔁 POST /api/real_dialogs/convert ---
class ConvertRequest(BaseModel):
    index: int
    target: str  # "good" или "bad"

@router.post("/convert")
def convert_dialog(req: ConvertRequest):
    """
    Перемещает фразу в good_dialogs.jsonl или bad_dialogs.jsonl, удаляет из real_dialogs.txt
    """
    path = REAL_DIALOGS_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    try:
        # читаем все непустые строки
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f if line.strip()]
        if req.index < 0 or req.index >= len(lines):
            raise HTTPException(status_code=404, detail="Индекс не найден")
        text = lines.pop(req.index)

        # перезаписываем файл без удалённой строки
        with open(path, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")

        # формируем запись для JSONL
        entry = {
            "user": text,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "dialog": [{"role": "user", "text": text}]
        }
        if req.target == "good":
            append_jsonl(GOOD_DIALOGS_PATH, entry)
        elif req.target == "bad":
            append_jsonl(BAD_DIALOGS_PATH, entry)
        else:
            raise HTTPException(status_code=400, detail="target должен быть 'good' или 'bad'")

        logger.info(f"🔁 Фраза перемещена в {req.target}")
        return {"moved": req.target, "text": text}
    except HTTPException:
        raise
    except Exception:
        logger.exception("❌ Ошибка при конвертации фразы")
        raise HTTPException(status_code=500, detail="Не удалось конвертировать фразу")
