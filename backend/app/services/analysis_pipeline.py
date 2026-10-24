from sqlalchemy.orm import Session

from app.models.gap_record import GapRecord
from app.models.research_session import ResearchSession
from app.models.source_document import SourceDocument
from app.services import claim_extractor, gap_classifier, paper_retriever


def _norm_files(files):
    if not files:
        return None
    norm = []
    for f in files:
        if isinstance(f, dict):
            norm.append(f)
        else:
            filename = getattr(f, "filename", "upload") or "upload"
            raw = getattr(f, "content", None)
            if raw is None and hasattr(f, "read"):
                raw = f.read()
            norm.append({"filename": filename, "content": raw or b""})
    return norm or None


def run_analysis(db: Session, user_id: int, topic: str, files=None) -> dict:
    topic = (topic or "").strip() or "unknown topic"
    session = ResearchSession(user_id=user_id, topic=topic)
    db.add(session)
    db.commit()
    db.refresh(session)

    sources = paper_retriever.retrieve(topic, _norm_files(files))
    doc_ids = {}
    for s in sources:
        doc = SourceDocument(
            session_id=session.id,
            title=(s.get("title") or "")[:500],
            ref=(s.get("ref") or "")[:500],
            mock=bool(s.get("mock", False)),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_ids[(doc.title, doc.ref)] = doc.id

    items = []
    for s in sources:
        src = {"title": s.get("title", ""), "ref": s.get("ref", ""), "mock": bool(s.get("mock", False))}
        for cl in claim_extractor.extract(s.get("text", "")):
            items.append({"sentence": cl["sentence"], "kind": cl["kind"], "source": src})

    gaps = gap_classifier.classify(items, topic)
    for g in gaps:
        first = (g.get("sources") or [{}])[0]
        sid = doc_ids.get((first.get("title", ""), first.get("ref", "")))
        if len(g.get("sources") or []) > 1:
            sid = None
        db.add(GapRecord(
            session_id=session.id,
            source_id=sid,
            category=g.get("category", ""),
            claim=g.get("claim", ""),
            sources=g.get("sources", []),
            confidence=float(g.get("confidence", 0.0)),
            why_unknown=g.get("why_unknown", ""),
            flagged=False,
        ))
    db.commit()
    return {
        "session_id": session.id,
        "gaps_found": len(gaps),
        "mock": any(bool(s.get("mock")) for s in sources),
    }
