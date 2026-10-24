from app.services import gap_classifier as gc

MOCK_A = {"title": "Mock review 1", "ref": "mock:offline", "mock": True}
MOCK_B = {"title": "Mock review 2", "ref": "mock:offline", "mock": True}


def _item(sentence, kind, source=MOCK_A):
    return {"sentence": sentence, "kind": kind, "source": source}


def test_open_question():
    items = [_item("The efficacy remains unclear and further research is needed to clarify outcomes here.", "hedged")]
    out = gc.classify(items, "sleep")
    assert any(g["category"] == "OPEN_QUESTION" and g["confidence"] == 0.7 for g in out)


def test_methodological_gap():
    items = [_item("This small sample observational study used self-report measures over several weeks here.", "methods")]
    out = gc.classify(items, "sleep")
    assert any(g["category"] == "METHODOLOGICAL_GAP" for g in out)


def test_replication_needed():
    items = [_item("These promising findings await independent replication in larger cohorts studied here.", "assertive")]
    out = gc.classify(items, "sleep")
    assert any(g["category"] == "REPLICATION_NEEDED" and g["confidence"] == 0.75 for g in out)


def test_edge_case():
    items = [_item("The treatment shows strong benefits in women with low-income backgrounds studied over many months here.", "assertive")]
    out = gc.classify(items, "sleep")
    assert any(g["category"] == "EDGE_CASE_UNEXPLORED" for g in out)


def test_assumed_but_unproven():
    items = [_item("This treatment cures insomnia in all adults within two days of administration here.", "assertive")]
    out = gc.classify(items, "sleep")
    found = [g for g in out if g["category"] == "ASSUMED_BUT_UNPROVEN"]
    assert found and found[0]["confidence"] == 0.5
    # citation marker suppresses assumed-but-unproven
    cited = [_item("This treatment cures insomnia in all adults here [12] with broad evidence shown.", "assertive")]
    out2 = gc.classify(cited, "sleep")
    assert not any(g["category"] == "ASSUMED_BUT_UNPROVEN" for g in out2)


def test_contested_across_sources():
    s1 = "Metformin treatment improves glycemic control outcomes in diabetic patients with extended observation here."
    s2 = "Metformin treatment never improves glycemic control outcomes in diabetic patients with extended observation here."
    items = [_item(s1, "assertive", MOCK_A), _item(s2, "assertive", MOCK_B)]
    out = gc.classify(items, "diabetes")
    cont = [g for g in out if g["category"] == "CONTESTED_CLAIM"]
    assert cont, f"expected contested, got {out}"
    assert cont[0]["confidence"] == 0.7
    assert len(cont[0]["sources"]) == 2


def test_mock_passthrough_and_llm_hook():
    items = [_item("The efficacy remains unclear and further research is needed to clarify outcomes here.", "hedged", MOCK_A)]
    out = gc.classify(items, "sleep")
    assert out[0]["sources"][0]["mock"] is True
    assert gc.classify_llm(items, "sleep") == out
