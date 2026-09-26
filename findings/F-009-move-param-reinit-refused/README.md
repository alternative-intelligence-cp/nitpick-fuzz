# F-009 — a `move` parameter re-initialised after a move cannot be read (`MOVE-001`): a legal program refused

**Lower priority** (CLAUDE.md: a refusal of what the reference admits). This is
not a memory fault.

**The shape.** In `func:f = int32(move string:x) { string:t = move(x); x =
raw nw(); pass raw obs_s(x); }`, the read of `x` after its re-assignment is
refused `NITPICK-MOVE-001`: "this binding was moved out of and is invalid
until it is assigned again". It has just been assigned again. The same body
with `x` a local compiles and returns 22.

MEMORY_REFERENCE §2.3: "A moved-from binding is invalid … It may be
reinitialized by assignment, after which it is live again — ordinary
definite-assignment analysis."

**Found by** the grid's section D, at both compilers (counts at HUNT2):
- `move_param × swap`: 25 cells, the read-after and reuse-sentinel cells
  over 13 types, are refused.
- `move_param × loop_move`: 47 cells, every observer over 12 types. A move of
  `x` in a loop that re-assigns it each trip is refused at the second trip's
  move.
- At `local`, the same operations compile and run clean: 51 `swap` cells and
  47 `loop_move` cells, all 0/0.

## Verdicts

Measured on 2026-09-26, by PLAN.md's recipe through `gen/run_findings.py
--heap`: at HUNT2 twice and at the baseline once (`VERDICTS.txt`; the HUNT2
runs agree).

| program | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|
| `move_param_reinit_read.npk`, the body above | 1, `MOVE-001` | 1, `MOVE-001` |
| control `ctl_local_reinit_read.npk`, the same body with `string:x = raw mk();` a local | 0 / 22 / 22 | 0 / 22 / 22 |

## Deduplication

`KNOWN_DEFECTS.md` has no over-restriction of this kind. D-208 (loop-carried
moved-from states, 1.4.3) made the move analysis learn about parameters. This
is a parameter's re-initialisation not being learned. **Both compilers: an old
over-restriction.**

## Measured, and inferred

- *Measured:* the two verdicts, and the grid's cells.
- *Inferred, not measured:* the definite-assignment analysis clears a
  parameter's moved-from state on nothing, while a local's is cleared by
  assignment.
