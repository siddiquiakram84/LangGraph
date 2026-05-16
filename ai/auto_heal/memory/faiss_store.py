"""
memory/faiss_store.py

FAISS-backed vector store for the auto-gen RAG pipeline.

Used for retrieving similar past scripts and page objects during
test case generation. Runs fully local — no API cost, no network call.

ChromaDB (healing_memory) handles the self-healing side.
FAISS handles the script generation side.

Interview talking point:
  "I split the vector store by concern. ChromaDB for healing events
  because it persists metadata well. FAISS for script retrieval because
  it is faster at similarity search over large corpora and runs in-process."
"""
import os
import json
import pickle
import numpy as np
import faiss
from ai.auto_heal.embedding.embedding_engine import EmbeddingEngine

FAISS_INDEX_PATH = "ai/memory/faiss_script_index.bin"
FAISS_META_PATH  = "ai/memory/faiss_script_meta.pkl"

engine = EmbeddingEngine()
DIMENSION = 384  # all-MiniLM-L6-v2 output dimension


class FAISSScriptStore:
    """
    Stores generated Playwright/pytest scripts as embeddings.
    On retrieval, returns the top-k most similar scripts as RAG context
    for the script generator agent.
    """

    def __init__(self):
        os.makedirs("ai/memory", exist_ok=True)
        self.index = self._load_or_create_index()
        self.metadata: list[dict] = self._load_metadata()

    def _load_or_create_index(self) -> faiss.IndexFlatIP:
        if os.path.exists(FAISS_INDEX_PATH):
            return faiss.read_index(FAISS_INDEX_PATH)
        return faiss.IndexFlatIP(DIMENSION)  # Inner product = cosine on normalised vecs

    def _load_metadata(self) -> list:
        if os.path.exists(FAISS_META_PATH):
            with open(FAISS_META_PATH, "rb") as f:
                return pickle.load(f)
        return []

    def _save(self):
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def _normalize(self, vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def add(self, test_description: str, script: str, script_type: str = "ui"):
        """
        Store a generated script with its test description as the key.
        script_type: 'ui' (Playwright) or 'api' (pytest+requests)
        """
        vec = self._normalize(engine.embed(test_description)).astype("float32")
        self.index.add(np.array([vec]))
        self.metadata.append({
            "description": test_description,
            "script": script,
            "type": script_type,
        })
        self._save()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Return top_k most similar past scripts for RAG context injection.
        Returns empty list if store is empty.
        """
        if self.index.ntotal == 0:
            return []

        vec = self._normalize(engine.embed(query)).astype("float32")
        scores, indices = self.index.search(np.array([vec]), min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx].copy()
            meta["similarity_score"] = float(score)
            results.append(meta)

        return results

    def count(self) -> int:
        return self.index.ntotal
