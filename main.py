# backend/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.routing import APIRoute
import os
import logging

# === 📦 Імпорт роутерів ===
from backend.api.real_dialogs import router as real_dialogs_router
from backend.api.bad_dialogs import router as bad_dialogs_router
from backend.api.good_dialogs import router as good_dialogs_router
from backend.api.strategies import router as strategies_router
from backend.api.feedback import router as feedback_router
from backend.api.training import router as training_router

# === 🚀 Ініціалізація FastAPI ===
app = FastAPI(
    title="HR Bot API",
    description="API для роботи з діалогами, фідбеком та навчанням",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# === 🌐 Налаштування CORS для фронтенду ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ⏹ Middleware для обрізки зайвих слешів ===
@app.middleware("http")
async def strip_trailing_slash(request: Request, call_next):
    path = request.url.path
    # Якщо шлях закінчується слешем і це не корінь, редиректимо на версію без слеша
    if path != "/" and path.endswith("/"):
        new_url = request.url.replace(path=path.rstrip("/"))
        return RedirectResponse(url=str(new_url))
    return await call_next(request)

# === 🔗 Реєстрація API-маршрутів ===
app.include_router(real_dialogs_router, prefix="/api/real_dialogs", tags=["Real Dialogs"])
app.include_router(good_dialogs_router,    prefix="/api/good_dialogs", tags=["Good Dialogs"])
app.include_router(bad_dialogs_router,     prefix="/api/bad_dialogs",  tags=["Bad Dialogs"])
app.include_router(feedback_router,        prefix="/api/feedback",     tags=["Feedback"])
app.include_router(strategies_router,      prefix="/api/strategies",   tags=["Strategies"])
app.include_router(training_router,        prefix="/api/training",     tags=["Training"])

# === 🧭 Логування доступних маршрутів при старті ===
@app.on_event("startup")
async def log_all_routes():
    print("📍 Зареєстровані маршрути:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            print(f"  {route.path} [{methods}]")

# === 🖼️ Видача фронтенду з папки frontend/dist ===
frontend_dir = os.path.join("frontend", "dist")
index_html   = os.path.join(frontend_dir, "index.html")

if os.path.exists(index_html):
    # Обслуговуємо статику
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(index_html)

    print(f"✅ Фронтенд знайдено й доступний: {frontend_dir}")
else:
    print("⚠️ Не знайдено фронтенд (frontend/dist/index.html) — сайт не буде доступний.")
