"""M11 claims: VERIFICATION_REFERENCE.md lines 1-845 at HUNT2 (sections 1-7).

prove/assert_static, limit<Rules> and Rules composition, a field's own rule,
contracts (requires/ensures/old/result), the dead Result intercept, loop
invariants, termination (decreases/unbounded, recursion), the struck flags and
levels, the backends, the wildx boundary, deadlock.

No z3 here: what the VERIFIED build proves is untestable "[z3]". What every
build does is tested: a false requires/ensures/invariant/limit/decreases traps,
`prove` lowers to nothing in the plain build, `assert_static` folds, the
checker refuses, and `npkc --obligations DIR` (the compiler's half of
verification, no z3) writes rows.txt/index.txt, which the `sh:0` claims read.

rows.txt fields (tab-separated): NNNN k kind hash encoded symbol space:site role
group traps tier ctx; index.txt: NNNN symbol checks group measured.

Reviewed by session 7 before any of its programs ran (PROGRESS.md S51): the check
errors fixed (ids renamed to their lines, quotes moved to the lines that hold them),
and every claim's text and expectation read against its line; the full text around
each claim is re-read at triage for every claim whose program disagrees.
"""
from m11lib import *

covers("VERIFICATION", 1, 845)

D = "VERIFICATION"


# ------------------------------------------------------------------ helpers
def whole(mod, src):
    """A complete program for an sh script: mod line, helpers, src, failsafe."""
    h = helpers_text(src)
    out = "mod:%s;\n\n" % mod
    if h:
        out += h + "\n\n"
    out += src.strip() + "\n"
    if "func:failsafe" not in src:
        out += "\n" + failsafe_text(src)
    return out


def heredoc(path, text):
    return "cat > %s <<'NPK'\n%sNPK\n" % (path, text if text.endswith("\n") else text + "\n")


ROWS_FN = r"""rows() { awk -F'\t' -v k="$1" -v m="$2" '$3 == k && index($6, m) > 0' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" '$3 == k && index($6, m) > 0 { print $f }' obl/rows.txt; }"""


def obl_sh(cid, src, check):
    """Write the program, compile it with --obligations obl, then run `check`.
    exit 3: the program itself did not compile (the claim is not reached)."""
    return (heredoc(cid + ".npk", whole(cid, src)) +
            '"$NPKC" %s.npk --obligations obl -o %s.ll >npkc.out 2>&1 || exit 3\n' % (cid, cid) +
            "[ -f obl/rows.txt ] || exit 4\n" + ROWS_FN + "\n" + check.strip() + "\n")


FLAG_SRC = main_("""    int32:x = raw v32(3i32);
    if (x != 3i32) { exit 10i32; }
    exit 0i32;""")


def flag_sh(cid, flags):
    """The program compiles without the flag (the control), and npkc does not accept it with."""
    s = heredoc(cid + ".npk", whole(cid, FLAG_SRC))
    s += '"$NPKC" %s.npk -o ok.ll >ok.out 2>&1 || exit 3\n' % cid
    for f in flags:
        s += '"$NPKC" %s.npk %s -o bad.ll >bad.out 2>&1 && exit 1\n' % (cid, f)
    s += "exit 0\n"
    return s


def failsafe_custom(pre="", arms=(), skip=()):
    """A failsafe naming every TRAPS arm except `skip`, plus `arms` first."""
    lines = ["        %s" % a for a in arms]
    lines += ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS if n not in skip]
    lines.append("        (*) { exit 99i32; }")
    return ("func:failsafe = int32(Error:e) {\n" + pre +
            "    pick (e) {\n" + "\n".join(lines) + "\n    }\n    exit 9i32;\n};\n")


# the §3 example's function, reused by §3.1
DIVIDE = """func:divide = int32(int32:a, int32:b)
    requires b != 0i32
    ensures result > 0i32
{
    pass(10i32); // Hardcoded for example
};"""

HALF = "func:half = int32(int32:n) requires n > 0i32 { pass (n / 2i32); };"

FACT = """func:fact = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 1i32; }
    pass (n * (raw fact(n - 1i32)));
};"""

UPDATE_LIMITED = """Rules<int32>:EvenIdx = { $ % 2i32 == 0i32 };
Rules<int32>:OddIdx  = { $ % 2i32 == 1i32 };

func:update = int32(limit<EvenIdx> int32:i, limit<OddIdx> int32:j, int32[8]:arr) never fails {
    int32->:a = $$m arr[i => int64];   // an exclusive claim at an even index
    int32->:b = $$m arr[j => int64];   // z3 proves i != j: the `disjoint` row discharges
    <-a = 7i32;
    <-b = 9i32;
    pass ((<-a) + (<-b));
};"""

UPDATE_PLAIN = """func:update = int32(int32:i, int32:j, int32[8]:arr) never fails {
    int32->:a = $$m arr[i => int64];
    int32->:b = $$m arr[j => int64];
    <-a = 7i32;
    <-b = 9i32;
    pass ((<-a) + (<-b));
};"""

ARR8 = "int32[8]:arr = [0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32];"

WILDX_OK = """    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 184u8;                   // mov eax, 7
    page[1i64] = 7u8;
    page[2i64] = 0u8;
    page[3i64] = 0u8;
    page[4i64] = 0u8;
    page[5i64] = 195u8;                   // ret
    wildx_seal(page);
    int64:r = wildx_call(page, 0i64);
    wildx_free(page);
    if (r != 7i64) { exit 10i32; }
    exit 0i32;"""


# ================================================================== the banner (1-21)
claim("vf0003", D, 3, "mathematically prove the correctness of the code before it is allowed to execute", "rule",
      "Nitpick proves the code correct with Z3 before it is allowed to execute.",
      untestable="[vague] a statement of intent: the plain build runs unverified code by design (the "
                 "banner at 5-21 and §1.2), and the sentence names no outcome a program can check")

claim("vf0007", D, 7, "`npkc --obligations DIR`", "rule",
      "The compiler writes every function's proof obligations as SMT-LIB2 text under `--obligations DIR`: "
      "numbered .smt2 files holding (check-sat) queries, plus index.txt and rows.txt.",
      expect="sh:0", sh=obl_sh("vf0007", """func:quot = int32(int32:a, int32:b) never fails { pass (a / b); };

func:main = int32(cstring[]:_~argv) {
    int32:q = raw quot(raw v32(10i32), raw v32(2i32));
    if (q != 5i32) { exit 10i32; }
    exit 0i32;
};""", """
ls obl/*.smt2 >/dev/null 2>&1 || exit 1
grep -q 'check-sat' obl/*.smt2 || exit 1
[ -s obl/index.txt ] || exit 1
[ -s obl/rows.txt ] || exit 1
exit 0"""),
      wrong="the flag is refused, or no .smt2 query, index.txt or rows.txt is written")

claim("vf0008", D, 8, "`npkc --elide nitpick.obligations`", "rule",
      "The compiler reads a manifest of verdicts with `--elide FILE` and emits the verified build.",
      untestable="[z3] the manifest's verdicts come only from `npkg verify` with the pinned z3; a hand-made "
                 "manifest's header (the z3 pin, the profile) is §8's and outside this claim")

claim("vf0009", D, 9, "spawns the pinned z3", "rule",
      "`npkg verify` runs one fresh z3 per function, decides every obligation, holds the rows to the committed "
      "nitpick.obligations and emits the VERIFIED build, each discharged guard replaced by llvm.assume.",
      untestable="[z3] needs `npkg verify` with the pinned z3")

claim("vf0020", D, 20, "manifest holds 5,890 rows", "rule",
      "At the 1.5 close the compiler's own manifest holds 5,890 rows.",
      untestable="[tree] a figure about the compiler's own tree and manifest")


# ================================================================== §1.1 assert_static
claim("vf0026", D, 26, "compilation immediately halts", "rule",
      "An `assert_static` whose expression evaluates to false halts compilation.",
      expect="refuse", src=main_("""    assert_static(2i32 < 1i32);
    exit 0i32;"""), wrong="accepted (the false assertion ignored)")

claim("vf0028", D, 28, "```nitpick", "example",
      "The example `assert_static(1i32 == 1i32);` compiles: a true constant proposition passes and the "
      "program runs.",
      expect="run:0", src=main_("""    assert_static(1i32 == 1i32);
    exit 0i32;"""), wrong="refused")

claim("vf0035", D, 35, "`NITPICK-TYPE-069`", "rule",
      "An assert_static proposition that reads a value the evaluator cannot see (a run-time value) is refused, "
      "NITPICK-TYPE-069.",
      expect="refuse:TYPE-069", src=main_("""    int32:d = raw v32(1i32);
    assert_static(d > 0i32);
    exit 0i32;"""), wrong="accepted (folded as unknown, or lowered to a run-time check)")

claim("vf0036", D, 36, "one that folds to `false` halts compilation under the same code", "rule",
      "An assert_static that folds to false halts compilation with NITPICK-TYPE-069.",
      expect="refuse:TYPE-069", src=main_("""    assert_static(1i32 == 2i32);
    exit 0i32;"""), wrong="accepted, or refused under another code")

claim("vf0037", D, 37, "`comptime` body the evaluator folds it per call", "rule",
      "In a comptime body an assert_static over the function's parameter is folded per call: called "
      "comptime with a value that satisfies it, the program compiles and computes.",
      expect="run:0", src=main_("""    int32:v = comptime(checked(3i32));
    if (v != 6i32) { exit 10i32; }
    exit 0i32;""", """comptime func:checked = int32(int32:n) {
    assert_static(n > 0i32);
    pass (n * 2i32);
};"""), wrong="refused as reading a run-time value (TYPE-069 at the declaration)")

claim("vf0037b", D, 37, "a false `prove` there", "rule",
      "A false `prove` in a comptime body, evaluated at a comptime call, is a counterexample: compilation "
      "is refused.",
      expect="refuse", src=main_("""    int32:v = comptime(low(3i32));
    exit 0i32;""", """comptime func:low = int32(int32:n) { prove(n > 5i32); pass n; };"""),
      wrong="accepted (the comptime prove not evaluated)")

claim("vf0038", D, 38, "The statement lowers to nothing", "rule",
      "An assert_statement lowers to nothing: the IR of a program with `assert_static(1i32 == 1i32)` appended "
      "to a line has as many lines as the same program without it.",
      expect="sh:0", sh=("mkdir a b\n" +
                         heredoc("a/vf0038.npk", whole("vf0038", main_("""    int32:x = raw v32(3i32); assert_static(1i32 == 1i32);
    if (x != 3i32) { exit 10i32; }
    exit 0i32;"""))) +
                         heredoc("b/vf0038.npk", whole("vf0038", main_("""    int32:x = raw v32(3i32);
    if (x != 3i32) { exit 10i32; }
    exit 0i32;"""))) +
                         '"$NPKC" a/vf0038.npk -o a.ll >a.out 2>&1 || exit 3\n'
                         '"$NPKC" b/vf0038.npk -o b.ll >b.out 2>&1 || exit 3\n'
                         '[ "$(wc -l < a.ll)" -eq "$(wc -l < b.ll)" ] || exit 1\n'
                         "exit 0\n"),
      wrong="the statement emits code (a branch, a call or a constant): the two IRs differ in length",
      note="A line count, not a byte compare: site numbers may shift between the two programs.")

claim("vf0039", D, 39, "row in the manifest is the catalogue's `checker` entry", "rule",
      "An assert_static's row is the catalogue's checker entry: one `assert-static` row, frontend-decided "
      "(`c` in rows.txt's encoded column), no query.",
      expect="sh:0", sh=obl_sh("vf0039", main_("""    assert_static(2i32 == 2i32);
    exit 0i32;"""), """
[ "$(rows assert-static vf0039.)" -eq 1 ] || exit 1
[ "$(field assert-static vf0039. 5 | sort -u)" = "c" ] || exit 1
exit 0"""), wrong="no assert-static row, or a row with a query (encoded 1)")


# ================================================================== §1.2 prove
claim("vf0043", D, 43, "forces the SMT solver to construct a mathematical proof", "rule",
      "`prove` makes the solver prove the expression across all control flows and states.",
      untestable="[z3] a verdict of the verified build; the `--verify` flag it names is struck (§5, line 86)")

claim("vf0045", D, 45, "If the solver finds a path where the expression is false, compilation fails", "rule",
      "A prove with a counterexample path fails the (verified) compilation and reports the counterexample.",
      untestable="[z3] the verified build's refusal (VERIFY-001) needs z3's verdict; `--prove-report` is struck")

claim("vf0047", D, 47, "```nitpick", "example",
      "The example compiles: `prove(x != 0i32)` inside `if (x > 0i32)` is accepted, and the plain build runs "
      "it as nothing.",
      expect="run:0", src=main_("""    int32:x = raw get_val();
    if (x > 0i32) {
        prove(x != 0i32); // Mathematically verified at compile time.
    }
    exit 0i32;""", """func:get_val = int32() never fails { pass 7i32; };"""),
      wrong="refused",
      note="The example leaves get_val undeclared and calls it bare; a never-fails call is spelled `raw`.")

claim("vf0055", D, 55, "path-condition-aware", "rule",
      "Branch guards of enclosing control flow are asserted as axioms before a prove's obligation.",
      untestable="[z3] only a z3 verdict shows which hypotheses a row carries")

claim("vf0059", D, 59, "an `if`'s condition inside its then-arm and its negation", "rule",
      "An if's condition is a hypothesis in its then-arm, its negation in the else-arm.",
      untestable="[z3] a hypothesis of the encoder, visible only through a verdict")

claim("vf0061", D, 61, "terminator", "rule",
      "After an arm that never falls through (pass, fail, return, exit, trap, break, continue, give), the other "
      "arm's condition holds.",
      untestable="[z3] a hypothesis of the encoder, visible only through a verdict")

claim("vf0063", D, 63, "a `pick` arm's pattern (a value, a range, a wildcard as the", "rule",
      "A pick arm is taken under its pattern and the negations of the earlier arms: the first matching arm "
      "in source order wins.",
      m10="p03_first_match_wins",
      note="The text states the solver's model of pick; the run checks the emitted code the model assumes.")

claim("vf0065", D, 65, "`where` guard", "rule",
      "A pick arm's where guard is a hypothesis; none when a fall sits in the pick, only the pattern when any "
      "arm carries a guard.",
      untestable="[z3] a hypothesis of the encoder, visible only through a verdict")

claim("vf0066", D, 66, "a loop's negated condition after a loop nothing", "rule",
      "After a loop nothing breaks out of, the negated loop condition is a hypothesis.",
      untestable="[z3] a hypothesis of the encoder, visible only through a verdict")

claim("vf0067", D, 67, "`when`'s `then` and `end` on whether the body ran", "rule",
      "when's then and end blocks carry whether the body ran as a hypothesis.",
      untestable="[z3] a hypothesis of the encoder, visible only through a verdict")

claim("vf0068", D, 68, "a ternary's branches under theirs", "rule",
      "A ternary's branches are evaluated under their conditions: only the chosen one runs.",
      m10="x05_ternary_evaluates_one_branch",
      note="The text states the solver's model; the run checks the emitted code the model assumes.")

claim("vf0068b", D, 68, "right-hand side of `&&`/`||`", "rule",
      "The right-hand side of && and || is evaluated under its left side: a division guarded by the left "
      "operand never runs when the left operand decides.",
      expect="run:0", src=main_("""    int32:d = raw v32(0i32);
    bool:b = (d != 0i32) && ((100i32 / d) > 1i32);
    if (b) { exit 10i32; }
    bool:c = (d == 0i32) || ((100i32 / d) > 1i32);
    if (!c) { exit 11i32; }
    exit 0i32;"""), wrong="both sides evaluated: the division traps DivByZero (97)",
      note="The text states the solver's model; the run checks the emitted code the model assumes.")

claim("vf0070", D, 70, "MERGE as `(ite c v_then v_else)`", "rule",
      "Versions after an if, a when or a pick merge as an ite; a pick expression's value is the chain of its "
      "arms' give terms.",
      untestable="[z3] the encoder's terms, visible only through a verdict")

claim("vf0072", D, 72, "counted loop's `$` and a range `for`'s binding are terms with their bounds", "rule",
      "A counted loop's `$` and a range for's binding are terms carrying their bounds.",
      untestable="[z3] the encoder's terms, visible only through a verdict")

claim("vf0075", D, 75, "is a row of kind `prove`", "rule",
      "Each `prove(e)` is one obligation row of kind `prove`.",
      expect="sh:0", sh=obl_sh("vf0075", main_("""    int32:x = raw v32(3i32);
    if (x > 0i32) {
        prove(x != 0i32);
    }
    exit 0i32;"""), """
[ "$(rows prove vf0075.)" -eq 1 ] || exit 1
exit 0"""), wrong="no prove row, or more than one")

claim("vf0076", D, 76, "nothing executes", "rule",
      "A prove is walked quiet: nothing in it executes, so a division by zero inside a prove does not trap "
      "at run time.",
      expect="run:0", src=main_("""    int32:d = raw v32(0i32);
    prove((100i32 / d) > 0i32);
    exit 0i32;"""), wrong="the proposition is evaluated: DivByZero (97)")

claim("vf0077", D, 77, "is not a site", "rule",
      "A division inside a prove is not a site: it records no div-zero row (while the prove row exists).",
      expect="sh:0", sh=obl_sh("vf0078", main_("""    int32:d = raw v32(4i32);
    prove((100i32 / d) > 0i32);
    exit 0i32;"""), """
[ "$(rows prove vf0078.)" -eq 1 ] || exit 1
[ "$(rows div-zero vf0078.)" -eq 0 ] || exit 1
exit 0"""), wrong="a div-zero row for the division inside the proposition")

claim("vf0077b", D, 77, "knowledge for every site", "rule",
      "Once discharged, a prove is knowledge for every site after it.",
      untestable="[z3] a discharge is z3's verdict")

claim("vf0078", D, 78, "The plain build lowers the", "rule",
      "The plain build lowers a prove to nothing and claims nothing: a prove that is false at run time does "
      "not trap.",
      expect="run:0", src=main_("""    int32:x = raw v32(-4i32);
    prove(x > 0i32);
    exit 0i32;"""), wrong="a run-time check that traps, or a refusal")

claim("vf0079", D, 79, "The VERIFIED build refuses an", "rule",
      "Under --elide, a prove whose row the manifest does not discharge (open, budget, unencoded or absent) is "
      "NITPICK-VERIFY-001 at the statement.",
      untestable="[z3] needs a manifest from `npkg verify` with the pinned z3")

claim("vf0083", D, 83, "writes the", "rule",
      "`npkg verify --explain` writes the model of an open prove.",
      untestable="[z3] needs `npkg verify` with the pinned z3")

claim("vf0085", D, 85, "is `open` rather than `unencoded`", "rule",
      "A bool proposition always has at least an opaque term, so a prove row is open rather than unencoded.",
      untestable="[z3] `open` is z3's verdict; which propositions the encoder cannot express is not stated here")


