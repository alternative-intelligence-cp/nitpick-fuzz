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
- [x] **M11** — the reference, checked against the compiler: all fourteen references,
  10 419 lines, 3 385 claims, 2 872 tested, 2 587 agree, 285 disagree, every one triaged.
  - Session 6 stopped part-way on the author's word, the cloud credit nearly spent.
  - Session 7 (local, branch `local-m11`) reviewed, ran and triaged the drafted ranges:
    F-018 … F-028.
  - Session 8 (2026-10-02, on the workbench's brief from `nitpick-libs_12`, S57)
    extracted MEMORY, OP and CONTROL in turn, each to a clean point: F-029 … F-032. Its
    scope is done.
  - Session 9 (2026-10-02, the workbench's next brief, S60) extracts the ranges not
    started, smallest first. MODULE, LEXICAL, AST, BUILD, TRAITS and VERIFICATION
    1248–2351 are done, each to a clean point: F-033 … F-043, among them F-037, a use
    after free, and F-041, an npkc hang. BUILD's 38 and VERIFICATION 1248–2351's 16
    tested claims all agree. TYPE 661–2122 followed in three parts (S65):
    - F-044 (thirty-three documentation rows);
    - F-045 (a compiler message that advises the retired `?`);
    - F-046 (three safe departures);
    - **F-047, a silent wrong answer: a `fixed uint8[]` view written through**;
    - F-048 (a `NIL` field emitted as invalid IR).
  - Extracted: all 10 419 lines; 3 385 claims, 2 872 tested, 2 587 agree, 285 disagree.

  M11 is complete; "M11 — the state at the stop" below is its record, not a resume point.
  - [x] 11.1 every code example, normative claim and table row of the fourteen references at HUNT2 in `m11/CLAIMS.md`, with its file and line — all fourteen whole
  - [x] 11.2 a program per testable claim, its expected outcome from the text, committed before the first run; run at HUNT2 — the final run: 2 587 agree, 285 disagree, all triaged
  - [x] 11.3 `REPORT.md` §12; stop — §12 written; session 9 stopped there (2026-10-02)
- [x] **M12** — the re-baseline at HUNT3 `0c0f5a3`, the compiler's `main` after landing 113, under
  LLVM 20.1.8 (session 10, the Team seat; S66–S68). The boxes are the brief's sections, in the order
  they run: section 3 runs after section 4, whose corpus and comparers its control needs.
  - [x] 1 the start checks: GitHub fetched, `main` fast-forwarded (a no-op at `d44dfe3`), M11 ticked and merged, the tree clean, branch `local-m12` new (S69); the go quoted (S67)
  - [x] 2 HUNT3 named (`0c0f5a3`, carrying landings 112 and 113); the baseline and HUNT2 rebuilt byte-identical and commissioned under 20.1.2
  - [x] 4 the landing-103 spelling committed before any HUNT3 run; `compare.py --grid9` and `gen/compare_runs.py`; the shakedown identical at `c3bdae2` and `9126350`
  - [x] 3 LLVM 20.1.8 fetched; HUNT3 built and checked against its ladder row; the LLVM control at `9126350`
  - [x] 5 the runs at HUNT3 (recall, findings, M2, M9, M10, M11) and the comparisons with `9126350`
  - [x] 6 the move table, `results/0c0f5a3/MOVES12.md`
  - [x] 7 `KNOWN_DEFECTS.md` DEF-227 … DEF-251; FZ-1 … FZ-10; `NEWEST`
  - [x] 8 the gate; `REPORT.md` §13
- [x] **M13** — the initialisation and pointer-store grid, with the -O2 leg as the observer, at HUNT4
  `c72639f` (landing 137) under LLVM 20.1.8 (session 11, the Team seat; S76–S81). The boxes are the
  brief's sections §1–§11.
  - [x] 1 the start checks: GitHub fetched, `main` fast-forwarded `d44dfe3` → `581c091`, `f31dfc6` an ancestor, M12 ticked, the tree clean before the switch, `local-m13` new (S79); the go quoted as S77, covering (i) and (ii)
  - [x] 2 HUNT4 named (`c72639f`, landings 114–137; D-355 (ii) is 119) and built; its `npkc.ll` and `npkrt.o` equal notice 137's ladder row; both LLVMs as stated; the canaries pass at the baseline, HUNT3 and HUNT4
  - [x] 3 the housekeeping (1b): M12v's (1), (2), (4), (6), (7) and (8); DEF-256's row and F-049's two reported facts; DEF-236 (a) measured at HUNT4 (note (a)); no committed record changed but MOVES12's row 4 wording
  - [x] 4 learn by snippet, at HUNT4 and HUNT3: 130 + 51 probes and 89 template probes (S82, S89); the spellings and codes in the M13 section
  - [x] 5 `gen/grid13.py`, `gen/classify13.py` and `gen/compare13.py`, committed before any grid13 run: 933 cells, 431 skipped with reasons, `--selfcheck` passing; every expectation with its rule (S83–S88)
  - [x] 6 the seeds and the LLVM control at HUNT3, with HUNT3's record: the seeds 107/11, 107/99, 170/170 as `ACCEPTED:DEFECT:…` (P1); HUNT3's record 933 cells, its self-compare 0; the control under 20.1.2 moves 0 cells
  - [x] 7 grid13 at the baseline and at HUNT4 twice, and `FACES13.txt`: HUNT4's two runs agree (0 cells differ); 184 faces moved from HUNT3; 10 HUNT4 cells for triage
  - [x] 8 the regression leg at HUNT4 and `MOVES13.md`: recall 25/25; findings moved F-029 (136) and F-049 (132); M2 0; M9 24 (132); M10 0; zero UNEXPLAINED; P1–P11 ticked or explained
  - [x] 9 triage: F-050 (a soundness hole, DEF-252's array-element face), F-051 (the check of DEF-251 (i), scope wild), F-052 (crash / loud emission); C's six `OVERRESTRICT` a wrong expectation of mine (D-004 rule 3); each finding through the five steps with its control
  - [-] 10 (optional) the M11 re-spellings — not done: dispatch notes (a) and (c) keep `m11/` untouched (S91); closed unworked by S96 (M13v's finding (10)): the re-spellings stay with the fuzzer's manager for Option C
  - [x] 11 the gate holds in every box; `REPORT.md` §14; `KNOWN_DEFECTS.md`'s DEF-250, DEF-251 and DEF-252 rows from the seeds at HUNT4 (note (c)); the scratch removed
- [x] **M14** — the S-140 class (F-051 R1), a narrow run, at HUNT5 `249eae9` (landing 161) under LLVM 20.1.2
  (session 12, the Team seat; S92–S100). The boxes are the brief's sections §1–§8.
  - [x] 1 the start checks: GitHub fetched, `main` fast-forwarded `581c091` → `e289864`, `e289864` an ancestor, M13 ticked, the tree clean before the switch, `local-m14` new; the go quoted as S93
  - [x] 2 HUNT5 named (`249eae9`, carrying landing 155 and §27's S-140 sentence; landings 149–161 past 148) and built; its `npkc.ll`, `npkc.o` and `npkrt.o` equal notice 161's ladder row; `llvm-config` prints 20.1.2; the canaries pass at the baseline and HUNT5
  - [x] 3 the housekeeping: items 1–4 in (1b) (`3942f3f`: M13's box 10 `[-]`, M13v's (7), (8), (9)); items 5 and 6 with the triage (4): `KNOWN_DEFECTS.md`'s M13 block from HUNT5's registry, F-051's README section "S-140 (R1)"
  - [x] 4 learn by snippet, at HUNT5 and the baseline: the manager's 22 probes give their landing-148 verdicts at HUNT5; 25 grid14 templates, for spellings only, all compile at HUNT5, so no respelling and no skip (S97)
  - [x] 5 `gen/grid14.py` and `gen/classify14.py`, committed before any grid14 run: 109 cells (S 7, U 40, W 20, K 30, B 12), 0 skipped, `--selfcheck` passing with condition (c) literal on 43 flagged cells; `--selftest` 15 of 15 (S98, S99)
  - [x] 6 the runs: grid14 at HUNT5 twice (0 of 109 cells differ) and at the baseline; `--against13` exits 0 at both; F-050 … F-052 at HUNT5 twice and the baseline; the narrowness control's three parts reported with their counts
  - [x] 7 triage, through M5's five steps: B's ten 107/0 cells are one candidate, F-053 (a read `wild` `NULL` load sunk or deleted at -O2), reported apart as the check of §27 (D-364); no K, U or twin cell to triage (S100)
  - [x] 8 the gate holds in every box; `REPORT.md` §15, with a pointer in its opening; the scratch removed
- [x] **M15** — the DEF-296 family (a view of a pointer parameter's pointee stored through an indirection), a grid of
  the store roads and the freeing writes, at HUNT6 `1480ca8` (landing 163) with the regression leg REG155 `02856cf`
  (landing 155), under LLVM 20.1.2 (session 13, the Team seat; S101 onward). The boxes are the brief's sections §1–§8.
  - [x] 1 the start checks: GitHub fetched, `main` fast-forwarded `e289864` → `70a0d8b`, `70a0d8b` an ancestor, M14 ticked, the tree clean before the switch, `local-m15` new; the go quoted as S102, the release beside it (after a stop on a guard refusal and the dispatcher's ruling, in the Log)
  - [x] 2 HUNT6 named (`1480ca8`, landing 163, carrying 156; no landing past 163 at the fetch) and REG155 `02856cf` (landing 155), both built under 20.1.2; each one's `npkc.ll`, `npkc.o`, `npkrt.o` and `builder.o` equal its ladder row (notice 164's, notice 156's); `llvm-config` prints 20.1.2; the canaries pass at both
  - [x] 3 the housekeeping (1b): F-053's README number (13 → 12); `KNOWN_DEFECTS.md`'s DEF-296 family block, its rows read at HUNT6's registry (the cells column is box 7's); M14v's F3 and F5 notes
  - [x] 4 learn by snippet at HUNT6 and REG155: the expectations table copied and checked (104 rows, 0 mismatches); 96 probes, every hazard probe at its table row at both compilers, every twin clean; every grid15 cell one of the probed programs
  - [x] 5 `gen/grid15.py` and `gen/classify15.py`, committed before any grid15 run: 100 cells (S 16, R 64, W 20), 1 356 skipped of 1 440 combinations, `--selfcheck` passing; `--selftest` 18 of 18 (S105, S106)
  - [x] 6 the runs: grid15 at HUNT6 twice (0 of 100 cells differ) and at REG155; the recall gate exits 0, every check passing; 14 hazard cells `ACCEPTED:DEFECT:uaf` at HUNT6, the table's eight `H6/leak` keys
  - [x] 7 triage, through M5's five steps: the fourteen accepted cells are eight keys, each OPEN at HUNT6 (DEF-298, DEF-299, DEF-309, DEF-305's parameter-rooted gap), so known and not filed (S107); no regression; the family block's cell ids filled
  - [x] 8 the gate holds in every box; `REPORT.md` §16, with a pointer in its opening; the scratch removed

## Compilers

| role | commit | subject | `npkc.ll` bytes / sha256 | build time |
|---|---|---|---|---|
| baseline | `c3bdae2` (`c3bdae270d63c93ab6e89825fddeec9425e2c6fd`), 2026-09-25 07:06:41 -0400 | 1.5.8d steps 1-3: the close of cycle 1.5 | 28 111 929 / `4029fc70efbe9cd3…` | 67 s |
| hunt | `6fb85d3` (`6fb85d3d834fb7d5568ab996005f800d6d269e8f`), 2026-09-25 18:25:47 -0400 | 1.6.0 step 3f: DEF-99 — `NITPICK-TYPE-084` refuses the move out of `fixed` | 28 132 333 / `25eb7ee168604005…` | 69 s |
| HUNT2 (M8) | `9126350` (`9126350d11d12d20bbcc087dc261405bf2729f29`), 2026-09-26 03:42:01 -0400 | 1.6.1 step 0, the NIKOS half (D-324) — docs and `meta/roadmap/1.6/` tools over `2eea6f4` (1.6.1 step 0: DEF-107, `NITPICK-BORROW-015`) | 28 857 206 / `2448b3b60d9eb189…` | 75.8 s |
| newest `main` (M10, findings only; S37) | `9f6f370`, 2026-09-26 06:04:05 -0400 | 1.6.1 step 0c, the record of S-107's and S-108's approval — over `b564746` (1.6.1 step 0c: DEF-116, `NITPICK-TYPE-014`; DEF-117) | 28 872 365 / `7bab110a1e45cc9d…` | 88.9 s |
| HUNT3 (M12) | `0c0f5a3` (`0c0f5a39fcd2a54e78bf7409add841cbc16927b7`), 2026-10-15 12:00:05 -0400 | 1.6.1e, landing 113: DEF-235, DEF-236 (c)(d)(e), DEF-237 and DEF-234 (c), over landing 112 (`958890a`, DEF-232); built under LLVM 20.1.8 | 31 701 272 / `f520d5744b1e9951…` | 55.2 s |
| HUNT4 (M13) | `c72639f` (`c72639f2332208649309b91796d6f173d19a64d2`), 2026-10-19 15:08:30 -0400 | 1.6.1e, landing 137: DEF-267 (the awaited and the spawned qualified call), over landings 114–136; built under LLVM 20.1.8 | 32 424 412 / `2f1b9480701e1c86…` | 56.0 s |
| HUNT5 (M14) | `249eae9` (`249eae91559bfc1e3b8a17b12286c21108e4215a`), 2026-10-24 21:57:10 -0400 | 1.6.1e, landing 161: DEF-305 (a call-result pointer resolved by its return provenance), over landings 138–160; built under LLVM 20.1.2 | 33 418 659 / `59d16f1d2273e545…` | 64.9 s |
| HUNT6 (M15) | `1480ca8` (`1480ca81aa4d9d82976149f7f6ae5e44b2c5c640`), 2026-10-26 14:05:02 -0400 | 1.6.1e, landing 163: DEF-306 + DEF-308 (a spawn's lend, and a view of a pointee, compared against a write of the same storage reached by another name through a pointer), over landings 156–162; built under LLVM 20.1.2 | 33 468 275 / `fbd42f41e1ea4828…` | 64.8 s |
| REG155 (M15) | `02856cf` (`02856cfc72463f105da70bd9c23c7f2cc1bf8151`), 2026-10-23 09:34:46 -0400 | 1.6.1e, landing 155: DEF-288 and DEF-290 (a `for` binding is a block-scoped local to the escape and aliasing analyses); M15's regression leg, before DEF-296's fix at 156; built under LLVM 20.1.2 | 32 973 616 / `8f76731c6fc1c7ca…` | 66.0 s |

Other build products (M0.5):

| role | `npkc` bytes / sha256 | `npkrt.o` bytes / sha256 |
|---|---|---|
| baseline | 9 724 232 / `0cbc150ced5d20f7…` | 72 576 / `162b897539285a77…` |
| HUNT2 | 9 972 944 / `20d35e2822b99080…` | 72 576 / `162b897539285a77…` |
| hunt | 9 739 968 / `a81223d352d316be…` | 72 576 / `162b897539285a77…` |
| HUNT3 | 11 283 680 / `02e7b06321a16950…` (linked by the release `ld.lld` 20.1.8) | 72 656 / `c8e5033ad17c70f8…` |
| HUNT4 | 11 528 072 / `ba798aa0e5500a8d…` (linked by the release `ld.lld` 20.1.8) | 72 656 / `c8e5033ad17c70f8…` |
| HUNT5 | 11 957 184 / `2c8d898f101a3280…` (built under 20.1.2; the ladder row's is the same size) | 72 656 / `c8e5033ad17c70f8…` |
| HUNT6 | 11 970 864 / `7f7b2ab1b1d322dd…` (built under 20.1.2; the ladder row's is the same size) | 72 656 / `c8e5033ad17c70f8…` |
| REG155 | 11 843 192 / `32dcfb0b084c60b5…` (built under 20.1.2; the ladder row's is the same size) | 72 656 / `c8e5033ad17c70f8…` |

**Commissioning check (M0.5): PASSED.** The baseline's `.internal/quickemit/npkc.ll`
is exactly 28 111 929 bytes with sha256 `4029fc70efbe9cd3…`, as GitHub's CI
printed. The emission is identical on this machine.

**LLVM:** **20.1.2 for every `c3bdae2` and `9126350` record**, and for `6fb85d3`'s, `9f6f370`'s,
`1b4f0c6`'s and `93bcb66`'s: the `LLVM-20.1.2-Linux-X64` release tarball in sessions 1–6 (PLAN.md
0.2, S13), the machine's `/usr/lib/llvm-20` from session 7 on (S48), `llvm-config --version`
printing `20.1.2` either way. **20.1.8 for HUNT3** (`0c0f5a3`, M12), on the author's go (S67): the
`LLVM-20.1.8-Linux-X64` release tarball, 2 021 269 412 bytes, sha256
`1ead36b3dfcb774b57be530df42bec70ab2d239fbce9889447c7a29a4ddc1ae6`, fetched in S13's form; its
`llvm-config --version` prints `20.1.8`. **20.1.2 for HUNT5** (`249eae9`, M14) and for every M14 record,
PLAN.md:10's own pin, which needs no go (S95). **20.1.2 for HUNT6** (`1480ca8`) **and REG155** (`02856cf`), M15, and
for every M15 record, the same pin (S104).

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

### M11 — the state at the stop

*The last clean point is session 9's TYPE 1593–2122, part C of TYPE 661–2122 (S65), which
completes M11: every reference extracted, run, triaged, committed, pushed. Session 8 did MEMORY, OP and CONTROL the same way (S57). M11 is ticked (line 44).*

**Done, committed and measured.**
- Extracted: BUILTIN, CONCURRENCY, IO, MACRO, MEMORY, OP, CONTROL, MODULE, LEXICAL, AST,
  BUILD, TRAITS, VERIFICATION and TYPE whole. That is all 10 419 of the references'
  10 419 lines (S58 corrected the count).
- **3 385 claims, 2 872 testable, 513 untestable** with reasons (`m11/CLAIMS.md`).
- The final run at HUNT2 (`results/9126350/m11.jsonl`): **2 587 agree, 285 disagree**.
- Every disagreement is triaged (`gen/m11_triage.py`) and run at the baseline and at
  its session's newest `main`: `1b4f0c6` for session 7's, `93bcb66` for sessions 8's
  and 9's.

Written up in `m11/RESULTS.md`, `REPORT.md` §12 and findings F-018 … F-048:
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
  - F-039: five lower-priority compiler rows;
  - F-040: eighteen documentation rows (two classes corrected at BUILD's clean point);
- TRAITS' are:
  - F-041: **npkc does not terminate** on an unbounded generic instantiation;
  - F-042: one lower-priority compiler row;
  - F-043: thirteen documentation rows.
- TYPE 661–2122's (in three parts, S65):
  - F-044: thirty-three documentation rows;
  - F-045: a compiler message that advises the retired `?`;
  - F-046: three safe departures;
  - F-047: **a silent wrong answer**, a `fixed uint8[]` view written through;
  - F-048: a `NIL` struct field emitted as invalid IR.

**Not started:** nothing. M11 is done. PLAN.md: "After M11, if the credit remains, the
author and the workbench choose the next task together."

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
   and extend `REPORT.md` §12. Findings number on from F-049.

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
  - F-039: 5 lower-priority compiler rows:
    - a `comptime` value parameter is EMIT-002;
    - `<|` takes its function on the right, as `|>` does;
    - a non-constant `joins` is accepted;
    - any attribute name is accepted;
    - an `opaque struct` is accepted outside an extern block;
  - F-040: 18 documentation rows;
  - 1 not a finding: `as0365` tested a free function named after an inherent method's
    LOWERED name (TRAITS:132).
  - Two corrections were made at BUILD's clean point, while reading TRAITS, and are
    recorded there: `as0043` moved from F-040 to F-039 e, and `as0365` from F-040 to
    not a finding.
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
- **Run 1:** 37 agree, 1 disagree.
  - `bd0529` was a script that took the first line of the output for the error. The note
    at the declaration comes first, and the script now looks for both lines anywhere.
  - The stage scripts were re-spelled once (run 2), and the re-spelling was withdrawn
    before run 3. `explore`'s script had agreed because the runner refused its bogus
    `kind`, so I suspected the runner refused a `kind` before checking the stage. A probe
    showed the opposite: an unknown stage with a `kind` is refused for the stage. So the
    first spelling was sound.
  - What run 2 did measure: `npkg`'s refusal of an unknown stage lists "compile, parse,
    resolve, check, accept, fixture, program, runtime, verify, cost". It leaves out
    `explore`, which it accepts (`npkg/manifest.npk:41`) and the compiler's own
    `nitpick.toml` uses (:224). The list in the message is stale. No claim disagrees
    for it.
- **Run 3:** 38 agree, 0 disagree. The final full run of all 2 197 claims: 1 969 agree,
  228 disagree. The 2 159 earlier claims re-ran identical.
- **The screen.** Every BUILD script's last line was read; each refusal is the claim's own
  (the toolchain pin, `edition`, the lock, `update`, the `[[test]]` schema).

**TRAITS (all 766 lines), `gen/m11_claims/traits.py`.** The week read 89% before it.
- **The extraction.** 119 claims (19 examples, 16 rows, 84 rules); 115 testable, 4
  untestable (3 `vague`, 1 `internal`). No M10 item tests a TRAITS sentence. Committed
  before any of its programs ran.
  - Every example is tested as written, around declarations it needs. Several use
    spellings other references retired: a `buffer` return with `pass result;`,
    `assoc:Error`, `flt64(…)` as a cast, `Mutex` and `Handle` as type names, a lent
    `T` passed out, `item.render();` as a bare statement, a lambda. The run says
    which still stand.
- **Run 1:** 96 agree, 19 disagree.
- **The fixes** (12 programs, over two runs):
  - A generic struct literal takes no type arguments: it is `Box{ … }` with the type on
    the binding, as the compiler's own programs write it. This affected 10 programs.
    Three of them (`tr0461`, `tr0513`, `tr0586`) had agreed in run 1 for that
    PARSE-002 (S55).
  - `pub` on a struct field does not parse (`tr0364`).
  - An impl's generic method was refused for its signature (`tr0686`). Both had agreed
    in run 2 for those reasons, and were re-spelled.
- **Runs 2 and 3:** 100, then 99 agree.
  - Run 3 took `tr0586`'s record from run 2, since its program had not changed. That
    saved a 120 s timeout.
  - The final full run of all 2 312 claims: 2 068 agree, 244 disagree. The 2 197 earlier
    claims re-ran identical.
- **Triage of the 16**, each run at the baseline and `93bcb66`:
  - **F-041, npkc does not terminate** on an unbounded generic instantiation (`tr0586`).
    Measured by hand at three compilers: no exit in 300 s, 4.4 GB resident (`timeout
    300` under `ulimit -v 8000000`). TRAITS:586 caps the depth at 64 with a compile
    error.
  - F-042: `opaque` accepted outside an extern block (`tr0368`), as F-039 e;
  - F-043: 13 documentation rows;
  - 1 not a finding (`tr0350`): the sentence says a blanket impl does not apply to
    itself, not that it is refused.

  All stand at `93bcb66`. At the baseline, `tr0404` (the lent `T`) and `tr0435`
  (`struct:Mutex`) compiled.
- **The screen.** TRAITS' agreeing refusals were screened after each run (S55). Five had
  agreed for a reason of their own and were re-spelled; each now agrees or disagrees for
  the claim's reason.

**VERIFICATION 1248–2351, `gen/m11_claims/verif3.py`.** The week read 90% before it.
- **The extraction.** 131 claims (2 examples, 49 rows, 80 rules); 16 testable, 115
  untestable: 87 `tool`, 13 `z3`, 12 `tree`, 2 `vague`, 1 `internal`. The range is §8
  (the SMT elimination manifest), §9 (the floor's obligations: the spec grammar, the
  kernel boundary and its 30-row effect table, the rows and verdicts, the protocol
  models, the floor's stack) and §10 (the schedule explorer). Nearly all of it is the
  verified build's runners, the floor's translator, the models and the explorer, which
  need z3 or `npkg`'s full ladder (verif2's reasons, copied). Committed before any of its
  programs ran.
  - The tested claims are what the compiler emits: `npkc --obligations` scripts
    (verif2's scaffolding, copied) and `ir:` tests of the trap spellings (`@npk_trap(i32
    -4110)`, `-4099`, `-4119`; a program's raise `@npk_raise`).
- **Run 1:** 16 agree, 0 disagree. Each agreeing refusal or script was read; each is the
  claim's own reason (BORROW-013 for a static overlap; the rows' role, encoded, tier and
  clause-context fields; hashes unmoved by blank lines). The final full run of all 2 328
  claims: 2 084 agree, 244 disagree. The 2 312 earlier claims re-ran identical. No finding.

**TYPE 661–1176, `gen/m11_claims/type2.py`** (part A of TYPE 661–2122, S65). The workbench
held the session at VERIFICATION's clean point, then relayed the author's go for TYPE, to
land at a clean point by 95 % of the week. The week read 90 % before it.
- **The extraction.** 268 claims (10 examples, 68 rows, 190 rules); 249 testable, 16 of
  them M10's programs; 19 untestable: 5 `z3`, 4 `internal`, 4 `vague`, 3 `unobservable`,
  2 `tree`, 1 `tool`. The range is §6 (tbb), §7 (the ternary and nonary kinds), §8 (the
  flag families, one claim per member row) and §9 (structs with `sealed`/`hidden` and
  `limit<Rules>` fields, fixed arrays, slices, tagged and generic enums). Committed before
  any of its programs ran.
  - Where the text says a cast "traps" and names no trap, the program's `failsafe` sends
    every trap to 42 (`fs_any`), and the claim expects `run:42`.
  - Every refusal of a `sealed`, `hidden` or `limit` rule expects the code the text names
    (TYPE-079, -080, -081, -059, -063, -077), so a program refused for a spelling of its own
    cannot agree.
  - Reasoned while extracting, not measured: TYPE:805's two spellings `42` and `1T1T0t` are
    not one value (balanced `1T1T0` is 81 − 27 + 9 − 3 = 60). The claim expects what the
    text says.
- **Run 1:** 237 agree, 12 disagree. Every agreeing refusal's first diagnostic was read:
  one, `ty0855`, agreed for a reason of its own (the prelude's `Whence` has no `SEEK_SET`;
  its variants are `Start`, `Current`, `End`). Four programs fixed with `refix()`:
  - `ty0786`: its own nyte product, 1000 × 30, was past the bound;
  - `ty0803b`: `raw f(x).m()` parses as `raw (f(x).m())`;
  - `ty0854` and `ty0855`: the variant names.
- **Run 2** (the four): 4 agree. `ty0855` is now refused for the claim's reason (`Whence`
  has no bitwise operations).
- **Triage.** Nine disagree, and each gives the same result at the baseline and `93bcb66`:
  - **F-044**, eight documentation rows:
    - §6's tbb128/tbb256 alignment 8 (they align to 16, as §5 itself says);
    - the failsafe signature;
    - `42` and `1T1T0t`;
    - `struct MyStruct`;
    - the field-access IR;
    - "never up" for a slice;
    - `#wild_slice`'s retired wild-context phrase;
  - one not a finding: `ty1084`'s regex demanded `\b` after `}`.
  - **`ty1107` was run down by hand, for a memory fault.** A slice parameter passed back
    up is accepted. A slice of the frame's own local is BORROW-001. A view laundered
    through such a function and stored past its storage is BORROW-002. So no view outlives
    its storage. The registry's S-107 controls describe the same reading.
- **The final full run**, all 2 577 programs: 2 324 agree, 253 disagree. The 2 328 earlier
  programs re-ran identical.

**TYPE 1177–1592, `gen/m11_claims/type3.py`** (part B, S65). The week read 90 % before it.
- **The extraction.** 129 claims (9 examples, 37 rows, 83 rules); 123 testable, 10 of
  them M10's programs; 6 untestable: 3 `internal`, 2 `vague`, 1 `unobservable`.
  - The range is §10 (pointers, pointer indexing and TYPE-082), §11 (Optional and
    Result: the rows of both tables, the unwrap operators and their shorthands, the
    struck spellings), §12 (Handle and arena layouts), §13 (the six atomic operations'
    IR, scoped to `main`), §14 (SIMD: rows, limits, any-lane traps, reductions, the
    obligation rows), §15 (the library vector types, by a script that loads the
    compiler's own `lib/nvec.npk` and `lib/ntensor.npk`), §16 (function types), §17
    (Future) and §18 (`dyn` sizes and bound order).
  - Its scaffolding is shared with part C through `gen/m11_tyhelp.py`, which is not a
    claims module. `type2.py` keeps its own copy, as committed.
  - Committed before any of its programs ran (`2e9f871`, with the files `gen/m11.py`
    writes).
- **Run 1:** 114 agree, 9 disagree. Every agreeing refusal's first diagnostic was read,
  and each is the claim's own reason.
  - One reads `ty1375`'s refusal (TYPE-007, `??` on a Result) as advising "`?` is the one
    that unwraps a `Result`". The compiler itself refuses that spelling (PARSE-011, D-175).
    This is F-045, measured with a control at three compilers.
- **Runs 2 and 3:** `ty1507` and `ty1508`'s scripts did not name the two errors
  `lib/ntensor.npk` declares (REACH-002). Fixed in two steps. Then they build, run, and
  report sizes other than the table's.
- **Triage.** Nine disagree, and each gives the same result at the baseline and `93bcb66`.
  All nine are F-044 rows:
  - `--guard-pages`, which no tool has;
  - the bare `?`, twice;
  - the extern example (EXTERN-001);
  - the arena's `alloc(N) => arena<T>->` (TYPE-009);
  - §15's `vec3`, `matrix` and `tensor` layouts (32, 40 and 104 bytes, measured);
  - the elided-Result IR.
- **The final full run**, all 2 700 programs: 2 438 agree, 262 disagree. The 2 577 earlier
  programs re-ran identical.

**TYPE 1593–2122, `gen/m11_claims/type4.py`** (part C, S65). The week read 91 % before it.
TYPE is one reference, so its last part is not a new reference. The landing line the
author set for TYPE is 95 % (the workbench's go).
- **The extraction.** 178 claims (9 examples, 58 rows, 111 rules); 172 testable, 7 of them
  M10's programs; 6 untestable: 3 `tool`, 1 `internal`, 1 `unobservable`, 1 `vague`. One
  table is excluded: the implementation-priority table, a plan by cycle.
  - The range is:
    - §19 (dimensional types);
    - §20 (frac: rows, the five invariants, ERR, casts, `ToString`);
    - §21 (complex);
    - §22 (`binary` removed);
    - §23 (`buffer`);
    - §25 (the library tier, by scripts over the compiler's `lib/`);
    - §26 (`fixed`);
    - §27 (NIL, NULL, `void`, `any`, auto-dereference, `unknown`);
    - §28 (every row of the operator tables, as IR or as behaviour).
  - `lib_run` gained failsafe arms for a library's own errors, defaulting to none, so part
    B's scripts are unchanged (regenerated identical).
  - Committed before any of its programs ran (`a66247f`, with the files `gen/m11.py`
    writes).
- **Run 1:** 147 agree, 25 disagree. Every agreeing refusal's first diagnostic was read.
  - Two agreed for a reason of their own: `ty1989` and `ty2007` hit `@x =>! any->`, which
    parses as `@(x =>! any->)`.
  - Four programs were fixed: those two, `ty1987` (the same spelling), and `ty1607` (an
    inline unit `Meters/Seconds` does not parse; the prelude names `MetersPerSecond`).
- **Run 2** (the four): 4 agree, each for the claim's reason.
- **Triage.** 23 disagree. All give the same result at the baseline, and all but two at
  `93bcb66`. The 23 are:
  - **F-047, a silent wrong answer.** A `fixed uint8[]` is the reference's immutable byte
    view (TYPE:1719, D-074), yet a write through it lands, a callee's through a `fixed`
    parameter included. Measured with two controls at three compilers. The class is
    reasoned: a reading where `fixed` fixes only the view would make it a documentation
    row.
  - **F-048:** a `NIL` struct field is accepted and emitted as `{ i32, void }`, which
    `llc` and `opt` refuse.
  - **F-046,** three lower-priority rows:
    - a frac member assignment passes the checker and is EMIT-002;
    - a `fixed` parameter is reassigned;
    - the backward pipe, F-039 b's shape.
  - **F-026's shape on `int32`:** `int32<Meters>` is accepted. It is refused at
    `93bcb66`, and so is F-026's own `tfp64<Meters>` (`ty0553`, re-run there).
  - **DEF-131's `<=>`,** which compiles at `93bcb66`.
  - **Sixteen F-044 rows.** One is frac's `ToString`: −(1 3/8) renders "-2 5/8", the
    reference's own example, which a reader of mixed numbers takes for −2.625. It was
    measured at three compilers and is flagged for the author.
- **The final full run**, all 2 872 programs: 2 587 agree, 285 disagree. The 2 700 earlier
  programs re-ran identical.

## M12 — the re-baseline at HUNT3 (session 10, the Team seat)

**The start checks** (the brief's section 1; PLAN.md's start rules (a)–(d)).
- **The remote.** `git remote get-url origin` is GitHub's (this clone's remote is SSH), so no
  `set-url`; `git fetch origin` at 16:42 EDT.
- **The gate.** `git switch main && git merge --ff-only origin/main` was a no-op: `main` =
  `origin/main` = `d44dfe3`. `git merge-base --is-ancestor d44dfe3 origin/main` exits 0. M11 is
  ticked (line 44) and there were no M12 boxes. "M11 stays unticked" in M11's state note is FZ-3's
  wording defect, fixed with section 7.
- **Clean tree.** `git status --porcelain` printed nothing.
- **The branch.** There was no `origin/local-m12` and no local one, so `git switch -c local-m12
  --no-track origin/main` (S69). No upstream is set.
- **(a)** `uname -a`, `nproc`, `free -g`, `df -h .` and `python3 --version` are under Environment
  below. **(b)** `CLAUDE.md` was re-read, the silent-wrong-answer rule with it: an accepted program
  whose result differs from the reference's, with no memory error, is a defect. **(c)** `.work/` was
  absent, so the compilers were rebuilt by M0's commands (below). **(d)** M12 starts at its first box.
- **The go** is S67, quoted verbatim. It covers LLVM 20.1.8, and HUNT3 as "after 113 lands" (S68).

**HUNT3** (section 2; S68). The compiler was cloned from GitHub to `.work/nitpick` at 16:43 EDT
(3.9 s). Its `origin/main` is `0c0f5a3` (`0c0f5a39fcd2a54e78bf7409add841cbc16927b7`, 2026-10-15
12:00:05 -0400, "1.6.1e, landing 113: DEF-235, DEF-236 (c)(d)(e), DEF-237 AND DEF-234 (c)"). The
brief's four confirmations:
- `meta/NOTICES.md` has a `| 113 |` row (its line 174; the sha cell reads "—");
- the registry has DEF-235 (`OPEN_DECISIONS.md:3937`), DEF-237 (`:3980`) and DEF-236 (c)(d)(e)
  (`:3957`) FIXED at landing 113, and DEF-234 (c) with them (`:3922`);
- `git merge-base --is-ancestor 0c0f5a3 origin/main` exits 0: it is `origin/main`;
- the go names it, as "after 113 lands" (S67).

The landings past 111 it carries: **112** (`958890a`, DEF-232, this repository's F-048) and **113**.
Not 114 or 115: DEF-250 (`:4159`) and DEF-251 (`:4175`) are OPEN in HUNT3's registry. Landing 113's
commit also registers DEF-252 (a view re-seated by a callee outlives its string: a use after free in
safe code) and DEF-253 (a `Self->` trait method through a bound does not link), both OPEN.

**HUNT3's ladder row.** HUNT3's NOTICES rows 112 and 113 and its 1.6.1e record carry no digests.
The workbench's BOARD (`nitpick-libs`, "THE BASELINE NOTICE 114 MUST QUOTE", notice 113's rows "at
`0c0f5a3`") transcribes them: `npkc.ll` 31 701 272 B `f520d5744b1e9951…`, `npkrt.o` 72 656 B
`c8e5033ad17c70f8…`, `npkc` 11 283 608 B `bd85ba7a09d6b963…`. Section 3 checks HUNT3 against that row
(S68).

**The baseline and HUNT2** (section 2), built one at a time by M0.5's command under LLVM 20.1.2
(`.work/llvm-20.1.2`, S70), each under the Team seat's harness lock:

| compiler | build | `npkc.ll` bytes / sha256 | `npkrt.o` | `npkc` |
|---|---|---|---|---|
| `c3bdae2` | 74.6 s | 28 111 929 / `4029fc70efbe9cd3…` | 72 576 / `162b897539285a77…` | 9 724 160 / `5fd636b9ab557c19…` |
| `9126350` | 72.7 s | 28 857 206 / `2448b3b60d9eb189…` | 72 576 / `162b897539285a77…` | 9 972 872 / `c7212b6be06fe6a4…` |

All six are byte-identical to the committed digests (`npkc` in its Ubuntu-lld form, session 7's), so
the commissioning check passes again. Canaries (PLAN 0.6) at both: `canary.npk` gives npkc 0 and runs
0/0; `canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` and writes no `.ll`.

**The landing-103 spelling** (section 4; S71). From landing 103 `string_bytes` returns `fixed
uint8[]`, and a `fixed` view never converts back to a plain `uint8[]`: that is `TYPE-007` (D-351,
DEF-246). So every binding of its result into a plain `uint8[]` becomes `fixed uint8[]`:
- **three generator lines:** `gen/grid.py`'s and `gen/grid9.py`'s `obs_s` (`uint8[]:bs =
  string_bytes(v);`), changed together (S27), and `gen/m10.py`'s `t07_bytes_view_bounds`
  (`uint8[]:b = string_bytes(s);`);
- **the hand-written programs,** found by the brief's anchored grep over `known/` and `findings/`:
  48 files (5 in `known/`, 43 in `findings/`, among them F-004's five with two sites each), 53 lines,
  re-spelled by its `sed` and by nothing else;
- `python3 gen/m10.py` regenerated `t07`'s program and nothing else in `m10/`.

The anchored grep over every `.npk` now lists only six files, `m11/programs/{bi0105, bi0241, me0208,
me0217, me0221, me0228}.npk`, generated from `gen/m11_claims/`. They are left for Option C, as the
brief says: at HUNT3 they are refused `TYPE-007`, a move explained by landing 103 (D-351), and their
expectations never change (S45). Regenerated, the grids are unchanged in size: `gen/grid.py` 956
cells (1 284 skipped), `gen/grid9.py` 7 571 (28 519 skipped), and `gen/grid9.py --selfcheck` prints
"956 of 956 M2 programs byte-identical".

**The two comparers** (section 4, written before the shakedown, which needs them; S72, S73).
- `gen/compare.py --grid9 OLD/ NEW/` compares two widened-grid records, `cells9.jsonl` and
  `classified9.jsonl`, and writes `MOVES9.md` in the new directory. The move key is (npkc rc, codes,
  -O0, -O2, `heap_O0`, `heap_O2`). No M2 rule applies: every moved cell is listed, grouped by place,
  operation, both classes and verdicts, with a column naming what moved. Tested in scratch: the
  committed `9126350` record against a copy of itself gives "7571 cells, 0 moved", and one planted
  `allocated` word gives 1 moved, `heap_O0:a`.
- Without `--grid9`, `compare.py` is unchanged: on copies of the `c3bdae2` and `9126350` records,
  the committed script and the new one write byte-identical `MOVES.md` and print the same lines.
- `gen/compare_runs.py OLD.jsonl NEW.jsonl` compares two M10 or M11 records by `id`, on npkc, codes,
  O0, O2, `sh`, verdict, kind and the heap words; a field absent from both is equal. It lists every
  changed id and every id on one side only, prints the totals and writes nothing. The committed
  `9126350` records against themselves: "223 ids, 0 changed" and "2872 ids, 0 changed"; M10 at
  `c3bdae2` against `9126350`: 10 changed, DEF-108's and the block string's, as recorded.

**The shakedown** (section 4): under LLVM 20.1.2, into `.work/shake/`, with nothing committed as a
result. Its gate is cell-for-cell identity with the committed records, and **it holds everywhere**:
- the grid statistics, regenerated through a scratch directory, are byte-identical to
  `results/GRID.md` (956 generated, 1 284 skipped) and `results/GRID9.md` (7 571, 28 519);
- the runs, each from a fresh directory and each `run.py` from "0 already done":

| record | `c3bdae2` | `9126350` |
|---|---|---|
| M2 grid, `cells.jsonl` (`compare.py`) | 956 cells, 0 moved (68.5 s) | 956 cells, 0 moved (62.6 s) |
| M9 grid, `cells9.jsonl`, heap words included (`compare.py --grid9`) | 7 571 cells, 0 moved (509.5 s) | 7 571 cells, 0 moved (484.1 s) |
| recall, `known-m10.txt` (`diff`) | 25 of 25 lines identical (7.5 s) | 25 of 25 (5.1 s) |
| M10, `m10.jsonl` (`compare_runs.py`) | 223 ids, 0 changed (17.4 s): 210 agree, 13 disagree | 223 ids, 0 changed (18.2 s): 212 agree, 11 disagree |

  At `c3bdae2`, `compare.py`'s MISSING count is 136: M8's rules read against the old compiler, as
  the brief expects, and not the gate.
- **the findings shakedown**, once: the ten findings that hold a re-spelled file, HUNT `9126350`
  twice and the baseline once (`run_findings.py … --name VERDICTS-shake.txt`, the seven with heap
  words under `--heap`; 21.2 s and 32.5 s). Every line but the timestamp equals the committed record
  (`VERDICTS-9126350.txt` for F-001 and F-002, `VERDICTS.txt` for the other eight): all ten print
  `same`, and the HUNT runs agree in each.

**The prediction held: identical.** The spelling is neutral at both compilers, so no per-compiler
spelling was needed. The scratch was then removed: `.work/shake` and every `VERDICTS-shake.txt`.

**LLVM 20.1.8** (section 3, run after section 4; S67's go). A header request first showed the asset
exists (HTTP 200, 2 021 269 412 bytes). The tarball was then fetched in S13's form: `curl -C -` to a
file in a bounded retry loop (one attempt, 56 s), `xz -t`, and `tar -xJ --strip-components=1` into
`.work/llvm-20.1.8` (328 s in all). `llvm-config --version` prints exactly `20.1.8`, and `llc` and
`opt` print "LLVM version 20.1.8". The tarball is 2 021 269 412 bytes, sha256
`1ead36b3dfcb774b57be530df42bec70ab2d239fbce9889447c7a29a4ddc1ae6`; no reference digest for it is
recorded anywhere. The machine's apt.llvm.org prefix was not used (S67).

**HUNT3, built** by M0.5's command under `.work/llvm-20.1.8` and the lock, in 55.2 s:

| product | HUNT3 `0c0f5a3` | the ladder row (notice 113's, S68) | |
|---|---|---|---|
| `npkc.ll` | 31 701 272 / `f520d5744b1e9951…` | 31 701 272 / `f520d5744b1e9951…` | equal |
| `npkrt.o` | 72 656 / `c8e5033ad17c70f8…` | 72 656 / `c8e5033ad17c70f8…` | equal |
| `npkc` | 11 283 680 / `02e7b06321a16950…` | 11 283 608 / `bd85ba7a09d6b963…` | 72 bytes longer |

The emission and the runtime object equal the ladder row. The linked `npkc`'s `.comment` reads
`Linker: LLD 20.1.8 (https://github.com/llvm/llvm-project 87f0227c…)`. *Reasoned, not measured:*
the ladder's `npkc` was linked by apt.llvm.org's `ld.lld`, whose comment is shorter. 72 bytes is the
difference the release `ld.lld` made at 20.1.2 too (sessions 1–6's `npkc` against session 7's, S48).
Canaries at HUNT3 under 20.1.8: `canary.npk` gives npkc 0 and runs 0/0; `canary_malformed.npk` gives
npkc 1 with `NITPICK-PARSE-001` and writes no `.ll`.

**The LLVM control** (section 3): `9126350` re-run under 20.1.8 into `.work/control/`, with the
re-spelled corpus and section 4's comparers, against its committed records, which were measured
under 20.1.2. **Identical in every record:**

| record | `9126350` under 20.1.8 |
|---|---|
| recall, `known-m10.txt` | 25 of 25 lines identical (4.6 s) |
| M2 grid | 956 cells, 0 moved (55.8 s, from "0 already done") |
| M9 grid, heap words included | 7 571 cells, 0 moved (429.5 s, from "0 already done") |
| M10 | 223 ids, 0 changed (17.1 s): 212 agree, 11 disagree |
| M11 | 2 872 ids, 0 changed (342.9 s): 2 587 agree, 285 disagree |

- **P32 at `9126350`: no BUILD claim moved**, so the dispatch's allowance for the pin refusal (S66
  (a)) was not needed. 23 shell scripts carry a `[toolchain]` section (`/usr/bin/grep -l
  '\[toolchain\]' m11/programs/*.sh | wc -l`, run in M13's housekeeping), and under 20.1.8 each gives
  the verdict it gave under 20.1.2. Two of them, `bd0075` and `bd0299`, reach npkg's toolchain check by
  design: their committed output at `9126350` is its refusal ("… is 20.1.2 but nitpick.toml pins …").
  `bd0299`, whose claim is that a 20.1.1 pin is refused, now reads "ld.lld is 20.1.8 but nitpick.toml
  pins 20.1.1", which shows the scripts ran with 20.1.8 on `PATH`. *(Corrected in M13's housekeeping,
  M12v's finding (1): this bullet said "21 BUILD scripts", and that each stops before the check.)*
- So **0 cells moved by the toolchain**, in every record, and every move at HUNT3 is the compiler's.
  The question for the author, whether 20.1.8 stands for the fuzzer, does not arise. The scratch was
  removed (`rm -rf .work/control`).

**The runs at HUNT3** (section 5): every runner under `--llvm .work/llvm-20.1.8`, one at a time under
the lock, into `results/0c0f5a3/` and each finding's `VERDICTS-0c0f5a3.txt` (S21).
`git ls-files results/0c0f5a3` printed nothing before the first.

| run | at HUNT3 `0c0f5a3` | against `9126350` | time |
|---|---|---|---|
| recall, `known-m12.txt` | 25 rows; `check_known_fixed.py` prints 19 `match` and no MISMATCH or MISSING; its 6 gaps are DEF-106's and DEF-108's rows, each its "once fixed" verdict by hand (`TYPE-086` twice, `FLOW-001` twice, both controls 0/0) | identical to `known-m10.txt`, 25 of 25 | 4.9 s |
| findings, `VERDICTS-0c0f5a3.txt` (HUNT3 twice, the baseline once) | 48 findings, 156 programs; the two HUNT3 runs agree for every program; F-003 … F-010 re-run with `--heap` | 67 programs moved, in 29 findings; every baseline line equals the committed one | 247.1 s, then 29.7 s |
| M2 grid, `cells.jsonl` | 956: 562 clean, 394 refused, 0 anomalies | 956 cells, 0 moved (`MOVES.md`) | 58.4 s |
| M9 grid, `cells9.jsonl` | 7 571: 4 047 clean, 3 524 refused, **0 anomalies** (HUNT2: 197) | 393 moved (`MOVES9.md`) | 465.7 s |
| M10, `m10.jsonl` | 223: 218 agree, 5 disagree | 9 changed (`m10-changes.txt`) | 17.4 s |
| M11, `m11.jsonl` | 2 872: 2 628 agree, 244 disagree | 95 changed (`m11-changes.txt`) | 323.2 s |
| M11, HUNT2's 285 disagreements, `m11-disagree.jsonl` | 62 agree, 223 disagree, each as in the full run | — | 22.8 s |

- **No memory fault at HUNT3.** No HUNT3 line of any finding exits 70, 95, 107 or 139 (312 lines);
  neither grid has a `DEFECT` class; no M11 claim has a leg mismatch or reads the poison, and the 14
  that exit 70 or 95 each expect that trap and agree. Every memory finding (F-001 … F-008, F-011,
  F-022, F-037, F-047) gives its fixed verdict.
- **Fifteen header-only records.** `run_findings.py` run over every finding writes a
  `VERDICTS-0c0f5a3.txt` for the fifteen row findings too (F-027, F-028, F-030 … F-036, F-039,
  F-040, F-042 … F-044, F-046), whose programs are M11's claim programs, measured in `m11.jsonl`.
  Their files hold the header and no program; they are kept as the brief's command wrote them.
- **F-025** has no `run_findings.py` record of its own: its committed `VERDICTS.txt` is `run.sh`'s, at
  `9126350` twice. Its `run.sh` at HUNT3, twice: `plain: npkc=0   no-wildx: npkc=0, 0 x WILDX-003`
  both times, so the flag accepts the program; at the baseline once: `no-wildx: npkc=1, 256 x
  WILDX-003`, as recorded at `9126350`. Its canary's new line (0/0 at all three runs) has no
  committed counterpart.
- **Probes for the move table**, one lock each, with `gen/snip.py --show-msg`: F-041's `h1` is
  `TYPE-018` in 0.09 s at HUNT3; F-024's `c1` is `PARSE-001` "expected a type" at its `$$i` receiver
  (8:26); F-045's `d1` stays `TYPE-007`, its advice now naming `?!`/`?|` (D-175) where `9126350`'s
  named `?`.

**A candidate: F-049** (section 9; S74). Of the M9 grid's 393 moved cells, 24 SAFE cells are newly
refused `MOVE-001`: `pick_own × loop_move` (16) and the read-after and reuse-sentinel cells of
`pick_own × swap` (8). A consuming pick's binding, moved and then re-assigned, cannot be read; its
`local` twins run clean. Taken through PLAN 5.2:
- **(a)** Neither KNOWN_DEFECTS (DEF-118 is the opposite fault; DEF-124, F-009, is this shape at a
  `move` parameter, its fix reaching parameters only) nor HUNT3's registry has it. **Bisected**
  (S23): the 32 `pick_own × {loop_move, swap}` cells and their 98 `local` twins were run at landing
  73 `bbb1530` and landing 74 `40deffa`, built in `.work/bisect/` under 20.1.2 (55.8 s, 56.9 s;
  canaries pass): all run at 73, and the 24 are refused at 74, 1.6.1d step 1 (DEF-118). New at 74.
- **(b)** Written small by hand in F-009's form, from its helpers: the re-initialised read, the loop
  form, the local control, and a control moved and not re-assigned.
- **(c)** HUNT3 twice, both legs: the two reproducers and the moved-not-reassigned control refused
  `MOVE-001`, the local control 0/22/22.
- **(d)** The baseline, HUNT2 and landing 73: the reproducers 0/22/22 (the right answer); the
  moved-not-reassigned control 0/21/21, DEF-118's shape.
- **(e)** `findings/F-049-pick-binding-reinit-refused/` (README, four programs, `VERDICTS.txt` at
  HUNT3, `VERDICTS-9126350.txt`). Lower priority, an over-restriction; a regression against HUNT2.
  The bisection's worktrees and runs were then removed (`.work/bisect`).

**The move table** (section 6): `results/0c0f5a3/MOVES12.md`, 97 rows over the six runs and the LLVM
control. **Every move carries a landing number or a finding id; zero UNEXPLAINED.**
- Recall 0 of 25 and M2 0 of 956 moved. Findings: 67 programs in 29 findings, plus F-025's `run.sh`
  and F-045's message, each its registry fix (74 … 113). M9: 393 cells in ten groups, among them the
  60 `OwnedFd` cells whose `to_cstring` buffers are now freed (78) and F-049's 24 (74, bisected). M10:
  9 programs. M11: 95 claims, 62 to AGREE, 21 to DISAGREE, 4 changed inside DISAGREE and 8 inside
  AGREE.
- Evidence (i), the registry or notice text at HUNT3 naming the program or its shape, for every row
  but F-049's, whose evidence is (ii), the bisection.
- **New disagreements at HUNT3, each a recorded change:** the six `uint8[]` bindings (103), `mc0388`
  (106), `me0119`/`me0119b`, `as0572` and `md0042` (113), six BUILD scripts (71: `[toolchain]` now
  requires a `triple` pin), `c25`/`ty0190` and `vf0983`/`vf1149` (88, 91: a long `flt32` literal now
  compiles to the nearest float), `ty0322` (78: `cstring` is 24 bytes), `ty1635` (97: D-347's
  invariants) and `ty1669` (83: `flt64` is no literal suffix). Expectations unchanged (S45).
- **Two reference rows still contradict HUNT3**, for the author and the compiler seat: TYPE_REFERENCE:1858
  at HUNT3 spells `complex(3.0flt64, 4.0flt64)`, which HUNT3 refuses `LEX-009`; and
  AST_REFERENCE:578's node comment still lists `#[align(16)]` and `#[cfg(...)]`, while the paragraph
  under it says `#[derive]` is the one attribute (DERIVE-007 since 113).
- **`as0572`** (dispatch note (g)), through PLAN 5.2: the move is 113's (DEF-236 (d)). At `9126350`
  and `c3bdae2` the attribute was a silent no-op, measured: `#size_of<Aligned>()` is 8 with
  `#[align(16i32)]` and 8 without, at both. No reference sentence at HUNT2 gave `#[align]` a result
  (AST_REFERENCE §6 shows it as syntax; DECISIONS says types "will lower onto it"), so the acceptance
  was F-039 (d)'s shape, an attribute the language does not have accepted and ignored, which DEF-236
  (d) fixes; not a silent wrong answer against a stated result.
- **Predicted moves:** 29 of 33 ticked. P1 and P2 split (4 cells each went to a refusal, F-008's fix
  and F-049), P17's F-024 is `PARSE-001` where the brief said `MACRO-010` (DEF-150's record says so),
  and P32's pin refusal never arose (landing 71's `triple` rule comes first); each is explained in
  the table.

**The registry rows, FZ-1 … FZ-10 and `NEWEST`** (section 7). None of FZ-1 … FZ-10 was on GitHub's
`main` (`d44dfe3`) already.
- **KNOWN_DEFECTS.md** gains "M11 sessions 8 and 9's findings (F-029 … F-048), and the registry's
  DEF-227 … DEF-253" (FZ-8), from DR §2's draft: every status read at HUNT3, every fixed row
  measured there, with DEF-190, DEF-252 and DEF-253 (registered at 113), and F-049 named as
  unregistered. Every DEF-118 … DEF-154 bullet carries its landing and its HUNT3 measurement
  (DEF-126 at 1.6.1d step 4 and DEF-134 at step 1, landings 79 and 74, which those NOTICES rows
  name); the header's "expectations until M1.3 measures them" gives way to the measurements; and the
  F-001/F-002 note is under "Closed as faces of known defects".
- **FZ-1**: the M11 section's lead and DEF-154's bullet (OPEN).
- **FZ-2**: F-044's frac row reclassified, and `ty1657`'s `wrong:` line in `gen/m11_claims/type4.py`;
  `python3 gen/m11.py` changed only `m11/programs/ty1657.npk`. **The counting is the author's**:
  33 → 32 in F-044's README, its `ROWS.md`, `m11/RESULTS.md:309`, REPORT §12.2 and the PROGRESS counts.
- **FZ-3**: the M11 "resume" and "unticked" wording, three places. **FZ-4**: F-039's rows, five.
- **FZ-5**: REPORT §12's baseline sentence names three, `cc0042`, `tr0404` and `tr0435`.
- **FZ-6**: F-030's title, eight. Its third line already counts eight rows and DEF-148's one, so it
  was left.
- **FZ-7**: F-039 (b) and F-046 (c) reclassified as documentation rows (titles and notes); F-031's
  correction note in its README and, through `gen/m11_rows.py`'s new `NOTES` (S75), in its `ROWS.md`;
  REPORT §12.2's lower-priority counts 5 → 4 and 3 → 2, documentation + 2, the total 285 unchanged.
- **FZ-9**: README's "five places" is "four". **`PLAN.md:16` and `README.md:25`** ("the five known
  defects") are the author's.
- **FZ-10**: `gen/m11_rows.py`'s docstring, and the line-number note in REPORT §12.1 and
  `gen/m11_report.py`'s intro; `m11/RESULTS.md` regenerated, its diff that note only (4 lines).
- **`NEWEST`** is `("0c0f5a3", "93bcb66", "1b4f0c6")`. `python3 gen/m11_rows.py` rewrote 15 `ROWS.md`
  files: every newest column is `0c0f5a3`, and of their 224 rows the 27 that do not read "same" are
  exactly the claims that moved at HUNT3.

**The gate** (section 8), at the commit that ticks M12:
- [x] The start checks passed: GitHub fetched, `main` fast-forwarded (a no-op at `d44dfe3`), `d44dfe3`
  an ancestor, M11 ticked, the tree clean, `local-m12` new; the go quoted as S67.
- [x] The baseline's and HUNT2's products byte-identical to the committed digests (`npkc` in its
  Ubuntu-lld form); the canaries pass at all three compilers, and at landings 73 and 74.
- [x] HUNT3's digests recorded against notice 113's ladder row: `npkc.ll` and `npkrt.o` equal to it;
  `npkc` 72 bytes longer, its linker comment (reasoned).
- [x] The re-spelling committed (`daad233`) before HUNT3 was built or run; the anchored grep lists only
  the 6 `m11/` files; identity at `c3bdae2` and `9126350` in M2, M9 with heap words, recall, M10 and
  the ten findings.
- [x] The LLVM control at `9126350` under 20.1.8 identical in every record; S66 (a)'s allowance unused.
- [x] Recall 25/25 at the baseline as committed (the shakedown); at HUNT3 19/19 by the script, 6/6 by
  hand.
- [x] Every finding whose registry row is FIXED gives its fixed verdict at HUNT3, and every control its
  recorded answer but one, listed with its cause: F-020's `ctl_j3`, 10/10 under D-334.
- [x] Every finding's new baseline line equals its committed one. F-025's committed record is
  `run.sh`'s at `9126350` only; its `run.sh` at the baseline gives what `9126350` recorded.
- [x] Every moved cell and claim carries a landing number or a finding id (`MOVES12.md`); zero
  UNEXPLAINED; every prediction ticked (29) or explained (4).
- [x] `KNOWN_DEFECTS.md` carries DEF-227 … DEF-251, with DEF-190, DEF-252 and DEF-253, with landing
  numbers, and the F-001/F-002 note.
- [x] FZ-1 … FZ-10 applied, FZ-2's counting and `PLAN.md:16`/`README.md:25` listed for the author;
  `NEWEST` rebased.
- [x] REPORT §13's denominators add up: M2 956 = 562 + 394; M9 7 571 = 4 047 + 3 524; M10 223 = 218 + 5;
  M11 2 872 = 2 628 + 244; the 285 = 62 + 223; in every run, moved = explained.
- [x] No committed record of `c3bdae2` or `9126350` changed. The brief's form, `git diff --stat origin/main --
  results/c3bdae2 results/9126350 results/GRID.md results/GRID9.md 'findings/*/VERDICTS.txt'
  'findings/*/VERDICTS-9126350.txt'`, did not print nothing, as the brief's box asked: it lists F-049's two new
  files, added, which match its pathspec. The `--diff-filter=MDR` form prints nothing, so no existing record
  changed, and the box is ticked on that form (worded so in M13, M12v's finding (4)). The scratch is gone: no `.work/shake`, `.work/control` or
  `.work/bisect`, and no `VERDICTS-shake.txt`, `VERDICTS-scratch.txt` or `VERDICTS-bisect.txt`.

## M13 — the initialisation and pointer-store grid (session 11, the Team seat)

**The start checks** (the brief's §1; PLAN.md's start rules (a)–(d)).
- **The remote.** `git remote get-url origin` is GitHub's, over SSH, so no `set-url`. `git fetch origin`
  at 04:10 EDT moved `origin/main` from `d44dfe3` to `581c091` (dispatch note (b)).
- **Clean tree, before any switch.** On `local-m12` at `f31dfc6`, `git status --porcelain` printed
  nothing, and there was no stash.
- **The fast-forward.** `git switch main && git merge --ff-only origin/main` took `main` from `d44dfe3`
  to `581c091`. `581c091` changes only `CLAUDE.md` and `README.md` from `f31dfc6`.
- **The gate.** `git merge-base --is-ancestor f31dfc6 origin/main` exits 0; M12 is ticked; there were
  no M13 boxes.
- **The branch.** There was no `origin/local-m13` and no local one, so `git switch -c local-m13
  --no-track origin/main` at `581c091` (S79). No upstream is set.
- **The go** is S77, quoted verbatim. It names (i) HUNT4 as the compiler's `origin/main` at this fetch
  and (ii) LLVM 20.1.8 for HUNT3 and HUNT4.
- **(a)** `uname -a`, `nproc`, `free -g`, `df -h .` and `python3 --version` are under Environment
  below. **(b)** `CLAUDE.md`'s defect definition was re-read: an accepted program whose result differs
  from the reference's, with no memory error, is a defect. **(c)** Only HUNT4 needed building:
  `.work/` holds M12's compiler clone, its base, hunt2 and hunt3 worktrees, and both LLVM trees.
  **(d)** M13 starts at its first box.

**The LLVM trees** (§2). `.work/llvm-20.1.8/bin/llvm-config --version` prints `20.1.8`, and
`.work/llvm-20.1.2/bin/llvm-config --version` prints `20.1.2` (the symlink to `/usr/lib/llvm-20`, S48,
S70). The 20.1.8 tarball's sha256 is `1ead36b3…`, as recorded under Compilers, so nothing was fetched
again. `cells/INDEX.jsonl` has 956 lines and `cells9/INDEX.jsonl` 7 571, as M12 left them.

**HUNT4** (§2; S78). `git -C .work/nitpick fetch origin` at 04:11 EDT moved the compiler's `origin/main`
from `0c0f5a3` to `c72639f` (`c72639f2332208649309b91796d6f173d19a64d2`, 2026-10-19 15:08:30 -0400,
"1.6.1e, landing 137: DEF-267 …"), written to `.work/H4.full` and `.work/H4`. It is not HUNT3, and its
`meta/NOTICES.md` has a `| 114 |` row. It is 24 commits past HUNT3, one per landing, so it carries
**landings 114 to 137**, each with its NOTICES row:
- 114 `2f0937a` DEF-250: a module binding with no initialiser, `TYPE-055` at the declaration;
- 115 `7992c77` DEF-251 (i): LLVM's `null_pointer_is_valid` on every emitted `define`;
- 116 `2f50640` DEF-252: a view re-seated by a callee, `BORROW-002` at the destination argument; DEF-256
  registered (F-049);
- 117 `76a8102` D-353 / DEF-236 (a): a `comptime` value parameter, `TYPE-095` at its declaration;
- 118 `c9baa9e` DEF-253 and DEF-254: a `Self->` trait method through a bound;
- 119 `34979dc` D-355, S-136's option (c): `NULL` leaves the plain pointer, `TYPE-096` at the literal;
- 120 `0156326` D-360: `??!`, the Optional's unwrap-or-trap;
- 121 `f9a9428` D-361 and the `#ptr_add` confinement: a value of wild provenance enters a plain pointer
  slot only through `=>! T->`, `TYPE-097` at the value;
- 122 `29e93a9` D-357: a `comptime func:` exists at compile time only (`TYPE-098`);
- 123 `284402d` D-356: a payload-less enum variant is a constant outside the enum;
- 124 `ccf7f95` D-359: the orphan rule;
- 125 `2b95bb4` DEF-234 (a) and (b);
- 126 `e709f77` DEF-242: the site table holds the sites the emission holds;
- 127 `1670427` D-339 / DEF-181: the lock walk's six holes;
- 128 `463cf93` D-341: a `buffer` is indexed and ranged like a slice of bytes;
- 129 `17d26ad` DEF-244: the source manager keys a file by its identity;
- 130 `c1e20e8` DEF-245 and DEF-260: a declaration whose header fails is one report;
- 131 `b1a23b8` DEF-255: the qualified trait call through a bound and a pointer receiver;
- 132 `6f0f518` DEF-256 (F-049): a consuming `pick`'s binding re-assigned after a move is live again;
- 133 `c230073` DEF-257 and D-362: a `pick` does not select on a pointer (`TYPE-065`);
- 134 `a73b68d` DEF-178 and DEF-187: a `pick`'s value pattern is a constant of the selector's type;
- 135 `0280fc9` DEF-190 and DEF-182: a numeral's digit run ends in a digit;
- 136 `19d674b` DEF-258, DEF-259 and DEF-261: a keyword is never a parameter's name, and a local
  `T:keyword` is `PARSE-001` at the name;
- 137 `c72639f` DEF-267: the awaited and the spawned qualified call reach, as their dotted twins do.

**D-355 (ii) has landed**, as landing 119: `NULL` where a plain pointer or an Optional is expected is
`NITPICK-TYPE-096` at the literal, and keeps its meaning only in a `wild` context. §4 measures the code by
name.

**HUNT4, built** by the brief's command under `.work/llvm-20.1.8` and the lock, in 56.0 s (04:12–04:13
EDT). Its log's `npkg/main.npk: exit 2` line is in HUNT3's build log too.

| product | HUNT4 `c72639f` | notice 137's ladder row | |
|---|---|---|---|
| `npkc.ll` | 32 424 412 / `2f1b9480701e1c86…` | 32 424 412 / `2f1b9480701e1c86…` | equal |
| `npkrt.o` | 72 656 / `c8e5033ad17c70f8…` | 72 656 / `c8e5033ad17c70f8…` | equal (HUNT3's too) |
| `npkc.o` | 13 339 504 / `8299668097e438b3…` | 13 339 504 / `8299668097e438b3…` | equal |
| `builder.o` | 12 067 840 / `5870b02dcf97950c…` | 12 067 840 / `5870b02dcf97950c…` | equal |
| `npkc` | 11 528 072 / `ba798aa0e5500a8d…` | 11 528 000 / `e258d3249e2c5f7e…` | 72 bytes longer |
| `builder` | 10 402 608 / `ff0489d70fc58347…` | 10 402 536 / `b4dff7b33b187ce0…` | 72 bytes longer |

The ladder row is the workbench BOARD's "THE BASELINE NOTICE 138 MUST QUOTE" (notice 137's rows "at
`c72639f`"; the Workspace copy at `93627bb`). The emission, the runtime object and both unlinked objects
equal it. The two linked binaries are each 72 bytes longer, and `npkc`'s `.comment` reads `Linker: LLD
20.1.8 (https://github.com/llvm/llvm-project 87f0227c…)`. *Reasoned, not measured:* that is the release
`ld.lld`'s longer comment, the 72 bytes M12 found for HUNT3's `npkc` (S68).

**The baseline and HUNT3** are M12's builds, unchanged: their `npkc.ll`, `npkrt.o` and `npkc` give the
committed sizes and sha256 (`4029fc70…`, `162b8975…`, `5fd636b9…`; `f520d574…`, `c8e5033a…`, `02e7b063…`),
and both worktrees are clean.

**Canaries** (M0.6), one batch under the lock: at the baseline (20.1.2), HUNT3 and HUNT4 (20.1.8),
`canary.npk` gives npkc 0 and runs 0/0, and `canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001`
and writes no `.ll`.

**The housekeeping (1b)** (§3): M12v's non-blocking findings, DEF-256 and dispatch note (a), each a
wording edit or a note. No committed record changed except `results/0c0f5a3/MOVES12.md`'s row 4, the
wording edit the brief names.
- **(1)** The P32 bullet above and REPORT §13.3: "21 scripts" is replaced by my grep's count, 23 with a
  `[toolchain]` section (`/usr/bin/grep -l '\[toolchain\]' m11/programs/*.sh | wc -l`; 22 of them have an
  `llvm =` line and 20 pin `"20.1.2"`). `bd0075` and `bd0299` are named as reaching npkg's toolchain check by
  design: their committed output at `9126350` is its refusal.
- **(2)** MOVES12 row 4 and DEF-119's bullet: `view_claim_i_to_freeing_callee`'s `BORROW-013` is DEF-123's
  code, and `view_addr_to_freeing_callee`'s `BORROW-015` DEF-119's; both landed at 74 (F-004's
  `VERDICTS-0c0f5a3.txt`; OD:2532 and OD:2586 at HUNT3).
- **(4)** M12's box 13 now says which form it was ticked on: the brief's `--stat` form lists F-049's two new
  files, and the `--diff-filter=MDR` form prints nothing.
- **(6)** DEF-247 and DEF-249: no program of ours, each with its search. DEF-247: `git grep -nE
  'func:[A-Za-z_0-9]+ *= *(fixed|stack) ' -- '*.npk'`, and the same over `cells/` and `cells9/`, find none.
  DEF-249: `git grep -nE '\bexit +(raw +)?[A-Za-z_][A-Za-z_0-9.]*\(' -- '*.npk'` finds one `exit` of a call,
  `cc0264`'s `exit c.load() - 1i32;`, an `atomic<int32>` load that cannot fail; the cells have none.
- **(7)** The fifteen header-only `VERDICTS-0c0f5a3.txt` files are kept as records. REPORT §13.4 gains one
  erratum line, and `gen/run_findings.py` writes no file for a finding with no programs. Checked on F-027
  with `--name VERDICTS-scratch.txt`: it prints "0 programs, no file written" and writes nothing.
- **(8)** REPORT §13.6: "No anomaly is left by the classifier's classes".
- **DEF-256:** its row in KNOWN_DEFECTS.md, from the registry at HUNT4 (registered at 116, fixed at 132,
  `6f0f518`). F-049's README gains the two facts the brief names, each labelled as reported, not measured
  here: the registration with its cause in `assign_assign`, and `nitpick-fuzz_2`'s reproduction.
- **Note (a):** DEF-236's bullet. (a) is fixed at 117, measured by one compile of `m11/programs/as0062.npk` (a
  copy in scratch; `m11/` untouched) under the lock: at HUNT4 npkc 1, `NITPICK-TYPE-095 as0062.npk:10:12`
  ("`K` is a `comptime` value parameter, a form the language reserves and has not designed (D-353)"), at
  line 10's `func:scale<comptime int32:K> = …`; at HUNT3 npkc 1, `NITPICK-EMIT-002` at 10:71, as note (a)
  says.

**Learn by snippet** (§4; S82). Three batches of probes in `.work/probes13/`, each compiled and run at
HUNT4 and HUNT3 under 20.1.8 by `gen/snip.py`'s recipe, one batch per lock: 130 probes, one per axis
value (04:30); 51 for the spellings the templates need (04:40); 89 copies of generated templates, for
spellings only (04:46, S89). None is committed. What they settle, by code at HUNT4 / HUNT3:
- **Module bindings (A).** `int64:x;` and every other binding that is neither `fixed` nor a constant
  initialiser of `fixed` (`pub`, `stack`, `wild`, `wildx`, a struct, `int64[4]`, `atomic<int64>`,
  `Channel<int64, 1i32, 4i64>`, `bool`, `uint8`, `int32`) is `TYPE-055` at the declaration at HUNT4 (114);
  at HUNT3 the bare forms compile, and a write faults at -O0 and reads back zero at -O2 (107/12, 107/13),
  a read gives the zero default (13/13), an atomic store faults on both legs (107/107), and a channel
  `send` reports `ChannelClosed` (102/102). With an initialiser the binding is `TYPE-055` at both.
  `fixed T:g = c;` reads its constant (0/0 at both), `fixed stack`, `fixed wild … = NULL` and `fixed wildx
  … = NULL` too. A write to a `fixed` binding is `ASSIGN-002`, a compound assignment too; a field or
  element write `TYPE-086`; `@g` of a `fixed` binding `TYPE-071` (D-287) at both compilers, into a writer
  or a reader alike, so **P4's suspect is refused at HUNT3 already**. `const` is no keyword:
  `const int64:X = 5i64;` is `PARSE-001` "expected `:`, found `int64`" at both (TYPE_REFERENCE §26). No
  constant of type `atomic<int64>` exists for a module initialiser (`TYPE-007`), nor of a channel
  (`channel()` is `TYPE-035`).
- **Pointers (B).** `NULL` in a plain slot (a local, a `fixed` local, a module `fixed T->`, a struct field,
  a parameter's argument, a `pass`, and `p == NULL` itself) is `TYPE-096` at the literal at HUNT4 (119);
  at HUNT3 each store through it gives 107/99, DEF-251's face. A `wild` store or load through `NULL` is
  107/107 at HUNT4 (115) and 107/99 at HUNT3, through a `wild` parameter too (note (d): no `TYPE-097`);
  a `wild` value into a plain parameter is `TYPE-097` at HUNT4 (121). **A dead `wild` load followed by a
  `NULL` test is 107/14 at HUNT4 and at HUNT3**: the -O2 leg deletes the load and takes the null branch.
  `T->?` exists: `NIL`, `!= NIL`, `?? @d` and `?.` run 0/0; `<-p`, `p.a` and a `T->?` passed to a plain
  parameter are `TYPE-007`; `p ??! Unreachable` traps 95/95 at HUNT4 and is `TYPE-007` at HUNT3 (`??!`
  is landing 120's).
- **Locals (C).** Every read before definite assignment is `ASSIGN-001` at both, whatever the type
  (`int64`, `int32`, `bool`, a struct, an array, `string`, `T->`, `T?`) and whatever the path (one `if`
  branch, a loop that may run zero times, one `pick` arm, `@x` to a reader, by value, `x = x + 1`, a
  helper's local, a loop body's); a field write into an unassigned struct is `ASSIGN-001` too; a struct
  literal missing a field is `TYPE-027`. The definitely-assigned twins run 0/0.
- **Operators (D)**, M10's measured rows at both: a known shift amount outside the range is `TYPE-070`; a
  constant `/ 0`, `% 0`, `MIN / -1`, `MIN % -1` is `TYPE-004`; a constant `-MIN` is `TYPE-076`; at run
  time 111, 97, 98 and 93 on both legs; an unsigned negation is `TYPE-008`; the twins run 0/0. A
  `uint64` literal above 2⁶³−1 is `LEX-004`, so the top bit is built as `9223372036854775807u64 + 1u64`.
- **The trap identities.** HUNT4's prelude declares 31 (`pub error:`), the same 31 names as HUNT3's and
  HUNT2's: `gen/m10.py`'s twenty TRAPS and eleven more, which S44 already coded for M11 (100–105,
  118–122). None is new, so no code is added (S83). A failsafe naming all 31 compiles at both.
- **DEF-252's shape (E).** The direct store is `BORROW-002` at both; a callee storing the view whole,
  into a field, two levels down or through a method is `BORROW-002` at HUNT4 (116) and reads the poison
  at HUNT3 (170/170; 25/25 with a reuse sentinel). A callee returning a holder assigned outside is
  `BORROW-002` at both. **A callee storing into an element of an array of holders through a pointer
  compiles at HUNT4 and reads the poison, 170/170 (25/25 with a sentinel)**, a face 116 does not reach.
  Each outlives twin runs 0/0.
- **One more probe result**, outside grid13's axes: `p.store(7i64)` and `p.load()` through an
  `atomic<int64>->` parameter are `NITPICK-EMIT-002` ("the emitter could not lower this, although the
  frontend accepted it") at both compilers (`q_a09`). It goes to triage (§9).

**The grid** (§5; S83–S88): `gen/grid13.py` (936 lines), `gen/classify13.py`, `gen/compare13.py`.
`python3 gen/grid13.py --out cells13` generates **933 cells** and skips 431 combinations, each with its
reason in `cells13/SKIPPED.txt`; 1 364 combinations in all, the three seeds among them: the axes give 1 361
(930 generated + 431 skipped), and with the 3 seeds 930 + 3 = 933 generated, 933 + 431 = 1 364 (measured from
`gen/grid13.py`'s `enumerate_space()` and `build()` in M14; this line said "1 364 combinations in all, plus the
three seeds" until M14 (1b), counting the seeds twice: M13v's finding (8)):

| section | generated | REFUSE | SAFE | TRAP | skipped |
|---|---|---|---|---|---|
| S, the seeds | 3 | 3 | 0 | 0 | 0 |
| A, module bindings (11 types × 5 declarations × 9 operations) | 166 | 157 | 9 | 0 | 329 (99 `const`) |
| B, `NULL` and pointer stores (8 places × 8 operations × 2 types) | 106 | 87 | 8 | 11 | 22 |
| C, definite assignment (8 types × 5 places × 7 operations, each with its twin) | 500 | 250 | 250 | 0 | 60 |
| D, constants at the edge (5 types × 15 operations × 2 forms) | 130 | 37 | 56 | 37 | 20 |
| E, stores into a pointee (7 stores × 2 lifetimes × 2 observers) | 28 | 14 | 14 | 0 | 0 |
| **all** | **933** | **548** | **337** | **48** | **431** |

29 cells carry `"scope": "wild"`. The expected codes: `ASSIGN-001` 200, `TYPE-055` 129, `TYPE-096` 79,
`TYPE-027` 50, `TYPE-070` 18, `TYPE-004` 16, `BORROW-002` 15, `TYPE-071` 14, `ASSIGN-002` 13, `TYPE-007`
9, `TYPE-076` 3, `TYPE-086` 2; the TRAP exits 111 ×18, 97 ×10, 107 ×9, 98 ×6, 93 ×3, 95 ×2.
`python3 gen/grid13.py --selfcheck` prints "selfcheck: 933 cells (A 166, B 106, C 500, D 130, E 28, S 3),
431 skipped, 1364 combinations; every check passes": two builds identical; ids are module names equal
to their `mod:` lines; every meta has `run.py`'s keys, its rule and its source; every REFUSE cell names
a code, every TRAP exit is a failsafe arm; the layout (helpers before `main`, `failsafe` directly after
it, grid13's failsafe) and D-013 (`exit` only in `main` and `failsafe`) hold in every cell; TRAPS equals
`gen/m10.py`'s and the 31 arms `gen/m11lib.py`'s; the seeds' embedded text and their sources give the
recorded sha256; generated + skipped = the combinations; and `cells13/` is this build byte for byte.
`cells13/` is gitignored (`.gitignore` gains the line).

**The classifier and the comparer, tested before any run** on synthetic records in scratch: a record
meeting every expectation classes as 548 `refused` and 385 `clean`; 23 planted cases each give the class
the brief names (the seeds' 107/11, 107/99 and 170/170 as `ACCEPTED:DEFECT:leg_mismatch`, `…:fallthrough`
and `…:uaf`; `ACCEPTED:clean`; `OVERRESTRICT`; `REFUSED_TRAP`; `CRASH:npkc` for an exit 3 and a compile
timeout; `timeout`; `LOUD`; `DEFECT:fallthrough`; a TRAP 107 cell at 107/107 `clean`; 107/14
`DEFECT:leg_mismatch`; a TRAP cell at 0/0 `DEFECT:wrong_value`; `DEFECT:segv`, `false_trap` (a TRAP cell
raising another identity, and a SAFE cell at 93/93), `double_free`, `uaf` for 25, and `other` for 102 and
an unbuilt leg); a refusal missing its code reads `exp_mismatch` "codes". `compare13.py` lists 0 and
exits 0 on a file against itself, lists three planted differences (a class move, a code move, a
`MISSING:new`) with their class pairs and exits 1; `classify13.py` exits 1 without the index.

**The recall gate and the LLVM control at HUNT3** (§6), each run under the lock at 4 jobs:
- **The seeds at HUNT3** (`.work/ctl13/seeds-h3/`, 04:50): `bare_binding` npkc 0, 107/11,
  `ACCEPTED:DEFECT:leg_mismatch`; `null_store` npkc 0, 107/99, `ACCEPTED:DEFECT:fallthrough`;
  `probe08h_view_reseated` npkc 0, 170/170, `ACCEPTED:DEFECT:uaf`. **Each is flagged as §6 names it
  (P1 holds)**: the instrument sees the class.
- **HUNT3's record under 20.1.8** (`results/0c0f5a3/cells13.jsonl`, 57 s): 933 cells. The self-compare
  of `classified13.jsonl` lists 0 cells and exits 0.

| class at HUNT3 | S | A | B | C | D | E | all |
|---|---|---|---|---|---|---|---|
| refused | | 75 | 9 | 250 | 37 | 4 | 375 |
| clean | | 9 | 8 | 244 | 93 | 14 | 368 |
| `ACCEPTED:DEFECT:leg_mismatch` | 1 | 44 | 17 | | | | 62 |
| `ACCEPTED:DEFECT:fallthrough` | 1 | | 37 | | | | 38 |
| `ACCEPTED:DEFECT:wrong_value` | | 34 | | | | | 34 |
| `ACCEPTED:clean` | | | 24 | | | | 24 |
| `ACCEPTED:DEFECT:uaf` | 1 | | | | | 10 | 11 |
| `ACCEPTED:DEFECT:segv` | | 2 | | | | | 2 |
| `ACCEPTED:other` | | 2 | | | | | 2 |
| `DEFECT:fallthrough` (scope wild) | | | 6 | | | | 6 |
| `DEFECT:leg_mismatch` (scope wild) | | | 3 | | | | 3 |
| `OVERRESTRICT` | | | | 6 | | | 6 |
| `REFUSED_TRAP` | | | 2 | | | | 2 |
| **generated** | **3** | **166** | **106** | **500** | **130** | **28** | **933** |

  HUNT3 is the class before 114 and 115, not the hunt: its faces are tabulated against HUNT4 in REPORT
  §14.7 (FACES13). The `REFUSED_TRAP` pair is `??!`, which HUNT3 does not have (landing 120). The six
  `OVERRESTRICT` are C's pointer twins at the literal and array places (an `@z` stored in a branch, a loop
  or an arm); triage reads them at HUNT4.
- **The LLVM control: HUNT3 under 20.1.2** (`.work/ctl13/h3-20.1.2/`, 64 s): `compare13.py` against the
  record lists **0 cells** and exits 0. No cell of grid13 moves between 20.1.2 and 20.1.8 at HUNT3 (P11:
  none differ), so the control finds no undefined behaviour that the two versions fold apart. It cannot see
  undefined behaviour both versions fold alike, which is why -O0 against -O2 stays the observer.

**The runs** (§7), one at a time under the lock, at 4 jobs:
- **The baseline** `c3bdae2` under 20.1.2 (`results/c3bdae2/cells13.jsonl`, 53 s): 933 cells.
- **HUNT4, run 1** (`results/c72639f/cells13.jsonl`, the record, 47 s) and **run 2** (`.work/shake13/h4-run2/`,
  47 s): `compare13.py` lists **0 cells** between them and exits 0. HUNT4's two runs agree.
- **HUNT3 against HUNT4**, `results/c72639f/FACES13.txt`: 184 cells differ (it exits 1 by design).

| class | baseline `c3bdae2` | HUNT3 `0c0f5a3` | HUNT4 `c72639f` |
|---|---|---|---|
| refused | 374 | 375 | **546** |
| clean | 362 | 368 | **377** |
| `ACCEPTED:DEFECT:leg_mismatch` | 61 | 62 | 0 |
| `ACCEPTED:DEFECT:fallthrough` | 32 | 38 | 0 |
| `ACCEPTED:DEFECT:wrong_value` | 34 | 34 | 0 |
| `ACCEPTED:clean` | 20 | 24 | 0 |
| `ACCEPTED:DEFECT:false_trap` | 16 | 0 | 0 |
| `ACCEPTED:DEFECT:uaf` | 7 | 11 | **2** |
| `ACCEPTED:DEFECT:segv` | 2 | 2 | 0 |
| `ACCEPTED:other` | 2 | 2 | 0 |
| `DEFECT:fallthrough` (scope wild) | 6 | 6 | 0 |
| `DEFECT:leg_mismatch` (scope wild) | 3 | 3 | **2** |
| `OVERRESTRICT` | 12 | 6 | **6** |
| `REFUSED_TRAP` | 2 | 2 | 0 |
| **generated** | **933** | **933** | **933** |

- **At HUNT4, by section:** S 3 refused; A 157 refused, 9 clean; B 87 refused, 17 clean, 2
  `DEFECT:leg_mismatch` (scope wild); C 250 refused, 244 clean, 6 `OVERRESTRICT`; D 37 refused, 93 clean;
  E 12 refused, 14 clean, 2 `ACCEPTED:DEFECT:uaf`. Every refused cell names the code its rule names.
- **The ten cells for triage** (§9): `g0915`/`g0916` (E, a callee storing the view into an element of an
  array of holders, dies-first: 70/70 and 25/25); `g0249`/`g0250` (B, the dead `wild` load before a `NULL`
  test: 107/14, scope wild); and C's six pointer twins at the literal and array places, `if_one`,
  `loop_zero`, `pick_one` (`g0692`, `g0694`, `g0696`, `g0704`, `g0706`, `g0708`): `BORROW-002`.
- **FACES13's 184 moves**, by class pair: `ACCEPTED:DEFECT:leg_mismatch` → refused 62,
  `ACCEPTED:DEFECT:fallthrough` → refused 38, `ACCEPTED:DEFECT:wrong_value` → refused 34, `ACCEPTED:clean`
  → refused 24, `ACCEPTED:DEFECT:uaf` → refused 9, `DEFECT:fallthrough` → clean 6 (wild), refused → refused
  4 (the atomic address cells: `EMIT-002` → `TYPE-055`), `ACCEPTED:DEFECT:segv` → refused 2,
  `ACCEPTED:other` → refused 2, `REFUSED_TRAP` → clean 2 (`??!`), `DEFECT:leg_mismatch` → clean 1 (wild).
  REPORT §14.7 reads them by DEF and landing.
- **At the baseline** the class looks as at HUNT3, with these differences of its own: D's 16 constant
  `/ 0`, `% 0`, `MIN / -1` and `MIN % -1` cells are accepted and trap at run time (97/98 on both legs,
  `ACCEPTED:DEFECT:false_trap`: DEF-133's d7 shape, refused by name since D-331 at landing 79); E's 4
  outlives `Seat` cells are `OVERRESTRICT` and its 4 dies-first `Seat` cells refused, by `PARSE-001`
  "expected a type" (the grouped `(fixed uint8[])` field type is later); A's `fixed wild` and `fixed wildx
  … = NULL` reads are `OVERRESTRICT` and B's module `fixed T-> = NULL` cells refused, by `TYPE-004` ("a
  `const` initialiser must be a constant expression"); A's four atomic address cells are refused
  `EMIT-002`, as at HUNT3. Read at triage step (d).

**The regression leg at HUNT4** (§8), every runner under `--llvm .work/llvm-20.1.8` and the lock, into
`results/c72639f/` and each finding's `VERDICTS-c72639f.txt`; the findings' baseline line runs under 20.1.8
too (one `--llvm` serves both, as in M12):

| run | at HUNT4 `c72639f` | against HUNT3 `0c0f5a3` | time |
|---|---|---|---|
| recall, `known-m13.txt` | 25 rows; `check_known_fixed.py`: 19 `match`, no MISMATCH; its 6 gaps DEF-106's and DEF-108's rows, each its "once fixed" verdict by hand (`TYPE-086` twice, `FLOW-001` twice, both controls 0/0) | identical to `known-m12.txt` (`diff` prints nothing) | 5 s |
| findings, `VERDICTS-c72639f.txt` (HUNT4 twice, the baseline once) | 49 findings: 160 programs in 34; the 15 row findings write no file (M12v (7)'s fix, §3); the HUNT4 runs agree for every program; F-003 … F-010 re-run with `--heap` | the loop prints `moved: F-029` alone; F-049 read by hand; every baseline line as committed | 250 s, then 30 s |
| M2 grid, `cells.jsonl` | 956: 562 clean, 394 refused | 0 moved (`MOVES.md`) | 59 s |
| M9 grid, `cells9.jsonl` | 7 571: 4 071 clean, 3 500 refused, 0 anomalies | 24 moved, refused → clean (`MOVES9.md`) | 458 s |
| M10, `m10.jsonl` | 223: 218 agree, 5 disagree | 0 changed (`m10-changes.txt`) | 18 s |

- **F-029** (`moved:`): `ctl_k3_int64_buffer_refused` is `PARSE-001` at 7:11 at HUNT4 ("expected a name:
  `buffer` is a keyword and cannot name a binding") where HUNT3 gives `PARSE-002` at 7:5 ("expected an
  expression"), both by `gen/snip.py --show-msg` under the lock; `k1` and `k2` unchanged. Landing 136.
- **F-049**, read by hand against `VERDICTS.txt` (its `0c0f5a3` lines; the loop skips a finding with no
  `VERDICTS-0c0f5a3.txt`): `pick_reinit_read` and `pick_reinit_loop` `MOVE-001` → 0/22/22 at both HUNT4 runs;
  `ctl_local_reinit_read` 22/22 and `ctl_pick_moved_read` `MOVE-001` unchanged; the baseline lines as
  committed. Landing 132 (DEF-256).
- **M9's 24** are MOVES12 row 44's cells exactly (checked by id against HUNT2's and HUNT3's records): the
  16 `pick_own × loop_move` (the four that leaked at HUNT2 now live 0/0) and the 8 `pick_own × swap`
  read-after and reuse-sentinel cells, each SAFE, refused `MOVE-001` at HUNT3, clean at HUNT4. Landing 132.
- **F-025's `run.sh`** at HUNT4, twice (outside §8's written commands, as M12 ran it): "plain: npkc=0
  no-wildx: npkc=0, 0 x WILDX-003" both times, as at HUNT3.
- **No memory fault in the regression leg** at HUNT4: no finding line moved to 70, 95, 107, 139 or 170;
  M2 and M9 have no `DEFECT` class.
- **Dispatch note (e), each from HUNT4:** (1) F-049 as read: `pick_reinit_read` and `pick_reinit_loop`
  `MOVE-001` → 22 at both legs, `ctl_local_reinit_read` 22/22 and `ctl_pick_moved_read` `MOVE-001`
  unchanged — ticked. (2) The 24 cells left `MOVE-001` and run clean, the 4 F-006 leak cells clean too; none
  stays refused, so no may-fact shape arises; no memory fault — ticked. (3) `ctl_k3_int64_buffer_refused`
  `PARSE-002` → `PARSE-001`, 7:5 → 7:11, still refused; `k1` and `k2` unchanged — ticked.
- **The move table** is `results/c72639f/MOVES13.md`: the regression leg's moves (F-029 by 136; F-049 and
  M9's 24 by 132) and grid13's 184 faces by landing (114, 115, 116, 119, 120), **zero UNEXPLAINED**, and
  P1–P11 each ticked or explained. One detail of P6 there: at HUNT3 and the baseline a struct reached
  through a parameter or a helper's return gives 107/0, the `NULL` test folded away after the dereference,
  DEF-251's inferred face measured.

**Triage** (§9; S90), every HUNT4 cell that is not `refused` or `clean` (10) and the probe result, through
M5's five steps. The triage programs were run as probes (`.work/probes13/t_*`, 23) under the lock at HUNT4
twice and HUNT3 under 20.1.8 and at the baseline under its own 20.1.2; each finding's programs were then
recorded by `gen/run_findings.py` at HUNT4 twice and the baseline (`VERDICTS.txt`) and at HUNT3 twice and the
baseline (`VERDICTS-0c0f5a3.txt`), under 20.1.8.
- **(a) The tie to a later registry:** `git -C .work/nitpick fetch origin` at 05:05 EDT left `origin/main` at
  `c72639f`, HUNT4 itself, so no face is "fixed at a later landing". Dedup against `KNOWN_DEFECTS.md` and the
  registry at HUNT4 is in each README.
- **F-050** (`g0915`, `g0916`; `findings/F-050-callee-view-store-into-array-element/`), **a soundness hole**:
  a callee storing a block-local view into an element of the array behind its pointer argument, `(<-a)[0i64]
  = Cursor{ src: src, … }`, compiles and the program reads the free poison after the block, 170 at both
  legs, at HUNT4, HUNT3 and the baseline. DEF-252's shape at a destination landing 116's sixteen sites do not
  name; the direct element store is `BORROW-002` everywhere, the whole-pointee callee store `BORROW-002` at
  HUNT4. (b) minimised by `gen/minimize.py` (`--want 0,170,170`: the body kept whole, the failsafe cut to the
  arms the compiler demands); (c) HUNT4 twice, both legs; (d) the baseline, the same. Its control
  `ctl_elem_outlives` (0/0) is the case an implementation refusing every element store gets wrong.
- **F-051** (`g0249`, `g0250`; `findings/F-051-wild-dead-load-legs-disagree/`), **reported apart as the check
  of DEF-251 (i)**, scope wild: a load through a `wild` `NULL` pointer whose value is unused faults at -O0 and
  is deleted at -O2 (107/14 before a `NULL` test, 107/0 without one) at all three compilers; the used-load
  control is 107/107 at HUNT4 and 107/12 before 115. (b) `gen/minimize.py --want 0,107,14`, the body kept
  whole.
- **F-052** (§4's probe `q_a09`; `findings/F-052-atomic-method-through-pointer-not-lowered/`), lower priority,
  **crash / loud emission**: `p.store(…)` and `p.load()` through an `atomic<int64>->` are `EMIT-002` at all
  three compilers, where `(<-p).load()` lowers (0/0). Written by hand (S74's reason). In grid13 it shows at
  HUNT3 and the baseline as A's four atomic address cells refused `EMIT-002`; at HUNT4 `TYPE-055` comes first.
- **C's six `OVERRESTRICT`** (`g0692`, `g0694`, `g0696`, `g0704`, `g0706`, `g0708`): **not a finding — my
  expectation was wrong.** Each twin stores `@z` into a field or element of a local inside a branch, a loop
  or an arm. The probes show the refusal does not depend on the nesting: `w.f = @z;` in the same block is
  `BORROW-002` too, while `W{ a: 1i64, f: @z }` and `x = @z` are accepted. The compiler's sentence is D-004
  rule 3's: "a borrow cannot be stored here: only a local binding in the borrowing frame is provably no
  longer-lived than the borrow", and D-004 says "Rule 3 is deliberately strict to start. If real compiler
  code needs borrow-into-inner-aggregate, relax it then, with evidence." The compiler is right by the
  ruling. The expectation stays as committed (S36, S45), and the six cells' verdict is read against it.
- **A slip of mine**, not a finding: the triage probe `t_4_atomic_ptr_fetch_add` named a local `old`, a
  keyword at HUNT4 (`PARSE-001`, landing 136); it is not used.

**The close** (§11, §13): `REPORT.md` §14 written, with a pointer in its opening; `KNOWN_DEFECTS.md`'s DEF-250,
DEF-251 and DEF-252 rows updated from the three seeds' HUNT4 measurements, labelled `c72639f` (dispatch note
(c); DEF-251's names 115 (i) and 119 (ii)), DEF-253's status read from the registry (fixed at 118), and F-050,
F-051 and F-052 listed as candidates. The scratch is removed: `.work/probes13`, `.work/ctl13` and
`.work/shake13`; no `VERDICTS-scratch.txt` was made.

**The gate** (§11), at the commit that ticks M13:
- [x] Start checks passed: the tree clean before the switch, GitHub fetched, `main` fast-forwarded `d44dfe3` →
  `581c091`, `f31dfc6` an ancestor, M12 ticked, `local-m13` new; the go quoted as S77, covering (i) and (ii).
- [x] The compiler fetched; `.work/H4.full` is `c72639f…`, not `0c0f5a3`, and NOTICES has a `| 114 |` row. The
  three compilers built (HUNT4 here, the baseline and HUNT3 M12's, their digests re-read); HUNT4's `npkc.ll` and
  `npkrt.o` equal notice 137's ladder row; the canaries pass at all three; `llvm-config` prints 20.1.8 and 20.1.2.
- [x] Housekeeping (1b) committed (`b8f9a4f`), DEF-256 among it, with no committed record changed but MOVES12's
  row 4 wording.
- [x] grid13, classify13 and compare13 committed (`cbc38b9`: the commit's own date 04:49:55, its push 04:49:57 by
  the reflog of `origin/local-m13`; M13v's finding (9)) before any grid13 run (the first, the
  seeds at HUNT3, at 04:50:05). The 89 template probes before it were §4's, for spellings only (S89). Every
  cell's expectation carries its rule and source; ids equal `mod:` names; the denominators are stated with
  `SKIPPED.txt` (933 generated, 431 skipped).
- [x] The seeds flagged at HUNT3 as `ACCEPTED:DEFECT:…` (107/11, 107/99, 170/170); the LLVM control run, and no
  cell differs, so there is no candidate from it.
- [x] grid13 run at the baseline, at HUNT3 (the record) and at HUNT4 twice; the two HUNT4 runs agree in all 933
  cells.
- [x] The regression leg at HUNT4: `MOVES13.md`, zero UNEXPLAINED, every prediction ticked or explained.
- [x] Every candidate through the five steps and classed by §9's table (F-050 a soundness hole, F-052 crash /
  loud emission, F-051 reported apart as the check of DEF-251 (i)); every finding has a control a wrong
  implementation gets wrong (`ctl_elem_outlives`, `ctl_wild_used_load`, `ctl_atomic_ptr_explicit`). C's six
  `OVERRESTRICT` are recorded as a wrong expectation, with the rule.
- [x] §14's denominators add up: in each of the three runs, 933 = refused + clean + `OVERRESTRICT` +
  `REFUSED_TRAP` + each `DEFECT` and `ACCEPTED` count (no `LOUD`, `CRASH`, `timeout` or `other` but the baseline's
  and HUNT3's two `ACCEPTED:other`); moved = explained (184 in FACES13; 3 programs, 0, 24 and 0 cells in the
  regression leg).
- [x] No committed record changed: `git diff --name-only --diff-filter=MDR origin/main -- results/c3bdae2
  results/9126350 results/0c0f5a3 'findings/*/VERDICTS*.txt'` prints only `results/0c0f5a3/MOVES12.md`, the
  (1b)(2) wording edit. No scratch is left (`.work/probes13`, `.work/ctl13`, `.work/shake13`).

## M14 — the S-140 class (F-051 R1), a narrow run (session 12, the Team seat)

**The start checks** (the brief's §1; PLAN.md's start rules (a)–(d)).
- **The remote.** `git remote get-url origin` is GitHub's `alternative-intelligence-cp/nitpick-fuzz`, over SSH.
  `git fetch origin` at 03:02 EDT moved `origin/main` from `581c091` to `e289864` (M13, merged).
- **Clean tree, before any switch.** On `local-m13` at `e289864`, `git status --porcelain` printed nothing, and
  there was no stash.
- **The fast-forward.** `git switch main && git merge --ff-only origin/main` took `main` from `581c091` to
  `e289864`.
- **The order gate.** `git merge-base --is-ancestor e289864 origin/main` exits 0; M13 is ticked; there were no M14
  boxes. The file's only unticked box is M13's optional box 10 (`PROGRESS.md:91`), closed unworked by S91: commit
  M14 (1b) marks it `[-]` (S96), and M14 does not touch `m11/`.
- **The branch.** There was no `origin/local-m14` and no local one, so `git switch -c local-m14 --no-track
  origin/main` at `e289864` (03:02:41). No upstream is set; every push is `git push origin local-m14`.
- **The go** is S93, management_2's funding quoted verbatim. The dispatch says those words stand as the go for
  HUNT5 = the compiler's `origin/main` at this fetch, that management_2 asked for no author's go, and that no
  LLVM go is needed (S95).
- **(a)** `uname -a`, `nproc`, `free -g`, `df -h .` and `python3 --version` are under Environment below. **(b)**
  `CLAUDE.md`'s defect definition was re-read: it covers an accepted program with no `wild`, no `=>!` and no raw
  pointer arithmetic, and a silent wrong answer counts as a memory fault does. Every grid14 cell contains `wild`, so
  S-140 changes no verdict under it; grid14's cells are reported apart, as the check of §27 (D-364). **(c)** Only
  HUNT5 needed building: `.work/` holds the compiler clone, the baseline `c3bdae2` (M12's build; its `npkc.ll`
  28 111 929 / `4029fc70…`, `npkrt.o` 72 576 / `162b8975…` and `npkc` 9 724 160 / `5fd636b9…` re-read, the
  worktree clean) and `.work/llvm-20.1.2`. **(d)** M14 starts at its first box.
- **Read first, in the brief's order:** `CLAUDE.md`; PLAN.md 2.1, 2.2, 5.2 (a)–(e) and the start rules; this
  file's M13 section and S76–S91; F-051's README and its four programs; REPORT §14; `gen/grid13.py` and
  `gen/classify13.py`. Read only, at HUNT5 once fetched: TYPE_REFERENCE §27's `NULL` subsection, whose last bullet
  equals the brief's quote; DECISIONS.md D-364; the registry's DEF-272, DEF-273 and DEF-274
  (`meta/roadmap/OPEN_DECISIONS.md`); and the manager's 22 probes at landing 148 (`sha256sum -c SHA256SUMS`: 22 OK).

**The LLVM** (§2; S95). `.work/llvm-20.1.2/bin/llvm-config --version` prints `20.1.2` (the symlink to
`/usr/lib/llvm-20`, S48, S70). Every runner in M14 names it, and runs with `TMPDIR` =
`/home/randy/Team/TMP/M14/tmp` (the brief; S80's practice).

**HUNT5** (§2; S94). `git -C .work/nitpick fetch origin` at 03:02:58 EDT moved the compiler's `origin/main` from
`c72639f` to `249eae9` (`249eae91559bfc1e3b8a17b12286c21108e4215a`, 2026-10-24 21:57:10 -0400, "1.6.1e, landing
161: DEF-305 …"), written to `.work/H5.full` and `.work/H5`. `git merge-base --is-ancestor 02856cfc` it exits 0,
so it carries landing 155, and TYPE_REFERENCE §27 at it holds "whose value NOTHING uses" once. It is 24 commits
past HUNT4, one per landing (138–161). Among 138–148, the ones M14 reads are 138 (`2a9d601`, DEF-272, the
fuzzer's F-050), 142 (`79cd363`, DEF-176; its notice: "S-134 and S-140 RATIFIED as D-363 and D-364") and 146
(`915f427`, DEF-274 and S-134's R4). The landings past 148, from `meta/NOTICES.md`:
- 149 `50ebf7d` DEF-277; 150 `ea571d5` DEF-276; 151 `9eaf3b6` D-363's R1; 152 `538c596` DEF-278 and DEF-281;
- 153 `ea1307c` DEF-282 and DEF-285; 154 `5136096` DEF-287; 155 `02856cf` DEF-288 and DEF-290;
- 156 `a5693a6` DEF-296 and DEF-289's first face; 157 `5cc1fb9` DEF-289's second face; 158 `8e33737` DEF-300;
- 159 `51b6d82` DEF-297 and DEF-301 (with DEF-303); 160 `954c21a` DEF-302; 161 `249eae9` DEF-305.

**HUNT5, built** by the brief's command under `.work/llvm-20.1.2` and the lock, in 64.9 s (03:04:04–03:05:09 EDT).
Its log's `npkg/main.npk: exit 2` line is the normal one.

| product | HUNT5 `249eae9` | notice 161's ladder row | |
|---|---|---|---|
| `npkc.ll` | 33 418 659 / `59d16f1d2273e545…` | 33 418 659 / `59d16f1d2273e545…` | equal |
| `npkc.o` | 13 828 024 / `34c7d3dd9b95d6e4…` | 13 828 024 / `34c7d3dd9b95d6e4…` | equal |
| `npkrt.o` | 72 656 / `c8e5033ad17c70f8…` | 72 656 / `c8e5033ad17c70f8…` | equal (HUNT3's and HUNT4's too) |
| `builder.o` | 12 067 840 / `5870b02dcf97950c…` | 12 067 840 / `5870b02dcf97950c…` | equal |
| `npkc` | 11 957 184 / `2c8d898f101a3280…` | 11 957 184 / `3705093c8d6a7c65…` | not compared: a linked binary's sha differs between builds (the brief) |
| `builder` | 10 402 536 / `98f91fec7da79220…` | 10 402 536 / `b4dff7b33b187ce0…` | not compared, as `npkc` |

The ladder row is the workbench BOARD's "THE BASELINE NOTICE 162 MUST QUOTE" (notice 161's rows "at `249eae9`";
the Workspace copy at `9fc5dca`, read only).

**Canaries** (M0.6), one batch under the lock (03:05:35, 0.9 s), by
`$L python3 gen/snip.py commission/canary.npk commission/canary_malformed.npk --at hunt5 base --llvm .work/llvm-20.1.2`:
at the baseline and HUNT5, `canary.npk` gives npkc 0 and runs 0/0, and `canary_malformed.npk` gives npkc 1 with
`NITPICK-PARSE-001` ("canary_malformed.npk:3:20: expected a type").

**The housekeeping (1b)** (§3, items 1–4), wording only; no committed record changes.
- **(1) M13's box 10** is `[-]`, closed unworked by S96, with the reason appended (§1 step 5).
- **(2) M13v's finding (7).** `KNOWN_DEFECTS.md`'s "Open:" heading stood over DEF-250 … DEF-253, whose rows read
  "fixed". It is now "Open at HUNT3:" over DEF-190 … DEF-245, and a new heading, "Open at HUNT3, fixed since",
  stands over DEF-250 … DEF-253. No row's text changed and no row moved.
- **(3) M13v's finding (8).** The M13 section's "1 364 combinations in all, plus the three seeds" counted the
  seeds twice. Measured from `gen/grid13.py` (`enumerate_space()` and `build()`): the axes give 1 361 (930
  generated + 431 skipped), and with the 3 seeds 933 generated, 933 + 431 = 1 364. The line now shows that
  arithmetic.
- **(4) M13v's finding (9).** The M13 gate's "`cbc38b9`, 04:49:57" now names both times: the commit's own date
  04:49:55 (`git log -1 --format=%ci cbc38b9`) and its push 04:49:57 (`git reflog show --date=iso
  origin/local-m13`, "update by push").

**Learn by snippet** (§4; S97). Two batches in `.work/probes14/` (probe files only, never committed), each run by
`$L python3 gen/snip.py <files> --at hunt5 base --llvm .work/llvm-20.1.2` under the lock. By npkc and O0/O2, at
HUNT5 / the baseline:
- **The manager's 22 probes**, copied (`sha256sum` against their `SHA256SUMS`: 22 equal; 03:11:46, 12.8 s). At HUNT5
  every one gives its landing-148 verdict (§4's table):
  - the discard spellings are refused at both: `q01_discard` (`int64:_~v = <-p;`) and `q02_drop` (`drop <-p;`),
    `PARSE-002` "expected an expression". So U has no discard form;
  - the twin `q14_twin` 14/14 at both, and the unused bindings `t01_unused_p`, `t02_unused_q` and
    `t03_discard_q` 0/0 at both;
  - the dead load at four more places, `q10_param`, `q11_field`, `q12_module` and `q13_returned`: 107/14 at
    HUNT5; at the baseline the same, but `q12_module` is `TYPE-004` ("a `const` initialiser must be a constant
    expression", the module place's refusal there, as in M13);
  - `q07_overwrite` (the overwrite, then `v` read) 107/0 at both;
  - the used loads `q09_callee_reads` and `r08_arith` 107/107 (107/12 at the baseline), and `r04_deadcalc`
    (`int64:w = v + 1i64;`, `w` unread) 107/107 (107/0 at the baseline);
  - the boundary shapes `q03_untaken`, `q05_ignore`, `r15_copy`, `r06_selfcancel` and `r18_selfcmp`: **107/0**
    at both;
  - `q04_deadcalc`, `q06_selfcancel` and `q08_arith`, with the short six-arm failsafe: `REACH-002` at both,
    "`failsafe` does not name `IntOverflow`, which can reach it (D-179)". grid14 uses `grid13.FAILSAFE13`, which
    names every identity.
- **25 grid14 templates, for spellings only** (03:18:44, 17.3 s): every spelling §4's batch had not compiled at
  HUNT5, each a generated cell copied under its own name: the struct `S` at the five places (U's `overwrite` +
  `test`: `wild S->`, `S:v = <-X;`, `v = S{ a: 5i64, b: 2i32 };`), the W `none` twins' unused bindings (`H:h` at
  `field`, `P` at `module`, `p` at `returned`, for both T, and `S` at `local` and `param`), `v.a` in K's `cmp`,
  `arith` and `callee` (at `local`, and `callee` at `param`), B's six struct forms (`argv.len`, `ign(v)` with
  `S:_~x`, `S:w = v;`, `v.a - v.a`, `v.a != v.a`, `v.a + 1i64`), the `int64` overwrite with nothing read after,
  and `wild_dead_struct_load_t`. **All 25 compile at HUNT5** (npkc 0), so no twin needs a respelling and none is
  skipped. At the baseline the three `module` templates are `TYPE-004`. No expectation was set or changed from
  these runs (S97). One reading ahead of the runs: at the baseline the struct `test` cells at `param` and
  `returned` give 107/0, the folded `NULL` test that P9 expects to be the live control for condition (c).

**The grid** (§5; S98). `gen/grid14.py` (539 lines) imports `gen/grid13.py`'s `Prog`, `X`, `FAILSAFE13`, `STRUCT_S`,
`ARM`, `Skip` and `WILD_RE`, and does not edit it. `cells14/` was added to `.gitignore` before it first wrote
anything. `python3 gen/grid14.py --out cells14` generates **109 cells** and skips none (`cells14/SKIPPED.txt`: "0
combinations not emitted"):

| section | what | generated | expect | flagged (`s140`) |
|---|---|---|---|---|
| S | F-051's four programs, byte for byte, and the three dead loads' twins | 7 | 4 TRAP 107, 3 SAFE (14, 0, 14) | 3 |
| U | the unused load: O (`bind`, `overwrite`) × P × T × after (`test`, `none`) | 40 | TRAP 107 | 40 |
| W | the twins: P × T × after, no load | 20 | SAFE, 14 (`test`) or 0 (`none`) | 0 |
| K | the used load: O (`cmp`, `arith`, `callee`) × P × T | 30 | TRAP 107 | 0 |
| B | the boundary of "uses": O (`untaken`, `ignore`, `copy`, `selfsub`, `selfcmp`, `deadadd`) × `local` × T | 12 | TRAP 107, the strict reading | 0 |
| **all** | | **109** | 86 TRAP 107 (4 + 40 + 30 + 12), 23 SAFE (3 + 20) | **43** |

Every cell is scope wild; its `rule` is
§27's last `NULL` bullet copied from HUNT5's file (TYPE_REFERENCE.md:2314–2324 at `249eae9`, equal to the brief's
quote), B's with the brief's note appended; its `source` names that bullet and D-364.
`python3 gen/grid14.py --selfcheck` prints:
```
note: RULE27 equals §27's bullet at HUNT5 249eae9
selfcheck: 109 cells (B 12, K 30, S 7, U 40, W 20), 0 skipped, 109 combinations; condition (c): 43 flagged cells, each its twin with the load deleted (0 respellings); every check passes
```
It checks: two builds identical; ids are module names, equal to their `mod:` lines and metas; every meta has
`run.py`'s keys, `section`, `expect_exit`, `scope` "wild", `rule` and `source`; the rule equals HUNT5's text (read by
`git show 249eae9…:meta/specs/TYPE_REFERENCE.md`); every TRAP exit is `MachineFault`'s arm and every SAFE cell a twin
with 14 or 0; only U cells and the three dead-load seeds carry `s140`, each with `s140_o2` equal to its twin's
expected exit and `s140_twin` naming an emitted, unflagged SAFE cell of the same P, T and after; **condition (c),
literally**: each flagged cell's text with its one load line (and its one overwrite line) deleted and its `mod:`
name changed to the twin's equals the twin's text; the layout and D-013 in every generated cell; the denominators
(109 combinations = 109 cells + 0 skipped, per section); and `cells14/` is this build byte for byte.

**The classifier** (§5; S99). `gen/classify14.py` (391 lines) imports `run_class` and `classify` from
`gen/classify13.py` and nothing else; it never calls `classify13.main()` and writes no `*13.*` file. Its changes are
marked CHANGE 1–5 in the code. `python3 gen/classify14.py --selftest` prints:
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
The brief's eleven cases come first, each flagged one with a twin agreeing with its `s140_o2` but for the three about
the twin; the two unflagged ones carry everything but the flag, so they fail on condition 1 alone. Four more follow.
**Tested before any run on synthetic records in scratch** (`/home/randy/Team/TMP/M14/synth/`, from `cells14/INDEX.jsonl`,
no compiler): a record shaped like the predictions at HUNT5 classes as 43 `PERMITTED:S-140`, 56 `clean` and B's 10
`DEFECT:leg_mismatch`, and `--against13` exits 0 with 43 moves of kind (a) and 12 of kind (b); a record shaped like
the baseline's reading (the module cells refused, K at 107/12, the four struct `test` cells at `param` and `returned`
at 107/0) exits 0 with the four counted as failing condition 4, each `DEFECT:leg_mismatch`. Two wrong classifiers put
in place of the S-140 test, each a case the control must get right: "flagged and O0 = 107" (no condition (c)) makes
`--against13` exit 1 on the baseline-shaped record (its four cells) and 0 on the HUNT5-shaped one, which has no live
population; "any wild cell with 107 at -O0" makes it exit 1 on both.

**The runs** (§6), each block under `set -e`, each runner alone under the lock at 4 jobs, LLVM 20.1.2:
- **HUNT5, run 1** (`results/249eae9/cells14.jsonl`, the record; 03:23:57, 10.5 s) after `--out cells14`,
  `--selfcheck` ("every check passes") and `--selftest` ("15 cases, 15 pass"); **run 2** (`.work/shake14/h5-run2/`,
  03:24:14, 10.6 s). `compare13.py` lists **0 of 109 cells** and exits 0: HUNT5's two runs agree.
- **The baseline** (`results/c3bdae2/cells14.jsonl`, 03:24:30, 8.0 s).
- **F-050 … F-052** (`findings/F-05[012]-*/VERDICTS-249eae9.txt`, 03:24:51, 12.4 s): HUNT5 twice, the baseline once;
  the HUNT5 runs agree for every program, and every baseline line equals `VERDICTS.txt`'s.

| class | S | U | W | K | B | all at HUNT5 `249eae9` | all at the baseline `c3bdae2` |
|---|---|---|---|---|---|---|---|
| `PERMITTED:S-140` | 3 / 3 | 40 / 28 | | | | **43** | 31 |
| clean | 4 / 3 | | 20 / 16 | 30 / – | 2 / – | **56** | 19 |
| `DEFECT:leg_mismatch` | – / 1 | – / 4 | | – / 9 | 10 / 9 | **10** | 23 |
| `DEFECT:fallthrough` | | | | – / 15 | – / 3 | 0 | 18 |
| `REFUSED_TRAP` | | – / 8 | | – / 6 | | 0 | 14 |
| `OVERRESTRICT` | | | – / 4 | | | 0 | 4 |
| **generated** | **7** | **40** | **20** | **30** | **12** | **109** | **109** |

(Each section cell reads HUNT5 / the baseline.) At each compiler 109 = the sum of the class counts, and no cell is
`LOUD`, `CRASH`, `timeout` or `other`.
- **At HUNT5:** the three dead-load seeds are permitted at 107/14, 107/0 and 107/14, `ctl_wild_used_load` is clean
  at 107/107 and the three twins clean (14/14, 0/0, 14/14); every U cell is permitted, 20 at 107/14 (`test`) and 20
  at 107/0 (`none`), each with its twin at 14/14 or 0/0; every W twin clean; **every K cell 107/107, clean**; B's
  `deadadd` 107/107 clean at both T, and **B's other ten, `untaken`, `ignore`, `copy`, `selfsub` and `selfcmp` at
  both T, 107/0, `DEFECT:leg_mismatch`**: the cells for triage (§7).
- **At the baseline:** the module place is refused `TYPE-004` ("a `const` initialiser must be a constant
  expression"), so its 8 U and 6 K cells are `REFUSED_TRAP` and its 4 W twins `OVERRESTRICT`, as M13 found the
  module `fixed … = NULL` refused there. The dead-load seeds are permitted, `ctl_wild_used_load` is 107/12; U is
  permitted in 28 cells and **4 are 107/0 against an `s140_o2` of 14** (below); K disagrees in all 24 cells it
  compiles, the `int64` cells at `local`, `field` and `returned` 107/12 (9, `DEFECT:leg_mismatch`) and the struct
  cells and the `int64` `param` cells 107/99 (15, `DEFECT:fallthrough`: the -O2 leg runs into the failsafe's
  `(*)` arm, DEF-251's face before landing 115); B is 107/0 in 9 cells and 107/99 in 3 (the struct `untaken`,
  `ignore` and `deadadd`).
- **`--against13`** (writes nothing) **exits 0 at both compilers.** At HUNT5, 55 cells differ between classify13
  and classify14: 43 `DEFECT:leg_mismatch` → `PERMITTED:S-140` on cells meeting conditions 1–5 (kind (a)), and 12
  `DEFECT:wrong_value` → `clean` on the 14-twins (the 10 W `test` twins and two seed twins; kind (b)). At the
  baseline, 41: 31 of kind (a) and 10 of kind (b) (its two module `test` twins are refused). Nothing else moves.

**The narrowness control** (§6), three parts, each against a wrong classifier of its own:
1. **Against a broad allowance** ("any `wild` cell with 107 at -O0"): every unflagged cell at 107 and then
   something else stays a defect class, so condition 1 holds the class to the generator's flag. **At HUNT5, 10
   cells**: B's ten at 107/0, each `DEFECT:leg_mismatch`. **At the baseline, 37 cells**: `ctl_wild_used_load` and
   the nine `int64` K cells at 107/12, `DEFECT:leg_mismatch` (the case the brief names); the 15 K cells at 107/99,
   `DEFECT:fallthrough` (decided before the class, as the brief's order puts it); B's 9 at 107/0, `DEFECT:leg_mismatch`;
   B's 3 at 107/99, `DEFECT:fallthrough`. None is permitted.
2. **Against a mid-width allowance** ("flagged and O0 = 107", without (c)): the flagged cells whose legs disagree
   but fail condition 4 or 5, counted by `--against13`. **At the baseline, 4 cells, the live population the brief
   expected**: `m007_u_struct_param_bind_test`, `m019_u_struct_returned_bind_test`,
   `m027_u_struct_param_overwrite_test` and `m039_u_struct_returned_overwrite_test`, each 107/0 against an `s140_o2`
   of 14 with its twin at 14/14, each failing condition 4 and each `DEFECT:leg_mismatch`: U's struct `test` cells at
   `param` and `returned`, the `NULL` test folded away after the load as `KNOWN_DEFECTS.md` records before landing
   115, now measured on `wild` cells. No other U `test` cell joined them. **At HUNT5, 0**: every flagged cell meets
   (c), so there the selftest's cases are (c)'s only control.
3. **Against a classifier that moves anything else:** `--against13` exits 0 at both, so the only moves into
   `PERMITTED:S-140` are flagged leg mismatches meeting conditions 1–5: **43 cells at HUNT5, 31 at the baseline**,
   besides the twins' change-1 moves (12 and 10).

**Triage** (§7; S100). At HUNT5 the cells that are neither `clean` nor `PERMITTED:S-140` are B's ten at 107/0,
`DEFECT:leg_mismatch`: `untaken`, `ignore`, `copy`, `selfsub` and `selfcmp`, each at `int64` and struct. No K cell
(all 30 clean at 107/107), no U cell (all 40 permitted) and no twin (all 23 clean) needs triage. One candidate, F-053,
through M5's five steps:
- **Where the load goes** (a probe batch under the lock, 03:29:14, 2.3 s: `npkc` and `opt -O2` at HUNT5 under 20.1.2
  on grid14's `int64` cells, the `load` instructions counted in each `@main`): `untaken` keeps one `load i64, ptr
  null` at -O2, sunk into the branch that reads it (`if.then0`, entered when `argv.len > 100`); `ignore`, `copy`,
  `selfsub` and `selfcmp` keep none; `deadadd`, K's `cmp` keep one; F-051's dead load keeps none. Two mechanisms, a
  sink and a deletion, and by my reading one cause, so one candidate, as the brief's "sunk or deleted" foresees.
- **(a) Deduplication** against `KNOWN_DEFECTS.md`, the registry at HUNT5 and S-140/D-364: F-051 / DEF-273 is the
  load whose value nothing reads, and D-364 permits "an UNUSED load … and nothing else"; no registry entry names a read
  load sunk or deleted (searched for "sunk", "untaken", `v != v`, `v - v`, "dead load", "F-053"). Not a duplicate.
  The compiler was fetched again before filing (07:57:18): `origin/main` is still `249eae9`, so no newer landing
  changes a face.
- **(b) Minimised** by `gen/minimize.py .work/hunt5 <cell> --want 0,107,0 --llvm .work/llvm-20.1.2` on the five
  `int64` cells, each alone under the lock (07:58:04–07:59:16, 72.5 s, 54–57 builds each): it cut every failsafe to
  the six arms the compiler demands; it kept `ignore`'s body whole, and in the other four it also deleted the read,
  leaving F-051's dead load at the same 0/107/0. That is the face: by exit codes the read is invisible. So the four
  reproducers keep the body whole under the minimiser's failsafe (`IntOverflow` added where the compiler demands it,
  `REACH-002`), and the README says so.
- **(c) Confirmed** on both legs twice and **(d) at the baseline** by `gen/run_findings.py F-053 --hunt .work/hunt5
  --base .work/base --llvm .work/llvm-20.1.2 --name VERDICTS.txt` (08:00:14, 8.9 s): the five faces 0/107/0 at both
  HUNT5 runs and at the baseline (old: present before landing 115); the controls `ctl_wild_used_cmp` 107/107 (107/12
  at the baseline), `ctl_wild_dead_load` 107/0 at both (the permitted reference), `ctl_wild_dead_add` 107/107 (107/0
  at the baseline). The HUNT5 runs agree.
- **(e)** `findings/F-053-wild-used-load-legs-disagree/`: five faces, three controls, `VERDICTS.txt` and the README
  (the shape, §27 and D-364's words, the verdicts, grid14's ten cells at both compilers, the IR, the controls, the
  minimisation, the deduplication, and what is measured apart from what is inferred). Class: **reported apart, as
  the check of §27 (D-364), scope wild**, as F-051 was. It goes to the fuzzer's manager for D6 through the
  dispatcher.

**The housekeeping, items 5 and 6** (§3), in the same commit:
- **(5)** `KNOWN_DEFECTS.md`'s M13 block ("Not registered … candidates for the workbench") is rewritten from the
  registry at HUNT5: F-050 = DEF-272, FIXED at 138 (`2a9d601`); F-051 = DEF-273, ruled R1 by S-140 and recorded as
  D-364 with landing 142 (`79cd363`), the legs' one permitted disagreement, not a defect; F-052 = DEF-274, FIXED at
  146 (`915f427`). Each "fixed" is confirmed by M14's `run_findings` at HUNT5; the manager's re-measures at 138, 142
  and 146 are labelled as reported. D6 is named the fuzzer's manager's (`README.md:46`). F-053 is listed after it as
  M14's candidate.
- **(6)** F-051's README gains a section "S-140 (R1)": the ruling and D-364 at 142, §27's sentence, the three holes
  permitted and `ctl_wild_used_load` guarding the used-load half, and the four programs' HUNT5 verdicts with their
  grid14 classes. No earlier line changed (`diff` against the copy before it: 0 lines removed), and no
  `VERDICTS*.txt` file.

**The close** (§8, §10): `REPORT.md` §15 written, with a one-bullet pointer in its opening; the scratch removed
(`.work/probes14`, `.work/shake14` and `/home/randy/Team/TMP/M14`, at 08:07 EDT). `cells14/` stays, gitignored and
regenerable, as `cells13/` does.

**The gate** (§8), at the commit that ticks M14:
- [x] Start checks: the tree clean before the switch, GitHub fetched, `main` fast-forwarded `581c091` → `e289864`,
  `e289864` an ancestor, M13 ticked, `local-m14` new; the go quoted as S93.
- [x] HUNT5 fetched (`249eae9`), carrying landing 155 (`02856cfc` an ancestor) and §27's S-140 sentence (one match);
  built (64.9 s); its `npkc.ll`, `npkc.o` and `npkrt.o` equal notice 161's ladder row; the canaries pass at the
  baseline and HUNT5; `llvm-config` prints 20.1.2.
- [x] Housekeeping (1b) committed (`3942f3f`), with M13's box 10 marked `[-]` and no committed record changed.
- [x] grid14 and classify14 committed (`f20e418`: the commit's own date 03:23:43, its push 03:23:45 by the reflog of
  `origin/local-m14`) before any grid14 run (the first, HUNT5's run 1, at 03:23:57). The 25 template probes before it
  were §4's, for spellings only (S97). `--selfcheck` and `--selftest` pass; every cell's `meta.json` carries its
  expectation and rule; every id equals its `mod:` name; the denominators come with `SKIPPED.txt` (109 generated, 0
  skipped).
- [x] The runs: grid14 at HUNT5 twice, agreeing in all 109 cells, and at the baseline; `run_findings` for F-050 …
  F-052 at HUNT5 twice and the baseline.
- [x] The narrowness control: all three parts reported with their cell counts (10 and 37 unflagged cells; 0 and 4
  flagged cells failing a condition; 43 and 31 moves into the class, at HUNT5 and the baseline); `--against13` exits
  0 at HUNT5 and at the baseline.
- [x] Triage: every cell in §7's scope (B's ten) through the five steps; F-053 with its controls; `KNOWN_DEFECTS.md`'s
  M13 block and F-051's README updated (`2558ec6`).
- [x] Denominators: §15's add up; per run the generated count is the sum of the class counts (109 = 43 + 56 + 10 at
  HUNT5; 109 = 31 + 19 + 23 + 18 + 14 + 4 at the baseline).
- [x] No committed record changed: `git diff --name-only --diff-filter=MDR origin/main -- results
  'findings/*/VERDICTS*.txt'` prints nothing. No scratch is left: `.work/probes14`, `.work/shake14` and
  `/home/randy/Team/TMP/M14` are removed.

## M15 — the DEF-296 family, a view of a pointer's pointee stored through an indirection (session 13, the Team seat)

**The start checks** (the brief's §1; PLAN.md's start rules (a)–(d)).
- **First, a stop and a ruling.** Before any check ran, the Team's deny rule refused a read-only `sed` on a file of the
  manager's probe set in the Workspace clone; the session stopped and reported, and the dispatcher ruled that it resume
  here, reading the Workspace with read-only tools only. The Log (2026-10-28) records both.
- **The remote.** `git remote get-url origin` is GitHub's `alternative-intelligence-cp/nitpick-fuzz`, over SSH. `git
  fetch origin` at 23:19:17 EDT moved `origin/main` from `e289864` to `70a0d8b` (M14, merged).
- **Clean tree, before any switch.** On `local-m14` at `70a0d8b`, `git status --porcelain` printed nothing, and there
  was no stash.
- **The fast-forward.** `git switch main && git merge --ff-only origin/main` took `main` from `e289864` to `70a0d8b`.
- **The order gate.** `git merge-base --is-ancestor 70a0d8b origin/main` exits 0; M14 is ticked (`PROGRESS.md:93`);
  there were no M15 boxes. The only box not `[x]` is M13's `[-]` box 10 (S96). M15 touches no other milestone's boxes
  and does not touch `m11/`.
- **The branch.** There was no `origin/local-m15` and no local one, so `git switch -c local-m15 --no-track
  origin/main` at `70a0d8b` (23:19:31). No upstream is set; every push is `git push origin local-m15`.
- **The go** is S102: management_3's GO for the Team's week, verbatim, with `nitpick-fuzz_5`'s release beside it. The
  dispatch says those words stand as the go for HUNT6 = the compiler's `origin/main` at this fetch, and that no LLVM go
  is needed (S104).
- **(a)** `uname -a`, `nproc`, `free -g`, `df -h .` and `python3 --version` are under Environment below. **(b)**
  `CLAUDE.md`'s defect definition was re-read: an accepted program with no `wild`, no `=>!` and no raw pointer
  arithmetic that reads freed memory (the poison 170, read as 70 through grid15's observer) is a defect. M15's hazard
  cells are such programs, so its findings are reported normally, not apart. **(c)** HUNT6 and REG155 were built after
  the go was recorded; `.work/` keeps every tree and log it held (the compiler clone, `base`, `hunt2`, `hunt5`, the
  LLVM trees). **(d)** M15 starts at its first box.
- **Read first, in the brief's order:** `CLAUDE.md`; PLAN.md 2.1, 2.2, 5.2 (a)–(e) and the start rules; this file's
  M13 and M14 sections and S76–S100; F-050's README and its programs; REPORT §14 and §15; `gen/grid13.py` and
  `gen/classify13.py`. Read only, at HUNT6 once fetched: MEMORY_REFERENCE.md's D-325 paragraph (`:269`–`:284`) and its
  holder paragraph (`:320`–`:333`); DECISIONS.md's landing-156 note (`:22145`–`:22154`), which holds the indirection
  walk (`record_refs_through_indirection`) the brief's quote ends with; the registry's DEF-289 and DEF-296 … DEF-310
  (`meta/roadmap/OPEN_DECISIONS.md`; DEF-311 is not registered at HUNT6); NOTICES rows 156–163. The manager's sets in
  the Workspace clone's `.work/briefs/`, each checked by `sha256sum -c SHA256SUMS`: `m15-probes-l163/` 60 OK (its 16
  `r_*.npk`, which the file does not list, equal `m15-roads/`'s byte for byte), `m15-probes-l163-r2/` 60 OK,
  `m15-roads/` 16 OK, `m15-seeds/` 8 OK, `m15-expect/` 4 OK; with the logs beside them. `m15-probes-q-l163/` is not this
  family and was not opened.

**The LLVM** (§2; S104). `.work/llvm-20.1.2/bin/llvm-config --version` prints `20.1.2`. The link is `/usr/lib/llvm-20`,
whose `opt`, `llc`, `ld.lld` and `clang` each print 20.1.2. The bare `opt` on `PATH` is `~/.local/bin/opt`, 20.1.8, and no
runner uses it: `gen/run.py` and `gen/snip.py` put `<--llvm>/bin` first. Every runner in M15 names
`--llvm .work/llvm-20.1.2` and runs with `TMPDIR` = `/home/randy/Team/TMP/M15/tmp`.

**HUNT6** (§2; S103). `git -C .work/nitpick fetch origin` at 23:19:56–23:19:57 EDT moved the compiler's `origin/main`
from `249eae9` to `1480ca8` (`1480ca81aa4d9d82976149f7f6ae5e44b2c5c640`, 2026-10-26 14:05:02 -0400, "1.6.1e, landing
163: DEF-306 + DEF-308 …"), written to `.work/H6.full` and `.work/H6`, which were absent. `a5693a6` (156) is an
ancestor of it and `1480ca8` is HUNT6 itself, so neither STOP check fires. No commit lies past `1480ca8`, and HUNT6's
NOTICES has no `| 164 |` row: **no landing past 163**. (management_4's word, in the release, was that harness 164
`3adfc05` would land about 00:15 EDT; the fetch came before it, so §7 measures any later landing at its own tree.) The
landings from REG155 to HUNT6, from `meta/NOTICES.md` at HUNT6:
- 156 `a5693a6` DEF-296 and DEF-289's first face; 157 `5cc1fb9` DEF-289's second face; 158 `8e33737` DEF-300;
- 159 `51b6d82` DEF-297 and DEF-301 with DEF-303; 160 `954c21a` DEF-302; 161 `249eae9` DEF-305;
- 162 `8c4f005` DEF-304; 163 `1480ca8` DEF-306 + DEF-308.

**REG155** (§2; S104) is `02856cf` (`02856cfc72463f105da70bd9c23c7f2cc1bf8151`, 2026-10-23 09:34:46 -0400, landing 155:
DEF-288 and DEF-290), in `.work/REG.full` and `.work/REG`.

**Both built** by the brief's commands, each alone under the lock, in the worktrees `.work/hunt6` and `.work/reg155`:
HUNT6 in 64.8 s (23:20:28–23:21:33 EDT), REG155 in 66.0 s (23:21:44–23:22:50). Each log's `npkg/main.npk: exit 2` line
is the normal one.

| product | HUNT6 `1480ca8` | notice 164's row | REG155 `02856cf` | notice 156's row |
|---|---|---|---|---|
| `npkc.ll` | 33 468 275 / `fbd42f41e1ea4828…` | equal | 32 973 616 / `8f76731c6fc1c7ca…` | equal |
| `npkc.o` | 13 844 112 / `faec89d321a8ce6b…` | equal | 13 689 368 / `9031ecebf6fbdbe9…` | equal |
| `npkrt.o` | 72 656 / `c8e5033ad17c70f8…` | equal | 72 656 / `c8e5033ad17c70f8…` | equal |
| `builder.o` | 12 067 840 / `5870b02dcf97950c…` | equal | 12 067 840 / `5870b02dcf97950c…` | equal |
| `npkc` | 11 970 864 / `7f7b2ab1b1d322dd…` | same size, not compared | 11 843 192 / `32dcfb0b084c60b5…` | same size, not compared |
| `builder` | 10 402 536 / `98f91fec7da79220…` | same size, not compared | 10 402 536 / `98f91fec7da79220…` | same size, not compared |

The rows are the workbench BOARD's "THE BASELINE NOTICE 164 MUST QUOTE" (notice 163's rows at `1480ca8`) and "THE
BASELINE NOTICE 156 MUST QUOTE" (notice 155's rows at `02856cf`), read in the Workspace copy (read only) and compared
to 64 hex by a script that only reads. A linked binary's sha differs between builds (the brief), so `npkc` and `builder`
are not compared.

**Canaries** (M0.6), one batch under the lock (23:22:58, 0.9 s), by `$L python3 gen/snip.py commission/canary.npk
commission/canary_malformed.npk --at hunt6 reg155 --llvm .work/llvm-20.1.2`: at HUNT6 and REG155, `canary.npk` gives
npkc 0 and runs 0/0, and `canary_malformed.npk` gives npkc 1 with `NITPICK-PARSE-001` ("canary_malformed.npk:3:20:
expected a type").

**The housekeeping (1b)** (the brief's §3; wording only, no committed record changed):
1. **F-053's README** (M14v's F6): "would answer 13" is now 12, with a parenthesis naming where 12 is measured at
   `c3bdae2`: `ctl_wild_used_cmp` at 107/12 (F-053's `VERDICTS.txt`) and grid14's nine `int64` K cells at `local`,
   `field` and `returned` (`m061`, `m065`, `m069`, `m071`, `m075`, `m079`, `m081`, `m085`, `m089`) at 107/12
   (`results/c3bdae2/classified14.jsonl`). No `VERDICTS*.txt` is edited.
2. **`KNOWN_DEFECTS.md`'s DEF-296 family block**, a section after the M13/M14 block: one row for each of DEF-289 and
   DEF-296 … DEF-311, its one-line shape and status read in HUNT6's registry, labelled as the compiler seat's
   registrations, measured where a grid cell exists by M15, with F-050 = DEF-272 cross-referenced, not repeated. The
   cells column is filled in M15 (4); DEF-304, DEF-306, DEF-307 and DEF-310 say "no grid cell". The brief's §3 labels
   (DEF-302 `destroy`, DEF-304 and DEF-306 spawn, DEF-310 the `List` reallocation) do not match HUNT6's registry, which
   gives DEF-302 the aliased pointer write, DEF-304 and DEF-307 the `List` element pointer, DEF-306 the spawn's lend and
   DEF-310 `destroy`; the rows follow the registry, and the block says so. DEF-311 is not registered at HUNT6.
3. **M14v's F3 and F5**: a one-line note under F-053's "Not registered" entry in `KNOWN_DEFECTS.md`, and one after
   §15.6's three parts in `REPORT.md`, each saying M14v ruled the point non-blocking. No verdict changes.

**Learn by snippet** (the brief's §4), at HUNT6 and REG155.
- **The copies.** With `cat`, one file at a time, into `.work/probes15/` (scratch): the files each `SHA256SUMS` lists
  in `m15-probes-l163/` (60), `m15-probes-l163-r2/` (60), `m15-roads/` (16) and `m15-seeds/` (8); each set's
  `sha256sum -c`, run on the copies against its `SHA256SUMS` (itself copied with `cat` to the Team scratch), is all OK.
  `m15_expect.tsv` and `m15_expect_check.py` into `gen/`, both OK against `m15-expect/SHA256SUMS`. The checker, as §4
  runs it, reading only: `python3 -B gen/m15_expect_check.py gen/m15_expect.tsv
  /home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs` prints **"104 rows, 0 mismatches"**, exit 0 (rows cite
  `m15-roads.log` 32, `m15-grid-l163l155.log` 36, `m15-probes-l155.log` 16, `m15-probes-l163-r2.log` 16,
  `m15-f050-l163l155.log` 4).
- **My own probes**, 30, where the named sets have none: the seven `fld` writes the table keys (`w_pp_fld_<w>` for
  `whole`, `alias`, `walias`, `callee`, `calias`, `cwhole`, `method`; `r_fld.npk` with the write spellings of
  `m15-probes-l163/`'s `p03`–`p09`), and 23 twins (`rt_<road>` for the 16 roads, `wt_pp_fld_<w>` for the seven).
- **One batch under the lock** (23:39:55–23:40:56 EDT, 61 s, `.work/probes15-h6r155.log`): 96 files at HUNT6 and
  REG155, by `$L python3 gen/snip.py <files> --at hunt6 reg155 --llvm .work/llvm-20.1.2 --show-msg`: the 16 roads,
  `m15-probes-l163-r2/`'s `q01`–`q20` with their twins (40), my 30, the eight seeds and F-050's two holes.
  - **Every hazard probe gives its table row**, at both compilers: 104 lines, the 42 `pp` keys, the eight seeds and
    F-050's two, 0 differ.
  - **Every twin is clean**, 0/0 at both compilers, 42 of 42.
  - **`q18_pp_fld_cresf` and its twin** are `NITPICK-TYPE-024` at both (`(raw ids(p)).s = …` is no place), the write
    grid15 omits.
- **The spellings and codes**, every one compiled at both compilers:
  - **The view** `string_bytes(p.s)` (`S->:p`), its twin `string_bytes("abcdef")`.
  - **The roads**: `bare` `fixed uint8[]:hv = V;`; `fld` `h.v = V;`; `pl` `Holder->:hp = @h; hp.v = V;`; `pld`
    `(<-hp).v = V;`; `plw` `<-hp = Holder{ v: V, k: 1i32 };`; `pf` `Outer:ou = Outer{ inner: @h, n: 0i32 };
    ou.inner.v = V;`; `tl` `BP:b = BP{ p: @h, n: 0i32 }; BP->:bp = @b; bp.p.v = V;`; `sle` `Holder[]:sl =
    arr[0i64...2i64]; sl[0i64].v = V;`; `rge` `arr[0i64...2i64][0i64].v = V;`; `lst` `List<Holder>->:lp = @l;
    (<-lp)[0i64].v = V;` (the `List` by `list_init::<Holder>(2i64)` and one `list_push`); `cad` `drop put(@h, V);`;
    `cpl` `drop put(hp, V);`; `csl` `drop puts(arr[0i64...2i64], V);`; `cslv` `Holder[]:t = arr[0i64...2i64]; drop
    puts(t, V);`; `cps` `Box:bx = Box{ sl: arr[0i64...2i64], n: 0i32 }; drop putq(@bx, V);`; `cpp` `PB:pb = PB{ q:
    @h, n: 0i32 }; drop putpq(@pb, V);`; `cbv` `drop gb(Box{ sl: arr[0i64...2i64], n: 0i32 }, V);`; `cbp` `drop
    gp(PB{ q: @h, n: 0i32 }, V);`; `mth` `drop h.hset(V);`; `mpl` `drop hp.hset(V);`.
  - **The writes**: `dir` `p.s = raw fresh();`; `whole` `<-p = S{ s: raw fresh() };`; `alias` `S->:q = p; q.s =
    raw fresh();`; `walias` `S->:q = p; <-q = S{ s: raw fresh() };`; `callee` `drop ws(p);`; `calias` `S->:q = p;
    drop ws(q);`; `cwhole` `S->:q = p; drop wsw(q);`; `method` `drop p.sset();`; `cres` `(<-(raw ids(p))) = S{ s:
    raw fresh() };`; `cresc` `drop ws(raw ids(p));`; `cresm` `drop (raw ids(p)).sset();`.
  - **The inner placement**: `int32:g = 0i32; if (g == 0i32) { <the road's bindings and the store> }`, the
    holder (`h`, `arr` or the `List`) before it.
  - **The codes**: every refusal of a hazard probe is `NITPICK-BORROW-015` at both compilers, but F-050's two holes,
    `NITPICK-BORROW-002` at both; every accepted hazard probe reads 70/70 (the seeds 170/170, their own observer).
- **grid15's cells are the probes' programs.** Each of grid15's 84 `pp` and twin cells equals a probe of this batch
  byte for byte apart from its `mod:` line (a scratch comparison): 35 `pp` cells the manager's (16 `m15-roads/`, 19
  `m15-probes-l163-r2/`), 7 mine, 19 twins the manager's (`-r2`'s), 23 mine. So every spelling grid15 uses was
  compiled and run at HUNT6 and REG155 before any grid15 run.

**grid15 and classify15** (the brief's §5; S105, S106), committed in M15 (2) before any grid15 run.
- **`gen/grid15.py`** imports `Prog`, `X`, `FAILSAFE13`, `OBS_V`, `Skip` and `WILD_RE` from `gen/grid13.py` and
  defines its own `S` and `Holder`. **100 cells:** S 16 (the eight DEF-296 faces, F-050's two holes, the six
  candidates), R 64 (32 `pp` keys, 20 same-block `dir` roads and 12 inner, each with its twin), W 20 (`fld` × ten
  writes, each with its twin). The space R × W × B × V is 20 × 12 × 2 × 3 = **1 440 combinations: 84 emitted, 1 356
  in `cells15/SKIPPED.txt`** (480 the `lo` view, deferred; 760 a write other than `dir` on a road other than `fld`;
  80 `cresf`, `TYPE-024`; 36 an inner placement on a road without one). `cells15/` is in `.gitignore` (this commit)
  before the first write. `--selfcheck`:
  ```
  note RULE15 equals the D-325 paragraph at HUNT6 1480ca8
  note cells15/ is this build, byte for byte
  selfcheck: 100 cells (R:pp 32, R:twin 32, S 16, W:pp 10, W:twin 10), 1356 skipped, 1440 combinations + 16 seeds; 42 pp keys = the table's; every check passes
  ```
- **`gen/classify15.py`** imports `classify`, `run_class` and `exp_mismatch` from `gen/classify13.py`, writes
  `classified15.jsonl` and `SUMMARY15.md`, and runs the recall gate (`--recall`). `--selftest`, in memory:
  ```
  ok    good pair: seeds uaf@REG, leak cells uaf@REG, twins clean, codes, anchored, coverage, commits -> {}, exit 0
  ok    COMMIT: both files carry the same commit                                                      -> {COMMIT}, exit 1
  ok    COMMIT: the two files' commits swapped                                                        -> {COMMIT}, exit 1
  ok    COVERAGE: an extra id in one file, a benign twin clean at HUNT6                               -> {COVERAGE}, exit 1
  ok    SEED-RECALL: a named seed ACCEPTED:DEFECT:double_free@REG (95/95)                             -> {SEED-RECALL}, exit 1
  ok    SEED-RECALL: a named seed ACCEPTED:DEFECT:false_trap@REG (91/91)                              -> {SEED-RECALL}, exit 1
  ok    LEAK-RECALL: pp:pl:dir:same (leak, refused@HUNT6) refused@REG with BORROW-015                 -> {LEAK-RECALL}, exit 1
  ok    SILENT-PASS: a leak pp cell ACCEPTED:clean@HUNT6 (0/0)                                        -> {SILENT-PASS}, exit 1
  ok    SILENT-PASS: a leak pp cell ACCEPTED:other@HUNT6 (5/5)                                        -> {SILENT-PASS}, exit 1
  ok    SILENT-PASS: pp:fld:dir:same (refuse) ACCEPTED:timeout@REG155                                 -> {SILENT-PASS}, exit 1
  ok    TWIN@REG155: a twin not clean at REG155 (70/70, DEFECT:uaf), clean@HUNT6                      -> {TWIN}, exit 1
  ok    TWIN@HUNT6: a twin not clean at HUNT6 (refused, OVERRESTRICT), clean@REG155                   -> {TWIN}, exit 1
  ok    CODE-H6: pp:fld:dir:same refused@HUNT6 with PARSE-001 only, clean BORROW-015@REG              -> {CODE-H6}, exit 1
  ok    CODE-REG: pp:fld:dir:same refused@REG with BORROW-015 and PARSE-001, clean@HUNT6              -> {CODE-REG}, exit 1
  ok    UNANCHORED: a pp cell with reg155 None refused at both                                        -> {UNANCHORED}, exit 1
  ok    FINDINGS: pp:pl:dir:same ACCEPTED:DEFECT:uaf@HUNT6, leak@REG: listed, no tag                  -> {}, exit 0
  ok    REGRESSION: pp:fld:dir:same (refuse) refused@REG, ACCEPTED:DEFECT:uaf@HUNT6                   -> {REGRESSION}, exit 3
  ok    REGRESSION outranks: a regression and a COVERAGE breakage                                     -> {COVERAGE, REGRESSION}, exit 3
  selftest: 18 cases, 18 pass
  ```
- **Disclosed:** before this commit `gen/grid15.py` wrote `cells15/` (for `--selfcheck`'s comparison of the written
  grid), and `classify15.py` and its gate were tried once on synthetic records made from the table's rows in the Team
  scratch (no compiler ran; gate exit 0, 14 findings, as the table predicts). No cell of `cells15/` was compiled or run.

**The runs** (the brief's §6), by its block as written (a script in the Team scratch, each runner alone under the lock,
no `flock` 75; `.work/run15.log`), after commit M15 (2) `51337dc`. The trees were `1480ca8` and `02856cf`, their HEADs
equal to `.work/H6.full` and `.work/REG.full`, and `gen/grid15.py` and `gen/classify15.py` equal to HEAD; the grid
was regenerated, `--selfcheck` passed and `--selftest` gave 18 of 18 first.

| run | wall | `ACCEPTED:DEFECT:uaf` | `clean` | `refused` | generated |
|---|---|---|---|---|---|
| HUNT6 `1480ca8`, run 1 (the record) | 23:53:28–23:53:36 | 14 | 42 | 44 | 100 |
| HUNT6, run 2 (`.work/shake15/`) | 23:53:36–23:53:43 | 14 | 42 | 44 | 100 |
| REG155 `02856cf` | 23:53:43–23:53:52 | 48 | 42 | 10 | 100 |

- **HUNT6's two runs agree:** `compare13` lists 0 of 100 cells, exit 0.
- **By section**, at HUNT6: S 6 `uaf` (the six candidates) and 10 `refused` (the eight DEF-296 faces, `BORROW-015`;
  F-050's two, `BORROW-002`); R 5 `uaf` (`tl`, `cps` and `cpp` inner; `cbv` and `cbp`), 27 `refused`, 32 twins clean;
  W 3 `uaf` (`cres`, `cresc`, `cresm`), 7 `refused`, 10 twins clean. At REG155: S 14 `uaf` (the eight faces at
  170/170, the candidates at 70/70) and 2 `refused` (F-050's); R 26 `uaf`, 6 `refused` (`bare`, `fld`, `cad`, `mth`,
  and `cps` and `cpp` in one block), 32 clean; W 8 `uaf`, 2 `refused` (`callee`, `whole`), 10 clean. Every refusal
  of a hazard cell is `NITPICK-BORROW-015` at both compilers but F-050's `NITPICK-BORROW-002`.
- **The recall gate**, `python3 gen/classify15.py --cells cells15 --recall results/1480ca8/classified15.jsonl
  results/02856cf/classified15.jsonl`, **exit 0**:
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
  The fourteen: `n019_pp_fld_cres_same`, `n021_pp_fld_cresc_same`, `n023_pp_fld_cresm_same`, `n043_pp_tl_dir_inner`,
  `n069_pp_cps_dir_inner`, `n073_pp_cpp_dir_inner`, `n075_pp_cbv_dir_same`, `n077_pp_cbp_dir_same`, each 70/70 at
  both compilers, and the six candidate seeds `q05`, `q11`, `q12`, `q17`, `q19`, `q20` (the same six keys), 70/70 at
  both: the table's eight `H6/leak` keys, no other. Every hazard verdict of the two record runs is the table's row for
  its key (116 records, the 58 hazard cells at both compilers, 0 differ, by a scratch comparison).
- **Disclosed:** a `git -C .work/nitpick fetch origin` (23:53:39–23:53:40, for §7) ran while HUNT6's run 2 was
  running. A fetch moves no worktree's HEAD or files, and the compiler's `origin/main` was still `1480ca8`.

**Triage** (the brief's §7; PLAN 5.2's five steps; S107). Its scope is every HUNT6 cell neither `clean` nor
`refused`: the fourteen `ACCEPTED:DEFECT:uaf` cells, which are eight keys (the six candidate seeds are six of the
grid's keys again). No twin is anything but clean (42 of 42 at both compilers), so no harness problem stands first.
- **(a) Deduplicated** against `KNOWN_DEFECTS.md` (the family block) and HUNT6's registry (`OPEN_DECISIONS.md` at
  `1480ca8`, read in `.work/od-h6.md`). Every key is a shape OPEN at HUNT6, so each is known: PLAN 5.2 (a)'s "note
  the cell id and move on", and P7 binds. None is filed, and F-054 is not used.

  | key | cells at HUNT6, 70/70 | the registry's row at HUNT6 | how the cell matches it |
  |---|---|---|---|
  | `pp:cbv:dir:same` | `n075` | DEF-298, OPEN (`:3568`) | the registered shape r1, a by-value struct parameter's slice field handed on to a storing callee |
  | `pp:cbp:dir:same` | `n077` | DEF-298, OPEN | the pointer twin the row measured at 158 (t298b, a by-value parameter's POINTER field handed on) |
  | `pp:cps:dir:inner` | `n069`, `q11` | DEF-299, OPEN (`:3586`) | the registered shape pf: the box in an inner block, its slice field stored through by a callee |
  | `pp:cpp:dir:inner` | `n073`, `q12` | DEF-299, OPEN | the pointer twin the row measured at 158 (t299c); one block refuses, as its t299b does |
  | `pp:tl:dir:inner` | `n043`, `q05` | DEF-299, OPEN | the brief's pre-map; the same cause read (the store is recorded on the pointee `b`, whose block ends, not on `h` its field points to), in a same-frame two-level pointer local where the row names a parameter's pointee |
  | `pp:fld:cres:same` | `n019`, `q17` | DEF-309, OPEN (`:3818`) | a direct whole-pointee write through a call-result pointer, `(<-(raw ids(p))) = S{…}` |
  | `pp:fld:cresc:same` | `n021`, `q19` | DEF-305, FIXED at 161 (`:3737`) | its writer face (k302j) with the result rooted at a pointer PARAMETER: still open, the brief's incomplete fix |
  | `pp:fld:cresm:same` | `n023`, `q20` | DEF-305, FIXED at 161 | its receiver face (k302k), the same parameter-rooted gap |

  **Two flags for D6** (readings, not measurements): the DEF-299 row's letter names a pointer PARAMETER's pointee
  stored through by a callee, while `tl`-inner is a pointer local's pointee stored through directly (and `pf`-inner,
  one pointer level on a local struct, is refused); and the DEF-305 row says FIXED and names no parameter-rooted
  exception. DEF-302's row (`:3672`–`:3676`) says the landing-160 resolver gives no target for a pointer rooted at a
  PARAMETER ("a pointer parameter's pointee stays DEF-275's store-matrix question"), which may be why `cresc` and
  `cresm` stay open; that is inferred, not bisected. The manager's r2 log reads all six candidates 70/70 at `249eae9`
  (161) as well (`m15-probes-l163-r2.log` lines 18, 42, 46, 66, 74, 78, the manager's measurement).
- **(b) Minimising** does not apply: (a) ends the triage of a known shape. The grid cell is already one probed
  program of about forty lines, and its twin is the control a wrong analysis gets wrong.
- **(c) Both legs, twice:** already measured. Each of the fourteen reads 70 at `-O0` and at `-O2` in HUNT6's run 1
  and run 2, and in the probe batch before them.
- **(d) The pair with REG155**, over the 58 hazard cells (by a scratch count of the two `classified15.jsonl`):
  - accepted at both: the fourteen above, still-open holes, deduplicated by (a);
  - accepted at REG155 and refused at HUNT6: 34, the 26 `pp` cells the table marks `reg155=="leak"` but the eight
    `H6/leak` keys, and the eight DEF-296 seeds. A fix landed in (155, 163], so none is a finding;
  - refused at both: 10, the `pp` cells `bare`, `fld`, `cad`, `mth`, `cps` and `cpp` in one block and `fld` ×
    `callee` and `whole`, and F-050's two. They were fixed before 155;
  - refused at REG155 and accepted at HUNT6: **none, so no regression** (the gate's `REGRESSION` 0).
- **(e)** No finding directory is written.
- **KNOWN_DEFECTS' family block:** the cells column is filled for every row, with the verdicts at both compilers.
  DEF-311 says "no grid cell" (it is not registered at HUNT6). The compiler's `origin/main` was still `1480ca8` at
  every fetch for §7: 23:53:40, 23:56:07, 23:57:20 and 00:00:45 on 2026-10-29, and at the close, 00:07:42
(`.work/fetch-m15-triage.log`). So no landing past 163
  is measured, and the three call-result keys stand against DEF-309 and DEF-305 at 163.

**The close** (the brief's §8 and §10).
- **The gate holds in every box.** The start checks, the compilers and the housekeeping are boxes 1–3. grid15 and
  classify15 were committed before any run, with `--selfcheck` and `--selftest` passing (boxes 4 and 5). The runs
  had the trees at their pins and `gen/` equal to M15 (2), HUNT6's two runs agreed, and the recall gate exited 0
  (box 6). The triage is box 7.
- **The recall gate is reported** with every tag's count in `REPORT.md` §16.6.
- **The denominators add up.** In each run, generated = the sum of the class counts: HUNT6 14 + 42 + 44 = 100 (both
  runs) and REG155 48 + 42 + 10 = 100. The grid is 84 emitted + 1 356 skipped = 1 440 combinations, plus 16 seeds,
  which gives the 100 cells.
- **No committed record changed.** `git diff --name-only --diff-filter=MDR origin/main -- results
  'findings/*/VERDICTS*.txt'` prints nothing. M15 only adds the six files under `results/1480ca8/` and
  `results/02856cf/`.
- **The scratch is removed** at 00:08:09: `.work/probes15/`, `.work/shake15/` and `/home/randy/Team/TMP/M15/` (with
  the `TMPDIR` in it). `.work/` keeps its trees (`hunt6`, `reg155` and the rest) and its logs, including
  `.work/probes15-h6r155.log`, `.work/run15.log` and `.work/fetch-m15-triage.log`.
- **`REPORT.md` §16**, "M15 — the DEF-296 family", has sections 16.1–16.11, with P1–P7 each ticked. A bullet points to
  it from the report's opening paragraph.

## Environment

*(session 13, measured 2026-10-28 23:19:31 EDT; M15 run here, on the Team seat: the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-38-generic #38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 31 used, 53 free, 125 available; Swap 15 (1 used)
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  2.5T used  4.1T avail (38%)
os:        Linux Mint 22.3 (Ubuntu 24.04 base)
python3:   Python 3.12.3
git:       2.43.0
llvm:      .work/llvm-20.1.2 -> /usr/lib/llvm-20 (20.1.2; S48, S70, S104); the bare `opt` on PATH is 20.1.8, unused
earlyoom:  active
```

The author's machine, shared with the compiler seat, the library agents and the Workspace's other seats.
Every build and every run takes the Team seat's harness lock (`flock -w 300 -E 75` on
`/home/randy/Team/TMP/harness.lock`) for one build, batch or runner at a time, at 4 jobs; library work outranks
the fuzzer on it, and on `flock`'s exit 75 the same command is run again, at most six attempts in a row (S101). Every
runner runs with `TMPDIR` = `/home/randy/Team/TMP/M15/tmp`.

*(session 12, measured 2026-10-25 03:02:45 EDT; M14 run here, on the Team seat: the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-38-generic #38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 39 used, 18 free, 117 available; Swap 15 (0 used)
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  2.5T used  4.1T avail (38%)
os:        Linux Mint 22.3 (Ubuntu 24.04 base)
python3:   Python 3.12.3
git:       2.43.0
llvm:      .work/llvm-20.1.2 -> /usr/lib/llvm-20 (20.1.2; S48, S70, S95)
earlyoom:  active
```

The author's machine, shared with the compiler seat, the library agents and the Workspace's other seats.
Every build and every run takes the Team seat's harness lock (`flock -w 300 -E 75` on
`/home/randy/Team/TMP/harness.lock`) for one build, batch or runner at a time, at 4 jobs; library work outranks
the fuzzer on it (S92). Every runner runs with `TMPDIR` = `/home/randy/Team/TMP/M14/tmp`.

*(session 11, measured 2026-10-21 04:11 EDT; M13 run here, on the Team seat: the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-38-generic #38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 34 used, 50 free, 122 available; Swap 15 (0 used)
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  2.5T used  4.2T avail (38%)
os:        Linux Mint 22.3 (Ubuntu 24.04 base)
python3:   Python 3.12.3
git:       2.43.0
llvm:      .work/llvm-20.1.2 -> /usr/lib/llvm-20 (20.1.2; S48, S70); .work/llvm-20.1.8, the release tarball (S67, S77)
earlyoom:  active
```

The author's machine, shared with the compiler seat, the library agents and the Workspace's other seats.
Every build and every run takes the Team seat's harness lock (`flock -w 300 -E 75` on
`/home/randy/Team/TMP/harness.lock`), one at a time, at 4 jobs (S1). Every runner runs with `TMPDIR` in
the session's scratch (S80).

*(session 10, measured 2026-10-15 16:43 EDT; M12 run here, on the Team seat: the start check (a))*

```
uname -a:  Linux AriaX-DEV-1 7.0.0-38-generic #38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
nproc:     48
free -g:   Mem 157 total, 33 used, 69 free, 123 available; Swap 15 (0 used)
df -h .:   /dev/mapper/ariax--vg-ariax--lv  6.9T  2.4T used  4.2T avail (37%)
os:        Linux Mint 22.3 (Ubuntu 24.04 base)
python3:   Python 3.12.3
git:       2.43.0
llvm:      /usr/lib/llvm-20 (llvm-config 20.1.2), linked as .work/llvm-20.1.2 (S48, S70)
earlyoom:  active
```

The author's machine, shared with the compiler seat, the library agents and two other Team agents.
Every build and every run takes the Team seat's harness lock, one at a time, and parallelism stays at
4 jobs (S1).

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
- **S65 — TYPE 661–2122 is taken in three parts, each to its own clean point.** The
  workbench relayed the author's go with a softer landing line: TYPE lands at a clean point
  by 95 % of the week, or stops at a clean point inside it. So the range is cut at section
  boundaries: A, 661–1176 (§6–9, `type2.py`); B, 1177–1592 (§10–18, `type3.py`); C,
  1593–2122 (§19–28, `type4.py`). Each part is extracted, committed, run, triaged, pushed
  and reported on its own, as a reference is. A claims module may not import another (its
  claims would load twice), so `type2.py` copies the scaffolding it shares with `type1.py`
  and `verif3.py`.

- **S66 — M12 is the re-baseline at HUNT3, on management's corrected brief**
  (`fuzz-m12-brief-revise-2026-10-15.md`, READY by its re-verification
  `fuzz-m12-brief-reverify-2026-10-15.md` with one gate fix). PLAN.md ends at M11 ("the author and
  the workbench choose the next task together"); the brief is that choice (management_0's queue, item
  3; its proposal's Option A). PLAN.md is not edited (rule 9). The session is the brief's single
  worker, dispatched on the Team seat by its manager, Ailp-team_3, on 2026-10-15 at 16:41: no
  sub-agents, at most 4 jobs. `nitpick-fuzz_2`, this repository's manager, reviews `local-m12` and
  merges it. The dispatch adds seven binding notes, (a)–(e) from management_0 and (f)–(g) from
  `nitpick-fuzz_2`:
  - (a) the gate fix: sections 3 and 8 allow M11 BUILD claims whose new output is the pin refusal
    (their manifests pin `llvm = "20.1.2"`, P32), recorded as P32's toolchain moves; any other
    difference stops the run, and section 6's "0 cells moved by the toolchain" excludes those claims;
  - (b) an existing local `local-m12` is resumed with `git switch`;
  - (c) a bisected findings run uses `--name VERDICTS-bisect.txt`, deleted afterwards;
  - (d) `gen/m10.py` reads the `.work/hunt2` and `.work/base` worktrees, which exist by section 4;
  - (e) section 3 runs after section 4;
  - (f) landing 112 (DEF-232, F-048) is on the compiler's `main`, so HUNT3 carries it: P21 and
    section 7's item 2 take their "carries 112" branch, and M11's `ty1944`, F-048's source claim,
    moves with it;
  - (g) from `nitpick-libs_19`'s advance notice of landing 113 (F55), each measured here: P22's
    programs, with F-029's `k2` already refused `PARSE-002` at `9126350`; `me0119`, `me0119b` and
    `me0183`, refused `PARSE-001` at a binding named `buffer` before their claims are reached
    (DEF-235), explained by landing 113, listed in REPORT §13.12 and NOT re-spelled in M12 (that is
    `nitpick-fuzz_2`'s to schedule); and `as0572`, whose `#[align(16i32)]` is refused at 113 because the
    language has no `#[align]` (D-020), triaged through PLAN 5.2 with its acceptance at `9126350`
    checked for a silent no-op.
- **S67 — the author's go** (the brief's section 1, step 7), as the dispatch relays it. Quoted
  verbatim, all three parts:
  - management_0's recommendation 6, as put to the author at 07:28:59 on 2026-10-15:
    > "6. **Fuzzer re-baseline (M12):** run it on the Team seat after 113 lands. It needs your go to switch to LLVM 20.1.8, because the fuzzer's plan forbids changing LLVM without your word. This independently re-checks 29 compiler fixes that only the compiler has checked so far. *I recommend yes.*"
  - The author's answer, 07:42:39 on 2026-10-15, from management_0's transcript:
    > "great work. i just got back form the school. I just finished looking over the questions and from the best i can tell all the recommendations look fine to me. Lets go with those."
  - The mapping, as management_0 gives it:
    > - (i) LLVM 20.1.8 is covered in so many words.
    > - (ii) HUNT3 is covered by "after 113 lands", which is the brief's §2 "main after 113": HUNT3 is origin/main at your fetch, with 113 on it. The go never names HUNT3; this is management's reading of its own recommendation, and S67 says so.
    > - The go does NOT cover the e50eaf4 fallback. If 113 is not on origin/main at your fetch, STOP (brief §2, "If neither holds").
    > - The go does not name the apt.llvm.org prefix ~/.local/llvm-20.1.8, so never use it (brief §3).

  So (i), LLVM 20.1.8, is the go's own words. **(ii), HUNT3, is management's reading of its own
  recommendation**: the go never names HUNT3. The go does not reach the `e50eaf4` fallback, nor the
  machine's apt.llvm.org prefix, and neither is used.
- **S68 — HUNT3 is `0c0f5a3`**, the compiler's `origin/main` at this session's fetch (16:43 EDT), with
  landing 113 on it (M12 section above). It carries landings 112 and 113, and not 114 or 115. Its
  ladder row is not in its own NOTICES: rows 112 and 113 carry no digests. The row checked is the
  workbench BOARD's transcription of notice 113's rows "at `0c0f5a3`", the same source the repin
  inventory took landing 111's row from.
- **S69 — the branch is `local-m12` of the Team seat's clone**, `git switch -c local-m12 --no-track
  origin/main` at `d44dfe3`. `--no-track` keeps a bare `git push` from ever reaching `main` (S47).
  Every push is `git push origin local-m12`; `nitpick-fuzz_2` reviews and merges. The clone's
  `origin` is GitHub over SSH, which carries the push credentials, so no `set-url`.
- **S70 — two LLVMs, each named on every runner.** `.work/llvm-20.1.2` links `/usr/lib/llvm-20`
  (20.1.2, S48) for the baseline, HUNT2 and the shakedown. `.work/llvm-20.1.8` is the 20.1.8 release
  tarball (section 3), for HUNT3 and the LLVM control. Every runner gets `--llvm`, and no
  `.work/llvm` is made, so a runner run without `--llvm` fails rather than silently picking one.
- **S71 — the landing-103 spelling, `fixed uint8[]` for `string_bytes`'s result, is its own commit
  before any HUNT3 run** (the brief's section 4; 8.3's precedent). It is three generator lines and
  53 lines in 48 hand-written programs. S36's list for M10 gains one text change after the first run:
  `t07_bytes_view_bounds`, `uint8[]:b` → `fixed uint8[]:b`. That is a spelling of the program's own:
  the item is about the view's bounds check, not the binding's qualifier, and its expectation `run:94`
  stands. One spelling serves all three compilers; the shakedown checks it is neutral at `c3bdae2` and
  `9126350`. Not re-spelled: M11's six generated programs that bind a plain `uint8[]`, and the claims
  that pass a view to a plain parameter or return one (`gen/m11_claims/`, Option C's).
- **S72 — `gen/compare.py --grid9`, additive (S28's practice).** No comparer existed for the widened
  grid. The option reads `cells9.jsonl`/`classified9.jsonl` in both directories and writes
  `MOVES9.md` in the new one; its key adds the leak observer's heap words to M2's (npkc rc, codes,
  -O0, -O2). It applies none of M8's rules, so every moved cell is listed. Without the option the
  script behaves exactly as before, which was checked byte for byte.
- **S73 — `gen/compare_runs.py`, a claim-by-claim comparer for M10 and M11.** None existed. It keys
  by `id` and compares npkc, codes, O0, O2, `sh`, verdict, kind and `heap_O0`/`heap_O2`, a field
  absent from both being equal. It lists every changed id and every one-sided id, prints the totals,
  and writes nothing; a listing worth keeping is redirected into `results/<commit>/`.
- **S74 — F-049, a candidate the workbench verifies (PLAN D6).** The M12 brief's section 9 takes an
  unexplained move through M5's five steps. The 24 `pick_own` cells are explained by landing 74
  (bisected, S23), but what 74 left is a refusal of a legal program, so they are taken through the
  five steps as a finding, numbered on from F-048 as M11's state note says. Its programs are written
  by hand in F-009's form, as M9 wrote its probe-found shapes, because `gen/minimize.py` keeps only
  npkc's exit and the legs, and a refusal minimised that way can keep any refusal at all.
- **S75 — `gen/m11_rows.py` gains `NOTES`, additive.** FZ-7 puts a correction pointer in F-031's
  `ROWS.md`, which `gen/m11_rows.py` writes. The group's heading is the triage text, which also feeds
  `m11/RESULTS.md`, and FZ-10 requires that file to move by its note only. So the pointer is a note
  keyed by the group's text and printed under it; every other `ROWS.md` is written as before.
- **S76 — M13 is the initialisation and pointer-store grid, with the -O2 leg as the observer, on
  `nitpick-fuzz_2`'s brief** `/home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs/fuzz-m13-brief-2026-10-15.md`
  (536 lines, sha256 `2d09692a1604f3d4bae83d93613398df4de3692b558e91c0b30cdbebe6e6a91d`, read by
  `sha256sum` at 04:09 EDT on 2026-10-21; the Team copy
  `/home/randy/Team/META/nitpick-fuzz/briefs/fuzz-m13-brief-2026-10-15.md` gives the same), READY by its
  final check. PLAN.md ends at M11 and M12 was S66's choice; this brief is the next one (its Option B).
  PLAN.md is not edited (rule 9). The session is the brief's one worker, dispatched on the Team seat by its
  manager, Ailp-team_13, on 2026-10-21 at 04:09, on management_1's word ("M13 now, in lane 2, as booked,
  from its ready hand-off"): no sub-agents, at most 4 jobs. `nitpick-fuzz_2` reviews `local-m13` and
  merges it, and verifies every candidate first (PLAN D6). The dispatch carries five notes from
  `nitpick-fuzz_2`, each binding:
  - (a) landing 117 (D-353, DEF-236 (a)) is in HUNT4: the housekeeping updates DEF-236's bullet, measured
    by one compile of `m11/programs/as0062.npk` at HUNT4 (HUNT3 gave `EMIT-002`); `m11/` is not touched;
  - (b) `main` moved to `581c091`, a wording-only fix to `CLAUDE.md` and `README.md`; `local-m13` branches
    from it;
  - (c) landing 119 is D-355 (ii), its code taken from HUNT4 by name; at the close, the DEF-250, DEF-251
    and DEF-252 rows are updated from the three seeds' HUNT4 measurements, labelled with HUNT4's sha,
    DEF-251's naming 115 (i) and 119 (ii); `m11/` is not touched;
  - (d) landings 118–121; in grid13 B, for the `wild T->` local, the dereferencing callee's parameter is
    declared `wild T->` (as `dalloc`'s is `wild any->`), so the cell stays in wild context; a cell that
    still draws `TYPE-097` at HUNT4 is D-361 working, explained by 121 and listed;
  - (e) three of `nitpick-fuzz_2`'s readings, not measurements: F-049 read by hand against `VERDICTS.txt`
    at HUNT4 (§8's loop skips it); MOVES12 row 44's 24 M9 cells should leave `MOVE-001` at 132; F-029's
    `ctl_k3_int64_buffer_refused` should move from `PARSE-002` to `PARSE-001` at 136.
  Every prediction in those notes is `nitpick-fuzz_2`'s reading of the files; every code, verdict and
  move here is taken from HUNT4 by measurement.
- **S77 — the author's go** (the brief's §1, step 6), as the dispatch relays it. Quoted verbatim:
  - the author's message of 2026-10-15 21:00:54 EDT, relayed by management_0:
    > "i rand the shell script and also approve the two points"
  - what it answers, as `nitpick-fuzz_2`'s hand-off gives it (21:11:49 on 2026-10-15): (i) HUNT4 = the
    compiler's `origin/main` at your fetch; (ii) LLVM 20.1.8 for HUNT3 and HUNT4 in M13. "The shell
    script" is an unrelated settings step: A2's `apply.sh`, run at 21:00:34.
  - This is the recorded go that §1 step 6 looks for. It names (i) and (ii).
- **S78 — HUNT4 is `c72639f`** (`c72639f2332208649309b91796d6f173d19a64d2`), the compiler's `origin/main`
  at this session's fetch (04:11 EDT on 2026-10-21), landing 137. It carries landings 114 to 137 (the M13
  section lists each), many more than the brief, written at 116–121, foresaw; the brief provides for that
  (§2 records each, §8 explains each move by its landing). D-355 (ii) is landing 119, `TYPE-096`. Its
  ladder row is the workbench BOARD's "THE BASELINE NOTICE 138 MUST QUOTE" (notice 137's rows at
  `c72639f`), which its `npkc.ll` and `npkrt.o` equal.
- **S79 — the branch is `local-m13` of the Team seat's clone**, `git switch -c local-m13 --no-track
  origin/main` at `581c091` (S47, S69). Every push is `git push origin local-m13`; `nitpick-fuzz_2`
  reviews and merges. The clone's `origin` is GitHub over SSH, which carries the push credentials.
- **S80 — every runner runs with `TMPDIR` in the session's scratch** (`/home/randy/Team/TMP/M13/tmp`).
  `gen/run.py`, `gen/snip.py` and the other runners make their working directories with Python's
  `tempfile`, which reads `TMPDIR`, so nothing of M13's lands in `/tmp`. A program runs under `env -i`,
  so it never sees the variable: no verdict can depend on it.
- **S81 — HUNT2 (`9126350`) is not run in M13** (the brief's §2). M12 re-baselined at HUNT3, and HUNT2's
  records stand. M13's compilers are the baseline `c3bdae2` under 20.1.2 (M5 step (d)), HUNT3 `0c0f5a3`
  under 20.1.8 (the class before 114 and 115) and HUNT4 under 20.1.8 (the hunt).
- **S82 — §4's probes run at HUNT4 and HUNT3, both legs, under 20.1.8, never committed.** They live in
  `.work/probes13/<name>/<name>.npk` (one directory each, so `gen/snip.py`'s copy of a probe's directory
  is the probe alone), run by `gen/snip.py`'s `build_and_run` at most 4 at a time under the lock. Their
  spellings and codes are summarised in the M13 section; the probe results recorded there were measured,
  each at both compilers.
- **S83 — grid13's failsafe names all 31 identities of HUNT4's prelude.** The brief takes the failsafe from
  `gen/m10.py`'s TRAPS so that `(*)` (99) is reached only by a garbage argument, and asks that an identity
  missing from TRAPS get a code from 118 up. HUNT4's prelude declares 31 identities, the same 31 names as
  HUNT3's and HUNT2's: TRAPS's twenty and eleven M10 left out, which S44 coded for M11 (`StaleHandle` 100,
  `DeadlineExceeded` 101, `ChannelClosed` 102, `DriverLeak` 103, `IoEof` 104, `WouldBlock` 105,
  `Interrupted` 118, `NotFound` 119, `Exists` 120, `CrossDevice` 121, `BadPath` 122). None is new since
  M10, and 118–122 are S44's already, so no new code is made: grid13 arms all 31 with their existing codes
  (exactly `gen/m11lib.py`'s TRAPS, M11's failsafe), which is what makes `(*)` a garbage argument's alone.
  A channel cell's failed `send` or `recv` raises `ChannelClosed` (102) by `?!`; grid13 has no user error.
  No fall-through sentinel (D-013): every template declares its helpers before `main` and `failsafe`
  directly after it, the `null_store` seed's layout.
- **S84 — grid13's codes**, the brief's table with S83's arms: 0 success; 12 a value read back that is not
  the one written; 13 a zero read where a non-zero value was written or where nothing was; 14 a `NULL` test
  after a dereference that took the null branch; 21–25 E's view (the original, the new value, vacant,
  another live value, the reuse sentinel); 70 the free poison as an observation; 170 the poison byte as the
  exit (the DEF-252 seed); 91–98 and 106–117 TRAPS; 100–105 and 118–122 S44's; 99 `(*)`. A helper passes
  its code to `main`, which exits with it.
- **S85 — expectations from rulings, written in the generator before any run.** Each cell's `meta.json`
  carries `expect`, `expect_codes`, `expect_exit`, the rule's text and its source at HUNT4: D-211 with its
  landing-114 note (`TYPE-055`), TYPE_REFERENCE §26 (`ASSIGN-002`), D-287 (`TYPE-086`, `TYPE-071`), D-355
  (ii) (`TYPE-096`), TYPE_REFERENCE §27 with landing 115 (`wild` `NULL` traps 107 on both legs), §11.1
  with D-355 (a `T->?` dereferenced without `??`/`??!`/`?.` is refused: `TYPE-007`, the code §4's probes
  found, the rule naming none), D-360 (`??!` on an empty `T->?` traps its identity), D-010 (`ASSIGN-001`,
  named by TYPE_REFERENCE §27; `TYPE-027` for a struct literal), D-277, D-310, D-331 and D-007 for D (by
  form), D-004 rule 3 with landing 116 (`BORROW-002`). A settled D- ruling wins over reference text that
  has not caught up. A REFUSE cell is `refused` when every code its rule names is among npkc's.
- **S86 — the classify13 classes and compare13's contract are the brief's** (§5), in its order:
  `CRASH:npkc`; `refused` (`exp_mismatch` "codes" when a named code is missing), `OVERRESTRICT` for any SAFE
  cell, `REFUSED_TRAP`; then `timeout`, `LOUD`, `DEFECT:fallthrough`, `DEFECT:leg_mismatch`, `clean`,
  `DEFECT:uaf`, `double_free`, `segv`, `wrong_value`, `false_trap`, `other`; an accepted REFUSE cell is
  `ACCEPTED:<run class>`; `scope` comes from the index, and the `wild` cells are reported apart.
  `classify13.py` refuses to run without `cells13/INDEX.jsonl`. `compare13.py` keys a cell by (npkc, codes,
  O0, O2, class), counts a one-sided cell as `MISSING:old` or `MISSING:new`, and exits 1 when anything
  differs.
- **S87 — the axes as written, with these spellings and one addition.**
  - A: `const` is dropped with its reason (no declaration form since 1.4.2c; 99 combinations in
    `SKIPPED.txt`); `fixed atomic<int64>` and a channel with an initialiser are skipped (no constant of the
    type); the channel is `Channel<int64, 1i32, 4i64>`; "pub" is `pub T:g;` with no initialiser.
  - B: each place holds `NULL` (the `T->?` place `NIL`); the parameter place is a helper `runp` called with
    `NULL`; the `wild` local's dereferencing callee takes `wild T->` (note (d)). **Added:** `unwrap_trap`,
    `p ??! Unreachable` at the `T->?` place (2 cells, TRAP 95 by D-360), the Optional's third accessor,
    landed at 120 after the brief was written; the other places skip it.
  - C: "a struct literal missing a field" is `W{ a: 1i64 }` for `struct:W = { int64:a; T:f; }`, and "an
    array declared with no initialiser" is `T[4]:arr;`, so every type meets every place; each REFUSE cell
    has a twin (O `<o>_da`) that assigns on every path; a run-time condition keeps the assigning branch,
    arm or loop untaken, so an accepted read meets the unassigned value.
  - D: `x` is 1 for a shift and 5 for a division; the run-time form passes both operands through the
    identity functions; the unsigned types skip the negative operand and negation (`TYPE-008`).
  - E: the holders are landing 116's own, `Cursor` (a write-once view field, re-seated whole) and `Seat`
    (`(fixed uint8[]):src`, a field written again); `ra` and `rs` read the view through `obs_v` (21–25, 70).
- **S88 — the seeds are embedded in `gen/grid13.py`**, byte for byte, so `cells13/` regenerates on any
  machine. The generator refuses to write if an embedded text's sha256 is not the recorded one, and
  `--selfcheck` also checks each source's sha256 where the source exists.
- **S89 — the templates were compiled as probes before the commit, for spellings only.** A covering set
  of 89 generated programs (each section's T, P and O values at least once, a SAFE one where there is one),
  each copied to `.work/probes13/r_<id>/` under its own module name and run as §4's probes at HUNT4 and
  HUNT3. No expectation was set or changed from them, and none needed a spelling change: every SAFE
  template ran 0/0 at both compilers, every REFUSE template drew its code at HUNT4, and the departures were
  the faces §4 had already measured (DEF-250's and DEF-251's at HUNT3, `??!` absent at HUNT3, the dead
  `wild` load at HUNT4).
- **S90 — the triage's findings are F-050, F-051 and F-052, numbered on from F-049** (the brief). Each
  candidate goes to `nitpick-fuzz_2` for D6 verification before anyone else sees it. F-051 is scope wild and
  reported apart as the check of DEF-251 (i), outside `CLAUDE.md`'s definition and §9's classes. F-052 came
  from §4's probe, not a HUNT4 grid cell: a compiler defect found is recorded, never worked around (rule 8),
  and grid13 sees it at HUNT3 and the baseline. C's six `OVERRESTRICT` are recorded as a wrong expectation
  of mine (D-004 rule 3 is deliberately strict) and no finding; their expectation is not changed (S36,
  S45). The triage probes ran the baseline under its own 20.1.2; `gen/run_findings.py`'s records ran it under
  20.1.8, as the regression leg's did.
- **S91 — §10, the optional M11 re-spellings, is not done.** It edits `gen/m11_claims/` and regenerates
  `m11/programs/` with `gen/m11.py`, and dispatch notes (a) and (c), binding, both say "Don't touch m11/"
  (the Team seat's readings repeat it). The ten re-spellings (`me0119`, `me0119b`, `me0183`, `md0042`, the six
  BUILD scripts' `triple` and `datalayout`) stay with `nitpick-fuzz_2` for Option C.
- **S92 — M14 is the S-140 class (F-051 R1), a narrow run, on `nitpick-fuzz_4`'s brief**
  `/home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs/fuzz-m14-brief-2026-10-23.md` (480 lines, sha256
  `291db53fd5bc85df45f07aaa72b6f23514b67cae1311c92392160ed9a7f8cf6f`, read by `sha256sum` at 03:01:00 EDT on
  2026-10-25), the final after management_2's verify and re-verify (v2 READY; the final adds the re-verify's five
  non-blocking slips, marked "(final)"). It comes from S-140, the author's ruling R1 on F-051, and management_2's
  funding at its re-size of 2026-10-23 23:00:26. PLAN.md ends at M11; M12 and M13 came from briefs like this one,
  and PLAN.md is not edited (rule 9). New findings are numbered from F-053. The session is the brief's one worker,
  dispatched on the Team seat by its manager, Ailp-team_19, at 03:00:18 EDT on 2026-10-25, in lane 2: no
  sub-agents, at most 4 jobs. The fuzzer's manager, `nitpick-fuzz_4`, reviews `local-m14` and merges it, and
  verifies every candidate first (PLAN D6), each reported through the dispatcher. **The lock:** library work
  outranks the fuzzer on the Team seat's harness lock (management_0, 2026-10-15 13:23:16, as the dispatcher's
  correction of 03:03:25 relays it), so each build, canary batch, probe batch and runner takes it alone, with the
  bookkeeping between; on `flock`'s exit 75 the same command is run again, at most six attempts in a row.
- **S93 — management_2's go for M14** (the brief's §1, step 7), as the dispatch relays it, verbatim as it reached
  the Team seat at 23:41:14 on 2026-10-23:
  > management_2 -> Ailp-team_18 (copy: nitpick-fuzz_4), 23:41:04 by `date`: **S93, re-sent to you directly.** It first went to Ailp-team_17 at 23:25:03, before your takeover, and _17 is now closed.
  >
  > **S93, management's go for fuzz's M14:** the F-051 R1 run (PERMITTED:S-140), at HUNT5 = the compiler's origin/main at the fetch, under LLVM 20.1.2.
  > - The rule is the author's (S-140 R1, D-364, Q56). The run was funded at the re-size (Fri 23:00:26).
  > - **Brief, final:** /home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs/fuzz-m14-brief-2026-10-23.md, 480 lines, sha256 291db53fd5bc85df45f07aaa72b6f23514b67cae1311c92392160ed9a7f8cf6f.
  > - **Verified:** v2 (dab19659...1392) is READY by the credits re-verify, report MANAGEMENT/credits/out/fuzz-m14-brief-reverify-2026-10-23.md. The final adds only that report's five non-blocking slips, marked "(final)" (six markers). The first verify's report is beside it.
  > - **Size:** one short Team session, ~60-100 min and 250-400k tokens, with M14v after.
  > - **Placement:** after Saturday's gate, not before 12:30, at your choice under the Sun 03:00 line of 65 %, or at Sun 03:00:30 if the line won't hold it.

  The dispatch adds: "Those words stand as the go for HUNT5 = the compiler's origin/main at your fetch.
  management_2 asked for no author's go. No LLVM go is needed (S95)." This is the recorded go §1 step 7 looks for.
- **S94 — HUNT5 is `249eae9`** (`249eae91559bfc1e3b8a17b12286c21108e4215a`, 2026-10-24 21:57:10 -0400), the
  compiler's `origin/main` at this session's fetch (03:02:58 EDT on 2026-10-25): landing 161. It carries landing
  155 (`02856cf`, the brief's floor) and §27's S-140 sentence, and past 148 it carries landings 149–161, each
  listed with its DEF and D- ids in the M14 section (149 DEF-277; 150 DEF-276; 151 D-363's R1; 152 DEF-278,
  DEF-281; 153 DEF-282, DEF-285; 154 DEF-287; 155 DEF-288, DEF-290; 156 DEF-296, DEF-289's first face; 157
  DEF-289's second face; 158 DEF-300; 159 DEF-297, DEF-301, DEF-303; 160 DEF-302; 161 DEF-305). Its `npkc.ll`,
  `npkc.o`, `npkrt.o` and `builder.o` equal notice 161's ladder row, the workbench BOARD's "THE BASELINE NOTICE 162
  MUST QUOTE".
- **S95 — LLVM 20.1.2 throughout, PLAN.md:10's own pin; HUNT3 and HUNT4 are not run** (the brief's §2). M12 and
  M13 ran their HUNTs under 20.1.8 on the author's per-milestone go (S67, S77); M14 returns to PLAN's pin, which
  needs no go. `.work/llvm-20.1.2` (the machine's `/usr/lib/llvm-20`, S48, S70) prints `20.1.2`, and every M14
  runner names it. M14's compilers are the baseline `c3bdae2` (the narrowness control: before landing 115 a used
  load gave 107/12) and HUNT5 (the run). HUNT4 (`c72639f`) and HUNT3 (`0c0f5a3`) are not run: no compare with
  grid13 is needed, and the rule under test dates from landing 142. Reported by the brief, not measured here: the
  manager's build of HUNT4 under 20.1.2 gave F-050 … F-052's verdict lines identical to M13's 20.1.8
  `VERDICTS.txt`, with `npkc.ll` and `npkrt.o` byte-identical, and its builds of landings 141–148 under 20.1.2
  matched the compiler's ladder rows for `npkc.ll` and `npkc.o`.
- **S96 — M13's box 10 is closed unworked** (the brief's §1, step 5; M13v's finding (10)). The box, "the M11
  re-spellings — not done", was the file's only unticked one, and it is no work to resume: S91 closed it unworked,
  since dispatch notes (a) and (c) kept `m11/` untouched, and M14 does not touch `m11/` either. Commit M14 (1b)
  changes its `[ ]` to `[-]` and appends the reason, so the resume rule ("resume from the first unticked box")
  cannot send a later session into `m11/`. The ten re-spellings stay with the fuzzer's manager for Option C.
- **S97 — §4's probes run at HUNT5 and the baseline, both legs, under 20.1.2, never committed; the templates for
  spellings only.** They live in `.work/probes14/` (probe files only, so `gen/snip.py`'s copy of a probe's directory
  holds probes alone), copied, never run in place, and each batch runs under the lock. The first batch is the
  manager's 22 probes at landing 148. The second is 25 generated grid14 templates, copied under their own names,
  that carry every spelling the first batch had not compiled at HUNT5 (the struct forms and the twins' unused
  bindings, §4's "still to confirm"), as M13 compiled its templates as probes (S89). They were run for their
  spellings: every expectation was written in the generator from §27 before them, and none was set or changed from
  their exits. All compile at HUNT5, so `RESPELL` and `TWIN_SKIP` stay empty.
- **S98 — grid14's sections, as the brief's §5 writes them, with these spellings.** S 7 (F-051's four programs read
  from `findings/F-051-wild-dead-load-legs-disagree/` and checked against their sha256, so `cells14/` regenerates
  from the repository; the twins by two substitutions, each asserted once), U 40, W 20, K 30 and B 12: 109 cells, 0
  skipped. Ids are `m<nnn>_<section>_<T>_<P>_<O>[_<after>]`, numbered over the whole space so a skip would not
  renumber them; T is `int64` or `struct` (the struct S, read as `v.a`); `after` is a meta field of U and W; W's O is
  `twin`; B's `boundary` is its O. A helper passes its code back: `runp` (the `param` place) with `pass`, and K's
  `callee` through `func:rd = int32(int64:x)`, q09's form; B's `untaken` names `main`'s parameter `argv` (one
  asserted substitution of grid13's `_~argv`), every other cell keeps `_~argv`. The expectations come from §27's
  bullet at HUNT5 before any run (PLAN 9.6) and are not changed after it (S36, S45): U, K, B and the four seeds TRAP
  107, the twins SAFE with the exit their own text gives. `s140` is set by the construction alone.
- **S99 — the class `PERMITTED:S-140` and its order, in `gen/classify14.py`.** classify13's classes and order, with
  the brief's five changes: the twins' expected exit (1); `PERMITTED:S-140` after `timeout`, `LOUD` and
  `DEFECT:fallthrough` and before `DEFECT:leg_mismatch`, on the generator's flag and conditions 1–5 only, a flagged
  cell without its twin's record an error (2); `--selftest` (3); `SUMMARY14.md` and `classified14.jsonl` (4); and
  `--against13`, writing nothing, which re-derives conditions 1–5 itself (5). It wraps classify13's `run_class` for
  every class but the new one, and imports `classify` for the re-class; `exp_mismatch` is copied. One addition:
  `classified14.jsonl` also carries `after`. The live control for condition (c) is `--against13`'s third group.
- **S100 — the triage's finding is F-053, numbered from F-053** (the brief). B's ten 107/0 cells are one candidate,
  "a load through a `wild` `NULL` pointer whose value the program uses is sunk or deleted at -O2", where §27 promises a
  fault at both legs: the -O2 IR shows a sink in one form and a deletion in four, which I read as one cause (the load
  has no side effect for the optimiser to keep). Its faces are B's five forms, each at `int64`; its controls K's
  `cmp` (107/107, the case an implementation deleting every load gets wrong), the permitted dead load (D-364's
  reference) and B's `deadadd` (107/107). It is classed as F-051 was, reported apart as the check of §27 (D-364),
  scope wild; whether §27's sentence or the lowering changes is the compiler seat's and the author's, and the README
  argues for neither. `gen/minimize.py` cannot keep a read whose deletion leaves the verdict unchanged, so four
  reproducers keep their bodies whole under its failsafe, as the README records. The candidate goes to the fuzzer's
  manager for D6 through the dispatcher.
- **S101 — M15 is the DEF-296 family, on `nitpick-fuzz_5`'s brief**
  `/home/randy/Workspace/REPOS/nitpick-fuzz/.work/briefs/fuzz-m15-brief-2026-10-28.md` (387 lines with a trailing
  newline, sha256 `e0e6a554e07694be1ace88c45e7108c1d453d61a59e2c846e47721fa45339b84`, read by `sha256sum` at 23:13:22 EDT on
  2026-10-28), verified READY by management_4 and released by `nitpick-fuzz_5` at 23:02 on 2026-10-28 (S102 quotes the
  release). It comes from management_3's GO for the week (S102), which makes the DEF-296 family M15, run on the Team as M14
  was. PLAN.md ends at M11; M12, M13 and M14 came from briefs like this one, and PLAN.md is not edited (rule 9). New
  findings are numbered from F-054, decisions from S101. The session is the brief's one worker, dispatched on the Team seat
  by its manager, Ailp-team_24, at 23:12:50 EDT on 2026-10-28, in lane 2: no sub-agents, at most 4 jobs. The fuzzer's
  manager, `nitpick-fuzz_5`, reviews `local-m15` and merges it, and D6-verifies every candidate first, each reported
  through the dispatcher. The brief's `.work/briefs/` paths are the Workspace clone's, read there with read-only tools
  (the dispatcher's ruling, in the Log); the copies M15 takes from them are made with `cat` into this clone and checked
  against their `SHA256SUMS`. **The lock:** library work outranks the fuzzer on the Team seat's harness lock, so each
  build, canary batch, probe batch and runner takes it alone, with the bookkeeping between; on `flock`'s exit 75 the same
  command is run again, at most six attempts in a row (the dispatcher's limit), and a sixth 75 is a §9 stop.
- **S102 — management_3's GO for the week** (the brief's §1, step 7), as the dispatch relays it, verbatim as it reached
  the Team seat at 20:11:29 on 2026-10-28:
  > management_3 -> Ailp-team_23, Wed 2026-10-28 20:11:21: GO for the Team's week (it began Wed 03:00). This is the slot message you were waiting on.
  > - **Lane 1:** T7fix3 (sonnet) in the order settled at Sun 22:40:44, plus O-N42's one-line rename if it fits. Then T7v5, scoped to it. libs_27 rules on it before 0.0.0's first execution dispatch.
  > - **Lane 2:** parse 0.0.2 as a new chain (libs_25's GO of Sun 10:45 stands).
  > - **Diogenes' code part** on team/diogenes-0.0-gate: U7–U9, `--max`, and D8bv's findings 1–4, 7 and 8 (docs, help text and tests, plus a verifier). You write its brief. Put management's note in it: M6b passed by 0.1 s, so get the 75 s bound's derivation and the design's worst case. If the worst case can reach 75 s, fix the mechanism or the bound, so the gate isn't a coin flip on a re-run.
  > - **M15** (fuzz's DEF-296-family generator), run on the Team as M14 was. Its Max side is fuzz_4's brief and review, so agree the slot with nitpick-fuzz_4 (`uds:/run/user/1000/cc-socks/1268635.sock`).
  > - **Budget:** the Team week is ours to spend in full. Pace ≈ 14 % a day (≈ 85 % by Tue 03:00), and start nothing new from 98 %. Last week's estimates ran 1.5–2× low, so size from that. Each chain's Max-side review (libs_27, diogenes_3, fuzz_4) costs Max points, so batch your lines to them.
  > - **Lines to management:** your order and lane plan with a /usage reading, then each DONE, PASS, FAIL or stop.

  The dispatch adds: "Those words stand as the go for HUNT6 = the compiler's origin/main at your fetch. No LLVM go is
  needed (S104). The GO names nitpick-fuzz_4 for the slot; the fuzz seat has been nitpick-fuzz_5 since 20:19:40 on
  2026-10-28. The management seat has been management_4 since 21:51, and nothing in the plan or the lines changed." This
  is the recorded go §1 step 7 looks for. **Beside it, the release** of HUNT6, REG155, the LLVM, the branch and the
  expectations table: `nitpick-fuzz_5`'s word to the Team seat, verbatim as it arrived at 23:02:44 on 2026-10-28:
  > [nitpick-fuzz_5 → Ailp-team_24, 2026-10-28 23:02 EDT] M15 is READY — go. (brief verified READY by management_4, no further credits round.)
  >
  > Brief: .work/briefs/fuzz-m15-brief-2026-10-28.md
  > sha256: e0e6a554e07694be1ace88c45e7108c1d453d61a59e2c846e47721fa45339b84  (387 lines, trailing newline — verify this before you start)
  >
  > Run M15 exactly per the brief. Parameters:
  > - HUNT6 = your `git fetch origin && origin/main` at fetch time (≥163 = 1480ca8). NB from management_4: harness 164 (3adfc05) lands green ~00:15 EDT; if your fetch is after that, HUNT6 carries 164 — brief §2 handles it (record it from NOTICES.md, compare against its own ladder row, or record the digests if BOARD.md has no row yet).
  > - REG155 (recall leg) = 02856cf.
  > - LLVM 20.1.2 — your clone's `.work/llvm-20.1.2/bin` (brief §5 gate S104 must print 20.1.2 or STOP).
  > - branch: local-m15.
  > - The single source of measured verdicts is the expectations table: copy `m15-expect/m15_expect.tsv` + `m15_expect_check.py` into `gen/` (brief §5). The checker must print "104 rows, 0 mismatches" before any grid run.
  >
  > When the grid + recall gate run completes, report back and I'll D6-review on my own builds. If you can't read that brief path on your side, tell me and I'll ship the file to you.
- **S103 — HUNT6 is `1480ca8`** (`1480ca81aa4d9d82976149f7f6ae5e44b2c5c640`, 2026-10-26 14:05:02 -0400), the compiler's
  `origin/main` at this session's fetch (23:19:57 EDT on 2026-10-28): landing 163, DEF-306 + DEF-308. It carries landing
  156 (`a5693a6`, DEF-296) and is landing 163 itself, the brief's floor. No landing lies past 163 (no commit past it, no
  `| 164 |` row in its NOTICES), so there are none to record. From REG155 it carries 156 (DEF-296, DEF-289's first face),
  157 (DEF-289's second face), 158 (DEF-300), 159 (DEF-297, DEF-301, DEF-303), 160 (DEF-302), 161 (DEF-305), 162 (DEF-304)
  and 163 (DEF-306, DEF-308), as the M15 section lists. Its `npkc.ll`, `npkc.o`, `npkrt.o` and `builder.o` equal notice
  163's ladder row, the workbench BOARD's "THE BASELINE NOTICE 164 MUST QUOTE". `.work/H6.full` is written once, so a
  resume never re-points a recorded run at a newer `origin/main`.
- **S104 — REG155 = `02856cf` is the regression leg; `c3bdae2` is not run; LLVM 20.1.2 throughout** (the brief's §2).
  REG155 (`02856cfc72463f105da70bd9c23c7f2cc1bf8151`, landing 155: DEF-288 and DEF-290) is the compiler before DEF-296's
  first fix (156), where the family is a live use-after-free: the recall leg. `c3bdae2` cannot exercise the family: the
  manager measured `p02_pp_pl_dir`, `q05_pp_tl_dir_in` and `q17_pp_fld_cres` each `npkc=1 NITPICK-PARSE-001` there
  (`.work/briefs/m15-c3bdae2-parse.log`: the pointer-local, slice and `fixed uint8[]` syntax postdates the baseline), so it
  is not run, nor are HUNT3, HUNT4 and HUNT5. The LLVM is PLAN.md:10's own pin, which needs no go: `.work/llvm-20.1.2`
  (the machine's `/usr/lib/llvm-20`, S48, S70) prints `20.1.2`, and its `opt`, `llc`, `ld.lld` and `clang` are 20.1.2; the
  manager's probes ran under the same toolchain (`.work/briefs/m15-llvm-versions.log`). REG155's `npkc.ll`, `npkc.o`,
  `npkrt.o` and `builder.o` equal notice 155's ladder row, "THE BASELINE NOTICE 156 MUST QUOTE".
- **S105 — grid15's sections** (the brief's §5). A cell is one road R (20), one write W (12, `cresf` among them),
  one placement B (`same`, `inner`) and one provenance V (`pp`, `twin`, `lo`): 1 440 combinations. Emitted: every `pp`
  key of the expectations table, 42 (section R: the 20 roads with `dir` in one block and the 12 indirection roads
  `pl pld plw pf tl sle lst cpl cslv mpl cps cpp` inner; section W: `fld` with the ten writes other than `dir`, in one
  block), each with its twin, 84; the rest, 1 356, in `SKIPPED.txt` with their reasons (`lo` deferred, the brief's
  Deliverable 1; `cresf` `TYPE-024`, measured in §4; the write-side sweep on `fld` only; no inner placement for `bare
  fld rge cad csl cbv cbp mth`). Section S, 16: the eight DEF-296 faces and the six candidates embedded byte for byte
  with the manager's `SHA256SUMS` lines, F-050's two holes read from their committed directory against their sha256.
  The readings: **(a)** each cell's text is the manager's spelling (§4), the template `f(S->:p)` storing the view,
  writing the pointee and passing grid13's observer's code to `main`, grid13's failsafe after `main`; **(b)** `expect`
  is the rule's (REFUSE for a `pp` cell and a seed, SAFE with exit 0 for a twin), `expect_codes` and `reg155` are the
  table's (the H6 row's code when it refuses, else `NITPICK-BORROW-015`; the REG row's verdict), written before the
  first run; **(c)** `rule` is the D-325 paragraph at HUNT6 (MEMORY_REFERENCE.md:269–284, its lines joined by one
  space; `--selfcheck` re-reads it from `1480ca8`), and `source` names the governing landing by the registry's shapes
  at HUNT6, read and not measured, as each `source` says (the brief's 156, 154, 116 and 160, refined where the
  registry names the road: 157 for a slice parameter, 158 for a range, DEF-298 and DEF-299 OPEN); **(d)** a seed's T,
  P, O and observer are "seed" (the brief's §5 seed line, which I read over its general "observer = exit"), and so are
  its R, W, V and B; **(e)** ids are `n<NNN>_<V>_<R>_<W>_<B>` for the grid and the program's own `mod:` name for a
  seed; T, P and O carry V, R and `<W>_<B>` for `gen/run.py`, and every meta also carries `key` (the table's) and
  `pair` (the twin's pp cell, and back).
- **S106 — the recall gate, its selftest, and the finding rule** (the brief's §5 and §6). `gen/classify15.py
  --recall` runs every check (COMMIT, COVERAGE, SEED-RECALL, LEAK-RECALL, SILENT-PASS, TWIN, CODE-H6, CODE-REG,
  UNANCHORED, REGRESSION), prints each one's result with its count and a `TAG` line for each failure, lists the
  findings, and exits 3 on REGRESSION, else 1 on any tag, else 0. The twin is the only gated control. My readings:
  **(a)** SILENT-PASS, CODE-H6 and CODE-REG are asked of every hazard cell, the seeds with the `pp` cells (the brief
  names `pp` cells; asking the seeds too can only add a failure, and the table predicts none); **(b)** a record whose
  id is not in the index, or an index id with no record, is COVERAGE's alone, so each check fires by itself; **(c)**
  the brief's selftest "a twin is ACCEPTED:…" is a twin not clean (a SAFE cell's class has no `ACCEPTED:` prefix):
  70/70 at REG155, refused (OVERRESTRICT) at HUNT6. `--selftest` builds its records in memory with classify13's own
  `classify` and `exp_mismatch` and reads no file: 18 cases, each its exact tag set and exit code. **The finding
  rule:** a `pp` cell or a seed accepted at HUNT6 that reads the poison (ACCEPTED:DEFECT:uaf) is a use after free in
  safe code, a defect by CLAUDE.md, reported normally; it goes through §7's triage, where a road or write OPEN in the
  registry at HUNT6 is known and noted with its DEF, not filed.
- **S107 — the triage files nothing: HUNT6's fourteen accepted hazard cells are eight known-open keys** (the brief's
  §7 and P7). `cbv` and `cbp` are DEF-298 (OPEN); `cps`-inner, `cpp`-inner and `tl`-inner are DEF-299 (OPEN; `tl` by
  the brief's pre-map); `cres` is DEF-309 (OPEN); `cresc` and `cresm` are DEF-305's parameter-rooted gap (the row says
  FIXED at 161; the brief reads it as an incomplete fix, not a new defect). PLAN 5.2 (a) makes a shape whose fix is
  not in HUNT6 known, so (b)–(e) do not run, F-054 is not used, and no `findings/` directory is added. The candidates
  go to the fuzzer's manager through the dispatcher for D6, with two flags (DEF-299's letter against `tl`-inner,
  DEF-305's FIXED against `cresc`/`cresm`). No landing past 163 reached the compiler's `origin/main` by the last
  fetch, so no ADDITIONAL verdict at a later sha is recorded.

- **S108 — D6 review (the fuzzer's manager, `nitpick-fuzz_5`, 2026-10-29) and the landing-164 delta.** The fourteen
  candidate cells and the controls were reproduced independently on the manager's own builds (`.work/l163` =
  `1480ca8`, `.work/l155` = `02856cf`, LLVM 20.1.2) and agree with the committed results cell by cell, leg by leg;
  `m15_expect_check.py` reads 104/0, `grid15 --selfcheck` and `classify15 --selftest` pass, and the recall gate exits
  0 (FINDINGS 14, REGRESSION 0). Logs: `.work/briefs/m15-d6-l163l155.log`, `m15-d6-controls-l163l155.log`. Decisions:
  (a) the landing-164 delta is recorded in REPORT §16.12 as an annotation, not a measurement — M15 built nothing past
  163, and the 164 refusals are the compiler seat's record (`OPEN_DECISIONS` at `3adfc05`, read by M15v; libs_28's
  W-30), not the manager's reading; (b) `cresc`/`cresm` = DEF-305's parameter-rooted gap at 163 is the face the
  compiler registers and FIXES as DEF-311 at 164 (citing the fuzz seat's `q17`/`q19`/`q20`), with DEF-309 for `cres`
  — D6 does not adjudicate 305-vs-311 beyond citing `OPEN_DECISIONS`; (c) the landing-162 citation `c79a2c0` (the
  D-364 meta-amendment child) is corrected to the landing commit `8c4f005` in `KNOWN_DEFECTS.md` and `PROGRESS.md`
  (M15v's finding 1, verified against the compiler history at `1480ca8`). M15v's other findings (2, 3, 4, 6, 7) are
  non-blocking and need no change to the tree. `main` is fast-forwarded to M15's branch.

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
    after free through a `=> dyn` cast**; F-038, an npkc trap; F-039 (5 lower-priority
    compiler rows); F-040 (18 documentation rows); 2 known; 1 not a finding (two classes
    corrected at BUILD's clean point).
  - **BUILD.** 97 claims, 38 testable, committed before any run (`e880214`). Run 1: 37
    agree, 1 disagree, a script's own mistake. Final: 38 agree, 0 disagree. No finding.
    One observation: npkg's unknown-stage message omits `explore`.
  - **TRAITS.** 119 claims, 115 testable, committed before any run (`423a68d`). Run 1: 96
    agree, 19 disagree. 12 programs fixed. Final: 99 agree, 16 disagree. Triaged: **F-041,
    an npkc hang**; F-042 (1 lower-priority compiler row); F-043 (13 documentation rows);
    1 not a finding.
  - **VERIFICATION 1248–2351.** 131 claims, 16 testable, committed before any run
    (`4f62a49`). Run 1: 16 agree, 0 disagree. No finding.
  - **TYPE 661–1176**, part A of TYPE 661–2122 (S65). The author's go came through the
    workbench after a hold. 268 claims, 249 testable, committed before any run (`36971df`,
    the module; the files `gen/m11.py` writes from it come with the run's commit).
    Run 1: 237 agree, 12 disagree. Four programs fixed. Final: 240 agree, 9 disagree.
    Triaged: F-044 (8 documentation rows), 1 not a finding.
  - **TYPE 1177–1592**, part B (S65). 129 claims, 123 testable, committed before any run
    (`2e9f871`). Run 1: 114 agree, 9 disagree. Two scripts fixed. Final: 114 agree, 9
    disagree. Triaged: F-044 grows to seventeen rows, plus F-045 (a diagnostic that
    advises the retired `?`, found while screening the agreements).
  - **TYPE 1593–2122**, part C (S65). 178 claims, 172 testable, committed before any run
    (`a66247f`). Run 1: 147 agree, 25 disagree. Four programs fixed. Final: 149 agree, 23
    disagree. Triaged:
    - **F-047, a silent wrong answer** (a `fixed uint8[]` view written through);
    - F-048 (a `NIL` field emitted as invalid IR);
    - F-046 (three lower-priority rows);
    - F-044 grows to thirty-three rows;
    - F-026's shape and DEF-131, both fixed at `93bcb66`.
  - **M11 is done**: all fourteen references, 10 419 lines. The session stopped there, as
    11.3 says.
- 2026-10-15 (session 10, the Team seat, branch `local-m12`): **M12, the re-baseline at HUNT3**, on
  management's corrected brief (S66).
  - **(1) The start checks** passed: GitHub fetched, `main` = `origin/main` = `d44dfe3`, M11 ticked,
    the tree clean, `local-m12` new (S69). The go is S67, verbatim.
  - **HUNT3 is `0c0f5a3`**, landing 113, carrying 112 (S68). The baseline and HUNT2 were rebuilt under
    20.1.2 in 74.6 s and 72.7 s, byte-identical to the committed digests; the canaries pass at both.
  - **(2) The landing-103 spelling** (S71): `fixed uint8[]` in three generator lines and in 53 lines
    of 48 hand-written programs; `gen/m10.py` regenerated `t07` alone. The anchored grep lists only
    M11's six generated programs, left for Option C.
  - **(2b) The comparers:** `gen/compare.py --grid9` (S72, additive, checked byte for byte) and
    `gen/compare_runs.py` (S73), each tested on the committed records.
  - **(2c) The shakedown, identical** at `c3bdae2` and `9126350` under 20.1.2: M2 956/956, M9
    7 571/7 571 with the heap words, recall 25/25, M10 223/223, and the ten re-spelled findings line
    for line. No per-compiler spelling was needed.
  - **(3) LLVM 20.1.8 and HUNT3:** the release tarball fetched in S13's form (sha256
    `1ead36b3…`); HUNT3 built in 55.2 s, its `npkc.ll` and `npkrt.o` equal to notice 113's ladder
    row; the canaries pass. The LLVM control at `9126350` is identical in every record (recall, M2,
    M9 with heap words, M10, M11): 0 cells moved by the toolchain.
  - **(4) The runs at HUNT3**, in `results/0c0f5a3/` and `VERDICTS-0c0f5a3.txt`: recall identical
    to `9126350` (25/25 "once fixed"); findings 67 programs moved in 29 findings, every baseline line
    as committed; M2 0 moved; M9 0 anomalies, 393 moved; M10 218/5, 9 changed; M11 2 628/244, 95
    changed. No memory fault at HUNT3.
  - **F-049, a candidate** (S74): a consuming pick's binding re-initialised after a move cannot be
    read (`MOVE-001`), new at landing 74 (bisected); 24 SAFE cells of the M9 grid. Lower priority.
  - **(5) The move table**, `results/0c0f5a3/MOVES12.md`: 97 rows, every move explained by a
    landing or a finding id, zero UNEXPLAINED; 29 of 33 predictions ticked, the other four explained.
  - **(6) The registry rows and FZ-1 … FZ-10:** KNOWN_DEFECTS.md's DEF-227 … DEF-253 section, every
    status read and every fixed row measured at HUNT3; FZ-1 … FZ-10 applied (FZ-2's counting,
    `PLAN.md:16` and `README.md:25` left for the author); `NEWEST` rebased to `0c0f5a3`.
  - **(7) REPORT.md §13** written, with a pointer in its opening; the gate holds in every box; **M12 is
    ticked**. The session stops here (18:37 EDT), as the brief says.
- 2026-10-21 (session 11, the Team seat, branch `local-m13`): **M13, the initialisation and pointer-store
  grid**, on `nitpick-fuzz_2`'s brief (S76), dispatched at 04:09 EDT.
  - **(1) The start checks** passed: GitHub fetched, `main` fast-forwarded `d44dfe3` → `581c091`, `f31dfc6`
    an ancestor, M12 ticked, the tree clean before the switch, `local-m13` new (S79). The go is S77,
    verbatim, naming (i) and (ii).
  - **HUNT4 is `c72639f`**, landing 137, carrying 114–137; D-355 (ii) is 119 (S78). Built in 56.0 s under
    20.1.8; `npkc.ll` and `npkrt.o` equal notice 137's ladder row. The baseline and HUNT3 are M12's builds,
    byte-identical to the committed digests. The canaries pass at all three.
  - **(1b) The housekeeping:** M12v's (1), (2), (4), (6), (7) and (8) as worded edits; DEF-256's row and
    F-049's two reported facts; DEF-236 (a) fixed at 117, `as0062` `TYPE-095` at HUNT4 (note (a)).
    `gen/run_findings.py` writes no file for a finding with no programs.
  - **(2) Learn by snippet and the grid:** 130 + 51 probes and 89 template probes at HUNT4 and HUNT3
    (S82, S89). `gen/grid13.py` writes 933 cells (S 3, A 166, B 106, C 500, D 130, E 28) and skips 431 with
    reasons; `--selfcheck` passes; `gen/classify13.py` and `gen/compare13.py` tested on synthetic records.
    Committed before any grid13 run. Two probe results ahead of the runs: the dead `wild` load is 107/14 at
    HUNT4, and a callee storing into an element of an array of holders reads the poison at HUNT4.
  - **(3) The recall gate and the LLVM control at HUNT3:** the seeds flagged as §6 names them (P1); HUNT3's
    record, 933 cells (375 refused, 368 clean, 190 the class before 114–116 and `??!`); the control under
    20.1.2 moves 0 cells.
  - **(4) grid13 at the baseline and HUNT4:** HUNT4's two runs agree; HUNT4 546 refused, 377 clean and 10
    cells for triage (2 `ACCEPTED:DEFECT:uaf`, 2 wild `DEFECT:leg_mismatch`, 6 `OVERRESTRICT`); FACES13: 184
    faces moved from HUNT3.
  - **(5) The regression leg at HUNT4:** recall 25/25 as at HUNT3; findings: F-029's `ctl_k3` code (136) and
    F-049's two reproducers to 22/22 (132), nothing else; M2 0 moved; M9 24 moved, row 44's cells (132); M10 0
    changed. `MOVES13.md`: zero UNEXPLAINED, P1–P11 ticked or explained; note (e)'s three readings ticked.
  - **(6) Triage:** F-050, a callee storing a block-local view into an element of an array of holders,
    170/170 at HUNT4 (a soundness hole, DEF-252's face left by 116); F-051, a dead `wild` load deleted at -O2
    (107/14), the check of DEF-251 (i); F-052, an atomic's method through a pointer `EMIT-002` (crash / loud
    emission). C's six `OVERRESTRICT` are D-004 rule 3 working: my expectation was wrong. All three findings
    present at the baseline. §10 is not done (S91).
  - **(7) The close:** REPORT.md §14 with a pointer in its opening; KNOWN_DEFECTS.md's DEF-250, DEF-251 and
    DEF-252 rows from the seeds' HUNT4 measurements (note (c)), DEF-253's registry status, and F-050 … F-052
    as candidates; the scratch removed; the gate holds in every box; **M13 is ticked**. §10 is not done (S91).
    The work ran from 04:09 to 05:26 EDT; nothing was written from 05:25:35 until `date` read 07:49:43, an
    idle gap, so the close commit came more than 45 minutes after the one before it (05:22:49). The session
    stops here, as the brief says.
- 2026-10-25 (session 12, the Team seat, branch `local-m14`): **M14, the S-140 class (F-051 R1)**, on
  `nitpick-fuzz_4`'s brief (S92), dispatched at 03:00:18 EDT.
  - **(1) The start checks** passed: GitHub fetched, `main` fast-forwarded `581c091` → `e289864`, `e289864` an
    ancestor, M13 ticked, the tree clean before the switch, `local-m14` new. The go is S93, verbatim.
  - **HUNT5 is `249eae9`**, landing 161, carrying 155 and §27's S-140 sentence; landings 149–161 past 148 (S94).
    Built in 64.9 s under 20.1.2 (S95); `npkc.ll`, `npkc.o`, `npkrt.o` and `builder.o` equal notice 161's ladder
    row. The baseline is M12's build, its digests re-read. The canaries pass at the baseline and HUNT5.
  - **(1b) The housekeeping:** M13's box 10 `[-]` (S96); M13v's (7) (`KNOWN_DEFECTS.md`'s headings), (8) (grid13's
    count, 1 361 + 3 = 1 364) and (9) (`cbc38b9`'s commit 04:49:55 and push 04:49:57). Wording only.
  - **(2) Learn by snippet, the grid and the classifier:** the manager's 22 probes give their landing-148 verdicts
    at HUNT5, and 25 grid14 templates compile there, for spellings only (S97). `gen/grid14.py` writes 109 cells (S 7,
    U 40, W 20, K 30, B 12), skips none, and `--selfcheck` passes with condition (c) literal on 43 flagged cells
    (S98); `gen/classify14.py --selftest` passes 15 of 15, and `--against13` was tried on synthetic records with two
    wrong classifiers (S99). Committed before any grid14 run.
  - **(3) The runs:** grid14 at HUNT5 twice (0 of 109 differ) and at the baseline. HUNT5: 43 `PERMITTED:S-140`, 56
    clean, 10 `DEFECT:leg_mismatch` (B's boundary forms at 107/0); every K cell 107/107. The baseline: 31 permitted,
    the module place `TYPE-004`, K at 107/12 and 107/99. `--against13` exits 0 at both; the live control for (c) is
    the baseline's four struct `test` cells at `param` and `returned`, 107/0, `DEFECT:leg_mismatch`. F-050's holes
    `BORROW-002`, F-051 107/14, 107/0, 107/14 with its control 107/107, F-052's programs 0/0, at HUNT5.
  - **An idle gap.** After the triage's IR probes (03:29:14 by `date`, and one short IR print after them), nothing ran
    until `date` read 07:57:18: about 4 h 28 min with no command of mine and no cause found, as on earlier Team runs.
    Nothing moved in it: `origin/main` was still `e289864`, `origin/local-m14` was `7e84583`, equal to HEAD, the tree
    was clean, the files of the runs kept their 03:23–03:24 times, and the compiler's `origin/main` was still
    `249eae9`. So commit M14 (4) comes more than 45 minutes after M14 (3) (03:26:35).
  - **(4) Triage:** F-053, a load through a `wild` `NULL` pointer whose value the text reads but that decides nothing
    on the path run, sunk (`untaken`) or deleted (`ignore`, `copy`, `selfsub`, `selfcmp`) at -O2: 107/0 at HUNT5 and the
    baseline, its controls 107/107 (`cmp`, `deadadd`) and the permitted dead load 107/0; reported apart as the check
    of §27 (D-364). `KNOWN_DEFECTS.md`'s M13 block rewritten from HUNT5's registry (DEF-272, DEF-273 by D-364,
    DEF-274), F-053 listed as M14's candidate; F-051's README gains "S-140 (R1)".
  - **(5) The close:** REPORT.md §15 with a pointer in its opening; P1–P9 each ticked; the gate holds in every box;
    the scratch removed; **M14 is ticked**. The session stops here, as the brief says, and its summary goes to the
    dispatcher, F-053 with it for the fuzzer's manager's D6 verification.
- 2026-10-28 (session 13, the Team seat, branch `local-m15`): **M15, the DEF-296 family**, on `nitpick-fuzz_5`'s brief
  (S101), dispatched at 23:12:50 EDT by Ailp-team_24.
  - **A stop, and the dispatcher's ruling.** After the brief's sha256 (23:13:22), while the manager's probe sets in the
    Workspace clone were being read, one Bash command was refused before any of it ran. It ended in `sed -n
    '/^func:main/,/^};/p' m15-probes-l163-r2/q15_pp_cbv_dir.npk`, a read, and the Team project's deny rule
    `Edit(//home/randy/Workspace/**)` refused it ("sed to '…/q15_pp_cbv_dir.npk' was blocked by a deny rule"): the
    harness counts a `sed` naming a path as an edit of it. The dispatch says "If it refuses anything, STOP and report it;
    never work around a refusal", so the session stopped with nothing built, switched or written, and reported in §9's
    block (the `date` read for it: 23:17:40). It disclosed that before the stop it had listed `m15-grid-probes/`'s names
    and checked its `SHA256SUMS` (42 OK), listed `m15-probe-gen/`'s names and read `m15-grid-l163l155.README`, none of
    which the brief names, and had printed probe files' road lines with `awk`.
    **The ruling**, Ailp-team_24 at 23:18:58: the stop was right; resume at §1 with the context as it is. The Team's rules
    forbid any write under `/home/randy/Workspace` but allow reading there, and the deny rule guards writes, counting
    `sed` and `cp` as edits whenever a Workspace path is named, even for a read. On a Workspace path, only the Read tool,
    `cat`, `head`, `tail`, `wc`, `ls`, `sha256sum` (with `-c`), `cmp`, `/usr/bin/grep` and `python3 -B` scripts that only
    read; never `sed`, `cp`, `mv`, `awk`, `tee`, `rsync`, `install` or an in-place tool, and never a redirect into it. The
    brief's copies are made with `cat SRC > DST`, one file at a time into this clone, each checked against its
    directory's `SHA256SUMS`, and the copies are what is read and run. Only the sets the brief names are read
    (`m15-grid-probes/` and `m15-probe-gen/` are not among them, so nothing more is opened there). A further refusal is a
    stop. The precedent: an earlier Team seat copied the compiler pin out of the Workspace with `cat`, because `cp` was
    refused, in the Team seat's log of 2026-10-12 (the setup), the date as the dispatcher's correction gives it.
  - **(1) The start checks** passed: GitHub fetched, `main` fast-forwarded `e289864` → `70a0d8b`, `70a0d8b` an ancestor,
    M14 ticked, the tree clean before the switch, `local-m15` new at 23:19:31. The go is S102, verbatim, with the release
    beside it.
  - **HUNT6 is `1480ca8`**, landing 163, carrying 156; no landing past 163 at the fetch (23:19:57; S103). REG155 is
    `02856cf` (S104). Both built under 20.1.2, in 64.8 s and 66.0 s; each one's `npkc.ll`, `npkc.o`, `npkrt.o` and
    `builder.o` equal its ladder row (notice 164's, notice 156's). The canaries pass at both.
  - **(1b) The housekeeping** (§3), wording only: F-053's README says 12 where it said 13 (M14v's F6);
    `KNOWN_DEFECTS.md` gains the DEF-296 family block, read at HUNT6's registry, whose rows follow the registry where
    the brief's §3 labels differ; M14v's F3 and F5 each get a one-line note. No committed record changed.
  - **(2) Learn by snippet, grid15 and classify15.** The manager's sets copied with `cat` and checked (all OK); the
    expectations table and its checker into `gen/`, "104 rows, 0 mismatches". One probe batch at HUNT6 and REG155 (61
    s): every hazard probe at its table row at both compilers, every twin clean, `cresf` `TYPE-024`. grid15, 100 cells
    (S 16, R 64, W 20), each grid cell one of the probed programs; `--selfcheck` passes; classify15's `--selftest` 18
    of 18 (S105, S106). Committed as M15 (2), before any grid15 run.
  - **(3) The runs** (23:53:28–23:53:52): grid15 at HUNT6 twice, agreeing in all 100 cells, and at REG155; the recall
    gate exits 0 with every check passing. HUNT6 accepts the table's eight `H6/leak` keys and their six candidate
    seeds (70/70), and refuses every other hazard cell with `BORROW-015` (F-050's with `BORROW-002`); every twin is
    clean at both compilers; REG155 reads the poison in all 48 `reg155=="leak"` cells. Committed as M15 (3).
  - **(4) Triage** (§7; S107): the fourteen accepted cells are eight keys, each OPEN in HUNT6's registry (DEF-298,
    DEF-299, DEF-309, and DEF-305's parameter-rooted gap), so known; nothing is filed. Against REG155: 14 accepted at
    both, 34 fixed in (155, 163], 10 fixed before 155, no regression. The family block's cells column is filled. The
    compiler's `origin/main` stayed `1480ca8` through 00:00:45. Committed as M15 (4).
  - **(5) The close** (2026-10-29): the last fetch (00:07:42) still found `1480ca8`, so nothing is measured past 163.
    `REPORT.md` §16 is written, with a pointer in its opening paragraph. Every box of the gate holds, and no
    committed record changed. The scratch was removed at 00:08:09. M15 is ticked, and the session stops here. The
    eight candidates go to the fuzzer's manager through the dispatcher, for D6.
  - **(6) D6 and merge** (the manager, `nitpick-fuzz_5`, 2026-10-29): the fourteen candidates and the controls
    reproduced on the manager's own builds (`.work/l163`, `.work/l155`), agreeing with the committed results leg by
    leg; checker 104/0; `--selfcheck`/`--selftest` pass; the recall gate exits 0 (FINDINGS 14, REGRESSION 0). REPORT
    §16.12 adds the D6 attestation and the annotated landing-164 delta (`cres`/`cresc`/`cresm` refused at `3adfc05`
    by the compiler's record — DEF-309 and DEF-311 FIXED at 164 — not measured here), and `KNOWN_DEFECTS.md` and
    `PROGRESS.md` correct the landing-162 citation to `8c4f005` (S108). `main` is fast-forwarded from `70a0d8b` to
    M15's branch; M15 closed.
