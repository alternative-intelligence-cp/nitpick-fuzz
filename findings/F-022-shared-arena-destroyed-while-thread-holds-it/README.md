# F-022 — a shared arena can be destroyed while a spawned thread still holds it; the thread then allocates in it, and the program ends in `WildLeak`

**The shape.** CONCURRENCY_REFERENCE §5.2:321: "`destroy` on a shared arena requires
that no thread still holds handles. That is ownership, not synchronization: the owner
destroys it after joining." The program below compiles:
```
drop filler(@s);     // a thread that holds the arena (a sanctioned crossing, D-180)
s.destroy();         // before the thread is joined
```
The thread allocates in the destroyed arena 100 ms later. The program's `exit 0` then
traps `WildLeak` (96). Destroying after the join is clean, and so is destroying with no
thread at all. So the leak is the use after destroy.

D-180 makes `shared_arena<T>->` a sanctioned spawn crossing because "a scope exit JOIN
[happens] before it drops". An explicit `destroy()` before that join is not covered.

Found by M11's claim `cc0321`: the refusal expected, npkc 0 measured, run 96/96.

## Verdicts

The reference's answer for `a1` is a refusal (npkc 1).

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `a1_destroy_while_thread_holds` | npkc **0**, **96 / 96** | 0, **96 / 96** | 0, **96 / 96** |
| `ctl_a2_destroy_after_join` — the thread joined at its block's exit | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_a3_destroy_no_thread` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

`KNOWN_DEFECTS.md` has no arena or `destroy` entry. DEF-107 and DEF-119 concern a
view's root, not an arena's lifetime. The shape is present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts. `WildLeak` is the exit check's trap at `exit 0`. Neither
  control trips it.
- **Inferred, not measured:** what the thread's `alloc` does to a destroyed arena. It
  apparently maps a new chunk that nothing frees. Whether its `get` then reads the right
  value is not observed: the thread's own error, if any, never reaches `main` before the
  exit check traps.
