# F-051 — a dead load through a `wild` NULL pointer faults at -O0 and is deleted at -O2: the legs disagree under DEF-251 (i) (scope wild)

**Reported apart, as the check of DEF-251 (i)** (the M13 brief's §5 and §9). The programs contain `wild`,
which `CLAUDE.md`'s defect definition excludes, so this is not a defect by that definition and takes no
class from §9's table. It is a measurement against (i)'s own promise, which the registry states as "both
legs fault".

**The shape.** `wild int64->:p = NULL; int64:v = <-p;`, where `v` is never read, then `if (p == NULL) {
exit 14i32; }`. The -O0 leg executes the load and faults (`MachineFault`, 107). The -O2 leg deletes the
unused load and takes the null branch (14). Without the test the -O2 leg exits 0, a reported success where
-O0 faults. A struct load behaves the same.

**What (i) says.** Landing 115 (DEF-251 (i)) puts LLVM's `null_pointer_is_valid` on every emitted `define`.
The registry row at HUNT4: "a store to or a load from `null` is a memory operation to every pass, nothing is
inferred from a dereference, both legs fault and the fault is D-307's `MachineFault`". TYPE_REFERENCE §27 at
HUNT4: "A store through or a load from a `NULL` pointer (a `wild` one, since landing 119) is a hardware fault
that reaches `failsafe` as `MachineFault` (D-307) at BOTH legs".

**Found by** grid13 (M13): section B, the `wild` local × the unused load before a `NULL` test, `g0249`
(int64) and `g0250` (struct), 107/14 at the baseline, HUNT3 and HUNT4 (`DEFECT:leg_mismatch`, scope wild).
The brief's P6 named it: "A deleted dead load answering 14 at -O2 is a `leg_mismatch` against (i)."

## Verdicts

Measured on 2026-10-21 by PLAN.md's recipe through `gen/run_findings.py`: at HUNT4 `c72639f` twice and the
baseline once under LLVM 20.1.8 (`VERDICTS.txt`; the HUNT4 runs agree), and at HUNT3 `0c0f5a3` twice and the
baseline once (`VERDICTS-0c0f5a3.txt`). The baseline under its own LLVM 20.1.2, by `gen/snip.py`, gives the
same verdicts.

| program | HUNT4 `c72639f`, runs 1 and 2 | HUNT3 `0c0f5a3` | baseline `c3bdae2` |
|---|---|---|---|
| `wild_dead_load.npk`, the shape above (minimised by `gen/minimize.py`, keeping 0/107/14) | 0 / 107 / 14 | 0 / 107 / 14 | 0 / 107 / 14 |
| `wild_dead_load_exit0.npk`, the same load with no test after it | 0 / 107 / 0 | 0 / 107 / 0 | 0 / 107 / 0 |
| `wild_dead_struct_load.npk`, a struct loaded and not read, then the test | 0 / 107 / 14 | 0 / 107 / 14 | 0 / 107 / 14 |
| control `ctl_wild_used_load.npk`, the loaded value read (`if (v == 0i64) { exit 13i32; }`) | 0 / 107 / 107 | 0 / 107 / 12 | 0 / 107 / 12 |

**The control** (rule 5) is the one an implementation without (i) gets wrong: before landing 115 the -O2
leg reads the load as undefined and answers 12; under (i) a live load faults on both legs. So (i) holds for
a load whose value is used and not for one whose value is not.

## Deduplication

- `KNOWN_DEFECTS.md`: DEF-251 is this class. Its registry row at HUNT4 records (i) as fixed at 115 and (ii)
  as fixed at 119. It lists one broader face as inferred and unmeasured, "a `p == NULL` test AFTER a
  dereference may be folded away at -O2". Under (i) that is not what happens here: the test stands and
  answers 14; it is the load that is deleted. The row does not name a dead load.
- M13 measured the inferred face itself for plain pointers at HUNT3 and the baseline: a struct reached through
  a parameter or a helper's return, loaded and not read, gives 107/0 (the test folded away; grid13's `g0224`,
  `g0237`). At HUNT4 those programs are refused `TYPE-096` (D-355 (ii)), so in safe code the face is gone.
- The registry at HUNT4 has no entry naming a dead `wild` load. The compiler's `main` at 05:05 EDT on
  2026-10-21 was still HUNT4.

## Measured, and inferred

- *Measured:* the verdicts above, and grid13's `g0249`/`g0250` at the three compilers.
- *Inferred, not measured:* under `null_pointer_is_valid` a load from address 0 is an ordinary load, and an
  ordinary load whose value is unused is dead code that the -O2 pipeline may delete, while the -O0 leg
  executes it. Since landing 119 a plain pointer cannot hold `NULL`, so the face is confined to `wild` code,
  where a dereference is the author's responsibility under the TOS. Whether (i)'s sentence or the
  dereference's lowering is to change is the compiler seat's call.
