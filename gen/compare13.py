#!/usr/bin/env python3
"""M13 — compare two grid13 classifications cell by cell.

usage: python3 gen/compare13.py OLD/classified13.jsonl NEW/classified13.jsonl

Lists every cell whose (npkc, codes, O0, O2, class) differs between the two, with
the counts per (old class, new class) pair. A cell present on one side only is
listed as MISSING:old or MISSING:new and counted as a difference. Prints to
stdout (redirect it to keep the listing) and writes nothing.

Exit status: 0 when nothing differs, 1 when anything does, so a gate can read it;
the listing remains the record. A file compared with itself lists 0 and exits 0.
"""
import collections, json, sys

KEY = ("npkc", "codes", "O0", "O2", "class")


def load(path):
    out = {}
    for l in open(path):
        if l.strip():
            r = json.loads(l)
            out[r["id"]] = r
    return out


def verdict(r):
    if r is None:
        return "-"
    return "npkc=%s %s %s/%s %s" % (r["npkc"], ",".join(r["codes"]) or "-", r["O0"], r["O2"], r["class"])


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old_p, new_p = sys.argv[1], sys.argv[2]
    old, new = load(old_p), load(new_p)
    ids = sorted(set(old) | set(new))
    moved, pairs = [], collections.Counter()
    for cid in ids:
        a, b = old.get(cid), new.get(cid)
        if a is None or b is None:
            pair = ("MISSING:old", b["class"]) if a is None else (a["class"], "MISSING:new")
        elif tuple(a[k] for k in KEY) == tuple(b[k] for k in KEY):
            continue
        else:
            pair = (a["class"], b["class"])
        moved.append((cid, a, b))
        pairs[pair] += 1
    print("# compare13: %s -> %s" % (old_p, new_p))
    print("# %d cells (%d old, %d new); %d differ" % (len(ids), len(old), len(new), len(moved)))
    if moved:
        print("#")
        print("# per class pair (old -> new):")
        for (a, b), n in sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0])):
            print("#   %-30s -> %-30s %d" % (a, b, n))
        print("#")
        print("# cell | old | new")
        for cid, a, b in moved:
            print("%s | %s | %s" % (cid, verdict(a), verdict(b)))
    sys.exit(1 if moved else 0)


if __name__ == "__main__":
    main()
