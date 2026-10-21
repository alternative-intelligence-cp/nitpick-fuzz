#!/usr/bin/env python3
"""M13 — the initialisation and pointer-store grid, with the -O2 leg as the observer
(the M13 brief's §5; PROGRESS.md S76 onward).

usage: python3 gen/grid13.py [--out cells13] [--selfcheck]

Writes cells13/<id>/<id>.npk and cells13/<id>/meta.json, cells13/INDEX.jsonl (id
order) and cells13/SKIPPED.txt (every combination not emitted, with its reason).
A cell's id is its file name and its `mod:` name (PLAN 2.2). `cells13/` is
gitignored and regenerable: the three seeds are embedded below byte for byte,
with the sha256 of their sources.

Every cell carries its EXPECTATION, written here before its first run (PLAN 9.6),
from the rule that governs it, with the rule's text and its source in meta.json.
A settled D- ruling wins over reference text that has not caught up. A code the
rule does not name is the one §4's probes found, and the source says so.
  REFUSE  npkc refuses, naming every code in `expect_codes`;
  SAFE    npkc compiles it and both legs exit 0;
  TRAP    npkc compiles it and both legs exit `expect_exit`, the failsafe arm of
          the identity the rule says traps.
A cell whose program contains `wild` or `wildx` carries "scope": "wild" (CLAUDE.md's
defect definition excludes such programs; they are the check of DEF-251 (i)).

Sections:
  S  the three seeds, copied byte for byte: bare_binding (DEF-250), null_store
     (DEF-251), probe08h_view_reseated (DEF-252); T, P and O "seed", observer "exit";
  A  module bindings (DEF-250's class): type and qualifier x declaration x operation;
  B  NULL and pointer stores (DEF-251's class): place x operation x type;
  C  uninitialised locals and partial initialisation (D-010): type x place x
     operation, each REFUSE cell with its definitely-assigned SAFE twin (O "<o>_da");
  D  constants at the type's edge: type x operation x operand form (`const`, folded;
     `rt`, through gen/m10.py's identity functions), with the SAFE twins;
  E  stores through a pointer into a pointee (DEF-252's class): holder store x
     lifetime x observer (ra, rs).

Codes (the program's exit is the observation; `exit` is legal only in `main` and
`failsafe`, D-013, so a helper passes its code to `main`):
  0        success: the reference's answer
  12       the value read back is not the one written
  13       a zero read where a non-zero value was written, or where nothing was
  14       a NULL test after a dereference took the null branch
  21-25    E's view: 21 the original, 22 the new value, 23 vacant, 24 another
           live value, 25 the reuse sentinel (freed and reused), as grid9
  70       the free poison read as an observation
  170      the free poison byte itself as the exit (the DEF-252 seed only)
  91-98, 106-117   gen/m10.py's TRAPS arms
  100-105, 118-122 the prelude's eleven other identities, with S44's codes (M11's
           failsafe, gen/m11lib.py's TRAPS); grid13 has no user error
  99       the failsafe's (*) arm: only a garbage argument reaches it, which is
           DEF-251's -O2 face (`main` emptied, control running into `failsafe`).
           So every template declares its helpers before `main` and `failsafe`
           directly after `main`, the layout of the null_store seed.
"""
import argparse, hashlib, json, os, re, shutil, sys

AT = "c72639f"   # HUNT4: the compiler whose references the rule texts are read at

# ------------------------------------------------------------------ the failsafe
# gen/m10.py's TRAPS (lines 40-45) and the eleven other prelude identities with
# S44's codes: together gen/m11lib.py's TRAPS, every identity HUNT4's prelude
# declares (the same 31 at HUNT2, HUNT3 and HUNT4; §4). --selfcheck compares both.
TRAPS = [("HeapBadRequest", 91), ("HeapOom", 92), ("IntOverflow", 93), ("OutOfBounds", 94),
         ("Unreachable", 95), ("WildLeak", 96), ("DivByZero", 97), ("DivOverflow", 98),
         ("StackExhausted", 106), ("MachineFault", 107), ("LimitViolated", 108),
         ("DecreasesViolated", 109), ("TbbErr", 110), ("ShiftRange", 111), ("CastRange", 112),
         ("BadStep", 113), ("BorrowOverlap", 114), ("RequiresViolated", 115),
         ("EnsuresViolated", 116), ("InvariantViolated", 117)]
OTHER = [("StaleHandle", 100), ("DeadlineExceeded", 101), ("ChannelClosed", 102), ("DriverLeak", 103),
         ("IoEof", 104), ("WouldBlock", 105), ("Interrupted", 118), ("NotFound", 119),
         ("Exists", 120), ("CrossDevice", 121), ("BadPath", 122)]


def _failsafe():
    arms = sorted(TRAPS + OTHER, key=lambda a: a[1])
    body = "".join("        (%s) { exit %di32; },\n" % a for a in arms)
    return ("func:failsafe = int32(Error:e) {\n    pick (e) {\n%s        (*) { exit 99i32; }\n    }\n"
            "    exit 9i32;\n};\n" % body)


FAILSAFE13 = _failsafe()
ARM = dict(TRAPS + OTHER)

# identity functions (gen/m10.py's form): a value through one is no constant to the folder
IDF_TY = {"v8": "int8", "vu8": "uint8", "v32": "int32", "v64": "int64", "vu64": "uint64", "vb": "bool"}


def idf(name):
    t = IDF_TY[name]
    return "func:%s = %s(%s:x) never fails { pass x; };\n" % (name, t, t)


STRUCT_S = "struct:S = { int64:a; int32:b; };\n"


class Skip(Exception):
    pass


class Prog:
    """A program: structs, module bindings, helpers (all before `main`), `main`, then the failsafe."""

    def __init__(self):
        self.structs, self.mods, self.helpers, self.body = [], [], [], []
        self.async_main = False

    def need(self, part, text):
        lst = getattr(self, part)
        if text not in lst:
            lst.append(text)

    def render(self, cid):
        head = "async func:main" if self.async_main else "func:main"
        main = "%s = int32(cstring[]:_~argv) {\n%s};\n" % (head, "".join("    %s\n" % l for l in self.body))
        return ("mod:%s;\n\n" % cid + "".join(self.structs) + "".join(self.mods) + "".join(self.helpers)
                + main + FAILSAFE13)


def X(exp, codes=(), exit_=None, rule="", source=""):
    return {"expect": exp, "expect_codes": list(codes), "expect_exit": exit_, "rule": rule, "source": source}


