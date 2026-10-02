"""M11 claims: LEXICAL_REFERENCE.md (lines 1-410) at HUNT2 (9126350), extracted by session 9.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). No M10 item tests exactly a LEXICAL sentence.

Most of the reference is EBNF. A grammar block is claimed at its fence by a program
that uses what the block defines, and its separable lines are claimed where a program
can check them. The keyword productions are checked one source line at a time by a
shell script (`kw`): for each word on the line, it compiles a local binding of that
name and a function of that name, and every compile must be refused. A word the
reference says is NOT a keyword (removed, or never one) is checked the other way,
as a local's name only (`free`). A module-level function's name can be refused for
reasons of its own: a prelude or builtin name (D-239, D-294).
"""
from m11lib import *

covers("LEXICAL", 1)

D = "LEXICAL"
FS = failsafe_text("")


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


KW_LIB = r'''FAILS=""
probe() {
    sed "s/WORD/$2/g" "$1" > k.npk
    "$NPKC" k.npk -o k.ll > k.out 2>&1; rc=$?
    if [ "$rc" != "$3" ] || grep -q 'NITPICK-EMIT-002' k.out; then
        FAILS="$FAILS $2[$1:rc=$rc:$(grep -m1 -o 'NITPICK-[A-Z]*-[0-9]*' k.out)]"
    fi
}
'''
LOCAL_T = "mod:k;\n\n" + main_("    int32:WORD = 1i32;\n    exit 0i32;") + "\n" + FS
FUNC_T = "mod:k;\n\nfunc:WORD = int32() never fails { pass 1i32; };\n\n" + main_("    exit 0i32;") + "\n" + FS


def kw_sh(reserved=(), free=()):
    s = KW_LIB + "cat > local.t <<'EOF'\n" + LOCAL_T.rstrip() + "\nEOF\n"
    if reserved:
        s += "cat > func.t <<'EOF'\n" + FUNC_T.rstrip() + "\nEOF\n"
        s += "for w in %s; do probe local.t $w 1; probe func.t $w 1; done\n" % " ".join(reserved)
    if free:
        s += "for w in %s; do probe local.t $w 0; done\n" % " ".join(free)
    return s + 'echo "exceptions:${FAILS:- none}"\n[ -z "$FAILS" ]'


def names(words):
    return ", ".join("`%s`" % w for w in words)


def kw(cid, line, quote, words, kind="rule", text=None):
    claim(cid, D, line, quote, kind,
          text or "%s: each is reserved, so a local and a function of that name are each refused." % names(words),
          expect="sh:0", sh=kw_sh(reserved=words),
          wrong="a word accepted as a name (the script lists it)")


def free(cid, line, quote, words, kind="rule", text=None):
    claim(cid, D, line, quote, kind,
          text or "%s: none is a keyword, so a local of that name compiles." % names(words),
          expect="sh:0", sh=kw_sh(free=words),
          wrong="a word still reserved (the script lists it)")


# ================================================================== 1-3. source, whitespace, identifiers
claim("lx0014", D, 14, "Nitpick source is a sequence of Unicode code points encoded in UTF-8", "rule",
      "Source is UTF-8: a string literal holding `é` compiles, and the string is its two UTF-8 bytes.",
      expect="run:0",
      src=main_("""    string:s = "é";
%s
%s
    exit 0i32;""" % (chk("string_byte_length(s) == 2i64", 10), chk("string_bytes(s)[0i64] == 195u8", 11))),
      wrong="refused, or another encoding (10/11)")
claim("lx0015", D, 15, "not forming part of a valid token are a lexical error", "rule",
      "A character that forms no token (`§` between two operands) is a lexical error: refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32) § 2i32;
    exit 0i32;"""),
      wrong="accepted (the character skipped)")
claim("lx0017", D, 17, "```ebnf", "example",
      "Every code point up to U+10FFFF is a source character: a string literal holding U+1F600 compiles "
      "and is its four UTF-8 bytes.",
      expect="run:0",
      src=main_("""    string:s = "\U0001F600";
%s
%s
    exit 0i32;""" % (chk("string_byte_length(s) == 4i64", 10), chk("string_bytes(s)[0i64] == 240u8", 11))),
      wrong="refused, or another length (10/11)")
claim("lx0024", D, 24, "Block comments do **not** nest", "rule",
      "Block comments do not nest: `/* a /* b */ c */` ends at the first `*/`, leaving `c */` as code, "
      "which is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    /* a /* b */ c */
    exit 0i32;"""),
      wrong="accepted: the comments nest")
claim("lx0024b", D, 24, "stream. Block comments", "rule",
      "Since block comments do not nest, an inner `/*` is comment text: `/* a /* b */` is one whole "
      "comment and the program compiles.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    /* a /* b */
%s
    exit 0i32;""" % chk("x == 1i32", 10)),
      wrong="refused: an unclosed nested comment")
claim("lx0026", D, 26, "```ebnf", "example",
      "Whitespace (space, tab, CR, LF) and both comment forms are discarded: `1i32 /* c */ + 2i32 // d` "
      "with a tab and a CRLF is 3.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32)\t/* c */ + 2i32; // d\r
%s
    exit 0i32;""" % chk("x == 3i32", 10)),
      wrong="refused, or 10")
claim("lx0035", D, 35, "ASCII-bounded, beginning with a letter or underscore", "rule",
      "Identifiers are ASCII-bounded: `café` is not an identifier, and a local of that name is refused.",
      expect="refuse",
      src=main_("""    int32:café = raw v32(1i32);
    exit 0i32;"""),
      wrong="accepted: a non-ASCII letter in an identifier")
claim("lx0035b", D, 35, "beginning with a letter or underscore", "rule",
      "An identifier may begin with an underscore: `_n2` is a local's name.",
      expect="run:0",
      src=main_("""    int32:_n2 = raw v32(4i32);
%s
    exit 0i32;""" % chk("_n2 == 4i32", 10)),
      wrong="refused")
claim("lx0037", D, 37, "```ebnf", "example",
      "`Identifier ::= [a-zA-Z_] [a-zA-Z0-9_]*`: `a_1B` and `Z9` are names.",
      expect="run:0",
      src=main_("""    int32:a_1B = raw v32(2i32);
    int32:Z9 = raw v32(3i32);
%s
    exit 0i32;""" % chk("a_1B + Z9 == 5i32", 10)),
      wrong="refused")
claim("lx0043", D, 43, "The lexer resolves `_?`, `_!`, and `_~` as distinct operators", "rule",
      "`_!` is lexed as the operator before any identifier: `_! g(3i32)` on a `never fails` callee is 3.",
      expect="run:0",
      src=main_("""    int32:v = _! g(raw v32(3i32));
%s
    exit 0i32;""" % chk("v == 3i32", 10), "func:g = int32(int32:x) never fails { pass x; };"),
      wrong="refused: `_!` read as an identifier `_` and a `!`")
claim("lx0043b", D, 43, "`_?`", "rule",
      "`_?` is lexed as the operator: `_? note();` discards a `never fails` NIL call.",
      expect="compile",
      src=main_("""    _? note();
    exit 0i32;""", "func:note = NIL() never fails { pass NIL; };"),
      wrong="refused: `_?` read as an identifier")

# ================================================================== 4. keywords
kw("lx0048", 48, "```ebnf", ["wild", "relaxed", "if", "prove", "async", "use", "struct", "int8", "is"],
   kind="example",
   text="The keyword families are reserved: one word of each (`wild`, `relaxed`, `if`, `prove`, `async`, "
        "`use`, `struct`, `int8`, `is`) is refused as a local's and a function's name.")
