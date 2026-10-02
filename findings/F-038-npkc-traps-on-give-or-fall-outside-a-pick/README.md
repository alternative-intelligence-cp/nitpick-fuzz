# F-038 — npkc traps (exit 3, no diagnostic) on `give` or `fall` outside a pick arm

**The shape.** AST_REFERENCE:202–203 says `fall label;` and `give e;` are "legal only in a
`PickArm` body". AST_REFERENCE:267 says the parser accepts them anywhere and "the placement
check belongs to semantic analysis", which would refuse them by name. Instead, npkc itself
traps: exit 3, nothing printed.
```
int32:x = raw v32(1i32);
if (x == 1i32) { give 5i32; }   // npkc exits 3
fall nowhere;                    // npkc exits 3
```
A crash of the compiler is CLAUDE.md's lower-priority report. F-024 (three other trap
shapes) is the precedent.

Found by M11's AST claims `as0202`, `as0203` and `as0267` (all three: npkc exit 3).
A `give` at the very end of a function's body is FLOW-001 instead (the function reaches
its end without `pass`), so the trap is reached when the statement is followed by more
code.

## The programs

| program | the reference's answer | measured |
|---|---|---|
| `c1_give_outside_pick` | npkc 1, a refusal naming the placement | npkc **3**, no output |
| `c2_fall_outside_pick` | npkc 1 | npkc **3**, no output |
| `ctl_c3_give_in_pick` (control: `give` in an expression pick) | npkc 0, exits 0 | npkc 0, 0 / 0 |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`)

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | newest `main` `93bcb66` |
|---|---|---|---|
| `c1_give_outside_pick` | npkc 3 | 3 | 3 |
| `c2_fall_outside_pick` | npkc 3 | 3 | 3 |
| `ctl_c3_give_in_pick` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

- KNOWN_DEFECTS.md has no `give`/`fall` placement entry.
- The registry at `93bcb66` has none.
- F-024's three trap shapes are a macro emitting a method into an impl, a 500-deep
  expression and a macro emitting a comptime function. None is this.

## Measured, and inferred

- **Measured:** npkc's exit at three compilers.
- **Reasoned, not measured:** that the checker reaches the statement with no enclosing arm
  and dereferences the missing arm's context. Nothing is printed to say where.
