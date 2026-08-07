"""ada-doc-check — prepare-only ADA/WCAG-ish document triage.

Extracted from M.A.N.A.G.E.R. A.I.D.A. Product A (generic accessibility).
Not a certified Section 508 auditor. Humans sign off.
"""

from __future__ import annotations

from ada_check.compliance import ada_pre_check
from ada_check.gate import accessibility_gate
from ada_check.triage import needs_ocr, looks_like_binary

__version__ = "0.1.0"

__all__ = [
    "ada_pre_check",
    "accessibility_gate",
    "needs_ocr",
    "looks_like_binary",
    "__version__",
]
