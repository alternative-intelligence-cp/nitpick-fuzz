"""M11 claims: AST_REFERENCE.md (lines 1-644) at HUNT2 (9126350), extracted by session 9.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). Where an M10 item tests exactly the claim, the claim
links it (`m10=`).

The reference lists the parser's node kinds. A row that only lists a node's fields is
`internal`. A row or a note that states a spelling, a placement rule or a run-time
rule is tested by a program in that spelling. The `extern` scripts are MODULE's
(S61): HUNT2's block form, with the compiler's `lib/nbridge.npk` and `lib/nsys.npk`
copied beside the program, and a failsafe naming nbridge's ten constants.
"""
from m11lib import *

covers("AST", 1)

D = "AST"
FS = failsafe_text("")


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


K = "func:k = int32(int32:x) { pass x; };"            # a fallible identity
G = "func:g = int32(int32:x) never fails { pass x; };"  # a never-fails identity

# ---- the extern scripts (MODULE's helpers, S61)
SH_LIB = r'''refused() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 1 ] || return 1
    ! grep -q 'NITPICK-EMIT-002' npkc.out || return 1
    [ -z "$2" ] || grep -q -- "$2" npkc.out
}
accepted() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 0 ] && [ -s p.ll ]
}
'''
NB = ('cp "$(dirname "$NPKC")/../../lib/nbridge.npk" "$(dirname "$NPKC")/../../lib/nsys.npk" . || exit 5\n')
NB_ERRS = ("EShmCreate", "EShmSeal", "EShmMap", "EDriverSpawn", "EDriverProtocol", "EDriverFault",
           "EDriverDeadline", "ERingFull", "EBridgePoisoned", "EDriverError")
NB_FS = failsafe_with("".join("        (%s) { exit %di32; },\n" % (n, 60 + i) for i, n in enumerate(NB_ERRS)))


def ext_sh(block, accept=True):
    prog = ('mod:r;\nuse "./nbridge.npk".*;\n\n' + block.strip() + "\n\n" + main_("    exit 0i32;") + "\n" + NB_FS)
    return (SH_LIB + NB + "cat > r.npk <<'EOF'\n" + prog.rstrip() + "\nEOF\n" +
            ("accepted r.npk" if accept else "refused r.npk"))


SPEAKS = """trait:Speaks = { func:say = int32(Self:self); };
struct:Loud = { string:name; int32:v; };
impl:Loud:Speaks = { func:say = int32(Loud:self) { pass self.v; }; };"""
SEQ = """trait:Seq = {
    assoc:Item;
    func:next = Item(Self:self);
};
struct:Counter = { int32:n; };
impl:Counter:Seq = {
    assoc:Item = int32;
    func:next = int32(Counter:self) { pass self.n; };
};
error:E9;
func:first<T: Seq> = T.Item(T:it) { pass (it.next()) ?! E9; };"""
SEQ_MAIN = """    Counter:c = Counter{ n: 4i32 };
    int32:v = first::<Counter>(c) ?| 0i32;
%s
    exit 0i32;""" % chk("v == 4i32", 10)

# ================================================================== 1. declarations
claim("as0032", D, 32, "**`mod:name = { … };`**, or **`mod:name;`** for a file (D-088)", "row",
      "A module is `mod:name = { … };` inline or `mod:name;` for a file: both compile and are reached.",
      expect="run:0",
      src=main_("""    int32:a = raw inl.f();
    int32:b = raw lib.f();
%s
    exit 0i32;""" % chk("a == 1i32 && b == 5i32", 10), """mod:inl = { pub func:f = int32() never fails { pass 1i32; }; };
mod:lib;"""),
      files={"lib.npk": "mod:lib;\npub func:f = int32() never fails { pass 5i32; };"},
      wrong="refused")
claim("as0033", D, 33, "`kind` ∈ wildcard / single / selective / namespace", "row",
      "An import is one of four kinds, wildcard, single, selective and namespace: all four compile.",
      expect="run:0",
      src=main_("""    int32:a = raw f();
    int32:b = raw h();
    int32:c = raw q.f();
%s
    exit 0i32;""" % chk("a == 5i32 && b == 6i32 && c == 5i32 && K2 == 7i32", 10),
                'use "./lib.npk".*;\nuse "./two.npk".h;\nuse "./two.npk".{K2};\nuse "./lib.npk" as q;'),
      files={"lib.npk": "mod:lib;\npub func:f = int32() never fails { pass 5i32; };",
             "two.npk": "mod:two;\npub func:h = int32() never fails { pass 6i32; };\npub fixed int32:K2 = 7i32;"},
      wrong="refused (a kind unknown)")
claim("as0034", D, 34, "the contracts window holds `requires`/`ensures`/`acquires`, the `never fails`", "row",
      "A function's contracts window holds `requires`, `ensures`, `never fails` and `pure` together.",
      expect="run:0",
      src=main_("""    int32:v = raw inc(raw v32(4i32));
%s
    exit 0i32;""" % chk("v == 5i32", 10),
                "func:inc = int32(int32:x) requires x >= 0i32 ensures result == x + 1i32 pure never fails "
                "{ pass (x + 1i32); };"),
      wrong="refused: a clause not admitted with the others")
claim("as0035", D, 35, "| `StructDecl` | `name`, `visibility`, `generics`, `fields: FieldDecl[]`, `attributes` | |", "row",
      "The StructDecl node holds name, visibility, generics, fields and attributes.",
      untestable="[internal] the node's fields")
claim("as0036", D, 36, "variants may carry payloads", "row",
      "Enum variants may carry payloads: `Opt.Som(5i32)` matched by `(Som(x))` binds 5.",
      expect="run:0",
      src=main_("""    Opt:o = Opt.Som(raw v32(5i32));
    int32:r = 0i32;
    pick (o) { (Som(x)) { r = x; }, (Opt.Non) { r = 9i32; } }
%s
    exit 0i32;""" % chk("r == 5i32", 10), "enum:Opt = { Non; Som(int32); };"),
      wrong="refused, or 10")
claim("as0037", D, 37, "supertraits combine with **`&`** (D-029)", "row",
      "Supertraits combine with `&`: `trait:C = A & B & { … };` compiles, and a type implementing all "
      "three calls each.",
      expect="run:0",
      src=main_("""    S:s = S{ n: 1i32 };
%s
    exit 0i32;""" % chk("(raw s.a()) + (raw s.b()) + (raw s.c()) == 6i32", 10), """trait:A = { func:a = int32(Self:self) never fails; };
trait:B = { func:b = int32(Self:self) never fails; };
trait:C = A & B & { func:c = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:A = { func:a = int32(S:self) never fails { pass 1i32; }; };
impl:S:B = { func:b = int32(S:self) never fails { pass 2i32; }; };
impl:S:C = { func:c = int32(S:self) never fails { pass 3i32; }; };"""),
      wrong="refused: `&` not the supertrait combinator")
claim("as0038", D, 38, "**`impl:Type`** or **`impl:Type:Trait`**", "row",
      "`impl:Type` and `impl:Type:Trait` both compile: an inherent method and a trait method are called.",
      expect="run:0",
      src=main_("""    Loud:l = Loud{ name: string_concat("a", "b"), v: 7i32 };
%s
    exit 0i32;""" % chk("(raw l.twice()) == 14i32 && (l.say() ?| 0i32) == 7i32", 10),
                SPEAKS + "\nimpl:Loud = { func:twice = int32(Loud:self) never fails { pass (self.v * 2i32); }; };"),
      wrong="refused")
claim("as0038b", D, 38, "type always first, no connector (D-031)", "rule",
      "There is no connector: `impl Speaks for Loud` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """trait:Speaks = { func:say = int32(Self:self); };
struct:Loud = { int32:v; };
impl Speaks for Loud { func:say = int32(Loud:self) { pass self.v; }; }"""),
      wrong="accepted")
claim("as0039", D, 39, "`Rules<int32>:r = { $ > 0i32 }`", "row",
      "`Rules<int32>:r_pos = { $ > 0i32 };` declares a rule: a `limit<r_pos>` binding assigned -1 traps "
      "LimitViolated.",
      expect="trap:LimitViolated",
      src=main_("""    limit<r_pos> int32:x = raw v32(5i32);
    x = raw v32(-1i32);
    if (x < 0i32) { exit 10i32; }
    exit 11i32;""", "Rules<int32>:r_pos = { $ > 0i32 };"),
      wrong="10: the rule not checked")
claim("as0040", D, 40, "invoked as **`#name(args)`** (D-046)", "row",
      "A macro is invoked as `#name(args)`: an expression macro `#twice(4i32)` is 8.",
      expect="run:0",
      src=main_("""    int32:v = #twice(raw v32(4i32));
%s
    exit 0i32;""" % chk("v == 8i32", 10), "macro:twice = (x) { x * 2i32; };"),
      wrong="refused, or 10")
claim("as0041", D, 41, "an invocation standing **where a declaration is expected**", "row",
      "A declaration macro invoked at module level splices its declaration: the emitted function is called.",
      expect="run:0",
      src=main_("""    int32:v = raw emitted();
%s
    exit 0i32;""" % chk("v == 1i32", 10),
                "macro:mk = () { func:emitted = int32() never fails { pass 1i32; }; };\n#mk();"),
      wrong="refused: no splice at module level")
claim("as0042", D, 42, "**`extern:\"libc\" = { … };`** (D-088)", "row",
      "An extern block is named by a string: `extern:\"mockif\" = { … };` compiles (in HUNT2's method form).",
      expect="sh:0",
      sh=ext_sh("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within);
};"""),
      wrong="refused: the block's string name")
claim("as0043", D, 43, "**`extern`-block item only**", "row",
      "An `opaque struct` is an extern-block item only: one at module level is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "opaque struct:OpHandle;"),
      wrong="accepted outside an extern block")
claim("as0044", D, 44, "`pub const int32:MAX = 100i32;`", "row",
      "A global is declared `pub const int32:MAX = 100i32;`: MAX is 100.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("MAX == 100i32", 10), "pub const int32:MAX = 100i32;"),
      wrong="refused: `const` not the language's spelling")
