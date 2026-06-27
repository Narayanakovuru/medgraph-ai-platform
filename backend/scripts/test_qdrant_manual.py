"""
Manual Qdrant Inspection & Test Script
=======================================
Run from the backend/ directory:

    python -m scripts.test_qdrant_manual

What this script does:
 1. Connects to your Qdrant Cloud instance
 2. Lists all collections in the database
 3. Shows collection stats  (vector size, distance, point count)
 4. Fetches 3 real stored points so you can see the raw payload
 5. Performs a live semantic search with a biomedical query
 6. Prints a similarity score + matching text for every result
"""

import sys

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.rag.embeddings import get_embedder


# ─── 1. Connect ────────────────────────────────────────────────────────────────

def step1_connect():
    print("\n" + "=" * 60)
    print("STEP 1 - Connecting to Qdrant")
    print("=" * 60)
    print(f"  Mode      : {settings.QDRANT_MODE}")
    print(f"  URL       : {settings.QDRANT_URL}")
    print(f"  Collection: {settings.QDRANT_COLLECTION_NAME}")

    client = get_qdrant_client()
    print("  [OK]  Connected successfully!")
    return client


# ─── 2. List all collections ───────────────────────────────────────────────────

def step2_list_collections(client):
    print("\n" + "=" * 60)
    print("STEP 2 - All Collections in Qdrant")
    print("=" * 60)

    response = client.get_collections()
    collections = response.collections

    if not collections:
        print("  [!] No collections found! Have you run the indexing script yet?")
        sys.exit(1)

    for col in collections:
        print(f"  * {col.name}")

    return collections


# ─── 3. Collection stats ───────────────────────────────────────────────────────

def step3_collection_stats(client):
    print("\n" + "=" * 60)
    print("STEP 3 - Collection Stats")
    print("=" * 60)

    col_name = settings.QDRANT_COLLECTION_NAME
    info = client.get_collection(collection_name=col_name)

    print(f"  Collection name : {col_name}")
    print(f"  Points count    : {info.points_count}")
    print(f"  Vector size     : {info.config.params.vectors.size}")
    print(f"  Distance metric : {info.config.params.vectors.distance}")
    print(f"  Status          : {info.status}")

    if info.points_count == 0:
        print("\n  [!] Collection is EMPTY. Run scripts/index_pubmed_chunks.py first.")
        sys.exit(1)

    return info


# ─── 4. Peek at real stored points ─────────────────────────────────────────────

def step4_peek_real_points(client, peek_count: int = 3):
    print("\n" + "=" * 60)
    print(f"STEP 4 - Peeking at {peek_count} Real Stored Points (with payload)")
    print("=" * 60)

    col_name = settings.QDRANT_COLLECTION_NAME

    # scroll() lets us browse points without a query vector
    results, _next_page = client.scroll(
        collection_name=col_name,
        limit=peek_count,
        with_payload=True,
        with_vectors=False,   # skip the 768-dim vector to keep output readable
    )

    for i, point in enumerate(results, 1):
        payload = point.payload or {}
        print(f"\n  -- Point #{i} --")
        print(f"    ID          : {point.id}")
        print(f"    chunk_id    : {payload.get('chunk_id', 'N/A')}")
        print(f"    source      : {payload.get('source', 'N/A')}")
        print(f"    document_id : {payload.get('document_id', 'N/A')}")
        print(f"    chunk_index : {payload.get('chunk_index', 'N/A')}")
        text_preview = payload.get("text", "")[:200].replace("\n", " ")
        print(f"    text preview: \"{text_preview}...\"")

    return results


# ─── 5. Live semantic search ───────────────────────────────────────────────────

def step5_semantic_search(client, query: str, limit: int = 5):
    print("\n" + "=" * 60)
    print("STEP 5 - Live Semantic Search")
    print("=" * 60)
    print(f"  Query : \"{query}\"")
    print(f"  Top-K : {limit}")
    print("\n  Loading BioBERT embedder (first time is slow - ~30 sec)...")

    embedder = get_embedder()
    query_vector = embedder.embed_text(query)

    print(f"  Query vector dimension: {len(query_vector)}")
    print("  Searching Qdrant...")

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    hits = results.points
    print(f"\n  Found {len(hits)} results:\n")

    for rank, hit in enumerate(hits, 1):
        payload = hit.payload or {}
        text_preview = payload.get("text", "")[:300].replace("\n", " ")
        print(f"  Rank #{rank}  |  Score: {hit.score:.4f}")
        print(f"    source      : {payload.get('source')}")
        print(f"    chunk_index : {payload.get('chunk_index')}")
        print(f"    text        : \"{text_preview}...\"")
        print()

    return results


# ─── main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=== MedGraph - Manual Qdrant Test ===" + "\n")

    client = step1_connect()
    step2_list_collections(client)
    step3_collection_stats(client)
    step4_peek_real_points(client, peek_count=3)

    # Change this query to anything you like!
    test_query = "insulin resistance and type 2 diabetes gene expression"
    step5_semantic_search(client, query=test_query, limit=5)

    print("\n" + "=" * 60)
    print("[OK] All tests passed. Data IS in Qdrant and retrieval works!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
