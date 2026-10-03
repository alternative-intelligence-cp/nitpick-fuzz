# F-047 — a `fixed uint8[]` view is not immutable: a write through it is accepted and lands, a callee's included

**The shape.** TYPE_REFERENCE §22, :1716–1719, quoting D-074: "immutability is a **binding**
property in Nitpick rather than a type property, so an immutable byte view is `fixed
uint8[]`." D-074 retired the `binary` type on that ground. At HUNT2 a write through a
`fixed uint8[]` is accepted and changes the bytes it views:
```
func:m11w = NIL(fixed uint8[]:v) never fails { v[0i64] = 9u8; pass NIL; };
...
uint8[4]:arr = [1u8, 2u8, 3u8, 4u8];
drop m11w(arr[0i64...4i64]);      // arr[0] is now 9
```
So a function that declares its parameter an immutable byte view can rewrite its caller's
bytes, and the caller is told nothing.
- `fixed` is enforced on a scalar local (ASSIGN-002, the control `s4`).
- It is not enforced on what a `fixed` slice views.

Found by M11's claim `ty1719b` (TYPE 1593–2122, part C): the refusal was expected, npkc 0
and exit 0 were measured. Re-measured with the programs here.

## Why a silent wrong answer

The caller's array holds a value the reference says no code can have written through that
view. The compiler accepts the write, and the program's result differs from what the
reference says it must be, with no error. That is the author's rule of 2026-09-26.
*Reasoned:* the class is a judgment. A reading where `fixed` fixes only the view (its
pointer and length) and not the bytes would make this TYPE:1719's documentation error
instead. D-074 retired `binary` on the claim that `fixed uint8[]` is its immutable
replacement, so this report takes the reference at its word.

## The programs

| program | the reference's answer | measured |
|---|---|---|
| `s1_fixed_view_written` (a local `fixed uint8[]` view written) | refused | npkc 0, 10 / 10: the write landed |
| `s2_fixed_param_written` (a callee writes through its `fixed uint8[]` parameter) | refused | npkc 0, 10 / 10: the caller's bytes changed |
| `ctl_s3_plain_param_written` (the control: the same callee over a plain `uint8[]`) | 0, the write lands | npkc 0, 0 / 0 |
| `ctl_s4_fixed_scalar_written` (the control: a `fixed int32` written again) | ASSIGN-002 | npkc 1, ASSIGN-002 |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`, by `gen/run_findings.py`)

Every program gives the same result at HUNT2 `9126350` (both runs), at the baseline
`c3bdae2` and at `93bcb66`.

## Deduplication

- KNOWN_DEFECTS.md has no entry for it.
- The registry at `93bcb66` has none either. Its DEF-72 (FIXED, D-313) is the headers of
  compiler-known containers, not a `fixed` view's elements.
- F-046 b (a `fixed` parameter reassigned) is the same keyword on a scalar parameter, with
  no effect outside the callee.

## Measured, and inferred

- **Measured:** each program's result at three compilers, both legs.
- **Reasoned, not measured:** the class (above), and that every element write form (an
  index, `@`, a compound assignment) behaves as the index does. Only the index was run.
