# Public Demo Launch Guide

## Goal
Publish the final capstone in the same artifact pattern used by strong prior cohorts:

1. a branded public-facing case-study page,
2. a live demo URL,
3. the final deck,
4. the GitHub repository.

The repository already contains the case-study page source in `web/showcase/` and the Streamlit demo in `app.py`.

## 1) Deploy the Live Demo

### Recommended: Streamlit Community Cloud
1. Push the repository to GitHub.
2. Create a new Streamlit app using `app.py` as the entrypoint.
3. Set secrets:
   - `GROQ_API_KEY`
   - any optional config overrides from `.env.example`
4. Validate both modes:
   - `mock` mode for presentation reliability
   - `real` mode for one confirmed live run

### Backup
- Use Docker locally: `docker compose up --build`

## 2) Activate the Showcase CTA
After the Streamlit deployment is live, update this field in `web/showcase/config.js`:

```js
demoUrl: "https://your-streamlit-demo-url"
```

The hero button on `web/showcase/index.html` will switch automatically from the deployment guide to the live demo.

## 3) Publish the Showcase Page

### Option A: GitHub Pages
Host the `web/showcase/` folder with GitHub Pages or copy its contents into the Pages branch.

### Option B: Netlify / Vercel / Cloudflare Pages
Deploy the static `web/showcase/` folder directly.

## 4) Final External Links To Share
- Public case-study page
- Live Streamlit demo
- Final slide deck: `presentation/certAIn-Project-Intelligence-Capstone.pptx`
- GitHub repository

## 5) Final QA Checklist
- Showcase loads on desktop and mobile
- Hero CTA opens the correct live demo
- Slide deck download works
- Repo link works
- Demo starts in `mock` mode with no blockers
- Smoke test passes before presentation

## 6) Presenter Recommendation
Use the public showcase page as the opener, then click into the live Streamlit demo, and keep the PowerPoint for the formal presentation segment.
