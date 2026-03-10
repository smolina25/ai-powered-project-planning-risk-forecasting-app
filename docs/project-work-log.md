# Project Work Log

Updated: March 9, 2026

## Purpose

This file summarizes the major project work completed in the repository so the team does not need to rely on chat history to remember what was built, changed, or added.

## 1. Capstone completion work

The repository was expanded and aligned to satisfy the coach-facing capstone requirements more clearly.

Added capstone evidence files:

- `docs/capstone-business-questions.md`
- `docs/technical-eda-summary.md`
- `docs/model-comparison.md`
- `docs/capstone-deliverables-map.md`
- `docs/mvp-test-synthesis.md`
- `docs/public-demo-launch.md`

These documents were created to make the following visible and reviewable:

- business questions and value proposition
- technical EDA summary
- model comparison evidence
- capstone deliverables mapping
- MVP test synthesis
- public demo/deployment steps

## 2. Branding alignment

The project branding was aligned to the final name:

- Brand: `certAIn Project Intelligence`
- Topic: `AI-Powered Project Planning & Risk Forecasting App`

Branding and naming were updated across major app and presentation assets so the repo tells one consistent story.

Key files updated:

- `app.py`
- `README.md`
- `presentation/powerpoint-ready-deck.md`
- `presentation/stakeholder-evidence-pack.md`
- `scripts/generate_pptx.py`
- `docker-compose.yml`
- `.github/workflows/ci.yml`

Presentation export was also renamed to:

- `presentation/certAIn-Project-Intelligence-Capstone.pptx`

## 3. Model training and advisory ML improvements

The original training pipeline was expanded from a minimal baseline/final comparison into a multi-model benchmark.

Training work included:

- benchmarking multiple models
- selecting by cross-validated macro F1
- regenerating the saved model artifact
- regenerating the metrics JSON

Key files:

- `scripts/train_risk_model.py`
- `models/risk_classifier.joblib`
- `models/risk_model_metrics.json`

Selected advisory model:

- `HistGradientBoosting`
- version label: `v1-advisory-multimodel`

Positioning kept intentionally consistent:

- Monte Carlo remains the primary forecasting engine
- ML remains an advisory risk signal, not the main commitment engine

## 4. Presentation and submission packaging

Presentation materials were improved and aligned with the current product story.

Key files:

- `presentation/certAIn-Project-Intelligence-Capstone.pptx`
- `presentation/demo-script.md`
- `presentation/backup-demo.md`
- `presentation/post-presentation-qa-playbook.md`
- `presentation/stakeholder-evidence-pack.md`

This work made the repo more usable for:

- capstone submission
- live demo rehearsal
- stakeholder Q&A
- presentation backup planning

## 5. Repo cleanup

Unnecessary or low-signal artifacts were removed to make the project look more professional and easier to review.

Removed or cleaned:

- `.DS_Store` files
- old notebook exports
- redundant exploratory notebook files
- extra HTML iframe exports
- stale presentation draft artifacts

`.gitignore` was also updated to avoid tracking system clutter and generated noise.

## 6. Streamlit run issue diagnosis

The app startup issue was reproduced and explained.

Main findings:

- `python app.py` with system Python fails if `streamlit` is not installed there
- even with the virtual environment, `python app.py` is not the correct run mode for this app
- the correct command is:

```bash
streamlit run app.py
```

Optional developer hint addressed:

- `watchdog` can be installed for better local reload performance

## 7. Public showcase and website work

Several separate website variants were created and preserved in the repo instead of replacing one another.

### Website Version 1

Folder:

- `web/showcase/`

Purpose:

- public-facing case-study microsite
- portfolio and capstone-story presentation layer

Key files:

- `web/showcase/index.html`
- `web/showcase/styles.css`
- `web/showcase/main.js`
- `web/showcase/config.js`

### Website Version 2

Folder:

- `web/platform-prototype/`

Purpose:

- higher-fidelity interactive product concept
- demo-friendly UI for planning, forecasting, scenarios, and evidence

Key files:

- `web/platform-prototype/index.html`
- `web/platform-prototype/styles.css`
- `web/platform-prototype/main.js`
- `web/platform-prototype/README.md`

### Website Version 3

Folder:

