"""M11 claims: TYPE_REFERENCE.md lines 1-660 at HUNT2 (sections 1 to 5a).

Scalars, booleans, signed/unsigned integers, IEEE floats, characters, strings
and cstring, the wide integers, twisted fixed point and dim256. Every
expectation below is written from the reference's TEXT, before any program ran.
"""
from m11lib import *

D = "TYPE"


# ------------------------------------------------------------------ helpers
# `ir:` regexes are scoped to ONE function the program defines: the emitted .ll
# declares every overflow intrinsic up front and carries the prelude, so a
# file-wide search for an intrinsic's name would match whatever the program says.
def _fn(name):
    """the `define` line of the function whose symbol ends in `name`"""
    return r'^define [^@\n]*@"?(?:[\w$]+\.)*' + name + r'"?\('


def _body(p):
    """a lookahead: the rest of the current function (up to its closing `}`) contains p"""
    return r"(?=(?:(?!\n\}).)*?" + p + ")"


def ir_fn(name, *pats):
    """ir: the body of function `name` contains every pattern"""
    return "ir:(?s)" + _fn(name) + "".join(_body(p) for p in pats)


def ir_fn_lacks(name, has, lacks):
    """ir: function `name` exists, contains every pattern in `has`, and not `lacks`"""
    return "ir:(?s)" + _fn(name) + "".join(_body(p) for p in has) + \
        r"(?!(?:(?!\n\}).)*?" + lacks + ")"


def sig(name, ret, params):
    """a fragment: function `name` is defined returning `ret` with parameters opening `params`"""
    return r'^define [^@\n]*' + ret + r' @"?(?:[\w$]+\.)*' + name + r'"?\(' + params


def ir_all(*frags):
    """ir: every fragment matches somewhere in the file"""
    return r"ir:(?s)\A" + "".join("(?=.*?" + f + ")" for f in frags)


def fs_without(*omit):
    """a failsafe naming every identity of TRAPS except `omit`, with a `(*)` arm"""
    arms = ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS if n not in omit]
    arms.append("        (*) { exit 99i32; }")
    return ("func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) +
            "\n    }\n    exit 9i32;\n};\n")


def layout(types, size, align, decls="", body=""):
    """a run program: #size_of each type is `size`, and after an int8 it sits at
    offset `align` (so {int8, T} is align + size bytes)"""
    d, b = [], []
    code = 10
    for i, t in enumerate(types):
        if not t.replace("_", "").isalnum():          # a generic or array type: wrap it
            d.append("struct:S%d = { %s:v; };" % (i, t))
        d.append("struct:P%d = { int8:a; %s:v; };" % (i, t))
    for i, t in enumerate(types):
        what = t if t.replace("_", "").isalnum() else "S%d" % i
        b.append("    if (#size_of<" + what + ">() != " + str(size) + "i64) { exit " +
                 str(code) + "i32; }")
        b.append("    if (#size_of<P" + str(i) + ">() != " + str(align + size) +
                 "i64) { exit " + str(code + 1) + "i32; }")
        code += 2
    src = main_("\n".join(b) + ("\n" + body.rstrip() if body.strip() else "") +
                "\n    exit 0i32;", "\n".join(d) + ("\n" + decls if decls else ""))
    return src


def layout_wrong(types, size, align):
    out = []
    code = 10
    for t in types:
        out.append("%d: %s is not %d bytes; %d: it does not sit at offset %d after an int8 "
                   "(an alignment other than %d)" % (code, t, size, code + 1, align, align))
        code += 2
    return "; ".join(out)


# ------------------------------------------------------------------ header
claim("ty0003", D, 3, "No C/C++ in any form", "rule",
      "No type is defined in C or C++: each is handwritten LLVM IR (Tier 0) or Nitpick source (Tier 1+).",
      untestable="[tree] where a type's definition is written is a fact about the compiler's source tree")

