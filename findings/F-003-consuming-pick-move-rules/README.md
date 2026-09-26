# F-003 — a consuming `pick`'s binding escapes the move rules: a read after its move, and a second move, compile

**The shape.** In a consuming `pick (move(e))`, an arm's binding owns its
payload (CONTROL_REFERENCE §1.2, D-216). A `move(x)` of that binding does not
make `x` invalid to the checker. A read of `x` after the move compiles, and so
does a second `move(x)`: two moves, a move in a loop, or a move in one branch
followed by a read. The moved value's new owner frees it, so:
- the read then sees the free poison (**70**), or a freed `List<string>`'s
  element pointer (**107**);
- the second owner frees it again (**95**).

The same code with `x` a local is refused `NITPICK-MOVE-001`.

**Found by** the widened grid's `pick_own` place (M9 section C) crossed with
section D's value operations. **44 cells** show it at HUNT2 `9126350`, with the
same verdicts at the baseline `c3bdae2`. They are listed with both compilers'
verdicts in `CELLS.txt`:
- `loop_move_nr` (a move in a loop with no re-initialisation), 16 cells: 95/95
  on every observer, at `str`, `box`, `list`, `lstr`.
- `cond_move_t` (a move in a branch taken, then a read), 8 cells: 70/70 on the
  read, 25/25 under the reuse sentinel (the freed body reused by the
  sentinel), and 107/107 for `lstr`.
- `move` then a read, 8 cells: 21/21. The value is still owned by `y` when
  `x` is read, so the read of a moved-from binding returns the value.
- `cond_move_f` and `move_part` then a read, 12 cells: accepted and clean,
  where MEMORY_REFERENCE §2.3 and D-065 say any read of a moved-from binding
  is refused.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once. Every
line is in `VERDICTS.txt`. The two HUNT2 runs agree for every program. Each cell
below gives npkc's rc / the -O0 exit / the -O2 exit.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `pick_move_twice_drop.npk` | in the arm `(Som(x))`: `string:a = move(x); string:b = move(x);`, then `run` returns so every drop runs | 0 / **95** / **95** | 0 / **95** / **95** |
| `pick_read_after_move.npk` | in the arm: `if (raw truth(1i64)) { string:a = move(x); }`, then read `x` | 0 / **70** / **70** | 0 / **70** / **70** |
| `minimized/m7092_…_loop_move_nr_dx.npk` | the grid cell minimised (`gen/minimize.py`, 74 builds, 30 lines): `for (int64:k in 0i64...2i64) { string:y = move(x); }` in the arm | 0 / **95** / **95** | 0 / **95** / **95** |
| `minimized/m5771_…_cond_move_t_ra.npk` | the grid cell minimised (81 builds, 36 lines): the conditional move, then the read | 0 / **70** / **70** | 0 / **70** / **70** |

## The controls

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_local_move_twice.npk` | the two moves of `pick_move_twice_drop`, of a local `string:x` | refused `MOVE-001`, the rule the binding escapes | 1, `MOVE-001` | 1, `MOVE-001` |
| `ctl_local_read_after_move.npk` | the conditional move and read of `pick_read_after_move`, of a local | refused `MOVE-001` | 1, `MOVE-001` | 1, `MOVE-001` |
| `ctl_pick_single_move.npk` | the consuming arm moves `x` once and never reads it | 0 / 0 / 0: one owner, one drop | 0 / 0 / 0 | 0 / 0 / 0 |

So the rule exists and fires on a local. One move out of a consuming binding
is sound, and the recipe and observer read a clean run as 0. What differs is
the binding a consuming `pick` introduces.

## Deduplication

`KNOWN_DEFECTS.md` has no shape at a `pick` binding.
- DEF-102, DEF-104, F-001 and F-002 are loans, and a consuming binding is an
  owner.
- DEF-88 (the compiler's own, 1.5.8b step 6d) made `_` bind nothing in a
  consuming arm. That is a different construct, and its fix is in both
  compilers.
- The lending form (`pick (e)`) is the view rule of D-266, and the grid's
  `pick_view` cells are refused as that rule says (`TYPE-047` for a move,
  `TYPE-066` for a write).

**Present at both compilers, with identical verdicts: an old defect, not a
regression.**

## Measured, and inferred

- *Measured:* the verdicts above, and the grid's 44 cells. Each ran once per
  compiler; the finding's programs ran twice at HUNT2.
- *Inferred, not measured:* the move analysis does not track a consuming
  binding's moved-from state, because it does not see the binding as an owning
  local. F-006 (the binding is never dropped at the arm's end) may be the
  emitter's half of the same omission. The two are kept apart because they are
  different rules (the move rule and the arm's drop), with different verdicts.
