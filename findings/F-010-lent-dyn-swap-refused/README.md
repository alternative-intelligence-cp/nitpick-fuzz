# F-010 — a swap through a lent `dyn`'s method is refused `BORROW-002` at HUNT2 and accepted at the baseline

**Lower priority** (a refusal of what the reference admits). This is not a
memory fault. It is **new between the two compilers**: 8.5's rule counts a
cell that was clean and is now refused as a regression until shown otherwise.

**The shape.** A lent `dyn` parameter's method (a `Self->` receiver) swaps its
owning field with an owned local:

```
func:op = NIL(DHold->:self) never fails {
    string:other = raw nw();
    string:tmp = move(self.v);
    self.v = move(other);
    other = move(tmp);
    pass NIL;
};
```

It is called through `func:callit = NIL(dyn Tr:d) { drop d.op(); … }`.
- At HUNT2 `9126350` the call is refused `NITPICK-BORROW-002`: "a view of this
  frame's storage is stored by this call into the cell of a `dyn` this frame
  was lent (D-004 rule 3, D-325 …)".
- At the baseline `c3bdae2` it compiles, and the caller reads the new value
  (22).
- Nothing in the swap is a view. `other` and `tmp` are owning strings moved
  whole, and after the swap the cell holds `other`'s original heap string.

MEMORY_REFERENCE §2.3 (D-325, DEF-115): "a LENT `dyn`'s cell is the caller's
(the one owning-by-cell kind a loan may write, through its methods), so a
BORROW stored into it refuses at the call (`BORROW-002`)". A moved owning
value is not a borrow.

**Found by** the grid's `dyn_recv × swap` cells: 12 cells, `string`, `Box`
and `List<string>` × 4 observers. At the baseline all 12 run clean, the leak
observer reading 0 live. At HUNT2 all 12 are refused `BORROW-002`.

## Verdicts

Measured on 2026-09-26, by PLAN.md's recipe through `gen/run_findings.py
--heap`: at HUNT2 twice and at the baseline once (`VERDICTS.txt`; the HUNT2
runs agree).

| program | what the method does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `lent_dyn_swap.npk` | the swap above | **1, `BORROW-002`** | 0 / 22 / 22 |
| control `ctl_lent_dyn_store_call.npk` | `self.v = raw nw();` | 0 / 22 / 22 | 0 / 22 / 22 |
| control `ctl_lent_dyn_store_moved_local.npk` | `string:other = raw nw(); self.v = move(other);` | 0 / 22 / 22 | 0 / 22 / 22 |

So storing a call's result, and storing a moved local, into the lent cell are
both accepted at HUNT2. Only the swap is refused, which also moves the old
field out into the frame (`tmp`, then `other`).

## Deduplication

`KNOWN_DEFECTS.md` has no over-restriction. The refusal is DEF-115's rule
(1.6.1 step 0, in HUNT2 and not in the baseline) firing where no borrow
exists. **New at HUNT2: an acceptance regression of DEF-115's fix.**

## Measured, and inferred

- *Measured:* the verdicts above, and the 12 cells.
- *Inferred, not measured:* the provenance summary of `op` records that
  `self.v`'s old value flows into a local of the frame (`tmp`, then `other`).
  It then treats the local stored back into the cell as carrying the frame's
  provenance, though it holds an owned heap value, not a view of the frame.