claim("ty0004", D, 4, "No libc", "rule",
      "Programs use no libc: a program that allocates (a concatenation, a to_cstring) declares no libc "
      "allocator, stdio or string function in its IR.",
      expect=r"ir!:^declare [^\n]*@(?:malloc|calloc|realloc|free|printf|puts|fopen|fwrite|strlen)\(",
      src=main_("""    string:a = "ab";
    string:b = string_concat(a, "cd");
    Result<cstring>:r = to_cstring(b);
    if (r.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="the IR declares malloc/free/printf/strlen or another libc symbol",
      note="the runtime floor defines its own memcpy/memset/fmod/__divti3 (hand-written IR); those names are left out")

claim("ty0017", D, 17, "These map directly to LLVM primitive types", "rule",
      "The fundamental scalars map directly to LLVM primitive types: an int16 function is `i16` in, `i16` out, "
      "and a flt32 one `float`.",
      expect=ir_all(sig("m11s16", r"\bi16", "i16 "), sig("m11f32", r"\bfloat", "float ")),
      src=main_("""    if (raw m11s16(raw v16(7i16)) != 7i16) { exit 10i32; }
    if (raw m11f32(raw vf32(1.5f32)) != 1.5f32) { exit 11i32; }
    exit 0i32;""", """func:m11s16 = int16(int16:x) never fails { pass x; };
func:m11f32 = flt32(flt32:x) never fails { pass x; };"""),
      wrong="a scalar boxed or widened: the signature is not i16/float")

# ------------------------------------------------------------------ 1.1 bool
claim("ty0023", D, 23, "| `bool` | `i1` (stored as `i8`) | 1 byte | 1 |", "row",
      "`bool` is 1 byte with alignment 1, and `true` is 1, `false` 0.",
      expect="run:0",
      src=layout(["bool"], 1, 1, body="""    if ((raw vb(true) => int32) != 1i32) { exit 12i32; }
    if ((raw vb(false) => int32) != 0i32) { exit 13i32; }"""),
      wrong="10: bool is not 1 byte; 11: {int8, bool} is not 2 bytes (alignment above 1); 12/13: true/false not 1/0")

claim("ty0026", D, 26, "`&&` (short-circuit AND), `||` (short-circuit OR)", "rule",
      "`&&` and `||` short-circuit: the right side is not evaluated when the left decides.",
      m10="x04_short_circuit")

claim("ty0027", D, 27, "Comparison: `==`, `!=`", "rule",
      "`bool` compares with `==` and `!=`.",
      expect="run:0",
      src=main_("""    bool:t = raw vb(true);
    bool:f = raw vb(false);
    if (!(t == raw vb(true))) { exit 10i32; }
    if (t == f) { exit 11i32; }
    if (!(t != f)) { exit 12i32; }
    if (f != raw vb(false)) { exit 13i32; }
    exit 0i32;"""),
      wrong="refused, or an equality answered wrongly (10-13)")

claim("ty0027b", D, 27, "Comparison: `==`, `!=`", "rule",
      "`bool` has `==` and `!=` and no ordering: `<`/`>` on bools is refused.",
      m10="m10_bool_ordering_refused")

claim("ty0028", D, 28, "No arithmetic operations", "rule",
      "`bool` has no arithmetic: `true + false` is refused.",
      expect="refuse",
      src=main_("""    bool:c = raw vb(true) + raw vb(false);
    if (c) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: bool arithmetic on the byte (exit 10 or 11)")

claim("ty0029", D, 29, "Cast: `bool => int32` yields 0 or 1", "rule",
      "`bool => int32` yields 0 or 1.", m10="c14_bool_to_int")

claim("ty0032", D, 32, "```llvm", "example",
      "A bool local is an `i8` alloca, and a branch on it truncates the loaded `i8` to `i1`.",
      expect=ir_fn("m11bl", r"alloca i8\b", r"trunc i8 %\S+ to i1"),
      src=main_("""    if (raw m11bl(raw vb(true)) != 1i32) { exit 10i32; }
    exit 0i32;""", """func:m11bl = int32(bool:x) never fails {
    bool:y = x;
    if (y) { pass 1i32; }
    pass 0i32;
};"""),
      wrong="a bool stored as i1, or tested another way than trunc to i1",
      note="an IR-pattern block: the program checks its storage and branch shape, not register names")

# ------------------------------------------------------------------ 1.2 signed
for ln, t, sz in ((47, "int8", 1), (48, "int16", 2), (49, "int32", 4), (50, "int64", 8)):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` is %d byte%s with alignment %d." % (t, sz, "" if sz == 1 else "s", sz),
          expect="run:0", src=layout([t], sz, sz), wrong=layout_wrong([t], sz, sz))

claim("ty0053", D, 53, "Arithmetic: `+`, `-`, `*` — **overflow TRAPS**", "rule",
      "Plain-integer `+` traps IntOverflow on overflow.", m10="o01_int32_add")
claim("ty0053b", D, 53, "Arithmetic: `+`, `-`, `*` — **overflow TRAPS**", "rule",
      "Plain-integer `-` traps IntOverflow on overflow.", m10="o02_int32_sub")
claim("ty0053c", D, 53, "Arithmetic: `+`, `-`, `*` — **overflow TRAPS**", "rule",
      "Plain-integer `*` traps IntOverflow on overflow.", m10="o03_int32_mul")
claim("ty0053d", D, 53, "Arithmetic: `+`, `-`, `*` — **overflow TRAPS**", "rule",
      "Only an overflow traps: a result equal to a type's maximum or minimum is a value.",
      m10="o17_edges_do_not_trap")

claim("ty0054", D, 54, "`IntOverflow` (−4110)", "rule",
      "IntOverflow's code is -4110: the guard of a computed int32 `+` routes -4110 to failsafe.",
      expect=ir_fn("m11add", r"-4110\b"),
      src=main_("""    if (raw m11add(raw v32(1i32), raw v32(2i32)) != 3i32) { exit 10i32; }
    exit 0i32;""", "func:m11add = int32(int32:a, int32:b) never fails { pass a + b; };"),
      wrong="another number carried to the trap",
      note="the numeric code is visible only in the IR (Error is nominal: no cast out of it)")

claim("ty0056", D, 56, "Lowers through `llvm.{s,u}{add,sub,mul}.with.overflow.iN`", "rule",
      "Signed `+ - *` lower through llvm.sadd/ssub/smul.with.overflow at the operand width.",
      expect=ir_fn("m11s", r"@llvm\.sadd\.with\.overflow\.i32\(", r"@llvm\.ssub\.with\.overflow\.i32\(",
                   r"@llvm\.smul\.with\.overflow\.i32\("),
      src=main_("""    if (raw m11s(raw v32(3i32), raw v32(4i32)) != -5i32) { exit 10i32; }
    exit 0i32;""", "func:m11s = int32(int32:a, int32:b) never fails { pass ((a + b) - (a * b)); };"),
      wrong="a widened compute-and-compare, or a missing guard")

claim("ty0057", D, 57, "Signedness picks the family", "rule",
      "Unsigned `+ - *` lower through the unsigned family llvm.uadd/usub/umul.with.overflow and not the signed one.",
      expect=ir_fn_lacks("m11u", [r"@llvm\.uadd\.with\.overflow\.i32\(", r"@llvm\.usub\.with\.overflow\.i32\(",
                                  r"@llvm\.umul\.with\.overflow\.i32\("],
                         r"@llvm\.s(?:add|sub|mul)\.with\.overflow"),
      src=main_("""    if (raw m11u(raw vu32(3u32), raw vu32(4u32)) != 5u32) { exit 10i32; }
    exit 0i32;""", "func:m11u = uint32(uint32:a, uint32:b) never fails { pass ((a * b) - (a + b)); };"),
      wrong="an unsigned operation guarded by the signed intrinsics (a wrong overflow bit)")

claim("ty0058", D, 58, "legalized at every width the language has", "rule",
      "The overflow trap holds at the wide widths: an int128 `+` past the maximum traps IntOverflow.",
      m10="o16_int128_add")

claim("ty0058b", D, 58, "`int8` through `int4096`", "rule",
      "The overflow trap holds at the top of the ladder: an int4096 `+` past the maximum traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    int4096:one = raw w4096(1i4096);
    int4096:h = one << raw w4096(4094i4096);
    int4096:mx = h + (h - one);
    int4096:o = mx + one;
    if (o < raw w4096(0i4096)) { exit 10i32; }
    exit 11i32;""", "func:w4096 = int4096(int4096:x) never fails { pass x; };"),
      wrong="wraps to the minimum (exit 10), or another value with no trap (11)")

claim("ty0059", D, 59, "A `simd`'s integer lanes go through the vector form", "rule",
      "A simd's integer lane that overflows traps IntOverflow as its scalar does.",
      m10="o22_simd_lane_overflow")

claim("ty0059b", D, 59, "`.<N x iW>`", "rule",
      "A simd<int32, 4> `+` lowers through the vector overflow intrinsic llvm.sadd.with.overflow.v4i32.",
      expect=ir_fn("m11v", r"@llvm\.sadd\.with\.overflow\.v4i32\("),
      src=main_("""    simd<int32, 4>:x = simd(raw v32(1i32), 2i32, 3i32, 4i32);
    if (raw m11v(x, x) != 2i32) { exit 10i32; }
    exit 0i32;""", """func:m11v = int32(simd<int32, 4>:a, simd<int32, 4>:b) never fails {
    simd<int32, 4>:s = a + b;
    pass s[0i64];
};"""),
      wrong="per-lane scalar intrinsics, or a bare vector add")

claim("ty0060", D, 60, "overflow lanes folded to one any-lane test", "rule",
      "The lanes' overflow bits are folded into one any-lane test.",
      untestable="[internal] how the overflow bits are combined changes no outcome, and the text names no instruction to look for")

claim("ty0061", D, 61, "traps per fold step", "rule",
      "An integer simd `.sum()` whose total overflows traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    simd<int32, 4>:v = simd(raw v32(1073741824i32), 1073741824i32, 0i32, 0i32);
    int32:s = v.sum();
    if (s < 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="the fold wraps to -2147483648 (exit 10), or another value (11)")

claim("ty0061b", D, 61, "traps per fold step", "rule",
      "`.sum()` traps per fold step: a step that overflows traps even when the lanes' total fits.",
      expect="trap:IntOverflow",
      src=main_("""    simd<int32, 4>:v = simd(raw v32(2147483647i32), 1i32, 1i32, -3i32);
    int32:s = v.sum();
    if (s == 2147483646i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="only the total is checked (or a wider accumulator): 2147483646 with no trap (exit 10)",
      note="the text names no fold order; the lanes make a left fold, a pairwise tree and a halving tree each "
           "overflow at a step (a right fold would not). TYPE:1494 (outside this range) says 'the fold through "
           "the scalar `+`'")

claim("ty0062", D, 62, "is checked AFTER every write", "rule",
      "A limit<Rules> integer binding is checked after every write: an assignment its rule refuses traps LimitViolated.",
      expect="trap:LimitViolated",
      src=main_("""    limit<R> int64:x = raw v64(5i64);
    x = raw v64(200i64);
    if (x == 200i64) { exit 10i32; }
    exit 11i32;""", "Rules<int64>:R = { $ >= 0i64, $ <= 100i64 };"),
      wrong="the rule checked only at the declaration: x holds 200 (exit 10)")

claim("ty0063", D, 63, "`LimitViolated` (−4111)", "rule",
      "LimitViolated's code is -4111: the check after a computed write to a limit binding routes -4111 to failsafe.",
      expect=ir_fn("m11lim", r"-4111\b"),
      src=main_("""    if (raw m11lim(raw v64(7i64)) != 7i64) { exit 10i32; }
    exit 0i32;""", """Rules<int64>:R = { $ >= 0i64, $ <= 100i64 };
func:m11lim = int64(int64:v) never fails {
    limit<R> int64:x = 0i64;
    x = v;
    pass x;
};"""),
      wrong="another number carried to the trap, or no check emitted")

claim("ty0065", D, 65, "their `limit` rows are decided by z3", "rule",
      "An integer limit row is decided by z3, and a discharged one elides into one llvm.assume over the rule's range clauses.",
      untestable="[z3] rows are decided and elided only under `npkg verify` with the pinned z3")

claim("ty0067", D, 67, "**Unary `-` is `0 - x`**", "rule",
      "Unary `-` traps IntOverflow on the most negative value.", m10="o04_int32_negate_min")

claim("ty0069", D, 69, "**`x += y` traps identically**", "rule",
      "The compound `+=` traps IntOverflow exactly as `+` does.", m10="o12_compound_add")

claim("ty0071", D, 71, "**Bit operations are unchanged**", "rule",
      "Bit operations have nothing to overflow: `<<` loses the bits past the width and does not trap.",
      m10="o18_shift_loses_bits_no_trap")

claim("ty0073", D, 73, "`x << n` and `x >> n` are defined", "rule",
      "`x << n` is defined for 0 <= n < width only: a computed amount equal to the width traps ShiftRange.",
      m10="s04_shift_amount_equals_width")
claim("ty0073b", D, 73, "`x << n` and `x >> n` are defined", "rule",
      "The amount rule holds for `>>` too: a computed amount equal to the width traps ShiftRange.",
      m10="s06_right_shift_amount_width")

claim("ty0074", D, 74, "a known amount outside it is TYPE-070", "rule",
      "A known shift amount outside 0 <= n < width is NITPICK-TYPE-070 at the `<<`.",
      m10="s07_shift_literal_amount_refused")

claim("ty0075", D, 75, "the shift (both spellings)", "rule",
      "A known amount outside the range is TYPE-070 at a `>>` as at a `<<`.",
      expect="refuse:NITPICK-TYPE-070",
      src=main_("""    uint8:x = raw vu8(128u8) >> 8u8;
    if (x == 0u8) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a `>>` by the width yields 0 (exit 10) or the masked shift (11)",
      note="'both spellings' is ambiguous: `<<`/`>>`, or the plain and compound forms; ty0075b takes the other reading")

claim("ty0075b", D, 75, "the shift (both spellings)", "rule",
      "A known amount outside the range is TYPE-070 at the compound `<<=` as at `<<`.",
      expect="refuse:NITPICK-TYPE-070",
      src=main_("""    int32:x = raw v32(1i32);
    x <<= 32i32;
    if (x == 1i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: the compound spelling escapes the static check (exit 10 or 11)")

claim("ty0075c", D, 75, "a computed one is guarded by one unsigned", "rule",
      "A computed shift amount is guarded by one unsigned compare against the width (`icmp ult n, W`).",
      expect=ir_fn("m11shl", r"icmp ult i32 %\S+, 32\b", r"\bshl i32 "),
      src=main_("""    if (raw m11shl(raw v32(1i32), raw v32(3i32)) != 8i32) { exit 10i32; }
    exit 0i32;""", "func:m11shl = int32(int32:a, int32:n) never fails { pass a << n; };"),
      wrong="no guard, or a signed compare that lets a negative amount through")

claim("ty0076", D, 76, "traps `ShiftRange` (−4115)", "rule",
      "ShiftRange's code is -4115: the guard of a computed shift amount routes -4115 to failsafe.",
      expect=ir_fn("m11shl", r"-4115\b"),
      src=main_("""    if (raw m11shl(raw v32(1i32), raw v32(3i32)) != 8i32) { exit 10i32; }
    exit 0i32;""", "func:m11shl = int32(int32:a, int32:n) never fails { pass a << n; };"),
      wrong="another number carried to the trap")

claim("ty0077", D, 77, "eliding the guard where proven", "rule",
      "The shift-range obligation elides the guard where it is proven.",
      untestable="[z3] obligations are discharged only under `npkg verify` with the pinned z3")

claim("ty0078", D, 78, "**`/` and `%` by zero still trap**", "rule",
      "Integer `/` by zero traps DivByZero.", m10="v03_div_by_zero")
claim("ty0078b", D, 78, "**`/` and `%` by zero still trap**", "rule",
      "Integer `%` by zero traps DivByZero.", m10="v04_rem_by_zero")
claim("ty0078c", D, 78, "signed `/` adds the", "rule",
      "Signed `/` of the minimum by -1 traps DivOverflow.", m10="v05_min_div_minus_one")
claim("ty0078d", D, 78, "**`/` and `%` by zero still trap**", "rule",
      "The compound `/=` by zero traps DivByZero as `/` does.", m10="v10_compound_div_by_zero")

claim("ty0079", D, 79, "On `tbb` both yield ERR", "rule",
      "On tbb, `/` and `%` by zero yield ERR and do not trap.", m10="v18_tbb_div_by_zero_is_err")

claim("ty0080", D, 80, "**There are no sub-byte widths.**", "rule",
      "There are no sub-byte integer widths: `int4` is not a type.",
      expect="refuse",
      src=main_("""    int4:x = 1;
    if (x == 1) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: int4 is a type (exit 10 or 11)")

claim("ty0081", D, 81, "twins were STRUCK at D-231", "rule",
      "The unsigned sub-byte twins were struck too: `uint2` is not a type.",
      expect="refuse",
      src=main_("""    uint2:x = 1;
    if (x == 1) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: uint2 is a type (exit 10 or 11)")

claim("ty0083", D, 83, "a range-limited byte is `limit<Rules>`", "rule",
      "A range-limited byte is a limit<Rules> binding of a byte type: writing a value outside its rule traps LimitViolated.",
      expect="trap:LimitViolated",
      src=main_("""    limit<Two> uint8:b = raw vu8(3u8);
    b = raw vu8(4u8);
    if (b == 4u8) { exit 10i32; }
    exit 11i32;""", "Rules<uint8>:Two = { $ <= 3u8 };"),
      wrong="the byte holds 4 (exit 10): the rule is not checked on a byte")

claim("ty0084", D, 84, "The ladder is `int8` … `int4096`", "rule",
      "The signed ladder is int8 through int4096: each rung exists and its sign bit is bit W-1 (1 << (W-1) is negative).",
      expect="run:0",
      src=main_("""    if (!((raw v8(1i8) << raw v8(7i8)) < 0i8)) { exit 10i32; }
    if (!((raw v16(1i16) << raw v16(15i16)) < 0i16)) { exit 11i32; }
    if (!((raw v32(1i32) << raw v32(31i32)) < 0i32)) { exit 12i32; }
    if (!((raw v64(1i64) << raw v64(63i64)) < 0i64)) { exit 13i32; }
    if (!((raw vi128(1i128) << raw vi128(127i128)) < 0i128)) { exit 14i32; }
    if (!((raw w256(1i256) << raw w256(255i256)) < 0i256)) { exit 15i32; }
    if (!((raw w512(1i512) << raw w512(511i512)) < 0i512)) { exit 16i32; }
    if (!((raw w1024(1i1024) << raw w1024(1023i1024)) < 0i1024)) { exit 17i32; }
    if (!((raw w2048(1i2048) << raw w2048(2047i2048)) < 0i2048)) { exit 18i32; }
    if (!((raw w4096(1i4096) << raw w4096(4095i4096)) < 0i4096)) { exit 19i32; }
    exit 0i32;""", """func:w256 = int256(int256:x) never fails { pass x; };
func:w512 = int512(int512:x) never fails { pass x; };
func:w1024 = int1024(int1024:x) never fails { pass x; };
func:w2048 = int2048(int2048:x) never fails { pass x; };
func:w4096 = int4096(int4096:x) never fails { pass x; };"""),
      wrong="a rung refused, or a rung of another width (10-19 name int8 ... int4096)")

claim("ty0085", D, 85, "arithmetic including `/` and `%` at 1024, 2048 and 4096 bits", "rule",
      "`/` and `%` compute at 1024, 2048 and 4096 bits; signed quotients truncate toward zero and remainders keep the dividend's sign.",
      expect="run:0",
      src=main_("""    uint1024:p = raw wu1024(1u1024) << raw wu1024(700u1024);
    uint1024:q = raw wu1024(1u1024) << raw wu1024(690u1024);
    if ((p / q) != 1024u1024) { exit 10i32; }
    if (((p + 5u1024) % q) != 5u1024) { exit 11i32; }
    int2048:one = raw w2048(1i2048);
    int2048:n = 0i2048 - ((one << raw w2048(1000i2048)) + raw w2048(3i2048));
    int2048:m = one << raw w2048(990i2048);
    if ((n / m) != -1024i2048) { exit 12i32; }
    if ((n % m) != -3i2048) { exit 13i32; }
    uint4096:a = (raw wu4096(1u4096) << raw wu4096(4000u4096)) + raw wu4096(7u4096);
    uint4096:b = raw wu4096(1024u4096);
    if ((a / b) != (raw wu4096(1u4096) << raw wu4096(3990u4096))) { exit 14i32; }
    if ((a % b) != 7u4096) { exit 15i32; }
    exit 0i32;""", """func:wu1024 = uint1024(uint1024:x) never fails { pass x; };
func:w2048 = int2048(int2048:x) never fails { pass x; };
func:wu4096 = uint4096(uint4096:x) never fails { pass x; };"""),
      wrong="a wrong quotient or remainder (10-15; 12 = floored, not truncated; 13 = the divisor's sign), or a link failure (a libcall at a wide width)")

claim("ty0086", D, 86, "D-210 trap at 512", "rule",
      "An int512 addition past the maximum traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    int512:one = raw w512(1i512);
    int512:h = one << raw w512(510i512);
    int512:o = h + h;
    if (o < raw w512(0i512)) { exit 10i32; }
    exit 11i32;""", "func:w512 = int512(int512:x) never fails { pass x; };"),
      wrong="wraps to the minimum (exit 10), or no trap (11)")

claim("ty0088", D, 88, "with the compound forms `+%=`, `-%=`, `*%=`", "rule",
      "The compound wrapping forms `+%=`, `-%=`, `*%=` wrap modulo 2^N.",
      expect="run:0",
      src=main_("""    uint8:a = raw vu8(3u8);
    a -%= raw vu8(5u8);
    if (a != 254u8) { exit 10i32; }
    int32:m = raw v32(65536i32);
    m *%= raw v32(65536i32);
    if (m != 0i32) { exit 11i32; }
    int8:p = raw v8(120i8);
    p +%= raw v8(10i8);
    if (p != -126i8) { exit 12i32; }
    exit 0i32;"""),
      wrong="a compound form refused, a trap (93), or not the low N bits (10-12)")

claim("ty0089", D, 89, "is the low N bits, always", "rule",
      "`+% -% *%` compute modulo 2^N: the result is the low N bits.", m10="o19_wrapping_family")

claim("ty0089b", D, 89, "there is no guard", "rule",
      "A wrapping operation has no guard: a `*%` lowers to a plain `mul` with no overflow intrinsic.",
      expect=ir_fn_lacks("m11wm", [r"= mul i32 "], r"with\.overflow"),
      src=main_("""    if (raw m11wm(raw vu32(65536u32), raw vu32(65536u32)) != 0u32) { exit 10i32; }
    exit 0i32;""", "func:m11wm = uint32(uint32:a, uint32:b) never fails { pass a *% b; };"),
      wrong="an overflow intrinsic (a guard) in the wrapping function")

claim("ty0089c", D, 89, "no obligation row", "rule",
      "A wrapping operation has no obligation row.",
      untestable="[z3] obligation rows are written by `npkg verify`")

claim("ty0090", D, 90, "`failsafe` arm, because nothing can go wrong", "rule",
      "A wrapping operation arms no failsafe arm: a program whose only arithmetic is `+%`/`*%` compiles with a "
      "failsafe that does not name IntOverflow.",
      expect="run:0", fs=False,
      src=main_("""    uint32:h = raw vu32(4000000000u32) +% raw vu32(500000000u32);
    if ((h *% raw vu32(2u32)) != 410065408u32) { exit 10i32; }
    exit 0i32;""") + "\n" + fs_without("IntOverflow"),
      wrong="REACH-002: the wrap armed IntOverflow, so failsafe must name it; or a wrong value (10)")

claim("ty0091", D, 91, "```nitpick", "example",
      "`uint32:mixed = h *% 2654435761u32;` is the low 32 bits of the product.",
      expect="run:0",
      src=main_("""    uint32:h = raw vu32(3u32);
    uint32:mixed = h *% 2654435761u32;      // the mix step, said once
    if (mixed != 3668339987u32) { exit 10i32; }
    exit 0i32;"""),
      wrong="a trap (93), or a value other than 3 * 2654435761 mod 2^32 (exit 10)")

claim("ty0094", D, 94, "and `simd` integer lanes'", "rule",
      "The wrapping family applies to simd integer lanes: `+%` wraps each lane.",
      expect="run:0",
      src=main_("""    simd<int32, 4>:a = simd(raw v32(2147483647i32), 1i32, -2147483647i32, 0i32);
    simd<int32, 4>:b = simd(raw v32(1i32), 1i32, -2i32, 0i32);
    simd<int32, 4>:c = a +% b;
    if (c[0i64] != (-2147483647i32 - 1i32)) { exit 10i32; }
    if (c[1i64] != 2i32) { exit 11i32; }
    if (c[2i64] != 2147483647i32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused for simd, a trap (93), or a lane not wrapped (10-12)")

claim("ty0095", D, 95, "`NITPICK-TYPE-078` names the kind", "rule",
      "The wrapping operators are refused on a twisted value (tbb): NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    tbb32:a = raw vt32(5tbb32);
    tbb32:b = a +% raw vt32(3tbb32);
    if (is_err(b)) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: ERR laundered into a number (exit 10 or 11)")

claim("ty0096", D, 96, "the ternary kinds saturate", "rule",
      "The wrapping operators are refused on a ternary kind (tryte): NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    tryte:a = 42;
    tryte:b = a +% a;
    if ((b => int32) == 84i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)")

claim("ty0097", D, 97, "`frac` is exact or ERR", "rule",
      "The wrapping operators are refused on `frac`: NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    frac32:a = (raw v32(5i32)) => frac32;
    frac32:b = a *% a;
    if (b.whole == 25i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)")

claim("ty0097b", D, 97, "`dim256` carries a unit", "rule",
      "The wrapping operators are refused on `dim256`: NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    dim256<Meters>:d = 2.0dim256<Meters>;
    dim256<Meters>:e = d +% d;
    if ((e => tfp256) == 4.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)")

claim("ty0098", D, 98, "`complex` computes per component", "rule",
      "The wrapping operators are refused on `complex`: NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    complex<flt64>:a = complex(raw vf64(1.0f64), 2.0f64);
    complex<flt64>:b = a +% a;
    if (b.re() == 2.0f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)")

claim("ty0098b", D, 98, "and a float is IEEE", "rule",
      "The wrapping operators are refused on a float: NITPICK-TYPE-078.",
      expect="refuse:NITPICK-TYPE-078",
      src=main_("""    flt64:x = raw vf64(1.5f64) +% raw vf64(2.0f64);
    if (x == 3.5f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: `+%` on a float computes an IEEE sum (exit 10)")

claim("ty0098c", D, 98, "A constant wrap folds", "rule",
      "A constant wrap folds WITH the wrap.", m10="o20_wrapping_folds_with_wrap")

claim("ty0099", D, 99, "where the trapping twin is `NITPICK-TYPE-076`", "rule",
      "A constant `+ - *` that overflows is NITPICK-TYPE-076 where it is written.",
      m10="o21_constant_overflow_refused")

claim("ty0109", D, 109, "**`tbb` remains the saturate-to-ERR family**", "rule",
      "tbb overflow is a value the program inspects: it saturates to ERR (sticky) and `is_err` sees it without a trap.",
      m10="m13_tbb_err_sticky")

claim("ty0122", D, 122, "Arithmetic, wrapping: `+%`, `-%`, `*%`", "rule",
      "`+% -% *%` lower to `add`, `sub`, `mul` with no flags.",
      expect=ir_fn("m11wr", r"= add i32 %", r"= sub i32 %", r"= mul i32 %"),
      src=main_("""    if (raw m11wr(raw v32(3i32), raw v32(4i32)) != -5i32) { exit 10i32; }
    exit 0i32;""", "func:m11wr = int32(int32:a, int32:b) never fails { pass ((a +% b) -% (a *% b)); };"),
      wrong="`nsw`/`nuw` flags (poison on wrap), or intrinsic calls")

claim("ty0124", D, 124, "Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=` → `icmp eq/ne/slt/sgt/sle/sge`", "rule",
      "Signed integer comparisons are signed: -5 is below 3 under all six operators.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(-5i32);
    int32:b = raw v32(3i32);
    if (!(a < b)) { exit 10i32; }
    if (a > b) { exit 11i32; }
    if (!(a <= b)) { exit 12i32; }
    if (a >= b) { exit 13i32; }
    if (a == b) { exit 14i32; }
    if (!(a != b)) { exit 15i32; }
    exit 0i32;"""),
      wrong="an unsigned compare on the bit pattern: -5 above 3 (10-13)")

claim("ty0124b", D, 124, "`icmp eq/ne/slt/sgt/sle/sge`", "rule",
      "A signed `<` lowers to `icmp slt`.",
      expect=ir_fn("m11lt", r"icmp slt i32 "),
      src=main_("""    if (!(raw m11lt(raw v32(-5i32), raw v32(3i32)))) { exit 10i32; }
    exit 0i32;""", "func:m11lt = bool(int32:a, int32:b) never fails { pass a < b; };"),
      wrong="another predicate (ult)")

claim("ty0125", D, 125, "Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`", "rule",
      "The bitwise operators on signed integers are and/or/xor/not/shl/ashr: `-8 >> 1` is -4.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(-8i32);
    int32:b = raw v32(12i32);
    if ((a & b) != 8i32) { exit 10i32; }
    if ((a | b) != -4i32) { exit 11i32; }
    if ((a ^ b) != -12i32) { exit 12i32; }
    if ((~a) != 7i32) { exit 13i32; }
    if ((a << raw v32(2i32)) != -32i32) { exit 14i32; }
    if ((a >> raw v32(1i32)) != -4i32) { exit 15i32; }
    exit 0i32;"""),
      wrong="a wrong bit result (10-14), or a logical `>>` on a signed value (15)")

claim("ty0125b", D, 125, "`and`, `or`, `xor`, `shl`, `ashr`", "rule",
      "A signed `>>` lowers to `ashr`.",
      expect=ir_fn("m11sr", r"\bashr i32 "),
      src=main_("""    if (raw m11sr(raw v32(-8i32), raw v32(1i32)) != -4i32) { exit 10i32; }
    exit 0i32;""", "func:m11sr = int32(int32:a, int32:n) never fails { pass a >> n; };"),
      wrong="`lshr` on a signed operand")

claim("ty0126", D, 126, "Casting: explicit only", "rule",
      "Integer conversions are explicit only: an int32 assigned to an int64 without `=>` is refused.",
      expect="refuse",
      src=main_("""    int32:a = raw v32(5i32);
    int64:b = a;
    if (b == 5i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: an implicit widening (exit 10)")

claim("ty0127", D, 127, "Literal suffixes: `42i32`, `-1i8`, `0FFhexi64`", "rule",
      "`42i32`, `-1i8` and `0FFhexi64` are literals of 42, -1 and 255.",
      expect="run:0",
      src=main_("""    if (42i32 != raw v32(42i32)) { exit 10i32; }
    int8:m = raw v8(-1i8);
    if ((m + 1i8) != 0i8) { exit 11i32; }
    if (0FFhexi64 != raw v64(255i64)) { exit 12i32; }
    exit 0i32;"""),
      wrong="a spelling refused, or another value (10-12)")

claim("ty0130", D, 130, "```llvm", "example",
      "`a + b` lowers through llvm.sadd.with.overflow.i32 and `a / b` tests the divisor against 0 before an `sdiv`.",
      expect=ir_fn("m11ad", r"@llvm\.sadd\.with\.overflow\.i32\(", r"icmp eq i32 %\S+, 0\b", r"= sdiv i32 "),
      src=main_("""    if (raw m11ad(raw v32(6i32), raw v32(2i32)) != 4i32) { exit 10i32; }
    exit 0i32;""", """func:m11ad = int32(int32:a, int32:b) never fails {
    int32:r = a + b;
    pass r / b;
};"""),
      wrong="no overflow intrinsic, no zero test, or a division other than sdiv")

claim("ty0144", D, 144, "`tbb` uses the same intrinsics", "rule",
      "tbb arithmetic uses the same overflow intrinsics: a tbb32 `+` lowers through llvm.sadd.with.overflow.i32.",
      expect=ir_fn("m11tb", r"@llvm\.sadd\.with\.overflow\.i32\("),
      src=main_("""    if (is_err(raw m11tb(raw vt32(1tbb32), raw vt32(2tbb32)))) { exit 10i32; }
    exit 0i32;""", "func:m11tb = tbb32(tbb32:a, tbb32:b) never fails { pass a + b; };"),
      wrong="a widened compute-and-clamp instead of the intrinsic")

# ------------------------------------------------------------------ 1.3 unsigned
for ln, t, sz in ((151, "uint8", 1), (152, "uint16", 2), (153, "uint32", 4), (154, "uint64", 8)):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` is %d byte%s with alignment %d." % (t, sz, "" if sz == 1 else "s", sz),
          expect="run:0", src=layout([t], sz, sz), wrong=layout_wrong([t], sz, sz))

claim("ty0158", D, 158, "Division/modulo use `udiv`/`urem`", "rule",
      "Unsigned division and remainder are unsigned (udiv/urem).", m10="v14_unsigned_div_rem")
claim("ty0159", D, 159, "Comparisons use `ult`/`ugt`/`ule`/`uge`", "rule",
      "Unsigned comparisons are unsigned (ult/ugt/ule/uge).", m10="m03_unsigned_ordering")
claim("ty0160", D, 160, "Right shift uses `lshr` (logical)", "rule",
      "`>>` on an unsigned operand is logical.", m10="s02_unsigned_right_shift_logical")
claim("ty0161", D, 161, "Overflow TRAPS, as with signed types", "rule",
      "Unsigned `+` overflow traps IntOverflow (255 + 1 at uint8).", m10="o07_uint8_add")
claim("ty0161b", D, 161, "Overflow TRAPS, as with signed types", "rule",
      "Unsigned `-` below zero traps IntOverflow (0 - 1 at uint8).", m10="o08_uint8_sub")

claim("ty0164", D, 164, "Literal suffixes: `42u32`, `0FFhexu8`", "rule",
      "`42u32` and `0FFhexu8` are literals of 42 and 255.",
      expect="run:0",
      src=main_("""    if (0FFhexu8 != raw vu8(255u8)) { exit 10i32; }
    if (42u32 != raw vu32(42u32)) { exit 11i32; }
    exit 0i32;"""),
      wrong="a spelling refused, or another value (10, 11)")

claim("ty0166", D, 166, "are **semantically distinct**", "rule",
      "`uint8` and `char8` are distinct types: a char8 compared with a uint8 is refused.",
      m10="m09_char_vs_uint8_refused")

# ------------------------------------------------------------------ 1.4 floats
claim("ty0172", D, 172, "| `flt32` | `float` | 4 bytes | 4 |", "row",
      "`flt32` is 4 bytes with alignment 4.",
      expect="run:0", src=layout(["flt32"], 4, 4), wrong=layout_wrong(["flt32"], 4, 4))
claim("ty0172b", D, 172, "| `flt32` | `float` |", "row",
      "`flt32` is `float`: its arithmetic rounds at 24 significand bits.", m10="f02_flt32_rounds_in_flt32")
claim("ty0173", D, 173, "| `flt64` | `double` | 8 bytes | 8 |", "row",
      "`flt64` is 8 bytes with alignment 8.",
      expect="run:0", src=layout(["flt64"], 8, 8), wrong=layout_wrong(["flt64"], 8, 8))

claim("ty0174", D, 174, "| `flt128` | `fp128` | 16 bytes | 16 |", "row",
      "`flt128` is 16 bytes with alignment 16.",
      expect="run:0", src=layout(["flt128"], 16, 16), wrong=layout_wrong(["flt128"], 16, 16))

claim("ty0174b", D, 174, "no literals, arithmetic, or comparison", "rule",
      "flt128 has no literals: `1.5f128` is refused.",
      expect="refuse",
      src=main_("""    flt128:x = 1.5f128;
    discard(x);
    exit 0i32;"""),
      wrong="accepted: a flt128 literal")

claim("ty0174c", D, 174, "no literals, arithmetic, or comparison", "rule",
      "flt128 has no arithmetic: `a + b` on flt128 values is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:m11q = flt128(flt128:a, flt128:b) never fails { pass a + b; };"),
      wrong="accepted: a soft-float add with no verified provider (or a link failure later)")

claim("ty0174d", D, 174, "no literals, arithmetic, or comparison", "rule",
      "flt128 has no comparison: `a == b` on flt128 values is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:m11qc = bool(flt128:a, flt128:b) never fails { pass a == b; };"),
      wrong="accepted: a soft-float compare")

claim("ty0174e", D, 174, "holds, moves", "rule",
      "flt128 is storage: a value is held in a local and a struct field and moved through a function.",
      expect="run:0",
      src=main_("""    flt128[2]:z = [];
    flt128:x = raw m11qm(z[1i64]);
    Q:q = Q{ v: x, k: 7i32 };
    flt128:y = q.v;
    discard(y);
    if (q.k != 7i32) { exit 10i32; }
    exit 0i32;""", """struct:Q = { flt128:v; int32:k; };
func:m11qm = flt128(flt128:a) never fails { flt128:b = a; pass b; };"""),
      wrong="refused: a flt128 cannot be held or moved; or the struct's other field corrupted (10)")

claim("ty0174f", D, 174, "crosses FFI", "rule",
      "flt128 crosses FFI.",
      untestable="[tool] an FFI crossing needs a foreign object linked into the program; the harness links only the runtime")

claim("ty0174g", D, 174, "| `flt128` | `fp128` |", "row",
      "flt128 is `fp128` in the IR.",
      expect="ir:" + sig("m11fp", r"\bfp128", "fp128 "),
      src=main_("""    flt128[1]:z = [];
    flt128:x = raw m11fp(z[0i64]);
    discard(x);
    exit 0i32;""", "func:m11fp = flt128(flt128:a) never fails { pass a; };"),
      wrong="another carrier (i128, a struct)")

claim("ty0176", D, 176, "are **reserved words, not types**", "rule",
      "`flt256` is not a type: a binding declared with it is refused.",
      expect="refuse",
      src=main_("""    flt256:x = raw vf64(1.5f64) => flt256;
    discard(x);
    exit 0i32;"""),
      wrong="accepted: flt256 is a type")

claim("ty0176b", D, 176, "are **reserved words, not types**", "rule",
      "`flt512` is a reserved word: it cannot name a binding.",
      expect="refuse",
      src=main_("""    int32:flt512 = raw v32(0i32);
    exit flt512;"""),
      wrong="accepted: flt512 is an ordinary identifier (exit 0)")

claim("ty0178", D, 178, "the `f256`/`f512` literal suffixes are gone", "rule",
      "The `f512` literal suffix is gone: `1.5f512` is refused.",
      expect="refuse",
      src=main_("""    flt64:x = 1.5f512 =>! flt64;
    discard(x);
    exit 0i32;"""),
      wrong="accepted: an f512 literal")

claim("ty0181", D, 181, "Arithmetic: `+`, `-`, `*`, `/`, `%` → `fadd`", "rule",
      "Float arithmetic is IEEE `fadd` and friends; a constant means what the run time means: 0.1 + 0.2 is not 0.3.",
      m10="f01_decimal_sum_not_exact")

claim("ty0181b", D, 181, "`fadd`, `fsub`, `fmul`, `fdiv`, `frem`", "rule",
      "flt64 `+ - * /` lower to `fadd`, `fsub`, `fmul`, `fdiv` on `double`.",
      expect=ir_fn("m11fa", r"= fadd double ", r"= fsub double ", r"= fmul double ", r"= fdiv double "),
      src=main_("""    if (raw m11fa(raw vf64(2.0f64), raw vf64(4.0f64)) != -0.5f64) { exit 10i32; }
    exit 0i32;""", "func:m11fa = flt64(flt64:a, flt64:b) never fails { pass ((a + b) - (a * b)) / b; };"),
      wrong="calls, fast-math flags, or another type")

claim("ty0182", D, 182, "(`frem` lowers to the runtime floor's hand-written, exact `fmod`/`fmodf`)", "rule",
      "Float `%` is the exact fmod: the result takes the dividend's sign.", m10="v17_float_remainder")

claim("ty0182b", D, 182, "`frem` lowers to the runtime floor's", "rule",
      "flt64 `%` is emitted as `frem double`.",
      expect=ir_fn("m11fr", r"= frem double "),
      src=main_("""    if (raw m11fr(raw vf64(5.5f64), raw vf64(2.0f64)) != 1.5f64) { exit 10i32; }
    exit 0i32;""", "func:m11fr = flt64(flt64:a, flt64:b) never fails { pass a % b; };"),
      wrong="a hand-rolled remainder, or a direct call")

claim("ty0183", D, 183, "**Total, no traps**", "rule",
      "Float division by zero yields an infinity and does not trap.", m10="v16_float_div_by_zero")

claim("ty0186", D, 186, "Negation is `fneg` (sign-bit exact", "rule",
      "Float negation is sign-bit exact: -(0.0) is -0.0.", m10="m08_negative_zero")

claim("ty0186b", D, 186, "Negation is `fneg`", "rule",
      "flt64 unary `-` lowers to `fneg double`.",
      expect=ir_fn("m11fn", r"= fneg double "),
      src=main_("""    if (raw m11fn(raw vf64(2.0f64)) != -2.0f64) { exit 10i32; }
    exit 0i32;""", "func:m11fn = flt64(flt64:a) never fails { pass -a; };"),
      wrong="`fsub double 0.0, %a` (which gives +0.0 for 0.0)")

claim("ty0187", D, 187, "`fcmp` ordered predicates, except `!=` which is `une`", "rule",
      "Float comparisons are ordered except `!=`, which is unordered: NaN != NaN is true.",
      m10="m07_nan_comparisons")

claim("ty0187b", D, 187, "`fcmp` ordered predicates", "rule",
      "flt64 `!=` lowers to `fcmp une` and `<` to the ordered `fcmp olt`.",
      expect=ir_all(_fn("m11ne") + _body(r"fcmp une double "), _fn("m11fl") + _body(r"fcmp olt double ")),
      src=main_("""    if (!(raw m11ne(raw vf64(1.0f64), raw vf64(2.0f64)))) { exit 10i32; }
    if (!(raw m11fl(raw vf64(1.0f64), raw vf64(2.0f64)))) { exit 11i32; }
    exit 0i32;""", """func:m11ne = bool(flt64:a, flt64:b) never fails { pass a != b; };
func:m11fl = bool(flt64:a, flt64:b) never fails { pass a < b; };"""),
      wrong="`fcmp one` for `!=`, or an unordered `<`")

claim("ty0189", D, 189, "Literal suffixes: `3.14f32`, `2.718f64`", "rule",
      "`3.14f32` and `2.718f64` are float literals of those values.",
      expect="run:0",
      src=main_("""    flt32:a = raw vf32(3.14f32);
    if (!((a > 3.13f32) && (a < 3.15f32))) { exit 10i32; }
    flt64:b = raw vf64(2.718f64);
    if (!((b > 2.717f64) && (b < 2.719f64))) { exit 11i32; }
    exit 0i32;"""),
      wrong="a spelling refused, or another value (10, 11)")

claim("ty0189b", D, 189, "`3.14flt32`", "rule",
      "The spelling `3.14flt32` does not lex: it is refused.",
      expect="refuse",
      src=main_("""    flt32:x = 3.14flt32;
    discard(x);
    exit 0i32;"""),
      wrong="accepted: `flt32` as a literal suffix")

claim("ty0190", D, 190, "carries at most 15 significant digits", "rule",
      "A flt32 literal with 16 significant digits is refused.", m10="c25_flt32_literal_16_digits")

claim("ty0190b", D, 190, "carries at most 15 significant digits", "rule",
      "A flt32 literal of exactly 15 significant digits is accepted and correctly rounded (through a correctly-rounded double).",
      expect="run:0",
      src=main_("""    flt32:a = 0.123456789012345f32;
    flt32:b = 0.12345679f32;
    if (a != b) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (15 digits denied), or not the correctly rounded float (exit 10)")

claim("ty0194", D, 194, "Math functions (sin, cos, sqrt, …) arrive with the library tier", "rule",
      "Math functions arrive with the library tier, wrapping LLVM intrinsics.",
      untestable="[vague] names no spelling, module or result to check (and 'arrive' reads as a plan)")


claim("ty0198", D, 198, "term of the IEEE sort", "rule",
      "A flt32/flt64 value is a term of the SMT IEEE sort (tier 1), with a Real-interval twin (tier 2).",
      untestable="[z3] the encoding is exercised only by `npkg verify` with the pinned z3")

claim("ty0201", D, 201, "no obligation row is a", "rule",
      "No obligation row is a float's.",
      untestable="[z3] obligation rows are written by `npkg verify`")

claim("ty0202", D, 202, "a `limit`, a contract, an `invariant`", "rule",
      "A limit, contract, invariant or prove over floats is decided.",
      untestable="[z3] decided only under `npkg verify` with the pinned z3")

claim("ty0203", D, 203, "**A float `/` or `%` arms no", "rule",
      "A float `/` or `%` arms no DivByZero/DivOverflow: a program whose only division is a float's compiles "
      "with a failsafe that names neither.",
      expect="run:0", fs=False,
      src=main_("""    if (raw m11fd(raw vf64(7.0f64), raw vf64(2.0f64)) != 4.5f64) { exit 10i32; }
    exit 0i32;""", "func:m11fd = flt64(flt64:a, flt64:b) never fails { pass (a / b) + (a % b); };") +
      "\n" + fs_without("DivByZero", "DivOverflow"),
      wrong="REACH-002: the float division armed DivByZero/DivOverflow; or a wrong value (10)")

claim("ty0205", D, 205, "the emitter writes a bare `fdiv`/`frem`", "rule",
      "The emitter writes a bare `fdiv`/`frem`: no compare guards a float division.",
      expect=ir_fn_lacks("m11fd", [r"= fdiv double ", r"= frem double "], r"fcmp"),
      src=main_("""    if (raw m11fd(raw vf64(7.0f64), raw vf64(2.0f64)) != 4.5f64) { exit 10i32; }
    exit 0i32;""", "func:m11fd = flt64(flt64:a, flt64:b) never fails { pass (a / b) + (a % b); };"),
      wrong="a divisor test (fcmp) guarding the float division")

claim("ty0205b", D, 205, "a `failsafe` names the two only", "rule",
      "Where an integer division exists, failsafe must name DivByZero and DivOverflow: one that names neither is refused.",
      expect="refuse", fs=False,
      src=main_("""    if (raw m11id(raw v32(7i32), raw v32(2i32)) != 3i32) { exit 10i32; }
    exit 0i32;""", "func:m11id = int32(int32:a, int32:b) never fails { pass a / b; };") +
      "\n" + fs_without("DivByZero", "DivOverflow"),
      wrong="accepted: an integer division's traps left unnamed (exit 0)")

claim("ty0206", D, 206, "`#sqrt` is `fp.sqrt`", "rule",
      "`#sqrt` is encoded as fp.sqrt; `%` and a cast out of a float stay opaque to the verifier.",
      untestable="[z3] the encoding is exercised only by `npkg verify` with the pinned z3")

# ------------------------------------------------------------------ 2 characters
claim("ty0214", D, 214, "`char8:c = 65char8;` is the letter 'A'", "rule",
      "`65char8` is the letter 'A'.",
      expect="run:0",
      src=main_("""    char8:c = 65char8;
    if (c != 'A') { exit 10i32; }
    if (raw vc8(65char8) != raw vc8('A')) { exit 11i32; }
    exit 0i32;"""),
      wrong="the literal refused, or another character (10, 11)")

claim("ty0222", D, 222, "| `char8` | `i8` | 1 byte | 1 |", "row",
      "`char8` is 1 byte with alignment 1.",
      expect="run:0", src=layout(["char8"], 1, 1), wrong=layout_wrong(["char8"], 1, 1))
claim("ty0223", D, 223, "| `char16` | `i16` | 2 bytes | 2 |", "row",
      "`char16` is 2 bytes with alignment 2.",
      expect="run:0", src=layout(["char16"], 2, 2), wrong=layout_wrong(["char16"], 2, 2))
claim("ty0224", D, 224, "| `char32` | `i32` | 4 bytes | 4 |", "row",
      "`char32` is 4 bytes with alignment 4.",
      expect="run:0", src=layout(["char32"], 4, 4), wrong=layout_wrong(["char32"], 4, 4))

claim("ty0224b", D, 224, "Unicode scalar value (full codepoint)", "rule",
      "A char32 is a Unicode scalar value: a literal above U+10FFFF is refused.",
      expect="refuse",
      src=main_("""    char32:c = 1114112char32;
    if (c == 1114112char32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a char32 that is no code point (exit 10)")

claim("ty0224c", D, 224, "Unicode scalar value (full codepoint)", "rule",
      "A char32 is a Unicode scalar value: a surrogate (U+D800) is not one, so the literal is refused.",
      expect="refuse",
      src=main_("""    char32:c = 55296char32;
    if (c == 55296char32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a char32 holding a surrogate (exit 10)",
      note="inferred from the column's 'Unicode scalar value' (surrogates excluded by definition); the text does not say the literal is refused in words")

for i, op in enumerate(["+", "-", "*", "/", "%"]):
    claim("ty0227" + ("", "b", "c", "d", "e")[i], D, 227, "cannot perform arithmetic on char type", "rule",
          "Arithmetic `%s` on char8 is a compile-time error." % op,
          expect="refuse",
          src=main_("""    char8:c = raw vc8('A') """ + op + """ raw vc8('B');
    if (c == 'A') { exit 10i32; }
    exit 11i32;"""),
          wrong="accepted: `%s` computes on the byte (exit 10 or 11)" % op)

for i, op in enumerate(["&", "|", "^", "~", "<<", ">>"]):
    expr = ("~raw vc8('A')" if op == "~" else "raw vc8('A') " + op + " raw vc8('B')")
    claim("ty0228" + ("", "b", "c", "d", "e", "f")[i], D, 228,
          "cannot perform bitwise operations on char type", "rule",
          "Bitwise `%s` on char8 is a compile-time error." % op,
          expect="refuse",
          src=main_("    char8:c = " + expr + """;
    if (c == 'A') { exit 10i32; }
    exit 11i32;"""),
          wrong="accepted: `%s` on the byte (exit 10 or 11)" % op)

claim("ty0231", D, 231, "(unsigned comparison for Unicode ordering)", "rule",
      "char8 comparisons are unsigned: '\\xC3' is above 'A'.", m10="m05_char_ordering_unsigned")

claim("ty0231b", D, 231, "Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`", "rule",
      "Ordering is permitted on char16 and char32 too, and is unsigned: 65535char16 is above 65char16.",
      expect="run:0",
      src=main_("""    char16:h = raw vch16(65535char16);
    char16:l = raw vch16(65char16);
    if (!(h > l)) { exit 10i32; }
    if (!(l <= h)) { exit 11i32; }
    char32:e = raw vch32(128512char32);
    char32:a = raw vch32(65char32);
    if (!(e > a)) { exit 12i32; }
    if (e == a) { exit 13i32; }
    exit 0i32;""", """func:vch16 = char16(char16:x) never fails { pass x; };
func:vch32 = char32(char32:x) never fails { pass x; };"""),
      wrong="ordering refused on the wide chars, or a signed char16 compare: 65535 below 65 (10, 11)")

claim("ty0232", D, 232, "Assignment: `char8:c = 'A';` or `char8:c = 65char8;`", "rule",
      "`char8:c = 'A';` and `char8:c = 65char8;` assign the same character.",
      expect="run:0",
      src=main_("""    char8:c = 'A';
    char8:d = 65char8;
    if (c != d) { exit 10i32; }
    exit 0i32;"""),
      wrong="a spelling refused, or two different values (exit 10)")

claim("ty0233", D, 233, "Indexing into char arrays", "rule",
      "A char array indexes to its chars: `arr[0]` is the first.",
      expect="run:0",
      src=main_("""    char8[3]:buf = ['x', 'y', 'z'];
    char8[]:arr = buf[0i64...3i64];
    char8:c = arr[0];
    if (c != 'x') { exit 10i32; }
    if (arr[raw v64(2i64)] != 'z') { exit 11i32; }
    exit 0i32;"""),
      wrong="indexing refused, or the wrong char (10, 11)")

_CHARFN = [
    (239, "toUpper", "Convert to uppercase (ASCII range only for char8)",
     "`toUpper` uppercases an ASCII letter and leaves every other char8 unchanged (ASCII range only).",
     """    if (raw toUpper(raw vc8('a')) != 'A') { exit 10i32; }
    if (raw toUpper(raw vc8('Z')) != 'Z') { exit 11i32; }
    if (raw toUpper(raw vc8('1')) != '1') { exit 12i32; }
    if (raw toUpper(raw vc8('\\xE9')) != '\\xE9') { exit 13i32; }""",
     "refused (no such function); 10/11: a letter not converted; 12: a non-letter changed; 13: Latin-1 e-acute uppercased beyond ASCII"),
    (240, "toLower", "Convert to lowercase (ASCII range only for char8)",
     "`toLower` lowercases an ASCII letter and leaves every other char8 unchanged (ASCII range only).",
     """    if (raw toLower(raw vc8('A')) != 'a') { exit 10i32; }
    if (raw toLower(raw vc8('z')) != 'z') { exit 11i32; }
    if (raw toLower(raw vc8('@')) != '@') { exit 12i32; }
    if (raw toLower(raw vc8('\\xC9')) != '\\xC9') { exit 13i32; }""",
     "refused; 10/11: a letter wrong; 12: '@' (just below 'A') changed; 13: Latin-1 lowercased beyond ASCII"),
    (241, "isAlpha", "Is alphabetic character",
     "`isAlpha` is true for letters and false for a digit and for the bytes beside 'A' and 'Z'.",
     """    if (!(raw isAlpha(raw vc8('a')))) { exit 10i32; }
    if (!(raw isAlpha(raw vc8('Z')))) { exit 11i32; }
    if (raw isAlpha(raw vc8('1'))) { exit 12i32; }
    if (raw isAlpha(raw vc8('@'))) { exit 13i32; }
    if (raw isAlpha(raw vc8('['))) { exit 14i32; }""",
     "refused; 10/11: a letter denied; 12: a digit alphabetic; 13/14: an off-by-one range"),
    (242, "isDigit", "Is decimal digit",
     "`isDigit` is true for '0' through '9' only.",
     """    if (!(raw isDigit(raw vc8('0')))) { exit 10i32; }
    if (!(raw isDigit(raw vc8('9')))) { exit 11i32; }
    if (raw isDigit(raw vc8('/'))) { exit 12i32; }
    if (raw isDigit(raw vc8(':'))) { exit 13i32; }""",
     "refused; 10/11: a digit denied; 12/13: an off-by-one range"),
    (243, "isAlphaNumeric", "Is alpha or digit",
     "`isAlphaNumeric` is true for a letter or a digit and false otherwise.",
     """    if (!(raw isAlphaNumeric(raw vc8('q')))) { exit 10i32; }
    if (!(raw isAlphaNumeric(raw vc8('7')))) { exit 11i32; }
    if (raw isAlphaNumeric(raw vc8('_'))) { exit 12i32; }
    if (raw isAlphaNumeric(raw vc8(' '))) { exit 13i32; }""",
     "refused; 10/11: denied; 12/13: punctuation or space accepted"),
    (244, "isWhitespace", "Is space, tab, CR, LF",
     "`isWhitespace` is true for exactly space, tab, CR and LF: vertical tab and form feed are not in the list.",
     """    if (!(raw isWhitespace(raw vc8(' ')))) { exit 10i32; }
    if (!(raw isWhitespace(raw vc8('\\t')))) { exit 11i32; }
    if (!(raw isWhitespace(raw vc8('\\r')))) { exit 12i32; }
    if (!(raw isWhitespace(raw vc8('\\n')))) { exit 13i32; }
    if (raw isWhitespace(raw vc8('\\x0B'))) { exit 14i32; }
    if (raw isWhitespace(raw vc8('\\x0C'))) { exit 15i32; }
    if (raw isWhitespace(raw vc8('a'))) { exit 16i32; }""",
     "refused; 10-13: a listed char denied; 14/15: C's isspace (VT, FF) instead of the four listed; 16: a letter"),
    (245, "isUpper", "Is uppercase letter",
     "`isUpper` is true for 'A' through 'Z' only.",
     """    if (!(raw isUpper(raw vc8('A')))) { exit 10i32; }
    if (raw isUpper(raw vc8('a'))) { exit 11i32; }
    if (raw isUpper(raw vc8('@'))) { exit 12i32; }""",
     "refused; 10: denied; 11: lowercase accepted; 12: an off-by-one range"),
    (246, "isLower", "Is lowercase letter",
     "`isLower` is true for 'a' through 'z' only.",
     """    if (!(raw isLower(raw vc8('z')))) { exit 10i32; }
    if (raw isLower(raw vc8('Z'))) { exit 11i32; }
    if (raw isLower(raw vc8('{'))) { exit 12i32; }""",
     "refused; 10: denied; 11: uppercase accepted; 12: an off-by-one range"),
    (247, "toUint", "Reinterpret as unsigned integer",
     "`toUint` reinterprets a char8 as its uint8 byte.",
     """    if (raw toUint(raw vc8('A')) != 65u8) { exit 10i32; }
    if (raw toUint(raw vc8('\\xFF')) != 255u8) { exit 11i32; }""",
     "refused; 10/11: another value"),
    (248, "fromUint", "Reinterpret unsigned integer as char",
     "`fromUint` reinterprets a uint8 as the char8 of that byte.",
     """    if (raw fromUint(raw vu8(66u8)) != 'B') { exit 10i32; }
    if (raw fromUint(raw vu8(200u8)) != '\\xC8') { exit 11i32; }""",
     "refused; 10/11: another char"),
    (249, "toChar16", "Widen (zero-extend)",
     "`toChar16` zero-extends a char8: '\\xE9' becomes 233char16.",
     """    if (raw toChar16(raw vc8('\\xE9')) != 233char16) { exit 10i32; }
    if (raw toChar16(raw vc8('A')) != 65char16) { exit 11i32; }""",
     "refused; 10: sign-extended to 65513; 11: another value"),
    (250, "toChar32", "Widen (zero-extend)",
     "`toChar32` zero-extends a char8: '\\xFF' becomes 255char32.",
     """    if (raw toChar32(raw vc8('\\xFF')) != 255char32) { exit 10i32; }
    if (raw toChar32(raw vc8('A')) != 65char32) { exit 11i32; }""",
     "refused; 10: sign-extended; 11: another value"),
]
for ln, fn, q, text, body, wrong in _CHARFN:
    claim("ty%04d" % ln, D, ln, "| `%s` |" % fn, "row", text, expect="run:0",
          src=main_(body + "\n    exit 0i32;"), wrong=wrong,
          note="Tier 1 (written in Nitpick), so called as a `never fails` function with `raw`; the row's quote: " + q)

claim("ty0257", D, 257, "```llvm", "example",
      "A char8 range test lowers to the unsigned predicates `icmp uge i8 ..., 65` and `icmp ule i8 ..., 90`.",
      expect=ir_fn("m11cu", r"icmp uge i8 %\S+, 65\b", r"icmp ule i8 %\S+, 90\b"),
      src=main_("""    if (!(raw m11cu(raw vc8('Q')))) { exit 10i32; }
    exit 0i32;""", "func:m11cu = bool(char8:c) never fails { pass (c >= 'A') && (c <= 'Z'); };"),
      wrong="signed predicates (sge/sle), or the char widened first")

claim("ty0272", D, 272, "```nitpick", "example",
      "The character literals compile to their code units: '\\n' 10, '\\t' 9, '\\0' 0, '\\\\' 92, '\\'' 39, "
      "'\\x41' 'A', and '\\u{1F600}' in a char32 is U+1F600.",
      expect="run:0",
      src=main_(r"""    char8:a = 'A';           // Single character literal
    char8:newline = '\n';    // Escape sequences
    char8:tab = '\t';
    char8:null = '\0';
    char8:backslash = '\\';
    char8:quote = '\'';
    char8:hex = '\x41';      // Hex escape (= 'A')
    char32:emoji = '\u{1F600}';  // Unicode escape (char32 only)
    if (a != 65char8) { exit 10i32; }
    if (newline != 10char8) { exit 11i32; }
    if (tab != 9char8) { exit 12i32; }
    if (null != 0char8) { exit 13i32; }
    if (backslash != 92char8) { exit 14i32; }
    if (quote != 39char8) { exit 15i32; }
    if (hex != a) { exit 16i32; }
    if (emoji != 128512char32) { exit 17i32; }
    exit 0i32;"""),
      wrong="a literal or a binding name refused, or a wrong code unit (10-17)")

claim("ty0280", D, 280, "// Unicode escape (char32 only)", "rule",
      "The `\\u{...}` escape is for char32 only: in a char8 slot it is refused.",
      expect="refuse",
      src=main_(r"""    char8:c = '\u{41}';
    if (c == 'A') { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted in a char8 (exit 10)",
      note="'(char32 only)' may instead mean only that U+1F600 needs a char32; this claim takes the escape reading")

claim("ty0285", D, 285, "```nitpick", "example",
      "The example compiles: a char8[5] holds 5 chars, `cstring:cs = \"Hello\";` is a cstring of length 5, "
      "and `to_cstring` of a clean string succeeds.",
      expect="run:0",
      src=main_("""    // char arrays do NOT implicitly add a null byte
    char8[5]:hello = ['H', 'e', 'l', 'l', 'o'];

    // To create a C-compatible string, use the cstring type (D-049):
    cstring:cs = "Hello";                        // literal — checked at compile time
    string:some_string = "world";
    Result<cstring>:r = to_cstring(some_string);  // runtime — fails on an interior NUL
    if (hello.len != 5i64) { exit 10i32; }
    if (cs.len != 5i64) { exit 11i32; }
    if (r.is_error) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused (a literal in cstring position denied), or 10: a NUL added; 11: the terminator counted; 12: a clean string failed",
      note="`some_string` is declared (the example leaves it undeclared); the commented-out error line is ty0295; M9 measured that no string literal types as cstring")

claim("ty0286", D, 286, "char arrays do NOT implicitly add a null byte", "rule",
      "A char array holds exactly its elements: `char8[5]` of 'Hello' has len 5 and occupies 5 bytes.",
      expect="run:0",
      src=main_("""    char8[5]:hello = ['H', 'e', 'l', 'l', 'o'];
    if (hello.len != 5i64) { exit 10i32; }
    if (#size_of<H>() != 5i64) { exit 11i32; }
    exit 0i32;""", "struct:H = { char8[5]:h; };"),
      wrong="a NUL added: len 6 (10) or 6 bytes (11)")

claim("ty0290", D, 290, "cstring:cs = \"Hello\";", "rule",
      "A string literal in cstring position is a cstring: `cstring:cs = \"Hello\";` compiles with length 5.",
      expect="run:0",
      src=main_("""    cstring:cs = "Hello";
    if (cs.len != 5i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no literal types as cstring), or the terminator counted (10)",
      note="M9 measured that no string literal types as `cstring`; extracted and tested again here")

claim("ty0295", D, 295, "ERROR: cannot assign char8[] to string", "rule",
      "A char array is not a string: assigning one to a `string` is a compile error.",
      expect="refuse",
      src=main_("""    char8[5]:hello = ['H', 'e', 'l', 'l', 'o'];
    string:s = hello;
    if (string_byte_length(s) == 5i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: the array converted implicitly (exit 10 or 11)")

claim("ty0304", D, 304, "| `trit` | A base-3 unit of information", "row",
      "A trit holds the base-3 digits 0 and 1 (common to both readings the row gives).",
      expect="run:0",
      src=main_("""    trit:a = 0;
    trit:b = 1;
    if ((a => int32) != 0i32) { exit 10i32; }
    if ((b => int32) != 1i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or another value (10, 11)",
      note="the row allows '-1, 0, 1 or 0, 1, 2' (ambiguous); §7 (line 736) says -1, 0, 1")

claim("ty0304b", D, 304, "(values: -1, 0, 1 or 0, 1, 2)", "rule",
      "A trit holds three values: 3 is outside both readings and is refused.",
      expect="refuse",
      src=main_("""    trit:t = 3;
    if ((t => int32) == 3i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a trit holding 3 (exit 10) or clamped (11)")

claim("ty0305", D, 305, "| `tryte` | A block of 10 trits", "row",
      "A tryte is 10 trits: it holds 29524 (ten balanced trits; six would stop at 364) and has 10 digits.",
      expect="run:0",
      src=main_("""    tryte:t = 29524;
    if ((t => int32) != 29524i32) { exit 10i32; }
    if (t.len != 10i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (a narrower tryte), or 10: another value; 11: another digit count",
      note="`.len` as the digit count is §7's spelling (line 802); the row's '(GRAMMAR_ADOPTION_CONFLICTS Part Q ...)' is the annotation §7 says was removed at 1.3.0")

claim("ty0306", D, 306, "| `nit` | Base-9 primitive (values: 0-8)", "row",
      "A nit takes the values 0 to 8: `nit:n = 8;` holds 8.",
      expect="run:0",
      src=main_("""    nit:n = 8;
    if ((n => int32) != 8i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: a nit is balanced -4..4 as §7 (line 738) says; or another value (10)",
      note="contradicts §7's '−4 … 4'; the expectation follows this row")

claim("ty0307", D, 307, "| `nyte` | A block of 2 nits (values: 0-80)", "row",
      "A nyte is 2 nits holding 0 to 80: `nyte:n = 81;` is out of range and refused.",
      expect="refuse",
      src=main_("""    nyte:n = 81;
    if ((n => int32) == 81i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a nyte is 5 nits (±29524) as §7 (lines 739-742) says, the row being the stale '2 nits'",
      note="§7 says the '2 nits' reading was a carry-over defect fixed at 1.3.0; the expectation follows this row")

claim("ty0307b", D, 307, "(values: 0-80)", "rule",
      "A nyte holds 80, the top of the row's range.",
      expect="run:0",
      src=main_("""    nyte:n = 80;
    if ((n => int32) != 80i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or another value (10)")

claim("ty0308", D, 308, "| `tensor` | N-dimensional array primitive.", "row",
      "`tensor` is a native primitive: `tensor<flt64>` names a type with no import.",
      expect="run:0",
      src=main_("    exit 0i32;", "func:m11ten = int32(tensor<flt64>:_~t) never fails { pass 0i32; };"),
      wrong="refused: tensor is a library type (lib/ntensor.npk), as §15 and LEXICAL §4 say",
      note="contradicts §15 (line 1500: 'library, not keywords', 'nothing SIMD about them')")

claim("ty0308b", D, 308, "Emits LLVM vector/SIMD intrinsics.", "row",
      "Tensor operations emit LLVM vector/SIMD intrinsics.",
      untestable="[vague] names no operation (and no construction in this range) whose emission could be checked")

claim("ty0309", D, 309, "| `matrix` | 2D data primitive.", "row",
      "`matrix` is a native primitive: `matrix<flt64>` names a type with no import.",
      expect="run:0",
      src=main_("    exit 0i32;", "func:m11mat = int32(matrix<flt64>:_~m) never fails { pass 0i32; };"),
      wrong="refused: matrix is a library type (lib/ntensor.npk), as §15 and LEXICAL §4 say",
      note="contradicts §15 (line 1500)")

claim("ty0309b", D, 309, "Hardware-accelerated dot products / SGEMM.", "row",
      "Matrix operations are hardware-accelerated dot products / SGEMM.",
      untestable="[vague] names no operation or instruction to check")

# ------------------------------------------------------------------ 3 strings
claim("ty0319", D, 319, "| `string` | `string<char8>` | `{ptr, i64, i64}` | 24 bytes | 8 |", "row",
      "`string` is 24 bytes with alignment 8.",
      expect="run:0", src=layout(["string"], 24, 8), wrong=layout_wrong(["string"], 24, 8))

claim("ty0319b", D, 319, "| `string` | `string<char8>` |", "row",
      "`string` is an alias for `string<char8>`: a `string<char8>` is accepted wherever a string is.",
      expect="run:0",
      src=main_("""    string<char8>:t = "abc";
    if (string_byte_length(t) != 3i64) { exit 10i32; }
    if (!(string_equals(t, "abc"))) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused: string<char8> is not the same type; or a wrong value (10, 11)")

claim("ty0320", D, 320, "| `string<char16>` | — | `{ptr, i64, i64}` | 24 bytes | 8 |", "row",
      "`string<char16>` is 24 bytes with alignment 8.",
      expect="run:0", src=layout(["string<char16>"], 24, 8), wrong=layout_wrong(["string<char16>"], 24, 8))
claim("ty0321", D, 321, "| `string<char32>` | — | `{ptr, i64, i64}` | 24 bytes | 8 |", "row",
      "`string<char32>` is 24 bytes with alignment 8.",
      expect="run:0", src=layout(["string<char32>"], 24, 8), wrong=layout_wrong(["string<char32>"], 24, 8))
claim("ty0322", D, 322, "| `cstring` | — | `{ptr, i64}` | 16 bytes | 8 |", "row",
      "`cstring` is 16 bytes with alignment 8.",
      expect="run:0", src=layout(["cstring"], 16, 8), wrong=layout_wrong(["cstring"], 16, 8))

claim("ty0327", D, 327, "is not NUL-terminated", "rule",
      "A `string` is `{ptr, len, cap}` and is not NUL-terminated.",
      untestable="[unobservable] a byte after a string's last is out of its bounds: no in-bounds read can see whether it is 0")

claim("ty0330", D, 330, "pointers are thin", "rule",
      "Pointers are thin: an `int8->` parameter is one `ptr`, with no bounds metadata.",
      expect="ir:" + sig("m11tp", r"\bi8", "ptr "),
      src=main_("""    int8:x = raw v8(5i8);
    int8->:p = @x;
    if (raw m11tp(p) != 5i8) { exit 10i32; }
    exit 0i32;""", "func:m11tp = int8(int8->:p) never fails { pass <-p; };"),
      wrong="a fat pointer ({ptr, i64} or wider)")

claim("ty0332", D, 332, "a `string` may carry an interior NUL", "rule",
      "A `string` may carry an interior NUL: one built at run time keeps all its bytes.",
      expect="run:0",
      src=main_(r"""    string:s = string_concat("a\0", "b");
    if (string_byte_length(s) != 3i64) { exit 10i32; }
    if (!(string_equals(s, "a\0b"))) { exit 11i32; }
    exit 0i32;"""),
      wrong="truncated at the NUL: length 1 (10), or the bytes changed (11)")

claim("ty0338", D, 338, "```llvm", "example",
      "A `string` is the struct `{ ptr, i64, i64 }`: a string parameter has that type.",
      expect="ir:" + sig("m11sl", r"\bi64", r"\{ ?ptr, i64, i64 ?\} "),
      src=main_("""    if (raw m11sl("hello") != 5i64) { exit 10i32; }
    exit 0i32;""", "func:m11sl = int64(string:s) never fails { pass string_byte_length(s); };"),
      wrong="another layout, or a string passed by pointer")

claim("ty0340", D, 340, "(heap-allocated data buffer)", "rule",
      "A string's data buffer is heap-allocated.",
      untestable="[vague] §3.3 (line 435) says a literal's buffer is constant data, so no one outcome is stated; no program here can see where a buffer lives")

claim("ty0341", D, 341, "length (number of char units, NOT bytes for char16/32)", "rule",
      "A string's length counts char units, which for `string` are bytes.", m10="t01_byte_length_utf8")

claim("ty0342", D, 342, "capacity (allocated char units)", "rule",
      "Field 2 of a string is its capacity in char units.",
      untestable="[internal] no accessor for the capacity is documented; a program cannot read it")

claim("ty0348", D, 348, "| 0 | 8 | data | `ptr`", "row",
      "The data pointer is at offset 0: the struct opens with `ptr` ({ptr, i64, i64}).",
      expect="ir:" + sig("m11sd", r"\bi64", r"\{ ?ptr, i64, i64 ?\} "),
      src=main_("""    if (raw m11sd("abc") != 3i64) { exit 10i32; }
    exit 0i32;""", "func:m11sd = int64(string:s) never fails { pass string_byte_length(s); };"),
      wrong="another field order")

claim("ty0349", D, 349, "| 8 | 8 | length | `i64` |", "row",
      "The length is field 1 (offset 8): `s.len` reads field 1 of the string struct.",
      expect=ir_fn("m11ln", r"(?:extractvalue \{ ?ptr, i64, i64 ?\} %\S+, 1\b|getelementptr [^\n]*\{ ?ptr, i64, i64 ?\}, ptr %\S+, i32 0, i32 1\b)"),
      src=main_("""    if (raw m11ln("abcde") != 5i64) { exit 10i32; }
    exit 0i32;""", "func:m11ln = int64(string:s) never fails { pass s.len; };"),
      wrong="the length read from another field")

claim("ty0350", D, 350, "| 16 | 8 | capacity | `i64` |", "row",
      "The capacity is field 2 (offset 16).",
      untestable="[internal] no accessor for the capacity is documented; its position shows only in the struct type ty0348 checks")

claim("ty0355", D, 355, "`+` is **concatenation**, NOT addition", "rule",
      "On `string`, `+` is concatenation.", m10="t14_string_plus_concatenates")

for i, op in enumerate(["-", "*", "/", "%"]):
    claim("ty0355" + ("b", "c", "d", "e")[i], D, 355, "No `-`, `*`, `/`, `%`.", "rule",
          "`%s` on strings is refused." % op,
          expect="refuse",
          src=main_("""    string:a = "abc";
    string:b = "b";
    string:c = a """ + op + """ b;
    if (string_byte_length(c) == 2i64) { exit 10i32; }
    exit 11i32;"""),
          wrong="accepted: `%s` means something on strings (exit 10 or 11)" % op)

claim("ty0358", D, 358, "allocates new buffer, copies both", "rule",
      "`a + b` allocates a new buffer and copies both operands: `a` and `b` stay usable and unchanged.",
      expect="run:0",
      src=main_("""    string:a = "ab";
    string:b = "cd";
    string:c = a + b;
    if (!(string_equals(c, "abcd"))) { exit 10i32; }
    if (!(string_equals(a, "ab"))) { exit 11i32; }
    if (!(string_equals(b, "cd"))) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused as a use after move (the operands consumed, not copied), or 10: wrong result; 11/12: an operand changed")

claim("ty0359", D, 359, "Comparison: `a.eq(b)`", "rule",
      "`a.eq(b)` (the prelude's string: Eq) compares byte by byte.",
      expect="run:0",
      src=main_("""    string:a = "abc";
    string:b = "abc";
    string:c = "abd";
    string:d = "ab";
    if (!(a.eq(b) ?! E9)) { exit 10i32; }
    if (a.eq(c) ?! E9) { exit 11i32; }
    if (a.eq(d) ?! E9) { exit 12i32; }
    exit 0i32;""", "error:E9;"),
      wrong="refused (no `eq`), or 10: equal strings unequal; 11: a byte ignored; 12: a prefix taken as equal",
      note="called with `?!` as M10's t16 calls the prelude's `cmp`")

claim("ty0359b", D, 359, "`string_eq(a, b)`", "rule",
      "`string_eq(a, b)` compares byte by byte.",
      expect="run:0",
      src=main_("""    if (!(string_eq("abc", "abc"))) { exit 10i32; }
    if (string_eq("abc", "abd")) { exit 11i32; }
    if (string_eq("ab", "abc")) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused (no `string_eq` for programs), or a wrong answer (10-12)",
      note="spelled as the builtin `string_equals` is called (a plain call); the text gives no call form")

claim("ty0360", D, 360, "**`==` and `!=` are REFUSED on a `string`**", "rule",
      "`==` on strings is refused: NITPICK-TYPE-034.", m10="m11_string_eq_refused")

claim("ty0360b", D, 360, "**`==` and `!=` are REFUSED on a `string`**", "rule",
      "`!=` on strings is refused: NITPICK-TYPE-034.",
      expect="refuse:NITPICK-TYPE-034",
      src=main_("""    string:a = "ab";
    string:b = "ab";
    if (a != b) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a pointer compare (10) or a byte compare (11)")

claim("ty0364", D, 364, "Ordering: `a.cmp(b)`", "rule",
      "`a.cmp(b)` orders strings lexicographically.", m10="t16_string_order")

claim("ty0365", D, 365, "the operators are refused as `==` is", "rule",
      "The ordering operators are refused on strings: `a < b` is refused.",
      expect="refuse",
      src=main_("""    string:a = "ab";
    string:b = "ac";
    if (a < b) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a pointer or byte order (10 or 11)")

claim("ty0365b", D, 365, "the operators are refused as `==` is", "rule",
      "The ordering operators are refused on strings: `a <=> b` is refused.",
      expect="refuse",
      src=main_("""    string:a = "ab";
    string:b = "ac";
    if ((a <=> b) < 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)")

claim("ty0366", D, 366, "Indexing: `char8:c = s[0];`", "rule",
      "`s[i]` returns the char at that index.", m10="t08_string_index")
claim("ty0366b", D, 366, "(bounds-checked)", "rule",
      "String indexing is bounds-checked: past the end traps OutOfBounds.", m10="t09_string_index_past_end")
claim("ty0367", D, 367, "Length: `int64:len = s.length;`", "rule",
      "A string's length is the field `s.length`.", m10="t02_length_spelled_length")

_STRFN = [
    (373, "charAt", "`charAt(s, i)` is the char at index i.",
     """    string:s = "hello";
    if (raw charAt(s, raw v64(1i64)) != 'e') { exit 10i32; }
    if (raw charAt(s, raw v64(4i64)) != 'o') { exit 11i32; }""",
     "refused (no such function), or the wrong char (10, 11)"),
    (374, "substring", "`substring(s, start, length)` extracts `length` chars from `start`.",
     """    string:t = raw substring("hello", raw v64(1i64), raw v64(3i64));
    if (!(string_equals(t, "ell"))) { exit 10i32; }""",
     "refused, or (start, end) read instead of (start, length): \"el\" (exit 10)"),
    (375, "split", "`split(s, c)` splits by the delimiter into its parts.",
     """    string[]:parts = raw split("a,b,c", ',');
    if (parts.len != 3i64) { exit 10i32; }
    if (!(string_equals(parts[1i64], "b"))) { exit 11i32; }""",
     "refused (a `string[]` view cannot own its parts: the D-070 argument the toCharArray row makes), or 10/11: wrong parts"),
    (376, "trim", "`trim` removes leading and trailing whitespace.",
     """    string:t = raw trim(" \t ab \n");
    if (!(string_equals(t, "ab"))) { exit 10i32; }""",
     "refused, or whitespace left (10)"),
    (377, "trimLeft", "`trimLeft` removes leading whitespace only.",
     """    string:t = raw trimLeft("  ab ");
    if (!(string_equals(t, "ab "))) { exit 10i32; }""",
     "refused, or the wrong side trimmed (10)"),
    (378, "trimRight", "`trimRight` removes trailing whitespace only.",
     """    string:t = raw trimRight("  ab ");
    if (!(string_equals(t, "  ab"))) { exit 10i32; }""",
     "refused, or the wrong side trimmed (10)"),
    (379, "contains", "`contains(s, t)` is a substring search.",
     """    if (!(raw contains("hello", "ell"))) { exit 10i32; }
    if (raw contains("hello", "elo")) { exit 11i32; }""",
     "refused, or a wrong answer (10: a substring missed; 11: a subsequence taken as a substring)"),
    (380, "startsWith", "`startsWith(s, p)` is a prefix check.",
     """    if (!(raw startsWith("hello", "he"))) { exit 10i32; }
    if (raw startsWith("hello", "el")) { exit 11i32; }""",
     "refused, or a wrong answer (10, 11)"),
    (381, "endsWith", "`endsWith(s, p)` is a suffix check.",
     """    if (!(raw endsWith("hello", "lo"))) { exit 10i32; }
    if (raw endsWith("hello", "ll")) { exit 11i32; }""",
     "refused, or a wrong answer (10, 11)"),
    (382, "indexOf", "`indexOf(s, c)` is the first occurrence's index, -1 if not found.",
     """    if (raw indexOf("hello", 'l') != 2i64) { exit 10i32; }
    if (raw indexOf("hello", 'z') != -1i64) { exit 11i32; }""",
     "refused, or 10: not the first occurrence; 11: not-found not -1"),
    (383, "toUpper", "`toUpper(s)` uppercases the ASCII letters and leaves other bytes alone.",
     """    string:t = raw toUpper("abC1");
    if (!(string_equals(t, "ABC1"))) { exit 10i32; }
    string:u = raw toUpper("é");
    if (!(string_equals(u, "é"))) { exit 11i32; }""",
     "refused (the name is also §2.1's char8 toUpper), or 10: wrong; 11: a non-ASCII letter uppercased"),
    (384, "toLower", "`toLower(s)` lowercases the ASCII letters and leaves other bytes alone.",
     """    string:t = raw toLower("ABc1");
    if (!(string_equals(t, "abc1"))) { exit 10i32; }
    string:u = raw toLower("É");
    if (!(string_equals(u, "É"))) { exit 11i32; }""",
     "refused (the name is also §2.1's char8 toLower), or 10: wrong; 11: a non-ASCII letter lowercased"),
    (386, "fromCharArray", "`fromCharArray(a)` copies a char array into a string.",
     """    char8[3]:a = ['x', 'y', 'z'];
    string:s = raw fromCharArray(a[0i64...3i64]);
    if (!(string_equals(s, "xyz"))) { exit 10i32; }""",
     "refused, or another string (10)"),
]
for ln, fn, text, body, wrong in _STRFN:
    claim("ty%04d" % ln, D, ln, "| `%s` |" % fn, "row", text, expect="run:0",
          src=main_(body + "\n    exit 0i32;"), wrong=wrong,
          note="Tier 1 (written in Nitpick), so called as a `never fails` function with `raw`")

claim("ty0373b", D, 373, "Get character at index (bounds-checked)", "row",
      "`charAt` is bounds-checked: an index past the end traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    string:s = "hello";
    char8:c = raw charAt(s, raw v64(5i64));
    if (c == '\\0') { exit 10i32; }
    exit 11i32;"""),
      wrong="no bounds check: a byte past the end (10 or 11), or refused (no such function)")

claim("ty0385", D, 385, "| `toCharArray` |", "row",
      "`toCharArray(s, dest)` copies into a caller-owned destination and returns the elements written.",
      expect="run:0",
      src=main_("""    char8[8]:buf = [];
    int64:n = toCharArray("abc", buf[0i64...8i64]) ?! E1;
    if (n != 3i64) { exit 10i32; }
    if (buf[0i64] != 'a') { exit 11i32; }
    if (buf[2i64] != 'c') { exit 12i32; }
    exit 0i32;""", "error:E1;"),
      wrong="refused (no such function), or 10: a wrong count; 11/12: the destination not written")

claim("ty0387", D, 387, "| `to_cstring` |", "row",
      "`to_cstring` fails on an interior NUL and succeeds on a clean string.", m10="t12_to_cstring_interior_nul")

claim("ty0388", D, 388, "| `to_string` |", "row",
      "`to_string(c)` copies a cstring out into a string.",
      expect="run:0",
      src=main_("""    cstring:c = to_cstring("abc") ?! E1;
    string:s = to_string(c);
    if (!(string_equals(s, "abc"))) { exit 10i32; }
    exit 0i32;""", "error:E1;"),
      wrong="refused (no free `to_string` builtin), or another string (10)")

claim("ty0392", D, 392, "so it cannot be", "rule",
      "A `string` cannot be handed to a syscall: passing one where a builtin takes a cstring is refused.",
      expect="refuse",
      src=main_("""    string:s = "/";
    if (path_exists(s)) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a non-terminated string reaches the kernel (exit 10 or 11)",
      note="`path_exists` (BUILTIN: cstring -> bool) is the syscall-taking builtin used")

claim("ty0393", D, 393, "`cstring` is the type that can", "rule",
      "A `cstring` can be handed to a syscall.",
      expect="run:0",
      src=main_("""    cstring:c = to_cstring("/") ?! E1;
    if (!(path_exists(c))) { exit 10i32; }
    exit 0i32;""", "error:E1;"),
      wrong="refused, or \"/\" reported absent (10)")

claim("ty0395", D, 395, "```", "example",
      "`cstring` is `{ ptr, len }`: a cstring parameter is the struct `{ ptr, i64 }`.",
      expect="ir:" + sig("m11cl", r"\bi64", r"\{ ?ptr, i64 ?\} "),
      src=main_("""    cstring:c = to_cstring("abcd") ?! E1;
    if (raw m11cl(c) != 4i64) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:m11cl = int64(cstring:c) never fails { pass c.len; };"""),
      wrong="another layout")

claim("ty0399", D, 399, "**The length is retained**", "rule",
      "A cstring retains its length: `.len` excludes the terminator.", m10="t13_cstring_keeps_length")

claim("ty0399b", D, 399, "The buffer is `len + 1` bytes with `buf[len] == 0u8`.", "rule",
      "A cstring's buffer holds a NUL at index len.",
      expect="run:0",
      src=main_("""    cstring:c = to_cstring("abc") ?! E1;
    wild char8->:p = c.ptr;
    char8:t = p[c.len];
    char8:f = p[0i64];
    if (t != '\\0') { exit 10i32; }
    if (f != 'a') { exit 11i32; }
    exit 0i32;""", "error:E1;"),
      wrong="no terminator (10), or the data elsewhere (11); refused if the field `ptr` is not readable",
      note="reads through the field `ptr` the layout at line 396 names")

claim("ty0400", D, 400, "never calls `strlen`", "rule",
      "nlibc never calls strlen: the unbounded scan is absent from every path and name in the library.",
      untestable="[tree] a claim about the library's source")

claim("ty0404", D, 404, "**`to_cstring` fails on an interior NUL.**", "rule",
      "`to_cstring` fails on an interior NUL.", m10="t12_to_cstring_interior_nul")

claim("ty0414", D, 414, "| string literal in `cstring` position | compile time", "row",
      "A string literal in cstring position costs nothing at run time: it is a NUL-terminated constant.",
      expect=r'ir:constant \[4 x i8\] c"abc\\00"',
      src=main_("""    cstring:c = "abc";
    if (c.len != 3i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no literal types as cstring), or the literal copied or scanned at run time",
      note="M9 measured that no string literal types as `cstring`")

claim("ty0414b", D, 414, "interior NUL is a compile error", "rule",
      "A string literal with an interior NUL in cstring position is a compile error.",
      expect="refuse",
      src=main_(r"""    cstring:c = "a\0b";
    if (c.len == 1i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a truncated cstring (10) or the NUL carried (11)",
      note="meaningful only if a clean literal is accepted in cstring position (ty0290, ty0414)")

claim("ty0415", D, 415, "| `to_cstring(s)` on a runtime `string`", "row",
      "`to_cstring` on a string built at run time: an interior NUL is Result.err, a clean one converts.",
      expect="run:0",
      src=main_(r"""    string:bad = string_concat("ab", "\0cd");
    Result<cstring>:r = to_cstring(bad);
    if (!r.is_error) { exit 10i32; }
    string:good = string_concat("ab", "cd");
    Result<cstring>:q = to_cstring(good);
    if (q.is_error) { exit 11i32; }
    exit 0i32;"""),
      wrong="the poison-NUL bypass: a silent truncation (10), or a clean string failed (11)")

claim("ty0418", D, 418, "until D-053 removed that type", "rule",
      "The `fmt` type was removed: a binding of type `fmt` is refused.",
      expect="refuse",
      src=main_("""    fmt:f = "abc";
    discard(f);
    exit 0i32;"""),
      wrong="accepted: fmt is a type")

claim("ty0420", D, 420, "`cstring` is immutable", "rule",
      "`cstring` is immutable: writing its field is refused.",
      expect="refuse",
      src=main_("""    cstring:c = to_cstring("abc") ?! E1;
    c.len = 1i64;
    if (c.len == 1i64) { exit 10i32; }
    exit 11i32;""", "error:E1;"),
      wrong="accepted: the terminator invariant broken (exit 10)")

claim("ty0421", D, 421, "is an explicit `to_string`", "rule",
      "cstring to string is only the explicit `to_string`: an implicit assignment is refused.",
      expect="refuse",
      src=main_("""    cstring:c = to_cstring("abc") ?! E1;
    string:s = c;
    if (string_byte_length(s) == 3i64) { exit 10i32; }
    exit 11i32;""", "error:E1;"),
      wrong="accepted: an implicit copy (exit 10 or 11)")

claim("ty0426", D, 426, "```nitpick", "example",
      "`string:greeting = \"Hello, world!\";` compiles, a 13-byte string.",
      expect="run:0",
      src=main_("""    string:greeting = "Hello, world!";
    if (string_byte_length(greeting) != 13i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or another length (10)")

claim("ty0430", D, 430, "```llvm", "example",
      "A string literal is emitted as a constant `[13 x i8]` of its bytes, with no NUL.",
      expect=r'ir:constant \[13 x i8\] c"Hello, world!"',
      src=main_("""    string:greeting = "Hello, world!";
    if (string_byte_length(greeting) != 13i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="a NUL-terminated [14 x i8], or the bytes built at run time")

# ------------------------------------------------------------------ 4 wide integers
claim("ty0453", D, 453, "i128 division emits the four `__divti3`-family libcalls", "rule",
      "i128 division works through the runtime floor's __divti3 family: signed and unsigned `/` and `%` compute and link.",
      expect="run:0",
      src=main_("""    int128:big = raw vi128(1i128) << raw vi128(100i128);
    int128:n = 0i128 - (big + raw vi128(7i128));
    int128:d = raw vi128(1i128) << raw vi128(90i128);
    if ((n / d) != -1024i128) { exit 10i32; }
    if ((n % d) != -7i128) { exit 11i32; }
    uint128:u = (raw vu128(1u128) << raw vu128(100u128)) + raw vu128(9u128);
    uint128:v = raw vu128(1u128) << raw vu128(64u128);
    if ((u / v) != (raw vu128(1u128) << raw vu128(36u128))) { exit 12i32; }
    if ((u % v) != 9u128) { exit 13i32; }
    exit 0i32;""", "func:vu128 = uint128(uint128:x) never fails { pass x; };"),
      wrong="a link failure (a libcall unprovided), or a wrong quotient/remainder (10-13)")

claim("ty0455", D, 455, "expands inline", "rule",
      "Division at a width above 128 expands inline: an int256 `/` and `%` compute and link with no libcall.",
      expect="run:0",
      src=main_("""    int256:one = raw w256(1i256);
    int256:n = 0i256 - ((one << raw w256(200i256)) + raw w256(5i256));
    int256:d = one << raw w256(190i256);
    if ((n / d) != -1024i256) { exit 10i32; }
    if ((n % d) != -5i256) { exit 11i32; }
    exit 0i32;""", "func:w256 = int256(int256:x) never fails { pass x; };"),
      wrong="a link failure (a libcall such as __divei4), or a wrong answer (10, 11)")

claim("ty0456", D, 456, "ARE the LLVM types; nothing is limbed", "rule",
      "Wide integers are the LLVM types: an int256 function takes and returns `i256` and adds through the i256 intrinsic.",
      expect=ir_all(sig("m11w", r"\bi256", "i256 "), _fn("m11w") + _body(r"@llvm\.sadd\.with\.overflow\.i256\(")),
      src=main_("""    if (raw m11w(raw w256(1i256), raw w256(2i256)) != 3i256) { exit 10i32; }
    exit 0i32;""", """func:w256 = int256(int256:x) never fails { pass x; };
func:m11w = int256(int256:a, int256:b) never fails { pass a + b; };"""),
      wrong="a limb struct, or limb-wise arithmetic")

for ln, types, sz in ((460, ["int128", "uint128", "tbb128"], 16), (461, ["int256", "uint256", "tbb256"], 32),
                      (462, ["int512", "uint512"], 64), (463, ["int1024", "uint1024"], 128),
                      (464, ["int2048", "uint2048"], 256), (465, ["int4096", "uint4096"], 512)):
    claim("ty%04d" % ln, D, ln, "| `%s` /" % types[0], "row",
          "%s are %d bytes with alignment 16." % (" / ".join("`%s`" % t for t in types), sz),
          expect="run:0", src=layout(types, sz, 16), wrong=layout_wrong(types, sz, 16))

claim("ty0469", D, 469, "put `{i8, i128}` at 32 bytes and `{i8, i256}` at 48", "rule",
      "`{int8, int128}` is 32 bytes and `{int8, int256}` is 48.",
      expect="run:0",
      src=main_("""    if (#size_of<P1>() != 32i64) { exit 10i32; }
    if (#size_of<P2>() != 48i64) { exit 11i32; }
    exit 0i32;""", """struct:P1 = { int8:a; int128:b; };
struct:P2 = { int8:a; int256:b; };"""),
      wrong="the frontend's bits/8 alignment (P2 at 64: exit 11), or alignment 8 (24 and 40)")

claim("ty0471", D, 471, "the frontend now stores exactly this column", "rule",
      "The frontend's layout of wide fields is LLVM's: `{int8, int256, int8}` is 64 bytes, `{int8, tbb256}` 48, and the fields round-trip.",
      expect="run:0",
      src=main_("""    if (#size_of<W>() != 64i64) { exit 10i32; }
    if (#size_of<T>() != 48i64) { exit 11i32; }
    int256:big = raw w256(1i256) << raw w256(200i256);
    W:w = W{ a: 1i8, b: big, c: 3i8 };
    if (w.b != big) { exit 12i32; }
    if (w.c != 3i8) { exit 13i32; }
    exit 0i32;""", """func:w256 = int256(int256:x) never fails { pass x; };
struct:W = { int8:a; int256:b; int8:c; };
struct:T = { int8:a; tbb256:b; };"""),
      wrong="a frontend offset that is not LLVM's (10, 11), or a field corrupted (12, 13)")

claim("ty0475", D, 475, "ordinary integer semantics at every width — D-037 wrapping", "rule",
      "The wide integers have D-037 wrapping: an int128 `+` past the maximum wraps to the minimum.",
      expect="run:0",
      src=main_("""    int128:big = raw vi128(1i128) << raw vi128(126i128);
    int128:mx = big + (big - raw vi128(1i128));
    int128:o = mx + raw vi128(1i128);
    if (o != ((0i128 - mx) - 1i128)) { exit 10i32; }
    exit 0i32;"""),
      wrong="a trap (IntOverflow, 93): D-210's checked arithmetic, as §1.2 (lines 53-58) and M10 o16 say",
      note="contradicts §1.2 (D-210: overflow traps at every width); the expectation follows this line's text")

claim("ty0476", D, 476, "D-092 explicit widening", "rule",
      "Widening to a wide integer is explicit: an int64 assigned to an int256 without `=>` is refused.",
      expect="refuse",
      src=main_("""    int256:w = raw v64(5i64);
    if (w == 5i256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: an implicit widening (exit 10)")

claim("ty0476b", D, 476, "D-092 explicit widening", "rule",
      "An explicit widening keeps the value: a negative int64 sign-extends, a uint64 zero-extends.",
      expect="run:0",
      src=main_("""    int256:w = raw v64(-5i64) => int256;
    if (w != -5i256) { exit 10i32; }
    uint256:u = raw vu64(18446744073709551615u64) => uint256;
    if (u != 18446744073709551615u256) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: zero-extended (a huge positive); 11: sign-extended")

claim("ty0477", D, 477, "structural INT_MIN/−1 check", "rule",
      "The signed minimum divided by -1 traps DivOverflow (at int8).", m10="v07_int8_min_div_minus_one")

claim("ty0476c", D, 476, "the D-142 division guards (zero divisor", "rule",
      "At a wide width, integer division by zero traps DivByZero.",
      expect="trap:DivByZero",
      src=main_("""    int256:q = raw w256(7i256) / raw w256(0i256);
    if (q == 0i256) { exit 10i32; }
    exit 11i32;""", "func:w256 = int256(int256:x) never fails { pass x; };"),
      wrong="no trap: a hardware fault (107) or a value (10, 11)")

claim("ty0477c", D, 477, "which is width-independent by construction", "rule",
      "At a wide width, the signed minimum divided by -1 traps DivOverflow.",
      expect="trap:DivOverflow",
      src=main_("""    int256:mn = raw w256(1i256) << raw w256(255i256);
    int256:q = mn / raw w256(-1i256);
    if (q == mn) { exit 10i32; }
    exit 11i32;""", "func:w256 = int256(int256:x) never fails { pass x; };"),
      wrong="no trap: the minimum back (10), or a fault (107)")

# ------------------------------------------------------------------ 5 tfp
_TFP_HELPERS = """func:vtf32 = tfp32(tfp32:x) never fails { pass x; };
func:vtf64 = tfp64(tfp64:x) never fails { pass x; };
func:vtf128 = tfp128(tfp128:x) never fails { pass x; };
func:vtf256 = tfp256(tfp256:x) never fails { pass x; };"""


def tfp_main(body, decls=""):
    """main_ with the tfp identity helpers the body calls"""
    hs = [h for h in _TFP_HELPERS.split("\n") if h.split(" ")[0][5:] + "(" in body]
    return main_(body, "\n".join(hs) + ("\n" + decls if decls else ""))


claim("ty0485", D, 485, "reserves a specific value (the most negative value)", "rule",
      "tfp's error state is the most negative raw value, and it is sticky.",
      expect="run:0",
      src=tfp_main("""    wild int8->:b = alloc(4i64);
    wild tfp32->:tp = b =>! wild tfp32->;
    wild uint32->:ip = b =>! wild uint32->;
    tfp32:e = ERR;
    <-tp = e;
    uint32:bits = <-ip;
    <-ip = 2147483648u32;
    tfp32:back = <-tp;
    <-ip = 2147483649u32;
    tfp32:v = <-tp;
    dalloc(b);
    if (bits != 2147483648u32) { exit 10i32; }
    if (!(is_err(back))) { exit 11i32; }
    if (is_err(v)) { exit 12i32; }
    if (!(is_err(e + raw vtf32(1.0tfp32)))) { exit 13i32; }
    exit 0i32;"""),
      wrong="10: ERR is another bit pattern; 11: the most negative raw is not ERR; 12: its neighbour is ERR too; 13: ERR not sticky",
      note="raw bits read through a wild buffer, as the compiler's tfp_tostring test builds raw values")

claim("ty0487", D, 487, "resolve to this error state rather than crashing", "rule",
      "tfp operations that overflow or divide by zero resolve to ERR rather than trapping.",
      expect="run:0",
      src=tfp_main("""    tfp64:d = raw vtf64(2.5tfp64) / raw vtf64(0.0tfp64);
    if (!(is_err(d))) { exit 10i32; }
    tfp32:m = raw vtf32(32767.5tfp32);
    if (!(is_err(m + m))) { exit 11i32; }
    if (!(is_err(m * m))) { exit 12i32; }
    exit 0i32;"""),
      wrong="a trap (DivByZero 97 / IntOverflow 93), or a value that is not ERR (10-12)")

_TFP_ROWS = [
    (491, "tfp32", 4, 4, "Q16.16", "0.0000152587890625", "256.0", "32767.5"),
    (492, "tfp64", 8, 8, "Q32.32", "0.00000000023283064365386962890625", "65536.0", "2147483647.5"),
    (493, "tfp128", 16, 16, "Q64.64", "0.0000000000000000000542101086242752217003726400434970855712890625",
     "4294967296.0", "9223372036854775807.5"),
]
for ln, t, sz, al, q, eps, half, top in _TFP_ROWS:
    body = ("    " + t + ":eps = raw vtf" + t[3:] + "(" + eps + t + ");\n"
            "    if (((eps * " + half + t + ") * " + half + t + ") != 1.0" + t + ") { exit 12i32; }\n"
            "    " + t + ":top = raw vtf" + t[3:] + "(" + top + t + ");\n"
            "    if (is_err(top + 0.25" + t + ")) { exit 13i32; }\n"
            "    if (!(is_err(top + 1.0" + t + "))) { exit 14i32; }")
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` is %d bytes, alignment %d, format %s: the least step is 2^-%d and the integer part tops out at 2^%d - 1."
          % (t, sz, al, q, sz * 4, sz * 4 - 1),
          expect="run:0",
          src=layout([t], sz, al, decls=[h for h in _TFP_HELPERS.split("\n") if ("vtf" + t[3:] + " ") in h][0],
                     body=body),
          wrong=layout_wrong([t], sz, al) + "; 12: another fraction width; 13: an integer part narrower than %s; "
                "14: wider (no ERR past the top)" % q)

claim("ty0494", D, 494, "| `tfp256` | `i256` | 32 bytes | Q128.128 | 16 |", "row",
      "`tfp256` is 32 bytes, alignment 16, format Q128.128: 2^-128 is its least step and the integer part tops out at 2^127 - 1.",
      expect="run:0",
      src=layout(["tfp256"], 32, 16, decls="func:vtf256 = tfp256(tfp256:x) never fails { pass x; };",
                 body="""    tfp256:k = raw vtf256(18446744073709551616.0tfp256);
    tfp256:e = (raw vtf256(1.0tfp256) / k) / k;
    if (!(e > 0.0tfp256)) { exit 12i32; }
    if (((e * k) * k) != 1.0tfp256) { exit 13i32; }
    if ((e / 4.0tfp256) != 0.0tfp256) { exit 14i32; }
    tfp256:top = raw vtf256(170141183460469231731687303715884105727.5tfp256);
    if (is_err(top + 0.25tfp256)) { exit 15i32; }
    if (!(is_err(top + 1.0tfp256))) { exit 16i32; }"""),
      wrong=layout_wrong(["tfp256"], 32, 16) + "; 12-14: another fraction width; 15: a narrower integer part; 16: a wider one",
      note="the least step is built by division (Div is `(a << F) / b`, line 506) since its decimal has 128 digits")

claim("ty0497", D, 497, "```nitpick", "example",
      "Suffixing a numeric literal with the type name makes a tfp literal of that value.",
      expect="run:0",
      src=main_("""    tfp256:pi = 3.14159265358979323846tfp256;
    tfp64:half = 0.5tfp64;
    tfp32:ratio = 1.5tfp32;
    if ((half + half) != 1.0tfp64) { exit 10i32; }
    if ((ratio * 2.0tfp32) != 3.0tfp32) { exit 11i32; }
    if (!((pi > 3.140625tfp256) && (pi < 3.1416015625tfp256))) { exit 12i32; }
    exit 0i32;"""),
      wrong="a literal refused (pi is not a dyadic rational: 'exact literals', line 596, may refuse it), or a wrong value (10-12)")

claim("ty0504", D, 504, "Add/sub: same as integer add/sub on the raw representation", "rule",
      "tfp add and subtract are the integer add/sub of the raw values.",
      expect="run:0",
      src=tfp_main("""    tfp32:a = raw vtf32(1.25tfp32);
    tfp32:b = raw vtf32(2.5tfp32);
    if ((a + b) != 3.75tfp32) { exit 10i32; }
    if ((a - b) != -1.25tfp32) { exit 11i32; }
    exit 0i32;"""),
      wrong="a wrong sum (10) or difference (11)")

claim("ty0505", D, 505, "Mul: `(a * b) >> FRAC_BITS`", "rule",
      "tfp multiply is `(a * b) >> FRAC_BITS` on the raws: the shift floors, so -2^-16 * 0.5 is -2^-16 and 2^-16 * 0.5 is 0.",
      expect="run:0",
      src=tfp_main("""    tfp32:a = raw vtf32(1.5tfp32);
    if ((a * raw vtf32(2.5tfp32)) != 3.75tfp32) { exit 10i32; }
    tfp32:half = raw vtf32(0.5tfp32);
    tfp32:eps = raw vtf32(0.0000152587890625tfp32);
    if ((eps * half) != 0.0tfp32) { exit 11i32; }
    tfp32:neps = raw vtf32(-0.0000152587890625tfp32);
    if ((neps * half) != neps) { exit 12i32; }
    exit 0i32;"""),
      wrong="10: a wrong product; 11: a rounding up; 12: truncation toward zero (0) instead of the formula's arithmetic shift",
      note="exit 12 tests the formula literally: `>>` of a negative raw floors")

claim("ty0506", D, 506, "Div: `(a << FRAC_BITS) / b`", "rule",
      "tfp divide is `(a << FRAC_BITS) / b` on the raws, an integer division that truncates toward zero: 1/3 and -1/3 are ±21845/65536 at tfp32.",
      expect="run:0",
      src=tfp_main("""    tfp32:three = raw vtf32(3.0tfp32);
    if ((raw vtf32(1.0tfp32) / three) != 0.3333282470703125tfp32) { exit 10i32; }
    if ((raw vtf32(-1.0tfp32) / three) != -0.3333282470703125tfp32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: a rounded-up quotient; 11: a floored quotient (-21846/65536)")

claim("ty0507", D, 507, "Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`, `<=>` (spaceship)", "rule",
      "tfp values compare with all six operators and `<=>`, which yields -1, 0 or 1.",
      expect="run:0",
      src=tfp_main("""    tfp32:a = raw vtf32(-1.5tfp32);
    tfp32:b = raw vtf32(0.25tfp32);
    if (!(a < b)) { exit 10i32; }
    if (!(a <= b)) { exit 11i32; }
    if (a > b) { exit 12i32; }
    if (a >= b) { exit 13i32; }
    if (a == b) { exit 14i32; }
    if (!(a != b)) { exit 15i32; }
    if ((a <=> b) != -1i32) { exit 16i32; }
    if ((b <=> a) != 1i32) { exit 17i32; }
    if ((b <=> raw vtf32(0.25tfp32)) != 0i32) { exit 18i32; }
    exit 0i32;"""),
      wrong="an operator refused, an unsigned raw compare (-1.5 above 0.25: 10-13), or `<=>` wrong (16-18)")

claim("ty0509", D, 509, "overflow produce the `ERR` sentinel", "rule",
      "An overflowing tfp operation produces ERR and it is sticky: ERR * 0, ERR - ERR and -ERR stay ERR.",
      expect="run:0",
      src=tfp_main("""    tfp64:m = raw vtf64(2147483647.5tfp64);
    tfp64:e = m + m;
    if (!(is_err(e))) { exit 10i32; }
    if (!(is_err(e * raw vtf64(0.0tfp64)))) { exit 11i32; }
    if (!(is_err(e - e))) { exit 12i32; }
    if (!(is_err(-e))) { exit 13i32; }
    exit 0i32;"""),
      wrong="10: no ERR on overflow; 11-13: ERR laundered by `* 0`, `e - e` or negation")

claim("ty0510", D, 510, "a comparison on an ERR operand TRAPS to `failsafe`", "rule",
      "A comparison with an ERR tfp operand traps to failsafe (TbbErr, the family's one trap, line 723).",
      expect="trap:TbbErr",
      src=tfp_main("""    tfp32:e = raw vtf32(1.0tfp32) / raw vtf32(0.0tfp32);
    if (e == raw vtf32(0.0tfp32)) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap: the comparison answers true (10) or false (11), the NaN-style reading")

claim("ty0512", D, 512, "`is_err(x)` is the test that looks", "rule",
      "`is_err` tests a tfp for ERR without trapping.",
      expect="run:0",
      src=tfp_main("""    tfp32:e = raw vtf32(1.0tfp32) / raw vtf32(0.0tfp32);
    if (!(is_err(e))) { exit 10i32; }
    if (is_err(raw vtf32(1.0tfp32))) { exit 11i32; }
    exit 0i32;"""),
      wrong="a trap (TbbErr 110) on the look, or a wrong answer (10, 11)")

claim("ty0514", D, 514, "Remainder: `%` — the same-scale remainder", "rule",
      "tfp `%` is the same-scale remainder (the sign of the dividend), and `% 0` is ERR.",
      expect="run:0",
      src=tfp_main("""    tfp64:b = raw vtf64(2.0tfp64);
    if ((raw vtf64(5.5tfp64) % b) != 1.5tfp64) { exit 10i32; }
    if ((raw vtf64(-5.5tfp64) % b) != -1.5tfp64) { exit 11i32; }
    if (!(is_err(raw vtf64(5.5tfp64) % raw vtf64(0.0tfp64)))) { exit 12i32; }
    exit 0i32;"""),
      wrong="10: a wrong remainder; 11: a floored remainder (0.5); 12: `% 0` not ERR (or a DivByZero trap, 97)")

claim("ty0515", D, 515, "Unary negation: `-val` (total", "rule",
      "tfp negation is total: the most positive value negates to a valid value (not ERR), and -ERR is ERR.",
      expect="run:0",
      src=tfp_main("""    tfp32:mx = raw vtf32(32767.9999847412109375tfp32);
    tfp32:n = -mx;
    if (is_err(n)) { exit 10i32; }
    if ((n + mx) != 0.0tfp32) { exit 11i32; }
    tfp32:e = ERR;
    if (!(is_err(-e))) { exit 12i32; }
    exit 0i32;"""),
      wrong="10: negation of the top overflows to ERR; 11: a wrong negation; 12: -ERR laundered")

claim("ty0516", D, 516, "Shift / bitwise on the raw representation~~ — STRUCK", "rule",
      "Bitwise operators on tfp are struck: `a & b` is refused.",
      expect="refuse",
      src=tfp_main("""    tfp32:c = raw vtf32(1.5tfp32) & raw vtf32(2.5tfp32);
    if (c == 0.5tfp32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: the raw bits exposed (exit 10 or 11)")

claim("ty0516b", D, 516, "Shift / bitwise on the raw representation~~ — STRUCK", "rule",
      "Shifts on tfp are struck: `x << 1` is refused (`ERR << 1` would launder ERR to zero).",
      expect="refuse",
      src=tfp_main("""    tfp32:c = raw vtf32(1.5tfp32) << 1i32;
    if (c == 3.0tfp32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10 or 11)",
      note="the amount's type is a guess (int32); the claim is the refusal of any tfp shift")

claim("ty0518", D, 518, "Scaling is multiplication by a power-of-two constant", "rule",
      "Scaling a tfp is multiplication by a power-of-two constant, exact both ways.",
      expect="run:0",
      src=tfp_main("""    tfp32:x = raw vtf32(3.25tfp32);
    if ((x * 4.0tfp32) != 13.0tfp32) { exit 10i32; }
    if ((x * 0.25tfp32) != 0.8125tfp32) { exit 11i32; }
    exit 0i32;"""),
      wrong="an inexact scaling (10, 11)")

claim("ty0520", D, 520, "`floor` and `trunc` are METHODS on every width", "rule",
      "`.floor()` (toward -inf) and `.trunc()` (toward zero) are methods at every tfp width.",
      expect="run:0",
      src=tfp_main("""    tfp32:a = raw vtf32(-2.5tfp32);
    if (a.floor() != -3.0tfp32) { exit 10i32; }
    if (a.trunc() != -2.0tfp32) { exit 11i32; }
    tfp64:b = raw vtf64(-2.5tfp64);
    if (b.floor() != -3.0tfp64) { exit 12i32; }
    if (b.trunc() != -2.0tfp64) { exit 13i32; }
    tfp128:c = raw vtf128(-2.5tfp128);
    if (c.floor() != -3.0tfp128) { exit 14i32; }
    if (c.trunc() != -2.0tfp128) { exit 15i32; }
    tfp256:d = raw vtf256(-2.5tfp256);
    if (d.floor() != -3.0tfp256) { exit 16i32; }
    if (d.trunc() != -2.0tfp256) { exit 17i32; }
    exit 0i32;"""),
      wrong="a method missing at a width (refused), or floor/trunc swapped or wrong on a negative (10-17)")


claim("ty0521", D, 521, "`tfp256_*` free-function family", "rule",
      "The `tfp256_*` free functions are struck: `tfp256_floor(x)` is refused.",
      expect="refuse",
      src=tfp_main("""    tfp256:x = raw vtf256(3.5tfp256);
    tfp256:f = raw tfp256_floor(x);
    if (f == 3.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: the struck family still resolves (exit 10)")

claim("ty0522", D, 522, "```nitpick", "example",
      "`3.7tfp256.floor()` and `.trunc()` are both 3.0tfp256.",
      expect="run:0",
      src=main_("""    tfp256:x = 3.7tfp256;
    tfp256:floored = x.floor();   // -> 3.0tfp256 (toward -inf)
    tfp256:trunced = x.trunc();   // -> 3.0tfp256 (toward zero)
    if (floored != 3.0tfp256) { exit 10i32; }
    if (trunced != 3.0tfp256) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (3.7 is not dyadic: 'exact literals' may refuse it), or a wrong result (10, 11)")

claim("ty0529", D, 529, "```nitpick", "example",
      "The cast block's accepted lines compile and compute: 42.5 into flt64 both ways, 42 by `=>!` to int64, "
      "42.5 narrowed to tfp64, 1.5 widened to tfp128.",
      expect="run:0",
      src=main_("""    tfp32:g = 42.5tfp32;
    flt64:fl  = g => flt64;         // OK — 32 raw bits fit a 53-bit mantissa exactly
    tfp256:f = 42.5tfp256;
    flt64:f2  = f =>! flt64;        // Q128.128 into 52 mantissa bits LOSES (corrected at 1.3.2)
    int64:i2  = f =>! int64;        // OK — explicit opt-in, truncates toward zero, yields 42
    tfp64:f64 = f =>! tfp64;        // narrowing: precision loss, so =>! is required
    tfp128:w  = 1.5tfp64 => tfp128; // widening keeps every value; ERR maps to ERR
    if (fl != 42.5f64) { exit 10i32; }
    if (f2 != 42.5f64) { exit 11i32; }
    if (i2 != 42i64) { exit 12i32; }
    if (f64 != 42.5tfp64) { exit 13i32; }
    if (w != 1.5tfp128) { exit 14i32; }
    exit 0i32;"""),
      wrong="a line refused, or a wrong value (10-14)",
      note="the block's `int64:i = f => int64;` (a COMPILE ERROR by its own comment) is left out here: ty0534")

claim("ty0531", D, 531, "32 raw bits fit a 53-bit mantissa exactly", "rule",
      "`tfp32 => flt64` is accepted and exact, even for a value using all 32 raw bits.",
      expect="run:0",
      src=tfp_main("""    tfp32:g = raw vtf32(-32767.9999847412109375tfp32);
    flt64:fl = g => flt64;
    if (fl != -32767.9999847412109375f64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (`=>!` demanded), or an inexact conversion (10)")

claim("ty0533", D, 533, "Q128.128 into 52 mantissa bits LOSES", "rule",
      "tfp256 into flt64 loses precision, so the plain `=>` is refused.",
      expect="refuse",
      src=tfp_main("""    flt64:f2 = raw vtf256(42.5tfp256) => flt64;
    if (f2 == 42.5f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a lossy `=>` (exit 10)")

claim("ty0534", D, 534, "COMPILE ERROR — drops the fractional part", "rule",
      "`tfp256 => int64` is a compile error: it drops the fractional part.",
      expect="refuse",
      src=tfp_main("""    int64:i = raw vtf256(42.5tfp256) => int64;
    if (i == 42i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a lossy `=>` (exit 10 or 11)")

claim("ty0535", D, 535, "truncates toward zero, yields 42", "rule",
      "`tfp256 =>! int64` truncates toward zero: 42.5 gives 42 and -42.5 gives -42.",
      expect="run:0",
      src=tfp_main("""    if ((raw vtf256(42.5tfp256) =>! int64) != 42i64) { exit 10i32; }
    if ((raw vtf256(-42.5tfp256) =>! int64) != -42i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: rounding (43); 11: flooring (-43)")

claim("ty0536", D, 536, "narrowing: precision loss, so =>! is required", "rule",
      "Narrowing tfp256 to tfp64 requires `=>!`: the plain `=>` is refused.",
      expect="refuse",
      src=tfp_main("""    tfp64:f64 = raw vtf256(42.5tfp256) => tfp64;
    if (f64 == 42.5tfp64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a lossy `=>` (exit 10)")

claim("ty0537", D, 537, "widening keeps every value; ERR maps to ERR", "rule",
      "Widening tfp64 to tfp128 keeps every value (the most negative valid one included) and maps ERR to ERR.",
      expect="run:0",
      src=tfp_main("""    tfp64:a = raw vtf64(-2147483647.99999999976716935634613037109375tfp64);
    tfp128:w = a => tfp128;
    if (w != -2147483647.99999999976716935634613037109375tfp128) { exit 10i32; }
    tfp64:e = ERR;
    tfp128:we = e => tfp128;
    if (!(is_err(we))) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: an edge value changed; 11: ERR's raw bits sign-extended into a valid tfp128 (-2^31)")

claim("ty0540", D, 540, "A cast OUT of the family TRAPS on an ERR operand under BOTH spellings", "rule",
      "A cast of an ERR tfp out of the family with `=>!` traps (TbbErr).",
      expect="trap:TbbErr",
      src=tfp_main("""    tfp64:e = raw vtf64(1.0tfp64) / raw vtf64(0.0tfp64);
    int64:k = e =>! int64;
    if (k == 0i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap: ERR laundered into a number (10 or 11)")

claim("ty0540b", D, 540, "under BOTH spellings", "rule",
      "A cast of an ERR tfp out of the family with the plain `=>` traps (TbbErr).",
      expect="trap:TbbErr",
      src=tfp_main("""    tfp32:e = raw vtf32(1.0tfp32) / raw vtf32(0.0tfp32);
    flt64:f = e => flt64;
    if (f < 0.0f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap: ERR converted to -32768.0 (10) or another number (11)")

claim("ty0544", D, 544, "is a **compile-time error** wherever data loss is possible", "rule",
      "`=>` is a compile-time error wherever data loss is possible: `flt64 => tfp32` is refused.",
      expect="refuse",
      src=main_("""    tfp32:t = raw vf64(3.5f64) => tfp32;
    if (t == 3.5tfp32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a lossy `=>` (exit 10 or 11)")

# ------------------------------------------------------------------ 5a dim256
claim("ty0553", D, 553, "Only `dim256` supports", "rule",
      "Only dim256 takes a unit annotation: `tfp64<Meters>` is refused.",
      expect="refuse",
      src=tfp_main("""    tfp64<Meters>:x = raw vtf64(1.0tfp64);
    if (x == 1.0tfp64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a narrower fixed-point type with a unit (exit 10 or 11)")


claim("ty0559", D, 559, "vectors themselves and is TOTAL", "rule",
      "The unit algebra is total: products and quotients whose vectors nothing names compose and cancel.",
      expect="run:0",
      src=main_("""    dim256<Kilograms>:m = 2.0dim256<Kilograms>;
    dim256<Kilograms>:back = (m * m * m * m * m) / (m * m * m * m);
    if ((back => tfp256) != 2.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: an unnamed intermediate (Kilograms^5) has no type; or a wrong value (10)")

claim("ty0560", D, 560, "Two `dim256` types are the same type", "rule",
      "Two dim256 types are the same exactly when their vectors are equal: Kilograms * (m/s)^2 and Newtons * Meters are both Joules.",
      expect="run:0",
      src=main_("""    dim256<Kilograms>:m = 2.0dim256<Kilograms>;
    dim256<MetersPerSecond>:v = 3.0dim256<MetersPerSecond>;
    dim256<Joules>:ke = m * (v * v);
    dim256<Newtons>:f = 4.0dim256<Newtons>;
    dim256<Meters>:d = 2.0dim256<Meters>;
    dim256<Joules>:w = f * d;
    dim256<Joules>:sum = ke + w;
    if ((ke => tfp256) != 18.0tfp256) { exit 10i32; }
    if ((sum => tfp256) != 26.0tfp256) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused: equal vectors under different names are different types; or a wrong value (10, 11)")

claim("ty0562", D, 562, "which is why `dist / dist` is a bare", "rule",
      "The dimensionless vector IS tfp256: `dist / dist` is a bare tfp256.",
      expect="run:0",
      src=main_("""    dim256<Meters>:d = 5.0dim256<Meters>;
    tfp256:r = d / d;
    if (r != 1.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: the quotient is a dimensionless dim256; or a wrong value (10)")

claim("ty0563", D, 563, "why bare `dim256` (as an annotation or a literal suffix) is", "rule",
      "Bare `dim256` as an annotation is refused.",
      expect="refuse",
      src=tfp_main("""    dim256:x = raw vtf256(5.0tfp256);
    if ((x => tfp256) == 5.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: bare dim256 as a second name for tfp256 (exit 10)")

claim("ty0564", D, 564, "refused — the dimensionless type already has a name", "rule",
      "Bare `dim256` as a literal suffix is refused.",
      expect="refuse",
      src=main_("""    tfp256:y = 5.0dim256;
    if (y == 5.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10)")

claim("ty0567", D, 567, "```nitpick", "example",
      "`dim256<Unit>` bindings take `dim256<Unit>`-suffixed literals of those values.",
      expect="run:0",
      src=main_("""    dim256<Joules>:energy = 1000.0dim256<Joules>;
    dim256<Meters>:dist   = 5.0dim256<Meters>;
    dim256<Seconds>:time  = 2.0dim256<Seconds>;
    if ((energy => tfp256) != 1000.0tfp256) { exit 10i32; }
    if ((dist => tfp256) != 5.0tfp256) { exit 11i32; }
    if ((time => tfp256) != 2.0tfp256) { exit 12i32; }
    exit 0i32;"""),
      wrong="a spelling refused, or a wrong value (10-12)")

claim("ty0573", D, 573, "The seven SI base units are compiler-declared", "rule",
      "The seven SI base units Kilograms, Meters, Seconds, Amperes, Kelvin, Moles and Candela are declared.",
      expect="run:0",
      src=main_("""    dim256<Kilograms>:a = 1.0dim256<Kilograms>;
    dim256<Meters>:b = 1.0dim256<Meters>;
    dim256<Seconds>:c = 1.0dim256<Seconds>;
    dim256<Amperes>:d = 1.0dim256<Amperes>;
    dim256<Kelvin>:e = 1.0dim256<Kelvin>;
    dim256<Moles>:f = 1.0dim256<Moles>;
    dim256<Candela>:g = 1.0dim256<Candela>;
    tfp256:s = (a => tfp256) + (b => tfp256) + (c => tfp256) + (d => tfp256) + (e => tfp256) + (f => tfp256) + (g => tfp256);
    if (s != 7.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="a base unit missing (refused), or a wrong value (10)")

claim("ty0576", D, 576, "`Pascals`, `Watts`, `MetersPerSecond`, …) are PRELUDE declarations", "rule",
      "The derived names Newtons, Joules, Hertz, Pascals, Watts and MetersPerSecond are declared in the prelude with their SI vectors.",
      expect="run:0",
      src=main_("""    dim256<Kilograms>:kg = 2.0dim256<Kilograms>;
    dim256<Meters>:m = 3.0dim256<Meters>;
    dim256<Seconds>:s = 0.5dim256<Seconds>;
    dim256<Newtons>:n = (kg * m) / (s * s);
    dim256<Joules>:j = n * m;
    dim256<Hertz>:hz = 1.0tfp256 / s;
    dim256<Pascals>:pa = n / (m * m);
    dim256<Watts>:w = j / s;
    dim256<MetersPerSecond>:v = m / s;
    if ((n => tfp256) != 24.0tfp256) { exit 10i32; }
    if ((j => tfp256) != 72.0tfp256) { exit 11i32; }
    if ((hz => tfp256) != 2.0tfp256) { exit 12i32; }
    if ((pa => tfp256) != (24.0tfp256 / 9.0tfp256)) { exit 13i32; }
    if ((w => tfp256) != 144.0tfp256) { exit 14i32; }
    if ((v => tfp256) != 6.0tfp256) { exit 15i32; }
    exit 0i32;"""),
      wrong="a name missing or with another vector (refused), or a wrong value (10-15)")

claim("ty0580", D, 580, "```nitpick", "example",
      "Unit declarations of this form compile, and a declared name is its vector's name (Furlongs is Meters).",
      expect="run:0",
      src=main_("""    dim256<Furlongs>:x = 3.0dim256<Furlongs>;
    dim256<Meters>:y = x + 1.0dim256<Meters>;
    if ((y => tfp256) != 4.0tfp256) { exit 10i32; }
    dim256<Hertz>:f = 1.0tfp256 / 4.0dim256<Seconds>;
    if ((f => tfp256) != 0.25tfp256) { exit 11i32; }
    dim256<Newtons>:n = (2.0dim256<Kilograms> * 3.0dim256<Meters>) / (1.0dim256<Seconds> * 1.0dim256<Seconds>);
    if ((n => tfp256) != 6.0tfp256) { exit 12i32; }
    exit 0i32;""", """unit:Hertz = 1 / Seconds;
unit:Newtons = Kilograms * Meters / (Seconds * Seconds);
pub unit:Furlongs = Meters;   // a name is a name for a VECTOR — this one
                              // equals Meters' vector; declare it only to
                              // write it in annotations"""),
      wrong="refused (a program may not write the prelude's Hertz/Newtons again, or the form does not parse), or a wrong value (10-12)",
      note="taken literally: Hertz and Newtons are also prelude declarations (line 576)")

claim("ty0588", D, 588, "unit names, `1`, `*`, `/`,", "rule",
      "A unit declaration's right-hand side is unit algebra only: a number other than 1 is refused.",
      expect="refuse",
      src=main_("""    dim256<Bad>:b = 1.0dim256<Bad>;
    if ((b => tfp256) == 1.0tfp256) { exit 10i32; }
    exit 11i32;""", "unit:Bad = 2 * Meters;"),
      wrong="accepted: a scaled unit (exit 10 or 11)")

claim("ty0589", D, 589, "An annotation position takes a", "rule",
      "An annotation takes a single unit name, never an inline expression: `dim256<Meters / Seconds>` is refused.",
      expect="refuse",
      src=main_("""    dim256<Meters / Seconds>:v = 1.0dim256<MetersPerSecond>;
    if ((v => tfp256) == 1.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: an inline unit expression (exit 10)")

claim("ty0593", D, 593, "is IDENTICAL to bare `tfp256` at the", "rule",
      "`dim256<Joules>` is identical to tfp256 at the IR: functions over each take and return `i256`.",
      expect=ir_all(sig("m11dj", r"\bi256", "i256 "), sig("m11tf", r"\bi256", "i256 ")),
      src=main_("""    dim256<Joules>:j = raw m11dj(5.0dim256<Joules>);
    tfp256:t = raw m11tf(5.0tfp256);
    if ((j => tfp256) != t) { exit 10i32; }
    exit 0i32;""", """func:m11dj = dim256<Joules>(dim256<Joules>:x) never fails { pass x; };
func:m11tf = tfp256(tfp256:x) never fails { pass x; };"""),
      wrong="a unit-carrying representation, or two different carriers",
      note="i256 is row 494's carrier; the block at line 648 says `{ i64, i64, i64, i64 }` instead (ty0648)")

claim("ty0595", D, 595, "every D-195 `tfp256` rule (ERR discipline, saturation", "rule",
      "Every tfp256 rule applies to dim256 unchanged: floor/trunc, saturation to ERR, ERR on division by zero.",
      expect="run:0",
      src=tfp_main("""    dim256<Meters>:x = -3.75dim256<Meters>;
    if ((x.floor() => tfp256) != -4.0tfp256) { exit 10i32; }
    if ((x.trunc() => tfp256) != -3.0tfp256) { exit 11i32; }
    dim256<Meters>:big = 170141183460469231731687303715884105727.0dim256<Meters>;
    if (!(is_err(big + big))) { exit 12i32; }
    dim256<Seconds>:z = raw vtf256(0.0tfp256) =>! dim256<Seconds>;
    if (!(is_err(x / z))) { exit 13i32; }
    exit 0i32;"""),
      wrong="10/11: floor/trunc wrong or missing; 12: no saturation; 13: no ERR (or a trap)")

claim("ty0599", D, 599, "```nitpick", "example",
      "Units are tracked through arithmetic: `dim256<Meters>:speed = dist / time;` is a compile error.",
      expect="refuse",
      src=main_("""    // Units are tracked through arithmetic:
    dim256<Meters>:dist  = 10.0dim256<Meters>;
    dim256<Seconds>:time = 5.0dim256<Seconds>;
    dim256<Meters>:speed = dist / time;      // ERROR: Meters/Seconds != Meters
    dim256<Newtons>:force = 2.0dim256<Newtons>;
    // Multiply creates compound units — the algebra is total, no registration:
    dim256<Joules>:work = force * dist;      // OK: Newtons * Meters IS the Joules vector
    if ((work => tfp256) != 20.0tfp256) { exit 10i32; }
    if ((speed => tfp256) != 2.0tfp256) { exit 11i32; }
    exit 0i32;"""),
      wrong="accepted: the unit mismatch unseen (exit 11 or 0)",
      note="`force` is declared (the block leaves it undeclared); the OK line alone is ty0608")

claim("ty0608", D, 608, "OK: Newtons * Meters IS the Joules vector", "rule",
      "`force * dist` of Newtons and Meters is a Joules value, with no registration.",
      expect="run:0",
      src=main_("""    dim256<Newtons>:force = 2.0dim256<Newtons>;
    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Joules>:work = force * dist;
    if ((work => tfp256) != 20.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or a wrong value (10)")

claim("ty0612", D, 612, "Adding/subtracting/`%` same unit", "rule",
      "`+`, `-` and `%` of the same unit keep the unit.",
      expect="run:0",
      src=main_("""    dim256<Meters>:a = 10.0dim256<Meters>;
    dim256<Meters>:b = 3.0dim256<Meters>;
    dim256<Meters>:s = a + b;
    dim256<Meters>:d = a - b;
    dim256<Meters>:r = a % b;
    if ((s => tfp256) != 13.0tfp256) { exit 10i32; }
    if ((d => tfp256) != 7.0tfp256) { exit 11i32; }
    if ((r => tfp256) != 1.0tfp256) { exit 12i32; }
    exit 0i32;"""),
      wrong="an operator refused or the unit lost, or a wrong value (10-12)")

claim("ty0613", D, 613, "Adding/subtracting different units", "rule",
      "Adding different units is a compile-time error.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:time = 5.0dim256<Seconds>;
    dim256<Meters>:x = dist + time;
    if ((x => tfp256) == 15.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: 15 of no sensible unit (exit 10)")

claim("ty0613b", D, 613, "Adding/subtracting different units", "rule",
      "Subtracting different units is a compile-time error.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:time = 5.0dim256<Seconds>;
    dim256<Meters>:x = dist - time;
    if ((x => tfp256) == 5.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10)")

claim("ty0614", D, 614, "a bare `tfp256` operand is the", "rule",
      "Multiplying or dividing by a bare tfp256 scales, in either operand order; tfp256 over a unit inverts it.",
      expect="run:0",
      src=main_("""    dim256<Meters>:d = 6.0dim256<Meters>;
    dim256<Meters>:a = d * 2.0tfp256;
    dim256<Meters>:b = 2.0tfp256 * d;
    dim256<Meters>:c = d / 2.0tfp256;
    dim256<Seconds>:t = 4.0dim256<Seconds>;
    dim256<Hertz>:f = 2.0tfp256 / t;
    if ((a => tfp256) != 12.0tfp256) { exit 10i32; }
    if ((b => tfp256) != 12.0tfp256) { exit 11i32; }
    if ((c => tfp256) != 3.0tfp256) { exit 12i32; }
    if ((f => tfp256) != 0.5tfp256) { exit 13i32; }
    exit 0i32;"""),
      wrong="an operand order refused (the scaling special-cased), or a wrong value (10-13)")

claim("ty0616", D, 616, "Comparing different units", "rule",
      "Comparing different units is a compile-time error.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:time = 5.0dim256<Seconds>;
    if (dist < time) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a raw compare across units (exit 10 or 11)")

claim("ty0616b", D, 616, "same vector: full ordering", "rule",
      "Values of the same vector have the full ordering.",
      expect="run:0",
      src=main_("""    dim256<Meters>:a = 2.0dim256<Meters>;
    dim256<Meters>:b = 3.0dim256<Meters>;
    if (!(a < b)) { exit 10i32; }
    if (!(a <= b)) { exit 11i32; }
    if (a > b) { exit 12i32; }
    if (a >= b) { exit 13i32; }
    if (a == b) { exit 14i32; }
    if (!(a != b)) { exit 15i32; }
    if ((a <=> b) != -1i32) { exit 16i32; }
    exit 0i32;"""),
      wrong="an ordering operator refused, or a wrong answer (10-16)")

claim("ty0618", D, 618, "`dim256<U> => tfp256`: ✅ drops the unit", "rule",
      "`dim256<U> => tfp256` drops the unit, and an ERR rides through it without a trap.",
      expect="run:0",
      src=tfp_main("""    dim256<Meters>:d = 2.0dim256<Meters>;
    dim256<Seconds>:z = raw vtf256(0.0tfp256) =>! dim256<Seconds>;
    dim256<MetersPerSecond>:e = d / z;
    tfp256:t = e => tfp256;
    if (!(is_err(t))) { exit 10i32; }
    if ((d => tfp256) != 2.0tfp256) { exit 11i32; }
    exit 0i32;"""),
      wrong="a trap on the unit drop (TbbErr 110: the leaving trap applied), or ERR lost (10), or the value changed (11)")

claim("ty0621", D, 621, "`tfp256 =>! dim256<U>`: the acknowledged unit ASSERTION", "rule",
      "`tfp256 =>! dim256<U>` asserts a unit and keeps the value.",
      expect="run:0",
      src=tfp_main("""    dim256<Newtons>:f = raw vtf256(3.0tfp256) =>! dim256<Newtons>;
    if ((f => tfp256) != 3.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or the value changed (10)")

claim("ty0622", D, 622, "refuses — a silent unit-gain is how unit bugs are born", "rule",
      "Without `=>!`, `tfp256 => dim256<U>` is refused.",
      expect="refuse",
      src=tfp_main("""    dim256<Newtons>:f = raw vtf256(3.0tfp256) => dim256<Newtons>;
    if ((f => tfp256) == 3.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a silent unit gain (exit 10)")

claim("ty0624", D, 624, "`dim256<U> => dim256<V>`", "rule",
      "`dim256<U> => dim256<V>` is impossible: refused.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:t = dist => dim256<Seconds>;
    if ((t => tfp256) == 10.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: a relabel in one step (exit 10)")

claim("ty0624b", D, 624, "❌ CAST_IMPOSSIBLE", "rule",
      "A unit relabel is impossible under `=>!` too: `dim256<U> =>! dim256<V>` is refused.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:t = dist =>! dim256<Seconds>;
    if ((t => tfp256) == 10.0tfp256) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10)")

claim("ty0624c", D, 624, "`dim256<U>` ⇄ anything else", "rule",
      "A dim256 casts to nothing but tfp256: `dim256<U> =>! int64` is refused.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    int64:k = dist =>! int64;
    if (k == 10i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted (exit 10)")

claim("ty0625", D, 625, "a relabel is spelled as its two honest halves", "rule",
      "A relabel is `=> tfp256` then `=>! dim256<V>`, keeping the value.",
      expect="run:0",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    dim256<Seconds>:t = (dist => tfp256) =>! dim256<Seconds>;
    if ((t => tfp256) != 10.0tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or the value changed (10)")

claim("ty0627", D, 627, "a dimensioned value has no `ToString` BY DESIGN", "rule",
      "A dimensioned value has no ToString: interpolating one is refused.",
      expect="refuse",
      src=main_("""    dim256<Meters>:dist = 10.0dim256<Meters>;
    string:s = `&{ dist }`;
    if (string_byte_length(s) > 0i64) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: the unit silently dropped in rendering (exit 10)")

claim("ty0628", D, 628, "drops are explicit: `&{x => tfp256}`", "rule",
      "Rendering a dimensioned value is the explicit drop `&{x => tfp256}`.",
      expect="run:0",
      src=main_("""    dim256<Meters>:x = 10.0dim256<Meters>;
    string:s = `&{ x => tfp256 }`;
    if (string_byte_length(s) == 0i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or an empty rendering (10)")

claim("ty0631", D, 631, "```nitpick", "example",
      "A function declared to return `dim256<Meters>` that passes `d / t` (Meters*Seconds^-1) is a type error.",
      expect="refuse",
      src=main_("    exit 0i32;", """func:velocity = dim256<Meters>(dim256<Meters>:d, dim256<Seconds>:t) {
    pass(d / t);    // Type error: d/t is Meters*Seconds^-1, not Meters
                    // Must declare return as dim256<MetersPerSecond> or bare tfp256
};"""),
      wrong="accepted: the unit mismatch at `pass` unseen",
      note="the block's closing `}` gets the `;` a function body needs")

claim("ty0634", D, 634, "Must declare return as dim256<MetersPerSecond>", "rule",
      "Declared to return dim256<MetersPerSecond>, the same body compiles and computes d / t.",
      expect="run:0",
      src=main_("""    dim256<MetersPerSecond>:v = raw velocity(10.0dim256<Meters>, 4.0dim256<Seconds>);
    if ((v => tfp256) != 2.5tfp256) { exit 10i32; }
    exit 0i32;""", """func:velocity = dim256<MetersPerSecond>(dim256<Meters>:d, dim256<Seconds>:t) never fails {
    pass(d / t);
};"""),
      wrong="refused, or a wrong value (10)")

claim("ty0634b", D, 634, "or bare tfp256", "rule",
      "Declared to return bare tfp256, the same body `pass(d / t)` compiles.",
      expect="run:0",
      src=main_("""    tfp256:v = raw velocity(10.0dim256<Meters>, 4.0dim256<Seconds>);
    if (v != 2.5tfp256) { exit 10i32; }
    exit 0i32;""", """func:velocity = tfp256(dim256<Meters>:d, dim256<Seconds>:t) never fails {
    pass(d / t);
};"""),
      wrong="refused: the unit drop at `pass` must be explicit (`=> tfp256`), as line 628 says drops are",
      note="contradicts line 628 ('drops are explicit') unless 'bare tfp256' means with an explicit `=> tfp256`")

claim("ty0639", D, 639, "```nitpick", "example",
      "A struct may hold dim256 fields of different units; they read and compose.",
      expect="run:0",
      src=main_("""    PhysicsBody:b = PhysicsBody{ position: 1.5dim256<Meters>, velocity: 2.0dim256<MetersPerSecond>, mass: 80.0dim256<Kilograms> };
    dim256<Meters>:moved = b.velocity * 0.5dim256<Seconds>;
    if ((moved => tfp256) != 1.0tfp256) { exit 10i32; }
    if ((b.mass => tfp256) != 80.0tfp256) { exit 11i32; }
    if ((b.position => tfp256) != 1.5tfp256) { exit 12i32; }
    exit 0i32;""", """pub struct:PhysicsBody = {
    dim256<Meters>:position;
    dim256<MetersPerSecond>:velocity;
    dim256<Kilograms>:mass;
};"""),
      wrong="refused, or a field wrong (10-12)")

claim("ty0648", D, 648, "```llvm", "example",
      "At the IR, dim256<Joules> is tfp256, whose type is `{ i64, i64, i64, i64 }`.",
      expect=r"ir:^%\"?tfp256\"? = type \{ ?i64, i64, i64, i64 ?\}|" + sig("m11dj", "", r"\{ ?i64, i64, i64, i64 ?\} "),
      src=main_("""    dim256<Joules>:j = raw m11dj(5.0dim256<Joules>);
    if ((j => tfp256) != 5.0tfp256) { exit 10i32; }
    exit 0i32;""", "func:m11dj = dim256<Joules>(dim256<Joules>:x) never fails { pass x; };"),
      wrong="the native i256 carrier (row 494, D-195): the block's word struct being stale",
      note="contradicts row 494 ('`tfp256` | `i256` ... native carrier (D-195; the word-struct rows were pre-D-011)')")

claim("ty0654", D, 654, "The dimensional annotation is attached to the AST type node", "rule",
      "The annotation lives on the AST type node; the type checker verifies the algebra and codegen ignores it.",
      untestable="[internal] the AST's type node is not observable; codegen's ignoring the unit is ty0593's IR test")
