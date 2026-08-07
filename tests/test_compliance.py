from ada_check.compliance import ada_pre_check


def test_empty_content_penalized():
    r = ada_pre_check({"content": ""}, doc_type="pdf")
    assert r["ada_score"] == 45  # -40 empty -15 missing alt
    assert "empty_content" in r["ada_flags"]
    assert "missing_alt_text" in r["ada_flags"]


def test_good_text_high_score():
    r = ada_pre_check(
        {"content": "Hello accessible document text.", "has_alt_text": True},
        doc_type="pdf",
    )
    assert r["ada_score"] == 100
    assert r["vision_impaired_ready"] is True


def test_each_deduction():
    r = ada_pre_check(
        {
            "content": "some text",
            "has_alt_text": False,
            "reading_order_unclear": True,
            "low_contrast_hint": True,
            "table_without_headers": True,
        },
        doc_type="pdf",
    )
    assert "missing_alt_text" in r["ada_flags"]
    assert "reading_order" in r["ada_flags"]
    assert "contrast" in r["ada_flags"]
    assert "table_headers" in r["ada_flags"]
    assert r["ada_score"] == 100 - 15 - 10 - 10 - 10
