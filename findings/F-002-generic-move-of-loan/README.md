# F-002 — `move(x)` of a lent `T` in a generic body frees the caller's value

**The shape.** In a generic function whose parameter is lent (an ordinary
`T:x`, not `move T:x`), `T:y = move(x);` compiles. Instantiated at an owning
type, `y` takes ownership of what the caller still owns, and `y`'s drop frees
it. The caller's read then sees the free poison (**70**), and the caller's own
drop frees it again (**95**). The same function written for `string` is
refused `NITPICK-TYPE-047`.

**The grid's cells** (4; the same verdicts at HUNT `6fb85d3` and at the
baseline `c3bdae2`): `c0887`/`c0888` (`gen_str`), `c0945`/`c0946` (`gen_box`).
The `ra` cells exit 70/70 and the `dx` cells 95/95.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py`, at HUNT twice and at the baseline once. Every line is in
`VERDICTS.txt`. The two HUNT runs agree for every program. Each cell below
gives npkc's rc / the -O0 exit / the -O2 exit.

| program | what it does | HUNT `6fb85d3`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `gen_move_read.npk` | `func:take<T> = NIL(T:x) { T:y = move(x); … }`; `drop take::<string>(s);` then read `s` and exit before any drop | 0 / **70** / **70** | 0 / **70** / **70** |
| `gen_move_drop.npk` | the same call in `run`, which returns normally so every drop runs | 0 / **95** / **95** | 0 / **95** / **95** |

## The controls

| control | what differs | expected | HUNT, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_concrete_move.npk` | `take` written for `string`: `func:take = NIL(string:x) { string:y = move(x); … }` | refused `NITPICK-TYPE-047`, the rule the generic body escapes | 1, `TYPE-047` | 1, `TYPE-047` |
| `ctl_gen_move_param.npk` | the same generic body with the parameter declared `move T:x`, called as `take::<string>(move(s))`, the moved value passed back and read in `run`, then every drop run | 21: the value intact, owned once | 0 / 21 / 21 | 0 / 21 / 21 |

So the rule exists and fires on the concrete spelling. A generic move of an
*owned* `T` is sound, and the observer and recipe read an intact value as 21.
What differs is a lent `T` moved under a type parameter.

## Deduplication

This is DEF-104's family, but not a shape `KNOWN_DEFECTS.md` names. DEF-104 is
"a lent `T` in a generic body escapes the loan rules", and its fix (1.6.0 step
3g) names two operations: a **pass-out**, refused `TYPE-047`, and **`@x` of a
lent `T`**, refused `TYPE-085`. The grid's cells of those two operations are
deduplicated as DEF-104: `c0889`/`c0890`, `c0947`/`c0948` (`pass_out`), and
`c0895`/`c0896`, `c0953`/`c0954` (`at_free`). The explicit **`move`
operator** is not named.

- **Measured:** the copy of a lent `T`, `T:y = x;`, is refused
  `NITPICK-TYPE-046` at both compilers (grid `c0885`/`c0886`,
  `c0943`/`c0944`); that is DEF-23/O-N19, fixed by the compiler's D-264. The
  concrete move is refused `TYPE-047` (`ctl_concrete_move`). Among the
  operations that take ownership, the move is the one the grid finds unasked in
  a generic body, besides DEF-104's pass-out.
- **Read in the source at `6fb85d3`, not measured:** `move(x)` and `pass x`
  ask one function, `refuse_move_of_borrowed`
  (`src/frontend/type_expr.npk:510`). It is called by the `move` operator at
  `type_expr.npk:4004`, and by `pass` at `src/frontend/type_stmt.npk:2029`,
  whose comment calls it "the same rule `move(p)` answers to, asked of the
  implicit move". It returns early at line 515,
  `if (!(raw type_drops(@pr, ty, e.scope, 64i32))) { pass NIL; }`.
- **Inferred:** for an unsubstituted `T`, `type_drops` answers that it does
  not drop. That one early return would let both DEF-104's `pass x` and this
  `move(x)` through. If 3g's fix is made inside `refuse_move_of_borrowed`, it
  covers this finding; if it is made at `pass` alone, it does not. 3g is not in
  HUNT, so this is not measurable here. Running `gen_move_read.npk` and
  `gen_move_drop.npk` at the 3g commit settles it.

## What was measured, and what is inferred

**Measured:**
- every verdict above, at both compilers, on both legs, the HUNT ones twice;
- the minimisation: `minimized/` holds `gen/minimize.py`'s output for `c0887`
  (29 lines) and `c0888` (26 lines). The minimiser deletes lines and
  brace-balanced blocks while the verdict stays exactly the cell's, and never
  deletes a bare `pass`/`exit`. Both reproduce their cells' verdicts at both
  compilers (`VERDICTS.txt`). The programs above are those, with the grid's
  full observer and fail-safe restored and renamed.

**Inferred, not measured:** the mechanism. The lent `x` is a copy of the
caller's header (D-065, "passing transfers nothing"). The unasked `move(x)`
makes `y` a second owner of the same heap body, and `y`'s drop at the end of
`take` frees it while the caller still owns it. This is DEF-104's mechanism,
with `move` in place of `pass`.
