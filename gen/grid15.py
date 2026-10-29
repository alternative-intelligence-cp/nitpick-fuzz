#!/usr/bin/env python3
"""M15 — the DEF-296 family: a view of a pointer parameter's pointee stored into the
frame's own storage through some road, the pointee then written (the M15 brief's §5;
PROGRESS.md S105 onward).

usage: python3 gen/grid15.py [--out cells15] [--selfcheck]

Writes cells15/<id>/<id>.npk and cells15/<id>/meta.json, cells15/INDEX.jsonl (id
order) and cells15/SKIPPED.txt (every combination not emitted, with its reason). A
cell's id is its file name and its `mod:` name (PLAN 2.2). `cells15/` is gitignored
and regenerable: the fourteen seeds copied from the manager's sets are embedded
below byte for byte, with the manager's SHA256SUMS lines; F-050's two holes are read
from their committed directory, their sha256 checked.

The hazard. `f(S->:p)` stores the VIEW `string_bytes(p.s)` into this frame's storage
by a road R, writes the pointee by a write W (the old body is freed), then reads the
stored view through grid13's observer (21 the original byte, 22 the new one, 25 the
reuse sentinel, 70 the free poison, 23 vacant, 24 anything else); `main` exits 0 on
21 and the observer's code otherwise. D-325's freeze refuses the write
(`NITPICK-BORROW-015`); a compiler that accepts it reads 70 at both legs, a use after
free in safe code. A cell is one R, one W, one provenance V and one placement B:
  V  pp    the view of the pointer parameter's pointee: the hazard, REFUSE;
     twin  `string_bytes("abcdef")`, a literal never freed, in the same text: the
           control the compiler must accept, SAFE (exit 0); its text is its pp
           cell's with the view changed and nothing else (rule 5);
     lo    a frame-local view: deferred (the brief's Deliverable 1), never emitted.
  B  same  the store and the write in one block;
     inner the store, and the holders the road declares, in an inner block that
           ends before the write (the outer holder stays outside); emitted for the
           twelve indirection roads the table carries.
Sections:
  S  the seeds, 16: the eight DEF-296 faces (the compiler's probes_sib/, by way of
     the manager's m15-seeds/), F-050's two holes and the manager's six candidates
     (m15-probes-l163-r2/); T, P, O, observer, R, W, V and B "seed";
  R  the store roads: each road x B x V, with W = dir;
  W  the freeing writes: R = fld x each write but dir x V, with B = same.
Every cell's expectation is written here before its first run (PLAN 9.6). `expect`
is the rule's reading (a pp cell or a seed REFUSE, a twin SAFE); `expect_codes` and
`reg155` are read from gen/m15_expect.tsv, the manager's expectations table (§4):
`expect_codes` the detail of the key's H6 row when that row is `refuse`, else
NITPICK-BORROW-015; `reg155` its REG row's verdict, `leak` or `refuse`.

Codes: 0 the view intact; 70 the free poison through the observer; 170 the poison
byte itself (the DEF-296 seeds' own observer); 21-25 as above; 91-122 and 99 grid13's
failsafe (FAILSAFE13).
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid13 import Prog, X, FAILSAFE13, OBS_V, Skip, WILD_RE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AT = "1480ca8"                                         # HUNT6: the rule is read at this commit
AT_FULL = "1480ca81aa4d9d82976149f7f6ae5e44b2c5c640"
TSV = os.path.join(ROOT, "gen", "m15_expect.tsv")      # the manager's expectations table (§4)
BORROW_015 = "NITPICK-BORROW-015"

# ------------------------------------------------------------------ the rule
# MEMORY_REFERENCE.md at HUNT6, the D-325 paragraph (lines 269-284), from its bold
# opening to its last sentence, its lines joined by one space. --selfcheck re-reads it.
RULE15 = (
    "**A view's root is frozen while the view is live** (D-325, 1.6.1 step 0): a view of a binding — a "
    "view-maker's result (`string_bytes`, `string_from_bytes`), a range view (`l[lo...hi]`), the result "
    'of a call whose own body views what it was handed (`@d`, or a `string` passed by value), a view '
    "moved through a call or pushed into a `List` — is a shared party on its root from the holder's "
    "declaration to the end of its block, or for its call when it is a call's argument, and every "
    'write-capable access of what it views refuses (`NITPICK-BORROW-015`): an assignment into it, '
    '`@root`/`$$m root` handed to a callee that writes through it, a pointer-receiver call, a `move` out '
    "of it, `list_push` on the viewed list. A pointer LOCAL's VALUE handed to a callee is the same access "
    "of what it points at as `@place` (DEF-275, landing 140): the callee's written paths are judged "
    "against the views rooted at the pointer's name, so `Holder->:b = @hd; … string_bytes(b.items[0i64]); "
    '… clobber(b)` refuses as `clobber(@hd)` does; a callee that writes another field, or reads, stands. '
    'Reads, `$$i`, a disjoint field, a disjoint numeral range, a callee that writes nothing through what '
    "it is handed, and a pointer root's own reassignment stay. A struct field viewing another field of "
    'its own struct freezes that field; a view of the very storage a store overwrites refuses at the '
    "store (`NITPICK-BORROW-002`). End the view's block before writing its root, or make the view a copy "
    '(`.clone()`, `string_concat("", …)`).'
)
RULE_OPEN, RULE_CLOSE = "**A view's root is frozen while the view is live**", "`string_concat(\"\", …)`)."
RULE_SRC = "MEMORY_REFERENCE.md, the D-325 paragraph (lines 269-284), at HUNT6 %s" % AT
READ_NOTE = ("the governing landing is read from the registry's shapes at HUNT6 (OPEN_DECISIONS.md), not measured: "
             "M15 runs REG155 and HUNT6 only")

# ------------------------------------------------------------------ the program's parts
STRUCT_S = "struct:S = { string:s; };\n"
HOLDER = "struct:Holder = { (fixed uint8[]):v; int32:k; };\n"
ORIG = 'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
FRESH = 'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
VIEW = {"pp": "string_bytes(p.s)", "twin": 'string_bytes("abcdef")'}
MAIN = ["S:s = S{ s: raw orig() };", "int32:o = raw f(@s);", "if (o != 21i32) { exit o; }", "exit 0i32;"]

BP = "struct:BP = { Holder->:p; int32:n; };\n"
OUTER = "struct:Outer = { Holder->:inner; int32:n; };\n"
BOX = "struct:Box = { Holder[]:sl; int32:n; };\n"
PB = "struct:PB = { Holder->:q; int32:n; };\n"
PUT = "func:put = NIL(Holder->:dst, fixed uint8[]:v) never fails { dst.v = v; pass NIL; };\n"
PUTS = "func:puts = NIL(Holder[]:sl, fixed uint8[]:v) never fails { sl[0i64].v = v; pass NIL; };\n"
PUTQ = "func:putq = NIL(Box->:q, fixed uint8[]:v) never fails { q.sl[0i64].v = v; pass NIL; };\n"
PUTPQ = "func:putpq = NIL(PB->:q, fixed uint8[]:v) never fails { q.q.v = v; pass NIL; };\n"
GB = "func:gb = NIL(Box:b, fixed uint8[]:v) never fails { drop puts(b.sl, v); pass NIL; };\n"
GP = "func:gp = NIL(PB:b, fixed uint8[]:v) never fails { drop put(b.q, v); pass NIL; };\n"
HSET = ("impl:Holder = { func:hset = NIL(Holder->:self, fixed uint8[]:v) never fails { self.v = v; pass NIL; }; "
        "};\n")
IDS = "func:ids = S->(S->:x) never fails { pass x; };\n"
WS = "func:ws = NIL(S->:q) never fails { q.s = raw fresh(); pass NIL; };\n"
WSW = "func:wsw = NIL(S->:q) never fails { <-q = S{ s: raw fresh() }; pass NIL; };\n"
SSET = "impl:S = { func:sset = NIL(S->:self) never fails { self.s = raw fresh(); pass NIL; }; };\n"

H = 'Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };'
ARR = ('Holder[2]:arr = [Holder{ v: string_bytes("zz"), k: 0i32 }, Holder{ v: string_bytes("zz"), k: 0i32 }];')
LST = ["List<Holder>:l = raw list_init::<Holder>(2i64);",
       'drop list_push(@l, Holder{ v: string_bytes("zz"), k: 0i32 });']


def road(st, hp, outer, mov, store, obs, gov):
    """st: structs; hp: helpers; outer: the holders that stay in f's block; mov: the bindings that go into
    the inner block with the store (None: the road has no inner cell); store: "{V}" marks the view."""
    return dict(st=st, hp=hp, outer=outer, mov=mov, store=store, obs=obs, gov=gov)


G156 = "landing 156 (DEF-296, `record_refs_through_indirection`, escape.npk)"
ROADS = {
    "bare": road([], [], [], None, "fixed uint8[]:hv = {V};", "hv",
                 "a holder declared from the view: D-325's own freeze (1.6.1 step 0)"),
    "fld": road([], [], [H], None, "h.v = {V};", "h.v", "a direct field store into the frame's holder: landing 154"),
    "pl": road([], [], [H], ["Holder->:hp = @h;"], "hp.v = {V};", "h.v",
               "a store through a pointer local (`hp.v`): " + G156),
    "pld": road([], [], [H], ["Holder->:hp = @h;"], "(<-hp).v = {V};", "h.v",
                "a store through an explicit dereference of a pointer local (`(<-hp).v`): " + G156),
    "plw": road([], [], [H], ["Holder->:hp = @h;"], "<-hp = Holder{ v: {V}, k: 1i32 };", "h.v",
                "a whole-pointee store through a pointer local (`<-hp = Holder{…}`): " + G156),
    "pf": road([OUTER], [], [H], ["Outer:ou = Outer{ inner: @h, n: 0i32 };"], "ou.inner.v = {V};", "h.v",
               "a store through a pointer field on the path (`ou.inner.v`): " + G156),
    "tl": road([BP], [], [H], ["BP:b = BP{ p: @h, n: 0i32 };", "BP->:bp = @b;"], "bp.p.v = {V};", "h.v",
               "a store through two levels, a pointer local to a struct holding a pointer (`bp.p.v`): " + G156
               + "; in an inner block, DEF-299's shape by the brief's pre-map (OPEN at 163)"),
    "sle": road([], [], [ARR], ["Holder[]:sl = arr[0i64...2i64];"], "sl[0i64].v = {V};", "arr[0i64].v",
                "a store through a local slice's element (`sl[0i64].v`): landing 156 (DEF-289's first face)"),
    "rge": road([], [], [ARR], None, "arr[0i64...2i64][0i64].v = {V};", "arr[0i64].v",
                "a direct store through a range of the array itself: landing 158 (DEF-300)"),
    "lst": road([], [], LST, ["List<Holder>->:lp = @l;"], "(<-lp)[0i64].v = {V};", "l[0i64].v",
                "a store through a pointer local to a `List`'s element (`(<-lp)[0i64].v`): " + G156),
    "cad": road([], [PUT], [H], None, "drop put(@h, {V});", "h.v",
                "a callee's store through `@h` (the store matrix): landing 116 (DEF-252)"),
    "cpl": road([], [PUT], [H], ["Holder->:hp = @h;"], "drop put(hp, {V});", "h.v",
                "a callee's store through a pointer local handed by value: " + G156),
    "csl": road([], [PUTS], [ARR], None, "drop puts(arr[0i64...2i64], {V});", "arr[0i64].v",
                "a callee's store through a slice parameter's element, a range argument: landing 157 (DEF-289's "
                "second face)"),
    "cslv": road([], [PUTS], [ARR], ["Holder[]:t = arr[0i64...2i64];"], "drop puts(t, {V});", "arr[0i64].v",
                 "a callee's store through a slice parameter's element, a slice local argument: landing 157 "
                 "(DEF-289's second face)"),
    "cps": road([BOX], [PUTQ], [ARR], ["Box:bx = Box{ sl: arr[0i64...2i64], n: 0i32 };"], "drop putq(@bx, {V});",
                "arr[0i64].v",
                "a callee's store through a box's slice field (`q.sl[0i64].v`, `Box->:q`): the store matrix records "
                "it on the box (landing 116); in an inner block, DEF-299 (the pointee frozen, not what its field "
                "views; OPEN at 163)"),
    "cpp": road([PB], [PUTPQ], [H], ["PB:pb = PB{ q: @h, n: 0i32 };"], "drop putpq(@pb, {V});", "h.v",
                "a callee's store through a box's pointer field (`q.q.v`, `PB->:q`): the store matrix records it "
                "on the box (landing 116); in an inner block, DEF-299's pointer twin (OPEN at 163)"),
    "cbv": road([BOX], [PUTS, GB], [ARR], None, "drop gb(Box{ sl: arr[0i64...2i64], n: 0i32 }, {V});",
                "arr[0i64].v",
                "a by-value box's slice field handed on to a storing callee: DEF-298 (OPEN at 163)"),
    "cbp": road([PB], [PUT, GP], [H], None, "drop gp(PB{ q: @h, n: 0i32 }, {V});", "h.v",
                "a by-value box's pointer field handed on to a storing callee: DEF-298's shape by the brief's "
                "pre-map (OPEN at 163)"),
    "mth": road([], [HSET], [H], None, "drop h.hset({V});", "h.v",
                "a method's store through its `Self->` receiver (the store matrix): landing 116 (DEF-252)"),
    "mpl": road([], [HSET], [H], ["Holder->:hp = @h;"], "drop hp.hset({V});", "h.v",
                "a method's store through a pointer local's receiver: " + G156),
}
INNER_ROADS = ("pl", "pld", "plw", "pf", "tl", "sle", "lst", "cpl", "cslv", "mpl", "cps", "cpp")
NO_INNER = {
    "bare": "the road's holder is the store itself (`fixed uint8[]:hv = view;`): in an inner block it would die "
            "before the write, holding nothing past it",
    "fld": "a direct store into the outer holder by its name: no binding of the road's to declare in an inner block",
    "rge": "the range is an expression over the outer array: no binding of the road's to declare in an inner block",
    "cad": "the callee is handed `@h`, an expression over the outer holder: no binding of the road's to declare in "
           "an inner block",
    "csl": "the slice argument is a range expression over the outer array: no binding of the road's to declare in "
           "an inner block",
    "cbv": "the box is a by-value argument expression: no binding of the road's to declare in an inner block",
    "cbp": "the box is a by-value argument expression: no binding of the road's to declare in an inner block",
    "mth": "the method is called on the outer holder by its name: no binding of the road's to declare in an inner "
           "block",
}


def write(hp, lines, gov):
    return dict(hp=hp, lines=lines, gov=gov)


WRITES = {
    "dir": write([], ["p.s = raw fresh();"],
                 "the pointee's field written through the parameter (`p.s = …`): D-325's freeze at the write"),
    "whole": write([], ["<-p = S{ s: raw fresh() };"],
                   "the whole pointee written through the parameter (`<-p = S{…}`): D-325's freeze at the write"),
    "alias": write([], ["S->:q = p;", "q.s = raw fresh();"],
                   "the field written through a second pointer (`S->:q = p; q.s = …`): landing 160 (DEF-302)"),
    "walias": write([], ["S->:q = p;", "<-q = S{ s: raw fresh() };"],
                    "the whole pointee written through a second pointer (`<-q = S{…}`): landing 160 (DEF-302)"),
    "callee": write([WS], ["drop ws(p);"],
                    "the parameter handed to a callee that writes through it (`drop ws(p)`): D-325's `@root` "
                    "handed to a writing callee"),
    "calias": write([WS], ["S->:q = p;", "drop ws(q);"],
                    "a second pointer handed to a writing callee (`drop ws(q)`): landing 160 (DEF-302), with "
                    "DEF-275's pointer value (landing 140)"),
    "cwhole": write([WSW], ["S->:q = p;", "drop wsw(q);"],
                    "a second pointer handed to a callee replacing the whole pointee (`drop wsw(q)`): landing 160 "
                    "(DEF-302) and landing 163 (DEF-308)"),
    "method": write([SSET], ["drop p.sset();"],
                    "a writing `Self->` method called on the parameter (`drop p.sset()`): a pointer-receiver call "
                    "(D-325), through `check_written` since landing 160 (DEF-302)"),
    "cres": write([IDS], ["(<-(raw ids(p))) = S{ s: raw fresh() };"],
                  "the whole pointee written through a call-result pointer (`(<-(raw ids(p))) = S{…}`): DEF-309 "
                  "(OPEN at 163)"),
    "cresc": write([IDS, WS], ["drop ws(raw ids(p));"],
                   "a call-result pointer handed to a writing callee (`drop ws(raw ids(p))`): landing 161 (DEF-305)"),
    "cresm": write([IDS, SSET], ["drop (raw ids(p)).sset();"],
                   "a writing method called on a call-result pointer (`drop (raw ids(p)).sset()`): landing 161 "
                   "(DEF-305)"),
    "cresf": None,
}
PLACES = ("same", "inner")
PROVENANCE = ("pp", "twin", "lo")
LO_REASON = ("the frame-local view `lo` is the second hazard shape, deferred to a later milestone (the brief's "
             "Deliverable 1 and §4): M15 sweeps pp and twin only")
CRESF_REASON = ("`(raw ids(p)).s = …` is no place: NITPICK-TYPE-024 at HUNT6 and REG155 for the hazard and its twin "
                "(§4's probes q18_pp_fld_cresf and q18t_pp_fld_cresf), so there is no program to run")
WSIDE_REASON = ("the write-side sweep runs on the `fld` road only (the brief's §5: R = fld x each W); every other "
                "road is swept with W = dir")
NOT_INNER_REASON = "%s; the inner placement is emitted for the twelve indirection roads the table carries only"

# ------------------------------------------------------------------ S: the seeds
SEED_SET = "/home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs"
FACES_ORIGIN = ".internal/handoff_35/probes_sib/ in the compiler's tree (read only), copied by the manager to %s" % (
    SEED_SET + "/m15-seeds/")
FACES = ["s11_pointer_local_field", "s11b_deref_field", "s11c_ptr_local_list_elem", "s11d_ptr_local_whole_pointee",
         "s11f_ptr_local_to_byvalue_param_field", "s11g_ptr_field_on_path", "s11h_ptr_local_async_frame",
         "s24_callee_store_via_ptr_local_arg"]
CANDIDATES = [("q05_pp_tl_dir_in", "pp:tl:dir:inner", "DEF-299"), ("q11_pp_cps_dir_in", "pp:cps:dir:inner", "DEF-299"),
              ("q12_pp_cpp_dir_in", "pp:cpp:dir:inner", "DEF-299"), ("q17_pp_fld_cres", "pp:fld:cres:same", "DEF-309"),
              ("q19_pp_fld_cresc", "pp:fld:cresc:same", "DEF-305"),
              ("q20_pp_fld_cresm", "pp:fld:cresm:same", "DEF-305")]
F050_DIR = "findings/F-050-callee-view-store-into-array-element"
F050 = [("elem_callee", "4597090a39da72374a955e99948a68e61358ad163ebeab4cbc66ffba9f519d3e"),
        ("elem_field_callee", "f09dab9aeeec4e7fb720b11d97ac36c8fb8aaacfff20dc2ebf37c673f5a200a3")]
# m15-seeds/SHA256SUMS, whole, and lines 9, 21, 23, 33, 37 and 39 of m15-probes-l163-r2/SHA256SUMS,
# as the manager wrote them; --selfcheck matches each embedded program against its line.
SUMS = {
    "m15-seeds": (
        "b90a72c26092d38a3bb2f76c60470bbbb6885f83ee09b8dc183169c9048caa4b  s11b_deref_field.npk\n"
        "9ccb379c194baea3332ce0b106d837b8bd2faecc3d74ff62fbce761483ce63f9  s11c_ptr_local_list_elem.npk\n"
        "bbbbb75873599b6bf210867c9c0df41efb9dc6092a684341e8647644c4740c49  s11d_ptr_local_whole_pointee.npk\n"
        "2e4c459597054da85e47c95fe8012ffef730fcdd43341bedb1a88c714998d7a7  s11f_ptr_local_to_byvalue_param_field.npk\n"
        "b54611fcd8e6e752873a3b02b82f05cf77f471fd4344b2c0ef0c56d79359a609  s11g_ptr_field_on_path.npk\n"
        "32e61310f34cc756e20e8523a4f4b2f380f118277ce92f314c39ecafb6d2061c  s11h_ptr_local_async_frame.npk\n"
        "14d6e4cb781c903bda9a1960242cc58c2ec87db229fa8ce7986cbe18e12d39dc  s11_pointer_local_field.npk\n"
        "c2d54e51a4a6739f3de362dba985757b1235a67b51f75968da0da50551ff61c2  s24_callee_store_via_ptr_local_arg.npk\n"),
    "m15-probes-l163-r2": (
        "6d254da7214f1ef4124abe0d3ceb2e20979fcd290c54dd37e85ea6b35f258c3e  q05_pp_tl_dir_in.npk\n"
        "be8365caa74c8a064e405621235038edd5b73cffa0fcea6d00acd811ddf36c38  q11_pp_cps_dir_in.npk\n"
        "22df3e04ecd7d20627b0dab81dc211a30a8846480f06276d71edd65949a76970  q12_pp_cpp_dir_in.npk\n"
        "f2305f877fde393044df76c37a66c2e7694ee9efce7f2bff976aa84983235bc2  q17_pp_fld_cres.npk\n"
        "6e283a1a12fb47fd49167a30e7897de5653b396c6982fd592ca83b95f7d36930  q19_pp_fld_cresc.npk\n"
        "ebc9340f7b111c00848d6686ab01034615d80e72e434cf1ea5f56532a25c2d84  q20_pp_fld_cresm.npk\n"),
}


def sums():
    """-> {stem: (sha256, set name)} from the embedded SHA256SUMS lines."""
    out = {}
    for name, block in SUMS.items():
        for line in block.splitlines():
            sha, f = line.split("  ")
            out[f[:-4]] = (sha, name)
    return out


# SEED_TEXT: begin (generated from the manager's sets; each text's sha256 is its SUMS line)
SEED_TEXT = {
    's11_pointer_local_field':
        'mod:s11_pointer_local_field;\n'
        "// a pointee's view stored into a local's field THROUGH A POINTER LOCAL (`hp.v = …`, the auto-dereference), the pointee then written\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Holder->:hp = @h;\n'
        '    hp.v = string_bytes(p.s);\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (h.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11b_deref_field':
        'mod:s11b_deref_field;\n'
        '// s11 with the explicit `<-`: `(<-hp).v = …`\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Holder->:hp = @h;\n'
        '    (<-hp).v = string_bytes(p.s);\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (h.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11c_ptr_local_list_elem':
        'mod:s11c_ptr_local_list_elem;\n'
        "// a pointee's view stored into a List element through a pointer local to the list (`(<-lp)[0i64].v = …`), the pointee then written\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    List<Holder>:l = raw list_init::<Holder>(2i64);\n'
        '    drop list_push(@l, Holder{ v: string_bytes("zz"), k: 0i32 });\n'
        '    List<Holder>->:lp = @l;\n'
        '    (<-lp)[0i64].v = string_bytes(p.s);\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (l[0i64].v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11d_ptr_local_whole_pointee':
        'mod:s11d_ptr_local_whole_pointee;\n'
        "// a struct carrying a pointee's view stored as the WHOLE pointee of a pointer local (`<-hp = Holder{…}`), the pointee then written\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Holder->:hp = @h;\n'
        '    <-hp = Holder{ v: string_bytes(p.s), k: 1i32 };\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (h.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11f_ptr_local_to_byvalue_param_field':
        'mod:s11f_ptr_local_to_byvalue_param_field;\n'
        "// a pointee's view stored through a pointer local that points at a BY-VALUE parameter's field (`hp = @b; hp.v = …`), the pointee then written\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:f = int32(S->:p, Holder:b) never fails {\n'
        '    Holder->:hp = @b;\n'
        '    hp.v = string_bytes(p.s);\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (b.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    int32:r = raw f(@s, h);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11g_ptr_field_on_path':
        'mod:s11g_ptr_field_on_path;\n'
        "// a pointee's view stored through a POINTER FIELD of a local (`o.inner = @h; o.inner.v = …`: a pointer on the path, D-098), the pointee then written\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'struct:Outer = { Holder->:inner; int32:n; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Outer:o = Outer{ inner: @h, n: 0i32 };\n'
        '    o.inner.v = string_bytes(p.s);\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (h.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's11h_ptr_local_async_frame':
        'mod:s11h_ptr_local_async_frame;\n'
        '// the pointer-local road inside a COROUTINE, the view held across an `await`, the pointee then written\n'
        'error:E1;\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'async func:tick = int32() { pass 1i32; };\n'
        'async func:f = int32(S->:p) {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Holder->:hp = @h;\n'
        '    hp.v = string_bytes(p.s);\n'
        '    int32:t = await tick() ?! E1;\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass ((h.v[0i64] => int32) + t - 1i32);\n'
        '};\n'
        'async func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = await f(@s) ?! E1;\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (E1)                { exit 90i32; },\n'
        '        (DeadlineExceeded)  { exit 93i32; },\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    's24_callee_store_via_ptr_local_arg':
        'mod:s24_callee_store_via_ptr_local_arg;\n'
        "// a CALLEE stores the pointee's view into its pointer parameter's pointee; the caller hands a POINTER LOCAL (`put(hp, …)`, not `@h`)\n"
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:put = NIL(Holder->:dst, fixed uint8[]:view) never fails { dst.v = view; pass NIL; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    Holder->:hp = @h;\n'
        '    drop put(hp, string_bytes(p.s));\n'
        '    p.s = string_concat("x", "y");\n'
        '    pass (h.v[0i64] => int32);\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: string_concat("a", "b") };\n'
        '    int32:r = raw f(@s);\n'
        '    if (r != 97i32) { exit (r & 255i32); }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest)    { exit 91i32; },\n'
        '        (HeapOom)           { exit 92i32; },\n'
        '        (Unreachable)       { exit 95i32; },\n'
        '        (WildLeak)          { exit 96i32; },\n'
        '        (StackExhausted)    { exit 106i32; },\n'
        '        (MachineFault)      { exit 107i32; },\n'
        '        (IntOverflow)       { exit 108i32; },\n'
        '        (OutOfBounds)       { exit 109i32; },\n'
        '        (LimitViolated)     { exit 110i32; },\n'
        '        (DecreasesViolated) { exit 111i32; },\n'
        '        (*)                 { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q05_pp_tl_dir_in':
        'mod:q05_pp_tl_dir_in;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'struct:BP = { Holder->:p; int32:n; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    int32:g = 0i32;\n'
        '    if (g == 0i32) {\n'
        '        BP:b = BP{ p: @h, n: 0i32 };\n'
        '        BP->:bp = @b;\n'
        '        bp.p.v = string_bytes(p.s);\n'
        '    }\n'
        '    p.s = raw fresh();\n'
        '    int32:o = raw obs_v(h.v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q11_pp_cps_dir_in':
        'mod:q11_pp_cps_dir_in;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'struct:Box = { Holder[]:sl; int32:n; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:putq = NIL(Box->:q, fixed uint8[]:v) never fails { q.sl[0i64].v = v; pass NIL; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder[2]:arr = [Holder{ v: string_bytes("zz"), k: 0i32 }, Holder{ v: string_bytes("zz"), k: 0i32 }];\n'
        '    int32:g = 0i32;\n'
        '    if (g == 0i32) {\n'
        '        Box:bx = Box{ sl: arr[0i64...2i64], n: 0i32 };\n'
        '        drop putq(@bx, string_bytes(p.s));\n'
        '    }\n'
        '    p.s = raw fresh();\n'
        '    int32:o = raw obs_v(arr[0i64].v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q12_pp_cpp_dir_in':
        'mod:q12_pp_cpp_dir_in;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'struct:PB = { Holder->:q; int32:n; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:putpq = NIL(PB->:q, fixed uint8[]:v) never fails { q.q.v = v; pass NIL; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    int32:g = 0i32;\n'
        '    if (g == 0i32) {\n'
        '        PB:pb = PB{ q: @h, n: 0i32 };\n'
        '        drop putpq(@pb, string_bytes(p.s));\n'
        '    }\n'
        '    p.s = raw fresh();\n'
        '    int32:o = raw obs_v(h.v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q17_pp_fld_cres':
        'mod:q17_pp_fld_cres;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:ids = S->(S->:x) never fails { pass x; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    h.v = string_bytes(p.s);\n'
        '    (<-(raw ids(p))) = S{ s: raw fresh() };\n'
        '    int32:o = raw obs_v(h.v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q19_pp_fld_cresc':
        'mod:q19_pp_fld_cresc;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:ids = S->(S->:x) never fails { pass x; };\n'
        'func:ws = NIL(S->:q) never fails { q.s = raw fresh(); pass NIL; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    h.v = string_bytes(p.s);\n'
        '    drop ws(raw ids(p));\n'
        '    int32:o = raw obs_v(h.v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
    'q20_pp_fld_cresm':
        'mod:q20_pp_fld_cresm;\n'
        '\n'
        'struct:S = { string:s; };\n'
        'struct:Holder = { (fixed uint8[]):v; int32:k; };\n'
        'func:orig = string() never fails { pass string_concat("abc", "def"); };\n'
        'func:fresh = string() never fails { pass string_concat("ghij", "klmn"); };\n'
        'func:obs_v = int32(fixed uint8[]:v) never fails {\n'
        '    if (v.len == 0i64) { pass 23i32; }\n'
        '    if (v[0i64] == 97u8) { pass 21i32; }\n'
        '    if (v[0i64] == 103u8) { pass 22i32; }\n'
        '    if (v[0i64] == 115u8) { pass 25i32; }\n'
        '    if (v[0i64] == 170u8) { pass 70i32; }\n'
        '    pass 24i32;\n'
        '};\n'
        'func:ids = S->(S->:x) never fails { pass x; };\n'
        'impl:S = { func:sset = NIL(S->:self) never fails { self.s = raw fresh(); pass NIL; }; };\n'
        'func:f = int32(S->:p) never fails {\n'
        '    Holder:h = Holder{ v: string_bytes("zz"), k: 0i32 };\n'
        '    h.v = string_bytes(p.s);\n'
        '    drop (raw ids(p)).sset();\n'
        '    int32:o = raw obs_v(h.v);\n'
        '    pass o;\n'
        '};\n'
        'func:main = int32(cstring[]:_~argv) {\n'
        '    S:s = S{ s: raw orig() };\n'
        '    int32:o = raw f(@s);\n'
        '    if (o != 21i32) { exit o; }\n'
        '    exit 0i32;\n'
        '};\n'
        'func:failsafe = int32(Error:e) {\n'
        '    pick (e) {\n'
        '        (HeapBadRequest) { exit 91i32; },\n'
        '        (HeapOom) { exit 92i32; },\n'
        '        (IntOverflow) { exit 93i32; },\n'
        '        (OutOfBounds) { exit 94i32; },\n'
        '        (Unreachable) { exit 95i32; },\n'
        '        (WildLeak) { exit 96i32; },\n'
        '        (DivByZero) { exit 97i32; },\n'
        '        (DivOverflow) { exit 98i32; },\n'
        '        (StaleHandle) { exit 100i32; },\n'
        '        (DeadlineExceeded) { exit 101i32; },\n'
        '        (ChannelClosed) { exit 102i32; },\n'
        '        (DriverLeak) { exit 103i32; },\n'
        '        (IoEof) { exit 104i32; },\n'
        '        (WouldBlock) { exit 105i32; },\n'
        '        (StackExhausted) { exit 106i32; },\n'
        '        (MachineFault) { exit 107i32; },\n'
        '        (LimitViolated) { exit 108i32; },\n'
        '        (DecreasesViolated) { exit 109i32; },\n'
        '        (TbbErr) { exit 110i32; },\n'
        '        (ShiftRange) { exit 111i32; },\n'
        '        (CastRange) { exit 112i32; },\n'
        '        (BadStep) { exit 113i32; },\n'
        '        (BorrowOverlap) { exit 114i32; },\n'
        '        (RequiresViolated) { exit 115i32; },\n'
        '        (EnsuresViolated) { exit 116i32; },\n'
        '        (InvariantViolated) { exit 117i32; },\n'
        '        (Interrupted) { exit 118i32; },\n'
        '        (NotFound) { exit 119i32; },\n'
        '        (Exists) { exit 120i32; },\n'
        '        (CrossDevice) { exit 121i32; },\n'
        '        (BadPath) { exit 122i32; },\n'
        '        (*) { exit 99i32; }\n'
        '    }\n'
        '    exit 9i32;\n'
        '};\n',
}
# SEED_TEXT: end


# ------------------------------------------------------------------ the expectations table
def load_table(path=TSV):
    """-> {(key, "H6"|"REG"): (verdict, detail, logfile, line)}; a duplicate or malformed row is an error."""
    rows = {}
    for raw in open(path, encoding="utf-8"):
        raw = raw.rstrip("\n")
        if not raw or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) != 6:
            raise SystemExit("grid15: a malformed row in %s: %r" % (path, raw[:80]))
        key, comp, verdict, detail, lf, ln = parts
        if (key, comp) in rows:
            raise SystemExit("grid15: a duplicate row in %s: %s %s" % (path, key, comp))
        rows[(key, comp)] = (verdict, detail, lf, int(ln))
    return rows


def expect_of(table, key):
    """-> (expect_codes, reg155) for a hazard key: the H6 row's codes when it refuses, else BORROW-015;
    the REG row's verdict, None when there is no REG row."""
    h6, reg = table.get((key, "H6")), table.get((key, "REG"))
    codes = h6[1].split(",") if h6 and h6[0] == "refuse" else [BORROW_015]
    return codes, (reg[0] if reg else None)


