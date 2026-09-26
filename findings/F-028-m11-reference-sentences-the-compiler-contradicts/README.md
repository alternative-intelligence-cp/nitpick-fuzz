# F-028 — ninety-four M11 claims whose reference sentence the compiler contradicts, where the compiler is right or at least safe (documentation findings)

PLAN.md 11.2: "The compiler right and the reference wrong is a documentation finding".
These are M11's, over the extracted ranges (BUILTIN, CONCURRENCY, IO and MACRO whole,
TYPE 1–660, VERIFICATION 1–1247). The rows, with each claim's program and its verdicts
at HUNT2 `9126350`, the baseline `c3bdae2` and the newest `main` `1b4f0c6`, are in
[`ROWS.md`](ROWS.md). Every row gives the same result at all three but one (`cc0042`
at the baseline, refused with other codes).

**By kind** (a claim may stand for several rows of one table):
- **A surface the language does not have.**
  - TYPE §2's char8 functions (`toUpper` … `toChar32`: 12 rows) and §3.2's string
    functions (`charAt` … `fromCharArray`, `string_eq`, `to_string` of a cstring: 17);
  - `tensor`, `matrix`; the `Stream` trait; an `Actor` type; `ThreadPool.create`;
    `#align_of`; `text_writer_create`;
  - the flags `--seccomp`, `--extra-picky=no-sys` and `--extra-picky=no-wild`
    (`vf0811`'s second half);
  - inline assembly (`bi0432`, `bi0439`).
- **A stale spelling or name.**
  - `?! 9tbb32` / `?! 7tbb32` (`?!` takes a declared `Error`, D-179);
    `close(release_fd(move o))` (`move(o)`); `atomic_from_ptr<int32>(p)`;
    `assert_static comptime(…)`; `const` (D-222);
  - `DEADLINE_EXCEEDED` for `DeadlineExceeded`, `E_EOF` for `IoEof`;
  - `NITPICK-040` for `TYPE-043`, `TYPE-064` for `TYPE-060`.
- **An example that does not compile as written.**
  - `main` with no parameter (CONCURRENCY:42);
  - `raw` on a callee that is not `never fails` (MACRO:112);
  - a mutable module binding (MACRO:159, D-211);
  - redeclared prelude units (TYPE:580).
- **A rule a later decision changed.**
  - A borrow may cross an `await` since D-180 (CONCURRENCY:298, VERIFICATION:268, 819);
  - `fixed` folds in `comptime` since D-222 (MACRO:334);
  - a spawned task returns `NIL` (D-177, CONCURRENCY:73);
  - `thread` is a keyword (CONCURRENCY:21);
  - nit/nyte are balanced (TYPE:306–307 against TYPE §6 and D-197);
  - unsuffixed literals are accepted in a typed context (MACRO:371);
  - `sys`'s nested-builtin refusal is stale (D-201).
- **A sentence that contradicts another in the same reference.**
  - `await f()` is `Result<T>` (CONCURRENCY:53) or `T` (:142);
  - a `requires` on a `never fails` function (VERIFICATION:351 yes, :437 no);
  - a bare `tfp256` return (TYPE:634 against the explicit drop at :618).
- **What the compiler emits or encodes, misdescribed.**
  - No `llvm.coro` and no `%Future`;
  - a bool branch is `icmp ne`, not `trunc`;
  - `tbb` does not use the `with.overflow` intrinsics;
  - `tfp256` is `i256`, not four `i64`s;
  - `.len` is a per-binding `|len.x.N|`, not `(|npk.len| base)`;
  - a struct subject's `limit` and a `List`-count loop bound are encoded;
  - an await of a limited coroutine has a `limit-subsume` row;
  - a `simd` float-to-int cast has no `cast-range` row, though its guard traps;
  - a `simd` float `.min()` returns a NaN in the last lane (VERIFICATION:1201 says a NaN
    lane is passed over; the lane order decides).
- **A rule the compiler does not enforce, harmlessly.**
  - The standard streams are not confined to `main` (IO:242);
  - `#wild_ptr`, `#ptr_add` and `atomic_from_ptr` work outside `wild`, which no
    reference defines (session 6's BUILTIN candidates; D-315 struck the like rule).

## Deduplication

F-017's seven rows (DEF-133) are not repeated here: M11's `ty0366`, `ty0366b`,
`ty0367` and `ty0475` are those sentences and are classed "known". DEF-100 and DEF-101
are documentation defects whose sentences `KNOWN_DEFECTS.md` does not give, so they
could not be checked against these rows. The workbench can.

## Measured, and inferred

- **Measured:** every row's result at three compilers.
- **Reasoned:** that the compiler is the right side in each row: by a decision the row
  cites, by a sibling sentence, or because the construct is safe as the compiler treats
  it. Where the compiler might instead be the one to move, the row is in F-027 (c), not
  here.
