from fastapi import APIRouter, Response, HTTPException
from typing import Optional, List
import subprocess

router = APIRouter()

# --- Конфігурація --- #
TRAINER_DIR = "trainer"
TIMEOUT = 300  # 5 хвилин

ALLOWED_SCRIPTS = {
    "train_from_good.py",
    "train_from_bad.py",
    "feedback_processor.py",
    "training.py",
}


def run_script(script_name: str, args: Optional[List[str]] = None) -> Response:
    """
    Запускає Python-скрипт з trainer/ з необов'язковими аргументами.
    """
    if script_name not in ALLOWED_SCRIPTS:
        raise HTTPException(status_code=400, detail=f"⛔ Скрипт {script_name} не дозволений")

    command = ["python", f"{TRAINER_DIR}/{script_name}"]
    if args:
        command.extend(args)

    try:
        print(f"🔧 Запуск: {' '.join(command)}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )

        output = result.stdout.strip()
        errors = result.stderr.strip()

        if result.returncode == 0:
            print("✅ Навчання завершено успішно")
            return Response(content=output, status_code=200, media_type="text/plain")
        else:
            print("❌ Навчання завершилось з помилкою")
            return Response(
                content=f"⚠️ Навчання завершено з кодом {result.returncode}\n\nSTDOUT:\n{output}\n\nSTDERR:\n{errors}",
                status_code=500,
                media_type="text/plain"
            )

    except subprocess.TimeoutExpired:
        return Response(
            content=f"⏰ Час виконання скрипта {script_name} перевищено ({TIMEOUT} сек)",
            status_code=500,
            media_type="text/plain"
        )

    except Exception as e:
        return Response(
            content=f"❌ Невідома помилка запуску {script_name}: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


# --- API маршрути навчання --- #

@router.post("/api/training/good")
def train_from_good():
    """Навчання на good_dialogs"""
    return run_script("train_from_good.py")


@router.post("/api/training/bad")
def train_from_bad():
    """Навчання на bad_dialogs"""
    return run_script("train_from_bad.py")


@router.post("/api/training/feedback")
def train_from_feedback():
    """Навчання з урахуванням фідбеків"""
    return run_script("feedback_processor.py")


@router.post("/api/training/real")
def train_from_real():
    """Навчання на реальних діалогах"""
    return run_script("training.py", ["real"])


@router.post("/api/training/all")
def train_all():
    """Повне навчання на всіх джерелах"""
    return run_script("training.py", ["all"])
