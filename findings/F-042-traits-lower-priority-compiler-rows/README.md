# F-042 — TRAITS_REFERENCE: one place where the compiler departs from the reference safely (lower priority)

The row, with its claim's program and its verdicts at HUNT2 `9126350`, the baseline
`c3bdae2` and the newest `main` `93bcb66`, is in [`ROWS.md`](ROWS.md). It gives the same
result at all three.

**a. An `opaque struct` is accepted at module level** (`tr0368`)
- TRAITS:367–371: `opaque` "is legal **only inside an `extern` block** (D-066, as narrowed
  by D-149)".
- `opaque struct:DbHandle;` at module level compiles.
- Inside an extern block, the one place the reference allows, it is EXTERN-001, a tier
  "reserved for the LOAD_MODULE work" (D-190; `tr0373` here, `md0241` in MODULE).
- This is AST's F-039 e, met in TRAITS' own sentence.

## Deduplication

The same shape as F-039 e (AST:43); not in KNOWN_DEFECTS.md or the registry at `93bcb66`.

## Measured, and inferred

- **Measured:** the row's result at three compilers.
- **Reasoned, not measured:** that this is the compiler's departure. Two references and two
  decisions say extern-only.