claim("as0045", D, 45, "**`unit:Hertz = 1 / Seconds;`** (D-196, 1.3.3)", "row",
      "`unit:Hertz = 1 / Seconds;` declares a named unit for `dim256<U>`: a `dim256<Hertz>` value compiles.",
      expect="compile",
      src=main_("""    dim256<Hertz>:f = 2.0dim256<Hertz>;
    discard(f);
    exit 0i32;""", "unit:Hertz = 1 / Seconds;"),
      wrong="refused")
claim("as0045b", D, 45, "The RHS is unit algebra only", "rule",
      "A unit's right side is unit algebra only (names, `1`, `*`, `/`, parentheses): `Seconds + Seconds` is "
      "refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "unit:Bad = Seconds + Seconds;"),
      wrong="accepted")

# ------------------------------------------------------------------ 1.1 functions
claim("as0049", D, 49, "```", "example",
      "A FunctionDecl takes generics after the name, parameters, the success type, contracts and a body: "
      "`f::<int64>(1i64, 3i32)` is 3.",
      expect="run:0",
      src=main_("""    int32:v = raw f::<int64>(raw v64(1i64), raw v32(3i32));
%s
    exit 0i32;""" % chk("v == 3i32", 10),
                "func:f<T> = int32(T:_~x, int32:n) requires n >= 0i32 never fails { pass n; };"),
      wrong="refused, or 10")
claim("as0062", D, 62, "```", "example",
      "A generic parameter is a type or a compile-time value: `scale<comptime int32:K>` called "
      "`scale::<3i32>(2i32)` is 6.",
      expect="run:0",
      src=main_("""    int32:v = raw scale::<3i32>(raw v32(2i32));
%s
    exit 0i32;""" % chk("v == 6i32", 10),
                "func:scale<comptime int32:K> = int32(int32:x) never fails { pass (x * K); };"),
      wrong="refused, or 10")
claim("as0075", D, 75, "**Not to be confused with `type:T`**, which is an ordinary `ParamDecl` in a", "rule",
      "`type:T` is legal only in a `comptime` function: as a parameter of an ordinary function it is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:f = int32(type:T) never fails { pass 0i32; };"),
      wrong="accepted")
claim("as0079", D, 79, "**`ParamDecl` and `FieldDecl` carry memory qualifiers**", "rule",
      "A parameter carries a memory qualifier: `wild int8->:buf` as a parameter compiles.",
      expect="compile",
      src=main_("    exit 0i32;", "func:take = int64(wild int8->:buf) never fails { pass 0i64; };"),
      wrong="refused: the qualifier not read on a parameter")
claim("as0080", D, 80, "`wild int8->:buf` is a", "rule",
      "A field carries a memory qualifier: a struct field `wild int8->:buf;` compiles.",
      expect="compile",
      src=main_("    exit 0i32;", "struct:Holder = { wild int8->:buf; int64:n; };"),
      wrong="refused: the qualifier not read on a field")
claim("as0090", D, 90, "**Reading a discarded parameter is an error**", "rule",
      "Reading a parameter declared discarded (`int32:_~x`) is an error.",
      expect="refuse",
      src=main_("""    int32:v = raw f(raw v32(1i32));
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", "func:f = int32(int32:_~x) never fails { pass x; };"),
      wrong="accepted: the discard claim unchecked")
claim("as0092", D, 92, "checked as `NITPICK-TYPE-083` since 1.6.0 step 3c", "rule",
      "`main`'s arity is fixed: a `main` with no parameter is refused, NITPICK-TYPE-083.",
      expect="refuse:NITPICK-TYPE-083",
      src="func:main = int32() {\n    exit 0i32;\n};\n",
      wrong="accepted, or refused with another code")
claim("as0092b", D, 92, "the arity, the parameter's type and the `int32` return", "rule",
      "`main` returns `int32`: a `main` returning `int64` is refused, NITPICK-TYPE-083.",
      expect="refuse:NITPICK-TYPE-083",
      src="func:main = int64(cstring[]:_~argv) {\n    exit 0i32;\n};\n",
      wrong="accepted, or refused with another code")
claim("as0092c", D, 92, "`failsafe`'s shape is `NITPICK-TYPE-044`", "rule",
      "`failsafe`'s shape is fixed: a `failsafe` with two parameters is refused, NITPICK-TYPE-044.",
      expect="refuse:NITPICK-TYPE-044", fs=False,
      src=main_("    exit 0i32;") + "\nfunc:failsafe = int32(Error:e, int32:extra) {\n    pick (e) { (*) { exit 99i32; } }\n    exit 9i32;\n};\n",
      wrong="accepted, or refused with another code")
claim("as0093", D, 93, "`failsafe` sets the same precedent with `tbb32:err`", "rule",
      "`failsafe`'s one parameter is `tbb32:err`: a failsafe so declared compiles.",
      expect="compile", fs=False,
      src=main_("    exit 0i32;") + "\nfunc:failsafe = int32(tbb32:err) {\n    pick (err) { ERR: { exit 2i32; }, (*) { exit 3i32; } }\n    exit 9i32;\n};\n",
      wrong="refused: failsafe takes another parameter")
claim("as0095", D, 95, "`argc`: a slice carries its length (D-070)", "rule",
      "There is no `argc`: `main(int32:argc, cstring[]:argv)` is refused, NITPICK-TYPE-083.",
      expect="refuse:NITPICK-TYPE-083",
      src="func:main = int32(int32:argc, cstring[]:_~argv) {\n    exit 0i32;\n};\n",
      wrong="accepted, or refused with another code")
claim("as0098", D, 98, "implicitly, except `main` and `failsafe`", "rule",
      "Every function but `main` and `failsafe` returns `Result<T>`: a call binds as `Result<int32>`.",
      expect="run:0",
      src=main_("""    Result<int32>:r = k(raw v32(3i32));
    if (r.is_error) { exit 10i32; }
%s
    exit 0i32;""" % chk("r.value == 3i32", 11), K),
      wrong="refused")
claim("as0100", D, 100, "**`extern` is not a modifier here**", "rule",
      "`extern` is not a function modifier: `extern func:f = …` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "extern func:f = int32() { pass 1i32; };"),
      wrong="accepted")

# ------------------------------------------------------------------ variadics and sys
TOTAL = """func:total = int64(int64:base, ..*int64[]:rest) never fails {
    int64:acc = base;
    int64:i = 0i64;
    while (i < rest.len) decreases rest.len - i {
        acc = acc + rest[i];
        i = i + 1i64;
    }
    pass acc;
};"""
claim("as0105", D, 105, "```", "example",
      "A variadic parameter is `..*T[]`, a slice: `total(1, 2, 3)` is 6.",
      expect="run:0",
      src=main_("""    int64:t = raw total(1i64, 2i64, 3i64);
%s
    exit 0i32;""" % chk("t == 6i64", 10), TOTAL),
      wrong="refused, or 10")
claim("as0110", D, 110, "**One form: homogeneous.**", "rule",
      "A variadic tail is homogeneous: an `int32` among `int64` trailing arguments is refused.",
      expect="refuse",
      src=main_("""    int64:t = raw total(1i64, 2i64, raw v32(3i32));
    exit 0i32;""", TOTAL),
      wrong="accepted")
claim("as0120", D, 120, "**removed by D-053** along with the `fmt` type itself", "rule",
      "The format-directed form (a bare `..*` after a `fmt` parameter) is removed: refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:p = int32(fmt:f, ..*) never fails { pass 0i32; };"),
      wrong="accepted")
claim("as0124", D, 124, "The surviving consumer is the `sys` builtin", "rule",
      "`sys(CONST, ..*int64[])` is the surviving variadic: `sys(39i64)` (getpid) returns a positive pid.",
      expect="run:0",
      src=main_("""    Result<int64>:p = sys(39i64);
    if (p.is_error) { exit 10i32; }
%s
    exit 0i32;""" % chk("p.value > 0i64", 11)),
      wrong="refused, or 10/11")

# ------------------------------------------------------------------ 1.2 ExternFn
claim("as0128", D, 128, "```", "example",
      "An extern function's failure contract is REQUIRED: a method with none is a compile error.",
      expect="sh:0",
      sh=ext_sh("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within);
};""", accept=False),
      wrong="accepted with no failure contract")
