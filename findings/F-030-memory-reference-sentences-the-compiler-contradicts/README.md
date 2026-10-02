# F-030 — MEMORY_REFERENCE: nine sentences the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over MEMORY_REFERENCE (all 533 lines) at HUNT2: 181 claims, 146 tested,
137 agree, 9 disagree. Eight of the nine are documentation rows (below). The ninth is
DEF-148 (F-022), whose shape is refused `BORROW-016` at `93bcb66`. The rows, with each
claim's program and its verdicts at HUNT2, the baseline and the newest `main`
`93bcb66`, are in [`ROWS.md`](ROWS.md). All eight give the same result at all three.

- **Stale examples.**
  - `wildx uint8->:code = wildx_alloc(4096i64);` (MEMORY:126) is `TYPE-007`: the result
    is `int8->` and needs `=>! wildx uint8->`.
  - `#wild_ptr<int8->>(addr)` (MEMORY:136) passes the pointer type where the argument is
    the pointee, giving `int8->->`.
  - `wild int8->:manual_buf = nodrop alloc(16i64);` (MEMORY:174) puts `nodrop` on the
    initialiser. It qualifies the binding (DECISIONS: "`nodrop` requires `wild` or
    `wildx`").
  - The `move` example (MEMORY:184) uses `malloc`/`free`, which §3:281 itself says do
    not exist, and names its binding `buffer`, a reserved word (F-029). The refusal it
    describes is coded `NITPICK-019`, a code the compiler does not have.
  - The arena example and its note (MEMORY:385, :399) take `?` as the fallback. It is
    `?|` since D-175 (`PARSE-011`).
- **A rule the compiler does not enforce, harmlessly.** `#wild_ptr` is "legal only in
  `wild` context (D-019)" (MEMORY:133). It is accepted bound to a plain pointer, as
  BUILTIN's row `bi0417b` (F-028) found; D-315 struck the like rule from `#wild_slice`.
- **A sentence a later decision changed.** "An un-destroyed arena is a wild-role leak
  the exit-time check names" (MEMORY:397): an `arena<T>` left undestroyed at `exit 0`
  is not reported, because its storage is managed since D-183. The runtime's
  `npk_arena_make` says so: "MANAGED, NOT WILD (D-183, 1.2.5c) … They were wild while
  `destroy` was the only reclaimer". A `shared_arena<T>` is still counted (`me0482`
  agrees).

**One more row, from run 1:** MEMORY:121's example names its binding `buffer`. It
compiles only because the example never uses it (F-029). Its program now uses `buf` and
agrees.

## Deduplication

These are MEMORY's sentences, none of them among F-028's rows (DEF-154, open). F-028's
`bi0417b` is BUILTIN's sentence about `#wild_ptr`; MEMORY:133 is the same rule stated
again, so it is listed here as its own row. The registry at `93bcb66` has no entry for
any of the eight.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and the runtime comment quoted.
- **Reasoned:** that the compiler is the right side in each, by the decision cited.
