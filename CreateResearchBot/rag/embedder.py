import config

EMBED_BATCH_SIZE = 100

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"Загрузка локальной модели '{config.LOCAL_EMBED_MODEL}'...")
        _local_model = SentenceTransformer(config.LOCAL_EMBED_MODEL)
    return _local_model


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if config.EMBED_PROVIDER == "local":
        model = _get_local_model()
        results = []
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i : i + EMBED_BATCH_SIZE]
            vectors = model.encode(batch, normalize_embeddings=True).tolist()
            results.extend(vectors)
        return results

    # OpenAI
    import openai
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    results = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i : i + EMBED_BATCH_SIZE]
        response = client.embeddings.create(input=batch, model=config.EMBEDDING_MODEL)
        batch_vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
        results.extend(batch_vectors)
    return results


def get_embedding(text: str) -> list[float]:
    return get_embeddings_batch([text])[0]