# ================================================================== §2 limit<Rules>
claim("vf0096", D, 96, "```nitpick", "example",
      "The example compiles and runs: a Rules block over int32 and a limited local initialised with 5, "
      "which satisfies it.",
      expect="run:0", src="""// 1. Define a rule for an integer
// The '$' variable represents the value being constrained
Rules<int32>:r_positive = { $ > 0i32 };

func:main = int32(cstring[]:_~argv) {
    // 2. Bind the rule to a variable
    limit<r_positive> int32:x = 5i32;
    exit 0i32;
};""", wrong="refused",
      note="The example spells `func:main = int32()`; main's fixed signature (D-089) is used instead.")

claim("vf0109", D, 109, "a typo is `NITPICK-RESOLVE-002`", "rule",
      "The rule name in limit<...> resolves like any name: a misspelt rule at a local is NITPICK-RESOLVE-002.",
      expect="refuse:RESOLVE-002", src=main_("""    limit<r_postive> int32:x = raw v32(5i32);
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted, or another code")

claim("vf0110", D, 110, "`NITPICK-RESOLVE-011`", "rule",
      "A limit<...> naming something that is not a Rules block (a function) is NITPICK-RESOLVE-011.",
      expect="refuse:RESOLVE-011", src=main_("""    limit<helper> int32:x = raw v32(5i32);
    exit 0i32;""", "func:helper = int32(int32:v) never fails { pass v; };"), wrong="accepted, or another code")

claim("vf0111", D, 111, "parameter", "rule",
      "The rule name resolves at a parameter: a misspelt rule on a parameter is NITPICK-RESOLVE-002.",
      expect="refuse:RESOLVE-002", src=main_("""    int32:v = raw keep(raw v32(5i32));
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:keep = int32(limit<r_postive> int32:n) never fails { pass n; };"""), wrong="accepted, or another code")

claim("vf0111b", D, 111, "and a refinement", "rule",
      "The rule name resolves at a refinement: a misspelt refinement inside a Rules block is NITPICK-RESOLVE-002.",
      expect="refuse:RESOLVE-002", src=main_("""    limit<r_small> int32:x = raw v32(5i32);
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
Rules<int32>:r_small = { limit<r_postive>, $ < 100i32 };"""), wrong="accepted, or another code")

claim("vf0111c", D, 111, "types eagerly", "rule",
      "A Rules body types eagerly: an ill-typed Rules block is refused even when nothing uses it.",
      expect="refuse", src=main_("""    exit 0i32;""", "Rules<int32>:r_unused = { $ + 1i32 };"),
      wrong="accepted (typed only when a binding uses it)")

claim("vf0112", D, 112, "every clause a `bool`", "rule",
      "Every Rules clause is a bool: a clause of type int32 is refused.",
      expect="refuse", src=main_("""    limit<r_num> int32:x = raw v32(5i32);
    exit 0i32;""", "Rules<int32>:r_num = { $ + 1i32 };"), wrong="accepted (a non-zero integer read as true)")

claim("vf0112b", D, 112, "subject's type", "rule",
      "`$` has the subject's type: in a Rules<bool>, comparing `$` with an int32 is refused.",
      expect="refuse", src=main_("""    limit<r_b> bool:x = raw vb(true);
    exit 0i32;""", "Rules<bool>:r_b = { $ > 0i32 };"), wrong="accepted")

claim("vf0113", D, 113, "`limit<r_positive> int64:x` refuses", "rule",
      "A limited binding's declared type must be the rule's subject by identity: limit<r_positive> int64:x "
      "over a Rules<int32> is NITPICK-TYPE-059.",
      expect="refuse:TYPE-059", src=main_("""    limit<r_positive> int64:x = raw v64(5i64);
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted (widened)")

claim("vf0114", D, 114, "and so does a type parameter", "rule",
      "A limited binding whose declared type is a type parameter is NITPICK-TYPE-059.",
      expect="refuse:TYPE-059", src=main_("""    int32:v = raw keep::<int32>(raw v32(5i32));
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:keep<T> = T(limit<r_positive> T:x) never fails { pass x; };"""), wrong="accepted")

claim("vf0116", D, 116, "clause is a contract expression and follows", "rule",
      "A Rules clause is a contract expression under §3's admission: a clause using `?|` is refused.",
      expect="refuse", src=main_("""    limit<r_fall> int32:x = raw v32(5i32);
    exit 0i32;""", """error:E1;
func:mayfail = int32(int32:v) { if (v < 0i32) { fail E1; } pass v; };
Rules<int32>:r_fall = { (mayfail($) ?| 0i32) > 0i32 };"""), wrong="accepted")

claim("vf0119", D, 119, "is enforced in every build", "rule",
      "limit<Rules> is enforced in every build: a limited local initialised at run time with a value its rule "
      "refuses traps LimitViolated in the plain build.",
      expect="trap:LimitViolated", src=main_("""    limit<r_positive> int32:x = raw v32(-3i32);
    exit 10i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="no check without --verify: exit 10")

claim("vf0121", D, 121, "the integrated Z3 solver proves that the assigned", "rule",
      "With verification the solver proves `5i32` satisfies `$ > 0i32` and the check is removed.",
      untestable="[z3] a discharge and its elision are the verified build's")

claim("vf0124", D, 124, "traps to `failsafe`", "rule",
      "Where a check remains, a violation traps to failsafe: an assignment of a run-time value the rule "
      "refuses traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_positive> int32:x = 5i32;
    x = raw v32(0i32);
    exit 10i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="the write passes unchecked: exit 10")

claim("vf0127", D, 127, "proving a constraint removes its runtime check", "rule",
      "Proving a constraint removes its runtime check.",
      untestable="[z3] elision is the verified build's")

claim("vf0131", D, 131, "checked AFTER every write", "rule",
      "A limited binding is checked after every write over its whole value: a compound assignment that "
      "leaves the rule traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_small> int32:c = 8i32;
    c += raw v32(5i32);
    exit 10i32;""", "Rules<int32>:r_small = { $ >= 0i32, $ < 10i32 };"), wrong="compound writes unchecked: exit 10")

claim("vf0132", D, 132, "a declaration without one is not a", "rule",
      "A declaration without an initialiser is not a write point: the vacant value (0, outside `$ > 0`) is "
      "never checked, and the first assignment is.",
      expect="run:0", src=main_("""    limit<r_positive> int32:x;
    x = raw v32(4i32);
    if (x != 4i32) { exit 10i32; }
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"),
      wrong="the vacant 0 checked at the declaration: LimitViolated (108)")

claim("vf0133", D, 133, "every assignment to it", "rule",
      "Every assignment to a limited binding is a write point: assigning a whole struct value the rule "
      "refuses traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_q1> Pt:p = Pt{ x: 1i32, y: 2i32 };
    p = Pt{ x: raw v32(-1i32), y: 2i32 };
    exit 10i32;""", """struct:Pt = { int32:x; int32:y; };
Rules<Pt>:r_q1 = { $.x >= 0i32, $.y >= 0i32 };"""), wrong="unchecked: exit 10")

claim("vf0134", D, 134, "a field or element store re-checks the root", "rule",
      "A field store to a limited struct re-checks the whole root: storing a refused field value traps "
      "LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_q1> Pt:p = Pt{ x: 1i32, y: 2i32 };
    p.x = raw v32(-5i32);
    exit 10i32;""", """struct:Pt = { int32:x; int32:y; };
Rules<Pt>:r_q1 = { $.x >= 0i32, $.y >= 0i32 };"""), wrong="field stores unchecked: exit 10")

claim("vf0134b", D, 134, "element store", "rule",
      "An element store to a limited array re-checks the whole root: storing a refused element traps "
      "LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_all> int32[3]:a = [1i32, 2i32, 3i32];
    a[1i64] = raw v32(-5i32);
    exit 10i32;""", "Rules<int32[3]>:r_all = { $[0i64] > 0i32, $[1i64] > 0i32, $[2i64] > 0i32 };"),
      wrong="element stores unchecked: exit 10")

claim("vf0135", D, 135, "callee's entry for a limited parameter, once per call in a sync function", "rule",
      "A limited parameter is checked at the callee's entry in a sync function: a call with a refused "
      "argument traps LimitViolated before the body runs.",
      expect="trap:LimitViolated", src=main_("""    int32:v = raw limited(raw v32(-5i32));
    exit 10i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:limited = int32(limit<r_positive> int32:x) never fails { pass (x + 100i32); };"""),
      wrong="parameters unchecked: exit 10")

claim("vf0136", D, 136, "once per task at state 0 in a coroutine", "rule",
      "A coroutine's limited parameter is checked at state 0: awaiting it with a refused argument traps "
      "LimitViolated.",
      expect="trap:LimitViolated", src="""error:E9;
Rules<int32>:r_positive = { $ > 0i32 };
async func:fetch = int32(limit<r_positive> int32:v) { pass (v + 1i32); };

async func:main = int32(cstring[]:_~argv) {
    int32:b = (await fetch(raw v32(-2i32))) ?! E9;
    exit 10i32;
};""", wrong="coroutine parameters unchecked: exit 10")

claim("vf0137", D, 137, "`@\"npk.<module>.<name>\"`", "rule",
      "The check is one generated predicate per Rules declaration, emitted as @\"npk.<module>.<name>\".",
      expect=r'ir:^define [^\n]*@"npk\.vf0137\.r_positive"\(', src=main_("""    limit<r_positive> int32:x = raw v32(5i32);
    if (x != 5i32) { exit 10i32; }
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"),
      wrong="no such function: the rule inlined, or named otherwise")

claim("vf0138", D, 138, "the clauses in source order, short-circuit", "rule",
      "A rule's clauses run in source order, short-circuit: `$ != 0` false ends the check, so the division "
      "in the next clause never runs and the trap is LimitViolated, not DivByZero.",
      expect="trap:LimitViolated", src=main_("""    limit<r_div> int32:x = raw v32(0i32);
    exit 10i32;""", "Rules<int32>:r_div = { $ != 0i32, 100i32 / $ > 1i32 };"),
      wrong="all clauses evaluated: DivByZero (97)")

claim("vf0138b", D, 138, "refinements then the clauses", "rule",
      "The refinements run before the clauses: a refinement written after a dividing clause still runs "
      "first, so zero traps LimitViolated, not DivByZero.",
      expect="trap:LimitViolated", src=main_("""    limit<r_div> int32:x = raw v32(0i32);
    exit 10i32;""", """Rules<int32>:r_nz = { $ != 0i32 };
Rules<int32>:r_div = { 100i32 / $ > 1i32, limit<r_nz> };"""),
      wrong="plain source order: the division runs first, DivByZero (97)")

claim("vf0140", D, 140, "limited binding has no address", "rule",
      "`@` of a limited binding is refused, NITPICK-TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    limit<r_positive> int32:x = raw v32(5i32);
    int32->:p = @x;
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted")

claim("vf0140b", D, 140, "`$$m`", "rule",
      "`$$m` of a limited binding is refused, NITPICK-TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    limit<r_positive> int32:x = raw v32(5i32);
    int32->:p = $$m x;
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted")

claim("vf0140c", D, 140, "`$$i` of it", "rule",
      "`$$i` of a limited binding is refused, NITPICK-TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    limit<r_positive> int32:x = raw v32(5i32);
    int32->:p = $$i x;
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted")

claim("vf0141", D, 141, "out of an owning field or element of it, refuse (NITPICK-TYPE-063)", "rule",
      "A move out of an owning field of a limited binding is refused, NITPICK-TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    limit<r_named> Named:n = Named{ name: string_concat("ab", "c"), v: raw v32(5i32) };
    string:s = move(n.name);
    exit 0i32;""", """struct:Named = { string:name; int32:v; };
Rules<Named>:r_named = { $.v > 0i32 };"""), wrong="accepted")

claim("vf0141b", D, 141, "element of it", "rule",
      "Passing an owning element out of a limited array is refused, NITPICK-TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    string:s = first(raw v32(1i32)) ?! E1;
    exit 0i32;""", """error:E1;
Rules<string[2]>:r_two = { $[0i64].len > 0i64 };
func:first = string(int32:seed) {
    limit<r_two> string[2]:a = ["ab", "cd"];
    pass a[0i64];
};"""), wrong="accepted")

claim("vf0142", D, 142, "pass it by value", "rule",
      "A limited binding passed by value is accepted (the permitted twin of the address refusal).",
      expect="run:0", src=main_("""    limit<r_positive> int32:x = raw v32(5i32);
    int32:v = raw show(x);
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:show = int32(int32:n) never fails { pass n; };"""), wrong="refused")

claim("vf0144", D, 144, "trait signature's parameter", "rule",
      "A limit on a trait signature's parameter (no write point) is refused, NITPICK-TYPE-064.",
      expect="refuse:TYPE-064", src=main_("""    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
trait:Scaler = {
    func:scale = int32(Self:self, limit<r_positive> int32:k);
};"""), wrong="accepted")

claim("vf0144b", D, 144, "a `wild`/`wildx` binding", "rule",
      "A limit on a `wild` binding is refused, NITPICK-TYPE-064.",
      expect="refuse:TYPE-064", src=main_("""    wild limit<r_positive> int32:w = raw v32(5i32);
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), wrong="accepted",
      note="The wildx twin is not tested separately: its binding would need a pointer-typed rule.")

claim("vf0145", D, 145, "function;", "rule",
      "A limit in a comptime function (its parameter) is refused, NITPICK-TYPE-064.",
      expect="refuse:TYPE-064", src=main_("""    int32:v = comptime(twice(3i32));
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
comptime func:twice = int32(limit<r_positive> int32:n) { pass (n * 2i32); };"""), wrong="accepted")

claim("vf0145b", D, 145, "`main`/`failsafe`'s parameters under D-244", "rule",
      "A limit on main's parameter is refused: the sentence lists it among the TYPE-064 sites.",
      expect="refuse:TYPE-064", src="""Rules<cstring[]>:r_args = { $.len > 0i64 };

func:main = int32(limit<r_args> cstring[]:_~argv) {
    exit 0i32;
};""", wrong="accepted, or refused under another code",
      note="Ambiguous: 'under D-244' may mean D-244's own refusal code (main/failsafe carry no contract, "
           "TYPE-060) rather than TYPE-064; the expectation reads the sentence's code literally.")

claim("vf0146", D, 146, "every write point is a `limit` row", "rule",
      "Every write point of a limited binding is one `limit` row: an initialiser, an assignment and a "
      "compound assignment in main are three.",
      expect="sh:0", sh=obl_sh("vf0146", main_("""    limit<r_positive> int32:x = raw v32(3i32);
    x = raw v32(4i32);
    x += 1i32;
    if (x != 5i32) { exit 10i32; }
    exit 0i32;""", "Rules<int32>:r_positive = { $ > 0i32 };"), """
[ "$(rows limit vf0146.main)" -eq 3 ] || exit 1
exit 0"""), wrong="fewer rows (a write point without its row) or more")

claim("vf0147", D, 147, "HYPOTHESIS", "rule",
      "The rule is a hypothesis on every later version of the binding, so a division by a limited divisor "
      "discharges, after a loop included.",
      untestable="[z3] a discharge is z3's verdict")

claim("vf0150", D, 150, "scalar family is inside it", "rule",
      "Every scalar family is inside the encoder's fragment: a limit over a flt64 subject is an encoded row.",
      expect="sh:0", sh=obl_sh("vf0150", main_("""    limit<r_unit> flt64:p = raw vf64(0.5f64);
    if (p > 1.0f64) { exit 10i32; }
    exit 0i32;""", "Rules<flt64>:r_unit = { $ >= 0.0f64, $ <= 1.0f64 };"), """
[ "$(rows limit vf0150.main)" -eq 1 ] || exit 1
[ "$(field limit vf0150.main 5)" = "1" ] || exit 1
exit 0"""), wrong="the float row unencoded (0)")

claim("vf0151", D, 151, "a string, a struct or an array is", "rule",
      "A struct subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt).",
      expect="sh:0", sh=obl_sh("vf0151", main_("""    limit<r_q1> Pt:p = Pt{ x: raw v32(1i32), y: raw v32(2i32) };
    if ((p.x + p.y) != 3i32) { exit 10i32; }
    exit 0i32;""", """struct:Pt = { int32:x; int32:y; };
Rules<Pt>:r_q1 = { $.x >= 0i32, $.y >= 0i32 };"""), """
[ "$(rows limit vf0151.main)" -eq 1 ] || exit 1
[ "$(field limit vf0151.main 5)" = "0" ] || exit 1
exit 0"""), wrong="the struct row encoded (1)",
      note="The text contradicts itself: lines 674-676 record D-317 (1.5.8d step 0), by which a by-value "
           "aggregate carries an identity and its fields are functions of it, i.e. a struct subject is encoded.")

claim("vf0151b", D, 151, "or an array", "rule",
      "An array subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt).",
      expect="sh:0", sh=obl_sh("vf0151b", main_("""    limit<r_all> int32[3]:a = [raw v32(1i32), 2i32, 3i32];
    if (a[0i64] != 1i32) { exit 10i32; }
    exit 0i32;""", "Rules<int32[3]>:r_all = { $[0i64] > 0i32, $[1i64] > 0i32, $[2i64] > 0i32 };"), """
[ "$(rows limit vf0151b.main)" -eq 1 ] || exit 1
[ "$(field limit vf0151b.main 5)" = "0" ] || exit 1
exit 0"""), wrong="the array row encoded (1)")

claim("vf0152", D, 152, "is an `unencoded` row", "rule",
      "A string subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt).",
      expect="sh:0", sh=obl_sh("vf0152", main_("""    limit<r_ne> string:s = string_concat("ab", "c");
    if (s.len != 3i64) { exit 10i32; }
    exit 0i32;""", "Rules<string>:r_ne = { $.len > 0i64 };"), """
[ "$(rows limit vf0152.main)" -eq 1 ] || exit 1
[ "$(field limit vf0152.main 5)" = "0" ] || exit 1
exit 0"""), wrong="the string row encoded (1), or no row")

claim("vf0152b", D, 152, "whose guard stays", "rule",
      "An unencoded row's guard stays: a string subject's rule is still checked at run time, and an empty "
      "string traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_ne> string:s = string_concat("", "");
    exit 10i32;""", "Rules<string>:r_ne = { $.len > 0i64 };"), wrong="no check for a subject outside the fragment: exit 10")

claim("vf0153", D, 153, "limited parameters is a `limit-subsume` row", "rule",
      "Every direct call of a sync callee with limited parameters is one limit-subsume row: two calls, two rows.",
      expect="sh:0", sh=obl_sh("vf0153", main_("""    int32:a = raw narrow(raw v32(3i32));
    int32:b = raw narrow(raw v32(4i32));
    if ((a + b) != 7i32) { exit 10i32; }
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:narrow = int32(limit<r_positive> int32:n) never fails { pass n; };"""), """
[ "$(rows limit-subsume vf0153.)" -eq 2 ] || exit 1
exit 0"""), wrong="no limit-subsume rows, or not one per call")

claim("vf0156", D, 156, "ONE `llvm.assume` over the rule's range clauses", "rule",
      "A discharged write point emits one llvm.assume over the rule's range clauses and no check.",
      untestable="[z3] needs a manifest with the row discharged")

claim("vf0158", D, 158, "`limit-subsume` row lets the call name the callee's BODY", "rule",
      "A discharged limit-subsume row lets the call name the callee's body past its checked entry.",
      untestable="[z3] needs a manifest with the row discharged")

claim("vf0159", D, 159, "a sync function with a limited parameter is emitted as", "rule",
      "A sync function with a limited parameter is emitted as <symbol>.body plus its ordinary symbol, the "
      "checked entry.",
      expect=r'ir:^define [^\n]*@"npk\.vf0159\.limited\.body"\(', src=main_("""    int32:v = raw limited(raw v32(3i32));
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
func:limited = int32(limit<r_positive> int32:x) never fails { pass x; };"""),
      wrong="one symbol only, the check inside it")

claim("vf0161", D, 161, "function value, vtable slot and spawn names by construction", "rule",
      "A function value names the checked entry: calling a limited function through a function value with a "
      "refused argument traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    func int32(int32):f = limited;
    int32:b = f(raw v32(-5i32)) ?! E1;
    exit 10i32;""", """error:E1;
Rules<int32>:r_positive = { $ > 0i32 };
func:limited = int32(limit<r_positive> int32:x) { pass (x + 1i32); };"""),
      wrong="the function value bypasses the entry check: exit 10")

