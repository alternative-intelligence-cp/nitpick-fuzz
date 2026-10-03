# F-044 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-044: `#wild_slice` "in `wild` context only": D-315 retired the phrase (no such rule exists or can be checked), and TYPE §9.2.1 still states it**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1112` | TYPE_REFERENCE.md:1112 | `#wild_slice` is for wild context only: outside one it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-044: `--guard-pages` "remains available": no tool has it; npkc refuses the argument, and only DECISIONS:2300 and a grammar note name it**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1200` | TYPE_REFERENCE.md:1200 | `--guard-pages` is available: npkc accepts it on an ordinary program. | `sh:0` | script 1 | same | same |

**F-044: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are not one value: balanced 1T1T0 is 60 (81 - 27 + 9 - 3), as the compiler computes, and 42 is 1TTT0**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0805` | TYPE_REFERENCE.md:805 | A ternary-typed slot takes an unsuffixed integer literal and a balanced-digit literal: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are one value spelled two ways. | `run:0` | npkc 0, 10 / 10 | same | same |

**F-044: a may-fail call "`? NIL`-swallowed": the same retired `?` (PARSE-011, D-175)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1387` | TYPE_REFERENCE.md:1387 | A may-fail NIL call is swallowed with `? NIL`. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-044: a slice "passes down the call stack and never up": a slice PARAMETER passed back up is accepted, and safe: a view of the frame's own local is BORROW-001, and a returned view stored past its storage is BORROW-002 (measured); the registry's S-107 controls describe the same reading of D-004**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1107` | TYPE_REFERENCE.md:1107 | A slice never passes up the call stack: a function returning a slice is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-044: an arena "allocated via alloc() and cast: alloc(N) => arena<T>->": the cast is TYPE-009 (a pointer reinterpretation takes `=>!`), and an arena is made with `arena_make(n)`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1439` | TYPE_REFERENCE.md:1439 | An arena is allocated with `alloc(N)` and a cast: `alloc(N) => arena<T>->` compiles. | `compile` | npkc 1 TYPE-009, - / - | same | same |

**F-044: tbb is "used for ... the `failsafe` signature": `failsafe` takes exactly one `Error` (D-179, TYPE-044)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0715` | TYPE_REFERENCE.md:715 | tbb is used for the failsafe signature: a failsafe whose parameter is a tbb32 is accepted. | `run:0` | npkc 1 TYPE-044, - / - | same | same |

**F-044: the elided-Result IR (`define i32 @add_elided`): a `never fails` function returns `{ i32, i32 }`; no Result elision is emitted**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1535` | TYPE_REFERENCE.md:1535 | A function proved infallible returns a raw `i32`: a `never fails` int32 function is `define i32`. | `ir:(?m)^define i32 @"?(?:[\w$]+\.)*m11e"?\(` | npkc 0, 0 / 0 | same | same |

**F-044: the field-access IR (a `getelementptr` to field 1, then an `i64` load) is not what is emitted: the struct is loaded whole and the field taken with `extractvalue`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0936` | TYPE_REFERENCE.md:936 | Reading `obj.y` is a `getelementptr` to field index 1 and an `i64` load. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11gy"?\((?=(?:(?!\n\}).)*?getelementptr[^\n]*, i32 0, i32 1\b)(?=(?:(?!\n\}).)*?load i64)` | npkc 0, 0 / 0 | same | same |

**F-044: the safe unwrap `expr ? defaultVal`: a bare `?` is PARSE-011 since D-175; the fallback is `expr ?\| d`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1374` | TYPE_REFERENCE.md:1374 | Safe unwrap `expr ? defaultVal` gives the default on an error. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-044: the storage_driver extern example is EXTERN-001: the `opaque` tier is reserved (D-190), as at TRAITS:373 (F-043)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1396` | TYPE_REFERENCE.md:1396 | The storage_driver extern example compiles. | `compile` | npkc 1 EXTERN-001, - / - | same | same |

**F-044: the struct example is spelled `struct MyStruct = ...` (PARSE-001); a struct is `struct:Name`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0921` | TYPE_REFERENCE.md:921 | The struct example compiles as written. | `compile` | npkc 1 PARSE-001, - / - | same | same |

**F-044: §15's `matrix<T>` is `{ptr, i32, i32}`, 24 bytes: the library's is `{ {ptr, i64, i64}, i64, i64 }`, 40 bytes for `matrix<int64>`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1507` | TYPE_REFERENCE.md:1507 | `matrix<int64>` (the library's `ntensor.npk`) is 24 bytes. | `sh:0` | script 1 | same | same |

**F-044: §15's `tensor<T>` is `{ptr, ptr, i32}`, 24 bytes: the library's is `{ {ptr, i64, i64}, i64, [9 x i64] }`, 104 bytes for `tensor<int64>`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1508` | TYPE_REFERENCE.md:1508 | `tensor<int64>` (the library's `ntensor.npk`) is 24 bytes. | `sh:0` | script 1 | same | same |

**F-044: §15's `vec3` is 24 bytes: its `simd<flt64, 3>` aligns to 32 by §14's own rule, so `vec3` is 32**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1505` | TYPE_REFERENCE.md:1505 | `vec3` (the library's `nvec.npk`) is 24 bytes. | `sh:0` | script 1 | same | same |

**F-044: §6's table gives `tbb128` and `tbb256` alignment 8; both align to 16 (`{i8, i128}` is 32 bytes, `{i8, i256}` 48), as TYPE §5's rows 460-461 and its line 469 say (ty0460, ty0461, ty0469 agree)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0673` | TYPE_REFERENCE.md:673 | `tbb128` is 16 bytes with alignment 8; its valid range is symmetric, -(2^127-1) .. 2^127-1, and one step past either end is ERR. | `run:0` | npkc 0, 11 / 11 | same | same |
| `ty0674` | TYPE_REFERENCE.md:674 | `tbb256` is 32 bytes with alignment 8; its valid range is symmetric, -(2^255-1) .. 2^255-1, and one step past either end is ERR. | `run:0` | npkc 0, 11 / 11 | same | same |
