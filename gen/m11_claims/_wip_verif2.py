"""M11 claims: VERIFICATION_REFERENCE.md lines 846-2352 at HUNT2 (9126350).

§7b the obligation catalogue, §7c the theories, §8 the SMT elimination manifest,
§9 the floor's obligations (spec grammar, kernel boundary, rows and verdicts,
protocol models, the floor's stack) and §10 the schedule explorer.

Every expectation is written from the reference's text alone. Where a claim is
about what the compiler EMITS for verification, the test is a script over
`npkc FILE --obligations DIR` (the compiler's half of verification, no z3): the
text names `rows.txt`'s fifth (encoded), eleventh (tier) and twelfth (clause
context) fields; the positions of the other fields (kind 3, hash 4, symbol 6,
site 7, role 8, group 9, traps 10) and index.txt's (NNNN symbol checks group
measured) are the compiler's own header comment in
`src/backend/smt/smt_table.npk` -- scaffolding, not an expectation. A few
scripts build the VERIFIED build without z3 by handing `npkc --elide` a
manifest in the `nitpick.obligations v1` shape (§8, §9's file table) that marks
chosen rows `discharged`, and count what the emission then holds.
"""
from m11lib import *

D = "VERIFICATION"

# --------------------------------------------------------------------- reasons
Z3V = "[z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment)"
Z3ENC = "[z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches"
RUNNERS = "[tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full tree"
FLOOR = "[tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll and runtime/npkrt.spec), which this session neither builds nor runs"
SPEC = "[tool] a rule of runtime/npkrt.spec's grammar as the floor writer (npkg/floor_smt.npk) reads it; testing it needs the writer run over a spec"
MODELS = "[tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt npkg/floor_explore.npk; not run here"
EXPLORE = "[tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls); not run here"
KERNEL = "[tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the translator"
NOMEM = "[unobservable] the row claims the kernel writes no user memory, and the call as the floor issues it passes no address the kernel could write; a probe has nothing to compare"
HISTORY = "[tree] a measurement or a record of what a step landed, about the compiler's tree and its records rather than what it does with a program"


# ------------------------------------------------------------------- programs
def prog(src, name="p"):
    """A whole program for a script: `mod:`, the identity helpers it calls, the
    source, and the M11 failsafe unless the source carries its own."""
    h = helpers_text(src)
    out = "mod:%s;\n\n" % name + (h + "\n\n" if h else "") + src.strip() + "\n"
    if "func:failsafe" not in src:
        out += "\n" + failsafe_text(src)
    return out


OBL_HEAD = r'''# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
@@PROG@@
NPK_EOF
"$NPKC" p.npk -o p.ll --obligations ob >out.txt 2>err.txt; rc=$?
if [ "$rc" -ne 0 ]; then echo "npkc exit $rc"; head -c 800 err.txt; exit 3; fi
[ -f ob/rows.txt ] && [ -f ob/index.txt ] || { echo "no rows.txt or index.txt"; ls ob; exit 4; }
rows() { awk -F'\t' -v f="$1" -v k="$2" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } (k == "*" || $3 == k) && $6 ~ re' ob/rows.txt; }
n() { rows "$1" "$2" | wc -l | tr -d ' '; }
col() { rows "$1" "$2" | cut -f"$3" | sort -u | tr '\n' ' ' | sed 's/ $//'; }
file_of() { awk -F'\t' -v f="$1" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } $2 ~ re { print "ob/" $1 ".smt2"; exit }' ob/index.txt; }
want() { [ "$2" = "$3" ] || { echo "$1: got [$2], want [$3]"; exit "$4"; }; }
'''

ELIDE_HEAD = r'''fbody() { awk -v a=".$1\"(" -v b="@npk_$1(" 'index($0, "define ") == 1 && (index($0, a) > 0 || index($0, b) > 0) { on = 1 } on { print } on && /^}/ { on = 0 }' "$2"; }
manifest() { { echo '# nitpick.obligations v1'; awk -F'\t' "$1"' { print $4 " " $3 " " $11 " discharged elided " $6 }' ob/rows.txt; } > m.txt; }
elide() { "$NPKC" p.npk -o e.ll --elide m.txt >out2.txt 2>err2.txt; rc=$?; if [ "$rc" -ne 0 ]; then echo "npkc --elide exit $rc"; head -c 800 err2.txt; exit 5; fi; }
assumes() { fbody "$1" "$2" | grep -c 'call void @llvm.assume('; }
traps() { fbody "$1" "$2" | grep -cF "@npk_trap(i32 $3)"; }
'''


def obl(src, checks):
    """A script: compile `src` (a whole program's text) with --obligations, then
    the checks (bash; exit 0 when the claim holds, 10.. naming the failed one)."""
    return OBL_HEAD.replace("@@PROG@@", prog(src)) + checks.strip() + "\nexit 0\n"


def elided(src, checks):
    """As obl(), with the verified-build helpers: `manifest AWKCOND` writes m.txt
    marking the rows.txt rows AWKCOND selects `discharged`, `elide` compiles
    p.npk to e.ll under it, `assumes F FILE` / `traps F FILE CODE` count in F's
    body."""
    return OBL_HEAD.replace("@@PROG@@", prog(src)) + ELIDE_HEAD + checks.strip() + "\nexit 0\n"


def calls(*names):
    """A `main` that calls each never-fails function once through `discard`."""
    return "\n".join("    discard(raw %s);" % n for n in names)


# the M11 failsafe's `exit` count for a source with no `error:` declarations
FS_EXITS = failsafe_text("").count("exit ")

# ---------------------------------------------------------------- §7b catalogue
claim("vf0848", D, 848, "Every kind the manifest's `kind` column may carry, exhaustively", "rule",
      "The catalogue lists every obligation kind exhaustively: every row the compiler writes to rows.txt carries one of its 22 kinds.",
      expect="sh:0", sh=obl('''
Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fs = int32(int32:x, int32:n) never fails { pass (x << n); };
func:need = int32(limit<r_pos> int32:m) { pass (m + 1i32); };
func:fl = int32(int32[]:xs, int64:i) never fails { pass xs[i]; };
func:main = int32(cstring[]:_~argv) {
    int32:i = 0i32;
    while (i < 3i32) decreases 3i32 - i { i = i + 1i32; }
    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fs(raw v32(1i32), raw v32(2i32)));
    discard(raw fl(arr[0i64...4i64], raw v64(1i64)));
    int32:r = need(raw v32(3i32)) ?! E9;
    int32:k = pick (r) { (4i32) { give 0i32; }, (*) { give 10i32; } };
    exit k;
};''', '''
K=" div-zero div-min overflow bounds cast-range exhaustive requires ensures invariant limit limit-subsume terminate stack-depth err-exit failsafe-post loop-step shift-range prove assert-static disjoint floor-spec floor-model "
nk=$(cut -f3 ob/rows.txt | sort -u | wc -l | tr -d ' ')
[ "$nk" -ge 5 ] || { echo "only $nk kinds: the program should have produced more"; exit 10; }
bad=$(cut -f3 ob/rows.txt | sort -u | while read -r k; do case "$K" in *" $k "*) ;; *) echo "$k";; esac; done)
[ -z "$bad" ] || { echo "kinds outside the catalogue: $bad"; exit 11; }'''),
      wrong="a row whose kind the catalogue does not list (exit 11)")

# -- div-zero
P_DIV = '''
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fr = int32(int32:a, int32:b) never fails { pass (a % b); };
func:fu = uint32(uint32:a, uint32:b) never fails { pass (a / b); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fr(raw v32(7i32), raw v32(2i32)));
    discard(raw fu(raw vu32(7u32), raw vu32(2u32)));
    exit 0i32;
};'''

claim("vf0857", D, 857, "| `div-zero` | the divisor of an integer `/` or `%` is not zero", "row",
      "An integer `/` or `%` by a computed divisor is one `div-zero` row: one each in a signed `/`, a signed `%` and an unsigned `/`.",
      expect="sh:0", sh=obl(P_DIV, '''
want "div-zero rows of fq (a / b)" "$(n fq div-zero)" 1 10
want "div-zero rows of fr (a % b)" "$(n fr div-zero)" 1 11
want "div-zero rows of fu (uint32 a / b)" "$(n fu div-zero)" 1 12'''),
      wrong="no row for a division (exit 10-12), or several")

claim("vf0857b", D, 857, "| yes | 1.5.0 |", "row",
      "`div-zero` has a guard: in the plain build an integer `%` by a computed zero traps DivByZero.",
      expect="trap:DivByZero", src=main_('''    int32:r = raw v32(7i32) % raw v32(0i32);
    if (r == 0i32) { exit 10i32; }
    exit 11i32;'''),
      wrong="no guard: a machine fault (107/136) or some value (10, 11)")

P_SIMD_DIV = '''
func:fv = int32(int32:a0, int32:a1, int32:b0, int32:b1) never fails {
    simd<int32, 4>:a = simd(a0, a1, a0, a1);
    simd<int32, 4>:b = simd(b0, b1, b0, b1);
    simd<int32, 4>:q = a / b;
    pass q[0i64];
};
func:fw = uint32(uint32:a0, uint32:b0) never fails {
    simd<uint32, 4>:a = simd(a0, a0, a0, a0);
    simd<uint32, 4>:b = simd(b0, b0, b0, b0);
    simd<uint32, 4>:q = a / b;
    pass q[0i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fv(raw v32(8i32), raw v32(6i32), raw v32(2i32), raw v32(3i32)));
    discard(raw fw(raw vu32(8u32), raw vu32(2u32)));
    exit 0i32;
};'''

claim("vf0857c", D, 857, "a `simd` division's any-lane guard is ONE row over the lanes' conjunction (D-282)", "row",
      "A `simd<int32, 4>` division by a computed vector has ONE `div-zero` row, not one per lane.",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "div-zero rows of the simd<int32, 4> division" "$(n fv div-zero)" 1 10
want "div-zero rows of the simd<uint32, 4> division" "$(n fw div-zero)" 1 11'''),
      wrong="one row per lane (4: exit 10/11) or none")

# -- div-min
claim("vf0858", D, 858, "| `div-min` |", "row",
      "A signed integer division has one `div-min` row; an unsigned division has none.",
      expect="sh:0", sh=obl(P_DIV, '''
want "div-min rows of fq (int32 a / b)" "$(n fq div-min)" 1 10
want "div-min rows of fr (int32 a % b)" "$(n fr div-min)" 1 11
want "div-min rows of fu (uint32 a / b)" "$(n fu div-min)" 0 12'''),
      wrong="no div-min row for a signed division (10, 11) or one for an unsigned one (12)")

claim("vf0858b", D, 858, "a signed division is not `INT_MIN / -1` (D-142)", "row",
      "`div-min` has a guard: the int32 minimum divided by -1 traps DivOverflow in the plain build.",
      m10="v05_min_div_minus_one")

claim("vf0858c", D, 858, "one row over the lanes for a signed-element `simd` (D-282)", "row",
      "A signed-element `simd` division has ONE `div-min` row over the lanes; an unsigned-element one has none.",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "div-min rows of the simd<int32, 4> division" "$(n fv div-min)" 1 10
want "div-min rows of the simd<uint32, 4> division" "$(n fw div-min)" 0 11'''),
      wrong="one per lane (4), none for the signed element, or one for the unsigned")

# -- overflow
claim("vf0859", D, 859, "| `overflow` | a plain-integer `+ - *` or negation stays in range (D-210)", "row",
      "Each plain-integer `+`, `-`, `*` and negation over computed operands is one `overflow` row at its own node: `a + b` one, `-a` one, `(a + b) * c` two, a compound `x += b` one.",
      expect="sh:0", sh=obl('''
func:fa = int32(int32:a, int32:b) never fails { pass (a + b); };
func:fneg = int32(int32:a) never fails { pass (-a); };
func:fm = int32(int32:a, int32:b, int32:c) never fails { pass ((a + b) * c); };
func:fcomp = int32(int32:a, int32:b) never fails { int32:x = a; x += b; pass x; };
func:main = int32(cstring[]:_~argv) {
    discard(raw fa(raw v32(1i32), raw v32(2i32)));
    discard(raw fneg(raw v32(1i32)));
    discard(raw fm(raw v32(1i32), raw v32(2i32), raw v32(3i32)));
    discard(raw fcomp(raw v32(1i32), raw v32(2i32)));
    exit 0i32;
};''', '''
want "overflow rows of a + b" "$(n fa overflow)" 1 10
want "overflow rows of -a" "$(n fneg overflow)" 1 11
want "overflow rows of (a + b) * c" "$(n fm overflow)" 2 12
want "overflow rows of x += b" "$(n fcomp overflow)" 1 13'''),
      wrong="no overflow rows (the kind still pending) or one per function")

claim("vf0859b", D, 859, "ONE row over the lanes for a `simd` integer operation", "row",
      "A `simd<int32, 4>` `+` of computed vectors is ONE `overflow` row, not one per lane.",
      expect="sh:0", sh=obl('''
func:fva = int32(int32:a0, int32:b0) never fails {
    simd<int32, 4>:a = simd(a0, a0, a0, a0);
    simd<int32, 4>:b = simd(b0, 1i32, 2i32, 3i32);
    simd<int32, 4>:s = a + b;
    pass s[0i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fva(raw v32(1i32), raw v32(2i32)));
    exit 0i32;
};''', '''
want "overflow rows of a simd<int32, 4> +" "$(n fva overflow)" 1 10'''),
      wrong="four rows (one per lane) or none")

P_SUM = '''
func:fsum = int32(int32:a0, int32:a1, int32:a2, int32:a3) never fails {
    simd<int32, 4>:a = simd(a0, a1, a2, a3);
    pass a.sum();
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fsum(raw v32(1i32), raw v32(2i32), raw v32(3i32), raw v32(4i32)));
    exit 0i32;
};'''

claim("vf0859c", D, 859, "ONE with N-1 traps for an integer `.sum()`", "row",
      "An integer `.sum()` of a `simd<int32, 4>` is ONE `overflow` row whose traps field is 3 (N-1).",
      expect="sh:0", sh=obl(P_SUM, '''
want "overflow rows of a simd<int32, 4> .sum()" "$(n fsum overflow)" 1 10
want "the row's traps field" "$(col fsum overflow 10)" 3 11'''),
      wrong="three rows of one trap each (exit 10), or one row counting one trap (exit 11)")

claim("vf0859d", D, 859, "a node the folder writes as its constant has no guard and no row (D-310)", "row",
      "`2i32 + 3i32`, which the folder writes as its constant, has no `overflow` row.",
      expect="sh:0", sh=obl('''
func:fk = int32() never fails { pass (2i32 + 3i32); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fk());
    exit 0i32;
};''', '''
want "overflow rows of the folded 2 + 3" "$(n fk overflow)" 0 10'''),
      wrong="a row (and a guard) for a folded node")

claim("vf0859e", D, 859, "| yes | 1.5.8b step 3 |", "row",
      "`overflow` has a guard: a plain int32 `+` past the maximum traps IntOverflow in the plain build.",
      m10="o01_int32_add")

claim("vf0859f", D, 859, "or negation stays in range (D-210)", "row",
      "Negating the int32 minimum traps IntOverflow.",
      m10="o04_int32_negate_min")

