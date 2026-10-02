"""M11 claims: TYPE_REFERENCE.md lines 661-1176 at HUNT2 (sections 6 to 9).

tbb, the ternary and nonary kinds, the flag families, and the composites: structs
(with `sealed`/`hidden` and `limit<Rules>`), fixed arrays, slices and tagged enums.
Every expectation below is written from the reference's TEXT, before any program ran.
Session 9 extracted it (S65): TYPE 661-2122 is taken in three parts, each to its own
clean point.
"""
import re

from m11lib import *

covers("TYPE", 661, 1176)

D = "TYPE"


# ------------------------------------------------------------------ helpers
# The scaffolding below is type1.py's (layout, the IR fragments) and verif3.py's (the
# obligations script), copied: a claims module may not import another, whose claims
# would load twice.
def layout(types, size, align, decls="", body=""):
    """a run program: #size_of each type is `size`, and after an int8 it sits at
    offset `align` (so {int8, T} is align + size bytes)"""
    d, b = [], []
    code = 10
    for i, t in enumerate(types):
        if not t.replace("_", "").isalnum():
            d.append("struct:S%d = { %s:v; };" % (i, t))
        d.append("struct:P%d = { int8:a; %s:v; };" % (i, t))
    for i, t in enumerate(types):
        what = t if t.replace("_", "").isalnum() else "S%d" % i
        b.append("    if (#size_of<" + what + ">() != " + str(size) + "i64) { exit " +
                 str(code) + "i32; }")
        b.append("    if (#size_of<P" + str(i) + ">() != " + str(align + size) +
                 "i64) { exit " + str(code + 1) + "i32; }")
        code += 2
    return prog_("\n".join(b) + ("\n" + body.rstrip() if body.strip() else "") +
                 "\n    exit 0i32;", "\n".join(d) + ("\n" + decls if decls else ""))


def layout_wrong(t, size, align):
    return "10: %s is not %d bytes; 11: it does not sit at offset %d after an int8" % (t, size, align)


# the module's own identity helpers (m11lib's HELPERS has none for these types)
MYH = {"wt16": "tbb16", "wt64": "tbb64", "wt128": "tbb128", "wt256": "tbb256",
       "w256": "int256", "vtt": "trit", "vtr": "tryte", "vnt": "nit", "vny": "nyte",
       "vox": "oflags"}


def prog_(body, decls=""):
    """main_ around `body`, with the module's own identity helpers the text calls"""
    text = decls + "\n" + body
    hs = ["func:%s = %s(%s:x) never fails { pass x; };" % (n, t, t)
          for n, t in MYH.items() if re.search(r"\b%s\(" % n, text)]
    return main_(body, "\n".join(hs) + ("\n" + decls if decls.strip() else ""))


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


def _fn(name):
    return r'^define [^@\n]*@"?(?:[\w$]+\.)*' + name + r'"?\('


def _body(p):
    return r"(?=(?:(?!\n\}).)*?" + p + ")"


def ir_fn(name, *pats):
    """ir: the body of function `name` contains every pattern"""
    return "ir:(?s)" + _fn(name) + "".join(_body(p) for p in pats)


def param(name, ty):
    """a fragment: function `name`'s first parameter is `ty` (every function returns
    `{ T, i32 }`, so a return type is never demanded)"""
    return _fn(name) + ty + r"\b"


def ir_all(*frags):
    return r"ir:(?s)\A" + "".join("(?=.*?" + f + ")" for f in frags)


def fs_any():
    """a failsafe in which every trap exits 42: for a claim that says `traps` and names
    no trap"""
    arms = ["        (%s) { exit 42i32; }," % n for n, _ in TRAPS]
    arms.append("        (*) { exit 99i32; }")
    return ("func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) +
            "\n    }\n    exit 9i32;\n};")


def any_trap(body, decls=""):
    """a run:42 program: `body` should trap; reaching its end exits 10"""
    return prog_(body.rstrip() + "\n    exit 10i32;", (decls + "\n" if decls else "") + fs_any())


ANY = "names no trap: every trap exits 42 (`fs_any`)"


def prog(src, name="p"):
    """A whole program for a script (verif3's)."""
    h = helpers_text(src)
    out = "mod:%s;\n\n" % name + (h + "\n\n" if h else "") + src.strip() + "\n"
    if "func:failsafe" not in src:
        out += "\n" + failsafe_text(src)
    return out


OBL_HEAD = r'''# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
cat > p.npk <<'NPK_EOF'
@@PROG@@
NPK_EOF
"$NPKC" p.npk -o p.ll --obligations ob >out.txt 2>err.txt; rc=$?
if [ "$rc" -ne 0 ]; then echo "npkc exit $rc"; head -c 800 err.txt; exit 3; fi
[ -f ob/rows.txt ] || { echo "no rows.txt"; ls ob; exit 4; }
rows() { awk -F'\t' -v f="$1" -v k="$2" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } (k == "*" || $3 == k) && $6 ~ re' ob/rows.txt; }
n() { rows "$1" "$2" | wc -l | tr -d ' '; }
kinds() { rows "$1" '*' | cut -f3 | sort | uniq -c | tr -s ' ' | tr '\n' ';'; }
'''


def obl(src, checks):
    return OBL_HEAD.replace("@@PROG@@", prog(src)) + checks.strip() + "\nexit 0\n"


# ================================================================== 6. tbb
claim("ty0663", D, 663, "**reserved as the ERR sentinel**", "rule",
      "The most negative bit pattern is ERR, not a number: -127 is a tbb8 value, and -127 - 1 is ERR.",
      expect="run:0",
      src=prog_("""    tbb8:a = raw vt8(-127tbb8);
    if (is_err(a)) { exit 10i32; }
    tbb8:b = a - raw vt8(1tbb8);
%s
    exit 0i32;""" % chk("is_err(b)", 11)),
      wrong="10: -127 is not a value; 11: -128 is a number (the two's-complement range)")

TBB_MAX = {8: "127", 16: "32767", 32: "2147483647", 64: "9223372036854775807"}
TBB_ROWS = ((669, 8, 1, 1), (670, 16, 2, 2), (671, 32, 4, 4), (672, 64, 8, 8),
            (673, 128, 16, 8), (674, 256, 32, 8))
