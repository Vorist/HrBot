from fastapi import APIRouter, Response, HTTPException
import subprocess
import os

router = APIRouter()

# Дозволені скрипти, які можна запускати
ALLOWED_SCRIPTS = {
    "train_from_good.py",
    "train_from_bad.py",
    "feedback_processor.py",
    "training.py"
}

# --- Запуск python-скрипта з trainer/ --- #
def run_script(script_name: str, args: list[str] = None) -> Response:
    if script_name not in ALLOWED_SCRIPTS:
        raise HTTPException(status_code=400, detail="⛔ Невідомий скрипт")

    try:
        cmd = ["python", f"trainer/{script_name}"]
        if args:
            cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr

        status = 200 if result.returncode == 0 else 500
        return Response(content=output, status_code=status, media_type="text/plain")

    except Exception as e:
        return Response(
            content=f"❌ Помилка запуску скрипта: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

# --- POST: запуск окремих навчань --- #
@router.post("/api/training/good")
def train_from_good():
    return run_script("train_from_good.py")

@router.post("/api/training/bad")
def train_from_bad():
    return run_script("train_from_bad.py")

@router.post("/api/training/feedback")
def train_from_feedback():
    return run_script("feedback_processor.py")

@router.post("/api/training/real")
def train_from_real():
    return run_script("training.py", ["real"])

@router.post("/api/training/all")
def train_all():
    return run_script("training.py", ["all"])
