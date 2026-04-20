"""FastAPI Backend for Professional Email Generator."""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.config import load_config
from src.model_manager import ModelManager
from src.orchestrator import EmailAssistantOrchestrator
from src.models import EmailRequest
from src.agents import EmailCoachAgent, SuggestorAgent

app = FastAPI(title="Professional Email Generator API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
model_manager = ModelManager(config)

class UIRequest(BaseModel):
    email_purpose: str
    recipient: str
    situation: str
    tone_preference: str = "auto detect"
    key_points: str = ""
    drafting_style: str = "balanced"
    improve_existing_email: bool = False
    existing_email: str = ""
    num_versions: int = 3

@app.post("/generate")
async def generate_email(request: UIRequest):
    email_req = EmailRequest(
        email_purpose=request.email_purpose,
        recipient=request.recipient,
        situation=request.situation,
        tone_preference=request.tone_preference,
        key_points=request.key_points,
        drafting_style=request.drafting_style,
        improve_existing_email=request.improve_existing_email,
        existing_email=request.existing_email,
        num_versions=request.num_versions
    )

    def _run_workflow(llm):
        orchestrator = EmailAssistantOrchestrator(llm)
        return orchestrator.run(email_req)

    try:
        result = model_manager.run_with_fallback(_run_workflow)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SuggestRequest(BaseModel):
    email_purpose: str
    recipient: str

@app.post("/suggest-points")
async def suggest_points(request: SuggestRequest):
    def _run_suggest(llm):
        suggestor = SuggestorAgent(llm)
        return suggestor.run(request.email_purpose, request.recipient)

    try:
        result = model_manager.run_with_fallback(_run_suggest)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CoachRequest(BaseModel):
    current_draft: str
    recipient: str
    intent: str

@app.post("/coach")
async def coach_email(request: CoachRequest):
    def _run_coach(llm):
        coach = EmailCoachAgent(llm)
        return coach.run(request.current_draft, request.recipient, request.intent)

    try:
        result = model_manager.run_with_fallback(_run_coach)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
