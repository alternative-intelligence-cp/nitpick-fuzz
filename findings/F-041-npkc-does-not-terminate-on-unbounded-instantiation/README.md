# F-041 — npkc does not terminate on an unbounded generic instantiation

**The shape.** TRAITS_REFERENCE:586: "Instantiation depth is capped at **64**; exceeding it is
a compile error with the instantiation stack printed, never a silent truncation." A
generic function that instantiates itself at a larger type each time never reaches that
error. npkc runs on, growing, and prints nothing:
```
struct:Box<T> = { T:v; };
func:deep<T> = int32(move T:x) never fails {
    Box<T>:b = Box{ v: move(x) };
    pass (raw deep::<Box<T>>(move(b)));     // deep<int32> → deep<Box<int32>> → …
};
... raw deep::<int32>(raw v32(1i32)) ...
```
Measured by hand, at HUNT2 `9126350`, the baseline `c3bdae2` and `93bcb66`: no exit within
300 s, maximum resident set 4.4 GB (4 591 800 KB at HUNT2), no output. The commands were
`timeout 300` under `ulimit -v 8000000` and `/usr/bin/time`. M11's claim `tr0586` and
the programs here meet the runners' 120 s compile timeout instead.

A compiler that never returns is CLAUDE.md's lower-priority report ("the compiler
crashing"), and arguably worse than a trap: a build that hangs is not even a refusal.
The memory growth means a build machine can be driven into its OOM killer. This one has
earlyoom, which was not reached at 4.4 GB under the 8 GB cap.

Found by M11's TRAITS claim `tr0586`. Its program first used a generic struct literal
spelling of its own (`Box<T>{ … }`, PARSE-002), and agreed in run 1 for that reason. Once
re-spelled, it timed out (S45, S55).

## The programs

| program | the reference's answer | measured |
|---|---|---|
| `h1_unbounded_instantiation` | npkc 1, the instantiation stack printed | no exit (the runner's timeout) |
| `ctl_h2_bounded_nesting` (the control: the same generic over a fixed nesting, three deep) | npkc 0, exits 0 | npkc 0, 0 / 0 |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`, by `gen/run_findings.py`)

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | newest `main` `93bcb66` |
|---|---|---|---|
| `h1_unbounded_instantiation` | npkc **T** (no exit in 120 s), both runs | T | T |
| `ctl_h2_bounded_nesting` | npkc 0, 0 / 0 | npkc 0, then `llc` and `opt` refuse its IR | npkc 0, 0 / 0 |

At the baseline the control's nested generic emits IR that `llc` refuses. That is an older
defect, fixed by HUNT2, and not this finding.

## Deduplication

- KNOWN_DEFECTS.md has no instantiation-depth entry.
- The registry at `93bcb66` has none.
- F-024's npkc traps exit 3. This shape never exits.

## Measured, and inferred

- **Measured:** no exit in 300 s and the maximum resident set, at three compilers, by
  hand; the runners' timeouts.
- **Reasoned, not measured:** that the instantiation walk has no depth counter, or one
  that is not consulted on this path. Whether it would finish given unbounded memory and
  time was not tried.
