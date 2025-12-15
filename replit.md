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
- **Backend**: Python 3.11 + FastAPI (REST API)
- **Frontend**: Vue 3 + TypeScript + Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **Database**: SQLite (pa_copilot.db)
- **AI**: OpenAI GPT-4o for clinical analysis
- **Styling**: Custom CSS (based on Bootstrap design)

## Project Structure
```
├── main.py                      # FastAPI REST API entry point
├── src/
│   ├── models/
│   │   └── database.py          # SQLite database models and queries
│   ├── services/
│   │   ├── openai_client.py     # OpenAI API integration
│   │   └── policy_engine.py     # Rule-based criteria evaluation
│   └── data/
│       └── seed_data.py         # Synthetic cases and policies
├── frontend/                    # Vue 3 SPA
│   ├── src/
│   │   ├── views/               # Page components (Dashboard, CaseDetail, Metrics)
│   │   ├── components/          # Shared components (AppLayout)
│   │   ├── stores/              # Pinia stores (cases, metrics, app)
│   │   ├── services/            # API service layer
│   │   ├── types/               # TypeScript interfaces
│   │   ├── router/              # Vue Router configuration
│   │   ├── App.vue              # Root component
│   │   └── main.ts              # Application entry point
│   ├── vite.config.ts           # Vite configuration with API proxy
│   └── package.json             # Node.js dependencies
└── templates/                   # Legacy Jinja2 templates (archived)
```

## Key Features
1. **Case Dashboard**: View all PA cases with status and AI recommendations
2. **Co-Pilot Screen**: Structured summary, policy alignment, draft letters
3. **Policy Engine**: Evaluates stage, biomarker, and prior therapy criteria
4. **AI Recommendations**: Approve/Deny/Pend with clinical rationale
5. **Metrics Dashboard**: Track turnaround times and decision consistency

## API Endpoints
- `GET /api/cases` - List all cases
- `GET /api/cases/{id}` - Get case details
- `POST /api/cases/{id}/process` - Process case with AI
- `POST /api/cases/{id}/decide` - Submit decision
- `GET /api/metrics` - Get performance metrics
- `GET /api/status` - Get demo mode status
- `GET /api/health` - Health check

## Environment Variables
- `OPENAI_API_KEY`: Required for AI-powered case analysis (optional for demo mode)

## Running the Application
The application runs with two workflows:

**Frontend (Vue 3):**
- Runs on port 5000 with Vite dev server
- Proxies API requests to backend on port 8000

**Backend (FastAPI):**
- Runs on port 8000 with Uvicorn
- Serves REST API endpoints

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
- Professional healthcare UI
- Color-coded status indicators (met/unmet/unknown)
- Editable draft letters before finalization
- Vue 3 SPA for modern, responsive experience

## Recent Changes
- December 8, 2025: Converted to Vue 3 SPA
  - Created Vue 3 frontend with Vite, Vue Router, and Pinia
  - Refactored FastAPI to serve JSON REST API
  - Implemented Dashboard, Case Detail, and Metrics views
  - Added TypeScript types and API service layer
  - Configured dual workflow (Frontend on 5000, Backend on 8000)
- December 8, 2025: Configured for Replit environment
  - Set up uv-based workflow on port 5000
  - Added Python and Node.js .gitignore entries
- December 2024: Initial MVP implementation
  - Added 5 synthetic oncology cases
  - Implemented rule-based policy engine
  - Created co-pilot dashboard with AI integration
