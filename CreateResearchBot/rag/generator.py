import argparse
import logging

import config
from rag.search import search

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        if config.CHAT_PROVIDER == "groq":
            from groq import Groq
            _client = Groq(api_key=config.GROQ_API_KEY)
        else:
            from openai import OpenAI
            _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def _count_tokens(text: str) -> int:
    return len(text) // 4


def _build_context(chunks: list[dict]) -> str:
    parts: list[str] = []
    used = _count_tokens(config.SYSTEM_PROMPT)
    for chunk in chunks:
        text = chunk.get("text", "").strip()
        if not text:
            continue
        tokens = _count_tokens(text)
        if used + tokens > config.MAX_CONTEXT_TOKENS:
            break
        parts.append(text)
        used += tokens
    return "\n\n".join(parts)


def generate(question: str) -> str:
    if not question or not question.strip():
        return "Пожалуйста, задай вопрос."

    chunks = search(question)
    context = _build_context(chunks)

    user_message = f"Контекст:\n{context}\n\nВопрос: {question}" if context else f"Вопрос: {question}"

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        response = _get_client().chat.completions.create(
            model=config.CHAT_MODEL,
            messages=messages,
            max_tokens=config.MAX_RESPONSE_TOKENS,
            temperature=0.3,
        )
        answer = response.choices[0].message.content
        return answer.strip() if answer else "Я не нашёл информацию по этому вопросу."
    except Exception:
        logger.exception("Ошибка %s API при генерации ответа", config.CHAT_PROVIDER)
        return "Произошла ошибка, попробуй позже"


if __name__ == "__main__":
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="Ручное тестирование RAG-генератора")
    parser.add_argument("--question", required=True, help="Вопрос для бота")
    args = parser.parse_args()

    print(generate(args.question))
