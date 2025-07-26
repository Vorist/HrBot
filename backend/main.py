# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# === 📦 Імпорт API-маршрутів ===
from backend.api.real_dialogs import router as real_dialogs_router
from backend.api.strategies import router as strategies_router
from backend.api.good_dialogs import router as good_dialogs_router
from backend.api.bad_dialogs import router as bad_dialogs_router
from backend.api.feedback import router as feedback_router
from backend.api.training import router as trainer_router

# === 🚀 Ініціалізація FastAPI ===
app = FastAPI(
    title="HR Bot API",
    description="API для керування діалогами, стратегіями та навчанням бота",
    version="1.0.0"
)

# === 🌐 Дозвіл CORS для фронтенду ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 🔗 Підключення API без додаткових prefix (вони вже є в файлах) ===
app.include_router(real_dialogs_router)
app.include_router(good_dialogs_router)
app.include_router(bad_dialogs_router)
app.include_router(feedback_router)
app.include_router(strategies_router)
app.include_router(trainer_router)

# === 🖼️ Подача фронтенду (React) у продакшені ===
frontend_dist = os.path.join("frontend", "dist")
index_html = os.path.join(frontend_dist, "index.html")

if os.path.exists(index_html):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    @app.get("/")
    async def serve_index():
        return FileResponse(index_html)

    print(f"✅ Фронтенд знайдено й доступний: {frontend_dist}")
else:
    print("⚠️ Папка frontend/dist або index.html не знайдена — фронтенд не буде відданий.")
