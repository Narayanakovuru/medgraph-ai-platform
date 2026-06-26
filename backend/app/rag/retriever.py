from typing import Any, List

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.rag.embeddings import get_embedder


def retrieve_relevant_chunks(query: str, limit: int = 5) -> List[dict[str, Any]]:
    """
    Retrieve semantically relevant chunks from Qdrant for a user query.
    """

    if not query.strip():
        return []

    client = get_qdrant_client()
    embedder = get_embedder()

    query_vector = embedder.embed_text(query)

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "score": result.score,
            "payload": result.payload,
        }
        for result in results
    ]