claim("as0137", D, 137, "```", "example",
      "A failure contract is `fails on …` or `never fails`: an extern method declared `never fails` compiles.",
      expect="sh:0",
      sh=ext_sh("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within) never fails;
};"""),
      wrong="refused")
claim("as0145", D, 145, "**`FailsOn` and `NeverFails` are separate node kinds**", "rule",
      "FailsOn and NeverFails are separate node kinds.",
      untestable="[internal] the node kinds are the parser's")

# ------------------------------------------------------------------ 1.3 trait items
claim("as0157", D, 157, "**`assoc:Item;`** (D-028)", "row",
      "`assoc:Item;` declares an associated type in a trait, which an impl binds: `first(c)` reads it.",
      expect="run:0", src=main_(SEQ_MAIN, SEQ),
      wrong="refused")
claim("as0158", D, 158, "**`error:Name;`** (D-179): one declared error constant", "row",
      "`error:Name;` declares an error constant: a function fails with it and the caller's arm sees it.",
      expect="run:0",
      src=main_("""    Result<int32>:r = boom(raw v32(1i32));
    int32:c = 0i32;
    if (r.is_error) { pick (r.err) { (Boom) { c = 1i32; }, (*) { c = 2i32; } } }
%s
    exit 0i32;""" % chk("c == 1i32", 10), """error:Boom;
func:boom = int32(int32:v) { if (v > 0i32) { fail Boom; } pass v; };""") + "\n" +
          failsafe_with("        (Boom) { exit 80i32; },"),
      fs=False, wrong="refused, or 10")
claim("as0158b", D, 158, "The explicit-code form (`error:Name = 4102i32;`) is the prelude's alone", "rule",
      "The explicit-code form `error:Name = 4102i32;` is the prelude's alone: a program's is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "error:Boom = 4102i32;"),
      wrong="accepted")
claim("as0160", D, 160, "**`TraitMethod` is removed. A method in a trait body is an ordinary", "rule",
      "A trait method is an ordinary function: one with a body is a default, one without is a declaration "
      "the impl must give.",
      expect="run:0",
      src=main_("""    Loud:l = Loud{ name: string_concat("x", "y"), v: 3i32 };
%s
    exit 0i32;""" % chk("(raw l.hello()) == 7i32 && (raw l.say()) == 3i32", 10), """trait:Greets = {
    func:say = int32(Self:self) never fails;
    func:hello = int32(Self:self) never fails { pass 7i32; };
};
struct:Loud = { string:name; int32:v; };
impl:Loud:Greets = { func:say = int32(Loud:self) never fails { pass self.v; }; };"""),
      wrong="refused, or 10")

# ================================================================== 2. statements
claim("as0180", D, 180, "| `BlockStmt` | `stmts: Stmt[]` — introduces a scope |", "row",
      "A block introduces a scope: a local declared inside an `if` block is not visible after it.",
      expect="refuse",
      src=main_("""    if (raw vb(true)) { int32:t = 1i32; }
    int32:u = t;
    exit 0i32;"""),
      wrong="accepted")
for _ln, _q in ((181, "| `VarDeclStmt` |"), (182, "| `AssignStmt` |"), (184, "| `IfStmt` |"),
                (185, "| `PickStmt` |"), (190, "| `WhenStmt` |"), (191, "| `BreakStmt` |"),
                (192, "| `ContinueStmt` |"), (193, "| `PassStmt` |"), (194, "| `FailStmt` |")):
    claim("as%04d" % _ln, D, _ln, _q, "row", "The node's fields.",
          untestable="[internal] the node's fields; the construct itself is CONTROL's and TYPE's claims")
claim("as0183", D, 183, "a bare call discards a `Result` (`TYPE-039`)", "row",
      "A bare call statement that discards a `Result` is refused, NITPICK-TYPE-039.",
      expect="refuse:NITPICK-TYPE-039",
      src=main_("""    k(raw v32(1i32));
    exit 0i32;""", K),
      wrong="accepted: the Result dropped silently")
claim("as0183b", D, 183, "`drop f();` / `relay f();` / `f() ?! c;` / `f() ?\\| NIL;`", "rule",
      "The value-less statement forms compile: `drop g();`, `relay f();`, `f() ?! c;` and `f() ?| NIL;`.",
      expect="run:0",
      src=main_("""    drop note();
    nk() ?! E1;
    nk() ?| NIL;
    int32:v = outer() ?| 9i32;
%s
    exit 0i32;""" % chk("v == 0i32", 10), """error:E1;
func:note = NIL() never fails { pass NIL; };
func:nk = NIL() { pass NIL; };
func:outer = int32() { relay nk(); pass 0i32; };"""),
      wrong="refused (a form not admitted), or 10")
claim("as0186", D, 186, "| `WhileStmt` | `label: Ident?`", "row",
      "A `while` may carry a label: `break outer;` from an inner loop leaves the labelled one.",
      expect="run:0",
      src=main_("""    int32:n = raw v32(5i32);
    int32:hits = 0i32;
    outer: while (n > 0i32) decreases n {
        int32:m = 3i32;
        while (m > 0i32) decreases m {
            hits = hits + 1i32;
            if (hits == 2i32) { break outer; }
            m = m - 1i32;
        }
        n = n - 1i32;
    }
%s
    exit 0i32;""" % chk("hits == 2i32 && n == 5i32", 10)),
      wrong="refused, or 10 (the inner loop only)")
claim("as0187", D, 187, "| `ForStmt` |", "row",
      "A `for` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:s = 0i64;
    for (int64:i in 0i64...3i64) decreases 3i64 { s = s + i; }
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("as0188", D, 188, "| `LoopStmt` |", "row",
      "A `loop` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:s = 0i64;
    loop (0i64, 3i64, 1i64) decreases 3i64 { s = s + 1i64; }
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("as0189", D, 189, "| `TillStmt` |", "row",
      "A `till` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:s = 0i64;
    till (3i64, 1i64) decreases 3i64 { s = s + 1i64; }
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("as0195", D, 195, "| `ReturnStmt` | `result: Expr` — the literal `Result{…}` form only |", "row",
      "`return` takes the literal `Result{…}` form: `return Result{ value: 5i32, err: 0i32 };` returns 5.",
      expect="run:0",
      src=main_("""    int32:v = five() ?| 0i32;
%s
    exit 0i32;""" % chk("v == 5i32", 10), "func:five = int32() { return Result{ value: 5i32, err: 0i32 }; };"),
      wrong="refused, or 10")
claim("as0195b", D, 195, "the literal `Result{…}` form only", "rule",
      "`return` takes only the `Result{…}` literal: `return 5i32;` is refused.",
      expect="refuse",
      src=main_("""    int32:v = five() ?| 0i32;
    exit 0i32;""", "func:five = int32() { return 5i32; };"),
      wrong="accepted")
claim("as0196", D, 196, "| `ExitStmt` | `code: Expr` — legal only in `main` / `failsafe` |", "row",
      "`exit` is legal only in `main` and `failsafe`: one in another function is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw f();
    exit 0i32;""", "func:f = int32() never fails { exit 3i32; };"),
      wrong="accepted")
claim("as0197", D, 197, "| `TrapStmt` | `error: Expr` — `!!! errCode;` |", "row",
      "`!!! errCode;` traps to failsafe with that code: `!!! E1;` reaches failsafe's `E1` arm (81).",
      expect="run:81",
      src=main_("""    !!! E1;
    exit 10i32;""", "error:E1;"),
      wrong="10: the statement did nothing")
claim("as0198", D, 198, "| `DeferStmt` | `body: BlockStmt` |", "row",
      "A `defer` body runs at its scope's exit: the deferred write through a pointer is seen after the call.",
      expect="run:0",
      src=main_("""    int32:x = 0i32;
    int32:v = raw f(@x);
%s
    exit 0i32;""" % chk("x == 9i32 && v == 1i32", 10),
                "func:f = int32(int32->:p) never fails { defer { <-p = 9i32; } pass 1i32; };"),
      wrong="refused, or 10")
claim("as0199", D, 199, "`discard(e)` / `_~ e`", "row",
      "A value is discarded by `discard(e)` or `_~ e`: both compile.",
      expect="compile",
      src=main_("""    int32:a = raw v32(1i32);
    int32:b = raw v32(2i32);
    discard(a);
    _~ b;
    exit 0i32;"""),
      wrong="refused (a form unknown)")
claim("as0200", D, 200, "| `ProveStmt` | `condition: Expr` — **compile-time** obligation |", "row",
      "`prove` is a compile-time obligation.",
      untestable="[z3] a `prove` obligation is discharged by `npkg verify` with the pinned z3")
claim("as0201", D, 201, "| `AssertStaticStmt` | `condition: Expr` |", "row",
      "`assert_static(cond);` is a statement: a true condition compiles and runs.",
      expect="run:0",
      src=main_("""    assert_static(1i32 + 1i32 == 2i32);
    exit 0i32;"""),
      wrong="refused")
claim("as0201b", D, 201, "`AssertStaticStmt`", "rule",
      "`assert_static` of a false condition is refused at compile time.",
      expect="refuse",
      src=main_("""    assert_static(1i32 + 1i32 == 3i32);
    exit 0i32;"""),
      wrong="accepted")
