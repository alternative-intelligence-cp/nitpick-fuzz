"""M11 claims: OP_REFERENCE.md (lines 1-403) at HUNT2 (9126350), extracted by session 8.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). Where an M10 item tests exactly the claim, the claim
links it (`m10=`) and takes M10's expectation. Values meant to be computed at run time
go through the identity helpers (`raw v32(..)`), so the folder cannot decide them.
Precedence rows are tested by an expression whose two readings give different values.
"""
from m11lib import *

covers("OP", 1)

D = "OP"


def chk(expr_true, code=10):
    """a line that exits `code` unless the bool `expr_true` holds"""
    return "    if (!(%s)) { exit %di32; }" % (expr_true, code)


# ================================================================== the header
claim("op0005", D, 5, "Operator overloading is strictly forbidden", "rule",
      "Operator overloading is forbidden: an impl of an operator for a user struct is refused.",
      expect="refuse",
      src=main_("""    V:a = V{ x: 1i32 };
    V:b = V{ x: 2i32 };
    V:c = a + b;
    exit 0i32;""", "struct:V = { int32:x; };"),
      wrong="accepted: `+` on a user struct")

# ================================================================== 0. precedence (the table at 13)
claim("op0015", D, 15, "| 1 | Postfix |", "row",
      "Postfix binds tightest: `-a[1]` is -(a[1]), and `~a[0]` is ~(a[0]).",
      expect="run:0",
      src=main_("""    int32[2]:a = [raw v32(1i32), raw v32(4i32)];
    int32:y = -a[1i64];
%s
    int32:z = ~a[0i64];
%s
    exit 0i32;""" % (chk("y == -4i32", 10), chk("z == -2i32", 11))),
      wrong="refused, or 10/11")
claim("op0016", D, 16, "| **2** | **Result unary** *(right-assoc)* |", "row",
      "The Result unary operators are looser than postfix and tighter than cast: `raw f(x) => int64` "
      "casts the unwrapped value.",
      expect="run:0",
      src=main_("""    int64:y = raw twice(raw v32(21i32)) => int64;
%s
    exit 0i32;""" % chk("y == 42i64"), "func:twice = int32(int32:a) never fails { pass a * 2i32; };"),
      wrong="refused: the cast applied to the Result")
claim("op0017", D, 17, "| 3 | Pipeline |", "row",
      "The pipeline operators sit at level 3: `x |> f()` passes x as f's first argument.",
      expect="run:0",
      src=main_("""    int32:y = raw (raw v32(21i32) |> twice());
%s
    exit 0i32;""" % chk("y == 42i32"), "func:twice = int32(int32:a) never fails { pass a * 2i32; };"),
      wrong="refused (no pipeline operator)")
claim("op0018", D, 18, "| 4 | Cast | `=>` `=>!` |", "row",
      "Cast binds tighter than unary negation.",
      m10="x01_cast_binds_tighter_than_negation")
claim("op0019", D, 19, "| 5 | Unary |", "row",
      "Unary binds tighter than multiplicative: `~a * b` is (~a) * b.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(1i32);
    int32:b = raw v32(2i32);
    int32:y = ~a * b;
%s
    exit 0i32;""" % chk("y == -4i32")),
      wrong="10: read as ~(a * b), -3")
claim("op0020", D, 20, "| 6 | Multiplicative |", "row",
      "Multiplicative binds tighter than additive: 2 + 3 * 4 is 14.",
      expect="run:0",
      src=main_("""    int32:y = raw v32(2i32) + raw v32(3i32) * raw v32(4i32);
%s
    exit 0i32;""" % chk("y == 14i32")),
      wrong="10: 20")
claim("op0021", D, 21, "| 7 | Additive |", "row",
      "Additive binds tighter than shift.",
      m10="x02_additive_before_shift")
claim("op0022", D, 22, "| 8 | Shift |", "row",
      "Shift binds tighter than relational: `1 << 2 < 5` is (1 << 2) < 5.",
      expect="run:0",
      src=main_("""    bool:r = raw v32(1i32) << 2i32 < 5i32;
%s
    exit 0i32;""" % chk("r")),
      wrong="refused (read as 1 << (2 < 5)), or 10")
claim("op0023", D, 23, "| 9 | Range / Spread |", "row",
      "Range binds looser than additive: `0...1 + 2` is 0...3, three iterations.",
      expect="run:0",
      src=main_("""    int64:n = 0i64;
    int64:one = raw v64(1i64);
    for (int64:i in 0i64...one + 2i64) { n = n + 1i64; discard(i); }
%s
    exit 0i32;""" % chk("n == 3i64")),
      wrong="refused or 10")
claim("op0024", D, 24, "| 10 | Relational |", "row",
      "Relational binds tighter than equality: `a < b == c < d` is (a < b) == (c < d).",
      expect="run:0",
      src=main_("""    int32:a = raw v32(1i32);
    bool:r = a < 2i32 == 3i32 < 4i32;
%s
    exit 0i32;""" % chk("r")),
      wrong="refused or 10")
claim("op0025", D, 25, "| 11 | Equality |", "row",
      "Equality binds tighter than bitwise AND.",
      m10="x03_equality_before_bitand")
claim("op0026", D, 26, "| 12 | Bitwise AND |", "row",
      "AND binds tighter than XOR: 1 ^ 3 & 2 is 1 ^ (3 & 2) = 3.",
      expect="run:0",
      src=main_("""    int32:y = raw v32(1i32) ^ raw v32(3i32) & raw v32(2i32);
%s
    exit 0i32;""" % chk("y == 3i32")),
      wrong="10: 2, read as (1 ^ 3) & 2")
claim("op0027", D, 27, "| 13 | Bitwise XOR |", "row",
      "XOR binds tighter than OR: 1 | 3 ^ 3 is 1 | (3 ^ 3) = 1.",
      expect="run:0",
      src=main_("""    int32:y = raw v32(1i32) | raw v32(3i32) ^ raw v32(3i32);
%s
    exit 0i32;""" % chk("y == 1i32")),
      wrong="10: 0, read as (1 | 3) ^ 3")
claim("op0028", D, 28, "| 14 | Bitwise OR |", "row",
      "Bitwise OR binds tighter than logical AND: `false && true | true` is false && (true | true).",
      expect="run:0",
      src=main_("""    bool:r = raw vb(false) && raw vb(true) | raw vb(true);
%s
    exit 0i32;""" % chk("!r")),
      wrong="refused (no `|` on bool), or 10: read as (false && true) | true")
claim("op0029", D, 29, "| 15 | Logical AND | `&&` (short-circuiting) |", "row",
      "AND binds tighter than OR: `true || false && false` is true || (false && false).",
      expect="run:0",
      src=main_("""    bool:r = raw vb(true) || raw vb(false) && raw vb(false);
%s
    exit 0i32;""" % chk("r")),
      wrong="10: read as (true || false) && false")
claim("op0030", D, 30, "| 16 | Logical OR | `\\|\\|` (short-circuiting) |", "row",
      "`||` short-circuits: its right side is not evaluated when the left is true.",
      expect="run:0",
      src=main_("""    int32:z = raw v32(0i32);
    bool:r = raw vb(true) || (10i32 / z == 1i32);
%s
    exit 0i32;""" % chk("r")),
      wrong="97: the right side ran")
claim("op0031", D, 31, "| 17 | Null Coalescing | `??` |", "row",
      "`??` unwraps an Optional: a NIL Optional coalesces to the right side.",
      expect="run:0",
      src=main_("""    int64?:o = NIL;
    int64:v = o ?? 7i64;
%s
    exit 0i32;""" % chk("v == 7i64")),
      wrong="refused (no Optional or no `??`), or 10")
claim("op0032", D, 32, "| 18 | Ternary / Fallback |", "row",
      "`is` is the ternary: `is x > 0 : 1 : -1` picks by the condition.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(-3i32);
    int32:r = is x > 0i32 : 1i32 : -1i32;
%s
    exit 0i32;""" % chk("r == -1i32")),
      wrong="refused, or 10")
