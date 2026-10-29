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
- **M9, the widened grid (section 10).**
  - **What was added:** a leak observer, a reuse sentinel and a read-now
    observer, plus new types, places, operations and exits. That is 7 571
    cells, and 28 519 combinations skipped with reasons.
  - **The recall gate holds.**
  - **At HUNT2:** 197 anomalies in four families, and **eight findings** in
    all. Two are **memory faults at HUNT2**:
    - **F-003**, a consuming `pick`'s binding escapes the move rules (a use
      after free, a double free);
    - **F-004**, a view's root freed through a callee that moves out, a gap
      in DEF-107's fix.
  - **The others:** three leaks (F-005 a store through a pointer, F-006,
    F-007), a claim rule not enforced (F-008), and two lower-priority
    over-restrictions.
  - **Seven of the eight are present at the baseline too.**
- **M10, silent wrong answers (section 11).**
  - **The checklist:** 229 items from the references. Each carries the
    sentence that states its answer and an expectation written from that
    text before any run. 223 are testable, with a program each; 6 cannot be
    tested from the text, each with its reason.
  - **At HUNT2:** 212 agree and 11 disagree. At the baseline 210 agree, and
    the two more that disagree are known (DEF-101, DEF-98). The DEF-108 recall
    holds: the four shapes are flagged at the baseline and refused
    `FLOW-001` at HUNT2.
  - **The disagreements are seven findings, all present at the baseline and
    at the compiler's newest `main` (`9f6f370`):**
    - **F-011**: a `for` binding outlives its loop in the emitter. A later
      use of an outer binding of the same name reads the loop's slot: a
      silent wrong value, and with an array outer binding an out-of-bounds
      stack read that differs between -O0 and -O2.
    - **F-012**: a `for` range runs zero times at its type's edges: a signed
      inclusive range ending at the maximum, and an unsigned range across
      the sign bit.
    - **F-013**: `loop`/`till` sign-extend an unsigned bound. `loop(100u8,
      200u8, 1u8)` runs 156 times downward.
    - **F-014**: `till` with a negative limit counts down, where the
      reference says zero trips.
    - **F-015** and **F-016**: `<=>` and a negative range pattern are refused
      by the emitter (`EMIT-002`).
    - **F-017**: seven reference sentences the compiler contradicts
      (documentation findings).
- **M12, the re-baseline at HUNT3 (section 13).** At HUNT3 `0c0f5a3`, the compiler's `main` after
  landing 113, under LLVM 20.1.8 on the author's go: the recall suite gives "once fixed" in all 25
  rows; every finding whose registry row is FIXED gives its fixed verdict, measured here for the first
  time outside the compiler seat; the widened grid has no anomaly left (197 at HUNT2); and every move
  from HUNT2 carries a landing number (`results/0c0f5a3/MOVES12.md`, zero unexplained). One new
  lower-priority finding: **F-049**, a consuming `pick`'s binding re-initialised after a move is
  refused, since landing 74.
- **M13, the initialisation and pointer-store grid (section 14).** 933 cells aimed at DEF-250, DEF-251
  and DEF-252's class, with the -O2 leg as the observer, run at the baseline, HUNT3 and HUNT4 `c72639f`
  (landing 137). At HUNT3 190 cells are off their expectation; at HUNT4 landings 114, 115, 116, 119 and 120
  bring 180 of them to it, the regression leg moves only by landings 132 and 136, and three findings remain,
  all present at the baseline: **F-050**, a callee storing a block-local view into an element of an array of holders,
  a use after free in safe code at HUNT4 (a soundness hole, DEF-252's face that 116 does not reach);
  **F-051**, a dead `wild` load deleted at -O2, the legs disagreeing under DEF-251 (i) (scope wild, reported
  apart); and **F-052**, an atomic's method through a pointer that the emitter cannot lower (`EMIT-002`).
- **M14, the S-140 class (section 15).** At HUNT5 `249eae9` (landing 161) under LLVM 20.1.2, the oracle gains one
  narrow run class, `PERMITTED:S-140`: the legs' one disagreement D-364 permits, an unused load through a `wild`
  `NULL` pointer, granted only to a cell the generator built as one and only when its -O2 leg answers as its
  load-deleted twin does. grid14's 109 cells: 43 permitted, 56 clean, and every used load faults at both legs (30 of
  30). One candidate, **F-053**: a `wild` `NULL` load whose value the text reads but that decides nothing on the path
  run is sunk or deleted at -O2 (107/0), reported apart as the check of §27 (D-364). At HUNT5 F-050 and F-052 are
  fixed, and F-051 is the permitted disagreement.
- **M15, the DEF-296 family (section 16).** This is a sweep, at HUNT6 `1480ca8` (landing 163) with REG155 `02856cf`
  as the recall leg, under LLVM 20.1.2. It covers the roads that store a view of a pointer parameter's pointee into the
  frame's storage, and the writes that then free the pointee. grid15 has 100 cells (1 356 combinations skipped), and
  the recall gate passes every check. Every twin is clean at both compilers, and nothing regressed. At HUNT6, 14
  cells (eight keys) read freed memory in safe code. Each key is a shape still OPEN in the registry, so M15 files no
  new finding:
  - DEF-298 (`cbv`, `cbp`);
  - DEF-299 (`cps`, `cpp` and `tl` in an inner block);
  - DEF-309 (`cres`);
  - DEF-305's parameter-rooted gap (`cresc`, `cresm`).

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

## 10. M9 — the ownership grid widened into its named gaps

Written 2026-09-26 by session 4, on a fresh 4-vCPU cloud VM. Every number is
measured by the committed scripts. The records are:
- `results/c3bdae2/` and `results/9126350/`: `cells9.jsonl`, `SUMMARY9.md`,
  `classified9.jsonl` and `DEDUP9.md`;
- `results/GRID9.md`: the denominators;
- `findings/F-003` … `F-010`, each with `VERDICTS.txt` and, where it came from
  the grid, `CELLS.txt`.

The build record is in `PROGRESS.md`'s M9 section.

### 10.1 The compilers

The same two as section 9: the baseline `c3bdae2`, and HUNT2 `9126350`, which
was still the compiler's `origin/main` at 10:28 UTC. Both were rebuilt by M0's
commands, byte-identical to session 3's, and passed the commissioning check
and the canaries. The M2 grid re-run on this VM is identical to the committed
records in 956 of 956 cells at each.

### 10.2 The new observers (9.1, 9.2)

- **Leak (`lk`).**
  - *Why a probe:* the runtime's `heap:` line prints bytes requested,
    peak_live and the allocation count, and **no live-at-exit figure**. It was
    read in `npkrt.ll` at the baseline and in `nitpick-time`'s
    `meta/roadmap/0.1/0.1.4b.md` at `1cfd3f0`. 0.1.4b's §1.2 states the
    consequence: `peak_live` alone cannot tell a leak at exit.
  - *How:* the cell's drop-at-exit program, then `main` allocates a
    1 048 576-byte probe and exits. `peak_live − 1 048 576` is the bytes live
    after `run` returned, exact whenever `allocated − 1 048 576 < 1 048 576`,
    which the same line shows.
  - *Calibration:* a program that frees everything reads 0. One that keeps a
    46-byte string (`exit` runs no drop) reads 46, where a peak-only reading
    gives 46 for both.
  - *`OwnedFd`:* the leak is a descriptor. `main` counts the descriptors 3..15
    still open after `run`.
- **Reuse sentinel (`rs`).** The read-after program, with a same-sized sentinel
  allocated between the operation and the reads. A freed body that is still
  free is taken by the sentinel, and the original then reads the sentinel's
  bytes (25).
- **Read now (`rn`), at the loop places.** The original is read inside the loop
  right after the first iteration's operation, before the next iteration
  allocates.

**What they added, measured**, on section A's same 478 M2 programs, against
each program's M2 twin:

| observer | at the baseline | at HUNT2 |
|---|---|---|
| leak, against the M2 drop-at-exit twin | 66 cells the twin called clean leak | **42** cells the twin called clean leak |
| read now, against the M2 read-after twin | 2 cells turn the twin's reused-block 22 into the poison, 70 (F-001's field writes) | none (every loop write is refused) |
| reuse sentinel | 54 read cells read the sentinel through the original, **reuse proven**; 2 still read the poison | 3 cells read the sentinel (F-003) |

### 10.3 The widened grid (9.3–9.5) and its denominators

`gen/grid9.py` writes `cells9/`, and `gen/grid.py`'s 956 cells are unchanged.
Its `--selfcheck` renders the M2 programs with the new builder, byte-identical
in 956 of 956. **7 571 cells, and 28 519 combinations skipped with their
reasons: 36 090 in all.** Expectations: REFUSE 3 210, SAFE 4 361, each written
in the generator before the grid's first run (9.6).

| section | crossed | cells | skipped |
|---|---|---|---|
| A | the M2 grid's 478 combinations × the leak and sentinel observers (read now at the loop place) | 986 | 448 |
| B | **types**: `List<string>` (growth moves owning elements), a struct in a struct (`h.v.s`), `string[3]`, `Box[3]`, a generic `T` at `List<string>` and at `string[2]`, `buffer`, `OwnedFd`, `dyn` × the M2 places and operations | 1 700 | 4 600 |
| C | **places**: `for` over an index range of an array or a `List`; `for` over a slice parameter from an array or a `List`; a lending and a consuming `pick`; a `Self->` receiver on an owned and a lent holder; a lent `dyn`'s method; `$$m`; `$$i`; a temporary; the `Result` paths (`?|` success, `?|` failure, `relay`) × the M2 operations, the partial move and the swap | 2 076 | 13 224 |
| D | **operations**: a partial move, a swap, a conditional move taken and not taken, a move in a loop with and without re-initialisation × every place | 2 396 | 9 844 |
| E | **exits with live owners**: `break`, `continue`, an early `pass`, an early `pass` of an owner, `relay`, `relay` past a temporary, a trap to failsafe, a trap past a temporary × holders × types | 413 | 403 |

Where the language has no spelling, the cell is skipped with the reason:
- `for` over a local slice view is `BORROW-009`;
- `for` over a `List` is `TYPE-033`;
- `dyn T[2]` and `dyn T->` parse as `dyn (T[2])` and `dyn (T->)`;
- a generic `T` cannot be grown.

Two shakedowns fixed four generator bugs before any result counted
(`PROGRESS.md` S29). No expectation was changed.

### 10.4 The recall gate, kept (9.6)

At the baseline every known shape is flagged in the widened grid, by the new
observers as well (`gen/recall9.py`):

| known | cells of the shape | flagged `DEFECT` | read-after / drop / leak / sentinel / read-now |
|---|---|---|---|
| DEF-99 | 348 | 224 | 45 / 51 / 71 / 57 / 0 |
| DEF-106 | 116 | 64 | 10 / 10 / 22 / 22 / 0 |
| DEF-102 (the pointer-receiver call on a loan included) | 305 | 175 | 32 / 29 / 70 / 44 / 0 |
| F-001 (a `for` over a slice parameter included) | 235 | 133 | 17 / 15 / 51 / 25 / 25 |
| DEF-104 | 36 | 22 | 2 / 4 / 12 / 4 / 0 |
| F-002 | 12 | 12 | 2 / 2 / 4 / 4 / 0 |
| DEF-105 | 14 | 4, and case 1's four refused controls | 0 / 0 / 2 / 2 / 0 |

### 10.5 The widened grid at both compilers (9.7; 4 jobs)

| class | baseline `c3bdae2` (340 s) | HUNT2 `9126350` (325 s) |
|---|---|---|
| refused | 2 584 | 3 500 |
| clean | 4 168 | 3 874 |
| `DEFECT:double_free` | 260 | 16 |
| `DEFECT:leak` | 214 | 149 |
| `DEFECT:leg_mismatch` | 149 | 0 |
| `DEFECT:uaf` | 109 | 6 |
| `DEFECT:wrong_value` | 46 | 24 |
| `DEFECT:segv` | 37 | 2 |
| `OVERRESTRICT` | 4 | 0 |
| `CRASH:npkc`, `timeout`, `other` | 0 | 0 |
| **total** | **7 571** | **7 571** |

Deduplication (`gen/dedup9.py`):
- At the baseline, **840 anomalies: 618 of known shapes** (DEF-99 224,
  DEF-102 175, F-001 133, DEF-106 44, DEF-104 22, F-002 12, DEF-105 8), and
  222 candidates.
- At HUNT2, which carries every fix, **197 anomalies, all candidates**. They
  fall into four families, with nothing left over, and each family is a
  finding below.

### 10.6 The findings

Each was taken through M5's five steps.
- **Minimised:** by `gen/minimize.py` where it came from a grid cell, with
  `--live` keeping a leak's reading, and by hand where it came from a probe.
- **Confirmed** twice at HUNT2 on both legs, and **run** at the baseline.
- **Written up** with controls in `findings/F-NNN-*/`.

"live" is the leak reading.

