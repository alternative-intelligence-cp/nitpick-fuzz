#!/usr/bin/env python3
"""M11 -- run every testable claim's program at one compiler and judge it against
the expectation written from the reference text (m11/EXPECT.tsv).

usage: python3 gen/m11_run.py <compiler-dir> [--jobs 4] [--ids ID ...] [--out FILE]
                              [--llvm .work/llvm]

A `.npk` program is compiled, linked and run on both legs by PLAN.md's recipe, from
a private copy of its own file (or of its own directory, for a claim with support
modules): a 120 s compile, a 10 s run under `env -i` with stdin /dev/null, T on a
timeout, 128+N on a signal; under NPK_HEAP_STATS=1 when the claim checks the heap.
A `.sh` claim runs `bash` in a scratch directory with $NPKC, $NPKG, $NPKRT and
$LLVM_BIN set (60 s). One named line per claim:
  <id> @<commit> npkc=<rc> [codes] O0=<rc> O2=<rc> expect=<e> -> AGREE | DISAGREE:<kind>
and one JSON line each in results/<commit>/m11.jsonl (overwritten). Kinds:
  accepted      expected a refusal, npkc 0
  refused       expected a program to compile, npkc 1
  other_code    refused, but not with the expected code
  wrong_exit    compiled, both legs agree, and the exit is not the expected one
  leg_mismatch  compiled, and -O0 differs from -O2
  build_fail    npkc 0, and opt, llc or ld.lld refused the emission
  heap          the exits agree and a leg's `heap:` line does not match
  ir            the emitted IR does not (or does) match the expected pattern
  crash         npkc exited other than 0 or 1
  timeout       a leg or a script hit its timeout
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_RE = re.compile(r"NITPICK-[A-Z]+-\d{3}")
HEAP_RE = re.compile(r"heap: allocated=(\d+) peak_live=(\d+) count=(\d+)")


def sh(cmd, cwd=None, env=None, timeout=120, stdin=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout, stdin=stdin,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        return (128 - rc if rc < 0 else rc), p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        return "T", (e.stdout or b"").decode("utf-8", "replace")


def load_expect():
    rows = []
    with open(os.path.join(ROOT, "m11", "EXPECT.tsv")) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(head, line.rstrip("\n").split("\t"))))
    return rows


def build_and_run(row, comp, llvm):
    npkc = os.path.join(comp, ".internal", "quickemit", "npkc")
    npkrt = os.path.join(comp, ".internal", "quickemit", "npkrt.o")
    npkg = os.path.join(comp, ".internal", "quickemit", "p_main_npk")
    src = os.path.normpath(os.path.join(ROOT, "m11", row["file"]))
    work = tempfile.mkdtemp(prefix="m11-")
    rec = {"npkc": "-", "codes": [], "msg": "", "O0": "-", "O2": "-", "heap_O0": None,
           "heap_O2": None, "ir": None, "sh": None, "out": ""}
    try:
        lbin = os.path.join(llvm, "bin")
        if src.endswith(".sh"):
            env = {"PATH": lbin + ":/usr/bin:/bin", "HOME": work, "NPKC": npkc, "NPKG": npkg,
                   "NPKRT": npkrt, "LLVM_BIN": lbin}
            rc, out = sh(["bash", src], cwd=work, env=env, timeout=60, stdin=subprocess.DEVNULL)
            rec["sh"] = rc
            rec["out"] = out[-600:]
            return rec
        d = os.path.join(work, "src")
        own_dir = os.path.basename(os.path.dirname(src)) == os.path.basename(src)[:-4]
        if own_dir:
            shutil.copytree(os.path.dirname(src), d)
        else:
            os.makedirs(d)
            shutil.copy(src, d)
        base = os.path.basename(src)
        stem = base[:-4]
        ll = os.path.join(work, stem + ".ll")
        rc, out = sh([npkc, base, "-o", ll], cwd=d, stdin=subprocess.DEVNULL)
        rec["npkc"] = rc
        rec["codes"] = sorted(set(CODE_RE.findall(out)))
        first = [l for l in out.splitlines() if "NITPICK-" in l][:1]
        rec["msg"] = first[0][:300] if first else out.strip()[:300]
        if rc != 0 or not os.path.exists(ll):
            return rec
        e = row["expect"]
        if e.startswith("ir"):
            pat = e.split(":", 1)[1]
            with open(ll, encoding="utf-8", errors="replace") as f:
                rec["ir"] = bool(re.search(pat, f.read(), re.M))
        env = {"PATH": lbin + ":" + os.environ.get("PATH", "")}
        heap = row.get("heap", "-") != "-"
        for leg in ("O0", "O2"):
            s = ll
            if leg == "O2":
                s = os.path.join(work, stem + ".opt.ll")
                r, o = sh(["opt", "-O2", "-S", ll, "-o", s], env=env)
                if r != 0:
                    rec[leg] = "opt!%s" % r
                    continue
            obj, exe = os.path.join(work, stem + "." + leg + ".o"), os.path.join(work, stem + "." + leg)
            r, o = sh(["llc", "-" + leg, "-filetype=obj", "-relocation-model=static", s, "-o", obj], env=env)
            if r != 0:
                rec[leg] = "llc!%s" % r
                continue
            r, o = sh(["ld.lld", "-static", obj, npkrt, "-o", exe], env=env)
            if r != 0:
                rec[leg] = "ld!%s" % r
                continue
            cmd = ["env", "-i"] + (["NPK_HEAP_STATS=1"] if heap else []) + [exe]
            r, o = sh(cmd, cwd=d, timeout=10, stdin=subprocess.DEVNULL)
            rec[leg] = r
            m = HEAP_RE.findall(o)
            rec["heap_" + leg] = "/".join(m[-1]) if m else None
        return rec
    finally:
        shutil.rmtree(work, ignore_errors=True)


def heap_ok(pat, got):
    if got is None:
        return False
    for p, g in zip(pat.split("/"), got.split("/")):
        if p != "*" and p != g:
            return False
    return True


def judge(row, r):
    """-> (verdict, kind)."""
    e = row["expect"]
    if e.startswith("sh:"):
        if r["sh"] == "T":
            return "DISAGREE", "timeout"
        return ("AGREE", "") if r["sh"] == int(e[3:]) else ("DISAGREE", "wrong_exit")
    if r["npkc"] not in (0, 1):
        return "DISAGREE", "crash"
    kind, _, val = e.partition(":")
    if kind == "refuse":
        if r["npkc"] == 0:
            return "DISAGREE", "accepted"
        if val:
            code = val if val.startswith("NITPICK-") else "NITPICK-" + val
            if code not in r["codes"]:
                return "DISAGREE", "other_code"
        return "AGREE", ""
    if r["npkc"] == 1:
        return "DISAGREE", "refused"
    built = all(isinstance(r[l], int) or r[l] == "T" for l in ("O0", "O2"))
    if not built:
        return "DISAGREE", "build_fail"
    if kind in ("ir", "ir!"):
        want = kind == "ir"
        return ("AGREE", "") if r["ir"] == want else ("DISAGREE", "ir")
    if kind == "compile":
        return "AGREE", ""
    if "T" in (r["O0"], r["O2"]):
        return "DISAGREE", "timeout"
    if r["O0"] != r["O2"]:
        return "DISAGREE", "leg_mismatch"
    if r["O0"] != int(val):
        return "DISAGREE", "wrong_exit"
    if row.get("heap", "-") != "-":
        if not (heap_ok(row["heap"], r["heap_O0"]) and heap_ok(row["heap"], r["heap_O2"])):
            return "DISAGREE", "heap"
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
    out = a.out or os.path.join(ROOT, "results", commit, "m11.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    def one(row):
        r = build_and_run(row, comp, os.path.abspath(a.llvm))
        v, k = judge(row, r)
        return row, r, v, k

    recs = {}
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for row, r, v, k in ex.map(one, rows):
            shown = ("sh=%s" % r["sh"]) if r["sh"] is not None else "npkc=%s %s O0=%s O2=%s" % (
                r["npkc"], ",".join(r["codes"]) or "-", r["O0"], r["O2"])
            print("%-10s @%s %s expect=%s -> %s" % (row["id"], commit, shown, row["expect"],
                                                     v + (":" + k if k else "")), flush=True)
            recs[row["id"]] = dict(id=row["id"], doc=row["doc"], line=int(row["line"]),
                                   kind_claim=row["kind"], file=row["file"], commit=commit,
                                   expect=row["expect"], heap_expect=row.get("heap", "-"),
                                   verdict=v, kind=k, **r)
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(recs[row["id"]]) + "\n")
    agree = sum(1 for x in recs.values() if x["verdict"] == "AGREE")
    print("%s: %d programs, %d agree, %d disagree -> %s" % (commit, len(recs), agree,
                                                           len(recs) - agree, out))


if __name__ == "__main__":
    main()
