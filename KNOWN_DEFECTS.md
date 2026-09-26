# Known defects — the recall set, and the list to deduplicate against

Every verdict in the `c3bdae2` columns was **measured on 2026-09-25** by the
library workbench's orchestrator. It used the recipe in `PLAN.md`, at the
workbench's pinned compiler built from `c3bdae2`. The "once fixed" columns are
what the compiler's maintainers stated for their fix, measured there. Here they
are expectations until M1.3 measures them.

Identify a fix at HUNT by its commit:
`git merge-base --is-ancestor <commit> <HUNT>`. Where no commit is given, the
fix had not landed on `main` when this was written; find it by its subject in
`git log origin/main`, for example `1.6.0 step 3g`.

## DEF-99 — a move out of `fixed` storage compiles, and faults

`fixed` storage is an LLVM `constant` global, and moving out of it stores the
vacancy into that constant.

- **Fixed at** `6fb85d3` (1.6.0 step 3f), as a refusal: `NITPICK-TYPE-084`.
- **Workbench id** O-N20.

| `known/def99_fixed_move/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed |
|---|---|---|---|---|
| `case1_element_move` — `move(NAMES[1i64])` | 0 | **107** | **95** | refused `TYPE-084` |
| `case2_element_pass` — `pass NAMES[i]`, an implicit move | 0 | **107** | **95** | refused `TYPE-084` |
| `case3_scalar_move` — `move(V)` of a `fixed string` | 0 | **95** | **95** | refused `TYPE-084` |
| `case4_clone_control` — the same reads by `.clone()` | 0 | 0 | 0 | 0 / 0 |

## DEF-102 — a write through a LENT parameter frees the caller's value

An ordinary by-value parameter is a loan. Assigning an owning field of it drops
the caller's value.

- **Fixed in** 1.6.0 step 3g, as "a loan is read-only when it owns":
  `NITPICK-TYPE-085`. This covers every write path — assignment into or to the
  place, `@`, `$$i`/`$$m`, pointer-receiver calls — except calls through a
  `dyn` receiver.
- **Workbench id** O-N21.

| `known/def102_lent_param/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed |
|---|---|---|---|---|
| `lent_field` — callee writes `b.s = …`; caller reads `b.s` | 0 | **70** | **70** | refused `TYPE-085` |
| `lent_field_nodread` — the same, returning normally | 0 | **95** | **95** | refused `TYPE-085` |
| `ctl_local` — the same write on a local | 0 | 22 (the new value) | 22 | 22 / 22 |
| `ctl_whole_lent_string` — `s = …` to a lent `string` | 0 | 21 (caller intact) | 21 | refused `TYPE-085`: the rule covers a whole-binding assignment |
| `ctl_move_param` — the write on a `move Box:b` | 0 | 0 | 0 | 0 / 0 |

## DEF-104 — a lent `T` in a generic body escapes the loan rules

A generic function can hand back its lent `T` parameter as a second owner.

- **Fixed in** 1.6.0 step 3g, alongside DEF-102. A pass-out is refused with
  `NITPICK-TYPE-047`, and `@x` of a lent `T` with `NITPICK-TYPE-085`.
- **Workbench id** O-N22.

| `known/def104_generic_lent/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed |
|---|---|---|---|---|
| `gen_id` — `func:id<T> = T(T:x) { pass x; }` at `string` | 0 | **95** | **95** | refused `TYPE-047` |
| `gen_id_read` — the same, the result passed out and read | 0 | **70** | **70** | refused `TYPE-047` |
| `ctl_concrete` — the same function written for `string` | **1**, `TYPE-047` | — | — | 1, `TYPE-047` |

## DEF-105 — an imported `fixed` binding's type resolves in the importer's scope

- **Fixed in** 1.6.0 step 3h.
- **Workbench id** O-N23.
- `rows.npk` declares `pub struct:Row = { int64:x; int64:y; }` and
  `pub fixed Row[2]:ROWS`. It is a support module, never a root.
- **Run the cases from their own directory.**

| `known/def105_import_scope/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed |
|---|---|---|---|---|
| `case1_table_only` — `ROWS` imported alone | **1**, `TYPE-001` at `rows.npk` | — | — | compiles, runs 0 |
| `case2_same_name` — beside the importer's own `Row { y; x; }` | 0 | **10** (wrong field) | **10** | 0 / 0 |
| `case3_wider_same_name` — beside a 3-field `Row` (24-byte stride over 16-byte rows) | 0 | **10** | **10** | 0 / 0 |
| `case4_type_imported` — `Row` imported by name as well | 0 | 0 | 0 | 0 / 0 |
| `case5_type_imported_same_name` — `Row` imported by name, and a same-named struct | **1**, `RESOLVE-001` | — | — | 1, `RESOLVE-001` |
| `case6_scalar_same_name` — a `fixed Row` scalar beside a same-named struct | 0 | **10** | **10** | 0 / 0 |
| `case7_function_only` — a function returning `Row`, imported alone | 0 | 0 | 0 | 0 / 0 |

