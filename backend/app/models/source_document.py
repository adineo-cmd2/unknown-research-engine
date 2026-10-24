from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("research_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    ref: Mapped[str] = mapped_column(String(500), default="")
    mock: Mapped[bool] = mapped_column(Boolean, default=False)
