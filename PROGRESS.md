# PROGRESS

The live state of `PLAN.md`. Tick a box only when its step is done and
committed. A session that starts here resumes at the first unticked box.

## Milestones

- [x] **M0** — the two compilers built and commissioned
- [x] **M1** — the recall suite (`known/`) run at both compilers and matched
- [x] **M2** — the generator, the runner and the classifier
- [x] **M3** — the recall gate: the grid re-finds every known defect at `c3bdae2`
- [x] **M4** — CALIBRATION CHECKPOINT: ~100 cells at HUNT, then **stop and wait**
  — 4.1 and 4.2 done and pushed (session 1); 4.3: on 2026-09-26 the author said
  to continue with M5 and M6, at the same HUNT `6fb85d3` (session 2).
- [x] **M5** — the hunt: 956 cells at HUNT, 82 anomalies, 62 known, 20 new
  in 2 findings (F-001, F-002), both also present at the baseline
- [x] **M6** — the report: [`REPORT.md`](REPORT.md)
- [x] **M8** — the re-hunt at HUNT2 `9126350`, the compiler carrying the fixes (session 3):
  956 cells, 0 anomalies, every cell as expected; 148 moves from HUNT (136
  expected, 12 bisected to DEF-105's fix); no new finding
  - [x] 8.1 HUNT2 recorded (it carries 3g, 3h, 4b and 5c) and built; the baseline built too (8.3 applies)
  - [x] 8.2 the recall suite at HUNT2: 19/19 rows match "once fixed"; F-001's 13 and F-002's 4 defect programs refused, every control as recorded
  - [x] 8.3 DEF-108 is in HUNT2: every generated function already leaves explicitly (0 of 1 000 programs draw `FLOW-001`), so the generator is unchanged; the baseline re-run is identical in 956/956 cells
  - [x] 8.4 the grid at HUNT2: 562 clean, 394 refused, 0 anomalies
  - [x] 8.5 HUNT2 against `6fb85d3`, cell by cell: 148 moved, 136 expected, 0 missing, 12 changed codes explained (bisected to 3h)
  - [x] 8.6 the anomalies at HUNT2 through M5's five steps: none to take
  - [x] 8.7 `REPORT.md` §9; stop (M9 waits for the author)
- [x] **M9** — the ownership grid widened into its named gaps (session 4): 7 571
  cells; the recall gate holds; at HUNT2 197 anomalies in four families; eight
  findings (F-003–F-010), two of them memory faults at HUNT2 (F-003, F-004)
  - [x] 9.1 the leak observer (the `heap:` line read from the runtime and 0.1.4b; a 1 MiB probe after `run`; calibrated by controls)
  - [x] 9.2 the reuse-proof read (a same-sized sentinel; read-now at the loop places)
  - [x] 9.3 types, 9.4 places, 9.5 operations (sections B–E of `gen/grid9.py`)
  - [x] 9.6 the recall gate kept: every known shape flagged at the baseline; every expectation written in the generator before the first run
  - [x] 9.7 the grid at the baseline and HUNT2, triaged by M5's five steps; `REPORT.md` §10; stop (M10 waits for the author)
- [x] **M10** — silent wrong answers (session 5): 229 items, 223 testable; at HUNT2
  212 agree and 11 disagree; the DEF-108 recall holds; seven findings (F-011–F-017),
  four of them silent wrong answers and one an out-of-bounds read, all present at
  the baseline and at the compiler's newest `main`
  - [x] 10.1 the checklist (`m10/CHECKLIST.md`, `gen/m10.py`): 229 items, 223 testable and 6 untestable with reasons, each citing the reference sentence located by its text at both compilers
  - [x] 10.2 one program per testable item, its expected verdict written from the text before the first run; run at the baseline and HUNT2, both legs
  - [x] 10.3 DEF-108's shapes flagged at the baseline and refused `FLOW-001` at HUNT2
  - [x] 10.4 `REPORT.md` §11; stop (M11 waits for the author)
- [ ] **M11** — the reference, checked against the compiler. **In part.**
  - Session 6 stopped part-way on the author's word, the cloud credit nearly spent.
  - Session 7 (local, branch `local-m11`) reviewed, ran and triaged the drafted ranges:
    F-018 … F-028.
  - Session 8 (2026-10-02, on the workbench's brief from `nitpick-libs_12`, S57)
    extracted MEMORY, OP and CONTROL in turn, each to a clean point: F-029 … F-032. Its
    scope is done.
  - Session 9 (2026-10-02, the workbench's next brief, S60) extracts the ranges not
    started, smallest first. MODULE, LEXICAL and AST are done, each to a clean point:
    F-033 … F-040, among them F-037, a use after free.
  - Extracted so far: 6 405 of 10 419 lines; 2 463 claims, 2 159 tested, 1 931 agree,
    228 disagree.

  Resume from "M11 — the state at the stop" below.
  - [ ] 11.1 every code example, normative claim and table row of the fourteen references at HUNT2 in `m11/CLAIMS.md`, with its file and line — BUILTIN, CONCURRENCY, IO, MACRO, MEMORY, OP, CONTROL, MODULE, LEXICAL, AST whole, TYPE 1–660, VERIFICATION 1–1247 done; TYPE 661–2122, VERIFICATION 1248–2351, TRAITS and BUILD not started
  - [ ] 11.2 a program per testable claim, its expected outcome from the text, committed before the first run; run at HUNT2 — done for the extracted ranges (the final run: 1 931 agree, 228 disagree, all triaged)
  - [ ] 11.3 `REPORT.md` §12; stop — §12 written for the extracted ranges

## Compilers

| role | commit | subject | `npkc.ll` bytes / sha256 | build time |
|---|---|---|---|---|
| baseline | `c3bdae2` (`c3bdae270d63c93ab6e89825fddeec9425e2c6fd`), 2026-09-25 07:06:41 -0400 | 1.5.8d steps 1-3: the close of cycle 1.5 | 28 111 929 / `4029fc70efbe9cd3…` | 67 s |
| hunt | `6fb85d3` (`6fb85d3d834fb7d5568ab996005f800d6d269e8f`), 2026-09-25 18:25:47 -0400 | 1.6.0 step 3f: DEF-99 — `NITPICK-TYPE-084` refuses the move out of `fixed` | 28 132 333 / `25eb7ee168604005…` | 69 s |
| HUNT2 (M8) | `9126350` (`9126350d11d12d20bbcc087dc261405bf2729f29`), 2026-09-26 03:42:01 -0400 | 1.6.1 step 0, the NIKOS half (D-324) — docs and `meta/roadmap/1.6/` tools over `2eea6f4` (1.6.1 step 0: DEF-107, `NITPICK-BORROW-015`) | 28 857 206 / `2448b3b60d9eb189…` | 75.8 s |
| newest `main` (M10, findings only; S37) | `9f6f370`, 2026-09-26 06:04:05 -0400 | 1.6.1 step 0c, the record of S-107's and S-108's approval — over `b564746` (1.6.1 step 0c: DEF-116, `NITPICK-TYPE-014`; DEF-117) | 28 872 365 / `7bab110a1e45cc9d…` | 88.9 s |

Other build products (M0.5):

| role | `npkc` bytes / sha256 | `npkrt.o` bytes / sha256 |
|---|---|---|
| baseline | 9 724 232 / `0cbc150ced5d20f7…` | 72 576 / `162b897539285a77…` |
| HUNT2 | 9 972 944 / `20d35e2822b99080…` | 72 576 / `162b897539285a77…` |
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

**Rebuilt in session 2 (2026-09-26, the cloud VM below), by M0's commands.**
The compiler's `origin/main` was still `6fb85d3` when cloned (03:36 UTC), so
HUNT is unchanged. Build times: base 60.1 s, hunt 64.7 s (run one after the
other). **All six products are byte-identical to session 1's:** `npkc.ll`
28 111 929 / `4029fc70efbe9cd3…` and 28 132 333 / `25eb7ee168604005…`;
`npkc` 9 724 232 / `0cbc150ced5d20f7…` and 9 739 968 / `a81223d352d316be…`;
`npkrt.o` 72 576 / `162b897539285a77…` for both. LLVM: `llvm-config
--version` prints `20.1.2` (tarball sha256 `3a392f151375eeed…`, 2 021 628 328
bytes; see S13). Canaries: the same four verdicts at both compilers. The
recall suite re-run at both compilers is identical line for line to
`results/known-c3bdae2.txt` and `results/known-6fb85d3.txt` (19/19 rows each).
The first 100 cells re-run at HUNT are identical to the committed records
(npkc rc, codes, -O0, -O2) in 100 of 100 cells.

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

## M4 — calibration checkpoint (4.1, 4.2 done; waiting at 4.3)

The first 100 cells in id order (`c0001`–`c0100`, all `str`: local,
fixed_scalar, fixed_elem, lent_param, move_param, ptr_param, and the first of
for_binding) ran at HUNT `6fb85d3` in 5.4 s: `results/6fb85d3/`. `origin/main`
was re-fetched after the run and is still `6fb85d3`.

| class at HUNT | cells |
|---|---|
| clean | 56 |
| refused | 40 |
| DEFECT:double_free | 3 |
| DEFECT:uaf | 1 |

Against the same 100 at the baseline: the 8 DEF-99 cells (`c0019`–`c0022`,
`c0035`–`c0038`) moved from DEFECT/clean to `refused NITPICK-TYPE-084`, as the
fix says. Nothing else moved.

The four DEFECTs at HUNT:

| cell | HUNT -O0/-O2 | baseline -O0/-O2 | known? |
|---|---|---|---|
| `c0059_str_lent_param_at_free_ra` | 70/70 uaf | 70/70 | DEF-102 (`@x` of a lent param to a freeing callee; fix 3g not in HUNT) |
| `c0060_str_lent_param_at_free_dx` | 95/95 double_free | 95/95 | DEF-102, as above |
| `c0039_str_fixed_elem_assign_ra` | 95/95 double_free | 95/95 | **not in `KNOWN_DEFECTS.md`** |
| `c0040_str_fixed_elem_assign_dx` | 95/95 double_free | 95/95 | **not in `KNOWN_DEFECTS.md`**, same shape |

`c0039`'s shape: `FA[i] = raw nw();` where `fixed string[2]:FA` is a module
binding. It compiles at both compilers and exits 95 on both legs; the whole
binding's assignment (`c0023`) is refused `ASSIGN-002` and its address
(`c0025`, `c0041`) `TYPE-071`. Measured once per compiler per leg; not yet
minimised, repeated or taken through M5's five steps. *Inferred, not measured:*
the element assignment drops the old element, a string literal in a `constant`
global that was never allocated, and the allocator stops as `Unreachable`,
the same end DEF-99's -O2 leg reaches.

## M5 — the hunt at HUNT `6fb85d3` (session 2)

**5.1 — the rest of the grid.** The 856 cells `c0101`–`c0956` ran at HUNT in
43 s (4 jobs, the cloud VM), appended to `results/6fb85d3/cells.jsonl`, which
now holds all 956 cells. `results/6fb85d3/SUMMARY.md` and `classified.jsonl`
are regenerated from it.

| class | at HUNT `6fb85d3` | at the baseline `c3bdae2` |
|---|---|---|
| clean | 604 | 612 |
| refused | 270 | 230 |
| DEFECT:double_free | 48 | 56 |
| DEFECT:uaf | 22 | 22 |
| DEFECT:leg_mismatch | 3 | 25 |
| DEFECT:segv | 3 | 5 |
| DEFECT:wrong_value | 2 | 2 |
| OVERRESTRICT | 4 | 4 |
| CRASH, timeout, other | 0 | 0 |

**Baseline against HUNT, cell by cell** (npkc rc, codes, -O0, -O2): exactly
40 cells moved, and all 40 went to `refused NITPICK-TYPE-084`. They are every
cell of DEF-99's shape (a `fixed` place × `move`/`pass_out`, 40 cells): 32
were anomalies at the baseline and 8 ran clean. Nothing else moved. No cell
became an anomaly at HUNT, and no control became refused.

**The same machine, both compilers:** the whole grid re-run at the baseline on
this VM (50 s, into scratch) is identical to the committed
`results/c3bdae2/cells.jsonl` in 956 of 956 cells.

**5.2 (a) — deduplication.** `gen/dedup.py` states KNOWN_DEFECTS.md's shapes
on the grid's axes and writes `results/<commit>/DEDUP.md`. At HUNT, with
DEF-99's fix counted as present, there are **82 anomalies: 62 known and 20
candidates.**

| known defect (fix not in HUNT) | cells at HUNT |
|---|---|
| DEF-106 — a write into a part of a `fixed` binding (S14) | 24 |
| DEF-102 — a write through a lent parameter | 24 |
| DEF-105 — an imported table's row type resolved in the importer (4 are the `OVERRESTRICT` `TYPE-001` cells, case 1) | 8 |
| DEF-104 — a lent `T` passed out, or `@x` of it, in a generic body | 6 |
| **candidate** | **20** |

The 20 candidates are two shapes, the two M3 noted:
- **writes through a `for` binding**: `for_binding` × `at_free` (8 cells: 70/70
  on `ra`, 95/95 on `dx`, for `str`, `box`, `list`, `wrap`), × `at_grow` (4:
  `list`, `wrap`) and × `field_write` (4: `box`, `wrap`, 22/22 on `ra` and
  95/95 on `dx`);
- **`move(x)` of a lent `T` in a generic body**: `generic_param` × `move` (4:
  `gen_str`, `gen_box`, 70/70 on `ra`, 95/95 on `dx`).

At the baseline the same script accounts for all 114 of M3's anomalies: 32
DEF-99, 24 DEF-106, 24 DEF-102, 8 DEF-105, 6 DEF-104, and the same 20
candidates.

**5.2 (b)–(e) — the two candidate shapes, taken through the remaining steps:**
- **(b)** `gen/minimize.py` reduced eight representative cells (`c0107`,
  `c0108`, `c0275`, `c0276`, `c0459`, `c0460`, `c0887`, `c0888`) to 26–35
  lines each, in 37–61 builds per cell. Its outputs are kept in each finding's
  `minimized/`. The findings' programs are those outputs with the grid's full
  observer and fail-safe restored, plus the controls (S17).
- **(c)** `gen/run_findings.py` ran every finding program twice at HUNT. Both
  runs agree for all 23 programs (17 in F-001, 6 in F-002) on both legs.
- **(d)** Once at the baseline: every verdict is identical to HUNT's, so both
  shapes are old defects, not regressions.
- **(e)** Written:

| finding | shape | grid cells | HUNT = baseline verdicts | deduplication, in short |
|---|---|---|---|---|
| [`F-001`](findings/F-001-for-binding-write/) | a write through a `for` binding (`x.s = …`, or `@x` to a callee that frees or grows) frees the array's element | 16 | read 70/70 (22/22 at element 0), drop 95/95; 4 controls clean | DEF-102's defect at a second place: the compiler refuses a *move* of this binding with the lent parameter's own `TYPE-047` message; 3g might cover it, not measurable at HUNT |
| [`F-002`](findings/F-002-generic-move-of-loan/) | `T:y = move(x);` of a lent `T` in a generic body frees the caller's value | 4 | read 70/70, drop 95/95; the concrete twin refused `TYPE-047`, the `move T:x` twin 21/21 | DEF-104's family, an operator its fix does not name; `move` and `pass` ask one rule, which returns early when `type_drops` says no |

**5.3 — M5's counts.** Cells run at HUNT: **956** (100 in session 1, 856 here).
Anomalies at HUNT: **82** (78 `DEFECT`, 4 `OVERRESTRICT`, no `CRASH`,
timeout or other). Known: **62** (DEF-106 24, DEF-102 24, DEF-105 8, DEF-104
6). New: **20** cells in **2** findings (F-001 16, F-002 4). Both new
findings are present at the baseline as well. Neither is a regression, and
nothing regressed between the two compilers (5.1).

## M8 — the re-hunt at HUNT2 (session 3)

**The start checks.** (a) `uname -a` and `nproc` are under Environment below
(4 cores, the hosted VM). (b) `CLAUDE.md` re-read: a silent wrong answer is a
defect, exactly as a memory-safety fault is. (c) The VM was fresh, so the
toolchain was rebuilt by M0's commands (below). (d) Resumed at the first
unticked box, M8; nothing ticked was redone.

**The rebuild (M0's commands).** LLVM 20.1.2 was fetched to a file and
extracted as S13 records (download 19 s, total 345 s). The tarball's sha256
is `3a392f151375eeed…`, as in session 2, and `llvm-config --version` prints
`20.1.2`. The compiler was cloned to `.work/nitpick`, and the worktrees
`.work/base` (`c3bdae2`) and `.work/hunt2` (HUNT2) were built one after the
other by M0.5's command: HUNT2 in 75.8 s, the baseline in 75.4 s. The
baseline's products are byte-identical to sessions 1 and 2's. Its `npkc.ll`
is 28 111 929 bytes, sha256 `4029fc70efbe9cd3…`, so the commissioning check
passes again. `npkrt.o` is the same 72 576 bytes at all three compilers.
Canaries (M0.6), at both: `canary.npk` gives npkc 0 and runs 0/0;
`canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` and writes no
`.ll`. The old HUNT `6fb85d3` was not rebuilt: M8 compares with its committed
records.

**8.1 — HUNT2.** The compiler's `origin/main` was `2eea6f4` at the clone
(09:58 UTC) and `9126350` at a re-fetch at 10:01 UTC, before any build. HUNT2
is **`9126350`** (S20). It carries every fix this plan names; each was checked
with `git merge-base --is-ancestor <sha> 9126350` (rc 0) and found by its
subject in `git log --oneline origin/main | grep '1.6.0 step'`:

| subject | commit | fixes | in HUNT2 |
|---|---|---|---|
| `1.6.0 step 3g` | `5bdae98` | DEF-102, DEF-103, DEF-104 (`TYPE-085`, `TYPE-047`, `PARSE-001`) | yes |
| `1.6.0 step 3h` | `c1a4a05` | DEF-105 | yes |
| `1.6.0 step 4b` | `f87d2df` | DEF-106 (`TYPE-086`) | yes |
| `1.6.0 step 5c` | `c970483` | DEF-108 (`FLOW-001`) | yes |
| `1.6.1 step 0` | `2eea6f4` | DEF-107 (`BORROW-015`), and DEF-109 to DEF-115 found by its probes | yes |

The shas are the ones `KNOWN_DEFECTS.md` lists as planned. Every one of the
five is an ancestor of HUNT2.

**8.2 — the recall suite at HUNT2:** `results/known-9126350.txt`. Checked by
`gen/check_known_fixed.py` (the "once fixed" column transcribed) with DEF-99,
DEF-102, DEF-104 and DEF-105 counted as fixed: **19 rows judged, 19 match.**
The DEF-102 rows `lent_field`, `lent_field_nodread` and
`ctl_whole_lent_string` are refused `TYPE-085`, and `ctl_local` runs 22/22,
`ctl_move_param` 0/0. The DEF-104 rows `gen_id`, `gen_id_read` and
`ctl_concrete` are refused `TYPE-047`. DEF-105's cases 1–4, 6 and 7 run 0/0,
and case 5 is refused `RESOLVE-001`. DEF-99's cases 1–3 are refused
`TYPE-084`, and case 4 runs 0/0. The recall suite re-run at the baseline on
this VM is identical to `results/known-c3bdae2.txt` line for line.

**8.2 — F-001 and F-002 at HUNT2:** `findings/*/VERDICTS-9126350.txt`
(`gen/run_findings.py --hunt .work/hunt2 --name VERDICTS-9126350.txt`, HUNT2
twice, the baseline once; S21). The two HUNT2 runs agree for every program.

| finding | defect programs (reproducers and `minimized/`) | controls |
|---|---|---|
| F-001 | all 13 refused `NITPICK-TYPE-085` | `ctl_elem_at_free` 23/23, `ctl_elem_at_grow` 21/21, `ctl_elem_field_write` 22/22, `ctl_for_read` 21/21: as `VERDICTS.txt` |
| F-002 | all 4 refused `NITPICK-TYPE-047` | `ctl_concrete_move` refused `TYPE-047`; `ctl_gen_move_param` 21/21: as `VERDICTS.txt` |

The baseline lines are identical to the committed `VERDICTS.txt`'s (17 and 6).
So `KNOWN_DEFECTS.md`'s "closed as faces" entries hold at HUNT2: F-001 is
refused as DEF-102's `for`-binding face, and F-002 as DEF-104's `move` face.

**8.3 — DEF-108 is in HUNT2, and the generator needs no change** (S22).
Every function the generator emits already ends in `pass`, `exit` or `fail`:
the helpers, the `at_*` callees, `hold`, `op`, `run`, `main` and `failsafe`.
Measured two ways by `gen/check_leaves.py`:
- statically: 7 930 functions in the 1 032 files of `cells/`, and none that
  does not end in a leaver. The only static flag in `known/`, `findings/` and
  `commission/` is `canary_malformed.npk`, which is malformed on purpose;
- by HUNT2's own rule: all 1 000 root programs (the 956 cells, `known/`,
  `findings/`, `commission/`) compiled at HUNT2 (577 npkc 0, 423 npkc 1), and
  **0 carry `NITPICK-FLOW-001`**.

The control for both checks is a planted fall-off: `c0092`'s `at_fr` with its
one `pass NIL;` removed (the substitution asserted to match once). HUNT2
refuses it with `FLOW-001` (npkc 1), the baseline accepts it (npkc 0), and the
static check flags it. The grid regenerated by the unchanged `gen/grid.py`
(last changed in M2, `de1130e`) is the same 956 cells, 1 284 skipped. **The
whole grid re-run at the baseline on this VM (63 s) is identical to the
committed `results/c3bdae2/cells.jsonl` in 956 of 956 cells** (npkc rc, codes,
-O0, -O2). No verdict changed, since nothing in the generator changed.
Committed as `ba0072e` before any hunting.

**8.4 — the grid at HUNT2.** All 956 cells ran in 60.5 s (4 jobs):
`results/9126350/` (`cells.jsonl`, `SUMMARY.md`, `classified.jsonl`).
**562 clean, 394 refused, 0 anomalies**: no `DEFECT`, `CRASH`,
`OVERRESTRICT`, timeout or `other`. **Every cell's outcome is its
expectation**: all 394 REFUSE cells are refused, and all 562 SAFE cells run
0/0. Refusal codes, each counted once: `TYPE-046` 108, `TYPE-085` 92,
`TYPE-047` 48, `TYPE-084` 40, `TYPE-071` 40, `TYPE-086` 28, `MOVE-001` 26,
`TYPE-007` 12, `ASSIGN-002` 8, `TYPE-027` 2. In 42 refusals the codes differ
from the expected ones:
- 28 are `TYPE-086` where `grid.py` (written before 4b) expected `ASSIGN-002`;
- 12 carry `TYPE-007` (below);
- 2 are the `TYPE-027` + `TYPE-071` seen since M3.

**8.5 — HUNT2 against `6fb85d3`, cell by cell** (`gen/compare.py`,
`results/9126350/MOVES.md`). **148 cells moved: 136 are 8.5's expected moves,
none missing, and 12 changed refusal code.**

| rule (8.5) | moved | to |
|---|---|---|
| DEF-102 | 48 (24 anomalies, 24 clean) | `TYPE-085` |
| F-001 | 32 (16 anomalies, 16 clean) | `TYPE-085` |
| DEF-104 | 16 (6 anomalies, 10 clean) | `TYPE-047` (4), `TYPE-085` (12) |
| F-002 | 4 anomalies | `TYPE-047` |
| DEF-105 | 8 (4 `OVERRESTRICT`, 4 segv/leg) | clean |
| DEF-106 | 28 (24 anomalies, 4 refused `TYPE-001`/`TYPE-027`) | `TYPE-086` |
| not a rule: 3h's type identity | 12 (refused `TYPE-046` 4, `TYPE-084` 8) | `TYPE-007` (4), `TYPE-007`+`TYPE-084` (8) |

REPORT.md §6's 50 "expected refused, ran clean" cells are all refused (48
`TYPE-085`, 2 `TYPE-047`). No cell became an anomaly, and no SAFE cell is
refused. Among cells compiled at both compilers, the only exits that changed
are `c0379`–`c0382` (DEF-105's wider row, now 0/0).

**The 12 changed refusals were investigated.** These are `imported_fixed_same`
and `imported_fixed_wider` × `copy`/`move`/`pass_out`, with the message
*"expected `Box`, found `Box`"*.
- **Bisected** (S23): 3g `5bdae98` and 3h `c1a4a05` were built (75.8 s and
  75.6 s), and all 76 import cells run at each (`results/5bdae98/` and
  `results/c1a4a05/cells-imported.jsonl`, `results/9126350/BISECT-3h.md`).
  `6fb85d3` equals 3g in 76/76. `TYPE-007` appears at 3h exactly, and 3h
  equals HUNT2 in the 12.
- **The control:** at `imported_fixed_typed` (the table's `Box` imported by
  name), the same operations stay `TYPE-046`/`TYPE-084` at all four
  compilers.
- *Read, not measured:* 3h types `TBL[i]` as `tbl`'s `Box`, and the cell's
  `Box:y` names the importer's own struct. So these are the fix at work on
  the grid's own spelling, not a regression.
- It leaves a generator gap: the 4 copy cells no longer reach `TYPE-046`
  (REPORT.md §7). The message naming both types `Box` is a wording
  observation.

**8.6 — no anomaly at HUNT2**, so nothing to take through M5's five steps; no
new finding. Recorded on the way:
- `c0371`/`c0372` are refused `TYPE-086` at HUNT2, which `KNOWN_DEFECTS.md`
  had only inferred.
- At 3h, between DEF-105's and DEF-106's fixes, `c0341`/`c0342` (the
  table-only import's `field_write`) compile and run 95/95: DEF-106 reached
  through an import.

**8.7 — `REPORT.md` §9** holds HUNT2, the recall and findings results, the
DEF-108 check, the counts by class at all three compilers, the move table, the
bisection and the cost. A one-bullet pointer is in its opening paragraph, and
the new generator gap is in §7.

**The estimate for M9, for the author** (reasoned from this session's and
M2's measured costs, not measured):
- **Compute is small.**
  - The present grid runs in about 60 s per compiler (16 cells/s at 4 jobs).
  - A widened grid of 3 000–5 000 cells runs in 3–6 min per compiler, so
    10–15 min at the baseline and HUNT2 together, with reruns.
  - The toolchain rebuild on a fresh VM costs about 8.5 min (LLVM 345 s, two
    builds 76 s each).
- **The work is authoring and triage.** Each new type, place and operation has
  its syntax learned by probing snippets at both compilers, and its
  expectation written before its first run (9.6). M9.1 (the leak observer)
  needs the runtime's `NPK_HEAP_STATS` source at the baseline, plus
  `nitpick-time`'s `meta/roadmap/0.1/0.1.4b.md`, a read-only clone of a
  second repository that this session has not tried.
- **Anomalies are likely.**
  - At the baseline, the new axes should re-find DEF-102, DEF-104 and DEF-106
    through new paths; that is the recall gate 9.6 keeps.
  - At HUNT2, the likeliest new ones are: `List<string>` growth moving owning
    elements, partial and conditional moves, moves in loops, and `?`/failsafe
    exits with live owners.
  - Each finding costs a minimisation, two confirmations, a baseline run and
    a write-up. By its commit times, session 2 committed M5's two findings
    10 min after the grid run (`4266b24` at 03:49 UTC, `dc76306` at 03:59).
- **Overall:** one session. M8 took 09:57–10:21 UTC by the clock (24 min, of
  which about 9 were the rebuild). M9 is likely 3–8 times that, **roughly
  1.5–3 hours**, and its compute stays under 30 min. The generator's new axes
  set the low end, and the number of new anomalies to triage sets the high
  end.

## M9 — widen the ownership grid (session 4)

**The start checks.** (a) `uname -a` and `nproc` are under Environment below
(4 cores, the hosted VM). (b) `CLAUDE.md` re-read, the silent-wrong-answer rule
with it: a result that differs from the reference counts as a defect, exactly
as a memory fault does. (c) The VM was fresh (`.work/` absent), so the toolchain
was rebuilt by M0's commands (below). (d) This branch began at `7370a9d`, before
M8; M8 (`ea77960`) was fast-forwarded in first (S24), so M9 resumes at the first
unticked box and nothing ticked was redone.

**The rebuild (M0's commands).** LLVM 20.1.2 was fetched to a file and
extracted as S13 records: the download took 10 s, the whole step 281 s. The
tarball is 2 021 628 328 bytes, sha256 `3a392f151375eeed…` (as in sessions 2
and 3), and `llvm-config --version` prints `20.1.2`. The compiler was cloned to
`.work/nitpick`. Its `origin/main` was `9126350` at 10:28 UTC, so HUNT2 is
unchanged (S25). The worktrees `.work/hunt2` (`9126350`) and `.work/base`
(`c3bdae2`) were built one after the other by M0.5's command: HUNT2 in 52.5 s,
the baseline in 54.4 s. **All six products are byte-identical to session 3's**:
- `npkc.ll`: 28 857 206 / `2448b3b60d9eb189…` (HUNT2), and 28 111 929 /
  `4029fc70efbe9cd3…` (the baseline). The commissioning check passes again.
- `npkc`: 9 972 944 / `20d35e2822b99080…` and 9 724 232 / `0cbc150ced5d20f7…`.
- `npkrt.o`: 72 576 / `162b897539285a77…` for both.

Canaries (M0.6), at both compilers: `canary.npk` gives npkc 0 and runs 0/0, and
`canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` and writes no
`.ll`. **The M2 grid re-run on this VM is identical to the committed records**:
956 of 956 cells at HUNT2 (41 s), and 956 of 956 at the baseline (44 s). Both
were compared on npkc rc, codes, -O0 and -O2.

**9.1 — what the `heap:` line means, read from the source and measured.**
- *Read* at the baseline, in `runtime/npkrt.ll`:
  - `npk_hs_note_alloc` adds each request's REQUESTED size (not the rounded
    class) to `allocated` and to live, raises `peak_live` to live when live
    exceeds it, and adds 1 to `count`.
  - `npk_hs_note_free` subtracts from live, and `npk_hs_note_resize` moves
    live by the difference.
  - `npk_exit`'s `leave` block prints `heap: allocated=<n> peak_live=<n>
    count=<n>` once per process, on every exit, a trapped one included.
  - **Live bytes at exit are not printed.**
- *Read* in `nitpick-time`'s `meta/roadmap/0.1/0.1.4b.md`, at commit
  `1cfd3f001c915bc19901b2cccd148b4cd2034638` (a read-only clone in `.work/`).
  It measures the same line, and states the consequence: `peak_live` is a
  high-water mark, so a program that leaks once, as it exits, reports what one
  that frees there reports (its §1.2). It also records that failsafe's region
  allocations are not counted, and that a moving `ralloc` counts as an
  allocation and then a free.
- **The observer, therefore:** after `run` returns (every drop done), `main`
  allocates a probe of B = 1 048 576 bytes (`buffer_new`) and exits. The probe
  lifts the peak to (live after `run`) + B whenever B exceeds every earlier live
  total. That holds if allocated − B < B, since no peak can exceed the bytes
  ever requested, and the line itself shows it. So **live after `run` =
  peak_live − B**. *Measured*, at both compilers, both legs identical:

| control | line (allocated / peak_live / count) | live after `run` |
|---|---|---|
| `l0_nothing` (allocates nothing) | 0 / 0 / 0 | — |
| `l3_probe_only` (the probe alone) | 1 048 576 / 1 048 576 / 1 | B = 1 048 576 |
| `l1_freeall` (`run` makes one `mk()` string and returns) | B+46 / B / 2 | **0** |
| `l2_keepone` (`main` also keeps one `mk()` string: `exit` runs no drop) | B+92 / B+46 / 3 | **46**, the kept string |

  A peak read without the probe gives 46 for both `l1` and `l2`, so `l2` is the
  control a wrong observer gets wrong. `mk()` requests 46 bytes, `nw()` 43, and
  the sentinel `sn()` 46.

**Found while learning the syntax** (probes in scratch; each noted, none worked
around; to be taken through M5's steps in triage):
- **`to_cstring`'s buffer is never freed.** *Measured* at both compilers, both
  legs, identical:
  - A function that converts `"/dev/null"` and returns, called N times, peaks
    at exactly 10 × N live bytes: `allocated=10000 peak_live=10000 count=1000`
    at N = 1 000, and 40 000 at N = 4 000. The program exits 0.
  - The control is the same loop with an owning `string` of the same length.
    It peaks at 9 (the substitution was asserted to match once).
  - *Read:* `npk_to_cstring` allocates through `npk_alloc_internal`, the
    managed internal entry that D-151's exit check does not count. `cstring` is
    `{ptr, len}`, with no `cap` and no drop.
  - TYPE_REFERENCE §3.2.1 types the buffer as `wild char8->`, and CONTROL §4.6
    says a successful `exit` with live `wild` memory traps instead. One of the
    two is wrong. A candidate finding.
- **The `Result` fallback is spelled `?|`.** A bare `expr ? default` is refused
  `NITPICK-PARSE-011` ("a bare `?` is not the `Result` fallback (D-175)"). Yet
  TYPE_REFERENCE §11.2's unwrap table still lists `expr ? defaultVal`, as does
  MEMORY_REFERENCE §4.2's `my_arena.get(h) ? 0i64`. A documentation mismatch,
  for M11.
- **No string literal types as `cstring`.** `cstring:dn = "/dev/null";` and a
  literal handed to `open` are both refused, `TYPE-007` ("expected `cstring`,
  found `string`"). TYPE_REFERENCE §3.2.1 lists "string literal in `cstring`
  position" as a zero-cost source. Another documentation mismatch, for M11.
- Also measured, and each is the language's stated rule rather than a finding:
  - a read of a binding after a partial move is `MOVE-001` (D-065's
    whole-binding rule);
  - `for` over a `List` is `TYPE-033` (it iterates a range, a slice, an array
    or an `Iterator`);
  - `for` over a slice view bound in the same function (`a[0...2]`,
    `l[0...n]`) is `BORROW-009`;
  - `for` over a `string[]` PARAMETER compiles;
  - `gid` is a reserved kernel-identifier type (`PARSE-001` at HUNT2).

**The shakedown (before any result counted), and the generator's fixes.**
- **First shakedown.** The whole grid (then 7 826 cells) ran at the baseline
  into scratch. Two generator bugs showed, and nothing else of the
  generator's own:
  - `use` is a keyword, so every `self_lent` and `dyn_recv` cell stopped at
    `PARSE-002`;
  - `dyn T[2]` and `dyn T->` parse as `dyn (T[2])` and `dyn (T->)`
    (`TYPE-006`).

  The helper was renamed, and a `dyn` is no longer crossed with the array and
  pointer places or the `at_*` operations (`c034731`, `M9 (2)`).
- **Second shakedown.** The first full run at both compilers showed two more
  gaps. They were fixed and that run was superseded; its records are kept in
  scratch (`9949f75`, `M9 (3)`):
  - the generic body had no `at_grow`, so 16 cells performed no operation;
  - the descriptor observer's number test cannot follow a loop's reuse.
- **An observer bug found in triage.** A vacant `OwnedFd`'s `value => int64`
  reads 4 294 967 295 (the i32 −1, zero-extended; D-042 makes `fd` an `i32`),
  and `obs_fd` compared the value with `-1i64` only. So the observer called a
  vacant descriptor "closed" (70). `obs_fd` now takes either spelling of −1.
  Only helper text changed, so the ids are stable, and the 403 `OwnedFd`
  cells were re-run at both compilers and their records replaced.
- **No expectation was changed** by any of these fixes (S29).

**The widened grid** (`gen/grid9.py`; the denominators are in
`results/GRID9.md`): **7 571 cells** and **28 519 skipped** combinations, each
with its reason; 36 090 in all. REFUSE 3 210, SAFE 4 361.

| section | what | cells | skipped |
|---|---|---|---|
| A | the M2 grid's 478 combinations × the new observers (leak, reuse sentinel; read-now at the loop place) | 986 | 448 |
| B | the new types (`List<string>`, a nested struct, `string[3]`, `Box[3]`, generic `T` at `List<string>` and `string[2]`, `buffer`, `OwnedFd`, `dyn`) × the M2 places and operations | 1 700 | 4 600 |
| C | the new places (`for` over a range of an array or a `List`, over a slice parameter from an array or a `List`, a lending and a consuming `pick`, a `Self->` receiver on an owned and on a lent holder, a lent `dyn`'s method, `$$m`, `$$i`, a temporary, the `Result` paths `?|`-success, `?|`-failure and `relay`) × the M2 operations and the partial move and swap | 2 076 | 13 224 |
| D | the new value operations (a partial move, a swap, a conditional move taken and not taken, a move in a loop with and without re-initialisation) × every place | 2 396 | 9 844 |
| E | the control-flow exits with live owners (`break`, `continue`, an early `pass`, an early `pass` of an owner, `relay`, `relay` past a temporary, a trap, a trap past a temporary) × holders × types | 413 | 403 |

**9.7 — the runs** (4 jobs; `results/<commit>/cells9.jsonl`, `SUMMARY9.md`,
`classified9.jsonl`, `DEDUP9.md`): the baseline in 340 s and HUNT2 in 325 s,
plus the 403 `OwnedFd` cells again at each.

| class | baseline `c3bdae2` | HUNT2 `9126350` |
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
| `CRASH`, timeout, other | 0 | 0 |
| **total** | **7 571** | **7 571** |

**9.6 — the recall gate holds** (`gen/recall9.py`, at the baseline): every
known shape is flagged in the widened grid, by the new observers as well.

| known | cells of the shape | flagged `DEFECT` | ra / dx / lk / rs / rn |
|---|---|---|---|
| DEF-99 | 348 | 224 | 45 / 51 / 71 / 57 / 0 |
| DEF-106 | 116 | 64 | 10 / 10 / 22 / 22 / 0 |
| DEF-102 (with the pointer-receiver call on a loan) | 305 | 175 | 32 / 29 / 70 / 44 / 0 |
| F-001 (with a `for` over a slice parameter) | 235 | 133 | 17 / 15 / 51 / 25 / 25 |
| DEF-104 | 36 | 22 | 2 / 4 / 12 / 4 / 0 |
| F-002 | 12 | 12 | 2 / 2 / 4 / 4 / 0 |
| DEF-105 | 14 | 4 (+ its 4 `OVERRESTRICT` controls, case 1) | 0 / 0 / 2 / 2 / 0 |

**Deduplication** (`gen/dedup9.py`):
- At the baseline, 840 anomalies: 618 are known shapes, and 222 are
  candidates.
- At HUNT2, which carries every fix, **197 anomalies, all candidates**. They
  fall into four families, with nothing left over (triage below):

| family (HUNT2) | cells | verdicts |
|---|---|---|
| a store through a pointer, `(<-p) = v`, does not drop the old value | 117 | `DEFECT:leak`: the original's bytes, or a descriptor left open |
| a consuming `pick`'s binding is not dropped at the arm's end | 28 | `DEFECT:leak` |
| the two at once (`pick_own` × `at_overwrite`) | 4 | `DEFECT:leak` |
| a consuming `pick`'s binding escapes the move rules | 32 | `DEFECT:uaf`, `double_free`, `segv`, `wrong_value` |
| a write through a `$$i` claim (the expectation REFUSE, `BORROW-013`) | 16 | `DEFECT:wrong_value`: the write happened |

**9.7 — triage by M5's five steps.**
- **(a) Deduplicated.** Nothing at HUNT2 is a known shape.
- **(b) Minimised.** Where a family came from a grid cell, the minimiser ran on
  a representative cell at HUNT2, with `--live` for a leak: 28–36 lines, 62–81
  builds each, in each finding's `minimized/`. Probe-found shapes were written
  small by hand.
- **(c) Confirmed** twice at HUNT2, both legs; the runs agree for every
  program.
- **(d) Run at the baseline.**
- **(e) Written:**

| finding | shape | class | cells | HUNT2 `9126350` | baseline |
|---|---|---|---|---|---|
| F-003 | a consuming `pick`'s binding escapes the move rules | use-after-free, double free | 44 | 0/95/95, 0/70/70; a local: `MOVE-001` | the same |
| F-004 | a view's root freed by a callee that moves out through `@x` or `$$i x` | use-after-free | probe | 0/70/70; `$$m x`, an overwriting callee and a direct move: `BORROW-015` | the same (there, DEF-107 itself) |
| F-005 | a store through a pointer, `(<-p) = v`, never frees the old value | leak | 121 | live 46; churn 46 × N + 43; an `OwnedFd` left open (26) | the same |
| F-006 | a consuming `pick`'s named binding is never dropped at the arm's end | leak | 32 | live 46 with an empty arm; `_`, the lending form and a moved-out binding: 0 | the same |
| F-007 | `to_cstring`'s buffer is never freed | leak | probe | peak 10 × N; an owning `string`: 9 | the same |
| F-008 | a write through a `$$i` claim's holder compiles, which the reference's table names `BORROW-013` | a rule not enforced | 40 | 0/22/22; the root's write under `$$i`: `BORROW-013` | the same |
| F-009 | a `move` parameter re-initialised after a move cannot be read | over-restriction (lower priority) | 72 | `MOVE-001`; a local: 22 | the same |
| F-010 | a swap through a lent `dyn`'s method is refused `BORROW-002` | over-restriction (lower priority) | 12 | `BORROW-002` | 0/22/22: **new at HUNT2** |

**The expectations the compiler did not meet, at HUNT2.**
- 84 REFUSE cells were accepted: F-003's 44 and F-008's 40.
- 374 SAFE cells were refused:
  - 262 are `MOVE-001` by D-065's whole-binding rule (a swap or a move through
    a field, an element or a range: the generator's reading, not the
    compiler's);
  - 72 are F-009;
  - 28 are `TYPE-047` on `pass self.v` through a receiver (a refusal);
  - 12 are F-010.

Details in REPORT.md §10.7.

**What the new observers added, on section A's same 478 M2 programs.**
- The leak observer: 42 HUNT2 cells, and 66 at the baseline, that the M2
  drop-at-exit twin called clean.
- The read-now observer: 2 baseline cells, which turn a reused-block 22 into
  the poison.
- The sentinel read its own bytes through the original in 54 baseline cells
  (reuse proven), against 2 that still read the poison.

**Observations for M10 and M11**, measured and not findings here:
- `?` is `?|` since D-175, but TYPE_REFERENCE §11.2 and MEMORY_REFERENCE §4.2
  still spell `?`.
- No string literal types as `cstring`, against TYPE_REFERENCE §3.2.1.
- `fd => int64` zero-extends a vacant `OwnedFd`'s −1 to 4 294 967 295.

**The estimate for M10, for the author** (reasoned from this session's
measured costs, not measured):
- **Compute is small.**
  - The rebuild on a fresh VM costs about 7 min (LLVM 281 s, two builds of
    about 55 s).
  - M10's programs are small, one per checklist item or claim: a few hundred
    at most. They build and run at about 10 per second per compiler at 4 jobs,
    so under 5 min for both compilers.
- **The work is reading and writing.** Each checklist item needs its reference
  sentence found, and its expected exit code written from the TEXT before the
  run. The sources:
  - TYPE_REFERENCE (2 122 lines) for defaults, conversions and overflow;
  - CONTROL_REFERENCE for `pick`, `when`, `defer` and loop ranges;
  - BUILTIN_REFERENCE for string lengths;
  - OP_REFERENCE for operators.

  M9 already found three sentences the compiler contradicts (above). So
  documentation findings are likely, and each costs a reading of the rule
  against the compiler's behaviour.
- **Overall:** one session. M9 ran from 10:27 UTC to its final commit, about 11:50 UTC, under 1.5 h,
  of which compute was about 25 min. M10 is likely 1–2.5 h. The size of the
  checklist sets the low end, and the number of disagreements to confirm and
  write up sets the high end.

## M10 — silent wrong answers (session 5)

**The start checks.**
- **(a)** `uname -a` and `nproc` are under Environment below (4 cores, the hosted VM).
- **(b)** `CLAUDE.md` was re-read, the silent-wrong-answer rule with it. A result that
  differs from the reference, with no memory error, counts exactly as a memory fault
  does, and is never filed as an observation outside the definition.
- **(c)** The VM was fresh (`.work/` absent), so the toolchain was rebuilt by M0's
  commands (below).
- **(d)** The branch began at `88e6355`, which is `origin/main` (M9 merged): the
  fast-forward was a no-op. M9 is ticked and M10 is not, so M10 resumes at its first
  box. Nothing ticked was redone.

**The rebuild (M0's commands).** LLVM 20.1.2 was fetched to a file and extracted as
S13 records. The download took 15 s and the whole step 383 s. The tarball is
2 021 628 328 bytes, sha256 `3a392f151375eeed…`, as in sessions 2–4, and
`llvm-config --version` prints `20.1.2`.

The compiler was cloned to `.work/nitpick` at 11:57 UTC. Its `origin/main` was
`b564746` (1.6.1 step 0c, DEF-116), and `9f6f370` at a re-fetch at 12:29 UTC (a
record commit over it). HUNT2 stays `9126350` (S32). The worktrees `.work/hunt2`
(`9126350`) and `.work/base` (`c3bdae2`) were built one after the other by M0.5's
command: HUNT2 in 90.8 s, the baseline in 91.7 s.

**All six products are byte-identical to sessions 3 and 4's**:
- `npkc.ll`: 28 857 206 / `2448b3b60d9eb189…` (HUNT2) and 28 111 929 /
  `4029fc70efbe9cd3…` (the baseline), so the commissioning check passes again;
- `npkc`: 9 972 944 / `20d35e2822b99080…` and 9 724 232 / `0cbc150ced5d20f7…`;
- `npkrt.o`: 72 576 / `162b897539285a77…` for both.

Canaries (M0.6), at both compilers: `canary.npk` gives npkc 0 and runs 0/0, and
`canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001`.

**The machine checks.**
- The M2 grid re-run on this VM is identical to the committed records in 956 of 956
  cells at HUNT2 (73 s) and 956 of 956 at the baseline (78 s).
- The recall suite (`gen/run_known.py`) now holds 25 programs. Its 19 old rows are
  identical to `results/known-9126350.txt` and `results/known-c3bdae2.txt` line for
  line.
- The 6 rows added at M9's merge (`known/def106_fixed_part/`,
  `known/def108_fall_off/`) give exactly `KNOWN_DEFECTS.md`'s verdicts:
  - at the baseline, DEF-106's cases 0/95/95 and 0/107/11, DEF-108's 0/10/10 and
    0/12/12, both controls 0/0/0;
  - at HUNT2, the four cases refused (`TYPE-086`, `FLOW-001`) and both controls
    0/0/0.
- Recorded as `results/<commit>/known-m10.txt` (S35).

**10.1 — the checklist** (`gen/m10.py` writes `m10/CHECKLIST.md`, `m10/EXPECT.tsv` and
`m10/programs/`).
- **Sources read for it, at HUNT2:**
  - OP_REFERENCE whole;
  - CONTROL_REFERENCE whole;
  - TYPE_REFERENCE §1–4, §6, §9–11, §26–28;
  - BUILTIN_REFERENCE whole;
  - LEXICAL_REFERENCE §5–6;
  - the decisions they cite (D-010, D-022, D-060, D-092, D-095, D-136, D-139, D-148,
    D-225, D-234, D-306) and VERIFICATION_REFERENCE §1.2's `pick` model.
- **229 items in 17 areas.** 223 are testable and 6 untestable, each with its reason.
  The plan's eleven features are all there: defaults, conversions and literals,
  overflow, division, comparisons, strings, `pick`, `when`/`defer`, `Result`, loops and
  shadowing. They are joined by shifts, precedence and evaluation order, arrays and
  slices, floats, `exit`, and DEF-108's recall (10.3).
- **Each citation is a quoted phrase.** `gen/m10.py` locates it by its text, uniquely,
  at HUNT2 and at the baseline. All 320 resolve at HUNT2. The ones absent at the
  baseline are exactly the sentences that changed since: FLOW-001's paragraph, the
  tag-only enum's `=>!`, and the block-string closing sentence.
- **Every item says what a wrong implementation would answer**, so each program is a
  case the wrong implementation gets wrong.
- **The expectations are committed before the first run** (S36).

**10.2 — the runs** (`gen/m10_run.py`; `results/<commit>/m10.jsonl`, with run 1 as
`m10-run1.jsonl`). 223 programs per compiler, both legs, 4 jobs, 25–26 s each.
- **Run 1:** HUNT2 210 agree and 13 disagree; the baseline 208 and 15.
- **Two programs were re-spelled** (S36):
  - `m12`: `>` on tbb is refused, since ordering on tbb is a compile error
    (D-093), so it compares with `==`;
  - `d16`: a direct field write into a struct declared without a value is
    refused (D-010), so it uses D-225's `$$m` idiom.
- **Run 2:** HUNT2 **212 agree, 11 disagree**; the baseline **210 and 13**. The
  other 221 programs' records are identical between the runs at both compilers,
  so every verdict was measured twice.
- **The baseline's two extra disagreements are known:**
  - DEF-101 (`c18`): its reference called `intN =>! enum` impossible, and its
    compiler accepts it;
  - DEF-98 (`t04`).
- `m10/RESULTS.md` (by `gen/m10_report.py`) classifies every disagreement,
  leaving none unclassified.

**10.3 — the DEF-108 recall holds.**
- The four shapes the plan names, and `string`, `bool`, `NIL` and a trailing
  `for`, are flagged at the baseline: they compile and answer a zero value
  (10, 12, or a silent exit 0).
- At HUNT2 they are refused `FLOW-001` (`q01`–`q07`, `q11`).
- The rule's three stated exceptions are not over-refused at either compiler
  (`q08`–`q10`).
- `known/def108_fall_off/` agrees.

**The triage** (M5's five steps; `findings/F-011` … `F-017`). Every finding was:
- deduplicated against `KNOWN_DEFECTS.md` (none is a known shape);
- written small, with controls that give the reference's answer;
- confirmed twice at HUNT2 on both legs (`gen/run_findings.py`: the runs agree);
- run at the baseline;
- run twice at the compiler's newest `main` `9f6f370` (S37).

**All seven are present at all three compilers with the same verdicts: old
defects, not regressions.**

| finding | shape | class | the measurement (HUNT2 = baseline = `9f6f370`) |
|---|---|---|---|
| F-011 | a `for` binding outlives its loop in the emitter; a later use of an outer binding of the same name reads the loop's slot | **silent wrong value; an out-of-bounds read**; invalid IR | same type: `i` reads 3, not 100 (0/10/10); an outer `int32[4]`: `v[3]` reads past the loop's 4-byte slot, 0/**11**/**10** (the legs differ); an outer `string`: npkc 0, `llc`/`opt` reject |
| F-012 | a `for` range runs zero times: a signed inclusive range ending at the maximum; an unsigned range across 2^(W-1) | **silent wrong answer** | 7 programs, each 0 trips (0/10/10) |
| F-013 | `loop`/`till` sign-extend an unsigned bound | **silent wrong answer**; a spurious trap | `loop(100u8, 200u8, 1u8)`: 156 trips down to -55; `till(200u8, 1u8)`: 56 trips down; a uint32 `loop`: 93 |
| F-014 | `till` with a negative limit counts down | **silent wrong answer** | `till(-3, 1)`: 3 trips, 0 … -2, where the reference says zero |
| F-015 | `<=>` refused by the emitter | `EMIT-002` (lower priority) | even `1i32 <=> 2i32` |
| F-016 | a negative range pattern refused by the emitter (a gap in DEF-35's fix) | `EMIT-002` (lower priority) | `(-5..-2)`, `(-5..2)`, `(-5...-2)` |
| F-017 | seven reference sentences the compiler contradicts | documentation | `s.length`, `s[i]`, §28's `fcmp one` and `select`, §4's wrapping, `TYPE-033`, a local constant `/ 0` |

- **How they were found.** The checklist found F-011 (`h02`), F-012 (`l06`,
  `l08`), F-014 (`l11`), F-015, F-016 and F-017. The emitted IR and probes then
  mapped each shape. F-013 and F-012's unsigned face came from those probes.
- **What was read, not measured:** the mechanisms, read from HUNT2's
  `src/backend/ir/ir_stmt.npk`. They are in each README, apart from what was
  measured.

**10.4 — `REPORT.md` §11** holds the checklist's denominators (229 items, 223
testable, 212 agreeing and 11 disagreeing at HUNT2, 210 and 13 at the baseline,
6 untestable with reasons), the recall, the findings, what the checklist does
not cover, and the cost.

**The estimate for M11, for the author** (reasoned from this session's measured
costs, not measured):
- **Compute is small.** The rebuild on a fresh VM costs about 9 min. A program
  builds and runs at about 9 per second per compiler at 4 jobs, so even 1 000
  claims' programs run in under 5 min per compiler.
- **The work is reading.** M11 extracts every normative claim and code example
  from every `*_REFERENCE.md` at HUNT2: about 10 400 lines in 14 files.
  - M10 read about a third of that closely and turned it into 229 items. It
    covered most of OP, CONTROL, BUILTIN and LEXICAL, and a third of TYPE.
  - M11's remainder is TYPE §5–8 and §12–25, MEMORY, MODULE, TRAITS, IO, MACRO,
    CONCURRENCY, BUILD, AST and VERIFICATION. That is plausibly 600–1 200 more
    claims.
  - Many will be untestable here: VERIFICATION's solver rows need `npkg verify`
    and z3; BUILD's `npkg` claims need the package tool; CONCURRENCY's need
    threads under a schedule. Each is still to be listed with its reason.
- **Findings are likely.** M10 found a documentation mismatch in roughly one
  claim in 30, and M9 found three sentences for M11 already (`?`, `cstring`
  literals, `fd`'s sign).
- **Overall:** this session ran from 11:57 UTC to M10's last commit at 12:53: 56
  minutes. About 19 of them were compute: LLVM 6.4 min, three compiler builds
  4.5, the grid check 2.5, the checklist's four runs 1.7, the findings' runs
  about 2, and probes. M10 read about a third of the references into 229 items.
  M11 reads the rest into perhaps 600–1 200 more, so it is likely **2–4
  hours**: one long session, or two. Split it by reference: TYPE, MEMORY,
  MODULE and TRAITS first, reusing `gen/m10.py`'s citation-by-text; then IO,
  MACRO, BUILD, CONCURRENCY, AST and VERIFICATION, with most solver and
  toolchain claims listed untestable.

## M11 — the reference, checked against the compiler (session 6)

**The start checks.**
- **The gate.** `git fetch origin && git merge --ff-only origin/main` was a no-op: the
  branch began at `626c22d`, the workbench's commit after M10's merge, which is
  `origin/main`. M10 is ticked and M11 is not.
- **(a)** `uname -a` and `nproc` are under Environment below (4 cores, the hosted VM).
- **(b)** `CLAUDE.md` was re-read, the silent-wrong-answer rule with it: a result that
  differs from the reference, with no memory error, is a defect, exactly as a memory
  fault is, and is never filed as an observation outside the definition.
- **(c)** The VM was fresh (`.work/` absent), so the toolchain was rebuilt by M0's
  commands (below).
- **(d)** M11 resumes at its first box; nothing ticked was redone.

**The rebuild (M0's commands).** LLVM 20.1.2 was fetched to a file and extracted as
S13 records: the download took 13 s and the whole step 307 s. The tarball is
2 021 628 328 bytes, sha256 `3a392f151375eeed…` (as in sessions 2–5), and
`llvm-config --version` prints `20.1.2`. The compiler was cloned to `.work/nitpick`
at 13:03 UTC. Its `origin/main` was `9f6f370`, the record commit session 5 last saw,
so HUNT2 stays `9126350` (S41). The worktrees were built one after the other by
M0.5's command: `.work/hunt2` (`9126350`) in 55.9 s, `.work/base` (`c3bdae2`) in
57.0 s, and `.work/main9f6` (`9f6f370`, S37's third compiler, for the findings) in
53.1 s.

**All nine products are byte-identical to sessions 3–5's**:
- `npkc.ll`: 28 857 206 / `2448b3b60d9eb189…` (HUNT2), 28 111 929 / `4029fc70efbe9cd3…`
  (the baseline, so the commissioning check passes again), 28 872 365 /
  `7bab110a1e45cc9d…` (`9f6f370`);
- `npkc`: 9 972 944 / `20d35e2822b99080…`, 9 724 232 / `0cbc150ced5d20f7…` and
  9 977 464 / `339926efccec34f0…`;
- `npkrt.o`: 72 576 / `162b897539285a77…` at all three.

Canaries (M0.6), at all three compilers: `canary.npk` gives npkc 0 and runs 0/0, and
`canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` and writes no `.ll`.

**The machine checks.**
- The recall suite (`gen/run_known.py`) is identical to `results/<commit>/known-m10.txt`
  line for line at both compilers: 25 rows each (9 s for both).
- M10's 223 programs re-run at HUNT2 are identical to `results/9126350/m10.jsonl` in
  223 of 223 (npkc rc, codes, both legs, verdict; 16 s): 212 agree, 11 disagree, as
  recorded.

### M11 — the state at the stop (read this first to resume)

*The last clean point is session 9's AST (S60), after its MODULE and LEXICAL: extracted,
run, triaged, committed, pushed. Session 8 did MEMORY, OP and CONTROL the same way (S57). M11 stays unticked.*

**Done, committed and measured.**
- Extracted: BUILTIN, CONCURRENCY, IO, MACRO, MEMORY, OP, CONTROL, MODULE, LEXICAL and
  AST whole, TYPE 1–660 and VERIFICATION 1–1247. That is 6 405 of the references'
  10 419 lines (S58 corrected the count).
- **2 463 claims, 2 159 testable, 304 untestable** with reasons (`m11/CLAIMS.md`).
- The final run at HUNT2 (`results/9126350/m11.jsonl`): **1 931 agree, 228 disagree**.
- Every disagreement is triaged (`gen/m11_triage.py`) and run at the baseline and at
  its session's newest `main`: `1b4f0c6` for session 7's, `93bcb66` for sessions 8's
  and 9's.

Written up in `m11/RESULTS.md`, `REPORT.md` §12 and findings F-018 … F-040:
- MEMORY's are F-029 (a reserved word accepted as a binding's name) and F-030 (eight
  documentation rows);
- OP's is F-031 (five documentation rows);
- CONTROL's is F-032 (six documentation rows);
- MODULE's are F-033 (seven documentation rows) and F-034 (three lower-priority compiler
  rows);
- LEXICAL's are F-035 (six documentation rows) and F-036 (two lower-priority compiler
  rows);
- AST's are:
  - F-037: **a use after free**, a trait object built by `x => dyn Trait`;
  - F-038: npkc traps on `give`/`fall` outside a pick;
  - F-039: four lower-priority compiler rows;
  - F-040: twenty documentation rows.

**Not started:** TYPE 661–2122, VERIFICATION 1248–2351, TRAITS and BUILD. About 4 010
lines, roughly 2 000 claims. Session 9's brief (S60) takes them smallest first: BUILD,
TRAITS, VERIFICATION 1248–2351, TYPE 661–2122.

**To resume (a later session):**
1. The start checks; M0's rebuild only where `.work/` is stale. HUNT2 stays `9126350`;
   the newest `main` for findings is `93bcb66`, unless the workbench names a newer one.
2. Extract a range into a new module of `gen/m11_claims/`. The module declares its
   lines with `covers()` (S52) and follows `m11/BRIEF.md`. `memory.py` shows the
   `heap=` pattern: lists of known size and the requested-bytes figures.
3. Commit the module, then `python3 gen/m11.py`, then run its claims with
   `gen/m11_run.py .work/hunt2 --ids …`. Fix the programs' own mistakes with `refix()`
   (text only, S45), run again, and screen the agreeing refusals' first diagnostics.
4. Triage into `gen/m11_triage.py`. Run the disagreements at the baseline and the
   newest `main`, appending to `results/<commit>/m11-disagree.jsonl`. Do a full final
   run, then `gen/m11_rows.py` (add the row finding to `FINDINGS`), `gen/m11_report.py`,
   and extend `REPORT.md` §12. Findings number on from F-041.

### M11 — the state at session 6's stop (history)

The author stopped the session at about 13:50 UTC because the cloud credit was
nearly spent. Nothing below is ticked. Everything committed is consistent: no
claim program ran except BUILTIN's, and every expectation was written from the
text before its program's first run.

**Done, committed and measured: BUILTIN_REFERENCE** (`gen/m11_claims/builtin.py`,
the session's own extraction, S42): 227 claims (2 examples, 108 rows, 117
rules), 194 testable (10 of them M10's programs), 33 untestable with reasons;
every code block and table row covered; the uncovered-line check (below) clean
but for history sentences. Its shakedown ran twice in scratch at HUNT2 (run 1:
165 agree, 27 disagree; 21 programs then fixed for their own mistakes, each
claim's `fixed` saying why, S45). **Run 2: 182 agree, 12 disagree**, and every
one of the 12 gives the same verdict at the baseline `c3bdae2` and at
`9f6f370` (old, not regressions). Triage is NOT done; the candidates:
- **documentation**, the compiler right by the decisions:
  - `#wild_ptr` (417b), `#ptr_add` (419b) and `atomic_from_ptr` (148c) are
    accepted outside a `wild` context, which no reference defines (D-315 struck
    the same rule from `#wild_slice` as "nothing ever enforced or defined it");
  - `close(release_fd(move o))` (261): the row's own spelling is PARSE-001
    (`move(o)` works, 261c agrees);
  - `sys`'s "a nested bare-builtin call is refused" (348) is stale since D-201
    typed every builtin (D-192's own text dates it);
  - `--seccomp` (368) and `--extra-picky=no-sys` (375) exist in no tool: npkc
    knows only `--extra-picky=no-wildx`, and npkg neither;
  - §5's inline assembly, the row and the example (432, 439), is PARSE-002.
- **compiler, lower priority:** `suspend_until` in a sync function (256) is
  accepted by the checker and refused by the emitter, `EMIT-002`.
- **the claim holds, more strictly than the program expected:** a store to a
  sealed page (154) and a call of an unsealed one (141) are refused at compile
  time (`WILDX-001`, `WILDX-002`) where the programs expected a run-time fault.
- Not a finding: a `shared_arena` alive in `main` at `exit 0` traps `WildLeak`,
  which MEMORY_REFERENCE §4.3 states ("an un-destroyed shared arena is a
  wild-role leak the exit check names").

**Drafted by the sub-agents, NOT yet reviewed, and excluded from the loader**
(a leading `_` makes `gen/m11.py` skip a module): the agents were stopped
mid-work. `python3 gen/m11.py --check --module _wip_X --doc D --lines A-B` gives:

| module | range | claims | check |
|---|---|---|---|
| `_wip_type1.py` | TYPE 1–660 | 322 | 0 errors: complete |
| `_wip_macro_ast.py` | MACRO 1–413 | 124 | 0 errors: complete |
| `_wip_macro_ast.py` | AST 1–645 | 0 | not started |
| `_wip_concurrency_io.py` | CONCURRENCY 1–648 | 152 | 6 errors |
| `_wip_concurrency_io.py` | IO 1–288 | 78 | 5 errors |
| `_wip_verif1.py` | VERIFICATION 1–845 | 357 | 18 errors (quotes on neighbouring lines) |
| `_wip_verif2.py` | VERIFICATION 846–2352 | 228 | 51 errors: stopped near line 1338 |

**Not started:** TYPE 661–2123, TRAITS, MEMORY, MODULE, BUILD, OP, CONTROL,
LEXICAL and AST (about 5 900 lines).

**To resume (a later session):**
1. The start checks and M0's rebuild as always (about 7 min).
2. For each `_wip_` module: fix its check errors, read its claims against the
   reference (the quotes are checked; the expectations and programs are not),
   then drop the `_wip_` prefix. `m11/BRIEF.md` is the convention.
3. Extract the nine ranges not started, by the brief: by the session, or by
   fewer sub-agents than session 6 used, since eleven at once is what spent the
   credit.
4. Commit every module (expectations before runs), run all with
   `gen/m11.py` then `gen/m11_run.py .work/hunt2` (about 10 s per 200
   programs), fix program mistakes (text only, `fixed=`), run again, and check
   every AGREEING refusal's first diagnostic: run 1 of BUILTIN had four
   refusals that agreed for a reason other than the claim's.
5. Triage by M5's steps; `gen/m11_report.py` writes `m11/RESULTS.md` and reads
   the classes from a `gen/m11_triage.py` still to be written; then REPORT.md
   §12.

### M11, session 7 (local): the start checks

- **The gate.** The workbench's brief (from `nitpick-libs_s7`, its orchestrator) says
  to work on a branch of this clone, so the session began with `git fetch origin && git
  switch -c local-m11 origin/main`. `origin/main` was `cbdec2e` (KNOWN_DEFECTS.md with
  M10's DEF-127 … DEF-133 and DEF-134). M10 is ticked and M11 is not. The branch's
  upstream was unset, so that no push can reach `main` (S47).
- **(a)** `uname -a` and `nproc` are under Environment below: 48 cores, the author's
  machine, shared with the compiler seat and the library agents.
- **(b)** `CLAUDE.md` was re-read, the silent-wrong-answer rule with it.
- **(c)** `.work/` was absent, so the toolchain was rebuilt by M0's commands, with two
  departures: LLVM 20.1.2 is the machine's own (S48); and the compiler's newest
  `main` is built for the findings only (S49).
- **(d)** M11 resumes at its first box, from "the state at the stop" above; nothing
  ticked was redone.

**The rebuild.** LLVM: `.work/llvm` is a symbolic link to `/usr/lib/llvm-20`, whose
`llvm-config --version` prints `20.1.2` (S48). The compiler was cloned from GitHub to
`.work/nitpick` at 14:24 UTC, in 4.8 s. Its `origin/main` is `1b4f0c6` (2026-09-26
07:09:26 -0400, 1.6.1 step 1: E-8, every module states its layout and triple), so
HUNT2 stays `9126350` (S41). Three worktrees were built by M0.5's command:
- `.work/hunt2` (`9126350`), alone, in 72.2 s;
- `.work/base` (`c3bdae2`) in 73.6 s and `.work/main1b4` (`1b4f0c6`) in 55.6 s, the
  two together.

| compiler | `npkc.ll` bytes / sha256 | `npkrt.o` | `npkc` bytes / sha256 |
|---|---|---|---|
| HUNT2 `9126350` | 28 857 206 / `2448b3b60d9eb189…`, as sessions 3–6 | 72 576 / `162b897539285a77…` | 9 972 872 / `c7212b6be06fe6a4…` (sessions 3–6: 9 972 944) |
| baseline `c3bdae2` | 28 111 929 / `4029fc70efbe9cd3…`, so the commissioning check passes | the same | 9 724 160 / `5fd636b9ab557c19…` (sessions 1–6: 9 724 232) |
| newest `main` `1b4f0c6` | 28 872 936 / `ec29f358c08dfe80…`, the digest its commit message states | the same | 9 977 536 / `07de906a85d58594…` |

The emissions and the runtime object are byte-identical to the earlier sessions'. The
linked `npkc` is 72 bytes shorter at both old compilers. Its `.comment` section reads
`Linker: Ubuntu LLD 20.1.2`. *Reasoned, not measured:* the release tarball's `ld.lld`
writes its repository URL and commit there instead, which accounts for the length. The
checks below show that the verdicts do not move.

Canaries (M0.6), at all three compilers: `canary.npk` gives npkc 0 and runs 0/0.
`canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` and writes no `.ll`.

**The machine checks.**
- The recall suite (`gen/run_known.py`) is identical to `results/<commit>/known-m10.txt`
  line for line at HUNT2 and at the baseline: 25 rows each.
- M10's 223 programs re-run at HUNT2 are identical to `results/9126350/m10.jsonl` in
  223 of 223 (npkc rc, codes, both legs, verdict; 19 s): 212 agree, 11 disagree, as
  recorded.

**The plan for the session (S50).** The five drafted ranges are reviewed, committed,
run and triaged, together with BUILTIN's candidates. The nine ranges not started are
about 6 600 lines, or roughly 3 300 claims at the drafts' density. That is far more than
the brief's "a few hours", so the session stops cleanly after the drafted modules, as
the brief says.

### M11, session 8 (local): the start checks, and MEMORY

- **The gate.** The brief came from `nitpick-libs_12`, the workbench orchestrator,
  with the author's approval. `local-m11` was fast-forwarded from `3d7d924` to
  `origin/main` `41ba27b`: KNOWN_DEFECTS.md now carries M11's findings as DEF-144 …
  DEF-154. M10 is ticked and M11 is not.
- **(a)** `uname -a` and `nproc` are under Environment below.
- **(b)** `CLAUDE.md` was re-read; it is unchanged at `41ba27b`.
- **(c)** `.work/` survives from session 7. Its three builds were byte-identical to
  session 7's digests (`npkc` `c7212b6b…`, `5fd636b9…`, `07de906a…`), so nothing was
  rebuilt. The compiler's newest `main`, `93bcb66` (2026-10-01, 1.6.1e, landing 93),
  is on GitHub's `main`. It was built as `.work/main93b` in 59.6 s, for the findings
  only (S57):
  - `npkc.ll` 31 367 470 bytes, `30b8f5b02191de09…`;
  - `npkrt.o` 72 656, `c8e5033ad17c70f8…`;
  - `npkc` 11 159 232, `0a8c9bf85ff680fb…`.
- **(d)** M11 resumes from "the state at the stop".
- **The machine checks.**
  - The canaries give their four verdicts at HUNT2, the baseline and `93bcb66`.
  - The recall suite is identical line for line at HUNT2 and the baseline (25 rows).
  - M10's 223 programs re-ran identical at HUNT2.
- **The week.** `jq .rate_limits.seven_day ~/.claude/usage-latest.json` read 86% at the
  start. The brief's limits: no new reference at 91%, land at 93%.

**MEMORY (all 533 lines), `gen/m11_claims/memory.py`.**
- **The extraction.** 181 claims (10 examples, 11 rows, 160 rules); 146 testable, 35
  untestable with reasons. Committed before any of its programs ran (`2f936bc`).
- **Run 1:** 131 agree, 15 disagree (12 s).
- **The fixes.** Seven programs were fixed for mistakes of their own (S53's `refix()`):
  - `buffer` used as a name (`me0120`, `me0179`; `me0179` had agreed for that reason,
    S55);
  - `.clone()`'s `Result` (`me0250`);
  - `drop` on a callee that is not `never fails` (`me0290`);
  - a taint test (`me0390`);
  - the large-frame programs (`me0507`, `me0530`). These had misread "refused at the
    prologue": the prologue refuses a frame that crosses the limit, so they now recurse
    until one does, and trap `StackExhausted` as the text says.
- **Run 2:** 137 agree, 9 disagree. The final full run of all 1 408 claims changed
  nothing.
- **Triage:**
  - 8 documentation rows (F-030);
  - DEF-148's shape, `me0461`, known, and refused `BORROW-016` at `93bcb66`;
  - F-029, found in run 1: `wild int8->:buffer` is accepted at its declaration and
    refused at its use.

  All are the same at the baseline, and at `93bcb66` but `me0461`.
- **The screen.** The agreeing refusals were screened (S55). One, `me0179`, had agreed
  for the reserved word's sake, not the claim's.

**OP (all 403 lines), `gen/m11_claims/op.py`.**
- **The extraction.** 159 claims (87 rows, 72 rules); 157 testable, 38 of them linked to
  the M10 item that tests exactly their sentence. The precedence table's rows are tested
  by expressions whose two readings give different values. Committed before any of its
  programs ran (`1161bad`).
- **The runs.**
  - Run 1: 143 agree, 14 disagree.
  - Five programs were fixed for mistakes of their own: the literals outside the 64-bit
    envelope, `-128i8`, the ternary's parentheses in the precedence row, and the
    pipe's spelling. `op0017` needed two fixes: the pipe's right side is the function,
    and its `Result` takes `?|`, not `raw`.
  - Runs 2 and 3: 147, then 148 agree. The final full run of all 1 565 claims changed
    nothing.
- **Triage of the 9.**
  - 5 documentation rows (F-031);
  - `<=>` twice, DEF-131, which compiles and runs at `93bcb66`;
  - 2 claims no program can test as written: no well-typed expression separates `|`
    from `&&`, and `!!b` is two negations.
- **The screen.** OP's agreeing refusals were screened, and each is the claim's own
  reason.

**CONTROL (all 415 lines), `gen/m11_claims/control.py`.**
- **The extraction.** 110 claims (14 examples, 7 rows, 89 rules); 108 testable, 43 of
  them linked to the M10 item that tests exactly their sentence. Committed before any of
  its programs ran (`717c7d2`).
- **Run 1:** 89 agree, 19 disagree.
- **The fixes.** Nine programs were fixed for mistakes of their own:
  - a unit variant's pattern is written qualified, `(Opt.Non)` or `(St.A)`, though a
    payload variant's `(Som(x))` is not. Seven programs, among them `ct0032f`, which had
    agreed for that reason (S55);
  - `$` is an int64 counter whatever the bounds' type, so the two `$` examples sum
    into an int64.
- **Run 2:** 98 agree, 10 disagree. The final full run of all 1 673 claims changed
  nothing.
- **Triage of the 10.**
  - 6 documentation rows (F-032);
  - 4 known: DEF-133 (d6); DEF-130 twice; and DEF-135, the compiler seat's own
    registry entry for a `tbb` loop bound holding ERR, which session 8 had begun to
    probe as new;
  - DEF-130's and DEF-135's claims agree at `93bcb66`.
- **The screen.** CONTROL's agreeing refusals were screened (S55).

### M11, session 9 (local): the start checks, and MODULE

- **The gate.** The brief came from `nitpick-libs_12`, the workbench orchestrator, with the
  author's approval, after session 8's handoff (S60). `git fetch origin && git merge
  --ff-only origin/main` was a no-op: `local-m11` = `origin/main` = `6eb5392`. M10 is
  ticked and M11 is not.
- **(a)** `uname -a` and `nproc` are under Environment below (the author's machine).
- **(b)** `CLAUDE.md` was re-read; it is unchanged since `41ba27b`.
- **(c)** `.work/` survives from session 8. Its three builds are byte-identical to the
  recorded digests (`npkc` `c7212b6b…`, `5fd636b9…`, `0a8c9bf8…`; `npkc.ll` and `npkrt.o`
  likewise), so nothing was rebuilt. The newest `main` for the findings stays `93bcb66`,
  as the brief names it.
- **(d)** M11 resumes from "the state at the stop".
- **The machine checks.**
  - The canaries give their four verdicts at HUNT2, the baseline and `93bcb66`.
  - The recall suite is identical line for line at HUNT2 and the baseline (25 rows, 13 s).
  - M10's 223 programs re-ran identical at HUNT2 (19 s): 212 agree, 11 disagree.
- **The week.** `jq .rate_limits.seven_day ~/.claude/usage-latest.json` read 87% at the
  start. The brief's limits: no new reference at 91%, land at 93%.

**MODULE (all 300 lines), `gen/m11_claims/module.py`.**
- **The extraction.** 139 claims (7 examples, 3 rows, 129 rules); 124 testable, 15
  untestable with reasons (8 `tool`, 4 `vague`, 2 `internal`, 1 `tree`). No M10 item
  tests a MODULE sentence. Committed before any of its programs ran.
  - The programs' module spellings are the compiler's own module programs' at HUNT2
    (`mod_qualified.npk`, `mod_file_import.npk`, `error_arm_forms.npk`).
  - 23 claims are shell scripts (S61): a support file in a subdirectory, a header the
    claim is about, an empty file, a diagnostic's wording, the IR's independence of the
    import order, and the `extern` blocks in HUNT2's form.
- **Run 1:** 92 agree, 32 disagree (5 s).
- **The fixes** (S45, through `refix()`, which now also reaches a support file, S62):
  - `hidden` is a reserved word: 14 programs' support files. `md0099b` had agreed for
    that reason (S55);
  - `nbridge.npk` imports `nsys.npk`, which nine scripts did not copy. `md0273` had
    agreed for that reason;
  - REACH-002 asks `failsafe` to name every constant that can reach it. That is
    `nbridge.npk`'s ten in seven scripts, and `md0080b.Boom`, which `classify` handles.
- **Runs 2 and 3:** 107, then 109 agree. The final full run of all 1 797 claims: 1 610
  agree, 187 disagree. The 1 673 earlier claims re-ran identical, and MODULE's are run 3's.
- **Triage of the 15**, each run at the baseline and `93bcb66`:
  - 7 documentation rows (F-033);
  - 3 lower-priority compiler rows over 5 claims (F-034): a byte payload's driver stub is
    TYPE-072 in its own generated code; `use m.f;` is refused against D-273 (2); a
    constant cycle's diagnostic names no cycle;
  - 1 known: DEF-153's `cstring` literal (`md0296b`), which compiles at `93bcb66`;
  - 2 not findings: a message gives the sentence's sense in other words (`md0122`); the
    IR's lines are the same for two import orders, and only one function moves
    (`md0185`).

  All stand at the baseline and at `93bcb66`, but `md0296b`.
- **The screen.** MODULE's agreeing refusals were screened (S55). Two had agreed for a
  reason of their own (`md0099b`, `md0273`), and both were re-spelled.

**LEXICAL (all 410 lines), `gen/m11_claims/lexical.py`.** The week read 88% before it.
- **The extraction.** 184 claims (9 examples, 34 rows, 141 rules); 181 testable, 3
  untestable (`vague`, `tree`, `internal`, one each). No M10 item tests a LEXICAL
  sentence. Committed before any of its programs ran.
  - The keyword productions are checked one source line at a time (44 claims). A
    script compiles a local binding and a function named after each word, and every
    compile must be refused. A word the text says is no keyword (D-135's seven, and
    the corrections table's removals) is compiled as a local's name, which must be
    accepted (S63).
  - The base-suffixed literals are written as the reference writes them, with no type
    suffix, in a typed declaration (`int32:b = 0Tt;`, D-148's contextual type).
- **Run 1:** 167 agree, 14 disagree (14 s).
- **The fixes.** Four programs were fixed for mistakes of their own:
  - a `decreases` measure called the identity helper, in a contract position (TYPE-060);
  - a check kept a `%%`;
  - a generic identity passed out its lent parameter (TYPE-047): `lx0240`, and `lx0239`,
    which had agreed through its own parse error.
- **Run 2:** 170 agree, 11 disagree. The final full run of all 1 978 claims: 1 780 agree,
  198 disagree. The 1 797 earlier claims re-ran identical.
- **Triage of the 11**, each run at the baseline and `93bcb66`:
  - 6 documentation rows (F-035): `++`/`--`, `sys_full`, the `f128` suffix, `0u64 -
    1u64`, the dead LBIM note twice;
  - 2 lower-priority compiler rows over 4 claims (F-036). Four keywords (`acquire`,
    `any`, `trit`, `nit`) are accepted as a function's name, which no call can reach:
    DEF-103's residue, measured by hand at HUNT2 and `93bcb66`. And a literal's trailing
    underscore is accepted;
  - 1 known: DEF-131's `<=>` (`lx0178`), which compiles and runs at `93bcb66`.

  All stand at the baseline and at `93bcb66`, but `lx0178`. At the baseline, which
  predates DEF-103's fix, more keywords are accepted as a function's name.
- **The screen.** LEXICAL's agreeing refusals were screened (S55): each is the claim's
  own reason. `lx0239`'s parse error is its claim's.

**AST (all 644 lines), `gen/m11_claims/ast.py`.** The week read 89% before it.
- **The extraction.** 202 claims (8 examples, 116 rows, 78 rules); 181 testable (2
  linked to the M10 item that tests exactly their sentence), 21 untestable (19
  `internal`: a row that lists only a node's fields; 1 `z3`; 1 `vague`). Committed
  before any of its programs ran.
  - A row or a note that states a spelling, a placement or a run-time rule is tested in
    that spelling, even where another reference's claim already tests the construct.
  - Where AST's sentence and another reference disagree, the claim takes AST's
    sentence. Examples: implicit generic arguments `f<int32>(x)` (LEXICAL:239 says the
    turbofish is always written), `ok(val)` among the bare-name builtins (AST:329 says
    it is removed), `?|` struck (every program uses it). The run says which side the
    compiler is on.
- **Run 1:** 150 agree, 31 disagree.
- **The fixes.** Two programs were fixed for mistakes of their own:
  - a `$$m` claim was live at the read (BORROW-013);
  - `move(mk())` was refused for the call's `Result`, not for its operand. It had
    agreed for that reason (S55).
- **Runs 2 and 3:** 151 agree, 30 disagree. The final full run of all 2 159 claims:
  1 931 agree, 228 disagree. The 1 978 earlier claims re-ran identical.
- **Triage of the 30**, each run at the baseline and `93bcb66`:
  - **F-037, a use after free** (`as0453`). A trait object built by `x => dyn Trait`
    points at freed storage, and its method returns the 0xAA poison (170).
    - Measured by hand in four variants, then by `gen/run_findings.py`: three
      programs exit 10 and two controls exit 0, at HUNT2 twice, the baseline and
      `93bcb66`, both legs.
    - The implicit `dyn Trait:d = move(x);` is correct.
  - F-038: npkc traps (exit 3) on `give` or `fall` outside a pick arm (`as0202`,
    `as0203`, `as0267`), at all three compilers;
  - F-039: 4 lower-priority compiler rows:
    - a `comptime` value parameter is EMIT-002;
    - `<|` takes its function on the right, as `|>` does;
    - a non-constant `joins` is accepted;
    - any attribute name is accepted;
  - F-040: 20 documentation rows;
  - 2 known: DEF-131's `<=>` and DEF-153's `cstring` literal. Both compile at `93bcb66`.

  All stand at the baseline and at `93bcb66`, but the two known.
- **The screen.** AST's agreeing refusals were screened (S55). One had agreed for a
  reason of its own (`as0352`), and was re-spelled.

**BUILD (all 682 lines), `gen/m11_claims/build.py`.** The week read 89% before it.
- **The extraction.** 97 claims (4 examples, 26 rows, 67 rules); 38 testable, 59
  untestable: 28 `tool`, 17 `tree`, 6 `vague`, 6 `z3`, 1 `platform`, 1 `internal`. The
  reference describes the compiler's own build: the ladder, the two test runners, the
  verified build. Committed before any of its programs ran.
  - `npkg build` cannot build a project outside the compiler's repository: it reads the
    floor's `runtime/npkrt.ll` from the manifest's root. This was measured in a scratch
    project, as a probe of `npkg`'s spelling. `npkg test` builds the compiler's ladder
    before its entries, which is longer than a script's 60 s.
  - What a script can check is tested (S64):
    - each refusal `npkg` makes before it builds: the manifest, the lock, the toolchain
      pin, `edition`, `update`;
    - the `[[test]]` schema refusals and the stage names, which `npkg test` refuses by
      name before anything runs;
    - every rule about what `npkc` emits.

## Environment

*(session 9, measured 2026-10-02 16:31 UTC; M11 resumed here — the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-34-generic #34~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep  4 15:38:29 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 21 used, 50 free, 135 available
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  1.7T used  4.9T avail (26%)
python3:   Python 3.12.3
llvm:      /usr/lib/llvm-20 (llvm-config 20.1.2), linked as .work/llvm
earlyoom:  active
```

*(session 8, measured 2026-10-02 15:07 UTC; M11 resumed here — the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-34-generic #34~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep  4 15:38:29 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 22 used, 51 free, 134 available; Swap 15
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  1.7T used  4.9T avail (26%)
python3:   Python 3.12.3
llvm:      /usr/lib/llvm-20 (llvm-config 20.1.2), linked as .work/llvm
earlyoom:  active
```

*(session 7, measured 2026-09-26 14:23 UTC; M11 resumed here, on the author's machine
— the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-34-generic #34~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep  4 15:38:29 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 14 used, 93 free, 142 available; Swap 15 (2 used)
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  1.7T used  4.9T avail (26%)
os:        Linux Mint 22.3 (Ubuntu 24.04 base)
python3:   Python 3.12.3
git:       2.43.0
llvm:      /usr/lib/llvm-20 (llvm-config 20.1.2), linked as .work/llvm
earlyoom:  active
```

The machine is shared with the compiler seat's harnesses and the library agents.
Parallelism stays at 4 jobs (CLAUDE.md rule 7, S1).

*(session 6, measured 2026-09-26 13:03 UTC; M11 run here — the start check (a))*

```
uname -a:  Linux vm 6.18.44-fc-v37 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
nproc:     4
free -g:   Mem 15 total, 0 used, 15 free, 15 available; Swap 0
df -h .:   /dev/vda  252G  7.1G used  30G avail (20%) -- 30 GB is the session's writable allowance
os:        Ubuntu 24.04.4 LTS
python3:   Python 3.11.15
git:       2.43.0
```

A fresh VM of the same kind as sessions 2–5: `.work/` did not exist.

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

*(session 2, measured 2026-09-26 03:34 UTC; M5 and M6 run here)*

```
uname -a:  Linux vm 6.18.44-fc-v42 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
nproc:     4
free -g:   Mem 15 total, 0 used, 14 free, 15 available; Swap 0
df -h .:   /dev/vda  252G  7.1G used  30G avail (20%) -- 30 GB is the session's writable allowance
os:        Ubuntu 24.04.4 LTS
python3:   Python 3.11.15
git:       2.43.0
```

This is the cloud VM `PLAN.md` describes (4 vCPUs, 16 GB, 30 GB). Outbound
HTTPS goes through an agent proxy.

*(session 3, measured 2026-09-26 09:57 UTC; M8 run here — the start check (a))*

```
uname -a:  Linux vm 6.18.44-fc-v37 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
nproc:     4
free -g:   Mem 15 total, 0 used, 15 free, 15 available; Swap 0
df -h .:   /dev/vda  252G  7.1G used  30G avail (20%) -- 30 GB is the session's writable allowance
os:        Ubuntu 24.04.4 LTS
python3:   Python 3.11.15
git:       2.43.0
```

A fresh VM of the same kind as session 2's: `.work/` did not exist.

*(session 4, measured 2026-09-26 10:27 UTC; M9 run here — the start check (a))*

```
uname -a:  Linux vm 6.18.44-fc-v37 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
nproc:     4
free -g:   Mem 15 total, 0 used, 15 free, 15 available; Swap 0
df -h .:   /dev/vda  252G  7.1G used  30G avail (20%) -- 30 GB is the session's writable allowance
os:        Ubuntu 24.04.4 LTS
python3:   Python 3.11.15
git:       2.43.0
```

A fresh VM of the same kind as sessions 2 and 3: `.work/` did not exist.

*(session 5, measured 2026-09-26 11:57 UTC; M10 run here — the start check (a))*

```
uname -a:  Linux vm 6.18.44-fc-v37 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
nproc:     4
free -g:   Mem 15 total, 0 used, 15 free, 15 available; Swap 0
df -h .:   /dev/vda  252G  7.1G used  30G avail (20%) -- 30 GB is the session's writable allowance
os:        Ubuntu 24.04.4 LTS
python3:   Python 3.11.15
git:       2.43.0
```

A fresh VM of the same kind as sessions 2–4: `.work/` did not exist.

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
- **S12 — session 2 works on branch `claude/awesome-cannon-b092si`**, which the
  session's harness names. It started at `1bcd82d`, the same commit as `main`
  and as session 1's branch.
- **S13 — LLVM was fetched to a file, then extracted.** PLAN.md 0.2's piped
  `curl | tar` was reset mid-transfer by the agent proxy's tunnel (curl 56,
  `ws_closed_mid_exchange`), so the same URL was downloaded with `curl -C -` in
  a retry loop (the first attempt completed), checked with `xz -t`, and
  extracted with the same `tar -xJ --strip-components=1`. It is the same
  release tarball, and `llvm-config --version` prints `20.1.2`.
- **S14 — DEF-106 was added to `KNOWN_DEFECTS.md` on the author's
  instruction** (the workbench's O-N24; fixed in 1.6.0 step 4b as
  `NITPICK-TYPE-086`, not in HUNT). The writes INTO `fixed` storage that M3
  and M4 flagged are its instances and are deduplicated, not investigated:
  `c0039`/`c0040`, `c0185`/`c0186`, `c0203`–`c0206`, `c0645`/`c0646`,
  `c0753`/`c0754`, and the imported twins `c0151`/`c0152`, `c0329`–`c0332`,
  `c0353`–`c0356`, `c0371`/`c0372`.
- **S15 — the machine changed between M4 and M5**, so before M5 the rebuild
  was checked to be byte-identical (above) and the committed first-100 HUNT
  records were reproduced exactly. The M5 cells are appended to the same
  `results/6fb85d3/cells.jsonl`.
- **S16 — CONFIRMED A DEFECT (2026-09-26): DEF-108**, the compiler's `NITPICK-FLOW-001`, by the author's own rule (every path of every function, `NIL` included, must leave explicitly). The note below was written under the first brief, which counted only memory-safety faults — `CLAUDE.md` now counts silent wrong answers too.
- **S16 — a function with a declared result and no `pass` compiles** and
  returns a zero value: 0 for `int32`, an empty string for `string`. `main`
  without `exit` exits 0. This was probed at both compilers (npkc 0, 0/0),
  after the first minimiser run produced programs leaning on it. No reference
  sentence says so (searched: TYPE, CONTROL, MEMORY, SPEC_GAPS). It is outside
  the grid's definition of a defect, since a zero `string` is a vacancy and
  its drop is a no-op, so it is recorded here and in REPORT.md, not
  investigated (CLAUDE.md rule 8).
- **S17 — minimisation.** `gen/minimize.py` deletes single lines and
  brace-balanced blocks while the verdict (npkc, -O0, -O2) stays exactly the
  cell's. It never deletes a bare `pass …;`/`exit …;` line (S16): a reproducer
  must not rest on an implicit zero result. A finding's committed programs are
  the minimiser's output with the grid's full observer (21/22/23/70) and
  fail-safe restored, so that each exit code names what it saw. The raw
  outputs stay in `minimized/` and are measured as well.
- **S18 — one finding per shape, not per cell.** The 16 `for_binding` cells
  are one shape (three write paths through one binding, as DEF-102 counts
  every write path as one defect), and the 4 generic `move` cells are another.
  Each finding keeps a program per write path and observer, plus its controls.
- **S19 — session 3 works on branch `claude/fervent-feynman-fhlm63`**, which
  the session's harness names. It started at `7370a9d`, the commit that wrote
  M8–M11 into `PLAN.md`.
- **S20 — HUNT2 is `9126350`, not `2eea6f4`.** At the clone (09:58 UTC) the
  compiler's `origin/main` was `2eea6f4` (1.6.1 step 0: DEF-107). A re-fetch
  at 10:01 UTC, before anything was built, showed `9126350` (1.6.1 step 0, the
  NIKOS half). PLAN.md 8.1 says HUNT2 is the newest `origin/main`, so it is
  `9126350`. It differs from `2eea6f4` in six files, all docs and
  `meta/roadmap/1.6/` tools (`CLAUDE.md`, `meta/NOTICES.md`,
  `meta/roadmap/1.6/1.6.1.md`, `meta/roadmap/1.6/tools/engines.sh`,
  `meta/roadmap/1.6/tools/pins.txt`, `meta/roadmap/OPEN_DECISIONS.md`), with
  nothing under `src/`, `lib/`, `runtime/`, `bootstrap/` or `npkg/`. So its
  compiler is built from the same sources as `2eea6f4`'s. The author confirmed
  mid-session that the build needs LLVM 20.1.2 and nothing else (no z3, no
  analyzer engines), and that M0's commands stand unchanged.
- **S21 — a finding's record at a later compiler sits beside the first.**
  `gen/run_findings.py` takes `--name`, so M8's F-001/F-002 runs are
  `VERDICTS-9126350.txt`. The committed `VERDICTS.txt` (HUNT `6fb85d3`) is
  kept as it was measured.
- **S22 — 8.3 changed nothing in the generator, because nothing needed
  changing.** The plan asks for "`pass NIL;` in each `NIL` function, and so
  on". `gen/grid.py` has emitted an explicit `pass`/`exit` at the end of every
  function since M2: the M5 minimiser leaned on implicit returns, not the grid
  (S16, S17). This was measured statically and by HUNT2's own `FLOW-001`
  (M8 section), with a planted fall-off as the control, rather than taken
  from reading `grid.py`. `gen/check_leaves.py` is committed as the check.
  The baseline was built and re-run anyway: 8.3 asks for it, and 8.6 needs it.
- **S23 — two more compilers were built for 8.5's investigation**, beyond
  what M8 names: 1.6.0 step 3g (`5bdae98`) and step 3h (`c1a4a05`), in the
  worktrees `.work/s3g` and `.work/s3h`. 8.5 counts a changed refusal code as
  a regression "until shown otherwise", and 3h's parent is 3g, so running the
  12 changed cells and their 64 import-place neighbours at the two adjacent
  commits shows which commit changed them. The runs are committed as partial
  records, `results/<commit>/cells-imported.jsonl`, and not as `cells.jsonl`,
  so that `gen/run.py` and `gen/classify.py` never mistake them for a whole
  grid. The old HUNT `6fb85d3` was not rebuilt: its committed record is what
  8.5 compares with, and 3g agrees with it in all 76 import cells.

- **S24 — session 4 works on branch `claude/focused-ride-3dfwa8`**, which the
  session's harness names. The branch started at `7370a9d` (the plan's M8–M11
  commit, then `main`), without M8. M8 lived on `claude/fervent-feynman-fhlm63`
  (`ea77960`), a direct descendant, so it was fast-forwarded in
  (`git merge --ff-only`) before any work. The workbench's orchestrator
  confirmed during the session that it had fast-forwarded `main` to `ea77960`
  at 10:27 UTC, and this branch's history is `main`'s.
- **S25 — HUNT2 stays `9126350`.** M9 runs "at the baseline and at HUNT2"
  (PLAN.md 9.7), and HUNT2 is the compiler M8 named. The compiler's
  `origin/main` was still `9126350` when it was cloned at 10:28 UTC, so no
  newer compiler existed to consider.
- **S26 — `gen/snip.py`**, a one-file runner by PLAN.md's recipe, at one or
  both compilers, optionally under `NPK_HEAP_STATS`. It is for probes and
  controls, with one job at a time. The grid's cells still go through
  `gen/run.py`.
- **S27 — the widened grid is a second generator, `gen/grid9.py`, writing
  `cells9/`, with ids `mNNNN`.** `gen/grid.py` and its 956 cells are unchanged,
  so every M2–M8 record stays reproducible. `grid9.py --selfcheck` renders the
  M2 grid's 956 read_after and drop_at_exit programs with the new builder. With
  the M2 helpers and fail-safe swapped back in, all 956 are byte-identical to
  `grid.py`'s. So section A's new observers ride on exactly the M2 programs.
- **S28 — `gen/run.py` gained the leak observer's run (additive).** A cell whose
  `meta.json` says `"heap": true` runs under `NPK_HEAP_STATS=1`, and each leg
  records the `heap:` line's three words. Cells without the key run exactly as
  before.

- **S29 — the shakedowns changed the generator, never an expectation.** M2's
  practice was followed: a run into scratch, then its generator's own bugs
  fixed before any result counts. Four such fixes were made (above), each
  committed before the run that counts. Where a verdict differs from its
  expectation because the language's rule is not the one the generator
  assumed, the expectation stands as written, and the difference is explained
  in the triage below. Examples are D-065's whole-binding rule refusing a swap
  through a field, and `TYPE-047` refusing `pass self.v` through a receiver.
- **S30 — the leak observer's verdict is the `heap:` line.** `gen/minimize.py`
  gained `--live N`, which keeps a deletion only while the leak reading stays
  N on both legs. `gen/run_findings.py` gained `--heap`, which records both
  legs' `heap:` words beside the exit codes. Both are additive.

- **S31 — session 5 works on branch `claude/peaceful-mccarthy-ohbxra`**, which the
  session's harness names. It started at `88e6355`, the workbench's commit after M9's
  merge, which is `origin/main`.
- **S32 — HUNT2 stays `9126350`.** PLAN.md 10.2 runs each program "at the baseline and
  at HUNT2", and HUNT2 is the compiler M8 named (S20, S25). The compiler's
  `origin/main` had moved to `b564746` (1.6.1 step 0c: DEF-116's fix,
  `NITPICK-TYPE-014`, and DEF-117) by 11:57 UTC, and to `9f6f370` (a record commit)
  by 12:29. Neither is HUNT2.
- **S33 — each compiler is held to its own reference where the text changed; otherwise
  to HUNT2's.** An item's expectation comes from HUNT2's reference text. Where the
  baseline's own reference says something else, the item carries a second
  expectation for the baseline, from the baseline's text (`expect_base`):
  - the tag-only enum's `intN =>! enum` (`c18`);
  - DEF-108's shapes (`q01`–`q07`, `q11`), whose baseline has no FLOW-001 sentence.
    Its expected answer there is the known defect's measured one, which is what
    10.3's "flagged" means.

  The block string (`t04`) keeps one expectation, since the baseline's production
  already said three quotes (its lexer had DEF-98). The citations show, per quote,
  the line at each compiler or `absent`.
- **S34 — the M10 program convention.**
  - `failsafe` carries the grid's arms (S4) plus seven more, with unused codes:
    `ShiftRange` 111, `CastRange` 112, `BadStep` 113, `BorrowOverlap` 114,
    `RequiresViolated` 115, `EnsuresViolated` 116, `InvariantViolated` 117.
  - A program's own error `E<k>` exits 80+k.
  - Exit 0 is the reference's answer, and 10–59 name the check that saw a wrong value.
  - A value meant to be computed at run time goes through a `never fails` identity
    function (`raw v32(x)`), so the compiler's folder cannot evaluate it. A value
    meant to be folded is a module `fixed` initialiser. Where the reference speaks of
    both (`OP_REFERENCE`: "a constant expression means what the run time means"),
    there is an item for each.
- **S35 — M10's records are per compiler:** `results/<commit>/m10.jsonl` (one JSON line
  per program: npkc rc, codes, first diagnostic, both legs, verdict) and
  `results/<commit>/known-m10.txt` (this session's recall-suite run, 25 rows). The
  M1/M8 files `results/known-*.txt` are kept as measured.
- **S36 — expectations before runs.** `gen/m10.py`, the programs, `m10/EXPECT.tsv` and
  the checklist are committed before any program runs. If a program fails for a
  mistake of its own (a spelling the language does not have, where the item is about
  something else), only its text changes, never its expectation, and each such fix is
  listed here. This is M2's and M9's practice (S29).

  The two fixes, both after run 1:
  - `m12`: `a > 0` on a `tbb8` → `a == 0`, since ordering on tbb is a compile
    error (D-093);
  - `d16`: direct field writes into `Hs:h;` → D-225's `drop init($$m h);`,
    since D-010 refuses the first.

  Run 1's records are kept as `results/<commit>/m10-run1.jsonl`.
- **S37 — a third compiler for the findings only.** The compiler's newest `main`,
  `9f6f370`, was built in `.work/main9f6` (88.9 s; `npkc.ll` 28 872 365 bytes,
  sha256 `7bab110a1e45cc9d…`; canaries pass). Each finding's programs were run
  there twice (`VERDICTS-9f6f370.txt`), so the workbench knows whether a shape
  still stands at the tree the maintainers work on. This is S23's practice.
  No checklist verdict is taken from it.
- **S38 — the documentation findings are one finding, F-017, with a row each.**
  PLAN.md 10.2 asks for a documentation finding to be "reported the same way,
  with the reference line". Each of F-017's seven has:
  - its sentence, file and line;
  - its program, and a control where one helps;
  - its verdicts at the three compilers.

  They share a directory because each is one sentence and one program, and
  none is a wrong answer at run time.
- **S39 — a finding's program exits 0 on the reference's answer and 10 on the
  measured wrong one** (11 on anything else). So each program names what it
  saw, as the grid's observer codes do. The controls exit 0. The one exception
  is F-016: its programs exit the matched arm's code, 4, which is the
  reference's answer.

- **S40 — session 6 works on branch `claude/pensive-allen-pdhqpv`**, which the session's
  harness names. It started at `626c22d`, the workbench's commit after M10's merge, which
  is `origin/main`.
- **S41 — HUNT2 stays `9126350`.** PLAN.md 11.1 extracts from "the compiler's references
  at HUNT2" and 11.2 runs "at HUNT2", and HUNT2 is the compiler M8 named (S20, S25, S32).
  The compiler's `origin/main` is `9f6f370`, the docs-only record commit over `b564746`
  that session 5 saw (S32); it is built as `.work/main9f6` for the findings only (S37).
- **S42 — the extraction was split by line range.** The fourteen references (10 433
  lines) were divided into twelve ranges. The session wrote BUILTIN's claims itself
  (`gen/m11_claims/builtin.py`), and eleven sub-agents wrote the other eleven ranges, one
  module each, from one brief committed as `m11/BRIEF.md`. **No agent ran the compiler,
  a program or `llc`:** every expectation was written from the reference's text before
  the first run, as S36 requires. Each agent learnt the language from programs that
  compile at HUNT2 (M10's, `known/`, `findings/`, the compiler's own
  `tests/backend/programs/`). The session reviewed every module before the commit that
  precedes the first run.
- **S43 — a claim is checked against its line, and coverage is checked mechanically.**
  A claim's id is its reference's two-letter prefix and its HUNT2 line (`bi0242`,
  `bi0242b`), and it quotes that line: `gen/m11.py` refuses a quote not on its line.
  It also refuses a reference with a fenced code block or a table body row that has no
  claim at its line, unless the row's table is `excluded` with a reason (a history or a
  legend). So "every code example" and "each row of a table" are counted by the
  generator; the normative prose sentences are extracted by reading, and their count
  is the reading's.
- **S44 — M11's `failsafe` names every prelude identity at HUNT2** (31): M10's twenty
  (S4, S34) and `StaleHandle` 100, `DeadlineExceeded` 101, `ChannelClosed` 102,
  `DriverLeak` 103, `IoEof` 104, `WouldBlock` 105, `Interrupted` 118, `NotFound` 119,
  `Exists` 120, `CrossDevice` 121, `BadPath` 122. A program's own `E<k>` exits 80+k, and
  exit 0 is the reference's answer (S34, S39).

- **S45 — a program's text may change after its first run, its expectation not.**
  S36's rule, carried to M11: a claim's `fixed` field says why its program changed
  (a spelling of the program's own, not the claim's). One exception is recorded
  where it happens: a claim read inside `failsafe` signals the reference's answer
  with exit 42, not 0, because REACH-004 forbids `failsafe` an exit of 0 (D-014);
  the claim itself is unchanged (`bi0262`, `bi0263`). An `EMIT-002` never counts as
  a claimed refusal: its message names itself a compiler defect (`gen/m11_run.py`).
- **S46 — the session stopped mid-M11 on the author's word** (the credit nearly
  spent). The eleven sub-agents were stopped; their partial modules are committed
  as `gen/m11_claims/_wip_*.py`, unreviewed and outside the loader, so that nothing
  committed claims more than was done.

- **S47 — session 7 works on branch `local-m11` of the author's local clone**, as the
  workbench's brief says: `git switch -c local-m11 origin/main` at `cbdec2e`. The
  workbench reviews the branch and fast-forwards `main`; the session never pushes to
  `main`. Its upstream was unset at once, since `switch -c` had set it to `origin/main`.
  The brief also asks for one session in sequence with no sub-agents, since session 6's
  eleven parallel extractors are what spent the cloud credit.
- **S48 — LLVM 20.1.2 is the machine's own**, `/usr/lib/llvm-20` (Ubuntu's build),
  linked as `.work/llvm` so that every runner's default finds it. PLAN.md 0.2's rule is
  "never substitute another LLVM". The version is exactly `20.1.2`, and the checks
  bear it out: the emissions are byte-identical, and so is the runtime object; the
  recall suite matches at both compilers; M10's 223 programs match. Only the linked
  `npkc` moved, by 72 bytes, in its linker comment.
- **S49 — the compiler's newest `main` is `1b4f0c6` (1.6.1 step 1)**, built as
  `.work/main1b4` for the findings only. This is S37's practice: each finding's programs
  also run there, so the workbench knows whether a shape stands at the tree the
  maintainers work on. No claim's verdict is taken from it. HUNT2 stays `9126350`
  (S41), since the claims are read from its lines.
- **S50 — the drafted modules first; the ranges not started are left for later.** They
  are the rest of TYPE (661–2123), TRAITS, MEMORY, MODULE, BUILD, OP, CONTROL, LEXICAL,
  AST, and VERIFICATION after `_wip_verif2`'s last claim: about 6 600 lines, or roughly
  3 300 claims at 0.5 a line (BUILTIN gave 227 for 447 lines, TYPE 1–660 gave 322).
  The brief says to stop at a clean point after the `_wip_` modules if the rest looks
  like more than a few hours. Also, `gen/m11.py --module _wip_X` now loads the draft
  it names. Session 6's loader skipped every `_` module, even one named, so the
  command in "the state at the stop" could not check a draft as written. Run with the
  new loader, it reproduces that table exactly: 322, 124, 152 and 78 claims with 0, 0,
  6 and 5 errors, and 357 and 228 with 18 and 51.
- **S51 — how the drafts were reviewed, before any of their programs ran.**
  - **The check errors.** They were fixed mechanically; no expectation changed.
    - Nine ids did not match their lines (the quote was on the line given): each id
      was renamed to its line, with a letter where the line already had a claim.
      `cc0091` and `cc0092` were swapped, and `cc0430` moved to 429.
    - Eighteen quotes in `verif1` sat on a neighbouring line: each moved to the line
      holding it, the id with it. One quote (`vf0306`) broke across two lines and was
      cut to the part on its line; another (`vf0344b`) was made longer, to be unique.
    - Two cross-references were updated to the new ids.
  - **`verif2` stopped at the end of §7c.** It covers 846–1247; its 51 errors were
    §8's and later blocks and rows, never started. `macro_ast`'s AST half had no claim
    (the module is now `macro.py`).
  - **The reading.** For IO (all 78) and CONCURRENCY 1–310, every claim was read with
    the full reference text around it. For the other 1 100 or so, each claim's text and
    expectation were read against its own line (a claims-only sheet), looking for an
    expectation the sentence does not state. None was found: the drafts are careful,
    and extract the text faithfully even where it contradicts itself. Example: TYPE:53
    traps on overflow (D-210) while TYPE:475 still says wide integers wrap (D-037).
    The full text around a claim is re-read at triage, for every claim whose program
    disagrees. This lighter reading is the brief's cost limit applied. A misread
    expectation found at triage is classed as the extraction's error, never "fixed" by
    changing the expectation (S45).
  - The drafts dropped their `_wip_` prefix: `type1.py`, `macro.py`,
    `concurrency_io.py`, `verif1.py` and `verif2.py`.
- **S52 — a module declares the lines it extracted: `covers(doc, first, last)`.** The
  whole-set check demanded coverage of every reference, so with nine ranges not
  started, `m11/` could never be written from the whole set. Coverage (every fence,
  every table row) is now checked inside the declared ranges only. A claim outside its
  own module's ranges is an error, and so are overlapping ranges. `m11/CLAIMS.md` lists
  the ranges extracted and those not yet extracted, so the denominators say which part
  of each reference they are over. Extracted: BUILTIN, CONCURRENCY, IO and MACRO
  whole, TYPE 1–660, and VERIFICATION 1–1247, which is 3 704 of the 10 433 lines.
- **S53 — a program's text changes after a run through `refix()`; four runs.**
  - `m11lib.refix(cid, why, pairs, field)` replaces text in a claim's program. Each
    `old` must occur, and `why` goes into the claim's `fixed`. The fixes sit at the end
    of each module, after the drafts, so each change is a small diff that can be read.
    The expectation never changes, except `cc0636`'s, under S45's recorded exception.
  - **38 programs changed**, all for mistakes of their own. The main one: `verif1`'s
    shared rows helper matched `main`'s rows by `<module>.` / `<module>.main`, but
    `main`'s symbol in `rows.txt` is `@main`, so every count in `main` read 0. The
    helper was corrected in all 25 scripts that embed it, and `vf0306`'s inline filter
    separately. None of those that agreed moved to disagree.
  - **The runs**, all at HUNT2, both legs, 4 jobs, about 210 s each:
    - run 1: 1 093 agree / 169 disagree;
    - run 2: 1 114 / 148, 21 moved, all to agree;
    - run 3: 1 118 / 144, the four programs re-fixed moved;
    - the final run: 1 118 / 144. Only `mc0312b` changed, which agreed in run 3 for
      another reason (a spelling's `PARSE-001`) and now agrees for its own (`TYPE-069`).
  - Runs 1–3 are kept as `results/9126350/m11-run1…3.jsonl`.
- **S54 — the triage, and how the findings are grouped.** Every disagreement has one
  class in `gen/m11_triage.py`, which checks that the classes and the disagreements
  match exactly. Following S18 (one finding per shape) and S38 (sentence-sized rows
  share a directory):
  - each compiler shape with a wrong answer, a memory fault, invalid IR, a crash, an
    unusable flag or a lost safety check has its own finding, F-018 … F-026, with
    minimal programs and controls, run twice at HUNT2 and once each at the baseline and
    `1b4f0c6`;
  - the sixteen safe compiler departures are F-027's rows;
  - the ninety-four documentation claims are F-028's rows.

  The rows cite the claims' own programs in `m11/programs/`, with verdicts from the
  final run and from `results/<commit>/m11-disagree.jsonl` (`gen/m11_rows.py`). A
  claim whose program tested more than its sentence is classed "not a finding",
  never re-expected (S45, S51).
- **S55 — the agreeing refusals were screened.** Of 368 agreeing refusals, the 238 with
  no named code were screened. Those whose first diagnostic is a parse, lex,
  resolve-002, reach or `raw` error (66) were read by hand. All but one are refusals
  of a spelling the claim itself says does not exist. The one, `mc0312b`, was
  re-spelled (S53).
- **S56 — the session stops after the drafted modules, with M11 unticked.** This is the
  brief's instruction (S50). The extraction left is about 6 700 lines. Its state and
  the way back are "M11 — the state at the stop" above.
- **S57 — session 8 works on `local-m11`, on the brief from `nitpick-libs_12`.** The
  scope is MEMORY, then OP, then CONTROL. Each reference stops at a clean point:
  extracted, run, triaged, committed and pushed to `local-m11` only, with a message to
  the workbench. The week's usage is read before each reference: no new reference at
  91%, land at 93%. There are no sub-agents. The compiler's newest `main` for the
  findings is `93bcb66`, which replaces `1b4f0c6` (S37, S49), and deduplication is also
  against its registry, read with `git show 93bcb66:meta/roadmap/OPEN_DECISIONS.md`.
  HUNT2 stays `9126350` (S41).
- **S58 — a reference's length is its real last line** (`m11lib.doc_len`). The count
  had included the empty element after each file's final newline: one line too many per
  reference, 10 433 for 10 419. The workbench's brief named the right ends (TYPE 2122,
  VERIFICATION 2351). Every expectation and claim is unaffected; only the "lines"
  figures change.
- **S59 — MEMORY's heap claims use lists of known size.** A `List<int64>` of capacity c
  is one managed block of exactly 8c bytes, by the prelude's `list_init`. The `heap:`
  line reports requested bytes, so "dropped at scope exit, not at last use" or "a
  temporary dies at its statement's end" is an exact peak, read from the code and not
  from a run. All six such claims agree.

- **S60 — session 9 works on `local-m11`, on the brief from `nitpick-libs_12`.** Session 8
  handed over with a pause until the week's reset. The workbench lifted it with the
  author's approval: the machine is restarted only after every session has finished. The
  scope is the ranges not started, smallest first: MODULE, LEXICAL, AST, BUILD, TRAITS,
  VERIFICATION 1248–2351, TYPE 661–2122, as many as the week allows. The other rules are
  S57's. Deduplication is against KNOWN_DEFECTS.md, the compiler's registry at `93bcb66`,
  and F-029 … F-032 (the workbench's O-N35).
- **S61 — a claim whose files the DSL cannot lay out is a shell script.** `files=` writes
  support files beside the root only, and `gen/m11.py` requires each to open with its own
  header. A claim about a subdirectory (`network/mod.npk`, `sub/a.npk`), about a header
  (missing, wrong, or a file with no declarations), or about the `extern` vocabulary is
  an `sh:0` script instead. It writes its files with heredocs, then either builds and
  runs both legs by PLAN.md's recipe (`build`, `legs`), checks a refusal (`refused`, which
  never counts an `EMIT-002`, as `gen/m11_run.py` does not), or checks an acceptance.
  The `extern` blocks are written in HUNT2's form (`Bridge->` first, `Duration` last; the
  compiler's own `extern_stub.npk`), so each script copies the compiler's
  `lib/nbridge.npk` beside its program. The reference's own spelling of a block is
  tested separately, as a claim program (`md0241`).
- **S62 — `refix()` reaches a support file:** `field="files:<name>"`. MODULE's run 1
  showed that a support file can be where the program's own mistake sits (`hidden`).
  A second `refix()` of one claim passes the first one's reason on, so the claim's
  `fixed` names both.
- **S63 — a keyword list is checked word by word, in two positions.** A word of a keyword
  production is reserved when a local binding of that name and a function of that name
  are both refused (one `sh:0` script per source line, `lexical.py`'s `kw`). F-029 found
  a reserved word accepted in one position and refused in another, so one position is
  not enough. A word the text says is NOT a keyword is checked as a local's name only.
  A module-level function's name can be refused for reasons of its own, a prelude or
  builtin name (D-239, D-294).
- **S64 — BUILD's `npkg` claims run in a scratch project, and stop before the build.**
  Each script writes a `nitpick.toml`, a one-function `src/main.npk` and (unless the claim
  is about its absence) a `nitpick.lock`, and runs `$NPKG`. A stage name is checked by an
  entry with that stage and a bogus `kind`: the runner refuses the entry by name before
  anything runs. A known stage is refused for its kind, an unknown one for the stage. So
  no claim waits on the compiler's ladder.

## Log

- 2026-09-25 (session 1, this branch): started at M0.1 with nothing ticked.
  M0 done: LLVM 20.1.2 fetched, compiler cloned, `base` (c3bdae2) and `hunt`
  (6fb85d3) worktrees built in 67 s / 69 s, digests recorded, both commissioned.
  M1 done: recall suite matches at the baseline 19/19; HUNT carries only the
  DEF-99 fix.
  M2 done: 956 cells generated, 1 284 skipped; one generator bug found and
  fixed in a baseline shakedown.
  M3 done: whole grid at c3bdae2 in 58 s; every known shape flagged, no miss.
  M4.1-4.2 done: 100 cells at HUNT; stopped at the calibration checkpoint.
- 2026-09-26 (session 2, branch `claude/awesome-cannon-b092si`, the cloud VM):
  the author said to continue (M4.3). The toolchain was rebuilt by M0's
  commands, byte-identical, and the machine change was checked (S15). DEF-106
  was added (S14). M5.1: the remaining 856 cells ran at HUNT in 43 s; 40 cells
  moved from the baseline, all to `TYPE-084`. M5.2: 82 anomalies, 62 known;
  20 new in two shapes, minimised, confirmed twice, run at the baseline, and
  written up as F-001 and F-002. M5 done. M6: `REPORT.md` written, with the
  denominators (956 generated + 1 284 skipped = 2 240; at HUNT 270 refused +
  604 clean + 82 anomalies = 956), the recall table with DEF-106 added, the
  findings table and the coverage gaps. M6 done. M7 only if the author asks.
- 2026-09-26 (session 3, branch `claude/fervent-feynman-fhlm63`, a fresh cloud
  VM): M8. The toolchain was rebuilt by M0's commands; the baseline's products
  are byte-identical to sessions 1 and 2's. 8.1: HUNT2 is `9126350` (S20), and
  it carries 3g, 3h, 4b and 5c. 8.2: the recall suite matches "once fixed" in
  19/19 rows, and F-001 and F-002 are refused at HUNT2 with their controls as
  recorded. 8.3: DEF-108 is in HUNT2; the grid already leaves explicitly
  (0 `FLOW-001` in 1 000 programs), so the generator is unchanged, and the
  baseline re-run is identical in 956/956 cells. Committed before any hunting.
- 2026-09-26 (session 3, continued): 8.4: the grid at HUNT2 in 60.5 s, 562
  clean, 394 refused, 0 anomalies, every cell as its expectation. 8.5: 148
  cells moved from HUNT `6fb85d3`; 136 are the expected moves, none missing;
  12 changed refusal code (`TYPE-007` at the import places), bisected to 3h
  (S23): DEF-105's fix at work on the grid's own spelling. 8.6: nothing to
  take; no new finding. 8.7: `REPORT.md` §9 written, the M9 estimate above.
  M8 done; stopped for the author before M9.
- 2026-09-26 (session 4, branch `claude/focused-ride-3dfwa8`, a fresh cloud
  VM): M9.
  - **Setup.** M8 was fast-forwarded in first (S24). The toolchain was rebuilt
    by M0's commands, byte-identical to session 3's, and the M2 grid re-ran
    identical in 956/956 cells at both compilers.
  - **9.1.** The `heap:` line read at the baseline and in `nitpick-time`'s
    0.1.4b (`1cfd3f0`): it prints no live-at-exit figure. The leak observer is
    a 1 MiB probe after `run`, calibrated by controls.
  - **9.2.** A same-sized reuse sentinel, and read-now at the loop places.
  - **9.3–9.5.** `gen/grid9.py`, sections A–E: 7 571 cells, 28 519 skipped
    with reasons. Two shakedowns fixed four generator bugs before any result
    counted (S29).
  - **9.6.** Every known shape flagged at the baseline.
  - **9.7.** The baseline in 340 s: 840 anomalies, 618 known. HUNT2 in 325 s:
    197 anomalies, all candidates, in four families. Eight findings, F-003 to
    F-010, each minimised, confirmed twice at HUNT2, run at the baseline and
    written up. Two are memory faults at HUNT2: F-003, and F-004 (a gap in
    DEF-107's fix). `REPORT.md` §10 written.
  - M9 done; stopped for the author before M10.
- 2026-09-26 (session 5, branch `claude/peaceful-mccarthy-ohbxra`, a fresh cloud
  VM): M10.
  - **Setup.** The gate held (`origin/main` = `88e6355`, M9 ticked). The toolchain
    was rebuilt by M0's commands, byte-identical to sessions 3 and 4's. The M2 grid
    re-ran identical in 956/956 cells at both compilers, and the recall suite's 19
    old rows are identical, with its 6 new rows as `KNOWN_DEFECTS.md` says.
  - **10.1.** The checklist: 229 items (223 testable), each citing the reference
    sentence that states its answer. Committed with the programs and their
    expectations before any run (S36).
  - **10.2.** The 223 programs at both compilers, twice (25–26 s a run). HUNT2:
    212 agree, 11 disagree. The baseline: 210 and 13, its extra two known
    (DEF-101, DEF-98). Two programs were re-spelled between the runs, their
    expectations unchanged (S36).
  - **10.3.** DEF-108's shapes are flagged at the baseline and refused
    `FLOW-001` at HUNT2; the rule's exceptions are not over-refused.
  - **Triage.** Seven findings, each written small with controls, confirmed
    twice at HUNT2, and run at the baseline and at the compiler's newest `main`
    `9f6f370` (S37); all present at all three:
    - F-011, a `for` binding that outlives its loop in the emitter (a silent
      wrong value, and an out-of-bounds read with -O0 ≠ -O2);
    - F-012, `for` ranges running zero times at their type's edges;
    - F-013, counted loops sign-extending unsigned bounds;
    - F-014, `till` counting down for a negative limit;
    - F-015 and F-016, two `EMIT-002` refusals;
    - F-017, seven documentation findings.
  - **10.4.** `REPORT.md` §11, and the M11 estimate above. M10 done; stopped for
    the author before M11.
- 2026-09-26 (session 6, branch `claude/pensive-allen-pdhqpv`, a fresh cloud VM):
  M11, stopped part-way.
  - **Setup.** The gate held (`origin/main` = `626c22d`, M10 ticked). The toolchain
    and three compilers were rebuilt, byte-identical to sessions 3–5; the recall
    suite and M10's 223 programs re-ran identical.
  - **11.1–11.2, part.** The claim framework (`gen/m11lib.py`, `gen/m11.py`,
    `gen/m11_run.py`, `gen/m11_report.py`) and the brief. BUILTIN extracted (227
    claims) and run twice at HUNT2: 182 agree, 12 disagree, all old. Five other
    ranges drafted by sub-agents, unreviewed; nine not started.
  - **Stopped** on the author's word, the credit nearly spent (S46).
- 2026-09-26 (session 7, branch `local-m11`, the author's machine): M11 resumed on the
  workbench's brief.
  - **Setup.** The gate held (`origin/main` = `cbdec2e`, M10 ticked). LLVM 20.1.2 is
    the machine's own (S48). The compiler was cloned; HUNT2 `9126350`, the baseline and
    the newest `main` `1b4f0c6` were built (S49). The emissions are byte-identical to
    earlier sessions'; the canaries, the recall suite and M10's 223 programs re-ran
    identical.
  - **11.1, the drafts.** The five `_wip_` modules were reviewed (S51), renamed, and
    given their extracted ranges (S52). With BUILTIN: 1 488 claims (1 262 testable,
    226 untestable) over 3 704 of the references' 10 433 lines. `m11/` was written
    from the whole set and committed before any of the new programs ran.
  - **11.2, the runs.** Run 1 at HUNT2: 1 093 agree, 169 disagree. 38 programs were fixed
    for mistakes of their own (S53). The final run: 1 118 agree, 144 disagree. The
    agreeing refusals were screened (S55).
  - **Triage (S54).** The 144 were classed: 94 documentation, 16 lower-priority
    compiler, 10 extraction errors, 7 known, 6 silent wrong answers, 4 compiler traps,
    2 flag, 2 stricter than the text, 1 use after destroy, 1 invalid IR, 1 unit.
    All 144 give the same result at the baseline and at `1b4f0c6`.
  - **Findings.** F-018 … F-028, each confirmed on both legs, twice at HUNT2, and at
    the baseline and `1b4f0c6`: every one is old and still stands. `REPORT.md` §12 and
    `m11/RESULTS.md` written.
  - **Stopped** after the drafted modules, as the brief says (S56). M11 stays unticked:
    about 6 700 lines are not yet extracted.
- 2026-10-02 (session 8, branch `local-m11`, the author's machine): M11 resumed on the
  workbench's brief (S57).
  - **Setup.** Fast-forwarded to `41ba27b`. `.work/` was intact, and `93bcb66` was
    built for the findings. The machine checks are identical.
  - **MEMORY.** 181 claims, committed before any run. Run 1: 131 agree, 15 disagree.
    Seven programs fixed. Run 2: 137 agree, 9 disagree. Triaged: F-029 (lower-priority
    compiler), F-030 (8 documentation rows), 1 known (DEF-148).
  - **OP.** 159 claims, committed before any run. Run 1: 143 agree, 14 disagree. Five
    programs fixed over two runs. Final: 148 agree, 9 disagree. Triaged: F-031 (5
    documentation rows), 2 known (DEF-131, fixed at `93bcb66`), 2 not testable as
    written.
  - **CONTROL.** 110 claims, committed before any run. Run 1: 89 agree, 19 disagree.
    Nine programs fixed. Run 2: 98 agree, 10 disagree. Triaged: F-032 (6
    documentation rows), 4 known (DEF-133, DEF-130 twice, DEF-135).
  - **Stopped** with the brief's scope done; M11 stays unticked (about 5 400 lines left).
- 2026-10-02 (session 9, branch `local-m11`, the author's machine): M11 resumed on the
  workbench's next brief (S60), after session 8's handoff.
  - **Setup.** `local-m11` = `origin/main` = `6eb5392`. `.work/` was intact, and the
    machine checks were identical.
  - **MODULE.** 139 claims, committed before any run (`aba1fec`). Run 1: 92 agree, 32
    disagree. 24 programs fixed over two runs. Final: 109 agree, 15 disagree. Triaged:
    F-033 (7 documentation rows), F-034 (3 lower-priority compiler rows), 1 known
    (DEF-153), 2 not findings.
  - **LEXICAL.** 184 claims, committed before any run (`a967fbc`). Run 1: 167 agree, 14
    disagree. Four programs fixed. Final: 170 agree, 11 disagree. Triaged: F-035 (6
    documentation rows), F-036 (2 lower-priority compiler rows), 1 known (DEF-131).
  - **AST.** 202 claims, committed before any run (`c7bdff7`). Run 1: 150 agree, 31
    disagree. Two programs fixed. Final: 151 agree, 30 disagree. Triaged: **F-037, a use
    after free through a `=> dyn` cast**; F-038, an npkc trap; F-039 (4 lower-priority
    compiler rows); F-040 (20 documentation rows); 2 known.