claim("op0033", D, 33, "| 19 | Assignment |", "row",
      "The assignment operators `= += -= *= /= %= &= |= ^= <<= >>=` all assign in place.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(6i32);
    x += 4i32;
    x -= 2i32;
    x *= 3i32;
    x /= 4i32;
    x %%= 4i32;
%s
    x = 12i32;
    x &= 10i32;
    x |= 1i32;
    x ^= 3i32;
    x <<= 2i32;
    x >>= 1i32;
%s
    exit 0i32;""" % (chk("x == 2i32", 10), chk("x == 20i32", 11))),
      wrong="refused (an operator missing), or 10/11")
claim("op0037", D, 37, "`raw a.eq(b)` takes the receiver or the call", "rule",
      "Level 2 is looser than postfix: `raw a.eq(b)` unwraps the call, not the receiver.",
      expect="run:0",
      src=main_("""    string:a = string_concat("ab", "c");
    string:b = string_concat("a", "bc");
    bool:r = raw a.eq(b);
%s
    exit 0i32;""" % chk("r")),
      wrong="refused (raw applied to the receiver), or 10")
claim("op0041", D, 41, "`discard` / `_~` is absent because D-060 makes it a statement", "rule",
      "discard is a statement, not an expression: using it as a value is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32:y = discard(x);
    exit 0i32;"""),
      wrong="accepted")
claim("op0046", D, 46, "**`->` removed from level 1.**", "rule",
      "`->` is not member access: `p->x` is refused.",
      expect="refuse",
      src=main_("""    P:q = P{ x: 1i32 };
    P->:p = @q;
    int32:v = p->x;
    exit 0i32;""", "struct:P = { int32:x; };"),
      wrong="accepted")
claim("op0049", D, 49, "**`=>!` added to the Cast level**", "rule",
      "`=>!` shares the cast level, tighter than negation: `-x =>! int8` with x = 128 is -(x =>! int8), "
      "the negation of int8 -128, which traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    int32:x = raw v32(128i32);
    int8:y = -x =>! int8;
    exit 10i32;"""),
      wrong="10: read as (-x) =>! int8, -128 with no trap")
claim("op0051", D, 51, "**`#` removed from the Unary level**", "rule",
      "`#` is not a unary operator: `#x` (the old pin) is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32:y = #x;
    exit 0i32;"""),
      wrong="accepted")

# ------------------------------------------------------------------ 0.1 expression semantics
claim("op0056", D, 56, "**Assignment is a statement, not an expression** (D-060)", "rule",
      "Assignment is a statement: `int32:y = (x = 5i32) + 2i32;` does not parse.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32:y = (x = 5i32) + 2i32;
    exit 0i32;"""),
      wrong="accepted: assignment as an expression")
claim("op0064", D, 64, "`if (x = 3)` needs no dedicated rule rejecting", "rule",
      "`if (x = 3)` is not expressible: it is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if (x = 3i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("op0066", D, 66, "Conditions must still be a strict `bool`", "rule",
      "Conditions are strictly bool: `if (x)` on an int32 is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if (x) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: an integer as a condition")
claim("op0067", D, 67, "**`&&` and `||` short-circuit**", "rule",
      "`&&` and `||` short-circuit.",
      m10="x04_short_circuit")
claim("op0067b", D, 67, "require strictly boolean operands", "rule",
      "`&&` requires boolean operands: `1i32 && 2i32` is refused.",
      expect="refuse",
      src=main_("""    bool:r = raw v32(1i32) && raw v32(2i32);
    exit 0i32;"""),
      wrong="accepted")
claim("op0068", D, 68, "(spaceship) yields `int32`", "rule",
      "`<=>` yields an int32: -1, 0 or 1.",
      m10="m06_spaceship")
claim("op0070", D, 70, "`expr ?| fallback` yields `expr`'s value", "rule",
      "`expr ?| fallback` yields the value, or the fallback if it errored.",
      m10="r01_fallback")
claim("op0073", D, 73, "A bare `?`", "rule",
      "A bare `?` is refused by name, NITPICK-PARSE-011.",
      expect="refuse:PARSE-011",
      src=main_("""    int32:v = f() ? 5i32;
    exit v - 5i32;""", "error:E1;\nfunc:f = int32() { fail E1; };"),
      wrong="accepted, or another code")
claim("op0074b", D, 74, "and the word `defaults` are refused by name", "rule",
      "The word `defaults` is refused by name, NITPICK-PARSE-011.",
      expect="refuse:PARSE-011",
      src=main_("""    int32:v = f() defaults 5i32;
    exit v - 5i32;""", "error:E1;\nfunc:f = int32() { fail E1; };"),
      wrong="accepted, or another code")
claim("op0075", D, 75, "The parser still reads the old form and refuses it by name", "rule",
      "`++` is struck: the parser refuses `x++` by name, NITPICK-PARSE-010.",
      expect="refuse:PARSE-010",
      src=main_("""    int32:x = raw v32(1i32);
    x++;
    exit 0i32;"""),
      wrong="accepted, or another code")
claim("op0075b", D, 75, "`x += 1` / `x -= 1` are the spellings", "rule",
      "`x += 1` and `x -= 1` are the increment's spellings.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    x += 1i32;
    x += 1i32;
    x -= 1i32;
%s
    exit 0i32;""" % chk("x == 2i32")),
      wrong="refused or 10")