# -- bounds
claim("vf0860", D, 860, "| `bounds` | an index is inside its array, slice, buffer or `List`", "row",
      "A computed index into a fixed array and into a slice is one `bounds` row each.",
      expect="sh:0", sh=obl('''
func:fx = int32(int32[4]:a, int64:i) never fails { pass a[i]; };
func:fy = int32(int32[]:xs, int64:i) never fails { pass xs[i]; };
func:main = int32(cstring[]:_~argv) {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    discard(raw fx(a, raw v64(1i64)));
    discard(raw fy(a[0i64...4i64], raw v64(1i64)));
    exit 0i32;
};''', '''
want "bounds rows of a[i] on int32[4]" "$(n fx bounds)" 1 10
want "bounds rows of xs[i] on int32[]" "$(n fy bounds)" 1 11'''),
      wrong="no bounds rows (the kind still pending), or two per access")

P_RANGE = '''
func:cnt = int64(int32[]:s) never fails { pass s.len; };
func:fz = int64(int32[]:xs, int64:lo, int64:hi) never fails { pass (raw cnt(xs[lo...hi])); };
func:main = int32(cstring[]:_~argv) {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    discard(raw fz(a[0i64...4i64], raw v64(1i64), raw v64(3i64)));
    exit 0i32;
};'''

claim("vf0860b", D, 860, "ONE row for a range slice's pair (`lo <= hi <= len`) at the RANGE's node", "row",
      "A range slice `xs[lo...hi]` with computed bounds is ONE `bounds` row for the pair.",
      expect="sh:0", sh=obl(P_RANGE, '''
want "bounds rows of xs[lo...hi]" "$(n fz bounds)" 1 10'''),
      wrong="two rows (one per bound) or none")

claim("vf0860c", D, 860, "`0 <= i < len` at every checked element access", "row",
      "The element check is `0 <= i < len`: a negative index traps OutOfBounds.",
      m10="a04_index_negative")

claim("vf0860d", D, 860, "| yes | 1.5.8b step 5", "row",
      "`bounds` has a guard: an index past the end of an array traps OutOfBounds.",
      m10="a03_index_past_end")

claim("vf0860e", D, 860, "ONE row at each call of `string_from_bytes(p, len)`", "row",
      "A call of `string_from_bytes(p, len)` is ONE `bounds` row, keyed on the call.",
      expect="sh:0", sh=obl('''
func:mk = int64(cstring:c) never fails {
    string:s = string_from_bytes(c.ptr, c.len);
    pass s.len;
};
func:main = int32(cstring[]:argv) {
    discard(raw mk(argv[0i64]));
    exit 0i32;
};''', '''
want "bounds rows of a string_from_bytes call" "$(n mk bounds)" 1 10'''),
      wrong="no row: the length no allocation bounds goes unchecked by the table")

claim("vf0860f", D, 860, "`0 <= len <= 2^47`, the emitter's guard read back", "row",
      "The emitter guards `string_from_bytes(p, len)` with `0 <= len <= 2^47`: a length of 2^47 + 1 traps (the `bounds` code, OutOfBounds) before any byte is read.",
      expect="trap:OutOfBounds", src='''
func:main = int32(cstring[]:argv) {
    string:s = string_from_bytes(argv[0i64].ptr, raw v64(140737488355329i64));
    if (s.len > 0i64) { exit 10i32; }
    exit 11i32;
};''',
      wrong="no guard: the copy reads 2^47 bytes (machine fault 107/139, HeapOom 92, or HeapBadRequest 91)")

claim("vf0860g", D, 860, "`0 <= len <= 2^47`", "row",
      "The same guard's lower half: `string_from_bytes(p, -1)` traps OutOfBounds.",
      expect="trap:OutOfBounds", src='''
func:main = int32(cstring[]:argv) {
    string:s = string_from_bytes(argv[0i64].ptr, raw v64(-1i64));
    if (s.len > 0i64) { exit 10i32; }
    exit 11i32;
};''',
      wrong="a negative length read as huge by the allocator (HeapBadRequest 91 / HeapOom 92) or an empty string (11)")

claim("vf0860h", D, 860, "a discharged row elides the guard into one `llvm.assume`", "row",
      "In the verified build a discharged `string_from_bytes` row replaces its guard with exactly one `llvm.assume` and no OutOfBounds trap.",
      expect="sh:0", sh=elided('''
func:mk = int64(cstring:c) never fails {
    string:s = string_from_bytes(c.ptr, c.len);
    pass s.len;
};
func:main = int32(cstring[]:argv) {
    discard(raw mk(argv[0i64]));
    exit 0i32;
};''', '''
want "OutOfBounds traps in mk, plain build" "$(traps mk p.ll -4099)" 1 10
manifest '$3=="bounds"'
elide
want "llvm.assume calls in mk, verified build" "$(assumes mk e.ll)" 1 11
want "OutOfBounds traps in mk, verified build" "$(traps mk e.ll -4099)" 0 12'''),
      wrong="the guard kept beside a discharged row (12), or no assume (11)")

claim("vf0860i", D, 860, "the length is the term `(|npk.len| base)` wherever it is named", "row",
      "A loop over `xs.len` indexing `xs[i]` states the length as `|npk.len|` in its obligation file.",
      expect="sh:0", sh=obl('''
func:fl = int32(int32[]:xs) never fails {
    int32:acc = 0i32;
    for (int64:i in 0i64...xs.len) { acc = acc +% xs[i]; }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    discard(raw fl(a[0i64...4i64]));
    exit 0i32;
};''', '''
f=$(file_of fl); [ -n "$f" ] && [ -f "$f" ] || { echo "no obligation file for fl"; exit 10; }
grep -qF '|npk.len|' "$f" || { echo "no |npk.len| in $f"; exit 11; }'''),
      wrong="the length a fresh symbol per read, never the one term")

claim("vf0860j", D, 860, "so a loop written over `xs.len` or `l.count` proves the accesses inside it", "row",
      "An access inside a loop bounded by `xs.len` or `l.count` is a discharged row.",
      untestable=Z3V)

claim("vf0860k", D, 860, "a fixed array's length is its type's constant", "row",
      "A fixed array's length enters the goal as its type's constant.",
      untestable=Z3ENC)

# -- cast-range
P_CAST = '''
func:fc = int32(flt64:f) never fails { pass (f =>! int32); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fc(raw vf64(2.5f64)));
    exit 0i32;
};'''

claim("vf0861", D, 861, "| `cast-range` | a float's `=>!` cast to an integer has an integer meaning (D-306)", "row",
      "A `flt64 =>! int32` is one `cast-range` row.",
      expect="sh:0", sh=obl(P_CAST, '''
want "cast-range rows of f =>! int32" "$(n fc cast-range)" 1 10'''),
      wrong="no row: the cast's meaning unchecked by the table")

claim("vf0861b", D, 861, "the value is not NaN or an infinity", "row",
      "A NaN's `=>!` to an integer traps CastRange.",
      m10="c11_float_nan_to_int_traps")

claim("vf0861c", D, 861, "lies inside the target", "row",
      "A float whose truncation the target cannot hold (3e9 to int32) traps CastRange.",
      m10="c12_float_too_big_to_int_traps")

claim("vf0861d", D, 861, "its truncation toward zero", "row",
      "The cast truncates toward zero (3.7 is 3, -3.7 is -3).",
      m10="c10_float_to_int_truncates")

claim("vf0861e", D, 861, "the two ordered compares before the conversion, `CastRange`", "row",
      "An infinity's `=>!` to int32 traps CastRange.",
      expect="trap:CastRange", src=main_('''    flt64:big = raw vf64(1.0e308f64) * raw vf64(10.0f64);
    int32:x = big =>! int32;
    if (x == 0i32) { exit 10i32; }
    exit 11i32;'''),
      wrong="LLVM poison read as some integer (10 or 11)")

claim("vf0861f", D, 861, "its truncation toward zero lies inside the target", "row",
      "It is the TRUNCATION that must fit: -2147483648.5 and 2147483647.5 cast to int32 give the minimum and the maximum without trapping.",
      expect="run:0", src=main_('''    int32:lo = raw vf64(-2147483648.5f64) =>! int32;
    if (lo != (-2147483647i32 - 1i32)) { exit 10i32; }
    int32:hi = raw vf64(2147483647.5f64) =>! int32;
    if (hi != 2147483647i32) { exit 11i32; }
    exit 0i32;'''),
      wrong="compares on the untruncated value: CastRange (112) for -2147483648.5; a wrong value (10, 11)")

claim("vf0861g", D, 861, "a `simd` cast's any-lane guard is one row over the lanes", "row",
      "A `simd<flt64, 4> =>! simd<int32, 4>` is ONE `cast-range` row.",
      expect="sh:0", sh=obl('''
func:fvc = int32(flt64:a) never fails {
    simd<flt64, 4>:v = simd(a, a, a, a);
    simd<int32, 4>:w = v =>! simd<int32, 4>;
    pass w[0i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fvc(raw vf64(2.5f64)));
    exit 0i32;
};''', '''
want "cast-range rows of a simd<flt64, 4> =>! simd<int32, 4>" "$(n fvc cast-range)" 1 10'''),
      wrong="four rows (one per lane) or none")

# -- exhaustive
P_PICK = '''
func:fp1 = int32(int32:x) never fails {
    int32:r = 0i32;
    pick (x) { (1i32) { r = 10i32; }, (*) { r = 20i32; } }
    pass r;
};
func:fpk = int32(int32:x) never fails {
    int32:r = 0i32;
    pick (x) { (1i32) { r = 10i32; }, (*) { r = 20i32; } }
    int32:s = pick (x) { (2i32) { give 3i32; }, (*) { give 4i32; } };
    pass r + s;
};
func:fas = int32() never fails {
    assert_static(1i32 + 1i32 == 2i32);
    pass 1i32;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fp1(raw v32(1i32)));
    discard(raw fpk(raw v32(1i32)));
    discard(raw fas());
    exit 0i32;
};'''

claim("vf0862", D, 862, "| `exhaustive` | a `pick` covers its domain (checker-discharged)", "row",
      "A `pick` statement is one `exhaustive` row, decided by the checker (`c` in rows.txt's fifth field).",
      expect="sh:0", sh=obl(P_PICK, '''
want "exhaustive rows of one pick" "$(n fp1 exhaustive)" 1 10
want "their encoded field" "$(col fp1 exhaustive 5)" c 11'''),
      wrong="no row for a pick, or a solver query (fifth field 1)")

claim("vf0862b", D, 862, "(checker-discharged) | no | 1.5.4 |", "row",
      "The checker decides coverage: a `pick` over int32 with no arm for most values and no `(*)` is refused.",
      expect="refuse", src=main_('''    int32:x = raw v32(1i32);
    int32:r = 0i32;
    pick (x) { (1i32) { r = 10i32; }, (2i32) { r = 20i32; } }
    exit r;'''),
      wrong="accepted: an uncovered value falls through the pick")

# -- requires
P_REQ = '''
error:E9;
func:need = int32(int32:m) requires m >= 0i32 { pass (m + 1i32); };
func:fcall = int32(int32:v) { pass (need(v) ?! E9); };
func:main = int32(cstring[]:_~argv) {
    int32:r = fcall(raw v32(1i32)) ?! E9;
    exit (r - 2i32);
};'''

claim("vf0863", D, 863, "| `requires` | a callee's precondition holds at the call (D-221)", "row",
      "A call of a function with a `requires` is one `requires` row in the caller.",
      expect="sh:0", sh=obl(P_REQ, '''
want "requires rows at the call in fcall" "$(n fcall requires)" 1 10'''),
      wrong="no call-site row (the precondition checked only at the entry)")

claim("vf0863b", D, 863, "| `requires` | a callee's precondition holds at the call (D-221) | yes |", "row",
      "`requires` has a guard: calling with an argument that breaks the precondition traps RequiresViolated in the plain build.",
      expect="trap:RequiresViolated", src=main_('''    int32:r = need(raw v32(-1i32)) ?! E9;
    if (r == 0i32) { exit 10i32; }
    exit 11i32;''', '''error:E9;
func:need = int32(int32:m) requires m >= 0i32 { pass (m + 1i32); };'''),
      wrong="no check: the body runs (exit 10/11), or the violation surfaces as the call's error (E9: 89)")

# -- ensures
claim("vf0864", D, 864, "| `ensures` |", "row",
      "A postcondition is checked at each return: a function with two `pass` seams and an `ensures` has two `ensures` rows.",
      expect="sh:0", sh=obl('''
error:E9;
func:fe = int32(int32:x) ensures result > 0i32 {
    if (x > 0i32) { pass x; }
    pass 1i32;
};
func:main = int32(cstring[]:_~argv) {
    int32:r = fe(raw v32(3i32)) ?! E9;
    exit (r - 3i32);
};''', '''
want "ensures rows of a function with two return seams" "$(n fe ensures)" 2 10'''),
      wrong="one row for the function, or none")

claim("vf0864b", D, 864, "a body's postcondition holds at its return (D-221)", "row",
      "`ensures` has a guard: a return that breaks the postcondition traps EnsuresViolated in the plain build.",
      expect="trap:EnsuresViolated", src=main_('''    int32:r = fe(raw v32(0i32)) ?! E9;
    if (r == 0i32) { exit 10i32; }
    exit 11i32;''', '''error:E9;
func:fe = int32(int32:x) ensures result > 0i32 { pass x; };'''),
      wrong="no check: 0 returned (exit 10)")

# -- invariant
P_INV = '''
func:fi = int32(int32:n) never fails {
    int32:i = 0i32;
    int32:acc = 0i32;
    while (i < n) decreases n - i invariant acc >= 0i32 {
        i = i + 1i32;
        acc = acc + 1i32;
    }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fi(raw v32(3i32)));
    exit 0i32;
};'''

claim("vf0865", D, 865, "| `invariant` | a loop invariant holds at entry and is preserved (D-221)", "row",
      "A `while` with an `invariant` and no `continue` has two `invariant` rows: the entry and the preservation.",
      expect="sh:0", sh=obl(P_INV, '''
want "invariant rows of one loop" "$(n fi invariant)" 2 10'''),
      wrong="one row (entry only) or none")

claim("vf0865b", D, 865, "a loop invariant holds at entry and is preserved", "row",
      "`invariant` has a guard: a body that breaks the invariant traps InvariantViolated at the next head visit.",
      expect="trap:InvariantViolated", src=main_('''    int32:i = 0i32;
    int32:acc = 0i32;
    while (i < 3i32) decreases 3i32 - i invariant acc >= 0i32 {
        i = i + 1i32;
        acc = acc - raw v32(1i32);
    }
    exit 10i32;'''),
      wrong="no check: the loop ends normally (exit 10)")

# -- limit
claim("vf0866", D, 866, "| `limit` | a `limit<Rules>` binding satisfies its rule at every write point (D-220)", "row",
      "A limited binding's initial write and a later assignment are one `limit` row each.",
      expect="sh:0", sh=obl('''
Rules<int32>:r_pos = { $ > 0i32 };
func:fw1 = int32(int32:a, int32:b) never fails {
    limit<r_pos> int32:x = a;
    x = b;
    pass x;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fw1(raw v32(1i32), raw v32(2i32)));
    exit 0i32;
};''', '''
want "limit rows of two write points" "$(n fw1 limit)" 2 10'''),
      wrong="one row (the declaration only) or none")

