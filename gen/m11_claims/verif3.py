"""M11 claims: VERIFICATION_REFERENCE.md lines 1248-2351 at HUNT2 (9126350), extracted by session 9.
§8 the SMT elimination manifest, §9 the floor's obligations (the spec grammar, the kernel
boundary, the rows and verdicts, the protocol models, the floor's stack) and §10 the
schedule explorer.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). Almost all of the range is the verified build's and
the runners' own machinery: z3's verdicts, the floor's translator, the protocol
models, the explorer. Those claims are untestable with verif2's reasons. A claim
about what the compiler EMITS is a script over `npkc FILE --obligations DIR` (the
compiler's half of verification, no z3), as in verif2. The scaffolding (OBL_HEAD,
prog) is verif2's, copied, since a claims module loads alone. A claim about a trap's
spelling is an `ir:` test.
"""
from m11lib import *

covers("VERIFICATION", 1248, 2351)

D = "VERIFICATION"

Z3V = "[z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment)"
RUNNERS = ("[tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, "
           "which need the pinned z3 and the full ladder")
FLOOR = ("[tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or "
         "tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3")
SPEC = "[tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec"
MODELS = ("[tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk "
          "or the explicit-state belt, run by `npkg verify`")
EXPLORE = ("[tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim "
           "runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test`")
KERNEL = ("[tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, "
          "generated from this region); no program observes the model")
HISTORY = "[tree] a measurement or a record of what a step landed, about the compiler's tree and its records"


