# F-007 — `to_cstring`'s buffer is never freed: every conversion leaks `len + 1` bytes

**The shape.** `cstring:dn = to_cstring("/dev/null") ?! E9;` in a function
that returns: the 10-byte buffer the conversion allocated is never freed.
Called N times, the program holds 10 × N bytes. A successful `exit 0`
reports nothing.

**Found by** a probe while learning the syntax for the grid's `OwnedFd` type
(M9.3). `open` takes a `cstring`, and the leak observer's calibration probes
showed the conversions accumulating. The grid does not cross `cstring`, and
its `OwnedFd` cells make one conversion per descriptor. That is why the
`OwnedFd` cells are judged by the descriptors left open, not by the heap
reading (`gen/grid9.py`).

## Verdicts

Measured on 2026-09-26 on the cloud VM, by PLAN.md's recipe through
`gen/run_findings.py --heap`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). No probe is allocated: `peak_live` is
the line as printed.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `cstr_churn1000.npk` | `conv()` converts `"/dev/null"` and returns its `len`; called 1 000 times | exit 0/0, `allocated=10000` **`peak_live=10000`** `count=1000` | the same |
| `cstr_churn4000.npk` | 4 000 calls | exit 0/0, `allocated=40000` **`peak_live=40000`** `count=4000` | the same |

`peak_live` equals `allocated`, so no conversion's buffer was ever freed.

## The control

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_str4000.npk` | `conv()` makes an owning `string` of the same length with `string_concat("/dev/nul", "l")`, 4 000 calls. The substitution was asserted to match once. | the peak one string's body | exit 0/0, `allocated=36000` **`peak_live=9`** | the same |

## Deduplication

`KNOWN_DEFECTS.md` has no leak of a floor primitive. The compiler's own
history has two siblings, both fixed in both compilers:
- DEF-25: `string_concat` of two empties allocated a block its cap-0 result
  never freed.
- DEF-51: `read_file` and `read_stdin` leaked the buffers they outgrew.

This is a third primitive. **Present at both compilers, identically: an old
defect.**

## Measured, and inferred

- *Measured:* the verdicts above.
- *Read, not measured* (at both compilers' `runtime/npkrt.ll`):
  `npk_to_cstring` allocates its `len + 1` bytes through
  `npk_alloc_internal`, the managed internal entry. D-151's exit check does
  not count that entry. `cstring` is `{ptr, len}`, with no `cap`, and no drop
  frees it.
- **The reference disagrees with itself here.**
  - TYPE_REFERENCE §3.2.1 types the buffer `wild char8->`. CONTROL_REFERENCE
    §4.6 says a successful `exit` with live `wild` memory traps
    (`WildLeak`), and MEMORY_REFERENCE §1.3 says a `wild` pointer must be
    freed manually.
  - A program cannot free a `cstring`'s buffer without `wild`, and the
    measured exit is 0 with 40 000 bytes live.
  - So either the buffer is managed and should be dropped (a missing drop),
    or it is `wild` and should trap at `exit 0` (a missing check). Either way
    the program's memory is not what the reference says.
