import argparse
import logging
import os
import pathlib
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

import config
from ingestion.parser import parse_file, SUPPORTED_EXTENSIONS
from ingestion.chunker import chunk_text
from rag.embedder import get_embeddings_batch

logger = logging.getLogger(__name__)

UPSERT_BATCH_SIZE = 100


def _get_client() -> QdrantClient:
    if config.QDRANT_URL:
        return QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY or None)
    return QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)


def _ensure_collection(client: QdrantClient, vector_size: int) -> None:
    existing = {c.name for c in client.get_collections().collections}
    if config.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Создана коллекция '%s' (dim=%d)", config.QDRANT_COLLECTION, vector_size)
    else:
        logger.info("Коллекция '%s' уже существует", config.QDRANT_COLLECTION)


def _collect_chunks(directory: pathlib.Path) -> list[dict]:
    """Парсит все поддерживаемые файлы в директории, возвращает чанки."""
    files = sorted(f for f in directory.rglob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS)
    if not files:
        logger.warning("Нет поддерживаемых файлов в %s", directory)
        return []

    all_chunks: list[dict] = []
    for file in files:
        try:
            text = parse_file(file)
            chunks = chunk_text(text, source=file.name)
            all_chunks.extend(chunks)
            logger.info("  %s → %d чанков", file.name, len(chunks))
            print(f"  {file.name} → {len(chunks)} чанков")
        except Exception:
            logger.exception("Ошибка при обработке файла: %s", file.name)
            print(f"  [ОШИБКА] {file.name} — пропущен, см. лог")

    return all_chunks


def _embed_chunks(chunks: list[dict]) -> list[PointStruct]:
    """Получает эмбеддинги батчами, возвращает готовые PointStruct."""
    texts = [c["text"] for c in chunks]
    points: list[PointStruct] = []
    total = len(texts)

    for batch_start in range(0, total, UPSERT_BATCH_SIZE):
        batch_end = min(batch_start + UPSERT_BATCH_SIZE, total)
        batch_texts = texts[batch_start:batch_end]
        batch_chunks = chunks[batch_start:batch_end]

        try:
            vectors = get_embeddings_batch(batch_texts)
        except Exception:
            logger.exception(
                "Ошибка при получении эмбеддингов для батча %d–%d", batch_start, batch_end
            )
            print(f"  [ОШИБКА] батч {batch_start}–{batch_end} пропущен, см. лог")
            continue

        for chunk, vector in zip(batch_chunks, vectors):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=chunk,
                )
            )

        print(f"  Эмбеддинги: {batch_end}/{total}")

    return points


def _upsert_points(client: QdrantClient, points: list[PointStruct]) -> int:
    """Загружает точки в Qdrant батчами. Возвращает число успешно загруженных."""
    uploaded = 0
    for batch_start in range(0, len(points), UPSERT_BATCH_SIZE):
        batch = points[batch_start : batch_start + UPSERT_BATCH_SIZE]
        try:
            client.upsert(collection_name=config.QDRANT_COLLECTION, points=batch)
            uploaded += len(batch)
        except Exception:
            logger.exception(
                "Ошибка при upsert батча %d–%d", batch_start, batch_start + len(batch)
            )
            print(f"  [ОШИБКА] upsert батча {batch_start}–{batch_start + len(batch)} провалился")

    return uploaded


def load_directory(path: str | pathlib.Path) -> None:
    directory = pathlib.Path(path)
    if not directory.is_dir():
        raise NotADirectoryError(f"Не является директорией: {directory}")

    print(f"\nСбор файлов из {directory} ...")
    chunks = _collect_chunks(directory)
    if not chunks:
        print("Нет чанков для загрузки.")
        return

    print(f"\nПолучение эмбеддингов для {len(chunks)} чанков ...")
    points = _embed_chunks(chunks)
    if not points:
        print("Нет точек для загрузки — все батчи провалились.")
        return

    print(f"\nПодключение к Qdrant {config.QDRANT_HOST}:{config.QDRANT_PORT} ...")
    client = _get_client()
    _ensure_collection(client, vector_size=len(points[0].vector))

    print(f"Загрузка {len(points)} точек в '{config.QDRANT_COLLECTION}' ...")
    uploaded = _upsert_points(client, points)

    logger.info("Загрузка завершена: %d/%d точек", uploaded, len(points))
    print(f"\nГотово: загружено {uploaded}/{len(points)} чанков в '{config.QDRANT_COLLECTION}'.")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Загрузка файлов из директории в Qdrant (RAG ingestion)"
    )
    parser.add_argument("--path", required=True, help="Путь к папке с файлами (.pdf/.docx/.xlsx/.txt)")
    args = parser.parse_args()

    load_directory(args.path)
