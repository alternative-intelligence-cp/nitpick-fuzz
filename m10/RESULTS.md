# M10 results: the checklist at both compilers

Written by `gen/m10_report.py` from `results/<commit>/m10.jsonl` (run 2; run 1 is
`m10-run1.jsonl`, and the two differ only in the two re-spelled programs listed
below). The checklist, its citations and its expectations are in `CHECKLIST.md`.

## The denominators (PLAN.md 10.4)

| | HUNT2 `9126350` | baseline `c3bdae2` |
|---|---|---|
| items | 229 | 229 |
| testable (a program each) | 223 | 223 |
| agreeing with the reference | 212 | 210 |
| disagreeing | 11 | 13 |
| untestable, with a reason | 6 | 6 |
| … of which `accepted` | 1 | 2 |
| … of which `other_code` | 1 | 1 |
| … of which `refused` | 5 | 6 |
| … of which `wrong_exit` | 4 | 4 |

## By area

| area | items | HUNT2 agree / disagree | baseline agree / disagree |
|---|---|---|---|
| defaults and zero values | 16 | 16 / 0 | 16 / 0 |
| numeric conversions and literals | 28 | 28 / 0 | 27 / 1 |
| integer overflow | 22 | 22 / 0 | 22 / 0 |
| division | 18 | 17 / 1 | 17 / 1 |
| shifts | 9 | 9 / 0 | 9 / 0 |
| comparisons | 13 | 12 / 1 | 12 / 1 |
| string lengths and bounds | 17 | 14 / 3 | 13 / 4 |
| pick | 13 | 12 / 1 | 12 / 1 |
| `when` and `defer` ordering | 12 | 12 / 0 | 12 / 0 |
| `Result`, `?\|`, `?!`, `relay` | 10 | 10 / 0 | 10 / 0 |
| loop ranges | 28 | 24 / 4 | 24 / 4 |
| shadowing and scope | 4 | 3 / 1 | 3 / 1 |
| precedence and evaluation | 7 | 7 / 0 | 7 / 0 |
| arrays, slices and value semantics | 9 | 9 / 0 | 9 / 0 |
| floats | 3 | 3 / 0 | 3 / 0 |
| `exit` and the leak check | 3 | 3 / 0 | 3 / 0 |
| DEF-108 recall (10.3): falling off the end | 11 | 11 / 0 | 11 / 0 |

## Every disagreement, and what it is

Each cell: npkc rc (codes) / -O0 / -O2, and the kind of disagreement; `=` where the
item agrees there.

