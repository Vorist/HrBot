# backend/utils/jsonl_utils.py

import os
import json
from typing import List, Dict, Any


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    """
    Завантажує список словників з .jsonl файлу.
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(path: str, items: List[Dict[str, Any]]):
    """
    Перезаписує .jsonl файл повністю новим списком об'єктів.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def append_jsonl(path: str, item: Dict[str, Any]):
    """
    Додає один об'єкт в кінець .jsonl файлу.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def validate_dialog(dialog: List[Dict[str, Any]]) -> bool:
    """
    Перевіряє, що діалог має принаймні одну репліку user і одну — bot,
    та що кожен елемент є словником з ключами 'role' і 'text'.
    """
    if not isinstance(dialog, list) or not dialog:
        return False

    has_user = has_bot = False

    for item in dialog:
        if not isinstance(item, dict):
            return False
        if 'role' not in item or 'text' not in item:
            return False
        if item['role'] == "user":
            has_user = True
        elif item['role'] == "bot":
            has_bot = True

    return has_user and has_bot
