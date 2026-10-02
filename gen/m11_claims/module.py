"""M11 claims: MODULE_REFERENCE.md (lines 1-300) at HUNT2 (9126350), extracted by session 9.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). No M10 item tests a MODULE sentence.

The spellings around each claim are those of the compiler's own module programs at
HUNT2 (`tests/backend/programs/mod_qualified.npk`, `mod_file_import.npk`,
`error_arm_forms.npk`): an inline module `mod:m = { ... };`, `pub fixed` for a module
constant, and an error arm qualified by the declaring FILE's basename. A failsafe must
name every error constant that can reach it (REACH-002: `(*)` counts for nothing), so
a program raising its own constant to failsafe writes its own failsafe.

Some layouts are not claim programs: a support file in a subdirectory, a header the
claim is about, an empty file, and the `extern` blocks written in HUNT2's form (they
need the compiler's own `lib/nbridge.npk` beside them). Each of those is a shell
script. It writes its files, and builds and runs both legs by PLAN.md's recipe
(`build`, `legs`) or checks a refusal (`refused`). It exits 0 exactly when the claim
holds.
"""
import os
from m11lib import *

covers("MODULE", 1)

D = "MODULE"
FS = failsafe_text("")


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


def root(body, decls=""):
    """A whole root file `r.npk` for a shell claim: header, decls, main, failsafe."""
    return "mod:r;\n" + (decls.strip() + "\n\n" if decls.strip() else "") + main_(body) + "\n" + FS


