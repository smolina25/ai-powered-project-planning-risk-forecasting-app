# certAIn Project Intelligence

## AI-Powered Project Planning & Risk Forecasting Platform

certAIn Project Intelligence is a stakeholder-ready **Streamlit application** that generates structured project plans using LLMs, builds dependency workflows, runs Monte Carlo forecasting, highlights delay drivers, compares execution scenarios, and stores session history in SQLite.

The platform helps project managers move from **static spreadsheet planning to probabilistic, AI-assisted decision making**.

certAIn is designed as a generalized AI-powered project planning platform. Its core capabilities, including natural-language task generation, dependency graph modeling, critical-path analysis, Monte Carlo forecasting, scenario comparison, and executive reporting, are applicable across many project domains. The current dataset is used only to support the first version of the advisory ML risk model and to provide a concrete demonstration of the platform’s workflow. In other words, the platform itself is domain-agnostic.

---

# Project Motivation

Project planning is commonly performed using spreadsheets and static Gantt charts that fail to capture uncertainty, task dependencies, and real-world execution risks.

certAIn Project Intelligence introduces an AI-assisted planning workflow that combines:

- LLM-generated project structures
- dependency-aware workflow modeling
- Monte Carlo schedule forecasting
- machine-learning-based risk classification

The platform enables project managers to **evaluate uncertainty, compare execution scenarios, and improve planning confidence**.

---

# Core Capabilities

## AI Planning
- AI task decomposition from plain-language project descriptions
- Strict task validation (IDs, dependencies, durations, risk factors)

## Workflow Modeling
- DAG workflow modeling
- Critical-path analysis

## Forecasting
- Dynamic critical-path Monte Carlo simulation
- Risk metrics: Mean completion, P50, P80, delay probability
- Delay-driver ranking from simulated critical-path frequency

## Machine Learning
- Advisory ML risk classification using a trained construction task model

## Decision Support
- Scenario lab comparing:
  - Baseline execution
  - Aggressive deadlines
  - Increased capacity scenarios

## Platform Features
- SQLite session history with reload capability
- CSV / JSON export
- Stakeholder-friendly UI with executive summary outputs

---

# System Architecture

| Layer | Technology |
|------|------------|
| Web Application | Streamlit |
| LLM Planning Engine | Groq (`llama-3.3-70b-versatile`) |
| Data Validation | Pydantic |
| Workflow Graph | NetworkX |
| Simulation Engine | NumPy + Pandas |
| Visualization | Plotly |
| ML Risk Classifier | scikit-learn |
| Model Storage | joblib |
| Persistence | SQLite |

---

<br>

## Dataset Strategy

The capstone uses **three bundled datasets** with different roles in the workflow:
1. Task-level dataset `construction_dataset.csv`: Training the ML model

2. Project-level dataset: `project_portfolio_history.csv`: EDA, understanding delays, simulation context

3. Monitoring dataset `risk_monitoring_snapshot.csv`: Tracking performance, alerts, drift

- **construction_dataset.csv** is the **task-level training dataset** for the first bundled advisory risk classifier in the app. It contains the features and labels used by `scripts/train_risk_model.py` to produce `models/risk_classifier.joblib` and `models/risk_model_metrics.json`. The checked-in file aligns with the Kaggle `Construction Project Management Dataset` listing, whose page describes it as schedule, cost, and risk data from real projects.
- **project_portfolio_history.csv** is the **project-level historical dataset** used for exploratory analysis, project-level benchmarking, forecasting context, and dashboard storytelling.
- **risk_monitoring_snapshot.csv** is the **monitoring dataset** used for confidence tracking, forecast error analysis, and drift-oriented monitoring views.

The three datasets support different parts of the capstone rather than one single end-to-end training table. They support the current demonstration workflow and bundled model artifacts, while the underlying platform remains extensible to additional domains and retrained models. The repository also includes `scripts/generate_capstone_datasets.py`, which can generate synthetic capstone-style datasets for local experimentation, but that utility script should not be treated as the provenance source for the checked-in `construction_dataset.csv`.

---

<br>

# Repository Structure

