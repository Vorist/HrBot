# bot.py
import asyncio
import random
import sys
import os
from telethon import TelegramClient, events

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import API_ID, API_HASH, SESSION_NAME
from dialog_memory import load_memory, append_to_memory, get_history
from knowledge_embeddings import search_combined_context
from utils import build_messages, get_openai_response, log, detect_source
from dialog_logger import save_good, save_bad
from dialog_evaluator import evaluate_dialog
from question_tracker import add_user_phrase
from dialog_meta import detect_meta_flags, update_meta
from trainer.strategy_refiner import refine_bad_dialogs
from trainer.feedback_processor import get_feedback_comments_for_chat

# --- Завантажуємо памʼять ---
memory = load_memory()

# --- Ініціалізація Telegram клієнта ---
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# --- Обробка вхідних повідомлень ---
@client.on(events.NewMessage(incoming=True))
async def handle(event):
    sender = await event.get_sender()
    chat_id = str(event.chat_id)
    user_input = event.raw_text.strip()

    if not user_input:
        return

    log(f"[{chat_id}] {sender.first_name}: {user_input}")

    meta_flags = detect_meta_flags(user_input)
    update_meta(memory, chat_id, meta_flags)

    add_user_phrase(user_input)

    history = get_history(memory, chat_id)
    context_chunks = search_combined_context(user_input)
    messages = build_messages(chat_id, user_input, context_chunks, memory)

    try:
        bot_response = get_openai_response(messages)
    except Exception as e:
        await event.respond(f"⚠️ OpenAI error: {e}")
        log(f"[{chat_id}] ❌ OpenAI error: {e}")
        return

    append_to_memory(memory, chat_id, user_input, bot_response)

    await asyncio.sleep(random.uniform(1.5, 5.0))
    await event.respond(bot_response)
    log(f"[{chat_id}] 🤖 HR: {bot_response}")

    history_now = get_history(memory, chat_id)
    eval_result = evaluate_dialog(history_now)
    formatted = format_dialog(history_now)

    if eval_result["dialog_score"] >= 5:
        save_good({"chat_id": chat_id, "memory": memory})
    else:
        save_bad({"chat_id": chat_id, "memory": memory})

        try:
            improved_variants = refine_bad_dialogs({"text": formatted})
            if isinstance(improved_variants, list) and improved_variants:
                joined = "\n---\n".join(i["improved"] if isinstance(i, dict) else str(i) for i in improved_variants)
                log("💡 Покращений варіант:\n" + joined)
        except Exception as e:
            log(f"⚠️ refine_bad_dialogs error: {e}")

        comments = get_feedback_comments_for_chat(chat_id)
        if comments:
            log(f"✍️ Коментарі користувача до {chat_id}:\n" + "\n".join(c["comment"] for c in comments))

    source = detect_source(formatted)
    if source != "unknown":
        log(f"[📥] Джерело: {source}")


# --- Форматування діалогу у вигляді тексту ---
def format_dialog(dialog: list) -> str:
    lines = []
    for msg in dialog:
        if "from_user" in msg:
            lines.append(f"👤 {msg['from_user']}")
        if "from_ai" in msg:
            lines.append(f"🤖 {msg['from_ai']}")
    return "\n".join(lines)


# --- Запуск ---
def main():
    print("✅ Запуск HR-бота...")
    client.start()
    client.run_until_disconnected()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Помилка: {e}")
