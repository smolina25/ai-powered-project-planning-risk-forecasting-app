# V1 Manual Build Guide

## Version
`v1` case-study showcase in `web/showcase/`

## What this version is for

This version is the public narrative layer of the capstone.

Use it when you want to explain:
- the business problem
- the value proposition
- the evidence behind the project
- the deliverables in one clean page

It is not meant to replace the product UI. It is meant to package the capstone clearly.

## How two teammates could do this manually

### Teammate A
- extract the business framing from the capstone docs
- decide the section order
- write the copy
- check that the story is accurate and stakeholder-friendly

### Teammate B
- build the HTML page structure
- create the CSS system
- wire the buttons and config-driven links
- test the page on desktop and mobile

### Shared review
- confirm the page supports the capstone requirements
- confirm all linked evidence is real and present in the repo
- remove any language that overclaims outcomes

## Manual workflow

1. Collect the source material.
   Use:
   - `docs/capstone-business-questions.md`
   - `docs/technical-eda-summary.md`
   - `docs/model-comparison.md`
   - `presentation/certAIn-Project-Intelligence-Capstone.pptx`
   - `README.md`

2. Decide the content architecture.
   A strong order is:
   - hero
   - problem
   - solution
   - evidence
   - deliverables
   - call to action

3. Create the files.
   ```bash
   mkdir -p showcase
   touch web/showcase/index.html web/showcase/styles.css web/showcase/main.js web/showcase/config.js
   ```

4. Build the HTML first.
   Focus only on structure and section order before styling.

5. Build the CSS system.s
   Define:
   - color palette
   - typography
   - spacing
   - content widths
   - button and card styles

6. Add lightweight JavaScript.
   Use `config.js` so links can be updated without rewriting the page.

7. Test locally.
   ```bash
   python -m http.server 8000
   ```
   Open:
   `http://127.0.0.1:8000/web/showcase/`

8. Review the page against the coach requirements.
   This version directly supports stakeholder communication and project framing.

## What to say in the presentation

\"We created the showcase site as the public-facing case-study layer of the capstone. We started from our business questions, technical evidence, and presentation material, then translated them into a clear narrative page. One teammate focused on the story and content structure, while the other implemented the frontend and dynamic links.\"

## Human quality checklist

- The problem is understandable within seconds.
- The evidence is linked clearly.
- The page looks professional on desktop and mobile.
- The wording works for non-technical readers.
- The page supports the presentation instead of duplicating it poorly.
