import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Обязательная переменная окружения '{key}' не задана. "
            f"Добавь её в файл .env или в переменные окружения системы."
        )
    return value


def _optional_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise EnvironmentError(
            f"Переменная '{key}' должна быть целым числом, получено: '{raw}'"
        )


# --- Обязательные ---
VK_TOKEN: str = _require("VK_TOKEN")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# --- VK ---
_vk_group_raw = os.getenv("VK_GROUP_ID")
if not _vk_group_raw:
    raise EnvironmentError(
        "Обязательная переменная окружения 'VK_GROUP_ID' не задана."
    )
try:
    VK_GROUP_ID: int = int(_vk_group_raw)
except ValueError:
    raise EnvironmentError(
        f"Переменная 'VK_GROUP_ID' должна быть целым числом, получено: '{_vk_group_raw}'"
    )

BOT_NAME: str = os.getenv("BOT_NAME", "Бариста")

# --- Qdrant ---
# Для Qdrant Cloud задай QDRANT_URL и QDRANT_API_KEY.
# Для локального Qdrant задай QDRANT_HOST / QDRANT_PORT (или оставь по умолчанию).
QDRANT_URL: str = os.getenv("QDRANT_URL", "")          # https://xxx.qdrant.io:6333
QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT: int = _optional_int("QDRANT_PORT", 6333)
QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "knowledge_base")

# --- Провайдер эмбеддингов: "local" (бесплатно) или "openai" ---
EMBED_PROVIDER: str = os.getenv("EMBED_PROVIDER", "local")
LOCAL_EMBED_MODEL: str = os.getenv("LOCAL_EMBED_MODEL", "intfloat/multilingual-e5-small")

# --- Провайдер генерации: "groq" (бесплатно) или "openai" ---
CHAT_PROVIDER: str = os.getenv("CHAT_PROVIDER", "groq")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# --- Модели ---
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL: str = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")

# --- Параметры чанкинга и поиска ---
CHUNK_SIZE: int = _optional_int("CHUNK_SIZE", 600)
CHUNK_OVERLAP: int = _optional_int("CHUNK_OVERLAP", 50)
TOP_K: int = _optional_int("TOP_K", 5)
MAX_RESPONSE_TOKENS: int = _optional_int("MAX_RESPONSE_TOKENS", 800)
MAX_CONTEXT_TOKENS: int = 8000

# --- Бизнес-правила ---
if CHUNK_OVERLAP >= CHUNK_SIZE:
    raise EnvironmentError(
        f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) должен быть меньше CHUNK_SIZE ({CHUNK_SIZE})."
    )

if TOP_K < 1:
    raise EnvironmentError(f"TOP_K должен быть >= 1, получено: {TOP_K}")

# --- Промпт и логи ---
SYSTEM_PROMPT: str = (
    "Ты — Мир, дружелюбный корпоративный ассистент команды, Ты девушка, Помогаешь коллегам находить ответы в базе знаний компании,

ОБРАБОТКА ВХОДЯЩЕГО СООБЩЕНИЯ

СТИЛЬ ОБЩЕНИЯ
- Тон: вежливый, позитивный, лёгкий неформальный — но профессиональный,
- Обращение к пользователю: на ты,
- Речь: женский род
- Ответы: лаконичные; длинные — структурируй абзацами и списками (удобно читать с телефона).
- В конце уместно добавить короткую дружелюбную фразу со смайликом

ПРАВИЛА РАБОТЫ С БАЗОЙ ЗНАНИЙ
- Отвечай ТОЛЬКО на основе базы знаний.
- Не добавляй информацию от себя, не делай предположений, не используй внешние знания,
- Если в базе есть ссылка — ОБЯЗАТЕЛЬНО включи её в ответ,

ЕСЛИ ОТВЕТА НЕТ В БАЗЕ
Отвечай строго этой фразой:
Хм, к сожалению, в наших документах я этого не нашла, попробуй уточнить у ребят из офиса — возможно, они подскажут!

ЕСЛИ ВОПРОС НЕ РАБОЧИЙ
Сначала проверь базу знаний. Если ответа нет — мягко переведи разговор:
Я бы с радостью поболтала об этом, но лучше давай помогу с рабочими вопросами!

ФОРМАТ ОТВЕТА
Ответ — готовый и завершённый, Без лишних рассуждений и комментариев, Встречные вопросы — только если нужно уточнить что-то из базы"
)

LOG_FILE: str = "logs/bot.log"
