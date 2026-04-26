"""Pydantic schemas for the Talent Scouting Agent."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    name: str
    title: str
    years_experience: int
    location: str
    work_mode: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    summary: str
    current_company: Optional[str] = None
    linkedin: Optional[str] = None


class ParsedJD(BaseModel):
    """Structured representation extracted from a free-text Job Description."""

    role_title: str
    seniority: str = Field(
        description="One of: junior, mid, senior, lead, principal, manager, director"
    )
    min_years_experience: int = 0
    max_years_experience: int = 30
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    work_mode: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    raw_jd: str


class ScoreBreakdown(BaseModel):
    skills_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    domain_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    semantic_score: float = Field(ge=0, le=100)


class MatchedCandidate(BaseModel):
    candidate: Candidate
    match_score: float = Field(ge=0, le=100)
    breakdown: ScoreBreakdown
    matched_must_have: List[str] = Field(default_factory=list)
    missing_must_have: List[str] = Field(default_factory=list)
    matched_nice_to_have: List[str] = Field(default_factory=list)
    explanation: str


class ScoutRequest(BaseModel):
    jd_text: str = Field(min_length=20, description="Raw job description text")
    top_k: int = Field(default=10, ge=1, le=30)


class ScoutResponse(BaseModel):
    parsed_jd: ParsedJD
    matches: List[MatchedCandidate]
    total_candidates_considered: int
    llm_mode: str = Field(description="'gemini' or 'heuristic'")
