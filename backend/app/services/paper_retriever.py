import json
import urllib.parse
import urllib.request

SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def _decode_content(content) -> str:
    if content is None:
        return ""
    if isinstance(content, bytes):
        if content[:4] == b"%PDF":
            try:
                from io import BytesIO

                from pypdf import PdfReader

                reader = PdfReader(BytesIO(content))
                return "\n\n".join((p.extract_text() or "") for p in reader.pages)
            except Exception:
                return ""
        return content.decode("utf-8", errors="ignore")
    return str(content)


def _mock_sources(topic: str) -> list[dict]:
    out = []
    for i in range(3):
        out.append({
            "title": f"Mock review {i + 1} on {topic}",
            "ref": "mock:offline",
            "text": (
                f"Mock review {i + 1} on {topic} finds mixed results. "
                "The effects remain unclear and further research is needed to clarify outcomes here. "
                "Available evidence is limited and inconclusive in this area."
            ),
            "mock": True,
        })
    return out


def _scholar_sources(topic: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": topic,
        "limit": 5,
        "fields": "title,abstract,url",
    })
    req = urllib.request.Request(
        f"{SCHOLAR_URL}?{params}",
        headers={"User-Agent": "04-unknown-research-engine/1.0"},
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
    sources = []
    for paper in (payload or {}).get("data", []):
        title = (paper or {}).get("title") or ""
        abstract = (paper or {}).get("abstract") or ""
        if not title or not abstract:
            continue
        sources.append({
            "title": title,
            "ref": (paper or {}).get("url") or "",
            "text": abstract,
            "mock": False,
        })
    if not sources:
        raise ValueError("no scholar abstracts")
    return sources


def retrieve(topic: str, files=None) -> list[dict]:
    topic = (topic or "").strip() or "unknown topic"
    if files:
        sources = []
        for f in files:
            if isinstance(f, dict):
                filename = f.get("filename", "upload")
                content = f.get("content", "")
            else:
                filename = getattr(f, "filename", "upload") or "upload"
                content = getattr(f, "content", "") or ""
            sources.append({
                "title": filename,
                "ref": f"upload:{filename}",
                "text": _decode_content(content),
                "mock": False,
            })
        return sources
    try:
        return _scholar_sources(topic)
    except Exception:
        return _mock_sources(topic)
