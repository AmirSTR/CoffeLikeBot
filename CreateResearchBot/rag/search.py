import argparse
import logging

from qdrant_client import QdrantClient

import config
from rag.embedder import get_embedding

logger = logging.getLogger(__name__)

_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        if config.QDRANT_URL:
            _client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY or None)
        else:
            _client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    return _client


def search(query: str) -> list[dict]:
    """
    Эмбеддит query и возвращает топ-TOP_K чанков из Qdrant.
    Каждый элемент: {"text": str, "source": str, "chunk_id": int, "score": float}.
    При ошибке Qdrant логирует и возвращает [].
    """
    if not query or not query.strip():
        return []

    try:
        vector = get_embedding(query)
    except Exception:
        logger.exception("Ошибка при получении эмбеддинга запроса")
        return []

    try:
        # qdrant-client >= 1.7: search() удалён, используем query_points()
        response = _get_client().query_points(
            collection_name=config.QDRANT_COLLECTION,
            query=vector,
            limit=config.TOP_K,
            with_payload=True,
        )
    except Exception:
        logger.exception("Ошибка при поиске в Qdrant (коллекция '%s')", config.QDRANT_COLLECTION)
        return []

    results = []
    for hit in response.points:
        payload = hit.payload or {}
        results.append({
            "text": payload.get("text", ""),
            "source": payload.get("source", ""),
            "chunk_id": payload.get("chunk_id", -1),
            "score": round(hit.score, 4),
        })

    logger.debug("search('%s'): найдено %d результатов", query[:60], len(results))
    return results


if __name__ == "__main__":
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Ручной поиск по базе знаний"
    )
    parser.add_argument("--query", required=True, help="Поисковый запрос")
    args = parser.parse_args()

    chunks = search(args.query)

    if not chunks:
        print("Ничего не найдено.")
    else:
        print(f"Топ-{len(chunks)} результатов для: «{args.query}»\n")
        for i, chunk in enumerate(chunks, 1):
            print(f"[{i}] score={chunk['score']:.4f}  {chunk['source']} (chunk #{chunk['chunk_id']})")
            print(f"     {chunk['text'][:200].strip()}")
            print()
