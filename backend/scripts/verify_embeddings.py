from app.rag.embeddings import get_embedder


def main() -> None:
    embedder = get_embedder()

    sample_text = (
        "PPARG activation is associated with improved insulin sensitivity "
        "in type 2 diabetes."
    )

    embedding = embedder.embed_text(sample_text)

    print("Embedding generated successfully.")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")


if __name__ == "__main__":
    main()