# F-043 — TRAITS_REFERENCE: thirteen claims the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over TRAITS_REFERENCE (all 766 lines) at HUNT2: 119 claims, 115 tested, 99
agree, 16 disagree. The 16:
- thirteen documentation rows (below);
- [F-041](../F-041-npkc-does-not-terminate-on-unbounded-instantiation/), npkc does not
  terminate on an unbounded instantiation (`tr0586`);
- one lower-priority compiler row, [F-042](../F-042-traits-lower-priority-compiler-rows/):
  `opaque` outside an extern block;
- one not a finding (`tr0350`): "a blanket impl does not apply to itself" says its bound is
  not met by itself, not that `impl:<T: Loggable>:T:Loggable` is refused, which is what the
  program expected.

The rows, with each claim's program and its verdicts at HUNT2, the baseline and `93bcb66`,
are in [`ROWS.md`](ROWS.md). All thirteen give the same result at HUNT2 and `93bcb66`. At
the baseline two compiled (`tr0404`, `tr0435`): decisions after it retired those examples.

- **Examples that no longer compile.**
  - Serializable (TRAITS:21) passes `result` from a body: `result` is the
    `ensures`-only keyword since D-221 (TYPE-060).
  - Iterator (:97) declares a trait the prelude owns (RESOLVE-001).
  - `assoc:Error = string;` (:109) names the compiler's `Error` (D-179, D-239).
  - The inherent impl (:124) casts with `flt64(…)` (PARSE-002; the casts are `=>` and
    `=>!`).
  - `l.push(v)` (:149): `List<T>` has no `push` (TYPE-019).
  - The storage_driver block (:373) is EXTERN-001.
  - The opaque-copy example (:384) names `Handle`, a builtin type keyword, and a
    `handle_create` that does not exist, so OPAQUE-COPY-001 is never reached.
  - `extract_value` (:404) passes a lent `T` out (TYPE-047; D-065, D-264).
  - `item.render();` (:419) is a bare statement that discards a `Result` (TYPE-039).
  - The value-parameter example (:435) declares `struct:Mutex`, a builtin name.
  - The arena example (:602) calls `alloc(my_node)`: an arena's `alloc` takes no
    arguments.
- **The field visibility sentence** (:364): "Struct fields follow module visibility —
  private by default, exported with `pub`".
  - A plain field is read outside its module, so fields are not private by default.
  - `pub` on a field does not parse (PARSE-001). This was measured by run 2's program,
    which wrote one; it was then re-spelled (S55).
  - The field qualifiers are D-313/D-314's `sealed` and `hidden` (LEXICAL's `lx0091` …
    `lx0093` agree).
- **"Lambdas without capture remain as function values"** (:764–765): there is no lambda
  expression (PARSE-002). AST:476 says closures are removed and function values are named
  functions.

**Agreements worth naming.**
- The struck spellings are refused: `trait:X { … }`, `impl X for Y`, `impl:T:for:U`,
  `impl:Loggable:for:T:where:…`, `func<T>:f`, `opaque:Name;`, `@derive`, `@cast<T>`,
  `dyn A + B`.
- The contract rule (TYPE-041) and transitive supertraits (TYPE-014).
- The trait name as a namespace:
  - `Speaks.say(l)` works;
  - an unimplemented one is refused;
  - an ambiguous `p.tag()` is TYPE-020, and `Ta.tag(s)` disambiguates.
- The seven derives:
  - each method's name and return type;
  - `Ord` in declaration order;
  - DERIVE-002 for `Default`/`Display`, DERIVE-005 and DERIVE-006 naming the field;
  - TYPE-017 at the call, re-homed with no `<derived-N>` path.
- The prelude's scalar impls:
  - `cmp`, `eq`, `partial_cmp` NIL for nan, string's byte order;
  - TbbErr on an ERR `eq`;
  - TYPE-013 for `impl:int32:Ord`, while `impl:bool:Ord` is admitted.
- Blanket impls: one per trait; a concrete impl first; a trait is required.
- Value parameters' four rules.
- The generic-body rules:
  - TYPE-046 for a copy of `T`;
  - the bound named in a refusal;
  - closed bound sets;
  - no UFCS through a parameter.
- Coherence, every row of the table, with the note at the earlier impl.
- Object safety, all four rules and the associated-type rule (TYPE-015).
- `dyn`:
  - 16 bytes, and (N+1)×8 for N traits;
  - widening;
  - no supertrait method through a `dyn`;
  - the bare trait as a value type refused (TYPE-002).

**Found in runs 1 and 2, not findings.** These were the programs' own mistakes:
- A generic struct literal takes no type arguments: `Box{ … }`, not `Box<int32>{ … }`.
  This affected 10 programs, three of which had agreed for that reason.
- `pub` on a field (`tr0364`) and an impl whose generic method's signature was refused
  (`tr0686`) had both agreed for their own reasons (S55).

## Deduplication

- None of these sentences is among F-028's rows (DEF-154), which cover no TRAITS line.
- The lambda row repeats, in TRAITS' words, AST's `as0476`, which agreed with AST's
  sentence.
- The registry at `93bcb66` has no entry for any of the thirteen.

## Measured, and inferred

- **Measured:** each row's result at three compilers.
- **Reasoned, not measured:** that the compiler is the right side in each.
