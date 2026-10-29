#!/usr/bin/env python3
"""M15 — classify a grid15 record (cells15.jsonl) and write SUMMARY15.md and
classified15.jsonl beside it; the recall gate over HUNT6's and REG155's classified
files; and the gate's selftest (the M15 brief's §5; PROGRESS.md S106).

usage: python3 gen/classify15.py --cells cells15 results/<commit>/cells15.jsonl
       python3 gen/classify15.py --cells cells15 --recall <HUNT6 classified15.jsonl> <REG155 classified15.jsonl>
       python3 gen/classify15.py --selftest

The classes are classify13's, imported (`classify`, `run_class`, `exp_mismatch`):
a pp cell or a seed accepted and reading 70 or 170 is ACCEPTED:DEFECT:uaf, a twin
reading 0 is clean. A cell's metadata comes from <cells>/INDEX.jsonl (gen/run.py
copies only `section` and `expect_exit` into a record). The compiler is the results
directory's name, `commit` in every classified line: it ties a file to its sha only
by name, so the gate's COMMIT check catches a swapped or doubled file; §6's check of
each worktree's HEAD is the tie between a verdict and a compiler.

The recall gate runs EVERY check, prints each one's result with its count, and a
`TAG <name>` line for each one that fails; then the findings. Exit 3 when REGRESSION
is among the tags, else 1 when any tag fired, else 0. The checks:
  COMMIT       the HUNT6 file's commit is .work/H6, the REG155 file's .work/REG, and
               the two differ;
  COVERAGE     each file holds one record for every INDEX id and no other;
  SEED-RECALL  each of the eight named DEF-296 seeds is ACCEPTED:DEFECT:uaf at REG155;
  LEAK-RECALL  every cell whose meta says reg155 "leak" is ACCEPTED:DEFECT:* at REG155;
  SILENT-PASS  no hazard cell (pp or seed) is ACCEPTED:clean, :other or :timeout at
               either compiler;
  TWIN         every twin is clean at both compilers;
  CODE-H6      every hazard cell refused at HUNT6 names every code it expects
               (`exp_mismatch` "": expect_codes within the codes);
  CODE-REG     every hazard cell refused at REG155 names only NITPICK-BORROW- codes;
  UNANCHORED   no pp cell with reg155 None is refused at both compilers;
  REGRESSION   no hazard cell refused at REG155 is ACCEPTED:DEFECT:* at HUNT6.
FINDINGS lists every hazard cell ACCEPTED:DEFECT:* at HUNT6, for triage; a finding
is not a failure. A record whose id is not in the index is COVERAGE's alone.
"""
import argparse, collections, contextlib, io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify13 import classify, run_class, exp_mismatch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS8 = ("s11_pointer_local_field", "s11b_deref_field", "s11c_ptr_local_list_elem", "s11d_ptr_local_whole_pointee",
          "s11f_ptr_local_to_byvalue_param_field", "s11g_ptr_field_on_path", "s11h_ptr_local_async_frame",
          "s24_callee_store_via_ptr_local_arg")
SILENT = ("ACCEPTED:clean", "ACCEPTED:other", "ACCEPTED:timeout")
FIELDS = ("id", "section", "T", "P", "O", "observer", "scope", "expect", "expect_exit", "class", "exp_mismatch",
          "npkc", "codes", "O0", "O2", "R", "W", "V", "B", "key", "reg155", "commit")
AXES = ("section", "R", "W", "V", "B")


def load_index(cells):
    idx = os.path.join(cells, "INDEX.jsonl")
    if not os.path.exists(idx):
        sys.exit("classify15: %s is missing; generate the grid first (python3 gen/grid15.py)" % idx)
    metas = collections.OrderedDict()
    for l in open(idx, encoding="utf-8"):
        m = json.loads(l)
        metas[m["id"]] = m
    return metas


