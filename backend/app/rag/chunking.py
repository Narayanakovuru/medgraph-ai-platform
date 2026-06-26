from dataclasses import dataclass
from typing import List

from app.core.config import settings


@dataclass(frozen=True)
class TextChunk:
    """
    Represents one text chunk prepared for embedding and indexing.
    """

    chunk_id: str
    text: str
    source: str
    document_id: str
    chunk_index: int


def split_text_into_chunks(
    text: str,
    source: str,
    document_id: str,
) -> List[TextChunk]:
    """
    Split a large document into smaller overlapping chunks.
    """

    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    chunk_size = settings.RAG_CHUNK_SIZE
    chunk_overlap = settings.RAG_CHUNK_OVERLAP

    if chunk_overlap >= chunk_size:
        raise ValueError("RAG_CHUNK_OVERLAP must be smaller than RAG_CHUNK_SIZE.")

    chunks: List[TextChunk] = []
    start = 0
    chunk_index = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk_text = cleaned_text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_id=f"{source}_{document_id}_chunk_{chunk_index}",
                    text=chunk_text,
                    source=source,
                    document_id=document_id,
                    chunk_index=chunk_index,
                )
            )

        start += chunk_size - chunk_overlap
        chunk_index += 1

    return chunks