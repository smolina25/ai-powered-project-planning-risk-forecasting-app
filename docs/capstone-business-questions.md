# Capstone Business Questions

## Business Problem
Project teams still commit to single-date plans built from deterministic estimates. That creates two business problems:

- delay risk is discovered late, when mitigation is expensive,
- stakeholders cannot see which tasks are most likely to cause schedule failure,
- delivery conversations rely on intuition instead of quantified confidence.

certAIn Project Intelligence addresses that gap by turning a short project brief into a validated plan, a probability-based schedule forecast, and a scenario-backed recommendation.

## Primary Business Questions

| Business Question | Why It Matters | Stakeholders | Decision Enabled | Success Signal |
|---|---|---|---|---|
| Can a PM move from project brief to a validated plan fast enough to use the tool in real planning conversations? | If setup friction is high, the product will not be adopted even if the analytics are good. | Project managers, founders, PMO leads | Whether the tool can replace manual first-pass planning for early-stage schedule conversations | Time to first forecast stays under 2 minutes for a sample project |
| How likely is the current plan to miss the target date, and what is a safer commitment date? | Teams need a risk-aware commitment, not a single optimistic estimate. | PMs, delivery leads, sponsors | Whether to keep the current deadline, renegotiate it, or add mitigation | Delay probability and P80 are clearly interpretable and usable in the presentation |
| Which tasks drive most of the schedule risk? | Mitigation only creates value if it focuses on the real bottlenecks. | PMO leads, project leads, delivery managers | Where to add capacity, reduce scope, or de-risk dependencies | Top delay drivers are ranked and can be explained in plain language |
| Does adding an advisory ML signal improve task-level risk visibility without replacing the simulation engine? | The model should complement decision-making, not create false certainty. | Technical stakeholders, coaches, reviewers | Whether ML belongs in the MVP and how it should be positioned | Model is explicitly advisory, benchmarked against alternatives, and shown alongside Monte Carlo outputs |

## Value Proposition
certAIn Project Intelligence helps teams commit to schedules with evidence instead of gut feel. The product value is:

- faster first-pass planning,
- earlier detection of delivery risk,
- clearer stakeholder communication through P50, P80, delay probability, and top delay drivers,
- better mitigation decisions through scenario comparison.

## Baseline and Target Framing
The baseline workflow is a static plan with one expected completion date and no quantified uncertainty. The target workflow is:

1. Generate a draft plan from a business brief.
2. Validate task structure and dependencies.
3. Forecast completion as a distribution, not a single date.
4. Highlight the bottleneck tasks and scenario tradeoffs.
5. Present a safer commitment recommendation.

## Business Impact Narrative For The Deck
- Before: teams defend deadlines with deterministic plans and subjective status updates.
- After: teams can defend commitments with quantified risk, identified drivers, and scenario-based action options.
