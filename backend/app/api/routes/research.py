from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.analysis_pipeline import run_analysis

router = APIRouter()


def _decode_upload(filename: str, raw: bytes) -> str:
    if filename.lower().endswith(".pdf") or raw[:4] == b"%PDF":
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(raw))
            return "\n\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            return ""
    return raw.decode("utf-8", errors="ignore")


@router.post("/analyse")
async def analyse(
    topic: str = Form(""),
    files: list[UploadFile] | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    uploads = []
    for f in files or []:
        raw = await f.read()
        uploads.append(
            {"filename": f.filename or "upload", "content": _decode_upload(f.filename or "", raw)}
        )
    if not (topic or "").strip() and not uploads:
        raise HTTPException(status_code=400, detail="topic or files required")
    return run_analysis(db, user.id, topic, uploads or None)
