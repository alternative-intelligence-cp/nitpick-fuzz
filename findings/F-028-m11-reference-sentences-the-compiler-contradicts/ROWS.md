# F-028 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `1b4f0c6`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-028: #wild_ptr, #ptr_add, atomic_from_ptr accepted outside wild, which no reference defines**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0148c` | BUILTIN_REFERENCE.md:148 | atomic_from_ptr is wild-context only: over the address of a plain local it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
| `bi0417b` | BUILTIN_REFERENCE.md:417 | #wild_ptr is legal only in wild context: into a binding not declared `wild` it is refused (D-019's reading). | `refuse` | npkc 0, 0 / 0 | same | same |
| `bi0419b` | BUILTIN_REFERENCE.md:419 | #ptr_add is legal only in wild context: over a buffer's pointer, outside wild, it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: TYPE §2's char8 function table names functions that do not exist**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0239` | TYPE_REFERENCE.md:239 | `toUpper` uppercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0240` | TYPE_REFERENCE.md:240 | `toLower` lowercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0241` | TYPE_REFERENCE.md:241 | `isAlpha` is true for letters and false for a digit and for the bytes beside 'A' and 'Z'. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0242` | TYPE_REFERENCE.md:242 | `isDigit` is true for '0' through '9' only. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0243` | TYPE_REFERENCE.md:243 | `isAlphaNumeric` is true for a letter or a digit and false otherwise. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0244` | TYPE_REFERENCE.md:244 | `isWhitespace` is true for exactly space, tab, CR and LF: vertical tab and form feed are not in the list. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0245` | TYPE_REFERENCE.md:245 | `isUpper` is true for 'A' through 'Z' only. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0246` | TYPE_REFERENCE.md:246 | `isLower` is true for 'a' through 'z' only. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0247` | TYPE_REFERENCE.md:247 | `toUint` reinterprets a char8 as its uint8 byte. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0248` | TYPE_REFERENCE.md:248 | `fromUint` reinterprets a uint8 as the char8 of that byte. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0249` | TYPE_REFERENCE.md:249 | `toChar16` zero-extends a char8: '\xE9' becomes 233char16. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0250` | TYPE_REFERENCE.md:250 | `toChar32` zero-extends a char8: '\xFF' becomes 255char32. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0359b` | TYPE_REFERENCE.md:359 | `string_eq(a, b)` compares byte by byte. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0373` | TYPE_REFERENCE.md:373 | `charAt(s, i)` is the char at index i. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0373b` | TYPE_REFERENCE.md:373 | `charAt` is bounds-checked: an index past the end traps OutOfBounds. | `run:94` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0374` | TYPE_REFERENCE.md:374 | `substring(s, start, length)` extracts `length` chars from `start`. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0375` | TYPE_REFERENCE.md:375 | `split(s, c)` splits by the delimiter into its parts. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0376` | TYPE_REFERENCE.md:376 | `trim` removes leading and trailing whitespace. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0377` | TYPE_REFERENCE.md:377 | `trimLeft` removes leading whitespace only. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0378` | TYPE_REFERENCE.md:378 | `trimRight` removes trailing whitespace only. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0379` | TYPE_REFERENCE.md:379 | `contains(s, t)` is a substring search. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0380` | TYPE_REFERENCE.md:380 | `startsWith(s, p)` is a prefix check. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0381` | TYPE_REFERENCE.md:381 | `endsWith(s, p)` is a suffix check. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0382` | TYPE_REFERENCE.md:382 | `indexOf(s, c)` is the first occurrence's index, -1 if not found. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0383` | TYPE_REFERENCE.md:383 | `toUpper(s)` uppercases the ASCII letters and leaves other bytes alone. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0384` | TYPE_REFERENCE.md:384 | `toLower(s)` lowercases the ASCII letters and leaves other bytes alone. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0385` | TYPE_REFERENCE.md:385 | `toCharArray(s, dest)` copies into a caller-owned destination and returns the elements written. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0386` | TYPE_REFERENCE.md:386 | `fromCharArray(a)` copies a char array into a string. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |
| `ty0388` | TYPE_REFERENCE.md:388 | `to_string(c)` copies a cstring out into a string. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-028: `--extra-picky=no-sys` exists in no tool**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0375` | BUILTIN_REFERENCE.md:375 | `--extra-picky=no-sys` refuses a program that calls sys; without it the program compiles. | `sh:0` | script 1 | same | same |

**F-028: `--seccomp` exists in no tool**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0368` | BUILTIN_REFERENCE.md:368 | The compiler has a `--seccomp` option (a kernel-enforced allowlist). | `sh:0` | script 1 | same | same |

