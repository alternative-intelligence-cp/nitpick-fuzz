# PROGRESS

The live state of `PLAN.md`. Tick a box only when its step is done and
committed. A session that starts here resumes at the first unticked box.

## Milestones

- [x] **M0** — the two compilers built and commissioned
- [x] **M1** — the recall suite (`known/`) run at both compilers and matched
- [x] **M2** — the generator, the runner and the classifier
- [x] **M3** — the recall gate: the grid re-finds every known defect at `c3bdae2`
- [ ] **M4** — CALIBRATION CHECKPOINT: ~100 cells at HUNT, then **stop and wait**
- [ ] **M5** — the hunt
- [ ] **M6** — the report

## Compilers

| role | commit | subject | `npkc.ll` bytes / sha256 | build time |
|---|---|---|---|---|
| baseline | `c3bdae2` (`c3bdae270d63c93ab6e89825fddeec9425e2c6fd`), 2026-09-25 07:06:41 -0400 | 1.5.8d steps 1-3: the close of cycle 1.5 | 28 111 929 / `4029fc70efbe9cd3…` | 67 s |
| hunt | `6fb85d3` (`6fb85d3d834fb7d5568ab996005f800d6d269e8f`), 2026-09-25 18:25:47 -0400 | 1.6.0 step 3f: DEF-99 — `NITPICK-TYPE-084` refuses the move out of `fixed` | 28 132 333 / `25eb7ee168604005…` | 69 s |

Other build products (M0.5):

| role | `npkc` bytes / sha256 | `npkrt.o` bytes / sha256 |
|---|---|---|
| baseline | 9 724 232 / `0cbc150ced5d20f7…` | 72 576 / `162b897539285a77…` |
| hunt | 9 739 968 / `a81223d352d316be…` | 72 576 / `162b897539285a77…` |

**Commissioning check (M0.5): PASSED.** The baseline's `.internal/quickemit/npkc.ll`
is exactly 28 111 929 bytes with sha256 `4029fc70efbe9cd3…`, as GitHub's CI
printed. The emission is identical on this machine.

**LLVM:** `.work/llvm/bin/llvm-config --version` prints `20.1.2` (the
`LLVM-20.1.2-Linux-X64` release tarball, downloaded and extracted by the
command in PLAN.md 0.2).

**Canaries (M0.6), both compilers:** `commission/canary.npk` — npkc rc 0, links,
runs to 0 on the -O0 leg and on the -O2 leg. `commission/canary_malformed.npk`
— npkc rc 1, prints `NITPICK-PARSE-001`, writes no `.ll`.

## M1 — the recall suite

**1.2, baseline `c3bdae2`:** `results/known-c3bdae2.txt` — all 19 rows match
`KNOWN_DEFECTS.md`'s `c3bdae2` columns line by line (npkc rc, codes, -O0, -O2).
No mismatch, nothing to resolve.

**1.3, HUNT `6fb85d3`:** `results/known-6fb85d3.txt`. Which fixes HUNT carries:

| defect | fix | in HUNT? | how checked | HUNT verdicts |
|---|---|---|---|---|
| DEF-99 | `6fb85d3` (step 3f) | **yes** | `git merge-base --is-ancestor 6fb85d3 <HUNT>` (HUNT *is* the fix) | case1/2/3 refused `TYPE-084`; case4 0/0 — matches "once fixed" |
| DEF-102 | step 3g | no | no `1.6.0 step 3g` subject in `git log <HUNT>` | identical to baseline (70/70, 95/95, 22, 21, 0) — still known at HUNT |
| DEF-104 | step 3g | no | as above | identical to baseline (95/95, 70/70, `TYPE-047`) — still known at HUNT |
| DEF-105 | step 3h | no | no `1.6.0 step 3h` subject in `git log <HUNT>` | identical to baseline — still known at HUNT |

