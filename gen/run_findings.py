#!/usr/bin/env python3
"""M5.2 (c)/(d) — run each finding's programs twice at HUNT and once at the baseline.

usage: python3 gen/run_findings.py [F-NNN ...] [--hunt .work/hunt] [--base .work/base]
                                   [--runs 2] [--llvm .work/llvm] [--name VERDICTS.txt]

For every findings/F-*/ (or the ones named), each *.npk in it and in its
minimized/ folder is built and run by PLAN.md's recipe (gen/run_known.py's
build_and_run, from the program's own directory): --runs times at the hunt
compiler, once at the baseline. It writes findings/F-*/VERDICTS.txt (or the
file --name gives, so that a later compiler's record sits beside the first),
one line per program per run naming the compiler commit, and prints whether
the HUNT runs agree with each other.

M9: --heap runs every program under NPK_HEAP_STATS (gen/snip.py's build) and
adds each leg's `heap:` words (allocated/peak_live/count) to its line: a leak
finding's verdict is that line, not only the exit code.
"""
import argparse, os, shutil, subprocess, sys, tempfile, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_known import build_and_run  # noqa: E402
import snip  # noqa: E402

SUPPORT = ("rows.npk", "tbl.npk")   # imported modules, never roots


def commit_of(comp):
    return subprocess.run(["git", "-C", comp, "rev-parse", "--short=7", "HEAD"],
                          stdout=subprocess.PIPE, check=True).stdout.decode().strip()


def programs(fdir):
    out = []
    for sub in ("", "minimized"):
        d = os.path.join(fdir, sub)
        if os.path.isdir(d):
            out += [os.path.join(d, f) for f in sorted(os.listdir(d))
                    if f.endswith(".npk") and f not in SUPPORT]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--hunt", default=os.path.join(".work", "hunt"))
    ap.add_argument("--base", default=os.path.join(".work", "base"))
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--llvm", default=os.path.join(".work", "llvm"))
    ap.add_argument("--name", default="VERDICTS.txt")
    ap.add_argument("--heap", action="store_true")
    a = ap.parse_args()
    llvm = os.path.abspath(a.llvm)
    comps = [(os.path.abspath(a.hunt), n + 1) for n in range(a.runs)] + [(os.path.abspath(a.base), 1)]
    fdirs = sorted(os.path.join("findings", d) for d in os.listdir("findings")
                   if d.startswith("F-") and (not a.ids or d.split("-")[0] + "-" + d.split("-")[1] in a.ids
                                              or d in a.ids))
    for fdir in fdirs:
        progs = programs(fdir)
        rows, hunt_seen = [], {}
        for comp, run in comps:
            commit = commit_of(comp)
            for p in progs:
                if a.heap:
                    r = snip.build_and_run(p, comp, llvm, heap=True)
                    rc, codes, o0, o2 = r["npkc"], r["codes"], r["O0"], r["O2"]
                    note = "heap O0=%s O2=%s" % (snip.fmt_heap(r["heap_O0"]), snip.fmt_heap(r["heap_O2"]))
                else:
                    scratch = tempfile.mkdtemp(prefix="finding-")
                    try:
                        rc, codes, o0, o2, note = build_and_run(p, comp, llvm, scratch)
                    finally:
                        shutil.rmtree(scratch, ignore_errors=True)
                rel = os.path.relpath(p, fdir)[:-4]
                v = (rc, ",".join(codes) or "-", o0, o2) + ((note,) if a.heap else ())
                rows.append("%-44s %s  run %d  npkc=%s  codes=%s  O0=%s  O2=%s%s"
                            % (rel, commit, run, v[0], v[1], v[2], v[3], ("  " + note) if note else ""))
                if comp == comps[0][0]:
                    hunt_seen.setdefault(rel, set()).add(v)
        unstable = sorted(k for k, s in hunt_seen.items() if len(s) > 1)
        head = ["# %s — verdicts by PLAN.md's recipe (gen/run_findings.py)" % os.path.basename(fdir),
                "# measured %s; HUNT %s run %d times, the baseline %s once"
                % (time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), commit_of(comps[0][0]), a.runs,
                   commit_of(comps[-1][0])),
                "# HUNT runs agree for every program: %s" % ("yes" if not unstable else "NO: " + ", ".join(unstable)),
                ""]
        with open(os.path.join(fdir, a.name), "w") as fh:
            fh.write("\n".join(head + rows) + "\n")
        print("%s: %d programs, %d lines, HUNT runs agree: %s"
              % (fdir, len(progs), len(rows), "yes" if not unstable else "NO " + ", ".join(unstable)))


if __name__ == "__main__":
    main()
