#!/usr/bin/env python3
"""M1.1 — run the recall suite (known/) at one compiler, by PLAN.md's recipe.

usage: python3 gen/run_known.py <compiler-dir> [--llvm DIR] [--out FILE]

<compiler-dir> is a compiler worktree holding .internal/quickemit/{npkc,npkrt.o}.
For every known/*/*.npk except rows.npk (a support module) it prints one line:
    dir/file  npkc=<rc> [codes]  O0=<rc>  O2=<rc>
where [codes] are the distinct NITPICK-...-NNN codes in npkc's output, and a
run leg's value is '-' when the program was not built, 'T' on the 10-second
run timeout. Compilation happens in the program's own directory (imports are
relative); build products go to a scratch directory and never beside known/.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

CODE_RE = re.compile(r"NITPICK-[A-Z]+-\d{3}")
RUN_TIMEOUT = 10
COMPILE_TIMEOUT = 120


def run(cmd, cwd=None, timeout=COMPILE_TIMEOUT, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc < 0:                      # died by signal N: report 128+N
            rc = 128 - rc
        return rc, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace")
        return "T", out


def build_and_run(npk, comp, llvm, scratch):
    """Apply the recipe to one program. Returns (npkc_rc, codes, o0, o2, note)."""
    npkc = os.path.join(comp, ".internal", "quickemit", "npkc")
    npkrt = os.path.join(comp, ".internal", "quickemit", "npkrt.o")
    d = os.path.dirname(os.path.abspath(npk))
    stem = os.path.splitext(os.path.basename(npk))[0]
    ll = os.path.join(scratch, stem + ".ll")
    rc, out = run([npkc, os.path.basename(npk), "-o", ll], cwd=d)
    codes = sorted(set(CODE_RE.findall(out)))
    if rc != 0:
        return rc, codes, "-", "-", ("ll-written" if os.path.exists(ll) else "")
    if not os.path.exists(ll):
        return rc, codes, "-", "-", "no-ll"
    env = {"PATH": os.path.join(llvm, "bin") + ":" + os.environ.get("PATH", "")}
    legs = {}
    for leg in ("O0", "O2"):
        src = ll
        if leg == "O2":
            src = os.path.join(scratch, stem + ".opt.ll")
            r, o = run(["opt", "-O2", "-S", ll, "-o", src], env=env)
            if r != 0:
                legs[leg] = "opt!%s" % r
                continue
        obj = os.path.join(scratch, stem + "." + leg + ".o")
        exe = os.path.join(scratch, stem + "." + leg)
        r, o = run(["llc", "-" + leg, "-filetype=obj", "-relocation-model=static",
                    src, "-o", obj], env=env)
        if r != 0:
            legs[leg] = "llc!%s" % r
            continue
        r, o = run(["ld.lld", "-static", obj, npkrt, "-o", exe], env=env)
        if r != 0:
            legs[leg] = "ld!%s" % r
            continue
        r, o = run(["env", "-i", exe], cwd=scratch, timeout=RUN_TIMEOUT)
        legs[leg] = r
    return rc, codes, legs["O0"], legs["O2"], ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("compiler")
    ap.add_argument("--llvm", default=os.path.join(".work", "llvm"))
    ap.add_argument("--known", default="known")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    comp = os.path.abspath(a.compiler)
    llvm = os.path.abspath(a.llvm)
    files = []
    for dn in sorted(os.listdir(a.known)):
        dp = os.path.join(a.known, dn)
        if not os.path.isdir(dp):
            continue
        for fn in sorted(os.listdir(dp)):
            if fn.endswith(".npk") and fn != "rows.npk":
                files.append(os.path.join(dp, fn))
    scratch = tempfile.mkdtemp(prefix="known-")
    lines = []
    try:
        for f in files:
            rc, codes, o0, o2, note = build_and_run(f, comp, llvm, scratch)
            rel = os.path.relpath(f, a.known)[:-4]
            line = "%-46s npkc=%s [%s]  O0=%s  O2=%s%s" % (
                rel, rc, ",".join(codes), o0, o2, ("  " + note) if note else "")
            print(line, flush=True)
            lines.append(line)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
