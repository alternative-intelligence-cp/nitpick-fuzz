# PLAN — the ownership grid

Written 2026-09-25 by the library workbench's orchestrator (`nitpick-libs`),
for a session that was not present for the planning. Every step says what to
run and what counts as done. Tick the boxes in `PROGRESS.md`, not here.

## The facts this plan rests on

- **The compiler** is `github.com/alternative-intelligence-cp/nitpick`, public.
  It builds with **LLVM 20.1.2 exactly** and Python 3, through its own
  bootstrap ladder: `python3 bootstrap/harness/quickemit.py --keep npkg/main.npk`,
  run from the compiler's root. That command leaves `npkc` (the compiler) and
  `npkrt.o` (the runtime every program links) in `.internal/quickemit/`. This
  is how the libraries' CI builds it on a clean Ubuntu 24.04 machine.
- **The baseline** is commit `c3bdae270d63c93ab6e89825fddeec9425e2c6fd`
  (`c3bdae2`), the close of the compiler's cycle 1.5. The five known defects of
  `KNOWN_DEFECTS.md` are present there. GitHub's CI built it on 2026-09-25 and
  printed its emission `.internal/quickemit/npkc.ll` as **28 111 929 bytes,
  sha256 beginning `4029fc70`**. The compiler's rule (its D-265) is that this
  emission is identical across machines.
- **The hunt compiler** is whatever `origin/main` of the compiler is when M0
  runs. It moves often. On the night of 2026-09-25 it gains the fixes for
  DEF-102, DEF-104 and DEF-105; DEF-99's is already there. So
  `KNOWN_DEFECTS.md` says which fix each known defect needs, and a known
  defect still present at the hunt compiler is deduplicated, not re-reported.
- **The build-and-run recipe** is the libraries' harness recipe, which produced
  every verdict in `KNOWN_DEFECTS.md`:
  ```
  npkc f.npk -o f.ll
  llc -O0 -filetype=obj -relocation-model=static f.ll -o f.o
  ld.lld -static f.o <npkrt.o> -o f
  env -i ./f ; echo $?                     # the -O0 leg
  opt -O2 -S f.ll -o f.opt.ll
  llc -O2 -filetype=obj -relocation-model=static f.opt.ll -o f.opt.o
  ld.lld -static f.opt.o <npkrt.o> -o f.opt
  env -i ./f.opt ; echo $?                 # the -O2 leg
  ```
  Compile from the program's own directory: imports are relative. A signal
  death reports 128+N (139 is SIGSEGV).
- **The cloud VM**: Ubuntu 24.04, 4 vCPUs, 16 GB, 30 GB disk, with Python 3,
  git and gh preinstalled. A command times out after 2 minutes by default, 10 at
  most. **Run downloads and builds in the background and poll them.**

## The decisions taken at planning, and why

- **D1, two compilers.** The baseline makes a recall gate possible: the grid
  must re-find the bugs we already know. The hunt compiler is where new ones
  are.
- **D2, an exhaustive grid, not random generation.** The space is small, a few
  hundred to a couple of thousand programs. Every known defect lives in it, and
  a grid has a statable denominator.
- **D3, exit-code observers, not sanitizers.** The runtime already poisons
  freed memory (`0xAA`) and guards its allocator. The programs are static and
  use no libc, so LLVM's sanitizers do not apply.
- **D4, Python 3 standard library only.** Nothing to install.
- **D5, stop at M4.** The author is calibrating what the run costs before
  committing the rest.
- **D6, findings are verified by the workbench before anyone else sees them.**
  That is the workbench's standing practice: every defect sent to the
  compiler's maintainers was reproduced there first.

---

## M0 — the two compilers

- [ ] **0.1** Record the environment in `PROGRESS.md`: `uname -a`, `nproc`,
  `free -g`, `df -h .`, `python3 --version`.
- [ ] **0.2** LLVM 20.1.2, in the background:
  `mkdir -p .work/llvm && curl -fsSL https://github.com/llvm/llvm-project/releases/download/llvmorg-20.1.2/LLVM-20.1.2-Linux-X64.tar.xz | tar -xJ --strip-components=1 -C .work/llvm`.
  Then assert `.work/llvm/bin/llvm-config --version` prints exactly `20.1.2`.
  **If the download is blocked by the network policy, STOP and say so.** The
  author changes the environment's network access. Never substitute another
  LLVM.