claim("as0202", D, 202, "legal only in a `PickArm` body (§2.2)", "row",
      "`fall label;` is legal only in a pick arm: one in a plain block is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if (x == 1i32) { fall nowhere; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0203", D, 203, "| `GiveStmt` | `value: Expr` — `give e;`, legal only in a `PickArm` body (§2.2) |", "row",
      "`give e;` is legal only in a pick arm: one in a plain block is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if (x == 1i32) { give 5i32; }
    exit 0i32;"""),
      wrong="accepted")

# ------------------------------------------------------------------ notes carrying decisions
claim("as0207", D, 207, "**`ForStmt.binding` is a full `ParamDecl` with a required type.**", "rule",
      "A `for` binding needs its type: `for (i in 0i64...3i64)` is refused.",
      expect="refuse",
      src=main_("""    int64:s = 0i64;
    for (i in 0i64...3i64) { s = s + i; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0210", D, 210, "are **counted**, exposing the counter as `$`", "rule",
      "`loop` is counted and exposes its counter as `$`: the body sees `$` equal to 1 on some trip.",
      expect="run:0",
      src=main_("""    int64:seen = 0i64;
    loop (0i64, 3i64, 1i64) { if ($ == 1i64) { seen = seen + 1i64; } }
%s
    exit 0i32;""" % chk("seen == 1i64", 10)),
      wrong="refused, or 10")
claim("as0211", D, 211, "so `step` must be positive — a negative or zero step is a compile error", "rule",
      "A `loop` with a zero step is a compile error.",
      expect="refuse",
      src=main_("""    int64:n = 0i64;
    loop (0i64, 3i64, 0i64) { n = n + 1i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0211b", D, 211, "a negative or zero step", "rule",
      "A `loop` with a negative step is a compile error.",
      expect="refuse",
      src=main_("""    int64:n = 0i64;
    loop (3i64, 0i64, -1i64) { n = n + 1i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0212", D, 212, "Neither has an `end` block", "rule",
      "A `loop` has no `end` block: one is refused.",
      expect="refuse",
      src=main_("""    int64:n = 0i64;
    loop (0i64, 3i64, 1i64) { n = n + 1i64; } end { n = 0i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0213", D, 213, "**`WhenStmt.then_block` runs when the body executed at least once, *including*", "rule",
      "`when`'s `then` runs when the body ran at least once, including after a `break`; `end` does not.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(5i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x { if (x == 4i32) { break; } x = x - 1i32; } then { t = t + 1i32; } end { e = e + 1i32; }
%s
    exit 0i32;""" % chk("t == 1i32 && e == 0i32", 10)),
      wrong="10: `break` lowered to `end`")
claim("as0214", D, 214, "`end_block` runs only when the condition was false initially", "rule",
      "`when`'s `end` runs only when the condition was false at the start, and then `then` does not.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(0i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x { x = x - 1i32; } then { t = t + 1i32; } end { e = e + 1i32; }
%s
    exit 0i32;""" % chk("t == 0i32 && e == 1i32", 10)),
      wrong="10")
claim("as0223", D, 223, "**`DeferStmt` does not run on a trap** (D-014)", "rule",
      "A `defer` does not run on a trap: a division by zero traps DivByZero, though the pending defer "
      "would itself have trapped IntOverflow.",
      expect="trap:DivByZero",
      src=main_("""    int32:v = raw f(raw v32(0i32));
    exit 10i32;""", """func:f = int32(int32:d) never fails {
    defer { int8:z = raw v8(127i8) + 1i8; discard(z); }
    pass (10i32 / d);
};"""),
      wrong="IntOverflow (93): the defer ran on the trap")

# ------------------------------------------------------------------ 2.1 pick arms
claim("as0228", D, 228, "```", "example",
      "A pick arm may carry a `where` guard: a false guard passes to the next arm.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(1i32);
    int32:b = raw v32(2i32);
    int32:r = 0i32;
    pick (a) { (1i32) where (a > b) { r = 1i32; }, (1i32) { r = 2i32; }, (*) { r = 3i32; } }
%s
    exit 0i32;""" % chk("r == 2i32", 10)),
      wrong="refused, or 10")
claim("as0236", D, 236, "```", "example",
      "A pick pattern is a value, a range or a wildcard: 550 takes the `(500..599)` arm.",
      expect="run:0",
      src=main_("""    int32:c = raw v32(550i32);
    int32:r = 0i32;
    pick (c) { (200i32) { r = 1i32; }, (500i32..599i32) { r = 2i32; }, (*) { r = 3i32; } }
%s
    exit 0i32;""" % chk("r == 2i32", 10)),
      wrong="refused, or another arm (10)")
claim("as0239", D, 239, "StructDestructure(type, binds) // (MouseClick { x, y })", "rule",
      "A struct destructure pattern `(MouseClick { x, y })` binds the fields.",
      expect="run:0",
      src=main_("""    MouseClick:ev = MouseClick{ x: raw v32(3i32), y: 4i32 };
    int32:r = 0i32;
    pick (ev) { (MouseClick { x, y }) { r = x + y; } }
%s
    exit 0i32;""" % chk("r == 7i32", 10), "struct:MouseClick = { int32:x; int32:y; };"),
      wrong="refused, or 10")
claim("as0240", D, 240, "EnumDestructure(path, binds)   // (Net.Disconnect(reason))", "rule",
      "An enum destructure pattern is written with its path: `(Net.Disconnect(reason))` binds the payload.",
      expect="run:0",
      src=main_("""    Net:n = Net.Disconnect(raw v32(7i32));
    int32:r = 0i32;
    pick (n) { (Net.Disconnect(reason)) { r = reason; }, (Net.Up) { r = 1i32; } }
%s
    exit 0i32;""" % chk("r == 7i32", 10), "enum:Net = { Up; Disconnect(int32); };"),
      wrong="refused: the payload pattern is written unqualified")
claim("as0241", D, 241, "ErrPattern                     // ERR:", "rule",
      "`ERR:` matches the tbb error sentinel.",
      expect="run:0",
      src=main_("""    tbb8:t = ERR;
    int32:r = 0i32;
    pick (t) { (1tbb8) { r = 1i32; }, ERR: { r = 2i32; }, (*) { r = 3i32; } }
%s
    exit 0i32;""" % chk("r == 2i32", 10)),
      wrong="refused, or 10")
claim("as0246", D, 246, "**requires** an explicit `ERR:` arm", "rule",
      "A `pick` on a `tbb` selector requires an explicit `ERR:` arm; `(*)` may not absorb it.",
      m10="p12_tbb_pick_needs_err_arm")
claim("as0248", D, 248, "**There is no `Unreachable` pattern.**", "rule",
      "There is no `(!)` pattern: an arm written `(!)` is refused.",
      expect="refuse",
      src=main_("""    tbb8:t = raw vt8(1tbb8);
    int32:r = 0i32;
    pick (t) { (1tbb8) { r = 1i32; }, (!) { r = 2i32; }, (*) { r = 3i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("as0251", D, 251, "`#unreachable()`", "rule",
      "An arm believed unreachable has `#unreachable()` as its body, which traps when reached.",
      expect="trap:Unreachable",
      src=main_("""    int32:x = raw v32(2i32);
    pick (x) { (1i32) { exit 10i32; }, (*) { #unreachable(); } }
    exit 11i32;"""),
      wrong="11: the arm fell through")
claim("as0256", D, 256, "`pick` must be exhaustive", "rule",
      "A `pick` must be exhaustive.",
      m10="p10_int_pick_not_exhaustive")
claim("as0256b", D, 256, "A `pick` whose arms `give` is an **expression**", "rule",
      "A `pick` whose arms `give` is an expression: `int32:v = pick (y) { … };` initialises v.",
      expect="run:0",
      src=main_("""    int32:y = raw v32(2i32);
    int32:v = pick (y) { (1i32) { give 10i32; }, (2i32) { give 20i32; }, (*) { give 30i32; } };
%s
    exit 0i32;""" % chk("v == 20i32", 10)),
      wrong="refused, or 10")
claim("as0257", D, 257, "must additionally agree on one type across all arms", "rule",
      "An expression `pick`'s arms agree on one type: an `int32` arm and an `int64` arm are refused.",
      expect="refuse",
      src=main_("""    int32:y = raw v32(2i32);
    int32:v = pick (y) { (1i32) { give 10i32; }, (*) { give 30i64; } };
    exit 0i32;"""),
      wrong="accepted")
claim("as0267", D, 267, "a **semantic** restriction, not a syntactic one", "rule",
      "`give` outside a pick arm is refused by the checker, not the parser: the refusal is no PARSE code.",
      expect="sh:0",
      sh=SH_LIB + "cat > r.npk <<'EOF'\n" + ("mod:r;\n\n" + main_("""    int32:x = raw v32(1i32);
    if (x == 1i32) { give 5i32; }
    exit 0i32;""") + "\n" + FS + helpers_text("raw v32(")).rstrip() + "\nEOF\n" + """refused r.npk || exit 1
first=$(grep -m1 -o 'NITPICK-[A-Z]*-[0-9]*' npkc.out)
echo "first: $first"
case "$first" in NITPICK-PARSE-*) exit 1;; esac""",
      wrong="the parser's \"expected a statement\" (a PARSE code)")

# ================================================================== 3. expressions
claim("as0281", D, 281, "**suffix-form bases** (`FFhex`, `1T0t`, `2An`)", "row",
      "`FFhex` is a hex literal: an `int32` bound to it is 255.",
      expect="run:0",
      src=main_("""    int32:a = FFhex;
%s
    exit 0i32;""" % chk("a == 255i32", 10)),
      wrong="refused: `FFhex` is an identifier (D-147)")
claim("as0281b", D, 281, "`1T0t`, `2An`", "rule",
      "`1T0t` (balanced ternary) is 6 and `2An` (balanced nonary) is 17.",
      expect="run:0",
      src=main_("""    int32:a = 1T0t;
    int32:b = 2An;
%s
    exit 0i32;""" % chk("a == 6i32 && b == 17i32", 10)),
      wrong="refused, or 10")
claim("as0281c", D, 281, "A `dim256`-suffixed literal may carry a **`<UnitName>` tail**", "rule",
      "An integer `dim256` literal may carry a unit tail: `5dim256<Meters>` compiles.",
      expect="compile",
      src=main_("""    dim256<Meters>:d = 5dim256<Meters>;
    discard(d);
    exit 0i32;"""),
      wrong="refused")
claim("as0282", D, 282, "the `dim256` unit tail as on `IntLiteral`", "row",
      "A float `dim256` literal may carry a unit tail: `2.5dim256<Meters>` compiles.",
      expect="compile",
      src=main_("""    dim256<Meters>:d = 2.5dim256<Meters>;
    discard(d);
    exit 0i32;"""),
      wrong="refused")
claim("as0283", D, 283, "**not an integer** (D-005)", "row",
      "A character literal is not an integer: `int32:x = 'A';` is refused.",
      expect="refuse",
      src=main_("""    int32:x = 'A';
    exit 0i32;"""),
      wrong="accepted")
claim("as0284", D, 284, "| `StringLiteral` | escape-processed |", "row",
      "A string literal is escape-processed: `\"a\\tb\"` is three bytes, the second a tab.",
      expect="run:0",
      src=main_("""    string:s = "a\\tb";
%s
    exit 0i32;""" % chk("string_byte_length(s) == 3i64 && string_bytes(s)[1i64] == 9u8", 10)),
      wrong="refused, or 10")
claim("as0285", D, 285, "`r\"…\"` — no escape processing (D-024)", "row",
      "A raw string has no escape processing: `r\"a\\tb\"` is four bytes.",
      expect="run:0",
      src=main_("""    string:s = r"a\\tb";
%s
    exit 0i32;""" % chk("string_byte_length(s) == 4i64", 10)),
      wrong="refused, or 10")
claim("as0286", D, 286, "`\"\"\"…\"\"\"` — newlines preserved (D-024)", "row",
      "A block string preserves its newline.",
      expect="run:0",
      src=main_('''    string:s = """a
b""";
%s
    exit 0i32;''' % chk("string_byte_length(s) == 3i64 && string_bytes(s)[1i64] == 10u8", 10)),
      wrong="refused, or 10")
claim("as0287", D, 287, "| `BoolLiteral` | |", "row", "The BoolLiteral node.",
      untestable="[internal] the node; LEXICAL's lx0269 tests the literals")
claim("as0288", D, 288, "`NULL`, `NIL`, `ERR` — **not `unknown`**", "row",
      "`NULL`, `NIL` and `ERR` are sentinel literals, each binding where its type is expected.",
      expect="run:0",
      src=main_("""    int8->:p = NULL;
    int32?:o = NIL;
    tbb8:e = ERR;
    discard(p);
%s
    exit 0i32;""" % chk("o == NIL && is_err(e)", 10)),
      wrong="refused, or 10")
claim("as0289", D, 289, "| `TemplateLiteral` |", "row", "The TemplateLiteral node's parts.",
      untestable="[internal] the node's parts; LEXICAL's lx0383 and lx0387 test the literal")

# ------------------------------------------------------------------ 3.2 operators
claim("as0295", D, 295, "| `BinaryExpr` | `op`, `lhs`, `rhs` |", "row",
      "The binary operators compute (all of the row's but `<=>`, which is as0295b).",
      expect="run:0",
      src=main_("""    int32:a = raw v32(12i32);
    int32:b = raw v32(5i32);
%s
%s
%s
%s
    exit 0i32;""" % (chk("a + b == 17i32 && a - b == 7i32 && a * b == 60i32 && a / b == 2i32 && a % b == 2i32", 10),
                      chk("(a == 12i32) && (a != b) && (b < a) && (b <= 5i32) && (a > b) && (a >= 12i32)", 11),
                      chk("(a > b && b > 0i32) && (a < b || b < a)", 12),
                      chk("((a & b) == 4i32) && ((a | b) == 13i32) && ((a ^ b) == 9i32) && ((b << 2i32) == 20i32) && ((a >> 2i32) == 3i32)", 13))),
      wrong="refused, or 10-13")
claim("as0295b", D, 295, "<=>", "rule",
      "`<=>` is a binary operator: `1 <=> 2` is negative.",
      expect="run:0",
      src=main_("""    int32:c = raw v32(1i32) <=> raw v32(2i32);
%s
    exit 0i32;""" % chk("c < 0i32", 10)),
      wrong="refused (DEF-131's shape), or 10")
claim("as0296", D, 296, "| `UnaryExpr` | `op`, `operand` | `!` `~` `-` |", "row",
      "The unary operators `!`, `~` and `-` compute.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(5i32);
    bool:t = raw vb(true);
%s
    exit 0i32;""" % chk("(!t) == false && (~a) == -6i32 && (-a) == -5i32", 10)),
      wrong="refused, or 10")
claim("as0297", D, 297, "| `PostfixExpr` | `op`, `operand` | `++` `--` |", "row",
      "`++` and `--` are postfix operators: `x++; x--;` compiles.",
      expect="compile",
      src=main_("""    int32:x = raw v32(1i32);
    x++;
    x--;
    discard(x);
    exit 0i32;"""),
      wrong="refused: removed")
claim("as0298", D, 298, "yields a **second-class borrow**, not a pointer (D-004)", "row",
      "`@x` is a second-class borrow: it cannot be returned out of its function.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "func:leak = int32->() never fails { int32:x = 5i32; pass @x; };"),
      wrong="accepted: a borrow of a local escapes")
claim("as0299", D, 299, "| `DerefExpr` | `operand` | `<-ptr` |", "row",
      "`<-ptr` dereferences: a write through it reaches the local.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    int32->:p = @x;
    <-p = 6i32;
%s
    exit 0i32;""" % chk("x == 6i32", 10)),
      wrong="refused, or 10")
claim("as0300", D, 300, "`$$i` / `$$m`", "row",
      "`$$m` takes a mutable borrow: a write through `$$m arr[2]` changes the element.",
      expect="run:0",
      src=main_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32->:p = $$m arr[2i64];
    <-p = 9i32;
%s
    exit 0i32;""" % chk("arr[2i64] == 9i32", 10)),
      wrong="refused, or 10")
claim("as0300b", D, 300, "| `BorrowExpr` |", "rule",
      "`$$i` takes an immutable borrow: reading through `$$i x` gives x.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(4i32);
    int32->:q = $$i x;
    int32:v = <-q;
%s
    exit 0i32;""" % chk("v == 4i32", 10)),
      wrong="refused, or 10")
claim("as0301", D, 301, "| `PipeExpr` | `direction`, `value`, `callee` | `\\|>` / `<\\|` |", "row",
      "`|>` and `<|` pipe a value into a function: `4 |> dbl` is 8 and `dbl <| 5` is 10.",
      expect="run:0",
      src=main_("""    int32:a = (raw v32(4i32) |> dbl) ?| 0i32;
    int32:b = (dbl <| raw v32(5i32)) ?| 0i32;
%s
    exit 0i32;""" % chk("a == 8i32 && b == 10i32", 10), "func:dbl = int32(int32:x) never fails { pass (x * 2i32); };"),
      wrong="refused, or 10")
claim("as0302", D, 302, "| `RangeExpr` | `lo`, `hi`, `inclusive` | `..` / `...` |", "row",
      "`..` is inclusive and `...` exclusive: the sums over 1 to 3 are 6 and 3.",
      expect="run:0",
      src=main_("""    int64:s = 0i64;
    int64:t = 0i64;
    for (int64:i in 1i64..3i64) { s = s + i; }
    for (int64:j in 1i64...3i64) { t = t + j; }
%s
    exit 0i32;""" % chk("s == 6i64 && t == 3i64", 10)),
      wrong="refused, or 10")
claim("as0303", D, 303, "**`..^`** — expands a collection at a call site (D-026)", "row",
      "`..^` expands a slice at a call site: `total(1, ..^xs)` with xs = [2, 3] is 6.",
      expect="run:0",
      src=main_("""    int64[3]:arr = [2i64, 3i64, 4i64];
    int64[]:xs = arr[0i32...2i32];
    int64:t = raw total(1i64, ..^xs);
%s
    exit 0i32;""" % chk("t == 6i64", 10), TOTAL),
      wrong="refused, or 10")
claim("as0304", D, 304, "| `TernaryExpr` | `cond`, `then_expr`, `else_expr` | `is (c) : a : b` |", "row",
      "The ternary is `is (c) : a : b`.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(3i32);
    int32:v = is (x > 2i32) : 10i32 : 20i32;
%s
    exit 0i32;""" % chk("v == 10i32", 10)),
      wrong="refused, or 10")
claim("as0305", D, 305, "**`move(place)`** — transfers ownership and invalidates the source (D-065)", "row",
      "`move(place)` transfers ownership: the destination holds the string.",
      expect="run:0",
      src=main_("""    string:s = string_concat("a", "b");
    string:t = move(s);
%s
    exit 0i32;""" % chk('string_equals(t, "ab")', 10)),
      wrong="refused, or 10")
claim("as0306", D, 306, "**`is_err(tbbValue)`** — tests a `tbb` for ERR **without trapping**", "row",
      "`is_err(t)` tests a tbb for ERR without trapping: true for ERR, false for 5.",
      expect="run:0",
      src=main_("""    tbb8:e = ERR;
    tbb8:f = raw vt8(5tbb8);
%s
    exit 0i32;""" % chk("is_err(e) && !is_err(f)", 10)),
      wrong="refused, a trap, or 10")
claim("as0307", D, 307, "**`Result{value: v, err: e}`** — the only way to construct a `Result`", "row",
      "`Result{value: v, err: e}` constructs a Result: one with err 0 is not an error and holds v.",
      expect="run:0",
      src=main_("""    Result<int32>:r = Result{ value: 5i32, err: 0i32 };
    if (r.is_error) { exit 10i32; }
%s
    exit 0i32;""" % chk("r.value == 5i32", 11)),
      wrong="refused, or 10/11")
claim("as0310", D, 310, "built by writing the value and emptied by writing `NIL`", "rule",
      "An Optional is built by writing the value and emptied by writing `NIL`.",
      expect="run:0",
      src=main_("""    int32?:a = raw v32(5i32);
%s
    a = NIL;
%s
    exit 0i32;""" % (chk("(a ?? 0i32) == 5i32", 10), chk("a == NIL", 11))),
      wrong="refused, or 10/11")
claim("as0326", D, 326, "Its operand is a **`tbb`**, not a `Result`", "rule",
      "`is_err`'s operand is a tbb, not a Result: `is_err(r)` on a Result is refused.",
      expect="refuse",
      src=main_("""    Result<int32>:r = k(raw v32(1i32));
    bool:b = is_err(r);
    exit 0i32;""", K),
      wrong="accepted")
claim("as0329", D, 329, "**`ok(val)`** was removed instead (D-097)", "rule",
      "`ok(val)` is removed: a call to it is refused.",
      expect="refuse",
      src=main_("""    tbb8:t = raw vt8(5tbb8);
    bool:b = ok(t);
    exit 0i32;"""),
      wrong="accepted")
claim("as0352", D, 352, "Its operand is a **place**, not a value", "rule",
      "`move`'s operand is a place: `move(f())` is refused.",
      expect="refuse",
      src=main_("""    string:t = move(mk());
    exit 0i32;""", 'func:mk = string() never fails { pass string_concat("a", "b"); };'),
      wrong="accepted")

# ------------------------------------------------------------------ 3.3 access and calls
claim("as0360", D, 360, "| `IdentifierExpr` | `name` |", "row", "The IdentifierExpr node.",
      untestable="[internal] the node")
claim("as0361", D, 361, "**`.` only** — auto-dereferences pointers", "row",
      "`.` auto-dereferences a pointer: `q.y` on a `Pt->` reads the field.",
      expect="run:0",
      src=main_("""    Pt:v = Pt{ x: raw v32(4i32), y: 5i32 };
    Pt->:q = @v;
%s
    exit 0i32;""" % chk("q.y == 5i32", 10), "struct:Pt = { int32:x; int32:y; };"),
      wrong="refused, or 10")
claim("as0361b", D, 361, "`->` is type-position only (D-006)", "rule",
      "`->` is type-position only: `q->y` is refused.",
      expect="refuse",
      src=main_("""    Pt:v = Pt{ x: raw v32(4i32), y: 5i32 };
    Pt->:q = @v;
    int32:w = q->y;
    exit 0i32;""", "struct:Pt = { int32:x; int32:y; };"),
      wrong="accepted")
claim("as0362", D, 362, "| `SafeNavExpr` | `base`, `field` | `?.` |", "row",
      "`?.` reads a field through an Optional: a present one gives the field, an empty one NIL.",
      expect="run:0",
      src=main_("""    Pt?:p = Pt{ x: raw v32(3i32), y: 4i32 };
    Pt?:q = NIL;
%s
    exit 0i32;""" % chk("(p?.x ?? 0i32) == 3i32 && (q?.y ?? 9i32) == 9i32", 10), "struct:Pt = { int32:x; int32:y; };"),
      wrong="refused, or 10")
claim("as0363", D, 363, "| `IndexExpr` | `base`, `index` | bounds-checked |", "row",
      "Indexing is bounds-checked: index 4 of a 4-element array traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32:v = a[raw v64(4i64)];
    if (v == 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="10/11: an unchecked read")
claim("as0364", D, 364, "`generic_args` may arrive implicitly (`f<int32>(x)`)", "row",
      "Generic arguments may arrive implicitly: `idt<int32>(5i32)` is a call, as `idt::<int32>(5i32)` is.",
      expect="run:0",
      src=main_("""    int32:v = raw idt<int32>(raw v32(5i32));
%s
    exit 0i32;""" % chk("v == 5i32", 10), "func:idt<T> = int32(T:_~x) never fails { pass 5i32; };"),
      wrong="refused: only the turbofish (LEXICAL:239)")
claim("as0365", D, 365, "UFCS — `p.magnitude()` resolves to `Point_magnitude(p)` (D-006)", "row",
      "UFCS: with a free function `Point_magnitude(Point:p)`, `p.magnitude()` calls it.",
      expect="run:0",
      src=main_("""    Point:p = Point{ x: raw v32(3i32), y: 4i32 };
%s
    exit 0i32;""" % chk("(raw p.magnitude()) == 7i32", 10), """struct:Point = { int32:x; int32:y; };
func:Point_magnitude = int32(Point:p) never fails { pass (p.x + p.y); };"""),
      wrong="refused: no method `magnitude`")
claim("as0366", D, 366, "**`#name<T>(…)`** (D-020)", "row",
      "A compiler builtin is `#name<T>(…)`: `#size_of<int32>()` is 4.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<int32>() == 4i64", 10)),
      wrong="refused, or 10")
