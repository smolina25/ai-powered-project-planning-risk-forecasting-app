# AI-Powered Project Planning & Risk Forecasting App

An AI-powered project planning application for project managers. Input a project description, deadline, and team capacity, and get a structured task plan, workflow graph, Monte Carlo simulation, and delay risk forecast before your project begins.

---

## Overview

This app moves project management from **reactive** to **predictive**. Instead of discovering risks mid-execution, you surface them upfront using AI-generated task decomposition and probabilistic simulation.

---

## Key Features

- **AI Task Generation:** Groq LLM decomposes your project description into structured tasks with durations, dependencies, and risk scores
- **Workflow Graph & Critical Path:** NetworkX DAG with automated critical path detection
- **Monte Carlo Simulation:** 500–5,000 iterations sampling task durations to produce a completion time distribution
- **Delay Probability & Percentiles:** P50, P80, and percentage likelihood of missing your deadline
- **Risk Driver Ranking:** Identifies which tasks most frequently appear on the critical path across simulations
- **Scenario Comparison:** Side-by-side baseline vs. aggressive deadline vs. increased capacity (+15% faster)
- **Executive Summary:** Human-readable forecast statement ready for stakeholder communication
- **Editable Task Plan:** Tweak durations and uncertainty estimates before running simulation

---

## How It Works

1. **User Input:** Enter a project description, deadline (days), and simulation parameters in the sidebar
2. **AI Task Generation:** Groq LLM generates a structured JSON task plan with IDs, dependencies, mean durations, standard deviations, and risk factors
3. **Graph Construction:** asks are built into a directed acyclic graph (DAG); cycles are detected and rejected
4. **Critical Path:** The longest path through the DAG by mean duration is computed and displayed
5. **Monte Carlo Simulation:** For each iteration, task durations are sampled from Normal(mean, std_dev); project completion is computed as the sum of durations along the critical path
6. **Risk Metrics:** Mean, P50, P80, and delay probability are derived from the simulation distribution
7. **Risk Drivers:** asks are ranked by how frequently they appear on the simulated critical path
8. **Scenario Analysis:** Three scenarios are compared: baseline, tightened deadline (−15%), and boosted capacity (+15% faster)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application Framework | Streamlit |
| Language | Python 3.11+ |
| AI / LLM | Groq API (Llama 3.3 70B) |
| Data Validation | Pydantic |
| Graph Modeling | NetworkX |
| Simulation & Analytics | NumPy, Pandas |
| Visualization | Plotly |
| Configuration | python-dotenv |

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd project-sense-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
APP_MODE=real
GROQ_MODEL=llama-3.3-70b-versatile
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com)

> Set `APP_MODE=mock` during development to bypass the API and use a built-in sample plan.

### 5. Run the app

```bash
streamlit run app.py
```

---

## Usage

1. Open the app in your browser (default: `http://localhost:8501`)
2. Enter a project description in the sidebar (e.g. *"Launch a customer portal with authentication, billing, and analytics"*)
3. Set your deadline in days and number of simulation runs
4. Click **Generate & Simulate**
5. Review the four tabs: **Plan Overview**, **Workflow & Critical Path**, **Risk Dashboard**, **Scenario Comparison**

---

## Example Projects to Test

```
"Implement a CRM rollout across 3 teams"
"Plan a marketing campaign launch"
"Build a mobile app MVP with login and payments"
"Migrate legacy database to cloud infrastructure"
```

---

## Deployment

### Streamlit Community Cloud

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `GROQ_API_KEY` in the Secrets section
4. Deploy

### Hugging Face Spaces

1. Create a new Space with the **Streamlit** SDK
2. Push your repo
3. Add `GROQ_API_KEY` in the Space Settings → Repository Secrets

---

## Development Tips

- Use `APP_MODE=mock` to iterate on UI without consuming API tokens
- Keep `max_tasks` at 12 or below for stable JSON output
- Keep simulation runs at or below 2,000 for fast response times
- If the LLM returns malformed JSON, retry — the strict prompt resolves this in most cases

---

## License

MIT
