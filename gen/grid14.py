#!/usr/bin/env python3
"""M14 — the S-140 class (F-051 R1): a narrow grid around TYPE_REFERENCE §27's `NULL`
bullet at HUNT5 (the M14 brief's §5; PROGRESS.md S92 onward).

usage: python3 gen/grid14.py [--out cells14] [--selfcheck]

Writes cells14/<id>/<id>.npk and cells14/<id>/meta.json, cells14/INDEX.jsonl (id
order) and cells14/SKIPPED.txt (every combination not emitted, with its reason). A
cell's id is its file name and its `mod:` name (PLAN 2.2). `cells14/` is gitignored
and regenerable: the seeds are read from findings/F-051-wild-dead-load-legs-disagree/,
each checked against its recorded sha256. It imports gen/grid13.py and does not edit
it.

The rule under test is §27's last `NULL` bullet at HUNT5, RULE27 below, copied from
HUNT5's file (--selfcheck compares it with that file when the compiler clone is
here). Every cell contains `wild`, which CLAUDE.md's defect definition excludes: the
grid is reported apart, as the check of §27 (D-364).

Every cell carries its EXPECTATION, written here before its first run (PLAN 9.6),
from that rule, with the rule's text and its source in meta.json:
  TRAP 107  npkc compiles it and both legs reach failsafe as MachineFault;
  SAFE      npkc compiles it and both legs exit `expect_exit` (14 or 0): the twins,
            which load nothing.

Sections:
  S  F-051's four programs, byte for byte, and the three dead loads' twins (`<id>_t`:
     the one load line deleted, the `mod:` line renamed); T, P and O "seed": 7 cells;
  U  the permitted pattern, an unused load: O (bind, overwrite) x P x T x after
     (test, none): 40 cells, TRAP 107, each flagged with its twin and `s140_o2`;
  W  the twins: P x T x after, with no load: 20 cells, SAFE with 14 or 0;
  K  the guarantee, a used load whose value decides the exit: O (cmp, arith, callee)
     x P x T: 30 cells, TRAP 107;
  B  the boundary of "uses": the text reads the value, but on the path run the exit
     does not depend on it: O (untaken, ignore, copy, selfsub, selfcmp, deadadd) x P
     local x T: 12 cells, TRAP 107 by the strict reading, with a note in the rule.
The places P: `local` (`wild T->:p = NULL;`), `param` (a helper `runp` taking `wild
T->:q`, called with NULL, passing its code back), `field` (`H:h = H{ p: NULL };`, the
place `h.p`), `module` (`fixed wild T->:P = NULL;`), `returned` (a helper `nptr`
passing NULL). T: `int64`, and the struct S (gen/grid13.py's STRUCT_S), read as `v.a`.

Codes, as in grid13 (gen/grid13.py:36-52): 0 success; 12 and 13 a read-back check;
14 the NULL test took the null branch (the right answer in a twin, and on a flagged
cell's -O2 leg); 99 the failsafe's (*) arm; 91-98 and 106-117 the TRAPS arms, 107
MachineFault. A helper passes its code to `main`, which exits with it (D-013).

The flag. `s140` = "unused_load" is set by the CONSTRUCTION -- on every U cell and on
the three dead-load seeds -- never from an exit. `s140_o2` is the exit the program
gives with its load deleted, which the generator knows (14 after the NULL test, 0
with none); `s140_twin` names the cell that is that program. --selfcheck makes
condition (c) literal: each flagged cell's text, with its load line (and an overwrite
line) deleted and its `mod:` name changed to the twin's, equals the twin's text.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid13 import Prog, X, FAILSAFE13, STRUCT_S, ARM, Skip, WILD_RE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AT = "249eae9"                                    # HUNT5, landing 161: the rule is read here
AT_FULL = "249eae91559bfc1e3b8a17b12286c21108e4215a"
MF = ARM["MachineFault"]                          # 107

# ------------------------------------------------------------------ the rule
# TYPE_REFERENCE.md §27, the `NULL` subsection's last bullet, at HUNT5 (lines 2314-2324),
# its lines joined by one space. --selfcheck re-reads it from HUNT5's file.
RULE27 = (
    "A store through a `NULL` pointer (a `wild` one, since landing 119), or a load from one whose value the "
    "program USES, is a hardware fault that reaches `failsafe` as `MachineFault` (D-307) at BOTH legs: every "
    "emitted function carries LLVM's `null_pointer_is_valid` attribute (DEF-251, 1.6.1e landing 115), so the "
    "optimiser never reads the dereference as undefined and never folds the body that holds it. A load whose "
    "value NOTHING uses is no read at -O2 -- dead-code elimination removes an unused load from valid memory, as "
    "it may of any load, and no attribute keeps one -- and faults at -O0: the legs' one permitted disagreement, "
    "narrow to an unused load through a `wild` `NULL` pointer (D-364, 2026-10-22; DEF-273, the fuzzer's F-051; "
    "the fuzz corpus records F-051's programs as that disagreement). This bullet said \"a store through or a "
    "load from a `NULL` pointer … at BOTH legs\" from landing 115 until landing 142.")
SRC27 = ("TYPE_REFERENCE.md §27, the `NULL` subsection's last bullet (lines 2314-2324), at HUNT5 %s; DECISIONS.md "
         "D-364 (S-140's R1, recorded with landing 142)" % AT)
B_NOTE = ("whether this form USES the value, §27's words do not settle; the expectation is the strict reading, "
          "and a disagreement is reported, not permitted.")
SRC = {
    "seed": SRC27 + "; F-051's program, byte for byte",
    "seed_ctl": SRC27 + "; F-051's control: the value decides the exit, a USED load, TRAP 107 at both legs",
    "twin": SRC27 + "; a twin loads nothing, so its own text decides its exit: the NULL test (a comparison "
                    "against a wild place, §27's first bullet) answers 14, or the program exits 0",
    "U": SRC27 + "; U, the permitted half: an unused load faults at -O0 (TRAP 107), and at -O2 it may be no read, "
                 "the run class PERMITTED:S-140",
    "K": SRC27 + "; K, the guarantee: \"a load from one whose value the program USES\" faults at BOTH legs",
    "B": SRC27 + "; B, the boundary of \"uses\": the strict reading, a value the text reads is USED",
}

# ------------------------------------------------------------------ S: the seeds
F051 = "findings/F-051-wild-dead-load-legs-disagree"
SEEDS = [   # (id, sha256 of the committed file, s140_o2 -- None for the used-load control --, its one load line)
    ("wild_dead_load", "c933454f34bbe63a40552e692d71d3de34178d37bcf69570a1600b644ee7fa6a", 14, "    int64:v = <-p;\n"),
    ("wild_dead_load_exit0", "cb294b84865c3249aa063fc20f7feeeee69539a9011304ed9003b6687bb402a8", 0,
     "    int64:v = <-p;\n"),
    ("wild_dead_struct_load", "fde4acd9cd94a06bad7190bc83e44b8ad0b3fdf0b5c18f39c281c51c1c4ee530", 14,
     "    S:v = <-p;\n"),
    ("ctl_wild_used_load", "4c3f45d4a1cd59305dc5e70e367932f62dfcd5966eee53c69506853c0b76f970", None, None),
]


def read_seed(sid, sha):
    path = os.path.join(ROOT, F051, sid + ".npk")
    with open(path, "rb") as fh:
        data = fh.read()
    if hashlib.sha256(data).hexdigest() != sha:
        raise SystemExit("grid14: seed %s: %s is not the recorded sha256 %s" % (sid, path, sha))
    return data.decode()


def once(text, old, new, what):
    """Replace `old` by `new`, asserting it matched exactly once (rule 5)."""
    n = text.count(old)
    if n != 1:
        raise SystemExit("grid14: %s: %r matched %d times, not once" % (what, old, n))
    return text.replace(old, new, 1)


def seed_twin(sid, src, load):
    return once(once(src, load, "", sid + "'s load line"), "mod:%s;" % sid, "mod:%s_t;" % sid, sid + "'s mod: line")


# ------------------------------------------------------------------ the axes
PLACES = ["local", "param", "field", "module", "returned"]
TYPES = {"int64": dict(ty="int64", val="v", ow="v = 5i64;"),
         "struct": dict(ty="S", val="v.a", ow="v = S{ a: 5i64, b: 2i32 };")}
AFTER = ["test", "none"]
U_O = ["bind", "overwrite"]
K_O = ["cmp", "arith", "callee"]
B_O = ["untaken", "ignore", "copy", "selfsub", "selfcmp", "deadadd"]
RD = "func:rd = int32(int64:x) never fails {\n    if (x == 0i64) { pass 13i32; }\n    pass 12i32;\n};\n"

# A W twin's binding left unused that HUNT5 refuses (§4) is respelled by an explicit
# substitution, applied to the twin and asserted by --selfcheck, or the twin and its U
# cells are skipped with the reason. §4's probes at HUNT5 found every unused binding
# compiles, so both are empty.
RESPELL = {}     # (T, P, after) -> (old, new), applied once to the twin's text
TWIN_SKIP = {}   # (T, P, after) -> reason


def space():
    """Every combination: (section, T, P, O, after); after is None outside U and W."""
    for o in U_O:
        for pk in PLACES:
            for tk in TYPES:
                for after in AFTER:
                    yield ("U", tk, pk, o, after)
    for pk in PLACES:
        for tk in TYPES:
            for after in AFTER:
                yield ("W", tk, pk, "twin", after)
    for o in K_O:
        for pk in PLACES:
            for tk in TYPES:
                yield ("K", tk, pk, o, None)
    for o in B_O:
        for tk in TYPES:
            yield ("B", tk, "local", o, None)


def cell_id(n, sec, tk, pk, o, after):
    return "m%03d_%s_%s_%s_%s%s" % (n, sec.lower(), tk, pk, o, ("_" + after) if after else "")


IDS = {c: cell_id(i + 1, *c) for i, c in enumerate(space())}   # numbered over the whole space: stable under skips


def twin_key(tk, pk, after):
    return ("W", tk, pk, "twin", after)


class Prog14(Prog):
    """grid13's Prog, rendered by grid13; `main`'s parameter is `argv` where the body reads it (§4)."""

    def __init__(self):
        Prog.__init__(self)
        self.argv = "_~argv"

    def render(self, cid):
        src = Prog.render(self, cid)
        if self.argv != "_~argv":
            src = once(src, "func:main = int32(cstring[]:_~argv) {", "func:main = int32(cstring[]:%s) {" % self.argv,
                       cid + "'s main")
        return src


def program(sec, tk, pk, o, after):
    t = TYPES[tk]
    ty, val = t["ty"], t["val"]
    p = Prog14()
    if tk == "struct":
        p.need("structs", STRUCT_S)
    inner = pk == "param"
    E = (lambda n: "pass %di32;" % n) if inner else (lambda n: "exit %di32;" % n)
    pre = []
    if pk == "local":
        place, pre = "p", ["wild %s->:p = NULL;" % ty]
    elif pk == "param":
        place = "q"
    elif pk == "field":
        p.structs.append("struct:H = { wild %s->:p; };\n" % ty)
        place, pre = "h.p", ["H:h = H{ p: NULL };"]
    elif pk == "module":
        p.mods.append("fixed wild %s->:P = NULL;\n" % ty)
        place = "P"
    elif pk == "returned":
        p.helpers.append("func:nptr = wild %s->() never fails { pass NULL; };\n" % ty)
        place, pre = "p", ["wild %s->:p = raw nptr();" % ty]
    lines = list(pre)
    if sec in ("U", "K", "B"):
        lines.append("%s:v = <-%s;" % (ty, place))          # the load: its one line
    if sec == "U" and o == "overwrite":
        lines.append(t["ow"])                               # then `v` is never read
    if sec in ("U", "W"):
        if after == "test":
            lines.append("if (%s == NULL) { %s }" % (place, E(14)))
        lines.append(E(0))
    elif sec == "K":
        if o == "cmp":
            lines += ["if (%s == 0i64) { %s }" % (val, E(13)), E(12)]
        elif o == "arith":
            lines += ["if (%s + 1i64 == 1i64) { %s }" % (val, E(13)), E(12)]
        elif o == "callee":
            p.helpers.append(RD)
            lines += ["int32:r = raw rd(%s);" % val, "pass r;" if inner else "exit r;"]
    elif sec == "B":                                        # P is local: the body is main's
        if o == "untaken":
            p.argv = "argv"
            lines += ["if (argv.len > 100i64) {", "    if (%s == 0i64) { exit 13i32; }" % val, "    exit 12i32;", "}",
                      "exit 0i32;"]
        elif o == "ignore":
            p.helpers.append("func:ign = int32(%s:_~x) never fails { pass 0i32; };\n" % ty)
            lines += ["int32:r = raw ign(v);", "exit r;"]
        elif o == "copy":
            lines += ["%s:w = v;" % ty, "exit 0i32;"]
        elif o == "selfsub":
            lines += ["if (%s - %s != 0i64) { exit 12i32; }" % (val, val), "exit 0i32;"]
        elif o == "selfcmp":
            lines += ["if (%s != %s) { exit 12i32; }" % (val, val), "exit 0i32;"]
        elif o == "deadadd":
            lines += ["int64:w = %s + 1i64;" % val, "exit 0i32;"]
    if inner:
        p.helpers.append("func:runp = int32(wild %s->:q) never fails {\n%s};\n"
                         % (ty, "".join("    %s\n" % l for l in lines)))
        p.body += ["int32:r = raw runp(NULL);", "exit r;"]
    else:
        p.body += lines
    return p


def expectation(sec, after):
    if sec == "W":
        return X("SAFE", [], 14 if after == "test" else 0, RULE27, SRC["twin"])
    if sec == "B":
        return X("TRAP", [], MF, RULE27 + " Note (B): " + B_NOTE, SRC["B"])
    return X("TRAP", [], MF, RULE27, SRC[sec])


# ------------------------------------------------------------------ the build
def build():
    """-> (cells, skipped): cells a list of (id, source, meta), skipped of (section, T, P, O, after, reason)."""
    cells, skipped = [], []
    for sid, sha, o2, load in SEEDS:
        src = read_seed(sid, sha)
        meta = {"id": sid, "section": "S", "T": "seed", "P": "seed", "O": "seed", "observer": "exit",
                "scope": "wild" if WILD_RE.search(src) else "plain",
                "seed_source": "%s/%s.npk" % (F051, sid), "seed_sha256": sha}
        meta.update(X("TRAP", [], MF, RULE27, SRC["seed" if o2 is not None else "seed_ctl"]))
        if o2 is not None:
            meta.update({"s140": "unused_load", "s140_o2": o2, "s140_twin": sid + "_t"})
        cells.append((sid, src, meta))
        if o2 is not None:
            tsrc = seed_twin(sid, src, load)
            tmeta = {"id": sid + "_t", "section": "S", "T": "seed", "P": "seed", "O": "seed", "observer": "exit",
                     "scope": "wild" if WILD_RE.search(tsrc) else "plain", "twin_of": sid,
                     "seed_source": "%s/%s.npk" % (F051, sid), "seed_sha256": sha, "deleted": load.strip()}
            tmeta.update(X("SAFE", [], o2, RULE27, SRC["twin"]))
            cells.append((sid + "_t", tsrc, tmeta))
    for combo in space():
        sec, tk, pk, o, after = combo
        cid = IDS[combo]
        try:
            if sec == "W" and (tk, pk, after) in TWIN_SKIP:
                raise Skip(TWIN_SKIP[(tk, pk, after)])
            if sec == "U" and (tk, pk, after) in TWIN_SKIP:
                raise Skip("its twin %s is skipped: %s" % (IDS[twin_key(tk, pk, after)], TWIN_SKIP[(tk, pk, after)]))
            src = program(sec, tk, pk, o, after).render(cid)
        except Skip as e:
            skipped.append((sec, tk, pk, o, after or "-", str(e)))
            continue
        if sec == "W" and (tk, pk, after) in RESPELL:
            old, new = RESPELL[(tk, pk, after)]
            src = once(src, old, new, cid + "'s respelling")
        meta = {"id": cid, "section": sec, "T": tk, "P": pk, "O": o, "observer": "exit",
                "scope": "wild" if WILD_RE.search(src) else "plain"}
        if after:
            meta["after"] = after
        meta.update(expectation(sec, after))
        if sec == "U":
            meta.update({"s140": "unused_load", "s140_o2": 14 if after == "test" else 0,
                         "s140_twin": IDS[twin_key(tk, pk, after)]})
        if sec == "B":
            meta["boundary"] = o
        cells.append((cid, src, meta))
    return cells, skipped


def write(out, cells, skipped):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for cid, src, meta in cells:
        d = os.path.join(out, cid)
        os.makedirs(d)
        with open(os.path.join(d, cid + ".npk"), "w") as fh:
            fh.write(src)
        with open(os.path.join(d, "meta.json"), "w") as fh:
            json.dump(meta, fh, indent=1)
    with open(os.path.join(out, "INDEX.jsonl"), "w") as fh:
        for _, _, meta in sorted(cells, key=lambda c: c[0]):
            fh.write(json.dumps(meta) + "\n")
    with open(os.path.join(out, "SKIPPED.txt"), "w") as fh:
        fh.write("# section T P O after -- reason (%d combinations not emitted)\n" % len(skipped))
        for s in skipped:
            fh.write("%s %s %s %s %s -- %s\n" % s)


def counts(cells, skipped):
    by, sk = {}, {}
    for _, _, m in cells:
        by[m["section"]] = by.get(m["section"], 0) + 1
    for s in skipped:
        sk[s[0]] = sk.get(s[0], 0) + 1
    return by, sk


# ------------------------------------------------------------------ the self-check
LOAD_RE = re.compile(r"^ *(?:int64|S):v = <-(?:p|q|h\.p|P);\n", re.M)
OW_RE = re.compile(r"^ *v = (?:5i64|S\{ a: 5i64, b: 2i32 \});\n", re.M)


def delete_once(text, rx, what, cid, errs):
    ms = list(rx.finditer(text))
    if len(ms) != 1:
        errs.append("%s: its %s line matches %d times, not once" % (cid, what, len(ms)))
        return None
    return text[:ms[0].start()] + text[ms[0].end():]


def rule_at_hunt5():
    """§27's last NULL bullet from HUNT5's file, joined; None when the compiler clone is not here."""
    clone = os.path.join(ROOT, ".work", "nitpick")
    if not os.path.isdir(clone):
        return None
    p = subprocess.run(["git", "-C", clone, "show", AT_FULL + ":meta/specs/TYPE_REFERENCE.md"],
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if p.returncode != 0:
        return None
    lines = p.stdout.decode().split("\n")
    starts = [i for i, l in enumerate(lines) if l.startswith("- A store through a `NULL` pointer")]
    if len(starts) != 1:
        return "(%d bullets begin so at HUNT5)" % len(starts)
    i = starts[0]
    out, j = [lines[i][2:]], i + 1
    while j < len(lines) and lines[j].startswith("  ") and lines[j].strip():
        out.append(lines[j].strip())
        j += 1
    return " ".join(out)


def selfcheck(out):
    errs, notes = [], []
    cells, skipped = build()
    if build() != (cells, skipped):
        errs.append("two builds differ: the generator is not deterministic")
    ids = [c[0] for c in cells]
    if len(set(ids)) != len(ids):
        errs.append("duplicate ids")
    by_id = {cid: (src, m) for cid, src, m in cells}
    # the rule: copied from HUNT5's file
    h5 = rule_at_hunt5()
    if h5 is None:
        notes.append("the rule was not compared with HUNT5's file: no compiler clone with %s here" % AT)
    elif h5 != RULE27:
        errs.append("RULE27 differs from §27's last NULL bullet at HUNT5 %s" % AT)
    else:
        notes.append("RULE27 equals §27's bullet at HUNT5 %s" % AT)
    need = ("id", "T", "P", "O", "observer", "expect", "section", "expect_codes", "expect_exit", "rule", "source",
            "scope")
    for cid, src, m in cells:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", cid):
            errs.append("%s: id is no module name" % cid)
        if re.findall(r"^mod:(\w+);", src, re.M) != [cid] or m["id"] != cid:
            errs.append("%s: id, mod: name and meta disagree" % cid)
        for k in need:
            if k not in m:
                errs.append("%s: meta lacks %s" % (cid, k))
        if m.get("observer") != "exit":
            errs.append("%s: observer is not exit" % cid)
        if m.get("scope") != "wild" or not WILD_RE.search(src):
            errs.append("%s: not scope wild, or no `wild` in the program" % cid)
        sec, e = m["section"], m["expect"]
        if sec == "B":
            if m["rule"] != RULE27 + " Note (B): " + B_NOTE:
                errs.append("%s: a B cell's rule is not §27 with the note" % cid)
            if m.get("boundary") != m["O"]:
                errs.append("%s: a B cell without its boundary form" % cid)
        elif m["rule"] != RULE27:
            errs.append("%s: the rule is not §27's bullet verbatim" % cid)
        if sec != "B" and "boundary" in m:
            errs.append("%s: boundary outside B" % cid)
        if not m.get("source"):
            errs.append("%s: no source" % cid)
        if m["expect_codes"]:
            errs.append("%s: expect_codes in a grid with no REFUSE cell" % cid)
        if e == "TRAP" and m["expect_exit"] != MF:
            errs.append("%s: TRAP exit is not MachineFault's arm" % cid)
        if e == "SAFE" and m["expect_exit"] not in (0, 14):
            errs.append("%s: SAFE without its exit, 14 or 0" % cid)
        if e not in ("TRAP", "SAFE"):
            errs.append("%s: expect %s" % (cid, e))
        twin_cell = sec == "W" or (sec == "S" and "twin_of" in m)
        if twin_cell != (e == "SAFE"):
            errs.append("%s: SAFE is the twins' alone" % cid)
        if ("after" in m) != (sec in ("U", "W")):
            errs.append("%s: after outside U and W, or missing there" % cid)
        # the flag: only U cells and the three dead-load seeds
        flagged = m.get("s140") is not None
        should = sec == "U" or (sec == "S" and m["id"] in [s[0] for s in SEEDS if s[2] is not None])
        if flagged != should or (flagged and m["s140"] != "unused_load"):
            errs.append("%s: s140 is %r; only U cells and the three dead-load seeds carry it" % (cid, m.get("s140")))
        if not flagged and ("s140_o2" in m or "s140_twin" in m):
            errs.append("%s: s140_o2 or s140_twin without the flag" % cid)
        if flagged:
            tw = m.get("s140_twin")
            if tw not in by_id:
                errs.append("%s: s140_twin %r names no emitted cell" % (cid, tw))
                continue
            tsrc, tm = by_id[tw]
            if tm["expect"] != "SAFE" or tm.get("s140") is not None:
                errs.append("%s: its twin %s is not an unflagged SAFE cell" % (cid, tw))
            if m.get("s140_o2") not in (0, 14) or m["s140_o2"] != tm["expect_exit"]:
                errs.append("%s: s140_o2 %r is not its twin's expected exit %r" % (cid, m.get("s140_o2"),
                                                                                   tm["expect_exit"]))
            if m["T"] != "seed" and (tm["T"], tm["P"], tm.get("after")) != (m["T"], m["P"], m.get("after")):
                errs.append("%s: its twin %s has another P, T or after" % (cid, tw))
            # condition (c), literally: delete the load (and the overwrite), rename, compare
            t = delete_once(src, LOAD_RE, "load", cid, errs)
            if t is not None and m["O"] == "overwrite":
                t = delete_once(t, OW_RE, "overwrite", cid, errs)
            if t is not None:
                if t.count("mod:%s;" % cid) != 1:
                    errs.append("%s: its mod: line does not match once" % cid)
                    continue
                t = t.replace("mod:%s;" % cid, "mod:%s;" % tw, 1)
                key = (m["T"], m["P"], m.get("after"))
                if key in RESPELL:
                    old, new = RESPELL[key]
                    if t.count(old) != 1:
                        errs.append("%s: the respelling %r -> %r does not match once" % (cid, old, new))
                        continue
                    t = t.replace(old, new, 1)
                if t != tsrc:
                    errs.append("%s: with its load deleted it is not its twin %s's text (condition (c))" % (cid, tw))
        if sec == "S":
            continue
        # layout: helpers before main, failsafe directly after main, grid13's failsafe
        tops = [(mt.start(), mt.group(1)) for mt in re.finditer(r"^(?:async )?func:(\w+)", src, re.M)]
        names = [t_[1] for t_ in tops]
        if names.count("main") != 1 or names[-1] != "failsafe" or names[-2] != "main":
            errs.append("%s: helpers are not all before main, or failsafe is not directly after it" % cid)
        if not src.endswith(FAILSAFE13):
            errs.append("%s: the failsafe is not grid13's" % cid)
        for (s0, name), nxt in zip(tops, tops[1:] + [(len(src), "")]):
            if name not in ("main", "failsafe") and re.search(r"\bexit\b", src[s0:nxt[0]]):
                errs.append("%s: `exit` in %s (D-013)" % (cid, name))
    # every s140_twin names an emitted cell (above); every twin of a skipped twin's U cell is skipped too
    for sk in skipped:
        if sk[0] == "W":
            for o in U_O:
                if IDS[("U", sk[1], sk[2], o, sk[4])] in by_id:
                    errs.append("a U cell of skipped twin %s is emitted" % IDS[twin_key(sk[1], sk[2], sk[4])])
    # denominators: every combination is a cell or a skip
    space_n = sum(1 for _ in space())
    if space_n != len(cells) - 7 + len(skipped):
        errs.append("denominators: %d combinations, %d cells, %d skipped" % (space_n, len(cells) - 7, len(skipped)))
    by, sk = counts(cells, skipped)
    for sec, n in (("S", 7), ("U", 40), ("W", 20), ("K", 30), ("B", 12)):
        if by.get(sec, 0) + sk.get(sec, 0) != n:
            errs.append("section %s: %d cells + %d skipped, not %d" % (sec, by.get(sec, 0), sk.get(sec, 0), n))
    # the written grid, if there is one, is this build byte for byte
    if os.path.isdir(out):
        for cid, src, m in cells:
            f = os.path.join(out, cid, cid + ".npk")
            if not os.path.exists(f) or open(f).read() != src:
                errs.append("%s/%s differs from this build" % (out, cid))
            mf = os.path.join(out, cid, "meta.json")
            if not os.path.exists(mf) or json.load(open(mf)) != m:
                errs.append("%s/%s/meta.json differs from this build" % (out, cid))
        on_disk = sorted(d for d in os.listdir(out) if os.path.isdir(os.path.join(out, d)))
        if on_disk != sorted(ids):
            errs.append("%s holds other cells than this build" % out)
        idx = [json.loads(l) for l in open(os.path.join(out, "INDEX.jsonl"))]
        if idx != [m for _, _, m in sorted(cells, key=lambda c: c[0])]:
            errs.append("%s/INDEX.jsonl differs from this build" % out)
    else:
        notes.append("no %s/ to compare" % out)
    nflag = sum(1 for _, _, m in cells if m.get("s140"))
    for e in errs[:40]:
        print("FAIL " + e)
    for n in notes:
        print("note: " + n)
    print("selfcheck: %d cells (%s), %d skipped, %d combinations; condition (c): %d flagged cells, each its twin "
          "with the load deleted (%d respellings); %s"
          % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())), len(skipped), space_n + 7, nflag,
             len(RESPELL), "every check passes" if not errs else "%d FAILURES" % len(errs)))
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cells14")
    ap.add_argument("--selfcheck", action="store_true",
                    help="check ids, the rule, expectations, the flag, condition (c), layout, denominators and the "
                         "written grid")
    a = ap.parse_args()
    if a.selfcheck:
        sys.exit(selfcheck(a.out))
    cells, skipped = build()
    write(a.out, cells, skipped)
    by, sk = counts(cells, skipped)
    print("generated %d cells (%s), skipped %d (%s)" % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                       len(skipped), ", ".join("%s %d" % kv for kv in sorted(sk.items()))
                                                       or "none"))


if __name__ == "__main__":
    main()
