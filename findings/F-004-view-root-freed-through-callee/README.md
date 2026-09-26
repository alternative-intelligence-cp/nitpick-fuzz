# F-004 — a view's root freed through a callee that moves the value out: `@x` and `$$i x` pass DEF-107's fix

**The shape.** While a view of a binding is live (`uint8[]:v =
string_bytes(x);`), `@x` or `$$i x` is handed to a callee that moves the
value out through its pointer: `func:at_fr = NIL(string->:p) { string:t =
move(<-p); … }`, where `t` drops at the callee's end. This compiles at HUNT2
`9126350`, which carries DEF-107's fix (1.6.1 step 0, `NITPICK-BORROW-015`).
The callee frees the viewed bytes, and the view reads the free poison
(**70/70**).

The same fix refuses `$$m x` to the same callee. It also refuses `@x` to a
callee that overwrites through the pointer, and a `move(x)` in place.

**Found by** a probe in M9's triage, not by a grid cell. The grid's `claim_i`
cells showed a write through a `$$i` claim accepted (F-008). The reference
admits a `$$i` claim while a view is live, so the combination was probed with
a view, and then with `@x`. The grid has no view place, which REPORT.md §10
lists among its gaps.

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc's rc / the -O0
exit / the -O2 exit.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `view_addr_to_freeing_callee.npk` | `uint8[]:v = string_bytes(x); drop at_fr(@x);`, then read `v[0i64]` | 0 / **70** / **70** | 0 / **70** / **70** |
| `view_claim_i_to_freeing_callee.npk` | the same with `drop at_fr($$i x);` | 0 / **70** / **70** | 0 / **70** / **70** |

## The controls

| control | what differs | expected at HUNT2 (the fix) | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_view_claim_m_to_freeing_callee.npk` | `$$m x` to the same freeing callee | refused `BORROW-015` | 1, `BORROW-015` | 0 / 70 / 70 |
| `ctl_view_addr_to_overwriting_callee.npk` | `@x` to a callee that does `(<-p) = raw nw();` | refused `BORROW-015` | 1, `BORROW-015` | 0 / 21 / 21 |
| `ctl_view_move_direct.npk` | `string:t = move(x);` while the view is live | refused `BORROW-015` | 1, `BORROW-015` | 0 / 0 / 0 |

So the fix exists and fires on three sibling spellings of the same freeing
write. What passes it is a callee whose write is a *move out* through its
pointer, reached by `@x` or by `$$i x`.

The baseline's 21 for the overwriting callee is F-005: the store through the
pointer never frees the old bytes, so the view keeps reading them.

## Deduplication

This is **DEF-107's shape**, a view's root written while the view is live.
`KNOWN_DEFECTS.md` says to deduplicate "any view-outlives-its-root cell"
against it, and at the baseline these programs are exactly DEF-107. But HUNT2
carries the fix (`2eea6f4`, 1.6.1 step 0). A cell of a fixed defect's shape
that is still anomalous is where the fix did not reach (`gen/dedup9.py`'s
rule, M5's). **It is a gap in DEF-107's fix, found at HUNT2**, and not a
regression: the baseline gives 70 for these spellings too.

The reference at HUNT2, MEMORY_REFERENCE §2.3 on D-325:

> every write-capable access of what it views refuses (`NITPICK-BORROW-015`):
> an assignment into it, `@root`/`$$m root` handed to a callee that writes
> through it, a pointer-receiver call, a move out of it, `list_push` on the
> viewed list. Reads, `$$i`, a disjoint field, a disjoint numeral range, **a
> callee that writes nothing through what it is handed**, and a pointer root's
> own reassignment stay.

- *Read, not measured:* a callee that moves the value out through its pointer
  stores the vacant value into the pointee and frees the old one. So it writes
  through what it is handed, and the first sentence covers the `@x` spelling.
- The `$$i` spelling is admitted by the second sentence. But a `$$i` claim does
  not stop its holder from writing (F-008), so admitting it lets the same free
  through.

## Measured, and inferred

- *Measured:* the verdicts above.
- *Inferred, not measured:* D-325's summaries read "what a call stores" off the
  callee's body. A `move(<-p)` stores the vacant value through `p`, and a store
  analysis that counts only assignments would miss it. That fits all five
  verdicts, but the compiler's source was not read to confirm it.