claim("vf0164", D, 164, "It traps to `failsafe`, as", "rule",
      "A constraint violation traps to failsafe: a limited local driven out of its rule by a loop traps "
      "LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_small> int32:c = 0i32;
    int32:i = 0i32;
    while (i < 20i32) decreases 20i32 - i {
        c = c + raw v32(1i32);
        i = i + 1i32;
    }
    exit 10i32;""", "Rules<int32>:r_small = { $ >= 0i32, $ < 10i32 };"), wrong="unchecked: exit 10")


# ================================================================== §2.1 Z3 and the borrow checker
claim("vf0174", D, 174, "the solver proves the indices unequal and the borrows disjoint", "rule",
      "With indices under different rules, the solver proves two $$m claims disjoint.",
      untestable="[z3] the disjoint row's discharge is z3's verdict")

claim("vf0177", D, 177, "```nitpick", "example",
      "The example compiles and runs in the plain build: two $$m claims of one array at an even and an odd "
      "index, 7 + 9 = 16.",
      expect="run:0", src=main_("""    %s
    int32:r = raw update(raw v32(2i32), raw v32(3i32), arr);
    if (r != 16i32) { exit 10i32; }
    exit 0i32;""" % ARR8, UPDATE_LIMITED), wrong="refused (an aliasing error), or a wrong sum")

claim("vf0193", D, 193, "declaration-qualifier spelling the prototype text carried", "rule",
      "The declaration-qualifier borrow spelling `$$m int32:a = arr[i];` never existed: it is refused.",
      expect="refuse", src=main_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int64:i = raw v64(1i64);
    $$m int32:a = arr[i];
    exit 0i32;"""), wrong="accepted")

claim("vf0195", D, 195, "is a SHARED claim (many readers)", "rule",
      "$$i is a shared claim: two $$i of one local and a plain read of it may live together.",
      expect="run:0", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$i x;
    int32->:q = $$i x;
    int32:y = x;
    if (((<-p) + (<-q) + y) != 12i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused as a conflict")

claim("vf0196", D, 196, "an EXCLUSIVE one (one writer, no other name)", "rule",
      "$$m is an exclusive claim: reading the local by its name while the $$m claim lives is a static "
      "conflict, NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$m x;
    int32:y = x;
    <-p = 5i32;
    exit 0i32;"""), wrong="accepted")

claim("vf0197", D, 197, "plain address that claims nothing", "rule",
      "`@place` claims nothing: two `@` of one local and a read of it may live together.",
      expect="run:0", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = @x;
    int32->:q = @x;
    <-p = 6i32;
    int32:y = (<-q) + x;
    if (y != 12i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused as a conflict")

claim("vf0198", D, 198, "counts as a write-capable access", "rule",
      "`@place` counts as a write-capable access: taking `@x` while a $$i claim of x lives is "
      "NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$i x;
    int32->:q = @x;
    int32:y = <-p;
    exit 0i32;"""), wrong="accepted (@ read as a read)")

claim("vf0200", D, 200, "conflicts with the call's other arguments", "rule",
      "A whole call argument's claim conflicts with the call's other arguments: `two($$m x, $$i x)` is "
      "NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32:r = raw two($$m x, $$i x);
    exit 0i32;""", "func:two = int32(int32->:a, int32->:b) never fails { pass ((<-a) + (<-b)); };"),
      wrong="accepted")

claim("vf0202", D, 202, "held by that local from its declaration to the end of the block", "rule",
      "A pointer local's claim ends with the block that declares it: after an inner block holding $$m x, x "
      "is read freely.",
      expect="run:0", src=main_("""    int32:x = raw v32(4i32);
    {
        int32->:p = $$m x;
        <-p = 7i32;
    }
    int32:y = x;
    if (y != 7i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused (the claim outlives its block)")

claim("vf0203", D, 203, "a `defer` body sees every claim of its enclosing blocks", "rule",
      "A defer body sees every claim of its enclosing blocks: writing x in a defer while $$i x is held is "
      "NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:r = raw hold(raw v32(4i32));
    exit 0i32;""", """func:hold = int32(int32:v) never fails {
    int32:x = v;
    int32->:p = $$i x;
    defer { x = 9i32; }
    pass (<-p);
};"""), wrong="accepted")

claim("vf0204", D, 204, "Non-lexical lifetimes and two-phase borrows are decided OUT", "rule",
      "Non-lexical lifetimes are out: reading x after the last use of a $$m holder, in the same block, is "
      "still NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$m x;
    <-p = 7i32;
    int32:y = x;
    exit 0i32;"""), wrong="accepted (a non-lexical lifetime)")

claim("vf0207", D, 207, "a nested expression", "rule",
      "A claim in a nested expression is NITPICK-BORROW-014.",
      expect="refuse:BORROW-014", src=main_("""    int32:x = raw v32(4i32);
    int32:y = (<-($$i x)) + 1i32;
    exit 0i32;"""), wrong="accepted")

claim("vf0210", D, 210, "the fix is to spell `@` for an address that claims nothing", "rule",
      "The same nested position with `@` (an address that claims nothing) is accepted.",
      expect="run:0", src=main_("""    int32:x = raw v32(4i32);
    int32:y = (<-(@x)) + 1i32;
    if (y != 5i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused")

claim("vf0212", D, 212, "a field that differs", "rule",
      "Paths through different fields are disjoint: writing s.b while $$m s.a lives is accepted.",
      expect="run:0", src=main_("""    Pr:s = Pr{ a: raw v32(1i32), b: raw v32(2i32) };
    {
        int32->:p = $$m s.a;
        s.b = 5i32;
        <-p = 3i32;
    }
    if ((s.a + s.b) != 8i32) { exit 10i32; }
    exit 0i32;""", "struct:Pr = { int32:a; int32:b; };"), wrong="refused (the whole struct claimed)")

claim("vf0212b", D, 212, "two unequal numerals: disjoint", "rule",
      "Two unequal numeral indices are disjoint: writing a[1] while $$m a[0] lives is accepted.",
      expect="run:0", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    {
        int32->:p = $$m a[0i64];
        a[1i64] = 9i32;
        <-p = 7i32;
    }
    if ((a[0i64] + a[1i64]) != 16i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused (the whole array claimed)")

claim("vf0213", D, 213, "statically overlapping", "rule",
      "Equal numeral indices (nothing computed) overlap statically: writing a[0] while $$m a[0] lives is "
      "NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32->:p = $$m a[0i64];
    a[0i64] = 9i32;
    <-p = 7i32;
    exit 0i32;"""), wrong="accepted, or deferred to a run-time guard")

claim("vf0214", D, 214, "write-capable access under `$$i`", "rule",
      "A write to x while a $$i claim of x lives is NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$i x;
    x = 5i32;
    int32:y = <-p;
    exit 0i32;"""), wrong="accepted")

claim("vf0215", D, 215, "claim on storage a held `@` reaches", "rule",
      "A claim on storage a held `@` reaches is NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = @x;
    int32->:q = $$m x;
    <-q = 5i32;
    exit 0i32;"""), wrong="accepted")

claim("vf0215b", D, 215, "a write through a shared claim's", "rule",
      "A write through a shared ($$i) claim's holder is NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32->:p = $$i x;
    <-p = 5i32;
    exit 0i32;"""), wrong="accepted")

claim("vf0216", D, 216, "a call's arguments among themselves", "rule",
      "A call's arguments conflict among themselves: `two($$i x, @x)` (a write-capable `@` beside a shared "
      "claim) is NITPICK-BORROW-013.",
      expect="refuse:BORROW-013", src=main_("""    int32:x = raw v32(4i32);
    int32:r = raw two($$i x, @x);
    exit 0i32;""", "func:two = int32(int32->:a, int32->:b) never fails { pass ((<-a) + (<-b)); };"),
      wrong="accepted")

claim("vf0219", D, 219, "held by the binding that holds the view from its declaration to the", "rule",
      "A view is a party on its root until the end of the block declaring its holder: after that block the "
      "root may be written.",
      expect="run:0", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int64:n = 0i64;
    {
        int32[]:s = a[1i64...3i64];
        n = s.len;
    }
    a[1i64] = 9i32;
    if (n != 2i64) { exit 10i32; }
    if (a[1i64] != 9i32) { exit 11i32; }
    exit 0i32;"""), wrong="refused (the view outlives its block)")

claim("vf0220", D, 220, "or live for the call a view expression", "rule",
      "A view expression passed as a call argument is live for that call only: the root may be written "
      "after the call.",
      expect="run:0", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int64:n = raw vsum(a[1i64...3i64]);
    a[1i64] = 9i32;
    if (n != 5i64) { exit 10i32; }
    if (a[1i64] != 9i32) { exit 11i32; }
    exit 0i32;""", """func:vsum = int64(int32[]:s) never fails {
    int64:t = 0i64;
    for (int64:k in 0i64...s.len) { t = t + (s[k] => int64); }
    pass t;
};"""), wrong="refused (the argument's view held past the call)")

claim("vf0222", D, 222, "it lives is `NITPICK-BORROW-015`", "rule",
      "A write-capable access of viewed storage while the view lives is NITPICK-BORROW-015.",
      expect="refuse:BORROW-015", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32[]:s = a[1i64...3i64];
    a[1i64] = 9i32;
    if (s.len != 2i64) { exit 10i32; }
    exit 0i32;"""), wrong="accepted")

claim("vf0222b", D, 222, "with no runtime guard for a computed pair", "rule",
      "A computed index against a live view has no run-time guard: the pair refuses (BORROW-015) even when "
      "the index would fall outside the view.",
      expect="refuse:BORROW-015", src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32[]:s = a[1i64...3i64];
    a[raw v64(0i64)] = 9i32;
    if (s.len != 2i64) { exit 10i32; }
    exit 0i32;"""), wrong="accepted with a run-time compare, or accepted")

claim("vf0224", D, 224, "the ESCAPE analysis's provenance", "rule",
      "What a binding views is the escape analysis's provenance at its fixpoint, with per-function summaries.",
      untestable="[internal] the analysis's representation; its consequences are claimed at 219-236")

claim("vf0231", D, 231, "recorded declaration (a `dyn` method, a function value) is read with every", "rule",
      "A call with no recorded declaration is read with every bit set: handing `@d` to a function value while "
      "a view of d lives is refused (BORROW-015), where the direct call is accepted (vf0235).",
      expect="refuse:BORROW-015", src=main_("""    string:d = string_concat("hello", " world");
    string:s = string_from_bytes(d.ptr, 5i64);
    func int64(string->):f = peek;
    int64:n = f(@d) ?! E1;
    if (s.len != 5i64) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:peek = int64(string->:p) { pass p.len; };"""), wrong="accepted (the function value trusted)")

claim("vf0233", D, 233, "The path is what makes", "rule",
      "The path separates fields: a view of one string field does not freeze a write to a sibling int field.",
      expect="run:0", src=main_("""    Bx:b = Bx{ s: string_concat("hello", " world"), t: raw v32(1i32) };
    string:v = string_from_bytes(b.s.ptr, 5i64);
    b.t = 5i32;
    if (v.len != 5i64) { exit 10i32; }
    if (b.t != 5i32) { exit 11i32; }
    exit 0i32;""", "struct:Bx = { string:s; int32:t; };"), wrong="refused (the whole struct frozen)")

claim("vf0235", D, 235, "the mutation summary what makes `@r` handed to a callee that writes", "rule",
      "`@d` handed to a callee that writes nothing through it conflicts with no view of d: accepted.",
      expect="run:0", src=main_("""    string:d = string_concat("hello", " world");
    string:s = string_from_bytes(d.ptr, 5i64);
    int64:n = raw peek(@d);
    if (n != 11i64) { exit 10i32; }
    if (s.len != 5i64) { exit 11i32; }
    exit 0i32;""", "func:peek = int64(string->:p) never fails { pass p.len; };"),
      wrong="refused (BORROW-015 for a callee that only reads)")

claim("vf0236", D, 236, "The prelude `List`'s", "rule",
      "A List's count, cap and items are its header: disjoint from a body view through an element's ptr, "
      "overlapping a slice of its storage.",
      untestable="[internal] the List header's path rule is an analysis detail no single program here isolates")

claim("vf0239", D, 239, "COMPUTED conflict is a RUNTIME GUARD in every build", "rule",
      "A computed conflict is a run-time guard in every build: two $$m claims of one array at computed "
      "indices that are equal at run time trap BorrowOverlap.",
      expect="trap:BorrowOverlap", src=main_("""    %s
    int32:r = raw update(raw v32(2i32), raw v32(2i32), arr);
    exit 10i32;""" % ARR8, UPDATE_PLAIN), wrong="no guard: exit 10")

claim("vf0244", D, 244, "the obligation is the `disjoint` row", "rule",
      "The obligation of a computed claim pair is one `disjoint` row per site: §2.1's example has one.",
      expect="sh:0", sh=obl_sh("vf0244", main_("""    %s
    int32:r = raw update(raw v32(2i32), raw v32(3i32), arr);
    if (r != 16i32) { exit 10i32; }
    exit 0i32;""" % ARR8, UPDATE_LIMITED), """
[ "$(rows disjoint vf0244.)" -eq 1 ] || exit 1
exit 0"""), wrong="no disjoint row, or more than one")

claim("vf0248", D, 248, "removes the compare (no `llvm.assume` over pointers)", "rule",
      "A discharged disjoint row removes the compare, with no llvm.assume over pointers.",
      untestable="[z3] needs a manifest with the row discharged")

claim("vf0250", D, 250, "the verified build carries no compare where the plain build", "rule",
      "In the example the rules make (not (= i j)) unsat, so the verified build carries no compare.",
      untestable="[z3] z3's verdict and the verified build")

claim("vf0253", D, 253, "accesses that spell the SAME ROOT", "rule",
      "Exclusivity is decided among accesses that spell the same root: a $$m claim through one pointer "
      "parameter and a write through another aliasing it are two roots, accepted.",
      expect="run:0", src=main_("""    Pt:p = Pt{ x: raw v32(1i32) };
    int32:r = raw alias(@p, @p);
    if (r != 5i32) { exit 10i32; }
    exit 0i32;""", """struct:Pt = { int32:x; };
func:alias = int32(Pt->:a, Pt->:b) never fails {
    int32->:c = $$m a.x;
    b.x = 5i32;
    pass (<-c);
};"""), wrong="refused (the aliasing seen), contrary to the stated limit")

claim("vf0257", D, 257, "a `fixed` binding has no address", "rule",
      "`@` of a fixed local is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    fixed int32:x = 1i32;
    int32->:p = @x;
    exit 0i32;"""), wrong="accepted")

claim("vf0258", D, 258, "`$$i`", "rule",
      "`$$i` of a fixed local is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    fixed int32:x = 1i32;
    int32->:p = $$i x;
    exit 0i32;"""), wrong="accepted")

claim("vf0258b", D, 258, "`$$m`", "rule",
      "`$$m` of a fixed local is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    fixed int32:x = 1i32;
    int32->:p = $$m x;
    <-p = 2i32;
    exit 0i32;"""), wrong="accepted (a fixed value overwritten)")

claim("vf0258c", D, 258, "the implicit pointer-receiver address", "rule",
      "A pointer-receiver call on a fixed binding (its implicit address) is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    fixed Cfg:c = Cfg{ n: 2i32 };
    drop c.bump();
    exit 0i32;""", """struct:Cfg = { int32:n; };
func:bump = NIL(Cfg->:self) never fails { self.n = self.n + 1i32; pass NIL; };"""), wrong="accepted")

claim("vf0259", D, 259, "field included", "rule",
      "`@` of a fixed field of a plain struct is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    Cfg:c = Cfg{ bound: 1i32, n: 2i32 };
    int32->:p = @c.bound;
    exit 0i32;""", "struct:Cfg = { fixed int32:bound; int32:n; };"), wrong="accepted")

claim("vf0260", D, 260, "through a `fixed` module binding", "rule",
      "`@` of a fixed module binding is refused, NITPICK-TYPE-071.",
      expect="refuse:TYPE-071", src=main_("""    int32->:p = @G;
    exit 0i32;""", "fixed int32:G = 1i32;"), wrong="accepted (a write through it would be a SIGSEGV)")

claim("vf0267", D, 267, "A borrow may not be returned", "rule",
      "A borrow may not be returned: `pass @x` of a local is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", """func:ret = int32->() never fails {
    int32:x = 5i32;
    pass @x;
};"""), wrong="accepted (a dangling pointer)")

claim("vf0267b", D, 267, "stored into anything outliving the frame", "rule",
      "A borrow may not be stored into anything outliving the frame: storing `@x` of a local into the "
      "caller's struct is refused.",
      expect="refuse", src=main_("""    Holder:h = Holder{ inner: NULL };
    drop keep(@h);
    exit 0i32;""", """struct:Holder = { int32->:inner; };
func:keep = NIL(Holder->:h) never fails {
    int32:x = 5i32;
    h.inner = @x;
    pass NIL;
};"""), wrong="accepted")

claim("vf0268", D, 268, "an `await` point", "rule",
      "A borrow may not be carried across an await point: a pointer local holding `@x` used after an await "
      "is refused.",
      expect="refuse", src="""error:E9;
async func:later = int32(int32:v) { pass v; };

async func:main = int32(cstring[]:_~argv) {
    int32:x = raw v32(4i32);
    int32->:p = @x;
    int32:y = (await later(1i32)) ?! E9;
    int32:z = <-p;
    if ((y + z) != 5i32) { exit 10i32; }
    exit 0i32;
};""", wrong="accepted")


