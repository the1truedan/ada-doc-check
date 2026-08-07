"""Pass/fail accessibility gate combining triage + ADA score (prepare-only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ada_check.compliance import ada_pre_check
from ada_check.triage import extract_text_simple, needs_ocr


def accessibility_gate(
    *,
    path: Optional[Union[str, Path]] = None,
    content: Optional[str] = None,
    doc_type: str = "document",
    min_score: float = 50.0,
    min_chars: int = 200,
) -> Dict[str, Any]:
    """Run triage + ADA score. Never claims certification."""
    text = content or ""
    triage: Optional[Dict[str, Any]] = None
    p = Path(path).expanduser() if path else None

    if p is not None:
        triage = needs_ocr(p, min_chars=min_chars)
        if triage.get("decidable") and not text:
            extracted = extract_text_simple(p)
            if extracted.get("status") == "ok" and not (
                extracted.get("engine") == "binary_sample"
            ):
                text = extracted.get("text") or ""
        if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            doc_type = "pdf" if p.suffix.lower() == ".pdf" else "image"

    score = ada_pre_check(
        {
            "content": text,
            "has_alt_text": bool(content) or (triage or {}).get("accessible_as_is"),
        },
        doc_type=doc_type,
    )

    flags = list(score.get("ada_flags") or [])
    if triage is not None:
        if triage.get("decidable") is False:
            flags.append("triage_undecidable")
        elif triage.get("needs_ocr"):
            flags.append("needs_ocr")

    ok = score["ada_score"] >= min_score and "empty_content" not in flags
    if triage and triage.get("accessible_as_is") is False:
        ok = False

    return {
        "ok": ok,
        "path": str(p) if p else None,
        "ada_score": score["ada_score"],
        "ada_flags": flags,
        "wcag_hints": score.get("wcag_hints") or [],
        "triage": triage,
        "prepare_only": True,
        "note": "First-pass triage only — not a Section 508 / WCAG certification.",
    }
