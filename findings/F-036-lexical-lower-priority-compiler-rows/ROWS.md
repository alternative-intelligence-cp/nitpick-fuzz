# F-036 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-036 a: four keywords (`acquire`, `any`, `trit`, `nit`) are accepted as a module-level function's name, and the function can never be called (PARSE-002 at the call): DEF-103's fix exempts them at every function site, for the method names it meant**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0054` | LEXICAL_REFERENCE.md:54 | `relaxed`, `acquire`, `release`, `acq_rel`, `seq_cst`: each is reserved, so a local and a function of that name are each refused. | `sh:0` | script 1 | same | same |
| `lx0114` | LEXICAL_REFERENCE.md:114 | `dyn`, `any`, `Result`, `Optional`: each is reserved, so a local and a function of that name are each refused. | `sh:0` | script 1 | same | same |
| `lx0121` | LEXICAL_REFERENCE.md:121 | `trit`, `tryte`, `nit`, `nyte`: each is reserved, so a local and a function of that name are each refused. | `sh:0` | script 1 | same | same |

**F-036 b: a decimal literal ending in an underscore (`10_i32`) is accepted, against `DecimalLiteral ::= [0-9] ([0-9_]* [0-9])?`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `lx0296b` | LEXICAL_REFERENCE.md:296 | A decimal literal ends with a digit: `10_i32` (a trailing underscore) is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