# ================================================================== §2.2 Rules composition
claim("vf0276", D, 276, "```nitpick", "example",
      "The example's r_small_positive refines r_positive: a value that meets `$ < 100` but not the "
      "refinement's `$ > 0` traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_small_positive> int32:x = raw v32(0i32);
    exit 10i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
Rules<int32>:r_small_positive = { limit<r_positive>, $ < 100i32 };
// r_small_positive requires: $ > 0i32 AND $ < 100i32"""), wrong="the refinement ignored: exit 10")

claim("vf0279", D, 279, "r_small_positive requires: $ > 0i32 AND $ < 100i32", "rule",
      "r_small_positive requires its own clause too: 100 traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    limit<r_small_positive> int32:x = raw v32(100i32);
    exit 10i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
Rules<int32>:r_small_positive = { limit<r_positive>, $ < 100i32 };"""), wrong="only the refinement checked: exit 10")

claim("vf0282", D, 282, "The Z3 solver can prove that one Rules block subsumes another", "rule",
      "The solver proves one Rules block implies another, enabling narrowing at call sites without checks.",
      untestable="[z3] a limit-subsume discharge is z3's verdict")

claim("vf0285", D, 285, "refining a `Rules<int32>` is `NITPICK-TYPE-059`", "rule",
      "A Rules<int64> refining a Rules<int32> is NITPICK-TYPE-059.",
      expect="refuse:TYPE-059", src=main_("""    limit<r_mixed> int64:w = raw v64(5i64);
    exit 0i32;""", """Rules<int32>:r_positive = { $ > 0i32 };
Rules<int64>:r_mixed = { limit<r_positive>, $ < 9i64 };"""), wrong="accepted")

claim("vf0287", D, 287, "`Rules` block that refines itself, directly or through a chain, is refused", "rule",
      "A Rules block that refines itself directly is refused at resolve, NITPICK-RESOLVE-006.",
      expect="refuse:RESOLVE-006", src=main_("""    limit<r_self> int32:x = raw v32(5i32);
    exit 0i32;""", "Rules<int32>:r_self = { limit<r_self>, $ > 0i32 };"), wrong="accepted, or the compiler hangs")

claim("vf0287b", D, 287, "through a chain", "rule",
      "A Rules block that refines itself through a chain is refused at resolve, NITPICK-RESOLVE-006.",
      expect="refuse:RESOLVE-006", src=main_("""    limit<r_a> int32:x = raw v32(5i32);
    exit 0i32;""", """Rules<int32>:r_a = { limit<r_b>, $ > 0i32 };
Rules<int32>:r_b = { limit<r_a>, $ < 9i32 };"""), wrong="accepted, or the compiler hangs")

claim("vf0290", D, 290, "the conjunction is `enc_rule`", "rule",
      "The conjunction is enc_rule; the implication is a limit-subsume row decided by z3.",
      untestable="[internal] an encoder function name; the row's verdict is z3's")


# ================================================================== §2.1 (second) a field's own rule
claim("vf0299", D, 299, "`sealed limit<Len> int64:count;`", "rule",
      "A struct field may carry limit<R> after its qualifiers and before its type (`sealed limit<Len> "
      "int64:count;`): it compiles, and a write the rule admits runs.",
      expect="run:0", src=main_("""    Ctr:c = Ctr{ count: raw v64(2i64), other: 0i64 };
    c.count = c.count + 1i64;
    if (c.count != 3i64) { exit 10i32; }
    exit 0i32;""", """Rules<int64>:Len = { $ >= 0i64 };
struct:Ctr = { sealed limit<Len> int64:count; int64:other; };"""), wrong="refused")

claim("vf0301", D, 301, "Its subject is the field's type by identity (TYPE-059)", "rule",
      "A field rule's subject must be the field's type by identity: a Rules<int32> on an int64 field is "
      "TYPE-059.",
      expect="refuse:TYPE-059", src=main_("""    Bad:b = Bad{ n: raw v64(1i64) };
    exit 0i32;""", """Rules<int32>:r_i32 = { $ >= 0i32 };
struct:Bad = { limit<r_i32> int64:n; };"""), wrong="accepted")

claim("vf0302", D, 302, "struct literal's value for the field", "rule",
      "A struct literal's value for a limited field is a write point, checked in every build: a refused "
      "value traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    Tank:t = Tank{ n: raw v64(101i64), serial: 1i64 };
    exit 10i32;""", """Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };
struct:Tank = { limit<r_level> int64:n; int64:serial; };"""), wrong="literals unchecked: exit 10")

claim("vf0303", D, 303, "`p.f = v` through a pointer", "rule",
      "An assignment through a pointer to a limited field is a write point: a refused value traps "
      "LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    Tank:t = Tank{ n: 1i64, serial: 1i64 };
    drop setn(@t, raw v64(200i64));
    exit 10i32;""", """Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };
struct:Tank = { limit<r_level> int64:n; int64:serial; };
func:setn = NIL(Tank->:p, int64:v) never fails { p.n = v; pass NIL; };"""), wrong="writes through a pointer unchecked: exit 10")

claim("vf0302b", D, 302, "an assignment through any path (`s.f = v`", "rule",
      "An assignment `s.f = v` to a limited field is a write point: a refused value traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    Tank:t = Tank{ n: 1i64, serial: 1i64 };
    t.n = raw v64(-1i64);
    exit 10i32;""", """Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };
struct:Tank = { limit<r_level> int64:n; int64:serial; };"""), wrong="field assignments unchecked: exit 10")

claim("vf0303b", D, 303, "and a compound assignment", "rule",
      "A compound assignment to a limited field is a write point: leaving the rule traps LimitViolated.",
      expect="trap:LimitViolated", src=main_("""    Tank:t = Tank{ n: 1i64, serial: 1i64 };
    t.n += raw v64(150i64);
    exit 10i32;""", """Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };
struct:Tank = { limit<r_level> int64:n; int64:serial; };"""), wrong="compound writes unchecked: exit 10")

claim("vf0306", D, 306, "limited binding is two checks at two keys", "rule",
      "A write to a limited field of a limited binding is two limit rows (the field's and the root's): "
      "adding the statement `t.n = v` adds two limit rows to main.",
      expect="sh:0", sh=("mkdir a b\n" +
                         heredoc("a/vf0306.npk", whole("vf0306", main_("""    limit<r_t> Tk:t = Tk{ n: 1i64, m: 1i64 };
    t.n = raw v64(2i64);
    if (t.n != 2i64) { exit 10i32; }
    exit 0i32;""", """Rules<int64>:r_n = { $ >= 0i64 };
struct:Tk = { limit<r_n> int64:n; int64:m; };
Rules<Tk>:r_t = { $.m >= 0i64 };"""))) +
                         heredoc("b/vf0306.npk", whole("vf0306", main_("""    limit<r_t> Tk:t = Tk{ n: 1i64, m: 1i64 };
    if (t.n != 2i64) { exit 10i32; }
    exit 0i32;""", """Rules<int64>:r_n = { $ >= 0i64 };
struct:Tk = { limit<r_n> int64:n; int64:m; };
Rules<Tk>:r_t = { $.m >= 0i64 };"""))) +
                         '"$NPKC" a/vf0306.npk --obligations oa -o a.ll >a.out 2>&1 || exit 3\n'
                         '"$NPKC" b/vf0306.npk --obligations ob -o b.ll >b.out 2>&1 || exit 3\n'
                         r"""na=$(awk -F'\t' '$3 == "limit" && index($6, "vf0306.main") > 0' oa/rows.txt | wc -l)
nb=$(awk -F'\t' '$3 == "limit" && index($6, "vf0306.main") > 0' ob/rows.txt | wc -l)
[ $((na - nb)) -eq 2 ] || exit 1
exit 0
"""),
      wrong="one row for the statement (one check), or none")

claim("vf0306b", D, 306, "Every read of", "rule",
      "Every read of a limited field is a fact: the rule over the read's term is a hypothesis for later rows.",
      untestable="[z3] a hypothesis shows only through z3's verdicts")

claim("vf0309", D, 309, "The rule must hold of the field's vacant", "rule",
      "A field rule that holds of the vacant value (0 for `$ >= 0`) is accepted.",
      expect="run:0", src=main_("""    Good:g = Good{ n: raw v64(4i64), free: 0i64 };
    if (g.n != 4i64) { exit 10i32; }
    exit 0i32;""", """Rules<int64>:r_nonneg = { $ >= 0i64 };
struct:Good = { limit<r_nonneg> int64:n; int64:free; };"""), wrong="refused")

claim("vf0311", D, 311, "TYPE-077 otherwise", "rule",
      "A field rule that the vacant value fails (0 for `$ > 0`) is NITPICK-TYPE-077.",
      expect="refuse:TYPE-077", src=main_("""    BadPos:b = BadPos{ n: raw v64(1i64) };
    exit 0i32;""", """Rules<int64>:r_pos = { $ > 0i64 };
struct:BadPos = { limit<r_pos> int64:n; };"""), wrong="accepted")

claim("vf0311b", D, 311, "TYPE-077", "rule",
      "A bool field whose rule refuses the vacant `false` is NITPICK-TYPE-077.",
      expect="refuse:TYPE-077", src=main_("""    BadBool:b = BadBool{ armed: raw vb(true) };
    exit 0i32;""", """Rules<bool>:r_true = { $ == true };
struct:BadBool = { limit<r_true> bool:armed; };"""), wrong="accepted")

claim("vf0311c", D, 311, "a rule the folder cannot decide there is refused too", "rule",
      "A field rule the constant folder cannot decide at the declaration (a call) is refused.",
      expect="refuse", src=main_("""    BadCall:b = BadCall{ n: raw v64(1i64) };
    exit 0i32;""", """func:pure_id = int64(int64:v) never fails pure { pass v; };
Rules<int64>:r_call = { raw pure_id($) >= 0i64 };
struct:BadCall = { limit<r_call> int64:n; };"""), wrong="accepted")

claim("vf0312", D, 312, "the subject is a plain integer, a `bool` or a `char`", "rule",
      "A field rule's subject is a plain integer, a bool or a char: a flt64 field with a rule is refused, "
      "even one the vacant 0.0 would satisfy.",
      expect="refuse", src=main_("""    BadFloat:b = BadFloat{ p: raw vf64(0.5f64) };
    exit 0i32;""", """Rules<flt64>:r_unit = { $ >= 0.0f64, $ <= 1.0f64 };
struct:BadFloat = { limit<r_unit> flt64:p; };"""), wrong="accepted")

FIELD_DECLS = """Rules<int64>:r_nonneg = { $ >= 0i64 };
struct:Good = { limit<r_nonneg> int64:n; int64:free; };
func:poke = NIL(int64->:p) never fails { pass NIL; };
func:read_at = int64(int64->:p) never fails { pass (<-p); };"""

claim("vf0312b", D, 312, "A limited field has no", "rule",
      "`@s.f` of a limited field is refused, TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    Good:g = Good{ n: 1i64, free: 0i64 };
    drop poke(@g.n);
    exit 0i32;""", FIELD_DECLS), wrong="accepted")

claim("vf0313b", D, 313, "through a pointer to its struct as well", "rule",
      "`@` of a limited field reached through a pointer to its struct is refused, TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    Good:g = Good{ n: 1i64, free: 0i64 };
    Good->:pg = @g;
    drop poke(@pg.n);
    exit 0i32;""", FIELD_DECLS), wrong="accepted")

claim("vf0313c", D, 313, "`$$m`/`$$i`", "rule",
      "`$$m` of a limited field is refused, TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    Good:g = Good{ n: 1i64, free: 0i64 };
    drop poke($$m g.n);
    exit 0i32;""", FIELD_DECLS), wrong="accepted")

claim("vf0314", D, 314, "of it and a pointer-receiver call on it refuse", "rule",
      "`$$i` of a limited field is refused, TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    Good:g = Good{ n: 1i64, free: 0i64 };
    int64:r = raw read_at($$i g.n);
    exit 0i32;""", FIELD_DECLS), wrong="accepted")

claim("vf0314b", D, 314, "pointer-receiver call on it", "rule",
      "A pointer-receiver call on a limited field is refused, TYPE-063.",
      expect="refuse:TYPE-063", src=main_("""    Good:g = Good{ n: 1i64, free: 0i64 };
    drop g.n.poke();
    exit 0i32;""", FIELD_DECLS), wrong="accepted")

claim("vf0315", D, 315, "REACH arms `LimitViolated` at the writes", "rule",
      "The reach analysis arms LimitViolated at a limited field's writes: a program writing one, whose "
      "failsafe names every arm but LimitViolated, is refused.",
      expect="refuse", fs=False, src="""Rules<int64>:r_level = { $ >= 0i64, $ <= 100i64 };
struct:Tank = { limit<r_level> int64:n; int64:serial; };

func:main = int32(cstring[]:_~argv) {
    Tank:t = Tank{ n: raw v64(5i64), serial: 1i64 };
    if (t.n != 5i64) { exit 10i32; }
    exit 0i32;
};

""" + failsafe_custom(skip=("LimitViolated",)), wrong="accepted (the write's trap not armed)",
      note="Reads 'arms' through D-179's arm contract: a reachable identity must be named in failsafe.")

claim("vf0317", D, 317, "a name D-239 reserves", "rule",
      "ListLen is a name D-239 reserves: a user Rules block named ListLen is refused.",
      expect="refuse", src=main_("""    limit<ListLen> int64:x = raw v64(1i64);
    exit 0i32;""", "Rules<int64>:ListLen = { $ >= 0i64 };"), wrong="accepted")

claim("vf0316b", D, 316, "The prelude's `List` carries", "rule",
      "The prelude's List carries the ListLen rule on count and cap.",
      untestable="[internal] no program may write a List's header, so the rule is visible only as the "
                 "prelude's own rows and facts")

claim("vf0318", D, 318, "built-in lengths of `string`, `cstring`, a slice and a `buffer` carry the same", "rule",
      "The built-in lengths carry the [0, 2^47] bound as a fact at every read.",
      untestable="[z3] a fact shows only through z3's verdicts")

claim("vf0321", D, 321, "program may write a header", "rule",
      "No program may write a header: assigning a string's `.len` is refused.",
      expect="refuse", src=main_("""    string:s = string_concat("ab", "c");
    s.len = 1i64;
    exit 0i32;"""), wrong="accepted")


# ================================================================== §3 contracts
claim("vf0330", D, 330, "```nitpick", "example",
      "The example's divide (requires b != 0, ensures result > 0, passes 10) compiles, and divide(10, 2) "
      "returns 10.",
      expect="run:0", src=main_("""    int32:y = divide(raw v32(10i32), raw v32(2i32)) ?! E1;
    if (y != 10i32) { exit 10i32; }
    exit 0i32;""", "error:E1;\n" + DIVIDE), wrong="refused")

claim("vf0339", D, 339, "Nitpick automatically enforces these contracts at runtime", "rule",
      "Without the static verifier contracts are enforced at run time: divide(10, 0) traps RequiresViolated.",
      expect="trap:RequiresViolated", src=main_("""    int32:y = divide(raw v32(10i32), raw v32(0i32)) ?! E1;
    exit 10i32;""", "error:E1;\n" + DIVIDE),
      wrong="unchecked: exit 10; or a Result error (the E1 arm, 81)")

claim("vf0339b", D, 339, "the compiler translates these contracts into Z3 assertions", "rule",
      "With verification the contracts are translated into Z3 assertions and proven.",
      untestable="[z3] the verified build; `--verify-contracts` is struck (§5)")

claim("vf0342", D, 342, "Every proposition", "rule",
      "A requires clause must be a bool: an int32 clause is NITPICK-TYPE-007.",
      expect="refuse:TYPE-007", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) requires a + 1i32 { pass a; };"),
      wrong="accepted")

claim("vf0342b", D, 342, "`ensures`", "rule",
      "An ensures clause must be a bool: `ensures result` over an int32 is NITPICK-TYPE-007.",
      expect="refuse:TYPE-007", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) ensures result { pass a; };"),
      wrong="accepted")

claim("vf0342c", D, 342, "each `invariant` conjunct", "rule",
      "An invariant conjunct must be a bool: `invariant t` over an int32 is NITPICK-TYPE-007.",
      expect="refuse:TYPE-007", src=main_("""    exit 0i32;""", """func:f = int32(int32:n) never fails {
    int32:t = 0i32;
    while (t < n) decreases n - t invariant t { t = t + 1i32; }
    pass t;
};"""), wrong="accepted")

claim("vf0343", D, 343, "`prove`, `assert_static` — is a `bool`", "rule",
      "A prove proposition must be a bool: `prove(a)` over an int32 is NITPICK-TYPE-007.",
      expect="refuse:TYPE-007", src=main_("""    int32:a = raw v32(1i32);
    prove(a);
    exit 0i32;"""), wrong="accepted")

claim("vf0343b", D, 343, "`assert_static`", "rule",
      "An assert_static proposition must be a bool: `assert_static(1i32)` is NITPICK-TYPE-007.",
      expect="refuse:TYPE-007", src=main_("""    assert_static(1i32);
    exit 0i32;"""), wrong="accepted, or refused as not folding (TYPE-069)")

claim("vf0344", D, 344, "the SUCCESS value, typed `T`", "rule",
      "`result` is typed T: comparing an int32 function's result with an int64 is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) ensures result > 0i64 { pass a; };"),
      wrong="accepted")

claim("vf0345", D, 345, "`ensures` alone", "rule",
      "`result` is legal in ensures alone: in a requires it is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) requires result > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0344b", D, 344, "typed `T`, legal in", "rule",
      "`result` is legal in ensures alone: in a function body it is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) { pass result; };"),
      wrong="accepted")

claim("vf0345c", D, 345, "so no binding can shadow it", "rule",
      "`result` is a keyword: a local named result is refused.",
      expect="refuse", src=main_("""    int32:result = raw v32(5i32);
    exit 0i32;"""), wrong="accepted")

claim("vf0346", D, 346, "the operand's value at the function's ENTRY", "rule",
      "`old(n)` is n's value at the function's entry: after the body adds 5 to n, `result == old(n) + 1` "
      "holds of `n - 4`.",
      expect="run:0", src=main_("""    int32:r = bump(raw v32(10i32)) ?! E1;
    if (r != 11i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:bump = int32(int32:n) ensures result == old(n) + 1i32 {
    n = n + 5i32;
    pass (n - 4i32);
};"""), wrong="old(n) read at the seam (15): EnsuresViolated (116)")

claim("vf0346b", D, 346, "legal in `ensures`", "rule",
      "`old(...)` is legal in ensures and invariant only: in a requires it is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) requires old(a) > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0347", D, 347, "never nested", "rule",
      "`old` is never nested: `old(old(a))` is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) ensures old(old(a)) == a { pass a; };"),
      wrong="accepted")

claim("vf0348", D, 348, "`result`, and only of a COPYABLE value", "rule",
      "`old` is never of result: `old(result)` is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:a) ensures old(result) == a { pass a; };"),
      wrong="accepted")

claim("vf0348b", D, 348, "neither an owner (a `string`, a", "rule",
      "`old` is only of a copyable value: `old(s)` of a string (an owner) is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(string:s) ensures old(s).len > 0i64 { pass 1i32; };"),
      wrong="accepted")

claim("vf0349", D, 349, "nor an address (a pointer, a slice)", "rule",
      "`old` is only of a copyable value: `old(s)` of a slice (an address) is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int64(int32[]:s) ensures old(s).len == s.len { pass s.len; };"),
      wrong="accepted")

claim("vf0350", D, 350, "`main` and `failsafe` carry no contract (D-244)", "rule",
      "main carries no contract: a requires on main is refused.",
      expect="refuse", src="""func:main = int32(cstring[]:_~argv) requires 1i32 == 1i32 {
    exit 0i32;
};""", wrong="accepted")

