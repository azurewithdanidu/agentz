#!/usr/bin/env python3
"""Rank catalog entries by overlap with a query. Standard library only.

Uses the overlap coefficient on name and description words, the same scoring
as the CI duplicate check in scripts/validate_repo.py.

  python3 search_catalog.py --catalog catalog.json --query "review bicep against AVM"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STOPWORDS = set(
    "a an and are as at be by do does for from how if in into is it its of on or that the this to "
    "use used uses using when with without you your not any all can should user users ask asks".split()
)


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 2}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", default="catalog.json")
    ap.add_argument("--query", required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    a = ap.parse_args()

    path = Path(a.catalog)
    if not path.exists():
        print(f"catalog not found: {path}. Run from the agentz repository root.", file=sys.stderr)
        return 2
    catalog = json.loads(path.read_text(encoding="utf-8"))

    query = tokens(a.query)
    if not query:
        print("query has no searchable words", file=sys.stderr)
        return 2

    rows = []
    for plugin in catalog.get("plugins", []):
        for kind in ("skills", "agents", "commands"):
            for item in plugin.get(kind, []):
                words = tokens(item["name"].replace("-", " ") + " " + item.get("description", ""))
                if not words:
                    continue
                shared = query & words
                score = len(shared) / min(len(query), len(words))
                rows.append({
                    "plugin": plugin["name"], "kind": kind[:-1], "name": item["name"],
                    "score": round(score, 2), "shared": sorted(shared),
                    "description": item.get("description", ""),
                })
    rows.sort(key=lambda r: r["score"], reverse=True)
    rows = rows[: a.top]

    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    print(f"{'score':>5}  {'plugin':<24} {'kind':<8} name")
    for r in rows:
        print(f"{r['score']:>5.2f}  {r['plugin']:<24} {r['kind']:<8} {r['name']}")
        print(f"       shared: {', '.join(r['shared'][:12])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
