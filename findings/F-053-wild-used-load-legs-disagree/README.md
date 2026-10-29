# F-053 — a load through a `wild` NULL pointer whose value the program text reads is sunk or deleted at -O2: the legs disagree where §27 promises a fault at both (scope wild)

**Reported apart, as the check of TYPE_REFERENCE §27 (D-364)** (the M14 brief's §7), as F-051 was. The programs
contain `wild`, which `CLAUDE.md`'s defect definition excludes, so this is not a defect by that definition and takes
no class from it. It is a measurement against §27's own promise, at the boundary D-364 leaves open: whether these
forms USE the value, §27's words do not settle. grid14 wrote their expectation by the strict reading (a value the
text reads is used, so both legs fault), and a disagreement is reported, not permitted.

**The shape.** `wild int64->:p = NULL; int64:v = <-p;`, then `v` is read, but on the path run the exit does not
depend on it: read only inside a branch not taken (`if (argv.len > 100i64) { … }`), passed to a callee that ignores
it, copied into a local never read, used in `v - v`, or used in `v != v`. The -O0 leg executes the load and faults
(`MachineFault`, 107). The -O2 leg does not execute it and exits 0, a reported success: 107/0.

**What §27 says at HUNT5 `249eae9`** (the `NULL` subsection's last bullet, TYPE_REFERENCE.md:2314–2324): "A store
through a `NULL` pointer (a `wild` one, since landing 119), or a load from one whose value the program USES, is a
hardware fault that reaches `failsafe` as `MachineFault` (D-307) at BOTH legs … A load whose value NOTHING uses is
no read at -O2 … and faults at -O0: the legs' one permitted disagreement, narrow to an unused load through a `wild`
`NULL` pointer (D-364, 2026-10-22; DEF-273, the fuzzer's F-051 …)." D-364 at HUNT5: "THE ALLOWANCE IS NARROW, so
that it cannot hide a real disagreement between the legs: it covers an UNUSED load through a `wild` NULL pointer and
nothing else -- a used load, a store, a plain pointer …, and every other construct still answer alike at -O0 and
-O2".

**Found by** grid14 (M14), section B, the boundary of "uses": `m091_b_int64_local_untaken`,
`m093_b_int64_local_ignore`, `m095_b_int64_local_copy`, `m097_b_int64_local_selfsub`, `m099_b_int64_local_selfcmp`
and their struct twins `m092`, `m094`, `m096`, `m098`, `m100` (the struct read as `v.a`, an `S` passed whole to
`ign`, `S:w = v;`), all 107/0 at HUNT5, `DEFECT:leg_mismatch` under `gen/classify14.py` (they carry no `s140` flag,
so the S-140 class never applies). B's sixth form, `deadadd` (`int64:w = v + 1i64;`, `w` never read), is 107/107 at
HUNT5, clean. The brief's P5 named it: "`untaken`, `ignore`, `copy`, `selfsub` and `selfcmp` give 107/0 … `deadadd`
gives 107/107 … Together they make one candidate, F-053." The manager's probes at landing 148 gave the same
(`q03_untaken`, `q05_ignore`, `r15_copy`, `r06_selfcancel`, `r18_selfcmp`: 107/0; `r04_deadcalc` 107/107), and M14's
re-run of them at HUNT5 gives the same again.

## Verdicts

Measured on 2026-10-25 by PLAN.md's recipe through `gen/run_findings.py` under LLVM 20.1.2: at HUNT5 `249eae9` twice
and the baseline `c3bdae2` once (`VERDICTS.txt`; the HUNT5 runs agree for every program).

| program | HUNT5 `249eae9`, runs 1 and 2 (npkc / O0 / O2) | baseline `c3bdae2` |
|---|---|---|
| `wild_load_read_untaken.npk`: `v` read only inside `if (argv.len > 100i64) { … }` | 0 / 107 / 0 | 0 / 107 / 0 |
| `wild_load_to_ignoring_callee.npk`: `int32:r = raw ign(v); exit r;`, `ign` ignoring its `_~x` | 0 / 107 / 0 | 0 / 107 / 0 |
| `wild_load_copied_unread.npk`: `int64:w = v;`, `w` never read | 0 / 107 / 0 | 0 / 107 / 0 |
| `wild_load_self_sub.npk`: `if (v - v != 0i64) { exit 12i32; }` | 0 / 107 / 0 | 0 / 107 / 0 |
| `wild_load_self_cmp.npk`: `if (v != v) { exit 12i32; }` | 0 / 107 / 0 | 0 / 107 / 0 |
| control `ctl_wild_used_cmp.npk`: the value decides the exit (`if (v == 0i64) { exit 13i32; } exit 12i32;`, K's `cmp`) | 0 / 107 / 107 | 0 / 107 / 12 |
| control `ctl_wild_dead_load.npk`: `int64:v = <-p; exit 0i32;`, the permitted dead load (F-051's shape) | 0 / 107 / 0 | 0 / 107 / 0 |
| control `ctl_wild_dead_add.npk`: `int64:w = v + 1i64;`, `w` never read (B's `deadadd`) | 0 / 107 / 107 | 0 / 107 / 0 |

grid14's ten cells, from `results/249eae9/classified14.jsonl` and `results/c3bdae2/classified14.jsonl`:

| form | `int64` at HUNT5 / baseline | struct S at HUNT5 / baseline |
|---|---|---|
| `untaken` | 107/0 / 107/0 (`m091`) | 107/0 / 107/99 (`m092`) |
| `ignore` | 107/0 / 107/0 (`m093`) | 107/0 / 107/99 (`m094`) |
| `copy` | 107/0 / 107/0 (`m095`) | 107/0 / 107/0 (`m096`) |
| `selfsub` | 107/0 / 107/0 (`m097`) | 107/0 / 107/0 (`m098`) |
| `selfcmp` | 107/0 / 107/0 (`m099`) | 107/0 / 107/0 (`m100`) |
| `deadadd` (holds) | 107/107 / 107/0 (`m101`) | 107/107 / 107/99 (`m102`) |

**Where the load goes at -O2** (measured at HUNT5: `npkc` then `opt -O2` under 20.1.2 on grid14's `int64` cells,
counting the `load` instructions in `@main`): in `untaken` one `load i64, ptr null` remains, moved into the branch
that reads it (`if.then0`, entered only when `argv.len > 100`), so the path run never reaches it; in `ignore`,
`copy`, `selfsub` and `selfcmp` no load remains in `@main` (nor in `ign`); in `deadadd` and in K's `cmp` one load
remains. F-051's dead load (`wild_dead_load_exit0`) has none at -O2, as here. So the -O2 leg sinks the load in one
face and deletes it in four. *My reading, not measured:* the read is gone because `ign`'s argument is unused, the
copy is dead, and `v - v` and `v != v` fold; the add's overflow check and the comparison keep theirs.

**The controls** (rule 5), each a case a wrong implementation gets wrong:
- `ctl_wild_used_cmp`, K's `cmp`: an implementation that deleted every load through a `wild` pointer at -O2 would
  answer 12 there; HUNT5 faults at both legs (107/107), and so do all 30 of grid14's K cells, at all five places and
  both types. Before landing 115 the baseline answers 12 at -O2. (12 is what `c3bdae2` measures: this control at 107/12,
  and grid14's nine `int64` K cells at `local`, `field` and `returned` at 107/12; this line said 13 until M15 (1b), M14v's
  finding F6.)
- `ctl_wild_dead_load`, the permitted reference: the dead load §27 allows (D-364), 107/0, the -O2 leg as in the faces.
- `ctl_wild_dead_add`, B's `deadadd`: the value is read only by an add whose result is never read, and the load
  stays (107/107), so HUNT5's -O2 leg does not drop every load whose value misses the exit; the faces are the forms
  whose read the optimiser can remove or move.

**Minimised** (M5 (b)) by `gen/minimize.py <hunt5> <cell> --want 0,107,0` on the five `int64` cells, 54 to 57 builds
each. It cut each failsafe to the six arms the compiler demands (`HeapBadRequest`, `HeapOom`, `Unreachable`,
`WildLeak`, `StackExhausted`, `MachineFault`, and `(*)`). In `ignore` it kept the body whole (the protected `exit r;`
needs the call), and `wild_load_to_ignoring_callee.npk` is its output, renamed. In the other four it deleted the
read too, which leaves F-051's dead load at the same verdict, 0/107/0: by exit codes alone a face cannot be told from
the permitted shape, which is the face itself. So those four reproducers keep the body whole, the read restored,
under the minimiser's failsafe; `wild_load_self_sub.npk` and `ctl_wild_dead_add.npk` also name `IntOverflow`, which
the compiler demands of their checked arithmetic (`REACH-002` otherwise, as the manager's `q06_selfcancel` and
`q04_deadcalc` show). `ctl_wild_dead_load.npk` is the minimiser's output for `copy`, renamed.

## Deduplication

- **F-051 / DEF-273** is the dead load: a load whose value nothing reads. Its programs never read `v`. Here the text
  reads `v` in each face; deleting that read is what turns a face into F-051's shape. DEF-273's registry row at HUNT5
  closes it by D-364: "a load whose value the program USES faults at both legs, a load through a `wild` NULL pointer
  whose value nothing uses is no read at -O2".
- **D-364 / S-140** permit "an UNUSED load through a `wild` NULL pointer and nothing else". Whether a value read only
  in a branch not taken, by a callee that ignores it, by a copy never read, or in `v - v` or `v != v`, is USED, the
  ruling and §27 do not say. Under the strict reading these faces are outside the permission.
- **`KNOWN_DEFECTS.md`**: DEF-251's row (i), fixed at 115, makes every load a memory operation to every pass; the row
  records F-051 and names no read load. The registry at HUNT5 has no entry for a read load sunk or deleted (searched
  for "sunk", "untaken", `v != v`, `v - v`, "dead load", "F-053").
- The compiler's `origin/main` at 07:57 EDT on 2026-10-25, fetched again before filing, is still HUNT5 `249eae9`.

## Measured, and inferred

- *Measured:* the verdicts above, grid14's ten cells at HUNT5 and the baseline, the loads left in each -O2 `@main`,
  and the minimiser's output.
- *Inferred, not measured:* under `null_pointer_is_valid` a load from address 0 is an ordinary load with no side
  effect, so the -O2 pipeline may move it to the only block that reads its value, or delete it once folding or
  inlining leaves its value unread, while the -O0 leg executes it in program order. That is one cause behind the two
  mechanisms, which is why the faces stay one finding, the brief's "sunk or deleted". Whether §27's sentence or the
  dereference's lowering is to change is for the compiler seat and the author to decide.
