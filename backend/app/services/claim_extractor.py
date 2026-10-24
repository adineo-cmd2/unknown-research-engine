import re

HEDGES = [
    "unclear",
    "unknown",
    "uncertain",
    "mixed results",
    "further research is needed",
    "remains to be",
    "limited evidence",
    "controversial",
    "debated",
    "inconclusive",
    "may suggest",
    "could indicate",
    "not well understood",
]

METHODS_WEAK = [
    "small sample",
    "observational",
    "self-report",
    "cross-sectional",
    "no control",
    "single-centre",
    "single-center",
    "retrospective",
]


def split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def classify_sentence(s: str) -> str:
    low = (s or "").lower()
    for pat in METHODS_WEAK:
        if pat in low:
            return "methods"
    for pat in HEDGES:
        if pat in low:
            return "hedged"
    return "assertive"


def extract(text: str) -> list[dict]:
    out = []
    for sent in split_sentences(text):
        if len(sent) < 40:
            continue
        out.append({"sentence": sent, "kind": classify_sentence(sent)})
    return out
