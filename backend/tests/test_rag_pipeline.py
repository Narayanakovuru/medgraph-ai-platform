from app.rag.chunking import split_text_into_chunks


def test_split_text_into_chunks_returns_chunks():
    text = (
        "PPARG activation is associated with improved insulin sensitivity "
        "in type 2 diabetes. "
    ) * 50

    chunks = split_text_into_chunks(
        text=text,
        source="test",
        document_id="sample_doc",
    )

    assert len(chunks) > 0
    assert chunks[0].source == "test"
    assert chunks[0].document_id == "sample_doc"
    assert chunks[0].text