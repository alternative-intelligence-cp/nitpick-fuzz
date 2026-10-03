"""M11 claims: TYPE_REFERENCE.md lines 1593-2122 at HUNT2 (sections 19 to 28).

Dimensional types, frac, complex, the removed `binary`, `buffer`, the library tier,
`fixed`, the special values (NIL, NULL, void, any, unknown) and the operator reference.
Part C of TYPE 661-2122 (S65). Every expectation below is written from the reference's
TEXT, before any program ran.
"""
from m11lib import *
from m11_tyhelp import *
from m11_tyhelp import _fn, _body

covers("TYPE", 1593, 2122)

D = "TYPE"

ERRS = "error:E1;\nerror:E2;"
K = ERRS + "\nfunc:m11k = int32(int32:x) {\n    if (x == 1i32) { fail E2; }\n    pass 5i32;\n};"
NT_ARMS = "        (ntensor.BadShape) { exit 80i32; },\n        (ntensor.BadIndex) { exit 81i32; },"


def frac_of(n, d, w="32"):
    """a frac`w` n/d, built by division from the lossless entry"""
    return "((raw v%s(%di%s) => frac%s) / (%di%s => frac%s))" % (w, n, w, w, d, w, w)


# ================================================================== 19. dimensional types
claim("ty1595", D, 1595, "Dimensional analysis types carry unit metadata at compile time only.", "rule",
      "A dimensional value is its base numeric type at run time: a `dim256<Meters>` parameter and a "
      "`tfp256` one have the same IR type.",
      expect=r'ir:(?s)\A(?=.*?@"?(?:[\w$]+\.)*m11d"?\(([^ ,)]+))(?=.*?@"?(?:[\w$]+\.)*m11t"?\(\1[ ,)])',
      src=prog_("""    dim256<Meters>:d = raw m11d(1.5dim256<Meters>);
    tfp256:t = raw m11t(1.5tfp256);
    if ((d => tfp256) != t) { exit 10i32; }
    exit 0i32;""", """func:m11d = dim256<Meters>(dim256<Meters>:x) never fails { pass x; };
func:m11t = tfp256(tfp256:x) never fails { pass x; };"""),
      wrong="a unit carried at run time: another IR type")