for ln, bits, size, align in TBB_ROWS:
    t = "tbb%d" % bits
    h = {8: "vt8", 32: "vt32"}.get(bits, "wt%d" % bits)
    if bits in TBB_MAX:
        mk = "    tbb%d:mx = raw %s(%stbb%d);" % (bits, h, TBB_MAX[bits], bits)
    else:   # past the 64-bit literal envelope: build 2^(N-1) - 1 in the integer of the width
        it, ih = ("int128", "vi128") if bits == 128 else ("int256", "w256")
        mk = ("    %s:hh = raw %s(1i%d) << %di%d;\n    %s:mm = (hh - 1i%d) + hh;\n"
              "    tbb%d:mx = mm => tbb%d;" % (it, ih, bits, bits - 2, bits, it, bits, bits, bits))
    body = mk + """
    if (is_err(mx)) { exit 20i32; }
%s
    tbb%d:mn = 0tbb%d - mx;
    if (is_err(mn)) { exit 22i32; }
%s""" % (chk("is_err(mx + raw %s(1tbb%d))" % (h, bits), 21), bits, bits,
         chk("is_err(mn - raw %s(1tbb%d))" % (h, bits), 23))
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` is %d byte%s with alignment %d; its valid range is symmetric, -(2^%d-1) .. 2^%d-1, "
          "and one step past either end is ERR." % (t, size, "" if size == 1 else "s", align,
                                                     bits - 1, bits - 1),
          expect="run:0", src=layout([t], size, align, body=body),
          wrong=layout_wrong(t, size, align) + "; 20/22: an end of the range is not a value; "
          "21/23: one past it is a number (wrapped)")
    claim("ty%04db" % ln, D, ln, "| `%s` | `i%d` |" % (t, bits), "row",
          "A `%s` parameter is an `i%d` in the IR." % (t, bits),
          expect="ir:(?m)" + param("m11t", "i%d" % bits),
          src=prog_("""    tbb%d:a = raw m11t(raw %s(5tbb%d));
    if (is_err(a)) { exit 10i32; }
    exit 0i32;""" % (bits, h, bits), "func:m11t = %s(%s:x) never fails { pass x; };" % (t, t)),
          wrong="another carrier")

claim("ty0680", D, 680, "makes negation and absolute", "rule",
      "Negation is total on tbb: for the valid -127, `x * -1` and `-x` are 127, not ERR.",
      expect="run:0",
      src=prog_("""    tbb8:x = raw vt8(-127tbb8);
    tbb8:y = x * raw vt8(-1tbb8);
    if (is_err(y)) { exit 10i32; }
    if (y != 127tbb8) { exit 11i32; }
    tbb8:z = -x;
    if (is_err(z)) { exit 12i32; }
    if (z != 127tbb8) { exit 13i32; }
    exit 0i32;"""),
      wrong="10/12: the negation of a valid value is ERR; 11/13: another number")
claim("ty0682", D, 682, "`INT_MIN / -1` — which faults in hardware on x86 — cannot arise", "rule",
      "The hardware's INT_MIN / -1 cannot arise: ERR / -1 at tbb32 is ERR, with no trap and no fault.",
      expect="run:0",
      src=prog_("""    tbb32:e = ERR;
    tbb32:q = raw vt32(e) / raw vt32(-1tbb32);
%s
    exit 0i32;""" % chk("is_err(q)", 10)),
      wrong="a DivOverflow trap (98), a SIGFPE (136), or a number (10)")
claim("ty0687", D, 687, "**Any operation on an ERR value yields ERR.**", "rule",
      "Any operation on ERR yields ERR, overriding identities: `ERR * 0` and `ERR - ERR` are ERR.",
      m10="m13_tbb_err_sticky")
claim("ty0690", D, 690, "Overflow **saturates to ERR** rather than wrapping", "rule",
      "tbb overflow saturates to ERR rather than wrapping: 100 + 100 at tbb8 is ERR, not -56.",
      expect="run:0",
      src=prog_("""    tbb8:a = raw vt8(100tbb8) + raw vt8(100tbb8);
%s
    exit 0i32;""" % chk("is_err(a)", 10)),
      wrong="10: a wrapped number (-56)")
claim("ty0692", D, 692, "Division or modulo by zero yields ERR (D-007).", "rule",
      "tbb division or modulo by zero yields ERR, with no trap.", m10="v18_tbb_div_by_zero_is_err")
claim("ty0693", D, 693, "**Comparison or branching on ERR traps to `failsafe`**", "rule",
      "Comparing or branching on ERR traps to failsafe.", m10="m12_tbb_compare_on_err_traps")
claim("ty0696", D, 696, "trapping, or a `pick` with an explicit `ERR:` arm.", "rule",
      "A pick with an explicit `ERR:` arm takes ERR without trapping.", m10="p13_tbb_err_arm_taken")
claim("ty0695", D, 695, "Use `is_err(x)` to test without", "rule",
      "`is_err(x)` tests a tbb for ERR without trapping, true for ERR and false for a value.",
      expect="run:0",
      src=prog_("""    tbb16:e = raw wt16(ERR);
    tbb16:v = raw wt16(5tbb16);
    bool:a = is_err(e);
    bool:b = is_err(v);
%s
%s
    exit 0i32;""" % (chk("a", 10), chk("!(b)", 11))),
      wrong="a trap (110), or 10/11: the test misreads ERR or a value")
claim("ty0697", D, 697, "**Bitwise operators are rejected** on `tbb`", "rule",
      "`~` on a tbb is refused.", expect="refuse",
      src=prog_("""    tbb8:x = raw vt8(127tbb8);
    tbb8:y = ~x;
    if (is_err(y)) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: `~127` fabricates the sentinel (10)")
claim("ty0698", D, 698, "or destroy it (`ERR & 0` is `0`)", "rule",
      "`&` on a tbb is refused.", expect="refuse",
      src=prog_("""    tbb8:e = raw vt8(ERR);
    tbb8:y = e & raw vt8(0tbb8);
    if (is_err(y)) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: ERR & 0 destroys the taint (11)")
claim("ty0699", D, 699, "**Casts are never straight bit operations.**", "rule",
      "A tbb8 ERR cast to tbb32 is ERR: the sentinel maps across widths rather than sign-extending "
      "into a valid -128.",
      expect="run:0",
      src=prog_("""    tbb8:e = raw vt8(ERR);
    tbb32:w = e => tbb32;
%s
    exit 0i32;""" % chk("is_err(w)", 10)),
      wrong="10: the sentinel sign-extended into the valid tbb32 -128")
claim("ty0702", D, 702, "**A cast OUT of the family traps on an ERR operand under BOTH spellings**", "rule",
      "`=>` out of tbb traps TbbErr on an ERR operand.", expect="trap:TbbErr",
      src=prog_("""    tbb8:e = raw vt8(ERR);
    int32:x = e => int32;
    if (x == -128i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="the sentinel converted as -128 (10) or another number (11)")
claim("ty0702b", D, 702, "**A cast OUT of the family traps on an ERR operand under BOTH spellings**", "rule",
      "`=>!` out of tbb traps TbbErr on an ERR operand: the bang acknowledges a value's loss, and ERR "
      "is not a value.", expect="trap:TbbErr",
      src=prog_("""    tbb32:e = raw vt32(ERR);
    int8:x = e =>! int8;
    if (x == 0i8) { exit 10i32; }
    exit 11i32;"""),
      wrong="the sentinel truncated to 0 (10) or converted otherwise (11)")
claim("ty0705", D, 705, "so `tbb64 =>", "rule",
      "`tbb64 => int8` is a compile error: the value is range-classified like any numeric pair.",
      expect="refuse",
      src=prog_("""    tbb64:v = raw wt64(5tbb64);
    int8:x = v => int8;
    if (x != 5i8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0706", D, 706, "`tbb32 => uint32` are compile errors", "rule",
      "`tbb32 => uint32` is a compile error.", expect="refuse",
      src=prog_("""    tbb32:v = raw vt32(5tbb32);
    uint32:x = v => uint32;
    if (x != 5u32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0706b", D, 706, "and take the bang", "rule",
      "With the bang, `tbb32 =>! uint32` and `tbb64 =>! int8` compile and convert an in-range value.",
      expect="run:0",
      src=prog_("""    tbb32:v = raw vt32(5tbb32);
    uint32:x = v =>! uint32;
    if (x != 5u32) { exit 10i32; }
    tbb64:w = raw wt64(-7tbb64);
    int8:y = w =>! int8;
    if (y != -7i8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11: a wrong value")
claim("ty0708", D, 708, "`=>` traps on a value with no image (the sentinel bit pattern, or out of", "rule",
      "Entering tbb8 with `=>` traps on the sentinel's bit pattern: int8 -128 has no tbb8 image.",
      expect="run:42", fs=False,
      src=any_trap("""    int8:m = raw v8(-127i8) - 1i8;
    tbb8:t = m => tbb8;
    if (is_err(t)) { exit 11i32; }"""),
      wrong="no trap: ERR (11) or a number (10)", note=ANY)
claim("ty0708b", D, 708, "`=>` traps on a value with no image (the sentinel bit pattern, or out of", "rule",
      "Entering tbb8 with `=>` traps on an out-of-range value: int32 200 has no tbb8 image.",
      expect="run:42", fs=False,
      src=any_trap("""    int32:m = raw v32(200i32);
    tbb8:t = m => tbb8;
    if (is_err(t)) { exit 11i32; }"""),
      wrong="no trap: ERR (11) or a wrapped number (10)", note=ANY)
claim("ty0709", D, 709, "and `=>!` saturates it to ERR", "rule",
      "Entering tbb8 with `=>!`, an out-of-range int32 (200) and the sentinel's int8 bit pattern "
      "(-128) are ERR, with no trap.",
      expect="run:0",
      src=prog_("""    int32:m = raw v32(200i32);
    tbb8:t = m =>! tbb8;
%s
    int8:s = raw v8(-127i8) - 1i8;
    tbb8:u = s =>! tbb8;
%s
    exit 0i32;""" % (chk("is_err(t)", 10), chk("is_err(u)", 11))),
      wrong="a trap, or 10/11: a number")
claim("ty0711", D, 711, "Definite-assignment analysis rejects", "rule",
      "There is no implicit default: a read before any write is refused.", m10="d02_read_unassigned")
claim("ty0713", D, 713, "so an ERR taint is cleared by `x = 5i32`", "rule",
      "Assignment replaces a value: an ERR binding assigned 5 holds 5, not ERR.",
      expect="run:0",
      src=prog_("""    tbb32:x = raw vt32(ERR);
    x = raw vt32(5tbb32);
    if (is_err(x)) { exit 10i32; }
    if (x != 5tbb32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10: the taint survives the assignment; 11: another value")
claim("ty0713b", D, 713, "Assignment *replaces* a value", "rule",
      "A binding declared without a value may be written later, and arithmetic after it is ordinary.",
      m10="d04_tbb_assign_replaces")
claim("ty0715", D, 715, "the `failsafe` signature", "rule",
      "tbb is used for the failsafe signature: a failsafe whose parameter is a tbb32 is accepted.",
      expect="run:0", fs=False,
      src=prog_("    exit 0i32;", """func:failsafe = int32(tbb32:code) {
    exit 9i32;
};"""),
      wrong="refused: the failsafe signature takes something else")

claim("ty0718", D, 718, "**To the verifier (D-278", "rule",
      "The verifier models a twisted value as an unbounded Int in the carrier's range, ERR being its "
      "most negative value; `is_err(x)` is `(= x MIN)`; each operation is the emitter's "
      "saturate-to-ERR `ite`.",
      untestable="[z3] the SMT model is what `npkg verify` gives z3; only the rows are written without it (below)")
claim("ty0723", D, 723, "trap the family has (`TbbErr` at a comparison or a cast out) is the", "rule",
      "A tbb comparison's TbbErr guard is an `err-exit` obligation: `npkc --obligations` writes an "
      "err-exit row for a function that compares a tbb32 parameter.",
      expect="sh:0",
      sh=obl("""func:f = int32(tbb32:a) never fails {
    if (a == 0tbb32) { pass 1i32; }
    pass 0i32;
};
""" + main_("""    if (raw f(raw vt32(3tbb32)) != 0i32) { exit 10i32; }
    exit 0i32;"""), """
echo "f's kinds: $(kinds f)"
[ "$(n f err-exit)" -ge 1 ] || exit 10
"""),
      wrong="10: no err-exit row for f")
claim("ty0725", D, 725, "division has no row: a zero divisor is ERR", "rule",
      "A twisted division has no row: a function dividing two tbb32s has no div-zero or div-min row.",
      expect="sh:0",
      sh=obl("""func:f = tbb32(tbb32:a, tbb32:b) never fails { pass (a / b); };
""" + main_("""    tbb32:q = raw f(raw vt32(7tbb32), raw vt32(2tbb32));
    if (is_err(q)) { exit 10i32; }
    exit 0i32;"""), """
echo "f's kinds: $(kinds f)"
[ "$(n f div-zero)" -eq 0 ] || exit 10
[ "$(n f div-min)" -eq 0 ] || exit 11
"""),
      wrong="10: a div-zero row; 11: a div-min row")

# ================================================================== 7. ternary and nonary
claim("ty0736", D, 736, "| `trit` | base-3 | −1, 0, 1 |", "row",
      "A trit holds -1, 0 and 1, and 1 + 1 is past its bound (ERR).",
      expect="run:0",
      src=prog_("""    trit:a = 0Tt;
    trit:b = 0;
    trit:c = 1;
    if ((a => int32) != -1i32) { exit 10i32; }
    if ((b => int32) != 0i32) { exit 11i32; }
    if ((c => int32) != 1i32) { exit 12i32; }
    trit:d = raw vtt(c) + raw vtt(c);
%s
    exit 0i32;""" % chk("is_err(d)", 13)),
      wrong="10-12: a state misread; 13: 2 is a trit value")
claim("ty0737", D, 737, "| `tryte` | base-3 | 10 trits |", "row",
      "A tryte is 10 trits: `.len` is 10, its largest value is 29524 ((3^10-1)/2), and 29524 + 1 is ERR.",
      expect="run:0",
      src=prog_("""    tryte:t = 29524;
    if (t.len != 10i64) { exit 10i32; }
    if (is_err(t)) { exit 11i32; }
    tryte:one = 1;
    tryte:u = raw vtr(t) + raw vtr(one);
%s
    exit 0i32;""" % chk("is_err(u)", 12)),
      wrong="10: another digit count; 11: 29524 is not a value; 12: 29525 is")
claim("ty0738", D, 738, "| `nit` | base-9 | −4 … 4 |", "row",
      "A nit holds -4 .. 4: 4 and -4 are values, and 4 + 1 is ERR.",
      expect="run:0",
      src=prog_("""    nit:a = 4;
    nit:one = 1;
    nit:b = 0 - a;
    if ((a => int32) != 4i32) { exit 10i32; }
    if ((b => int32) != -4i32) { exit 11i32; }
    nit:c = raw vnt(a) + raw vnt(one);
%s
    exit 0i32;""" % chk("is_err(c)", 12)),
      wrong="10/11: an end misread; 12: 5 is a nit value")
claim("ty0739", D, 739, "| `nyte` | base-9 | 5 nits |", "row",
      "A nyte is 5 nits: `.len` is 5, its largest value is 29524 ((9^5-1)/2), and 29524 + 1 is ERR.",
      expect="run:0",
      src=prog_("""    nyte:t = 29524;
    if (t.len != 5i64) { exit 10i32; }
    if (is_err(t)) { exit 11i32; }
    nyte:one = 1;
    nyte:u = raw vny(t) + raw vny(one);
%s
    exit 0i32;""" % chk("is_err(u)", 12)),
      wrong="10: another digit count; 11: 29524 is not a value; 12: 29525 is")
claim("ty0741", D, 741, "`tryte` and `nyte` hold the SAME 59049 states", "rule",
      "tryte and nyte hold the same states: -29524 and 29524 are values of both.",
      expect="run:0",
      src=prog_("""    tryte:a = 29524;
    tryte:b = 0 - a;
    nyte:c = 29524;
    nyte:d = 0 - c;
    if ((b => int32) != -29524i32) { exit 10i32; }
    if ((d => int32) != -29524i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10/11: the lower end is not a value")

TERN_ROWS = ((751, "trit", 8, 1), (752, "tryte", 16, 2), (753, "nit", 8, 1), (754, "nyte", 16, 2))
TERN_H = {"trit": "vtt", "tryte": "vtr", "nit": "vnt", "nyte": "vny"}
for ln, t, bits, size in TERN_ROWS:
    claim("ty%04d" % ln, D, ln, "| `%s` | `i%d` | %d byte" % (t, bits, size), "row",
          "On the binary rung a `%s` is %d byte%s with alignment %d." % (t, size, "" if size == 1 else "s", size),
          expect="run:0", src=layout([t], size, size), wrong=layout_wrong(t, size, size))
    claim("ty%04db" % ln, D, ln, "| `%s` | `i%d` |" % (t, bits), "row",
          "A `%s` parameter is an `i%d` in the IR." % (t, bits),
          expect="ir:(?m)" + param("m11t", "i%d" % bits),
          src=prog_("""    %s:one = 1;
    %s:a = raw m11t(raw %s(one));
    if ((a => int32) != 1i32) { exit 10i32; }
    exit 0i32;""" % (t, t, TERN_H[t]), "func:m11t = %s(%s:x) never fails { pass x; };" % (t, t)),
          wrong="another carrier")

claim("ty0768", D, 768, "ternary arithmetic is checked as **ternary** in the frontend", "rule",
      "Ternary arithmetic is checked as ternary in the frontend; nothing above the backend assumes `i8`.",
      untestable="[internal] where a check runs inside the compiler is not observable; its results are (below)")
claim("ty0777", D, 777, "**The binary rung stores the VALUE**", "rule",
      "The binary rung stores a tryte's balanced value: the tryte 60 is the constant `i16 60` in the IR.",
      expect=ir_fn("m11v", r"\bi16 60\b"),
      src=prog_("""    tryte:a = raw m11v();
    if ((a => int32) != 60i32) { exit 10i32; }
    exit 0i32;""", """func:m11v = tryte() never fails {
    tryte:t = 1T1T0t;
    pass t;
};"""),
      wrong="a packed-trit encoding: another constant")
claim("ty0779", D, 779, "ERR sentinel is the carrier's most-negative (−128 / −32768)", "rule",
      "A tryte's ERR is the carrier's most negative value: a function passing ERR as a tryte emits `-32768`.",
      expect=ir_fn("m11e", r"-32768\b"),
      src=prog_("""    tryte:a = raw m11e();
%s
    exit 0i32;""" % chk("is_err(a)", 10), """func:m11e = tryte() never fails {
    tryte:t = ERR;
    pass t;
};"""),
      wrong="another sentinel")
claim("ty0780", D, 780, "The prototype's packed-trit LUT emulation is deliberately NOT carried", "rule",
      "The packed-trit lookup-table emulation is not carried.",
      untestable="[internal] an emulation's absence; ty0777 tests the stored value")
claim("ty0786", D, 786, "`+ - *` at all four types", "rule",
      "`+ - *` compute at trit, tryte, nit and nyte.",
      expect="run:0",
      src=prog_("""    trit:t1 = 1;
    trit:tm = 0Tt;
    trit:ts = raw vtt(t1) + raw vtt(tm);
    if ((ts => int32) != 0i32) { exit 10i32; }
    trit:tp = raw vtt(tm) * raw vtt(tm);
    if ((tp => int32) != 1i32) { exit 11i32; }
    tryte:a = 100;
    tryte:b = 7;
    tryte:c = (raw vtr(a) - raw vtr(b)) * raw vtr(b);
    if ((c => int32) != 651i32) { exit 12i32; }
    nit:n = 3;
    nit:m = 0 - 2;
    nit:s = raw vnt(n) + raw vnt(m);
    if ((s => int32) != 1i32) { exit 13i32; }
    nyte:x = 1000;
    nyte:y = 30;
    nyte:z = raw vny(x) * raw vny(y) - raw vny(x);
    if ((z => int32) != 29000i32) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused at one type, or 10-14: a wrong result")
claim("ty0786b", D, 786, "**`/ %` at `tryte`/`nyte` only**", "rule",
      "`/` and `%` compute at tryte and nyte: 100 / 7 is 14 and 100 % 7 is 2 (truncating).",
      expect="run:0",
      src=prog_("""    tryte:a = 100;
    tryte:b = 7;
    tryte:q = raw vtr(a) / raw vtr(b);
    tryte:r = raw vtr(a) %% raw vtr(b);
    if ((q => int32) != 14i32) { exit 10i32; }
    if ((r => int32) != 2i32) { exit 11i32; }
    nyte:x = 100;
    nyte:y = 7;
    nyte:p = raw vny(x) / raw vny(y);
    if ((p => int32) != 14i32) { exit 12i32; }
    exit 0i32;""".replace("%%", "%")),
      wrong="refused, or 10-12: a wrong result")
claim("ty0787", D, 787, "refused by name (TYPE-051)", "rule",
      "`/` at trit is refused, TYPE-051.", expect="refuse:NITPICK-TYPE-051",
      src=prog_("""    trit:a = 1;
    trit:b = 1;
    trit:c = raw vtt(a) / raw vtt(b);
    if ((c => int32) != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0787b", D, 787, "refused by name (TYPE-051)", "rule",
      "`%` at nit is refused, TYPE-051.", expect="refuse:NITPICK-TYPE-051",
      src=prog_("""    nit:a = 3;
    nit:b = 2;
    nit:c = raw vnt(a) %% raw vnt(b);
    if ((c => int32) != 1i32) { exit 10i32; }
    exit 0i32;""".replace("%%", "%")),
      wrong="accepted")
claim("ty0788", D, 788, "**Overflow past the BALANCED bound → ERR**", "rule",
      "Overflow past the balanced bound is ERR at every width: nit 4 + 1, tryte 29524 * 2 and "
      "nyte -29524 - 1 are ERR.",
      expect="run:0",
      src=prog_("""    nit:a = 4;
    nit:one = 1;
%s
    tryte:t = 29524;
    tryte:two = 2;
%s
    nyte:y = 29524;
    nyte:ny = 0 - y;
    nyte:n1 = 1;
%s
    exit 0i32;""" % (chk("is_err(raw vnt(a) + raw vnt(one))", 10), chk("is_err(raw vtr(t) * raw vtr(two))", 11),
                     chk("is_err(raw vny(ny) - raw vny(n1))", 12))),
      wrong="10-12: a clamped or wrapped number")
claim("ty0789", D, 789, "`trit` is ERR exactly as `MAX + 1` is at `tbb`", "rule",
      "1 + 1 at trit is ERR (the prototype's clamp to 1 is overruled).",
      expect="run:0",
      src=prog_("""    trit:a = 1;
    trit:s = raw vtt(a) + raw vtt(a);
%s
    exit 0i32;""" % chk("is_err(s)", 10)),
      wrong="10: clamped to 1, or wrapped to -1")
claim("ty0792", D, 792, "Division by zero yields ERR (D-007's twisted row)", "rule",
      "Ternary division and modulo by zero yield ERR, with no trap.",
      expect="run:0",
      src=prog_("""    tryte:a = 42;
    tryte:z = 0;
%s
%s
    nyte:b = 42;
    nyte:y = 0;
%s
    exit 0i32;""" % (chk("is_err(raw vtr(a) / raw vtr(z))", 10), chk("is_err(raw vtr(a) %% raw vtr(z))", 11),
                     chk("is_err(raw vny(b) / raw vny(y))", 12))).replace("%%", "%"),
      wrong="a DivByZero trap (97), or 10-12: a number")
claim("ty0792b", D, 792, "comparisons at all four", "rule",
      "Comparisons work at all four ternary types in balanced (numeric) order.",
      expect="run:0",
      src=prog_("""    trit:tm = 0Tt;
    trit:tz = 0;
    if (!(raw vtt(tm) < raw vtt(tz))) { exit 10i32; }
    tryte:a = 0 - 5;
    tryte:b = 3;
    if (!(raw vtr(a) < raw vtr(b))) { exit 11i32; }
    nit:n = 0 - 4;
    nit:m = 4;
    if (!(raw vnt(m) > raw vnt(n))) { exit 12i32; }
    nyte:x = 0 - 100;
    nyte:y = 0 - 99;
    if (!(raw vny(x) <= raw vny(y))) { exit 13i32; }
    if (raw vny(x) == raw vny(y)) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused (ordering at a twisted type), or 10-14: an order other than the balanced value's")
claim("ty0794", D, 794, "comparison traps; `is_err` looks", "rule",
      "An ERR operand at a bare ternary comparison traps TbbErr (the family's one trap, line 723).",
      expect="trap:TbbErr",
      src=prog_("""    tryte:e = ERR;
    tryte:a = 5;
    if (raw vtr(e) < raw vtr(a)) { exit 10i32; }
    exit 11i32;"""),
      wrong="ERR ordered as a number (10, 11)")
claim("ty0795", D, 795, "ternary `pick` selector demands that arm exactly as a `tbb`'s does", "rule",
      "A ternary pick selector without an `ERR:` arm is refused.", expect="refuse",
      src=prog_("""    tryte:t = ERR;
    int32:r = 0i32;
    pick (raw vtr(t)) { (*) { r = 2i32; } }
    if (r == 2i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="accepted: ERR steers into `(*)` (10)")
claim("ty0794b", D, 794, "the `pick` `ERR:` arm handles", "rule",
      "A ternary pick's `ERR:` arm takes ERR.",
      expect="run:0",
      src=prog_("""    tryte:t = ERR;
    int32:r = 0i32;
    pick (raw vtr(t)) { ERR: { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="a trap, or 10: ERR steered elsewhere")
claim("ty0796", D, 796, "on `trit`/`nit`, `&` is three-valued", "rule",
      "On trit, `&` is min and `|` is max (Kleene), and NOT is `0 - x`.",
      expect="run:0",
      src=prog_("""    trit:tt = 1;
    trit:tu = 0;
    trit:tf = 0Tt;
    trit:a = raw vtt(tt) & raw vtt(tf);
    if ((a => int32) != -1i32) { exit 10i32; }
    trit:o = raw vtt(tu) | raw vtt(tf);
    if ((o => int32) != 0i32) { exit 11i32; }
    trit:u = raw vtt(tt) & raw vtt(tu);
    if ((u => int32) != 0i32) { exit 12i32; }
    trit:n = 0 - raw vtt(tf);
    if ((n => int32) != 1i32) { exit 13i32; }
    exit 0i32;"""),
      wrong="refused, or 10-13: a binary AND/OR on the carrier")
claim("ty0796b", D, 796, "on `trit`/`nit`, `&` is three-valued", "rule",
      "On nit, `&` is min and `|` is max.",
      expect="run:0",
      src=prog_("""    nit:a = 3;
    nit:b = 0 - 2;
    nit:m = raw vnt(a) & raw vnt(b);
    if ((m => int32) != -2i32) { exit 10i32; }
    nit:x = raw vnt(a) | raw vnt(b);
    if ((x => int32) != 3i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11: a bitwise result on the carrier")
claim("ty0797", D, 797, "ERR sticky", "rule",
      "The Kleene operators keep ERR: `1 & ERR` and `-1 | ERR` at trit are ERR.",
      expect="run:0",
      src=prog_("""    trit:tt = 1;
    trit:tf = 0Tt;
    trit:e = ERR;
%s
%s
    exit 0i32;""" % (chk("is_err(raw vtt(tt) & raw vtt(e))", 10), chk("is_err(raw vtt(tf) | raw vtt(e))", 11))),
      wrong="10/11: ERR absorbed by min or max")
claim("ty0799", D, 799, "the operators stay refused", "rule",
      "`&` on tryte is refused.", expect="refuse",
      src=prog_("""    tryte:a = 5;
    tryte:b = 3;
    tryte:c = raw vtr(a) & raw vtr(b);
    if ((c => int32) != 3i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0799b", D, 799, "multi-digit types the operators stay refused", "rule",
      "`|` on nyte is refused.", expect="refuse",
      src=prog_("""    nyte:a = 5;
    nyte:b = 3;
    nyte:c = raw vny(a) | raw vny(b);
    if ((c => int32) != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0801", D, 801, "**Digit access**: `t.trit(i)` / `n.nit(i)`", "rule",
      "`t.trit(i)` reads a tryte's balanced digits from the least significant (60 = 1T1T0: 0, -1, 1), "
      "and `n.nit(i)` a nyte's (100 = 121 nonary: 1, 2, 1).",
      expect="run:0",
      src=prog_("""    tryte:b = 1T1T0t;
    trit:d0 = b.trit(0i64);
    trit:d1 = b.trit(1i64);
    trit:d2 = b.trit(2i64);
    if ((d0 => int32) != 0i32) { exit 10i32; }
    if ((d1 => int32) != -1i32) { exit 11i32; }
    if ((d2 => int32) != 1i32) { exit 12i32; }
    nyte:y = 100;
    nit:e0 = y.nit(0i64);
    nit:e1 = y.nit(1i64);
    if ((e0 => int32) != 1i32) { exit 13i32; }
    if ((e1 => int32) != 2i32) { exit 14i32; }
    exit 0i32;"""),
      wrong="10-14: a digit misread (another order or encoding)")
claim("ty0802", D, 802, "`tryte` has trits, not nits", "rule",
      "A tryte has trits, not nits: `t.nit(0)` on a tryte is refused.", expect="refuse",
      src=prog_("""    tryte:b = 60;
    nit:d = b.nit(0i64);
    if ((d => int32) != 0i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0803", D, 803, "array's (OUT_OF_BOUNDS)", "rule",
      "A digit index past the digit count traps OutOfBounds: `t.trit(10)` on a tryte.",
      expect="trap:OutOfBounds",
      src=prog_("""    tryte:b = 60;
    trit:d = b.trit(raw v64(10i64));
    if ((d => int32) == 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="a digit read past the end (10, 11)")
claim("ty0803b", D, 803, "an ERR receiver yields an ERR digit", "rule",
      "An ERR receiver yields an ERR digit.",
      expect="run:0",
      src=prog_("""    tryte:e = ERR;
    trit:d = raw vtr(e).trit(0i64);
%s
    exit 0i32;""" % chk("is_err(d)", 10)),
      wrong="a trap, or 10: a digit of the sentinel's bits")
claim("ty0803c", D, 803, "`.len` is", "rule",
      "`.len` is the digit count as an int64: 10 for a tryte, 5 for a nyte, 1 for a trit or a nit.",
      expect="run:0",
      src=prog_("""    tryte:a = 1;
    nyte:b = 1;
    trit:c = 1;
    nit:d = 1;
    int64:la = a.len;
    if (la != 10i64) { exit 10i32; }
    if (b.len != 5i64) { exit 11i32; }
    if (c.len != 1i64) { exit 12i32; }
    if (d.len != 1i64) { exit 13i32; }
    exit 0i32;"""),
      wrong="refused, or 10-13: another count")
claim("ty0805", D, 805, "**Literals are contextual, any base**", "rule",
      "A ternary-typed slot takes an unsuffixed integer literal and a balanced-digit literal: "
      "`tryte:t = 42;` and `tryte:t = 1T1T0t;` are one value spelled two ways.",
      expect="run:0",
      src=prog_("""    tryte:a = 42;
    tryte:b = 1T1T0t;
    if (raw vtr(a) != raw vtr(b)) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10: the two spellings are different values",
      note="balanced 1T1T0 is 81 - 27 + 9 - 3 = 60 (reasoned): the text's two spellings may not be one value")
claim("ty0808", D, 808, "range-checked EXACTLY against the balanced bound", "rule",
      "A literal past the balanced bound is refused: `tryte:t = 29525;`.", expect="refuse",
      src=prog_("""    tryte:t = 29525;
    if (is_err(t)) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted (as ERR, 10, or wrapped)")
claim("ty0808b", D, 808, "range-checked EXACTLY against the balanced bound", "rule",
      "A literal past the balanced bound is refused: `trit:t = 2;`.", expect="refuse",
      src=prog_("""    trit:t = 2;
    if (is_err(t)) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0808c", D, 808, "range-checked EXACTLY against the balanced bound", "rule",
      "A literal at the bound is accepted exactly: `tryte:t = 29524;` and `nit:n = -4` (as `0 - 4`) are values.",
      expect="run:0",
      src=prog_("""    tryte:t = 29524;
    if ((t => int32) != 29524i32) { exit 10i32; }
    nit:n = 4;
    if ((n => int32) != 4i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty0808d", D, 808, "`ERR` takes the slot's", "rule",
      "`ERR` takes the slot's type: `nit:e = ERR;` is the nit ERR.",
      expect="run:0",
      src=prog_("""    nit:e = ERR;
%s
    exit 0i32;""" % chk("is_err(raw vnt(e))", 10)),
      wrong="refused, or 10")
claim("ty0810", D, 810, "one family within itself — value-preserving, the sentinel maps", "rule",
      "Within the ternary family a cast preserves the value and maps the sentinel: trit -1 => tryte is -1, "
      "and trit ERR => tryte is ERR.",
      expect="run:0",
      src=prog_("""    trit:a = 0Tt;
    tryte:w = raw vtt(a) => tryte;
    if ((w => int32) != -1i32) { exit 10i32; }
    trit:e = ERR;
    tryte:we = raw vtt(e) => tryte;
%s
    exit 0i32;""" % chk("is_err(we)", 11)),
      wrong="refused, or 10: a value changed; 11: the sentinel became a number")
claim("ty0811", D, 811, "a smaller-bound target trap-or-saturates (`=>` / `=>!`)", "rule",
      "A cast to a smaller-bound ternary target traps under `=>` when the value does not fit (tryte 60 => trit).",
      expect="run:42", fs=False,
      src=any_trap("""    tryte:b = 60;
    trit:t = raw vtr(b) => trit;
    if (is_err(t)) { exit 11i32; }"""),
      wrong="no trap: ERR (11) or a number (10)", note=ANY)
claim("ty0811b", D, 811, "a smaller-bound target trap-or-saturates (`=>` / `=>!`)", "rule",
      "A cast to a smaller-bound ternary target saturates to ERR under `=>!` (tryte 60 =>! trit), and a "
      "value that fits converts (tryte 1 =>! trit is 1).",
      expect="run:0",
      src=prog_("""    tryte:b = 60;
    trit:t = raw vtr(b) =>! trit;
%s
    tryte:c = 1;
    trit:u = raw vtr(c) =>! trit;
    if ((u => int32) != 1i32) { exit 11i32; }
    exit 0i32;""" % chk("is_err(t)", 10)),
      wrong="a trap, or 10: a number; 11: a fitting value lost")
claim("ty0812", D, 812, "`tryte ⇄ nyte` (the same 59049 values) is a pure relabel", "rule",
      "tryte => nyte => tryte keeps every value: 29524 and -29524 survive.",
      expect="run:0",
      src=prog_("""    tryte:a = 29524;
    tryte:b = 0 - a;
    nyte:x = raw vtr(a) => nyte;
    nyte:y = raw vtr(b) => nyte;
    tryte:c = raw vny(x) => tryte;
    if ((x => int32) != 29524i32) { exit 10i32; }
    if ((y => int32) != -29524i32) { exit 11i32; }
    if ((c => int32) != 29524i32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, a trap, or 10-12: a value changed")
claim("ty0813", D, 813, "ERR traps under BOTH spellings", "rule",
      "Leaving the ternary family, ERR traps TbbErr under `=>`.", expect="trap:TbbErr",
      src=prog_("""    tryte:e = ERR;
    int32:x = raw vtr(e) => int32;
    if (x == -32768i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="the sentinel converted (10, 11)")
claim("ty0813b", D, 813, "ERR traps under BOTH spellings", "rule",
      "Leaving the ternary family, ERR traps TbbErr under `=>!`.", expect="trap:TbbErr",
      src=prog_("""    trit:e = ERR;
    flt64:x = raw vtt(e) =>! flt64;
    if (x == 0.0f64) { exit 10i32; }
    exit 11i32;"""),
      wrong="the sentinel converted (10, 11)")
claim("ty0814", D, 814, "range-classified", "rule",
      "Leaving, the value is range-classified: `tryte => int8` is a compile error (29524 does not fit).",
      expect="refuse",
      src=prog_("""    tryte:t = 5;
    int8:x = raw vtr(t) => int8;
    if (x != 5i8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0814b", D, 814, "Entering: out-of-range traps under `=>`", "rule",
      "Entering the ternary family with `=>`, an out-of-range value traps: int32 30000 => tryte.",
      expect="run:42", fs=False,
      src=any_trap("""    int32:v = raw v32(30000i32);
    tryte:t = v => tryte;
    if (is_err(t)) { exit 11i32; }"""),
      wrong="no trap: ERR (11) or a number (10)", note=ANY)
claim("ty0815", D, 815, "under `=>!`.", "rule",
      "Entering the ternary family with `=>!`, an out-of-range value is ERR: int32 30000 =>! tryte.",
      expect="run:0",
      src=prog_("""    int32:v = raw v32(30000i32);
    tryte:t = v =>! tryte;
%s
    exit 0i32;""" % chk("is_err(t)", 10)),
      wrong="a trap, or 10: a number")
claim("ty0815b", D, 815, "Another twisted family (`tbb`, `tfp`, `dim256`) is reached", "rule",
      "Another twisted family is reached through the plain integer: (tryte => int32) => tbb32 converts.",
      expect="run:0",
      src=prog_("""    tryte:t = 42;
    tbb32:x = (raw vtr(t) => int32) => tbb32;
    if (x != 42tbb32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty0816", D, 816, "cross-family casts do not exist", "rule",
      "A direct cross-family cast is refused: tryte => tbb32.", expect="refuse",
      src=prog_("""    tryte:t = 42;
    tbb32:x = raw vtr(t) => tbb32;
    if (x != 42tbb32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0816b", D, 816, "cross-family casts do not exist", "rule",
      "A direct cross-family cast is refused under the bang too: tbb32 =>! nyte.", expect="refuse",
      src=prog_("""    tbb32:t = raw vt32(42tbb32);
    nyte:x = t =>! nyte;
    if ((x => int32) != 42i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0817", D, 817, "**`ToString`** renders the VALUE", "rule",
      "ToString renders a ternary value as its number, and ERR as \"ERR\".",
      expect="run:0",
      src=prog_("""    tryte:t = 1T1T0t;
    string:s = `&{ t }`;
%s
    nit:n = 0 - 3;
    string:u = `&{ n }`;
%s
    tryte:e = ERR;
    string:w = `&{ e }`;
%s
    exit 0i32;""" % (chk('string_equals(s, "60")', 10), chk('string_equals(u, "-3")', 11),
                     chk('string_equals(w, "ERR")', 12))),
      wrong="refused, or 10-12: digits or the carrier rendered")

# ================================================================== 8. flag types
claim("ty0825", D, 825, "`PROT_READ` where an `oflags` belongs", "rule",
      "Each flag family is a distinct type: `PROT_READ` where an `oflags` belongs is refused.",
      expect="refuse",
      src=prog_("""    oflags:f = PROT_READ;
    if ((f => int32) != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0830", D, 830, "Every family lowers to `i32`.", "rule",
      "Every flag family lowers to `i32`: a parameter of each of the four families is an `i32`.",
      expect=ir_all(param("m11o", "i32"), param("m11p", "i32"), param("m11m", "i32"), param("m11f", "i32")),
      src=prog_("""    oflags:a = raw m11o(O_APPEND);
    prot:b = raw m11p(PROT_READ);
    mflags:c = raw m11m(MAP_SHARED);
    fmode:d = raw m11f(S_IRUSR);
    if (a != O_APPEND) { exit 10i32; }
    if (b != PROT_READ) { exit 11i32; }
    if (c != MAP_SHARED) { exit 12i32; }
    if (d != S_IRUSR) { exit 13i32; }
    exit 0i32;""", """func:m11o = oflags(oflags:x) never fails { pass x; };
func:m11p = prot(prot:x) never fails { pass x; };
func:m11m = mflags(mflags:x) never fails { pass x; };
func:m11f = fmode(fmode:x) never fails { pass x; };"""),
      wrong="another carrier")
claim("ty0832", D, 832, "`|` combines, `&` tests, `~` complements", "rule",
      "Within one family `|` combines, `&` tests and `~` complements, each giving that family; `==`/`!=` compare.",
      expect="run:0",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) | O_CLOEXEC;
    oflags:t = f & O_CLOEXEC;
    if (t != O_CLOEXEC) { exit 10i32; }
    oflags:g = f & (~O_CLOEXEC);
    if (g != O_WRONLY) { exit 11i32; }
    if ((f => int32) != 524289i32) { exit 12i32; }
    if (f == O_WRONLY) { exit 13i32; }
    exit 0i32;"""),
      wrong="refused, or 10-13: a wrong set")
claim("ty0833", D, 833, "There is no arithmetic", "rule",
      "There is no arithmetic on flags: `O_WRONLY + O_APPEND` is refused.", expect="refuse",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) + O_APPEND;
    if ((f => int32) != 1025i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0834", D, 834, "ordering, no `^` and no shifts", "rule",
      "There is no ordering on flags: `O_WRONLY < O_APPEND` is refused.", expect="refuse",
      src=prog_("""    if (raw vox(O_WRONLY) < O_APPEND) { exit 0i32; }
    exit 10i32;"""),
      wrong="accepted")
claim("ty0834b", D, 834, "ordering, no `^` and no shifts", "rule",
      "There is no `^` on flags.", expect="refuse",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) ^ O_APPEND;
    if ((f => int32) != 1025i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0834c", D, 834, "ordering, no `^` and no shifts", "rule",
      "There are no shifts on flags: `O_WRONLY << 1` is refused.", expect="refuse",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) << 1i32;
    if ((f => int32) != 2i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0835", D, 835, "`oflags | prot` refuses", "rule",
      "Two families never meet: `oflags | prot` is refused, TYPE-058.", expect="refuse:NITPICK-TYPE-058",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) | PROT_READ;
    if ((f => int32) != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0836", D, 836, "as does `O_RDONLY | 1i32`", "rule",
      "An integer is not a member: `O_RDONLY | 1i32` is refused, TYPE-058.", expect="refuse:NITPICK-TYPE-058",
      src=prog_("""    oflags:f = raw vox(O_RDONLY) | 1i32;
    if ((f => int32) != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0838", D, 838, "`flags => int32` is the one outbound conversion", "rule",
      "`flags => int32` converts losslessly: the word is the members' sum.",
      expect="run:0",
      src=prog_("""    oflags:f = raw vox(O_APPEND) | O_CREAT;
    int32:w = f => int32;
    if (w != 1088i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty0838b", D, 838, "is the one outbound conversion", "rule",
      "`=> int32` is the only outbound conversion: `flags => int64` is refused.", expect="refuse",
      src=prog_("""    int64:w = raw vox(O_APPEND) => int64;
    if (w != 1024i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0840", D, 840, "`int32 =>! flags` is the read-back direction", "rule",
      "`int32 =>! flags` reads a word back into the family.",
      expect="run:0",
      src=prog_("""    int32:w = raw v32(1024i32);
    oflags:f = w =>! oflags;
    if (f != O_APPEND) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty0841b", D, 841, "so it takes the bang", "rule",
      "The read-back takes the bang: `int32 => flags` is refused.", expect="refuse",
      src=prog_("""    int32:w = raw v32(1024i32);
    oflags:f = w => oflags;
    if (f != O_APPEND) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0841", D, 841, "Nothing else enters or leaves", "rule",
      "Nothing else enters: `int64 =>! oflags` is refused.", expect="refuse",
      src=prog_("""    int64:w = raw v64(1024i64);
    oflags:f = w =>! oflags;
    if (f != O_APPEND) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0842", D, 842, "family never converts to another", "rule",
      "A family never converts to another: `oflags =>! prot` is refused.", expect="refuse",
      src=prog_("""    prot:p = raw vox(O_WRONLY) =>! prot;
    if (p != PROT_READ) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0844", D, 844, "**Members.** The named bits are **prelude constants**, `pub fixed", "rule",
      "The members are `fixed` prelude constants: assigning to `O_APPEND` is refused.", expect="refuse",
      src=prog_("""    O_APPEND = O_RDONLY;
    exit 0i32;"""),
      wrong="accepted: a prelude member rebound")
claim("ty0846", D, 846, "`src/prelude/prelude.npk`'s marked region from the table below by", "rule",
      "The members are generated into the prelude by `gen_tables.py`, with the family indices and the "
      "builtin-type table.",
      untestable="[tree] how the compiler's tree generates its prelude")
claim("ty0849", D, 849, "authority; a member added here exists everywhere the prelude is bound", "rule",
      "A member exists in every module, since the prelude is bound in every module.",
      expect="run:0",
      files={"m11fl.npk": """mod:m11fl;

pub func:word = int32() never fails { pass (O_EXCL => int32); };"""},
      src=prog_("""    if (raw m11fl.word() != 128i32) { exit 10i32; }
    if ((O_EXCL => int32) != 128i32) { exit 11i32; }
    exit 0i32;""", "mod:m11fl;"),
      wrong="refused in the second module, or 10/11")
claim("ty0850", D, 850, "A derived set is an ordinary module binding", "rule",
      "A derived set is an ordinary module binding that folds: `fixed oflags:CREATE_RW = (O_RDWR | O_CREAT) | "
      "O_CLOEXEC;` is the word 524354.",
      expect="run:0",
      src=prog_("""    if ((CREATE_RW => int32) != 524354i32) { exit 10i32; }
    exit 0i32;""", "fixed oflags:CREATE_RW = (O_RDWR | O_CREAT) | O_CLOEXEC;"),
      wrong="refused, or 10")
claim("ty0853", D, 853, "The four that are bitmasks by nature", "rule",
      "There are four flag families: oflags, prot, mflags and fmode.",
      untestable="[unobservable] that no fifth family exists; each of the four is tested (ty0830)")
claim("ty0854", D, 854, "`whence` is the prelude enum `Whence`", "rule",
      "`whence` is the prelude enum `Whence`: `Whence.SEEK_END` is a value a pick can match.",
      expect="run:0",
      src=prog_("""    Whence:w = Whence.SEEK_END;
    int32:r = 0i32;
    pick (w) { (Whence.SEEK_END) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no such enum or member), or 10")
claim("ty0855", D, 855, "OR-ed — a flags type would admit `SEEK_SET | SEEK_END`", "rule",
      "A `Whence` is exactly one value: `Whence.SEEK_SET | Whence.SEEK_END` is refused.", expect="refuse",
      src=prog_("""    Whence:w = Whence.SEEK_SET | Whence.SEEK_END;
    exit 0i32;"""),
      wrong="accepted")
claim("ty0855b", D, 855, "`fcmd`/`advice`", "rule",
      "`fcmd` and `advice` are enumerations, not flag types.",
      untestable="[vague] the text names no member of either, so no program can spell one")
claim("ty0857", D, 857, "The family INDEX is the type's `a` operand", "rule",
      "The family index is the type's `a` operand, in the table's order of first appearance.",
      untestable="[internal] a type's operand window")

FLAGS = [(864, "oflags", "O_RDONLY", 0), (865, "oflags", "O_WRONLY", 1), (866, "oflags", "O_RDWR", 2),
         (867, "oflags", "O_CREAT", 64), (868, "oflags", "O_EXCL", 128), (869, "oflags", "O_NOCTTY", 256),
         (870, "oflags", "O_TRUNC", 512), (871, "oflags", "O_APPEND", 1024),
         (872, "oflags", "O_NONBLOCK", 2048), (873, "oflags", "O_DSYNC", 4096),
         (874, "oflags", "O_DIRECTORY", 65536), (875, "oflags", "O_NOFOLLOW", 131072),
         (876, "oflags", "O_CLOEXEC", 524288), (877, "oflags", "O_SYNC", 1052672),
         (878, "oflags", "O_PATH", 2097152), (879, "prot", "PROT_NONE", 0), (880, "prot", "PROT_READ", 1),
         (881, "prot", "PROT_WRITE", 2), (882, "prot", "PROT_EXEC", 4), (883, "mflags", "MAP_SHARED", 1),
         (884, "mflags", "MAP_PRIVATE", 2), (885, "mflags", "MAP_FIXED", 16),
         (886, "mflags", "MAP_ANONYMOUS", 32), (887, "mflags", "MAP_NORESERVE", 16384),
         (888, "mflags", "MAP_POPULATE", 32768), (889, "mflags", "MAP_FIXED_NOREPLACE", 1048576),
         (890, "fmode", "S_NONE", 0), (891, "fmode", "S_IXOTH", 1), (892, "fmode", "S_IWOTH", 2),
         (893, "fmode", "S_IROTH", 4), (894, "fmode", "S_IRWXO", 7), (895, "fmode", "S_IXGRP", 8),
         (896, "fmode", "S_IWGRP", 16), (897, "fmode", "S_IRGRP", 32), (898, "fmode", "S_IRWXG", 56),
         (899, "fmode", "S_IXUSR", 64), (900, "fmode", "S_IWUSR", 128), (901, "fmode", "S_IRUSR", 256),
         (902, "fmode", "S_IRWXU", 448), (903, "fmode", "S_ISVTX", 512), (904, "fmode", "S_ISGID", 1024),
         (905, "fmode", "S_ISUID", 2048)]
for ln, fam, mem, val in FLAGS:
    claim("ty%04d" % ln, D, ln, "| `%s` | `%s` | %d |" % (fam, mem, val), "row",
          "`%s` is a `%s` member whose word is %d." % (mem, fam, val),
          expect="run:0",
          src=prog_("""    %s:m = %s;
    if ((m => int32) != %di32) { exit 10i32; }
    exit 0i32;""" % (fam, mem, val)),
          wrong="refused (no such member, or another family), or 10: another value")
claim("ty0864b", D, 864, "so `f & O_RDONLY == O_RDONLY` always", "row",
      "`O_RDONLY` is the empty set: `f & O_RDONLY == O_RDONLY` for any f.",
      expect="run:0",
      src=prog_("""    oflags:f = raw vox(O_WRONLY) | O_APPEND;
    if ((f & O_RDONLY) != O_RDONLY) { exit 10i32; }
    exit 0i32;"""),
      wrong="10")
claim("ty0894b", D, 894, "| `fmode` | `S_IRWXO` | 7 | others: all three |", "row",
      "S_IRWXO is S_IROTH | S_IWOTH | S_IXOTH; S_IRWXU likewise for the owner.",
      expect="run:0",
      src=prog_("""    fmode:a = S_IROTH | S_IWOTH | S_IXOTH;
    if (a != S_IRWXO) { exit 10i32; }
    fmode:b = S_IRUSR | S_IWUSR | S_IXUSR;
    if (b != S_IRWXU) { exit 11i32; }
    exit 0i32;"""),
      wrong="10/11")
claim("ty0909", D, 909, "The lowering is pinned in `tests/backend/ir_types.npk`", "rule",
      "The lowering, the rules and the executed semantics are pinned by three named tests of the compiler's tree.",
      untestable="[tree] the compiler's own tests")

# ================================================================== 9.1 structs
MYSTRUCT = "struct:MyStruct = { int32:x; int64:y; bool:flag; };"
claim("ty0921", D, 921, "```nitpick", "example",
      "The struct example compiles as written.", expect="compile",
      src=prog_("    exit 0i32;", "struct MyStruct = { int32:x; int64:y; bool:flag; };"),
      wrong="refused (the declaration's spelling)")
claim("ty0925", D, 925, "```llvm", "example",
      "MyStruct is laid out with C padding: 24 bytes, alignment 8.",
      expect="run:0", src=layout(["MyStruct"], 24, 8, decls=MYSTRUCT), wrong=layout_wrong("MyStruct", 24, 8))
claim("ty0926", D, 926, "%MyStruct = type { i32, i64, i8 }", "rule",
      "MyStruct's LLVM type is `{ i32, i64, i8 }`.",
      expect=r'ir:(?m)^%"?[^"\n]*MyStruct"? = type \{ i32, i64, i8 \}',
      src=prog_("""    MyStruct:s = MyStruct{ x: 1i32, y: 2i64, flag: true };
    if (s.y != 2i64) { exit 10i32; }
    exit 0i32;""", MYSTRUCT),
      wrong="another field order or carrier (bool as i1)")
claim("ty0936", D, 936, "```llvm", "example",
      "Reading `obj.y` is a `getelementptr` to field index 1 and an `i64` load.",
      expect=ir_fn("m11gy", r"getelementptr[^\n]*, i32 0, i32 1\b", r"load i64"),
      src=prog_("""    MyStruct:s = MyStruct{ x: 1i32, y: 2i64, flag: true };
    if (raw m11gy(@s) != 2i64) { exit 10i32; }
    exit 0i32;""", MYSTRUCT + "\nfunc:m11gy = int64(MyStruct->:obj) never fails { pass obj.y; };"),
      wrong="another access shape")

BANK = """mod:bank = {
    pub struct:Acct = {
        sealed int64:bal;
        hidden int64:pin;
        int64:note;
    };
    pub func:deposit = NIL(Acct->:a, int64:n) never fails { a.bal += n; pass NIL; };
    pub func:mk = Acct() never fails { Acct:a = Acct{ bal: 5i64, pin: 9i64, note: 1i64 }; pass a; };
};
use bank.{Acct};"""


def outside(body, extra=BANK):
    """a program whose `main` is outside module `bank`"""
    return prog_(body, extra)


claim("ty0946", D, 946, "A generic struct's qualifiers, and its module, are its", "rule",
      "A generic struct's qualifiers are its template's: a sealed `T` field of `Box<int64>` is refused a "
      "write from outside, TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Box<int64>:b = raw bank.mk();
    b.v = raw v64(6i64);
    exit 0i32;""", """mod:bank = {
    pub struct:Box<T> = { sealed T:v; };
    pub func:mk = Box<int64>() never fails { Box<int64>:b = Box{ v: 5i64 }; pass b; };
};
use bank.{Box};"""),
      wrong="accepted")
claim("ty0949", D, 949, "```nitpick", "example",
      "The `bank` example compiles.", expect="compile",
      src=prog_("    exit 0i32;", """mod:bank = {
    pub struct:Acct = {
        sealed int64:bal;     // read anywhere; written only inside `bank`
        hidden int64:pin;     // neither read nor written outside `bank`
        int64:note;           // anyone
    };
    pub func:deposit = NIL(Acct->:a, int64:n) never fails { a.bal += n; pass NIL; };
};"""),
      wrong="refused")
claim("ty0952", D, 952, "read anywhere; written only inside `bank`", "rule",
      "A sealed field is read outside its module and written inside it: `a.bal` reads 5, and after "
      "`bank.deposit(@a, 3)` reads 8.",
      expect="run:0",
      src=outside("""    Acct:a = raw bank.mk();
    if (a.bal != 5i64) { exit 10i32; }
    drop bank.deposit(@a, raw v64(3i64));
    if (a.bal != 8i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty0953", D, 953, "neither read nor written outside `bank`", "rule",
      "A hidden field is not read outside its module: TYPE-080.", expect="refuse:NITPICK-TYPE-080",
      src=outside("""    Acct:a = raw bank.mk();
    if (a.pin != 9i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0954", D, 954, "int64:note;           // anyone", "rule",
      "An unqualified field is written and read by anyone.",
      expect="run:0",
      src=outside("""    Acct:a = raw bank.mk();
    a.note = raw v64(7i64);
    if (a.note != 7i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty0960", D, 960, "refuses every WRITE from outside, `NITPICK-TYPE-079`", "rule",
      "A sealed field's assignment from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Acct:a = raw bank.mk();
    a.bal = raw v64(6i64);
    exit 0i32;"""),
      wrong="accepted")
claim("ty0962", D, 962, "including a part of a sealed value", "rule",
      "Writing a part of a sealed value (`h.inner.x`) from outside is TYPE-079.",
      expect="refuse:NITPICK-TYPE-079",
      src=outside("""    H:h = raw bank.mk();
    h.inner.x = raw v64(3i64);
    exit 0i32;""", """mod:bank = {
    pub struct:In = { int64:x; };
    pub struct:H = { sealed In:inner; int64:k; };
    pub func:mk = H() never fails { H:h = H{ inner: In{ x: 1i64 }, k: 2i64 }; pass h; };
};
use bank.{H, In};"""),
      wrong="accepted")
claim("ty0963", D, 963, "a sealed field reached through a pointer", "rule",
      "Writing a sealed field through a pointer from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Acct:a = raw bank.mk();
    Acct->:p = @a;
    p.bal = raw v64(6i64);
    exit 0i32;"""),
      wrong="accepted")
claim("ty0964", D, 964, "a compound assignment;", "rule",
      "A compound assignment to a sealed field from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Acct:a = raw bank.mk();
    a.bal += raw v64(1i64);
    exit 0i32;"""),
      wrong="accepted")
claim("ty0965", D, 965, "a struct literal naming the field;", "rule",
      "A struct literal naming a sealed field outside its module is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Wallet:w = Wallet{ bal: raw v64(1i64), note: 2i64 };
    if (w.note != 2i64) { exit 10i32; }
    exit 0i32;""", """mod:bank = {
    pub struct:Wallet = { sealed int64:bal; int64:note; };
};
use bank.{Wallet};"""),
      wrong="accepted")
claim("ty0966", D, 966, "a `move` or `pass` out of an OWNING sealed field", "rule",
      "A move out of an owning sealed field from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Named:n = raw bank.mk();
    string:s = move(n.name);
    if (!(string_equals(s, "abc"))) { exit 10i32; }
    exit 0i32;""", """mod:bank = {
    pub struct:Named = { sealed string:name; int64:k; };
    pub func:mk = Named() never fails { Named:n = Named{ name: "abc", k: 1i64 }; pass n; };
};
use bank.{Named};"""),
      wrong="accepted")
claim("ty0968", D, 968, "`@` and `$$m`;", "rule",
      "Taking `@` of a sealed field from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Acct:a = raw bank.mk();
    int64->:p = @a.bal;
    <-p = 7i64;
    exit 0i32;"""),
      wrong="accepted")
claim("ty0968b", D, 968, "`@` and `$$m`;", "rule",
      "Claiming a sealed field `$$m` from outside is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Acct:a = raw bank.mk();
    int64->:p = $$m a.bal;
    <-p = 7i64;
    exit 0i32;"""),
      wrong="accepted")
claim("ty0969", D, 969, "a call through a `Self->` receiver;", "rule",
      "A call through a `Self->` receiver on a sealed field from outside is TYPE-079.",
      expect="refuse:NITPICK-TYPE-079",
      src=outside("""    Box2:b = raw bank.mk();
    drop b.c.bump();
    exit 0i32;""", """mod:bank = {
    pub struct:Ctr = { int64:n; };
    pub trait:Bump = { func:bump = NIL(Self->:self) never fails; };
    impl:Ctr:Bump = { func:bump = NIL(Ctr->:self) never fails { self.n += 1i64; pass NIL; }; };
    pub struct:Box2 = { sealed Ctr:c; };
    pub func:mk = Box2() never fails { Box2:b = Box2{ c: Ctr{ n: 0i64 } }; pass b; };
};
use bank.{Box2, Ctr, Bump};"""),
      wrong="accepted")
claim("ty0970", D, 970, "any operation on a stateful value, which writes through its address", "rule",
      "Any operation on a stateful sealed value is a write.",
      untestable="[vague] which values are stateful, and which operations, is not named here")
claim("ty0973", D, 973, "A read, a copy out, a `$$i` claim (D-286 holds it read-only)", "rule",
      "A read, a copy out and a `$$i` claim of a sealed field pass outside its module.",
      expect="run:0",
      src=outside("""    Acct:a = raw bank.mk();
    int64:c = a.bal;
    int64->:q = $$i a.bal;
    int64:r = <-q;
    if (c != 5i64) { exit 10i32; }
    if (r != 5i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty0974", D, 974, "THROUGH a sealed pointer field all pass", "rule",
      "A write through a sealed pointer field passes outside its module: it writes the pointee.",
      expect="run:0",
      src=outside("""    int64:x = raw v64(1i64);
    Pf:f = raw bank.mk(@x);
    <-f.p = 7i64;
    if (x != 7i64) { exit 10i32; }
    exit 0i32;""", """mod:bank = {
    pub struct:Pf = { sealed int64->:p; int64:k; };
    pub func:mk = Pf(int64->:t) never fails { Pf:r = Pf{ p: t, k: 1i64 }; pass r; };
};
use bank.{Pf};"""),
      wrong="refused, or 10: the write lost")
claim("ty0976", D, 976, "refuses every touch from outside, read or write", "rule",
      "Writing a hidden field from outside is TYPE-080.", expect="refuse:NITPICK-TYPE-080",
      src=outside("""    Acct:a = raw bank.mk();
    a.pin = raw v64(1i64);
    exit 0i32;"""),
      wrong="accepted")
SEC = """mod:bank = {
    pub struct:Sec = { hidden int64:pin; int64:note; };
    pub func:mk = Sec() never fails { Sec:s = Sec{ pin: 9i64, note: 1i64 }; pass s; };
};
use bank.{Sec};"""
claim("ty0977", D, 977, "a struct literal naming", "rule",
      "A struct literal naming a hidden field outside its module is TYPE-080.", expect="refuse:NITPICK-TYPE-080",
      src=outside("""    Sec:s = Sec{ pin: raw v64(1i64), note: 2i64 };
    if (s.note != 2i64) { exit 10i32; }
    exit 0i32;""", SEC),
      wrong="accepted")
claim("ty0978", D, 978, "it, a struct pattern binding it", "rule",
      "A struct pattern binding a hidden field outside its module is TYPE-080.", expect="refuse:NITPICK-TYPE-080",
      src=outside("""    Sec:s = raw bank.mk();
    int64:r = 0i64;
    pick (s) { (Sec { pin }) { r = pin; } }
    if (r != 9i64) { exit 10i32; }
    exit 0i32;""", SEC),
      wrong="accepted")
claim("ty0978b", D, 978, "it, a struct pattern binding it", "rule",
      "A struct pattern binding an unqualified field outside its module is accepted (the twin of ty0978).",
      expect="run:0",
      src=outside("""    Sec:s = raw bank.mk();
    int64:r = 0i64;
    pick (s) { (Sec { note }) { r = note; } }
    if (r != 1i64) { exit 10i32; }
    exit 0i32;""", SEC),
      wrong="refused, or 10")
claim("ty0980", D, 980, "On a local, a parameter, a module binding or", "rule",
      "`sealed` on a local is TYPE-081.", expect="refuse:NITPICK-TYPE-081",
      src=prog_("""    sealed int64:x = raw v64(5i64);
    if (x != 5i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0980b", D, 980, "On a local, a parameter, a module binding or", "rule",
      "`hidden` on a parameter is TYPE-081.", expect="refuse:NITPICK-TYPE-081",
      src=prog_("""    if (raw m11h(raw v64(5i64)) != 5i64) { exit 10i32; }
    exit 0i32;""", "func:m11h = int64(hidden int64:x) never fails { pass x; };"),
      wrong="accepted")
claim("ty0981", D, 981, "a cast target, or both on one field, the qualifier is `NITPICK-TYPE-081`", "rule",
      "`sealed` and `hidden` both on one field is TYPE-081.", expect="refuse:NITPICK-TYPE-081",
      src=prog_("""    S:s = S{ v: 1i64 };
    if (s.v != 1i64) { exit 10i32; }
    exit 0i32;""", "struct:S = { sealed hidden int64:v; };"),
      wrong="accepted")
claim("ty0982", D, 982, "`for` binding takes no qualifier at all", "rule",
      "A `for` binding takes no qualifier: `for (sealed int64:i in …)` is refused.", expect="refuse",
      src=prog_("""    int64:t = 0i64;
    for (sealed int64:i in 0i64...3i64) { t = t + i; }
    if (t != 3i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty0984", D, 984, "`ptr`, `len` and `cap` of a `string`, a `cstring`, a slice and a `buffer`", "rule",
      "A string's `len` is sealed in every module: `s.len = s.len` is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=prog_("""    string:s = "abcdef";
    s.len = s.len;
    exit 0i32;"""),
      wrong="accepted (DEF-72's shape)")
claim("ty0984b", D, 984, "`ptr`, `len` and `cap` of a `string`, a `cstring`, a slice and a `buffer`", "rule",
      "A slice's `len` is sealed in every module: writing it is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32[]:v = arr[0i64...2i64];
    v.len = 4i64;
    exit 0i32;"""),
      wrong="accepted")
claim("ty0987", D, 987, "An `OwnedFd`'s `.value`, the descriptor its drop closes.", "rule",
      "An OwnedFd's `.value` is sealed in every module: writing it is TYPE-079.", expect="refuse:NITPICK-TYPE-079",
      src=prog_("    exit 0i32;", "func:m11p = NIL(OwnedFd->:f) never fails { f.value = f.value; pass NIL; };"),
      wrong="accepted")
claim("ty0993", D, 993, "**An `RGuard`'s `.value` is read-only at every write form**", "rule",
      "An RGuard's `.value` is read-only: assigning it is TYPE-007.", expect="refuse:NITPICK-TYPE-007",
      src=prog_("    exit 0i32;", "func:m11g = NIL(RGuard<int64>->:g) never fails { g.value = 1i64; pass NIL; };"),
      wrong="accepted")

# ------------------------------------------------------------------ 9.1.2 limit fields
LEVEL = "Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };"
TANK = LEVEL + "\nstruct:Tank = {\n    sealed limit<r_level> int64:n;\n    int64:serial;\n};"
claim("ty1002", D, 1002, "```", "example",
      "The limited-field example compiles.", expect="compile",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    if (t.n != 5i64) { exit 10i32; }
    exit 0i32;""", TANK),
      wrong="refused")
claim("ty1012", D, 1012, "Struct-wide relational rules (`$.count <= $.cap`) are decided", "rule",
      "Struct-wide relational field rules are decided out.",
      untestable="[vague] a decision against a feature; the subject rule (ty1017) is what refuses one")
claim("ty1017", D, 1017, "**The subject is the field's type by identity**", "rule",
      "A field rule's subject is the field's type by identity: a `Rules<int32>` on an int64 field is TYPE-059.",
      expect="refuse:NITPICK-TYPE-059",
      src=prog_("""    S:s = S{ n: 5i64 };
    if (s.n != 5i64) { exit 10i32; }
    exit 0i32;""", "Rules<int32>:r_small = { $ >= 0i32 };\nstruct:S = { limit<r_small> int64:n; };"),
      wrong="accepted (a widening)")
claim("ty1019", D, 1019, "limited field of a generic struct's `T` refuses", "rule",
      "A limited field of a generic struct's `T` is refused (TYPE-059).", expect="refuse:NITPICK-TYPE-059",
      src=prog_("""    G<int64>:g = G{ v: 5i64 };
    if (g.v != 5i64) { exit 10i32; }
    exit 0i32;""", LEVEL + "\nstruct:G<T> = { limit<r_level> T:v; };"),
      wrong="accepted")
claim("ty1020", D, 1020, "**The rule must hold of the field's VACANT value** (`NITPICK-TYPE-077`)", "rule",
      "A field rule that its vacant value (0) breaks is TYPE-077.", expect="refuse:NITPICK-TYPE-077",
      src=prog_("""    S:s = S{ n: 5i64 };
    if (s.n != 5i64) { exit 10i32; }
    exit 0i32;""", "Rules<int64>:r_pos = { $ > 0i64 };\nstruct:S = { limit<r_pos> int64:n; };"),
      wrong="accepted: a vacant field holds 0, which no check sees")
claim("ty1024", D, 1024, "the rule at the declaration with `$` bound to it — 0 for a plain integer,", "rule",
      "A bool field's vacant value is false: a rule `$ == true` on it is TYPE-077.",
      expect="refuse:NITPICK-TYPE-077",
      src=prog_("""    S:s = S{ b: true };
    if (!(s.b)) { exit 10i32; }
    exit 0i32;""", "Rules<bool>:r_t = { $ == true };\nstruct:S = { limit<r_t> bool:b; };"),
      wrong="accepted")
claim("ty1025", D, 1025, "a rule it cannot decide there is refused too", "rule",
      "A field rule the folder cannot decide at the declaration is refused.",
      untestable="[vague] what the folder cannot decide is not stated")
claim("ty1026", D, 1026, "Only a plain integer, a `bool` or a `char`", "rule",
      "A field rule on another subject (flt64) is refused with the vacant-value reason, TYPE-077.",
      expect="refuse:NITPICK-TYPE-077",
      src=prog_("""    S:s = S{ x: 1.5f64 };
    if (s.x != 1.5f64) { exit 10i32; }
    exit 0i32;""", "Rules<flt64>:r_f = { $ >= 0.0f64 };\nstruct:S = { limit<r_f> flt64:x; };"),
      wrong="accepted")
claim("ty1029", D, 1029, "**The write points**, each checked after the write in EVERY build", "rule",
      "In-range writes at every write point pass: a literal of 5, an assignment of 50, a write of 60 through "
      "a pointer and `+= 40`.",
      expect="run:0",
      src=prog_("""    Tank:t = Tank{ n: raw v64(5i64), serial: 1i64 };
    t.n = raw v64(50i64);
    Tank->:p = @t;
    p.n = raw v64(60i64);
    t.n += raw v64(40i64);
    if (t.n != 100i64) { exit 10i32; }
    exit 0i32;""", TANK),
      wrong="a trap, or 10")
claim("ty1031", D, 1031, "a struct literal's value for the field;", "rule",
      "A struct literal's out-of-rule value for a limited field traps LimitViolated.", expect="trap:LimitViolated",
      src=prog_("""    Tank:t = Tank{ n: raw v64(101i64), serial: 1i64 };
    if (t.n == 101i64) { exit 10i32; }
    exit 11i32;""", TANK),
      wrong="the value stored (10)")
claim("ty1032", D, 1032, "an assignment to the field through ANY path", "rule",
      "An assignment of an out-of-rule value to a limited field traps LimitViolated.", expect="trap:LimitViolated",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    t.n = raw v64(-1i64);
    if (t.n == -1i64) { exit 10i32; }
    exit 11i32;""", TANK),
      wrong="the value stored (10)")
claim("ty1033", D, 1033, "pointer `p.f = v`, since the rule is the field's wherever its struct lives", "rule",
      "An out-of-rule write through a pointer to the struct traps LimitViolated.", expect="trap:LimitViolated",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    Tank->:p = @t;
    p.n = raw v64(200i64);
    if (t.n == 200i64) { exit 10i32; }
    exit 11i32;""", TANK),
      wrong="the value stored (10)")
claim("ty1034", D, 1034, "a compound assignment, `s.f += v`.", "rule",
      "A compound assignment that leaves the rule traps LimitViolated.", expect="trap:LimitViolated",
      src=prog_("""    Tank:t = Tank{ n: 90i64, serial: 1i64 };
    t.n += raw v64(20i64);
    if (t.n == 110i64) { exit 10i32; }
    exit 11i32;""", TANK),
      wrong="the value stored (10)")
claim("ty1035", D, 1035, "**A limited field has no address** (`NITPICK-TYPE-063`", "rule",
      "`@s.f` of a limited field is TYPE-063.", expect="refuse:NITPICK-TYPE-063",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    int64->:q = @t.n;
    <-q = 500i64;
    exit 0i32;""", TANK),
      wrong="accepted: a write no write point sees")
claim("ty1036", D, 1036, "`@s.f`, `$$i`/`$$m` of it", "rule",
      "`$$m` of a limited field is TYPE-063.", expect="refuse:NITPICK-TYPE-063",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    int64->:q = $$m t.n;
    <-q = 500i64;
    exit 0i32;""", TANK),
      wrong="accepted")
claim("ty1036b", D, 1036, "`@s.f`, `$$i`/`$$m` of it", "rule",
      "`$$i` of a limited field is TYPE-063.", expect="refuse:NITPICK-TYPE-063",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    int64->:q = $$i t.n;
    int64:r = <-q;
    if (r != 5i64) { exit 10i32; }
    exit 0i32;""", TANK),
      wrong="accepted")
claim("ty1037", D, 1037, "through a pointer to the struct as well", "rule",
      "`@p.f` of a limited field through a pointer to its struct is TYPE-063.", expect="refuse:NITPICK-TYPE-063",
      src=prog_("""    Tank:t = Tank{ n: 5i64, serial: 1i64 };
    Tank->:p = @t;
    int64->:q = @p.n;
    <-q = 500i64;
    exit 0i32;""", TANK),
      wrong="accepted")
claim("ty1038", D, 1038, "A write through `wild` storage is the author's", "rule",
      "A write through wild storage is unchecked.",
      untestable="[unobservable] an opt-out promises nothing a program could check")
claim("ty1040", D, 1040, "**Every read is a fact**", "rule",
      "Every read of a limited field is a hypothesis for the rows after it.",
      untestable="[z3] a hypothesis matters only to the solver's verdicts")
claim("ty1045", D, 1045, "The verified build elides a write point's check where its `limit` row", "rule",
      "The verified build elides a write point's check where its limit row discharges.",
      untestable="[z3] needs `npkg verify` with the pinned z3")

# ================================================================== 9.2 fixed arrays
claim("ty1050", D, 1050, "Passing `int32[4]` to a function copies all 16 bytes", "rule",
      "Passing a fixed array copies it.", m10="a02_array_argument_copies")
claim("ty1050b", D, 1050, "Fixed arrays are **Value Types**, not references", "rule",
      "Assigning a fixed array copies it.", m10="a01_array_assignment_copies")
claim("ty1050c", D, 1050, "explicitly pass a pointer to it (`int32[4]->`)", "rule",
      "A write through an `int32[4]->` reaches the caller's array.", m10="a06_write_through_array_pointer")
claim("ty1050d", D, 1050, "They do NOT implicitly decay to pointers like in C", "rule",
      "A fixed array does not decay to a pointer: passing `int32[4]` where `int32->` is expected is refused.",
      expect="refuse",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    if (raw m11f(arr) != 1i32) { exit 10i32; }
    exit 0i32;""", "func:m11f = int32(int32->:p) never fails { pass <-p; };"),
      wrong="accepted: an implicit decay")
claim("ty1052", D, 1052, "```nitpick", "example",
      "`int32[4]:arr = [1i32, 2i32, 3i32, 4i32];` holds 1, 2, 3, 4.",
      expect="run:0",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    if (arr[0i64] != 1i32) { exit 10i32; }
    if (arr[raw v64(3i64)] != 4i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1056", D, 1056, "```llvm", "example",
      "A local `int32[4]` is an `alloca [4 x i32]`, and an index is checked `icmp ult i64 %idx, 4` before a "
      "`getelementptr [4 x i32]`.",
      expect=ir_fn("m11ix", r"alloca \[4 x i32\]", r"icmp ult i64 %[^,\n]+, 4\b", r"getelementptr[^\n]*\[4 x i32\]"),
      src=prog_("""    if (raw m11ix(raw v64(2i64)) != 3i32) { exit 10i32; }
    exit 0i32;""", """func:m11ix = int32(int64:i) never fails {
    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    pass arr[i];
};"""),
      wrong="another check (a signed compare, or none) or another access")
claim("ty1058", D, 1058, "; Element access (bounds-checked):", "rule",
      "An index past the end traps OutOfBounds.", m10="a03_index_past_end")
claim("ty1061", D, 1061, "%in_bounds = icmp ult i64 %idx, 4", "rule",
      "A negative index traps OutOfBounds (the unsigned compare).", m10="a04_index_negative")
claim("ty1068", D, 1068, "**A zero-length fixed array `T[0]` is a supported type**", "rule",
      "`T[0]` is accepted and zero bytes wide: a struct holding only an `int64[0]` is 0 bytes.",
      expect="run:0",
      src=prog_("""    int64[0]:e = [];
    if (e.len != 0i64) { exit 10i32; }
    if (#size_of<Z>() != 0i64) { exit 11i32; }
    exit 0i32;""", "struct:Z = { int64[0]:e; };"),
      wrong="refused, or 10/11")
claim("ty1070", D, 1070, "OWNING when `T` owns", "rule",
      "A struct with a `hidden string[0]` field is move-only: copying it is TYPE-046.",
      expect="refuse:NITPICK-TYPE-046",
      src=prog_("""    M:a = M{ tag: [], v: 1i64 };
    M:b = a;
    if (b.v != 1i64) { exit 10i32; }
    exit 0i32;""", "struct:M = { hidden string[0]:tag; int64:v; };"),
      wrong="accepted: the copy")
claim("ty1072", D, 1072, "while `int64[0]` copies freely", "rule",
      "A struct with an `int64[0]` field copies freely.",
      expect="run:0",
      src=prog_("""    C:a = C{ tag: [], v: 1i64 };
    C:b = a;
    if (b.v != 1i64) { exit 10i32; }
    if (a.v != 1i64) { exit 11i32; }
    exit 0i32;""", "struct:C = { int64[0]:tag; int64:v; };"),
      wrong="refused (TYPE-046), or 10/11")
claim("ty1075", D, 1075, "`arr.len` is the count the type carries", "rule",
      "`arr.len` is the array's count.", m10="a05_array_len")
claim("ty1077", D, 1077, "a local `uint8[20]` asking its length", "rule",
      "A local `uint8[20]` asking its length compiles, and the length is 20.",
      expect="run:0",
      src=prog_("""    uint8[20]:b = [];
    int64:n = b.len;
    if (n != 20i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (DEF-22's internal-defect refusal), or 10")

# ------------------------------------------------------------------ 9.2.1 slices
claim("ty1084", D, 1084, "```llvm", "example",
      "A slice is `{ ptr, i64 }`: an `int32[]` parameter has that type.",
      expect="ir:(?m)" + param("m11sl", r"\{ ?ptr, i64 ?\}"),
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    if (raw m11sl(arr[0i64...3i64]) != 3i64) { exit 10i32; }
    exit 0i32;""", "func:m11sl = int64(int32[]:s) never fails { pass s.len; };"),
      wrong="another carrier")
claim("ty1088", D, 1088, "**Indexing is bounds-checked against the runtime `len`**", "rule",
      "A slice index past its own len traps OutOfBounds.", m10="a09_view_index_past_its_len")
claim("ty1088b", D, 1088, "**Indexing is bounds-checked against the runtime `len`**", "rule",
      "A byte view's index past its len traps OutOfBounds.", m10="t07_bytes_view_bounds")
claim("ty1092", D, 1092, "**`.len`** is available on every slice.", "rule",
      "`.len` is available on every slice: a range of an array and a range of a slice.",
      expect="run:0",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32[]:v = arr[raw v64(1i64)...4i64];
    int32[]:w = v[0i64...2i64];
    if (v.len != 3i64) { exit 10i32; }
    if (w.len != 2i64) { exit 11i32; }
    if (w[1i64] != 3i32) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
claim("ty1093", D, 1093, "**Every built-in length lies in `[0, 2^47]`, and the verifier knows it**", "rule",
      "Every built-in length lies in [0, 2^47], and the verifier pushes the fact at every read.",
      untestable="[z3] the fact matters to the solver's verdicts; the guard below is tested")
claim("ty1099", D, 1099, "2^47`, one unsigned compare, trapping `OutOfBounds` outside it", "rule",
      "`#wild_slice` guards the caller's count: a negative count traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=prog_("""    wild int8->:p = alloc(16i64);
    wild uint8->:u = p =>! wild uint8->;
    uint8[]:v = #wild_slice<uint8>(u, raw v64(-1i64));
    if (v.len == 7i64) { exit 10i32; }
    dalloc(p);
    exit 11i32;"""),
      wrong="a slice of length 2^64-1 (11)")
claim("ty1102", D, 1102, "`s.len + 1` cannot overflow an `int64` and its row discharges", "rule",
      "`s.len + 1`'s overflow row discharges.",
      untestable="[z3] a discharge is z3's verdict")
claim("ty1103", D, 1103, "The prelude's `List` carries the same bound as a", "rule",
      "A program that pushes to a List reaches the prelude's `limit<ListLen>` writes, so its failsafe must "
      "name LimitViolated: one that does not is refused.",
      expect="refuse",
      src=prog_("""    List<int64>:l = raw list_init::<int64>(4i64);
    drop list_push(@l, raw v64(1i64));
    exit 0i32;""", """func:failsafe = int32(Error:e) {
    pick (e) {
%s
        (*) { exit 99i32; }
    }
    exit 9i32;
};""" % "\n".join("        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS if n != "LimitViolated")),
      wrong="accepted: a failsafe that cannot name the List's own trap")
claim("ty1103b", D, 1103, "The prelude's `List` carries the same bound as a", "rule",
      "A program that pushes to a List, with a failsafe naming LimitViolated, compiles and runs.",
      expect="run:0",
      src=prog_("""    List<int64>:l = raw list_init::<int64>(4i64);
    drop list_push(@l, raw v64(1i64));
    exit 0i32;"""),
      wrong="refused")
claim("ty1107", D, 1107, "**A slice is a second-class borrow** (D-004)", "rule",
      "A slice never passes up the call stack: a function returning a slice is refused.", expect="refuse",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32[]:v = raw m11up(arr[0i64...2i64]);
    if (v.len != 2i64) { exit 10i32; }
    exit 0i32;""", "func:m11up = int32[](int32[]:s) never fails { pass s; };"),
      wrong="accepted: a view passed up")
claim("ty1111", D, 1111, "Constructed by ranging a fixed array or another slice", "rule",
      "Ranging a fixed array makes a slice of it.", m10="a08_range_view")
claim("ty1112", D, 1112, "`wild` context only, from a raw pointer and a length with", "rule",
      "`#wild_slice` is for wild context only: outside one it is refused.", expect="refuse",
      src=prog_("""    wild int8->:p = alloc(16i64);
    wild uint8->:u = p =>! wild uint8->;
    uint8[]:v = #wild_slice<uint8>(u, raw v64(4i64));
    if (v.len != 4i64) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted outside a wild context",
      note="BUILTIN's bi0418 calls #wild_slice in the same position (S42: D-315 struck the rule for it)")
claim("ty1117", D, 1117, "`T[]` **never owns**", "rule",
      "A slice never owns its elements.",
      untestable="[unobservable] a view's not-owning shows only as the absence of a free")
claim("ty1119", D, 1119, "A slice does not cross an `extern` boundary as a view", "rule",
      "A byte-slice parameter of an extern block is a sized payload the Bridge copies.",
      untestable="[tool] needs a driver behind an extern block")

# ================================================================== 9.3 enums
COLOR = "pub enum:Color = { Red = 0i32; Green = 1i32; Blue = 2i32; };"
SHAPE = "enum:Shape = { Circle(flt64); Rect(flt64, flt64); };"
claim("ty1126", D, 1126, "```nitpick", "example",
      "`Color`'s variants are the i32 tags 0, 1, 2.",
      expect="run:0",
      src=prog_("""    Color:c = Color.Green;
    if ((c =>! int32) != 1i32) { exit 10i32; }
    if ((Color.Blue =>! int32) != 2i32) { exit 11i32; }
    exit 0i32;""", COLOR),
      wrong="refused, or 10/11")
claim("ty1130", D, 1130, "```llvm", "example",
      "Enum values are plain i32 constants: a `Color` parameter is an `i32`.",
      expect="ir:(?m)" + param("m11c", "i32"),
      src=prog_("""    Color:c = raw m11c(Color.Blue);
    if ((c =>! int32) != 2i32) { exit 10i32; }
    exit 0i32;""", COLOR + "\nfunc:m11c = Color(Color:x) never fails { pass x; };"),
      wrong="another carrier")
claim("ty1136", D, 1136, "%Shape = type { i32, [2 x i64] }", "rule",
      "Shape is a tag and a two-i64 payload slot: 24 bytes, alignment 8.",
      expect="run:0", src=layout(["Shape"], 24, 8, decls=SHAPE), wrong=layout_wrong("Shape", 24, 8))
claim("ty1136b", D, 1136, "%Shape = type { i32, [2 x i64] }", "rule",
      "Shape's LLVM type is `{ i32, [2 x i64] }`.",
      expect=r'ir:(?m)^%"?[^"\n]*Shape"? = type \{ i32, \[2 x i64\] \}',
      src=prog_("""    Shape:s = Shape.Rect(1.0f64, 2.0f64);
    if ((s =>! int32) != 1i32) { exit 10i32; }
    exit 0i32;""", SHAPE),
      wrong="another slot")
claim("ty1137", D, 1137, "payload's alignment in bits, N covering the widest size", "rule",
      "The payload slot is [N x iK], K the widest payload's alignment in bits: for payloads int8 and "
      "(int32, int32) it is `[2 x i32]`.",
      expect=r'ir:(?m)^%"?[^"\n]*Ev"? = type \{ i32, \[2 x i32\] \}',
      src=prog_("""    Ev:e = Ev.B(1i32, 2i32);
    if ((e =>! int32) != 1i32) { exit 10i32; }
    exit 0i32;""", "enum:Ev = { A(int8); B(int32, int32); };"),
      wrong="another slot")
claim("ty1140", D, 1140, "`enum =>! intN` reads the TAG (slot 0) at every shape", "rule",
      "`enum =>! intN` reads the tag.", m10="c17_enum_to_int_reads_tag")
claim("ty1140b", D, 1140, "`enum =>! intN` reads the TAG (slot 0) at every shape", "rule",
      "`enum =>! intN` reads the tag of a payload-carrying enum: Shape.Rect is 1, Shape.Circle 0.",
      expect="run:0",
      src=prog_("""    Shape:r = Shape.Rect(raw vf64(1.0f64), 2.0f64);
    Shape:c = Shape.Circle(raw vf64(3.0f64));
    if ((r =>! int32) != 1i32) { exit 10i32; }
    if ((c =>! int32) != 0i32) { exit 11i32; }
    exit 0i32;""", SHAPE),
      wrong="refused, or 10/11: a payload word read")
claim("ty1142", D, 1142, "`intN =>! enum`, which manufactures a tag", "rule",
      "A tag-only enum takes `intN =>! enum`: 2 =>! Color is Blue.",
      expect="run:0",
      src=prog_("""    int32:i = raw v32(2i32);
    Color:c = i =>! Color;
    int32:r = 0i32;
    pick (c) { (Color.Blue) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;""", COLOR),
      wrong="refused, or 10")
claim("ty1142b", D, 1142, "hence the bang; `=>`", "rule",
      "`intN => enum` without the bang is TYPE-009.", expect="refuse:NITPICK-TYPE-009",
      src=prog_("""    int32:i = raw v32(2i32);
    Color:c = i => Color;
    exit 0i32;""", COLOR),
      wrong="accepted")
claim("ty1143", D, 1143, "a PAYLOAD-CARRYING enum like this `Shape` admits neither", "rule",
      "A payload-carrying enum admits no `intN =>! enum`: TYPE-032.", expect="refuse:NITPICK-TYPE-032",
      src=prog_("""    int32:i = raw v32(1i32);
    Shape:s = i =>! Shape;
    exit 0i32;""", SHAPE),
      wrong="accepted: a tag manufactured over no payload")
claim("ty1144", D, 1144, "spelling (TYPE-032)", "rule",
      "A payload-carrying enum admits no `intN => enum` either: TYPE-032.", expect="refuse:NITPICK-TYPE-032",
      src=prog_("""    int32:i = raw v32(1i32);
    Shape:s = i => Shape;
    exit 0i32;""", SHAPE),
      wrong="accepted, or another code")
OPT = "enum:Opt<T> = { Some(T); None; };"
claim("ty1150", D, 1150, "`enum:Opt<T> = { Some(T); None; };` is a template", "rule",
      "A generic enum is a template: `Opt<int32>` and `Opt<string>` are instances, constructed and matched.",
      expect="run:0",
      src=prog_("""    Opt<int32>:a = Opt.Some(raw v32(3i32));
    Opt<string>:b = Opt.Some("x");
    int32:r = 0i32;
    pick (a) { (Some(v)) { r = v; }, (Opt.None) { r = 9i32; } }
    if (r != 3i32) { exit 10i32; }
    int32:s = 0i32;
    pick (b) { (Some(t)) { s = 1i32; }, (Opt.None) { s = 2i32; } }
    if (s != 1i32) { exit 11i32; }
    exit 0i32;""", OPT),
      wrong="refused, or 10/11")
claim("ty1152", D, 1152, "header (`%\"…Opt<int32>\" = type { i32, [1 x i32] }`)", "rule",
      "`Opt<int32>` has its own header `{ i32, [1 x i32] }`.",
      expect=r'ir:(?m)^%"[^"\n]*Opt<int32>" = type \{ i32, \[1 x i32\] \}',
      src=prog_("""    Opt<int32>:a = Opt.Some(raw v32(3i32));
    int32:r = 0i32;
    pick (a) { (Some(v)) { r = v; }, (Opt.None) { r = 9i32; } }
    if (r != 3i32) { exit 10i32; }
    exit 0i32;""", OPT),
      wrong="another header")
claim("ty1153", D, 1153, "`Opt<int32>` is a tag", "rule",
      "`Opt<int32>` is a tag and four bytes: 8 bytes, alignment 4.",
      expect="run:0", src=layout(["Opt<int32>"], 8, 4, decls=OPT), wrong=layout_wrong("Opt<int32>", 8, 4))
claim("ty1153b", D, 1153, "`Opt<string>` owns and drops its payload", "rule",
      "`Opt<string>` owns its payload: copying one is refused.", expect="refuse",
      src=prog_("""    Opt<string>:a = Opt.Some("x");
    Opt<string>:b = a;
    discard(b);
    exit 0i32;""", OPT),
      wrong="accepted: two owners of one string")
claim("ty1153c", D, 1153, "`Opt<int32>` is a tag", "rule",
      "`Opt<int32>` copies freely (the twin of ty1153b).",
      expect="run:0",
      src=prog_("""    Opt<int32>:a = Opt.Some(raw v32(3i32));
    Opt<int32>:b = a;
    int32:r = 0i32;
    pick (b) { (Some(v)) { r = v; }, (Opt.None) { r = 9i32; } }
    if (r != 3i32) { exit 10i32; }
    exit 0i32;""", OPT),
      wrong="refused, or 10")
claim("ty1159", D, 1159, "**The instance of a constructor or a bare variant reference**", "rule",
      "A constructor's instance is the expected type: `Opt.None` and `Opt.Some(5i64)` passed to an "
      "`Opt<int64>` parameter compile and match.",
      expect="run:0",
      src=prog_("""    if (raw m11u(Opt.None) != 0i64) { exit 10i32; }
    if (raw m11u(Opt.Some(raw v64(5i64))) != 5i64) { exit 11i32; }
    exit 0i32;""", OPT + """
func:m11u = int64(Opt<int64>:o) never fails {
    int64:r = 0i64;
    pick (o) { (Some(v)) { r = v; }, (Opt.None) { r = 0i64; } }
    pass r;
};"""),
      wrong="refused, or 10/11")
claim("ty1162", D, 1162, "else INFERRED from the payload arguments", "rule",
      "With no expected type, the instance is inferred from the payload: `Opt.Some(5i64)` is an `Opt<int64>`.",
      expect="run:0",
      src=prog_("""    discard(Opt.Some(raw v64(5i64)));
    exit 0i32;""", OPT),
      wrong="refused")
claim("ty1164", D, 1164, "type from context, an unsuffixed literal say, teaches nothing", "rule",
      "An unsuffixed literal teaches nothing: `Opt.Some(5)` with no expected type is TYPE-022.",
      expect="refuse:NITPICK-TYPE-022",
      src=prog_("""    discard(Opt.Some(5));
    exit 0i32;""", OPT),
      wrong="accepted (a default instance)")
claim("ty1165", D, 1165, "else refused: `NITPICK-TYPE-022` naming the parameter", "rule",
      "A payload-less variant with no expected type is TYPE-022.", expect="refuse:NITPICK-TYPE-022",
      src=prog_("""    discard(Opt.None);
    exit 0i32;""", OPT),
      wrong="accepted")
claim("ty1167", D, 1167, "`Opt<int32>:o = Opt.None;`", "rule",
      "A payload-less variant takes its instance from the annotation: `Opt<int32>:o = Opt.None;`.",
      expect="run:0",
      src=prog_("""    Opt<int32>:o = Opt.None;
    int32:r = 0i32;
    pick (o) { (Some(v)) { r = v; }, (Opt.None) { r = 7i32; } }
    if (r != 7i32) { exit 10i32; }
    exit 0i32;""", OPT),
      wrong="refused, or 10")
claim("ty1169", D, 1169, "`Opt<Point>` under `enum:Opt<T: Pr>` is", "rule",
      "An inferred instance is judged as an annotated one: `Opt.Some(Point{…})` under `enum:Opt<T: Pr>` where "
      "Point lacks Pr is TYPE-017.",
      expect="refuse:NITPICK-TYPE-017",
      src=prog_("""    discard(Opt.Some(Point{ x: 1i32 }));
    exit 0i32;""", """trait:Pr = { func:p = int32(Self->:self) never fails; };
enum:Opt<T: Pr> = { Some(T); None; };
struct:Point = { int32:x; };"""),
      wrong="accepted")
claim("ty1170", D, 1170, "In pattern position a bare variant is read", "rule",
      "In pattern position a bare variant is read against the selector: `(Opt.None)` matches an "
      "`Opt<string>` with no annotation.",
      expect="run:0",
      src=prog_("""    Opt<string>:o = Opt.None;
    int32:r = 0i32;
    pick (o) { (Opt.None) { r = 1i32; }, (Some(t)) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;""", OPT),
      wrong="refused (TYPE-022 in a pattern), or 10")
claim("ty1171", D, 1171, "A non-generic enum binds an", "rule",
      "A non-generic enum binds an empty window, unchanged.",
      untestable="[internal] a type's operand window")
