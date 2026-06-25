from functools import lru_cache
from typing import Iterable, List

import torch
import torch.nn.functional as F
from transformers import BertModel, BertTokenizer

from app.core.config import settings


def _resolve_device() -> torch.device:
    """
    Resolve embedding device.

    EMBEDDING_DEVICE options:
    - auto: use CUDA if available, otherwise CPU
    - cpu: force CPU
    - cuda: force GPU
    """

    configured_device = settings.EMBEDDING_DEVICE.lower()

    if configured_device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if configured_device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("EMBEDDING_DEVICE=cuda but CUDA is not available.")

    return torch.device(configured_device)


class BioBERTEmbedder:
    """
    BioBERT-based text embedding service.

    Converts biomedical text into dense vectors for Qdrant.
    """

    def __init__(self) -> None:
        self.device = _resolve_device()

        self.tokenizer = BertTokenizer.from_pretrained(
            settings.EMBEDDING_MODEL_NAME
        )

        self.model = BertModel.from_pretrained(
            settings.EMBEDDING_MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single text into one embedding vector.
        """

        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: Iterable[str]) -> List[list[float]]:
        """
        Convert multiple texts into embedding vectors.

        Uses mean pooling over token embeddings.
        """

        clean_texts = [text.strip() for text in texts if text and text.strip()]

        if not clean_texts:
            return []

        encoded_input = self.tokenizer(
            clean_texts,
            padding=True,
            truncation=True,
            max_length=settings.EMBEDDING_MAX_LENGTH,
            return_tensors="pt",
        )

        encoded_input = {
            key: value.to(self.device)
            for key, value in encoded_input.items()
        }

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input["attention_mask"]

        sentence_embeddings = self._mean_pooling(
            token_embeddings=token_embeddings,
            attention_mask=attention_mask,
        )

        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings.cpu().tolist()

    @staticmethod
    def _mean_pooling(
        token_embeddings: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Mean pooling converts token-level embeddings into one text-level embedding.

        BioBERT returns vectors for each token.
        Qdrant needs one vector for each text/chunk.
        """

        input_mask_expanded = (
            attention_mask
            .unsqueeze(-1)
            .expand(token_embeddings.size())
            .float()
        )

        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)

        sum_mask = torch.clamp(
            input_mask_expanded.sum(dim=1),
            min=1e-9,
        )

        return sum_embeddings / sum_mask


@lru_cache
def get_embedder() -> BioBERTEmbedder:
    """
    Return cached BioBERT embedder.

    Loading BioBERT is expensive, so we load it once and reuse it.
    """

    return BioBERTEmbedder()