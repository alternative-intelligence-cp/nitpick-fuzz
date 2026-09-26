# F-017 — seven reference sentences the compiler contradicts, where the compiler is right or at least safe (documentation findings)

PLAN.md 10.2: "If the compiler is right and the reference is wrong, it is a
documentation finding. Report it the same way, with the reference line." M10's
checklist found seven.
- Four are sentences the compiler refuses or answers otherwise (d1, d2, d6,
  d7).
- Three are sentences that contradict another sentence of the same
  reference; the run shows which one the compiler follows (d3, d4, d5).

None is a wrong answer at run time: each program either is refused or runs to
an answer the reference states elsewhere. They are kept together in one
finding because each is one sentence and one program (S38). Line numbers are
HUNT2's (`9126350`); every sentence is also in the baseline's text.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree; at `9f6f370` the same,
`VERDICTS-9f6f370.txt`). Each cell gives npkc / -O0 / -O2, identical at the
three compilers.

| # | the sentence (file:line) | program | measured | control |
|---|---|---|---|---|
| d1 | TYPE_REFERENCE §3.2:367 — "Length: `int64:len = s.length;` → field access" | `d1_string_length_member.npk` | 1, `TYPE-019`: "`string` has no member `length`" | `d1_ctl_string_len_member.npk`: `s.len` (§9.1.1:984, the header word) → 0 / 0 / 0 |
| d2 | TYPE_REFERENCE §3.2:366 — "Indexing: `char8:c = s[0];` → returns the char at that index (bounds-checked)" | `d2_string_index.npk` | 1, `TYPE-007`: "`string` cannot be indexed" | `d2_ctl_string_bytes_index.npk`: `string_bytes(s)[1]` → 0 / 0 / 0 |
| d3 | TYPE_REFERENCE §28:2054 — "`!=` \| not equal \| `icmp ne`/`fcmp one`" | `d3_float_ne_nan.npk`: NaN != NaN | 0 / **0** / **0**: true, so the compiler emits `fcmp une`, as §1.4:187 says. The IR reads `fcmp une`. | — |
| d4 | TYPE_REFERENCE §28:2101 — the ternary "`is (cond) : then : else` \| … \| `select i1 %cond, %then, %else`" | `d4_ternary_one_branch.npk`: `is (d != 0) : 100 / d : 7` with d = 0 | 0 / **0** / **0**: 7 and no trap, so only the chosen branch runs, as VERIFICATION §1.2:68 models it. The IR has `is.then`/`is.else` blocks and no `select`. | — |
| d5 | TYPE_REFERENCE §4:475 — the wide integers have "ordinary integer semantics at every width — D-037 wrapping" | `d5_int128_overflow_traps.npk`: `int128` max + 1 | 0 / **93** / **93**: `IntOverflow`, as §1.2:56–58 says (D-210) | — |
| d6 | CONTROL_REFERENCE §2.3:186–188 — a `for` binding's type must equal the element type, "Anything else is refused at the checker by name (`NITPICK-TYPE-033`)" | `d6_for_binding_type_code.npk`: `for (int32:i in 0i64...3i64)` | 1, **`TYPE-007`**, with the rule's words: "a `for` binding's type is the element type" | — |
| d7 | OP_REFERENCE §1.1:164–165 — "a constant `MIN / −1` or `MIN % −1` is refused as a constant division by zero is (TYPE-004)" | `d7_local_constant_div_zero.npk`: `int32:x = 5i32 / 0i32;` in `main` | 0 / **97** / **97**: accepted, and the run traps `DivByZero` | `d7_ctl_fixed_constant_div_zero.npk`: the same division as a `fixed` initialiser → 1, `TYPE-004` |

## Each, in a sentence

- **d1, d2.** TYPE_REFERENCE §3.2's string surface (`s.length`, `s[i]`) is not the language's.
  - The length is the sealed header word `len` (§9.1.1:984, and BUILTIN's
    `string_byte_length`).
  - A string's bytes are reached through `string_bytes`'s view.
  - §3.2's "Standard functions" table (`charAt`, `substring`, …) is `nlibc`'s
    planned surface, which BUILTIN_REFERENCE §2 says no library builds today.
    Not tested here.
- **d3.** §28's table row contradicts §1.4. The compiler follows §1.4 (`une`,
  so that `!=` stays the negation of `==`), so the row is the stale text.
- **d4.** §28's lowering column says `select`, which would evaluate a
  trapping branch that was not chosen. The compiler branches, and the
  verifier models the branches under their conditions, so the column is the
  stale text.
- **d5.** §4 still says D-037 wrapping for `int128`…`int4096`. §1.2 and D-210
  make every width trap, and the compiler traps, so §4 is stale. (§1.2 also
  cites `wide_ladder.npk` executing "the D-210 trap at 512".)
- **d6.** The refusal is right; its code is not the one named. `TYPE-033` is
  the "not iterable" refusal (M9 measured it for a `for` over a `List`), so
  the sentence names the wrong code for the binding-type rule.
- **d7.** A constant division by zero is refused in a folded context (a `fixed`
  initialiser: the control) and not in a local initialiser, whose division
  reaches the run time and traps there.
  - The program stops under control either way, so no wrong answer escapes.
  - But the sentence promises a compile-time refusal for "a constant division
    by zero" without that scope, and `+ - *` overflow in the same local
    position IS refused at compile time (M10 item `o21`, `TYPE-076`).

## Deduplication

- Not in `KNOWN_DEFECTS.md`.
- The two documentation defects it lists, DEF-100 (BUILD_REFERENCE's `npkg`
  features) and DEF-101 (§9.3's enum-cast sentence, fixed 2026-09-25), are
  other sentences. At the baseline M10 measured DEF-101 itself: its old
  sentence called `intN =>! enum` impossible, and the baseline compiler
  accepts it (item `c18`), so it is deduplicated there.
- M9's observations for M10/M11 are other sentences too: the `?` spelling in
  §11.2 and a string literal in `cstring` position.

## Measured, and inferred

- *Measured:* every verdict above, and the IR predicates quoted for d3 and d4
  (`fcmp une`; branches, no `select`), read from HUNT2's emitted `.ll` of the
  M10 programs `m07_nan_comparisons` and `x05_ternary_evaluates_one_branch`.
- *Judged, not measured:* which sentence is the stale one in d3–d5. The
  compiler's behaviour and the later decision (§1.4's own statement for d3,
  VERIFICATION §1.2 for d4, D-210 for d5) agree, so the other sentence is
  called the documentation defect.
