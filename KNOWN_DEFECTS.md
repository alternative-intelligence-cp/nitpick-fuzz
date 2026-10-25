# Known defects — the recall set, and the list to deduplicate against

Every verdict in the `c3bdae2` columns was **measured on 2026-09-25** by the
library workbench's orchestrator. It used the recipe in `PLAN.md`, at the
workbench's pinned compiler built from `c3bdae2`. The "once fixed" columns are
what the compiler's maintainers stated for their fix, measured there. This
repository has measured them since: M1.3 at HUNT, M8 at HUNT2, and **M12 at HUNT3
`0c0f5a3`** (`results/0c0f5a3/known-m12.txt`), where every row gives its "once
fixed" verdict: 19 by `gen/check_known_fixed.py`, DEF-106's and DEF-108's six by
hand.

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
- **The F-001/F-002 note (M12).** The compiler's registry names neither finding: DEF-102's and
  DEF-104's records (OPEN_DECISIONS:2282-2330 at the time of the registration audit) do not cite
  them. Their closure rests on the workbench's O-N21 and O-N22, step 3g (landing 59), this
  repository's `VERDICTS-9126350.txt`, and now `VERDICTS-0c0f5a3.txt`: at HUNT3 `0c0f5a3` F-001's
  13 programs are `TYPE-085` and F-002's 4 `TYPE-047`, the controls as recorded, `ctl_gen_move_param`
  21/21.
- The compiler's chain was re-based after 3g's first harness. The planned shas are 3g
  `5bdae98`, 3h `c1a4a05`, step 3 `0da2be7`, step 4 `996784e`, 4b `f87d2df` (DEF-106),
  5 `4e467bc`, 5b `77314e9`, then 5c (DEF-108, `FLOW-001`). **Identify each by its
  commit SUBJECT, not by a sha**, since a chain can be re-based again.

## M9's findings, registered by the compiler seat — deduplicate against these

Registered on 2026-09-26 in the compiler's OPEN_DECISIONS §4, each citing this
repository's `findings/` directory and `main` `88e6355` as its evidence. **All
nine are fixed in the compiler's subcycle 1.6.1d, which lands after 1.6.1c** —
so none is fixed in HUNT2 `9126350`, nor in `9f6f370`. Find each fix by its
subject. Each bullet now carries its landing (1.6.1d step 1 = landing 74, step 3 =
76, step 3b = 78, step 4 = 79) and M12's measurement at HUNT3 `0c0f5a3`
(`findings/F-0NN-*/VERDICTS-0c0f5a3.txt`, `results/0c0f5a3/MOVES12.md`).

- **DEF-118** — F-003: a consuming `pick`'s binding escapes the move rules (a
  read after its move, a second move). **Fixed at landing 74.** At HUNT3: F-003's four defect programs `MOVE-001`; the grid's 44 cells refused.
- **DEF-119** — F-004: a move out through a pointer while a view of the root is
  live (the freeze records a write, not a move out). **Fixed at 74.** At HUNT3: `view_addr_to_freeing_callee`
  `BORROW-015`, DEF-119's code; `view_claim_i_to_freeing_callee` `BORROW-013`, which is DEF-123's (a `$$i` claim's
  holder), also landed at 74 (worded so in M13, M12v's finding (2)).
- **DEF-120** — F-005: `(<-p) = v` never drops the old value. **Fixed at 76.** At HUNT3: live 0; the grid's 113 leak cells clean (its other 4 are DEF-123's REFUSE cells, refused).
- **DEF-121** — F-006: a consuming `pick`'s binding is never dropped. **Fixed at 76.** At HUNT3: live 0; 24 of the grid's 28 cells clean, the other 4 F-049's (below).
- **DEF-122** — F-007: `to_cstring`'s buffer is never freed. **Fixed at 78** (D-328). At HUNT3: the churn's peak is 10, not 10 × N; 60 `OwnedFd` cells' live bytes fell to 0.
- **DEF-123** — F-008: a write through a `$$i` claim's holder is not refused. **Fixed at 74.** At HUNT3: `BORROW-013`; the grid's 40 cells refused.
- **DEF-124** — F-009: a re-initialised `move` parameter cannot be read. **Fixed at 79.** At HUNT3: 22/22; the grid's 72 cells clean. The same shape at a consuming pick's binding is F-049, new at 74.
- **DEF-125** — F-010: the lent-`dyn` swap refused `BORROW-002` since 1.6.1
  step 0. **Fixed at 79.** At HUNT3: 0/22/22; the grid's 12 cells clean.
