# F-039 — AST_REFERENCE: four places where the compiler departs from the reference safely (lower priority)

None of these is a wrong answer at run time or a memory fault. The rows, with each claim's
program and its verdicts at HUNT2 `9126350`, the baseline `c3bdae2` and the newest `main`
`93bcb66`, are in [`ROWS.md`](ROWS.md). Every row gives the same result at all three.

**a. A `comptime` value parameter is a hole the compiler names** (`as0062`)
- AST:62–74 gives a generic parameter's second kind, `<comptime int32:LEVEL>`.
- `func:scale<comptime int32:K> = int32(int32:x) never fails { pass (x * K); };` called as
  `scale::<3i32>(2i32)` passes the checker. It is then `NITPICK-EMIT-002`: "the emitter
  could not lower this, although the frontend accepted it; a defect in the compiler rather
  than in this program".
- This is F-027 b's kind: the compiler names its own hole.

**b. The backward pipe takes its function on the right** (`as0301`)
- OP:378: "`<|` Pipe Backward — evaluates the right expression first, passes to the left
  function", example `func() <| val`. AST:301 lists `|>` / `<|`.
- `dbl <| x` is TYPE-007: "the right side of a pipe is the function the value is passed
  to, and this is not a function".
- Measured by hand at HUNT2 and `93bcb66`: `(x <| dbl) ?| 0i32` with x = 5 is 10. So `<|`
  takes the value on its left and the function on its right, exactly as `|>` does.
- F-031's row `op0378` recorded `func() <| val` as refused because the function side
  was a call. That reading was incomplete: `func <| val` is refused too.

**c. A `joins` deadline that is no constant expression is accepted** (`as0555`)
- AST:555: `joins <const Duration>`, "Constant-expression only".
- `thread async func:t = NIL(int64:_~n) joins raw duration_secs(1i64) { … };` compiles.
- So does a deadline computed from the thread function's own parameter,
  `joins raw duration_secs(n)`. This was measured by hand at HUNT2 and `93bcb66`.

**d. An attribute the language does not have is accepted and ignored** (`as0583`)
- AST:583: `#[lexical_drop]` and `#[nll_drop]` are removed.
- A struct carrying `#[lexical_drop]` compiles. So does one carrying
  `#[nosuch_attribute]`, measured by hand at HUNT2 and `93bcb66`.
- So no attribute name is checked, and a misspelt `#[derive]` or `#[align]` is silent.

## Deduplication

- None of the four is in KNOWN_DEFECTS.md, the registry at `93bcb66`, or F-027 …
  F-036's rows.
- Row b corrects F-031's reading of `op0378` (above). It does not change that row's
  verdict.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and the hand runs named.
- **Reasoned, not measured:** that each is the compiler's departure.