- [ ] **0.3** `git clone https://github.com/alternative-intelligence-cp/nitpick .work/nitpick`
  (full history). Record `git -C .work/nitpick rev-parse origin/main` as **HUNT**.
  Record its `git log -1 --format='%h %ci %s'`.
- [ ] **0.4** Two worktrees: `git -C .work/nitpick worktree add ../base c3bdae2`
  and `git -C .work/nitpick worktree add ../hunt <HUNT>`.
- [ ] **0.5** Build each, in the background, with LLVM first on `PATH`:
  `(cd .work/base && PATH=$PWD/../llvm/bin:$PATH python3 bootstrap/harness/quickemit.py --keep npkg/main.npk) > .work/build-base.log 2>&1`,
  and the same for `hunt`. Record each build's wall time and the sizes and
  sha256 of `npkc`, `npkrt.o` and `npkc.ll`.
  **Commissioning check:** the baseline's `.internal/quickemit/npkc.ll` should
  be 28 111 929 bytes with a sha256 beginning `4029fc70`. A mismatch is a
  finding to record (the emission is meant to be identical across machines),
  not a reason to stop.
- [ ] **0.6** Commission both compilers in both directions.
  `commission/canary.npk` must compile at exit 0, link, and run to exit 0.
  `commission/canary_malformed.npk` must exit 1 printing `NITPICK-PARSE-001`
  and write no `.ll`.
- [ ] **0.7** Commit and push. Tick M0 in `PROGRESS.md` with the two commits,
  the digests, the LLVM version and the build times.

## M1 — the recall suite, `known/`

- [ ] **1.1** Write `gen/run_known.py`. For every `.npk` under `known/*/`,
  except `rows.npk` (a support module the `def105` cases import), apply the
  recipe above at a given compiler. Use a 10-second run timeout; a timeout is
  its own verdict. Print one line per file:
  `dir/file  npkc=<rc> [codes]  O0=<rc>  O2=<rc>`, where `[codes]` are the
  distinct `NITPICK-…-NNN` codes in the compiler's output.
- [ ] **1.2** Run it at the baseline, and compare line by line with
  `KNOWN_DEFECTS.md`'s `c3bdae2` column. **Every row must match.** A mismatch
  means your build or recipe differs from the one the table was measured with.
  Resolve it before M2, and record what you found.
- [ ] **1.3** Run it at HUNT. For each defect whose fix HUNT carries, compare
  with the "once fixed" column. Check whether HUNT carries a fix with
  `git merge-base --is-ancestor <fix> <HUNT>`, or by the fix's commit subject in
  `git log`, as `KNOWN_DEFECTS.md` says.
- [ ] **1.4** Commit `results/known-c3bdae2.txt` and `results/known-<HUNT>.txt`.
  Tick M1.

## M2 — the generator, the runner, the classifier

- [ ] **2.1** Learn the language from what compiles, not from memory.
  - The programs in `known/` all compile at the baseline, and they show the
    conventions: `main` is `func:main = int32(cstring[]:_~argv)`; the
    `failsafe` handler; `raw` on a call whose result is used; `drop` on one
    whose result is discarded.
  - Read the compiler's `meta/specs/TYPE_REFERENCE.md` and
    `BUILTIN_REFERENCE.md` at the baseline.
  - Find the prelude's `List<T>` and its functions (`list_init`, `list_push`,
    …) with `git -C .work/base grep -n "List<"`.
  - **Compile a snippet before you rely on any syntax.**
- [ ] **2.2** Write `gen/grid.py`. It writes one program per cell to
  `cells/<cell-id>/<cell-id>.npk`, plus support modules for the import axis.
  - **A file's name must equal its `mod:` name**, or the compiler refuses it
    (`RESOLVE-012`).
  - Every program uses `known/def102_lent_param/lent_field.npk`'s `failsafe`
    (arms 91–96, 106, 107, and `(*)` exiting 99).
  - If the compiler demands another arm (a `NITPICK-REACH-002` naming it), add
    it with an unused code from 108–119, and record the choice.
