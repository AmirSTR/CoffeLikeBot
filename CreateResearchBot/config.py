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
    "Ты помощник для баристов. Отвечай строго на основе предоставленного контекста. "
    'Если ответа нет в контексте — скажи "Я не нашёл информацию по этому вопросу". '
    "Отвечай кратко и по делу. Не придумывай информацию. "
    "Язык ответа: русский."
)

LOG_FILE: str = "logs/bot.log"
