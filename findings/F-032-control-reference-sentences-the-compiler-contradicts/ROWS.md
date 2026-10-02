# F-032 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-032: `ok()` is not "the taint-clearing builtin" (CONTROL:347): it is removed (D-097, OP:172)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ct0347` | CONTROL_REFERENCE.md:347 | `ok()` is the taint-clearing builtin: `ok(x)` compiles. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-032: the fallthrough example calls `println`, which no prelude declares (RESOLVE-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ct0034` | CONTROL_REFERENCE.md:34 | The fallthrough example: `fall two;` in arm one continues into arm two. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-032: the guards-and-macros example's pattern `MyMacro!(a, b) where (a > b)` is removed (PARSE-001; MACRO:374, and macro invocation is `#name(args)`)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ct0080` | CONTROL_REFERENCE.md:80 | pick matches a macro invocation pattern with a where guard: `MyMacro!(a, b) where (a > b)`. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-032: §4.2 names NITPICK-IF-002, -IF-001 and -WHEN-001; the compiler refuses each program with a PARSE code (OP:65: IF-002 "describes a diagnostic for a program that cannot be written")**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ct0314` | CONTROL_REFERENCE.md:314 | An assignment inside an if condition is rejected as NITPICK-IF-002. | `refuse:IF-002` | npkc 1 PARSE-001,PARSE-002, - / - | same | same |
| `ct0317` | CONTROL_REFERENCE.md:317 | An else without an immediately preceding if is NITPICK-IF-001. | `refuse:IF-001` | npkc 1 PARSE-002, - / - | same | same |
| `ct0319` | CONTROL_REFERENCE.md:319 | An orphaned `then` without a preceding when is NITPICK-WHEN-001. | `refuse:WHEN-001` | npkc 1 PARSE-002, - / - | same | same |
