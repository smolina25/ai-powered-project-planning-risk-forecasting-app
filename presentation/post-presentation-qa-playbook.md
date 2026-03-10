# Post-Presentation Q&A Playbook

Use this as a rapid answer sheet after the demo.
Each item has:
- `Short answer` for immediate response
- `Evidence` so you can point to implementation proof

## 1) What problem does this solve?
Short answer: It turns static project planning into probability-based decision support before execution starts.
Evidence: `app.py` tabs and workflow; `README.md`.

## 2) Why is this better than a normal Gantt plan?
Short answer: A normal plan gives one date; this gives risk distribution, P50/P80, and delay probability.
Evidence: Risk dashboard logic in `src/analytics/metrics.py`, `src/simulation/monte_carlo.py`.

## 3) Why P80 and not only P50?
Short answer: P50 is median; P80 is safer for commitments under uncertainty.
Evidence: Executive summary and metrics in `app.py`, clean notebook `ai-planning-risk-app-02.ipynb`.

## 4) How are tasks generated?
Short answer: LLM generates JSON task plans using strict prompt rules, then schema validation enforces structure.
Evidence: `src/ai/prompt.py`, `src/ai/task_generator.py`, `src/ai/schema.py`.

## 5) What if the LLM output is bad?
Short answer: Validation rejects malformed output; mock mode is available for deterministic demos.
Evidence: Error handling in `src/ai/task_generator.py`; fallback in `app.py`; `presentation/backup-demo.md`.

## 6) How do you ensure dependency correctness?
Short answer: Tasks are validated for sequential IDs and dependency order, then DAG-validated for no cycles.
Evidence: `src/ai/schema.py`, `src/modeling/graph_builder.py`.

## 7) Is the critical path static or dynamic?
Short answer: Dynamic during simulation. The critical path can change each Monte Carlo iteration.
Evidence: `src/simulation/monte_carlo.py`, `src/modeling/critical_path.py`.

## 8) How do you compute delay probability?
Short answer: Fraction of simulated completion times that exceed the chosen deadline.
Evidence: `src/analytics/metrics.py`.

## 9) What are delay drivers?
Short answer: Tasks that most frequently appear on simulated critical paths.
Evidence: `src/analytics/risk_drivers.py`.

## 10) How does scenario recommendation work?
Short answer: Compares baseline, aggressive deadline, and increased capacity; recommends lowest delay probability.
Evidence: `src/analytics/scenarios.py`, scenario tab in `app.py`.

## 11) Is this reproducible?
Short answer: Yes, simulations support fixed random seeds for reproducible runs.
Evidence: seed usage in `src/simulation/monte_carlo.py`; UI input in `app.py`.

## 12) What data storage is used?
Short answer: SQLite for lightweight local persistence of runs, plans, and scenarios.
Evidence: `src/storage/db.py`, `src/storage/repository.py`.

## 13) Can you reload past runs?
Short answer: Yes, previous runs can be listed and reloaded from history.
Evidence: History tab in `app.py`; repository methods.

## 14) What can be exported?
Short answer: Tasks CSV, scenarios CSV, drivers CSV, and full JSON run payload.
Evidence: Export section in `app.py`.

## 15) How reliable is the app for live demo?
Short answer: Mock mode, smoke test, and backup demo flow are prepared for reliability.
Evidence: `scripts/smoke_test.py`, `presentation/backup-demo.md`.

## 16) How is quality checked?
Short answer: Unit tests + smoke test + CI pipeline.
Evidence: `tests/`, `scripts/smoke_test.py`, `.github/workflows/ci.yml`.

## 17) Did you use all course topics?
Short answer: No, we used only what is required for this product to avoid scope creep.
Evidence: explicit scope policy in `PROJECT_WORKFLOW.md` and `ai-planning-risk-app-02.ipynb`.

## 18) How are you using the trained ML model?
Short answer: We use a supervised classifier as an advisory signal at task level; Monte Carlo and scenarios remain primary decision engines.
Evidence: `app.py` (ML Risk Scoring tab), `src/ml/`, `models/risk_classifier.joblib`.

## 19) Why did you choose this advisory model?
Short answer: We benchmarked several model families and selected the one with the best cross-validated macro F1 because the `High` risk minority class matters more than raw accuracy alone.
Evidence: `docs/model-comparison.md`, `models/risk_model_metrics.json`, `scripts/train_risk_model.py`.

## 20) Why no RAG/agents/MCP in this version?
Short answer: Not needed for MVP outcome; omitted intentionally to keep the system reliable and explainable.
Evidence: scope decisions in `PROJECT_WORKFLOW.md`.

## 21) Why no cloud deployment?
Short answer: Local + Streamlit-ready architecture was enough for capstone timeline; cloud is a roadmap item.
Evidence: deployment section in `README.md`; roadmap in deck files.

## 22) What are the main limitations?
Short answer: Quality depends on prompt input; no multi-user auth; single-project focus.
Evidence: `presentation/powerpoint-ready-deck.md`, app scope.

## 23) How is stakeholder value measured?
Short answer: Better commitment quality, earlier risk visibility, and faster planning cycles.
Evidence: value slides in `presentation/powerpoint-ready-deck.md`; KPIs in `PROJECT_WORKFLOW.md`.

## 24) How did the two of you split work?
Short answer: Product/presentation ownership and engineering/analytics ownership, with shared QA and final packaging.
Evidence: `PROJECT_WORKFLOW.md`; clean notebook sections 14-17.

## 25) How did you manage delivery in 4 weeks?
Short answer: Week-based milestones, clear DoR/DoD, and priority on demo reliability and correctness.
Evidence: `PROJECT_WORKFLOW.md`.

## 26) What is the next version?
Short answer: Portfolio dashboard, external PM tool integrations, and collaboration/auth.
Evidence: roadmap in `presentation/powerpoint-ready-deck.md`.

## 27) What should we do if asked something unknown?
Short answer:
- State current implemented scope clearly.
- Give reason for design choice.
- Offer concrete next step for future iteration.

Template:
"In this version we focused on X because it drives immediate decision value.  
We intentionally deferred Y to keep reliability high in 4 weeks.  
Next step would be Z, starting with [specific module/integration]."

## 28) 30-Second Closing Answer
"This project is not just task generation. It is a decision-support system: validate plan quality, quantify schedule risk, identify delay drivers, and compare mitigation scenarios before execution begins."
