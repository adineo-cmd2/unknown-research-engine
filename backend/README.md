# What's Still Unknown Research Engine — backend

Run from `backend/`:

```bash
pip install -r requirements.txt
cp .env.example .env   # optional; works with no keys (mock sources mode)
python3 -m uvicorn app.main:app --port 8004
```

Tests: `python3 -m pytest tests/ -v` (12 tests).