# ================================================================== 1. arithmetic (the table at 81)
claim("op0083", D, 83, "| `+` | Add | Safe addition. |", "row",
      "`+` is safe: a plain-integer overflow traps IntOverflow.",
      m10="o01_int32_add")
claim("op0084", D, 84, "| `-` | Subtract | Safe subtraction. |", "row",
      "`-` is safe: an overflow traps IntOverflow.",
      m10="o02_int32_sub")
claim("op0085", D, 85, "| `*` | Multiply | Safe multiplication. |", "row",
      "`*` is safe: an overflow traps IntOverflow.",
      m10="o03_int32_mul")
claim("op0086", D, 86, "| `/` | Divide | Safe division.", "row",
      "Integer `/` by zero traps DivByZero (the plain-integer row of the type-directed rule).",
      m10="v03_div_by_zero")
claim("op0087", D, 87, "| `%` | Modulo | Remainder operation. Same divide-by-zero rule as `/`. |", "row",
      "`%` by zero follows `/`'s rule: it traps DivByZero.",
      m10="v04_rem_by_zero")
claim("op0088", D, 88, "| `**` | Power | Exponentiation (Standard Library expansion). |", "row",
      "`**` is exponentiation: 2 ** 8 is 256.",
      expect="run:0",
      src=main_("""    int32:p = raw v32(2i32) ** raw v32(8i32);
%s
    exit 0i32;""" % chk("p == 256i32")),
      wrong="refused (no `**`), or 10")
claim("op0089", D, 89, "| `+%` | Add, wrapping |", "row",
      "`+%` adds modulo 2^N: the u64 maximum +% 1 is 0, with no trap.",
      expect="run:0",
      src=main_("""    uint64:h = ~raw vu64(0u64);
    uint64:r = h +%% 1u64;
%s
    exit 0i32;""" % chk("r == 0u64")),
      wrong="93 (a trap) or 10")
claim("op0090", D, 90, "| `-%` | Subtract, wrapping | Subtraction modulo 2^N. |", "row",
      "`-%` subtracts modulo 2^N: 0 -% 1 at uint8 is 255.",
      expect="run:0",
      src=main_("""    uint8:h = raw vu8(0u8);
    uint8:r = h -%% 1u8;
%s
    exit 0i32;""" % chk("r == 255u8")),
      wrong="93 or 10")
claim("op0091", D, 91, "| `*%` | Multiply, wrapping |", "row",
      "`*%` multiplies modulo 2^N: 0x80000000 *% 2 at uint32 is 0.",
      expect="run:0",
      src=main_("""    uint32:h = raw vu32(2147483648u32);
    uint32:r = h *%% 2u32;
%s
    exit 0i32;""" % chk("r == 0u32")),
      wrong="93 or 10")
claim("op0102", D, 102, "The kinds that own their own arithmetic refuse it by name", "rule",
      "The kinds that own their arithmetic refuse the wrapping family by name: `+%` on a tbb8 is "
      "TYPE-078.",
      expect="refuse:TYPE-078",
      src=main_("""    tbb8:a = raw vt8(5tbb8);
    tbb8:b = a +% 1tbb8;
    exit 0i32;"""),
      wrong="accepted")
claim("op0106", D, 106, "A constant wrap folds", "rule",
      "A constant wrap folds WITH the wrap.",
      m10="o20_wrapping_folds_with_wrap")

# ------------------------------------------------------------------ 1.1 division and overflow (the table at 119)
claim("op0121", D, 121, "| `tbb8`…`tbb256` | yields **ERR**", "row",
      "On tbb, overflow yields ERR and divide by zero yields ERR, neither a trap.",
      expect="run:0",
      src=main_("""    tbb8:a = raw vt8(127tbb8) + 1tbb8;
%s
    tbb8:z = raw vt8(0tbb8);
    tbb8:q = raw vt8(5tbb8) / z;
%s
    exit 0i32;""" % (chk("is_err(a)", 10), chk("is_err(q)", 11))),
      wrong="a trap, or 10/11: not ERR")
claim("op0122", D, 122, "| `int32`, `uint64`, … | **wraps** — defined, no check, no trap |", "row",
      "Plain integers: the row says they wrap, and the note at line 138 supersedes it: `+ - *` "
      "trap IntOverflow since D-210.",
      expect="trap:IntOverflow",
      src=main_("""    int32:x = raw v32(2147483647i32) + 1i32;
    exit 10i32;"""),
      wrong="10: the wrap the row (not the note) describes",
      note="the row is stale and the reference says so (line 138); the expectation is the note's")
claim("op0122b", D, 122, "**traps to `failsafe`**", "row",
      "Plain-integer divide by zero traps to failsafe.",
      m10="v03_div_by_zero")
claim("op0123", D, 123, "| `flt32`…`flt512` | **IEEE 754** — `inf` / `nan`, no trap |", "row",
      "Floats overflow to infinity, with no trap.",
      expect="run:0",
      src=main_("""    flt64:big = raw vf64(1.0e308f64);
    flt64:r = big * 10.0f64;
%s
    exit 0i32;""" % chk("r > big && r == r * 2.0f64")),
      wrong="a trap, or 10: not infinity")
claim("op0123b", D, 123, "**IEEE 754** — `inf` / `nan` | numeric work |", "row",
      "Float division by zero is IEEE: an infinity, with no trap.",
      m10="v16_float_div_by_zero")
claim("op0144", D, 144, "A `simd` integer lane traps as its", "rule",
      "A simd integer lane traps as its scalar does.",
      m10="o22_simd_lane_overflow")