claim("vf0350b", D, 350, "`failsafe` carry no contract", "rule",
      "failsafe carries no contract: an ensures on failsafe is refused.",
      expect="refuse", fs=False, src="""func:main = int32(cstring[]:_~argv) {
    exit 0i32;
};

func:failsafe = int32(Error:_~e) ensures result > 0i32 {
    exit 1i32;
};""", wrong="accepted")

claim("vf0351", D, 351, "fails` function may (D-241)", "rule",
      "A never fails function may carry contracts: one with a requires and an ensures compiles and runs.",
      expect="run:0", src=main_("""    int32:r = raw keep_pos(raw v32(3i32));
    if (r != 3i32) { exit 10i32; }
    exit 0i32;""", "func:keep_pos = int32(int32:a) never fails requires a > 0i32 ensures result > 0i32 { pass a; };"),
      wrong="refused",
      note="Contradicted by line 437, which says a function with a requires is never `never fails` (vf0437).")

claim("vf0354", D, 354, "no `await`", "rule",
      "A contract may not contain await: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", """async func:later = int32(int32:v) { pass v; };
async func:f = int32(int32:a) requires (await later(a)) > 0i32 { pass a; };"""), wrong="accepted")

claim("vf0355", D, 355, "`move`, no", "rule",
      "A contract may not contain move: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", "func:f = int32(string:s) requires (move(s)).len > 0i64 { pass 1i32; };"),
      wrong="accepted")

MAYFAIL = """error:E1;
func:mayfail = int32(int32:v) { if (v < 0i32) { fail E1; } pass v; };"""

claim("vf0355b", D, 355, "`relay`", "rule",
      "A contract may not contain relay: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", MAYFAIL + "\nfunc:f = int32(int32:a) requires (relay mayfail(a)) > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0355c", D, 355, "`?!`", "rule",
      "A contract may not contain `?!`: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", MAYFAIL + "\nfunc:f = int32(int32:a) requires (mayfail(a) ?! E1) > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0355d", D, 355, "`?|`", "rule",
      "A contract may not contain `?|`: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", MAYFAIL + "\nfunc:f = int32(int32:a) requires (mayfail(a) ?| 0i32) > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0355e", D, 355, "no `pick` expression", "rule",
      "A contract may not contain a pick expression: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""",
                                           "func:f = int32(int32:a) requires pick (a) { (0i32) { give true; }, (*) { give false; } } { pass a; };"),
      wrong="accepted")

claim("vf0358", D, 358, "a user function spelled `raw f(", "rule",
      "A contract may call a named pure never-fails user function spelled `raw f(...)`: accepted, and the "
      "call runs.",
      expect="run:0", src=main_("""    int32:r = apply(raw v32(3i32)) ?! E1;
    if (r != 9i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:sq = int32(int32:n) pure never fails { pass (n * n); };
func:apply = int32(int32:n) requires (raw sq(n)) < 100i32 { pass (raw sq(n)); };"""), wrong="refused")

claim("vf0359", D, 359, "that is **`pure`**", "rule",
      "A contract's callee must be pure: a never-fails function that is not pure is NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", """func:impure = int32(int32:v) never fails { pass v; };
func:f = int32(int32:a) requires (raw impure(a)) > 0i32 { pass a; };"""), wrong="accepted")

claim("vf0359b", D, 359, "a function value, a field", "rule",
      "A contract may not call a function value: NITPICK-TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""",
                                           "func:f = int32(func int32(int32) never fails:g, int32:a) requires (raw g(a)) > 0i32 { pass a; };"),
      wrong="accepted")

claim("vf0362", D, 362, "`is_err(x)` is a predicate and passes", "rule",
      "`is_err(x)` passes in a contract: a requires over `!(is_err(t))` compiles and a call with a non-ERR "
      "value runs.",
      expect="run:0", src=main_("""    int32:r = safe(raw vt8(5tbb8)) ?! E1;
    if (r != 1i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:safe = int32(tbb8:t) requires !(is_err(t)) { pass 1i32; };"""), wrong="refused")

claim("vf0365", D, 365, "a pure function may `fail`", "rule",
      "pure is orthogonal to never fails: a pure function may fail, and its failure reaches the caller.",
      expect="run:0", src=main_("""    int32:r = checked(raw v32(-1i32)) ?| 7i32;
    if (r != 7i32) { exit 10i32; }
    int32:s = checked(raw v32(3i32)) ?! E1;
    if (s != 6i32) { exit 11i32; }
    exit 0i32;""", """error:E1;
func:checked = int32(int32:a) pure { if (a < 0i32) { fail E1; } pass (a * 2i32); };"""), wrong="refused")

claim("vf0367", D, 367, "no `async`/`thread`", "rule",
      "A pure function may not be async: NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", "async func:p = int32(int32:a) pure { pass a; };"),
      wrong="accepted")

claim("vf0367b", D, 367, "no `move` parameter", "rule",
      "A pure function may not take a move parameter: NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", "func:p = int32(move string:s) pure { pass 1i32; };"),
      wrong="accepted")

claim("vf0367c", D, 367, "no callee", "rule",
      "A pure function may not call a function that is not pure: NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", """func:impure = int32(int32:v) never fails { pass v; };
func:p = int32(int32:a) pure { pass (raw impure(a)); };"""), wrong="accepted")

claim("vf0370", D, 370, "the clock", "rule",
      "A builtin that touches the clock is an effect: `mono_now()` in a pure function is NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", "func:p = int32(int32:a) pure { int64:t = mono_now(); pass a; };"),
      wrong="accepted")

claim("vf0372", D, 372, "no `wild`/`wildx` storage", "rule",
      "A pure function may not hold wild storage: NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", "func:p = int32(int32:a) pure { wild int8->:q = NULL; pass a; };"),
      wrong="accepted")

claim("vf0372b", D, 372, "no owning local", "rule",
      "A pure function may not have an owning local: a string local is NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", 'func:p = int32(int32:a) pure { string:s = "x"; pass a; };'),
      wrong="accepted")

claim("vf0373", D, 373, "store that reaches memory the caller can see", "rule",
      "A pure function may not store to memory the caller can see: a write through a pointer parameter is "
      "NITPICK-TYPE-061.",
      expect="refuse:TYPE-061", src=main_("""    exit 0i32;""", "func:p = int32(int32->:q) pure { <-q = 1i32; pass 1i32; };"),
      wrong="accepted")

claim("vf0374", D, 374, "impl keeps its trait method's `pure`", "rule",
      "An impl keeps its trait method's pure: an impl method dropping it is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", """trait:Shape = { func:area = int32(Self->:self) never fails pure; };
struct:Sq = { int32:side; };
impl:Sq:Shape = { func:area = int32(Sq->:self) never fails { pass self.side; }; };"""), wrong="accepted")

claim("vf0374b", D, 374, "Purity never rides a function type", "rule",
      "Purity never rides a function type: a pure function calling a never-fails function value is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:p = int32(func int32(int32) never fails:f, int32:a) pure { pass (raw f(a)); };"),
      wrong="accepted")

claim("vf0377", D, 377, "A contract violation is a TRAP", "rule",
      "A violated requires is a trap: RequiresViolated reaches failsafe.",
      expect="trap:RequiresViolated", src=main_("""    int32:r = half(raw v32(0i32)) ?! E1;
    exit 10i32;""", "error:E1;\n" + HALF), wrong="unchecked: exit 10; or a Result error (81)")

claim("vf0378", D, 378, "`EnsuresViolated`", "rule",
      "A violated ensures is a trap: EnsuresViolated reaches failsafe.",
      expect="trap:EnsuresViolated", src=main_("""    int32:r = neg(raw v32(3i32)) ?! E1;
    exit 10i32;""", """error:E1;
func:neg = int32(int32:a) ensures result > 0i32 { pass (0i32 - a); };"""), wrong="unchecked: exit 10")

claim("vf0378b", D, 378, "`InvariantViolated`", "rule",
      "A violated loop invariant is a trap: InvariantViolated reaches failsafe.",
      expect="trap:InvariantViolated", src=main_("""    int32:i = 0i32;
    int32:acc = raw v32(0i32);
    while (i < 5i32) decreases 5i32 - i invariant acc < 2i32 {
        acc = acc + 1i32;
        i = i + 1i32;
    }
    exit 10i32;"""), wrong="unchecked: exit 10")

claim("vf0380", D, 380, "A `requires` is checked at the CALLEE's", "rule",
      "A requires is checked at the callee's entry, every clause: with two requires clauses, violating the "
      "second traps RequiresViolated.",
      expect="trap:RequiresViolated", src=main_("""    int32:r = rng(raw v32(12i32)) ?! E1;
    exit 10i32;""", """error:E1;
func:rng = int32(int32:n) requires n > 0i32 requires n < 10i32 { pass n; };"""),
      wrong="only the first clause checked: exit 10")

claim("vf0381", D, 381, "`<symbol>.req`", "rule",
      "A requires is checked in a generated predicate <symbol>.req.",
      expect=r'ir:^define [^\n]*@"npk\.vf0381\.half\.req"\(', src=main_("""    int32:r = half(raw v32(4i32)) ?! E1;
    if (r != 2i32) { exit 10i32; }
    exit 0i32;""", "error:E1;\n" + HALF), wrong="no .req predicate: the check inlined or absent")

claim("vf0384", D, 384, "therefore splits into `<symbol>.body`", "rule",
      "A sync function with a requires splits into <symbol>.body and its ordinary symbol (the checked entry).",
      expect=r'ir:^define [^\n]*@"npk\.vf0384\.half\.body"\(', src=main_("""    int32:r = half(raw v32(4i32)) ?! E1;
    if (r != 2i32) { exit 10i32; }
    exit 0i32;""", "error:E1;\n" + HALF), wrong="one symbol only")

claim("vf0385", D, 385, "or at state 0 of a coroutine", "rule",
      "A coroutine's requires is checked at state 0: awaiting it with a violating argument traps "
      "RequiresViolated.",
      expect="trap:RequiresViolated", src="""error:E9;
async func:fetch = int32(int32:v) requires v > 0i32 { pass (v + 1i32); };

async func:main = int32(cstring[]:_~argv) {
    int32:b = (await fetch(raw v32(0i32))) ?! E9;
    exit 10i32;
};""", wrong="unchecked: exit 10")

claim("vf0387", D, 387, "indirect", "rule",
      "Every caller is covered, indirect too: calling a requires function through a function value with a "
      "violating argument traps RequiresViolated.",
      expect="trap:RequiresViolated", src=main_("""    func int32(int32):f = half;
    int32:b = f(raw v32(0i32)) ?! E1;
    exit 10i32;""", "error:E1;\n" + HALF), wrong="the function value bypasses the check: exit 10")

claim("vf0387b", D, 387, "through `dyn`", "rule",
      "Every caller is covered through dyn: a trait call with a violating argument traps RequiresViolated.",
      expect="trap:RequiresViolated", src=main_("""    Box:b = Box{ w: 3i32 };
    int32:r = through(b, raw v32(0i32)) ?! E9;
    exit 10i32;""", """error:E9;
trait:Sized = { func:size = int32(Self:self, int32:scale) requires scale > 0i32; };
struct:Box = { int32:w; };
impl:Box:Sized = {
    func:size = int32(Box:self, int32:scale) requires scale > 0i32 { pass (self.w * scale); };
};
func:through = int32(dyn Sized:s, int32:k) { pass ((s.size(k)) ?! E9); };"""), wrong="unchecked through dyn: exit 10")

claim("vf0388", D, 388, "every return seam", "rule",
      "An ensures is checked at every return seam: the second of two `pass` points violating it traps "
      "EnsuresViolated.",
      expect="trap:EnsuresViolated", src=main_("""    int32:r = sgn(raw v32(-3i32)) ?! E1;
    exit 10i32;""", """error:E1;
func:sgn = int32(int32:a) ensures result > 0i32 {
    if (a > 5i32) { pass 1i32; }
    pass a;
};"""), wrong="only one seam checked: exit 10")

claim("vf0388b", D, 388, "and `return Result{", "rule",
      "An ensures is checked at a `return Result{...}` whose error field is 0: a violating value traps "
      "EnsuresViolated.",
      expect="trap:EnsuresViolated", src=main_("""    int32:r = bumpr(raw v32(3i32)) ?! E1;
    exit 10i32;""", """error:E1;
func:bumpr = int32(int32:n) ensures result > 0i32 {
    int32:m = n - 10i32;
    return Result{ value: m };
};"""), wrong="the long-form return unchecked: exit 10")

claim("vf0389", D, 389, "is 0), before the value is stored", "rule",
      "An ensures is checked only on success (error field 0): a failing path is not checked, and the "
      "caller's `?|` default is taken.",
      expect="run:0", src=main_("""    int32:r = pos(raw v32(-1i32)) ?| 7i32;
    if (r != 7i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:pos = int32(int32:a) ensures result > 0i32 {
    if (a < 0i32) { fail E1; }
    pass 1i32;
};"""), wrong="the failure path checked: EnsuresViolated (116)")

claim("vf0390", D, 390, "`old(e)` a snapshot taken once at the body's start", "rule",
      "In a coroutine `old(v)` is a snapshot taken at the body's start: after the body adds 5, "
      "`result == old(v) + 1` holds of `v - 4`.",
      expect="run:0", src="""error:E1;
async func:grow = int32(int32:v) ensures result == old(v) + 1i32 {
    v = v + 5i32;
    pass (v - 4i32);
};

async func:main = int32(cstring[]:_~argv) {
    int32:r = (await grow(raw v32(10i32))) ?! E1;
    if (r != 11i32) { exit 10i32; }
    exit 0i32;
};""", wrong="old(v) read at the seam: EnsuresViolated (116)")

claim("vf0393", D, 393, "a literal that is not positive refused by the checker", "rule",
      "failsafe's postcondition: an `exit` with a literal that is not positive is refused, REACH-004.",
      expect="refuse:REACH-004", fs=False, src="""func:main = int32(cstring[]:_~argv) {
    exit 0i32;
};

func:failsafe = int32(Error:_~e) {
    exit 0i32;
};""", wrong="accepted (failsafe reporting success)")

claim("vf0395", D, 395, "re-enters it and ends the process at 70", "rule",
      "A computed non-positive failsafe exit is guarded: EnsuresViolated inside failsafe re-enters it and "
      "ends the process at 70.",
      expect="run:70", fs=False, src="""error:E9;
func:broken = int32() { fail E9; };

func:main = int32(cstring[]:_~argv) {
    int32:v = broken() ?! E9;
    exit (v + 1i32);
};

""" + failsafe_custom(pre="    int32:z = 0i32;\n", arms=("(E9) { exit z; },",)),
      wrong="exit 0 (the unchecked zero), or 116 (a second failsafe run taking the EnsuresViolated arm)")

REQ_ROWS_SRC = main_("""    int32:a = half(raw v32(4i32)) ?! E9;
    int32:b = half(raw v32(6i32)) ?! E9;
    if ((a + b) != 5i32) { exit 10i32; }
    exit 0i32;""", "error:E9;\n" + HALF)

claim("vf0397", D, 397, "One `requires` row per CALL with a recorded callee", "rule",
      "One requires row per call with a recorded callee and one per function entry: two direct calls of a "
      "requires function make three rows.",
      expect="sh:0", sh=obl_sh("vf0397", REQ_ROWS_SRC, """
[ "$(rows requires vf0397.)" -eq 3 ] || exit 1
exit 0"""), wrong="no call-site rows, or no entry row")

claim("vf0398", D, 398, "`bypass` at a direct sync", "rule",
      "A direct sync call's requires row has the role `bypass`.",
      expect="sh:0", sh=obl_sh("vf0398", REQ_ROWS_SRC, """
[ "$(field requires vf0398.main 8 | grep -cx bypass)" -eq 2 ] || exit 1
exit 0"""), wrong="another role at the call sites")

claim("vf0400", D, 400, "`held` at an `await` or through a `dyn`", "rule",
      "A requires row through dyn has the role `held`.",
      expect="sh:0", sh=obl_sh("vf0400", main_("""    Box:b = Box{ w: 3i32 };
    int32:r = through(b, raw v32(2i32)) ?! E9;
    if (r != 6i32) { exit 10i32; }
    exit 0i32;""", """error:E9;
trait:Sized = { func:size = int32(Self:self, int32:scale) requires scale > 0i32; };
struct:Box = { int32:w; };
impl:Box:Sized = {
    func:size = int32(Box:self, int32:scale) requires scale > 0i32 { pass (self.w * scale); };
};
func:through = int32(dyn Sized:s, int32:k) { pass ((s.size(k)) ?! E9); };"""), """
field requires vf0400.through 8 | grep -qx held || exit 1
exit 0"""), wrong="no row at the dyn call, or another role")

claim("vf0405", D, 405, "One `ensures` row per return point", "rule",
      "One ensures row per return point: a function with two `pass` points has two ensures rows.",
      expect="sh:0", sh=obl_sh("vf0405", main_("""    int32:r = choose(raw v32(3i32)) ?! E9;
    if (r != 2i32) { exit 10i32; }
    exit 0i32;""", """error:E9;
func:choose = int32(int32:a) ensures result >= 0i32 {
    if (a > 5i32) { pass 1i32; }
    pass 2i32;
};"""), """
[ "$(rows ensures vf0405.choose)" -eq 2 ] || exit 1
exit 0"""), wrong="one row per function")

claim("vf0407", D, 407, "A callee's `ensures` is KNOWLEDGE at every unwrap", "rule",
      "A callee's ensures is knowledge at every unwrap that continues only on success, never at `?|`.",
      untestable="[z3] knowledge shows only through z3's verdicts")

claim("vf0410", D, 410, "UNINTERPRETED FUNCTION", "rule",
      "A pure never-fails callee is an uninterpreted function in the obligations.",
      untestable="[z3] the encoding shows only through z3's verdicts")

claim("vf0413", D, 413, "CONFORMANCE is two rows per impl method", "rule",
      "Conformance is two rows per impl method whose trait method carries a contract (role `conform`, no guard).",
      expect="sh:0", sh=obl_sh("vf0413", main_("""    Wide:a = Wide{ w: 3i32 };
    int32:r = through(a) ?! E9;
    if (r != 4i32) { exit 10i32; }
    exit 0i32;""", """error:E9;
trait:Sized = { func:size = int32(Self:self, int32:scale) requires scale > 0i32 ensures result >= 0i32; };
struct:Wide = { int32:w; };
impl:Wide:Sized = {
    func:size = int32(Wide:_~self, int32:scale) requires scale > -1i32 ensures result >= 1i32 { pass 4i32; };
};
func:through = int32(dyn Sized:s) { pass ((s.size(1i32)) ?! E9); };"""), r"""
[ "$(awk -F'\t' '$8 == "conform" && index($6, "vf0413.") > 0' obl/rows.txt | wc -l)" -eq 2 ] || exit 1
exit 0"""), wrong="no conformance rows, or not two",
      note="The role word `conform` is §8's (line 1300); line 414 names the elision word `none`.")

