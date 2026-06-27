from typing import Any, List

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.rag.embeddings import get_embedder


def retrieve_relevant_chunks(query: str, limit: int = 5) -> List[dict[str, Any]]:
    """
    Retrieve semantically relevant chunks from Qdrant for a user query.

    Uses client.query_points() which is the current API in qdrant-client >= 1.13.
    (client.search() was removed in v1.13.)
    """

    if not query.strip():
        return []

    client = get_qdrant_client()
    embedder = get_embedder()

    query_vector = embedder.embed_text(query)

    # Make it compatible with both older and newer qdrant-client versions
    if hasattr(client, "query_points"):
        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )
        hits = response.points
    else:
        hits = client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
        )

    return [
        {
            "score": point.score,
            "payload": point.payload,
        }
        for point in hits
    ]