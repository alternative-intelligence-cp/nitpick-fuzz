# F-033 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-033: `pub const int32:MAX = 100i32;` does not parse (PARSE-001): a module constant is `fixed`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0209` | MODULE_REFERENCE.md:209 | The four `pub` declarations (a function, a struct, a `pub const`, a `pub mod`) compile in a file, and an importer uses each. | `run:0` | npkc 1 PARSE-001, - / - | same | same |
| `md0212` | MODULE_REFERENCE.md:212 | `pub const int32:MAX = 100i32;` declares a public module constant: `MAX` is 100. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-033: the `cuda_driver` example is EXTERN-001: its `opaque struct` tier "is reserved for the LOAD_MODULE work and does not lower yet (D-190)", and its methods take no `Bridge->` first and no `Duration` last**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0241` | MODULE_REFERENCE.md:241 | The `cuda_driver` block (an opaque struct and two methods) is valid syntax: the program compiles. | `compile` | npkc 1 EXTERN-001, - / - | same | same |

**F-033: the example's `raw some_query(name)` and `_! some_query(name)` are TYPE-042: `raw`, which `_!` spells too, needs a `never fails` callee (D-163), and a driver method never is one (MODULE:263-266, EXTERN-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0289` | MODULE_REFERENCE.md:289 | A driver method's call is read with `raw` or with `_!`; both forms compile and give the value. | `run:0` | npkc 1 TYPE-042, - / - | same | same |

**F-033: the wire vocabulary is v1's (D-190): a method's parameters are `int32`, `int64`, `int8[]` or `uint8[]`; a POD struct, an `int16` and a typed handle are each EXTERN-001**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0270` | MODULE_REFERENCE.md:270 | A POD struct of fixed-width scalars is in the wire vocabulary: a method taking one compiles. | `sh:0` | script 1 | same | same |
| `md0270b` | MODULE_REFERENCE.md:270 | Every fixed-width scalar is in the wire vocabulary: a method taking an `int16` compiles. | `sh:0` | script 1 | same | same |
| `md0270d` | MODULE_REFERENCE.md:270 | A typed handle is in the wire vocabulary: a method taking the block's `opaque struct` compiles. | `sh:0` | script 1 | same | same |