claim("vf0417", D, 417, "never a refusal: the impl's own entry traps the argument the trait admits", "rule",
      "An impl that strengthens its trait's requires is not refused; through the trait, an argument the trait "
      "admits and the impl does not traps RequiresViolated at the impl's entry.",
      expect="trap:RequiresViolated", src=main_("""    Narrow:b = Narrow{ w: 3i32 };
    int32:v = through(b) ?! E9;
    exit 10i32;""", """error:E9;
trait:Sized = { func:size = int32(Self:self, int32:scale) requires scale > 0i32; };
struct:Narrow = { int32:w; };
impl:Narrow:Sized = {
    func:size = int32(Narrow:_~self, int32:scale) requires scale > 5i32 { pass 2i32; };
};
func:through = int32(dyn Sized:s) { pass ((s.size(1i32)) ?! E9); };"""),
      wrong="refused at compile time, or the impl's clause unchecked (exit 10)")

claim("vf0418", D, 418, "A guard inside a clause (a division in a `requires`)", "rule",
      "A guard inside a requires clause is the function's own site in the predicate: dividing by a zero "
      "argument there traps DivByZero.",
      expect="trap:DivByZero", src=main_("""    int32:r = ratio(raw v32(0i32)) ?! E1;
    exit 10i32;""", """error:E1;
func:ratio = int32(int32:b) requires (100i32 / b) > 1i32 { pass b; };"""),
      wrong="no guard in the clause: an undefined division, or RequiresViolated")

claim("vf0422", D, 422, "it has a row in every context the head's one check runs in", "rule",
      "A guard inside an invariant has a row per context of the head's check (entry, back edge, each "
      "continue): a division in an invariant of a loop with one continue has three div-zero rows.",
      expect="sh:0", sh=obl_sh("vf0422", main_("""    int32:d = raw v32(5i32);
    int32:i = 0i32;
    while (i < 3i32) decreases 3i32 - i invariant (100i32 / d) > 0i32 {
        i = i + 1i32;
        if (i == 1i32) { continue; }
    }
    exit 0i32;"""), """
[ "$(rows div-zero vf0422.main)" -eq 3 ] || exit 1
exit 0"""), wrong="one row for the clause")


# ================================================================== §3.1 the Result intercept (dead)
claim("vf0429", D, 429, "PROGRAM-INVALID state, not a value", "rule",
      "A contract violation is a trap, never a Result: a violated requires traps RequiresViolated even when "
      "the caller offers a `?|` default.",
      expect="trap:RequiresViolated", src=main_("""    int32:y = divide(raw v32(10i32), raw v32(0i32)) ?| 5i32;
    exit 10i32;""", DIVIDE), wrong="the Result intercept: the default taken, exit 10")

claim("vf0437", D, 437, "so it is never `never fails`", "rule",
      "A function with a requires is never `never fails`: declaring one is refused.",
      expect="refuse", src=main_("""    int32:r = raw keep_pos(raw v32(3i32));
    exit 0i32;""", "func:keep_pos = int32(int32:a) never fails requires a > 0i32 { pass a; };"),
      wrong="accepted",
      note="§3.1 is marked dead (428-433) but this parenthetical cites D-163 and reads as current; it "
           "contradicts line 351 (D-241: a never fails function may carry a contract, vf0351).")

claim("vf0437b", D, 437, "`raw` does not apply here", "rule",
      "`raw` does not apply to a call of a function with a requires (not never fails): it is refused.",
      expect="refuse", src=main_("""    int32:y = raw divide(raw v32(10i32), raw v32(2i32));
    exit 0i32;""", DIVIDE), wrong="accepted")

claim("vf0439", D, 439, "```nitpick", "example",
      "The example compiles and runs with §3's divide: `divide(10i32, 2i32) ?! 7tbb32` unwraps 10 and main "
      "exits 0.",
      expect="run:0", src=DIVIDE + """

func:main = int32(cstring[]:_~argv) {
    // Because `divide` has a `requires` contract, the call can fail, and
    // the failure is handled like any other -- here, trapped.
    int32:y = divide(10i32, 2i32) ?! 7tbb32;

    exit 0i32;
};""", wrong="refused (the `?! 7tbb32` spelling)",
      note="§3.1 is marked dead by D-221 (the paragraphs are the record of what was replaced); the "
           "example still stands in the text. It spells `func:main = int32()`; main's fixed signature is used.")


# ================================================================== §4 loop invariants
claim("vf0453", D, 453, "support an `invariant` clause", "rule",
      "A counted `loop` supports an invariant, checked: an accumulator leaving it traps InvariantViolated.",
      expect="trap:InvariantViolated", src=main_("""    int64:acc = raw v64(0i64);
    loop (0i64, 5i64, 1i64) invariant acc < 3i64 { acc = acc + 1i64; }
    exit 10i32;"""), wrong="unsupported (refused) or unchecked (exit 10)")

claim("vf0453b", D, 453, "`while`", "rule",
      "A `while` supports an invariant, checked: violating it traps InvariantViolated.",
      expect="trap:InvariantViolated", src=main_("""    int64:acc = raw v64(0i64);
    int64:i = 0i64;
    while (i < 5i64) decreases 5i64 - i invariant acc < 3i64 { acc = acc + 1i64; i = i + 1i64; }
    exit 10i32;"""), wrong="unsupported (refused) or unchecked (exit 10)")

claim("vf0453c", D, 453, "`till`", "rule",
      "A `till` supports an invariant, checked: violating it traps InvariantViolated.",
      expect="trap:InvariantViolated", src=main_("""    int64:acc = raw v64(0i64);
    till (5i64, 1i64) invariant acc < 3i64 { acc = acc + 1i64; }
    exit 10i32;"""), wrong="unsupported (refused) or unchecked (exit 10)")

claim("vf0453d", D, 453, "`when`", "rule",
      "A `when` supports an invariant, checked: violating it traps InvariantViolated.",
      expect="trap:InvariantViolated", src=main_("""    int32:w = raw v32(4i32);
    when (w > 0i32) decreases w invariant w != 2i32 { w = w - 1i32; } then { w = 0i32; } end { w = 0i32; }
    exit 10i32;"""), wrong="unsupported (refused) or unchecked (exit 10)")

claim("vf0453e", D, 453, "BEFORE the invariant", "rule",
      "A while/when states `decreases E` or `unbounded` before the invariant: the invariant first is refused.",
      expect="refuse", src=main_("""    int32:i = raw v32(0i32);
    when (i < 3i32) invariant i >= 0i32 unbounded { i = i + 1i32; }
    exit 0i32;"""), wrong="accepted")

claim("vf0455", D, 455, "```nitpick", "example",
      "The example sum_range (requires n > 0, ensures result >= 0, a while with decreases and a two-conjunct "
      "invariant) compiles, and sum_range(3) is 3.",
      expect="run:0", src=main_("""    int32:t = sum_range(raw v32(3i32)) ?! E1;
    if (t != 3i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:sum_range = int32(int32:n)
    requires n > 0i32
    ensures result >= 0i32
{
    int32:total = 0i32;
    int32:i = 0i32;
    while (i < n) decreases n - i invariant total >= 0i32, i >= 0i32 {
        total = total + 1i32;
        i = i + 1i32;
    }
    pass(total);
};"""), wrong="refused, or a wrong sum")

claim("vf0470", D, 470, "the Z3 solver verifies the inductive step", "rule",
      "The solver verifies the invariant's inductive step.",
      untestable="[z3] a verdict; `--verify-contracts` is struck (§5)")

claim("vf0473", D, 473, "a counted loop's invariant may name `$`", "rule",
      "A counted loop's invariant may name `$` (the counter): `invariant $ < 3` traps InvariantViolated when "
      "the counter reaches 3.",
      expect="trap:InvariantViolated", src=main_("""    int64:acc = raw v64(0i64);
    loop (0i64, 5i64, 1i64) invariant $ < 3i64 { acc = acc + 1i64; }
    exit 10i32;"""), wrong="`$` refused, or unchecked (exit 10)")

claim("vf0474", D, 474, "`old(expr)` — the value at the FUNCTION's entry", "rule",
      "An invariant's `old(n)` is n's value at the function's entry: with n lowered by 3 before the loop, "
      "`i <= old(n)` holds for i up to 4.",
      expect="run:0", src=main_("""    int32:r = raw walk(raw v32(5i32));
    if (r != 4i32) { exit 10i32; }
    exit 0i32;""", """func:walk = int32(int32:n) never fails {
    n = n - 3i32;
    int32:i = 0i32;
    while (i < 4i32) decreases 4i32 - i invariant i <= old(n) { i = i + 1i32; }
    pass i;
};"""), wrong="old(n) read at the loop (2): InvariantViolated (117)")

claim("vf0477", D, 477, "CHECKED AT THE LOOP HEAD, before", "rule",
      "The invariant is checked at the loop head before the condition: an invariant false at entry traps even "
      "when the condition is false and the body never runs.",
      expect="trap:InvariantViolated", src=main_("""    int32:i = raw v32(0i32);
    while (i < 0i32) decreases 0i32 - i invariant i > 5i32 { i = i + 1i32; }
    exit 10i32;"""), wrong="checked only inside the body: exit 10")

claim("vf0478", D, 478, "at entry and after every iteration", "rule",
      "The invariant is checked after every iteration, the last included (the exit is a head visit): an "
      "invariant only the final iteration breaks traps.",
      expect="trap:InvariantViolated", src=main_("""    int32:i = raw v32(0i32);
    while (i < 3i32) decreases 3i32 - i invariant i < 3i32 { i = i + 1i32; }
    exit 10i32;"""), wrong="not checked at the exiting head visit: exit 10")

claim("vf0479", D, 479, "for every loop form", "rule",
      "The invariant is checked for every loop form, a range for included: violating it traps "
      "InvariantViolated.",
      expect="trap:InvariantViolated", src=main_("""    int32:acc = raw v32(0i32);
    for (int32:k in 0i32...5i32) invariant acc < 3i32 { acc = acc + 1i32; }
    exit 10i32;"""), wrong="unchecked on a for: exit 10")

claim("vf0481", D, 481, "the ENTRY row at the loop statement", "rule",
      "An invariant's rows: the entry row, the preservation row and one per continue: a while with one "
      "continue has three invariant rows.",
      expect="sh:0", sh=obl_sh("vf0481", main_("""    int32:i = 0i32;
    int32:acc = 0i32;
    while (i < 5i32) decreases 5i32 - i invariant acc >= 0i32 {
        i = i + 1i32;
        if (i == 2i32) { continue; }
        acc = acc + 1i32;
    }
    if (acc != 4i32) { exit 10i32; }
    exit 0i32;"""), """
[ "$(rows invariant vf0481.main)" -eq 3 ] || exit 1
exit 0"""), wrong="the continue has no row, or one row per loop")

claim("vf0484", D, 484, "Inside the body the invariant and", "rule",
      "Inside the body the invariant and the condition are hypotheses; after a loop nothing breaks out of, "
      "the invariant and the negated condition.",
      untestable="[z3] hypotheses show only through z3's verdicts")

claim("vf0492", D, 492, "(descending, `limit < $ <= start`)", "rule",
      "A descending counted loop's `$` lies in limit < $ <= start: loop(5, 0, 1) visits 5, 4, 3, 2, 1.",
      expect="run:0", src=main_("""    int64:lo = 100i64;
    int64:hi = 0i64;
    int64:cnt = 0i64;
    loop (raw v64(5i64), 0i64, 1i64) {
        if ($ < lo) { lo = $; }
        if ($ > hi) { hi = $; }
        cnt = cnt + 1i64;
    }
    if (cnt != 5i64) { exit 10i32; }
    if (lo != 1i64) { exit 11i32; }
    if (hi != 5i64) { exit 12i32; }
    exit 0i32;"""), wrong="the limit visited (0) or the start skipped",
      note="The text states the solver's model of `$`; the run checks the emitted loop the model assumes.")

claim("vf0496", D, 496, "its bounds captured at entry", "rule",
      "A range for's bounds are captured at entry: raising the bound's variable inside the body does not "
      "add iterations.",
      expect="run:0", src=main_("""    int64:n = raw v64(3i64);
    int64:c = 0i64;
    for (int64:i in 0i64...n) {
        if (c < 2i64) { n = n + 1i64; }
        c = c + 1i64;
    }
    if (c != 3i64) { exit 10i32; }
    exit 0i32;"""), wrong="the bound re-read each trip: 5 iterations (exit 10)")

claim("vf0499", D, 499, "a name a bound mentions moves nothing", "rule",
      "A counted loop's bounds are captured as the emitter's slots hold them: a body assigning the bound's "
      "variable moves nothing.",
      expect="run:0", src=main_("""    int64:n = raw v64(3i64);
    int64:c = 0i64;
    loop (0i64, n, 1i64) {
        if (c < 2i64) { n = n + 1i64; }
        c = c + 1i64;
    }
    if (c != 3i64) { exit 10i32; }
    exit 0i32;"""), wrong="the bound re-read each trip: 5 iterations (exit 10)")

claim("vf0500", D, 500, "the compare at the loop's entry is its guard", "rule",
      "A computed step's positivity is guarded at the loop's entry: a zero step at run time traps BadStep.",
      expect="trap:BadStep", src=main_("""    int64:s = raw v64(0i64);
    int64:acc = 0i64;
    loop (0i64, 5i64, s) { acc = acc + 1i64; }
    exit 10i32;"""), wrong="no guard: an endless loop, or exit 10")

claim("vf0500b", D, 500, "`loop-step` row (S-46, D-270)", "rule",
      "A computed step is one `loop-step` row; a literal step has none.",
      expect="sh:0", sh=obl_sh("vf0500b", main_("""    int64:s = raw v64(1i64);
    int64:acc = 0i64;
    loop (0i64, 5i64, s) { acc = acc + 1i64; }
    loop (0i64, 5i64, 1i64) { acc = acc + 1i64; }
    if (acc != 10i64) { exit 10i32; }
    exit 0i32;"""), """
[ "$(rows loop-step vf0500b.main)" -eq 1 ] || exit 1
exit 0"""), wrong="no row, or a row for the literal step too")

claim("vf0501", D, 501, "a literal step is the checker's (TYPE-068, D-022)", "rule",
      "A literal step that is not positive is the checker's: a zero literal step is TYPE-068.",
      expect="refuse:TYPE-068", src=main_("""    int64:acc = 0i64;
    loop (0i64, 5i64, 0i64) { acc = acc + 1i64; }
    exit 0i32;"""), wrong="accepted (BadStep at run time)")

claim("vf0502", D, 502, "An invariant naming `$` or the binding is decided on the", "rule",
      "An invariant naming `$` or the for binding is decided on the merits.",
      untestable="[z3] a verdict")


# ================================================================== §4b termination
claim("vf0509", D, 509, "```nitpick", "example",
      "Both shapes compile and run: a while with `decreases n - i` then its invariant, and `while (true) "
      "unbounded` (left here by break).",
      expect="run:0", src=main_("""    int32:n = raw v32(4i32);
    int32:i = 0i32;
    int32:total = 0i32;
    while (i < n) decreases n - i invariant total >= 0i32 { total = total + 1i32; i = i + 1i32; }
    int32:spins = 0i32;
    while (true) unbounded { spins = spins + 1i32; if (spins == 3i32) { break; } }
    if (total != 4i32) { exit 10i32; }
    if (spins != 3i32) { exit 11i32; }
    exit 0i32;"""), wrong="refused", note="The example's bodies are `…`; they are filled in.")

claim("vf0514", D, 514, "is a plain integer (`intN`/`uintN`, TYPE-073)", "rule",
      "A loop measure is a plain integer: a flt64 measure is TYPE-073.",
      expect="refuse:TYPE-073", src=main_("""    exit 0i32;""", """func:f = flt64(flt64:f0) never fails {
    flt64:f = f0;
    while (f > 0.0f64) decreases f { f = f - 1.0f64; }
    pass f;
};"""), wrong="accepted")

