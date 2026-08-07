"""CLI for ada-doc-check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ada_check.gate import accessibility_gate
from ada_check.triage import process_paths


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ada-doc-check",
        description="ADA/WCAG-ish document first-pass triage (prepare-only)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", help="Gate a single path or stdin text")
    s.add_argument("path", nargs="?", default=None)
    s.add_argument("--text", default=None, help="Inline text instead of file")
    s.add_argument("--doc-type", default="document")

    s = sub.add_parser("triage", help="Batch triage paths")
    s.add_argument("paths", nargs="+")
    s.add_argument("--min-chars", type=int, default=200)

    args = p.parse_args(argv)
    if args.cmd == "check":
        if not args.path and args.text is None:
            print(json.dumps({"error": "path or --text required"}), file=sys.stderr)
            return 2
        out = accessibility_gate(path=args.path, content=args.text, doc_type=args.doc_type)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1

    if args.cmd == "triage":
        report = process_paths(args.paths, min_chars=args.min_chars)
        print(json.dumps(report, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
