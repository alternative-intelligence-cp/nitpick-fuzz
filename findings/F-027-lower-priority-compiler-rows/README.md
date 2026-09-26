# F-027 — sixteen claims where the compiler departs from the reference safely: accepted though refused, a hole the compiler names, refused though permitted, a diagnostic (lower priority)

None of these is a wrong answer at run time or a memory fault. Each is one sentence and
one program, so they share a directory, as F-017's rows do (PROGRESS.md S38). The rows,
with each claim's program and its verdicts at the three compilers, are in
[`ROWS.md`](ROWS.md). Every row gives the same result at HUNT2 `9126350`, the baseline
`c3bdae2` and the newest `main` `1b4f0c6`.

**a. Accepted, though the reference refuses it** (7 rows)
- the `f512` suffix (`ty0178`), which TYPE:178 says is gone and LEXICAL:315's suffix
  production lacks (`f32 | f64 | f128`);
- the `flt32` suffix (`ty0189b`: TYPE:189 says `3.14flt32` "never lexed");
- `flt256` as a type (`ty0176`): accepted by the checker and then `EMIT-002` (see b);
- a `fixed` qualifier spliced into a struct body, silently stripped (`mc0085b`: MACRO:85
  says it is refused rather than stripped);
- a self-invoking macro declaration, accepted while never invoked (`mc0246`: MACRO:246
  marks it `// refused`);
- the lock levels: a send on a level-4 channel while a level-5 guard is held is
  accepted (`cc0380`: CONCURRENCY:380, DECISIONS:5120 "LEVEL is the D-056 lock level");
  and a `dyn` method with no declared level may acquire one (`vf0831`:
  VERIFICATION:831).

**b. The compiler names its own hole** (2 rows, plus `ty0176` above)
- `suspend_until` in a synchronous function passes the checker and is `EMIT-002`, whose
  message says "a defect in the compiler rather than in this program" (`bi0256`,
  session 6's candidate);
- an invocation inside a `while`'s `decreases` measure is never expanded:
  `NITPICK-MACRO-006` says "this is a hole in the expander" (`mc0278`: MACRO:278 says
  the walk reaches every statement kind).

**c. Refused, though the reference permits it** (5 rows; the workbench decides whether
the compiler or the text moves)
- a string literal in `cstring` position is `TYPE-007` (`ty0285`, `ty0290`, `ty0414`:
  TYPE:290 and TYPE:414, "literal — checked at compile time"). D-049 does not settle it;
- an alias of a declaration macro at module level is `MACRO-005` (`mc0046b`: MACRO:46,
  D-125, "is whatever `b` is"). The expression and statement aliases agree;
- comptime does not fold `a.cmp(b)` on strings, `TYPE-004` (`mc0309b`: MACRO:309's
  evaluator table).

**d. A diagnostic that says less than the reference states** (2 rows)
- the round bound's `MACRO-004` names neither macro of the chain and points at
  `prelude.npk:17:1` (`mc0251`: MACRO:251);
- a comptime failure names the division but not the call chain (`mc0344`: MACRO:344).

## Deduplication

None of these shapes is in `KNOWN_DEFECTS.md`: DEF-131/DEF-132 are other `EMIT-002`s,
and DEF-96 is `main`'s signature. Every row is present at the baseline.

## Measured, and inferred

- **Measured:** each row's result at three compilers (`ROWS.md`, from
  `results/9126350/m11.jsonl` and `results/<commit>/m11-disagree.jsonl`).
- **Reasoned:** which side is wrong in (c), where the reference promises a feature the
  compiler does not build.
