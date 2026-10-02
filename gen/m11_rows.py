#!/usr/bin/env python3
"""M11 -- the row tables of the two findings made of claims (F-027, F-028).

usage: python3 gen/m11_rows.py

For each claim that gen/m11_triage.py classes `comp` (F-027) or `doc` (F-028), one
row: the reference sentence's file and line, the claim, its program in m11/programs/,
the expectation written from the text, and the measured result at HUNT2 (the final
run, results/9126350/m11.jsonl), at the baseline and at the compiler's newest `main`
(results/<commit>/m11-disagree.jsonl). Writes ROWS.md beside each README.
"""
import importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import m11lib as L  # noqa: E402

# a row finding: its id (the prefix of each claim's class text) -> its directory
FINDINGS = {"F-027": "F-027-lower-priority-compiler-rows",
            "F-028": "F-028-m11-reference-sentences-the-compiler-contradicts",
            "F-030": "F-030-memory-reference-sentences-the-compiler-contradicts"}
NEWEST = ("93bcb66", "1b4f0c6")   # the compiler's newest main, newest first (S37, S49)


def load(path):
    return {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, path))}


def meas(r):
    if r is None:
        return "—"
    if r["sh"] is not None:
        return "script %s" % r["sh"]
    codes = ",".join(x.replace("NITPICK-", "") for x in r["codes"])
    return "npkc %s%s, %s / %s" % (r["npkc"], (" " + codes) if codes else "", r["O0"], r["O2"])


def md(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def main():
    spec = importlib.util.spec_from_file_location("m11gen", os.path.join(ROOT, "gen", "m11.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.load_modules()
    byid = {c["id"]: c for c in L.CLAIMS}
    spec = importlib.util.spec_from_file_location("m11triage", os.path.join(ROOT, "gen", "m11_triage.py"))
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    h = load("results/9126350/m11.jsonl")
    b = load("results/c3bdae2/m11-disagree.jsonl")
    newest = {c: load("results/%s/m11-disagree.jsonl" % c) for c in NEWEST
              if os.path.exists(os.path.join(ROOT, "results", c, "m11-disagree.jsonl"))}
    key = lambda r: (r["verdict"], r["npkc"], tuple(r["codes"]), r["O0"], r["O2"], r["sh"])
    for fid, d in FINDINGS.items():
        ids = sorted((i for i, v in t.CLASS.items() if v[1].startswith(fid)),
                     key=lambda i: (t.CLASS[i][1], byid[i]["doc"], byid[i]["line"], i))
        nc = next((c for c in NEWEST if c in newest and all(i in newest[c] for i in ids)), NEWEST[-1])
        n = newest.get(nc, {})
        out = ["# %s — the rows (written by `gen/m11_rows.py`)" % d[:5], "",
               "One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is",
               "`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it",
               "first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the",
               "compiler's newest `main` `%s`; \"same\" is the same npkc, codes, both legs and verdict" % nc,
               "as HUNT2.", ""]
        cur = None
        for i in ids:
            what = t.CLASS[i][1]
            if what != cur:
                out += ["", "**%s**" % md(what), "",
                        "| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `%s` |" % nc,
                        "|---|---|---|---|---|---|---|"]
                cur = what
            c, r = byid[i], h[i]
            ob = "same" if i in b and key(b[i]) == key(r) else meas(b.get(i))
            on = "same" if i in n and key(n[i]) == key(r) else meas(n.get(i))
            out.append("| `%s` | %s:%d | %s | `%s` | %s | %s | %s |" % (
                i, L.DOCS[c["doc"]][1].split("/")[-1], c["line"], md(c["text"]), r["expect"], meas(r), ob, on))
        with open(os.path.join(ROOT, "findings", d, "ROWS.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
        print("%s: %d rows" % (d, len(ids)))


if __name__ == "__main__":
    main()
