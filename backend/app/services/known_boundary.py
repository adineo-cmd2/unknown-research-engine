import re

STOPWORDS = {
    "about", "after", "again", "among", "because", "before", "between",
    "could", "would", "should", "there", "their", "these", "those",
    "which", "while", "with", "from", "that", "this", "have", "has",
    "were", "been", "also", "into", "more", "most", "other", "such",
    "than", "then", "them", "they",
}


def _keywords(sentence: str) -> list[str]:
    words = re.findall(r"[a-z]{5,}", (sentence or "").lower())
    return [w for w in words if w not in STOPWORDS]


def _src_of(claim: dict):
    src = (claim or {}).get("source") or {}
    if isinstance(src, dict):
        return src.get("title", "") or src.get("ref", "")
    return str(src)


def build(gaps: list[dict], claims: list[dict]) -> dict:
    established = []
    for c in claims or []:
        if (c or {}).get("kind") != "assertive":
            continue
        sent = ((c or {}).get("sentence") or "").strip()
        if not sent:
            continue
        established.append({
            "statement": sent[:200],
            "source": _src_of(c),
        })
        if len(established) >= 5:
            break

    est_kw = [_keywords(e["statement"]) for e in established]
    unknown = []
    for g in gaps or []:
        claim = (g or {}).get("claim", "")
        kw = _keywords(claim)
        topic = "general"
        for eks in est_kw:
            shared = [w for w in kw if w in eks]
            if shared:
                topic = shared[0]
                break
        unknown.append({
            "statement": claim,
            "category": (g or {}).get("category", ""),
            "why_unknown": (g or {}).get("why_unknown", ""),
            "topic": topic,
        })
    return {"established": established, "unknown": unknown}
