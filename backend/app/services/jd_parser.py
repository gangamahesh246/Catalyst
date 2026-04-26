"""Job Description parser. Uses Gemini if available, else regex/keyword heuristics."""
from __future__ import annotations

import re
from typing import List, Optional

from app.models.schemas import ParsedJD
from app.services.llm import LLMService


_KNOWN_SKILLS = {
    "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "kotlin",
    "swift", "dart", "ruby", "php", "scala", "solidity",
    "react", "next.js", "nextjs", "vue", "angular", "svelte", "tailwindcss", "tailwind",
    "redux", "graphql", "rest", "rest apis", "trpc", "node.js", "node", "express", "nest.js",
    "django", "flask", "fastapi", "spring boot", "spring", "rails", "laravel",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "snowflake", "bigquery", "elasticsearch",
    "kafka", "rabbitmq", "celery", "airflow", "spark", "dbt", "hadoop",
    "aws", "azure", "gcp", "kubernetes", "k8s", "docker", "terraform", "ansible", "jenkins",
    "ci/cd", "ci", "cd", "linux", "prometheus", "grafana",
    "pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost", "pandas", "numpy",
    "mlops", "mlflow", "sagemaker", "huggingface", "hugging face", "transformers", "llms", "llm",
    "rag", "vector databases", "pinecone", "langchain", "llamaindex", "openai api", "prompt engineering",
    "figma", "design systems", "user research", "prototyping", "accessibility", "ux writing",
    "selenium", "cypress", "playwright", "jest", "jmeter", "test automation", "api testing",
    "system design", "microservices", "distributed systems", "agile", "scrum",
    "sql", "tableau", "power bi", "excel", "statistics", "a/b testing", "experimentation",
    "smart contracts", "ethereum", "web3", "web3.js", "hardhat", "solana",
    "ios", "android", "flutter", "firebase",
    "owasp", "penetration testing", "security", "siem", "incident response",
}

_SENIORITY_PATTERNS = [
    (r"\bdirector\b", "director"),
    (r"\b(vp|vice president|head of)\b", "director"),
    (r"\b(engineering manager|em)\b", "manager"),
    (r"\b(principal)\b", "principal"),
    (r"\b(staff engineer|staff)\b", "lead"),
    (r"\b(sr\.?|senior)\b", "senior"),
    (r"\b(architect|tech lead|team lead|lead)\b", "lead"),
    (r"\bmanager\b", "manager"),
    (r"\b(jr\.?|junior|entry[- ]level|fresher|new grad)\b", "junior"),
    (r"\b(intermediate|mid[- ]level|mid)\b", "mid"),
]

_WORK_MODE_PATTERNS = {
    "remote": r"\b(remote|work from home|wfh|fully[- ]remote)\b",
    "hybrid": r"\b(hybrid)\b",
    "onsite": r"\b(on[- ]?site|in[- ]office|in[- ]person)\b",
}


