# F-013 — `loop` and `till` widen an unsigned bound by its sign: an ascending uint8 `loop` runs 156 times the wrong way, and a uint32 one traps

**The shape.** A counted loop whose bounds are unsigned and at or above
2^(W-1):
- **`loop(100u8, 200u8, 1u8)`** should count up, `$` = 100 … 199, 100 times.
  It counts DOWN from 100 to -55, 156 times, with `$` negative.
- **`till(200u8, 1u8)`** should count up from 0, `$` = 0 … 199, 200 times. It
  counts down from 0 to -55, 56 times.
- **`loop(2147483640u32, 2147483650u32, 1u32)`** should run 10 times. It traps
  `IntOverflow`.

The first two are silent wrong answers. The third stops, but where the
reference states ten plain iterations. No `wild`, no `=>!`.

**Found by** a probe. F-012 showed that the `for` head ignores signedness, so
the counted loops were probed with unsigned bounds that cross the sign bit.
The checklist's counted-loop items (`l10`–`l22`) used signed bounds and
agreed.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc / -O0 / -O2.
Exit 0 is the reference's answer; exit 10 names the measured wrong one.

| program | the loop | stated | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|---|
| `loop_uint8_across_128.npk` | `loop(100u8, 200u8, 1u8)` | 100 trips, `$` 100 … 199 | 0 / **10** / **10**: exactly 156 trips, `$` 100 … -55 | the same |
| `till_uint8_limit_200.npk` | `till(200u8, 1u8)` | 200 trips, `$` 0 … 199 | 0 / **10** / **10**: exactly 56 trips, `$` 0 … -55 | the same |
| `loop_uint32_across_2p31.npk` | `loop(2147483640u32, 2147483650u32, 1u32)` | 10 trips | 0 / **93** / **93**: `IntOverflow` | the same |

At `9f6f370`, every program gives the same verdict (`VERDICTS-9f6f370.txt`).

## The controls

| control | the loop | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_loop_uint8_below_128.npk` | `loop(10u8, 20u8, 1u8)` | 10 trips, `$` 10 … 19 | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_loop_int8_signed.npk` | `loop(100i8, -56i8, 1i8)`: 200u8's bit pattern, as a signed value | 156 trips, `$` 100 … -55 (descending is right here) | 0 / 0 / 0 | 0 / 0 / 0 |

The second control is the wrong implementation's answer given the type where
it is right. The loop machinery is correct for signed bounds; the unsigned
bound is read as that signed value.

## What the emitted IR shows

The uint8 `loop`'s head at HUNT2:
```
%t5  = sext i8 %t4 to i64       ; start 100
%t8  = sext i8 %t7 to i64       ; limit 200 -> -56
%t13 = icmp slt i64 %t5, %t8    ; "ascending?" 100 < -56: no -> descending
```

## Deduplication

- Not in `KNOWN_DEFECTS.md`.
- The compiler's history has the same CLASS elsewhere, fixed at 1.4.2: "the
  argument coercion's blind `zext` … which now reads signedness off the
  recorded type" (D-192, for builtin arguments). This is the counted loop's
  widening, which reads no signedness.
- Present at the baseline: **an old defect, not a regression**. Present at
  `9f6f370`.
- **F-014** is the same function's other defect, `till` inferring a direction.
  `till_uint8_limit_200` shows both at once: the limit is misread by F-013,
  and the descent is F-014's.

## The reference

- CONTROL_REFERENCE §2.4 (HUNT2 lines 205–215): `loop(start, limit, step)`'s
  "Direction is inferred from `start` and `limit`". `loop(0i32, 10i32, 1i32)`
  is "ascending: 0, 1, ..., 9".
- Line 198: `till` "Counts **up from 0** to `limit`."
- DECISIONS D-095 (line 6691): a lossless conversion keeps every value, which
  is what widening must do.
- TYPE_REFERENCE §1.3 (lines 158–160): unsigned comparisons are `ult`/`ugt`.

## Measured, and inferred

- *Measured:* the verdicts above, and the IR quoted.
- *Read, not measured* (`src/backend/ir/ir_stmt.npk` at HUNT2):
  `loop_i64` (lines 1088–1095) widens every bound to `i64` with `sext`, whatever
  its type's signedness. `emit_counted` then infers the direction with
  `icmp slt i64`. Why the uint32 loop traps rather than descends was not
  traced; *inferred:* the descending counter passes below the widened limit's
  range, and a checked subtraction guards it.