def chk(expr, want, zero, E="exit"):
    """expr must read `want`: 13 when it reads zero, else 12."""
    return ["if (%s != %s) {" % (expr, want), "    if (%s == %s) { %s 13i32; }" % (expr, zero, E),
            "    %s 12i32;" % E, "}"]


# ------------------------------------------------------------------ the rules
R_D211 = ("every module binding that is neither `const` nor `fixed` is refused: \"module state is `fixed` "
          "(D-211)\", NITPICK-TYPE-055, asked since landing 114 of a binding with no initialiser too (DEF-250)",
          "DECISIONS.md D-211 and its landing-114 note, at HUNT4 %s; NOTICES row 114" % AT)
R_FIXED_READ = ("a `fixed` module binding holds the constant it is declared with (D-165, D-211)",
                "TYPE_REFERENCE.md §26 at HUNT4 %s" % AT)
R_ASSIGN002 = ("a `fixed` binding is written once, where it is declared; a later write is NITPICK-ASSIGN-002",
               "TYPE_REFERENCE.md §26 at HUNT4 %s (\"every one of these is NITPICK-ASSIGN-002\")" % AT)
R_TYPE086 = ("no part of a `fixed` binding is written after its declaration: NITPICK-TYPE-086 (D-287)",
             "DECISIONS.md D-287 at HUNT4 %s" % AT)
R_TYPE071 = ("a `fixed` binding has no address: `@` of one is NITPICK-TYPE-071 (D-287)",
             "DECISIONS.md D-287 at HUNT4 %s" % AT)
R_D355 = ("`NULL` written where a plain pointer or an Optional is expected is NITPICK-TYPE-096 at the literal: "
          "a plain `T->` always points at something (D-355 (ii), S-136 option (c), landing 119)",
          "DECISIONS.md D-355 and its landing note, TYPE_REFERENCE.md §27, at HUNT4 %s" % AT)
R_D355_I = ("a store through or a load from a `wild` NULL pointer reaches failsafe as MachineFault (D-307) at "
            "BOTH legs: every emitted function carries `null_pointer_is_valid` (DEF-251 (i), landing 115)",
            "TYPE_REFERENCE.md §27 at HUNT4 %s; NOTICES row 115" % AT)
R_WILD_SAFE = ("a `wild` pointer compared with NULL before any dereference never dereferences it: the guarded "
               "store and the comparison run to their answer (D-355 keeps NULL in a wild context)",
               "TYPE_REFERENCE.md §27 at HUNT4 %s" % AT)
R_OPT_REFUSE = ("an Optional pointer `T->?` is no pointer: it is read through `??`, `??!` or `?.` and tested with "
                "`== NIL`, so a dereference, a field access or a plain-pointer argument without them is refused "
                "(D-355; code NITPICK-TYPE-007 by §4's probes p_b18, p_b18b, p_b29, q_b01, q_b09)",
                "TYPE_REFERENCE.md §11.1 and §27, DECISIONS.md D-355, at HUNT4 %s" % AT)
R_OPT_SAFE = ("a `T->?` tested against NIL, or read through `?? @d`, never dereferences an absent pointer",
              "TYPE_REFERENCE.md §11.1 at HUNT4 %s (D-355)" % AT)
R_D360 = ("`p ??! Ident` is the pointer, or a trap with the named identity: an empty `T->?` traps Unreachable "
          "(D-360, landing 120)", "DECISIONS.md D-360 at HUNT4 %s" % AT)
R_D010 = ("no implicit default value: definite-assignment analysis refuses any path that reads a binding before "
          "writing it (D-010); NITPICK-ASSIGN-001 (TYPE_REFERENCE §27 names it; §4's probes c01-c22)",
          "DECISIONS.md D-010 and TYPE_REFERENCE.md §27 at HUNT4 %s" % AT)
R_D010_LIT = ("a struct literal gives every field a value; there is no default (D-010's definite assignment "
              "for aggregates): NITPICK-TYPE-027", "DECISIONS.md D-010's aggregate note at HUNT4 %s; §4's probe p_c05" % AT)
R_DA_SAFE = ("a binding definitely assigned on every path is read as its value (D-010)",
             "DECISIONS.md D-010 at HUNT4 %s" % AT)
R_SHIFT_K = ("a known shift amount outside 0 <= n < width is NITPICK-TYPE-070 at the shift (D-277)",
             "OP_REFERENCE.md (D-277) at HUNT4 %s; m10/CHECKLIST.md s07" % AT)
R_SHIFT_RT = ("a computed shift amount outside 0 <= n < width traps ShiftRange (D-277)",
              "OP_REFERENCE.md (D-277) at HUNT4 %s; m10/CHECKLIST.md s04-s06, s08" % AT)
R_DIV_K = ("a constant division or remainder by zero, and a constant MIN / -1 or MIN % -1, is NITPICK-TYPE-004 "
           "wherever the folder decides the pair (D-331)", "OP_REFERENCE.md:164-167 at HUNT4 %s" % AT)
R_DIV0_RT = ("integer `/` and `%` by zero trap DivByZero (D-007)",
             "TYPE_REFERENCE.md at HUNT4 %s; m10/CHECKLIST.md v03, v04" % AT)
R_MINDIV_RT = ("a signed minimum divided by -1 traps DivOverflow, MIN % -1 too",
               "TYPE_REFERENCE.md and OP_REFERENCE.md at HUNT4 %s; m10/CHECKLIST.md v05-v08" % AT)
R_NEG_K = ("a constant negation whose exact value does not fit is NITPICK-TYPE-076 (D-310)",
           "OP_REFERENCE.md at HUNT4 %s" % AT)
R_NEG_RT = ("unary `-` is `0 - x` and traps IntOverflow on the most negative value (D-210)",
            "TYPE_REFERENCE.md at HUNT4 %s; m10/CHECKLIST.md o04" % AT)
R_D_SAFE = ("an operation inside its type's range is computed exactly; a constant one is the machine's answer "
            "(D-310, D-311)", "OP_REFERENCE.md at HUNT4 %s" % AT)
R_D004 = ("a view stored into a holder declared outside the block that declares its storage is "
          "NITPICK-BORROW-002, directly (D-004 rule 3, DEF-42) and through a callee (DEF-252, landing 116)",
          "DECISIONS.md D-004 rule 3 at HUNT4 %s; NOTICES row 116" % AT)
R_E_SAFE = ("a view whose storage outlives its holder is read as the bytes it views",
            "DECISIONS.md D-004 at HUNT4 %s" % AT)