claim("as0367", D, 367, "**`comptime(expr)`** — forces compile-time resolution", "row",
      "`comptime(expr)` resolves at compile time: `comptime(6i32 * 7i32)` is 42.",
      expect="run:0",
      src=main_("""    int32:v = comptime(6i32 * 7i32);
%s
    exit 0i32;""" % chk("v == 42i32", 10)),
      wrong="refused, or 10")
claim("as0367b", D, 367, "a compile error if it cannot be resolved", "rule",
      "`comptime(expr)` that cannot be resolved at compile time is a compile error.",
      expect="refuse",
      src=main_("""    int32:v = comptime(raw v32(1i32));
    exit 0i32;"""),
      wrong="accepted (evaluated at run time)")
claim("as0384", D, 384, "| **`#`-prefixed** | `BuiltinExpr` |", "row",
      "`#`-prefixed calls are compiler builtins and macros: `#size_of<int64>()` and a user macro compile.",
      expect="run:0",
      src=main_("""    int32:v = #three();
%s
    exit 0i32;""" % chk("v == 3i32 && #size_of<int64>() == 8i64", 10), "macro:three = () { 3i32; };"),
      wrong="refused, or 10")
claim("as0385", D, 385, "| **bare name** | ordinary `CallExpr` |", "row",
      "The bare-name builtins are ordinary calls: `sys(39i64)` and `string_concat` are called bare.",
      expect="run:0",
      src=main_("""    Result<int64>:p = sys(39i64);
    if (p.is_error) { exit 10i32; }
    string:s = string_concat("a", "b");
%s
    exit 0i32;""" % chk("string_byte_length(s) == 2i64", 11)),
      wrong="refused, or 10/11")
