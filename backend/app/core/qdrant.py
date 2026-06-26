from qdrant_client import QdrantClient

from app.core.config import settings


def get_qdrant_client() -> QdrantClient:
    """
    Return a configured Qdrant client.

    Supports two modes controlled by the QDRANT_MODE setting:

    - ``cloud``  – connects to Qdrant Cloud using QDRANT_URL + QDRANT_API_KEY.
    - ``local``  – connects to a self-hosted instance using QDRANT_HOST + QDRANT_PORT.
    """

    mode = settings.QDRANT_MODE.lower()

    if mode == "cloud":
        return QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

    if mode == "local":
        host = settings.QDRANT_HOST or "localhost"
        port = settings.QDRANT_PORT or 6333
        return QdrantClient(host=host, port=port)

    raise ValueError(
        f"Unknown QDRANT_MODE '{settings.QDRANT_MODE}'. "
        "Must be 'cloud' or 'local'."
    )
