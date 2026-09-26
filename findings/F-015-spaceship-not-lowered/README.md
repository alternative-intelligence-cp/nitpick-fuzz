# F-015 — `<=>` is accepted by the checker and refused by the emitter (`NITPICK-EMIT-002`) in every form

**The shape.** Any use of the three-way comparison `a <=> b`, even between
two `int32` literals, stops the compile with `NITPICK-EMIT-002`: "the emitter
could not lower this, although the frontend accepted it; a defect in the
compiler rather than in this program". The operator is documented in three
references, with a type and a result.

This is a refusal, so nothing runs wrong. By the compiler's own message it is
a compiler defect. This repository's definition files it at the lower
priority of refusals of what the reference promises.

**Found by** the M10 checklist item `m06_spaceship`, refused at both
compilers.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree).

| program | the use | the reference's answer | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|---|
| `spaceship_literals.npk` | `int32:r = 1i32 <=> 2i32;` | -1 (exit 0) | 1, `EMIT-002` at the `<=>` | the same |
| `spaceship_values.npk` | run-time `int32` pairs | -1, 0, 1 | 1, `EMIT-002` | the same |
| `spaceship_uint64.npk` | `~0u64 <=> 1u64` | 1 | 1, `EMIT-002` | the same |

At `9f6f370`, all three are refused the same way (`VERDICTS-9f6f370.txt`).

## The control

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_three_way_by_hand.npk` | the same three answers from `<` and `==` in a `never fails` function | runs, exit 0 | 0 / 0 / 0 | 0 / 0 / 0 |

## Deduplication

- Not in `KNOWN_DEFECTS.md`. The compiler's OPEN_DECISIONS names no `<=>`
  defect.
- Present at the baseline: **an old defect**. Present at `9f6f370`.

## The reference

- OP_REFERENCE §0.1 (HUNT2 line 68): "**`<=>`** (spaceship) yields `int32`:
  `-1`, `0`, or `1`."
- OP_REFERENCE §3 (line 213): "`<=>` | Spaceship | 3-way comparison. Returns
  `-1`, `0`, or `1`."
- TYPE_REFERENCE §28 (line 2038): "`<=>` | spaceship | `icmp`+select |
  Returns -1/0/1".
- OP_REFERENCE §0's precedence table lists it at level 10 with the relational
  operators.

## Measured, and inferred

- *Measured:* the refusals and the control.
- *Not read:* the emitter's source for why `<=>` has no arm. The message and
  its position, the operator, are the compiler's own account.
