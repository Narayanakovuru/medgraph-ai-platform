import sys
from app.core.qdrant import get_qdrant_client
from qdrant_client.http.exceptions import UnexpectedResponse

def verify_connection():
    print("Connecting to Qdrant Cloud...")
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        print(f"Successfully connected to Qdrant!")
        print(f"Collections found: {len(collections.collections)}")
        for collection in collections.collections:
            print(f"- {collection.name}")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_connection()
