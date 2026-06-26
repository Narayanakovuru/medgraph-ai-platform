from app.core.config import settings
from app.core.qdrant import get_qdrant_client


def main() -> None:
    client = get_qdrant_client()

    collection_info = client.get_collection(
        collection_name=settings.QDRANT_COLLECTION_NAME
    )

    print(f"Collection: {settings.QDRANT_COLLECTION_NAME}")
    print(f"Points count: {collection_info.points_count}")


if __name__ == "__main__":
    main()