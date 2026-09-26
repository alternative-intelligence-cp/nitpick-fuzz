"""M11 claims: MACRO_REFERENCE.md (lines 1-413) at HUNT2.

Every expectation below is written from the reference's text alone; nothing here was
run. Where a program is transcribed literally from a reference example that looks stale
against another reference or a decision, the `note` says so and why: that is reasoned,
not measured.

AST_REFERENCE.md was assigned to this module as well, and was not started when
session 6 stopped: the notes' `as0392` and `as0413` name AST claims not yet extracted.

Reviewed by session 7 before any of its programs ran (PROGRESS.md S51): the check
errors fixed (ids renamed to their lines, quotes moved to the lines that hold them),
and every claim's text and expectation read against its line; the full text around
each claim is re-read at triage for every claim whose program disagrees.
"""
from m11lib import *

covers("MACRO", 1)


def _whole(decls, body):
    """A whole program for a `sh:` claim: `mod:p;`, the declarations, `main` around
    `body`, and the standard failsafe (every prelude identity named)."""
    src = "mod:p;\n" + main_(body, decls)
    return src + "\n" + failsafe_text(src)


def _sh(prog, checks):
    """A script: write `prog` as p.npk, compile it, keep rc and the output, then `checks`."""
    return ("cat > p.npk <<'NPKEOF'\n" + prog.rstrip() + "\nNPKEOF\n"
            'out=$("$NPKC" p.npk -o p.ll 2>&1); rc=$?\n'
            'printf \'%s\\n\' "$out" | grep NITPICK | head -5\n' + checks.strip() + "\n")


# =====================================================================================
# MACRO_REFERENCE.md
# =====================================================================================
D = "MACRO"

claim("mc0015", D, 15, "does not compile against", "rule",
      "The prototype's 32-test corpus is written in a dialect that does not compile against this language.",
      untestable="[tree] a statement about the compiler repository's regression corpus (tests/bugs/), "
                 "not about what the compiler does with a program")

# ---- 1. Declaring a macro ------------------------------------------------------------
claim("mc0022", D, 22, "```nitpick", "example",
      "The declaration shape `macro:name = (param, …) { body };` declares a macro invoked as `#name(...)`.",
      expect="run:0",
      src=main_(r"""    int32:v = #name(41i32);
    if (v != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:name = (param) { param + 1i32; };"""),
      wrong="the declaration shape refused, or the parameter not substituted (exit 10)",
      note="the template instantiated with one parameter and an expression body")

claim("mc0026", D, 26, "What it contains determines where the macro may be", "rule",
      "Only the body decides where a macro may be invoked: an expression body invoked where a declaration "
      "is expected (module level) is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:just_value = () { 1i32 + 2i32; };

#just_value();"""),
      wrong="accepted: an expression spliced among declarations, or silently dropped")

claim("mc0032", D, 32, "| declarations (`func:`, …) | module level | top-level declarations |", "row",
      "A body of declarations invoked at module level splices as TOP-LEVEL declarations: a function "
      "written above the invocation can call what it emits.",
      expect="run:0",
      src=main_(r"""    if ((raw uses_it()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
func:uses_it = int32() never fails { pass ((raw emitted_one()) + 1i32); };

macro:emit_one = () { func:emitted_one = int32() never fails { pass 41i32; }; };

#emit_one();"""),
      wrong="refused: the emitted function not a top-level name (unresolved), or a wrong value (exit 10)")

claim("mc0033", D, 33, "| variable declarations | a `struct` body | fields |", "row",
      "A body of variable declarations invoked in a struct body splices as that struct's fields.",
      expect="run:0",
      src=main_(r"""    S:s = S{ a: 40i32, b: 2i32 };
    if ((s.a + s.b) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:two_fields = () { int32:a; int32:b; };

struct:S = { #two_fields(); };"""),
      wrong="refused: the struct has no field a or b (the splice emitted nothing)")

claim("mc0034", D, 34, "| function declarations | an `impl` body | methods |", "row",
      "A body of function declarations invoked in an impl body splices as methods of the type.",
      expect="run:0",
      src=main_(r"""    Cell:c = Cell{ n: 42i32 };
    if ((raw c.get_n()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
struct:Cell = { int32:n; };

macro:emit_get = () { func:get_n = int32(Cell:self) never fails { pass self.n; }; };

impl:Cell = { #emit_get(); };"""),
      wrong="refused: `Cell` has no method get_n (the splice emitted nothing)")

claim("mc0035", D, 35, "| a single expression | expression position | that expression |", "row",
      "A body of one expression invoked in expression position is that expression, as one node: "
      "`#four() * 10i32` is (2 + 2) * 10.",
      expect="run:0",
      src=main_(r"""    int32:v = #four() * 10i32;
    if (v != 40i32) {
        if (v == 22i32) { exit 10i32; }
        exit 11i32;
    }
    exit 0i32;""", r"""
macro:four = () { 2i32 + 2i32; };"""),
      wrong="a textual splice, 2 + 2 * 10 = 22 (exit 10), or another value (exit 11)")

claim("mc0037", D, 37, "A macro taking no parameters still declares an empty list", "rule",
      "A macro with no parameters must still write `()`: `macro:m = { … };` is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:m = { 7i32; };"""),
      wrong="accepted without the empty parameter list")

claim("mc0039", D, 39, "A body is a declaration body if it CONTAINS a declaration", "rule",
      "A body that contains a declaration is a declaration body even when its first item is an invocation; "
      "invoked at module level it emits both what the inner macro emits and its own declaration.",
      expect="run:0",
      src=main_(r"""    if (((raw f1()) + (raw f3())) != 40i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:inner_decl = () { func:f1 = int32() never fails { pass 10i32; }; };
macro:outer_decl = () { #inner_decl(); func:f3 = int32() never fails { pass 30i32; }; };

#outer_decl();"""),
      wrong="the body read per item from its leading `#`, and refused or emitting only part of it")

claim("mc0043", D, 43, "`macro:opt = () { #caller(x) + 1i32; };`", "rule",
      "`macro:opt = () { #caller(x) + 1i32; };` is accepted as a single-expression macro (a body beginning "
      "with `#` is not thereby a declaration body).",
      expect="run:0",
      src=main_(r"""    int32:x = raw v32(41i32);
    int32:v = #opt();
    if (v != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:opt = () { #caller(x) + 1i32; };"""),
      wrong="refused as \"not a single expression\" (the per-item reading D-125 replaced)")

claim("mc0044", D, 44, "a statement macro could not invoke another one", "rule",
      "A statement macro may invoke another statement macro (it could not before D-125): the body "
      "`{ #check_base(); #check_base(); }` expands at statement position.",
      expect="run:0",
      src=main_(r"""    #check_twice();
    exit 0i32;""", r"""
fixed int32:base = 7i32;

macro:check_base = () { if (base != 7i32) { exit 11i32; } };
macro:check_twice = () { #check_base(); #check_base(); };"""),
      wrong="refused (the body read as declarations), or the inner check misresolved (exit 11)")

claim("mc0046", D, 46, "nothing but a single invocation", "rule",
      "A body that is only one invocation is whatever the invoked macro is: an alias of an expression macro "
      "works in expression position.",
      expect="run:0",
      src=main_(r"""    int32:v = #alias();
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:b_val = () { 5i32; };
macro:alias = () { #b_val(); };"""),
      wrong="refused, or a wrong value (exit 10)")

claim("mc0046b", D, 46, "`macro:alias = () { #b(); };`", "rule",
      "\"is whatever `b` is\": an alias whose target is a declaration macro, invoked at module level, emits "
      "the target's declarations.",
      expect="run:0",
      src=main_(r"""    if ((raw from_b()) != 5i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:b_decls = () { func:from_b = int32() never fails { pass 5i32; }; };
macro:alias_d = () { #b_decls(); };

#alias_d();"""),
      wrong="refused for standing where a declaration is expected",
      note="AMBIGUOUS: the next sentence says the body 'is read as an expression body' and names only the "
           "expression and statement positions ('Both work'); the compiler's own tests/expansion/rejection/"
           "bounds.npk says such a body is refused at module level. The headline 'is whatever b is' is the "
           "expectation here.")

claim("mc0048", D, 48, "at statement position it becomes a block holding", "rule",
      "An alias of a statement macro, invoked at statement position, becomes a block holding `#b();` that "
      "the next round expands.",
      expect="run:0",
      src=main_(r"""    #alias_s();
    exit 0i32;""", r"""
fixed int32:base = 7i32;

macro:b_stmts = () { int32:t = base + 1i32; if (t != 8i32) { exit 11i32; } };
macro:alias_s = () { #b_stmts(); };"""),
      wrong="refused, or left unexpanded (a MACRO refusal), or misresolved (exit 11)")

# ---- 2. Invoking one -----------------------------------------------------------------
claim("mc0053", D, 53, "```nitpick", "example",
      "`#name()` invokes with no arguments and `#name(a, b)` with arguments.",
      expect="run:0",
      src=main_(r"""    int32:v = #zero();
    int32:w = #add2(40i32, 2i32);
    if (v != 0i32) { exit 10i32; }
    if (w != 42i32) { exit 11i32; }
    exit 0i32;""", r"""
macro:zero = () { 0i32; };
macro:add2 = (a, b) { a + b; };"""),
      wrong="either invocation form refused, or a wrong value (exit 10, 11)")

