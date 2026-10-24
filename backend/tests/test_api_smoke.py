"""Smoke: analyse topic-only -> map -> boundary -> flag -> sessions -> delete (no auth, single local user)."""

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app

TOPIC = "sleep deprivation effects on memory consolidation"


def test_api_smoke():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    c = TestClient(app)

    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = c.post("/api/research/analyse", data={"topic": ""})
    assert r.status_code == 400

    r = c.post("/api/research/analyse", data={"topic": TOPIC})
    assert r.status_code == 200
    body = r.json()
    assert {"session_id", "gaps_found", "mock"} <= set(body)
    assert body["gaps_found"] >= 1
    assert body["mock"] is True
    sid = body["session_id"]

    r = c.get(f"/api/sessions/{sid}/map")
    assert r.status_code == 200
    m = r.json()
    assert m["total"] >= 1
    assert m["by_category"]
    assert m["mock"] is True
    first_gap = next(iter(m["by_category"].values()))[0]
    assert {"id", "claim", "category"} <= set(first_gap)
    gid = first_gap["id"]

    r = c.get(f"/api/research/{sid}/known-boundary")
    assert r.status_code == 200
    b = r.json()
    assert len(b["established"]) >= 1
    assert len(b["unknown"]) >= 1

    r = c.patch(f"/api/gaps/{gid}/flag")
    assert r.status_code == 200
    assert r.json() == {"flagged": True}

    r = c.get("/api/sessions")
    assert r.status_code == 200
    items = r.json()
    mine = next(it for it in items if it["id"] == sid)
    assert {"id", "topic", "date", "gap_count"} <= set(mine)
    assert mine["gap_count"] >= 1

    r = c.delete(f"/api/sessions/{sid}")
    assert r.status_code == 200
    r = c.get(f"/api/sessions/{sid}/map")
    assert r.status_code == 404
