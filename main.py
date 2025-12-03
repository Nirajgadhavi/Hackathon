import os
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.models.database import (
    init_db, get_all_cases, get_case, update_case, 
    add_audit_log, get_metrics, get_policy
)
from src.data.seed_data import seed_database
from src.services.openai_client import extract_case_data, generate_recommendation, draft_letters, is_demo_mode
from src.services.policy_engine import evaluate_criteria, calculate_complexity, get_triage_summary

app = FastAPI(title="PA Co-Pilot", description="AI-Powered Prior Authorization Co-Pilot")

os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    seed_database()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    cases = get_all_cases()
    metrics = get_metrics()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cases": cases,
        "metrics": metrics,
        "demo_mode": is_demo_mode()
    })

@app.get("/case/{case_id}", response_class=HTMLResponse)
async def case_detail(request: Request, case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    policy = get_policy(case['policy_id'])
    
    return templates.TemplateResponse("case_detail.html", {
        "request": request,
        "case": case,
        "policy": policy,
        "demo_mode": is_demo_mode()
    })

@app.post("/case/{case_id}/process")
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

@app.post("/case/{case_id}/decide")
async def submit_decision(
    case_id: str,
    final_decision: str = Form(...),
    decision_notes: str = Form(""),
    provider_letter: str = Form(""),
    member_letter: str = Form("")
):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    created_at = datetime.fromisoformat(case['created_at'].replace('Z', '+00:00') if case['created_at'] else datetime.now().isoformat())
    now = datetime.now()
    turnaround_minutes = int((now - created_at.replace(tzinfo=None)).total_seconds() / 60)
    
    update_case(case_id, {
        'final_decision': final_decision,
        'final_decision_notes': decision_notes,
        'provider_letter': provider_letter,
        'member_letter': member_letter,
        'status': 'decided',
        'decided_at': now.isoformat(),
        'turnaround_minutes': turnaround_minutes
    })
    
    add_audit_log(case_id, "decision_finalized", f"Medical Director decision: {final_decision}")
    
    return RedirectResponse(url=f"/case/{case_id}?decided=true", status_code=303)

@app.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request):
    metrics = get_metrics()
    cases = get_all_cases()
    
    decided_cases = [c for c in cases if c.get('final_decision')]
    
    return templates.TemplateResponse("metrics.html", {
        "request": request,
        "metrics": metrics,
        "decided_cases": decided_cases
    })

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
