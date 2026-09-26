#!/usr/bin/env python3
"""M8.3 — check that every function in every program leaves explicitly.

usage: python3 gen/check_leaves.py [DIR ...] [--compiler DIR]   (default: cells known findings)

DEF-108's fix (`NITPICK-FLOW-001`, 1.6.0 step 5c) refuses a body that can reach
its own closing brace: every path ends in `pass`, `fail`, `exit` or a trap, and
a `NIL` function passes `NIL`. A program that leans on the old fall-off return
would be refused for the wrong reason at a compiler carrying the fix.

This is a static reading of the source, not the compiler's walk. For every
`func:` declaration it finds the body's closing `};` and asks that the body's
LAST top-level statement is a `pass`, `fail` or `exit`. A body whose last
statement is a nested block (an `if`, a loop, a `pick`) is listed for a look by
hand: the compiler may still accept it (a `pick` whose every arm leaves), but
this check does not decide that.

With --compiler, every root program (every .npk but the support modules
tbl.npk and rows.npk) is also compiled by that compiler's npkc, from a private
copy of its directory, 4 at a time, and the programs whose output carries
NITPICK-FLOW-001 are listed: the compiler's own answer to the same question.
"""
import argparse, concurrent.futures as cf, os, re, shutil, subprocess, sys, tempfile

SUPPORT = ("tbl.npk", "rows.npk")

LEAVE = re.compile(r"^\s*(pass|fail|exit)\b.*;\s*$")


def functions(src):
    """Yield (name, first line no, [body lines]) for each top-level func."""
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^(?:pub\s+)?func:([A-Za-z_][A-Za-z0-9_]*)", lines[i])
        if m and lines[i].rstrip().endswith("{"):
            start, depth, body = i, 0, []
            for j in range(i, len(lines)):
                depth += lines[j].count("{") - lines[j].count("}")
                if j > i:
                    body.append(lines[j])
                if depth == 0:
                    i = j
                    break
            yield m.group(1), start + 1, body[:-1]      # drop the closing `};`
        elif m and re.search(r"\{\s*\}\s*;\s*$", lines[i]):
            yield m.group(1), i + 1, []                 # `{ };` on one line: an empty body
        i += 1


def check(path):
    bad = []
    src = open(path, encoding="utf-8").read()
    for name, ln, body in functions(src):
        stmts = [l for l in body if l.strip() and not l.strip().startswith("//")]
        if not stmts:
            bad.append((path, ln, name, "empty body"))
        elif not LEAVE.match(stmts[-1]):
            bad.append((path, ln, name, "last statement: %s" % stmts[-1].strip()[:60]))
    return bad


def flow001(path, npkc):
    """Compile one root program; return its FLOW-001 lines (empty if none)."""
    work = tempfile.mkdtemp(prefix="leaves-")
    try:
        d = os.path.join(work, "src")
        shutil.copytree(os.path.dirname(os.path.abspath(path)), d)
        p = subprocess.run([npkc, os.path.basename(path), "-o", os.path.join(work, "x.ll")], cwd=d,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        out = p.stdout.decode("utf-8", "replace")
        return p.returncode, [l for l in out.splitlines() if "NITPICK-FLOW-001" in l]
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*")
    ap.add_argument("--compiler", default=None)
    a = ap.parse_args()
    dirs = a.dirs or ["cells", "known", "findings"]
    n_files = n_bad = 0
    roots = []
    for d in dirs:
        for dp, _, fs in os.walk(d):
            for f in sorted(fs):
                if f.endswith(".npk"):
                    n_files += 1
                    if f not in SUPPORT:
                        roots.append(os.path.join(dp, f))
                    for p, ln, name, why in check(os.path.join(dp, f)):
                        n_bad += 1
                        print("%s:%d  func:%s  %s" % (p, ln, name, why))
    print("%d files, %d functions not ending in pass/fail/exit" % (n_files, n_bad))
    if a.compiler:
        npkc = os.path.join(os.path.abspath(a.compiler), ".internal", "quickemit", "npkc")
        hits, rcs = [], {}
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            for path, (rc, lines) in zip(roots, ex.map(lambda r: flow001(r, npkc), roots)):
                rcs[rc] = rcs.get(rc, 0) + 1
                if lines:
                    hits.append(path)
                    print("FLOW-001  %s  %s" % (path, lines[0][:160]))
        print("%d root programs compiled by %s: npkc rc %s; %d carry NITPICK-FLOW-001"
              % (len(roots), npkc, dict(sorted(rcs.items())), len(hits)))


if __name__ == "__main__":
    main()
