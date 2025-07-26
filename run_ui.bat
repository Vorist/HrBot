@echo off
chcp 65001 >nul
title 🚀 HR UI LAUNCHER

echo ===============================================
echo 🔧 Запуск повної системи HR-інтерфейсу...
echo ===============================================
echo.

:: ========== PYTHON BACKEND ==========

echo 🧪 Перевірка virtualenv...
if not exist venv\Scripts\activate.bat (
    echo 📁 Створення нового venv...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Помилка при створенні venv!
        pause
        exit /b
    )
)

echo ✅ Venv активовано
call venv\Scripts\activate.bat

echo 📦 Встановлення залежностей Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ pip install завершився з помилкою!
    pause
    exit /b
)
echo ✅ Python-залежності встановлено
echo.

:: ========== NODE FRONTEND ==========

cd frontend
if not exist node_modules (
    echo 📦 Встановлення залежностей Node...
    npm install
    if errorlevel 1 (
        echo ❌ npm install завершився з помилкою!
        pause
        exit /b
    )
)
cd ..

echo ✅ Node-залежності перевірено
echo.

:: ========== ЗАПУСК БЕКЕНДУ ==========

echo 🚀 Запуск бекенду (FastAPI)...
start "BACKEND" cmd /k "cd /d %cd% && call venv\Scripts\activate.bat && uvicorn backend.main:app --reload"

:: ========== ЗАПУСК ФРОНТЕНДУ ==========

echo 🚀 Запуск фронтенду (Vite)...
start "FRONTEND" cmd /k "cd /d %cd%\frontend && npm run dev"

:: ========== ФІНАЛ ==========

echo.
echo ✅ Успішний запуск!
echo 🔗 Backend:  http://localhost:8000
echo 🔗 Frontend: http://localhost:5173
echo -----------------------------------------------
pause
