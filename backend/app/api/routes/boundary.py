from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.gap_record import GapRecord
from app.models.research_session import ResearchSession
from app.models.source_document import SourceDocument
from app.models.user import User
from app.services import known_boundary

router = APIRouter()


@router.get("/{session_id}/known-boundary")
def get_known_boundary(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = (
        db.query(ResearchSession)
        .filter(ResearchSession.id == session_id, ResearchSession.user_id == user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    gaps = (
        db.query(GapRecord)
        .filter(GapRecord.session_id == session.id)
        .order_by(GapRecord.id)
        .all()
    )
    docs = (
        db.query(SourceDocument)
        .filter(SourceDocument.session_id == session.id)
        .order_by(SourceDocument.id)
        .all()
    )
    gap_dicts = [
        {"claim": g.claim, "category": g.category, "why_unknown": g.why_unknown}
        for g in gaps
    ]
    claims = [
        {
            "sentence": d.title,
            "kind": "assertive",
            "source": {"title": d.title, "ref": d.ref, "mock": d.mock},
        }
        for d in docs
        if (d.title or "").strip()
    ]
    result = known_boundary.build(gap_dicts, claims)
    result["mock"] = any(d.mock for d in docs)
    return result