claim("as0385b", D, 385, "`asm`, `ok`, `is_err`", "rule",
      "`ok` is one of the bare-name builtins: `ok(t)` is an ordinary call.",
      expect="compile",
      src=main_("""    tbb8:t = raw vt8(5tbb8);
    bool:b = ok(t);
    discard(b);
    exit 0i32;"""),
      wrong="refused: `ok` removed (AST:329)")
claim("as0403", D, 403, "return `Result<T>`, and are subject to", "rule",
      "A bare-name builtin returns `Result<T>` like any function: `string_byte_length`'s call binds as a "
      "`Result<int64>`.",
      expect="compile",
      src=main_("""    Result<int64>:n = string_byte_length("abc");
    if (n.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: the builtin returns a plain int64")

# ------------------------------------------------------------------ 3.4 Result and safety
claim("as0413", D, 413, "| `SafeUnwrapExpr` | `expr`, `default` | `e ? d` |", "row",
      "`e ? d` unwraps with a default: `k(3i32) ? 0i32` is 3.",
      expect="run:0",
      src=main_("""    int32:v = k(raw v32(3i32)) ? 0i32;
%s
    exit 0i32;""" % chk("v == 3i32", 10), K),
      wrong="refused: a bare `?` (D-175)")
claim("as0414", D, 414, "| `NullCoalesceExpr` | `expr`, `default` | `e ?? d` |", "row",
      "`e ?? d` gives the default for an empty Optional.",
      expect="run:0",
      src=main_("""    int32?:a = NIL;
    int32?:b = raw v32(42i32);
%s
    exit 0i32;""" % chk("(a ?? 7i32) == 7i32 && (b ?? 7i32) == 42i32", 10)),
      wrong="refused, or 10")
claim("as0415", D, 415, "**`e ?! code`** — exactly one `tbb32` argument (D-009)", "row",
      "`e ?! code` takes exactly one `tbb32` argument: `k(3i32) ?! 5tbb32` compiles.",
      expect="compile",
      src=main_("""    int32:v = k(raw v32(3i32)) ?! 5tbb32;
    discard(v);
    exit 0i32;""", K),
      wrong="refused: the code is an error constant, not a tbb32")
claim("as0416", D, 416, "`?\\|` / `defaults` — **struck (D-167)**", "row",
      "`?|` is struck (D-167) and refused by name: `k(3i32) ?| 0i32` is refused.",
      expect="refuse",
      src=main_("""    int32:v = k(raw v32(3i32)) ?| 0i32;
    discard(v);
    exit 0i32;""", K),
      wrong="accepted")
claim("as0416b", D, 416, "the node is still built so the parser never restricts, and refused by name", "rule",
      "`defaults` is struck and refused by name: `k(3i32) defaults 0i32` is refused.",
      expect="refuse",
      src=main_("""    int32:v = k(raw v32(3i32)) defaults 0i32;
    discard(v);
    exit 0i32;""", K),
      wrong="accepted")
claim("as0417", D, 417, "| `RawUnwrapExpr` | `expr` | `raw e` / `_! e` |", "row",
      "`raw e` and `_! e` unwrap a never-fails call.",
      expect="run:0",
      src=main_("""    int32:a = raw g(raw v32(3i32));
    int32:b = _! g(raw v32(4i32));
%s
    exit 0i32;""" % chk("a + b == 7i32", 10), G),
      wrong="refused, or 10")
claim("as0418", D, 418, "| `DropExpr` | `expr` | `drop e` / `_? e` |", "row",
      "`drop e` and `_? e` discard a never-fails NIL call.",
      expect="compile",
      src=main_("""    drop note();
    _? note();
    exit 0i32;""", "func:note = NIL() never fails { pass NIL; };"),
      wrong="refused")
RELAY = """error:E1;
func:inner = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};
func:outer = int32(int32->:flag, int32:v) {
    defer { <-flag = 7i32; }
    int32:r = %s inner(v);
    pass r;
};
func:classify = int32(int32->:flag) never fails {
    Result<int32>:r = outer(flag, raw v32(5i32));
    if (r.is_error) {
        pick (r.err) { (E1) { pass 10i32; }, (*) { pass 30i32; } }
    }
    pass 0i32;
};"""
RELAY_MAIN = """    int32:f = 0i32;
    int32:c = raw classify(@f);
%s
%s
    exit 0i32;""" % (chk("c == 10i32", 10), chk("f == 7i32", 11))
claim("as0419", D, 419, "**`relay e` / `_^ e`** (D-080) — on error, returns the same code", "row",
      "`relay e` returns the same error code from the enclosing function, and its `defer` runs.",
      expect="run:0", src=main_(RELAY_MAIN, RELAY % "relay"),
      wrong="another code (10), or the defer skipped (11)")
claim("as0421", D, 421, "**`RelayExpr` is a normal exit path**, so `defer` runs on the error branch", "rule",
      "`_^`'s error branch is a normal exit: the `defer` runs.",
      expect="run:0", src=main_(RELAY_MAIN, RELAY % "_^"),
      wrong="refused, or 10/11")
claim("as0422", D, 422, "unlike `EmphaticUnwrapExpr`, which traps and runs nothing", "rule",
      "`?!` traps and runs nothing: a pending `defer` that would trap IntOverflow does not run, and "
      "failsafe sees `E1` (81).",
      expect="run:81",
      src=main_("""    int32:v = raw f(raw v32(1i32));
    exit 10i32;""", """error:E1;
func:k = int32(int32:x) { if (x > 0i32) { fail E1; } pass x; };
func:f = int32(int32:x) never fails {
    defer { int8:z = raw v8(127i8) + 1i8; discard(z); }
    int32:v = k(x) ?! E1;
    pass v;
};"""),
      wrong="IntOverflow (93): the defer ran")
claim("as0423", D, 423, "It is **illegal in `main` and `failsafe`**", "rule",
      "`relay` is illegal in `main`: refused.",
      expect="refuse",
      src=main_("""    int32:v = relay k(raw v32(1i32));
    exit 0i32;""", K),
      wrong="accepted")

# ------------------------------------------------------------------ 3.5 casts
claim("as0432", D, 432, "`=>`, **compile error if loss is possible**", "row",
      "`=>` is a compile error where loss is possible: `int64 => int32` is refused.",
      expect="refuse",
      src=main_("""    int64:a = raw v64(5i64);
    int32:b = a => int32;
    exit 0i32;"""),
      wrong="accepted")
claim("as0433", D, 433, "`=>!`, the sole opt-out", "row",
      "`=>!` is the opt-out: `int64 =>! int32` of 5 is 5.",
      expect="run:0",
      src=main_("""    int64:a = raw v64(5i64);
    int32:b = a =>! int32;
%s
    exit 0i32;""" % chk("b == 5i32", 10)),
      wrong="refused, or 10")
claim("as0435", D, 435, "`cast<T>` / `#cast<T>` / `@cast<T>` do not exist (D-021)", "rule",
      "`cast<T>(x)` does not exist: refused.",
      expect="refuse",
      src=main_("""    int64:a = raw v64(5i64);
    int32:b = cast<int32>(a);
    exit 0i32;"""),
      wrong="accepted")
claim("as0435b", D, 435, "`#cast<T>`", "rule",
      "`#cast<T>(x)` does not exist: refused.",
      expect="refuse",
      src=main_("""    int64:a = raw v64(5i64);
    int32:b = #cast<int32>(a);
    exit 0i32;"""),
      wrong="accepted")
claim("as0437", D, 437, "**A cast target carries a memory qualifier** — `p => wild int8->`", "rule",
      "A cast target carries a memory qualifier: `p => wild int8->` compiles.",
      expect="compile",
      src=main_("""    int8:b = raw v8(1i8);
    int8->:p = @b;
    wild int8->:w = p => wild int8->;
    discard(w);
    exit 0i32;"""),
      wrong="refused: the qualifier not read on a cast target")

# ------------------------------------------------------------------ 3.6 construction and async
for _ln, _q in ((448, "| `StructLiteralExpr` | `type`, `fields` |"), (449, "| `ArrayLiteralExpr` | `elements` |")):
    claim("as%04d" % _ln, D, _ln, _q, "row", "The node's fields.",
          untestable="[internal] the node's fields")
claim("as0450", D, 450, "`vec3(1.0, 2.0, 3.0)`", "row",
      "`vec3(1.0, 2.0, 3.0)` constructs a vector.",
      expect="compile",
      src=main_("""    vec3:v = vec3(1.0f32, 2.0f32, 3.0f32);
    discard(v);
    exit 0i32;"""),
      wrong="refused: `vec3` is a library type now (D-135)")
claim("as0451", D, 451, "legal only inside `async func` (`NITPICK-040`)", "row",
      "`await` is legal only inside an `async func`: one in a plain function is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw f();
    exit 0i32;""", """async func:a = int32() { pass 1i32; };
func:f = int32() never fails { int32:x = await a() ?| 0i32; pass x; };"""),
      wrong="accepted")
