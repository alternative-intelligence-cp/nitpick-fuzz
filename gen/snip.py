#!/usr/bin/env python3
"""M9 — compile, link and run one or more .npk files by PLAN.md's recipe, at
one or both compilers, on both legs; optionally under NPK_HEAP_STATS.

usage: python3 gen/snip.py FILE.npk [FILE.npk ...] [--at hunt2 base] [--heap]
                           [--show-msg] [--llvm .work/llvm]

One line per file per compiler:
  <file> @<commit> npkc=<rc> [codes] O0=<rc> O2=<rc> [heap O0=a/p/c O2=a/p/c]
where a/p/c are the runtime's `heap: allocated= peak_live= count=` words (the
line the runtime prints on fd 2 at exit when the environment carries
NPK_HEAP_STATS), `-` when the leg printed no such line. Each file is compiled
from a private copy of its own directory (imports are relative). A run gets
10 s; a timeout prints T. At most one job: this is a probe, not a grid run.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

CODE_RE = re.compile(r"NITPICK-[A-Z]+-\d{3}")
HEAP_RE = re.compile(r"heap: allocated=(\d+) peak_live=(\d+) count=(\d+)")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(cmd, cwd=None, env=None, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        return (128 - rc if rc < 0 else rc), p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        return "T", (e.stdout or b"").decode("utf-8", "replace")


def heap_of(out):
    m = HEAP_RE.findall(out)
    return tuple(int(x) for x in m[-1]) if m else None


def build_and_run(src, comp, llvm, heap=False):
    """-> dict(npkc, codes, msg, O0, O2, heap_O0, heap_O2, out_O0, out_O2)."""
    npkc = os.path.join(comp, ".internal", "quickemit", "npkc")
    npkrt = os.path.join(comp, ".internal", "quickemit", "npkrt.o")
    work = tempfile.mkdtemp(prefix="snip-")
    try:
        d = os.path.join(work, "src")
        shutil.copytree(os.path.dirname(os.path.abspath(src)), d,
                        ignore=shutil.ignore_patterns("*.ll", "*.o", "*.opt"))
        base = os.path.basename(src)
        stem = base[:-4]
        ll = os.path.join(work, stem + ".ll")
        rc, out = sh([npkc, base, "-o", ll], cwd=d)
        rec = {"npkc": rc, "codes": sorted(set(CODE_RE.findall(out))), "O0": "-", "O2": "-",
               "heap_O0": None, "heap_O2": None, "out_O0": "", "out_O2": ""}
        first = [l for l in out.splitlines() if "NITPICK-" in l][:1]
        rec["msg"] = first[0][:300] if first else ""
        if rc != 0 or not os.path.exists(ll):
            return rec
        env = {"PATH": os.path.join(llvm, "bin") + ":" + os.environ.get("PATH", "")}
        for leg in ("O0", "O2"):
            s = ll
            if leg == "O2":
                s = os.path.join(work, stem + ".opt.ll")
                r, o = sh(["opt", "-O2", "-S", ll, "-o", s], env=env)
                if r != 0:
                    rec[leg] = "opt!%s" % r; continue
            obj, exe = os.path.join(work, stem + "." + leg + ".o"), os.path.join(work, stem + "." + leg)
            r, o = sh(["llc", "-" + leg, "-filetype=obj", "-relocation-model=static", s, "-o", obj], env=env)
            if r != 0:
                rec[leg] = "llc!%s" % r; continue
            r, o = sh(["ld.lld", "-static", obj, npkrt, "-o", exe], env=env)
            if r != 0:
                rec[leg] = "ld!%s" % r; continue
            cmd = ["env", "-i"] + (["NPK_HEAP_STATS=1"] if heap else []) + [exe]
            r, o = sh(cmd, cwd=work, timeout=10)
            rec[leg] = r
            rec["out_" + leg] = o
            rec["heap_" + leg] = heap_of(o)
        return rec
    finally:
        shutil.rmtree(work, ignore_errors=True)


def fmt_heap(h):
    return "-" if h is None else "%d/%d/%d" % h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--at", nargs="+", default=["hunt2", "base"])
    ap.add_argument("--heap", action="store_true")
    ap.add_argument("--show-msg", action="store_true")
    ap.add_argument("--llvm", default=os.path.join(ROOT, ".work", "llvm"))
    a = ap.parse_args()
    for f in a.files:
        for at in a.at:
            comp = os.path.join(ROOT, ".work", at)
            commit = subprocess.run(["git", "-C", comp, "rev-parse", "--short=7", "HEAD"],
                                    stdout=subprocess.PIPE).stdout.decode().strip()
            r = build_and_run(f, comp, os.path.abspath(a.llvm), heap=a.heap)
            line = "%s @%s npkc=%s %s O0=%s O2=%s" % (os.path.basename(f), commit, r["npkc"],
                                                   ",".join(r["codes"]) or "-", r["O0"], r["O2"])
            if a.heap:
                line += " heap O0=%s O2=%s" % (fmt_heap(r["heap_O0"]), fmt_heap(r["heap_O2"]))
            print(line, flush=True)
            if a.show_msg and r["msg"]:
                print("    " + r["msg"], flush=True)


if __name__ == "__main__":
    main()
