#!/usr/bin/env python3
"""M9.6 — the recall gate over the widened grid, at the baseline.

usage: python3 gen/recall9.py results/c3bdae2/

For each known shape (gen/dedup9.py's RULES), counts the widened grid's cells
of that shape, and those flagged DEFECT at this compiler, per observer and
per section. PLAN.md 9.6: every known shape must still be flagged at the
baseline. Prints a markdown table and exits 1 if a shape has no flagged cell.
"""
import argparse, collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dedup9 import RULES  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    a = ap.parse_args()
    cells = {}
    for l in open(os.path.join(a.dir, "cells9.jsonl")):
        r = json.loads(l)
        cells[r["id"]] = r
    for l in open(os.path.join(a.dir, "classified9.jsonl")):
        c = json.loads(l)
        cells[c["id"]].update(c)
    rows = ["| known | cells of the shape | flagged DEFECT | by observer (ra/dx/lk/rs/rn) | by section | first flagging cells |",
            "|---|---|---|---|---|---|"]
    missing = []
    for name, pred, text in RULES:
        shape = [r for r in cells.values() if pred(r)]
        flagged = [r for r in shape if r["class"].startswith("DEFECT")]
        byo = collections.Counter(r["observer"] for r in flagged)
        bys = collections.Counter(r.get("section") for r in flagged)
        obs = "/".join(str(byo.get(o, 0)) for o in ("read_after", "drop_at_exit", "leak", "reuse_sentinel", "read_now"))
        sec = ", ".join("%s %d" % kv for kv in sorted(bys.items()))
        first = " ".join("`%s`" % r["id"][:5] for r in sorted(flagged, key=lambda r: r["id"])[:6])
        rows.append("| %s | %d | %d | %s | %s | %s |" % (name, len(shape), len(flagged), obs, sec, first))
        if not flagged:
            missing.append(name)
    print("\n".join(rows))
    if missing:
        print("\nNOT FLAGGED: %s" % ", ".join(missing))
        sys.exit(1)
    print("\nevery known shape flagged")


if __name__ == "__main__":
    main()