claim("vf0866b", D, 866, "| yes | 1.5.2; fields 1.5.8b step 6 |", "row",
      "`limit` has a guard: an assignment that breaks the rule traps LimitViolated in the plain build.",
      expect="trap:LimitViolated", src=main_('''    limit<r_pos> int32:x = 5i32;
    x = raw v32(0i32);
    if (x == 0i32) { exit 10i32; }
    exit 11i32;''', "Rules<int32>:r_pos = { $ > 0i32 };"),
      wrong="no check: 0 stored (exit 10)")

claim("vf0866c", D, 866, "so a write to a limited field of a limited binding is two rows at two keys", "row",
      "Assigning a limited field of a limited binding adds two `limit` rows (the field's, keyed on the written expression, and the root's, keyed on the statement), at two distinct sites.",
      expect="sh:0", sh=obl('''
Rules<int32>:r_pos = { $ > 0i32 };
struct:Tk = { limit<r_pos> int32:n; int32:m; };
Rules<Tk>:r_tk = { $.m >= 0i32 };
func:ff1 = int32(int32:a) never fails {
    limit<r_tk> Tk:t = Tk{ n: a, m: 0i32 };
    pass t.n;
};
func:ff2 = int32(int32:a, int32:b) never fails {
    limit<r_tk> Tk:t = Tk{ n: a, m: 0i32 };
    t.n = b;
    pass t.n;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw ff1(raw v32(1i32)));
    discard(raw ff2(raw v32(1i32), raw v32(2i32)));
    exit 0i32;
};''', '''
a=$(n ff1 limit); b=$(n ff2 limit)
want "limit rows the assignment t.n = b adds" "$((b - a))" 2 10
want "distinct sites among ff2's limit rows" "$(rows ff2 limit | cut -f7 | sort -u | wc -l | tr -d ' ')" "$b" 11'''),
      wrong="one row for the write (10), or two rows at one key (11)")

claim("vf0866d", D, 866, "an assignment through any path including a pointer's", "row",
      "A write to a limited field through a pointer is a `limit` row, as the struct literal's value for it is.",
      expect="sh:0", sh=obl('''
Rules<int32>:r_pos = { $ > 0i32 };
struct:Tk = { limit<r_pos> int32:n; int32:m; };
func:fptr = int32(int32:a, int32:b) never fails {
    Tk:t = Tk{ n: a, m: 0i32 };
    Tk->:p = $$m t;
    p.n = b;
    pass t.n;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fptr(raw v32(1i32), raw v32(2i32)));
    exit 0i32;
};''', '''
want "limit rows: the literal's value and the write through the pointer" "$(n fptr limit)" 2 10'''),
      wrong="the pointer's write unchecked (one row)")

# -- limit-subsume
P_SUB = '''
Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:narrow = int32(limit<r_pos> int32:n) { pass n; };
func:fcaller = int32(int32:v) { pass (narrow(v) ?! E9); };
func:main = int32(cstring[]:_~argv) {
    int32:r = fcaller(raw v32(5i32)) ?! E9;
    exit (r - 5i32);
};'''

claim("vf0867", D, 867, "| `limit-subsume` | one `Rules` implies another at a boundary (D-220)", "row",
      "A direct call of a sync callee with a limited parameter is one `limit-subsume` row in the caller.",
      expect="sh:0", sh=obl(P_SUB, '''
want "limit-subsume rows at fcaller's call" "$(n fcaller limit-subsume)" 1 10'''),
      wrong="no row at the call")

P_ASYNC_LIMIT = '''
Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
async func:fetchl = int32(limit<r_pos> int32:v) { pass (v + 1i32); };
async func:main = int32(cstring[]:_~argv) {
    int32:a = (await fetchl(raw v32(7i32))) ?! E9;
    exit (a - 8i32);
};'''

claim("vf0867b", D, 867, "at a direct call of a sync callee", "row",
      "A call of an ASYNC callee with a limited parameter has no `limit-subsume` row.",
      expect="sh:0", sh=obl(P_ASYNC_LIMIT, '''
want "limit-subsume rows at main's await of a coroutine" "$(n main limit-subsume)" 0 10'''),
      wrong="a row at a coroutine's call site, where nothing could elide its check")

claim("vf0867c", D, 867, "| yes | 1.5.2 |", "row",
      "`limit-subsume`'s guard is the callee's entry check: calling a limited parameter with a value outside its rule traps LimitViolated in the plain build.",
      expect="trap:LimitViolated", src=main_('''    int32:r = narrow(raw v32(0i32)) ?! E9;
    if (r == 0i32) { exit 10i32; }
    exit 11i32;''', '''Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:narrow = int32(limit<r_pos> int32:n) { pass n; };'''),
      wrong="no entry check: 0 accepted (exit 10)")

# -- terminate
P_TERM = '''
func:ft = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases n - i { i = i + 1i32; }
    pass i;
};
func:ftu = uint32(uint32:u0) never fails {
    uint32:u = u0;
    while (u > 0u32) decreases u { u = u - 1u32; }
    pass u;
};
func:ftc = int32(int32:n) never fails {
    int32:i = 0i32;
    int32:odd = 0i32;
    while (i < n) decreases n - i {
        i = i + 1i32;
        if ((i % 2i32) == 1i32) { odd = odd + 1i32; continue; }
    }
    pass odd;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw ft(raw v32(3i32)));
    discard(raw ftu(raw vu32(3u32)));
    discard(raw ftc(raw v32(4i32)));
    exit 0i32;
};'''

claim("vf0868", D, 868, "| `terminate` | a `while`/`when` loop's `decreases E` measure is at least zero at every head visit", "row",
      "A `while` with a signed `decreases` measure and no `continue` has two `terminate` rows: the entry row and the preservation row.",
      expect="sh:0", sh=obl(P_TERM, '''
want "terminate rows of a signed-measure loop" "$(n ft terminate)" 2 10'''),
      wrong="one row, or none (the kind pending)")

claim("vf0868b", D, 868, "an unsigned one cannot be below zero and records no such row", "row",
      "A loop whose measure is unsigned records no entry row: one `terminate` row (the preservation).",
      expect="sh:0", sh=obl(P_TERM, '''
want "terminate rows of an unsigned-measure loop" "$(n ftu terminate)" 1 10'''),
      wrong="an entry row for an unsigned measure (2 rows)")

claim("vf0868c", D, 868, "one per `continue` re-entering the loop", "row",
      "Each `continue` that re-enters the loop adds one `terminate` row: a signed loop with one `continue` has three.",
      expect="sh:0", sh=obl(P_TERM, '''
want "terminate rows of a signed loop with one continue" "$(n ftc terminate)" 3 10'''),
      wrong="the continue's re-entry unrecorded (2 rows)")

claim("vf0868d", D, 868, "the head's check, `DecreasesViolated`", "row",
      "`terminate` has a guard: a measure that does not decrease between head visits traps DecreasesViolated in the plain build.",
      expect="trap:DecreasesViolated", src=main_('''    int32:i = 0i32;
    int32:step = raw v32(0i32);
    while (i < 3i32) decreases 3i32 - i { i = i + step; }
    exit 10i32;'''),
      wrong="no check: the loop never ends (timeout)")

P_REC = '''
func:fact = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 1i32; }
    pass (n *% (raw fact(n - 1i32)));
};
func:is_ev = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass true; }
    pass (raw is_od(n - 1i32));
};
func:is_od = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass false; }
    pass (raw is_ev(n - 1i32));
};
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fact(raw v32(4i32)));
    discard(raw is_ev(raw v32(4i32)));
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    exit 0i32;
};'''

claim("vf0868e", D, 868, "the callee's measure at the arguments below the caller's at entry with the caller's at least zero", "row",
      "A recursive call inside a group whose members state `decreases` is one `terminate` row of the caller's at the call site.",
      expect="sh:0", sh=obl(P_REC, '''
want "terminate rows at fact's one recursive call" "$(n fact terminate)" 1 10
want "terminate rows at is_ev's one call" "$(n is_ev terminate)" 1 11'''),
      wrong="no row at a recursive call")

claim("vf0868f", D, 868, "the check before the call, one trap", "row",
      "A recursive call whose argument's measure is not below the caller's traps DecreasesViolated before the call.",
      expect="trap:DecreasesViolated", src=main_('''    int32:r = raw spin(raw v32(3i32));
    if (r == 0i32) { exit 10i32; }
    exit 11i32;''', '''func:spin = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 0i32; }
    pass (raw spin(n));
};'''),
      wrong="no check: unbounded recursion (StackExhausted 106) or a hang")

claim("vf0868g", D, 868, "a recursive call inside a `requires` clause or a measure has no check and an `unencoded` row with no trap", "row",
      "A recursive call inside a `requires` clause or a measure is an `unencoded` row with no trap.",
      untestable="[vague] the text gives no spelling of a recursive call inside a clause or a measure (a pure, measured callee inside its own group's contract) that this extractor has seen compile")

# -- stack-depth
claim("vf0869", D, 869, "| `stack-depth` | the recursion depth is bounded (the audit's G-6 row; D-305 (7))", "row",
      "One `stack-depth` row per recursive group with a cycle, derived (`d` in rows.txt's fifth field): a self-recursive function and a mutual pair give two rows, both `d`.",
      expect="sh:0", sh=obl(P_REC, '''
want "stack-depth rows (two cyclic groups)" "$(awk -F'\\t' '$3 == "stack-depth"' ob/rows.txt | wc -l | tr -d ' ')" 2 10
want "their encoded field" "$(awk -F'\\t' '$3 == "stack-depth" { print $5 }' ob/rows.txt | sort -u | tr -d '\\n')" d 11'''),
      wrong="a row per member (3), none, or a solver query")

claim("vf0869b", D, 869, "in the first member the emission reaches", "row",
      "A group's `stack-depth` row sits in the file of its first member the emission reaches.",
      untestable="[internal] which member the emission reaches first is the emitter's order, which the text does not fix")

claim("vf0869c", D, 869, "DERIVED by the runners from the group's `terminate` call rows", "row",
      "The row's verdict is derived by the runners: `discharged` when every member states `decreases` and every call row is discharged, `open` otherwise.",
      untestable=Z3V)

claim("vf0869d", D, 869, "no query, no guard, elides nothing (the stack check stays in every build)", "row",
      "A `stack-depth` row elides nothing: the stack check stays in the verified build.",
      untestable=Z3V)

# -- err-exit
P_TBB_CMP = '''
func:fte = int32(tbb32:a, tbb32:b) never fails {
    if (a == b) { pass 1i32; }
    pass 0i32;
};
func:fte2 = int32(tbb32:a, tbb32:b) never fails {
    int32:r = 0i32;
    if (a == b) { r = 1i32; }
    if (a != b) { r = 2i32; }
    pass r;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fte(raw vt32(1tbb32), raw vt32(2tbb32)));
    discard(raw fte2(raw vt32(1tbb32), raw vt32(2tbb32)));
    exit 0i32;
};'''

claim("vf0870", D, 870, "| `err-exit` | the `TbbErr` guard's condition (D-144 as amended, D-278)", "row",
      "A comparison of two computed `tbb32` values is one `err-exit` row.",
      expect="sh:0", sh=obl(P_TBB_CMP, '''
want "err-exit rows of one tbb32 comparison" "$(n fte err-exit)" 1 10'''),
      wrong="no row (the TbbErr guard outside the table)")

claim("vf0870b", D, 870, "neither operand is ERR at a comparison on a twisted value", "row",
      "Comparing a `tbb8` holding ERR traps TbbErr.",
      m10="m12_tbb_compare_on_err_traps")

claim("vf0870c", D, 870, "the operand is not ERR at a cast out of its family (both spellings)", "row",
      "An ERR `tbb8` cast out of its family with `=>!` traps TbbErr.",
      expect="trap:TbbErr", src=main_('''    tbb8:e = raw vt8(127tbb8) + raw vt8(1tbb8);
    int32:x = e =>! int32;
    if (x == 0i32) { exit 10i32; }
    exit 11i32;'''),
      wrong="ERR's carrier value (-128) or 0 cast silently (10, 11)")

claim("vf0870d", D, 870, "a cast out of its family (both spellings)", "row",
      "An ERR `tbb8` cast out of its family with the checked `=>` traps TbbErr too.",
      expect="trap:TbbErr", src=main_('''    tbb8:e = raw vt8(127tbb8) + raw vt8(1tbb8);
    int64:x = e => int64;
    if (x == 0i64) { exit 10i32; }
    exit 11i32;'''),
      wrong="ERR's carrier value cast silently (10, 11)")

claim("vf0870e", D, 870, "a checked crossing into or within a family lands in the target's range", "row",
      "A checked crossing into `tbb8` of a value outside its range (1000 from int64) traps TbbErr.",
      expect="trap:TbbErr", src=main_('''    int64:v = raw v64(1000i64);
    tbb8:t = v => tbb8;
    if (is_err(t)) { exit 10i32; }
    exit 11i32;'''),
      wrong="ERR produced silently (10) or the value wrapped (11)")

P_TBB_DIV = '''
func:ftd = tbb32(tbb32:a, tbb32:b) never fails { pass (a / b); };
func:ftm = tbb32(tbb32:a, tbb32:b) never fails { pass (a % b); };
func:main = int32(cstring[]:_~argv) {
    discard(raw ftd(raw vt32(7tbb32), raw vt32(2tbb32)));
    discard(raw ftm(raw vt32(7tbb32), raw vt32(2tbb32)));
    exit 0i32;
};'''

claim("vf0870f", D, 870, "a twisted division has no row", "row",
      "A `tbb32` `/` or `%` by a computed divisor has no row at all (no div-zero, div-min or err-exit).",
      expect="sh:0", sh=obl(P_TBB_DIV, '''
want "rows of a tbb32 division" "$(n ftd '*')" 0 10
want "rows of a tbb32 remainder" "$(n ftm '*')" 0 11'''),
      wrong="a div-zero/div-min/err-exit row for a division that never traps")

claim("vf0870g", D, 870, "(a zero divisor is ERR)", "row",
      "A `tbb` division or remainder by zero yields ERR without a trap.",
      m10="v18_tbb_div_by_zero_is_err")

# -- failsafe-post
claim("vf0871", D, 871, "| `failsafe-post` | `failsafe` returns a positive value (D-014)", "row",
      "Every `exit` in `failsafe` is checked positive, one `failsafe-post` row each.",
      expect="sh:0", sh=obl(P_DIV, '''
want "failsafe-post rows (one per exit in failsafe)" "$(n npk_failsafe failsafe-post)" %d 10''' % FS_EXITS),
      wrong="one row for the function, or none")

