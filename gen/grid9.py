#!/usr/bin/env python3
"""M9 — the widened ownership grid (PLAN.md 9.1–9.6).

usage: python3 gen/grid9.py [--out cells9] [--selfcheck]

Writes cells9/<id>/<id>.npk (plus tbl.npk for the import places),
cells9/<id>/meta.json, cells9/INDEX.jsonl (id order) and cells9/SKIPPED.txt
(every combination not emitted, with its reason). The M2 grid (`gen/grid.py`,
`cells/`) is unchanged: its 956 programs and their records stand as measured.

Every cell carries its EXPECTATION, written here before its first run (9.6):
REFUSE with the codes the rule names, or SAFE with the exit code both legs must
give and, for the leak observer, the live bytes the cell's own arithmetic
predicts after `run` returns. The rule text is in the metadata beside it.

Five sections, each a cross product with its skips stated:
  A  the M2 grid's 478 (T, P, O) combinations under the new observers
     (lk, rs; rn at the loop place);
  B  the new TYPES (9.3) in the M2 places under the M2 operations;
  C  the new PLACES (9.4) under the M2 operations;
  D  the new operations on a value (9.5: a partial move, a swap, a
     conditional move, a move in a loop) in the M2 places;
  E  the new control-flow exits with live owners (9.5: break, continue, an
     early pass, relay, a trap to failsafe).

Observers:
  ra  read_after, as M2: after the operation read the ORIGINAL, then exit
      (exit runs no drop).
  dx  drop_at_exit, as M2: the work in `run`, which returns so every drop runs.
  lk  LEAK (9.1): dx, then `main` allocates a 1 MiB probe and exits. Under
      NPK_HEAP_STATS, peak_live - 1048576 is the bytes live after `run`
      returned, exact whenever allocated - 1048576 < 1048576 (the controls in
      PROGRESS.md M9). For OwnedFd the leak is a descriptor: `main` counts the
      descriptors 3..15 still open after `run` and exits 26 if any is.
  rs  REUSE SENTINEL (9.2): ra, but after the operation and before the reads
      `main` allocates a same-sized sentinel (a 46-byte string of 's', a
      one-element List<int64> of 555555, a dyn over a sentinel string, a new
      descriptor). A body freed and still free is taken by the sentinel, so
      the original reads the sentinel (25) instead of the poison.
  rn  READ NOW (9.2, loop places): the original is read inside the loop right
      after the FIRST iteration's operation, before the next one allocates.

Codes: 21 original, 22 new value, 23 vacant, 24 other live value, 25 the
sentinel (freed and reused), 26 a descriptor leaked, 70 the free poison (or a
trap inside failsafe), 111 failsafe's E9 arm (the expected exit of a trap cell).
"""
import argparse, json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid as G  # noqa: E402  the M2 grid: its literals, fail-safe and combination rules

ORIG_LIT, NEW_LIT, FIXED_LIT, POISON = G.ORIG_LIT, G.NEW_LIT, G.FIXED_LIT, G.POISON
SEN_LIT = "s" + "t" * (len(ORIG_LIT) - 1)          # sn() is 46 bytes, as mk() is
PROBE = 1048576

FAILSAFE9 = G.FAILSAFE.replace("        (*) { exit 99i32; }",
                               "        (E9) { exit 111i32; },\n        (*) { exit 99i32; }")
assert FAILSAFE9 != G.FAILSAFE

HELPERS9 = """func:mk = string() never fails {
    pass string_concat("%s", "c");
};
func:nw = string() never fails {
    pass string_concat("%s", "w");
};
func:sn = string() never fails {
    pass string_concat("%s", "u");
};
func:truth = bool(int64:n) never fails {
    pass n > 0i64;
};
func:obs_s = int32(string:v) never fails {
    if (string_byte_length(v) == 0i64) { pass 23i32; }
    uint8[]:bs = string_bytes(v);
    if (bs[0i64] == 97u8) { pass 21i32; }
    if (bs[0i64] == 120u8) { pass 22i32; }
    if (bs[0i64] == 115u8) { pass 25i32; }
    if (bs[0i64] == 170u8) { pass 70i32; }
    pass 24i32;
};
func:mkl = List<int64>(int64:v) never fails {
    List<int64>:l = raw list_init::<int64>(1i64);
    drop list_push::<int64>(@l, v);
    pass l;
};
func:obs_l = int32(List<int64>:v) never fails {
    if (v.count == %s) { pass 70i32; }
    if (v.count == 0i64) { pass 23i32; }
    int64:e = v[0i64];
    if (e == 424242i64) { pass 21i32; }
    if (e == 777777i64) { pass 22i32; }
    if (e == 555555i64) { pass 25i32; }
    if (e == %s) { pass 70i32; }
    pass 24i32;
};
""" % (ORIG_LIT, NEW_LIT, SEN_LIT, POISON, POISON)

NEEDS = {
    "box": "struct:Box = { string:s; };\n",
    "wrap": "struct:Wrap = { List<int64>:l; };\n",
    "nest": "struct:Nest = { Box:v; };\n",
    "lstr": """func:mkls = List<string>() never fails {
    List<string>:l = raw list_init::<string>(1i64);
    drop list_push::<string>(@l, raw mk());
    pass l;
};
func:mklsn = List<string>() never fails {
    List<string>:l = raw list_init::<string>(1i64);
    drop list_push::<string>(@l, raw nw());
    pass l;
};
func:obs_ls = int32(List<string>:v) never fails {
    if (v.count == %s) { pass 70i32; }
    if (v.count == 0i64) { pass 23i32; }
    pass raw obs_s(v[0i64]);
};
""" % POISON,
    "buf": """func:obs_b = int32(buffer:v) never fails {
    if (v.cap == 0i64) { pass 23i32; }
    if (v.len == 46i64) { pass 21i32; }
    if (v.len == 47i64) { pass 22i32; }
    pass 24i32;
};
""",
    # fdt() is written per cell: the first descriptor number a NEW value gets.
    "ofd": """func:mkfd = OwnedFd() {
    cstring:dn = to_cstring("/dev/null") ?! E9;
    fd:f = open(dn, (O_RDONLY => int32) => int64, (S_NONE => int32) => int64) ?! E9;
    pass own_fd(f);
};
func:fd_open = bool(int64:n) never fails {
    Result<int64>:r = sys(72i64, n, 1i64, 0i64);
    pass !(r.is_error);
};
func:obs_fd = int32(OwnedFd:v) never fails {
    int64:n = v.value => int64;
    if (n == -1i64) { pass 23i32; }
    if (!(raw fd_open(n))) { pass 70i32; }
    if (n < (raw fdt())) { pass 21i32; }
    pass 22i32;
};
func:obs_fds = int32(OwnedFd:v, OwnedFd:s) never fails {
    if ((v.value => int64) == (s.value => int64)) { pass 25i32; }
    pass raw obs_fd(v);
};
func:open_fds = int32() never fails {
    int32:n = 0i32;
    for (int64:k in 3i64...16i64) {
        if (raw fd_open(k)) { n = n + 1i32; }
    }
    pass n;
};
""",
    "dyn": """trait:Obs = { func:first = int32(Self:self) never fails; };
struct:DBox = { string:s; };
impl:DBox:Obs = {
    func:first = int32(DBox:self) never fails { pass raw obs_s(self.s); };
};
func:mkd = dyn Obs() never fails {
    DBox:b = DBox{ s: raw mk() };
    dyn Obs:d = move(b);
    pass d;
};
func:mkdn = dyn Obs() never fails {
    DBox:b = DBox{ s: raw nw() };
    dyn Obs:d = move(b);
    pass d;
};
func:mkds = dyn Obs() never fails {
    DBox:b = DBox{ s: raw sn() };
    dyn Obs:d = move(b);
    pass d;
};
func:obs_d = int32(dyn Obs:v) never fails {
    pass raw v.first();
};
""",
}

