#!/usr/bin/env python3
"""M14 — classify a grid14 record (cells14.jsonl) with the S-140 class, and write
SUMMARY14.md and classified14.jsonl beside it (the M14 brief's §5).

usage: python3 gen/classify14.py --cells cells14 results/<commit>/cells14.jsonl
       python3 gen/classify14.py --selftest
       python3 gen/classify14.py --cells cells14 --against13 results/<commit>/cells14.jsonl

It extends gen/classify13.py and does not edit it: it imports classify13's `run_class`
(wrapped below) and `classify` (--against13's re-class) and nothing else. It never
calls classify13.main() and never writes a `*13.*` file. Each cell's metadata comes
from <cells>/INDEX.jsonl; a missing index is an error, not a fallback.

The classes are classify13's, in its order, with these changes, each marked CHANGE n
in the code:
  1. The expected exit is `expect_exit` for a TRAP cell and for a SAFE cell that
     carries one (the twins: 14 or 0); 0 otherwise.
  2. PERMITTED:S-140 is decided after `timeout`, `LOUD` and `DEFECT:fallthrough`, and
     before `DEFECT:leg_mismatch`, only when all of these hold:
       (1) the cell's INDEX.jsonl entry has s140 = "unused_load", the generator's flag;
       (2) its scope is "wild", its expect TRAP and its expect_exit 107;
       (3) O0 == 107;
       (4) O2 == its s140_o2, which is not 107;
       (5) its twin's record (s140_twin), in the same record file, has
           O0 == O2 == s140_o2.
     A flagged cell whose twin has no record is an error: exit 1. Every other O0 != O2
     stays DEFECT:leg_mismatch, and a flagged cell at 107/107 is clean.
  3. --selftest runs with no record file: synthetic records, each asserting its class
     (one fails, or passes, on the condition it names); exit 0 only when every one
     matches.
  4. The outputs are SUMMARY14.md and classified14.jsonl, beside the record, with
     classified13's fields plus s140, s140_o2, s140_twin, boundary and after.
     SUMMARY14 lists the PERMITTED:S-140 cells in a table of their own, each with its
     twin's result.
  5. --against13 RECORD writes no file. It re-classes every record in memory with
     classify13's `classify`, lists every cell whose class differs from this
     classifier's, with the counts per (old, new) pair, and exits 1 unless every
     difference is (a) DEFECT:leg_mismatch -> PERMITTED:S-140 on a cell meeting
     conditions 1-5, re-checked here from the index and the record without calling
     the classification it checks, or (b) DEFECT:wrong_value -> clean on a SAFE twin
     whose expect_exit is non-zero and whose two legs both give it (change 1). It
     then counts the flagged cells: 107/107 (clean in both); legs disagreeing and
     meeting conditions 2-5 (PERMITTED:S-140); legs disagreeing and failing one of
     them, each asserted DEFECT:leg_mismatch, or DEFECT:fallthrough where a leg gives
     99 -- the live control for condition (c).
"""
import argparse, collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify13 import run_class, classify as classify13  # noqa: E402  (the two names §5 allows)

FLAG = "unused_load"
PERMITTED = "PERMITTED:S-140"
FIELDS = ("id", "section", "T", "P", "O", "observer", "scope", "expect", "expect_exit", "class", "exp_mismatch",
          "npkc", "codes", "O0", "O2", "s140", "s140_o2", "s140_twin", "boundary", "after")


class TwinMissing(Exception):
    pass


def expected_exit(meta):
    """CHANGE 1: a TRAP cell's arm, a twin's own exit (14 or 0), and 0 otherwise."""
    e = meta["expect"]
    if e == "TRAP" or (e == "SAFE" and meta.get("expect_exit") is not None):
        return meta.get("expect_exit")
    return 0


def permitted(r, meta, recs):
    """CHANGE 2: conditions (1)-(5); the twin's presence is asserted by classify14 first."""
    if meta.get("s140") != FLAG:                                                   # (1)
        return False
    if meta.get("scope") != "wild" or meta.get("expect") != "TRAP" or meta.get("expect_exit") != 107:   # (2)
        return False
    if r["O0"] != 107:                                                             # (3)
        return False
    o2 = meta.get("s140_o2")
    if o2 is None or o2 == 107 or r["O2"] != o2:                                   # (4)
        return False
    tw = recs[meta["s140_twin"]]                                                   # (5)
    return tw["O0"] == o2 and tw["O2"] == o2


