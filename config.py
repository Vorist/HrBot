import os
from dotenv import load_dotenv

# === 🧪 Завантаження змінних середовища ===
load_dotenv()

# === 🤖 Telegram API ===
API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_NAME = "hr_userbot"

# === 🧠 OpenAI API ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = "gpt-4o"
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K_RESULTS = 5  # Кількість результатів з FAISS для пошуку

# === 📁 Основні директорії ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

# === 📚 Промпти та знання ===
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.txt")
CONDITIONS_PATH = os.path.join(DATA_DIR, "conditions.txt")
FREQUENT_QUESTIONS_PATH = os.path.join(DATA_DIR, "frequent_questions.json")

# === 💬 Діалоги ===
GOOD_DIALOGS_PATH = os.path.join(DATA_DIR, "good_dialogs.jsonl")
BAD_DIALOGS_PATH = os.path.join(DATA_DIR, "bad_dialogs.jsonl")
REAL_DIALOGS_PATH = os.path.join(DATA_DIR, "real_dialogs.jsonl")
REAL_DIALOGS_TXT_PATH = os.path.join(DATA_DIR, "real_dialogs.txt")
FEEDBACK_COMMENTS_PATH = os.path.join(DATA_DIR, "feedback_comments.jsonl")
USED_DIALOGS_PATH = os.path.join(DATA_DIR, "used_real_dialogs.json")

# === 📘 Чанки знань і діалогів ===
# === 📘 Чанки знань і діалогів ===
GOOD_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "good_dialog_chunks.json")
BAD_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "bad_dialog_chunks.json")  # 🔧 додано
DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "dialog_chunks.json")
REAL_DIALOG_CHUNKS_PATH = os.path.join(DATA_DIR, "real_dialog_chunks.json")
KNOWLEDGE_CHUNKS_PATH = os.path.join(DATA_DIR, "knowledge_chunks.json")
TRAINING_OUTPUT_PATH = os.path.join(DATA_DIR, "training_knowledge.json")
REFINED_BAD_PATH = os.path.join(DATA_DIR, "refined_bad_dialogs.jsonl")
FEEDBACK_LESSONS_PATH = os.path.join(DATA_DIR, "feedback_lessons.json")


# === 🧠 FAISS-індекси ===
KNOWLEDGE_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "knowledge_faiss.index")
DIALOG_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "dialog_faiss.index")
GOOD_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "good_faiss.index")
BAD_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "bad_faiss.index")
REAL_INDEX_PATH = os.path.join(VECTORSTORE_DIR, "real_faiss.index")

# === 💾 Памʼять, кеш, лог ===
MEMORY_PATH = os.path.join(DATA_DIR, "memory.json")
EMBED_CACHE_PATH = os.path.join(DATA_DIR, "embed_cache.json")
LOG_PATH = os.path.join(DATA_DIR, "bot_log.txt")