L = FIXED_LIT
TYPEDEFS = {
    "str": dict(ty="string", init="raw mk()", new="raw nw()", fixed=L, clone="",
                obs="raw obs_s(%s)", sen="s"),
    "box": dict(ty="Box", init="Box{ s: raw mk() }", new="Box{ s: raw nw() }", fixed="Box{ s: %s }" % L,
                sub=(".s", "raw nw()"), clone=".s", part=(".s", "string"), obs="raw obs_s(%s.s)", sen="s",
                needs=("box",)),
    "list": dict(ty="List<int64>", init="raw mkl(424242i64)", new="raw mkl(777777i64)",
                 obs="raw obs_l(%s)", sen="l", grows=True),
    "wrap": dict(ty="Wrap", init="Wrap{ l: raw mkl(424242i64) }", new="Wrap{ l: raw mkl(777777i64) }",
                 sub=(".l", "raw mkl(777777i64)"), part=(".l", "List<int64>"), obs="raw obs_l(%s.l)",
                 sen="l", grows=True, needs=("wrap",)),
    "arr_str": dict(ty="string[2]", init="[raw mk(), raw mk()]", new="[raw nw(), raw nw()]",
                    fixed="[%s, %s]" % (L, L), sub=("[0i64]", "raw nw()"), clone="[0i64]",
                    part=("[0i64]", "string"), obs="raw obs_s(%s[0i64])", sen="s"),
    "arr_box": dict(ty="Box[2]", init="[Box{ s: raw mk() }, Box{ s: raw mk() }]",
                    new="[Box{ s: raw nw() }, Box{ s: raw nw() }]", fixed="[Box{ s: %s }, Box{ s: %s }]" % (L, L),
                    sub=("[0i64]", "Box{ s: raw nw() }"), clone="[0i64].s", part=("[0i64]", "Box"),
                    obs="raw obs_s(%s[0i64].s)", sen="s", needs=("box",)),
    "lstr": dict(ty="List<string>", init="raw mkls()", new="raw mklsn()", sub=("[0i64]", "raw nw()"),
                 clone="[0i64]", part=("[0i64]", "string"), obs="raw obs_ls(%s)", sen="s", grows=True,
                 needs=("lstr",)),
    "nest": dict(ty="Nest", init="Nest{ v: Box{ s: raw mk() } }", new="Nest{ v: Box{ s: raw nw() } }",
                 fixed="Nest{ v: Box{ s: %s } }" % L, sub=(".v.s", "raw nw()"), clone=".v.s",
                 part=(".v.s", "string"), obs="raw obs_s(%s.v.s)", sen="s", needs=("box", "nest")),
    "arr3_str": dict(ty="string[3]", init="[raw mk(), raw mk(), raw mk()]", new="[raw nw(), raw nw(), raw nw()]",
                     fixed="[%s, %s, %s]" % (L, L, L), sub=("[2i64]", "raw nw()"), clone="[2i64]",
                     part=("[2i64]", "string"), obs="raw obs_s(%s[2i64])", sen="s"),
    "arr3_box": dict(ty="Box[3]", init="[Box{ s: raw mk() }, Box{ s: raw mk() }, Box{ s: raw mk() }]",
                     new="[Box{ s: raw nw() }, Box{ s: raw nw() }, Box{ s: raw nw() }]",
                     fixed="[Box{ s: %s }, Box{ s: %s }, Box{ s: %s }]" % (L, L, L),
                     sub=("[2i64]", "Box{ s: raw nw() }"), clone="[2i64].s", part=("[2i64]", "Box"),
                     obs="raw obs_s(%s[2i64].s)", sen="s", needs=("box",)),
    "buf": dict(ty="buffer", init="buffer_new(46i64)", new="buffer_new(47i64)", obs="raw obs_b(%s)", sen=None,
                needs=("buf",)),
    "ofd": dict(ty="OwnedFd", init="mkfd() ?! E9", new="mkfd() ?! E9", obs="raw obs_fd(%s)", sen="f",
                needs=("ofd",)),
    "dyn": dict(ty="dyn Obs", init="raw mkd()", new="raw mkdn()", obs="raw obs_d(%s)", sen="d", needs=("dyn",)),
}
GEN = {"gen_str": "str", "gen_box": "box", "gen_lstr": "lstr", "gen_arr": "arr_str"}

OLD_TYPES = list(G.TYPES)
NEW_TYPES = ["lstr", "nest", "arr3_str", "arr3_box", "gen_lstr", "gen_arr", "buf", "ofd", "dyn"]
OLD_PLACES = list(G.PLACES)
NEW_PLACES = ["for_range", "for_range_list", "for_slice", "for_list", "pick_view", "pick_own",
              "self_recv", "self_lent", "dyn_recv", "claim_m", "claim_i", "temp",
              "res_ok", "res_err", "res_relay"]
OLD_OPS = list(G.OPS)
VALUE_OPS = ["move_part", "swap", "cond_move_t", "cond_move_f", "loop_move", "loop_move_nr"]
FLOW_OPS = ["break_live", "continue_live", "early_pass", "early_pass_out", "relay_live", "relay_temp",
            "trap_live", "trap_live_temp"]
OBS_SHORT = {"read_after": "ra", "drop_at_exit": "dx", "leak": "lk", "reuse_sentinel": "rs", "read_now": "rn"}
LOOP_PLACES = ("for_binding", "for_range", "for_range_list", "for_slice", "for_list")

# which types each new place is crossed with (the reason is the place's own shape)
NEW_PLACE_TYPES = {
    "for_range": ["str", "box", "list", "lstr", "nest", "dyn", "ofd", "buf"],
    "for_range_list": ["str", "box"],
    "for_slice": ["str", "box", "lstr", "nest"],
    "for_list": ["str", "box"],
    "pick_view": ["str", "box", "list", "lstr"],
    "pick_own": ["str", "box", "list", "lstr"],
    "self_recv": ["str", "box", "list", "lstr"],
    "self_lent": ["str", "box", "list", "lstr"],
    "dyn_recv": ["str", "box", "lstr"],
    "claim_m": ["str", "box", "list", "lstr"],
    "claim_i": ["str", "box", "list", "lstr"],
    "temp": ["str", "box", "list", "lstr"],
    "res_ok": ["str", "box", "lstr"],
    "res_err": ["str", "box", "lstr"],
    "res_relay": ["str", "box", "lstr"],
}


class T9:
    def __init__(self, name):
        self.name = name
        self.gen = name in GEN
        base = GEN.get(name, name)
        self.base = base
        d = TYPEDEFS[base]
        self.ty, self.init, self.new = d["ty"], d["init"], d["new"]
        self.fixed_init = d.get("fixed")
        self.sub = d.get("sub")
        self.clone_part = d.get("clone")
        self.part = d.get("part")
        self.obs_fn = d["obs"]
        self.sen = d.get("sen")
        self.grows = d.get("grows", False)
        self.needs = d.get("needs", ())

    def obs(self, e):
        return self.obs_fn % e


class Skip(Exception):
    pass


# ------------------------------------------------------------ the expectation
# Place kinds, each with the rule that governs it (MEMORY_REFERENCE 2.3, TYPE-085):
#   owned   the holder owns the value: local, field, elem, move_param, for_range(_list)
#           (an element reached by index), pick_own (a consuming pick's binding owns,
#           CONTROL 1.2), res_* (a binding initialised through a Result path);
#   ptr     reached through a pointer the caller owns: ptr_param, self_recv (a Self->
#           receiver), claim_m ($$m), dyn_recv (a lent dyn's cell written through its
#           method: the one write a loan admits, MEMORY 2.3 "a LENT dyn's cell is the
#           caller's (the one owning-by-cell kind a loan may write, through its methods)");
#   shared  claim_i: `$$i` admits readers and excludes writers (D-286);
#   loan    lent_param, for_binding, generic_param, for_slice, for_list: a loan is
#           read-only when it owns (TYPE-085), and has no ownership to move (TYPE-047);
#   view    pick_view: a lending pick's binding is a view (D-266): writes TYPE-066,
#           a move or pass TYPE-047;
#   lentrecv self_lent: a pointer-receiver call on a lent owning value (TYPE-085);
#   fixed   read-only storage: moves TYPE-084, the address TYPE-071, a part written
#           TYPE-086, the whole binding re-assigned ASSIGN-002;
#   temp    a temporary: an owning value no place takes, dropped at its statement's
#           end (MEMORY 1.1a, D-246).
def place_kind(p):
    if p in ("local", "field", "elem", "move_param", "for_range", "for_range_list", "pick_own",
             "res_ok", "res_err", "res_relay"):
        return "owned"
    if p in ("ptr_param", "self_recv", "claim_m", "dyn_recv"):
        return "ptr"
    if p == "claim_i":
        return "shared"
    if p in ("lent_param", "for_binding", "generic_param", "for_slice", "for_list"):
        return "loan"
    if p == "pick_view":
        return "view"
    if p == "self_lent":
        return "lentrecv"
    if p == "temp":
        return "temp"
    return "fixed"


