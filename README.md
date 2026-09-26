# nitpick-fuzz

A systematic hunt for **memory-safety defects in the Nitpick compiler**: programs
the compiler *accepts* that then read freed memory, free twice, write read-only
memory, or behave differently at `-O0` and `-O2`.

Nitpick's promise is that an accepted program without an explicit unsafe
construct (`wild`, `=>!`, raw pointer arithmetic) cannot do any of those things.
On 2026-09-25 the libraries built on it found five places where that promise
did not hold — a move out of `fixed` storage, a write through a lent parameter,
a generic identity function, an imported table read with the importer's row
type — each by hand, each in the same space: **where an owning value lives,
crossed with what is done to it**. This repository crosses those two axes
exhaustively instead of waiting for the next one to be stepped on.

## How it works

1. **A grid.** Every combination of an owning type (`string`, a struct holding
   one, the prelude's `List<int64>`, arrays of them, a generic `T`), a place
   (a local, `fixed` storage, a lent / `move` / pointer parameter, a `for`
   binding, a field, an element, an imported table, a generic body) and an
   operation (copy, move, `pass`, field write, whole assignment, `@` handed to a
   callee, `.clone()`, read) becomes one small program.
2. **Two compilers.** Each program is compiled by a *baseline* compiler — commit
   `c3bdae2`, where the five known defects are present — and by the *hunt*
   compiler, the newest commit on the compiler's `main`.
3. **Two legs.** Every accepted program is linked and run at `-O0` and through
   `opt -O2`, and its exit code is classified.
4. **A recall gate.** Before the hunt counts, the grid must re-find every known
   defect at the baseline (`known/`, `KNOWN_DEFECTS.md`). A fuzzer that cannot
   find the bugs we already know about is not evidence about the ones we don't.

Findings go to `findings/`, each a minimal reproducer with its verdicts on both
compilers and both legs, deduplicated against the known list.

## Status

The results are in [`REPORT.md`](REPORT.md), and each confirmed anomaly is in
[`findings/`](findings/). The live state is [`PROGRESS.md`](PROGRESS.md). The plan is [`PLAN.md`](PLAN.md); anyone
working in this repository — a cloud session or a local one — starts at
[`CLAUDE.md`](CLAUDE.md).

## Relation to the rest of the ecosystem

Read-only use of the compiler at [`nitpick`](https://github.com/alternative-intelligence-cp/nitpick);
findings are verified by the library workbench
([`nitpick-libs`](https://github.com/alternative-intelligence-cp/nitpick-libs))
and relayed to the compiler's maintainers from there.

Licensed under the Apache License 2.0.
