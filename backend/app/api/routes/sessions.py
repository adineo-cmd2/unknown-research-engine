from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.gap_record import GapRecord
from app.models.research_session import ResearchSession
from app.models.source_document import SourceDocument
from app.models.user import User

router = APIRouter()


def _own_session(db: Session, user_id: int, session_id: int) -> ResearchSession:
    session = (
        db.query(ResearchSession)
        .filter(ResearchSession.id == session_id, ResearchSession.user_id == user_id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


def _gap_dict(g: GapRecord) -> dict:
    return {
        "id": g.id,
        "category": g.category,
        "claim": g.claim,
        "sources": g.sources,
        "confidence": g.confidence,
        "why_unknown": g.why_unknown,
        "flagged": g.flagged,
    }


@router.get("")
def list_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sessions = (
        db.query(ResearchSession)
        .filter(ResearchSession.user_id == user.id)
        .order_by(ResearchSession.id)
        .all()
    )
    out = []
    for s in sessions:
        out.append(
            {
                "id": s.id,
                "topic": s.topic,
                "date": s.created_at.isoformat() if s.created_at else None,
                "gap_count": db.query(GapRecord)
                .filter(GapRecord.session_id == s.id)
                .count(),
            }
        )
    return out


@router.get("/{session_id}/map")
def session_map(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = _own_session(db, user.id, session_id)
    gaps = (
        db.query(GapRecord)
        .filter(GapRecord.session_id == session.id)
        .order_by(GapRecord.id)
        .all()
    )
    by_category: dict[str, list] = {}
    mock = False
    for g in gaps:
        by_category.setdefault(g.category, []).append(_gap_dict(g))
        for src in g.sources or []:
            if isinstance(src, dict) and src.get("mock"):
                mock = True
    return {
        "topic": session.topic,
        "by_category": by_category,
        "total": len(gaps),
        "mock": mock,
    }


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = _own_session(db, user.id, session_id)
    db.query(GapRecord).filter(GapRecord.session_id == session.id).delete(
        synchronize_session=False
    )
    db.query(SourceDocument).filter(SourceDocument.session_id == session.id).delete(
        synchronize_session=False
    )
    db.delete(session)
    db.commit()
    return {"ok": True}
