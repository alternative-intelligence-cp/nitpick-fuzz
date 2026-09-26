# PROGRESS

The live state of `PLAN.md`. Tick a box only when its step is done and
committed. A session that starts here resumes at the first unticked box.

## Milestones

- [x] **M0** — the two compilers built and commissioned
- [x] **M1** — the recall suite (`known/`) run at both compilers and matched
- [ ] **M2** — the generator, the runner and the classifier
- [ ] **M3** — the recall gate: the grid re-finds every known defect at `c3bdae2`
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

## Log

- 2026-09-25 (session 1, this branch): started at M0.1 with nothing ticked.
  M0 done: LLVM 20.1.2 fetched, compiler cloned, `base` (c3bdae2) and `hunt`
  (6fb85d3) worktrees built in 67 s / 69 s, digests recorded, both commissioned.
  M1 done: recall suite matches at the baseline 19/19; HUNT carries only the
  DEF-99 fix.
