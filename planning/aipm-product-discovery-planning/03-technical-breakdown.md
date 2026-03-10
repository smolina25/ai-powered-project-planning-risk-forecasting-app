# 03 - Technical Work Breakdown

## Technical Framing
This MVP reuses the strongest proven capstone idea:
- structured AI task generation,
- strict validation,
- Monte Carlo risk forecasting,
- explainable stakeholder output.

It intentionally avoids extra architectural layers that are not needed for the capstone, such as a separate FastAPI service, RAG, or multi-agent orchestration.

## Feature 1 - Guided Intake and Editable Task Plan

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | Prompt for `project brief -> task JSON`, plus task schema with fields for ID, task name, duration, dependency, and risk factor | `M` | LLM returns vague or overly large plans; users may not trust generated tasks |
| Core logic | `src/ai/task_generator.py` and `src/ai/schema.py` validate and normalize generated plans before analysis | `M` | Validation edge cases, malformed JSON, inconsistent dependency references |
| UI | `app.py` Streamlit intake controls and editable task table | `M` | Too many required fields creates drop-off; editing UX could become slow |
| Integration | Connect brief form -> generation -> edit loop -> validation -> saved run | `S` | Broken handoff between AI output and manual edits |
| Analytics | Track saved runs in SQLite and maintain sample projects for demos | `S` | Weak demo traceability if run history is not persisted |

Estimated total: `~5 team days`

## Feature 2 - Forecast Engine and Risk Metrics

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | DAG builder, duration sampling assumptions, dynamic critical-path recomputation, delay-driver logic | `C` | Metrics may be technically correct but hard for users to interpret |
| Core logic | `src/modeling/`, `src/simulation/`, and `src/analytics/` return delay probability, mean, P50, P80, and driver ranking | `M` | Performance issues, cycle-handling bugs, weak error messages |
| UI | KPI cards, deadline input, histogram, scenario comparison, and top-risk-driver list in Streamlit | `M` | UI may show too much math and reduce trust |
| Integration | Submit validated plan to forecasting modules and return results to the tabs in `app.py` | `S` | Contract mismatch between task-plan payload and forecast output |
| Analytics | Persist simulation runs and scenario outputs in SQLite for reload and export | `S` | Hard to audit results if history storage is incomplete |

Estimated total: `~6 team days`

## Feature 3 - Explainable Results and Validation Package

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | Executive summary template grounded in delay probability, P80, and top drivers | `S` | Generic explanations reduce trust if they are not tied to actual outputs |
| Core logic | Summary generation in `app.py`, advisory ML scoring in `src/ml/`, and model benchmarking in `scripts/train_risk_model.py` | `S` | Extra analytics may be mistaken for the primary decision engine |
| UI | Executive summary panel, methodology notes, export actions, and advisory ML disclaimer | `M` | Users may still not understand why the score is trustworthy |
| Integration | Bind app outputs to presentation assets, evidence pack, and capstone docs | `S` | Deck and repo can drift if artifacts are not updated together |
| Analytics | Package EDA, model comparison, and validation-readout docs in `docs/` | `S` | Missing evidence makes the capstone look incomplete even if the app works |

Estimated total: `~4 team days`

## Technical Dependencies
1. Task schema must be finalized before prompt and validation work can stabilize.
2. Forecast engine depends on validated task plans and DAG checks.
3. Executive summary and presentation assets depend on a stable forecast output contract.
4. Capstone evidence docs depend on stable model metrics and EDA findings.

## Main Risks and Mitigations
- Risk: users do not trust AI-generated task plans.
  Mitigation: make the task table editable and show validation transparently.
- Risk: forecast output feels too technical.
  Mitigation: lead with delay probability, P80, and top delay drivers before charts.
- Risk: demo reliability breaks due to API dependency.
  Mitigation: keep `mock` mode and sample-project fallback ready.
- Risk: the advisory model is overinterpreted.
  Mitigation: benchmark multiple models, select by macro F1, and keep Monte Carlo as the primary engine.

## Feasibility Summary
- Must-have build effort: `~15 team days`
- Recommended integration and QA buffer: `~3 team days`

This fits the course guideline for a 2-person, 3.5-week MVP because the build focuses on one clean end-to-end workflow and packages the capstone evidence in the repository.
