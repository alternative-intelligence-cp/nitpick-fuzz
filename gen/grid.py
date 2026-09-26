#!/usr/bin/env python3
"""M2.2/2.3 — generate the ownership grid.

usage: python3 gen/grid.py [--out cells]

Writes cells/<id>/<id>.npk (plus cells/<id>/tbl.npk for the import axis),
cells/<id>/meta.json, cells/INDEX.jsonl (one line per cell, in id order) and
cells/SKIPPED.txt (every combination not emitted, with its reason).

A cell is (T, P, O, observer). Its metadata carries the expectation — REFUSE
or SAFE — as this generator's reading of the language's rules (the reading is
stated beside each rule below), the codes a refusal is expected to carry, and
for read_after the observations it makes with the code each should give.

Observer codes (the program's exit code when an observation is unexpected):
  21 the original value (string byte 97, list element 424242)
  22 the new value an operation wrote (byte 120, element 777777)
  23 vacant (a string of length 0, a list of count 0)
  24 some other live value
  70 the free poison 0xAA (byte 170, element -6148914691236517206)
An observation equal to its expected code passes; read_after then exits 0
WITHOUT running drops (exit runs none). drop_at_exit does the operation in
`run`, which returns normally so every drop runs, and main exits with its 0.
"""
import argparse, json, os, shutil

ORIG_LIT = "abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"       # + "c": 46+... heap string
NEW_LIT = "xyzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
FIXED_LIT = '"abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbc"'   # a literal: not heap
POISON = "-6148914691236517206i64"

FAILSAFE = """func:failsafe = int32(Error:e) {
    pick (e) {
        (HeapBadRequest) { exit 91i32; }, (HeapOom) { exit 92i32; }, (IntOverflow) { exit 93i32; },
        (OutOfBounds) { exit 94i32; }, (Unreachable) { exit 95i32; }, (WildLeak) { exit 96i32; },
        (StackExhausted) { exit 106i32; }, (MachineFault) { exit 107i32; },
        (LimitViolated) { exit 108i32; }, (DecreasesViolated) { exit 109i32; }, (TbbErr) { exit 110i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};
"""

HELPERS = """func:mk = string() never fails {
    pass string_concat("%s", "c");
};
func:nw = string() never fails {
    pass string_concat("%s", "w");
};
func:obs_s = int32(string:v) never fails {
    if (string_byte_length(v) == 0i64) { pass 23i32; }
    uint8[]:bs = string_bytes(v);
    if (bs[0i64] == 97u8) { pass 21i32; }
    if (bs[0i64] == 120u8) { pass 22i32; }
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
    if (e == %s) { pass 70i32; }
    pass 24i32;
};
""" % (ORIG_LIT, NEW_LIT, POISON, POISON)

BOX_DECL = "struct:Box = { string:s; };\n"
WRAP_DECL = "struct:Wrap = { List<int64>:l; };\n"

# ---------------------------------------------------------------- the axes
TYPES = ["str", "box", "list", "wrap", "arr_str", "arr_box", "gen_str", "gen_box"]
PLACES = ["local", "fixed_scalar", "fixed_elem", "lent_param", "move_param",
          "ptr_param", "for_binding", "field", "elem",
          "imported_fixed_typed", "imported_fixed_bare", "imported_fixed_same",
          "imported_fixed_wider", "generic_param"]
OPS = ["copy", "move", "pass_out", "field_write", "assign",
       "at_overwrite", "at_free", "at_grow", "clone", "read"]
OBSERVERS = ["read_after", "drop_at_exit"]
OBS_SHORT = {"read_after": "ra", "drop_at_exit": "dx"}

GEN = {"gen_str": "str", "gen_box": "box"}


