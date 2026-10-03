# F-044 — TYPE_REFERENCE 661–2122: sentences the compiler contradicts, where the compiler is right or at least safe (documentation findings)

M11's claims over TYPE_REFERENCE 661–2122 at HUNT2 `9126350`. Session 9 takes the range in
three parts, each to its own clean point (PROGRESS.md S65). This finding grows with each
part.

| part | lines | claims | tested | agree | disagree | here |
|---|---|---|---|---|---|---|
| A | 661–1176 (§6–9) | 268 | 249 | 240 | 9 | 8 rows |
| B | 1177–1592 (§10–18) | 129 | 123 | 114 | 9 | 9 rows |
| C | 1593–2122 (§19–28) | 178 | 172 | 149 | 23 | 16 rows |

Part A's nine disagreements are:
- eight documentation rows (below);
- one not a finding (`ty1084`): its regex demanded a word boundary after `}`, which
  cannot match there. Compiled by hand, the slice parameter is `{ ptr, i64 }`, as claimed.

The rows, with each claim's program and its verdicts at HUNT2, the baseline `c3bdae2` and
`93bcb66`, are in [`ROWS.md`](ROWS.md). All thirty-three give the same result at all three.

## Part A (§6–9)

- **The tbb table's alignments** (:673–674). §6 gives `tbb128` and `tbb256` alignment 8.
  - Both align to 16: `{int8, tbb128}` is 32 bytes, and `{int8, tbb256}` is 48. The plain
    `int128` and `int256` measure the same, by hand at HUNT2.
  - TYPE §5 says 16 for the same two types, at its rows 460–461 and its line 469. Their
    claims `ty0460`, `ty0461` and `ty0469` agree.
  - So the reference contradicts itself, and the compiler follows §5.
- **"Used for … the `failsafe` signature"** (:715). `failsafe` takes exactly one `Error` and
  returns `int32` (D-179, TYPE-044). A failsafe over a `tbb32` is refused.
- **"`tryte:t = 42;` and `tryte:t = 1T1T0t;` are one value spelled two ways"** (:805–807).
  - They are not. The program's two bindings differ.
  - Balanced `1T1T0` is 81 − 27 + 9 − 3 + 0 = 60. The compiler computes 60, and its own
    test `tern_basic.npk` says so. 42 is `1TTT0`.
- **The struct example** (:921), `struct MyStruct = { … };`, is PARSE-001. A struct is
  `struct:MyStruct = { … };`. With that spelling, its layout of 24 bytes at alignment 8 and
  its type `{ i32, i64, i8 }` agree (`ty0925`, `ty0926`).
- **The field-access IR** (:936–940). It shows a `getelementptr` to field 1 and an `i64`
  load. What is emitted loads the struct whole and takes the field with `extractvalue 1`.
  The value read is the same.
- **"A slice … passes down the call stack and never up"** (:1107).
  - A function that passes its slice PARAMETER back (`pass s;`) is accepted and runs.
  - It is safe. A slice of the function's own local is refused, BORROW-001 ("a borrow
    cannot travel up … D-004 rule 2"). A returned view stored in a binding that outlives
    its storage is refused too, BORROW-002, even through the call. Both were measured by
    hand at HUNT2.
  - The registry's S-107 entry (settled as D-326) describes the same reading: a borrow of
    a parameter returns to the frame that owns it.
  - D-004 rule 2's own words ("a borrow may not appear in the value of `pass`") are as
    broad as TYPE's.
