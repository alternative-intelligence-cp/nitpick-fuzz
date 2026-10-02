"""M11 claims: BUILD_REFERENCE.md (lines 1-682) at HUNT2 (9126350), extracted by session 9.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). No M10 item tests a BUILD sentence.

Most of the reference describes the compiler's own build: the bootstrap ladder, the two
test runners, the verified build. Those claims are `tree`, `tool` or `z3`.
`npkg build` cannot build a project outside the compiler's repository: it reads the
floor's `runtime/npkrt.ll` from the manifest's root. That was measured before the
extraction, in a scratch project, as a probe of `npkg`'s spelling. What a script CAN check
is every refusal `npkg` makes before it builds anything, and every rule about what `npkc`
emits. Each `npkg` claim is an `sh:0` script with `$NPKG` (HUNT2's `npkg`) in a scratch
project: a manifest, maybe a lock, and a one-function entry.
"""
from m11lib import *

covers("BUILD", 1)

D = "BUILD"
FS = failsafe_text("")

ENTRY = "mod:main;\n\n" + main_("    exit 3i32;") + "\n" + FS
TOOLCHAIN = """
[toolchain]
llvm          = "20.1.2"
llc-flags     = ["-O0", "-filetype=obj", "-relocation-model=static"]
llc-opt-flags = ["-O2", "-filetype=obj", "-relocation-model=static"]
opt-flags     = ["-O2", "-S"]
lld-flags     = ["-static"]
"""
BASE = """[project]
name    = "demo"
version = "0.1.0"
%s
[build]
entry     = "src/main.npk"
output    = "build/demo"
opt-level = 0
"""
LOCK = "# nitpick.lock -- no dependencies\n"


def project(manifest, lock=True, extra=""):
    """A scratch project: nitpick.toml, src/main.npk, and nitpick.lock unless lock=False."""
    s = "mkdir -p src\ncat > nitpick.toml <<'EOF'\n" + manifest.rstrip() + "\nEOF\n"
    s += "cat > src/main.npk <<'EOF'\n" + ENTRY.rstrip() + "\nEOF\n"
    if lock:
        s += "cat > nitpick.lock <<'EOF'\n" + LOCK.rstrip() + "\nEOF\n"
    return s + extra


def npkg(args, pat, rc_ok="[ $rc -ne 0 ]"):
    """Run npkg with `args`; the script holds when the exit satisfies rc_ok and the output
    holds `pat` (a fixed string)."""
    return ('"$NPKG" %s > npkg.out 2>&1; rc=$?\necho "rc=$rc"; head -3 npkg.out | cut -c1-200\n'
            '%s && grep -q -F -- %s npkg.out' % (args, rc_ok, sh_quote(pat)))


def sh_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def test_entry(body):
    return BASE % "" + TOOLCHAIN + "\n[[test]]\n" + body.strip() + "\n"


NOT_KNOWN = "is not one this runner knows"


def stage_known(cid, line, quote, stage, text):
    claim(cid, D, line, quote, "row", text,
          expect="sh:0",
          sh=project(test_entry('name = "x"\nstage = "%s"\nkind = "bogus"\npath = "t"' % stage)) +
          '"$NPKG" test > npkg.out 2>&1; rc=$?\necho "rc=$rc"; head -2 npkg.out | cut -c1-200\n'
          '[ $rc -eq 2 ] && ! grep -q -F %s npkg.out' % sh_quote(NOT_KNOWN),
          wrong="the stage unknown to the runner (refused as \"%s\")" % NOT_KNOWN)


# ================================================================== the two tools
claim("bd0015", D, 15, "| **`npkc`** | the compiler — one module set to one object, or to one artifact |", "row",
      "npkc compiles one module set to one object or artifact.",
      untestable="[vague] the row names a role; what npkc emits (text, D-067) is bd0175's claim")
claim("bd0016", D, 16, "| **`npkg`** | the driver — reads the manifest", "row",
      "npkg reads the manifest: in a directory with none, `npkg build` refuses and names `nitpick.toml`.",
      expect="sh:0", sh=npkg("build", "nitpick.toml"),
      wrong="npkg runs without a manifest")
