# F-012 — a `for` over a range runs zero times at its type's edges: a signed inclusive range ending at the maximum, and an unsigned range that crosses the sign bit

**The shape.** `for (T:i in lo..hi)` and `for (T:i in lo...hi)` over integer
ranges, with the bounds computed at run time:
- **a signed inclusive range whose upper bound is its type's maximum runs zero
  times.** `for (int8:i in 125i8..127i8)` should run 3 times, and
  `for (int8:i in 0i8..127i8)` 128 times. Each runs 0 times, with no trap. The
  same holds at int32 and int64.
- **an unsigned range that crosses 2^(W-1) runs zero times.**
  `for (uint8:i in 100u8..200u8)` should run 101 times, and `100u8...200u8`
  100 times. Each runs 0 times. The same holds for a uint32 range across 2^31.

Both are silent: the program compiles, runs, and simply never enters the loop.
No `wild`, no `=>!`.

**Found by** the M10 checklist items `l06_for_inclusive_to_int8_max` and
`l08_for_inclusive_to_int64_max` (exit 10 at both compilers: zero trips where
three are stated). The emitted IR then showed the head's test, and probes
followed it to the unsigned face. The checklist's own unsigned item
`l07_for_inclusive_to_uint8_max` (250..255) agreed, by the coincidence the
controls explain.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc / -O0 / -O2.
Every program exits 0 when the trip count is the reference's, and 10 on zero
trips.

| program | the loop | trips stated | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|---|
| `incl_int8_to_max.npk` | `for (int8:i in 125..127)` | 3 | 0 / **10** / **10** | the same |
| `incl_int8_whole_positive.npk` | `for (int8:i in 0..127)` | 128 | 0 / **10** / **10** | the same |
| `incl_int32_to_max.npk` | `for (int32:i in max-2..max)` | 3 | 0 / **10** / **10** | the same |
| `incl_int64_to_max.npk` | `for (int64:i in max-2..max)` | 3 | 0 / **10** / **10** | the same |
| `uns_uint8_across_128.npk` | `for (uint8:i in 100..200)` | 101 | 0 / **10** / **10** | the same |
| `uns_uint8_across_128_excl.npk` | `for (uint8:i in 100...200)` | 100 | 0 / **10** / **10** | the same |
| `uns_uint32_across_2p31.npk` | `for (uint32:i in 2147483640...2147483650)` | 10 | 0 / **10** / **10** | the same |

Probes, not kept as programs, found the same zero at int16 (`32765..32767`)
and at uint16 (`30000..40000`), and at uint64 across 2^63. An inclusive
range ending at the UNSIGNED maximum (uint16, uint32, uint64 `max-2..max`;
uint8 `250..255`) runs the right number of times. The controls say why.

At `9f6f370`, every program gives the same verdict (`VERDICTS-9f6f370.txt`).

## The controls

| control | the loop | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_incl_int8_below_max.npk` | `for (int8:i in 125..126)` | 2 trips | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_uns_uint8_below_128.npk` | `for (uint8:i in 10..20)` | 11 trips | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_uns_uint8_above_128.npk` | `for (uint8:i in 250..255)` | 6 trips | 0 / 0 / 0 | 0 / 0 / 0 |

The third control is right by coincidence. Read as `int8`, 250..255 is
-6..-1, and 255 + 1 wraps to 0, which is above them. So the signed test
`i < 0` holds for exactly the six values. A range wholly below 128 is right
for the plain reason. The defect needs its two edges.

## What the emitted IR shows

`incl_int8_to_max`'s probe at HUNT2, the range's exclusive end and the head:
```
%t10 = add i8 %t9, 1          ; hi + 1: 127 + 1 wraps to -128, no overflow check
...
fr.head0:
  %t19 = icmp slt i8 %t17, %t18   ; SIGNED, for uint8 as well
```
`uns_uint8_across_128`'s head is the same `icmp slt i8`. Read as signed, 100
is not below 201 (-55 as `i8`), so the loop never enters.

## Deduplication

- Not in `KNOWN_DEFECTS.md`, and not among the compiler's own recorded defects
  (OPEN_DECISIONS mentions no `for`-range bound).
- Present at the baseline: **an old defect, not a regression**. Present at
  `9f6f370`.

## The reference

- OP_REFERENCE §8 (HUNT2 lines 375–376): `..` is the "Inclusive range `[a, b]`",
  `...` the "Exclusive range `[a, b)`", both "Used in `for` and `pick`".
- CONTROL_REFERENCE §2 (line 109): "`for`, `loop` and `till` are bounded by
  construction".
- TYPE_REFERENCE §1.3 (lines 158–160): an unsigned type's "Comparisons use
  `ult`/`ugt`/`ule`/`uge` instead of `slt`/`sgt`/`sle`/`sge`".

## Measured, and inferred

- *Measured:* the verdicts above, and the two IR lines quoted.
- *Read, not measured* (`src/backend/ir/ir_stmt.npk` at HUNT2):
  - `emit_for`'s range arm writes its head's test as the fixed text
    `icmp slt` (line 1347), whatever the binding's signedness;
  - the inclusive range reaches it as an exclusive bound already computed
    as `hi + 1` by a plain `add`, where the wrap happens.

  The two readings account for every verdict, the coincidental control
  included.
