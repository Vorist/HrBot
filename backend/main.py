# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Імпорти роутерів
from api.real_dialogs import router as real_router
from api.good_dialogs import router as good_router
from api.bad_dialogs import router as bad_router
from api.strategies import router as strategies_router
from api.feedback import router as feedback_router
from api.training import router as training_router

# Ініціалізація FastAPI
app = FastAPI(
    title="HR Bot Backend",
    description="API для управління діалогами, навчанням і стратегіями",
    version="1.0.0"
)

# ✅ CORS Middleware: дозволити запити з фронтенду (розширено)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # dev frontend
        "http://127.0.0.1:5173",
        # "https://your-production-site.com",  # розкоментувати в продакшн
        "*",  # тимчасово — дозволити всі (небажано для продакшн)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📥 Підключення роутерів (групування по напрямках)
app.include_router(real_router, prefix="/api/real_dialogs", tags=["Real Dialogs"])
app.include_router(good_router, prefix="/api/good_dialogs", tags=["Good Dialogs"])
app.include_router(bad_router, prefix="/api/bad_dialogs", tags=["Bad Dialogs"])
app.include_router(strategies_router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(training_router, prefix="/api/training", tags=["Training"])

# 🏠 Стартова перевірка (Ping)
@app.get("/")
def root():
    return {"message": "✅ HR Bot backend is running"}
