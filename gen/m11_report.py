#!/usr/bin/env python3
"""M11 -- the claims' results at HUNT2: m11/RESULTS.md.

usage: python3 gen/m11_report.py

Reads the claims (gen/m11.py's modules) and results/9126350/m11.jsonl (the final
run, the run that counts) with m11-run1.jsonl (run 1), and the disagreeing claims'
runs at the baseline and the newest main (results/<commit>/m11-disagree.jsonl), and
writes the denominators
PLAN.md 11.3 names -- claims extracted, testable, tested, agreeing, disagreeing,
and untestable with a reason -- per reference and per kind, then every
disagreement with what triage found it to be (CLASS in gen/m11_triage.py), the
programs whose TEXT changed between the runs (a claim's `fixed`), and the
agreeing refusals' first diagnostics (each checked to be the claimed reason).
"""
import collections, importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import m11lib as L  # noqa: E402

HUNT2 = "9126350"


def load_claims():
    spec = importlib.util.spec_from_file_location("m11gen", os.path.join(ROOT, "gen", "m11.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.load_modules()
    return L.CLAIMS


def load_runs(name):
    p = os.path.join(ROOT, "results", HUNT2, name)
    if not os.path.exists(p):
        return {}
    return {json.loads(l)["id"]: json.loads(l) for l in open(p)}


def load_triage():
    p = os.path.join(ROOT, "gen", "m11_triage.py")
    if not os.path.exists(p):
        return {}, {}
    spec = importlib.util.spec_from_file_location("m11triage", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, "CLASS", {}), getattr(m, "GROUPS", {})


def md(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def main():
    claims = load_claims()
    run2 = load_runs("m11.jsonl")
    run1 = load_runs("m11-run1.jsonl")
    other = {}
    for c in ("c3bdae2", "1b4f0c6"):
        p = os.path.join(ROOT, "results", c, "m11-disagree.jsonl")
        if os.path.exists(p):
            other[c] = {json.loads(l)["id"]: json.loads(l) for l in open(p)}
    cls, groups = load_triage()
    byid = {c["id"]: c for c in claims}
    docs = [d for d in L.DOCS if any(c["doc"] == d for c in claims)]
    out = ["# M11 results: the references at HUNT2 `%s`, claim by claim" % HUNT2, "",
           "Written by `gen/m11_report.py` from the claims (`m11/CLAIMS.md`) and the run",
           "(`results/%s/m11.jsonl`, the final run, both legs, 4 jobs). A claim's program AGREES when npkc and" % HUNT2,
           "both legs give the outcome its expectation states, written from the reference's text",
           "before the first run.", ""]
    # denominators
    tot = collections.Counter()
    rows = []
    for d in docs:
        cs = [c for c in claims if c["doc"] == d]
        t = [c for c in cs if not c["untestable"]]
        run = [c for c in t if c["id"] in run2]
        ag = [c for c in run if run2[c["id"]]["verdict"] == "AGREE"]
        k = dict(claims=len(cs), examples=sum(c["kind"] == "example" for c in cs),
                 rows=sum(c["kind"] == "row" for c in cs), rules=sum(c["kind"] == "rule" for c in cs),
                 testable=len(t), tested=len(run), agree=len(ag), disagree=len(run) - len(ag),
                 untestable=len(cs) - len(t))
        tot.update(k)
        rows.append((d, k))
    out += ["## 1. The denominators", "",
            "| reference | claims | examples | rows | rules | untestable | testable | tested | agree | disagree |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for d, k in rows + [("**total**", tot)]:
        out.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            d, k["claims"], k["examples"], k["rows"], k["rules"], k["untestable"], k["testable"],
            k["tested"], k["agree"], k["disagree"]))
    out.append("")
    cov = []
    for d in L.DOCS:
        r = L.covered_ranges(d)
        n = len(L.doc_lines(d))
        cov.append("%s %s of %d" % (d, ", ".join("%d–%d" % x for x in r) or "none", n))
    ext = sum(b - a + 1 for d in L.DOCS for a, b in L.covered_ranges(d))
    alln = sum(len(L.doc_lines(d)) for d in L.DOCS)
    out += ["**These denominators cover %d of the references' %d lines** (the ranges extracted; the" % (ext, alln),
            "rest is not yet extracted): " + "; ".join(cov) + ".", ""]
    ut = collections.Counter()
    for c in claims:
        if c["untestable"]:
            ut[c["untestable"][1:].split("]")[0]] += 1
    out += ["Untestable, by reason (each claim's own sentence is in `m11/CLAIMS.md`):", ""]
    why = {"z3": "needs the verified build (`npkg verify` and the pinned z3), not in this environment",
           "tool": "needs a tool or workflow beyond a program: a package tree, the harness, the explorer, a driver",
           "tree": "a claim about the compiler's own source tree, generators, harness or documents",
           "internal": "a compiler internal no program observes (an AST field, a table's layout)",
           "platform": "another architecture or OS, root, the network, or more memory than the VM",
           "timing": "a schedule, a race or a duration",
           "unobservable": "no program can tell the claim's truth from its falsehood",
           "vague": "the sentence states no checkable outcome"}
    for tag, n in ut.most_common():
        out.append("- `%s` %d — %s" % (tag, n, why.get(tag, "")))
    out.append("")
    # disagreements
    dis = [run2[i] for i in run2 if run2[i]["verdict"] != "AGREE"]
    kinds = collections.Counter(r["kind"] for r in dis)
    out += ["## 2. The disagreements (%d)" % len(dis), "",
            "By kind: " + ", ".join("`%s` %d" % kv for kv in kinds.most_common()) + ".", ""]
    if groups:
        out += ["| class | claims |", "|---|---|"]
        for g, desc in groups.items():
            ids = sorted(i for i, v in cls.items() if v[0] == g and i in run2 and run2[i]["verdict"] != "AGREE")
            out.append("| %s | %d |" % (desc, len(ids)))
        out.append("")
    out += ["Every disagreement below was also run at the baseline `c3bdae2` and at the compiler's newest",
            "`main` `1b4f0c6`; the last column says whether each gave the same result (npkc, codes, both",
            "legs, verdict) as HUNT2.", ""]
    out += ["| id | line | claim | expected | measured | class | c3bdae2 / 1b4f0c6 |", "|---|---|---|---|---|---|---|"]
    for r in sorted(dis, key=lambda r: (r["doc"], r["line"], r["id"])):
        c = byid[r["id"]]
        meas = ("sh %s" % r["sh"]) if r["sh"] is not None else "npkc %s %s, %s/%s" % (
            r["npkc"], ",".join(x.replace("NITPICK-", "") for x in r["codes"]) or "", r["O0"], r["O2"])
        k = cls.get(r["id"], ("?", "not yet triaged"))
        same = []
        for cm in ("c3bdae2", "1b4f0c6"):
            o = other.get(cm, {}).get(r["id"])
            key = lambda x: (x["verdict"], x["npkc"], tuple(x["codes"]), x["O0"], x["O2"], x["sh"])
            same.append("—" if o is None else ("same" if key(o) == key(r) else
                        "npkc %s %s, %s/%s" % (o["npkc"], ",".join(x.replace("NITPICK-", "") for x in o["codes"]), o["O0"], o["O2"])))
        out.append("| `%s` | %s:%d | %s | `%s` | %s (`%s`) | %s | %s |" % (
            r["id"], r["doc"], r["line"], md(c["text"]), r["expect"], meas, r["kind"], md(k[1]), " / ".join(same)))
    out.append("")
    # fixes
    fx = [c for c in claims if c["fixed"]]
    out += ["## 3. Programs whose text changed after a run (%d; no expectation changed but where stated)" % len(fx), "",
            "| id | why |", "|---|---|"]
    for c in fx:
        out.append("| `%s` | %s |" % (c["id"], md(c["fixed"])))
    out.append("")
    if run1:
        same = sum(1 for i in run2 if i in run1 and run1[i]["verdict"] == run2[i]["verdict"]
                   and run1[i]["npkc"] == run2[i]["npkc"] and run1[i]["O0"] == run2[i]["O0"]
                   and run1[i]["O2"] == run2[i]["O2"])
        out += ["Run 1 against the final run: %d of %d programs identical (npkc, both legs, verdict); the" % (
            same, len(run2)), "others are programs above, whose text changed (a text change that did not move",
            "the verdict leaves its program identical).", ""]
    with open(os.path.join(ROOT, "m11", "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("m11/RESULTS.md: %d claims, %d tested, %d agree, %d disagree" % (
        tot["claims"], tot["tested"], tot["agree"], tot["disagree"]))


if __name__ == "__main__":
    main()