# ------------------------------------------------------------------ classification
def classify_file(path, cells):
    metas = load_index(cells)
    recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    ids = [r["id"] for r in recs]
    if len(set(ids)) != len(ids):
        sys.exit("classify15: %s holds an id twice" % path)
    missing = [i for i in ids if i not in metas]
    if missing:
        sys.exit("classify15: %d records have no cell in the index, the first %s" % (len(missing), missing[0]))
    recs.sort(key=lambda r: r["id"])
    outdir = os.path.dirname(os.path.abspath(path))
    commit = os.path.basename(outdir)
    for r in recs:
        m = metas[r["id"]]
        r["class"] = classify(r)
        r["exp_mismatch"] = exp_mismatch(r, m)
        for k in ("scope", "R", "W", "V", "B", "key", "reg155"):
            r[k] = m.get(k)
        r["expect_codes"] = m.get("expect_codes") or []
        r["commit"] = commit
    summary(recs, commit, path, cells, outdir)
    with open(os.path.join(outdir, "classified15.jsonl"), "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps({k: r.get(k) for k in FIELDS}) + "\n")
    by = collections.Counter(r["class"] for r in recs)
    print("%d cells -> %s" % (len(recs), os.path.join(outdir, "SUMMARY15.md")))
    for k, v in sorted(by.items()):
        print("  %-28s %d" % (k, v))


def summary(recs, commit, path, cells, outdir):
    by = collections.Counter(r["class"] for r in recs)
    L = ["# SUMMARY15 — grid15 at `%s`" % commit, "",
         "Generated by `gen/classify15.py` from `%s` (%d cells; the metadata from `%s`)."
         % (os.path.basename(path), len(recs), os.path.join(cells, "INDEX.jsonl")), "",
         "## Count per class", "", "| class | cells |", "|---|---|"]
    for k, v in sorted(by.items()):
        L.append("| %s | %d |" % (k, v))
    L.append("| **generated** | **%d** |" % len(recs))
    L += ["", "## Expectation vs verdict", "", "| expectation | npkc 0 | npkc 1 | other |", "|---|---|---|---|"]
    for e in ("REFUSE", "SAFE"):
        rs = [r for r in recs if r["expect"] == e]
        L.append("| %s | %d | %d | %d |" % (e, sum(r["npkc"] == 0 for r in rs), sum(r["npkc"] == 1 for r in rs),
                                          sum(r["npkc"] not in (0, 1) for r in rs)))
    classes = sorted(by)
    for axis in AXES:
        vals = sorted(set(str(r.get(axis)) for r in recs))
        L += ["", "## Per class per %s" % axis, "", "| %s | %s |" % (axis, " | ".join(classes)),
              "|---|%s" % ("---|" * len(classes))]
        for v in vals:
            c = collections.Counter(r["class"] for r in recs if str(r.get(axis)) == v)
            L.append("| %s | %s |" % (v, " | ".join(str(c.get(k, 0)) for k in classes)))
    codes = collections.Counter(",".join(r["codes"]) for r in recs if r["npkc"] == 1)
    L += ["", "## Refusal codes", "", "| codes | cells |", "|---|---|"]
    for k, v in codes.most_common():
        L.append("| %s | %d |" % (k or "(none)", v))
    cm = [r for r in recs if r["exp_mismatch"] == "codes"]
    L += ["", "## Refused, but without every code expected (%d)" % len(cm), ""]
    if cm:
        cc = collections.Counter((",".join(r["expect_codes"]), ",".join(r["codes"])) for r in cm)
        L += ["| expected | got | cells |", "|---|---|---|"] + ["| %s | %s | %d |" % (k[0], k[1], v)
                                                              for k, v in cc.most_common()]
    else:
        L.append("(none)")
    look = [r for r in recs if r["class"] not in ("refused", "clean")]
    L += ["", "## Every cell to triage (not `refused`, not `clean`) (%d)" % len(look), ""]
    if look:
        L += ["| cell | class | npkc | codes | O0 | O2 | R | W | V | B | reg155 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in look:
            L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["id"], r["class"], r["npkc"], ",".join(r["codes"]) or "-", r["O0"], r["O2"], r["R"], r["W"],
                r["V"], r["B"], r["reg155"]))
    else:
        L.append("(none)")
    with open(os.path.join(outdir, "SUMMARY15.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ the recall gate
def _by_id(recs):
    out, dups = {}, []
    for r in recs:
        if r["id"] in out:
            dups.append(r["id"])
        out[r["id"]] = r
    return out, dups


def gate(h6, reg, metas, h6_sha, reg_sha):
    """h6, reg: classified records (lists); metas: id -> INDEX meta; the pinned shas as strings.
    Prints every check; -> (tags, exit code, findings)."""
    tags = []

    def res(tag, failed, detail):
        if failed:
            tags.append(tag)
            print("TAG %s — %s" % (tag, detail))
        else:
            print("ok  %s — %s" % (tag, detail))

    H, hd = _by_id(h6)
    R, rd = _by_id(reg)
    idx = set(metas)
    # 1. COMMIT
    hc, rc_ = sorted(set(str(r.get("commit")) for r in h6)), sorted(set(str(r.get("commit")) for r in reg))
    res("COMMIT", not (hc == [h6_sha] and rc_ == [reg_sha] and h6_sha != reg_sha),
        "the HUNT6 file's commit %s (pinned %s), the REG155 file's %s (pinned %s)" % (
            ",".join(hc) or "-", h6_sha, ",".join(rc_) or "-", reg_sha))
    # 2. COVERAGE
    hs, rs = set(H), set(R)
    bad = hs != idx or rs != idx or hs != rs or hd or rd
    res("COVERAGE", bad, "%d index ids; HUNT6 %d records (%d missing, %d extra, %d doubled), REG155 %d records "
                         "(%d missing, %d extra, %d doubled)" % (
                             len(idx), len(h6), len(idx - hs), len(hs - idx), len(hd), len(reg), len(idx - rs),
                             len(rs - idx), len(rd)))
    if bad:
        for name, s in (("HUNT6", hs), ("REG155", rs)):
            for i in sorted(idx - s)[:5]:
                print("    %s lacks %s" % (name, i))
            for i in sorted(s - idx)[:5]:
                print("    %s has %s, not in the index" % (name, i))
    # 3. SEED-RECALL
    miss = [s for s in SEEDS8 if R.get(s, {}).get("class") != "ACCEPTED:DEFECT:uaf"]
    res("SEED-RECALL", bool(miss), "%d of the 8 named DEF-296 seeds ACCEPTED:DEFECT:uaf at REG155%s" % (
        len(SEEDS8) - len(miss), "".join("; %s is %s" % (s, R.get(s, {}).get("class", "missing")) for s in miss)))
    # 4. LEAK-RECALL
    leak = [i for i in sorted(idx) if metas[i].get("reg155") == "leak"]
    miss = [i for i in leak if i in R and not str(R[i]["class"]).startswith("ACCEPTED:DEFECT:")]
    res("LEAK-RECALL", bool(miss), "%d of %d reg155==\"leak\" cells ACCEPTED:DEFECT:* at REG155%s" % (
        len(leak) - len(miss), len(leak), "".join("; %s is %s" % (i, R[i]["class"]) for i in miss)))
    hazard = [i for i in sorted(idx) if metas[i].get("V") in ("pp", "seed")]
    # 5. SILENT-PASS
    silent = [(i, leg, F[i]["class"]) for i in hazard for leg, F in (("HUNT6", H), ("REG155", R))
              if i in F and F[i]["class"] in SILENT]
    res("SILENT-PASS", bool(silent), "%d hazard cells ACCEPTED:clean/other/timeout at either compiler (of %d)%s"
        % (len(silent), len(hazard), "".join("; %s %s at %s" % (i, c, leg) for i, leg, c in silent)))
    # 6. TWIN
    twins = [i for i in sorted(idx) if metas[i].get("V") == "twin"]
    nt = [(i, leg, F[i]["class"]) for i in twins for leg, F in (("HUNT6", H), ("REG155", R))
          if i in F and F[i]["class"] != "clean"]
    res("TWIN", bool(nt), "%d of %d twins clean at both compilers%s" % (
        len(twins) - len(set(i for i, _, _ in nt)), len(twins), "".join("; %s %s at %s" % (i, c, leg)
                                                                          for i, leg, c in nt)))
    # 7. CODE-H6 and CODE-REG
    rh = [i for i in hazard if i in H and H[i]["class"] == "refused"]
    bh = [i for i in rh if exp_mismatch({"npkc": 1, "expect": "REFUSE", "codes": H[i]["codes"]}, metas[i]) != ""]
    res("CODE-H6", bool(bh), "%d of %d hazard cells refused at HUNT6 name every expected code%s" % (
        len(rh) - len(bh), len(rh), "".join("; %s %s, expected %s" % (i, ",".join(H[i]["codes"]) or "-",
                                                                     ",".join(metas[i]["expect_codes"])) for i in bh)))
    rr = [i for i in hazard if i in R and R[i]["class"] == "refused"]
    br = [i for i in rr if not R[i]["codes"] or any(not c.startswith("NITPICK-BORROW-") for c in R[i]["codes"])]
    res("CODE-REG", bool(br), "%d of %d hazard cells refused at REG155 name only NITPICK-BORROW- codes%s" % (
        len(rr) - len(br), len(rr), "".join("; %s %s" % (i, ",".join(R[i]["codes"]) or "-") for i in br)))
    # 8. UNANCHORED
    un = [i for i in sorted(idx) if metas[i].get("V") == "pp" and metas[i].get("reg155") is None
          and H.get(i, {}).get("class") == "refused" and R.get(i, {}).get("class") == "refused"]
    res("UNANCHORED", bool(un), "%d pp cells with reg155 None refused at both compilers%s" % (
        len(un), "".join("; %s" % i for i in un)))
    # 9. FINDINGS and REGRESSION
    findings = [i for i in hazard if i in H and str(H[i]["class"]).startswith("ACCEPTED:DEFECT:")]
    regress = [i for i in findings if R.get(i, {}).get("class") == "refused"]
    res("REGRESSION", bool(regress), "%d hazard cells refused at REG155 and ACCEPTED:DEFECT:* at HUNT6%s" % (
        len(regress), "".join("; %s" % i for i in regress)))
    print("FINDINGS: %d hazard cells ACCEPTED:DEFECT:* at HUNT6 (for triage, not a failure)" % len(findings))
    for i in findings:
        m = metas[i]
        print("    %s  R=%s W=%s V=%s B=%s  HUNT6 %s %s/%s  REG155 %s  key %s" % (
            i, m.get("R"), m.get("W"), m.get("V"), m.get("B"), H[i]["class"], H[i].get("O0"), H[i].get("O2"),
            R.get(i, {}).get("class", "missing"), m.get("key")))
    rest = [i for i in hazard if i in H and H[i]["class"] not in ("refused",) + SILENT
            and not str(H[i]["class"]).startswith("ACCEPTED:DEFECT:")]
    if rest:
        print("OTHER hazard classes at HUNT6: %s" % ", ".join("%s %s" % (i, H[i]["class"]) for i in rest))
    rc = 3 if "REGRESSION" in tags else (1 if tags else 0)
    print("gate: %d checks failed%s; exit %d" % (len(tags), (" (" + ", ".join(tags) + ")") if tags else "", rc))
    return tags, rc, findings


def recall(cells, h6_path, reg_path):
    metas = load_index(cells)
    h6 = [json.loads(l) for l in open(h6_path, encoding="utf-8") if l.strip()]
    reg = [json.loads(l) for l in open(reg_path, encoding="utf-8") if l.strip()]
    pins = []
    for name in ("H6", "REG"):
        with open(os.path.join(ROOT, ".work", name), encoding="utf-8") as fh:
            pins.append(fh.read().strip())
    print("# recall gate: HUNT6 %s, REG155 %s; pinned .work/H6 %s, .work/REG %s" % (h6_path, reg_path, *pins))
    tags, rc, findings = gate(h6, reg, metas, pins[0], pins[1])
    return rc


# ------------------------------------------------------------------ the selftest
H6_SHA, REG_SHA = "aaaaaaa", "bbbbbbb"


def _metas():
    metas = collections.OrderedDict()

    def m(i, V, reg155, codes=("NITPICK-BORROW-015",), R="seed", W="seed", B="seed"):
        e = "SAFE" if V == "twin" else "REFUSE"
        metas[i] = {"id": i, "V": V, "R": R, "W": W, "B": B, "reg155": reg155, "expect": e,
                    "expect_codes": list(codes) if e == "REFUSE" else [], "expect_exit": 0 if e == "SAFE" else None,
                    "key": None}
    for s in SEEDS8:
        m(s, "seed", "leak")
    m("elem_callee", "seed", "refuse", ("NITPICK-BORROW-002",))
    for n, (R, reg155) in enumerate((("pl", "leak"), ("fld", "refuse"), ("cbv", "leak")), 1):
        m("n%03d_pp_%s_dir_same" % (2 * n - 1, R), "pp", reg155, R=R, W="dir", B="same")
        m("n%03d_twin_%s_dir_same" % (2 * n, R), "twin", None, (), R=R, W="dir", B="same")
    return metas


PL, FLD, CBV = "n001_pp_pl_dir_same", "n003_pp_fld_dir_same", "n005_pp_cbv_dir_same"
TW_PL = "n002_twin_pl_dir_same"


def _rec(meta, commit, npkc, codes=(), o0="-", o2="-"):
    r = {"id": meta["id"], "npkc": npkc, "codes": list(codes), "O0": o0, "O2": o2, "expect": meta["expect"],
         "expect_exit": meta["expect_exit"], "commit": commit}
    r["class"] = classify(r)
    r["exp_mismatch"] = exp_mismatch(r, meta)
    return r


def _good(metas):
    """The good pair: the seeds refused at HUNT6 and 170/170 at REG155; elem_callee refused at both (BORROW-002);
    pl refused at HUNT6, 70/70 at REG155; fld refused at both; cbv 70/70 at both (an open hole, a finding);
    the twins 0/0 at both."""
    h6, reg = {}, {}
    for i, m in metas.items():
        if m["V"] == "twin":
            h6[i], reg[i] = _rec(m, H6_SHA, 0, o0=0, o2=0), _rec(m, REG_SHA, 0, o0=0, o2=0)
        elif i in SEEDS8:
            h6[i], reg[i] = _rec(m, H6_SHA, 1, m["expect_codes"]), _rec(m, REG_SHA, 0, o0=170, o2=170)
        elif m["reg155"] == "refuse":
            h6[i], reg[i] = _rec(m, H6_SHA, 1, m["expect_codes"]), _rec(m, REG_SHA, 1, m["expect_codes"])
        elif i == CBV:
            h6[i], reg[i] = _rec(m, H6_SHA, 0, o0=70, o2=70), _rec(m, REG_SHA, 0, o0=70, o2=70)
        else:
            h6[i], reg[i] = _rec(m, H6_SHA, 1, m["expect_codes"]), _rec(m, REG_SHA, 0, o0=70, o2=70)
    return h6, reg


def selftest():
    if run_class({"O0": 70, "O2": 70, "expect": "REFUSE"}, 0) != "DEFECT:uaf":
        print("FAIL classify13's run_class does not read 70/70 as DEFECT:uaf")
        return 1
    cases = []

    def case(name, want_tags, want_rc, edit=None, want_finding=None, want_findings=False):
        metas = _metas()
        h6, reg = _good(metas)
        h6_sha, reg_sha = H6_SHA, REG_SHA
        if edit:
            edit(metas, h6, reg)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tags, rc, findings = gate(list(h6.values()), list(reg.values()), metas, h6_sha, reg_sha)
        printed = set(l.split()[1] for l in buf.getvalue().splitlines() if l.startswith("TAG "))
        ok = printed == set(want_tags) == set(tags) and rc == want_rc
        if want_finding:
            ok = ok and want_finding in findings
        if want_findings:
            ok = ok and bool(findings)
        cases.append((name, ok, printed, rc))

    def put(F, metas, i, commit, npkc, codes=(), o0="-", o2="-"):
        F[i] = _rec(metas[i], commit, npkc, codes, o0, o2)

    def swap_commits(metas, h6, reg):
        for r in h6.values():
            r["commit"] = REG_SHA
        for r in reg.values():
            r["commit"] = H6_SHA

    def same_commits(metas, h6, reg):
        for r in reg.values():
            r["commit"] = H6_SHA

    def extra_twin(metas, h6, reg):
        t = dict(h6[TW_PL])
        t["id"] = "n999_twin_pl_dir_same"
        h6[t["id"]] = t

    def regression(metas, h6, reg):
        put(h6, metas, FLD, H6_SHA, 0, o0=70, o2=70)

    case("good pair: seeds uaf@REG, leak cells uaf@REG, twins clean, codes, anchored, coverage, commits", [], 0,
         want_findings=True)
    case("COMMIT: both files carry the same commit", ["COMMIT"], 1, same_commits)
    case("COMMIT: the two files' commits swapped", ["COMMIT"], 1, swap_commits)
    case("COVERAGE: an extra id in one file, a benign twin clean at HUNT6", ["COVERAGE"], 1, extra_twin)
    case("SEED-RECALL: a named seed ACCEPTED:DEFECT:double_free@REG (95/95)", ["SEED-RECALL"], 1,
         lambda M, h, r: put(r, M, SEEDS8[2], REG_SHA, 0, o0=95, o2=95))
    case("SEED-RECALL: a named seed ACCEPTED:DEFECT:false_trap@REG (91/91)", ["SEED-RECALL"], 1,
         lambda M, h, r: put(r, M, SEEDS8[5], REG_SHA, 0, o0=91, o2=91))
    case("LEAK-RECALL: pp:pl:dir:same (leak, refused@HUNT6) refused@REG with BORROW-015", ["LEAK-RECALL"], 1,
         lambda M, h, r: put(r, M, PL, REG_SHA, 1, ["NITPICK-BORROW-015"]))
    case("SILENT-PASS: a leak pp cell ACCEPTED:clean@HUNT6 (0/0)", ["SILENT-PASS"], 1,
         lambda M, h, r: put(h, M, PL, H6_SHA, 0, o0=0, o2=0))
    case("SILENT-PASS: a leak pp cell ACCEPTED:other@HUNT6 (5/5)", ["SILENT-PASS"], 1,
         lambda M, h, r: put(h, M, PL, H6_SHA, 0, o0=5, o2=5))
    case("SILENT-PASS: pp:fld:dir:same (refuse) ACCEPTED:timeout@REG155", ["SILENT-PASS"], 1,
         lambda M, h, r: put(r, M, FLD, REG_SHA, 0, o0="T", o2="T"))
    case("TWIN@REG155: a twin not clean at REG155 (70/70, DEFECT:uaf), clean@HUNT6", ["TWIN"], 1,
         lambda M, h, r: put(r, M, TW_PL, REG_SHA, 0, o0=70, o2=70))
    case("TWIN@HUNT6: a twin not clean at HUNT6 (refused, OVERRESTRICT), clean@REG155", ["TWIN"], 1,
         lambda M, h, r: put(h, M, TW_PL, H6_SHA, 1, ["NITPICK-BORROW-015"]))
    case("CODE-H6: pp:fld:dir:same refused@HUNT6 with PARSE-001 only, clean BORROW-015@REG", ["CODE-H6"], 1,
         lambda M, h, r: put(h, M, FLD, H6_SHA, 1, ["NITPICK-PARSE-001"]))
    case("CODE-REG: pp:fld:dir:same refused@REG with BORROW-015 and PARSE-001, clean@HUNT6", ["CODE-REG"], 1,
         lambda M, h, r: put(r, M, FLD, REG_SHA, 1, ["NITPICK-BORROW-015", "NITPICK-PARSE-001"]))
    case("UNANCHORED: a pp cell with reg155 None refused at both", ["UNANCHORED"], 1,
         lambda M, h, r: M[FLD].update(reg155=None))
    case("FINDINGS: pp:pl:dir:same ACCEPTED:DEFECT:uaf@HUNT6, leak@REG: listed, no tag", [], 0,
         lambda M, h, r: put(h, M, PL, H6_SHA, 0, o0=70, o2=70), want_finding=PL)
    case("REGRESSION: pp:fld:dir:same (refuse) refused@REG, ACCEPTED:DEFECT:uaf@HUNT6", ["REGRESSION"], 3, regression)
    case("REGRESSION outranks: a regression and a COVERAGE breakage", ["REGRESSION", "COVERAGE"], 3,
         lambda M, h, r: (regression(M, h, r), extra_twin(M, h, r)))
    width = max(len(c[0]) for c in cases)
    for name, ok, printed, rc in cases:
        print("%s  %-*s -> {%s}, exit %d" % ("ok  " if ok else "FAIL", width, name, ", ".join(sorted(printed)), rc))
    npass = sum(1 for c in cases if c[1])
    print("selftest: %d cases, %d pass" % (len(cases), npass))
    return 0 if npass == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="?")
    ap.add_argument("--cells", default="cells15")
    ap.add_argument("--recall", nargs=2, metavar=("HUNT6", "REG155"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.recall:
        sys.exit(recall(a.cells, a.recall[0], a.recall[1]))
    if not a.results:
        sys.exit(__doc__)
    classify_file(a.results, a.cells)


if __name__ == "__main__":
    main()
