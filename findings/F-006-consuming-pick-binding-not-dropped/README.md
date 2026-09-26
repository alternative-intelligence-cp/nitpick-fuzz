# F-006 — a consuming `pick`'s binding is never dropped at the arm's end: a leak

**The shape.** In `pick (move(e)) { (Som(x)) { … }, (*) { } }`, the binding `x`
owns its payload. CONTROL_REFERENCE §1.2 says of the consuming form: "its
bindings OWN their payloads and drop at the arm's exit, and `v` is moved-from
after". Measured, `x` is not dropped at the arm's end. The payload stays live
after every drop has run, and nothing owns it. The minimiser reduced the grid
cell to an arm with an **empty body**: binding `x` is enough to leak the
46-byte string.

**Found by** the leak observer (M9.1), at the grid's `pick_own` place. **32
cells** at HUNT2 `9126350` show it, with the same live bytes at the baseline
`c3bdae2` (`CELLS.txt`):
- Every operation that leaves `x` holding a value at the arm's end leaks that
  value: `read`, `clone`, `field_write`, `assign`, `swap`, `cond_move_f`,
  `loop_move`, `move_part`, `at_grow` and `at_overwrite`.
- The types are `string` and `Box` (46, or 43 when the value is the new one),
  `List<int64>` (8), and `List<string>` (70 or 67). A grown list leaks its
  grown buffer (128, 774).
- Where the arm moves `x` out into a local, nothing leaks (`ctl_binding_moved_out_noleak`).
- Four cells (`at_overwrite`) carry F-005's leak as well.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). "live" is `peak_live − 1 048 576`
after `run` returned and `main` allocated the probe.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `pick_arm_read_leak.npk` | `pick (move(e)) { (Som(x)) { int32:rd = raw obs_s(x); }, (*) { } }` in `run` | exit 0/0, **live 46** (`allocated=1048622 peak_live=1048622 count=2`) | the same |
| `minimized/m3613_str_pick_own_read_lk.npk` | the grid cell minimised with `--live 46` (72 builds, 28 lines): the arm `(Som(x)) { }` is empty | exit 0/0, **live 46** | the same |

## The controls

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_lending_pick_noleak.npk` | the lending `pick (e)`: `e` keeps the payload and drops it at `run`'s end | live 0 | live **0** | live 0 |
| `ctl_binding_moved_out_noleak.npk` | the consuming arm does `string:y = move(x);`: `y` drops it | live 0 | live **0** | live 0 |
| `ctl_wildcard_arm_noleak.npk` | the consuming arm binds `_` instead of `x` | live 0 (DEF-88's fix: an all-wildcard consuming arm drops the whole value) | live **0** | live 0 |

So the observer reads 0 whenever the payload has an owner that drops it. The
wildcard form of the same consuming arm does drop it. Only a NAMED consuming
binding that is still live at the arm's end is left undropped.

## Deduplication

`KNOWN_DEFECTS.md` has no `pick` shape. The nearest is the compiler's own
DEF-88 (1.5.8b step 6d), fixed in both compilers. Its fix made `_` bind
nothing, and made "a consuming arm of wildcards [own] and [drop] the whole
value". `ctl_wildcard_arm_noleak` confirms that half. A named binding is
another path. **Present at both compilers, with identical live bytes: an old
defect, not a regression.**

## Measured, and inferred

- *Measured:* the verdicts above, and the grid's 32 cells.
- *Inferred, not measured:* the arm's scope exit does not register a named
  consuming binding as an owning local to drop. F-003 (the same binding's
  moves are not tracked) may be the checker's half of the same omission; see
  there.
- The compiler's own guide says that when adding a pattern shape to the
  emitter, one should "ask who frees what the pattern does not name — and
  measure it with a churn twin under `NPK_HEAP_STATS`". Here what the pattern
  *does* name is not freed.