**F-028: `.len` is a per-binding `\|len.x.N\|` symbol, not `(\|npk.len\| base)`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0860i` | VERIFICATION_REFERENCE.md:860 | A loop over `xs.len` indexing `xs[i]` states the length as `\|npk.len\|` in its obligation file. | `sh:0` | script 11 | same | same |
| `vf0895` | VERIFICATION_REFERENCE.md:895 | `.len` of a slice is the uninterpreted `\|npk.len\|` applied to the base in the obligation text. | `sh:0` | script 11 | same | same |

**F-028: `?! 9tbb32` / `?! 7tbb32`: `?!` takes a declared Error (D-179)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0059` | CONCURRENCY_REFERENCE.md:59 | The three honest spellings (relay, `?\| fallback`, `?! 9tbb32`) compile, and each yields the callee's value when it succeeds. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
| `cc0062` | CONCURRENCY_REFERENCE.md:62 | `await f() ?! 9tbb32` on a failing call traps to failsafe with code 9, which no named arm matches, so the catch-all arm answers. | `run:99` | npkc 1 TYPE-007, - / - | same | same |
| `vf0439` | VERIFICATION_REFERENCE.md:439 | The example compiles and runs with §3's divide: `divide(10i32, 2i32) ?! 7tbb32` unwraps 10 and main exits 0. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-028: `ThreadPool.create(n)?` is two stale spellings (a bare `?`, a static method)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0535` | CONCURRENCY_REFERENCE.md:535 | `ThreadPool<LEVEL, CAP>:pool = ThreadPool.create(n)?;` and `await pool.submit(move(job), deadline)?;` compile and run. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-028: `assert_static comptime(...)` needs parentheses**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0312` | MACRO_REFERENCE.md:312 | `assert_static comptime(…)` is evaluated: a true proposition compiles. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-028: `atomic_from_ptr<int32>(p)` does not parse**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0243` | CONCURRENCY_REFERENCE.md:243 | The three ways to obtain an atomic compile as written: scope storage, a struct field, and `atomic_from_ptr<int32>(hdr_ptr)` bound to a local. | `run:0` | npkc 1 PARSE-002, - / - | same | same |
| `cc0250` | CONCURRENCY_REFERENCE.md:250 | `atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr)` aliases existing memory: a store through lk is what the pointer reads. | `run:0` | npkc 1 PARSE-002, - / - | same | same |

**F-028: `await f()` yields Result<T> (line 53), not T (line 142)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0142` | CONCURRENCY_REFERENCE.md:142 | `await f()` yields `T` directly: `int32:x = await f(..)` compiles and x is the value. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-028: `await` outside async is TYPE-043, not NITPICK-040**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0066` | CONCURRENCY_REFERENCE.md:66 | `await` in a synchronous function is refused with the code NITPICK-040. | `refuse:NITPICK-040` | npkc 1 TYPE-043, - / - | same | same |

