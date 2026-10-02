# F-042 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-042 a: an `opaque struct` is accepted at module level, against TRAITS:368 (as AST's F-039 e)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0368` | TRAITS_REFERENCE.md:368 | `opaque` is legal only inside an `extern` block: one at module level is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
