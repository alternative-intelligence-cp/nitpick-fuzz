#!/usr/bin/env python3
"""M10 — run the checklist's programs at one compiler and judge each against the
expectation written from the reference text (m10/EXPECT.tsv).

usage: python3 gen/m10_run.py <compiler-dir> [--jobs 4] [--ids ID ...] [--out FILE]
                              [--llvm .work/llvm]

Each program is compiled, linked and run on both legs by PLAN.md's recipe
(gen/snip.py's build_and_run: a private copy of m10/programs/, a 120 s compile,
a 10 s run, T on a timeout, 128+N on a signal). One named line per program:
  <id> @<commit> npkc=<rc> [codes] O0=<rc> O2=<rc> expect=<e> -> AGREE | DISAGREE:<kind>
and one JSON line each in results/<commit>/m10.jsonl (overwritten). The
expectation is the TSV's `expect_base` column at c3bdae2 and `expect_hunt2`
elsewhere. Kinds of disagreement:
  accepted      expected a refusal, npkc 0 (the run's exits say what the program computed)
  refused       expected a run, npkc 1
  other_code    refused, but not with the expected code
  wrong_exit    compiled, both legs agree, and the exit is not the expected one
  leg_mismatch  compiled, and -O0 differs from -O2
  crash         npkc exited other than 0 or 1
  timeout       a leg hit the run timeout
"""
import argparse, concurrent.futures as cf, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snip import build_and_run  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_expect():
    rows = []
    with open(os.path.join(ROOT, "m10", "EXPECT.tsv")) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(head, line.rstrip("\n").split("\t"))))
    return rows


def judge(expect, r):
    """-> (verdict, kind)."""
    if r["npkc"] not in (0, 1):
        return "DISAGREE", "crash"
    kind, _, val = expect.partition(":")
    if kind == "refuse":
        if r["npkc"] == 0:
            return "DISAGREE", "accepted"
        if val and val not in r["codes"]:
            return "DISAGREE", "other_code"
        return "AGREE", ""
    want = int(val)
    if r["npkc"] == 1:
        return "DISAGREE", "refused"
    if "T" in (r["O0"], r["O2"]):
        return "DISAGREE", "timeout"
    if r["O0"] != r["O2"]:
        return "DISAGREE", "leg_mismatch"
    if r["O0"] != want:
        return "DISAGREE", "wrong_exit"
    return "AGREE", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("compiler")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--ids", nargs="*", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--llvm", default=os.path.join(ROOT, ".work", "llvm"))
    a = ap.parse_args()
    comp = os.path.abspath(a.compiler)
    commit = subprocess.run(["git", "-C", comp, "rev-parse", "--short=7", "HEAD"],
                            stdout=subprocess.PIPE).stdout.decode().strip()
    rows = load_expect()
    if a.ids:
        rows = [r for r in rows if r["id"] in set(a.ids)]
    col = "expect_base" if commit == "c3bdae2" else "expect_hunt2"
    out = a.out or os.path.join(ROOT, "results", commit, "m10.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    def one(row):
        r = build_and_run(os.path.join(ROOT, "m10", row["file"]), comp, os.path.abspath(a.llvm))
        v, k = judge(row[col], r)
        return row, r, v, k

    recs = {}
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for row, r, v, k in ex.map(one, rows):
            line = "%-40s @%s npkc=%s %s O0=%s O2=%s expect=%s -> %s" % (
                row["id"], commit, r["npkc"], ",".join(r["codes"]) or "-", r["O0"], r["O2"],
                row[col], v + (":" + k if k else ""))
            print(line, flush=True)
            recs[row["id"]] = dict(id=row["id"], area=row["area"], commit=commit, expect=row[col],
                                   npkc=r["npkc"], codes=r["codes"], msg=r["msg"],
                                   O0=r["O0"], O2=r["O2"], verdict=v, kind=k)
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(recs[row["id"]]) + "\n")
    agree = sum(1 for x in recs.values() if x["verdict"] == "AGREE")
    print("%s: %d programs, %d agree, %d disagree -> %s" % (commit, len(recs), agree,
                                                           len(recs) - agree, out))


if __name__ == "__main__":
    main()
