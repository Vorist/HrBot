# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
import os

# === 📦 Импорт роутеров ===
from backend.api.real_dialogs import router as real_dialogs_router
from backend.api.good_dialogs import router as good_dialogs_router
from backend.api.bad_dialogs import router as bad_dialogs_router
from backend.api.feedback import router as feedback_router
from backend.api.strategies import router as strategies_router
from backend.api.training import router as training_router

# === 🚀 Инициализация FastAPI ===
app = FastAPI(
    title="HR Bot API",
    description="API для роботи з діалогами, фідбеком та навчанням",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# === 🌐 CORS настройка ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],  # * только для DEV!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 🔗 Роутеры ===
app.include_router(real_dialogs_router, prefix="/api/real_dialogs", tags=["Real Dialogs"])
app.include_router(good_dialogs_router, prefix="/api/good_dialogs", tags=["Good Dialogs"])
app.include_router(bad_dialogs_router,  prefix="/api/bad_dialogs", tags=["Bad Dialogs"])
app.include_router(feedback_router,     prefix="/api/feedback",    tags=["Feedback"])
app.include_router(strategies_router,   prefix="/api/strategies",  tags=["Strategies"])
app.include_router(training_router,     prefix="/api/training",    tags=["Training"])

# === 🧭 Лог маршрутов при запуске ===
@app.on_event("startup")
async def log_all_routes():
    print("📍 Зарегистрированные маршруты:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            print(f"  {route.path} [{methods}]")

# === 🖼️ Отдача фронтенда ===
frontend_dir = os.path.join("frontend", "dist")
index_html   = os.path.join(frontend_dir, "index.html")

if os.path.exists(index_html):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(index_html)

    print(f"✅ Фронтенд знайдено й доступний: {frontend_dir}")
else:
    print("⚠️ Не знайдено фронтенд (frontend/dist/index.html) — сайт не буде доступний.")
