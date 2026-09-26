# F-026 — a unit annotation on a `tfp64` is accepted and ignored, so Meters plus Seconds compiles

**The shape.** TYPE_REFERENCE §5a:553: "Dimensional analysis is a `dim256`-exclusive
feature. Only `dim256` supports" a unit. At HUNT2, `tfp64<Meters>:a` and
`tfp64<Seconds>:b` are accepted, and `tfp64:c = a + b;` compiles and computes 5.0. The
same sum over `dim256` is refused, `NITPICK-TYPE-049` ("dimensional mismatch").

A reader of `tfp64<Meters>` is told the value carries a unit that the checker then
never checks.

Found by M11's claim `ty0553`: the refusal expected, npkc 0 measured, exit 10 (the
program's "the annotation was accepted and the value is 1.0").

## Verdicts

`d1` exits 10 when the mismatched sum compiled and computed 5.0; the reference's
answer is a refusal.

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `d1_tfp64_unit_mismatch_compiles` | npkc **0**, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `ctl_d2_dim256_mismatch_refused` | 1, `TYPE-049` | 1 | 1 |

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns units. Present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts.
- **Inferred:** that the parser accepts a type argument on `tfp64` and the checker
  drops it. Whether it is kept anywhere was not looked for.
