import tiktoken
import config

# cl100k_base используется моделями text-embedding-3-* и gpt-4*
_enc = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, source: str) -> list[dict]:
    """
    Нарезает text на чанки по CHUNK_SIZE токенов с перекрытием CHUNK_OVERLAP.
    Возвращает список dict: {"text", "source", "chunk_id"}.
    """
    if not text or not text.strip():
        return []

    tokens = _enc.encode(text)
    total = len(tokens)

    if total == 0:
        return []

    step = config.CHUNK_SIZE - config.CHUNK_OVERLAP  # всегда > 0, гарантировано config.py
    chunks: list[dict] = []
    chunk_id = 0
    start = 0

    while start < total:
        end = min(start + config.CHUNK_SIZE, total)
        chunk_tokens = tokens[start:end]
        chunks.append({
            "text": _enc.decode(chunk_tokens),
            "source": source,
            "chunk_id": chunk_id,
        })
        chunk_id += 1

        if end == total:
            break
        start += step

    return chunks