# ------------------------------------------------------------------ a cell
def pp_key(R, W, B):
    return "pp:%s:%s:%s" % (R, W, B)


def program(R, W, B, V):
    """-> the Prog of one combination; Skip with the reason when it is not emitted."""
    if V == "lo":
        raise Skip(LO_REASON)
    wr = WRITES[W]
    if wr is None:
        raise Skip(CRESF_REASON)
    if W != "dir" and R != "fld":
        raise Skip(WSIDE_REASON)
    rd = ROADS[R]
    if B == "inner" and R not in INNER_ROADS:
        raise Skip(NOT_INNER_REASON % NO_INNER[R])
    p = Prog()
    for s in [STRUCT_S, HOLDER] + rd["st"]:
        p.need("structs", s)
    for h in [ORIG, FRESH, OBS_V] + rd["hp"] + wr["hp"]:
        p.need("helpers", h)
    store = rd["store"].replace("{V}", VIEW[V])
    body = list(rd["outer"])
    if B == "same":
        body += (rd["mov"] or []) + [store]
    else:
        body += ["int32:g = 0i32;", "if (g == 0i32) {"] + ["    " + l for l in rd["mov"] + [store]] + ["}"]
    body += wr["lines"] + ["int32:o = raw obs_v(%s);" % rd["obs"], "pass o;"]
    p.helpers.append("func:f = int32(S->:p) never fails {\n%s};\n" % "".join("    %s\n" % l for l in body))
    p.body = list(MAIN)
    return p