- **`#wild_slice` "in `wild` context only"** (:1112). D-315 retired the phrase: no such rule
  exists, and none can be checked (the registry's S-95). TYPE §9.2.1 still states it, and
  `#wild_slice` compiles in `main`.

**Agreements worth naming (part A).**
- tbb:
  - the sentinel;
  - saturation (100 + 100 is ERR, not −56);
  - `ERR / −1` is ERR with no fault;
  - casts out trap TbbErr under both spellings;
  - entering traps under `=>` and saturates under `=>!`;
  - the `err-exit` obligation row for a comparison, and no row for a division.
- The ternary kinds:
  - balanced bounds at every width;
  - `/ %` refused at `trit`/`nit` (TYPE-051);
  - the Kleene `&`/`|` at `trit` and `nit`;
  - digit access and its bounds;
  - the stored value (`i16 60`) and the sentinel (`-32768`);
  - the casts, and `ToString`.
- All 42 flag members' words, and every operation and crossing rule (TYPE-058, -032, -009).
- `sealed` and `hidden`:
  - every write form named is TYPE-079 or TYPE-080;
  - a qualifier off a field is TYPE-081;
  - the headers of `string`, a slice and `OwnedFd` are sealed;
  - an `RGuard`'s `.value` is read-only (TYPE-007).
- Field limits: TYPE-059, -077 and -063, and LimitViolated at each of the three write points.
- Arrays, slices and enums:
  - `T[0]`;
  - the List's `limit<ListLen>` reaching `failsafe` (REACH-002);
  - the enum layouts `{ i32, [2 x i64] }` and `{ i32, [2 x i32] }`;
  - tag casts (TYPE-009, -032);
  - generic enum instances and their inference (TYPE-022, TYPE-017).

## Part B (§10–18)

All nine of part B's disagreements are documentation rows:
- **`--guard-pages` "remains available"** (:1200). No tool has it. npkc refuses it ("unknown
  argument"), and only DECISIONS:2300 and a grammar note name it. This is BUILTIN's
  `--seccomp` shape (F-028).
- **The bare `?`** (:1374, :1387). The safe unwrap `expr ? defaultVal` and "`? NIL`-swallowed"
  are PARSE-011 since D-175; the fallback is `expr ?| d`. The compiler's own advice for
  `??` on a `Result` names the bare `?`: that is [F-045](../F-045-diagnostic-advises-the-retired-question-mark/).
- **The storage_driver extern example** (:1396) is EXTERN-001. The `opaque` tier is
  reserved (D-190); it is the same example as TRAITS:373 (F-043).
- **"Allocated via alloc() and cast: `alloc(N) => arena<T>->`"** (:1439–1441).
  - The cast is TYPE-009: reinterpreting a pointer takes `=>!`.
  - An arena is made with `arena_make(n)` as an `arena<T>` (MEMORY's agreeing
    programs).
- **§15's library layouts** (:1505, :1507, :1508), measured by hand at HUNT2:
  - `vec2` is 16 bytes and `vec4` 32, as the table says.
  - `vec3` is 32, not 24: its `simd<flt64, 3>` aligns to 32 by §14's own rule (:1472).
  - `matrix<int64>` is `{ {ptr, i64, i64}, i64, i64 }`, 40 bytes; the table says
    `{ptr, i32, i32}` and 24.
  - `tensor<int64>` is `{ {ptr, i64, i64}, i64, [9 x i64] }`, 104 bytes; the table says
    `{ptr, ptr, i32}` and 24.
  - The library (`lib/ntensor.npk`) is the measure; TYPE §25 (part C) describes it as
    landed.
- **The elided-Result IR** (:1535). `define i32 @add_elided` is not emitted: a `never fails`
  function returns `{ i32, i32 }` like any other (`ty1320` and `ty1526` agree).

## Part C (§19–28)

Part C's 23 disagreements are:
- sixteen documentation rows (below);
- a silent wrong answer, [F-047](../F-047-a-fixed-byte-view-is-not-immutable/): a
  `fixed uint8[]` view is not immutable;
- invalid IR, [F-048](../F-048-a-nil-field-emits-invalid-ir/): a `NIL` struct field;
- three lower-priority compiler rows,
  [F-046](../F-046-type-reference-661-2122-lower-priority-compiler-rows/);
- F-026's shape (`int32<Meters>` accepted, refused at `93bcb66`);
- DEF-131 (`<=>`, which compiles at `93bcb66`).

The documentation rows:
- **frac `ToString`** (:1657): "whole num/denom" — "-2 5/8". Measured by hand at three
  compilers:
  - −(1 3/8) is {−2, 5, 8} and renders "-2 5/8";
  - −(2 5/8) is {−3, 3, 8} and renders "-3 3/8".
  - So the compiler renders the stated format literally. The example does not say which
    value it shows, and a reader of mixed numbers takes "-2 5/8" for −2.625, not −1.375.
  - *Reasoned:* whether that rendering is a wrong answer is the author's call. Under the
    reference's letter it is not.
- **complex `ToString`** (:1700) is "3.0+4.0i", not "3+4i": each element renders as flt64
  does ("3.0").
- **`pass(NIL)` "desugars to `return Result{ value: NIL, err: 0i32 }`"** (:1942): an `err`
  is an `Error` (D-179, TYPE-007).
- **"`drop(myFunc());`"** (:1943) is TYPE-042: `drop` is licensed by `never fails` only
  (D-163).
- **`void`.**
  - "Only inside `extern { }` blocks" (:1975): a driver method returns NIL, int32 or int64
    (EXTERN-001, D-190).
  - Elsewhere (:1976), the diagnostic is not the one quoted: there is no type named `void`
    (TYPE-001).
- **§28's operator tables**, measured by hand:
  - `+ - *` on integers lower through `llvm.s{add,sub,mul}.with.overflow` (as TYPE:56 says),
    not `add`/`sub`/`mul`;
  - there is no `**` (PARSE-002);
  - `!=` on floats is `fcmp une`, the IEEE predicate (the table's `one` would make
    NaN != NaN false);
  - the string comparison is `string_equals`, not `string_eq`;
  - `ptr->field` does not parse;
  - `val.field` is `extractvalue`, not a `getelementptr` and `load`;
  - the bare `?` is retired (D-175);
  - the ternary branches (`br i1`) rather than `select`, and evaluates one arm (M10's `x05`
    agrees).

**Agreements worth naming (part C).**
- dim256 erased at run time (the same IR type as `tfp256`), and the five named units.
- frac:
  - every row's members and size;
  - automatic normalization and the five invariants;
  - ERR `{min, min, 0}`, sticky, at a zero divisor;
  - TbbErr at a comparison and on any exit;
  - `=>!` truncating toward zero (−2, not −3);
  - no `%`, no bitwise, no literals, no pick;
  - the prelude core.
- complex:
  - Smith's division;
  - ERR in both components;
  - IEEE `==` with NaN;
  - TbbErr on tfp `==`;
  - the element gate and the methods.
- buffer:
  - the example run as written;
  - `{ ptr, i64, i64 }`;
  - the empty buffer for n <= 0;
  - move-only;
  - the four verbs that were not landed.
- The library tier through the compiler's own `lib/`:
  - vec3's methods and `.cross` on vec3 alone;
  - vec9's row-major `.mul`;
  - `matrix`'s 40 and `tensor`'s 104 bytes, as §25 says;
  - rank 9;
  - ternary cells.
- `fixed`:
  - module constants and D-211;
  - ASSIGN-002 for a local, a late local and a field through a pointer;
  - `comptime` (TYPE-004);
  - the constant global.
- NIL, NULL, `any` (its quoted diagnostic) and the one-level `.`.
- `unknown` (TAINT-001), and `ok` gone.
- `<<`'s TYPE-070 and ShiftRange, signed and unsigned `>>`, `@` of a `fixed` (TYPE-071),
  and both ranges in a `for` and a `pick`.

**Found in run 1, not findings (part C).** These were the programs' own mistakes:
- an inline unit expression (`dim256<Meters/Seconds>` does not parse; the unit is
  `MetersPerSecond`);
- `@x =>! any->`, which parses as `@(x =>! any->)`. `ty1989` and `ty2007` had agreed for
  that reason; re-spelled, each agrees for its own.

**Agreements worth naming (part B).**
- Pointers:
  - thin;
  - one `ptr` for wild and borrow alike;
  - TYPE-082 on an array, a slice and a `List` pointer;
  - `(<-p)[i]`.
- Optional:
  - every row of both tables;
  - `zeroinitializer` and no `undef`;
  - the flattening `?.`;
  - TYPE-065 in both forms;
  - the struck `Some`, `Optional{…}`, `.has_value` and `.value`;
  - `NIL?` and `Optional<Optional<T>>`.
- Result:
  - `{ i32, i32 }`;
  - `pass(…)`/`fail(…)`;
  - free field order;
  - no `is_error` to write;
  - `?!` routing its own code to `failsafe` (exit 81 for `E1`, not the callee's `E2`);
  - the `_!`, `_?` and `_~` shorthands;
  - TYPE-039 and TYPE-042.
- All six atomic operations, each as native `seq_cst` IR.
- SIMD:
  - the three rows;
  - the lane and byte limits;
  - alignment as the next power of two;
  - any-lane DivByZero and DivOverflow;
  - lane IntOverflow for `+`, `.sum()` and `+=`;
  - the ordered float `.sum()` ([1e16, 1, −1e16, 1] is 1);
  - one `div-zero`, one `div-min` and one `shift-range` row.
- `dyn`:
  - (N+1) × 8 bytes;
  - `{ ptr, ptr }`;
  - `dyn A & B` is `dyn B & A`.

**Found in run 1, not findings (part B).** Two scripts' own failsafes did not name the
errors `lib/ntensor.npk` declares (`BadShape`, `BadIndex`; REACH-002). They were fixed in
two steps, and the rows above are the measured sizes.

**Found in run 1, not findings (part A).** These were the programs' own mistakes:
- a nyte product past the bound (`ty0786`);
- `raw f(x).m()` parsing as `raw (f(x).m())` (`ty0803b`);
- the prelude's `Whence` variants, which are `Start`, `Current` and `End`. `ty0855` had
  agreed for that reason. Re-spelled, it is refused for the claim's own: `Whence` has no
  bitwise operations.

## Deduplication

- None of these sentences is among F-028's rows (DEF-154), which cover TYPE 1–660 only.
- The `#wild_slice` row is the TYPE sentence that D-315's retirement missed. BUILTIN's rows
  `bi0417b` and `bi0419b` (F-028) are the same phrase for `#wild_ptr` and `#ptr_add`.
- The registry at `93bcb66` has no open entry for any of the thirty-three. Its S-95 and
  S-107 are settled.
- The bare `?` rows repeat, in TYPE's words, rows F-030, F-031 and F-040 found in MEMORY,
  OP and AST. The extern example repeats TRAITS' (F-043).

## Measured, and inferred

- **Measured:**
  - each row's result at three compilers;
  - by hand at HUNT2: the four alignments, the two BORROW refusals, ty1084's parameter,
    and the five library sizes;
  - by hand at three compilers: the two frac renderings, the complex rendering, and the
    operators' IR.
- **Reasoned, not measured:** that the compiler is the right side in each, and the
  balanced-ternary arithmetic of `1T1T0`.
