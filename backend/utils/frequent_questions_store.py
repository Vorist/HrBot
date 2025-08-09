# backend/utils/frequent_questions_store.py
import os, json, re, sys
from datetime import datetime

# безопасный импорт конфига
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import (
    FREQUENT_QUESTIONS_STORE_PATH,  # JSON-словарь: {"вопрос": count}
    FREQUENT_QUESTIONS_PUBLIC_PATH, # Публичный список: [{"question": "...", "answer": ""}, ...]
)

_WORD_RE = re.compile(r"\w", re.UNICODE)

def _ensure_dirs(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def _load_store() -> dict:
    if not os.path.exists(FREQUENT_QUESTIONS_STORE_PATH):
        return {}
    try:
        with open(FREQUENT_QUESTIONS_STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save_store(store: dict):
    _ensure_dirs(FREQUENT_QUESTIONS_STORE_PATH)
    with open(FREQUENT_QUESTIONS_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

def _save_public(store: dict, top: int | None = None):
    """
    Генерирует публичный список FAQ (без перезаписи ответов, если они уже есть).
    Если FREQUENT_QUESTIONS_PUBLIC_PATH существует и это список, стараемся
    сохранить существующие ответы.
    """
    # существующие ответы
    existing_answers = {}
    if os.path.exists(FREQUENT_QUESTIONS_PUBLIC_PATH):
        try:
            with open(FREQUENT_QUESTIONS_PUBLIC_PATH, "r", encoding="utf-8") as f:
                cur = json.load(f)
            if isinstance(cur, list):
                for item in cur:
                    q = str(item.get("question", "")).strip()
                    a = str(item.get("answer", "")).strip()
                    if q:
                        existing_answers[q] = a
        except Exception:
            pass

    items = sorted(store.items(), key=lambda kv: kv[1], reverse=True)
    if top is not None:
        items = items[:top]

    out = []
    for q, _cnt in items:
        out.append({
            "question": q,
            "answer": existing_answers.get(q, "")
        })

    _ensure_dirs(FREQUENT_QUESTIONS_PUBLIC_PATH)
    with open(FREQUENT_QUESTIONS_PUBLIC_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

def normalize_question(text: str) -> str | None:
    if not text:
        return None
    # быстрый фильтр — должна быть хотя бы 1 «словесная» буква/цифра
    if not _WORD_RE.search(text):
        return None
    q = " ".join(text.strip().split())
    # трим вопросительный знак, но не обязателен
    return q

def add_question(text: str, *, autocommit_public: bool = True, top: int | None = None) -> bool:
    """
    Увеличивает счётчик вопроса в приватном хранилище.
    При autocommit_public=True — синхронизирует публичный список.
    """
    q = normalize_question(text)
    if not q:
        return False
    store = _load_store()
    store[q] = int(store.get(q, 0)) + 1
    _save_store(store)
    if autocommit_public:
        _save_public(store, top=top)
    return True

def bulk_add(questions: list[str], *, autocommit_public: bool = True, top: int | None = None) -> int:
    cnt = 0
    store = _load_store()
    for raw in questions or []:
        q = normalize_question(raw)
        if not q:
            continue
        store[q] = int(store.get(q, 0)) + 1
        cnt += 1
    _save_store(store)
    if autocommit_public:
        _save_public(store, top=top)
    return cnt