**F-028: `close(release_fd(move o))` is PARSE-001; the spelling is `move(o)`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0261` | BUILTIN_REFERENCE.md:261 | close(release_fd(move o)) consumes the owner and closes once, reporting close's verdict. | `run:0` | npkc 1 PARSE-001, - / - | same | same |
| `io0212` | IO_REFERENCE.md:212 | `close(release_fd(move o))` closes an owned descriptor and reports the verdict: the reader then sees end of input. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-028: `const` is gone and `fixed` folds (D-222)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0332` | MACRO_REFERENCE.md:332 | A `const` global folds: `comptime(N * 2i32)` over `const int32:N = 4i32;` is 8. | `run:0` | npkc 1 PARSE-001, - / - | same | same |
| `mc0334` | MACRO_REFERENCE.md:334 | A `fixed` binding is not a constant: `comptime(F * 2i32)` over `fixed int32:F` is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: `thread` is a keyword (the spawn form), against 'no language keywords'**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0021` | CONCURRENCY_REFERENCE.md:21 | System threading uses no language keywords, so `thread` is an ordinary identifier. | `run:0` | npkc 1 PARSE-002, - / - | same | same |

**F-028: a bare tfp256 return needs the explicit `=> tfp256` (line 618)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0634b` | TYPE_REFERENCE.md:634 | Declared to return bare tfp256, the same body `pass(d / t)` compiles. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-028: a bool branch is `icmp ne`, not `trunc`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0032` | TYPE_REFERENCE.md:32 | A bool local is an `i8` alloca, and a branch on it truncates the loaded `i8` to `i1`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11bl"?\((?=(?:(?!\n\}).)*?alloca i8\b)(?=(?:(?!\n\}).)*?trunc i8 %\S+ to i1)` | npkc 0, 0 / 0 | same | same |

**F-028: a borrow may cross an await since D-180 (spawn only)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0298b` | CONCURRENCY_REFERENCE.md:298 | A borrow may not cross an await point: a borrow held across an `await` and used after it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
| `cc0298c` | CONCURRENCY_REFERENCE.md:298 | A borrow may not cross an await point: passing `@x` into an awaited async callee that suspends while holding it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
| `vf0268` | VERIFICATION_REFERENCE.md:268 | A borrow may not be carried across an await point: a pointer local holding `@x` used after an await is refused. | `refuse` | npkc 0, 0 / 0 | same | same |
| `vf0819` | VERIFICATION_REFERENCE.md:819 | Borrows cannot cross an await: a $$i claim held by a pointer local across an await is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: a limit on main's parameter is TYPE-060, not TYPE-064**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0145b` | VERIFICATION_REFERENCE.md:145 | A limit on main's parameter is refused: the sentence lists it among the TYPE-064 sites. | `refuse:TYPE-064` | npkc 1 TYPE-060, - / - | same | same |

**F-028: a requires on a never-fails function is accepted (line 351 says so; line 437 not)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0437` | VERIFICATION_REFERENCE.md:437 | A function with a requires is never `never fails`: declaring one is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: a simd float .min() returns a NaN in the last lane**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf1201` | VERIFICATION_REFERENCE.md:1201 | A float `simd` `.min()` folds with a select over the ordered strict compare, false on NaN, so a NaN lane is passed over: min of (1, 3, 0.5, NaN) is 0.5. | `run:0` | npkc 0, 10 / 10 | same | same |

**F-028: a simd float-to-int cast has no cast-range row (its guard traps CastRange)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0861g` | VERIFICATION_REFERENCE.md:861 | A `simd<flt64, 4> =>! simd<int32, 4>` is ONE `cast-range` row. | `sh:0` | script 10 | same | same |

**F-028: a spawned task must return NIL (D-177), against 'VALUE discarded'**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0073` | CONCURRENCY_REFERENCE.md:73 | `drop work();` spawns an async function whose VALUE is discarded: a value-returning async callee is accepted in the spawn form. | `run:0` | npkc 1 TYPE-043, - / - | same | same |

**F-028: a struct subject's limit row, and a List-count loop bound, are encoded**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0151` | VERIFICATION_REFERENCE.md:151 | A struct subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt). | `sh:0` | script 1 | same | same |
| `vf0548` | VERIFICATION_REFERENCE.md:548 | A List's count as a loop's bound has no length term: the terminate rows are unencoded (0 in rows.txt). | `sh:0` | script 1 | same | same |
| `vf1036` | VERIFICATION_REFERENCE.md:1036 | A `limit` over a struct subject is an `unencoded` row (fifth field `0`). | `sh:0` | script 11 | same | same |
| `vf1228b` | VERIFICATION_REFERENCE.md:1228 | A `limit` over a struct subject is `unencoded`. | `sh:0` | script 11 | same | same |
| `vf1244` | VERIFICATION_REFERENCE.md:1244 | Still at 1.5.8b: a `limit` over a struct is `unencoded` with its guard kept. | `sh:0` | script 11 | same | same |

