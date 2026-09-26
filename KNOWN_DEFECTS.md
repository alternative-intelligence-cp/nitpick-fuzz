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
- Added on 2026-09-26, after M4, on the author's instruction. Its `known/`
  case (below) was added at M9's merge; the grid's own cells are its instances too; their
  verdicts were measured by this repository's M3 run at `c3bdae2`, not by the
  workbench. At a HUNT without step 4b they are deduplicated here, not
  re-investigated.

| `known/def106_fixed_part/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed (at `c970483`) |
|---|---|---|---|---|
| `case1_owning_elem` — `FA[1i64] = "gamma"` into `fixed string[2]:FA` | 0 | **95** | **95** | refused `TYPE-086` |
| `case2_plain_elem` — `FI[1i64] = 7i64` into `fixed int64[2]:FI`, then read | 0 | **107** | **11** (the write dropped) | refused `TYPE-086` |
| `ctl_local_elem` — the same write into a local array | 0 | 0 | 0 | 0 / 0 |

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

## DEF-107 — a view's root can be written while the view is live

A view (`string_bytes`, `string_from_bytes`, a range view) has an ESCAPE rule
and no freeze. Its root can be reassigned, cleared or grown while the view is
still used, and the view then reads rewritten or freed memory. The compiler
seat's six-line reproduction, with no `wild` and no `=>!`:
`string:d = …; string:s = string_from_bytes(d.ptr, 5i64); d = …;`. `s` reads
the poison (exit 12 in its encoding).
- **Fixed in** 1.6.1 step 0, as a refusal: `NITPICK-BORROW-015` — a view's
  root is frozen for the view's lexical lifetime (the author's D-325). Find it
  by its subject; HUNT2 `9126350` carries it. **M9's F-004 is a gap in that
  fix** (`findings/F-004-view-root-freed-through-callee/`): a callee that moves
  the value out through `@x` or `$$i x` still frees the root.
- **Deduplicate** any view-outlives-its-root cell against this.
- **Workbench id** O-N25.

## DEF-108 — a function that falls off its end returns a zero value

`func:f = int64() never fails { };` compiles and returns 0. A missing path
returns 0 on the other path, a `string` returns empty, a `bool` false, and
**a fallible function returns a success carrying 0**. `main` falling off its
end exits 0.
- **Fixed in** 1.6.0 step 5c, as a refusal: `NITPICK-FLOW-001`, by the
  author's rule: every path of every function, `NIL` functions included, ends
  in `pass`, `fail`, `exit` or a trap. Find it by its subject; HUNT2 carries it.
- **Once a HUNT compiler carries it, every generated program must leave
  explicitly** (`pass NIL;` in every `NIL` function), or its cells are refused
  for the wrong reason.
- **Workbench id** O-N26.

| `known/def108_fall_off/` | npkc at `c3bdae2` | -O0 | -O2 | once fixed (at `c970483`) |
|---|---|---|---|---|
| `case1_empty_body` — `func:f = int64() never fails { };`, read against 5 | 0 | **10** (it read 0) | **10** | refused `FLOW-001` |
| `case2_fallible_missing_path` — `g(0)` falls off a fallible function | 0 | **12** (a success) | **12** | refused `FLOW-001` |
| `ctl_explicit` — the same function leaving on every path | 0 | 0 | 0 | 0 / 0 |

M10.3's other two shapes — a missing path in a function that cannot fail, and
`main` without `exit` — have no `known/` case yet; M10.3 needs its own programs
for them.

## Closed as faces of known defects (measured at 3g by the compiler seat)

- **F-001** (this repository's `findings/F-001-for-binding-write/`) — a write
  through a `for` binding over owning elements. This is DEF-102's for-binding
  face, refused `NITPICK-TYPE-085` at 1.6.0 step 3g.
- **F-002** (`findings/F-002-generic-move-of-loan/`) — `move(x)` of a lent `T`
  in a generic body. This is DEF-104's move face, refused `NITPICK-TYPE-047`
  at 3g.
- **Resolved:** F-002's control `ctl_gen_move_param` was once reported as exit 2
  at 3g. That was a stale cached binary in the compiler seat's batch loop. Run one at
  a time, it exits **21 on both legs under 3g** (the amended tree `5bdae98`). Any HUNT
  carrying 3g must still give 21.
- The compiler's chain was re-based after 3g's first harness. The planned shas are 3g
  `5bdae98`, 3h `c1a4a05`, step 3 `0da2be7`, step 4 `996784e`, 4b `f87d2df` (DEF-106),
  5 `4e467bc`, 5b `77314e9`, then 5c (DEF-108, `FLOW-001`). **Identify each by its
  commit SUBJECT, not by a sha**, since a chain can be re-based again.

## M9's findings, registered by the compiler seat — deduplicate against these

Registered on 2026-09-26 in the compiler's OPEN_DECISIONS §4, each citing this
repository's `findings/` directory and `main` `88e6355` as its evidence. **All
nine are fixed in the compiler's subcycle 1.6.1d, which lands after 1.6.1c** —
so none is fixed in HUNT2 `9126350`, nor in `9f6f370`. Find each fix by its
subject.

- **DEF-118** — F-003: a consuming `pick`'s binding escapes the move rules (a
  read after its move, a second move).
- **DEF-119** — F-004: a move out through a pointer while a view of the root is
  live (the freeze records a write, not a move out).
- **DEF-120** — F-005: `(<-p) = v` never drops the old value.
- **DEF-121** — F-006: a consuming `pick`'s binding is never dropped.
- **DEF-122** — F-007: `to_cstring`'s buffer is never freed.
- **DEF-123** — F-008: a write through a `$$i` claim's holder is not refused.
- **DEF-124** — F-009: a re-initialised `move` parameter cannot be read.
- **DEF-125** — F-010: the lent-`dyn` swap refused `BORROW-002` since 1.6.1
  step 0.
- **DEF-126** — M8's observation: a `TYPE-007` message names two same-named
  types by one word (the workbench's O-N29). The refusal is right.

## M10's findings, and one of the compiler seat's own — deduplicate against these

Registered on 2026-09-26 by the compiler seat, each citing this repository's
`findings/` and its M10 verdicts; **all are fixed in the compiler's subcycle
1.6.1d** (its step 1: DEF-127 and DEF-134; step 2: DEF-128 … DEF-130; step 4:
DEF-131 … DEF-133), so HUNT2 `9126350` and `9f6f370` still carry them.

- **DEF-127** — F-011: a `for` binding outlives its loop in the emitter; an
  outer binding of the same name reads the loop's slot, and past it.
- **DEF-128** — F-012: a `for` over a range runs zero times at its type's edges.
- **DEF-129** — F-013: `loop` and `till` widen an unsigned bound by its sign.
- **DEF-130** — F-014: `till` with a negative limit counts down.
- **DEF-131** — F-015: `<=>` refused by the emitter (`EMIT-002`).
- **DEF-132** — F-016: a `pick` range pattern with a negative bound is `EMIT-002`.
- **DEF-133** — F-017: seven reference sentences the compiler contradicts.
- **DEF-134** — the compiler seat's own: a by-value receiver method called on
  a POINTER (`q.peek()` with `Box->:q`, `peek = int64(Box:self)`) reads the
  pointer's bits as the struct — a silent wrong answer at every pin.

## M11's findings, registered by the compiler seat — deduplicate against these

Registered on 2026-09-26, each citing this repository's `findings/` and `main` `3d7d924`; **fixed in the compiler's
subcycle 1.6.1e**, planned after 1.6.1d step 3 — so HUNT2, `9f6f370` and `1b4f0c6` still carry them. A resumed M11
must not report these again.

- **DEF-144** — F-018: a macro's free name, alone or as a comparison's operand, reads the call site's local.
- **DEF-145** — F-019: a `'\u{…}'` escape is typed `char8` and truncated to its low byte.
- **DEF-146** — F-020: the scope-exit join relays the last-spawned child's error, not the first.
- **DEF-147** — F-021: an expired `timedwait` returns success after the full wait.
- **DEF-148** — F-022: a shared arena destroyed while a spawned thread holds it.
- **DEF-149** — F-023: an un-awaited `async` method call is accepted and emits an undefined symbol.
- **DEF-150** — F-024: `npkc` traps (exit 3) on three macro and depth shapes.
- **DEF-151** — F-025: `--extra-picky=no-wildx` refuses every program, at the prelude.
- **DEF-152** — F-026: `tfp64<Meters>` is accepted and its unit ignored.
- **DEF-153** — F-027: the sixteen lower-priority rows.
- **DEF-154** — F-028: the ninety-four documentation rows.

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
- **DEF-116** — an impl may declare `move` on a parameter its trait lends, or
  lend one its trait moves, and a call through the trait frees twice or leaks.
  Refused `TYPE-014` from 1.6.1 step 0c, which is AFTER HUNT2 `9126350`: HUNT2
  still has it. Its twin DEF-117 (a refused argument cascading into `TYPE-022`
  at a generic call) is a diagnostic. Workbench id O-N28.
- **DEF-103** — a keyword accepted as a declared function or type name, and
  then uncallable. Refused `PARSE-001` from 1.6.0 step 3g.
- **DEF-23 / O-N19** — `TYPE-046` not asked of an unsubstituted `T`. Fixed by
  the compiler's D-264 before `c3bdae2`: a generic copy of an owning element is
  refused there. The grid should see it refused, which makes it a control.
- **Keywords that read like names:** `pid`, `tid`, `fd`, `uid`, `gid`,
  `decreases`, `unbounded`, `sealed`, `hidden`. A binding or module named after
  one is refused at its declaration. That is not a defect.