kw("lx0052", 52, 'MemoryQualifier     ::= "wild"', ["wild", "wildx", "stack", "defer"])
kw("lx0054", 54, 'MemoryOrdering      ::= "relaxed"', ["relaxed", "acquire", "release", "acq_rel", "seq_cst"])
kw("lx0056", 56, 'ControlFlow         ::= "if"', ["if", "else", "while", "for", "loop", "till"])
kw("lx0057", 57, '"when" | "then" | "end" | "pick"', ["when", "then", "end", "pick", "fall", "where"])
kw("lx0058", 58, '"give" | "break" | "continue"', ["give", "break", "continue", "return", "pass"])
kw("lx0059", 59, '"fail" | "exit" | "raw"', ["fail", "exit", "raw", "drop", "nodrop"])
kw("lx0060", 60, '"defaults" | "discard" | "move" | "relay"', ["defaults", "discard", "move", "relay"])
kw("lx0062", 62, 'VerificationKeyword ::= "prove"', ["prove", "assert_static", "requires", "ensures"])
kw("lx0063", 63, '"acquires" | "gives"', ["acquires", "gives"])
kw("lx0064", 64, '"invariant" | "fails" | "on" | "with" | "never"', ["invariant", "fails", "on", "with", "never"])
kw("lx0065", 65, '"old" | "result" | "pure"', ["old", "result", "pure"])
kw("lx0066", 66, '"decreases" | "unbounded"', ["decreases", "unbounded"])
kw("lx0085", 85, 'AsyncKeyword        ::= "async"', ["async", "await", "thread", "joins"])
kw("lx0087", 87, 'ModuleKeyword       ::= "use"', ["use", "mod", "pub", "extern", "cfg", "as"])
kw("lx0088", 88, '"comptime" | "inline" | "noinline"', ["comptime", "inline", "noinline", "macro", "derive"])
kw("lx0089", 89, '"sealed" | "hidden"', ["sealed", "hidden"])
kw("lx0095", 95, 'TypeKeyword         ::= "struct"', ["struct", "enum", "assoc", "opaque", "error"])
kw("lx0096", 96, '| "unit"', ["unit"])
kw("lx0097", 97, '"trait" | "impl" | "Self"', ["trait", "impl", "Self"])
kw("lx0098", 98, '"Rules" | "limit" | "fixed"', ["Rules", "limit", "fixed"])
kw("lx0100", 100, 'BuiltinType         ::= "int8"', ["int8", "int16", "int32"])
kw("lx0101", 101, '"int64" | "int128" | "int256"', ["int64", "int128", "int256", "int512", "int1024"])
kw("lx0102", 102, '"int2048" | "int4096"', ["int2048", "int4096"])
kw("lx0103", 103, '"uint8" | "uint16"', ["uint8", "uint16"])
kw("lx0104", 104, '"uint32" | "uint64" | "uint128"', ["uint32", "uint64", "uint128", "uint256", "uint512"])
kw("lx0105", 105, '"uint1024" | "uint2048" | "uint4096"', ["uint1024", "uint2048", "uint4096"])
kw("lx0106", 106, '"tbb8" | "tbb16" | "tbb32"', ["tbb8", "tbb16", "tbb32", "tbb64", "tbb128", "tbb256"])
kw("lx0107", 107, '"frac8" | "frac16" | "frac32" | "frac64"', ["frac8", "frac16", "frac32", "frac64"])
kw("lx0108", 108, '"tfp32" | "tfp64" | "tfp128"', ["tfp32", "tfp64", "tfp128", "tfp256", "dim256"])
kw("lx0109", 109, '"flt32" | "flt64" | "flt128"', ["flt32", "flt64", "flt128", "flt256", "flt512"])
kw("lx0110", 110, '"bool" | "char8" | "char16"', ["bool", "char8", "char16", "char32", "string"])
kw("lx0111", 111, '| "cstring"', ["cstring"])
kw("lx0112", 112, '"fd" | "pid" | "tid" | "uid" | "gid"', ["fd", "pid", "tid", "uid", "gid"])
kw("lx0113", 113, '"oflags" | "prot" | "mflags" | "fmode"', ["oflags", "prot", "mflags", "fmode"])
kw("lx0114", 114, '"dyn" | "any" | "Result" | "Optional"', ["dyn", "any", "Result", "Optional"])
kw("lx0115", 115, '"Handle" | "arena" | "shared_arena"', ["Handle", "arena", "shared_arena", "atomic", "Future"])
kw("lx0116", 116, '| "Channel"', ["Channel"])
kw("lx0117", 117, '"Mutex" | "Guard" | "RwLock" | "RGuard"', ["Mutex", "Guard", "RwLock", "RGuard"])
kw("lx0118", 118, '"CondVar" | "Barrier" | "OwnedFd"', ["CondVar", "Barrier", "OwnedFd"])
kw("lx0119", 119, '"simd" | "complex" | "array" | "func"', ["simd", "complex", "array", "func"])
kw("lx0120", 120, '| "range"', ["range"])
kw("lx0121", 121, '"trit" | "tryte" | "nit" | "nyte"', ["trit", "tryte", "nit", "nyte"])
kw("lx0122", 122, '"buffer" | "NIL"', ["buffer", "NIL"])
kw("lx0124", 124, 'BuiltinHelper       ::= "is" | "in" | "is_err"', ["is", "in", "is_err"])

# ------------------------------------------------------------------ the contract comments inside the block
claim("lx0072", D, 72, "`decreases Expr` on a FUNCTION (D-304 (5), 1.5.8c) is the measure a recursive", "rule",
      "A function's `decreases n` is checked at every recursive call: a call with a measure that does "
      "not shrink traps DecreasesViolated.",
      expect="trap:DecreasesViolated",
      src=main_("""    int64:r = raw down(raw v64(3i64));
    if (r == 0i64) { exit 10i32; }
    exit 11i32;""", """func:down = int64(int64:n) decreases n never fails {
    if (n <= 0i64) { pass 0i64; }
    pass (raw down(n));
};"""),
      wrong="StackExhausted (the measure never checked), or 10/11")
