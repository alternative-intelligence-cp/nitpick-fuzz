# F-032 — CONTROL_REFERENCE: six sentences the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over CONTROL_REFERENCE (all 415 lines) at HUNT2: 110 claims, 108 tested
(43 of them linked to the M10 item that tests exactly their sentence), 98 agree, 10
disagree. The 10:
- six documentation rows (below);
- four known:
  - DEF-133 (F-017 d6), the `for` binding's refusal code;
  - DEF-130 twice (F-014), `till` with a non-positive limit;
  - DEF-135, the compiler seat's own: a `tbb` bound holding ERR ran the loop in silence.

  DEF-130's and DEF-135's agree at `93bcb66`.

The rows, with each claim's program and its verdicts at HUNT2, the baseline and the
newest `main` `93bcb66`, are in [`ROWS.md`](ROWS.md). All six give the same result at
all three.

- **Examples that do not compile as written.**
  - The fallthrough example (CONTROL:34) calls `println`, which no prelude declares.
  - The guards-and-macros example (CONTROL:80) matches `MyMacro!(a, b) where (a > b)`.
    The macro pattern is removed (MACRO:374), and a macro is invoked as `#name(args)`.
- **Diagnostic codes the compiler does not emit.** §4.2 (CONTROL:314–319) names
  `NITPICK-IF-002` (an assignment in an `if`), `NITPICK-IF-001` (an `else` without an
  `if`) and `NITPICK-WHEN-001` (an orphaned `then`/`end`). Each program is refused, but
  with a `PARSE` code. OP:65 says as much for IF-002: it "describes a diagnostic for a
  program that cannot be written".
- **A builtin that was removed.** "`ok()` is the taint-clearing builtin" (CONTROL:347):
  `ok` is removed (D-097; OP:172 says so, and its claim agrees).

**Agreements worth naming.**
- The lending `pick`'s view rules all refuse as stated: a `move` of a view is
  `TYPE-047`, a copy of an owning view `TYPE-046`, an assignment to a view `TYPE-066`, a
  write of the frozen selector `TYPE-067`. An arm that binds nothing may write the
  selector, and a consuming `pick` leaves its selector moved-from.
- So do the `Optional` selector refusal (`TYPE-065`), `when`/`then`/`end`, the labelled
  `break`, `#unreachable()`, the head checks of `loop` and `till`, and every flow rule.

**Found in run 1, not a finding:** a unit variant's pattern is written qualified,
`(St.A)`, while a payload variant's `(Som(x))` is not. Six programs and one agreeing
refusal (`ct0032f`) were re-spelled.

## Deduplication

None of these sentences is among F-028's rows (DEF-154). The `ok()` row is CONTROL's
sentence, where F-031 is OP's. The registry at `93bcb66` has no entry for any of the six.

## Measured, and inferred

- **Measured:** each row's result at three compilers.
- **Reasoned:** that the compiler is the right side in each.
