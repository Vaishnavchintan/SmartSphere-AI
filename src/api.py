"""
FastAPI Webhook & REST Service for SmartSphere AI.
Exposes endpoints for CI/CD pipelines, GitHub webhooks, and editor integrations.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.agents.crew import SmartSphereCrew
from src.tools.static_analyzer import RadonTool, BanditTool, SecretScannerTool

app = FastAPI(
    title="SmartSphere AI API",
    description="Multi-Agent Code Review & Documentation System",
    version="1.0.0",
)

radon_tool = RadonTool()
bandit_tool = BanditTool()
secret_tool = SecretScannerTool()


class ReviewRequest(BaseModel):
    code: str = Field(..., description="Python source code to review")
    filename: Optional[str] = Field("app.py", description="Name of the file")
    repo_path: Optional[str] = Field(".", description="Path to codebase for RAG context")


class StaticAnalysisResponse(BaseModel):
    radon_complexity: str
    security_findings: str
    secret_findings: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartSphere AI Multi-Agent API",
        "version": "1.0.0",
    }


@app.post("/api/analyze-static", response_model=StaticAnalysisResponse)
def analyze_static(req: ReviewRequest):
    """Fast deterministic static analysis without LLM latency."""
    return StaticAnalysisResponse(
        radon_complexity=radon_tool._run(req.code),
        security_findings=bandit_tool._run(req.code),
        secret_findings=secret_tool._run(req.code),
    )


@app.post("/api/review")
def run_crew_review(req: ReviewRequest):
    """Executes the full 4-agent CrewAI orchestration."""
    try:
        crew = SmartSphereCrew(repo_path=req.repo_path)
        report = crew.run(code_content=req.code, filename=req.filename)
        return {
            "status": "success",
            "filename": req.filename,
            "markdown_report": report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
