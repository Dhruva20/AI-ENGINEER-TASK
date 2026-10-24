import os
import time

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

BATCH_SIZE = 20          # chunks per API request (smaller = gentler on token limits)
BATCH_PAUSE = 1.5        # seconds to wait between batches
MAX_RETRIES = 5


class EmbeddingError(Exception):
    """Raised with a friendly message when embedding fails."""


def _embed(texts: list[str], task_type: str) -> np.ndarray:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise EmbeddingError("API key not found. Add API_KEY=... to your .env file.")

    model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    client = genai.Client(api_key=api_key)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = client.models.embed_content(
                model=model,
                contents=texts,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            vectors = np.array([e.values for e in result.embeddings], dtype=np.float32)
            break
        except Exception as e:
            msg = str(e).lower()
            rate_limited = any(k in msg for k in ("429", "quota", "resource_exhausted"))
            busy = any(k in msg for k in ("503", "unavailable", "timeout"))

            if (rate_limited or busy) and attempt < MAX_RETRIES:
                # rate limits reset per minute, so wait much longer than for a 503
                time.sleep(15 * attempt if rate_limited else 2 * attempt)
                continue
            if "404" in msg or "not_found" in msg:
                raise EmbeddingError(f"Embedding model '{model}' not found. Check EMBEDDING_MODEL in .env.")
            if any(k in msg for k in ("api key", "401", "403", "permission")):
                raise EmbeddingError("Your API key looks invalid. Check the .env file.")
            if rate_limited:
                raise EmbeddingError(
                    "Rate or daily quota reached. Wait a few minutes, or try a smaller document."
                )
            if busy:
                raise EmbeddingError("The embedding service is busy. Try again in a minute.")
            raise EmbeddingError(f"Embedding failed: {e}")

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


def embed_documents(chunks: list[str], on_progress=None) -> np.ndarray:
    """Embed many chunks in small batches. on_progress(done, total) is called after each batch."""
    parts = []
    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        parts.append(_embed(chunks[i : i + BATCH_SIZE], "RETRIEVAL_DOCUMENT"))
        if on_progress:
            on_progress(min(i + BATCH_SIZE, total), total)
        time.sleep(BATCH_PAUSE)
    return np.vstack(parts)


def embed_query(question: str) -> np.ndarray:
    """Embed one question. Returns a 1-D vector."""
    return _embed([question], "RETRIEVAL_QUERY")[0]