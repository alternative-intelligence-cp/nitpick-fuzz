# F-052 — an atomic's method called through a pointer with `.` passes the checker and the emitter cannot lower it (`EMIT-002`)

**Lower priority** (`CLAUDE.md`: the compiler failing). The M13 brief's §9 class: **crash / loud emission**,
the compiler failing on a legal program. Its own message says so: "the emitter could not lower this,
although the frontend accepted it; a defect in the compiler rather than in this program".

**The shape.** `func:put = NIL(atomic<int64>->:p) never fails { p.store(7i64); pass NIL; };` is
`NITPICK-EMIT-002` at 3:50, the `p.store(…)`. So is `p.load()` through the same parameter (3:57), and
`q.store(7i64)` through a local `atomic<int64>->:q = @t;` (6:6). The explicit dereference, `(<-p).load()`,
compiles and runs 0/0, and the methods called on the atomic itself compile and run.

**What the references say.** CONCURRENCY_REFERENCE §4.2 at HUNT4: the atomic's six methods, `.load()`,
`.store(v)`, `.swap(v)`, `.fetch_add(v)`, `.fetch_sub(v)`, `.compare_exchange(expected, desired)`, and
"Methods dispatch via UFCS". TYPE_REFERENCE §10: `ptr.field` is unified member access, which "automatically
dereferences if pointer" (D-098, one level).

**Found by** M13's learning by snippet (§4, probe `q_a09`, an atomic through a pointer parameter), and in
grid13 at HUNT3 and the baseline, where section A's four atomic address cells (`g0119`, `g0120`, `g0127`,
`g0128`, a module `atomic<int64>` with no initialiser handed to a writer or a reader by `@`) are refused
`EMIT-002`. At HUNT4 those four are refused `TYPE-055` at their declaration first (landing 114), so the grid
no longer sees it; these programs use a local atomic.

## Verdicts

Measured on 2026-10-21 by PLAN.md's recipe through `gen/run_findings.py`: at HUNT4 `c72639f` twice and the
baseline once under LLVM 20.1.8 (`VERDICTS.txt`; the HUNT4 runs agree), and at HUNT3 `0c0f5a3` twice and the
baseline once (`VERDICTS-0c0f5a3.txt`). The baseline under its own LLVM 20.1.2, by `gen/snip.py`, gives the
same verdicts. These programs are written by hand, as F-049's were (S74): `gen/minimize.py` keeps only
npkc's exit and the legs, and a refusal minimised that way can keep any refusal at all.

| program | HUNT4 `c72639f`, runs 1 and 2 | HUNT3 `0c0f5a3` | baseline `c3bdae2` |
|---|---|---|---|
| `atomic_ptr_store.npk`, `p.store(7i64)` through an `atomic<int64>->` parameter | 1, `EMIT-002` at 3:50 | 1, `EMIT-002` | 1, `EMIT-002` |
| `atomic_ptr_load.npk`, `p.load()` through the parameter | 1, `EMIT-002` at 3:57 | 1, `EMIT-002` | 1, `EMIT-002` |
| `atomic_local_ptr.npk`, `q.store(7i64)` through a local pointer | 1, `EMIT-002` at 6:6 | 1, `EMIT-002` | 1, `EMIT-002` |
| control `ctl_atomic_ptr_explicit.npk`, `(<-p).load()` | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| control `ctl_atomic_direct.npk`, `t.store(7i64)` and `t.load()` on the atomic | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

**The controls** (rule 5). `ctl_atomic_ptr_explicit` is the control an implementation that cannot lower an
atomic behind a pointer at all gets wrong: with the dereference written, the same operation through the
same parameter lowers and answers 5. `ctl_atomic_direct` shows the methods themselves lower.

## Deduplication

- `KNOWN_DEFECTS.md` has no atomic row. The compiler's registry at HUNT4 (`OPEN_DECISIONS.md` at `c72639f`)
  has no entry for an atomic method through a pointer: a search for "atomic" beside `EMIT-002` or a
  pointer finds only B-7, an instrument row. DEF-194 and DEF-236 (a) were `EMIT-002` of a `comptime` value
  parameter, another construct (refused by name at 117).
- The compiler's `main` at 05:05 EDT on 2026-10-21 was still HUNT4.
- Present at HUNT3 and the baseline: an old defect, not a regression.

## Measured, and inferred

- *Measured:* the verdicts above, and grid13's four atomic address cells at the baseline and HUNT3.
- *Inferred, not measured:* that the checker resolves the method through the one-level auto-dereference
  (D-098) while the emitter's atomic path is handed the pointer where it expects the atomic's place. The
  compiler's source was not read.
