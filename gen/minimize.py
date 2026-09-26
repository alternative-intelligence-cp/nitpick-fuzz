#!/usr/bin/env python3
"""M5.2 (b) — minimise a program by deleting statements one at a time.

usage: python3 gen/minimize.py <compiler-dir> <file.npk> --want NPKC,O0,O2
                               [--out FILE] [--llvm DIR]

The program is built and run by PLAN.md's recipe (gen/run_known.py's
build_and_run), from a private copy of its directory: imports are relative,
and the file keeps its name, which must equal its `mod:` name. A deletion is
kept only when the verdict -- npkc's rc, the -O0 exit, the -O2 exit -- is
still exactly --want. The units tried are single lines and brace-balanced
blocks (a whole function, a whole `for` or `if` block); passes repeat until
one deletes nothing. The result is printed with the number of builds tried.

A bare `pass …;` or `exit …;` line is never deleted on its own: a function
with a declared result and no `pass` compiles and returns a zero value (probed
at both compilers, 2026-09-26), and a reproducer must not lean on that.
"""
import argparse, os, re, shutil, sys, tempfile

PROTECTED = re.compile(r"^\s*(pass|exit)\b")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_known import build_and_run  # noqa: E402


def depth_change(line):
    """Net '{' minus '}' outside string literals and // comments."""
    d, in_str, i = 0, False, 0
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                i += 1
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif line.startswith("//", i):
            break
        elif ch == "{":
            d += 1
        elif ch == "}":
            d -= 1
        i += 1
    return d


def units(lines):
    """Spans [i, j] (inclusive) that can be deleted as a whole: a line whose
    braces balance, or a line that opens a block, through the line closing it.
    Larger spans first within the order of their first line."""
    out = []
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        d = depth_change(l)
        if d == 0:
            if not PROTECTED.match(l):
                out.append((i, i))
        elif d > 0:
            acc = d
            for k in range(i + 1, len(lines)):
                acc += depth_change(lines[k])
                if acc <= 0:
                    out.append((i, k))
                    break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("compiler")
    ap.add_argument("npk")
    ap.add_argument("--want", required=True, help="npkc,O0,O2 e.g. 0,70,70")
    ap.add_argument("--out", default=None)
    ap.add_argument("--llvm", default=os.path.join(".work", "llvm"))
    a = ap.parse_args()
    want = tuple(x.strip() for x in a.want.split(","))
    comp, llvm = os.path.abspath(a.compiler), os.path.abspath(a.llvm)
    src_dir = os.path.dirname(os.path.abspath(a.npk))
    name = os.path.basename(a.npk)
    work = tempfile.mkdtemp(prefix="min-")
    tries = [0]

    def verdict(lines):
        tries[0] += 1
        d = os.path.join(work, "src")
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(src_dir, d)
        with open(os.path.join(d, name), "w") as fh:
            fh.write("\n".join(lines) + "\n")
        scratch = os.path.join(work, "build")
        shutil.rmtree(scratch, ignore_errors=True)
        os.makedirs(scratch)
        rc, codes, o0, o2, _ = build_and_run(os.path.join(d, name), comp, llvm, scratch)
        return (str(rc), str(o0), str(o2))

    try:
        lines = [l.rstrip("\n") for l in open(a.npk)]
        v = verdict(lines)
        if v != want:
            sys.exit("the program's own verdict is %s, not --want %s" % (",".join(v), ",".join(want)))
        changed = True
        while changed:
            changed = False
            i = 0
            spans = units(lines)
            while i < len(spans):
                s, e = spans[i]
                cand = lines[:s] + lines[e + 1:]
                if verdict(cand) == want:
                    lines = cand
                    changed = True
                    spans = units(lines)
                    # the span that was at i+1 now starts at or after s: resume there
                    i = next((n for n, (s2, _) in enumerate(spans) if s2 >= s), len(spans))
                else:
                    i += 1
        lines = [l for l in lines if l.strip()]
        if verdict(lines) != want:
            sys.exit("dropping blank lines changed the verdict")
        text = "\n".join(lines) + "\n"
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text)
        print(text, end="")
        print("-- %d lines, verdict %s, %d builds tried" % (len(lines), ",".join(want), tries[0]),
              file=sys.stderr)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