**F-028: an await of a coroutine with a limited parameter has a limit-subsume row**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `vf0867b` | VERIFICATION_REFERENCE.md:867 | A call of an ASYNC callee with a limited parameter has no `limit-subsume` row. | `sh:0` | script 10 | same | same |
| `vf0931` | VERIFICATION_REFERENCE.md:931 | An async callee with a limited parameter has no `.body` twin and its call site no `limit-subsume` row. | `sh:0` | script 10 | same | same |

**F-028: async lowers to no llvm.coro and no %Future type**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0130` | CONCURRENCY_REFERENCE.md:130 | `async` lowers to `@llvm.coro` state machines: the emitted IR uses llvm.coro intrinsics. | `ir:@llvm\.coro\.` | npkc 0, 0 / 0 | same | same |
| `cc0132` | CONCURRENCY_REFERENCE.md:132 | `Future<T>` is the handle `%Future = type { ptr, ptr }` (coroutine handle, result slot) in the emitted IR of an async program. | `ir:%Future = type \{ ptr, ptr \}` | npkc 0, 0 / 0 | same | same |

**F-028: nit and nyte ranges are §6's balanced ones (D-197), not 0-8 / 2 nits**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0306` | TYPE_REFERENCE.md:306 | A nit takes the values 0 to 8: `nit:n = 8;` holds 8. | `run:0` | npkc 1 TYPE-031, - / - | same | same |
| `ty0307` | TYPE_REFERENCE.md:307 | A nyte is 2 nits holding 0 to 80: `nyte:n = 81;` is out of range and refused. | `refuse` | npkc 0, 10 / 10 | same | same |

**F-028: no buffered stream has seek**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `io0232` | IO_REFERENCE.md:232 | Seeking a buffered stream discards its read buffer: after a text reader has read `ab` (buffering `cd`), seeking to the start and reading gives `ab` again. | `run:0` | npkc 1 TYPE-019,TYPE-043, - / - | same | same |

**F-028: sys's nested bare-builtin refusal is stale since D-201**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0348` | BUILTIN_REFERENCE.md:348 | An argument that is a nested bare-builtin call is refused (bind it to a typed name first). | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: tbb arithmetic does not use the with.overflow intrinsics**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0144` | TYPE_REFERENCE.md:144 | tbb arithmetic uses the same overflow intrinsics: a tbb32 `+` lowers through llvm.sadd.with.overflow.i32. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11tb"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i32\()` | npkc 0, 0 / 0 | same | same |

**F-028: tensor and matrix are not types (P4, line 2120)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0308` | TYPE_REFERENCE.md:308 | `tensor` is a native primitive: `tensor<flt64>` names a type with no import. | `run:0` | npkc 1 TYPE-001, - / - | same | same |
| `ty0309` | TYPE_REFERENCE.md:309 | `matrix` is a native primitive: `matrix<flt64>` names a type with no import. | `run:0` | npkc 1 TYPE-001, - / - | same | same |

**F-028: tfp256 is i256 at the IR, not { i64, i64, i64, i64 }**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0648` | TYPE_REFERENCE.md:648 | At the IR, dim256<Joules> is tfp256, whose type is `{ i64, i64, i64, i64 }`. | `ir:^%\"?tfp256\"? = type \{ ?i64, i64, i64, i64 ?\}|^define [^@\n]* @"?(?:[\w$]+\.)*m11dj"?\(\{ ?i64, i64, i64, i64 ?\} ` | npkc 0, 0 / 0 | same | same |