def classify14(r, meta, recs):
    if meta.get("s140") == FLAG and meta.get("s140_twin") not in recs:
        raise TwinMissing("%s is flagged, and its twin %r has no record in this file" % (r["id"], meta.get("s140_twin")))
    rc = r["npkc"]
    if rc not in (0, 1):
        return "CRASH:npkc"
    e = r["expect"]
    if rc == 1:
        return {"REFUSE": "refused", "SAFE": "OVERRESTRICT", "TRAP": "REFUSED_TRAP"}[e]
    head = run_class(r, expected_exit(meta))      # classify13's run classes, in its order (CHANGE 1's exit)
    if head in ("timeout", "LOUD", "DEFECT:fallthrough"):
        c = head                                  # decided before the S-140 class
    elif permitted(r, meta, recs):
        c = PERMITTED                             # CHANGE 2: just before DEFECT:leg_mismatch
    else:
        c = head                                  # DEFECT:leg_mismatch, clean and the rest, as classify13
    return "ACCEPTED:" + c if e == "REFUSE" else c


def exp_mismatch(r, meta):
    """classify13's, copied (only run_class and classify are imported)."""
    if r["npkc"] == 1:
        if r["expect"] == "REFUSE":
            return "" if set(meta.get("expect_codes") or []) <= set(r["codes"]) else "codes"
        return "refused"
    if r["npkc"] == 0 and r["expect"] == "REFUSE":
        return "accepted"
    return ""


# ------------------------------------------------------------------ CHANGE 3: the selftest
def selftest():
    def world(cell_meta, o0, o2, twin=None, npkc=0):
        """A cell's meta and record, and its twin's record (o0, o2), or none."""
        m = dict({"id": "c", "section": "U", "T": "int64", "P": "local", "O": "bind", "observer": "exit",
                  "scope": "wild", "expect": "TRAP", "expect_exit": 107}, **cell_meta)
        recs = {"c": {"id": "c", "expect": m["expect"], "expect_exit": m["expect_exit"], "npkc": npkc, "codes": [],
                      "O0": o0, "O2": o2}}
        if twin is not None:
            recs["t"] = {"id": "t", "expect": "SAFE", "expect_exit": m.get("s140_o2"), "npkc": 0, "codes": [],
                         "O0": twin[0], "O2": twin[1]}
        return m, recs

    F14 = {"s140": FLAG, "s140_o2": 14, "s140_twin": "t"}      # flagged, its twin answering 14
    F0 = {"s140": FLAG, "s140_o2": 0, "s140_twin": "t"}        # flagged, its twin answering 0
    U14 = {"s140_o2": 14, "s140_twin": "t"}                    # everything but the flag
    U0 = {"s140_o2": 0, "s140_twin": "t"}
    cases = [
        ("flagged, 107/14, twin 14/14", F14, 107, 14, (14, 14), PERMITTED),
        ("flagged, 107/107, twin 14/14", F14, 107, 107, (14, 14), "clean"),
        ("flagged, 107/0 with s140_o2 14, twin 14/14 (condition 4)", F14, 107, 0, (14, 14), "DEFECT:leg_mismatch"),
        ("flagged, 106/14, twin 14/14 (condition 3)", F14, 106, 14, (14, 14), "DEFECT:leg_mismatch"),
        ("flagged, 107/14, twin 14/0 (condition 5)", F14, 107, 14, (14, 0), "DEFECT:leg_mismatch"),
        ("flagged, 107/14, twin 0/0: the twin's legs agree, but not with s140_o2 (condition 5)", F14, 107, 14, (0, 0),
         "DEFECT:leg_mismatch"),
        ("flagged, 107/99, twin 14/14", F14, 107, 99, (14, 14), "DEFECT:fallthrough"),
        ("flagged but scope plain, 107/14, twin 14/14 (condition 2)", dict(F14, scope="plain"), 107, 14, (14, 14),
         "DEFECT:leg_mismatch"),
        ("unflagged, 107/14: s140_o2 14 and a 14/14 twin, the flag alone absent (condition 1)", U14, 107, 14,
         (14, 14), "DEFECT:leg_mismatch"),
        ("unflagged, 107/0: s140_o2 0 and a 0/0 twin, the flag alone absent (condition 1)", U0, 107, 0, (0, 0),
         "DEFECT:leg_mismatch"),
        ("flagged, with its twin missing", F14, 107, 14, None, "ERROR"),
        # beyond the brief's list:
        ("flagged, 107/0 with s140_o2 0, twin 0/0 (the exit-0 seed's shape)", F0, 107, 0, (0, 0), PERMITTED),
        ("flagged, expect_exit 106, 107/14, twin 14/14 (condition 2)", dict(F14, expect_exit=106), 107, 14, (14, 14),
         "DEFECT:leg_mismatch"),
        ("a twin, SAFE with expect_exit 14, at 14/14 (change 1)", {"section": "W", "O": "twin", "expect": "SAFE",
                                                                  "expect_exit": 14}, 14, 14, None, "clean"),
        ("a twin, SAFE with expect_exit 0, at 0/0 (change 1)", {"section": "W", "O": "twin", "expect": "SAFE",
                                                               "expect_exit": 0}, 0, 0, None, "clean"),
    ]
    bad = 0
    for name, cm, o0, o2, twin, want in cases:
        m, recs = world(cm, o0, o2, twin)
        try:
            got = classify14(recs["c"], m, recs)
        except TwinMissing:
            got = "ERROR"
        ok = got == want
        bad += not ok
        print("%s  %-92s -> %s%s" % ("ok  " if ok else "FAIL", name, got, "" if ok else "  (want %s)" % want))
    print("selftest: %d cases, %d %s" % (len(cases), len(cases) - bad, "pass" if not bad else "pass, %d FAIL" % bad))
    return 1 if bad else 0


