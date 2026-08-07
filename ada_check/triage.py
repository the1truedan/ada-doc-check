"""Text-layer triage: needs OCR vs accessible as-is vs undecidable.

Fails closed: missing files and binary-as-text are never scored as fully accessible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def looks_like_binary(text: str, *, sample: int = 2000) -> bool:
    """True when 'text' is really undecoded binary rather than document text."""
    if not text:
        return False
    head = text[:sample]
    if "\x00" in head or "\ufffd" in head:
        return True
    printable = sum(1 for c in head if c.isprintable() or c in "\n\r\t")
    return (printable / len(head)) < 0.85


def extract_text_simple(path: Path) -> Dict[str, Any]:
    """Best-effort text extract without monorepo deps.

    - .txt/.md: utf-8 read
    - .pdf: optional pypdf if installed
    - images/other: binary sample for triage (never claim accessible text layer)
    """
    p = Path(path)
    if not p.is_file():
        return {"status": "error", "error": "file not found", "text": None, "engine": None}

    suffix = p.suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".html", ".htm"}:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"status": "error", "error": str(exc), "text": None, "engine": None}
        return {"status": "ok", "text": text, "engine": "plain_text", "chars": len(text)}

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            # Without pypdf we cannot claim a text layer — undecidable at caller
            return {
                "status": "unavailable",
                "text": None,
                "engine": None,
                "error": "pypdf not installed (pip install ada-doc-check[pdf])",
            }
        try:
            reader = PdfReader(str(p))
            parts: List[str] = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            text = "\n".join(parts)
            return {"status": "ok", "text": text, "engine": "pypdf", "chars": len(text)}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "error": f"{type(exc).__name__}: {exc}", "text": None, "engine": "pypdf"}

    # image / unknown: read raw bytes as "text" only to feed binary detector
    try:
        raw = p.read_bytes()[:8000]
    except OSError as exc:
        return {"status": "error", "error": str(exc), "text": None, "engine": None}
    # latin-1 preserves bytes for binary heuristics
    fake = raw.decode("latin-1", errors="replace")
    return {
        "status": "ok",
        "text": fake,
        "engine": "binary_sample",
        "chars": len(raw),
        "note": "non-text file sampled for binary detection",
    }


def needs_ocr(
    pdf_path: Union[str, Path],
    *,
    min_chars: int = 200,
    text: Optional[str] = None,
    engine: Optional[str] = None,
) -> Dict[str, Any]:
    """Decide whether a document is accessible as-is.

    Fails to UNDECIDABLE rather than guessing when the path is missing or extract fails.
    Binary masquerading as text is never scored as a good text layer.
    """
    p = Path(pdf_path).expanduser()
    if text is None:
        if not p.is_file():
            return {
                "decidable": False,
                "reason": "file not found",
                "pdf_path": str(p),
                "chars": None,
                "needs_ocr": None,
                "accessible_as_is": None,
            }
        extracted = extract_text_simple(p)
        if extracted["status"] != "ok":
            return {
                "decidable": False,
                "reason": extracted.get("error") or extracted["status"],
                "pdf_path": str(p),
                "chars": None,
                "needs_ocr": None,
                "accessible_as_is": None,
                "extract": extracted,
            }
        text = extracted.get("text") or ""
        engine = extracted.get("engine")
    else:
        if not p.is_file() and text is None:
            return {
                "decidable": False,
                "reason": "file not found",
                "pdf_path": str(p),
                "chars": None,
                "needs_ocr": None,
                "accessible_as_is": None,
            }

    assert text is not None
    if looks_like_binary(text) or engine == "binary_sample":
        return {
            "decidable": False,
            "reason": (
                f"extractor returned binary as text "
                f"(engine={engine!r}, {len(text)} bytes) — "
                f"this is an image or unparsed file, not a text layer"
            ),
            "pdf_path": str(p),
            "chars": None,
            "needs_ocr": True,
            "accessible_as_is": False,
        }

    chars = len(text.strip())
    return {
        "decidable": True,
        "chars": chars,
        "threshold": min_chars,
        "needs_ocr": chars < min_chars,
        "accessible_as_is": chars >= min_chars,
        "pdf_path": str(p),
        "engine": engine,
    }


def process_paths(
    paths: List[Union[str, Path]],
    *,
    min_chars: int = 200,
) -> Dict[str, Any]:
    accessible, needs, undecidable = [], [], []
    for path in paths:
        verdict = needs_ocr(path, min_chars=min_chars)
        if not verdict.get("decidable"):
            undecidable.append({"pdf_path": str(path), "reason": verdict.get("reason"), **{k: verdict.get(k) for k in ("needs_ocr", "accessible_as_is")}})
        elif verdict.get("needs_ocr"):
            needs.append(verdict)
        else:
            accessible.append(verdict)
    return {
        "considered": len(paths),
        "accessible_as_is": len(accessible),
        "needs_ocr": len(needs),
        "undecidable": len(undecidable),
        "detail": {
            "accessible": accessible,
            "needs_ocr": needs,
            "undecidable": undecidable,
        },
        "prepare_only": True,
    }
