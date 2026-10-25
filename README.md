# Unknown Research Engine

> Map the boundary between the known and the unknown.

A research engine focused on unknowns: it analyses sources, draws the known-boundary of a field, and produces gap maps showing exactly where the open questions are.

## Features

- Source analysis pipeline
- Known-boundary maps per field
- Gap maps of open research questions
- Analysis reports with citations

## Architecture

| Layer | Stack | Path |
|---|---|---|
| Frontend | Astro (file-based routing) | `frontend/` |
| Backend | FastAPI + SQLAlchemy + Pydantic | `backend/` |
| Tests | pytest | `backend/tests/` |

Frontend routes: `analyse, gap-map, known-boundary`.

## Quick start

Backend (from `backend/`):

```bash
pip install -r requirements.txt
cp .env.example .env        # optional — works with no keys
python3 -m uvicorn app.main:app --port 8001
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Tests: `python3 -m pytest backend/tests/ -v`

## Deployment

The frontend builds to a static bundle and deploys to GitHub Pages on every
push to `main` (`.github/workflows/deploy.yml`):

**https://adineo-cmd2.github.io/unknown-research-engine/**

## Project structure

```
backend/
  app/          FastAPI application
  tests/        pytest suite
frontend/
  src/pages/    Astro routes
```