claim("lx0076", D, 76, "`while (c) unbounded` -- exactly one of the two, TYPE-072", "rule",
      "A `while` stating both `decreases` and `unbounded` is refused, NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 3i64) decreases 3i64 - i unbounded { i = i + 1i64; }
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("lx0076b", D, 76, "exactly one of the two", "rule",
      "A `while` stating neither `decreases` nor `unbounded` is refused, NITPICK-TYPE-072.",
      expect="refuse:NITPICK-TYPE-072",
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 3i64) { i = i + 1i64; }
    exit 0i32;"""),
      wrong="accepted")
claim("lx0078", D, 78, "arguments and nothing else -- no allocation, no I/O, no suspension, no", "rule",
      "A `pure` function's body is checked: one that allocates (`string_concat`) is refused.",
      expect="refuse",
      src=main_("""    int64:n = raw p();
    if (n != 2i64) { exit 10i32; }
    exit 0i32;""", """func:p = int64() pure never fails {
    string:s = string_concat("a", "b");
    pass string_byte_length(s);
};"""),
      wrong="accepted: the purity not checked")
claim("lx0080", D, 80, "call site inside a contract, which admits only `never fails` `pure` callees", "rule",
      "A contract admits only `never fails` `pure` callees: `requires raw pos(n)` with `pos` not `pure` "
      "is refused.",
      expect="refuse",
      src=main_("""    int32:h = half(raw v32(8i32)) ?| 0i32;
    if (h != 4i32) { exit 10i32; }
    exit 0i32;""", """func:pos = bool(int32:v) never fails { pass (v > 0i32); };
func:half = int32(int32:n) requires raw pos(n) { pass (n / 2i32); };"""),
      wrong="accepted: an impure callee in a contract")
claim("lx0080b", D, 80, "admits only `never fails` `pure` callees", "rule",
      "The permitted twin: `requires raw pos(n)` with `pos` declared `pure never fails` compiles and "
      "`half(8)` is 4.",
      expect="run:0",
      src=main_("""    int32:h = half(raw v32(8i32)) ?| 0i32;
%s
    exit 0i32;""" % chk("h == 4i32", 10), """func:pos = bool(int32:v) pure never fails { pass (v > 0i32); };
func:half = int32(int32:n) requires raw pos(n) { pass (n / 2i32); };"""),
      wrong="refused, or 10")
claim("lx0083", D, 83, "`never fails` is also legal after a function TYPE's parameter list", "rule",
      "`never fails` after a function type's parameter list: `func int64() never fails:f = seven;` and "
      "`raw f()` is 7.",
      expect="run:0",
      src=main_("""    func int64() never fails:f = seven;
%s
    exit 0i32;""" % chk("(raw f()) == 7i64", 10), "func:seven = int64() never fails { pass 7i64; };"),
      wrong="refused")
SEALED = """mod:bank = {
    pub struct:Acct = { sealed int64:bal; hidden int64:key; int64:open; };
    pub func:mk = Acct() never fails { Acct:a = Acct{ bal: 5i64, key: 9i64, open: 1i64 }; pass a; };
};
use bank.{Acct};"""
claim("lx0091", D, 91, "`sealed` and `hidden` are FIELD qualifiers (D-313, D-314): a sealed field is", "rule",
      "A `sealed` field is read anywhere: outside its struct's module, `a.bal` reads 5.",
      expect="run:0",
      src=main_("""    Acct:a = raw bank.mk();
%s
    exit 0i32;""" % chk("a.bal == 5i64", 10), SEALED),
      wrong="refused: the read outside the module")
claim("lx0092", D, 92, "read anywhere and written only by code in the module that declares its", "rule",
      "A `sealed` field is written only inside its struct's module: `a.bal = 6i64;` outside is refused.",
      expect="refuse",
      src=main_("""    Acct:a = raw bank.mk();
    a.bal = raw v64(6i64);
    if (a.bal != 6i64) { exit 10i32; }
    exit 0i32;""", SEALED),
      wrong="accepted: the write outside the module")
claim("lx0093", D, 93, "a hidden field is neither read nor written outside that module", "rule",
      "A `hidden` field is not read outside its struct's module: `a.key` outside is refused.",
      expect="refuse",
      src=main_("""    Acct:a = raw bank.mk();
    if (a.key != 9i64) { exit 10i32; }
    exit 0i32;""", SEALED),
      wrong="accepted: the read outside the module")
free("lx0127", 127, "`vec2`, `vec3`, `vec9`, `matrix`, `tmatrix`, `tensor` and `ttensor` were",
     ["vec2", "vec3", "vec9", "matrix", "tmatrix", "tensor", "ttensor"],
     text="`vec2`, `vec3`, `vec9`, `matrix`, `tmatrix`, `tensor` and `ttensor` are not keywords (D-135): a "
          "local of each name compiles.")

# ------------------------------------------------------------------ the corrections table
free("lx0142", 142, "| `gc` removed from `MemoryQualifier` |", ["gc"], kind="row")
kw("lx0143", 143, "| `fails`, `on`, `with`, `never` added |", ["fails", "on", "with", "never"], kind="row")
kw("lx0144", 144, "| `is_err` added |", ["is_err"], kind="row")
free("lx0145", 145, "| **`ok` removed** |", ["ok"], kind="row")
kw("lx0146", 146, "| `discard` added to `ControlFlow` |", ["discard"], kind="row")
claim("lx0147", D, 147, "| `tbb128`, `tbb256` added |", "row",
      "`tbb128` and `tbb256` are types: `5tbb128 + 5tbb128` is `10tbb128`, and `7tbb256` binds.",
      expect="run:0",
      src=main_("""    tbb128:a = 5tbb128;
    tbb256:b = 7tbb256;
%s
%s
    exit 0i32;""" % (chk("a + a == 10tbb128", 10), chk("b == 7tbb256", 11))),
      wrong="refused: a type unknown")
claim("lx0148", D, 148, "| `fix256` → `dim256` |", "row",
      "`fix256` is no longer a name the language holds, so a local of that name compiles; `dim256` is "
      "reserved.",
      expect="sh:0", sh=kw_sh(reserved=["dim256"], free=["fix256"]),
      wrong="`fix256` still reserved, or `dim256` not")
claim("lx0149", D, 149, "| `tfp128`, `tfp256` added |", "row",
      "`tfp128` and `tfp256` are types: `1.5tfp128 + 1.5tfp128` is `3.0tfp128`, and `2.5tfp256` binds.",
      expect="run:0",
      src=main_("""    tfp128:a = 1.5tfp128;
    tfp256:b = 2.5tfp256;
%s
%s
    exit 0i32;""" % (chk("a + a == 3.0tfp128", 10), chk("b == 2.5tfp256", 11))),
      wrong="refused: a type unknown")
claim("lx0150", D, 150, "| `char8/16/32` added |", "row",
      "`char8` is semantically distinct from `uint8`: binding a `char8` to a `uint8` is refused.",
      expect="refuse",
      src=main_("""    char8:c = 65char8;
    uint8:u = c;
    if (u != 65u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: char8 is uint8")
kw("lx0151", 151, "`Handle`, `arena`, `shared_arena`, `atomic`, `Future`, `Optional`, `simd`, `complex` added",
   ["Handle", "arena", "shared_arena", "atomic", "Future", "Optional", "simd", "complex"], kind="row")
free("lx0152", 152, "| **35 `a*` collection keywords removed** |", ["astack", "alist", "ahash", "astringlist"],
     kind="row")
claim("lx0153", D, 153, "| `fd`, `pid`, `tid`, `uid`, `gid` added |", "row",
      "Kernel identifiers permit no arithmetic: `a + b` on two `fd`s is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "func:sum = fd(fd:a, fd:b) never fails { pass (a + b); };"),
      wrong="accepted: fd arithmetic")
claim("lx0153b", D, 153, "permitting comparison but not arithmetic", "rule",
      "Kernel identifiers permit comparison: `a == b` on two `fd`s compiles.",
      expect="compile",
      src=main_("""    exit 0i32;""", "func:same = bool(fd:a, fd:b) never fails { pass (a == b); };"),
      wrong="refused: comparison refused")
claim("lx0153c", D, 153, "POSIX's `-1` goes to `Result.err` and is not representable", "rule",
      "An `fd` of -1 is not representable: `(-1i32) => fd` is refused.",
      expect="refuse",
      src=main_("""    fd:x = (raw v32(-1i32)) => fd;
    exit 0i32;"""),
      wrong="accepted: -1 is an fd")
claim("lx0154", D, 154, "| `range` added |", "row",
      "`range<T>` can be written: `range<int64>:r = 0i64...3i64;` compiles.",
      expect="compile",
      src=main_("""    range<int64>:r = 0i64...3i64;
    discard(r);
    exit 0i32;"""),
      wrong="refused: the type cannot be written")
claim("lx0155", D, 155, "| `oflags`, `prot`, `mflags`, `fmode` added |", "row",
      "A flag family takes `|` within the family and `=> int32` outbound: `(O_WRONLY | O_CREAT) => int32` "
      "is the two flags' ints or-ed.",
      expect="run:0",
      src=main_("""    oflags:f = O_WRONLY | O_CREAT;
    int32:v = f => int32;
    int32:w = (O_WRONLY => int32) | (O_CREAT => int32);
%s
    exit 0i32;""" % chk("v == w", 10)),
      wrong="refused, or 10")
claim("lx0155b", D, 155, "no arithmetic and no order", "rule",
      "A flag family has no arithmetic: `O_WRONLY + O_CREAT` is refused.",
      expect="refuse",
      src=main_("""    oflags:f = O_WRONLY + O_CREAT;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0155c", D, 155, "no order", "rule",
      "A flag family has no order: `O_WRONLY < O_CREAT` is refused.",
      expect="refuse",
      src=main_("""    bool:b = O_WRONLY < O_CREAT;
    discard(b);
    exit 0i32;"""),
      wrong="accepted")
claim("lx0155d", D, 155, "families never convert to each other", "rule",
      "Flag families never convert to each other: `O_WRONLY => prot` is refused.",
      expect="refuse",
      src=main_("""    prot:p = O_WRONLY => prot;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0155e", D, 155, "`int32 =>! ` inbound", "rule",
      "Inbound to a flag family is `=>!`, not `=>`: `(1i32) => oflags` is refused.",
      expect="refuse",
      src=main_("""    oflags:f = (raw v32(1i32)) => oflags;
    exit 0i32;"""),
      wrong="accepted: a plain inbound cast")
claim("lx0155f", D, 155, "`=> int32` outbound and `int32 =>! ` inbound", "rule",
      "Inbound with `=>!` compiles: `(1i32) =>! oflags`.",
      expect="compile",
      src=main_("""    oflags:f = (raw v32(1i32)) =>! oflags;
    discard(f);
    exit 0i32;"""),
      wrong="refused")
kw("lx0156", 156, "| `assoc` added |", ["assoc"], kind="row")
free("lx0157", 157, "| **`Type` removed** |", ["Type"], kind="row")
free("lx0158", 158, "| **`stream`, `process`, `pipe`, `debug`, `log` removed** |",
     ["stream", "process", "pipe", "debug", "log"], kind="row")
free("lx0159", 159, "| **`const` removed** |", ["const"], kind="row",
     text="`const` is removed and not reserved (D-088's rule): a local named `const` compiles.")
free("lx0160", 160, "| **`binary` removed** |", ["binary"], kind="row")
kw("lx0160b", 160, "`buffer` is retained", ["buffer"])
claim("lx0161", D, 161, "| **`move` moved** from `MemoryQualifier` to `ControlFlow` |", "row",
      "`move(place)` is a keyword operator: `string:t = move(s);` takes the string.",
      expect="run:0",
      src=main_("""    string:s = string_concat("a", "b");
    string:t = move(s);
%s
    exit 0i32;""" % chk('string_equals(t, "ab")', 10)),
      wrong="refused")
claim("lx0161b", D, 161, "marking a CONSUMING parameter", "rule",
      "`move` on a parameter marks it consuming: `take(move(s))` passes the string in.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    int64:n = raw take(move(s));
%s
    exit 0i32;""" % chk("n == 3i64", 10),
                "func:take = int64(move string:p) never fails { pass string_byte_length(p); };"),
      wrong="refused, or 10")
claim("lx0161c", D, 161, "is refused (`NITPICK-MOVE-004`) anywhere but a parameter", "rule",
      "`move` in a declaration anywhere but a parameter is refused, NITPICK-MOVE-004.",
      expect="refuse:NITPICK-MOVE-004",
      src=main_("""    move string:t = string_concat("a", "b");
    discard(t);
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
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
claim("lx0162", D, 162, "| **`relay` and `_^` added** |", "row",
      "`relay` forwards the error's code verbatim and runs `defer`: the caller's arm `(E1)` matches, and "
      "the deferred write happened.",
      expect="run:0", src=main_(RELAY_MAIN, RELAY % "relay"),
      wrong="another identity (10), or the defer skipped (11)")
claim("lx0162b", D, 162, "`relay` forwards the code verbatim and runs `defer`", "rule",
      "`_^` is `relay`'s operator: `_^ inner(v)` forwards the code and runs `defer` the same way.",
      expect="run:0", src=main_(RELAY_MAIN, RELAY % "_^"),
      wrong="refused, or 10/11")
kw("lx0163", 163, "| `Self` added |", ["Self"], kind="row")
claim("lx0164", D, 164, "| `NIL` added to `BuiltinType` |", "row",
      "`NIL` is a type: `func:reset = NIL(int32->:a)` compiles, and its call writes through the pointer.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(5i32);
    drop reset(@x);
%s
    exit 0i32;""" % chk("x == 0i32", 10), "func:reset = NIL(int32->:a) never fails { <-a = 0i32; pass NIL; };"),
      wrong="refused: NIL not a type")
claim("lx0165", D, 165, "| `cstring` added to `BuiltinType` |", "row",
      "`cstring` is a builtin type's keyword: a user type named `cstring` is refused, never a shadow.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "struct:cstring = { int32:x; };"),
      wrong="accepted: the builtin silently shadowed")
claim("lx0166", D, 166, "`result` is the SUCCESS value in `ensures`", "row",
      "`result` names the success value in `ensures`: `ensures result == x + 1i32` holds for `inc`.",
      expect="run:0",
      src=main_("""    int32:v = inc(raw v32(4i32)) ?| 0i32;
%s
    exit 0i32;""" % chk("v == 5i32", 10),
                "func:inc = int32(int32:x) ensures result == x + 1i32 { pass (x + 1i32); };"),
      wrong="refused: `result` unbound, or EnsuresViolated")
claim("lx0167", D, 167, "checked in every build, `DecreasesViolated`", "row",
      "A `while`'s `decreases` is checked in every build: a measure that does not shrink traps "
      "DecreasesViolated.",
      expect="trap:DecreasesViolated",
      src=main_("""    int64:i = raw v64(0i64);
    while (i < 3i64) decreases raw v64(5i64) { i = i + 1i64; }
    exit 10i32;"""),
      wrong="10: the measure never checked")
claim("lx0168", D, 168, "| `pure` added to `VerificationKeyword` |", "row",
      "Purity is checked in the body: a `pure` function calling one that is not `pure` is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw p(raw v32(3i32));
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", """func:q = int32(int32:x) never fails { pass x; };
func:p = int32(int32:x) pure never fails { pass (raw q(x)); };"""),
      wrong="accepted: an impure callee")
claim("lx0168b", D, 168, "`pure` never rides a function TYPE", "rule",
      "`pure` never rides a function type: `func int64() pure never fails:f` is refused.",
      expect="refuse",
      src=main_("""    func int64() pure never fails:f = seven;
    discard(raw f());
    exit 0i32;""", "func:seven = int64() pure never fails { pass 7i64; };"),
      wrong="accepted")
claim("lx0169", D, 169, "`for` is **not** duplicated", "row",
      "`for` is one reserved token.",
      untestable="[vague] the row states the grammar's bookkeeping; that `for` is reserved is lx0056's claim")

# ================================================================== 5. operators and punctuation
claim("lx0173", D, 173, "```ebnf", "example",
      "The arithmetic, compound, comparison, logical and bitwise operators of the block lex and compute: "
      "a program using each gets the expected values.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(12i32);
    int32:b = raw v32(5i32);
    int32:x = a;
    x += 1i32; x -= 2i32; x *= 3i32; x /= 11i32; x %%= 2i32;
    int32:y = raw v32(6i32);
    y &= 3i32; y |= 8i32; y ^= 1i32; y <<= 2i32; y >>= 1i32;
%s
%s
%s
%s
%s
%s
    exit 0i32;""" % (chk("a + b == 17i32 && a - b == 7i32 && a * b == 60i32 && a / b == 2i32 && a %% b == 2i32", 10),
                      chk("x == 1i32", 11), chk("y == 22i32", 12),
                      chk("(a == 12i32) && (a != b) && (b < a) && (b <= 5i32) && (a > b) && (a >= 12i32)", 13),
                      chk("((a & b) == 4i32) && ((a | b) == 13i32) && ((a ^ b) == 9i32) && ((~b) == -6i32)", 14),
                      chk("((b << 2i32) == 20i32) && ((a >> 2i32) == 3i32) && (!(a < b) || false)", 15))),
      wrong="refused (an operator not lexed), or 10-15")
claim("lx0174", D, 174, '"++" | "--"', "rule",
      "`++` and `--` are operator tokens: `x++; x--;` compiles.",
      expect="compile",
      src=main_("""    int32:x = raw v32(1i32);
    x++;
    x--;
    discard(x);
    exit 0i32;"""),
      wrong="refused: the tokens are not the language's")
claim("lx0178", D, 178, '"<=>"', "rule",
      "`<=>` is an operator: `a <=> b` compiles and orders (-1 when a < b).",
      expect="run:0",
      src=main_("""    int32:c = raw v32(1i32) <=> raw v32(2i32);
%s
    exit 0i32;""" % chk("c < 0i32", 10)),
      wrong="refused (DEF-131's shape), or 10")
claim("lx0186", D, 186, 'CompilerSigil ::= "#"', "rule",
      "`#` addresses the compiler: `#size_of<int64>()` is 8.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<int64>() == 8i64", 10)),
      wrong="refused, or 10")
claim("lx0191", D, 191, "`=>` and `=>!` are the *only*", "rule",
      "`=>` and `=>!` are the only cast forms: a C-style cast `(int64)x` is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(3i32);
    int64:y = (int64)x;
    exit 0i32;"""),
      wrong="accepted: a third cast form")
claim("lx0191b", D, 191, "**`=>!` added**", "rule",
      "`x as int64` is no cast either: refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(3i32);
    int64:y = x as int64;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0195", D, 195, "It was formerly", "rule",
      "`#` is not a value operator (the old pin): `#x` on a value is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(3i32);
    int32:y = #x;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0203", D, 203, "**The wrapping family `+% -% *%`**", "rule",
      "`+%` computes modulo 2^N and never traps: `127i8 +% 1i8` is -128.",
      expect="run:0",
      src=main_("""    int8:a = raw v8(127i8) +%% 1i8;
    int8:b = raw v8(-127i8 - 1i8) -%% 1i8;
    int8:c = raw v8(64i8) *%% 2i8;
%s
%s
%s
    exit 0i32;""" % (chk("a == -127i8 - 1i8", 10), chk("b == 127i8", 11), chk("c == -127i8 - 1i8", 12))),
      wrong="IntOverflow (93), or 10-12")
claim("lx0204", D, 204, "forms `+%= -%= *%=`", "rule",
      "The compound forms wrap: `u +%= 1u8` from 255 is 0, `-%=` back is 255, `*%= 2u8` is 254.",
      expect="run:0",
      src=main_("""    uint8:u = raw vu8(255u8);
    u +%%= 1u8;
%s
    u -%%= 1u8;
%s
    u *%%= 2u8;
%s
    exit 0i32;""" % (chk("u == 0u8", 10), chk("u == 255u8", 11), chk("u == 254u8", 12))),
      wrong="refused, a trap, or 10-12")
claim("lx0204b", D, 204, "Plain `+ - *` TRAP on overflow (D-210)", "rule",
      "Plain `+` traps on overflow: `127i8 + 1i8` traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    int8:a = raw v8(127i8) + 1i8;
    if (a < 0i8) { exit 10i32; }
    exit 11i32;"""),
      wrong="wraps (10)")
