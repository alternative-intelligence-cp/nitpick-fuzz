# F-019 — a `\u{…}` character escape is a `char8`, truncated to its low byte; a `char32` cannot take it (a silent wrong answer)

**The shape.** TYPE_REFERENCE §2.3:280 writes `char32:emoji = '\u{1F600}';  // Unicode
escape (char32 only)`. At HUNT2 the escape's literal is typed `char8`:
- `char8:c = '\u{1F641}';` compiles, and `c` is `'A'`, the low byte 0x41 of U+1F641.
  (`'\u{1F600}'` gives 0, and `'\u{E9}'` gives 233.)
- `char32:emoji = '\u{1F600}';` is refused, `NITPICK-TYPE-007`: "expected `char32`,
  found `char8`".

So the one construct the reference names for code points above a byte cannot make a
`char32`, and in a `char8` it silently keeps the low byte of any code point.

Found by M11's claims `ty0272` (the §2.3 example block) and `ty0280` ("The `\u{...}`
escape is for char32 only: in a char8 slot it is refused").

## Verdicts

`u1` exits 10 when the code point came out as `'A'`; the reference's answer is a
refusal. `u2` exits 0 on U+1F600; the reference's answer is npkc 0 and exit 0.

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `u1_char8_takes_high_codepoint` | npkc **0**, **10 / 10** | 0, **10 / 10** | 0, **10 / 10** |
| `u2_char32_refuses_escape` | npkc **1**, `TYPE-007` | 1 | 1 |
| `ctl_u3_char32_numeric` — `128512char32` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_u4_char8_hex_escape` — `'\x41'` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns character literals or their escapes. The
shape is present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts above, plus three probe values in `char8`: `'\u{1F600}'`
  is 0, `'\u{E9}'` is 233 and `'\u{1F641}'` is `'A'`.
- **Inferred:** that the lexer types every quoted character literal `char8` and stores
  the escape's value modulo 256. The three values fit that reading.
