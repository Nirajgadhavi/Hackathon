# PA Co-Pilot - AI-Powered Prior Authorization System

## Overview
An AI-powered clinical co-pilot for specialty drug prior authorization review that dramatically reduces Medical Director review time while ensuring consistent, evidence-based decisions.

## Purpose & Goals
- Auto-summarize PA requests (diagnosis, labs, biomarkers, prior therapy)
- Evaluate coverage criteria against payer policies
- Generate AI recommendations with clinical rationale
- Draft provider and member communication letters
- Reduce MD review time from 25-40 min to 6-10 min per case

## Current State
MVP implementation complete with:
- 5 synthetic oncology PA cases (approve/deny/pend scenarios)
- 2 payer policies (Keytruda for NSCLC, Opdivo for Melanoma)
- AI-powered case extraction and recommendation
- Rule-based policy criteria evaluation
- Automated letter generation

## Tech Stack
- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Jinja2 templates + Bootstrap 5
- **Database**: SQLite (pa_copilot.db)
- **AI**: OpenAI GPT-4o for clinical analysis
- **Server**: Uvicorn on port 5000

## Project Structure
```
├── main.py                      # FastAPI application entry point
├── src/
│   ├── models/
│   │   └── database.py          # SQLite database models and queries
│   ├── services/
│   │   ├── openai_client.py     # OpenAI API integration
│   │   └── policy_engine.py     # Rule-based criteria evaluation
│   └── data/
│       └── seed_data.py         # Synthetic cases and policies
├── templates/
│   ├── base.html                # Base template with navigation
│   ├── index.html               # Case list dashboard
│   ├── case_detail.html         # Co-pilot review screen
│   └── metrics.html             # Performance metrics
└── static/                      # Static assets
```

## Key Features
1. **Case Dashboard**: View all PA cases with status and AI recommendations
2. **Co-Pilot Screen**: Structured summary, policy alignment, draft letters
3. **Policy Engine**: Evaluates stage, biomarker, and prior therapy criteria
4. **AI Recommendations**: Approve/Deny/Pend with clinical rationale
5. **Metrics Dashboard**: Track turnaround times and decision consistency

## Environment Variables
- `OPENAI_API_KEY`: Required for AI-powered case analysis

## Running the Application
```bash
python main.py
```
The server starts on http://0.0.0.0:5000

## Demo Flow
1. Select a PA case from the dashboard
2. Click "Process with AI" to analyze the case
3. Review AI-extracted summary and policy alignment
4. Review AI recommendation and draft letters
5. Make final decision and save

## Expected Impact
| Metric | Pre-AI | Post-AI |
|--------|--------|---------|
| PA Turnaround | 72-120 hrs | 12-24 hrs |
| MD Review Time | 25-40 min | 6-10 min |
| SLA Compliance | 82-88% | 97-99% |
| Appeals Rate | High | 30-45% lower |

## User Preferences
- Professional healthcare UI with Bootstrap 5
- Color-coded status indicators (met/unmet/unknown)
- Editable draft letters before finalization

## Recent Changes
- December 2024: Initial MVP implementation
- Added 5 synthetic oncology cases
- Implemented rule-based policy engine
- Created co-pilot dashboard with AI integration