| id | shape | class | grid cells | HUNT2 `9126350` | baseline `c3bdae2` |
|---|---|---|---|---|---|
| [F-003](findings/F-003-consuming-pick-move-rules/) | a consuming `pick`'s binding escapes the move rules: a second move and a read after a move compile | **use-after-free, double free** | 44 | 0 / **95** / **95**; 0 / **70** / **70** (a local: `MOVE-001`) | the same |
| [F-004](findings/F-004-view-root-freed-through-callee/) | a view's root freed by a callee that moves the value out through `@x` or `$$i x` | **use-after-free** | probe | 0 / **70** / **70** (`$$m x`, an overwriting callee and a direct move: `BORROW-015`) | the same, as DEF-107 itself |
| [F-005](findings/F-005-store-through-pointer-leak/) | a store through a pointer, `(<-p) = v`, never frees the old value | **leak** | 121 | live **46** per store; 46 × N + 43 over N calls; an `OwnedFd` left open (26) | the same |
| [F-006](findings/F-006-consuming-pick-binding-not-dropped/) | a consuming `pick`'s named binding is never dropped at the arm's end | **leak** | 32 | live **46**, with an empty arm (the lending form, a moved-out binding and `_`: 0) | the same |
| [F-007](findings/F-007-to-cstring-leak/) | `to_cstring`'s buffer is never freed | **leak** | probe | `peak_live` = 10 × N (an owning `string`: 9) | the same |
| [F-008](findings/F-008-shared-claim-holder-write/) | a write through a `$$i` claim's holder compiles, where the reference's table names it `BORROW-013` | a rule not enforced (with a view it is F-004) | 40 | 0 / 22 / 22 (the root's write under `$$i`: `BORROW-013`) | the same |
| [F-009](findings/F-009-move-param-reinit-refused/) | a `move` parameter re-initialised after a move cannot be read | over-restriction, lower priority | 72 | 1, `MOVE-001` (a local: 22) | the same |
| [F-010](findings/F-010-lent-dyn-swap-refused/) | a swap through a lent `dyn`'s method is refused `BORROW-002` | over-restriction, lower priority; **new at HUNT2** | 12 | 1, `BORROW-002` | 0 / 22 / 22 |

- **Two memory faults at HUNT2**, F-003 and F-004. F-004 is a gap in DEF-107's
  fix: the fix refuses three spellings of the same free, and not a callee that
  moves out.
- **Three leaks**, F-005, F-006 and F-007, visible only to the new leak
  observer. **One claim rule not enforced**, F-008: with a view it is F-004's
  `$$i` spelling.
- **All but F-010 are old defects**, with identical verdicts at the baseline.
  F-010 is DEF-115's fix (1.6.1 step 0) refusing where no borrow exists.

### 10.7 The expectations the compiler did not meet, each explained

At HUNT2, **84 cells expected REFUSE were accepted**: F-003's 44 and F-008's
40.

**374 cells expected SAFE were refused:**
- 262 are `MOVE-001` by D-065's whole-binding rule. MEMORY_REFERENCE §1.1c:
  a move out of a part invalidates the root, and assigning the part does not
  re-initialise it. These are a swap or a move through a field, an element or
  a range. *The generator's reading was wrong; the rule is stated.*
- 72 are F-009.
- 28 are `TYPE-047` on `pass self.v` through a `Self->` receiver, whose
  message is "`pass` would hand the caller a copy". It is a refusal. *An
  observation:* the grid's `pass (<-x)` of a whole pointee is accepted and
  leaves the vacant value.
- 12 are F-010.

### 10.8 Observations for M10 and M11 (measured; not findings of this milestone)

- **`?` is not the `Result` fallback.** A bare `expr ? default` is
  `PARSE-011` (D-175: write `?|`). TYPE_REFERENCE §11.2's unwrap table, and
  MEMORY_REFERENCE §4.2's `get(h) ? 0i64`, still spell `?`. A documentation
  mismatch, for M11.
- **No string literal types as `cstring`.** `cstring:dn = "/dev/null";` and a
  literal passed to `open` are both `TYPE-007`. TYPE_REFERENCE §3.2.1 lists
  "string literal in `cstring` position" as a source. For M11.
- **`fd => int64` zero-extends.** A vacant `OwnedFd`'s `value` (−1, D-225)
  converts to 4 294 967 295. D-042 makes `fd` an `i32` and does not say
  whether it is signed. For M10's conversion checks.

### 10.9 What the widened grid still does not cover

**Places and types.**
- Views, beyond F-004's probe: the grid has no view place, and a view ×
  claim × callee cross is the natural next axis.
- Closures and function values, arenas and `Handle<T>`, channels, threads and
  `async` frames.
- `defer`, `when`, `Optional`, a `Result`'s `.value` as a place, `List<Box>`
  growth, and a nesting deeper than `h.v.s`.
- An array of, or a pointer to, a `dyn`, which has no spelling.

**Observers.**
- A `buffer`'s bytes are read only through pointer indexing, so `buffer` has
  no sentinel, and its read-after sees vacancy and length only.
- An `OwnedFd` closed twice at scope exit is silent: EBADF, unless another
  descriptor took the number between the two closes.
- No drop runs on a trap and failsafe's region is not counted, so the leak
  observer has no reading after a trap.
- The sentinel can prove reuse only while the freed block is still free when
  the sentinel is allocated.
- Section 7's remaining blind spots stand: one leg pair, one target, and
  exit-code comparison between the legs.

### 10.10 Cost, for calibration (the cloud VM, 4 jobs)

| step | time |
|---|---|
| LLVM 20.1.2 fetch, test and extract | 281 s (the download 10 s) |
| the two compiler builds | 52.5 s and 54.4 s |
| the M2 grid at both compilers (the machine check) | 41 s and 44 s |
| the widened grid, 7 571 cells | 340 s at the baseline, 325 s at HUNT2 (twice, with the superseded run) |
| the two shakedowns and the `OwnedFd` re-run | about 12 min |
| the minimiser, four cells in parallel | about 3 min (62–81 builds each) |
| the findings' programs, HUNT2 twice and the baseline once | about 3 min |

The session ran from 10:27 UTC to its last commit, which `PROGRESS.md`'s log
records.

### 10.11 Reproducing

```
python3 gen/grid9.py                     # cells9/, 7 571 programs (--selfcheck: the M2 programs byte-identical)
python3 gen/grid9_stats.py               # results/GRID9.md, the denominators
python3 gen/run.py .work/base  --cells cells9 --out results/c3bdae2/cells9.jsonl
python3 gen/run.py .work/hunt2 --cells cells9 --out results/9126350/cells9.jsonl
python3 gen/classify9.py results/9126350/cells9.jsonl
python3 gen/dedup9.py results/9126350/ --fixed DEF-99 DEF-102 DEF-104 DEF-105 DEF-106 F-001 F-002
python3 gen/recall9.py results/c3bdae2/  # the recall gate
python3 gen/run_findings.py F-003 F-004 F-005 F-006 F-007 F-008 F-009 F-010 --hunt .work/hunt2 --base .work/base --heap
python3 gen/snip.py FILE.npk --heap      # one program, both compilers, both legs
```

## 11. M10 — silent wrong answers

Written 2026-09-26 by session 5, on a fresh 4-vCPU cloud VM. Every number is
measured by the committed scripts. The records are:
- `m10/CHECKLIST.md` (the checklist) and `m10/RESULTS.md` (its results);
- `results/<commit>/m10.jsonl`, with run 1 as `m10-run1.jsonl`;
- `findings/F-011` … `F-017`, each with `VERDICTS.txt` and
  `VERDICTS-9f6f370.txt`.

The build record is in `PROGRESS.md`'s M10 section. **A silent wrong answer
counts as a defect** (`CLAUDE.md`, the author's rule of 2026-09-26): an
accepted program whose result differs from what the reference says, with no
memory error.

### 11.1 The compilers

- **The baseline `c3bdae2` and HUNT2 `9126350`** were rebuilt by M0's commands,
  byte-identical to sessions 3 and 4, with the commissioning check and the
  canaries passing.
- **The machine checks.** The M2 grid re-run on this VM is identical to the
  committed records in 956 of 956 cells at each compiler. The recall suite
  (`known/`, 25 programs since M9's merge) gives `KNOWN_DEFECTS.md`'s verdicts
  in every row (`results/<commit>/known-m10.txt`).
- **The compiler's newest `main`.** It moved during the session: `b564746` at
  11:57 UTC (1.6.1 step 0c, DEF-116's fix), then `9f6f370` at 12:29 (a record
  commit). HUNT2 stays `9126350`, the compiler PLAN.md 10.2 names (S32).
- `9f6f370` was built as well (88.9 s; `npkc.ll` 28 872 365 bytes, sha256
  `7bab110a1e45cc9d…`; canaries pass), but only to say whether each finding is
  still there (S37). No checklist verdict is taken from it.

### 11.2 The checklist (10.1)

`gen/m10.py` holds the checklist.
- **229 items in 17 areas**: PLAN.md 10.1's eleven features, plus shifts,
  precedence and evaluation, arrays and slices, floats, `exit`, and 10.3's
  DEF-108 recall.
- **Each item carries:**
  - the claim, in one sentence;
  - one or more quoted reference sentences;
  - the expected verdict, written from that text;
  - what an implementation that gets the claim wrong would answer, so every
    program is a case the wrong implementation gets wrong.
- **The citations are located by their text, not typed as line numbers.** All
  320 resolve to exactly one line of HUNT2's reference.
- **The same quotes were looked up at the baseline.** They are absent there
  only where the text changed since: FLOW-001's paragraph, the tag-only
  enum's cast, and the block string's closing sentence. For those items each
  compiler is held to its own reference's text (S33).
- **Sources read for it, at HUNT2:**
  - OP, CONTROL and BUILTIN_REFERENCE whole;
  - TYPE_REFERENCE §1–4, §6, §9–11 and §26–28;
  - LEXICAL_REFERENCE §5–6;
  - VERIFICATION_REFERENCE §1.2's `pick` and path-condition model;
  - SAFETY_ARCHITECTURE's `--extra-picky` table;
  - the decisions those cite (D-010, D-022, D-060, D-092, D-093, D-095,
    D-136, D-139, D-148, D-225, D-234, D-306).

**The program convention** (S34):
- exit 0 is the reference's answer, and 10–59 name the check that saw a wrong
  value;
- a trap exits its `failsafe` arm: the grid's codes plus `ShiftRange` 111,
  `CastRange` 112 and `BadStep` 113;
- a run-time value goes through a `never fails` identity function, so the
  compiler's folder cannot evaluate it;
- a folded value is a module `fixed` initialiser;
- where the reference speaks of both ("a constant expression means what the
  run time means"), there is an item for each.

**The expectations were committed before any program ran** (`a19c821`, S36).

### 11.3 The runs (10.2)

223 programs at each compiler, both legs, 4 jobs: about 25 s per compiler.

**Two programs were re-spelled after run 1, their expectations unchanged**
(S36):
- `m12` compared tbb values with `>`: ordering on tbb is refused (D-093);
- `d16` wrote fields directly into a struct declared without a value: refused
  by D-010, while D-225's `$$m` idiom is the one it serves.

Run 2 is identical to run 1 in the other 221 programs at both compilers, so
every verdict below was measured twice.

| | HUNT2 `9126350` | baseline `c3bdae2` |
|---|---|---|
| items | 229 | 229 |
| testable (a program each) | 223 | 223 |
| **agreeing** with the reference | **212** | **210** |
| **disagreeing** | **11** | **13** |
| … a program the text refuses, accepted | 1 | 2 |
| … a program the text admits, refused | 5 | 6 |
| … refused with another code | 1 | 1 |
| … a wrong exit on both legs | 4 | 4 |
| untestable, with a reason | 6 | 6 |

The baseline's two extra are known: DEF-101 (`c18`: its reference called
`intN =>! enum` impossible, and its compiler accepts it) and DEF-98 (`t04`: a
block string holding `""`).

**Every disagreement is accounted for** (`m10/RESULTS.md`), and nothing is
left unclassified:
- **4 items are silent wrong answers**: F-011, F-012 (two items), F-014;
- **2 are emitter refusals**: F-015, F-016;
- **5 are documentation findings** (F-017).

**Three items agreed and settled which of two contradicting sentences is
stale:**
- `!=` on floats is `une`;
- the ternary branches rather than `select`s;
- `int128` traps.

Those are F-017 d3–d5.

**By area.** Defaults and zero values (16), overflow (22), shifts (9), `when`
and `defer` (12), `Result` (10), precedence (7), arrays and slices (9), floats
(3) and `exit` (3) agree in every item at both compilers. The disagreements
fall in loops (4), strings (3), division (1), comparisons (1), `pick` (1) and
shadowing (1).

### 11.4 The DEF-108 recall (10.3)

| shape | M10 item | baseline `c3bdae2` | HUNT2 `9126350` |
|---|---|---|---|
| an empty body | `q01` | 0 / 10 / 10: returns 0 | refused `FLOW-001` |
| a missing path, `never fails` | `q02` | 0 / 10 / 10: returns 0 | refused `FLOW-001` |
| a fallible function's missing path | `q03` | 0 / 12 / 12: a success carrying 0 | refused `FLOW-001` |
| `main` without `exit` | `q04` | 0 / 0 / 0: falls off, exits 0 | refused `FLOW-001` |
| a `string` / `bool` function's missing path | `q05`, `q06` | 0 / 10 / 10: `""`, `false` | refused `FLOW-001` |
| a `NIL` function falling off | `q07` | 0 / 0 / 0 | refused `FLOW-001` |
| a `for` as the last statement, passing inside | `q11` | 0 / 0 / 0 | refused `FLOW-001` (loops complete as a whole) |
| controls: `while (true)` passing inside; an `if`/`else` and a `pick` whose arms all pass | `q08`–`q10` | 0 / 0 / 0 | 0 / 0 / 0 (not refused) |

`known/def108_fall_off/`'s two cases give the same: 0/10/10 and 0/12/12 at
the baseline, `FLOW-001` at HUNT2, with the control 0/0/0 at both. **So the
recall holds:** every DEF-108 shape the plan names is flagged at the
baseline, where it answers a zero value, and refused `FLOW-001` at HUNT2.
The flow rule's three stated exceptions are not over-refused.

### 11.5 The findings

Each was taken through M5's five steps:
- deduplicated against `KNOWN_DEFECTS.md` (none is known);
- written small with its controls;
- confirmed twice at HUNT2 on both legs (the runs agree);
- run at the baseline;
- run at `9f6f370`.

**Every finding is present at all three compilers with the same verdicts: old
defects, not regressions.**

| finding | shape | class | HUNT2 `9126350` = baseline = `9f6f370` |
|---|---|---|---|
| [F-011](findings/F-011-for-binding-outlives-loop/) | a `for` binding outlives its loop in the emitter: after `int64:i = 100; for (int64:i in 0...3) {…}`, `i` reads the loop's slot | silent wrong value; **out-of-bounds read**; invalid IR | same type 0/**10**/**10** (reads 3); an outer `int32[4]` read at [3] 0/**11**/**10** (past a 4-byte slot, the legs differ); an outer `string`: npkc 0, `llc`/`opt` reject the IR |
| [F-012](findings/F-012-for-range-head-signed-and-wrapping/) | a `for` range runs zero times at its type's edges | silent wrong answer | `int8 125..127`, `0..127`, int32/int64 `…..max`: 0 trips; `uint8 100..200`, `100...200`, uint32 across 2^31: 0 trips (0/**10**/**10** each) |
| [F-013](findings/F-013-counted-loop-unsigned-bound-sign-extended/) | `loop`/`till` sign-extend an unsigned bound | silent wrong answer; a spurious trap | `loop(100u8, 200u8, 1u8)`: 156 trips, `$` 100 → -55; `till(200u8, 1u8)`: 56 trips, `$` 0 → -55; a uint32 `loop` across 2^31: `IntOverflow` (93) |
| [F-014](findings/F-014-till-negative-limit-counts-down/) | `till` with a negative limit counts down | silent wrong answer | `till(-3, 1)`: 3 trips, `$` 0, -1, -2, where the reference says zero |
| [F-015](findings/F-015-spaceship-not-lowered/) | `<=>` refused by the emitter | the compiler's `EMIT-002` (lower priority) | 1, `EMIT-002`, even for `1i32 <=> 2i32` |
| [F-016](findings/F-016-negative-range-pattern-not-lowered/) | a `pick` range pattern with a negative bound refused by the emitter; where DEF-35's fix did not reach | the compiler's `EMIT-002` (lower priority) | 1, `EMIT-002`; `(-3i32)` and `(2i32..5i32)` compile |
| [F-017](findings/F-017-reference-sentences-the-compiler-contradicts/) | seven reference sentences the compiler contradicts | documentation | d1 `s.length` → `TYPE-019`; d2 `s[i]` → `TYPE-007`; d3 §28's `fcmp one` (it is `une`); d4 §28's ternary `select` (it branches); d5 §4's wrapping wide integers (they trap); d6 `TYPE-033` (it is `TYPE-007`); d7 a local constant `/ 0` accepted, trapping at run time |

**How they were found.**
- The checklist pointed at F-011 (`h02`), F-012 (`l06`, `l08`), F-014
  (`l11`), F-015 (`m06`), F-016 (`p05`) and F-017. The emitted IR and probes
  then measured each shape's extent.
- F-013 and F-012's unsigned face were found by probes that followed the IR:
  its loop tests are `icmp slt` for every type, and a counted loop's bounds
  are widened by `sext`.
- The checklist's own unsigned item (`l07`, `250..255`) agreed by a
  coincidence F-012's third control explains. *Inferred:* an item at one
  edge is not enough, and the crossing needs its own item.

**The mechanisms, read from HUNT2's `src/backend/ir/ir_stmt.npk`, not
measured:**
- `emit_for` binds its loop variable with `fnem_local` in the enclosing scope
  (F-011);
- its range head is the literal text `icmp slt`, and the inclusive range
  arrives as an unchecked `hi + 1` (F-012);
- `loop_i64` widens a counted loop's bounds with `sext`, whatever their
  signedness (F-013);
- `emit_counted` infers a direction for `till` as for `loop` (F-014).

Each finding's README keeps what was measured apart from what was read.

### 11.6 What the checklist does not cover

- **The six untestable items** (`m10/RESULTS.md`): no sentence states the
  answer for
  - a vacant `OwnedFd`'s conversion;
  - `?|`'s laziness;
  - a same-scope redeclaration;
  - a float's text;
  - `k =>! Enum` for a value that is no tag;
  - the library's `**`.
- **Items that rest on inference rather than a stated sentence**, marked in
  `CHECKLIST.md`:
  - shadowing's default (`h01`–`h04`), read from SAFETY_ARCHITECTURE's
    optional rule;
  - an empty inclusive range `3..1`;
  - `loop`'s steps other than 1;
  - an unwritten field (`d11`);
  - `bool` ordering;
  - left associativity.

  Each is a reading of the text, and two of those readings found defects
  (F-011's `h02`, and F-014 through the stated table).
- **Reference text not read for this milestone:** TYPE_REFERENCE §5, §7, §8
  and §12–25 (`tfp`, `dim256`, the ternary kinds, flags, arenas, atomics,
  `simd` beyond one item, `dyn`, `frac`, `complex`, `buffer`), and MEMORY,
  MODULE, TRAITS, IO, MACRO, CONCURRENCY, BUILD, AST and most of
  VERIFICATION. That is M11's reading, every normative claim of every
  reference.
- **Features with no item:**
  - generics and traits;
  - closures and function values;
  - `async`, threads and channels;
  - formatting beyond integers;
  - `Optional` beyond `??`/`?.`;
  - enums with payloads;
  - the verified build (`prove`, contracts, `limit`), whose meaning is a
    solver's verdict and not an exit code.
- **The observer is the exit code.** An item sees a wrong value only where its
  checks compare it. A wrong value no check reads, a leak (M9's observer was
  not used here), or a trap routed to the right code for the wrong reason is
  not seen. F-011's out-of-bounds WRITE was probed and not seen to corrupt a
  live local, which is a limit of the observer, not evidence that nothing is
  overwritten.

### 11.7 Cost, for calibration (the cloud VM, 4 jobs)

| step | time |
|---|---|
| LLVM 20.1.2 fetch, test and extract | 383 s (the download 15 s) |
| the two compiler builds | 90.8 s and 91.7 s (and `9f6f370`, 88.9 s) |
| the M2 grid at both compilers (the machine check) | 73 s and 78 s |
| the checklist, 223 programs | 25–26 s per compiler per run, four runs |
| the findings' programs (46), HUNT2 twice and the baseline once | 67 s (the two runs at `9f6f370` were not timed) |

The session ran from 11:57 UTC to M10's last commit at 12:53: 56 minutes, of
which about 19 were compute (the rows above, plus probes). The rest went into
reading the references, writing the checklist, and triage.

### 11.8 Reproducing

```
python3 gen/m10.py                       # m10/programs/, EXPECT.tsv, CHECKLIST.md (--refs-only: the citations at both compilers)
python3 gen/m10_run.py .work/hunt2       # results/9126350/m10.jsonl, one named line per program
python3 gen/m10_run.py .work/base        # results/c3bdae2/m10.jsonl
python3 gen/m10_report.py                # m10/RESULTS.md, the denominators and every disagreement
python3 gen/run_findings.py F-011 F-012 F-013 F-014 F-015 F-016 F-017 --hunt .work/hunt2 --base .work/base
python3 gen/run_known.py .work/hunt2     # the recall suite, DEF-108's known cases among it
```

## 12. M11 — the reference, checked against the compiler

Written 2026-09-26 by session 7 and extended by sessions 8 and 9 (2026-10-02), all on
the author's machine (48 cores), from the committed scripts. **Every one of the fourteen
references is extracted: all 10 419 lines.** Session 8 corrected the count, which had
included the empty element after each file's final newline (10 433 before):
- BUILTIN, CONCURRENCY, IO and MACRO by sessions 6 and 7;
- MEMORY, OP and CONTROL by session 8;
- MODULE, LEXICAL, AST, BUILD, TRAITS and VERIFICATION's rest by session 9;
- TYPE: 1–660 by session 7, 661–2122 by session 9 in three parts (S65).

The records are:
- `m11/CLAIMS.md` (every claim with its line, quote and expectation) and
  `m11/RESULTS.md` (the results, claim by claim);
- `results/9126350/m11.jsonl` (the final run), with runs 1–3 beside it;
- `results/c3bdae2/m11-disagree.jsonl`, `results/1b4f0c6/m11-disagree.jsonl` (session 7)
  and `results/93bcb66/m11-disagree.jsonl` (sessions 8 and 9): the disagreeing claims at
  the baseline and at the compiler's newest `main` of each session;
- `gen/m11_triage.py` (the class of each disagreement);
- `findings/F-018` … `F-048`.

### 12.1 The denominators

Every reference line number in the findings and results is a line of the reference at HUNT2 `9126350`. The references have moved since (for example `MEMORY_REFERENCE.md`'s `wildx_alloc` example is at line 168 at HUNT3 `0c0f5a3`, not 126); find a sentence by its quoted text.

| reference | claims | examples | rows | rules | untestable | testable = tested | agree | disagree |
|---|---|---|---|---|---|---|---|---|
| AST | 202 | 8 | 116 | 78 | 21 | 181 | 151 | 30 |
| BUILD | 97 | 4 | 26 | 67 | 59 | 38 | 38 | 0 |
| BUILTIN | 227 | 2 | 109 | 116 | 33 | 194 | 182 | 12 |
| CONCURRENCY | 152 | 11 | 21 | 120 | 30 | 122 | 101 | 21 |
| CONTROL | 110 | 14 | 7 | 89 | 2 | 108 | 98 | 10 |
| IO | 78 | 5 | 9 | 64 | 11 | 67 | 60 | 7 |
| LEXICAL | 184 | 9 | 34 | 141 | 3 | 181 | 170 | 11 |
| MACRO | 124 | 13 | 34 | 77 | 5 | 119 | 98 | 21 |
| MEMORY | 181 | 10 | 11 | 160 | 35 | 146 | 137 | 9 |
| MODULE | 139 | 7 | 3 | 129 | 15 | 124 | 109 | 15 |
| OP | 159 | 0 | 87 | 72 | 2 | 157 | 148 | 9 |
| TRAITS | 119 | 19 | 16 | 84 | 4 | 115 | 99 | 16 |
| TYPE | 897 | 47 | 237 | 613 | 50 | 847 | 745 | 102 |
| VERIFICATION | 716 | 11 | 146 | 559 | 243 | 473 | 451 | 22 |
| **total** | **3 385** | 160 | 856 | 2 369 | **513** | **2 872** | **2 587** | **285** |

Untestable, each with its reason in `m11/CLAIMS.md`:
- `z3` 117: needs `npkg verify` with the pinned z3;
- `vague` 69: no checkable outcome;
- `internal` 77 (AST's 19 are rows that list only a node's fields);
- `tree` 75: the compiler's own tree;
- `tool` 135: a running driver process, a package in the compiler's tree, `npkg test`, which
  builds the compiler first (BUILD's 28), or the verified build's runners, floor
  translator, protocol models and schedule explorer (VERIFICATION 1248–2351's 87);
- `unobservable` 29;
- `timing` 8;
- `platform` 3.

Every expectation was written from the reference's text before its program first ran.
Session 6 drafted five of the six modules with sub-agents. Session 7 reviewed them
before their first run (PROGRESS.md S51). **59 programs** changed their text after a
run, for a mistake of their own: 21 of BUILTIN's in session 6, and 38 in session 7 (26
of them one mistake in `verif1`'s scripts, reading `main`'s rows as `<module>.main` where
the symbol is `@main`: 25 through one shared helper, S53). The expectation stayed, except
one under S45's recorded exception (`cc0636`). Each change carries its reason (`fixed`,
listed in `m11/RESULTS.md` §3). Session 7's run 1 gave 1 093 agree and 169 disagree;
its final run gives 1 118 and 144. Sessions 8 and 9 changed 21 and 30 more programs the
same way. AST's 2 were a borrow live at a read and a `move` of a call's `Result`.
BUILD's 1 was a script that took a diagnostic's note for its error's place. TRAITS' 12
were a generic struct literal's spelling (10: `Box{ … }`, never `Box<int32>{ … }`), a `pub`
field and an impl's generic method (S55). LEXICAL's 4 were a contract measure calling a helper, a `%%` left in a check,
and a generic identity passing out its lent parameter (2). MODULE's 24 were three
mistakes:
- `hidden`, a reserved word (14);
- `nbridge.npk`'s import of `nsys.npk`, which the scripts did not copy (9);
- failsafe arms that REACH-002 asks for (8, seven of them also among the nine).

### 12.2 The disagreements, by class

| class | claims |
|---|---|
| compiler: a silent wrong answer (F-018 … F-021; **TYPE's F-047, a `fixed` byte view written through**) | 6 + 1 |
| compiler: memory — a use after destroy (F-022); **a use after free through a `=> dyn` cast (AST's F-037)** | 1 + 1 |
| compiler: accepted, then invalid IR (F-023; TYPE's F-048) | 1 + 1 |
| compiler: npkc traps, exit 3 (F-024; AST's F-038) | 4 + 3 |
| compiler: npkc does not terminate (TRAITS' F-041) | 1 |
| compiler: a flag that refuses every program (F-025) | 2 |
| compiler: a unit annotation accepted and ignored (F-026, and in TYPE §19) | 1 + 1 |
| compiler, lower priority (F-027; MODULE's F-034; LEXICAL's F-036; AST's F-039; TRAITS' F-042; TYPE's F-046) | 16 + 5 + 4 + 4 + 1 + 2 |
| documentation (F-028; MEMORY's F-030; OP's F-031; CONTROL's F-032; MODULE's F-033; LEXICAL's F-035; AST's F-040; TRAITS' F-043; TYPE 661–2122's F-044; the backward pipe, AST's F-039 b and TYPE's F-046 c, reclassified in M12, FZ-7) | 94 + 8 + 5 + 6 + 7 + 6 + 18 + 13 + 33 + 2 |
| known (DEF-123, DEF-131, DEF-133; MEMORY's DEF-148; OP's DEF-131 twice; CONTROL's DEF-133, DEF-130 twice, DEF-135; MODULE's DEF-153; LEXICAL's DEF-131; AST's DEF-131 and DEF-153; TYPE's DEF-131) | 7 + 1 + 2 + 4 + 1 + 1 + 2 + 1 |
| not a finding: refused at compile time where the text says it traps | 2 |
| not a finding: the program tests more than its sentence, or cannot be written | 10 + 2 (OP) + 2 (MODULE) + 1 (AST) + 1 (TRAITS) + 1 (TYPE 661–1176) |
| **total** | **285** |

**Every disagreement fails at the baseline too, though three give a different result there**:
`cc0042` (other codes), and `tr0404` and `tr0435` (both compiled at the baseline, npkc 0 and 0/0,
and are refused at HUNT2). So each is old. Session 7's all stand at its newest `main` `1b4f0c6`. Session 8's
MEMORY, OP and CONTROL rows all stand at `93bcb66` but six, all known: `me0461`,
DEF-148's shape, is refused there (`BORROW-016`); OP's two `<=>` claims (DEF-131)
compile and run; and CONTROL's DEF-130 pair and DEF-135 agree there. MEMORY's run 1 also found F-029, a reserved word accepted as a binding's
name, which no final disagreement carries, since the programs it broke were
re-spelled. Session 9's MODULE rows all stand at the baseline and at `93bcb66` but one,
known: `md0296b`, DEF-153's string literal in `cstring` position, compiles at `93bcb66`.
LEXICAL's all stand at both but one, known: `lx0178`, DEF-131's `<=>`, compiles and runs
at `93bcb66`. AST's all stand at both but its two known, which compile at `93bcb66`.
TYPE 661–2122's all stand at both but two, both fixed at `93bcb66`:
- `ty2038`, DEF-131's `<=>`, compiles and runs;
- `ty1598`, F-026's shape on `int32`, is refused (TYPE-016), and so is F-026's own
  `tfp64<Meters>` (`ty0553`, re-run there).

**AST's run found the session's one memory fault, F-037.** A trait object built by an
explicit cast, `x => dyn Trait`, points at freed storage, and its method reads the
allocator's poison (0xAA in every byte). This holds at HUNT2, the baseline and `93bcb66`,
on both legs. The implicit coercion `dyn Trait:d = move(x);` is correct. It also found a
second npkc trap shape, F-038: `give` or `fall` outside a pick arm. TRAITS' run found
F-041: npkc never terminates on an unbounded generic instantiation (300 s, 4.4 GB, at all
three compilers), where the reference caps the depth at 64. TRAITS' rows all stand at
`93bcb66`. Two of its examples compiled at the baseline and no longer do.

**TYPE 661–2122's run found a silent wrong answer, F-047.** A `fixed uint8[]` is the
reference's immutable byte view (TYPE:1719, D-074), yet a write through it is accepted and
lands. That includes a callee's write through its `fixed` parameter, so the caller's bytes
change. It holds at all three compilers, on both legs, with two controls. Part C also
found F-048, a `NIL` struct field emitted as LLVM `void`, which `llc` and `opt` refuse. It
also found three safe departures, F-046. Part B's screening found F-045: the compiler's
own message for `??` on a `Result` advises the bare `?`, which D-175 retired.

### 12.3 The findings

| id | shape | class | HUNT2 | baseline | `1b4f0c6` |
|---|---|---|---|---|---|
| F-018 | a macro's free name, alone or a comparison's operand, reads the call site's local | silent wrong answer | 0, 10/10 | the same | the same |
| F-019 | a `\u{…}` escape is a `char8`, truncated to its low byte (`'\u{1F641}'` is `'A'`); a `char32` refuses it | silent wrong answer | 0, 10/10; `char32`: 1 | the same | the same |
| F-020 | the join relays the last-spawned child's error, not the first child error | silent wrong answer | 0, 10/10 | the same | the same |
| F-021 | a `timedwait` expiring with no signal reports success | silent wrong answer (an error path becomes a success) | 0, 10/10 | the same | the same |
| F-022 | a shared arena destroyed while a spawned thread holds it; the program ends in `WildLeak` | memory: use after destroy | 0, 96/96 | the same | the same |
| F-023 | an un-awaited async method call is accepted and emits a call to an undefined symbol | compiler: invalid IR | 0, llc!1/opt!1 | the same | the same |
| F-024 | npkc traps (exit 3, no message) on a macro emitting a method into an impl, a 500-deep expression, a macro emitting a comptime function | compiler crash | 3 | 3 | 3 |
| F-025 | `--extra-picky=no-wildx` refuses every program (256 `WILDX-003` in the prelude) | compiler: a flag unusable | 1 | 1 | 1 |
| F-026 | `tfp64<Meters>` accepted and its unit ignored: Meters + Seconds compiles (TYPE §19's `int32<Meters>` too) | compiler: a refusal missing | 0, 10/10 | the same | the same; both refused at `93bcb66` |
| F-027 | sixteen safe departures: accepted though refused, a named hole, refused though permitted, a diagnostic | compiler, lower priority | per row | the same | the same |
| F-028 | ninety-four reference sentences the compiler contradicts, the compiler right or safe | documentation | per row | the same | the same |
| F-029 | the reserved word `buffer` is accepted as a `wild` pointer binding's name, then unusable (`PARSE-002` at the use) | compiler, lower priority | 0, 3/3; use: 1 | the same | the same (at `93bcb66`) |
| F-030 | MEMORY's eight stale sentences (examples, a struck rule, the arena leak) | documentation | per row | the same | the same (at `93bcb66`) |
| F-031 | OP's five stale sentences (no `**`, the ternary and pipe examples, line 171's `?`) | documentation | per row | the same | the same (at `93bcb66`) |
| F-032 | CONTROL's six stale sentences (`println`, the macro pattern, three codes never emitted, `ok()`) | documentation | per row | the same | the same (at `93bcb66`) |
| F-033 | MODULE's seven stale claims (`pub const`, the `cuda_driver` example, the wire vocabulary beyond D-190's v1, `raw` on a driver method) | documentation | per row | the same | the same (at `93bcb66`) |
| F-034 | MODULE's safe departures: a byte payload's driver stub refused (TYPE-072 in the generated code), `use m.f;` refused against D-273, a cycle's diagnostic that names no cycle | compiler, lower priority | per row | the same | the same (at `93bcb66`) |
| F-035 | LEXICAL's six stale claims (`++`/`--`, `sys_full`, the `f128` suffix, `0u64 - 1u64`, the dead LBIM note) | documentation | per row | the same | the same (at `93bcb66`) |
| F-036 | LEXICAL's safe departures: `acquire`, `any`, `trit`, `nit` still name an uncallable function (DEF-103's residue), a literal's trailing underscore accepted | compiler, lower priority | per row | the same, and more words | the same (at `93bcb66`) |
| F-037 | a trait object built by `x => dyn Trait` reads freed memory: the method returns the 0xAA poison | **memory: use after free** | 0, 10/10 | the same | the same (at `93bcb66`) |
| F-038 | npkc traps (exit 3, no message) on `give` or `fall` outside a pick arm | compiler crash | 3 | 3 | 3 (at `93bcb66`) |
| F-039 | AST's safe departures: a `comptime` value parameter EMIT-002, the backward pipe's function on the right, a non-constant `joins`, any attribute name accepted, an `opaque struct` outside an extern block | compiler, lower priority | per row | the same | the same (at `93bcb66`) |
| F-041 | npkc does not terminate on an unbounded generic instantiation (no exit in 300 s, 4.4 GB), against the reference's depth cap of 64 | compiler: hang | no exit | no exit | no exit (at `93bcb66`) |
| F-042 | TRAITS' safe departure: an `opaque struct` accepted outside an extern block (as F-039 e) | compiler, lower priority | per row | the same | the same (at `93bcb66`) |
| F-043 | TRAITS' thirteen stale claims (eleven examples, the field visibility sentence, the lambdas sentence) | documentation | per row | the same, two compiled | the same (at `93bcb66`) |
| F-040 | AST's eighteen stale claims (retired spellings, the error model before D-179, the extern rows before D-149, and four more) | documentation | per row | the same | the same (at `93bcb66`) |
| F-044 | TYPE 661–2122's thirty-three stale or ambiguous claims (§6's tbb alignments, the failsafe signature, the `42` = `1T1T0t` example, the struct example, the field-access IR, "never up" for a slice, `#wild_slice`'s wild context, `--guard-pages`, the bare `?`, the extern example, the arena cast, §15's library layouts, the elided-Result IR, frac's and complex's `ToString`, `void`, §28's IR columns, `**`, `string_eq`, `ptr->field`) | documentation | per row | the same | the same (at `93bcb66`) |
| F-045 | the compiler's message for `??` on a `Result` advises the bare `?`, which it refuses (PARSE-011, D-175) | compiler, lower priority: a diagnostic | TYPE-007, then PARSE-011 | the same | the same (at `93bcb66`) |
| F-046 | TYPE's safe departures: a frac member assigned (EMIT-002), a `fixed` parameter reassigned, the backward pipe (F-039 b) | compiler, lower priority | per row | the same | the same (at `93bcb66`) |
| F-047 | a `fixed uint8[]` view is not immutable: a write through it lands, a callee's through a `fixed` parameter included | **silent wrong answer** | 0, 10/10 | the same | the same (at `93bcb66`) |
| F-048 | a struct with a `NIL` field is accepted and emitted as `{ i32, void }` | compiler: invalid IR | 0, llc!1/opt!1 | the same | the same (at `93bcb66`) |

### 12.4 What these claims do not cover

- **No range is left unextracted.** What a claim cannot test is listed above with its
  reason (the untestable tags).
- **VERIFICATION 1248–2351 is mostly the verified build's own machinery.** 115 of its 131
  claims need z3 or the runners. Its 16 tested claims (what `npkc --obligations` writes,
  the trap spellings, the stack's prologue and notes) all agree.
- **BUILD's own process.** 59 of BUILD's 97 claims are the compiler's ladder, its test
  runners and its verified build, which a scratch project cannot reach (`npkg build` reads
  the compiler tree's `runtime/npkrt.ll`). Its 38 tested claims are `npkg`'s refusals
  before a build, the `[[test]]` schema and stage names, and what `npkc` emits. All 38
  agree.
- **The verified build.** 117 claims need `npkg verify` with the pinned z3, and are
  untestable here. Claims about what the compiler writes for verification were tested
  through `npkc --obligations`, which needs no z3.
- **A program per claim.** One agreeing program shows the claim for that program, not
  for every program. The refusals that agreed were screened for a first diagnostic of
  another kind (a parse, lex, resolve or reach error). One was found (`mc0312b`), and
  it now agrees for its own reason. Sessions 8 and 9 screened theirs the same way and
  found four more (`me0179`, `ct0032f`, `md0099b`, `md0273`), each re-spelled.

## 13. M12 — the re-baseline at HUNT3

M12 is the task the author and the workbench chose after M11 (PLAN.md ends there; S66): every record
re-run at the compiler's current `main`, and every move from HUNT2 explained. It ran on 2026-10-15,
on the Team seat, on branch `local-m12`, one harness at a time under the seat's lock, at 4 jobs.

### 13.1 The compilers and the toolchain

| role | commit | LLVM | build | `npkc.ll` bytes / sha256 | `npkrt.o` | `npkc` |
|---|---|---|---|---|---|---|
| baseline | `c3bdae2` | 20.1.2 | 74.6 s | 28 111 929 / `4029fc70efbe9cd3…`, as committed | 72 576 / `162b897539285a77…` | 9 724 160 / `5fd636b9ab557c19…` |
| HUNT2 | `9126350` | 20.1.2 | 72.7 s | 28 857 206 / `2448b3b60d9eb189…`, as committed | 72 576 / `162b897539285a77…` | 9 972 872 / `c7212b6be06fe6a4…` |
| HUNT3 | `0c0f5a3` (`0c0f5a39fcd2a54e78bf7409add841cbc16927b7`) | 20.1.8 | 55.2 s | 31 701 272 / `f520d5744b1e9951…`, equal to notice 113's ladder row | 72 656 / `c8e5033ad17c70f8…`, equal | 11 283 680 / `02e7b06321a16950…`; the row's is 72 bytes shorter, its linker comment (reasoned) |

- **HUNT3** is the compiler's `origin/main` at the session's fetch (16:43 EDT): landing 113 (DEF-235,
  DEF-236 (c)(d)(e), DEF-237, DEF-234 (c)) over landing 112 (DEF-232, this repository's F-048). It
  carries neither 114 nor 115: DEF-250 and DEF-251 are OPEN in its registry (S68). Its ladder row is
  notice 113's as the workbench's BOARD transcribes it; HUNT3's own NOTICES rows carry no digests.
- **LLVM 20.1.2** is the machine's `/usr/lib/llvm-20` (S48). **LLVM 20.1.8** is the release tarball
  `LLVM-20.1.8-Linux-X64.tar.xz`, 2 021 269 412 bytes, sha256
  `1ead36b3dfcb774b57be530df42bec70ab2d239fbce9889447c7a29a4ddc1ae6`, fetched in S13's form; no reference
  digest exists for it. Every runner names its LLVM (S70).
- **The author's go** (S67): management_0's recommendation 6 — "run it on the Team seat after 113 lands.
  It needs your go to switch to LLVM 20.1.8" — and the author's answer, "all the recommendations look
  fine to me. Lets go with those." LLVM 20.1.8 is in its words; HUNT3 is management's reading of "after
  113 lands", recorded as such.
- The canaries pass at all three compilers, and at the two built for the bisection (13.11).

### 13.2 The landing-103 spelling and the shakedown

From landing 103 `string_bytes` returns `fixed uint8[]`, which never converts back to a plain `uint8[]`
(`TYPE-007`, D-351). Before any HUNT3 run the corpus was re-spelled in its own commit (S71): three
generator lines (`grid.py` and `grid9.py`'s observer, `m10.py`'s `t07`) and 53 lines in 48 hand-written
programs (5 in `known/`, 43 in `findings/`). M11's six generated programs that bind a plain `uint8[]`
are left for Option C.

**The shakedown**, under 20.1.2 into scratch, is identical cell for cell at both old compilers:

| record | `c3bdae2` | `9126350` |
|---|---|---|
| M2 grid, 956 cells | 0 moved | 0 moved |
| M9 grid, 7 571 cells, heap words included | 0 moved | 0 moved |
| recall, 25 rows | identical | identical |
| M10, 223 programs | 0 changed | 0 changed |
| the ten findings holding a re-spelled file | line for line | line for line |

The grid statistics regenerate byte-identical to `results/GRID.md` and `GRID9.md`. Two comparers were
written for it and kept: `gen/compare.py --grid9` (S72, additive, checked byte for byte) and
`gen/compare_runs.py` (S73).

### 13.3 The LLVM control

`9126350` re-run under 20.1.8 against its own records, which were measured under 20.1.2: recall 25 of
25 identical, M2 956 cells 0 moved, M9 7 571 cells 0 moved with the heap words, M10 223 programs 0
changed, M11 2 872 claims 0 changed. **0 cells moved by the toolchain**, so every move at HUNT3 is the
compiler's. No BUILD claim moved, so the pin refusal the brief foresaw (P32) does not arise. Of the 23
shell scripts with a `[toolchain]` section (`/usr/bin/grep -l '\[toolchain\]' m11/programs/*.sh`), two,
`bd0075` and `bd0299`, reach npkg's toolchain check by design and print its refusal under either LLVM;
`bd0299`'s own message, "ld.lld is 20.1.8 but nitpick.toml pins 20.1.1", shows the scripts ran with
20.1.8. *(Corrected in M13, M12v's finding (1): this said no BUILD claim reaches the check, and named 21
scripts.)*

### 13.4 Recall and findings at HUNT3

**Recall:** 25 rows, every one "once fixed": 19 by `gen/check_known_fixed.py`, DEF-106's and DEF-108's
six by hand (`TYPE-086` twice, `FLOW-001` twice, both controls 0/0). Identical to `9126350`'s record.

**Findings** (`findings/F-0NN-*/VERDICTS-0c0f5a3.txt`: HUNT3 twice and the baseline once, under 20.1.8;
the HUNT3 runs agree for every program; every baseline line equals the committed one):

| F | DEF | landing | HUNT3 | baseline `c3bdae2` |
|---|---|---|---|---|
| F-001, F-002 | faces of DEF-102, DEF-104 | 59 (step 3g) | refused `TYPE-085`, `TYPE-047`; controls as recorded, `ctl_gen_move_param` 21/21 | as committed |
| F-003 | DEF-118 | 74 | `MOVE-001` | as committed |
| F-004 | DEF-119 | 74 | `BORROW-015`, `BORROW-013` | as committed |
| F-005 | DEF-120 | 76 | live 0; the descriptor closed | as committed |
| F-006 | DEF-121 | 76 | live 0 | as committed |
| F-007 | DEF-122 | 78 | peak 10, not 10 × N | as committed |
| F-008 | DEF-123 | 74 | `BORROW-013` | as committed |
| F-009, F-010 | DEF-124, DEF-125 | 79 | 22/22; 0/22/22 | as committed |
| F-011 | DEF-127 | 74 | 0/0 | as committed |
| F-012, F-013, F-014 | DEF-128, DEF-129, DEF-130 | 75 | 0/0 | as committed |
| F-015, F-016 | DEF-131, DEF-132 | 79 | 0/0; 4/4 | as committed |
| F-017 | DEF-133 | 79 | `d7` `TYPE-004`; the six sentences' programs unmoved (the references were corrected) | as committed |
| F-018, F-019, F-021 | DEF-144, DEF-145, DEF-147 | 77 | agree | as committed |
| F-020 | DEF-146, under D-334 | 77 | `j1` 0/0; **the control `ctl_j3` now 10/10** | as committed |
| F-022 | DEF-148 | 77 | `BORROW-016` | as committed |
| F-023 | DEF-149 | 80 | `TYPE-043` | as committed |
| F-024 | DEF-150 | 80 | `PARSE-001` (c1's `$$i` receiver), `PARSE-012`, 0/0 | as committed |
| F-025 | DEF-151 | 80 | `run.sh`, twice: the flag accepts the program | `run.sh`: 256 × `WILDX-003`, as at `9126350` |
| F-026 | DEF-152 | 80 | `TYPE-016` | as committed |
| F-027 | DEF-153 | 78, 83, 90 | 15 of its 16 claims agree; `mc0085b` is a documentation row by DEF-153's record | claims |
| F-028 | DEF-154 | OPEN | none of its 94 claims moved | claims |
| F-029 | DEF-235 | 113 | `k1` `PARSE-001`; `k2` `PARSE-001` beside its `PARSE-002` | as committed |
| F-030 … F-033, F-035, F-040, F-043, F-044 | DEF-239 | OPEN | none moved but `me0183`'s code (113); F-044's frac row `ty1657` agrees (DEF-231, 97) | claims |
| F-034 | DEF-234 | (c) 113; (a)(b) OPEN | (c) agrees | claims |
| F-036 | (a) DEF-235; (b) DEF-190 | 113; OPEN | (a) agrees; (b) unmoved | claims |
| F-037 | DEF-227 | 94 | 0/0: it answers 7 | as committed |
| F-038 | DEF-233 | 111 | `TYPE-094`; `ctl_c3` 0/0 | as committed |
| F-039, F-042 | DEF-236 | (c)(d)(e) 113; (a) OPEN | (c)(d)(e) agree; (a) unmoved; (b) a documentation row | claims |
| F-041 | DEF-229 | 96 | `TYPE-018` in 0.09 s | as committed (the 120 s timeout) |
| F-045 | DEF-237 | 113 | `TYPE-007`, its advice naming `?!`/`?|` | as committed |
| F-046 | (a) DEF-238; (b) DEF-248 | 111; 102 | both agree; (c) a documentation row | claims |
| F-047 | DEF-230 | 98, 103 | `TYPE-086`; the controls as recorded | as committed |
| F-048 | DEF-232 | 112 | 0/0; `ctl_n3` 0/0 | as committed |
| **F-049** (new) | — | (74) | `MOVE-001`; its local control 22/22 | 22/22, the right answer |

**Every memory finding (F-001 … F-008, F-011, F-022, F-037, F-047) gives its fixed verdict at HUNT3**,
and no HUNT3 line exits 70, 95, 107 or 139. The fifteen row findings get a header-only
`VERDICTS-0c0f5a3.txt`: their programs are M11's claims (13.8).
*Erratum (M13, M12v's finding (7)):* those fifteen files' line "HUNT runs agree for every program: yes" is
said of zero programs; the files are kept as the records the command wrote, and from M13
`gen/run_findings.py` writes no file for a finding with no programs.

### 13.5 The M2 grid

| class | `c3bdae2` | `9126350` | HUNT3 `0c0f5a3` |
|---|---|---|---|
| clean | 612 | 562 | 562 |
| refused | 230 | 394 | 394 |
| `DEFECT:double_free` | 56 | 0 | 0 |
| `DEFECT:leg_mismatch` | 25 | 0 | 0 |
| `DEFECT:uaf` | 22 | 0 | 0 |
| `DEFECT:segv` | 5 | 0 | 0 |
| `OVERRESTRICT` | 4 | 0 | 0 |
| `DEFECT:wrong_value` | 2 | 0 | 0 |
| **generated** | **956** | **956** | **956** |

No cell moved from `9126350` (`results/0c0f5a3/MOVES.md`).

### 13.6 The M9 grid

| class | `c3bdae2` | `9126350` | HUNT3 `0c0f5a3` |
|---|---|---|---|
| clean | 4 168 | 3 874 | 4 047 |
| refused | 2 584 | 3 500 | 3 524 |
| `DEFECT:double_free` | 260 | 16 | 0 |
| `DEFECT:leak` | 214 | 149 | 0 |
| `DEFECT:leg_mismatch` | 149 | 0 | 0 |
| `DEFECT:uaf` | 109 | 6 | 0 |
| `DEFECT:wrong_value` | 46 | 24 | 0 |
| `DEFECT:segv` | 37 | 2 | 0 |
| `OVERRESTRICT` | 4 | 0 | 0 |
| **generated** | **7 571** | **7 571** | **7 571** |

**No anomaly is left by the classifier's classes** (`DEFECT`, `CRASH`, `OVERRESTRICT`; F-049's 24
refused SAFE cells are named below; worded so in M13, M12v's finding (8)). 393 cells moved from `9126350` (`results/0c0f5a3/MOVES9.md`): F-003's 44 and
F-008's 40 accepted REFUSE cells are refused (74); the store-through-pointer and pick-binding leaks
are clean (76), 141 cells; F-009's 72 and F-010's 12 refused SAFE cells are clean (79); 60 `OwnedFd`
cells lost F-007's `to_cstring` bytes (78); and 24 SAFE `pick_own` cells are newly refused, F-049
(74). D-065's 262 `MOVE-001` cells and the 28 `TYPE-047` receiver cells did not move.

### 13.7 M10

At HUNT3, **218 agree and 5 disagree** (HUNT2: 212 and 11; 223 tested). Seven of HUNT2's
disagreements now agree: `h02` (74), `l06`, `l08`, `l11` (75), `m06_spaceship`, `p05_negative_patterns`
and `v12` (79). Four still disagree with HUNT2's text, F-017's documentation sentences (`t02`, `t08`,
`t09`, `l28`), which the references have since corrected. One newly disagrees: `c25`, a 16-digit `flt32`
literal, which landing 91 accepts on purpose (D-346 lifted the 15-digit rule). `t07`, re-spelled, is
unchanged at 94.

### 13.8 M11

At HUNT3, **2 628 agree and 244 disagree** (HUNT2: 2 587 and 285; 2 872 tested). 95 claims changed: 62
to AGREE, 21 to DISAGREE, 4 inside DISAGREE and 8 inside AGREE (`results/0c0f5a3/m11-changes.txt`).

**The 285, by registry status** (`results/0c0f5a3/m11-disagree.jsonl`):

| status at HUNT3 | claims | at HUNT3 |
|---|---|---|
| FIXED, with its landing (MOVES12 rows 54–80, 91) | 69 | 62 agree; 7 still disagree: `mc0136` (80, DEF-150: the program copies the reference's old `$$i` example, now `PARSE-001`), `mc0085b` (DEF-153: a documentation row), and DEF-133's five (79: the references corrected, the claims keep HUNT2's text) |
| OPEN, DEF-154: F-028's documentation rows | 94 | disagree |
| OPEN, DEF-239: F-030 … F-044's documentation rows | 95 | disagree |
| OPEN, DEF-234 (a)(b), DEF-190, DEF-236 (a) | 6 | disagree |
| not a defect: the backward pipe (F-039 b, F-046 c) | 2 | disagree |
| not findings: strict 2, extraction 17 | 19 | disagree |
| **total** | **285** | **62 agree, 223 disagree** |

**The 21 new disagreements are each a change the compiler made on purpose** (MOVES12 rows 81–90): the
six `uint8[]` bindings (103), `mc0388` (106), `me0119`/`me0119b`, `as0572` and `md0042` (113), six BUILD
scripts (71: npkg requires a `[toolchain]` `triple` pin), `ty0190` (91), `ty0322` (78: `cstring` is 24
bytes), `ty1635` (97: D-347's invariants) and `ty1669` (83: `flt64` is no literal suffix). Two
agreements now agree for another reason (S55's screen): `bi0010` and `bi0017` are refused `TYPE-007` at
the view, not `BORROW-001` (Option C's).

### 13.9 The move table

`results/0c0f5a3/MOVES12.md`, 97 rows: one per group of moves sharing a shape and a cause, with the
LLVM control as row 0. Recall 0, M2 0, findings 67 programs (and F-025's script, F-045's message), M9
393 cells, M10 9, M11 95. **Every move carries a landing number with its DEF or D- number, or a finding
id; zero UNEXPLAINED.** The evidence is the registry or notice text at HUNT3 naming the program or its
shape, or for F-049's 24 cells a bisection. **Predicted moves: 29 of 33 ticked**; the other four are
explained there: P1 and P2 each lost four cells to a refusal (F-008's fix; F-049), P17's F-024 is
`PARSE-001` as DEF-150's record says, and P32's pin refusal never arose. The grid comparisons are
`results/0c0f5a3/MOVES.md` and `MOVES9.md`.

### 13.10 The registry refresh and the FZ items

`KNOWN_DEFECTS.md` gains the DEF-227 … DEF-253 section (FZ-8), every status read at HUNT3 and every
fixed row measured there; each older DEF bullet carries its landing and its HUNT3 verdict; the
F-001/F-002 note sits with the faces of known defects. FZ-1 … FZ-10 are applied as the document-fix
draft words them. For the author: FZ-2's counting (F-044's 33 → 32 and the counts that follow),
`PLAN.md:16` and `README.md:25` ("the five known defects"), and F-020's `ctl_j3`.

### 13.11 Candidates and findings

- **F-049**, lower priority, an over-restriction (`findings/F-049-pick-binding-reinit-refused/`): a
  consuming `pick`'s binding, moved and then re-assigned, cannot be read; `MOVE-001` says it "is
  invalid until it is assigned again" just after it was. Its local twin compiles and reads 22. It is
  DEF-124's shape (F-009) at a pattern binding. **Bisected to landing 74** (`40deffa`, DEF-118's fix):
  the grid's 24 cells and the finding's programs run at landing 73 `bbb1530` and are refused at 74. At
  the baseline and HUNT2 the reproducers give the right answer. Not registered; the workbench verifies
  it first (PLAN D6).
- **Two reference rows contradict HUNT3**, documentation, the compiler right: TYPE_REFERENCE:1858 at
  HUNT3 spells `complex(3.0flt64, 4.0flt64)`, which HUNT3 refuses `LEX-009` (`flt64` is no suffix); and
  AST_REFERENCE:578's node comment lists `#[align(16)]` and `#[cfg(...)]` while its paragraph says
  `#[derive]` is the one attribute (`DERIVE-007` since 113). Measured by `ty1669` and `as0572`.
- **`as0572`, the dispatch's question**: at `9126350` and the baseline `#[align(16i32)]` was a silent
  no-op, measured (`#size_of<Aligned>()` is 8 with and without it). No reference sentence gave the
  attribute a result, so it is F-039 (d)'s shape, an attribute the language does not have accepted and
  ignored, fixed by DEF-236 (d) at 113; not a silent wrong answer against a stated result.

### 13.12 What M12 does not cover

- **Option C's reference delta.** Every claim keeps the sentence it was extracted from at HUNT2; the
  references have moved since, and the new disagreements above are where. Re-extracting is Option C.
- **The `m11_claims` spellings**: the six `uint8[]` bindings and `bi0010`/`bi0017`, and the claims that pass
  a view to a plain parameter or return one.
- **Re-spellings left to `nitpick-fuzz_2`**: `me0119`, `me0119b` and `me0183` (a binding named `buffer`,
  refused before their claims are reached), `md0042` (a `mod:mod;` header), the six BUILD scripts
  (no `triple` pin), and F-020's `ctl_j3`.
- **Option B's class**: the -O2 initialisation and pointer-store defects (DEF-250, DEF-251), and DEF-252's
  view re-seated by a callee, a use after free registered at 113; none lies on the grid's axes.
- The grid's own blind spots (section 7) stand.

### 13.13 Cost

At 4 jobs, one harness at a time (wall time of each run; the lock waits are not counted):

| step | wall |
|---|---|
| builds: the baseline, HUNT2, HUNT3 | 74.6 + 72.7 + 55.2 s |
| LLVM 20.1.8: fetch, test, extract | 328 s (the download 56 s) |
| the shakedown: M2, M9, recall, M10 at each old compiler, and the findings | 602.9 + 570.0 + 53.7 s ≈ 20.5 min |
| the LLVM control | 849.9 s ≈ 14.2 min |
| the runs at HUNT3: recall, findings (two passes), M2, M9, M10, M11, the 285 | 1 169.2 s ≈ 19.5 min |
| F-049: two bisection builds, 130 cells twice, its programs | 112.7 + 25.3 + 5.6 s |
| **in all** | about 66 min of harness time |

The session ran from 16:41 to 18:37 EDT on 2026-10-15.

### 13.14 Reproducing

From a clone at the commit that closes M12, with the compiler cloned to `.work/nitpick`:
```
git -C .work/nitpick worktree add ../base c3bdae2
git -C .work/nitpick worktree add ../hunt2 9126350
git -C .work/nitpick worktree add ../hunt3 0c0f5a39fcd2a54e78bf7409add841cbc16927b7
ln -s /usr/lib/llvm-20 .work/llvm-20.1.2     # llvm-config: 20.1.2
# .work/llvm-20.1.8: LLVM-20.1.8-Linux-X64.tar.xz, sha256 1ead36b3…, extracted --strip-components=1
(cd .work/hunt3 && PATH=$PWD/../llvm-20.1.8/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk)
python3 gen/grid.py && python3 gen/grid9.py
python3 gen/run_known.py .work/hunt3 --llvm .work/llvm-20.1.8 --out results/0c0f5a3/known-m12.txt
python3 gen/run_findings.py --hunt .work/hunt3 --base .work/base --llvm .work/llvm-20.1.8 --name VERDICTS-0c0f5a3.txt
python3 gen/run.py .work/hunt3 --llvm .work/llvm-20.1.8
python3 gen/run.py .work/hunt3 --llvm .work/llvm-20.1.8 --cells cells9 --out results/0c0f5a3/cells9.jsonl
python3 gen/m10_run.py .work/hunt3 --llvm .work/llvm-20.1.8
python3 gen/m11_run.py .work/hunt3 --llvm .work/llvm-20.1.8
python3 gen/compare.py results/9126350/ results/0c0f5a3/
python3 gen/compare.py --grid9 results/9126350/ results/0c0f5a3/
python3 gen/compare_runs.py results/9126350/m11.jsonl results/0c0f5a3/m11.jsonl
```
The baseline and HUNT2 are built the same way under `.work/llvm-20.1.2`; the findings with heap words
are re-run with `--heap` (F-003 … F-010). `PROGRESS.md`'s M12 section has every command and time.

## 14. M13 — the initialisation and pointer-store grid

M13 is the task after M12 (S76): a grid aimed at the class the libraries found silent wrong answers in at
-O2, with the -O2 leg as the observer. DEF-250 (a module binding with no initialiser emitted read-only),
DEF-251 (a store through `NULL`) and DEF-252 (a view re-seated by a callee) each had one reproducer; the grid
asks how many more faces each has and whether the fixes cover them. It ran on 2026-10-21, on the Team seat,
on branch `local-m13`, one harness at a time under the seat's lock, at 4 jobs.

### 14.1 The compilers and the toolchain

| role | commit | LLVM | build | `npkc.ll` bytes / sha256 | `npkrt.o` | `npkc` |
|---|---|---|---|---|---|---|
| baseline | `c3bdae2` | 20.1.2 | M12's | 28 111 929 / `4029fc70efbe9cd3…`, as committed | 72 576 / `162b897539285a77…` | 9 724 160 / `5fd636b9ab557c19…` |
| HUNT3 | `0c0f5a3` | 20.1.8 | M12's | 31 701 272 / `f520d5744b1e9951…`, as committed | 72 656 / `c8e5033ad17c70f8…` | 11 283 680 / `02e7b06321a16950…` |
| HUNT4 | `c72639f` (`c72639f2332208649309b91796d6f173d19a64d2`) | 20.1.8 | 56.0 s | 32 424 412 / `2f1b9480701e1c86…`, equal to notice 137's ladder row | 72 656 / `c8e5033ad17c70f8…`, equal | 11 528 072 / `ba798aa0e5500a8d…`; the row's is 72 bytes shorter, its linker comment (reasoned) |

- **HUNT4** is the compiler's `origin/main` at the session's fetch (04:11 EDT): landing 137, carrying landings
  114 to 137 (PROGRESS.md's M13 section lists each). Among them: 114 (DEF-250, `TYPE-055`), 115 (DEF-251 (i),
  `null_pointer_is_valid`), 116 (DEF-252, `BORROW-002` at a callee's store), 117 (D-353), 118 (DEF-253, DEF-254),
  **119 (D-355 (ii): `NULL` leaves the plain pointer, `TYPE-096`)**, 120 (D-360, `??!`), 121 (D-361, `TYPE-097`),
  132 (DEF-256, this repository's F-049) and 136 (a keyword local is `PARSE-001`). The ladder row is the
  workbench BOARD's "THE BASELINE NOTICE 138 MUST QUOTE"; `npkc.o` and `builder.o` equal it too. A second
  fetch at 05:05 EDT found no newer landing.
- **The baseline and HUNT3** are M12's builds, unchanged (their digests re-read). The canaries pass at all
  three compilers.
- **LLVM:** 20.1.2 is the machine's `/usr/lib/llvm-20`; 20.1.8 the release tarball (sha256 `1ead36b3…`, as
  M12 recorded). Every runner names its LLVM, and every runner's temporary directories sit in the session's
  scratch (S80).
- **The author's go** (S77): "i rand the shell script and also approve the two points", the message of
  2026-10-15 21:00:54 EDT relayed by management_0, answering (i) HUNT4 = the compiler's `origin/main` at the
  fetch and (ii) LLVM 20.1.8 for HUNT3 and HUNT4.

### 14.2 The housekeeping

M12v's non-blocking findings, each a wording edit or a note (commit M13 (1b)): (1) the P32 bullet and §13.3
now count 23 `[toolchain]` scripts by a quoted grep, and name `bd0075` and `bd0299` as reaching npkg's
toolchain check by design; (2) MOVES12 row 4 and DEF-119's bullet give `BORROW-013` to DEF-123; (4) M12's box
13 says which form it was ticked on; (6) DEF-247 and DEF-249 say "no program of ours", with the searches; (7)
an erratum line in §13.4, and `gen/run_findings.py` writes no file for a finding with no programs; (8) "no
anomaly is left by the classifier's classes". DEF-256's row is added from the registry at HUNT4 (F-049, fixed
at 132), and F-049's README gains the registration and the workbench's reproduction, each labelled as
reported. Dispatch note (a): DEF-236 (a) is fixed at 117; `m11/programs/as0062.npk` is `TYPE-095` at 10:12 at
HUNT4 (`EMIT-002` at 10:71 at HUNT3). No committed record changed but MOVES12's row 4 wording.

### 14.3 The grid

`gen/grid13.py` writes 933 cells and states 431 combinations it skips, each with its reason
(`cells13/SKIPPED.txt`); `--selfcheck` passes (S83–S88). Every cell carries its expectation, written before
any run from the rule that governs it, with the rule's text and source in `meta.json` (S85). The learning by
snippet (§4) is in PROGRESS.md's M13 section: 130 probes, 51 more, and 89 template copies for spellings only
(S89).

| section | axes | rules | generated | REFUSE | SAFE | TRAP | skipped |
|---|---|---|---|---|---|---|---|
| S | the three seeds, byte for byte | D-211; D-355 (ii); D-004 rule 3 | 3 | 3 | | | |
| A | 11 types and qualifiers × 5 declarations × 9 operations | D-211 (`TYPE-055`); TYPE_REFERENCE §26 (`ASSIGN-002`); D-287 (`TYPE-086`, `TYPE-071`) | 166 | 157 | 9 | | 329 (99 `const`, retired at 1.4.2c) |
| B | 8 places × 8 operations × 2 types | D-355 (ii) (`TYPE-096`); DEF-251 (i) (TRAP 107); §11.1 (`TYPE-007`); D-360 (TRAP 95) | 106 | 87 | 8 | 11 | 22 |
| C | 8 types × 5 places × 7 operations, each with its definitely-assigned twin | D-010 (`ASSIGN-001`; `TYPE-027` for a literal) | 500 | 250 | 250 | | 60 |
| D | 5 types × 15 operations × 2 operand forms | D-277, D-310, D-331 (`TYPE-070`, `TYPE-076`, `TYPE-004`); D-007, D-210 (TRAP 111, 97, 98, 93) | 130 | 37 | 56 | 37 | 20 |
| E | 7 stores × 2 lifetimes × 2 observers | D-004 rule 3 with landing 116 (`BORROW-002`) | 28 | 14 | 14 | | |
| **all** | | | **933** | **548** | **337** | **48** | **431** |

**The codes** (S84): 0 success; 12 a value read back that is not the one written; 13 a zero read where a
value was written or where nothing was; 14 a `NULL` test after a dereference that took the null branch; 21–25
E's view (the original, the new value, vacant, another value, the reuse sentinel); 70 the free poison as an
observation; 170 the poison byte as the exit (the DEF-252 seed); 91–98 and 106–117 `gen/m10.py`'s TRAPS; 100–105
and 118–122 the prelude's eleven other identities with S44's codes, so the failsafe names all 31 and its `(*)`
arm (99) is reached only by a garbage argument, DEF-251's -O2 face; every template declares its helpers before
`main` and `failsafe` directly after it (S83). 29 cells contain `wild` and are scope wild.

### 14.4 The seeds

| seed | DEF | baseline | HUNT3 | HUNT4 |
|---|---|---|---|---|
| `bare_binding` | DEF-250 | 107/11 `ACCEPTED:DEFECT:leg_mismatch` | 107/11 `ACCEPTED:DEFECT:leg_mismatch` | refused `TYPE-055` (114) |
| `null_store` | DEF-251 | 107/99 `ACCEPTED:DEFECT:fallthrough` | 107/99 `ACCEPTED:DEFECT:fallthrough` | refused `TYPE-096` (119) |
| `probe08h_view_reseated` | DEF-252 | 170/170 `ACCEPTED:DEFECT:uaf` | 170/170 `ACCEPTED:DEFECT:uaf` | refused `BORROW-002` (116) |

At HUNT3 each is flagged as the recall gate requires (P1), and at HUNT4 each is refused by its fix (P2).

### 14.5 The LLVM control

HUNT3 under 20.1.2 against HUNT3's record under 20.1.8: **0 of 933 cells differ** (P11). No undefined
behaviour in grid13's emission is folded apart by the two versions. The control cannot see undefined
behaviour both fold alike, which is why -O0 against -O2 stays the observer.

### 14.6 Results by section and compiler

From `results/<commit>/classified13.jsonl` (each run generated = refused + `OVERRESTRICT` + `REFUSED_TRAP` +
clean + each `DEFECT`, `ACCEPTED`, `LOUD`, `CRASH`, `timeout` and `other` count; none of the last four
occurs). HUNT4's two runs agree in all 933 cells.

**At the baseline `c3bdae2` (20.1.2):**

| class | S | A | B | C | D | E | all |
|---|---|---|---|---|---|---|---|
| clean |  | 7 | 8 | 244 | 93 | 10 | 362 |
| refused |  | 73 | 22 | 250 | 21 | 8 | 374 |
| `DEFECT:fallthrough` |  |  | 6 |  |  |  | 6 |
| `DEFECT:leg_mismatch` |  |  | 3 |  |  |  | 3 |
| `OVERRESTRICT` |  | 2 |  | 6 |  | 4 | 12 |
| `REFUSED_TRAP` |  |  | 2 |  |  |  | 2 |
| `ACCEPTED:DEFECT:fallthrough` | 1 |  | 31 |  |  |  | 32 |
| `ACCEPTED:DEFECT:false_trap` |  |  |  |  | 16 |  | 16 |
| `ACCEPTED:DEFECT:leg_mismatch` | 1 | 46 | 14 |  |  |  | 61 |
| `ACCEPTED:DEFECT:segv` |  | 2 |  |  |  |  | 2 |
| `ACCEPTED:DEFECT:uaf` | 1 |  |  |  |  | 6 | 7 |
| `ACCEPTED:DEFECT:wrong_value` |  | 34 |  |  |  |  | 34 |
| `ACCEPTED:clean` |  |  | 20 |  |  |  | 20 |
| `ACCEPTED:other` |  | 2 |  |  |  |  | 2 |
| **generated** | **3** | **166** | **106** | **500** | **130** | **28** | **933** |

**At HUNT3 `0c0f5a3` (20.1.8):**

| class | S | A | B | C | D | E | all |
|---|---|---|---|---|---|---|---|
| clean |  | 9 | 8 | 244 | 93 | 14 | 368 |
| refused |  | 75 | 9 | 250 | 37 | 4 | 375 |
| `DEFECT:fallthrough` |  |  | 6 |  |  |  | 6 |
| `DEFECT:leg_mismatch` |  |  | 3 |  |  |  | 3 |
| `OVERRESTRICT` |  |  |  | 6 |  |  | 6 |
| `REFUSED_TRAP` |  |  | 2 |  |  |  | 2 |
| `ACCEPTED:DEFECT:fallthrough` | 1 |  | 37 |  |  |  | 38 |
| `ACCEPTED:DEFECT:leg_mismatch` | 1 | 44 | 17 |  |  |  | 62 |
| `ACCEPTED:DEFECT:segv` |  | 2 |  |  |  |  | 2 |
| `ACCEPTED:DEFECT:uaf` | 1 |  |  |  |  | 10 | 11 |
| `ACCEPTED:DEFECT:wrong_value` |  | 34 |  |  |  |  | 34 |
| `ACCEPTED:clean` |  |  | 24 |  |  |  | 24 |
| `ACCEPTED:other` |  | 2 |  |  |  |  | 2 |
| **generated** | **3** | **166** | **106** | **500** | **130** | **28** | **933** |

**At HUNT4 `c72639f` (20.1.8):**

| class | S | A | B | C | D | E | all |
|---|---|---|---|---|---|---|---|
| clean |  | 9 | 17 | 244 | 93 | 14 | 377 |
| refused | 3 | 157 | 87 | 250 | 37 | 12 | 546 |
| `DEFECT:leg_mismatch` |  |  | 2 |  |  |  | 2 |
| `OVERRESTRICT` |  |  |  | 6 |  |  | 6 |
| `ACCEPTED:DEFECT:uaf` |  |  |  |  |  | 2 | 2 |
| **generated** | **3** | **166** | **106** | **500** | **130** | **28** | **933** |

The wild-scoped cells (29) are counted above and read apart in 14.7 and 14.8. At HUNT4 every refused cell
names the code its rule names.

### 14.7 The faces of DEF-250, DEF-251 and DEF-252, and what each fix covers

From `results/c72639f/FACES13.txt` (HUNT3 against HUNT4: 184 cells moved) and `MOVES13.md` rows 8–19:

| DEF | grid13's faces at HUNT3 | the fix | at HUNT4 |
|---|---|---|---|
| DEF-250 (A) | 86 cells: every binding with no initialiser, `pub` with none, and the `stack`, `wild` and `wildx` forms, of every type. A write faults at -O0 and reads zero at -O2 (107/13: a write, a compound assignment, a field or element write, a write through `@g` in a callee); a read gives the zero default on both legs (13/13, a default standing in); an atomic store faults on both legs (107/107); a channel `send` fails (`ChannelClosed`, 102/102). Four atomic address cells are refused `EMIT-002` (F-052's shape) | 114: `TYPE-055` at the declaration | **all 86 refused**. A binding with an initialiser was refused at HUNT3 already (D-211); `fixed` reads run clean at every compiler; `@g` of a `fixed` binding is `TYPE-071` (D-287) at every compiler, so P4's suspect has no face |
| DEF-251, plain (B) | 78 cells: `NULL` in a plain local, a `fixed` local, a module `fixed T->`, a struct field, a parameter, a helper's return. A store, a used load, a field read or a dereferencing callee falls through (107/99) or disagrees (107/12); the unused load before a `NULL` test answers 14 at -O2 where -O0 faults, and for a struct reached through a parameter or a return the -O2 leg folds the test away and reports success (107/0, **DEF-251's inferred face, measured**); the guarded store and the comparison run 0/0, accepted (24) | 119, D-355 (ii): `TYPE-096` at the literal | **all 78 refused** |
| DEF-251, `wild` (B, scope wild) | 9 cells: a store, a used load, a field read, a `wild` callee falls through or disagrees (107/99, 107/12); the unused load before a test gives 107/14 | 115, DEF-251 (i): `null_pointer_is_valid` | 7 move to the expected 107/107; **the dead load stays 107/14 (F-051)**; the guarded store and the comparison run clean |
| DEF-252 (E) | 10 dies-first cells read freed memory (70 through the observer, 25 with the reuse sentinel): a callee storing the view into the whole pointee, into a field, through a method, two levels down, and into an element of an array of holders. The direct store and a returned holder are refused `BORROW-002` at HUNT3 already | 116: `BORROW-002` at a callee's store into a destination the frame owns | 8 refused; **the array-element store stays 70/70 and 25/25 (F-050)**; the outlives twins run clean |

Landing 120 adds the Optional's `??!`, refused at HUNT3 (`TYPE-007`, read as `??` then `!`), and at HUNT4 it
traps its identity on both legs (95/95), 2 cells.

### 14.8 Candidates and findings

Each goes to `nitpick-fuzz_2` for D6 verification first (PLAN D6), through the dispatcher.

| finding | §9 class | grid13 cells | HUNT4 | HUNT3 | baseline |
|---|---|---|---|---|---|
| **F-050**, a callee storing a block-local view into an ELEMENT of the array behind its pointer argument outlives the storage (`findings/F-050-callee-view-store-into-array-element/`) | **soundness hole**: accepted, reads the free poison | `g0915`, `g0916` (`ACCEPTED:DEFECT:uaf`) | 0 / 170 / 170 | 0 / 170 / 170 | 0 / 170 / 170 |
| **F-051**, a dead load through a `wild` `NULL` pointer faults at -O0 and is deleted at -O2 (`findings/F-051-wild-dead-load-legs-disagree/`) | **reported apart: the check of DEF-251 (i)**, scope wild (outside CLAUDE.md's definition) | `g0249`, `g0250` (`DEFECT:leg_mismatch`) | 0 / 107 / 14; 0 / 107 / 0 with no test | the same | the same |
| **F-052**, an atomic's method through a pointer with `.` is `EMIT-002`; `(<-p).load()` lowers (`findings/F-052-atomic-method-through-pointer-not-lowered/`) | **crash / loud emission**, lower priority | at HUNT3 and the baseline, A's four atomic address cells; found by §4's probe | 1 `EMIT-002` | the same | the same |

All three are old: present at the baseline. Each README holds the shape, the verdicts as compiler × leg ×
(npkc, run), the control a wrong implementation gets wrong, the deduplication and what was measured apart
from what is inferred.

**Not a finding:** C's six `OVERRESTRICT` cells (`g0692` … `g0708`) store `@z` into a field or element of a
local in a branch, loop or arm, and are `BORROW-002` at every compiler. The compiler cites D-004 rule 3 ("only a
local binding in the borrowing frame is provably no longer-lived than the borrow"), which D-004 makes
"deliberately strict to start". The expectation was mine and wrong; it stays as committed, and the six cells
are read against it.

### 14.9 The regression leg and `MOVES13.md`

At HUNT4 under 20.1.8: recall 25/25 "once fixed", identical to HUNT3's record; findings, 160 programs in 34
(the 15 row findings write no file now), every baseline line as committed, two findings moved: F-029's
control `PARSE-002` → `PARSE-001` at 7:11 (136) and F-049's two reproducers `MOVE-001` → 22/22 (132); M2 956
cells, 0 moved; M9 7 571 cells, 4 071 clean and 3 500 refused, 24 moved, MOVES12 row 44's cells exactly (132);
M10 223, 0 changed. **No memory fault in the regression leg.** `results/c72639f/MOVES13.md` carries every
move with its landing, **zero UNEXPLAINED**, and P1–P11 each ticked or explained. Dispatch note (e)'s three
readings hold as written.

### 14.10 What M13 does not cover

- **The roads landing 121 leaves** for a later run's family (note (d)): a pick expression's `give` and a
  method's receiver taking a value of wild provenance.
- **Module state across tasks**, D-211's reason: grid13's channels and atomics run in one task.
- **E's holders** are a struct and an array of structs; the lists, `dyn`, function values and async callees
  of landing 116's own test are not re-tested here.
- **D's types** are int8, uint8, int32, int64 and uint64; the compound spellings (`<<=`, `/=`) and `CastRange`
  are M10's.
- **The `const` axis** has no cells: `const` is no declaration form (99 combinations skipped).
- **Option C** (M11's reference delta) and §10's re-spellings, which dispatch notes (a) and (c) keep out of
  M13 (S91).
- The LLVM control's blind spot (14.5), and the grid's own (section 7).

### 14.11 Cost

At 4 jobs, one harness at a time (the wall time of each command, any lock wait included; no `flock` ever
returned 75):

| step | wall |
|---|---|
| HUNT4's build | 56.0 s |
| the canaries, `as0062`, three probe batches (130, 51 and 89 programs at two compilers) | about 35 s |
| the seeds at HUNT3, HUNT3's record, the LLVM control | 1 + 57 + 64 s |
| grid13 at the baseline and HUNT4 twice | 53 + 47 + 47 s |
| the regression leg: recall, findings (two passes), M2, M9, M10 | 5 + 280 + 59 + 458 + 18 s |
| triage: 23 programs at four runs, two minimisations, three findings recorded | about 60 s |
| **in all** | about 21 min of harness time |

The work ran from 04:09 EDT (the dispatch) to 05:26 EDT on 2026-10-21, and the close was committed after a gap
with no activity, from 05:26 to 07:49 (the last file written at 05:25:35, the next `date` read 07:49:43);
PROGRESS.md's Log has the times.

### 14.12 Reproducing

From a clone at the commit that closes M13, with the compiler cloned to `.work/nitpick` and M12's worktrees:
```
git -C .work/nitpick worktree add --detach ../hunt4 c72639f2332208649309b91796d6f173d19a64d2
(cd .work/hunt4 && PATH=$PWD/../llvm-20.1.8/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk)
python3 gen/grid13.py --out cells13 && python3 gen/grid13.py --selfcheck
python3 gen/run.py .work/hunt3 --cells cells13 --llvm .work/llvm-20.1.8 --jobs 4 --out results/0c0f5a3/cells13.jsonl
python3 gen/run.py .work/base  --cells cells13 --llvm .work/llvm-20.1.2 --jobs 4 --out results/c3bdae2/cells13.jsonl
python3 gen/run.py .work/hunt4 --cells cells13 --llvm .work/llvm-20.1.8 --jobs 4 --out results/c72639f/cells13.jsonl
python3 gen/classify13.py --cells cells13 results/c72639f/cells13.jsonl
python3 gen/compare13.py results/0c0f5a3/classified13.jsonl results/c72639f/classified13.jsonl
python3 gen/run_findings.py --hunt .work/hunt4 --base .work/base --llvm .work/llvm-20.1.8 --name VERDICTS-c72639f.txt
python3 gen/run.py .work/hunt4 --cells cells9 --llvm .work/llvm-20.1.8 --jobs 4 --out results/c72639f/cells9.jsonl
```
The other regression runs are §8's commands with `hunt4` and `c72639f`; `PROGRESS.md`'s M13 section has every
command and time.

## 15. M14 — the S-140 class

M14 is the task after M13 (S92). The author's ruling R1 on F-051 (S-140, 2026-10-22 03:49:41, recorded as D-364 with
landing 142) amended TYPE_REFERENCE §27: a load through a `wild` `NULL` pointer whose value nothing uses is no read at
-O2, the legs' one permitted disagreement. M14 gives the oracle that allowance as narrowly as the ruling gives it
(management_2: "any allowance in an oracle can hide a real disagreement"), and tests the guarantee's other half, that a
used load faults at both legs. It ran on 2026-10-25, on the Team seat, on branch `local-m14`, one harness at a time
under the seat's lock, at 4 jobs, under LLVM 20.1.2, from the fuzzer's manager's brief
(`fuzz-m14-brief-2026-10-23.md`, sha256 `291db53f…`, S92).

### 15.1 The compilers

| role | commit | LLVM | build | `npkc.ll` bytes / sha256 | `npkc.o` | `npkrt.o` | `npkc` |
|---|---|---|---|---|---|---|---|
| baseline | `c3bdae2` | 20.1.2 | M12's | 28 111 929 / `4029fc70efbe9cd3…`, as committed | | 72 576 / `162b897539285a77…` | 9 724 160 / `5fd636b9ab557c19…` |
| HUNT5 | `249eae9` (`249eae91559bfc1e3b8a17b12286c21108e4215a`) | 20.1.2 | 64.9 s | 33 418 659 / `59d16f1d2273e545…`, equal to notice 161's ladder row | 13 828 024 / `34c7d3dd9b95d6e4…`, equal | 72 656 / `c8e5033ad17c70f8…`, equal | 11 957 184 / `2c8d898f101a3280…`; the row's is the same size (a linked binary's sha is not compared) |

- **HUNT5** is the compiler's `origin/main` at the session's fetch (03:02:58 EDT; committed 2026-10-24 21:57:10
  -0400): landing 161, carrying landing 155 (the brief's floor) and §27's S-140 sentence. Past 148 it carries 149
  (DEF-277), 150 (DEF-276), 151 (D-363's R1), 152 (DEF-278, DEF-281), 153 (DEF-282, DEF-285), 154 (DEF-287), 155
  (DEF-288, DEF-290), 156 (DEF-296, DEF-289's first face), 157 (DEF-289's second face), 158 (DEF-300), 159 (DEF-297,
  DEF-301, DEF-303), 160 (DEF-302) and 161 (DEF-305) (S94). The ladder row is the workbench BOARD's "THE BASELINE
  NOTICE 162 MUST QUOTE"; `builder.o` equals it too. A second fetch at 07:57 EDT, before filing, found no newer landing.
- **LLVM 20.1.2 throughout**, PLAN.md:10's own pin, which needs no go (S95): `.work/llvm-20.1.2` is the machine's
  `/usr/lib/llvm-20`. HUNT3 and HUNT4 are not run. The canaries pass at the baseline and HUNT5.
- **The go** (S93) is management_2's funding, quoted verbatim in PROGRESS.md: "**S93, management's go for fuzz's
  M14:** the F-051 R1 run (PERMITTED:S-140), at HUNT5 = the compiler's origin/main at the fetch, under LLVM 20.1.2."
  The dispatch adds that those words stand as the go, that management_2 asked for no author's go, and that no LLVM
  go is needed.

### 15.2 The housekeeping

Commit M14 (1b), wording only: M13's optional box 10 is `[-]`, closed unworked (S96, M13v's (10)), so the resume rule
cannot send a session into `m11/`; `KNOWN_DEFECTS.md`'s "Open:" heading, which stood over four fixed rows, is "Open
at HUNT3:", with a heading of their own over DEF-250 … DEF-253 (M13v's (7)); M13's count reads 1 361 axis
combinations (930 generated + 431 skipped) plus 3 seeds = 1 364 (M13v's (8)); `cbc38b9`'s commit time 04:49:55 and
push time 04:49:57 are named apart (M13v's (9)). Commit M14 (4): `KNOWN_DEFECTS.md`'s M13 block is rewritten from the
registry at HUNT5 (F-050 = DEF-272, fixed at 138; F-051 = DEF-273, ruled R1 by S-140 as D-364 at 142, not a defect;
F-052 = DEF-274, fixed at 146), each "fixed" confirmed by M14's own `run_findings` at HUNT5 and the manager's
re-measures labelled as reported; F-051's README gains a section "S-140 (R1)", appended. No committed record changed.

### 15.3 The class

**The rule** is §27's last `NULL` bullet at HUNT5 (TYPE_REFERENCE.md:2314–2324), which every grid14 cell carries
verbatim: a load whose value the program USES faults at both legs; "A load whose value NOTHING uses is no read at
-O2 … and faults at -O0: the legs' one permitted disagreement, narrow to an unused load through a `wild` `NULL`
pointer (D-364 …)".

**The class**, `PERMITTED:S-140`, in `gen/classify14.py` (S99), which extends `gen/classify13.py` by importing its
`run_class` and `classify` and nothing else. It is decided after `timeout`, `LOUD` and `DEFECT:fallthrough`, and
before `DEFECT:leg_mismatch`, only when all five hold: (1) the cell's index entry carries `s140` = "unused_load",
which the generator sets by construction on the 40 U cells and the three dead-load seeds and on nothing else; (2)
scope wild, expect TRAP, `expect_exit` 107; (3) O0 = 107; (4) O2 = its `s140_o2`, the exit the program gives with its
load deleted, not 107; (5) its twin, that load-deleted program, gives `s140_o2` on both legs in the same record. A
flagged cell without its twin's record is an error. Every other disagreement stays `DEFECT:leg_mismatch`. The twins'
expected exit is their own (14 or 0), not 0 (change 1). **`--selftest`** prints:
```
ok    flagged, 107/14, twin 14/14                                                                  -> PERMITTED:S-140
ok    flagged, 107/107, twin 14/14                                                                 -> clean
ok    flagged, 107/0 with s140_o2 14, twin 14/14 (condition 4)                                     -> DEFECT:leg_mismatch
ok    flagged, 106/14, twin 14/14 (condition 3)                                                    -> DEFECT:leg_mismatch
ok    flagged, 107/14, twin 14/0 (condition 5)                                                     -> DEFECT:leg_mismatch
ok    flagged, 107/14, twin 0/0: the twin's legs agree, but not with s140_o2 (condition 5)         -> DEFECT:leg_mismatch
ok    flagged, 107/99, twin 14/14                                                                  -> DEFECT:fallthrough
ok    flagged but scope plain, 107/14, twin 14/14 (condition 2)                                    -> DEFECT:leg_mismatch
ok    unflagged, 107/14: s140_o2 14 and a 14/14 twin, the flag alone absent (condition 1)          -> DEFECT:leg_mismatch
ok    unflagged, 107/0: s140_o2 0 and a 0/0 twin, the flag alone absent (condition 1)              -> DEFECT:leg_mismatch
ok    flagged, with its twin missing                                                               -> ERROR
ok    flagged, 107/0 with s140_o2 0, twin 0/0 (the exit-0 seed's shape)                            -> PERMITTED:S-140
ok    flagged, expect_exit 106, 107/14, twin 14/14 (condition 2)                                   -> DEFECT:leg_mismatch
ok    a twin, SAFE with expect_exit 14, at 14/14 (change 1)                                        -> clean
ok    a twin, SAFE with expect_exit 0, at 0/0 (change 1)                                           -> clean
selftest: 15 cases, 15 pass
```
**`--against13`** re-classes a record with classify13 in memory and exits 0 only when every class that differs is a
flagged leg mismatch meeting conditions 1–5 (re-derived apart from the classifier it checks) moving to
`PERMITTED:S-140`, or a 14-twin moving from `DEFECT:wrong_value` to `clean`; it also asserts that every flagged cell
whose legs disagree and that fails a condition is `DEFECT:leg_mismatch` (or `DEFECT:fallthrough` with a 99). Before
any run it was tried on synthetic records with two wrong classifiers in place of the class, and caught each where a
live population exists (PROGRESS.md, S99).

### 15.4 grid14

`gen/grid14.py` imports `gen/grid13.py` (its program layout, failsafe, struct S and helpers) and does not edit it. It
writes 109 cells and skips none (`cells14/SKIPPED.txt`: "0 combinations not emitted"); `--selfcheck` passes, making
condition (c) literal: each of the 43 flagged cells, with its one load line (and its one overwrite line) deleted and
its `mod:` name changed to its twin's, equals its twin's text. The learning by snippet (§4) is in PROGRESS.md's M14
section: the manager's 22 probes at HUNT5, and 25 templates for spellings only (S97); none needed a respelling.

| section | axes | expectation (from §27 at HUNT5, before any run) | generated | skipped |
|---|---|---|---|---|
| S | F-051's four programs, byte for byte, and the three dead loads' twins | the dead loads and the control TRAP 107; the twins SAFE 14, 0, 14 | 7 | 0 |
| U | the unused load: O (`bind`, `overwrite`) × P × T × after (`test`, `none`) | TRAP 107, flagged; `s140_o2` 14 or 0 | 40 | 0 |
| W | the twins: P × T × after, no load | SAFE, 14 or 0 | 20 | 0 |
| K | the used load: O (`cmp`, `arith`, `callee`) × P × T | TRAP 107 ("a load … whose value the program USES") | 30 | 0 |
| B | the boundary of "uses": O (`untaken`, `ignore`, `copy`, `selfsub`, `selfcmp`, `deadadd`) × `local` × T | TRAP 107, the strict reading, with the note "whether this form USES the value, §27's words do not settle; … a disagreement is reported, not permitted" | 12 | 0 |
| **all** | | 86 TRAP, 23 SAFE; 43 flagged | **109** | **0** |

The places P are `local`, `param` (a helper `runp` taking `wild T->:q`, called with `NULL`), `field` (`H{ p: NULL }`),
`module` (`fixed wild T->:P = NULL;`) and `returned` (a helper passing `NULL`); T is `int64` and the struct S, read as
`v.a`. **The codes** are grid13's: 0 success; 12 and 13 a read-back check; 14 the `NULL` test took the null branch
(right in a twin, and on a flagged cell's -O2 leg); 99 the failsafe's `(*)` arm; 107 `MachineFault`. Every cell is
scope wild, so `CLAUDE.md`'s defect definition excludes it: grid14 is the check of §27 (D-364), reported apart.

### 15.5 Results by section and compiler

From `results/<commit>/classified14.jsonl`. In each run generated = the sum of the class counts; no cell is `LOUD`,
`CRASH`, `timeout` or `other`. HUNT5's two runs agree in all 109 cells.

**At HUNT5 `249eae9`:**

| class | S | U | W | K | B | all |
|---|---|---|---|---|---|---|
| `PERMITTED:S-140` | 3 | 40 | | | | 43 |
| clean | 4 | | 20 | 30 | 2 | 56 |
| `DEFECT:leg_mismatch` | | | | | 10 | 10 |
| **generated** | **7** | **40** | **20** | **30** | **12** | **109** |

**At the baseline `c3bdae2`:**

| class | S | U | W | K | B | all |
|---|---|---|---|---|---|---|
| `PERMITTED:S-140` | 3 | 28 | | | | 31 |
| clean | 3 | | 16 | | | 19 |
| `DEFECT:leg_mismatch` | 1 | 4 | | 9 | 9 | 23 |
| `DEFECT:fallthrough` | | | | 15 | 3 | 18 |
| `REFUSED_TRAP` | | 8 | | 6 | | 14 |
| `OVERRESTRICT` | | | 4 | | | 4 |
| **generated** | **7** | **40** | **20** | **30** | **12** | **109** |

At HUNT5 the dead-load seeds give 107/14, 107/0 and 107/14 and the U cells 107/14 (`test`) or 107/0 (`none`), each
with its twin at 14/14 or 0/0; every K cell faults at both legs; B's `deadadd` is 107/107 and its other five forms
107/0 at both T. At the baseline the module place is `TYPE-004` (its 8 U, 6 K and 4 W cells), K disagrees in every
cell it compiles (107/12 for `int64` at `local`, `field` and `returned`; 107/99 for the struct and for `int64` at
`param`), and four struct U `test` cells give 107/0 (15.6).

**The predictions**, each from the manager's probes at landing 148:
- **P1** ✓ `--selfcheck` and `--selftest` pass.
- **P2** ✓ At HUNT5 the three dead loads are `PERMITTED:S-140` (107/14, 107/0, 107/14), `ctl_wild_used_load` is clean
  at 107/107, and the three twins are clean; at the baseline the dead loads are permitted and `ctl_wild_used_load` is
  `DEFECT:leg_mismatch` at 107/12.
- **P3** ✓ U at HUNT5 is `PERMITTED:S-140` in all 40 cells at all five places; none is clean, since no -O2 leg keeps
  an unused load; no cell gives 99; every W cell is clean.
- **P4** ✓ K at HUNT5 is all clean, 107/107.
- **P5** ✓ B at HUNT5: `untaken`, `ignore`, `copy`, `selfsub` and `selfcmp` 107/0, `DEFECT:leg_mismatch`; `deadadd`
  107/107, clean; together one candidate, F-053.
- **P6** ✓, explained: at the baseline every K cell it compiles disagrees, 9 at 107/12 and 15 at 107/99 (the -O2 leg
  running into the failsafe's `(*)` arm, DEF-251's face before landing 115, which "or the like" covers), and the 6 at
  `module` are refused `TYPE-004`; none is permitted.
- **P7** ✓ F-050's two holes give `BORROW-002` and its three controls are as at HUNT4 (I measured HUNT5 against HUNT4's
  committed lines; landing 138 is the manager's measurement); F-051 gives 107/14, 107/0 and 107/14, its control
  107/107; F-052's three programs and two controls give 0/0.
- **P8** ✓ HUNT5's two runs agree: 0 of 109 differ.
- **P9** ✓ `--against13` exits 0 at both; its moves are only the flagged dead loads (`DEFECT:leg_mismatch` →
  `PERMITTED:S-140`: 43 at HUNT5, 31 at the baseline) and the 14-twins (`DEFECT:wrong_value` → `clean`: 12 and 10); at
  the baseline the struct U `test` cells at `param` and `returned` give 107/0 against `s140_o2` 14 and stay
  `DEFECT:leg_mismatch`, now measured on `wild` cells. No other U `test` cell joins them.

### 15.6 The narrowness control

Three parts, each against a wrong classifier of its own (rule 5):
1. **A broad allowance** ("any `wild` cell with 107 at -O0") would permit unflagged cells. Every unflagged cell at 107
   and then something else stays a defect class: **10 cells at HUNT5** (B's ten at 107/0, `DEFECT:leg_mismatch`) and
   **37 at the baseline** (`ctl_wild_used_load` and nine K cells at 107/12, `DEFECT:leg_mismatch`; 15 K cells at
   107/99, `DEFECT:fallthrough`; B's 9 at 107/0 and 3 at 107/99). Condition 1 holds the class to the generator's flag.
2. **A mid-width allowance** ("flagged and O0 = 107", without condition (c)) would permit a flagged cell whose -O2 leg
   does not answer as its twin. `--against13` counts **4 such cells at the baseline**, the live population the brief
   expected: `m007_u_struct_param_bind_test`, `m019_u_struct_returned_bind_test`, `m027_u_struct_param_overwrite_test`
   and `m039_u_struct_returned_overwrite_test`, each 107/0 against an `s140_o2` of 14 (its twin 14/14), failing
   condition 4, each `DEFECT:leg_mismatch`: the `NULL` test folded away after the load, as `KNOWN_DEFECTS.md` records
   before landing 115. **At HUNT5, 0**: every flagged cell meets (c), so there the selftest is (c)'s only control.
3. **A classifier that moves anything else** would show in `--against13`, which exits 0 at both compilers: the only
   moves into `PERMITTED:S-140` are flagged leg mismatches meeting conditions 1–5, **43 at HUNT5 and 31 at the
   baseline**.

*A note of M15 (1b):* part 2 says of condition 4 that the selftest is its only control at HUNT5; condition 5 (the
twin gives `s140_o2` on both legs) has no live population at either compiler, so the selftest is its only control
there too. M14v (M14's verification, 2026-10-25) recorded this as its F5 and ruled it non-blocking; no verdict changes.

### 15.7 Candidates and findings

At HUNT5 the cells that are neither `clean` nor `PERMITTED:S-140` are B's ten; no K cell, U cell or twin needs triage.
They are one candidate, through M5's five steps (S100). It goes to the fuzzer's manager for D6 verification first,
through the dispatcher.

| finding | class | grid14 cells | HUNT5 `249eae9` | baseline `c3bdae2` |
|---|---|---|---|---|
| **F-053**, a load through a `wild` `NULL` pointer whose value the program text reads, but that decides nothing on the path run, is sunk or deleted at -O2 (`findings/F-053-wild-used-load-legs-disagree/`) | **reported apart: the check of §27 (D-364)**, scope wild (outside CLAUDE.md's definition) | `m091`–`m100` (`DEFECT:leg_mismatch`) | 0 / 107 / 0 in all five faces (`untaken`, `ignore`, `copy`, `selfsub`, `selfcmp`) | 0 / 107 / 0 |

Its controls: K's `cmp` (107/107 at HUNT5, 107/12 at the baseline: the case an implementation deleting every load gets
wrong), the permitted dead load (107/0 at both) and B's `deadadd` (107/107 at HUNT5: a value read only by a checked add
whose result is unread keeps its load). The -O2 IR at HUNT5 shows two mechanisms: in `untaken` the load is sunk into
the branch that reads it, which the path run never takes; in the other four it is deleted. By my reading one cause:
the load has no side effect for the optimiser to keep. `gen/minimize.py` deletes the read in four faces (the verdict
is unchanged without it, which is the face), so those reproducers keep their bodies whole; the README records it.
Whether §27's sentence or the dereference's lowering changes is for the compiler seat and the author.

### 15.8 F-050 … F-052 at HUNT5

`gen/run_findings.py` at HUNT5 twice and the baseline once, under 20.1.2 (`findings/F-05[012]-*/VERDICTS-249eae9.txt`);
the HUNT5 runs agree for every program, and every baseline line equals the committed `VERDICTS.txt`'s.

| finding | registry at HUNT5 | at HUNT4 `c72639f` (M13) | at HUNT5 `249eae9` |
|---|---|---|---|
| F-050 | DEF-272, FIXED at landing 138 (`2a9d601`) | the two holes 170/170 | the two holes `BORROW-002`; `ctl_elem_direct` and `ctl_whole_callee` `BORROW-002`, `ctl_elem_outlives` 0/0, as at HUNT4 |
| F-051 | DEF-273, FIXED BY D-364 (landing 142, `79cd363`): the permitted disagreement | 107/14, 107/0, 107/14; control 107/107 | the same; grid14 classes the three `PERMITTED:S-140` and the control clean |
| F-052 | DEF-274, FIXED at landing 146 (`915f427`) | the three programs `EMIT-002` | the three programs 0/0; both controls 0/0 |

### 15.9 What M14 does not cover

Not funded (the brief's §3):
- the rest of `KNOWN_DEFECTS.md`'s rebase to HUNT5: DEF-234, DEF-245 and DEF-265, DEF-253 and DEF-254, DEF-256,
  DEF-190, DEF-268, DEF-275, DEF-276 to DEF-290, and DEF-296;
- the Option C re-read of the M11 rows, and the M11 re-spellings;
- F-020's `ctl_j3`, and a RESERVED class;
- the wild→plain roads family, D-339's lock rules, landing 128's buffer ground, and DEF-264;
- the regression leg (recall, F-001 … F-049, M2, M9, M10) at HUNT5.

And grid14's own limits: B is asked at `local` only; T is `int64` and one struct; a `wild` pointer here only ever
holds `NULL` (no load from valid `wild` memory is asked); U has no discard form, since both discard spellings are
refused (`PARSE-002`); one LLVM, and -O0 against -O2 only. Left for the author, through the dispatcher: whether
`CLAUDE.md`'s defect definition should name S-140's exception (no edit is needed for `wild` programs, which it
excludes); FZ-2's counting; `PLAN.md:16` and `README.md:25`; F-020's `ctl_j3`; and, from F-053, whether §27's "USES"
covers a value read only where it decides nothing.

### 15.10 Cost

At 4 jobs, one harness at a time under the lock (each command's wall time, any lock wait included; no `flock` returned 75):

| step | wall |
|---|---|
| HUNT5's build | 64.9 s |
| the canaries | 0.9 s |
| §4's probes: the manager's 22, then 25 templates, each at two compilers | 12.8 + 17.3 s |
| grid14 at HUNT5 twice and at the baseline | 10.5 + 10.6 + 8.0 s |
| F-050 … F-052 at HUNT5 twice and the baseline | 12.4 s |
| triage: the IR probes, five minimisations, F-053 recorded | 2.3 + 72.5 + 8.9 s |
| **in all** | about 221 s, under 4 min of harness time |

The session was dispatched at 03:00:18 EDT on 2026-10-25 and worked to 03:29; nothing ran from 03:29 until `date`
read 07:57:18, an idle gap with no cause found, in which nothing moved (PROGRESS.md's Log); the work resumed at 07:57
and closed after 08:00. PROGRESS.md's M14 section has every command and time.

### 15.11 Reproducing

From a clone at the commit that closes M14, with the compiler cloned to `.work/nitpick`, the baseline built at
`.work/base` (M0's commands) and LLVM 20.1.2 at `.work/llvm-20.1.2`:
```
git -C .work/nitpick worktree add --detach ../hunt5 249eae91559bfc1e3b8a17b12286c21108e4215a
(cd .work/hunt5 && PATH=$PWD/../llvm-20.1.2/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk)
python3 gen/grid14.py --out cells14 && python3 gen/grid14.py --selfcheck
python3 gen/classify14.py --selftest
python3 gen/run.py .work/hunt5 --cells cells14 --llvm .work/llvm-20.1.2 --jobs 4 --out results/249eae9/cells14.jsonl
python3 gen/classify14.py --cells cells14 results/249eae9/cells14.jsonl
python3 gen/run.py .work/base --cells cells14 --llvm .work/llvm-20.1.2 --jobs 4 --out results/c3bdae2/cells14.jsonl
python3 gen/classify14.py --cells cells14 results/c3bdae2/cells14.jsonl
python3 gen/classify14.py --cells cells14 --against13 results/249eae9/cells14.jsonl
python3 gen/classify14.py --cells cells14 --against13 results/c3bdae2/cells14.jsonl
python3 gen/run_findings.py F-050 F-051 F-052 --hunt .work/hunt5 --base .work/base --llvm .work/llvm-20.1.2 --name VERDICTS-249eae9.txt
python3 gen/run_findings.py F-053 --hunt .work/hunt5 --base .work/base --llvm .work/llvm-20.1.2 --name VERDICTS.txt
```
`gen/run.py` appends to its `--out` and skips the cells already there, so a re-run writes to a fresh path and is
compared with `python3 gen/compare13.py`.

## 16. M15 — the DEF-296 family

M15 is the task after M14 (S101). It sweeps the roads by which a VIEW of a pointer parameter's pointee
(`string_bytes(p.s)` with `S->:p`) can be stored into the frame's own storage, and the writes by which that pointee can
then be freed. The aim is to confirm that the fixes of landings 156–163 hold at HUNT6 and to find any road still open.
Every hazard cell is safe code, with no `wild`, no `=>!` and no raw pointer arithmetic. So a cell that is accepted and
reads the allocator's poison is a defect by `CLAUDE.md`, reported normally, not apart as M14's were. M15 ran on
2026-10-28 and 29, on the Team seat, on branch `local-m15`. It ran one harness at a time under the seat's lock, at 4
jobs, under LLVM 20.1.2, from the fuzzer's manager's brief (`fuzz-m15-brief-2026-10-28.md`, sha256 `e0e6a554…`, S101).

### 16.1 The compilers

| role | commit | LLVM | build | `npkc.ll` bytes / sha256 | `npkc.o` | `npkrt.o` | `npkc` |
|---|---|---|---|---|---|---|---|
| HUNT6 | `1480ca8` (`1480ca81aa4d9d82976149f7f6ae5e44b2c5c640`) | 20.1.2 | 64.8 s | 33 468 275 / `fbd42f41e1ea4828…`, equal to notice 164's ladder row | 13 844 112 / `faec89d321a8ce6b…`, equal | 72 656 / `c8e5033ad17c70f8…`, equal | 11 970 864 / `7f7b2ab1b1d322dd…`; the row's is the same size |
| REG155 | `02856cf` (`02856cfc72463f105da70bd9c23c7f2cc1bf8151`) | 20.1.2 | 66.0 s | 32 973 616 / `8f76731c6fc1c7ca…`, equal to notice 156's ladder row | 13 689 368 / `9031ecebf6fbdbe9…`, equal | 72 656 / `c8e5033ad17c70f8…`, equal | 11 843 192 / `32dcfb0b084c60b5…`; the row's is the same size |

- **HUNT6** is the compiler's `origin/main` at the session's fetch: 23:19:57 EDT, committed 2026-10-26 14:05:02 -0400.
  It is landing 163 (DEF-306 + DEF-308) and carries landing 156 (`a5693a6`, the brief's floor).
  - The landings from REG155 to HUNT6 are 156 (DEF-296, DEF-289's first face), 157 (DEF-289's second face), 158
    (DEF-300), 159 (DEF-297, DEF-301, DEF-303), 160 (DEF-302), 161 (DEF-305), 162 (DEF-304) and 163 (DEF-306, DEF-308)
    (S103).
  - **No landing past 163** is in HUNT6, or was in the compiler's `origin/main` at any later fetch. The last fetch
    was at 00:07:42 EDT on 2026-10-29. management_4's word was that landing 164 (`3adfc05`: DEF-309, DEF-310, DEF-311) would land
    about 00:15 EDT.
  - The ladder rows are the workbench BOARD's "THE BASELINE NOTICE 164 MUST QUOTE" and "… 156 MUST QUOTE", and
    `builder.o` equals them too.
- **REG155** is landing 155 (DEF-288, DEF-290). It comes before DEF-296's first fix, so it is the recall and
  regression leg. `c3bdae2` is not run, because the family's spellings are `PARSE-001` there (the manager's
  measurement). HUNT3, HUNT4 and HUNT5 are not run either (S104).
- **LLVM 20.1.2 throughout**, PLAN.md:10's own pin (S104): `.work/llvm-20.1.2` is the machine's `/usr/lib/llvm-20`,
  and its `llvm-config` prints 20.1.2. The canaries pass at both compilers.
- **The go** (S102) is management_3's GO for the Team's week (2026-10-28 20:11:21): "**M15** (fuzz's DEF-296-family
  generator), run on the Team as M14 was." The dispatch adds: "Those words stand as the go for HUNT6 = the
  compiler's origin/main at your fetch. No LLVM go is needed (S104)." `nitpick-fuzz_5`'s release (23:02:44) is
  quoted beside it.

### 16.2 The housekeeping

Commit M15 (1b), wording only:
- **F-053's README** now says a deleted-load implementation would answer 12, not 13 (M14v's F6). 12 is measured at
  `c3bdae2`, by `ctl_wild_used_cmp` and grid14's nine `int64` K cells, each at 107/12.
- **`KNOWN_DEFECTS.md` gains the DEF-296 family block.** It has one row for each of DEF-289 and DEF-296 … DEF-311,
  with the shape and status read in HUNT6's registry. The rows are labelled as the compiler seat's registrations,
  measured where a grid cell exists by M15, and F-050 = DEF-272 is cross-referenced, not repeated. The brief's §3
  labels for DEF-302, DEF-304, DEF-306 and DEF-310 do not match HUNT6's registry, so the rows follow the registry and
  the block says so.
- **M14v's F3 and F5** each get a one-line note: under F-053's "Not registered" entry, and after 15.6.

M15 (4) filled the block's cells column (16.8). No committed record changed.

### 16.3 The rule under test, and the recall gate

**The rule** is MEMORY_REFERENCE.md's D-325 paragraph at HUNT6 (`:269`–`:284`). Every grid15 cell carries it verbatim
as its `rule`, and `--selfcheck` re-reads it from `1480ca8`. A view of a binding is a shared party on its root from
the holder's declaration to the end of its block, and every write-capable access of what it views refuses
(`NITPICK-BORROW-015`). Since landing 156 (DEF-296), a store through an indirection lands where the indirection points
(`record_refs_through_indirection`). So once a view of `p`'s pointee is stored anywhere this frame owns, the pointee
is frozen while the holder lives, and a write that frees the old body (`p.s = …`) must refuse.

**The hazard and its control.** Every hazard cell stores the view by one road, frees the pointee by one write, and then
reads the stored view through grid13's `OBS_V`. The observer gives 21 for the original byte, so `main` exits 0, and 70
for the free poison 170. The twin stores `string_bytes("abcdef")` instead, an owned literal that is never freed, and
must run to 0. A wrong analysis, one that flags the store road rather than the stored borrow, refuses the twin.

**The recall gate**, `gen/classify15.py --recall` (S106), runs ten checks and prints every failing check's tag. It
exits 3 on `REGRESSION`, 1 on any other tag, and 0 otherwise. The ten checks:
- `COMMIT`: each file is tied to its pinned sha;
- `COVERAGE`: each file covers every index id;
- `SEED-RECALL`: the eight DEF-296 seeds are `ACCEPTED:DEFECT:uaf` at REG155;
- `LEAK-RECALL`: every `reg155=="leak"` cell is accepted and reads freed memory at REG155;
- `SILENT-PASS`: no hazard cell is `ACCEPTED:clean`, `other` or `timeout` at either compiler;
- `TWIN`: every twin is clean at both compilers;
- `CODE-H6`: every expected code is named at HUNT6;
- `CODE-REG`: only `BORROW-` codes are named at REG155;
- `UNANCHORED`: no unanchored hazard is refused at both compilers;
- `REGRESSION`: no hazard cell is refused at REG155 and accepted at HUNT6.

It also lists the FINDINGS, the hazard cells accepted at HUNT6. `--selftest` builds synthetic records in memory and
proves that each check fires with exactly its own tag set and exit code: 18 cases, 18 pass (PROGRESS.md has the
output).

### 16.4 grid15

`gen/grid15.py` imports `Prog`, `X`, `FAILSAFE13`, `OBS_V`, `Skip` and `WILD_RE` from grid13. It defines its own
`S = { string:s; }` and `Holder = { (fixed uint8[]):v; int32:k; }`.

**The axes:**
- R, 20 store roads: `bare`, `fld`, `pl`, `pld`, `plw`, `pf`, `tl`, `sle`, `rge`, `lst`, `cad`, `cpl`, `csl`,
  `cslv`, `cps`, `cpp`, `cbv`, `cbp`, `mth` and `mpl`;
- W, 12 freeing writes: `dir`, `whole`, `alias`, `walias`, `callee`, `calias`, `cwhole`, `method`, `cres`, `cresc`,
  `cresm` and `cresf`;
- B, the placement: `same`, or `inner` (the store in an inner block that ends before the write);
- V, the view: `pp` (the hazard), `lo` (deferred) and `twin`.

PROGRESS.md's M15 section spells out every road and write.

**Where the expectations come from:**
- A cell's `expect` is a reading of the rule, written before the first run: `REFUSE` for a hazard, `SAFE` (exit 0)
  for a twin.
- Its `expect_codes` and `reg155` come from the manager's expectations table, `gen/m15_expect.tsv`. The table has 104
  rows, each citing the log line it was read from, and `m15_expect_check.py` prints "104 rows, 0 mismatches". No cell
  has a code override.
- Every spelling was compiled and run at both compilers before any grid run. Every grid cell equals a probed program
  byte for byte, apart from its `mod:` line.

| section | what | expectation (before any run) | generated |
|---|---|---|---|
| S | the eight DEF-296 faces (the compiler's `.internal/handoff_35/probes_sib/`, through the manager's `m15-seeds/`), F-050's two holes, and the six candidates (`m15-probes-l163-r2/`), byte for byte with their sha256 | `REFUSE`, `BORROW-015` (F-050's `BORROW-002`); `reg155` "leak" (F-050's "refuse") | 16 |
| R | the 20 roads × B (`same` for all 20, `inner` for the 12 indirection roads) × V (`pp`, `twin`), with W = `dir` | `pp` `REFUSE` `BORROW-015`; twin `SAFE`, 0 | 64 |
| W | R = `fld` × the ten writes `whole` … `cresm` × `same` × V | the same | 20 |
| **all** | 1 440 combinations (20 × 12 × 2 × 3) and 16 seeds: 84 emitted, **1 356 in `cells15/SKIPPED.txt`** | 58 `REFUSE` (42 `pp` keys and 16 seeds), 42 `SAFE` | **100** |

**The skip reasons:**
- 480 have the `lo` view, which is deferred to a later milestone;
- 760 have a write other than `dir` on a road other than `fld`;
- 80 have `cresf`: `(raw ids(p)).s = …` is `TYPE-024`, not a place;
- 36 have an inner placement on a road without one: `bare`, `fld`, `cad`, `csl`, `rge`, `mth`, `cbv` and `cbp`.

**The exit codes seen:** 0 for an intact view, 70 for the poison read through `OBS_V`, and 170 for the seeds' own
observer. 22 to 25 never occur.

### 16.5 Results by section and compiler

From `results/<commit>/classified15.jsonl`. In each run, generated = the sum of the class counts, and no cell is
`LOUD`, `CRASH`, `timeout` or `other`. HUNT6's two runs agree in all 100 cells.

| class | S at HUNT6 | R at HUNT6 | W at HUNT6 | **HUNT6** | S at REG155 | R at REG155 | W at REG155 | **REG155** |
|---|---|---|---|---|---|---|---|---|
| `ACCEPTED:DEFECT:uaf` | 6 | 5 | 3 | **14** | 14 | 26 | 8 | **48** |
| clean | | 32 | 10 | **42** | | 32 | 10 | **42** |
| refused | 10 | 27 | 7 | **44** | 2 | 6 | 2 | **10** |
| **generated** | **16** | **64** | **20** | **100** | **16** | **64** | **20** | **100** |

**By road**, for the `pp` cell with W = `dir`. In this table "refused" is `BORROW-015`, "70" is `ACCEPTED:DEFECT:uaf`
at 70/70, and each column gives HUNT6 / REG155:

| R | one block | inner block | R | one block | inner block |
|---|---|---|---|---|---|
| `bare` | refused / refused | — | `cad` | refused / refused | — |
| `fld` | refused / refused | — | `cpl` | refused / 70 | refused / 70 |
| `pl` | refused / 70 | refused / 70 | `csl` | refused / 70 | — |
| `pld` | refused / 70 | refused / 70 | `cslv` | refused / 70 | refused / 70 |
| `plw` | refused / 70 | refused / 70 | `cps` | refused / refused | **70 / 70** |
| `pf` | refused / 70 | refused / 70 | `cpp` | refused / refused | **70 / 70** |
| `tl` | refused / 70 | **70 / 70** | `cbv` | **70 / 70** | — |
| `sle` | refused / 70 | refused / 70 | `cbp` | **70 / 70** | — |
| `rge` | refused / 70 | — | `mth` | refused / refused | — |
| `lst` | refused / 70 | refused / 70 | `mpl` | refused / 70 | refused / 70 |

**By write**, R = `fld`, one block, HUNT6 / REG155:
- refused / refused: `dir`, `whole` and `callee`;
- refused / 70: `alias`, `walias`, `calias`, `cwhole` and `method`;
- **70 / 70**: `cres`, `cresc` and `cresm`.

**The seeds:**
- The eight DEF-296 faces are refused (`BORROW-015`) at HUNT6 and read 170/170 at REG155.
- F-050's two holes are refused (`BORROW-002`) at both compilers.
- The six candidates read 70/70 at both.

Every one of the 42 twins is clean, 0/0, at both compilers.

**The predictions**, from the manager's probes at landing 163:
- **P1** ✓ `--selfcheck` passes, and no cell is `wild`: every cell's scope is "plain".
- **P2** ✓ The eight DEF-296 seeds read 170/170 at REG155 (`DEFECT:uaf`) and are refused with `BORROW-015` at HUNT6.
  F-050's two holes are `BORROW-002` at both compilers.
- **P3** ✓ At HUNT6 every same-block `pp` road is refused but `cbv` and `cbp`. The other holes are `tl`, `cps` and
  `cpp` in an inner block, and the writes `cres`, `cresc` and `cresm`. The same-block `cps` and `cpp` and the `fld` ×
  `cwhole` write are refused. No landing past 163 reached `origin/main` by the last fetch, so nothing is re-measured
  past 163.
- **P4** ✓ At REG155 the twelve same-block `dir` roads fixed at 156–159 read 70/70: `pl`, `pld`, `plw`, `pf`, `tl`,
  `sle`, `rge`, `lst`, `cpl`, `csl`, `cslv` and `mpl`. `bare`, `fld`, `mth` and `cad` are refused. The seeds read
  170/170.
- **P5** ✓ All 42 twins are clean at both compilers. `bare`'s hazard is refused at both, and no cell has an
  `expect_codes` override.
- **P6** ✓ HUNT6's two runs agree: 0 of 100 cells differ.
- **P7** ✓ The open DEF-298, DEF-299, DEF-309 and DEF-305 keys are deduplicated and not filed (16.7). There is no new
  finding, which is inside the prediction of zero to one.

### 16.6 The recall gate

Run as `python3 gen/classify15.py --cells cells15 --recall results/1480ca8/classified15.jsonl
results/02856cf/classified15.jsonl`, it **exits 0**:
```
ok  COMMIT — the HUNT6 file's commit 1480ca8 (pinned 1480ca8), the REG155 file's 02856cf (pinned 02856cf)
ok  COVERAGE — 100 index ids; HUNT6 100 records (0 missing, 0 extra, 0 doubled), REG155 100 records (0 missing, 0 extra, 0 doubled)
ok  SEED-RECALL — 8 of the 8 named DEF-296 seeds ACCEPTED:DEFECT:uaf at REG155
ok  LEAK-RECALL — 48 of 48 reg155=="leak" cells ACCEPTED:DEFECT:* at REG155
ok  SILENT-PASS — 0 hazard cells ACCEPTED:clean/other/timeout at either compiler (of 58)
ok  TWIN — 42 of 42 twins clean at both compilers
ok  CODE-H6 — 44 of 44 hazard cells refused at HUNT6 name every expected code
ok  CODE-REG — 10 of 10 hazard cells refused at REG155 name only NITPICK-BORROW- codes
ok  UNANCHORED — 0 pp cells with reg155 None refused at both compilers
ok  REGRESSION — 0 hazard cells refused at REG155 and ACCEPTED:DEFECT:* at HUNT6
FINDINGS: 14 hazard cells ACCEPTED:DEFECT:* at HUNT6 (for triage, not a failure)
```
**The pairs** over the 58 hazard cells:
- 14 are accepted at both compilers: the open holes in 16.7.
- 34 are accepted at REG155 and refused at HUNT6, so a fix landed in (155, 163]. These are 26 `pp` cells and the
  eight DEF-296 seeds.
- 10 are refused at both, fixed before 155. These are `bare`, `fld`, `cad` and `mth`, `cps` and `cpp` in one block,
  `fld` × `callee` and `whole`, and F-050's two.
- **None is refused at REG155 and accepted at HUNT6, so there is no regression.**

Every hazard verdict of the two record runs is the table's row for its key: 116 records, 0 differ.

### 16.7 Candidates and findings

**M15 files no finding** (S107). HUNT6's fourteen accepted cells are eight keys, and each one's shape is OPEN in
HUNT6's registry. Under PLAN 5.2 (a) that makes each one known: note the cell id and move on. P7 binds the same way, so
F-054 is not used.

Each of the eight is `ACCEPTED:DEFECT:uaf`: a use-after-free in safe code at both legs (70/70), at HUNT6 and at REG155
alike. That is a defect by `CLAUDE.md`, and the compiler seat's registration.

| key | cells | control: the twin, clean at both (and a refused neighbour) | the registry's row at HUNT6 | what governs it |
|---|---|---|---|---|
| `pp:cbv:dir:same` | `n075` | `n076` | DEF-298, OPEN: its registered shape r1, a by-value struct parameter's slice field handed on to a storing callee | open at 163; the compiler seat's M3 plan, with DEF-299 |
| `pp:cbp:dir:same` | `n077` | `n078` | DEF-298, OPEN: the pointer twin it measured at 158 (t298b) | the same |
| `pp:cps:dir:inner` | `n069`, `q11` | `n070` (`n067`, one block, refused) | DEF-299, OPEN: its registered shape pf | the same |
| `pp:cpp:dir:inner` | `n073`, `q12` | `n074` (`n071`, one block, refused) | DEF-299, OPEN: the pointer twin it measured at 158 (t299c) | the same |
| `pp:tl:dir:inner` | `n043`, `q05` | `n044` (`n041`, one block, refused) | DEF-299, OPEN, by the brief's pre-map | the same |
| `pp:fld:cres:same` | `n019`, `q17` | `n020` | DEF-309, OPEN: a direct whole-pointee write through a call-result pointer | open at 163; landing 164, by the compiler seat's word, not reached by the last fetch |
| `pp:fld:cresc:same` | `n021`, `q19` | `n022` (`n011`, the named `callee`, refused) | DEF-305, FIXED at 161: its writer face, with the result rooted at a pointer PARAMETER | the fix at 161 does not reach it: an incomplete fix (the brief), not a new defect |
| `pp:fld:cresm:same` | `n023`, `q20` | `n024` (`n017`, the named `method`, refused) | DEF-305, FIXED at 161: its receiver face, the same parameter-rooted gap | the same |

The manager's r2 log reads all six candidates at 70/70 at `249eae9` (161) as well, the manager's measurement.

**Two flags for D6**, both readings rather than measurements:
- **DEF-299's text and `tl`-inner.** The row's text names a pointer parameter's pointee that a callee stores through.
  `tl`-inner instead stores directly through a pointer local's pointee (`bp.p.v`), and `pf`-inner, one pointer level
  on a local struct, is refused. The cause reads the same: the store is recorded on the pointee `b`, whose block ends,
  and not on `h`, which its field points to.
- **DEF-305's status and `cresc`/`cresm`.** DEF-305's row says FIXED and names no parameter-rooted exception. DEF-302's
  row says that the landing-160 resolver gives no target for a pointer rooted at a PARAMETER, which may be the cause.
  That is inferred, not bisected.

All eight go to the fuzzer's manager through the dispatcher, for D6.

### 16.8 The family's status at HUNT6

The registry's status at `1480ca8`, and the grid15 cells by the registry's shapes (read, not bisected). The verdicts
column gives HUNT6 / REG155; `KNOWN_DEFECTS.md`'s family block has the shapes.

| DEF | at HUNT6 | grid15 cells | HUNT6 / REG155 |
|---|---|---|---|
| DEF-289 | FIXED: face 1 at 156, face 2 at 157 | `n045`, `n047` (`sle`); `n061` (`csl`); `n063`, `n065` (`cslv`) | refused / 70 |
| DEF-296 | FIXED at 156 | 15 cells: `pl`, `pld`, `plw`, `pf`, `lst`, `cpl`, `mpl` in both placements, and `tl` in one block; and the eight seeds | refused / 70 (the seeds 170) |
| DEF-297 | FIXED at 159 | no grid cell | — |
| DEF-298 | **OPEN** | `n075` `cbv`, `n077` `cbp` | **70 / 70** |
| DEF-299 | **OPEN** | `n069` `cps`, `n073` `cpp` and `n043` `tl`, inner (with `q11`, `q12`, `q05`); in one block, `n067` and `n071` | **70 / 70**; one block, refused / refused |
| DEF-300 | FIXED at 158 | `n049` `rge` | refused / 70 |
| DEF-301 | FIXED at 159 | no grid cell | — |
| DEF-302 | FIXED at 160 | `n007` `alias`, `n009` `walias`, `n013` `calias`, `n017` `method` | refused / 70 |
| DEF-303 | FIXED at 159 | no grid cell | — |
| DEF-304 | FIXED at 162 | no grid cell | — |
| DEF-305 | FIXED at 161 | `n021` `cresc`, `n023` `cresm` (with `q19`, `q20`), parameter-rooted | **70 / 70** |
| DEF-306 | FIXED at 163 | no grid cell | — |
| DEF-307 | **OPEN** | no grid cell | — |
| DEF-308 | FIXED at 163 | `n015` `cwhole` | refused / 70 |
| DEF-309 | **OPEN** | `n019` `cres` (with `q17`) | **70 / 70** |
| DEF-310 | **OPEN** | no grid cell | — |
| DEF-311 | not registered at HUNT6 | no grid cell | — |

The early-fixed controls are refused at both compilers. They are `bare`, `fld`, `cad` and `mth` with `dir`, and `fld`
with `whole` and `callee`, closed before 155 by D-325's base, landing 154's direct field store and the store-matrix
callee store.

### 16.9 What M15 does not cover

Not funded (the brief's §3):
- the rest of `KNOWN_DEFECTS.md`'s rebase to HUNT6: DEF-234, DEF-245 and DEF-265, DEF-256, DEF-190, DEF-268, and the
  non-family defects in the 275–295 range;
- the Option C re-read of the M11 rows, and the M11 re-spellings;
- F-020's `ctl_j3`, a RESERVED class, the wild→plain roads family, D-339's lock rules, landing 128's buffer ground,
  and DEF-264;
- the regression leg of the old grids (recall, F-001 … F-053, M2, M9, M10, M13, M14) at HUNT6.

**grid15's own limits:**
- The frame-local `lo` view is deferred: 480 combinations are skipped, and the manager's log keeps its measurements.
- The writes are asked on the `fld` road only, and the roads with `dir` only.
- The inner placement is asked on the twelve indirection roads only.
- There is one view, a `string`'s bytes, and one holder.
- No cell reaches `destroy`, a spawn or a `List` reallocation, so DEF-297, DEF-301, DEF-303, DEF-304, DEF-306,
  DEF-307 and DEF-310 are not measured.
- `cresf` is `TYPE-024`.
- One LLVM is used, and only -O0 against -O2.
- Landing 164 had not reached the compiler's `origin/main` by the last fetch, so nothing is measured past 163.

**Left for the author, through the dispatcher.** None of these is M15's to settle:
- `CLAUDE.md`'s defect definition and S-140 (M14's item);
- FZ-2's counting;
- `PLAN.md:16` and `README.md:25`;
- F-020's `ctl_j3`.

F-053's §27 "USES" was ruled Q77 (b), and nothing is open there.

### 16.10 Cost

At 4 jobs, one harness at a time under the lock. Each time is the command's wall time, any lock wait included, and no
`flock` returned 75.

| step | wall |
|---|---|
| HUNT6's build | 64.8 s |
| REG155's build | 66.0 s |
| the canaries | 0.9 s |
| §4's probe batch: 96 files at two compilers | 61 s |
| grid15 at HUNT6 twice, and at REG155 | 8 + 7 + 9 s |
| triage | no compiler run |
| **in all** | **about 217 s**, under 4 min of harness time |

**The session's times:**
- dispatched at 23:12:50 EDT on 2026-10-28;
- stopped at 23:17:40 on a guard refusal, and resumed on the dispatcher's ruling at 23:18:58 (PROGRESS.md's Log);
- the commits: M15 (1) at 23:29:53, (1b) at 23:36:23, (2) at 23:52:58, (3) at 23:55:35 and (4) at 00:02:07 on
  2026-10-29;
- this section's commit closes M15.

PROGRESS.md's M15 section has every command and time.

### 16.11 Reproducing

Start from a clone at the commit that closes M15, with the compiler cloned to `.work/nitpick` and LLVM 20.1.2 at
`.work/llvm-20.1.2`. `.work/H6` and `.work/REG` hold the short shas that `--recall`'s `COMMIT` check reads.
```
git -C .work/nitpick worktree add --detach ../hunt6 1480ca81aa4d9d82976149f7f6ae5e44b2c5c640
git -C .work/nitpick worktree add --detach ../reg155 02856cfc72463f105da70bd9c23c7f2cc1bf8151
(cd .work/hunt6 && PATH=$PWD/../llvm-20.1.2/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk)
(cd .work/reg155 && PATH=$PWD/../llvm-20.1.2/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk)
echo 1480ca8 > .work/H6; echo 02856cf > .work/REG
python3 gen/grid15.py --out cells15 && python3 gen/grid15.py --selfcheck
python3 gen/classify15.py --selftest
python3 gen/run.py .work/hunt6 --cells cells15 --llvm .work/llvm-20.1.2 --jobs 4 --out results/1480ca8/cells15.jsonl
python3 gen/classify15.py --cells cells15 results/1480ca8/cells15.jsonl
python3 gen/run.py .work/reg155 --cells cells15 --llvm .work/llvm-20.1.2 --jobs 4 --out results/02856cf/cells15.jsonl
python3 gen/classify15.py --cells cells15 results/02856cf/cells15.jsonl
python3 gen/classify15.py --cells cells15 --recall results/1480ca8/classified15.jsonl results/02856cf/classified15.jsonl
```
`gen/run.py` appends to its `--out` and skips the cells already there. So a re-run writes to a fresh path and is
compared with `python3 gen/compare13.py`.