# ------------------------------------------------------------------ CHANGE 5: against classify13
def failed_conditions(meta, rec, recs):
    """Conditions 1-5 re-derived from the index and the record for --against13, apart from permitted() and
    classify14(), whose answer this checks: -> the numbers of those that fail."""
    out = []
    want_o2 = meta.get("s140_o2")
    twin = recs.get(meta.get("s140_twin")) or {}
    checks = [
        (1, meta.get("s140") == "unused_load"),
        (2, (meta.get("scope"), meta.get("expect"), meta.get("expect_exit")) == ("wild", "TRAP", 107)),
        (3, rec.get("O0") == 107),
        (4, want_o2 is not None and want_o2 != 107 and rec.get("O2") == want_o2),
        (5, want_o2 is not None and (twin.get("O0"), twin.get("O2")) == (want_o2, want_o2)),
    ]
    for n, holds in checks:
        if not holds:
            out.append(n)
    return out


def against13(metas, recs, path):
    new = {cid: classify14(r, metas[cid], recs) for cid, r in recs.items()}
    old = {cid: classify13(r) for cid, r in recs.items()}
    diffs = sorted(cid for cid in recs if old[cid] != new[cid])
    pairs = collections.Counter((old[c], new[c]) for c in diffs)
    bad = []
    kinds = collections.Counter()
    for cid in diffs:
        m, r = metas[cid], recs[cid]
        if (old[cid], new[cid]) == ("DEFECT:leg_mismatch", PERMITTED) and not failed_conditions(m, r, recs):
            kinds["a"] += 1
        elif ((old[cid], new[cid]) == ("DEFECT:wrong_value", "clean") and m["expect"] == "SAFE"
              and m.get("expect_exit") not in (None, 0) and r["O0"] == r["O2"] == m["expect_exit"]):
            kinds["b"] += 1
        else:
            bad.append(cid)
    print("# against13: %s: %d records; %d differ between classify13 and classify14" % (path, len(recs), len(diffs)))
    for (a, b), n in sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0])):
        print("#   %-24s -> %-20s %d" % (a, b, n))
    print("# (a) leg_mismatch -> %s on a cell meeting conditions 1-5: %d; (b) wrong_value -> clean on a "
          "non-zero twin: %d; anything else: %d" % (PERMITTED, kinds["a"], kinds["b"], len(bad)))
    for cid in diffs:
        r = recs[cid]
        print("%s | %s/%s | %s -> %s%s" % (cid, r["O0"], r["O2"], old[cid], new[cid], "  NOT (a) OR (b)" if cid in bad
                                                                                     else ""))
    # the flagged cells, by group
    groups = collections.OrderedDict((k, []) for k in ("107/107", "permitted", "fail", "refused or crashed",
                                                       "legs agree, not 107"))
    gbad = []
    for cid in sorted(recs):
        m, r = metas[cid], recs[cid]
        if m.get("s140") != FLAG:
            continue
        if r["npkc"] != 0:
            groups["refused or crashed"].append(cid)
        elif r["O0"] == r["O2"]:
            if r["O0"] == 107:
                groups["107/107"].append(cid)
                if not (old[cid] == new[cid] == "clean"):
                    gbad.append((cid, "107/107 but not clean in both"))
            else:
                groups["legs agree, not 107"].append(cid)
        else:
            f = failed_conditions(m, r, recs)
            if not f:
                groups["permitted"].append(cid)
                if new[cid] != PERMITTED:
                    gbad.append((cid, "meets conditions 1-5 but is %s" % new[cid]))
            else:
                groups["fail"].append((cid, f))
                want = "DEFECT:fallthrough" if 99 in (r["O0"], r["O2"]) else "DEFECT:leg_mismatch"
                if new[cid] != want:
                    gbad.append((cid, "legs disagree, condition(s) %s fail, class %s, not %s" % (f, new[cid], want)))
    nflag = sum(len(v) for v in groups.values())
    print("# flagged cells: %d -- 107/107 (clean in both) %d; legs disagree and meet conditions 1-5 (%s) %d; legs "
          "disagree and fail a condition (each asserted leg_mismatch, or fallthrough with a 99) %d; refused or "
          "crashed %d; legs agree, not 107 %d" % (nflag, len(groups["107/107"]), PERMITTED, len(groups["permitted"]),
                                                 len(groups["fail"]), len(groups["refused or crashed"]),
                                                 len(groups["legs agree, not 107"])))
    for cid, f in groups["fail"]:
        m, r = metas[cid], recs[cid]
        tw = recs.get(m.get("s140_twin")) or {}
        print("#   fails %s: %s | %s/%s, s140_o2 %s | twin %s %s/%s | %s" % (
            ",".join(map(str, f)), cid, r["O0"], r["O2"], m.get("s140_o2"), m.get("s140_twin"), tw.get("O0"),
            tw.get("O2"), new[cid]))
    for cid in groups["legs agree, not 107"] + groups["refused or crashed"]:
        r = recs[cid]
        print("#   %s: npkc=%s %s/%s %s" % (cid, r["npkc"], r["O0"], r["O2"], new[cid]))
    for cid, why in gbad:
        print("FAIL %s: %s" % (cid, why))
    ok = not bad and not gbad
    print("# against13: %s" % ("every difference is (a) or (b), and every flagged group holds: exit 0" if ok
                               else "%d differences not (a) or (b), %d group failures: exit 1" % (len(bad), len(gbad))))
    return 0 if ok else 1


