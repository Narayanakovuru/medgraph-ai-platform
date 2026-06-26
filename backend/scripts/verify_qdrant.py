from qdrant_client.models import Distance, VectorParams

from app.core.config import settings
from app.core.qdrant import get_qdrant_client


DISTANCE_MAP = {
    "COSINE": Distance.COSINE,
    "DOT": Distance.DOT,
    "EUCLID": Distance.EUCLID,
}


def main() -> None:
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    existing_collections = client.get_collections().collections
    existing_names = {collection.name for collection in existing_collections}

    if collection_name in existing_names:
        print(f"Collection already exists: {collection_name}")
    else:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=DISTANCE_MAP[settings.QDRANT_DISTANCE],
            ),
        )
        print(f"Collection created: {collection_name}")

    print("Qdrant setup completed successfully.")


if __name__ == "__main__":
    main()