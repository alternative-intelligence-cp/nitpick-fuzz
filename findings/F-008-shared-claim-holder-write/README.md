# F-008 — a write through a `$$i` claim's holder compiles, where the reference names it `BORROW-013`

**The shape.** `string->:p = $$i x; (<-p) = raw nw();` compiles, and the write
lands: `x` reads the new value (22). The same holds when the `$$i` claim is a
call's argument and the callee writes through it (`drop store($$i x);`).

The reference's conflict table lists "a write through a shared claim's
holder" among the static conflicts that are `NITPICK-BORROW-013`:
- VERIFICATION_REFERENCE's aliasing paragraph (line 215 at HUNT2);
- D-286 (4);
- the compiler's guide: "a write under `$$i` … and a write through a shared
  holder are BORROW-013".

The table's other `$$i` clause fires. A write to the ROOT while the `$$i`
claim is live is refused `BORROW-013`.

**Found by** the grid's `claim_i` place (M9 section C). It expected REFUSE
`BORROW-013` for every write-capable operation handed a `$$i` claim, and **40
cells** are accepted instead at HUNT2 `9126350`, and at the baseline
`c3bdae2`:
- `at_overwrite`, `at_free` and `at_grow` at `string`, `Box`, `List<int64>`
  and `List<string>`;
- in the read-after cells, the writes are visible (22 after an overwrite, 23
  after a move out);
- the four `at_overwrite` leak cells are F-005.

They are listed in `CELLS.txt`. The grid's first reading was that `$$i`'s
"excludes writers" speaks only of overlapping accesses. The reference's table,
read in triage, names the holder's own write too, which makes this a finding
(PROGRESS.md M9).

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc's rc / the -O0
exit / the -O2 exit.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `claim_i_holder_write.npk` | `string->:p = $$i x; (<-p) = raw nw();`, then read `x` | **0** / 22 / 22 | 0 / 22 / 22 |
| `claim_i_argument_write.npk` | `drop store($$i x);`, where `store` does `(<-p) = raw nw();` | **0** / 22 / 22 | 0 / 22 / 22 |

## The controls

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_claim_i_root_write.npk` | `string->:p = $$i x; x = raw nw();`: a write to the root while the `$$i` claim is live | refused `BORROW-013` (the table's "a write-capable access under `$$i`") | 1, `BORROW-013` | 1, `BORROW-013` |
| `ctl_claim_m_holder_write.npk` | a `$$m` claim's holder writes and reads through the holder | 0 / 22 / 22: an exclusive holder may write | 0 / 22 / 22 | 0 / 22 / 22 |

So the table is implemented for the root's write under `$$i`. The same program
with an exclusive claim is legal and runs as expected. What passes is the
holder's own write through a shared claim.

## Why it matters, measured

A `$$i` claim is what the view rule admits while a view is live
(MEMORY_REFERENCE §2.3: "Reads, `$$i`, … stay"). A `$$i` claim handed to a
callee that frees through it therefore frees a live view's bytes at HUNT2:
F-004's `view_claim_i_to_freeing_callee` reads the poison, 70/70. An
unenforced holder rule is thus a way past DEF-107's fix.

## Deduplication

`KNOWN_DEFECTS.md` has no claim shape. D-286 is the compiler's aliasing
decision (1.5.5), in both compilers. **Present at both, identically: an old
defect.**

## Measured, and inferred

- *Measured:* the verdicts above, and the grid's 40 cells.
- *Inferred, not measured:* the conflict table is applied to accesses spelled
  on the claimed ROOT, and a write through the holder, `(<-p) = …`, is not
  classified as an access of `x`. MEMORY_REFERENCE §2.3 notes that
  "exclusivity is decided among accesses that spell the SAME ROOT".
