# certAIn Project Intelligence - PowerPoint Ready Deck (12 Slides)

Use this file to build the final `.pptx` quickly.  
One slide = one section below.

## Slide 1 - Title
certAIn Project Intelligence  
AI-Powered Project Planning & Risk Forecasting App

Subtitle:
From deterministic planning to probability-based decision support.

## Slide 2 - Problem
- Business question: can teams go from a short project brief to a defensible, risk-aware commitment in one planning session?
- Current state: teams commit to single-date plans without quantified uncertainty.
- Impact: delays appear late, mitigation is expensive, and stakeholder updates rely on intuition.

## Slide 3 - Data and EDA
- Dataset: `1300` construction-task rows, `8` numeric features, `3` risk classes.
- Missing values: `0`; duplicate rows: `0`; duplicate task IDs: `0`.
- Class balance: `Low 50.8%`, `Medium 29.0%`, `High 20.2%`.
- Key insight: data is clean, but class separation is weak, so ML must remain advisory.

## Slide 4 - Solution and Architecture
Flow:
1. User project description
2. LLM task generation (or mock fallback)
3. Schema validation (Pydantic)
4. DAG + critical path
5. Monte Carlo simulation
6. Metrics + scenarios + advisory ML + exports

Tech:
- Streamlit, Groq, Pydantic, NetworkX, NumPy/Pandas, Plotly, SQLite

## Slide 5 - Live App Walkthrough
Show the 7 tabs:
- Executive Brief
- Task Plan
- Workflow
- Risk Dashboard
- ML Risk Scoring
- Scenario Lab
- History & Export

## Slide 6 - Forecast Metrics
Explain:
- Mean completion time
- P50 (median outcome)
- P80 (recommended commitment date)
- Delay probability against selected deadline

Decision message:
Use P80 for realistic commitments under uncertainty.

## Slide 7 - Model Comparison
- Baseline: `DummyClassifier` accuracy `0.5077`, macro F1 `0.2245`.
- Compared models: Logistic Regression, Random Forest, Extra Trees, HistGradientBoosting.
- Selected advisory model: `HistGradientBoosting`.
- Selection rule: highest cross-validated macro F1 (`0.3028`).

## Slide 8 - Risk Drivers and Scenario Decision Support
- Critical-path frequency ranking identifies bottleneck tasks.
- Scenarios compared: baseline, aggressive deadline, increased capacity.
- Recommendation rule: choose the scenario with the lowest delay probability.
- Result: analytics becomes a concrete action recommendation, not only a chart.

## Slide 9 - Product & Engineering Quality
- Input validation and graph checks
- Session persistence with SQLite
- Exportable CSV/JSON outputs
- Smoke test + unit test suite
- CI pipeline via GitHub Actions
- Dockerized local reproducibility

## Slide 10 - Team Workflow and Validation
- Week 1: scope + architecture + base app
- Week 2: analytics engine + notebook
- Week 3: scenarios + persistence + test hardening
- Week 4: CI + rehearsal + final packaging

- Include DoR/DoD and ownership split between both teammates.
- Mention internal rehearsal findings and the target-user test template in `docs/mvp-test-synthesis.md`.

## Slide 11 - Responsible AI (Right-Sized for Scope)
- No personal data required for this demo.
- User input transparency: generated plan is editable and reviewable.
- Risk note: LLM outputs can be imperfect; schema validation and manual review are required.
- ML note: classifier is advisory only because dataset signal is moderate.

Why included:
shows practical AI governance without over-scoping the project.

## Slide 12 - Results, Limits, Next Steps
Results:
- Faster planning cycle
- Earlier risk visibility
- Better commitment quality

Current limits:
- Single-project scope
- No multi-user auth or PM-tool integrations
- No SQL-based training-data warehouse in this capstone snapshot

Next steps:
- Portfolio view
- Jira/Asana connectors
- Optional cloud deployment