claim("mc0060", D, 60, "```nitpick", "example",
      "The four positions with one spelling: module level emits declarations, a struct body splices fields, "
      "an impl body splices methods, an expression position substitutes the expression.",
      expect="run:0",
      src=main_(r"""    string:s = #emit_msg();
    if (!(string_equals(s, "hello"))) { exit 10i32; }
    if (((raw greet1()) + (raw greet2())) != 10i32) { exit 11i32; }
    Point:p = Point{ x: 3i32, y: 4i32 };
    if ((p.x + p.y) != 7i32) { exit 12i32; }
    Box:b = Box{ n: 41i32 };
    if ((b.add_one() ?| 0i32) != 42i32) { exit 13i32; }
    exit 0i32;""", r"""
macro:make_pair = () {
    func:greet1 = int32() never fails { pass 7i32; };
    func:greet2 = int32() never fails { pass 3i32; };
};
macro:make_xy_fields = () { int32:x; int32:y; };
macro:emit_methods = () {
    func:add_one = int32(Box:self) { pass (self.n + 1i32); };
};
macro:emit_msg = () { "hello"; };

struct:Box = { int32:n; };
trait:Pair = { func:add_one = int32(Self:self); };

#make_pair();                          // module level — emits declarations

struct:Point = { #make_xy_fields(); };  // struct body — splices fields

impl:Box:Pair = { #emit_methods(); };   // impl body — splices methods"""),
      wrong="one of the four positions refused or emitting nothing (unresolved names), or a wrong value (10-13)")