# ------------------------------------------------------------------ CHANGE 4: the outputs
def summary(recs, metas, idx, results):
    outdir = os.path.dirname(os.path.abspath(results))
    commit = os.path.basename(outdir)
    rs = [recs[c] for c in sorted(recs)]
    by = collections.Counter(r["class"] for r in rs)
    classes = sorted(by)
    L = ["# SUMMARY14 — grid14 at `%s`" % commit, "",
         "Generated by `gen/classify14.py` from `%s` (%d cells; the metadata from `%s`). Every cell is scope wild: "
         "the check of TYPE_REFERENCE §27 (D-364), reported apart." % (os.path.basename(results), len(rs), idx), "",
         "## Count per class", "", "| class | cells |", "|---|---|"]
    for k in classes:
        L.append("| %s | %d |" % (k, by[k]))
    L.append("| **generated** | **%d** |" % len(rs))
    L += ["", "## Expectation vs verdict", "", "| expectation | npkc 0 | npkc 1 | other |", "|---|---|---|---|"]
    for e in ("TRAP", "SAFE"):
        es = [r for r in rs if r["expect"] == e]
        L.append("| %s | %d | %d | %d |" % (e, sum(r["npkc"] == 0 for r in es), sum(r["npkc"] == 1 for r in es),
                                          sum(r["npkc"] not in (0, 1) for r in es)))
    for axis in ("section", "T", "P", "O", "after"):
        vals = sorted(set(str(r.get(axis)) for r in rs))
        L += ["", "## Per class per %s" % axis, "", "| %s | %s |" % (axis, " | ".join(classes)),
              "|---|%s" % ("---|" * len(classes))]
        for v in vals:
            c = collections.Counter(r["class"] for r in rs if str(r.get(axis)) == v)
            L.append("| %s | %s |" % (v, " | ".join(str(c.get(k, 0)) for k in classes)))
    codes = collections.Counter(",".join(r["codes"]) for r in rs if r["npkc"] == 1)
    L += ["", "## Refusal codes", ""]
    L += (["| codes | cells |", "|---|---|"] + ["| %s | %d |" % (k or "(none)", v) for k, v in codes.most_common()]
          if codes else ["(none)"])
    pm = [r for r in rs if r["class"] == PERMITTED]
    L += ["", "## %s (%d): each with its twin's result" % (PERMITTED, len(pm)), ""]
    if pm:
        L += ["| cell | section | T | P | O | after | O0 | O2 | s140_o2 | twin | twin O0 | twin O2 | twin class |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in pm:
            t = recs[r["s140_twin"]]
            L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | `%s` | %s | %s | %s |" % (
                r["id"], r["section"], r["T"], r["P"], r["O"], r.get("after") or "-", r["O0"], r["O2"], r["s140_o2"],
                r["s140_twin"], t["O0"], t["O2"], t["class"]))
    else:
        L.append("(none)")
    fl = [r for r in rs if r.get("s140") == FLAG]
    L += ["", "## The flagged cells (%d) by class" % len(fl), "", "| class | cells |", "|---|---|"]
    for k, v in sorted(collections.Counter(r["class"] for r in fl).items()):
        L.append("| %s | %d |" % (k, v))
    look = [r for r in rs if r["class"] not in ("clean", PERMITTED)]
    L += ["", "## Every cell to triage: not `clean`, not `%s` (%d)" % (PERMITTED, len(look)), ""]
    if look:
        L += ["| cell | section | class | npkc | codes | O0 | O2 | expect | s140_o2 | boundary |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in look:
            L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s %s | %s | %s |" % (
                r["id"], r["section"], r["class"], r["npkc"], ",".join(r["codes"]) or "-", r["O0"], r["O2"],
                r["expect"], r.get("expect_exit"), r.get("s140_o2", "-") if r.get("s140") else "-",
                r.get("boundary") or "-"))
    else:
        L.append("(none)")
    with open(os.path.join(outdir, "SUMMARY14.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    with open(os.path.join(outdir, "classified14.jsonl"), "w") as fh:
        for r in rs:
            fh.write(json.dumps({k: r.get(k) for k in FIELDS}) + "\n")
    return outdir, by


def load(cells, results):
    idx = os.path.join(cells, "INDEX.jsonl")
    if not os.path.exists(idx):
        sys.exit("classify14: %s is missing; generate the grid first (python3 gen/grid14.py)" % idx)
    metas = {}
    for l in open(idx):
        m = json.loads(l)
        metas[m["id"]] = m
    recs = {}
    for l in open(results):
        if l.strip():
            r = json.loads(l)
            recs[r["id"]] = r
    missing = sorted(c for c in recs if c not in metas)
    if missing:
        sys.exit("classify14: %d records have no cell in %s, the first %s" % (len(missing), idx, missing[0]))
    for cid, r in recs.items():
        if r["expect"] != metas[cid]["expect"]:
            sys.exit("classify14: %s: the record's expect %s is not the index's %s" % (cid, r["expect"],
                                                                                     metas[cid]["expect"]))
    return idx, metas, recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="?")
    ap.add_argument("--cells", default="cells14")
    ap.add_argument("--selftest", action="store_true", help="CHANGE 3: synthetic records, no record file")
    ap.add_argument("--against13", metavar="RECORD", help="CHANGE 5: re-class RECORD against classify13; writes nothing")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.against13:
        idx, metas, recs = load(a.cells, a.against13)
        try:
            sys.exit(against13(metas, recs, a.against13))
        except TwinMissing as e:
            sys.exit("classify14: %s" % e)
    if not a.results:
        sys.exit(__doc__)
    idx, metas, recs = load(a.cells, a.results)
    for cid, r in recs.items():
        m = metas[cid]
        try:
            r["class"] = classify14(r, m, recs)
        except TwinMissing as e:
            sys.exit("classify14: %s" % e)
        r["exp_mismatch"] = exp_mismatch(r, m)
        for k in ("scope", "s140", "s140_o2", "s140_twin", "boundary", "after"):
            r[k] = m.get(k)
        r.setdefault("section", m.get("section"))
    outdir, by = summary(recs, metas, idx, a.results)
    print("%d cells -> %s" % (len(recs), os.path.join(outdir, "SUMMARY14.md")))
    for k, v in sorted(by.items()):
        print("  %-28s %d" % (k, v))


if __name__ == "__main__":
    main()