claim("bd0018", D, 18, "**Naming discrepancy to settle.**", "rule",
      "The package manager is `npkg`, not `npkpkg`.",
      untestable="[tree] a note about the compiler repository's CLAUDE.md")

# ================================================================== 1. the manifest
claim("bd0027", D, 27, "One schema (D-077). Six tables", "rule",
      "The manifest has six tables and the `[[test]]` array.",
      untestable="[vague] the sentence lists the schema; bd0462-bd0464 test the `[[test]]` keys it refuses")
claim("bd0030", D, 30, "```toml", "example",
      "The example manifest (nlibc, with `[dependencies]`, `[verify]` and `[limits]`) is one `npkg` builds.",
      untestable="[tool] `npkg build` reads the floor's `runtime/npkrt.ll` from the manifest's root, so a "
                 "project outside the compiler's repository does not build (measured in a scratch project "
                 "before the extraction)")
claim("bd0036", D, 36, "PLANNED, read by nothing today", "rule",
      "`target` is planned and read by nothing.",
      untestable="[tool] what a build makes of `target` needs a build that completes (bd0030)")
claim("bd0066", D, 66, "`target` is READ BY", "rule",
      "Every build is one executable from `[build] entry`; `target` is read by nothing.",
      untestable="[tool] needs a completed build (bd0030)")
claim("bd0072", D, 72, "**`[project]` is identity, `[build]` is settings.**", "rule",
      "`entry` lives in `[build]`, not `[project]`.",
      untestable="[vague] the sentence states the schema's split; it names no refusal")
claim("bd0074", D, 74, "**`[toolchain]` is an INPUT, not a setting** (D-204)", "rule",
      "The toolchain is a build input: a manifest with no `[toolchain]` pin is refused, naming the toolchain.",
      expect="sh:0", sh=project(BASE % "") + npkg("build", "toolchain"),
      wrong="the build proceeds unpinned")
claim("bd0075", D, 75, "version is an EXACT PATCH RELEASE: a minor-version pin is insufficient", "rule",
      "The pin is an exact patch release: `llvm = \"20.1\"` (a minor-version pin) is refused.",
      expect="sh:0",
      sh=project(BASE % "" + TOOLCHAIN.replace('llvm          = "20.1.2"', 'llvm          = "20.1"')) +
      npkg("build", "20.1"),
      wrong="accepted: a minor-version pin")
claim("bd0079", D, 79, "the thing that runs them rather than restated there", "rule",
      "The flag lists are read by the tool that runs them.",
      untestable="[tool] which flags llc and opt were run with is visible only in a completed build (bd0030)")
claim("bd0088", D, 88, "**`[verify]` belongs in the manifest**", "rule",
      "The verification flags are the manifest's `[verify]`, not the command line's.",
      untestable="[z3] `npkg verify` needs the pinned z3")
claim("bd0095", D, 95, "**The solver is an INPUT like the toolchain**", "rule",
      "Both runners refuse a mismatched z3 version or hash, no `rlimit=`, or a wall-clock knob.",
      untestable="[z3] needs the pinned z3 and `npkg verify`")
claim("bd0112", D, 112, "**There is no `edition` key** (D-077)", "rule",
      "There is no `edition` key: a manifest with `edition = \"2024\"` is refused.",
      expect="sh:0",
      sh=project(BASE % 'edition = "2024"\n' + TOOLCHAIN) + npkg("build", "edition"),
      wrong="the key accepted (or ignored)")
claim("bd0118", D, 118, "`nitpick.lock` records, for every dependency in the transitive graph", "rule",
      "The lock records every dependency's exact version and content hash, and is committed.",
      untestable="[tool] dependencies bind nothing today (bd0161); the lock's rows are never written")
claim("bd0121", D, 121, "`npkg build` **reads the lock and never writes it.**", "rule",
      "`npkg build` never writes the lock: a build refused for a missing lock leaves no `nitpick.lock` behind.",
      expect="sh:0",
      sh=project(BASE % "" + TOOLCHAIN, lock=False) +
      '"$NPKG" build > npkg.out 2>&1; rc=$?\necho "rc=$rc"; head -2 npkg.out | cut -c1-200\n'
      '[ $rc -ne 0 ] && [ ! -e nitpick.lock ]',
      wrong="the build wrote a lock")