claim("mc0070", D, 70, "An invocation whose expansion does not fit where it landed is an error", "rule",
      "Fields into something that is not a struct is an error: a variable-declaration body invoked in an "
      "impl body is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
struct:T = { int32:v; };

macro:stmts = () { int32:a; };

impl:T = { #stmts(); };"""),
      wrong="accepted: the variable declaration dropped or turned into something the impl holds")

claim("mc0071", D, 71, "declarations into an expression", "rule",
      "Declarations into an expression is an error: a declaration body invoked where a value is expected "
      "is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = #decls();
    exit 0i32;""", r"""
macro:decls = () { func:g = int32() never fails { pass 1i32; }; };"""),
      wrong="accepted: the invocation typed as nothing (the pre-D-126 INVALID path) or the declarations dropped")

claim("mc0076", D, 76, "| module level | declarations | cloned |", "row",
      "At module level a declarations body arrives as a copy of its declarations, all of them callable.",
      expect="run:0",
      src=main_(r"""    if (((raw greet1()) + (raw greet2())) != 10i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:make_pair = () {
    func:greet1 = int32() never fails { pass 7i32; };
    func:greet2 = int32() never fails { pass 3i32; };
};

#make_pair();"""),
      wrong="refused: an emitted function missing, or a wrong value (exit 10)")

claim("mc0077", D, 77, "| `struct` body | variable declarations | **converted to fields** |", "row",
      "In a struct body a variable-declarations body is converted to fields, which can be written and read "
      "like any field.",
      expect="run:0",
      src=main_(r"""    Point:p = Point{ x: 1i32, y: 2i32 };
    p.x = 40i32;
    if ((p.x + p.y) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:xy = () { int32:x; int32:y; };

struct:Point = { #xy(); };"""),
      wrong="refused: no such fields, or a write lost (exit 10)")

claim("mc0078", D, 78, "| `impl` or `trait` body | declarations | cloned |", "row",
      "A trait body takes a declarations body too: spliced signatures become required methods an impl supplies.",
      expect="run:0",
      src=main_(r"""    Bx:b = Bx{ n: 42i32 };
    if ((b.size_it() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:sigs = () { func:size_it = int32(Self:self); };

trait:Sized2 = { #sigs(); };

struct:Bx = { int32:n; };

impl:Bx:Sized2 = { func:size_it = int32(Bx:self) { pass self.n; }; };"""),
      wrong="refused: the trait body refuses the splice, or the impl's method is not a member of the trait")

claim("mc0079", D, 79, "| expression position | one expression | substituted in place |", "row",
      "In expression position the one expression is substituted in place, each invocation its own copy with "
      "its own argument: #doubled(3) + #doubled(10) = 26.",
      expect="run:0",
      src=main_(r"""    int32:v = #doubled(3i32) + #doubled(10i32);
    if (v != 26i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:doubled = (V) { V + V; };"""),
      wrong="a shared body rewritten by the second invocation (20 or 40: exit 10)")

claim("mc0080", D, 80, "| `enum` body | — | refused |", "row",
      "An invocation in an enum body is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:fields = () { int32:a; };

enum:Col = { First; #fields(); };"""),
      wrong="accepted: the body mapped onto variants, or dropped")

claim("mc0082", D, 82, "parses as a STATEMENT", "rule",
      "`int32:x;` parses as a statement in a macro body and as a field in a struct, so a struct splice is a "
      "conversion rather than a copy.",
      untestable="[internal] which grammar reads the text and how the splice converts it are the parser's "
                  "and expander's internals; mc0077 tests the observable result")

claim("mc0085", D, 85, "carrying an initialiser or a qualifier is refused rather than stripped", "rule",
      "A variable declaration with an initialiser spliced into a struct body is refused rather than stripped.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:with_init = () { int32:a = 5i32; };

struct:S = { #with_init(); };"""),
      wrong="accepted with the initialiser silently dropped")

claim("mc0085b", D, 85, "a field has", "rule",
      "A variable declaration carrying a qualifier (`fixed`) spliced into a struct body is refused rather "
      "than stripped: \"a field has neither\".",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:with_qual = () { fixed int32:a; };

struct:S = { #with_qual(); };"""),
      wrong="accepted",
      note="CONTRADICTED ELSEWHERE (reasoned): AST_REFERENCE:79 says FieldDecl carries memory qualifiers, "
           "D-222 makes `fixed` legal on a struct field, and the compiler's tests/accept/splicing.npk says a "
           "qualified field splices WITH its qualifier since 1.0.8.")

claim("mc0088", D, 88, "An enum body is refused", "rule",
      "An enum body is refused whatever the body's shape: a declarations body invoked in an enum is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:decl_body = () { func:gg = int32() never fails { pass 1i32; }; };

enum:Col = { Red; #decl_body(); };"""),
      wrong="accepted: declarations mapped onto variants or dropped")

# ---- 3. Parameter substitution -------------------------------------------------------
claim("mc0094", D, 94, "An argument replaces every occurrence of the parameter name in the body", "rule",
      "An argument replaces every occurrence of the parameter, including inside a declaration the body emits.",
      expect="run:0",
      src=main_(r"""    if ((raw twice_n()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:mk_twice = (N) { func:twice_n = int32() never fails { pass (N + N); }; };

#mk_twice(21i32);"""),
      wrong="refused: N left unresolved inside the emitted function, or only one occurrence replaced")

claim("mc0097", D, 97, "```nitpick", "example",
      "`#make_const(42i32);` emits `func:my_const = int32() { pass 42i32; };`.",
      expect="run:0",
      src=main_(r"""    if ((my_const() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:make_const = (N) {
    func:my_const = int32() { pass N; };
};

#make_const(42i32);      // emits  func:my_const = int32() { pass 42i32; };"""),
      wrong="refused (N unresolved), or my_const not emitted, or a wrong value (exit 10)")

claim("mc0105", D, 105, "Substitution traverses the whole emitted subtree", "rule",
      "Substitution reaches a parameter however deep it sits in the emitted subtree (inside a pick arm "
      "inside an if inside an emitted function).",
      expect="run:0",
      src=main_(r"""    if ((raw deep_fn(1i32)) != 42i32) { exit 10i32; }
    if ((raw deep_fn(5i32)) != 21i32) { exit 11i32; }
    exit 0i32;""", r"""
macro:mk_deep = (K) {
    func:deep_fn = int32(int32:a) never fails {
        if (a > 0i32) {
            pick (a) { (1i32) { pass (K * 2i32); }, (*) { pass K; } }
        }
        pass 0i32;
    };
};

#mk_deep(21i32);"""),
      wrong="refused: K left standing in a nested node")

claim("mc0105b", D, 105, "It is not textual", "rule",
      "Substitution is not textual: the argument lands as one AST node, so #times3(1 + 2) is (1 + 2) * 3 = 9.",
      expect="run:0",
      src=main_(r"""    int32:v = #times3(1i32 + 2i32);
    if (v != 9i32) {
        if (v == 7i32) { exit 10i32; }
        exit 11i32;
    }
    exit 0i32;""", r"""
macro:times3 = (N) { N * 3i32; };"""),
      wrong="a textual substitution, 1 + 2 * 3 = 7 (exit 10)")

# ---- 4. Emission ---------------------------------------------------------------------
claim("mc0112", D, 112, "```nitpick", "example",
      "The emit_helpers example: three emitted declarations referencing each other; helper_sum is 42.",
      expect="run:0",
      src=main_(r"""    if ((helper_sum() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:emit_helpers = () {
    func:helper_a = int32() { pass 11i32; };
    func:helper_b = int32() { pass 31i32; };
    func:helper_sum = int32() { pass (raw helper_a()) + (raw helper_b()); };
};

#emit_helpers();"""),
      wrong="refused, or a wrong value (exit 10)",
      note="Transcribed literally. Reasoned, not measured: the example applies `raw` to helper_a/helper_b, which "
           "are declared without `never fails`; D-163 licenses `raw` only by a `never fails` callee "
           "(NITPICK-TYPE-042), so the example as printed may not be a valid program. mc0120 tests the same "
           "claim with `never fails` added.")

claim("mc0120", D, 120, "All three become top-level declarations", "rule",
      "All three emitted functions become top-level declarations and helper_sum resolves the other two.",
      expect="run:0",
      src=main_(r"""    if ((raw helper_sum()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:emit_helpers = () {
    func:helper_a = int32() never fails { pass 11i32; };
    func:helper_b = int32() never fails { pass 31i32; };
    func:helper_sum = int32() never fails { pass ((raw helper_a()) + (raw helper_b())); };
};

#emit_helpers();"""),
      wrong="refused: helper_a or helper_b unresolved inside helper_sum")

claim("mc0121", D, 121, "Names emitted by one expansion are visible to each other", "rule",
      "Names emitted by one expansion are visible to each other regardless of order: the first emitted "
      "function calls two emitted after it.",
      expect="run:0",
      src=main_(r"""    if ((raw total_first()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:emit_rev = () {
    func:total_first = int32() never fails { pass ((raw part_x()) + (raw part_y())); };
    func:part_x = int32() never fails { pass 40i32; };
    func:part_y = int32() never fails { pass 2i32; };
};

#emit_rev();"""),
      wrong="refused: part_x/part_y unresolved (resolution run while emitting)")

claim("mc0126", D, 126, "```nitpick", "example",
      "`struct:Point = { #make_xy_fields(); };` gives Point fields x and y.",
      expect="run:0",
      src=main_(r"""    Point:p = Point{ x: 3i32, y: 4i32 };
    if ((p.x + p.y) != 7i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:make_xy_fields = () { int32:x; int32:y; };

struct:Point = { #make_xy_fields(); };"""),
      wrong="refused: Point has no field x or y")

claim("mc0132", D, 132, "may mix spliced and literal fields freely", "rule",
      "A struct may mix spliced and literal fields: a literal field, a splice of two, a literal field gives "
      "four fields of 16 bytes, each holding its own value.",
      expect="run:0",
      src=main_(r"""    Quad:q = Quad{ a: 1i32, b: 2i32, c: 3i32, d: 4i32 };
    if (q.a != 1i32) { exit 10i32; }
    if (q.b != 2i32) { exit 11i32; }
    if (q.c != 3i32) { exit 12i32; }
    if (q.d != 4i32) { exit 13i32; }
    if (#size_of<Quad>() != 16i64) { exit 14i32; }
    exit 0i32;""", r"""
macro:two_mid = () { int32:b; int32:c; };

struct:Quad = { int32:a; #two_mid(); int32:d; };"""),
      wrong="refused, a field misplaced (10-13), or a layout with a field lost or doubled (14)")

claim("mc0136", D, 136, "```nitpick", "example",
      "The emit_methods example: `impl:Box:Pair = { #emit_methods(); };` gives Box the method add_one.",
      expect="run:0",
      src=main_(r"""    Box:b = Box{ n: 41i32 };
    if ((b.add_one() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
struct:Box = { int32:n; };
trait:Pair = { func:add_one = int32(Self:self); };

macro:emit_methods = () {
    func:add_one = int32($$i Box:self) { pass (self.n + 1i32); };
};

impl:Box:Pair = { #emit_methods(); };"""),
      wrong="refused, or a wrong value (exit 10)",
      note="Transcribed literally. Reasoned, not measured: `$$i Box:self` is written nowhere else in the "
           "references; AST_REFERENCE:300/503 and OP_REFERENCE:311 make `$$i` a unary EXPRESSION operator, not "
           "a parameter qualifier, so the example as printed may not parse. mc0034 tests the claim with the "
           "known-good receiver spelling.")

# ---- 5. Hygiene ----------------------------------------------------------------------
claim("mc0146", D, 146, "An identifier in a macro body resolves in the scope where the macro was", "rule",
      "An identifier in a macro body resolves where the macro was written, always: invoked inside a function "
      "with a local of the same name, the macro reads the module binding.",
      expect="run:0",
      src=main_(r"""    int32:r = raw probe();
    if (r != 101i32) {
        if (r == 6i32) { exit 10i32; }
        exit 11i32;
    }
    exit 0i32;""", r"""
fixed int32:shared = 100i32;

macro:report = () { shared + 1i32; };

func:probe = int32() never fails {
    int32:shared = 5i32;
    int32:got = #report();
    discard(shared);
    pass got;
};"""),
      wrong="the caller's local read (6: exit 10), the prototype's back-compat path")

claim("mc0149", D, 149, "A macro is invocable only in the module that declares it", "rule",
      "A macro is invocable in the module that declares it, including a nested module invoking a macro it "
      "declares itself.",
      expect="run:0",
      src=main_(r"""    if ((raw inner_m.reads_it()) != 51i32) { exit 10i32; }
    exit 0i32;""", r"""
mod:inner_m = {
    fixed int32:only_inside = 50i32;

    macro:read_inside = () { only_inside + 1i32; };

    pub func:reads_it = int32() never fails {
        int32:got = #read_inside();
        pass got;
    };
};"""),
      wrong="refused: the nested module's own macro unreachable, or resolved in the file's scope")

claim("mc0150", D, 150, "`use` does not bind it, `pub` on it changes nothing", "rule",
      "A macro is not exported: a `pub macro:` in another module, named in a `use`, is still not invocable.",
      expect="refuse",
      src=main_(r"""    int32:v = #lib_seven();
    if (v != 7i32) { exit 10i32; }
    exit 0i32;""", r"""
use "./maclib.npk".lib_seven;"""),
      files={"maclib.npk": r"""mod:maclib;

pub macro:lib_seven = () { 7i32; };

pub func:anchor = int32() never fails { pass 0i32; };"""},
      wrong="accepted: the imported `pub` macro expands (exit 0)",
      note="AST_REFERENCE:392 says the opposite ('A macro may be imported'); as0392 tests that reading.")

claim("mc0151", D, 151, "inside the declaring one cannot reach it", "rule",
      "A module nested inside the declaring one cannot invoke its macro; invoking a macro from another "
      "module is NITPICK-MACRO-007.",
      expect="refuse:NITPICK-MACRO-007",
      src=main_(r"""    exit 0i32;""", r"""
macro:file_macro = () { 1i32; };

mod:inner_n = {
    pub func:use_it = int32() never fails {
        int32:v = #file_macro();
        pass v;
    };
};"""),
      wrong="accepted: the nested module reaches the file's macro")

claim("mc0154", D, 154, "macro from another module is `NITPICK-MACRO-007`", "rule",
      "Invoking, at module level, a macro declared in another file module (imported with `use ….*`) is "
      "NITPICK-MACRO-007.",
      expect="refuse:NITPICK-MACRO-007",
      src=main_(r"""    int32:a = raw anchor();
    discard(a);
    exit 0i32;""", r"""
use "./maclib.npk".*;

#shared_macro();"""),
      files={"maclib.npk": r"""mod:maclib;

pub macro:shared_macro = () { func:emitted = int32() never fails { pass 1i32; }; };

pub func:anchor = int32() never fails { pass 0i32; };"""},
      wrong="accepted: the macro crosses the module boundary, or refused under another code")

claim("mc0156", D, 156, "is the mechanism for code generation that crosses a module", "rule",
      "`#[derive]` is the mechanism for code generation across modules; `macro:` is a local shorthand.",
      untestable="[vague] a statement of which mechanism is meant for what; it states no outcome a program "
                 "could check beyond mc0150/mc0154")

claim("mc0159", D, 159, "```nitpick", "example",
      "The hygiene example: `#report()` reads the TOP-LEVEL `shared` (100), not main's local 5, so the "
      "template is \"shared = 100\".",
      expect="run:0",
      src=r"""int32:shared = 100i32;

macro:report = () { `shared = &{shared}`; };

func:main = int32(cstring[]:_~argv) {
    int32:shared = 5i32;
    string:s = #report();     // `shared` is the TOP-LEVEL 100, not the local 5
    if (!(string_equals(s, "shared = 100"))) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="the local read: \"shared = 5\" (exit 10)",
      note="Transcribed literally. Reasoned, not measured: the module-level `int32:shared = 100i32;` carries no "
           "qualifier, and D-211/D-222 require every module binding to be `fixed`; mc0203 tests the claim with "
           "`fixed`.")

claim("mc0171", D, 171, "that is a **compile error**", "rule",
      "A name in a macro body that does not resolve in the defining scope is a compile error, never a "
      "fallback to the call site.",
      expect="refuse",
      src=main_(r"""    int32:only_local = raw v32(3i32);
    int32:s = #grab();
    discard(s);
    discard(only_local);
    exit 0i32;""", r"""
macro:grab = () { only_local + 1i32; };"""),
      wrong="accepted: the caller's only_local used (the prototype's fallback)")

claim("mc0176", D, 176, "```nitpick", "example",
      "`#caller(shared)` inside a template reads the invocation site's `shared`: \"shared = 5\".",
      expect="run:0",
      src=main_(r"""    int32:shared = raw v32(5i32);
    string:s = #report_opt();
    if (!(string_equals(s, "shared = 5"))) { exit 10i32; }
    exit 0i32;""", r"""
fixed int32:shared = 100i32;

macro:report_opt = () { `shared = &{#caller(shared)}`; };"""),
      wrong="the defining scope's 100 read (exit 10)")

claim("mc0180", D, 180, "resolves `NAME` at the **invocation site**", "rule",
      "`#caller(NAME)` resolves NAME at the invocation site: the caller's int32 `flag`, not the module's bool.",
      expect="run:0",
      src=main_(r"""    int32:flag = raw v32(41i32);
    int32:b = #report_flag();
    if (b != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
fixed bool:flag = true;

macro:report_flag = () { #caller(flag) + 1i32; };"""),
      wrong="refused: the module's bool read, so `bool + int32` fails to type")

claim("mc0181", D, 181, "naming something absent there is an error", "rule",
      "`#caller(NAME)` naming something absent at the invocation site is an error.",
      expect="refuse",
      src=main_(r"""    int32:v = #reach_absent();
    discard(v);
    exit 0i32;""", r"""
macro:reach_absent = () { #caller(nowhere_at_all) + 1i32; };"""),
      wrong="accepted: the unresolved name typed as nothing")

claim("mc0186", D, 186, "It resolves the way any name at that point resolves", "rule",
      "`#caller(NAME)` reaches past the caller's locals to the module's own names: with no local of that "
      "name it reads the module binding.",
      expect="run:0",
      src=main_(r"""    int32:v = #via_caller();
    if (v != 8i32) { exit 10i32; }
    exit 0i32;""", r"""
fixed int32:mod_only = 7i32;

macro:via_caller = () { #caller(mod_only) + 1i32; };"""),
      wrong="refused: `#caller` limited to the caller's locals")

claim("mc0188", D, 188, "It differs from writing the", "rule",
      "`#caller(NAME)` differs from the bare name exactly when the invocation site has a local binding of it.",
      expect="run:0",
      src=main_(r"""    int32:lvl = raw v32(3i32);
    int32:c = #bare_lvl();
    int32:d = #caller_lvl();
    if ((raw no_local()) != 0i32) { exit 10i32; }
    if (c != 7i32) { exit 11i32; }
    if (d != 3i32) { exit 12i32; }
    exit 0i32;""", r"""
fixed int32:lvl = 7i32;

macro:bare_lvl = () { lvl; };
macro:caller_lvl = () { #caller(lvl); };

func:no_local = int32() never fails {
    int32:a = #bare_lvl();
    int32:b = #caller_lvl();
    pass (a - b);
};"""),
      wrong="the two differ with no local (10), the bare name reads the local (11), or #caller the module (12)")

claim("mc0193", D, 193, "site is `NITPICK-RESOLVE-002`", "rule",
      "`#caller(NAME)` naming something absent from the invocation site (declared only inside another "
      "function) is NITPICK-RESOLVE-002.",
      expect="refuse:NITPICK-RESOLVE-002",
      src=main_(r"""    int32:s = #reach();
    discard(s);
    exit 0i32;""", r"""
func:elsewhere = int32() never fails {
    int32:only_in_elsewhere = 1i32;
    pass only_in_elsewhere;
};

macro:reach = () { #caller(only_in_elsewhere) + 1i32; };"""),
      wrong="accepted, or refused under another code")

claim("mc0194", D, 194, "is `NITPICK-MACRO-008`", "rule",
      "Writing `#caller` outside a macro body is NITPICK-MACRO-008.",
      expect="refuse:NITPICK-MACRO-008",
      src=main_(r"""    int32:v = raw v32(1i32);
    int32:w = #caller(v);
    discard(w);
    exit 0i32;"""),
      wrong="accepted: `#caller(v)` read as `v` or as nothing")

claim("mc0201", D, 201, "| a declaration | the declarations, in this module | landing where the macro was written |", "row",
      "Declarations emitted at module level land in this module, where the macro was written: a free name in "
      "an emitted function resolves to the module binding.",
      expect="run:0",
      src=main_(r"""    int32:base_d = raw v32(0i32);
    discard(base_d);
    if ((raw read_base()) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
fixed int32:base_d = 40i32;

macro:emit_reader = () { func:read_base = int32() never fails { pass (base_d + 2i32); }; };

#emit_reader();"""),
      wrong="refused or a wrong value (exit 10)")

claim("mc0202", D, 202, "| a statement | **a block** holding the statements | the block's parent being the module scope |", "row",
      "A statement invocation becomes a block whose parent is the module scope: a free name in it reads the "
      "module binding past the caller's local of the same name.",
      expect="run:0",
      src=main_(r"""    int32:base = raw v32(3i32);
    #check_base();
    if (base != 3i32) { exit 12i32; }
    exit 0i32;""", r"""
fixed int32:base = 7i32;

macro:check_base = () { if (base != 7i32) { exit 11i32; } };"""),
      wrong="the caller's local 3 read (exit 11), or the caller's binding changed (12)")

claim("mc0203", D, 203, "| an expression | the expression, substituted in place | one mark on the substituted node |", "row",
      "An expression invocation is substituted in place and still resolves its free names where the macro "
      "was written: 101, not the caller's 5 + 1.",
      expect="run:0",
      src=main_(r"""    int32:shared = raw v32(5i32);
    int32:a = #report();
    if (a != 101i32) {
        if (a == 6i32) { exit 10i32; }
        exit 11i32;
    }
    if (shared != 5i32) { exit 12i32; }
    exit 0i32;""", r"""
fixed int32:shared = 100i32;

macro:report = () { shared + 1i32; };"""),
      wrong="the caller's local read (6: exit 10)")

claim("mc0207", D, 207, "collide with a caller's `tmp`", "rule",
      "A `tmp` declared in a statement body cannot collide with the caller's `tmp`: both coexist and the "
      "caller's keeps its value.",
      expect="run:0",
      src=main_(r"""    int32:tmp = raw v32(1i32);
    #make_tmp();
    if (tmp != 1i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:make_tmp = () { int32:tmp = 99i32; discard(tmp); };"""),
      wrong="refused as a redeclaration, or the caller's tmp overwritten (exit 10)")

claim("mc0207b", D, 207, "it cannot be read after the invocation", "rule",
      "A local declared in a statement body cannot be read after the invocation.",
      expect="refuse",
      src=main_(r"""    #make_tmp();
    int32:t2 = tmp;
    discard(t2);
    exit 0i32;""", r"""
macro:make_tmp = () { int32:tmp = 99i32; discard(tmp); };"""),
      wrong="accepted: the macro's tmp leaked into the caller's scope")

claim("mc0208", D, 208, "name in the body walks up past the caller's locals to the module", "rule",
      "A free name in a statement body walks past the caller's locals to the module: a module FUNCTION is "
      "called although the caller has an int32 local of the same name.",
      expect="run:0",
      src=main_(r"""    int32:helper_v = raw v32(3i32);
    #check_helper();
    discard(helper_v);
    exit 0i32;""", r"""
func:helper_v = int32() never fails { pass 7i32; };

macro:check_helper = () { if ((raw helper_v()) != 7i32) { exit 11i32; } };"""),
      wrong="refused: the caller's int32 local found and called")

claim("mc0209", D, 209, "statement-position hygiene needs no check anywhere", "rule",
      "One block node carries the statement-position hygiene rule; no check is needed anywhere.",
      untestable="[internal] how the expander represents the rule; the observable halves are mc0202-mc0208")

claim("mc0220", D, 220, "no longer exists", "rule",
      "NITPICK-061 (MACRO_HYGIENE_VIOLATION) no longer exists: a macro whose free name resolves differently at "
      "the call site compiles with no such diagnostic.",
      expect="sh:0",
      sh=_sh(_whole(r"""
fixed int32:shared = 100i32;

macro:report = () { shared + 1i32; };""", r"""    int32:shared = 5i32;
    int32:a = #report();
    if (a != 101i32) { exit 10i32; }
    if (shared != 5i32) { exit 11i32; }
    exit 0i32;"""), r"""
[ "$rc" -eq 0 ] || exit 2
if printf '%s\n' "$out" | grep -qE 'NITPICK-061|HYGIENE'; then exit 3; fi
exit 0"""),
      wrong="a refusal (2) or a NITPICK-061 hygiene warning (3)")

# ---- 6. Expansion order --------------------------------------------------------------
claim("mc0225", D, 225, "Expansion precedes everything.", "rule",
      "Expansion runs before name resolution: a struct emitted by a macro names a parameter type of a "
      "function written above the invocation.",
      expect="run:0",
      src=main_(r"""    Pt2:p = Pt2{ a: 40i32, b: 2i32 };
    if ((raw use_pt(p)) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
func:use_pt = int32(Pt2:p) never fails { pass (p.a + p.b); };

macro:emit_type = () { struct:Pt2 = { int32:a; int32:b; }; };

#emit_type();"""),
      wrong="refused: Pt2 unresolved at the function above the invocation")

claim("mc0226", D, 226, "so what those passes see is the expanded", "rule",
      "Static analyses see the expanded program: an emitted function with a path that reaches its end "
      "without `pass` is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:emit_bad = () {
    func:bad_path = int32(int32:a) never fails { if (a > 0i32) { pass 1i32; } };
};

#emit_bad();"""),
      wrong="accepted: the analysis ran on the unexpanded program and never saw bad_path")

claim("mc0231", D, 231, "```nitpick", "example",
      "`#outer();` expands to `{ #inner(); f3 }`, then inner expands on the next round: f1 and f3 both exist.",
      expect="run:0",
      src=main_(r"""    if (((f1() ?| 0i32) + (f3() ?| 0i32)) != 40i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:inner = () { func:f1 = int32() { pass 10i32; }; };
macro:outer = () { #inner(); func:f3 = int32() { pass 30i32; }; };

#outer();     // expands to { #inner(); f3 }, then inner expands on the next round"""),
      wrong="refused: f1 missing (one round only) or #inner() left standing")

claim("mc0238", D, 238, "The loop repeats until no invocation remains.", "rule",
      "The fixed-point loop repeats until no invocation remains: three levels of nested declaration macros "
      "all expand.",
      expect="run:0",
      src=main_(r"""    if (((raw g1()) + (raw g2()) + (raw g3())) != 6i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:lvl3 = () { func:g3 = int32() never fails { pass 3i32; }; };
macro:lvl2 = () { #lvl3(); func:g2 = int32() never fails { pass 2i32; }; };
macro:lvl1 = () { #lvl2(); func:g1 = int32() never fails { pass 1i32; }; };

#lvl1();"""),
      wrong="refused: g3 missing (a bounded number of rounds)")

claim("mc0239", D, 239, "struct-body macro may expand to a body containing another struct-body macro", "rule",
      "A struct-body macro may expand to a body containing another struct-body macro, which expands next round.",
      expect="run:0",
      src=main_(r"""    Trio:t = Trio{ p: 5i32, q: 6i32, r: 9i32 };
    if ((t.p + t.q + t.r) != 20i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:inner_two = () { int32:p; int32:q; };
macro:outer_three = () { #inner_two(); int32:r; };

struct:Trio = { #outer_three(); };"""),
      wrong="refused: p/q missing, or the inner invocation left in the field list")

claim("mc0241", D, 241, "Expansion precedes `comptime` evaluation", "rule",
      "Expansion precedes comptime evaluation: `comptime(#twice_m(21i32))` evaluates the expanded expression.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(#twice_m(21i32));
    if (v != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:twice_m = (V) { V * 2i32; };"""),
      wrong="refused: comptime over an unexpanded invocation")

# ---- 7. Expansion is bounded ---------------------------------------------------------
claim("mc0246", D, 246, "```nitpick", "example",
      "`macro:m = () { #m(); };      // refused` — the self-invoking declaration is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:m = () { #m(); };      // refused"""),
      wrong="accepted",
      note="AMBIGUOUS: the example refuses the DECLARATION, but the bounds are properties of expansion (an "
           "uninvoked body is a template, line 281); mc0250b tests the invoked case. Transcribed literally, "
           "with no invocation.")

_deep = "1i32"
for _i in range(1000):
    _deep = "(1i32 + " + _deep + ")"

claim("mc0250", D, 250, "limits one invocation's nesting", "rule",
      "A depth bound limits one invocation's nesting: an expression body nested 1000 operators deep is "
      "refused as a compile error.",
      expect="refuse",
      src=main_(r"""    int32:v = #deep();
    discard(v);
    exit 0i32;""", "macro:deep = () { " + _deep + "; };"),
      wrong="accepted (no depth bound), or the compiler crashes (exit other than 0/1)",
      note="the text states no number (line 411 leaves it open); 1000 nested additions is far past anything "
           "written on purpose, which is the text's own reason for the bound")

claim("mc0250b", D, 250, "limits", "rule",
      "An iteration bound limits the fixed-point loop: two declaration macros that invoke each other are "
      "refused as a compile error instead of looping.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:ping_m = () {
    func:from_ping = int32() never fails { pass 1i32; };
    #pong_m();
};
macro:pong_m = () {
    func:from_pong = int32() never fails { pass 2i32; };
    #ping_m();
};

#ping_m();"""),
      wrong="the compiler never terminates (the prototype), or crashes")

claim("mc0251", D, 251, "Exceeding either is an ordinary compile error naming the", "rule",
      "Exceeding the iteration bound is a compile error naming the macro and the chain that reached the "
      "bound: both ping_m and pong_m appear in the diagnostic.",
      expect="sh:0",
      sh=_sh(_whole(r"""
macro:ping_m = () {
    func:from_ping = int32() never fails { pass 1i32; };
    #pong_m();
};
macro:pong_m = () {
    func:from_pong = int32() never fails { pass 2i32; };
    #ping_m();
};

#ping_m();""", r"""    exit 0i32;"""), r"""
[ "$rc" -eq 1 ] || exit 2
printf '%s\n' "$out" | grep -q 'ping_m' || exit 3
printf '%s\n' "$out" | grep -q 'pong_m' || exit 4
exit 0"""),
      wrong="accepted or crashed (2), or a diagnostic that names neither macro or only one (3, 4)")

claim("mc0256", D, 256, "one budget would report them alike", "rule",
      "The depth bound and the iteration bound are separate and report differently: a too-deep single "
      "expansion and a mutual recursion are refused with different diagnostic codes.",
      expect="sh:0",
      sh=r"""
d="1i32"
for i in $(seq 1000); do d="(1i32 + $d)"; done
cat > deep.npk <<NPKEOF
mod:deep;
macro:deep_m = () { $d; };
func:main = int32(cstring[]:_~argv) {
    int32:v = #deep_m();
    discard(v);
    exit 0i32;
};
func:failsafe = int32(Error:_~e) { exit 1i32; };
NPKEOF
cat > loopy.npk <<'NPKEOF'
mod:loopy;
macro:ping_m = () {
    func:from_ping = int32() never fails { pass 1i32; };
    #pong_m();
};
macro:pong_m = () {
    func:from_pong = int32() never fails { pass 2i32; };
    #ping_m();
};
#ping_m();
func:main = int32(cstring[]:_~argv) { exit 0i32; };
func:failsafe = int32(Error:_~e) { exit 1i32; };
NPKEOF
o1=$("$NPKC" deep.npk -o deep.ll 2>&1); r1=$?
o2=$("$NPKC" loopy.npk -o loopy.ll 2>&1); r2=$?
c1=$(printf '%s\n' "$o1" | grep -oE 'NITPICK-[A-Z]+-[0-9]+' | sort -u | tr '\n' ' ')
c2=$(printf '%s\n' "$o2" | grep -oE 'NITPICK-[A-Z]+-[0-9]+' | sort -u | tr '\n' ' ')
echo "deep rc=$r1 [$c1] loop rc=$r2 [$c2]"
[ "$r1" -eq 1 ] || exit 2
[ "$r2" -eq 1 ] || exit 3
[ -n "$c1" ] && [ -n "$c2" ] || exit 4
[ "$c1" != "$c2" ] || exit 5
exit 0""",
      wrong="either case accepted (2, 3), no code (4), or both reported alike (5)")

claim("mc0264", D, 264, "still in the program when expansion finishes is refused", "rule",
      "Every `#name(...)` still standing after expansion is refused, wherever it stands: an unknown one as a "
      "statement inside a loop body.",
      expect="refuse",
      src=main_(r"""    for (int64:i in 0i64...2i64) {
        #nothing_here_stmt();
        discard(i);
    }
    exit 0i32;"""),
      wrong="accepted: the invocation expands to nothing and says nothing")

claim("mc0265", D, 265, "as `MACRO-001` if the name is unknown", "rule",
      "An unknown `#name(...)` left standing at module level is NITPICK-MACRO-001.",
      expect="refuse:NITPICK-MACRO-001",
      src=main_(r"""    exit 0i32;""", r"""
#no_such_macro();"""),
      wrong="accepted, or refused under another code")

claim("mc0265b", D, 265, "`MACRO-007` if the macro is", "rule",
      "An invocation of a macro declared in another module, left standing in expression position, is "
      "NITPICK-MACRO-007.",
      expect="refuse:NITPICK-MACRO-007",
      src=main_(r"""    int32:v = #lib_seven();
    discard(v);
    exit 0i32;""", r"""
use "./maclib.npk".*;"""),
      files={"maclib.npk": r"""mod:maclib;

pub macro:lib_seven = () { 7i32; };

pub func:anchor = int32() never fails { pass 0i32; };"""},
      wrong="accepted (the macro crosses modules), or refused as unknown (MACRO-001)")

claim("mc0266", D, 266, "`MACRO-008` if it is `#caller`", "rule",
      "A `#caller(...)` left standing in an ordinary function (outside any macro) is NITPICK-MACRO-008.",
      expect="refuse:NITPICK-MACRO-008",
      src=main_(r"""    int32:r = raw plain_fn(2i32);
    discard(r);
    exit 0i32;""", r"""
func:plain_fn = int32(int32:k) never fails { pass #caller(k); };"""),
      wrong="accepted: `#caller(k)` read as `k`")

claim("mc0266b", D, 266, "Only the three", "rule",
      "Only the three compiler builtins survive expansion.",
      untestable="[vague] the text does not name the three builtins, and the references use more than three "
                 "`#` builtins (`#size_of`, `#align_of`, `#wild_ptr`, `#unreachable`, `#sqrt`, `#caller`), so "
                 "no program can tell which one the sentence says is refused")

claim("mc0270", D, 270, "`#totally_not_a_macro(3i32)` used to compile clean", "rule",
      "`#totally_not_a_macro(3i32)` in expression position is refused as NITPICK-MACRO-001 (it used to "
      "compile clean).",
      expect="refuse:NITPICK-MACRO-001",
      src=main_(r"""    int32:v = #totally_not_a_macro(3i32);
    discard(v);
    exit 0i32;"""),
      wrong="accepted silently (the INVALID-type path)")

claim("mc0278", D, 278, "the scan afterwards cannot", "rule",
      "The expansion walk reaches every statement kind (a miss would arrive as a refusal): invocations in an "
      "if condition, a while condition and measure, a for body, a pick arm, a when body and then block, a "
      "nested block, a struct literal, an array literal, a call argument and a give all expand.",
      expect="run:0",
      src=main_(r"""    int32:n = 0i32;
    if (#one() == 1i32) { n = n + #one(); }
    while (n < #three()) decreases #three() - n { n = n + #one(); }
    for (int64:i in 0i64...3i64) { n = n + #one(); discard(i); }
    pick (n) { (6i32) { n = n + #one(); }, (*) { exit 20i32; } }
    when (n < 9i32) decreases 9i32 - n { n = n + #one(); } then { n = n + #one(); } end { exit 21i32; }
    { n = n + #one(); }
    n = n + (raw add_one_to(#one()));
    Pt:p = Pt{ x: #one(), y: #three() };
    int32[2]:arr = [#one(), #three()];
    int32:g = pick (n) { (13i32) { give #one(); }, (*) { give 0i32; } };
    if (n != 13i32) { exit 10i32; }
    if ((p.x + p.y) != 4i32) { exit 11i32; }
    if (arr[1i64] != 3i32) { exit 12i32; }
    if (g != 1i32) { exit 13i32; }
    exit 0i32;""", r"""
macro:one = () { 1i32; };
macro:three = () { 3i32; };

struct:Pt = { int32:x; int32:y; };

func:add_one_to = int32(int32:a) never fails { pass (a + #one()); };"""),
      wrong="a refusal naming an invocation in a statement kind the walk missed, or a wrong count (10-13, 20, 21)")

claim("mc0281", D, 281, "A macro body is exempt", "rule",
      "A macro body is exempt from the leftover-invocation scan: an unknown invocation inside a macro that is "
      "never invoked is not refused.",
      expect="run:0",
      src=main_(r"""    exit 0i32;""", r"""
macro:never_used = () { #not_declared_anywhere(1i32); };"""),
      wrong="refused: the template's invocation treated as standing in the program")

# ---- 8. comptime ---------------------------------------------------------------------
claim("mc0290", D, 290, "```nitpick", "example",
      "`comptime func:double` is a callable; `comptime(double(21i32))` forces it: 42.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(double(21i32));                            // a forcing form
    if (v != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
comptime func:double = int32(int32:n) { pass (n * 2i32); };   // a callable"""),
      wrong="refused, or a wrong value (exit 10)")

claim("mc0296", D, 296, "is a **keyword operator with a parenthesised operand**", "rule",
      "`comptime(expr)` is a keyword operator, not a call: its value is the plain int32, used with no `raw`.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(6i32 * 7i32);
    if (v != 42i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused as a call to an unknown function `comptime`, or typed as a Result")

claim("mc0296b", D, 296, "keyword operator with a parenthesised operand", "rule",
      "The operand of `comptime` is parenthesised: `comptime 42i32` without parentheses is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = comptime 42i32;
    discard(v);
    exit 0i32;"""),
      wrong="accepted: `comptime` read as a prefix operator")

claim("mc0305", D, 305, "| integer arithmetic | throughout |", "row",
      "The comptime evaluator does integer arithmetic as the language does: `/`, `%` and negation agree with "
      "the run-time result for -7 and 2.",
      expect="run:0",
      src=main_(r"""    int32:c = comptime(arith(-7i32, 2i32));
    int32:r = raw arith_rt(raw v32(-7i32), raw v32(2i32));
    if (c != r) { exit 10i32; }
    if (c != -317i32) { exit 11i32; }
    exit 0i32;""", r"""
comptime func:arith = int32(int32:a, int32:b) { pass ((a / b) * 100i32 + (a % b) * 10i32 - (0i32 - a)); };
func:arith_rt = int32(int32:a, int32:b) never fails { pass ((a / b) * 100i32 + (a % b) * 10i32 - (0i32 - a)); };"""),
      wrong="the evaluator disagrees with the run time (exit 10); -397 would be floor division (exit 11)")

claim("mc0306", D, 306, "**mutable locals and assignment**", "row",
      "The evaluator supports mutable locals and assignment, `x = x + n` and chains of them: accum(7) = 35.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(accum(7i32));
    if (v != 35i32) { exit 10i32; }
    exit 0i32;""", r"""
comptime func:accum = int32(int32:n) {
    int32:x = 0i32;
    x = x + n;
    x = x + n;
    int32:y = x;
    y = y + x + n;
    pass y;
};"""),
      wrong="refused (no mutable locals), or an assignment lost (exit 10)")

claim("mc0307", D, 307, "**loops** — `loop(lo, hi, step) { … }`", "row",
      "The evaluator runs `loop(lo, hi, step)`: a comptime sum over loop(0, 10, 3) equals the same loop "
      "run at run time.",
      expect="run:0",
      src=main_(r"""    int64:c = comptime(sum_step(0i64, 10i64));
    int64:r = raw sum_step_rt(raw v64(0i64), raw v64(10i64));
    if (c != r) { exit 10i32; }
    if (c == 0i64) { exit 11i32; }
    exit 0i32;""", r"""
comptime func:sum_step = int64(int64:lo, int64:hi) {
    int64:t = 0i64;
    loop(lo, hi, 3i64) { t = t + $; }
    pass t;
};
func:sum_step_rt = int64(int64:lo, int64:hi) never fails {
    int64:t = 0i64;
    loop(lo, hi, 3i64) { t = t + $; }
    pass t;
};"""),
      wrong="refused (no loops), or a count that disagrees with the run time (exit 10)")

claim("mc0308", D, 308, "calls to `comptime func:` declarations, nested", "row",
      "The evaluator follows nested calls between comptime functions: sum_sq(3, 4) = 25.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(sum_sq(3i32, 4i32));
    if (v != 25i32) { exit 10i32; }
    exit 0i32;""", r"""
comptime func:sq = int32(int32:n) never fails { pass (n * n); };
comptime func:sum_sq = int32(int32:a, int32:b) { pass ((raw sq(a)) + (raw sq(b))); };"""),
      wrong="refused (no nested calls), or a wrong value (exit 10)")

claim("mc0309", D, 309, "**strings** — concatenation, equality, ordering, length", "row",
      "The evaluator handles string concatenation, equality and length: len(\"ab\" ++ \"cde\") = 5 and "
      "\"ab\" ++ \"c\" equals \"abc\".",
      expect="run:0",
      src=main_(r"""    int64:n = comptime(str_len());
    bool:e = comptime(str_eq());
    if (n != 5i64) { exit 10i32; }
    if (!e) { exit 11i32; }
    exit 0i32;""", r"""
comptime func:str_len = int64() { pass string_byte_length(string_concat("ab", "cde")); };
comptime func:str_eq = bool() { pass string_equals(string_concat("ab", "c"), "abc"); };"""),
      wrong="refused (strings not evaluable), or a wrong length (10) or equality (11)")

claim("mc0309b", D, 309, "ordering", "row",
      "The evaluator handles string ordering: \"ab\" orders before \"b\".",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(str_order());
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", r"""
error:E9;

comptime func:str_order = int32() {
    string:a = "ab";
    string:b = "b";
    Ordering:o = a.cmp(b) ?! E9;
    pick (o) { (Ordering.Less) { pass 1i32; }, (*) { pass 2i32; } }
};"""),
      wrong="refused (ordering not evaluable), or a length-first order (exit 10)",
      note="ordering spelled `a.cmp(b)`, the current string ordering (TYPE_REFERENCE:364, D-257)")

claim("mc0310", D, 310, "size and alignment intrinsics", "row",
      "The evaluator folds the size intrinsic: `comptime(#size_of<int64>())` is 8.",
      expect="run:0",
      src=main_(r"""    int64:s = comptime(#size_of<int64>());
    if (s != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or a wrong size (exit 10)")

claim("mc0310b", D, 310, "| size and alignment intrinsics |", "row",
      "The evaluator folds the alignment intrinsic: `comptime(#align_of<int64>())` is 8.",
      expect="run:0",
      src=main_(r"""    int64:a = comptime(#align_of<int64>());
    if (a != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no alignment intrinsic), or a wrong alignment (exit 10)",
      note="`#align_of` is spelled only in MACRO_REFERENCE:369 and no compiler test at HUNT2 uses it")

claim("mc0311", D, 311, "built-in macros inside `comptime(…)`", "row",
      "Built-in `#` forms are evaluated inside `comptime(…)`: `comptime(#size_of<int32>() * 2i64)` is 8.",
      expect="run:0",
      src=main_(r"""    int64:v = comptime(#size_of<int32>() * 2i64);
    if (v != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or a wrong value (exit 10)")

claim("mc0312", D, 312, "`assert_static comptime(…)`", "row",
      "`assert_static comptime(…)` is evaluated: a true proposition compiles.",
      expect="run:0",
      src=main_(r"""    assert_static comptime(nine());
    exit 0i32;""", r"""
comptime func:nine = bool() { pass ((3i32 * 3i32) == 9i32); };"""),
      wrong="refused: the spelling or the evaluation")

claim("mc0312b", D, 312, "short-circuiting to the verifier", "row",
      "`assert_static comptime(…)` over a false proposition halts compilation.",
      expect="refuse",
      src=main_(r"""    assert_static comptime(not_nine());
    exit 0i32;""", r"""
comptime func:not_nine = bool() { pass ((3i32 * 3i32) == 10i32); };"""),
      wrong="accepted: the assertion not evaluated")

claim("mc0315", D, 315, "executes loops and mutates locals", "rule",
      "The evaluator is an interpreter: it runs a `while` loop that mutates locals: tri(10) = 55.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(tri(10i32));
    if (v != 55i32) { exit 10i32; }
    exit 0i32;""", r"""
comptime func:tri = int32(int32:n) {
    int32:i = 0i32;
    int32:t = 0i32;
    while (i < n) decreases n - i { i = i + 1i32; t = t + i; }
    pass t;
};"""),
      wrong="refused (a constant folder, not an interpreter), or a wrong value (exit 10)")

claim("mc0316", D, 316, "the compiler runs at build time", "rule",
      "What `comptime(...)` expresses runs at build time: the emitted IR carries no call to the comptime function.",
      expect=r"ir!:call[^\n]*@[\w.$]*tri_ct",
      src=main_(r"""    int32:v = comptime(tri_ct(10i32));
    exit v - 55i32;""", r"""
comptime func:tri_ct = int32(int32:n) {
    int32:i = 0i32;
    int32:t = 0i32;
    while (i < n) decreases n - i { i = i + 1i32; t = t + i; }
    pass t;
};"""),
      wrong="the call emitted and run at run time")

claim("mc0321", D, 321, "```nitpick", "example",
      "Macros and comptime both ways: a macro body containing comptime (#four() = 4), comptime over an "
      "invocation (6), and nested arbitrarily (21).",
      expect="run:0",
      src=main_(r"""    int64:a = comptime(#double_it(3i32));            // comptime over a macro invocation
    int64:b = comptime(#add_one(#double_it(10i32))); // nested arbitrarily
    int32:c = #four();
    if (a != 6i64) { exit 10i32; }
    if (b != 21i64) { exit 11i32; }
    if (c != 4i32) { exit 12i32; }
    exit 0i32;""", r"""
macro:four = () { comptime(2i32 * 2i32); };      // a macro body containing comptime
macro:double_it = (V) { ((V * 2i32) => int64); };
macro:add_one = (V) { V + 1i64; };"""),
      wrong="refused, or a wrong value (10-12)",
      note="#double_it and #add_one are not declared by the example; declared here so the example's lines "
           "type as written (an int32 argument, an int64 result)")

claim("mc0327", D, 327, "expansion runs to a fixed point first, then evaluation", "rule",
      "Expansion runs to a fixed point first, then evaluation runs over the result: a comptime function "
      "EMITTED by a macro can be evaluated.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(sq_e(7i32));
    if (v != 49i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:mk_sq = () { comptime func:sq_e = int32(int32:n) { pass (n * n); }; };

#mk_sq();"""),
      wrong="refused: sq_e unknown to the evaluator")

claim("mc0332", D, 332, "A `const` global folds", "rule",
      "A `const` global folds: `comptime(N * 2i32)` over `const int32:N = 4i32;` is 8.",
      expect="run:0",
      src=main_(r"""    int32:v = comptime(N * 2i32);
    if (v != 8i32) { exit 10i32; }
    exit 0i32;""", r"""
const int32:N = 4i32;"""),
      wrong="refused: the const global not a constant",
      note="Reasoned, not measured: D-222 retired `const` (AST_REFERENCE:505 says so), so this sentence and "
           "D-130's table may be stale.")

claim("mc0334", D, 334, "A `fixed`", "rule",
      "A `fixed` binding is not a constant: `comptime(F * 2i32)` over `fixed int32:F` is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = comptime(F * 2i32);
    discard(v);
    exit 0i32;""", r"""
fixed int32:F = 4i32;"""),
      wrong="accepted: the fixed binding folded")

claim("mc0336", D, 336, "local or a parameter of an ordinary function", "rule",
      "A local is not a constant: `comptime(loc + 1i32)` is refused.",
      expect="refuse",
      src=main_(r"""    int32:loc = 3i32;
    int32:v = comptime(loc + 1i32);
    discard(v);
    exit 0i32;"""),
      wrong="accepted: the local folded")

claim("mc0336b", D, 336, "a parameter of an ordinary function", "rule",
      "A parameter of an ordinary function is not a constant: `comptime(p + 1i32)` is refused.",
      expect="refuse",
      src=main_(r"""    int32:r = raw f(1i32);
    discard(r);
    exit 0i32;""", r"""
func:f = int32(int32:p) never fails {
    int32:v = comptime(p + 1i32);
    pass v;
};"""),
      wrong="accepted: the parameter folded")

claim("mc0338", D, 338, "a call folds when the function is declared `comptime`", "rule",
      "A call folds only when the function is declared comptime: `comptime(four_rt())` over an ordinary "
      "(foldable) function is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = comptime(four_rt());
    discard(v);
    exit 0i32;""", r"""
func:four_rt = int32() never fails { pass 4i32; };"""),
      wrong="accepted: an ordinary function run at compile time because it happened to be foldable")

claim("mc0344", D, 344, "The diagnostic names **the offending expression**", "rule",
      "A comptime failure inside nested comptime calls names the offending expression and the call chain: "
      "the diagnostic mentions inner_div and outer_call and points at the division.",
      expect="sh:0",
      sh=_sh(r"""mod:p;
comptime func:inner_div = int32(int32:d) never fails { pass (100i32 / d); };
comptime func:outer_call = int32(int32:d) never fails { pass (raw inner_div(d)); };
func:main = int32(cstring[]:_~argv) {
    int32:v = comptime(outer_call(0i32));
    exit v;
};
""" + failsafe_text(""), r"""
[ "$rc" -eq 1 ] || exit 2
printf '%s\n' "$out" | grep -q 'inner_div' || exit 3
printf '%s\n' "$out" | grep -q 'outer_call' || exit 4
printf '%s\n' "$out" | grep -qE 'p\.npk:2:|100i32 / d' || exit 5
exit 0"""),
      wrong="accepted (2), no chain named (3, 4), or the offending expression not located (5)")

claim("mc0346", D, 346, "A comptime failure is a compile error.", "rule",
      "A comptime evaluation that fails (division by zero inside a comptime function) is a compile error.",
      expect="refuse",
      src=main_(r"""    int32:v = comptime(dz(0i32));
    discard(v);
    exit 0i32;""", r"""
comptime func:dz = int32(int32:d) { pass (100i32 / d); };"""),
      wrong="accepted: folded to a value, or deferred to a run-time trap")

claim("mc0351", D, 351, "A budget bounds the total work", "rule",
      "A budget bounds the total work: a comptime loop that never ends is NITPICK-TYPE-025.",
      expect="refuse:NITPICK-TYPE-025",
      src=main_(r"""    int32:a = comptime(spin(1i32));
    discard(a);
    exit 0i32;""", r"""
comptime func:spin = int32(int32:n) {
    int32:i = 0i32;
    while (i >= 0i32) unbounded { i = i + 1i32; i = i - 1i32; }
    pass (i + n);
};"""),
      wrong="the build never finishes, or another code")

claim("mc0352", D, 352, "a `comptime func:` that calls itself", "rule",
      "A depth bound bounds recursion: a comptime function that calls itself forever is NITPICK-TYPE-025, "
      "not a crashed compiler.",
      expect="refuse:NITPICK-TYPE-025",
      src=main_(r"""    int32:a = comptime(forever(1i32));
    discard(a);
    exit 0i32;""", r"""
comptime func:forever = int32(int32:n) never fails { pass (raw forever(n)); };"""),
      wrong="the checker's stack exhausted (a crash), or another code")

claim("mc0356", D, 356, "Exceeding either is `NITPICK-TYPE-025`", "rule",
      "Exceeding either evaluation bound is NITPICK-TYPE-025: two comptime functions recursing into each "
      "other are refused with it.",
      expect="refuse:NITPICK-TYPE-025",
      src=main_(r"""    int32:a = comptime(ping_c(0i32));
    discard(a);
    exit 0i32;""", r"""
comptime func:ping_c = int32(int32:n) never fails { pass (raw pong_c(n + 1i32)); };
comptime func:pong_c = int32(int32:n) never fails { pass (raw ping_c(n + 1i32)); };"""),
      wrong="a crash or a hang, or 'not a constant' instead of TYPE-025")

# ---- 9. The corpus's dialect ---------------------------------------------------------
claim("mc0368", D, 368, "| `impl:Trait:for:Type` | `impl:Type:Trait` | D-030 |", "row",
      "The corpus's `impl:Trait:for:Type` is not this language: it is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
struct:Box = { int32:n; };
trait:Pair = { func:add_one = int32(Self:self); };

impl:Pair:for:Box = { func:add_one = int32(Box:self) { pass (self.n + 1i32); }; };"""),
      wrong="accepted: the connector form still parses as an impl")

claim("mc0368b", D, 368, "`impl:Type:Trait`", "row",
      "This language writes `impl:Type:Trait`.",
      expect="run:0",
      src=main_(r"""    Box:b = Box{ n: 41i32 };
    if ((b.add_one() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
struct:Box = { int32:n; };
trait:Pair = { func:add_one = int32(Self:self); };

impl:Box:Pair = { func:add_one = int32(Box:self) { pass (self.n + 1i32); }; };"""),
      wrong="refused, or a wrong value (exit 10)")

claim("mc0369", D, 369, "| `@sizeof(T)`, `@alignof(T)` |", "row",
      "The corpus's `@sizeof(T)` is not this language (`@` is address-of and nothing else): it is refused.",
      expect="refuse",
      src=main_(r"""    int64:s = @sizeof(int32);
    discard(s);
    exit 0i32;"""),
      wrong="accepted: `@sizeof` still a builtin")

claim("mc0369b", D, 369, "`#size_of<T>()`", "row",
      "This language writes `#size_of<T>()`: `#size_of<int64>()` is 8.",
      expect="run:0",
      src=main_(r"""    if (#size_of<int64>() != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or a wrong size (exit 10)")

claim("mc0369c", D, 369, "`#align_of<T>()`", "row",
      "This language writes `#align_of<T>()`: `#align_of<int64>()` is 8.",
      expect="run:0",
      src=main_(r"""    if (#align_of<int64>() != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (no such builtin), or a wrong alignment (exit 10)",
      note="`#align_of` is spelled only here in the references and in no compiler test at HUNT2")

claim("mc0370", D, 370, "| `expr ? default` | the defaults operator |", "row",
      "The corpus's `expr ? default` is respelled: a bare `?` fallback is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = k() ? 7i32;
    discard(v);
    exit 0i32;""", r"""
error:E1;
func:k = int32() { fail E1; };"""),
      wrong="accepted: the bare `?` still a fallback",
      note="AST_REFERENCE:413 lists `e ? d` as the SafeUnwrapExpr spelling; as0413 tests that reading")

claim("mc0371", D, 371, "| `0`, `10`, `exit 1` |", "row",
      "The corpus's width-less literals (`0`, `10`, `exit 1`) are not this language: they are refused "
      "(literals carry their width).",
      expect="refuse",
      src=main_(r"""    int32:z = 0;
    int32:t = 10;
    discard(z);
    discard(t);
    exit 1;"""),
      wrong="accepted: the unsuffixed literals typed by context (the program exits 1)",
      note="TENSION (reasoned): D-092, which the row cites, types an unsuffixed literal by the position it "
           "stands in (M10 c19 measured it accepted), so the row may overstate the difference.")

claim("mc0372", D, 372, "| `func:main = int32()` |", "row",
      "The corpus's `func:main = int32()` is not this language: a main with no parameter is refused.",
      expect="refuse",
      src=r"""func:main = int32() { exit 0i32; };
""",
      wrong="accepted")

claim("mc0372b", D, 372, "`func:main = int32(cstring[]:argv)`", "row",
      "This language writes `func:main = int32(cstring[]:argv)`.",
      expect="run:0",
      src=r"""func:main = int32(cstring[]:argv) { exit 0i32; };
""",
      wrong="refused (an unread named parameter), or a nonzero exit")

claim("mc0373", D, 373, "| `name!(args)` — the invocation | **`#name(args)`** |", "row",
      "The corpus's invocation `name!(args)` is not this language: `make_pair!();` at module level is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:make_pair = () {
    func:greet1 = int32() never fails { pass 7i32; };
};

make_pair!();"""),
      wrong="accepted: the postfix-! invocation still expands")

claim("mc0374", D, 374, "| `MacroPattern` in a `pick` arm | **removed** |", "row",
      "A MacroPattern in a pick arm (the corpus's `MyMacro!(a, b) where (a > b) { … }`) is removed: refused.",
      expect="refuse",
      src=main_(r"""    int32:ast_node = raw v32(3i32);
    int32:r = 0i32;
    pick (ast_node) {
        my_macro!(a, b) where (a > b) { r = 1i32; },
        (*) { r = 2i32; }
    }
    discard(r);
    exit 0i32;""", r"""
macro:my_macro = (a, b) { a + b; };"""),
      wrong="accepted: a pattern matching macro invocations",
      note="the spelling is CONTROL_REFERENCE:80-84's, the one place a MacroPattern is written; that section "
           "still presents it as current (a cross-reference contradiction)")

claim("mc0379", D, 379, "there is no postfix `!` in the grammar", "rule",
      "There is no postfix `!`: `twice!(3i32)` in expression position is refused.",
      expect="refuse",
      src=main_(r"""    int32:v = twice!(3i32);
    discard(v);
    exit 0i32;""", r"""
macro:twice = (V) { V * 2i32; };"""),
      wrong="accepted: `twice!(…)` expands")

# ---- 10. What the corpus does not settle ---------------------------------------------
claim("mc0388", D, 388, "the emitted function is literally called", "rule",
      "Substitution does not reach a declaration's name: `macro:m = (N) { func:N = …; };` emits a function "
      "literally named N (unimplemented rather than refused).",
      expect="run:0",
      src=main_(r"""    if ((raw N()) != 5i32) { exit 10i32; }
    exit 0i32;""", r"""
macro:m = (N) { func:N = int32() never fails { pass 5i32; }; };

#m(7i32);"""),
      wrong="refused, or the name substituted (N unresolved)")

claim("mc0393", D, 393, "a macro never renames what", "rule",
      "A macro never renames what it emits: a spliced method keeps its name and so satisfies the trait "
      "it implements.",
      expect="run:0",
      src=main_(r"""    Box:b = Box{ n: 41i32 };
    if ((b.add_one() ?| 0i32) != 42i32) { exit 10i32; }
    exit 0i32;""", r"""
struct:Box = { int32:n; };
trait:Pair = { func:add_one = int32(Self:self); };

macro:emit_methods = () { func:add_one = int32(Box:self) { pass (self.n + 1i32); }; };

impl:Box:Pair = { #emit_methods(); };"""),
      wrong="refused: a renamed method leaves the trait unsatisfied")

claim("mc0394", D, 394, "a collision is an error like any other name declared", "rule",
      "Two module-level invocations of one declaration macro emit one name twice: a collision is an error.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:one_fn = () { func:dup_fn = int32() never fails { pass 1i32; }; };

#one_fn();
#one_fn();"""),
      wrong="accepted: the emitted names renamed, or the second silently shadowing the first")

claim("mc0394b", D, 394, "it emits** (D-128)", "rule",
      "Two splices of one field macro into one struct collide: refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""
macro:one_x = () { int32:x; };

struct:P = { #one_x(); #one_x(); };"""),
      wrong="accepted: a struct with two x fields, the second unreachable")

claim("mc0405", D, 405, "currently carries the macro's", "rule",
      "A diagnostic inside an expansion carries the macro body's location: \"cannot find only_local\" is "
      "reported at the macro BODY's line, not the invocation's.",
      expect="sh:0",
      sh=_sh(r"""mod:p;
macro:grab = () { only_local + 1i32; };
func:main = int32(cstring[]:_~argv) {
    int32:only_local = 3i32;
    int32:s = #grab();
    exit 0i32;
};
""" + failsafe_text(""), r"""
[ "$rc" -eq 1 ] || exit 2
first=$(printf '%s\n' "$out" | grep -m1 'NITPICK-')
echo "first: $first"
printf '%s\n' "$first" | grep -q 'p\.npk:2:' || exit 3
exit 0"""),
      wrong="accepted (2), or the first diagnostic placed elsewhere, e.g. at the invocation's line 5 (3)",
      note="the sentence also says 0.6.6 will add the invocation's location; only the body's location is "
           "checked (a note pointing at line 5 as well does not fail this)")


# ------------------------------------------------------------------ after the runs (S45, S53)
# mc0312b AGREED for another reason: `assert_static comptime(...)` is refused for its spelling
# (PARSE-001, the parentheses; mc0312's documentation row), not for its false proposition. Its
# TEXT now uses the parenthesised spelling, so the refusal it expects is the proposition's.
refix("mc0312b", "it agreed for another reason: `assert_static comptime(...)` is refused for its "
      "spelling (PARSE-001; mc0312's row), so the program now writes `assert_static(comptime(...))` "
      "and the refusal it expects is the false proposition's",
      [("    assert_static comptime(not_nine());", "    assert_static(comptime(not_nine()));")])
