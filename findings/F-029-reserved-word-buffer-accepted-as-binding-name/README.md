# F-029 — the reserved word `buffer` is accepted as a `wild` pointer binding's name, then cannot be referenced (lower priority)

**The shape.** LEXICAL_REFERENCE:122 lists `buffer` among the reserved type words, so it
names no binding. A plain binding named `buffer` is refused at its declaration
(`int64:buffer = …;`, `PARSE-002`), as `pid` is (KNOWN_DEFECTS.md: "a binding … named
after one is refused at its declaration"). But a `wild` pointer binding named `buffer`
**is accepted**:
```
wild int8->:buffer = alloc(16i64);    // accepted
dalloc(buffer);                       // PARSE-002 "expected an expression"
```
Its first use is refused, so the block it holds can never be freed. This is DEF-103's
shape (a keyword accepted as a declared name, then unusable), seen at a binding.

MEMORY_REFERENCE's own examples at lines 121 and 184 name their binding `buffer`. The
first compiles only because the example never uses it. Found by M11's run 1 of
`me0120`, `me0179` and `me0183`. `me0179` had **agreed** for this reason (its expected
refusal was the `move`'s), and its program was re-spelled (S53, S55).

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`)

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | newest `main` `93bcb66` |
|---|---|---|---|
| `k1_wild_buffer_declared` — declared, then `exit 3` | npkc **0**, 3 / 3 | 0, 3 / 3 | 0, 3 / 3 |
| `k2_wild_buffer_declared_then_used` | npkc 1, `PARSE-002` at the use | 1 | 1 |
| `ctl_k3_int64_buffer_refused` | npkc 1, `PARSE-002` at the declaration | 1 | 1 |
| `ctl_k4_wild_buf` — the same with `buf` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

The reference's answer for `k1` is a refusal at the declaration.

## Deduplication

DEF-103 covers a keyword as a declared function or type name, refused `PARSE-001` since
1.6.0 step 3g. This is a binding's name in the `wild` pointer form, unrefused at all
three compilers. KNOWN_DEFECTS.md's keyword list does not include `buffer`, and the
registry at `93bcb66` has no entry for it.

## Measured, and inferred

- **Measured:** the four programs at three compilers.
- **Inferred:** that the declaration parser takes a name after `wild T->:` without the
  keyword check the plain form applies. Only the pair of outcomes was measured.