WRITES = ("field_write", "assign", "at_overwrite", "at_free", "at_grow")
MOVES = ("move", "pass_out", "move_part", "swap", "cond_move_t", "cond_move_f", "loop_move", "loop_move_nr")
READS_AFTER = ("read_after", "reuse_sentinel", "read_now")


def expectation9(p, o, observer):
    """-> (REFUSE|SAFE, [codes expected on refusal], rule text)."""
    k = place_kind(p)
    ra = observer in READS_AFTER
    if k == "lentrecv":
        return "REFUSE", ["NITPICK-TYPE-085"], "a pointer-receiver call on a lent owning value (TYPE-085, 1.6.0 step 3g)"
    if k == "temp":
        if o == "at_free":
            return "REFUSE", [], "the address of a temporary is refused (the checker's list: 'takes the address of a temporary')"
        return "SAFE", [], "a temporary is taken by the place that keeps it, or dropped at its statement's end (MEMORY 1.1a, D-246)"
    if o == "copy":
        return "REFUSE", ["NITPICK-TYPE-046"], "a copy of an owning value is refused (D-183)"
    if o in ("clone", "read"):
        return "SAFE", [], "a control: clone/read of any place compiles and runs clean"
    if o in MOVES:
        if k in ("loan", "view"):
            return "REFUSE", ["NITPICK-TYPE-047"], "a lent value (a loan or a view) has no ownership to move (D-065, D-266)"
        if k == "fixed":
            return "REFUSE", ["NITPICK-TYPE-084"], "a move out of fixed storage (TYPE-084, 1.6.0 step 3f)"
        if k == "shared":
            return "REFUSE", ["NITPICK-BORROW-013"], "a shared claim excludes writers (D-286)"
        if k == "owned" and o == "loop_move_nr":
            return "REFUSE", ["NITPICK-MOVE-001"], "a move in a loop with no re-initialisation: moved in an earlier trip (D-208)"
        if k == "owned" and ra and o in ("move", "move_part", "cond_move_t", "cond_move_f"):
            return "REFUSE", ["NITPICK-MOVE-001"], "reading the root after a (possible, or partial) move (D-065's whole-binding rule)"
        return "SAFE", [], "a move out of an owner; through a pointer it leaves the vacant value (S-26)"
    # writes
    if k == "loan":
        return "REFUSE", ["NITPICK-TYPE-085"], "a loan is read-only when it owns (1.6.0 step 3g)"
    if k == "view":
        return "REFUSE", ["NITPICK-TYPE-066"], "a view has no address and takes no write (D-266)"
    if k == "shared":
        return "REFUSE", ["NITPICK-BORROW-013"], "a shared claim excludes writers (D-286)"
    if k == "fixed":
        if o.startswith("at_"):
            return "REFUSE", ["NITPICK-TYPE-071"], "a fixed binding has no address (D-287)"
        if o == "assign" and p in ("fixed_scalar",):
            return "REFUSE", ["NITPICK-ASSIGN-002"], "a fixed binding is written once (TYPE_REFERENCE s26)"
        return "REFUSE", ["NITPICK-TYPE-086"], "no part of a fixed binding is written after its declaration (1.6.0 step 4b)"
    return "SAFE", [], "a write to an owned or pointed-to value"


def expected_obs9(p, o):
    """The code an observation of the ORIGINAL should give after o."""
    k = place_kind(p)
    if k in ("loan", "fixed", "view", "shared", "lentrecv"):
        return 21
    if o in ("field_write", "assign", "at_overwrite", "swap", "loop_move"):
        return 22
    if o in ("at_free", "move", "pass_out", "move_part", "cond_move_t", "loop_move_nr"):
        return 23
    return 21


# ------------------------------------------------------------ the builder
class Cell:
    def __init__(self, t, p, o, observer, section):
        self.t, self.p, self.o, self.observer, self.section = T9(t), p, o, observer, section
        self.decls = []
        self.support = None
        self.imports = []
        self.own_box = True
        self.expect_exit = 0
        self.expect_live = 0          # lk: bytes live after run returns
        self.fd_originals = 1         # ofd: how many original descriptors the place opens

    def need(self, name, text):
        tag = "// %s\n" % name
        if not any(d.startswith(tag) for d in self.decls):
            self.decls.append(tag + text)


def callee_decls(c, o, claim=False):
    t, TY = c.t, c.t.ty
    if o == "at_overwrite":
        c.need("at_ow", "func:at_ow = NIL(%s->:p) never fails {\n    (<-p) = %s;\n    pass NIL;\n};\n" % (TY, t.new))
    if o == "at_free":
        c.need("at_fr", "func:at_fr = NIL(%s->:p) never fails {\n    %s:t = move(<-p);\n    pass NIL;\n};\n" % (TY, TY))
    if o == "at_grow":
        if t.base == "list":
            pushes = "".join("    drop list_push::<int64>(p, %di64);\n" % (7 + n) for n in range(8))
        elif t.base == "wrap":
            pushes = "".join("    drop list_push::<int64>(@(<-p).l, %di64);\n" % (7 + n) for n in range(8))
        else:  # lstr
            pushes = "".join("    drop list_push::<string>(p, raw nw());\n" for n in range(8))
        c.need("at_gr", "func:at_gr = NIL(%s->:p) never fails {\n%s    pass NIL;\n};\n" % (TY, pushes))
    if o == "read" and claim:
        c.need("at_rd", "func:at_rd = int32(%s->:p) never fails {\n    pass %s;\n};\n" % (TY, t.obs("(<-p)")))


def op_stmts(c, X, ADDR, claim=None):
    """The statements that perform c.o on the place X (address ADDR)."""
    t, o, TY = c.t, c.o, c.t.ty
    callee_decls(c, o, claim=bool(claim))
    A = ("%s %s" % (claim, X)) if claim else ADDR
    if o == "copy":
        return ["%s:y = %s;" % (TY, X)]
    if o == "move":
        return ["%s:y = move(%s);" % (TY, X)]
    if o == "field_write":
        return ["%s%s = %s;" % (X, t.sub[0], t.sub[1])]
    if o == "assign":
        return ["%s = %s;" % (X, t.new)]
    if o == "at_overwrite":
        return ["drop at_ow(%s);" % A]
    if o == "at_free":
        return ["drop at_fr(%s);" % A]
    if o == "at_grow":
        return ["drop at_gr(%s);" % A]
    if o == "clone":
        return ["string:y = %s%s.clone() ?! HeapOom;" % (X, t.clone_part)]
    if o == "read":
        if claim:
            return ["int32:rd = raw at_rd(%s);" % A]
        return ["int32:rd = %s;" % t.obs(X)]
    if o == "move_part":
        return ["%s:y = move(%s%s);" % (t.part[1], X, t.part[0])]
    if o == "swap":
        return ["%s:other = %s;" % (TY, t.new), "%s:tmp = move(%s);" % (TY, X),
                "%s = move(other);" % X, "other = move(tmp);"]
    if o in ("cond_move_t", "cond_move_f"):
        return ["if (raw truth(%di64)) {\n        %s:y = move(%s);\n    }" % (1 if o == "cond_move_t" else 0, TY, X)]
    if o == "loop_move":
        return ["for (int64:k in 0i64...2i64) {\n        %s:y = move(%s);\n        %s = %s;\n    }" % (TY, X, X, t.new)]
    if o == "loop_move_nr":
        return ["for (int64:k in 0i64...2i64) {\n        %s:y = move(%s);\n    }" % (TY, X)]
    raise AssertionError(o)


