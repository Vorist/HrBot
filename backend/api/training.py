# backend/api/training.py

import os
import subprocess
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter(
    prefix="/api/train",
    tags=["Training"]
)

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
    Запускає Python-скрипт із папки trainer/, з можливістю передачі аргументів.
    """
    if script_name not in ALLOWED_SCRIPTS:
        logger.warning(f"⛔ Спроба запуску забороненого скрипта: {script_name}")
        raise HTTPException(
            status_code=400,
            detail=f"Скрипт `{script_name}` не дозволено запускати"
        )

    cmd = ["python", os.path.join(TRAINER_DIR, script_name)]
    if args:
        cmd.extend(args)

    try:
        logger.info(f"🔧 Виконання: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            logger.info("✅ Скрипт виконано успішно")
            return Response(content=stdout, media_type="text/plain")
        else:
            logger.error(f"❌ Скрипт завершився з кодом {result.returncode}")
            return Response(
                content=(
                    f"⚠️ Скрипт повернув код {result.returncode}\n\n"
                    f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                ),
                status_code=500,
                media_type="text/plain"
            )

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Таймаут ({TIMEOUT}s) при виконанні скрипта {script_name}")
        return Response(
            content=(
                f"⏰ Час виконання скрипта `{script_name}` "
                f"перевищив {TIMEOUT} секунд"
            ),
            status_code=500,
            media_type="text/plain"
        )

    except Exception as e:
        logger.exception(f"❌ Помилка при запуску скрипта {script_name}")
        return Response(
            content=f"❌ Не вдалося запустити `{script_name}`: {e}",
            status_code=500,
            media_type="text/plain"
        )


# === 📡 Маршрути API ===

@router.post("/good", summary="Train on good_dialogs")
def train_from_good():
    """Навчання на `good_dialogs.jsonl`"""
    return run_script("train_from_good.py")


@router.post("/bad", summary="Train on bad_dialogs")
def train_from_bad():
    """Навчання на `bad_dialogs.jsonl`"""
    return run_script("train_from_bad.py")


@router.post("/feedback", summary="Train using feedback data")
def train_from_feedback():
    """Навчання з урахуванням фідбеків"""
    return run_script("feedback_processor.py")


@router.post("/real", summary="Train on real_dialogs")
def train_from_real():
    """Навчання на реальних діалогах (`real_dialogs.txt`)"""
    return run_script("training.py", ["real"])


@router.post("/all", summary="Train on all data")
def train_all():
    """Повне навчання на `good`, `bad`, `feedback`, `real`"""
    return run_script("training.py", ["all"])