- **DEF-126** — M8's observation: a `TYPE-007` message names two same-named
  types by one word (the workbench's O-N29). The refusal is right. **Fixed at 1.6.1d
  step 4, landing 79** (NOTICES row 79 names it); a message, not measured here.

## M10's findings, and one of the compiler seat's own — deduplicate against these

Registered on 2026-09-26 by the compiler seat, each citing this repository's
`findings/` and its M10 verdicts; **all are fixed in the compiler's subcycle
1.6.1d** (its step 1: DEF-127 and DEF-134; step 2: DEF-128 … DEF-130; step 4:
DEF-131 … DEF-133), so HUNT2 `9126350` and `9f6f370` still carry them. Those steps
are landings 74, 75 and 79. At HUNT3 `0c0f5a3` (M12) every finding below gives its
fixed verdict.

- **DEF-127** — F-011: a `for` binding outlives its loop in the emitter; an
  outer binding of the same name reads the loop's slot, and past it. **Fixed at 74.** At HUNT3: 0/0.
- **DEF-128** — F-012: a `for` over a range runs zero times at its type's edges. **Fixed at 75.** At HUNT3: 0/0.
- **DEF-129** — F-013: `loop` and `till` widen an unsigned bound by its sign. **Fixed at 75.** At HUNT3: 0/0.
- **DEF-130** — F-014: `till` with a negative limit counts down. **Fixed at 75.** At HUNT3: 0/0.
- **DEF-131** — F-015: `<=>` refused by the emitter (`EMIT-002`). **Fixed at 79.** At HUNT3: 0/0, and M11's seven `<=>` claims agree.
- **DEF-132** — F-016: a `pick` range pattern with a negative bound is `EMIT-002`. **Fixed at 79.** At HUNT3: 4/4.
- **DEF-133** — F-017: seven reference sentences the compiler contradicts. **Fixed at 79** (d7 by D-331, d1–d6 by correcting the references). At HUNT3: `d7` is `TYPE-004`.
- **DEF-134** — the compiler seat's own: a by-value receiver method called on
  a POINTER (`q.peek()` with `Box->:q`, `peek = int64(Box:self)`) reads the
  pointer's bits as the struct — a silent wrong answer at every pin. **Fixed at 1.6.1d
  step 1, landing 74** (NOTICES row 74 names it); no program of this repository's.

## M11's findings, registered by the compiler seat — deduplicate against these

Registered on 2026-09-26, each citing this repository's `findings/` and `main` `3d7d924`. **DEF-144 … DEF-153 are
fixed in the compiler's subcycle 1.6.1e** (DEF-153 for its sixteen rows), so HUNT2, `9f6f370` and `1b4f0c6` still carry
them. **DEF-154 (F-028's ninety-four documentation rows) is OPEN** in the compiler's registry (status read at HUNT3
`0c0f5a3`, 2026-10-15). A resumed M11 must not report these again. Landings: 1.6.1e step 1 = 77, step 2 = 80, step 3 =
83; M12's measurement at HUNT3 follows each.

- **DEF-144** — F-018: a macro's free name, alone or as a comparison's operand, reads the call site's local. **Fixed at 77.** At HUNT3: 0/0; `mc0188`, `mc0202` agree.
- **DEF-145** — F-019: a `'\u{…}'` escape is typed `char8` and truncated to its low byte. **Fixed at 77** (the escape is `char32`). At HUNT3: `u1` `TYPE-007`, `u2` 0/0.
- **DEF-146** — F-020: the scope-exit join relays the last-spawned child's error, not the first. **Fixed at 77** under D-334 (the earliest-*spawned* child's error). At HUNT3: `j1` 0/0; the control `ctl_j3` now 10/10, the file the fuzzer's to re-spell (the author's call).
- **DEF-147** — F-021: an expired `timedwait` returns success after the full wait. **Fixed at 77.** At HUNT3: 0/0.
- **DEF-148** — F-022: a shared arena destroyed while a spawned thread holds it. **Fixed at 77.** At HUNT3: `BORROW-016`.
- **DEF-149** — F-023: an un-awaited `async` method call is accepted and emits an undefined symbol. **Fixed at 80.** At HUNT3: `TYPE-043`.
- **DEF-150** — F-024: `npkc` traps (exit 3) on three macro and depth shapes. **Fixed at 80.** At HUNT3: `PARSE-001` (c1's `$$i` receiver, the reference's own example's), `PARSE-012`, 0/0.
- **DEF-151** — F-025: `--extra-picky=no-wildx` refuses every program, at the prelude. **Fixed at 80.** At HUNT3: the flag accepts the canary.
- **DEF-152** — F-026: `tfp64<Meters>` is accepted and its unit ignored. **Fixed at 80.** At HUNT3: `TYPE-016`.
- **DEF-153** — F-027: the sixteen lower-priority rows. **Fixed for its rows**: three at 78 (the `cstring` literal), twelve at 83, `mc0309b` at 90 (D-338); `mc0085b` became a documentation row. At HUNT3 its claims agree.
- **DEF-154** — F-028: the ninety-four documentation rows. **OPEN** (documentation; no landing). At HUNT3 none of its claims moved.

## M11 sessions 8 and 9's findings (F-029 … F-048), and the registry's DEF-227 … DEF-253 — deduplicate against these

Registered from 2026-10-07 in the compiler's OPEN_DECISIONS §4 (from the workbench's O-N35 and O-N36), with
the compiler seat's own and the library seats' entries beside them. **Status read at HUNT3 `0c0f5a3`** (landing
113, 2026-10-15; `git show 0c0f5a3:meta/roadmap/OPEN_DECISIONS.md` and `meta/NOTICES.md`), and every fixed row
**measured there by M12** (`findings/F-0NN-*/VERDICTS-0c0f5a3.txt`, `results/0c0f5a3/`). HUNT2 `9126350` and
`93bcb66` carry every one of these.

