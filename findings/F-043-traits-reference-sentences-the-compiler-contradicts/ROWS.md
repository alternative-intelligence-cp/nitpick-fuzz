# F-043 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-043: "Lambdas without capture remain as function values": there is no lambda expression (PARSE-002; AST:476 says closures are removed and function pointers are named functions)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0764` | TRAITS_REFERENCE.md:764 | Lambdas without capture remain as function values: one bound to a function-typed local compiles. | `compile` | npkc 1 PARSE-001,PARSE-002, - / - | same | same |

**F-043: `assoc:Error = string;` names the compiler's own `Error` (D-179, D-239; RESOLVE-001)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0109` | TRAITS_REFERENCE.md:109 | An associated type may carry a default (`assoc:Error = string;`), inherited by an impl that omits it. | `compile` | npkc 1 RESOLVE-001, - / - | same | same |

**F-043: `extract_value` passes a lent `T` out (TYPE-047, D-065, D-264); it compiled at the baseline**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0404` | TRAITS_REFERENCE.md:404 | Container<T> and `extract_value<T>`: extracting from a `Container<int32>` gives its value. | `run:0` | npkc 1 TYPE-047, - / - | npkc 0, 0 / 0 | same |

**F-043: `item.render();` as a bare statement discards a `Result` (TYPE-039)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0419` | TRAITS_REFERENCE.md:419 | Bounds with `&`: `process<T: Renderable & Serializable>` calling `item.render();` compiles. | `compile` | npkc 1 TYPE-039, - / - | same | same |

**F-043: `l.push(v)`: the prelude's `List<T>` has no `push` method (TYPE-019)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0149` | TRAITS_REFERENCE.md:149 | An inherent family method may take its receiver by pointer: `l.push(v)` beside `list_push(@l, v)`. | `compile` | npkc 1 TYPE-019, - / - | same | same |

**F-043: struct fields are not private by default: a plain field is read outside its module (D-313's `sealed`/`hidden` are the field qualifiers), and `pub` on a field does not parse**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0364` | TRAITS_REFERENCE.md:364 | A struct field is private by default: a field without `pub` is not read outside its module. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-043: the Iterator example declares a trait the prelude owns (`Iterator`, RESOLVE-001)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0097` | TRAITS_REFERENCE.md:97 | Iterator with `assoc:Item`: the impl binds `Item = int32`, and `next` returns `self.current`. | `run:0` | npkc 1 RESOLVE-001, - / - | same | same |

**F-043: the Serializable example passes `result` from a body: `result` is the ensures-only keyword since D-221 (TYPE-060)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0021` | TRAITS_REFERENCE.md:21 | The Serializable example (a trait with `to_bytes = buffer(Self:self)`, an impl passing `result`) compiles. | `compile` | npkc 1 TYPE-060, - / - | same | same |

**F-043: the arena example calls `alloc(my_node)`: an arena's `alloc` takes no arguments (TYPE-007)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0602` | TRAITS_REFERENCE.md:602 | An `arena<Node<T>>` field in a generic struct, with chained access: `hdr.node_arena.alloc(my_node)`. | `compile` | npkc 1 TYPE-007, - / - | same | same |

**F-043: the inherent-impl example casts with `flt64(…)`, a call form the language has no (PARSE-002; casts are `=>`/`=>!`)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0124` | TRAITS_REFERENCE.md:124 | An inherent impl: Point's `magnitude` (flt64_sqrt over a call-cast `flt64(…)`) compiles. | `compile` | npkc 1 PARSE-002, - / - | same | same |

**F-043: the opaque-copy example names `Handle` (a builtin type keyword) and a `handle_create` that does not exist; OPAQUE-COPY-001 is never reached**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0384` | TRAITS_REFERENCE.md:384 | An opaque value is not copied: `Handle:h2 = h;` is refused, NITPICK-OPAQUE-COPY-001. | `sh:0` | script 1 | same | same |

**F-043: the storage_driver example is EXTERN-001: the `opaque` tier is reserved (D-190) and its methods take no `Bridge->`/`Duration`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0373` | TRAITS_REFERENCE.md:373 | The storage_driver extern block (an opaque struct, db_open and db_rows) compiles. | `compile` | npkc 1 EXTERN-001, - / - | same | same |

**F-043: the value-parameter example declares `struct:Mutex`, a builtin name (PARSE-001); it compiled at the baseline**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `tr0435` | TRAITS_REFERENCE.md:435 | `struct:Mutex<T, comptime int32:LEVEL> = { … };` and `Mutex<Config, 2>:cfg_lock;` are the value parameter's spelling: they compile. | `compile` | npkc 1 PARSE-001, - / - | npkc 0, 0 / 0 | same |
