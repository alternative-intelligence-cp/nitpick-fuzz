# CLAUDE.md — nitpick-fuzz

**You are the fuzzing session.** Your job is `PLAN.md`, milestone by milestone,
recording each step in `PROGRESS.md`. Read these three files before anything
else: this one, `PLAN.md`, `PROGRESS.md`. If `PROGRESS.md` shows work already
done, **resume from the first unticked box** — never redo a ticked one.

## First, before any work: the order is a gate

A milestone starts only after the workbench has merged the one before it into
`main`, and a session can start from a stale `main` — M9's did, from a `main`
without M8, and was saved only because a message reached it. So, before
anything else:

1. **Fast-forward to `origin/main`:** `git fetch origin && git merge --ff-only
   origin/main`. If that is not a fast-forward, STOP and say so.
2. **Read `PROGRESS.md`. If the milestone BEFORE the one you were asked to do
   is not ticked, STOP** and end your turn naming the unticked box. Never do
   the previous milestone yourself, and never redo a ticked one: an unticked
   predecessor means the order has slipped, and only the author says how it is
   recovered.

## The rules

1. **Write only in this repository.** Never push to, open issues on, or open
   pull requests against any other repository. The compiler
   (`alternative-intelligence-cp/nitpick`) is **read-only**: clone it into
   `.work/` (gitignored) and build it there; never commit to it.
2. **Commit and push after every milestone and at least every 45 minutes of
   work**, with `PROGRESS.md` updated in the same commit. A session can be
   stopped at any moment — by the author, by a spending limit, by inactivity —
   and what is not pushed is lost. The next session resumes from `PROGRESS.md`.
3. **STOP at the calibration checkpoint (milestone M4)** and end your turn with
   the summary M4 asks for. The author checks what the run has cost before
   letting it continue. Do not continue past M4 until told to.
4. **Measured, not inferred.** Every verdict in a finding is a command you ran,
   with its exit code, at a named compiler commit, on a named leg. Where you
   reason rather than measure, say so in those words.
5. **A control must be a case the WRONG implementation gets wrong**, and must
   assert that its substitution matched. A result is read from its named line,
   never from an exit status alone.
6. **Be frugal with output.** Never print a whole `.ll`, a whole log or a whole
   results file; print counts and the lines that matter. Long runs go to log
   files you then summarise.
7. **Parallelism: at most 4 jobs** (the cloud VM has 4 vCPUs and 16 GB). A
   compile of a small program uses ~15 MB; the compiler's own build more.
8. **Do not work around a defect you find** — record it and carry on with the
   grid. You are finding them, not fixing them.
9. **Do not edit `PLAN.md`'s goals.** Record decisions you take, and any
   deviation from the plan with its reason, in `PROGRESS.md`'s decisions
   section.

## What "a defect" means here

An **accepted** program (the compiler exits 0) that contains no `wild`, no
`=>!` and no raw pointer arithmetic, and that at run time:

- reads freed memory — the allocator poisons freed bytes with `0xAA`, so an
  observer reading `170` is a use-after-free (the grid's programs exit **70**);
- frees twice or frees what it never allocated — the runtime stops as
  `Unreachable` (**95** under the grid's failsafe);
- writes read-only memory — `SIGSEGV`, reported as `MachineFault` (**107**) at
  `c3bdae2` and later, or **139** as a raw signal;
- reads the wrong field or past an object's end (the grid's observers exit
  **10**-range codes the template defines);
- or gives a **different exit code at `-O0` and through `opt -O2`**.

**And a SILENT WRONG ANSWER is a defect too — the author's rule, 2026-09-26.**
An accepted program whose result differs from what the language's reference
says it must be, with no memory error at all, counts exactly as a
memory-safety fault does. Examples:
- a function that falls off its end and returns a zero value (DEF-108);
- an error path that becomes a success;
- a write the program never sees;
- a default value standing in for one never set.

**Never file one as "an observation outside the defect definition".** This
repository's first run did exactly that with DEF-108, and the author caught it
by reading the session's reasoning.

Also report, at lower priority: the compiler **crashing** (an exit other than 0
or 1, or a signal), and a **control refused** — a `.clone()` or a plain read
that the compiler will not accept.

A **refusal** of an unsafe operation (`NITPICK-TYPE-046`, `-047`, `-084`,
`-085` and the like) is the language working, not a finding.

## Where things go

| path | what |
|---|---|
| `.work/` | the compiler clones, LLVM, scratch — gitignored, never committed |
| `gen/` | the generator, the runner, the classifier (Python 3, stdlib only) |
| `cells/` | generated programs — gitignored; regenerable from `gen/` |
| `results/<compiler>/` | one JSON line per cell per compiler, plus `SUMMARY.md` — committed |
| `findings/F-NNN-<slug>/` | each confirmed anomaly: minimal program(s), `README.md` |
| `REPORT.md` | the final report (milestone M6) |