Fixed:
- **DEF-227** — F-037: a trait object built by `x => dyn Trait` read freed memory. **Fixed at landing 94**
  (`05a7b02`). At HUNT3: `u1`/`u2`/`u3` 0/0 (they answer 7), and `as0453` agrees.
- **DEF-228** — the workbench's O-N38 item 1: the `&{ }` splice leaked every `to_string` result. **Fixed at 95**
  (`d98c5e1`). No program of this repository's.
- **DEF-229** — F-041: npkc did not terminate on an unbounded generic instantiation. **Fixed at 96** (`afa8499`):
  `NITPICK-TYPE-018`. At HUNT3: `h1` is `TYPE-018` in 0.09 s, and `tr0586` agrees.
- **DEF-230** — F-047: a write through a `fixed uint8[]` view landed. **Fixed in two steps**, at 98 (`9fede45`,
  D-348) and 103 (`7e91730`, D-350/D-351: `fixed T[]` a type). At HUNT3: `s1`/`s2` `TYPE-086`, `ctl_s3` 0/0,
  `ctl_s4` `ASSIGN-002`; `ty1719b` agrees.
- **DEF-231** — `ty1657`, F-044's frac row: a `frac` printed its stored parts, so −(1 3/8) read "-2 5/8". **Fixed
  at 97** (`28194e0`, D-347). At HUNT3: `ty1657` agrees. `ty1635`, whose claim was the old invariants, now
  disagrees (10/10): D-347 changed them.
- **DEF-232** — F-048: a struct with a `NIL` field was emitted as `{ i32, void }`. **Fixed at 112** (`958890a`): a
  `NIL` member occupies nothing in the emitter too (D-084). At HUNT3: `n1`/`n2` 0/0, `ctl_n3` 0/0; `ty1944` agrees.
- **DEF-233** — F-038: npkc exited 3 on `give` or `fall` outside a pick arm. **Fixed at 111** (`e50eaf4`):
  `NITPICK-TYPE-094`; `NITPICK-TYPE-040` inside a `defer` body. At HUNT3: `c1`/`c2` `TYPE-094`, `ctl_c3` 0/0;
  `as0202`, `as0203` and `as0267.sh` agree.
- **DEF-235** — F-029 and F-036 (a): a keyword accepted as a declared name. **Fixed at 113** (`0c0f5a3`): every
  declared name of every kind is an identifier, `PARSE-001`. At HUNT3: `k1` `PARSE-001`, `k2` `PARSE-001` beside
  its `PARSE-002`; `lx0054`, `lx0114`, `lx0121` agree. Three claims are now refused at a binding named `buffer`
  before their own claims are reached (`me0119`, `me0119b`, `me0183`), and `md0042` at a `mod:mod;` header:
  their re-spelling is `nitpick-fuzz_2`'s to schedule.
- **DEF-237** — F-045: `??` on a `Result` advised the retired `?`. **Fixed at 113**: the advice names `?!`/`?|`
  (D-175). At HUNT3: `d1` is still `TYPE-007`, with the new advice.
- **DEF-238** — F-046 (a): a `frac` member assigned or addressed passed the checker and was `EMIT-002`. **Fixed
  at 111**, "both rows": `NITPICK-TYPE-024` by name. At HUNT3: `ty1649` agrees.
