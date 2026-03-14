# certAIn Project Intelligence

## AI-Powered Project Planning & Risk Forecasting Platform

certAIn Project Intelligence is a stakeholder-ready **Streamlit application** that generates structured project plans using LLMs, builds dependency workflows, runs Monte Carlo forecasting, highlights delay drivers, compares execution scenarios, and stores session history in SQLite.

The platform helps project managers move from **static spreadsheet planning to probabilistic, AI-assisted decision making**.

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

# Dataset Note

The datasets used in this capstone are **synthetic but designed to reflect realistic project planning characteristics**, including schedule delays, cost overruns, resource allocation, and stakeholder alignment.

Synthetic data was used because real project portfolio data is typically **confidential and not publicly available**.

The goal of this capstone is to demonstrate the **analytical workflow, modeling approach, and platform design**, rather than represent a specific organization’s internal project data.

**project_portfolio_history.csv** is used for **model training and analysis dataset**. It contains **historical project data**, which represents past project outcomes. It answers: **What project characteristics lead to higher risk or delays?** 

**risk_monitoring_snapshot.csv** is used for **post-deployment model monitoring dataset**. It represents **new incoming projects after the model has already been deployed**. It answers: **Is the deployed model still reliable on new projects?**

---

<br>

# Repository Structure

```
AI-powered-project-planning-risk-forecasting-app/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── pages.yml
│
├── docs/
│   ├── capstone-business-questions.md
│   ├── technical-eda-summary.md
│   ├── model-comparison.md
│   ├── capstone-deliverables-map.md
│   └── mvp-test-synthesis.md
│
├── notebooks/
│   ├── 01_business_understanding_and_data_audit.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_baseline_and_model_comparison.ipynb
│   ├── 04_risk_forecasting_simulation.ipynb
│   └── 05_model_monitoring.ipynb
│
├── scripts/
│   ├── smoke_test.py
│   └── train_risk_model.py
│
├── tests/
│   ├── test_schema.py
│   ├── test_graph_builder.py
│   └── test_ml_predictor.py
│
├── src/
│   ├── modeling/
│   ├── simulation/
│   ├── analytics/
│   └── utils/
│
├── models/
│   └── risk_classifier.joblib
│
├── data/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
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
04_risk_forecasting_simulation.ipynb
05_model_monitoring.ipynb
```

These notebooks demonstrate the **full ML lifecycle required for the capstone**:

1. Business understanding  
2. Exploratory data analysis  
3. Model comparison  
4. Monte Carlo risk forecasting  
5. Model monitoring  

---

# Running the Streamlit Application

Start the platform locally:

```bash
streamlit run app.py
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
```

### Notes

- `APP_MODE=mock` is recommended for UI development and demos.
- `APP_MODE=real` requires a valid `GROQ_API_KEY`.
- ML scoring is advisory and should be interpreted alongside Monte Carlo results.

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
3. Select `app.py` as entrypoint  
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

Located in:

```
presentation/
```

Includes:

- demo script
- backup demo
- final presentation slides
- stakeholder evidence pack

---

# Capstone Evidence

The `docs/` folder contains artifacts used for evaluation:

- business questions
- technical EDA summary
- model comparison
- deliverables mapping
- MVP testing synthesis

---

# Suggested Demo Projects

Example planning prompts:

- Implement a CRM rollout across three teams
- Plan a marketing campaign launch
- Build a mobile app MVP with authentication and payments

---

# License

MIT