def _heuristic_parse(jd_text: str) -> ParsedJD:
    text = jd_text.strip()
    lower = text.lower()

    role_title = ""
    for line in text.splitlines():
        line = line.strip(" -*•\t")
        if line:
            role_title = line[:100]
            break
    if not role_title:
        role_title = "Unspecified Role"

    seniority = "mid"
    for pat, label in _SENIORITY_PATTERNS:
        if re.search(pat, lower):
            seniority = label
            break

    min_y, max_y = 0, 30
    yr_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*\+?\s*(?:yrs?|years)", lower)
    if yr_match:
        min_y, max_y = int(yr_match.group(1)), int(yr_match.group(2))
    else:
        single = re.search(r"(\d+)\s*\+\s*(?:yrs?|years)", lower)
        if single:
            min_y = int(single.group(1))
            max_y = min_y + 8
        else:
            single2 = re.search(r"(?:at least|minimum|min\.?)\s*(\d+)\s*(?:yrs?|years)", lower)
            if single2:
                min_y = int(single2.group(1))

    found_skills: List[str] = []
    for skill in _KNOWN_SKILLS:
        pat = r"\b" + re.escape(skill) + r"\b"
        if re.search(pat, lower):
            canonical = skill.title() if skill.islower() and not skill.isupper() else skill
            if skill in {"aws", "gcp", "ios", "ci/cd", "k8s", "llm", "llms", "rag", "siem", "sql"}:
                canonical = skill.upper()
            if canonical not in found_skills:
                found_skills.append(canonical)

    must, nice = found_skills, []
    must_section = re.search(
        r"(must[- ]have|requirements|required skills|what you bring)[:\s]*\n?([\s\S]*?)(?=\n\s*(nice[- ]to[- ]have|preferred|bonus|good to have|responsibilities|about you|$))",
        lower,
    )
    nice_section = re.search(
        r"(nice[- ]to[- ]have|preferred|bonus|good to have)[:\s]*\n?([\s\S]*?)(?=\n\s*(responsibilities|about|$))",
        lower,
    )

    if must_section or nice_section:
        must, nice = [], []
        must_text = must_section.group(2) if must_section else lower
        nice_text = nice_section.group(2) if nice_section else ""
        for skill in found_skills:
            in_must = skill.lower() in must_text
            in_nice = skill.lower() in nice_text
            if in_nice and not in_must:
                nice.append(skill)
            else:
                must.append(skill)

    work_modes = [m for m, p in _WORK_MODE_PATTERNS.items() if re.search(p, lower)]

    location: Optional[str] = None
    loc_match = re.search(
        r"(?:location|based in|office in)[:\s]+([A-Z][A-Za-z .,/-]+?)(?:\.|\n|,\s|$)",
        text,
    )
    if loc_match:
        location = loc_match.group(1).strip()
    else:
        for city in ["Bangalore", "Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune",
                     "Chennai", "Gurgaon", "Noida", "Kolkata", "Kochi", "Ahmedabad",
                     "Remote", "London", "New York", "San Francisco", "Berlin"]:
            if re.search(r"\b" + city + r"\b", text):
                location = city
                break

    domains: List[str] = []
    for d in ["fintech", "healthtech", "edtech", "saas", "ecommerce", "logistics",
              "ai", "ml", "web3", "banking", "consumer", "marketplace",
              "developer-tools", "developer tools", "enterprise", "trading"]:
        if d in lower:
            domains.append(d.replace(" ", "-"))

    responsibilities: List[str] = []
    resp_section = re.search(
        r"(responsibilities|what you'?ll do|the role)[:\s]*\n?([\s\S]*?)(?=\n\s*(requirements|must|nice|qualifications|about|$))",
        lower,
    )
    if resp_section:
        for line in resp_section.group(2).splitlines():
            line = line.strip(" -*•\t")
            if 10 < len(line) < 200:
                responsibilities.append(line.capitalize())
                if len(responsibilities) >= 6:
                    break

    return ParsedJD(
        role_title=role_title,
        seniority=seniority,
        min_years_experience=min_y,
        max_years_experience=max_y,
        must_have_skills=must,
        nice_to_have_skills=nice,
        domains=domains,
        location=location,
        work_mode=work_modes,
        responsibilities=responsibilities,
        raw_jd=jd_text,
    )


def _llm_parse(jd_text: str, llm: LLMService) -> Optional[ParsedJD]:
    prompt = f"""You are a recruiting assistant. Extract structured fields from this Job Description.

Return ONLY a valid JSON object with this exact schema:
{{
  "role_title": "string (e.g. 'Senior Backend Engineer')",
  "seniority": "one of: junior, mid, senior, lead, principal, manager, director",
  "min_years_experience": "integer",
  "max_years_experience": "integer",
  "must_have_skills": ["array of canonical skill strings"],
  "nice_to_have_skills": ["array of canonical skill strings"],
  "domains": ["array like fintech, saas, healthtech, ai, ecommerce"],
  "location": "string or null",
  "work_mode": ["any of: remote, hybrid, onsite"],
  "responsibilities": ["3-6 short bullets"]
}}

Use canonical skill names (e.g. 'Python', 'React', 'AWS', 'PostgreSQL', 'Kubernetes').
If a field isn't specified, use sensible defaults (min_years=0, max_years=30, empty arrays).

Job Description:
\"\"\"
{jd_text}
\"\"\"
"""
    data = llm.generate_json(prompt)
    if not data:
        return None
    try:
        return ParsedJD(
            role_title=data.get("role_title", "Unspecified Role"),
            seniority=data.get("seniority", "mid"),
            min_years_experience=int(data.get("min_years_experience", 0) or 0),
            max_years_experience=int(data.get("max_years_experience", 30) or 30),
            must_have_skills=list(data.get("must_have_skills") or []),
            nice_to_have_skills=list(data.get("nice_to_have_skills") or []),
            domains=list(data.get("domains") or []),
            location=data.get("location"),
            work_mode=list(data.get("work_mode") or []),
            responsibilities=list(data.get("responsibilities") or []),
            raw_jd=jd_text,
        )
    except Exception:
        return None


def parse_jd(jd_text: str, llm: LLMService) -> ParsedJD:
    """Parse a free-text JD into a structured ParsedJD."""
    if llm.available:
        parsed = _llm_parse(jd_text, llm)
        if parsed is not None:
            return parsed
    return _heuristic_parse(jd_text)
