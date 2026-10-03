# F-048 — a struct with a `NIL` field is accepted, and its IR is refused by `llc` and `opt`

**The shape.** TYPE_REFERENCE §27, :1944–1946: "**`NIL` is zero-sized** (D-084). Its only
value carries no information, so it occupies nothing: a `NIL` struct field takes no
space." At HUNT2, `struct:S = { int32:a; NIL:n; };` passes the checker, and the emitter
writes
```
%"npk.n1_nil_field.S" = type { i32, void }
```
which LLVM refuses: `llc: error: … void type only allowed for function results`, and `opt`
likewise. Neither leg builds, whether the struct is only measured (`#size_of`) or built
and read.

This is F-023's class: accepted, then invalid IR. The compiler's output is not a program.

Found by M11's claim `ty1944` (TYPE 1593–2122, part C): npkc 0, then `llc!1`/`opt!1`.

## The programs

| program | the reference's answer | measured |
|---|---|---|
| `n1_nil_field` (`#size_of<S>()` is 4) | 0 | npkc 0, llc 1 / opt 1 |
| `n2_nil_field_built` (`S{ a: 7, n: NIL }`, `s.a` read) | 0 | npkc 0, llc 1 / opt 1 |
| `ctl_n3_no_nil_field` (the control: the struct without the `NIL` field) | 0 | npkc 0, 0 / 0 |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`, by `gen/run_findings.py`)

Every program gives the same result at HUNT2 `9126350` (both runs), at the baseline
`c3bdae2` and at `93bcb66`.

## Deduplication

- KNOWN_DEFECTS.md has no entry for it.
- The registry at `93bcb66` has none either. D-084 states the size; nothing records the
  lowering.
- F-023 is another construct with the same outcome.

## Measured, and inferred

- **Measured:** each program's result and the IR line, at three compilers.
- **Reasoned, not measured:** that the emitter maps a `NIL` field to LLVM `void` where it
  should drop the field. `Result<NIL>`, which is `{ i32 }`, shows that it knows how to
  (`ty1957` and `ty1957b` agree).
