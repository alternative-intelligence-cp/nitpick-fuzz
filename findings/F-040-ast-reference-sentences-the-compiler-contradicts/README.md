# F-040 — AST_REFERENCE: eighteen claims the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over AST_REFERENCE (all 644 lines) at HUNT2: 202 claims, 181 tested, 151
agree, 30 disagree. The 30:
- eighteen documentation rows (below);
- [F-037](../F-037-dyn-cast-reads-freed-memory/), a use after free through a `=> dyn`
  cast (`as0453`);
- [F-038](../F-038-npkc-traps-on-give-or-fall-outside-a-pick/), npkc traps on
  `give`/`fall` outside a pick (`as0202`, `as0203`, `as0267`);
- five lower-priority compiler rows, [F-039](../F-039-ast-lower-priority-compiler-rows/);
- one not a finding (`as0365`): AST:365's `Point_magnitude(p)` is the lowering of an inherent
  method (TRAITS:132), and the program had declared a free function of that name. UFCS itself
  holds: `p.magnitude()` reaches a free `magnitude(p)` (measured by hand);
- two known: DEF-131's `<=>` (`as0295b`) and DEF-153's `cstring` literal (`as0492`), both
  of which compile at `93bcb66`.

AST_REFERENCE describes the parser's nodes, and its notes carry spellings that later
decisions changed. The rows, with each claim's program and its verdicts at HUNT2, the
baseline and `93bcb66`, are in [`ROWS.md`](ROWS.md). All eighteen give the same result at
all three.

- **Spellings retired by a later decision.**
  - `pub const int32:MAX = 100i32;` (AST:44) and the `const` local qualifier (AST:499):
    PARSE-001. AST:505 itself says `const` retired at 1.4.2c.
  - `FFhex` as a literal (AST:281): an identifier since D-147.
  - `++` / `--` (AST:297): removed (D-174).
  - The bare `?` fallback (AST:413): PARSE-011 (D-175).
  - `?|` "struck (D-167)" (AST:416): it is THE fallback that D-175 names. Every program
    uses it.
  - `ok(val)` among the bare-name builtins (AST:385): removed, as AST:329 says.
  - `vec3(…)` (AST:450): a library type since D-135.
- **D-179 changed the error model under the AST's notes.**
  - `failsafe` takes one `Error` (TYPE-044), not `tbb32:err` (AST:93).
  - `?!`'s argument is an `Error` constant, not a `tbb32` (AST:415).
  - A `Result` literal's `err` is an `Error`. `Result{ value: 5i32, err: 0i32 }` is
    TYPE-007 (AST:195, :307).
  - A success literal omits `err`, as TYPE:1330 writes it; measured by hand,
    `return Result{ value: 5i32 };` returns 5. That is against AST:333's "exactly `value`
    and `error`".
- **The extern rows describe the D-002 era** (D-149 removed the contracts):
  - an extern method needs no failure contract (AST:128);
  - `never fails` on one is EXTERN-002 (AST:137).
- **Other notes.**
  - Implicit generic arguments `f<int32>(x)` (AST:364): the turbofish is required
    (LEXICAL:239, D-064).
  - A bare-name builtin need not return `Result<T>` (AST:403): `string_byte_length`
    returns `int64`.
  - A cast to a `wild` target is `=>!`, D-019's one door. `p => wild int8->` (AST:437)
    is BORROW-011, even from argv's pointer, which is no borrow; `=>!` compiles
    (measured by hand at HUNT2 and `93bcb66`).
  - The example `unit:Hertz = 1 / Seconds;` (AST:45) is RESOLVE-001, since the prelude
    declares `Hertz`. `unit:PerSec = 1 / Seconds;` compiles (measured by hand).

**Agreements worth naming.**
- The entry points' fixed shapes: TYPE-083 three ways and TYPE-044.
- `_~` discarded parameters, which cannot be read.
- The statement placement rules:
  - `exit` only in `main`/`failsafe`;
  - `relay` not in them;
  - `$` only in `loop`/`till`;
  - `await` only in `async`.
- The loop rules:
  - `for`, `loop` and `till` refuse `decreases`;
  - a counted step must be positive;
  - no `end` on `loop`/`till`;
  - `when`'s `then`/`end`, `break` lowering to `then`;
  - the clause order before `invariant`.
- `defer`: no defer on a trap; relay's defer runs; `?!` runs none.
- The verification nodes: `old`, `result`, `decreases` over a recursive group,
  invariants, and `limit` on a parameter.
- Pick patterns: value, range, struct destructure, `ERR:`, `(!)` removed,
  `#unreachable()`.
- Types:
  - thin pointers;
  - arrays as values that do not decay;
  - function types and the `never fails` slot;
  - `any` only under `->`;
  - `Self` only in traits;
  - `int32[COUNT]`.

**Found in runs 1 and 2, not findings.** These were the programs' own mistakes:
- a `$$m` claim live at the read (BORROW-013);
- `move(mk())` refused for the call's `Result` rather than for its operand (S55).

## Deduplication

- None of these sentences is among F-028's rows (DEF-154), which cover no AST line.
- Several repeat, in AST's own words, a spelling another reference's row already
  records: `pub const` (MODULE's F-033), `++`/`--` (LEXICAL's F-035), the bare `?`
  (OP's F-031). Each is AST's own sentence, so it is AST's row.
- The registry at `93bcb66` has no entry for any of the eighteen.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and the hand runs named.
- **Reasoned, not measured:** that the compiler is the right side in each. The decisions
  named (D-147, D-149, D-174, D-175, D-179, D-190, D-019, D-064, D-135) say so.