def source_of(R, W, B, V):
    s = "%s; the road: %s; the write: %s (%s)" % (RULE_SRC, ROADS[R]["gov"], WRITES[W]["gov"], READ_NOTE)
    if V == "twin":
        s += ("; the twin: its view is a literal (`string_bytes(\"abcdef\")`), an owned constant never freed, so "
              "the write frees nothing it views and it runs to 0 (rule 5's control: an analysis flagging the road, "
              "not the stored borrow, refuses it)")
    return s


def enumerate_space():
    """Every (R, W, B, V) combination, in the order ids are given: (section, R, W, B, V)."""
    for R in ROADS:
        for W in WRITES:
            for B in PLACES:
                for V in PROVENANCE:
                    yield ("R" if W == "dir" else "W"), R, W, B, V


def build():
    """-> (cells, skipped): cells a list of (id, source, meta), skipped of (section, R, W, B, V, reason)."""
    table = load_table()
    cells, skipped = [], []
    smap = sums()
    for stem in FACES:
        codes, reg = expect_of(table, "seed:" + stem)
        cells.append(seed_cell(stem, SEED_TEXT[stem], "seed:" + stem, "DEF-296", SEED_SET + "/m15-seeds/%s.npk" % stem,
                               smap[stem][0], codes, reg,
                               "DEF-296 (registered and fixed at landing 156); measured by the manager at 1480ca8 and "
                               "02856cf under LLVM 20.1.2 (m15-grid-l163l155.log)", origin=FACES_ORIGIN))
    for name, sha in F050:
        path = os.path.join(F050_DIR, name + ".npk")
        with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
            text = fh.read()
        codes, reg = expect_of(table, "seed:F050:" + name)
        cells.append(seed_cell(name, text, "seed:F050:" + name, "DEF-272 (F-050)", path, sha, codes, reg,
                               "F-050 = DEF-272, fixed at landing 138; measured by the manager at 1480ca8 and 02856cf "
                               "under LLVM 20.1.2 with the programs' sha256 (m15-f050-l163l155.log)"))
    for stem, key, def_ in CANDIDATES:
        codes, reg = expect_of(table, key)
        cells.append(seed_cell(stem, SEED_TEXT[stem], key, "candidate, pre-mapped to %s (the brief's §7)" % def_,
                               SEED_SET + "/m15-probes-l163-r2/%s.npk" % stem, smap[stem][0], codes, reg,
                               "the manager's candidate, measured at 1480ca8 (163), 249eae9 (161) and 02856cf (155) "
                               "under LLVM 20.1.2 (m15-probes-l163-r2.log, m15-probes-l155.log); pre-mapped to %s"
                               % def_))
    n = 0
    pending = {}
    for section, R, W, B, V in enumerate_space():
        try:
            prog = program(R, W, B, V)
        except Skip as e:
            skipped.append((section, R, W, B, V, str(e)))
            continue
        n += 1
        cid = "n%03d_%s_%s_%s_%s" % (n, V, R, W, B)
        src = prog.render(cid)
        meta = {"id": cid, "section": section, "T": V, "P": R, "O": "%s_%s" % (W, B), "observer": "exit",
                "R": R, "W": W, "V": V, "B": B, "key": pp_key(R, W, B) if V == "pp" else None, "pair": None,
                "scope": "wild" if WILD_RE.search(src) else "plain"}
        if V == "pp":
            codes, reg = expect_of(table, pp_key(R, W, B))
            meta.update(X("REFUSE", codes, None, RULE15, source_of(R, W, B, V)))
            meta["reg155"] = reg
        else:
            meta.update(X("SAFE", [], 0, RULE15, source_of(R, W, B, V)))
            meta["reg155"] = None
        pending.setdefault((R, W, B), {})[V] = meta
        cells.append((cid, src, meta))
    for pair in pending.values():
        if "pp" in pair and "twin" in pair:
            pair["pp"]["pair"], pair["twin"]["pair"] = pair["twin"]["id"], pair["pp"]["id"]
    return cells, skipped


