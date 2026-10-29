#!/usr/bin/env python3
"""Check m15_expect.tsv against the log lines it cites (standalone).

For each row (cell, compiler, verdict, detail, logfile, line): re-open
logfile at the cited line, parse  <probe> @<sha> npkc=.. O0=.. O2=.. , and
confirm (a) the sha maps to the row's compiler, (b) the parsed verdict/detail
equal the row's, and (c) the probe stem maps to the row's cell.  Prints one
MISMATCH line per failure and a final "N rows, M mismatches"; exits non-zero
if any mismatch.  The cited logs live in the manager's probe set (pass its dir
as <logdir>); grid15 reads only the .tsv, never the logs.

usage: python3 m15_expect_check.py <m15_expect.tsv> <logdir>
"""
import os, re, sys

SHA = {"1480ca8": "H6", "02856cf": "REG"}
LINE = re.compile(r'^([A-Za-z0-9_]+)\.npk @([0-9a-f]+) npkc=(\d+) (\S+) O0=(\S+) O2=(\S+)')
TWIN = re.compile(r'^[a-z]+\d+t_')


def cell_key(stem):
    """probe stem -> grid15 cell key, mirroring the builder (keep in sync)."""
    if TWIN.match(stem):
        return None
    if re.match(r'^s\d', stem):
        return "seed:" + stem
    if stem in ("elem_callee", "elem_field_callee"):
        return "seed:F050:" + stem
    m = re.match(r'^r_([a-z]+)$', stem)
    if m:
        return "pp:%s:dir:same" % m.group(1)
    m = re.match(r'^w_pp_fld_([a-z]+)$', stem)
    if m:
        return "pp:fld:%s:same" % m.group(1)
    m = re.match(r'^q\d+_(pp|lo|lp|pq)_([a-z]+)_([a-z]+)(_in)?$', stem)
    if m:
        V, road, w, inner = m.groups()
        if V != "pp" or w == "cresf":
            return None
        return "pp:%s:%s:%s" % (road, w, "inner" if inner else "same")
    return None


def verdict_of(npkc, code, o0, o2):
    if npkc == "1":
        return "refuse", code
    if o0 == o2 and o0 in ("70", "170"):
        return "leak", "%s/%s" % (o0, o2)
    if o0 == "0" and o2 == "0":
        return "clean", "0/0"
    return "other", "%s/%s" % (o0, o2)


def main():
    tsv, logdir = sys.argv[1], sys.argv[2]
    n = mm = 0
    cache = {}
    seen = set()
    for raw in open(tsv):
        raw = raw.rstrip("\n")
        if not raw or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) != 6:
            print("MISMATCH malformed row:", raw[:80]); mm += 1; continue
        cell, comp, verdict, detail, lf, lineno = parts
        n += 1
        if (cell, comp) in seen:
            print("MISMATCH duplicate (cell, compiler) row:", cell, comp); mm += 1; continue
        seen.add((cell, comp))
        path = os.path.join(logdir, lf)
        if path not in cache:
            try:
                cache[path] = open(path).readlines()
            except IOError:
                cache[path] = None
        lines = cache[path]
        if lines is None:
            print("MISMATCH", cell, comp, "-- cannot open", lf); mm += 1; continue
        try:
            target = lines[int(lineno) - 1]
        except (IndexError, ValueError):
            print("MISMATCH", cell, comp, "-- no %s:%s" % (lf, lineno)); mm += 1; continue
        m = LINE.match(target)
        if not m:
            print("MISMATCH", cell, comp, "-- %s:%s not a probe line" % (lf, lineno)); mm += 1; continue
        stem, sha, npkc, code, o0, o2 = m.groups()
        lcomp = SHA.get(sha, sha)
        lv, ld = verdict_of(npkc, code, o0, o2)
        lcell = cell_key(stem)
        if (lcomp, lv, ld) != (comp, verdict, detail):
            print("MISMATCH", cell, "row=(%s,%s,%s)" % (comp, verdict, detail),
                  "cited=(%s,%s,%s)@%s:%s" % (lcomp, lv, ld, lf, lineno)); mm += 1
        elif lcell != cell:
            print("MISMATCH", cell, "cited probe %r maps to %s (@%s:%s)" % (stem, lcell, lf, lineno)); mm += 1
    print("%d rows, %d mismatches" % (n, mm))
    return 1 if mm else 0


if __name__ == "__main__":
    sys.exit(main())
