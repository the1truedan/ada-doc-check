# ada-doc-check

**Prepare-only** ADA/WCAG-ish **first-pass** triage for document piles.

| | |
|--|--|
| Version | **0.1.0** |
| Python | 3.10+ · stdlib core |
| Optional | `pip install 'ada-doc-check[pdf]'` for PDF text layers (`pypdf`) |

This is **not** a Section 508 or WCAG **certification** tool. A human signs off.

Extracted from the M.A.N.A.G.E.R. **A.I.D.A.** stack (Product A — generic accessibility).
Zero caregiving PHI vocabulary. Related lab metrics: [aida-complex-doc-lab](https://github.com/the1truedan/aida-complex-doc-lab).

---

## What it does

1. **Score** structured text for common accessibility gaps (`empty_content`, alt text, contrast, …)
2. **Triage** files: accessible text layer vs needs OCR vs **undecidable** (missing / binary)
3. **Fail closed** — a JPEG must never score as fully accessible

### Known failure modes fixed upstream (2026-08)

| Bug | Fix |
|-----|-----|
| Binary read as text layer → ADA 100 | `looks_like_binary()` |
| Missing path scored as “needs OCR” | `decidable: False` |

---

## Install & run

```bash
cd ~/ada-doc-check
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m ada_check check --text "Hello accessible document."
python -m ada_check triage ./fixtures/sample.txt /tmp/missing.pdf
pytest -q
```

---

## API

```python
from ada_check import ada_pre_check, needs_ocr, accessibility_gate

print(ada_pre_check({"content": "…", "has_alt_text": True}, doc_type="pdf"))
print(needs_ocr("scan.pdf"))
print(accessibility_gate(path="notes.txt"))
```

---

## Honest limits

- No LayoutLM / production OCR pipeline in this package (queue OCR elsewhere)
- PDF extract needs optional `pypdf`
- Scoring is a **heuristic first pass**, not legal compliance

Gateway stack (optional): [ai-gateway](https://github.com/the1truedan/ai-gateway) · [grok-tua-tok-tua](https://github.com/the1truedan/grok-tua-tok-tua)

---

<p align="left">
  <a href="https://linktr.ee/the1truedan"><img src="https://img.shields.io/badge/Linktree-39E09B?style=for-the-badge&logo=linktree&logoColor=white" alt="Linktree"></a>
  <a href="https://ko-fi.com/the1truedan"><img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-fi"></a>
</p>

**© 2026 M.A.N.A.G.E.R. LLC** — *prepare for the care when we cannot be there*