# ------------------------------------------------------------------ S: the seeds
SEED_DIR_LIBS = "/home/randy/Workspace/REPOS/nitpick-libs/.internal/defects/2026-10-12-null-store-legs"
SEED_DIR_TEAM = "/home/randy/Team/REPORTS/defects/2026-10-15-parse-probes"
SEEDS = [
    ("bare_binding", "DEF-250", SEED_DIR_LIBS + "/bare_binding.npk",
     "59401b8dafe3f2321e6a1f2123d82b8a6ae25903b56172d82ec54396d43e3daa",
     X("REFUSE", ["NITPICK-TYPE-055"], None, *R_D211)),
    ("null_store", "DEF-251", SEED_DIR_LIBS + "/null_store.npk",
     "024f53a6a22d523e1ac03bac39bb9972e9845959d4341c23e1a5d74df4e99d55",
     X("REFUSE", ["NITPICK-TYPE-096"], None, *R_D355)),
    ("probe08h_view_reseated", "DEF-252", SEED_DIR_TEAM + "/probe08h_view_reseated.npk",
     "2bef7468dca52ec12c6c3bc21465fcbe8eb76bddc0af0fe4d21165fa4416d6e7",
     X("REFUSE", ["NITPICK-BORROW-002"], None, *R_D004)),
]
# SEED_TEXT: begin (generated from the sources above; their sha256 is checked)
SEED_TEXT = {
    'bare_binding':
        'mod:bare_binding;\n'
        '\n'
        'int64:counter;\n'
        '\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    counter = 5i64;\n'
        '    if (counter != 5i64) { exit 11i32; }\n'
        '    exit 0i32;\n'
        '};\n'
        '\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'null_store':
        'mod:null_store;\n'
        '\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    int64->:p = NULL;\n'
        '    <-p = 5i64;\n'
        '    exit 0i32;\n'
        '};\n'
        '\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'probe08h_view_reseated':
        '// npkc: 0\n'
        '// run: 170 at -O0 and through opt -O2 -- the free poison, 0xAA\n'
        '//\n'
        "// PROBE 08h -- PROBE 08g's RESEAT, DONE BY A CALLEE. A COMPILER DEFECT AT `7e91730`.\n"
        '//\n'
        '// ASKS: `reset(@c, string_bytes(t))` where `reset` writes `<-c = Cursor{ src: src, ... }`, `c`\n'
        '// declared outside the block and `t` inside it. The direct assignment is refused\n'
        '// `NITPICK-BORROW-002` (`refused/probe08g_holder_outlives_view.npk`). Is the call?\n'
        '//\n'
        '// THE ANSWER AT `7e91730`, measured at planning: ACCEPTED (`npkc` exit 0), and after the block\n'
        "// `c.src[0]` reads the runtime's free poison, 0xAA -- exit 170 at -O0 and through `opt -O2`. A\n"
        "// use-after-free in safe code. The callee's store is read by the compiler's D-325 summary, which\n"
        "// asks whether the view outlives the FRAME; DEF-42's block rule is asked of a direct assignment\n"
        "// only. See this directory's `README.md`.\n"
        'mod:probe08h_view_reseated;\n'
        '\n'
        'struct:Cursor = { fixed uint8[]:src; int64:pos; };\n'
        '\n'
        'func:reset = NIL(Cursor->:c, fixed uint8[]:src) never fails {\n'
        '    <-c = Cursor{ src: src, pos: 0i64 };\n'
        '    pass NIL;\n'
        '};\n'
        '\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    string:s = string_concat("abc", "def");\n'
        '    Cursor:c = Cursor{ src: string_bytes(s), pos: 0i64 };\n'
        '    if (c.pos == 0i64) {\n'
        '        string:t = string_concat("ghij", "klmn");\n'
        '        drop reset(@c, string_bytes(t));\n'
        '    }\n'
        '    if (c.src.len != 8i64) { exit 10i32; }\n'
        '    if (c.src[0i64] != 103u8) { exit (c.src[0i64] => int32); }\n'
        '    exit 0i32;\n'
        '};\n'
        '\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (OutOfBounds)       { exit 94i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
}
# SEED_TEXT: end

# ------------------------------------------------------------------ A: module bindings
A_T = {
    "int64": dict(q="", ty="int64", c="5i64", w="7i64", z="0i64", two="2i64", c2="7i64",
                  ops=("read", "write", "compound", "addr_w", "addr_r")),
    "int32": dict(q="", ty="int32", c="5i32", w="7i32", z="0i32", two="2i32", c2="7i32",
                  ops=("read", "write", "compound", "addr_w", "addr_r")),
    "uint8": dict(q="", ty="uint8", c="5u8", w="7u8", z="0u8", two="2u8", c2="7u8",
                  ops=("read", "write", "compound", "addr_w", "addr_r")),
    "bool": dict(q="", ty="bool", c="true", w="true", z="false", ops=("read", "write", "addr_w", "addr_r")),
    "struct": dict(q="", ty="S", c="S{ a: 5i64, b: 2i32 }", w="S{ a: 7i64, b: 3i32 }", part=".a",
                   ops=("read", "write", "field", "addr_w", "addr_r")),
    "arr": dict(q="", ty="int64[4]", c="[5i64, 6i64, 7i64, 8i64]", w="[7i64, 7i64, 7i64, 7i64]", part="[0i64]",
                ops=("read", "write", "elem", "addr_w", "addr_r")),
    "atomic": dict(q="", ty="atomic<int64>", c="5i64", ops=("read", "store_load", "addr_w", "addr_r")),
    "chan": dict(q="", ty="Channel<int64, 1i32, 4i64>", ops=("send_recv",)),
    "stack": dict(q="stack ", ty="int64", c="5i64", w="7i64", z="0i64", two="2i64", c2="7i64",
                  ops=("read", "write", "compound", "addr_w", "addr_r")),
    "wild": dict(q="wild ", ty="int64->", c="NULL", ops=("read", "write")),
    "wildx": dict(q="wildx ", ty="int64->", c="NULL", ops=("read", "write")),
}
A_DECL = ["noinit", "init", "const", "fixed", "pub"]
A_OPS = ["read", "write", "compound", "field", "elem", "store_load", "send_recv", "addr_w", "addr_r"]
A_OP_WHY = {
    "write": "a whole-binding write: an atomic is written through its methods and a channel through send",
    "compound": "a compound assignment needs an arithmetic type",
    "field": "a field write needs the struct",
    "elem": "an element write needs the array",
    "store_load": "store/load is the atomic's",
    "send_recv": "send/recv is the channel's",
    "addr_w": "the address of a pointer binding is a pointer to a pointer, and a channel has no write through one",
    "addr_r": "the address of a pointer binding is a pointer to a pointer, and a channel has no read through one",
    "read": "a channel is read by recv (send_recv)",
}


