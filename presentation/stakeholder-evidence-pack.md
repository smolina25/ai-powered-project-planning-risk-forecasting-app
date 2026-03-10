# Stakeholder Evidence Pack

## 1) Deployment Proof
- Primary app URL: not committed in this repository snapshot; deploy via the `README.md` Streamlit instructions when a public URL is needed
- Backup run method: `docker compose up --build`
- Build date: `2026-03-09`
- Public case-study page source: `web/showcase/index.html`

## 2) Technical Proof Points
- App entrypoint: `app.py`
- Monte Carlo simulation: `src/simulation/monte_carlo.py`
- Delay drivers + scenarios: `src/analytics/`
- Advisory ML scoring: `src/ml/`
- Persistence and history: `src/storage/`

## 3) Reliability Evidence
- Smoke test command:
  - `python scripts/smoke_test.py`
- CI workflow:
  - `.github/workflows/ci.yml`
- Mock-mode fallback:
  - default with `DEMO_DEFAULT_MODE=mock`

## 4) Model Governance Snapshot
- Training script: `scripts/train_risk_model.py`
- Model artifact: `models/risk_classifier.joblib`
- Metadata: `models/risk_model_metrics.json`
- Comparison report: `docs/model-comparison.md`
- Version field: `RISK_MODEL_VERSION=v1-advisory-multimodel`
- Positioning: advisory signal, not sole decision engine

## 5) Demonstration Evidence
- Script: `presentation/demo-script.md`
- Deck: `presentation/powerpoint-ready-deck.md`
- Final deck export: `presentation/certAIn-Project-Intelligence-Capstone.pptx`
- Q&A playbook: `presentation/post-presentation-qa-playbook.md`
- Backup flow: `presentation/backup-demo.md`
- Business framing: `docs/capstone-business-questions.md`
- EDA summary: `docs/technical-eda-summary.md`
- Deliverables map: `docs/capstone-deliverables-map.md`

## 6) Known Limitations (Transparent)
- LLM quality depends on input prompt quality.
- Advisory classifier performance is moderate and should be interpreted with simulation metrics.
- No multi-user auth or enterprise RBAC in current release.
