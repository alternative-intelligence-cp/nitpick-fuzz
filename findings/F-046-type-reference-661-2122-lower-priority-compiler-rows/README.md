# F-046 — TYPE_REFERENCE 661–2122: three places where the compiler departs from the reference safely (lower priority)

None of these is a memory fault or a wrong answer at run time. The rows, with each claim's
program and its verdicts at HUNT2 `9126350`, the baseline `c3bdae2` and `93bcb66`, are in
[`ROWS.md`](ROWS.md). Every row gives the same result at all three.

**a. An assignment to a frac's `.num` passes the checker, and the emitter names its own
hole** (`ty1649`)
- TYPE:1649–1650: "**Members `.whole` / `.num` / `.denom`** are read-only component views
  (values, not places — the invariants cannot be broken through them)".
- `a.num = 2i32;` is not refused by the checker. It reaches the emitter, which reports
  `NITPICK-EMIT-002`: "the emitter could not lower this, although the frontend accepted it;
  a defect in the compiler rather than in this program".
- This is F-039 a's kind: the compiler names its own hole, and the program is refused in
  the end.

**b. A `fixed` parameter is reassigned** (`ty1873`)
- TYPE:1872–1876: "A parameter the callee may not reassign. … every one of these is
  `NITPICK-ASSIGN-002`".
- `func:g = int32(fixed int32:x) never fails { x = 2i32; pass x; };` compiles, and `g(1)`
  returns 2. This was measured by hand at three compilers.
- The parameter is the callee's own copy, so nothing outside the callee changes. When the
  `fixed` binding is a byte view, the caller's bytes do change: that is
  [F-047](../F-047-a-fixed-byte-view-is-not-immutable/).

**c. The backward pipe takes its function on the right** (`ty2084`)
- TYPE:2084: "`f <| v` = `f(v)`". `m11dbl <| x` is TYPE-007, "the right side of a pipe is
  the function the value is passed to".
- This is AST's F-039 b, met in TYPE's words. OP:378 and AST:301 say the same as TYPE.

## Deduplication

- Rows a and b are not in KNOWN_DEFECTS.md, the registry at `93bcb66`, or F-027 … F-045.
- Row c is F-039 b's shape.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and row b's returned value, by hand.
- **Reasoned, not measured:** that each is the compiler's departure.
