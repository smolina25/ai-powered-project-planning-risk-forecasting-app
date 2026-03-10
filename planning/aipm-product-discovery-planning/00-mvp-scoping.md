# 00 - MVP Scoping

## Project Context
Product: `certAIn Project Intelligence`  
Category: AI-powered project planning and risk forecasting platform  
Team: 2 people  
Time box: 3.5 weeks  
Assumed kickoff: Monday, March 9, 2026

## MVP Goal
Build a working MVP that lets a project manager or founder describe a project, review an editable AI-generated task plan, and receive an explainable risk forecast with delay probability, P50/P80 dates, and top delay drivers.

## Core Hypothesis to Validate
If project leaders can go from project brief to explainable risk forecast in under 2 minutes, they will trust the output enough to use it in stakeholder conversations more than static timelines or intuition-based status reporting.

Secondary hypotheses:
- Users value `delay probability`, `P80 commitment guidance`, and `top risk drivers` more than generic project-planning features.
- Trust increases when the forecast is explainable and the generated task plan is editable.
- Adoption depends on low input friction, so guided intake matters more than deep workflow automation in the first release.

## One-Paragraph MVP Summary
The MVP for certAIn Project Intelligence is not a full project management suite. It is a focused risk-intelligence layer that turns a short project brief into a validated task plan, runs Monte Carlo forecasting on task dependencies, and returns an executive-ready explanation of delivery risk. This scope follows the strongest signals from discovery and user research: PMs do not want more dashboards, they want quantified confidence before they commit to deadlines. The MVP therefore prioritizes guided intake, forecast quality, explainability, and lightweight feedback capture over integrations, portfolio management, or collaboration features.

## Must-Have MVP Components
1. Guided intake and editable task plan
   - Project brief form in Streamlit
   - AI-generated draft task list
   - Manual edit/validation for tasks, durations, and dependencies
   - One sample-project fallback for demo reliability
2. Forecasting engine
   - Dependency graph creation
   - Monte Carlo simulation
   - Delay probability, mean, P50, P80, and top risk drivers
3. Explainable results and lightweight feedback
   - KPI cards and risk visualization
   - Plain-language explanation of why the plan is risky
   - Copy-ready executive summary
   - Confidence and trust feedback capture

## Should-Have Features
- CSV project-plan upload instead of manual re-entry
- Simple scenario comparison: baseline vs capacity boost
- Downloadable executive-summary export

## Could-Have Features
- Saved run history for same-session retesting
- Expanded sample-project library for demos and testing

## Won't-Have in This MVP
- Jira or Asana integration
- Portfolio dashboard across multiple projects
- Multi-user collaboration and authentication
- Historical forecast accuracy loop against real project outcomes
- Full replacement for Jira, Asana, or MS Project

## Recommended Stack and Workflow
Frontend:
- Streamlit for the intake, analysis, and export experience
- Reuse the implemented information architecture instead of redesigning the flow

Core services:
- Python modules in `src/`
- `NetworkX` for dependency graph logic
- `NumPy` and `Pandas` for simulation and metrics
- `Pydantic` for task-plan validation

AI Layer:
- Use Groq for:
  - project brief -> draft task plan
  - forecast JSON -> plain-language explanation
- Keep both prompts narrow and structured; no model training in the MVP

Data and Analytics:
- SQLite for run history and session persistence
- Notion or Trello for team task tracking
- Use a few sample project plans to test forecast consistency and demo reliability

Delivery workflow:
1. Freeze data contract first
2. Build intake -> validation -> forecast happy path
3. Add explainability only after forecast metrics are stable
4. Reserve the last half week for QA, user testing, and demo hardening

## Individual Learning Goals
- Person A - Backend / AI / Simulation
  Learn to orchestrate LLM prompts, strict schema validation, and Monte Carlo forecasting in shared Python services.
- Person B - Streamlit / PM / UX / Research
  Learn to turn complex risk analytics into a simple Streamlit flow and validate value with lightweight stakeholder testing materials.

## Why This Scope Is Realistic
- It keeps the wedge narrow: `confidence before commitment`
- It matches the strongest user-research signals: explainability, low input friction, and risk visibility
- It reuses what is already technically proven in the prototype: task generation, dependency validation, and Monte Carlo forecasting
- It avoids the biggest scope traps: integrations, portfolio views, and collaboration workflows
