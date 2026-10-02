# F-030 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-030: #wild_ptr is accepted outside wild context, against MEMORY:133 (D-019); D-315 struck the like rule from #wild_slice**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0133` | MEMORY_REFERENCE.md:133 | #wild_ptr is legal only in wild context: bound to a plain pointer, it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-030: #wild_ptr's type argument is the pointee: the example's `#wild_ptr<int8->>(addr)` is `int8->->` (TYPE-007)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0135` | MEMORY_REFERENCE.md:135 | `wild int8->:page = #wild_ptr<int8->>(addr);` builds a wild pointer from an address. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-030: `nodrop` qualifies a wild binding (DECISIONS: "nodrop requires wild or wildx"); `= nodrop alloc(...)` does not parse**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0173` | MEMORY_REFERENCE.md:173 | `wild int8->:manual_buf = nodrop alloc(16i64);` compiles (freed here with dalloc). | `run:0` | npkc 1 PARSE-001,PARSE-002, - / - | same | same |

**F-030: an un-destroyed arena<T> is not a leak the exit check names: its storage is managed since D-183 (1.2.5c; the runtime's npk_arena_make says so)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0397` | MEMORY_REFERENCE.md:397 | An un-destroyed arena is a wild-role leak the exit check names: WildLeak at `exit 0`. | `run:96` | npkc 0, 0 / 0 | same | same |

**F-030: the arena example and its note use a bare `?` as the fallback; it is `?\|` since D-175 (PARSE-011)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0381` | MEMORY_REFERENCE.md:381 | The example compiles and runs: put 41, `get(h) ? 0i64` reads it, then free and destroy. | `run:0` | npkc 1 PARSE-011, - / - | same | same |
| `me0399` | MEMORY_REFERENCE.md:399 | `?` takes a fallback value: a stale get with `? 0i64` yields 0. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-030: the move example uses malloc/free (§3:281: no aliases), a binding named `buffer` (a reserved word) and the code NITPICK-019; it does not compile**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0183` | MEMORY_REFERENCE.md:183 | The example: `free(buffer)` after `move(buffer)` is refused as NITPICK-019 (use after move). | `refuse:NITPICK-019` | npkc 1 PARSE-002, - / - | same | same |

**F-030: wildx_alloc's result is `int8->`: the example's `wildx uint8->:code = wildx_alloc(4096i64);` is TYPE-007 (VERIFICATION's own programs cast it `=>! wildx uint8->`)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `me0126` | MEMORY_REFERENCE.md:126 | `wildx uint8->:code = wildx_alloc(4096i64);` allocates an executable page (freed here). | `compile` | npkc 1 TYPE-007, - / - | same | same |
