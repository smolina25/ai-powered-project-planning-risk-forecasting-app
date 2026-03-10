# V2 Manual Build Guide

## Version
`v2` product prototype in `web/platform-prototype/`

## What this version is for

This version demonstrates the product interaction model.

Use it when you want to show:
- the planning workflow
- KPI and forecast surfaces
- scenario comparison
- what the product would feel like in use

## How two teammates could do this manually

### Teammate A
- study the real app flow in `app.py`
- choose which modules belong in the prototype
- define believable sample scenarios and metrics
- review whether the prototype still reflects the real capstone logic

### Teammate B
- create the visual layout
- implement the dashboard cards and navigation
- wire the scenario switching logic
- test layout and interaction states

### Shared review
- validate the realism of the mock data
- align the prototype with the demo script
- confirm the interface is presentation-safe

## Manual workflow

1. Read the actual product flow first.
   Use:
   - `app.py`
   - `README.md`
   - `presentation/demo-script.md`

2. Decide the interaction modules.
   Example:
   - project brief composer
   - executive forecast
   - distribution chart
   - critical path view
   - scenario lab
   - evidence area

3. Create the files.
   ```bash
   mkdir -p platform-prototype
   touch web/platform-prototype/index.html web/platform-prototype/styles.css web/platform-prototype/main.js
   ```

4. Build the layout and content hierarchy.
   Start with static cards and sections before any JavaScript logic.

5. Create consistent mock data.
   The metrics, scenario summaries, and recommendation states should feel internally coherent.

6. Add interactivity.
   Typical tasks:
   - switch scenarios
   - update KPI values
   - update narrative summaries
   - change badges or recommendation states

7. Test as a demo.
   Ask:
   - can we present from this smoothly?
   - is the data believable?
   - is the UI aligned with the real product story?

## What to say in the presentation

\"We built the platform prototype to show the product experience at a higher level of polish. We first mapped the actual app flow, then selected the most important modules for a live walkthrough. One teammate focused on product logic and scenario realism, while the other built the interface and interaction states.\"

## Human quality checklist

- The prototype feels like a product, not a poster.
- The scenarios are easy to explain.
- The metrics support the spoken demo.
- The interface remains faithful to the real capstone.
- The page is stable enough for presentation use.
