from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import boundary, gaps, research, sessions
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

import app.models.user  # noqa: F401 register tables
import app.models.research_session  # noqa: F401
import app.models.source_document  # noqa: F401
import app.models.gap_record  # noqa: F401

Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title="Unknown Research Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4324"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(boundary.router, prefix="/api/research", tags=["research"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(gaps.router, prefix="/api/gaps", tags=["gaps"])
