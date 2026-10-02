# F-033 — MODULE_REFERENCE: seven claims the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over MODULE_REFERENCE (all 300 lines) at HUNT2: 139 claims, 124 tested, 109
agree, 15 disagree. The 15:
- seven documentation rows (below);
- five lower-priority compiler rows, [F-034](../F-034-module-lower-priority-compiler-rows/);
- one known: DEF-153 (F-027 c), a string literal in `cstring` position (`md0296b`). It
  compiles at `93bcb66`;
- two that are not findings:
  - `md0122`: the refusal says "`helper` is a function, not a module" where the
    sentence says "is not a module";
  - `md0185`: the IR for two import orders holds the same lines, and only one function's
    position follows the import order. The script demanded a byte-identical file.

The rows, with each claim's program and its verdicts at HUNT2, the baseline and the
newest `main` `93bcb66`, are in [`ROWS.md`](ROWS.md). All seven give the same result at
all three.

- **A spelling the language no longer has.** `pub const int32:MAX = 100i32;` (MODULE:212,
  in §3's example at 209) does not parse: PARSE-001, "expected `:`, found `int32`". A
  module constant is `fixed` (`pub fixed int32:MAX`), as the compiler's own module programs
  write it. The rest of §3's example compiles once that line is set aside.
- **The driver interface describes more than lowers.**
  - The `cuda_driver` example (MODULE:241) is EXTERN-001. Its `opaque struct` "is reserved
    for the LOAD_MODULE work and does not lower yet (D-190)". Its methods also take no
    `Bridge->` first and no `Duration` last, which the stub generator requires. In that
    form (the compiler's own `extern_stub.npk`), `md0250` and `md0259` compile.
  - "Fixed-width scalars, POD structs of them, sized byte payloads, and typed handles"
    (MODULE:270): a method's parameters are "`int32`, `int64`, `int8[]` or `uint8[]` in
    the v1 wire vocabulary (D-190)". A POD struct, an `int16` and a typed handle are each
    EXTERN-001. The byte payloads are admitted, and then their stub fails (F-034 a).
  - The example at MODULE:289 is TYPE-042: `int32:n = raw some_query(name);` and
    `int32:x = _! some_query(name);`.
    - `raw` needs a `never fails` callee (D-163), and the checker reads `_!` as `raw`.
    - A driver method returns `Result<T>` (MODULE:259; its claim agrees).
    - A driver method can never be `never fails`: MODULE:263–266 says the contract is
      refused naming D-149, and its claim agrees (EXTERN-002).
    - The program stands in an ordinary fallible function for the driver method, which
      line 259 says a driver method's call is like.

**Agreements worth naming.**
- **The header (D-248).** RESOLVE-012 for:
  - a file with no header;
  - a header naming a sibling that exists;
  - a `network/mod.npk` headed `mod:mod;`;
  - a file with no declarations.
- **The entry points.** RESOLVE-013 for `main` and for `failsafe`, each in an imported module
  and in an inline module.
- **Imports (D-274, D-276).**
  - A member-less `mod:network;` loads `network.npk` or `network/mod.npk`, relative to the
    declaring file, and its symbol carries the file's scope.
  - A `pub mod:` is re-exported with its scope.
  - A `use`, a `pub use` and a `mod:` written inside an inline module bind into it, and an
    inline module is sealed from its file's imports.
  - `use` is not transitive, and a `pub use` re-exports in either order.
  - Order never matters, and a `use` cycle of two or of three modules is legal.
- **Visibility (D-273).** RESOLVE-003 for a private member from every spelling:
  - qualified;
  - a binding;
  - a hop through a private nested module;
  - `use nested.internal;`;
  - a file's private symbol.

  The message says "is private to".
- **The error arms (D-275).**
  - A constant two inline modules deep is the file's identity.
  - `(m.Name)`, `(file.Nosuch)`, `(nosuch.Name)` and `(x.DivByZero)` are RESOLVE-002, in
    `failsafe` and in an ordinary `pick`.
  - A literal, a global, a range and a three-segment arm are TYPE-007.
- **Builtin names (D-294, D-296).** RESOLVE-001 for:
  - a module-level function named `mono_now`;
  - an `extern` method so named;
  - a callable parameter so named;
  - a callable local so named.

  A method of that name is accepted, and so is a plain local.

**Found in runs 1 and 2, not findings.** These were the programs' own mistakes, fixed
by `refix()`, with every expectation unchanged:
- `hidden` is a reserved word: 14 programs. One of them had agreed for that reason
  (`md0099b`, S55).
- `nbridge.npk` imports `nsys.npk`, which the scripts did not copy: 9 scripts. One of
  them had agreed for that reason (`md0273`).
- REACH-002 asks `failsafe` to name every error constant that can reach it: 8 programs.
  This covers `nbridge.npk`'s ten constants, and `md0080b.Boom`, which `classify`
  handles.

## Deduplication

None of these sentences is among F-028's rows (DEF-154), which cover no MODULE line.
None is among F-029 … F-032 (O-N35). The registry at `93bcb66` has no entry for any of
the seven.

## Measured, and inferred

- **Measured:** each row's result at three compilers.
- **Reasoned, not measured:** that the compiler is the right side in each. For the
  driver rows, D-190's v1 vocabulary is the compiler's stated stage, and the reference
  describes the whole design.
