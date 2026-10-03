# F-045 — the compiler's message for `??` on a `Result` advises the bare `?`, which the compiler refuses (lower priority: a diagnostic)

**The shape.** `??` applied to a `Result` is refused, rightly: `??` is the `Optional`
unwrap (TYPE:1375, D-099). The message says what to write instead:
```
NITPICK-TYPE-007 …: `??` unwraps an `Optional`, and this is `Result<int32>`; `?` is the one that unwraps a `Result`
```
A programmer who follows the advice is refused next:
```
NITPICK-PARSE-011 …: a bare `?` is not the `Result` fallback (D-175): write `expr ?| fallback` — `?` reads as Rust's error-propagation, but Nitpick's fallback yields a value
```
So the first message names the spelling that D-175 retired. The right one is `?|`, and the
control compiles with it and runs 0.

Found while screening M11's agreeing refusals for TYPE 1177–1592: `ty1375`'s refusal
carries the first message, and `ty1374`/`ty1387` the second (F-044's rows: TYPE:1374
and :1387 still spell the bare `?`). No claim disagrees for it, since the refusal is right
and only its advice is wrong.

## The programs

| program | what it is | measured |
|---|---|---|
| `d1_coalesce_on_result` | `k(…) ?? 7i32` on a `Result<int32>` | npkc 1, TYPE-007, the message advising `?` |
| `d2_the_advice_followed` | `k(…) ? 7i32`, the advice followed | npkc 1, PARSE-011 (D-175) |
| `ctl_d3_fallback` | the control: `k(…) ?| 7i32` | npkc 0, 0 / 0 |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`, by `gen/run_findings.py`)

All three programs give the same result at HUNT2 `9126350` (both runs), at the baseline
`c3bdae2` and at `93bcb66`. The two messages' texts were read by hand at all three, and
they are identical.

## Deduplication

- KNOWN_DEFECTS.md and the registry at `93bcb66` have no entry for the message.
- F-030, F-031 and F-040 record the bare `?` in three references' TEXT (PARSE-011, D-175),
  and F-044 records it in TYPE's. This finding is the compiler's own text recommending it.

## Measured, and inferred

- **Measured:** each program's result, and both messages' texts, at three compilers.
- **Reasoned, not measured:** that the advice was written before D-175 and missed when
  D-175 retired `?`.