- [ ] **2.3** The axes. A cell is one type **T**, one place **P**, one
  operation **O**, and one observer variant.

  **T, the owning type:**
  - `str` is a `string` made by `string_concat("abbb…b", "c")`. That is a
    68-byte heap string; copy the literal from `known/`. It is observed through
    `string_bytes(x)[0i64]`: 97 means intact, 120 means the new value `x…`
    written by the operation, 170 means the free poison.
  - `box` is `struct:Box = { string:s; };`, observed through `.s`.
  - `list` is the prelude's `List<int64>` holding one element, `424242`, and is
    observed by reading element 0. The poison reads as `0xAAAAAAAAAAAAAAAA`,
    which is -6148914691236517206.
  - `wrap` is `struct:Wrap = { List<int64>:l; };`.
  - `arr_str` is `string[2]`; `arr_box` is `Box[2]`.
  - `gen_str` and `gen_box` are a generic `T`, instantiated at `string` and at
    `Box`.

  **P, where the value lives and how it is reached:**
  - `local` — a local binding;
  - `fixed_scalar` — a module-level `fixed` binding;
  - `fixed_elem` — an element of a `fixed` array;
  - `lent_param` — an ordinary by-value parameter, which is a LOAN in this
    language;
  - `move_param` — a `move T:x` parameter;
  - `ptr_param` — a `T->` parameter;
  - `for_binding` — `for (T:x in arr)`;
  - `field` — a field of a local struct;
  - `elem` — an element of a local array;
  - `imported_fixed` — a `fixed` table declared in a second module. Import it
    four ways: with its row type, without it, beside a same-named struct in the
    importer, and beside a same-named struct that is wider;
  - `generic_param` — `T:x` inside a generic body.

  **O, the operation:**
  - `copy` — `T:y = x;`
  - `move` — `T:y = move(x);`
  - `pass_out` — `pass x;` out of the function that holds it;
  - `field_write` — `x.s = …;`, for types with fields;
  - `assign` — `x = …;`
  - `at_callee` — hand `@x` to a callee taking `T->` that frees, grows or
    overwrites through it;
  - `clone` — `x.clone()`, a control;
  - `read` — a read and nothing else, a control.

  **Observer variants, two per cell:**
  - `read_after` — after the operation, read the ORIGINAL through its
    observer. Exit 70 on the poison, 0 on the value the rules say it should
    hold, 20–29 on a live but unexpected value (each code named in the cell's
    metadata).
  - `drop_at_exit` — no read. Return normally so every drop runs; a double
    free shows as 95.

  **Not every combination means something.** For example, `field_write` on a
  bare `str`, or `fixed_elem` on a non-array, does not. Emit a cell only where
  the combination does. Write the skipped ones, each with its reason, to
  `cells/SKIPPED.txt`. The denominator is stated, not implied.

  **Each cell's metadata carries the expected answer**, as your reading of the
  language's rules. It is either **REFUSE** (for example a copy of an owning
  value, a move out of a lent parameter or out of `fixed` storage, or a write
  path through a lent owning parameter) or **SAFE** (compiles and runs clean).
  A cell whose verdict differs from its expectation is where you look first.
- [ ] **2.4** Write `gen/run.py`. It compiles, links and runs each cell at a
  given compiler on both legs, by the recipe.
  - Run 4 jobs at a time, with a 120-second compile timeout and a 10-second
    run timeout.
  - Write one JSON line per cell to `results/<commit>/cells.jsonl`: the cell
    id, T, P, O, the observer, the expectation, npkc's rc and codes, the -O0 rc
    and the -O2 rc.
  - **It must be resumable**: skip every cell already in the file.