claim("op0150", D, 150, "An integer `+ - *` or negation whose operands the compiler folds", "rule",
      "A folded constant is computed exactly at its type: a fixed product is its exact value.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("P == 1000000i32"), "fixed int32:P = 1000i32 * 1000i32;"),
      wrong="refused or 10")
claim("op0153", D, 153, "**A value that does not fit is `NITPICK-TYPE-076`**", "rule",
      "A constant that does not fit is NITPICK-TYPE-076 where it is written.",
      m10="o21_constant_overflow_refused")
claim("op0155", D, 155, "`int8:x = 100 + 100;` is refused too", "rule",
      "An unsuffixed constant pair takes its width from the context: `int8:x = 100 + 100;` is refused.",
      m10="c26_constant_overflow_contextual")
claim("op0156", D, 156, "**A value that fits is emitted as the constant**, with no guard", "rule",
      "A constant that fits is emitted as the constant: `-1i32` is no checked `sub` (no overflow "
      "intrinsic in the function that returns it).",
      expect=r'ir:(?s)^define [^@\n]*@"[^"]*\.negone"\((?!(?:(?!\n\}).)*?with\.overflow)',
      src=main_("""    int32:r = raw negone();
    exit r + 1i32;""", "func:negone = int32() never fails { pass -1i32; };"),
      wrong="an ssub.with.overflow in negone: a checked 0 - 1")
claim("op0158", D, 158, "A width past 64 bits folds inside the 64-bit window only", "rule",
      "A width past 64 bits folds inside the 64-bit window only; beyond it the run-time guard stays.",
      untestable="[internal] declining the fold changes no value (the guard computes the same "
                 "product); only the emission differs, and no width past 64 bits is named to scope an "
                 "IR test by")
claim("op0161", D, 161, "`<<` loses the bits past its width (`1i8 << 7i8` is −128)", "rule",
      "The folder shifts as the machine does: `1i8 << 7i8` is -128 and `~5u8` is 250.",
      m10="s03_shifts_folded")
claim("op0163", D, 163, "a `uint64` divides, takes remainders, shifts right and orders UNSIGNED", "rule",
      "The folder divides and takes remainders unsigned for a uint64.",
      m10="v15_unsigned_div_rem_folded")
claim("op0163b", D, 163, "orders UNSIGNED", "rule",
      "The folder orders a uint64 unsigned.",
      m10="m04_unsigned_ordering_folded")
claim("op0164", D, 164, "a constant `MIN / −1` or `MIN % −1` is refused", "rule",
      "A constant MIN / -1 is refused as a constant division by zero is (TYPE-004).",
      m10="v13_constant_min_div_minus_one")
claim("op0166", D, 166, "`uint64` values past 2^63−1 are built with bit operations", "rule",
      "uint64 values past 2^63-1 are built with bit operations: `~0u64` is the maximum and "
      "`(1u64 << 63u64) | 1u64` is 2^63 + 1.",
      expect="run:0",
      src=main_("""    uint64:m = ~0u64;
    uint64:h = (1u64 << 63u64) | 1u64;
%s
%s
%s
    exit 0i32;""" % (chk("m +% 1u64 == 0u64", 10), chk("h > 9223372036854775807u64", 11),
                     chk("h -% 1u64 == 1u64 << 63u64", 12))),
      wrong="refused, or 10-12")
claim("op0169", D, 169, "ERR is **absorbing and overrides identities**", "rule",
      "ERR is absorbing: ERR * 0 is ERR, and ERR - ERR is ERR.",
      expect="run:0",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    tbb8:a = e * 0tbb8;
    tbb8:b = e - e;
%s
%s
    exit 0i32;""" % (chk("is_err(a)", 10), chk("is_err(b)", 11))),
      wrong="10/11: an identity laundered ERR into a number")
claim("op0171", D, 171, "Only an explicit check (`is_err`) or a fallback (`?`) leaves the state", "rule",
      "A fallback leaves the ERR state: an ERR tbb with a fallback yields the fallback.",
      expect="run:0",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    tbb8:v = e ? 3tbb8;
%s
    exit 0i32;""" % chk("!is_err(v)")),
      wrong="refused: a bare `?` is struck (line 74), and `?|` takes a Result only (line 257)")
claim("op0172", D, 172, "*(`ok()` was listed here and is removed — D-097.)*", "rule",
      "`ok()` is removed: calling it is refused.",
      expect="refuse",
      src=main_("""    tbb8:e = raw vt8(5tbb8);
    bool:r = ok(e);
    exit 0i32;"""),
      wrong="accepted")
claim("op0174", D, 174, "**comparing or", "rule",
      "Comparing or branching on an ERR value traps to failsafe.",
      m10="m12_tbb_compare_on_err_traps")
claim("op0177", D, 177, "Use `is_err(x)` to test without trapping, or a `pick` with an explicit", "rule",
      "A pick with an explicit ERR: arm branches on ERR without trapping.",
      m10="p13_tbb_err_arm_taken")
claim("op0177b", D, 177, "Use `is_err(x)` to test without trapping", "rule",
      "`is_err(x)` tests for ERR without trapping.",
      expect="run:0",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    tbb8:g = raw vt8(5tbb8);
%s
%s
    exit 0i32;""" % (chk("is_err(e)", 10), chk("!is_err(g)", 11))),
      wrong="a trap, or 10/11")
claim("op0180", D, 180, "Bitwise operators (`&`, `|`, `^`, `~`, `<<`, `>>`) are **rejected on `tbb` types**", "rule",
      "Bitwise operators are rejected on tbb: `a & b` on tbb8 is refused.",
      expect="refuse",
      src=main_("""    tbb8:a = raw vt8(5tbb8);
    tbb8:b = a & 3tbb8;
    exit 0i32;"""),
      wrong="accepted")
claim("op0182", D, 182, "Cast to a plain integer first — which traps if the", "rule",
      "Casting an ERR tbb to a plain integer traps (TbbErr).",
      expect="trap:TbbErr",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    int32:x = e =>! int32;
    exit 10i32;"""),
      wrong="10: the taint crossed silently")