def seed_cell(cid, text, key, of, path, sha, codes, reg, source, origin=None):
    meta = {"id": cid, "section": "S", "T": "seed", "P": "seed", "O": "seed", "observer": "seed",
            "R": "seed", "W": "seed", "V": "seed", "B": "seed", "key": key, "pair": None,
            "scope": "wild" if WILD_RE.search(text) else "plain", "seed_of": of, "seed_source": path,
            "seed_sha256": sha}
    if origin:
        meta["seed_origin"] = origin
    meta.update(X("REFUSE", codes, None, RULE15, source))
    meta["reg155"] = reg
    return (cid, text, meta)


def write_grid(out, cells, skipped):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for cid, src, meta in cells:
        d = os.path.join(out, cid)
        os.makedirs(d)
        with open(os.path.join(d, cid + ".npk"), "w", encoding="utf-8") as fh:
            fh.write(src)
        with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=1)
    with open(os.path.join(out, "INDEX.jsonl"), "w", encoding="utf-8") as fh:
        for _, _, meta in sorted(cells, key=lambda c: c[0]):
            fh.write(json.dumps(meta) + "\n")
    with open(os.path.join(out, "SKIPPED.txt"), "w", encoding="utf-8") as fh:
        fh.write("# section R W B V -- reason (%d combinations not emitted)\n" % len(skipped))
        for s in skipped:
            fh.write("%s %s %s %s %s -- %s\n" % s)


