# TalentScout — AI Talent Scouting Agent

A single-agent system that turns a raw Job Description into a **ranked, explainable candidate shortlist** in seconds — replacing hours of manual profile-sifting with deterministic multi-dimensional scoring and LLM-powered explanations.

## What it does

1. **Parses the JD** — extracts role, seniority, must-have / nice-to-have skills, location, work mode, and domains from free text.
2. **Retrieves candidates** — hybrid search over a candidate pool (semantic similarity via TF-IDF + skill/domain keyword signals).
3. **Scores & explains** — every candidate gets a 0-100 Match Score across **5 dimensions** (Skills, Experience, Domain, Location, Semantic) plus a human-readable explanation grounded in their actual profile.

## Tech stack

**Backend** (`backend/`)
- Python 3.10 + FastAPI + Pydantic
- scikit-learn TF-IDF + cosine similarity (lightweight, no PyTorch)
- Google Gemini for JD parsing & natural-language explanations (free tier)
- **Heuristic fallback** — works fully without any API key

**Frontend** (`frontend/`)
- React 18 + TypeScript + Vite
- TailwindCSS (custom olive/cream design system)

**Data**
- 30 synthetic but realistic candidate profiles (`backend/app/data/candidates.json`) covering backend, frontend, ML, GenAI, design, PM, DevOps, security, and more.

## Project structure

```
backend/
  app/
    agents/scout.py           # The Talent Scouting Agent orchestrator
    services/
      jd_parser.py            # JD → structured ParsedJD (LLM + heuristic)
      embeddings.py           # TF-IDF vector store
      retriever.py            # Hybrid retrieval
      matcher.py              # 5-dimensional scoring + explanations
      llm.py                  # Gemini client with graceful fallback
    models/schemas.py         # Pydantic models
    data/candidates.json      # Candidate pool
    main.py                   # FastAPI app
  requirements.txt
  .env.example
frontend/
  src/
    App.tsx
    components/               # Header, Hero, Marquee, JDInput, …
    types.ts
  package.json
```

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate     # PowerShell on Windows
pip install -r requirements.txt

# Optional: get a free Gemini key from https://aistudio.google.com/app/apikey
copy .env.example .env       # then paste your key into .env

python -m uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Try `GET /api/health` to confirm.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` → `http://localhost:8000`.

## Usage

1. Paste a JD (or pick one of the 3 built-in samples).
2. Slide the "Top results" control (3–15).
3. Click **Scout Candidates**.

You'll get:
- A **Parsed JD** card showing exactly what was extracted (must-haves, nice-to-haves, location, domains).
- A **ranked shortlist** with score rings, matched/missing skill chips, breakdown bars, and a 2-3 sentence explanation per candidate.

## Scoring weights

```
Match Score = 0.45 · Skills
            + 0.20 · Experience
            + 0.15 · Semantic similarity
            + 0.10 · Domain
            + 0.10 · Location / work-mode
```

A perfect must-have skill match adds a small calibration bonus.

## API

`POST /api/scout`
```json
{ "jd_text": "Senior Backend Engineer …", "top_k": 8 }
```
Response is a `ScoutResponse` containing the parsed JD, ranked matches with full breakdowns, and the active `llm_mode` (`gemini` or `heuristic`).

`GET /api/health` — liveness + LLM mode + pool size.
`GET /api/candidates` — full candidate pool (debug).

## Extending

- **Plug in a real ATS** — replace `app/data/candidates.json` and re-run; the embedding store rebuilds at startup.
- **Swap the LLM** — `app/services/llm.py` is provider-agnostic; point it at OpenAI / Anthropic by editing `generate()`.
- **Add an Engagement Agent** — the natural next step is a conversational outreach agent that takes this shortlist and produces an Interest Score per candidate.
