"""Candidate matcher: deterministic scoring across multiple dimensions, plus
LLM-augmented natural language explanations (with templated fallback)."""
from __future__ import annotations

from typing import List, Tuple

from app.models.schemas import (
    Candidate,
    MatchedCandidate,
    ParsedJD,
    ScoreBreakdown,
)
from app.services.llm import LLMService


_SENIORITY_RANGES = {
    "junior": (0, 2),
    "mid": (2, 5),
    "senior": (5, 9),
    "lead": (8, 13),
    "principal": (10, 20),
    "manager": (7, 15),
    "director": (12, 25),
}


def _norm(s: str) -> str:
    return s.lower().strip().replace(".", "").replace("-", " ")


def _skill_overlap(jd_skills: List[str], cand_skills: List[str]) -> Tuple[List[str], List[str]]:
    cand_set = {_norm(s) for s in cand_skills}
    matched, missing = [], []
    for s in jd_skills:
        if _norm(s) in cand_set:
            matched.append(s)
        else:
            missing.append(s)
    return matched, missing


def _experience_score(jd: ParsedJD, candidate: Candidate) -> float:
    yrs = candidate.years_experience
    lo, hi = jd.min_years_experience, jd.max_years_experience
    sen_lo, sen_hi = _SENIORITY_RANGES.get(jd.seniority, (lo, hi))
    target_lo = max(lo, 0) if lo else sen_lo
    target_hi = hi if hi and hi < 30 else sen_hi

    if target_lo <= yrs <= target_hi:
        return 100.0
    if yrs < target_lo:
        gap = target_lo - yrs
        return max(0.0, 100.0 - gap * 25.0)
    overshoot = yrs - target_hi
    return max(40.0, 100.0 - overshoot * 8.0)


def _domain_score(jd_domains: List[str], cand_domains: List[str]) -> float:
    if not jd_domains:
        return 75.0
    jd_set = {_norm(d) for d in jd_domains}
    cand_set = {_norm(d) for d in cand_domains}
    overlap = jd_set & cand_set
    if not overlap:
        return 40.0
    return min(100.0, 60.0 + 40.0 * (len(overlap) / len(jd_set)))


def _location_score(jd: ParsedJD, candidate: Candidate) -> float:
    score = 70.0
    if "remote" in [w.lower() for w in jd.work_mode] and "remote" in [
        w.lower() for w in candidate.work_mode
    ]:
        score = 100.0
    elif jd.work_mode and any(w.lower() in [m.lower() for m in candidate.work_mode] for w in jd.work_mode):
        score = 90.0

    if jd.location:
        jd_loc = _norm(jd.location)
        cand_loc = _norm(candidate.location)
        if jd_loc in cand_loc or cand_loc in jd_loc:
            score = max(score, 95.0)
        elif "remote" in [w.lower() for w in candidate.work_mode]:
            score = max(score, 85.0)
        else:
            score = min(score, 60.0)
    return score


def _skills_score(
    jd: ParsedJD, candidate: Candidate
) -> Tuple[float, List[str], List[str], List[str]]:
    matched_must, missing_must = _skill_overlap(jd.must_have_skills, candidate.skills)
    matched_nice, _ = _skill_overlap(jd.nice_to_have_skills, candidate.skills)

    must_total = max(1, len(jd.must_have_skills))
    nice_total = max(1, len(jd.nice_to_have_skills)) if jd.nice_to_have_skills else 1

    must_ratio = len(matched_must) / must_total if jd.must_have_skills else 1.0
    nice_ratio = len(matched_nice) / nice_total if jd.nice_to_have_skills else 0.0

    score = 100.0 * (0.85 * must_ratio + 0.15 * nice_ratio)
    if jd.must_have_skills and len(matched_must) == len(jd.must_have_skills):
        score = min(100.0, score + 5.0)
    return score, matched_must, missing_must, matched_nice


def _composite(b: ScoreBreakdown) -> float:
    return round(
        0.45 * b.skills_score
        + 0.20 * b.experience_score
        + 0.15 * b.semantic_score
        + 0.10 * b.domain_score
        + 0.10 * b.location_score,
        1,
    )


