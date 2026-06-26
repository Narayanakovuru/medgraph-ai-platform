from pathlib import Path

from app.core.config import settings
from app.rag.chunking import split_text_into_chunks
from app.rag.indexer import index_chunks


def main() -> None:
    """
    Read the PubMed abstracts file, split it into chunks, and index them in Qdrant.

    The data file path is resolved in this order:
    1. If PUBMED_ABSTRACTS_PATH is absolute, use it as-is.
    2. Otherwise resolve it relative to the *backend* directory (the parent of
       this script's directory) so the script works regardless of the current
       working directory.
    """

    configured_path = Path(settings.PUBMED_ABSTRACTS_PATH)

    if configured_path.is_absolute():
        pubmed_file_path = configured_path
    else:
        # Always resolve relative to the backend/ directory so the script
        # works when launched from any working directory.
        backend_dir = Path(__file__).resolve().parent.parent
        pubmed_file_path = backend_dir / configured_path

    if not pubmed_file_path.exists():
        raise FileNotFoundError(
            f"PubMed abstracts file not found: {pubmed_file_path}\n"
            "Run scripts/pubmed_download.py first, or check PUBMED_ABSTRACTS_PATH in .env."
        )

    print(f"Reading abstracts from: {pubmed_file_path}")
    text = pubmed_file_path.read_text(encoding="utf-8")

    chunks = split_text_into_chunks(
        text=text,
        source="pubmed",
        document_id="diabetes_abstracts",
    )

    print(f"Generated chunks: {len(chunks)}")

    if settings.RAG_INDEX_LIMIT > 0:
        chunks = chunks[: settings.RAG_INDEX_LIMIT]
        print(f"Indexing limited to {len(chunks)} chunks (RAG_INDEX_LIMIT={settings.RAG_INDEX_LIMIT})")
    else:
        print("Indexing all chunks (RAG_INDEX_LIMIT=0 means unlimited).")

    indexed_count = index_chunks(chunks)

    print(f"Indexed {indexed_count} chunks into Qdrant.")
    print("PubMed chunk indexing completed successfully.")


if __name__ == "__main__":
    main()