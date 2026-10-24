from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.gap_record import GapRecord
from app.models.research_session import ResearchSession
from app.models.user import User

router = APIRouter()


@router.patch("/{gap_id}/flag")
def flag_gap(
    gap_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    gap = db.query(GapRecord).filter(GapRecord.id == gap_id).first()
    if gap is None:
        raise HTTPException(status_code=404, detail="gap not found")
    session = (
        db.query(ResearchSession)
        .filter(ResearchSession.id == gap.session_id, ResearchSession.user_id == user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="gap not found")
    gap.flagged = True
    db.commit()
    return {"flagged": True}
