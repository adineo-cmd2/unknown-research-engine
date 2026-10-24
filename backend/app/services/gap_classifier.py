import os
import re

STOPWORDS = {
    "about", "after", "again", "among", "because", "before", "between",
    "could", "would", "should", "there", "their", "these", "those",
    "which", "while", "with", "from", "that", "this", "have", "has",
    "were", "been", "also", "into", "more", "most", "other", "such",
    "than", "then", "them", "they", "under", "until", "where", "when",
    "study", "studies", "results", "result", "effect", "effects",
    "using", "used", "shows", "shown", "found",
}

EDGE_QUALIFIERS = [
    "women",
    "children",
    "elderly",
    "low-income",
    "low income",
    "lmic",
    "rare disease",
    "specific subgroup",
    "pregnant",
    "adolescent",
    "infant",
    "rural",
    "indigenous",
    "minority",
]

NEG_RE = re.compile(
    r"\b(not|never|no|n't|cannot|can't|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|none|neither|nor|fail|fails|failed|ineffective)\b",
    re.IGNORECASE,
)
CITATION_RE = re.compile(r"\[\d+\]|et al\.|\(\d{4}")
NUM_RE = re.compile(r"\d+")


def _keywords(sentence: str) -> set[str]:
    words = re.findall(r"[a-z]{5,}", (sentence or "").lower())
    return {w for w in words if w not in STOPWORDS}


def _has_negation(sentence: str) -> bool:
    return bool(NEG_RE.search(sentence or ""))


def _numbers(sentence: str) -> list[str]:
    return NUM_RE.findall(sentence or "")


def _has_citation(sentence: str) -> bool:
    return bool(CITATION_RE.search(sentence or ""))


def _is_edge(sentence: str) -> bool:
    low = (sentence or "").lower()
    return any(q in low for q in EDGE_QUALIFIERS)


def _src_entry(source) -> dict:
    source = source or {}
    if isinstance(source, dict):
        return {
            "title": source.get("title", ""),
            "ref": source.get("ref", ""),
            "mock": bool(source.get("mock", False)),
        }
    return {"title": str(source), "ref": "", "mock": False}


def classify(items: list[dict], topic: str = "") -> list[dict]:
    gaps: list[dict] = []
    for it in items or []:
        sentence = ((it or {}).get("sentence") or "").strip()
        if not sentence:
            continue
        kind = (it or {}).get("kind", "assertive")
        claim = sentence[:300]
        src = _src_entry((it or {}).get("source"))
        low = sentence.lower()
        if "replicat" in low:
            gaps.append({
                "category": "REPLICATION_NEEDED",
                "claim": claim,
                "sources": [src],
                "confidence": 0.75,
                "why_unknown": "authors call for replication",
            })
        elif kind == "methods":
            gaps.append({
                "category": "METHODOLOGICAL_GAP",
                "claim": claim,
                "sources": [src],
                "confidence": 0.65,
                "why_unknown": "weak methodology limits conclusions",
            })
        elif _is_edge(sentence):
            gaps.append({
                "category": "EDGE_CASE_UNEXPLORED",
                "claim": claim,
                "sources": [src],
                "confidence": 0.6,
                "why_unknown": "finding limited to specific population",
            })
        elif kind == "hedged":
            gaps.append({
                "category": "OPEN_QUESTION",
                "claim": claim,
                "sources": [src],
                "confidence": 0.7,
                "why_unknown": "authors explicitly hedge",
            })
        elif kind == "assertive" and not _has_citation(sentence):
            gaps.append({
                "category": "ASSUMED_BUT_UNPROVEN",
                "claim": claim,
                "sources": [src],
                "confidence": 0.5,
                "why_unknown": "asserted without citation",
            })
        # assertive with citation -> established, no gap

    # contested across sources: shared keywords + negation/number clash
    n = len(items or [])
    for i in range(n):
        for j in range(i + 1, n):
            a = (items or [])[i] or {}
            b = (items or [])[j] or {}
            sa, sb = a.get("sentence", ""), b.get("sentence", "")
            if not sa or not sb:
                continue
            src_a, src_b = _src_entry(a.get("source")), _src_entry(b.get("source"))
            if src_a == src_b:
                continue
            if len(_keywords(sa) & _keywords(sb)) < 2:
                continue
            neg_clash = _has_negation(sa) != _has_negation(sb)
            nums_a, nums_b = set(_numbers(sa)), set(_numbers(sb))
            num_clash = bool(nums_a and nums_b and nums_a != nums_b)
            if neg_clash or num_clash:
                gaps.append({
                    "category": "CONTESTED_CLAIM",
                    "claim": sa.strip()[:300],
                    "sources": [src_a, src_b],
                    "confidence": 0.7,
                    "why_unknown": "sources disagree on shared claim",
                })
    return gaps


def classify_llm(items: list[dict], topic: str = "") -> list[dict]:
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        return classify(items, topic)
    return classify(items, topic)