def a_cell(tk, decl, o):
    t = A_T[tk]
    if decl == "const":
        raise Skip("`const` is no declaration form: retired at 1.4.2c and an ordinary identifier (TYPE_REFERENCE "
                   "§26 at HUNT4); §4's probe p_a03_const_int64 is PARSE-001 at 3:7 at HUNT3 and HUNT4")
    if o not in t["ops"]:
        raise Skip("%s does not apply to %s: %s" % (o, tk, A_OP_WHY[o]))
    if tk == "chan" and decl in ("init", "fixed"):
        raise Skip("a channel has no constant initialiser: `channel()` is a call (TYPE-035, §4's probes p_a19, q_a10)")
    if tk == "atomic" and decl == "fixed":
        raise Skip("no constant of type atomic<int64> exists for a module initialiser (TYPE-007 \"expected "
                   "atomic<int64>, found int64\", §4's probe p_a17)")
    p = Prog()
    q, ty = t["q"], t["ty"]
    if tk == "struct":
        p.need("structs", STRUCT_S)
    has = decl in ("init", "fixed")
    p.mods.append({"noinit": "%s%s:g;\n" % (q, ty), "init": "%s%s:g = %s;\n" % (q, ty, t.get("c")),
                   "fixed": "fixed %s%s:g = %s;\n" % (q, ty, t.get("c")), "pub": "pub %s%s:g;\n" % (q, ty)}[decl])
    b = p.body
    part = t.get("part", "")
    if tk in ("struct", "arr"):
        rd, cv, wv, z = "g" + part, "5i64", "7i64", "0i64"
    elif tk == "atomic":
        rd, cv, wv, z = "v", "5i64", "7i64", "0i64"
    elif tk in ("wild", "wildx"):
        rd = cv = wv = z = None
    elif tk != "chan":
        rd, cv, wv, z = "g", t["c"], t["w"], t["z"]
    if o == "read":
        if tk == "atomic":
            b.append("int64:v = g.load();")
        if tk in ("wild", "wildx"):
            b.append("if (g != NULL) { exit 12i32; }" if has else "if (g == NULL) { exit 13i32; }")
        else:
            b += chk(rd, cv, z) if has else ["if (%s == %s) { exit 13i32; }" % (rd, z)]
    elif o == "write":
        if tk in ("wild", "wildx"):
            b += ["g = alloc(8i64) =>! %sint64->;" % q, "if (g == NULL) { exit 13i32; }", "dalloc(g);"]
        else:
            b.append("g = %s;" % t["w"])
            b += chk(rd, wv, z)
    elif o == "compound":
        b.append("g += %s;" % t["two"])
        b += chk("g", t["c2"] if has else t["two"], z)
    elif o == "field":
        b += ["g.a = 7i64;"] + chk("g.a", "7i64", "0i64")
    elif o == "elem":
        b += ["g[0i64] = 7i64;"] + chk("g[0i64]", "7i64", "0i64")
    elif o == "store_load":
        b += ["g.store(7i64);", "int64:v = g.load();"] + chk("v", "7i64", "0i64")
    elif o == "send_recv":
        p.async_main = True
        b += ["await g.send(7i64, raw duration_ms(100i64)) ?! ChannelClosed;",
              "int64:v = await g.recv(raw duration_ms(100i64)) ?! ChannelClosed;"] + chk("v", "7i64", "0i64")
    elif o == "addr_w":
        if tk == "struct":
            p.helpers.append("func:wrp = NIL(S->:p) never fails { p.a = 7i64; pass NIL; };\n")
        elif tk == "arr":
            p.helpers.append("func:wrp = NIL(int64[4]->:p) never fails { (<-p)[0i64] = 7i64; pass NIL; };\n")
        elif tk == "atomic":
            p.helpers.append("func:wrp = NIL(atomic<int64>->:p) never fails { p.store(7i64); pass NIL; };\n")
        else:
            p.helpers.append("func:wrp = NIL(%s->:p) never fails { <-p = %s; pass NIL; };\n" % (ty, t["w"]))
        b.append("drop wrp(@g);")
        if tk == "atomic":
            b.append("int64:v = g.load();")
        b += chk(rd, wv, z)
    elif o == "addr_r":
        if tk == "struct":
            p.helpers.append("func:rdp = int64(S->:p) never fails { pass p.a; };\n")
        elif tk == "arr":
            p.helpers.append("func:rdp = int64(int64[4]->:p) never fails { pass (<-p)[0i64]; };\n")
        elif tk == "atomic":
            p.helpers.append("func:rdp = int64(atomic<int64>->:p) never fails { pass p.load(); };\n")
        else:
            p.helpers.append("func:rdp = %s(%s->:p) never fails { pass (<-p); };\n" % (ty, ty))
        rty = ty if tk not in ("struct", "arr", "atomic") else "int64"
        b.append("%s:v = raw rdp(@g);" % rty)
        b += chk("v", cv, z) if has else ["if (v == %s) { exit 13i32; }" % z]
    b.append("exit 0i32;")
    if decl != "fixed":
        exp = X("REFUSE", ["NITPICK-TYPE-055"], None, *R_D211)
    elif o == "read":
        exp = X("SAFE", [], None, *R_FIXED_READ)
    elif o in ("write", "compound"):
        exp = X("REFUSE", ["NITPICK-ASSIGN-002"], None, *R_ASSIGN002)
    elif o in ("field", "elem"):
        exp = X("REFUSE", ["NITPICK-TYPE-086"], None, *R_TYPE086)
    else:
        exp = X("REFUSE", ["NITPICK-TYPE-071"], None, *R_TYPE071)
    return p, exp


# ------------------------------------------------------------------ B: NULL and pointer stores
B_T = {"int64": dict(ty="int64", v="5i64", dummy="int64:d = 1i64;"),
       "struct": dict(ty="S", v="S{ a: 5i64, b: 2i32 }", dummy="S:d = S{ a: 1i64, b: 1i32 };")}
B_P = ["local", "fixed_local", "module_fixed", "field", "param", "returned", "wild_local", "opt"]
B_O = ["store", "load_used", "load_unused_test", "field_read", "pass_deref", "guarded_store", "compare",
       "unwrap_trap"]
B_DEREF = ("store", "load_used", "load_unused_test", "field_read", "pass_deref")


