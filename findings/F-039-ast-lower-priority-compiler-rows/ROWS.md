# F-039 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-039 a: a function with a `comptime` value parameter passes the checker and is EMIT-002 (a hole the compiler names)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0062` | AST_REFERENCE.md:62 | A generic parameter is a type or a compile-time value: `scale<comptime int32:K>` called `scale::<3i32>(2i32)` is 6. | `run:0` | npkc 1 EMIT-002, - / - | same | same |

**F-039 b: the backward pipe takes its function on the RIGHT, as `\|>` does: `dbl <\| x` is TYPE-007, and `x <\| dbl` computes dbl(x) (OP:378 says it passes to the LEFT function)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0301` | AST_REFERENCE.md:301 | `\|>` and `<\|` pipe a value into a function: `4 \|> dbl` is 8 and `dbl <\| 5` is 10. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-039 c: a `joins` deadline that is no constant expression is accepted (a call; a parameter's call, measured by hand)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0555` | AST_REFERENCE.md:555 | `joins` takes a constant expression only: a call as the deadline is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-039 d: an attribute the language does not have is accepted and ignored: the removed `#[lexical_drop]`, and `#[nosuch_attribute]` (measured by hand)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0583` | AST_REFERENCE.md:583 | `#[lexical_drop]` is removed: a struct carrying it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-039 e: an `opaque struct` is accepted at module level, against AST:43 and TRAITS:368 (extern-block item only, D-066 as narrowed by D-149); inside an `extern` block it is EXTERN-001, a tier reserved (D-190)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0043` | AST_REFERENCE.md:43 | An `opaque struct` is an extern-block item only: one at module level is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
