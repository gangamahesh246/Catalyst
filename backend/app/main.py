"""FastAPI entrypoint for the Talent Scouting Agent."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.agents.scout import TalentScoutAgent  # noqa: E402
from app.models.schemas import ScoutRequest, ScoutResponse  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scout-agent")

agent: TalentScoutAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    log.info("Loading Talent Scouting Agent...")
    agent = TalentScoutAgent()
    log.info(
        "Agent ready. LLM mode: %s | Candidates: %d",
        agent.llm.mode,
        len(agent.candidates),
    )
    yield


app = FastAPI(
    title="Talent Scouting Agent",
    description="AI agent that parses a JD and returns ranked, explainable candidate matches.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_mode": agent.llm.mode if agent else "unknown",
        "candidates_loaded": len(agent.candidates) if agent else 0,
    }


@app.get("/api/candidates")
def list_candidates():
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not ready")
    return {"count": len(agent.candidates), "candidates": [c.model_dump() for c in agent.candidates]}


@app.post("/api/scout", response_model=ScoutResponse)
def scout(req: ScoutRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not ready")
    try:
        return agent.scout(req.jd_text, top_k=req.top_k)
    except Exception as e:
        log.exception("Scout failed")
        raise HTTPException(status_code=500, detail=str(e))
