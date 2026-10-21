# F-050 — a callee that stores a block-local view into an ELEMENT of an array of holders outlives its storage: a use after free in safe code, live at HUNT4

**A soundness hole** (the M13 brief's §9: the compiler accepts what it should refuse, and the program
reads freed memory). It is DEF-252's shape, a view re-seated by a callee, at a destination landing 116
does not reach: an element of the array behind the pointer argument. **Present at the baseline**: an old
hole, not a regression.

**The shape.** A callee `func:seti = NIL(Cursor[2]->:a, fixed uint8[]:src) never fails { (<-a)[0i64] =
Cursor{ src: src, pos: 0i64 }; pass NIL; };`, called as `drop seti(@cs, string_bytes(t));` inside a block
that declares the string `t`, with the array `cs` declared outside it. `npkc` exits 0, and after the block
`cs[0i64].src[0i64]` reads 170 (0xAA, the allocator's free poison) at -O0 and at -O2. The same store written
directly in the block, `cs[0i64] = Cursor{ src: string_bytes(t), pos: 0i64 };`, is `NITPICK-BORROW-002`
(D-004 rule 3, DEF-42's holder-scope rule), and a callee storing the view into the WHOLE pointee is
`BORROW-002` since landing 116. A callee writing only the view field of an element, `(<-a)[0i64].src =
src`, reads the poison too.

**Found by** grid13 at HUNT4 `c72639f` (M13): section E, store (4), dies-first, `g0915` (`ra`, the view
read through the observer: 70/70) and `g0916` (`rs`, a same-sized sentinel allocated after the block and
read through the view: 25/25, the freed body reused). Both are the same at HUNT3 and at the baseline.

## Verdicts

Measured on 2026-10-21 by PLAN.md's recipe through `gen/run_findings.py`: at HUNT4 `c72639f` twice and the
baseline once under LLVM 20.1.8 (`VERDICTS.txt`; the HUNT4 runs agree), and at HUNT3 `0c0f5a3` twice and the
baseline once (`VERDICTS-0c0f5a3.txt`). The baseline under its own LLVM 20.1.2, by `gen/snip.py` (§9 (d)),
gives the same verdicts.

| program | HUNT4 `c72639f`, runs 1 and 2 | HUNT3 `0c0f5a3` | baseline `c3bdae2` |
|---|---|---|---|
| `elem_callee.npk`, the shape above (minimised by `gen/minimize.py`, keeping 0/170/170) | 0 / 170 / 170 | 0 / 170 / 170 | 0 / 170 / 170 |
| `elem_field_callee.npk`, the callee writes an element's view field (`Seat`'s grouped `(fixed uint8[])` field) | 0 / 170 / 170 | 0 / 170 / 170 | 1, `PARSE-001` (the grouped field type is later) |
| control `ctl_elem_direct.npk`, the same element store written directly in the block | 1, `BORROW-002` | 1, `BORROW-002` | 1, `BORROW-002` |
| control `ctl_whole_callee.npk`, a callee storing into the whole pointee (DEF-252's own shape) | 1, `BORROW-002` | 0 / 170 / 170 | 0 / 170 / 170 |
| control `ctl_elem_outlives.npk`, the callee's element store with the string declared before the array | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

A program's exit is the first byte the view reads: 103 (`g`) is the new string, which `ctl_elem_outlives`
checks and turns into 0; 170 is the free poison.

**The controls** (rule 5). `ctl_elem_outlives` is the control an implementation refusing every element
store through a callee gets wrong: the storage outlives the holder, so it must compile and read the new
bytes. `ctl_elem_direct` shows the rule decides this destination when the store is direct. `ctl_whole_callee`
separates landing 116 from what came before: refused at HUNT4, the poison at HUNT3 and the baseline.

## Deduplication

- `KNOWN_DEFECTS.md`: DEF-252 (fixed at 116) is a callee's store into the whole pointee. Its registry row at
  HUNT4 says what 116 asks: DEF-42's holder-scope question "of every argument the callee's matrix flows into a
  destination this frame owns, a local or a by-value parameter", and a destination behind a dereferenced
  pointer (`@(<-p)`). Landing 116's own test (`tests/analysis/rejection/view_reseat_call.npk`) has sixteen
  sites: the whole pointee, a field, a nested callee, `list_push` and `list_insert`, a method receiver, a
  `dyn`, a function value, a struct argument, an awaited async callee, an address through a callee, a loop
  body's string, a `move` parameter holder, `@(<-cp)` and a view-holding local. None is an element of an
  array behind the pointer.
- The compiler's registry at HUNT4 (`OPEN_DECISIONS.md` at `c72639f`) has no entry for it. DEF-42 is the
  direct form, refused (`ctl_elem_direct`).
- The tie to a later registry: the compiler's `origin/main` was fetched again at 05:05 EDT on 2026-10-21,
  before this was written, and it was still HUNT4: no newer landing to measure.
- Present at HUNT3 and the baseline, so it is not a regression: 116 closed the whole-pointee, field,
  method and nested forms (grid13's E stores (2), (3), (5) and (7)) and not this one.

## Measured, and inferred

- *Measured:* the verdicts above, and grid13's `g0915`/`g0916` at the baseline, HUNT3 and HUNT4.
- *Inferred, not measured:* that the callee's store matrix (D-325) does not connect a store through
  `(<-a)[i]` to the pointer argument's pointee, or that 116's holder-scope question is not asked of such a
  destination. The compiler's source was not read.
