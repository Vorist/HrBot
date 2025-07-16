# feedback_ui/app.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, json

from utils import detect_source, parse_dialog_text
from config import (
    GOOD_DIALOGS_PATH,
    BAD_DIALOGS_PATH,
    REAL_DIALOGS_PATH,
    FEEDBACK_COMMENTS_PATH
)
from trainer.feedback_processor import process_feedbacks
from trainer.learner import learn_from_dialogs


# --- 🔧 Ініціалізація FastAPI ---
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# --- 📂 Завантаження JSONL-файлу ---
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# --- 📄 Головна сторінка інтерфейсу ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, type: str = "good", focus: int = -1):
    dialog_paths = {
        "good": GOOD_DIALOGS_PATH,
        "bad": BAD_DIALOGS_PATH,
        "real": REAL_DIALOGS_PATH
    }
    selected_path = dialog_paths.get(type, GOOD_DIALOGS_PATH)
    raw_dialogs = load_jsonl(selected_path)
    feedbacks = load_jsonl(FEEDBACK_COMMENTS_PATH)

    feedback_lookup = {
        (f["dialog_id"], f["message"], f["role"]): f
        for f in feedbacks
        if "dialog_id" in f and "message" in f and "role" in f
    }

    dialogs = []
    for i, entry in enumerate(raw_dialogs):
        text = entry.get("text", "")
        parsed = parse_dialog_text(text)
        source = detect_source(text)
        dialogs.append({
            "id": i,
            "messages": parsed,
            "source": source,
            "focus": (i == focus)
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "dialogs": dialogs,
        "type": type,
        "focus_id": focus,
        "feedbacks": feedback_lookup
    })


# --- 💬 Обробка нових коментарів ---
@app.post("/comment")
async def comment(
    request: Request,
    dialog_id: int = Form(...),
    role: str = Form(...),
    message: str = Form(...),
    comment: str = Form(...),
    type: str = Form("good")
):
    entry = {
        "dialog_id": dialog_id,
        "role": role,
        "message": message,
        "comment": comment
    }

    with open(FEEDBACK_COMMENTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    process_feedbacks()
    learn_from_dialogs()

    return RedirectResponse(
        url=f"/?type={type}&focus={dialog_id}",
        status_code=303
    )


# --- 🔁 Запуск ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("feedback_ui.app:app", host="127.0.0.1", port=8000, reload=True)
