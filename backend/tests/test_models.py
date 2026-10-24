from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.gap_record import GapRecord
from app.models.research_session import ResearchSession
from app.models.source_document import SourceDocument
from app.models.user import User


def test_user_session_source_gap_link():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    u = User(email="unknown@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)

    session = ResearchSession(user_id=u.id, topic="What is still unknown about sleep?")
    db.add(session)
    db.commit()
    db.refresh(session)
    assert session.user_id == u.id

    source = SourceDocument(
        session_id=session.id,
        title="Mock sleep study",
        ref="mock-ref-1",
        mock=True,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    assert source.session_id == session.id
    assert source.mock is True

    gap = GapRecord(
        session_id=session.id,
        source_id=source.id,
        category="OPEN_QUESTION",
        claim="Whether deep sleep clears metabolic waste remains open.",
        sources=[{"title": source.title, "ref": source.ref, "mock": True}],
        confidence=0.72,
        why_unknown="Single mock source with hedged wording.",
        flagged=False,
    )
    db.add(gap)
    db.commit()
    db.refresh(gap)
    assert gap.session_id == session.id
    assert gap.source_id == source.id
    assert gap.category == "OPEN_QUESTION"
    assert gap.flagged is False

    # nullable source_id link also works
    gap2 = GapRecord(
        session_id=session.id,
        source_id=None,
        category="CONTESTED_CLAIM",
        claim="Contested claim without a single source.",
        sources=[],
        confidence=0.65,
        why_unknown="Cross-source clash.",
        flagged=False,
    )
    db.add(gap2)
    db.commit()
    db.refresh(gap2)
    assert gap2.source_id is None

    db.close()
