# REPORT — the ownership grid at two Nitpick compilers

The final report of `PLAN.md` (M6), written 2026-09-26. Every number here was
measured by the repository's own scripts, and each is traceable to a committed
file: `results/<commit>/` for the grid, `findings/*/VERDICTS.txt` for the
findings, and `PROGRESS.md` for the build record. Where a sentence is reasoning
rather than measurement, it says so.

## In one paragraph

The grid crosses 8 owning types, 14 places and 10 operations, under two
observers. That is 2 240 combinations: 956 were generated as programs and
1 284 skipped, each with a stated reason. Each program was compiled, linked and
run on two legs (-O0, and through `opt -O2`) at two compilers.
- **The recall gate held:** at the baseline, the grid flags every known
  defect's shape.
- **At the hunt compiler:** 82 of the 956 cells are anomalies. 62 are known
  defects whose fixes HUNT does not yet carry. The other **20 are two new
  findings**, both memory-safety defects, and both present at the baseline
  too:
  - **F-001**, a write through a `for` binding;
  - **F-002**, `move(x)` of a lent `T` in a generic body.
- **Between the compilers, nothing regressed.** Exactly 40 cells moved, and
  every one of them is DEF-99's shape, now refused by its fix.
- **M8, the re-hunt (section 9).** At HUNT2 `9126350`, which carries every
  fix named here, the grid has **no anomaly**: 394 cells refused and 562
  clean, each exactly as the generator expected. F-001 and F-002 are refused.
  148 cells moved from HUNT. 136 are the expected moves, and 12 changed
  refusal code, which a bisection traces to DEF-105's fix. There is no new
  finding.

## 1. The two compilers

| role | commit | date | subject | `npkc.ll` bytes / sha256 |
|---|---|---|---|---|
| baseline | `c3bdae2` (`c3bdae270d63c93ab6e89825fddeec9425e2c6fd`) | 2026-09-25 07:06 -0400 | 1.5.8d steps 1-3: the close of cycle 1.5 | 28 111 929 / `4029fc70efbe9cd3…` |
| HUNT | `6fb85d3` (`6fb85d3d834fb7d5568ab996005f800d6d269e8f`) | 2026-09-25 18:25 -0400 | 1.6.0 step 3f: DEF-99, `NITPICK-TYPE-084` | 28 132 333 / `25eb7ee168604005…` |

- **Toolchain.** Both were built with LLVM 20.1.2, by the compiler's
  `quickemit` ladder, on two machines. Session 1 (M0–M4) ran on the author's
  48-core machine and session 2 (M5–M6) on the 4-vCPU cloud VM.
- **Reproducibility.**
  - The baseline's emission matches what GitHub's CI printed (the
    commissioning check).
  - All six build products (`npkc.ll`, `npkc`, `npkrt.o` × 2) are
    byte-identical on the two machines.
  - The recall suite, the first 100 HUNT cells and the whole baseline grid,
    re-run on the second machine, are identical to the first machine's
    records.
- **HUNT's age.** HUNT was the compiler's `origin/main` at M0.3, and it was
  still `origin/main` on 2026-09-26 03:36 UTC. It carries DEF-99's fix and
  none of DEF-102's, DEF-104's, DEF-105's or DEF-106's: its history has a
  `1.6.0 step 3f` subject and none for 3g, 3h or 4b, and its
  `src/frontend/type_codes.npk` declares neither `TYPE-085` nor `TYPE-086`.
- **Cost, for calibration** (the cloud VM, 4 jobs):
  - one compiler build, 60–65 s;
  - the whole grid at one compiler, about 50 s;
  - minimising a cell, 37–61 builds in a few seconds.

## 2. The grid's denominators

**Combinations:** 8 T × 14 P × 10 O × 2 observers = **2 240**.
**Generated: 956**, of which the generator's reading of the rules expects 394
to be refused and 562 to be safe. **Skipped: 1 284.** The list is in
`cells/SKIPPED.txt`, regenerable with `python3 gen/grid.py`.