def counts(cells, skipped):
    by, sk = {}, {}
    for _, _, m in cells:
        k = m["section"] + ("" if m["section"] == "S" else ":" + m["V"])
        by[k] = by.get(k, 0) + 1
    for s in skipped:
        sk[s[5][:24]] = sk.get(s[5][:24], 0) + 1
    return by, sk


# ------------------------------------------------------------------ the self-check
def rule_at_hunt6():
    """The D-325 paragraph from HUNT6's MEMORY_REFERENCE.md, joined; None when the compiler clone is not here."""
    clone = os.path.join(ROOT, ".work", "nitpick")
    if not os.path.isdir(clone):
        return None
    p = subprocess.run(["git", "-C", clone, "show", AT_FULL + ":meta/specs/MEMORY_REFERENCE.md"],
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if p.returncode != 0:
        return None
    lines = p.stdout.decode("utf-8").split("\n")
    starts = [i for i, l in enumerate(lines) if RULE_OPEN in l]
    if len(starts) != 1:
        return "(%d lines open the paragraph at HUNT6)" % len(starts)
    out = []
    for l in lines[starts[0]:]:
        out.append(l.strip())
        if RULE_CLOSE in l:
            break
    s = " ".join(out)
    if RULE_CLOSE not in s:
        return "(the paragraph's last sentence is not found at HUNT6)"
    return s[s.index(RULE_OPEN):s.index(RULE_CLOSE) + len(RULE_CLOSE)]


def selfcheck(out):
    errs, notes = [], []
    cells, skipped = build()
    if build() != (cells, skipped):
        errs.append("two builds differ: the generator is not deterministic")
    ids = [c[0] for c in cells]
    if len(set(ids)) != len(ids):
        errs.append("duplicate ids")
    by_id = {cid: (src, m) for cid, src, m in cells}
    table = load_table()
    # the rule, copied from HUNT6's file
    h6 = rule_at_hunt6()
    if h6 is None:
        notes.append("the rule was not compared with HUNT6's file: no compiler clone with %s here" % AT)
    elif h6 != RULE15:
        errs.append("RULE15 differs from the D-325 paragraph at HUNT6 %s" % AT)
    else:
        notes.append("RULE15 equals the D-325 paragraph at HUNT6 %s" % AT)
    # the seeds: each embedded text against the manager's SHA256SUMS line; F-050's files against their sha256
    smap = sums()
    if sorted(smap) != sorted(FACES + [c[0] for c in CANDIDATES]) or sorted(SEED_TEXT) != sorted(smap):
        errs.append("the embedded seeds are not the eight faces and the six candidates, one SUMS line each")
    for stem, (sha, setname) in sorted(smap.items()):
        if stem not in SEED_TEXT or hashlib.sha256(SEED_TEXT[stem].encode("utf-8")).hexdigest() != sha:
            errs.append("seed %s: the embedded text's sha256 is not its %s/SHA256SUMS line" % (stem, setname))
    for name, sha in F050:
        with open(os.path.join(ROOT, F050_DIR, name + ".npk"), "rb") as fh:
            if hashlib.sha256(fh.read()).hexdigest() != sha:
                errs.append("seed %s: %s/%s.npk's sha256 is not the recorded one" % (name, F050_DIR, name))
    # the table: every pp key has an H6 and a REG row, and the emitted pp keys are the table's
    tkeys = sorted(set(k for k, _ in table))
    t_pp = sorted(k for k in tkeys if k.startswith("pp:"))
    for k in tkeys:
        for comp in ("H6", "REG"):
            if (k, comp) not in table:
                errs.append("the table's %s has no %s row" % (k, comp))
    for (k, comp), (verdict, detail, lf, ln) in table.items():
        if verdict not in ("refuse", "leak"):
            errs.append("the table's %s %s row is %s, neither refuse nor leak" % (k, comp, verdict))
    g_pp = sorted(m["key"] for _, _, m in cells if m["V"] == "pp")
    if g_pp != t_pp:
        errs.append("STOP: the emitted pp keys (%d) are not the table's %d pp keys: missing %s, extra %s"
                    % (len(g_pp), len(t_pp), sorted(set(t_pp) - set(g_pp))[:5], sorted(set(g_pp) - set(t_pp))[:5]))
    g_seed = sorted(m["key"] for _, _, m in cells if m["V"] == "seed")
    t_seed = sorted(k for k in tkeys if k.startswith("seed:")) + sorted(c[1] for c in CANDIDATES)
    if g_seed != sorted(t_seed):
        errs.append("the seeds' keys are not the table's seed keys and the six candidates' pp keys")
    need = ("id", "T", "P", "O", "observer", "expect", "section", "expect_codes", "expect_exit", "rule", "source",
            "scope", "R", "W", "V", "B", "key", "pair", "reg155")
    for cid, src, m in cells:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", cid):
            errs.append("%s: id is no module name" % cid)
        mods = re.findall(r"^mod:(\w+);", src, re.M)
        if mods != [cid] or m["id"] != cid:
            errs.append("%s: id, mod: name and meta disagree" % cid)
        for k in need:
            if k not in m:
                errs.append("%s: meta lacks %s" % (cid, k))
        if m.get("rule") != RULE15 or not m.get("source"):
            errs.append("%s: the rule is not RULE15, or there is no source" % cid)
        if m["scope"] != "plain" or WILD_RE.search(src):
            errs.append("STOP: %s carries `wild`" % cid)
        if any(not c.startswith("NITPICK-BORROW-") for c in m["expect_codes"]):
            errs.append("%s: an expected code is not a BORROW code: %s" % (cid, m["expect_codes"]))
        if m["V"] in ("pp", "seed"):
            if m["expect"] != "REFUSE" or not m["expect_codes"] or m["expect_exit"] is not None:
                errs.append("%s: a hazard cell is not REFUSE with codes and no exit" % cid)
            codes, reg = expect_of(table, m["key"])
            if m["expect_codes"] != codes or m["reg155"] != reg:
                errs.append("%s: expect_codes/reg155 %s/%s, the table %s/%s" % (cid, m["expect_codes"], m["reg155"],
                                                                                codes, reg))
            if m["reg155"] not in ("leak", "refuse"):
                errs.append("%s: reg155 is %r: every hazard cell needs its REG row" % (cid, m["reg155"]))
        elif m["V"] == "twin":
            if m["expect"] != "SAFE" or m["expect_codes"] or m["expect_exit"] != 0 or m["reg155"] is not None:
                errs.append("%s: a twin is not SAFE with exit 0, no codes and no reg155" % cid)
        else:
            errs.append("%s: provenance %r" % (cid, m["V"]))
        if m["section"] == "S":
            if hashlib.sha256(src.encode("utf-8")).hexdigest() != m["seed_sha256"]:
                errs.append("%s: the seed's text is not the program its sha256 names" % cid)
            continue
        # rule 5: the twin is its pp cell with the view changed, exactly once
        if m["V"] == "pp":
            tw = m["pair"]
            if tw not in by_id:
                errs.append("%s: no twin" % cid)
            else:
                tsrc, tm = by_id[tw]
                if src.count(VIEW["pp"]) != 1 or VIEW["twin"] in src:
                    errs.append("%s: the hazard's view does not occur exactly once" % cid)
                want = src.replace(VIEW["pp"], VIEW["twin"], 1).replace("mod:%s;" % cid, "mod:%s;" % tw, 1)
                if tsrc != want or tm["pair"] != cid or (tm["R"], tm["W"], tm["B"]) != (m["R"], m["W"], m["B"]):
                    errs.append("%s: its twin %s is not its text with only the view changed" % (cid, tw))
        # layout: helpers before main, failsafe directly after main, grid13's failsafe; D-013
        tops = [(mt.start(), mt.group(1)) for mt in re.finditer(r"^(?:async )?func:(\w+)", src, re.M)]
        names = [t[1] for t in tops]
        if names.count("main") != 1 or names[-1] != "failsafe" or names[-2] != "main" or names[-3] != "f":
            errs.append("%s: f, main and failsafe are not the last three functions in that order" % cid)
        if not src.endswith(FAILSAFE13):
            errs.append("%s: the failsafe is not grid13's" % cid)
        for (s0, name), nxt in zip(tops, tops[1:] + [(len(src), "")]):
            if name not in ("main", "failsafe") and re.search(r"\bexit\b", src[s0:nxt[0]]):
                errs.append("%s: `exit` in %s (D-013)" % (cid, name))
    # placement: inner for exactly the twelve indirection roads
    inner = sorted(set(m["R"] for _, _, m in cells if m["B"] == "inner"))
    if inner != sorted(INNER_ROADS):
        errs.append("the inner placement is emitted for %s, not the twelve roads" % inner)
    # denominators: every combination is a cell or a skip
    space = sum(1 for _ in enumerate_space())
    grid = len(cells) - len(FACES) - len(F050) - len(CANDIDATES)
    if space != grid + len(skipped):
        errs.append("denominators: %d combinations, %d cells, %d skipped" % (space, grid, len(skipped)))
    # the written grid, if there is one, is this build byte for byte
    if os.path.isdir(out):
        for cid, src, m in cells:
            f = os.path.join(out, cid, cid + ".npk")
            if not os.path.exists(f) or open(f, encoding="utf-8").read() != src:
                errs.append("%s/%s differs from this build" % (out, cid))
            mf = os.path.join(out, cid, "meta.json")
            if not os.path.exists(mf) or json.load(open(mf, encoding="utf-8")) != m:
                errs.append("%s/%s/meta.json differs from this build" % (out, cid))
        on_disk = sorted(d for d in os.listdir(out) if os.path.isdir(os.path.join(out, d)))
        if on_disk != sorted(ids):
            errs.append("%s holds other cells than this build" % out)
        idx = [json.loads(l) for l in open(os.path.join(out, "INDEX.jsonl"), encoding="utf-8")]
        if idx != [m for _, _, m in sorted(cells, key=lambda c: c[0])]:
            errs.append("%s/INDEX.jsonl differs from this build" % out)
        notes.append("%s/ is this build, byte for byte" % out)
    for n_ in notes:
        print("note " + n_)
    for e in errs[:40]:
        print("FAIL " + e)
    by, sk = counts(cells, skipped)
    print("selfcheck: %d cells (%s), %d skipped, %d combinations + %d seeds; %d pp keys = the table's; %s"
          % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())), len(skipped), space,
             len(cells) - grid, len(g_pp), "every check passes" if not errs else "%d FAILURES" % len(errs)))
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cells15")
    ap.add_argument("--selfcheck", action="store_true",
                    help="check ids, layout, twins, expectations against the table, seeds, denominators and the "
                         "written grid")
    a = ap.parse_args()
    if a.selfcheck:
        sys.exit(selfcheck(a.out))
    cells, skipped = build()
    smap = sums()
    for stem, (sha, setname) in smap.items():
        if hashlib.sha256(SEED_TEXT[stem].encode("utf-8")).hexdigest() != sha:
            sys.exit("seed %s: the embedded text is not its SHA256SUMS line" % stem)
    if any(m["scope"] != "plain" for _, _, m in cells):
        sys.exit("STOP: a cell carries `wild`")
    write_grid(a.out, cells, skipped)
    by, sk = counts(cells, skipped)
    print("generated %d cells (%s), skipped %d" % (len(cells), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                  len(skipped)))


if __name__ == "__main__":
    main()
