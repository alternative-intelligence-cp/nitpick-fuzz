#!/usr/bin/env python3
"""M10 — the checklist's results at both compilers: m10/RESULTS.md.

usage: python3 gen/m10_report.py

Reads the checklist (gen/m10.py's ITEMS) and results/<commit>/m10.jsonl for
HUNT2 9126350 and the baseline c3bdae2, and writes the denominators PLAN.md
10.4 names (items, testable, agreeing, disagreeing, untestable with a reason),
the counts per area, and every disagreement with what it was found to be
(CLASS below, written after triage) and the agreeing items that settle a
contradiction between two reference sentences (SETTLES).
"""
import importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILERS = [("9126350", "HUNT2"), ("c3bdae2", "baseline")]

# every item that disagreed at either compiler (run 2), and what triage found
CLASS = {
    "h02_for_binding_shadow": "**F-011**: the `for` binding outlives its loop in the emitter (a silent wrong value; an out-of-bounds read with another type)",
    "l06_for_inclusive_to_int8_max": "**F-012**: a signed inclusive range ending at its type's maximum runs zero times",
    "l08_for_inclusive_to_int64_max": "**F-012**: as `l06`, at int64",
    "l11_till_nonpositive_limit": "**F-014**: `till` with a negative limit counts down",
    "m06_spaceship": "**F-015**: `<=>` refused by the emitter (`EMIT-002`)",
    "p05_negative_patterns": "**F-016**: a negative range pattern refused by the emitter (`EMIT-002`); its `(-1i32)` arm compiles",
    "t02_length_spelled_length": "**F-017 d1** (documentation): the member is `.len`",
    "t08_string_index": "**F-017 d2** (documentation): a string cannot be indexed",
    "t09_string_index_past_end": "**F-017 d2** (documentation), as `t08`",
    "l28_for_binding_type_mismatch": "**F-017 d6** (documentation): refused, as `TYPE-007` not `TYPE-033`",
    "v12_constant_div_by_zero": "**F-017 d7** (documentation): accepted in a local initialiser, traps at run time",
    "c18_int_to_tag_only_enum": "known **DEF-101** at the baseline (its reference's sentence, since corrected)",
    "t04_block_string_quotes": "known **DEF-98** at the baseline (fixed at `395308f`)",
}
# agreeing items whose run settles which of two reference sentences is stale
SETTLES = {
    "m07_nan_comparisons": "**F-017 d3**: `!=` is `une` (§1.4), not §28's `fcmp one`",
    "x05_ternary_evaluates_one_branch": "**F-017 d4**: the ternary branches (VERIFICATION §1.2), not §28's `select`",
    "o16_int128_add": "**F-017 d5**: `int128` traps (§1.2, D-210), not §4's 'D-037 wrapping'",
}
# programs re-spelled after run 1 (S36): the expectation unchanged
FIXED = {
    "m12_tbb_compare_on_err_traps": "run 1 spelled `>`, refused `TYPE-008` (tbb has no ordering, D-093)",
    "d16_uninit_owning_field_overwrite": "run 1 wrote the fields directly, refused `ASSIGN-001` (D-010); now D-225's `$$m` idiom",
}


def load_items():
    spec = importlib.util.spec_from_file_location("m10", os.path.join(ROOT, "gen", "m10.py"))
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["x"]
    spec.loader.exec_module(m)
    sys.argv = argv
    return m.ITEMS


