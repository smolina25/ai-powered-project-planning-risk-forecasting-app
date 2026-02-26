# Backup Demo Plan (If API Is Slow/Unavailable)

## Trigger Condition
If Groq response latency exceeds demo timing or API errors occur, switch to `APP_MODE=mock` immediately.

## Backup Flow
1. In sidebar, select `mock` mode.
2. Use preloaded project description:
   - `Implement a CRM rollout across 3 teams`
3. Run `Generate & Simulate`.
4. Continue the same storyline:
   - Executive Brief
   - Workflow
   - Risk Dashboard
   - Scenario Lab
   - History & Export

## Message to Stakeholders
- "The demo now uses deterministic mock generation for reliability."
- "Simulation, risk forecasting, and scenario decision logic remain the same."

## Pre-Demo Checklist
- Keep one mock run already saved in history.
- Verify `python scripts/smoke_test.py` passes.
- Keep one exported JSON file ready as a fallback artifact.
