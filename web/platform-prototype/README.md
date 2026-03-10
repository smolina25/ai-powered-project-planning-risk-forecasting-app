# certAIn Project Intelligence Platform Prototype

This folder contains a standalone polished web prototype for the `certAIn Project Intelligence` capstone demo.

It is intentionally isolated from the main Streamlit app so you can present:

- the production capstone app in `app.py`
- the public showcase in `web/showcase/`
- this higher-fidelity product concept in `web/platform-prototype/`

## What It Is

A static frontend prototype inspired by modern product demos:

- AI project brief composer
- executive forecast command center
- Monte Carlo-style distribution panel
- critical path and task risk views
- scenario lab comparison
- stakeholder evidence links

## What It Is Not

- It does not replace the Streamlit app
- It does not call your Python backend
- It does not overwrite any existing repo files

## Run Locally

From the repository root:

```bash
python -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/web/platform-prototype/
```

## Presentation Use

Use this when you want a more polished product-story walkthrough before switching to the live Streamlit demo.
