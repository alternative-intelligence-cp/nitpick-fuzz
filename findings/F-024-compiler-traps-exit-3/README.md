# F-024 — npkc traps (exit 3, no diagnostic) on three shapes: a macro emitting a method into an impl, a 500-deep expression, a macro emitting a comptime function

**The shape.** npkc's own `failsafe` maps every trap to exit 3 (`src/npkc.npk:285`,
D-179), so exit 3 with empty output is a trap inside the compiler. Three programs,
each small, reach it:
- **`c1`** (MACRO_REFERENCE §3:136, the `emit_methods` example): a macro whose body
  declares a method, invoked in an `impl` body.
- **`c2`**: a parenthesised expression nested 500 deep, `(1i32 + (1i32 + (…)))`, with
  or without a macro. 250 deep compiles. MACRO_REFERENCE §5:250 promises a depth bound
  reported as a compile error for an expansion. Measured, the bound is a trap, and it is
  not the macro's: the plain expression traps too.
- **`c3`** (MACRO_REFERENCE §6:327): a macro that emits a `comptime` function, then
  `comptime(sq_e(7i32))`. The reference says expansion runs to a fixed point first, so
  the emitted function can be evaluated.

Found by M11's claims `mc0136`, `mc0250` (with `mc0256`'s "deep" half) and `mc0327`.
All are npkc 3 at HUNT2.

## Verdicts

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `c1_macro_method_into_impl` | npkc **3** | 3 | 3 |
| `c2_nested_expression_500` | npkc **3** | 3 | 3 |
| `c3_macro_emits_comptime_function` | npkc **3** | 3 | 3 |
| `ctl_c4_nested_expression_250` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_c5_comptime_function_direct` — the function written directly | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

No entry of `KNOWN_DEFECTS.md` is a compiler trap. All three shapes are present at the
baseline.

## Measured, and inferred

- **Measured:** the exit codes, and that the output is empty.
- **Not measured:** which trap each is. The compiler's `failsafe` does not say.
  `c2`'s depth threshold lies between 250 and 500; it was not bisected further. A stack
  exhaustion is the obvious guess for `c2`, but it is a guess.