## DEF-106 — a write INTO a `fixed` binding's element or field compiles, and stores into the constant

`fixed` storage is an LLVM `constant` global, as in DEF-99. The whole binding's
assignment is refused (`NITPICK-ASSIGN-002`) and so is its address
(`NITPICK-TYPE-071`), but an assignment to one of its parts — `FA[i] = …;`,
`FX.s = …;`, `FX[0i64] = …;` — compiles and stores into the constant.

- **Fixed in** 1.6.0 step 4b, as a refusal: `NITPICK-TYPE-086`. No commit is
  given: find it by its subject, `1.6.0 step 4b`.
- **Workbench id** O-N24.
- **The workbench's verdicts:** where the written part owns (a `string`, a
  `Box`), the program exits **95** on both legs. Where it is a plain value, it
  exits **107** at -O0, and at -O2 the write is silently dropped.
- Added on 2026-09-26, after M4, on the author's instruction. There is no
  `known/` case for it. The grid's own cells below are its instances; their
  verdicts were measured by this repository's M3 run at `c3bdae2`, not by the
  workbench. At a HUNT without step 4b they are deduplicated here, not
  re-investigated.

| grid cells (`ra`, `dx`) | the write | npkc at `c3bdae2` | -O0 | -O2 | once fixed |
|---|---|---|---|---|---|
| `c0039`, `c0040` | `FA[i] = …` into `fixed string[2]:FA` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0185`, `c0186` | `FX.s = …` into `fixed Box:FX` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0203`, `c0204` | `FA[i].s = …` into `fixed Box[2]:FA` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0205`, `c0206` | `FA[i] = …` into `fixed Box[2]:FA` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0645`, `c0646` | `FX[0i64] = …` into `fixed string[2]:FX` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0753`, `c0754` | `FX[0i64] = …` into `fixed Box[2]:FX` | 0 | **95** | **95** | refused `TYPE-086` |
| `c0151`, `c0152` | the imported twin of `c0039`: `TBL[i] = …` (`imported_fixed_typed`, `str`) | 0 | **95** | **95** | refused `TYPE-086` |
| `c0329`–`c0332` | the imported twins of `c0203`–`c0206` (`imported_fixed_typed`, `box`) | 0 | **95** | **95** | refused `TYPE-086` |
| `c0353`–`c0356` | the same, beside a same-named, same-layout `Box` (`imported_fixed_same`) | 0 | **95** | **95** | refused `TYPE-086` |
| `c0371`, `c0372` | `TBL[i].s = …` beside a wider same-named `Box` (`imported_fixed_wider`): DEF-106 reached through DEF-105's wrong stride | 0 | **95** | **107** (`ra`), **0** (`dx`) | *inferred, not stated:* refused `TYPE-086` once DEF-105's fix resolves the row to the table's own `Box` |

## Other known defects, for deduplication only (not in `known/`)

- **DEF-95** — a literal-step `till`/`loop` demanded a spurious `(BadStep)` arm.
  Fixed at `dfbaf1a`.
- **DEF-96** — `main` must be exactly `int32(cstring[]:argv)` (`TYPE-083`).
  Checked from `d156c4f`.
- **DEF-97** — a generic struct instance used only inside a generic function
  had its type definition emitted after its first use. `npkc` exited 0 and
  `llc` refused with *"Cannot allocate unsized type"*. Fixed at `f758995`.
- **DEF-98** — a block string closed at the first `""` instead of `"""`
  (`PARSE-003`). Fixed at `395308f`.
- **DEF-100, DEF-101** — documentation defects in the compiler's references.
- **DEF-103** — a keyword accepted as a declared function or type name, and
  then uncallable. Refused `PARSE-001` from 1.6.0 step 3g.
- **DEF-23 / O-N19** — `TYPE-046` not asked of an unsubstituted `T`. Fixed by
  the compiler's D-264 before `c3bdae2`: a generic copy of an owning element is
  refused there. The grid should see it refused, which makes it a control.
- **Keywords that read like names:** `pid`, `tid`, `fd`, `uid`, `gid`,
  `decreases`, `unbounded`, `sealed`, `hidden`. A binding or module named after
  one is refused at its declaration. That is not a defect.