def b_cell(tk, pk, o):
    t = B_T[tk]
    ty, v = t["ty"], t["v"]
    if o == "field_read" and tk == "int64":
        raise Skip("an int64 pointee has no field")
    if o == "unwrap_trap" and pk != "opt":
        raise Skip("`??!` takes an Optional (D-360, landing 120): only the `T->?` place has one")
    p = Prog()
    if tk == "struct":
        p.need("structs", STRUCT_S)
    in_param = pk == "param"
    E = (lambda n: "pass %si32;" % n) if in_param else (lambda n: "exit %si32;" % n)
    pe = "h.p" if pk == "field" else "p"
    null = "NIL" if pk == "opt" else "NULL"
    pre = []
    if pk == "local":
        pre = ["%s->:p = NULL;" % ty]
    elif pk == "fixed_local":
        pre = ["fixed %s->:p = NULL;" % ty]
    elif pk == "module_fixed":
        p.mods.append("fixed %s->:p = NULL;\n" % ty)
    elif pk == "field":
        p.structs.append("struct:H = { %s->:p; };\n" % ty)
        pre = ["H:h = H{ p: NULL };"]
    elif pk == "returned":
        p.helpers.append("func:nptr = %s->() never fails { pass NULL; };\n" % ty)
        pre = ["%s->:p = raw nptr();" % ty]
    elif pk == "wild_local":
        pre = ["wild %s->:p = NULL;" % ty]
    elif pk == "opt":
        pre = ([t["dummy"]] if o == "guarded_store" else []) + ["%s->?:p = NIL;" % ty]
    lines = []
    if o == "store":
        lines = ["<-%s = %s;" % (pe, v), E(0)]
    elif o == "load_used":
        if tk == "int64":
            lines = ["int64:v = <-%s;" % pe, "if (v == 0i64) { %s }" % E(13), E(12)]
        else:
            lines = ["S:v = <-%s;" % pe, "if (v.a == 0i64) { %s }" % E(13), E(12)]
    elif o == "load_unused_test":
        lines = ["%s:v = <-%s;" % (ty, pe), "if (%s == %s) { %s }" % (pe, null, E(14)), E(0)]
    elif o == "field_read":
        lines = ["int64:v = %s.a;" % pe, "if (v == 0i64) { %s }" % E(13), E(12)]
    elif o == "pass_deref":
        # dispatch note (d): the wild local's dereferencing callee takes `wild T->`, as dalloc's
        # parameter is `wild any->`, so the cell stays inside wild context
        p.helpers.append("func:stp = NIL(%s%s->:q) never fails { <-q = %s; pass NIL; };\n"
                         % ("wild " if pk == "wild_local" else "", ty, v))
        lines = ["drop stp(%s);" % pe, E(0)]
    elif o == "guarded_store":
        if pk == "opt":
            lines = ["if (p != NIL) {", "    %s->:q = p ?? @d;" % ty, "    <-q = %s;" % v, "}", E(0)]
        else:
            lines = ["if (%s != NULL) { <-%s = %s; }" % (pe, pe, v), E(0)]
    elif o == "compare":
        lines = ["if (%s != %s) { %s }" % (pe, null, E(12)), E(0)]
    elif o == "unwrap_trap":
        lines = ["%s->:q = p ??! Unreachable;" % ty, "<-q = %s;" % v, E(0)]
    if in_param:
        p.helpers.append("func:runp = int32(%s->:p) never fails {\n%s};\n" % (ty, "".join("    %s\n" % l for l in lines)))
        p.body += ["int32:r = raw runp(NULL);", "exit r;"]
    else:
        p.body += pre + lines
    if pk == "wild_local":
        exp = X("TRAP", [], ARM["MachineFault"], *R_D355_I) if o in B_DEREF else X("SAFE", [], None, *R_WILD_SAFE)
    elif pk == "opt":
        if o in B_DEREF:
            exp = X("REFUSE", ["NITPICK-TYPE-007"], None, *R_OPT_REFUSE)
        elif o == "unwrap_trap":
            exp = X("TRAP", [], ARM["Unreachable"], *R_D360)
        else:
            exp = X("SAFE", [], None, *R_OPT_SAFE)
    else:
        exp = X("REFUSE", ["NITPICK-TYPE-096"], None, *R_D355)
    return p, exp


# ------------------------------------------------------------------ C: definite assignment
C_T = {
    "int64": dict(ty="int64", v="5i64", v0="4i64", one="1i64", rd="%s", k="i64"),
    "int32": dict(ty="int32", v="5i32", v0="4i32", one="1i32", rd="%s", k="i32"),
    "bool": dict(ty="bool", v="true", rd="%s", k="b"),
    "struct": dict(ty="S", v="S{ a: 5i64, b: 2i32 }", rd="%s.a", k="i64"),
    "arr": dict(ty="int64[4]", v="[5i64, 5i64, 5i64, 5i64]", rd="%s[0i64]", k="i64"),
    "string": dict(ty="string", v="raw mks()", rd="string_byte_length(%s)", k="i64"),
    "ptr": dict(ty="int64->", v="@z", rd="(<-%s)", k="i64"),
    "opt": dict(ty="int64?", v="5i64", rd="(%s ?? 0i64)", k="i64"),
}
C_P = ["main", "helper", "loop", "lit", "arr"]
C_O = ["read", "if_one", "loop_zero", "pick_one", "addr_r", "byvalue", "self_inc"]
C_YTY = {"i64": "int64", "i32": "int32", "b": "bool"}


def c_obs(t, place, E):
    y = t["rd"] % place
    if t["k"] == "b":
        return ["bool:y = %s;" % y, "if (!y) { %s 13i32; }" % E]
    want, zero = ("5i64", "0i64") if t["k"] == "i64" else ("5i32", "0i32")
    return ["%s:y = %s;" % (C_YTY[t["k"]], y)] + chk("y", want, zero, E)


def c_fn_obs(t, arg):
    """A helper body's observation of `arg`, passing the code."""
    return "".join("    %s\n" % l for l in c_obs(t, arg, "pass")) + "    pass 0i32;\n"