claim("lx0208", D, 208, "They are the longest match, so `a +% b` is one token", "rule",
      "`a + %b` was never a program (`%` starts no expression): refused.",
      expect="refuse",
      src=main_("""    int32:a = raw v32(1i32);
    int32:b = raw v32(2i32);
    int32:c = a + %%b;
    exit 0i32;"""),
      wrong="accepted")

# ------------------------------------------------------------------ 5.1 the range and spread family
claim("lx0218", D, 218, "| `..` | inclusive range `[a, b]` | expression |", "row",
      "`..` is inclusive: summing `1i64..3i64` is 6.",
      expect="run:0",
      src=main_("""    int64:s = 0i64;
    for (int64:i in 1i64..3i64) { s = s + i; }
%s
    exit 0i32;""" % chk("s == 6i64", 10)),
      wrong="3 (exclusive), or refused")
claim("lx0219", D, 219, "| `...` | exclusive range `[a, b)` | expression |", "row",
      "`...` is exclusive: summing `1i64...3i64` is 3.",
      expect="run:0",
      src=main_("""    int64:s = 0i64;
    for (int64:i in 1i64...3i64) { s = s + i; }
%s
    exit 0i32;""" % chk("s == 3i64", 10)),
      wrong="6 (inclusive), or refused")
TOTAL = """func:total = int64(int64:base, ..*int64[]:rest) never fails {
    int64:acc = base;
    int64:i = 0i64;
    while (i < rest.len) decreases rest.len - i {
        acc = acc + rest[i];
        i = i + 1i64;
    }
    pass acc;
};"""
claim("lx0220", D, 220, "| `..*` | variadic rest marker — **collects** arguments | declaration site |", "row",
      "`..*` collects the trailing arguments: `total(1, 2, 3)` is 6.",
      expect="run:0",
      src=main_("""    int64:t = raw total(1i64, 2i64, 3i64);
%s
    exit 0i32;""" % chk("t == 6i64", 10), TOTAL),
      wrong="refused, or 10")
