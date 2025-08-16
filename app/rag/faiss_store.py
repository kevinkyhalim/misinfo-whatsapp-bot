# app/rag/faiss_store.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

@dataclass
class RetrievalHit:
    score: float
    id: str
    title: str
    url: str
    text: str

class FaissRetriever:
    """
    Lightweight FAISS wrapper. Loads a local FAISS index + metadata arrays produced
    by build_faiss_index.py and provides a .search(claim, k) method.
    """
    def __init__(self,
                 index_path: str = "data/faiss.index",
                 meta_path: str = "data/meta.npy",
                 texts_path: str = "data/texts.npy",
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL) -> None:
        self.index_path = index_path
        self.meta_path = meta_path
        self.texts_path = texts_path

        if not (os.path.exists(index_path) and os.path.exists(meta_path) and os.path.exists(texts_path)):
            raise FileNotFoundError(
                f"Missing FAISS artifacts. Expected {index_path}, {meta_path}, {texts_path}."
            )

        self.model = SentenceTransformer(embedding_model)
        self.index = faiss.read_index(index_path)
        # allow_pickle=True because we stored dict objects (id/title/url)
        self.meta = np.load(meta_path, allow_pickle=True)
        self.texts = np.load(texts_path, allow_pickle=True)

    def embed(self, text: str) -> np.ndarray:
        emb = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return emb.astype("float32")

    def search(self, query: str, k: int = 5, min_score: float = 0.3) -> List[RetrievalHit]:
        q = self.embed(query)
        D, I = self.index.search(q, k)
        hits: List[RetrievalHit] = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            s = float(score)
            if s < min_score:
                continue
            m: Dict[str, Any] = self.meta[idx].items() if isinstance(self.meta[idx], np.ndarray) else self.meta[idx]
            t: str = str(self.texts[idx])
            hits.append(RetrievalHit(score=s, id=m["id"], title=m["title"], url=m["url"], text=t))
        return hits

# Singleton-ish loader (so we only load model/index once in the process)
_retriever_singleton: FaissRetriever | None = None

def get_faiss_retriever() -> FaissRetriever:
    global _retriever_singleton
    if _retriever_singleton is None:
        index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss.index")
        meta_path = os.getenv("FAISS_META_PATH", "data/meta.npy")
        texts_path = os.getenv("FAISS_TEXTS_PATH", "data/texts.npy")
        _retriever_singleton = FaissRetriever(index_path, meta_path, texts_path)
    return _retriever_singleton