def c_cell(tk, pk, o, da):
    t = C_T[tk]
    if o == "self_inc" and tk not in ("int64", "int32"):
        raise Skip("`x = x + 1` needs an arithmetic type")
    ty, v = t["ty"], t["v"]
    p = Prog()
    p.need("helpers", idf("vb"))
    p.need("helpers", idf("v32"))
    p.need("helpers", idf("v64"))
    if tk == "struct":
        p.need("structs", STRUCT_S)
    if tk == "string":
        p.need("helpers", 'func:mks = string() never fails { pass string_concat("abc", "de"); };\n')
    in_helper = pk == "helper"
    E = "pass" if in_helper else "exit"
    decl = ["int64:z = 5i64;"] if tk == "ptr" else []
    vinit = t.get("v0", v) if o == "self_inc" else v
    if pk == "lit":
        p.structs.append("struct:W = { int64:a; %s:f; };\n" % ty)
        decl.append("W:w = W{ a: 1i64, f: %s };" % vinit if da else "W:w = W{ a: 1i64 };")
        place, addr = "w.f", "(w.f)"
    elif pk == "arr":
        decl.append("%s[4]:arr = [%s, %s, %s, %s];" % (ty, vinit, vinit, vinit, vinit) if da else "%s[4]:arr;" % ty)
        place, addr = "arr[0i64]", "(arr[0i64])"
    else:
        decl.append("%s:x;" % ty)
        place, addr = "x", "x"
    late = da and pk in ("main", "helper", "loop")      # the twin assigns the local by a statement
    lines = list(decl)
    if o == "read":
        lines += (["x = %s;" % v] if late else []) + c_obs(t, place, E)
    elif o == "if_one":
        lines += ["if (raw vb(false)) { %s = %s; }%s" % (place, v, (" else { %s = %s; }" % (place, v)) if late else "")]
        lines += c_obs(t, place, E)
    elif o == "loop_zero":
        lines += (["x = %s;" % v] if late else [])
        lines += ["for (int64:k in 0i64...(raw v64(0i64))) { %s = %s; }" % (place, v)] + c_obs(t, place, E)
    elif o == "pick_one":
        lines += ["pick (raw v32(2i32)) {", "    (1i32) { %s = %s; }," % (place, v),
                  "    (*) { %s }" % (("%s = %s;" % (place, v)) if late else ""), "}"]
        lines += c_obs(t, place, E)
    elif o == "addr_r":
        p.helpers.append("func:rdt = int32(%s->:p) never fails {\n%s};\n" % (ty, c_fn_obs(t, "(<-p)")))
        lines += (["x = %s;" % v] if late else [])
        lines += ["int32:o = raw rdt(@%s);" % addr, "if (o != 0i32) { %s o; }" % E]
    elif o == "byvalue":
        p.helpers.append("func:obt = int32(%s:v) never fails {\n%s};\n" % (ty, c_fn_obs(t, "v")))
        lines += (["x = %s;" % v] if late else [])
        lines += ["int32:o = raw obt(%s);" % place, "if (o != 0i32) { %s o; }" % E]
    elif o == "self_inc":
        lines += (["x = %s;" % t["v0"]] if late else [])
        lines += ["%s = %s + %s;" % (place, place, t["one"])] + c_obs(t, place, E)
    if in_helper:
        p.helpers.append("func:hc = int32() never fails {\n%s    pass 0i32;\n};\n" % "".join("    %s\n" % l for l in lines))
        p.body += ["int32:r = raw hc();", "exit r;"]
    elif pk == "loop":
        p.body += ["for (int64:j in 0i64...1i64) {"] + ["    " + l for l in lines] + ["}", "exit 0i32;"]
    else:
        p.body += lines + ["exit 0i32;"]
    if da:
        exp = X("SAFE", [], None, *R_DA_SAFE)
    elif pk == "lit":
        exp = X("REFUSE", ["NITPICK-TYPE-027"], None, *R_D010_LIT)
    else:
        exp = X("REFUSE", ["NITPICK-ASSIGN-001"], None, *R_D010)
    return p, exp


# ------------------------------------------------------------------ D: constants at the type's edge
D_T = {
    "int8": dict(s="i8", w=8, idf="v8", signed=True, min="(-127i8 - 1i8)", max="127i8"),
    "uint8": dict(s="u8", w=8, idf="vu8", signed=False, min="0u8", top="128u8"),
    "int32": dict(s="i32", w=32, idf="v32", signed=True, min="(-2147483647i32 - 1i32)", max="2147483647i32"),
    "int64": dict(s="i64", w=64, idf="v64", signed=True, min="(-9223372036854775807i64 - 1i64)",
                  max="9223372036854775807i64"),
    "uint64": dict(s="u64", w=64, idf="vu64", signed=False, min="0u64", top="(9223372036854775807u64 + 1u64)"),
}
D_O = ["shl_w", "shl_w1", "shr_w", "shl_neg", "div0", "rem0", "mindiv", "minrem", "negmin",
       "shl_wm1", "shr_wm1", "div1", "rem3", "mindiv1", "negmin1"]
D_FORM = ["const", "rt"]
D_SIGNED_ONLY = ("shl_neg", "mindiv", "minrem", "negmin", "negmin1")
D_TWIN = ("shl_wm1", "shr_wm1", "div1", "rem3", "mindiv1", "negmin1")


def d_cell(tk, o, form):
    t = D_T[tk]
    if o in D_SIGNED_ONLY and not t["signed"]:
        raise Skip("an unsigned type has no negative operand and no negation (TYPE-008, §4's probe p_d17)")
    p = Prog()
    s = t["s"]
    if form == "rt":
        p.helpers.append(idf(t["idf"]))
        L = lambda n: "raw %s(%d%s)" % (t["idf"], n, s)
        MIN = ("(raw %s(%d%s) - raw %s(1%s))" % (t["idf"], -(2 ** (t["w"] - 1) - 1), s, t["idf"], s)
               if t["signed"] else L(0))
    else:
        L = lambda n: "%d%s" % (n, s)
        MIN = t["min"]
    w = t["w"]
    expr = {"shl_w": "%s << %s" % (L(1), L(w)), "shl_w1": "%s << %s" % (L(1), L(w + 1)),
            "shr_w": "%s >> %s" % (L(1), L(w)), "shl_neg": "%s << %s" % (L(1), L(-1)),
            "div0": "%s / %s" % (L(5), L(0)), "rem0": "%s %% %s" % (L(5), L(0)),
            "mindiv": "%s / %s" % (MIN, L(-1)), "minrem": "%s %% %s" % (MIN, L(-1)),
            "negmin": "-%s" % MIN,
            "shl_wm1": "%s << %s" % (L(1), L(w - 1)), "shr_wm1": "%s >> %s" % (L(1), L(w - 1)),
            "div1": "%s / %s" % (L(5), L(1)), "rem3": "%s %% %s" % (L(5), L(3)),
            "mindiv1": "%s / %s" % (MIN, L(1)), "negmin1": "-(%s + %s)" % (MIN, L(1))}[o]
    zero = "0%s" % s
    p.body.append("%s:r = %s;" % (tk, expr))
    if o in D_TWIN:
        want = {"shl_wm1": t["min"] if t["signed"] else t["top"], "shr_wm1": zero, "div1": "5%s" % s,
                "rem3": "2%s" % s, "mindiv1": t["min"], "negmin1": t.get("max")}[o]
        p.body += chk("r", want, zero) + ["exit 0i32;"]
        return p, X("SAFE", [], None, *R_D_SAFE)
    p.body += ["if (r == %s) { exit 13i32; }" % zero, "exit 12i32;"]
    shift = o in ("shl_w", "shl_w1", "shr_w", "shl_neg")
    if form == "const":
        if shift:
            return p, X("REFUSE", ["NITPICK-TYPE-070"], None, *R_SHIFT_K)
        if o == "negmin":
            return p, X("REFUSE", ["NITPICK-TYPE-076"], None, *R_NEG_K)
        return p, X("REFUSE", ["NITPICK-TYPE-004"], None, *R_DIV_K)
    if shift:
        return p, X("TRAP", [], ARM["ShiftRange"], *R_SHIFT_RT)
    if o in ("div0", "rem0"):
        return p, X("TRAP", [], ARM["DivByZero"], *R_DIV0_RT)
    if o in ("mindiv", "minrem"):
        return p, X("TRAP", [], ARM["DivOverflow"], *R_MINDIV_RT)
    return p, X("TRAP", [], ARM["IntOverflow"], *R_NEG_RT)


