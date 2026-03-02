# AI-Powered Project Planning & Risk Forecasting App

A stakeholder-ready Streamlit application that generates project plans with Groq, builds dependency workflows, runs Monte Carlo forecasting, highlights delay drivers, compares execution scenarios, and stores session history in SQLite.

## What This App Delivers
- AI task decomposition from plain-language project descriptions
- Strict task validation (IDs, dependencies, durations, risk factors)
- DAG workflow modeling and critical-path analysis
- Dynamic critical-path Monte Carlo simulation (per-iteration path recomputation)
- Risk metrics: Mean, P50, P80, delay probability
- Delay-driver ranking from simulated critical-path frequency
- Scenario lab: baseline vs aggressive deadline vs increased capacity
- SQLite session history with reload and export
- Stakeholder-friendly UI with executive summary and downloadable outputs

## Architecture
- `Streamlit` for the web app
- `Groq` (`llama-3.3-70b-versatile`) for plan generation
- `Pydantic` for schema validation
- `NetworkX` for workflow DAG modeling
- `NumPy` + `Pandas` for simulation and analytics
- `Plotly` for interactive charts
- `SQLite` for lightweight run persistence

## Repository Structure
```
ai-powered-project-planning-risk-forecasting-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app.py
├── PROJECT_WORKFLOW.md
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── scripts/
│   └── smoke_test.py
├── tests/
│   ├── test_schema.py
│   ├── test_graph_builder.py
│   ├── test_simulation.py
│   ├── test_metrics.py
│   ├── test_scenarios_and_drivers.py
│   └── test_integration_generation.py
├── presentation/
│   ├── stakeholder-deck.md
│   ├── demo-script.md
│   ├── backup-demo.md
│   └── powerpoint-ready-deck.md
└── src/
    ├── config.py
    ├── ai/
    ├── modeling/
    ├── simulation/
    ├── analytics/
    ├── visualization/
    ├── storage/
    └── utils/
```

## Environment Setup

**`macOS` / `Linux`**
```bash
# Set up Python environment
pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**`Windows` (PowerShell)**
```powershell
# Set up Python environment
pyenv local 3.11.3
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
**`Windows` (Git Bash)**
```Git Bash
# Set up Python environment
pyenv local 3.12.12
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

1. Create and activate the environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install runtime dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template and fill values:
   ```bash
   cp .env.example .env
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Environment Variables
Use `.env` (or deployment secrets):

```
GROQ_API_KEY=
APP_MODE=mock
GROQ_MODEL=llama-3.3-70b-versatile
DEFAULT_ITERATIONS=1000
MAX_ITERATIONS=2000
MAX_TASKS=12
MIN_DURATION=0.1
GROQ_TIMEOUT_SECONDS=30
GROQ_MAX_RETRIES=2
SQLITE_DB_PATH=data/app.db
```

Notes:
- `APP_MODE=mock` is best for UI development and fallback demos.
- `APP_MODE=real` requires `GROQ_API_KEY`.

## UI Walkthrough
The final UI is organized into 6 tabs:
1. `Executive Brief` (risk badge, KPI cards, summary)
2. `Task Plan` (editable plan table + recompute)
3. `Workflow` (dependency graph + critical path)
4. `Risk Dashboard` (Monte Carlo histogram + top delay drivers)
5. `Scenario Lab` (decision comparison across scenarios)
6. `History & Export` (SQLite history, reload, CSV/JSON export)

## Testing
Install dev dependencies and run tests:
```bash
pip install -r requirements-dev.txt
pytest -q
```

Run smoke test before demos:
```bash
python scripts/smoke_test.py
```

## Deployment

### Primary: Streamlit Community Cloud
1. Push repo to GitHub
2. Create app at `share.streamlit.io`
3. Set `app.py` entrypoint
4. Add secrets: `GROQ_API_KEY` (and optional config vars)
5. Deploy and verify both `mock` and `real` modes

### Backup: Hugging Face Spaces (Streamlit SDK)
1. Create Streamlit Space
2. Push the same repo
3. Add `GROQ_API_KEY` in repository secrets

### Docker (Optional, for reproducibility)
```bash
docker compose up --build
```

Docker is not required for Streamlit Cloud deployment, but included for production-readiness and local parity.

## Presentation Assets
Use the materials in `presentation/`:
- `stakeholder-deck.md` (10-slide narrative)
- `demo-script.md` (5-7 minute live flow)
- `backup-demo.md` (mock-mode contingency)
- `powerpoint-ready-deck.md` (12-slide, PowerPoint-ready structure)
- `post-presentation-qa-playbook.md` (rapid Q&A answer sheet)

## Team Workflow Asset
- `PROJECT_WORKFLOW.md` includes:
  - 2-person 4-week execution plan
  - scope discipline (only required topics)
  - DoR / DoD
  - ownership and readiness checklist

## Internal Understanding Asset
- `PROJECT_UNDERSTANDING_GUIDE.md`:
  - end-to-end system explanation
  - module-by-module ownership and logic map
  - metrics/scenario interpretation
  - troubleshooting and handover checklist

## Suggested Demo Projects
- `Implement a CRM rollout across 3 teams`
- `Plan a marketing campaign launch`
- `Build a mobile app MVP with login and payments`

## License
MIT
