import sys, os
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    GOOD_DIALOGS_PATH, BAD_DIALOGS_PATH, REAL_DIALOGS_TXT_PATH,
    TRAINING_OUTPUT_PATH, FEEDBACK_COMMENTS_PATH
)
from knowledge_embeddings import embed_text
from utils import split_dialog_into_chunks, log
from trainer.feedback_processor import extract_feedback_insights
from trainer.strategy_refiner import refine_bad_dialogs


def load_text_dialogs(path):
    if not os.path.exists(path):
        return []
    dialogs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if isinstance(obj, dict) and "text" in obj:
                    dialogs.append(obj["text"])
            except json.JSONDecodeError:
                continue
    return dialogs


def load_real_dialogs_from_txt(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    return blocks


def learn_from_dialogs():
    log("[📚] Навчання на основі good, bad, real (txt), feedback, refined...")

    combined_chunks = []

    def add_chunks(dialogs, label):
        for dialog in dialogs:
            chunks = split_dialog_into_chunks(dialog, label=label)
            combined_chunks.extend(chunks)

    add_chunks(load_text_dialogs(GOOD_DIALOGS_PATH), "good")
    add_chunks(load_text_dialogs(BAD_DIALOGS_PATH), "bad")
    add_chunks(load_real_dialogs_from_txt(REAL_DIALOGS_TXT_PATH), "real")

    if os.path.exists(FEEDBACK_COMMENTS_PATH):
        try:
            with open(FEEDBACK_COMMENTS_PATH, "r", encoding="utf-8") as f:
                feedback_entries = [json.loads(line) for line in f if line.strip()]
            feedback_chunks = extract_feedback_insights(feedback_entries)
            for fb in feedback_chunks:
                recommendation = fb.get("recommendation", "").strip()
                if recommendation:
                    combined_chunks.append({
                        "text": recommendation,
                        "label": "feedback"
                    })
        except Exception as e:
            log(f"⚠️ Не вдалося прочитати коментарі: {e}")

    try:
        refined_chunks = refine_bad_dialogs()
        for item in refined_chunks:
            improved = item.get("improved", "")
            if isinstance(improved, dict):
                improved = improved.get("text", "")
            improved = improved.strip()
            if improved:
                combined_chunks.append({
                    "text": improved,
                    "label": "refined"
                })
    except Exception as e:
        log(f"⚠️ Не вдалося покращити погані відповіді: {e}")

    embedded_chunks = []
    for chunk in combined_chunks:
        text = chunk.get("text", "").strip()
        label = chunk.get("label", "unknown")
        if not text:
            continue
        vector = embed_text(text)
        if vector is not None and isinstance(vector, np.ndarray) and vector.any():
            embedded_chunks.append({
                "text": text,
                "label": label,
                "vector": vector.tolist()
            })

    os.makedirs(os.path.dirname(TRAINING_OUTPUT_PATH), exist_ok=True)
    with open(TRAINING_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)

    log(f"✅ Навчання завершено: {len(embedded_chunks)} ембедінгів збережено → {TRAINING_OUTPUT_PATH}")


if __name__ == "__main__":
    learn_from_dialogs()
