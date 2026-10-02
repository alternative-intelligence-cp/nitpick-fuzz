# F-034 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-034 a: an extern method taking a byte payload (`int8[]`, or `uint8[]`; both in the v1 vocabulary) generates a stub the compiler refuses: TYPE-072 at `<bridge-1>:10:5`, a `while` stating no `decreases`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0270c` | MODULE_REFERENCE.md:270 | A sized byte payload is in the wire vocabulary: a method taking an `int8[]` compiles. | `sh:0` | script 1 | same | same |

**F-034 b: the single-name form over a logical path (`use network.connect;`, `use helpers.f;`, `use core.math.sq;`) is RESOLVE-002, "is a function, not a module", against MODULE:68, :111 and :119 and D-273 (2), which lists `use hidden.f;`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0068b` | MODULE_REFERENCE.md:68 | `use network.connect;` binds the one member bare. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `md0105` | MODULE_REFERENCE.md:105 | The block's six logical-path imports compile together (with `nested`, `core.math` and a file import binding `helpers` declared), and each bound name works. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `md0119` | MODULE_REFERENCE.md:119 | Every form of the file imports works through a logical path: `use core.math.sq;` (one name) binds `sq`. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-034 c: a constant cycle's diagnostic says each member "is initialised from itself"; it never names the members in the order they refer to each other (MODULE:183)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `md0183` | MODULE_REFERENCE.md:183 | The cycle's diagnostic names its members (`FIRST`, `SECOND`) on its first line, not "circular import". | `sh:0` | script 1 | same | same |
