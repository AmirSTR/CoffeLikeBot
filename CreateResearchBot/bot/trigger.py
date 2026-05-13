import re
import config

# Для проверки упоминания — просто имя, без захвата знаков препинания
_MENTION_RE = re.compile(re.escape(config.BOT_NAME), re.IGNORECASE)

# Для удаления — имя с опциональными окружающими запятыми и пробелами
_EXTRACT_RE = re.compile(
    r"(?:,\s*)?" + re.escape(config.BOT_NAME) + r"(?:\s*,)?",
    re.IGNORECASE,
)


def is_bot_mentioned(text: str) -> bool:
    """Возвращает True если BOT_NAME встречается в тексте (регистронезависимо)."""
    if not text:
        return False
    return bool(_MENTION_RE.search(text))


def extract_question(text: str) -> str:
    """
    Удаляет все вхождения BOT_NAME с окружающими запятыми из текста,
    сохраняя оригинальный регистр остального.
    """
    result = _EXTRACT_RE.sub(" ", text)
    # Убираем пробел перед знаками препинания: "Привет !" → "Привет!"
    result = re.sub(r" +([!?.,])", r"\1", result)
    # Схлопываем множественные пробелы
    result = re.sub(r" {2,}", " ", result).strip(" ,")
    # Если осталась только пунктуация (имя было единственным словом)
    if re.fullmatch(r"[!?.,\s]*", result):
        return ""
    return result