| skipped | why |
|---|---|
| 520 | a generic `T` is reached only inside a generic body (400); `generic_param` is the place of a generic `T` only (120) |
| 328 | imported tables hold `str` or `box` rows (280); a `string` row has no row type to import, omit or shadow (48) |
| 120 | `at_grow` grows a `List`; the other types do not grow |
| 72 | arrays of arrays, as an element and under `for` |
| 70 | `fixed_elem` is an element of a `fixed` array of `str` or `box` only |
| 52 | no owning sub-place to write: a bare `string`, `List<int64>` |
| 52 | nothing to clone: `List<int64>` and `Wrap` hold no owning string and have no `clone` (`TYPE-019` at probe) |
| 34 | no compile-time constant, so no `fixed`: `Wrap`, `List<int64>` |
| 16 | a generic `T` has no fields a body may name |
| 12 | an import without its row type cannot name `Box`, which six operations need |
| 8 | `Box` declares no `Clone`, so a `Clone`-bounded `T` cannot be `Box` |
| **1 284** | |

**What the 956 did** (`results/<commit>/SUMMARY.md`):

| class | baseline `c3bdae2` | HUNT `6fb85d3` |
|---|---|---|
| refused | 230 | 270 |
| clean | 612 | 604 |
| `DEFECT:double_free` (95) | 56 | 48 |
| `DEFECT:uaf` (70) | 22 | 22 |
| `DEFECT:leg_mismatch` (-O0 ≠ -O2) | 25 | 3 |
| `DEFECT:segv` (107/139) | 5 | 3 |
| `DEFECT:wrong_value` (20–29, 10) | 2 | 2 |
| `OVERRESTRICT` (a control refused) | 4 | 4 |
| `CRASH:npkc`, `timeout`, `other` | 0 | 0 |
| **total** | **956** | **956** |

- **Against the generator's expectations, at HUNT:**
  - Of the 394 expected refusals, 270 are refused and 124 compile. Of those
    124, 74 are `DEFECT`s and 50 run clean (section 6).
  - Of the 562 expected safe, 558 compile (554 clean, and the 4 `DEFECT`s of
    DEF-105's wider row) and 4 are refused (DEF-105 case 1, the
    `OVERRESTRICT` cells).
- **Refusal codes at HUNT**, over 274 refusals including the 4
  `OVERRESTRICT`, each counted once: `TYPE-046` 112, `TYPE-084` 40, `TYPE-047`
  40, `TYPE-071` 38, `MOVE-001` 26, `ASSIGN-002` 8, `TYPE-001` 6, `TYPE-027` 4
  (2 of these also carry `TYPE-071`). The baseline has the same counts without
  `TYPE-084`.
- **Refusals with other codes than expected: 6**, all at DEF-105's import
  places. Two are `TYPE-001` (case 1). Four are `TYPE-027`, the grid's own
  `Box{ s: … }` literal refused for not giving the importer's wider `Box` its
  `z` field; section 7 counts this as a gap.
- No crash, no timeout, and no `other` at either compiler.

## 3. The recall table (M3, at the baseline `c3bdae2`)

The grid had to flag, as `DEFECT:*`, cells of every known defect's shape. It
did at the first run, so neither the grid nor the classifier needed a fix.

