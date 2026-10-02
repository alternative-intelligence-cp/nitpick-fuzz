# F-035 — LEXICAL_REFERENCE: six claims the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over LEXICAL_REFERENCE (all 410 lines) at HUNT2: 184 claims, 181 tested, 170
agree, 11 disagree. The 11:
- six documentation rows (below);
- four lower-priority compiler rows, [F-036](../F-036-lexical-lower-priority-compiler-rows/);
- one known: DEF-131 (F-015), `<=>` refused by the emitter (`lx0178`). It compiles and runs
  at `93bcb66`.

The rows, with each claim's program and its verdicts at HUNT2, the baseline and the newest
`main` `93bcb66`, are in [`ROWS.md`](ROWS.md). All six give the same result at all three.

- **Operators and builtins the language no longer has.**
  - `"++" | "--"` (LEXICAL:174) are listed among the operator tokens. `x++;` is
    PARSE-010: "`++` / `--` are removed (D-174): write `x += 1`".
  - "the full-tier syscall is spelled **`sys_full`**" (LEXICAL:256). No builtin of that
    name exists (RESOLVE-002). The syscall builtin is `sys` (BUILTIN's claims use it), and
    BUILTIN_REFERENCE never names `sys_full`.
- **A suffix with no literal.** `"f32" | "f64" | "f128"` (LEXICAL:315) lists `f128` as a
  literal suffix. `flt128:c = 1.5f128;` is TYPE-030: "`flt128` is a storage format (D-143):
  it holds and moves values but has no literals, arithmetic, or comparison". The other
  suffix lines all compile: `u8` … `u4096`, `i8` … `i4096`, the `tbb`, `tfp`, `dim256` and
  `char` suffixes.
- **Sentences that a later sentence of the same page withdrew.**
  - "`0u64 - 1u64` is the maximum" (LEXICAL:324) is TYPE-076. The italic note at
    LEXICAL:328–331 says so ("from 1.5.8b step 2 the spelling is refused"), and its claim
    (`lx0330`) agrees. The parenthesis at 324 was left standing.
  - The LBIM note (LEXICAL:353–354) says `int2048` and `int4096` "have no direct source
    literal" and are "instantiated by parsing, e.g. `parse_uint2048("1.5e308")`".
    - `5i2048` compiles, as LEXICAL:313's suffix list says (its claim `lx0313` agrees).
    - There is no `parse_uint2048` (RESOLVE-002).
    - TYPE_REFERENCE:449 calls the LBIM section "the dead reading".

**Agreements worth naming.**
- **The keyword productions** (44 claims, one per source line; S63). Every word on 40 of
  the lines is refused as a local's name and as a function's name. The four exceptions are
  F-036 a. The corrections table's removals (`gc`, `ok`, the `a*` collection words, `Type`,
  `stream` … `log`, `const`, `binary`) and D-135's seven library type names are all free
  names.
- **The literal rules.** All of these hold as stated:
  - every base by its suffix;
  - the leading-digit rule (`0FFhex`, `0Tt`, `0an`, `0ban`, `0tt`);
  - balanced ternary and nonary, each digit and suffix;
  - the 64-bit envelope (LEX-004) and the type fit (TYPE-031);
  - `0b4bni8` as −128;
  - `~0u64`, `(1u64 << 63u64) | k` and `0u64 -% 1u64`;
  - `0xFF` as LEX-003, and `0o17` and `0t1T` refused.
- **Strings.**
  - Every escape gives its byte.
  - A raw string processes none.
  - A block string keeps newlines and indentation, and holds `"` and `""` as body text
    (DEF-98 is fixed at HUNT2).
  - Template literals interpolate.
- **Operators.**
  - The wrapping family `+% -% *%` and its compound forms wrap, and plain `+` traps.
  - `a + %b` is no program.
  - `..` is inclusive and `...` exclusive, and `..*` collects what `..^` spreads.
  - `>>` closes a nested generic and shifts elsewhere, and the turbofish is required in
    an expression.
  - `!!` and `name!()` are refused, and `!!!` reaches failsafe.
- **The kernel identifiers and flag families.** They compare but do not compute. A flag
  family takes `|` and `=> int32`, refuses arithmetic, order and conversion to another
  family, and comes in by `=>!` only.
- **The contract clauses.** A function's and a loop's `decreases` trap
  DecreasesViolated. `while` states exactly one of `decreases` and `unbounded`
  (TYPE-072). `pure` is checked in the body and at a contract's call.
- **`sealed` and `hidden` fields** (TYPE-079, TYPE-080).

**Found in run 1, not findings.** These were the programs' own mistakes, fixed by
`refix()`, with every expectation unchanged:
- A `decreases` measure may not call the identity helper, since the measure is a contract
  position (TYPE-060).
- A check passed into a %-formatted body kept a `%%`.
- A generic identity cannot pass out its lent parameter (TYPE-047). `lx0239` had agreed
  through its own parse error, which still stands.

## Deduplication

None of these sentences is among F-028's rows (DEF-154), which cover no LEXICAL line.
None is among F-029 … F-034. DEF-98 (block strings) and DEF-103 (keyword names) are
KNOWN_DEFECTS.md's; this finding's rows are neither. The registry at `93bcb66` has no
entry for any of the six.

## Measured, and inferred

- **Measured:** each row's result at three compilers.
- **Reasoned, not measured:** that the compiler is the right side in each. For `++`/`--`
  and LBIM, the compiler's own decisions (D-174) and TYPE_REFERENCE:449 say so.
