#!/usr/bin/env python3
"""M10 — silent wrong answers: the checklist, and one program per item.

usage: python3 gen/m10.py [--refs-only]

Every item states a claim, cites the reference sentence that states the right
answer (quoted, located by text at HUNT2 `.work/hunt2` and at the baseline
`.work/base`), and carries its EXPECTED verdict, written here from that text
before the program's first run (PLAN.md 10.2). Writes:
  m10/programs/<id>.npk   one program per testable item
  m10/EXPECT.tsv          id, file, expectation at HUNT2, at the baseline
  m10/CHECKLIST.md        the checklist: claim, citations, expectation, and
                          what a wrong implementation would answer
An expectation is `run:N` (npkc 0, both legs exit N), `refuse` (npkc 1) or
`refuse:CODE` (npkc 1 naming CODE). `expect_base` is set only where the
baseline's own reference text says something else (recorded per item).

The program convention: exit 0 is the reference's answer; 10-59 name the check
that saw a wrong value; a trap reaches `failsafe` and exits its arm's code
(TRAPS below); a user error `E<k>` exits 80+k.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "m10")

DOCS = {
    "TYPE": "meta/specs/TYPE_REFERENCE.md",
    "OP": "meta/specs/OP_REFERENCE.md",
    "CONTROL": "meta/specs/CONTROL_REFERENCE.md",
    "BUILTIN": "meta/specs/BUILTIN_REFERENCE.md",
    "LEXICAL": "meta/specs/LEXICAL_REFERENCE.md",
    "MEMORY": "meta/specs/MEMORY_REFERENCE.md",
    "VERIFICATION": "meta/specs/VERIFICATION_REFERENCE.md",
    "SAFETY": "meta/specs/SAFETY_ARCHITECTURE.md",
    "DECISIONS": "meta/specs/DECISIONS.md",
}

# failsafe arms: the grid's codes (PROGRESS S4) and M10's additions (111-117)
TRAPS = [("HeapBadRequest", 91), ("HeapOom", 92), ("IntOverflow", 93), ("OutOfBounds", 94),
         ("Unreachable", 95), ("WildLeak", 96), ("DivByZero", 97), ("DivOverflow", 98),
         ("StackExhausted", 106), ("MachineFault", 107), ("LimitViolated", 108),
         ("DecreasesViolated", 109), ("TbbErr", 110), ("ShiftRange", 111), ("CastRange", 112),
         ("BadStep", 113), ("BorrowOverlap", 114), ("RequiresViolated", 115),
         ("EnsuresViolated", 116), ("InvariantViolated", 117)]

# identity functions: a value that goes through one is not a constant to the
# compiler's folder, so the run-time operation is what gets measured
HELPERS = {
    "v8": "int8", "v16": "int16", "v32": "int32", "v64": "int64", "vi128": "int128",
    "vu8": "uint8", "vu16": "uint16", "vu32": "uint32", "vu64": "uint64",
    "vf32": "flt32", "vf64": "flt64", "vc8": "char8", "vb": "bool",
    "vt8": "tbb8", "vt32": "tbb32",
}

ITEMS = []


def item(iid, area, title, claim, refs, expect, src=None, wrong="", note="",
         expect_base=None, untestable=None):
    ITEMS.append(dict(id=iid, area=area, title=title, claim=claim, refs=refs, expect=expect,
                      src=src, wrong=wrong, note=note, expect_base=expect_base,
                      untestable=untestable))


def main_(body, decls=""):
    """A program: top-level declarations, then `main` around `body`."""
    return (decls.strip() + "\n\n" if decls.strip() else "") + \
        "func:main = int32(cstring[]:_~argv) {\n" + body.rstrip() + "\n};\n"


# ---------------------------------------------------------------- D defaults
AREA_D = "defaults and zero values"

item("d01_struct_lit_omits_field", AREA_D,
     "a struct literal that omits a field",
     "A struct literal must name every field; one that omits a field is refused, "
     "since the omitted field would have no value.",
     [("DECISIONS", "struct literal that omits a field leaves it with no value"),
      ("DECISIONS", "struct literal cannot omit fields")],
     "refuse",
     main_("""    Pt:p = Pt{ x: 1i32 };
    if (p.y == 0i32) { exit 10i32; }
    exit 11i32;""", "struct:Pt = { int32:x; int32:y; };"),
     wrong="accepted: the omitted field reads 0 (exit 10), a default standing in for a value never set")

item("d02_read_unassigned", AREA_D,
     "a read of a binding declared without a value",
     "Definite assignment refuses a read before any write.",
     [("TYPE", "Definite-assignment analysis rejects"),
      ("DECISIONS", "compile time any path that reads a variable before writing it**. That guarantee is")],
     "refuse",
     main_("""    int32:x;
    int32:y = x + 1i32;
    if (y == 1i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: `x` reads 0 (exit 10) or garbage (11)")

item("d03_read_unassigned_on_a_path", AREA_D,
     "a read after a write on only one path",
     "Definite assignment refuses a read that SOME path reaches unwritten.",
     [("DECISIONS", "compile time any path that reads a variable before writing it**. That guarantee is")],
     "refuse",
     main_("""    int32:x;
    if (raw vb(false)) { x = 5i32; }
    if (x == 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: the unwritten path reads 0 (exit 10)")

item("d04_tbb_assign_replaces", AREA_D,
     "a declared tbb assigned later, then computed",
     "A binding declared without a value may be written later; the assignment replaces, "
     "and arithmetic after it is ordinary (D-010's own example).",
     [("TYPE", "Assignment *replaces* a value"),
      ("DECISIONS", "assignment REPLACES")],
     "run:0",
     main_("""    tbb32:x;
    x = raw vt32(5tbb32);
    x = x + 1tbb32;
    if (is_err(x)) { exit 10i32; }
    if (x != 6tbb32) { exit 11i32; }
    exit 0i32;"""),
     wrong="a declared-then-written binding misread (11), or tainted (10)")

item("d05_empty_array_literal_is_zero", AREA_D,
     "`[]` is the zeroed array",
     "An empty array literal where a fixed-length array is expected is that array zeroed.",
     [("DECISIONS", "An empty array literal, where a fixed-length array type is expected, is that")],
     "run:0",
     main_("""    discard(raw dirty());
    if (raw clean() != 0i64) { exit 10i32; }
    exit 0i32;""", """func:dirty = int64() never fails {
    int64[64]:j = [];
    for (int64:k in 0i64...64i64) { j[k] = 12345i64; }
    pass j[raw v64(63i64)];
};
func:clean = int64() never fails {
    int64[64]:z = [];
    int64:s = 0i64;
    for (int64:k in 0i64...64i64) { s = s + z[k]; }
    pass s;
};"""),
     wrong="the frame's previous bytes (a dirty stack) read through a `[]` array (exit 10)")

item("d06_short_array_literal", AREA_D,
     "a non-empty array literal shorter than its type",
     "A non-empty array literal must match the length exactly; partial initialisation is unspellable.",
     [("DECISIONS", "A **non-empty** literal must still match the")],
     "refuse",
     main_("""    int32[4]:a = [1i32, 2i32];
    if (a[raw v64(3i64)] == 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: the missing elements read 0 (exit 10)")

item("d07_result_literal_omits_err", AREA_D,
     "`Result{ value: v }` with the error omitted",
     "Either field of a Result literal may be omitted and defaults to the zero for its side: "
     "an omitted `err` is success.",
     [("TYPE", "**Either field may be omitted**"),
      ("CONTROL", "the literal form, the only way to return a value")],
     "run:0",
     main_("""    Result<int32>:r = f();
    if (r.is_error) { exit 10i32; }
    if ((f() ?| 0i32) != 7i32) { exit 11i32; }
    exit 0i32;""", """func:f = int32() {
    return Result{ value: 7i32 };
};"""),
     wrong="the omitted error field read as a failure (10) or the value lost (11)")

item("d08_result_literal_omits_value", AREA_D,
     "`Result{ err: E }` with the value omitted",
     "A Result literal with only `err` is that error.",
     [("TYPE", "**Either field may be omitted**")],
     "run:0",
     main_("""    Result<int32>:r = f();
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    if ((f() ?| 5i32) != 5i32) { exit 12i32; }
    exit 0i32;""", """error:E1;
func:f = int32() {
    return Result{ err: E1 };
};"""),
     wrong="an error literal read as success (10) or the wrong error (11)")

item("d09_optional_nil_and_value", AREA_D,
     "an Optional built from `NIL` and from a value",
     "`NIL` is the empty Optional, a value is the holding one, `??` yields the value or the default.",
     [("TYPE", "| `int32?:a = NIL;` | empty |"),
      ("TYPE", "| `a ?? d` | the value, or `d` |")],
     "run:0",
     main_("""    int32?:a = NIL;
    int32?:b = raw v32(42i32);
    if (a != NIL) { exit 10i32; }
    if ((a ?? 7i32) != 7i32) { exit 11i32; }
    if ((b ?? 7i32) != 42i32) { exit 12i32; }
    if (b == NIL) { exit 13i32; }
    exit 0i32;"""),
     wrong="the empty Optional reading as holding its zeroed value 0 (11), or a held value lost (12)")

item("d10_read_field_of_undeclared_struct", AREA_D,
     "a field read of a struct declared without a value",
     "A struct declared without an initialiser and never written may not be read.",
     [("DECISIONS", "compile time any path that reads a variable before writing it**. That guarantee is"),
      ("DECISIONS", "struct literal that omits a field leaves it with no value")],
     "refuse",
     main_("""    Pt:p;
    if (p.y == 0i32) { exit 10i32; }
    exit 11i32;""", "struct:Pt = { int32:x; int32:y; };"),
     wrong="accepted: the field reads 0 (exit 10), a default standing in for one never set")

item("d11_read_unwritten_field", AREA_D,
     "a read of the one field never written",
     "Writing one field of a declared-uninitialised struct does not give the other a value.",
     [("DECISIONS", "struct literal that omits a field leaves it with no value"),
      ("DECISIONS", "compile time any path that reads a variable before writing it**. That guarantee is")],
     "refuse",
     main_("""    Pt:p;
    p.x = raw v32(1i32);
    if (p.y == 0i32) { exit 10i32; }
    exit 11i32;""", "struct:Pt = { int32:x; int32:y; };"),
     wrong="accepted: the unwritten field reads 0 (exit 10)",
     note="Inferred, not stated: the references state definite assignment per variable; "
          "that an unwritten FIELD counts as unassigned is read from D-129's sentence about a "
          "literal's omitted field.")

item("d12_fixed_local_written_later", AREA_D,
     "a `fixed` local written once, later, at run time",
     "A `fixed` local may be written once after its declaration, from a run-time value.",
     [("TYPE", "derived = raw compute(seed);   // the one write, at run time")],
     "run:0",
     main_("""    fixed int32:d;
    d = raw v32(5i32);
    if (d != 5i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the run-time write lost (exit 10)")

item("d13_fixed_local_written_twice", AREA_D,
     "a second write to a `fixed` local",
     "A `fixed` binding is written once and never again: a second write is ASSIGN-002.",
     [("TYPE", "// derived = 0i32;             // NITPICK-ASSIGN-002"),
      ("TYPE", "**Diagnostic:** every one of these is `NITPICK-ASSIGN-002`")],
     "refuse:NITPICK-ASSIGN-002",
     main_("""    fixed int32:d;
    d = raw v32(5i32);
    d = raw v32(6i32);
    if (d == 6i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: the second write lands (exit 10)")

item("d14_fixed_field_written", AREA_D,
     "a write to a `fixed` field after construction",
     "A `fixed` struct field is written when the aggregate is constructed and never after.",
     [("TYPE", "// A struct field, written when the aggregate is constructed and never after"),
      ("TYPE", "**Diagnostic:** every one of these is `NITPICK-ASSIGN-002`")],
     "refuse:NITPICK-ASSIGN-002",
     main_("""    Cfg:c = Cfg{ k: 1i32, v: 2i32 };
    c.k = raw v32(9i32);
    if (c.k == 9i32) { exit 10i32; }
    exit 11i32;""", "struct:Cfg = { fixed int32:k; int32:v; };"),
     wrong="accepted: the fixed field is rewritten (exit 10)")

item("d15_safe_navigation_on_empty", AREA_D,
     "`?.` through an empty and a holding Optional",
     "`?.` yields an empty Optional when its operand is empty, and the field wrapped when present.",
     [("TYPE", "`?.` yields `zeroinitializer` of the result type when empty and wraps"),
      ("TYPE", "| `a?.f` | the field, still wrapped |")],
     "run:0",
     main_("""    Pt?:o = NIL;
    Pt?:q = Pt{ x: 3i32, y: 4i32 };
    if ((o?.x ?? 9i32) != 9i32) { exit 10i32; }
    if ((q?.y ?? 9i32) != 4i32) { exit 11i32; }
    exit 0i32;""", "struct:Pt = { int32:x; int32:y; };"),
     wrong="the empty Optional's zeroed field read as present, 0 (exit 10)")

item("d16_uninit_owning_field_overwrite", AREA_D,
     "an owning field written into a struct declared without a value",
     "A declaration without an initialiser writes the canonical vacant value, so the first "
     "overwrite of an owning field drops nothing.",
     [("DECISIONS", "without an initialiser WRITES it. This completes a design the drop bodies"),
      ("DECISIONS", "without an initialiser — `Front:f;`, the `$$m` out-parameter idiom `src/main.npk`"),
      ("TYPE", "A declared-uninitialised aggregate holds the vacant value (D-225)")],
     "run:0",
     main_("""    Hs:h;
    drop init($$m h);
    if (h.s.len != 3i64) { exit 10i32; }
    if (h.n != 1i32) { exit 11i32; }
    exit 0i32;""", """struct:Hs = { string:s; int32:n; };
func:init = NIL(Hs->:p) never fails {
    p.s = string_concat("ab", "c");
    p.n = raw v32(1i32);
    pass NIL;
};"""),
     wrong="the overwrite drops the slot's garbage (a trap, 91 or 95) or loses the value (10)",
     note="Run 1 wrote the fields directly (`h.s = ...` after `Hs:h;`): refused `ASSIGN-001` at "
          "the first field write, D-010's rule. D-225 names the idiom it serves, `Front:f;` "
          "handed as `$$m f` to an initialiser, so the program now uses it (S36); the "
          "expectation is unchanged.")

# ------------------------------------------------------------ C conversions
AREA_C = "numeric conversions and literals"

item("c01_widen_signed_keeps_value", AREA_C,
     "`=>` widening a negative signed value",
     "`=>` accepts a conversion only when every source value is representable in the target, "
     "so the value is kept: a negative value sign-extends.",
     [("DECISIONS", "A conversion is lossless when every value of the source type is representable"),
      ("OP", "| `=>` | Safe Cast | Checked cast.")],
     "run:0",
     main_("""    int32:a = raw v32(-1i32);
    int64:w = a => int64;
    if (w != -1i64) { exit 10i32; }
    int8:b = raw v8(-100i8);
    if ((b => int64) != -100i64) { exit 11i32; }
    exit 0i32;"""),
     wrong="zero-extension: -1 becomes 4294967295 (exit 10)")

item("c02_widen_unsigned_keeps_value", AREA_C,
     "`=>` from an unsigned type to a wider signed one",
     "An unsigned value converted by `=>` keeps its value: it zero-extends (D-095's own "
     "example is `uint8 => int16`).",
     [("DECISIONS", "The difference is not academic. `uint8 => int16` is lossless")],
     "run:0",
     main_("""    uint32:u = raw vu32(4294967295u32);
    int64:w = u => int64;
    if (w != 4294967295i64) { exit 10i32; }
    uint8:b = raw vu8(200u8);
    if ((b => int16) != 200i16) { exit 11i32; }
    uint32:c = raw vu32(3000000000u32);
    if ((c => uint64) != 3000000000u64) { exit 12i32; }
    exit 0i32;"""),
     wrong="sign-extension: 4294967295 becomes -1 (10), 200 becomes -56 (11)")

item("c03_narrow_signed_refused", AREA_C,
     "`int64 => int32`",
     "`=>` is a compile-time error wherever data loss is possible.",
     [("OP", "**Compile-time error** if data loss is possible"),
      ("TYPE", "as the plain matrix spells `int64 => int8` and `int32 => uint32`")],
     "refuse",
     main_("""    int64:a = raw v64(5000000000i64);
    int32:n = a => int32;
    if (n == 705032704i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a silent truncation (exit 10)")

item("c04_signed_to_unsigned_refused", AREA_C,
     "`int32 => uint32`",
     "`int32 => uint32` loses the negative values and is refused.",
     [("TYPE", "as the plain matrix spells `int64 => int8` and `int32 => uint32`")],
     "refuse",
     main_("""    int32:a = raw v32(-1i32);
    uint32:n = a => uint32;
    if (n == 4294967295u32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: -1 silently reinterpreted (exit 10)")

item("c05_uint8_to_int8_refused", AREA_C,
     "`uint8 => int8`",
     "`uint8 => int8` loses 128..255 and is refused (range containment, not type families).",
     [("DECISIONS", "A conversion is lossless when every value of the source type is representable")],
     "refuse",
     main_("""    uint8:a = raw vu8(200u8);
    int8:n = a => int8;
    if (n < 0i8) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: 200 silently becomes -56 (exit 10)")

item("c06_int32_to_flt64_exact", AREA_C,
     "`int32 => flt64`",
     "`int32 => flt64` is accepted, and exact: 53 significand bits hold every int32.",
     [("DECISIONS", "`int32 => flt64` is accepted")],
     "run:0",
     main_("""    int32:a = raw v32(16777217i32);
    if ((a => flt64) != 16777217.0f64) { exit 10i32; }
    int32:b = raw v32(2147483647i32);
    if ((b => flt64) != 2147483647.0f64) { exit 11i32; }
    exit 0i32;"""),
     wrong="a conversion through flt32 rounds 16777217 to 16777216 (exit 10)")

item("c07_int64_to_flt64_refused", AREA_C,
     "`int64 => flt64`",
     "`int64 => flt64` is refused: 53 significand bits are fewer than 63.",
     [("DECISIONS", "`int64 => flt64` is **refused**")],
     "refuse",
     main_("""    int64:a = raw v64(9007199254740993i64);
    flt64:f = a => flt64;
    if (f == 9007199254740992.0f64) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: 2^53+1 silently rounds (exit 10)")

item("c08_int32_to_flt32_refused", AREA_C,
     "`int32 => flt32`",
     "`int32 => flt32` is refused: 24 significand bits are fewer than 31.",
     [("DECISIONS", "`int32 => flt32` is refused too")],
     "refuse",
     main_("""    int32:a = raw v32(16777217i32);
    flt32:f = a => flt32;
    if (f == 16777216.0f32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: 16777217 silently rounds (exit 10)")

item("c09_float_to_int_checked_refused", AREA_C,
     "`flt64 => int64`",
     "A float to an integer is always lossy, so `=>` refuses it.",
     [("DECISIONS", "Float to integer is always lossy at every width")],
     "refuse",
     main_("""    flt64:a = raw vf64(2.5f64);
    int64:n = a => int64;
    if (n == 2i64) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: the fraction silently dropped (exit 10)")

item("c10_float_to_int_truncates", AREA_C,
     "`flt64 =>! int32` of 3.7 and -3.7",
     "A float's `=>!` cast to an integer truncates toward zero.",
     [("TYPE", "explicit opt-in, truncates toward zero"),
      ("VERIFICATION", "its truncation toward zero lies inside the target")],
     "run:0",
     main_("""    flt64:a = raw vf64(3.7f64);
    flt64:b = raw vf64(-3.7f64);
    if ((a =>! int32) != 3i32) { exit 10i32; }
    if ((b =>! int32) != -3i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="rounding to nearest (4, -4: exits 10) or flooring (-4: exit 11)")

item("c11_float_nan_to_int_traps", AREA_C,
     "`flt64 =>! int32` of NaN",
     "A float's `=>!` cast to an integer traps `CastRange` on NaN.",
     [("DECISIONS", "A float's `=>!` cast to an integer traps `CastRange` (4117) on NaN")],
     "run:112",
     main_("""    flt64:z = raw vf64(0.0f64);
    flt64:n = z / z;
    int32:k = n =>! int32;
    if (k == 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="no trap: LLVM poison, read as some integer (10 or 11)")

item("c12_float_too_big_to_int_traps", AREA_C,
     "`flt64 =>! int32` of 3e9",
     "A float's `=>!` cast to an integer traps `CastRange` on a value whose truncation the "
     "target cannot hold.",
     [("DECISIONS", "a value whose truncation the target cannot hold")],
     "run:112",
     main_("""    flt64:big = raw vf64(3000000000.0f64);
    int32:k = big =>! int32;
    if (k < 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="no trap: a saturated or wrapped integer (10 or 11)")

item("c13_unchecked_cast_truncates_bits", AREA_C,
     "`=>!` between integer types",
     "`=>!` is a direct bit-cast or truncation without checking.",
     [("OP", "Direct bit-cast/truncation without checking")],
     "run:0",
     main_("""    int32:a = raw v32(300i32);
    if ((a =>! uint8) != 44u8) { exit 10i32; }
    int32:m = raw v32(-1i32);
    if ((m =>! uint32) != 4294967295u32) { exit 11i32; }
    uint32:u = raw vu32(4294967295u32);
    if ((u =>! int32) != -1i32) { exit 12i32; }
    int64:c = raw v64(-129i64);
    if ((c =>! int8) != 127i8) { exit 13i32; }
    uint64:w = raw vu64(4294967297u64);
    if ((w =>! uint32) != 1u32) { exit 14i32; }
    exit 0i32;"""),
     wrong="a saturating or value-checked narrowing (any of 10-14)")

item("c14_bool_to_int", AREA_C,
     "`bool => int32`",
     "`bool => int32` yields 0 or 1.",
     [("TYPE", "Cast: `bool => int32` yields 0 or 1")],
     "run:0",
     main_("""    bool:t = raw vb(true);
    bool:f = raw vb(false);
    if ((t => int32) != 1i32) { exit 10i32; }
    if ((f => int32) != 0i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="true as -1 or 255 (exit 10)")

item("c15_int_to_bool_refused", AREA_C,
     "`int32 => bool`",
     "`intN => bool` is refused outright: it is not a conversion at all.",
     [("DECISIONS", "**`intN => bool` is refused outright.**")],
     "refuse",
     main_("""    bool:b = raw v32(2i32) => bool;
    if (b) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: C truthiness (exit 10)")

item("c16_int_to_bool_unchecked_refused", AREA_C,
     "`int32 =>! bool`",
     "`=>!` does not rescue a conversion that is not one: `intN =>! bool` is refused too.",
     [("DECISIONS", "and `=>!` does not rescue the third"),
      ("DECISIONS", "**`intN => bool` is refused outright.**")],
     "refuse",
     main_("""    bool:b = raw v32(2i32) =>! bool;
    if (b) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a truthiness or low-bit reading (exit 10 or 11)")

item("c17_enum_to_int_reads_tag", AREA_C,
     "`enum =>! int32`",
     "`enum =>! intN` reads the tag, whose values the declaration states.",
     [("TYPE", "pub enum:Color = { Red = 0i32; Green = 1i32; Blue = 2i32; };"),
      ("TYPE", "; `enum =>! intN` reads the TAG (slot 0) at every shape")],
     "run:0",
     main_("""    Color:c = Color.Blue;
    if ((c =>! int32) != 2i32) { exit 10i32; }
    Color:g = Color.Green;
    if ((g =>! int32) != 1i32) { exit 11i32; }
    exit 0i32;""", "enum:Color = { Red = 0i32; Green = 1i32; Blue = 2i32; };"),
     wrong="an ordinal or the wrong slot (exit 10 or 11)")

item("c18_int_to_tag_only_enum", AREA_C,
     "`int32 =>! enum` for a tag-only enum",
     "A tag-only enum takes `intN =>! enum`, which manufactures that tag.",
     [("TYPE", "; SCOPED BY SHAPE (D-140; scoped here 2026-09-25, DEF-101): a TAG-ONLY enum takes")],
     "run:0",
     main_("""    int32:k = raw v32(2i32);
    Color:c = k =>! Color;
    int32:r = 0i32;
    pick (c) {
        (Color.Red) { r = 1i32; },
        (Color.Green) { r = 2i32; },
        (Color.Blue) { r = 3i32; }
    }
    if (r != 3i32) { exit 10i32; }
    exit 0i32;""", "enum:Color = { Red = 0i32; Green = 1i32; Blue = 2i32; };"),
     wrong="the tag mis-manufactured (exit 10)",
     expect_base="refuse",
     note="The baseline's own TYPE_REFERENCE says `intN => enum` is impossible in both spellings; "
          "the sentence was scoped by shape on 2026-09-25 (DEF-101), after `c3bdae2`.")

item("c19_unsuffixed_literal_takes_context", AREA_C,
     "an unsuffixed literal beside a typed operand",
     "An unsuffixed integer literal takes its type from its context, including the other operand.",
     [("DECISIONS", "So an unsuffixed literal is typed by the position it appears in"),
      ("DECISIONS", "int64:g;               g + 1                 // int64")],
     "run:0",
     main_("""    int64:g = raw v64(4000000000i64);
    int64:h = g + 1;
    if (h != 4000000001i64) { exit 10i32; }
    uint8:u = raw vu8(200u8);
    if (u < 100) { exit 11i32; }
    exit 0i32;"""),
     wrong="the literal typed int32 or int8: 200 as int8 is below 100 (exit 11)")

item("c20_literal_must_fit", AREA_C,
     "`300u8`",
     "A numeric literal must fit its type (TYPE-031).",
     [("LEXICAL", "and must fit its type — suffixed or contextual — verified at the literal")],
     "refuse:NITPICK-TYPE-031",
     main_("""    uint8:x = 300u8;
    if (x == 44u8) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: truncated to 44 (exit 10)")

item("c21_most_negative_decimal_unspellable", AREA_C,
     "`-128i8` in decimal",
     "A signed width's most negative value is constructed, not spelled, in decimal: the "
     "literal `128i8` does not fit.",
     [("LEXICAL", "spelled**: `uint64` above 2⁶³−1 (`0u64 - 1u64` is the maximum), a signed"),
      ("LEXICAL", "width's most negative value in decimal (spell it in a balanced base:")],
     "refuse",
     main_("""    int8:m = -128i8;
    if (m == raw v8(-127i8) - raw v8(1i8)) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted (exit 10 or 11): the reference's sentence would not hold")

item("c22_literal_bases", AREA_C,
     "hex, binary, octal, nonary and balanced-ternary literals, and underscores",
     "The base is a suffix: `0FFhex` is 255, `0b4bni8` is -128; underscores are ignored.",
     [("LEXICAL", "Underscores are permitted for readability and ignored."),
      ("LEXICAL", "`0b4bni8` is −128"),
      ("LEXICAL", "HexLiteral     ::= [0-9] ([0-9a-fA-F_]* [0-9a-fA-F])? \"hex\""),
      ("LEXICAL", "/* Balanced nonary: A..D / a..d denote -1..-4 */"),
      ("LEXICAL", "/* Balanced ternary: T/t denotes -1 */")],
     "run:0",
     main_("""    if (0FFhexi32 != 255i32) { exit 10i32; }
    if (101bini32 != 5i32) { exit 11i32; }
    if (17octi32 != 15i32) { exit 12i32; }
    if (1_000i32 != 1000i32) { exit 13i32; }
    if (12ni32 != 11i32) { exit 14i32; }
    int8:m = raw v8(-127i8) - raw v8(1i8);
    if (0b4bni8 != m) { exit 15i32; }
    if (1T0ti32 != 6i32) { exit 16i32; }
    if (0Tti32 != -1i32) { exit 17i32; }
    exit 0i32;"""),
     wrong="a digit or base misread (the check's code)")

item("c23_c_hex_prefix_refused", AREA_C,
     "`0xFF`",
     "The C prefixes were removed: `0xFF` is a bad-digit error at the `x`.",
     [("LEXICAL", "`0xFF` is a bad-digit error at the `x`")],
     "refuse:NITPICK-LEX-003",
     main_("""    int32:x = 0xFF;
    if (x == 255i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: C's reading (exit 10)")

item("c24_float_literal_exponent", AREA_C,
     "`1.5e2f64`",
     "A float literal takes a decimal exponent.",
     [("LEXICAL", "FloatLiteral   ::= DecimalLiteral \".\" DecimalLiteral Exponent? TypeSuffix?")],
     "run:0",
     main_("""    flt64:x = raw vf64(1.5e2f64);
    if (x != 150.0f64) { exit 10i32; }
    flt64:y = raw vf64(2.5e-1f64);
    if (y != 0.25f64) { exit 11i32; }
    exit 0i32;"""),
     wrong="the exponent dropped or mis-signed (10 or 11)")

item("c25_flt32_literal_16_digits", AREA_C,
     "a `flt32` literal with 16 significant digits",
     "A flt32 literal carries at most 15 significant digits.",
     [("TYPE", "A `flt32` literal carries at most 15 significant digits")],
     "refuse",
     main_("""    flt32:x = 0.1234567890123456f32;
    if (x > 0.0f32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: an implementation-defined value (exit 10)")

item("c26_constant_overflow_contextual", AREA_C,
     "`int8:x = 100 + 100;`",
     "A constant that does not fit its type is TYPE-076; an unsuffixed pair takes its width "
     "from the context.",
     [("OP", "so `int8:x = 100 + 100;` is refused too")],
     "refuse:NITPICK-TYPE-076",
     main_("""    int8:x = 100 + 100;
    if (x < 0i8) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: wrapped to -56 (exit 10)")

item("c27_uint64_zero_minus_one_refused", AREA_C,
     "`0u64 - 1u64`",
     "`0u64 - 1u64` is refused (TYPE-076); the maximum is `~0u64`.",
     [("LEXICAL", "(NITPICK-TYPE-076). `uint64`'s upper half is constructed with bit operations,")],
     "refuse:NITPICK-TYPE-076",
     main_("""    uint64:m = 0u64 - 1u64;
    if (m == ~0u64) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: wrapped (exit 10)")

item("c28_uint64_max_by_bits", AREA_C,
     "`~0u64`, `0u64 -% 1u64`, and a high value by `|`",
     "`~0u64` is the uint64 maximum, `0u64 -% 1u64` equals it, and `(1u64 << 63u64) | k` builds "
     "a value above 2^63-1.",
     [("LEXICAL", "which never overflow: `~0u64` is the maximum, and `(1u64 << 63u64) | k` gives"),
      ("LEXICAL", "From 1.5.8b step 4, `0u64 -% 1u64` also works")],
     "run:0",
     main_("""    uint64:m = ~0u64;
    if ((0u64 -% 1u64) != m) { exit 10i32; }
    if ((m >> 63u64) != 1u64) { exit 11i32; }
    if ((m +% 1u64) != 0u64) { exit 12i32; }
    uint64:r = raw vu64(0u64) -% raw vu64(1u64);
    if (r != m) { exit 13i32; }
    uint64:h = (1u64 << 63u64) | 5u64;
    if ((h -% 5u64) != (m >> 1u64) +% 1u64) { exit 14i32; }
    exit 0i32;"""),
     wrong="a signed reading of the high half (11, 14)")

# ------------------------------------------------------------ O overflow
AREA_O = "integer overflow"
REF_TRAP = ("TYPE", "Arithmetic: `+`, `-`, `*` — **overflow TRAPS** (D-210, 1.4.2b), through the")
REF_UNSIGNED_TRAP = ("TYPE", "Overflow TRAPS, as with signed types (D-210)")


def trap_item(iid, title, decl_a, op_b, wrong_msg, refs=None, extra_note=""):
    """`<decl_a>; <T>:b = <op_b>;` must trap IntOverflow (93)."""
    item(iid, AREA_O, title,
         "Plain-integer `+ - *` and negation trap `IntOverflow` on overflow, at every width.",
         refs or [REF_TRAP],
         "run:93",
         main_(decl_a + "\n" + op_b + """
    exit 11i32;"""),
         wrong=wrong_msg, note=extra_note)


trap_item("o01_int32_add", "int32 `+` past the maximum",
          "    int32:a = raw v32(2147483647i32);",
          "    int32:b = a + raw v32(1i32);\n    if (b < 0i32) { exit 10i32; }",
          "wraps to a negative value (exit 10)")
trap_item("o02_int32_sub", "int32 `-` past the minimum",
          "    int32:a = raw v32(-2147483647i32);",
          "    int32:b = a - raw v32(2i32);\n    if (b > 0i32) { exit 10i32; }",
          "wraps to a positive value (exit 10)")
trap_item("o03_int32_mul", "int32 `*` past the maximum",
          "    int32:a = raw v32(65536i32);",
          "    int32:b = a * raw v32(65536i32);\n    if (b == 0i32) { exit 10i32; }",
          "wraps to 0 (exit 10)")
trap_item("o04_int32_negate_min", "negation of the int32 minimum",
          "    int32:m = raw v32(-2147483647i32) - raw v32(1i32);",
          "    int32:b = -m;\n    if (b < 0i32) { exit 10i32; }",
          "negation of the minimum returns the minimum (exit 10)",
          refs=[("TYPE", "**Unary `-` is `0 - x`** and so traps on the most negative value")])
trap_item("o05_int8_add", "int8 `+` past the maximum",
          "    int8:a = raw v8(127i8);",
          "    int8:b = a + raw v8(1i8);\n    if (b < 0i8) { exit 10i32; }",
          "computed in a wider type and truncated: -128 (exit 10)")
trap_item("o06_int16_mul", "int16 `*` past the maximum",
          "    int16:a = raw v16(200i16);",
          "    int16:b = a * raw v16(200i16);\n    if (b < 0i16) { exit 10i32; }",
          "computed wider and truncated: -25536 (exit 10)")
trap_item("o07_uint8_add", "uint8 `+` past 255",
          "    uint8:a = raw vu8(255u8);",
          "    uint8:b = a + raw vu8(1u8);\n    if (b == 0u8) { exit 10i32; }",
          "the 255 -> 0 wrap (exit 10)", refs=[REF_UNSIGNED_TRAP])
trap_item("o08_uint8_sub", "uint8 `-` below 0",
          "    uint8:a = raw vu8(0u8);",
          "    uint8:b = a - raw vu8(1u8);\n    if (b == 255u8) { exit 10i32; }",
          "the 0 -> 255 wrap (exit 10)", refs=[REF_UNSIGNED_TRAP])
trap_item("o09_uint32_sub", "uint32 `-` below 0",
          "    uint32:a = raw vu32(0u32);",
          "    uint32:b = a - raw vu32(1u32);\n    if (b == 4294967295u32) { exit 10i32; }",
          "the wrap to the maximum (exit 10)", refs=[REF_UNSIGNED_TRAP])
trap_item("o10_uint64_mul", "uint64 `*` past the maximum",
          "    uint64:a = raw vu64(4294967296u64);",
          "    uint64:b = a * raw vu64(4294967296u64);\n    if (b == 0u64) { exit 10i32; }",
          "wraps to 0 (exit 10)", refs=[REF_UNSIGNED_TRAP])
trap_item("o11_int64_add", "int64 `+` past the maximum",
          "    int64:a = raw v64(9223372036854775807i64);",
          "    int64:b = a + raw v64(1i64);\n    if (b < 0i64) { exit 10i32; }",
          "wraps to the minimum (exit 10)")
trap_item("o12_compound_add", "int32 `+=` past the maximum",
          "    int32:x = raw v32(2147483647i32);",
          "    x += raw v32(1i32);\n    if (x < 0i32) { exit 10i32; }",
          "the compound spelling wraps where `+` traps (exit 10)",
          refs=[("TYPE", "**`x += y` traps identically**: both spellings route through one arithmetic")])
trap_item("o13_compound_mul_int8", "int8 `*=` past the maximum",
          "    int8:x = raw v8(64i8);",
          "    x *= raw v8(2i8);\n    if (x < 0i8) { exit 10i32; }",
          "the compound spelling wraps (exit 10)",
          refs=[("TYPE", "**`x += y` traps identically**: both spellings route through one arithmetic")])
trap_item("o14_compound_sub_uint16", "uint16 `-=` below 0",
          "    uint16:x = raw vu16(0u16);",
          "    x -= raw vu16(1u16);\n    if (x == 65535u16) { exit 10i32; }",
          "the compound spelling wraps (exit 10)",
          refs=[("TYPE", "**`x += y` traps identically**: both spellings route through one arithmetic"),
                REF_UNSIGNED_TRAP])
trap_item("o15_int8_sub_past_min", "int8 `-` below the minimum",
          "    int8:a = raw v8(-127i8);",
          "    int8:b = a - raw v8(2i8);\n    if (b > 0i8) { exit 10i32; }",
          "wraps to 127 (exit 10)")
trap_item("o16_int128_add", "int128 `+` past the maximum",
          "    int128:big = raw vi128(1i128) << raw vi128(126i128);\n"
          "    int128:mx = big + (big - raw vi128(1i128));",
          "    int128:o = mx + raw vi128(1i128);\n    if (o < raw vi128(0i128)) { exit 10i32; }",
          "wraps to the minimum (exit 10)",
          refs=[("TYPE", "and legalized at every width the language has, `int8` through `int4096`."),
                ("TYPE", "**Behaviors:** ordinary integer semantics at every width — D-037 wrapping,")],
          extra_note="TYPE_REFERENCE contradicts itself here: §1.2 says the intrinsics trap at every "
                     "width, §4 still says 'D-037 wrapping' for the wide integers. The expectation "
                     "follows §1.2 (D-210, the later decision); the program decides which text is stale.")

item("o17_edges_do_not_trap", AREA_O,
     "arithmetic that lands exactly on a type's edge",
     "Only a result that does not fit traps: a result equal to the maximum or minimum is a value.",
     [REF_TRAP, REF_UNSIGNED_TRAP],
     "run:0",
     main_("""    if ((raw v32(2147483646i32) + raw v32(1i32)) != 2147483647i32) { exit 10i32; }
    int32:mn = raw v32(-2147483647i32) - raw v32(1i32);
    if ((mn + raw v32(1i32)) != -2147483647i32) { exit 11i32; }
    int8:m8 = raw v8(-127i8) - raw v8(1i8);
    if ((m8 + raw v8(127i8)) != -1i8) { exit 12i32; }
    if ((raw vu8(254u8) + raw vu8(1u8)) != 255u8) { exit 13i32; }
    if ((raw v64(-3037000499i64) * raw v64(3037000499i64)) != -9223372030926249001i64) { exit 14i32; }
    if ((raw vu64(4294967295u64) * raw vu64(4294967297u64)) != ~0u64) { exit 15i32; }
    exit 0i32;"""),
     wrong="a guard off by one traps at the edge (93)")

item("o18_shift_loses_bits_no_trap", AREA_O,
     "an in-range shift that loses bits",
     "Bit operations are not arithmetic and have nothing to overflow: `<<` loses the bits past "
     "its width (`1i8 << 7i8` is -128).",
     [("TYPE", "**Bit operations are unchanged** — `&`, `|`, `^`, `~`, `<<`, `>>` are bit"),
      ("OP", "`<<` loses the bits past its width (`1i8 << 7i8` is −128)")],
     "run:0",
     main_("""    int8:m8 = raw v8(-127i8) - raw v8(1i8);
    if ((raw v8(64i8) << raw v8(1i8)) != m8) { exit 10i32; }
    if ((raw vu32(4294967295u32) << raw vu32(4u32)) != 4294967280u32) { exit 11i32; }
    if ((raw v32(1i32) << raw v32(31i32)) != raw v32(-2147483647i32) - raw v32(1i32)) { exit 12i32; }
    exit 0i32;"""),
     wrong="an overflow trap on a shift (93)")

item("o19_wrapping_family", AREA_O,
     "`+% -% *%` at run time",
     "The wrapping family computes modulo 2^N: the result is the low N bits, always.",
     [("TYPE", "4): `+%`, `-%`, `*%`, with the compound forms `+%=`, `-%=`, `*%=`. The result"),
      ("TYPE", "is the low N bits, always; there is no guard, no obligation row and no")],
     "run:0",
     main_("""    if ((raw vu8(255u8) +% raw vu8(1u8)) != 0u8) { exit 10i32; }
    if ((raw vu8(0u8) -% raw vu8(1u8)) != 255u8) { exit 11i32; }
    int8:mn = raw v8(-127i8) - raw v8(1i8);
    if ((raw v8(127i8) +% raw v8(1i8)) != mn) { exit 12i32; }
    if ((raw vu32(4000000000u32) *% raw vu32(2u32)) != 3705032704u32) { exit 13i32; }
    if ((raw v32(-2147483647i32) -% raw v32(2i32)) != 2147483647i32) { exit 14i32; }
    uint32:h = raw vu32(4000000000u32);
    h +%= raw vu32(500000000u32);
    if (h != 205032704u32) { exit 15i32; }
    exit 0i32;"""),
     wrong="a trap (93) or a saturation (the check's code)")

item("o20_wrapping_folds_with_wrap", AREA_O,
     "`+% -% *%` folded as constants",
     "A constant wrap folds WITH the wrap.",
     [("OP", "IEEE. A constant wrap folds WITH the wrap, where the trapping twin would be")],
     "run:0",
     main_("""    if (W1 != 0u8) { exit 10i32; }
    if (W2 != 2147483647i32) { exit 11i32; }
    if (W3 != 3705032704u32) { exit 12i32; }
    exit 0i32;""", """fixed uint8:W1 = 255u8 +% 1u8;
fixed int32:W2 = -2147483647i32 -% 2i32;
fixed uint32:W3 = 4000000000u32 *% 2u32;"""),
     wrong="a constant folded as the trapping twin (refused TYPE-076) or saturated (the check's code)")

item("o21_constant_overflow_refused", AREA_O,
     "`2147483647i32 + 1i32` as a constant",
     "A folded `+ - *` whose value does not fit is NITPICK-TYPE-076 where it is written.",
     [("OP", "**A value that does not fit is `NITPICK-TYPE-076`**")],
     "refuse:NITPICK-TYPE-076",
     main_("""    int32:x = 2147483647i32 + 1i32;
    if (x < 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: folded with a wrap (exit 10)")

item("o22_simd_lane_overflow", AREA_O,
     "an int32 `simd` lane `+` past the maximum",
     "A `simd`'s integer lanes trap as their scalar does.",
     [("TYPE", "A `simd`'s integer lanes go through the vector form `.<N x iW>`, the"),
      ("OP", "scalar does since 1.5.4e (D-284)")],
     "run:93",
     main_("""    simd<int32, 4>:v = simd(raw v32(2147483647i32), 1i32, 2i32, 3i32);
    simd<int32, 4>:w = simd(1i32, 1i32, 1i32, 1i32);
    simd<int32, 4>:s = v + w;
    if (s[0i64] < 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="the lane wraps to a negative value (exit 10), DEF-38's shape")

# ------------------------------------------------------------ V division
AREA_V = "division"

item("v01_truncation_run_time", AREA_V,
     "`/` and `%` on negative int32 operands at run time",
     "Signed `/` is `sdiv` and `%` is `srem`: the quotient truncates toward zero and the "
     "remainder takes the dividend's sign.",
     [("TYPE", "| `/` | divide | `sdiv`/`fdiv` | div-by-zero → failsafe |"),
      ("TYPE", "| `%` | remainder | `srem`/`frem` | |")],
     "run:0",
     main_("""    int32:a = raw v32(-7i32);
    int32:b = raw v32(2i32);
    if ((a / b) != -3i32) { exit 10i32; }
    if ((raw v32(7i32) / raw v32(-2i32)) != -3i32) { exit 11i32; }
    if ((a % b) != -1i32) { exit 12i32; }
    if ((raw v32(7i32) % raw v32(-2i32)) != 1i32) { exit 13i32; }
    exit 0i32;"""),
     wrong="floor division: -4 (10, 11) and a divisor-signed remainder 1 / -1 (12, 13)",
     note="The references state the lowering (`sdiv`, `srem`), not a rounding rule in words; "
          "the expected values are those instructions' semantics.")

item("v02_truncation_folded", AREA_V,
     "`/` and `%` on negative constants, folded",
     "A constant expression means what the run time means: the folder divides as `sdiv` does.",
     [("OP", "**A constant expression means what the run time means (D-310, D-311; 1.5.8b"),
      ("OP", "- Every other operation the folder evaluates is also the machine's answer:")],
     "run:0",
     main_("""    if (Q1 != -3i32) { exit 10i32; }
    if (Q2 != -3i32) { exit 11i32; }
    if (R1 != -1i32) { exit 12i32; }
    if (R2 != 1i32) { exit 13i32; }
    exit 0i32;""", """fixed int32:Q1 = -7i32 / 2i32;
fixed int32:Q2 = 7i32 / -2i32;
fixed int32:R1 = -7i32 % 2i32;
fixed int32:R2 = 7i32 % -2i32;"""),
     wrong="a folder that floors, or rounds (the check's code)")


def trap_div(iid, title, body, code, refs, wrong):
    claim = {97: "Integer `/` and `%` by zero trap `DivByZero`, at every width and in both "
                 "spellings (`/`, `/=`).",
             98: "A signed minimum divided by -1 traps `DivOverflow`, at every width; the run "
                 "time traps `MIN % -1` too."}[code]
    item(iid, AREA_V, title, claim, refs, "run:%d" % code, main_(body + "\n    exit 11i32;"), wrong=wrong)


REF_DIV0 = ("TYPE", "**`/` and `%` by zero still trap** (D-007), and signed `/` adds the")
REF_MOD_SAME = ("OP", "| `%` | Modulo | Remainder operation. Same divide-by-zero rule as `/`. |")
trap_div("v03_div_by_zero", "`/` by a run-time zero",
         "    int32:q = raw v32(1i32) / raw v32(0i32);\n    if (q == 0i32) { exit 10i32; }",
         97, [REF_DIV0], "no trap: a hardware fault (107) or a value (10)")
trap_div("v04_rem_by_zero", "`%` by a run-time zero",
         "    int32:q = raw v32(1i32) % raw v32(0i32);\n    if (q == 0i32) { exit 10i32; }",
         97, [REF_DIV0, REF_MOD_SAME], "no trap: a hardware fault (107) or a value (10)")
trap_div("v05_min_div_minus_one", "int32 minimum `/` -1",
         "    int32:m = raw v32(-2147483647i32) - raw v32(1i32);\n"
         "    int32:q = m / raw v32(-1i32);\n    if (q < 0i32) { exit 10i32; }",
         98, [REF_DIV0, ("BUILTIN", "−4098 INT_MIN_OVERFLOW")],
         "no trap: SIGFPE (107) or the minimum back (10)")
trap_div("v06_min_rem_minus_one", "int32 minimum `%` -1",
         "    int32:m = raw v32(-2147483647i32) - raw v32(1i32);\n"
         "    int32:q = m % raw v32(-1i32);\n    if (q == 0i32) { exit 10i32; }",
         98, [("OP", "a constant `MIN / −1` or `MIN % −1` is refused as a constant division by"),
              ("OP", "zero is (TYPE-004), since the run time traps `DivOverflow`.")],
         "the mathematical 0 with no trap (10), or SIGFPE (107)")
trap_div("v07_int8_min_div_minus_one", "int8 minimum `/` -1",
         "    int8:m = raw v8(-127i8) - raw v8(1i8);\n"
         "    int8:q = m / raw v8(-1i8);\n    if (q < 0i8) { exit 10i32; }",
         98, [("TYPE", "structural INT_MIN/−1 check, which is width-independent by construction).")],
         "computed wider: 128 truncates back to -128 with no trap (10)")
trap_div("v08_int64_min_div_minus_one", "int64 minimum `/` -1",
         "    int64:m = raw v64(-9223372036854775807i64) - raw v64(1i64);\n"
         "    int64:q = m / raw v64(-1i64);\n    if (q < 0i64) { exit 10i32; }",
         98, [REF_DIV0], "no trap: SIGFPE (107)")
trap_div("v09_unsigned_div_by_zero", "uint32 `/` by a run-time zero",
         "    uint32:q = raw vu32(7u32) / raw vu32(0u32);\n    if (q == 0u32) { exit 10i32; }",
         97, [REF_DIV0], "no trap: a hardware fault (107)")
trap_div("v10_compound_div_by_zero", "`/=` by a run-time zero",
         "    int32:x = raw v32(5i32);\n    x /= raw v32(0i32);\n    if (x == 0i32) { exit 10i32; }",
         97, [("TYPE", "**`x += y` traps identically**: both spellings route through one arithmetic"), REF_DIV0],
         "the compound spelling reaches the hardware: SIGFPE (107)")
trap_div("v11_compound_rem_by_zero", "`%=` by a run-time zero",
         "    int32:x = raw v32(5i32);\n    x %= raw v32(0i32);\n    if (x == 0i32) { exit 10i32; }",
         97, [("TYPE", "**`x += y` traps identically**: both spellings route through one arithmetic"), REF_DIV0],
         "the compound spelling reaches the hardware: SIGFPE (107)")

item("v12_constant_div_by_zero", AREA_V,
     "`5i32 / 0i32` as a constant",
     "A constant division by zero is refused (TYPE-004).",
     [("OP", "a constant `MIN / −1` or `MIN % −1` is refused as a constant division by")],
     "refuse:NITPICK-TYPE-004",
     main_("""    int32:x = 5i32 / 0i32;
    if (x == 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a run-time trap (97) or a folded value (10)")

item("v13_constant_min_div_minus_one", AREA_V,
     "the int32 minimum `/` -1 as a constant",
     "A constant `MIN / -1` is refused as a constant division by zero is.",
     [("OP", "a constant `MIN / −1` or `MIN % −1` is refused as a constant division by")],
     "refuse:NITPICK-TYPE-004",
     main_("""    if (Z < 0i32) { exit 10i32; }
    exit 11i32;""", "fixed int32:Z = (-2147483647i32 - 1i32) / -1i32;"),
     wrong="accepted: folded to the minimum (exit 10)")

item("v14_unsigned_div_rem", AREA_V,
     "unsigned `/` and `%` on high values at run time",
     "Unsigned division and remainder use `udiv`/`urem`.",
     [("TYPE", "Division/modulo use `udiv`/`urem` instead of `sdiv`/`srem`")],
     "run:0",
     main_("""    if ((raw vu32(4294967294u32) / raw vu32(2u32)) != 2147483647u32) { exit 10i32; }
    if ((raw vu32(4294967295u32) % raw vu32(10u32)) != 5u32) { exit 11i32; }
    if ((raw vu8(200u8) / raw vu8(3u8)) != 66u8) { exit 12i32; }
    if ((raw vu64(~0u64) / raw vu64(2u64)) != 9223372036854775807u64) { exit 13i32; }
    if ((raw vu16(65535u16) % raw vu16(256u16)) != 255u16) { exit 14i32; }
    exit 0i32;"""),
     wrong="signed division on the bit pattern: -2/2 = -1 (10), -1%10 = -1 (11)")

item("v15_unsigned_div_rem_folded", AREA_V,
     "unsigned `/` and `%` on high values, folded",
     "The folder divides and takes remainders UNSIGNED for an unsigned type.",
     [("OP", "a `uint64` divides, takes remainders, shifts right and orders UNSIGNED;")],
     "run:0",
     main_("""    if (U1 != 9223372036854775807u64) { exit 10i32; }
    if (U2 != 5u32) { exit 11i32; }
    if (U3 != 66u8) { exit 12i32; }
    exit 0i32;""", """fixed uint64:U1 = ~0u64 / 2u64;
fixed uint32:U2 = 4294967295u32 % 10u32;
fixed uint8:U3 = 200u8 / 3u8;"""),
     wrong="a signed fold (the check's code)")

item("v16_float_div_by_zero", AREA_V,
     "`flt64` division by zero",
     "Float division is total: division by zero yields an infinity, with no trap.",
     [("TYPE", "- **Total, no traps**: division by zero yields ±inf/nan per IEEE — defined")],
     "run:0",
     main_("""    flt64:z = raw vf64(0.0f64);
    flt64:q = raw vf64(1.0f64) / z;
    if (!(q > 1.0e308f64)) { exit 10i32; }
    flt64:n = raw vf64(-1.0f64) / z;
    if (!(n < -1.0e308f64)) { exit 11i32; }
    exit 0i32;"""),
     wrong="a DivByZero trap (97) on a float")

item("v17_float_remainder", AREA_V,
     "`flt64` `%`",
     "Float `%` is `frem`, lowered to the floor's exact `fmod`: the result takes the dividend's sign.",
     [("TYPE", "(`frem` lowers to the runtime floor's hand-written, exact `fmod`/`fmodf`)")],
     "run:0",
     main_("""    flt64:b = raw vf64(2.0f64);
    if ((raw vf64(5.5f64) % b) != 1.5f64) { exit 10i32; }
    if ((raw vf64(-5.5f64) % b) != -1.5f64) { exit 11i32; }
    flt64:c = raw vf64(5.0f64) % raw vf64(0.0f64);
    if (!(c != c)) { exit 12i32; }
    exit 0i32;"""),
     wrong="a floored remainder 0.5 (11), or a trap on the zero divisor (97)")

item("v18_tbb_div_by_zero_is_err", AREA_V,
     "`tbb32` `/` and `%` by zero",
     "On `tbb`, division or modulo by zero yields ERR, with no trap.",
     [("TYPE", "- Division or modulo by zero yields ERR (D-007).")],
     "run:0",
     main_("""    tbb32:a = raw vt32(5tbb32);
    tbb32:q = a / raw vt32(0tbb32);
    if (!(is_err(q))) { exit 10i32; }
    tbb32:r = a % raw vt32(0tbb32);
    if (!(is_err(r))) { exit 11i32; }
    exit 0i32;"""),
     wrong="a DivByZero trap (97), or a non-ERR value (10, 11)")

# ------------------------------------------------------------ S shifts
AREA_S = "shifts"

item("s01_signed_right_shift_arithmetic", AREA_S,
     "`>>` on a negative signed value",
     "`>>` is arithmetic on a signed operand.",
     [("TYPE", "Arithmetic on a SIGNED operand, logical on an UNSIGNED one — the operand's")],
     "run:0",
     main_("""    if ((raw v32(-8i32) >> raw v32(1i32)) != -4i32) { exit 10i32; }
    int8:m8 = raw v8(-127i8) - raw v8(1i8);
    if ((m8 >> raw v8(7i8)) != -1i8) { exit 11i32; }
    if ((raw v64(-1i64) >> raw v64(63i64)) != -1i64) { exit 12i32; }
    exit 0i32;"""),
     wrong="a logical shift on a signed value (the check's code)")

item("s02_unsigned_right_shift_logical", AREA_S,
     "`>>` on unsigned values with the high bit set",
     "`>>` is logical on an unsigned operand.",
     [("TYPE", "Right shift uses `lshr` (logical) instead of `ashr` (arithmetic)")],
     "run:0",
     main_("""    if ((raw vu32(2147483648u32) >> raw vu32(31u32)) != 1u32) { exit 10i32; }
    if ((raw vu8(128u8) >> raw vu8(7u8)) != 1u8) { exit 11i32; }
    if ((raw vu64(~0u64) >> raw vu64(63u64)) != 1u64) { exit 12i32; }
    if ((raw vu16(65535u16) >> raw vu16(8u16)) != 255u16) { exit 13i32; }
    exit 0i32;"""),
     wrong="an arithmetic shift on the bit pattern: all ones (the check's code)")

item("s03_shifts_folded", AREA_S,
     "`<<`, `>>` and `~` folded as constants",
     "The folder shifts as the machine does: `1i8 << 7i8` is -128, `~5u8` is 250, an unsigned "
     "`>>` is logical.",
     [("OP", "`<<` loses the bits past its width (`1i8 << 7i8` is −128)"),
      ("OP", "- `~5u8` is 250;"),
      ("OP", "a `uint64` divides, takes remainders, shifts right and orders UNSIGNED;")],
     "run:0",
     main_("""    int8:m8 = raw v8(-127i8) - raw v8(1i8);
    if (F1 != m8) { exit 10i32; }
    if (F2 != 250u8) { exit 11i32; }
    if (F3 != 9223372036854775807u64) { exit 12i32; }
    if (F4 != -4i32) { exit 13i32; }
    if (F5 != 1u32) { exit 14i32; }
    exit 0i32;""", """fixed int8:F1 = 1i8 << 7i8;
fixed uint8:F2 = ~5u8;
fixed uint64:F3 = ~0u64 >> 1u64;
fixed int32:F4 = -8i32 >> 1i32;
fixed uint32:F5 = 2147483648u32 >> 31u32;"""),
     wrong="a folder that computes wider, or signed (the check's code)")

REF_SHIFT_RT = ("OP", "amount is checked at run time by one unsigned compare on its carrier (a")
item("s04_shift_amount_equals_width", AREA_S,
     "`<<` by a run-time amount equal to the width",
     "A computed shift amount outside `0 <= n < width` traps `ShiftRange`.",
     [("TYPE", "for `0 ≤ n < width(x)` only — a known amount outside it is TYPE-070 at"), REF_SHIFT_RT],
     "run:111",
     main_("""    int32:x = raw v32(1i32) << raw v32(32i32);
    if (x == 1i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="the hardware's masked shift gives 1 (exit 10), LLVM poison gives anything (11)")

item("s05_shift_amount_negative", AREA_S,
     "`<<` by a negative run-time amount",
     "A negative computed amount reads as huge and traps `ShiftRange`.",
     [("OP", "negative amount reads as huge) and traps `ShiftRange` (−4115), which the")],
     "run:111",
     main_("""    int32:x = raw v32(1i32) << raw v32(-1i32);
    if (x == 0i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="a masked or saturated shift (10 or 11)")

item("s06_right_shift_amount_width", AREA_S,
     "`>>` by a run-time amount equal to the width",
     "The amount rule is `>>`'s too.",
     [("TYPE", "operations, not arithmetic, and have nothing to overflow. **A shift's"),
      ("TYPE", "AMOUNT is checked** (D-277, 1.5.4b): `x << n` and `x >> n` are defined")],
     "run:111",
     main_("""    uint8:x = raw vu8(128u8) >> raw vu8(8u8);
    if (x == 0u8) { exit 10i32; }
    exit 11i32;"""),
     wrong="a saturated 0 (exit 10)")

item("s07_shift_literal_amount_refused", AREA_S,
     "`<<` by the literal amount 32 on an int32",
     "A known amount outside the range is NITPICK-TYPE-070 at the shift.",
     [("OP", "(D-277, 1.5.4b).** A known amount outside the range — a literal, a negated"),
      ("OP", "literal, a `fixed` constant the folder knows — is `NITPICK-TYPE-070` at the")],
     "refuse:NITPICK-TYPE-070",
     main_("""    int32:x = raw v32(1i32) << 32i32;
    if (x == 1i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a masked or poison shift (10 or 11)")

item("s08_compound_shift_amount", AREA_S,
     "`<<=` by an out-of-range run-time amount",
     "The amount check covers the compound spellings `<<=` and `>>=`.",
     [("OP", "shift, both operators and the compound spellings `<<=`/`>>=`; a computed")],
     "run:111",
     main_("""    int32:x = raw v32(1i32);
    x <<= raw v32(40i32);
    if (x == 256i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="the compound spelling unguarded: x86 masks 40 to 8 (exit 10)")

item("s09_bitwise_not", AREA_S,
     "`~` at run time",
     "`~` inverts every bit (`xor -1`).",
     [("TYPE", "| `~` | bitwise NOT | `xor %v, -1` | |")],
     "run:0",
     main_("""    if ((~raw v32(0i32)) != -1i32) { exit 10i32; }
    if ((~raw vu8(5u8)) != 250u8) { exit 11i32; }
    if ((~raw vu64(0u64)) != ~0u64) { exit 12i32; }
    exit 0i32;"""),
     wrong="a logical not, or a wider result truncated wrongly (the check's code)")

# ------------------------------------------------------------ M comparisons
AREA_M = "comparisons"
REF_NO_WIDEN = ("DECISIONS", "**Two typed operands share a type or the programmer writes the cast.** Widening")

item("m01_mixed_width_refused", AREA_M,
     "`int32 < int64`",
     "Two typed operands share a type or the program writes the cast: no implicit widening, "
     "for any operator.",
     [REF_NO_WIDEN],
     "refuse",
     main_("""    int32:a = raw v32(1i32);
    int64:b = raw v64(4294967296i64);
    if (a < b) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: an implicit widening, or a truncating compare (11)")

item("m02_mixed_sign_refused", AREA_M,
     "`int32 == uint32`",
     "Operands of different signedness are refused.",
     [REF_NO_WIDEN, ("DECISIONS", "int32:e; uint32:f;     e + f                 // REFUSED")],
     "refuse",
     main_("""    int32:a = raw v32(-1i32);
    uint32:b = raw vu32(4294967295u32);
    if (a == b) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a bit-pattern compare calls -1 equal to 4294967295 (exit 10)")

item("m03_unsigned_ordering", AREA_M,
     "`<`/`>` on unsigned values with the high bit set",
     "Unsigned comparisons use `ult`/`ugt`/`ule`/`uge`.",
     [("TYPE", "Comparisons use `ult`/`ugt`/`ule`/`uge` instead of `slt`/`sgt`/`sle`/`sge`")],
     "run:0",
     main_("""    if (!(raw vu8(200u8) > raw vu8(100u8))) { exit 10i32; }
    if (!(raw vu32(4294967295u32) > raw vu32(1u32))) { exit 11i32; }
    uint64:d = (raw vu64(1u64) << raw vu64(63u64)) | raw vu64(5u64);
    if (!(d > raw vu64(9223372036854775807u64))) { exit 12i32; }
    if (raw vu16(40000u16) < raw vu16(1u16)) { exit 13i32; }
    if (!(raw vu8(255u8) >= raw vu8(128u8))) { exit 14i32; }
    exit 0i32;"""),
     wrong="a signed compare on the bit pattern (the check's code)")

item("m04_unsigned_ordering_folded", AREA_M,
     "unsigned comparisons folded as constants",
     "The folder orders an unsigned type UNSIGNED.",
     [("OP", "a `uint64` divides, takes remainders, shifts right and orders UNSIGNED;")],
     "run:0",
     main_("""    if (!B1) { exit 10i32; }
    if (!B2) { exit 11i32; }
    if (B3) { exit 12i32; }
    exit 0i32;""", """fixed bool:B1 = 200u8 > 100u8;
fixed bool:B2 = ~0u64 > 1u64;
fixed bool:B3 = 4294967295u32 < 7u32;"""),
     wrong="a signed fold (the check's code)")

item("m05_char_ordering_unsigned", AREA_M,
     "`char8` ordering with a byte above 0x7F",
     "`char8` comparisons are unsigned (`icmp ult/ugt/...`).",
     [("TYPE", "- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=` → `icmp eq/ne/ult/ugt/ule/uge` (unsigned comparison for Unicode ordering)")],
     "run:0",
     main_("""    char8:hi = raw vc8('\\xC3');
    char8:a = raw vc8('A');
    if (!(hi > a)) { exit 10i32; }
    if (hi < a) { exit 11i32; }
    exit 0i32;"""),
     wrong="a signed byte compare: 0xC3 as -61 is below 'A' (exit 10)")

item("m06_spaceship", AREA_M,
     "`<=>` on signed and unsigned values",
     "`<=>` yields an int32: -1, 0 or 1.",
     [("OP", "- **`<=>`** (spaceship) yields `int32`: `-1`, `0`, or `1`.")],
     "run:0",
     main_("""    if ((raw v32(-5i32) <=> raw v32(3i32)) != -1i32) { exit 10i32; }
    if ((raw v32(3i32) <=> raw v32(3i32)) != 0i32) { exit 11i32; }
    if ((raw v32(7i32) <=> raw v32(3i32)) != 1i32) { exit 12i32; }
    if ((raw vu64(~0u64) <=> raw vu64(1u64)) != 1i32) { exit 13i32; }
    if ((raw vu8(200u8) <=> raw vu8(100u8)) != 1i32) { exit 14i32; }
    exit 0i32;"""),
     wrong="a signed order for the unsigned pair (13, 14), or a difference instead of -1/0/1 (10, 12)")

item("m07_nan_comparisons", AREA_M,
     "`==`, `!=`, `<` with a NaN operand",
     "Float comparisons are ordered, except `!=`, which is `une`, so NaN != NaN is true.",
     [("TYPE", "- Comparison: `fcmp` ordered predicates, except `!=` which is `une` so that"),
      ("TYPE", "| `!=` | not equal | `icmp ne`/`fcmp one` | |")],
     "run:0",
     main_("""    flt64:z = raw vf64(0.0f64);
    flt64:n = z / z;
    if (!(n != n)) { exit 10i32; }
    if (n == n) { exit 11i32; }
    if (n < raw vf64(1.0f64)) { exit 12i32; }
    if (n > raw vf64(1.0f64)) { exit 13i32; }
    exit 0i32;"""),
     wrong="`!=` lowered as the ordered `one`: NaN != NaN is false (exit 10)",
     note="TYPE_REFERENCE contradicts itself: §1.4 says `!=` is `une`, §28's table says "
          "`fcmp one`. The expectation follows §1.4, which states the property; the run shows "
          "which sentence the compiler follows.")

item("m08_negative_zero", AREA_M,
     "`-(0.0)`",
     "Float negation is `fneg`: -(0.0) is -0.0, equal to 0.0 and of negative sign.",
     [("TYPE", "- Negation is `fneg` (sign-bit exact: `-(0.0)` is `-0.0`)")],
     "run:0",
     main_("""    flt64:z = raw vf64(0.0f64);
    flt64:nz = -z;
    if (!(nz == z)) { exit 10i32; }
    flt64:inv = raw vf64(1.0f64) / nz;
    if (!(inv < raw vf64(0.0f64))) { exit 11i32; }
    exit 0i32;"""),
     wrong="negation as `0.0 - x` gives +0.0, so 1/-0.0 is +inf (exit 11)")

item("m09_char_vs_uint8_refused", AREA_M,
     "`char8 == uint8`",
     "`char8` and `uint8` are distinct types; two typed operands must share a type.",
     [("TYPE", "> **Note:** `uint8` and `char8` share the same LLVM IR type (`i8`) but are **semantically distinct**."),
      REF_NO_WIDEN],
     "refuse",
     main_("""    char8:c = raw vc8('A');
    uint8:u = raw vu8(65u8);
    if (c == u) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a byte compare (exit 10)")

item("m10_bool_ordering_refused", AREA_M,
     "`true > false`",
     "`bool` has `==` and `!=` and no ordering.",
     [("TYPE", "^- Comparison: `==`, `!=`")],
     "refuse",
     main_("""    if (raw vb(true) > raw vb(false)) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: an integer order on the byte (exit 10)",
     note="Inferred from a closed list: §1.1 lists `==`/`!=` as bool's comparisons and states "
          "no ordering; it does not say the ordering is refused in words.")

item("m11_string_eq_refused", AREA_M,
     "`==` on strings",
     "`==` and `!=` are refused on a `string` (TYPE-034).",
     [("TYPE", "byte-by-byte. **`==` and `!=` are REFUSED on a `string`** (`NITPICK-TYPE-034`;")],
     "refuse:NITPICK-TYPE-034",
     main_("""    string:a = "x";
    if (a == "x") { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: a pointer or byte compare (10 or 11)")

item("m12_tbb_compare_on_err_traps", AREA_M,
     "a comparison of a `tbb8` holding ERR",
     "Comparing or branching on ERR traps to failsafe.",
     [("TYPE", "- **Comparison or branching on ERR traps to `failsafe`** — `bool` has exactly two"),
      ("OP", "branching on an ERR value traps to `failsafe`**. ERR flows freely through data")],
     "run:110",
     main_("""    tbb8:a = raw vt8(127tbb8) + raw vt8(1tbb8);
    if (a == raw vt8(0tbb8)) { exit 10i32; }
    exit 11i32;"""),
     wrong="no trap: ERR compared as -128 (exit 11)",
     note="Run 1 spelled the comparison `a > 0`: refused `TYPE-008`, since ordering on tbb is "
          "a compile error (D-093; error codes are compared, not sorted). The claim is about "
          "the ERR trap, so the program now compares with `==` (S36); the expectation is unchanged.")

item("m13_tbb_err_sticky", AREA_M,
     "ERR through `+`, `*` by 0, `-` of itself, and underflow",
     "Overflow saturates to ERR, any operation on ERR yields ERR (`ERR * 0` and `ERR - ERR` "
     "included), and `is_err` tests without trapping.",
     [("TYPE", "- **Any operation on an ERR value yields ERR.** This overrides mathematical"),
      ("TYPE", "- Overflow **saturates to ERR** rather than wrapping. Out-of-range results land")],
     "run:0",
     main_("""    tbb8:a = raw vt8(127tbb8) + raw vt8(1tbb8);
    if (!(is_err(a))) { exit 10i32; }
    tbb8:b = a * raw vt8(0tbb8);
    if (!(is_err(b))) { exit 11i32; }
    tbb8:c = a - a;
    if (!(is_err(c))) { exit 12i32; }
    tbb8:d = raw vt8(-127tbb8) - raw vt8(1tbb8);
    if (!(is_err(d))) { exit 13i32; }
    exit 0i32;"""),
     wrong="an identity erasing ERR: `ERR * 0` as 0 (11), `ERR - ERR` as 0 (12)")

# ------------------------------------------------------------ T strings
AREA_T = "string lengths and bounds"

item("t01_byte_length_utf8", AREA_T,
     "the length of a string holding a two-byte UTF-8 character",
     "A `string`'s length counts char units, which for `string` (`string<char8>`) are bytes; "
     "`string_byte_length` is the byte length.",
     [("TYPE", ";   Field 1: i64   — length (number of char units, NOT bytes for char16/32)"),
      ("BUILTIN", "| `string_byte_length` | `string → int64` | Folds at comptime.")],
     "run:0",
     main_("""    string:s = "héllo";
    if (string_byte_length(s) != 6i64) { exit 10i32; }
    if (s.len != 6i64) { exit 11i32; }
    exit 0i32;"""),
     wrong="a code-point count, 5 (10, 11)")

item("t02_length_spelled_length", AREA_T,
     "`s.length`",
     "TYPE_REFERENCE §3.2 spells a string's length `s.length`, a field access.",
     [("TYPE", "- Length: `int64:len = s.length;` → field access")],
     "run:0",
     main_("""    string:s = "hello";
    if (s.length != 5i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="the documented spelling refused, or a wrong length (exit 10)")

item("t03_escapes_and_raw", AREA_T,
     "the length of escaped and raw literals",
     "An escape is one character (`\\n`, `\\0`, `\\x41`); a raw string performs no escape processing.",
     [("LEXICAL", "EscapeSequence     ::= \"\\\" (\"n\" | \"r\" | \"t\" | \"\\\" | '\"' | \"'\" | \"0\""),
      ("LEXICAL", "> `RawStringLiteral` performs **no** escape processing.")],
     "run:0",
     main_(r"""    if (string_byte_length("a\nb") != 3i64) { exit 10i32; }
    if (string_byte_length("a\0b") != 3i64) { exit 11i32; }
    if (!(string_equals("\x41", "A"))) { exit 12i32; }
    if (string_byte_length(r"a\nb") != 4i64) { exit 13i32; }
    if (string_byte_length("\t\\\"") != 3i64) { exit 14i32; }
    exit 0i32;"""),
     wrong="an escape kept as two bytes (10), a NUL ending the literal (11), a raw string escaped (13)")

item("t04_block_string_quotes", AREA_T,
     "a block string holding `\"` and `\"\"`",
     "A block string ends at the FIRST `\"\"\"`; a `\"` or `\"\"` inside the body is body text; "
     "newlines are preserved verbatim.",
     [("LEXICAL", "BlockStringLiteral ::= '\"\"\"' (SourceCharacter - '\"\"\"')* '\"\"\"'"),
      ("LEXICAL", "or a `\"\"` inside the body is body text, as the production says (the lexer closed on")],
     "run:0",
     main_('''    string:a = """ab"c""";
    if (string_byte_length(a) != 4i64) { exit 10i32; }
    string:b = """a""b""";
    if (string_byte_length(b) != 4i64) { exit 11i32; }
    string:c = """x
y""";
    if (string_byte_length(c) != 3i64) { exit 12i32; }
    exit 0i32;'''),
     wrong="the literal closed at `\"\"` (DEF-98's shape: a parse error, or 11)",
     note="At the baseline this is DEF-98 (fixed at 1.6.0 step 3e, `395308f`); its reference's "
          "production already said three quotes, so the expectation is the same at both.")

item("t05_slice_half_open", AREA_T,
     "`string_slice` of [1, 3) and of an empty range",
     "`string_slice(s, lo, hi)` is byte-indexed and half-open, an owned copy; an empty slice is empty.",
     [("BUILTIN", "| `string_slice` | `(string, int64:lo, int64:hi) → Result<string>` | Byte-indexed, half-open")],
     "run:0",
     main_("""    string:s = "hello";
    string:t = string_slice(s, raw v64(1i64), raw v64(3i64)) ?| "X";
    if (!(string_equals(t, "el"))) { exit 10i32; }
    string:u = string_slice(s, raw v64(5i64), raw v64(5i64)) ?| "X";
    if (u.len != 0i64) { exit 11i32; }
    exit 0i32;"""),
     wrong="an inclusive end, \"ell\" (10), or an error for the empty slice (11)")

item("t06_slice_out_of_range", AREA_T,
     "`string_slice` with lo > hi, hi > len, or lo < 0",
     "A slice out of range is an error (the floor's code -34), not a clamp.",
     [("BUILTIN", "reuse that vocabulary — an interior NUL is −22, a slice out of range −34 — and"),
      ("BUILTIN", "| `string_slice` | `(string, int64:lo, int64:hi) → Result<string>` | Byte-indexed, half-open")],
     "run:0",
     main_("""    string:s = "hello";
    Result<string>:a = string_slice(s, raw v64(3i64), raw v64(1i64));
    if (!a.is_error) { exit 10i32; }
    Result<string>:b = string_slice(s, raw v64(0i64), raw v64(6i64));
    if (!b.is_error) { exit 11i32; }
    Result<string>:c = string_slice(s, raw v64(-1i64), raw v64(2i64));
    if (!c.is_error) { exit 12i32; }
    exit 0i32;"""),
     wrong="a clamped or empty success (the check's code), or a read past the end")

item("t07_bytes_view_bounds", AREA_T,
     "`string_bytes(s)[len]`",
     "`string_bytes` is the bytes as a slice, and slice indexing is bounds-checked against the "
     "run-time length.",
     [("BUILTIN", "| `string_bytes` | `string → uint8[]` | **The string→slice bridge**"),
      ("TYPE", "- **Indexing is bounds-checked against the runtime `len`**, trapping to")],
     "run:94",
     main_("""    string:s = "abc";
    uint8[]:b = string_bytes(s);
    if (b.len != 3i64) { exit 10i32; }
    if (b[raw v64(1i64)] != 98u8) { exit 11i32; }
    uint8:x = b[raw v64(3i64)];
    if (x == 0u8) { exit 12i32; }
    exit 13i32;"""),
     wrong="no bounds check: the byte past the end is read (12 or 13)")

item("t08_string_index", AREA_T,
     "`s[i]` on a string",
     "Indexing a string returns the char at that index, bounds-checked.",
     [("TYPE", "- Indexing: `char8:c = s[0];` → returns the char at that index (bounds-checked)")],
     "run:0",
     main_("""    string:s = "hello";
    char8:c = s[raw v64(1i64)];
    if (c != 'e') { exit 10i32; }
    exit 0i32;"""),
     wrong="the documented indexing refused, or the wrong char (exit 10)")

item("t09_string_index_past_end", AREA_T,
     "`s[len]` on a string",
     "String indexing is bounds-checked.",
     [("TYPE", "- Indexing: `char8:c = s[0];` → returns the char at that index (bounds-checked)")],
     "run:94",
     main_("""    string:s = "hello";
    char8:c = s[raw v64(5i64)];
    if (c == 'x') { exit 10i32; }
    exit 11i32;"""),
     wrong="no bounds check (10 or 11), or indexing refused")

item("t10_int_to_string", AREA_T,
     "`int_to_string` of -42, 0, the int64 minimum and maximum",
     "`int_to_string` renders any int64 in decimal and never fails.",
     [("BUILTIN", "| `int_to_string` | `int64 → string` | Decimal rendering.")],
     "run:0",
     main_("""    if (!(string_equals(int_to_string(raw v64(-42i64)), "-42"))) { exit 10i32; }
    if (!(string_equals(int_to_string(raw v64(0i64)), "0"))) { exit 11i32; }
    int64:mn = raw v64(-9223372036854775807i64) - raw v64(1i64);
    if (!(string_equals(int_to_string(mn), "-9223372036854775808"))) { exit 12i32; }
    if (!(string_equals(int_to_string(raw v64(9223372036854775807i64)), "9223372036854775807"))) { exit 13i32; }
    exit 0i32;"""),
     wrong="the minimum negated before rendering: an overflow trap (93) or garbage (12)")

item("t11_template_interpolation", AREA_T,
     "a template interpolating a negative int64 and an expression",
     "A template literal interpolates the value of each `&{ }` expression.",
     [("OP", "| `&{ }` | Interpolation | Evaluates and interpolates an expression inside a template."),
      ("LEXICAL", "Backtick-delimited, with `&{ … }` interpolation.")],
     "run:0",
     main_("""    int64:n = raw v64(-5i64);
    string:t = `a&{ n }b`;
    if (!(string_equals(t, "a-5b"))) { exit 10i32; }
    int32:k = raw v32(12i32);
    string:u = `&{ k + 1i32 }`;
    if (!(string_equals(u, "13"))) { exit 11i32; }
    exit 0i32;"""),
     wrong="the sign lost (10), or the expression not evaluated (11)",
     note="The decimal rendering is the reading of 'interpolates' for an integer; no sentence "
          "states the format in words.")

item("t12_to_cstring_interior_nul", AREA_T,
     "`to_cstring` of a string with an interior NUL",
     "`to_cstring` fails on an interior NUL (the floor's code -22).",
     [("TYPE", "**`to_cstring` fails on an interior NUL.** A `string` may contain `0u8` anywhere;"),
      ("BUILTIN", "reuse that vocabulary — an interior NUL is −22, a slice out of range −34 — and")],
     "run:0",
     main_(r"""    Result<cstring>:r = to_cstring("a\0b");
    if (!r.is_error) { exit 10i32; }
    Result<cstring>:q = to_cstring("abc");
    if (q.is_error) { exit 11i32; }
    exit 0i32;"""),
     wrong="a silent truncation at the NUL (exit 10): the poison-NUL bypass")

item("t13_cstring_keeps_length", AREA_T,
     "the length of a `cstring`",
     "A `cstring` retains its length (the buffer is len + 1 bytes).",
     [("TYPE", "The buffer is `len + 1` bytes with `buf[len] == 0u8`. **The length is retained**,")],
     "run:0",
     main_("""    cstring:c = to_cstring("abcd") ?! E1;
    if (c.len != 4i64) { exit 10i32; }
    exit 0i32;""", "error:E1;"),
     wrong="the terminator counted, 5 (exit 10)")

item("t14_string_plus_concatenates", AREA_T,
     "`a + b` on strings",
     "On `string`, `+` is concatenation.",
     [("TYPE", "- Arithmetic: `+` is **concatenation**, NOT addition. No `-`, `*`, `/`, `%`."),
      ("TYPE", "- Concatenation: `string:c = a + b;` → allocates new buffer, copies both")],
     "run:0",
     main_("""    string:a = "ab";
    string:b = "cd";
    string:c = a + b;
    if (!(string_equals(c, "abcd"))) { exit 10i32; }
    exit 0i32;"""),
     wrong="the documented operator refused, or the operands in the wrong order (exit 10)")

item("t15_concat_empty", AREA_T,
     "`string_concat` with empty operands",
     "`string_concat` concatenates; an empty result allocates nothing.",
     [("BUILTIN", "| `string_concat` | `(string, string) → string` | The one string operation")],
     "run:0",
     main_("""    string:e = string_concat("", "");
    if (e.len != 0i64) { exit 10i32; }
    string:f = string_concat("ab", "");
    if (!(string_equals(f, "ab"))) { exit 11i32; }
    string:g = string_concat("", "cd");
    if (!(string_equals(g, "cd"))) { exit 12i32; }
    exit 0i32;"""),
     wrong="a lost operand (the check's code)")

item("t16_string_order", AREA_T,
     "`cmp` on strings: a prefix, a shorter larger string, a high byte",
     "`a.cmp(b)` orders strings lexicographically, byte by byte.",
     [("TYPE", "- Ordering: `a.cmp(b)` (the prelude's `string: Ord`, D-257) → lexicographic;")],
     "run:0",
     main_(r"""    string:a = "abc";
    string:b = "abd";
    int32:r = 0i32;
    pick (a.cmp(b) ?! E9) { (Ordering.Less) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    string:c = "ab";
    pick (c.cmp(a) ?! E9) { (Ordering.Less) { r = 3i32; }, (*) { r = 4i32; } }
    if (r != 3i32) { exit 11i32; }
    string:d = "b";
    pick (d.cmp(a) ?! E9) { (Ordering.Greater) { r = 5i32; }, (*) { r = 6i32; } }
    if (r != 5i32) { exit 12i32; }
    string:h = "\xC3";
    pick (h.cmp(a) ?! E9) { (Ordering.Greater) { r = 7i32; }, (*) { r = 8i32; } }
    if (r != 7i32) { exit 13i32; }
    exit 0i32;""", "error:E9;"),
     wrong="a length-first order (12), or a signed byte compare (13)")

item("t17_string_equals", AREA_T,
     "`string_equals` on a prefix and on empties",
     "`string_equals` is a byte-equal comparison.",
     [("BUILTIN", "*   `string_equals(a, b)`: Byte-equal comparison.")],
     "run:0",
     main_("""    if (string_equals("ab", "abc")) { exit 10i32; }
    if (!(string_equals("", ""))) { exit 11i32; }
    if (string_equals("abc", "abd")) { exit 12i32; }
    exit 0i32;"""),
     wrong="a prefix compare calls \"ab\" equal to \"abc\" (exit 10)")

# ------------------------------------------------------------ P pick
AREA_P = "pick"

item("p01_no_implicit_fallthrough", AREA_P,
     "a matching arm followed by others",
     "`pick` does not fall through implicitly.",
     [("CONTROL", "*   **Fallthrough:** Nitpick does not implicitly fall through.")],
     "run:0",
     main_("""    int32:x = raw v32(1i32);
    int32:a = 0i32;
    pick (x) {
        (1i32) { a = a + 1i32; },
        (2i32) { a = a + 10i32; },
        (*) { a = a + 100i32; }
    }
    if (a != 1i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="C's fallthrough: 111 (exit 10)")

item("p02_fall_to_label", AREA_P,
     "`fall two;` from the first arm",
     "`fall label;` falls through to the labelled arm, and only to it.",
     [("CONTROL", "*   **`fall label;`** — falls through to the labelled arm. There is no implicit fallthrough.")],
     "run:0",
     main_("""    int32:x = raw v32(1i32);
    int32:a = 0i32;
    pick (x) {
        (1i32) { a = a + 1i32; fall two; },
        two: (2i32) { a = a + 10i32; },
        (3i32) { a = a + 100i32; },
        (*) { a = a + 1000i32; }
    }
    if (a != 11i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the fall continues past the labelled arm (111, 1111) or does not happen (1)")

item("p03_first_match_wins", AREA_P,
     "overlapping arms: a range, then a value inside it",
     "An arm is taken under its pattern and the negations of the earlier arms: the first "
     "matching arm in source order wins.",
     [("VERIFICATION", "> condition; a `pick` arm's pattern (a value, a range, a wildcard as the"),
      ("VERIFICATION", "> negation of the arms before it), the negations of the earlier arms and its")],
     "run:0",
     main_("""    int32:x = raw v32(5i32);
    int32:r = 0i32;
    pick (x) {
        (1i32..10i32) { r = 1i32; },
        (5i32) { r = 2i32; },
        (*) { r = 3i32; }
    }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the most specific or the last matching arm (exit 10)",
     note="The order is stated in VERIFICATION_REFERENCE's model of `pick` (what the solver "
          "assumes the emitted code does); CONTROL_REFERENCE states no order in words.")

item("p04_range_pattern_edges", AREA_P,
     "`(0...5)` and `(5..9)` at 0, 5, 9 and 10",
     "`..` is the inclusive range [a, b] and `...` the exclusive [a, b), in `pick` patterns too.",
     [("OP", "| `..` | Inclusive Range | Inclusive range `[a, b]`. Used in `for` and `pick`. | `0..10` |"),
      ("OP", "| `...` | Exclusive Range | Exclusive range `[a, b)`. Used in `for` and `pick`. | `0...10` |")],
     "run:0",
     main_("""    int32:r = 0i32;
    int32:v5 = raw v32(5i32);
    pick (v5) { (0i32...5i32) { r = 1i32; }, (5i32..9i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 2i32) { exit 10i32; }
    int32:v9 = raw v32(9i32);
    pick (v9) { (0i32...5i32) { r = 1i32; }, (5i32..9i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 2i32) { exit 11i32; }
    int32:v10 = raw v32(10i32);
    pick (v10) { (0i32...5i32) { r = 1i32; }, (5i32..9i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 3i32) { exit 12i32; }
    int32:v0 = raw v32(0i32);
    pick (v0) { (0i32...5i32) { r = 1i32; }, (5i32..9i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 1i32) { exit 13i32; }
    exit 0i32;"""),
     wrong="the two range spellings swapped at an edge (the check's code)")

item("p05_negative_patterns", AREA_P,
     "negative literal and range patterns",
     "A pattern is a value or a range; a negative value matches itself.",
     [("OP", "| `..` | Inclusive Range | Inclusive range `[a, b]`. Used in `for` and `pick`. | `0..10` |")],
     "run:0",
     main_("""    int32:x = raw v32(-1i32);
    int32:r = 0i32;
    pick (x) { (-1i32) { r = 1i32; }, (1i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 1i32) { exit 10i32; }
    int32:y = raw v32(-3i32);
    pick (y) { (-5i32..-2i32) { r = 4i32; }, (*) { r = 5i32; } }
    if (r != 4i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="the negation dropped from the pattern (the check's code)")

item("p06_unsigned_selector_ranges", AREA_P,
     "a `uint8` selector of 200 against `(0..127)`, `(128..255)`, `(200)`",
     "An unsigned selector is matched against its patterns by its unsigned value.",
     [("TYPE", "Comparisons use `ult`/`ugt`/`ule`/`uge` instead of `slt`/`sgt`/`sle`/`sge`"),
      ("OP", "| `..` | Inclusive Range | Inclusive range `[a, b]`. Used in `for` and `pick`. | `0..10` |")],
     "run:0",
     main_("""    uint8:x = raw vu8(200u8);
    int32:r = 0i32;
    pick (x) { (0u8..127u8) { r = 1i32; }, (128u8..255u8) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 2i32) { exit 10i32; }
    pick (x) { (200u8) { r = 4i32; }, (*) { r = 5i32; } }
    if (r != 4i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="a signed range test: 200 as -56 falls in neither range (exit 10)")

item("p07_char_selector_high_byte", AREA_P,
     "a `char8` selector above 0x7F against ranges",
     "A `char8` is ordered unsigned, in patterns as in comparisons.",
     [("TYPE", "- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=` → `icmp eq/ne/ult/ugt/ule/uge` (unsigned comparison for Unicode ordering)")],
     "run:0",
     main_(r"""    char8:c = raw vc8('\xC3');
    int32:r = 0i32;
    pick (c) { ('a'..'z') { r = 1i32; }, ('\x80'..'\xFF') { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 2i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="a signed byte range test (exit 10)")

item("p08_guard_false_moves_on", AREA_P,
     "an arm whose `where` guard is false",
     "An arm with a `where` guard matches only when the guard holds.",
     [("CONTROL", "The `pick` construct can also match on macro invocations, and individual arms can be guarded by a conditional `where` clause:")],
     "run:0",
     main_("""    int32:x = raw v32(7i32);
    int32:r = 0i32;
    pick (x) { (7i32) where (x > 10i32) { r = 1i32; }, (7i32) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 2i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the guard ignored (exit 10)")

item("p09_pick_expression_give", AREA_P,
     "a `pick` expression yielding through `give`",
     "`give expr;` yields the value of the `pick` used as an expression.",
     [("CONTROL", "*   **`give expr;`** — yields a value out of the `pick` block when it is used as an expression.")],
     "run:0",
     main_("""    int32:x = raw v32(3i32);
    int32:v = pick (x) { (1i32) { give 10i32; }, (3i32) { give 30i32; }, (*) { give 0i32; } };
    if (v != 30i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the wrong arm's value (exit 10)")

item("p10_int_pick_not_exhaustive", AREA_P,
     "an int32 `pick` without `(*)`",
     "`pick` must be exhaustive.",
     [("CONTROL", "> **`pick` must be exhaustive**, and a `tbb` selector additionally **requires an")],
     "refuse",
     main_("""    int32:x = raw v32(3i32);
    int32:r = 0i32;
    pick (x) { (1i32) { r = 1i32; }, (3i32) { r = 3i32; } }
    if (r == 3i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: an unmatched value silently skips the pick")

item("p11_enum_pick_missing_variant", AREA_P,
     "an enum `pick` missing a variant",
     "`pick` must be exhaustive over an enum's variants.",
     [("CONTROL", "> **`pick` must be exhaustive**, and a `tbb` selector additionally **requires an")],
     "refuse",
     main_("""    Color:c = raw v32(2i32) =>! Color;
    int32:r = 0i32;
    pick (c) { (Color.Red) { r = 1i32; }, (Color.Green) { r = 2i32; } }
    if (r == 0i32) { exit 10i32; }
    exit 11i32;""", "enum:Color = { Red = 0i32; Green = 1i32; Blue = 2i32; };"),
     wrong="accepted: `Blue` silently matches nothing (exit 10)")

item("p12_tbb_pick_needs_err_arm", AREA_P,
     "a `tbb8` `pick` with `(*)` and no `ERR:` arm",
     "A `tbb` selector requires an explicit `ERR:` arm; `(*)` may not absorb ERR.",
     [("CONTROL", "> explicit `ERR:` arm** (D-008 §5.1). `(*)` may not absorb the ERR case, or a")],
     "refuse",
     main_("""    tbb8:t = raw vt8(127tbb8) + raw vt8(1tbb8);
    int32:r = 0i32;
    pick (t) { (5tbb8) { r = 1i32; }, (*) { r = 2i32; } }
    if (r == 2i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted: ERR steers into `(*)` (exit 10)")

item("p13_tbb_err_arm_taken", AREA_P,
     "a `tbb8` holding ERR against an `ERR:` arm",
     "A `pick` with an explicit `ERR:` arm branches on ERR without trapping.",
     [("OP", "a `pick` with an explicit"),
      ("TYPE", "trapping, or a `pick` with an explicit `ERR:` arm.")],
     "run:0",
     main_("""    tbb8:t = raw vt8(127tbb8) + raw vt8(1tbb8);
    int32:r = 0i32;
    pick (t) { ERR: { r = 1i32; }, (5tbb8) { r = 2i32; }, (*) { r = 3i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="a trap (110), or ERR matched as a number (exit 10)")

# ------------------------------------------------------------ W when / defer
AREA_W = "`when` and `defer` ordering"
REF_THEN_END = ("CONTROL", "**`then` and `end` partition the outcomes exactly.** One of them always runs, and")

item("w01_when_ran_then", AREA_W,
     "a `when` whose body runs",
     "`then` runs when the body ran at least once; `end` does not.",
     [REF_THEN_END, ("CONTROL", "| body ran ≥ 1 time, condition later became false | `then` |")],
     "run:0",
     main_("""    int32:x = raw v32(3i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x { x = x - 1i32; } then { t = t + 1i32; } end { e = e + 1i32; }
    if (t != 1i32) { exit 10i32; }
    if (e != 0i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="both or neither clause (10, 11)")

item("w02_when_never_ran_end", AREA_W,
     "a `when` whose condition is false at once",
     "`end` runs only when the body never ran; `then` does not.",
     [REF_THEN_END, ("CONTROL", "| condition false initially — body never ran | `end` |")],
     "run:0",
     main_("""    int32:x = raw v32(0i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x { x = x - 1i32; } then { t = t + 1i32; } end { e = e + 1i32; }
    if (t != 0i32) { exit 10i32; }
    if (e != 1i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="`then` run for a body that never ran (10)")

item("w03_when_break_then", AREA_W,
     "a `when` left by `break`",
     "A body that ran and was left by `break` runs `then`, not `end`.",
     [("CONTROL", "| body ran ≥ 1 time, exited early via `break` | `then` |")],
     "run:0",
     main_("""    int32:x = raw v32(5i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x { if (x == 4i32) { break; } x = x - 1i32; } then { t = t + 1i32; } end { e = e + 1i32; }
    if (t != 1i32) { exit 10i32; }
    if (e != 0i32) { exit 11i32; }
    if (x != 4i32) { exit 12i32; }
    exit 0i32;"""),
     wrong="the earlier revision's reading: `break` goes to `end` (10, 11)")

item("w04_defer_lifo", AREA_W,
     "two `defer`s in a block",
     "`defer` pushes onto a stack: at scope exit the defers run LIFO.",
     [("CONTROL", "Pushes a block onto a stack to run when the enclosing lexical scope exits."),
      ("CONTROL", "LIFO, innermost scope first.")],
     "run:0",
     main_("""    int32:log = 0i32;
    {
        defer { log = log * 10i32 + 1i32; }
        defer { log = log * 10i32 + 2i32; }
        log = raw v32(5i32);
    }
    if (log != 521i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="FIFO order: 512 (exit 10), or the defers deferred to the function's end")

item("w05_pass_value_before_defer", AREA_W,
     "`pass x` with a `defer` that changes `x`",
     "`pass v` returns the `v` read at the `pass`; the defers run after it is read (D-136).",
     [("CONTROL", "**after the exit's value is evaluated** (D-136): `pass v` returns the `v` that was read at the `pass`, whatever the defers then do.")],
     "run:0",
     main_("""    if (raw settled() != 0i32) { exit 10i32; }
    exit 0i32;""", """func:settled = int32() never fails {
    int32:x = raw v32(0i32);
    defer { x = x + 9i32; }
    pass x;
};"""),
     wrong="the seed's order, defers first: 9 (exit 10)")

item("w06_defer_on_fail", AREA_W,
     "a `defer` in a function that fails",
     "Defers run on every normal exit path, `fail` included.",
     [("CONTROL", "Runs on **every normal exit path** — scope end, `return`, `pass`, `fail`, `relay`, `exit` —")],
     "run:0",
     main_("""    int32:c = 0i32;
    Result<int32>:r = f(@c);
    if (!r.is_error) { exit 10i32; }
    if (c != 1i32) { exit 11i32; }
    exit 0i32;""", """error:E1;
func:f = int32(int32->:cnt) {
    defer { <-cnt = (<-cnt) + 1i32; }
    fail E1;
};"""),
     wrong="the defer skipped on the failure path (exit 11)")

item("w07_defer_on_relay", AREA_W,
     "a `defer` in a function whose `relay` propagates an error",
     "`relay`'s early return is a normal exit: its defers run.",
     [("CONTROL", "Runs on **every normal exit path** — scope end, `return`, `pass`, `fail`, `relay`, `exit` —"),
      ("OP", "`defer` runs — it is a normal exit path, not a trap.")],
     "run:0",
     main_("""    int32:c = 0i32;
    Result<int32>:r = f(@c);
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    if (c != 1i32) { exit 12i32; }
    exit 0i32;""", """error:E1;
func:g = int32() { fail E1; };
func:f = int32(int32->:cnt) {
    defer { <-cnt = (<-cnt) + 1i32; }
    int32:v = relay g();
    pass v;
};"""),
     wrong="the defer skipped on the relay path (exit 12)")

item("w08_defer_on_exit", AREA_W,
     "a `defer` in `main` before `exit 5`",
     "Defers run at `exit` too, after its code is read.",
     [("CONTROL", "Runs on **every normal exit path** — scope end, `return`, `pass`, `fail`, `relay`, `exit` —"),
      ("DECISIONS", "**`fail` and `exit` follow the same rule** — the code is read at the statement,")],
     "run:97",
     main_("""    int32:z = raw v32(0i32);
    defer { int32:q = 7i32 / z; discard(q); }
    exit 5i32;"""),
     wrong="the defer skipped at `exit` (exit 5)",
     note="The observer: the defer divides by a run-time zero, so a defer that runs is seen as "
          "the DivByZero trap's 97, and one that does not run leaves the `exit 5`.")

item("w09_no_defer_on_trap", AREA_W,
     "a `defer` in `main` when `?!` traps",
     "`defer` does not run on a trap: `?!` transfers to failsafe without unwinding.",
     [("CONTROL", "> **`defer` does NOT run on a trap** (D-014). `!!!` and `?!` transfer control")],
     "run:82",
     main_("""    int32:z = raw v32(0i32);
    defer { int32:q = 7i32 / z; discard(q); }
    int32:v = bad() ?! E2;
    exit v;""", """error:E1;
error:E2;
func:bad = int32() { fail E1; };"""),
     wrong="the defer runs first and traps DivByZero (97, or 70 on re-entry)")

item("w10_defer_per_iteration", AREA_W,
     "a `defer` in a loop body",
     "A loop body is a block: its defer runs at each iteration's scope end.",
     [("CONTROL", "A block is zero or more statements in braces `{ … }`. Blocks introduce a lexical"),
      ("CONTROL", "Runs on **every normal exit path** — scope end, `return`, `pass`, `fail`, `relay`, `exit` —")],
     "run:0",
     main_("""    int32:count = 0i32;
    for (int64:i in 0i64...3i64) {
        defer { count = count + 1i32; }
        discard(i);
    }
    if (count != 3i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the defers held to the function's end (0), or one per loop (1)")

item("w11_defer_inner_scope_first", AREA_W,
     "a `defer` in an inner block",
     "An inner block's defers run at the inner block's end, before the code after it.",
     [("CONTROL", "LIFO, innermost scope first.")],
     "run:0",
     main_("""    int32:a = 0i32;
    {
        defer { a = 1i32; }
    }
    if (a != 1i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the inner defer deferred to the function's end (exit 10)")

item("w12_exit_code_read_before_defer", AREA_W,
     "`exit code` with a `defer` that changes `code`",
     "`exit`'s code is read at the statement; the defers run after.",
     [("DECISIONS", "**`fail` and `exit` follow the same rule** — the code is read at the statement,")],
     "run:3",
     main_("""    int32:code = raw v32(3i32);
    defer { code = 4i32; }
    exit code;"""),
     wrong="the defer's value taken: exit 4")

# ------------------------------------------------------------ R Result
AREA_R = "`Result`, `?|`, `?!`, `relay`"

item("r01_fallback", AREA_R,
     "`?|` on a failure and on a success",
     "`expr ?| fallback` yields the value, or the fallback if the call errored.",
     [("OP", "`expr ?| fallback` yields `expr`'s value, or `fallback` if it errored. D-167")],
     "run:0",
     main_("""    if ((f(raw vb(false)) ?| 7i32) != 7i32) { exit 10i32; }
    if ((f(raw vb(true)) ?| 7i32) != 5i32) { exit 11i32; }
    exit 0i32;""", """error:E1;
func:f = int32(bool:ok) { if (ok) { pass 5i32; } fail E1; };"""),
     wrong="the zeroed value half read on failure: 0 (exit 10)")

item("r02_relay_same_error", AREA_R,
     "`relay` of a callee's error",
     "`relay` returns the callee's error verbatim, and yields `.value` on success.",
     [("CONTROL", "if `expr` is an error the enclosing function returns immediately **with that")],
     "run:0",
     main_("""    Result<int32>:r = g(raw v32(1i32));
    if (!r.is_error) { exit 10i32; }
    if (r.err != E2) { exit 11i32; }
    if ((g(raw v32(0i32)) ?| 0i32) != 11i32) { exit 12i32; }
    exit 0i32;""", """error:E1;
error:E2;
func:f = int32(int32:k) { if (k > 0i32) { fail E2; } pass 1i32; };
func:g = int32(int32:k) { int32:v = relay f(k); pass v + 10i32; };"""),
     wrong="a substituted error (11), the prototype's `fail 1;` shape")

item("r03_relay_returns_at_once", AREA_R,
     "code after a `relay` that met an error",
     "On an error, `relay` returns immediately: nothing after it runs.",
     [("CONTROL", "if `expr` is an error the enclosing function returns immediately **with that")],
     "run:0",
     main_("""    int32:c = 0i32;
    Result<int32>:r = g(@c);
    if (!r.is_error) { exit 10i32; }
    if (c != 0i32) { exit 11i32; }
    exit 0i32;""", """error:E1;
func:f = int32() { fail E1; };
func:g = int32(int32->:cnt) {
    int32:v = relay f();
    <-cnt = (<-cnt) + 1i32;
    pass v;
};"""),
     wrong="the statement after the relay runs (exit 11)")

item("r04_emphatic_unwrap_error", AREA_R,
     "`f() ?! E2` where `f` fails with `E1`",
     "`?!` calls failsafe with its one argument, an Error constant.",
     [("OP", "| `?!` | Emphatic Unwrap | Unwraps a Result. If error, calls `failsafe(err)`. **Takes exactly one argument**, an `Error` constant")],
     "run:82",
     main_("""    int32:v = f() ?! E2;
    exit v;""", """error:E1;
error:E2;
func:f = int32() { fail E1; };"""),
     wrong="failsafe given the callee's E1 (81), or no trap (the value)")

item("r05_drop_of_fallible_refused", AREA_R,
     "`drop f();` where `f` may fail",
     "`drop` is licensed only for a `never fails`, NIL-returning callee (TYPE-042): an error is "
     "never discarded without a keyword that handles it.",
     [("TYPE", "> - `drop` = the \"void call\": run a `never fails` function whose success type is"),
      ("OP", "the `void` call of a `never fails`, `NIL` callee — refused otherwise, `TYPE-042`")],
     "refuse:NITPICK-TYPE-042",
     main_("""    drop f();
    exit 0i32;""", """error:E1;
func:f = NIL() { fail E1; };"""),
     wrong="accepted: the error silently dropped (exit 0)")

item("r06_bare_call_refused", AREA_R,
     "a bare `f();` on a fallible call",
     "A bare `f();` on a `Result` is refused: a value-less statement is `drop`, `relay`, `?!` or `?| NIL`.",
     [("DECISIONS", "a value-less statement is one of `drop f();` / `relay f();` / `f() ?! c;` / `f() ?| NIL;`, and a bare `f();` on a `Result` is refused")],
     "refuse",
     main_("""    f();
    exit 0i32;""", """error:E1;
func:f = NIL() { fail E1; };"""),
     wrong="accepted: the error silently dropped (exit 0)")

item("r07_value_without_check_refused", AREA_R,
     "`r.value` read with no check of `r.is_error`",
     "`.value` may not be read without first checking `.is_error` (or an unwrap operator).",
     [("TYPE", "The compiler WILL NOT allow accessing `.value` without first checking `.is_error`")],
     "refuse",
     main_("""    Result<int32>:r = f();
    int32:v = r.value;
    if (v == 0i32) { exit 10i32; }
    exit 11i32;""", """error:E1;
func:f = int32() { fail E1; };"""),
     wrong="accepted: the failure's zeroed value read as 0 (exit 10)")

item("r08_raw_on_fallible_refused", AREA_R,
     "`raw f()` where `f` may fail",
     "`raw` is licensed only on a `never fails` callee (TYPE-042).",
     [("TYPE", "> - `raw` = unwrap a `Result<T>`'s value. **D-163 (settled; the licence is ON — `NITPICK-TYPE-042`)**: licensed only")],
     "refuse:NITPICK-TYPE-042",
     main_("""    int32:v = raw f();
    if (v == 0i32) { exit 10i32; }
    exit 11i32;""", """error:E1;
func:f = int32() { fail E1; };"""),
     wrong="accepted: an unchecked read of the zeroed value (exit 10)")

item("r09_discard_of_result_refused", AREA_R,
     "`discard(f());` where `f` returns a Result",
     "`discard` takes a value, never a `Result`.",
     [("TYPE", "> - `discard` = \"I have this value/param and will not use it\" — takes a VALUE,")],
     "refuse",
     main_("""    discard(f());
    exit 0i32;""", """error:E1;
func:f = int32() { fail E1; };"""),
     wrong="accepted: the error silently discarded (exit 0)")

item("r10_result_literal_both", AREA_R,
     "`return Result{ err: E1, value: 3 }`",
     "The literal form returns a value and an error at once; it is an error.",
     [("CONTROL", "the literal form, the only way to return a value"),
      ("TYPE", "| `return Result{err: errCode, value: retVal};` | (literal, no desugar) | Special: return both value AND error |")],
     "run:0",
     main_("""    Result<int32>:r = f();
    if (!r.is_error) { exit 10i32; }
    if ((f() ?| 9i32) != 9i32) { exit 11i32; }
    exit 0i32;""", """error:E1;
func:f = int32() { return Result{ err: E1, value: 3i32 }; };"""),
     wrong="the value taken over the error (11)")

# ------------------------------------------------------------ L loops
AREA_L = "loop ranges"
REF_INCL = ("OP", "| `..` | Inclusive Range | Inclusive range `[a, b]`. Used in `for` and `pick`. | `0..10` |")
REF_EXCL = ("OP", "| `...` | Exclusive Range | Exclusive range `[a, b)`. Used in `for` and `pick`. | `0...10` |")
REF_BOUNDED = ("CONTROL", "or both, is `NITPICK-TYPE-072`; `for`, `loop` and `till` are bounded by")


def count_item(iid, title, claim, refs, head, bindtype, expect_n, expect_sum, wrong, note="", pre=""):
    item(iid, AREA_L, title, claim, refs, "run:0",
         main_(pre + """    int64:n = 0i64;
    int64:s = 0i64;
    %s { n = n + 1i64; s = s + (%s); }
    if (n != %di64) { exit 10i32; }
    if (s != %di64) { exit 11i32; }
    exit 0i32;""" % (head, bindtype, expect_n, expect_sum)),
         wrong=wrong, note=note)


count_item("l01_for_inclusive", "`for (i in 1..3)`",
           "`..` is the inclusive range [a, b].", [REF_INCL, ("CONTROL", "for (int64:i in 1..3) {")],
           "for (int64:i in 1i64..3i64)", "i", 3, 6, "an exclusive reading: 1, 2 (10)")
count_item("l02_for_exclusive", "`for (i in 0...3)`",
           "`...` is the exclusive range [a, b).", [REF_EXCL],
           "for (int64:i in 0i64...3i64)", "i", 3, 3, "an inclusive reading: 0..3 (10)")
count_item("l03_for_negative_bounds", "`for (i in -3..-1)` from run-time bounds",
           "An inclusive range over negative run-time bounds visits each value once.", [REF_INCL],
           "for (int64:i in lo..hi)", "i", 3, -6, "a signed/unsigned slip on negative bounds (10, 11)",
           pre="    int64:lo = raw v64(-3i64);\n    int64:hi = raw v64(-1i64);\n")
count_item("l04_for_inclusive_empty", "`for (i in 3..1)` from run-time bounds",
           "An inclusive range [a, b] with a > b is empty.", [REF_INCL],
           "for (int64:i in lo..hi)", "i", 0, 0, "a descending walk 3, 2, 1 (10)",
           note="Inferred, not stated: the text defines `..` as the interval [a, b], which is empty "
                "for a > b; no sentence says what `for` does with a > b. (`loop` infers a "
                "direction; `for` is not said to.)",
           pre="    int64:lo = raw v64(3i64);\n    int64:hi = raw v64(1i64);\n")
count_item("l05_for_exclusive_empty", "`for (i in 3...3)` from run-time bounds",
           "An exclusive range [a, a) is empty.", [REF_EXCL],
           "for (int64:i in lo...hi)", "i", 0, 0, "one iteration (10)",
           pre="    int64:lo = raw v64(3i64);\n    int64:hi = raw v64(3i64);\n")
count_item("l06_for_inclusive_to_int8_max", "`for (int8:i in 125..127)`",
           "An inclusive range ending at the type's maximum visits the maximum and ends: `for` is "
           "bounded by construction.", [REF_INCL, REF_BOUNDED],
           "for (int8:i in lo..hi)", "i => int64", 3, 378,
           "the counter stepped past 127: an overflow trap (93), or a wrap and a loop that does not end (T)",
           pre="    int8:lo = raw v8(125i8);\n    int8:hi = raw v8(127i8);\n")
count_item("l07_for_inclusive_to_uint8_max", "`for (uint8:i in 250..255)`",
           "An inclusive range ending at 255 on a uint8 visits 255 and ends.", [REF_INCL, REF_BOUNDED],
           "for (uint8:i in lo..hi)", "i => int64", 6, 1515,
           "the counter stepped past 255 (93, or T)",
           pre="    uint8:lo = raw vu8(250u8);\n    uint8:hi = raw vu8(255u8);\n")
count_item("l08_for_inclusive_to_int64_max", "`for (int64:i in max-2..max)`",
           "An inclusive range ending at the int64 maximum visits it and ends.", [REF_INCL, REF_BOUNDED],
           "for (int64:i in lo..hi)", "i - lo", 3, 3,
           "the counter stepped past the maximum (93, or T)",
           pre="    int64:hi = raw v64(9223372036854775807i64);\n    int64:lo = hi - raw v64(2i64);\n")
count_item("l09_for_exclusive_to_int8_max", "`for (int8:i in 125...127)`",
           "An exclusive range ending at the maximum stops before it.", [REF_EXCL],
           "for (int8:i in lo...hi)", "i => int64", 2, 251, "the maximum visited (10)",
           pre="    int8:lo = raw v8(125i8);\n    int8:hi = raw v8(127i8);\n")
count_item("l10_till_counts_from_zero", "`till(5, 1)`",
           "`till(limit, step)` counts up from 0 to limit: `$` ranges 0..limit-1.",
           [("CONTROL", "**`till(limit, step)`** — the simple form. Counts **up from 0** to `limit`."),
            ("CONTROL", "x += $;  // '$' ranges from 0 to 9")],
           "till (5i64, 1i64)", "$", 5, 10, "an inclusive limit, 0..5 (10)")
count_item("l11_till_nonpositive_limit", "`till(-3, 1)` with a run-time limit",
           "`till` with limit <= 0 runs zero times.",
           [("CONTROL", "| `till` with `limit <= 0` | zero iterations — `till` ascends from `0` |")],
           "till (raw v64(-3i64), 1i64)", "$", 0, 0,
           "a descent toward the negative limit (10)")
count_item("l12_loop_ascending", "`loop(0, 5, 1)`",
           "`loop(start, limit, step)` ascends when start < limit: `$` is 0, 1, ..., limit-1.",
           [("CONTROL", "    x += $;  // ascending:  0, 1, ..., 9")],
           "loop (0i64, 5i64, 1i64)", "$", 5, 10, "an inclusive limit (10)")
item("l13_loop_descending", AREA_L,
     "`loop(5, 0, 1)`",
     "`loop` infers a descent when start > limit: `$` counts down from start, and the limit is "
     "excluded (10, 9, ..., 1).",
     [("CONTROL", "    x += $;  // descending: 10, 9, ..., 1"),
      ("DECISIONS", "- `$` is well-defined in both forms, and counts *down* in a descending `loop`.")],
     "run:0",
     main_("""    int64:acc = 0i64;
    loop (5i64, 0i64, 1i64) { acc = acc * 10i64 + $; }
    if (acc != 54321i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="an ascending walk, or the limit included (543210) (exit 10)")
count_item("l14_loop_start_equals_limit", "`loop(3, 3, 1)`",
           "`loop` with start == limit runs zero times.",
           [("CONTROL", "| `start == limit` | zero iterations |")],
           "loop (3i64, 3i64, 1i64)", "$", 0, 0, "one iteration (10)")
count_item("l15_loop_step_ascending", "`loop(0, 10, 3)`",
           "The step is the size of the jump: 0, 3, 6, 9.",
           [("CONTROL", "> Because direction is inferred from the bounds, `step` controls **only the size")],
           "loop (0i64, 10i64, 3i64)", "$", 4, 18, "a stepped walk off by one (10)",
           note="Inferred: the text gives step-1 examples only; that a step of 3 visits "
                "start + 3k while short of the limit is the reading of 'the size of the jump'.")
count_item("l16_loop_step_descending", "`loop(10, 0, 3)`",
           "A descending loop with step 3 visits 10, 7, 4, 1.",
           [("CONTROL", "> Because direction is inferred from the bounds, `step` controls **only the size")],
           "loop (10i64, 0i64, 3i64)", "$", 4, 22, "a stepped walk off by one (10)",
           note="Inferred, as l15.")
count_item("l17_loop_step_near_int8_max", "`loop(0i8, 127i8, 100i8)`",
           "A counted loop is bounded by construction: `$` is 0 and 100, and the next step past "
           "the limit ends the loop.",
           [REF_BOUNDED, ("CONTROL", "> Because direction is inferred from the bounds, `step` controls **only the size")],
           "loop (0i8, 127i8, 100i8)", "$ => int64", 2, 100,
           "the counter computed as 100 + 100 in int8: an overflow trap (93), or a wrap to -56 and more trips",
           note="Inferred, as l15; the trip that would pass the limit is never taken.")
item("l18_loop_step_near_int8_min", AREA_L,
     "`loop(-27i8, min, 100i8)`",
     "A descending counted loop ends without computing a counter past the limit: `$` is -27 "
     "and -127.",
     [REF_BOUNDED],
     "run:0",
     main_("""    int8:mn = raw v8(-127i8) - raw v8(1i8);
    int64:n = 0i64;
    int64:s = 0i64;
    loop (-27i8, mn, 100i8) { n = n + 1i64; s = s + ($ => int64); }
    if (n != 2i64) { exit 10i32; }
    if (s != -154i64) { exit 11i32; }
    exit 0i32;"""),
     wrong="-127 - 100 computed in int8: an overflow trap (93), or a wrap (10)",
     note="Inferred, as l15.")

item("l19_zero_step_literal_refused", AREA_L,
     "`till(10, 0)`",
     "A literal step must be positive: zero is a compile error (TYPE-068).",
     [("CONTROL", "| `step` negative or zero | compile error |"),
      ("CONTROL", "`loop` takes three arguments and `till` two, and a step written as")],
     "refuse:NITPICK-TYPE-068",
     main_("""    int64:n = 0i64;
    till (10i64, 0i64) { n = n + 1i64; }
    exit 11i32;"""),
     wrong="accepted: a loop that cannot end, or a run-time trap")

item("l20_negative_step_literal_refused", AREA_L,
     "`loop(0, 10, -1)`",
     "A negative literal step is a compile error (TYPE-068).",
     [("CONTROL", "| `step` negative or zero | compile error |")],
     "refuse:NITPICK-TYPE-068",
     main_("""    int64:n = 0i64;
    loop (0i64, 10i64, -1i64) { n = n + 1i64; }
    exit 11i32;"""),
     wrong="accepted: an infinite or descending loop")

item("l21_zero_step_computed_traps", AREA_L,
     "`till(10, k)` with k = 0 at run time",
     "A computed step keeps a run-time check that traps to failsafe (`BadStep`).",
     [("CONTROL", "`step > 0` as a proof obligation, falling back to a runtime check that traps to")],
     "run:113",
     main_("""    int64:n = 0i64;
    till (10i64, raw v64(0i64)) { n = n + 1i64; }
    exit 11i32;"""),
     wrong="no check: a loop that never ends (T)")

item("l22_negative_step_computed_traps", AREA_L,
     "`loop(0, 10, k)` with k = -2 at run time",
     "A computed step that is not positive traps to failsafe (`BadStep`).",
     [("CONTROL", "`step > 0` as a proof obligation, falling back to a runtime check that traps to")],
     "run:113",
     main_("""    int64:n = 0i64;
    loop (0i64, 10i64, raw v64(-2i64)) { n = n + 1i64; }
    exit 11i32;"""),
     wrong="no check: a sign read as a direction (11), or a loop that never ends (T)")

item("l23_for_captures_bound", AREA_L,
     "a `for` whose bound variable changes in the body",
     "A `for` evaluates its range once, at entry.",
     [("DECISIONS", "**The fact the rule rests on, measured by probe before any loop moved.** A"),
      ("DECISIONS", "`for (intN:i in lo...hi)` evaluates its range ONCE, at entry — `emit_for`")],
     "run:0",
     main_("""    int64:n = raw v64(3i64);
    int32:c = 0i32;
    for (int64:i in 0i64...n) { n = 10i64; c = c + 1i32; discard(i); }
    if (c != 3i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the bound re-read each trip: 10 iterations (exit 10)",
     note="The rule is stated in DECISIONS (D-234) as a measured fact about `emit_for`; "
          "CONTROL_REFERENCE is silent.")

item("l24_while_rereads_bound", AREA_L,
     "a `while` whose bound variable changes in the body",
     "A `while` re-reads its bound every iteration.",
     [("DECISIONS", "extracts `hi` into a loop slot — while a `while (i < x.count)` re-reads")],
     "run:0",
     main_("""    int64:n = raw v64(3i64);
    int64:i = 0i64;
    while (i < n) decreases 100i64 - i {
        if (i == 0i64) { n = 6i64; }
        i = i + 1i64;
    }
    if (i != 6i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="the bound captured: 3 (exit 10)")

item("l25_for_over_array_in_order", AREA_L,
     "`for (v in arr)`",
     "A `for` iterates an array's elements.",
     [("CONTROL", "> **What `for` iterates (D-166, 1.0.9):** a range, a slice, an array, or a")],
     "run:0",
     main_("""    int32[3]:arr = [5i32, 6i32, 7i32];
    int32:acc = 0i32;
    for (int32:v in arr) { acc = acc * 10i32 + v; }
    if (acc != 567i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="a reversed or skipping walk (exit 10)")

item("l26_labelled_continue", AREA_L,
     "`continue outer;` from an inner loop",
     "`continue label;` targets the labelled loop.",
     [("CONTROL", "`break label;` and `continue label;` both target a labelled loop.")],
     "run:0",
     main_("""    int32:n = 0i32;
    outer: for (int64:i in 0i64...3i64) {
        for (int64:j in 0i64...3i64) {
            if (j == 1i64) { continue outer; }
            n = n + 1i32;
        }
        n = n + 100i32;
        discard(i);
    }
    if (n != 3i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the inner loop continued instead (6 or 306), or the outer body finished (303)")

item("l27_continue_in_for", AREA_L,
     "`continue` in a `for` range",
     "`continue` skips to the next iteration.",
     [("CONTROL", "Nitpick supports `break;` to exit the innermost loop, and `continue;` to skip to the next iteration across all loop types.")],
     "run:0",
     main_("""    int64:s = 0i64;
    for (int64:i in 0i64...5i64) {
        if (i == 2i64) { continue; }
        s = s + i;
    }
    if (s != 8i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="an iteration skipped twice, or none (exit 10)")

item("l28_for_binding_type_mismatch", AREA_L,
     "`for (int32:i in 0i64...3i64)`",
     "The binding's type must equal the element type (TYPE-033).",
     [("CONTROL", "`assoc:Item; func:next = Item?(Self->:self);`, `NIL` ending the loop (the"),
      ("CONTROL", "name (`NITPICK-TYPE-033`), never at a backend rung.")],
     "refuse:NITPICK-TYPE-033",
     main_("""    int32:s = 0i32;
    for (int32:i in 0i64...3i64) { s = s + i; }
    exit s;"""),
     wrong="accepted: an implicit narrowing of each element")

# ------------------------------------------------------------ H shadowing
AREA_H = "shadowing and scope"
REF_SHADOW = ("SAFETY", "| `shadow` | bans inner scopes redefining outer names, ignoring macro-generated hygiene names |")
NOTE_SHADOW = ("Inferred, not stated: no reference states the default rule for a local that "
               "shadows an outer one. SAFETY_ARCHITECTURE lists `shadow` among the optional "
               "`--extra-picky` rules ('bans inner scopes redefining outer names', pedantry "
               "'beyond what safety requires'), which implies the default admits it. What is "
               "tested is that, where accepted, the inner binding does not write the outer one.")

item("h01_block_shadow", AREA_H,
     "an inner block redeclaring an outer local",
     "An inner scope may redefine an outer name; the outer binding is untouched.",
     [REF_SHADOW, ("SAFETY", "here adds pedantry beyond what safety requires; none of them gates a safety")],
     "run:0",
     main_("""    int32:x = raw v32(1i32);
    {
        int32:x = raw v32(2i32);
        if (x != 2i32) { exit 10i32; }
    }
    if (x != 1i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="the inner declaration writes the outer slot: 2 (exit 11)", note=NOTE_SHADOW)

item("h02_for_binding_shadow", AREA_H,
     "a `for` binding named like an outer local",
     "A `for` binding's scope is the loop; the outer binding is untouched.",
     [REF_SHADOW],
     "run:0",
     main_("""    int64:i = raw v64(100i64);
    int64:s = 0i64;
    for (int64:i in 0i64...3i64) { s = s + i; }
    if (i != 100i64) { exit 10i32; }
    if (s != 3i64) { exit 11i32; }
    exit 0i32;"""),
     wrong="the loop counter written into the outer `i` (exit 10)", note=NOTE_SHADOW)

item("h03_block_binding_invisible", AREA_H,
     "a use of a block's binding after the block",
     "Blocks introduce a lexical scope: a binding declared inside is invisible outside.",
     [("CONTROL", "scope: variables declared inside are invisible outside, and scope-managed")],
     "refuse",
     main_("""    {
        int32:y = raw v32(1i32);
        discard(y);
    }
    exit y;"""),
     wrong="accepted: the dead slot read")

item("h04_local_shadows_module_binding", AREA_H,
     "a local named like a module `fixed` binding",
     "A local may redefine a module-level name; the module binding keeps its value.",
     [REF_SHADOW],
     "run:0",
     main_("""    int32:K = raw v32(7i32);
    if (K != 7i32) { exit 10i32; }
    if (raw get() != 5i32) { exit 11i32; }
    exit 0i32;""", """fixed int32:K = 5i32;
func:get = int32() never fails { pass K; };"""),
     wrong="the local read as the module constant (10), or written into it (11)", note=NOTE_SHADOW)

# ------------------------------------------------------------ X evaluation
AREA_X = "precedence and evaluation"

item("x01_cast_binds_tighter_than_negation", AREA_X,
     "`-m => int64` with m the int32 minimum",
     "Cast (level 4) binds tighter than unary minus (level 5): `-m => int64` is `-(m => int64)`.",
     [("OP", "| 4 | Cast | `=>` `=>!` |"), ("OP", "| 5 | Unary | `!` `~` `-` `@` `<-` `$$i` `$$m` |")],
     "run:0",
     main_("""    int32:m = raw v32(-2147483647i32) - raw v32(1i32);
    int64:w = -m => int64;
    if (w != 2147483648i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="`(-m) => int64`: the int32 negation traps (93)")

item("x02_additive_before_shift", AREA_X,
     "`1 + 1 << 2` and `1 << 2 + 1`",
     "Additive (level 7) binds tighter than shift (level 8).",
     [("OP", "| 7 | Additive | `+` `-` `+%` `-%` |"), ("OP", "| 8 | Shift | `<<` `>>` |")],
     "run:0",
     main_("""    int32:one = raw v32(1i32);
    if ((one + one << raw v32(2i32)) != 8i32) { exit 10i32; }
    if ((one << raw v32(2i32) + one) != 8i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="shift before add: 5 and 5 (10, 11)")

item("x03_equality_before_bitand", AREA_X,
     "`a & b == c`",
     "Equality (level 11) binds tighter than `&` (level 12), so `a & b == c` is `a & (b == c)`: "
     "an int32 `&` a bool, refused.",
     [("OP", "| 11 | Equality | `==` `!=` |"), ("OP", "| 12 | Bitwise AND | `&` |"), REF_NO_WIDEN],
     "refuse",
     main_("""    int32:a = raw v32(6i32);
    if (a & 2i32 == 2i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="accepted as `(a & 2) == 2` (exit 10)")

item("x04_short_circuit", AREA_X,
     "`&&` and `||` whose right side would trap",
     "`&&` and `||` short-circuit.",
     [("OP", "- **`&&` and `||` short-circuit** and require strictly boolean operands.")],
     "run:0",
     main_("""    int32:d = raw v32(0i32);
    if ((d != 0i32) && ((100i32 / d) > 1i32)) { exit 10i32; }
    if (!((d == 0i32) || ((100i32 / d) > 1i32))) { exit 11i32; }
    exit 0i32;"""),
     wrong="both sides evaluated: the division traps (97)")

item("x05_ternary_evaluates_one_branch", AREA_X,
     "`is (d != 0) : 100 / d : 7` with d = 0",
     "A ternary's branches are evaluated under their conditions: only the chosen one runs.",
     [("VERIFICATION", "> right-hand side of `&&`/`||` and a ternary's branches under theirs. An"),
      ("TYPE", "| `is (cond) : then : else` | ternary/conditional | `select i1 %cond, %then, %else` | NOT `? :` syntax |")],
     "run:0",
     main_("""    int32:d = raw v32(0i32);
    int32:r = is (d != 0i32) : 100i32 / d : 7i32;
    if (r != 7i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="both branches evaluated, as a `select` would: the division traps (97)",
     note="The references differ: VERIFICATION_REFERENCE models the branches under their "
          "conditions; TYPE_REFERENCE §28 gives the lowering as `select`, which evaluates both. "
          "The expectation follows the evaluation rule; the run shows which text holds.")

item("x06_optional_default_lazy", AREA_X,
     "`o ?? (100 / d)` with `o` holding a value and d = 0",
     "`??` evaluates its default only on the empty path.",
     [("TYPE", "test in either operand order; `??` evaluates its default only on the empty")],
     "run:0",
     main_("""    int32:d = raw v32(0i32);
    int32?:o = raw v32(5i32);
    int32:r = o ?? (100i32 / d);
    if (r != 5i32) { exit 10i32; }
    exit 0i32;"""),
     wrong="the default evaluated eagerly: the division traps (97)")

item("x07_left_associative", AREA_X,
     "`10 - 3 - 2`, `100 / 10 / 5`, `7 % 4 * 2`, `2 * 7 % 4`",
     "Operators of one level group left to right.",
     [("OP", "| 6 | Multiplicative | `*` `/` `%` `*%` |"), ("OP", "| 7 | Additive | `+` `-` `+%` `-%` |")],
     "run:0",
     main_("""    int32:a = raw v32(10i32);
    if ((a - raw v32(3i32) - raw v32(2i32)) != 5i32) { exit 10i32; }
    if ((raw v32(100i32) / raw v32(10i32) / raw v32(5i32)) != 2i32) { exit 11i32; }
    if ((raw v32(7i32) % raw v32(4i32) * raw v32(2i32)) != 6i32) { exit 12i32; }
    if ((raw v32(2i32) * raw v32(7i32) % raw v32(4i32)) != 2i32) { exit 13i32; }
    exit 0i32;"""),
     wrong="right grouping: 9 (10), 50 (11), 7 (12), 6 (13)",
     note="Inferred, not stated: the precedence table gives levels and marks level 2 alone as "
          "right-associative; left grouping of the binary levels is the reading of that silence.")

# ------------------------------------------------------------ A arrays and structs
AREA_A = "arrays, slices and value semantics"

item("a01_array_assignment_copies", AREA_A,
     "a write to a copy of an array",
     "Fixed arrays are value types: an assigned copy is independent.",
     [("TYPE", "> **Design Note:** Fixed arrays are **Value Types**, not references.")],
     "run:0",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32[4]:b = a;
    b[0i64] = raw v32(9i32);
    if (a[0i64] != 1i32) { exit 10i32; }
    if (b[0i64] != 9i32) { exit 11i32; }
    exit 0i32;"""),
     wrong="a shared reference: the write shows through the original (exit 10)")

item("a02_array_argument_copies", AREA_A,
     "a callee writing its array parameter",
     "Passing `int32[4]` copies all 16 bytes; to mutate the caller's array, pass a pointer.",
     [("TYPE", "Passing `int32[4]` to a function copies all 16 bytes.")],
     "run:0",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    if (raw poke(a) != 9i32) { exit 10i32; }
    if (a[0i64] != 1i32) { exit 11i32; }
    exit 0i32;""", """func:poke = int32(int32[4]:p) never fails {
    p[0i64] = 9i32;
    pass p[0i64];
};"""),
     wrong="a decay to a pointer: the caller sees 9 (exit 11)",
     note="Whether a by-value array parameter may be written is not stated; the sentence "
          "'to mutate an array inside a function ... pass a pointer' reads as the copy being "
          "the callee's own. A refusal would be a finding about the text, not a wrong answer.")

item("a03_index_past_end", AREA_A,
     "`a[4]` on an `int32[4]`",
     "Array indexing is bounds-checked.",
     [("TYPE", "; Element access (bounds-checked):")],
     "run:94",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32:v = a[raw v64(4i64)];
    exit v;"""),
     wrong="no check: the word past the array is read")

item("a04_index_negative", AREA_A,
     "`a[-1]` on an `int32[4]`",
     "The bounds check is one unsigned compare, so a negative index fails it.",
     [("TYPE", "%in_bounds = icmp ult i64 %idx, 4")],
     "run:94",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32:v = a[raw v64(-1i64)];
    exit v;"""),
     wrong="a signed check that passes -1 (the word before the array is read)")

item("a05_array_len", AREA_A,
     "`a.len` of an `int32[4]`",
     "`arr.len` is the count the type carries.",
     [("TYPE", "`arr.len` is the count the type carries — an `int64` constant, no load")],
     "run:0",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    if (a.len != 4i64) { exit 10i32; }
    exit 0i32;"""),
     wrong="a byte size, 16 (exit 10)")

item("a06_write_through_array_pointer", AREA_A,
     "a callee writing `(<-p)[0]` through an `int32[4]->`",
     "A pointer to the array lets a callee mutate the caller's array; its element is `(<-p)[i]`.",
     [("TYPE", "If you want to mutate an array inside a function or avoid copying, you must explicitly pass a pointer to it (`int32[4]->`)."),
      ("TYPE", "(`.`). Here the element is spelled `(<-p)[i]`, one level brought back. A")],
     "run:0",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    drop poke(@a);
    if (a[0i64] != 9i32) { exit 10i32; }
    exit 0i32;""", """func:poke = NIL(int32[4]->:p) never fails {
    (<-p)[0i64] = 9i32;
    pass NIL;
};"""),
     wrong="the write lost to a copy (exit 10): a write the program never sees")

item("a07_write_through_struct_pointer", AREA_A,
     "a callee writing `p.x` through a `Pt->`",
     "`.` dereferences a pointer once: `p.x` through `Pt->` writes the caller's struct.",
     [("TYPE", "`.` dereferences a pointer once. `p.x` where `p` is `T->` reaches the field;")],
     "run:0",
     main_("""    Pt:q = Pt{ x: 1i32, y: 2i32 };
    drop setx(@q);
    if (q.x != 9i32) { exit 10i32; }
    if (q.y != 2i32) { exit 11i32; }
    exit 0i32;""", """struct:Pt = { int32:x; int32:y; };
func:setx = NIL(Pt->:p) never fails {
    p.x = 9i32;
    pass NIL;
};"""),
     wrong="the write lost to a copy (exit 10)")

item("a08_range_view", AREA_A,
     "`a[1...3]` and `a[1..2]` of an `int32[4]`",
     "A range of a fixed array is a slice of those elements, with `.len`.",
     [("TYPE", "Constructed by ranging a fixed array or another slice — `arr[0...n]` — or, in"), REF_INCL, REF_EXCL],
     "run:0",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32[]:s = a[1i64...3i64];
    if (s.len != 2i64) { exit 10i32; }
    if (s[0i64] != 2i32) { exit 11i32; }
    if (s[1i64] != 3i32) { exit 12i32; }
    int32[]:t = a[1i64..2i64];
    if (t.len != 2i64) { exit 13i32; }
    if (t[1i64] != 3i32) { exit 14i32; }
    exit 0i32;"""),
     wrong="the range spellings swapped (10, 13), or the view offset wrong (11)")

item("a09_view_index_past_its_len", AREA_A,
     "`s[2]` on `s = a[1...3]` (len 2) of an `int32[4]`",
     "A slice's index is checked against the slice's own run-time `len`, not the storage under it.",
     [("TYPE", "- **Indexing is bounds-checked against the runtime `len`**, trapping to")],
     "run:94",
     main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32[]:s = a[1i64...3i64];
    int32:v = s[raw v64(2i64)];
    if (v == 4i32) { exit 10i32; }
    exit 11i32;"""),
     wrong="a check against the array under the view: the fourth element is read (exit 10)")

# ------------------------------------------------------------ F floats
AREA_F = "floats"

item("f01_decimal_sum_not_exact", AREA_F,
     "`0.1 + 0.2 == 0.3` on `flt64` literals",
     "Float arithmetic is IEEE (`fadd`), and a constant means what the run time means: "
     "0.1 + 0.2 is not 0.3.",
     [("TYPE", "- Arithmetic: `+`, `-`, `*`, `/`, `%` → `fadd`, `fsub`, `fmul`, `fdiv`, `frem`"),
      ("OP", "- Every other operation the folder evaluates is also the machine's answer:")],
     "run:0",
     main_("""    if ((0.1f64 + 0.2f64) == 0.3f64) { exit 10i32; }
    flt64:r = raw vf64(0.1f64) + raw vf64(0.2f64);
    if (r == 0.3f64) { exit 11i32; }
    if (r != (0.1f64 + 0.2f64)) { exit 12i32; }
    exit 0i32;"""),
     wrong="a folder computing in decimal: equal to 0.3 (exit 10), or unequal to the run time (12)")

item("f02_flt32_rounds_in_flt32", AREA_F,
     "`16777216.0f32 + 1.0f32`",
     "`flt32` is `float`: its arithmetic rounds at 24 significand bits.",
     [("TYPE", "| `flt32` | `float` | 4 bytes | 4 | everything |")],
     "run:0",
     main_("""    flt32:a = raw vf32(16777216.0f32);
    flt32:b = a + raw vf32(1.0f32);
    if (b != a) { exit 10i32; }
    exit 0i32;"""),
     wrong="the sum kept in double precision: 16777217 (exit 10)")

item("f03_sqrt_of_negative", AREA_F,
     "`#sqrt(-1.0)`",
     "`#sqrt` of a negative operand yields NaN, with no error channel.",
     [("BUILTIN", "IEEE semantics: a negative operand yields NaN, no error channel.")],
     "run:0",
     main_("""    flt64:r = #sqrt(raw vf64(-1.0f64));
    if (!(r != r)) { exit 10i32; }
    exit 0i32;"""),
     wrong="0 or a trap (10, or a failsafe code)")

# ------------------------------------------------------------ E exit
AREA_E = "`exit` and the leak check"

item("e01_exit_zero_with_live_wild", AREA_E,
     "`exit 0` with a live `wild` allocation",
     "A successful `exit` with live `wild` memory routes `WildLeak` (-4105) to failsafe.",
     [("CONTROL", "`wild` or `wildx` memory triggers the `failsafe` trap instead of returning;"),
      ("CONTROL", "non-empty `<wild-live>` routes `-4105` to `failsafe`, which may call")],
     "run:96",
     main_("""    wild int8->:p = alloc(16i64);
    exit 0i32;"""),
     wrong="a silent success (exit 0)")

item("e02_failure_exit_keeps_code", AREA_E,
     "`exit 3` with a live `wild` allocation",
     "The leak check runs on `exit 0` only: a failure exit keeps its code.",
     [("CONTROL", "runs on `exit 0` — a failure exit keeps its code, because overwriting an")],
     "run:3",
     main_("""    wild int8->:p = alloc(16i64);
    exit 3i32;"""),
     wrong="the code overwritten by the leak trap (96)")

item("e03_exit_outside_main_refused", AREA_E,
     "`exit` in an ordinary function",
     "`exit` may appear only in `main` or `failsafe`.",
     [("CONTROL", "**`exit code;`** terminates the process, and may appear only in `main` or")],
     "refuse",
     main_("""    drop f();
    exit 0i32;""", """func:f = NIL() never fails {
    exit 3i32;
};"""),
     wrong="accepted: a process exit from a library function (exit 3)")

# ------------------------------------------------------------ Q DEF-108 recall (PLAN 10.3)
AREA_Q = "DEF-108 recall (10.3): falling off the end"
REF_FLOW = ("CONTROL", "*   **Every path of a function body ends in one of these, or in `exit` (in")
NOTE_Q = ("DEF-108 (KNOWN_DEFECTS.md): at the baseline, whose CONTROL_REFERENCE has no FLOW-001 "
          "sentence, the shape compiles and answers a zero value, which is the defect the recall "
          "must flag; HUNT2 carries 1.6.0 step 5c and must refuse it with FLOW-001.")

item("q01_empty_body", AREA_Q,
     "an empty body declared to return int64",
     "A body that can reach its own closing brace is refused (FLOW-001).",
     [REF_FLOW], "refuse:NITPICK-FLOW-001",
     main_("""    if (raw f() != 5i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64() never fails {
};"""),
     wrong="accepted: the empty body returns 0 (exit 10)", expect_base="run:10", note=NOTE_Q)

item("q02_missing_path", AREA_Q,
     "a `never fails` function whose `if` has no `else` and no pass after it",
     "Every path ends in `pass`, `fail`, `exit` or a trap; an `if` without `else` completes.",
     [REF_FLOW, ("CONTROL", "walk is conservative towards refusal: an `if` without `else` completes, an")],
     "refuse:NITPICK-FLOW-001",
     main_("""    if (raw f(raw v64(0i64)) != 5i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64(int64:x) never fails {
    if (x > 0i64) { pass 1i64; }
};"""),
     wrong="accepted: the missing path returns 0 (exit 10)", expect_base="run:10", note=NOTE_Q)

item("q03_fallible_missing_path", AREA_Q,
     "a fallible function with a path that names no failure",
     "A fallible function names its failure on every path.",
     [REF_FLOW, ("CONTROL", "`NIL` function passes `NIL`, a fallible function names its failure on every")],
     "refuse:NITPICK-FLOW-001",
     main_("""    Result<int64>:r = g(raw v64(0i64));
    if (r.is_error) { exit 0i32; }
    exit 12i32;""", """func:g = int64(int64:x) {
    if (x > 0i64) { pass 1i64; }
};"""),
     wrong="accepted: the missing path is a SUCCESS carrying 0 (exit 12)", expect_base="run:12", note=NOTE_Q)

item("q04_main_without_exit", AREA_Q,
     "`main` that can reach its closing brace",
     "`main` exits on every path.",
     [REF_FLOW, ("CONTROL", "path, `main` exits. There is no implicit return and no implicit value — until")],
     "refuse:NITPICK-FLOW-001",
     """func:main = int32(cstring[]:_~argv) {
    if (raw vb(false)) { exit 7i32; }
};
""",
     wrong="accepted: `main` falls off and the process exits 0, a silent success",
     expect_base="run:0", note=NOTE_Q)

item("q05_string_missing_path", AREA_Q,
     "a `string` function with a missing path",
     "No implicit value: a `string` function's missing path is refused.",
     [REF_FLOW], "refuse:NITPICK-FLOW-001",
     main_("""    string:s = raw f(raw vb(false));
    if (s.len == 0i64) { exit 10i32; }
    exit 11i32;""", """func:f = string(bool:b) never fails {
    if (b) { pass "x"; }
};"""),
     wrong="accepted: the missing path returns an empty string (exit 10)", expect_base="run:10", note=NOTE_Q)

item("q06_bool_missing_path", AREA_Q,
     "a `bool` function with a missing path",
     "No implicit value: a `bool` function's missing path is refused.",
     [REF_FLOW], "refuse:NITPICK-FLOW-001",
     main_("""    if (!(raw f(raw vb(false)))) { exit 10i32; }
    exit 11i32;""", """func:f = bool(bool:b) never fails {
    if (b) { pass false; }
};"""),
     wrong="accepted: the missing path returns false (exit 10)", expect_base="run:10", note=NOTE_Q)

item("q07_nil_function_falls_off", AREA_Q,
     "a `NIL` function that falls off",
     "A `NIL` function passes `NIL`.",
     [("CONTROL", "`NIL` function passes `NIL`, a fallible function names its failure on every")],
     "refuse:NITPICK-FLOW-001",
     main_("""    drop f();
    exit 0i32;""", """func:f = NIL() never fails {
    int32:x = raw v32(1i32);
    discard(x);
};"""),
     wrong="accepted (nothing observable: NIL carries no value)", expect_base="run:0", note=NOTE_Q)

item("q08_while_true_never_completes", AREA_Q,
     "a function whose body is `while (true)` passing inside, with nothing after",
     "A `while (true)` with no `break` never completes, so nothing after it is needed.",
     [("CONTROL", "arm ending in `fall` continues into the next arm), a `while (true)` with no")],
     "run:0",
     main_("""    if (raw f() != 5i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64() never fails {
    // the loop passes on its first trip -- the shape under test
    while (true) unbounded { pass 5i64; }
};"""),
     wrong="refused FLOW-001: an over-restriction")

item("q09_if_else_both_pass", AREA_Q,
     "an `if`/`else` whose arms both pass",
     "An `if`/`else` completes only if an arm does: two passing arms leave nothing after.",
     [("CONTROL", "`if`/`else` completes if either arm does, a `pick` if any arm's body does (an")],
     "run:0",
     main_("""    if (raw f(raw v64(0i64)) != 2i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64(int64:x) never fails {
    if (x > 0i64) { pass 1i64; } else { pass 2i64; }
};"""),
     wrong="refused FLOW-001: an over-restriction")

item("q10_pick_all_arms_pass", AREA_Q,
     "a `pick` whose arms all pass",
     "A `pick` completes only if an arm's body does: all-passing arms leave nothing after.",
     [("CONTROL", "`if`/`else` completes if either arm does, a `pick` if any arm's body does (an")],
     "run:0",
     main_("""    if (raw f(raw v32(2i32)) != 20i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64(int32:x) never fails {
    pick (x) { (1i32) { pass 10i64; }, (2i32) { pass 20i64; }, (*) { pass 0i64; } }
};"""),
     wrong="refused FLOW-001: an over-restriction")

item("q11_for_loop_completes", AREA_Q,
     "a function whose last statement is a `for` that passes inside",
     "Every loop other than `while (true)` completes as a whole, so a pass is still owed after it.",
     [("CONTROL", "`break` never completes, every other loop and `when` completes as a whole.")],
     "refuse:NITPICK-FLOW-001",
     main_("""    if (raw f() != 0i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64() never fails {
    for (int64:i in 0i64...3i64) { pass i; }
};"""),
     wrong="accepted (the first trip happens to pass, so the answer is right here)",
     expect_base="run:0", note=NOTE_Q)

# ------------------------------------------------------------ untestable items
item("u01_fd_vacant_to_int64", AREA_C,
     "`o.value => int64` of a vacant `OwnedFd`",
     "What a vacant descriptor converts to.", [("DECISIONS", "\"did I check for `-1`?\" bug class does not exist, because `-1` is not")],
     None, untestable="D-042 says -1 is not representable as an `fd`, while D-225 stores -1 in a "
                      "vacant `OwnedFd`; no sentence says what the conversion of that value gives "
                      "(M9 measured 4 294 967 295, the i32 -1 zero-extended).")
item("u02_fallback_laziness", AREA_R,
     "whether `?|` evaluates its fallback on success",
     "Evaluation of `?|`'s right side.", [("OP", "`expr ?| fallback` yields `expr`'s value, or `fallback` if it errored. D-167")],
     None, untestable="No sentence states whether `?|`'s fallback is evaluated when the call "
                      "succeeds (`??`'s laziness is stated; `?|`'s is not).")
item("u03_same_scope_redeclaration", AREA_H,
     "a second declaration of a name in the same scope",
     "Same-scope redeclaration.", [REF_SHADOW],
     None, untestable="No reference sentence states the rule for two declarations of one name "
                      "in one scope (the compiler's own notes call it RESOLVE-001).")
item("u04_float_to_string", AREA_T,
     "the text a float interpolates to",
     "Float `ToString`'s format.", [("TYPE", "### 1.4 IEEE Floating Point (final form: D-143, 0.9.4)")],
     None, untestable="No reference sentence states a float's decimal rendering (shortest "
                      "round-trip is D-193's implementation, not a stated format).")
item("u05_int_to_enum_out_of_range", AREA_C,
     "`k =>! Color` for a k that is no tag",
     "An unchecked tag manufacture outside the declared tags.",
     [("TYPE", "; `intN =>! enum`, which manufactures a tag (an assertion, hence the bang; `=>`")],
     None, untestable="The text calls `intN =>! enum` an assertion and does not say what a "
                      "value that is no tag becomes.")
item("u06_power_operator", AREA_V,
     "`**`",
     "Exponentiation.", [("OP", "| `**` | Power | Exponentiation (Standard Library expansion). | `2 ** 8` |")],
     None, untestable="`**` is a 'Standard Library expansion', not in the compiler; nothing "
                      "states its overflow rule.")


# ================================================================ the writer
def doc_lines(tree, doc):
    path = os.path.join(ROOT, ".work", tree, DOCS[doc])
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def locate(lines, quote):
    """Lines holding `quote`; a quote starting with `^` must be the whole (stripped) line."""
    if quote.startswith("^"):
        return [i + 1 for i, l in enumerate(lines) if l.strip() == quote[1:]]
    return [i + 1 for i, l in enumerate(lines) if quote in l]


def cite(refs):
    """-> list of (doc, quote, hunt2_line, base_line_or_None); fails loudly on a quote that
    is absent at HUNT2 or ambiguous there."""
    out = []
    for doc, quote in refs:
        h = locate(doc_lines("hunt2", doc), quote)
        if len(h) != 1:
            raise SystemExit("citation %s %r: %d matches at HUNT2" % (doc, quote, len(h)))
        b = locate(doc_lines("base", doc), quote)
        out.append((doc, quote, h[0], b[0] if len(b) == 1 else None))
    return out


def failsafe(src):
    arms = ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS]
    for e in sorted(set(re.findall(r"\berror:(E(\d));", src))):
        arms.append("        (%s) { exit %di32; }," % (e[0], 80 + int(e[1])))
    arms.append("        (*) { exit 99i32; }")
    return "func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) + \
        "\n    }\n    exit 9i32;\n};\n"


def helpers(src):
    out = []
    for name, t in HELPERS.items():
        if re.search(r"\b%s\(" % name, src):
            out.append("func:%s = %s(%s:x) never fails { pass x; };" % (name, t, t))
    return "\n".join(out)


def program(it, cites):
    head = ["// M10 %s -- %s" % (it["id"], it["title"]),
            "// claim: " + it["claim"]]
    for doc, quote, hl, bl in cites:
        head.append("// ref: %s:%d  \"%s\"" % (DOCS[doc], hl, quote.lstrip("^").strip()))
    head.append("// expect: " + it["expect"] +
                ("   (at the baseline: %s)" % it["expect_base"] if it["expect_base"] else ""))
    head.append("// wrong: " + it["wrong"])
    src = it["src"]
    body = "\n".join(head) + "\nmod:%s;\n\n" % it["id"]
    h = helpers(src)
    if h:
        body += h + "\n\n"
    return body + src + "\n" + failsafe(src)


def md_cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def main():
    refs_only = "--refs-only" in sys.argv
    ids = [it["id"] for it in ITEMS]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit("duplicate ids: %s" % sorted(dup))
    for it in ITEMS:
        it["cites"] = cite(it["refs"])
    if refs_only:
        for it in ITEMS:
            for doc, quote, hl, bl in it["cites"]:
                print("%-40s %-12s hunt2:%-6d base:%s" % (it["id"], doc, hl, bl if bl else "ABSENT"))
        return
    pdir = os.path.join(OUT, "programs")
    os.makedirs(pdir, exist_ok=True)
    for f in os.listdir(pdir):
        if f.endswith(".npk"):
            os.remove(os.path.join(pdir, f))
    rows = ["id\tfile\tarea\texpect_hunt2\texpect_base"]
    for it in ITEMS:
        if it["untestable"]:
            continue
        fn = "programs/%s.npk" % it["id"]
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(program(it, it["cites"]))
        rows.append("\t".join([it["id"], fn, it["area"], it["expect"], it["expect_base"] or it["expect"]]))
    with open(os.path.join(OUT, "EXPECT.tsv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    # the checklist
    areas = []
    for it in ITEMS:
        if it["area"] not in areas:
            areas.append(it["area"])
    testable = [it for it in ITEMS if not it["untestable"]]
    L = ["# M10 checklist: silent wrong answers",
         "",
         "Written by `gen/m10.py` (regenerate with `python3 gen/m10.py`). Each item states a claim,",
         "quotes the reference sentence that states the right answer, and carries the verdict",
         "expected from that TEXT, written before the program's first run (PLAN.md 10.2).",
         "Line numbers are located by the quoted text: the first at HUNT2 `9126350`, the second at",
         "the baseline `c3bdae2` (`absent` where the baseline's text does not hold the sentence).",
         "Paths are the compiler's `meta/specs/`.",
         "",
         "- **Expected** `run:N` = compiled (npkc 0) and both legs exit N; `refuse` = npkc 1;",
         "  `refuse:CODE` = npkc 1 naming CODE. Exit 0 is the reference's answer, 10-59 name the",
         "  check that saw a wrong value, a trap exits its `failsafe` arm (IntOverflow 93,",
         "  OutOfBounds 94, WildLeak 96, DivByZero 97, DivOverflow 98, TbbErr 110, ShiftRange 111,",
         "  CastRange 112, BadStep 113; a program's own error `E<k>` exits 80+k).",
         "- **Wrong** is what an implementation that gets the claim wrong would answer: the item is a",
         "  case the wrong implementation gets wrong.",
         "",
         "**%d items: %d testable, %d untestable** (each with its reason, at the end)."
         % (len(ITEMS), len(testable), len(ITEMS) - len(testable)),
         ""]
    for a in areas:
        its = [it for it in ITEMS if it["area"] == a and not it["untestable"]]
        if not its:
            continue
        L.append("## %s (%d)" % (a, len(its)))
        L.append("")
        L.append("| id | case | claim | reference (HUNT2 line / base line) | expected | wrong |")
        L.append("|---|---|---|---|---|---|")
        for it in its:
            refs = "<br>".join("%s:%d / %s — “%s”" % (DOCS[d].split("/")[-1].replace(".md", ""), hl,
                                                        bl if bl else "absent", md_cell(q.lstrip("^").strip()))
                               for d, q, hl, bl in it["cites"])
            exp = it["expect"] + ("<br>base: " + it["expect_base"] if it["expect_base"] else "")
            claim = md_cell(it["claim"]) + (" *" + md_cell(it["note"]) + "*" if it["note"] else "")
            L.append("| `%s` | %s | %s | %s | %s | %s |" % (it["id"], md_cell(it["title"]), claim, refs,
                                                          exp, md_cell(it["wrong"])))
        L.append("")
    L.append("## Untestable (%d)" % (len(ITEMS) - len(testable)))
    L.append("")
    L.append("| id | case | why it cannot be tested from the text |")
    L.append("|---|---|---|")
    for it in ITEMS:
        if it["untestable"]:
            L.append("| `%s` | %s | %s |" % (it["id"], md_cell(it["title"]), md_cell(it["untestable"])))
    L.append("")
    with open(os.path.join(OUT, "CHECKLIST.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("items %d: testable %d, untestable %d; programs in m10/programs/" %
          (len(ITEMS), len(testable), len(ITEMS) - len(testable)))


if __name__ == "__main__":
    main()