| known | shape on the grid's axes | cells of the shape | flagged | the flagging cells |
|---|---|---|---|---|
| DEF-99 | `fixed_scalar`/`fixed_elem` × `move`/`pass_out` | 24 | 16 | `c0020` `c0022` `c0182` `c0184` `c0642` `c0644` `c0750` `c0752` (95/95); `c0035`–`c0038`, `c0199`–`c0202` (107/0, 107/95) |
| DEF-102 | `lent_param` × `field_write`/`assign`/`at_*` | 48 | 24 | `field_write`: `c0221`/`c0222` `c0519`/`c0520` `c0663`/`c0664` `c0771`/`c0772`; `at_free`: `c0059`/`c0060` `c0227`/`c0228` `c0409`/`c0410` `c0525`/`c0526` `c0669`/`c0670` `c0777`/`c0778`; `at_grow`: `c0411`/`c0412` `c0527`/`c0528` (`ra` 70/70, `dx` 95/95) |
| DEF-104 | `generic_param` × `pass_out` | 4 | 2 | `c0890`, `c0948` (95/95) |
| DEF-105 | `imported_fixed` beside a same-named struct, without its row type | 36 | 18 | `c0379`–`c0382` (the wider row read: 107/107, 107/0), and 14 moves and writes through the import |
| DEF-106 *(added 2026-09-26)* | a write into a part of a `fixed` binding: `fixed_scalar` × `field_write`, `fixed_elem` and `imported_fixed_*` × `field_write`/`assign` | 28 | 24 | `c0039`/`c0040` `c0185`/`c0186` `c0203`–`c0206` `c0645`/`c0646` `c0753`/`c0754`, and `c0151`/`c0152` `c0329`–`c0332` `c0353`–`c0356` `c0371`/`c0372` (95/95; 95/107 and 95/0 through DEF-105's wider row) |

- **Why some cells of a shape are unflagged (measured).** A `read_after`
  observation exits before any drop, so a second owner is not seen (DEF-99's
  and DEF-104's `ra` cells). A whole-binding assignment to a loan leaves the
  caller intact (DEF-102's `assign`/`at_overwrite`, as its
  `ctl_whole_lent_string` records). A same-layout row reads correctly
  (DEF-105's `_same`). DEF-106's 4 unflagged cells are refused before the write
  is asked: `TYPE-001` (DEF-105 case 1) and `TYPE-027` (section 7).
- **The known refusals classify as `refused`:** a copy of a local `str`
  (`TYPE-046`, `c0001`/`c0002`) and a non-generic pass-out of a lent `str`
  (`TYPE-047`, `c0053`/`c0054`).
- **DEF-106 was flagged before it was listed.** M3 recorded its cells as "seen
  at the baseline and not in `KNOWN_DEFECTS.md`". On 2026-09-26 the author
  identified them as the workbench's O-N24, and it was added as DEF-106,
  fixed in 1.6.0 step 4b as `TYPE-086`.

## 4. HUNT against the baseline

- **Exactly 40 cells moved** (npkc rc, codes, -O0, -O2), and all 40 went to
  `refused NITPICK-TYPE-084`. They are every cell of DEF-99's shape (a `fixed`
  place, including the imported ones, × `move`/`pass_out`): 32 were anomalies
  at the baseline and 8 ran clean. So DEF-99's fix covers its whole shape in
  the grid.
- **Nothing else moved:** no new anomaly, and no control newly refused. There
  is no regression between `c3bdae2` and `6fb85d3` in the grid.
- **The 82 anomalies at HUNT, deduplicated** (`gen/dedup.py`,
  `results/6fb85d3/DEDUP.md`):

| | cells | its fix |
|---|---|---|
| DEF-106 — a write into a part of a `fixed` binding | 24 | 1.6.0 step 4b, `TYPE-086` — not in HUNT |
| DEF-102 — a write through a lent parameter | 24 | step 3g, `TYPE-085` — not in HUNT |
| DEF-105 — an imported table's row type resolved in the importer (incl. the 4 `OVERRESTRICT`) | 8 | step 3h — not in HUNT |
| DEF-104 — a lent `T` passed out, or `@x` of it, in a generic body | 6 | step 3g — not in HUNT |
| **new: F-001** | **16** | |
| **new: F-002** | **4** | |
| **total** | **82** | |

## 5. The findings

Both findings were minimised, confirmed twice at HUNT on both legs, and run at
the baseline. Each directory holds the reproducers, the controls, the
minimiser's raw outputs, `VERDICTS.txt` and a `README.md` with the
deduplication argument.

| id | shape | class | HUNT `6fb85d3` (npkc / -O0 / -O2, both runs) | baseline `c3bdae2` | controls |
|---|---|---|---|---|---|
| [F-001](findings/F-001-for-binding-write/) | in `for (T:x in arr)` with `T` owning, `x.s = …;` or `@x` handed to a callee that frees or grows the value compiles, and frees heap storage the array's element still owns | `uaf` + `double_free` (and `wrong_value` 22 where the freed block is reused) | the read: 0 / **70** / **70** (field write at element 0: 0 / 22 / 22); the drop: 0 / **95** / **95**; for all three write paths | identical | the same operations through the element itself: 23, 22 and 21 as the rules say; a read-only loop: 21 |
| [F-002](findings/F-002-generic-move-of-loan/) | in a generic body, `T:y = move(x);` of a LENT `T:x` compiles and, at an owning type, frees the caller's value | `uaf` + `double_free` | the read: 0 / **70** / **70**; the drop: 0 / **95** / **95** | identical | the concrete twin: refused `TYPE-047`; the `move T:x` twin: 0 / 21 / 21 |

Deduplication, in short:
- **F-001 is DEF-102's defect at a second place.** The compiler already refuses
  a *move* of a `for` binding with the lent parameter's own `TYPE-047` message.
  In the source, the rule reaches that message only past a `DeclParamDecl`
  check (read, not measured). Whether step 3g's `TYPE-085` covers it cannot be
  measured at HUNT.
- **F-002 is DEF-104's family, with an operator its fix does not name.** In the
  source, `move` and `pass` ask one rule, which returns early when `type_drops`
  says the type does not drop (read, not measured). Whether 3g covers it
  depends on where that fix lands.
- Each README says which programs settle the question at the 3g commit.

## 6. Observations outside the defect definition

- **50 cells the generator expected refused compile and run clean at HUNT.**
  They are 24 `lent_param` × `assign`/`at_overwrite`, which DEF-102's fix
  states it will refuse; 16 `for_binding` × `assign`/`at_overwrite`, F-001's
  place; 8 `generic_param` × `assign`/`at_overwrite`, whose `@x` half DEF-104's
  fix names; and 2 `generic_param` × `pass_out` `ra`, DEF-104's own cells. No observer sees a memory error in
  them, so they are not defects by `CLAUDE.md`'s definition. Each is a write
  or pass-out through a loan that the stated loan rules say should be refused.
- **CONFIRMED A DEFECT AFTER THIS REPORT: DEF-108, `NITPICK-FLOW-001`** — seen by the author in this
  session's reasoning and ruled a defect by his rule that silent wrong answers count; measured further by
  the workbench (a fallible function falling off its end returns a SUCCESS carrying zero).
  **A function with a declared result and no `pass` compiles** and returns a
  zero value (0, or an empty `string`), and `main` without `exit` exits 0. This
  was probed at both compilers (`PROGRESS.md` S16). No reference sentence was
  found for it. It has no memory-safety consequence, since a zero `string` is a
  vacancy.
- **`TYPE-047` calls a `for` binding "this parameter"**, a wording
  observation (F-001).

## 7. What the grid does not cover

**Types.**
- Only `string`, a one-string struct, `List<int64>`, a struct holding a
  `List`, two-element arrays of `string` and `Box`, and a generic `T` at
  `string` and `Box`. Outside the grid are `buffer`, `OwnedFd`, `dyn`, `pick`
  payloads and `Result`, nested structs (`Box` in `Box`), arrays of arrays,
  arrays longer than 2, and generic instantiations at `List` or arrays.
- **A `List` of owning elements (`List<string>`) is outside the grid.** Every
  `List` here holds `int64`, so a reallocation that moves owning elements is
  never exercised.
- One string length only: a 46-byte heap body. A string the runtime might not
  put on the heap is not tried.

**Places.**
- A `for` over an array only: not over a `List`, a slice, a range of owning
  values, or an `Iterator`.
- No `pick` views (D-266), `Result`/`?` paths, closures, method receivers
  (`Self->`), `dyn` receivers (the one write path DEF-102's fix says it does
  not cover), `$$i`/`$$m` paths, or nested fields (`h.v.s`).
- No module-level storage other than `fixed`, and no temporaries.
- One level of pointer (`T->`), and no pointer to a loan's field.

**Operations.**
- Not tried: partial moves (`move(x.s)`), swaps, conditional moves (a move in
  one branch), moves inside loops, `break`/`continue` with live owners, early
  `pass` from a loop body with live owners, `?`, and the fail-safe paths.
- `at_callee` is three callees (overwrite, free, grow), each through one
  pointer.
- Writes into `fixed` storage are two sub-places (`.s`, `[i]`). **Plain
  (non-owning) fields are outside the grid**, and that is where DEF-106's -O0
  107 / -O2 "write dropped" half lives, per the workbench's statement.

**The observers' blind spots.**
- `read_after` exits before any drop, so a **second owner is invisible**
  until something frees it (the unflagged DEF-99 and DEF-104 `ra` cells).
- `drop_at_exit` sees a double free (95) or a fault; **a leak is invisible**.
  There is no leak observer, so a value never freed passes as clean.
  *Inferred, not measured:* the new string that a whole assignment to a loan
  stores may be such a value.
- **The poison shows only until the block is reused.** An allocation after a
  free can land in the freed block, turning a use-after-free into a "new
  value" read (F-001's element 0 reads 22). If the reused block held the
  original's bytes it would read as intact (21), and the cell would be
  classified clean.
- The observers read one byte of a string, or element 0 and `count` of a
  list. Corruption past them is invisible.
- `leg_mismatch` compares exit codes only; two legs that differ in state but
  exit alike agree.

**The recipe.**
- Two legs only: `llc -O0` on the unoptimised IR, and `opt -O2` then
  `llc -O2`. There is no -O1, -O3 or LTO, and one target (x86-64, static).
- A 10-second run timeout, one thread, `env -i`, and no input.

**The generator's own gaps.**
- `imported_fixed_wider` × `assign`/`at_overwrite` (4 cells) are refused
  `TYPE-027` for an incomplete `Box{ s: … }` literal against the importer's
  wider `Box`. The rule the cell targets was never asked there.
- `imported_fixed_bare`'s writes (2 cells) stop at DEF-105 case 1's `TYPE-001`.
- *(Found in M8, section 9.6.)* Once DEF-105 is fixed, `imported_fixed_same`
  and `imported_fixed_wider` × `copy` (4 cells) stop at `TYPE-007`. The
  grid's `Box:y` names the importer's own struct, not the table's row type,
  and the importer cannot name the row type beside its own (`RESOLVE-001`).
  So the copy rule (`TYPE-046`) is not asked there. The `move`/`pass_out`
  cells still reach `TYPE-084`.
- A known defect in a cell can mask another in the same cell.
- The expectations (REFUSE/SAFE) are the generator's reading of the rules. A
  cell whose verdict matches a wrong expectation is not looked at.

## 8. Reproducing

```
python3 gen/grid.py                                   # cells/, 956 programs
python3 gen/run.py .work/hunt                         # results/6fb85d3/cells.jsonl (resumable)
python3 gen/classify.py results/6fb85d3/cells.jsonl   # SUMMARY.md, classified.jsonl
python3 gen/dedup.py results/6fb85d3/ --fixed DEF-99  # DEDUP.md
python3 gen/run_findings.py                           # findings/*/VERDICTS.txt
python3 gen/run_known.py .work/base                   # the recall suite
```

`.work/` holds LLVM 20.1.2 and the two compiler worktrees, built by M0's
commands in `PLAN.md` (see `PROGRESS.md` for the digests to check against).

## 9. M8 — the re-hunt at HUNT2 `9126350`

Written 2026-09-26 by session 3, on a fresh 4-vCPU cloud VM. Every number is
measured by the committed scripts. The records are `results/9126350/`
(`SUMMARY.md`, `MOVES.md`, `DEDUP.md`, `BISECT-3h.md`),
`results/known-9126350.txt` and `findings/*/VERDICTS-9126350.txt`. The build
record is in `PROGRESS.md`'s M8 section.

### 9.1 HUNT2

| role | commit | date | subject | `npkc.ll` bytes / sha256 |
|---|---|---|---|---|
| HUNT2 | `9126350` (`9126350d11d12d20bbcc087dc261405bf2729f29`) | 2026-09-26 03:42 -0400 | 1.6.1 step 0, the NIKOS half (D-324) | 28 857 206 / `2448b3b60d9eb189…` |

- **Which commit.** HUNT2 was the compiler's newest `origin/main` when it was
  built. Its compiler sources are `2eea6f4`'s (1.6.1 step 0: DEF-107's fix,
  `NITPICK-BORROW-015`). `9126350` itself changes only docs and
  `meta/roadmap/1.6/` tools (`PROGRESS.md` S20).
- **Which fixes.** It carries every fix `KNOWN_DEFECTS.md` names. Each commit
  was found by its subject and checked with `git merge-base --is-ancestor`.
  The earlier fixes pass the same check: DEF-95 to DEF-99 (`dfbaf1a`,
  `d156c4f`, `f758995`, `395308f`, `6fb85d3`). The ones this plan waited for:

  | step | commit | fixes |
  |---|---|---|
  | 3g | `5bdae98` | DEF-102, DEF-103, DEF-104 |
  | 3h | `c1a4a05` | DEF-105 |
  | 4b | `f87d2df` | DEF-106 |
  | 5c | `c970483` | DEF-108 |
  | 1.6.1 step 0 | `2eea6f4` | DEF-107 |

- **The build.** M0's commands, 75.8 s. The baseline was rebuilt beside it:
  it is byte-identical to sessions 1 and 2's, and it passes the commissioning
  check again. Both compilers pass the canaries.

### 9.2 Recall, and the two findings, at HUNT2

- **The recall suite matches `KNOWN_DEFECTS.md`'s "once fixed" column in 19
  of 19 rows** (DEF-99, DEF-102, DEF-104, DEF-105; `gen/check_known_fixed.py`).
- **F-001:** all 13 defect programs (7 reproducers, 6 minimised) are refused
  `NITPICK-TYPE-085`. The 4 controls run 23, 21, 22 and 21, as before.
- **F-002:** all 4 defect programs are refused `NITPICK-TYPE-047`. The
  controls run as before: `ctl_concrete_move` is refused `TYPE-047`, and
  `ctl_gen_move_param` runs 21/21.
- Both findings are therefore closed at HUNT2, as `KNOWN_DEFECTS.md` records
  them: faces of DEF-102 and DEF-104. The two HUNT2 runs agree for every
  program. The baseline lines are identical to the committed `VERDICTS.txt`.

### 9.3 DEF-108 and the generator

HUNT2 refuses a body that can reach its own closing brace (`FLOW-001`).
**The grid already ends every function in `pass` or `exit`**, so the
generator was not changed:
- 0 of 7 930 functions in `cells/` fails the static check;
- 0 of 1 000 programs (the grid, `known/`, `findings/`, `commission/`) draws
  `FLOW-001` at HUNT2;
- a planted fall-off is refused by HUNT2 and accepted by the baseline.

The whole grid re-run at the baseline on this VM is identical to the
committed record in 956 of 956 cells.

### 9.4 The grid at HUNT2 (60.5 s, 4 jobs)

| class | baseline `c3bdae2` | HUNT `6fb85d3` | HUNT2 `9126350` |
|---|---|---|---|
| refused | 230 | 270 | **394** |
| clean | 612 | 604 | **562** |
| `DEFECT:double_free` | 56 | 48 | 0 |
| `DEFECT:uaf` | 22 | 22 | 0 |
| `DEFECT:leg_mismatch` | 25 | 3 | 0 |
| `DEFECT:segv` | 5 | 3 | 0 |
| `DEFECT:wrong_value` | 2 | 2 | 0 |
| `OVERRESTRICT` | 4 | 4 | 0 |
| `CRASH:npkc`, `timeout`, `other` | 0 | 0 | 0 |
| **total** | **956** | **956** | **956** |

- **Every cell's outcome is its expectation.** All 394 REFUSE cells are
  refused, and all 562 SAFE cells run 0 on both legs. This is the first
  compiler at which the grid and the generator's reading of the rules agree in
  every cell.
- **Refusal codes**, each counted once over the 394: `TYPE-046` 108,
  `TYPE-085` 92, `TYPE-047` 48, `TYPE-084` 40, `TYPE-071` 40, `TYPE-086` 28,
  `MOVE-001` 26, `TYPE-007` 12, `ASSIGN-002` 8, `TYPE-027` 2.
- **Codes other than the expected ones: 42.**
  - 28 are `TYPE-086` where the generator, written before step 4b, expected
    `ASSIGN-002`.
  - 12 carry `TYPE-007` (9.6).
  - 2 are the `TYPE-027` + `TYPE-071` of the wider `Box` literal, unchanged
    since M3 (section 7).

### 9.5 HUNT2 against HUNT `6fb85d3`, cell by cell (`MOVES.md`)

**148 cells moved.** 136 are the moves `PLAN.md` 8.5 expects. None of the
expected moves is missing. 12 changed refusal code.

| rule (8.5) | cells | at `6fb85d3` | at HUNT2 |
|---|---|---|---|
| DEF-102 — `lent_param` × a write | 48 | 24 anomalies (12 uaf, 12 double free), 24 clean (`assign`, `at_overwrite`) | refused `TYPE-085` |
| F-001 — `for_binding` × a write | 32 | 16 anomalies, 16 clean (`assign`, `at_overwrite`) | refused `TYPE-085` |
| DEF-104 — `generic_param` × `pass_out`, `assign`, `at_overwrite`, `at_free` | 16 | 6 anomalies, 10 clean | refused `TYPE-047` (the 4 `pass_out`), `TYPE-085` (12) |
| F-002 — `generic_param` × `move` | 4 | 4 anomalies | refused `TYPE-047` |
| DEF-105 — the import places × `clone`/`read` | 8 | 4 `OVERRESTRICT` (`TYPE-001`), 4 segv / leg mismatch | clean |
| DEF-106 — the `fixed` places × `field_write`/`assign` | 28 | 24 anomalies; 2 refused `TYPE-001`, 2 `TYPE-027` | refused `TYPE-086` |
| DEF-105's fix: the row type's identity (9.6) | 12 | refused `TYPE-046` (4), `TYPE-084` (8) | refused `TYPE-007` (4), `TYPE-007` + `TYPE-084` (8) |
| **total** | **148** | | |

- **All 82 of HUNT's anomalies are gone.** Each is refused or clean at HUNT2.
- **All 50 cells of section 6** ("expected refused, ran clean") are refused:
  - 48 `TYPE-085`: the 24 `lent_param`, the 16 `for_binding` and the 8
    `generic_param` whole-binding assignments and `at_overwrite`s;
  - 2 `TYPE-047`: the generic `pass_out` reads.
- **No cell became an anomaly, and no SAFE cell is refused.** Among cells that
  compile at both compilers, the only exits that changed are DEF-105's four
  wider-row `clone`/`read` cells (`c0379`–`c0382`), which now run 0/0. The
  only cells newly accepted are DEF-105 case 1's four controls
  (`c0343`–`c0346`).

### 9.6 The 12 changed refusals: DEF-105's fix, bisected

**The cells** are `imported_fixed_same` and `imported_fixed_wider` × `copy`
(4), `move` (4) and `pass_out` (4). At `6fb85d3` they were refused `TYPE-046`
(copy) or `TYPE-084`. At HUNT2 the copies are refused `TYPE-007`, *"expected
`Box`, found `Box`"*, and the moves and pass-outs `TYPE-007` + `TYPE-084`.
8.5 counts a changed refusal code as a regression until shown otherwise, so
the change was bisected (`BISECT-3h.md`).

**Measured:**
- All 76 import cells were run at 3g (`5bdae98`) and at 3h (`c1a4a05`, whose
  parent is 3g).
  - `6fb85d3` and 3g agree in 76 of 76.
  - **`TYPE-007` appears at 3h exactly**, and 3h agrees with HUNT2 in these
    12 cells.
- The control: with the table's `Box` imported by name
  (`imported_fixed_typed`), the same six operations stay refused `TYPE-046`
  or `TYPE-084` at `6fb85d3`, 3g, 3h and HUNT2.

**Read, not measured:**
- 3h's commit message says it resolves an imported `fixed` binding's declared
  type in the binding's home module. So `TBL[i]` is `tbl`'s `Box`, and the
  cell's `Box:y` (or `hold`'s result type) names the importer's own
  same-named struct, which is a different type.