def block(lines, n):
    """Indent statements by n spaces. A statement may hold its own newlines; those
    continuation lines are written for a statement at 4 spaces and shift with it."""
    out = []
    for l in lines:
        parts = l.split("\n")
        out.append(" " * n + parts[0])
        for q in parts[1:]:
            out.append(" " * (n - 4) + q)
    return "".join(x + "\n" for x in out)


def sentinel(c):
    """(statements allocating the sentinel, the sentinel's own observation, obs rewriter)."""
    s = c.t.sen
    if s == "s":
        return ["string:sen = raw sn();"], ("raw obs_s(sen)", 25)
    if s == "l":
        return ["List<int64>:sen = raw mkl(555555i64);"], ("raw obs_l(sen)", 25)
    if s == "d":
        return ["dyn Obs:sen = raw mkds();"], ("raw obs_d(sen)", 25)
    if s == "f":
        return ["OwnedFd:sen = mkfd() ?! E9;"], None
    raise AssertionError(s)


# ------------------------------------------------------ non-generic places
def gen_value(c):
    """Sections A-D: a value of type T at place P under operation O.

    Returns (stmts, observations); an observation is (expression, code) where the
    expression is a PLACE to observe with t.obs, or ('@code:v', code) for a code
    the program computed itself."""
    t, p, o = c.t, c.p, c.o
    TY = t.ty
    k = place_kind(p)
    stmts, observations = [], []
    exp_orig = expected_obs9(p, o)
    ob = c.observer
    if o != "pass_out" and p != "temp":
        callee_decls(c, o, claim=p in ("claim_m", "claim_i"))

    # module-level storage
    if p == "fixed_scalar":
        c.decls.append("fixed %s:FX = %s;\n" % (TY, t.fixed_init))
    if p == "fixed_elem":
        c.decls.append("fixed %s[2]:FA = [%s, %s];\n" % (TY, t.fixed_init, t.fixed_init))
    if p.startswith("imported_fixed"):
        v = p.rsplit("_", 1)[1]
        if t.base == "str":
            c.support = "mod:tbl;\npub fixed string[2]:TBL = [%s, %s];\n" % (FIXED_LIT, FIXED_LIT)
        else:
            c.support = ("mod:tbl;\npub struct:Box = { string:s; };\n"
                         "pub fixed Box[2]:TBL = [Box{ s: %s }, Box{ s: %s }];\n" % (FIXED_LIT, FIXED_LIT))
            c.own_box = False
            if v == "typed":
                c.imports.append('use "./tbl.npk".Box;')
            elif v == "same":
                c.decls.insert(0, "struct:Box = { string:s; };\n")
            elif v == "wider":
                c.decls.insert(0, "struct:Box = { string:s; int64:z; };\n")
        c.imports.append('use "./tbl.npk".TBL;')
    if p in ("field", "self_recv", "self_lent"):
        c.decls.append("struct:Hold = { %s:v; };\n" % TY)
    if p in ("pick_view", "pick_own"):
        c.decls.append("enum:Opt = { Non; Som(%s); };\n" % TY)
        c.decls.append("func:obs_e = int32(Opt:e) never fails {\n    int32:r = 24i32;\n"
                       "    pick (e) {\n        (Som(z)) { r = %s; },\n        (*) { r = 23i32; }\n    }\n"
                       "    pass r;\n};\n" % t.obs("z"))
    if p.startswith("res_"):
        c.decls.append("func:mf = %s(bool:ok) {\n    if (ok) { pass %s; }\n    fail E9;\n};\n" % (TY, t.init))
        if p == "res_relay":
            c.decls.append("func:get = %s() {\n    %s:v = relay mf(raw truth(1i64));\n    pass v;\n};\n" % (TY, TY))

    two = "[%s, %s]" % (t.init, t.init)
    place = {
        "local": ("x", "@x", ["%s:x = %s;" % (TY, t.init)]),
        "field": ("h.v", "@h.v", ["Hold:h = Hold{ v: %s };" % t.init]),
        "elem": ("a[i]", "@a[i]", ["%s[2]:a = %s;" % (TY, two), "int64:i = 1i64;"]),
        "fixed_scalar": ("FX", "@FX", []),
        "fixed_elem": ("FA[i]", "@FA[i]", ["int64:i = 1i64;"]),
        "res_ok": ("x", "@x", ["%s:x = mf(raw truth(1i64)) ?| %s;" % (TY, t.new)]),
        "res_err": ("x", "@x", ["%s:x = mf(raw truth(0i64)) ?| %s;" % (TY, t.init)]),
        "res_relay": ("x", "@x", ["%s:x = get() ?! E9;" % TY]),
    }
    if p.startswith("imported_fixed"):
        place[p] = ("TBL[i]", "@TBL[i]", ["int64:i = 1i64;"])
    if p in ("elem",):
        c.fd_originals = 2

    # ---- pass_out: the holder is a function that passes the value out
    if o == "pass_out":
        if p in place:
            X, ADDR, setup = place[p]
            body = "".join("    %s\n" % s for s in setup)
            fails = "" if p.startswith("res_") else " never fails"
            c.decls.append("func:hold = %s()%s {\n%s    pass %s;\n};\n" % (TY, fails, body, X))
            call = ("hold() ?! E9" if p.startswith("res_") else "raw hold()")
            stmts.append("%s:r = %s;" % (TY, call))
            observations.append(("r", 21))
            if k == "fixed":
                if p == "fixed_scalar":
                    observations.append(("FX", 21))
                else:
                    stmts.append("int64:j = 1i64;")
                    observations.append((X.replace("[i]", "[j]"), 21))
        elif p == "lent_param":
            c.decls.append("func:hold = %s(%s:x) never fails {\n    pass x;\n};\n" % (TY, TY))
            stmts += ["%s:orig = %s;" % (TY, t.init), "%s:r = raw hold(orig);" % TY]
            observations += [("r", 21), ("orig", 21)]
        elif p == "move_param":
            c.decls.append("func:hold = %s(move %s:x) never fails {\n    pass x;\n};\n" % (TY, TY))
            stmts += ["%s:orig = %s;" % (TY, t.init), "%s:r = raw hold(move(orig));" % TY]
            observations += [("r", 21)]
        elif p == "ptr_param":
            c.decls.append("func:hold = %s(%s->:x) never fails {\n    pass (<-x);\n};\n" % (TY, TY))
            stmts += ["%s:orig = %s;" % (TY, t.init), "%s:r = raw hold(@orig);" % TY]
            observations += [("r", 21), ("orig", 23)]
        elif p == "for_binding":
            c.decls.append("func:hold = %s() never fails {\n    %s[2]:arr = %s;\n"
                           "    for (%s:x in arr) {\n        pass x;\n    }\n    pass %s;\n};\n"
                           % (TY, TY, two, TY, t.init))
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        elif p == "for_range":
            c.decls.append("func:hold = %s() never fails {\n    %s[2]:arr = %s;\n"
                           "    for (int64:i in 0i64...2i64) {\n        pass arr[i];\n    }\n    pass %s;\n};\n"
                           % (TY, TY, two, t.init))
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        elif p == "for_range_list":
            c.decls.append("func:hold = %s() never fails {\n    List<%s>:arr = raw list_init::<%s>(2i64);\n"
                           "    drop list_push::<%s>(@arr, %s);\n    drop list_push::<%s>(@arr, %s);\n"
                           "    for (int64:i in 0i64...2i64) {\n        pass arr[i];\n    }\n    pass %s;\n};\n"
                           % (TY, TY, TY, TY, t.init, TY, t.init, t.init))
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        elif p in ("for_slice", "for_list"):
            c.decls.append("func:hold = %s(%s[]:s) never fails {\n    for (%s:x in s) {\n        pass x;\n    }\n"
                           "    pass %s;\n};\n" % (TY, TY, TY, t.init))
            if p == "for_slice":
                stmts += ["%s[2]:arr = %s;" % (TY, two), "%s:r = raw hold(arr[0i64...2i64]);" % TY]
            else:
                stmts += ["List<%s>:arr = raw list_init::<%s>(2i64);" % (TY, TY),
                          "drop list_push::<%s>(@arr, %s);" % (TY, t.init),
                          "drop list_push::<%s>(@arr, %s);" % (TY, t.init),
                          "%s:r = raw hold(arr[0i64...2i64]);" % TY]
            observations += [("r", 21), ("arr[0i64]", 21)]
        elif p in ("pick_view", "pick_own"):
            sel = "e" if p == "pick_view" else "move(e)"
            c.decls.append("func:hold = %s() never fails {\n    Opt:e = Opt.Som(%s);\n    pick (%s) {\n"
                           "        (Som(x)) { pass x; },\n        (*) { }\n    }\n    pass %s;\n};\n"
                           % (TY, t.init, sel, t.init))
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        elif p in ("self_recv", "self_lent"):
            c.decls.append("impl:Hold = {\n    func:op = %s(Hold->:self) never fails { pass self.v; };\n};\n" % TY)
            if p == "self_recv":
                stmts += ["Hold:h = Hold{ v: %s };" % t.init, "%s:r = raw h.op();" % TY]
                observations += [("r", 21), ("h.v", 23)]
            else:
                c.decls.append("func:callit = %s(Hold:h) never fails {\n    pass raw h.op();\n};\n" % TY)
                stmts += ["Hold:h = Hold{ v: %s };" % t.init, "%s:r = raw callit(h);" % TY]
                observations += [("r", 21), ("h.v", 21)]
        elif p == "dyn_recv":
            dyn_recv_decls(c, ["pass self.v;"], TY)
            c.decls.append("func:callit = %s(dyn Tr:d) never fails {\n    pass raw d.op();\n};\n" % TY)
            stmts += ["DHold:b = DHold{ v: %s };" % t.init, "dyn Tr:d = move(b);", "%s:r = raw callit(d);" % TY]
            observations += [("r", 21), ("@peek", 23)]
        elif p == "temp":
            c.decls.append("func:mkt = %s() never fails {\n    pass %s;\n};\n" % (TY, t.init))
            c.decls.append("func:hold = %s() never fails {\n    pass raw mkt();\n};\n" % TY)
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        else:
            raise AssertionError(p)
        return stmts, observations

    # ---- the place's own shape
    if p in place:
        X, ADDR, setup = place[p]
        stmts += setup + op_stmts(c, X, ADDR)
        observations.append((X, exp_orig))
        if o == "swap" and p in ("local", "field", "elem", "res_ok", "res_err", "res_relay"):
            observations.append(("other", 21))
    elif p == "lent_param":
        body = block(op_stmts(c, "x", "@x"), 4)
        c.decls.append("func:op = NIL(%s:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
        stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(orig);"]
        observations.append(("orig", exp_orig))
    elif p == "ptr_param":
        body = block(op_stmts(c, "(<-x)", "x"), 4)
        c.decls.append("func:op = NIL(%s->:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
        stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(@orig);"]
        observations.append(("orig", exp_orig))
    elif p == "move_param":
        body = block(op_stmts(c, "x", "@x"), 4)
        if ob in READS_AFTER:
            if ob == "reuse_sentinel":
                sst, _ = sentinel(c)
                body += block(sst, 4)
                obs_x = ("raw obs_fds(x, sen)" if c.t.sen == "f" else t.obs("x"))
            else:
                obs_x = t.obs("x")
            c.decls.append("func:op = int32(move %s:x) never fails {\n%s    pass %s;\n};\n" % (TY, body, obs_x))
            stmts += ["%s:orig = %s;" % (TY, t.init), "int32:o0 = raw op(move(orig));"]
            observations.append(("@code:o0", exp_orig))
            c.sentinel_done = True
        else:
            c.decls.append("func:op = NIL(move %s:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
            stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(move(orig));"]
    elif p == "for_binding":
        c.fd_originals = 2
        inner = op_stmts(c, "x", "@x")
        stmts += ["%s[2]:arr = %s;" % (TY, two)] + loop_with_rn(c, "for (%s:x in arr)" % TY, inner, "arr[0i64]")
        observations.append(("@code:rn1", exp_orig) if ob == "read_now" else ("arr[0i64]", exp_orig))
    elif p in ("for_range", "for_range_list"):
        c.fd_originals = 2
        inner = op_stmts(c, "arr[i]", "@arr[i]")
        if p == "for_range":
            stmts.append("%s[2]:arr = %s;" % (TY, two))
        else:
            stmts += ["List<%s>:arr = raw list_init::<%s>(2i64);" % (TY, TY),
                      "drop list_push::<%s>(@arr, %s);" % (TY, t.init),
                      "drop list_push::<%s>(@arr, %s);" % (TY, t.init)]
        stmts += loop_with_rn(c, "for (int64:i in 0i64...2i64)", inner, "arr[0i64]")
        observations.append(("@code:rn1", exp_orig) if ob == "read_now" else ("arr[0i64]", exp_orig))
    elif p in ("for_slice", "for_list"):
        c.fd_originals = 2
        inner = op_stmts(c, "x", "@x")
        if ob == "read_now":
            loop = ("    int64:it = 0i64;\n    int32:r = 0i32;\n    for (%s:x in s) {\n%s"
                    "        if (it == 0i64) { r = %s; }\n        it = it + 1i64;\n    }\n    pass r;\n"
                    % (TY, block(inner, 8), t.obs("s[0i64]")))
            c.decls.append("func:op = int32(%s[]:s) never fails {\n%s};\n" % (TY, loop))
            call = "int32:o0 = raw op(arr[0i64...2i64]);"
        else:
            c.decls.append("func:op = NIL(%s[]:s) never fails {\n    for (%s:x in s) {\n%s    }\n    pass NIL;\n};\n"
                           % (TY, TY, block(inner, 8)))
            call = "drop op(arr[0i64...2i64]);"
        if p == "for_slice":
            stmts += ["%s[2]:arr = %s;" % (TY, two), call]
        else:
            stmts += ["List<%s>:arr = raw list_init::<%s>(2i64);" % (TY, TY),
                      "drop list_push::<%s>(@arr, %s);" % (TY, t.init),
                      "drop list_push::<%s>(@arr, %s);" % (TY, t.init), call]
        if ob == "read_now":
            observations.append(("@code:o0", exp_orig))
        else:
            observations.append(("arr[0i64]", exp_orig))
    elif p == "pick_view":
        inner = op_stmts(c, "x", "@x")
        stmts += ["Opt:e = Opt.Som(%s);" % t.init,
                  "pick (e) {\n        (Som(x)) {\n%s        },\n        (*) { }\n    }" % block(inner, 12)]
        observations.append(("@obs_e", exp_orig))
    elif p == "pick_own":
        inner = op_stmts(c, "x", "@x")
        if ob in READS_AFTER:
            # the binding lives inside the arm, so the arm observes it and exits
            c.arm_observe = True
            stmts += ["Opt:e = Opt.Som(%s);" % t.init, ("@ARM", inner)]
            observations.append(("x", exp_orig))
        else:
            stmts += ["Opt:e = Opt.Som(%s);" % t.init,
                      "pick (move(e)) {\n        (Som(x)) {\n%s        },\n        (*) { }\n    }" % block(inner, 12)]
    elif p in ("self_recv", "self_lent"):
        body = op_stmts(c, "self.v", "@self.v")
        c.decls.append("impl:Hold = {\n    func:op = NIL(Hold->:self) never fails {\n%s        pass NIL;\n    };\n};\n"
                       % block(body, 8))
        if p == "self_recv":
            stmts += ["Hold:h = Hold{ v: %s };" % t.init, "drop h.op();"]
        else:
            c.decls.append("func:callit = NIL(Hold:h) never fails {\n    drop h.op();\n    pass NIL;\n};\n")
            stmts += ["Hold:h = Hold{ v: %s };" % t.init, "drop callit(h);"]
        observations.append(("h.v", exp_orig))
    elif p == "dyn_recv":
        dyn_recv_decls(c, op_stmts(c, "self.v", "@self.v") + ["pass NIL;"], "NIL")
        c.decls.append("func:callit = NIL(dyn Tr:d) never fails {\n    drop d.op();\n    pass NIL;\n};\n")
        stmts += ["DHold:b = DHold{ v: %s };" % t.init, "dyn Tr:d = move(b);", "drop callit(d);"]
        observations.append(("@peek", exp_orig))
    elif p in ("claim_m", "claim_i"):
        claim = "$$m" if p == "claim_m" else "$$i"
        stmts += ["%s:x = %s;" % (TY, t.init)] + op_stmts(c, "x", "@x", claim=claim)
        observations.append(("x", exp_orig))
    elif p == "temp":
        c.decls.append("func:mkt = %s() never fails {\n    pass %s;\n};\n" % (TY, t.init))
        if o == "read":
            c.decls.append("func:lend = int32(%s:v) never fails {\n    pass %s;\n};\n" % (TY, t.obs("v")))
            stmts.append("int32:rd = raw lend(raw mkt());")
            observations.append(("@code:rd", 21))
        elif o == "move":
            c.decls.append("func:take = int32(move %s:v) never fails {\n    pass %s;\n};\n" % (TY, t.obs("v")))
            stmts.append("int32:tk = raw take(raw mkt());")
            observations.append(("@code:tk", 21))
        elif o == "at_free":
            callee_decls(c, "at_free")
            stmts.append("drop at_fr(@(raw mkt()));")
        else:
            raise AssertionError(o)
    else:
        raise AssertionError(p)
    return stmts, observations


def loop_with_rn(c, head, inner, target):
    """A loop over `inner`; under read_now the original is read after the first trip."""
    if c.observer != "read_now":
        return ["%s {\n%s    }" % (head, block(inner, 8))]
    c.rn_var = True
    return ["int64:it = 0i64;", "int32:rn1 = 0i32;",
            "%s {\n%s        if (it == 0i64) { rn1 = %s; }\n        it = it + 1i64;\n    }"
            % (head, block(inner, 8), c.t.obs(target))]


def dyn_recv_decls(c, body, ret):
    t, TY = c.t, c.t.ty
    c.decls.append("trait:Tr = { func:peek = int32(Self:self) never fails; func:op = %s(Self->:self) never fails; };\n" % ret)
    c.decls.append("struct:DHold = { %s:v; };\n" % TY)
    c.decls.append("impl:DHold:Tr = {\n    func:peek = int32(DHold:self) never fails { pass %s; };\n"
                   "    func:op = %s(DHold->:self) never fails {\n%s    };\n};\n"
                   % (t.obs("self.v"), ret, block(body, 8)))


# --------------------------------------------------------- generic places
def gen_generic9(c):
    """As grid.py's gen_generic, at the new instantiations too (List<string>, string[2])."""
    t, p, o = c.t, c.p, c.o
    TY = t.ty
    stmts, observations = [], []
    exp_orig = expected_obs9(p, o)
    bound = "T: Clone" if o == "clone" else "T"
    params = {"generic_param": "T:x", "move_param": "move T:x", "ptr_param": "T->:x",
              "local": "move T:seed"}[p]
    X = "(<-x)" if p == "ptr_param" else "x"
    ADDR = "x" if p == "ptr_param" else "@x"
    fresh = o in ("assign", "at_overwrite")
    if fresh:
        params += ", move T:fresh"
    body = []
    if p == "local":
        body.append("T:x = move(seed);")
    if o == "copy":
        body.append("T:y = %s;" % X)
    elif o == "move":
        body.append("T:y = move(%s);" % X)
    elif o == "pass_out":
        body.append("pass %s;" % X)
    elif o == "assign":
        body.append("%s = move(fresh);" % X)
    elif o == "at_overwrite":
        c.decls.append("func:g_ow<T> = NIL(T->:p, move T:f) never fails {\n    (<-p) = move(f);\n    pass NIL;\n};\n")
        body.append("drop g_ow::<T>(%s, move(fresh));" % ADDR)
    elif o == "at_free":
        c.decls.append("func:g_fr<T> = NIL(T->:p) never fails {\n    T:t = move(<-p);\n    pass NIL;\n};\n")
        body.append("drop g_fr::<T>(%s);" % ADDR)
    elif o == "clone":
        body.append("T:y = %s.clone() ?! HeapOom;" % X)
    elif o == "read":
        c.decls.append("func:g_lend<T> = NIL(T:v) never fails {\n    pass NIL;\n};\n")
        body.append("drop g_lend::<T>(%s);" % X)
    owner_inside = p in ("move_param", "local")
    ob = c.observer
    reads = ob in READS_AFTER
    if o == "pass_out":
        ret = "T"
    elif owner_inside and reads:
        ret = "T"
        body.append("pass x;")
    else:
        ret = "NIL"
        body.append("pass NIL;")
    c.decls.append("func:op<%s> = %s(%s) never fails {\n%s};\n"
                   % (bound, ret, params, "".join("    %s\n" % s for s in body)))
    args = []
    if p == "local":
        args.append(t.init)
    else:
        stmts.append("%s:orig = %s;" % (TY, t.init))
        args.append({"generic_param": "orig", "move_param": "move(orig)", "ptr_param": "@orig"}[p])
    if fresh:
        args.append(t.new)
    call = "op::<%s>(%s)" % (TY, ", ".join(args))
    if ret == "T":
        stmts.append("%s:r = raw %s;" % (TY, call))
        if reads:
            if o == "pass_out":
                observations.append(("r", 21))
            else:
                observations.append(("r", exp_orig if not owner_inside else
                                     (22 if o in ("assign", "at_overwrite") else
                                      23 if o in ("at_free", "move") else 21)))
            if p in ("generic_param", "ptr_param"):
                observations.append(("orig", 23 if (p == "ptr_param" and o == "pass_out") else 21))
    else:
        stmts.append("drop %s;" % call)
        if reads and p in ("generic_param", "ptr_param"):
            observations.append(("orig", exp_orig))
    return stmts, observations


# ------------------------------------------------------- control-flow exits
def gen_flow(c):
    """Section E: owners live at a break, a continue, an early pass, a relay or a trap.

    The holder place is local (one owner), field (a struct holding it) or elem (an
    array of two). Every owner is created inside the construct that exits, so the
    exit is the owner's scope end: each must be dropped exactly once there."""
    t, p, o, TY = c.t, c.p, c.o, c.t.ty
    if p == "field":
        c.decls.append("struct:Hold = { %s:v; };\n" % TY)
    if p == "elem":
        c.fd_originals = 2
    mk_owner = {"local": ["%s:x = %s;" % (TY, t.init)],
                "field": ["Hold:h = Hold{ v: %s };" % t.init],
                "elem": ["%s[2]:a = [%s, %s];" % (TY, t.init, t.init)]}[p]
    owner_expr = {"local": "x", "field": "h.v", "elem": "a[1i64]"}[p]
    c.decls.append("func:mfi = int32(bool:ok) {\n    if (ok) { pass 0i32; }\n    fail E9;\n};\n")
    stmts = []
    if o in ("break_live", "continue_live"):
        cond = "k == 1i64" if o == "break_live" else "k == 0i64"
        kw = "break" if o == "break_live" else "continue"
        stmts += ["int32:n = 0i32;",
                  "for (int64:k in 0i64...3i64) {\n%s        if (%s) { %s; }\n        n = n + 1i32;\n    }"
                  % (block(mk_owner, 8), cond, kw),
                  "if (n != %di32) { pass 20i32; }" % (1 if o == "break_live" else 2)]
    elif o == "early_pass":
        c.decls.append("func:ep = int32(bool:c) never fails {\n%s    if (c) { pass 0i32; }\n    pass 20i32;\n};\n"
                       % block(mk_owner, 4))
        stmts += ["int32:v = raw ep(raw truth(1i64));", "if (v != 0i32) { pass v; }"]
    elif o == "early_pass_out":
        c.decls.append("func:ep = %s(bool:c) never fails {\n%s    %s:w = %s;\n    if (c) { pass %s; }\n    pass w;\n};\n"
                       % (TY, block(mk_owner, 4), TY, t.new, owner_expr))
        stmts += ["%s:r = raw ep(raw truth(1i64));" % TY, "int32:v = %s;" % t.obs("r"),
                  "if (v != 21i32) { pass v; }"]
    elif o in ("relay_live", "relay_temp"):
        if o == "relay_live":
            c.decls.append("func:rl = int32(bool:ok) {\n%s    int32:v = relay mfi(ok);\n    pass v;\n};\n"
                           % block(mk_owner, 4))
        else:
            c.decls.append("func:mkt = %s() never fails {\n    pass %s;\n};\n" % (TY, t.init))
            c.decls.append("func:lend = int32(%s:v) never fails {\n    pass %s;\n};\n" % (TY, t.obs("v")))
            c.decls.append("func:rl = int32(bool:ok) {\n    int32:v = (raw lend(raw mkt())) + (relay mfi(ok));\n"
                           "    pass v;\n};\n")
        stmts += ["int32:v = rl(raw truth(0i64)) ?| 0i32;", "if (v != 0i32) { pass 20i32; }"]
    elif o in ("trap_live", "trap_live_temp"):
        c.expect_exit = 111
        if o == "trap_live":
            stmts += mk_owner + ["int32:v = mfi(raw truth(0i64)) ?! E9;", "if (v != 0i32) { pass 20i32; }"]
        else:
            c.decls.append("func:mkt = %s() never fails {\n    pass %s;\n};\n" % (TY, t.init))
            c.decls.append("func:lend = int32(%s:v) never fails {\n    pass %s;\n};\n" % (TY, t.obs("v")))
            stmts += ["int32:v = (raw lend(raw mkt())) + (mfi(raw truth(0i64)) ?! E9);",
                      "if (v != 21i32) { pass 20i32; }"]
    else:
        raise AssertionError(o)
    return stmts, []


# ------------------------------------------------------------ rendering
def render9(c, cid):
    t = c.t
    c.sentinel_done = False
    c.arm_observe = False
    c.rn_var = False
    if c.section == "E":
        stmts, observations = gen_flow(c)
    elif t.gen:
        stmts, observations = gen_generic9(c)
    else:
        stmts, observations = gen_value(c)
    ob = c.observer
    head = ["mod:%s;" % cid, "error:E9;"] + c.imports
    needs = set(t.needs)
    if not c.own_box:
        needs.discard("box")
    structs = "".join(NEEDS[n] for n in ("box", "wrap", "nest") if n in needs)
    helpers = "".join(NEEDS[n] for n in ("lstr", "buf", "ofd", "dyn") if n in needs)
    if "ofd" in needs:
        helpers += "func:fdt = int64() never fails {\n    pass %di64;\n};\n" % (3 + c.fd_originals)
    decls = "".join(d.split("\n", 1)[1] if d.startswith("// ") else d for d in c.decls)
    src = "\n".join(head) + "\n" + structs + HELPERS9 + helpers + decls

    def obs_expr(e):
        if e == "@obs_e":
            return "raw obs_e(e)"
        if e == "@peek":
            return "raw d.peek()"
        if ob == "reuse_sentinel" and t.sen == "f" and not e.startswith("@"):
            return "raw obs_fds(%s, sen)" % e
        return t.obs(e)

    if ob in READS_AFTER:
        checks, pre = [], []
        if ob == "reuse_sentinel" and not c.sentinel_done:
            sst, sobs = sentinel(c)
            pre = sst
            if sobs is not None:
                observations = observations + [("@sen", 25)]
        n = 0
        for e, exp in observations:
            n += 1
            if e.startswith("@code:"):
                v = e[6:]
            else:
                v = "o%d" % n
                expr = sentinel(c)[1][0] if e == "@sen" else obs_expr(e)
                checks.append("int32:%s = %s;" % (v, expr))
            checks.append("if (%s != %di32) { exit %s; }" % (v, exp, v))
        if c.arm_observe:
            # pick_own: the operation, the sentinel and the reads all inside the arm
            arm_inner = None
            out = []
            for s in stmts:
                if isinstance(s, tuple) and s[0] == "@ARM":
                    arm_inner = s[1]
                else:
                    out.append(s)
            arm = ("pick (move(e)) {\n        (Som(x)) {\n%s        },\n        (*) { exit 24i32; }\n    }"
                   % block(arm_inner + pre + checks, 12))
            body = block(out + [arm], 4)
        else:
            body = block(stmts + pre + checks, 4)
        src += "func:main = int32(cstring[]:_~argv) {\n%s    exit 0i32;\n};\n" % body
        meta_obs = observations
    else:
        tail = []
        if ob == "leak":
            if t.base == "ofd":
                tail.append("if ((raw open_fds()) != 0i32) { exit 26i32; }")
            tail.append("buffer:probe = buffer_new(%di64);" % PROBE)
        src += ("func:run = int32() never fails {\n%s    pass 0i32;\n};\n"
                "func:main = int32(cstring[]:_~argv) {\n    int32:r = raw run();\n%s    exit r;\n};\n"
                % (block(stmts, 4), block(tail, 4)))
        meta_obs = []
    src += FAILSAFE9
    return src, meta_obs


# -------------------------------------------------------------- the space
def check_value(t, p, o, section):
    """Raise Skip with the reason when (t, p, o) means nothing; sections B-D."""
    gen = t.gen
    k = place_kind(p)
    if p in NEW_PLACES:
        if t.name not in NEW_PLACE_TYPES[p]:
            raise Skip("%s is crossed with %s only" % (p, ", ".join(NEW_PLACE_TYPES[p])))
    if gen and p not in ("generic_param", "move_param", "ptr_param", "local"):
        raise Skip("a generic T is reached only through a generic body's parameter or local")
    if not gen and p == "generic_param":
        raise Skip("generic_param is the place of a generic T only")
    if gen and o in ("field_write",) + tuple(VALUE_OPS):
        raise Skip("a generic T has no fields a body may name, and its value operations are the M2 grid's")
    if o == "field_write" and t.sub is None:
        raise Skip("%s has no owning sub-place to write" % t.ty)
    if o == "at_grow" and not t.grows:
        raise Skip("at_grow grows a List; %s does not grow" % t.ty)
    if o == "at_grow" and gen:
        raise Skip("a generic body cannot grow an opaque T: a push is List's, and T names no List")
    if o == "loop_move" and t.base == "ofd":
        raise Skip("a descriptor number is reused across the loop's trips, so the observer's number cannot tell "
                   "the new descriptor from the original")
    if o == "move_part" and t.part is None:
        raise Skip("%s has no owning part to move out" % t.ty)
    if o == "clone":
        if gen and t.base != "str":
            raise Skip("only string among the generic instantiations has a Clone impl")
        if t.clone_part is None:
            raise Skip("%s holds no owning string to clone, and has no clone method" % t.ty)
    if p == "fixed_scalar" and t.fixed_init is None:
        raise Skip("%s has no compile-time constant, so it cannot be fixed" % t.ty)
    if p == "fixed_elem" and t.base not in ("str", "box", "nest"):
        raise Skip("fixed_elem is an element of a fixed array of str, box or nest")
    if p in ("elem", "for_binding", "for_range") and t.base.startswith("arr"):
        raise Skip("an array of arrays is outside the grid")
    if p.startswith("imported_fixed"):
        if t.base not in ("str", "box") or t.name != t.base:
            raise Skip("imported tables hold str or box rows")
        v = p.rsplit("_", 1)[1]
        if t.base == "str" and v != "typed":
            raise Skip("a string row has no row type to import, omit or shadow; only imported_fixed_typed applies")
        if v == "bare" and o not in ("field_write", "clone", "read"):
            raise Skip("without its row type the importer cannot name Box, which %s needs" % o)
        if v != "typed" and section == "D":
            raise Skip("the value operations cross the import places at imported_fixed_typed only")
    if o == "field_write" and t.base == "str" and p.startswith("imported"):
        raise Skip("string has no owning sub-place to write")
    if p in ("claim_m", "claim_i") and o not in ("at_overwrite", "at_free", "at_grow", "read"):
        raise Skip("a claim is handed to a callee: the at_* operations and a read through it")
    if p == "temp" and o not in ("read", "move", "pass_out", "at_free"):
        raise Skip("a temporary is not a place: it is read, taken by a move parameter, passed out, or its address asked")
    if p in ("for_slice", "for_list", "pick_view", "self_lent") and o in VALUE_OPS[2:]:
        raise Skip("the conditional and loop moves are crossed with the owning places")
    if p == "dyn_recv" and o in VALUE_OPS[2:]:
        raise Skip("the conditional and loop moves are crossed with the owning places")
    if p in ("for_range", "for_range_list") and o in ("loop_move", "loop_move_nr"):
        raise Skip("a loop move inside a loop place is a nested loop, outside the grid")
    if t.base == "ofd" and o in ("clone",):
        raise Skip("OwnedFd has no clone")
    if t.base == "dyn" and (p in ("elem", "for_binding", "for_range", "ptr_param") or o.startswith("at_")):
        raise Skip("an array of, or a pointer to, a dyn has no spelling: `dyn T[2]` parses as `dyn (T[2])` "
                   "and `dyn T->` as `dyn (T->)` (TYPE-006; the compiler's own dyn_array test says so)")


def check_observer(t, p, o, ob):
    """Raise Skip when an observer cannot observe this cell."""
    if ob == "reuse_sentinel" and t.sen is None:
        raise Skip("a buffer's body is zeroed and read only through pointer indexing, so a sentinel cannot be told from it")
    if ob in READS_AFTER and t.base == "dyn" and expected_obs9(p, o) == 23:
        raise Skip("a vacant dyn has no receiver to observe through")
    if ob == "read_now" and p not in LOOP_PLACES:
        raise Skip("read_now is the loop places' observer")
    if ob == "read_now" and o == "pass_out":
        raise Skip("a pass_out's holder returns in its first trip; there is no later allocation to read before")


def emit(out, cid, c, src, meta):
    d = os.path.join(out, cid)
    os.makedirs(d)
    with open(os.path.join(d, cid + ".npk"), "w") as fh:
        fh.write(src)
    if c.support:
        with open(os.path.join(d, "tbl.npk"), "w") as fh:
            fh.write(c.support)
    with open(os.path.join(d, "meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)


def enumerate_cells():
    """Yield (section, t, p, o, observer) in a fixed order; Skip reasons are collected by the caller."""
    # A: the M2 combinations, new observers
    for tn in G.TYPES:
        for p in G.PLACES:
            for o in G.OPS:
                c0 = G.Cell(tn, p, o, "read_after")
                try:
                    G.check_combination(c0)
                except G.Skip:
                    continue
                for ob in ("leak", "reuse_sentinel", "read_now"):
                    yield "A", tn, p, o, ob
    # B: the new types in the M2 places, M2 operations
    for tn in NEW_TYPES:
        for p in G.PLACES:
            for o in G.OPS:
                for ob in ("read_after", "drop_at_exit", "leak", "reuse_sentinel", "read_now"):
                    yield "B", tn, p, o, ob
    # C: the new places, M2 operations (and the partial move and swap)
    for p in NEW_PLACES:
        for tn in OLD_TYPES + NEW_TYPES:
            for o in G.OPS + ["move_part", "swap"]:
                for ob in ("read_after", "drop_at_exit", "leak", "reuse_sentinel", "read_now"):
                    yield "C", tn, p, o, ob
    # D: the value operations in the M2 places (and the loop places C does not take)
    for o in VALUE_OPS:
        for tn in OLD_TYPES + NEW_TYPES:
            for p in G.PLACES:
                for ob in ("read_after", "drop_at_exit", "leak", "reuse_sentinel", "read_now"):
                    yield "D", tn, p, o, ob
        for p in NEW_PLACES:
            if o in ("move_part", "swap"):
                continue      # C carries them
            for tn in OLD_TYPES + NEW_TYPES:
                for ob in ("read_after", "drop_at_exit", "leak", "reuse_sentinel", "read_now"):
                    yield "D", tn, p, o, ob
    # E: control-flow exits with live owners
    for o in FLOW_OPS:
        for tn in OLD_TYPES + NEW_TYPES:
            for p in ("local", "field", "elem"):
                for ob in ("drop_at_exit", "leak"):
                    yield "E", tn, p, o, ob


def check_flow(t, p, o, ob):
    if t.gen:
        raise Skip("a generic T's exits are the concrete types' exits")
    if p == "elem" and t.base.startswith("arr"):
        raise Skip("an array of arrays is outside the grid")
    if p == "elem" and t.base == "dyn":
        raise Skip("an array of a dyn has no spelling: `dyn T[2]` parses as `dyn (T[2])` (TYPE-006)")
    if o in ("relay_temp", "trap_live_temp") and p != "local":
        raise Skip("a temporary's exit has no holder place: crossed once, at local")
    if o in ("trap_live", "trap_live_temp") and ob == "leak":
        raise Skip("no drop runs on a trap (D-014) and failsafe's region is not counted, so no probe can follow it")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cells9")
    ap.add_argument("--selfcheck", action="store_true",
                    help="also render the M2 grid's ra/dx cells with this generator and compare with grid.py")
    a = ap.parse_args()
    if a.selfcheck:
        sys.exit(selfcheck())
    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    os.makedirs(a.out)
    index, skipped = [], []
    n = 0
    seen = set()
    for section, tn, p, o, ob in enumerate_cells():
        key = (tn, p, o, ob)
        if key in seen:
            continue
        seen.add(key)
        c = Cell(tn, p, o, ob, section)
        try:
            if section == "E":
                check_flow(c.t, p, o, ob)
            else:
                if section != "A":
                    check_value(c.t, p, o, section)
                check_observer(c.t, p, o, ob)
        except Skip as e:
            skipped.append((section, tn, p, o, ob, str(e)))
            continue
        n += 1
        cid = "m%04d_%s_%s_%s_%s" % (n, tn, p, o, OBS_SHORT[ob])
        src, observations = render9(c, cid)
        if section == "E":
            exp, codes, rule = "SAFE", [], "an owner live at an exit is dropped exactly once there (MEMORY 1.1, D-246)"
            if o.startswith("trap"):
                rule = "a trap runs no drop and no defer (D-014); failsafe's E9 arm exits 111"
        else:
            exp, codes, rule = expectation9(p, o, ob)
        meta = {"id": cid, "section": section, "T": tn, "P": p, "O": o, "observer": ob,
                "expect": exp, "expect_codes": codes, "rule": rule,
                "expect_exit": c.expect_exit,
                "expect_live": (None if (ob != "leak" or c.t.base == "ofd") else c.expect_live),
                "heap": ob == "leak",
                "observations": [{"of": e, "expect": x} for e, x in observations]}
        emit(a.out, cid, c, src, meta)
        index.append(meta)
    with open(os.path.join(a.out, "INDEX.jsonl"), "w") as fh:
        for m in index:
            fh.write(json.dumps(m) + "\n")
    with open(os.path.join(a.out, "SKIPPED.txt"), "w") as fh:
        fh.write("# section T P O observer -- reason (%d combinations not emitted)\n" % len(skipped))
        for s in skipped:
            fh.write("%s %s %s %s %s -- %s\n" % s)
    by = {}
    for m in index:
        by[m["section"]] = by.get(m["section"], 0) + 1
    print("generated %d cells (%s), skipped %d" % (len(index), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                                   len(skipped)))


def selfcheck():
    """Render the M2 combinations' ra/dx programs with grid9's builder, the M2 helpers
    and fail-safe restored, and compare them with grid.py's text byte for byte."""
    bad = total = 0
    for tn in G.TYPES:
        for p in G.PLACES:
            for o in G.OPS:
                for ob in G.OBSERVERS:
                    c0 = G.Cell(tn, p, o, ob)
                    try:
                        G.check_combination(c0)
                    except G.Skip:
                        continue
                    total += 1
                    ref, _ = G.render(G.Cell(tn, p, o, ob), "x")
                    c = Cell(tn, p, o, ob, "A")
                    mine, _ = render9(c, "x")
                    mine = mine.replace(HELPERS9, G.HELPERS).replace(FAILSAFE9, G.FAILSAFE).replace("error:E9;\n", "")
                    if mine != ref:
                        bad += 1
                        if bad <= 3:
                            import difflib
                            print("DIFF %s %s %s %s" % (tn, p, o, ob))
                            for l in list(difflib.unified_diff(ref.splitlines(), mine.splitlines(), lineterm=""))[:30]:
                                print("   ", l)
    print("selfcheck: %d of %d M2 programs byte-identical" % (total - bad, total))
    return 1 if bad else 0


if __name__ == "__main__":
    main()