**F-028: the EOF identity is IoEof, not E_EOF**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `io0075` | IO_REFERENCE.md:75 | End of input is the error code `E_EOF`: a read of an exhausted stream fails with it. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-028: the constructor is text_writer, not text_writer_create**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `io0115` | IO_REFERENCE.md:115 | `TextWriter:w = text_writer_create(sink, LineEnding.Lf) ?! …;` and the CrLf twin build text writers; the CrLf one writes `\r\n`. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-028: the example uses `raw` on a callee that is not never fails (D-163)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0112` | MACRO_REFERENCE.md:112 | The emit_helpers example: three emitted declarations referencing each other; helper_sum is 42. | `run:0` | npkc 1 MACRO-009,TYPE-042, - / - | same | same |

**F-028: the example's `main` has no parameter (TYPE-083, DEF-96's rule)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0042` | CONCURRENCY_REFERENCE.md:42 | The declaring-and-awaiting example compiles as written and exits 0. | `run:0` | npkc 1 TYPE-010,TYPE-083, - / - | npkc 1 TYPE-010, - / - | same |

**F-028: the example's mutable module binding is refused (D-211)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0159` | MACRO_REFERENCE.md:159 | The hygiene example: `#report()` reads the TOP-LEVEL `shared` (100), not main's local 5, so the template is "shared = 100". | `run:0` | npkc 1 TYPE-055, - / - | same | same |

**F-028: the identity is DeadlineExceeded, not DEADLINE_EXCEEDED**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0426` | CONCURRENCY_REFERENCE.md:426 | Expiry is the error `DEADLINE_EXCEEDED`: an expired recv's error compares equal to it. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-028: the standard streams are not confined to main's scope**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `io0242b` | IO_REFERENCE.md:242 | The standard streams belong to main's scope and are passed down: constructing one in a helper function is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-028: the unit example redeclares prelude units (RESOLVE-001)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `ty0580` | TYPE_REFERENCE.md:580 | Unit declarations of this form compile, and a declared name is its vector's name (Furlongs is Meters). | `run:0` | npkc 1 RESOLVE-001, - / - | same | same |

**F-028: there is no #align_of**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0310b` | MACRO_REFERENCE.md:310 | The evaluator folds the alignment intrinsic: `comptime(#align_of<int64>())` is 8. | `run:0` | npkc 1 MACRO-001, - / - | same | same |
| `mc0369c` | MACRO_REFERENCE.md:369 | This language writes `#align_of<T>()`: `#align_of<int64>()` is 8. | `run:0` | npkc 1 MACRO-001, - / - | same | same |

**F-028: there is no Actor type**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `cc0501` | CONCURRENCY_REFERENCE.md:501 | `Actor<M, R, LEVEL>` is a type with `tell` (Result<NIL>) and `ask` (Result<R>), each taking a moved message and a deadline. | `run:0` | npkc 1 TYPE-001,TYPE-043, - / - | same | same |
| `cc0523` | CONCURRENCY_REFERENCE.md:523 | With R = NIL, `ask` is an acknowledgement: it yields Result<NIL>. | `run:0` | npkc 1 TYPE-001,TYPE-043, - / - | same | same |

**F-028: there is no Stream trait**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `io0022` | IO_REFERENCE.md:22 | `Stream` is the trait every readable or writable thing implements: it can bound a generic parameter. | `run:0` | npkc 1 TYPE-001, - / - | same | same |

**F-028: unsuffixed literals are accepted in a typed context**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `mc0371` | MACRO_REFERENCE.md:371 | The corpus's width-less literals (`0`, `10`, `exit 1`) are not this language: they are refused (literals carry their width). | `refuse` | npkc 0, 1 / 1 | same | same |

**F-028: §5's inline assembly (row and example) is PARSE-002**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `1b4f0c6` |
|---|---|---|---|---|---|---|
| `bi0432` | BUILTIN_REFERENCE.md:432 | asm<T> wraps the output in Result<T>; a negative integer return is an error. | `run:0` | npkc 1 PARSE-002, - / - | same | same |
| `bi0439` | BUILTIN_REFERENCE.md:439 | The example: x86_64 assembly adding 1 to its input, returning Result<int32>. | `run:0` | npkc 1 PARSE-002, - / - | same | same |
