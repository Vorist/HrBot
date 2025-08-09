# trainer/strategy_refiner.py

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import BAD_DIALOGS_PATH, REFINED_BAD_PATH
from utils import split_dialog_into_chunks, log, format_text
from openai import OpenAI  # GPT-перефразування

client = OpenAI()

def dialog_to_text(dialog):
    """Преобразует диалог из списка сообщений (role/text) в многострочный текст с emoji."""
    return "\n".join([
        f"{'👤' if msg['role'] == 'user' else '🤖'} {msg['text']}".strip()
        for msg in dialog if 'role' in msg and 'text' in msg
    ])

def refine_bad_dialogs(dialog=None):
    """
    Если передан dialog — переформулирует только его.
    Если нет — читает BAD_DIALOGS_PATH и обрабатывает все bad-диалоги.
    """
    bad_dialogs = []

    # Поддержка одиночного и батчевого режима
    if dialog:
        if isinstance(dialog, dict) and 'dialog' in dialog and isinstance(dialog['dialog'], list):
            bad_dialogs = [dialog]
        else:
            log("❗️ Вхідний діалог має невірний формат!")
            return []
    elif os.path.exists(BAD_DIALOGS_PATH):
        with open(BAD_DIALOGS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if isinstance(obj, dict) and "dialog" in obj and isinstance(obj["dialog"], list):
                        bad_dialogs.append(obj)
                except json.JSONDecodeError:
                    continue

    improved = []

    for item in bad_dialogs:
        raw_text = dialog_to_text(item["dialog"]).strip()
        if not raw_text:
            continue

        prompt = [
            {"role": "system", "content": (
                "Ти досвідчений HR. Перефразуй цей фрагмент діалогу, зроби його ввічливішим, структурованішим і результативнішим. "
                "Не змінюй суть, але покращ логіку і формулювання. Пиши коротко і максимально людяно."
            )},
            {"role": "user", "content": f"Оригінал:\n{raw_text}"}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=prompt,
                temperature=0.5,
            )
            new_text = response.choices[0].message.content.strip()
            improved.append({
                "original": format_text(raw_text),
                "improved": {"text": format_text(new_text)}
            })
            log(f"✅ Refined bad-dialog: {raw_text[:60]} → {new_text[:60]}")
        except Exception as e:
            log(f"⚠️ refine_bad_dialogs() error: {e}")

    if not dialog:
        os.makedirs(os.path.dirname(REFINED_BAD_PATH), exist_ok=True)
        with open(REFINED_BAD_PATH, "w", encoding="utf-8") as f:
            for entry in improved:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log(f"📝 Збережено {len(improved)} переформульованих bad-діалогів → {REFINED_BAD_PATH}")

    return improved

if __name__ == "__main__":
    refine_bad_dialogs()
