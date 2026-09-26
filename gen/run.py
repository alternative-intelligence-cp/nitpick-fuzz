#!/usr/bin/env python3
"""M2.4 — compile, link and run grid cells at one compiler, on both legs.

usage: python3 gen/run.py <compiler-dir> [--cells cells] [--limit N] [--ids ID ...]
                          [--jobs 4] [--out results/<commit>/cells.jsonl]

Cells run in id order. The output file is appended one JSON line per cell and
the run is RESUMABLE: every cell already in the file is skipped. A compile
step gets 120 s, a run 10 s; a run timeout is recorded as "T".

M9: a cell whose meta.json says "heap": true (the leak observer) runs under
NPK_HEAP_STATS=1, and each leg records the runtime's `heap:` line as
heap_O0/heap_O2 = [allocated, peak_live, count] (null when no line came). A
cell's "section", "expect_exit" and "expect_live" are carried into its record.
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess, sys, tempfile, threading

CODE_RE = re.compile(r"NITPICK-[A-Z]+-\d{3}")
HEAP_RE = re.compile(r"heap: allocated=(\d+) peak_live=(\d+) count=(\d+)")
COMPILE_TIMEOUT, RUN_TIMEOUT = 120, 10


def run(cmd, cwd=None, timeout=COMPILE_TIMEOUT, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        return (128 - rc if rc < 0 else rc), p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        return "T", (e.stdout or b"").decode("utf-8", "replace")


def commit_of(comp):
    return subprocess.run(["git", "-C", comp, "rev-parse", "--short=7", "HEAD"],
                          stdout=subprocess.PIPE, check=True).stdout.decode().strip()


def do_cell(meta, cells, comp, llvm):
    cid = meta["id"]
    src_dir = os.path.abspath(os.path.join(cells, cid))
    npkc = os.path.join(comp, ".internal", "quickemit", "npkc")
    npkrt = os.path.join(comp, ".internal", "quickemit", "npkrt.o")
    work = tempfile.mkdtemp(prefix="cell-")
    try:
        # compile from a private copy of the cell's directory: imports are relative
        d = os.path.join(work, "src")
        shutil.copytree(src_dir, d)
        ll = os.path.join(work, cid + ".ll")
        rc, out = run([npkc, cid + ".npk", "-o", ll], cwd=d)
        codes = sorted(set(CODE_RE.findall(out)))
        rec = {k: meta[k] for k in ("id", "T", "P", "O", "observer", "expect")}
        for k in ("section", "expect_exit", "expect_live"):   # M9's cells carry these
            if k in meta:
                rec[k] = meta[k]
        rec.update({"npkc": rc, "codes": codes, "O0": "-", "O2": "-"})
        first = [l for l in out.splitlines() if "NITPICK-" in l][:1]
        if first:
            rec["msg"] = first[0][:240]
        if rc != 0:
            if rc not in (1,):
                rec["tail"] = out[-400:]
            return rec
        if not os.path.exists(ll):
            rec["note"] = "npkc 0 but no .ll"
            return rec
        env = {"PATH": os.path.join(llvm, "bin") + ":" + os.environ.get("PATH", "")}
        for leg in ("O0", "O2"):
            s = ll
            if leg == "O2":
                s = os.path.join(work, cid + ".opt.ll")
                r, o = run(["opt", "-O2", "-S", ll, "-o", s], env=env)
                if r != 0:
                    rec[leg] = "opt!%s" % r; rec[leg + "_err"] = o[-300:]; continue
            obj, exe = os.path.join(work, cid + "." + leg + ".o"), os.path.join(work, cid + "." + leg)
            r, o = run(["llc", "-" + leg, "-filetype=obj", "-relocation-model=static", s, "-o", obj], env=env)
            if r != 0:
                rec[leg] = "llc!%s" % r; rec[leg + "_err"] = o[-300:]; continue
            r, o = run(["ld.lld", "-static", obj, npkrt, "-o", exe], env=env)
            if r != 0:
                rec[leg] = "ld!%s" % r; rec[leg + "_err"] = o[-300:]; continue
            # M9's leak observer: the runtime's `heap:` line on fd 2 at exit
            heap = bool(meta.get("heap"))
            r, o = run(["env", "-i"] + (["NPK_HEAP_STATS=1"] if heap else []) + [exe],
                       cwd=work, timeout=RUN_TIMEOUT)
            rec[leg] = r
            if heap:
                m = HEAP_RE.findall(o)
                rec["heap_" + leg] = [int(x) for x in m[-1]] if m else None
        return rec
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("compiler")
    ap.add_argument("--cells", default="cells")
    ap.add_argument("--llvm", default=os.path.join(".work", "llvm"))
    ap.add_argument("--limit", type=int, default=None, help="only the first N cells in id order")
    ap.add_argument("--ids", nargs="*", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.jobs > 4:
        sys.exit("at most 4 jobs (CLAUDE.md rule 7)")
    comp, llvm = os.path.abspath(a.compiler), os.path.abspath(a.llvm)
    commit = commit_of(comp)
    out = a.out or os.path.join("results", commit, "cells.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    metas = [json.loads(l) for l in open(os.path.join(a.cells, "INDEX.jsonl"))]
    metas.sort(key=lambda m: m["id"])
    if a.ids:
        want = set(a.ids)
        metas = [m for m in metas if m["id"] in want or m["id"].split("_")[0] in want]
    if a.limit:
        metas = metas[:a.limit]
    done = set()
    if os.path.exists(out):
        for l in open(out):
            if l.strip():
                done.add(json.loads(l)["id"])
    todo = [m for m in metas if m["id"] not in done]
    print("compiler %s: %d cells selected, %d already done, %d to run -> %s"
          % (commit, len(metas), len(metas) - len(todo), len(todo), out), flush=True)
    lock = threading.Lock()
    n = 0
    with open(out, "a") as fh, cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(do_cell, m, a.cells, comp, llvm): m for m in todo}
        for f in cf.as_completed(futs):
            rec = f.result()
            with lock:
                fh.write(json.dumps(rec) + "\n"); fh.flush()
                n += 1
                if n % 25 == 0 or n == len(todo):
                    print("  %d/%d" % (n, len(todo)), flush=True)


if __name__ == "__main__":
    main()