# -- loop-step
claim("vf0872", D, 872, "| `loop-step` | a counted loop's computed step is positive (D-022)", "row",
      "A counted loop with a computed step is one `loop-step` row; one with a literal step has none.",
      expect="sh:0", sh=obl('''
func:fst = int64(int64:st) never fails {
    int64:acc = 0i64;
    till (3i64, 2i64) { acc = acc + 1i64; }
    till (5i64, st) { acc = acc + 1i64; }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fst(raw v64(1i64)));
    exit 0i32;
};''', '''
want "loop-step rows (one computed step, one literal)" "$(n fst loop-step)" 1 10'''),
      wrong="a row for the literal step too (2) or none")

claim("vf0872b", D, 872, "the compare at the loop's entry, `BadStep`", "row",
      "A computed step of zero traps BadStep at the loop's entry.",
      m10="l21_zero_step_computed_traps")

claim("vf0872c", D, 872, "a literal step is the checker's (TYPE-068) and has no row", "row",
      "A literal zero step is refused by the checker (TYPE-068).",
      m10="l19_zero_step_literal_refused")

# -- shift-range
P_SHIFT = '''
func:fsl = int32(int32:x, int32:n) never fails { pass (x << n); };
func:fsr = int32(int32:x, int32:n) never fails { pass (x >> n); };
func:fsk = int32(int32:x) never fails { pass (x << 3i32); };
func:fvs = uint8(uint8:a, uint8:k) never fails {
    simd<uint8, 8>:v = simd(a);
    simd<uint8, 8>:s = v << simd(k);
    pass s[0i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fsl(raw v32(1i32), raw v32(2i32)));
    discard(raw fsr(raw v32(8i32), raw v32(2i32)));
    discard(raw fsk(raw v32(1i32)));
    discard(raw fvs(raw vu8(3u8), raw vu8(1u8)));
    exit 0i32;
};'''

claim("vf0873", D, 873, "| `shift-range` | a shift's COMPUTED amount is inside `0..width-1` (D-277)", "row",
      "A shift by a computed amount (`<<` or `>>`) is one `shift-range` row; a shift by a literal amount has none.",
      expect="sh:0", sh=obl(P_SHIFT, '''
want "shift-range rows of x << n" "$(n fsl shift-range)" 1 10
want "shift-range rows of x >> n" "$(n fsr shift-range)" 1 11
want "shift-range rows of x << 3" "$(n fsk shift-range)" 0 12'''),
      wrong="no row for a computed amount, or one for a literal")

claim("vf0873b", D, 873, "the compare before the shift, `ShiftRange`", "row",
      "A computed shift amount equal to the width traps ShiftRange.",
      m10="s04_shift_amount_equals_width")

claim("vf0873c", D, 873, "a known amount is the checker's (TYPE-070) and has no row", "row",
      "A literal amount outside the range is refused, NITPICK-TYPE-070.",
      m10="s07_shift_literal_amount_refused")

claim("vf0873d", D, 873, "a `simd` shift's any-lane guard is one row over the lanes (D-282)", "row",
      "A `simd<uint8, 8>` shift by a computed splat is ONE `shift-range` row.",
      expect="sh:0", sh=obl(P_SHIFT, '''
want "shift-range rows of a simd<uint8, 8> shift" "$(n fvs shift-range)" 1 10'''),
      wrong="eight rows (one per lane) or none")

# -- prove
P_PROVE = '''
func:fpv = int32(int32:d) never fails {
    prove(d != 0i32);
    pass d;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fpv(raw v32(1i32)));
    exit 0i32;
};'''

claim("vf0874", D, 874, "| `prove` | a `prove(...)` holds under its path conditions", "row",
      "A `prove(...)` statement is one `prove` row with a solver query (fifth field `1`).",
      expect="sh:0", sh=obl(P_PROVE, '''
want "prove rows" "$(n fpv prove)" 1 10
want "their encoded field" "$(col fpv prove 5)" 1 11'''),
      wrong="no row, or a checker/unencoded row")

claim("vf0874b", D, 874, "| `prove` | a `prove(...)` holds under its path conditions | no |", "row",
      "`prove` has no guard: in the plain build a `prove` that is false at run time is not checked, and the program runs on.",
      expect="run:0", src=main_('''    int32:d = raw v32(0i32);
    prove(d != 0i32);
    exit 0i32;'''),
      wrong="a runtime assertion traps (Unreachable 95 or another arm)")

# -- assert-static
claim("vf0875", D, 875, "| `assert-static` | an `assert_static(...)` folds to true (the frontend)", "row",
      "An `assert_static(...)` statement is one `assert-static` row, decided by the frontend (`c` in the fifth field).",
      expect="sh:0", sh=obl(P_PICK, '''
want "assert-static rows" "$(n fas assert-static)" 1 10
want "their encoded field" "$(col fas assert-static 5)" c 11'''),
      wrong="no row, or a solver query")

claim("vf0875b", D, 875, "an `assert_static(...)` folds to true", "row",
      "An `assert_static` whose proposition folds to false is refused.",
      expect="refuse", src=main_('''    assert_static(1i32 + 1i32 == 3i32);
    exit 0i32;'''),
      wrong="accepted: the assertion ignored")

# -- disjoint
P_DISJ = '''
func:fdj = int32(int32:i, int32:j, int32[8]:arr) never fails {
    int32->:a = $$m arr[i => int64];
    int32->:b = $$m arr[j => int64];
    <-a = 7i32;
    <-b = 9i32;
    pass ((<-a) + (<-b));
};'''

claim("vf0876", D, 876, "| `disjoint` | two accesses of one root through computed indices name disjoint storage", "row",
      "Two `$$m` claims on one array through computed indices are one `disjoint` row.",
      expect="sh:0", sh=obl(P_DISJ + '''
func:main = int32(cstring[]:_~argv) {
    int32[8]:arr = [0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32];
    discard(raw fdj(raw v32(1i32), raw v32(2i32), arr));
    exit 0i32;
};''', '''
want "disjoint rows" "$(n fdj disjoint)" 1 10'''),
      wrong="no row: the overlap check outside the table")

claim("vf0876b", D, 876, "the byte-range compare at the second access, `BorrowOverlap`", "row",
      "Two live `$$m` claims through computed indices that name the same element trap BorrowOverlap at the second access.",
      expect="trap:BorrowOverlap", src=main_('''    int32[8]:arr = [0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32];
    int32:i = raw v32(2i32);
    int32:r = raw fdj(i, i, arr);
    if (r == 18i32) { exit 10i32; }
    exit 11i32;''', P_DISJ),
      wrong="no check: two aliasing mutable claims (18: exit 11, or 16)")

claim("vf0876c", D, 876, "a static overlap is the aliasing analysis's (BORROW-013) and has no row", "row",
      "Two live `$$m` claims of the same literal element are refused, BORROW-013.",
      expect="refuse:BORROW-013", src=main_('''    int32[8]:arr = [0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32];
    int32->:a = $$m arr[1i64];
    int32->:b = $$m arr[1i64];
    <-a = 7i32;
    <-b = 9i32;
    exit ((<-a) + (<-b) - 18i32);'''),
      wrong="accepted, or a run-time check")

# -- the floor kinds
P_KINDS_OBL = OBL_HEAD  # (the vf0848 program is reused below through its script)
S_NO_FLOOR = obl(P_DIV, '''
want "floor-spec rows written by the compiler" "$(awk -F'\\t' '$3 == "floor-spec"' ob/rows.txt | wc -l | tr -d ' ')" 0 10
want "floor-model rows written by the compiler" "$(awk -F'\\t' '$3 == "floor-model"' ob/rows.txt | wc -l | tr -d ' ')" 0 11''')

claim("vf0877", D, 877, "| `floor-spec` | a clause of a floor symbol's section in `runtime/npkrt.spec` holds", "row",
      "A `floor-spec` row states a clause of a floor symbol's spec section of its IR; its rows land in runtime/npkrt.obligations.",
      untestable=FLOOR)

claim("vf0877b", D, 877, "rows from the floor writer (1.5.6), never the compiler", "row",
      "The compiler never writes a `floor-spec` row.",
      expect="sh:0", sh=S_NO_FLOOR, wrong="a floor kind in a program's rows.txt")

claim("vf0878", D, 878, "| `floor-model` | a bounded protocol model's bad predicate is unreachable within its depth and preemption bound", "row",
      "A `floor-model` row states that a protocol model's bad predicate is unreachable within its bounds.",
      untestable=MODELS)

claim("vf0878b", D, 878, "rows from the floor writer over `runtime/models/`", "row",
      "The compiler never writes a `floor-model` row.",
      expect="sh:0", sh=S_NO_FLOOR, wrong="a floor kind in a program's rows.txt")

# ------------------------------------------------------ §7b's notes (881-973)
claim("vf0886", D, 886, "already refuses a lossy crossing at compile time (D-095)", "rule",
      "A checked integer `=>` that could lose data (int64 to int32) is refused at compile time.",
      m10="c03_narrow_signed_refused")

claim("vf0888", D, 888, "now traps `CastRange`", "rule",
      "A float's `=>!` to an integer is guarded by a CastRange trap (4117) in the emission.",
      expect=r"ir:@npk_trap\(i32 -?4117\)", src=main_('''    int32:x = raw vf64(2.5f64) =>! int32;
    exit (x - 2i32);'''),
      wrong="no trap: the conversion's poison unguarded")

claim("vf0895", D, 895, "`(|npk.len| base)` -- an uninterpreted function of the base", "rule",
      "`.len` of a slice is the uninterpreted `|npk.len|` applied to the base in the obligation text.",
      expect="sh:0", sh=obl('''
func:fl = int32(int32[]:xs) never fails {
    int32:acc = 0i32;
    for (int64:i in 0i64...xs.len) { acc = acc +% xs[i]; }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    discard(raw fl(a[0i64...4i64]));
    exit 0i32;
};''', '''
f=$(file_of fl); [ -n "$f" ] && [ -f "$f" ] || { echo "no obligation file for fl"; exit 10; }
grep -qE '\\(\\|npk\\.len\\| ' "$f" || { echo "no application of |npk.len| in $f"; exit 11; }'''),
      wrong="the length a fresh constant per read")

claim("vf0898", D, 898, "against are the same symbol and the row discharges", "rule",
      "Inside `for (i in 0...xs.len)` the loop bound and the element row's length are one symbol, so the row discharges.",
      untestable=Z3V)

claim("vf0899", D, 899, "length term (DEF-14's rule: a name a pointer may write is never named)", "rule",
      "An escaped name, and a length read through a call, have no length term: a row over a parameter's element is `open` unless the loop bounds it.",
      untestable=Z3V)

claim("vf0902", D, 902, "A RANGE SLICE IS ONE ROW for the pair the emitter tests in one `and`", "rule",
      "A range slice is ONE `bounds` row for the pair.",
      expect="sh:0", sh=obl(P_RANGE, '''
want "bounds rows of xs[lo...hi]" "$(n fz bounds)" 1 10'''),
      wrong="two rows, one per bound")

claim("vf0903", D, 903, "recorded at the RANGE node -- the index expression's rhs, not the index", "rule",
      "The range slice's row is keyed on the RANGE node, the key the emitter asks with.",
      untestable="[internal] which AST node keys the row is internal; its effect (the guard elided under a discharged row) needs a discharged row of a range slice, which only z3 gives honestly")

P_DEFER = '''
func:wander = int32(int32[]:xs, int32:k) never fails {
    int32:acc = 0i32;
    defer {
        acc = acc +% xs[k => int64];
    }
    if (k > 0i32) { pass acc; }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    int32[3]:xs = [1i32, 2i32, 3i32];
    discard(raw wander(xs[0i64...3i64], raw v32(1i32)));
    exit 0i32;
};'''

claim("vf0908", D, 908, "A GUARD INSIDE A `defer` BODY IS ONE ROW AND SEVERAL TRAPS (DEF-82)", "rule",
      "A guarded index inside a `defer` body that runs at two exits is ONE `bounds` row.",
      expect="sh:0", sh=obl(P_DEFER, '''
want "bounds rows of the defer body's xs[k]" "$(n wander bounds)" 1 10'''),
      wrong="one row per copy the emitter writes (2)")

claim("vf0912", D, 912, "one copy's traps times the copies", "rule",
      "That row's traps field is one copy's traps times the copies: 2 for a `defer` written at two exits.",
      expect="sh:0", sh=obl(P_DEFER, '''
want "the defer row's traps field" "$(col wander bounds 10)" 2 10'''),
      wrong="1: the row counting one copy where the build holds two (DEF-82)")

P_FS_ZERO = '''error:E9;
func:broken = int32() { fail E9; };
func:main = int32(cstring[]:_~argv) {
    int32:v = broken() ?! E9;
    exit (v + 1i32);
};
func:failsafe = int32(Error:e) {
@@DECL@@    pick (e) {
        (E9) { exit @@EXIT@@; },
        (EnsuresViolated) { exit 33i32; },
        (IntOverflow) { exit 93i32; },
        (HeapBadRequest) { exit 91i32; },
        (HeapOom) { exit 92i32; },
        (Unreachable) { exit 95i32; },
        (WildLeak) { exit 96i32; },
        (StackExhausted) { exit 106i32; },
        (MachineFault) { exit 107i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};'''

claim("vf0919", D, 919, "checked positive at the `exit` (EnsuresViolated, the trap route's re-entry", "rule",
      "`failsafe`'s `exit` operand is checked positive: a computed zero is EnsuresViolated, and the trap route's re-entry rule ends the process at 70.",
      expect="run:70", fs=False, src=P_FS_ZERO.replace("@@DECL@@", "    int32:z = raw v32(0i32);\n").replace("@@EXIT@@", "z"),
      wrong="unchecked: the process exits 0 (a trap reported as success), or failsafe re-entered (33)")

claim("vf0920", D, 920, "a literal that is not positive refused by", "rule",
      "A literal `exit` operand in `failsafe` that is not positive is refused by the checker, REACH-004.",
      expect="refuse:REACH-004", fs=False, src=P_FS_ZERO.replace("@@DECL@@", "").replace("@@EXIT@@", "0i32"),
      wrong="accepted: failsafe may report success")

claim("vf0921", D, 921, "so a discharged row elides that check", "rule",
      "A discharged `failsafe-post` row elides the `exit`'s positivity check in the verified build.",
      untestable=Z3V)

P_BODY = '''Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:narrow = int32(limit<r_pos> int32:n) { pass n; };'''
S_BODY_MAIN = '''    int32:r = narrow(raw v32(5i32)) ?! E9;
    exit (r - 5i32);'''

claim("vf0925", D, 925, "The guard a discharged row elides is the CALLEE's", "rule",
      "In the verified build a direct call whose `limit-subsume` row is discharged calls `<symbol>.body`, skipping the callee's entry check; in the plain build it calls the entry.",
      expect="sh:0", sh=elided(P_SUB, '''
want "calls of narrow.body in fcaller, plain build" "$(fbody fcaller p.ll | grep -c 'narrow\\.body')" 0 10
manifest '$3=="limit-subsume"'
elide
b=$(fbody fcaller e.ll | grep -c 'narrow\\.body')
[ "$b" -ge 1 ] || { echo "fcaller does not call narrow.body in the verified build"; exit 11; }'''),
      wrong="the discharged call still names the checked entry (11)")

