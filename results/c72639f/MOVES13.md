# MOVES13 — HUNT4 `c72639f` against HUNT3 `0c0f5a3`: the regression leg, and grid13's faces

M13's move table (the brief's §8). One row per group of moves that share a shape and a cause. It covers
the regression leg's five runs at HUNT4 against HUNT3's committed records (recall, findings, M2, M9, M10),
and grid13's 184 moves between HUNT3 and HUNT4 (`FACES13.txt`), section by section. HUNT4 is the
compiler's `main` at M13's fetch, landing 137 (`c72639f2332208649309b91796d6f173d19a64d2`); both HUNT3 and
HUNT4 run under LLVM 20.1.8 (S77), and the LLVM control (row 0) moves nothing.

**Evidence** is the text at HUNT4 that names the program or its shape: **NT:n** is NOTICES row n of
`git show c72639f:meta/NOTICES.md`; **OD** is the registry row named, in `meta/roadmap/OPEN_DECISIONS.md`
at `c72639f`. A verdict is `npkc rc codes / O0 / O2` (`-` for a leg not built) or a class.

## Summary

| run | moved | explained | unexplained |
|---|---|---|---|
| control: grid13 at HUNT3 under 20.1.2 (933 cells) | 0 | — | 0 |
| recall (25 rows) | 0 | — | 0 |
| findings (160 programs in 34 findings; 15 row findings have no program of their own) | 3 programs in 2 findings | 3 | 0 |
| M2 grid (956 cells) | 0 | — | 0 |
| M9 grid (7 571 cells) | 24 | 24 | 0 |
| M10 (223 programs) | 0 | — | 0 |
| grid13, HUNT3 → HUNT4 (933 cells, `FACES13.txt`) | 184 | 184 | 0 |

**Zero UNEXPLAINED.** No move is a memory fault: every move in the regression leg is a refusal removed by
landing 132 (to the right answer) or a refusal's code changed by landing 136, and every grid13 move is a
fault or a wrong answer at HUNT3 removed by a landing (114, 115, 116, 119, 120).

## The table

