# F-049 — a consuming `pick`'s binding re-initialised after a move cannot be read (`MOVE-001`): a legal program refused, new at landing 74

**Lower priority** (CLAUDE.md: a refusal of what the reference admits). This is
not a memory fault. It is F-009's shape (DEF-124) at a pattern binding, and it
appeared with DEF-118's fix: **a regression against HUNT2**, where these
programs compiled and gave the right answer.

**The shape.** In a consuming pick's arm, `(Som(x)) { string:t = move(x); x =
raw nw(); int32:o = raw obs_s(x); … }`, the read of `x` after its
re-assignment is refused `NITPICK-MOVE-001`: "this binding was moved out of and
is invalid until it is assigned again (D-065)". It has just been assigned
again. The same body with `x` a local compiles and reads 22, the new value.

MEMORY_REFERENCE §2.3 (at HUNT2): "A moved-from binding is invalid … It may be
reinitialized by assignment, after which it is live again — ordinary
definite-assignment analysis."

**Found by** M12's M9 grid at HUNT3 `0c0f5a3`, as moved cells against HUNT2
`9126350` (`results/0c0f5a3/MOVES9.md`, `MOVES12.md`):
- `pick_own × loop_move`: 16 cells, every observer over str, box, list and
  lstr, are refused at HUNT3 (four of them were F-006's leak cells at HUNT2,
  the other twelve clean). A move of `x` in a loop that re-assigns it each trip
  is refused at the second trip's move.
- `pick_own × swap`: the 8 cells that read `x` after the swap (read-after and
  reuse-sentinel) are refused; the 8 with no read after it still run clean.
- At `local`, the same operations compile and run clean at every compiler
  measured: 47 `loop_move` cells and 51 `swap` cells.

## Verdicts

Measured on 2026-10-15, by PLAN.md's recipe through `gen/run_findings.py`: at
HUNT3 twice and the baseline once under LLVM 20.1.8 (`VERDICTS.txt`; the HUNT3
runs agree), and at HUNT2 once and the baseline once under LLVM 20.1.2
(`VERDICTS-9126350.txt`). Landings 73 and 74 by `gen/snip.py` under 20.1.2.

| program | HUNT3 `0c0f5a3`, runs 1 and 2 | landing 74 `40deffa` | landing 73 `bbb1530` | HUNT2 `9126350` | baseline `c3bdae2` |
|---|---|---|---|---|---|
| `pick_reinit_read.npk`, the body above | 1, `MOVE-001` | 1, `MOVE-001` | 0 / 22 / 22 | 0 / 22 / 22 | 0 / 22 / 22 |
| `pick_reinit_loop.npk`, the move and re-assignment in a `for` | 1, `MOVE-001` | 1, `MOVE-001` | 0 / 22 / 22 | 0 / 22 / 22 | 0 / 22 / 22 |
| control `ctl_local_reinit_read.npk`, the same body on a local | 0 / 22 / 22 | 0 / 22 / 22 | 0 / 22 / 22 | 0 / 22 / 22 | 0 / 22 / 22 |
| control `ctl_pick_moved_read.npk`, moved and NOT re-assigned, then read | 1, `MOVE-001` | 1, `MOVE-001` | 0 / 21 / 21 | 0 / 21 / 21 | 0 / 21 / 21 |

The observer's codes name what was read: 21 the original, 22 the new value
(S6). `ctl_pick_moved_read` is the control a wrong implementation gets wrong:
before landing 74 it compiles and reads the moved-out original (DEF-118's
shape, F-003), and from 74 it is refused, rightly. So the move of a pick's
binding is tracked from 74 on, and only its re-assignment is not read as one.

## Deduplication

- `KNOWN_DEFECTS.md`: DEF-118 (F-003) is the move rules not reaching a pick's
  binding, the opposite fault; DEF-124 (F-009) is this shape at a `move`
  parameter, and its fix marks a parameter's assignment as a local's
  (`assign_assign`'s `SYM_DECL` branch, its record at HUNT3), which a pattern
  binding is not.
- The compiler's registry at HUNT3 (`OPEN_DECISIONS.md`) has no entry for a
  re-initialised pick binding.
- **Bisected** (S23): the grid's 32 `pick_own × {loop_move, swap}` cells and
  their 98 `local` twins run at landing 73 `bbb1530` and landing 74 `40deffa`;
  the 24 cells move exactly at 74, 1.6.1d step 1 (DEF-118, DEF-119, DEF-123,
  DEF-127). So this is new at 74: **not present at the baseline or HUNT2.**

## Measured, and inferred

- *Measured:* the verdicts above, and the grid's cells at HUNT2, 73, 74 and
  HUNT3.
- *Inferred, not measured:* that the cause is the bindings analysis reading a
  pattern binding's assignment as no re-initialisation, as DEF-124 described
  for parameters before its fix. The compiler's source was not read.

## Reported since (added in M13; reported, not measured by this repository)

- **Registration.** `nitpick-compiler_38` registered F-049 as **DEF-256**
  (lower priority, a false refusal) and read the cause in the compiler:
  `assign_assign` (`src/frontend/analysis/bindings.npk`) marks an assignment
  only for `SYM_DECL` and `SYM_STMT` symbols, so a consuming arm's `SYM_PAT`
  binding is never re-marked. *Reported by the compiler seat, in its registry;
  not measured here.*
- **The workbench's reproduction.** `nitpick-fuzz_2` reproduced it on
  2026-10-15 on an independent build of `0c0f5a3` under LLVM 20.1.2, whose
  `npkc.ll` (`f520d574…`) and `npkrt.o` (`c8e5033a…`) are byte-identical to
  M12's, and at `2f0937a` (landing 114). *Reported by `nitpick-fuzz_2`; not
  measured here.*

The registry at HUNT4 `c72639f` records DEF-256 fixed at landing 132
(`6f0f518`); M13 measures these programs there (`VERDICTS-c72639f.txt`).