So at HUNT the deduplication list is DEF-102, DEF-104 and DEF-105 (their shapes
are still present); DEF-99's shape is expected to appear as `refused TYPE-084`.
The newest commit on the compiler's `main` at M0.3 was `6fb85d3`; the 3g/3h
fixes the plan anticipated "on the night of 2026-09-25" had not landed.

## M2 — the generator, the runner, the classifier

`gen/grid.py` (the cells), `gen/run.py` (4 jobs, resumable), `gen/classify.py`
(`SUMMARY.md` and `classified.jsonl`), `gen/grid_stats.py` (`results/GRID.md`).

**The grid's size:** 2 240 combinations (8 T × 14 P × 10 O × 2 observers);
**956 generated**, **1 284 skipped** with their reasons in `cells/SKIPPED.txt`
(regenerable) and summarised in `results/GRID.md`. Of the 956, the generator's
reading of the rules expects **394 REFUSE** and **562 SAFE**.

| T | generated | skipped | | P | generated | skipped |
|---|---|---|---|---|---|---|
| str | 160 | 120 | | local | 134 | 26 |
| box | 222 | 58 | | move_param | 134 | 26 |
| list | 112 | 168 | | ptr_param | 134 | 26 |
| wrap | 126 | 154 | | lent_param | 104 | 56 |
| arr_str | 108 | 172 | | field | 104 | 56 |
| arr_box | 108 | 172 | | fixed_scalar | 70 | 90 |
| gen_str | 64 | 216 | | elem | 68 | 92 |
| gen_box | 56 | 224 | | for_binding | 68 | 92 |
| | | | | imported_fixed_typed | 34 | 126 |
| | | | | fixed_elem | 34 | 126 |
| | | | | generic_param | 30 | 130 |
| | | | | imported_fixed_same | 18 | 142 |
| | | | | imported_fixed_wider | 18 | 142 |
| | | | | imported_fixed_bare | 6 | 154 |

By O and by observer: see `results/GRID.md` (each observer is exactly half,
478 cells).

**Shakedown (before any result counted):** the whole grid was run at the
baseline into `.work/` and every refusal's codes compared with the cell's
expected codes. One generator bug was found and fixed: a generic `pass_out`
cell's `drop_at_exit` discarded a value with `drop` (refused `TYPE-042`, D-163
rule 4); it now binds the result. After the fix no SAFE cell is refused except
the four `imported_fixed_bare` clone/read controls, which are DEF-105 case 1
(`TYPE-001` at `tbl.npk`), a known defect.

## M3 — the recall gate at `c3bdae2`

The whole grid, 956 cells, ran at the baseline in 58 s (4 jobs):
`results/c3bdae2/cells.jsonl`, `SUMMARY.md`, `classified.jsonl`.

| class | cells |
|---|---|
| clean | 612 |
| refused | 230 |
| DEFECT:double_free | 56 |
| DEFECT:leg_mismatch | 25 |
| DEFECT:uaf | 22 |
| DEFECT:segv | 5 |
| DEFECT:wrong_value | 2 |
| OVERRESTRICT | 4 |

**The recall table. Every known shape is flagged; no miss, so no fix to the
grid or the classifier was needed.** Measured at `c3bdae2`, both legs;
`ra` = read_after, `dx` = drop_at_exit.

