#!/usr/bin/env python3
"""M11 -- the reference, checked against the compiler: claims, programs, coverage.

usage: python3 gen/m11.py                      check everything, then write m11/
       python3 gen/m11.py --check [--doc DOC] [--lines A-B]
                                               check quotes and coverage only

Loads every module in gen/m11_claims/ (the DSL is gen/m11lib.py), then:
  - every claim's quote must occur on its line of the reference at HUNT2
    (.work/hunt2), and every id must be unique and well formed;
  - every fenced code block's opening line must carry a claim of kind
    `example`, and every table body row a claim of kind `row`, unless its
    table is `excluded` with a reason (the mechanical half of "every code
    example and every row"; prose claims are extracted by reading);
  - a testable claim has an expectation of a known form and a program (or an
    M10 item, or a script); an untestable one a tagged reason.
Writes m11/CLAIMS.md, m11/EXPECT.tsv and m11/programs/ (regenerated whole).
"""
import argparse, importlib.util, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m11lib as L  # noqa: E402

ROOT = L.ROOT
OUT = os.path.join(ROOT, "m11")
CLAIMS_DIR = os.path.join(ROOT, "gen", "m11_claims")


def load_modules(only=None):
    for f in sorted(os.listdir(CLAIMS_DIR)):
        # a leading `_` keeps a draft out of the whole set, unless it is named by --module
        if not f.endswith(".py") or (f.startswith("_") and f[:-3] != only):
            continue
        if only and f[:-3] != only:
            continue
        L._MODULE[0] = f[:-3]
        spec = importlib.util.spec_from_file_location("m11c_" + f[:-3], os.path.join(CLAIMS_DIR, f))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    L._MODULE[0] = None


def m10_expect():
    out = {}
    with open(os.path.join(ROOT, "m10", "EXPECT.tsv")) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            r = dict(zip(head, line.rstrip("\n").split("\t")))
            out[r["id"]] = r["expect_hunt2"]
    return out


def in_range(n, rng):
    return rng is None or rng[0] <= n <= rng[1]


def check(docs, rng):
    errs = []
    lines = {d: L.doc_lines(d) for d in L.DOCS}
    m10 = m10_expect()
    ids = {}
    for c in L.CLAIMS:
        if c["doc"] in L.DOCS and (c["doc"] not in docs or not in_range(c["line"], rng)):
            ids[c["id"]] = c["module"]
            continue
        where = "%s:%s (%s)" % (c["id"], c["line"], c["module"])
        if not L.ID_RE.match(c["id"]):
            errs.append("%s: malformed id" % where)
        if c["id"] in ids:
            errs.append("%s: duplicate id (also in %s)" % (where, ids[c["id"]]))
        ids[c["id"]] = c["module"]
        if c["doc"] not in L.DOCS:
            errs.append("%s: unknown doc %r" % (where, c["doc"]))
            continue
        pre = L.DOCS[c["doc"]][0]
        if not c["id"].startswith(pre) or c["id"][2:6] != "%04d" % c["line"]:
            errs.append("%s: the id must be %s%04d[letter]" % (where, pre, c["line"]))
        dl = lines[c["doc"]]
        if not (1 <= c["line"] <= len(dl)) or c["quote"] not in dl[c["line"] - 1]:
            errs.append("%s: quote %r not on %s line %d" % (where, c["quote"][:60], c["doc"], c["line"]))
        if c["kind"] not in ("example", "row", "rule"):
            errs.append("%s: kind %r" % (where, c["kind"]))
        if c["untestable"]:
            tag = re.match(r"^\[(\w+)\]", c["untestable"])
            if not tag or tag.group(1) not in L.UNTESTABLE_TAGS:
                errs.append("%s: untestable needs a [tag] from %s" % (where, L.UNTESTABLE_TAGS))
            if c["expect"] or c["src"] or c["sh"] or c["m10"]:
                errs.append("%s: untestable with a test" % where)
            continue
        if c["m10"]:
            if c["m10"] not in m10:
                errs.append("%s: no M10 item %s" % (where, c["m10"]))
            if c["src"] or c["sh"]:
                errs.append("%s: m10 and a program" % where)
            c["expect"] = c["expect"] or m10.get(c["m10"])
            continue
        e = c["expect"]
        if not e or not L.EXPECT_RE.match(e):
            errs.append("%s: expectation %r" % (where, e))
        elif e.startswith("trap:") and e[5:] not in L.TRAP_CODE:
            errs.append("%s: no failsafe arm for %s" % (where, e))
        if e and e.startswith("sh:"):
            if not c["sh"]:
                errs.append("%s: sh expectation without a script" % where)
        elif not c["src"]:
            errs.append("%s: no program" % where)
        elif c["src"] and "func:main" not in c["src"] and not c["files"]:
            errs.append("%s: the program has no main" % where)
        for fn, text in c["files"].items():
            if not re.search(r"^mod:%s;" % re.escape(fn[:-4]), text, re.M):
                errs.append("%s: support file %s must open with mod:%s;" % (where, fn, fn[:-4]))
    # coverage
    for d in docs:
        fences, tables = L.scan(d)
        ex = {c["line"] for c in L.CLAIMS if c["doc"] == d and c["kind"] == "example"}
        rows = {c["line"] for c in L.CLAIMS if c["doc"] == d and c["kind"] == "row"}
        exc = {e["line"] for e in L.EXCLUDED if e["doc"] == d}
        heads = {h for h, _ in tables}
        for e in L.EXCLUDED:
            if e["doc"] == d and e["line"] not in heads:
                errs.append("%s line %d: excluded, but no table header there" % (d, e["line"]))
        for f in fences:
            if in_range(f, rng) and f not in ex:
                errs.append("%s line %d: code block with no `example` claim" % (d, f))
        for h, body in tables:
            if h in exc:
                continue
            for r in body:
                if in_range(r, rng) and r not in rows:
                    errs.append("%s line %d: table row (table at %d) with no `row` claim" % (d, r, h))
    return errs


