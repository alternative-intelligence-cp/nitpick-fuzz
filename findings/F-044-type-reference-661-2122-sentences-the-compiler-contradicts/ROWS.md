# F-044 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-044: "`string_eq` for strings": the function is `string_equals` (RESOLVE-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2053e` | TYPE_REFERENCE.md:2053 | Strings compare with `string_eq`. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-044: "call a NIL-returning function without checking: `drop(myFunc());`": `drop` is licensed by `never fails` only (D-163, TYPE-042)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1943` | TYPE_REFERENCE.md:1943 | A NIL-returning function is called without checking by `drop(myFunc());`. | `run:0` | npkc 1 TYPE-042, - / - | same | same |

**F-044: `!=` is `fcmp one` on floats: it is `fcmp une`, the IEEE predicate (NaN != NaN is true; `one` would make it false)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2054` | TYPE_REFERENCE.md:2054 | `!=` lowers to `icmp ne` on int32 and `fcmp one` on flt64. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11i"?\((?=(?:(?!\n\}).)*?\bicmp ne i32\b))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11f"?\((?=(?:(?!\n\}).)*?\bfcmp one double\b))` | npkc 0, 0 / 0 | same | same |

**F-044: `#wild_slice` "in `wild` context only": D-315 retired the phrase (no such rule exists or can be checked), and TYPE §9.2.1 still states it**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1112` | TYPE_REFERENCE.md:1112 | `#wild_slice` is for wild context only: outside one it is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-044: `**` "power, library call": there is no `**` (PARSE-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2037` | TYPE_REFERENCE.md:2037 | `**` is power: 2 ** 10 is 1024. | `run:0` | npkc 1 PARSE-002, - / - | same | same |

**F-044: `--guard-pages` "remains available": no tool has it; npkc refuses the argument, and only DECISIONS:2300 and a grammar note name it**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1200` | TYPE_REFERENCE.md:1200 | `--guard-pages` is available: npkc accepts it on an ordinary program. | `sh:0` | script 1 | same | same |

**F-044: `pass(NIL)` "desugars to `return Result{ value: NIL, err: 0i32 }`": an `err` is an `Error` (D-179, TYPE-007)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1942` | TYPE_REFERENCE.md:1942 | The desugared form `return Result{ value: NIL, err: 0i32 };` is a success. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-044: `ptr->field` "member via ptr": it does not parse; a member is `.` (D-098)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2073` | TYPE_REFERENCE.md:2073 | `ptr->field` reads a member through a pointer. | `run:0` | npkc 1 PARSE-001, - / - | same | same |

**F-044: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are not one value: balanced 1T1T0 is 60 (81 - 27 + 9 - 3), as the compiler computes, and 42 is 1TTT0**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0805` | TYPE_REFERENCE.md:805 | A ternary-typed slot takes an unsuffixed integer literal and a balanced-digit literal: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are one value spelled two ways. | `run:0` | npkc 0, 10 / 10 | same | same |

**F-044: `val.field` is "`getelementptr` + `load`": it is `extractvalue` (as TYPE:936)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2074` | TYPE_REFERENCE.md:2074 | `val.field` lowers to a `getelementptr` and a `load`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11g"?\((?=(?:(?!\n\}).)*?\bgetelementptr\b)(?=(?:(?!\n\}).)*?\bload i32\b)` | npkc 0, 0 / 0 | same | same |

**F-044: `void` "ONLY valid inside `extern { }` blocks": a driver method returns NIL, int32 or int64 (EXTERN-001, D-190)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1975` | TYPE_REFERENCE.md:1975 | `void` is valid inside an extern block, as a method's return type. | `sh:0` | script 1 | same | same |

**F-044: `void` elsewhere is not the quoted diagnostic: there is no type named `void` (TYPE-001)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1976` | TYPE_REFERENCE.md:1976 | `void` outside an extern block is refused with "'void' is reserved for extern blocks; use 'NIL' for Nitpick functions returning nothing". | `sh:0` | script 1 | same | same |

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

**F-044: complex `ToString` "3+4i": via the element's own rendering it is "3.0+4.0i"**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1700` | TYPE_REFERENCE.md:1700 | ToString renders "3+4i" and "3-4i", and a tfp ERR pair "ERR". | `run:0` | npkc 0, 10 / 10 | same | same |

**F-044: frac `ToString` "whole num/denom", "-2 5/8": the example does not say its value. The compiler renders -(1 3/8) = {-2, 5, 8} as "-2 5/8" and -(2 5/8) = {-3, 3, 8} as "-3 3/8"; a reader of mixed numbers takes "-2 5/8" for -2.625**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty1657` | TYPE_REFERENCE.md:1657 | ToString renders "3 1/3", "-2 5/8", "0" and "ERR". | `run:0` | npkc 0, 11 / 11 | same | same |

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

**F-044: the ternary is "`select i1`": it branches (`br i1`), evaluating one arm (x05 agrees)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2101b` | TYPE_REFERENCE.md:2101 | The ternary lowers to `select i1`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\((?=(?:(?!\n\}).)*?\bselect i1\b)` | npkc 0, 0 / 0 | same | same |

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

**F-044: §28's IR column gives `add`/`sub`/`mul` for `+ - *`: integers lower through `llvm.s{add,sub,mul}.with.overflow` (TYPE:56 says so), floats through `fadd`/`fsub`/`fmul`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2032` | TYPE_REFERENCE.md:2032 | `+` lowers to `add` on int32 and `fadd` on flt64. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11i"?\((?=(?:(?!\n\}).)*?\badd\b))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11f"?\((?=(?:(?!\n\}).)*?\bfadd\b))` | npkc 0, 0 / 0 | same | same |
| `ty2033` | TYPE_REFERENCE.md:2033 | `-` lowers to `sub` on int32 and `fsub` on flt64. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11i"?\((?=(?:(?!\n\}).)*?\bsub\b))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11f"?\((?=(?:(?!\n\}).)*?\bfsub\b))` | npkc 0, 0 / 0 | same | same |
| `ty2034` | TYPE_REFERENCE.md:2034 | `*` lowers to `mul` on int32 and `fmul` on flt64. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11i"?\((?=(?:(?!\n\}).)*?\bmul\b))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11f"?\((?=(?:(?!\n\}).)*?\bfmul\b))` | npkc 0, 0 / 0 | same | same |

**F-044: §28's `?` safe unwrap: PARSE-011 since D-175**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty2079` | TYPE_REFERENCE.md:2079 | `res ? default` is the safe unwrap. | `run:0` | npkc 1 PARSE-011, - / - | same | same |

**F-044: §6's table gives `tbb128` and `tbb256` alignment 8; both align to 16 (`{i8, i128}` is 32 bytes, `{i8, i256}` 48), as TYPE §5's rows 460-461 and its line 469 say (ty0460, ty0461, ty0469 agree)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `ty0673` | TYPE_REFERENCE.md:673 | `tbb128` is 16 bytes with alignment 8; its valid range is symmetric, -(2^127-1) .. 2^127-1, and one step past either end is ERR. | `run:0` | npkc 0, 11 / 11 | same | same |
| `ty0674` | TYPE_REFERENCE.md:674 | `tbb256` is 32 bytes with alignment 8; its valid range is symmetric, -(2^255-1) .. 2^255-1, and one step past either end is ERR. | `run:0` | npkc 0, 11 / 11 | same | same |