- `web/lovable-style-site/`

Purpose:

- Lovable-inspired multi-page marketing/product site
- polished public-facing surface with complete internal navigation

Pages created:

- `web/lovable-style-site/index.html`
- `web/lovable-style-site/product.html`
- `web/lovable-style-site/ai-forecasting.html`
- `web/lovable-style-site/monte-carlo.html`
- `web/lovable-style-site/pricing.html`
- `web/lovable-style-site/dashboard.html`
- `web/lovable-style-site/about.html`
- `web/lovable-style-site/login.html`

Shared assets:

- `web/lovable-style-site/styles.css`
- `web/lovable-style-site/main.js`
- `web/lovable-style-site/README.md`

## 8. Website version history organization

To keep all website variants organized and presentation-friendly, a version index was created.

Files:

- `web/website-versions/index.html`
- `web/website-versions/styles.css`
- `web/website-versions/README.md`

This catalog now makes it clear that:

- `v1` = case-study showcase
- `v2` = product prototype
- `v3` = lovable-style site

The repo root landing page was updated to redirect to:

- `web/website-versions/`

via:

- `index.html`

## 9. Website build learning materials

To support presentation preparation and real learning, manual build documentation was added for each website version.

### Markdown build guides

- `docs/website-build-guides/README.md`
- `docs/website-build-guides/v1-showcase-manual-build.md`
- `docs/website-build-guides/v2-platform-prototype-manual-build.md`
- `docs/website-build-guides/v3-lovable-style-manual-build.md`

### Notebook learning versions

- `Notebooks/website-versions/README.md`
- `Notebooks/website-versions/v1-showcase-manual-build.ipynb`
- `Notebooks/website-versions/v2-platform-prototype-manual-build.ipynb`
- `Notebooks/website-versions/v3-lovable-style-manual-build.ipynb`

These learning assets now explain:

- what each version is for
- how two teammates could divide the work
- the human step-by-step workflow
- what commands and files a human team would use
- what to say about the work in the presentation
- what questions a coach may ask

## 10. Deployment and sharing work

Initial deployment/share setup work was added for static website sharing.

Files added:

- `.github/workflows/pages.yml`
- `.nojekyll`

Purpose:

- prepare GitHub Pages deployment for static site sharing

Important note:

- GitHub Pages may still require one-time activation in repository settings if the public URL is not yet live

A temporary local tunnel was also used during development for short-term sharing, but that was only a temporary dev link, not a permanent deployment solution.

## 11. Repo notes about planning folder state

At one point, `planning/aipm-product-discovery-planning/` was normalized from a broken gitlink-style state into regular tracked files so the planning content could exist properly in the main repository.

That may still appear as a delete/add style transition in git history depending on the current branch state.

## 12. Verification work completed

At different stages of the work, the following checks were run successfully:

- `python -m compileall -q src app.py scripts tests`
- `python scripts/smoke_test.py`
- `pytest -q`
- local HTTP preview checks for the website folders

Notebook JSON validity for the website learning notebooks was also checked successfully.

## 13. Current website presentation order

Recommended order for showing website variants:

1. `v3` lovable-style site
2. `v2` platform prototype
3. `v1` showcase case-study page

Reason:

- `v3` gives the strongest first impression
- `v2` shows product interaction more directly
- `v1` supports evidence, communication, and portfolio framing

## 14. Remaining open items

These are the main items still external or environment-dependent:

- live Streamlit production URL is not yet committed in the repo
- GitHub Pages may still need final activation/config confirmation
- if the team wants, a similar set of learning notebooks can still be created for:
  - app development
  - EDA workflow
  - model training and comparison
  - deployment process
  - final presentation creation

## 15. Quick navigation

Main version catalog:

- `web/website-versions/index.html`

Main public website candidates:

- `web/showcase/index.html`
- `web/platform-prototype/index.html`
- `web/lovable-style-site/index.html`

Main app:

- `app.py`

Main capstone evidence:

- `docs/capstone-business-questions.md`
- `docs/technical-eda-summary.md`
- `docs/model-comparison.md`
- `docs/capstone-deliverables-map.md`

Main learning materials:

- `docs/website-build-guides/`
- `Notebooks/website-versions/`