# ------------------------------------------------------------------ E: stores into a pointee
E_STORE = ["direct", "callee_whole", "callee_field", "callee_elem", "method", "returned", "two_level"]
E_LIFE = ["dies", "outlives"]
E_OBS = ["ra", "rs"]
E_HOLDER = {"direct": "cursor", "callee_whole": "cursor", "callee_field": "seat", "callee_elem": "cursor_arr",
            "method": "seat", "returned": "cursor", "two_level": "cursor"}
CURSOR = "struct:Cursor = { fixed uint8[]:src; int64:pos; };\n"
SEAT = "struct:Seat = { (fixed uint8[]):src; int64:pos; };\n"
OBS_V = ("func:obs_v = int32(fixed uint8[]:v) never fails {\n    if (v.len == 0i64) { pass 23i32; }\n"
         "    if (v[0i64] == 97u8) { pass 21i32; }\n    if (v[0i64] == 103u8) { pass 22i32; }\n"
         "    if (v[0i64] == 115u8) { pass 25i32; }\n    if (v[0i64] == 170u8) { pass 70i32; }\n    pass 24i32;\n};\n")
RESET = ("func:reset = NIL(Cursor->:c, fixed uint8[]:src) never fails {\n    <-c = Cursor{ src: src, pos: 0i64 };\n"
         "    pass NIL;\n};\n")


def e_cell(store, life, ob):
    p = Prog()
    holder = E_HOLDER[store]
    p.structs.append(SEAT if holder == "seat" else CURSOR)
    p.helpers += ['func:orig = string() never fails { pass string_concat("abc", "def"); };\n',
                  'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n']
    if ob == "rs":
        p.helpers.append('func:sen = string() never fails { pass string_concat("stuv", "wxyz"); };\n')
    p.helpers.append(OBS_V)
    V = "string_bytes(t)"
    if store == "direct":
        stmt = "c = Cursor{ src: %s, pos: 0i64 };" % V
    elif store == "callee_whole":
        p.helpers.append(RESET)
        stmt = "drop reset(@c, %s);" % V
    elif store == "callee_field":
        p.helpers.append("func:reseat = NIL(Seat->:c, fixed uint8[]:src) never fails {\n    c.src = src;\n    pass NIL;\n};\n")
        stmt = "drop reseat(@c, %s);" % V
    elif store == "callee_elem":
        p.helpers.append("func:seti = NIL(Cursor[2]->:a, fixed uint8[]:src) never fails {\n"
                         "    (<-a)[0i64] = Cursor{ src: src, pos: 0i64 };\n    pass NIL;\n};\n")
        stmt = "drop seti(@cs, %s);" % V
    elif store == "method":
        p.helpers.append("impl:Seat = { func:seat = NIL(Seat->:self, fixed uint8[]:src) never fails "
                         "{ self.src = src; pass NIL; }; };\n")
        stmt = "drop c.seat(%s);" % V
    elif store == "returned":
        p.helpers.append("func:mkc = Cursor(fixed uint8[]:src) never fails {\n    pass Cursor{ src: src, pos: 0i64 };\n};\n")
        stmt = "c = raw mkc(%s);" % V
    else:
        p.helpers += [RESET, "func:reset2 = NIL(Cursor->:c, fixed uint8[]:src) never fails {\n"
                             "    drop reset(c, src);\n    pass NIL;\n};\n"]
        stmt = "drop reset2(@c, %s);" % V
    b = p.body
    b.append("string:s = raw orig();")
    if life == "outlives":
        b.append("string:t = raw fresh();")
    if holder == "cursor_arr":
        b.append("Cursor[2]:cs = [Cursor{ src: string_bytes(s), pos: 0i64 }, Cursor{ src: string_bytes(s), pos: 0i64 }];")
        cond, view = "cs[1i64].pos == 0i64", "cs[0i64].src"
    else:
        ht = "Seat" if holder == "seat" else "Cursor"
        b.append("%s:c = %s{ src: string_bytes(s), pos: 0i64 };" % (ht, ht))
        cond, view = "c.pos == 0i64", "c.src"
    b.append("if (%s) {" % cond)
    if life == "dies":
        b.append("    string:t = raw fresh();")
    b += ["    " + stmt, "}"]
    if ob == "rs":
        b.append("string:z = raw sen();")
    b += ["int32:o = raw obs_v(%s);" % view, "if (o != 22i32) { exit o; }", "exit 0i32;"]
    if life == "dies":
        return p, X("REFUSE", ["NITPICK-BORROW-002"], None, *R_D004)
    return p, X("SAFE", [], None, *R_E_SAFE)


# ------------------------------------------------------------------ the space
def enumerate_space():
    """Every combination, section by section: (section, T, P, O, observer, builder)."""
    for tk in A_T:
        for decl in A_DECL:
            for o in A_OPS:
                yield "A", tk, decl, o, "exit", (lambda tk=tk, decl=decl, o=o: a_cell(tk, decl, o))
    for pk in B_P:
        for o in B_O:
            for tk in B_T:
                yield "B", tk, pk, o, "exit", (lambda tk=tk, pk=pk, o=o: b_cell(tk, pk, o))
    for tk in C_T:
        for pk in C_P:
            for o in C_O:
                for da in (False, True):
                    yield ("C", tk, pk, o + ("_da" if da else ""), "exit",
                           (lambda tk=tk, pk=pk, o=o, da=da: c_cell(tk, pk, o, da)))
    for tk in D_T:
        for o in D_O:
            for form in D_FORM:
                yield "D", tk, form, o, "exit", (lambda tk=tk, o=o, form=form: d_cell(tk, o, form))
    for store in E_STORE:
        for life in E_LIFE:
            for ob in E_OBS:
                yield ("E", E_HOLDER[store], life, store, ob,
                       (lambda store=store, life=life, ob=ob: e_cell(store, life, ob)))


