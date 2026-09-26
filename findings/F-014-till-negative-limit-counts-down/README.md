# F-014 — `till` with a negative limit counts down: `till(-3, 1)` runs three times, where the reference says zero

**The shape.** `till(limit, step)` with `limit < 0` should run zero times,
and runs `|limit|` times with `$` = 0, -1, … `limit`+1. `till` infers a
direction from its bounds as `loop` does. The reference gives `till` one
direction: up from 0. This is a silent wrong answer: the body runs for
counter values the program's author was promised it would never see. No
`wild`, no `=>!`.

**Found by** the M10 checklist item `l11_till_nonpositive_limit` (exit 10 at
both compilers). A probe measured the trips and the counter: 3 trips, the
last `$` -2.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc / -O0 / -O2.
Exit 0 is the reference's answer, zero trips. Exit 10 is exactly three trips
ending at `$` = -2.

| program | the loop | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `till_negative_limit.npk` | `till(k, 1i64)`, `k` = -3 at run time | 0 / **10** / **10** | the same |
| `till_negative_literal_limit.npk` | `till(-3i64, 1i64)` | 0 / **10** / **10** | the same |

At `9f6f370`, both give the same verdict (`VERDICTS-9f6f370.txt`).

## The controls

| control | the loop | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_till_zero_limit.npk` | `till(0, 1)` | zero trips | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_till_positive_limit.npk` | `till(3, 1)` | three trips, `$` 0, 1, 2 | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_loop_zero_to_negative.npk` | `loop(0, -3, 1)` | three trips, `$` 0, -1, -2: `loop` infers its direction, so here the descent is right | 0 / 0 / 0 | 0 / 0 / 0 |

The third control is F-014's defect program with `loop` for `till`. The
descent is the right answer for `loop` and the wrong one for `till`.

## Deduplication

- Not in `KNOWN_DEFECTS.md`.
- The compiler's history holds a mirror of it on the compile-time side. DEF-29
  (fixed at 1.5.4): the `comptime` evaluator "read `till(limit, step)` as
  `loop(lo, hi)`". *Not measured:* whether the evaluator's `till` agrees with
  the emitter's today.
- F-013 is a separate defect in the same function; `till(200u8, 1u8)` shows
  both.
- Present at the baseline: **an old defect, not a regression**. Present at
  `9f6f370`.

## The reference

- CONTROL_REFERENCE §2.4 (HUNT2 line 198): "**`till(limit, step)`** — the
  simple form. Counts **up from 0** to `limit`."
- Line 235, the edge-case table: "`till` with `limit <= 0` | zero iterations —
  `till` ascends from `0`".
- Lines 238–239: "`till` ascends from zero only, while `loop` handles
  arbitrary start points and both directions."
- DECISIONS D-022 (line 1529): "`till` with `limit <= 0` | zero iterations
  — `till` ascends from `0` and can never reach a non-positive limit".

## Measured, and inferred

- *Measured:* the verdicts above.
- *Read, not measured:* `emit_counted` (`src/backend/ir/ir_stmt.npk` at
  HUNT2, from line 1103) builds `till` as a `loop` whose start is `"0"`. Its
  comment says "DIRECTION IS INFERRED FROM THE BOUNDS". The direction test
  `icmp slt i64 start, limit` is written for both forms, so `till`'s limit
  below 0 selects the descending walk.
