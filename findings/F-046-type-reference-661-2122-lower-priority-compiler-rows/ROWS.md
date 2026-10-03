# F-046 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-046 a: an assignment to a frac's `.num` passes the checker and is EMIT-002, where TYPE:1649 makes the members read-only views**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1649` | TYPE_REFERENCE.md:1649 | The members are not places: assigning `.num` is refused. | `refuse` | npkc 1 EMIT-002, - / - | same | same |

**F-046 b: a `fixed` parameter is reassigned, against TYPE:1873 and :1876 (ASSIGN-002 in every position)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1873` | TYPE_REFERENCE.md:1873 | A fixed parameter may not be reassigned: ASSIGN-002. | `refuse:NITPICK-ASSIGN-002` | npkc 0, 0 / 0 | same | same |

**F-046 c: the backward pipe takes its function on the right, against TYPE:2084 (as AST's F-039 b)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2084` | TYPE_REFERENCE.md:2084 | `f <\| v` is `f(v)`. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
