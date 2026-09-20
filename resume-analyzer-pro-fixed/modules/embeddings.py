# ============================================================
# modules/embeddings.py
# Embedding Engine: sentence-transformers + FAISS Vector Store
# ============================================================

import numpy as np
import faiss
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Lazy-load the model (avoid re-loading on each run)
# ─────────────────────────────────────────────
_model = None
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast, offline, 384-dim, ~22MB


def get_embedding_model():
    """
    Singleton loader for the SentenceTransformer model.
    Downloads on first use, then cached locally by the library.
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(
                f"Could not load SentenceTransformer model '{MODEL_NAME}'. "
                "Run: pip install sentence-transformers"
            )
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Encode a list of text strings into dense embedding vectors.

    Args:
        texts: List of strings to embed
        batch_size: Number of texts to encode at once

    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    if not texts:
        raise ValueError("Cannot embed empty list of texts.")

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,  # L2 normalize for cosine similarity via dot product
        convert_to_numpy=True,
    )
    return embeddings.astype(np.float32)


def embed_single(text: str) -> np.ndarray:
    """
    Embed a single string. Returns shape (1, dim).
    """
    return embed_texts([text])


# ─────────────────────────────────────────────
# FAISS Vector Store
# ─────────────────────────────────────────────

class FAISSVectorStore:
    """
    In-memory FAISS vector store for semantic search.
    Uses Inner Product (IP) which equals cosine similarity
    when vectors are L2-normalized.
    """

    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.texts: list[str] = []
        self.metadata: list[dict] = []
        self.dim: int = 384  # default for all-MiniLM-L6-v2

    def build(self, texts: list[str], metadata: list[dict] = None) -> None:
        """
        Build the FAISS index from a list of text chunks.

        Args:
            texts: Text chunks to index
            metadata: Optional metadata dicts per chunk
        """
        if not texts:
            raise ValueError("No texts provided to build the vector store.")

        logger.info(f"Building FAISS index for {len(texts)} chunks...")
        embeddings = embed_texts(texts)
        self.dim = embeddings.shape[1]

        # Flat index with Inner Product (cosine on normalized vecs)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(embeddings)

        self.texts = texts
        self.metadata = metadata or [{} for _ in texts]
        logger.info(f"FAISS index built: {self.index.ntotal} vectors, dim={self.dim}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve top-k most similar chunks for a query string.

        Returns:
            List of dicts: {text, score, metadata, rank}
        """
        if self.index is None or self.index.ntotal == 0:
            raise RuntimeError("Vector store is empty. Call build() first.")

        query_vec = embed_single(query)
        top_k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue
            results.append({
                "text": self.texts[idx],
                "score": float(score),
                "metadata": self.metadata[idx],
                "rank": rank + 1,
            })

        return results

    def batch_search(self, queries: list[str], top_k: int = 3) -> list[list[dict]]:
        """
        Run multiple queries at once (more efficient than looping).
        """
        if self.index is None:
            raise RuntimeError("Vector store is empty. Call build() first.")

        query_vecs = embed_texts(queries)
        top_k = min(top_k, self.index.ntotal)

        scores_batch, indices_batch = self.index.search(query_vecs, top_k)

        all_results = []
        for q_scores, q_indices in zip(scores_batch, indices_batch):
            results = []
            for rank, (score, idx) in enumerate(zip(q_scores, q_indices)):
                if idx == -1:
                    continue
                results.append({
                    "text": self.texts[idx],
                    "score": float(score),
                    "metadata": self.metadata[idx],
                    "rank": rank + 1,
                })
            all_results.append(results)

        return all_results

    def get_all_embeddings(self) -> np.ndarray:
        """Return all stored embeddings as numpy array."""
        if self.index is None:
            return np.array([])
        # Reconstruct from flat index
        n = self.index.ntotal
        vecs = np.zeros((n, self.dim), dtype=np.float32)
        self.index.reconstruct_n(0, n, vecs)
        return vecs

    def __len__(self):
        return self.index.ntotal if self.index else 0


def cosine_similarity_texts(text_a: str, text_b: str) -> float:
    """
    Compute cosine similarity between two text strings.
    (Embeddings are already L2-normalized, so dot product = cosine sim)
    """
    vecs = embed_texts([text_a, text_b])
    return float(np.dot(vecs[0], vecs[1]))


def cosine_similarity_bulk(
    query_embedding: np.ndarray,
    corpus_embeddings: np.ndarray
) -> np.ndarray:
    """
    Compute cosine similarity of one query against many corpus vectors.
    Both must be L2-normalized.
    """
    return np.dot(corpus_embeddings, query_embedding)
