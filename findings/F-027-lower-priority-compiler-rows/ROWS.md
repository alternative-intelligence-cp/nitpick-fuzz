# F-027 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `1b4f0c6`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-027 a: `flt256` passes the checker and is refused by the emitter (EMIT-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0176` | TYPE_REFERENCE.md:176 | `flt256` is not a type: a binding declared with it is refused. | `refuse` | npkc 1 EMIT-002, - / - | same | same |

**F-027 a: a `fixed` qualifier spliced into a struct body is stripped, not refused**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0085b` | MACRO_REFERENCE.md:85 | A variable declaration carrying a qualifier (`fixed`) spliced into a struct body is refused rather than stripped: "a field has neither". | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 a: a channel's LEVEL is not checked against a held mutex's (a downward send is accepted)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0380` | CONCURRENCY_REFERENCE.md:380 | A channel's LEVEL is a D-056 lock level: a send on a level-4 channel while holding a level-5 mutex guard is a downward acquisition and is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 a: a dyn method with no declared level may acquire one**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0831` | VERIFICATION_REFERENCE.md:831 | An undeclared dynamically dispatched method may not acquire at all: an impl of a trait method with no level acquiring one is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 a: a self-invoking macro declaration is accepted while it is never invoked**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0246` | MACRO_REFERENCE.md:246 | `macro:m = () { #m(); };      // refused` — the self-invoking declaration is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 a: the `f512` suffix, gone by TYPE:178 and absent from LEXICAL:315, is accepted**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0178` | TYPE_REFERENCE.md:178 | The `f512` literal suffix is gone: `1.5f512` is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 a: the `flt32` suffix, never a suffix by TYPE:189 and LEXICAL:315, is accepted**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0189b` | TYPE_REFERENCE.md:189 | The spelling `3.14flt32` does not lex: it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-027 b: `suspend_until` in a sync function passes the checker and is EMIT-002**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0256` | BUILTIN_REFERENCE.md:256 | suspend_until is legal only inside an async function: in a sync function it is refused. | `refuse` | npkc 1 EMIT-002, - / - | same | same |

**F-027 b: an invocation in a while's `decreases` measure is never expanded (MACRO-006, a hole it names)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0278` | MACRO_REFERENCE.md:278 | The expansion walk reaches every statement kind (a miss would arrive as a refusal): invocations in an if condition, a while condition and measure, a for body, a pick arm, a when body and then block, a nested block, a struct literal, an array literal, a call argument and a give all expand. | `run:0` | npkc 1 MACRO-006, - / - | same | same |

**F-027 c: a string literal in cstring position is refused (TYPE-007); compiler or documentation**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0285` | TYPE_REFERENCE.md:285 | The example compiles: a char8[5] holds 5 chars, `cstring:cs = "Hello";` is a cstring of length 5, and `to_cstring` of a clean string succeeds. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
| `ty0290` | TYPE_REFERENCE.md:290 | A string literal in cstring position is a cstring: `cstring:cs = "Hello";` compiles with length 5. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
| `ty0414` | TYPE_REFERENCE.md:414 | A string literal in cstring position costs nothing at run time: it is a NUL-terminated constant. | `ir:constant \[4 x i8\] c"abc\\00"` | npkc 1 TYPE-007, - / - | same | same |

**F-027 c: an alias of a declaration macro is refused at module level (MACRO-005), against D-125**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0046b` | MACRO_REFERENCE.md:46 | "is whatever `b` is": an alias whose target is a declaration macro, invoked at module level, emits the target's declarations. | `run:0` | npkc 1 MACRO-005, - / - | same | same |

**F-027 c: comptime does not fold `a.cmp(b)` on strings (TYPE-004); compiler or documentation**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0309b` | MACRO_REFERENCE.md:309 | The evaluator handles string ordering: "ab" orders before "b". | `run:0` | npkc 1 TYPE-004, - / - | same | same |

**F-027 d: MACRO-004 names neither macro and points into prelude.npk**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0251` | MACRO_REFERENCE.md:251 | Exceeding the iteration bound is a compile error naming the macro and the chain that reached the bound: both ping_m and pong_m appear in the diagnostic. | `sh:0` | script 3 | same | same |

**F-027 d: a comptime failure's diagnostic names no call chain**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0344` | MACRO_REFERENCE.md:344 | A comptime failure inside nested comptime calls names the offending expression and the call chain: the diagnostic mentions inner_div and outer_call and points at the division. | `sh:0` | script 3 | same | same |
