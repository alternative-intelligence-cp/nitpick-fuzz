# F-020 — the scope-exit join relays the last-spawned child's error, not the first child error (a silent wrong answer)

**The shape.** CONCURRENCY_REFERENCE §2.2:79–80: a spawned task's error "reaches the
enclosing scope's D-062 join, which relays the **first child error, verbatim (D-080),
after every child has finished**". With two children, `fast_fail` (fails E1 at once)
spawned first and `slow_fail` (fails E2 after 50 ms) spawned second, the parent's
error is **E2**. Spawned in the other order, it is E1. The error that comes back is
the last-spawned child's. In `j1`, the first child error is E1 under either reading of
"first": `fast_fail` is spawned first and fails first.

A caller that handles E1 and E2 differently takes the wrong branch. Nothing reports
it.

Found by M11's claim `cc0080` (CONCURRENCY:80), which exits 11 at HUNT2. Session 7's
probe found it relaying E2.

## Verdicts

Exit 0 on the reference's answer (E1), 10 on E2.

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `j1_first_error_lost` — spawn fast, then slow | npkc 0, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `ctl_j2_single_child` — fast only | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_j3_spawn_order_swapped` — spawn slow, then fast | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

`ctl_j3` agrees with the reference only because its last-spawned child is also its
first to fail.

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns the join or error propagation from spawned
tasks. The shape is present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts above, and session 7's two-order probe (E2 when fast is
  spawned first, E1 when slow is).
- **Inferred:** "the last-spawned child's error" is read from two orders only. The rule
  might instead be "the error of the child joined last". With two children the two
  readings coincide.
