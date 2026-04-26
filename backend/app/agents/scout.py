"""Talent Scouting Agent — orchestrates JD parsing, retrieval, scoring & explanation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.models.schemas import (
    Candidate,
    MatchedCandidate,
    ParsedJD,
    ScoutResponse,
)
from app.services.embeddings import EmbeddingStore
from app.services.jd_parser import parse_jd
from app.services.llm import LLMService
from app.services.matcher import score_candidate
from app.services.retriever import retrieve


_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "candidates.json"


def _load_candidates() -> List[Candidate]:
    raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    return [Candidate(**c) for c in raw]


class TalentScoutAgent:
    """Single agent that turns raw JD text into a ranked, explainable shortlist."""

    def __init__(self) -> None:
        self.llm = LLMService()
        self.candidates: List[Candidate] = _load_candidates()
        self.store = EmbeddingStore(self.candidates)

    def scout(self, jd_text: str, top_k: int = 10) -> ScoutResponse:
        parsed: ParsedJD = parse_jd(jd_text, self.llm)
        longlist = retrieve(parsed, self.store, longlist_size=min(25, len(self.candidates)))

        matches: List[MatchedCandidate] = []
        for cand, semantic_pct in longlist:
            matches.append(score_candidate(parsed, cand, semantic_pct, self.llm))

        matches.sort(key=lambda m: m.match_score, reverse=True)
        top_matches = matches[:top_k]

        return ScoutResponse(
            parsed_jd=parsed,
            matches=top_matches,
            total_candidates_considered=len(self.candidates),
            llm_mode=self.llm.mode,
        )