claim("ty1598", D, 1598, "```nitpick", "example",
      "D-036 rejected value-generic units on plain integers: `int32<Meters>` is refused.", expect="refuse",
      src=prog_("""    int32<Meters>:x = raw v32(5i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1606", D, 1606, "`Joules`, `Meters`, `Seconds`, `Newtons`, `Kelvin`", "rule",
      "`Joules`, `Meters`, `Seconds`, `Newtons` and `Kelvin` are units a `dim256` takes.",
      expect="run:0",
      src=prog_("""    dim256<Joules>:e = 1.0dim256<Joules>;
    dim256<Meters>:m = 2.0dim256<Meters>;
    dim256<Seconds>:s = 3.0dim256<Seconds>;
    dim256<Newtons>:f = 4.0dim256<Newtons>;
    dim256<Kelvin>:k = 5.0dim256<Kelvin>;
    if ((e => tfp256) != 1.0tfp256) { exit 10i32; }
    if ((m => tfp256) != 2.0tfp256) { exit 11i32; }
    if ((s => tfp256) != 3.0tfp256) { exit 12i32; }
    if ((f => tfp256) != 4.0tfp256) { exit 13i32; }
    if ((k => tfp256) != 5.0tfp256) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused (a unit unknown), or 10-14")
claim("ty1607", D, 1607, "Arithmetic across dimensions is validated at compile time", "rule",
      "Arithmetic across dimensions composes units: Meters / Seconds binds to `dim256<Meters/Seconds>`.",
      expect="run:0",
      src=prog_("""    dim256<Meters>:m = 10.0dim256<Meters>;
    dim256<Seconds>:s = 4.0dim256<Seconds>;
    dim256<Meters/Seconds>:v = m / s;
    if ((v => tfp256) != 2.5tfp256) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")

# ================================================================== 20. frac
for ln, t, w, size in ((1619, "frac8", "8", 3), (1620, "frac16", "16", 6), (1621, "frac32", "32", 12),
                       (1622, "frac64", "64", 24)):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` holds a whole int%s, a numerator int%s and a denominator uint%s: %d bytes." % (t, w, w, w, size),
          expect="run:0",
          src=prog_("""    %s:a = %s;
    int%s:wh = a.whole;
    int%s:nu = a.num;
    uint%s:de = a.denom;
    if (wh != 0i%s) { exit 10i32; }
    if (nu != 1i%s) { exit 11i32; }
    if (de != 3u%s) { exit 12i32; }
    if (#size_of<%s>() != %di64) { exit 13i32; }
    exit 0i32;""" % (t, frac_of(1, 3, w), w, w, w, w, w, w, t, size)),
          wrong="refused (a member's type), or 10-12: 1/3 misread; 13: another size")
claim("ty1624", D, 1624, "```llvm", "example",
      "`frac32` is `{ i32, i32, i32 }`: a frac32 parameter has that type.",
      expect=ir_all(param("m11f", r"\{ ?i32, i32, i32 ?\}")),
      src=prog_("""    frac32:a = raw m11f(raw v32(5i32) => frac32);
    if (a.whole != 5i32) { exit 10i32; }
    exit 0i32;""", "func:m11f = frac32(frac32:x) never fails { pass x; };"),
      wrong="another layout")
claim("ty1631", D, 1631, "is AUTOMATIC after every operation, never a call", "rule",
      "Normalization is automatic: 1/2 + 1/3 is 5/6, and 2/4 equals 1/2 with denominator 2.",
      expect="run:0",
      src=prog_("""    frac32:a = %s + %s;
    if (a.num != 5i32) { exit 10i32; }
    if (a.denom != 6u32) { exit 11i32; }
    frac32:b = %s;
    if (b.num != 1i32) { exit 12i32; }
    if (b.denom != 2u32) { exit 13i32; }
    exit 0i32;""" % (frac_of(1, 2), frac_of(1, 3), frac_of(2, 4))),
      wrong="10-13: an unreduced form")
claim("ty1633", D, 1633, "**Operators are `+ - * /` and the comparisons, exactly** — no `%`, no", "rule",
      "`%` on frac is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    frac32:b = a %% a;
    exit 0i32;""" % frac_of(1, 3)),
      wrong="accepted")
claim("ty1634", D, 1634, "bitwise. Same-width only.", "rule",
      "Bitwise `&` on frac is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    frac32:b = a & a;
    exit 0i32;""" % frac_of(1, 3)),
      wrong="accepted")
claim("ty1634b", D, 1634, "bitwise. Same-width only.", "rule",
      "frac operators are same-width only: `frac32 + frac64` is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    frac64:b = %s;
    frac64:c = (a => frac64) + b;
    frac64:d = a + b;
    exit 0i32;""" % (frac_of(1, 3), frac_of(1, 3, "64"))),
      wrong="accepted")
claim("ty1634c", D, 1634, "Negation is unary `-` (through the same core).", "rule",
      "Unary `-` negates a frac: -(1/3) has numerator -1.",
      expect="run:0",
      src=prog_("""    frac32:a = %s;
    frac32:n = -a;
    if (n.whole != 0i32) { exit 10i32; }
    if (n.num != -1i32) { exit 11i32; }
    exit 0i32;""" % frac_of(1, 3)),
      wrong="refused, or 10/11")
claim("ty1635", D, 1635, "**The five invariants hold after every operation**", "rule",
      "The invariants hold: -(2 5/8) is whole -3 and num 3 over 8 (num >= 0 when whole != 0, the sign on "
      "whole), and 1/2 - 5/6 is whole 0, num -1, denom 3 (the sign on num).",
      expect="run:0",
      src=prog_("""    frac32:two58 = (raw v32(2i32) => frac32) + %s;
    frac32:n = -two58;
    if (n.whole != -3i32) { exit 10i32; }
    if (n.num != 3i32) { exit 11i32; }
    if (n.denom != 8u32) { exit 12i32; }
    frac32:d = %s - %s;
    if (d.whole != 0i32) { exit 13i32; }
    if (d.num != -1i32) { exit 14i32; }
    if (d.denom != 3u32) { exit 15i32; }
    exit 0i32;""" % (frac_of(5, 8), frac_of(1, 2), frac_of(5, 6))),
      wrong="10-15: an invariant broken")
claim("ty1637", D, 1637, "\"Call `frac_simplify` yourself\" was a latent-ERR", "rule",
      "`frac_simplify` is gone: calling it is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    frac32:b = raw frac_simplify(a);
    exit 0i32;""" % frac_of(2, 4)),
      wrong="accepted")
claim("ty1639", D, 1639, "is `{minN, minN, 0}` canonically, and `is_err` answers the", "rule",
      "A frac's ERR is `{min, min, 0}`, and `is_err` is true for it.",
      expect="run:0",
      src=prog_("""    frac32:e = ERR;
%s
    if (e.denom != 0u32) { exit 11i32; }
    exit 0i32;""" % chk("is_err(e)", 10)),
      wrong="10/11")
claim("ty1642", D, 1642, "division by an exact zero yields ERR", "rule",
      "frac division by an exact zero yields ERR, and ERR is sticky.",
      expect="run:0",
      src=prog_("""    frac32:a = raw v32(5i32) => frac32;
    frac32:z = raw v32(0i32) => frac32;
    frac32:q = a / z;
%s
%s
    exit 0i32;""" % (chk("is_err(q)", 10), chk("is_err(q + a)", 11))),
      wrong="a trap, or 10/11")
claim("ty1643", D, 1643, "operand at a comparison traps (", "rule",
      "A tainted frac at a comparison traps (-4100, TbbErr).", expect="trap:TbbErr",
      src=prog_("""    frac32:e = ERR;
    frac32:a = raw v32(5i32) => frac32;
    if (e < a) { exit 10i32; }
    exit 11i32;"""),
      wrong="ERR ordered as a number (10, 11)")
claim("ty1644", D, 1644, "reduced form that still exceeds the width — is ERR", "rule",
      "A result whose reduced form exceeds the width is ERR: frac8 100 + 100.",
      expect="run:0",
      src=prog_("""    frac8:a = raw v8(100i8) => frac8;
    frac8:s = a + a;
%s
    exit 0i32;""" % chk("is_err(s)", 10)),
      wrong="a trap, or 10: rounded or wrapped")
claim("ty1646", D, 1646, "`int => frac` is the lossless entry", "rule",
      "`int => frac` is the lossless entry: 7 is `{7, 0, 1}`.",
      expect="run:0",
      src=prog_("""    frac32:a = raw v32(7i32) => frac32;
    if (a.whole != 7i32) { exit 10i32; }
    if (a.num != 0i32) { exit 11i32; }
    if (a.denom != 1u32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
claim("ty1646b", D, 1646, "**No literals**", "rule",
      "There are no frac literals: `5frac32` is refused.", expect="refuse",
      src=prog_("""    frac32:a = 5frac32;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1647", D, 1647, "No `pick` selectors", "rule",
      "There are no frac pick selectors: a pick on a frac is refused.", expect="refuse",
      src=prog_("""    frac32:a = raw v32(1i32) => frac32;
    int32:r = 0i32;
    pick (a) { ERR: { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 2i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1649", D, 1649, "**Members `.whole` / `.num` / `.denom`** are read-only component views", "rule",
      "The members are not places: assigning `.num` is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    a.num = 2i32;
    exit 0i32;""" % frac_of(1, 3)),
      wrong="accepted: an invariant broken through a member")
claim("ty1651", D, 1651, "**Casts**: widths widen `=>`, narrow `=>!`", "rule",
      "A frac widens with `=>` and narrows with `=>!`, keeping the value.",
      expect="run:0",
      src=prog_("""    frac32:a = %s;
    frac64:w = a => frac64;
    if (w.num != 1i64) { exit 10i32; }
    frac8:n = a =>! frac8;
    if (n.num != 1i8) { exit 11i32; }
    exit 0i32;""" % frac_of(1, 3)),
      wrong="refused, or 10/11")
claim("ty1651b", D, 1651, "**Casts**: widths widen `=>`, narrow `=>!`", "rule",
      "Narrowing a frac with `=>` is refused.", expect="refuse",
      src=prog_("""    frac32:a = %s;
    frac8:n = a => frac8;
    exit 0i32;""" % frac_of(1, 3)),
      wrong="accepted")
claim("ty1652", D, 1652, "reduced form does not fit)", "rule",
      "Narrowing a frac whose reduced form does not fit absorbs as ERR: 200 1/3 =>! frac8.",
      expect="run:0",
      src=prog_("""    frac32:a = (raw v32(200i32) => frac32) + %s;
    frac8:n = a =>! frac8;
%s
    exit 0i32;""" % (frac_of(1, 3), chk("is_err(n)", 10))),
      wrong="a trap, or 10")
claim("ty1652b", D, 1652, "`frac =>! flt64` rounds", "rule",
      "`frac =>! flt64` rounds: 1/3 is about 0.3333.",
      expect="run:0",
      src=prog_("""    flt64:f = %s =>! flt64;
    if (!(f > 0.3333f64)) { exit 10i32; }
    if (!(f < 0.3334f64)) { exit 11i32; }
    exit 0i32;""" % frac_of(1, 3)),
      wrong="refused, or 10/11")
claim("ty1653", D, 1653, "implied a checked conversion,", "rule",
      "A checked `frac => flt64` is refused: the conversion rounds, so it takes the bang.", expect="refuse",
      src=prog_("""    flt64:f = %s => flt64;
    exit 0i32;""" % frac_of(1, 3)),
      wrong="accepted")
claim("ty1654", D, 1654, "`frac =>! intN` truncates toward zero", "rule",
      "`frac =>! intN` truncates toward zero: -(2 5/8) is -2, not -3.",
      expect="run:0",
      src=prog_("""    frac32:two58 = (raw v32(2i32) => frac32) + %s;
    frac32:n = -two58;
    int32:t = n =>! int32;
    if (t != -2i32) { exit 10i32; }
    exit 0i32;""" % frac_of(5, 8)),
      wrong="10: floored (-3, the canonical whole)")
claim("ty1655", D, 1655, "traps under BOTH spellings on any exit", "rule",
      "An ERR frac leaving the family traps TbbErr (`=>!` to flt64).", expect="trap:TbbErr",
      src=prog_("""    frac32:e = ERR;
    flt64:f = e =>! flt64;
    if (f == 0.0f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="the sentinel converted (10, 11)")
claim("ty1655b", D, 1655, "a float never enters", "rule",
      "A float never enters frac: `flt64 =>! frac32` is refused.", expect="refuse",
      src=prog_("""    frac32:a = raw vf64(0.5f64) =>! frac32;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1656", D, 1656, "other twisted families are reached through the plain integer", "rule",
      "Another twisted family is reached through the plain integer: tbb32 => frac32 is refused, "
      "(tbb32 => int32) => frac32 converts.",
      expect="refuse",
      src=prog_("""    tbb32:t = raw vt32(5tbb32);
    frac32:a = t => frac32;
    exit 0i32;"""),
      wrong="accepted: a cross-family cast")
claim("ty1657", D, 1657, "**`ToString`**: \"whole num/denom\"", "rule",
      "ToString renders \"3 1/3\", \"-2 5/8\", \"0\" and \"ERR\".",
      expect="run:0",
      src=prog_("""    frac32:a = (raw v32(3i32) => frac32) + %s;
    string:s = `&{ a }`;
%s
    frac32:two58 = (raw v32(2i32) => frac32) + %s;
    frac32:n = -two58;
    string:t = `&{ n }`;
%s
    frac32:z = raw v32(0i32) => frac32;
    string:u = `&{ z }`;
%s
    frac32:e = ERR;
    string:w = `&{ e }`;
%s
    exit 0i32;""" % (frac_of(1, 3), chk('string_equals(s, "3 1/3")', 10), frac_of(5, 8),
                     chk('string_equals(t, "-2 5/8")', 11), chk('string_equals(u, "0")', 12),
                     chk('string_equals(w, "ERR")', 13))),
      wrong="11: the canonical parts rendered (\"-3 3/8\"); 10/12/13: another rendering")
claim("ty1658", D, 1658, "**The implementation is the PRELUDE's** (1.3.5)", "rule",
      "frac arithmetic is the prelude's: a frac32 addition calls a prelude function.",
      expect=ir_fn("m11fa", r"call [^\n]*frac"),
      src=prog_("""    frac32:s = raw m11fa(%s, %s);
    if (s.num != 5i32) { exit 10i32; }
    exit 0i32;""" % (frac_of(1, 2), frac_of(1, 3)),
                "func:m11fa = frac32(frac32:a, frac32:b) never fails { pass (a + b); };"),
      wrong="arithmetic inline, no call")

# ================================================================== 21. complex
claim("ty1669", D, 1669, "```nitpick", "example",
      "`complex<flt64>:z = complex(3.0flt64, 4.0flt64);` is 3 + 4i.",
      expect="run:0",
      src=prog_("""    complex<flt64>:z = complex(3.0flt64, 4.0flt64);
    if (z.re() != 3.0f64) { exit 10i32; }
    if (z.im() != 4.0f64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (the literal's suffix), or 10/11")
claim("ty1673", D, 1673, "```llvm", "example",
      "`complex<flt64>` is `{ double, double }`: a parameter has that type.",
      expect=ir_all(param("m11c", r"\{ ?double, double ?\}")),
      src=prog_("""    complex<flt64>:z = raw m11c(complex(raw vf64(3.0f64), 4.0f64));
    if (z.re() != 3.0f64) { exit 10i32; }
    exit 0i32;""", "func:m11c = complex<flt64>(complex<flt64>:x) never fails { pass x; };"),
      wrong="another layout")
claim("ty1681", D, 1681, "`T` ∈ {`flt32`, `flt64`, `tfp32`, `tfp64`} exactly, gated at resolution", "rule",
      "`complex<int32>` is refused.", expect="refuse",
      src=prog_("""    complex<int32>:z = complex(raw v32(1i32), 2i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1681b", D, 1681, "`T` ∈ {`flt32`, `flt64`, `tfp32`, `tfp64`} exactly, gated at resolution", "rule",
      "`complex<flt32>` and `complex<tfp32>` are accepted.",
      expect="run:0",
      src=prog_("""    complex<flt32>:a = complex(raw vf32(1.5f32), 2.0f32);
    complex<tfp32>:b = complex(1.5tfp32, 2.0tfp32);
    if (a.re() != 1.5f32) { exit 10i32; }
    if (b.im() != 2.0tfp32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1683", D, 1683, "slot (the `simd(…)` shape); there are no literals and NO CASTS in either", "rule",
      "There are no casts out of complex: `complex<flt64> =>! complex<flt32>` is refused.", expect="refuse",
      src=prog_("""    complex<flt64>:z = complex(raw vf64(3.0f64), 4.0f64);
    complex<flt32>:w = z =>! complex<flt32>;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1683b", D, 1683, "slot (the `simd(…)` shape); there are no literals and NO CASTS in either", "rule",
      "There are no casts into complex: `flt64 => complex<flt64>` is refused.", expect="refuse",
      src=prog_("""    complex<flt64>:z = raw vf64(3.0f64) => complex<flt64>;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1685", D, 1685, "**Operators `+ - * /`, same-type only.**", "rule",
      "complex operators are same-type only: `complex<flt64> + complex<flt32>` is refused.", expect="refuse",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(1.0f64), 1.0f64);
    complex<flt32>:b = complex(raw vf32(1.0f32), 1.0f32);
    complex<flt64>:c = a + b;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1686", D, 1686, "the naive formula's denominator", "rule",
      "Float complex division is Smith's: 1 / (1e200 + 1e200i) is finite (about 5e-201), where the naive "
      "formula overflows.",
      expect="run:0",
      src=prog_("""    complex<flt64>:hug = complex(raw vf64(1.0e200f64), 1.0e200f64);
    complex<flt64>:one = complex(raw vf64(1.0f64), 0.0f64);
    complex<flt64>:t = one / hug;
    if (!(t.re() > 4.9e-201f64)) { exit 10i32; }
    if (!(t.re() < 5.1e-201f64)) { exit 11i32; }
    exit 0i32;"""),
      wrong="10/11: the naive formula's 0 or NaN")
claim("ty1688", D, 1688, "flt32 (no double-rounding through a wider width)", "rule",
      "flt32 complex arithmetic computes in flt32, with no double rounding.",
      untestable="[unobservable] no input is given whose flt32 result differs under double rounding")
claim("ty1690", D, 1690, "component ERR canonicalizes to BOTH components ERR after every operation", "rule",
      "On tfp elements, one ERR component makes both components ERR after an operation.",
      expect="run:0",
      src=prog_("""    tfp32:e = ERR;
    complex<tfp32>:a = complex(e, 1.0tfp32);
    complex<tfp32>:b = complex(1.0tfp32, 1.0tfp32);
    complex<tfp32>:c = a + b;
    tfp32:im = c.im();
%s
    exit 0i32;""" % chk("is_err(im)", 10)),
      wrong="10: the imaginary component left a number")
claim("ty1691", D, 1691, "**No order**", "rule",
      "complex has no order: `<` is refused.", expect="refuse",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(1.0f64), 1.0f64);
    if (a < a) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1692", D, 1692, "`==`/`!=` are per-component, IEEE on floats", "rule",
      "complex `==`/`!=` are per-component IEEE: a NaN component makes `==` false and `!=` true.",
      expect="run:0",
      src=prog_("""    flt64:nan = raw vf64(0.0f64) / raw vf64(0.0f64);
    complex<flt64>:a = complex(nan, 1.0f64);
    if (a == a) { exit 10i32; }
    if (!(a != a)) { exit 11i32; }
    complex<flt64>:b = complex(raw vf64(2.0f64), 1.0f64);
    if (!(b == b)) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
claim("ty1693", D, 1693, "taint-trapping on tfp (D-008 §5)", "rule",
      "complex `==` on a tfp element ERR traps TbbErr.", expect="trap:TbbErr",
      src=prog_("""    tfp32:e = ERR;
    complex<tfp32>:a = complex(e, 1.0tfp32);
    complex<tfp32>:b = complex(1.0tfp32, 1.0tfp32);
    if (a == b) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap (10, 11)")
claim("ty1693b", D, 1693, "No `pick`", "rule",
      "There are no complex pick selectors.", expect="refuse",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(1.0f64), 1.0f64);
    int32:r = 0i32;
    pick (a) { (*) { r = 1i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1694", D, 1694, "`is_err` reads the pair disjunction on tfp elements", "rule",
      "`is_err` on a tfp complex is the disjunction of its components.",
      expect="run:0",
      src=prog_("""    tfp32:e = ERR;
    complex<tfp32>:a = complex(1.0tfp32, e);
    complex<tfp32>:b = complex(1.0tfp32, 2.0tfp32);
%s
%s
    exit 0i32;""" % (chk("is_err(a)", 10), chk("!(is_err(b))", 11))),
      wrong="refused, or 10/11")
claim("ty1695", D, 1695, "refuses on float elements (a float carries NaN, not ERR)", "rule",
      "`is_err` on a float complex is refused.", expect="refuse",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(1.0f64), 1.0f64);
    if (is_err(a)) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1696", D, 1696, "**Methods**: `.re()` `.im()` `.conj()` `.abs2()` on every element type", "rule",
      "`.re() .im() .conj() .abs2()` work on flt64 and tfp32 elements, and `.abs()` on flt64.",
      expect="run:0",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(3.0f64), 4.0f64);
    complex<flt64>:c = a.conj();
    if (c.im() != -4.0f64) { exit 10i32; }
    if (a.abs2() != 25.0f64) { exit 11i32; }
    if (a.abs() != 5.0f64) { exit 12i32; }
    complex<tfp32>:t = complex(3.0tfp32, 4.0tfp32);
    complex<tfp32>:u = t.conj();
    if (u.re() != 3.0tfp32) { exit 13i32; }
    if (t.abs2() != 25.0tfp32) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused, or 10-14")
claim("ty1697", D, 1697, "`.abs()` on FLOAT elements only", "rule",
      "`.abs()` on a tfp complex is refused.", expect="refuse",
      src=prog_("""    complex<tfp32>:t = complex(3.0tfp32, 4.0tfp32);
    tfp32:m = t.abs();
    exit 0i32;"""),
      wrong="accepted")
claim("ty1700", D, 1700, "**`ToString`**: \"3+4i\" / \"3-4i\"", "rule",
      "ToString renders \"3+4i\" and \"3-4i\", and a tfp ERR pair \"ERR\".",
      expect="run:0",
      src=prog_("""    complex<flt64>:a = complex(raw vf64(3.0f64), 4.0f64);
    string:s = `&{ a }`;
%s
    complex<flt64>:b = complex(raw vf64(3.0f64), -4.0f64);
    string:t = `&{ b }`;
%s
    tfp32:e = ERR;
    complex<tfp32>:c = complex(e, e);
    string:u = `&{ c }`;
%s
    exit 0i32;""" % (chk('string_equals(s, "3+4i")', 10), chk('string_equals(t, "3-4i")', 11),
                     chk('string_equals(u, "ERR")', 12))),
      wrong="refused, or 10-12: another rendering")
claim("ty1702", D, 1702, "**The arithmetic is the PRELUDE'S**, per element type", "rule",
      "complex arithmetic is the prelude's, in Nitpick.",
      untestable="[internal] where a body lives; Smith's result is tested (ty1686)")

# ------------------------------------------------------------------ the memory note, 22. binary
claim("ty1710", D, 1710, "there is no `buffer_free`", "rule",
      "There is no `buffer_free`: calling it is refused.", expect="refuse",
      src=prog_("""    buffer:b = buffer_new(raw v64(16i64));
    buffer_free(b);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1721", D, 1721, "Redundant twice over. `binary` and its seven `binary_*` operations are removed;", "rule",
      "`binary` is removed: a `binary` parameter is refused.", expect="refuse",
      src=prog_("    exit 0i32;", "func:m11b = int64(binary:_~b) never fails { pass 0i64; };"),
      wrong="accepted")
claim("ty1719", D, 1719, "property, so an immutable byte view is `fixed uint8[]`", "rule",
      "An immutable byte view is `fixed uint8[]`: it binds and reads.",
      expect="run:0",
      src=prog_("""    uint8[4]:arr = [1u8, 2u8, 3u8, 4u8];
    fixed uint8[]:v = arr[0i64...4i64];
    if (v[raw v64(2i64)] != 3u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1719b", D, 1719, "property, so an immutable byte view is `fixed uint8[]`", "rule",
      "A `fixed uint8[]` is immutable: writing an element through it is refused.", expect="refuse",
      src=prog_("""    uint8[4]:arr = [1u8, 2u8, 3u8, 4u8];
    fixed uint8[]:v = arr[0i64...4i64];
    v[0i64] = 9u8;
    exit 0i32;"""),
      wrong="accepted: a write through the immutable view")
claim("ty1726", D, 1726, "keyword that was never defined. D-074 returns it to userland along with", "rule",
      "`stream`, `process`, `pipe`, `debug` and `log` are not keywords: locals of those names compile.",
      expect="run:0",
      src=prog_("""    int32:stream = raw v32(1i32);
    int32:process = 2i32;
    int32:pipe = 3i32;
    int32:debug = 4i32;
    int32:log = 5i32;
    if (stream + process + pipe + debug + log != 15i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: a name still reserved")

# ================================================================== 23. buffer
claim("ty1739", D, 1739, "```llvm", "example",
      "A buffer is `{ ptr, i64, i64 }`: 24 bytes, alignment 8.",
      expect="run:0", src=layout(["buffer"], 24, 8), wrong=layout_wrong("buffer", 24, 8))
claim("ty1742", D, 1742, "%buffer = type { ptr, i64, i64 }", "rule",
      "A buffer parameter is `{ ptr, i64, i64 }`.",
      expect=ir_all(param("m11b", r"\{ ?ptr, i64, i64 ?\}")),
      src=prog_("    exit 0i32;", "func:m11b = int64(buffer:b) never fails { pass b.len; };"),
      wrong="another layout")
claim("ty1745", D, 1745, "```nitpick", "example",
      "The buffer example runs: 42 written as an int32 through `#ptr_add`, read back, and its low byte read "
      "through the ptr.",
      expect="run:0",
      src=prog_("""    buffer:buf = buffer_new(1024i64);          // 1024 zeroed bytes, len == cap
    <-(#ptr_add<int32>(buf.ptr, 0i64)) = 42i32; // a typed write, the general way
    int32:back = <-(#ptr_add<int32>(buf.ptr, 0i64));
    uint8:b0 = buf.ptr[0i64];                  // byte reads index the ptr
    if (back != 42i32) { exit 10i32; }
    if (b0 != 42u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1754", D, 1754, "`buffer_new(n)` — `int64 → buffer`, **never fails**", "rule",
      "`buffer_new(n)` gives n zeroed bytes with len == cap == n, and `.ptr` is a `uint8->`.",
      expect="run:0",
      src=prog_("""    buffer:b = buffer_new(raw v64(16i64));
    if (b.len != 16i64) { exit 10i32; }
    if (b.cap != 16i64) { exit 11i32; }
    uint8->:p = b.ptr;
    if (p[raw v64(5i64)] != 0u8) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
claim("ty1755", D, 1755, "`n <= 0` is the EMPTY non-owning buffer", "rule",
      "`buffer_new(n)` for n <= 0 is the empty buffer: a null ptr and cap 0.",
      expect="run:0",
      src=prog_("""    buffer:b = buffer_new(raw v64(-5i64));
    if (b.cap != 0i64) { exit 10i32; }
    if (b.len != 0i64) { exit 11i32; }
    if (b.ptr != NULL) { exit 12i32; }
    exit 0i32;"""),
      wrong="a trap, or 10-12")
claim("ty1756", D, 1756, "Allocation failure traps", "rule",
      "A buffer_new the allocator cannot meet traps (2^50 bytes).",
      expect="run:42", fs=False,
      src=any_trap("""    buffer:b = buffer_new(raw v64(1125899906842624i64));
    if (b.len == 0i64) { exit 11i32; }"""),
      wrong="no trap: an empty buffer (11) or a huge one (10)", note=ANY)
claim("ty1757", D, 1757, "The count is `int64` by declaration", "rule",
      "buffer_new's count is int64 by declaration: an int32 count is refused.", expect="refuse",
      src=prog_("""    buffer:b = buffer_new(raw v32(16i32));
    exit 0i32;"""),
      wrong="accepted: an implicit widening")
claim("ty1762", D, 1762, "a buffer is move-only", "rule",
      "A buffer is move-only: copying one is TYPE-046.", expect="refuse:NITPICK-TYPE-046",
      src=prog_("""    buffer:a = buffer_new(raw v64(8i64));
    buffer:b = a;
    if (b.len != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: two owners")
claim("ty1763", D, 1763, "rides a channel whole under the send's `move`", "rule",
      "A buffer rides a channel whole under the send's `move`.",
      untestable="[tool] needs the concurrency runtime's spawn and channel; CONCURRENCY's claims test sends")
claim("ty1767", D, 1767, "`==` refuses as the string's does (D-169)", "rule",
      "`==` on buffers is refused.", expect="refuse",
      src=prog_("""    buffer:a = buffer_new(raw v64(8i64));
    buffer:b = buffer_new(raw v64(8i64));
    if (a == b) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: the addresses compared")
for ln, q, name, call in ((1771, "the per-width `buffer_write_i8/…/read_i64` verb family", "buffer_write_i8",
                           "buffer_write_i8(@b, 0i64, 1i8)"),
                          (1772, "`buffer_free` (the managed drop IS the free", "buffer_free", "buffer_free(b)"),
                          (1773, "`buffer_resize`", "buffer_resize", "buffer_resize(@b, 32i64)"),
                          (1773, "`buffer_bytes` (a borrow", "buffer_bytes", "buffer_bytes(@b)")):
    cid = "ty%04d" % ln + ("b" if name == "buffer_bytes" else "")
    claim(cid, D, ln, q, "rule",
          "`%s` was not landed: calling it is refused." % name, expect="refuse",
          src=prog_("""    buffer:b = buffer_new(raw v64(16i64));
    discard(raw %s);
    exit 0i32;""" % call),
          wrong="accepted")

# ================================================================== 25. the library tier
claim("ty1780", D, 1780, "None of these are compiler types.", "rule",
      "vec2 is not a compiler type: without the library, `vec2` as a type is refused.", expect="refuse",
      src=prog_("""    S0:s = S0{ n: 1i32 };
    exit 0i32;""", "struct:S0 = { vec2:v; int32:n; };"),
      wrong="accepted: a built-in vec2")
claim("ty1786", D, 1786, "Structs of one `simd<flt64, N>` field, with constructor FUNCTIONS", "rule",
      "vec3 is built by `vec3_of`, and its methods are lane reads, `.dot`, `.length2`, `.length` and `.cross`.",
      expect="sh:0",
      sh=lib_run(["nvec"], """    vec3:a = raw vec3_of(raw vf64(1.0f64), 2.0f64, 2.0f64);
    vec3:b = raw vec3_of(3.0f64, 0.0f64, 4.0f64);
    if ((raw a.x()) != 1.0f64) { exit 10i32; }
    if ((raw a.z()) != 2.0f64) { exit 11i32; }
    if ((raw a.dot(b)) != 11.0f64) { exit 12i32; }
    if ((raw a.length2()) != 9.0f64) { exit 13i32; }
    if ((raw a.length()) != 3.0f64) { exit 14i32; }
    vec3:c = raw a.cross(b);
    if ((raw c.x()) != 8.0f64) { exit 15i32; }
    if ((raw c.y()) != 2.0f64) { exit 16i32; }
    if ((raw c.z()) != -6.0f64) { exit 17i32; }
    exit 0i32;"""),
      wrong="refused, or 10-17")
claim("ty1792", D, 1792, "`.cross(o)` on `vec3` alone", "rule",
      "`.cross` is on vec3 alone: `vec2.cross` is refused.",
      expect="sh:0",
      sh=lib_refused(["nvec"], """    vec2:a = raw vec2_of(raw vf64(1.0f64), 2.0f64);
    vec2:c = raw a.cross(a);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1797", D, 1797, "```nitpick", "example",
      "vec9 has the nine named fields `m00` … `m22`, and `vec9_id()` is the identity.",
      expect="sh:0",
      sh=lib_run(["nvec"], """    vec9:m = raw vec9_id();
    if (m.m00 != 1.0f64) { exit 10i32; }
    if (m.m11 != 1.0f64) { exit 11i32; }
    if (m.m22 != 1.0f64) { exit 12i32; }
    if (m.m01 != 0.0f64) { exit 13i32; }
    if (m.m21 != 0.0f64) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused, or 10-14")
claim("ty1805", D, 1805, "`mRC` = row R, col C", "rule",
      "`mRC` is row R, column C, and `.mul` is the 3x3 product: (I + 2·e01)(I + 3·e10) has m00 = 7.",
      expect="sh:0",
      sh=lib_run(["nvec"], """    vec9:a = vec9{ m00: raw vf64(1.0f64), m01: 2.0f64, m02: 0.0f64, m10: 0.0f64, m11: 1.0f64, m12: 0.0f64, m20: 0.0f64, m21: 0.0f64, m22: 1.0f64 };
    vec9:b = vec9{ m00: raw vf64(1.0f64), m01: 0.0f64, m02: 0.0f64, m10: 3.0f64, m11: 1.0f64, m12: 0.0f64, m20: 0.0f64, m21: 0.0f64, m22: 1.0f64 };
    vec9:p = raw a.mul(b);
    if (p.m00 != 7.0f64) { exit 10i32; }
    if (p.m01 != 2.0f64) { exit 11i32; }
    if (p.m10 != 3.0f64) { exit 12i32; }
    exit 0i32;"""),
      wrong="10-12: a column-major product")
claim("ty1811", D, 1811, "`matrix<T>` is `{ buffer:cells; int64:rows; int64:cols; }`", "rule",
      "`matrix<T>` is a buffer and two int64s: 40 bytes.",
      expect="sh:0",
      sh=lib_run(["ntensor"], """    if (#size_of<S0>() != 40i64) { exit 10i32; }
    exit 0i32;""", "struct:S0 = { matrix<int64>:v; };", arms=NT_ARMS),
      wrong="10: another layout")
claim("ty1812", D, 1812, "`mat_of::<T>(rows, cols)` (zeroed birth) and bounds-checked `.get(r, c)` /", "rule",
      "`mat_of` makes a zeroed matrix; `.set`/`.get` reach a cell; an index out of bounds fails BadIndex.",
      expect="sh:0",
      sh=lib_run(["ntensor"], """    matrix<int64>:m = mat_of::<int64>(raw v64(2i64), 3i64) ?! BadShape;
    if ((m.get(1i64, 2i64) ?! BadIndex) != 0i64) { exit 10i32; }
    m.set(1i64, 2i64, raw v64(7i64)) ?! BadIndex;
    if ((m.get(1i64, 2i64) ?! BadIndex) != 7i64) { exit 11i32; }
    Result<int64>:r = m.get(raw v64(5i64), 0i64);
    if (!(r.is_error)) { exit 12i32; }
    if (r.err != BadIndex) { exit 13i32; }
    exit 0i32;""", arms=NT_ARMS),
      wrong="refused, a trap, or 10-13")
claim("ty1815", D, 1815, "`tensor<T>` is `{ buffer:cells; int64:ndims; int64[9]:dims; }`", "rule",
      "`tensor<T>` is a buffer, an int64 and nine inline int64 dims: 104 bytes.",
      expect="sh:0",
      sh=lib_run(["ntensor"], """    if (#size_of<S0>() != 104i64) { exit 10i32; }
    exit 0i32;""", "struct:S0 = { tensor<int64>:v; };", arms=NT_ARMS),
      wrong="10: another layout")
claim("ty1816", D, 1816, "**rank capped at 9**", "rule",
      "A tensor's rank is capped at 9: `tensor_of` with ten dims fails, and with three succeeds.",
      expect="sh:0",
      sh=lib_run(["ntensor"], """    int64[10]:d10 = [1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64];
    Result<tensor<int64>>:r = tensor_of::<int64>(d10[0i64...10i64]);
    if (!(r.is_error)) { exit 10i32; }
    int64[3]:d3 = [2i64, 3i64, 4i64];
    tensor<int64>:t = tensor_of::<int64>(d3[0i64...3i64]) ?! BadShape;
    if (t.ndims != 3i64) { exit 11i32; }
    exit 0i32;""", arms=NT_ARMS),
      wrong="refused, or 10: a rank-10 tensor made; 11")
claim("ty1825", D, 1825, "`matrix<tryte>` and", "rule",
      "`matrix<tryte>` is the ternary matrix: a cell holds a tryte, and ERR rides through it.",
      expect="sh:0",
      sh=lib_run(["ntensor"], """    matrix<tryte>:m = mat_of::<tryte>(raw v64(1i64), 2i64) ?! BadShape;
    tryte:t = 29524;
    m.set(0i64, 0i64, t) ?! BadIndex;
    tryte:e = ERR;
    m.set(0i64, 1i64, e) ?! BadIndex;
    tryte:a = m.get(0i64, 0i64) ?! BadIndex;
    tryte:b = m.get(0i64, 1i64) ?! BadIndex;
    if ((a => int32) != 29524i32) { exit 10i32; }
    if (!(is_err(b))) { exit 11i32; }
    exit 0i32;""", arms=NT_ARMS),
      wrong="refused, or 10/11")

# ================================================================== 26. fixed
claim("ty1843", D, 1843, "```nitpick", "example",
      "The example's positions (module bindings, a local, a late local, a struct field, a parameter) compile.",
      expect="compile",
      src=prog_("    exit 0i32;", """func:compute = int32(int32:x) never fails { pass x; };

// A module binding. Its initialiser is the only place it can be written
// (D-165), it must be a compile-time constant, and D-211 requires the keyword.
pub fixed int32:MAX_SIZE = 1024i32;
pub fixed string:VERSION = "1.0.0";

// A local, written where it is declared...
func:f = NIL() never fails {
    fixed int32:cap = 100i32;
    // cap = 200i32;        // NITPICK-ASSIGN-002
    pass NIL;
};

// ...or written ONCE, LATER, from a value nothing knew at compile time.
// This is the case other languages make you work around.
func:g = int32(int32:seed) never fails {
    fixed int32:derived;
    derived = raw compute(seed);   // the one write, at run time
    // derived = 0i32;             // NITPICK-ASSIGN-002
    pass derived;
};

// A struct field, written when the aggregate is constructed and never after —
// including through a pointer.
pub struct:Config = {
    fixed string:name;
    int32:value;
};

// A parameter the callee may not reassign.
func:greet = NIL(fixed string:name) { pass NIL; };"""),
      wrong="refused")
claim("ty1845", D, 1845, "(D-165), it must be a compile-time constant", "rule",
      "A module binding's initialiser must be a compile-time constant: a run-time call is refused.",
      expect="refuse",
      src=prog_("""    if (M != 5i32) { exit 10i32; }
    exit 0i32;""", "fixed int32:M = raw v32(5i32);"),
      wrong="accepted")
claim("ty1845b", D, 1845, "and D-211 requires the keyword", "rule",
      "D-211 requires the keyword: a module binding without `fixed` is refused.", expect="refuse",
      src=prog_("""    if (M != 5i32) { exit 10i32; }
    exit 0i32;""", "int32:M = 5i32;"),
      wrong="accepted")
claim("ty1852", D, 1852, "// cap = 200i32;        // NITPICK-ASSIGN-002", "rule",
      "A fixed local written again is ASSIGN-002.", expect="refuse:NITPICK-ASSIGN-002",
      src=prog_("""    fixed int32:cap = raw v32(100i32);
    cap = 200i32;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1860", D, 1860, "derived = raw compute(seed);   // the one write, at run time", "rule",
      "A fixed local may be written once, later, at run time.", m10="d12_fixed_local_written_later")
claim("ty1861", D, 1861, "// derived = 0i32;             // NITPICK-ASSIGN-002", "rule",
      "A second write to a late fixed local is ASSIGN-002.", m10="d13_fixed_local_written_twice")
claim("ty1865", D, 1865, "// A struct field, written when the aggregate is constructed and never after —", "rule",
      "A fixed field written after construction is ASSIGN-002.", m10="d14_fixed_field_written")
claim("ty1866", D, 1866, "// including through a pointer.", "rule",
      "A fixed field written through a pointer is ASSIGN-002.", expect="refuse:NITPICK-ASSIGN-002",
      src=prog_("""    Cfg:c = Cfg{ name: raw v32(1i32), value: 2i32 };
    Cfg->:p = @c;
    p.name = 3i32;
    exit 0i32;""", "struct:Cfg = { fixed int32:name; int32:value; };"),
      wrong="accepted: the field rewritten through the pointer")
claim("ty1873", D, 1873, "func:greet = NIL(fixed string:name) { pass NIL; };", "rule",
      "A fixed parameter may not be reassigned: ASSIGN-002.", expect="refuse:NITPICK-ASSIGN-002",
      src=prog_("""    if (raw m11g(raw v32(1i32)) != 2i32) { exit 10i32; }
    exit 0i32;""", "func:m11g = int32(fixed int32:x) never fails { x = 2i32; pass x; };"),
      wrong="accepted")
claim("ty1884", D, 1884, "```nitpick", "example",
      "`comptime(…)` around a folding initialiser is accepted: `comptime(2i32 * 3i32)` is 6.",
      expect="run:0",
      src=prog_("""    fixed int32:ok = comptime(2i32 * 3i32);
    if (ok != 6i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1886", D, 1886, "fixed int32:no = comptime(raw runtime_val());  // refused: does not fold", "rule",
      "`comptime(…)` around a run-time value is TYPE-004.", expect="refuse:NITPICK-TYPE-004",
      src=prog_("""    fixed int32:no = comptime(raw runtime_val());
    if (no != 1i32) { exit 10i32; }
    exit 0i32;""", "func:runtime_val = int32() never fails { pass 1i32; };"),
      wrong="accepted")
claim("ty1891", D, 1891, "A module binding lowers to `@\"npk.<module>.name\" =", "rule",
      "A fixed module binding is a constant global: `@\"npk.<module>.MAX_SIZE\" = constant i32 1024`.",
      expect=r'ir:(?m)^@"npk\.ty1891\.MAX_SIZE" = [^\n]*\bconstant i32 1024\b',
      src=prog_("""    if (MAX_SIZE != 1024i32) { exit 10i32; }
    exit 0i32;""", "pub fixed int32:MAX_SIZE = 1024i32;"),
      wrong="a mutable global, or a load from elsewhere")
claim("ty1922", D, 1922, "`const` is not a reserved word", "rule",
      "`const` is an ordinary identifier: a local named `const` compiles.",
      expect="run:0",
      src=prog_("""    int32:const = raw v32(5i32);
    if (const != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused")

# ================================================================== 27. special values
NILF = "func:m11n = NIL() {\n    pass(NIL);\n};"
claim("ty1941", D, 1941, "\"void functions\" DO NOT EXIST in Nitpick", "rule",
      "A NIL function returns `Result<NIL>`: its call binds to a `Result<NIL>`, which is not an error.",
      expect="run:0",
      src=prog_("""    Result<NIL>:r = m11n();
    if (r.is_error) { exit 10i32; }
    exit 0i32;""", NILF),
      wrong="refused, or 10")
claim("ty1942", D, 1942, "`pass(NIL)` desugars to `return Result{ value: NIL, err: 0i32 }`", "rule",
      "The desugared form `return Result{ value: NIL, err: 0i32 };` is a success.",
      expect="run:0",
      src=prog_("""    Result<NIL>:r = m11d();
    if (r.is_error) { exit 10i32; }
    exit 0i32;""", "func:m11d = NIL() {\n    return Result{ value: NIL, err: 0i32 };\n};"),
      wrong="refused (an int32 code), or 10")
claim("ty1943", D, 1943, "To call a NIL-returning function without checking: `drop(myFunc());`", "rule",
      "A NIL-returning function is called without checking by `drop(myFunc());`.",
      expect="run:0",
      src=prog_("""    drop(myFunc());
    exit 0i32;""", "func:myFunc = NIL() {\n    pass(NIL);\n};"),
      wrong="refused (TYPE-042: `drop` licensed by `never fails` only, D-163)")
claim("ty1944", D, 1944, "**`NIL` is zero-sized** (D-084)", "rule",
      "NIL is zero-sized: a struct of an int32 and a NIL field is 4 bytes.",
      expect="run:0",
      src=prog_("""    if (#size_of<S>() != 4i64) { exit 10i32; }
    exit 0i32;""", "struct:S = { int32:a; NIL:n; };"),
      wrong="refused, or 10")
claim("ty1953", D, 1953, "**`NULL` with no context is", "rule",
      "NULL with no context is an error.", expect="refuse",
      src=prog_("""    discard(NULL);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1954", D, 1954, "an error and `NIL` is not**", "rule",
      "NIL with no context is not an error: it is the unit value.",
      expect="run:0",
      src=prog_("""    discard(NIL);
    exit 0i32;"""),
      wrong="refused")
claim("ty1956", D, 1956, "`NIL?` is refused", "rule",
      "`NIL?` is refused.", expect="refuse",
      src=prog_("""    NIL?:x = NIL;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1957", D, 1957, "IR: `Result<NIL>` is therefore `{ i32 }`", "rule",
      "`Result<NIL>` is `{ i32 }`, 4 bytes, alignment 4.",
      expect="run:0", src=layout(["Result<NIL>"], 4, 4), wrong=layout_wrong("Result<NIL>", 4, 4))
claim("ty1957b", D, 1957, "IR: `Result<NIL>` is therefore `{ i32 }`", "rule",
      "A NIL function returns `{ i32 }`.",
      expect=r'ir:(?m)^define \{ i32 \} @"?(?:[\w$]+\.)*m11n"?\(',
      src=prog_("""    Result<NIL>:r = m11n();
    if (r.is_error) { exit 10i32; }
    exit 0i32;""", NILF),
      wrong="another return type")
claim("ty1968", D, 1968, "Represents address zero — the null pointer", "rule",
      "NULL is the null pointer: a pointer set to NULL compares equal to it.",
      expect="run:0",
      src=prog_("""    int32->:p = NULL;
    if (p != NULL) { exit 10i32; }
    int32:x = raw v32(1i32);
    p = @x;
    if (p == NULL) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1970", D, 1970, "NOT valid as a general \"no value\" — that's `NIL`", "rule",
      "NULL is not a general no-value: `int32:x = NULL;` is refused.", expect="refuse",
      src=prog_("""    int32:x = NULL;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1971", D, 1971, "IR: `ptr null`", "rule",
      "NULL is `ptr null` in the IR.",
      expect=ir_fn("m11z", r"\bptr null\b"),
      src=prog_("""    int32->:p = raw m11z();
    if (p != NULL) { exit 10i32; }
    exit 0i32;""", "func:m11z = int32->() never fails { int32->:p = NULL; pass p; };"),
      wrong="another constant")
claim("ty1975", D, 1975, "ONLY valid inside `extern { }` blocks, for functions that return C `void`", "rule",
      "`void` is valid inside an extern block, as a method's return type.",
      expect="sh:0",
      sh=SH_LIB + 'cp "$LIB/nbridge.npk" "$LIB/nsys.npk" . || exit 5\n' +
      "cat > r.npk <<'NPK_EOF'\n" + 'mod:r;\nuse "./nbridge.npk".*;\n\nextern:"drv" = {\n' +
      "    func:probe = void(Bridge->:b, Duration:within);\n};\n\n" +
      main_("    exit 0i32;") + "\n" + failsafe_text("") +
      'NPK_EOF\n"$NPKC" r.npk -o p.ll > npkc.out 2>&1; rc=$?; head -3 npkc.out\n[ $rc -eq 0 ]\n',
      wrong="refused")
claim("ty1976", D, 1976, "**Forbidden everywhere else** — type checker error with diagnostic:", "rule",
      "`void` outside an extern block is refused with \"'void' is reserved for extern blocks; use 'NIL' for "
      "Nitpick functions returning nothing\".",
      expect="sh:0",
      sh=sh_refused_with("func:m11v = void() never fails { pass NIL; };\n" + main_("    exit 0i32;"),
                         "is reserved for extern blocks; use"),
      wrong="accepted, or refused with another message")
claim("ty1978", D, 1978, "IR: maps to LLVM `void` return type in the extern function's `declare`", "rule",
      "An extern void function is a `declare void`.",
      untestable="[tool] an extern block lowers to driver-wire stubs (D-149), whose shape needs a driver to observe")
claim("ty1983", D, 1983, "MUST be used with the pointer suffix: `any->`  (NOT bare `any`)", "rule",
      "Bare `any` is refused with \"'any' must be used as a pointer type: 'any->'. Bare 'any' is not a valid type.\"",
      expect="sh:0",
      sh=sh_refused_with("func:m11a = int32(any:_~x) never fails { pass 0i32; };\n" + main_("    exit 0i32;"),
                         "must be used as a pointer type"),
      wrong="accepted, or refused with another message")
claim("ty1987", D, 1987, "Cast to concrete type via **`p =>! T`** before dereferencing", "rule",
      "An `any->` is cast to a concrete pointer with `=>!` and then dereferenced.",
      expect="run:0",
      src=prog_("""    int32:x = raw v32(5i32);
    any->:p = @x =>! any->;
    int32->:q = p =>! int32->;
    if (<-q != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1989", D, 1989, "This read `p => T`", "rule",
      "Giving an `any->` a type with `=>` is refused (D-095).", expect="refuse",
      src=prog_("""    int32:x = raw v32(5i32);
    any->:p = @x =>! any->;
    int32->:q = p => int32->;
    exit 0i32;"""),
      wrong="accepted")
PP = "struct:S = { int32:x; };"
claim("ty1998", D, 1998, "`.` dereferences a pointer once.", "rule",
      "`p.x` reaches the field through a `T->`, and `(<-pp).x` through a `T->->`.",
      expect="run:0",
      src=prog_("""    S:s = S{ x: raw v32(4i32) };
    S->:p = @s;
    S->->:pp = @p;
    if (p.x != 4i32) { exit 10i32; }
    if ((<-pp).x != 4i32) { exit 11i32; }
    exit 0i32;""", PP),
      wrong="refused, or 10/11")
claim("ty1999", D, 1999, "`pp.x` where `pp` is `T->->` is an error", "rule",
      "`pp.x` through a `T->->` is refused.", expect="refuse",
      src=prog_("""    S:s = S{ x: raw v32(4i32) };
    S->:p = @s;
    S->->:pp = @p;
    if (pp.x != 4i32) { exit 10i32; }
    exit 0i32;""", PP),
      wrong="accepted: two levels peeled silently")
claim("ty2004", D, 2004, "The same rule applies to UFCS: `q.method()` peels exactly one", "rule",
      "A method call peels exactly one level.",
      untestable="[vague] which receiver types a method accepts after its one peel is not stated")
claim("ty2007", D, 2007, "`any->` has no members at any level.", "rule",
      "`any->` has no members: `p.x` is refused.", expect="refuse",
      src=prog_("""    S:s = S{ x: raw v32(4i32) };
    any->:p = @s =>! any->;
    if (p.x != 4i32) { exit 10i32; }
    exit 0i32;""", PP),
      wrong="accepted")
claim("ty2011", D, 2011, "Not a type the user can write directly", "rule",
      "`unknown` is not a type a user writes: `unknown:x = …` is refused.", expect="refuse",
      src=prog_("""    unknown:x = raw v32(5i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ty2013", D, 2013, "Propagates through operations: `unknown + 1` → result is also `unknown`", "rule",
      "The taint propagates: `r.value + 1` from an unchecked Result is refused.", expect="refuse",
      src=prog_("""    Result<int32>:r = m11k(raw v32(0i32));
    int32:v = r.value + 1i32;
    if (v != 6i32) { exit 10i32; }
    exit 0i32;""", K),
      wrong="accepted")
claim("ty2014", D, 2014, "Must be cleared by checking `Result.is_error` first", "rule",
      "Checking `is_error` clears the taint: after the check, `r.value + 1` is 6.",
      expect="run:0",
      src=prog_("""    Result<int32>:r = m11k(raw v32(0i32));
    if (r.is_error) { exit 10i32; }
    int32:v = r.value + 1i32;
    if (v != 6i32) { exit 11i32; }
    exit 0i32;""", K),
      wrong="refused, or 10/11")
claim("ty2019", D, 2019, "has been removed from the language", "rule",
      "`ok` is removed: `ok(r)` is refused.", expect="refuse",
      src=prog_("""    Result<int32>:r = m11k(raw v32(0i32));
    int32:v = ok(r);
    exit 0i32;""", K),
      wrong="accepted")
claim("ty2021", D, 2021, "IR: uses `undef` value with taint metadata in debug builds", "rule",
      "A tainted value is `undef` with taint metadata in debug builds.",
      untestable="[tool] no debug build is defined for the harness; release IR has no taint metadata to read")

# ================================================================== 28. operators
ARITH = """func:m11i = int32(int32:a, int32:b) never fails { pass (a OP b); };
func:m11f = flt64(flt64:a, flt64:b) never fails { pass (a OP b); };"""


def arith(op, ival, fval):
    return prog_("""    if (raw m11i(raw v32(7i32), 2i32) != %s) { exit 10i32; }
    if (raw m11f(raw vf64(7.0f64), 2.0f64) != %s) { exit 11i32; }
    exit 0i32;""" % (ival, fval), ARITH.replace("OP", op))


for ln, op, ii, fi, iv, fv in ((2032, "+", "add", "fadd", "9i32", "9.0f64"),
                               (2033, "-", "sub", "fsub", "5i32", "5.0f64"),
                               (2034, "*", "mul", "fmul", "14i32", "14.0f64"),
                               (2035, "/", "sdiv", "fdiv", "3i32", "3.5f64"),
                               (2036, "%", "srem", "frem", "1i32", "1.0f64")):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % op, "row",
          "`%s` lowers to `%s` on int32 and `%s` on flt64." % (op, ii, fi),
          expect=ir_all(_fn("m11i") + _body(r"\b%s\b" % ii), _fn("m11f") + _body(r"\b%s\b" % fi)),
          src=arith(op, iv, fv), wrong="another instruction (an overflow intrinsic, a call)")
claim("ty2035b", D, 2035, "div-by-zero → failsafe", "row",
      "Integer division by zero goes to failsafe (DivByZero).", expect="trap:DivByZero",
      src=prog_("""    int32:q = raw v32(7i32) / raw v32(0i32);
    if (q == 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap (10, 11)")
claim("ty2037", D, 2037, "| `**` | power | library call | Tier 1 |", "row",
      "`**` is power: 2 ** 10 is 1024.",
      expect="run:0",
      src=prog_("""    int32:p = raw v32(2i32) ** 10i32;
    if (p != 1024i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no `**`), or 10")
claim("ty2038", D, 2038, "| `<=>` | spaceship | `icmp`+select | Returns -1/0/1 |", "row",
      "`<=>` returns -1, 0 or 1.",
      expect="run:0",
      src=prog_("""    int32:a = raw v32(3i32);
    if ((a <=> 5i32) != -1i32) { exit 10i32; }
    if ((a <=> 3i32) != 0i32) { exit 11i32; }
    if ((a <=> 1i32) != 1i32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
BITS = "func:m11b = int32(int32:a, int32:b) never fails { pass (a OP b); };"
for ln, op, ins, val in ((2043, "&", r"\band i32\b", "4i32"), (2044, "\\|", r"\bor i32\b", "13i32"),
                         (2045, "^", r"\bxor i32\b", "9i32")):
    o = op.replace("\\", "")
    claim("ty%04d" % ln, D, ln, "| `%s` |" % op, "row",
          "`%s` lowers to `%s`." % (o, ins.replace(r"\b", "")),
          expect=ir_fn("m11b", ins),
          src=prog_("""    if (raw m11b(raw v32(12i32), 5i32) != %s) { exit 10i32; }
    exit 0i32;""" % val, BITS.replace("OP", o)),
          wrong="another instruction")
claim("ty2046", D, 2046, "| `~` | bitwise NOT | `xor %v, -1` |", "row",
      "`~` lowers to `xor %v, -1`.",
      expect=ir_fn("m11n", r"\bxor i32 %[^,\n]+, -1\b"),
      src=prog_("""    if (raw m11n(raw v32(5i32)) != -6i32) { exit 10i32; }
    exit 0i32;""", "func:m11n = int32(int32:a) never fails { pass (~a); };"),
      wrong="another lowering")
claim("ty2046b", D, 2046, "| `~` | bitwise NOT | `xor %v, -1` |", "row",
      "`~` is bitwise NOT.", m10="s09_bitwise_not")
claim("ty2047", D, 2047, "| `<<` | left shift | `shl` |", "row",
      "`<<` lowers to `shl`, guarded by one `icmp ult` for a computed amount.",
      expect=ir_fn("m11s", r"\bshl i32\b", r"\bicmp ult i32\b"),
      src=prog_("""    if (raw m11s(raw v32(3i32), 2i32) != 12i32) { exit 10i32; }
    exit 0i32;""", "func:m11s = int32(int32:a, int32:b) never fails { pass (a << b); };"),
      wrong="another lowering, or no guard")
claim("ty2047b", D, 2047, "TYPE-070 for a known amount outside it", "row",
      "A known shift amount outside [0, width) is TYPE-070.", expect="refuse:NITPICK-TYPE-070",
      src=prog_("""    int32:a = raw v32(3i32) << 32i32;
    exit 0i32;"""),
      wrong="accepted")
claim("ty2047c", D, 2047, "one `icmp ult` and `ShiftRange` for a computed one", "row",
      "A computed shift amount outside [0, width) traps ShiftRange.", expect="trap:ShiftRange",
      src=prog_("""    int32:a = raw v32(3i32) << raw v32(32i32);
    if (a == 3i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap: x86's masked shift (10) or 0 (11)")
claim("ty2048", D, 2048, "Arithmetic on a SIGNED operand, logical on an UNSIGNED one", "row",
      "`>>` is `ashr` on a signed operand and `lshr` on an unsigned one.",
      expect=ir_all(_fn("m11a") + _body(r"\bashr i32\b"), _fn("m11l") + _body(r"\blshr i32\b")),
      src=prog_("""    if (raw m11a(raw v32(-8i32), 1i32) != -4i32) { exit 10i32; }
    if (raw m11l(raw vu32(8u32), 1u32) != 4u32) { exit 11i32; }
    exit 0i32;""", """func:m11a = int32(int32:a, int32:b) never fails { pass (a >> b); };
func:m11l = uint32(uint32:a, uint32:b) never fails { pass (a >> b); };"""),
      wrong="one shift for both")
claim("ty2048b", D, 2048, "the operand's signedness decides", "row",
      "A signed right shift is arithmetic.", m10="s01_signed_right_shift_arithmetic")
claim("ty2048c", D, 2048, "a `>>>` row until 1.5.1b (the workbench's O-N12): it never lexed", "row",
      "`>>>` does not exist: it is refused.", expect="refuse",
      src=prog_("""    int32:a = raw v32(-8i32) >>> 1i32;
    exit 0i32;"""),
      wrong="accepted")
CMP = """func:m11i = bool(int32:a, int32:b) never fails { pass (a OP b); };
func:m11f = bool(flt64:a, flt64:b) never fails { pass (a OP b); };"""
for ln, op, ii, fi, t1, t2 in ((2053, "==", "icmp eq", "fcmp oeq", "false", "true"),
                               (2054, "!=", "icmp ne", "fcmp one", "true", "false"),
                               (2055, "<", "icmp slt", "fcmp olt", "false", "false"),
                               (2056, "<=", "icmp sle", "fcmp ole", "false", "true"),
                               (2057, ">", "icmp sgt", "fcmp ogt", "true", "false"),
                               (2058, ">=", "icmp sge", "fcmp oge", "true", "true")):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % op, "row",
          "`%s` lowers to `%s` on int32 and `%s` on flt64." % (op, ii, fi),
          expect=ir_all(_fn("m11i") + _body(r"\b%s i32\b" % ii), _fn("m11f") + _body(r"\b%s double\b" % fi)),
          src=prog_("""    bool:a = raw m11i(raw v32(7i32), 2i32);
    bool:b = raw m11f(raw vf64(2.0f64), 2.0f64);
    if (a != %s) { exit 10i32; }
    if (b != %s) { exit 11i32; }
    exit 0i32;""" % (t1, t2), CMP.replace("OP", op)),
          wrong="another predicate (an unordered one for floats)")
claim("ty2054b", D, 2054, "| `!=` | not equal | `icmp ne`/`fcmp one` |", "row",
      "NaN comparisons follow IEEE.", m10="m07_nan_comparisons")
claim("ty2053b", D, 2053, "**A struct, array, `Result`, `string` or `dyn` does not compare with `==`**", "row",
      "A struct does not compare with `==`.", expect="refuse",
      src=prog_("""    S:a = S{ x: raw v32(1i32) };
    S:b = S{ x: 1i32 };
    if (a == b) { exit 0i32; }
    exit 10i32;""", PP),
      wrong="accepted")
claim("ty2053c", D, 2053, "**A struct, array, `Result`, `string` or `dyn` does not compare with `==`**", "row",
      "A string does not compare with `==`.", expect="refuse",
      src=prog_("""    string:a = "x";
    string:b = "x";
    if (a == b) { exit 0i32; }
    exit 10i32;"""),
      wrong="accepted")
claim("ty2053d", D, 2053, "**A struct, array, `Result`, `string` or `dyn` does not compare with `==`**", "row",
      "An array does not compare with `==`.", expect="refuse",
      src=prog_("""    int32[2]:a = [raw v32(1i32), 2i32];
    int32[2]:b = [1i32, 2i32];
    if (a == b) { exit 0i32; }
    exit 10i32;"""),
      wrong="accepted")
claim("ty2053e", D, 2053, "`string_eq` for strings", "row",
      "Strings compare with `string_eq`.",
      expect="run:0",
      src=prog_("""    string:a = "xy";
    string:b = "xy";
    if (!(string_eq(a, b))) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no `string_eq`), or 10")
claim("ty2063", D, 2063, "| `&&` | logical AND | `and i1` (short-circuit) | Both sides bool |", "row",
      "`&&` short-circuits: `false && f()` does not call f.",
      expect="run:0",
      src=prog_("""    int32:n = 0i32;
    if (raw vb(false) && raw m11t(@n)) { exit 10i32; }
    if (n != 0i32) { exit 11i32; }
    exit 0i32;""", "func:m11t = bool(int32->:p) never fails { <-p = 1i32; pass true; };"),
      wrong="11: the right side evaluated")
claim("ty2064", D, 2064, "| `\\|\\|` | logical OR | `or i1` (short-circuit) | Both sides bool |", "row",
      "`||` short-circuits: `true || f()` does not call f.",
      expect="run:0",
      src=prog_("""    int32:n = 0i32;
    if (!(raw vb(true) || raw m11t(@n))) { exit 10i32; }
    if (n != 0i32) { exit 11i32; }
    exit 0i32;""", "func:m11t = bool(int32->:p) never fails { <-p = 1i32; pass true; };"),
      wrong="11: the right side evaluated")
claim("ty2065", D, 2065, "| `!` | logical NOT | `xor i1 %v, true` |", "row",
      "`!` lowers to `xor i1 %v, true`.",
      expect=ir_fn("m11n", r"\bxor i1 %[^,\n]+, true\b"),
      src=prog_("""    if (raw m11n(raw vb(true))) { exit 10i32; }
    exit 0i32;""", "func:m11n = bool(bool:a) never fails { pass (!(a)); };"),
      wrong="another lowering")
claim("ty2070", D, 2070, "a `fixed` binding has no address (D-287, TYPE-071)", "row",
      "A fixed binding has no address: `@k` is TYPE-071.", expect="refuse:NITPICK-TYPE-071",
      src=prog_("""    fixed int32:k = raw v32(5i32);
    int32->:p = @k;
    exit 0i32;"""),
      wrong="accepted: a write path to a fixed value")
claim("ty2070b", D, 2070, "val must be lvalue", "row",
      "`@` needs an lvalue: `@(1 + 2)` is refused.", expect="refuse",
      src=prog_("""    int32->:p = @(raw v32(1i32) + 2i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ty2071", D, 2071, "| `$$i val` / `$$m val` | shared / exclusive claim | the same address |", "row",
      "`$$i` and `$$m` are the same address, one pointer type: a `$$i` read sees what a `$$m` wrote.",
      expect="run:0",
      src=prog_("""    int32:x = raw v32(1i32);
    if (raw vb(true)) {
        int32->:m = $$m x;
        <-m = 9i32;
    }
    int32->:i = $$i x;
    if (<-i != 9i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty2072", D, 2072, "| `<-ptr` | dereference | `load T, ptr %ptr` |", "row",
      "`<-ptr` lowers to a `load` of T through the pointer.",
      expect=ir_fn("m11d", r"\bload i32, ptr %"),
      src=prog_("""    int32:x = raw v32(5i32);
    if (raw m11d(@x) != 5i32) { exit 10i32; }
    exit 0i32;""", "func:m11d = int32(int32->:p) never fails { pass <-p; };"),
      wrong="another lowering")
claim("ty2073", D, 2073, "| `ptr->field` | member via ptr |", "row",
      "`ptr->field` reads a member through a pointer.",
      expect="run:0",
      src=prog_("""    S:s = S{ x: raw v32(4i32) };
    S->:p = @s;
    int32:v = p->x;
    if (v != 4i32) { exit 10i32; }
    exit 0i32;""", PP),
      wrong="refused (members are `.` only, D-098), or 10")
claim("ty2074", D, 2074, "| `val.field` | direct member | `getelementptr` + `load` |", "row",
      "`val.field` lowers to a `getelementptr` and a `load`.",
      expect=ir_fn("m11g", r"\bgetelementptr\b", r"\bload i32\b"),
      src=prog_("""    if (raw m11g(raw v32(4i32)) != 4i32) { exit 10i32; }
    exit 0i32;""", PP + "\nfunc:m11g = int32(int32:v) never fails { S:s = S{ x: v }; pass s.x; };"),
      wrong="another access (extractvalue)")
claim("ty2079", D, 2079, "| `?` | safe unwrap with default | branch + select | `res ? default` |", "row",
      "`res ? default` is the safe unwrap.",
      expect="run:0",
      src=prog_("""    int32:v = m11k(raw v32(1i32)) ? 7i32;
    if (v != 7i32) { exit 10i32; }
    exit 0i32;""", K),
      wrong="refused (PARSE-011, D-175), or 10")
claim("ty2080", D, 2080, "| `?!` | emphatic unwrap | branch → failsafe | No default |", "row",
      "`?!` goes to failsafe on an error, with its own code (E1 exits 81).",
      expect="run:81",
      src=prog_("""    int32:v = m11k(raw v32(1i32)) ?! E1;
    if (v == 5i32) { exit 10i32; }
    exit 11i32;""", K),
      wrong="no trap (10, 11), or the callee's code (82)")
claim("ty2081", D, 2081, "| `??` | null coalesce | branch + select | `opt ?? default` |", "row",
      "`opt ?? default` coalesces an empty Optional.",
      expect="run:0",
      src=prog_("""    int32?:o = NIL;
    if ((o ?? raw v32(7i32)) != 7i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty2082", D, 2082, "| `?.\\|` | safe navigation | branch + select | `opt?.field` |", "row",
      "`opt?.field` is safe navigation.",
      expect="run:0",
      src=prog_("""    S?:o = S{ x: raw v32(4i32) };
    int32?:r = o?.x;
    if ((r ?? 0i32) != 4i32) { exit 10i32; }
    exit 0i32;""", PP),
      wrong="refused, or 10")
claim("ty2083", D, 2083, "| `\\|>` | pipe forward | `call f(%v)` | `v \\|> f` = `f(v)` |", "row",
      "`v |> f` is `f(v)`.",
      expect="run:0",
      src=prog_("""    int32:r = (raw v32(5i32) |> m11dbl) ?| 0i32;
    if (r != 10i32) { exit 10i32; }
    exit 0i32;""", "func:m11dbl = int32(int32:x) never fails { pass (x * 2i32); };"),
      wrong="refused, or 10")
claim("ty2084", D, 2084, "| `<\\|` | pipe backward | `call f(%v)` | `f <\\| v` = `f(v)` |", "row",
      "`f <| v` is `f(v)`.",
      expect="run:0",
      src=prog_("""    int32:x = raw v32(5i32);
    int32:r = (m11dbl <| x) ?| 0i32;
    if (r != 10i32) { exit 10i32; }
    exit 0i32;""", "func:m11dbl = int32(int32:x) never fails { pass (x * 2i32); };"),
      wrong="refused (TYPE-007: the function on the right), or 10")
claim("ty2089", D, 2089, "| `expr => T` | checked cast |", "row",
      "`expr => T` is the checked cast: int8 -5 => int32 sign-extends (`sext`).",
      expect=ir_fn("m11w", r"\bsext i8\b"),
      src=prog_("""    if (raw m11w(raw v8(-5i8)) != -5i32) { exit 10i32; }
    exit 0i32;""", "func:m11w = int32(int8:a) never fails { pass (a => int32); };"),
      wrong="another conversion")
claim("ty2090", D, 2090, "| `expr =>! T` | unchecked cast | same but no bounds check |", "row",
      "`expr =>! T` narrows with no bounds check: int64 2^32 + 5 =>! int32 is 5.",
      expect="run:0",
      src=prog_("""    int32:t = raw v64(4294967301i64) =>! int32;
    if (t != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="a trap, or 10")
claim("ty2095", D, 2095, "| `a..b` | inclusive range [a, b] | Used in `for`, `pick` patterns |", "row",
      "`a..b` is inclusive, in a `for` and in a `pick` pattern.",
      expect="run:0",
      src=prog_("""    int64:t = 0i64;
    for (int64:i in 0i64..raw v64(3i64)) { t = t + i; }
    if (t != 6i64) { exit 10i32; }
    int32:r = 0i32;
    pick (raw v32(3i32)) { (1i32..3i32) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11: an exclusive end")
claim("ty2096", D, 2096, "| `a...b` | exclusive range [a, b) | Used in `for`, `pick` patterns |", "row",
      "`a...b` is exclusive, in a `for` and in a `pick` pattern.",
      expect="run:0",
      src=prog_("""    int64:t = 0i64;
    for (int64:i in 0i64...raw v64(3i64)) { t = t + i; }
    if (t != 3i64) { exit 10i32; }
    int32:r = 0i32;
    pick (raw v32(3i32)) { (1i32...3i32) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 2i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11: an inclusive end")
claim("ty2101", D, 2101, "| `is (cond) : then : else` |", "row",
      "The ternary evaluates one branch.", m10="x05_ternary_evaluates_one_branch")
claim("ty2101b", D, 2101, "`select i1 %cond, %then, %else`", "row",
      "The ternary lowers to `select i1`.",
      expect=ir_fn("m11t", r"\bselect i1\b"),
      src=prog_("""    if (raw m11t(raw vb(true)) != 1i32) { exit 10i32; }
    exit 0i32;""", "func:m11t = int32(bool:c) never fails { pass (is (c) : 1i32 : 2i32); };"),
      wrong="branches instead")
claim("ty2106", D, 2106, "| `` `text &{expr}` `` | template literal | Interpolation via `&{ }` |", "row",
      "A template interpolates `&{ }`.",
      expect="run:0",
      src=prog_("""    int32:n = raw v32(7i32);
    string:s = `n=&{ n }`;
%s
    exit 0i32;""" % chk('string_equals(s, "n=7")', 10)),
      wrong="refused, or 10")
claim("ty2107", D, 2107, "| `r\"raw\"` | raw string | No escape processing |", "row",
      "A raw string does no escape processing: `r\"a\\nb\"` is four bytes.",
      expect="run:0",
      src=prog_(r"""    string:s = r"a\nb";
    if (s.len != 4i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10: the escape processed")
claim("ty2108", D, 2108, "| `\"\"\"triple\"\"\"` | triple-quoted string | Multiline, preserves indentation |", "row",
      "A triple-quoted string spans lines and keeps indentation: `\"\"\"ab` newline `  cd\"\"\"` is 7 bytes.",
      expect="run:0",
      src=prog_('''    string:s = """ab
  cd""";
    if (s.len != 7i64) { exit 10i32; }
    exit 0i32;'''),
      wrong="refused, or 10: the newline or the indentation lost")

excluded(D, 2114, "the type implementation priority table: a plan by cycle, history, not behaviour")

# ------------------------------------------------------------------ after run 1 (S45: text only)
refix("ty1607", "run 1: a unit expression does not parse inside a type's angle brackets (PARSE-001 at "
      "`Meters/Seconds`); the velocity unit is the prelude's named `MetersPerSecond` (the compiler's "
      "dim_basic.npk)",
      [("    dim256<Meters/Seconds>:v = m / s;", "    dim256<MetersPerSecond>:v = m / s;")])
for _id, _pairs in (("ty1987", [(" = @x =>! any->;", " = (@x) =>! any->;")]),
                    ("ty1989", [(" = @x =>! any->;", " = (@x) =>! any->;")]),
                    ("ty2007", [(" = @s =>! any->;", " = (@s) =>! any->;")])):
    refix(_id, "run 1: `@x =>! any->` parses as `@(x =>! any->)`, an `any->->` (TYPE-007); the address "
          "is taken first, `(@x) =>! any->`" + ("" if _id == "ty1987" else
                                               " (this refusal had agreed for that reason)"), _pairs)
