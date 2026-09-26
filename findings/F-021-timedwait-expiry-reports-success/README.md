# F-021 — a `timedwait` whose deadline expires with no signal reports success (a silent wrong answer: an error path becomes a success)

**The shape.** No task ever signals the condition variable. `await cv.timedwait(g,
200 ms)` waits the full 200 ms and then returns a **success**, so the caller cannot
tell a timeout from a signal. What the references say:
- CONCURRENCY_REFERENCE §9:568 makes `timedwait` the only form (D-056).
- §6:426 makes a deadline's expiry the error `DeadlineExceeded`, "a catchable `Result`
  error" at a blocking operation.
- §9:571: "Every acquisition is async, deadline-bounded, and returns `Result`".
- DECISIONS (the D-056 amendment, at its 3661–3666) says of `timedwait`: "on
  DeadlineExceeded the guard is SPENT".

Found by M11's claim `cc0568b` (CONCURRENCY:568), which exits 10 at HUNT2.

## Verdicts

Exit 0 on an error (the reference's answer); 10 on a success after the full wait; 11
on a success at once.

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `t1_timedwait_expiry` | npkc 0, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `ctl_t2_recv_expiry` — a `recv` on an empty channel, 50 ms | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns condition variables or deadlines. The shape is
present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts. The wait lasts at least 150 ms of the 200: `t1`'s 10
  requires it.
- **Reasoned, not measured:** which outcome the design intends when the wait expires
  but the re-acquire (under the same deadline, per the decision) succeeds. The
  references state expiry as an error for blocking operations generally, and name
  `DeadlineExceeded` for `timedwait`. No sentence permits a success on expiry. The
  workbench should confirm the reading with the compiler seat.