**Why these are not regressions.** That reading, together with three
measurements, is why the 12 count as the fix at work on the grid's own
spelling:
- the change lands at 3h exactly;
- the ownership refusals stay wherever the row type is spelled right;
- `TYPE-084` is still reported beside `TYPE-007`.

**Consequences:**
- *For coverage:* the 4 copy cells at `_same`/`_wider` no longer reach
  `TYPE-046`. The importer cannot name the table's row type beside its own
  (`RESOLVE-001`, DEF-105 case 5), so the grid cannot spell those copies at
  all. This is a gap for section 7's list.
- *An observation, not a defect:* the program is refused, which is the
  language working. Still, the message names both types `Box`, without the
  module that tells them apart.

### 9.7 Findings

- **8.6: there is no anomaly at HUNT2**, so nothing was taken through M5's
  five steps. **M8 has no new finding.**
- **An inference in `KNOWN_DEFECTS.md` is now measured.** DEF-106's
  `c0371`/`c0372` (a write through DEF-105's wider row) were marked "inferred,
  not stated: refused `TYPE-086` once DEF-105's fix resolves the row". They are
  refused `TYPE-086` at HUNT2. At 3h, between the two fixes, both run 95/95,
  where 3g gave 95/107 and 95/0. *Inferred:* with the table's stride the two
  legs agree, and what remains is DEF-106's double free.
- **DEF-106 behind DEF-105.** At 3h, the table-only import's `field_write`
  (`c0341`/`c0342`) compiles once DEF-105's fix lets it, and runs 95/95.
  DEF-106 was reachable there through an import, and 4b refuses it.

### 9.8 What M8 does not change

- **What M8 shows.** At HUNT2 the grid is clean over its whole denominator.
  Every defect it was built around is fixed, and it finds no new one.
- **What it cannot show.** Section 7's blind spots are exactly what it cannot
  see:
  - leaks;
  - a second owner that is never dropped;
  - a use-after-free hidden by reuse;
  - `List<string>`, nested structs, the unlisted places and operations.

  M9 widens the grid into these.
- **Outside the grid altogether** are DEF-107's fix (a view's root frozen,
  `BORROW-015`) and DEF-109 to DEF-115, found by that step's probes. The grid
  has no views, no `dyn`, and no struct holding a pointer.