- **DEF-241** — the template's lone string item aliased. **Fixed at 95** (`d98c5e1`). No program of ours.
- **DEF-243** — the workbench's O-N40 item 1: a builtin named as a value. **Fixed at 107** (`508d7c5`):
  `NITPICK-TYPE-054`. No program of ours.
- **DEF-246** — DEF-230's faces: a `fixed` view meeting a plain slot. **Fixed at 103**: `TYPE-007`. At HUNT3:
  the six M11 claims binding `string_bytes` into a plain `uint8[]` are refused `TYPE-007` (Option C's), and
  `bi0010`/`bi0017` agree for that reason, not their own.
- **DEF-247** — `fixed`/`stack` as return qualifiers. **Fixed at 103.** No program of ours (M13's search: `git grep
  -nE 'func:[A-Za-z_0-9]+ *= *(fixed|stack) ' -- '*.npk'` and the same over `cells/` and `cells9/` find none).
- **DEF-248** — F-046 (b): a `fixed` parameter reassigned. **Fixed at 102** (`98cfe35`): `ASSIGN-002`. At HUNT3:
  `ty1873` agrees.
- **DEF-249** — the workbench's O-N41: `exit` of a fallible call. **Fixed at 104** (`085bc01`). No program of ours
  (M13's search: `git grep -nE '\bexit +(raw +)?[A-Za-z_][A-Za-z_0-9.]*\(' -- '*.npk'` finds one `exit` of a call,
  `cc0264`'s `exit c.load() - 1i32;`, an `atomic<int32>` load that cannot fail; `cells/` and `cells9/` have none, and
  no M12 move is landing 104's).

Partly fixed:
- **DEF-234** — F-034: (a) an `extern` method with a byte-slice parameter generates a stub refused `TYPE-072`,
  (b) `use mod.f;` is `RESOLVE-002`, (c) a constant cycle's `RESOLVE-006` named no cycle. **(c) fixed at 113**
  (one report per cycle, naming its chain; `md0183` agrees at HUNT3); **(a) and (b) OPEN.**
- **DEF-236** — F-039 (a)(c)(d)(e) and F-042: **(c), (d) and (e) fixed at 113**: a non-constant `joins` deadline
  is `TYPE-045`, an attribute the language does not have `NITPICK-DERIVE-007`, an `opaque struct` outside an
  `extern` block `NITPICK-RESOLVE-014`. At HUNT3 `as0555`, `as0583`, `as0043` and `tr0368` agree, and `as0572`'s
  `#[align(16i32)]` is refused (D-020: the language has no `#[align]`). **(a), a `comptime` value parameter, is no
  longer OPEN: fixed at 117** (`76a8102`; S-135 settled as D-353, out until designed): it is refused by name at its
  declaration as `NITPICK-TYPE-095`. Measured by M13 at HUNT4 `c72639f`, one compile of `m11/programs/as0062.npk`:
  npkc 1, `NITPICK-TYPE-095 as0062.npk:10:12`, "`K` is a `comptime` value parameter, a form the language reserves
  and has not designed (D-353)", at line 10, `func:scale<comptime int32:K> = int32(int32:x) never fails { pass (x *
  K); };`. HUNT3 gives `NITPICK-EMIT-002` at 10:71 (measured in M13 too). With (a), all of DEF-236 is fixed at HUNT4.

Open at HUNT3:
- **DEF-190** — F-036 (b): a literal's trailing `_` (`10_i32`) accepted. OPEN at HUNT3.
- **DEF-239** — documentation: F-030, F-031, F-032, F-033, F-035, F-040, F-043 and F-044 (32 TYPE rows), by file.
  OPEN; a documentation-sync landing, none scheduled. F-039 (b) and F-046 (c), the backward pipe, are **not
  defects**: `<|` takes its function on the right (DEF-236's note); they correct F-031's pipe row.
- **DEF-240** — this repository's BUILD observation: npkg's unknown-stage message omits `explore`. OPEN.
- **DEF-242** — the prelude's site table in every emission. OPEN, low.
- **DEF-244** — the workbench's O-N40 item 2: a sibling import (`RESOLVE-010`). OPEN.
- **DEF-245** — the sixth face of DEF-164: a failing declaration header's body reported again. It names
  `as0100` and six more fuzz programs (`tr0425`, `cc0151c`, `md0219`, `tr0448`, `vf0580`, `tr0550`). OPEN, low.
  At HUNT3 none of the seven moved.

Open at HUNT3, fixed since (each row names its landing; this heading is M14 (1b)'s, M13v's finding (7)):
- **DEF-250** — the library seats' report: a module binding with no initialiser emitted read-only; -O2 answers 0.
  OPEN at HUNT3 (registered there by `nitpick-compiler_37`). **Fixed at landing 114** (`2f0937a`): D-211 is asked of
  every module binding, `TYPE-055` at the declaration. **Measured by M13 at HUNT4 `c72639f`:** the seed
  `bare_binding` is refused `NITPICK-TYPE-055` (107/11 at HUNT3 and the baseline), and all 86 of grid13's section A
  faces with it (a write faulting at -O0 and reading zero at -O2, a read of the zero default, an atomic store
  faulting on both legs, a channel `send` failing); `results/c72639f/MOVES13.md` rows 8, 11–15.
- **DEF-251** — the same report: a NULL store; -O2 is `unreachable`. **(i) fixed at landing 115** (`7992c77`):
  `null_pointer_is_valid` on every emitted `define`. **(ii) fixed at landing 119** (`34979dc`, D-355, S-136's option
  (c)): `NULL` where a plain pointer or an Optional is expected is `TYPE-096` at the literal. **Measured by M13 at
  HUNT4 `c72639f`:** the seed `null_store` is refused `NITPICK-TYPE-096` (107/99 at HUNT3 and the baseline), and so
  are grid13's 78 plain section B faces, among them the inferred face measured at HUNT3 and the baseline (a struct
  reached through a parameter or a return, loaded and unread: the `NULL` test folded away, 107/0); under (i) the
  `wild` store, used load, field read and `wild` callee fault on both legs (107/107). **A dead `wild` load still
  faults at -O0 and is deleted at -O2 (107/14): F-051**, the check of (i), scope wild. `MOVES13.md` rows 9, 16, 17.
- **DEF-252** — the library seat's report of 2026-10-15: a view re-seated by a CALLEE outlives the block's
  string, exit 170 at both legs, **a use after free in safe code**. OPEN at HUNT3 (registered at 113). **Fixed at
  landing 116** (`2f50640`): `BORROW-002` at a callee's store into a destination the frame owns. **Measured by M13
  at HUNT4 `c72639f`:** the seed `probe08h_view_reseated` is refused `NITPICK-BORROW-002` (170/170 at HUNT3 and the
  baseline), and so are grid13's section E faces for a callee storing into the whole pointee, into a field,
  through a method and two levels down (8). **A callee storing into an element of an array of holders still reads
  the poison at HUNT4 (170/170): F-050.** `MOVES13.md` rows 10, 19.
- **DEF-253** — the same report: a `Self->` trait method called through a bound does not link. OPEN at HUNT3
  (registered at 113). The registry at HUNT4 records it **fixed at landing 118** (`c9baa9e`, with DEF-254); no
  program of ours exercises it (read, not measured).

Registered since M12 (status read in the registry at HUNT4 `c72639f`, landing 137, 2026-10-21):
- **DEF-256** — F-049 (M12, `findings/F-049-pick-binding-reinit-refused/`): a consuming `pick`'s binding re-assigned
  after a move was `MOVE-001` at its next read, a false refusal new at landing 74 (DEF-118's fix), DEF-124's shape at
  a third binding kind. Registered at landing 116 by `nitpick-compiler_38`, lower priority (a refusal of what
  MEMORY_REFERENCE §2.3 admits). **Fixed at landing 132** (`6f0f518`, 2026-10-18): `assign_assign` (bindings.npk)
  marks a `SYM_PAT` target assigned, as it marks a local and a parameter. **Measured by M13 at HUNT4:**
  `pick_reinit_read` and `pick_reinit_loop` 0/22/22, the controls unchanged; the M9 grid's 24 cells clean.

Not registered: M13's findings (2026-10-21), candidates for the workbench (PLAN D6), each present at the baseline:
- **F-050** (`findings/F-050-callee-view-store-into-array-element/`): a callee storing a block-local view into an
  element of the array behind its pointer argument outlives the storage, 170 at both legs at HUNT4: a use after
  free in safe code, DEF-252's shape at a destination landing 116 does not reach.
- **F-051** (`findings/F-051-wild-dead-load-legs-disagree/`): a dead load through a `wild` `NULL` pointer faults at
  -O0 and is deleted at -O2 (107/14), under DEF-251 (i). Scope wild, the check of (i).
- **F-052** (`findings/F-052-atomic-method-through-pointer-not-lowered/`): an atomic's method called through a
  pointer with `.` passes the checker and is `EMIT-002`; `(<-p).load()` lowers. Lower priority.

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
