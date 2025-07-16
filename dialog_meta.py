import re

# --- Ключові слова для підозри --- #
SUSPICION_KEYWORDS = [
    "це скам", "вы скам", "що за компанія", "де працюєте", "легально?", "це обман",
    "робота неофіційна", "це не чорна схема?", "чи офіційно", "а що конкретно робити",
    "що за шахрайство", "а якщо мене посадять", "відмивання грошей"
]

# --- Розпізнавання запиту на російську мову --- #
RU_KEYWORDS = ["по-русски", "можно на русском", "говори рус", "давай по-русски", "по русски", "перейди на русский"]

# --- Формальний стиль --- #
FORMAL_KEYWORDS = [
    "документ", "контракт", "офіційно", "ліцензія", "закон", "юридично", "оформлення", "офіційне працевлаштування"
]

# --- Дружній / розмовний стиль --- #
CASUAL_KEYWORDS = [
    "йо", "чувак", "погнали", "впєрьод", "шо там", "ясно", "та ладно", "ну", "ага", "ммм", "окей", "нічо", "добренько"
]

# --- Гумор / емодзі --- #
HUMOR_KEYWORDS = [
    "жарт", "прикол", "ахах", "лол", "ржунімагу", "ха-ха", "ха", "😆", "😂", "😄", "🤣", "смішно"
]


def detect_meta_flags(text: str) -> dict:
    """
    Визначає мета-флаги на основі змісту повідомлення користувача.
    """
    flags = {}
    text = text.lower()

    if any(x in text for x in SUSPICION_KEYWORDS):
        flags["suspicion"] = True
    if any(x in text for x in RU_KEYWORDS):
        flags["lang"] = "ru"
    if any(x in text for x in FORMAL_KEYWORDS):
        flags["tone"] = "formal"
    elif any(x in text for x in CASUAL_KEYWORDS):
        flags["tone"] = "casual"
    if any(x in text for x in HUMOR_KEYWORDS):
        flags["humor"] = True

    return flags


def update_meta(memory: dict, chat_id: int | str, flags: dict):
    str_id = str(chat_id)
    if str_id not in memory:
        memory[str_id] = {"dialog": [], "_meta": {}}
    if "_meta" not in memory[str_id]:
        memory[str_id]["_meta"] = {}
    memory[str_id]["_meta"].update(flags)


def get_meta(memory: dict, chat_id: int | str) -> dict:
    return memory.get(str(chat_id), {}).get("_meta", {})