class T:
    """What the generator knows about one owning type."""
    def __init__(self, name):
        self.name = name
        base = GEN.get(name, name)
        self.base = base
        self.ty = {"str": "string", "box": "Box", "list": "List<int64>", "wrap": "Wrap",
                   "arr_str": "string[2]", "arr_box": "Box[2]"}[base]
        self.init = {"str": "raw mk()", "box": "Box{ s: raw mk() }",
                     "list": "raw mkl(424242i64)", "wrap": "Wrap{ l: raw mkl(424242i64) }",
                     "arr_str": "[raw mk(), raw mk()]",
                     "arr_box": "[Box{ s: raw mk() }, Box{ s: raw mk() }]"}[base]
        self.new = {"str": "raw nw()", "box": "Box{ s: raw nw() }",
                    "list": "raw mkl(777777i64)", "wrap": "Wrap{ l: raw mkl(777777i64) }",
                    "arr_str": "[raw nw(), raw nw()]",
                    "arr_box": "[Box{ s: raw nw() }, Box{ s: raw nw() }]"}[base]
        self.fixed_init = {"str": FIXED_LIT, "box": "Box{ s: %s }" % FIXED_LIT,
                           "arr_str": "[%s, %s]" % (FIXED_LIT, FIXED_LIT),
                           "arr_box": "[Box{ s: %s }, Box{ s: %s }]" % (FIXED_LIT, FIXED_LIT)
                           }.get(base)
        # the sub-place a field_write writes, and its new value
        self.sub = {"box": (".s", "raw nw()"), "wrap": (".l", "raw mkl(777777i64)"),
                    "arr_str": ("[0i64]", "raw nw()"),
                    "arr_box": ("[0i64]", "Box{ s: raw nw() }")}.get(base)
        # the owning string a clone control copies
        self.clone_part = {"str": "", "box": ".s", "arr_str": "[0i64]",
                           "arr_box": "[0i64].s"}.get(base)
        self.needs_box = base in ("box", "arr_box")
        self.needs_wrap = base == "wrap"

    def obs(self, e):
        return {"str": "raw obs_s(%s)" % e, "box": "raw obs_s(%s.s)" % e,
                "list": "raw obs_l(%s)" % e, "wrap": "raw obs_l(%s.l)" % e,
                "arr_str": "raw obs_s(%s[0i64])" % e,
                "arr_box": "raw obs_s(%s[0i64].s)" % e}[self.base]


class Skip(Exception):
    pass


# --------------------------------------------------------- the expectation
# The reading of the rules, per (place kind, op). Places group as:
#   owned  — local, field, elem, move_param: the holder owns the value
#   ptr    — ptr_param: a pointer to a value the caller owns
#   loan   — lent_param, for_binding, generic_param: a LOAN (TYPE-047's words)
#   fixed  — fixed_scalar, fixed_elem, imported_fixed_*: read-only storage
def place_kind(p):
    if p in ("local", "field", "elem", "move_param"):
        return "owned"
    if p == "ptr_param":
        return "ptr"
    if p in ("lent_param", "for_binding", "generic_param"):
        return "loan"
    return "fixed"


def expectation(p, o, observer):
    """-> (REFUSE|SAFE, [codes expected on refusal], rule text)."""
    k = place_kind(p)
    if o == "copy":
        return "REFUSE", ["NITPICK-TYPE-046"], "a copy of an owning value is refused (D-183)"
    if o in ("clone", "read"):
        return "SAFE", [], "a control: clone/read of any place compiles and runs clean"
    if o in ("move", "pass_out"):
        if k == "loan":
            return "REFUSE", ["NITPICK-TYPE-047"], "a lent value has no ownership to move (D-065)"
        if k == "fixed":
            return "REFUSE", ["NITPICK-TYPE-084"], "a move out of fixed storage (TYPE-084, 6fb85d3)"
        if o == "move" and k == "owned" and observer == "read_after":
            return "REFUSE", ["NITPICK-MOVE-001"], "reading the original after its move (D-065)"
        return "SAFE", [], "a move/pass out of an owner; through a pointer it leaves a vacancy (S-26)"
    # writes: field_write, assign, at_*
    if k == "loan":
        return "REFUSE", ["NITPICK-TYPE-085"], "a loan is read-only when it owns (1.6.0 step 3g)"
    if k == "fixed":
        if o.startswith("at_"):
            return "REFUSE", ["NITPICK-TYPE-071"], "a fixed binding has no address (D-287)"
        return "REFUSE", ["NITPICK-ASSIGN-002"], "a fixed value is written once (TYPE_REFERENCE s26)"
    return "SAFE", [], "a write to an owned or pointed-to value"