claim("vf0927", D, 927, "its body under `<symbol>.body` and its ordinary symbol as the checked entry", "rule",
      "A sync function with a limited parameter emits a second define, `<symbol>.body`.",
      expect=r'ir:^define [^\n]*narrow\.body"?\(', src=main_(S_BODY_MAIN, P_BODY),
      wrong="one define: no body to call past the check")

claim("vf0928", D, 928, "(the entry checks, then a tail call of the body)", "rule",
      "The ordinary symbol is the checked entry, which ends in a tail call of the body.",
      expect=r"ir:tail call [^\n]*narrow\.body", src=main_(S_BODY_MAIN, P_BODY),
      wrong="the entry duplicating the body, or an ordinary call")

claim("vf0929", D, 929, "the manifest discharged names the body, every other call -- and every", "rule",
      "Without a manifest no call names the body except the entry's own tail call: the plain build's direct call names the entry.",
      expect=r'ir!:(?s)call [^\n]*narrow\.body"?\(.*call [^\n]*narrow\.body"?\(', src=main_(S_BODY_MAIN, P_BODY),
      wrong="main calling the body directly past the check")

claim("vf0931", D, 931, "A coroutine callee keeps one symbol and its call sites carry no", "rule",
      "An async callee with a limited parameter has no `.body` twin and its call site no `limit-subsume` row.",
      expect="sh:0", sh=obl(P_ASYNC_LIMIT, '''
want "limit-subsume rows at the await" "$(n main limit-subsume)" 0 10
want "fetchl.body occurrences in the emission" "$(grep -c 'fetchl\\.body' p.ll)" 0 11'''),
      wrong="a .body twin for a coroutine, or a row at its call")

claim("vf0933", D, 933, "runners hold the belt: every `.body` occurrence in an emission is its own", "rule",
      "The runners' belt: every `.body` occurrence is its define, the wrapper's tail call or a direct call, and the direct calls equal the discharged rows.",
      untestable=RUNNERS)

claim("vf0937", D, 937, "`exhaustive` (one", "rule",
      "`exhaustive` is one row per `pick`, both spellings: a `pick` statement and a `pick` expression give two rows.",
      expect="sh:0", sh=obl(P_PICK, '''
want "exhaustive rows of a pick statement and a pick expression" "$(n fpk exhaustive)" 2 10'''),
      wrong="the pick expression uncounted (1)")

claim("vf0940", D, 940, "`c` in `rows.txt`", "rule",
      "`exhaustive` and `assert-static` rows are inventory lines: `c` in rows.txt's fifth field.",
      expect="sh:0", sh=obl(P_PICK, '''
want "encoded field of exhaustive rows" "$(col fpk exhaustive 5)" c 10
want "encoded field of assert-static rows" "$(col fas assert-static 5)" c 11'''),
      wrong="a solver query (1) for a frontend decision")

claim("vf0941", D, 941, "query, tier `-`, word `none`", "rule",
      "A checker row's tier is `-`.",
      expect="sh:0", sh=obl(P_PICK, '''
want "tier of exhaustive rows" "$(col fpk exhaustive 11)" - 10
want "tier of assert-static rows" "$(col fas assert-static 11)" - 11'''),
      wrong="a theory word (int) for a row no solver decides")

claim("vf0941b", D, 941, "`prove` is decided by z3 like a guarded kind", "rule",
      "A `prove` row carries a solver query (fifth field `1`).",
      expect="sh:0", sh=obl(P_PROVE, '''
want "encoded field of the prove row" "$(col fpv prove 5)" 1 10'''),
      wrong="a checker row (c)")

claim("vf0942", D, 942, "and is the ONE kind whose non-discharge refuses the verified build", "rule",
      "The verified build refuses a program whose `prove` row is not discharged (NITPICK-VERIFY-001), while the plain build accepts it.",
      expect="sh:0", sh='''cat > p.npk <<'NPK_EOF'
''' + prog(P_PROVE) + '''NPK_EOF
"$NPKC" p.npk -o p.ll >out.txt 2>err.txt; rc=$?
[ "$rc" -eq 0 ] || { echo "plain build: npkc exit $rc"; head -c 600 err.txt; exit 3; }
echo '# nitpick.obligations v1' > m.txt
"$NPKC" p.npk -o e.ll --elide m.txt >out2.txt 2>err2.txt; rc=$?
[ "$rc" -eq 1 ] || { echo "verified build without the prove discharged: npkc exit $rc"; head -c 600 err2.txt; exit 10; }
grep -q 'NITPICK-VERIFY-001' err2.txt || { echo "refused without VERIFY-001"; head -c 600 err2.txt; exit 11; }
exit 0''',
      wrong="the verified build accepts an unproven claim (10)")

claim("vf0944", D, 944, "a computed step's compare, a literal step being the checker's", "rule",
      "A negative computed step traps BadStep at the loop's entry.",
      m10="l22_negative_step_computed_traps")

claim("vf0946", D, 946, "`err-exit` produces rows, and the", "rule",
      "`err-exit` rows are produced: a tbb comparison has one (see vf0870).",
      expect="sh:0", sh=obl(P_TBB_CMP, '''
want "err-exit rows of one tbb32 comparison" "$(n fte err-exit)" 1 10'''),
      wrong="no row")

claim("vf0947", D, 947, "twisted kinds are terms. A `tbb`/`tfp`/`dim256`/`trit`/`tryte`/`nit`/`nyte`", "rule",
      "A twisted value is an Int in its carrier's range, ERR the carrier's most negative value; `ERR` is MIN, `is_err(x)` is `(= x MIN)`, a symbol's axiom 'ERR or inside the valid range'.",
      untestable=Z3ENC)

claim("vf0953", D, 953, "emitter's own `ite`: saturate-to-ERR on `+ - *` and negation", "rule",
      "Twisted `+ - *` and negation saturate to ERR, and ERR is sticky.",
      m10="m13_tbb_err_sticky")

claim("vf0954", D, 954, "floor multiply `(div (* a b) 2^F)` and truncating divide `(npk_sdiv (* a", "rule",
      "The encoder models `tfp`'s `*` as the floor multiply and `/` as the truncating divide, narrowed by the range test, as the emitter computes them.",
      untestable=Z3ENC)

claim("vf0955", D, 955, "a zero divisor ERR", "rule",
      "A twisted division by zero is ERR.",
      m10="v18_tbb_div_by_zero_is_err")

P_KLEENE = main_('''    trit:a = raw vtr(1);
    trit:b = raw vtr(-1);
    trit:z = raw vtr(0);
    if ((a & b) != -1) { exit 10i32; }
    if ((a | b) != 1) { exit 11i32; }
    if ((z & a) != 0) { exit 12i32; }
    if ((z | b) != 0) { exit 13i32; }
    exit 0i32;''', "func:vtr = trit(trit:x) never fails { pass x; };")

claim("vf0956", D, 956, "digits' `&`/`|` as min/max", "rule",
      "The ternary digits' `&` and `|` are the Kleene min and max: 1 & -1 is -1, 1 | -1 is 1, 0 & 1 is 0, 0 | -1 is 0.",
      expect="run:0", src=P_KLEENE,
      wrong="two's-complement bitwise and/or: 1 & -1 = 1 (exit 10), 1 | -1 = -1 (exit 11)")

claim("vf0956b", D, 956, "`dim256` is `tfp256`", "rule",
      "To the solver `dim256` is `tfp256`.",
      untestable=Z3ENC)

claim("vf0957", D, 957, "one per `-4100` site", "rule",
      "The `TbbErr` guard is a `-4100` trap site: a comparison of computed tbb values emits `@npk_trap(i32 -4100)`.",
      expect=r"ir:@npk_trap\(i32 -4100\)", src=main_('''    tbb32:a = raw vt32(1tbb32);
    if (a == raw vt32(1tbb32)) { exit 0i32; }
    exit 10i32;'''),
      wrong="no TbbErr trap at a twisted comparison")

claim("vf0958", D, 958, "comparison, the operand not ERR at a cast out of its family (both", "rule",
      "An ERR operand at a cast out of its family traps TbbErr (the `=>!` spelling).",
      expect="trap:TbbErr", src=main_('''    tbb32:e = raw vt32(2147483647tbb32) + raw vt32(1tbb32);
    int64:x = e =>! int64;
    if (x == 0i64) { exit 10i32; }
    exit 11i32;'''),
      wrong="ERR's carrier value cast silently (10, 11)")

claim("vf0960", D, 960, "its fact is a hypothesis after the site (every continuing", "rule",
      "An err-exit row's fact is a hypothesis after its site.",
      untestable=Z3ENC)

claim("vf0961", D, 961, "and a discharged row's guard is one `llvm.assume`", "rule",
      "A discharged err-exit row's guard becomes one `llvm.assume`.",
      expect="sh:0", sh=elided(P_TBB_CMP, '''
want "TbbErr traps in fte, plain build" "$(traps fte p.ll -4100)" 1 10
manifest '$3=="err-exit"'
elide
want "llvm.assume calls in fte, verified build" "$(assumes fte e.ll)" 1 11
want "TbbErr traps in fte, verified build" "$(traps fte e.ll -4100)" 0 12'''),
      wrong="the guard kept under a discharged row (12) or no assume (11)")

P_FRAC = '''
func:ffr = int32(frac32:a, frac32:b) never fails {
    if (a < b) { pass 1i32; }
    pass 0i32;
};
func:main = int32(cstring[]:_~argv) {
    frac32:x = raw v32(1i32) => frac32;
    frac32:y = raw v32(2i32) => frac32;
    discard(raw ffr(x, y));
    exit 0i32;
};'''

claim("vf0962", D, 962, "A `frac` or a tfp-element `complex` guard is a row over an aggregate the", "rule",
      "A `frac32` comparison's TbbErr guard is one `err-exit` row, `unencoded` (fifth field `0`).",
      expect="sh:0", sh=obl(P_FRAC, '''
want "err-exit rows of a frac32 comparison" "$(n ffr err-exit)" 1 10
want "their encoded field" "$(col ffr err-exit 5)" 0 11'''),
      wrong="no row (10), or an encoded row for a value the walk has no term for (11)")

claim("vf0963", D, 963, "its trap kept", "rule",
      "The frac guard's trap is kept: comparing a `frac32` ERR traps TbbErr.",
      expect="trap:TbbErr", src=main_('''    frac32:z = raw v32(0i32) => frac32;
    frac32:e = (raw v32(5i32) => frac32) / z;
    frac32:one = raw v32(1i32) => frac32;
    if (e < one) { exit 10i32; }
    exit 11i32;'''),
      wrong="the comparison decided on ERR (10, 11)")

claim("vf0965", D, 965, "twisted division has no row: it never traps.", "rule",
      "A twisted division has no row (see vf0870f's program).",
      expect="sh:0", sh=obl(P_TBB_DIV, '''
want "rows of a tbb32 division" "$(n ftd '*')" 0 10'''),
      wrong="a row for a division that never traps")

claim("vf0966", D, 966, "subject encodes (its `$` the Int term)", "rule",
      "A `limit` over a twisted subject is an encoded row (fifth field `1`).",
      expect="sh:0", sh=obl('''
Rules<tbb32>:r_ok = { !is_err($), $ != 0tbb32 };
func:flt = int32(tbb32:a) never fails {
    limit<r_ok> tbb32:y = a;
    if (y == 6tbb32) { pass 1i32; }
    pass 0i32;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw flt(raw vt32(6tbb32)));
    exit 0i32;
};''', '''
want "limit rows over a tbb32 subject" "$(n flt limit)" 1 10
want "their encoded field" "$(col flt limit 5)" 1 11'''),
      wrong="`unencoded` (0) for a twisted subject")

claim("vf0967", D, 967, "`$` as the subject and each clause as a fact for the next (the predicate", "rule",
      "A rule's predicate traps on its FIRST false clause: with `{ $ != 0, 100 / $ > 1 }` a zero traps LimitViolated, never DivByZero.",
      expect="trap:LimitViolated", src=main_('''    limit<r_div> int32:x = raw v32(0i32);
    if (x == 0i32) { exit 10i32; }
    exit 11i32;''', "Rules<int32>:r_div = { $ != 0i32, 100i32 / $ > 1i32 };"),
      wrong="every clause evaluated: DivByZero (97) from the second")

claim("vf0968", D, 968, "A guard's fact is never pushed under a", "rule",
      "A guard's fact is never pushed under a quiet encoding nor from inside a contract clause encoded for its own row (DEF-33).",
      untestable=Z3ENC)

# ------------------------------------------------ D-281 (floats) and D-282 notes
P_FLT = '''
Rules<flt64>:r_unit = { $ >= 1.0f64, $ <= 2.0f64 };
Rules<flt32>:r_u32 = { $ >= 1.0f32, $ <= 2.0f32 };
Rules<flt64>:r_neg = { !($ < 1.0f64), !($ > 2.0f64) };
func:ratio = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:q = a / b;
    prove(q >= 0.5f64);
    pass q;
};
func:ratio32 = flt32(limit<r_u32> flt32:a, limit<r_u32> flt32:b) never fails {
    flt32:q = a / b;
    prove(q >= 0.5f32);
    pass q;
};
func:hyp = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:hypu = flt64(flt64:a, flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:hypn = flt64(limit<r_neg> flt64:a, limit<r_neg> flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:sameq = bool(limit<r_unit> flt64:a) never fails {
    prove(a == a);
    pass (a == a);
};
func:fent = tbb32(flt64:x) never fails { pass (x => tbb32); };
func:ffl = flt64(flt64:a, flt64:b) never fails { pass (((a + b) * (a - b)) / b); };
func:ffm = flt64(flt64:a, flt64:b) never fails { pass (a % b); };
func:main = int32(cstring[]:_~argv) {
    discard(raw ratio(1.5f64, 2.0f64));
    discard(raw ratio32(1.5f32, 2.0f32));
    discard(raw hyp(1.5f64, 2.0f64));
    discard(raw hypu(raw vf64(1.5f64), raw vf64(2.0f64)));
    discard(raw hypn(1.5f64, 2.0f64));
    discard(raw sameq(1.5f64));
    discard(raw fent(raw vf64(3.5f64)));
    discard(raw ffl(raw vf64(1.5f64), raw vf64(2.0f64)));
    discard(raw ffm(raw vf64(1.5f64), raw vf64(2.0f64)));
    exit 0i32;
};'''

claim("vf0975", D, 975, "FLOATS ARE TERMS IN TWO TIERS, and", "rule",
      "A float obligation's row carries the tier the encoder names: a `prove` over `flt64` values has tier `fp` in rows.txt's eleventh field.",
      expect="sh:0", sh=obl(P_FLT, '''
want "tier of ratio's prove row" "$(col ratio prove 11)" fp 10'''),
      wrong="tier `int` (the constant of 1.5.0) or `-`")

