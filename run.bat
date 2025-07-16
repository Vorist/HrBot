@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM === 📅 Формування імені лог-файлу ===
set LOG_DIR=logs
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set LOG_NAME=log_%%a.txt
set LOG_PATH=%LOG_DIR%\%LOG_NAME%
if not exist %LOG_DIR% mkdir %LOG_DIR%

REM === 📍 Перехід у кореневу директорію ===
cd /d "%~dp0"

REM === 🐍 Активація віртуального середовища ===
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Віртуальне середовище активовано
) else (
    echo ❌ Не знайдено venv\Scripts\activate.bat
    echo 💡 Створи його командою: python -m venv venv
    pause
    exit /b
)

REM === 🔁 Запуск повного циклу навчання бота ===
echo 🔁 Запуск повного циклу навчання бота...
echo 🔁 Запуск повного циклу навчання бота... > %LOG_PATH%

REM === 🧾 Конвертація реальних діалогів ===
echo 🔄 Крок 1: Конвертація TXT → JSONL
echo 🔄 Крок 1: Конвертація TXT → JSONL >> %LOG_PATH%
python scripts\convert_real_dialogs.py >> %LOG_PATH% 2>&1

REM === 🧠 Послідовне навчання ===
set CMD_LIST=^
echo 🔄 Крок 2: Побудова knowledge_chunks &&^
python trainer\build_knowledge_chunks.py &&^
echo 🔄 Крок 3: Побудова dialog_chunks &&^
python trainer\build_dialog_chunks.py &&^
echo 🔄 Крок 4: Обробка feedback &&^
python trainer\feedback_processor.py &&^
echo 🔄 Крок 5: Побудова good_index &&^
python vectorstore\build_good_index.py &&^
echo 🔄 Крок 6: Побудова bad_index &&^
python vectorstore\build_bad_index.py &&^
echo 🔄 Крок 7: Побудова knowledge_index &&^
python vectorstore\build_knowledge_index.py &&^
echo 🔄 Крок 8: Покращення bad-відповідей &&^
python trainer\strategy_refiner.py &&^
echo 🔄 Крок 9: Навчання бота &&^
python trainer\learner.py &&^
echo 🚀 Крок 10: Запуск HR-бота &&^
python bot.py

REM === Виконання команд з логуванням ===
cmd /c "!CMD_LIST!" >> %LOG_PATH% 2>&1

REM === Вивід лог-файлу після завершення ===
echo.
echo 🔎 Лог збережено у файлі: %LOG_PATH%
echo ---------------------- Вміст логу ----------------------
type %LOG_PATH%

pause
