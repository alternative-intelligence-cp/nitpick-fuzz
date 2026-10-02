# F-034 — MODULE_REFERENCE: three places where the compiler departs from the reference safely: a byte payload's driver stub refused, a `use` form refused, a cycle's diagnostic (lower priority)

None of these is a wrong answer at run time or a memory fault. The compiler refuses a
program that the reference and the decisions permit, or names a cycle less than the
reference says. Each is a few claims and their programs, so they share a directory, as
F-027's rows do (PROGRESS.md S38, S54). The rows, with each claim's program and its
verdicts at HUNT2 `9126350`, the baseline `c3bdae2` and the newest `main` `93bcb66`, are in
[`ROWS.md`](ROWS.md). Every row gives the same result at all three.

**a. A byte payload's driver stub is refused by the compiler's own loop rule** (`md0270c`)
- The program is an `extern` block in HUNT2's form (the compiler's own
  `tests/backend/programs/extern_stub.npk`, with `lib/nbridge.npk` beside it), with one
  method `func:put = int64(Bridge->:b, int8[]:data, Duration:within);`.
- `int8[]` is in the v1 wire vocabulary, by the compiler's own EXTERN-001 message: "a
  driver method's parameters are `int32`, `int64`, `int8[]` or `uint8[]`".
- npkc exits 1 with `NITPICK-TYPE-072 <bridge-1>:10:5: a while/when states why it ends
  (D-304)`. The `while` is in the GENERATED stub, so the program's author cannot add the
  clause.
- The same block with `uint8[]` is the same TYPE-072 at HUNT2 and at `93bcb66`. This was
  measured by hand: `md0270c.sh` with `int8[]:data` replaced by `uint8[]:data`, run with
  `$NPKC` set to each compiler.
- The same block with no payload compiles: `md0250` and `md0259` agree.

  So no driver method can take a byte payload at any of the three compilers.

**b. The single-name form of a logical-path import is refused** (`md0068b`, `md0105`, `md0119`)
- `use network.connect;` (MODULE:68), `use helpers.f;` (the example at MODULE:105, line
  111) and `use core.math.sq;` are each RESOLVE-002: "`network.connect` is a function,
  not a module: a `use` path walks module symbols and names members only after its last
  `.` (D-273)".
- MODULE:119–120 says a logical path binds "in every form the file forms have". D-273 (2)
  lists `use hidden.f;` among those forms.
- The other forms agree: `use network.*;`, `use network.{connect, Point};`, `use core.math
  as cm;`, `use core.math.*;`, and the file form `use "./sqlib.npk".square;`.
- *Reasoned:* the refusal's own sentence ("names members only after its last `.`")
  describes the form it refuses.

**c. A constant cycle's diagnostic does not name the cycle** (`md0183`)
- `fixed int32:FIRST = SECOND + 1i32; fixed int32:SECOND = FIRST;` is refused
  (RESOLVE-006, as MODULE:182 says, `md0182c`).
- The two diagnostics say "`FIRST` is initialised from itself" and "`SECOND` is
  initialised from itself". MODULE:183 says "The diagnostic names the members in the order
  they refer to each other". Neither line names the other member, and neither is
  initialised from itself directly.
- A struct cycle across two files names its member too ("`SA` contains itself"), the same
  shape (`md0182`, which agrees, since its claim is the refusal).

**Observed in an agreeing claim, not a row.** `md0042`'s refusal is RESOLVE-012, as the
claim says. Its message names the header as "`mod:;`" and "an import of ``". The header
`mod:mod;` reaches the message with an empty name. *Reasoned:* `mod` is a keyword, so the
header's name never parses.

## Deduplication

- KNOWN_DEFECTS.md has none of the three.
- None is among F-027's rows (DEF-153), F-028's (DEF-154) or F-029 … F-032 (O-N35).
- The registry at `93bcb66` (`git show 93bcb66:meta/roadmap/OPEN_DECISIONS.md`) has no
  entry for any of them. Its only `use hidden.fetch;` line describes the state BEFORE
  D-273, when no spelling resolved.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and row a's `uint8[]` variant at
  HUNT2 and `93bcb66`.
- **Reasoned, not measured:** that each is the compiler's departure rather than the
  reference's. For row b, D-273 and the reference agree with each other. For row a, the
  compiler's own message admits the type.
