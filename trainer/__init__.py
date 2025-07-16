# Ініціалізація пакету trainer

from .learner import learn_from_dialogs
from .feedback_processor import process_feedbacks, extract_feedback_insights
from .strategy_refiner import refine_bad_dialogs
from .build_dialog_chunks import build_dialog_chunks
from .build_knowledge_chunks import build_knowledge_chunks
from .train_from_good import train_on_good_dialogs
from .train_from_bad import train_on_bad_dialogs

__all__ = [
    "learn_from_dialogs",
    "process_feedbacks",
    "extract_feedback_insights",
    "refine_bad_dialogs",
    "build_dialog_chunks",
    "build_knowledge_chunks",
    "train_on_good_dialogs",
    "train_on_bad_dialogs"
]
