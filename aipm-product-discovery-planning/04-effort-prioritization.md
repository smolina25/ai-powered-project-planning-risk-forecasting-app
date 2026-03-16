# 04 - Effort-Informed Prioritization

## Prioritization Logic
We are optimizing for:
1. User value proof
2. Trust and explainability
3. Buildability in 3.5 weeks
4. Reuse of prototype logic already proven in the capstone

Because this is a 2-person team, the scope has to stay inside the course rule of `<=15 team days` plus a `20%` buffer. The committed build scope below is `15 team days`, with `3 days` reserved for integration, testing, and fixes.

## Prioritized Feature Set

| Feature | Estimated Effort | Priority | Reason |
|---------|------------------|----------|--------|
| Guided intake + editable AI-generated task plan | 5 days |  MUST HAVE | Reduces setup friction and makes the product feel immediately useful |
| Forecast engine: delay probability, P50/P80, top risk drivers | 6 days |  MUST HAVE | Core value proof; without this there is no differentiated product |
| Explainable results + confidence feedback | 4 days |  MUST HAVE | User research says trust depends on explainability, not extra PM features |
| CSV upload | 3 days |  SHOULD HAVE | Improves workflow fit but is not required to prove value |
| Simple scenario comparison | 3 days |  SHOULD HAVE | Valuable for founders and PMs, but secondary to core forecast trust |
| Downloadable summary export | 2 days |  COULD HAVE | Helpful for stakeholder communication, but copy-ready text is enough for the MVP |
| Expanded sample project templates | 1 day |  COULD HAVE | Useful for demos and testing, but not essential if one clean example exists |
| Jira / Asana integration | 6+ days |  WON'T HAVE | High adoption value but too large for the first MVP sprint |
| Portfolio dashboard | 6+ days |  WON'T HAVE | Strong PMO use case, but not needed to validate single-project wedge |
| Auth, collaboration, and sharing | 5+ days |  WON'T HAVE | Infrastructure-heavy and not tied to the core hypothesis |

## Capacity Check
Committed MVP build:
- Guided intake + editable AI task plan: `5`
- Forecast engine + risk metrics: `6`
- Explainable results + confidence feedback: `4`

Committed total: `15 team days`

Reserved buffer:
- Integration and QA: `1.5 days`
- User testing and issue fixing: `1.5 days`

Total planned: `18 team days`

This is realistic for a 2-person team over 3.5 weeks because the committed build remains narrow and the buffer is protected instead of being silently consumed by optional features.

## Outcome Goal -> Epic -> Deliverables

| Outcome Goal | Epic | Deliverables |
|--------------|------|--------------|
| Improve timeline decision confidence with explainable risk forecasting | Epic A - Guided intake | Brief form, task generation prompt, validation API, editable task table |
| Improve timeline decision confidence with explainable risk forecasting | Epic B - Forecast engine | DAG builder, Monte Carlo service, metrics endpoint, risk dashboard |
| Improve timeline decision confidence with explainable risk forecasting | Epic C - Explainable results and feedback | Summary service or template, mitigation hints, confidence survey, success-metrics sheet |

## Trade-Off Decisions
- We are building a `risk intelligence layer`, not a planning suite replacement
- We defer integrations until we prove users value the forecast itself
- We keep one project flow excellent instead of adding half-finished advanced features
- We treat user trust as a product requirement, not a post-launch concern
