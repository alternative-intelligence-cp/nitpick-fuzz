#!/usr/bin/env python3
"""M12 (S73) — compare two M10 or M11 records claim by claim.

usage: python3 gen/compare_runs.py OLD.jsonl NEW.jsonl

Both files hold one JSON line per program (gen/m10_run.py's or
gen/m11_run.py's records), keyed by `id`. A program CHANGED when any of these
fields differs:

  npkc, codes, O0, O2, sh, verdict, kind, heap_O0, heap_O2

A field absent from both records is equal; a field present in only one of them
is a change. Every changed id is listed with the fields that moved, and so is
every id present on one side only. The totals come last. Nothing is written.
"""
import argparse, json, os

FIELDS = ("npkc", "codes", "O0", "O2", "sh", "verdict", "kind", "heap_O0", "heap_O2")
ABSENT = "<absent>"


def load(path):
    recs = {}
    for l in open(path):
        if l.strip():
            r = json.loads(l)
            if r["id"] in recs:
                raise SystemExit("%s holds %s twice" % (path, r["id"]))
            recs[r["id"]] = r
    return recs


def show(v):
    if v is ABSENT:
        return v
    if isinstance(v, list):
        return "[" + ",".join(str(x).replace("NITPICK-", "") for x in v) + "]"
    return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    a = ap.parse_args()
    old, new = load(a.old), load(a.new)
    on, nn = (os.path.normpath(p) for p in (a.old, a.new))
    changed = 0
    for cid in sorted(set(old) & set(new)):
        o, n = old[cid], new[cid]
        diffs = []
        for f in FIELDS:
            ov, nv = o.get(f, ABSENT), n.get(f, ABSENT)
            if ov != nv:
                diffs.append("%s %s -> %s" % (f, show(ov), show(nv)))
        if diffs:
            changed += 1
            print("CHANGED %s: %s" % (cid, "; ".join(diffs)))
    only_old, only_new = sorted(set(old) - set(new)), sorted(set(new) - set(old))
    for cid in only_old:
        print("ONLY IN OLD %s" % cid)
    for cid in only_new:
        print("ONLY IN NEW %s" % cid)
    print("%d ids, %d changed, %d only in %s, %d only in %s"
          % (len(set(old) | set(new)), changed, len(only_old), on, len(only_new), nn))


if __name__ == "__main__":
    main()
