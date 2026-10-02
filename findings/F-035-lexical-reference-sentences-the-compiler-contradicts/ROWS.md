# F-035 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-035: "`0u64 - 1u64` is the maximum" (LEXICAL:324) is TYPE-076, as the note at LEXICAL:328-331 says**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0324` | LEXICAL_REFERENCE.md:324 | `0u64 - 1u64` is uint64's maximum. | `run:0` | npkc 1 TYPE-076, - / - | same | same |

**F-035: `++` and `--` are listed as operator tokens; they are removed (D-174), PARSE-010**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0174` | LEXICAL_REFERENCE.md:174 | `++` and `--` are operator tokens: `x++; x--;` compiles. | `compile` | npkc 1 PARSE-010, - / - | same | same |

**F-035: `f128` is listed as a literal suffix, and `flt128` is a storage format with no literals (TYPE-030, D-143)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0315` | LEXICAL_REFERENCE.md:315 | The suffixes `f32`, `f64` and `f128` are float literals' types. | `compile` | npkc 1 TYPE-030, - / - | same | same |

**F-035: the LBIM note (LEXICAL:353-354) is dead (TYPE:449): `5i2048` is a literal, and there is no `parse_uint2048`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0353` | LEXICAL_REFERENCE.md:353 | `int2048` has no direct source literal: `5i2048` is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
| `lx0354` | LEXICAL_REFERENCE.md:354 | Such a value is instantiated by parsing: `parse_uint2048("1.5e308")` compiles. | `compile` | npkc 1 RESOLVE-002, - / - | same | same |

**F-035: the full-tier syscall is not spelled `sys_full`: no such builtin (RESOLVE-002); the syscall builtin is `sys`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0256` | LEXICAL_REFERENCE.md:256 | The full-tier syscall is spelled `sys_full`: `sys_full(39i64)` compiles. | `compile` | npkc 1 RESOLVE-002, - / - | same | same |
