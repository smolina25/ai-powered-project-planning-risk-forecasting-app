# Website Versions

This folder organizes the separate website variants built for the project.

## Current Versions

- `v1` case-study site: `../showcase/`
- `v2` product prototype: `../platform-prototype/`
- `v3` lovable-style multi-page site: `../lovable-style-site/`

## Manual Build Documentation

Markdown guides:

- `../../docs/website-build-guides/v1-showcase-manual-build.md`
- `../../docs/website-build-guides/v2-platform-prototype-manual-build.md`
- `../../docs/website-build-guides/v3-lovable-style-manual-build.md`

Notebook versions:

- `../../Notebooks/website-versions/v1-showcase-manual-build.ipynb`
- `../../Notebooks/website-versions/v2-platform-prototype-manual-build.ipynb`
- `../../Notebooks/website-versions/v3-lovable-style-manual-build.ipynb`

## Purpose

Keep each website variant visible in the repository without overwriting the others.

Use this folder as the main entry point when you want to:

- review the website evolution
- choose which version to present
- share one clean index page with collaborators

## Local Preview

From the repository root:

```bash
python -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/web/website-versions/
```
