# F-005 — a store through a pointer, `(<-p) = v`, never drops the old value: a leak

**The shape.** `(<-p) = v;` stores a new value into the owning place `p`
points to, and the old value is never freed. In a callee
`func:store = NIL(string->:p) { (<-p) = raw nw(); … }`, called as
`store(@x)` on a local `x`:
- `x` holds the new value, and its drop frees that.
- The 46-byte original is still live after every drop has run, and nothing
  owns it.

Each such store leaks the whole old value: a string's body, an array's
elements, a `List`'s buffer and elements. An `OwnedFd` store leaves the old
descriptor open.

The same assignment made directly (`x = raw nw();`), or to a field through a
pointer (`p.s = raw nw();`), frees the old value.

**Found by** the leak observer (M9.1). **121 cells** at HUNT2 `9126350` show
it, with the same live bytes at the baseline `c3bdae2`. Each is listed with
both compilers' verdicts in `CELLS.txt`:
- 105 are `at_overwrite`: `@x`, `$$m x` or `$$i x` handed to a callee that
  does `(<-p) = …`. 16 are `ptr_param × assign`: `(<-x) = …` in the callee.
- Every owning type: `string`, `Box`, `Nest`, `buffer`, `List<int64>`,
  `Wrap`, `List<string>`, `string[2]`, `Box[2]`, `string[3]`, `Box[3]`, and
  the generic `T` at `string`, `Box`, `List<string>` and `string[2]`.
- Every place that reaches such a store: a local, a `move` and a pointer
  parameter, a field, an element, a `for` over a range of an array or a
  `List`, a consuming `pick`'s binding, a `Self->` receiver, a lent `dyn`'s
  method, `$$m`, `$$i`, and the `Result` paths.

The live bytes are each type's original, measured: 46 (`string`, `Box`,
`Nest`, `buffer`), 8 (a `List<int64>`'s buffer), 70 (a `List<string>`'s 24-byte
buffer and its 46-byte element), 92 (`string[2]`, `Box[2]`), and 138 (the
`[3]`s). A loop place stores twice and leaks twice (92, 140, 16). The four
`pick_own` cells add F-006's leak (89 = 46 + 43, 137 = 70 + 67). The seven
`OwnedFd` cells exit **26**: a descriptor left open after every drop has run.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree).

- "live" is the leak observer's reading: `peak_live − 1 048 576`, after `run`
  returned and `main` allocated the 1 MiB probe. It is valid because
  `allocated − 1 048 576 < 1 048 576` on every line.
- The churn programs have no probe, so their `peak_live` is shown as printed.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `ptr_store_leak.npk` | `run`: `string:x = raw mk(); drop store(@x);` (store does `(<-p) = raw nw();`) | exit 0/0, **live 46** (`allocated=1048665 peak_live=1048622 count=3`) | the same |
| `minimized/m0009_str_local_at_overwrite_lk.npk` | the grid cell minimised with `--live 46` (62 builds, 30 lines) | exit 0/0, **live 46** | the same |
| `ptr_store_churn1000.npk` | the store once per call, 1 000 calls, no probe | exit 0/0, `allocated=89000` **`peak_live=46043`** `count=2000` | the same |
| `ptr_store_churn4000.npk` | 4 000 calls | exit 0/0, `allocated=356000` **`peak_live=184043`** `count=8000` | the same |
| `ptr_store_fd_left_open.npk` | the same store on an `OwnedFd`, then `main` counts the descriptors 3..15 still open | **26/26**: one left open | the same |

The churn's peak is 46 × N + 43: every call's original is still live when the
next call runs. That is the leak compounding, not a one-off at exit.

## The controls

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_local_assign_noleak.npk` | `x = raw nw();` on the local, no pointer | live 0 | exit 0/0, live **0** | live 0 |
| `ctl_field_store_through_ptr_noleak.npk` | `p.s = raw nw();` through a `Box->`: a FIELD target through a pointer | live 0 (D-186's field drop) | exit 0/0, live **0** | live 0 |

Both use the same helper values and the same probe. So the observer reads 0
where the old value is dropped, and a store through a pointer to a field does
drop it. Only the whole pointee, stored through `<-`, is left undropped.

## Deduplication

`KNOWN_DEFECTS.md` has no leak of a stored-over value.
- DEF-102's `ctl_whole_lent_string` (a whole assignment to a loan) leaked the
  NEW value (43 bytes, measured at the baseline in this grid's `lent_param ×
  assign` cells). HUNT2 refuses it `TYPE-085`. This finding leaks the OLD
  value, through a pointer to an OWNED place, and HUNT2 accepts it.
- D-186 (the compiler's decision, "overwriting an owning field or managed
  element drops the old value") names field and element targets. It exempts
  "a `wild` pointee" and "an element reached through a pointer base". A
  managed pointee stored whole through `<-` is named nowhere. D-186's own
  soundness argument, that the target is always live, holds for it: the
  pointee of a `T->` to an owned place is that place.

**Present at both compilers, with identical live bytes: an old defect, not a
regression.**

## Measured, and inferred

- *Measured:* the verdicts above, and the grid's 121 cells.
- *Inferred, not measured:* D-186 added the drop-before-store for field and
  element targets, and the whole-pointee store `(<-p) = v` was not given it. A
  leak is not a memory fault. But the language has no garbage collector
  (MEMORY_REFERENCE §1, D-003), so every such store's old value is lost for the
  process's lifetime. For an `OwnedFd` the loss is a descriptor, and a program
  looping on it reaches the descriptor limit.
