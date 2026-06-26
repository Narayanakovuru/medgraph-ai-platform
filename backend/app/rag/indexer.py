from typing import Iterable, List
from uuid import NAMESPACE_URL, uuid5

from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.rag.chunking import TextChunk
from app.rag.embeddings import get_embedder


DISTANCE_MAP = {
    "COSINE": Distance.COSINE,
    "DOT": Distance.DOT,
    "EUCLID": Distance.EUCLID,
}


def _stable_uuid(value: str) -> str:
    """
    Create a stable UUID from a string.

    Same chunk_id always creates the same UUID.
    This prevents duplicate points when re-running indexing.
    """

    return str(uuid5(NAMESPACE_URL, value))


def _batch_items(items: List[TextChunk], batch_size: int) -> Iterable[List[TextChunk]]:
    """
    Yield chunks in batches to avoid high memory usage.
    """

    for index in range(0, len(items), batch_size):
        yield items[index:index + batch_size]


def ensure_collection_exists() -> None:
    """
    Create Qdrant collection if it does not exist.
    """

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    existing_collections = client.get_collections().collections
    existing_names = {collection.name for collection in existing_collections}

    if collection_name in existing_names:
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=settings.QDRANT_VECTOR_SIZE,
            distance=DISTANCE_MAP[settings.QDRANT_DISTANCE],
        ),
    )


def index_chunks(chunks: List[TextChunk]) -> int:
    """
    Convert chunks into embeddings and upsert them into Qdrant.
    """

    if not chunks:
        return 0

    ensure_collection_exists()

    client = get_qdrant_client()
    embedder = get_embedder()

    indexed_count = 0

    for batch in _batch_items(chunks, settings.RAG_BATCH_SIZE):
        texts = [chunk.text for chunk in batch]
        vectors = embedder.embed_texts(texts)

        points = [
            PointStruct(
                id=_stable_uuid(chunk.chunk_id),
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(batch, vectors)
        ]

        client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points,
        )

        indexed_count += len(points)

    return indexed_count