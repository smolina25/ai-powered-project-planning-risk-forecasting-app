# Stakeholder Deck: AI Project Planning & Risk Forecasting

## Slide 1 - Problem
Traditional project planning is deterministic and often misses uncertainty, causing schedule slips discovered too late.

## Slide 2 - Solution Overview
ProjectSense AI generates structured plans, models dependencies, simulates uncertainty, and forecasts delay risk before execution starts.

## Slide 3 - Architecture
- Groq LLM for task plan generation
- Pydantic for strict schema validation
- NetworkX DAG for workflow modeling
- Monte Carlo engine for timeline forecasting
- SQLite for session persistence
- Streamlit + Plotly for stakeholder UI

## Slide 4 - Data Flow
1. Project description input
2. AI plan generation
3. Validation and DAG construction
4. Monte Carlo simulation with dynamic critical path
5. Metrics and risk-driver extraction
6. Scenario comparison and decision recommendation

## Slide 5 - Core UI Walkthrough
Demo the 6 tabs:
- Executive Brief
- Task Plan
- Workflow
- Risk Dashboard
- Scenario Lab
- History & Export

## Slide 6 - Forecast Metrics
Explain:
- Mean completion
- P50 (median)
- P80 (recommended commitment date)
- Delay probability vs chosen deadline

## Slide 7 - Risk Driver Intelligence
Show critical-path frequency ranking and explain how mitigation on top drivers reduces schedule risk.

## Slide 8 - Scenario Decision Support
Compare baseline, aggressive deadline, and increased capacity. Highlight which option minimizes delay probability.

## Slide 9 - Business Value and Limits
Value:
- Early risk visibility
- Better deadline commitments
- Faster planning cycles

Current limits:
- LLM plan quality depends on prompt input
- Uses lightweight persistence and no multi-user auth in this version

## Slide 10 - Roadmap
- Real-time project updates
- Multi-project portfolio dashboard
- User authentication and team collaboration
- Enterprise connectors (Jira/MS Project/Asana)
