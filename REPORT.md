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

## 12. M11 — the reference, checked against the compiler (in part)

Written 2026-09-26 by session 7 and extended by sessions 8 and 9 (2026-10-02), all on
the author's machine (48 cores), from the committed scripts. **M11 is not finished.**
These denominators cover the ranges extracted so far, 7 087 of the fourteen references'
10 419 lines. Session 8 corrected the count, which had included the empty element after
each file's final newline (10 433 before):
- extracted whole: BUILTIN, CONCURRENCY, IO, MACRO; by session 8, MEMORY, OP and
  CONTROL; by session 9, MODULE, LEXICAL, AST and BUILD;
- extracted in part: TYPE 1–660 and VERIFICATION 1–1247;
- not yet extracted: TYPE 661–2122, VERIFICATION 1248–2351 and TRAITS.

The records are:
- `m11/CLAIMS.md` (every claim with its line, quote and expectation) and
  `m11/RESULTS.md` (the results, claim by claim);
- `results/9126350/m11.jsonl` (the final run), with runs 1–3 beside it;
- `results/c3bdae2/m11-disagree.jsonl`, `results/1b4f0c6/m11-disagree.jsonl` (session 7)
  and `results/93bcb66/m11-disagree.jsonl` (sessions 8 and 9): the disagreeing claims at
  the baseline and at the compiler's newest `main` of each session;
- `gen/m11_triage.py` (the class of each disagreement);
- `findings/F-018` … `F-040`.

### 12.1 The denominators

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
| TYPE (1–660) | 322 | 19 | 74 | 229 | 19 | 303 | 242 | 61 |
| VERIFICATION (1–1247) | 585 | 9 | 97 | 479 | 128 | 457 | 435 | 22 |
| **total** | **2 560** | 111 | 628 | 1 821 | **363** | **2 197** | **1 969** | **228** |

Untestable, each with its reason in `m11/CLAIMS.md`:
- `z3` 99: needs `npkg verify` with the pinned z3;
- `vague` 57: no checkable outcome;
- `internal` 67 (AST's 19 are rows that list only a node's fields);
- `tree` 61: the compiler's own tree;
- `tool` 44: a running driver process, a package in the compiler's tree, or `npkg test`, which
  builds the compiler first (BUILD's 28);
- `unobservable` 24;
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
BUILD's 1 was a script that took a diagnostic's note for its error's place. LEXICAL's 4 were a contract measure calling a helper, a `%%` left in a check,
and a generic identity passing out its lent parameter (2). MODULE's 24 were three
mistakes:
- `hidden`, a reserved word (14);
- `nbridge.npk`'s import of `nsys.npk`, which the scripts did not copy (9);
- failsafe arms that REACH-002 asks for (8, seven of them also among the nine).

### 12.2 The disagreements, by class

| class | claims |
|---|---|
| compiler: a silent wrong answer (F-018 … F-021) | 6 |
| compiler: memory — a use after destroy (F-022); **a use after free through a `=> dyn` cast (AST's F-037)** | 1 + 1 |
| compiler: accepted, then invalid IR (F-023) | 1 |
| compiler: npkc traps, exit 3 (F-024; AST's F-038) | 4 + 3 |
| compiler: a flag that refuses every program (F-025) | 2 |
| compiler: a unit annotation accepted and ignored (F-026) | 1 |
| compiler, lower priority (F-027; MODULE's F-034; LEXICAL's F-036; AST's F-039) | 16 + 5 + 4 + 5 |
| documentation (F-028; MEMORY's F-030; OP's F-031; CONTROL's F-032; MODULE's F-033; LEXICAL's F-035; AST's F-040) | 94 + 8 + 5 + 6 + 7 + 6 + 18 |
| known (DEF-123, DEF-131, DEF-133; MEMORY's DEF-148; OP's DEF-131 twice; CONTROL's DEF-133, DEF-130 twice, DEF-135; MODULE's DEF-153; LEXICAL's DEF-131; AST's DEF-131 and DEF-153) | 7 + 1 + 2 + 4 + 1 + 1 + 2 |
| not a finding: refused at compile time where the text says it traps | 2 |
| not a finding: the program tests more than its sentence, or cannot be written | 10 + 2 (OP) + 2 (MODULE) + 1 (AST) |
| **total** | **228** |

**Every disagreement gives the same result at the baseline** (one, `cc0042`, with other
codes), so each is old. Session 7's all stand at its newest `main` `1b4f0c6`. Session 8's
MEMORY, OP and CONTROL rows all stand at `93bcb66` but six, all known: `me0461`,
DEF-148's shape, is refused there (`BORROW-016`); OP's two `<=>` claims (DEF-131)
compile and run; and CONTROL's DEF-130 pair and DEF-135 agree there. MEMORY's run 1 also found F-029, a reserved word accepted as a binding's
name, which no final disagreement carries, since the programs it broke were
re-spelled. Session 9's MODULE rows all stand at the baseline and at `93bcb66` but one,
known: `md0296b`, DEF-153's string literal in `cstring` position, compiles at `93bcb66`.
LEXICAL's all stand at both but one, known: `lx0178`, DEF-131's `<=>`, compiles and runs
at `93bcb66`. AST's all stand at both but its two known, which compile at `93bcb66`.

**AST's run found the session's one memory fault, F-037.** A trait object built by an
explicit cast, `x => dyn Trait`, points at freed storage, and its method reads the
allocator's poison (0xAA in every byte). This holds at HUNT2, the baseline and `93bcb66`,
on both legs. The implicit coercion `dyn Trait:d = move(x);` is correct. It also found a
second npkc trap shape, F-038: `give` or `fall` outside a pick arm.

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
| F-026 | `tfp64<Meters>` accepted and its unit ignored: Meters + Seconds compiles | compiler: a refusal missing | 0, 10/10 | the same | the same |
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
| F-040 | AST's eighteen stale claims (retired spellings, the error model before D-179, the extern rows before D-149, and four more) | documentation | per row | the same | the same (at `93bcb66`) |

### 12.4 What these claims do not cover

- **The ranges not yet extracted** (above), about 3 330 lines: at the drafts' density,
  roughly 1 650 more claims.
- **BUILD's own process.** 59 of BUILD's 97 claims are the compiler's ladder, its test
  runners and its verified build, which a scratch project cannot reach (`npkg build` reads
  the compiler tree's `runtime/npkrt.ll`). Its 38 tested claims are `npkg`'s refusals
  before a build, the `[[test]]` schema and stage names, and what `npkc` emits. All 38
  agree.
- **The verified build.** 91 claims need `npkg verify` with the pinned z3, and are
  untestable here. Claims about what the compiler writes for verification were tested
  through `npkc --obligations`, which needs no z3.
- **A program per claim.** One agreeing program shows the claim for that program, not
  for every program. The refusals that agreed were screened for a first diagnostic of
  another kind (a parse, lex, resolve or reach error). One was found (`mc0312b`), and
  it now agrees for its own reason. Sessions 8 and 9 screened theirs the same way and
  found four more (`me0179`, `ct0032f`, `md0099b`, `md0273`), each re-spelled.
