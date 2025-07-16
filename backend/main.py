# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.real_dialogs import router as real_router
from api.good_dialogs import router as good_router
from api.bad_dialogs import router as bad_router
from api.strategies import router as strategies_router
from api.feedback import router as feedback_router
from api.training import router as training_router

app = FastAPI()

# ✅ Дозволити запити з фронтенду (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # або вкажи конкретно: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📥 Підключення всіх API
app.include_router(real_router)
app.include_router(good_router)
app.include_router(bad_router)
app.include_router(strategies_router)
app.include_router(feedback_router)
app.include_router(training_router)

# 🏠 Перевірка
@app.get("/")
def root():
    return {"message": "HR Bot backend is running"}
