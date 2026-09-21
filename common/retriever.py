"""TF-IDF based retriever shared by all three RAG pipelines.

Using TF-IDF (instead of a downloaded neural embedding model) keeps every
pipeline runnable offline with no model download and no API key, while still
giving a real retrieval step over the corpus.
"""
from dataclasses import dataclass
from typing import List, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float


class TfidfRetriever:
    def __init__(self):
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = None
        self._chunks: List[str] = []
        self._sources: List[str] = []

    def fit(self, chunks: Sequence[str], sources: Sequence[str]):
        if len(chunks) != len(sources):
            raise ValueError("chunks and sources must be the same length")
        self._chunks = list(chunks)
        self._sources = list(sources)
        self._matrix = self._vectorizer.fit_transform(self._chunks)
        return self

    def query(self, question: str, top_k: int = 3) -> List[RetrievedChunk]:
        if self._matrix is None:
            raise RuntimeError("Retriever has not been fit on any documents yet")

        query_vec = self._vectorizer.transform([question])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for i in ranked[:top_k]:
            if scores[i] <= 0:
                continue
            results.append(RetrievedChunk(
                text=self._chunks[i],
                source=self._sources[i],
                score=float(scores[i]),
            ))
        return results