SH_LIB = r'''build() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 0 ] || return 3
    opt -O2 -S p.ll -o p2.ll || return 4
    llc -O0 -filetype=obj -relocation-model=static p.ll -o p0.o || return 4
    llc -O2 -filetype=obj -relocation-model=static p2.ll -o p2.o || return 4
    ld.lld -static p0.o "$NPKRT" -o p0 || return 4
    ld.lld -static p2.o "$NPKRT" -o p2 || return 4
}
legs() {
    env -i ./p0 < /dev/null; a=$?
    env -i ./p2 < /dev/null; b=$?
    echo "O0=$a O2=$b"
    [ $a -eq "$1" ] && [ $b -eq "$1" ]
}
refused() {
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
NB = 'cp "$(dirname "$NPKC")/../../lib/nbridge.npk" . || exit 5\n'


def files_sh(files):
    out = []
    for path, text in files.items():
        d = os.path.dirname(path)
        if d:
            out.append("mkdir -p %s" % d)
        out.append("cat > %s <<'EOF'\n%s\nEOF" % (path, text.rstrip()))
    return "\n".join(out) + "\n"


def sh_run(files, code=0):
    return SH_LIB + files_sh(files) + "build r.npk || exit $?\nlegs %d" % code


def sh_refuse(files, pat="", pre=""):
    return SH_LIB + pre + files_sh(files) + "refused r.npk '%s'" % pat


def sh_accept(files, pre="", post=""):
    return SH_LIB + pre + files_sh(files) + "accepted r.npk" + post


def ext_root(block, decls=""):
    """A root that imports the compiler's `nbridge.npk` (copied beside it by NB) and
    declares an `extern` block in HUNT2's form: `Bridge->` first, `Duration` last."""
    return ('mod:r;\nuse "./nbridge.npk".*;\n\n' + (decls.strip() + "\n\n" if decls.strip() else "")
            + block.strip() + "\n\n" + main_("    exit 0i32;") + "\n" + FS)


NETWORK = """mod:network = {
    pub func:connect = int32() { pass 0i32; };
    func:internal = int32() { pass 1i32; }; // Private
};"""

NETLIB = """mod:network;
pub func:connect = int32() never fails { pass 0i32; };
pub fixed int32:MAX = 42i32;
func:hidden = int32() never fails { pass 1i32; };"""

NETMOD = """mod:network = {
    pub struct:Point = { int32:x; int32:y; };
    pub fixed int32:MAX = 11i32;
    pub func:connect = int32() never fails { pass 3i32; };
    pub func:origin = Point() never fails { Point:p = Point{ x: 1i32, y: 2i32 }; pass p; };
};"""

LIB = """mod:lib;
pub func:f = int32() never fails { pass 5i32; };
pub fixed int32:K = 7i32;
func:private_here = int32() never fails { pass 0i32; };"""

MID_PUBMOD = """mod:mid;
pub mod:network;
pub func:anchor = int32() never fails { pass 0i32; };"""

CORE = """mod:core = {
    pub mod:math = {
        pub func:sq = int32(int32:v) never fails { pass (v * v); };
    };
};"""

NESTED = """mod:nested = {
    func:internal = int32() never fails { pass 1i32; };
    fixed int32:SECRET = 2i32;
    mod:deep = { pub func:g = int32() never fails { pass 3i32; }; };
    pub func:visible = int32() never fails { pass (raw internal()); };
};"""

BOOM = """mod:m = {
    error:Boom;
    pub func:boom = int32(int32:v) {
        if (v > 0i32) { fail Boom; }
        pass v;
    };
};"""

SQLIB = """mod:sqlib;
pub func:square = int32(int32:v) never fails { pass (v * v); };
pub fixed int32:pi = 3i32;
func:hidden = int32() never fails { pass 0i32; };"""

# ================================================================== 1.1 defining modules
claim("md0013", D, 13, "```nitpick", "example",
      "An inline module with a `pub` and a private function compiles, and its `pub` member is called "
      "qualified: `network.connect()` is 0.",
      expect="run:0",
      src=main_("""    int32:v = network.connect() ?| 9i32;
%s
    exit 0i32;""" % chk("v == 0i32", 10), NETWORK),
      wrong="refused, or connect's value not 0 (10)")
claim("md0016", D, 16, "// Private", "rule",
      "A member written without `pub` is private: `network.internal()` from outside the module is refused.",
      expect="refuse",
      src=main_("""    int32:v = network.internal() ?| 9i32;
    if (v == 9i32) { exit 10i32; }
    exit 0i32;""", NETWORK),
      wrong="accepted: the private member reached from outside")
claim("md0021", D, 21, "```nitpick", "example",
      "`mod:network;` after the header loads `network.npk` beside the file, and `network.connect()` "
      "calls into it.",
      expect="run:0",
      src=main_("""    int32:v = raw network.connect();
%s
    exit 0i32;""" % chk("v == 0i32", 10), "mod:network;"),
      files={"network.npk": NETLIB},
      wrong="refused (the file not loaded), or 10")
claim("md0024", D, 24, "or `network/mod.npk` relative to the declaring file", "rule",
      "With no `network.npk`, `mod:network;` loads `network/mod.npk` (whose header is `mod:network;`).",
      expect="sh:0",
      sh=sh_run({"network/mod.npk": NETLIB,
                 "r.npk": root("""    int32:v = raw network.connect();
    int32:m = network.MAX;
    if (v != 0i32) { exit 10i32; }
    if (m != 42i32) { exit 11i32; }
    exit 0i32;""", "mod:network;")}),
      wrong="the directory form not searched (refused), or 10/11")
claim("md0024b", D, 24, "relative to the declaring file", "rule",
      "A `mod:b;` written in `sub/a.npk` loads `sub/b.npk`, not the `b.npk` beside the root.",
      expect="sh:0",
      sh=sh_run({"sub/a.npk": """mod:a;
mod:b;
pub func:fa = int32() never fails { pass (raw b.g()); };""",
                 "sub/b.npk": "mod:b;\npub func:g = int32() never fails { pass 7i32; };",
                 "b.npk": "mod:b;\npub func:g = int32() never fails { pass 3i32; };",
                 "r.npk": root("""    int32:v = raw a.fa();
    if (v == 3i32) { exit 10i32; }
    if (v != 7i32) { exit 11i32; }
    exit 0i32;""", 'use "./sub/a.npk" as a;')}),
      wrong="the b.npk beside the root loaded (10), or refused")
claim("md0026", D, 26, "`network.MAX` reads its binding", "rule",
      "After `mod:network;`, `network.MAX` reads the file's `pub` binding (42).",
      expect="run:0",
      src=main_("""    int32:m = network.MAX;
%s
    exit 0i32;""" % chk("m == 42i32", 10), "mod:network;"),
      files={"network.npk": NETLIB},
      wrong="refused, or 10")
claim("md0027", D, 27, "`use network.*;`", "rule",
      "After `mod:network;`, `use network.*;` binds the file's `pub` names bare.",
      expect="run:0",
      src=main_("""    int32:v = raw connect();
    int32:m = MAX;
%s
%s
    exit 0i32;""" % (chk("v == 0i32", 10), chk("m == 42i32", 11)), "mod:network;\nuse network.*;"),
      files={"network.npk": NETLIB},
      wrong="refused: the wildcard binds nothing through the file's symbol")
claim("md0027b", D, 27, "`use network.{connect};`", "rule",
      "After `mod:network;`, `use network.{connect};` binds `connect` bare.",
      expect="run:0",
      src=main_("""    int32:v = raw connect();
%s
    exit 0i32;""" % chk("v == 0i32", 10), "mod:network;\nuse network.{connect};"),
      files={"network.npk": NETLIB},
      wrong="refused")
claim("md0028", D, 28, "a `pub mod:network;` is", "rule",
      "A `pub mod:network;` in `mid.npk` is re-exported with its scope by `use \"./mid.npk\".*;`: "
      "`network.connect()` and `network.MAX` work in the importer.",
      expect="run:0",
      src=main_("""    int32:v = raw network.connect();
    int32:m = network.MAX;
%s
%s
    exit 0i32;""" % (chk("v == 0i32", 10), chk("m == 42i32", 11)), 'use "./mid.npk".*;'),
      files={"mid.npk": MID_PUBMOD, "network.npk": NETLIB},
      wrong="refused: `network` not re-exported, or re-exported with an empty scope")
claim("md0030", D, 30, "one meaning with `use \"./network.npk\" as network;`", "rule",
      "`use \"./network.npk\" as network;` gives the same symbol: `network.connect()` and `network.MAX` "
      "work through it.",
      expect="run:0",
      src=main_("""    int32:v = raw network.connect();
    int32:m = network.MAX;
%s
%s
    exit 0i32;""" % (chk("v == 0i32", 10), chk("m == 42i32", 11)), 'use "./network.npk" as network;'),
      files={"network.npk": NETLIB},
      wrong="refused, or 10/11")
claim("md0030b", D, 30, "one `inner` field", "rule",
      "The alias, the file import and the re-export share one `inner` field and one lookup.",
      untestable="[internal] the symbol's field and lookup are the compiler's data structures; md0028 and "
                 "md0030 test what a program sees of them")
claim("md0031", D, 31, "The link is made when every module has been", "rule",
      "A re-export is linked after every module is collected: a name imported through a `pub mod:` that "
      "another file re-exports is bound, not empty.",
      expect="run:0",
      src=main_("""    int32:v = raw connect();
    int32:m = network.MAX;
%s
%s
    exit 0i32;""" % (chk("v == 0i32", 10), chk("m == 42i32", 11)),
                'use "./mid.npk".*;\nuse network.{connect};'),
      files={"mid.npk": MID_PUBMOD, "network.npk": NETLIB},
      wrong="refused: the re-exported scope copied while empty (`connect` not a member)")
claim("md0034", D, 34, "a `use` in any of its forms", "rule",
      "A `use \"./lib.npk\".*;` written inside an inline module binds into that module's scope.",
      expect="run:0",
      src=main_("""    int32:v = raw m.g();
%s
    exit 0i32;""" % chk("v == 5i32", 10), """mod:m = {
    use "./lib.npk".*;
    pub func:g = int32() never fails { pass (raw f()); };
};"""),
      files={"lib.npk": LIB},
      wrong="refused: the import a silent no-op inside the module (`f` unbound)")
claim("md0034b", D, 34, "a `pub use`", "rule",
      "A `pub use` inside an inline module re-exports through it: `m.f()` reaches the imported function.",
      expect="run:0",
      src=main_("""    int32:v = raw m.f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), """mod:m = {
    pub use "./lib.npk".f;
    pub func:anchor = int32() never fails { pass 0i32; };
};"""),
      files={"lib.npk": LIB},
      wrong="refused: `m` has no member `f`")
claim("md0035", D, 35, "and a `mod:name;` written inside `mod:m = { … }` bind into `m`'s scope", "rule",
      "A `mod:lib;` written inside an inline module loads `lib.npk` beside the FILE and binds `lib` in the "
      "module's scope.",
      expect="run:0",
      src=main_("""    int32:v = raw m.g();
%s
    exit 0i32;""" % chk("v == 5i32", 10), """mod:m = {
    mod:lib;
    pub func:g = int32() never fails { pass (raw lib.f()); };
};"""),
      files={"lib.npk": LIB},
      wrong="refused")
claim("md0036", D, 36, "under the same rounds and refusals as at", "rule",
      "An import inside an inline module is refused as at file level: a `use` of a file that does not "
      "exist is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw m.g();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", """mod:m = {
    use "./nosuch.npk".*;
    pub func:g = int32() never fails { pass 1i32; };
};"""),
      wrong="accepted: the import a silent no-op")
claim("md0037", D, 37, "and `use m.*;` binds what `m` re-exports", "rule",
      "`use m.*;` binds what the inline module `m` re-exports with `pub use`.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), """mod:m = {
    pub use "./lib.npk".f;
    pub func:anchor = int32() never fails { pass 0i32; };
};
use m.*;"""),
      files={"lib.npk": LIB},
      wrong="refused: the re-export not bound by the wildcard")
claim("md0038", D, 38, "sealed from its file's imports", "rule",
      "An inline module is sealed from its file's imports: a name the file imports is not visible "
      "inside the module.",
      expect="refuse",
      src=main_("""    int32:v = raw m.g();
    int32:w = raw f();
    if (v != w) { exit 10i32; }
    exit 0i32;""", """use "./lib.npk".*;
mod:m = {
    pub func:g = int32() never fails { pass (raw f()); };
};"""),
      files={"lib.npk": LIB},
      wrong="accepted: the file's import leaks into the module")

# ------------------------------------------------------------------ the header
claim("md0042", D, 42, "`mod:<dir>;` for a `dir/mod.npk`", "rule",
      "A `dir/mod.npk`'s header is `mod:<dir>;`: a `network/mod.npk` whose header is `mod:mod;` names "
      "another module and is refused, NITPICK-RESOLVE-012.",
      expect="sh:0",
      sh=sh_refuse({"network/mod.npk": NETLIB.replace("mod:network;", "mod:mod;", 1),
                    "r.npk": root("""    int32:v = raw network.connect();
    if (v != 0i32) { exit 10i32; }
    exit 0i32;""", "mod:network;")}, "NITPICK-RESOLVE-012"),
      wrong="accepted: a `mod.npk` named `mod`")
claim("md0043", D, 43, "The header binds", "rule",
      "The header binds nothing: the file's own module name is not a symbol, so `md0043.f()` is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw md0043.f();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", "func:f = int32() never fails { pass 1i32; };"),
      wrong="accepted: the header bound the file's own name")
claim("md0044", D, 44, "A file whose first", "rule",
      "A file whose first declaration is not its header is refused at that declaration, "
      "NITPICK-RESOLVE-012.",
      expect="sh:0",
      sh=sh_refuse({"r.npk": "func:helper = int32() never fails { pass 1i32; };\n\n"
                             + main_("""    int32:v = raw helper();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""") + "\n" + FS}, "NITPICK-RESOLVE-012"),
      wrong="accepted: a file with no header")
claim("md0045", D, 45, "or a `mod:` naming another module, is refused", "rule",
      "A file whose header names another module (a sibling that exists) is refused, NITPICK-RESOLVE-012.",
      expect="sh:0",
      sh=sh_refuse({"sib.npk": "mod:sib;\npub func:s = int32() never fails { pass 2i32; };",
                    "lib.npk": "mod:sib;\npub func:f = int32() never fails { pass 5i32; };",
                    "r.npk": root("""    int32:v = raw f();
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", 'use "./lib.npk".*;')}, "NITPICK-RESOLVE-012"),
      wrong="accepted: the header loads the sibling, or is ignored")
claim("md0046", D, 46, "a file with no declarations at", "rule",
      "A file with no declarations at all is refused at its first line, NITPICK-RESOLVE-012.",
      expect="sh:0",
      sh=sh_refuse({"empty.npk": "// nothing is declared here",
                    "r.npk": root("    exit 0i32;", 'use "./empty.npk".*;')}, "NITPICK-RESOLVE-012"),
      wrong="accepted: an empty module imported")

# ------------------------------------------------------------------ the entry points
ELIB_MAIN = """mod:elib;
pub func:helper = int32() never fails { pass 1i32; };
func:main = int32(cstring[]:_~argv) { exit 0i32; };"""
claim("md0055", D, 55, "Declared in any other module of the program", "rule",
      "`main` declared in an imported module is refused, NITPICK-RESOLVE-013.",
      expect="refuse:NITPICK-RESOLVE-013",
      src=main_("""    int32:v = raw helper();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", 'use "./elib.npk".*;'),
      files={"elib.npk": ELIB_MAIN},
      wrong="accepted (two mains), or refused only by llc")
claim("md0055b", D, 55, "or inside an inline module", "rule",
      "`main` declared inside an inline module of the root is refused, NITPICK-RESOLVE-013.",
      expect="refuse:NITPICK-RESOLVE-013",
      src=main_("""    exit 0i32;""", """mod:inner = {
    func:main = int32(cstring[]:_~argv) { exit 0i32; };
    pub func:anchor = int32() never fails { pass 0i32; };
};"""),
      wrong="accepted")
claim("md0056", D, 56, "either is refused (`NITPICK-RESOLVE-013`)", "rule",
      "`failsafe` declared in an imported module is refused, NITPICK-RESOLVE-013.",
      expect="refuse:NITPICK-RESOLVE-013",
      src=main_("""    int32:v = raw helper();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", 'use "./elib.npk".*;'),
      files={"elib.npk": "mod:elib;\npub func:helper = int32() never fails { pass 1i32; };\n" + FS},
      wrong="accepted: a library's failsafe smuggled into the program")
claim("md0056b", D, 56, "the runtime calls both by name", "rule",
      "`failsafe` declared inside an inline module of the root is refused, NITPICK-RESOLVE-013.",
      expect="refuse:NITPICK-RESOLVE-013",
      src=main_("""    exit 0i32;""", "mod:inner = {\n" + FS + "    pub func:anchor = int32() never fails { pass 0i32; };\n};"),
      wrong="accepted")

# ------------------------------------------------------------------ nesting and visibility
claim("md0060", D, 60, "Modules can be arbitrarily nested", "rule",
      "Modules nest: `mod:core = { mod:math = { … }; };` compiles, and `math` is reached inside `core`.",
      expect="run:0",
      src=main_("""    int32:v = raw core.sq9();
%s
    exit 0i32;""" % chk("v == 9i32", 10), """mod:core = {
    mod:math = {
        pub func:sq = int32(int32:v) never fails { pass (v * v); };
    };
    pub func:sq9 = int32() never fails { pass (raw math.sq(3i32)); };
};"""),
      wrong="refused, or 10")
claim("md0061", D, 61, "Modules are private by default", "rule",
      "A nested module without `pub` is private: `core.math.sq(3i32)` from outside `core` is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw core.math.sq(raw v32(3i32));
    if (v != 9i32) { exit 10i32; }
    exit 0i32;""", CORE.replace("pub mod:math", "mod:math")),
      wrong="accepted: the private module reached from outside")
claim("md0061b", D, 61, "Use `pub mod` to expose them to outer scopes", "rule",
      "`pub mod` exposes a nested module: `core.math.sq(3i32)` from outside is 9.",
      expect="run:0",
      src=main_("""    int32:v = raw core.math.sq(raw v32(3i32));
%s
    exit 0i32;""" % chk("v == 9i32", 10), CORE),
      wrong="refused, or 10")
claim("md0063", D, 63, "An inline module's members are reached QUALIFIED", "rule",
      "An inline module's member is not in scope bare outside it: `connect()` without a qualifier or an "
      "import is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw connect();
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", NETMOD),
      wrong="accepted: the member leaks into the file's scope")
claim("md0064", D, 64, "the contract, purity, async", "rule",
      "A qualified call checks the member's `requires` as any named call does: a violated precondition "
      "traps RequiresViolated.",
      expect="trap:RequiresViolated",
      src=main_("""    int32:r = m.half(raw v32(-4i32)) ?| 7i32;
    if (r == 7i32) { exit 10i32; }
    exit 11i32;""", """mod:m = {
    pub func:half = int32(int32:n) requires n > 0i32 { pass (n / 2i32); };
};"""),
      wrong="no trap: the contract skipped on the qualified call (10 or 11)")
claim("md0065", D, 65, "and argument rules of any named call", "rule",
      "A qualified call checks its arguments as any named call does: an `int64` passed for an `int32` "
      "parameter is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw m.id(raw v64(3i64));
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", """mod:m = {
    pub func:id = int32(int32:x) never fails { pass x; };
};"""),
      wrong="accepted: the argument converted, or not checked")
claim("md0065b", D, 65, "`network.MAX` reads its binding", "rule",
      "`network.MAX` reads an inline module's `pub` binding (11).",
      expect="run:0",
      src=main_("""    int32:m = network.MAX;
%s
    exit 0i32;""" % chk("m == 11i32", 10), NETMOD),
      wrong="refused, or 10")
claim("md0066", D, 66, "`network.E` names its error constant", "rule",
      "`m.Boom` names the inline module's error constant: `?! m.Boom` raises it, and failsafe's "
      "`(md0066.Boom)` arm sees it (signalled with 42, S45).",
      expect="run:42", fs=False,
      src=main_("""    int32:v = m.boom(raw v32(5i32)) ?! m.Boom;
    if (v == 5i32) { exit 10i32; }
    exit 11i32;""", BOOM) + "\n" + failsafe_with("        (md0066.Boom) { exit 42i32; },"),
      wrong="refused (`m.Boom` not a name), 99 (another identity), or 10/11 (no failure)")
claim("md0067", D, 67, "(`core.math.sq(3i32)`)", "rule",
      "A member is reached qualified through any depth of nesting: `a.b.c.f()`, three modules down.",
      expect="run:0",
      src=main_("""    int32:v = raw a.b.c.f(raw v32(4i32));
%s
    exit 0i32;""" % chk("v == 16i32", 10), """mod:a = {
    pub mod:b = {
        pub mod:c = {
            pub func:f = int32(int32:v) never fails { pass (v * v); };
        };
    };
};"""),
      wrong="refused past the second level, or 10")
claim("md0067b", D, 67, "and IMPORTED with `use network.*;`", "rule",
      "`use network.*;` over an inline module binds its `pub` members bare.",
      expect="run:0",
      src=main_("""    int32:v = raw connect();
    int32:m = MAX;
%s
%s
    exit 0i32;""" % (chk("v == 3i32", 10), chk("m == 11i32", 11)), NETMOD + "\nuse network.*;"),
      wrong="refused")
claim("md0068", D, 68, "network.{connect, Point};`", "rule",
      "`use network.{connect, Point};` binds the function and the TYPE: `Point` is named bare outside the "
      "module.",
      expect="run:0",
      src=main_("""    Point:p = Point{ x: 4i32, y: 5i32 };
    int32:v = raw connect();
%s
    exit 0i32;""" % chk("p.x + p.y + v == 12i32", 10), NETMOD + "\nuse network.{connect, Point};"),
      wrong="refused: the type not importable")
claim("md0068b", D, 68, "`use network.connect;`", "rule",
      "`use network.connect;` binds the one member bare.",
      expect="run:0",
      src=main_("""    int32:v = raw connect();
%s
    exit 0i32;""" % chk("v == 3i32", 10), NETMOD + "\nuse network.connect;"),
      wrong="refused")
claim("md0068c", D, 68, "`use core.math as", "rule",
      "`use core.math as cm;` aliases a nested inline module: `cm.sq(3i32)` is 9.",
      expect="run:0",
      src=main_("""    int32:v = raw cm.sq(raw v32(3i32));
%s
    exit 0i32;""" % chk("v == 9i32", 10), CORE + "\nuse core.math as cm;"),
      wrong="refused")
claim("md0069", D, 69, "which is the only way an inline module's TYPES are named from", "rule",
      "An inline module's type is named from outside only by importing it: `network.Point:p` (qualified "
      "type) is refused.",
      expect="refuse",
      src=main_("""    network.Point:p = raw network.origin();
    if (p.x != 1i32) { exit 10i32; }
    exit 0i32;""", NETMOD),
      wrong="accepted: a type reached through the module path")
claim("md0070", D, 70, "An alias (`use \"./m.npk\" as m;`)", "rule",
      "An alias carries its file's scope: after `use \"./m.npk\" as m;`, `m.f()` works across files.",
      expect="run:0",
      src=main_("""    int32:v = raw m.f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use "./m.npk" as m;'),
      files={"m.npk": LIB.replace("mod:lib;", "mod:m;", 1)},
      wrong="refused")
claim("md0071", D, 71, "import carry their module's scope the same way", "rule",
      "A `pub mod:helpers = { … };` bound by a file import carries its scope: `helpers.f()` works in the "
      "importer.",
      expect="run:0",
      src=main_("""    int32:v = raw helpers.f();
%s
    exit 0i32;""" % chk("v == 6i32", 10), 'use "./hlib.npk".*;'),
      files={"hlib.npk": """mod:hlib;
pub mod:helpers = {
    pub func:f = int32() never fails { pass 6i32; };
    func:kept_here = int32() never fails { pass 0i32; };
};"""},
      wrong="refused")
claim("md0072", D, 72, "A module in value position is refused", "rule",
      "A module in value position is refused with \"`m` is a module, not a value\".",
      expect="sh:0",
      sh=sh_refuse({"r.npk": root("""    int32:x = network;
    if (x != 0i32) { exit 10i32; }
    exit 0i32;""", NETMOD)}, "is a module, not a value"),
      wrong="accepted, or refused with another message")
claim("md0073", D, 73, "as is a type reached through one", "rule",
      "A type reached through a module, in value position, is refused (`int32:v = network.Point;`).",
      expect="refuse",
      src=main_("""    int32:v = network.Point;
    if (v != 0i32) { exit 10i32; }
    exit 0i32;""", NETMOD),
      wrong="accepted")
claim("md0074", D, 74, "member the module lacks is \"module `m` has no member `x`\"", "rule",
      "A member the module lacks is refused with \"module `m` has no member `x`\".",
      expect="sh:0",
      sh=sh_refuse({"r.npk": root("""    int32:v = raw network.nosuch();
    if (v != 0i32) { exit 10i32; }
    exit 0i32;""", NETMOD)}, "has no member"),
      wrong="accepted, or refused with another message")

# ------------------------------------------------------------------ error constants in inline modules
claim("md0077", D, 77, "the basename of the declaring file, however deep the", "rule",
      "An error constant two inline modules deep is the FILE's identity: failsafe's `(md0077.Boom)` arm "
      "catches `a.b.Boom` (signalled with 42, S45).",
      expect="run:42", fs=False,
      src=main_("""    int32:v = a.b.boom(raw v32(5i32)) ?! a.b.Boom;
    if (v == 5i32) { exit 10i32; }
    exit 11i32;""", """mod:a = {
    pub mod:b = {
        error:Boom;
        pub func:boom = int32(int32:v) {
            if (v > 0i32) { fail Boom; }
            pass v;
        };
    };
};""") + "\n" + failsafe_with("        (md0077.Boom) { exit 42i32; },"),
      wrong="99: the code hashed from the module path, so the file's arm misses")
claim("md0079", D, 79, "`use m.{Name};` then `(Name)` is the bare spelling", "rule",
      "After `use m.{Boom};`, the bare arm `(Boom)` catches the inline module's constant (signalled with "
      "42, S45).",
      expect="run:42", fs=False,
      src=main_("""    int32:v = m.boom(raw v32(5i32)) ?! m.Boom;
    if (v == 5i32) { exit 10i32; }
    exit 11i32;""", BOOM + "\nuse m.{Boom};") + "\n" + failsafe_with("        (Boom) { exit 42i32; },"),
      wrong="refused (the bare arm not bound), or 99")
CLASSIFY = """func:classify = int32(int32:v) never fails {
    Result<int32>:r = m.boom(v);
    if (r.is_error) {
        pick (r.err) {
            (%s) { pass 10i32; },
            (*) { pass 30i32; }
        }
    }
    pass 0i32;
};"""
claim("md0080", D, 80, "SELECTOR IS CHECKED, in `failsafe` and in any other `pick`", "rule",
      "An arm over an `Error` in an ordinary `pick` is checked: `(nosuch.Boom)`, which no loaded file's "
      "constant hashes to, is refused, NITPICK-RESOLVE-002.",
      expect="refuse:NITPICK-RESOLVE-002",
      src=main_("""    int32:c = raw classify(raw v32(5i32));
    if (c != 10i32) { exit 10i32; }
    exit 0i32;""", BOOM + "\n" + CLASSIFY % "nosuch.Boom"),
      wrong="accepted: the arm matches nothing, silently (exit 10)")
claim("md0080b", D, 80, "`Error` SELECTOR IS CHECKED", "rule",
      "In an ordinary `pick` over an `Error`, the file-qualified arm `(md0080b.Boom)` catches the inline "
      "module's constant.",
      expect="run:0",
      src=main_("""    int32:c = raw classify(raw v32(5i32));
    int32:d = raw classify(raw v32(-1i32));
%s
%s
    exit 0i32;""" % (chk("c == 10i32", 10), chk("d == 0i32", 11)), BOOM + "\n" + CLASSIFY % "md0080b.Boom"),
      wrong="refused, or 10 (the arm missed)")


def bad_arm(cid, line, quote, arm, text, code, wrong, decls=BOOM):
    claim(cid, D, line, quote, "rule", text,
          expect="refuse:%s" % code, fs=False,
          src=main_("""    exit 0i32;""", decls) + "\n" + failsafe_with("        (%s) { exit 42i32; }," % arm),
          wrong=wrong)


bad_arm("md0083", 83, "`(m.Name)` with an inline module `m`", "m.Boom",
        "A failsafe arm `(m.Boom)` qualified by the inline module, not the file, is refused, "
        "NITPICK-RESOLVE-002.", "NITPICK-RESOLVE-002",
        "accepted: the arm hashes to a code no constant has and matches nothing")
bad_arm("md0083b", 83, "`(file.Nosuch)`", "md0083b.Nosuch",
        "A failsafe arm `(file.Nosuch)` naming no constant of the file is refused, NITPICK-RESOLVE-002.",
        "NITPICK-RESOLVE-002", "accepted")
bad_arm("md0083c", 83, "`(nosuch.Name)`", "nosuch.Boom",
        "A failsafe arm `(nosuch.Boom)` naming no loaded file is refused, NITPICK-RESOLVE-002.",
        "NITPICK-RESOLVE-002", "accepted")
bad_arm("md0084", 84, "`(x.DivByZero)` (a system constant's code is explicit, never a hash)", "x.DivByZero",
        "A failsafe arm `(x.DivByZero)` (a system constant under a qualifier) is refused, "
        "NITPICK-RESOLVE-002.", "NITPICK-RESOLVE-002", "accepted")
bad_arm("md0087", 87, "literal, a global, a range", "5i32",
        "A literal arm over an `Error` selector is refused, NITPICK-TYPE-007.", "NITPICK-TYPE-007",
        "accepted, or refused with another code")
bad_arm("md0087b", 87, "a global", "G",
        "An arm naming a global (not an error constant) over an `Error` selector is refused, "
        "NITPICK-TYPE-007.", "NITPICK-TYPE-007", "accepted, or refused with another code",
        decls=BOOM + "\nfixed int32:G = 1i32;")
bad_arm("md0087c", 87, "a range", "1i32..3i32",
        "A range arm over an `Error` selector is refused, NITPICK-TYPE-007.", "NITPICK-TYPE-007",
        "accepted, or refused with another code")
bad_arm("md0088", 88, "three-plus segments", "a.b.Boom",
        "A three-segment arm `(a.b.Boom)` over an `Error` selector is refused, NITPICK-TYPE-007.",
        "NITPICK-TYPE-007", "accepted, or refused with another code",
        decls="""mod:a = {
    pub mod:b = {
        error:Boom;
        pub func:boom = int32(int32:v) {
            if (v > 0i32) { fail Boom; }
            pass v;
        };
    };
};""")

# ================================================================== 2.1 file-based imports
claim("md0099", D, 99, "**Wildcard** (All `pub` symbols)", "rule",
      "`use \"./sqlib.npk\".*;` binds every `pub` symbol of the file bare.",
      expect="run:0",
      src=main_("""    int32:v = raw square(raw v32(3i32));
%s
%s
    exit 0i32;""" % (chk("v == 9i32", 10), chk("pi == 3i32", 11)), 'use "./sqlib.npk".*;'),
      files={"sqlib.npk": SQLIB},
      wrong="refused")
claim("md0099b", D, 99, "`use \"path/module.npk\".*;`", "rule",
      "The wildcard binds only `pub` symbols: the file's private `hidden()` is not bound by it.",
      expect="refuse",
      src=main_("""    int32:v = raw hidden();
    if (v != 0i32) { exit 10i32; }
    exit 0i32;""", 'use "./sqlib.npk".*;'),
      files={"sqlib.npk": SQLIB},
      wrong="accepted: a private symbol imported by the wildcard")
claim("md0100", D, 100, "`use \"path/module.npk\".square;`", "rule",
      "`use \"./sqlib.npk\".square;` binds the one name.",
      expect="run:0",
      src=main_("""    int32:v = raw square(raw v32(4i32));
%s
    exit 0i32;""" % chk("v == 16i32", 10), 'use "./sqlib.npk".square;'),
      files={"sqlib.npk": SQLIB},
      wrong="refused")
claim("md0101", D, 101, "`use \"path/module.npk\".{square, pi};`", "rule",
      "`use \"./sqlib.npk\".{square, pi};` binds the two names.",
      expect="run:0",
      src=main_("""    int32:v = raw square(raw v32(2i32));
%s
    exit 0i32;""" % chk("v + pi == 7i32", 10), 'use "./sqlib.npk".{square, pi};'),
      files={"sqlib.npk": SQLIB},
      wrong="refused")
claim("md0102", D, 102, "`use \"path/module.npk\" as math;`", "rule",
      "`use \"./sqlib.npk\" as math;` binds the namespace: `math.square(3i32)` and `math.pi`.",
      expect="run:0",
      src=main_("""    int32:v = raw math.square(raw v32(3i32));
%s
    exit 0i32;""" % chk("v + math.pi == 12i32", 10), 'use "./sqlib.npk" as math;'),
      files={"sqlib.npk": SQLIB},
      wrong="refused")

# ================================================================== 2.2 logical path imports
claim("md0105", D, 105, "```nitpick", "example",
      "The block's six logical-path imports compile together (with `nested`, `core.math` and a file import "
      "binding `helpers` declared), and each bound name works.",
      expect="run:0",
      src=main_("""    int32:a = raw fetch(raw v32(3i32));
    int32:b = raw sq(raw v32(3i32));
    int32:c = raw cm.sq(raw v32(2i32));
    int32:d = raw f();
%s
%s
%s
%s
    exit 0i32;""" % (chk("a == 7i32", 10), chk("b == 9i32", 11), chk("c == 4i32", 12), chk("d == 6i32", 13)),
                """use std.math.*;
use std.collections.{HashMap, HashSet};
use nested.*;                 // an inline module of this file
use core.math.{sq};           // a nested path
use core.math as cm;          // an alias over one
use helpers.f;                // a `pub mod` a file import bound
use "./hlib.npk".*;

mod:nested = {
    pub func:fetch = int32(int32:v) never fails { pass (v + 4i32); };
};
""" + CORE),
      files={"hlib.npk": """mod:hlib;
pub mod:helpers = {
    pub func:f = int32() never fails { pass 6i32; };
};"""},
      wrong="refused (a form not resolved, or `std` unknown), or 10-13")
claim("md0115", D, 115, "`std` is the standard library's, resolved by the driver", "rule",
      "A logical path whose first segment is `std` is resolved by the driver against the standard library.",
      untestable="[vague] the reference names no standard-library member whose signature a program could "
                 "call, so what `use std.…` binds is not observable; md0105 and md0148 check that the "
                 "forms compile")
claim("md0116", D, 116, "other first segment must name a MODULE SYMBOL", "rule",
      "A logical path may start at a `use \"…\" as name;` alias: `use lib.{f};` after the alias binds `f`.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use "./lib.npk" as lib;\nuse lib.{f};'),
      files={"lib.npk": LIB},
      wrong="refused: the alias is not a module symbol to a logical path")
claim("md0119", D, 119, "last module's public names are then bound through the same binders", "rule",
      "Every form of the file imports works through a logical path: `use core.math.sq;` (one name) "
      "binds `sq`.",
      expect="run:0",
      src=main_("""    int32:v = raw sq(raw v32(5i32));
%s
    exit 0i32;""" % chk("v == 25i32", 10), CORE + "\nuse core.math.sq;"),
      wrong="refused")
claim("md0120", D, 120, "forms use, in every form the file forms have", "rule",
      "Every form of the file imports works through a logical path: `use core.math.*;` binds `sq`.",
      expect="run:0",
      src=main_("""    int32:v = raw sq(raw v32(6i32));
%s
    exit 0i32;""" % chk("v == 36i32", 10), CORE + "\nuse core.math.*;"),
      wrong="refused")
claim("md0121", D, 121, "symbol in scope is refused by name (`NITPICK-RESOLVE-002`", "rule",
      "A logical path whose first segment names no module symbol in scope is refused, NITPICK-RESOLVE-002.",
      expect="refuse:NITPICK-RESOLVE-002",
      src=main_("""    exit 0i32;""", "use nosuch.*;"),
      wrong="accepted: the typo silent")
claim("md0122", D, 122, "one naming a function or a binding \"is not a module\"", "rule",
      "A logical path whose first segment names a function is refused (\"is not a module\").",
      expect="sh:0",
      sh=sh_refuse({"r.npk": root("""    int32:v = raw helper();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", "func:helper = int32() never fails { pass 1i32; };\nuse helper.*;")}, "is not a module"),
      wrong="accepted, or refused with another message")
claim("md0123", D, 123, "the module lacks is `NITPICK-RESOLVE-007`", "rule",
      "A later segment the module lacks is refused, NITPICK-RESOLVE-007.",
      expect="refuse:NITPICK-RESOLVE-007",
      src=main_("""    exit 0i32;""", CORE + "\nuse core.nosuch.*;"),
      wrong="accepted, or refused with another code")
claim("md0124", D, 124, "`NITPICK-RESOLVE-003`, exactly as for a named file import", "rule",
      "A later segment naming a private nested module is refused, NITPICK-RESOLVE-003.",
      expect="refuse:NITPICK-RESOLVE-003",
      src=main_("""    int32:v = raw sq(raw v32(3i32));
    if (v != 9i32) { exit 10i32; }
    exit 0i32;""", CORE.replace("pub mod:math", "mod:math") + "\nuse core.math.*;"),
      wrong="accepted: the private module's names imported")
claim("md0125", D, 125, "so `use lib.*;` may stand", "rule",
      "Order never matters: `use lib.*;` written ABOVE the `use \"./lib.npk\" as lib;` that binds `lib` "
      "works.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use lib.*;\nuse "./lib.npk" as lib;'),
      files={"lib.npk": LIB},
      wrong="refused: `lib` not yet bound (RESOLVE-002)")
claim("md0127", D, 127, "no program declares as a module (`NITPICK-RESOLVE-001`", "rule",
      "No program declares a module named `std`: `mod:std = { … };` is refused, NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    exit 0i32;""", """mod:std = {
    pub func:f = int32() never fails { pass 1i32; };
};"""),
      wrong="accepted")
claim("md0129", D, 129, "same code refuses a module-level FUNCTION", "rule",
      "A module-level function named after a bare-name builtin (`mono_now`) is refused, NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    int64:t = raw mono_now();
    if (t != 7i64) { exit 10i32; }
    exit 0i32;""", "func:mono_now = int64() never fails { pass 7i64; };"),
      wrong="accepted: the program's function takes over the builtin (exit 0)")
claim("md0129b", D, 129, "or an `extern` method, whose stub", "rule",
      "An `extern` method named after a bare-name builtin is refused, NITPICK-RESOLVE-001.",
      expect="sh:0",
      sh=sh_refuse({"r.npk": ext_root("""extern:"mockif" = {
    func:mono_now = int64(Bridge->:b, Duration:within);
};""")}, "NITPICK-RESOLVE-001", pre=NB),
      wrong="accepted: the stub takes over the builtin")
claim("md0133", D, 133, "Methods are exempt", "rule",
      "A method named after a bare-name builtin is accepted: `b.mono_now()` is the method.",
      expect="run:0",
      src=main_("""    Box:b = Box{ n: 7i64 };
%s
    exit 0i32;""" % chk("(raw b.mono_now()) == 7i64", 10), """struct:Box = { int64:n; };
impl:Box = {
    func:mono_now = int64(Self:self) never fails { pass self.n; };
};"""),
      wrong="refused RESOLVE-001")
claim("md0134", D, 134, "refuses a CALLABLE binding of that name", "rule",
      "Inside a function, a parameter of function type named after a builtin is refused, NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    int64:t = raw call_it(seven);
    if (t != 7i64) { exit 10i32; }
    exit 0i32;""", """func:seven = int64() never fails { pass 7i64; };
func:call_it = int64(func int64() never fails:mono_now) never fails { pass (raw mono_now()); };"""),
      wrong="accepted")
claim("md0134b", D, 134, "a parameter, a local", "rule",
      "Inside a function, a local of function type named after a builtin is refused, NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    func int64() never fails:mono_now = seven;
    int64:t = raw mono_now();
    if (t != 7i64) { exit 10i32; }
    exit 0i32;""", "func:seven = int64() never fails { pass 7i64; };"),
      wrong="accepted")
claim("md0134c", D, 134, "CALLABLE binding", "rule",
      "Only a CALLABLE binding is refused: a plain `int64` local named after a builtin is accepted.",
      expect="run:0",
      src=main_("""    int64:mono_now = raw v64(5i64);
%s
    exit 0i32;""" % chk("mono_now == 5i64", 10)),
      wrong="refused RESOLVE-001")

# ================================================================== 2.3 transitivity
TLIB_MID = """mod:mid;
%s
pub func:anchor = int32() never fails { pass 0i32; };"""
claim("md0139", D, 139, "strictly **not transitive**", "rule",
      "A plain `use` is not re-exported: a name `mid.npk` imports plain is not bound by `use \"./mid.npk\".*;`.",
      expect="refuse",
      src=main_("""    int32:v = raw f();
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", 'use "./mid.npk".*;'),
      files={"mid.npk": TLIB_MID % 'use "./lib.npk".*;', "lib.npk": LIB},
      wrong="accepted: the import transitive")
claim("md0139b", D, 139, "use `pub use` to expose them", "rule",
      "A `pub use` re-exports: a name `mid.npk` imports with `pub use` is bound by `use \"./mid.npk\".*;`.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use "./mid.npk".*;'),
      files={"mid.npk": TLIB_MID % 'pub use "./lib.npk".f;', "lib.npk": LIB},
      wrong="refused")
claim("md0139c", D, 139, "re-exports it all the same", "rule",
      "A `pub use` of a path the module already imported plain (plain first) still re-exports it.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use "./mid.npk".*;'),
      files={"mid.npk": TLIB_MID % 'use "./lib.npk".*;\npub use "./lib.npk".f;', "lib.npk": LIB},
      wrong="refused: the `pub use` downgraded to the plain `use`")
claim("md0139d", D, 139, "the two lines mean the same in either order", "rule",
      "The `pub use` re-exports in either order: `pub use` first, then the plain `use`.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 5i32", 10), 'use "./mid.npk".*;'),
      files={"mid.npk": TLIB_MID % 'pub use "./lib.npk".f;\nuse "./lib.npk".*;', "lib.npk": LIB},
      wrong="refused")

# ------------------------------------------------------------------ search paths
claim("md0146", D, 146, "| `use \"./util.npk\"`, `use \"../x/y.npk\"` | the **importing file's** directory |", "row",
      "A `../` path resolves against the IMPORTING file's directory: `sub/a.npk`'s `use \"../x/y.npk\"` "
      "loads `x/y.npk` beside the root.",
      expect="sh:0",
      sh=sh_run({"x/y.npk": "mod:y;\npub func:fy = int32() never fails { pass 8i32; };",
                 "sub/a.npk": """mod:a;
use "../x/y.npk".*;
pub func:fa = int32() never fails { pass (raw fy()); };""",
                 "r.npk": root("""    int32:v = raw fa();
    if (v != 8i32) { exit 10i32; }
    exit 0i32;""", 'use "./sub/a.npk".*;')}),
      wrong="refused: resolved against the root's or the working directory")
claim("md0147", D, 147, "| `use \"nfs/path.npk\"` | the **dependency roots** |", "row",
      "A path not starting with `.` resolves against the dependency roots only: with no dependency, "
      "`use \"nfs/path.npk\"` is refused even with `nfs/path.npk` beside the importing file.",
      expect="sh:0",
      sh=sh_refuse({"nfs/path.npk": "mod:path;\npub func:fp = int32() never fails { pass 4i32; };",
                    "r.npk": root("""    int32:v = raw fp();
    if (v != 4i32) { exit 10i32; }
    exit 0i32;""", 'use "nfs/path.npk".*;')}),
      wrong="accepted: the bare path resolved against the importing file's directory")
claim("md0148", D, 148, "| `use std.math.*` | the standard library |", "row",
      "`use std.math.*;` is a path the standard library resolves: the program compiles.",
      expect="compile",
      src=main_("""    exit 0i32;""", "use std.math.*;"),
      wrong="refused",
      note="the reference names no std member to call (md0115); a compile is all a program can check")
claim("md0150", D, 150, "A dependency named `nfs` declared at `../nfs` roots at", "rule",
      "A dependency named `nfs` declared at `../nfs` roots at `../nfs/src/`.",
      untestable="[tool] needs a package whose manifest declares a dependency (BUILD_REFERENCE §3); "
                 "BUILD's claims test the manifest")
claim("md0153", D, 153, "An ambiguous path is an error, not a first match.", "rule",
      "Two dependencies supplying the same path fail the build, naming both.",
      untestable="[tool] needs a package whose manifest declares two dependencies (BUILD_REFERENCE §3)")

# ================================================================== 2.4 cycles
CYC_A = """mod:a;
use "./b.npk".*;
pub struct:A = { int32:x; };
pub func:fa = int32() never fails { pass (raw fb()) + 1i32; };"""
CYC_B = """mod:b;
use "./a.npk".*;
pub func:fb = int32() never fails { A:v = A{ x: 2i32 }; pass v.x; };"""
claim("md0160", D, 160, "**A `use` cycle among modules is legal** (D-086)", "rule",
      "Two modules may import each other: `a.npk` and `b.npk`, each using the other's names, compile "
      "and run.",
      expect="run:0",
      src=main_("""    int32:v = raw fa();
%s
    exit 0i32;""" % chk("v == 3i32", 10), 'use "./a.npk".*;'),
      files={"a.npk": CYC_A, "b.npk": CYC_B},
      wrong="refused: a circular import")
claim("md0161", D, 161, "and so may any longer ring", "rule",
      "A longer ring of imports is legal: a → b → c → a.",
      expect="run:0",
      src=main_("""    int32:v = raw fa();
%s
    exit 0i32;""" % chk("v == 6i32", 10), 'use "./a.npk".*;'),
      files={"a.npk": """mod:a;
use "./b.npk".*;
pub func:fa = int32() never fails { pass (raw fb()) + 1i32; };
pub func:base = int32() never fails { pass 3i32; };""",
             "b.npk": """mod:b;
use "./c.npk".*;
pub func:fb = int32() never fails { pass (raw fc()) + 1i32; };""",
             "c.npk": """mod:c;
use "./a.npk".*;
pub func:fc = int32() never fails { pass (raw base()) + 1i32; };"""},
      wrong="refused: a circular import")
claim("md0166", D, 166, "Nitpick has no module-level execution", "rule",
      "There is no module-level execution: a statement at module level is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", """func:note = NIL() never fails { pass NIL; };
drop note();"""),
      wrong="accepted: the statement run at load, or ignored")
claim("md0178", D, 178, "**Collect every declaration in every module in the graph before resolving any", "rule",
      "Every declaration of every module is collected before any body resolves: a struct of `a.npk` used "
      "in `b.npk`'s body, across an import cycle, resolves.",
      expect="run:0",
      src=main_("""    int32:v = raw fb();
    int32:w = raw fa();
%s
    exit 0i32;""" % chk("v == 2i32 && w == 3i32", 10), 'use "./b.npk".*;\nuse "./a.npk".*;'),
      files={"a.npk": CYC_A, "b.npk": CYC_B},
      wrong="refused: `A` not yet declared when `b.npk`'s body resolves")
claim("md0179", D, 179, "lets a function refer to one", "rule",
      "A function may refer to one declared below it in the same file.",
      expect="run:0",
      src=main_("""    int32:v = raw first();
%s
    exit 0i32;""" % chk("v == 8i32", 10), """func:first = int32() never fails { pass (raw second()) * 2i32; };
func:second = int32() never fails { pass 4i32; };"""),
      wrong="refused: `second` not yet declared")
claim("md0182", D, 182, "depends on itself other than through a pointer", "rule",
      "A struct whose size depends on itself across two modules (by value) is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", 'use "./a.npk".*;'),
      files={"a.npk": """mod:a;
use "./b.npk".*;
pub struct:SA = { SB:b; int32:n; };""",
             "b.npk": """mod:b;
use "./a.npk".*;
pub struct:SB = { SA:a; };"""},
      wrong="accepted: an infinitely sized struct")
claim("md0182b", D, 182, "other than through a pointer", "rule",
      "A struct cycle through a pointer is legal: `SA = { SB->:b; }` and `SB = { SA:a; }` compile.",
      expect="run:0",
      src=main_("""    exit 0i32;""", """struct:SA = { SB->:b; };
struct:SB = { SA:a; int32:n; };"""),
      wrong="refused as a cycle")
claim("md0182c", D, 182, "or a `const` whose initialiser", "rule",
      "A module constant whose initialiser depends on itself (through another) is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", """fixed int32:FIRST = SECOND + 1i32;
fixed int32:SECOND = FIRST;"""),
      wrong="accepted: a value read before it is set",
      note="the reference spells the constant `const`; HUNT2's module constant is `fixed` (md0212 tests "
           "the `const` spelling itself)")
claim("md0183", D, 183, "The diagnostic names the members in the order they refer to", "rule",
      "The cycle's diagnostic names its members (`FIRST`, `SECOND`) on its first line, not \"circular "
      "import\".",
      expect="sh:0",
      sh=sh_refuse({"r.npk": root("    exit 0i32;", """fixed int32:FIRST = SECOND + 1i32;
fixed int32:SECOND = FIRST;""")}) + """ || exit 1
l=$(grep -m1 'NITPICK-' npkc.out)
echo "$l" | grep -q FIRST && echo "$l" | grep -q SECOND""",
      wrong="the diagnostic names one member, or none")
claim("md0185", D, 185, "The same module graph must produce", "rule",
      "The same module graph compiles to the same program whichever import the loader enters first: "
      "swapping the root's two import lines leaves the emitted IR identical.",
      expect="sh:0",
      sh=SH_LIB + """for d in d1 d2; do
mkdir -p $d
cat > $d/a.npk <<'EOF'
""" + CYC_A + """
EOF
cat > $d/b.npk <<'EOF'
""" + CYC_B + """
EOF
done
cat > d1/r.npk <<'EOF'
""" + root("    int32:v = raw fa();\n    if (v != 3i32) { exit 10i32; }\n    exit 0i32;",
           'use "./a.npk".*;\nuse "./b.npk".*;') + """
EOF
cat > d2/r.npk <<'EOF'
""" + root("    int32:v = raw fa();\n    if (v != 3i32) { exit 10i32; }\n    exit 0i32;",
           'use "./b.npk".*;\nuse "./a.npk".*;') + """
EOF
(cd d1 && "$NPKC" r.npk -o r.ll > npkc.out 2>&1) || { head -3 d1/npkc.out; exit 3; }
(cd d2 && "$NPKC" r.npk -o r.ll > npkc.out 2>&1) || { head -3 d2/npkc.out; exit 3; }
grep -v '^source_filename\\|^; ModuleID' d1/r.ll > 1.ll
grep -v '^source_filename\\|^; ModuleID' d2/r.ll > 2.ll
wc -l 1.ll 2.ll
cmp 1.ll 2.ll""",
      wrong="the IR differs with the import order")

# ================================================================== 3. visibility
claim("md0199", D, 199, "strict binary visibility model", "rule",
      "Visibility has two levels only, public and private.",
      untestable="[vague] no third level's spelling is named whose refusal a program could check")
claim("md0201", D, 201, "Symbols are accessible only within the same module/file", "rule",
      "A private symbol of another file is not importable: `use \"./lib.npk\".private_here;` is refused.",
      expect="refuse",
      src=main_("""    int32:v = raw private_here();
    if (v != 0i32) { exit 10i32; }
    exit 0i32;""", 'use "./lib.npk".private_here;'),
      files={"lib.npk": LIB},
      wrong="accepted")
claim("md0201b", D, 201, "Intra-module access to private symbols is always permitted", "rule",
      "A module's own `pub` function may call its private one: the importer sees the result.",
      expect="run:0",
      src=main_("""    int32:v = raw f();
%s
    exit 0i32;""" % chk("v == 11i32", 10), 'use "./plib.npk".*;'),
      files={"plib.npk": """mod:plib;
func:inner = int32() never fails { pass 11i32; };
pub func:f = int32() never fails { pass (raw inner()); };"""},
      wrong="refused")
claim("md0203", D, 203, "qualified path from outside its module (`nested.internal()`", "rule",
      "`nested.internal()`, a private member called qualified from outside, is refused, NITPICK-RESOLVE-003.",
      expect="refuse:NITPICK-RESOLVE-003",
      src=main_("""    int32:v = raw nested.internal();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", NESTED),
      wrong="accepted, or refused with another code")
claim("md0204", D, 204, "`nested.SECRET`", "rule",
      "`nested.SECRET`, a private binding read qualified from outside, is refused, NITPICK-RESOLVE-003.",
      expect="refuse:NITPICK-RESOLVE-003",
      src=main_("""    int32:v = nested.SECRET;
    if (v != 2i32) { exit 10i32; }
    exit 0i32;""", NESTED),
      wrong="accepted, or refused with another code")
claim("md0204b", D, 204, "a hop through a private nested module", "rule",
      "`nested.deep.g()`, a `pub` member reached through a private nested module, is refused, "
      "NITPICK-RESOLVE-003.",
      expect="refuse:NITPICK-RESOLVE-003",
      src=main_("""    int32:v = raw nested.deep.g();
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", NESTED),
      wrong="accepted, or refused with another code")
claim("md0205", D, 205, "`use nested.internal;`), is `NITPICK-RESOLVE-003`", "rule",
      "`use nested.internal;`, naming a private member by a `use`, is refused, NITPICK-RESOLVE-003.",
      expect="refuse:NITPICK-RESOLVE-003",
      src=main_("""    int32:v = raw internal();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", NESTED + "\nuse nested.internal;"),
      wrong="accepted, or refused with another code")
claim("md0206", D, 206, "\"`internal` is private to `nested`\"", "rule",
      "The refusal says \"`internal` is private to `nested`\".",
      expect="sh:0",
      sh=sh_refuse({"r.npk": root("""    int32:v = raw nested.internal();
    if (v != 1i32) { exit 10i32; }
    exit 0i32;""", NESTED)}, "is private to"),
      wrong="another message")
claim("md0209", D, 209, "```nitpick", "example",
      "The four `pub` declarations (a function, a struct, a `pub const`, a `pub mod`) compile in a file, "
      "and an importer uses each.",
      expect="run:0",
      src=main_("""    int32:c = compute() ?| 0i32;
    Point:p = Point{ x: 2i32 };
    int32:u = raw utils.one();
%s
    exit 0i32;""" % chk("c + p.x + MAX + u == 104i32", 10), 'use "./publib.npk".*;'),
      files={"publib.npk": """mod:publib;
pub func:compute = int32() { pass 1i32; };
pub struct:Point = { int32:x; };
pub const int32:MAX = 100i32;
pub mod:utils = { pub func:one = int32() never fails { pass 1i32; }; };"""},
      wrong="refused (a declaration's spelling not the language's), or 10")
claim("md0212", D, 212, "pub const int32:MAX = 100i32;", "rule",
      "`pub const int32:MAX = 100i32;` declares a public module constant: `MAX` is 100.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("MAX == 100i32", 10), "pub const int32:MAX = 100i32;"),
      wrong="refused: `const` not the language's spelling")

# ================================================================== 4. functions
claim("md0219", D, 219, "Legacy C-style/Rust-style `func name() -> type` is banned", "rule",
      "The legacy `func add(...) -> int32 { … }` syntax is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "func add(int32:a, int32:b) -> int32 { pass (a + b); };"),
      wrong="accepted")
claim("md0221", D, 221, "```nitpick", "example",
      "`func:add = int32(int32:a, int32:b) { pass (a + b); };` compiles, and `add(2, 3)` is 5.",
      expect="run:0",
      src=main_("""    int32:s = add(raw v32(2i32), raw v32(3i32)) ?| 0i32;
%s
    exit 0i32;""" % chk("s == 5i32", 10), """func:add = int32(int32:a, int32:b) {
    pass (a + b);
};"""),
      wrong="refused, or 10")
claim("md0226", D, 226, "The compiler automatically wraps this in a `Result<int32>`", "rule",
      "The declared type is the success type, wrapped in `Result<int32>`: the call binds as a "
      "`Result<int32>` whose value is 5.",
      expect="run:0",
      src=main_("""    Result<int32>:r = add(raw v32(2i32), raw v32(3i32));
    if (r.is_error) { exit 10i32; }
%s
    exit 0i32;""" % chk("r.value == 5i32", 11), "func:add = int32(int32:a, int32:b) { pass (a + b); };"),
      wrong="refused (the call is a plain int32), or 10/11")
claim("md0226b", D, 226, "is the *success* type", "rule",
      "The call is a `Result<int32>`, not an `int32`: binding it to a plain `int32` is refused.",
      expect="refuse",
      src=main_("""    int32:s = add(raw v32(2i32), raw v32(3i32));
    if (s != 5i32) { exit 10i32; }
    exit 0i32;""", "func:add = int32(int32:a, int32:b) { pass (a + b); };"),
      wrong="accepted: the Result unwrapped silently")

# ================================================================== 5. driver interfaces (extern)
claim("md0230", D, 230, "**In-process FFI does not exist in Nitpick (D-149).**", "rule",
      "There is no in-process FFI; an `extern` block declares a driver process's interface.",
      untestable="[vague] a statement of the design; its observable parts are md0241-md0274's")
claim("md0235", D, 235, "line — past it, a segfault, a hang, or a scribbled heap in the foreign code", "rule",
      "A fault in the driver arrives in the Nitpick process as a value, never as an uninterceptable fault.",
      untestable="[tool] needs a running driver process to fault")
claim("md0241", D, 241, "```nitpick", "example",
      "The `cuda_driver` block (an opaque struct and two methods) is valid syntax: the program compiles.",
      expect="compile",
      src=main_("""    exit 0i32;""", """extern:"cuda_driver" = {
    opaque struct:KernelHandle;
    func:load_kernel = KernelHandle(int8[]:image);
    func:dispatch    = NIL(KernelHandle:k, int8[]:args);
};"""),
      wrong="refused: the example's method shape is not the language's")
claim("md0249", D, 249, "The string names the driver; the functions are its methods.", "rule",
      "The block's string names the driver and its functions are the driver's methods.",
      untestable="[vague] a statement of what the parts mean; md0250 checks the stub the methods become")
claim("md0250", D, 250, "lowers each method to a **Bridge stub**", "rule",
      "Each method of an `extern` block lowers to a stub: the emitted IR defines a function for the "
      "method `probe`.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within);
};""")}, pre=NB, post=" || exit 1\ngrep -c '^define' p.ll | head -1\ngrep -q '^define.*probe' p.ll"),
      wrong="no function emitted for the method")
claim("md0252", D, 252, "An `opaque struct` declared here is a", "rule",
      "An opaque struct declared in a block is a typed wire handle, minted by the driver, dead after a "
      "restart.",
      untestable="[tool] needs a running driver to mint a handle and restart")
claim("md0259", D, 259, "All driver methods return `Result<T>` like every other function", "rule",
      "A driver method's call is a `Result<T>`: binding `await probe(…)` to `Result<int64>` compiles.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within);
};""", """async func:use_probe = int64(Bridge->:b) {
    Result<int64>:r = await probe(b, raw duration_secs(1i64));
    if (r.is_error) { pass 0i64; }
    pass r.value;
};""")}, pre=NB),
      wrong="refused: the method's result is not a Result")
claim("md0260", D, 260, "**no per-method error contracts**", "rule",
      "Timeouts, driver death and protocol violations arrive as uniform negative codes in the D-141 space.",
      untestable="[tool] needs a running driver to time out, die or violate the protocol")
claim("md0265", D, 265, "written anymore. The grammar remains parsed and is refused by the checker", "rule",
      "A failure contract (`never fails`) on a driver method is parsed and refused by the checker, which "
      "names D-149.",
      expect="sh:0",
      sh=sh_refuse({"r.npk": ext_root("""extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within) never fails;
};""")}, "D-149", pre=NB),
      wrong="accepted, or refused without naming D-149 (or as a parse error)")
claim("md0270", D, 270, "Fixed-width scalars, POD structs of them, sized byte payloads, and typed", "rule",
      "A POD struct of fixed-width scalars is in the wire vocabulary: a method taking one compiles.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    func:put = int64(Bridge->:b, Pt:p, Duration:within);
};""", "struct:Pt = { int32:x; int32:y; };")}, pre=NB),
      wrong="refused: a POD struct not admitted")
claim("md0270b", D, 270, "Fixed-width scalars", "rule",
      "Every fixed-width scalar is in the wire vocabulary: a method taking an `int16` compiles.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    func:put = int64(Bridge->:b, int16:v, Duration:within);
};""")}, pre=NB),
      wrong="refused: only some fixed-width scalars admitted")
claim("md0270c", D, 270, "sized byte payloads", "rule",
      "A sized byte payload is in the wire vocabulary: a method taking an `int8[]` compiles.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    func:put = int64(Bridge->:b, int8[]:data, Duration:within);
};""")}, pre=NB),
      wrong="refused")
claim("md0270d", D, 270, "and typed", "rule",
      "A typed handle is in the wire vocabulary: a method taking the block's `opaque struct` compiles.",
      expect="sh:0",
      sh=sh_accept({"r.npk": ext_root("""extern:"mockif" = {
    opaque struct:H;
    func:put = int64(Bridge->:b, H:h, Duration:within);
};""")}, pre=NB),
      wrong="refused: a handle not admitted")
claim("md0271", D, 271, "Payloads are **copied out of shared memory before validation**", "rule",
      "Payloads are copied out of shared memory before validation.",
      untestable="[tool] the copy happens on a live ring; needs a running driver")
claim("md0273", D, 273, "Nothing address-shaped crosses in either direction: no pointers", "rule",
      "No pointer crosses the wire: a method taking an `int32->` (besides its `Bridge->`) is refused.",
      expect="sh:0",
      sh=sh_refuse({"r.npk": ext_root("""extern:"mockif" = {
    func:put = int64(Bridge->:b, int32->:p, Duration:within);
};""")}, pre=NB),
      wrong="accepted: a pointer crosses the wire")
claim("md0274", D, 274, "(which is now valid nowhere in the language)", "rule",
      "`void*` is valid nowhere: a parameter of type `void->` is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "func:take = int32(void->:p) never fails { pass 0i32; };"),
      wrong="accepted")
claim("md0279", D, 279, "an **interface hash derived from the `extern` block's signatures**", "rule",
      "The handshake carries an interface hash from the block's signatures; a stale driver is refused "
      "before any call.",
      untestable="[tool] needs a driver built against another interface")
claim("md0281", D, 281, "the generated stub implements the `Driver` trait with D-055's", "rule",
      "The stub implements the Driver trait with D-055's obligations (deadline, no partial results, "
      "supervised child, failsafe-reachable registry).",
      untestable="[tool] the obligations are kept at run time against a running driver")
claim("md0284", D, 284, "**C SDK header**", "rule",
      "The driver side is built against the C SDK header.",
      untestable="[tree] the SDK is a file of the compiler's tree, not something a program does")
claim("md0289", D, 289, "```nitpick", "example",
      "A driver method's call is read with `raw` or with `_!`; both forms compile and give the value.",
      expect="run:0",
      src=main_("""    int32:n = raw some_query(raw v32(1i32));
    int32:x = _! some_query(raw v32(1i32));
%s
    exit 0i32;""" % chk("n == 1i32 && x == 1i32", 10),
                "func:some_query = int32(int32:name) { pass name; };"),
      wrong="refused: a spelling not the language's",
      note="no driver runs here; `some_query` is an ordinary fallible function, which a driver method's "
           "call is like (line 259)")
claim("md0296", D, 296, "a `string` is `{ptr, len, cap}` and is **not** NUL-terminated", "rule",
      "A `string` is `{ptr, len, cap}` and is not NUL-terminated.",
      untestable="[internal] a string's machine layout is not observable from a program without `wild`")
claim("md0296b", D, 296, "a string literal converts at compile time", "rule",
      "A string literal converts to a `cstring` at compile time: `cstring:c = \"abc\";` compiles.",
      expect="compile",
      src=main_("""    cstring:c = "abc";
    discard(c);
    exit 0i32;"""),
      wrong="refused")
claim("md0296c", D, 296, "`to_cstring(s)` converts a runtime `string`", "rule",
      "`to_cstring(s)` converts a runtime string without an interior NUL: the result is not an error.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    Result<cstring>:r = to_cstring(s);
    if (r.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10 (an error for a string with no NUL)")
claim("md0298", D, 298, "`int32->`: Scalar pointer", "rule",
      "`int32->` is a pointer to an int32: a write through it reaches the int32.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    int32->:p = @x;
    <-p = 5i32;
%s
    exit 0i32;""" % chk("x == 5i32", 10)),
      wrong="refused, or 10")
claim("md0299", D, 299, "`MyStruct->`: Struct pointer", "rule",
      "`MyStruct->` is a pointer to a struct: a read through it sees the struct's field.",
      expect="run:0",
      src=main_("""    Pt:v = Pt{ x: 4i32, y: 5i32 };
    Pt->:q = @v;
    int32:y = (<-q).y;
%s
    exit 0i32;""" % chk("y == 5i32", 10), "struct:Pt = { int32:x; int32:y; };"),
      wrong="refused, or 10")
claim("md0300", D, 300, "`any->`: Erased/Opaque pointer", "rule",
      "`any->` is the erased pointer type: a parameter of type `any->` compiles.",
      expect="compile",
      src=main_("""    exit 0i32;""", "func:take = int32(any->:p) never fails { pass 0i32; };"),
      wrong="refused: `any->` is not a type",
      note="line 274 says `void*` is valid nowhere; this row names `any->` as `void*`")

# ================================================================== after run 1 (S45, S53)
# The programs' own mistakes; every expectation above is unchanged.
WHY_KW = ("`hidden` is a reserved word (m11/BRIEF.md §5): the support file's private function, which the "
          "claim does not name, is renamed `kept_here` (PARSE-001)")
for cid in ("md0021", "md0026", "md0027", "md0027b", "md0028", "md0030", "md0031"):
    refix(cid, WHY_KW, [("func:hidden =", "func:kept_here =")], field="files:network.npk")
for cid in ("md0024", "md0042"):
    refix(cid, WHY_KW, [("func:hidden =", "func:kept_here =")], field="sh")
for cid in ("md0099", "md0099b", "md0100", "md0101", "md0102"):
    refix(cid, WHY_KW, [("func:hidden =", "func:kept_here =")], field="files:sqlib.npk")
refix("md0099b", WHY_KW + "; main reads `kept_here()` (it agreed in run 1 for the keyword's PARSE-002, S55)",
      [("raw hidden()", "raw kept_here()")])
WHY_NB = ("`nbridge.npk` imports `./nsys.npk` (`pub use`), which the script did not copy (RESOLVE-005); it "
          "now copies both")
for cid in ("md0129b", "md0250", "md0259", "md0265", "md0270", "md0270b", "md0270c", "md0270d", "md0273"):
    refix(cid, WHY_NB + (" (md0273 agreed in run 1 for that RESOLVE-005, S55)" if cid == "md0273" else ""),
          [('lib/nbridge.npk" . || exit 5',
            'lib/nbridge.npk" "$(dirname "$NPKC")/../../lib/nsys.npk" . || exit 5')], field="sh")
refix("md0080b", "REACH-002 (D-179's arm contract) asked failsafe to name `md0080b.Boom`, though `classify` "
      "handles every failure of `m.boom`; the program's own failsafe now names it",
      [("    pass 0i32;\n};", "    pass 0i32;\n};\n\n" + failsafe_with("        (md0080b.Boom) { exit 80i32; },"))])

# ================================================================== after run 2
NB_ERRS = ("EShmCreate", "EShmSeal", "EShmMap", "EDriverSpawn", "EDriverProtocol", "EDriverFault",
           "EDriverDeadline", "ERingFull", "EBridgePoisoned", "EDriverError")
NB_ARMS = "".join("        (%s) { exit %di32; },\n" % (n, 60 + k) for k, n in enumerate(NB_ERRS))
WHY_REACH = ("REACH-002: failsafe must name each of `nbridge.npk`'s ten error constants, which the generated "
             "stub can raise (the compiler's own `extern_stub.npk` names them); the script's failsafe now does")
for cid in ("md0250", "md0259", "md0270", "md0270b", "md0270c", "md0270d", "md0273"):
    prev = next(c for c in CLAIMS if c["id"] == cid)["fixed"]   # run 1's reason, kept
    refix(cid, prev + "; then " + WHY_REACH, [("func:failsafe = int32(Error:e) {\n    pick (e) {\n",
                            "func:failsafe = int32(Error:e) {\n    pick (e) {\n" + NB_ARMS)], field="sh")
