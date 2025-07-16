# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 🔌 Імпорт API-маршрутів
from api.real_dialogs import router as real_dialogs_router
from api.strategies import router as strategies_router

# 🔧 Ініціалізація FastAPI
app = FastAPI(
    title="HR Bot API",
    description="API для взаємодії з реальними діалогами та стратегіями",
    version="1.0.0"
)

# 🎯 Дозволяємо запити з фронтенду (локально або прод)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Реєстрація API-маршрутів
app.include_router(real_dialogs_router, prefix="/api/real-dialogs")
app.include_router(strategies_router, prefix="/api/strategies")

# 🌍 Видача React фронтенду (у продакшені)
frontend_dist = os.path.join("frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    print(f"🚀 Frontend доступний з {frontend_dist}")
else:
    print("⚠️ Папка фронтенду не знайдена — frontend не буде відданий.")

