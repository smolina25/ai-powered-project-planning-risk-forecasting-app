# Website Versions

This folder organizes the separate website variants built for the project.

## Current Versions

- `v1` case-study site: `../showcase/`
- `v2` product prototype: `../platform-prototype/`
- `v3` lovable-style multi-page site: `../lovable-style-site/`

## Supporting Files

Each version is self-contained in its folder. Supporting repo files you may want alongside them:

- `../showcase/config.js`
- `../platform-prototype/README.md`
- `../lovable-style-site/README.md`
- `../../presentation/certAIn_midterm_presentation.md`

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