| known | shape the plan names | cells of the shape | flagged `DEFECT:*` | the flagging cells |
|---|---|---|---|---|
| DEF-99 | `fixed_scalar`/`fixed_elem` × `move`/`pass_out` | 24 | 16 | `c0020`, `c0022`, `c0182`, `c0184`, `c0642`, `c0644`, `c0750`, `c0752` (fixed_scalar dx: double_free 95/95); `c0035`–`c0038`, `c0199`–`c0202` (fixed_elem ra and dx: leg_mismatch 107/0 and 107/95) |
| DEF-102 | `lent_param` × `field_write`/`assign`/`at_callee` | 48 | 24 | field_write: `c0221`/`c0222` box, `c0519`/`c0520` wrap, `c0663`/`c0664` arr_str, `c0771`/`c0772` arr_box; at_free: `c0059`/`c0060` str, `c0227`/`c0228`, `c0409`/`c0410`, `c0525`/`c0526`, `c0669`/`c0670`, `c0777`/`c0778`; at_grow: `c0411`/`c0412` list, `c0527`/`c0528` wrap — every ra uaf 70/70, every dx double_free 95/95 |
| DEF-104 | `generic_param` × `pass_out` at `gen_str`/`gen_box` | 4 | 2 | `c0890` gen_str dx, `c0948` gen_box dx: double_free 95/95 |
| DEF-105 | `imported_fixed` beside a same-named struct, without its row type | 36 | 18 | the type-resolution defect itself: `c0379`/`c0380` (clone) and `c0381`/`c0382` (read) of `imported_fixed_wider`: segv 107/107, and 107/0 on c0382. The other 14 are moves and writes into the imported `fixed` table (the DEF-99 shape and the fixed-write shape below, through an import) |

**The known refusals classify as `refused`:** `c0001`/`c0002` (copy of a local
`str`) carry `NITPICK-TYPE-046`; `c0053`/`c0054` (non-generic `pass_out` of a
lent `str`) carry `NITPICK-TYPE-047`. DEF-105 case 1 shows as the four
`OVERRESTRICT` cells `c0341`–`c0346` (`imported_fixed_bare` clone/read and
field_write refused `TYPE-001` at `tbl.npk`), as `KNOWN_DEFECTS.md` records it.

**What the unflagged cells of each shape are** (measured; the reading of why is
inference, marked so):
- DEF-99: the 8 `fixed_scalar` × `move`/`pass_out` `ra` cells run 0/0. The read
  happens before any drop and `exit` runs none, so the second owner is never
  freed. *Inferred:* the observer has no way to see a double owner until a drop.
- DEF-102: the 24 `assign` and `at_overwrite` cells run 0/0 with the caller's
  value intact, as `KNOWN_DEFECTS.md`'s `ctl_whole_lent_string` row (21, caller
  intact) says of a whole-binding assignment to a loan.
- DEF-104: the 2 `ra` cells read the returned value and the original, both
  intact, and exit before either is dropped.
- DEF-105: the `_same` read/clone cells, where the importer's struct has the
  same layout as the row, run clean — the same-named struct is resolved but
  nothing is read at a wrong offset.

**Seen at the baseline and not in `KNOWN_DEFECTS.md`** (for M5 to take through
its five steps; not minimised or deduplicated here): writes INTO `fixed`
storage compile — `field_write` into a `fixed` Box or array, and `assign` of a
`fixed` element — and exit 95/95: `c0039`/`c0040` (str fixed_elem assign),
`c0185`/`c0186`, `c0645`/`c0646`, `c0753`/`c0754` (fixed_scalar field_write),
`c0203`–`c0206` (box fixed_elem field_write and assign), and their
`imported_fixed` twins. A whole `assign` of a `fixed_scalar` is refused
`ASSIGN-002`; the sub-place writes are not. And loans
reached through a `for` binding (`for_binding` × `field_write`/`at_free`/`at_grow`)
and a generic body (`generic_param` × `move`/`at_free`) behave as DEF-102 and
DEF-104 do.

## Environment