claim("vf0977", D, 977, "value is a term of the IEEE sort (`(_ FloatingPoint 8 24)` / `(_", "rule",
      "A `flt32` value is a term of sort `(_ FloatingPoint 8 24)` and a `flt64` one of `(_ FloatingPoint 11 53)` in the obligation text.",
      expect="sh:0", sh=obl(P_FLT, '''
f=$(file_of ratio); g=$(file_of ratio32)
[ -n "$f" ] && [ -n "$g" ] || { echo "no obligation file for ratio or ratio32"; exit 10; }
grep -qF '(_ FloatingPoint 11 53)' "$f" || { echo "flt64 not (_ FloatingPoint 11 53) in $f"; exit 11; }
grep -qF '(_ FloatingPoint 8 24)' "$g" || { echo "flt32 not (_ FloatingPoint 8 24) in $g"; exit 12; }'''),
      wrong="floats opaque (no FloatingPoint sort), or a flt32 widened to the double sort (12)")

claim("vf0979", D, 979, "under SMT-LIB's IEEE semantics — `fp.add`/`sub`/`mul`/`div` under RNE", "rule",
      "A float division is `fp.div` under RNE in the obligation text.",
      expect="sh:0", sh=obl(P_FLT, '''
f=$(file_of ratio); [ -n "$f" ] || { echo "no obligation file for ratio"; exit 10; }
grep -qE 'fp\\.div (RNE|roundNearestTiesToEven)' "$f" || { echo "no fp.div under RNE in $f"; exit 11; }'''),
      wrong="the quotient an opaque symbol, or another rounding mode")

claim("vf0980", D, 980, "`#sqrt` as `fp.sqrt RNE`", "rule",
      "`#sqrt` is `fp.sqrt` under RNE in the obligation text.",
      expect="sh:0", sh=obl(P_FLT, '''
f=$(file_of hyp); [ -n "$f" ] || { echo "no obligation file for hyp"; exit 10; }
grep -qE 'fp\\.sqrt (RNE|roundNearestTiesToEven)' "$f" || { echo "no fp.sqrt under RNE in $f"; exit 11; }'''),
      wrong="#sqrt opaque")

P_NAN = main_('''    flt64:n = raw vf64(0.0f64) / raw vf64(0.0f64);
    if (n == n) { exit 10i32; }
    if (!(n != n)) { exit 11i32; }
    if (n < 1.0f64) { exit 12i32; }
    if (n >= 1.0f64) { exit 13i32; }
    exit 0i32;''')

claim("vf0981", D, 981, "`fcmp` writes (`==` is `fp.eq`, `!=` its negation, so NaN compares as the", "rule",
      "The machine's float compares are the ordered ones with `!=` their negation: NaN == NaN is false, NaN != NaN is true, and NaN < 1 and NaN >= 1 are both false.",
      expect="run:0", src=P_NAN,
      wrong="unordered compares (NaN == NaN true: 10; NaN < 1 or >= 1 true: 12, 13) or an ordered `!=` (11)")

P_DROUND = main_('''    flt32:a = raw vf32(1.0000000596046448309f32);
    if (a != 1.0f32) { exit 10i32; }
    exit 0i32;''')

claim("vf0983", D, 983, "text denotes (a `flt32` literal rounded twice, as the emitter's double-then-", "rule",
      "A `flt32` literal is rounded twice, to double then to float: 1.0000000596046448309 (just above the midpoint 1 + 2^-24) becomes 1 + 2^-24 as a double and then 1.0 (a tie, to even) as a flt32, where a single rounding gives 1 + 2^-23.",
      expect="run:0", src=P_DROUND,
      wrong="the literal rounded once to float: 1.0000001 (exit 10)")

claim("vf0984", D, 984, "an integer entering `to_fp RNE (to_real x)`, a", "rule",
      "An integer entering a float is `to_fp RNE`, a widening exact, a narrowing `=>!` rounded, in the obligation text.",
      untestable=Z3ENC)

claim("vf0985", D, 985, "`%` (`frem`) and a float LEAVING", "rule",
      "A float `%` and a float leaving to an integer are opaque values to the solver.",
      untestable=Z3ENC)

claim("vf0987", D, 987, "itself carries a `cast-range` row over the operand since 1.5.8b step 5", "rule",
      "A float's `=>!` to an integer is a `cast-range` row over the float operand.",
      expect="sh:0", sh=obl(P_CAST, '''
want "cast-range rows of f =>! int32" "$(n fc cast-range)" 1 10'''),
      wrong="no row")

claim("vf0988", D, 988, "`flt128` is storage (D-143) and has no term.", "rule",
      "`flt128` has no term to the solver.",
      untestable=Z3ENC)

claim("vf0988b", D, 988, "Every float value is NAMED and its definition", "rule",
      "Every float value is a named symbol whose definition is recorded.",
      untestable="[internal] the encoder's naming of float values; no outcome depends on it outside the verdicts")

claim("vf0989", D, 989, "Floats never trap: no row", "rule",
      "Float arithmetic has no rows: a function of float `+ - * /` and one of float `%` have none.",
      expect="sh:0", sh=obl(P_FLT, '''
want "rows of a float + - * / function" "$(n ffl '*')" 0 10
want "rows of a float % function" "$(n ffm '*')" 0 11'''),
      wrong="a div-zero row for a float division (DEF-37's shape)")

claim("vf0990", D, 990, "is theirs — what the terms buy is that a `limit`, a contract, an", "rule",
      "Over floats, a `limit`, a `prove` and the `TbbErr` guard of a float entering `tbb` are encoded rows (fifth field `1`).",
      expect="sh:0", sh=obl(P_FLT, '''
want "encoded field of ratio's limit rows" "$(col ratio limit 5)" 1 10
want "encoded field of ratio's prove row" "$(col ratio prove 5)" 1 11
want "encoded field of fent's err-exit row" "$(col fent err-exit 5)" 1 12'''),
      wrong="`unencoded` (0) float rows, as before 1.5.4b")

S_TIERS = obl('''
Rules<flt64>:r_unit = { $ >= 1.0f64, $ <= 2.0f64 };
Rules<string>:r_ne = { $.len > 0i64 };
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fbx = int32(int32:k, int32:m) never fails { pass (100i32 / ((k & m) | 1i32)); };
func:ratio = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:q = a / b;
    prove(q >= 0.5f64);
    pass q;
};
func:fp1 = int32(int32:x) never fails {
    int32:r = 0i32;
    pick (x) { (1i32) { r = 10i32; }, (*) { r = 20i32; } }
    pass r;
};
func:flim = int64(int64:n) never fails {
    limit<r_ne> string:s = "abc";
    if (n > 0i64) { s = "de"; }
    pass s.len;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fbx(raw v32(6i32), raw v32(3i32)));
    discard(raw ratio(1.5f64, 2.0f64));
    discard(raw fp1(raw v32(1i32)));
    discard(raw flim(raw v64(1i64)));
    exit 0i32;
};''', '''
want "tier of an Int division's div-zero row" "$(col fq div-zero 11)" int 10
want "tier of a div-zero row over (k & m) | 1" "$(col fbx div-zero 11)" bv 11
want "tier of a flt64 prove row" "$(col ratio prove 11)" fp 12
want "tier of a checker (exhaustive) row" "$(col fp1 exhaustive 11)" - 13
want "tier of an unencoded (string limit) row" "$(col flim limit 11)" - 14''')

claim("vf0992", D, 992, "THE TIER COLUMN: `rows.txt`'s eleventh", "rule",
      "rows.txt's eleventh field is the tier: `int` for an Int/Bool cone, `bv` where a bit-vector crossing is, `fp` where a float sort is, `-` for an unencoded or checker row.",
      expect="sh:0", sh=S_TIERS,
      wrong="one constant word for every row (int), or `-` missing for checker/unencoded rows")

claim("vf0995", D, 995, "runners carry it into the manifest", "rule",
      "Both runners carry the tier into the manifest.",
      untestable=Z3V)

S_TWIN = obl(P_FLT, '''
f=$(file_of hyp); [ -n "$f" ] || { echo "no obligation file for hyp"; exit 10; }
t=${f%.smt2}.t2.smt2
[ -f "$t" ] || { echo "no twin $t for hyp's bounded fp prove"; ls ob | head -40; exit 11; }
[ -f ob/index.t2.txt ] || { echo "no index.t2.txt"; exit 12; }
nn=$(basename "$f" .smt2)
grep -q "^$nn" ob/index.t2.txt || { echo "index.t2.txt does not name $nn"; exit 13; }''')

claim("vf0996", D, 996, "(D-218 (5)): for every `fp` row the encoder also writes a twin query", "rule",
      "For an `fp` row whose floats are bounded by literal comparisons (a `limit` rule), the encoder writes a twin `NNNN.t2.smt2` beside the tier-1 file and names it in `index.t2.txt`.",
      expect="sh:0", sh=S_TWIN,
      wrong="no twin: tier 2 never asked")

claim("vf0998", D, 998, "Real — an operation a fresh Real within `eps·|v| + eta` of its exact", "rule",
      "In the twin every float is a Real and every operation a fresh Real within eps·|v| + eta of its exact result; a square root r >= 0 with r² inside v·(1 ∓ eps)².",
      untestable=Z3ENC)

S_NOTWIN = r'''
nt() { f=$(file_of "$1"); [ -n "$f" ] || { echo "no obligation file for $1"; exit "$2"; }; t=${f%.smt2}.t2.smt2; [ ! -f "$t" ] || { echo "$1 has a twin $t"; exit "$2"; }; }
'''

claim("vf1001", D, 1001, "CONDITIONS, else no twin: (i) every float symbol no hypothesis defines is", "rule",
      "Condition (i): with the floats unbounded (plain parameters), the same `#sqrt` prove gets no twin.",
      expect="sh:0", sh=obl(P_FLT, S_NOTWIN + '''
nt hypu 10'''),
      wrong="a twin over unbounded floats, whose Real reading ignores NaN and the infinities")

claim("vf1004", D, 1004, "(ii) every operation's magnitude within the normal range, a", "rule",
      "Condition (ii): every operation's magnitude in the normal range, divisors nonzero and roots' arguments non-negative are conjoined to the twin's goal.",
      untestable=Z3ENC)

claim("vf1007", D, 1007, "(iii) the goal a comparison or a Boolean combination of comparisons — an", "rule",
      "Condition (iii): a goal that is an `fp.eq` (`prove(a == a)`) stays tier 1: no twin, even with the float bounded.",
      expect="sh:0", sh=obl(P_FLT, S_NOTWIN + '''
nt sameq 10'''),
      wrong="a twin for an fp.eq goal, whose Real reading loses NaN")

claim("vf1008", D, 1008, "The runner asks tier 1 first", "rule",
      "The runner asks tier 1 first and the twin once for a `budget` row; `unsat` discharges it with tier `real`; a tier-1 `sat` is never retried.",
      untestable=Z3V)

claim("vf1011", D, 1011, "`flt_tier2.npk` is the shape D-218 (5)", "rule",
      "`#sqrt(a*a + b*b) >= 0.0` under bounded a, b is `unknown` in QF_FP and `unsat` in the twin.",
      untestable=Z3V)

P_SIMD_BOTH = P_SIMD_DIV.split("func:main")[0] + '''func:fvs = uint8(uint8:a, uint8:k) never fails {
    simd<uint8, 8>:v = simd(a);
    simd<uint8, 8>:s = v << simd(k);
    pass s[0i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fv(raw v32(8i32), raw v32(6i32), raw v32(2i32), raw v32(3i32)));
    discard(raw fw(raw vu32(8u32), raw vu32(2u32)));
    discard(raw fvs(raw vu8(3u8), raw vu8(1u8)));
    exit 0i32;
};'''

claim("vf1015", D, 1015, "A `simd<T, N>` value is N scalar", "rule",
      "A `simd<T, N>`'s any-lane guards are one row each: its division one `div-zero` row, its shift one `shift-range` row.",
      expect="sh:0", sh=obl(P_SIMD_BOTH, '''
want "div-zero rows of a simd<int32, 4> division" "$(n fv div-zero)" 1 10
want "shift-range rows of a simd<uint8, 8> shift" "$(n fvs shift-range)" 1 11'''),
      wrong="one row per lane")

claim("vf1016", D, 1016, "The lanes ride EXPRESSIONS", "rule",
      "A simd value's lanes are terms carried by expression and by binding (constructor, splat, lane-wise operations, `[i]`, `.len`, `.any()`/`.all()`, `sum`/`min`/`max`, casts).",
      untestable=Z3ENC)

claim("vf1028", D, 1028, "Anything else (a call's value, a computed", "rule",
      "A call's value or a computed index is N opaque lanes; the vector itself has no scalar term.",
      untestable=Z3ENC)

claim("vf1029", D, 1029, "THE ROWS: a", "rule",
      "A `simd` division's any-lane guard is ONE `div-zero` row over the lanes' conjunction.",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "div-zero rows of a simd<int32, 4> division" "$(n fv div-zero)" 1 10'''),
      wrong="one row per lane")

claim("vf1031", D, 1031, "of the lanes' conditions and, for a signed element, one `div-min` row", "rule",
      "For a signed element the simd division also has one `div-min` row; an unsigned element none.",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "div-min rows, simd<int32, 4>" "$(n fv div-min)" 1 10
want "div-min rows, simd<uint32, 4>" "$(n fw div-min)" 0 11'''),
      wrong="per-lane rows, or a div-min row for an unsigned element")

claim("vf1032", D, 1032, "likewise; a `simd` shift's any-lane guard one `shift-range` row over its", "rule",
      "A `simd` shift's any-lane guard is one `shift-range` row.",
      expect="sh:0", sh=obl(P_SHIFT, '''
want "shift-range rows of a simd<uint8, 8> shift" "$(n fvs shift-range)" 1 10'''),
      wrong="one row per lane")

claim("vf1033", D, 1033, "conjunction — the emitter's one trap per site, one group", "rule",
      "A simd any-lane guard is one trap per site: the simd division's `div-zero` row keeps one trap (traps field 1).",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "traps field of the simd division's div-zero row" "$(col fv div-zero 10)" 1 10'''),
      wrong="a trap per lane (4)")

claim("vf1034", D, 1034, "The `unencoded` producers of 1.5.0 and", "rule",
      "A `simd` division and a `simd` shift are no longer `unencoded`: their rows carry a query (fifth field `1`).",
      expect="sh:0", sh=obl(P_SIMD_BOTH, '''
want "encoded field of the simd division's div-zero row" "$(col fv div-zero 5)" 1 10
want "encoded field of the simd shift's shift-range row" "$(col fvs shift-range 5)" 1 11'''),
      wrong="0: the 1.5.0 `unencoded` producers still live")

P_LIM_STRUCT = '''
struct:Pt = { int32:x; int32:y; };
Rules<Pt>:r_q = { $.x >= 0i32 };
func:fls = int32(int32:a) never fails {
    limit<r_q> Pt:p = Pt{ x: a, y: 0i32 };
    pass p.x;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fls(raw v32(1i32)));
    exit 0i32;
};'''
S_LIM_STRUCT = obl(P_LIM_STRUCT, '''
[ "$(n fls limit)" -ge 1 ] || { echo "no limit row for a limit over a struct"; exit 10; }
want "encoded field of a limit over a struct" "$(col fls limit 5)" 0 11''')

claim("vf1036", D, 1036, "producers are a `limit` over a subject no theory covers (a string, a struct,", "rule",
      "A `limit` over a struct subject is an `unencoded` row (fifth field `0`).",
      expect="sh:0", sh=S_LIM_STRUCT,
      wrong="an encoded row (1): the text behind D-317's aggregate terms")

claim("vf1037", D, 1037, "and the `TbbErr` guards over a `frac` or a tfp-`complex`", "rule",
      "The TbbErr guard of a `frac32` comparison is an `unencoded` row.",
      expect="sh:0", sh=obl(P_FRAC, '''
