"""Hybrid retriever: combines semantic similarity with light keyword filtering."""
from __future__ import annotations

from typing import Dict, List, Tuple

from app.models.schemas import Candidate, ParsedJD
from app.services.embeddings import EmbeddingStore


def _jd_query_text(jd: ParsedJD) -> str:
    return (
        f"{jd.role_title}. Seniority: {jd.seniority}. "
        f"Skills: {', '.join(jd.must_have_skills + jd.nice_to_have_skills)}. "
        f"Domains: {', '.join(jd.domains)}. "
        f"Experience: {jd.min_years_experience}-{jd.max_years_experience} years."
    )


def retrieve(
    jd: ParsedJD,
    store: EmbeddingStore,
    longlist_size: int = 25,
) -> List[Tuple[Candidate, float]]:
    """Return a longlist of (candidate, semantic_score_pct) ordered by similarity."""
    query = _jd_query_text(jd)
    semantic_results = store.search(query, k=min(longlist_size, len(store.candidates)))

    scored: Dict[str, Tuple[Candidate, float]] = {}
    for cand, sim in semantic_results:
        pct = round(sim * 100.0, 2)
        scored[cand.id] = (cand, pct)

    return list(scored.values())
