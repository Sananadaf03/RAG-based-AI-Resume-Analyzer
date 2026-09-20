# ============================================================
# modules/retriever.py
# RAG Retriever: Hybrid TF-IDF + Semantic Search
# ============================================================

import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

from modules.embeddings import FAISSVectorStore, embed_texts, embed_single

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retrieval combining:
    1. Dense semantic search (sentence-transformers + FAISS)
    2. Sparse TF-IDF lexical search
    Scores are fused with a configurable alpha weight.
    """

    def __init__(self, alpha: float = 0.6):
        """
        Args:
            alpha: Weight for semantic score (1-alpha = TF-IDF weight).
                   0.6 gives slight preference to semantic understanding.
        """
        self.alpha = alpha
        self.vector_store = FAISSVectorStore()
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            stop_words="english",
        )
        self.tfidf_matrix = None
        self.texts: list[str] = []
        self.metadata: list[dict] = []
        self._is_built = False

    def build_index(self, texts: list[str], metadata: list[dict] = None) -> None:
        """
        Build both the FAISS index and TF-IDF matrix from text chunks.
        """
        if not texts:
            raise ValueError("No texts to index.")

        self.texts = texts
        self.metadata = metadata or [{} for _ in texts]

        logger.info("Building semantic (FAISS) index...")
        self.vector_store.build(texts, self.metadata)

        logger.info("Building TF-IDF sparse index...")
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

        self._is_built = True
        logger.info(f"Retriever ready: {len(texts)} chunks indexed.")

    def retrieve(self, query: str, top_k: int = 8) -> list[dict]:
        """
        Retrieve top-k relevant chunks using hybrid search.

        Returns:
            Sorted list of {text, semantic_score, tfidf_score, hybrid_score, rank, metadata}
        """
        if not self._is_built:
            raise RuntimeError("Retriever not built. Call build_index() first.")

        n = len(self.texts)
        top_k = min(top_k, n)

        # ── 1. Semantic scores (FAISS returns top_k only; we need all for fusion)
        query_vec = embed_single(query)  # shape (1, dim)
        all_vecs = self.vector_store.get_all_embeddings()  # shape (n, dim)
        semantic_scores = np.dot(all_vecs, query_vec[0])  # cosine (normalized)

        # ── 2. TF-IDF lexical scores
        query_tfidf = self.tfidf_vectorizer.transform([query])
        tfidf_scores = sklearn_cosine(query_tfidf, self.tfidf_matrix)[0]

        # ── 3. Normalize both score arrays to [0, 1]
        def normalize(arr):
            mn, mx = arr.min(), arr.max()
            if mx - mn < 1e-9:
                return np.zeros_like(arr)
            return (arr - mn) / (mx - mn)

        sem_norm = normalize(semantic_scores)
        tfidf_norm = normalize(tfidf_scores)

        # ── 4. Hybrid fusion
        hybrid = self.alpha * sem_norm + (1 - self.alpha) * tfidf_norm

        # ── 5. Get top-k indices
        top_indices = np.argsort(hybrid)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                "text": self.texts[idx],
                "semantic_score": float(semantic_scores[idx]),
                "tfidf_score": float(tfidf_scores[idx]),
                "hybrid_score": float(hybrid[idx]),
                "rank": rank + 1,
                "metadata": self.metadata[idx],
                "chunk_index": int(idx),
            })

        return results

    def retrieve_for_jd_sections(
        self, jd_chunks: list[str], top_k_per_chunk: int = 3
    ) -> list[dict]:
        """
        For each JD chunk, retrieve relevant resume chunks.
        Deduplicates and returns merged result set.
        """
        seen_texts = set()
        all_results = []

        for jd_chunk in jd_chunks[:10]:  # Limit to first 10 JD chunks
            results = self.retrieve(jd_chunk, top_k=top_k_per_chunk)
            for r in results:
                if r["text"] not in seen_texts:
                    seen_texts.add(r["text"])
                    all_results.append(r)

        # Re-sort by hybrid score
        all_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return all_results

    def get_overall_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Compute full-document semantic similarity between resume and JD.
        We use a multi-chunk average to be more robust than single-pass.
        """
        # Use up to 3 chunks from each side for a more stable estimate
        def _chunks(text, size=600):
            words = text.split()
            out = []
            for i in range(0, min(len(words), size * 3), size):
                out.append(" ".join(words[i:i+size]))
            return out or [text[:1000]]

        r_chunks = _chunks(resume_text)
        j_chunks = _chunks(jd_text)

        scores = []
        for rc in r_chunks[:3]:
            for jc in j_chunks[:3]:
                try:
                    vecs = embed_texts([rc, jc])
                    scores.append(float(np.dot(vecs[0], vecs[1])))
                except Exception:
                    pass

        if not scores:
            vecs = embed_texts([resume_text[:2000], jd_text[:2000]])
            return float(np.dot(vecs[0], vecs[1]))

        # Return the top-percentile average (more generous than mean, more stable than max)
        arr = np.array(scores)
        top_k = max(1, len(arr) // 2)
        return float(np.sort(arr)[-top_k:].mean())


def build_retriever_from_resume(resume_data: dict, alpha: float = 0.6) -> HybridRetriever:
    """
    Convenience factory: build a retriever from parsed resume data.
    Attaches section metadata to each chunk for richer context.
    """
    chunks = resume_data["chunks"]
    sections = resume_data.get("sections", {})

    # Assign section labels to chunks (rough matching)
    full_text = resume_data["full_text"]
    metadata = []
    for chunk in chunks:
        # Find which section this chunk most likely belongs to
        best_section = "general"
        for sec_name, sec_text in sections.items():
            if chunk[:50] in sec_text or sec_text[:50] in chunk:
                best_section = sec_name
                break
        metadata.append({"section": best_section, "length": len(chunk.split())})

    retriever = HybridRetriever(alpha=alpha)
    retriever.build_index(chunks, metadata)
    return retriever
