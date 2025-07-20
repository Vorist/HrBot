@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo 🚀 Запускаємо систему: FastAPI + Vite + Feedback UI
echo ============================================

:: 📁 Створення logs
if not exist logs (
    mkdir logs
)

:: 🕒 Створення унікального лог-файлу
set NOW=%time::=m%
set NOW=%NOW: =0%
set LOG_FILE=logs\ui_log_%date:~6,4%-%date:~3,2%-%date:~0,2%_%NOW:~0,2%h%NOW:~2,2%m.txt
echo [START] %date% %time% > "%LOG_FILE%"

:: 📍 Перехід у корінь проєкту
cd /d "%~dp0"

:: 🐍 Активація Python-середовища
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat >> "%LOG_FILE%" 2>&1
    echo ✅ Віртуальне середовище активовано >> "%LOG_FILE%"
) else (
    echo ❌ Не знайдено venv\Scripts\activate.bat >> "%LOG_FILE%"
    echo 🔧 Створи середовище: python -m venv venv >> "%LOG_FILE%"
    pause
    exit /b
)

:: 🔄 Запуск бекенду
echo 🔄 Запуск бекенду (uvicorn)... >> "%LOG_FILE%"
start "📦 BACKEND" cmd /k "cd backend && uvicorn main:app --reload --port 8000"

:: 🌐 Перевірка frontend
if not exist frontend\package.json (
    echo ❌ Відсутній frontend\package.json >> "%LOG_FILE%"
    echo 💡 Перейди: cd frontend && npm install >> "%LOG_FILE%"
    pause
    exit /b
)

:: 🌐 Запуск фронтенду
echo 🌐 Запуск фронтенду (npm run dev)... >> "%LOG_FILE%"
start "🌐 FRONTEND" cmd /k "cd frontend && npm run dev"

:: 🧠 Запуск Feedback UI
if exist feedback_ui\app.py (
    echo 🧠 Запуск Feedback UI... >> "%LOG_FILE%"
    start "🧠 FEEDBACK_UI" cmd /k "cd feedback_ui && streamlit run app.py"
) else (
    echo ⚠️ Не знайдено feedback_ui\app.py — пропущено >> "%LOG_FILE%"
)

:: 🌍 Автовідкриття браузера
timeout /t 4 >nul
start http://localhost:5173

echo ✅ Усі компоненти запущено успішно! >> "%LOG_FILE%"
echo 🔎 Дивись лог: %LOG_FILE%
pause
