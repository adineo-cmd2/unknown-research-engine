from sqlalchemy import String, Integer, ForeignKey, Float, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GapRecord(Base):
    __tablename__ = "gap_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("research_sessions.id"), index=True)
    source_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("source_documents.id"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(40))
    claim: Mapped[str] = mapped_column(Text)
    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    why_unknown: Mapped[str] = mapped_column(Text, default="")
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
