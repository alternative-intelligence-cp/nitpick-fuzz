# F-001 — a write through a `for` binding frees the array's element

**The shape.** In `for (T:x in arr)`, where `T` owns, a write through `x` —
`x.s = …;`, or `@x` handed to a callee that frees or grows the value —
compiles, and it frees heap storage that the array's element still owns. A
read of the element afterwards sees the free poison (**70**), and the array's
own drop frees it a second time (**95**).

**The grid's cells** (16; the same verdicts at HUNT `6fb85d3` and at the
baseline `c3bdae2`): `at_free` — `c0107`/`c0108` (`str`), `c0281`/`c0282`
(`box`), `c0457`/`c0458` (`list`), `c0579`/`c0580` (`wrap`); `at_grow` —
`c0459`/`c0460` (`list`), `c0581`/`c0582` (`wrap`); `field_write` —
`c0275`/`c0276` (`box`), `c0573`/`c0574` (`wrap`). Every `ra` cell exits 70/70
(22/22 for `field_write`), and every `dx` cell exits 95/95.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py`, at HUNT twice and at the baseline once. Every line is in
`VERDICTS.txt`. The two HUNT runs agree for every program. Each cell below
gives npkc's rc / the -O0 exit / the -O2 exit.

| program | what it does | HUNT `6fb85d3`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `for_at_free_read.npk` | in the loop, `drop free_it(@x);` (the callee moves `<-p` out and drops it); then read `arr[0i64]` and exit before any drop | 0 / **70** / **70** | 0 / **70** / **70** |
| `for_at_free_drop.npk` | the same loop in `run`, which returns normally so every drop runs | 0 / **95** / **95** | 0 / **95** / **95** |
| `for_field_write_read.npk` | `Box[2]`; in the loop, `x.s = …;`; then read `arr[1i64].s` | 0 / **70** / **70** | 0 / **70** / **70** |
| `for_field_write_read_elem0.npk` | the same; read `arr[0i64].s` (the grid's observation) | 0 / **22** / **22** | 0 / **22** / **22** |
| `for_field_write_drop.npk` | the same loop in `run`, returning normally | 0 / **95** / **95** | 0 / **95** / **95** |
| `for_at_grow_read.npk` | `List<int64>[2]` of capacity 1; in the loop, `drop grow(@x);` (two pushes, so a reallocation); then read element 0 of `arr[0i64]` | 0 / **70** / **70** | 0 / **70** / **70** |
| `for_at_grow_drop.npk` | the same loop in `run`, returning normally | 0 / **95** / **95** | 0 / **95** / **95** |

The exit codes are the grid's: 21 the original value, 22 the new value, 23
vacant, 70 the free poison `0xAA`, and 95 the fail-safe's `Unreachable` (a
free of what is not live).

## The controls

Each control does the same operation, with the same callee, **through the
array's own element** instead of through the loop's binding. It observes the
element, and `run` returns the observation's code, so every drop runs before
`main` exits with that code. A double free would stop the program as 95 before
it could exit with the code. Each expected code asserts that the operation took
place, not just that nothing failed.

| control | the operation | expected | HUNT, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_elem_at_free.npk` | `drop free_it(@arr[0i64]);` | 23: the element is vacant | 0 / 23 / 23 | 0 / 23 / 23 |
| `ctl_elem_field_write.npk` | `arr[0i64].s = …;` | 22: the new value landed | 0 / 22 / 22 | 0 / 22 / 22 |
| `ctl_elem_at_grow.npk` | `drop grow(@arr[0i64]);`, then `count` must be 3 (24 if not) | 21: grown, element 0 kept | 0 / 21 / 21 | 0 / 21 / 21 |
| `ctl_for_read.npk` | the same loop, reading `x` and writing nothing | 21: intact | 0 / 21 / 21 | 0 / 21 / 21 |

So the callee, the write and the observer each behave when reached through
the owner, and reading through the binding is harmless. What differs is the
write path of the `for` binding. A compiler that dropped the binding at the end
of each iteration would fail `ctl_for_read` (70 or 95), and it does not.

## Deduplication

The place is not in any `KNOWN_DEFECTS.md` shape. DEF-102 is a write through a
lent **parameter**; this is a write through a **`for` binding**. The evidence
that it is DEF-102's defect reached through a second place:

- **Measured:** the compiler already treats this binding as lent when it is
  *moved*. A `move(x)` or `pass x` of it is refused `NITPICK-TYPE-047`, with
  the lent parameter's own message: *"this parameter was lent, not given
  (D-065: passing transfers nothing), so there is no ownership here to move
  on"*. This is grid cells `c0099`–`c0102`, `c0271`–`c0274`, `c0449`–`c0452`
  and `c0569`–`c0572`, at both compilers.
- **Read in the source at `6fb85d3`, not measured:** that message is raised by
  `refuse_move_of_borrowed` (`src/frontend/type_expr.npk:510`) only past
  `if (pd.kind != DeclKind.DeclParamDecl) { pass NIL; }` (line 534). So the
  `for` binding is declared as a parameter declaration, which is why it gets a
  parameter's words.
- **Inferred:** 1.6.0 step 3g's `NITPICK-TYPE-085` is DEF-102's fix, stated as
  "a loan is read-only when it owns", covering every write path. If it asks the
  same lent-parameter question, it refuses these writes too. 3g is not in HUNT,
  so this cannot be measured here. Running the seven `for_*` programs at the 3g
  commit settles it; each should then be refused, and the four controls still
  compile.
- The grid's `for_binding` × `assign` and × `at_overwrite` cells compile and
  run clean at both compilers: `c0103`–`c0106`, `c0277`–`c0280`,
  `c0453`–`c0456`, `c0575`–`c0578`. A whole-binding assignment through the
  loan leaves the element intact, as DEF-102's `ctl_whole_lent_string` does for
  a parameter (21, the caller intact). They are not anomalies by the grid's
  definition, but 3g's rule, which "covers a whole-binding assignment", would
  refuse them too.

## What was measured, and what is inferred

**Measured** (the tables above; the commands are PLAN.md's recipe):
- every verdict, at both compilers, on both legs, the HUNT ones twice;
- the minimisation: `minimized/` holds `gen/minimize.py`'s output for six of
  the cells. The minimiser deletes lines and brace-balanced blocks while the
  verdict (npkc, -O0, -O2) stays exactly the cell's, and never deletes a bare
  `pass`/`exit`. The results are 28–35 lines, and they reproduce their cells'
  verdicts at both compilers (`VERDICTS.txt`). The programs above are those,
  with the grid's full observer and fail-safe restored so that each exit code
  names what it saw.
- Two further probes at HUNT, each built by one `sed` from the element-0
  program with the substitution asserted to match once: a one-element `Box[1]`
  array exits 70/70 (not kept as a file), and observing `arr[1i64]` exits
  70/70 (kept as `for_field_write_read.npk`, and measured again above).

**Inferred, not measured:**
- *The mechanism.* The binding holds the element's value on loan, a copy of
  its header ("passing transfers nothing"). A write that drops the old value,
  or a callee handed `@x` that moves it out or reallocates it, therefore frees
  the heap body that the element still points at. This is DEF-102's mechanism,
  as `KNOWN_DEFECTS.md` states it for a parameter.
- *Why element 0 reads 22 and not 70.* The second iteration's new string is
  allocated in the block the first iteration freed, which element 0 still
  points at. The element written last (`arr[1i64]`) and a one-element array
  read the poison, and no allocation follows their free.
- *A wording observation, not a defect:* `TYPE-047` calls a `for` binding
  "this parameter".
