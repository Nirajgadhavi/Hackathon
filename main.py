import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.models.database import (
    init_db, get_all_cases, get_case, update_case, 
    add_audit_log, get_metrics, get_policy
)
from src.data.seed_data import seed_database
from src.services.openai_client import extract_case_data, generate_recommendation, draft_letters, is_demo_mode
from src.services.policy_engine import evaluate_criteria, calculate_complexity, get_triage_summary

app = FastAPI(title="PA Co-Pilot API", description="AI-Powered Prior Authorization Co-Pilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DecisionRequest(BaseModel):
    final_decision: str
    decision_notes: str = ""
    provider_letter: str = ""
    member_letter: str = ""

@app.on_event("startup")
async def startup_event():
    seed_database()

@app.get("/api/cases")
async def get_cases():
    cases = get_all_cases()
    return cases

@app.get("/api/cases/{case_id}")
async def get_case_detail(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases/{case_id}/process")
async def process_case(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    policy = get_policy(case['policy_id'])
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    add_audit_log(case_id, "processing_started", "AI processing initiated")
    
    extracted_data = extract_case_data(case['raw_text'])
    
    if 'error' in extracted_data:
        add_audit_log(case_id, "extraction_error", extracted_data.get('error'))
        raise HTTPException(status_code=500, detail=f"Extraction error: {extracted_data.get('error')}")
    
    add_audit_log(case_id, "case_extracted", "Clinical data extracted successfully")
    
    criteria_evaluation = evaluate_criteria(extracted_data, policy)
    complexity = calculate_complexity(criteria_evaluation)
    triage_summary = get_triage_summary(criteria_evaluation)
    
    add_audit_log(case_id, "criteria_evaluated", f"Complexity: {complexity}")
    
    recommendation = generate_recommendation(
        extracted_data,
        policy,
        criteria_evaluation,
        policy.get('guidelines', [])
    )
    
    add_audit_log(case_id, "recommendation_generated", f"AI suggests: {recommendation.get('recommendation', 'unknown')}")
    
    letters = draft_letters(extracted_data, policy, recommendation)
    
    add_audit_log(case_id, "letters_drafted", "Provider and member letters generated")
    
    update_case(case_id, {
        'extracted_data': extracted_data,
        'criteria_evaluation': criteria_evaluation,
        'ai_recommendation': recommendation,
        'provider_letter': letters.get('provider_letter', ''),
        'member_letter': letters.get('member_letter', ''),
        'complexity': complexity,
        'status': 'processed',
        'processed_at': datetime.now().isoformat()
    })
    
    add_audit_log(case_id, "processing_completed", "Case ready for Medical Director review")
    
    return {"status": "success", "message": "Case processed successfully"}

@app.post("/api/cases/{case_id}/decide")
async def submit_decision(case_id: str, request: DecisionRequest):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    created_at = datetime.fromisoformat(case['created_at'].replace('Z', '+00:00') if case['created_at'] else datetime.now().isoformat())
    now = datetime.now()
    turnaround_minutes = int((now - created_at.replace(tzinfo=None)).total_seconds() / 60)
    
    update_case(case_id, {
        'final_decision': request.final_decision,
        'final_decision_notes': request.decision_notes,
        'provider_letter': request.provider_letter,
        'member_letter': request.member_letter,
        'status': 'decided',
        'decided_at': now.isoformat(),
        'turnaround_minutes': turnaround_minutes
    })
    
    add_audit_log(case_id, "decision_finalized", f"Medical Director decision: {request.final_decision}")
    
    return {"status": "success", "message": "Decision recorded successfully"}

@app.get("/api/metrics")
async def get_metrics_data():
    metrics = get_metrics()
    return metrics

@app.get("/api/status")
async def get_status():
    return {"demo_mode": is_demo_mode()}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