```
AI-powered-project-planning-risk-forecasting-app/
│
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── construction_dataset.csv
│   ├── project_portfolio_history.csv
│   └── risk_monitoring_snapshot.csv
├── models/
│   ├── risk_classifier.joblib
│   └── risk_model_metrics.json
├── notebooks/
│   ├── 01_business_understanding_and_data_audit.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_baseline_and_model_comparison.ipynb
│   ├── 04_risk_forecasting_dag_monte_carlo.ipynb
│   └── 05_model_monitoring.ipynb
├── presentation/
│   └── certAIn_midterm_presentation.md
├── scripts/
│   ├── generate_capstone_datasets.py
│   ├── generate_final_ds_notebooks.py
│   ├── smoke_test.py
│   └── train_risk_model.py
├── src/
├── tests/
├── web/
├── app1.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

# Environment Setup

This project requires **Python 3.11**.

The same environment supports:

- Jupyter notebooks
- Streamlit application
- ML training pipeline
- automated tests

---

## macOS / Linux

```bash
pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

---

## Windows (PowerShell)

```powershell
pyenv local 3.11.3
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

---

## Windows (Git Bash)

```bash
pyenv local 3.11.3
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

---

# Running the Jupyter Notebooks

Launch Jupyter:

```bash
jupyter notebook
```

Run the notebooks in order:

```
01_business_understanding_and_data_audit.ipynb
02_exploratory_data_analysis.ipynb
03_baseline_and_model_comparison.ipynb
04_risk_forecasting_dag_monte_carlo.ipynb
05_model_monitoring.ipynb
```

These notebooks document the capstone workflow from project-level analysis through forecasting and monitoring:

1. Business understanding  
2. Exploratory portfolio analysis  
3. Exploratory project-level model comparison  
4. Monte Carlo risk forecasting  
5. Model monitoring  

The bundled advisory classifier used by the app is trained separately from `data/construction_dataset.csv` via `scripts/train_risk_model.py`.

---

# Running the Streamlit Application

Start the platform locally:

```bash
streamlit run app1.py
```

The application will open in your browser.

---

# Environment Variables

Configure runtime settings in `.env`.

```
GROQ_API_KEY=
APP_MODE=mock
DEMO_DEFAULT_MODE=mock
GROQ_MODEL=llama-3.3-70b-versatile
APP_BASE_URL=http://localhost:8501
DEFAULT_ITERATIONS=1000
MAX_ITERATIONS=2000
MAX_TASKS=12
MIN_DURATION=0.1
GROQ_TIMEOUT_SECONDS=30
GROQ_MAX_RETRIES=2
SQLITE_DB_PATH=data/app.db
RISK_MODEL_ENABLED=true
RISK_MODEL_PATH=models/risk_classifier.joblib
RISK_MODEL_METRICS_PATH=models/risk_model_metrics.json
RISK_MODEL_VERSION=v1-advisory-multimodel
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SENDER_EMAIL=
SMTP_SENDER_NAME=certAIn
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Notes

- `APP_MODE=mock` is recommended for UI development and demos.
- `APP_MODE=real` requires a valid `GROQ_API_KEY`.
- ML scoring is advisory and should be interpreted alongside Monte Carlo results.
- Footer newsletter confirmations send real emails only when the SMTP settings above are configured.

---

# Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Run the smoke test before demos:

```bash
python scripts/smoke_test.py
```

---

# Training the Risk Model

To retrain the machine learning model:

```bash
python scripts/train_risk_model.py \
--dataset data/construction_dataset.csv \
--model-out models/risk_classifier.joblib \
--metrics-out models/risk_model_metrics.json \
--model-version v1-advisory-multimodel
```

The training pipeline evaluates:

- LogisticRegression
- RandomForest
- ExtraTrees
- HistGradientBoosting

The best model is selected using **cross-validated macro F1 score**.

---

# Deployment

## Streamlit Community Cloud (Primary)

1. Push repository to GitHub  
2. Create a Streamlit app at **share.streamlit.io**  
3. Select `app1.py` as entrypoint  
4. Add secrets such as `GROQ_API_KEY`  
5. Deploy  

---

## Docker Deployment (Optional)

```bash
docker compose up --build
```

Docker ensures reproducible local environments but is optional for Streamlit Cloud deployment.

---

# Presentation Assets

Presentation assets are stored in `presentation/`, including the markdown slide deck and presentation images.

---

# Capstone Evidence

Evidence for the capstone is distributed across:

- `notebooks/` for analysis, forecasting, and monitoring
- `presentation/` for the presentation narrative and visual assets
- `models/risk_model_metrics.json` for the bundled model lineage and metrics
- `tests/` for automated verification of the core application logic

---

# Suggested Demo Projects

Example planning prompts:

- Implement a CRM rollout across three teams
- Plan a marketing campaign launch
- Build a mobile app MVP with authentication and payments

---

# License

MIT