claim("as0452", D, 452, "`$`, legal only inside `loop` / `till`", "row",
      "`$` is legal only inside `loop` and `till`: one in a `while` is refused.",
      expect="refuse",
      src=main_("""    int64:i = raw v64(0i64);
    int64:s = 0i64;
    while (i < 3i64) decreases 3i64 - i { s = s + $; i = i + 1i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0453", D, 453, "**A `=>` whose target is a `dyn` type is this node", "row",
      "A `=>` whose target is a `dyn` type builds a trait object: `move(l) => dyn Speaks` compiles and "
      "dispatches.",
      expect="run:0",
      src=main_("""    Loud:l = Loud{ name: string_concat("a", "b"), v: 7i32 };
    dyn Speaks:d = move(l) => dyn Speaks;
%s
    exit 0i32;""" % chk("(d.say() ?| 0i32) == 7i32", 10), SPEAKS),
      wrong="refused, or 10")
claim("as0454", D, 454, "a `pick` whose arms `give` (D-059)", "row",
      "A `pick` whose arms `give` is a PickExpr: it initialises a binding.",
      expect="run:0",
      src=main_("""    int32:y = raw v32(1i32);
    int32:v = pick (y) { (1i32) { give 10i32; }, (*) { give 20i32; } };
%s
    exit 0i32;""" % chk("v == 10i32", 10)),
      wrong="refused, or 10")
claim("as0455", D, 455, "legal in `ensures` and `invariant`, never nested", "row",
      "`old(expr)` is legal in `ensures`: `ensures result == old(x) + 1i32` holds.",
      expect="run:0",
      src=main_("""    int32:v = bump(raw v32(4i32)) ?| 0i32;
%s
    exit 0i32;""" % chk("v == 5i32", 10),
                "func:bump = int32(int32:x) ensures result == old(x) + 1i32 { pass (x + 1i32); };"),
      wrong="refused, or 10")
claim("as0455b", D, 455, "never nested", "rule",
      "`old` is never nested: `old(old(x))` is refused.",
      expect="refuse",
      src=main_("""    int32:v = bump(raw v32(4i32)) ?| 0i32;
    exit 0i32;""", "func:bump = int32(int32:x) ensures result == old(old(x)) + 1i32 { pass (x + 1i32); };"),
      wrong="accepted")
claim("as0455c", D, 455, "**`old(expr)`**, the operand's value at the function's ENTRY", "rule",
      "`old` is legal in `ensures` and `invariant` only: one in a function body is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw f(raw v32(4i32));
    exit 0i32;""", "func:f = int32(int32:x) never fails { pass old(x); };"),
      wrong="accepted")
claim("as0456", D, 456, "legal in `ensures` alone", "row",
      "`result` is legal in `ensures` alone: one in `requires` is refused.",
      expect="refuse",
      src=main_("""    int32:v = f(raw v32(4i32)) ?| 0i32;
    exit 0i32;""", "func:f = int32(int32:x) requires result > 0i32 { pass x; };"),
      wrong="accepted")
