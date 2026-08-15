#!/usr/bin/env python3
"""Render analysis.json into the interactive review HTML.

    python build_review_html.py analysis.json -o contract-review.html

Injects the analysis data into assets/review-template.html. The data lands
inside a <script type="application/json"> block, so we neutralize any
</script> / <! sequences to keep the JSON from breaking out of the tag.
"""
import argparse
import json
import sys
from pathlib import Path

PLACEHOLDER = "__ANALYSIS_JSON__"


def load_template() -> str:
    tpl = Path(__file__).resolve().parent.parent / "assets" / "review-template.html"
    if not tpl.exists():
        sys.exit(f"template not found: {tpl}")
    return tpl.read_text(encoding="utf-8")


def safe_json(data: dict) -> str:
    # Compact but valid; escape sequences that could close the host <script>.
    s = json.dumps(data, ensure_ascii=False)
    return s.replace("</", "<\\/").replace("<!", "<\\!")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the contract review HTML from analysis.json")
    ap.add_argument("analysis", help="Path to analysis.json")
    ap.add_argument("-o", "--output", default="contract-review.html", help="Output HTML path")
    args = ap.parse_args()

    data = json.loads(Path(args.analysis).read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    if not findings:
        print("warning: analysis has no findings", file=sys.stderr)

    html = load_template()
    if PLACEHOLDER not in html:
        sys.exit("placeholder missing from template")
    html = html.replace(PLACEHOLDER, safe_json(data))

    out = Path(args.output)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(findings)} findings, "
          f"score {data.get('score', {}).get('overall', '?')}/10)")


if __name__ == "__main__":
    main()
