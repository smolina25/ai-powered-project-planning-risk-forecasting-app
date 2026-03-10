# 02 - Now-Next-Future Roadmap

## Roadmap Principle
Sequence work in the same order users experience value:
`intake -> validated plan -> forecast -> explanation -> feedback`

## NOW - Weeks 1 to 3.5
Goal: Prove that explainable probabilistic forecasting changes timeline confidence.

### Week 1 - Intake and Data Contract
Build:
- Freeze the task-plan schema and shared data contracts
- Create the Streamlit intake flow for project brief, target date, and simulation settings
- Add AI-generated draft task plan with manual editing and validation
- Prepare 2-3 sample project plans for QA and demos

Learning objective:
- Can users get to a clean, editable plan without needing Jira integration?

### Week 2 - Forecast Engine
Build:
- Dependency graph builder and DAG validation
- Monte Carlo simulation service
- Delay probability, mean, P50, P80, and top risk driver ranking
- App integration and core analytics tests

Learning objective:
- Are the metrics stable, understandable, and fast enough for classroom demo conditions?

### Week 3 - Results, Explainability, and UX
Build:
- KPI cards, risk charts, and driver ranking in Streamlit
- Plain-language summary explaining the forecast and suggested mitigations
- Copy-ready executive summary
- Validation notes, methodology explanation, and deck-ready evidence pack

Learning objective:
- Does explanation increase trust enough for users to act on the forecast?

### Week 3.5 - Validation and Hardening
Build:
- Run internal rehearsals and package the external session template
- Fix the biggest UX and explanation blockers
- Polish one primary demo flow and one backup flow
- Review outcome metrics and decide what moves into the next release

Learning objective:
- Which signal is strongest: trust, repeat usage, or integration demand?

## NEXT - Month 2
Goal: Reduce adoption friction and improve stakeholder usefulness.

Build next:
- CSV project upload and mapping
- Jira/Asana import exploration
- Expanded scenario comparison
- Better executive export format
- Calibration and prompt tuning based on validation feedback

Why next:
- Research shows workflow friction and trust are the biggest barriers after core value is proven

## FUTURE - Month 3+
Goal: Expand from single-project insight to team-level decision intelligence.

Potential future investments:
- Portfolio dashboard for PMO use cases
- Forecast-vs-actual tracking to improve model calibration
- Alerts when delay probability crosses a threshold
- Collaboration, comments, and role-based access
- Continuous forecast refresh from project-management tools

## Key Dependencies
1. Task schema and validation must be stable before simulation work
2. Forecast payload must be stable before the results UI and explanation layer
3. Validation questions must be defined before target-user sessions
4. Demo reliability matters more than extra features in the final half week

## Roadmap Summary
- NOW: prove `confidence before commitment`
- NEXT: reduce friction and improve trust
- FUTURE: scale from one plan to portfolio intelligence
