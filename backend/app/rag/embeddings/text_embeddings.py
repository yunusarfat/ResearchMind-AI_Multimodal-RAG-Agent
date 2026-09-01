# """
# Text embedding wrapper.

# Wraps a sentence-transformers model (default: BAAI/bge-base-en-v1.5,
# 768 dims) behind a small class so the rest of the codebase never
# touches the model library directly — swapping embedding models later
# only means changing this file + VECTOR_DIM in config/.env.

# Note: BGE models expect a query-side instruction prefix for retrieval
# tasks ("Represent this sentence for searching relevant passages: ")
# but NOT for the documents being indexed. This matters for retrieval
# quality — get it backwards and recall drops noticeably.
# """

# from functools import lru_cache

# import numpy as np
# from sentence_transformers import SentenceTransformer

# from app.core.config import settings

# _BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


# class TextEmbedder:
#     def __init__(self, model_name: str | None = None, device: str | None = None):
#         self.model_name = model_name or settings.EMBEDDING_MODEL
#         self.device = device or settings.DEVICE
#         self._model = SentenceTransformer(self.model_name, device=self.device)

#     def embed_documents(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
#         """Embed passages that will be stored/searched over (no instruction prefix)."""
#         if not texts:
#             return []
#         embeddings = self._model.encode(
#             texts,
#             batch_size=batch_size,
#             normalize_embeddings=True,  # so cosine distance == dot product
#             show_progress_bar=False,
#         )
#         return np.asarray(embeddings).tolist()

#     def embed_query(self, query: str) -> list[float]:
#         """Embed a search query (BGE-style instruction prefix improves retrieval)."""
#         prefixed = _BGE_QUERY_INSTRUCTION + query
#         embedding = self._model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
#         return np.asarray(embedding).tolist()


# @lru_cache
# def get_embedder() -> TextEmbedder:
#     """Cached singleton — loading the model is expensive, do it once."""
#     return TextEmbedder()




"""
Text embedding wrapper.

Wraps a sentence-transformers model (default: BAAI/bge-base-en-v1.5,
768 dims) behind a small class so the rest of the codebase never
touches the model library directly — swapping embedding models later
only means changing this file + VECTOR_DIM in config/.env.

Note: BGE models expect a query-side instruction prefix for retrieval
tasks ("Represent this sentence for searching relevant passages: ")
but NOT for the documents being indexed. This matters for retrieval
quality — get it backwards and recall drops noticeably.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

_BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class TextEmbedder:
    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.DEVICE
        self._model = SentenceTransformer(self.model_name, device=self.device)

    def embed_documents(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Embed passages that will be stored/searched over (no instruction prefix)."""
        if not texts:
            return []
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,  # so cosine distance == dot product
            show_progress_bar=False,
        )
        return np.asarray(embeddings).tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query (BGE-style instruction prefix improves retrieval)."""
        prefixed = _BGE_QUERY_INSTRUCTION + query
        embedding = self._model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embedding).tolist()


@lru_cache
def get_embedder() -> TextEmbedder:
    """Cached singleton — loading the model is expensive, do it once."""
    return TextEmbedder()