*(M0.1, measured 2026-09-25)*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-34-generic #34~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep  4 15:38:29 UTC 2 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 12 used, 105 free, 144 available; Swap 15
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  1.7T used  4.9T avail (26%)
python3:   Python 3.12.3
git:       2.43.0
```

This is not the 4-vCPU cloud VM `PLAN.md` describes; it is the author's local
machine (the session was dispatched here by the workbench). See decision S1.

## Decisions and deviations

- **S1 — parallelism stays at 4 jobs** although the machine has 48 cores.
  CLAUDE.md rule 7 states the cap as a rule; the plan's timings were written for
  4 jobs and the recorded costs are meant to be comparable with a cloud run.
- **S2 — the work is on branch `claude/fuzzing-session-milestones-xiv0ni`**,
  not `main`, because the session's harness instructions name that branch.
  Every push goes there; the author merges.
- **S3 — `gen/run_known.py`'s line format.** A leg not built (npkc refused)
  prints `-`; a run that hits the 10-second timeout prints `T`; a signal
  death prints 128+N; a leg whose `opt`/`llc`/`ld.lld` step fails prints
  `opt!N`/`llc!N`/`ld!N`. Build products go to a temporary directory, never
  beside `known/`.

- **S4 — the failsafe carries three more arms** than `lent_field.npk`'s:
  `LimitViolated` 108 and `DecreasesViolated` 109 (demanded by `NITPICK-REACH-002`
  in any program using `List<T>`), and `TbbErr` 110 (demanded in a program with
  a `Clone`-bounded generic). They are in every cell, used or not; an unused
  named arm is accepted.
- **S5 — `exit` is legal only in `main` and `failsafe` (`NITPICK-TYPE-010`)**, so
  a `read_after` cell performs its operation and its observations in `main`
  (or in the callee the place requires) and `exit`s there: no drops run after
  an observation. A `drop_at_exit` cell does its work in `run`, which returns
  normally so every drop runs, and `main` exits with `run`'s result.
- **S6 — observer codes.** 21 original, 22 new value, 23 vacant (length 0 /
  count 0), 24 other live value, 70 poison. Each observation's expected code is
  in the cell's `meta.json`. For a cell expected REFUSE the observation expects
  21 (the original untouched), so if such a cell is accepted, a changed or
  freed original still shows.
- **S7 — `at_callee` is three operations**: `at_overwrite` (the callee assigns
  the whole value through the pointer), `at_free` (the callee moves the value
  out through the pointer and drops it) and `at_grow` (the callee pushes eight
  elements, forcing a reallocation; `list` and `wrap` only).
- **S8 — the sub-place a `field_write` writes** is `.s` for `box`, `.l` for
  `wrap`, and element 0 for `arr_str`/`arr_box` (an owning element). `str` and
  `list` have none (a List's fields are sealed and its element is `int64`).
- **S9 — `clone`**: `.clone()` of the owning string the value holds (`x`,
  `x.s`, `x[0]`, `x[0].s`). `Box`, arrays and `List` have no `clone` method at
  the baseline (`TYPE-019` at probe), so `list`/`wrap` have no clone cell;
  `gen_str`'s clone uses a `T: Clone` bound, and `gen_box` has none (`Box`
  declares no `Clone`).
- **S10 — `imported_fixed` is four places**: `_typed` (the table and its row
  type imported), `_bare` (the table alone), `_same` (the table beside the
  importer's own `struct:Box = { string:s; }`, identical layout) and `_wider`
  (beside `struct:Box = { string:s; int64:z; }`, a wider stride, as DEF-105's
  case 3). A `str` table has no row type, so it has only `_typed`. Without its
  row type the importer cannot name `Box`, so `_bare` has only the operations
  that do not name it (`field_write`, `clone`, `read`).
- **S11 — the generic places** are `generic_param` (a lent `T`), `move_param`,
  `ptr_param` and `local` (a `T` local initialised from a `move` parameter),
  all inside a generic body; the original is observed in the concrete caller.

## Log

- 2026-09-25 (session 1, this branch): started at M0.1 with nothing ticked.
  M0 done: LLVM 20.1.2 fetched, compiler cloned, `base` (c3bdae2) and `hunt`
  (6fb85d3) worktrees built in 67 s / 69 s, digests recorded, both commissioned.
  M1 done: recall suite matches at the baseline 19/19; HUNT carries only the
  DEF-99 fix.
  M2 done: 956 cells generated, 1 284 skipped; one generator bug found and
  fixed in a baseline shakedown.
  M3 done: whole grid at c3bdae2 in 58 s; every known shape flagged, no miss.