claim("bd0122", D, 122, "error, not an invitation to resolve", "rule",
      "A missing lock is an error, not an invitation to resolve: `npkg build` refuses, naming `nitpick.lock`.",
      expect="sh:0", sh=project(BASE % "" + TOOLCHAIN, lock=False) + npkg("build", "nitpick.lock"),
      wrong="the build resolves, or runs without a lock")

# ================================================================== 2. no network
claim("bd0126", D, 126, "## 2. A build never touches the network", "rule",
      "A build never touches the network; resolution is `npkg update`'s alone.",
      untestable="[platform] a build's network use is not observable here; bd0453 tests `npkg update`")

# ================================================================== 3. module resolution
claim("bd0154", D, 154, "| `use \"./util.npk\"` , `use \"../x/y.npk\"` | the **importing file's** directory |", "row",
      "A `../` path resolves against the importing file's directory.",
      expect="sh:0",
      sh="mkdir -p sub x\ncat > x/y.npk <<'EOF'\nmod:y;\npub func:fy = int32() never fails { pass 8i32; };\nEOF\n"
         "cat > sub/a.npk <<'EOF'\nmod:a;\nuse \"../x/y.npk\".*;\npub func:fa = int32() never fails { pass (raw fy()); };\nEOF\n"
         "cat > r.npk <<'EOF'\n" + ("mod:r;\nuse \"./sub/a.npk\".*;\n\n" + main_(
             "    int32:v = raw fa();\n    if (v != 8i32) { exit 10i32; }\n    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out\n[ $rc -eq 0 ] || exit 3\n"
         "llc -O0 -filetype=obj -relocation-model=static r.ll -o r.o && ld.lld -static r.o \"$NPKRT\" -o r || exit 4\n"
         "env -i ./r < /dev/null; e=$?; echo \"exit=$e\"; [ $e -eq 0 ]",
      wrong="refused: resolved elsewhere")
claim("bd0155", D, 155, "| `use \"nfs/path.npk\"` | the **dependency roots** |", "row",
      "A path not starting with `.` resolves against the dependency roots only: with no dependency, "
      "`use \"nfs/path.npk\"` is refused even with the file beside the importer.",
      expect="sh:0",
      sh="mkdir -p nfs\ncat > nfs/path.npk <<'EOF'\nmod:path;\npub func:fp = int32() never fails { pass 4i32; };\nEOF\n"
         "cat > r.npk <<'EOF'\n" + ("mod:r;\nuse \"nfs/path.npk\".*;\n\n" + main_(
             "    int32:v = raw fp();\n    if (v != 4i32) { exit 10i32; }\n    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out\n[ $rc -eq 1 ]",
      wrong="accepted: resolved against the importing file's directory")
claim("bd0156", D, 156, "| `use std.math.*` | the standard library |", "row",
      "`use std.math.*;` is the standard library's path: the program compiles.",
      expect="compile", src=main_("    exit 0i32;", "use std.math.*;"),
      wrong="refused")
claim("bd0158", D, 158, "A dependency named `nfs` declared at `../nfs` roots at **`../nfs/src/`**", "rule",
      "A dependency at `../nfs` roots at `../nfs/src/`.",
      untestable="[tool] dependencies bind nothing today (bd0161); the root is never formed")
claim("bd0161", D, 161, "the dependency-root form is PLANNED, not", "rule",
      "Today `use \"dep/thing.npk\"` is NITPICK-RESOLVE-005.",
      expect="refuse:NITPICK-RESOLVE-005",
      src=main_("    exit 0i32;", 'use "dep/thing.npk".*;'),
      wrong="accepted, or refused with another code")
claim("bd0167", D, 167, "**An ambiguous path is an error, not a first match.**", "rule",
      "Two dependencies supplying one path fail the build, naming both.",
      untestable="[tool] dependencies bind nothing today (bd0161)")

# ================================================================== 4. what a build does
claim("bd0175", D, 175, "Per D-067 the compiler **emits text and invokes tools**; it links nothing.", "rule",
      "npkc emits LLVM IR text and links nothing: its output is a text `.ll`, and no object or executable "
      "appears.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\n" + main_("    exit 0i32;") + "\n" + FS).rstrip() + "\nEOF\n"
         "\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1 || exit 3\n"
         "head -c 300 r.ll | tr -d '\\n' | cut -c1-120; echo; ls\n"
         "grep -q -m1 -E '^(; ModuleID|source_filename|target)' r.ll && [ \"$(ls | sort | tr '\\n' ' ')\" = \"npkc.out r.ll r.npk \" ]",
      wrong="an object or executable produced, or binary output")
claim("bd0177", D, 177, "```", "example",
      "The build pipeline: module graph, npkc to .ll, opt, llc at opt-level, the undefined-symbol scan, ld.lld.",
      untestable="[tool] `npkg build`'s pipeline needs a project in the compiler's tree (bd0030)")
claim("bd0187", D, 187, "**The undefined-symbol scan is a permanent pipeline step", "rule",
      "Every object is scanned and the build fails on an undefined symbol outside the runtime's allowlist.",
      untestable="[tool] the scan is `npkg build`'s (bd0030); a Nitpick program cannot name an outside symbol")
claim("bd0195", D, 195, "**An unreferenced prelude item is not emitted (D-262 §1, 1.5.2d).**", "rule",
      "An unreferenced prelude item is not emitted: a program that calls nothing has a few defines, and no "
      "`string_concat`.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\n" + main_("    exit 0i32;") + "\n" + FS).rstrip() + "\nEOF\n"
         "\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1 || exit 3\n"
         "n=$(grep -c '^define' r.ll); echo \"defines=$n bytes=$(wc -c < r.ll)\"\n"
         "[ \"$n\" -lt 40 ] && ! grep -q '^define[^(]*string_concat' r.ll",
      wrong="the whole prelude emitted")
claim("bd0215", D, 215, "**The scan's reader is `npkg`'s own**", "rule",
      "The scan reads the object's ELF symbol table itself, against the runtime's exports.",
      untestable="[tree] the scan's implementation and its counts")
claim("bd0235", D, 235, "Verification, where `[verify]` requests it, runs against the IR and the source", "rule",
      "Verification runs over SMT-LIB2 text to z3.",
      untestable="[z3] needs the pinned z3")
claim("bd0238", D, 238, "A failure in any subprocess is a nonzero exit status the driver reports", "rule",
      "A subprocess's failure is a nonzero exit the driver reports.",
      untestable="[tool] needs a build that reaches its subprocesses (bd0030)")
claim("bd0242", D, 242, "**`llc` must be invoked at the manifest's `opt-level`", "rule",
      "llc is invoked at the manifest's opt-level.",
      untestable="[tool] needs a completed build (bd0030)")
claim("bd0249", D, 249, "**Every emitted function checks its stack (D-305, 1.5.8 step 2).**", "rule",
      "Every define the compiler writes carries \"split-stack\": a program's own function does.",
      expect='ir:^define [^\\n]*@"npk\\.bd0249\\.helper"\\([^\\n]*"split-stack"',
      src=main_("""    int32:v = raw helper(raw v32(2i32));
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", "func:helper = int32(int32:x) never fails { pass (x + 1i32); };"),
      wrong="no split-stack attribute on the define")
claim("bd0252", D, 252, "The floor's object carries two linker", "rule",
      "The floor's object carries the notes `.note.GNU-split-stack` and `.note.GNU-no-split-stack`.",
      expect="sh:0",
      sh="llvm-readelf -S \"$NPKRT\" > s.txt 2>&1 || exit 3\ngrep -o 'note.GNU[a-z-]*' s.txt | sort -u\n"
         "grep -q 'note.GNU-split-stack' s.txt && grep -q 'note.GNU-no-split-stack' s.txt",
      wrong="a note missing")
claim("bd0260", D, 260, "floor's own functions carry no prologue", "rule",
      "The floor's own functions carry no split-stack prologue.",
      untestable="[internal] the floor's machine code")
claim("bd0268", D, 268, "A unit that does not define `failsafe` DECLARES `@npk_failsafe`", "rule",
      "A unit that does not define `failsafe` declares `@npk_failsafe`, so a non-root module compiled alone "
      "assembles: llc accepts it.",
      expect="sh:0",
      sh="cat > lib.npk <<'EOF'\nmod:lib;\nerror:E1;\npub func:f = int32(int32:x) { if (x > 9i32) { fail E1; } pass (x * 2i32); };\nEOF\n"
         "\"$NPKC\" lib.npk -o lib.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out\n[ $rc -eq 0 ] || exit 3\n"
         "grep -m1 'npk_failsafe' lib.ll | cut -c1-100\n"
         "grep -q '^declare[^\\n]*@npk_failsafe' lib.ll && llc -O0 -filetype=obj -relocation-model=static lib.ll -o lib.o",
      wrong="no declaration, and llc refuses the undefined value")
claim("bd0269", D, 269, "a generic's body is exported with its module, instantiation happens in the", "rule",
      "A generic's body is exported with its module and instantiated in the user; identical specialisations "
      "fold at link time.",
      untestable="[tool] needs a multi-object link that `npkg` performs (bd0030)")
claim("bd0272", D, 272, "Whole-program compilation is available as an opt-in", "rule",
      "Whole-program compilation is an opt-in for release and verification builds.",
      untestable="[vague] the sentence names no switch")
claim("bd0277", D, 277, "**A verification build and a release build are always clean builds.**", "rule",
      "Verification and release builds are always clean.",
      untestable="[tool] needs `npkg verify` and a release build (bd0030)")

# ================================================================== 5. reproducibility
claim("bd0290", D, 290, "**The same inputs produce a byte-identical output** (D-078).", "rule",
      "The same input produces a byte-identical emission, wherever it is compiled: one program compiled in "
      "two directories gives two identical `.ll` files.",
      expect="sh:0",
      sh="mkdir -p one/deeper two\nfor d in one/deeper two; do cat > $d/r.npk <<'EOF'\n" +
         ("mod:r;\n\n" + main_("    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\ndone\n(cd one/deeper && \"$NPKC\" r.npk -o r.ll > npkc.out 2>&1) || exit 3\n"
         "(cd two && \"$NPKC\" r.npk -o r.ll > npkc.out 2>&1) || exit 3\ncmp one/deeper/r.ll two/r.ll",
      wrong="the emission depends on the directory")
claim("bd0292", D, 292, "No timestamps, build paths, hostnames, or environment values in the artifact.", "rule",
      "The emission carries no build path: the `.ll` names no part of the directory it was compiled in.",
      expect="sh:0",
      sh="mkdir -p wxyzdir\ncat > wxyzdir/r.npk <<'EOF'\n" + ("mod:r;\n\n" + main_("    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\n(cd wxyzdir && \"$NPKC\" r.npk -o r.ll > npkc.out 2>&1) || exit 3\n"
         "! grep -q -e wxyzdir -e \"$(hostname)\" wxyzdir/r.ll",
      wrong="the directory or the hostname is in the emission")
claim("bd0295", D, 295, "D-064's mangled names are readable and reversible with **no hash**", "rule",
      "A generic instance's name is readable, with no hash: `idt` instantiated at `int32` is named by both.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\nfunc:idt<T> = int32(T:_~x) never fails { pass 5i32; };\n\n" + main_(
          "    int32:v = raw idt::<int32>(1i32);\n    if (v != 5i32) { exit 10i32; }\n    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1 || exit 3\n"
         "grep -o '@\"npk\\.r\\.idt[^\"]*\"' r.ll | sort -u | head -3\n"
         "grep -q '@\"npk\\.r\\.idt[^\"]*int32[^\"]*\"' r.ll",
      wrong="a hashed or unreadable instance name")
claim("bd0299", D, 299, "driver refuses a mismatching toolchain loudly", "rule",
      "The driver refuses a mismatching toolchain: a pin of 20.1.1 with 20.1.2 installed is refused.",
      expect="sh:0",
      sh=project(BASE % "" + TOOLCHAIN.replace('"20.1.2"', '"20.1.1"')) + npkg("build", "20.1.1"),
      wrong="the build proceeds with another toolchain")
claim("bd0300", D, 300, "A `repro` check builds twice from different working directories", "rule",
      "A repro check builds twice from different directories and byte-compares the emissions.",
      untestable="[tree] the harness's check; bd0290 does the same over a program")
claim("bd0303", D, 303, "**The pin is a version, and a version is not a binary**", "rule",
      "The pin is a version; the cross-machine claim is the compiler's own emission; every ladder run "
      "prints its sha256 report.",
      untestable="[tool] the ladder's report is `npkg build`'s in the compiler's tree (bd0030)")

# ================================================================== 6. the bootstrap ladder
for _ln, _q in ((335, "| **Seed** |"), (336, "| **1** |"), (337, "| **2** |")):
    claim("bd%04d" % _ln, D, _ln, _q, "row", "A stage of the bootstrap ladder.",
          untestable="[tree] the compiler's own bootstrap")
claim("bd0339", D, 339, "**Self-hosting is the fixpoint of the compiler's emission of itself**", "rule",
      "Self-hosting: stage N and stage N+1 emit the compiler byte-identically.",
      untestable="[tool] needs the compiler's own build ladder")
claim("bd0351", D, 351, "**Declared at 1.4.9 (2026-09-02).**", "rule", "The fixpoint held at 1.4.9.",
      untestable="[tree] a record of the compiler's history")
claim("bd0362", D, 362, "**The prototype `npkc` is not the seed** (D-085, superseding D-079).", "rule",
      "The prototype is not the seed.", untestable="[tree] the compiler's bootstrap")
claim("bd0368", D, 368, "**The parser never restricts; the backend does.**", "rule",
      "The parser accepts the whole grammar; a construct the backend cannot lower is a backend diagnostic.",
      untestable="[vague] since D-271 no construct is refused by rung; no program can tell the parser's "
                 "acceptance from the checker's here")
claim("bd0374", D, 374, "The seed is **invoked once, ever**", "rule", "The seed is invoked once.",
      untestable="[tree] the compiler's bootstrap")
claim("bd0379", D, 379, "**What the fixpoint does not prove.**", "rule",
      "The fixpoint does not exclude a seed backdoor.", untestable="[tree] a statement about the bootstrap")
claim("bd0397", D, 397, "They interact in one place.", "rule", "The capability ladder meets the bootstrap at self-hosting.",
      untestable="[tree] the compiler's plan")
claim("bd0402", D, 402, "**Subset 1 is what the two ladders share.**", "rule", "Subset 1's contents.",
      untestable="[tree] the compiler's own sources' subset")
claim("bd0416", D, 416, "**Once stage 2 exists, primitives are implemented in Nitpick.**", "rule",
      "Primitives are implemented in Nitpick after self-hosting.", untestable="[tree] the compiler's sources")
for _ln, _q in ((432, "| build with the current compiler |"), (433, "| build again with that one |"),
                (434, "| build a third time |")):
    claim("bd%04d" % _ln, D, _ln, _q, "row", "A pass of an ABI change's rebuild.",
          untestable="[tool] the compiler's own rebuild")

# ================================================================== 7. commands
claim("bd0451", D, 451, "| `npkg build` | reads lock + vendored source", "row",
      "`npkg build` reads the lock: with none, it refuses with D-078's sentence, \"a missing lock is an error\".",
      expect="sh:0",
      sh=project(BASE % "" + TOOLCHAIN, lock=False) + npkg("build", "a missing lock is an error"),
      wrong="the build resolves, or proceeds")
claim("bd0452", D, 452, "| `npkg test` | builds the compiler", "row",
      "`npkg test` builds the compiler, runs the self-check and every `[[test]]` in order.",
      untestable="[tool] `npkg test` builds the compiler's ladder first, longer than a script's 60 s; "
                 "bd0462-bd0464 test its refusals before anything runs")
claim("bd0453", D, 453, "| `npkg update` | PLANNED — refused today by name", "row",
      "`npkg update` is refused today by name: \"there is nothing to resolve in a single-repository world\".",
      expect="sh:0", sh=npkg("update", "there is nothing to resolve in a single-repository world"),
      wrong="update runs, or is refused otherwise")
claim("bd0454", D, 454, "| `npkg verify` | the ladder, then the VERIFIED build", "row",
      "`npkg verify` runs the verified build.", untestable="[z3] needs the pinned z3")

# ------------------------------------------------------------------ 7.1 test targets
claim("bd0462", D, 462, "entry a runner cannot honour is refused BY NAME before anything runs", "rule",
      "An entry with a stage the runner does not know is refused by name before anything runs, exit 2.",
      expect="sh:0",
      sh=project(test_entry('name = "x"\nstage = "nosuch"\npath = "t"')) +
      npkg("test", "nosuch", rc_ok="[ $rc -eq 2 ]"),
      wrong="the entry skipped, or the run started")
claim("bd0463b", D, 463, "never skipped: a stage it does not know, a `kind` on a stage that has none", "rule",
      "A `kind` on a stage that has none is refused by name, exit 2.",
      expect="sh:0",
      sh=project(test_entry('name = "x"\nstage = "program"\nkind = "positive"\npath = "t"')) +
      npkg("test", "kind", rc_ok="[ $rc -eq 2 ]"),
      wrong="accepted")
claim("bd0464", D, 464, "compile entry with no kind, no `paths`/`path` (or both), a key the schema lacks", "rule",
      "A compile entry with no `kind` is refused by name, exit 2.",
      expect="sh:0",
      sh=project(test_entry('name = "x"\nstage = "compile"\npath = "t"')) +
      npkg("test", "kind", rc_ok="[ $rc -eq 2 ]"),
      wrong="accepted")
claim("bd0464b", D, 464, "no `paths`/`path` (or both)", "rule",
      "An entry with both `path` and `paths` is refused by name, exit 2.",
      expect="sh:0",
      sh=project(test_entry('name = "x"\nstage = "program"\npath = "t"\npaths = ["u"]')) +
      npkg("test", "path", rc_ok="[ $rc -eq 2 ]"),
      wrong="accepted")
claim("bd0464c", D, 464, "a key the schema lacks", "rule",
      "An entry with a key the schema lacks is refused by name, exit 2.",
      expect="sh:0",
      sh=project(test_entry('name = "x"\nstage = "program"\npath = "t"\nflavour = "mint"')) +
      npkg("test", "flavour", rc_ok="[ $rc -eq 2 ]"),
      wrong="accepted")
claim("bd0466", D, 466, "```toml", "example",
      "Three `[[test]]` entries: conformance (compile, positive), types (check, recursive), programs.",
      untestable="[tool] running the entries needs the compiler's ladder first (bd0452)")
stage_known("bd0487", 487, "| `compile` (the default) |", "compile",
            "`compile` is a stage the runner knows (an entry with it is refused for its bad kind, not its stage).")
stage_known("bd0488", 488, "| `parse` | `tools/parse_check` |", "parse", "`parse` is a stage the runner knows.")
stage_known("bd0489", 489, "| `resolve` | `tools/resolve_check` |", "resolve", "`resolve` is a stage the runner knows.")
stage_known("bd0490", 490, "| `check` | `tools/check` |", "check", "`check` is a stage the runner knows.")
stage_known("bd0491", 491, "| `accept` | `tools/check` | accepted in silence |", "accept", "`accept` is a stage the runner knows.")
stage_known("bd0492", 492, "| `fixture` | the compiler under test |", "fixture", "`fixture` is a stage the runner knows.")
stage_known("bd0493", 493, "| `program` | the compiler under test |", "program", "`program` is a stage the runner knows.")
stage_known("bd0494", 494, "| `runtime` | `llc` + `ld.lld` |", "runtime", "`runtime` is a stage the runner knows.")
stage_known("bd0495", 495, "| `verify` | the compiler under test, z3 |", "verify", "`verify` is a stage the runner knows.")
stage_known("bd0496", 496, "| `cost` | the compiler under test, the runtime's `NPK_HEAP_STATS` |", "cost",
            "`cost` is a stage the runner knows.")
stage_known("bd0497", 497, "| `explore` | the compiler under test, the explored floor, the shim |", "explore",
            "`explore` is a stage the runner knows.")
claim("bd0499", D, 499, "Membership stays with the stage", "rule",
      "A file another file imports is skipped as a fixture.", untestable="[tool] needs a run of `npkg test` (bd0452)")
claim("bd0506", D, 506, "**Expectations live in the test file**", "rule",
      "Expectations live in the test file.", untestable="[tree] a convention of the compiler's tests")
claim("bd0509", D, 509, "```nitpick", "example",
      "The expectation markers: expect-error, -at, expect-note, expect-exit, stress, argv, expect-no-parse-error, "
      "expect-obligation.",
      untestable="[tool] the markers are read by `npkg test` and the harness (bd0452)")
claim("bd0529", D, 529, "`CODE path:line:col: message` (1.0.8), with `note ` or `warning ` in front", "rule",
      "A diagnostic renders as `CODE path:line:col: message`, with `note ` in front of a note.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\nmod:m = {\n    func:hid = int32() never fails { pass 1i32; };\n};\n\n" + main_(
          "    int32:v = raw m.hid();\n    exit 0i32;") + "\n" + FS).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -3 npkc.out | cut -c1-120\n[ $rc -eq 1 ] || exit 3\n"
         "head -1 npkc.out | grep -q -E '^NITPICK-[A-Z]+-[0-9]{3} r\\.npk:[0-9]+:[0-9]+: ' && "
         "grep -q -E '^note NITPICK-[A-Z]+-[0-9]{3} r\\.npk:[0-9]+:[0-9]+: ' npkc.out",
      wrong="another shape")
claim("bd0531", D, 531, "place of the position for a spanless diagnostic (D-162)", "rule",
      "A spanless diagnostic renders `<no span>` in place of the position.",
      untestable="[vague] the text names no diagnostic that has no span")
claim("bd0536", D, 536, "**A finding at a `<derived-N>` line fails the unit**", "rule",
      "A finding at a `<derived-N>` line fails the unit.", untestable="[tool] a rule of `npkg test` (bd0452)")
claim("bd0544", D, 544, "**A negative test with no `expect-error` is a failing test.**", "rule",
      "A negative test with no expect-error fails.", untestable="[tool] a rule of `npkg test` (bd0452)")
claim("bd0547", D, 547, "**Unexpected diagnostics fail a test as surely as missing ones.**", "rule",
      "An unexpected diagnostic fails a test.", untestable="[tool] a rule of `npkg test` (bd0452)")
claim("bd0576", D, 576, "**A `verify` test names its rows exactly**", "rule",
      "A verify test names its rows exactly.", untestable="[z3] a verify test's rows")
claim("bd0585", D, 585, "**The elided IR is an inventory**", "rule",
      "The elided IR's traps and assumes are counted by group.", untestable="[z3] needs the verified build")
claim("bd0618", D, 618, "**`expect-no-parse-error` is the load-bearing one.**", "rule",
      "expect-no-parse-error asserts the file reached the backend.", untestable="[tool] a marker `npkg test` reads")
claim("bd0623", D, 623, "**The suite it was written for retired at 1.5.4 step 4", "rule",
      "tests/rejection/ retired at 1.5.4.", untestable="[tree] the compiler's test tree")
claim("bd0634", D, 634, "**The harness is itself tested.**", "rule",
      "The harness's self-check feeds it wrong expectations and requires each to fail.",
      untestable="[tool] `npkg test --selfcheck` builds the compiler first (bd0452)")
claim("bd0646", D, 646, "**Parity between the runners is measured, not assumed**", "rule",
      "The parity stage diffs the two runners' verdicts.", untestable="[tree] the harness's stage")
claim("bd0653", D, 653, "**The descriptor ceiling (1.5.1b step 5).**", "rule",
      "A runner lowers its soft RLIMIT_NOFILE to `[limits] nofile` before it spawns anything.",
      untestable="[tool] observable only in programs a run of `npkg test` spawns (bd0452)")
claim("bd0669", D, 669, "**Test-target declaration.**", "rule", "Settled: see §7.1.",
      untestable="[tree] a settled open item")

# ================================================================== after run 1 (S45, S53)
# The programs' own mistakes; every expectation above is unchanged.
# (A re-spelling of the eleven stage scripts after run 1 was withdrawn before run 3: the runner
#  checks the stage before the kind, so a known stage is told from an unknown one as first
#  written; PROGRESS.md records run 2.)
refix("bd0529", "a note may come before its error (the note at the declaration came first): the script now "
      "looks for an error line and a note line anywhere in the output, not the error first",
      [("head -1 npkc.out | grep -q -E '^NITPICK-[A-Z]+-[0-9]{3} r\\.npk:[0-9]+:[0-9]+: ' && ",
        "grep -q -E '^NITPICK-[A-Z]+-[0-9]{3} r\\.npk:[0-9]+:[0-9]+: ' npkc.out && ")], field="sh")