def expected_obs(p, o):
    """The code an observation of the ORIGINAL should give after o."""
    k = place_kind(p)
    if k in ("loan", "fixed"):
        return 21   # refused ops; if accepted anyway the original must be untouched
    if o in ("field_write", "assign", "at_overwrite"):
        return 22
    if o == "at_free":
        return 23
    if o in ("move", "pass_out"):
        return 23   # a vacancy (ptr) or, for an owner, a moved-from binding
    return 21


# ------------------------------------------------------------ the builder
class Cell:
    def __init__(self, t, p, o, observer):
        self.t, self.p, self.o, self.observer = T(t), p, o, observer
        self.decls = []     # module-level declarations after the helpers
        self.support = None  # tbl.npk contents
        self.imports = []
        self.own_box = True


def check_combination(c):
    t, p, o = c.t, c.p, c.o
    gen = t.name in GEN
    if gen and p not in ("generic_param", "move_param", "ptr_param", "local"):
        raise Skip("a generic T is reached only through a generic body's parameter or local")
    if not gen and p == "generic_param":
        raise Skip("generic_param is the place of a generic T only")
    if gen and o == "field_write":
        raise Skip("a generic T has no fields a body may name")
    if o == "field_write" and t.sub is None:
        raise Skip("%s has no owning sub-place to write" % t.ty)
    if o == "at_grow" and t.base not in ("list", "wrap"):
        raise Skip("at_grow grows a List; %s does not grow" % t.ty)
    if o == "clone":
        if gen and t.base != "str":
            raise Skip("Box declares no Clone impl, so a Clone-bounded T cannot be Box")
        if t.clone_part is None:
            raise Skip("%s holds no owning string to clone, and has no clone method (TYPE-019 at probe)" % t.ty)
    if p in ("fixed_scalar",) and t.fixed_init is None:
        raise Skip("%s has no compile-time constant, so it cannot be fixed" % t.ty)
    if p == "fixed_elem" and t.base not in ("str", "box"):
        raise Skip("fixed_elem is an element of a fixed array of str or box; arrays of %s are outside the grid" % t.ty)
    if p == "elem" and t.base.startswith("arr_"):
        raise Skip("an array of arrays is outside the grid")
    if p == "for_binding" and t.base.startswith("arr_"):
        raise Skip("a for over an array of arrays is outside the grid")
    if p.startswith("imported_fixed"):
        if t.base not in ("str", "box"):
            raise Skip("imported tables hold str or box rows")
        v = p.rsplit("_", 1)[1]
        if t.base == "str" and v != "typed":
            raise Skip("a string row has no row type to import, omit or shadow; only imported_fixed_typed applies")
        if v == "bare" and o not in ("field_write", "clone", "read"):
            raise Skip("without its row type the importer cannot name Box, which %s needs" % o)
        if o == "field_write" and t.base == "str":
            raise Skip("string has no owning sub-place to write")