### 9.9 Cost, for calibration (the cloud VM, 4 jobs)

| step | time |
|---|---|
| LLVM 20.1.2 fetch, test and extract | 345 s |
| four compiler builds (HUNT2, the baseline, and 3g and 3h for 9.6) | 75–76 s each |
| the grid at HUNT2 | 60.5 s |
| the grid at the baseline (8.3) | 63 s |
| the `FLOW-001` check over 1 000 programs | 48 s |
| the recall suite, and the two findings' programs | about 1 min |

### 9.10 Reproducing

```
python3 gen/grid.py
python3 gen/check_leaves.py cells known findings commission --compiler .work/hunt2
python3 gen/run_known.py .work/hunt2 --out results/known-9126350.txt
python3 gen/check_known_fixed.py results/known-9126350.txt --fixed DEF-99 DEF-102 DEF-104 DEF-105
python3 gen/run_findings.py --hunt .work/hunt2 --base .work/base --name VERDICTS-9126350.txt
python3 gen/run.py .work/hunt2                        # results/9126350/cells.jsonl
python3 gen/classify.py results/9126350/cells.jsonl
python3 gen/dedup.py results/9126350/ --fixed DEF-99 DEF-102 DEF-104 DEF-105 DEF-106
python3 gen/compare.py results/6fb85d3/ results/9126350/   # MOVES.md
```
