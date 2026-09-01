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

Calls Gemini's embedding API (default: text-embedding-004, 768 dims)
behind a small class so the rest of the codebase never touches the
model library directly — swapping embedding models later only means
changing this file + VECTOR_DIM in config/.env.

Previously this wrapped a local sentence-transformers model, but that
pulls in torch at import time -- 300-500MB+ of RAM before a single
request is served, which OOMs a 512Mi Render instance on its own.
Calling the API instead keeps this process's memory footprint small.

Note: Gemini's embed_content takes an explicit task_type instead of
the manual instruction-prefix trick BGE models needed -- pass
RETRIEVAL_DOCUMENT for indexed passages and RETRIEVAL_QUERY for
search queries. Getting it backwards still hurts recall.
"""

from functools import lru_cache

from google import genai
from google.genai import types

from app.core.config import settings

_BATCH_SIZE = 100  # Gemini's embed_content caps requests around this size


class TextEmbedder:
    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._client = genai.Client(api_key=api_key or settings.GEMINI_API_KEY)

    def embed_documents(self, texts: list[str], batch_size: int = _BATCH_SIZE) -> list[list[float]]:
        """Embed passages that will be stored/searched over."""
        if not texts:
            return []
        results: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self._client.models.embed_content(
                model=self.model_name,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT",output_dimensionality=settings.VECTOR_DIM),
            )
            results.extend(embedding.values for embedding in response.embeddings)
        return results

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query."""
        response = self._client.models.embed_content(
            model=self.model_name,
            contents=[query],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY",output_dimensionality=settings.VECTOR_DIM),
        )
        return response.embeddings[0].values


@lru_cache
def get_embedder() -> TextEmbedder:
    """Cached singleton — reuses one API client instead of creating one per call."""
    return TextEmbedder()