claim("lx0221", D, 221, "| `..^` | spread — **expands** a collection into arguments | call site |", "row",
      "`..^` spreads a slice into the arguments: `total(1, ..^xs)` with `xs` = [2, 3] is 6.",
      expect="run:0",
      src=main_("""    int64[3]:arr = [2i64, 3i64, 4i64];
    int64[]:xs = arr[0i32...2i32];
    int64:t = raw total(1i64, ..^xs);
%s
    exit 0i32;""" % chk("t == 6i64", 10), TOTAL),
      wrong="refused, or 10")
claim("lx0223", D, 223, "`..*` and `..^` are inverses. Confirmed against the prototype:", "rule",
      "`..*` and `..^` are inverses, confirmed against the prototype's parser.",
      untestable="[tree] the confirmation cites the prototype's and the compiler's own sources; lx0221 "
                 "spreads what lx0220 collects")

# ------------------------------------------------------------------ 5.2 and 5.3
claim("lx0231", D, 231, "`>>` is the right-shift operator **and** the closing bracket pair of a nested", "rule",
      "`>>` closes a nested generic: `Result<List<int64>>:r = mk();` compiles and the list is usable.",
      expect="run:0",
      src=main_("""    Result<List<int64>>:r = mk();
    if (r.is_error) { exit 10i32; }
    exit 0i32;""", "func:mk = List<int64>() { List<int64>:l = raw list_init::<int64>(2i64); pass l; };"),
      wrong="refused: `>>` read as a shift")
claim("lx0239", D, 239, "Explicit type arguments in expression position are always written", "rule",
      "Explicit type arguments in an expression need the turbofish: `idt<int32>(5i32)` is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw idt<int32>(raw v32(5i32));
    exit 0i32;""", "func:idt<T> = T(T:x) never fails { pass x; };"),
      wrong="accepted: `<` opened a type-argument list in an expression")
claim("lx0240", D, 240, "with the turbofish", "rule",
      "With the turbofish, `idt::<int32>(5i32)` is 5.",
      expect="run:0",
      src=main_("""    int32:v = raw idt::<int32>(raw v32(5i32));
%s
    exit 0i32;""" % chk("v == 5i32", 10), "func:idt<T> = T(T:x) never fails { pass x; };"),
      wrong="refused")
claim("lx0241", D, 241, "splits inside a type-argument list and is a right-shift everywhere outside one", "rule",
      "Outside a type-argument list `>>` is a right shift: `64 >> 2` is 16.",
      expect="run:0",
      src=main_("""    int32:v = raw v32(64i32) >> 2i32;
%s
    exit 0i32;""" % chk("v == 16i32", 10)),
      wrong="refused, or 10")
claim("lx0251", D, 251, "| **leading** | negation | `!x`, `!=` |", "row",
      "A leading `!` negates: `!t` is false, and `a != b` compares.",
      expect="run:0",
      src=main_("""    bool:t = raw vb(true);
    int32:a = raw v32(1i32);
%s
%s
    exit 0i32;""" % (chk("(!t) == false", 10), chk("a != 2i32", 11))),
      wrong="refused, or 10/11")
claim("lx0252", D, 252, "| **trailing or repeated** | unchecked / emphatic | `?!`, `=>!`, `_!`, `!!!` |", "row",
      "The trailing forms lex as their operators: `?!`, `=>!` and `_!` compile and compute; `!!! E1;` "
      "goes to failsafe's `E1` arm (81).",
      expect="run:81",
      src=main_("""    int32:a = k(raw v32(3i32)) ?! E1;
    int8:b = (raw v32(5i32)) =>! int8;
    int32:c = _! g(raw v32(2i32));
    if (a + (b => int32) + c != 10i32) { exit 10i32; }
    !!! E1;
    exit 11i32;""", """error:E1;
func:k = int32(int32:x) { pass x; };
func:g = int32(int32:x) never fails { pass x; };"""),
      wrong="refused (a form not lexed), 10, or 11 (`!!!` did nothing)")
claim("lx0254", D, 254, "**`!!` no longer exists.**", "rule",
      "`!!` no longer exists: `asm!!` is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    Result<int32>:r = asm!!<int32>("x86_64", "mov %1, %0", "=r,r", x);
    exit 0i32;"""),
      wrong="accepted")