def md(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def render_program(c):
    head = ["// M11 %s -- %s:%d (%s)" % (c["id"], L.DOCS[c["doc"]][1], c["line"], c["kind"]),
            "// quote: " + c["quote"].strip(),
            "// claim: " + c["text"],
            "// expect: " + c["expect"] + (("   heap " + c["heap"]) if c["heap"] else ""),
            "// wrong: " + (c["wrong"] or "-")]
    src = c["src"]
    body = "\n".join(head) + "\n"
    if not re.search(r"^mod:%s;" % c["id"], src, re.M):
        body += "mod:%s;\n\n" % c["id"]
    h = L.helpers_text(src)
    if h:
        body += h + "\n\n"
    body += src.rstrip() + "\n"
    if c["fs"] and "func:failsafe" not in src:
        body += "\n" + L.failsafe_text(src)
    return body


def write(docs, out=OUT):
    """Write CLAIMS.md, EXPECT.tsv and programs/ under `out` (m11/, or a scratch
    directory for a shakedown). EXPECT.tsv's `file` is relative to the repository
    root when `out` is m11/, and absolute otherwise."""
    pdir = os.path.join(out, "programs")
    if os.path.isdir(pdir):
        shutil.rmtree(pdir)
    os.makedirs(pdir)
    rows = ["id\tdoc\tline\tkind\tfile\texpect\theap"]
    for c in L.CLAIMS:
        if c["untestable"]:
            continue
        if c["m10"]:
            fn = os.path.join(ROOT, "m10", "programs", "%s.npk" % c["m10"])
        elif c["expect"].startswith("sh:"):
            fn = os.path.join(pdir, "%s.sh" % c["id"])
            with open(fn, "w") as f:
                f.write("#!/bin/bash\n# M11 %s -- %s:%d\n# claim: %s\n# expect: %s\n%s\n" % (
                    c["id"], L.DOCS[c["doc"]][1], c["line"], c["text"], c["expect"], c["sh"].rstrip()))
        else:
            if c["files"]:
                d = os.path.join(pdir, c["id"])
                os.makedirs(d)
                fn = os.path.join(d, "%s.npk" % c["id"])
                for sf, text in c["files"].items():
                    with open(os.path.join(d, sf), "w") as f:
                        f.write(text.rstrip() + "\n")
            else:
                fn = os.path.join(pdir, "%s.npk" % c["id"])
            with open(fn, "w") as f:
                f.write(render_program(c))
        if out == OUT:
            fn = os.path.relpath(fn, ROOT)
        rows.append("\t".join([c["id"], c["doc"], str(c["line"]), c["kind"], fn,
                               L.normalize_expect(c["expect"]), c["heap"] or "-"]))
    with open(os.path.join(out, "EXPECT.tsv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    # the claims list
    tot = len(L.CLAIMS)
    unt = [c for c in L.CLAIMS if c["untestable"]]
    Lh = ["# M11 claims: the references, checked against the compiler",
          "",
          "Written by `gen/m11.py` from `gen/m11_claims/` (regenerate with `python3 gen/m11.py`).",
          "Each claim is read from one line of one reference at HUNT2 `9126350`",
          "(the compiler's `meta/specs/`), quotes that line, and carries the outcome the TEXT",
          "says, written before any program ran (PLAN.md 11.2). Kinds: `example` (a fenced",
          "code block, at its opening line), `row` (a table body row), `rule` (a normative",
          "sentence). Expected: `run:N` (npkc 0, both legs exit N; 0 is the reference's",
          "answer), `refuse[:CODE]` (npkc 1), `compile` (npkc 0 and both legs build),",
          "`ir:RE`/`ir!:RE` (the emitted IR does/does not match), `sh:N` (a script's exit).",
          "A trap exits its `failsafe` arm's code: %s." % ", ".join(
              "%s %d" % t for t in L.TRAPS),
          "",
          "**%d claims: %d testable, %d untestable** (each with its reason)." % (
              tot, tot - len(unt), len(unt)),
          ""]
    Lh.append("| reference | claims | examples | rows | rules | testable | untestable |")
    Lh.append("|---|---|---|---|---|---|---|")
    for d in docs:
        cs = [c for c in L.CLAIMS if c["doc"] == d]
        if not cs:
            continue
        Lh.append("| %s | %d | %d | %d | %d | %d | %d |" % (
            d, len(cs), sum(c["kind"] == "example" for c in cs), sum(c["kind"] == "row" for c in cs),
            sum(c["kind"] == "rule" for c in cs), sum(not c["untestable"] for c in cs),
            sum(bool(c["untestable"]) for c in cs)))
    Lh.append("")
    for d in docs:
        cs = sorted([c for c in L.CLAIMS if c["doc"] == d], key=lambda c: (c["line"], c["id"]))
        if not cs:
            continue
        Lh += ["## %s (`%s`)" % (d, L.DOCS[d][1]), "",
               "| id | line | kind | quote | claim | expected |", "|---|---|---|---|---|---|"]
        for c in cs:
            if c["untestable"]:
                exp = "untestable " + md(c["untestable"])
            else:
                exp = "`%s`" % c["expect"] + (" heap `%s`" % c["heap"] if c["heap"] else "") + \
                      (" (M10 `%s`)" % c["m10"] if c["m10"] else "")
            Lh.append("| `%s` | %d | %s | “%s” | %s | %s |" % (
                c["id"], c["line"], c["kind"], md(c["quote"].strip()), md(c["text"]), exp))
        ex = [e for e in L.EXCLUDED if e["doc"] == d]
        if ex:
            Lh += ["", "Tables whose rows are not claims:", ""]
            for e in sorted(ex, key=lambda e: e["line"]):
                Lh.append("- line %d: %s" % (e["line"], e["reason"]))
        Lh.append("")
    with open(os.path.join(out, "CLAIMS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(Lh))
    print("claims %d: testable %d, untestable %d; excluded tables %d; m11/ written" % (
        tot, tot - len(unt), len(unt), len(L.EXCLUDED)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--doc", default=None)
    ap.add_argument("--lines", default=None)
    ap.add_argument("--module", default=None)
    ap.add_argument("--out", default=None, help="write here instead of m11/ (a shakedown)")
    a = ap.parse_args()
    load_modules(a.module)
    docs = [a.doc] if a.doc else list(L.DOCS)
    rng = tuple(int(x) for x in a.lines.split("-")) if a.lines else None
    errs = check(docs, rng)
    for e in errs:
        print("ERROR " + e)
    n = len([c for c in L.CLAIMS if not a.doc or c["doc"] == a.doc])
    print("%d claims checked, %d errors" % (n, len(errs)))
    if errs:
        sys.exit(1)
    if not a.check:
        if (a.module or a.doc or a.lines) and not a.out:
            sys.exit("m11/ is written only from the whole set: use --out DIR for a part")
        out = os.path.abspath(a.out) if a.out else OUT
        os.makedirs(out, exist_ok=True)
        write(list(L.DOCS), out)


if __name__ == "__main__":
    main()