- [ ] **2.5** Write `gen/classify.py`. Classes:
  - `refused` (with its codes) and `clean`;
  - `DEFECT:uaf` (70);
  - `DEFECT:double_free` (95);
  - `DEFECT:segv` (107 or 139);
  - `DEFECT:wrong_value` (the cell's 20–29 codes, or 10 from the import cases);
  - `DEFECT:leg_mismatch` (-O0 ≠ -O2);
  - `CRASH:npkc` (an npkc rc other than 0 or 1, or a signal);
  - `OVERRESTRICT` (a `clone` or `read` control refused);
  - `timeout`;
  - `other`. Look at each `other` by hand.

  It writes `results/<commit>/SUMMARY.md`: the count per class, and per class
  per axis value.
- [ ] **2.6** Commit and push. Tick M2 with the grid's size: cells generated,
  cells skipped, and both split by axis value.

## M3 — the recall gate, at the baseline

- [ ] **3.1** Run the whole grid at `c3bdae2`.
- [ ] **3.2** The grid must flag, as `DEFECT:*`, cells of each known shape:
  - **DEF-99** — `fixed_scalar` or `fixed_elem` × `move` or `pass_out`;
  - **DEF-102** — `lent_param` × `field_write`, `assign` or `at_callee`;
  - **DEF-104** — `generic_param` × `pass_out`, at `gen_str` or `gen_box`;
  - **DEF-105** — `imported_fixed` beside a same-named struct, without its row
    type.

  It must also classify the known refusals as `refused`: a `copy` of a local
  `str` gives `NITPICK-TYPE-046`, and a non-generic `pass_out` of a lent `str`
  gives `NITPICK-TYPE-047`.
- [ ] **3.3** **If any known defect is not flagged, the grid or the classifier
  is wrong. Fix it and re-run before M4.** Record every miss and its fix: that
  record is what validates the fuzzer.
- [ ] **3.4** Commit `results/c3bdae2/`. Tick M3 with the recall table, each
  known shape mapped to the cell ids that flagged it.

## M4 — CALIBRATION CHECKPOINT: stop here

- [ ] **4.1** Run the first ~100 cells, in cell-id order, at HUNT. Commit and
  push.
- [ ] **4.2** End your turn with a summary:
  - the milestones done;
  - the grid's size;
  - the recall table;
  - the ~100 HUNT verdicts by class;
  - every `DEFECT` at HUNT that is not in `KNOWN_DEFECTS.md`;
  - your estimate of what M5 costs: the cells left, and the anomalies the
    first 100 suggest.
- [ ] **4.3** **Wait.** The author checks the cost and tells you whether to
  continue.

## M5 — the hunt

- [ ] **5.1** Run the rest of the grid at HUNT. Commit and push at least every
  45 minutes.
- [ ] **5.2** Take each `DEFECT`, `CRASH` and `OVERRESTRICT` at HUNT through
  five steps:
  - **(a)** Deduplicate it against `KNOWN_DEFECTS.md`. The same shape with its
    fix not yet in HUNT is known: note the cell id and move on.
  - **(b)** Otherwise minimise it: delete statements one at a time, keeping
    the smallest program that still shows it. Keep beside it a control that
    does not.
  - **(c)** Confirm it on both legs, twice.
  - **(d)** Run it at the baseline too, to tell a regression from an old
    defect.
  - **(e)** Write `findings/F-NNN-<slug>/` with the program or programs and a
    `README.md` holding:
    - the shape in one sentence;
    - the verdicts, as compiler × leg × (npkc, run);
    - the control;
    - the deduplication argument;
    - what you measured, kept separate from what you infer.
- [ ] **5.3** Tick M5 with the counts: cells run, anomalies, known, new.

## M6 — the report

- [ ] **6.1** Write `REPORT.md` with:
  - the two compiler commits;
  - the grid's denominators: generated, skipped (with the reasons), refused,
    clean, and each anomaly class;
  - the recall table;
  - the findings table: id, shape, class, and the HUNT and baseline verdicts;
  - **what the grid does not cover**: the types, places and operations outside
    it, and the observers' blind spots.
- [ ] **6.2** Commit, push, and end with a summary.

## M7 — only if the author asks

Widen the grid:
- more types: `buffer`, `OwnedFd`, `dyn`;
- more places: `pick` payloads, `Result` and `?`, nested generics, closures if
  the language has them;
- a documentation sweep of the compiler's reference against the compiler's
  behaviour.

## Acceptance for the whole job

M3's recall table is complete, with every known shape flagged by at least one
cell. `REPORT.md`'s denominators add up. Every finding carries a minimal
reproducer and a control.