# ================================================================== 2. assignment (the table at 189)
def asg(line, quote, op, start, v, want, t="int32", text=None):
    sfx = {"int32": "i32", "uint64": "u64", "uint32": "u32"}[t]
    helper = {"int32": "v32", "uint64": "vu64", "uint32": "vu32"}[t]
    claim("op%04d" % line, D, line, quote, "row",
          text or "`%s` assigns in place: %s%s %s %s%s gives %s." % (op, start, sfx, op, v, sfx, want),
          expect="run:0",
          src=main_("""    %s:x = raw %s(%s%s);
    x %s %s%s;
    if (x != %s%s) { exit 10i32; }
    exit 0i32;""" % (t, helper, start, sfx, op, v, sfx, want, sfx)),
          wrong="refused, or 10")


claim("op0191", D, 191, "| `=` | Assign | Standard assignment. |", "row",
      "`=` assigns.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    x = 5i32;
    if (x != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
asg(192, "| `+=` | Add & Assign |", "+=", "7", "5", "12")
asg(193, "| `-=` | Subtract & Assign |", "-=", "7", "5", "2")
asg(194, "| `*=` | Multiply & Assign |", "*=", "7", "5", "35")
asg(195, "| `/=` | Divide & Assign |", "/=", "-7", "2", "-3")
asg(196, "| `%=` | Modulo & Assign |", "%=", "-7", "5", "-2")
asg(197, "| `+%=` | Add wrapping & Assign |", "+%=", "18446744073709551615", "1", "0", t="uint64",
    text="`x +%= v` is `x = x +% v`: the u64 maximum +%= 1 is 0.")
asg(198, "| `-%=` | Subtract wrapping & Assign |", "-%=", "0", "1", "18446744073709551615", t="uint64",
    text="`-%=` subtracts modulo 2^N: 0 -%= 1 at uint64 is the maximum.")
asg(199, "| `*%=` | Multiply wrapping & Assign |", "*%=", "2147483648", "2", "0", t="uint32",
    text="`*%=` multiplies modulo 2^N: 2^31 *%= 2 at uint32 is 0.")

# ================================================================== 3. comparison (the table at 205)
for _ln, _q, _op, _a, _b, _want in (
        (207, "| `==` | Equality |", "==", "3", "3", "true"),
        (208, "| `!=` | Inequality |", "!=", "3", "4", "true"),
        (209, "| `<` | Less Than |", "<", "-5", "3", "true"),
        (210, "| `>` | Greater Than |", ">", "3", "-5", "true"),
        (211, "| `<=` | Less Than or Equal |", "<=", "3", "3", "true"),
        (212, "| `>=` | Greater Than or Equal|", ">=", "-5", "3", "false")):
    claim("op%04d" % _ln, D, _ln, _q, "row",
          "`%s` compares: %s %s %s is %s." % (_op, _a, _op, _b, _want),
          expect="run:0",
          src=main_("""    bool:r = raw v32(%si32) %s raw v32(%si32);
    if (r != %s) { exit 10i32; }
    exit 0i32;""" % (_a, _op, _b, _want)),
          wrong="refused, or 10")
claim("op0213", D, 213, "| `<=>` | Spaceship | 3-way comparison. Returns `-1`, `0`, or `1`. |", "row",
      "`<=>` returns -1, 0 or 1.",
      m10="m06_spaceship")

# ================================================================== 4. logical and bitwise (the table at 219)
for _ln, _q, _expr, _want, _t in (
        (221, "| `!` | Logical NOT |", "!raw vb(false)", "true", "bool"),
        (222, "| `&&` | Logical AND |", "raw vb(true) && raw vb(false)", "false", "bool"),
        (223, "| `\\|\\|` | Logical OR |", "raw vb(false) || raw vb(true)", "true", "bool"),
        (224, "| `~` | Bitwise NOT |", "~raw v32(5i32)", "-6i32", "int32"),
        (225, "| `&` | Bitwise AND |", "raw v32(12i32) & raw v32(10i32)", "8i32", "int32"),
        (226, "| `\\|` | Bitwise OR |", "raw v32(12i32) | raw v32(3i32)", "15i32", "int32"),
        (227, "| `^` | Bitwise XOR |", "raw v32(12i32) ^ raw v32(10i32)", "6i32", "int32")):
    claim("op%04d" % _ln, D, _ln, _q, "row",
          "%s is %s." % (_expr.replace("raw vb(", "").replace("raw v32(", "").replace(")", ""), _want),
          expect="run:0",
          src=main_("""    %s:r = %s;
    if (r != %s) { exit 10i32; }
    exit 0i32;""" % (_t, _expr, _want)),
          wrong="refused, or 10")
claim("op0228", D, 228, "| `<<` | Left Shift | Shifts bits left. | `a << 2` |", "row",
      "`<<` shifts left: `a << 2` with a = 3 is 12 (the example's unsuffixed amount).",
      expect="run:0",
      src=main_("""    int32:a = raw v32(3i32);
    int32:r = a << 2;
    if (r != 12i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (an unsuffixed literal), or 10")
claim("op0229", D, 229, "Shifts bits right (arithmetic/logical based on sign)", "row",
      "`>>` is arithmetic on a signed operand and logical on an unsigned one: -8 >> 1 is -4, and "
      "0xF0u8 >> 4 is 15.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(-8i32) >> 1i32;
    uint8:b = raw vu8(240u8) >> 4u8;
    if (a != -4i32) { exit 10i32; }
    if (b != 15u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: a logical shift of a signed value; 11")
claim("op0232", D, 232, "literal, a negated", "rule",
      "A known shift amount outside 0 <= n < width is NITPICK-TYPE-070 at the shift.",
      m10="s07_shift_literal_amount_refused")
claim("op0234", D, 234, "shift, both operators and the compound spellings", "rule",
      "The amount check covers the compound spellings.",
      m10="s08_compound_shift_amount")
claim("op0235", D, 235, "amount is checked at run time by one unsigned compare", "rule",
      "A computed amount outside the range traps ShiftRange.",
      m10="s04_shift_amount_equals_width")
claim("op0236", D, 236, "negative amount reads as huge", "rule",
      "A negative computed amount reads as huge and traps ShiftRange.",
      m10="s05_shift_amount_negative")
claim("op0237", D, 237, "every `failsafe`", "rule",
      "Wherever a computed shift exists, every failsafe must name ShiftRange: one that does not is refused.",
      expect="refuse", fs=False,
      src=main_("""    int32:n = raw v32(1i32);
    int32:r = raw v32(1i32) << n;
    exit r - 2i32;""") + "func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(
          "        (%s) { exit %di32; }," % t for t in TRAPS if t[0] != "ShiftRange") +
      "\n        (*) { exit 99i32; }\n    }\n    exit 9i32;\n};\n",
      wrong="accepted")
claim("op0242", D, 242, "The value of an in-range shift is unchanged", "rule",
      "An in-range shift is a bit operation with no overflow trap.",
      m10="o18_shift_loses_bits_no_trap")
claim("op0243", D, 243, "A `simd` shift's amount is a", "rule",
      "A simd shift's amount is checked any-lane: one lane's amount equal to the width traps ShiftRange.",
      expect="trap:ShiftRange",
      src=main_("""    simd<int32, 4>:a = simd(raw v32(1i32), 1i32, 1i32, 1i32);
    simd<int32, 4>:n = simd(raw v32(1i32), 1i32, 1i32, raw v32(32i32));
    simd<int32, 4>:r = a << n;
    exit 10i32;"""),
      wrong="10: the out-of-range lane went through")

# ================================================================== 5. Result and safety (the table at 251)
claim("op0253", D, 253, "| `?\\|` | Result Fallback |", "row",
      "`?|` unwraps a Result: on an error it yields the default.",
      m10="r01_fallback")
claim("op0254", D, 254, "| `??` | Null Coalesce |", "row",
      "`??` unwraps an Optional: a present value comes through.",
      expect="run:0",
      src=main_("""    int64?:o = raw v64(4i64);
    int64:v = o ?? 0i64;
    if (v != 4i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no Optional or no `??`), or 10")
claim("op0255", D, 255, "**Takes exactly one argument**, an `Error` constant", "row",
      "`?!` calls failsafe with its one argument, an Error constant.",
      m10="r04_emphatic_unwrap_error")
claim("op0257", D, 257, "take a `Result` and nothing else", "rule",
      "`?|` takes a Result and nothing else: on a tbb value it is refused.",
      expect="refuse",
      src=main_("""    tbb8:e = raw vt8(5tbb8);
    tbb8:v = e ?| 0tbb8;
    exit 0i32;"""),
      wrong="accepted: a tbb fallback")
claim("op0258", D, 258, "| `?.` | Safe Navigation |", "rule",
      "`?.` reaches a field through an Optional, and the result is an Optional of the field's type.",
      expect="run:0",
      src=main_("""    P?:o = NIL;
    int32?:f = o?.x;
    int32:v = f ?? 9i32;
    if (v != 9i32) { exit 10i32; }
    exit 0i32;""", "struct:P = { int32:x; };"),
      wrong="refused (no Optional or no `?.`), or 10")
claim("op0259", D, 259, "Refused by name. | — |", "rule",
      "A bare `?` is refused by name.",
      expect="refuse:PARSE-011",
      src=main_("""    int32:v = f() ? 1i32;
    exit v - 1i32;""", "error:E1;\nfunc:f = int32() { fail E1; };"),
      wrong="accepted")
claim("op0260", D, 260, "Desugars to `drop expr`", "rule",
      "`_? f();` is `drop f();`, the void call of a never-fails NIL function.",
      expect="run:0",
      src=main_("""    _? note();
    exit 0i32;""", "func:note = NIL() never fails { pass NIL; };"),
      wrong="refused: no `_?` spelling")
claim("op0260b", D, 260, "refused otherwise, `TYPE-042`", "rule",
      "`drop` of a callee that may fail is refused, TYPE-042.",
      m10="r05_drop_of_fallible_refused")
claim("op0261", D, 261, "Desugars to `raw expr`", "rule",
      "`_! f()` is `raw f()`: it unwraps a never-fails call's value.",
      expect="run:0",
      src=main_("""    int32:v = _! seven();
    if (v != 7i32) { exit 10i32; }
    exit 0i32;""", "func:seven = int32() never fails { pass 7i32; };"),
      wrong="refused, or 10")
claim("op0262", D, 262, "**propagates the error to the caller, verbatim**", "rule",
      "`_^ f()` is `relay f()`: it propagates the callee's error verbatim.",
      expect="run:0",
      src=main_("""    Result<int32>:r = outer();
    if (!r.is_error) { exit 10i32; }
    if (r.err != E2) { exit 11i32; }
    exit 0i32;""", """error:E1;
error:E2;
func:inner = int32() { fail E2; };
func:outer = int32() {
    int32:v = _^ inner();
    pass v;
};"""),
      wrong="refused (no `_^`), 10, or 11 (another error)")
claim("op0262b", D, 262, "`defer` runs — it is a normal exit path", "rule",
      "relay's early return is a normal exit: its defers run.",
      m10="w07_defer_on_relay")
claim("op0262c", D, 262, "Illegal in `main` / `failsafe`", "rule",
      "relay is illegal in main: it is refused.",
      expect="refuse",
      src=main_("""    int32:v = relay f();
    exit v;""", "error:E1;\nfunc:f = int32() { fail E1; };"),
      wrong="accepted")
claim("op0263", D, 263, "As a statement it desugars to `discard(expr)`", "rule",
      "`_~ x;` is the statement `discard(x)`.",
      expect="run:0",
      src=main_("""    int32:unused = raw v32(1i32);
    _~ unused;
    exit 0i32;"""),
      wrong="refused: no `_~` statement")
claim("op0263b", D, 263, "reading it anyway is an error, not a warning", "rule",
      "A parameter marked `_~` that the body reads is an error.",
      expect="refuse",
      src=main_("""    int32:r = raw f(raw v32(1i32));
    exit r;""", "func:f = int32(int32:_~x) never fails { pass x; };"),
      wrong="accepted")
claim("op0264", D, 264, "Immediately invokes `failsafe(err)`", "rule",
      "`!!! E1;` invokes failsafe with E1 through the trap route.",
      expect="run:81",
      src=main_("""    !!! E1;
    exit 10i32;""", "error:E1;"),
      wrong="10, or another arm")
claim("op0268", D, 268, "Neither takes a pointer.**", "rule",
      "`??` takes an Optional, never a pointer: `p ?? 0i32` on an int32-> is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32->:p = @x;
    int32:v = p ?? 0i32;
    exit 0i32;"""),
      wrong="accepted: a pointer dereferenced by `??`")
claim("op0280", D, 280, "`p == NULL` asks whether a pointer points anywhere", "rule",
      "`p == NULL` asks whether a pointer points anywhere: an address of a local is not NULL.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    int32->:p = @x;
    if (p == NULL) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no NULL), or 10")
claim("op0287", D, 287, "| **leading** | negation | `!x`, `!=` |", "row",
      "A leading `!` negates: `!x` and `!=`.",
      expect="run:0",
      src=main_("""    bool:b = raw vb(false);
    if (!(!b)) { exit 10i32; }
    if (!(raw v32(1i32) != 2i32)) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused or 10/11")
claim("op0288", D, 288, "| **trailing or repeated** | unchecked / emphatic |", "row",
      "A trailing or repeated `!` is unchecked or emphatic: `?!`, `=>!`, `_!` and `!!!` all compile.",
      expect="run:0",
      src=main_("""    int32:a = ok() ?! E1;
    int8:b = raw v32(300i32) =>! int8;
    int32:c = _! seven();
    if (a + c != 14i32) { exit 10i32; }
    if (b != 44i8) { exit 11i32; }
    if (a == 0i32) { !!! E1; }
    exit 0i32;""", """error:E1;
func:ok = int32() { pass 7i32; };
func:seven = int32() never fails { pass 7i32; };"""),
      wrong="refused (a form missing), or 10/11")
claim("op0295", D, 295, "**`!!` no longer exists**", "rule",
      "`!!` no longer exists: it is refused.",
      expect="refuse",
      src=main_("""    bool:b = raw vb(true);
    bool:c = !!b;
    exit 0i32;"""),
      wrong="accepted")

# ================================================================== 6. pointers (the table at 308)
claim("op0303", D, 303, "C-style `*` pointer", "rule",
      "C-style `*` pointer syntax is valid nowhere: `int32*:p` is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32*:p = @x;
    exit 0i32;"""),
      wrong="accepted")
claim("op0310", D, 310, "| `@` | Address-Of |", "row",
      "`@` takes an l-value's address: `int32->:ptr = @val;`.",
      expect="run:0",
      src=main_("""    int32:val = raw v32(5i32);
    int32->:ptr = @val;
    if (<-ptr != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0311", D, 311, "| `$$i` | Shared claim |", "row",
      "`$$i` is the address of a place under a shared claim: `int32->:p = $$i x;` reads it.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(5i32);
    int32->:p = $$i x;
    if (<-p != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0312", D, 312, "| `$$m` | Exclusive claim |", "row",
      "`$$m` is the address of a place under an exclusive claim: `int32->:p = $$m arr[i];` writes it.",
      expect="run:0",
      src=main_("""    int32[2]:arr = [1i32, 2i32];
    int64:i = raw v64(1i64);
    {
        int32->:p = $$m arr[i];
        <-p = 9i32;
    }
    if (arr[1i64] != 9i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0313", D, 313, "| `<-` | Dereference |", "row",
      "`<-` extracts the value from a pointer.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(6i32);
    int32->:ptr = @x;
    int32:val = <-ptr;
    if (val != 6i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0314", D, 314, "| `->` | Pointer To | In types: pointer declaration ONLY. |", "row",
      "`->` declares a pointer type.",
      expect="run:0",
      src=main_("""    int64:x = raw v64(2i64);
    int64->:p = @x;
    if (<-p != 2i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0315", D, 315, "| `.` | Member Access |", "row",
      "`.` handles all member access, dereferencing a pointer, and UFCS: `x.twice()` calls twice(x).",
      expect="run:0",
      src=main_("""    P:q = P{ n: 3i32 };
    P->:p = @q;
    if (p.n != 3i32) { exit 10i32; }
    int32:x = raw v32(4i32);
    if (raw x.twice() != 8i32) { exit 11i32; }
    exit 0i32;""", "struct:P = { int32:n; };\nfunc:twice = int32(int32:a) never fails { pass a * 2i32; };"),
      wrong="refused, or 10/11")
claim("op0320", D, 320, "anywhere else is", "rule",
      "A claim stands only as a whole call argument or a pointer local's whole value; anywhere else "
      "is NITPICK-BORROW-014.",
      expect="refuse:BORROW-014",
      src=main_("""    int32:x = raw v32(1i32);
    int32:y = <-($$i x) + 1i32;
    exit y - 2i32;"""),
      wrong="accepted, or another code")
claim("op0336", D, 336, "**compiler-directive sigil**", "rule",
      "`#` is the compiler-directive sigil: `#name<T>(...)` calls a builtin.",
      expect="run:0",
      src=main_("""    if (#size_of<int64>() != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0339", D, 339, "**Direction is semantic.**", "rule",
      "`->` points to, `<-` brings back, `=>` goes from one type to another.",
      untestable="[vague] a mnemonic for the operators claimed at op0313, op0314 and op0351")

# ================================================================== 7. casting (the table at 349)
claim("op0351", D, 351, "| `=>` | Safe Cast |", "row",
      "`=>` is a compile-time error where data loss is possible.",
      m10="c03_narrow_signed_refused")
claim("op0352", D, 352, "| `=>!` | Unchecked Cast |", "row",
      "`=>!` is a direct bit-cast or truncation without checking.",
      m10="c13_unchecked_cast_truncates_bits")
claim("op0356", D, 356, "Every `tbb` cast checks for the sentinel and", "rule",
      "Every tbb cast maps ERR to the target's ERR: a tbb8 ERR widened to tbb32 is ERR, not -128.",
      expect="run:0",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    tbb32:w = e => tbb32;
    if (!is_err(w)) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: a valid tbb32 -128 (a straight sign extension)")
claim("op0358", D, 358, "plain-integer→`tbb` traps on a source value that would forge one", "rule",
      "A plain integer that would forge the sentinel traps on its way into tbb (TbbErr).",
      expect="trap:TbbErr",
      src=main_("""    int8:x = raw v8(-128i8);
    tbb8:t = x => tbb8;
    exit 10i32;"""),
      wrong="10: ERR forged from a valid integer")
claim("op0358b", D, 358, "`=>!`", "rule",
      "`=>!` preserves the ERR state, not the bit pattern: a tbb8 ERR =>! tbb32 is ERR.",
      expect="run:0",
      src=main_("""    tbb8:e = raw vt8(127tbb8) + 1tbb8;
    tbb32:w = e =>! tbb32;
    if (!is_err(w)) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: the taint laundered")
claim("op0362", D, 362, "**Integer→pointer casting is illegal.**", "rule",
      "Integer to pointer casting is illegal outside `#wild_ptr`: `x => int32->` is refused.",
      expect="refuse",
      src=main_("""    int64:x = raw v64(4096i64);
    int32->:p = x => int32->;
    exit 0i32;"""),
      wrong="accepted")
claim("op0364", D, 364, "| `:` | Type Annotation |", "rule",
      "`:` annotates a declaration's type.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    if (x != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0365", D, 365, "the only form there (D-064). Bare `<T>` is type-position only", "rule",
      "Bare `<T>` is type-position only: `list_init<int64>(4i64)` in an expression is refused (the "
      "turbofish is the form).",
      expect="refuse",
      src=main_("""    List<int64>:l = raw list_init<int64>(4i64);
    exit 0i32;"""),
      wrong="accepted")
claim("op0365b", D, 365, "| `::<T>` | Turbofish |", "rule",
      "`::<T>` gives explicit type arguments in expression position.",
      expect="run:0",
      src=main_("""    List<int64>:l = raw list_init::<int64>(4i64);
    if (l.cap != 4i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0366", D, 366, "| `<T>?` | Optional Type |", "rule",
      "`T?` declares an Optional: an `int64?` holds a value or NIL.",
      expect="run:0",
      src=main_("""    int64?:o = raw v64(3i64);
    int64?:n = NIL;
    if ((o ?? 0i64) != 3i64) { exit 10i32; }
    if ((n ?? 5i64) != 5i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (no Optional type), or 10/11")

# ================================================================== 8. control flow and pipelines (the table at 372)
claim("op0374", D, 374, "| `is` | Ternary Conditional |", "row",
      "`is cond : then : else` branches: `is x > 0 : 1 : -1` with x = 5 is 1.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(5i32);
    int32:r = is x > 0i32 : 1i32 : -1i32;
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0375", D, 375, "| `..` | Inclusive Range |", "row",
      "`..` is the inclusive range [a, b].",
      m10="l01_for_inclusive")
claim("op0376", D, 376, "| `...` | Exclusive Range |", "row",
      "`...` is the exclusive range [a, b).",
      m10="l02_for_exclusive")
claim("op0377", D, 377, "| `\\|>` | Pipe Forward |", "row",
      "`val |> func()` passes val as func's first argument: 10 |> minus(3) is 7.",
      expect="run:0",
      src=main_("""    int32:y = raw (raw v32(10i32) |> minus(3i32));
    if (y != 7i32) { exit 10i32; }
    exit 0i32;""", "func:minus = int32(int32:a, int32:b) never fails { pass a - b; };"),
      wrong="refused, or 10 (-7: the value passed second)")
claim("op0378", D, 378, "| `<\\|` | Pipe Backward |", "row",
      "`func() <| val` evaluates val and passes it to func.",
      expect="run:0",
      src=main_("""    int32:y = raw (twice() <| raw v32(21i32));
    if (y != 42i32) { exit 10i32; }
    exit 0i32;""", "func:twice = int32(int32:a) never fails { pass a * 2i32; };"),
      wrong="refused, or 10")
claim("op0379", D, 379, "| `$` | Iteration Variable|", "row",
      "`$` is the loop counter bound inside `loop` and `till`: summing $ over loop(0, 3, 1) gives 3.",
      expect="run:0",
      src=main_("""    int64:x = 0i64;
    loop (0i64, 3i64, 1i64) { x += $; }
    if (x != 3i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")

# ================================================================== 9. literals (the table at 385)
claim("op0387", D, 387, "| `\"\"` | String Literal |", "row",
      "A string literal is UTF-8: \"é\" is two bytes.",
      expect="run:0",
      src=main_("""    string:s = "é";
    if (string_byte_length(s) != 2i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0388", D, 388, "| `r\"\"` | Raw String Literal|", "row",
      "A raw string has no escape processing: r\"C:\\Path\" is 7 bytes, the third a backslash.",
      expect="run:0",
      src=main_(r"""    string:s = r"C:\Path";
    if (string_byte_length(s) != 7i64) { exit 10i32; }
    if (string_bytes(s)[2i64] != 92u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (no raw strings), or 10/11")
claim("op0389", D, 389, "| `\"\"\" \"\"\"`| Triple Quote |", "row",
      "A triple-quoted literal spans lines and keeps the newline.",
      expect="run:0",
      src=main_('''    string:s = """a
b""";
    if (string_byte_length(s) != 3i64) { exit 10i32; }
    if (string_bytes(s)[1i64] != 10u8) { exit 11i32; }
    exit 0i32;'''),
      wrong="refused, or 10/11")
claim("op0390", D, 390, "| `''` | Char Literal |", "row",
      "`'A'` is a char literal of 65.",
      expect="run:0",
      src=main_("""    char8:c = 'A';
    if (c != 65char8) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0391", D, 391, "| Template Literal |", "row",
      "A backtick template with nothing interpolated is its text: `Hello` equals \"Hello\".",
      expect="run:0",
      src=main_("""    string:t = `Hello`;
    if (!(string_equals(t, "Hello"))) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0392", D, 392, "| `&{ }` | Interpolation |", "row",
      "`&{ }` interpolates an expression's value inside a template.",
      m10="t11_template_interpolation")
claim("op0393", D, 393, "| Escape | Escape sequence character. |", "row",
      "`\\n` is the newline byte and `\\t` the tab.",
      expect="run:0",
      src=main_(r"""    string:s = "a\nb\tc";
    if (string_bytes(s)[1i64] != 10u8) { exit 10i32; }
    if (string_bytes(s)[3i64] != 9u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")

# ================================================================== 10. comments (the table at 399)
claim("op0401", D, 401, "| `//` | Line Comment |", "row",
      "`//` comments out the rest of the line.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32); // exit 10i32;
    if (x != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("op0402", D, 402, "| `/*` | Block Start |", "row",
      "`/*` begins a block comment that spans lines.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    /* exit 10i32;
       exit 11i32; */
    if (x != 1i32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused (no block comments), or 10-12")
claim("op0403", D, 403, "| `*/` | Block End |", "row",
      "`*/` ends a block comment: code after it on the same line runs.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    /* a comment */ x = 2i32;
    if (x != 2i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
