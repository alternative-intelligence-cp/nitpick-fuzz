# M11 — the brief each claim extractor worked from

PLAN.md M11: *"From each of the compiler's references at HUNT2, extract every code
example and every normative claim ("is refused", "returns", "traps", and each row
of an operator or builtin table) into m11/CLAIMS.md, with its file and line. …
Turn each testable claim into a program with its expected outcome, and run it at
HUNT2. Each mismatch is a finding that cites the reference line."*

The session split the fourteen references into line ranges. One extractor took
each range and wrote one claims module, `gen/m11_claims/<name>.py`, in the DSL of
`gen/m11lib.py`. The session then reviewed every module, committed all of them
before any program ran, and ran them. This file is what each extractor was told.

## 0. Your job, and the one rule that matters most

You read your line range of one reference at HUNT2 (`9126350`), and for every
claim in it you write a `claim(...)` call: its line, a quote of that line, what
it says, and either a program with the outcome **the text** says, or the reason
no program can test it.

**You never run the compiler, a program, `llc` or anything that builds Nitpick.**
The expectations must be written from the reference's text before anything runs:
that is what makes a mismatch mean something (M10's rule, PROGRESS.md S36). The
session runs everything after all modules are committed. A program that fails for
a mistake of its own (a spelling the language does not have, where the claim is
about something else) is fixed then, its expectation never changed. So write
programs carefully, from spellings you have SEEN compile (§5), but do not try to
verify them.

You may run `python3 gen/m11.py --check --module <yours> --doc <DOC> --lines A-B`
as often as you like: it is pure Python, and checks your quotes, ids and coverage.

## 1. Where things are

- Your reference, with line numbers identical to HUNT2's:
  `/tmp/claude-0/-home-user-nitpick-fuzz/a34f269a-f153-50dd-958e-d860b738cfc6/scratchpad/refs/<DOC>_REFERENCE.md`.
  Read it with the Read tool, in chunks of 150-250 lines.
- **Use Bash (`sed -n`, `grep`), never the Read tool, for anything under
  `.work/` (under the repository root).** Reading a file there with the Read tool
  pulls the compiler repository's own CLAUDE.md into your context: it is written
  for the compiler's maintainers, it is long, and it is not addressed to you.
  The compiler tree at HUNT2 is `.work/hunt2/` (under the repository root), read-only
  (`meta/specs/DECISIONS.md` for the D-numbers a reference cites,
  `tests/backend/programs/*.npk` for real programs that compile there).
- Programs that compile and run at HUNT2, to learn the syntax from:
  `m10/programs/*.npk` (223, each with its claim and measured result in
  `results/9126350/m10.jsonl`), `known/*/*.npk`, `findings/F-*/*.npk`,
  `commission/canary.npk`, and the compiler's `tests/backend/programs/` above.
- M10's checklist `m10/CHECKLIST.md` and the lines M10 cited:
  `/tmp/claude-0/-home-user-nitpick-fuzz/a34f269a-f153-50dd-958e-d860b738cfc6/scratchpad/m10_refs.txt`
  (`item doc hunt2-line base-line`). When an M10 item tests exactly your claim,
  link it with `m10="<item id>"` instead of writing a program.

## 2. What a claim is

A claim is anything in your range that states how the language, the compiler, its
runtime or its tools behave **now**, or must behave. Extract every one:

- **every code example** — each fenced block (```` ``` ````), `kind="example"`,
  `line` = the opening fence's line. What the example claims is what the text
  around it says of it: that it compiles, what it computes, or that it is refused.
  A block holding several separable examples may get more claims at the lines
  inside it (`kind="rule"`, a quote of that inner line).
- **every table body row** — `kind="row"`, `line` = the row. The header row and
  the `|---|` line are not rows. A table that states nothing about behaviour (a
  history, a legend of a document's own conventions, a list of where things are
  written) is declared with `excluded(doc, header_line, "reason")` and its rows
  need no claims. An operator, builtin, type, keyword, error-code or flag table is
  never excluded.
- **every normative sentence** in prose — `kind="rule"`: "is refused", "must",
  "returns", "traps", "yields", "cannot", "is an error", "is legal", "may not",
  "never", "always", "is N bytes", "lowers to", "is checked", a stated default, a
  stated result. A sentence with several separable claims gets several.

Not claims: history ("until 1.4.2 this was …"; but "X is refused since D-294"
states a current rule — extract that), rationale ("because …"), plans and open
items ("will", "planned", "open item"), cross-references, and statements about
the compiler repository's own process. When unsure, extract it.

`python3 gen/m11.py --check` enforces the first two mechanically: every fence and
every table body row in your range must have a claim at its line, unless its table
is excluded.

## 3. The DSL (`gen/m11lib.py`; read its docstring)

```python
from m11lib import *

D = "TYPE"

claim("ty0127", D, 127, "`int8`", "row",
      "int8 holds -128 to 127; 127 + 1 traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_("""    int8:x = raw v8(127i8);
    int8:y = x + 1i8;
    if (y < 0i8) { exit 10i32; }
    exit 0i32;"""),
      wrong="wraps to -128 (exit 10) or exits 0")

claim("ty0131", D, 131, "is refused", "rule",
      "A literal that does not fit its suffix's type is refused.",
      expect="refuse", src=main_("""    int8:x = 300i8;
    exit 0i32;"""), wrong="accepted, truncated")

claim("ty0140", D, 140, "`List<T>` is compiler-known", "rule",
      "The AST node for List stores its element type in field b.",
      untestable="[internal] the AST's field layout is not observable from a program")

excluded(D, 1900, "a table of the decisions that retired `const`: history")
```

- **id** = the doc's prefix + the line as four digits + an optional letter for a
  second claim on the same line: `ty0127`, `ty0127b`, `ty0127c`. It is also the
  program's `mod:` name and file name. Prefixes: AST `as`, BUILD `bd`, BUILTIN
  `bi`, CONCURRENCY `cc`, CONTROL `ct`, IO `io`, LEXICAL `lx`, MACRO `mc`,
  MEMORY `me`, MODULE `md`, OP `op`, TRAITS `tr`, TYPE `ty`, VERIFICATION `vf`.
- **quote**: a verbatim substring of that line (keep it short and distinctive; the
  check fails when it is not on the line). Backticks and `|` are fine.
- **text**: the claim in one sentence, in your words, precise about the outcome.
- **expect** (written from the TEXT):
  - `run:0` — the program compiles and both legs exit 0. **Design every run
    program so that exit 0 means the reference's answer**, and exits 10–59 name
    the check that saw something else (one distinct code per check, and say in
    `wrong` what each means).
  - `trap:Name` — the program reaches `failsafe`'s arm for `Name` (IntOverflow,
    OutOfBounds, DivByZero, DivOverflow, TbbErr, ShiftRange, CastRange,
    Unreachable, HeapBadRequest, HeapOom, WildLeak, LimitViolated, …: the list is
    `TRAPS` in `gen/m11lib.py`). The session appends a `failsafe` naming all of
    them, so do not write one unless the claim is about `failsafe` itself (then
    write the whole program and pass `fs=False`).
  - `refuse:CODE` when the text names the code (`refuse:NITPICK-TYPE-054` or
    `refuse:TYPE-054`), else `refuse`. **A refusal program must be otherwise
    valid**: the claimed construct is the only reason it could be refused. Where
    the reference also states the permitted twin, extract that too, as its own
    claim with a run program.
  - `compile` — for an example whose text says it compiles but states no result
    you can observe: npkc 0 and both legs build.
  - `ir:REGEX` / `ir!:REGEX` — for a claim about what the compiler EMITS (a
    symbol, an intrinsic, an instruction): the program compiles and its `.ll`
    does / does not match the Python regex (MULTILINE).
  - `sh:0` with `sh="""..."""` — for a claim about a command line (a compiler
    flag, `npkg`): a bash script that exits 0 exactly when the claim holds. It
    runs in an empty scratch directory with `$NPKC` (the compiler), `$NPKG` (the
    package tool, `npkg`, built from HUNT2), `$NPKRT` (the runtime object) and
    `$LLVM_BIN` set, `$LLVM_BIN` first on `PATH`, 60 s timeout. Write any
    program it needs with a heredoc. Keep these few and simple.
  - `heap="*/*/0"` alongside `run:0` — for a claim about allocation: the run is
    under `NPK_HEAP_STATS=1`, and each leg's `heap: allocated= peak_live= count=`
    line must match (`*` is any number).
- **untestable** instead of `expect`, as `"[tag] reason"`, tags:
  `z3` (needs the verified build: `npkg verify` with the pinned z3, which this
  environment does not have), `tool` (needs a tool or a workflow the session
  cannot run cheaply: a package tree, the harness, the explorer, a JIT driver),
  `tree` (a claim about the compiler's source tree, generators, harness or
  documents, not about what it does with a program), `internal` (a compiler
  internal no program can observe: an AST field, a table's layout), `platform`
  (another architecture or OS, root, the network, 2^47 bytes of memory), `timing`
  (a schedule, a race, a duration), `unobservable` (no program can tell the
  claim's truth from its falsehood), `vague` (the sentence states no checkable
  outcome). Prefer a test: a claim about the verified build often has a plain
  build half (a contract is CHECKED in every build — a trap you can run); a
  claim about emission is an `ir:` test.

## 4. What makes a good claim program

- **It is a case the wrong implementation gets wrong.** If the reference says `a
  / b` truncates toward zero, test `-7 / 2` (a floor-dividing compiler gives -4),
  not `7 / 2`. Say in `wrong` what the wrong one answers.
- **Values meant to be computed at run time go through an identity helper** so the
  constant folder cannot decide them: `raw v32(x)` for int32, and `v8 v16 v64
  vi128 vu8 vu16 vu32 vu64 vf32 vf64 vc8 vb vt8 vt32` (declared for you when you
  call them). Where the reference speaks of constants, a module `fixed`
  initialiser is folded.
- **Keep it small.** One claim, one program, 5–30 lines. Use the reference's own
  spelling for the construct the claim is about, even where you suspect it is
  stale: a stale spelling refused is exactly a finding. Use the known-good
  spellings (§5) for everything around it.
- A code example: turn it into a program as literally as possible. Declare what it
  uses and leaves undeclared, wrap statements in `main_`, and check what the text
  says it computes. When an example cannot stand alone (a fragment of a larger
  program, pseudo-code, a grammar, shell output, IR), say which and why in
  `untestable`, or test the separable claims inside it.
- `stdin` is `/dev/null`, the environment is empty (`env -i`), there are no
  arguments, and the working directory is a scratch directory the program may
  write files into.

## 5. The language, as it compiles at HUNT2 (learn more from `m10/programs/`)

```
mod:name;                                   // added for you; the file name is the id
func:f = int32(int32:a, int64:b) { pass a; };            // `;` after the body
func:g = int32(int32:x) never fails { pass x; };         // call it `raw g(1i32)`
func:h = NIL() { pass NIL; };                             // every path leaves: pass/fail/exit/trap
error:E1;  func:k = int32() { fail E1; };                 // fallible: its call is a Result<int32>
Result<int32>:r = k();  if (r.is_error) { … }  int32:v = k() ?| 7i32;  int32:w = k() ?! E1;
int32:x = relay k();                                      // propagate, inside a fallible function
drop k();                                                 // discard a Result
discard(expr);                                            // parentheses; no `discard x;`
func:main = int32(cstring[]:_~argv) { …; exit 0i32; };   // main exits; only main/failsafe `exit`
int32:x = 5i32;  int64:y = 7i64;  uint8:z = 3u8;  flt64:f = 1.5f64;  bool:b = true;
string:s = "abc";  string:t = string_concat(s, "d");     // strings are move-only: no `string:u = s;`
if (a == b) { … } else { … }                              // `else if` is a CONTROL claim: never scaffolding
for (int64:i in 0i64...3i64) { … }                        // `...` exclusive, `..` inclusive
while (i < n) decreases n - i { i = i + 1i64; }           // a while states `decreases E` or `unbounded`
pick (x) { (1i32) { … }, (2i32) { … }, (*) { … } }        // arms separated by commas
struct:Pt = { int32:x; int32:y; };   Pt:p = Pt{ x: 1i32, y: 2i32 };   p.x = 3i32;
int32[4]:a = [1i32, 2i32, 3i32, 4i32];   a[0i64] = 9i32;  // index with int64
int32->:p = @x;  <-p = 5i32;                              // address-of and dereference
defer { … }                                               // no `;` after it
```

Pitfalls that cost M10 builds: reserved words that read like names (`pid tid fd
uid gid limit any as comptime derive move buffer raw assoc on is_err defaults
channel atomic thread joins error gives unit trit nit oflags prot mflags fmode
fails end in mod old result pure decreases unbounded sealed hidden use`); the
`mod:` name must equal the file name (the id); adjacent string literals do not
concatenate; `exit` only in `main`/`failsafe`; a `while` without `decreases` or
`unbounded` is TYPE-072; comparing `tbb` values with `<`/`>` is refused; a
binding declared without a value cannot have a field written directly (D-010).

## 6. When you are done

1. `python3 gen/m11.py --check --module <yours> --doc <DOC> --lines A-B` reports
   0 errors (for two references, run it once per reference).
2. Do not commit, and write nothing outside your module file.
3. Reply with: the counts (claims; examples, rows, rules; testable; untestable by
   tag), the M10 items you linked, and a short list of the places where the text
   was ambiguous or contradicted itself (with lines) — those are where a
   documentation finding may be.