want "encoded field of a frac32 comparison's err-exit row" "$(col ffr err-exit 5)" 0 10'''),
      wrong="an encoded row")

claim("vf1039", D, 1039, "The verdict column is `discharged` (unsat), `open` (sat", "rule",
      "The manifest's verdict is `discharged` (unsat), `open` (sat), `budget` (unknown under the rlimit), `unencoded` or `checker`.",
      untestable=Z3V)

claim("vf1043", D, 1043, "The elision", "rule",
      "The manifest's elision column is `elided`, `retained`, or `none` for a kind with no guard.",
      untestable=Z3V)

# ----------------------------------------------------------- §7c the theories
claim("vf1050", D, 1050, "a proposition holds only where its evaluation does not trap", "rule",
      "A proposition holds only where its evaluation does not trap: a `requires` clause whose own division meets a zero divisor traps DivByZero at run time, not RequiresViolated.",
      expect="trap:DivByZero", src=main_('''    int32:r = fdz(raw v32(0i32)) ?! E9;
    if (r == 0i32) { exit 10i32; }
    exit 11i32;''', '''error:E9;
func:fdz = int32(int32:d) requires 100i32 / d > 0i32 { pass d; };'''),
      wrong="the clause read as false (RequiresViolated 115) or the division unguarded (a machine fault)")

claim("vf1051", D, 1051, "Every guard met inside a contract clause, an", "rule",
      "Every guard met inside a clause, invariant conjunct, rule clause or `prove` is conjoined into the proposition's term and pushed as a hypothesis nowhere.",
      untestable=Z3ENC)

P_INTS = '''
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fd2 = int32(int32:a, int32:b, int32:c) never fails { pass ((a / b) / c); };
func:fm2 = int32(int32:a, int32:b, int32:c) never fails { pass ((a % b) / c); };
func:fmk = int32(int32:k) never fails { pass (100i32 / ((k & 7i32) + 1i32)); };
func:fbx = int32(int32:k, int32:m) never fails { pass (100i32 / ((k & m) | 1i32)); };
func:fbs = int32(int32:x, int32:n) never fails { pass (100i32 / ((x << n) | 1i32)); };
func:fbw = int128(int128:k, int128:m) never fails { pass (100i128 / ((k & m) | 1i128)); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fd2(raw v32(70i32), raw v32(2i32), raw v32(5i32)));
    discard(raw fm2(raw v32(7i32), raw v32(4i32), raw v32(1i32)));
    discard(raw fmk(raw v32(6i32)));
    discard(raw fbx(raw v32(6i32), raw v32(3i32)));
    discard(raw fbs(raw v32(1i32), raw v32(2i32)));
    discard(raw fbw(raw vi128(6i128), raw vi128(3i128)));
    exit 0i32;
};'''
S_FILE = r'''
fof() { f=$(file_of "$1"); [ -n "$f" ] && [ -f "$f" ] || { echo "no obligation file for $1" >&2; exit "$2"; }; echo "$f"; }
'''

claim("vf1063", D, 1063, "`intN`/`uintN` symbol is an `Int` with the axiom of its range", "rule",
      "A plain integer is an unbounded `Int` to the solver: the obligation file of an int32 division declares Int symbols and no bit-vector sort.",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fq 10) || exit 10
grep -qE '\\) Int\\)|\\(\\) Int|Int\\)' "$f" || { echo "no Int symbol in $f"; exit 11; }
if grep -q 'BitVec' "$f"; then echo "a BitVec sort in $f"; exit 12; fi'''),
      wrong="int32 as a 32-bit bit-vector (12)")

claim("vf1065", D, 1065, "truncating `npk_sdiv`/`npk_srem` as the machine's, with the D-007 pair as", "rule",
      "`/` and `%` are the truncating `npk_sdiv` / `npk_srem` in the obligation text (a quotient or remainder inside another division's cone).",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fd2 10) || exit 10
grep -q 'npk_sdiv' "$f" || { echo "no npk_sdiv in $f"; exit 11; }
g=$(fof fm2 12) || exit 12
grep -q 'npk_srem' "$g" || { echo "no npk_srem in $g"; exit 13; }'''),
      wrong="SMT-LIB's flooring div/mod standing for the machine's truncation")

claim("vf1066", D, 1066, "rows. A `bool` is `Bool`, a pattern's literal is read under the selector's", "rule",
      "A `bool` is `Bool`, a pattern's literal is read under the selector's type, and a path condition is a hypothesis in its arm.",
      untestable=Z3ENC)

claim("vf1069", D, 1069, "`x << n` and `x >> n` are defined for", "rule",
      "`x >> n` with a computed n equal to the width traps ShiftRange: shifts are defined for 0 <= n < width only.",
      m10="s06_right_shift_amount_width")

claim("vf1071", D, 1071, "known amount outside the range is `NITPICK-TYPE-070` at the shift (both", "rule",
      "A known amount outside the range is NITPICK-TYPE-070 for `>>` in its compound spelling too: `x >>= 32i32` on an int32.",
      expect="refuse:NITPICK-TYPE-070", src=main_('''    int32:x = raw v32(1i32);
    x >>= 32i32;
    exit x;'''),
      wrong="accepted: a run-time trap, a mask (x >> 0) or 0")

claim("vf1072", D, 1072, "operators, both spellings, the folder's bound the type's width)", "rule",
      "The folder's bound is the operand type's width: `int8 << 8i8` is NITPICK-TYPE-070.",
      expect="refuse:NITPICK-TYPE-070", src=main_('''    int8:y = raw v8(1i8) << 8i8;
    exit (y => int32);'''),
      wrong="accepted (a bound of 32 or 64 for every width)")

claim("vf1073", D, 1073, "amount is one unsigned compare on its carrier (`n <u W`, a negative amount", "rule",
      "A negative computed amount reads as huge and traps ShiftRange.",
      m10="s05_shift_amount_negative")

claim("vf1074", D, 1074, "reading as huge) trapping `ShiftRange` (−4115)", "rule",
      "A computed shift's guard is a `ShiftRange` trap, code -4115, in the emission.",
      expect=r"ir:@npk_trap\(i32 -4115\)", src=main_('''    int32:y = raw v32(1i32) << raw v32(3i32);
    exit (y - 8i32);'''),
      wrong="no guard (LLVM's poison for an oversized shift)")

claim("vf1075", D, 1075, "and, discharged, one `llvm.assume`", "rule",
      "In the verified build a discharged `shift-range` row's guard is one `llvm.assume` and no ShiftRange trap.",
      expect="sh:0", sh=elided(P_SHIFT, '''
want "ShiftRange traps in fsl, plain build" "$(traps fsl p.ll -4115)" 1 10
manifest '$3=="shift-range"'
elide
want "llvm.assume calls in fsl, verified build" "$(assumes fsl e.ll)" 1 11
want "ShiftRange traps in fsl, verified build" "$(traps fsl e.ll -4115)" 0 12'''),
      wrong="the guard kept under a discharged row (12), or removed with no assume (11)")

claim("vf1076", D, 1076, "hypothesis after the site either way", "rule",
      "A shift's range goal is a hypothesis after the site whether or not its row is discharged.",
      untestable=Z3ENC)

S_INT_FORM = obl(P_INTS, S_FILE + '''
f=$(fof fmk 10) || exit 10
if grep -q 'int2bv' "$f"; then echo "a bit-vector crossing for k & 7 in $f"; exit 11; fi
want "tier of the div-zero row over (k & 7) + 1" "$(col fmk div-zero 11)" int 12''')

claim("vf1081", D, 1081, "Wherever an operand is a numeral the encoder knows", "rule",
      "With a numeral operand a bitwise operation is Int arithmetic: `(k & 7) + 1` as a divisor crosses into no bit-vector theory (no `int2bv`, tier `int`).",
      expect="sh:0", sh=S_INT_FORM,
      wrong="a bit-vector crossing for a numeral mask (tier bv)")

claim("vf1087", D, 1087, "`x & (2^j − 1)` is `(mod x 2^j)`", "rule",
      "The Int forms: `x << k`, `x >> k`, `x & (2^j - 1)`, `x & 2^j`, `x & ~(2^j - 1)`, `~x` as `mod`/`div`/`*` arithmetic, at any width.",
      untestable=Z3ENC)

claim("vf1090", D, 1090, "Every other shape crosses at a word of at", "rule",
      "Any other bitwise shape crosses into bit-vectors at 64 bits or less: `(k & m) | 1` over int32 has `int2bv` in its file and tier `bv`.",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fbx 10) || exit 10
grep -q 'int2bv' "$f" || { echo "no int2bv crossing in $f"; exit 11; }
want "tier of the div-zero row over (k & m) | 1" "$(col fbx div-zero 11)" bv 12'''),
      wrong="the operation opaque (no crossing, tier int)")

claim("vf1095", D, 1095, "is exact — and `bvshl`/`bvlshr`/`bvashr` for a shift by a non-numeral", "rule",
      "A shift by a non-numeral amount inside a crossing is `bvshl` (for `<<`).",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fbs 10) || exit 10
grep -q 'bvshl' "$f" || { echo "no bvshl for x << n in $f"; exit 11; }'''),
      wrong="the shifted value opaque")

claim("vf1096", D, 1096, "Above 64 bits a", "rule",
      "Above 64 bits a general bitwise operation stays opaque: `(k & m) | 1` over int128 has no `int2bv`.",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fbw 10) || exit 10
if grep -q 'int2bv' "$f"; then echo "a crossing above 64 bits in $f"; exit 11; fi'''),
      wrong="a 128-bit crossing (the budget's cost the text measured)")

claim("vf1098", D, 1098, "measured 191 rlimit at 32 and 64 bits", "rule",
      "The crossing's measured cost per width (191 rlimit at 32 and 64 bits, 883,930 at 128, ...).",
      untestable=Z3V)

claim("vf1103", D, 1103, "A function with a crossing emits `(set-logic", "rule",
      "A function whose obligations hold a crossing emits `(set-logic ALL)`; one without does not.",
      expect="sh:0", sh=obl(P_INTS, S_FILE + '''
f=$(fof fbx 10) || exit 10
grep -qF '(set-logic ALL)' "$f" || { echo "no (set-logic ALL) in the crossing function's $f"; exit 11; }
g=$(fof fq 12) || exit 12
if grep -qF '(set-logic ALL)' "$g"; then echo "(set-logic ALL) in the crossing-free $g"; exit 13; fi'''),
      wrong="one header for every file (11 or 13)")

claim("vf1105", D, 1105, "A flag family (D-230) is an unsigned 32-bit word to the", "rule",
      "A flag family is an unsigned 32-bit word to the encoder; `int32 =>! oflags` and back re-sign the bit pattern.",
      untestable=Z3ENC)

claim("vf1109", D, 1109, "THE GATE (D-280): every row", "rule",
      "Every row discharged before a crossing is discharged after it; measured over the re-recorded manifest.",
      untestable=RUNNERS)

claim("vf1116", D, 1116, "value is an `Int` in the", "rule",
      "A twisted value is an Int in its carrier's range with ERR the most negative value, a value the terms carry.",
      untestable=Z3ENC)

claim("vf1123", D, 1123, "`+ - *` and negation saturate to ERR outside the", "rule",
      "Twisted `+ - *` and negation saturate to ERR outside the valid range.",
      m10="m13_tbb_err_sticky")

claim("vf1125", D, 1125, "`tfp`'s `*` is `(div (* a b) 2^F)` and its `/` `(npk_sdiv (* a 2^F) b)`", "rule",
      "`tfp`'s `*` and `/` are modelled as the emitter's floor multiply and truncating divide.",
      untestable=Z3ENC)

claim("vf1126", D, 1126, "each narrowed by the range test, a zero divisor is ERR, `/` and `%` at the", "rule",
      "A twisted `/` and `%` truncate: tbb32 -7 / 2 is -3 and -7 % 2 is -1.",
      expect="run:0", src=main_('''    tbb32:a = raw vt32(-7tbb32);
    tbb32:q = a / raw vt32(2tbb32);
    if (q != -3tbb32) { exit 10i32; }
    tbb32:r = a % raw vt32(2tbb32);
    if (r != -1tbb32) { exit 11i32; }
    exit 0i32;'''),
      wrong="flooring (-4 and 1: exits 10, 11)")

claim("vf1128", D, 1128, "the truncating quotient or remainder, the ternary digits' `&`/`|` are the", "rule",
      "The ternary digits' `&`/`|` are the Kleene min/max.",
      expect="run:0", src=P_KLEENE,
      wrong="two's-complement bitwise and/or (10, 11)")

claim("vf1129", D, 1129, "Kleene min/max, `dim256` is `tfp256`. Each raw result is named once", "rule",
      "Each raw twisted result is named once without an axiom before the range test reads it.",
      untestable="[internal] how the encoder names a raw result; no outcome but the verdicts depends on it")

claim("vf1132", D, 1132, "The rows are `err-exit`'s (§7b): one per", "rule",
      "One `err-exit` row per TbbErr guard: two tbb comparisons in a function are two rows.",
      expect="sh:0", sh=obl(P_TBB_CMP, '''
want "err-exit rows of two tbb32 comparisons" "$(n fte2 err-exit)" 2 10'''),
      wrong="one row per function, or none")

claim("vf1133", D, 1133, "A twisted division has", "rule",
      "A twisted division never traps: a zero divisor yields ERR.",
      m10="v18_tbb_div_by_zero_is_err")

claim("vf1134", D, 1134, "A `limit` over a twisted subject encodes", "rule",
      "A `limit` over a `tbb32` subject is an encoded row.",
      expect="sh:0", sh=obl('''
Rules<tbb32>:r_ok = { !is_err($), $ != 0tbb32 };
func:flt = int32(tbb32:a) never fails {
    limit<r_ok> tbb32:y = a;
    if (y == 6tbb32) { pass 1i32; }
    pass 0i32;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw flt(raw vt32(6tbb32)));
    exit 0i32;
};''', '''
want "encoded field of the tbb32 limit row" "$(col flt limit 5)" 1 10'''),
      wrong="`unencoded` (0)")

claim("vf1136", D, 1136, "for the next (the predicate traps on the first false clause)", "rule",
      "A rule's predicate traps on its first false clause (LimitViolated), before a later clause's own guard.",
      expect="trap:LimitViolated", src=main_('''    limit<r_div> int32:x = raw v32(0i32);
    if (x == 0i32) { exit 10i32; }
    exit 11i32;''', "Rules<int32>:r_div = { $ != 0i32, 100i32 / $ > 1i32 };"),
      wrong="DivByZero (97) from the second clause")

claim("vf1137", D, 1137, "tfp-element `complex` is an aggregate the walk has no term for: its guards", "rule",
      "A `frac`'s TbbErr guard is `unencoded` (fifth field `0`).",
      expect="sh:0", sh=obl(P_FRAC, '''
want "encoded field of the frac32 comparison's err-exit row" "$(col ffr err-exit 5)" 0 10'''),
      wrong="an encoded row")