WILD_RE = re.compile(r"\bwildx?\b")


def build():
    """-> (cells, skipped): cells a list of (id, source, meta), skipped of (section, T, P, O, observer, reason)."""
    cells, skipped = [], []
    for sid, def_, path, sha, exp in SEEDS:
        src = SEED_TEXT[sid]
        meta = {"id": sid, "section": "S", "T": "seed", "P": "seed", "O": "seed", "observer": "exit",
                "scope": "wild" if WILD_RE.search(src) else "plain", "seed_of": def_,
                "seed_source": path, "seed_sha256": sha}
        meta.update(exp)
        cells.append((sid, src, meta))
    n = 0
    for section, tk, pk, o, ob, make in enumerate_space():
        try:
            prog, exp = make()
        except Skip as e:
            skipped.append((section, tk, pk, o, ob, str(e)))
            continue
        n += 1
        cid = "g%04d_%s_%s_%s_%s" % (n, section.lower(), tk, pk, o) + ("_" + ob if section == "E" else "")
        src = prog.render(cid)
        meta = {"id": cid, "section": section, "T": tk, "P": pk, "O": o, "observer": ob,
                "scope": "wild" if WILD_RE.search(src) else "plain"}
        meta.update(exp)
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
        fh.write("# section T P O observer -- reason (%d combinations not emitted)\n" % len(skipped))
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
def selfcheck(out):
    errs = []
    cells, skipped = build()
    again = build()
    if again != (cells, skipped):
        errs.append("two builds differ: the generator is not deterministic")
    ids = [c[0] for c in cells]
    if len(set(ids)) != len(ids):
        errs.append("duplicate ids")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import m10, m11lib  # noqa: E402
    if TRAPS != m10.TRAPS:
        errs.append("TRAPS differs from gen/m10.py's")
    if sorted(TRAPS + OTHER, key=lambda a: a[1]) != sorted(m11lib.TRAPS, key=lambda a: a[1]):
        errs.append("TRAPS + OTHER differs from gen/m11lib.py's (S44)")
    for sid, def_, path, sha, exp in SEEDS:
        if hashlib.sha256(SEED_TEXT[sid].encode()).hexdigest() != sha:
            errs.append("seed %s: the embedded text's sha256 is not the recorded one" % sid)
        if os.path.exists(path):
            with open(path, "rb") as fh:
                if hashlib.sha256(fh.read()).hexdigest() != sha:
                    errs.append("seed %s: its source's sha256 is not the recorded one" % sid)
    need = ("id", "T", "P", "O", "observer", "expect", "section", "expect_codes", "expect_exit", "rule",
            "source", "scope")
    for cid, src, m in cells:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", cid):
            errs.append("%s: id is no module name" % cid)
        mods = re.findall(r"^mod:(\w+);", src, re.M)      # a seed may open with comments
        if mods != [cid] or m["id"] != cid:
            errs.append("%s: id, mod: name and meta disagree" % cid)
        for k in need:
            if k not in m:
                errs.append("%s: meta lacks %s" % (cid, k))
        if not m.get("rule") or not m.get("source"):
            errs.append("%s: no rule text or source" % cid)
        e = m["expect"]
        if e == "REFUSE" and not m["expect_codes"]:
            errs.append("%s: REFUSE without a code" % cid)
        if e == "TRAP" and m["expect_exit"] not in ARM.values():
            errs.append("%s: TRAP exit is no failsafe arm" % cid)
        if e == "SAFE" and (m["expect_codes"] or m["expect_exit"] is not None):
            errs.append("%s: SAFE with codes or an exit" % cid)
        if (m["scope"] == "wild") != bool(WILD_RE.search(src)):
            errs.append("%s: scope disagrees with the program" % cid)
        if m["section"] == "S":
            continue
        # layout: helpers before main, failsafe directly after main, the grid's failsafe
        tops = [(mt.start(), mt.group(1)) for mt in re.finditer(r"^(?:async )?func:(\w+)", src, re.M)]
        names = [t[1] for t in tops]
        if names.count("main") != 1 or names[-1] != "failsafe" or names[-2] != "main":
            errs.append("%s: helpers are not all before main, or failsafe is not directly after it" % cid)
        if not src.endswith(FAILSAFE13):
            errs.append("%s: the failsafe is not grid13's" % cid)
        # D-013: `exit` only in main and failsafe
        for (s0, name), nxt in zip(tops, tops[1:] + [(len(src), "")]):
            if name not in ("main", "failsafe") and re.search(r"\bexit\b", src[s0:nxt[0]]):
                errs.append("%s: `exit` in %s (D-013)" % (cid, name))
    # denominators: every combination is a cell or a skip
    space = sum(1 for _ in enumerate_space())
    if space != len(cells) - len(SEEDS) + len(skipped):
        errs.append("denominators: %d combinations, %d cells, %d skipped" % (space, len(cells) - len(SEEDS), len(skipped)))
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
    by, sk = counts(cells, skipped)
    for e in errs[:40]:
        print("FAIL " + e)
    print("selfcheck: %d cells (%s), %d skipped, %d combinations; %s"
          % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())), len(skipped), space + len(SEEDS),
             "every check passes" if not errs else "%d FAILURES" % len(errs)))
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cells13")
    ap.add_argument("--selfcheck", action="store_true",
                    help="check ids, layout, expectations, seeds, denominators and the written grid")
    a = ap.parse_args()
    if a.selfcheck:
        sys.exit(selfcheck(a.out))
    cells, skipped = build()
    for sid, def_, path, sha, exp in SEEDS:
        if hashlib.sha256(SEED_TEXT[sid].encode()).hexdigest() != sha:
            sys.exit("seed %s: the embedded text is not the recorded sha256" % sid)
    write(a.out, cells, skipped)
    by, sk = counts(cells, skipped)
    print("generated %d cells (%s), skipped %d (%s)" % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                       len(skipped), ", ".join("%s %d" % kv for kv in sorted(sk.items()))))


if __name__ == "__main__":
    main()
