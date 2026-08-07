"""ADA / WCAG preliminary scoring model (generic — no PHI vocabulary)."""

from __future__ import annotations

from typing import Any, Dict, List


def ada_pre_check(structured: Dict[str, Any], doc_type: str = "document") -> Dict[str, Any]:
    """Score accessibility readiness; flag issues for remediation.

    Deductions (100 baseline):
      empty_content        -40
      missing_alt_text     -15  (pdf/image/scan without has_alt_text)
      reading_order        -10
      contrast             -10
      table_headers        -10
    """
    flags: List[str] = []
    score = 100

    text = str(structured.get("text_preview", structured.get("content", "")))
    if not text.strip():
        flags.append("empty_content")
        score -= 40

    if doc_type in ("pdf", "image", "scan") and not structured.get("has_alt_text"):
        flags.append("missing_alt_text")
        score -= 15

    if structured.get("reading_order_unclear"):
        flags.append("reading_order")
        score -= 10

    if structured.get("low_contrast_hint"):
        flags.append("contrast")
        score -= 10

    if structured.get("table_without_headers"):
        flags.append("table_headers")
        score -= 10

    return {
        "ada_score": max(0, score),
        "ada_flags": flags,
        "wcag_hints": [
            "Provide heading hierarchy (h1→h2→h3)",
            "Add alt-text for charts and images",
            "Ensure logical reading order for screen readers",
            "Offer plain-language summary for complex tables",
        ]
        if flags
        else [],
        "vision_impaired_ready": score >= 80 and not flags,
        "prepare_only": True,
    }
