# F-016 — a `pick` range pattern with a negative bound is accepted by the checker and refused by the emitter (`NITPICK-EMIT-002`)

**The shape.** A range pattern whose bound is a negated literal, e.g.
`(-5i32..-2i32)`, `(-5i32..2i32)` or `(-5i32...-2i32)`, stops the compile with
`NITPICK-EMIT-002`, the compiler's "a defect in the compiler" message.
- A single negative value pattern `(-3i32)` compiles and runs: DEF-35's fix.
- A range with positive bounds compiles and runs.

This is a refusal of what the reference promises, a compiler defect by its
own message, at the lower priority.

**Found by** the M10 checklist item `p05_negative_patterns`: its `(-1i32)`
arm compiled and its `(-5i32..-2i32)` arm did not.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). The reference's answer for each is
exit 4 (-3 is in the range).

| program | the pattern | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `neg_range_pattern.npk` | `(-5i32..-2i32)` | 1, `EMIT-002` at the pattern | the same |
| `neg_low_bound_pattern.npk` | `(-5i32..2i32)` | 1, `EMIT-002` | the same |
| `neg_range_pattern_exclusive.npk` | `(-5i32...-2i32)` | 1, `EMIT-002` | the same |

At `9f6f370`, all three are refused the same way (`VERDICTS-9f6f370.txt`).

## The controls

| control | the pattern | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_pos_range_pattern.npk` | `(2i32..5i32)`, selector 3 | exit 4 | 0 / 4 / 4 | 0 / 4 / 4 |
| `ctl_neg_value_pattern.npk` | `(-3i32)`, selector -3 | exit 4 | 0 / 4 / 4 | 0 / 4 / 4 |

## Deduplication

- Not in `KNOWN_DEFECTS.md`.
- **It is where DEF-35's fix did not reach.** DEF-35 is in the compiler's
  OPEN_DECISIONS, fixed at 1.5.4b step 2, before the baseline: "a negated
  literal pattern `(-1i32)` was admitted by the checker … and refused by the
  EMITTER as `NITPICK-EMIT-002`: `pattern_const` folded a literal … and not a
  `-` over a literal. Fixed with the arm."
  - *Inferred, not read:* a range pattern's bounds go through another path
    than the value pattern's `pattern_const`, or a path the arm does not
    cover.
- Present at the baseline: **an old defect**. Present at `9f6f370`.

## The reference

- OP_REFERENCE §8 (HUNT2 lines 375–376): `..` and `...` are ranges "Used in
  `for` and `pick`".
- TYPE_REFERENCE §28's Range table (lines 2095–2096): "Used in `for`, `pick`
  patterns".

No sentence restricts a pattern's bounds to non-negative values, and the
checker and the exhaustiveness analysis both accept these patterns.

## Measured, and inferred

- *Measured:* the refusals, and the controls that compile.
- *Inferred:* the mechanism above. The emitter's source was not read.
