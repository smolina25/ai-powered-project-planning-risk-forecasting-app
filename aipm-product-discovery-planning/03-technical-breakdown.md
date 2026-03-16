# 03 - Technical Work Breakdown

## Technical Framing
This MVP should reuse the strongest proven idea from the prototype:
- structured AI task generation
- strict validation
- Monte Carlo risk forecasting
- explainable output

It should not introduce model training, RAG, or multi-agent complexity.

## Feature 1 - Guided Intake and Editable Task Plan

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | Prompt for `project brief -> task JSON`, plus task schema with fields for ID, task name, duration, dependency, and risk factor | `M` | LLM returns vague or overly large plans; users may not trust generated tasks |
| Backend | FastAPI endpoints: `/api/intake/generate` and `/api/intake/validate` | `M` | Validation edge cases, malformed JSON, inconsistent dependency references |
| Frontend | Lovable intake page, editable task table, input validation states, sample project selector | `M` | Too many required fields creates drop-off; editing UX could become slow |
| Integration | Connect brief form -> generation API -> task-table edit loop -> validation | `S` | Broken handoff between AI output and manual edits |
| Analytics | Track start rate, generation success rate, validation errors, and time to first clean plan | `S` | Missing event definitions makes later analysis weak |

Estimated total: `~5 team days`

## Feature 2 - Forecast Engine and Risk Metrics

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | DAG builder, duration sampling assumptions, dynamic critical-path recomputation, delay-driver logic | `C` | Metrics may be technically correct but hard for users to interpret |
| Backend | FastAPI endpoint: `/api/forecast/run` returning delay probability, mean, P50, P80, and top risk drivers | `M` | Performance issues, cycle-handling bugs, weak error messages |
| Frontend | KPI cards, deadline input, histogram or timeline distribution, top-risk-driver list | `M` | UI may show too much math and reduce trust |
| Integration | Submit validated plan to forecast engine and return results to results page | `S` | Contract mismatch between task-plan payload and forecast response |
| Analytics | Track forecast runs, reruns, chosen deadline, and result-view completion | `S` | Hard to distinguish curiosity clicks from meaningful usage |

Estimated total: `~6 team days`

*Directed Acyclic Graph (DAG):* A DAG Builder is a component that constructs a Directed Acyclic Graph (DAG) representing the task dependency structure of a project.

## Feature 3 - Explainable Results and Lightweight Feedback

| Area | Description | Effort | Risks |
|------|-------------|--------|-------|
| Data / Model | Prompt or template for `forecast JSON -> executive summary + mitigation suggestions`, grounded only in returned metrics | `S` | Generic explanations reduce trust if they are not tied to the actual drivers |
| Backend | Append explanation and event logging to the main forecast flow or expose a very small `/api/forecast/explain` endpoint | `S` | Extra API hop can add latency or complexity for a 2-person team |
| Frontend | Summary panel, methodology notes, copy-ready text action, and short confidence/trust survey | `M` | Users may still not understand why the score is trustworthy |
| Integration | Bind summary and feedback logging to the same forecast session | `S` | Summary and metrics can drift if not tied to the same payload |
| Analytics | Confidence lift, explanation clarity rating, rerun tracking, and summary usage | `S` | Too much instrumentation can slow the team down |

Estimated total: `~4 team days`

## Technical Dependencies
1. Task schema must be finalized before prompt and validation work can stabilize
2. Forecast engine depends on validated task plans and DAG checks
3. Explanation layer depends on a stable forecast response contract
4. Feedback instrumentation depends on the final results flow and event naming

## Main Risks and Mitigations
- Risk: Users do not trust AI-generated task plans
  Mitigation: make the task table editable and show validation transparently
- Risk: Forecast output feels too technical
  Mitigation: lead with delay probability, P80, and top 3 drivers before charts
- Risk: Input friction blocks adoption
  Mitigation: keep the first flow short and add sample projects for fast testing
- Risk: LLM failures break the demo
  Mitigation: support a fixed sample-project fallback and cache example responses

## Feasibility Summary
- Must-have build effort: `~15 team days`
- Recommended integration/QA buffer: `~3 team days`

This fits the course guideline for a 2-person, 3.5-week MVP if scope remains limited to one clean end-to-end flow.
