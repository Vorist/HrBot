# backend/api/training.py

import os
import subprocess
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from config import TRAINER_DIR, TRAIN_TIMEOUT_SECONDS

router = APIRouter(tags=["Training"])
logger = logging.getLogger(__name__)

# --- 🔒 Список дозволених скриптів ---
ALLOWED_SCRIPTS = {
    "train_from_good.py",
    "train_from_bad.py",
    "feedback_processor.py",
    "training.py",
}

# --- 🔧 Централізований запуск скрипта ---
def run_script(script_name: str, args: Optional[List[str]] = None) -> str:
    """
    Запуск Python-скрипта trainer/ і повернення stdout.
    """
    if script_name not in ALLOWED_SCRIPTS:
        logger.warning(f"⛔ Заборонена спроба: {script_name}")
        raise HTTPException(
            status_code=400, detail=f"Скрипт `{script_name}` не дозволено запускати"
        )

    if not os.path.exists(TRAINER_DIR):
        logger.error("❌ TRAINER_DIR не знайдено")
        raise HTTPException(status_code=500, detail="TRAINER_DIR не знайдено")

    script_path = os.path.join(TRAINER_DIR, script_name)
    if not os.path.isfile(script_path):
        logger.error(f"❌ Файл не знайдено: {script_path}")
        raise HTTPException(status_code=404, detail=f"Файл `{script_name}` не знайдено у trainer/")

    cmd = ["python", script_path]
    if args:
        cmd.extend(args)

    logger.info(f"🔧 Виконання: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TRAIN_TIMEOUT_SECONDS,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode == 0:
            logger.info(f"✅ Успіх {script_name}")
            return stdout or "(порожній stdout)"
        else:
            logger.error(f"❌ Код {result.returncode} | STDERR: {stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Скрипт повернув код {result.returncode}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            )
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Таймаут для {script_name}")
        raise HTTPException(
            status_code=504,
            detail=f"Час виконання `{script_name}` перевищив {TRAIN_TIMEOUT_SECONDS} секунд"
        )
    except Exception as e:
        logger.exception(f"❌ Exception запуску {script_name}")
        raise HTTPException(
            status_code=500,
            detail=f"Не вдалося запустити `{script_name}`: {e}"
        )

# --- API endpoints ---
@router.post("/good", summary="Навчання на good_dialogs", response_class=PlainTextResponse)
def train_from_good():
    """Запуск тренування на good_dialogs.jsonl"""
    return run_script("train_from_good.py")

@router.post("/bad", summary="Навчання на bad_dialogs", response_class=PlainTextResponse)
def train_from_bad():
    """Запуск тренування на bad_dialogs.jsonl"""
    return run_script("train_from_bad.py")

@router.post("/feedback", summary="Навчання з урахуванням фідбеку", response_class=PlainTextResponse)
def train_from_feedback():
    """Запуск обробки фідбеку"""
    return run_script("feedback_processor.py")

@router.post("/real", summary="Навчання на real_dialogs", response_class=PlainTextResponse)
def train_from_real():
    """Запуск тренування на real_dialogs.txt"""
    return run_script("training.py", ["real"])

@router.post("/all", summary="Повне навчання", response_class=PlainTextResponse)
def train_all():
    """Повний цикл навчання"""
    return run_script("training.py", ["all"])
