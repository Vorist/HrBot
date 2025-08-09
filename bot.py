# bot.py
import asyncio
import random
import sys
import os
from datetime import datetime
from telethon import TelegramClient, events

# --- sys.path для локального запуска/скриптов ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# --- Конфиг и утилиты ---
from config import (
    API_ID, API_HASH, SESSION_NAME,
    SAVE_AUTO_REAL_DIALOGS, AUTO_REAL_LOG_PATH,
)
from dialog_memory import load_memory, append_to_memory, get_history
from knowledge_embeddings import search_combined_context
from utils import build_messages, get_openai_response, log
from dialog_logger import save_good, save_bad
from dialog_evaluator import evaluate_dialog
from trainer.strategy_refiner import refine_bad_dialogs
from trainer.feedback_processor import get_feedback_comments_for_chat

# Частые вопросы — новый стор
from backend.utils.frequent_questions_store import add_question as faq_add_question


# =========================
#      ВСПОМОГАТЕЛЬНОЕ
# =========================

def looks_like_question(text: str) -> bool:
    """Простая эвристика: вопросительный знак или «как/что/когда/где/сколько/чому/навіщо/чи» и т.п."""
    if not text:
        return False
    t = text.strip().lower()
    if "?" in t:
        return True
    starters = ("как", "что", "когда", "где", "зачем", "почему", "сколько",
                "чому", "навіщо", "де", "котрий", "чи", "який")
    return any(t.startswith(w + " ") for w in starters)

def safe_update_faq(user_text: str):
    """Безопасно инкрементируем счётчик вопроса (не рушим диалог при ошибке)."""
    try:
        if looks_like_question(user_text):
            faq_add_question(user_text, autocommit_public=True)
    except Exception:
        # не ломаем бота, просто пропускаем
        pass

def format_dialog(dialog: list) -> str:
    """Форматируем историю для логов/оценки."""
    lines = []
    for msg in dialog:
        if "from_user" in msg and msg["from_user"]:
            lines.append(f"👤 {msg['from_user']}")
        if "from_ai" in msg and msg["from_ai"]:
            lines.append(f"🤖 {msg['from_ai']}")
    return "\n".join(lines)

def log_auto_dialog_jsonl(chat_id: str, history_snapshot: list, source: str = "telegram"):
    """Логируем авто-диалоги в JSONL (если включено). РЕАЛЬНЫЕ эталонные real_dialogs.txt не трогаем."""
    if not SAVE_AUTO_REAL_DIALOGS:
        return
    if not history_snapshot:
        return
    try:
        os.makedirs(os.path.dirname(AUTO_REAL_LOG_PATH), exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "source": source,
            "messages": history_snapshot,  # [{'from_user': '...'}, {'from_ai': '...'}, ...]
        }
        with open(AUTO_REAL_LOG_PATH, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # лог — в консоль, но без падения бота
        log(f"[{chat_id}] ⚠️ Не удалось записать авто-диалог у {AUTO_REAL_LOG_PATH}")

# =========================
#      ИНИЦИАЛИЗАЦИЯ
# =========================

memory = load_memory()
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# =========================
#    ОБРАБОТЧИК СООБЩЕНИЙ
# =========================

@client.on(events.NewMessage(incoming=True))
async def handle(event):
    sender = await event.get_sender()
    chat_id = str(event.chat_id)
    user_input = (event.raw_text or "").strip()
    if not user_input:
        return

    log(f"[{chat_id}] {getattr(sender, 'first_name', 'User')}: {user_input}")

    # 1) обновляем FAQ-счётчик, если это вопрос
    safe_update_faq(user_input)

    # 2) контекст и сообщения для LLM
    history = get_history(memory, chat_id)
    context_chunks = search_combined_context(user_input)
    messages = build_messages(chat_id, user_input, context_chunks, memory)

    # 3) LLM-ответ
    try:
        bot_response = get_openai_response(messages)
    except Exception as e:
        err = f"⚠️ OpenAI error: {e}"
        await event.respond(err)
        log(f"[{chat_id}] {err}")
        return

    # 4) сохраняем в память, отвечаем пользователю
    append_to_memory(memory, chat_id, user_input, bot_response)

    # немного «человечности»
    await asyncio.sleep(random.uniform(1.2, 3.2))
    try:
        await event.respond(bot_response)
    except Exception as e:
        log(f"[{chat_id}] ⚠️ Ошибка отправки сообщения: {e}")
        return

    log(f"[{chat_id}] 🤖 HR: {bot_response}")

    # 5) оценка текущего диалога
    history_now = get_history(memory, chat_id)
    formatted = format_dialog(history_now)

    # Авто-лог JSONL (НЕ в real_dialogs.txt)
    log_auto_dialog_jsonl(chat_id, history_now, source="telegram")

    eval_result = {}
    try:
        eval_result = evaluate_dialog(history_now) or {}
    except Exception:
        # не критично
        eval_result = {}

    score = int(eval_result.get("dialog_score", 0))

    if score >= 5:
        save_good({"chat_id": chat_id, "memory": memory})
    else:
        save_bad({"chat_id": chat_id, "memory": memory})

        # Попытка автоподсказок улучшения
        try:
            improved_variants = refine_bad_dialogs({"text": formatted})
            if isinstance(improved_variants, list) and improved_variants:
                joined = "\n---\n".join(
                    (iv.get("improved", {}).get("text", "") if isinstance(iv, dict) else str(iv)).strip()
                    for iv in improved_variants
                    if iv
                ).strip()
                if joined:
                    log("💡 Покращений варіант:\n" + joined)
        except Exception as e:
            log(f"[{chat_id}] ⚠️ refine_bad_dialogs error: {e}")

        # Вытащим возможные фидбеки по конкретному чату
        try:
            comments = get_feedback_comments_for_chat(chat_id)
            if comments:
                from itertools import islice
                preview = "\n".join(c.get("comment", "") for c in islice(comments, 5))
                log(f"✍️ Коментарі користувача до {chat_id}:\n{preview}")
        except Exception:
            pass


# =========================
#          ЗАПУСК
# =========================

def main():
    print("✅ Запуск HR-бота...")
    client.start()
    client.run_until_disconnected()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Помилка: {e}")