def gen_nongeneric(c):
    """Return the body of main (read_after) or run (drop_at_exit) and decls."""
    t, p, o = c.t, c.p, c.o
    TY = t.ty
    k = place_kind(p)
    stmts = []          # setup+op, placed in main or run
    observations = []   # (expr, expected code)
    exp_orig = expected_obs(p, o)

    def op_stmts(X, ADDR):
        if o == "copy":
            return ["%s:y = %s;" % (TY, X)]
        if o == "move":
            return ["%s:y = move(%s);" % (TY, X)]
        if o == "field_write":
            return ["%s%s = %s;" % (X, t.sub[0], t.sub[1])]
        if o == "assign":
            return ["%s = %s;" % (X, t.new)]
        if o == "at_overwrite":
            return ["drop at_ow(%s);" % ADDR]
        if o == "at_free":
            return ["drop at_fr(%s);" % ADDR]
        if o == "at_grow":
            return ["drop at_gr(%s);" % ADDR]
        if o == "clone":
            return ["string:y = %s%s.clone() ?! HeapOom;" % (X, t.clone_part)]
        if o == "read":
            return ["int32:rd = %s;" % t.obs(X)]
        raise AssertionError(o)

    # the at_* callees, non-generic
    if o == "at_overwrite":
        c.decls.append("func:at_ow = NIL(%s->:p) never fails {\n    (<-p) = %s;\n    pass NIL;\n};\n" % (TY, t.new))
    if o == "at_free":
        c.decls.append("func:at_fr = NIL(%s->:p) never fails {\n    %s:t = move(<-p);\n    pass NIL;\n};\n" % (TY, TY))
    if o == "at_grow":
        tgt = "p" if t.base == "list" else "@(<-p).l"
        pushes = "".join("    drop list_push::<int64>(%s, %di64);\n" % (tgt, 7 + n) for n in range(8))
        c.decls.append("func:at_gr = NIL(%s->:p) never fails {\n%s    pass NIL;\n};\n" % (TY, pushes))

    # the fixed storage
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
    if p == "field":
        c.decls.append("struct:Hold = { %s:v; };\n" % TY)

    place = {
        "local": ("x", "@x", ["%s:x = %s;" % (TY, t.init)]),
        "field": ("h.v", "@h.v", ["Hold:h = Hold{ v: %s };" % t.init]),
        "elem": ("a[i]", "@a[i]", ["%s[2]:a = [%s, %s];" % (TY, t.init, t.init), "int64:i = 1i64;"]),
        "fixed_scalar": ("FX", "@FX", []),
        "fixed_elem": ("FA[i]", "@FA[i]", ["int64:i = 1i64;"]),
    }
    if p.startswith("imported_fixed"):
        place[p] = ("TBL[i]", "@TBL[i]", ["int64:i = 1i64;"])

    if o == "pass_out":
        # the holder is a function that passes the value out; main/run reads it
        if p in place:
            X, ADDR, setup = place[p]
            body = "".join("    %s\n" % s for s in setup)
            c.decls.append("func:hold = %s() never fails {\n%s    pass %s;\n};\n" % (TY, body, X))
            stmts.append("%s:r = raw hold();" % TY)
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
            c.decls.append("func:hold = %s() never fails {\n    %s[2]:arr = [%s, %s];\n"
                           "    for (%s:x in arr) {\n        pass x;\n    }\n    pass %s;\n};\n"
                           % (TY, TY, t.init, t.init, TY, t.init))
            stmts.append("%s:r = raw hold();" % TY)
            observations.append(("r", 21))
        else:
            raise AssertionError(p)
        return stmts, observations

    if p in place:
        X, ADDR, setup = place[p]
        stmts += setup + op_stmts(X, ADDR)
        observations.append((X, exp_orig))
    elif p == "lent_param":
        body = "".join("    %s\n" % s for s in op_stmts("x", "@x"))
        c.decls.append("func:op = NIL(%s:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
        stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(orig);"]
        observations.append(("orig", exp_orig))
    elif p == "ptr_param":
        body = "".join("    %s\n" % s for s in op_stmts("(<-x)", "x"))
        c.decls.append("func:op = NIL(%s->:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
        stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(@orig);"]
        observations.append(("orig", exp_orig))
    elif p == "move_param":
        body = "".join("    %s\n" % s for s in op_stmts("x", "@x"))
        if c.observer == "read_after":
            c.decls.append("func:op = int32(move %s:x) never fails {\n%s    pass %s;\n};\n"
                           % (TY, body, t.obs("x")))
            stmts += ["%s:orig = %s;" % (TY, t.init), "int32:o0 = raw op(move(orig));"]
            observations.append(("@code:o0", exp_orig))
        else:
            c.decls.append("func:op = NIL(move %s:x) never fails {\n%s    pass NIL;\n};\n" % (TY, body))
            stmts += ["%s:orig = %s;" % (TY, t.init), "drop op(move(orig));"]
    elif p == "for_binding":
        inner = "".join("        %s\n" % s for s in op_stmts("x", "@x"))
        stmts += ["%s[2]:arr = [%s, %s];" % (TY, t.init, t.init),
                  "for (%s:x in arr) {\n%s    }" % (TY, inner)]
        observations.append(("arr[0i64]", exp_orig))
    else:
        raise AssertionError(p)
    return stmts, observations


def gen_generic(c):
    t, p, o = c.t, c.p, c.o
    TY = t.ty
    stmts, observations = [], []
    exp_orig = expected_obs(p, o)
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
    if o == "pass_out":
        ret = "T"
    elif owner_inside and c.observer == "read_after":
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
    if ret == "T" and c.observer == "read_after":
        stmts.append("%s:r = raw %s;" % (TY, call))
        if o == "pass_out":
            observations.append(("r", 21))
        else:
            observations.append(("r", exp_orig if not owner_inside else
                                 (22 if o in ("assign", "at_overwrite") else
                                  23 if o in ("at_free", "move") else 21)))
        if p in ("generic_param", "ptr_param"):
            observations.append(("orig", 23 if (p == "ptr_param" and o == "pass_out") else 21))
    elif ret == "T":
        # drop_at_exit: bind the result so it dies with run's scope (D-163 rule 4
        # refuses `drop` of a value)
        stmts.append("%s:r = raw %s;" % (TY, call))
    else:
        stmts.append("drop %s;" % call)
        if p in ("generic_param", "ptr_param"):
            observations.append(("orig", exp_orig))
    return stmts, observations


def render(c, cid):
    t = c.t
    gen = t.name in GEN
    stmts, observations = (gen_generic if gen else gen_nongeneric)(c)
    head = ["mod:%s;" % cid] + c.imports
    structs = []
    if t.needs_box and c.own_box:
        structs.append(BOX_DECL)
    if t.needs_wrap:
        structs.append(WRAP_DECL)
    src = "\n".join(head) + "\n" + "".join(structs) + HELPERS + "".join(c.decls)
    ind = "".join("    %s\n" % s for s in stmts)
    if c.observer == "read_after":
        checks = []
        for n, (e, exp) in enumerate(observations):
            if e.startswith("@code:"):
                v = e[6:]
            else:
                v = "o%d" % (n + 1)
                checks.append("    int32:%s = %s;\n" % (v, t.obs(e)))
            checks.append("    if (%s != %di32) { exit %s; }\n" % (v, exp, v))
        src += ("func:main = int32(cstring[]:_~argv) {\n%s%s    exit 0i32;\n};\n"
                % (ind, "".join(checks)))
    else:
        src += ("func:run = int32() never fails {\n%s    pass 0i32;\n};\n"
                "func:main = int32(cstring[]:_~argv) {\n    int32:r = raw run();\n    exit r;\n};\n"
                % ind)
        observations = []
    src += FAILSAFE
    return src, observations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cells")
    a = ap.parse_args()
    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    os.makedirs(a.out)
    index, skipped = [], []
    n = 0
    for tn in TYPES:
        for p in PLACES:
            for o in OPS:
                for ob in OBSERVERS:
                    c = Cell(tn, p, o, ob)
                    key = "%s %s %s %s" % (tn, p, o, ob)
                    try:
                        check_combination(c)
                    except Skip as e:
                        skipped.append((tn, p, o, ob, str(e)))
                        continue
                    n += 1
                    cid = "c%04d_%s_%s_%s_%s" % (n, tn, p, o, OBS_SHORT[ob])
                    src, observations = render(c, cid)
                    exp, codes, rule = expectation(p, o, ob)
                    d = os.path.join(a.out, cid)
                    os.makedirs(d)
                    with open(os.path.join(d, cid + ".npk"), "w") as fh:
                        fh.write(src)
                    if c.support:
                        with open(os.path.join(d, "tbl.npk"), "w") as fh:
                            fh.write(c.support)
                    meta = {"id": cid, "T": tn, "P": p, "O": o, "observer": ob,
                            "expect": exp, "expect_codes": codes, "rule": rule,
                            "observations": [{"of": e, "expect": x} for e, x in observations],
                            "codes": {"21": "original value", "22": "new value", "23": "vacant",
                                      "24": "other live value", "70": "free poison"}}
                    with open(os.path.join(d, "meta.json"), "w") as fh:
                        json.dump(meta, fh, indent=1)
                    index.append(meta)
    with open(os.path.join(a.out, "INDEX.jsonl"), "w") as fh:
        for m in index:
            fh.write(json.dumps(m) + "\n")
    with open(os.path.join(a.out, "SKIPPED.txt"), "w") as fh:
        fh.write("# T P O observer -- reason (%d combinations not emitted)\n" % len(skipped))
        for s in skipped:
            fh.write("%s %s %s %s -- %s\n" % s)
    total = len(TYPES) * len(PLACES) * len(OPS) * len(OBSERVERS)
    print("generated %d cells, skipped %d, of %d combinations" % (len(index), len(skipped), total))


if __name__ == "__main__":
    main()
