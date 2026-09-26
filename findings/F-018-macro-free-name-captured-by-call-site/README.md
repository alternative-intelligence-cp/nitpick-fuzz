# F-018 — a macro's free name reads the call site's local when it stands alone or is a comparison's operand (a silent wrong answer)

**The shape.** MACRO_REFERENCE §4:146: "An identifier in a macro body resolves where
the macro was written, always." With a module binding `fixed int32:lvl = 7i32;` and a
local `lvl` of 3 at the invocation site, the macro reads the **local**:
- when the body is the lone identifier (`macro:m1 = () { lvl; };`), and
- when the name is a comparison's operand in a statement macro
  (`if (lvl == 3i32) { … }`).

Inside arithmetic (`lvl + 0i32`) the same name reads the module's 7, as the reference
says. No diagnostic is given: the program runs with the wrong binding's value.

Found by M11's claims `mc0188` (MACRO:188, "`#caller(NAME)` differs from the bare name
exactly when the invocation site has a local binding of it") and `mc0202` (MACRO:202,
a statement invocation's free name "reads the module binding past the caller's local").
Both exit 11 at HUNT2. The claims `mc0146` and `mc0203` state the same rule and agree,
because their bodies read the name through `+`.

## Verdicts

Each program exits 0 on the reference's answer (the module's 7) and 10 on the call
site's local (3). Measured twice at HUNT2, once at the baseline and once at the
compiler's newest `main` (`VERDICTS.txt`, `VERDICTS-1b4f0c6.txt`).

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `h1_lone_identifier` — `{ lvl; }` | npkc 0, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `h2_comparison_operand` — `if (lvl == …)` in a statement macro | npkc 0, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `ctl_h3_arithmetic_operand` — `{ lvl + 0i32; }` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_h4_statement_arithmetic` — `int32:t = lvl + 0i32; if (t == …)` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns macro expansion or name resolution in a macro
body. The shape is present at the baseline, so it is old, not a regression.

## Measured, and inferred

- **Measured:** the four programs' verdicts above, on both legs, at three compilers.
  The probes behind them (session 7's scratch) also showed `{ lvl + 0i32; }` reading 7
  and an arithmetic-first statement body reading 7.
- **Inferred, not measured:** that the resolver marks an identifier as the macro's own
  when it sits under an arithmetic operator, and misses a lone identifier and a
  comparison's operand. Only the pattern of outcomes was measured, not the mechanism.