| item | expected | HUNT2 | baseline | what it is |
|---|---|---|---|---|
| `c18_int_to_tag_only_enum` | run:0 (base: refuse) | = | 0 / 0 / 0: `accepted` | known **DEF-101** at the baseline (its reference's sentence, since corrected) |
| `v12_constant_div_by_zero` | refuse:NITPICK-TYPE-004 | 0 / 97 / 97: `accepted` | 0 / 97 / 97: `accepted` | **F-017 d7** (documentation): accepted in a local initialiser, traps at run time |
| `m06_spaceship` | run:0 | 1 (EMIT-002) / - / -: `refused` | 1 (EMIT-002) / - / -: `refused` | **F-015**: `<=>` refused by the emitter (`EMIT-002`) |
| `t02_length_spelled_length` | run:0 | 1 (TYPE-019) / - / -: `refused` | 1 (TYPE-019) / - / -: `refused` | **F-017 d1** (documentation): the member is `.len` |
| `t04_block_string_quotes` | run:0 | = | 1 (LEX-005, PARSE-001, PARSE-003) / - / -: `refused` | known **DEF-98** at the baseline (fixed at `395308f`) |
| `t08_string_index` | run:0 | 1 (TYPE-007) / - / -: `refused` | 1 (TYPE-007) / - / -: `refused` | **F-017 d2** (documentation): a string cannot be indexed |
| `t09_string_index_past_end` | run:94 | 1 (TYPE-007) / - / -: `refused` | 1 (TYPE-007) / - / -: `refused` | **F-017 d2** (documentation), as `t08` |
| `p05_negative_patterns` | run:0 | 1 (EMIT-002) / - / -: `refused` | 1 (EMIT-002) / - / -: `refused` | **F-016**: a negative range pattern refused by the emitter (`EMIT-002`); its `(-1i32)` arm compiles |
| `l06_for_inclusive_to_int8_max` | run:0 | 0 / 10 / 10: `wrong_exit` | 0 / 10 / 10: `wrong_exit` | **F-012**: a signed inclusive range ending at its type's maximum runs zero times |
| `l08_for_inclusive_to_int64_max` | run:0 | 0 / 10 / 10: `wrong_exit` | 0 / 10 / 10: `wrong_exit` | **F-012**: as `l06`, at int64 |
| `l11_till_nonpositive_limit` | run:0 | 0 / 10 / 10: `wrong_exit` | 0 / 10 / 10: `wrong_exit` | **F-014**: `till` with a negative limit counts down |
| `l28_for_binding_type_mismatch` | refuse:NITPICK-TYPE-033 | 1 (TYPE-007) / - / -: `other_code` | 1 (TYPE-007) / - / -: `other_code` | **F-017 d6** (documentation): refused, as `TYPE-007` not `TYPE-033` |
| `h02_for_binding_shadow` | run:0 | 0 / 10 / 10: `wrong_exit` | 0 / 10 / 10: `wrong_exit` | **F-011**: the `for` binding outlives its loop in the emitter (a silent wrong value; an out-of-bounds read with another type) |

## Agreeing items that settle a contradiction between two sentences

| item | result at both | what it settles |
|---|---|---|
| `m07_nan_comparisons` | 0 / 0 / 0 (expected run:0) | **F-017 d3**: `!=` is `une` (§1.4), not §28's `fcmp one` |
| `x05_ternary_evaluates_one_branch` | 0 / 0 / 0 (expected run:0) | **F-017 d4**: the ternary branches (VERIFICATION §1.2), not §28's `select` |
| `o16_int128_add` | 0 / 93 / 93 (expected run:93) | **F-017 d5**: `int128` traps (§1.2, D-210), not §4's 'D-037 wrapping' |

## Programs re-spelled after run 1 (S36; the expectation unchanged)

| item | why | run 2 at both |
|---|---|---|
| `m12_tbb_compare_on_err_traps` | run 1 spelled `>`, refused `TYPE-008` (tbb has no ordering, D-093) | 0 / 110 / 110, agrees |
| `d16_uninit_owning_field_overwrite` | run 1 wrote the fields directly, refused `ASSIGN-001` (D-010); now D-225's `$$m` idiom | 0 / 0 / 0, agrees |

## The untestable items

| item | reason |
|---|---|
| `u01_fd_vacant_to_int64` | D-042 says -1 is not representable as an `fd`, while D-225 stores -1 in a vacant `OwnedFd`; no sentence says what the conversion of that value gives (M9 measured 4 294 967 295, the i32 -1 zero-extended). |
| `u02_fallback_laziness` | No sentence states whether `?\|`'s fallback is evaluated when the call succeeds (`??`'s laziness is stated; `?\|`'s is not). |
| `u03_same_scope_redeclaration` | No reference sentence states the rule for two declarations of one name in one scope (the compiler's own notes call it RESOLVE-001). |
| `u04_float_to_string` | No reference sentence states a float's decimal rendering (shortest round-trip is D-193's implementation, not a stated format). |
| `u05_int_to_enum_out_of_range` | The text calls `intN =>! enum` an assertion and does not say what a value that is no tag becomes. |
| `u06_power_operator` | `**` is a 'Standard Library expansion', not in the compiler; nothing states its overflow rule. |
