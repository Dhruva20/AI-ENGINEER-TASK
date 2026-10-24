import numpy as np


class VectorStore:
    """A tiny in-memory vector database using cosine similarity."""

    def __init__(self):
        self.items: list[dict] = []        # each: {"text", "source", "chunk_id"}
        self.vectors: np.ndarray | None = None

    def add(self, items: list[dict], vectors: np.ndarray) -> None:
        self.items.extend(items)
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])

    def __len__(self) -> int:
        return len(self.items)

    def search(self, query_vector: np.ndarray, top_k: int = 4, min_score: float = 0.45) -> list[dict]:
        """Return the top_k most similar chunks with score >= min_score."""
        if self.vectors is None or len(self.items) == 0:
            return []

        scores = self.vectors @ query_vector          # cosine similarity (vectors are normalised)
        best = np.argsort(scores)[::-1][:top_k]       # indices of highest scores first

        results = []
        for idx in best:
            if scores[idx] >= min_score:
                results.append({**self.items[idx], "score": float(scores[idx])})
        return results