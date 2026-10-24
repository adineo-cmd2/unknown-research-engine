from app.services import claim_extractor as ce


def test_classify_hedged_kind():
    s = "The long-term effects of this treatment remain unclear and not well understood in adults here."
    assert ce.classify_sentence(s) == "hedged"


def test_extract_finds_further_research():
    text = "Short. Further research is needed to understand sleep mechanisms in adults with sufficient detail here."
    items = ce.extract(text)
    assert any("Further research is needed" in it["sentence"] for it in items)
    hit = [it for it in items if "Further research is needed" in it["sentence"]][0]
    assert hit["kind"] == "hedged"


def test_split_and_methods_and_skip_short():
    assert len(ce.split_sentences("One. Two? Three!")) == 3
    s = "This was a small sample observational study with self-report measures collected over many weeks here."
    assert ce.classify_sentence(s) == "methods"
    items = ce.extract("Tiny. " + s)
    assert all(len(it["sentence"]) >= 40 for it in items)
