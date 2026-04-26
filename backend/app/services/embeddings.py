"""TF-IDF based semantic retrieval over candidate profiles.

Uses scikit-learn's TfidfVectorizer + cosine similarity. Lightweight and
dependency-free of heavy ML stacks (no PyTorch / sentence-transformers).
For our candidate pool size this gives excellent retrieval quality.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.schemas import Candidate


def _candidate_to_text(c: Candidate) -> str:
    """Flatten a candidate into a single retrieval document.

    Skills are repeated to give them more TF weight than narrative text.
    """
    skills_repeated = " ".join(c.skills * 3)
    domains_repeated = " ".join(c.domains * 2)
    return " ".join(
        [
            c.title,
            c.title,
            f"{c.years_experience} years experience",
            c.location,
            skills_repeated,
            domains_repeated,
            c.summary,
        ]
    )


class EmbeddingStore:
    """TF-IDF vector store over candidate profiles."""

    def __init__(self, candidates: List[Candidate]) -> None:
        self.candidates = candidates
        texts = [_candidate_to_text(c) for c in candidates]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            token_pattern=r"(?u)\b[\w+#\.]+\b",
        )
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str, k: int) -> List[Tuple[Candidate, float]]:
        """Return top-k (candidate, similarity in [0,1]) tuples."""
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        k = min(k, len(self.candidates))
        idxs = np.argsort(-sims)[:k]
        return [(self.candidates[int(i)], float(max(0.0, min(1.0, sims[i])))) for i in idxs]
