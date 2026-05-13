import logging
import random

from bot.trigger import is_bot_mentioned, extract_question
from rag.generator import generate

logger = logging.getLogger(__name__)

_FALLBACK = "Произошла ошибка, попробуй позже"
_NO_QUESTION = "Привет! Задай мне вопрос — я постараюсь помочь."


def handle_message(vk, event) -> None:
    message = event.obj.message
    text = (message.get("text") or "").strip()
    peer_id = message.get("peer_id")
    from_id = message.get("from_id")

    if not is_bot_mentioned(text):
        return

    question = extract_question(text)
    logger.info("Запрос от peer_id=%s from_id=%s", peer_id, from_id)

    if not question:
        _send(vk, peer_id, _NO_QUESTION)
        return

    try:
        answer = generate(question)
    except Exception:
        logger.exception("Неперехваченная ошибка generate() peer_id=%s", peer_id)
        answer = _FALLBACK

    _send(vk, peer_id, answer)


def _send(vk, peer_id: int, message: str) -> None:
    try:
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.getrandbits(31),
        )
    except Exception:
        logger.exception("Ошибка отправки сообщения peer_id=%s", peer_id)