claim("vf0514b", D, 514, "TYPE-073", "rule",
      "A loop measure is a plain integer: a bool measure is TYPE-073.",
      expect="refuse:TYPE-073", src=main_("""    exit 0i32;""", """func:f = int32() never fails {
    bool:go = true;
    int32:i = 0i32;
    while (go) decreases go { go = false; i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0515", D, 515, "a contract expression (§3's admission, TYPE-060)", "rule",
      "A measure is a contract expression: calling a never-fails function that is not pure in it is TYPE-060.",
      expect="refuse:TYPE-060", src=main_("""    exit 0i32;""", """func:left = int32(int32:n, int32:i) never fails { pass (n - i); };
func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases raw left(n, i) { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0516", D, 516, "neither `result` nor `old(", "rule",
      "`old(...)` does not exist in a measure: refused.",
      expect="refuse", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases old(n) - i { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0516b", D, 516, "`result`", "rule",
      "`result` does not exist in a measure: refused.",
      expect="refuse", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases result - i { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0517", D, 517, "BEFORE `invariant`, once", "rule",
      "The clause comes before invariant: `invariant ... decreases ...` is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) invariant i >= 0i32 decreases n - i { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0517b", D, 517, "once", "rule",
      "The clause comes once: two `decreases` are TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases n - i decreases n { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0517c", D, 517, "`unbounded` and `decreases` never both", "rule",
      "`unbounded` and `decreases` never both: TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases n - i unbounded { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0519", D, 519, "each of those shapes is TYPE-072 by name", "rule",
      "A `for` takes neither clause: `for ... decreases` is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32(int32:n) never fails {
    int32:i = 0i32;
    for (int32:k in 0i32...n) decreases n { i = i + k; }
    pass i;
};"""), wrong="accepted")

claim("vf0519b", D, 519, "TYPE-072", "rule",
      "A `loop` takes neither clause: `loop ... unbounded` is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32() never fails {
    int32:i = 0i32;
    loop (0i64, 5i64, 1i64) unbounded { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0519c", D, 519, "by name", "rule",
      "A `till` takes neither clause: `till ... decreases` is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    exit 0i32;""", """func:g = int32() never fails {
    int32:i = 0i32;
    till (5i64, 1i64) decreases 5i64 { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0520", D, 520, "`while`/`when` with NO clause", "rule",
      "A while with no clause is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    int32:i = raw v32(0i32);
    while (i < 3i32) { i = i + 1i32; }
    exit 0i32;"""), wrong="accepted")

claim("vf0520b", D, 520, "NO clause", "rule",
      "A when with no clause is TYPE-072.",
      expect="refuse:TYPE-072", src=main_("""    int32:i = raw v32(3i32);
    when (i > 0i32) { i = i - 1i32; } then { i = 0i32; } end { i = 0i32; }
    exit 0i32;"""), wrong="accepted")

claim("vf0522", D, 522, "at the top of the body, each time the", "rule",
      "The measure is checked at the top of the body each time the condition holds: a negative measure of a "
      "loop whose condition is false at entry is never checked.",
      expect="run:0", src=main_("""    int32:k = raw v32(-5i32);
    int32:i = raw v32(0i32);
    while (i < 0i32) decreases k { i = i + 1i32; k = k - 1i32; }
    exit 0i32;"""), wrong="checked at the head before the condition: DecreasesViolated (109)")

claim("vf0524", D, 524, "zero traps `DecreasesViolated` (4119)", "rule",
      "A signed measure below zero traps DecreasesViolated at the first visit.",
      expect="trap:DecreasesViolated", src=main_("""    int32:k = raw v32(-1i32);
    int32:i = 0i32;
    while (i < 3i32) decreases k { i = i + 1i32; k = k - 1i32; }
    exit 10i32;"""), wrong="only the decrease checked: exit 10",
      note="The text gives DecreasesViolated's code as 4119 where the other identities it names are negative "
           "(-4111 ... -4116).")

claim("vf0525", D, 525, "not below the previous visit's traps the same", "rule",
      "From the second visit on, a measure not below the previous visit's traps DecreasesViolated.",
      expect="trap:DecreasesViolated", src=main_("""    int32:k = raw v32(5i32);
    int32:i = 0i32;
    while (i < 3i32) decreases k { i = i + 1i32; }
    exit 10i32;"""), wrong="unchecked: exit 10")

claim("vf0526", D, 526, "sentinel (DEF-69)", "rule",
      "Two slots per loop, never a sentinel: an unsigned measure starting at UINT32_MAX is not mistaken for "
      "the previous visit's.",
      expect="run:0", src=main_("""    uint32:u = raw vu32(4294967295u32);
    int32:c = 0i32;
    while (u > 4294967290u32) decreases u { u = u - 1u32; c = c + 1i32; }
    if (c != 5i32) { exit 10i32; }
    exit 0i32;"""), wrong="a UINT_MAX sentinel: DecreasesViolated at the first visit (109)")

claim("vf0525b", D, 525, "never a", "rule",
      "Never a sentinel: a signed measure starting at INT32_MAX is not mistaken for the previous visit's.",
      expect="run:0", src=main_("""    int32:k = raw v32(2147483647i32);
    int32:c = 0i32;
    while (k > 2147483642i32) decreases k { k = k - 1i32; c = c + 1i32; }
    if (c != 5i32) { exit 10i32; }
    exit 0i32;"""), wrong="an INT_MAX sentinel: DecreasesViolated at the first visit (109)")

claim("vf0527", D, 527, "frame slots at roles 42 and 43", "rule",
      "The previous measure and the first-visit flag are allocas in a sync body and frame slots 42 and 43 in "
      "a coroutine.",
      untestable="[internal] the slots' placement; their behaviour is vf0525/vf0526")

claim("vf0528", D, 528, "`continue` re-enters the", "rule",
      "`continue` re-enters the head and is checked: a continue that leaves the measure unchanged traps "
      "DecreasesViolated at the next visit.",
      expect="trap:DecreasesViolated", src=main_("""    int32:k = raw v32(5i32);
    int32:i = 0i32;
    while (i < 4i32) decreases k {
        i = i + 1i32;
        if (i == 2i32) { continue; }
        k = k - 1i32;
    }
    exit 10i32;"""), wrong="the continue's visit unchecked: exit 10")

claim("vf0529", D, 529, "`break` and `exit` leave without one", "rule",
      "`break` leaves without a check: a body that grows the measure and breaks runs clean.",
      expect="run:0", src=main_("""    int32:k = raw v32(3i32);
    int32:n = 0i32;
    while (k > 0i32) decreases k { k = k + 1i32; n = n + 1i32; break; }
    if (n != 1i32) { exit 10i32; }
    exit 0i32;"""), wrong="a check at the exit: DecreasesViolated (109)")

claim("vf0530", D, 530, "emits nothing.", "rule",
      "`unbounded` emits nothing.",
      untestable="[unobservable] an unbounded loop has no measure to check and no clause-less twin to compare "
                 "against (a while with no clause is TYPE-072)")

claim("vf0531", D, 531, "the ENTRY row at the loop statement, `E >= 0`", "rule",
      "terminate rows: an entry row (signed measures only), a preservation row, and one per continue: a signed "
      "loop has two, an unsigned one one, a signed one with a continue three.",
      expect="sh:0", sh=obl_sh("vf0531", main_("""    int32:a = raw up(raw v32(3i32));
    uint32:b = raw down(raw vu32(3u32));
    int32:c = raw skip(raw v32(4i32));
    if (a != 3i32) { exit 10i32; }
    if (b != 0u32) { exit 11i32; }
    if (c != 2i32) { exit 12i32; }
    exit 0i32;""", """func:up = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases n - i { i = i + 1i32; }
    pass i;
};
func:down = uint32(uint32:u0) never fails {
    uint32:u = u0;
    while (u > 0u32) decreases u { u = u - 1u32; }
    pass u;
};
func:skip = int32(int32:n) never fails {
    int32:i = 0i32;
    int32:odd = 0i32;
    while (i < n) decreases n - i {
        i = i + 1i32;
        if ((i % 2i32) == 1i32) { odd = odd + 1i32; continue; }
    }
    pass odd;
};"""), """
[ "$(rows terminate vf0531.up)" -eq 2 ] || exit 1
[ "$(rows terminate vf0531.down)" -eq 1 ] || exit 1
[ "$(rows terminate vf0531.skip)" -eq 3 ] || exit 1
exit 0"""), wrong="an entry row for the unsigned measure, or no row for the continue")

claim("vf0537", D, 537, "compares become one `llvm.assume` each only when EVERY row is discharged", "rule",
      "The check's compares become assumes only when every terminate row is discharged.",
      untestable="[z3] needs a manifest with the rows discharged")

claim("vf0545", D, 545, "What discharges", "rule",
      "A counter's `bound - v` and a halving n under n > 0 discharge.",
      untestable="[z3] verdicts")

claim("vf0548", D, 548, "`List`'s `count` as the bound has no length term", "rule",
      "A List's count as a loop's bound has no length term: the terminate rows are unencoded (0 in rows.txt).",
      expect="sh:0", sh=obl_sh("vf0548", main_("""    List<int32>:l = raw list_init::<int32>(4i64);
    drop list_push(@l, 5i32);
    drop list_push(@l, 6i32);
    int64:i = 0i64;
    while (i < l.count) decreases l.count - i { i = i + 1i64; }
    if (i != 2i64) { exit 10i32; }
    exit 0i32;"""), """
[ "$(rows terminate vf0548.main)" -ge 1 ] || exit 1
[ "$(field terminate vf0548.main 5 | sort -u)" = "0" ] || exit 1
exit 0"""), wrong="the rows encoded (1)",
      note="Contradicted in the same range: lines 648-649 count 73 discharged rows 'of a List's count read "
           "off a local against a counter', and §7b's note gives `.count` a length term (|npk.len|).")

claim("vf0551", D, 551, "function's `decreases E` is a contract of kind `decreases`", "rule",
      "A function's decreases is a contract checked at recursive calls: fact(5) with `decreases n` runs and "
      "returns 120.",
      expect="run:0", src=main_("""    int32:f = raw fact(raw v32(5i32));
    if (f != 120i32) { exit 10i32; }
    exit 0i32;""", FACT), wrong="refused, or a trap on a decreasing recursion")

claim("vf0552", D, 552, "optional (D-304 (5))", "rule",
      "A function's measure is optional: a self-recursion without one compiles and runs.",
      expect="run:0", src=main_("""    int32:d = raw depth(raw v32(10i32));
    if (d != 10i32) { exit 10i32; }
    exit 0i32;""", """func:depth = int32(int32:n) never fails {
    if (n <= 0i32) { pass 0i32; }
    pass (1i32 + (raw depth(n - 1i32)));
};"""), wrong="refused")

claim("vf0552b", D, 552, "and checked at every call inside the", "rule",
      "The measure is checked at every call inside the recursive group: is_even(n) calling is_odd(n) (no "
      "decrease across the pair) traps DecreasesViolated.",
      expect="trap:DecreasesViolated", src=main_("""    bool:b = raw is_even(raw v32(4i32));
    exit 10i32;""", """func:is_even = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass true; }
    pass (raw is_odd(n));
};
func:is_odd = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass false; }
    pass (raw is_even(n - 1i32));
};"""), wrong="only self-calls checked: exit 10")

claim("vf0554", D, 554, "Tarjan's components", "rule",
      "The recursive groups are Tarjan's components over the checker's call edges, one predicate for emitter "
      "and encoder.",
      untestable="[internal] the pass's algorithm; its outcomes are vf0552b/vf0557/vf0562/vf0564")

claim("vf0557", D, 557, "a call through a `dyn` receiver or a function value is", "rule",
      "A call through a function value is no edge: a function whose only recursion is through a function value "
      "has no cycle, so its decreases is TYPE-075.",
      expect="refuse:TYPE-075", src=main_("""    exit 0i32;""", """func:viaval = int32(func int32(int32):f, int32:n) decreases n {
    if (n <= 0i32) { pass 0i32; }
    pass (f(n - 1i32) ?| 0i32);
};"""), wrong="accepted")

claim("vf0562", D, 562, "TYPE-074: every function of a cyclic", "rule",
      "Every function of a cyclic group states decreases if any member does: a pair with one measured member "
      "is TYPE-074.",
      expect="refuse:TYPE-074", src=main_("""    int32:v = f(raw v32(3i32)) ?| 0i32;
    exit 0i32;""", """func:f = int32(int32:n) decreases n {
    if (n <= 0i32) { pass 0i32; }
    pass (g(n - 1i32) ?| 0i32);
};
func:g = int32(int32:n) {
    if (n <= 0i32) { pass 0i32; }
    pass (f(n - 1i32) ?| 0i32);
};"""), wrong="accepted")

claim("vf0564", D, 564, "TYPE-075: a `decreases` on a function whose group has no cycle checks", "rule",
      "A decreases on a function whose group has no cycle is TYPE-075.",
      expect="refuse:TYPE-075", src=main_("""    exit (raw lone(raw v32(3i32)));""", """func:lone = int32(int32:n) decreases n never fails {
    pass (n + 1i32);
};"""), wrong="accepted")

claim("vf0565", D, 565, "TYPE-073, for functions: the measure is at most 64 bits wide", "rule",
      "A function's measure is at most 64 bits wide: an int128 measure is TYPE-073.",
      expect="refuse:TYPE-073", src=main_("""    int32:r = raw wide(raw vi128(3i128));
    exit 0i32;""", """func:wide = int32(int128:n) decreases n never fails {
    if (n <= 0i128) { pass 0i32; }
    pass (raw wide(n - 1i128));
};"""), wrong="accepted")

claim("vf0568", D, 568, "compares only with itself and keeps any width", "rule",
      "A loop's measure keeps any width: an int128 loop measure is accepted and checked.",
      expect="run:0", src=main_("""    int128:n = raw vi128(3i128);
    int32:c = 0i32;
    while (n > 0i128) decreases n { n = n - 1i128; c = c + 1i32; }
    if (c != 3i32) { exit 10i32; }
    exit 0i32;"""), wrong="refused as TYPE-073")

claim("vf0569", D, 569, "a generated predicate `<sym>.measure(params)", "rule",
      "The check is a generated predicate <sym>.measure(params) returning i128.",
      expect=r'ir:^define [^\n]*\bi128 @"npk\.vf0569\.fact\.measure"\(', src=main_("""    int32:f = raw fact(raw v32(5i32));
    if (f != 120i32) { exit 10i32; }
    exit 0i32;""", FACT), wrong="no .measure predicate, or another return type")

claim("vf0572", D, 572, "the body's ENTRY stores", "rule",
      "The body's entry stores m0 after the entry checks and before the old snapshots.",
      untestable="[internal] an ordering inside the emitted entry that no program here can isolate")

claim("vf0577", D, 577, "then `m0 >= 0`", "rule",
      "At a recursive call `m0 >= 0` is checked: step(-1), whose measure is negative at entry, traps "
      "DecreasesViolated at its recursive call.",
      expect="trap:DecreasesViolated", src=main_("""    int32:r = raw step(raw v32(-1i32));
    exit 10i32;""", """func:step = int32(int32:n) decreases n never fails {
    if (n == 0i32) { pass 0i32; }
    pass (1i32 + (raw step(n - 1i32)));
};"""), wrong="only m1 < m0 checked: the recursion runs down (StackExhausted 106, or exit 10)")

claim("vf0578", D, 578, "and `m1 < m0` as one verdict with ONE trap `DecreasesViolated`", "rule",
      "At a recursive call `m1 < m0` is checked: a self-call with an unchanged argument traps "
      "DecreasesViolated.",
      expect="trap:DecreasesViolated", src=main_("""    int32:r = raw loopy(raw v32(3i32));
    exit 10i32;""", """func:loopy = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 0i32; }
    pass (raw loopy(n));
};"""), wrong="unchecked: endless recursion (StackExhausted 106)")

claim("vf0579", D, 579, "predicate holds no snapshot", "rule",
      "A recursive call inside a requires clause or a measure is not checked.",
      untestable="[internal] a recursive call inside a generated predicate recurses through the predicate "
                 "itself; no program here isolates the missing check from that recursion")

claim("vf0580", D, 580, "`unbounded` is a", "rule",
      "`unbounded` is a loop's word only: on a function it is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", "func:f = int32(int32:n) unbounded never fails { pass n; };"),
      wrong="accepted")

claim("vf0582", D, 582, "the `terminate` CALL row", "rule",
      "A recursive call is one terminate row of the caller's, role `guard`.",
      expect="sh:0", sh=obl_sh("vf0582", main_("""    int32:f = raw fact(raw v32(5i32));
    if (f != 120i32) { exit 10i32; }
    exit 0i32;""", FACT), """
[ "$(rows terminate vf0582.fact)" -eq 1 ] || exit 1
[ "$(field terminate vf0582.fact 8)" = "guard" ] || exit 1
exit 0"""), wrong="no call row, or another role")

claim("vf0588", D, 588, "The measure's own guards (an overflow inside `E`) have ONE row each", "rule",
      "The measure's own guards have one row each at the function's entry, under the parameters' range "
      "axioms alone.",
      untestable="[z3] which hypotheses a row carries shows only through verdicts")

claim("vf0595", D, 595, "row (D-305", "rule",
      "One stack-depth row per cyclic group, `d` (derived) in rows.txt: a self-recursion and a mutual pair "
      "make two.",
      expect="sh:0", sh=obl_sh("vf0595", main_("""    int32:f = raw fact(raw v32(4i32));
    bool:e = raw is_even(raw v32(4i32));
    if (f != 24i32) { exit 10i32; }
    if (!e) { exit 11i32; }
    exit 0i32;""", FACT + """
func:is_even = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass true; }
    pass (raw is_odd(n - 1i32));
};
func:is_odd = bool(int32:n) decreases n never fails {
    if (n <= 0i32) { pass false; }
    pass (raw is_even(n - 1i32));
};"""), """
[ "$(rows stack-depth vf0595.)" -eq 2 ] || exit 1
[ "$(field stack-depth vf0595. 5 | sort -u)" = "d" ] || exit 1
exit 0"""), wrong="one row per function, or a row with a query")

claim("vf0598", D, 598, "its verdict is DERIVED by both runners", "rule",
      "The stack-depth verdict is derived by the runners from the group's terminate call rows.",
      untestable="[z3] the runners' derivation needs z3's verdicts")

claim("vf0605", D, 605, "It elides nothing", "rule",
      "The stack-depth row elides nothing: the stack check stays in every build.",
      untestable="[z3] a statement about the verified build's elision")

claim("vf0606", D, 606, "the compiler's own groups state no measure", "rule",
      "The compiler's own recursive groups state no measure, so their rows are open.",
      untestable="[tree] about the compiler's own source")

claim("vf0607", D, 607, "`index.txt` carries per file the function's cyclic group", "rule",
      "index.txt carries per file the function's cyclic group (0 for none) and whether it states a measure.",
      expect="sh:0", sh=obl_sh("vf0607", main_("""    int32:f = raw fact(raw v32(4i32));
    int32:q = raw quot(raw v32(10i32), raw v32(2i32));
    if ((f + q) != 29i32) { exit 10i32; }
    exit 0i32;""", FACT + """
func:quot = int32(int32:a, int32:b) never fails { pass (a / b); };"""), r"""
awk -F'\t' 'index($2, "vf0607.fact") > 0 { n++; if ($4 == "0" || $5 != "1") bad = 1 } END { exit (n > 0 && !bad) ? 0 : 1 }' obl/index.txt || exit 1
awk -F'\t' 'index($2, "vf0607.quot") > 0 { n++; if ($4 != "0" || $5 != "0") bad = 1 } END { exit (n > 0 && !bad) ? 0 : 1 }' obl/index.txt || exit 1
exit 0"""), wrong="no group or measure columns, or wrong values")

claim("vf0610", D, 610, "`fact(n) decreases n` calling `fact(n - 1)`", "rule",
      "fact's call row discharges on the path condition; step under n != 0 leaves m0 >= 0 open.",
      untestable="[z3] verdicts")

claim("vf0614", D, 614, "every `while` and `when` of the", "rule",
      "Every while and when of the compiler's tree (977 loops) states its clause.",
      untestable="[tree] about the compiler's own tree")

claim("vf0618", D, 618, "PROVE monotone (392)", "rule",
      "The sweep tool wrote 392 loops' measures; the others were read into decreases_read.txt.",
      untestable="[tree] about the compiler's own tree and tools")

claim("vf0634", D, 634, "call a `pure never fails` function (TYPE-060)", "rule",
      "A measure may call a pure never-fails function: accepted, and the loop runs.",
      expect="run:0", src=main_("""    int32:n = raw v32(4i32);
    int32:i = 0i32;
    while (i < n) decreases raw left(n, i) { i = i + 1i32; }
    if (i != 4i32) { exit 10i32; }
    exit 0i32;""", "func:left = int32(int32:n, int32:i) pure never fails { pass (n - i); };"),
      wrong="refused (TYPE-060)")

claim("vf0638", D, 638, "a measure that does not shrink", "rule",
      "The compile-time evaluator checks a measure of a loop it runs: one that does not shrink is a "
      "counterexample, TYPE-069.",
      expect="refuse:TYPE-069", src=main_("""    int32:a = comptime(climb(3i32));
    exit 0i32;""", """comptime func:climb = int32(int32:n) {
    int32:i = 0i32;
    while (i > (0i32 - 4i32)) decreases n - i { i = i - 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0638b", D, 638, "or a signed one below zero", "rule",
      "The compile-time evaluator refuses a signed measure below zero, TYPE-069.",
      expect="refuse:TYPE-069", src=main_("""    int32:a = comptime(neg_measure(3i32));
    exit 0i32;""", """comptime func:neg_measure = int32(int32:n) {
    int32:i = 0i32;
    while (i < 3i32) decreases n - 10i32 - i { i = i + 1i32; }
    pass i;
};"""), wrong="accepted")

claim("vf0639", D, 639, "Every `failsafe` in the tree", "rule",
      "Every failsafe in the compiler's tree names DecreasesViolated.",
      untestable="[tree] about the compiler's own tree")

claim("vf0644", D, 644, "1,183 `terminate` row sites in the compiler's own build", "rule",
      "The measurement over the compiler's own build: 1,183 terminate row sites, 684 discharged, 499 open.",
      untestable="[tree] a measurement of the compiler's own build")

claim("vf0667", D, 667, "116, all `open`", "rule",
      "The compiler's stack-depth rows: 116, all open.",
      untestable="[tree] a measurement of the compiler's own build")

claim("vf0674", D, 674, "the by-value aggregate carries", "rule",
      "Since D-317 a by-value aggregate carries an identity and its fields are functions of it.",
      untestable="[z3] the encoder's aggregate terms show only through verdicts",
      note="Bears on vf0151: line 151 still calls a struct subject outside the fragment.")

claim("vf0676", D, 676, "1,188 `terminate` row sites, 753 discharged, 435 open", "rule",
      "After D-317: 1,188 terminate row sites, 753 discharged, 435 open.",
      untestable="[tree] a measurement of the compiler's own build")


# ================================================================== §5 flags (struck) and levels
claim("vf0695", D, 695, "None of the flags below exists in `npkc`", "rule",
      "None of the tabulated verification flags exists in npkc: each is refused.",
      expect="sh:0", sh=flag_sh("vf0695", ["--verify", "--verify-contracts", "--verify-overflow",
                                          "--verify-concurrency", "--verify-memory", "--verify-level=1",
                                          "--smt-opt", "--smt-manifest=nitpick.obligations",
                                          "--smt-timeout=5000", "--prove-report", "--debug-z3"]),
      wrong="a struck flag accepted (silently ignored)")

claim("vf0696", D, 696, "PROJECT's, in `nitpick.toml`'s `[verify]`", "rule",
      "Verification configuration is the project's, in nitpick.toml's [verify], read by every invocation.",
      untestable="[tool] needs a package tree and `npkg verify`")

claim("vf0702", D, 702, "a knob that would re-enable it is refused", "rule",
      "The wall-clock timeout is disabled; a [verify] knob that would re-enable it is refused by name.",
      untestable="[tool] a package tree under `npkg`; the knob's name is not given")

claim("vf0706", D, 706, "`--prove-report` and `--debug-z3` are `npkg verify --explain`", "rule",
      "The report and the SMT dump are `npkg verify --explain` and build/verify/obl/.",
      untestable="[z3] needs `npkg verify` with the pinned z3")

FLAG_ROWS = [
    (714, "`--verify`", "--verify"),
    (715, "`--verify-contracts`", "--verify-contracts"),
    (716, "`--verify-overflow`", "--verify-overflow"),
    (717, "`--verify-concurrency`", "--verify-concurrency"),
    (718, "`--verify-memory`", "--verify-memory"),
    (719, "`--verify-level=N`", "--verify-level=2"),
    (720, "`--smt-opt`", "--smt-opt"),
    (721, "`--smt-manifest=<path>`", "--smt-manifest=nitpick.obligations"),
    (722, "`--smt-timeout=N`", "--smt-timeout=5000"),
    (723, "`--prove-report`", "--prove-report"),
    (724, "`--debug-z3`", "--debug-z3"),
]
for _line, _q, _flag in FLAG_ROWS:
    claim("vf%04d" % _line, D, _line, _q, "row",
          "The flag %s is struck (the banner at 694-710): npkc does not accept it." % _flag,
          expect="sh:0", sh=flag_sh("vf%04d" % _line, [_flag]),
          wrong="accepted (a verification flag that silently does nothing)")

for _line, _level in ((732, 0), (733, 1), (734, 2), (735, 3)):
    claim("vf%04d" % _line, D, _line, "| `%d` |" % _level, "row",
          "Verification level %d is struck with `--verify-level` (694-710): npkc does not accept "
          "`--verify-level=%d`." % (_level, _level),
          expect="sh:0", sh=flag_sh("vf%04d" % _line, ["--verify-level=%d" % _level]),
          wrong="accepted")


# ================================================================== §6 backends
claim("vf0746", D, 746, "Invoked during compilation (`npkc --verify`)", "rule",
      "Z3 is invoked during compilation by `npkc --verify`.",
      untestable="[z3] needs z3; and §5 (694-710) says the flag does not exist in npkc",
      note="Contradicts the §5 banner: verification is `npkg verify`'s, never a compiler flag.")

claim("vf0749", D, 749, "Covers: `limit<Rules>` constraints, function contracts, loop invariants,", "rule",
      "The obligations cover limit, contracts, invariants, prove/assert_static, overflow and index "
      "disjointness: one program using each yields a row of each kind.",
      expect="sh:0", sh=obl_sh("vf0749", main_("""    limit<r_positive> int32:x = raw v32(3i32);
    int32:h = half(x) ?! E9;
    int32:i = 0i32;
    int32:acc = 0i32;
    while (i < 3i32) decreases 3i32 - i invariant acc >= 0i32 { acc = acc + x; i = i + 1i32; }
    prove(acc >= 0i32);
    assert_static(1i32 < 2i32);
    %s
    int32:u = raw update(raw v32(1i32), raw v32(2i32), arr);
    if ((h + acc + u) != 26i32) { exit 10i32; }
    exit 0i32;""" % ARR8, """error:E9;
Rules<int32>:r_positive = { $ > 0i32 };
func:half = int32(int32:n) requires n > 0i32 ensures result >= 0i32 { pass (n / 2i32); };
""" + UPDATE_PLAIN), """
for k in limit requires ensures invariant prove assert-static overflow disjoint; do
  [ "$(rows $k vf0749.)" -ge 1 ] || exit 1
done
exit 0"""), wrong="a construct with no row of its kind")

claim("vf0750", D, 750, "memory safety,", "rule",
      "Z3 covers memory safety and concurrency.",
      untestable="[vague] no obligation kind of §7b's catalogue names memory safety or concurrency; the "
                 "sentence names no checkable row")

claim("vf0755", D, 755, "Used offline during language development, not during compilation", "rule",
      "The K framework proves the language's metatheory offline, not during compilation.",
      untestable="[tree] about the project's development process")

claim("vf0760", D, 760, "`k-semantics/nitpick.k`", "rule",
      "The operational semantics live in k-semantics/nitpick.k with proof claims in k-semantics/proofs/.",
      untestable="[tree] about the repository's files")

claim("vf0788", D, 788, "moves a page RW", "rule",
      "wildx_seal moves a page RW to RX with no reverse; a page is never writable and executable at once.",
      untestable="[unobservable] page permissions are not observable without raw memory access")

claim("vf0790", D, 790, "refuses any write after seal", "rule",
      "A write to a wildx page after its seal is refused, NITPICK-WILDX-001.",
      expect="refuse:WILDX-001", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    wildx_seal(page);
    page[0i64] = 144u8;
    wildx_free(page);
    exit 0i32;"""), wrong="accepted (a page writable after it is executable)")

claim("vf0791", D, 791, "any execute before it (`NITPICK-WILDX-002`)", "rule",
      "Executing a wildx page before its seal is refused, NITPICK-WILDX-002.",
      expect="refuse:WILDX-002", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    int64:r = wildx_call(page, 0i64);
    discard(r);
    wildx_free(page);
    exit 0i32;"""), wrong="accepted")

claim("vf0793", D, 793, "The lifecycle is a state machine", "rule",
      "The lifecycle alloc, write, seal, execute, free is accepted and runs: the page's `mov eax, 7; ret` "
      "returns 7.",
      expect="run:0", src=main_(WILDX_OK), wrong="refused, or a fault (MachineFault 107)")

claim("vf0794", D, 794, "double-free", "rule",
      "A double free of a wildx page is refused (a free is a move).",
      expect="refuse", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    wildx_free(page);
    wildx_free(page);
    exit 0i32;"""), wrong="accepted")

