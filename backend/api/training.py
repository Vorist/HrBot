from fastapi import APIRouter, Response, HTTPException
from typing import Optional, List
import subprocess
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# === 🔧 Налаштування ===
TRAINER_DIR = "trainer"
TIMEOUT = 300  # секунд

ALLOWED_SCRIPTS = {
    "train_from_good.py",
    "train_from_bad.py",
    "feedback_processor.py",
    "training.py",
}


def run_script(script_name: str, args: Optional[List[str]] = None) -> Response:
    """
    Запускає python-скрипт з trainer/, дозволяє передати аргументи.
    """
    if script_name not in ALLOWED_SCRIPTS:
        logger.warning(f"⛔ Заборонений скрипт: {script_name}")
        raise HTTPException(status_code=400, detail=f"⛔ Скрипт {script_name} не дозволено запускати.")

    command = ["python", os.path.join(TRAINER_DIR, script_name)]
    if args:
        command.extend(args)

    try:
        logger.info(f"🔧 Запуск скрипта: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            logger.info("✅ Навчання виконано успішно")
            return Response(content=stdout, status_code=200, media_type="text/plain")
        else:
            logger.error(f"❌ Навчання завершилось з кодом {result.returncode}")
            return Response(
                content=f"⚠️ Навчання завершилось з кодом {result.returncode}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}",
                status_code=500,
                media_type="text/plain"
            )

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Скрипт {script_name} перевищив таймаут {TIMEOUT} сек")
        return Response(
            content=f"⏰ Час виконання скрипта {script_name} перевищено ({TIMEOUT} сек)",
            status_code=500,
            media_type="text/plain"
        )

    except Exception as e:
        logger.exception(f"❌ Помилка запуску скрипта {script_name}")
        return Response(
            content=f"❌ Помилка запуску {script_name}: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


# === 📡 Маршрути API ===

@router.post("/api/train/good")
def train_from_good():
    """Навчання на good_dialogs"""
    return run_script("train_from_good.py")


@router.post("/api/train/bad")
def train_from_bad():
    """Навчання на bad_dialogs"""
    return run_script("train_from_bad.py")


@router.post("/api/train/feedback")
def train_from_feedback():
    """Навчання з урахуванням фідбеків"""
    return run_script("feedback_processor.py")


@router.post("/api/train/real")
def train_from_real():
    """Навчання на реальних діалогах"""
    return run_script("training.py", ["real"])


@router.post("/api/train/all")
def train_all():
    """Навчання на всіх джерелах"""
    return run_script("training.py", ["all"])
