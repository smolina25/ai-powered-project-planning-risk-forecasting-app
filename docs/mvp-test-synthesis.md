# Internal Validation Notes And External Test Synthesis Template

## Current Evidence In This Repository
This repository contains strong internal validation assets:

- end-to-end smoke test in `scripts/smoke_test.py`,
- unit and integration tests in `tests/`,
- release and demo checklists in `RELEASE_CHECKLIST.md`,
- presentation and backup-demo assets in `presentation/`.

Those assets support reliability and demo readiness. They do not claim completed external user research sessions.

## Internal Rehearsal Findings
- `mock` mode should be the default presentation path because it avoids API-latency risk.
- `P80` needs to be explained before charts, otherwise the audience tends to read only the median.
- The scenario comparison is the clearest action-oriented feature because it turns analytics into a decision.
- The advisory ML tab needs a disclaimer because dataset signal is moderate and class separation is weak.

## Ready-To-Run External Session Plan
- Target participants: PMs, PMO leads, technical founders
- Session length: 20 to 30 minutes
- Test flow:
  1. Enter a project brief
  2. Review and edit the generated plan
  3. Interpret delay probability and P80
  4. Review top delay drivers
  5. Choose a scenario recommendation
  6. Give confidence and clarity feedback

## Suggested Interview Questions
1. Was the generated plan close enough to be useful as a first draft?
2. Could you explain the P80 recommendation to a stakeholder after using the app?
3. Which output was most useful: delay probability, P80, top driver list, or scenario comparison?
4. What would stop you from using this in a real planning conversation?

## KPI Readout Template

| KPI | Definition | Target |
|---|---|---:|
| Time to first forecast | Time from project brief entry to first completed run | < 2 minutes |
| Confidence lift | % of users reporting higher confidence after the forecast | >= 60% |
| Rerun rate | % of sessions that trigger at least one task edit or rerun | >= 50% |
| Summary usefulness | % of users who say they would reuse the executive summary | >= 40% |
| Explanation clarity | % of users who say they can defend the output in a meeting | >= 60% |

## Session Log Template

| Session ID | Persona | Project Type | Confidence Before (1-5) | Confidence After (1-5) | Most Useful Output | Biggest Friction | Would Reuse Summary? |
|---|---|---|---:|---:|---|---|---|
| S1 | | | | | | | |
| S2 | | | | | | | |
| S3 | | | | | | | |
| S4 | | | | | | | |
| S5 | | | | | | | |

## How To Use This File
- Use the internal findings in the capstone Q&A today.
- Fill the session log after each external walkthrough.
- Add a short synthesis paragraph once target-user sessions are completed.