claim("lx0256", D, 256, "full-tier syscall is spelled **`sys_full`**", "rule",
      "The full-tier syscall is spelled `sys_full`: `sys_full(39i64)` compiles.",
      expect="compile",
      src=main_("""    Result<int64>:p = sys_full(39i64);
    if (p.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: no `sys_full`")
claim("lx0259", D, 259, "**Macro invocation is `#name(args)`**, not `name!(args)` (D-046)", "rule",
      "A macro is not invoked as `name!(args)`: `seven!()` is refused.",
      expect="refuse",
      src=main_("""    int32:v = seven!();
    exit 0i32;""", "macro:seven = () { 7i32; };"),
      wrong="accepted")
claim("lx0259b", D, 259, "**Macro invocation is `#name(args)`**", "rule",
      "A macro is invoked as `#name(args)`: `#seven()` is 7.",
      expect="run:0",
      src=main_("""    int32:v = #seven();
%s
    exit 0i32;""" % chk("v == 7i32", 10), "macro:seven = () { 7i32; };"),
      wrong="refused, or 10")

# ================================================================== 6. literals
claim("lx0269", D, 269, "```ebnf", "example",
      "`true`, `false`, `NIL` and `ERR` are literals: each binds where its type is expected.",
      expect="run:0",
      src=main_("""    bool:t = true;
    bool:f = false;
    int32?:o = NIL;
    tbb8:e = ERR;
%s
%s
%s
    exit 0i32;""" % (chk("t && !f", 10), chk("o == NIL", 11), chk("is_err(e)", 12))),
      wrong="refused, or 10-12")
claim("lx0271", D, 271, 'SentinelLiteral ::= "NULL" | "NIL" | "ERR"', "rule",
      "`NULL` is a literal: `int8->:p = NULL;` compiles.",
      expect="compile",
      src=main_("""    int8->:p = NULL;
    discard(p);
    exit 0i32;"""),
      wrong="refused")
claim("lx0274", D, 274, "**`unknown` is not a literal.**", "rule",
      "`unknown` is not a literal: `int32:x = unknown;` is refused.",
      expect="refuse",
      src=main_("""    int32:x = unknown;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0279", D, 279, "`ERR` **is** writable", "rule",
      "`ERR` is writable and is a `pick` label: a `tbb8` holding `ERR` takes the `ERR:` arm.",
      expect="run:0",
      src=main_("""    tbb8:t = ERR;
    int32:r = 0i32;
    pick (t) { (5tbb8) { r = 1i32; }, ERR: { r = 2i32; }, (*) { r = 3i32; } }
%s
    exit 0i32;""" % chk("r == 2i32", 10)),
      wrong="refused, or another arm (10)")
claim("lx0284", D, 284, "Underscores are permitted for readability and ignored", "rule",
      "Underscores in a literal are ignored: `1_000i32` is 1000.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("1_000i32 == 1000i32", 10)),
      wrong="refused, or 10")
claim("lx0287", D, 287, "leading significant digit is a letter takes a value-neutral leading zero", "rule",
      "A value whose leading digit is a letter takes a leading zero: `0FFhex` is 255, `0Tt` is -1, `0an` "
      "is -1.",
      expect="run:0",
      src=main_("""    int32:a = 0FFhex;
    int32:b = 0Tt;
    int32:c = 0an;
%s
%s
%s
    exit 0i32;""" % (chk("a == 255i32", 10), chk("b == -1i32", 11), chk("c == -1i32", 12))),
      wrong="refused, or 10-12")
claim("lx0290", D, 290, "```ebnf", "example",
      "Every base is a suffix: `10`, `0Ahex`, `1010bin`, `12oct`, `101t` and `11n` are each 10.",
      expect="run:0",
      src=main_("""    int32:a = 10;
    int32:b = 0Ahex;
    int32:c = 1010bin;
    int32:d = 12oct;
    int32:e = 101t;
    int32:f = 11n;
%s
%s
    exit 0i32;""" % (chk("a == 10i32 && b == 10i32 && c == 10i32", 10),
                      chk("d == 10i32 && e == 10i32 && f == 10i32", 11))),
      wrong="refused, or 10/11")
claim("lx0296", D, 296, 'DecimalLiteral ::= [0-9] ([0-9_]* [0-9])?', "rule",
      "Underscores may stand anywhere inside the digits: `1__0i32` is 10.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("1__0i32 == 10i32", 10)),
      wrong="refused, or 10")
claim("lx0296b", D, 296, "([0-9_]* [0-9])?", "rule",
      "A decimal literal ends with a digit: `10_i32` (a trailing underscore) is refused.",
      expect="refuse",
      src=main_("""    int32:x = 10_i32;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0297", D, 297, 'HexLiteral     ::= [0-9] ([0-9a-fA-F_]* [0-9a-fA-F])? "hex"', "rule",
      "Hex digits take either case: `0ffhex` equals `0FFhex`.",
      expect="run:0",
      src=main_("""    int32:a = 0ffhex;
    int32:b = 0FFhex;
%s
    exit 0i32;""" % chk("a == b && a == 255i32", 10)),
      wrong="refused, or 10")
claim("lx0302", D, 302, 'TernaryLiteral ::= [01] ([01Tt_]* [01Tt])? ("t" | "ter" | "tri")', "rule",
      "Balanced ternary takes the suffixes `t`, `ter` and `tri`, and `T` or `t` is -1: `1Tt`, `1Tter`, "
      "`1Ttri` and `1tt` are each 2.",
      expect="run:0",
      src=main_("""    int32:a = 1Tt;
    int32:b = 1Tter;
    int32:c = 1Ttri;
    int32:d = 1tt;
%s
    exit 0i32;""" % chk("a == 2i32 && b == 2i32 && c == 2i32 && d == 2i32", 10)),
      wrong="refused, or 10")
claim("lx0305", D, 305, 'NonaryLiteral  ::= [0-4] ([0-4a-dA-D_]* [0-4a-dA-D])? ("non" | "n")', "rule",
      "Balanced nonary takes `non` and `n`, and a..d / A..D are -1..-4: `1an` is 8, `1dn` and `1Dnon` are 5.",
      expect="run:0",
      src=main_("""    int32:a = 1an;
    int32:b = 1dn;
    int32:c = 1Dnon;
%s
    exit 0i32;""" % chk("a == 8i32 && b == 5i32 && c == 5i32", 10)),
      wrong="refused, or 10")
claim("lx0307", D, 307, 'FloatLiteral   ::= DecimalLiteral "." DecimalLiteral Exponent? TypeSuffix?', "rule",
      "A float literal with an exponent: `1.5e2f64` is 150.0.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("1.5e2f64 == 150.0f64", 10)),
      wrong="refused, or 10")
claim("lx0307b", D, 307, 'DecimalLiteral "." DecimalLiteral', "rule",
      "A float needs digits on both sides of the point: `.5f64` is refused.",
      expect="refuse",
      src=main_("""    flt64:x = .5f64;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0308", D, 308, 'Exponent       ::= [eE] [+-]? DecimalLiteral', "rule",
      "An exponent takes a sign and either case: `15.0E-1f64` is 1.5.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("15.0E-1f64 == 1.5f64", 10)),
      wrong="refused, or 10")


def suffixes(cid, line, quote, decls, text):
    claim(cid, D, line, quote, "rule", text, expect="compile",
          src=main_("\n".join("    %s;" % d for d in decls) + "\n" +
                    "\n".join("    discard(%s);" % d.split(":")[1].split(" ")[0] for d in decls) +
                    "\n    exit 0i32;"),
          wrong="refused: a suffix not the language's")


suffixes("lx0310", 310, 'TypeSuffix     ::= "u8" | "u16" | "u32" | "u64" | "u128"',
         ["uint8:a = 1u8", "uint16:b = 1u16", "uint32:c = 1u32", "uint64:d = 1u64", "uint128:e = 1u128"],
         "The suffixes `u8` … `u128` are literals' types.")
suffixes("lx0311", 311, '"u256" | "u512" | "u1024" | "u2048" | "u4096"',
         ["uint256:a = 1u256", "uint512:b = 1u512", "uint1024:c = 1u1024", "uint2048:d = 1u2048",
          "uint4096:e = 1u4096"],
         "The suffixes `u256` … `u4096` are literals' types.")
suffixes("lx0312", 312, '"i8" | "i16" | "i32" | "i64" | "i128"',
         ["int8:a = 1i8", "int16:b = 1i16", "int32:c = 1i32", "int64:d = 1i64", "int128:e = 1i128"],
         "The suffixes `i8` … `i128` are literals' types.")
suffixes("lx0313", 313, '"i256" | "i512" | "i1024" | "i2048" | "i4096"',
         ["int256:a = 1i256", "int512:b = 1i512", "int1024:c = 1i1024", "int2048:d = 1i2048",
          "int4096:e = 1i4096"],
         "The suffixes `i256` … `i4096` are literals' types.")
suffixes("lx0314", 314, '"tbb8" | "tbb16" | "tbb32" | "tbb64" | "tbb128" | "tbb256"',
         ["tbb8:a = 1tbb8", "tbb16:b = 1tbb16", "tbb32:c = 1tbb32", "tbb64:d = 1tbb64", "tbb128:e = 1tbb128",
          "tbb256:f = 1tbb256"],
         "The `tbb` suffixes are literals' types.")
suffixes("lx0315", 315, '"f32" | "f64" | "f128"',
         ["flt32:a = 1.5f32", "flt64:b = 1.5f64", "flt128:c = 1.5f128"],
         "The suffixes `f32`, `f64` and `f128` are float literals' types.")
suffixes("lx0316", 316, '"tfp32" | "tfp64" | "tfp128" | "tfp256" | "dim256"',
         ["tfp32:a = 1.5tfp32", "tfp64:b = 1.5tfp64", "tfp128:c = 1.5tfp128", "tfp256:d = 1.5tfp256",
          "dim256<Meters>:e = 1.5dim256<Meters>"],
         "The `tfp` suffixes and `dim256` are literals' types.")
suffixes("lx0317", 317, '"char8" | "char16" | "char32"',
         ["char8:a = 65char8", "char16:b = 65char16", "char32:c = 65char32"],
         "The `char` suffixes are literals' types.")
claim("lx0321", D, 321, "verified EXACTLY at scan time (`NITPICK-LEX-004`)", "rule",
      "A literal outside the signed 64-bit envelope is refused at scan time, NITPICK-LEX-004.",
      expect="refuse:NITPICK-LEX-004",
      src=main_("""    uint64:x = 9223372036854775808u64;
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("lx0323", D, 323, "(`NITPICK-TYPE-031`)", "rule",
      "A literal must fit its type, checked at the literal: `300i8` is refused, NITPICK-TYPE-031.",
      expect="refuse:NITPICK-TYPE-031",
      src=main_("""    int8:x = 300i8;
    exit 0i32;"""),
      wrong="accepted (truncated), or refused with another code")
claim("lx0324", D, 324, "(`0u64 - 1u64` is the maximum)", "rule",
      "`0u64 - 1u64` is uint64's maximum.",
      expect="run:0",
      src=main_("""    uint64:m = 0u64 - 1u64;
%s
    exit 0i32;""" % chk("m == ~0u64", 10)),
      wrong="refused (TYPE-076), IntOverflow, or 10",
      note="lines 328-334 say the spelling is refused since 1.5.8b step 2 (lx0330): the text holds both")
claim("lx0326", D, 326, "`0b4bni8` is −128", "rule",
      "`0b4bni8` is -128.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("0b4bni8 == -127i8 - 1i8", 10)),
      wrong="refused, or 10")
claim("lx0330", D, 330, "from 1.5.8b step 2 the spelling is refused", "rule",
      "From 1.5.8b step 2, `0u64 - 1u64` is refused, NITPICK-TYPE-076.",
      expect="refuse:NITPICK-TYPE-076",
      src=main_("""    uint64:m = 0u64 - 1u64;
    discard(m);
    exit 0i32;"""),
      wrong="accepted (the folder's wrap)")
claim("lx0332", D, 332, "`~0u64` is the maximum", "rule",
      "`~0u64` is uint64's maximum: every bit set.",
      expect="run:0",
      src=main_("""    uint64:m = ~0u64;
%s
    exit 0i32;""" % chk("m == ((1u64 << 63u64) | ((1u64 << 63u64) - 1u64))", 10)),
      wrong="refused, or 10")
claim("lx0332b", D, 332, "`(1u64 << 63u64) | k` gives", "rule",
      "`(1u64 << 63u64) | k` builds a value above 2^63-1: with `k` = `04BF29CE484222325hexu64` it is "
      "above 9223372036854775807.",
      expect="run:0",
      src=main_("""    uint64:v = (1u64 << 63u64) | 04BF29CE484222325hexu64;
%s
%s
    exit 0i32;""" % (chk("v > 9223372036854775807u64", 10),
                      chk("(v & 9223372036854775807u64) == 5472609002491880229u64", 11))),
      wrong="refused, or 10/11")
claim("lx0334", D, 334, "`0u64 -% 1u64` also works", "rule",
      "`0u64 -% 1u64` wraps to the maximum.",
      expect="run:0",
      src=main_("""    uint64:m = 0u64 -%% 1u64;
%s
    exit 0i32;""" % chk("m == ~0u64", 10)),
      wrong="refused, or 10")
free("lx0337", 337, "`FFhex`,", ["FFhex", "an", "ban", "tt"],
     text="By D-147 `FFhex`, `an`, `ban` and `tt` are ordinary identifiers: a local of each name compiles.")
claim("lx0338", D, 338, "`an`, `ban`, `tt` are ordinary identifiers; the values they used to spell are", "rule",
      "The values those words used to spell are `0FFhex` (255), `0an` (-1), `0ban` (-19) and `0tt` (-1).",
      expect="run:0",
      src=main_("""    int32:a = 0FFhex;
    int32:b = 0an;
    int32:c = 0ban;
    int32:d = 0tt;
%s
%s
    exit 0i32;""" % (chk("a == 255i32 && b == -1i32", 10), chk("c == -19i32 && d == -1i32", 11))),
      wrong="refused, or 10/11")
claim("lx0343", D, 343, "The **legacy C-style prefixes** (`0x`, `0b`, `0o`, `0n`)", "rule",
      "The C-style `0o` prefix is removed: `0o17` is refused.",
      expect="refuse",
      src=main_("""    int32:x = 0o17;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0346", D, 346, "`0xFF` is a bad-digit error at the `x`", "rule",
      "`0xFF` is a bad-digit error at the `x`, NITPICK-LEX-003.",
      expect="refuse:NITPICK-LEX-003",
      src=main_("""    int32:x = 0xFF;
    exit 0i32;"""),
      wrong="accepted, or refused with another code")
claim("lx0349", D, 349, "**Ternary/nonary use the suffix form**", "rule",
      "The prefix form of a ternary literal (`0t1T`) is not the language's: refused.",
      expect="refuse",
      src=main_("""    int32:x = 0t1T;
    exit 0i32;"""),
      wrong="accepted")
claim("lx0353", D, 353, "`int2048` and `int4096` have no direct source literal", "rule",
      "`int2048` has no direct source literal: `5i2048` is refused.",
      expect="refuse",
      src=main_("""    int2048:x = 5i2048;
    exit 0i32;"""),
      wrong="accepted",
      note="line 313 lists `i2048` and `i4096` among the suffixes (lx0313): the text holds both")
claim("lx0354", D, 354, "are instantiated by parsing", "rule",
      "Such a value is instantiated by parsing: `parse_uint2048(\"1.5e308\")` compiles.",
      expect="compile",
      src=main_("""    Result<uint2048>:r = parse_uint2048("1.5e308");
    if (r.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: no `parse_uint2048`")

# ------------------------------------------------------------------ 6.3 strings and characters
claim("lx0358", D, 358, "```ebnf", "example",
      "Each escape is its byte: `\\n \\r \\t \\\\ \\\" \\' \\0 \\x41 \\u{42}` is nine bytes 10 13 9 92 34 39 0 65 66.",
      expect="run:0",
      src=main_("""    string:s = "\\n\\r\\t\\\\\\"\\'\\0\\x41\\u{42}";
%s
%s
%s
    exit 0i32;""" % (chk("string_byte_length(s) == 9i64", 10),
                      chk("string_bytes(s)[0i64] == 10u8 && string_bytes(s)[1i64] == 13u8 && string_bytes(s)[2i64] == 9u8 && string_bytes(s)[3i64] == 92u8", 11),
                      chk("string_bytes(s)[4i64] == 34u8 && string_bytes(s)[5i64] == 39u8 && string_bytes(s)[6i64] == 0u8 && string_bytes(s)[7i64] == 65u8 && string_bytes(s)[8i64] == 66u8", 12))),
      wrong="refused (an escape unknown), or 10-12")
claim("lx0365", D, 365, "RawStringLiteral   ::= \"r\" '\"' (SourceCharacter - '\"')* '\"'", "rule",
      "A raw string performs no escape processing: `r\"a\\nb\"` is four bytes, the second a backslash.",
      expect="run:0",
      src=main_("""    string:s = r"a\\nb";
%s
%s
    exit 0i32;""" % (chk("string_byte_length(s) == 4i64", 10), chk("string_bytes(s)[1i64] == 92u8", 11))),
      wrong="refused, or the escape processed (10/11)")
claim("lx0366", D, 366, "BlockStringLiteral ::= '\"\"\"' (SourceCharacter - '\"\"\"')* '\"\"\"'", "rule",
      "A block string holds a lone `\"`: `\"\"\"a\"b\"\"\"` is the three bytes `a\"b`.",
      expect="run:0",
      src=main_('''    string:s = """a"b""";
%s
    exit 0i32;''' % chk("string_byte_length(s) == 3i64 && string_bytes(s)[1i64] == 34u8", 10)),
      wrong="refused, or 10")
claim("lx0368", D, 368, "CharacterLiteral   ::= \"'\"", "rule",
      "A character literal takes an escape: `'\\n'` is 10char8, and `'A'` is 65char8.",
      expect="run:0",
      src=main_("""    char8:c = '\\n';
    char8:d = 'A';
%s
    exit 0i32;""" % chk("c == 10char8 && d == 65char8", 10)),
      wrong="refused, or 10")
claim("lx0377", D, 377, "preserves newlines and indentation verbatim", "rule",
      "A block string preserves newlines and indentation verbatim: a newline and two spaces stay.",
      expect="run:0",
      src=main_('''    string:s = """a
  b""";
%s
    exit 0i32;''' % chk("string_byte_length(s) == 5i64 && string_bytes(s)[1i64] == 10u8 && string_bytes(s)[2i64] == 32u8", 10)),
      wrong="refused, or 10 (the newline or the spaces dropped)")
claim("lx0377b", D, 377, "ends at the FIRST `\"\"\"`: a `\"`", "rule",
      "A `\"\"` inside a block string is body text: `\"\"\"a\"\"b\"\"\"` is the four bytes `a\"\"b`.",
      expect="run:0",
      src=main_('''    string:s = """a""b""";
%s
    exit 0i32;''' % chk("string_byte_length(s) == 4i64", 10)),
      wrong="refused (DEF-98's shape: the block closed at `\"\"`), or 10")
claim("lx0383", D, 383, "Backtick-delimited, with `&{ … }` interpolation", "rule",
      "A template literal interpolates `&{ … }`: `` `x&{ n }y` `` with n = 5 is \"x5y\".",
      expect="run:0",
      src=main_("""    int32:n = raw v32(5i32);
    string:s = `x&{ n }y`;
%s
    exit 0i32;""" % chk('string_equals(s, "x5y")', 10)),
      wrong="refused, or 10")
claim("lx0383b", D, 383, "The lexer decomposes a template", "rule",
      "The lexer decomposes a template into TEMPLATE_START, TEMPLATE_PART, INTERP_START, INTERP_END, "
      "TEMPLATE_END.",
      untestable="[internal] the token kinds are the lexer's; lx0383 and lx0387 test the literal")
claim("lx0387", D, 387, "```ebnf", "example",
      "A template holds several interpolations of expressions: `` `&{ a }+&{ b }=&{ a + b }` `` is \"2+3=5\".",
      expect="run:0",
      src=main_("""    int32:a = raw v32(2i32);
    int32:b = raw v32(3i32);
    string:s = `&{ a }+&{ b }=&{ a + b }`;
%s
    exit 0i32;""" % chk('string_equals(s, "2+3=5")', 10)),
      wrong="refused, or 10")

# ================================================================== open items (the settled ones)
claim("lx0405", D, 405, "Ownership transfers only where `move` is written", "rule",
      "Ownership never transfers implicitly: `string:t = s;` is refused.",
      expect="refuse",
      src=main_("""    string:s = string_concat("a", "b");
    string:t = s;
    discard(t);
    exit 0i32;"""),
      wrong="accepted: an implicit move or copy")
claim("lx0406", D, 406, "implicitly — and the moved-from binding is invalid until reinitialized", "rule",
      "A moved-from binding is invalid: reading `s` after `move(s)` is refused.",
      expect="refuse",
      src=main_("""    string:s = string_concat("a", "b");
    string:t = move(s);
    int64:n = string_byte_length(s);
    discard(t);
    if (n != 2i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: a read of a moved-from string")
claim("lx0406b", D, 406, "until reinitialized", "rule",
      "Reinitialised after the move, the binding is valid again: `s` assigned anew reads its new value.",
      expect="run:0",
      src=main_("""    string:s = string_concat("a", "b");
    string:t = move(s);
    s = string_concat("xy", "z");
%s
%s
    exit 0i32;""" % (chk("string_byte_length(s) == 3i64", 10), chk('string_equals(t, "ab")', 11))),
      wrong="refused: still moved-from")
claim("lx0408", D, 408, "`impl` now takes", "rule",
      "`impl` takes no connector: `impl:Box:Show = {};` implements the trait, and `b.show()` is 7.",
      expect="run:0",
      src=main_("""    Box:b = Box{ n: 1i64 };
%s
    exit 0i32;""" % chk("(raw b.show()) == 7i32", 10), """struct:Box = { int64:n; };
trait:Show = {
    func:show = int32(Self:self) never fails { pass 7i32; };
};
impl:Box:Show = {};"""),
      wrong="refused")