claim("as0461", D, 461, "variables are a compile error", "rule",
      "An uninitialised variable is a compile error: `int32:x;` then a read of x is refused.",
      expect="refuse",
      src=main_("""    int32:x;
    if (x == 0i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0476", D, 476, "**No lambda or closure nodes.** Closures are removed (D-018)", "rule",
      "Closures are removed: an anonymous function expression is refused.",
      expect="refuse",
      src=main_("""    func int32(int32) never fails:f = func int32(int32:x) never fails { pass x; };
    exit 0i32;"""),
      wrong="accepted")

# ================================================================== 4. types
claim("as0485", D, 485, "| `NamedType` | `name`, `generic_args` | |", "row", "The NamedType node.",
      untestable="[internal] the node's fields")
claim("as0486", D, 486, "`T->` — **thin**, one word, no bounds metadata (D-038)", "row",
      "A pointer is thin, one word: `#size_of<int32->>()` is 8.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<int32->>() == 8i64", 10)),
      wrong="16 (a fat pointer), or refused")
claim("as0487", D, 487, "| `OptionalType` | `inner` | `T?` |", "row",
      "`T?` is the Optional type: `int32?` holds 5 or NIL.",
      expect="run:0",
      src=main_("""    int32?:a = raw v32(5i32);
    int32?:b = NIL;
%s
    exit 0i32;""" % chk("(a ?? 0i32) == 5i32 && b == NIL", 10)),
      wrong="refused, or 10")
claim("as0488", D, 488, "value type; does not decay", "row",
      "An array is a value type: a copy is independent of its source.",
      expect="run:0",
      src=main_("""    int32[2]:a = [1i32, 2i32];
    int32[2]:b = a;
    b[0i64] = 9i32;
%s
    exit 0i32;""" % chk("a[0i64] == 1i32 && b[0i64] == 9i32", 10)),
      wrong="refused, or 10 (the copy aliases)")
claim("as0488b", D, 488, "does not decay", "rule",
      "An array does not decay to a pointer: an `int32[2]` passed for an `int32->` is refused.",
      expect="refuse",
      src=main_("""    int32[2]:a = [1i32, 2i32];
    int32:v = raw first(a);
    exit 0i32;""", "func:first = int32(int32->:p) never fails { pass <-p; };"),
      wrong="accepted: the array decayed")
claim("as0489", D, 489, "| `FuncType` | `params`, `return_type`, `never_fails: bool` | D-163 |", "row",
      "The FuncType node (listed twice in the table; the second row gives the spelling).",
      untestable="[internal] the node's fields; as0491 tests the type's spelling")
claim("as0490", D, 490, "| `DynType` | `traits: TypeNode[]` | `dyn A & B` |", "row",
      "`dyn A & B` is a trait-object type over two traits: a binding of that type compiles.",
      expect="compile",
      src=main_("""    S:s = S{ n: 1i32 };
    dyn A & B:d = move(s);
    discard(d);
    exit 0i32;""", """trait:A = { func:a = int32(Self:self) never fails; };
trait:B = { func:b = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:A = { func:a = int32(S:self) never fails { pass 1i32; }; };
impl:S:B = { func:b = int32(S:self) never fails { pass 2i32; }; };"""),
      wrong="refused")
claim("as0491", D, 491, "**`func RetType(ParamTypes) [never fails]`** (D-087; D-163)", "row",
      "A function type is `func RetType(ParamTypes) never fails`: `f` of that type holding `twice` gives 6.",
      expect="run:0",
      src=main_("""    func int64(int64) never fails:f = twice;
%s
    exit 0i32;""" % chk("(raw f(3i64)) == 6i64", 10), "func:twice = int64(int64:x) never fails { pass (x * 2i64); };"),
      wrong="refused, or 10")
claim("as0491b", D, 491, "a may-fail function cannot fill a `never fails` slot", "rule",
      "A may-fail function cannot fill a `never fails` slot: refused.",
      expect="refuse",
      src=main_("""    func int64(int64) never fails:f = twice;
    discard(raw f(3i64));
    exit 0i32;""", "func:twice = int64(int64:x) { pass (x * 2i64); };"),
      wrong="accepted")
claim("as0492", D, 492, "Inhabited by string literals (checked at compile time) and by `to_cstring`", "row",
      "A `cstring` is inhabited by a string literal: `cstring:c = \"abc\";` compiles.",
      expect="compile",
      src=main_("""    cstring:c = "abc";
    discard(c);
    exit 0i32;"""),
      wrong="refused (DEF-153's shape)")
claim("as0493", D, 493, "**Only legal under `->`**; bare `any` is a type error", "row",
      "Bare `any` is a type error: a parameter of type `any` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:f = int32(any:x) never fails { pass 0i32; };"),
      wrong="accepted")
claim("as0494", D, 494, "`Self`, valid only in `trait` / `impl` bodies (D-030)", "row",
      "`Self` is valid only in trait and impl bodies: a free function returning `Self` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:f = Self() never fails { pass NIL; };"),
      wrong="accepted")
claim("as0495", D, 495, "**`Mutex<Config, 2>`** — a compile-time **value** in a type-argument list", "row",
      "A type-argument list holds a compile-time value: `Mutex<int64, 2i32>` is a type.",
      expect="compile",
      src=main_("    exit 0i32;", "func:f = int32(Mutex<int64, 2i32>->:_~m) never fails { pass 0i32; };"),
      wrong="refused")
claim("as0496", D, 496, "**`T.Item`** — an associated type projected from a type (D-164)", "row",
      "`T.Item` projects an associated type: `first<T: Seq>` returning `T.Item` gives the counter's value.",
      expect="run:0", src=main_(SEQ_MAIN, SEQ),
      wrong="refused, or 10")
claim("as0498", D, 498, "Qualifiers on `VarDeclStmt`, not on the type node: `stack`, `wild`, `wildx`,", "rule",
      "`stack` qualifies a local: `stack int32:x = 3i32;` compiles and holds 3.",
      expect="run:0",
      src=main_("""    stack int32:x = 3i32;
%s
    exit 0i32;""" % chk("x == 3i32", 10)),
      wrong="refused, or 10")
claim("as0499", D, 499, "`const`, `fixed`", "rule",
      "`const` qualifies a local: `const int32:x = 3i32;` compiles.",
      expect="compile",
      src=main_("""    const int32:x = 3i32;
    discard(x);
    exit 0i32;"""),
      wrong="refused: `const` retired (AST:505)")
claim("as0499b", D, 499, "**`gc` does not exist** (D-003)", "rule",
      "`gc` does not exist: `gc int32:x` is refused.",
      expect="refuse",
      src=main_("""    gc int32:x = 3i32;
    exit 0i32;"""),
      wrong="accepted")
claim("as0501", D, 501, "`borrow_imm` / `borrow_mut` are STRUCK", "rule",
      "`borrow_imm` is struck: a binding so qualified is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    borrow_imm int32->:p = @x;
    exit 0i32;"""),
      wrong="accepted")
claim("as0518", D, 518, "**`ArrayType.size` consumed one token and called it an integer literal**", "rule",
      "An array's size may be a named constant: `int32[COUNT]` with COUNT = 3 holds three elements.",
      expect="run:0",
      src=main_("""    int32[COUNT]:a = [1i32, 2i32, 3i32];
%s
    exit 0i32;""" % chk("a[2i64] == 3i32 && #size_of<int32[COUNT]>() == 12i64", 10), "fixed int64:COUNT = 3i64;"),
      wrong="refused, or 10 (another size)")
claim("as0538", D, 538, "Beyond the scalar families:", "rule",
      "The builtin type names are the compiler's: a user struct named `Result` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "struct:Result = { int32:x; };"),
      wrong="accepted: the builtin shadowed")

# ================================================================== 5. verification nodes
claim("as0551", D, 551, "compared at every call inside the function's recursive group", "row",
      "A function's `decreases` is compared at every call inside its recursive group: f and g calling each "
      "other with an unchanged measure trap DecreasesViolated.",
      expect="trap:DecreasesViolated",
      src=main_("""    int64:r = raw f(raw v64(3i64));
    if (r == 0i64) { exit 10i32; }
    exit 11i32;""", """func:f = int64(int64:n) decreases n never fails {
    if (n <= 0i64) { pass 0i64; }
    pass (raw g(n));
};
func:g = int64(int64:n) decreases n never fails {
    if (n <= 0i64) { pass 0i64; }
    pass (raw f(n));
};"""),
      wrong="StackExhausted (the group not checked)")
claim("as0552", D, 552, "| `InvariantNode` | `conditions: Expr[]` — attached to loop statements |", "row",
      "An invariant is attached to a loop: one that fails traps InvariantViolated.",
      expect="trap:InvariantViolated",
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 5i64) decreases 5i64 - i invariant i < 2i64 { i = i + 1i64; }
    exit 10i32;"""),
      wrong="10: the invariant not checked")
claim("as0553", D, 553, "`limit<r_pos>` on a declaration, a parameter", "row",
      "`limit<r_pos>` on a parameter: passing -1 traps LimitViolated.",
      expect="trap:LimitViolated",
      src=main_("""    int32:v = need(raw v32(-1i32)) ?| 0i32;
    exit 10i32;""", """Rules<int32>:r_pos = { $ > 0i32 };
func:need = int32(limit<r_pos> int32:m) { pass (m + 1i32); };"""),
      wrong="10: the parameter's rule not checked")
claim("as0554", D, 554, "the `never fails` contract on an ordinary function, trait method, impl method", "row",
      "`never fails` rides an ordinary function and a function type alike.",
      expect="run:0",
      src=main_("""    func int64() never fails:f = seven;
%s
    exit 0i32;""" % chk("(raw f()) == 7i64 && (raw seven()) == 7i64", 10),
                "func:seven = int64() never fails { pass 7i64; };"),
      wrong="refused, or 10")
claim("as0555", D, 555, "Constant-expression only", "row",
      "`joins` takes a constant expression only: a call as the deadline is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "thread async func:t = NIL(int64:_~n) joins raw duration_secs(1i64) { pass NIL; };"),
      wrong="accepted")
claim("as0556", D, 556, "A channel-returning function without it is a getter", "row",
      "A channel-returning function without `gives` is a getter: creating a channel inside one is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """error:E1;
async func:mk = Channel<int32, 3i32, 1i64>() {
    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    pass ch;
};"""),
      wrong="accepted")
claim("as0557", D, 557, "Orthogonal to `never fails`: a pure function may `fail`", "row",
      "A `pure` function may `fail`: `pure` without `never fails` compiles, and its failure reaches the caller.",
      expect="run:0",
      src=main_("""    int32:a = p(raw v32(3i32)) ?| 0i32;
    int32:b = p(raw v32(-1i32)) ?| 9i32;
%s
    exit 0i32;""" % chk("a == 3i32 && b == 9i32", 10), """error:E1;
func:p = int32(int32:x) pure { if (x < 0i32) { fail E1; } pass x; };"""),
      wrong="refused: pure demands never fails")
claim("as0558", D, 558, "a clause found after `invariant`, the wrong order, TYPE-072", "row",
      "The termination clause comes before `invariant`: `invariant P decreases E` is refused, "
      "NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 3i64) invariant i >= 0i64 decreases 3i64 - i { i = i + 1i64; }
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("as0563", D, 563, "A `decreases` measure admits neither", "rule",
      "A `decreases` measure admits neither `result` nor `old`: `decreases old(i)` is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", """func:f = int64(int64:n) decreases old(n) never fails {
    if (n <= 0i64) { pass 0i64; }
    pass (raw f(n - 1i64));
};"""),
      wrong="accepted")

# ================================================================== 6. attributes
claim("as0571", D, 571, "```", "example",
      "An attribute attaches to a declaration: `#[derive(Clone)]` on a struct compiles.",
      expect="compile",
      src=main_("    exit 0i32;", "#[derive(Clone)]\nstruct:Named = { string:s; int32:n; };"),
      wrong="refused")
claim("as0572", D, 572, "#[align(16)]", "rule",
      "`#[align(16)]` is an attribute: a struct carrying it compiles.",
      expect="compile",
      src=main_("    exit 0i32;", "#[align(16i32)]\nstruct:Aligned = { int64:a; };"),
      wrong="refused")
claim("as0575", D, 575, "not `@derive` (D-020)", "rule",
      "Derive is not `@derive`: `@derive(Clone)` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "@derive(Clone)\nstruct:Named = { string:s; int32:n; };"),
      wrong="accepted")
claim("as0583", D, 583, "`#[lexical_drop]` and `#[nll_drop]` are **removed**", "rule",
      "`#[lexical_drop]` is removed: a struct carrying it is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "#[lexical_drop]\nstruct:Named = { int32:n; };"),
      wrong="accepted")

# ================================================================== 7. removed
claim("as0593", D, 593, "| `PinExpr` (`#obj`) |", "row",
      "Pinning is removed: `#obj` on a value is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32:y = #x;
    exit 0i32;"""),
      wrong="accepted")
claim("as0594", D, 594, "| `LAMBDA` / closure capture | closures removed (D-018) |", "row",
      "Closures are removed: a nested function capturing a local is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    func:inner = int32() never fails { pass x; };
    exit 0i32;"""),
      wrong="accepted")
claim("as0595", D, 595, "| `gc` in `memory_modifier` | no collector (D-003) |", "row",
      "There is no `gc` memory modifier: a `gc` local is refused.",
      expect="refuse",
      src=main_("""    gc int64:y = 3i64;
    exit 0i32;"""),
      wrong="accepted")
claim("as0596", D, 596, "positional `.a` / `.b` / `.c` | replaced by named fields |", "row",
      "The nodes' positional slots are replaced by named fields.",
      untestable="[internal] the parser's node layout")
claim("as0597", D, 597, "| `end` block on `LOOP_STMT` / `TILL_STMT` | only `when` has one (D-027) |", "row",
      "A `till` has no `end` block: one is refused.",
      expect="refuse",
      src=main_("""    int64:n = 0i64;
    till (3i64, 1i64) { n = n + 1i64; } end { n = 0i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("as0598", D, 598, "| `a*` collection builtins |", "row",
      "The `a*` collection builtins are not the language's: `astack()` is refused.",
      expect="refuse",
      src=main_("""    int64:s = astack();
    exit 0i32;"""),
      wrong="accepted")

# ================================================================== 8. open items (the settled ones)
claim("as0621", D, 621, "**settled by D-058: internal", "rule",
      "`Future<T>` is an internal lowering artifact: no construct produces one.",
      untestable="[vague] the sentence names no construct whose refusal a program could check")
claim("as0635", D, 635, "**Resolved as: modifier + `comptime(expr)`, no block.**", "rule",
      "There is no `comptime { … }` block: one is refused.",
      expect="refuse",
      src=main_("""    comptime { int32:x = 1i32; };
    exit 0i32;"""),
      wrong="accepted")
claim("as0643", D, 643, "`FunctionDecl.modifiers` already", "rule",
      "`comptime` is a function modifier: `comptime func:sq` forced by `comptime(sq(5i32))` is 25.",
      expect="run:0",
      src=main_("""    int32:v = comptime(sq(5i32));
%s
    exit 0i32;""" % chk("v == 25i32", 10), "comptime func:sq = int32(int32:n) { pass (n * n); };"),
      wrong="refused, or 10")
