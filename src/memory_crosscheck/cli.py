"""Read-only CLI; only the optional report path is written."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import compare
from .model import LocalNLI


def main() -> int:
    parser = argparse.ArgumentParser(description="Find possible conflicts between current Markdown facts and older memory")
    parser.add_argument("--current", required=True, type=Path, help="current source-of-truth Markdown")
    parser.add_argument("--memory", required=True, type=Path, help="older memory Markdown")
    parser.add_argument("--out", type=Path, help="optional JSON report path (default: stdout)")
    parser.add_argument("--threshold", type=float, default=0.70, help="NLI contradiction signal threshold")
    args = parser.parse_args()
    try:
        report = compare(args.current.read_text(encoding="utf-8"), args.memory.read_text(encoding="utf-8"), LocalNLI(), args.threshold)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
