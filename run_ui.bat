@echo off
chcp 65001 >nul
title 🚀 HR UI LAUNCHER

echo ===============================================
echo 🔧 Запуск полной HR-системы (бекенд + фронтенд)
echo ===============================================
echo.

:: ========== PYTHON BACKEND ==========
echo 🧪 Проверка virtualenv...
if not exist venv\Scripts\activate.bat (
    echo 📁 Создание нового venv...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка при создании venv!
        pause
        exit /b
    )
)

echo ✅ Venv активирован
call venv\Scripts\activate.bat

echo 📦 Установка Python-зависимостей...
pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ pip install завершился с ошибкой!
    pause
    exit /b
)
echo ✅ Python-зависимости установлены
echo.

:: ========== NODE FRONTEND ==========
cd frontend
if not exist node_modules (
    echo 📦 Установка Node-зависимостей...
    npm install
    if errorlevel 1 (
        echo ❌ npm install завершился с ошибкой!
        pause
        exit /b
    )
)
cd ..

echo ✅ Node-зависимости готовы
echo.

:: ========== ЗАПУСК БЕКЕНДА ==========
echo 🚀 Запуск бекенда (FastAPI, Uvicorn)...
start "BACKEND" cmd /k "cd /d %cd% && call venv\Scripts\activate.bat && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 2 >nul

:: ========== ЗАПУСК ФРОНТЕНДА ==========
echo 🚀 Запуск фронтенда (Vite)...
start "FRONTEND" cmd /k "cd /d %cd%\frontend && npm run dev"
timeout /t 2 >nul

:: ========== ГОТОВО ==========
echo.
echo ✅ Система успешно запущена!
echo -----------------------------------------------
echo 🔗 Backend:  http://localhost:8000
echo 🔗 Frontend: http://localhost:5173
echo ===============================================
pause
