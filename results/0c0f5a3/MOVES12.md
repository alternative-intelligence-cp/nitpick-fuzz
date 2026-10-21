# MOVES12 — HUNT3 `0c0f5a3` against HUNT2 `9126350`, every run

M12's move table (the brief's section 6). One row per group of moves that share a shape and a
cause, across the six runs: recall, findings, M2, M9, M10 and M11. HUNT3 is the compiler's `main`
after landing 113 (`0c0f5a39fcd2a54e78bf7409add841cbc16927b7`), run under LLVM 20.1.8; `9126350`'s
records were measured under 20.1.2, and the LLVM control (row 0) shows the toolchain moves nothing.

**Evidence** is (i) the text at HUNT3 that names the program or its shape, cited as **OD:n** (line n
of `git show 0c0f5a3:meta/roadmap/OPEN_DECISIONS.md`) or **NT:n** (line n of `meta/NOTICES.md`), the
new verdict being what that text says; or (ii) a **bisection** build. A verdict is `npkc rc codes /
O0 / O2` (`-` for a leg not built, `live` the leak observer's bytes) or AGREE / DISAGREE:kind.
Landing numbers for the older fixes follow the registration audit's table (74 … 80) and the NOTICES
rows: 71 `1b4f0c6`, 74 `40deffa`, 75 `6dc8d13`, 76 `6f6f12c`, 77 `058505d`, 78 `d3a1759`, 79
`44ec7e9`, 80 `9b7204c`, 83 `9efe218`, 88 `88aa21d`, 90 `eaf6b08`, 91 `c15422e`, 94 `05a7b02`, 96
`afa8499`, 97 `28194e0`, 98 `9fede45`, 101 `8af8ddd`, 102 `98cfe35`, 103 `7e91730`, 106 `42ecf29`,
111 `e50eaf4`, 112 `958890a`, 113 `0c0f5a3`.

## Summary

| run | moved | explained | unexplained |
|---|---|---|---|
| recall (25 rows) | 0 | — | 0 |
| findings (156 programs in 48 findings) | 67 programs in 29 findings, plus F-025's `run.sh` and F-045's message | all | 0 |
| M2 grid (956 cells) | 0 | — | 0 |
| M9 grid (7 571 cells) | 393 | 393 (24 of them leave the candidate F-049) | 0 |
| M10 (223 programs) | 9 | 9 | 0 |
| M11 (2 872 claims) | 95 | 95 | 0 |

**Zero UNEXPLAINED.** One move leaves a new finding: the 24 cells of row 44, F-049, bisected to
landing 74.

## The table

| # | run | ids (count) | shape | `9126350` verdict | HUNT3 verdict | class move | explained by | evidence | prediction |
|---|---|---|---|---|---|---|---|---|---|
| 0 | control | every record at `9126350` under 20.1.8 | the LLVM move alone | the committed records (20.1.2) | identical: recall 25/25, M2 956/0, M9 7 571/0 with heap words, M10 223/0, M11 2 872/0 | none | the toolchain: **0 cells moved by the toolchain** | PROGRESS.md, M12 section 3 | — |
| 1 | recall | none (0 of 25) | `known/` | as `known-m10.txt` | identical (`known-m12.txt`) | none | — | `diff` prints nothing | P10 |
| 2 | M2 | none (0 of 956) | the M2 grid | as recorded | identical (`MOVES.md`: 956 cells, 0 moved) | none | — | `compare.py` | P9 |
| 3 | findings | F-003: `pick_read_after_move`, `pick_move_twice_drop`, `minimized/m5771…`, `minimized/m7092…` (4) | a consuming pick's binding escapes the move rules | 0 / 70 / 70, 0 / 95 / 95 | 1 `MOVE-001` | uaf, double free → refused | 74, DEF-118 | OD:2523; NT:96 | P12 |
| 4 | findings | F-004: `view_addr_to_freeing_callee`, `view_claim_i_to_freeing_callee` (2) | a view's root freed through a callee | 0 / 70 / 70 | 1 `BORROW-015`; 1 `BORROW-013` | uaf → refused | 74: DEF-119 (`view_addr_…`'s `BORROW-015`) and DEF-123 (`view_claim_i_…`'s `BORROW-013`, a `$$i` claim's code; worded so in M13, M12v's finding (2)) | OD:2532, OD:2586 | P12 |
| 5 | findings | F-005: `ptr_store_leak`, `ptr_store_churn1000`, `ptr_store_churn4000`, `ptr_store_fd_left_open`, `minimized/m0009…` (5) | `(<-p) = v` never drops the old value | live 46, 46·N + 43; a descriptor open (26) | live 0; 0 / 0 / 0 | leak → clean | 76, DEF-120 | OD:2540; NT:100 | P13 |
| 6 | findings | F-006: `pick_arm_read_leak`, `minimized/m3613…` (2) | a consuming pick's binding never dropped | live 46 | live 0 | leak → clean | 76, DEF-121 | OD:2559 | P13 |
| 7 | findings | F-007: `cstr_churn1000`, `cstr_churn4000` (2) | `to_cstring`'s buffer never freed | peak 10·N | peak 10 | leak → clean | 78, DEF-122 (D-328) | OD:2575; NT:106 | P13 |
| 8 | findings | F-008: `claim_i_holder_write`, `claim_i_argument_write` (2) | a write through a `$$i` claim's holder | 0 / 22 / 22 | 1 `BORROW-013` | wrong value → refused | 74, DEF-123 | OD:2586 | P12 |
| 9 | findings | F-009: `move_param_reinit_read` (1) | a re-initialised `move` parameter | 1 `MOVE-001` | 0 / 22 / 22 | refused → clean | 79, DEF-124 | OD:2592; NT:108 | P14 |
| 10 | findings | F-010: `lent_dyn_swap` (1) | a swap through a lent `dyn` | 1 `BORROW-002` | 0 / 22 / 22 | refused → clean | 79, DEF-125 | OD:2597 | P14 |
| 11 | findings | F-011: `leak_array_iteration`, `leak_array_read_past_slot`, `leak_same_type`, `leak_string_invalid_ir` (4) | a `for` binding outlives its loop | 0 / 10 / 10, 0 / 11 / 10, 0 / `llc!1` / `opt!1` | 0 / 0 / 0 | wrong value → clean | 74, DEF-127 | OD:2610 | P15 |
| 12 | findings | F-012: `incl_*` (4), `uns_*` (3) (7) | a range `for` at its type's edges | 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 75, DEF-128 | OD:2620; NT:98 | P15 |
| 13 | findings | F-013: `loop_uint32_across_2p31`, `loop_uint8_across_128`, `till_uint8_limit_200` (3) | an unsigned bound sign-extended | 0 / 93 / 93, 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 75, DEF-129 | OD:2629 | P15 |
| 14 | findings | F-014: `till_negative_limit`, `till_negative_literal_limit` (2) | `till` with a negative limit | 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 75, DEF-130 | OD:2635 | P15 |
| 15 | findings | F-015: `spaceship_literals`, `spaceship_uint64`, `spaceship_values` (3) | `<=>` | 1 `EMIT-002` | 0 / 0 / 0 | refused → clean | 79, DEF-131 | OD:2657 | P15 |
| 16 | findings | F-016: `neg_low_bound_pattern`, `neg_range_pattern`, `neg_range_pattern_exclusive` (3) | a negative range pattern | 1 `EMIT-002` | 0 / 4 / 4 | refused → clean | 79, DEF-132 | OD:2663 | P15 |
| 17 | findings | F-017: `d7_local_constant_div_zero` (1) | a certain constant division | 0 / 97 / 97 | 1 `TYPE-004` | trap → refused | 79, DEF-133 (D-331; the record names `d7`) | OD:2668 | P15 |
| 18 | findings | F-018: `h1_lone_identifier`, `h2_comparison_operand` (2) | a macro's free name | 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 77, DEF-144 | OD:2759; NT:104 | P16 |
| 19 | findings | F-019: `u1_char8_takes_high_codepoint`, `u2_char32_refuses_escape` (2) | a `\u{…}` escape's width | 0 / 10 / 10; 1 `TYPE-007` | 1 `TYPE-007`; 0 / 0 / 0 | wrong value → refused; refused → clean | 77, DEF-145 (the escape is `char32`) | OD:2772 | P16 |
| 20 | findings | F-020: `j1_first_error_lost` (1) | the join's relayed error | 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 77, DEF-146 | OD:2782 | P16 |
| 21 | findings | F-020: control `ctl_j3_spawn_order_swapped` (1) | the earliest-spawned child's error | 0 / 0 / 0 | 0 / 10 / 10 | a control moves | 77, D-334 (a ratified rule moving a control) | OD:2782 (the file is the fuzzer's to re-spell) | P23 |
| 22 | findings | F-021: `t1_timedwait_expiry` (1) | an expired `timedwait` | 0 / 10 / 10 | 0 / 0 / 0 | wrong value → clean | 77, DEF-147 | OD:2794 | P16 |
| 23 | findings | F-022: `a1_destroy_while_thread_holds` (1) | a shared arena destroyed while held | 0 / 96 / 96 | 1 `BORROW-016` | lifetime → refused | 77, DEF-148 | OD:2804 | P16 |
| 24 | findings | F-023: `i1_unawaited_method_call` (1) | an un-awaited async method | 0 / `llc!1` / `opt!1` | 1 `TYPE-043` | invalid IR → refused | 80, DEF-149 | OD:2822; NT:109 | P17 |
| 25 | findings | F-024: `c1_macro_method_into_impl`, `c2_nested_expression_500`, `c3_macro_emits_comptime_function` (3) | npkc trapped (exit 3) | 3 / - / - | 1 `PARSE-001` (c1, "expected a type" at its `$$i` receiver); 1 `PARSE-012` (c2); 0 / 0 / 0 (c3) | crash → refused, clean | 80, DEF-150 (c1: "a body with a parse error expands to nothing now (the errors are the report)") | OD:2826 | P17 |
| 26 | findings | F-025: `run.sh` (the canary under `--extra-picky=no-wildx`) | the flag refused every program | no-wildx: 1, 256 × `WILDX-003` | no-wildx: 0, 0 × `WILDX-003` (twice) | refused → accepted | 80, DEF-151 | OD:2831 | P17 |
| 27 | findings | F-026: `d1_tfp64_unit_mismatch_compiles` (1) | a unit annotation ignored | 0 / 10 / 10 | 1 `TYPE-016` | wrong value → refused | 80, DEF-152 | OD:2835 | P17 |
| 28 | findings | F-029: `k1_wild_buffer_declared` (1) | the keyword `buffer` as a binding's name | 0 / 3 / 3 | 1 `PARSE-001` | accepted → refused | 113, DEF-235 | NT:174 names `k1`/`k2`; OD:3937 | P22 |
| 29 | findings | F-029: `k2_wild_buffer_declared_then_used` (1) | the same, then used | 1 `PARSE-002` | 1 `PARSE-001`, `PARSE-002` | a code added to a refusal | 113, DEF-235 ("refused by both compilers already") | NT:174 | P22 (dispatch note (g)) |
| 30 | findings | F-037: `u1_dyn_cast_moved_pod`, `u2_dyn_cast_pod_no_move`, `u3_dyn_cast_owning_struct` (3) | a `=> dyn` cast | 0 / 10 / 10 | 0 / 0 / 0 (answers 7) | uaf → clean | 94, DEF-227 | OD:3790; NT:136 | P18 |
| 31 | findings | F-038: `c1_give_outside_pick`, `c2_fall_outside_pick` (2) | `give`/`fall` outside a pick | 3 / - / - | 1 `TYPE-094` | crash → refused | 111, DEF-233 | OD:3903; NT:170 | P20 |
| 32 | findings | F-041: `h1_unbounded_instantiation` (1) | unbounded generic instantiation | T (timeout) | 1 `TYPE-018`, in 0.09 s | hang → refused | 96, DEF-229 | OD:3823; NT:140 | P18 |
| 33 | findings | F-045: `d1_coalesce_on_result` (its message; the verdict line unmoved) | `??` on a `Result` | 1 `TYPE-007`, advice names `?` | 1 `TYPE-007`, advice names `?!`/`?|` (D-175) | a message | 113, DEF-237 | OD:3980; NT:174 | P22 |
| 34 | findings | F-047: `s1_fixed_view_written`, `s2_fixed_param_written` (2) | a write through a `fixed uint8[]` view | 0 / 10 / 10 | 1 `TYPE-086` | wrong value → refused | 98 and 103, DEF-230 | OD:3849; NT:144, 154 | P19 |
| 35 | findings | F-048: `n1_nil_field`, `n2_nil_field_built` (2) | a `NIL` field | 0 / `llc!1` / `opt!1` | 0 / 0 / 0 | invalid IR → clean | 112, DEF-232 | NT:172 names `n1`, `n2`; OD:3887 | P21 |
| 36 | M9 | F-003's 44 REFUSE cells, `pick_own` × the moves (44) | a consuming pick's binding escapes the move rules | uaf 6, double free 16, segv 2, wrong value 8, clean 12 | 1 `MOVE-001` | → refused | 74, DEF-118 | OD:2523; NT:96 | P4 |
| 37 | M9 | F-008's 40 REFUSE cells, `claim_i` × the writes (40) | a write through a `$$i` holder | wrong value 16, clean 20, leak 4 (`claim_i × at_overwrite`, also in F-005's family) | 1 `BORROW-013` | → refused | 74, DEF-123 | OD:2586 | P5; P1's 4 |
| 38 | M9 | F-005's family, `at_overwrite`/`assign` through a pointer at `local`, `move_param`, `ptr_param`, `elem`, `field`, `for_range`, `claim_m` … (106) | `(<-p) = v` never drops the old value | leak, live 8 to 140 | 0 / 0, live 0 | leak → clean | 76, DEF-120 | OD:2540; NT:100 | P1 |
| 39 | M9 | F-005's `ofd` cells (7) | the same, an `OwnedFd` left open | leak (a descriptor open, 26; no live reading) | 0 / 0; the heap's words all moved | leak → clean | 76, DEF-120, and 78, DEF-122 (the path buffers) | OD:2540, 2575 | P1 |
| 40 | M9 | F-006's family, `pick_own` × the reads and drops (24) | a consuming pick's binding never dropped | leak, live 8 to 774 | live 0 | leak → clean | 76, DEF-121 | OD:2559 | P2 |
| 41 | M9 | `pick_own × at_overwrite` (4) | both at once | leak | live 0 | leak → clean | 76, DEF-120 and DEF-121 | OD:2540, 2559 | P3 |
| 42 | M9 | F-009's SAFE cells, `move_param × loop_move` (47) and `× swap` (25) (72) | a re-initialised `move` parameter | 1 `MOVE-001` | 0 / 0 | refused → clean | 79, DEF-124 | OD:2592 | P6 |
| 43 | M9 | F-010's SAFE cells, `dyn_recv × swap` (12) | a swap through a lent `dyn` | 1 `BORROW-002` | 0 / 0 | refused → clean | 79, DEF-125 | OD:2597 | P7 |
| 44 | M9 | `pick_own × loop_move` (16: 4 were F-006's leak cells, 12 clean) and `pick_own × swap`'s read-after and reuse-sentinel cells (8) (24) | a consuming pick's binding re-initialised after a move | 0 / 0 (20 clean) or leak, live 8 to 67 (4) | 1 `MOVE-001` | SAFE → refused | 74, DEF-118's fix, leaving **F-049** | **bisection**: all 24 run at 73 `bbb1530`, refused at 74 `40deffa`; their 98 `local` twins run at both | P2's 4 (instead of clean) |
| 45 | M9 | `ofd` SAFE cells with no live prediction, at `local`, `move_param`, `elem`, `field`, `for_range` … (60) | `to_cstring` in the cell | 0 / 0, live 10, 20, 30, 40, 60 | 0 / 0, live 0 | clean → clean (`peak` moved) | 78, DEF-122 (D-328): `to_cstring`'s buffer freed | OD:2575; NT:106 | — (not predicted) |
| 46 | M10 | `h02_for_binding_shadow` (1) | a `for` binding outlives its loop | DISAGREE:wrong_exit 0 / 10 / 10 | AGREE 0 / 0 / 0 | → agree | 74, DEF-127 | OD:2610 | P25 |
| 47 | M10 | `l06_for_inclusive_to_int8_max`, `l08_for_inclusive_to_int64_max` (2) | a range `for` at its type's edges | DISAGREE:wrong_exit | AGREE | → agree | 75, DEF-128 | OD:2620 | P25 |
| 48 | M10 | `l11_till_nonpositive_limit` (1) | `till` with a non-positive limit | DISAGREE:wrong_exit | AGREE | → agree | 75, DEF-130 | OD:2635 | P25 |
| 49 | M10 | `m06_spaceship` (1) | `<=>` | DISAGREE:refused `EMIT-002` | AGREE 0 / 0 / 0 | → agree | 79, DEF-131 | OD:2657 | P25 |
| 50 | M10 | `p05_negative_patterns` (1) | a negative range pattern | DISAGREE:refused `EMIT-002` | AGREE | → agree | 79, DEF-132 | OD:2663 | P25 |
| 51 | M10 | `v12_constant_div_by_zero` (1) | a certain constant division | DISAGREE:accepted 0 / 97 / 97 | AGREE 1 `TYPE-004` | → agree | 79, DEF-133 (D-331) | OD:2668 | P26 |
| 52 | M10 | `c25_flt32_literal_16_digits` (1) | a 16-digit `flt32` literal | AGREE 1 `TYPE-030` | DISAGREE:accepted 0 / 10 / 10 | → disagree | 91, D-346 (DEF-205): the 15-digit rule lifted | NT:129 (F33) names it | — (the reference changed) |
| 53 | M10 | `c23_c_hex_prefix_refused` (1) | a lexer error's second report | AGREE 1 `LEX-003`, `PARSE-002` | AGREE 1 `LEX-003` | a code removed | 101, DEF-164 (D-240: one mistake, one report) | NT:150 names it | — |
| 54 | M11 | `mc0188`, `mc0202` (2) | F-018 | DISAGREE:wrong_exit 11 / 11 | AGREE | → agree | 77, DEF-144 | OD:2759 | P16 |
| 55 | M11 | `ty0272` (`TYPE-007` → 0 / 0), `ty0280` (10 / 10 → `TYPE-007`) (2) | F-019 | DISAGREE | AGREE | → agree | 77, DEF-145 | OD:2772 | P16 |
| 56 | M11 | `cc0080` (1) | F-020 | DISAGREE:wrong_exit | AGREE | → agree | 77, DEF-146 | OD:2782 | P16 |
| 57 | M11 | `cc0568b` (1) | F-021 | DISAGREE:wrong_exit | AGREE | → agree | 77, DEF-147 | OD:2794 | P16 |
| 58 | M11 | `cc0321`, `me0461` (2) | F-022 | DISAGREE:accepted 96 / 96 | AGREE 1 `BORROW-016` | → agree | 77, DEF-148 | OD:2804 | P30 |
| 59 | M11 | `io0045` (1) | F-023 | DISAGREE:accepted `llc!1` | AGREE 1 `TYPE-043` | → agree | 80, DEF-149 | OD:2822 | P17 |
| 60 | M11 | `mc0250`, `mc0256`, `mc0327` (3) | F-024 | DISAGREE:crash, `sh` 2 or 3 | AGREE (`PARSE-012`; `sh` 0; 0 / 0) | → agree | 80, DEF-150 | OD:2826 | P17 |
| 61 | M11 | `vf0808`, `vf0811` (2) | F-025 | DISAGREE:wrong_exit `sh` 1 | AGREE `sh` 0 | → agree | 80, DEF-151 | OD:2831 | P17 |
| 62 | M11 | `ty0553`, `ty1598` (2) | F-026 | DISAGREE:accepted | AGREE 1 `TYPE-016` | → agree | 80, DEF-152 | OD:2835 | P30 |
| 63 | M11 | `as0492`, `md0296b`, `ty0285`, `ty0290`, `ty0414` (5) | F-027 c: a string literal in `cstring` position | DISAGREE:refused `TYPE-007` | AGREE 0 / 0 | → agree | 78, DEF-153 (its three rows of 1.6.1d step 3b) | OD:2839 | P30 (`md0296b`) |
| 64 | M11 | `bi0256`, `cc0380`, `vf0831`, `mc0246`, `mc0251`, `mc0344`, `mc0278`, `mc0046b`, `ty0176`, `ty0178`, `ty0189b` (11) | F-027 a, b, c, d | DISAGREE | AGREE (each as the record says) | → agree | 83, DEF-153 (1.6.1e step 3) | OD:2839-2842 names each | — |
| 65 | M11 | `mc0309b` (1) | F-027 c: compile-time string ordering | DISAGREE:refused `TYPE-004` | AGREE 0 / 0 | → agree | 90, D-338 (1.6.1e step 3b) | OD:2844 | — |
| 66 | M11 | `md0183` (1) | F-034 c: a constant cycle's diagnostic | DISAGREE:wrong_exit `sh` 1 | AGREE `sh` 0 | → agree | 113, DEF-234 (c) | OD:3922; NT:174 | — |
| 67 | M11 | `lx0054`, `lx0114`, `lx0121` (3) | F-036 a: a keyword as a function's name | DISAGREE:wrong_exit `sh` 1 | AGREE `sh` 0 | → agree | 113, DEF-235 | OD:3937 | P22 |
| 68 | M11 | `as0453` (1) | F-037 | DISAGREE:wrong_exit 10 / 10 | AGREE 0 / 0 (answers 7) | → agree | 94, DEF-227 | OD:3790 | P30 |
| 69 | M11 | `as0202`, `as0203` (crash → `TYPE-094`), `as0267` (`sh` 1 → 0) (3) | F-038 | DISAGREE | AGREE | → agree | 111, DEF-233 | OD:3903; NT:170 | P28 |
| 70 | M11 | `as0555` (`TYPE-045`), `as0583` (`DERIVE-007`), `as0043`, `tr0368` (`RESOLVE-014`) (4) | F-039 c, d, e; F-042 a | DISAGREE:accepted | AGREE | → agree | 113, DEF-236 (c)(d)(e) | NT:174 names all four | P22 |
| 71 | M11 | `tr0586` (1) | F-041 | DISAGREE:crash (T) | AGREE 1 `TYPE-018` | → agree | 96, DEF-229 | OD:3823 | P18 |
| 72 | M11 | `ty1657` (1) | F-044's frac row | DISAGREE:wrong_exit 11 / 11 | AGREE 0 / 0 | → agree | 97, DEF-231 (D-347) | OD:3867 | P29 |
| 73 | M11 | `ty1649` (1) | F-046 a: a frac member written | DISAGREE:emit_defect | AGREE 1 `TYPE-024` | → agree | 111, DEF-238 | OD:3987; NT:170 | P28 |
| 74 | M11 | `ty1873` (1) | F-046 b: a `fixed` parameter reassigned | DISAGREE:accepted | AGREE 1 `ASSIGN-002` | → agree | 102, DEF-248 | OD:4133 | P29 |
| 75 | M11 | `ty1719b` (1) | F-047 | DISAGREE:accepted | AGREE 1 `TYPE-086` | → agree | 98 and 103, DEF-230 | OD:3849 | P30 |
| 76 | M11 | `ty1944` (1) | F-048's source claim | DISAGREE:build_fail `llc!1`/`opt!1` | AGREE 0 / 0 | → agree | 112, DEF-232 | NT:172 names it | P21 (dispatch note (f)) |
| 77 | M11 | `as0295b`, `lx0178`, `op0068`, `op0213`, `ty0507`, `ty0616b`, `ty2038` (7) | known DEF-131 (F-015) | DISAGREE:emit_defect | AGREE 0 / 0 | → agree | 79, DEF-131 | OD:2657 | P29 (`ty0507`), P30 |
| 78 | M11 | `ct0235`, `ct0258` (2) | known DEF-130 (F-014) | DISAGREE:wrong_exit | AGREE | → agree | 75, DEF-130 | OD:2635 | P30 |
| 79 | M11 | `ct0236` (1) | known DEF-135, a `tbb` bound holding ERR | DISAGREE:wrong_exit 10 / 10 | AGREE 110 / 110 | → agree | 75, DEF-135 | OD:2641 | P30 |
| 80 | M11 | `vf0215b` (1) | known DEF-123 (F-008) | DISAGREE:accepted | AGREE 1 `BORROW-013` | → agree | 74, DEF-123 | OD:2586 | — |
| 81 | M11 | `bi0105`, `bi0241`, `me0217`, `me0221` (`run:0` → refused); `me0208`, `me0228` (their codes → other_code) (6) | a `string_bytes` view bound into a plain `uint8[]` (left for Option C) | AGREE | DISAGREE 1 `TYPE-007` | → disagree | 103, D-351 (DEF-246) | OD:4107 | P31 |
| 82 | M11 | `mc0388` (1) | a macro parameter naming what the body emits | AGREE 0 / 0 | DISAGREE:refused `MACRO-011` | → disagree | 106, D-343 | NT:160 | P27 |
| 83 | M11 | `me0119`, `me0119b` (2) | a binding named `buffer`, before the claim is reached | AGREE 96 / 96 | DISAGREE:refused `PARSE-001` | → disagree | 113, DEF-235 | NT:174 names both | dispatch note (g); not re-spelled (REPORT §13.12) |
| 84 | M11 | `as0572` (1) | `#[align(16i32)]` | AGREE 0 / 0 | DISAGREE:refused `DERIVE-007` | → disagree | 113, DEF-236 (d) (D-020: no `#[align]`) | NT:174 names it | dispatch note (g) |
| 85 | M11 | `md0042` (1) | a support file whose header is `mod:mod;` | AGREE `sh` 0 | DISAGREE:wrong_exit `sh` 1 (`PARSE-001`: `mod` a keyword declared as a name) | → disagree | 113, DEF-235 | OD:3937 (every declared name of every kind) | — |
| 86 | M11 | `bd0075`, `bd0299`, `bd0462`, `bd0463b`, `bd0464`, `bd0464b` (6) | a `[toolchain]` with no `triple` | AGREE `sh` 0 | DISAGREE:wrong_exit `sh` 1 ("nitpick.toml has no [toolchain] triple pin") | → disagree | 71, E-8 and D-322 (5): `[toolchain]` gains two required rows | NT:90 (F15), NT:91 | P32 (instead) |
| 87 | M11 | `ty0190` (its program is M10's `c25`) (1) | a 16-digit `flt32` literal | AGREE 1 `TYPE-030` | DISAGREE:accepted 0 / 10 / 10 | → disagree | 91, D-346 | NT:129 names the program | — |
| 88 | M11 | `ty0322` (1) | `cstring` is 16 bytes | AGREE 0 / 0 | DISAGREE:wrong_exit 10 / 10 | → disagree | 78, D-328: `cstring` is `{ ptr, len, cap }`, 24 bytes | NT:106; HUNT3's TYPE_REFERENCE:424 | — |
| 89 | M11 | `ty1635` (1) | a frac's invariants | AGREE 0 / 0 | DISAGREE:wrong_exit 10 / 10 | → disagree | 97, DEF-231 (D-347) | NT:142 names it | — |
| 90 | M11 | `ty1669` (1) | `complex(3.0flt64, …)`: `flt64` as a literal suffix | AGREE 0 / 0 | DISAGREE:refused `LEX-009` | → disagree | 83, DEF-153 (a type name as a suffix is `LEX-009`) | OD:2841 (`ty0189b`'s shape) | — |
| 91 | M11 | `mc0136` (1) | the reference's own `emit_methods` example | DISAGREE:crash (3) | DISAGREE:refused `PARSE-001` | crash → refused | 80, DEF-150 (the example's `$$i Box:self`, corrected in the reference) | OD:2826 | — |
| 92 | M11 | `me0183` (1) | F-030's `buffer` row | DISAGREE 1 `PARSE-002` | DISAGREE 1 `PARSE-001`, `PARSE-002` | a code added | 113, DEF-235 | NT:174 names it | dispatch note (g) |
| 93 | M11 | `vf0983`, `vf1149` (2) | a `flt32` literal rounded twice | DISAGREE:refused `TYPE-030` | DISAGREE:wrong_exit 10 / 10 (rounded once, to the nearest float) | refused → wrong exit | 88, DEF-203, and 91, D-346 | OD:3405; NT:129 names both | — |
| 94 | M11 | `bi0010`, `bi0017` (2) | a view passed to a plain parameter or returned | AGREE 1 `BORROW-001` | AGREE 1 `TYPE-007` | a code changed | 103, D-351 (DEF-246): **agrees for the wrong reason** (S55's screen; Option C's) | OD:4107 | the brief's section 4 |
| 95 | M11 | `lx0321`, `lx0343`, `lx0346`, `lx0349`, `ty1646b` (5) | a lexer error's second report | AGREE `LEX-…`, `PARSE-002` | AGREE `LEX-…` | a code removed | 101, DEF-164 | NT:150 names all five | — |
| 96 | M11 | `ty0414b` (1) | an interior NUL in `cstring` position | AGREE 1 `TYPE-007` | AGREE 1 `TYPE-092` | a code changed | 78, D-328 ("TYPE-092 for an interior NUL") | NT:106 | — |

Totals: findings rows 3–35 hold 67 programs (and F-025's script and F-045's message); M9 rows 36–45
hold 44 + 40 + 106 + 7 + 24 + 4 + 72 + 12 + 24 + 60 = 393 cells; M10 rows 46–53 hold 9 programs; M11
rows 54–96 hold 62 + 21 + 4 + 8 = 95 claims.

## The predicted moves

**M9 grid**
- [ ] **P1** — F-005's 117 leak cells: **113 went to clean** (rows 38, 39); the other **4**, `claim_i ×
  at_overwrite`, went to refused `BORROW-013` (row 37): they are REFUSE cells, and DEF-123's fix (74)
  refuses them before DEF-120's could make them clean. Explained.
- [ ] **P2** — F-006's 28 leak cells: **24 went to clean** (row 40); the other **4**, `pick_own ×
  loop_move`, went to refused `MOVE-001`: F-049 (row 44), bisected to 74. Investigated as a candidate.
- [x] **P3** — the 4 `pick_own × at_overwrite` leak cells went to clean (row 41).
- [x] **P4** — F-003's 32 anomalies and the rest of its 44 accepted REFUSE cells: **44** to refused
  `MOVE-001` (row 36).
- [x] **P5** — F-008's 16 wrong-value cells and the rest of its 40: **40** to refused `BORROW-013`
  (row 37).
- [x] **P6** — F-009's **72** `MOVE-001` SAFE cells went to clean (row 42).
- [x] **P7** — F-010's **12** `BORROW-002` SAFE cells went to clean (row 43).
- [x] **P8** — unchanged: the **262** `MOVE-001` cells (D-065) and the **28** `TYPE-047` receiver cells;
  none moved.

**M2 grid**
- [x] **P9** — no cell moves: 956 cells, 0 moved (row 2).

**Recall and findings**
- [x] **P10** — the recall suite gives "once fixed" in all **25** rows (row 1).
- [x] **P11** — F-001's 13 programs `TYPE-085`, F-002's 4 `TYPE-047`, the controls as in
  `VERDICTS-9126350.txt`, `ctl_gen_move_param` 21/21: **0 of 23 moved**.
- [x] **P12** — F-003 (4) and F-004 (2) refused, F-008 (2) refused `BORROW-013` (rows 3, 4, 8).
- [x] **P13** — F-005 and F-006 show live 0 (rows 5, 6); F-007's peak is 10, no longer 10 × N (row 7).
- [x] **P14** — F-009's `move_param_reinit_read` 22/22; F-010's swap 0/22/22 (rows 9, 10).
- [x] **P15** — F-011 (4), F-012 (7), F-013 (3), F-014 (2) agree; F-015's `<=>` (3) and F-016's
  pattern (3) compile and run; F-017's `d7` is `TYPE-004` as DEF-133's record says (rows 11–17).
- [x] **P16** — F-018 … F-021 agree; F-022 is refused `BORROW-016` (rows 18–23).
- [ ] **P17** — F-023 is `TYPE-043` (row 24), F-025's flag accepts the program (row 26), F-026 is
  `TYPE-016` (row 27), as predicted. **F-024 is `PARSE-001` (c1), `PARSE-012` (c2) and 0/0 (c3), not
  `MACRO-010`/`PARSE-012`**: c1's refusal is the parse error of its `$$i Box:self` receiver, which
  DEF-150's record makes the report (OD:2826); `MACRO-010` is that record's code for a body mixing
  declarations and statements, none of F-024's programs. Explained.
- [x] **P18** — F-037 answers 7, clean (row 30); F-041 is `TYPE-018` in 0.09 s (row 32).
- [x] **P19** — F-047's `s1`/`s2` are `TYPE-086` (row 34); `ctl_s3` stays 0/0 and `ctl_s4` `ASSIGN-002`
  (unmoved).
- [x] **P20** — F-038's `c1`/`c2` are `TYPE-094` and `ctl_c3` stays 0/0 (row 31); F-046 (a), `ty1649`, is
  `TYPE-024` (row 73) and (b), `ty1873`, `ASSIGN-002` (row 74).
- [x] **P21** — HUNT3 carries 112: F-048's `n1`/`n2` compile and run 0/0, `ctl_n3` stays (row 35); and
  M11's `ty1944` with them (row 76).
- [x] **P22** — HUNT3 carries 113: F-029's `k1` is `PARSE-001` and `k2` gains `PARSE-001` beside the
  `PARSE-002` it already had at `9126350` (rows 28, 29); F-036 (a)'s four names are refused (row 67);
  `as0555` `TYPE-045`, `as0583` `DERIVE-007`, `as0043`/`tr0368` `RESOLVE-014` (row 70); F-045's text
  changes (row 33).
- [x] **P23** — F-020's control `ctl_j3` moves from 0/0 to **10/10** under D-334 (row 21).
- [x] **P24** — the findings whose registry rows are still OPEN do not move: F-028 (DEF-154), the
  documentation rows of F-030 … F-033, F-035, F-040, F-043 and F-044 (DEF-239), F-034 (a)(b), F-036
  (b), F-039 (a). One code moved inside a still-open row: `me0183`, F-030's `buffer` row, gains
  `PARSE-001` at 113 (row 92).

**M10**
- [x] **P25** — `h02`, `l06`, `l08`, `l11`, `m06_spaceship` and `p05_negative_patterns` agree (rows 46–50).
- [x] **P26** — `t07` is unchanged at 94 after its re-spelling; `v12` follows DEF-133's record
  (`TYPE-004`, row 51); `t02`, `t08`, `t09` and `l28` do not move (their sentences were corrected in
  the references, DEF-133's d1–d6).

**M11**
- [x] **P27** — `mc0388` goes from AGREE to DISAGREE:refused, `MACRO-011` (row 82); its expectation stays
  `run:0`.
- [x] **P28** — `as0202` and `as0203` agree with `TYPE-094`, `ty1649` with `TYPE-024`, and `as0267.sh`
  agrees, measured (rows 69, 73).
- [x] **P29** — `ty1873` agrees with `ASSIGN-002`, `ty1657` agrees, `ty0507` agrees (rows 74, 72, 77).
- [x] **P30** — the DEF-131 claims, CONTROL's DEF-130 pair and DEF-135 agree; `me0461` is refused
  `BORROW-016`; `md0296b` compiles; `ty1598` and `ty0553` give `TYPE-016`; `as0453` answers 7; F-047's
  `ty1719b` gives `TYPE-086` (rows 77–79, 58, 63, 62, 68, 75).
- [x] **P31** — the six claims binding a plain `uint8[]` are refused `TYPE-007` (row 81).
- [ ] **P32** — **no BUILD claim was refused for its `llvm = "20.1.2"` pin**, at `9126350` under 20.1.8
  (the control) or at HUNT3. Six BUILD claims moved instead for landing 71's rule: npkg refuses a
  `[toolchain]` with no `triple` pin before it reaches the LLVM pin (row 86). Explained.
- [x] **P33** — `as0100` and DEF-245's six other fuzz programs (`tr0425`, `cc0151c`, `md0219`, `tr0448`,
  `vf0580`, `tr0550`) do not move at all.
