# F-040 — the rows (written by `gen/m11_rows.py`)

One row per claim, grouped by what triage found (`gen/m11_triage.py`). The program is
`m11/programs/<id>.npk` (or `.sh`); its expectation was written from the sentence before it
first ran. Measured at HUNT2 `9126350` (the final run), the baseline `c3bdae2` and the
compiler's newest `main` `93bcb66`; "same" is the same npkc, codes, both legs and verdict
as HUNT2.


**F-040: `++` and `--` are removed (D-174, PARSE-010)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0297` | AST_REFERENCE.md:297 | `++` and `--` are postfix operators: `x++; x--;` compiles. | `compile` | npkc 1 PARSE-010, - / - | same | same |

**F-040: `?!`'s argument is an `Error` constant (D-179), not a `tbb32` (TYPE-007)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0415` | AST_REFERENCE.md:415 | `e ?! code` takes exactly one `tbb32` argument: `k(3i32) ?! 5tbb32` compiles. | `compile` | npkc 1 TYPE-007, - / - | same | same |

**F-040: `FFhex` is an identifier (D-147, LEXICAL:337), not a literal (RESOLVE-002)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0281` | AST_REFERENCE.md:281 | `FFhex` is a hex literal: an `int32` bound to it is 255. | `run:0` | npkc 1 RESOLVE-002, - / - | same | same |

**F-040: `failsafe` takes one `Error` (TYPE-044, D-179), not `tbb32:err`**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0093` | AST_REFERENCE.md:93 | `failsafe`'s one parameter is `tbb32:err`: a failsafe so declared compiles. | `compile` | npkc 1 TYPE-044, - / - | same | same |

**F-040: `ok` is no bare-name builtin: it is removed (AST:329, D-097), RESOLVE-002**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0385b` | AST_REFERENCE.md:385 | `ok` is one of the bare-name builtins: `ok(t)` is an ordinary call. | `compile` | npkc 1 RESOLVE-002, - / - | same | same |

**F-040: `pub const int32:MAX = 100i32;` and a `const` local qualifier do not parse (PARSE-001): `const` is retired (AST:505 says so)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0044` | AST_REFERENCE.md:44 | A global is declared `pub const int32:MAX = 100i32;`: MAX is 100. | `run:0` | npkc 1 PARSE-001, - / - | same | same |
| `as0499` | AST_REFERENCE.md:499 | `const` qualifies a local: `const int32:x = 3i32;` compiles. | `compile` | npkc 1 PARSE-001, - / - | same | same |

**F-040: `unit:Hertz = 1 / Seconds;` is RESOLVE-001: the prelude declares `Hertz` (another name compiles)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0045` | AST_REFERENCE.md:45 | `unit:Hertz = 1 / Seconds;` declares a named unit for `dim256<U>`: a `dim256<Hertz>` value compiles. | `compile` | npkc 1 RESOLVE-001, - / - | same | same |

**F-040: a Result literal's `err` is an `Error` (D-179): `err: 0i32` is TYPE-007, and a success literal omits `err` (TYPE:1330)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0195` | AST_REFERENCE.md:195 | `return` takes the literal `Result{…}` form: `return Result{ value: 5i32, err: 0i32 };` returns 5. | `run:0` | npkc 1 TYPE-007, - / - | same | same |
| `as0307` | AST_REFERENCE.md:307 | `Result{value: v, err: e}` constructs a Result: one with err 0 is not an error and holds v. | `run:0` | npkc 1 TYPE-007, - / - | same | same |

**F-040: a bare-name builtin need not return `Result<T>`: `string_byte_length` returns `int64` (TYPE-007 binding it to `Result<int64>`)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0403` | AST_REFERENCE.md:403 | A bare-name builtin returns `Result<T>` like any function: `string_byte_length`'s call binds as a `Result<int64>`. | `compile` | npkc 1 TYPE-007, - / - | same | same |

**F-040: a cast to a `wild` target is `=>!` (D-019's one door): `p => wild int8->` is BORROW-011, even from a pointer that is no borrow (measured by hand)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0437` | AST_REFERENCE.md:437 | A cast target carries a memory qualifier: `p => wild int8->` compiles. | `compile` | npkc 1 BORROW-011, - / - | same | same |

**F-040: an extern method's failure contract is not required (it compiles without one) and `never fails` on one is EXTERN-002: D-149 removed the contracts (MODULE:263-266)**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0128` | AST_REFERENCE.md:128 | An extern function's failure contract is REQUIRED: a method with none is a compile error. | `sh:0` | script 1 | same | same |
| `as0137` | AST_REFERENCE.md:137 | A failure contract is `fails on …` or `never fails`: an extern method declared `never fails` compiles. | `sh:0` | script 1 | same | same |

**F-040: generic arguments in an expression take the turbofish (LEXICAL:239, D-064): `f<int32>(x)` is PARSE-002**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0364` | AST_REFERENCE.md:364 | Generic arguments may arrive implicitly: `idt<int32>(5i32)` is a call, as `idt::<int32>(5i32)` is. | `run:0` | npkc 1 PARSE-002, - / - | same | same |

**F-040: the bare `?` fallback is struck (D-175, PARSE-011), and `?\|` is the fallback, not struck**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0413` | AST_REFERENCE.md:413 | `e ? d` unwraps with a default: `k(3i32) ? 0i32` is 3. | `run:0` | npkc 1 PARSE-011, - / - | same | same |
| `as0416` | AST_REFERENCE.md:416 | `?\|` is struck (D-167) and refused by name: `k(3i32) ?\| 0i32` is refused. | `refuse` | npkc 0, 0 / 0 | same | same |

**F-040: there is no `vec3(…)` constructor: `vec3` is a library type (D-135), RESOLVE-002**

| claim | sentence | the claim | expected | HUNT2 | `c3bdae2` | `93bcb66` |
|---|---|---|---|---|---|---|
| `as0450` | AST_REFERENCE.md:450 | `vec3(1.0, 2.0, 3.0)` constructs a vector. | `compile` | npkc 1 RESOLVE-002, - / - | same | same |
