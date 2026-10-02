# F-031 — OP_REFERENCE: five sentences the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over OP_REFERENCE (all 403 lines) at HUNT2: 159 claims, 157 tested (38
of them linked to the M10 item that tests exactly their sentence), 148 agree, 9
disagree:
- five documentation rows (below);
- `<=>` twice, DEF-131 (F-015), which compiles and runs at `93bcb66`;
- two claims whose programs could not test their sentence (not findings):
  - "`|` binds tighter than `&&`" (row 28) has no well-typed test: `|` takes integers,
    `&&` booleans;
  - `!!b` is two negations, not the struck `!!` token.

The rows, with each claim's program and its verdicts at HUNT2, the baseline and the
newest `main` `93bcb66`, are in [`ROWS.md`](ROWS.md). All five give the same result at
all three.

- **A surface the language does not have.** `**`, "Exponentiation (Standard Library
  expansion)" (OP:88): `2 ** 8` does not parse.
- **Examples in a stale spelling.**
  - The ternary `is x > 0 : 1 : -1` (OP:374) needs its condition in parentheses
    (`PARSE-001`), as TYPE:2101 writes it: `is (cond) : then : else`.
  - The pipes `val |> func()` and `func() <| val` (OP:377–378) are refused (`TYPE-007`).
    A pipe's other side is the function itself: `val |> func` compiles, and its result
    is a `Result` that `?|` unwraps.
- **A sentence that contradicts its own reference.** "Only an explicit check (`is_err`)
  or a fallback (`?`) leaves the [ERR] state" (OP:171). The bare `?` is struck (OP:73,
  D-175), and `?|` "take[s] a `Result` and nothing else", an ERR being handled "by
  `is_err` or a `pick` `ERR:` arm, never by `?|`" (OP:257).

**Agreements worth naming.** The Optional surface (`T?`, `??`, `?.`) all compiles and
behaves as written. So do the wrapping family and its compound forms, `#`, `$$i`/`$$m`,
`_?`/`_!`/`_^`/`_~`, `!!!`, every literal and comment form, and every precedence row
that can be tested.

## Deduplication

None of these is among F-028's rows (DEF-154), which hold no OP sentence. The registry
at `93bcb66` has no entry for them.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and the pipe's working spelling
  (a probe in session 8's scratch).
- **Reasoned:** that the compiler is the right side in each.
