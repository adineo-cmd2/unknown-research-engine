from datetime import datetime

from pydantic import BaseModel


class AnalyseIn(BaseModel):
    topic: str | None = None


class SessionOut(BaseModel):
    id: int
    topic: str
    created_at: datetime

    class Config:
        from_attributes = True


class GapOut(BaseModel):
    id: int
    session_id: int
    source_id: int | None = None
    category: str
    claim: str
    sources: list | None = None
    confidence: float = 0.0
    why_unknown: str = ""
    flagged: bool = False

    class Config:
        from_attributes = True