def prog(src, name="p"):
    """A whole program for a script: `mod:`, the identity helpers it calls, the source,
    and the M11 failsafe unless the source carries its own (verif2's)."""
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
want() { [ "$2" = "$3" ] || { echo "$1: got [$2], want [$3]"; exit "$4"; }; }
'''


def obl(src, checks):
    return OBL_HEAD.replace("@@PROG@@", prog(src)) + checks.strip() + "\nexit 0\n"


DIVF = "func:q = int32(int32:a, int32:b) never fails { pass (a / b); };"
MAIN0 = main_("    int32:v = raw q(raw v32(7i32), raw v32(2i32));\n    if (v != 3i32) { exit 10i32; }\n    exit 0i32;")

# ================================================================== 8. the SMT elimination manifest
claim("vf1251", D, 1251, "the file is `nitpick.obligations` at the manifest root, committed, written", "rule",
      "nitpick.obligations is written only by `npkg verify --record`.", untestable=RUNNERS)
claim("vf1255", D, 1255, "`<sha256> <kind> <tier> <verdict> <elision> <symbol>`", "rule",
      "A manifest row is `<sha256> <kind> <tier> <verdict> <elision> <symbol>`.", untestable=Z3V)
claim("vf1264", D, 1264, "`--obligations` writes a function's file and rows only when", "rule",
      "`--obligations` writes rows only for functions the emission holds: a program that formats no "
      "float has no row for the prelude's `flt_bits_shortest`.",
      expect="sh:0",
      sh=obl(DIVF + "\n" + MAIN0, """
total=$(wc -l < ob/rows.txt | tr -d ' ')
echo "rows=$total flt=$(n flt_bits_shortest '*') q=$(n q '*')"
[ "$total" -gt 0 ] || exit 10
want flt_bits_shortest "$(n flt_bits_shortest '*')" 0 11
"""),
      wrong="rows for prelude functions the emission does not hold")
claim("vf1281", D, 1281, "functions: `|uf.<name>.<decl>|` for a `pure never fails` callee (1.5.3)", "rule",
      "A row's text declares a `pure never fails` callee as an uninterpreted function `|uf.<name>.<decl>|`.",
      expect="sh:0",
      sh=obl("""func:pos = bool(int32:v) pure never fails { pass (v > 0i32); };
func:half = int32(int32:n) requires raw pos(n) { pass (n / 2i32); };
""" + main_("    int32:v = half(raw v32(8i32)) ?| 0i32;\n    if (v != 4i32) { exit 10i32; }\n    exit 0i32;"), """
c=$(cat ob/*.smt2 | grep -c '|uf\\.pos\\.')
echo "uf.pos mentions: $c"
[ "$c" -gt 0 ] || exit 10
"""),
      wrong="the callee not an uninterpreted function")
claim("vf1297", D, 1297, "`rows.txt` (`--obligations`) names each row's site (`space:index`), its", "rule",
      "rows.txt names each row's role: a division's row in its own function is a `guard`.",
      expect="sh:0",
      sh=obl(DIVF + "\n" + MAIN0, """
echo "q's rows: $(rows q '*' | cut -f3,8 | tr '\\t' ':' | tr '\\n' ' ')"
roles=$(col q '*' 8)
case " $roles " in *" guard "*) ;; *) exit 10;; esac
"""),
      wrong="no guard role")
claim("vf1308", D, 1308, "`rows.txt`'s fifth column is `1` (a row with a", "rule",
      "rows.txt's fifth column is `1` for a row with a `(check-sat)`: a division's row is encoded.",
      expect="sh:0",
      sh=obl(DIVF + "\n" + MAIN0, """
enc=$(col q '*' 5)
echo "encoded: $enc"
case " $enc " in *" 1 "*) ;; *) exit 10;; esac
"""),
      wrong="not 1")
claim("vf1314", D, 1314, "verified build refuses an undischarged `prove` (`NITPICK-VERIFY-001`)", "rule",
      "The verified build refuses an undischarged prove, NITPICK-VERIFY-001.", untestable=Z3V)
claim("vf1319", D, 1319, "`int`, `bv`, `fp`, `-`, and `real` written by the runner", "rule",
      "The tier column is the encoder's word: an int32 division's row is `int`.",
      expect="sh:0",
      sh=obl(DIVF + "\n" + MAIN0, """
tier=$(col q '*' 11)
echo "tier: $tier"
case " $tier " in *" int "*) ;; *) exit 10;; esac
"""),
      wrong="another tier")
claim("vf1330", D, 1330, "A static overlap is the", "rule",
      "A static overlap with a live claim is the aliasing analysis's own refusal, NITPICK-BORROW-013.",
      expect="refuse:NITPICK-BORROW-013",
      src=main_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32->:p = $$m arr[2i64];
    <-p = 9i32;
    int32:v = arr[2i64];
    if (v != 9i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("vf1334", D, 1334, "a PROGRAM's raise — `?!`, `!!!` — is", "rule",
      "A program's raise is `@npk_raise(i32 CODE)`: `!!! E1;` calls npk_raise.",
      expect='ir:call [^\\n]*@npk_raise\\(i32',
      src=main_("""    int32:x = raw v32(1i32);
    if (x == 2i32) { !!! E1; }
    exit 0i32;""", "error:E1;"),
      wrong="the raise lowered as a guard's npk_trap")
claim("vf1340", D, 1340, "THE HANG NET. Every", "rule",
      "Every z3 process runs under a hang net of 120 + 10·checks + 60·B seconds.", untestable=RUNNERS)
claim("vf1363", D, 1363, "`rows.txt` has a twelfth field, the row's CLAUSE CONTEXT", "rule",
      "rows.txt's twelfth field names a guard's clause context: a division inside an `ensures` clause has a "
      "row whose twelfth field is not 0.",
      expect="sh:0",
      sh=obl("""func:f = int32(int32:a, int32:b) ensures result == a / b { pass (a / b); };
""" + main_("    int32:v = f(raw v32(7i32), raw v32(2i32)) ?| 0i32;\n    if (v != 3i32) { exit 10i32; }\n    exit 0i32;"), """
echo "f's rows: $(rows f '*' | cut -f3,12 | tr '\\t' ':' | tr '\\n' ' ')"
ctx=$(rows f '*' | awk -F'\\t' '$12 != "0"' | wc -l | tr -d ' ')
[ "$ctx" -gt 0 ] || exit 10
"""),
      wrong="every row's clause context 0")
claim("vf1368", D, 1368, "**A guard in a check exists only where the check is emitted.**", "rule",
      "A guard inside a check whose rows are all discharged goes with the check.", untestable=Z3V)
claim("vf1374", D, 1374, "**A loop head's check runs at every visit.**", "rule",
      "A guard inside an invariant has a row in every context the head is reached from: the entry and the "
      "back edge give a division in the invariant at least two rows of one site.",
      expect="sh:0",
      sh=obl("""func:f = int32(int32:n) never fails {
    int32:i = 1i32;
    while (i < n) decreases n - i invariant 10i32 / i > 0i32 - 1i32 { i = i + 1i32; }
    pass i;
};
""" + main_("    int32:v = raw f(raw v32(4i32));\n    if (v != 4i32) { exit 10i32; }\n    exit 0i32;"), """
echo "f's rows: $(rows f '*' | cut -f3,7,12 | tr '\\t' ':' | tr '\\n' ' ')"
most=$(rows f div-zero | cut -f7 | sort | uniq -c | sort -rn | head -1 | awk '{print $1}')
echo "most rows at one div-zero site: ${most:-0}"
[ "${most:-0}" -ge 2 ] || exit 10
"""),
      wrong="one row: the entry only")
claim("vf1392", D, 1392, "THE BELTS COUNT GUARDS, NOT ROWS.", "rule", "The belts count guards, not rows.",
      untestable=RUNNERS)
claim("vf1405", D, 1405, "`overflow` traps", "rule",
      "An `overflow` guard traps -4110: a checked int32 addition's guard is `@npk_trap(i32 -4110)`.",
      expect='ir:@npk_trap\\(i32 -4110\\)',
      src=main_("""    int32:a = raw v32(2147483000i32);
    int32:b = a + raw v32(1000i32);
    if (b > 0i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="another code")
claim("vf1406", D, 1406, "`-4110`, `bounds` `-4099` and `cast-range` `-4117`", "rule",
      "A `bounds` guard traps -4099: an indexed read's guard is `@npk_trap(i32 -4099)`.",
      expect='ir:@npk_trap\\(i32 -4099\\)',
      src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32:v = a[raw v64(2i64)];
    if (v != 3i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="another code")
claim("vf1410", D, 1410, "`terminate` gained its guard -- the loop head's", "rule",
      "`terminate`'s guard, the loop head's DecreasesViolated check, traps -4119.",
      expect='ir:@npk_trap\\(i32 -4119\\)',
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 3i64) decreases 3i64 - i { i = i + 1i64; }
    if (i != 3i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="another code, or no guard")
claim("vf1416", D, 1416, "`terminate` rows at recursive", "rule",
      "terminate rows at recursive calls; stack-depth rows derived by the runners after every file is decided.", untestable=RUNNERS)
claim("vf1425", D, 1425, "`--smt-opt` is the only verification flag that changes generated code", "rule",
      "`--smt-opt` is the only verification flag that changes generated code.", untestable=Z3V)
claim("vf1430", D, 1430, "`--smt-timeout` defaults to 5000 ms", "rule",
      "`--smt-timeout` defaults to 5000 ms.", untestable=Z3V)
claim("vf1435", D, 1435, "**Every elision is therefore recorded in a manifest", "rule",
      "Every elision is recorded in a manifest that is authoritative on later builds.", untestable=Z3V)
claim("vf1438", D, 1438, "```", "example", "The manifest v1 sketch (superseded by D-218's schema, line 1260).",
      untestable=Z3V)
for _ln, _q, _t in ((1447, "| manifest matches exactly | build proceeds, binary reproducible |", "A matching manifest: the build proceeds."),
                    (1448, "| Z3 proves **more** than recorded | **build fails** |", "Z3 proving more than recorded fails the build."),
                    (1449, "| Z3 proves **less** than recorded | **build fails** |", "Z3 proving less than recorded fails the build."),
                    (1450, "| no manifest | generated; build marked *not reproducibility-verified* |", "No manifest: generated, marked not verified.")):
    claim("vf%04d" % _ln, D, _ln, _q, "row", _t, untestable=Z3V)
claim("vf1452", D, 1452, "Obligations are identified by a **hash of their normalised SMT-LIB2 form**", "rule",
      "An obligation's hash is over its normalised SMT text, not its source location: two programs that "
      "differ only by blank lines above the function give the same hashes.",
      expect="sh:0",
      sh=OBL_HEAD.replace("@@PROG@@", prog(DIVF + "\n" + MAIN0)) + """mv ob ob1
cat > p.npk <<'NPK_EOF'
""" + prog("\n\n\n\n" + DIVF + "\n" + MAIN0) + """NPK_EOF
"$NPKC" p.npk -o p.ll --obligations ob2 >out.txt 2>err.txt || exit 5
a=$(awk -F'\\t' '$6 ~ /q/ {print $4}' ob1/rows.txt | sort | tr '\\n' ' ')
b=$(awk -F'\\t' '$6 ~ /q/ {print $4}' ob2/rows.txt | sort | tr '\\n' ' ')
echo "hashes: [$a] [$b]"
[ -n "$a" ] && [ "$a" = "$b" ]
exit $?
""",
      wrong="a hash that moves with the source line")
claim("vf1456", D, 1456, "This does not make Z3 deterministic.", "rule",
      "The manifest makes divergence detectable and fatal.", untestable=Z3V)

# ================================================================== 9. the floor's obligations
claim("vf1467", D, 1467, "The runtime floor (`runtime/npkrt.ll`, hand-written LLVM IR, permanent under", "rule",
      "The floor is specified beside itself and decided by the same solver.", untestable=FLOOR)
for _ln, _q in ((1474, "| `runtime/npkrt.spec` |"), (1475, "| `runtime/models/*.model` |"),
                (1476, "| `runtime/npkrt.obligations` |")):
    claim("vf%04d" % _ln, D, _ln, _q, "row", "A file of the floor's evidence.",
          untestable="[tree] a file of the compiler's tree")
claim("vf1478", D, 1478, "**The writer is `npkg/floor_smt.npk`**", "rule", "The floor's writer and its modules.",
      untestable="[tree] the compiler's sources")
claim("vf1487", D, 1487, "A manifest row", "rule",
      "A manifest row of a kind its file does not carry is refused by name.", untestable=RUNNERS)
claim("vf1492", D, 1492, "**The theory is the program's (§7c, D-218 (4)):**", "rule",
      "The floor's theory is the program's.", untestable=FLOOR)
claim("vf1505", D, 1505, "**Memory is the uninterpreted function `(mem Int) Int`**", "rule",
      "Memory is an uninterpreted function with byte range axioms.", untestable=FLOOR)
claim("vf1518", D, 1518, "**An address computed", "rule", "An address computed by the body wraps once.",
      untestable=FLOOR)
claim("vf1558", D, 1558, "**A load of an element of", "rule", "A constant table's element reads as an ite.",
      untestable=FLOOR)
claim("vf1573", D, 1573, "**The bit-vector crossing is a symbol**", "rule", "The bv crossing is a symbol.",
      untestable=FLOOR)
claim("vf1579", D, 1579, "**A memory the translation cannot define", "rule",
      "A memory the translation cannot define pointwise is a template.", untestable=FLOOR)
claim("vf1596", D, 1596, "One `(symbol @name …)` section per specified define.", "rule",
      "The spec file's names.", untestable=SPEC)
for _ln, _q in ((1623, "| `(requires P)` |"), (1624, "| `(objects (lo len) …)` |"), (1625, "| `(views (lo len) …)` |"),
                (1626, "| `(ensures P)` |"), (1627, "| `(ensures-trap P)` |"), (1628, "| `(frame (lo len) …)` |"),
                (1629, "| `(ensures-fresh LEN)`"), (1630, "| `(loop LABEL (invariant I)"),
                (1631, "| `(loop LABEL (unroll N))` |"), (1632, "| `(summary)` |"), (1633, "| `(residue \"why\")` |"),
                (1634, "| `(boundary \"what\")` |")):
    claim("vf%04d" % _ln, D, _ln, _q, "row", "A spec clause and the rows it gives.", untestable=SPEC)
claim("vf1636", D, 1636, "**`requires`, `(objects …)` and `(views …)` are HYPOTHESES ABOUT THE CALLER", "rule",
      "requires/objects/views are hypotheses about the caller.", untestable=SPEC)
claim("vf1641", D, 1641, "**TCB.md §4d, GENERATED**", "rule", "TCB.md §4d is generated.",
      untestable="[tree] a document of the compiler's tree")
claim("vf1660", D, 1660, "**What is read once is written once.**", "rule",
      "Both runners refuse a clause written twice.", untestable=RUNNERS)
claim("vf1670", D, 1670, "A callee without `(summary)` is INLINED before translation", "rule",
      "A callee without summary is inlined; an unsupported form is a refusal naming the line.", untestable=FLOOR)
claim("vf1684", D, 1684, "**THE INSTANTIATION RULE (S-65, generalised at step 4).**", "rule",
      "The invariant's universal is instantiated at the section's free symbols.", untestable=FLOOR)
claim("vf1699", D, 1699, "**THE CONE.**", "rule", "A row's cone is the relevance closure.", untestable=FLOOR)
claim("vf1711", D, 1711, "A call of `npk_sys6(nr, a1…a6)` is `(sys nr a1 … a6 k)`", "rule",
      "A syscall is the uninterpreted sys under the kernel's answer shape.", untestable=FLOOR)
claim("vf1718", D, 1718, "**The kernel-effect table is ONE authority, and it is this region**", "rule",
      "The kernel-effect table is one authority, parsed strictly by the generator.",
      untestable="[tree] the compiler's generator and sources")
claim("vf1725", D, 1725, "- **effect** — `none` (memory is as it was)", "rule", "The effect column's words.",
      untestable=KERNEL)
claim("vf1736", D, 1736, "- **buffer**, **length** — for `writes`", "rule",
      "An error answer writes nothing, and a NULL buffer is written nowhere.", untestable=KERNEL)
claim("vf1740", D, 1740, "- **bound** — the argument a non-negative answer never exceeds.", "rule",
      "The bound column.", untestable=KERNEL)
claim("vf1741", D, 1741, "- **option** — for a number whose effect DEPENDS on an option argument", "rule",
      "A call site whose option is outside the row's set is refused by name.", untestable=KERNEL)
for _ln in range(1751, 1781):
    claim("vf%04d" % _ln, D, _ln, "|", "row", "A row of the kernel-effect table.", untestable=KERNEL)
claim("vf1783", D, 1783, "The option sets are the floor's own", "rule", "The option sets.", untestable=KERNEL)
claim("vf1792", D, 1792, "**The write-region rows are HELD TO THE RUNNING KERNEL, not accepted**", "rule",
      "kernel_effects.npk holds each writes row to the running kernel.",
      untestable="[tree] a test of the compiler's tree")
claim("vf1816", D, 1816, "**The envelope symbols**", "rule", "The envelope symbols are decided under the table.",
      untestable=FLOOR)
claim("vf1834", D, 1834, "A row per clause as the table says; `kind` `floor-spec`", "rule",
      "A floor row's fields.", untestable=FLOOR)
claim("vf1844", D, 1844, "**Verdicts.** `discharged` is a proof.", "rule",
      "`open` in the floor is a run failure by name.", untestable=RUNNERS)
claim("vf1853", D, 1853, "**The profile carries `lp.dio=false` since step 4 (S-71).**", "rule",
      "The z3 profile carries lp.dio=false.", untestable=Z3V)
claim("vf1870", D, 1870, "**The belts, before a solver is spawned**", "rule", "The spec belts.",
      untestable=RUNNERS)
claim("vf1882", D, 1882, "**What lands at 1.5.6 step 3**", "rule", "What step 3 landed.", untestable=HISTORY)
claim("vf1898", D, 1898, "**What lands at 1.5.6 step 4**", "rule", "What step 4 landed.", untestable=HISTORY)

# ------------------------------------------------------------------ 9.4 the protocol models
claim("vf1924", D, 1924, "A specification says what one function does to memory on one thread.", "rule",
      "Each protocol is a small transition system under runtime/models/.", untestable=MODELS)
claim("vf1932", D, 1932, "```", "example", "The model file's grammar.", untestable=MODELS)
claim("vf1948", D, 1948, "The unrolling asserts one step per tick for K ticks", "rule",
      "The unrolling, its preemption bound and the stutter.", untestable=MODELS)
claim("vf1970", D, 1970, "**A model that claims nothing is worth nothing, so every model carries", "rule",
      "Every model carries controls that must reach their bad state.", untestable=MODELS)
claim("vf1989", D, 1989, "**Soundness of the sequential-consistency reading.**", "rule",
      "The SC reading is sound for these protocols; the correspondence belt.", untestable=MODELS)
claim("vf2004", D, 2004, "**What lands at 1.5.6 step 5**", "rule", "What step 5 landed.", untestable=HISTORY)
claim("vf2028", D, 2028, "**A NAMED BLOCK IS NOT A MODELLED ONE", "rule", "The seventh model, reactor-io.",
      untestable=MODELS)
claim("vf2077", D, 2077, "**What the bounds cover, measured (1.5.6b step 2).**", "rule",
      "What the bounds cover, measured.", untestable=HISTORY)
claim("vf2096", D, 2096, "**The second reading is a BELT (1.5.6b step 4d; D-295).**", "rule",
      "The explicit-state search is a belt in both runners.", untestable=MODELS)

# ------------------------------------------------------------------ 9.5 the floor's stack
claim("vf2141", D, 2141, "An emitted `define` carries", "rule",
      "An emitted define carries \"split-stack\".",
      expect='ir:^define [^\\n]*@"npk\\.vf2141\\.helper"\\([^\\n]*"split-stack"',
      src=main_("""    int32:v = raw helper(raw v32(2i32));
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", "func:helper = int32(int32:x) never fails { pass (x + 1i32); };"),
      wrong="no split-stack")
claim("vf2145", D, 2145, "it would cross: the floor's `module asm` stub, which enters the trap route as", "rule",
      "A frame that would cross the limit enters the trap route as StackExhausted: unbounded recursion traps it.",
      expect="trap:StackExhausted",
      src=main_("""    int64:r = raw down(raw v64(1i64));
    if (r == 0i64) { exit 10i32; }
    exit 11i32;""", "func:down = int64(int64:n) never fails { pass (raw down(n)) + n; };"),
      wrong="a machine fault (the stack overrun unchecked), or 10/11")
claim("vf2149", D, 2149, "the floor object carries", "rule",
      "The floor object carries `.note.GNU-split-stack` and `.note.GNU-no-split-stack`.",
      expect="sh:0",
      sh="llvm-readelf -S \"$NPKRT\" > s.txt 2>&1 || exit 3\n"
         "grep -q 'note.GNU-split-stack' s.txt && grep -q 'note.GNU-no-split-stack' s.txt",
      wrong="a note missing")
claim("vf2153", D, 2153, "`__morestack_non_split`, which that rewrite would reach,", "rule",
      "__morestack_non_split traps -4102.", untestable="[internal] a floor symbol no program reaches")
claim("vf2156", D, 2156, "**`floor-stack-reserve`, in both runners**", "rule",
      "The floor's deepest chain fits a quarter of the 64 KiB reserve.", untestable=RUNNERS)
claim("vf2174", D, 2174, "**What the belt does not say**", "rule", "What the belt does not say.",
      untestable="[vague] a list of acceptances, no outcome")

# ================================================================== 10. the schedule explorer
for _ln, _q, _t in (
        (2183, "A proof decides what a model says", "The explorer runs the real code under a chosen interleaving."),
        (2194, "**The explored build is the real one, transformed", "The transformer, its points and the totality belt."),
        (2211, "**What no point can precede", "unrouted.txt states the asm syscalls."),
        (2223, "**The shim is hand-written IR", "The shim's virtual futexes, clock, signals and address space."),
        (2252, "**The scheduler is PCT with a fairness rule.**", "The scheduler and its replay belt."),
        (2267, "**The verdicts (D-301, D-302).**", "The explorer's verdicts."),
        (2282, "**The units (D-299, D-300, X-11).**", "Every stress program says explore: N or no."),
        (2297, "**The negative controls", "The negative controls."),
        (2329, "**The reference (D-303).**", "The C shim as the IR shim's reference.")):
    claim("vf%04d" % _ln, D, _ln, _q, "rule", _t, untestable=EXPLORE)
claim("vf2336", D, 2336, "**What it found.**", "rule", "What the explorer found.", untestable=HISTORY)
claim("vf2344", D, 2344, "**What it does not claim.**", "rule", "What the explorer does not claim.",
      untestable="[vague] a list of acceptances, no outcome")