def _templated_explanation(
    jd: ParsedJD,
    candidate: Candidate,
    breakdown: ScoreBreakdown,
    matched_must: List[str],
    missing_must: List[str],
    matched_nice: List[str],
) -> str:
    parts: List[str] = []

    if jd.must_have_skills:
        if len(matched_must) == len(jd.must_have_skills):
            parts.append(
                f"Hits all {len(matched_must)} must-have skills ({', '.join(matched_must)})."
            )
        else:
            parts.append(
                f"Matches {len(matched_must)}/{len(jd.must_have_skills)} must-have skills "
                f"({', '.join(matched_must) or 'none'})."
            )
            if missing_must:
                parts.append(f"Missing: {', '.join(missing_must)}.")

    if matched_nice:
        parts.append(f"Bonus nice-to-haves: {', '.join(matched_nice)}.")

    yrs = candidate.years_experience
    if jd.min_years_experience <= yrs <= jd.max_years_experience:
        parts.append(f"{yrs} yrs experience fits the {jd.min_years_experience}-{jd.max_years_experience} yr target.")
    elif yrs < jd.min_years_experience:
        parts.append(
            f"{yrs} yrs experience is below the {jd.min_years_experience}-yr minimum."
        )
    else:
        parts.append(
            f"{yrs} yrs experience exceeds the target range — possibly over-qualified."
        )

    if jd.domains and candidate.domains:
        overlap = set(d.lower() for d in jd.domains) & set(d.lower() for d in candidate.domains)
        if overlap:
            parts.append(f"Domain overlap: {', '.join(sorted(overlap))}.")

    if breakdown.location_score >= 90:
        parts.append("Location & work-mode align well.")
    elif breakdown.location_score < 70:
        parts.append("Location/work-mode is a partial fit.")

    return " ".join(parts)


def _llm_explanation(
    jd: ParsedJD,
    candidate: Candidate,
    breakdown: ScoreBreakdown,
    matched_must: List[str],
    missing_must: List[str],
    matched_nice: List[str],
    llm: LLMService,
) -> str:
    fallback = _templated_explanation(
        jd, candidate, breakdown, matched_must, missing_must, matched_nice
    )
    if not llm.available:
        return fallback

    prompt = f"""You are a recruiting assistant. Write a concise (2-3 sentence) explanation
for why this candidate matches (or doesn't fully match) the role. Be specific and factual.
Do NOT invent skills or experience the candidate doesn't have.

Role: {jd.role_title} ({jd.seniority}, {jd.min_years_experience}-{jd.max_years_experience} yrs)
Must-have skills: {', '.join(jd.must_have_skills) or 'none'}
Nice-to-have skills: {', '.join(jd.nice_to_have_skills) or 'none'}
JD domains: {', '.join(jd.domains) or 'unspecified'}

Candidate: {candidate.name} — {candidate.title}, {candidate.years_experience} yrs at {candidate.current_company or 'N/A'}
Skills: {', '.join(candidate.skills)}
Domains: {', '.join(candidate.domains)}
Summary: {candidate.summary}

Score breakdown (0-100):
- Skills: {breakdown.skills_score:.0f}
- Experience: {breakdown.experience_score:.0f}
- Domain: {breakdown.domain_score:.0f}
- Location/work-mode: {breakdown.location_score:.0f}
- Semantic similarity: {breakdown.semantic_score:.0f}

Matched must-haves: {', '.join(matched_must) or 'none'}
Missing must-haves: {', '.join(missing_must) or 'none'}
Bonus nice-to-haves: {', '.join(matched_nice) or 'none'}

Write 2-3 sentences. Lead with the strongest match signals, then call out any gaps."""

    text = llm.generate(prompt)
    return text or fallback


def score_candidate(
    jd: ParsedJD,
    candidate: Candidate,
    semantic_score_pct: float,
    llm: LLMService,
) -> MatchedCandidate:
    skills_score, matched_must, missing_must, matched_nice = _skills_score(jd, candidate)
    experience_score = _experience_score(jd, candidate)
    domain_score = _domain_score(jd.domains, candidate.domains)
    location_score = _location_score(jd, candidate)

    breakdown = ScoreBreakdown(
        skills_score=round(skills_score, 1),
        experience_score=round(experience_score, 1),
        domain_score=round(domain_score, 1),
        location_score=round(location_score, 1),
        semantic_score=round(semantic_score_pct, 1),
    )

    explanation = _llm_explanation(
        jd, candidate, breakdown, matched_must, missing_must, matched_nice, llm
    )

    return MatchedCandidate(
        candidate=candidate,
        match_score=_composite(breakdown),
        breakdown=breakdown,
        matched_must_have=matched_must,
        missing_must_have=missing_must,
        matched_nice_to_have=matched_nice,
        explanation=explanation,
    )