def main():
    items = load_items()
    res = {}
    for c, _ in COMPILERS:
        with open(os.path.join(ROOT, "results", c, "m10.jsonl")) as f:
            res[c] = {json.loads(l)["id"]: json.loads(l) for l in f}
    testable = [it for it in items if not it["untestable"]]
    L = ["# M10 results: the checklist at both compilers",
         "",
         "Written by `gen/m10_report.py` from `results/<commit>/m10.jsonl` (run 2; run 1 is",
         "`m10-run1.jsonl`, and the two differ only in the two re-spelled programs listed",
         "below). The checklist, its citations and its expectations are in `CHECKLIST.md`.",
         "",
         "## The denominators (PLAN.md 10.4)",
         "",
         "| | HUNT2 `9126350` | baseline `c3bdae2` |",
         "|---|---|---|"]
    agree = {c: sum(1 for it in testable if res[c][it["id"]]["verdict"] == "AGREE") for c, _ in COMPILERS}
    L.append("| items | %d | %d |" % (len(items), len(items)))
    L.append("| testable (a program each) | %d | %d |" % (len(testable), len(testable)))
    L.append("| agreeing with the reference | %d | %d |" % (agree["9126350"], agree["c3bdae2"]))
    L.append("| disagreeing | %d | %d |" % (len(testable) - agree["9126350"], len(testable) - agree["c3bdae2"]))
    L.append("| untestable, with a reason | %d | %d |" % (len(items) - len(testable), len(items) - len(testable)))
    kinds = {}
    for c, _ in COMPILERS:
        for it in testable:
            r = res[c][it["id"]]
            if r["verdict"] != "AGREE":
                kinds.setdefault(r["kind"], {"9126350": 0, "c3bdae2": 0})[c] += 1
    for k in sorted(kinds):
        L.append("| … of which `%s` | %d | %d |" % (k, kinds[k]["9126350"], kinds[k]["c3bdae2"]))
    L += ["", "## By area", "", "| area | items | HUNT2 agree / disagree | baseline agree / disagree |",
          "|---|---|---|---|"]
    areas = []
    for it in testable:
        if it["area"] not in areas:
            areas.append(it["area"])
    for a in areas:
        its = [it for it in testable if it["area"] == a]
        cells = []
        for c, _ in COMPILERS:
            ag = sum(1 for it in its if res[c][it["id"]]["verdict"] == "AGREE")
            cells.append("%d / %d" % (ag, len(its) - ag))
        L.append("| %s | %d | %s | %s |" % (a.replace("|", "\\|"), len(its), cells[0], cells[1]))
    L += ["", "## Every disagreement, and what it is", "",
          "Each cell: npkc rc (codes) / -O0 / -O2, and the kind of disagreement; `=` where the",
          "item agrees there.", "",
          "| item | expected | HUNT2 | baseline | what it is |", "|---|---|---|---|---|"]
    missing = []
    for it in testable:
        i = it["id"]
        rs = [res[c][i] for c, _ in COMPILERS]
        if all(r["verdict"] == "AGREE" for r in rs):
            continue
        cells = []
        for r in rs:
            if r["verdict"] == "AGREE":
                cells.append("=")
            else:
                cells.append("%s%s / %s / %s: `%s`" % (r["npkc"], " (%s)" % ", ".join(c.replace("NITPICK-", "") for c in r["codes"]) if r["codes"] else "",
                                                     r["O0"], r["O2"], r["kind"]))
        exp = it["expect"] + (" (base: %s)" % it["expect_base"] if it["expect_base"] else "")
        if i not in CLASS:
            missing.append(i)
        L.append("| `%s` | %s | %s | %s | %s |" % (i, exp, cells[0], cells[1], CLASS.get(i, "UNCLASSIFIED")))
    L += ["", "## Agreeing items that settle a contradiction between two sentences", "",
          "| item | result at both | what it settles |", "|---|---|---|"]
    for i, why in SETTLES.items():
        r = res["9126350"][i]
        L.append("| `%s` | %s / %s / %s (expected %s) | %s |" % (i, r["npkc"], r["O0"], r["O2"], r["expect"], why))
    L += ["", "## Programs re-spelled after run 1 (S36; the expectation unchanged)", "",
          "| item | why | run 2 at both |", "|---|---|---|"]
    for i, why in FIXED.items():
        r = res["9126350"][i]
        L.append("| `%s` | %s | %s / %s / %s, agrees |" % (i, why, r["npkc"], r["O0"], r["O2"]))
    L += ["", "## The untestable items", "", "| item | reason |", "|---|---|"]
    for it in items:
        if it["untestable"]:
            L.append("| `%s` | %s |" % (it["id"], it["untestable"].replace("|", "\\|")))
    L.append("")
    with open(os.path.join(ROOT, "m10", "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("m10/RESULTS.md written; HUNT2 %d agree / %d; baseline %d agree / %d; unclassified: %s"
          % (agree["9126350"], len(testable), agree["c3bdae2"], len(testable), missing or "none"))


if __name__ == "__main__":
    main()
