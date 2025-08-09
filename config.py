# config.py

import os
from dotenv import load_dotenv

# === 🧪 Загрузка переменных окружения ===
load_dotenv()

# === 🤖 Telegram Userbot API ===
API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "hr_userbot")

# === 🧠 OpenAI API ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))

# === 📁 Директории ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")  # Для обучающих скриптов
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Гарантируем, что базовые папки существуют
for _dir in (DATA_DIR, PROMPTS_DIR, VECTORSTORE_DIR, TRAINER_DIR, LOGS_DIR):
    os.makedirs(_dir, exist_ok=True)

# === 🕓 Параметры обучения ===
TRAIN_TIMEOUT_SECONDS = int(os.getenv("TRAIN_TIMEOUT_SECONDS", 600))  # 10 мин

# === 📜 Промпты и справочники ===
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.txt")
CONDITIONS_PATH = os.path.join(DATA_DIR, "conditions.txt")

# 👇 Разводим “витрину” FAQ и внутреннее хранилище счётчиков
FREQUENT_QUESTIONS_PUBLIC_PATH = os.path.join(DATA_DIR, "frequent_questions.json")       # список [{question, answer}]
FREQUENT_QUESTIONS_STORE_PATH = os.path.join(DATA_DIR, "frequent_questions_store.json")  # словарь {question: int}
# Для обратной совместимости
FREQUENT_QUESTIONS_PATH = FREQUENT_QUESTIONS_PUBLIC_PATH

# === 💬 Диалоги ===
GOOD_DIALOGS_PATH = os.path.join(DATA_DIR, "good_dialogs.jsonl")
BAD_DIALOGS_PATH = os.path.join(DATA_DIR, "bad_dialogs.jsonl")
REFINED_BAD_PATH = os.path.join(DATA_DIR, "refined_bad_dialogs.jsonl")

# === 🧑‍💼 Реальные диалоги менеджеров ===
REAL_DIALOGS_PATH = os.path.join(DATA_DIR, "real_dialogs.txt")
REAL_DIALOGS_TXT_PATH = REAL_DIALOGS_PATH  # совместимость

AUTO_REAL_LOG_PATH = os.path.join(DATA_DIR, "auto_captured_dialogs.jsonl")
SAVE_AUTO_REAL_DIALOGS = os.getenv("SAVE_AUTO_REAL_DIALOGS", "true").lower() in ("1", "true", "yes")
USED_DIALOGS_PATH = os.path.join(DATA_DIR, "used_real_dialogs.json")

# === 💬 Фидбеки ===
FEEDBACK_COMMENTS_PATH = os.path.join(DATA_DIR, "feedback_comments.jsonl")
FEEDBACK_LESSONS_PATH = os.path.join(DATA_DIR, "feedback_lessons.json")

# === 📚 Чанки для эмбеддинга и FAISS ===
DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "dialog_chunks.jsonl")
GOOD_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "good_dialog_chunks.json")
BAD_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "bad_dialog_chunks.json")
REAL_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "real_dialog_chunks.json")
KNOWLEDGE_CHUNKS_PATH = os.path.join(DATA_DIR, "knowledge_chunks.json")
TRAINING_OUTPUT_PATH = os.path.join(DATA_DIR, "training_knowledge.json")

# === 🧠 FAISS-индексы ===
KNOWLEDGE_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "knowledge_faiss.index")
DIALOG_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "dialog_faiss.index")
GOOD_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "good_faiss.index")
BAD_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "bad_faiss.index")
REAL_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "real_faiss.index")

# === 🧠 Кеш и логи ===
MEMORY_PATH = os.path.join(DATA_DIR, "memory.json")
EMBED_CACHE_PATH = os.path.join(DATA_DIR, "embed_cache.json")
LOG_PATH = os.path.join(DATA_DIR, "bot_log.txt")

# === Экспорт переменных для автокомплита и IDE ===
__all__ = [
    # TG
    "API_ID", "API_HASH", "SESSION_NAME",
    # OpenAI
    "OPENAI_API_KEY", "CHAT_MODEL", "EMBEDDING_MODEL", "TOP_K_RESULTS",
    # Dirs
    "BASE_DIR", "DATA_DIR", "PROMPTS_DIR", "VECTORSTORE_DIR", "TRAINER_DIR", "LOGS_DIR",
    # Train
    "TRAIN_TIMEOUT_SECONDS",
    # Prompts / refs
    "SYSTEM_PROMPT_PATH", "CONDITIONS_PATH",
    "FREQUENT_QUESTIONS_PUBLIC_PATH", "FREQUENT_QUESTIONS_STORE_PATH", "FREQUENT_QUESTIONS_PATH",
    # Dialogs
    "GOOD_DIALOGS_PATH", "BAD_DIALOGS_PATH", "REFINED_BAD_PATH",
    "REAL_DIALOGS_PATH", "REAL_DIALOGS_TXT_PATH", "AUTO_REAL_LOG_PATH", "SAVE_AUTO_REAL_DIALOGS",
    "USED_DIALOGS_PATH",
    # Feedback
    "FEEDBACK_COMMENTS_PATH", "FEEDBACK_LESSONS_PATH",
    # Chunks
    "DIALOG_CHUNKS_PATH", "GOOD_DIALOG_CHUNKS_PATH", "BAD_DIALOG_CHUNKS_PATH",
    "REAL_DIALOG_CHUNKS_PATH", "KNOWLEDGE_CHUNKS_PATH", "TRAINING_OUTPUT_PATH",
    # Indexes
    "KNOWLEDGE_INDEX_PATH", "DIALOG_INDEX_PATH", "GOOD_INDEX_PATH", "BAD_INDEX_PATH", "REAL_INDEX_PATH",
    # Cache / logs
    "MEMORY_PATH", "EMBED_CACHE_PATH", "LOG_PATH",
]