| # | run | ids (count) | shape | HUNT3 verdict | HUNT4 verdict | class move | explained by | evidence | prediction |
|---|---|---|---|---|---|---|---|---|---|
| 0 | control | grid13 at HUNT3 under 20.1.2 (933) | the LLVM move alone | the record (20.1.8) | identical | none | the toolchain | `compare13.py`: 0 cells | P11 |
| 1 | recall | none (0 of 25) | `known/` | as `known-m12.txt` | identical (`known-m13.txt`): 19 `match`, DEF-106's and DEF-108's six by hand | none | — | `diff` prints nothing | P10 |
| 2 | findings | F-029 `ctl_k3_int64_buffer_refused` (1; both HUNT runs) | a local named by a keyword, `int64:buffer` | 1 `PARSE-002` at 7:5 ("expected an expression") | 1 `PARSE-001` at 7:11 ("`buffer` is a keyword and cannot name a binding") | refused → refused (code) | 136, DEF-259: "A LOCAL `T:keyword` IS PARSE-001 AT THE NAME" | NT:136 | note (e) 3 |
| 3 | findings | F-049 `pick_reinit_read`, `pick_reinit_loop` (2; both HUNT runs; read by hand against `VERDICTS.txt`, which the brief's loop skips) | a consuming `pick`'s binding re-assigned after a move | 1 `MOVE-001` | 0 / 22 / 22 | refused → the right answer | 132, DEF-256 (F-049): "A CONSUMING `pick`'S BINDING RE-ASSIGNED AFTER A MOVE IS LIVE AGAIN" | NT:132; OD DEF-256 | §8 "F-049 still refused until DEF-256 lands": it has landed; note (e) 1 |
| 4 | findings | every other program (157) | — | as committed | identical, both HUNT runs; every baseline line as committed | none | — | the loop prints only F-029; F-049 by hand: `ctl_local_reinit_read` 22/22 and `ctl_pick_moved_read` `MOVE-001` unchanged | P10 |
| 5 | M2 | none (0 of 956) | — | 562 clean, 394 refused | the same | none | — | `MOVES.md`: 0 moved | P10 |
| 6 | M9 | `pick_own × loop_move` (16: drop-at-exit 4, leak 4, read-after 4, reuse-sentinel 4) and `pick_own × swap`'s read-after and reuse-sentinel cells (8) (24) | MOVES12 row 44: a consuming pick's binding re-initialised after a move | 1 `MOVE-001` | 0/0, the leak cells live 0/0 | refused → clean | 132, DEF-256 | NT:132 | note (e) 2; P10 (none is 115's) |
| 7 | M10 | none (0 of 223) | — | 218 agree, 5 disagree | the same | none | — | `m10-changes.txt`: 0 changed | — |
| 8 | grid13 S | `bare_binding` (1) | DEF-250's seed | 0 107/11 `ACCEPTED:DEFECT:leg_mismatch` | 1 `TYPE-055` | → refused | 114, DEF-250 | NT:114 | P2 |
| 9 | grid13 S | `null_store` (1) | DEF-251's seed | 0 107/99 `ACCEPTED:DEFECT:fallthrough` | 1 `TYPE-096` | → refused | 119, D-355 (ii) | NT:119 | P2 |
| 10 | grid13 S | `probe08h_view_reseated` (1) | DEF-252's seed | 0 170/170 `ACCEPTED:DEFECT:uaf` | 1 `BORROW-002` | → refused | 116, DEF-252 | NT:116 | P2 |
| 11 | grid13 A | the no-initialiser and `pub` bindings of int64, int32, uint8, bool, a struct, `int64[4]` and `stack int64` (68) | DEF-250's class: a module binding emitted read-only | write, compound, field, element and address-writer: 107/13 `ACCEPTED:DEFECT:leg_mismatch` (40); read and address-reader: 13/13 `ACCEPTED:DEFECT:wrong_value` (28) | 1 `TYPE-055` | → refused | 114, DEF-250 | NT:114 | P3 |
| 12 | grid13 A | the no-initialiser and `pub` `wild int64->` and `wildx int64->` bindings (8; scope wild) | the same, a wild pointer binding | write 107/13 `ACCEPTED:DEFECT:leg_mismatch` (4); read 13/13 `ACCEPTED:DEFECT:wrong_value` (4) | 1 `TYPE-055` | → refused | 114, DEF-250 | NT:114 | P3 |
| 13 | grid13 A | the no-initialiser and `pub` `atomic<int64>` bindings: store/load (2), read (2) | the same, an atomic | 107/107 `ACCEPTED:DEFECT:segv` (2); 13/13 `ACCEPTED:DEFECT:wrong_value` (2) | 1 `TYPE-055` | → refused | 114, DEF-250 | NT:114 | P3 |
| 14 | grid13 A | the same atomics' address writer and reader (4) | an atomic method through a pointer | 1 `EMIT-002` | 1 `TYPE-055` | refused → refused (code) | 114, DEF-250 (the declaration is refused before the emitter; F-052's shape stands behind it) | NT:114 | — |
| 15 | grid13 A | the no-initialiser and `pub` channels, send/recv (2) | the same, a channel | 102/102 `ACCEPTED:other` (`ChannelClosed`) | 1 `TYPE-055` | → refused | 114, DEF-250 | NT:114 | P3 |
| 16 | grid13 B | `NULL` in a plain local, a `fixed` local, a module `fixed T->`, a struct field, a parameter's argument and a helper's return, every operation (78) | DEF-251's class | store, used load, field read, dereferencing callee: 107/99 `ACCEPTED:DEFECT:fallthrough` (37); used load 107/12 (5), the unused load before a `NULL` test 107/14 (10) and, for a struct reached through a parameter or a helper's return, 107/0 (2: the -O2 leg folded the test away and reported success, DEF-251's inferred face) `ACCEPTED:DEFECT:leg_mismatch` (17); guarded store and compare 0/0 `ACCEPTED:clean` (24) | 1 `TYPE-096` | → refused | 119, D-355 (ii) | NT:119 | P5 |
| 17 | grid13 B | the `wild` local's store, used load, field read and dereferencing callee (7; scope wild) | DEF-251 (i) | 107/99 `DEFECT:fallthrough` (6); 107/12 `DEFECT:leg_mismatch` (1) | 107/107 clean (TRAP 107) | → clean | 115, DEF-251 (i) | NT:115 | P5, P6 |
| 18 | grid13 B | the `T->?` place's `??!` (2) | the Optional's unwrap-or-trap | 1 `TYPE-007` (`??` then `!`) `REFUSED_TRAP` | 95/95 clean (TRAP 95) | → clean | 120, D-360 | NT:120 | — |
| 19 | grid13 E | dies-first stores by a callee: whole pointee, field, method, two levels; `ra` and `rs` (8) | DEF-252's faces | 70/70 or 25/25 `ACCEPTED:DEFECT:uaf` | 1 `BORROW-002` | → refused | 116, DEF-252 | NT:116 | P9 |

Rows 11–15 make A's 86, rows 16–18 B's 87, row 19 E's 8 and rows 8–10 the seeds' 3: **184**, the
number `FACES13.txt` lists.

## Not moved: the cells for triage at HUNT4 (§9)

| ids | HUNT3 | HUNT4 | baseline | reading |
|---|---|---|---|---|
| `g0915`, `g0916` (E, a callee storing the view into an element of an array of holders, dies-first, `ra`/`rs`) | 70/70, 25/25 `ACCEPTED:DEFECT:uaf` | the same | the same | a face of DEF-252 that landing 116 does not reach: **F-050** |
| `g0249`, `g0250` (B, a dead `wild` load before a `NULL` test, int64 and struct; scope wild) | 107/14 `DEFECT:leg_mismatch` | the same | the same | DEF-251 (i) does not make the legs agree for a load whose value is unused: **F-051**, reported apart |
| `g0692`, `g0694`, `g0696`, `g0704`, `g0706`, `g0708` (C, the pointer twins at the literal and array places that store `@z` into a field or element inside a branch, a loop or an arm) | `OVERRESTRICT`, `BORROW-002` | the same | the same | **not a finding: my expectation was wrong.** D-004 rule 3 refuses a borrow stored into any part of an aggregate ("only a local binding in the borrowing frame is provably no longer-lived than the borrow"), "deliberately strict to start"; the expectation stands as committed (S36, S45) |

## The predicted moves (the brief's P1–P11 and §8's list)

- [x] **P1** — the three seeds flagged at HUNT3: 107/11, 107/99, 170/170, as `ACCEPTED:DEFECT:leg_mismatch`,
  `…:fallthrough`, `…:uaf`.
- [x] **P2** — at HUNT4 `bare_binding` refused `TYPE-055` (114); `null_store` takes the "refused if (ii) has
  landed" branch, `TYPE-096` (119); `probe08h_view_reseated` refused `BORROW-002` (116). Rows 8–10.
- [x] **P3**, with an explanation — at HUNT3 every binding that is neither `fixed` nor initialised is
  accepted, and its write-then-read disagrees across the legs (107/13); a binding with an initialiser was
  refused at HUNT3 already (D-211 asked it since 1.4.2b), the reads give the zero default on both legs
  (13/13), an atomic store faults on both legs (107/107) and a channel `send` reports `ChannelClosed`. At
  HUNT4 every one is refused `TYPE-055` (rows 11–15; A: 157 refused, 9 `fixed` reads clean).
- [x] **P4**, unknown before the run — `@X` of a `fixed` binding is refused `TYPE-071` (D-287) at HUNT3 and
  HUNT4 alike, into a writer or a reader, so it is no new face; `const` is no declaration form (§4).
- [x] **P5** — at HUNT3 the plain `NULL` cells fall through (107/99) or disagree across the legs; at HUNT4
  they are refused `TYPE-096` (119), the "are refused" branch (row 16).
- [x] **P6**, with an explanation — at HUNT3 (and at the baseline) the dead-load cells split. For a
  struct reached through a parameter or a helper's return (`g0224`, `g0237`) the -O2 leg skipped the test,
  107/0, a reported success: **DEF-251's inferred face, measured**. In the other ten plain cells and the
  two `wild` ones it did not skip the test: it deleted the unused load and the test answered 14 (107/14).
  At HUNT4 the plain cells are refused `TYPE-096`, and under (i) the two `wild` cells still disagree,
  107/14: a `leg_mismatch` against (i), as P6 says it would be. F-051.
- [x] **P7** — every read before definite assignment is refused at every compiler (250 of 250 at the
  baseline, HUNT3 and HUNT4); none is accepted. C's six `OVERRESTRICT` are a wrong expectation (above).
- [x] **P8**, unknown before the run — no fold differs across the legs at HUNT3 or HUNT4 (D: 37 refused, 93
  clean at both), and the SAFE twins are clean. At the baseline 16 constant `/ 0`, `% 0` and `MIN / -1`
  cells are accepted and trap at run time, DEF-133's d7 shape, fixed at 79.
- [x] **P9** — at HUNT3 store (2) reads the poison (70 through the observer, 25 with the sentinel), and so
  do (3), (5) and (7); (6), the returned holder, is refused `BORROW-002` at HUNT3 already. At HUNT4 (116)
  (2), (3), (5) and (7) are refused (row 19), and (4), a callee storing into an element of an array of
  holders, is a face 116 leaves open: F-050.
- [x] **P10** — recall 25/25 (row 1); every FIXED finding holds (row 4); M2 0 moved (row 5); M9's 24 moves
  are landing 132's, none 115's (row 6).
- [x] **P11** — the LLVM control: no cell differs (row 0).
- [x] §8: "refusal moves come only from landings whose NOTICES row names them" — row 2 (136 names a
  keyword local), row 3 and row 6 (132 names F-049), rows 8–19 (114, 115, 116, 119, 120).
