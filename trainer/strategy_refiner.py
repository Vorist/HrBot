# trainer/strategy_refiner.py

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import BAD_DIALOGS_PATH, REFINED_BAD_PATH
from utils import split_dialog_into_chunks, log, format_text
from openai import OpenAI  # GPT-перефразування

client = OpenAI()

def refine_bad_dialogs(dialog=None):
    """Якщо передано dialog — покращуємо тільки його.
       Якщо ні — читаємо BAD_DIALOGS_PATH і опрацьовуємо всі."""

    bad_dialogs = []

    if dialog:
        bad_dialogs = [dialog]
    elif os.path.exists(BAD_DIALOGS_PATH):
        with open(BAD_DIALOGS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if isinstance(obj, dict) and "text" in obj:
                        bad_dialogs.append(obj)
                except json.JSONDecodeError:
                    continue

    improved = []

    for item in bad_dialogs:
        raw_text = item.get("text", "").strip()
        if not raw_text:
            continue

        prompt = [
            {"role": "system", "content": "Ти досвідчений HR. Покращ цей фрагмент діалогу, щоб зробити його ввічливішим, зрозумілішим і ефективнішим."},
            {"role": "user", "content": f"Оригінал:\n{raw_text}"}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=prompt,
                temperature=0.7
            )
            new_text = response.choices[0].message.content.strip()
            improved.append({
                "original": format_text(raw_text),
                "improved": {"text": format_text(new_text)}
            })
        except Exception as e:
            log(f"⚠️ refine_bad_dialogs() error: {e}")

    if not dialog:
        with open(REFINED_BAD_PATH, "w", encoding="utf-8") as f:
            for entry in improved:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return improved


if __name__ == "__main__":
    refine_bad_dialogs()