claim("vf0794b", D, 794, "use-after-free", "rule",
      "Executing a wildx page after its free is refused (a use after a move).",
      expect="refuse", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    wildx_seal(page);
    wildx_free(page);
    int64:r = wildx_call(page, 0i64);
    discard(r);
    exit 0i32;"""), wrong="accepted")

claim("vf0794c", D, 794, "seal-after-free", "rule",
      "Sealing a wildx page after its free is refused.",
      expect="refuse", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    wildx_free(page);
    wildx_seal(page);
    exit 0i32;"""), wrong="accepted")

claim("vf0795", D, 795, "no-live-pages-at-exit", "rule",
      "No live pages at exit, from the <wild-live> registry: `exit 0` with a live wildx page traps WildLeak.",
      expect="trap:WildLeak", src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    wildx_seal(page);
    exit 0i32;"""), wrong="exit 0 with the page leaked")

claim("vf0796", D, 796, "Guard pages turn an", "rule",
      "Guard pages turn a wildx over/underrun into a fault.",
      untestable="[unobservable] reaching a guard page needs pointer arithmetic past the checked indexing")

claim("vf0797", D, 797, "the page is placed by the kernel's mmap", "rule",
      "A wildx page is placed by the kernel's mmap randomisation (ASLR).",
      untestable="[platform] the kernel's placement policy")

claim("vf0802", D, 802, "validated by Nikola's sandbox and oracle rounds", "rule",
      "The generated bytes' contents are validated by Nikola's sandbox and oracle rounds, not these backends.",
      untestable="[vague] about another project's process")

claim("vf0805", D, 805, "will not reach the", "rule",
      "A program containing wildx will not reach the highest DO-178C / IEC 61508 / ISO 26262 levels.",
      untestable="[vague] a certification statement")

claim("vf0808", D, 808, "**`--extra-picky=no-wildx`**", "rule",
      "`--extra-picky=no-wildx` excludes runtime code generation: a program without wildx compiles under it "
      "and one using wildx does not.",
      expect="sh:0", sh=(heredoc("vf0808.npk", whole("vf0808", main_(WILDX_OK))) +
                         heredoc("vf0808p.npk", whole("vf0808p", FLAG_SRC)) +
                         '"$NPKC" vf0808.npk -o a.ll >a.out 2>&1 || exit 3\n'
                         '"$NPKC" vf0808p.npk --extra-picky=no-wildx -o b.ll >b.out 2>&1 || exit 1\n'
                         '"$NPKC" vf0808.npk --extra-picky=no-wildx -o c.ll >c.out 2>&1 && exit 1\n'
                         "exit 0\n"),
      wrong="the mode is unknown, or it accepts wildx")

claim("vf0811", D, 811, "It is a rule separate from `no-wild`", "rule",
      "no-wildx is a rule separate from no-wild: a program using `wild` (not wildx) compiles under "
      "no-wildx and not under no-wild.",
      expect="sh:0", sh=(heredoc("vf0811.npk", whole("vf0811", main_("""    wild int8->:p = alloc(16i64);
    dalloc(p);
    exit 0i32;"""))) +
                         '"$NPKC" vf0811.npk -o a.ll >a.out 2>&1 || exit 3\n'
                         '"$NPKC" vf0811.npk --extra-picky=no-wildx -o b.ll >b.out 2>&1 || exit 1\n'
                         '"$NPKC" vf0811.npk --extra-picky=no-wild -o c.ll >c.out 2>&1 && exit 1\n'
                         "exit 0\n"),
      wrong="no-wildx refuses wild too, or no-wild does not exist / accepts wild")


# ================================================================== §7 deadlock
claim("vf0819", D, 819, "borrows cannot cross a thread spawn or", "rule",
      "Borrows cannot cross an await: a $$i claim held by a pointer local across an await is refused.",
      expect="refuse", src="""error:E9;
async func:later = int32(int32:v) { pass v; };

async func:main = int32(cstring[]:_~argv) {
    int32:x = raw v32(4i32);
    int32->:p = $$i x;
    int32:y = (await later(1i32)) ?! E9;
    int32:z = <-p;
    if ((y + z) != 5i32) { exit 10i32; }
    exit 0i32;
};""", wrong="accepted")

claim("vf0820", D, 820, "tasks do not migrate between threads", "rule",
      "Tasks do not migrate between threads.",
      untestable="[timing] a scheduling property; no single run can show a migration never happens")

claim("vf0821", D, 821, "never move memory or reuse slots", "rule",
      "Shared arenas never move memory or reuse slots.",
      untestable="[unobservable] a program cannot observe an arena's slot reuse without raw addresses")

LEVEL_MUTEXES = """    Mutex<int32, 5i32>:hi = mutex(0i32) ?! Unreachable;
    Mutex<int32, 3i32>:lo = mutex(0i32) ?! Unreachable;
    int32:v = 0i32;"""

claim("vf0828", D, 828, "acquisition must strictly increase", "rule",
      "Acquisition must strictly increase: holding a level-5 mutex and acquiring a level-3 one is refused.",
      expect="refuse", src="""error:E9;
async func:main = int32(cstring[]:_~argv) {
%s
    {
        Guard<int32>:g = await hi.acquire(raw duration_ms(500i64)) ?! E9;
        Guard<int32>:h = await lo.acquire(raw duration_ms(500i64)) ?! E9;
        g.value = h.value + 1i32;
        v = g.value;
    }
    exit 0i32;
};""" % LEVEL_MUTEXES, wrong="accepted (a downward acquisition)")

claim("vf0828b", D, 828, "strictly", "rule",
      "Strictly: acquiring a second mutex of the same level while holding the first is refused.",
      expect="refuse", src="""error:E9;
async func:main = int32(cstring[]:_~argv) {
    Mutex<int32, 3i32>:a = mutex(0i32) ?! Unreachable;
    Mutex<int32, 3i32>:b = mutex(0i32) ?! Unreachable;
    int32:v = 0i32;
    {
        Guard<int32>:g = await a.acquire(raw duration_ms(500i64)) ?! E9;
        Guard<int32>:h = await b.acquire(raw duration_ms(500i64)) ?! E9;
        g.value = h.value + 1i32;
        v = g.value;
    }
    exit 0i32;
};""", wrong="accepted (>= permitted)")

claim("vf0828c", D, 828, "Circular wait is impossible", "rule",
      "Increasing acquisition is accepted: level 3 then level 5 compiles and runs.",
      expect="run:0", src="""error:E9;
async func:main = int32(cstring[]:_~argv) {
%s
    {
        Guard<int32>:h = await lo.acquire(raw duration_ms(500i64)) ?! E9;
        Guard<int32>:g = await hi.acquire(raw duration_ms(500i64)) ?! E9;
        g.value = h.value + 2i32;
        v = g.value;
    }
    if (v != 2i32) { exit 10i32; }
    exit 0i32;
};""" % LEVEL_MUTEXES, wrong="refused")

LEASES = """error:E9;
struct:Lease = { int32:v; };
func:take_1 = Lease() acquires 1i32 { pass Lease{ v: 1i32 }; };
func:take_3 = Lease() acquires 3i32 { pass Lease{ v: 3i32 }; };
func:take_9 = Lease() acquires 9i32 { pass Lease{ v: 9i32 }; };"""

claim("vf0829", D, 829, "A whole-program analysis computes each function's transitive", "rule",
      "The analysis is whole-program: holding level 3 and calling a function that acquires level 1 is refused.",
      expect="refuse", src=main_("""    drop downward();
    exit 0i32;""", LEASES + """
func:reaches_1 = NIL() never fails {
    Lease:g = take_1() ?! E9;
    discard(g.v);
    pass NIL;
};
func:downward = NIL() never fails {
    Lease:a = take_3() ?! E9;
    discard(a.v);
    drop reaches_1();
    pass NIL;
};"""), wrong="accepted (only direct acquisitions checked)",
      note="The `acquires N` spelling is CONCURRENCY_REFERENCE's; this range names no spelling.")

claim("vf0830", D, 830, "dynamically dispatched methods declare a maximum level", "rule",
      "A dynamically dispatched method declares a maximum level and implementations are checked against it: "
      "an impl acquiring 9 under `acquires <= 3` is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", LEASES + """
trait:Storage = { func:commit = NIL(Self:self) acquires <= 3i32; };
struct:Loose = { int32:v; };
impl:Loose:Storage = {
    pub func:commit = NIL(Self:self) never fails {
        Lease:g = take_9() ?! E9;
        discard(g.v);
        pass NIL;
    };
};"""), wrong="accepted")

claim("vf0831", D, 831, "an undeclared method may not acquire at all", "rule",
      "An undeclared dynamically dispatched method may not acquire at all: an impl of a trait method with no "
      "level acquiring one is refused.",
      expect="refuse", src=main_("""    exit 0i32;""", LEASES + """
trait:Plain = { func:touch = NIL(Self:self); };
struct:Loose = { int32:v; };
impl:Loose:Plain = {
    pub func:touch = NIL(Self:self) never fails {
        Lease:g = take_1() ?! E9;
        discard(g.v);
        pass NIL;
    };
};"""), wrong="accepted")

claim("vf0834", D, 834, "operation takes a deadline and returns `Result`", "rule",
      "Every blocking operation takes a deadline: an acquire without one is refused.",
      expect="refuse", src="""error:E9;
async func:main = int32(cstring[]:_~argv) {
    Mutex<int32, 3i32>:m = mutex(0i32) ?! Unreachable;
    int32:v = 0i32;
    {
        Guard<int32>:g = await m.acquire() ?! E9;
        v = g.value;
    }
    exit 0i32;
};""", wrong="accepted (an infinitely blocking acquire)")

claim("vf0836", D, 836, "surfaces as a", "rule",
      "What the analysis cannot cover surfaces as a timeout error at a known point.",
      untestable="[timing] needs a contended acquire whose deadline expires")

claim("vf0839", D, 839, "The flag is documented as verifying", "rule",
      "The flag verifies data-race and lock-order freedom, not deadlock freedom.",
      untestable="[vague] about a struck flag's documentation")


# ------------------------------------------------------------------ after run 1 (S45, S53)
# The rows helper matched `main`'s rows by the module prefix (`<cid>.` or `<cid>.main`), but
# `main`'s symbol in rows.txt is `@main`: every count in main read 0 (run 1). The helper now
# maps `<cid>.main` to `@main` and lets a bare `<cid>.` match `@main` too; failsafe's rows
# (`@npk_failsafe`) still never match. Every script that embeds it changed its TEXT, its
# expectation not; a script that agreed in run 1 is re-measured with the rest.
_HIT = ("function hit(s) { if (m ~ /\\.main$/) return s == \"@main\"; "
        "if (m ~ /\\.$/) return index(s, m) > 0 || s == \"@main\"; return index(s, m) > 0 } ")
ROWS_FN2 = ("rows() { awk -F'\\t' -v k=\"$1\" -v m=\"$2\" '" + _HIT + "$3 == k && hit($6)' obl/rows.txt"
            " | wc -l | tr -d ' '; }\n"
            "field() { awk -F'\\t' -v k=\"$1\" -v m=\"$2\" -v f=\"$3\" '" + _HIT +
            "$3 == k && hit($6) { print $f }' obl/rows.txt; }")
for _c in [c for c in CLAIMS if c["module"] == "verif1" and c["sh"] and ROWS_FN in c["sh"]]:
    refix(_c["id"], "the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): "
          "the helper was corrected in every script that embeds it", [(ROWS_FN, ROWS_FN2)], field="sh")
refix("vf0138b", "a refinement leads a Rules block's list (`{ limit<r>, clause }`, as vf0276's example): "
      "written after a clause it does not parse (PARSE-001); it now leads, which still tells the "
      "orders apart (0 traps LimitViolated by the refinement before the clause divides by it)",
      [("Rules<int32>:r_div = { 100i32 / $ > 1i32, limit<r_nz> };",
        "Rules<int32>:r_div = { limit<r_nz>, 100i32 / $ > 1i32 };")])