claim("vf1138", D, 1138, "are `unencoded`, their traps kept.", "rule",
      "The unencoded frac guard's trap is kept: comparing a `frac32` ERR traps TbbErr.",
      expect="trap:TbbErr", src=main_('''    frac32:z = raw v32(0i32) => frac32;
    frac32:e = (raw v32(5i32) => frac32) / z;
    frac32:one = raw v32(1i32) => frac32;
    if (e < one) { exit 10i32; }
    exit 11i32;'''),
      wrong="the comparison decided on ERR (10, 11)")

claim("vf1142", D, 1142, "53)`) with NO range axiom — NaN and the infinities are values of it, and a", "rule",
      "A float term has no range axiom: NaN and the infinities are its values.",
      untestable=Z3ENC)

claim("vf1144", D, 1144, "the emitter's instruction under SMT-LIB's IEEE semantics: `fp.add`/`sub`/", "rule",
      "A float obligation's arithmetic is SMT-LIB's IEEE operations: a product and a sum in a `#sqrt` prove appear as `fp.mul` and `fp.add`.",
      expect="sh:0", sh=obl(P_FLT, S_FILE + '''
f=$(fof hyp 10) || exit 10
grep -q 'fp\\.mul' "$f" || { echo "no fp.mul in $f"; exit 11; }
grep -q 'fp\\.add' "$f" || { echo "no fp.add in $f"; exit 12; }'''),
      wrong="the float operations opaque")

claim("vf1146", D, 1146, "predicates the emitter's `fcmp` writes (`==` is `fp.eq`, `!=` its negation,", "rule",
      "NaN compares as the machine's ordered `fcmp` does, `!=` being `==`'s negation.",
      expect="run:0", src=P_NAN,
      wrong="unordered compares, or an ordered `!=`")

claim("vf1149", D, 1149, "the two agree by correct rounding; a `flt32` literal rounded twice, as the", "rule",
      "A `flt32` literal is rounded to double and then to float (1.0000000596046448309f32 is 1.0).",
      expect="run:0", src=P_DROUND,
      wrong="one rounding: 1.0000001 (exit 10)")

claim("vf1151", D, 1151, "(to_real x)`, a widening exact, a narrowing `=>!` rounded; `%` (`frem`, a", "rule",
      "A float `%` is `frem`, a truncated fmod and not IEEE's remainder: 5.5 % 2.0 is 1.5 and -5.5 % 2.0 is -1.5.",
      expect="run:0", src=main_('''    flt64:r = raw vf64(5.5f64) % raw vf64(2.0f64);
    if (r != 1.5f64) { exit 10i32; }
    flt64:s = raw vf64(-5.5f64) % raw vf64(2.0f64);
    if (s != -1.5f64) { exit 11i32; }
    exit 0i32;'''),
      wrong="IEEE remainder: -0.5 (exit 10) and 0.5 (exit 11)")

claim("vf1153", D, 1153, "opaque as VALUES -- the crossing itself carries a `cast-range` row over the", "rule",
      "A float leaving to an integer carries a `cast-range` row over the operand.",
      expect="sh:0", sh=obl(P_CAST, '''
want "cast-range rows of f =>! int32" "$(n fc cast-range)" 1 10'''),
      wrong="no row")

claim("vf1155", D, 1155, "compares; `flt128` is storage (D-143) and has no term.", "rule",
      "`flt128` has no term.",
      untestable=Z3ENC)

claim("vf1156", D, 1156, "Every float value is NAMED — a fresh symbol defined equal to the operation,", "rule",
      "Every float value is a fresh named symbol defined equal to its operation.",
      untestable="[internal] the encoder's naming; no outcome depends on it outside the verdicts")

claim("vf1158", D, 1158, "Floats never trap (D-007): no row is theirs", "rule",
      "Float arithmetic never traps: 1.0 / 0.0 is +infinity and 1.0 % 0.0 is NaN, with no trap.",
      expect="run:0", src=main_('''    flt64:q = raw vf64(1.0f64) / raw vf64(0.0f64);
    if (!(q > 1.0e308f64)) { exit 10i32; }
    flt64:r = raw vf64(1.0f64) % raw vf64(0.0f64);
    if (r == r) { exit 11i32; }
    exit 0i32;'''),
      wrong="a DivByZero trap (97) for a float division (DEF-37's shape)")

claim("vf1159", D, 1159, "`limit`, a contract clause, an `invariant`, a `prove` and the `err-exit` row", "rule",
      "Over floats a `limit`, a `prove` and a float entering `tbb` are encoded rows.",
      expect="sh:0", sh=obl(P_FLT, '''
want "encoded field of ratio's limit rows" "$(col ratio limit 5)" 1 10
want "encoded field of ratio's prove row" "$(col ratio prove 5)" 1 11
want "encoded field of fent's err-exit row" "$(col fent err-exit 5)" 1 12'''),
      wrong="`unencoded` float rows")

claim("vf1160", D, 1160, "Measured: a", "rule",
      "A bounded quotient's `prove` discharges in QF_FP in 3.9 s.",
      untestable=Z3V)

claim("vf1162", D, 1162, "TIER 2, the Real-interval abstraction: for every row whose cone holds a", "rule",
      "For a float row meeting the conditions the encoder writes a twin `NNNN.t2.smt2` beside the tier-1 file, named in `index.t2.txt`.",
      expect="sh:0", sh=S_TWIN,
      wrong="no twin")

claim("vf1165", D, 1165, "Real: an input symbol a free Real, a named operation a fresh Real `r` with", "rule",
      "The twin's Real model: each operation a fresh Real within ε·|v| + η of its exact value.",
      untestable=Z3ENC)

claim("vf1172", D, 1172, "The twin is written at all only under THREE CONDITIONS, else the row stays", "rule",
      "Without the conditions no twin is written: an unbounded float `prove` has none.",
      expect="sh:0", sh=obl(P_FLT, S_NOTWIN + '''
nt hypu 10'''),
      wrong="a twin over unbounded floats")

claim("vf1176", D, 1176, "`requires` clause, a path condition; a negated comparison is not a bound,", "rule",
      "A negated comparison is not a bound (it holds of NaN): floats bounded only by `!($ < 1.0)` and `!($ > 2.0)` get no twin.",
      expect="sh:0", sh=obl(P_FLT, S_NOTWIN + '''
nt hypn 10'''),
      wrong="a twin whose premise admits NaN")

claim("vf1179", D, 1179, "operation's magnitude within the normal range (`|v| ≤ MAX_NORMAL` per", "rule",
      "The twin conjoins every operation's normal-range magnitude, nonzero divisors and non-negative root arguments to its goal.",
      untestable=Z3ENC)

claim("vf1183", D, 1183, "combination of comparisons over symbols and the Int fragment — an `fp.eq`,", "rule",
      "An `fp.eq` goal stays tier 1 only: no twin for `prove(a == a)` over a bounded float.",
      expect="sh:0", sh=obl(P_FLT, S_NOTWIN + '''
nt sameq 10'''),
      wrong="a twin for an fp.eq goal")

claim("vf1184", D, 1184, "with its NaN reading, stays tier 1 only, and an uninterpreted function in", "rule",
      "An uninterpreted function in the cone excludes the row from tier 2.",
      untestable="[vague] which float cones hold an uninterpreted function (a `pure` float callee in a contract) is not spelled out enough to build one that surely meets the other two conditions")

claim("vf1185", D, 1185, "The runners ask tier 1 first; for a `budget` row", "rule",
      "The runners ask tier 1 first and the twin once for a `budget` row under the same profile and net; `--explain` names the tier that decided.",
      untestable=Z3V)

claim("vf1189", D, 1189, "Measured: `#sqrt(a*a + b*b) >= 0.0` under bounded", "rule",
      "The flt_tier2 shape is `unknown` in QF_FP and `unsat` in the twin.",
      untestable=Z3V)

claim("vf1193", D, 1193, "A `simd<T, N>` value is N scalar terms", "rule",
      "A `simd<T, N>` value is N scalar terms under its element's theory and has no term of its own.",
      untestable=Z3ENC)

P_LANE = '''
func:fvl = int32(int32:a, int64:i) never fails {
    simd<int32, 4>:v = simd(a, a, a, a);
    pass v[i];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fvl(raw v32(1i32), raw v64(2i64)));
    exit 0i32;
};'''

claim("vf1198", D, 1198, "with a numeral index the lane's term (a computed index opaque, its `bounds`", "rule",
      "A computed lane index `v[i]` is one `bounds` row.",
      expect="sh:0", sh=obl(P_LANE, '''
want "bounds rows of v[i] on a simd<int32, 4>" "$(n fvl bounds)" 1 10'''),
      wrong="no row for a computed lane index")

claim("vf1201", D, 1201, "right; `min`/`max` as its `select` over the strict compare, `fcmp olt`/`ogt`", "rule",
      "A float `simd` `.min()` folds with a select over the ordered strict compare, false on NaN, so a NaN lane is passed over: min of (1, 3, 0.5, NaN) is 0.5.",
      expect="run:0", src=main_('''    flt64:nan = raw vf64(0.0f64) / raw vf64(0.0f64);
    simd<flt64, 4>:v = simd(raw vf64(1.0f64), 3.0f64, 0.5f64, nan);
    flt64:m = v.min();
    if (m != 0.5f64) { exit 10i32; }
    exit 0i32;'''),
      wrong="the NaN lane taken (NaN: exit 10)")

claim("vf1204", D, 1204, "AND through bindings: a `simd` local's lanes are N", "rule",
      "A `simd` local's lanes are N symbols, a new set at every write, fresh and opaque at every invalidation, restore and merge.",
      untestable=Z3ENC)

claim("vf1209", D, 1209, "is N opaque lanes. A `simd` division's any-lane guard is ONE `div-zero`", "rule",
      "A `simd` division's any-lane guard is ONE `div-zero` row, a signed element's also one `div-min` row.",
      expect="sh:0", sh=obl(P_SIMD_DIV, '''
want "div-zero rows of a simd<int32, 4> division" "$(n fv div-zero)" 1 10
want "div-min rows of a simd<int32, 4> division" "$(n fv div-min)" 1 11'''),
      wrong="one row per lane")

claim("vf1211", D, 1211, "one `div-min` row; a `simd` shift's any-lane guard one `shift-range` row", "rule",
      "A `simd` shift's any-lane guard is one `shift-range` row.",
      expect="sh:0", sh=obl(P_SHIFT, '''
want "shift-range rows of a simd<uint8, 8> shift" "$(n fvs shift-range)" 1 10'''),
      wrong="one row per lane")

claim("vf1213", D, 1213, "the site as a scalar's is — and a discharged any-lane row elides its guard", "rule",
      "In the verified build a discharged any-lane `div-zero` row (an unsigned `simd` division, which has no `div-min` row) becomes exactly one `llvm.assume`.",
      expect="sh:0", sh=elided(P_SIMD_DIV, '''
manifest '$3=="div-zero"'
elide
want "llvm.assume calls in fw, verified build" "$(assumes fw e.ll)" 1 10'''),
      wrong="the vector guard ignorant of the manifest (0 assumes, the trap kept), or one assume per lane (4)")

claim("vf1220", D, 1220, "**The tier column (D-281).** `rows.txt`'s eleventh field, read off the", "rule",
      "rows.txt's eleventh field is the tier: `int`, `bv`, `fp`, or `-` for an unencoded or checker row.",
      expect="sh:0", sh=S_TIERS,
      wrong="a constant `int`")

claim("vf1224", D, 1224, "`real` is written by", "rule",
      "`real` is written by the runner for a row tier 2 discharged.",
      untestable=Z3V)

P_LIM_STR = '''
Rules<string>:r_ne = { $.len > 0i64 };
func:flim = int64(int64:n) never fails {
    limit<r_ne> string:s = "abc";
    if (n > 0i64) { s = "de"; }
    pass s.len;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw flim(raw v64(1i64)));
    exit 0i32;
};'''

claim("vf1228", D, 1228, "**What is still outside the fragment.** A `limit` over a string, a struct", "rule",
      "A `limit` over a string subject is `unencoded` (fifth field `0`).",
      expect="sh:0", sh=obl(P_LIM_STR, '''
[ "$(n flim limit)" -ge 1 ] || { echo "no limit rows for a limit over a string"; exit 10; }
want "encoded field of a string limit's rows" "$(col flim limit 5)" 0 11'''),
      wrong="an encoded row")

claim("vf1228b", D, 1228, "over a string, a struct", "rule",
      "A `limit` over a struct subject is `unencoded`.",
      expect="sh:0", sh=S_LIM_STRUCT,
      wrong="an encoded row (1): the text behind D-317's aggregate terms")

claim("vf1229", D, 1229, "or an array (P-12's residue)", "rule",
      "A `limit` over an array subject is `unencoded`.",
      expect="sh:0", sh=obl('''
Rules<int32[4]>:r_arr = { $[0i64] > 0i32 };
func:fla = int32(int32:a) never fails {
    limit<r_arr> int32[4]:v = [a, 1i32, 2i32, 3i32];
    pass v[1i64];
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fla(raw v32(1i32)));
    exit 0i32;
};''', '''
[ "$(n fla limit)" -ge 1 ] || { echo "no limit rows for a limit over an array"; exit 10; }
want "encoded field of an array limit's rows" "$(col fla limit 5)" 0 11'''),
      wrong="an encoded row")

claim("vf1230", D, 1230, "tfp-element `complex` are `unencoded`, their guards kept", "rule",
      "The guard of a limit over a string is kept: breaking the rule traps LimitViolated.",
      expect="trap:LimitViolated", src=main_('''    limit<r_ne> string:s = "abc";
    if (raw v32(1i32) > 0i32) { s = ""; }
    exit 10i32;''', "Rules<string>:r_ne = { $.len > 0i64 };"),
      wrong="no check for an unencoded rule (exit 10)")

claim("vf1232", D, 1232, "`cast-range` rows; D-210's overflow rows are 1.5.8's, over the lane", "rule",
      "A `simd`'s integer lanes trap as scalars do: a lane `+` past the maximum traps IntOverflow.",
      m10="o22_simd_lane_overflow")

claim("vf1234", D, 1234, "The compiler's own", "rule",
      "The compiler's own manifest at 1.5.4b's close: 368 rows in 197 files, 329 int, 11 bv, 28 -, no fp.",
      untestable=HISTORY)

claim("vf1244", D, 1244, "A `limit` over a string, a struct or an", "rule",
      "Still at 1.5.8b: a `limit` over a struct is `unencoded` with its guard kept.",
      expect="sh:0", sh=S_LIM_STRUCT,
      wrong="an encoded row (1)")

claim("vf1245", D, 1245, "array and the `TbbErr` guards over a `frac` or a tfp-element `complex` are", "rule",
      "Still at 1.5.8b: the TbbErr guard of a `frac` is `unencoded`.",
      expect="sh:0", sh=obl(P_FRAC, '''
want "encoded field of the frac32 comparison's err-exit row" "$(col ffr err-exit 5)" 0 10'''),
      wrong="an encoded row")

# @@END@@
