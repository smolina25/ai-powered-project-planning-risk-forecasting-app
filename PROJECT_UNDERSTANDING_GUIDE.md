# Project Understanding Guide (Internal)

This document is for team understanding and handover readiness.
It explains what the app does, how data flows, where each logic lives, and how to debug quickly.

## 1) What This Project Is
certAIn Project Intelligence is a planning-risk decision support app.
Given a project description, it:
- generates a structured task plan,
- validates task/dependency quality,
- builds a workflow DAG,
- runs Monte Carlo simulation for schedule uncertainty,
- reports risk metrics and delay drivers,
- compares execution scenarios,
- stores run history and supports export.

It is not a generic chatbot.
The supervised model is used as an advisory signal, while Monte Carlo remains the primary forecasting engine.

## 2) End-to-End Flow (Mental Model)
1. User enters project text and simulation settings in Streamlit sidebar (`app.py`).
2. Task plan is generated via:
   - `mock` mode: deterministic local sample data
   - `real` mode: Groq LLM JSON generation
3. Generated tasks are validated with Pydantic schema rules.
4. Tasks become a dependency graph (DAG).
5. Monte Carlo runs sample durations and recompute critical path each iteration.
6. Metrics are computed (mean, P50, P80, delay probability).
7. Delay drivers are ranked by critical-path frequency.
8. Advisory ML scoring predicts task risk classes from structured task features.
9. Scenario comparison runs across baseline / aggressive deadline / capacity boost.
10. Run is stored in SQLite and can be reloaded/exported.

## 3) Code Map (Where Things Live)
- UI and orchestration: `app.py`
- Config and environment: `src/config.py`
- AI generation:
  - prompt construction: `src/ai/prompt.py`
  - API client: `src/ai/llm_client.py`
  - generation + retries + parsing: `src/ai/task_generator.py`
  - schema validation: `src/ai/schema.py`
  - mock fallback: `src/ai/mock_data.py`
- Workflow modeling:
  - graph build and DAG checks: `src/modeling/graph_builder.py`
  - longest path / critical path: `src/modeling/critical_path.py`
- Simulation and analytics:
  - Monte Carlo engine: `src/simulation/monte_carlo.py`
  - metrics: `src/analytics/metrics.py`
  - delay drivers: `src/analytics/risk_drivers.py`
  - scenarios: `src/analytics/scenarios.py`
- Advisory ML scoring:
  - feature schema and validation: `src/ml/schema.py`
  - model loading and status handling: `src/ml/predictor.py`
  - scoring service: `src/ml/service.py`
- Charts: `src/visualization/charts.py`
- Persistence:
  - schema/init: `src/storage/db.py`
  - CRUD-style run persistence/load: `src/storage/repository.py`
- Reliability:
  - smoke check: `scripts/smoke_test.py`
  - tests: `tests/`
  - CI: `.github/workflows/ci.yml`

## 4) Key Technical Decisions (Why)
1. Strict schema validation before simulation
Reason: LLM output can be malformed; simulation needs reliable structure.

2. DAG enforcement for dependencies
Reason: cycles make schedule logic invalid.

3. Dynamic critical path per Monte Carlo iteration
Reason: uncertainty can shift bottlenecks; static path underestimates risk behavior.

4. P80 shown as commitment guidance
Reason: more robust than median-only planning under uncertainty.

5. SQLite persistence
Reason: lightweight, local, demo-friendly history/reload/export.

6. Mock mode
Reason: demo resilience if API latency/errors occur.

## 5) Data Contracts You Should Know
Task object (core fields):
- `id`: `T1`, `T2`, ...
- `name`
- `mean_duration` (days, >= 1)
- `std_dev` (>= 0)
- `dependencies` (list of prior task IDs)
- `risk_factor` (0..1)

Validation expectations:
- IDs are unique and sequential.
- Dependencies reference known earlier tasks only.
- Graph must be acyclic.

## 6) What the Main Metrics Mean
- `mean`: average completion across simulations.
- `p50`: median completion (50th percentile).
- `p80`: safer commitment date (80th percentile).
- `delay_probability`: probability completion exceeds selected deadline.

Operational interpretation:
- High delay probability + high P80 gap = schedule risk.
- Top delay drivers indicate where mitigation should focus.

## 7) Scenario Logic (Business Explanation)
- Baseline: current plan and deadline.
- Aggressive deadline: same work, tighter target (risk usually increases).
- Increased capacity: reduced duration/variance by factor (risk often decreases).

Recommendation in UI:
- scenario with lowest delay probability.

## 8) How to Run Fast (Daily Use)
Local app:
```bash
source .venv/bin/activate
streamlit run app.py
```

Reliability check:
```bash
source .venv/bin/activate
python scripts/smoke_test.py
```

Unit tests (when environment allows):
```bash
source .venv/bin/activate
pytest -q
```

## 9) Common Failure Points and Fixes
1. `GROQ_API_KEY` missing in `real` mode
- Fix: set key in `.env` or Streamlit secrets, or switch to `mock`.

2. Invalid task graph / dependency errors
- Fix: ensure dependencies reference existing earlier tasks and no cycles.

3. LLM malformed JSON
- Fix: retry, lower task count, or use mock mode for demo continuity.

4. SQLite write/load issues
- Fix: verify `SQLITE_DB_PATH` and writable `data/` directory.

5. Test command unavailable locally
- Fix: install `requirements-dev.txt` outside restricted environment, or use GitHub Actions CI.

## 10) What to Say If Asked “What Is New Here?”
Practical innovation is the integration:
- LLM plan generation + strict validation,
- dynamic critical-path Monte Carlo forecasting,
- delay-driver intelligence,
- advisory ML risk scoring on top of simulation outputs,
- scenario-based recommendation in a single stakeholder-facing app.

## 11) Scope Boundaries (Intentional)
Included because required for value now:
- planning, risk forecasting, advisory ML scoring, visualization, persistence, CI, demo-ready workflow.

Deferred to avoid scope creep:
- advanced model tuning and production MLOps workflows,
- RAG/agent/MCP stack,
- full cloud infrastructure rollout.

## 12) Handover Checklist (Internal)
- Can each teammate run the app in `mock` mode end-to-end?
- Can each teammate explain P50/P80/delay probability in plain language?
- Can each teammate explain why a task appears as top delay driver?
- Can each teammate explain how ML advisory scores complement Monte Carlo outputs?
- Can each teammate reload history and export outputs?
- Can each teammate run smoke test and describe CI pipeline purpose?
