# F-031 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-031: line 171's "a fallback (`?`)" leaves the ERR state: a bare `?` is struck (line 73, D-175), and `?\|` takes a Result only (line 257); ERR leaves by is_err or a pick's ERR: arm**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `op0171` | OP_REFERENCE.md:171 | A fallback leaves the ERR state: an ERR tbb with a fallback yields the fallback. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-031: the pipe examples `val \|> func()` and `func() <\| val` are refused: a pipe's other side is the function itself, not a call (TYPE-007)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `op0377` | OP_REFERENCE.md:377 | `val \|> func()` passes val as func's first argument: 10 \|> minus(3) is 7. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
| `op0378` | OP_REFERENCE.md:378 | `func() <\| val` evaluates val and passes it to func. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-031: the ternary example `is x > 0 : 1 : -1` needs its condition parenthesised (PARSE-001; TYPE:2101's `is (cond) : then : else`)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `op0374` | OP_REFERENCE.md:374 | `is cond : then : else` branches: `is x > 0 : 1 : -1` with x = 5 is 1. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-031: there is no `**` operator (OP:88, "Standard Library expansion"): `2 ** 8` does not parse**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `op0088` | OP_REFERENCE.md:88 | `**` is exponentiation: 2 ** 8 is 256. | `run:0` | npkc 1 PARSE-002, - / - | same | same |
