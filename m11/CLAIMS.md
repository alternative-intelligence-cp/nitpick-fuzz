# M11 claims: the references, checked against the compiler

Written by `gen/m11.py` from `gen/m11_claims/` (regenerate with `python3 gen/m11.py`).
Each claim is read from one line of one reference at HUNT2 `9126350`
(the compiler's `meta/specs/`), quotes that line, and carries the outcome the TEXT
says, written before any program ran (PLAN.md 11.2). Kinds: `example` (a fenced
code block, at its opening line), `row` (a table body row), `rule` (a normative
sentence). Expected: `run:N` (npkc 0, both legs exit N; 0 is the reference's
answer), `refuse[:CODE]` (npkc 1), `compile` (npkc 0 and both legs build),
`ir:RE`/`ir!:RE` (the emitted IR does/does not match), `sh:N` (a script's exit).
A trap exits its `failsafe` arm's code: HeapBadRequest 91, HeapOom 92, IntOverflow 93, OutOfBounds 94, Unreachable 95, WildLeak 96, DivByZero 97, DivOverflow 98, StaleHandle 100, DeadlineExceeded 101, ChannelClosed 102, DriverLeak 103, IoEof 104, WouldBlock 105, StackExhausted 106, MachineFault 107, LimitViolated 108, DecreasesViolated 109, TbbErr 110, ShiftRange 111, CastRange 112, BadStep 113, BorrowOverlap 114, RequiresViolated 115, EnsuresViolated 116, InvariantViolated 117, Interrupted 118, NotFound 119, Exists 120, CrossDevice 121, BadPath 122.

**3207 claims: 2700 testable, 507 untestable** (each with its reason).

| reference | claims | examples | rows | rules | testable | untestable |
|---|---|---|---|---|---|---|
| AST | 202 | 8 | 116 | 78 | 181 | 21 |
| BUILD | 97 | 4 | 26 | 67 | 38 | 59 |
| BUILTIN | 227 | 2 | 109 | 116 | 194 | 33 |
| CONCURRENCY | 152 | 11 | 21 | 120 | 122 | 30 |
| CONTROL | 110 | 14 | 7 | 89 | 108 | 2 |
| IO | 78 | 5 | 9 | 64 | 67 | 11 |
| LEXICAL | 184 | 9 | 34 | 141 | 181 | 3 |
| MACRO | 124 | 13 | 34 | 77 | 119 | 5 |
| MEMORY | 181 | 10 | 11 | 160 | 146 | 35 |
| MODULE | 139 | 7 | 3 | 129 | 124 | 15 |
| OP | 159 | 0 | 87 | 72 | 157 | 2 |
| TRAITS | 119 | 19 | 16 | 84 | 115 | 4 |
| TYPE | 719 | 38 | 179 | 502 | 675 | 44 |
| VERIFICATION | 716 | 11 | 146 | 559 | 473 | 243 |

The line ranges extracted (each module declares its own with `covers()`; coverage
of every code block and table row is checked inside them) and those not yet
extracted:

| reference | lines | extracted | lines extracted | not extracted |
|---|---|---|---|---|
| AST | 644 | 1–644 | 644 | — |
| BUILD | 682 | 1–682 | 682 | — |
| BUILTIN | 447 | 1–447 | 447 | — |
| CONCURRENCY | 647 | 1–647 | 647 | — |
| CONTROL | 415 | 1–415 | 415 | — |
| IO | 287 | 1–287 | 287 | — |
| LEXICAL | 410 | 1–410 | 410 | — |
| MACRO | 412 | 1–412 | 412 | — |
| MEMORY | 533 | 1–533 | 533 | — |
| MODULE | 300 | 1–300 | 300 | — |
| OP | 403 | 1–403 | 403 | — |
| TRAITS | 766 | 1–766 | 766 | — |
| TYPE | 2122 | 1–660, 661–1176, 1177–1592 | 1592 | 1593–2122 |
| VERIFICATION | 2351 | 1–845, 846–1247, 1248–2351 | 2351 | — |

## AST (`meta/specs/AST_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `as0032` | 32 | row | “**`mod:name = { … };`**, or **`mod:name;`** for a file (D-088)” | A module is `mod:name = { … };` inline or `mod:name;` for a file: both compile and are reached. | `run:0` |
| `as0033` | 33 | row | “`kind` ∈ wildcard / single / selective / namespace” | An import is one of four kinds, wildcard, single, selective and namespace: all four compile. | `run:0` |
| `as0034` | 34 | row | “the contracts window holds `requires`/`ensures`/`acquires`, the `never fails`” | A function's contracts window holds `requires`, `ensures`, `never fails` and `pure` together. | `run:0` |
| `as0035` | 35 | row | “\| `StructDecl` \| `name`, `visibility`, `generics`, `fields: FieldDecl[]`, `attributes` \| \|” | The StructDecl node holds name, visibility, generics, fields and attributes. | untestable [internal] the node's fields |
| `as0036` | 36 | row | “variants may carry payloads” | Enum variants may carry payloads: `Opt.Som(5i32)` matched by `(Som(x))` binds 5. | `run:0` |
| `as0037` | 37 | row | “supertraits combine with **`&`** (D-029)” | Supertraits combine with `&`: `trait:C = A & B & { … };` compiles, and a type implementing all three calls each. | `run:0` |
| `as0038` | 38 | row | “**`impl:Type`** or **`impl:Type:Trait`**” | `impl:Type` and `impl:Type:Trait` both compile: an inherent method and a trait method are called. | `run:0` |
| `as0038b` | 38 | rule | “type always first, no connector (D-031)” | There is no connector: `impl Speaks for Loud` is refused. | `refuse` |
| `as0039` | 39 | row | “`Rules<int32>:r = { $ > 0i32 }`” | `Rules<int32>:r_pos = { $ > 0i32 };` declares a rule: a `limit<r_pos>` binding assigned -1 traps LimitViolated. | `trap:LimitViolated` |
| `as0040` | 40 | row | “invoked as **`#name(args)`** (D-046)” | A macro is invoked as `#name(args)`: an expression macro `#twice(4i32)` is 8. | `run:0` |
| `as0041` | 41 | row | “an invocation standing **where a declaration is expected**” | A declaration macro invoked at module level splices its declaration: the emitted function is called. | `run:0` |
| `as0042` | 42 | row | “**`extern:"libc" = { … };`** (D-088)” | An extern block is named by a string: `extern:"mockif" = { … };` compiles (in HUNT2's method form). | `sh:0` |
| `as0043` | 43 | row | “**`extern`-block item only**” | An `opaque struct` is an extern-block item only: one at module level is refused. | `refuse` |
| `as0044` | 44 | row | “`pub const int32:MAX = 100i32;`” | A global is declared `pub const int32:MAX = 100i32;`: MAX is 100. | `run:0` |
| `as0045` | 45 | row | “**`unit:Hertz = 1 / Seconds;`** (D-196, 1.3.3)” | `unit:Hertz = 1 / Seconds;` declares a named unit for `dim256<U>`: a `dim256<Hertz>` value compiles. | `compile` |
| `as0045b` | 45 | rule | “The RHS is unit algebra only” | A unit's right side is unit algebra only (names, `1`, `*`, `/`, parentheses): `Seconds + Seconds` is refused. | `refuse` |
| `as0049` | 49 | example | “```” | A FunctionDecl takes generics after the name, parameters, the success type, contracts and a body: `f::<int64>(1i64, 3i32)` is 3. | `run:0` |
| `as0062` | 62 | example | “```” | A generic parameter is a type or a compile-time value: `scale<comptime int32:K>` called `scale::<3i32>(2i32)` is 6. | `run:0` |
| `as0075` | 75 | rule | “**Not to be confused with `type:T`**, which is an ordinary `ParamDecl` in a” | `type:T` is legal only in a `comptime` function: as a parameter of an ordinary function it is refused. | `refuse` |
| `as0079` | 79 | rule | “**`ParamDecl` and `FieldDecl` carry memory qualifiers**” | A parameter carries a memory qualifier: `wild int8->:buf` as a parameter compiles. | `compile` |
| `as0080` | 80 | rule | “`wild int8->:buf` is a” | A field carries a memory qualifier: a struct field `wild int8->:buf;` compiles. | `compile` |
| `as0090` | 90 | rule | “**Reading a discarded parameter is an error**” | Reading a parameter declared discarded (`int32:_~x`) is an error. | `refuse` |
| `as0092` | 92 | rule | “checked as `NITPICK-TYPE-083` since 1.6.0 step 3c” | `main`'s arity is fixed: a `main` with no parameter is refused, NITPICK-TYPE-083. | `refuse:NITPICK-TYPE-083` |
| `as0092b` | 92 | rule | “the arity, the parameter's type and the `int32` return” | `main` returns `int32`: a `main` returning `int64` is refused, NITPICK-TYPE-083. | `refuse:NITPICK-TYPE-083` |
| `as0092c` | 92 | rule | “`failsafe`'s shape is `NITPICK-TYPE-044`” | `failsafe`'s shape is fixed: a `failsafe` with two parameters is refused, NITPICK-TYPE-044. | `refuse:NITPICK-TYPE-044` |
| `as0093` | 93 | rule | “`failsafe` sets the same precedent with `tbb32:err`” | `failsafe`'s one parameter is `tbb32:err`: a failsafe so declared compiles. | `compile` |
| `as0095` | 95 | rule | “`argc`: a slice carries its length (D-070)” | There is no `argc`: `main(int32:argc, cstring[]:argv)` is refused, NITPICK-TYPE-083. | `refuse:NITPICK-TYPE-083` |
| `as0098` | 98 | rule | “implicitly, except `main` and `failsafe`” | Every function but `main` and `failsafe` returns `Result<T>`: a call binds as `Result<int32>`. | `run:0` |
| `as0100` | 100 | rule | “**`extern` is not a modifier here**” | `extern` is not a function modifier: `extern func:f = …` is refused. | `refuse` |
| `as0105` | 105 | example | “```” | A variadic parameter is `..*T[]`, a slice: `total(1, 2, 3)` is 6. | `run:0` |
| `as0110` | 110 | rule | “**One form: homogeneous.**” | A variadic tail is homogeneous: an `int32` among `int64` trailing arguments is refused. | `refuse` |
| `as0120` | 120 | rule | “**removed by D-053** along with the `fmt` type itself” | The format-directed form (a bare `..*` after a `fmt` parameter) is removed: refused. | `refuse` |
| `as0124` | 124 | rule | “The surviving consumer is the `sys` builtin” | `sys(CONST, ..*int64[])` is the surviving variadic: `sys(39i64)` (getpid) returns a positive pid. | `run:0` |
| `as0128` | 128 | example | “```” | An extern function's failure contract is REQUIRED: a method with none is a compile error. | `sh:0` |
| `as0137` | 137 | example | “```” | A failure contract is `fails on …` or `never fails`: an extern method declared `never fails` compiles. | `sh:0` |
| `as0145` | 145 | rule | “**`FailsOn` and `NeverFails` are separate node kinds**” | FailsOn and NeverFails are separate node kinds. | untestable [internal] the node kinds are the parser's |
| `as0157` | 157 | row | “**`assoc:Item;`** (D-028)” | `assoc:Item;` declares an associated type in a trait, which an impl binds: `first(c)` reads it. | `run:0` |
| `as0158` | 158 | row | “**`error:Name;`** (D-179): one declared error constant” | `error:Name;` declares an error constant: a function fails with it and the caller's arm sees it. | `run:0` |
| `as0158b` | 158 | rule | “The explicit-code form (`error:Name = 4102i32;`) is the prelude's alone” | The explicit-code form `error:Name = 4102i32;` is the prelude's alone: a program's is refused. | `refuse` |
| `as0160` | 160 | rule | “**`TraitMethod` is removed. A method in a trait body is an ordinary” | A trait method is an ordinary function: one with a body is a default, one without is a declaration the impl must give. | `run:0` |
| `as0180` | 180 | row | “\| `BlockStmt` \| `stmts: Stmt[]` — introduces a scope \|” | A block introduces a scope: a local declared inside an `if` block is not visible after it. | `refuse` |
| `as0181` | 181 | row | “\| `VarDeclStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0182` | 182 | row | “\| `AssignStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0183` | 183 | row | “a bare call discards a `Result` (`TYPE-039`)” | A bare call statement that discards a `Result` is refused, NITPICK-TYPE-039. | `refuse:NITPICK-TYPE-039` |
| `as0183b` | 183 | rule | “`drop f();` / `relay f();` / `f() ?! c;` / `f() ?\\| NIL;`” | The value-less statement forms compile: `drop g();`, `relay f();`, `f() ?! c;` and `f() ?\| NIL;`. | `run:0` |
| `as0184` | 184 | row | “\| `IfStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0185` | 185 | row | “\| `PickStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0186` | 186 | row | “\| `WhileStmt` \| `label: Ident?`” | A `while` may carry a label: `break outer;` from an inner loop leaves the labelled one. | `run:0` |
| `as0187` | 187 | row | “\| `ForStmt` \|” | A `for` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `as0188` | 188 | row | “\| `LoopStmt` \|” | A `loop` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `as0189` | 189 | row | “\| `TillStmt` \|” | A `till` takes no `decreases` clause: one is always refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `as0190` | 190 | row | “\| `WhenStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0191` | 191 | row | “\| `BreakStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0192` | 192 | row | “\| `ContinueStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0193` | 193 | row | “\| `PassStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0194` | 194 | row | “\| `FailStmt` \|” | The node's fields. | untestable [internal] the node's fields; the construct itself is CONTROL's and TYPE's claims |
| `as0195` | 195 | row | “\| `ReturnStmt` \| `result: Expr` — the literal `Result{…}` form only \|” | `return` takes the literal `Result{…}` form: `return Result{ value: 5i32, err: 0i32 };` returns 5. | `run:0` |
| `as0195b` | 195 | rule | “the literal `Result{…}` form only” | `return` takes only the `Result{…}` literal: `return 5i32;` is refused. | `refuse` |
| `as0196` | 196 | row | “\| `ExitStmt` \| `code: Expr` — legal only in `main` / `failsafe` \|” | `exit` is legal only in `main` and `failsafe`: one in another function is refused. | `refuse` |
| `as0197` | 197 | row | “\| `TrapStmt` \| `error: Expr` — `!!! errCode;` \|” | `!!! errCode;` traps to failsafe with that code: `!!! E1;` reaches failsafe's `E1` arm (81). | `run:81` |
| `as0198` | 198 | row | “\| `DeferStmt` \| `body: BlockStmt` \|” | A `defer` body runs at its scope's exit: the deferred write through a pointer is seen after the call. | `run:0` |
| `as0199` | 199 | row | “`discard(e)` / `_~ e`” | A value is discarded by `discard(e)` or `_~ e`: both compile. | `compile` |
| `as0200` | 200 | row | “\| `ProveStmt` \| `condition: Expr` — **compile-time** obligation \|” | `prove` is a compile-time obligation. | untestable [z3] a `prove` obligation is discharged by `npkg verify` with the pinned z3 |
| `as0201` | 201 | row | “\| `AssertStaticStmt` \| `condition: Expr` \|” | `assert_static(cond);` is a statement: a true condition compiles and runs. | `run:0` |
| `as0201b` | 201 | rule | “`AssertStaticStmt`” | `assert_static` of a false condition is refused at compile time. | `refuse` |
| `as0202` | 202 | row | “legal only in a `PickArm` body (§2.2)” | `fall label;` is legal only in a pick arm: one in a plain block is refused. | `refuse` |
| `as0203` | 203 | row | “\| `GiveStmt` \| `value: Expr` — `give e;`, legal only in a `PickArm` body (§2.2) \|” | `give e;` is legal only in a pick arm: one in a plain block is refused. | `refuse` |
| `as0207` | 207 | rule | “**`ForStmt.binding` is a full `ParamDecl` with a required type.**” | A `for` binding needs its type: `for (i in 0i64...3i64)` is refused. | `refuse` |
| `as0210` | 210 | rule | “are **counted**, exposing the counter as `$`” | `loop` is counted and exposes its counter as `$`: the body sees `$` equal to 1 on some trip. | `run:0` |
| `as0211` | 211 | rule | “so `step` must be positive — a negative or zero step is a compile error” | A `loop` with a zero step is a compile error. | `refuse` |
| `as0211b` | 211 | rule | “a negative or zero step” | A `loop` with a negative step is a compile error. | `refuse` |
| `as0212` | 212 | rule | “Neither has an `end` block” | A `loop` has no `end` block: one is refused. | `refuse` |
| `as0213` | 213 | rule | “**`WhenStmt.then_block` runs when the body executed at least once, *including*” | `when`'s `then` runs when the body ran at least once, including after a `break`; `end` does not. | `run:0` |
| `as0214` | 214 | rule | “`end_block` runs only when the condition was false initially” | `when`'s `end` runs only when the condition was false at the start, and then `then` does not. | `run:0` |
| `as0223` | 223 | rule | “**`DeferStmt` does not run on a trap** (D-014)” | A `defer` does not run on a trap: a division by zero traps DivByZero, though the pending defer would itself have trapped IntOverflow. | `trap:DivByZero` |
| `as0228` | 228 | example | “```” | A pick arm may carry a `where` guard: a false guard passes to the next arm. | `run:0` |
| `as0236` | 236 | example | “```” | A pick pattern is a value, a range or a wildcard: 550 takes the `(500..599)` arm. | `run:0` |
| `as0239` | 239 | rule | “StructDestructure(type, binds) // (MouseClick { x, y })” | A struct destructure pattern `(MouseClick { x, y })` binds the fields. | `run:0` |
| `as0240` | 240 | rule | “EnumDestructure(path, binds)   // (Net.Disconnect(reason))” | An enum destructure pattern is written with its path: `(Net.Disconnect(reason))` binds the payload. | `run:0` |
| `as0241` | 241 | rule | “ErrPattern                     // ERR:” | `ERR:` matches the tbb error sentinel. | `run:0` |
| `as0246` | 246 | rule | “**requires** an explicit `ERR:` arm” | A `pick` on a `tbb` selector requires an explicit `ERR:` arm; `(*)` may not absorb it. | `refuse` (M10 `p12_tbb_pick_needs_err_arm`) |
| `as0248` | 248 | rule | “**There is no `Unreachable` pattern.**” | There is no `(!)` pattern: an arm written `(!)` is refused. | `refuse` |
| `as0251` | 251 | rule | “`#unreachable()`” | An arm believed unreachable has `#unreachable()` as its body, which traps when reached. | `trap:Unreachable` |
| `as0256` | 256 | rule | “`pick` must be exhaustive” | A `pick` must be exhaustive. | `refuse` (M10 `p10_int_pick_not_exhaustive`) |
| `as0256b` | 256 | rule | “A `pick` whose arms `give` is an **expression**” | A `pick` whose arms `give` is an expression: `int32:v = pick (y) { … };` initialises v. | `run:0` |
| `as0257` | 257 | rule | “must additionally agree on one type across all arms” | An expression `pick`'s arms agree on one type: an `int32` arm and an `int64` arm are refused. | `refuse` |
| `as0267` | 267 | rule | “a **semantic** restriction, not a syntactic one” | `give` outside a pick arm is refused by the checker, not the parser: the refusal is no PARSE code. | `sh:0` |
| `as0281` | 281 | row | “**suffix-form bases** (`FFhex`, `1T0t`, `2An`)” | `FFhex` is a hex literal: an `int32` bound to it is 255. | `run:0` |
| `as0281b` | 281 | rule | “`1T0t`, `2An`” | `1T0t` (balanced ternary) is 6 and `2An` (balanced nonary) is 17. | `run:0` |
| `as0281c` | 281 | rule | “A `dim256`-suffixed literal may carry a **`<UnitName>` tail**” | An integer `dim256` literal may carry a unit tail: `5dim256<Meters>` compiles. | `compile` |
| `as0282` | 282 | row | “the `dim256` unit tail as on `IntLiteral`” | A float `dim256` literal may carry a unit tail: `2.5dim256<Meters>` compiles. | `compile` |
| `as0283` | 283 | row | “**not an integer** (D-005)” | A character literal is not an integer: `int32:x = 'A';` is refused. | `refuse` |
| `as0284` | 284 | row | “\| `StringLiteral` \| escape-processed \|” | A string literal is escape-processed: `"a\tb"` is three bytes, the second a tab. | `run:0` |
| `as0285` | 285 | row | “`r"…"` — no escape processing (D-024)” | A raw string has no escape processing: `r"a\tb"` is four bytes. | `run:0` |
| `as0286` | 286 | row | “`"""…"""` — newlines preserved (D-024)” | A block string preserves its newline. | `run:0` |
| `as0287` | 287 | row | “\| `BoolLiteral` \| \|” | The BoolLiteral node. | untestable [internal] the node; LEXICAL's lx0269 tests the literals |
| `as0288` | 288 | row | “`NULL`, `NIL`, `ERR` — **not `unknown`**” | `NULL`, `NIL` and `ERR` are sentinel literals, each binding where its type is expected. | `run:0` |
| `as0289` | 289 | row | “\| `TemplateLiteral` \|” | The TemplateLiteral node's parts. | untestable [internal] the node's parts; LEXICAL's lx0383 and lx0387 test the literal |
| `as0295` | 295 | row | “\| `BinaryExpr` \| `op`, `lhs`, `rhs` \|” | The binary operators compute (all of the row's but `<=>`, which is as0295b). | `run:0` |
| `as0295b` | 295 | rule | “<=>” | `<=>` is a binary operator: `1 <=> 2` is negative. | `run:0` |
| `as0296` | 296 | row | “\| `UnaryExpr` \| `op`, `operand` \| `!` `~` `-` \|” | The unary operators `!`, `~` and `-` compute. | `run:0` |
| `as0297` | 297 | row | “\| `PostfixExpr` \| `op`, `operand` \| `++` `--` \|” | `++` and `--` are postfix operators: `x++; x--;` compiles. | `compile` |
| `as0298` | 298 | row | “yields a **second-class borrow**, not a pointer (D-004)” | `@x` is a second-class borrow: it cannot be returned out of its function. | `refuse` |
| `as0299` | 299 | row | “\| `DerefExpr` \| `operand` \| `<-ptr` \|” | `<-ptr` dereferences: a write through it reaches the local. | `run:0` |
| `as0300` | 300 | row | “`$$i` / `$$m`” | `$$m` takes a mutable borrow: a write through `$$m arr[2]` changes the element. | `run:0` |
| `as0300b` | 300 | rule | “\| `BorrowExpr` \|” | `$$i` takes an immutable borrow: reading through `$$i x` gives x. | `run:0` |
| `as0301` | 301 | row | “\| `PipeExpr` \| `direction`, `value`, `callee` \| `\\|>` / `<\\|` \|” | `\|>` and `<\|` pipe a value into a function: `4 \|> dbl` is 8 and `dbl <\| 5` is 10. | `run:0` |
| `as0302` | 302 | row | “\| `RangeExpr` \| `lo`, `hi`, `inclusive` \| `..` / `...` \|” | `..` is inclusive and `...` exclusive: the sums over 1 to 3 are 6 and 3. | `run:0` |
| `as0303` | 303 | row | “**`..^`** — expands a collection at a call site (D-026)” | `..^` expands a slice at a call site: `total(1, ..^xs)` with xs = [2, 3] is 6. | `run:0` |
| `as0304` | 304 | row | “\| `TernaryExpr` \| `cond`, `then_expr`, `else_expr` \| `is (c) : a : b` \|” | The ternary is `is (c) : a : b`. | `run:0` |
| `as0305` | 305 | row | “**`move(place)`** — transfers ownership and invalidates the source (D-065)” | `move(place)` transfers ownership: the destination holds the string. | `run:0` |
| `as0306` | 306 | row | “**`is_err(tbbValue)`** — tests a `tbb` for ERR **without trapping**” | `is_err(t)` tests a tbb for ERR without trapping: true for ERR, false for 5. | `run:0` |
| `as0307` | 307 | row | “**`Result{value: v, err: e}`** — the only way to construct a `Result`” | `Result{value: v, err: e}` constructs a Result: one with err 0 is not an error and holds v. | `run:0` |
| `as0310` | 310 | rule | “built by writing the value and emptied by writing `NIL`” | An Optional is built by writing the value and emptied by writing `NIL`. | `run:0` |
| `as0326` | 326 | rule | “Its operand is a **`tbb`**, not a `Result`” | `is_err`'s operand is a tbb, not a Result: `is_err(r)` on a Result is refused. | `refuse` |
| `as0329` | 329 | rule | “**`ok(val)`** was removed instead (D-097)” | `ok(val)` is removed: a call to it is refused. | `refuse` |
| `as0352` | 352 | rule | “Its operand is a **place**, not a value” | `move`'s operand is a place: `move(f())` is refused. | `refuse` |
| `as0360` | 360 | row | “\| `IdentifierExpr` \| `name` \|” | The IdentifierExpr node. | untestable [internal] the node |
| `as0361` | 361 | row | “**`.` only** — auto-dereferences pointers” | `.` auto-dereferences a pointer: `q.y` on a `Pt->` reads the field. | `run:0` |
| `as0361b` | 361 | rule | “`->` is type-position only (D-006)” | `->` is type-position only: `q->y` is refused. | `refuse` |
| `as0362` | 362 | row | “\| `SafeNavExpr` \| `base`, `field` \| `?.` \|” | `?.` reads a field through an Optional: a present one gives the field, an empty one NIL. | `run:0` |
| `as0363` | 363 | row | “\| `IndexExpr` \| `base`, `index` \| bounds-checked \|” | Indexing is bounds-checked: index 4 of a 4-element array traps OutOfBounds. | `trap:OutOfBounds` |
| `as0364` | 364 | row | “`generic_args` may arrive implicitly (`f<int32>(x)`)” | Generic arguments may arrive implicitly: `idt<int32>(5i32)` is a call, as `idt::<int32>(5i32)` is. | `run:0` |
| `as0365` | 365 | row | “UFCS — `p.magnitude()` resolves to `Point_magnitude(p)` (D-006)” | UFCS: with a free function `Point_magnitude(Point:p)`, `p.magnitude()` calls it. | `run:0` |
| `as0366` | 366 | row | “**`#name<T>(…)`** (D-020)” | A compiler builtin is `#name<T>(…)`: `#size_of<int32>()` is 4. | `run:0` |
| `as0367` | 367 | row | “**`comptime(expr)`** — forces compile-time resolution” | `comptime(expr)` resolves at compile time: `comptime(6i32 * 7i32)` is 42. | `run:0` |
| `as0367b` | 367 | rule | “a compile error if it cannot be resolved” | `comptime(expr)` that cannot be resolved at compile time is a compile error. | `refuse` |
| `as0384` | 384 | row | “\| **`#`-prefixed** \| `BuiltinExpr` \|” | `#`-prefixed calls are compiler builtins and macros: `#size_of<int64>()` and a user macro compile. | `run:0` |
| `as0385` | 385 | row | “\| **bare name** \| ordinary `CallExpr` \|” | The bare-name builtins are ordinary calls: `sys(39i64)` and `string_concat` are called bare. | `run:0` |
| `as0385b` | 385 | rule | “`asm`, `ok`, `is_err`” | `ok` is one of the bare-name builtins: `ok(t)` is an ordinary call. | `compile` |
| `as0403` | 403 | rule | “return `Result<T>`, and are subject to” | A bare-name builtin returns `Result<T>` like any function: `string_byte_length`'s call binds as a `Result<int64>`. | `compile` |
| `as0413` | 413 | row | “\| `SafeUnwrapExpr` \| `expr`, `default` \| `e ? d` \|” | `e ? d` unwraps with a default: `k(3i32) ? 0i32` is 3. | `run:0` |
| `as0414` | 414 | row | “\| `NullCoalesceExpr` \| `expr`, `default` \| `e ?? d` \|” | `e ?? d` gives the default for an empty Optional. | `run:0` |
| `as0415` | 415 | row | “**`e ?! code`** — exactly one `tbb32` argument (D-009)” | `e ?! code` takes exactly one `tbb32` argument: `k(3i32) ?! 5tbb32` compiles. | `compile` |
| `as0416` | 416 | row | “`?\\|` / `defaults` — **struck (D-167)**” | `?\|` is struck (D-167) and refused by name: `k(3i32) ?\| 0i32` is refused. | `refuse` |
| `as0416b` | 416 | rule | “the node is still built so the parser never restricts, and refused by name” | `defaults` is struck and refused by name: `k(3i32) defaults 0i32` is refused. | `refuse` |
| `as0417` | 417 | row | “\| `RawUnwrapExpr` \| `expr` \| `raw e` / `_! e` \|” | `raw e` and `_! e` unwrap a never-fails call. | `run:0` |
| `as0418` | 418 | row | “\| `DropExpr` \| `expr` \| `drop e` / `_? e` \|” | `drop e` and `_? e` discard a never-fails NIL call. | `compile` |
| `as0419` | 419 | row | “**`relay e` / `_^ e`** (D-080) — on error, returns the same code” | `relay e` returns the same error code from the enclosing function, and its `defer` runs. | `run:0` |
| `as0421` | 421 | rule | “**`RelayExpr` is a normal exit path**, so `defer` runs on the error branch” | `_^`'s error branch is a normal exit: the `defer` runs. | `run:0` |
| `as0422` | 422 | rule | “unlike `EmphaticUnwrapExpr`, which traps and runs nothing” | `?!` traps and runs nothing: a pending `defer` that would trap IntOverflow does not run, and failsafe sees `E1` (81). | `run:81` |
| `as0423` | 423 | rule | “It is **illegal in `main` and `failsafe`**” | `relay` is illegal in `main`: refused. | `refuse` |
| `as0432` | 432 | row | “`=>`, **compile error if loss is possible**” | `=>` is a compile error where loss is possible: `int64 => int32` is refused. | `refuse` |
| `as0433` | 433 | row | “`=>!`, the sole opt-out” | `=>!` is the opt-out: `int64 =>! int32` of 5 is 5. | `run:0` |
| `as0435` | 435 | rule | “`cast<T>` / `#cast<T>` / `@cast<T>` do not exist (D-021)” | `cast<T>(x)` does not exist: refused. | `refuse` |
| `as0435b` | 435 | rule | “`#cast<T>`” | `#cast<T>(x)` does not exist: refused. | `refuse` |
| `as0437` | 437 | rule | “**A cast target carries a memory qualifier** — `p => wild int8->`” | A cast target carries a memory qualifier: `p => wild int8->` compiles. | `compile` |
| `as0448` | 448 | row | “\| `StructLiteralExpr` \| `type`, `fields` \|” | The node's fields. | untestable [internal] the node's fields |
| `as0449` | 449 | row | “\| `ArrayLiteralExpr` \| `elements` \|” | The node's fields. | untestable [internal] the node's fields |
| `as0450` | 450 | row | “`vec3(1.0, 2.0, 3.0)`” | `vec3(1.0, 2.0, 3.0)` constructs a vector. | `compile` |
| `as0451` | 451 | row | “legal only inside `async func` (`NITPICK-040`)” | `await` is legal only inside an `async func`: one in a plain function is refused. | `refuse` |
| `as0452` | 452 | row | “`$`, legal only inside `loop` / `till`” | `$` is legal only inside `loop` and `till`: one in a `while` is refused. | `refuse` |
| `as0453` | 453 | row | “**A `=>` whose target is a `dyn` type is this node” | A `=>` whose target is a `dyn` type builds a trait object: `move(l) => dyn Speaks` compiles and dispatches. | `run:0` |
| `as0454` | 454 | row | “a `pick` whose arms `give` (D-059)” | A `pick` whose arms `give` is a PickExpr: it initialises a binding. | `run:0` |
| `as0455` | 455 | row | “legal in `ensures` and `invariant`, never nested” | `old(expr)` is legal in `ensures`: `ensures result == old(x) + 1i32` holds. | `run:0` |
| `as0455b` | 455 | rule | “never nested” | `old` is never nested: `old(old(x))` is refused. | `refuse` |
| `as0455c` | 455 | rule | “**`old(expr)`**, the operand's value at the function's ENTRY” | `old` is legal in `ensures` and `invariant` only: one in a function body is refused. | `refuse` |
| `as0456` | 456 | row | “legal in `ensures` alone” | `result` is legal in `ensures` alone: one in `requires` is refused. | `refuse` |
| `as0461` | 461 | rule | “variables are a compile error” | An uninitialised variable is a compile error: `int32:x;` then a read of x is refused. | `refuse` |
| `as0476` | 476 | rule | “**No lambda or closure nodes.** Closures are removed (D-018)” | Closures are removed: an anonymous function expression is refused. | `refuse` |
| `as0485` | 485 | row | “\| `NamedType` \| `name`, `generic_args` \| \|” | The NamedType node. | untestable [internal] the node's fields |
| `as0486` | 486 | row | “`T->` — **thin**, one word, no bounds metadata (D-038)” | A pointer is thin, one word: `#size_of<int32->>()` is 8. | `run:0` |
| `as0487` | 487 | row | “\| `OptionalType` \| `inner` \| `T?` \|” | `T?` is the Optional type: `int32?` holds 5 or NIL. | `run:0` |
| `as0488` | 488 | row | “value type; does not decay” | An array is a value type: a copy is independent of its source. | `run:0` |
| `as0488b` | 488 | rule | “does not decay” | An array does not decay to a pointer: an `int32[2]` passed for an `int32->` is refused. | `refuse` |
| `as0489` | 489 | row | “\| `FuncType` \| `params`, `return_type`, `never_fails: bool` \| D-163 \|” | The FuncType node (listed twice in the table; the second row gives the spelling). | untestable [internal] the node's fields; as0491 tests the type's spelling |
| `as0490` | 490 | row | “\| `DynType` \| `traits: TypeNode[]` \| `dyn A & B` \|” | `dyn A & B` is a trait-object type over two traits: a binding of that type compiles. | `compile` |
| `as0491` | 491 | row | “**`func RetType(ParamTypes) [never fails]`** (D-087; D-163)” | A function type is `func RetType(ParamTypes) never fails`: `f` of that type holding `twice` gives 6. | `run:0` |
| `as0491b` | 491 | rule | “a may-fail function cannot fill a `never fails` slot” | A may-fail function cannot fill a `never fails` slot: refused. | `refuse` |
| `as0492` | 492 | row | “Inhabited by string literals (checked at compile time) and by `to_cstring`” | A `cstring` is inhabited by a string literal: `cstring:c = "abc";` compiles. | `compile` |
| `as0493` | 493 | row | “**Only legal under `->`**; bare `any` is a type error” | Bare `any` is a type error: a parameter of type `any` is refused. | `refuse` |
| `as0494` | 494 | row | “`Self`, valid only in `trait` / `impl` bodies (D-030)” | `Self` is valid only in trait and impl bodies: a free function returning `Self` is refused. | `refuse` |
| `as0495` | 495 | row | “**`Mutex<Config, 2>`** — a compile-time **value** in a type-argument list” | A type-argument list holds a compile-time value: `Mutex<int64, 2i32>` is a type. | `compile` |
| `as0496` | 496 | row | “**`T.Item`** — an associated type projected from a type (D-164)” | `T.Item` projects an associated type: `first<T: Seq>` returning `T.Item` gives the counter's value. | `run:0` |
| `as0498` | 498 | rule | “Qualifiers on `VarDeclStmt`, not on the type node: `stack`, `wild`, `wildx`,” | `stack` qualifies a local: `stack int32:x = 3i32;` compiles and holds 3. | `run:0` |
| `as0499` | 499 | rule | “`const`, `fixed`” | `const` qualifies a local: `const int32:x = 3i32;` compiles. | `compile` |
| `as0499b` | 499 | rule | “**`gc` does not exist** (D-003)” | `gc` does not exist: `gc int32:x` is refused. | `refuse` |
| `as0501` | 501 | rule | “`borrow_imm` / `borrow_mut` are STRUCK” | `borrow_imm` is struck: a binding so qualified is refused. | `refuse` |
| `as0518` | 518 | rule | “**`ArrayType.size` consumed one token and called it an integer literal**” | An array's size may be a named constant: `int32[COUNT]` with COUNT = 3 holds three elements. | `run:0` |
| `as0538` | 538 | rule | “Beyond the scalar families:” | The builtin type names are the compiler's: a user struct named `Result` is refused. | `refuse` |
| `as0551` | 551 | row | “compared at every call inside the function's recursive group” | A function's `decreases` is compared at every call inside its recursive group: f and g calling each other with an unchanged measure trap DecreasesViolated. | `trap:DecreasesViolated` |
| `as0552` | 552 | row | “\| `InvariantNode` \| `conditions: Expr[]` — attached to loop statements \|” | An invariant is attached to a loop: one that fails traps InvariantViolated. | `trap:InvariantViolated` |
| `as0553` | 553 | row | “`limit<r_pos>` on a declaration, a parameter” | `limit<r_pos>` on a parameter: passing -1 traps LimitViolated. | `trap:LimitViolated` |
| `as0554` | 554 | row | “the `never fails` contract on an ordinary function, trait method, impl method” | `never fails` rides an ordinary function and a function type alike. | `run:0` |
| `as0555` | 555 | row | “Constant-expression only” | `joins` takes a constant expression only: a call as the deadline is refused. | `refuse` |
| `as0556` | 556 | row | “A channel-returning function without it is a getter” | A channel-returning function without `gives` is a getter: creating a channel inside one is refused. | `refuse` |
| `as0557` | 557 | row | “Orthogonal to `never fails`: a pure function may `fail`” | A `pure` function may `fail`: `pure` without `never fails` compiles, and its failure reaches the caller. | `run:0` |
| `as0558` | 558 | row | “a clause found after `invariant`, the wrong order, TYPE-072” | The termination clause comes before `invariant`: `invariant P decreases E` is refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `as0563` | 563 | rule | “A `decreases` measure admits neither” | A `decreases` measure admits neither `result` nor `old`: `decreases old(i)` is refused. | `refuse` |
| `as0571` | 571 | example | “```” | An attribute attaches to a declaration: `#[derive(Clone)]` on a struct compiles. | `compile` |
| `as0572` | 572 | rule | “#[align(16)]” | `#[align(16)]` is an attribute: a struct carrying it compiles. | `compile` |
| `as0575` | 575 | rule | “not `@derive` (D-020)” | Derive is not `@derive`: `@derive(Clone)` is refused. | `refuse` |
| `as0583` | 583 | rule | “`#[lexical_drop]` and `#[nll_drop]` are **removed**” | `#[lexical_drop]` is removed: a struct carrying it is refused. | `refuse` |
| `as0593` | 593 | row | “\| `PinExpr` (`#obj`) \|” | Pinning is removed: `#obj` on a value is refused. | `refuse` |
| `as0594` | 594 | row | “\| `LAMBDA` / closure capture \| closures removed (D-018) \|” | Closures are removed: a nested function capturing a local is refused. | `refuse` |
| `as0595` | 595 | row | “\| `gc` in `memory_modifier` \| no collector (D-003) \|” | There is no `gc` memory modifier: a `gc` local is refused. | `refuse` |
| `as0596` | 596 | row | “positional `.a` / `.b` / `.c` \| replaced by named fields \|” | The nodes' positional slots are replaced by named fields. | untestable [internal] the parser's node layout |
| `as0597` | 597 | row | “\| `end` block on `LOOP_STMT` / `TILL_STMT` \| only `when` has one (D-027) \|” | A `till` has no `end` block: one is refused. | `refuse` |
| `as0598` | 598 | row | “\| `a*` collection builtins \|” | The `a*` collection builtins are not the language's: `astack()` is refused. | `refuse` |
| `as0621` | 621 | rule | “**settled by D-058: internal” | `Future<T>` is an internal lowering artifact: no construct produces one. | untestable [vague] the sentence names no construct whose refusal a program could check |
| `as0635` | 635 | rule | “**Resolved as: modifier + `comptime(expr)`, no block.**” | There is no `comptime { … }` block: one is refused. | `refuse` |
| `as0643` | 643 | rule | “`FunctionDecl.modifiers` already” | `comptime` is a function modifier: `comptime func:sq` forced by `comptime(sq(5i32))` is 25. | `run:0` |

## BUILD (`meta/specs/BUILD_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `bd0015` | 15 | row | “\| **`npkc`** \| the compiler — one module set to one object, or to one artifact \|” | npkc compiles one module set to one object or artifact. | untestable [vague] the row names a role; what npkc emits (text, D-067) is bd0175's claim |
| `bd0016` | 16 | row | “\| **`npkg`** \| the driver — reads the manifest” | npkg reads the manifest: in a directory with none, `npkg build` refuses and names `nitpick.toml`. | `sh:0` |
| `bd0018` | 18 | rule | “**Naming discrepancy to settle.**” | The package manager is `npkg`, not `npkpkg`. | untestable [tree] a note about the compiler repository's CLAUDE.md |
| `bd0027` | 27 | rule | “One schema (D-077). Six tables” | The manifest has six tables and the `[[test]]` array. | untestable [vague] the sentence lists the schema; bd0462-bd0464 test the `[[test]]` keys it refuses |
| `bd0030` | 30 | example | “```toml” | The example manifest (nlibc, with `[dependencies]`, `[verify]` and `[limits]`) is one `npkg` builds. | untestable [tool] `npkg build` reads the floor's `runtime/npkrt.ll` from the manifest's root, so a project outside the compiler's repository does not build (measured in a scratch project before the extraction) |
| `bd0036` | 36 | rule | “PLANNED, read by nothing today” | `target` is planned and read by nothing. | untestable [tool] what a build makes of `target` needs a build that completes (bd0030) |
| `bd0066` | 66 | rule | “`target` is READ BY” | Every build is one executable from `[build] entry`; `target` is read by nothing. | untestable [tool] needs a completed build (bd0030) |
| `bd0072` | 72 | rule | “**`[project]` is identity, `[build]` is settings.**” | `entry` lives in `[build]`, not `[project]`. | untestable [vague] the sentence states the schema's split; it names no refusal |
| `bd0074` | 74 | rule | “**`[toolchain]` is an INPUT, not a setting** (D-204)” | The toolchain is a build input: a manifest with no `[toolchain]` pin is refused, naming the toolchain. | `sh:0` |
| `bd0075` | 75 | rule | “version is an EXACT PATCH RELEASE: a minor-version pin is insufficient” | The pin is an exact patch release: `llvm = "20.1"` (a minor-version pin) is refused. | `sh:0` |
| `bd0079` | 79 | rule | “the thing that runs them rather than restated there” | The flag lists are read by the tool that runs them. | untestable [tool] which flags llc and opt were run with is visible only in a completed build (bd0030) |
| `bd0088` | 88 | rule | “**`[verify]` belongs in the manifest**” | The verification flags are the manifest's `[verify]`, not the command line's. | untestable [z3] `npkg verify` needs the pinned z3 |
| `bd0095` | 95 | rule | “**The solver is an INPUT like the toolchain**” | Both runners refuse a mismatched z3 version or hash, no `rlimit=`, or a wall-clock knob. | untestable [z3] needs the pinned z3 and `npkg verify` |
| `bd0112` | 112 | rule | “**There is no `edition` key** (D-077)” | There is no `edition` key: a manifest with `edition = "2024"` is refused. | `sh:0` |
| `bd0118` | 118 | rule | “`nitpick.lock` records, for every dependency in the transitive graph” | The lock records every dependency's exact version and content hash, and is committed. | untestable [tool] dependencies bind nothing today (bd0161); the lock's rows are never written |
| `bd0121` | 121 | rule | “`npkg build` **reads the lock and never writes it.**” | `npkg build` never writes the lock: a build refused for a missing lock leaves no `nitpick.lock` behind. | `sh:0` |
| `bd0122` | 122 | rule | “error, not an invitation to resolve” | A missing lock is an error, not an invitation to resolve: `npkg build` refuses, naming `nitpick.lock`. | `sh:0` |
| `bd0126` | 126 | rule | “## 2. A build never touches the network” | A build never touches the network; resolution is `npkg update`'s alone. | untestable [platform] a build's network use is not observable here; bd0453 tests `npkg update` |
| `bd0154` | 154 | row | “\| `use "./util.npk"` , `use "../x/y.npk"` \| the **importing file's** directory \|” | A `../` path resolves against the importing file's directory. | `sh:0` |
| `bd0155` | 155 | row | “\| `use "nfs/path.npk"` \| the **dependency roots** \|” | A path not starting with `.` resolves against the dependency roots only: with no dependency, `use "nfs/path.npk"` is refused even with the file beside the importer. | `sh:0` |
| `bd0156` | 156 | row | “\| `use std.math.*` \| the standard library \|” | `use std.math.*;` is the standard library's path: the program compiles. | `compile` |
| `bd0158` | 158 | rule | “A dependency named `nfs` declared at `../nfs` roots at **`../nfs/src/`**” | A dependency at `../nfs` roots at `../nfs/src/`. | untestable [tool] dependencies bind nothing today (bd0161); the root is never formed |
| `bd0161` | 161 | rule | “the dependency-root form is PLANNED, not” | Today `use "dep/thing.npk"` is NITPICK-RESOLVE-005. | `refuse:NITPICK-RESOLVE-005` |
| `bd0167` | 167 | rule | “**An ambiguous path is an error, not a first match.**” | Two dependencies supplying one path fail the build, naming both. | untestable [tool] dependencies bind nothing today (bd0161) |
| `bd0175` | 175 | rule | “Per D-067 the compiler **emits text and invokes tools**; it links nothing.” | npkc emits LLVM IR text and links nothing: its output is a text `.ll`, and no object or executable appears. | `sh:0` |
| `bd0177` | 177 | example | “```” | The build pipeline: module graph, npkc to .ll, opt, llc at opt-level, the undefined-symbol scan, ld.lld. | untestable [tool] `npkg build`'s pipeline needs a project in the compiler's tree (bd0030) |
| `bd0187` | 187 | rule | “**The undefined-symbol scan is a permanent pipeline step” | Every object is scanned and the build fails on an undefined symbol outside the runtime's allowlist. | untestable [tool] the scan is `npkg build`'s (bd0030); a Nitpick program cannot name an outside symbol |
| `bd0195` | 195 | rule | “**An unreferenced prelude item is not emitted (D-262 §1, 1.5.2d).**” | An unreferenced prelude item is not emitted: a program that calls nothing has a few defines, and no `string_concat`. | `sh:0` |
| `bd0215` | 215 | rule | “**The scan's reader is `npkg`'s own**” | The scan reads the object's ELF symbol table itself, against the runtime's exports. | untestable [tree] the scan's implementation and its counts |
| `bd0235` | 235 | rule | “Verification, where `[verify]` requests it, runs against the IR and the source” | Verification runs over SMT-LIB2 text to z3. | untestable [z3] needs the pinned z3 |
| `bd0238` | 238 | rule | “A failure in any subprocess is a nonzero exit status the driver reports” | A subprocess's failure is a nonzero exit the driver reports. | untestable [tool] needs a build that reaches its subprocesses (bd0030) |
| `bd0242` | 242 | rule | “**`llc` must be invoked at the manifest's `opt-level`” | llc is invoked at the manifest's opt-level. | untestable [tool] needs a completed build (bd0030) |
| `bd0249` | 249 | rule | “**Every emitted function checks its stack (D-305, 1.5.8 step 2).**” | Every define the compiler writes carries "split-stack": a program's own function does. | `ir:^define [^\n]*@"npk\.bd0249\.helper"\([^\n]*"split-stack"` |
| `bd0252` | 252 | rule | “The floor's object carries two linker” | The floor's object carries the notes `.note.GNU-split-stack` and `.note.GNU-no-split-stack`. | `sh:0` |
| `bd0260` | 260 | rule | “floor's own functions carry no prologue” | The floor's own functions carry no split-stack prologue. | untestable [internal] the floor's machine code |
| `bd0268` | 268 | rule | “A unit that does not define `failsafe` DECLARES `@npk_failsafe`” | A unit that does not define `failsafe` declares `@npk_failsafe`, so a non-root module compiled alone assembles: llc accepts it. | `sh:0` |
| `bd0269` | 269 | rule | “a generic's body is exported with its module, instantiation happens in the” | A generic's body is exported with its module and instantiated in the user; identical specialisations fold at link time. | untestable [tool] needs a multi-object link that `npkg` performs (bd0030) |
| `bd0272` | 272 | rule | “Whole-program compilation is available as an opt-in” | Whole-program compilation is an opt-in for release and verification builds. | untestable [vague] the sentence names no switch |
| `bd0277` | 277 | rule | “**A verification build and a release build are always clean builds.**” | Verification and release builds are always clean. | untestable [tool] needs `npkg verify` and a release build (bd0030) |
| `bd0290` | 290 | rule | “**The same inputs produce a byte-identical output** (D-078).” | The same input produces a byte-identical emission, wherever it is compiled: one program compiled in two directories gives two identical `.ll` files. | `sh:0` |
| `bd0292` | 292 | rule | “No timestamps, build paths, hostnames, or environment values in the artifact.” | The emission carries no build path: the `.ll` names no part of the directory it was compiled in. | `sh:0` |
| `bd0295` | 295 | rule | “D-064's mangled names are readable and reversible with **no hash**” | A generic instance's name is readable, with no hash: `idt` instantiated at `int32` is named by both. | `sh:0` |
| `bd0299` | 299 | rule | “driver refuses a mismatching toolchain loudly” | The driver refuses a mismatching toolchain: a pin of 20.1.1 with 20.1.2 installed is refused. | `sh:0` |
| `bd0300` | 300 | rule | “A `repro` check builds twice from different working directories” | A repro check builds twice from different directories and byte-compares the emissions. | untestable [tree] the harness's check; bd0290 does the same over a program |
| `bd0303` | 303 | rule | “**The pin is a version, and a version is not a binary**” | The pin is a version; the cross-machine claim is the compiler's own emission; every ladder run prints its sha256 report. | untestable [tool] the ladder's report is `npkg build`'s in the compiler's tree (bd0030) |
| `bd0335` | 335 | row | “\| **Seed** \|” | A stage of the bootstrap ladder. | untestable [tree] the compiler's own bootstrap |
| `bd0336` | 336 | row | “\| **1** \|” | A stage of the bootstrap ladder. | untestable [tree] the compiler's own bootstrap |
| `bd0337` | 337 | row | “\| **2** \|” | A stage of the bootstrap ladder. | untestable [tree] the compiler's own bootstrap |
| `bd0339` | 339 | rule | “**Self-hosting is the fixpoint of the compiler's emission of itself**” | Self-hosting: stage N and stage N+1 emit the compiler byte-identically. | untestable [tool] needs the compiler's own build ladder |
| `bd0351` | 351 | rule | “**Declared at 1.4.9 (2026-09-02).**” | The fixpoint held at 1.4.9. | untestable [tree] a record of the compiler's history |
| `bd0362` | 362 | rule | “**The prototype `npkc` is not the seed** (D-085, superseding D-079).” | The prototype is not the seed. | untestable [tree] the compiler's bootstrap |
| `bd0368` | 368 | rule | “**The parser never restricts; the backend does.**” | The parser accepts the whole grammar; a construct the backend cannot lower is a backend diagnostic. | untestable [vague] since D-271 no construct is refused by rung; no program can tell the parser's acceptance from the checker's here |
| `bd0374` | 374 | rule | “The seed is **invoked once, ever**” | The seed is invoked once. | untestable [tree] the compiler's bootstrap |
| `bd0379` | 379 | rule | “**What the fixpoint does not prove.**” | The fixpoint does not exclude a seed backdoor. | untestable [tree] a statement about the bootstrap |
| `bd0397` | 397 | rule | “They interact in one place.” | The capability ladder meets the bootstrap at self-hosting. | untestable [tree] the compiler's plan |
| `bd0402` | 402 | rule | “**Subset 1 is what the two ladders share.**” | Subset 1's contents. | untestable [tree] the compiler's own sources' subset |
| `bd0416` | 416 | rule | “**Once stage 2 exists, primitives are implemented in Nitpick.**” | Primitives are implemented in Nitpick after self-hosting. | untestable [tree] the compiler's sources |
| `bd0432` | 432 | row | “\| build with the current compiler \|” | A pass of an ABI change's rebuild. | untestable [tool] the compiler's own rebuild |
| `bd0433` | 433 | row | “\| build again with that one \|” | A pass of an ABI change's rebuild. | untestable [tool] the compiler's own rebuild |
| `bd0434` | 434 | row | “\| build a third time \|” | A pass of an ABI change's rebuild. | untestable [tool] the compiler's own rebuild |
| `bd0451` | 451 | row | “\| `npkg build` \| reads lock + vendored source” | `npkg build` reads the lock: with none, it refuses with D-078's sentence, "a missing lock is an error". | `sh:0` |
| `bd0452` | 452 | row | “\| `npkg test` \| builds the compiler” | `npkg test` builds the compiler, runs the self-check and every `[[test]]` in order. | untestable [tool] `npkg test` builds the compiler's ladder first, longer than a script's 60 s; bd0462-bd0464 test its refusals before anything runs |
| `bd0453` | 453 | row | “\| `npkg update` \| PLANNED — refused today by name” | `npkg update` is refused today by name: "there is nothing to resolve in a single-repository world". | `sh:0` |
| `bd0454` | 454 | row | “\| `npkg verify` \| the ladder, then the VERIFIED build” | `npkg verify` runs the verified build. | untestable [z3] needs the pinned z3 |
| `bd0462` | 462 | rule | “entry a runner cannot honour is refused BY NAME before anything runs” | An entry with a stage the runner does not know is refused by name before anything runs, exit 2. | `sh:0` |
| `bd0463b` | 463 | rule | “never skipped: a stage it does not know, a `kind` on a stage that has none” | A `kind` on a stage that has none is refused by name, exit 2. | `sh:0` |
| `bd0464` | 464 | rule | “compile entry with no kind, no `paths`/`path` (or both), a key the schema lacks” | A compile entry with no `kind` is refused by name, exit 2. | `sh:0` |
| `bd0464b` | 464 | rule | “no `paths`/`path` (or both)” | An entry with both `path` and `paths` is refused by name, exit 2. | `sh:0` |
| `bd0464c` | 464 | rule | “a key the schema lacks” | An entry with a key the schema lacks is refused by name, exit 2. | `sh:0` |
| `bd0466` | 466 | example | “```toml” | Three `[[test]]` entries: conformance (compile, positive), types (check, recursive), programs. | untestable [tool] running the entries needs the compiler's ladder first (bd0452) |
| `bd0487` | 487 | row | “\| `compile` (the default) \|” | `compile` is a stage the runner knows (an entry with it is refused for its bad kind, not its stage). | `sh:0` |
| `bd0488` | 488 | row | “\| `parse` \| `tools/parse_check` \|” | `parse` is a stage the runner knows. | `sh:0` |
| `bd0489` | 489 | row | “\| `resolve` \| `tools/resolve_check` \|” | `resolve` is a stage the runner knows. | `sh:0` |
| `bd0490` | 490 | row | “\| `check` \| `tools/check` \|” | `check` is a stage the runner knows. | `sh:0` |
| `bd0491` | 491 | row | “\| `accept` \| `tools/check` \| accepted in silence \|” | `accept` is a stage the runner knows. | `sh:0` |
| `bd0492` | 492 | row | “\| `fixture` \| the compiler under test \|” | `fixture` is a stage the runner knows. | `sh:0` |
| `bd0493` | 493 | row | “\| `program` \| the compiler under test \|” | `program` is a stage the runner knows. | `sh:0` |
| `bd0494` | 494 | row | “\| `runtime` \| `llc` + `ld.lld` \|” | `runtime` is a stage the runner knows. | `sh:0` |
| `bd0495` | 495 | row | “\| `verify` \| the compiler under test, z3 \|” | `verify` is a stage the runner knows. | `sh:0` |
| `bd0496` | 496 | row | “\| `cost` \| the compiler under test, the runtime's `NPK_HEAP_STATS` \|” | `cost` is a stage the runner knows. | `sh:0` |
| `bd0497` | 497 | row | “\| `explore` \| the compiler under test, the explored floor, the shim \|” | `explore` is a stage the runner knows. | `sh:0` |
| `bd0499` | 499 | rule | “Membership stays with the stage” | A file another file imports is skipped as a fixture. | untestable [tool] needs a run of `npkg test` (bd0452) |
| `bd0506` | 506 | rule | “**Expectations live in the test file**” | Expectations live in the test file. | untestable [tree] a convention of the compiler's tests |
| `bd0509` | 509 | example | “```nitpick” | The expectation markers: expect-error, -at, expect-note, expect-exit, stress, argv, expect-no-parse-error, expect-obligation. | untestable [tool] the markers are read by `npkg test` and the harness (bd0452) |
| `bd0529` | 529 | rule | “`CODE path:line:col: message` (1.0.8), with `note ` or `warning ` in front” | A diagnostic renders as `CODE path:line:col: message`, with `note ` in front of a note. | `sh:0` |
| `bd0531` | 531 | rule | “place of the position for a spanless diagnostic (D-162)” | A spanless diagnostic renders `<no span>` in place of the position. | untestable [vague] the text names no diagnostic that has no span |
| `bd0536` | 536 | rule | “**A finding at a `<derived-N>` line fails the unit**” | A finding at a `<derived-N>` line fails the unit. | untestable [tool] a rule of `npkg test` (bd0452) |
| `bd0544` | 544 | rule | “**A negative test with no `expect-error` is a failing test.**” | A negative test with no expect-error fails. | untestable [tool] a rule of `npkg test` (bd0452) |
| `bd0547` | 547 | rule | “**Unexpected diagnostics fail a test as surely as missing ones.**” | An unexpected diagnostic fails a test. | untestable [tool] a rule of `npkg test` (bd0452) |
| `bd0576` | 576 | rule | “**A `verify` test names its rows exactly**” | A verify test names its rows exactly. | untestable [z3] a verify test's rows |
| `bd0585` | 585 | rule | “**The elided IR is an inventory**” | The elided IR's traps and assumes are counted by group. | untestable [z3] needs the verified build |
| `bd0618` | 618 | rule | “**`expect-no-parse-error` is the load-bearing one.**” | expect-no-parse-error asserts the file reached the backend. | untestable [tool] a marker `npkg test` reads |
| `bd0623` | 623 | rule | “**The suite it was written for retired at 1.5.4 step 4” | tests/rejection/ retired at 1.5.4. | untestable [tree] the compiler's test tree |
| `bd0634` | 634 | rule | “**The harness is itself tested.**” | The harness's self-check feeds it wrong expectations and requires each to fail. | untestable [tool] `npkg test --selfcheck` builds the compiler first (bd0452) |
| `bd0646` | 646 | rule | “**Parity between the runners is measured, not assumed**” | The parity stage diffs the two runners' verdicts. | untestable [tree] the harness's stage |
| `bd0653` | 653 | rule | “**The descriptor ceiling (1.5.1b step 5).**” | A runner lowers its soft RLIMIT_NOFILE to `[limits] nofile` before it spawns anything. | untestable [tool] observable only in programs a run of `npkg test` spawns (bd0452) |
| `bd0669` | 669 | rule | “**Test-target declaration.**” | Settled: see §7.1. | untestable [tree] a settled open item |

## BUILTIN (`meta/specs/BUILTIN_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `bi0003` | 3 | rule | “available globally without needing to `use`” | Built-ins are callable with no declaration and no import. | `run:0` |
| `bi0003b` | 3 | rule | “map directly to LLVM instructions or safe runtime shims” | Built-ins map to LLVM instructions or runtime shims. | untestable [vague] a description of the lowering with no outcome a program can check |
| `bi0005` | 5 | rule | “You must explicitly import them via the `collections` module” | Collections (stacks, lists, hash tables) are not built in: using one without importing the `collections` module is refused. | `refuse` |
| `bi0010` | 10 | rule | “the 1-based index of the ARGUMENT WHOSE STORAGE THE RESULT” | string_bytes's result aliases its argument: returning the view of a local string is refused as a borrow escaping (D-004 rule 2). | `refuse` |
| `bi0017` | 17 | rule | “rule A (laundered through a call)” | A view laundered through a call (rule A) is still a borrow of its root: returning it from the root's function is refused. | `refuse` |
| `bi0018` | 18 | rule | “the range-view `arr[lo...hi]` gets the” | A range view arr[lo...hi] of a local array is a borrow: returning it is refused. | `refuse` |
| `bi0019` | 19 | rule | “This column is the ONE authority on aliasing for” | The Views column is the one authority on aliasing for builtins. | untestable [tree] a statement about which table the compiler's generator reads |
| `bi0024` | 24 | rule | “`<!-- builtins:begin -->` and `<!-- builtins:end -->` markers define the” | The marked regions define the bare-name builtin set, generated into builtins.npk by gen_tables.py. | untestable [tree] a statement about the compiler's generator and source tree |
| `bi0027` | 27 | rule | “That set is deliberately small (0.8.4)” | The builtin set is the floor, sys and the three comptime-foldable string names; everything else here is nlibc's, imported like any module. | untestable [vague] the set's membership is tested row by row, and the non-builtin names at lines 189-220 |
| `bi0035` | 35 | rule | “One row per builtin, and nothing but rows” | The generator reads only the marked regions' table rows and hard-fails on a missing name. | untestable [tree] the generator's behaviour |
| `bi0039` | 39 | rule | “`<!-- rtsyms:begin -->` … `<!-- rtsyms:end -->` (§2d) is the OTHER region” | The rtsyms region lists emitter-called symbols that are not builtins and never resolve as names. | untestable [tree] where the table is read; the resolution claim is tested at line 300 |
| `bi0048` | 48 | rule | “whose name is a row's name in a `builtins` region is” | A module-level function named after a builtin is NITPICK-RESOLVE-001 at its declaration. | `refuse:NITPICK-RESOLVE-001` |
| `bi0048b` | 48 | rule | “inline module or out” | A `pub` function named after a builtin, inside an inline module, is NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `bi0049` | 49 | rule | “`NITPICK-RESOLVE-001` at the declaration; so is an `extern` block's METHOD of” | An extern block's method named after a builtin is NITPICK-RESOLVE-001. | untestable [tool] an extern block needs a driver interface (MODULE_REFERENCE §5); its spelling is MODULE's claims' |
| `bi0051` | 51 | rule | “METHOD is exempt” | A method named after a builtin is accepted (it is reached through its receiver). | `run:0` |
| `bi0052` | 52 | rule | “a module-level BINDING cannot carry a” | A module-level binding cannot carry a function value (TYPE-035). | `refuse:NITPICK-TYPE-035` |
| `bi0054` | 54 | rule | “CALLABLE binding (D-296)” | Inside a function, a local of function type named after a builtin is NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `bi0054b` | 54 | rule | “a parameter, a local, a `for` binding or a `pick`” | A function-typed PARAMETER named after a builtin is NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `bi0057` | 57 | rule | “a binding of any other type may (`int64:read` cannot be” | A binding of a non-function type may take a builtin's name. | `run:0` |
| `bi0058` | 58 | rule | “and so may a function-typed FIELD, which is reached through its” | A function-typed field named after a builtin is accepted, and called through its receiver. | `run:0` |
| `bi0060` | 60 | rule | “RESERVES A NAME in every program” | Every row added to a marked region reserves a name in every program. | untestable [tree] a rule for the compiler's maintainers; its consequence is tested at lines 48-58 |
| `bi0070` | 70 | example | “```” | The Signature column's grammar: params → type, a param optionally `move`. | untestable [tree] the grammar gen_tables.py reads; the signatures' meaning is tested row by row |
| `bi0076` | 76 | rule | “The arrow is U+2192” | The signature arrow is U+2192; `->` inside a type is the pointer suffix. | untestable [tree] the document's notation |
| `bi0077` | 77 | rule | “A memory qualifier (`wild`, `wildx`, `stack`) is” | A memory qualifier is not part of a type: a `wild int8->` value binds to a plain `int8->`. | `run:0` |
| `bi0080` | 80 | rule | “`Result<T>` appears exactly when the Fails” | A `never fails` builtin's call types as the bare value: it binds with no unwrap. | `run:0` |
| `bi0081` | 81 | rule | “column says the builtin may fail” | A may-fail builtin's call types as Result<T>: binding it to the bare type is refused. | `refuse` |
| `bi0082` | 82 | rule | “The generator refuses a row where the two columns” | gen_tables.py refuses a row whose Signature and Fails columns disagree. | untestable [tree] the generator's behaviour |
| `bi0085` | 85 | rule | “The `**ABI:**` note” | A row's ABI note is the whole vocabulary of symbol departures. | untestable [tree] the document's notation; each row's note is tested where it names an emitted symbol |
| `bi0090` | 90 | row | “\| `inline` \|” | `inline`: no floor symbol; string_is_empty lowers to a length compare, with no call. | `ir!:call [^\n]*@npk_string_is_empty` |
| `bi0091` | 91 | row | “``sym=`@memcpy` ``” | `sym=`: the symbol is not @npk_<name>. | untestable [tree] the document's notation; mcpy's symbol is tested at line 133 |
| `bi0092` | 92 | row | “``ret=`{ ptr, ptr, i64, i64, i64 }` ``” | `ret=`: the LLVM return differs from the derived one. | untestable [tree] the document's notation; arena_make's is tested at line 146 |
| `bi0093` | 93 | row | “``args=`ptr, i32, i64` ``” | `args=`: the LLVM arguments differ from the derived ones. | untestable [tree] the document's notation; memset's is tested at line 135 |
| `bi0094` | 94 | row | “\| `envelope` \|” | `envelope`: a never-fails builtin whose symbol answers { T, i32 }, the value half extracted at the call. | untestable [internal] how a call's return is unpacked; the bare typing it gives is tested at line 80 |
| `bi0096` | 96 | rule | “Everything not noted is DERIVED” | check_runtime_sigs_agree diffs the derived ABI against runtime/npkrt.ll on every harness run. | untestable [tree] the harness's check |
| `bi0102` | 102 | rule | “classified by each row's IR body or inline lowering, never its prose” | The Pure column is classified from each row's IR body or inline lowering, never from its prose. | untestable [tree] how the column is written; each row's purity is tested through TYPE-060/061 at lines 105-112 |
| `bi0105` | 105 | rule | “`pure` body (`NITPICK-TYPE-061`) and a contract expression” | A `pure` body admits the pure rows (string_bytes, string_from_bytes' kin, string_equals, string_byte_length, string_is_empty). | `run:0` |
| `bi0105b` | 105 | rule | “(`NITPICK-TYPE-061`)” | A `pure` body refuses an effect row by name (TYPE-061): int_to_string allocates. | `refuse:NITPICK-TYPE-061` |
| `bi0106` | 106 | rule | “(`NITPICK-TYPE-060`) admit the `pure` rows and refuse the rest by name” | A contract expression admits a pure row: `requires !string_is_empty(s)` compiles and is checked. | `run:0` |
| `bi0106b` | 106 | rule | “and refuse the rest by name” | A contract expression refuses an effect row (TYPE-060): int_to_string in a `requires`. | `refuse:NITPICK-TYPE-060` |
| `bi0107` | 107 | rule | “Five rows are `pure`” | string_from_bytes is a pure row: a pure body may call it. | `run:0` |
| `bi0109` | 109 | rule | “Everything that allocates (the allocator family,” | string_concat is an effect row: a pure body calling it is refused TYPE-061. | `refuse:NITPICK-TYPE-061` |
| `bi0112` | 112 | rule | “a descriptor, the clock” | mono_now (the clock) is an effect row: a pure body calling it is refused TYPE-061. | `refuse:NITPICK-TYPE-061` |
| `bi0115` | 115 | rule | “A row's classification is a claim about its floor body” | A row's Pure classification is a claim about its floor body. | untestable [tree] a statement about the classification's source |
| `bi0122` | 122 | rule | “They all return `wild` pointers” | An allocation is unmanaged: a block still live at `exit 0` traps WildLeak (the programmer must free it). | `trap:WildLeak` |
| `bi0122b` | 122 | rule | “There is no garbage collector (D-003)” | There is no garbage collector. | untestable [unobservable] an absence; the leak check at line 122 is its consequence |
| `bi0123` | 123 | rule | “every allocation carries a hidden 16-byte header” | Every allocation carries a hidden 16-byte header: size and a secret-keyed magic word. | untestable [internal] the header's layout; reading below a block is outside every guarantee |
| `bi0123b` | 123 | rule | “Double-free, corruption, and a foreign or misaligned pointer trap to” | A double free the analysis cannot follow traps to failsafe with -4102 (Unreachable). | `trap:Unreachable` |
| `bi0123c` | 123 | rule | “OOM with `-4103`” | An allocation the kernel cannot back traps HeapOom (-4103): 2^47 bytes is legal and fails. | `trap:HeapOom` |
| `bi0123d` | 123 | rule | “a malformed request (negative size” | A negative size is a malformed request: HeapBadRequest (-4104). | `trap:HeapBadRequest` |
| `bi0123e` | 123 | rule | “checked `calloc` multiply overflow” | A calloc whose count*size overflows is a malformed request: HeapBadRequest. | `trap:HeapBadRequest` |
| `bi0123f` | 123 | rule | “`ralloc(p, 0)`” | ralloc(p, 0) is a malformed request: HeapBadRequest. | `trap:HeapBadRequest` |
| `bi0123g` | 123 | rule | “bad alignment) with `-4104`” | A bad alignment (not a power of two) is a malformed request: HeapBadRequest. | `trap:HeapBadRequest` |
| `bi0123h` | 123 | rule | “Double-free of a tracked binding is already a compile-time error (D-119)” | Freeing one binding twice is a compile-time error. | `refuse` |
| `bi0127` | 127 | row | “\| `alloc` \|” | alloc(0) is a real, unique, freeable block. | `run:0` |
| `bi0128` | 128 | row | “\| `alloc_managed` \|” | alloc_managed is prelude-only: a program's call is refused TYPE-054. | `refuse:NITPICK-TYPE-054` |
| `bi0129` | 129 | row | “\| `aalloc` \|” | aalloc allocates with a requested power-of-two alignment; the block is usable and freeable. | `run:0` |
| `bi0130` | 130 | row | “\| `calloc` \|” | calloc allocates count*size ZERO-initialised bytes. | `run:0` |
| `bi0131` | 131 | row | “\| `ralloc` \|” | ralloc resizes and copies the old contents (bounded by the old size); ralloc(NULL, n) is a fresh allocation. | `run:0` |
| `bi0132` | 132 | row | “\| `dalloc` \|” | dalloc(NULL) traps -4102 (Unreachable). | `trap:Unreachable` |
| `bi0133` | 133 | row | “\| `mcpy` \|” | mcpy copies n bytes from src to dst. | `run:0` |
| `bi0133b` | 133 | row | “**ABI:** sym=`@memcpy`” | mcpy's symbol is @memcpy. | `ir:@memcpy\b|@llvm\.memcpy` |
| `bi0134` | 134 | row | “\| `mmov` \|” | mmov is overlap-safe: moving bytes 0..7 to 1..8 in one block keeps them in order. | `run:0` |
| `bi0134b` | 134 | row | “**ABI:** sym=`@memmove`” | mmov's symbol is @memmove. | `ir:@memmove\b|@llvm\.memmove` |
| `bi0135` | 135 | row | “\| `memset` \|” | memset fills n bytes with the LOW 8 bits of val. | `run:0` |
| `bi0135b` | 135 | row | “**ABI:** sym=`@memset` args=`ptr, i32, i64`” | memset's symbol is @memset (or the llvm.memset intrinsic it maps to). | `ir:@memset\b|@llvm\.memset` |
| `bi0141` | 141 | rule | “a page is never writable and” | W^X: a page is never writable and executable at once, so an unsealed (writable) page cannot run: calling it faults. | `trap:MachineFault` |
| `bi0146` | 146 | row | “\| `arena_make` \|” | arena_make builds an arena for T from the annotation, with no element-type argument. | `run:0` |
| `bi0146b` | 146 | row | “ret=`{ ptr, ptr, i64, i64, i64 }` args=`i64, i64`” | arena_make's symbol is @npk_arena_make, returning { ptr, ptr, i64, i64, i64 } from (i64, i64). | `ir:\{ ptr, ptr, i64, i64, i64 \} @npk_arena_make\(i64[^,)]*, i64[^,)]*\)` |
| `bi0147` | 147 | row | “\| `shared_arena_make` \|” | shared_arena_make builds the atomically-shared arena from the annotation. | `run:0` |
| `bi0148` | 148 | row | “\| `atomic_from_ptr` \|” | atomic_from_ptr::<T> aliases existing wild memory as an atomic, used as a method's receiver. | `run:0` |
| `bi0148b` | 148 | row | “a declaration or assignment storing the result is refused (TYPE-007)” | Storing atomic_from_ptr's result in a declaration is refused TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `bi0148c` | 148 | row | “**`wild`-context only** (D-187)” | atomic_from_ptr is wild-context only: over the address of a plain local it is refused. | `refuse` |
| `bi0149` | 149 | row | “\| `wild_live_count` \|” | wild_live_count is the number of live wild allocations. | `run:0` |
| `bi0150` | 150 | row | “\| `clone_exec` \|” | clone_exec refuses a child-bound descriptor below 4 with an error, before anything is claimed. | `run:0` |
| `bi0151` | 151 | row | “\| `driver_retire` \|” | Retiring a registry slot that is not active traps -4102 (Unreachable). | `trap:Unreachable` |
| `bi0152` | 152 | row | “\| `wild_release_all` \|” | The statement after wild_release_all() must be `exit`: anything else is TYPE-062. | `refuse:NITPICK-TYPE-062` |
| `bi0152b` | 152 | row | “`argv` and `environ()`'s arrays live outside it (1.5.1b step 0)” | wild_release_all followed by exit is legal, and argv and environ() stay readable after it. | `run:0` |
| `bi0153` | 153 | row | “\| `wildx_alloc` \|” | wildx_alloc gives writable pages; filled with code, sealed and called, the code runs. | `run:0` |
| `bi0154` | 154 | row | “\| `wildx_seal` \|” | After wildx_seal the pages are not writable: a store faults (MachineFault). | `trap:MachineFault` |
| `bi0155` | 155 | row | “\| `wildx_call` \|” | wildx_call passes its int64 argument to the sealed code and returns its int64 result. | `run:0` |
| `bi0156` | 156 | row | “\| `wildx_free` \|” | wildx_free releases W^X pages; the program then exits cleanly. | `run:0` |
| `bi0160` | 160 | rule | “`malloc` and `free` are not builtins and are not aliases” | `malloc` is not a builtin: a call to it is refused. | `refuse` |
| `bi0160b` | 160 | rule | “and are not aliases” | `free` is not a builtin: a call to it is refused. | `refuse` |
| `bi0162` | 162 | rule | “there is no `extern "libc"` to declare them in” | In-process FFI does not exist: an `extern "libc"` block is refused. | `refuse` |
| `bi0163` | 163 | rule | “the WHOLE allocator API” | The natives above are the whole allocator API (five since aalloc). | untestable [unobservable] an absence; malloc and free are tested at line 160 |
| `bi0173` | 173 | rule | “Everything in this section arrives as ordinary Nitpick functions in” | §2's string functions are nlibc's ordinary functions, not builtins (bar §2c's three). | untestable [vague] tested name by name at lines 189-220 |
| `bi0180` | 180 | rule | “UNCLAIMED today” | No library in the ecosystem builds the nlibc string surface. | untestable [tree] a statement about the ecosystem's libraries |
| `bi0181` | 181 | rule | “None of these names resolves” | None of §2's names resolves unless it also has a row in a marked table. | untestable [vague] tested name by name at lines 189-220 |
| `bi0189` | 189 | rule | “`string_length(str)`” | `string_length` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0190` | 190 | rule | “`string_byte_length(str)`” | string_byte_length (a row of §2c) resolves and is the byte length: "héllo" is 6 bytes. | `run:0` |
| `bi0191` | 191 | rule | “`string_char_count(str)`” | `string_char_count` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0192` | 192 | rule | “`string_is_empty(str)`” | string_is_empty (a row of §2c) is true exactly when the length is 0. | `run:0` |
| `bi0193` | 193 | rule | “`string_is_valid_utf8(str)`” | `string_is_valid_utf8` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0196` | 196 | rule | “`string_equals(a, b)`” | string_equals is a byte-equal comparison. | `run:0` (M10 `t17_string_equals`) |
| `bi0197` | 197 | rule | “`string_contains(str, needle)`” | `string_contains` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0198` | 198 | rule | “`string_starts_with(str, prefix)`” | `string_starts_with` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0199` | 199 | rule | “`string_ends_with(str, suffix)`” | `string_ends_with` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0200` | 200 | rule | “`string_index_of(str, needle)`” | `string_index_of` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0201` | 201 | rule | “`string_last_index_of(str, needle)`” | `string_last_index_of` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0204` | 204 | rule | “`string_concat(a, b)`” | string_concat (a row of §2b) concatenates two strings. | `run:0` |
| `bi0205` | 205 | rule | “`string_substring(str, start, end)`” | `string_substring` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0206` | 206 | rule | “`string_count(str, needle)`” | `string_count` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0207` | 207 | rule | “`string_replace(str, needle, replacement)`” | `string_replace` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0208` | 208 | rule | “`string_repeat(str, n)`” | `string_repeat` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0211` | 211 | rule | “`string_trim(str)`” | `string_trim` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0212` | 212 | rule | “`string_trim_start(str)`” | `string_trim_start` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0212b` | 212 | rule | “`string_trim_end(str)`” | `string_trim_end` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0213` | 213 | rule | “`string_to_upper(str)`” | `string_to_upper` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0213b` | 213 | rule | “`string_to_lower(str)`” | `string_to_lower` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0214` | 214 | rule | “`string_pad_left(str, len, char)`” | `string_pad_left` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0214b` | 214 | rule | “`string_pad_right(str, len, char)`” | `string_pad_right` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0217` | 217 | rule | “`string_from_int(val)`” | `string_from_int` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0217b` | 217 | rule | “`string_to_int(str)`” | `string_to_int` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0218` | 218 | rule | “`string_from_int_hex(val)`” | `string_from_int_hex` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0219` | 219 | rule | “`string_from_char(byte)`” | `string_from_char` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0220` | 220 | rule | “`string_format_float(val, precision)`” | `string_format_float` is planned nlibc surface with no row in a marked table: it does not resolve (line 181). | `refuse` |
| `bi0228` | 228 | rule | “The functions `runtime/npkrt.ll` defines and every backend rung can” | The floor's functions are bare-name builtins, callable everywhere with no declaration. | untestable [vague] tested row by row below |
| `bi0234` | 234 | rule | “`check_runtime_sigs_agree` diffs all three on every harness run” | Three copies of the floor's signature set exist and check_runtime_sigs_agree diffs them. | untestable [tree] the compiler's source tree and harness |
| `bi0238` | 238 | row | “\| `string_concat` \|” | string_concat concatenates; an empty result allocates nothing. | `run:0` (M10 `t15_concat_empty`) |
| `bi0238b` | 238 | row | “also comptime-folds” | string_concat folds at compile time: it initialises a module `fixed` string. | `run:0` |
| `bi0239` | 239 | row | “\| `int_to_string` \|” | int_to_string renders an int64 in decimal and never fails. | `run:0` (M10 `t10_int_to_string`) |
| `bi0240` | 240 | row | “\| `string_slice` \|” | string_slice is byte-indexed and half-open. | `run:0` (M10 `t05_slice_half_open`) |
| `bi0240b` | 240 | row | “**an OWNED COPY** (D-186)” | string_slice returns an owned copy: the slice outlives the string it was cut from. | `run:0` |
| `bi0240c` | 240 | row | “An empty slice allocates nothing” | An empty slice allocates nothing. | `run:0` heap `0/0/0` |
| `bi0241` | 241 | row | “\| `string_bytes` \|” | string_bytes is the string's bytes as a view: same length, same bytes, no copy (no allocation). | `run:0` heap `*/*/1` |
| `bi0241b` | 241 | row | “The slice is a borrow (D-070)” | The bytes view is bounds-checked against its run-time length. | `run:94` (M10 `t07_bytes_view_bounds`) |
| `bi0242` | 242 | row | “\| `string_from_bytes` \|” | string_from_bytes' length is held to [0, 2^47]: a negative length traps OutOfBounds. | `trap:OutOfBounds` |
| `bi0242b` | 242 | row | “wraps existing bytes as a view (cap 0)” | string_from_bytes wraps existing bytes as a view with cap 0, the bytes the pointer names. | `run:0` |
| `bi0242c` | 242 | row | “the length is held to `[0, 2^47]`” | A length above 2^47 traps OutOfBounds. | `trap:OutOfBounds` |
| `bi0243` | 243 | row | “\| `to_cstring` \|” | to_cstring is a NUL-terminated copy: the length excludes the NUL, which follows the bytes. | `run:0` |
| `bi0244` | 244 | row | “\| `read_file` \|” | read_file reads a whole file. | `run:0` |
| `bi0245` | 245 | row | “\| `read_stdin` \|” | read_stdin reads the whole stream: an empty stdin gives an empty string, successfully. | `run:0` |
| `bi0246` | 246 | row | “\| `environ` \|” | environ() is the process environment's KEY=VALUE entries: under an empty environment it is empty. | `run:0` |
| `bi0247` | 247 | row | “\| `path_exists` \|” | path_exists never fails: an existing path answers true, a missing one false. | `run:0` |
| `bi0248` | 248 | row | “\| `mono_now` \|” | mono_now is CLOCK_MONOTONIC nanoseconds: it never goes backwards. | `run:0` |
| `bi0249` | 249 | row | “\| `hardware_concurrency` \|” | hardware_concurrency is at least 1 and at most 1024. | `run:0` |
| `bi0249b` | 249 | row | “Asked at each call, never cached” | hardware_concurrency follows the affinity mask at each call: pinned to one CPU it answers 1. | `run:0` |
| `bi0250` | 250 | row | “\| `buffer_new` \|” | buffer_new(n) is n zeroed bytes with len == cap == n; n <= 0 is the empty buffer. | `run:0` |
| `bi0250b` | 250 | row | “the cell drops at scope exit exactly as a string does” | A buffer drops at scope exit: 1000 buffers of 1000 bytes made in turn peak at 1000 live bytes. | `run:0` heap `1000000/1000/1000` |
| `bi0251` | 251 | row | “\| `channel` \|” | channel() reads element, level and capacity from the annotation and returns a Result. | `run:0` |
| `bi0251b` | 251 | row | “Allocates, so it returns a `Result`” | channel() returns a Result: binding it bare is refused. | `refuse` |
| `bi0252` | 252 | row | “\| `mutex` \|” | mutex(v) builds a Mutex from the annotation holding v, as a Result. | `run:0` |
| `bi0253` | 253 | row | “\| `rwlock` \|” | rwlock(v) builds an RwLock holding v: a reader sees v. | `run:0` |
| `bi0254` | 254 | row | “\| `condvar` \|” | condvar() builds a CondVar from the annotation, as a Result. | `run:0` |
| `bi0255` | 255 | row | “\| `barrier` \|” | barrier() builds a Barrier of N arrivals from the annotation: with N = 1 one arrival passes. | `run:0` |
| `bi0256` | 256 | row | “\| `suspend_until` \|” | suspend_until is legal only inside an async function: in a sync function it is refused. | `refuse` |
| `bi0256b` | 256 | row | “parks the TASK until an absolute monotonic timepoint” | suspend_until parks the task until the deadline: at least that long passes. | `run:0` |
| `bi0257` | 257 | row | “\| `suspend_io` \|” | suspend_io parks until the descriptor is ready or the deadline: a readable descriptor returns before a far deadline. | `run:0` |
| `bi0258` | 258 | row | “\| `io_unwatch` \|” | Removing an unwatched descriptor is a no-op, not an error. | `run:0` |
| `bi0259` | 259 | row | “\| `io_watch` \|” | io_watch registers a descriptor without parking; it is then unwatched. | `run:0` |
| `bi0260` | 260 | row | “\| `own_fd` \|” | own_fd takes ownership: the owner's drop closes the descriptor. | `run:0` |
| `bi0261` | 261 | row | “\| `release_fd` \|” | close(release_fd(move o)) consumes the owner and closes once, reporting close's verdict. | `run:0` |
| `bi0261b` | 261 | row | “the move defuses the drop, so no double close is” | After release_fd(move o), `o` is moved: a use of it is refused. | `refuse` |
| `bi0261c` | 261 | row | “consumes the owner and returns the bare number” | release_fd consumes the owner and returns the bare descriptor, so close sees it once and succeeds. | `run:0` |
| `bi0262` | 262 | row | “\| `chain_depth` \|” | chain_depth counts the sites the in-flight error's origin chain has passed. | `run:42` |
| `bi0263` | 263 | row | “\| `chain_site` \|” | chain_site(i) is 0 outside the kept range. | `run:42` |
| `bi0264` | 264 | row | “\| `site_line` \|” | site_line(0) is 0: the runtime's reserved site 0. | `run:0` |
| `bi0265` | 265 | row | “\| `site_path` \|” | site_path(0) is empty. | `run:0` |
| `bi0266` | 266 | row | “\| `write_file` \|” | write_file writes the whole buffer, replacing what was there. | `run:0` |
| `bi0267` | 267 | row | “\| `open` \|” | open is one openat at AT_FDCWD: a relative path opens relative to the working directory. | `run:0` |
| `bi0268` | 268 | row | “\| `close` \|” | A failed close is reported, never swallowed: a second close of one descriptor is an error. | `run:0` |
| `bi0269` | 269 | row | “\| `read` \|” | End of input is the error E_EOF (IoEof), never a zero in the value channel. | `run:0` |
| `bi0269b` | 269 | row | “Zero asked is zero delivered” | A read of zero bytes delivers zero, successfully. | `run:0` |
| `bi0270` | 270 | row | “\| `write` \|” | write is one kernel write returning the bytes taken. | `run:0` |
| `bi0272` | 272 | rule | “Error slots across the floor carry the kernel's own negative codes” | A floor error carries the kernel's code: a missing file's read_file error is ENOENT (NotFound). | `run:0` |
| `bi0274` | 274 | rule | “an interior NUL is −22” | to_cstring of a string with an interior NUL is an error. | `run:0` (M10 `t12_to_cstring_interior_nul`) |
| `bi0274b` | 274 | rule | “−22, a slice out of range −34” | The codes are -22 (interior NUL) and -34 (a slice out of range). | untestable [unobservable] a program compares an error only with a declared identity, the explicit-code form is the prelude's alone (AST_REFERENCE:158), and the prelude declares none for 22 or 34; that each is an error is tested at bi0274 and M10's t06 |
| `bi0274c` | 274 | rule | “a slice out of range −34” | A slice out of range is an error of string_slice. | `run:0` (M10 `t06_slice_out_of_range`) |
| `bi0275` | 275 | rule | “end-of-input is E_EOF = −4096” | E_EOF is -4096, the first code past the kernel's error space, so it collides with no errno. | untestable [unobservable] the numeric value; IoEof's identity at end of input is tested at line 269 |
| `bi0277` | 277 | rule | “−4098 INT_MIN_OVERFLOW” | INT_MIN / -1 reaches failsafe through the trap route (DivOverflow). | `run:98` (M10 `v05_min_div_minus_one`) |
| `bi0277b` | 277 | rule | “−4099 OUT_OF_BOUNDS” | An array index past the end reaches failsafe as OutOfBounds, not through a Result. | `trap:OutOfBounds` |
| `bi0277c` | 277 | rule | “−4097 DIV_BY_ZERO” | An integer division by zero reaches failsafe as DivByZero. | `trap:DivByZero` |
| `bi0278` | 278 | rule | “(a slice or array index past the end, D-070), and −4100 TBB_ERR (an ERR value” | An ERR tbb value at a bare comparison reaches failsafe as TbbErr. | `trap:TbbErr` |
| `bi0280` | 280 | rule | “Positive codes” | Positive codes belong to programs. | untestable [vague] an allocation of the code space; a program's own error identities are hashed, not chosen |
| `bi0285` | 285 | rule | “The three string names the compiler EVALUATES during `comptime` folding” | The compiler evaluates §2c's three names during comptime folding. | untestable [vague] tested per row below |
| `bi0290` | 290 | row | “\| `string_equals` \|” | string_equals folds at comptime: it initialises a module `fixed` bool. | `run:0` |
| `bi0291` | 291 | row | “\| `string_byte_length` \|” | string_byte_length is the byte length. | `run:0` (M10 `t01_byte_length_utf8`) |
| `bi0291b` | 291 | row | “Folds at comptime. **ABI:** inline” | string_byte_length folds at comptime: it initialises a module `fixed` int64. | `run:0` |
| `bi0292` | 292 | row | “\| `string_is_empty` \|” | string_is_empty folds at comptime: it initialises a module `fixed` bool. | `run:0` |
| `bi0300` | 300 | rule | “no program names them, the resolver admits” | The runtime symbols the emitter calls are not names: a program calling `arena_alloc` is refused. | `refuse` |
| `bi0311` | 311 | row | “\| `arena_alloc` \|” | Every emitted module declares @npk_arena_alloc as { i64, i32 } (ptr, i64). | `ir:^declare \{ i64, i32 \} @npk_arena_alloc\(ptr[^,)]*, i64[^,)]*\)` |
| `bi0312` | 312 | row | “\| `arena_at` \|” | Every emitted module declares @npk_arena_at as ptr (ptr, i64, i64, i32). | `ir:^declare ptr @npk_arena_at\(ptr[^,)]*, i64[^,)]*, i64[^,)]*, i32[^,)]*\)` |
| `bi0313` | 313 | row | “\| `arena_free` \|” | Every emitted module declares @npk_arena_free as i32 (ptr, i64, i64, i32). | `ir:^declare i32 @npk_arena_free\(ptr[^,)]*, i64[^,)]*, i64[^,)]*, i32[^,)]*\)` |
| `bi0314` | 314 | row | “\| `arena_reset` \|” | Every emitted module declares @npk_arena_reset as void (ptr, i64). | `ir:^declare void @npk_arena_reset\(ptr[^,)]*, i64[^,)]*\)` |
| `bi0315` | 315 | row | “\| `arena_destroy` \|” | Every emitted module declares @npk_arena_destroy as void (ptr). | `ir:^declare void @npk_arena_destroy\(ptr[^,)]*\)` |
| `bi0316` | 316 | row | “\| `sarena_bump` \|” | Every emitted module declares @npk_sarena_bump as i64 (ptr, i64). | `ir:^declare i64 @npk_sarena_bump\(ptr[^,)]*, i64[^,)]*\)` |
| `bi0317` | 317 | row | “\| `sarena_slot` \|” | Every emitted module declares @npk_sarena_slot as ptr (ptr, i64, i64). | `ir:^declare ptr @npk_sarena_slot\(ptr[^,)]*, i64[^,)]*, i64[^,)]*\)` |
| `bi0318` | 318 | row | “\| `sarena_destroy` \|” | Every emitted module declares @npk_sarena_destroy as void (ptr). | `ir:^declare void @npk_sarena_destroy\(ptr[^,)]*\)` |
| `bi0319` | 319 | row | “\| `exit` \|” | Every emitted module declares @npk_exit as void (i32). | `ir:^declare void @npk_exit\(i32[^,)]*\)` |
| `bi0323` | 323 | rule | “`arena_alloc`'s `{ i64, i32 }` is a `Handle<T>`, NOT a `Result`” | An arena's alloc() answers a Handle<T>, not a Result: it binds with no unwrap. | `run:0` |
| `bi0337` | 337 | row | “\| `sys` \|” | sys reaches any syscall; the kernel's negative returns land in the error slot. | `run:0` |
| `bi0341` | 341 | rule | “The call TYPES as `Result<int64>`” | A sys call types as Result<int64>: a wrong annotation over it is refused like any typed Result's. | `refuse` |
| `bi0344` | 344 | rule | “register: integer-family at 64 bits or below” | A sys argument that does not fit a kernel register (a string) is refused. | `refuse` |
| `bi0346` | 346 | rule | “at most” | At most six register arguments follow the syscall number: seven are refused. | `refuse` |
| `bi0348` | 348 | rule | “resolve (a nested bare-builtin call) is refused with "bind it to a typed” | An argument that is a nested bare-builtin call is refused (bind it to a typed name first). | `refuse` |
| `bi0350` | 350 | rule | “unsigned one or a kernel identifier ZERO-extends into its register” | At the trampoline a signed argument sign-extends and an unsigned one zero-extends: lseek to int32 -1 fails, to uint32 0xFFFFFFFF succeeds. | `run:0` |
| `bi0368` | 368 | rule | “Restricting which syscalls a binary may make is **`--seccomp`**'s job” | The compiler has a `--seccomp` option (a kernel-enforced allowlist). | `sh:0` |
| `bi0375` | 375 | rule | “`--extra-picky=no-sys` bans direct syscalls” | `--extra-picky=no-sys` refuses a program that calls sys; without it the program compiles. | `sh:0` |
| `bi0378` | 378 | rule | “**`asm!!` is spelled `asm`** (D-046)” | `asm!!` no longer exists: it is refused. | `refuse` |
| `bi0379` | 379 | rule | “`!!` no longer exists in the language” | `!!` no longer exists: `sys!!(...)` is refused. | `refuse` |
| `bi0381` | 381 | rule | “**`sys!!!` is removed** (D-001)” | `sys!!!` is removed: it is refused. | `refuse` |
| `bi0384` | 384 | rule | “Both remaining tiers are `Result`-wrapped” | Every function but main and failsafe returns Result<T>: a fallible function's result bound bare is refused. | `refuse` |
| `bi0386` | 386 | rule | “`raw` / `_!` remains the single explicit, greppable bypass” | `_!` is the other spelling of `raw`: it unwraps a never-fails call. | `run:0` |
| `bi0394` | 394 | rule | “`#` is the **compiler-directive sigil**” | `#` marks what is addressed to the compiler. | untestable [vague] tested through the forms below |
| `bi0399` | 399 | row | “\| `#name<T>(...)` \| builtin producing a value \|” | `#name<T>(...)` is a builtin producing a value: #size_of<int64>() is a value. | `run:0` |
| `bi0400` | 400 | row | “\| `#name(...)` \| **macro invocation** (D-046) — replaces `name!(args)` \|” | The old macro invocation `name!(args)` is replaced by `#name(args)`: `name!(args)` is refused. | `refuse` |
| `bi0401` | 401 | row | “\| `#[name(...)]` \| attribute annotating a declaration \|” | `#[name(...)]` annotates a declaration: #[derive(Eq)] on a struct derives ==. | `run:0` |
| `bi0403` | 403 | rule | “**`@` is never a builtin prefix.**” | `@` is never a builtin prefix: `@sizeof(int64)` is refused. | `refuse` |
| `bi0408` | 408 | rule | “**Except casting**, which has no builtin form at all” | A cast has no builtin form: `#cast<int64>(x)` is refused (the operators are => and =>!). | `refuse` |
| `bi0409` | 409 | rule | “`@cast_unchecked<T>` become the operators **`=>`** and **`=>!`** (D-021)” | `@cast<T>(x)` is not a cast; `x => T` is. | `refuse` |
| `bi0416` | 416 | row | “\| `#size_of<T>` \|” | #size_of<T> is T's size in bytes, known at compile time. | `run:0` |
| `bi0417` | 417 | row | “\| `#wild_ptr<T>(addr)` \|” | #wild_ptr<T>(addr) constructs a pointer from an integer address, in wild context. | `run:0` |
| `bi0417b` | 417 | row | “**Legal only in `wild` context**” | #wild_ptr is legal only in wild context: into a binding not declared `wild` it is refused (D-019's reading). | `refuse` |
| `bi0418` | 418 | row | “\| `#wild_slice<T>(ptr, len)` \|” | #wild_slice's count is held to [0, 2^47]: a negative count traps OutOfBounds. | `trap:OutOfBounds` |
| `bi0418b` | 418 | row | “TYPE-061 keeps it out of `pure` bodies” | #wild_slice is refused in a pure body (TYPE-061). | `refuse:NITPICK-TYPE-061` |
| `bi0418c` | 418 | row | “STRUCK by D-315 (2026-09-23)” | #wild_slice is no longer wild-context only: a slice over a plain pointer compiles. | `run:0` |
| `bi0419` | 419 | row | “\| `#ptr_add<T>(ptr, offset)` \|” | #ptr_add<T>'s offset is in elements of T: #ptr_add<int64>(p, 1) advances eight bytes. | `run:0` |
| `bi0419b` | 419 | row | “**Legal only in `wild` context** — pointer arithmetic is the manual regime's” | #ptr_add is legal only in wild context: over a buffer's pointer, outside wild, it is refused. | `refuse` |
| `bi0420` | 420 | row | “\| `#sqrt(x)` \|” | #sqrt of a negative operand yields NaN, with no error channel. | `run:0` (M10 `f03_sqrt_of_negative`) |
| `bi0420b` | 420 | row | “`flt32`/`flt64` only, by refusal” | #sqrt of an integer is refused. | `refuse` |
| `bi0420c` | 420 | row | “it lowers to `llvm.sqrt.f32`/`f64`” | #sqrt lowers to the llvm.sqrt intrinsic. | `ir:@llvm\.sqrt\.f64` |
| `bi0421` | 421 | row | “\| `#unreachable()` \|” | #unreachable() traps UNREACHABLE (-4102) when reached. | `trap:Unreachable` |
| `bi0421b` | 421 | row | “Takes no arguments” | #unreachable takes no arguments: #unreachable(1i32) is refused. | `refuse` |
| `bi0428` | 428 | rule | “Nitpick supports direct inline assembly for `x86_64` and `aarch64` targets” | Inline assembly is supported for x86_64 (and aarch64). | untestable [vague] tested through the row and the example below; aarch64 is another platform |
| `bi0432` | 432 | row | “\| `asm<T>(arch, code, constraints, args)` \|” | asm<T> wraps the output in Result<T>; a negative integer return is an error. | `run:0` |
| `bi0434` | 434 | rule | “**`asm!!!` is removed** (D-001)” | `asm!!!` is removed: it is refused. | `refuse` |
| `bi0439` | 439 | example | “```nitpick” | The example: x86_64 assembly adding 1 to its input, returning Result<int32>. | `run:0` |

Tables whose rows are not claims:

- line 357: the original three syscall tiers, removed by D-001 and D-048: history; the current rules are tested at lines 375-386

## CONCURRENCY (`meta/specs/CONCURRENCY_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `cc0020` | 20 | row | “native `async` / `await`, coroutines” | Asynchronous execution is native `async`/`await`: an async function that suspends (sleeps) and resumes is awaited from `async main` and yields its value. | `run:0` |
| `cc0021` | 21 | row | “standard library only, no language keywords” | System threading uses no language keywords, so `thread` is an ordinary identifier. | `run:0` |
| `cc0027` | 27 | rule | “Every thread runs an executor” | Every thread runs an executor: a thread's body spawns a task, awaits the channel it fills, and reports the value plus one. | `run:0` |
| `cc0027b` | 27 | rule | “waiting is always a task-level event” | Waiting is a task-level event: main waiting in `recv` does not stop a sibling task on the same thread from running and sending the value main waits for. | `run:0` |
| `cc0035` | 35 | rule | “blocking-versus-async split in the API” | There is no blocking form of a channel operation: `ch.recv(d)` without `await` is refused. | `refuse` |
| `cc0042` | 42 | example | “```nitpick” | The declaring-and-awaiting example compiles as written and exits 0. | `run:0` |
| `cc0053` | 53 | rule | “functions return `Result<T>` like every other function, so the result” | An awaited async call is a `Result<T>` that must be unwrapped: binding it straight to `int32` is refused. | `refuse` |
| `cc0053b` | 53 | rule | “`async` functions return `Result<T>`” | An awaited async call binds as `Result<int32>` and carries the callee's value. | `run:0` |
| `cc0055` | 55 | rule | “callee can never be `never fails`” | An `async` function can never be `never fails`: declaring one is refused. | `refuse` |
| `cc0056` | 56 | rule | “so `raw await f(…)` is unlicensed by” | `raw await f()` is unlicensed: it is refused. | `refuse` |
| `cc0059` | 59 | example | “```nitpick” | The three honest spellings (relay, `?\| fallback`, `?! 9tbb32`) compile, and each yields the callee's value when it succeeds. | `run:0` |
| `cc0060` | 60 | rule | “relay await fetch_data(url);      // propagate” | `relay await` propagates the callee's error verbatim as the caller's own. | `run:0` |
| `cc0061` | 61 | rule | “?\| fallback;     // default” | `await f() ?\| d` yields d when the call fails and the value when it succeeds. | `run:0` |
| `cc0062` | 62 | rule | “?! 9tbb32;       // trap” | `await f() ?! 9tbb32` on a failing call traps to failsafe with code 9, which no named arm matches, so the catch-all arm answers. | `run:99` |
| `cc0065` | 65 | rule | “is valid only inside an `async func`” | `await` in a synchronous function is refused. | `refuse` |
| `cc0066` | 66 | rule | “hard compile error, `NITPICK-040`” | `await` in a synchronous function is refused with the code NITPICK-040. | `refuse:NITPICK-040` |
| `cc0070` | 70 | rule | “and discarding the result spawns” | Calling an async function without `await` and discarding the result spawns it: the spawned task runs and delivers its value through a channel. | `run:0` |
| `cc0073` | 73 | example | “```nitpick” | `drop work();` spawns an async function whose VALUE is discarded: a value-returning async callee is accepted in the spawn form. | `run:0` |
| `cc0079` | 79 | rule | “the enclosing scope's D-062 join” | A spawned task's error reaches the join and becomes the enclosing async function's own error. | `run:0` |
| `cc0080` | 80 | rule | “after every child has finished” | The join relays the first child error verbatim, and only after every child has finished: a slower sibling's value is already in the channel when the parent returns. | `run:0` |
| `cc0081` | 81 | rule | “a task wound up by the join's deadline reports its wind-up” | A task wound up by the join's deadline reports its wind-up code as the enclosing async function's error, the way a child error does. | `run:0` |
| `cc0082` | 82 | rule | “A spawned task's error is observable or the program does not” | Spawning where no error can be observed does not compile: `drop work()` in a synchronous function is refused. | `refuse` |
| `cc0091` | 91 | rule | “The task runs” | The spawned task runs concurrently with its spawner: it waits for a value the spawner sends after spawning it, and answers. | `run:0` |
| `cc0092` | 92 | rule | “does not return until it has” | A spawned task cannot outlive its scope: the enclosing async function does not return until the task has finished, so its value is in the channel when the function returns. | `run:0` |
| `cc0097` | 97 | rule | “taking a normal” | A task the scope-exit join winds up observes the request at its next await and takes a normal error exit, so its `defer` runs (here the defer divides by zero). | `trap:DivByZero` |
| `cc0098` | 98 | rule | “The deadline is a property of the executor, fixed” | The join deadline is a property of the executor, fixed where the executor is created, not repeated at every spawn. | untestable [vague] the section gives no construct that sets an executor's deadline; `joins` appears only in LEXICAL_REFERENCE, never in this reference |
| `cc0100` | 100 | rule | “There is no unbounded join, and expiry **traps to” | There is no unbounded join: a thread that outlives its join deadline traps to failsafe (DeadlineExceeded) instead of being detached or waited for. | `trap:DeadlineExceeded` |
| `cc0108` | 108 | rule | “There is no cancellation operation.” | There is no operation that cancels a task. | untestable [unobservable] no task can be named (D-058), so no program can even form a call to a cancel operation; cc0143 tests that the spawn's result cannot be held |
| `cc0115` | 115 | rule | “A task resumes on the thread it suspended on.” | A task resumes on the thread it suspended on (no migration, no work-stealing): its gettid is the same after every await, while two other threads are busy. | `run:0` |
| `cc0130` | 130 | rule | “lowers to `@llvm.coro` state machines” | `async` lowers to `@llvm.coro` state machines: the emitted IR uses llvm.coro intrinsics. | `ir:@llvm\.coro\.` |
| `cc0132` | 132 | example | “```llvm” | `Future<T>` is the handle `%Future = type { ptr, ptr }` (coroutine handle, result slot) in the emitted IR of an async program. | `ir:%Future = type \{ ptr, ptr \}` |
| `cc0136` | 136 | rule | “Each thread's executor owns an `arena<T>` from which task frames are” | Each thread's executor allocates task frames from its own single-threaded arena, released on task completion. | untestable [internal] where a frame's bytes come from is the runtime's business; no program-visible operation distinguishes an executor arena from the heap |
| `cc0141` | 141 | rule | “is an internal lowering artifact, not surface syntax” | `Future<T>` is not surface syntax: a parameter of type `Future<int32>` is refused. | `refuse` |
| `cc0142` | 142 | rule | “yields `T` directly” | `await f()` yields `T` directly: `int32:x = await f(..)` compiles and x is the value. | `run:0` |
| `cc0143` | 143 | rule | “a user can neither name it nor hold it” | The result of an un-awaited async call cannot be held: binding `work()` is refused. | `refuse` |
| `cc0146` | 146 | rule | “fan-out and collect” | Fan-out and collect goes through a channel: three spawned tasks send their squares on one channel and main collects 1+4+9. | `run:0` |
| `cc0151` | 151 | rule | “no `spawn` or `go` keyword” | There is no `spawn` keyword: `spawn` is an ordinary identifier. | `run:0` |
| `cc0151b` | 151 | rule | “no `spawn` or `go` keyword” | There is no `go` keyword: `go` is an ordinary identifier. | `run:0` |
| `cc0151c` | 151 | rule | “no `sync` keyword” | There is no `sync` keyword and the compiler rejects it: a `sync` function modifier is refused. | `refuse` |
| `cc0153` | 153 | rule | “barriers are standard-library abstractions” | Threads, mutexes, condition variables, rwlocks and barriers are standard-library abstractions, not language constructs. | untestable [tree] where the primitives are implemented is a fact about the source tree; note LEXICAL_REFERENCE §4 lists Mutex, Guard, RwLock, RGuard, CondVar, Barrier as BuiltinType keywords and `thread` as a keyword |
| `cc0167` | 167 | rule | “supplies the primitives.” | libn's syscall layer wraps futex (12 uses), clone (5), gettid, tkill, set_robust_list. | untestable [tree] a count of call sites in the archived prototype's source |
| `cc0187` | 187 | rule | “The three carrying **direct** C shims are already marked deprecated” | The three prototype modules with direct C shims are marked deprecated in their source. | untestable [tree] a statement about the archived prototype's files |
| `cc0194` | 194 | rule | “Only `mutex`, `rwlock`, and `condvar` are genuinely” | Of the prototype's modules only mutex, rwlock and condvar are free of C dependencies. | untestable [tree] a statement about the archived prototype's imports |
| `cc0207` | 207 | rule | “records the full read” | meta/CONCURRENCY_STDLIB_AUDIT.md records the full read of the prototype modules. | untestable [tree] a statement about a document in the compiler repository |
| `cc0220` | 220 | rule | “language type emitting native LLVM atomic IR with no shim” | `atomic<T>` emits native LLVM atomic IR: `fetch_add` appears as an `atomicrmw add`. | `ir:atomicrmw add ` |
| `cc0220b` | 220 | rule | “with no shim” | `atomic<T>` needs no shim: the program's IR names no `*shim*` symbol. | `ir!:@[\w.$]*shim` |
| `cc0243` | 243 | example | “```nitpick” | The three ways to obtain an atomic compile as written: scope storage, a struct field, and `atomic_from_ptr<int32>(hdr_ptr)` bound to a local. | `run:0` |
| `cc0244` | 244 | rule | “atomic<int32>:counter = 0i32;” | An atomic may live in the enclosing scope, initialised from a plain value, and is usable there. | `run:0` |
| `cc0247` | 247 | rule | “atomic<int64>:hits;” | An atomic may be a struct field, and its methods work through the field. | `run:0` |
| `cc0250` | 250 | rule | “atomic_from_ptr<int32>(hdr_ptr);   // alias existing memory” | `atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr)` aliases existing memory: a store through lk is what the pointer reads. | `run:0` |
| `cc0253` | 253 | rule | “`atomic_new(0i32)` is **removed**” | `atomic_new(0i32)` is removed (there is no allocating constructor): it is refused. | `refuse` |
| `cc0258` | 258 | rule | “Where an aliased address originates as an integer it must be converted with” | An integer address must be converted with `#wild_ptr<T>` first: passing an int64 straight to `atomic_from_ptr` is refused. | `refuse` |
| `cc0259b` | 259 | rule | “`#wild_ptr<T>(addr)` in `wild` context” | An integer address converted with `#wild_ptr<T>(addr)` can be aliased as an atomic: a store through the alias is read back through the pointer (an mmap'd page). | `run:0` |
| `cc0260` | 260 | rule | “not the raw `hdr_ptr + 24i64`” | Offsets go through `#ptr_add`, not raw `ptr + n`: adding an integer to a pointer is refused. | `refuse` |
| `cc0260b` | 260 | rule | “`#ptr_add<T>(ptr, offset)`” | `#ptr_add<T>(ptr, offset)` offsets a pointer, and an atomic alias of the result works. | `run:0` |
| `cc0264` | 264 | rule | “Exactly six, and nothing else:” | The atomic method set is exactly six: a seventh (`fetch_or`) is refused. | `refuse` |
| `cc0266` | 266 | rule | “`.load()` · `.store(v)` · `.swap(v)`” | All six methods exist and act on the cell: store 5, fetch_add 3, fetch_sub 1, swap 10, compare_exchange(10, 20) leave 20. | `run:0` |
| `cc0268` | 268 | example | “```nitpick” | `int32:prev = counter.fetch_add(1i32);` yields the value before the add. | `run:0` |
| `cc0272` | 272 | rule | “Methods dispatch via UFCS” | Atomic methods dispatch via UFCS. | untestable [internal] UFCS is how `c.load()` is resolved; the reference gives no free-function spelling for an atomic method a program could call instead |
| `cc0276` | 276 | rule | “methods enforce SeqCst” | All six atomic methods lower with seq_cst ordering (load, store, xchg, add, sub, cmpxchg seq_cst seq_cst). | `ir:\A(?=[\s\S]*?load atomic i32[^\n]*seq_cst)(?=[\s\S]*?store atomic i32[^\n]*seq_cst)(?=[\s\S]*?atomicrmw xchg[^\n]*seq_cst)(?=[\s\S]*?atomicrmw add[^\n]*seq_cst)(?=[\s\S]*?atomicrmw sub[^\n]*seq_cst)(?=[\s\S]*?cmpxchg[^\n]*seq_cst seq_cst)` |
| `cc0277` | 277 | rule | “orderings such as `.load_acquire()` are rejected by the compiler” | A suffixed weaker ordering such as `.load_acquire()` is refused. | `refuse` |
| `cc0278` | 278 | rule | “are reserved keywords but reachable” | `relaxed` is a reserved keyword: it cannot name a variable. | `refuse` |
| `cc0278b` | 278 | rule | “are reserved keywords but reachable” | `acquire` is a reserved keyword: it cannot name a variable. | `refuse` |
| `cc0278c` | 278 | rule | “are reserved keywords but reachable” | `release` is a reserved keyword: it cannot name a variable. | `refuse` |
| `cc0279` | 279 | rule | “only through low-level compiler intrinsics” | The ordering keywords are reachable only through low-level compiler intrinsics. | untestable [vague] no intrinsic is named, so no program can reach one or show it absent |
| `cc0297` | 297 | rule | “they pass down the call stack and never up” | Borrows pass down the call stack and never up: a function returning a borrow of its own local is refused. | `refuse` |
| `cc0298` | 298 | rule | “a borrow may not cross **a thread spawn**” | A borrow may not cross a thread spawn: passing `@x` of an int32 to a thread is refused. | `refuse` |
| `cc0298b` | 298 | rule | “**an `await` point**” | A borrow may not cross an await point: a borrow held across an `await` and used after it is refused. | `refuse` |
| `cc0298c` | 298 | rule | “or **an `await` point**” | A borrow may not cross an await point: passing `@x` into an awaited async callee that suspends while holding it is refused. | `refuse` |
| `cc0309` | 309 | row | “\| Threading \| single-threaded \| multi-threaded \|” | A `shared_arena<T>` is multi-threaded: two threads allocate in one shared arena and read their values back. | `run:0` |
| `cc0309b` | 309 | row | “single-threaded” | An `arena<T>` is single-threaded: handing one to a thread is refused. | `refuse` |
| `cc0310` | 310 | row | “**`alloc`, `get`, `destroy` only**” | A `shared_arena<T>` has only alloc, get and destroy: `reset` is refused. | `refuse` |
| `cc0310b` | 310 | row | “`alloc`, `get`, `free`, `reset`, `destroy`” | An `arena<T>` supports alloc, get, free, reset and destroy: reset invalidates a live handle. | `run:0` |
| `cc0310c` | 310 | row | “`destroy` only**” | A `shared_arena<T>` supports alloc, get and destroy. | `run:0` |
| `cc0311` | 311 | row | “\| Per-slot `free` \| yes \| **no** \|” | A `shared_arena<T>` has no per-slot free: `free` is refused. | `refuse` |
| `cc0311b` | 311 | row | “\| Per-slot `free` \| yes \|” | An `arena<T>` frees per slot: the freed handle fails, a sibling handle still reads. | `run:0` |
| `cc0312` | 312 | row | “**chunked, never moves**” | A shared arena's storage is chunked and never moves; an arena<T> may reallocate. | untestable [unobservable] neither operation list yields an address a program could compare before and after growth; handles hide where the slot lives |
| `cc0313` | 313 | row | “one atomic bump per allocation” | An arena<T> allocation costs nothing extra; a shared arena's costs one atomic bump. | untestable [internal] the allocation paths are the runtime's (npk_arena_*, npk_sarena_*), not the program's IR |
| `cc0321` | 321 | rule | “requires that no thread still holds handles” | Destroying a shared arena needs no thread to hold it, by ownership: `destroy` while a spawned thread still borrows it is refused. | `refuse` |
| `cc0326` | 326 | rule | “Race freedom comes from three structural properties” | Race freedom comes from three structural properties (the list that follows has five). | untestable [vague] a count of the document's own list, which it gets wrong (3 vs 5); the five properties are tested at cc0298, cc0115, cc0309-0311, cc0092, cc0332 |
| `cc0332` | 332 | rule | “cannot outlive the scope that spawned them either” | Threads cannot outlive the scope that spawned them: a function that spawns a thread returns only after the thread has finished. | `run:0` |
| `cc0350` | 350 | rule | “that two threads can reach is classified” | Every word of runtime/npkrt.ll two threads can reach is classified in npkrt.spec, and a belt refuses an unclassified access. | untestable [tree] a claim about the runtime's specification files and the tree's belt |
| `cc0354` | 354 | rule | “Each protocol then has a bounded model in `runtime/models/`” | Each runtime protocol has a bounded model whose bad predicates are proven unreachable, with a control per predicate. | untestable [tree] a claim about runtime/models/ and the tree's full run |
| `cc0373` | 373 | example | “```nitpick” | `Channel<T, LEVEL, CAP>` is the channel type: an instance with T=int32, LEVEL=3, CAP=2 carries a value. | `run:0` |
| `cc0379` | 379 | row | “\| `T` \| element type \|” | T is the element type: sending an int64 on a `Channel<int32, ...>` is refused. | `refuse` |
| `cc0380` | 380 | row | “a channel blocks, so it is a blocking primitive” | A channel's LEVEL is a D-056 lock level: a send on a level-4 channel while holding a level-5 mutex guard is a downward acquisition and is refused. | `refuse` |
| `cc0380b` | 380 | row | “\| `LEVEL` \| D-056 lock level” | A send on a level-4 channel while holding a level-3 guard is an upward acquisition and is accepted. | `run:0` |
| `cc0381` | 381 | row | “`> 0` is buffered” | CAP > 0 is a buffer: with CAP 2 two sends complete with no receiver, and a third with a zero deadline fails. | `run:0` |
| `cc0383` | 383 | rule | “A rendezvous is not a one-slot buffer.” | A rendezvous (CAP 0) sender waits for a receiver, not for space: with no receiver a send times out instead of depositing. | `run:0` |
| `cc0386` | 386 | rule | “Registering as a receiver is itself the event” | A rendezvous completes in both arrival orders: a parked sender is taken by a later receiver, and a parked receiver takes a later send. | `run:0` |
| `cc0394` | 394 | rule | “Capacity lives in the **type**” | Capacity lives in the type: a CAP-2 endpoint cannot be bound as a CAP-4 channel. | `refuse` |
| `cc0399` | 399 | rule | “It is a capacity-1 channel the sender closes.” | A one-shot is a capacity-1 channel the sender closes: the receiver gets the value, then an error. | `run:0` |
| `cc0403` | 403 | example | “```nitpick” | The three operations: `await ch.send(move(v), d)` is Result<NIL>, `await ch.recv(d)` is Result<T>, `ch.close()` is Result<NIL>. | `run:0` |
| `cc0409` | 409 | rule | “was struck” | `len()` was struck: `ch.len()` is refused. | `refuse` |
| `cc0415` | 415 | rule | “with a zero deadline, which asks and acts atomically” | A zero deadline asks and acts without waiting: recv on an empty channel fails at once, recv on a non-empty one takes the value. | `run:0` |
| `cc0417` | 417 | rule | “A closed channel is an **error code, never a” | `recv` returns Result<T>: a received zero is a value, and a closed, drained channel is an error (not a timeout, not a value). | `run:0` |
| `cc0421` | 421 | rule | “the parameter is a RELATIVE” | The deadline is a RELATIVE Duration: `recv(Duration{ ns: 60 ms })` on an empty channel waits about 60 ms (an absolute reading would expire at once). | `run:0` |
| `cc0422` | 422 | rule | “(prelude `{ int64:ns }`)” | `Duration` is the prelude struct `{ int64:ns }`. | `run:0` |
| `cc0425` | 425 | rule | “so re-arms cannot drift” | A deadline is converted once to an absolute monotonic time at suspension entry, so re-arms cannot drift. | untestable [timing] drift across re-arms is a property of wait durations |
| `cc0426` | 426 | rule | “`DEADLINE_EXCEEDED` (−4107)” | Expiry is the error `DEADLINE_EXCEEDED`: an expired recv's error compares equal to it. | `run:0` |
| `cc0426b` | 426 | rule | “(−4107)” | DEADLINE_EXCEEDED's code is 4107 (−4107): comparing an error with it compares against that constant. | `ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4107\b` |
| `cc0427` | 427 | rule | “`acquire`, the JOIN's trap code” | Expiry is a catchable Result error at an `acquire`: a 1 ms acquire of a mutex another thread holds returns DeadlineExceeded. | `run:0` |
| `cc0428` | 428 | rule | “There is no unbounded `recv`” | Deadlines are mandatory: a `recv()` with no deadline is refused. | `refuse` |
| `cc0429` | 429 | rule | “`try_send` and `try_recv` do not” | `try_recv` does not exist: it is refused. | `refuse` |
| `cc0431` | 431 | rule | “written `move(v)`” | `send` takes ownership, written `move(v)`: sending an owning string without `move` is refused. | `refuse` |
| `cc0431b` | 431 | rule | “takes ownership” | After `send(move(s), d)` the sender no longer owns s: using s afterwards is refused. | `refuse` |
| `cc0433` | 433 | rule | “is woken by its peer, not by a timer” | A blocked operation is woken by its peer, not by a polling timer. | untestable [timing] the difference is the latency of a hand-off |
| `cc0442` | 442 | rule | “Every operation suspends the task, never the thread” | Channel operations are safe across threads (the ring is under a per-channel mutex): two threads sending 50 each to one channel lose nothing. | `run:0` |
| `cc0454` | 454 | rule | “may not contain a borrow” | A channel element may not contain a borrow: `Channel<int32->, ...>` is refused. | `refuse` |
| `cc0455` | 455 | rule | “so a slice — which is a borrow (D-070) —” | A slice is a borrow and cannot be sent: `Channel<uint8[], ...>` is refused. | `refuse` |
| `cc0458` | 458 | rule | “There is no `select`” | There is no `select`: the word is an ordinary identifier. | `run:0` |
| `cc0478` | 478 | rule | “as handles they may cross freely” | Channel endpoints are handles and cross a thread spawn freely, by value. | `run:0` |
| `cc0479` | 479 | rule | “`StaleHandle` (−4106)” | StaleHandle's code is 4106 (−4106): comparing an error with it compares against that constant. | `ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4106\b` |
| `cc0482` | 482 | rule | “`close` ends the stream, leaving the slot, the buffer and everything” | A closed channel is not reclaimed: values sent before the close are drained, and the end is reported as an error that is not StaleHandle. | `run:0` |
| `cc0489` | 489 | rule | “today a channel outlives its creating scope” | Reclamation is not built: a channel outlives the function that created it, so an endpoint it returns still delivers the value sent before it returned. | `run:0` |
| `cc0490` | 490 | rule | “provoked from source.” | StaleHandle cannot be provoked from source today. | untestable [unobservable] a claim that no program can produce the error; cc0489 tests the half that is observable |
| `cc0492` | 492 | rule | “no `destroy` and no endpoint reference counting” | There is no channel `destroy`: `ch.destroy()` is refused. | `refuse` |
| `cc0501` | 501 | example | “```nitpick” | `Actor<M, R, LEVEL>` is a type with `tell` (Result<NIL>) and `ask` (Result<R>), each taking a moved message and a deadline. | `run:0` |
| `cc0508` | 508 | rule | “An actor is a **task with a mailbox**” | An actor is a task with a mailbox, not a thread. | untestable [vague] no spelling is given to create or spawn an actor |
| `cc0513` | 513 | rule | “The mailbox is a `Channel<M, LEVEL, CAP>`” | An actor's mailbox is a Channel<M, LEVEL, CAP>. | untestable [vague] no operation reaches an actor's mailbox; CAP appears in no actor type parameter |
| `cc0518` | 518 | rule | “an endpoint is a generation-checked handle” | An endpoint may ride in a message: a request carrying its reply channel is answered on that channel. | `run:0` |
| `cc0523` | 523 | rule | “`R = NIL` for an actor that does not reply” | With R = NIL, `ask` is an acknowledgement: it yields Result<NIL>. | `run:0` |
| `cc0526` | 526 | rule | “an actor cannot outlive the scope that spawned” | An actor cannot outlive its spawning scope; scope exit closes, drains and joins it. | untestable [vague] no spelling is given to spawn an actor |
| `cc0528` | 528 | rule | “`alive` is an `atomic<bool>`” | `atomic<bool>` is a valid atomic: store, load and swap work on it. | `run:0` |
| `cc0535` | 535 | example | “```nitpick” | `ThreadPool<LEVEL, CAP>:pool = ThreadPool.create(n)?;` and `await pool.submit(move(job), deadline)?;` compile and run. | `run:0` |
| `cc0540` | 540 | rule | “A thread pool is N worker tasks receiving from one channel.” | A thread pool is N worker tasks receiving from one channel. | untestable [vague] describes the pool's construction, which no program can reach without a constructor that works (cc0535) |
| `cc0550` | 550 | rule | “Submitted work is lexically scoped” | The pool's owning scope does not exit until every submitted job has finished, under a deadline whose expiry traps. | untestable [vague] no pool can be built from the reference's spelling (cc0535) |
| `cc0555` | 555 | rule | “The job type is checked.” | The pool's job type is checked. | untestable [vague] the job type is never named |
| `cc0557` | 557 | rule | “does not exist” | `wait_idle` does not exist. | untestable [unobservable] no pool can be built to call it on (cc0535), so a refusal could not be attributed to wait_idle |
| `cc0566` | 566 | row | “owns its data (D-056); no recursive variant” | `Mutex<T, LEVEL>` owns its data: the guard reads the initial value, a write through one guard is seen through the next. | `run:0` |
| `cc0567` | 567 | row | “\| `RwLock<T, LEVEL>` \| owns its data \|” | `RwLock<T, LEVEL>` owns its data: read guards see it, a write guard changes it. | `run:0` |
| `cc0568` | 568 | row | “**`wait` is removed**” | `CondVar.wait` is removed: `cv.wait(g)` is refused. | `refuse` |
| `cc0568b` | 568 | row | “`timedwait` is the only form” | `timedwait` is the form: with no signal it returns an error when its deadline expires. | `run:0` |
| `cc0569` | 569 | row | “reimplemented natively; LEVELLED like every blocking primitive” | `Barrier<N, LEVEL>` exists: a lone arrival at a 3-party barrier fails when its deadline expires. | `run:0` |
| `cc0569b` | 569 | row | “from the unlevelled `Barrier<N>` this table first wrote” | The unlevelled `Barrier<N>` is gone: a one-parameter Barrier type is refused. | `refuse` |
| `cc0571` | 571 | rule | “deadline-bounded, and returns `Result`” | Every acquisition is deadline-bounded: `m.acquire()` with no deadline is refused. | `refuse` |
| `cc0574` | 574 | example | “```nitpick” | The critical section is a bare block: the guard is released at the closing brace (a 1 ms re-acquire succeeds) and the write through `guard.value.retries` is kept. | `run:0` |
| `cc0581` | 581 | rule | “`await` is not optional here” | `await` is not optional on an acquisition: `m.acquire(d)` without await is refused. | `refuse` |
| `cc0584` | 584 | rule | “no `with` construct” | There is no `with` construct for a critical section. | untestable [unobservable] `with` is a reserved VerificationKeyword (LEXICAL §4), so neither an identifier nor a statement test can show the absence |
| `cc0587` | 587 | rule | “There is no lock-free queue.” | There is no lock-free queue. | untestable [vague] no spelling of such a queue is given whose refusal could be tested |
| `cc0609` | 609 | rule | “acquisition must strictly” | Acquisition must strictly increase: holding a level-5 guard, acquiring a level-3 mutex is refused. | `refuse` |
| `cc0609b` | 609 | rule | “must strictly” | Strictly: holding a level-3 guard, acquiring another level-3 mutex is refused. | `refuse` |
| `cc0609c` | 609 | rule | “blocking primitive carries a compile-time `LEVEL`” | An increasing acquisition (level 3, then level 5, both held) is accepted. | `run:0` |
| `cc0613` | 613 | rule | “flag now claims lock-order freedom rather than deadlock freedom” | The concurrency flag claims lock-order freedom, not deadlock freedom. | untestable [tree] a statement about what a flag's documentation claims |
| `cc0614` | 614 | rule | “`create_recursive` is” | `create_recursive` is removed: calling it is refused. | `refuse` |
| `cc0628` | 628 | rule | “`exit` already” | `exit` routes to failsafe when a wild allocation is still live. | `trap:WildLeak` |
| `cc0632` | 632 | rule | “No coroutine is resumed on any thread, no `defer` runs” | A trap is a whole-program event: a suspended task's `defer` (which would divide by zero) does not run, and failsafe sees the original IntOverflow. | `trap:IntOverflow` |
| `cc0635` | 635 | rule | “stop *before* `failsafe` gets control” | Other threads stop before failsafe gets control. | untestable [timing] an ordering between threads at the moment of a trap |
| `cc0636` | 636 | rule | “`failsafe` runs on the trapping thread as a” | failsafe runs on the trapping thread: a trap on a spawned thread runs failsafe on that thread (its gettid is not the process id). | `run:42` |
| `cc0637` | 637 | rule | “plain call and **may not be `async`**” | `failsafe` may not be `async`: an async failsafe is refused. | `refuse` |
| `cc0641` | 641 | rule | “thread registry (64 slots” | The floor keeps a 64-slot thread registry, claimed and published before the clone. | untestable [internal] the registry's layout; the text states no outcome for a 65th live thread |
| `cc0646` | 646 | rule | “is the exit-70 stop” | A re-entering failsafe holder is the exit-70 stop: a trap inside failsafe ends the process with 70. | `run:70` |

Tables whose rows are not claims:

- line 174: an inventory of the archived prototype's stdlib files (line counts, C dependencies): facts about another source tree, not language behaviour

## CONTROL (`meta/specs/CONTROL_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `ct0003` | 3 | rule | “C-style three-clause `for` loops are deliberately **not** among them” | There is no C-style three-clause for: it is refused. | `refuse` |
| `ct0005` | 5 | rule | “**control flow blocks do NOT end with semicolons**” | A semicolon after an if block's closing brace is a syntax error. | `refuse` |
| `ct0012` | 12 | rule | “Parentheses around the condition are required” | The if condition's parentheses are required: `if x == 1i32 { }` is refused. | `refuse` |
| `ct0014` | 14 | example | “```nitpick” | if / else if / else picks the first true branch, the else catching the rest. | `run:0` |
| `ct0026` | 26 | rule | “Case patterns must be wrapped in parentheses” | Case patterns must be parenthesised: a bare pattern is refused. | `refuse` |
| `ct0027` | 27 | rule | “Cases must be separated by commas” | Cases must be separated by commas: two arms with none between them are refused. | `refuse` |
| `ct0028` | 28 | rule | “The default/catch-all case is designated by `(*)`” | `(*)` is the catch-all: a value no other arm names takes it. | `run:0` |
| `ct0029` | 29 | rule | “Nitpick does not implicitly fall through” | There is no implicit fallthrough. | `run:0` (M10 `p01_no_implicit_fallthrough`) |
| `ct0030` | 30 | rule | “**The selector may not be an `Optional`**” | A pick's selector may not be an Optional: TYPE-065. | `refuse:TYPE-065` |
| `ct0030b` | 30 | rule | “`pick (o ?? default) { … }`” | The Optional is reached with `??`: `pick (o ?? default)` is accepted. | `run:0` |
| `ct0030c` | 30 | rule | “A frac (D-198) and a complex (D-199) are refused at the selector” | A frac selector is refused by the same rule. | `refuse` |
| `ct0031` | 31 | rule | “**One rule set for both spellings**” | The expression form of pick yields through `give`: `int32:v = pick (s) { (A) { give 1i32; }, (*) { give 0i32; } };`. | `run:0` |
| `ct0032` | 32 | rule | “a `move` of one, or a `pass` of one out of the function, is TYPE-047” | A lending pick binds a view: a `move` of an owning view is TYPE-047. | `refuse:TYPE-047` |
| `ct0032b` | 32 | rule | “a copy of an owning view is TYPE-046” | A copy of an owning view is TYPE-046. | `refuse:TYPE-046` |
| `ct0032c` | 32 | rule | “**A view has no address**” | A view has no address: assigning a view is TYPE-066. | `refuse:TYPE-066` |
| `ct0032d` | 32 | rule | “**The selector is frozen while a view of it is live**” | The selector is frozen while a view of it lives: writing the selector in an arm that binds a name is TYPE-067. | `refuse:TYPE-067` |
| `ct0032e` | 32 | rule | “an arm that binds nothing may write it” | An arm that binds nothing may write the selector. | `run:0` |
| `ct0032f` | 32 | rule | “A CONSUMING `pick (move(v))` (D-216) takes the value apart” | A consuming pick's bindings own their payloads, and the selector is moved-from after: reading it is refused. | `refuse` |
| `ct0034` | 34 | example | “```nitpick” | The fallthrough example: `fall two;` in arm one continues into arm two. | `run:0` |
| `ct0047` | 47 | example | “```nitpick” | pick destructures struct and enum variants. | untestable [vague] the example's bodies are `...` and its types undeclared; the destructuring binding modes are ct0032 … ct0032f and ct0055 |
| `ct0055` | 55 | rule | “In a lending `pick` these names are views of `event`'s fields and payload” | A lending pick's names are views of the payload: reading one is accepted. | `run:0` |
| `ct0060` | 60 | rule | “**`fall label;`** — falls through to the labelled arm” | `fall label;` falls through to the labelled arm. | `run:0` (M10 `p02_fall_to_label`) |
| `ct0061` | 61 | rule | “**`give expr;`** — yields a value out of the `pick` block” | `give` yields a value out of a pick used as an expression. | `run:0` (M10 `p09_pick_expression_give`) |
| `ct0063` | 63 | rule | “**`(!)` is removed** (D-061)” | `(!)` is removed: an arm spelled `(!)` is refused. | `refuse` |
| `ct0070` | 70 | rule | “is `#unreachable()`” | An arm whose body is `#unreachable()` traps when it is reached. | `trap:Unreachable` |
| `ct0073` | 73 | rule | “**`pick` must be exhaustive**” | A pick must be exhaustive. | `refuse` (M10 `p10_int_pick_not_exhaustive`) |
| `ct0074` | 74 | rule | “explicit `ERR:` arm” | A tbb selector requires an explicit ERR: arm; `(*)` may not absorb it. | `refuse` (M10 `p12_tbb_pick_needs_err_arm`) |
| `ct0078` | 78 | rule | “individual arms can be guarded by a conditional `where` clause” | An arm guarded by a false `where` moves on to the next arm. | `run:0` (M10 `p08_guard_false_moves_on`) |
| `ct0080` | 80 | example | “```nitpick” | pick matches a macro invocation pattern with a where guard: `MyMacro!(a, b) where (a > b)`. | `run:0` |
| `ct0089` | 89 | rule | “explicitly uses the `is` keyword rather than `?`” | The ternary is `is`, not `?`: `a > b ? a : b` is refused. | `refuse` |
| `ct0091` | 91 | example | “```nitpick” | `int32:max = is (a > b) : a : b;` is the larger. | `run:0` |
| `ct0100` | 100 | rule | “`break;` to exit the innermost loop” | `break;` exits the innermost loop only. | `run:0` |
| `ct0100b` | 100 | rule | “`continue;` to skip to the next iteration across all loop types” | `continue;` skips to the next iteration. | `run:0` (M10 `l27_continue_in_for`) |
| `ct0108` | 108 | rule | “A `while`/`when` with neither” | A while with neither `decreases` nor `unbounded` is TYPE-072. | `refuse:TYPE-072` |
| `ct0109` | 109 | rule | “or both, is `NITPICK-TYPE-072`” | A while with both `decreases` and `unbounded` is TYPE-072. | `refuse:TYPE-072` |
| `ct0109b` | 109 | rule | “`for`, `loop` and `till` are bounded by” | for, loop and till take neither clause: a `for ... decreases` is refused. | `refuse` |
| `ct0115` | 115 | example | “```nitpick” | `while (x < 10i32) decreases 10i32 - x { x += 1i32; }` runs until x is 10. | `run:0` |
| `ct0122` | 122 | rule | “inherently tracks **whether the body ever executed**” | when tracks whether its body ever executed. | `run:0` (M10 `w01_when_ran_then`) |
| `ct0124` | 124 | example | “```nitpick” | The when example: with x = 3 the body runs, then `then` runs and `end` does not. | `run:0` |
| `ct0142` | 142 | row | “\| body ran ≥ 1 time, condition later became false \| `then` \|” | A body that ran and then saw its condition false takes `then`. | `run:0` (M10 `w01_when_ran_then`) |
| `ct0143` | 143 | row | “\| body ran ≥ 1 time, exited early via `break` \| `then` \|” | A body that broke out takes `then`. | `run:0` (M10 `w03_when_break_then`) |
| `ct0144` | 144 | row | “\| condition false initially — body never ran \| `end` \|” | A body that never ran takes `end`. | `run:0` (M10 `w02_when_never_ran_end`) |
| `ct0146` | 146 | rule | “Both clauses are optional.” | Both clauses are optional: a when with neither `then` nor `end` compiles and runs. | `run:0` |
| `ct0161` | 161 | example | “```nitpick” | `for (int64:i in 1..3)` visits 1, 2 and 3. | `run:0` |
| `ct0170` | 170 | example | “```nitpick” | The C-style three-clause for, the first rejected form, is refused. | `refuse` |
| `ct0172` | 172 | rule | “untyped binding — not supported” | An untyped for binding, `for (i in 0..10)`, is refused. | `refuse` |
| `ct0181` | 181 | rule | “there is no `auto`, `var`, or `let`” | There is no `let`: an inferred declaration is refused. | `refuse` |
| `ct0183` | 183 | rule | “a range, a slice, an array, or a” | for iterates a slice. | `run:0` |
| `ct0183b` | 183 | rule | “an array” | for iterates an array in order. | `run:0` (M10 `l25_for_over_array_in_order`) |
| `ct0184` | 184 | rule | “value whose type implements the prelude trait `Iterator`” | for iterates a value whose type implements Iterator (`next` returning `Item?`, NIL ending it). | `run:0` |
| `ct0187` | 187 | rule | “Anything else is refused at the checker by” | A for binding of another type than the element's is refused by name, TYPE-033. | `refuse:NITPICK-TYPE-033` (M10 `l28_for_binding_type_mismatch`) |
| `ct0191` | 191 | rule | “expose it inside the block via the special `$` keyword” | loop and till expose the counter as `$`. | `run:0` (M10 `l12_loop_ascending`) |
| `ct0193` | 193 | rule | “inside a `Rules`” | Inside a Rules body `$` is the subject. | `run:0` |
| `ct0198` | 198 | rule | “Counts **up from 0** to `limit`” | till counts up from 0 to limit (exclusive). | `run:0` (M10 `l10_till_counts_from_zero`) |
| `ct0199` | 199 | example | “```nitpick” | `till(10i32, 1i32) { x += $; }` sums 0 to 9: 45. | `run:0` |
| `ct0205` | 205 | rule | “**Direction is inferred**” | loop's direction is inferred from start and limit. | `run:0` (M10 `l13_loop_descending`) |
| `ct0207` | 207 | example | “```nitpick” | `loop(0i32, 10i32, 1i32)` sums 0..9 (45); `loop(10i32, 0i32, 1i32)` sums 10..1 (55). | `run:0` |
| `ct0220` | 220 | rule | “A negative step is a **compile error**” | A negative literal step is a compile error. | `refuse:NITPICK-TYPE-068` (M10 `l20_negative_step_literal_refused`) |
| `ct0222` | 222 | rule | “falling back to a runtime check that traps to” | A computed step is checked at run time: a zero step traps. | `run:113` (M10 `l21_zero_step_computed_traps`) |
| `ct0233` | 233 | row | “\| `step` negative or zero \| compile error \|” | A literal zero step is a compile error. | `refuse:NITPICK-TYPE-068` (M10 `l19_zero_step_literal_refused`) |
| `ct0234` | 234 | row | “\| `start == limit` \| zero iterations \|” | start == limit is zero iterations. | `run:0` (M10 `l14_loop_start_equals_limit`) |
| `ct0235` | 235 | row | “\| `till` with `limit <= 0` \| zero iterations” | till with limit <= 0 is zero iterations. | `run:0` (M10 `l11_till_nonpositive_limit`) |
| `ct0236` | 236 | row | “\| a bound is `tbb` holding ERR \| traps to `failsafe`” | A loop bound that is a tbb holding ERR traps to failsafe (TbbErr). | `trap:TbbErr` |
| `ct0242` | 242 | rule | “`loop` takes three arguments and `till` two” | loop takes three arguments: a two-argument loop is refused. | `refuse` |
| `ct0255` | 255 | rule | “**There is no `loop { }` infinite form and no do-while construct.**” | There is no infinite `loop { }`: it is refused. | `refuse` |
| `ct0255b` | 255 | rule | “`while (true)” | `while (true) unbounded` is the unbounded loop, left by break. | `run:0` |
| `ct0258` | 258 | rule | “defines `till` as do-while” | till is not a do-while: with limit 0 the body never runs. | `run:0` (M10 `l11_till_nonpositive_limit`) |
| `ct0266` | 266 | example | “```nitpick” | The labelled-loop example: `break outer` leaves both loops. | `run:0` |
| `ct0278` | 278 | rule | “`break label;` and `continue label;` both target a labelled loop” | `continue label;` targets a labelled loop. | `run:0` (M10 `l26_labelled_continue`) |
| `ct0286` | 286 | rule | “**`discard(expr);`**” | `discard(expr);` discards a value. | `run:0` |
| `ct0287` | 287 | rule | “**`_~ expr;`**” | `_~ expr;` desugars to discard(). | `run:0` |
| `ct0289` | 289 | example | “```nitpick” | The discard example compiles. | `run:0` |
| `ct0306` | 306 | rule | “Blocks introduce a lexical” | A block introduces a lexical scope: its variables are invisible outside it. | `refuse` (M10 `h03_block_binding_invisible`) |
| `ct0308` | 308 | rule | “bindings are destroyed at the closing brace” | Scope-managed bindings are destroyed at the block's closing brace: a list in a block is freed before a larger one after it, which peaks alone. | `run:0` heap `24000/16000/2` |
| `ct0314` | 314 | rule | “**`NITPICK-IF-002`**” | An assignment inside an if condition is rejected as NITPICK-IF-002. | `refuse:IF-002` |
| `ct0317` | 317 | rule | “**`NITPICK-IF-001`**” | An else without an immediately preceding if is NITPICK-IF-001. | `refuse:IF-001` |
| `ct0319` | 319 | rule | “**`NITPICK-WHEN-001`**” | An orphaned `then` without a preceding when is NITPICK-WHEN-001. | `refuse:WHEN-001` |
| `ct0323` | 323 | rule | “**`pass expr;`** — returns a successful `Result<T>`” | `pass expr;` returns a successful Result. | `run:0` |
| `ct0324` | 324 | rule | “**`fail errCode;`** — returns an errored `Result<T>`” | `fail errCode;` returns an errored Result carrying the code. | `run:0` |
| `ct0325` | 325 | rule | “*(expression, not a statement)* propagates” | relay propagates the same error code, verbatim. | `run:0` (M10 `r02_relay_same_error`) |
| `ct0326` | 326 | rule | “if `expr` is an error the enclosing function returns immediately” | relay returns at once on an error. | `run:0` (M10 `r03_relay_returns_at_once`) |
| `ct0332` | 332 | rule | “the literal form, the only way to return a value” | `return Result{ … };` returns a value and an error simultaneously. | `run:0` (M10 `r10_result_literal_both`) |
| `ct0334` | 334 | rule | “**Every path of a function body ends in one of these” | Every path of a function body ends in pass, fail, exit or a trap: an empty body is FLOW-001. | `refuse:NITPICK-FLOW-001` (M10 `q01_empty_body`) |
| `ct0337` | 337 | rule | “`NIL` function passes `NIL`” | A NIL function falling off its end is refused. | `refuse:NITPICK-FLOW-001` (M10 `q07_nil_function_falls_off`) |
| `ct0338` | 338 | rule | “`main` exits” | main without exit is refused. | `refuse:NITPICK-FLOW-001` (M10 `q04_main_without_exit`) |
| `ct0341` | 341 | rule | “an `if` without `else` completes” | A path past an if without else completes, so a missing pass after it is refused. | `refuse:NITPICK-FLOW-001` (M10 `q02_missing_path`) |
| `ct0342` | 342 | rule | “`if`/`else` completes if either arm does” | An if/else whose arms both pass does not complete: no pass is needed after it. | `run:0` (M10 `q09_if_else_both_pass`) |
| `ct0342b` | 342 | rule | “a `pick` if any arm's body does” | A pick whose arms all pass does not complete. | `run:0` (M10 `q10_pick_all_arms_pass`) |
| `ct0343` | 343 | rule | “a `while (true)` with no” | A while (true) with no break never completes. | `run:0` (M10 `q08_while_true_never_completes`) |
| `ct0344` | 344 | rule | “every other loop and `when` completes as a whole” | A for loop completes as a whole. | `refuse:NITPICK-FLOW-001` (M10 `q11_for_loop_completes`) |
| `ct0347` | 347 | rule | “`ok()` is the taint-clearing” | `ok()` is the taint-clearing builtin: `ok(x)` compiles. | `run:0` |
| `ct0348` | 348 | rule | “`err()` does not exist” | `err()` does not exist: calling it is refused. | `refuse` |
| `ct0354` | 354 | rule | “a **compile-time** proof obligation discharged by Z3” | prove is a compile-time obligation discharged by z3 under --verify; a counterexample fails compilation. | untestable [z3] the verified build's verdict; the plain build lowers prove to nothing (VERIFICATION:78's claim) |
| `ct0357` | 357 | rule | “**`assert_static(cond);`**” | assert_static halts compilation when its condition is false (TYPE-069). | `refuse:TYPE-069` |
| `ct0365` | 365 | rule | “`NITPICK-TYPE-069` when it does not fold to a constant” | assert_static over a run-time value does not fold: TYPE-069. | `refuse:TYPE-069` |
| `ct0366` | 366 | rule | “in a `comptime` body both statements are evaluated per call” | In a comptime body assert_static is evaluated per call: a call whose argument fails it is refused. | `refuse` |
| `ct0375` | 375 | rule | “Pushes a block onto a stack to run when the enclosing lexical scope exits” | defer pushes onto a stack: defers run LIFO. | `run:0` (M10 `w04_defer_lifo`) |
| `ct0377` | 377 | example | “```nitpick” | `wild int8->:buf = alloc(16i64); defer { dalloc(buf); }` frees the block at the scope's exit. | `run:0` |
| `ct0382` | 382 | rule | “**after the exit's value is evaluated** (D-136)” | Defers run after the exit's value is evaluated: `pass v` returns the v read at the pass. | `run:0` (M10 `w05_pass_value_before_defer`) |
| `ct0382b` | 382 | rule | “LIFO, innermost scope first” | Defers run innermost scope first. | `run:0` (M10 `w11_defer_inner_scope_first`) |
| `ct0382c` | 382 | rule | “Runs on **every normal exit path**” | defer runs on fail. | `run:0` (M10 `w06_defer_on_fail`) |
| `ct0384` | 384 | rule | “**`defer` does NOT run on a trap** (D-014)” | defer does not run on a trap. | `run:82` (M10 `w09_no_defer_on_trap`) |
| `ct0393` | 393 | rule | “may appear only in `main` or” | exit may appear only in main or failsafe. | `refuse` (M10 `e03_exit_outside_main_refused`) |
| `ct0397` | 397 | rule | “the `<wildx-states>` map must be empty” | A successful exit with live wildx memory triggers the failsafe trap (WildLeak). | `trap:WildLeak` |
| `ct0397b` | 397 | rule | “Reaching `exit` with live” | Reaching exit with live wild memory triggers the failsafe trap. | `run:96` (M10 `e01_exit_zero_with_live_wild`) |
| `ct0406` | 406 | rule | “a failure exit keeps its code” | A failure exit keeps its code. | `run:3` (M10 `e02_failure_exit_keeps_code`) |
| `ct0409` | 409 | rule | “`wild_release_all()` and exit positive” | failsafe may call wild_release_all() and exit positive; its own exit is exempt from the check. | `run:42` |
| `ct0411` | 411 | rule | “trap raised *inside* `failsafe` exits 70 directly” | A trap raised inside failsafe exits 70 directly. | `run:70` |
| `ct0412` | 412 | rule | “`wild_live_count()` is the program-visible view of the set” | wild_live_count() is the program-visible view of the set. | `run:0` |
| `ct0412b` | 412 | rule | “Managed-regime” | Managed storage is not in the set: a string alive at exit 0 is not reported. | `run:0` |

## IO (`meta/specs/IO_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `io0014` | 14 | rule | “D-074” | D-074 returns `stream` to userland: it is an ordinary identifier. | `run:0` |
| `io0015b` | 15 | rule | “returns it to userland along with `process`, `pipe`, `debug`, and `log`” | D-074 returns `process` to userland: it is an ordinary identifier. | `run:0` |
| `io0015c` | 15 | rule | “returns it to userland along with `process`, `pipe`, `debug`, and `log`” | D-074 returns `pipe` to userland: it is an ordinary identifier. | `run:0` |
| `io0015d` | 15 | rule | “returns it to userland along with `process`, `pipe`, `debug`, and `log`” | D-074 returns `debug` to userland: it is an ordinary identifier. | `run:0` |
| `io0015e` | 15 | rule | “returns it to userland along with `process`, `pipe`, `debug`, and `log`” | D-074 returns `log` to userland: it is an ordinary identifier. | `run:0` |
| `io0016` | 16 | rule | “what follows needs language syntax” | Nothing in the I/O model needs language syntax. | untestable [vague] no checkable outcome |
| `io0022` | 22 | rule | “`Stream` describes what every readable or writable thing can” | `Stream` is the trait every readable or writable thing implements: it can bound a generic parameter. | `run:0` |
| `io0023` | 23 | rule | “files, pipes, sockets, and memory buffers are stdlib types implementing it” | Files, pipes, sockets and memory buffers are stdlib types implementing the stream trait. | untestable [vague] names no socket or memory-buffer type to test |
| `io0025` | 25 | example | “```nitpick” | Reader and Writer have the example's shape: user types implementing `read`, `write` and `flush` with exactly those signatures are called through them. | `run:0` |
| `io0036` | 36 | rule | “receivers are `Self->`” | Receivers are `Self->`: an impl whose receiver is by value is refused. | `refuse` |
| `io0039` | 39 | rule | “An impl must keep the trait's” | An impl must keep the trait's `async`: a synchronous `write` in an impl of Writer is refused with TYPE-048. | `refuse:TYPE-048` |
| `io0039b` | 39 | rule | “are relative spans named `within`” | Deadline parameters are relative spans named `within`. | untestable [timing] relativity shows only as a wait's duration; cc0421 measures it on a channel |
| `io0045` | 45 | rule | “Every operation is `async`” | Every stream operation is async: `r.read(..)` without await is refused. | `refuse` |
| `io0048` | 48 | rule | “through raw syscalls” | The executor's readiness mechanism is io_uring or epoll through raw syscalls. | untestable [internal] the executor is the runtime's; the syscalls it makes are not visible to a program |
| `io0050` | 50 | rule | “and carries a **deadline**” | Every operation carries a deadline (there is no unbounded read): `read` without one is refused. | `refuse` |
| `io0052` | 52 | rule | “a read cannot be told a length that disagrees” | Buffers are slices: a read into a 4-byte slice of an 8-byte array takes 4 bytes of 8 available and leaves the rest of the array alone. | `run:0` |
| `io0063` | 63 | rule | “Object safety holds” | Reader and Writer are object-safe: `dyn Writer` and `dyn Reader` values dispatch to the user impls. | `run:0` |
| `io0070` | 70 | example | “```nitpick” | `Result<int64>:n = await src.read(dest, deadline);` yields the number of bytes read. | `run:0` |
| `io0074` | 74 | rule | “returns the number of bytes placed in `dest`” | `read` returns the number of bytes placed in dest: 5 available into an 8-byte slice gives 5. | `run:0` |
| `io0075` | 75 | rule | “code `E_EOF` = −4096” | End of input is the error code `E_EOF`: a read of an exhausted stream fails with it. | `run:0` |
| `io0075b` | 75 | rule | “= −4096” | E_EOF's code is 4096 (−4096): comparing a read's error with the EOF identity compares against that constant. | `ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4096\b` |
| `io0077` | 77 | rule | “pins the value” | tests/backend/programs/fd_io.npk pins E_EOF's value with a running program. | untestable [tree] a claim about a test file in the compiler repository (it compares with the identity IoEof, not with a number) |
| `io0078` | 78 | rule | “No operation returns a sentinel” | No operation returns a sentinel: an exhausted read is an error, not a zero count. | `run:0` |
| `io0090` | 90 | rule | “end-of-input is an error code, exactly as a closed channel is” | A closed, drained channel is an error code, as end-of-input is. | `run:0` |
| `io0099` | 99 | rule | “**different types** rather than a mode flag on one type” | Text and byte streams are different types: a ByteWriter cannot be bound as a TextWriter. | `refuse` |
| `io0103` | 103 | row | “\| Translation \| **none, ever** \| on \|” | A byte stream never translates: `a\r\nb\n` written by a ByteWriter reads back as the same 5 bytes. | `run:0` |
| `io0104` | 104 | row | “and lone `\r` all yield `\n`” | A text reader reads `\r\n`, `\n` and a lone `\r` each as one line break: `a\r\nb\nc\rd` is four lines. | `run:0` |
| `io0105` | 105 | row | “`\n`, unless opened requesting otherwise” | A text writer created with LineEnding.Lf writes `\n` as `\n`. | `run:0` |
| `io0106` | 106 | row | “\| Unit \| `uint8[]` \|” | A byte stream's unit is `uint8[]`: passing a `string` to a ByteWriter's write is refused. | `refuse` |
| `io0111` | 111 | rule | “is a creation parameter held in the writer” | The line ending is a creation parameter held in the writer, not in the type: an Lf and a CrLf writer have one type, and one function writes differently through each. | `run:0` |
| `io0115` | 115 | example | “```nitpick” | `TextWriter:w = text_writer_create(sink, LineEnding.Lf) ?! …;` and the CrLf twin build text writers; the CrLf one writes `\r\n`. | `run:0` |
| `io0117` | 117 | rule | “LineEnding.CrLf” | LineEnding.CrLf is the opt-in: a CrLf text writer writes `a\nb` as `a\r\nb`. | `run:0` |
| `io0121` | 121 | rule | “static methods — every trait and impl method takes `self`” | The language has no static methods: an impl method without `self`, called as `Type.method()`, is refused. | `refuse` |
| `io0124` | 124 | rule | “`Path.parse` spelling this document used” | Construction is a bare function: the `Path.parse` spelling is refused. | `refuse` |
| `io0130` | 130 | rule | “never inferred from whether the output is a terminal” | Buffering is never inferred from whether the output is a terminal. | untestable [platform] needs a terminal on stdout to compare with a pipe; the harness has none |
| `io0134` | 134 | row | “\| `stdin` \| fully buffered \|” | stdin is fully buffered. | untestable [unobservable] how far a reader fetches ahead of what it returns is not visible to the program; stdin is /dev/null here |
| `io0135` | 135 | row | “\| `stdout` \| line buffered, always \|” | stdout is line buffered, always: with fd 1 on a pipe, a partial line written through std_out() is not delivered until its newline. | `run:0` |
| `io0136` | 136 | row | “\| `stderr` \| **unbuffered, always** \|” | stderr is unbuffered: with fd 2 on a pipe, a partial line written through std_err() is delivered at once. | `run:0` |
| `io0144` | 144 | rule | “`io_isatty` remains available” | `io_isatty` is available and answers whether a descriptor is a terminal. | untestable [vague] the reference gives no signature, so no call can be written from the text; no BUILTIN_REFERENCE row names io_isatty |
| `io0151` | 151 | rule | “(`std_out` returns” | `std_out` returns `TextWriter<LineBufWriter<ByteWriter>>`: buffering is a type. | `run:0` |
| `io0157` | 157 | rule | “`defer` does not run on a trap (D-014)” | `defer` does not run on a trap: a registered defer that would divide by zero does not run when the program traps IntOverflow. | `trap:IntOverflow` |
| `io0158` | 158 | rule | “**No flush is attempted**” | No flush is attempted on a trap: a partial line in line-buffered stdout is lost when the program traps. | `sh:0` |
| `io0163` | 163 | rule | “so diagnostics written to it survive a trap” | stderr is unbuffered, so a partial line written to it survives a trap. | `sh:0` |
| `io0165` | 165 | rule | “The registry of open streams is reachable from `failsafe`” | The registry of open streams is reachable from failsafe, which may flush. | untestable [vague] no spelling reaches the registry; its shape is an open item (line 282) |
| `io0175` | 175 | example | “```nitpick” | `Path:p = path_parse("/etc/hosts") ?! …; ByteReader:r = byte_reader_open(p, within) ?! …;` opens a file for reading. | `run:0` |
| `io0184` | 184 | rule | “open `O_NONBLOCK \| O_CLOEXEC`” | Opened descriptors are O_NONBLOCK and O_CLOEXEC. | `run:0` |
| `io0187` | 187 | rule | “**Opening takes a `Path`**, never a `string`” | Opening takes a Path, never a string: `byte_reader_open("/dev/null", d)` is refused. | `refuse` |
| `io0188` | 188 | rule | “absolute, lexically normalized, and contains no interior NUL” | A Path is absolute: parsing a relative path fails. | `run:0` |
| `io0188b` | 188 | rule | “lexically normalized” | A Path is lexically normalized: `/a/./b/../c//d` parses as `/a/c/d`. | `run:0` |
| `io0188c` | 188 | rule | “contains no interior NUL” | A Path contains no interior NUL: parsing `/a\0b` fails. | `run:0` |
| `io0189` | 189 | rule | “where the conversion” | The conversion to cstring rejects interior NULs: `to_cstring("ab\0cd")` fails. | `run:0` |
| `io0191` | 191 | rule | “POSIX's `-1` goes to `Result.err`” | An fd is always valid: a failed open is a Result error, not a -1 descriptor. | `run:0` |
| `io0196` | 196 | rule | “Lexical normalization is not kernel resolution” | Normalization is lexical: `/no_such_dir_m11/../etc` normalizes to `/etc` though the directory does not exist. | `run:0` |
| `io0204` | 204 | rule | “and is closed at scope” | A stream is closed at the exit of the scope that opened it: after the writer's block, the reader drains its byte and then sees end of input. | `run:0` |
| `io0210` | 210 | rule | “There is no `close` in the surface.” | There is no close in the surface: `w.close()` on a stream is refused. | `refuse` |
| `io0212` | 212 | rule | “`close(release_fd(move o))` is the explicit spelling” | `close(release_fd(move o))` closes an owned descriptor and reports the verdict: the reader then sees end of input. | `run:0` |
| `io0213` | 213 | rule | “no double-close is” | No double close is spellable: a second `release_fd(move(o))` of a moved owner is refused. | `refuse` |
| `io0215` | 215 | rule | “A stream cannot be sent through a channel” | A stream cannot be sent through a channel: `Channel<ByteReader, ...>` is refused. | `refuse` |
| `io0216` | 216 | rule | “refusal fires on `OwnedFd`” | The element refusal fires on OwnedFd: `Channel<OwnedFd, ...>` is refused. | `refuse` |
| `io0218` | 218 | rule | “A MOVE into a spawn is legal” | A move of a stream into a thread spawn is legal: the thread writes through the moved writer, and its scope's close gives the reader end of input. | `run:0` |
| `io0220` | 220 | rule | “A BORROW of a stream still refuses at the” | A borrow of a stream refuses at the spawn. | `refuse` |
| `io0227` | 227 | example | “```nitpick” | `await s.seek(Whence.Start, offset, deadline)` returns Result<int64>, the new position. | `run:0` |
| `io0231` | 231 | rule | “not an `int64` constant” | `Whence` is an enum, not an int64: seeking with `0i64` as the origin is refused. | `refuse` |
| `io0231b` | 231 | rule | “`Start`, `Current`, `End`” | Whence.End, Whence.Start and Whence.Current measure from the end, the start and the current position. | `run:0` |
| `io0232` | 232 | rule | “Seeking a buffered stream discards the read buffer” | Seeking a buffered stream discards its read buffer: after a text reader has read `ab` (buffering `cd`), seeking to the start and reading gives `ab` again. | `run:0` |
| `io0239` | 239 | rule | “are `TextReader` / `TextWriter` over the three” | The standard streams are TextReader/TextWriter over the inherited descriptors: std_in() reads fd 0 (here /dev/null) and meets end of input at once. | `run:0` |
| `io0242` | 242 | rule | “They are **not** globals that any code may grab.” | The standard streams are not globals: the name `stdout` is not defined. | `refuse` |
| `io0242b` | 242 | rule | “They belong to `main`'s scope and” | The standard streams belong to main's scope and are passed down: constructing one in a helper function is refused. | `refuse` |
| `io0248` | 248 | rule | “Each owns a `F_DUPFD_CLOEXEC` DUP” | Each standard stream owns an F_DUPFD_CLOEXEC dup: its descriptor is not 0-2 and has FD_CLOEXEC. | `run:0` |
| `io0249` | 249 | rule | “scope-exit close can never close 0/1/2” | Scope-exit close never closes 0/1/2: after std_in/out/err are built and dropped, descriptors 0, 1 and 2 are still open. | `run:0` |
| `io0250` | 250 | rule | “The inherited descriptors stay BLOCKING” | The inherited descriptors stay blocking: after std_in/out/err are built, fds 0-2 lack O_NONBLOCK. | `run:0` |
| `io0252` | 252 | rule | “blocks the thread, bounded by the consumer” | A write to a stuffed stdout pipe blocks the thread, bounded by the consumer. | untestable [timing] a blocked thread shows only as a duration |
| `io0261` | 261 | row | “`cstring` at the boundary (D-049)” | nlibc is raw syscalls with cstring at the boundary: the floor's `open` refuses a `string` path. | `refuse` |
| `io0262` | 262 | row | “the text and byte streams, buffering, the standard streams” | The stdlib layer supplies Path, Reader/Writer, the text and byte streams, buffering and the standard streams, and they compose. | `run:0` |
| `io0267` | 267 | rule | “**`printf` and `scanf` are not in either layer**” | `printf` is not available. | `refuse` |
| `io0268` | 268 | rule | “spliced by `&{ }` interpolation” | Formatting is ordinary functions returning string, spliced by `&{ }` interpolation. | `run:0` |
| `io0269` | 269 | rule | “There is no format-specifier language” | There is no format-specifier language: a text writer writes `%d` verbatim. | `run:0` |
| `io0280` | 280 | rule | “and only epoll” | The readiness mechanism is epoll only, with no timerfd; io_uring is refused. | untestable [internal] the executor's syscalls are the runtime's, not visible to a program |

## LEXICAL (`meta/specs/LEXICAL_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `lx0014` | 14 | rule | “Nitpick source is a sequence of Unicode code points encoded in UTF-8” | Source is UTF-8: a string literal holding `é` compiles, and the string is its two UTF-8 bytes. | `run:0` |
| `lx0015` | 15 | rule | “not forming part of a valid token are a lexical error” | A character that forms no token (`§` between two operands) is a lexical error: refused. | `refuse` |
| `lx0017` | 17 | example | “```ebnf” | Every code point up to U+10FFFF is a source character: a string literal holding U+1F600 compiles and is its four UTF-8 bytes. | `run:0` |
| `lx0024` | 24 | rule | “Block comments do **not** nest” | Block comments do not nest: `/* a /* b */ c */` ends at the first `*/`, leaving `c */` as code, which is refused. | `refuse` |
| `lx0024b` | 24 | rule | “stream. Block comments” | Since block comments do not nest, an inner `/*` is comment text: `/* a /* b */` is one whole comment and the program compiles. | `run:0` |
| `lx0026` | 26 | example | “```ebnf” | Whitespace (space, tab, CR, LF) and both comment forms are discarded: `1i32 /* c */ + 2i32 // d` with a tab and a CRLF is 3. | `run:0` |
| `lx0035` | 35 | rule | “ASCII-bounded, beginning with a letter or underscore” | Identifiers are ASCII-bounded: `café` is not an identifier, and a local of that name is refused. | `refuse` |
| `lx0035b` | 35 | rule | “beginning with a letter or underscore” | An identifier may begin with an underscore: `_n2` is a local's name. | `run:0` |
| `lx0037` | 37 | example | “```ebnf” | `Identifier ::= [a-zA-Z_] [a-zA-Z0-9_]*`: `a_1B` and `Z9` are names. | `run:0` |
| `lx0043` | 43 | rule | “The lexer resolves `_?`, `_!`, and `_~` as distinct operators” | `_!` is lexed as the operator before any identifier: `_! g(3i32)` on a `never fails` callee is 3. | `run:0` |
| `lx0043b` | 43 | rule | “`_?`” | `_?` is lexed as the operator: `_? note();` discards a `never fails` NIL call. | `compile` |
| `lx0048` | 48 | example | “```ebnf” | The keyword families are reserved: one word of each (`wild`, `relaxed`, `if`, `prove`, `async`, `use`, `struct`, `int8`, `is`) is refused as a local's and a function's name. | `sh:0` |
| `lx0052` | 52 | rule | “MemoryQualifier     ::= "wild"” | `wild`, `wildx`, `stack`, `defer`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0054` | 54 | rule | “MemoryOrdering      ::= "relaxed"” | `relaxed`, `acquire`, `release`, `acq_rel`, `seq_cst`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0056` | 56 | rule | “ControlFlow         ::= "if"” | `if`, `else`, `while`, `for`, `loop`, `till`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0057` | 57 | rule | “"when" \| "then" \| "end" \| "pick"” | `when`, `then`, `end`, `pick`, `fall`, `where`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0058` | 58 | rule | “"give" \| "break" \| "continue"” | `give`, `break`, `continue`, `return`, `pass`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0059` | 59 | rule | “"fail" \| "exit" \| "raw"” | `fail`, `exit`, `raw`, `drop`, `nodrop`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0060` | 60 | rule | “"defaults" \| "discard" \| "move" \| "relay"” | `defaults`, `discard`, `move`, `relay`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0062` | 62 | rule | “VerificationKeyword ::= "prove"” | `prove`, `assert_static`, `requires`, `ensures`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0063` | 63 | rule | “"acquires" \| "gives"” | `acquires`, `gives`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0064` | 64 | rule | “"invariant" \| "fails" \| "on" \| "with" \| "never"” | `invariant`, `fails`, `on`, `with`, `never`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0065` | 65 | rule | “"old" \| "result" \| "pure"” | `old`, `result`, `pure`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0066` | 66 | rule | “"decreases" \| "unbounded"” | `decreases`, `unbounded`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0072` | 72 | rule | “`decreases Expr` on a FUNCTION (D-304 (5), 1.5.8c) is the measure a recursive” | A function's `decreases n` is checked at every recursive call: a call with a measure that does not shrink traps DecreasesViolated. | `trap:DecreasesViolated` |
| `lx0076` | 76 | rule | “`while (c) unbounded` -- exactly one of the two, TYPE-072” | A `while` stating both `decreases` and `unbounded` is refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `lx0076b` | 76 | rule | “exactly one of the two” | A `while` stating neither `decreases` nor `unbounded` is refused, NITPICK-TYPE-072. | `refuse:NITPICK-TYPE-072` |
| `lx0078` | 78 | rule | “arguments and nothing else -- no allocation, no I/O, no suspension, no” | A `pure` function's body is checked: one that allocates (`string_concat`) is refused. | `refuse` |
| `lx0080` | 80 | rule | “call site inside a contract, which admits only `never fails` `pure` callees” | A contract admits only `never fails` `pure` callees: `requires raw pos(n)` with `pos` not `pure` is refused. | `refuse` |
| `lx0080b` | 80 | rule | “admits only `never fails` `pure` callees” | The permitted twin: `requires raw pos(n)` with `pos` declared `pure never fails` compiles and `half(8)` is 4. | `run:0` |
| `lx0083` | 83 | rule | “`never fails` is also legal after a function TYPE's parameter list” | `never fails` after a function type's parameter list: `func int64() never fails:f = seven;` and `raw f()` is 7. | `run:0` |
| `lx0085` | 85 | rule | “AsyncKeyword        ::= "async"” | `async`, `await`, `thread`, `joins`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0087` | 87 | rule | “ModuleKeyword       ::= "use"” | `use`, `mod`, `pub`, `extern`, `cfg`, `as`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0088` | 88 | rule | “"comptime" \| "inline" \| "noinline"” | `comptime`, `inline`, `noinline`, `macro`, `derive`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0089` | 89 | rule | “"sealed" \| "hidden"” | `sealed`, `hidden`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0091` | 91 | rule | “`sealed` and `hidden` are FIELD qualifiers (D-313, D-314): a sealed field is” | A `sealed` field is read anywhere: outside its struct's module, `a.bal` reads 5. | `run:0` |
| `lx0092` | 92 | rule | “read anywhere and written only by code in the module that declares its” | A `sealed` field is written only inside its struct's module: `a.bal = 6i64;` outside is refused. | `refuse` |
| `lx0093` | 93 | rule | “a hidden field is neither read nor written outside that module” | A `hidden` field is not read outside its struct's module: `a.key` outside is refused. | `refuse` |
| `lx0095` | 95 | rule | “TypeKeyword         ::= "struct"” | `struct`, `enum`, `assoc`, `opaque`, `error`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0096` | 96 | rule | “\| "unit"” | `unit`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0097` | 97 | rule | “"trait" \| "impl" \| "Self"” | `trait`, `impl`, `Self`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0098` | 98 | rule | “"Rules" \| "limit" \| "fixed"” | `Rules`, `limit`, `fixed`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0100` | 100 | rule | “BuiltinType         ::= "int8"” | `int8`, `int16`, `int32`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0101` | 101 | rule | “"int64" \| "int128" \| "int256"” | `int64`, `int128`, `int256`, `int512`, `int1024`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0102` | 102 | rule | “"int2048" \| "int4096"” | `int2048`, `int4096`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0103` | 103 | rule | “"uint8" \| "uint16"” | `uint8`, `uint16`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0104` | 104 | rule | “"uint32" \| "uint64" \| "uint128"” | `uint32`, `uint64`, `uint128`, `uint256`, `uint512`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0105` | 105 | rule | “"uint1024" \| "uint2048" \| "uint4096"” | `uint1024`, `uint2048`, `uint4096`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0106` | 106 | rule | “"tbb8" \| "tbb16" \| "tbb32"” | `tbb8`, `tbb16`, `tbb32`, `tbb64`, `tbb128`, `tbb256`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0107` | 107 | rule | “"frac8" \| "frac16" \| "frac32" \| "frac64"” | `frac8`, `frac16`, `frac32`, `frac64`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0108` | 108 | rule | “"tfp32" \| "tfp64" \| "tfp128"” | `tfp32`, `tfp64`, `tfp128`, `tfp256`, `dim256`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0109` | 109 | rule | “"flt32" \| "flt64" \| "flt128"” | `flt32`, `flt64`, `flt128`, `flt256`, `flt512`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0110` | 110 | rule | “"bool" \| "char8" \| "char16"” | `bool`, `char8`, `char16`, `char32`, `string`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0111` | 111 | rule | “\| "cstring"” | `cstring`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0112` | 112 | rule | “"fd" \| "pid" \| "tid" \| "uid" \| "gid"” | `fd`, `pid`, `tid`, `uid`, `gid`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0113` | 113 | rule | “"oflags" \| "prot" \| "mflags" \| "fmode"” | `oflags`, `prot`, `mflags`, `fmode`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0114` | 114 | rule | “"dyn" \| "any" \| "Result" \| "Optional"” | `dyn`, `any`, `Result`, `Optional`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0115` | 115 | rule | “"Handle" \| "arena" \| "shared_arena"” | `Handle`, `arena`, `shared_arena`, `atomic`, `Future`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0116` | 116 | rule | “\| "Channel"” | `Channel`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0117` | 117 | rule | “"Mutex" \| "Guard" \| "RwLock" \| "RGuard"” | `Mutex`, `Guard`, `RwLock`, `RGuard`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0118` | 118 | rule | “"CondVar" \| "Barrier" \| "OwnedFd"” | `CondVar`, `Barrier`, `OwnedFd`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0119` | 119 | rule | “"simd" \| "complex" \| "array" \| "func"” | `simd`, `complex`, `array`, `func`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0120` | 120 | rule | “\| "range"” | `range`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0121` | 121 | rule | “"trit" \| "tryte" \| "nit" \| "nyte"” | `trit`, `tryte`, `nit`, `nyte`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0122` | 122 | rule | “"buffer" \| "NIL"” | `buffer`, `NIL`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0124` | 124 | rule | “BuiltinHelper       ::= "is" \| "in" \| "is_err"” | `is`, `in`, `is_err`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0127` | 127 | rule | “`vec2`, `vec3`, `vec9`, `matrix`, `tmatrix`, `tensor` and `ttensor` were” | `vec2`, `vec3`, `vec9`, `matrix`, `tmatrix`, `tensor` and `ttensor` are not keywords (D-135): a local of each name compiles. | `sh:0` |
| `lx0142` | 142 | row | “\| `gc` removed from `MemoryQualifier` \|” | `gc`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0143` | 143 | row | “\| `fails`, `on`, `with`, `never` added \|” | `fails`, `on`, `with`, `never`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0144` | 144 | row | “\| `is_err` added \|” | `is_err`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0145` | 145 | row | “\| **`ok` removed** \|” | `ok`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0146` | 146 | row | “\| `discard` added to `ControlFlow` \|” | `discard`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0147` | 147 | row | “\| `tbb128`, `tbb256` added \|” | `tbb128` and `tbb256` are types: `5tbb128 + 5tbb128` is `10tbb128`, and `7tbb256` binds. | `run:0` |
| `lx0148` | 148 | row | “\| `fix256` → `dim256` \|” | `fix256` is no longer a name the language holds, so a local of that name compiles; `dim256` is reserved. | `sh:0` |
| `lx0149` | 149 | row | “\| `tfp128`, `tfp256` added \|” | `tfp128` and `tfp256` are types: `1.5tfp128 + 1.5tfp128` is `3.0tfp128`, and `2.5tfp256` binds. | `run:0` |
| `lx0150` | 150 | row | “\| `char8/16/32` added \|” | `char8` is semantically distinct from `uint8`: binding a `char8` to a `uint8` is refused. | `refuse` |
| `lx0151` | 151 | row | “`Handle`, `arena`, `shared_arena`, `atomic`, `Future`, `Optional`, `simd`, `complex` added” | `Handle`, `arena`, `shared_arena`, `atomic`, `Future`, `Optional`, `simd`, `complex`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0152` | 152 | row | “\| **35 `a*` collection keywords removed** \|” | `astack`, `alist`, `ahash`, `astringlist`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0153` | 153 | row | “\| `fd`, `pid`, `tid`, `uid`, `gid` added \|” | Kernel identifiers permit no arithmetic: `a + b` on two `fd`s is refused. | `refuse` |
| `lx0153b` | 153 | rule | “permitting comparison but not arithmetic” | Kernel identifiers permit comparison: `a == b` on two `fd`s compiles. | `compile` |
| `lx0153c` | 153 | rule | “POSIX's `-1` goes to `Result.err` and is not representable” | An `fd` of -1 is not representable: `(-1i32) => fd` is refused. | `refuse` |
| `lx0154` | 154 | row | “\| `range` added \|” | `range<T>` can be written: `range<int64>:r = 0i64...3i64;` compiles. | `compile` |
| `lx0155` | 155 | row | “\| `oflags`, `prot`, `mflags`, `fmode` added \|” | A flag family takes `\|` within the family and `=> int32` outbound: `(O_WRONLY \| O_CREAT) => int32` is the two flags' ints or-ed. | `run:0` |
| `lx0155b` | 155 | rule | “no arithmetic and no order” | A flag family has no arithmetic: `O_WRONLY + O_CREAT` is refused. | `refuse` |
| `lx0155c` | 155 | rule | “no order” | A flag family has no order: `O_WRONLY < O_CREAT` is refused. | `refuse` |
| `lx0155d` | 155 | rule | “families never convert to each other” | Flag families never convert to each other: `O_WRONLY => prot` is refused. | `refuse` |
| `lx0155e` | 155 | rule | “`int32 =>! ` inbound” | Inbound to a flag family is `=>!`, not `=>`: `(1i32) => oflags` is refused. | `refuse` |
| `lx0155f` | 155 | rule | “`=> int32` outbound and `int32 =>! ` inbound” | Inbound with `=>!` compiles: `(1i32) =>! oflags`. | `compile` |
| `lx0156` | 156 | row | “\| `assoc` added \|” | `assoc`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0157` | 157 | row | “\| **`Type` removed** \|” | `Type`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0158` | 158 | row | “\| **`stream`, `process`, `pipe`, `debug`, `log` removed** \|” | `stream`, `process`, `pipe`, `debug`, `log`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0159` | 159 | row | “\| **`const` removed** \|” | `const` is removed and not reserved (D-088's rule): a local named `const` compiles. | `sh:0` |
| `lx0160` | 160 | row | “\| **`binary` removed** \|” | `binary`: none is a keyword, so a local of that name compiles. | `sh:0` |
| `lx0160b` | 160 | rule | “`buffer` is retained” | `buffer`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0161` | 161 | row | “\| **`move` moved** from `MemoryQualifier` to `ControlFlow` \|” | `move(place)` is a keyword operator: `string:t = move(s);` takes the string. | `run:0` |
| `lx0161b` | 161 | rule | “marking a CONSUMING parameter” | `move` on a parameter marks it consuming: `take(move(s))` passes the string in. | `run:0` |
| `lx0161c` | 161 | rule | “is refused (`NITPICK-MOVE-004`) anywhere but a parameter” | `move` in a declaration anywhere but a parameter is refused, NITPICK-MOVE-004. | `refuse:NITPICK-MOVE-004` |
| `lx0162` | 162 | row | “\| **`relay` and `_^` added** \|” | `relay` forwards the error's code verbatim and runs `defer`: the caller's arm `(E1)` matches, and the deferred write happened. | `run:0` |
| `lx0162b` | 162 | rule | “`relay` forwards the code verbatim and runs `defer`” | `_^` is `relay`'s operator: `_^ inner(v)` forwards the code and runs `defer` the same way. | `run:0` |
| `lx0163` | 163 | row | “\| `Self` added \|” | `Self`: each is reserved, so a local and a function of that name are each refused. | `sh:0` |
| `lx0164` | 164 | row | “\| `NIL` added to `BuiltinType` \|” | `NIL` is a type: `func:reset = NIL(int32->:a)` compiles, and its call writes through the pointer. | `run:0` |
| `lx0165` | 165 | row | “\| `cstring` added to `BuiltinType` \|” | `cstring` is a builtin type's keyword: a user type named `cstring` is refused, never a shadow. | `refuse` |
| `lx0166` | 166 | row | “`result` is the SUCCESS value in `ensures`” | `result` names the success value in `ensures`: `ensures result == x + 1i32` holds for `inc`. | `run:0` |
| `lx0167` | 167 | row | “checked in every build, `DecreasesViolated`” | A `while`'s `decreases` is checked in every build: a measure that does not shrink traps DecreasesViolated. | `trap:DecreasesViolated` |
| `lx0168` | 168 | row | “\| `pure` added to `VerificationKeyword` \|” | Purity is checked in the body: a `pure` function calling one that is not `pure` is refused. | `refuse` |
| `lx0168b` | 168 | rule | “`pure` never rides a function TYPE” | `pure` never rides a function type: `func int64() pure never fails:f` is refused. | `refuse` |
| `lx0169` | 169 | row | “`for` is **not** duplicated” | `for` is one reserved token. | untestable [vague] the row states the grammar's bookkeeping; that `for` is reserved is lx0056's claim |
| `lx0173` | 173 | example | “```ebnf” | The arithmetic, compound, comparison, logical and bitwise operators of the block lex and compute: a program using each gets the expected values. | `run:0` |
| `lx0174` | 174 | rule | “"++" \| "--"” | `++` and `--` are operator tokens: `x++; x--;` compiles. | `compile` |
| `lx0178` | 178 | rule | “"<=>"” | `<=>` is an operator: `a <=> b` compiles and orders (-1 when a < b). | `run:0` |
| `lx0186` | 186 | rule | “CompilerSigil ::= "#"” | `#` addresses the compiler: `#size_of<int64>()` is 8. | `run:0` |
| `lx0191` | 191 | rule | “`=>` and `=>!` are the *only*” | `=>` and `=>!` are the only cast forms: a C-style cast `(int64)x` is refused. | `refuse` |
| `lx0191b` | 191 | rule | “**`=>!` added**” | `x as int64` is no cast either: refused. | `refuse` |
| `lx0195` | 195 | rule | “It was formerly” | `#` is not a value operator (the old pin): `#x` on a value is refused. | `refuse` |
| `lx0203` | 203 | rule | “**The wrapping family `+% -% *%`**” | `+%` computes modulo 2^N and never traps: `127i8 +% 1i8` is -128. | `run:0` |
| `lx0204` | 204 | rule | “forms `+%= -%= *%=`” | The compound forms wrap: `u +%= 1u8` from 255 is 0, `-%=` back is 255, `*%= 2u8` is 254. | `run:0` |
| `lx0204b` | 204 | rule | “Plain `+ - *` TRAP on overflow (D-210)” | Plain `+` traps on overflow: `127i8 + 1i8` traps IntOverflow. | `trap:IntOverflow` |
| `lx0208` | 208 | rule | “They are the longest match, so `a +% b` is one token” | `a + %b` was never a program (`%` starts no expression): refused. | `refuse` |
| `lx0218` | 218 | row | “\| `..` \| inclusive range `[a, b]` \| expression \|” | `..` is inclusive: summing `1i64..3i64` is 6. | `run:0` |
| `lx0219` | 219 | row | “\| `...` \| exclusive range `[a, b)` \| expression \|” | `...` is exclusive: summing `1i64...3i64` is 3. | `run:0` |
| `lx0220` | 220 | row | “\| `..*` \| variadic rest marker — **collects** arguments \| declaration site \|” | `..*` collects the trailing arguments: `total(1, 2, 3)` is 6. | `run:0` |
| `lx0221` | 221 | row | “\| `..^` \| spread — **expands** a collection into arguments \| call site \|” | `..^` spreads a slice into the arguments: `total(1, ..^xs)` with `xs` = [2, 3] is 6. | `run:0` |
| `lx0223` | 223 | rule | “`..*` and `..^` are inverses. Confirmed against the prototype:” | `..*` and `..^` are inverses, confirmed against the prototype's parser. | untestable [tree] the confirmation cites the prototype's and the compiler's own sources; lx0221 spreads what lx0220 collects |
| `lx0231` | 231 | rule | “`>>` is the right-shift operator **and** the closing bracket pair of a nested” | `>>` closes a nested generic: `Result<List<int64>>:r = mk();` compiles and the list is usable. | `run:0` |
| `lx0239` | 239 | rule | “Explicit type arguments in expression position are always written” | Explicit type arguments in an expression need the turbofish: `idt<int32>(5i32)` is refused. | `refuse` |
| `lx0240` | 240 | rule | “with the turbofish” | With the turbofish, `idt::<int32>(5i32)` is 5. | `run:0` |
| `lx0241` | 241 | rule | “splits inside a type-argument list and is a right-shift everywhere outside one” | Outside a type-argument list `>>` is a right shift: `64 >> 2` is 16. | `run:0` |
| `lx0251` | 251 | row | “\| **leading** \| negation \| `!x`, `!=` \|” | A leading `!` negates: `!t` is false, and `a != b` compares. | `run:0` |
| `lx0252` | 252 | row | “\| **trailing or repeated** \| unchecked / emphatic \| `?!`, `=>!`, `_!`, `!!!` \|” | The trailing forms lex as their operators: `?!`, `=>!` and `_!` compile and compute; `!!! E1;` goes to failsafe's `E1` arm (81). | `run:81` |
| `lx0254` | 254 | rule | “**`!!` no longer exists.**” | `!!` no longer exists: `asm!!` is refused. | `refuse` |
| `lx0256` | 256 | rule | “full-tier syscall is spelled **`sys_full`**” | The full-tier syscall is spelled `sys_full`: `sys_full(39i64)` compiles. | `compile` |
| `lx0259` | 259 | rule | “**Macro invocation is `#name(args)`**, not `name!(args)` (D-046)” | A macro is not invoked as `name!(args)`: `seven!()` is refused. | `refuse` |
| `lx0259b` | 259 | rule | “**Macro invocation is `#name(args)`**” | A macro is invoked as `#name(args)`: `#seven()` is 7. | `run:0` |
| `lx0269` | 269 | example | “```ebnf” | `true`, `false`, `NIL` and `ERR` are literals: each binds where its type is expected. | `run:0` |
| `lx0271` | 271 | rule | “SentinelLiteral ::= "NULL" \| "NIL" \| "ERR"” | `NULL` is a literal: `int8->:p = NULL;` compiles. | `compile` |
| `lx0274` | 274 | rule | “**`unknown` is not a literal.**” | `unknown` is not a literal: `int32:x = unknown;` is refused. | `refuse` |
| `lx0279` | 279 | rule | “`ERR` **is** writable” | `ERR` is writable and is a `pick` label: a `tbb8` holding `ERR` takes the `ERR:` arm. | `run:0` |
| `lx0284` | 284 | rule | “Underscores are permitted for readability and ignored” | Underscores in a literal are ignored: `1_000i32` is 1000. | `run:0` |
| `lx0287` | 287 | rule | “leading significant digit is a letter takes a value-neutral leading zero” | A value whose leading digit is a letter takes a leading zero: `0FFhex` is 255, `0Tt` is -1, `0an` is -1. | `run:0` |
| `lx0290` | 290 | example | “```ebnf” | Every base is a suffix: `10`, `0Ahex`, `1010bin`, `12oct`, `101t` and `11n` are each 10. | `run:0` |
| `lx0296` | 296 | rule | “DecimalLiteral ::= [0-9] ([0-9_]* [0-9])?” | Underscores may stand anywhere inside the digits: `1__0i32` is 10. | `run:0` |
| `lx0296b` | 296 | rule | “([0-9_]* [0-9])?” | A decimal literal ends with a digit: `10_i32` (a trailing underscore) is refused. | `refuse` |
| `lx0297` | 297 | rule | “HexLiteral     ::= [0-9] ([0-9a-fA-F_]* [0-9a-fA-F])? "hex"” | Hex digits take either case: `0ffhex` equals `0FFhex`. | `run:0` |
| `lx0302` | 302 | rule | “TernaryLiteral ::= [01] ([01Tt_]* [01Tt])? ("t" \| "ter" \| "tri")” | Balanced ternary takes the suffixes `t`, `ter` and `tri`, and `T` or `t` is -1: `1Tt`, `1Tter`, `1Ttri` and `1tt` are each 2. | `run:0` |
| `lx0305` | 305 | rule | “NonaryLiteral  ::= [0-4] ([0-4a-dA-D_]* [0-4a-dA-D])? ("non" \| "n")” | Balanced nonary takes `non` and `n`, and a..d / A..D are -1..-4: `1an` is 8, `1dn` and `1Dnon` are 5. | `run:0` |
| `lx0307` | 307 | rule | “FloatLiteral   ::= DecimalLiteral "." DecimalLiteral Exponent? TypeSuffix?” | A float literal with an exponent: `1.5e2f64` is 150.0. | `run:0` |
| `lx0307b` | 307 | rule | “DecimalLiteral "." DecimalLiteral” | A float needs digits on both sides of the point: `.5f64` is refused. | `refuse` |
| `lx0308` | 308 | rule | “Exponent       ::= [eE] [+-]? DecimalLiteral” | An exponent takes a sign and either case: `15.0E-1f64` is 1.5. | `run:0` |
| `lx0310` | 310 | rule | “TypeSuffix     ::= "u8" \| "u16" \| "u32" \| "u64" \| "u128"” | The suffixes `u8` … `u128` are literals' types. | `compile` |
| `lx0311` | 311 | rule | “"u256" \| "u512" \| "u1024" \| "u2048" \| "u4096"” | The suffixes `u256` … `u4096` are literals' types. | `compile` |
| `lx0312` | 312 | rule | “"i8" \| "i16" \| "i32" \| "i64" \| "i128"” | The suffixes `i8` … `i128` are literals' types. | `compile` |
| `lx0313` | 313 | rule | “"i256" \| "i512" \| "i1024" \| "i2048" \| "i4096"” | The suffixes `i256` … `i4096` are literals' types. | `compile` |
| `lx0314` | 314 | rule | “"tbb8" \| "tbb16" \| "tbb32" \| "tbb64" \| "tbb128" \| "tbb256"” | The `tbb` suffixes are literals' types. | `compile` |
| `lx0315` | 315 | rule | “"f32" \| "f64" \| "f128"” | The suffixes `f32`, `f64` and `f128` are float literals' types. | `compile` |
| `lx0316` | 316 | rule | “"tfp32" \| "tfp64" \| "tfp128" \| "tfp256" \| "dim256"” | The `tfp` suffixes and `dim256` are literals' types. | `compile` |
| `lx0317` | 317 | rule | “"char8" \| "char16" \| "char32"” | The `char` suffixes are literals' types. | `compile` |
| `lx0321` | 321 | rule | “verified EXACTLY at scan time (`NITPICK-LEX-004`)” | A literal outside the signed 64-bit envelope is refused at scan time, NITPICK-LEX-004. | `refuse:NITPICK-LEX-004` |
| `lx0323` | 323 | rule | “(`NITPICK-TYPE-031`)” | A literal must fit its type, checked at the literal: `300i8` is refused, NITPICK-TYPE-031. | `refuse:NITPICK-TYPE-031` |
| `lx0324` | 324 | rule | “(`0u64 - 1u64` is the maximum)” | `0u64 - 1u64` is uint64's maximum. | `run:0` |
| `lx0326` | 326 | rule | “`0b4bni8` is −128” | `0b4bni8` is -128. | `run:0` |
| `lx0330` | 330 | rule | “from 1.5.8b step 2 the spelling is refused” | From 1.5.8b step 2, `0u64 - 1u64` is refused, NITPICK-TYPE-076. | `refuse:NITPICK-TYPE-076` |
| `lx0332` | 332 | rule | “`~0u64` is the maximum” | `~0u64` is uint64's maximum: every bit set. | `run:0` |
| `lx0332b` | 332 | rule | “`(1u64 << 63u64) \| k` gives” | `(1u64 << 63u64) \| k` builds a value above 2^63-1: with `k` = `04BF29CE484222325hexu64` it is above 9223372036854775807. | `run:0` |
| `lx0334` | 334 | rule | “`0u64 -% 1u64` also works” | `0u64 -% 1u64` wraps to the maximum. | `run:0` |
| `lx0337` | 337 | rule | “`FFhex`,” | By D-147 `FFhex`, `an`, `ban` and `tt` are ordinary identifiers: a local of each name compiles. | `sh:0` |
| `lx0338` | 338 | rule | “`an`, `ban`, `tt` are ordinary identifiers; the values they used to spell are” | The values those words used to spell are `0FFhex` (255), `0an` (-1), `0ban` (-19) and `0tt` (-1). | `run:0` |
| `lx0343` | 343 | rule | “The **legacy C-style prefixes** (`0x`, `0b`, `0o`, `0n`)” | The C-style `0o` prefix is removed: `0o17` is refused. | `refuse` |
| `lx0346` | 346 | rule | “`0xFF` is a bad-digit error at the `x`” | `0xFF` is a bad-digit error at the `x`, NITPICK-LEX-003. | `refuse:NITPICK-LEX-003` |
| `lx0349` | 349 | rule | “**Ternary/nonary use the suffix form**” | The prefix form of a ternary literal (`0t1T`) is not the language's: refused. | `refuse` |
| `lx0353` | 353 | rule | “`int2048` and `int4096` have no direct source literal” | `int2048` has no direct source literal: `5i2048` is refused. | `refuse` |
| `lx0354` | 354 | rule | “are instantiated by parsing” | Such a value is instantiated by parsing: `parse_uint2048("1.5e308")` compiles. | `compile` |
| `lx0358` | 358 | example | “```ebnf” | Each escape is its byte: `\n \r \t \\ \" \' \0 \x41 \u{42}` is nine bytes 10 13 9 92 34 39 0 65 66. | `run:0` |
| `lx0365` | 365 | rule | “RawStringLiteral   ::= "r" '"' (SourceCharacter - '"')* '"'” | A raw string performs no escape processing: `r"a\nb"` is four bytes, the second a backslash. | `run:0` |
| `lx0366` | 366 | rule | “BlockStringLiteral ::= '"""' (SourceCharacter - '"""')* '"""'” | A block string holds a lone `"`: `"""a"b"""` is the three bytes `a"b`. | `run:0` |
| `lx0368` | 368 | rule | “CharacterLiteral   ::= "'"” | A character literal takes an escape: `'\n'` is 10char8, and `'A'` is 65char8. | `run:0` |
| `lx0377` | 377 | rule | “preserves newlines and indentation verbatim” | A block string preserves newlines and indentation verbatim: a newline and two spaces stay. | `run:0` |
| `lx0377b` | 377 | rule | “ends at the FIRST `"""`: a `"`” | A `""` inside a block string is body text: `"""a""b"""` is the four bytes `a""b`. | `run:0` |
| `lx0383` | 383 | rule | “Backtick-delimited, with `&{ … }` interpolation” | A template literal interpolates `&{ … }`: `` `x&{ n }y` `` with n = 5 is "x5y". | `run:0` |
| `lx0383b` | 383 | rule | “The lexer decomposes a template” | The lexer decomposes a template into TEMPLATE_START, TEMPLATE_PART, INTERP_START, INTERP_END, TEMPLATE_END. | untestable [internal] the token kinds are the lexer's; lx0383 and lx0387 test the literal |
| `lx0387` | 387 | example | “```ebnf” | A template holds several interpolations of expressions: `` `&{ a }+&{ b }=&{ a + b }` `` is "2+3=5". | `run:0` |
| `lx0405` | 405 | rule | “Ownership transfers only where `move` is written” | Ownership never transfers implicitly: `string:t = s;` is refused. | `refuse` |
| `lx0406` | 406 | rule | “implicitly — and the moved-from binding is invalid until reinitialized” | A moved-from binding is invalid: reading `s` after `move(s)` is refused. | `refuse` |
| `lx0406b` | 406 | rule | “until reinitialized” | Reinitialised after the move, the binding is valid again: `s` assigned anew reads its new value. | `run:0` |
| `lx0408` | 408 | rule | “`impl` now takes” | `impl` takes no connector: `impl:Box:Show = {};` implements the trait, and `b.show()` is 7. | `run:0` |

## MACRO (`meta/specs/MACRO_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `mc0015` | 15 | rule | “does not compile against” | The prototype's 32-test corpus is written in a dialect that does not compile against this language. | untestable [tree] a statement about the compiler repository's regression corpus (tests/bugs/), not about what the compiler does with a program |
| `mc0022` | 22 | example | “```nitpick” | The declaration shape `macro:name = (param, …) { body };` declares a macro invoked as `#name(...)`. | `run:0` |
| `mc0026` | 26 | rule | “What it contains determines where the macro may be” | Only the body decides where a macro may be invoked: an expression body invoked where a declaration is expected (module level) is refused. | `refuse` |
| `mc0032` | 32 | row | “\| declarations (`func:`, …) \| module level \| top-level declarations \|” | A body of declarations invoked at module level splices as TOP-LEVEL declarations: a function written above the invocation can call what it emits. | `run:0` |
| `mc0033` | 33 | row | “\| variable declarations \| a `struct` body \| fields \|” | A body of variable declarations invoked in a struct body splices as that struct's fields. | `run:0` |
| `mc0034` | 34 | row | “\| function declarations \| an `impl` body \| methods \|” | A body of function declarations invoked in an impl body splices as methods of the type. | `run:0` |
| `mc0035` | 35 | row | “\| a single expression \| expression position \| that expression \|” | A body of one expression invoked in expression position is that expression, as one node: `#four() * 10i32` is (2 + 2) * 10. | `run:0` |
| `mc0037` | 37 | rule | “A macro taking no parameters still declares an empty list” | A macro with no parameters must still write `()`: `macro:m = { … };` is refused. | `refuse` |
| `mc0039` | 39 | rule | “A body is a declaration body if it CONTAINS a declaration” | A body that contains a declaration is a declaration body even when its first item is an invocation; invoked at module level it emits both what the inner macro emits and its own declaration. | `run:0` |
| `mc0043` | 43 | rule | “`macro:opt = () { #caller(x) + 1i32; };`” | `macro:opt = () { #caller(x) + 1i32; };` is accepted as a single-expression macro (a body beginning with `#` is not thereby a declaration body). | `run:0` |
| `mc0044` | 44 | rule | “a statement macro could not invoke another one” | A statement macro may invoke another statement macro (it could not before D-125): the body `{ #check_base(); #check_base(); }` expands at statement position. | `run:0` |
| `mc0046` | 46 | rule | “nothing but a single invocation” | A body that is only one invocation is whatever the invoked macro is: an alias of an expression macro works in expression position. | `run:0` |
| `mc0046b` | 46 | rule | “`macro:alias = () { #b(); };`” | "is whatever `b` is": an alias whose target is a declaration macro, invoked at module level, emits the target's declarations. | `run:0` |
| `mc0048` | 48 | rule | “at statement position it becomes a block holding” | An alias of a statement macro, invoked at statement position, becomes a block holding `#b();` that the next round expands. | `run:0` |
| `mc0053` | 53 | example | “```nitpick” | `#name()` invokes with no arguments and `#name(a, b)` with arguments. | `run:0` |
| `mc0060` | 60 | example | “```nitpick” | The four positions with one spelling: module level emits declarations, a struct body splices fields, an impl body splices methods, an expression position substitutes the expression. | `run:0` |
| `mc0070` | 70 | rule | “An invocation whose expansion does not fit where it landed is an error” | Fields into something that is not a struct is an error: a variable-declaration body invoked in an impl body is refused. | `refuse` |
| `mc0071` | 71 | rule | “declarations into an expression” | Declarations into an expression is an error: a declaration body invoked where a value is expected is refused. | `refuse` |
| `mc0076` | 76 | row | “\| module level \| declarations \| cloned \|” | At module level a declarations body arrives as a copy of its declarations, all of them callable. | `run:0` |
| `mc0077` | 77 | row | “\| `struct` body \| variable declarations \| **converted to fields** \|” | In a struct body a variable-declarations body is converted to fields, which can be written and read like any field. | `run:0` |
| `mc0078` | 78 | row | “\| `impl` or `trait` body \| declarations \| cloned \|” | A trait body takes a declarations body too: spliced signatures become required methods an impl supplies. | `run:0` |
| `mc0079` | 79 | row | “\| expression position \| one expression \| substituted in place \|” | In expression position the one expression is substituted in place, each invocation its own copy with its own argument: #doubled(3) + #doubled(10) = 26. | `run:0` |
| `mc0080` | 80 | row | “\| `enum` body \| — \| refused \|” | An invocation in an enum body is refused. | `refuse` |
| `mc0082` | 82 | rule | “parses as a STATEMENT” | `int32:x;` parses as a statement in a macro body and as a field in a struct, so a struct splice is a conversion rather than a copy. | untestable [internal] which grammar reads the text and how the splice converts it are the parser's and expander's internals; mc0077 tests the observable result |
| `mc0085` | 85 | rule | “carrying an initialiser or a qualifier is refused rather than stripped” | A variable declaration with an initialiser spliced into a struct body is refused rather than stripped. | `refuse` |
| `mc0085b` | 85 | rule | “a field has” | A variable declaration carrying a qualifier (`fixed`) spliced into a struct body is refused rather than stripped: "a field has neither". | `refuse` |
| `mc0088` | 88 | rule | “An enum body is refused” | An enum body is refused whatever the body's shape: a declarations body invoked in an enum is refused. | `refuse` |
| `mc0094` | 94 | rule | “An argument replaces every occurrence of the parameter name in the body” | An argument replaces every occurrence of the parameter, including inside a declaration the body emits. | `run:0` |
| `mc0097` | 97 | example | “```nitpick” | `#make_const(42i32);` emits `func:my_const = int32() { pass 42i32; };`. | `run:0` |
| `mc0105` | 105 | rule | “Substitution traverses the whole emitted subtree” | Substitution reaches a parameter however deep it sits in the emitted subtree (inside a pick arm inside an if inside an emitted function). | `run:0` |
| `mc0105b` | 105 | rule | “It is not textual” | Substitution is not textual: the argument lands as one AST node, so #times3(1 + 2) is (1 + 2) * 3 = 9. | `run:0` |
| `mc0112` | 112 | example | “```nitpick” | The emit_helpers example: three emitted declarations referencing each other; helper_sum is 42. | `run:0` |
| `mc0120` | 120 | rule | “All three become top-level declarations” | All three emitted functions become top-level declarations and helper_sum resolves the other two. | `run:0` |
| `mc0121` | 121 | rule | “Names emitted by one expansion are visible to each other” | Names emitted by one expansion are visible to each other regardless of order: the first emitted function calls two emitted after it. | `run:0` |
| `mc0126` | 126 | example | “```nitpick” | `struct:Point = { #make_xy_fields(); };` gives Point fields x and y. | `run:0` |
| `mc0132` | 132 | rule | “may mix spliced and literal fields freely” | A struct may mix spliced and literal fields: a literal field, a splice of two, a literal field gives four fields of 16 bytes, each holding its own value. | `run:0` |
| `mc0136` | 136 | example | “```nitpick” | The emit_methods example: `impl:Box:Pair = { #emit_methods(); };` gives Box the method add_one. | `run:0` |
| `mc0146` | 146 | rule | “An identifier in a macro body resolves in the scope where the macro was” | An identifier in a macro body resolves where the macro was written, always: invoked inside a function with a local of the same name, the macro reads the module binding. | `run:0` |
| `mc0149` | 149 | rule | “A macro is invocable only in the module that declares it” | A macro is invocable in the module that declares it, including a nested module invoking a macro it declares itself. | `run:0` |
| `mc0150` | 150 | rule | “`use` does not bind it, `pub` on it changes nothing” | A macro is not exported: a `pub macro:` in another module, named in a `use`, is still not invocable. | `refuse` |
| `mc0151` | 151 | rule | “inside the declaring one cannot reach it” | A module nested inside the declaring one cannot invoke its macro; invoking a macro from another module is NITPICK-MACRO-007. | `refuse:NITPICK-MACRO-007` |
| `mc0154` | 154 | rule | “macro from another module is `NITPICK-MACRO-007`” | Invoking, at module level, a macro declared in another file module (imported with `use ….*`) is NITPICK-MACRO-007. | `refuse:NITPICK-MACRO-007` |
| `mc0156` | 156 | rule | “is the mechanism for code generation that crosses a module” | `#[derive]` is the mechanism for code generation across modules; `macro:` is a local shorthand. | untestable [vague] a statement of which mechanism is meant for what; it states no outcome a program could check beyond mc0150/mc0154 |
| `mc0159` | 159 | example | “```nitpick” | The hygiene example: `#report()` reads the TOP-LEVEL `shared` (100), not main's local 5, so the template is "shared = 100". | `run:0` |
| `mc0171` | 171 | rule | “that is a **compile error**” | A name in a macro body that does not resolve in the defining scope is a compile error, never a fallback to the call site. | `refuse` |
| `mc0176` | 176 | example | “```nitpick” | `#caller(shared)` inside a template reads the invocation site's `shared`: "shared = 5". | `run:0` |
| `mc0180` | 180 | rule | “resolves `NAME` at the **invocation site**” | `#caller(NAME)` resolves NAME at the invocation site: the caller's int32 `flag`, not the module's bool. | `run:0` |
| `mc0181` | 181 | rule | “naming something absent there is an error” | `#caller(NAME)` naming something absent at the invocation site is an error. | `refuse` |
| `mc0186` | 186 | rule | “It resolves the way any name at that point resolves” | `#caller(NAME)` reaches past the caller's locals to the module's own names: with no local of that name it reads the module binding. | `run:0` |
| `mc0188` | 188 | rule | “It differs from writing the” | `#caller(NAME)` differs from the bare name exactly when the invocation site has a local binding of it. | `run:0` |
| `mc0193` | 193 | rule | “site is `NITPICK-RESOLVE-002`” | `#caller(NAME)` naming something absent from the invocation site (declared only inside another function) is NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `mc0194` | 194 | rule | “is `NITPICK-MACRO-008`” | Writing `#caller` outside a macro body is NITPICK-MACRO-008. | `refuse:NITPICK-MACRO-008` |
| `mc0201` | 201 | row | “\| a declaration \| the declarations, in this module \| landing where the macro was written \|” | Declarations emitted at module level land in this module, where the macro was written: a free name in an emitted function resolves to the module binding. | `run:0` |
| `mc0202` | 202 | row | “\| a statement \| **a block** holding the statements \| the block's parent being the module scope \|” | A statement invocation becomes a block whose parent is the module scope: a free name in it reads the module binding past the caller's local of the same name. | `run:0` |
| `mc0203` | 203 | row | “\| an expression \| the expression, substituted in place \| one mark on the substituted node \|” | An expression invocation is substituted in place and still resolves its free names where the macro was written: 101, not the caller's 5 + 1. | `run:0` |
| `mc0207` | 207 | rule | “collide with a caller's `tmp`” | A `tmp` declared in a statement body cannot collide with the caller's `tmp`: both coexist and the caller's keeps its value. | `run:0` |
| `mc0207b` | 207 | rule | “it cannot be read after the invocation” | A local declared in a statement body cannot be read after the invocation. | `refuse` |
| `mc0208` | 208 | rule | “name in the body walks up past the caller's locals to the module” | A free name in a statement body walks past the caller's locals to the module: a module FUNCTION is called although the caller has an int32 local of the same name. | `run:0` |
| `mc0209` | 209 | rule | “statement-position hygiene needs no check anywhere” | One block node carries the statement-position hygiene rule; no check is needed anywhere. | untestable [internal] how the expander represents the rule; the observable halves are mc0202-mc0208 |
| `mc0220` | 220 | rule | “no longer exists” | NITPICK-061 (MACRO_HYGIENE_VIOLATION) no longer exists: a macro whose free name resolves differently at the call site compiles with no such diagnostic. | `sh:0` |
| `mc0225` | 225 | rule | “Expansion precedes everything.” | Expansion runs before name resolution: a struct emitted by a macro names a parameter type of a function written above the invocation. | `run:0` |
| `mc0226` | 226 | rule | “so what those passes see is the expanded” | Static analyses see the expanded program: an emitted function with a path that reaches its end without `pass` is refused. | `refuse` |
| `mc0231` | 231 | example | “```nitpick” | `#outer();` expands to `{ #inner(); f3 }`, then inner expands on the next round: f1 and f3 both exist. | `run:0` |
| `mc0238` | 238 | rule | “The loop repeats until no invocation remains.” | The fixed-point loop repeats until no invocation remains: three levels of nested declaration macros all expand. | `run:0` |
| `mc0239` | 239 | rule | “struct-body macro may expand to a body containing another struct-body macro” | A struct-body macro may expand to a body containing another struct-body macro, which expands next round. | `run:0` |
| `mc0241` | 241 | rule | “Expansion precedes `comptime` evaluation” | Expansion precedes comptime evaluation: `comptime(#twice_m(21i32))` evaluates the expanded expression. | `run:0` |
| `mc0246` | 246 | example | “```nitpick” | `macro:m = () { #m(); };      // refused` — the self-invoking declaration is refused. | `refuse` |
| `mc0250` | 250 | rule | “limits one invocation's nesting” | A depth bound limits one invocation's nesting: an expression body nested 1000 operators deep is refused as a compile error. | `refuse` |
| `mc0250b` | 250 | rule | “limits” | An iteration bound limits the fixed-point loop: two declaration macros that invoke each other are refused as a compile error instead of looping. | `refuse` |
| `mc0251` | 251 | rule | “Exceeding either is an ordinary compile error naming the” | Exceeding the iteration bound is a compile error naming the macro and the chain that reached the bound: both ping_m and pong_m appear in the diagnostic. | `sh:0` |
| `mc0256` | 256 | rule | “one budget would report them alike” | The depth bound and the iteration bound are separate and report differently: a too-deep single expansion and a mutual recursion are refused with different diagnostic codes. | `sh:0` |
| `mc0264` | 264 | rule | “still in the program when expansion finishes is refused” | Every `#name(...)` still standing after expansion is refused, wherever it stands: an unknown one as a statement inside a loop body. | `refuse` |
| `mc0265` | 265 | rule | “as `MACRO-001` if the name is unknown” | An unknown `#name(...)` left standing at module level is NITPICK-MACRO-001. | `refuse:NITPICK-MACRO-001` |
| `mc0265b` | 265 | rule | “`MACRO-007` if the macro is” | An invocation of a macro declared in another module, left standing in expression position, is NITPICK-MACRO-007. | `refuse:NITPICK-MACRO-007` |
| `mc0266` | 266 | rule | “`MACRO-008` if it is `#caller`” | A `#caller(...)` left standing in an ordinary function (outside any macro) is NITPICK-MACRO-008. | `refuse:NITPICK-MACRO-008` |
| `mc0266b` | 266 | rule | “Only the three” | Only the three compiler builtins survive expansion. | untestable [vague] the text does not name the three builtins, and the references use more than three `#` builtins (`#size_of`, `#align_of`, `#wild_ptr`, `#unreachable`, `#sqrt`, `#caller`), so no program can tell which one the sentence says is refused |
| `mc0270` | 270 | rule | “`#totally_not_a_macro(3i32)` used to compile clean” | `#totally_not_a_macro(3i32)` in expression position is refused as NITPICK-MACRO-001 (it used to compile clean). | `refuse:NITPICK-MACRO-001` |
| `mc0278` | 278 | rule | “the scan afterwards cannot” | The expansion walk reaches every statement kind (a miss would arrive as a refusal): invocations in an if condition, a while condition and measure, a for body, a pick arm, a when body and then block, a nested block, a struct literal, an array literal, a call argument and a give all expand. | `run:0` |
| `mc0281` | 281 | rule | “A macro body is exempt” | A macro body is exempt from the leftover-invocation scan: an unknown invocation inside a macro that is never invoked is not refused. | `run:0` |
| `mc0290` | 290 | example | “```nitpick” | `comptime func:double` is a callable; `comptime(double(21i32))` forces it: 42. | `run:0` |
| `mc0296` | 296 | rule | “is a **keyword operator with a parenthesised operand**” | `comptime(expr)` is a keyword operator, not a call: its value is the plain int32, used with no `raw`. | `run:0` |
| `mc0296b` | 296 | rule | “keyword operator with a parenthesised operand” | The operand of `comptime` is parenthesised: `comptime 42i32` without parentheses is refused. | `refuse` |
| `mc0305` | 305 | row | “\| integer arithmetic \| throughout \|” | The comptime evaluator does integer arithmetic as the language does: `/`, `%` and negation agree with the run-time result for -7 and 2. | `run:0` |
| `mc0306` | 306 | row | “**mutable locals and assignment**” | The evaluator supports mutable locals and assignment, `x = x + n` and chains of them: accum(7) = 35. | `run:0` |
| `mc0307` | 307 | row | “**loops** — `loop(lo, hi, step) { … }`” | The evaluator runs `loop(lo, hi, step)`: a comptime sum over loop(0, 10, 3) equals the same loop run at run time. | `run:0` |
| `mc0308` | 308 | row | “calls to `comptime func:` declarations, nested” | The evaluator follows nested calls between comptime functions: sum_sq(3, 4) = 25. | `run:0` |
| `mc0309` | 309 | row | “**strings** — concatenation, equality, ordering, length” | The evaluator handles string concatenation, equality and length: len("ab" ++ "cde") = 5 and "ab" ++ "c" equals "abc". | `run:0` |
| `mc0309b` | 309 | row | “ordering” | The evaluator handles string ordering: "ab" orders before "b". | `run:0` |
| `mc0310` | 310 | row | “size and alignment intrinsics” | The evaluator folds the size intrinsic: `comptime(#size_of<int64>())` is 8. | `run:0` |
| `mc0310b` | 310 | row | “\| size and alignment intrinsics \|” | The evaluator folds the alignment intrinsic: `comptime(#align_of<int64>())` is 8. | `run:0` |
| `mc0311` | 311 | row | “built-in macros inside `comptime(…)`” | Built-in `#` forms are evaluated inside `comptime(…)`: `comptime(#size_of<int32>() * 2i64)` is 8. | `run:0` |
| `mc0312` | 312 | row | “`assert_static comptime(…)`” | `assert_static comptime(…)` is evaluated: a true proposition compiles. | `run:0` |
| `mc0312b` | 312 | row | “short-circuiting to the verifier” | `assert_static comptime(…)` over a false proposition halts compilation. | `refuse` |
| `mc0315` | 315 | rule | “executes loops and mutates locals” | The evaluator is an interpreter: it runs a `while` loop that mutates locals: tri(10) = 55. | `run:0` |
| `mc0316` | 316 | rule | “the compiler runs at build time” | What `comptime(...)` expresses runs at build time: the emitted IR carries no call to the comptime function. | `ir!:call[^\n]*@[\w.$]*tri_ct` |
| `mc0321` | 321 | example | “```nitpick” | Macros and comptime both ways: a macro body containing comptime (#four() = 4), comptime over an invocation (6), and nested arbitrarily (21). | `run:0` |
| `mc0327` | 327 | rule | “expansion runs to a fixed point first, then evaluation” | Expansion runs to a fixed point first, then evaluation runs over the result: a comptime function EMITTED by a macro can be evaluated. | `run:0` |
| `mc0332` | 332 | rule | “A `const` global folds” | A `const` global folds: `comptime(N * 2i32)` over `const int32:N = 4i32;` is 8. | `run:0` |
| `mc0334` | 334 | rule | “A `fixed`” | A `fixed` binding is not a constant: `comptime(F * 2i32)` over `fixed int32:F` is refused. | `refuse` |
| `mc0336` | 336 | rule | “local or a parameter of an ordinary function” | A local is not a constant: `comptime(loc + 1i32)` is refused. | `refuse` |
| `mc0336b` | 336 | rule | “a parameter of an ordinary function” | A parameter of an ordinary function is not a constant: `comptime(p + 1i32)` is refused. | `refuse` |
| `mc0338` | 338 | rule | “a call folds when the function is declared `comptime`” | A call folds only when the function is declared comptime: `comptime(four_rt())` over an ordinary (foldable) function is refused. | `refuse` |
| `mc0344` | 344 | rule | “The diagnostic names **the offending expression**” | A comptime failure inside nested comptime calls names the offending expression and the call chain: the diagnostic mentions inner_div and outer_call and points at the division. | `sh:0` |
| `mc0346` | 346 | rule | “A comptime failure is a compile error.” | A comptime evaluation that fails (division by zero inside a comptime function) is a compile error. | `refuse` |
| `mc0351` | 351 | rule | “A budget bounds the total work” | A budget bounds the total work: a comptime loop that never ends is NITPICK-TYPE-025. | `refuse:NITPICK-TYPE-025` |
| `mc0352` | 352 | rule | “a `comptime func:` that calls itself” | A depth bound bounds recursion: a comptime function that calls itself forever is NITPICK-TYPE-025, not a crashed compiler. | `refuse:NITPICK-TYPE-025` |
| `mc0356` | 356 | rule | “Exceeding either is `NITPICK-TYPE-025`” | Exceeding either evaluation bound is NITPICK-TYPE-025: two comptime functions recursing into each other are refused with it. | `refuse:NITPICK-TYPE-025` |
| `mc0368` | 368 | row | “\| `impl:Trait:for:Type` \| `impl:Type:Trait` \| D-030 \|” | The corpus's `impl:Trait:for:Type` is not this language: it is refused. | `refuse` |
| `mc0368b` | 368 | row | “`impl:Type:Trait`” | This language writes `impl:Type:Trait`. | `run:0` |
| `mc0369` | 369 | row | “\| `@sizeof(T)`, `@alignof(T)` \|” | The corpus's `@sizeof(T)` is not this language (`@` is address-of and nothing else): it is refused. | `refuse` |
| `mc0369b` | 369 | row | “`#size_of<T>()`” | This language writes `#size_of<T>()`: `#size_of<int64>()` is 8. | `run:0` |
| `mc0369c` | 369 | row | “`#align_of<T>()`” | This language writes `#align_of<T>()`: `#align_of<int64>()` is 8. | `run:0` |
| `mc0370` | 370 | row | “\| `expr ? default` \| the defaults operator \|” | The corpus's `expr ? default` is respelled: a bare `?` fallback is refused. | `refuse` |
| `mc0371` | 371 | row | “\| `0`, `10`, `exit 1` \|” | The corpus's width-less literals (`0`, `10`, `exit 1`) are not this language: they are refused (literals carry their width). | `refuse` |
| `mc0372` | 372 | row | “\| `func:main = int32()` \|” | The corpus's `func:main = int32()` is not this language: a main with no parameter is refused. | `refuse` |
| `mc0372b` | 372 | row | “`func:main = int32(cstring[]:argv)`” | This language writes `func:main = int32(cstring[]:argv)`. | `run:0` |
| `mc0373` | 373 | row | “\| `name!(args)` — the invocation \| **`#name(args)`** \|” | The corpus's invocation `name!(args)` is not this language: `make_pair!();` at module level is refused. | `refuse` |
| `mc0374` | 374 | row | “\| `MacroPattern` in a `pick` arm \| **removed** \|” | A MacroPattern in a pick arm (the corpus's `MyMacro!(a, b) where (a > b) { … }`) is removed: refused. | `refuse` |
| `mc0379` | 379 | rule | “there is no postfix `!` in the grammar” | There is no postfix `!`: `twice!(3i32)` in expression position is refused. | `refuse` |
| `mc0388` | 388 | rule | “the emitted function is literally called” | Substitution does not reach a declaration's name: `macro:m = (N) { func:N = …; };` emits a function literally named N (unimplemented rather than refused). | `run:0` |
| `mc0393` | 393 | rule | “a macro never renames what” | A macro never renames what it emits: a spliced method keeps its name and so satisfies the trait it implements. | `run:0` |
| `mc0394` | 394 | rule | “a collision is an error like any other name declared” | Two module-level invocations of one declaration macro emit one name twice: a collision is an error. | `refuse` |
| `mc0394b` | 394 | rule | “it emits** (D-128)” | Two splices of one field macro into one struct collide: refused. | `refuse` |
| `mc0405` | 405 | rule | “currently carries the macro's” | A diagnostic inside an expansion carries the macro body's location: "cannot find only_local" is reported at the macro BODY's line, not the invocation's. | `sh:0` |

## MEMORY (`meta/specs/MEMORY_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `me0005` | 5 | rule | “**There is no garbage collector** (D-003)” | There is no garbage collector: lifetimes are static. | untestable [vague] a design statement with no outcome of its own; the static lifetimes it names are claimed and tested at me0022 (scope), me0362 (handles) and me0119 (wild) |
| `me0007` | 7 | rule | “Nothing relocates memory” | Nothing relocates memory implicitly, and there are no collection pauses. | untestable [unobservable] a program sees no address to compare and no pause to time |
| `me0016` | 16 | rule | “a bare `T` is treated as owning” | In a generic body a bare T is owning: a copy of a T place is refused (TYPE-046), even when the only instantiation is int32. | `refuse:TYPE-046` |
| `me0018` | 18 | rule | “unless spelled `move(...)` or `.clone()`” | The permitted twin: in a generic body `move(x)` of a T place is accepted, and at int32 the value arrives. | `run:0` |
| `me0019` | 19 | rule | “`pick` binds a `T` payload as a VIEW in place” | A lending pick binds a T payload as a view in place (D-266) and a consuming one moves it. | untestable [internal] whether a T payload binds as a view or a move inside a generic body shows only through the loan rules' refusals; the grid's F-002 and DEF-104 cells measure those |
| `me0020` | 20 | rule | “The `move` of a scalar is its copy” | The move of a scalar is its copy: a generic function moving its T at int64 hands the value back, and the caller's own copy is still the same value. | `run:0` |
| `me0022` | 22 | rule | “a value's last textual use does not shorten its life” | A managed binding is dropped when its scope exits and at no earlier point: two lists in one block, the first last used before the second exists, are both live at once. | `run:0` heap `24000/24000/2` |
| `me0022b` | 22 | rule | “after the scope's joins and `defer`s” | A binding is dropped after its scope's defers: a defer reading the string at the scope's exit sees it intact. | `run:0` |
| `me0022c` | 22 | rule | “before its channel reclaims” | A scope's drops run before its channel reclaims. | untestable [unobservable] a channel's reclaim is not built (CONCURRENCY:489-490), so no order between it and a drop can be seen |
| `me0023` | 23 | example | “```nitpick” | `int32:x = 42i32;` is a managed binding that holds 42. | `run:0` |
| `me0031` | 31 | rule | “dropped **when its statement ends**” | A temporary is dropped when its statement ends: two statements each reading a field of a list nobody keeps peak at the larger list alone. | `run:0` heap `24000/16000/2` |
| `me0035` | 35 | rule | “The same drop runs on every path out of the statement” | The temporary's drop runs on every path out of its statement, a `relay` included: three calls whose statement relays a failure after building a list peak at one list. | `run:0` heap `24000/8000/3` |
| `me0037` | 37 | rule | “condition dies with the condition” | A temporary that feeds a loop's condition dies with the condition: four evaluations of a while's condition, each building a list, peak at one list. | `run:0` heap `32000/8000/4` |
| `me0037b` | 37 | rule | “Under `await` the temporaries” | Under await the temporaries of the awaiting statement live in the frame. | untestable [internal] where a temporary is stored across a suspension is the lowering's; no program sees a frame slot |
| `me0039` | 39 | rule | “`tests/backend/programs/temp_*.npk`” | The compiler's temp_*.npk programs and the cost stage's temporaries probe pin the rule. | untestable [tree] a statement about the compiler repository's tests and harness |
| `me0045` | 45 | rule | “**Its buffer is managed storage (D-263, 1.5.2e).**” | A List's buffer is managed storage: a List alive in main at `exit 0` is not a leak the exit check reports. | `run:0` |
| `me0052` | 52 | rule | “`alloc_managed` is the PRELUDE's own (TYPE-054 elsewhere)” | alloc_managed is the prelude's own: a program calling it is refused, TYPE-054. | `refuse:TYPE-054` |
| `me0053` | 53 | rule | “hand-written `wild` container relies on D-151's count” | A wild block unpaired at a successful exit is counted: the exit check traps WildLeak. | `trap:WildLeak` |
| `me0057` | 57 | rule | “its generated drop releases the” | A List's generated drop releases its elements through T's drop and hands the block back: a List of two lists dropped at its block's end leaves room, so a later list peaks alone. | `run:0` heap `48048/32000/4` |
| `me0059` | 59 | rule | “vacant List (`cap == 0`, D-225) owns nothing” | A vacant List owns nothing: a list moved out of drops nothing at its scope's end (no double free). | `run:0` |
| `me0061` | 61 | rule | “never copy it binding to binding” | List is move-only: copying a List binding to another is refused, TYPE-046. | `refuse:TYPE-046` |
| `me0061b` | 61 | rule | “with a `move T:p` parameter” | A List is consumed by a `move T:p` parameter. | `run:0` |
| `me0061c` | 61 | rule | “It is declared” | List and its functions are declared in the prelude. | untestable [tree] where the declaration is written; that List needs no import is the premise of every List claim here |
| `me0068` | 68 | rule | “`items` is not touched (TYPE-080)” | Outside the prelude a List's `items` is not touched: reading it is refused, TYPE-080. | `refuse:TYPE-080` |
| `me0068b` | 68 | rule | “and `count` and `cap` are read but” | Outside the prelude a List's `cap` is not written: assigning it is refused, TYPE-079. | `refuse:TYPE-079` |
| `me0068c` | 68 | rule | “`count` and `cap` are read but” | count and cap are read outside the prelude. | `run:0` |
| `me0074` | 74 | rule | “bounds-checked against `count`” | `l[i]` is bounds-checked against count, not cap: index 1 of a cap-4 list holding one element traps OutOfBounds. | `trap:OutOfBounds` |
| `me0075` | 75 | rule | “read it, write it, compound it” | `l[i]` is a place: written, then compounded, it reads the result. | `run:0` |
| `me0077` | 77 | rule | “owning element drops the old value” | Assigning over an owning element drops the old value: a list of lists whose element is replaced, then a larger list, peak without the old element. | `run:0` heap `32024/24024/4` |
| `me0078` | 78 | rule | “element is live or vacant after a move” | An element moved out is vacant, never unowned: the list's drop does not free it again. | `run:0` |
| `me0079` | 79 | rule | “is a checked `T[]` view of elements” | `l[lo...hi]` is a T[] view of elements lo to hi-1. | `run:0` |
| `me0080` | 80 | rule | “list (D-249)” | A range view borrows the list: list_push while the view lives is refused, BORROW-015. | `refuse:BORROW-015` |
| `me0081` | 81 | rule | “A list behind a pointer is `(<-p)[i]`” | A list behind a pointer is indexed as `(<-p)[i]`. | `run:0` |
| `me0081b` | 81 | rule | “`p[i]` on a pointer to an array” | `p[i]` on a pointer to a List is refused, TYPE-082. | `refuse:TYPE-082` |
| `me0085` | 85 | rule | “`list_push`, `list_reserve`” | list_push appends and list_reserve makes room for `need` more elements beyond the count. | `run:0` |
| `me0086` | 86 | rule | “`list_pop` (the last element, moved out)” | list_pop moves the last element out. | `run:0` |
| `me0087` | 87 | rule | “`list_truncate(l, n)` (drops `n…count−1`)” | list_truncate(l, n) keeps elements 0 to n-1. | `run:0` |
| `me0088` | 88 | rule | “`list_clear`” | list_clear empties the list. | `run:0` |
| `me0089` | 89 | rule | “`list_insert(l, i, v)` (`i` in `[0, count]`)” | list_insert(l, i, v) inserts at i for i in [0, count]: at 0 it shifts, at count it appends. | `run:0` |
| `me0090` | 90 | rule | “`list_remove(l, i)` (order kept)” | list_remove(l, i) removes element i and keeps the order of the rest. | `run:0` |
| `me0091` | 91 | rule | “`list_swap_remove(l, i)` (the last element moved into the hole)” | list_swap_remove(l, i) moves the last element into the hole. | `run:0` |
| `me0093` | 93 | rule | “An index outside the list is `OutOfBounds`, whatever spells it” | An index outside the list is OutOfBounds whatever spells it: list_insert at count + 1 traps. | `trap:OutOfBounds` |
| `me0093b` | 93 | rule | “whatever spells it” | list_remove at count traps OutOfBounds. | `trap:OutOfBounds` |
| `me0099` | 99 | rule | “`pass` moves the returned value out implicitly” | `pass h.name` moves the field out and the root stops owning it: h's drop does not free it, and the caller reads it intact. | `run:0` |
| `me0101` | 101 | rule | “**A value whose type does” | A value whose type does not drop transfers nothing: `pass g.n` copies the number and g's drop still frees its owning sibling, so three calls peak at one list. | `run:0` heap `24000/8000/3` |
| `me0107` | 107 | rule | “**One exception (D-251, 1.5.2)**” | A move out of an owning field of a limit<Rules> binding is refused, TYPE-063. | `refuse:TYPE-063` |
| `me0110` | 110 | rule | “move the whole binding, or copy the part” | The permitted twin: the whole limited binding moves. | `run:0` |
| `me0113` | 113 | rule | “Forces explicit allocation onto the hardware call stack” | A `stack` binding is on the call stack, reclaimed exactly at its scope's exit, a pointer bump. | untestable [unobservable] where a scalar lives and when its stack slot is reclaimed are not visible; the frame-size consequence is me0530 |
| `me0114` | 114 | example | “```nitpick” | `stack int32:counter = 0i32;` compiles and holds 0. | `run:0` |
| `me0119` | 119 | rule | “If you fail to free a `wild` pointer” | A wild pointer never freed is a leak reported on exit: WildLeak. | `trap:WildLeak` |
| `me0119b` | 119 | rule | “They explicitly bypass RAII tracking” | A wild pointer bypasses RAII: its block is not freed at its scope's exit (the exit check still sees it after the block). | `trap:WildLeak` |
| `me0120` | 120 | example | “```nitpick” | `wild int8->:buffer = alloc(1024i64);` allocates a wild block (freed here with dalloc). | `run:0` |
| `me0125` | 125 | rule | “adhering to W⊕X” | wildx memory follows W^X, with ASLR and guard pages. | untestable [unobservable] page permissions and placement are not visible; the W^X refusals are VERIFICATION:790-791's claims |
| `me0126` | 126 | example | “```nitpick” | `wildx uint8->:code = wildx_alloc(4096i64);` allocates an executable page (freed here). | `compile` |
| `me0132` | 132 | rule | “Casting an integer to a pointer is illegal in ordinary code” | Casting an integer to a pointer is refused in ordinary code. | `refuse` |
| `me0133` | 133 | rule | “legal only in `wild` context (D-019)” | #wild_ptr is legal only in wild context: bound to a plain pointer, it is refused. | `refuse` |
| `me0135` | 135 | example | “```nitpick” | `wild int8->:page = #wild_ptr<int8->>(addr);` builds a wild pointer from an address. | `run:0` |
| `me0144` | 144 | rule | “Nitpick uses static analysis to prevent leaks at compile time” | Static analysis prevents wild leaks at compile time. | untestable [vague] no leak is named that the compiler refuses; the run-time check (me0053, me0119) is what the reference shows catching one |
| `me0147` | 147 | rule | “This guarantees the free runs on every normal exit path” | A defer runs on every normal exit path, a `fail` included: the callee's wild block is freed, so main's `exit 0` finds no leak. | `run:0` |
| `me0147b` | 147 | rule | “or `exit`)” | A defer runs on `exit`: main's deferred free runs before the exit check. | `run:0` |
| `me0149` | 149 | rule | “**`defer` does not run on a trap.**” | A defer does not run on a `?!` trap: control reaches failsafe's arm for the raised error without the defer (which would divide by zero). | `run:81` |
| `me0149b` | 149 | rule | “`!!!` and `?!` transfer control directly to” | `!!!` transfers control directly to failsafe without running a defer. | `run:81` |
| `me0152` | 152 | rule | “`failsafe` receives the allocation registry intact” | failsafe receives the allocation registry intact: wild_live_count() inside it counts the block main left live. | `run:42` |
| `me0155` | 155 | rule | “allocates from a preallocated REGION” | failsafe allocates from a preallocated region: a small allocation inside it succeeds. | `run:42` |
| `me0158` | 158 | rule | “exhaustion is `HeapOom`” | The region is one mebibyte: a 2 MiB allocation inside failsafe is HeapOom there, which the re-entry rule ends at exit 70. | `run:70` |
| `me0161` | 161 | rule | “`failsafe` that waited for it would hang with no deadline” | A failsafe never waits for the heap's mutex. | untestable [timing] a thread parked inside the allocator at the stop is a race no single run arranges |
| `me0166` | 166 | example | “```nitpick” | `wild int8->:buf = alloc(16i64); defer { dalloc(buf); }` frees the block at the scope's exit. | `run:0` |
| `me0172` | 172 | rule | “The `nodrop` keyword acts as a per-binding RAII opt-out” | `nodrop` opts one binding's initialiser out of the auto-drop tracker. | untestable [vague] the text gives no managed initialiser whose drop `nodrop` would suppress observably; the example (me0173) is a wild one |
| `me0173` | 173 | example | “```nitpick” | `wild int8->:manual_buf = nodrop alloc(16i64);` compiles (freed here with dalloc). | `run:0` |
| `me0179` | 179 | rule | “`move(place)` transfers ownership out of a binding and invalidates the source” | move(place) invalidates the source: freeing the moved-from wild binding is refused. | `refuse` |
| `me0183` | 183 | example | “```nitpick” | The example: `free(buffer)` after `move(buffer)` is refused as NITPICK-019 (use after move). | `refuse:NITPICK-019` |
| `me0191` | 191 | rule | “**Ownership moves only where `move` is written.**” | Passing an owning value to a function borrows it: the caller still owns it afterwards. | `run:0` |
| `me0194` | 194 | rule | “Any read is” | A moved-from binding is invalid: any read of it is refused. | `refuse` |
| `me0195` | 195 | rule | “**reinitialized by assignment**” | A moved-from binding may be reinitialized by assignment, after which it is live again. | `run:0` |
| `me0196` | 196 | rule | “A `fixed` binding cannot be” | A fixed binding cannot be reinitialized: it cannot be assigned at all. | `refuse` |
| `me0198` | 198 | rule | “`move` is **not** a memory qualifier” | `move` is not a memory qualifier: a declaration qualified `move` is refused. | `refuse` |
| `me0199` | 199 | rule | “It is a keyword operator with a parenthesized operand” | move takes a parenthesized operand: `move s` without parentheses is refused. | `refuse` |
| `me0202` | 202 | rule | “`$$m place` excludes every other access” | `$$m place` excludes every other access while it lives: reading the place is BORROW-013. | `refuse:BORROW-013` |
| `me0203` | 203 | rule | “`$$i place` admits readers and excludes writers” | `$$i place` admits readers: a plain read beside it is accepted. | `run:0` |
| `me0203b` | 203 | rule | “excludes writers” | `$$i place` excludes writers: assigning the place while it lives is BORROW-013. | `refuse:BORROW-013` |
| `me0203c` | 203 | rule | “`@place` is a” | `@place` is a plain address with no claim: writing the place beside it is accepted, and the address sees the write. | `run:0` |
| `me0206` | 206 | rule | “a computed-index overlap is” | A computed-index overlap of two `$$m` claims is guarded at run time: BorrowOverlap. | `trap:BorrowOverlap` |
| `me0208` | 208 | rule | “**A view's root is frozen while the view is live**” | A view's root is frozen while the view lives: assigning the root is BORROW-015. | `refuse:BORROW-015` |
| `me0217` | 217 | rule | “Reads, `$$i`, a disjoint field” | Reads of a view's root stay legal while the view lives. | `run:0` |
| `me0221` | 221 | rule | “End the view's block” | Ending the view's block before writing its root is accepted. | `run:0` |
| `me0225` | 225 | rule | “cannot travel up (`NITPICK-BORROW-001`” | A by-value parameter's frame storage cannot travel up: returning its address is BORROW-001. | `refuse:BORROW-001` |
| `me0228` | 228 | rule | “is a view of a temporary” | A temporary handed to a callee that views it is a view of a temporary: BORROW-012. | `refuse:BORROW-012` |
| `me0230` | 230 | rule | “**What a call stores is read off the callee's own body**” | What a call stores is read off the callee's own body (D-325's summaries). | untestable [internal] the analysis's method; its outcomes are the BORROW refusals and acceptances claimed at me0208-me0228 |
| `me0242` | 242 | rule | “A plain by-value parameter of an OWNING type is a loan and is read-only” | A plain by-value parameter of an owning type is a read-only loan: assigning it is TYPE-085. | `refuse:TYPE-085` |
| `me0245` | 245 | rule | “changes an owning value takes it as `move T:p`” | A callee that changes an owning value takes it as `move T:p`. | `run:0` |
| `me0246` | 246 | rule | “a copyable parameter is a copy and keeps every write” | A copyable parameter is a copy: the callee's writes stay in the callee. | `run:0` |
| `me0247` | 247 | rule | “A `fixed` binding has no address” | A fixed binding has no address: `@F` is TYPE-071. | `refuse:TYPE-071` |
| `me0248` | 248 | rule | “cannot be moved out of” | An owning fixed binding cannot be moved out of: `move(FS)` is TYPE-084. | `refuse:TYPE-084` |
| `me0250` | 250 | rule | “`.clone()` is” | `.clone()` is the reading of an owning fixed binding. | `run:0` |
| `me0251` | 251 | rule | “and no PART of one is written after its declaration” | No part of a fixed binding is written after its declaration: an element store is TYPE-086. | `refuse:TYPE-086` |
| `me0255` | 255 | rule | “`NITPICK-ASSIGN-002`” | The whole fixed binding's second assignment stays ASSIGN-002. | `refuse:ASSIGN-002` |
| `me0262` | 262 | rule | “2^47 bytes (140,737,488,355,328” | A request above 2^47 bytes is a bad request: alloc(2^47 + 1) traps HeapBadRequest. | `trap:HeapBadRequest` |
| `me0268` | 268 | rule | “a compare that reads a negative size as” | The one compare reads a negative size as a huge one: alloc(-1) traps HeapBadRequest. | `trap:HeapBadRequest` |
| `me0269` | 269 | rule | “Exactly the ceiling is legal” | Exactly the ceiling is legal: alloc(2^47) is not a bad request, and the kernel's refusal is HeapOom. | `trap:HeapOom` |
| `me0276` | 276 | rule | “**`alloc(size)`**: Allocate `size` uninitialized bytes” | alloc(size) gives size bytes the program can write and read back. | `run:0` |
| `me0277` | 277 | rule | “**`calloc(count, size)`**: Allocate zero-initialized memory” | calloc(count, size) allocates zero-initialized memory. | `run:0` |
| `me0278` | 278 | rule | “**`ralloc(ptr, new_size)`**: Resize the allocation” | ralloc resizes the allocation and keeps its contents. | `run:0` |
| `me0278b` | 278 | rule | “Old pointer becomes invalid” | After ralloc the old pointer is invalid: freeing it is refused. | `refuse` |
| `me0281` | 281 | rule | “There are **no aliases**” | There are no aliases: `realloc` is refused. | `refuse` |
| `me0285` | 285 | rule | “**`aalloc(size, align)`**” | aalloc(size, align) serves an alignment above sixteen. | `run:0` |
| `me0288` | 288 | rule | “a hidden 16-byte header” | Every heap allocation carries a hidden 16-byte header: the size and a keyed magic word. | untestable [internal] the header is out of the payload a program may read |
| `me0290` | 290 | rule | “double-free and header corruption and routes them to `failsafe`” | The allocator detects a double free the static analysis cannot follow and routes it to failsafe (-4102, Unreachable): a pointer freed twice through a callee. | `trap:Unreachable` |
| `me0292` | 292 | rule | “the multiply is CHECKED” | calloc's count x size is checked: an overflowing product traps HeapBadRequest. | `trap:HeapBadRequest` |
| `me0293` | 293 | rule | “`ralloc(p, 0)`” | ralloc(p, 0) is a malformed request: HeapBadRequest. | `trap:HeapBadRequest` |
| `me0293b` | 293 | rule | “a non-power-of-two alignment” | A non-power-of-two alignment is a malformed request: aalloc(64, 48) traps HeapBadRequest. | `trap:HeapBadRequest` |
| `me0301` | 301 | rule | “binding is additionally a compile-time error (D-119)” | Double-free of a tracked binding is a compile-time error. | `refuse` |
| `me0305` | 305 | rule | “a garbage” | dalloc proves a pointer lies in allocator-owned memory first: a garbage pointer is one of the allocator's traps, never a wild load (failsafe here maps HeapBadRequest, HeapOom and Unreachable to 42, MachineFault to 43). | `run:42` |
| `me0306` | 306 | rule | “The heap is single-threaded at this” | The heap is single-threaded at this rung. | untestable [vague] a statement about a past rung; the heap has had a mutex since D-291 (line 160) |
| `me0312` | 312 | rule | “from `alloc`, `aalloc`, `calloc` and a `ralloc` of one” | Every calloc block is counted: one unpaired at `exit 0` traps WildLeak. | `trap:WildLeak` |
| `me0313` | 313 | rule | “never managed storage: a string's” | The exit check never counts managed storage: a string alive in main at `exit 0` is not reported. | `run:0` |
| `me0316` | 316 | rule | “so an owning local of” | exit runs no drops, so an owning local of main is never dropped by a program that exits. | untestable [unobservable] a managed body freed or not at exit is the kernel's either way; no program reads it after exit |
| `me0328` | 328 | rule | “**`wild_live_count()`**” | wild_live_count() counts the live wild blocks. | `run:0` |
| `me0333` | 333 | rule | “with a non-empty set routes to `failsafe`” | A successful exit with a non-empty set routes to failsafe with -4105 (WildLeak). | `trap:WildLeak` |
| `me0334` | 334 | rule | “A failure exit keeps its code” | A failure exit keeps its code: `exit 3` with a live wild block exits 3. | `run:3` |
| `me0337` | 337 | rule | “followed by `exit` and by” | wild_release_all() is followed by exit and nothing else: another statement after it is TYPE-062. | `refuse:TYPE-062` |
| `me0339` | 339 | rule | “drops every chunk and” | failsafe may call wild_release_all() then exit positive: the leak's handler exits 42. | `run:42` |
| `me0342` | 342 | rule | “same flag makes a trap RAISED INSIDE failsafe exit 70 directly” | A trap raised inside failsafe exits 70 directly instead of recursing. | `run:70` |
| `me0345` | 345 | rule | “**One registry mechanism, three clients**” | One registry mechanism serves the allocation tables, the stream registry and the driver registry. | untestable [internal] the runtime's table layout |
| `me0358` | 358 | rule | “allocate the graph” | Arenas handle cycles: a graph is allocated in an arena and dropped wholesale. | untestable [vague] a pattern of use; the arena's operations are claimed at me0390-me0397 |
| `me0362` | 362 | rule | “Attempting to use the old handle immediately fails safely” | A handle whose slot was freed fails safely through Result, never a silent use-after-free. | `run:0` |
| `me0364` | 364 | rule | “Handles are **indices, not pointers**” | Handles are indices, safe across arena growth: ten slots in an arena made for two all read back. | `run:0` |
| `me0368` | 368 | rule | “lowers into a 16-byte aligned struct” | Handle<T> is a 16-byte struct. | `run:0` |
| `me0368b` | 368 | rule | “(`%Handle = type { i64, i32 }` in LLVM IR)” | Handle<T> is `{ i64, i32 }` in the IR: a function taking one has that parameter type. | `ir:^define [^\n]*@"[^"]*\.hh"\(\{ ?i64, i32 ?\}` |
| `me0369` | 369 | rule | “**Bytes [0-7]**: `uint64:index`” | Bytes 0-7 are the index, 8-11 the generation, 12-15 padding. | untestable [internal] a handle's bytes are not readable from a program; the field order is me0368b's IR test |
| `me0375` | 375 | rule | “Creation is the **`arena_make(cap)`** builtin” | Creation is arena_make(cap), type-directed by the annotation. | `run:0` |
| `me0377` | 377 | rule | “wrote `arena<int64>.alloc(1000)`” | The old spelling `arena<int64>.alloc(1000)` (creation on the type) is not the language. | `refuse` |
| `me0381` | 381 | example | “```nitpick” | The example compiles and runs: put 41, `get(h) ? 0i64` reads it, then free and destroy. | `run:0` |
| `me0390` | 390 | rule | “The set is `alloc() -> Handle<T>`” | The arena's set is alloc, get, put, free, reset and destroy, with their stated results. | `run:0` |
| `me0392` | 392 | rule | “`get` returns the element” | get returns the element by value: changing the copy leaves the slot. | `run:0` |
| `me0394` | 394 | rule | “A stale handle fails” | A stale handle fails get, put and free with -4106 (StaleHandle) in Result.err, never a trap. | `run:0` |
| `me0396` | 396 | rule | “`destroy` CONSUMES the arena” | destroy consumes the arena at compile time: using it afterwards is refused. | `refuse` |
| `me0397` | 397 | rule | “un-destroyed arena is a wild-role leak the exit-time check names” | An un-destroyed arena is a wild-role leak the exit check names: WildLeak at `exit 0`. | `trap:WildLeak` |
| `me0399` | 399 | rule | “`?` takes a **fallback value**” | `?` takes a fallback value: a stale get with `? 0i64` yields 0. | `run:0` |
| `me0399b` | 399 | rule | “`?!` takes a **failsafe error” | `?!` takes a failsafe error code and traps: a stale get with `?! E2` reaches E2's arm. | `run:82` |
| `me0404` | 404 | rule | “`.` handles all member access and auto-dereferences pointers” | `.` auto-dereferences a pointer: `p.n` through a Box-> reads the field. | `run:0` |
| `me0408` | 408 | example | “```nitpick” | An arena embedded in a struct: `app.my_arena.alloc()` works as member-place addressing. | `compile` |
| `me0418` | 418 | rule | “The surface `arena<T>` is a **fixed-slot** allocator” | The executor frame allocator is not arena<T>: arena<T> hands out fixed-slot indices. | untestable [internal] the coroutine frame allocator is the runtime's |
| `me0424` | 424 | rule | “runtime-internal — no keyword, no” | The executor frame allocator is runtime-internal, no builtin: npk_frame_alloc is not callable. | `refuse` |
| `me0434` | 434 | rule | “an un-destroyed executor is a countable leak” | The executor and its chunks are wild-role blocks; an un-destroyed executor is a countable leak. | untestable [internal] no program holds an executor to leave undestroyed |
| `me0439` | 439 | rule | “`arena<T>` is **single-threaded**” | arena<T> is single-threaded: handing one to a thread is refused. | `refuse` |
| `me0449` | 449 | row | “\| Threading \| single-threaded \| multi-threaded \|” | A shared_arena is multi-threaded: a thread allocates in it, and after the join the owner reads the value through the handle the thread returned on a channel. | `run:0` |
| `me0450` | 450 | row | “\| Operations \| `alloc`, `get`, `free`, `reset`, `destroy` \|” | A shared_arena has only alloc, get and destroy: `reset` is refused. | `refuse` |
| `me0451` | 451 | row | “\| Per-slot `free` \| yes \| **no** \|” | A shared_arena has no per-slot free: `s.free(h)` is refused. | `refuse` |
| `me0452` | 452 | row | “\| Storage \| may reallocate on growth \| **chunked, never moves** \|” | A shared arena's storage is chunked and never moves; an arena<T>'s may reallocate. | untestable [unobservable] no operation yields an address to compare before and after growth |
| `me0453` | 453 | row | “\| Cost \| zero \| one atomic bump per allocation \|” | An arena<T> allocation costs nothing extra; a shared arena's one atomic bump. | untestable [internal] the allocation paths are the runtime's (npk_arena_*, npk_sarena_*) |
| `me0455` | 455 | rule | “Dropping per-slot `free` is what makes concurrency safe” | Dropping per-slot free makes concurrency safe without epochs, hazard pointers or counting. | untestable [vague] the rationale for the contract; the contract is me0450-me0451 |
| `me0461` | 461 | rule | “`destroy` requires that no thread still holds handles” | destroy requires that no thread still holds the arena: destroying it while a spawned thread holds it is refused. | `refuse` |
| `me0464` | 464 | rule | “creation is `shared_arena_make(cap)`” | Creation is shared_arena_make(cap), type-directed like arena_make. | `run:0` |
| `me0465` | 465 | rule | “the surface value is ONE POINTER” | A shared_arena's surface value is one pointer: 8 bytes. | `run:0` |
| `me0467` | 467 | rule | “**`alloc(v)` carries the value**, because there is no `put`” | A shared arena has no `put`: `s.put(h, v)` is refused. | `refuse` |
| `me0471` | 471 | rule | “`get` COPIES” | A shared arena's get copies: changing the copy leaves the slot. | `run:0` |
| `me0474` | 474 | rule | “RESERVES a capacity range with one atomic `fetch_add`” | Growth reserves a capacity range with one atomic fetch_add and publishes the chunk by CAS. | untestable [internal] the runtime's growth protocol; its model is VERIFICATION §9's |
| `me0476` | 476 | rule | “chunk sizes are geometric” | Chunk sizes are geometric, capped at 65536 slots. | untestable [internal] chunk sizes are not visible to a program |
| `me0479` | 479 | rule | “`arena<T>` issues generations starting at 2” | Shared handles carry generation 0 and arena<T>'s start at 2: an arena<T> handle in a shared get is refused as stale (StaleHandle), not read. | `run:0` |
| `me0481` | 481 | rule | “`destroy` consumes the binding at compile time” | A shared arena's destroy consumes the binding at compile time: a use after it is MOVE-002. | `refuse:MOVE-002` |
| `me0482` | 482 | rule | “an un-destroyed shared arena is a wild-role leak” | An un-destroyed shared arena is a wild-role leak the exit check names: WildLeak. | `trap:WildLeak` |
| `me0488` | 488 | rule | “`ulimit -s` and `RLIMIT_STACK` do not size any” | ulimit -s does not size the main thread's stack: a recursion using about 4 MiB runs to 0 under `ulimit -s 512`. | `sh:0` |
| `me0491` | 491 | rule | “Each stack is ONE anonymous mapping” | Each stack is one anonymous mapping, lowest address first. | untestable [internal] a mapping's layout is not visible to a program |
| `me0496` | 496 | row | “\| guard (`PROT_NONE`) \| 4 KiB \| yes \| yes \| yes \|” | Each stack starts with a 4 KiB PROT_NONE guard (main, spawned and failsafe). | untestable [unobservable] reaching a guard page needs an address below the frame |
| `me0497` | 497 | row | “\| signal stack \| 64 KiB \| yes \| yes \| — \|” | Main and spawned threads have a 64 KiB signal stack. | untestable [internal] the signal stack's size is not visible |
| `me0498` | 498 | row | “\| guard (`PROT_NONE`) \| 4 KiB \| yes \| yes \| — \|” | A second 4 KiB guard sits above the signal stack. | untestable [unobservable] as me0496 |
| `me0499` | 499 | row | “\| reserve (below the limit word) \| 64 KiB \| yes \| yes \| yes \|” | A 64 KiB reserve lies below the limit word. | untestable [internal] the reserve is the floor's; no emitted function may enter it |
| `me0500` | 500 | row | “\| usable \| — \| 8 MiB \| 2 MiB \| 1 MiB \|” | The main thread's usable stack is 8 MiB: a recursion using about 4 MiB runs. | `run:0` |
| `me0500b` | 500 | row | “\| 2 MiB \|” | A spawned thread's usable stack is 2 MiB: the same 4 MiB recursion on a thread traps StackExhausted. | `trap:StackExhausted` |
| `me0502` | 502 | rule | “**The check is in every function the compiler emits.**” | Every function the compiler emits carries LLVM's split-stack prologue. | `ir:^define [^\n]*@"[^"]*\.plain"\([^)]*\) "split-stack"` |
| `me0505` | 505 | rule | “Crossing it enters the trap route” | Crossing the limit enters the trap route as StackExhausted: an unbounded recursion traps it. | `trap:StackExhausted` |
| `me0506` | 506 | rule | “which every `failsafe` names because every program” | Every failsafe names StackExhausted: one that does not is refused. | `refuse` |
| `me0507` | 507 | rule | “A frame larger than a page is refused at the prologue” | A frame larger than a page is refused at its prologue: StackExhausted, not a jump over the guard. | `trap:StackExhausted` |
| `me0509` | 509 | rule | “The” | The floor's own functions carry no prologue and fit in the reserve. | untestable [internal] the runtime's functions; a belt proves it (VERIFICATION §9.5) |
| `me0512` | 512 | rule | “**`failsafe` runs on a stack of its own**” | failsafe runs on its own stack: entered by StackExhausted, it still has room for a recursion of about 512 KiB. | `run:42` |
| `me0514` | 514 | rule | “an overflow inside `failsafe` meets” | An overflow inside failsafe meets the re-entry rule and exits 70. | `run:70` |
| `me0515` | 515 | rule | “**Signals run on the thread's signal stack**” | Signals run on the thread's signal stack (SA_ONSTACK). | untestable [internal] which stack a signal frame lands on is not visible |
| `me0520` | 520 | rule | “**A spawned thread's stack is released at its join**” | A spawned thread's stack is unmapped at its join. | untestable [unobservable] a mapping's release shows only in the process's maps, which a program here does not read |
| `me0526` | 526 | rule | “a program spawn and” | Threads are spawned and joined without limit: two hundred in sequence, each joined, run. | `run:0` |
| `me0527` | 527 | rule | “The 65th LIVE thread is refused at its start” | The 65th live thread is refused at its start. | untestable [vague] the outcome of the refusal (a trap, an error, its identity) is not stated |
| `me0530` | 530 | rule | “**A `stack` binding (§1.2) lives in the frame of the function that declares” | A `stack` binding lives in its function's frame: a large stack array is a large frame, refused at the prologue (StackExhausted). | `trap:StackExhausted` |

## MODULE (`meta/specs/MODULE_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `md0013` | 13 | example | “```nitpick” | An inline module with a `pub` and a private function compiles, and its `pub` member is called qualified: `network.connect()` is 0. | `run:0` |
| `md0016` | 16 | rule | “// Private” | A member written without `pub` is private: `network.internal()` from outside the module is refused. | `refuse` |
| `md0021` | 21 | example | “```nitpick” | `mod:network;` after the header loads `network.npk` beside the file, and `network.connect()` calls into it. | `run:0` |
| `md0024` | 24 | rule | “or `network/mod.npk` relative to the declaring file” | With no `network.npk`, `mod:network;` loads `network/mod.npk` (whose header is `mod:network;`). | `sh:0` |
| `md0024b` | 24 | rule | “relative to the declaring file” | A `mod:b;` written in `sub/a.npk` loads `sub/b.npk`, not the `b.npk` beside the root. | `sh:0` |
| `md0026` | 26 | rule | “`network.MAX` reads its binding” | After `mod:network;`, `network.MAX` reads the file's `pub` binding (42). | `run:0` |
| `md0027` | 27 | rule | “`use network.*;`” | After `mod:network;`, `use network.*;` binds the file's `pub` names bare. | `run:0` |
| `md0027b` | 27 | rule | “`use network.{connect};`” | After `mod:network;`, `use network.{connect};` binds `connect` bare. | `run:0` |
| `md0028` | 28 | rule | “a `pub mod:network;` is” | A `pub mod:network;` in `mid.npk` is re-exported with its scope by `use "./mid.npk".*;`: `network.connect()` and `network.MAX` work in the importer. | `run:0` |
| `md0030` | 30 | rule | “one meaning with `use "./network.npk" as network;`” | `use "./network.npk" as network;` gives the same symbol: `network.connect()` and `network.MAX` work through it. | `run:0` |
| `md0030b` | 30 | rule | “one `inner` field” | The alias, the file import and the re-export share one `inner` field and one lookup. | untestable [internal] the symbol's field and lookup are the compiler's data structures; md0028 and md0030 test what a program sees of them |
| `md0031` | 31 | rule | “The link is made when every module has been” | A re-export is linked after every module is collected: a name imported through a `pub mod:` that another file re-exports is bound, not empty. | `run:0` |
| `md0034` | 34 | rule | “a `use` in any of its forms” | A `use "./lib.npk".*;` written inside an inline module binds into that module's scope. | `run:0` |
| `md0034b` | 34 | rule | “a `pub use`” | A `pub use` inside an inline module re-exports through it: `m.f()` reaches the imported function. | `run:0` |
| `md0035` | 35 | rule | “and a `mod:name;` written inside `mod:m = { … }` bind into `m`'s scope” | A `mod:lib;` written inside an inline module loads `lib.npk` beside the FILE and binds `lib` in the module's scope. | `run:0` |
| `md0036` | 36 | rule | “under the same rounds and refusals as at” | An import inside an inline module is refused as at file level: a `use` of a file that does not exist is refused. | `refuse` |
| `md0037` | 37 | rule | “and `use m.*;` binds what `m` re-exports” | `use m.*;` binds what the inline module `m` re-exports with `pub use`. | `run:0` |
| `md0038` | 38 | rule | “sealed from its file's imports” | An inline module is sealed from its file's imports: a name the file imports is not visible inside the module. | `refuse` |
| `md0042` | 42 | rule | “`mod:<dir>;` for a `dir/mod.npk`” | A `dir/mod.npk`'s header is `mod:<dir>;`: a `network/mod.npk` whose header is `mod:mod;` names another module and is refused, NITPICK-RESOLVE-012. | `sh:0` |
| `md0043` | 43 | rule | “The header binds” | The header binds nothing: the file's own module name is not a symbol, so `md0043.f()` is refused. | `refuse` |
| `md0044` | 44 | rule | “A file whose first” | A file whose first declaration is not its header is refused at that declaration, NITPICK-RESOLVE-012. | `sh:0` |
| `md0045` | 45 | rule | “or a `mod:` naming another module, is refused” | A file whose header names another module (a sibling that exists) is refused, NITPICK-RESOLVE-012. | `sh:0` |
| `md0046` | 46 | rule | “a file with no declarations at” | A file with no declarations at all is refused at its first line, NITPICK-RESOLVE-012. | `sh:0` |
| `md0055` | 55 | rule | “Declared in any other module of the program” | `main` declared in an imported module is refused, NITPICK-RESOLVE-013. | `refuse:NITPICK-RESOLVE-013` |
| `md0055b` | 55 | rule | “or inside an inline module” | `main` declared inside an inline module of the root is refused, NITPICK-RESOLVE-013. | `refuse:NITPICK-RESOLVE-013` |
| `md0056` | 56 | rule | “either is refused (`NITPICK-RESOLVE-013`)” | `failsafe` declared in an imported module is refused, NITPICK-RESOLVE-013. | `refuse:NITPICK-RESOLVE-013` |
| `md0056b` | 56 | rule | “the runtime calls both by name” | `failsafe` declared inside an inline module of the root is refused, NITPICK-RESOLVE-013. | `refuse:NITPICK-RESOLVE-013` |
| `md0060` | 60 | rule | “Modules can be arbitrarily nested” | Modules nest: `mod:core = { mod:math = { … }; };` compiles, and `math` is reached inside `core`. | `run:0` |
| `md0061` | 61 | rule | “Modules are private by default” | A nested module without `pub` is private: `core.math.sq(3i32)` from outside `core` is refused. | `refuse` |
| `md0061b` | 61 | rule | “Use `pub mod` to expose them to outer scopes” | `pub mod` exposes a nested module: `core.math.sq(3i32)` from outside is 9. | `run:0` |
| `md0063` | 63 | rule | “An inline module's members are reached QUALIFIED” | An inline module's member is not in scope bare outside it: `connect()` without a qualifier or an import is refused. | `refuse` |
| `md0064` | 64 | rule | “the contract, purity, async” | A qualified call checks the member's `requires` as any named call does: a violated precondition traps RequiresViolated. | `trap:RequiresViolated` |
| `md0065` | 65 | rule | “and argument rules of any named call” | A qualified call checks its arguments as any named call does: an `int64` passed for an `int32` parameter is refused. | `refuse` |
| `md0065b` | 65 | rule | “`network.MAX` reads its binding” | `network.MAX` reads an inline module's `pub` binding (11). | `run:0` |
| `md0066` | 66 | rule | “`network.E` names its error constant” | `m.Boom` names the inline module's error constant: `?! m.Boom` raises it, and failsafe's `(md0066.Boom)` arm sees it (signalled with 42, S45). | `run:42` |
| `md0067` | 67 | rule | “(`core.math.sq(3i32)`)” | A member is reached qualified through any depth of nesting: `a.b.c.f()`, three modules down. | `run:0` |
| `md0067b` | 67 | rule | “and IMPORTED with `use network.*;`” | `use network.*;` over an inline module binds its `pub` members bare. | `run:0` |
| `md0068` | 68 | rule | “network.{connect, Point};`” | `use network.{connect, Point};` binds the function and the TYPE: `Point` is named bare outside the module. | `run:0` |
| `md0068b` | 68 | rule | “`use network.connect;`” | `use network.connect;` binds the one member bare. | `run:0` |
| `md0068c` | 68 | rule | “`use core.math as” | `use core.math as cm;` aliases a nested inline module: `cm.sq(3i32)` is 9. | `run:0` |
| `md0069` | 69 | rule | “which is the only way an inline module's TYPES are named from” | An inline module's type is named from outside only by importing it: `network.Point:p` (qualified type) is refused. | `refuse` |
| `md0070` | 70 | rule | “An alias (`use "./m.npk" as m;`)” | An alias carries its file's scope: after `use "./m.npk" as m;`, `m.f()` works across files. | `run:0` |
| `md0071` | 71 | rule | “import carry their module's scope the same way” | A `pub mod:helpers = { … };` bound by a file import carries its scope: `helpers.f()` works in the importer. | `run:0` |
| `md0072` | 72 | rule | “A module in value position is refused” | A module in value position is refused with "`m` is a module, not a value". | `sh:0` |
| `md0073` | 73 | rule | “as is a type reached through one” | A type reached through a module, in value position, is refused (`int32:v = network.Point;`). | `refuse` |
| `md0074` | 74 | rule | “member the module lacks is "module `m` has no member `x`"” | A member the module lacks is refused with "module `m` has no member `x`". | `sh:0` |
| `md0077` | 77 | rule | “the basename of the declaring file, however deep the” | An error constant two inline modules deep is the FILE's identity: failsafe's `(md0077.Boom)` arm catches `a.b.Boom` (signalled with 42, S45). | `run:42` |
| `md0079` | 79 | rule | “`use m.{Name};` then `(Name)` is the bare spelling” | After `use m.{Boom};`, the bare arm `(Boom)` catches the inline module's constant (signalled with 42, S45). | `run:42` |
| `md0080` | 80 | rule | “SELECTOR IS CHECKED, in `failsafe` and in any other `pick`” | An arm over an `Error` in an ordinary `pick` is checked: `(nosuch.Boom)`, which no loaded file's constant hashes to, is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0080b` | 80 | rule | “`Error` SELECTOR IS CHECKED” | In an ordinary `pick` over an `Error`, the file-qualified arm `(md0080b.Boom)` catches the inline module's constant. | `run:0` |
| `md0083` | 83 | rule | “`(m.Name)` with an inline module `m`” | A failsafe arm `(m.Boom)` qualified by the inline module, not the file, is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0083b` | 83 | rule | “`(file.Nosuch)`” | A failsafe arm `(file.Nosuch)` naming no constant of the file is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0083c` | 83 | rule | “`(nosuch.Name)`” | A failsafe arm `(nosuch.Boom)` naming no loaded file is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0084` | 84 | rule | “`(x.DivByZero)` (a system constant's code is explicit, never a hash)” | A failsafe arm `(x.DivByZero)` (a system constant under a qualifier) is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0087` | 87 | rule | “literal, a global, a range” | A literal arm over an `Error` selector is refused, NITPICK-TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `md0087b` | 87 | rule | “a global” | An arm naming a global (not an error constant) over an `Error` selector is refused, NITPICK-TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `md0087c` | 87 | rule | “a range” | A range arm over an `Error` selector is refused, NITPICK-TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `md0088` | 88 | rule | “three-plus segments” | A three-segment arm `(a.b.Boom)` over an `Error` selector is refused, NITPICK-TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `md0099` | 99 | rule | “**Wildcard** (All `pub` symbols)” | `use "./sqlib.npk".*;` binds every `pub` symbol of the file bare. | `run:0` |
| `md0099b` | 99 | rule | “`use "path/module.npk".*;`” | The wildcard binds only `pub` symbols: the file's private `hidden()` is not bound by it. | `refuse` |
| `md0100` | 100 | rule | “`use "path/module.npk".square;`” | `use "./sqlib.npk".square;` binds the one name. | `run:0` |
| `md0101` | 101 | rule | “`use "path/module.npk".{square, pi};`” | `use "./sqlib.npk".{square, pi};` binds the two names. | `run:0` |
| `md0102` | 102 | rule | “`use "path/module.npk" as math;`” | `use "./sqlib.npk" as math;` binds the namespace: `math.square(3i32)` and `math.pi`. | `run:0` |
| `md0105` | 105 | example | “```nitpick” | The block's six logical-path imports compile together (with `nested`, `core.math` and a file import binding `helpers` declared), and each bound name works. | `run:0` |
| `md0115` | 115 | rule | “`std` is the standard library's, resolved by the driver” | A logical path whose first segment is `std` is resolved by the driver against the standard library. | untestable [vague] the reference names no standard-library member whose signature a program could call, so what `use std.…` binds is not observable; md0105 and md0148 check that the forms compile |
| `md0116` | 116 | rule | “other first segment must name a MODULE SYMBOL” | A logical path may start at a `use "…" as name;` alias: `use lib.{f};` after the alias binds `f`. | `run:0` |
| `md0119` | 119 | rule | “last module's public names are then bound through the same binders” | Every form of the file imports works through a logical path: `use core.math.sq;` (one name) binds `sq`. | `run:0` |
| `md0120` | 120 | rule | “forms use, in every form the file forms have” | Every form of the file imports works through a logical path: `use core.math.*;` binds `sq`. | `run:0` |
| `md0121` | 121 | rule | “symbol in scope is refused by name (`NITPICK-RESOLVE-002`” | A logical path whose first segment names no module symbol in scope is refused, NITPICK-RESOLVE-002. | `refuse:NITPICK-RESOLVE-002` |
| `md0122` | 122 | rule | “one naming a function or a binding "is not a module"” | A logical path whose first segment names a function is refused ("is not a module"). | `sh:0` |
| `md0123` | 123 | rule | “the module lacks is `NITPICK-RESOLVE-007`” | A later segment the module lacks is refused, NITPICK-RESOLVE-007. | `refuse:NITPICK-RESOLVE-007` |
| `md0124` | 124 | rule | “`NITPICK-RESOLVE-003`, exactly as for a named file import” | A later segment naming a private nested module is refused, NITPICK-RESOLVE-003. | `refuse:NITPICK-RESOLVE-003` |
| `md0125` | 125 | rule | “so `use lib.*;` may stand” | Order never matters: `use lib.*;` written ABOVE the `use "./lib.npk" as lib;` that binds `lib` works. | `run:0` |
| `md0127` | 127 | rule | “no program declares as a module (`NITPICK-RESOLVE-001`” | No program declares a module named `std`: `mod:std = { … };` is refused, NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `md0129` | 129 | rule | “same code refuses a module-level FUNCTION” | A module-level function named after a bare-name builtin (`mono_now`) is refused, NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `md0129b` | 129 | rule | “or an `extern` method, whose stub” | An `extern` method named after a bare-name builtin is refused, NITPICK-RESOLVE-001. | `sh:0` |
| `md0133` | 133 | rule | “Methods are exempt” | A method named after a bare-name builtin is accepted: `b.mono_now()` is the method. | `run:0` |
| `md0134` | 134 | rule | “refuses a CALLABLE binding of that name” | Inside a function, a parameter of function type named after a builtin is refused, NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `md0134b` | 134 | rule | “a parameter, a local” | Inside a function, a local of function type named after a builtin is refused, NITPICK-RESOLVE-001. | `refuse:NITPICK-RESOLVE-001` |
| `md0134c` | 134 | rule | “CALLABLE binding” | Only a CALLABLE binding is refused: a plain `int64` local named after a builtin is accepted. | `run:0` |
| `md0139` | 139 | rule | “strictly **not transitive**” | A plain `use` is not re-exported: a name `mid.npk` imports plain is not bound by `use "./mid.npk".*;`. | `refuse` |
| `md0139b` | 139 | rule | “use `pub use` to expose them” | A `pub use` re-exports: a name `mid.npk` imports with `pub use` is bound by `use "./mid.npk".*;`. | `run:0` |
| `md0139c` | 139 | rule | “re-exports it all the same” | A `pub use` of a path the module already imported plain (plain first) still re-exports it. | `run:0` |
| `md0139d` | 139 | rule | “the two lines mean the same in either order” | The `pub use` re-exports in either order: `pub use` first, then the plain `use`. | `run:0` |
| `md0146` | 146 | row | “\| `use "./util.npk"`, `use "../x/y.npk"` \| the **importing file's** directory \|” | A `../` path resolves against the IMPORTING file's directory: `sub/a.npk`'s `use "../x/y.npk"` loads `x/y.npk` beside the root. | `sh:0` |
| `md0147` | 147 | row | “\| `use "nfs/path.npk"` \| the **dependency roots** \|” | A path not starting with `.` resolves against the dependency roots only: with no dependency, `use "nfs/path.npk"` is refused even with `nfs/path.npk` beside the importing file. | `sh:0` |
| `md0148` | 148 | row | “\| `use std.math.*` \| the standard library \|” | `use std.math.*;` is a path the standard library resolves: the program compiles. | `compile` |
| `md0150` | 150 | rule | “A dependency named `nfs` declared at `../nfs` roots at” | A dependency named `nfs` declared at `../nfs` roots at `../nfs/src/`. | untestable [tool] needs a package whose manifest declares a dependency (BUILD_REFERENCE §3); BUILD's claims test the manifest |
| `md0153` | 153 | rule | “An ambiguous path is an error, not a first match.” | Two dependencies supplying the same path fail the build, naming both. | untestable [tool] needs a package whose manifest declares two dependencies (BUILD_REFERENCE §3) |
| `md0160` | 160 | rule | “**A `use` cycle among modules is legal** (D-086)” | Two modules may import each other: `a.npk` and `b.npk`, each using the other's names, compile and run. | `run:0` |
| `md0161` | 161 | rule | “and so may any longer ring” | A longer ring of imports is legal: a → b → c → a. | `run:0` |
| `md0166` | 166 | rule | “Nitpick has no module-level execution” | There is no module-level execution: a statement at module level is refused. | `refuse` |
| `md0178` | 178 | rule | “**Collect every declaration in every module in the graph before resolving any” | Every declaration of every module is collected before any body resolves: a struct of `a.npk` used in `b.npk`'s body, across an import cycle, resolves. | `run:0` |
| `md0179` | 179 | rule | “lets a function refer to one” | A function may refer to one declared below it in the same file. | `run:0` |
| `md0182` | 182 | rule | “depends on itself other than through a pointer” | A struct whose size depends on itself across two modules (by value) is refused. | `refuse` |
| `md0182b` | 182 | rule | “other than through a pointer” | A struct cycle through a pointer is legal: `SA = { SB->:b; }` and `SB = { SA:a; }` compile. | `run:0` |
| `md0182c` | 182 | rule | “or a `const` whose initialiser” | A module constant whose initialiser depends on itself (through another) is refused. | `refuse` |
| `md0183` | 183 | rule | “The diagnostic names the members in the order they refer to” | The cycle's diagnostic names its members (`FIRST`, `SECOND`) on its first line, not "circular import". | `sh:0` |
| `md0185` | 185 | rule | “The same module graph must produce” | The same module graph compiles to the same program whichever import the loader enters first: swapping the root's two import lines leaves the emitted IR identical. | `sh:0` |
| `md0199` | 199 | rule | “strict binary visibility model” | Visibility has two levels only, public and private. | untestable [vague] no third level's spelling is named whose refusal a program could check |
| `md0201` | 201 | rule | “Symbols are accessible only within the same module/file” | A private symbol of another file is not importable: `use "./lib.npk".private_here;` is refused. | `refuse` |
| `md0201b` | 201 | rule | “Intra-module access to private symbols is always permitted” | A module's own `pub` function may call its private one: the importer sees the result. | `run:0` |
| `md0203` | 203 | rule | “qualified path from outside its module (`nested.internal()`” | `nested.internal()`, a private member called qualified from outside, is refused, NITPICK-RESOLVE-003. | `refuse:NITPICK-RESOLVE-003` |
| `md0204` | 204 | rule | “`nested.SECRET`” | `nested.SECRET`, a private binding read qualified from outside, is refused, NITPICK-RESOLVE-003. | `refuse:NITPICK-RESOLVE-003` |
| `md0204b` | 204 | rule | “a hop through a private nested module” | `nested.deep.g()`, a `pub` member reached through a private nested module, is refused, NITPICK-RESOLVE-003. | `refuse:NITPICK-RESOLVE-003` |
| `md0205` | 205 | rule | “`use nested.internal;`), is `NITPICK-RESOLVE-003`” | `use nested.internal;`, naming a private member by a `use`, is refused, NITPICK-RESOLVE-003. | `refuse:NITPICK-RESOLVE-003` |
| `md0206` | 206 | rule | “"`internal` is private to `nested`"” | The refusal says "`internal` is private to `nested`". | `sh:0` |
| `md0209` | 209 | example | “```nitpick” | The four `pub` declarations (a function, a struct, a `pub const`, a `pub mod`) compile in a file, and an importer uses each. | `run:0` |
| `md0212` | 212 | rule | “pub const int32:MAX = 100i32;” | `pub const int32:MAX = 100i32;` declares a public module constant: `MAX` is 100. | `run:0` |
| `md0219` | 219 | rule | “Legacy C-style/Rust-style `func name() -> type` is banned” | The legacy `func add(...) -> int32 { … }` syntax is refused. | `refuse` |
| `md0221` | 221 | example | “```nitpick” | `func:add = int32(int32:a, int32:b) { pass (a + b); };` compiles, and `add(2, 3)` is 5. | `run:0` |
| `md0226` | 226 | rule | “The compiler automatically wraps this in a `Result<int32>`” | The declared type is the success type, wrapped in `Result<int32>`: the call binds as a `Result<int32>` whose value is 5. | `run:0` |
| `md0226b` | 226 | rule | “is the *success* type” | The call is a `Result<int32>`, not an `int32`: binding it to a plain `int32` is refused. | `refuse` |
| `md0230` | 230 | rule | “**In-process FFI does not exist in Nitpick (D-149).**” | There is no in-process FFI; an `extern` block declares a driver process's interface. | untestable [vague] a statement of the design; its observable parts are md0241-md0274's |
| `md0235` | 235 | rule | “line — past it, a segfault, a hang, or a scribbled heap in the foreign code” | A fault in the driver arrives in the Nitpick process as a value, never as an uninterceptable fault. | untestable [tool] needs a running driver process to fault |
| `md0241` | 241 | example | “```nitpick” | The `cuda_driver` block (an opaque struct and two methods) is valid syntax: the program compiles. | `compile` |
| `md0249` | 249 | rule | “The string names the driver; the functions are its methods.” | The block's string names the driver and its functions are the driver's methods. | untestable [vague] a statement of what the parts mean; md0250 checks the stub the methods become |
| `md0250` | 250 | rule | “lowers each method to a **Bridge stub**” | Each method of an `extern` block lowers to a stub: the emitted IR defines a function for the method `probe`. | `sh:0` |
| `md0252` | 252 | rule | “An `opaque struct` declared here is a” | An opaque struct declared in a block is a typed wire handle, minted by the driver, dead after a restart. | untestable [tool] needs a running driver to mint a handle and restart |
| `md0259` | 259 | rule | “All driver methods return `Result<T>` like every other function” | A driver method's call is a `Result<T>`: binding `await probe(…)` to `Result<int64>` compiles. | `sh:0` |
| `md0260` | 260 | rule | “**no per-method error contracts**” | Timeouts, driver death and protocol violations arrive as uniform negative codes in the D-141 space. | untestable [tool] needs a running driver to time out, die or violate the protocol |
| `md0265` | 265 | rule | “written anymore. The grammar remains parsed and is refused by the checker” | A failure contract (`never fails`) on a driver method is parsed and refused by the checker, which names D-149. | `sh:0` |
| `md0270` | 270 | rule | “Fixed-width scalars, POD structs of them, sized byte payloads, and typed” | A POD struct of fixed-width scalars is in the wire vocabulary: a method taking one compiles. | `sh:0` |
| `md0270b` | 270 | rule | “Fixed-width scalars” | Every fixed-width scalar is in the wire vocabulary: a method taking an `int16` compiles. | `sh:0` |
| `md0270c` | 270 | rule | “sized byte payloads” | A sized byte payload is in the wire vocabulary: a method taking an `int8[]` compiles. | `sh:0` |
| `md0270d` | 270 | rule | “and typed” | A typed handle is in the wire vocabulary: a method taking the block's `opaque struct` compiles. | `sh:0` |
| `md0271` | 271 | rule | “Payloads are **copied out of shared memory before validation**” | Payloads are copied out of shared memory before validation. | untestable [tool] the copy happens on a live ring; needs a running driver |
| `md0273` | 273 | rule | “Nothing address-shaped crosses in either direction: no pointers” | No pointer crosses the wire: a method taking an `int32->` (besides its `Bridge->`) is refused. | `sh:0` |
| `md0274` | 274 | rule | “(which is now valid nowhere in the language)” | `void*` is valid nowhere: a parameter of type `void->` is refused. | `refuse` |
| `md0279` | 279 | rule | “an **interface hash derived from the `extern` block's signatures**” | The handshake carries an interface hash from the block's signatures; a stale driver is refused before any call. | untestable [tool] needs a driver built against another interface |
| `md0281` | 281 | rule | “the generated stub implements the `Driver` trait with D-055's” | The stub implements the Driver trait with D-055's obligations (deadline, no partial results, supervised child, failsafe-reachable registry). | untestable [tool] the obligations are kept at run time against a running driver |
| `md0284` | 284 | rule | “**C SDK header**” | The driver side is built against the C SDK header. | untestable [tree] the SDK is a file of the compiler's tree, not something a program does |
| `md0289` | 289 | example | “```nitpick” | A driver method's call is read with `raw` or with `_!`; both forms compile and give the value. | `run:0` |
| `md0296` | 296 | rule | “a `string` is `{ptr, len, cap}` and is **not** NUL-terminated” | A `string` is `{ptr, len, cap}` and is not NUL-terminated. | untestable [internal] a string's machine layout is not observable from a program without `wild` |
| `md0296b` | 296 | rule | “a string literal converts at compile time” | A string literal converts to a `cstring` at compile time: `cstring:c = "abc";` compiles. | `compile` |
| `md0296c` | 296 | rule | “`to_cstring(s)` converts a runtime `string`” | `to_cstring(s)` converts a runtime string without an interior NUL: the result is not an error. | `run:0` |
| `md0298` | 298 | rule | “`int32->`: Scalar pointer” | `int32->` is a pointer to an int32: a write through it reaches the int32. | `run:0` |
| `md0299` | 299 | rule | “`MyStruct->`: Struct pointer” | `MyStruct->` is a pointer to a struct: a read through it sees the struct's field. | `run:0` |
| `md0300` | 300 | rule | “`any->`: Erased/Opaque pointer” | `any->` is the erased pointer type: a parameter of type `any->` compiles. | `compile` |

## OP (`meta/specs/OP_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `op0005` | 5 | rule | “Operator overloading is strictly forbidden” | Operator overloading is forbidden: an impl of an operator for a user struct is refused. | `refuse` |
| `op0015` | 15 | row | “\| 1 \| Postfix \|” | Postfix binds tightest: `-a[1]` is -(a[1]), and `~a[0]` is ~(a[0]). | `run:0` |
| `op0016` | 16 | row | “\| **2** \| **Result unary** *(right-assoc)* \|” | The Result unary operators are looser than postfix and tighter than cast: `raw f(x) => int64` casts the unwrapped value. | `run:0` |
| `op0017` | 17 | row | “\| 3 \| Pipeline \|” | The pipeline operators sit at level 3: `x \|> f()` passes x as f's first argument. | `run:0` |
| `op0018` | 18 | row | “\| 4 \| Cast \| `=>` `=>!` \|” | Cast binds tighter than unary negation. | `run:0` (M10 `x01_cast_binds_tighter_than_negation`) |
| `op0019` | 19 | row | “\| 5 \| Unary \|” | Unary binds tighter than multiplicative: `~a * b` is (~a) * b. | `run:0` |
| `op0020` | 20 | row | “\| 6 \| Multiplicative \|” | Multiplicative binds tighter than additive: 2 + 3 * 4 is 14. | `run:0` |
| `op0021` | 21 | row | “\| 7 \| Additive \|” | Additive binds tighter than shift. | `run:0` (M10 `x02_additive_before_shift`) |
| `op0022` | 22 | row | “\| 8 \| Shift \|” | Shift binds tighter than relational: `1 << 2 < 5` is (1 << 2) < 5. | `run:0` |
| `op0023` | 23 | row | “\| 9 \| Range / Spread \|” | Range binds looser than additive: `0...1 + 2` is 0...3, three iterations. | `run:0` |
| `op0024` | 24 | row | “\| 10 \| Relational \|” | Relational binds tighter than equality: `a < b == c < d` is (a < b) == (c < d). | `run:0` |
| `op0025` | 25 | row | “\| 11 \| Equality \|” | Equality binds tighter than bitwise AND. | `refuse` (M10 `x03_equality_before_bitand`) |
| `op0026` | 26 | row | “\| 12 \| Bitwise AND \|” | AND binds tighter than XOR: 1 ^ 3 & 2 is 1 ^ (3 & 2) = 3. | `run:0` |
| `op0027` | 27 | row | “\| 13 \| Bitwise XOR \|” | XOR binds tighter than OR: 1 \| 3 ^ 3 is 1 \| (3 ^ 3) = 1. | `run:0` |
| `op0028` | 28 | row | “\| 14 \| Bitwise OR \|” | Bitwise OR binds tighter than logical AND: `false && true \| true` is false && (true \| true). | `run:0` |
| `op0029` | 29 | row | “\| 15 \| Logical AND \| `&&` (short-circuiting) \|” | AND binds tighter than OR: `true \|\| false && false` is true \|\| (false && false). | `run:0` |
| `op0030` | 30 | row | “\| 16 \| Logical OR \| `\\|\\|` (short-circuiting) \|” | `\|\|` short-circuits: its right side is not evaluated when the left is true. | `run:0` |
| `op0031` | 31 | row | “\| 17 \| Null Coalescing \| `??` \|” | `??` unwraps an Optional: a NIL Optional coalesces to the right side. | `run:0` |
| `op0032` | 32 | row | “\| 18 \| Ternary / Fallback \|” | `is` is the ternary: `is x > 0 : 1 : -1` picks by the condition. | `run:0` |
| `op0033` | 33 | row | “\| 19 \| Assignment \|” | The assignment operators `= += -= *= /= %= &= \|= ^= <<= >>=` all assign in place. | `run:0` |
| `op0037` | 37 | rule | “`raw a.eq(b)` takes the receiver or the call” | Level 2 is looser than postfix: `raw a.eq(b)` unwraps the call, not the receiver. | `run:0` |
| `op0041` | 41 | rule | “`discard` / `_~` is absent because D-060 makes it a statement” | discard is a statement, not an expression: using it as a value is refused. | `refuse` |
| `op0046` | 46 | rule | “**`->` removed from level 1.**” | `->` is not member access: `p->x` is refused. | `refuse` |
| `op0049` | 49 | rule | “**`=>!` added to the Cast level**” | `=>!` shares the cast level, tighter than negation: `-x =>! int8` with x = 128 is -(x =>! int8), the negation of int8 -128, which traps IntOverflow. | `trap:IntOverflow` |
| `op0051` | 51 | rule | “**`#` removed from the Unary level**” | `#` is not a unary operator: `#x` (the old pin) is refused. | `refuse` |
| `op0056` | 56 | rule | “**Assignment is a statement, not an expression** (D-060)” | Assignment is a statement: `int32:y = (x = 5i32) + 2i32;` does not parse. | `refuse` |
| `op0064` | 64 | rule | “`if (x = 3)` needs no dedicated rule rejecting” | `if (x = 3)` is not expressible: it is refused. | `refuse` |
| `op0066` | 66 | rule | “Conditions must still be a strict `bool`” | Conditions are strictly bool: `if (x)` on an int32 is refused. | `refuse` |
| `op0067` | 67 | rule | “**`&&` and `\|\|` short-circuit**” | `&&` and `\|\|` short-circuit. | `run:0` (M10 `x04_short_circuit`) |
| `op0067b` | 67 | rule | “require strictly boolean operands” | `&&` requires boolean operands: `1i32 && 2i32` is refused. | `refuse` |
| `op0068` | 68 | rule | “(spaceship) yields `int32`” | `<=>` yields an int32: -1, 0 or 1. | `run:0` (M10 `m06_spaceship`) |
| `op0070` | 70 | rule | “`expr ?\| fallback` yields `expr`'s value” | `expr ?\| fallback` yields the value, or the fallback if it errored. | `run:0` (M10 `r01_fallback`) |
| `op0073` | 73 | rule | “A bare `?`” | A bare `?` is refused by name, NITPICK-PARSE-011. | `refuse:PARSE-011` |
| `op0074b` | 74 | rule | “and the word `defaults` are refused by name” | The word `defaults` is refused by name, NITPICK-PARSE-011. | `refuse:PARSE-011` |
| `op0075` | 75 | rule | “The parser still reads the old form and refuses it by name” | `++` is struck: the parser refuses `x++` by name, NITPICK-PARSE-010. | `refuse:PARSE-010` |
| `op0075b` | 75 | rule | “`x += 1` / `x -= 1` are the spellings” | `x += 1` and `x -= 1` are the increment's spellings. | `run:0` |
| `op0083` | 83 | row | “\| `+` \| Add \| Safe addition. \|” | `+` is safe: a plain-integer overflow traps IntOverflow. | `run:93` (M10 `o01_int32_add`) |
| `op0084` | 84 | row | “\| `-` \| Subtract \| Safe subtraction. \|” | `-` is safe: an overflow traps IntOverflow. | `run:93` (M10 `o02_int32_sub`) |
| `op0085` | 85 | row | “\| `*` \| Multiply \| Safe multiplication. \|” | `*` is safe: an overflow traps IntOverflow. | `run:93` (M10 `o03_int32_mul`) |
| `op0086` | 86 | row | “\| `/` \| Divide \| Safe division.” | Integer `/` by zero traps DivByZero (the plain-integer row of the type-directed rule). | `run:97` (M10 `v03_div_by_zero`) |
| `op0087` | 87 | row | “\| `%` \| Modulo \| Remainder operation. Same divide-by-zero rule as `/`. \|” | `%` by zero follows `/`'s rule: it traps DivByZero. | `run:97` (M10 `v04_rem_by_zero`) |
| `op0088` | 88 | row | “\| `**` \| Power \| Exponentiation (Standard Library expansion). \|” | `**` is exponentiation: 2 ** 8 is 256. | `run:0` |
| `op0089` | 89 | row | “\| `+%` \| Add, wrapping \|” | `+%` adds modulo 2^N: the u64 maximum +% 1 is 0, with no trap. | `run:0` |
| `op0090` | 90 | row | “\| `-%` \| Subtract, wrapping \| Subtraction modulo 2^N. \|” | `-%` subtracts modulo 2^N: 0 -% 1 at uint8 is 255. | `run:0` |
| `op0091` | 91 | row | “\| `*%` \| Multiply, wrapping \|” | `*%` multiplies modulo 2^N: 0x80000000 *% 2 at uint32 is 0. | `run:0` |
| `op0102` | 102 | rule | “The kinds that own their own arithmetic refuse it by name” | The kinds that own their arithmetic refuse the wrapping family by name: `+%` on a tbb8 is TYPE-078. | `refuse:TYPE-078` |
| `op0106` | 106 | rule | “A constant wrap folds” | A constant wrap folds WITH the wrap. | `run:0` (M10 `o20_wrapping_folds_with_wrap`) |
| `op0121` | 121 | row | “\| `tbb8`…`tbb256` \| yields **ERR**” | On tbb, overflow yields ERR and divide by zero yields ERR, neither a trap. | `run:0` |
| `op0122` | 122 | row | “\| `int32`, `uint64`, … \| **wraps** — defined, no check, no trap \|” | Plain integers: the row says they wrap, and the note at line 138 supersedes it: `+ - *` trap IntOverflow since D-210. | `trap:IntOverflow` |
| `op0122b` | 122 | row | “**traps to `failsafe`**” | Plain-integer divide by zero traps to failsafe. | `run:97` (M10 `v03_div_by_zero`) |
| `op0123` | 123 | row | “\| `flt32`…`flt512` \| **IEEE 754** — `inf` / `nan`, no trap \|” | Floats overflow to infinity, with no trap. | `run:0` |
| `op0123b` | 123 | row | “**IEEE 754** — `inf` / `nan` \| numeric work \|” | Float division by zero is IEEE: an infinity, with no trap. | `run:0` (M10 `v16_float_div_by_zero`) |
| `op0144` | 144 | rule | “A `simd` integer lane traps as its” | A simd integer lane traps as its scalar does. | `run:93` (M10 `o22_simd_lane_overflow`) |
| `op0150` | 150 | rule | “An integer `+ - *` or negation whose operands the compiler folds” | A folded constant is computed exactly at its type: a fixed product is its exact value. | `run:0` |
| `op0153` | 153 | rule | “**A value that does not fit is `NITPICK-TYPE-076`**” | A constant that does not fit is NITPICK-TYPE-076 where it is written. | `refuse:NITPICK-TYPE-076` (M10 `o21_constant_overflow_refused`) |
| `op0155` | 155 | rule | “`int8:x = 100 + 100;` is refused too” | An unsuffixed constant pair takes its width from the context: `int8:x = 100 + 100;` is refused. | `refuse:NITPICK-TYPE-076` (M10 `c26_constant_overflow_contextual`) |
| `op0156` | 156 | rule | “**A value that fits is emitted as the constant**, with no guard” | A constant that fits is emitted as the constant: `-1i32` is no checked `sub` (no overflow intrinsic in the function that returns it). | `ir:(?s)^define [^@\n]*@"[^"]*\.negone"\((?!(?:(?!\n\}).)*?with\.overflow)` |
| `op0158` | 158 | rule | “A width past 64 bits folds inside the 64-bit window only” | A width past 64 bits folds inside the 64-bit window only; beyond it the run-time guard stays. | untestable [internal] declining the fold changes no value (the guard computes the same product); only the emission differs, and no width past 64 bits is named to scope an IR test by |
| `op0161` | 161 | rule | “`<<` loses the bits past its width (`1i8 << 7i8` is −128)” | The folder shifts as the machine does: `1i8 << 7i8` is -128 and `~5u8` is 250. | `run:0` (M10 `s03_shifts_folded`) |
| `op0163` | 163 | rule | “a `uint64` divides, takes remainders, shifts right and orders UNSIGNED” | The folder divides and takes remainders unsigned for a uint64. | `run:0` (M10 `v15_unsigned_div_rem_folded`) |
| `op0163b` | 163 | rule | “orders UNSIGNED” | The folder orders a uint64 unsigned. | `run:0` (M10 `m04_unsigned_ordering_folded`) |
| `op0164` | 164 | rule | “a constant `MIN / −1` or `MIN % −1` is refused” | A constant MIN / -1 is refused as a constant division by zero is (TYPE-004). | `refuse:NITPICK-TYPE-004` (M10 `v13_constant_min_div_minus_one`) |
| `op0166` | 166 | rule | “`uint64` values past 2^63−1 are built with bit operations” | uint64 values past 2^63-1 are built with bit operations: `~0u64` is the maximum and `(1u64 << 63u64) \| 1u64` is 2^63 + 1. | `run:0` |
| `op0169` | 169 | rule | “ERR is **absorbing and overrides identities**” | ERR is absorbing: ERR * 0 is ERR, and ERR - ERR is ERR. | `run:0` |
| `op0171` | 171 | rule | “Only an explicit check (`is_err`) or a fallback (`?`) leaves the state” | A fallback leaves the ERR state: an ERR tbb with a fallback yields the fallback. | `run:0` |
| `op0172` | 172 | rule | “*(`ok()` was listed here and is removed — D-097.)*” | `ok()` is removed: calling it is refused. | `refuse` |
| `op0174` | 174 | rule | “**comparing or” | Comparing or branching on an ERR value traps to failsafe. | `run:110` (M10 `m12_tbb_compare_on_err_traps`) |
| `op0177` | 177 | rule | “Use `is_err(x)` to test without trapping, or a `pick` with an explicit” | A pick with an explicit ERR: arm branches on ERR without trapping. | `run:0` (M10 `p13_tbb_err_arm_taken`) |
| `op0177b` | 177 | rule | “Use `is_err(x)` to test without trapping” | `is_err(x)` tests for ERR without trapping. | `run:0` |
| `op0180` | 180 | rule | “Bitwise operators (`&`, `\|`, `^`, `~`, `<<`, `>>`) are **rejected on `tbb` types**” | Bitwise operators are rejected on tbb: `a & b` on tbb8 is refused. | `refuse` |
| `op0182` | 182 | rule | “Cast to a plain integer first — which traps if the” | Casting an ERR tbb to a plain integer traps (TbbErr). | `trap:TbbErr` |
| `op0191` | 191 | row | “\| `=` \| Assign \| Standard assignment. \|” | `=` assigns. | `run:0` |
| `op0192` | 192 | row | “\| `+=` \| Add & Assign \|” | `+=` assigns in place: 7i32 += 5i32 gives 12. | `run:0` |
| `op0193` | 193 | row | “\| `-=` \| Subtract & Assign \|” | `-=` assigns in place: 7i32 -= 5i32 gives 2. | `run:0` |
| `op0194` | 194 | row | “\| `*=` \| Multiply & Assign \|” | `*=` assigns in place: 7i32 *= 5i32 gives 35. | `run:0` |
| `op0195` | 195 | row | “\| `/=` \| Divide & Assign \|” | `/=` assigns in place: -7i32 /= 2i32 gives -3. | `run:0` |
| `op0196` | 196 | row | “\| `%=` \| Modulo & Assign \|” | `%=` assigns in place: -7i32 %= 5i32 gives -2. | `run:0` |
| `op0197` | 197 | row | “\| `+%=` \| Add wrapping & Assign \|” | `x +%= v` is `x = x +% v`: the u64 maximum +%= 1 is 0. | `run:0` |
| `op0198` | 198 | row | “\| `-%=` \| Subtract wrapping & Assign \|” | `-%=` subtracts modulo 2^N: 0 -%= 1 at uint64 is the maximum. | `run:0` |
| `op0199` | 199 | row | “\| `*%=` \| Multiply wrapping & Assign \|” | `*%=` multiplies modulo 2^N: 2^31 *%= 2 at uint32 is 0. | `run:0` |
| `op0207` | 207 | row | “\| `==` \| Equality \|” | `==` compares: 3 == 3 is true. | `run:0` |
| `op0208` | 208 | row | “\| `!=` \| Inequality \|” | `!=` compares: 3 != 4 is true. | `run:0` |
| `op0209` | 209 | row | “\| `<` \| Less Than \|” | `<` compares: -5 < 3 is true. | `run:0` |
| `op0210` | 210 | row | “\| `>` \| Greater Than \|” | `>` compares: 3 > -5 is true. | `run:0` |
| `op0211` | 211 | row | “\| `<=` \| Less Than or Equal \|” | `<=` compares: 3 <= 3 is true. | `run:0` |
| `op0212` | 212 | row | “\| `>=` \| Greater Than or Equal\|” | `>=` compares: -5 >= 3 is false. | `run:0` |
| `op0213` | 213 | row | “\| `<=>` \| Spaceship \| 3-way comparison. Returns `-1`, `0`, or `1`. \|” | `<=>` returns -1, 0 or 1. | `run:0` (M10 `m06_spaceship`) |
| `op0221` | 221 | row | “\| `!` \| Logical NOT \|” | !false is true. | `run:0` |
| `op0222` | 222 | row | “\| `&&` \| Logical AND \|” | true && false is false. | `run:0` |
| `op0223` | 223 | row | “\| `\\|\\|` \| Logical OR \|” | false \|\| true is true. | `run:0` |
| `op0224` | 224 | row | “\| `~` \| Bitwise NOT \|” | ~5i32 is -6i32. | `run:0` |
| `op0225` | 225 | row | “\| `&` \| Bitwise AND \|” | 12i32 & 10i32 is 8i32. | `run:0` |
| `op0226` | 226 | row | “\| `\\|` \| Bitwise OR \|” | 12i32 \| 3i32 is 15i32. | `run:0` |
| `op0227` | 227 | row | “\| `^` \| Bitwise XOR \|” | 12i32 ^ 10i32 is 6i32. | `run:0` |
| `op0228` | 228 | row | “\| `<<` \| Left Shift \| Shifts bits left. \| `a << 2` \|” | `<<` shifts left: `a << 2` with a = 3 is 12 (the example's unsuffixed amount). | `run:0` |
| `op0229` | 229 | row | “Shifts bits right (arithmetic/logical based on sign)” | `>>` is arithmetic on a signed operand and logical on an unsigned one: -8 >> 1 is -4, and 0xF0u8 >> 4 is 15. | `run:0` |
| `op0232` | 232 | rule | “literal, a negated” | A known shift amount outside 0 <= n < width is NITPICK-TYPE-070 at the shift. | `refuse:NITPICK-TYPE-070` (M10 `s07_shift_literal_amount_refused`) |
| `op0234` | 234 | rule | “shift, both operators and the compound spellings” | The amount check covers the compound spellings. | `run:111` (M10 `s08_compound_shift_amount`) |
| `op0235` | 235 | rule | “amount is checked at run time by one unsigned compare” | A computed amount outside the range traps ShiftRange. | `run:111` (M10 `s04_shift_amount_equals_width`) |
| `op0236` | 236 | rule | “negative amount reads as huge” | A negative computed amount reads as huge and traps ShiftRange. | `run:111` (M10 `s05_shift_amount_negative`) |
| `op0237` | 237 | rule | “every `failsafe`” | Wherever a computed shift exists, every failsafe must name ShiftRange: one that does not is refused. | `refuse` |
| `op0242` | 242 | rule | “The value of an in-range shift is unchanged” | An in-range shift is a bit operation with no overflow trap. | `run:0` (M10 `o18_shift_loses_bits_no_trap`) |
| `op0243` | 243 | rule | “A `simd` shift's amount is a” | A simd shift's amount is checked any-lane: one lane's amount equal to the width traps ShiftRange. | `trap:ShiftRange` |
| `op0253` | 253 | row | “\| `?\\|` \| Result Fallback \|” | `?\|` unwraps a Result: on an error it yields the default. | `run:0` (M10 `r01_fallback`) |
| `op0254` | 254 | row | “\| `??` \| Null Coalesce \|” | `??` unwraps an Optional: a present value comes through. | `run:0` |
| `op0255` | 255 | row | “**Takes exactly one argument**, an `Error` constant” | `?!` calls failsafe with its one argument, an Error constant. | `run:82` (M10 `r04_emphatic_unwrap_error`) |
| `op0257` | 257 | rule | “take a `Result` and nothing else” | `?\|` takes a Result and nothing else: on a tbb value it is refused. | `refuse` |
| `op0258` | 258 | rule | “\| `?.` \| Safe Navigation \|” | `?.` reaches a field through an Optional, and the result is an Optional of the field's type. | `run:0` |
| `op0259` | 259 | rule | “Refused by name. \| — \|” | A bare `?` is refused by name. | `refuse:PARSE-011` |
| `op0260` | 260 | rule | “Desugars to `drop expr`” | `_? f();` is `drop f();`, the void call of a never-fails NIL function. | `run:0` |
| `op0260b` | 260 | rule | “refused otherwise, `TYPE-042`” | `drop` of a callee that may fail is refused, TYPE-042. | `refuse:NITPICK-TYPE-042` (M10 `r05_drop_of_fallible_refused`) |
| `op0261` | 261 | rule | “Desugars to `raw expr`” | `_! f()` is `raw f()`: it unwraps a never-fails call's value. | `run:0` |
| `op0262` | 262 | rule | “**propagates the error to the caller, verbatim**” | `_^ f()` is `relay f()`: it propagates the callee's error verbatim. | `run:0` |
| `op0262b` | 262 | rule | “`defer` runs — it is a normal exit path” | relay's early return is a normal exit: its defers run. | `run:0` (M10 `w07_defer_on_relay`) |
| `op0262c` | 262 | rule | “Illegal in `main` / `failsafe`” | relay is illegal in main: it is refused. | `refuse` |
| `op0263` | 263 | rule | “As a statement it desugars to `discard(expr)`” | `_~ x;` is the statement `discard(x)`. | `run:0` |
| `op0263b` | 263 | rule | “reading it anyway is an error, not a warning” | A parameter marked `_~` that the body reads is an error. | `refuse` |
| `op0264` | 264 | rule | “Immediately invokes `failsafe(err)`” | `!!! E1;` invokes failsafe with E1 through the trap route. | `run:81` |
| `op0268` | 268 | rule | “Neither takes a pointer.**” | `??` takes an Optional, never a pointer: `p ?? 0i32` on an int32-> is refused. | `refuse` |
| `op0280` | 280 | rule | “`p == NULL` asks whether a pointer points anywhere” | `p == NULL` asks whether a pointer points anywhere: an address of a local is not NULL. | `run:0` |
| `op0287` | 287 | row | “\| **leading** \| negation \| `!x`, `!=` \|” | A leading `!` negates: `!x` and `!=`. | `run:0` |
| `op0288` | 288 | row | “\| **trailing or repeated** \| unchecked / emphatic \|” | A trailing or repeated `!` is unchecked or emphatic: `?!`, `=>!`, `_!` and `!!!` all compile. | `run:0` |
| `op0295` | 295 | rule | “**`!!` no longer exists**” | `!!` no longer exists: it is refused. | `refuse` |
| `op0303` | 303 | rule | “C-style `*` pointer” | C-style `*` pointer syntax is valid nowhere: `int32*:p` is refused. | `refuse` |
| `op0310` | 310 | row | “\| `@` \| Address-Of \|” | `@` takes an l-value's address: `int32->:ptr = @val;`. | `run:0` |
| `op0311` | 311 | row | “\| `$$i` \| Shared claim \|” | `$$i` is the address of a place under a shared claim: `int32->:p = $$i x;` reads it. | `run:0` |
| `op0312` | 312 | row | “\| `$$m` \| Exclusive claim \|” | `$$m` is the address of a place under an exclusive claim: `int32->:p = $$m arr[i];` writes it. | `run:0` |
| `op0313` | 313 | row | “\| `<-` \| Dereference \|” | `<-` extracts the value from a pointer. | `run:0` |
| `op0314` | 314 | row | “\| `->` \| Pointer To \| In types: pointer declaration ONLY. \|” | `->` declares a pointer type. | `run:0` |
| `op0315` | 315 | row | “\| `.` \| Member Access \|” | `.` handles all member access, dereferencing a pointer, and UFCS: `x.twice()` calls twice(x). | `run:0` |
| `op0320` | 320 | rule | “anywhere else is” | A claim stands only as a whole call argument or a pointer local's whole value; anywhere else is NITPICK-BORROW-014. | `refuse:BORROW-014` |
| `op0336` | 336 | rule | “**compiler-directive sigil**” | `#` is the compiler-directive sigil: `#name<T>(...)` calls a builtin. | `run:0` |
| `op0339` | 339 | rule | “**Direction is semantic.**” | `->` points to, `<-` brings back, `=>` goes from one type to another. | untestable [vague] a mnemonic for the operators claimed at op0313, op0314 and op0351 |
| `op0351` | 351 | row | “\| `=>` \| Safe Cast \|” | `=>` is a compile-time error where data loss is possible. | `refuse` (M10 `c03_narrow_signed_refused`) |
| `op0352` | 352 | row | “\| `=>!` \| Unchecked Cast \|” | `=>!` is a direct bit-cast or truncation without checking. | `run:0` (M10 `c13_unchecked_cast_truncates_bits`) |
| `op0356` | 356 | rule | “Every `tbb` cast checks for the sentinel and” | Every tbb cast maps ERR to the target's ERR: a tbb8 ERR widened to tbb32 is ERR, not -128. | `run:0` |
| `op0358` | 358 | rule | “plain-integer→`tbb` traps on a source value that would forge one” | A plain integer that would forge the sentinel traps on its way into tbb (TbbErr). | `trap:TbbErr` |
| `op0358b` | 358 | rule | “`=>!`” | `=>!` preserves the ERR state, not the bit pattern: a tbb8 ERR =>! tbb32 is ERR. | `run:0` |
| `op0362` | 362 | rule | “**Integer→pointer casting is illegal.**” | Integer to pointer casting is illegal outside `#wild_ptr`: `x => int32->` is refused. | `refuse` |
| `op0364` | 364 | rule | “\| `:` \| Type Annotation \|” | `:` annotates a declaration's type. | `run:0` |
| `op0365` | 365 | rule | “the only form there (D-064). Bare `<T>` is type-position only” | Bare `<T>` is type-position only: `list_init<int64>(4i64)` in an expression is refused (the turbofish is the form). | `refuse` |
| `op0365b` | 365 | rule | “\| `::<T>` \| Turbofish \|” | `::<T>` gives explicit type arguments in expression position. | `run:0` |
| `op0366` | 366 | rule | “\| `<T>?` \| Optional Type \|” | `T?` declares an Optional: an `int64?` holds a value or NIL. | `run:0` |
| `op0374` | 374 | row | “\| `is` \| Ternary Conditional \|” | `is cond : then : else` branches: `is x > 0 : 1 : -1` with x = 5 is 1. | `run:0` |
| `op0375` | 375 | row | “\| `..` \| Inclusive Range \|” | `..` is the inclusive range [a, b]. | `run:0` (M10 `l01_for_inclusive`) |
| `op0376` | 376 | row | “\| `...` \| Exclusive Range \|” | `...` is the exclusive range [a, b). | `run:0` (M10 `l02_for_exclusive`) |
| `op0377` | 377 | row | “\| `\\|>` \| Pipe Forward \|” | `val \|> func()` passes val as func's first argument: 10 \|> minus(3) is 7. | `run:0` |
| `op0378` | 378 | row | “\| `<\\|` \| Pipe Backward \|” | `func() <\| val` evaluates val and passes it to func. | `run:0` |
| `op0379` | 379 | row | “\| `$` \| Iteration Variable\|” | `$` is the loop counter bound inside `loop` and `till`: summing $ over loop(0, 3, 1) gives 3. | `run:0` |
| `op0387` | 387 | row | “\| `""` \| String Literal \|” | A string literal is UTF-8: "é" is two bytes. | `run:0` |
| `op0388` | 388 | row | “\| `r""` \| Raw String Literal\|” | A raw string has no escape processing: r"C:\Path" is 7 bytes, the third a backslash. | `run:0` |
| `op0389` | 389 | row | “\| `""" """`\| Triple Quote \|” | A triple-quoted literal spans lines and keeps the newline. | `run:0` |
| `op0390` | 390 | row | “\| `''` \| Char Literal \|” | `'A'` is a char literal of 65. | `run:0` |
| `op0391` | 391 | row | “\| Template Literal \|” | A backtick template with nothing interpolated is its text: `Hello` equals "Hello". | `run:0` |
| `op0392` | 392 | row | “\| `&{ }` \| Interpolation \|” | `&{ }` interpolates an expression's value inside a template. | `run:0` (M10 `t11_template_interpolation`) |
| `op0393` | 393 | row | “\| Escape \| Escape sequence character. \|” | `\n` is the newline byte and `\t` the tab. | `run:0` |
| `op0401` | 401 | row | “\| `//` \| Line Comment \|” | `//` comments out the rest of the line. | `run:0` |
| `op0402` | 402 | row | “\| `/*` \| Block Start \|” | `/*` begins a block comment that spans lines. | `run:0` |
| `op0403` | 403 | row | “\| `*/` \| Block End \|” | `*/` ends a block comment: code after it on the same line runs. | `run:0` |

## TRAITS (`meta/specs/TRAITS_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `tr0011` | 11 | rule | “Nitpick uses strict **composition over inheritance**” | There is no class inheritance; traits and structs compose. | untestable [vague] no inheritance spelling is named whose refusal a program could check |
| `tr0021` | 21 | example | “```nitpick” | The Serializable example (a trait with `to_bytes = buffer(Self:self)`, an impl passing `result`) compiles. | `compile` |
| `tr0037` | 37 | rule | “`Self` denotes the implementing type inside a `trait` or `impl` body” | `Self` is invalid outside a trait or impl body: a free function taking `Self` is refused. | `refuse` |
| `tr0040` | 40 | rule | “spells these `trait:Reader { … };` (no `=`)” | The struck form `trait:Reader { … };` (no `=`) is refused. | `refuse` |
| `tr0041` | 41 | rule | “`impl Reader for FileStream { … }` (space-separated)” | The struck form `impl Reader for FileStream { … }` is refused. | `refuse` |
| `tr0045` | 45 | rule | “Chapter 13's own `impl:Trait:for:Type` is also superseded” | `impl:Trait:for:Type` is superseded: refused. | `refuse` |
| `tr0048` | 48 | example | “> ```ebnf” | `impl:Type:Trait = { … };` is the impl form: it compiles and the method is called. | `run:0` |
| `tr0059` | 59 | rule | “`never fails` (`NITPICK-TYPE-041`)” | An impl may not drop a trait method's `never fails`: NITPICK-TYPE-041. | `refuse:NITPICK-TYPE-041` |
| `tr0060` | 60 | rule | “The reverse is fine — an impl may be” | An impl may be `never fails` where its trait is not; the guarantee shows on the concrete receiver: `raw l.say()` compiles. | `run:0` |
| `tr0067` | 67 | rule | “Impls that omit the method inherit it; any impl” | An impl may override a default method: the override is called. | `run:0` |
| `tr0070` | 70 | example | “```nitpick” | Describable: an impl giving only `name` inherits `describe`'s default, "an object". | `run:0` |
| `tr0084` | 84 | example | “```nitpick” | `trait:Ordered = Equatable & { … };` declares a supertrait requirement: it compiles. | `compile` |
| `tr0090` | 90 | rule | “Requirements are enforced **transitively**” | Requirements are transitive: implementing C (which requires B, which requires A) without A is refused. | `refuse` |
| `tr0097` | 97 | example | “```nitpick” | Iterator with `assoc:Item`: the impl binds `Item = int32`, and `next` returns `self.current`. | `run:0` |
| `tr0109` | 109 | rule | “Associated types may carry defaults — `assoc:Error = string;`” | An associated type may carry a default (`assoc:Error = string;`), inherited by an impl that omits it. | `compile` |
| `tr0124` | 124 | example | “```nitpick” | An inherent impl: Point's `magnitude` (flt64_sqrt over a call-cast `flt64(…)`) compiles. | `compile` |
| `tr0132` | 132 | rule | “Inherent methods dispatch **statically via UFCS**” | Inherent methods dispatch statically; `p.magnitude()` resolves to `Point_magnitude(p)`. | untestable [internal] the lowered name of an inherent method; tr0495 tests UFCS over a free function |
| `tr0136` | 136 | rule | “**A trait name is a namespace, so a method may be called qualified** (D-172)” | A trait name qualifies a method: `Speaks.say(l)` is `l.say()`. | `run:0` |
| `tr0138` | 138 | rule | “and is refused by name when” | The qualified call is refused by name when the receiver's type does not implement the trait. | `refuse` |
| `tr0139` | 139 | rule | “This is how a call disambiguates” | The qualified call disambiguates: `Ta.tag(s)` and `Tb.tag(s)` give 1 and 2. | `run:0` |
| `tr0140` | 140 | rule | “traits a type implements declare one name (`p.tag()` alone cannot choose, D-102)” | Two traits declaring one name: `p.tag()` alone is refused as ambiguous. | `refuse` |
| `tr0146` | 146 | rule | “`impl:<T>:List<T> = { … }` names its target” | A generic subject has inherent impls: `impl:<T>:Cell<T>` gives every instance the method. | `run:0` |
| `tr0149` | 149 | rule | “(`List<T>->:self`), so a generic struct's methods can mutate it” | An inherent family method may take its receiver by pointer: `l.push(v)` beside `list_push(@l, v)`. | `compile` |
| `tr0158` | 158 | example | “```nitpick” | The seven derives on Config (an int32 and a string field) compile. | `compile` |
| `tr0166` | 166 | rule | “Supported, and there are **seven** (D-123)” | There are seven derives: an eighth name (`Default`) is refused. | `refuse` |
| `tr0169` | 169 | rule | “`Ord` compares **in declaration order**” | A derived `Ord` compares fields in declaration order: (1, 9) is Less than (2, 0). | `run:0` |
| `tr0170` | 170 | rule | “`Hash` combines with **FNV-1a**” | A derived Hash combines the members with FNV-1a. | untestable [vague] the text names the function, not what bytes of each member it is fed in what order |
| `tr0175` | 175 | rule | “A refusal **names the field that blocks it**, not the type.” | A derive's refusal names the blocking field: `List<int64>` in field `items` is named. | `sh:0` |
| `tr0177` | 177 | rule | “**On a generic subject, derive writes the family form**” | `#[derive(Eq)]` on `struct:Box<T>` compiles (as `impl:<T>:Box<T>:Eq`). | `compile` |
| `tr0196` | 196 | rule | “The bound is enforced where the impl is USED” | `Box<Point>` under a derived Ord is a fine type until `cmp` is called (Point implements nothing). | `compile` |
| `tr0198` | 198 | rule | “refused naming the derive, the” | Calling `cmp` on `Box<Point>` (Point lacking Ord) is refused at the call, NITPICK-TYPE-017. | `refuse:NITPICK-TYPE-017` |
| `tr0216` | 216 | rule | “program may not declare a name the prelude declares” | A program may not declare a name the prelude declares: `struct:Ordering` is refused. | `refuse` |
| `tr0222` | 222 | rule | “**And the prelude IMPLEMENTS them for every scalar it can name**” | The prelude implements the derives for scalars: `a.cmp(b)` on two int32s is Less, `a.eq(a)` true. | `run:0` |
| `tr0230` | 230 | rule | “only, answering `NIL` for `nan`” | A float's `partial_cmp` answers NIL for nan. | `run:0` |
| `tr0233` | 233 | rule | “`string` has `Eq`, `Ord` (byte-lexicographic, the shorter prefix” | string's Ord is byte-lexicographic with the shorter prefix Less: "ab" is Less than "abc". | `run:0` |
| `tr0235` | 235 | rule | “`eq`/`cmp` trap on ERR as the operator does” | A twisted scalar's `eq` traps on ERR, as the operator does. | `trap:TbbErr` |
| `tr0236` | 236 | rule | “of a pair the prelude covers is TYPE-013” | A program's own impl of a pair the prelude covers (`impl:int32:Ord`) is NITPICK-TYPE-013. | `refuse:NITPICK-TYPE-013` |
| `tr0237` | 237 | rule | “pair it does not cover (`impl:bool:Ord`) is admitted” | A pair the prelude does not cover (`impl:bool:Ord`) is admitted. | `compile` |
| `tr0246` | 246 | row | “\| `Eq` \| `func:eq = bool(Self:self, Self:other);` \|” | Eq's method is `eq`, returning bool. | `compile` |
| `tr0247` | 247 | row | “\| `Ord` \| `func:cmp = Ordering(Self:self, Self:other);` \|” | Ord's method is `cmp`, returning Ordering. | `compile` |
| `tr0248` | 248 | row | “\| `PartialOrd` \| `func:partial_cmp = Ordering?(Self:self, Self:other);` \|” | PartialOrd's method is `partial_cmp`, returning Ordering?. | `compile` |
| `tr0249` | 249 | row | “\| `Clone` \| `func:clone = Self(Self:self);` \|” | Clone's method is `clone`, returning Self. | `compile` |
| `tr0250` | 250 | row | “\| `Hash` \| `func:hash = uint64(Self:self);` \|” | Hash's method is `hash`, returning uint64. | `compile` |
| `tr0251` | 251 | row | “\| `ToString` \| `func:to_string = string(Self:self);` \|” | ToString's method is `to_string`, returning string. | `compile` |
| `tr0252` | 252 | row | “\| `Debug` \| `func:debug = string(Self:self);` \|” | Debug's method is `debug`, returning string. | `compile` |
| `tr0254` | 254 | rule | “`Ordering` is a prelude enum — `Less`, `Equal`, `Greater`” | `Ordering` is a prelude enum with Less, Equal and Greater. | `run:0` |
| `tr0255` | 255 | rule | “integer**: the prototype returned `int32`” | An ordering is not an integer: binding one to an int32 is refused. | `refuse` |
| `tr0266` | 266 | rule | “All seven generate for a struct and for an enum” | All seven generate for an enum, `string` and bare `T` payloads included: `enum:Opt<T> = { Some(T); None; }`. | `compile` |
| `tr0280` | 280 | rule | “**DERIVE-005** — a `simd` field under anything but `Eq`” | A `simd` field under Ord is refused, NITPICK-DERIVE-005. | `refuse:NITPICK-DERIVE-005` |
| `tr0283` | 283 | rule | “**DERIVE-006** — a member no derived body can be written for” | An owning builtin member (`List<int64>`) under Eq is refused, NITPICK-DERIVE-006. | `refuse:NITPICK-DERIVE-006` |
| `tr0296` | 296 | rule | “RE-HOMED to the derive's” | A checker verdict inside a derive is re-homed to the declaration, naming the field: `bool` under Ord. | `sh:0` |
| `tr0306` | 306 | rule | “**`Default` and `Display` were listed here and are removed (D-123).**” | `Display` is removed: `#[derive(Display)]` is refused. | `refuse` |
| `tr0327` | 327 | example | “```nitpick” | A blanket impl `impl:<T: Printable>:T:Loggable` gives every Printable type `log_str`: "[LOG]". | `run:0` |
| `tr0335` | 335 | rule | “**Concrete” | A concrete impl takes priority over the blanket one. | `run:0` |
| `tr0342` | 342 | rule | “**At most one blanket impl per trait.**” | Two blanket impls of one trait are refused. | `refuse` |
| `tr0347` | 347 | rule | “**A blanket impl must name a trait.**” | A blanket impl naming no trait (`impl:<T: Printable>:T = { … };`) is refused. | `refuse` |
| `tr0350` | 350 | rule | “**A blanket impl does not apply to itself.**” | A blanket impl does not apply to itself: `impl:<T: Loggable>:T:Loggable` is refused. | `refuse` |
| `tr0356` | 356 | rule | “spells this `impl:Loggable:for:T:where:Printable = { … };`” | Chapter 13's `impl:Loggable:for:T:where:Printable` is refused. | `refuse` |
| `tr0364` | 364 | rule | “Struct fields follow module visibility — private by default, exported with `pub`.” | A struct field is private by default: a field without `pub` is not read outside its module. | `refuse` |
| `tr0368` | 368 | rule | “it is legal **only inside an” | `opaque` is legal only inside an `extern` block: one at module level is refused. | `refuse` |
| `tr0373` | 373 | example | “```nitpick” | The storage_driver extern block (an opaque struct, db_open and db_rows) compiles. | `compile` |
| `tr0384` | 384 | example | “```nitpick” | An opaque value is not copied: `Handle:h2 = h;` is refused, NITPICK-OPAQUE-COPY-001. | `sh:0` |
| `tr0392` | 392 | rule | “The standalone `opaque:DatabaseHandle;` form previously shown here is **struck**” | The standalone `opaque:DatabaseHandle;` form is struck: refused. | `refuse` |
| `tr0404` | 404 | example | “```nitpick” | Container<T> and `extract_value<T>`: extracting from a `Container<int32>` gives its value. | `run:0` |
| `tr0419` | 419 | example | “```nitpick” | Bounds with `&`: `process<T: Renderable & Serializable>` calling `item.render();` compiles. | `compile` |
| `tr0425` | 425 | rule | “places parameters **before** the name — `func<T: …>:process`” | Parameters before the name (`func<T>:process`) are struck: refused. | `refuse` |
| `tr0432` | 432 | rule | “Parameters may carry a compile-time **value** as well as a type” | A struct may take a compile-time value parameter: `Lock<int64, 2>` is a type. | `compile` |
| `tr0435` | 435 | example | “```nitpick” | `struct:Mutex<T, comptime int32:LEVEL> = { … };` and `Mutex<Config, 2>:cfg_lock;` are the value parameter's spelling: they compile. | `compile` |
| `tr0448` | 448 | rule | “**A value argument stops below the binary operators.**” | A value argument stops below the binary operators: `Lock<int64, 2 > 1>` (unparenthesised) is refused. | `refuse` |
| `tr0454` | 454 | rule | “**Only an integer literal is constant at this rung.**” | Only an integer literal is a constant value argument: a named constant is refused. | `refuse` |
| `tr0456` | 456 | rule | “**An unsuffixed literal takes the parameter's declared type; a suffixed one must” | A suffixed value argument must already be the parameter's type: `2i64` against `comptime int32` is refused. | `refuse` |
| `tr0461` | 461 | rule | “Two values are two arguments and therefore two types” | `Lock<T, 2>` and `Lock<T, 3>` are two types: one passed for the other is refused. | `refuse` |
| `tr0466` | 466 | rule | “**A bare type parameter is move-only in the body that names it (D-264,” | A bare `T` is move-only in a generic body: a plain copy `T:y = x;` is refused, NITPICK-TYPE-046. | `refuse:NITPICK-TYPE-046` |
| `tr0483` | 483 | rule | “**a body may not use any capability its bounds do not” | A generic body may not use a capability its bounds do not declare; the refusal names the declared bound. | `sh:0` |
| `tr0492` | 492 | rule | “**A bound set is transitively closed.**” | A bound set is transitively closed: under `T: Ordered` (Ordered = Equatable & …) the body uses Equatable's method. | `run:0` |
| `tr0495` | 495 | rule | “**UFCS does not reach a free function through a parameter.**” | UFCS does not reach a free function through a type parameter: `x.magnitude()` on a `T` is refused. | `refuse` |
| `tr0496` | 496 | rule | “and `magnitude(p)` are the same call for a concrete receiver (D-006)” | For a concrete receiver, `p.magnitude()` and `magnitude(p)` are the same call. | `run:0` |
| `tr0501` | 501 | rule | “**A `comptime` value parameter is not a type.**” | A comptime value parameter is not a type: `LEVEL:x` is refused. | `refuse` |
| `tr0504` | 504 | rule | “A parameter **shadows** a module-level type of the same name” | A type parameter shadows a module-level type of the same name: `func:f<T>` with `struct:T` declared compiles. | `compile` |
| `tr0513` | 513 | rule | “(`Pair<T, T>` does not match `Pair<int32, int64>`)” | A family impl's repeated parameter binds one type: `impl:<T>:Pair<T, T>:Sum` does not apply to `Pair<int32, int64>`, so `sum` on it is refused. | `refuse` |
| `tr0536` | 536 | example | “```nitpick” | Type arguments are inferred at the call: `extract(c)` with nothing written. | `run:0` |
| `tr0543` | 543 | example | “```nitpick” | Explicit type arguments in an expression are the turbofish: `count::<int32>(c)`. | `run:0` |
| `tr0549` | 549 | row | “\| Type \| bare brackets — `Handle<Node<int64>>:h;`, `struct:Container<T>` \|” | Type position takes bare brackets: `struct:Container<T>` and a `Container<Container<int64>>` parameter. | `compile` |
| `tr0550` | 550 | row | “\| Expression \| turbofish, always — `extract_value::<int32>(c)` \|” | Expression position is the turbofish, always: `count<int32>(c)` without it is refused. | `refuse` |
| `tr0551` | 551 | row | “\| `#`-builtin \| bare brackets — `#size_of<int32>()`” | A `#`-builtin takes bare brackets: `#size_of<int32>()` is 4. | `run:0` |
| `tr0554` | 554 | rule | “`enum:Opt<T: Pr> = { Some(T); None; }` instantiated as `Opt<Point>`” | An enum instance is judged like a struct's: `Opt<Point>` with Point lacking `Pr` is refused, NITPICK-TYPE-017. | `refuse:NITPICK-TYPE-017` |
| `tr0561` | 561 | rule | “naming the parameter (TYPE-022)” | A variant constructor whose instance nothing decides is refused naming the parameter, NITPICK-TYPE-022. | `refuse:NITPICK-TYPE-022` |
| `tr0563` | 563 | rule | “The earlier form — implicit `f<int32>(x)`” | The implicit `f<int32>(x)` is struck: refused. | `refuse` |
| `tr0575` | 575 | example | “```nitpick” | Nested generics close with `>>`: `Handle<Node<int64>>` is a type. | `compile` |
| `tr0586` | 586 | rule | “Instantiation depth is capped at **64**” | Instantiation depth is capped at 64: an unbounded generic recursion is a compile error, not a crash or a silent truncation. | `refuse` |
| `tr0589` | 589 | rule | “**mangled names are readable and” | Instantiations' names are readable, no hash: `idt` at `int32` is named by both. | `sh:0` |
| `tr0593` | 593 | rule | “There is **no specialization**” | No specialization: an impl for `Box<int32>` beside the family `impl:<T>:Box<T>` is refused. | `refuse` |
| `tr0602` | 602 | example | “```nitpick” | An `arena<Node<T>>` field in a generic struct, with chained access: `hdr.node_arena.alloc(my_node)`. | `compile` |
| `tr0622` | 622 | rule | “There is **at most one implementation** of a given trait for a given type.” | Two impls of one trait for one type are refused, reported at the SECOND impl. | `sh:0` |
| `tr0633` | 633 | row | “\| `impl:Item:T` twice \| overlap — the plain case \|” | The same impl twice is an overlap: refused. | `refuse` |
| `tr0634` | 634 | row | “\| `impl:<T>:Box<T>:S` and `impl:Box<int32>:S` \| **overlap**” | A family impl and an instance's are an overlap: refused. | `refuse` |
| `tr0635` | 635 | row | “\| `impl:<T>:Box<T>:S` and `impl:<U>:Box<U>:S` \| **overlap**” | Two family impls over one declaration are an overlap: refused. | `refuse` |
| `tr0636` | 636 | row | “\| two blanket impls of one trait \| overlap (§2.6, D-111) \|” | Two blanket impls of one trait are an overlap: refused. | `refuse` |
| `tr0637` | 637 | row | “\| a blanket impl and a concrete one \| **not** an overlap (§2.6)” | A blanket impl and a concrete one are not an overlap: compiles. | `compile` |
| `tr0638` | 638 | row | “\| impls of *different* traits on one type \| not an overlap” | Impls of different traits on one type are not an overlap: compiles. | `compile` |
| `tr0653` | 653 | rule | “**Every overlap report carries a NOTE at the earlier impl**” | An overlap report carries a note at the earlier impl. | `sh:0` |
| `tr0677` | 677 | rule | “every method takes a `self` parameter — no static methods” | A trait with a static method (no `self`) is not object-safe: `dyn Bad` is refused. | `refuse` |
| `tr0678` | 678 | rule | “**`Self` appears nowhere but the receiver**” | A trait whose method returns `Self` is not object-safe: `dyn Bad` is refused. | `refuse` |
| `tr0682` | 682 | rule | “**The receiver itself may be `Self` or `Self->`**” | A `Self->` receiver keeps a trait object-safe: `dyn Good` over one compiles. | `compile` |
| `tr0686` | 686 | rule | “**no generic methods**” | A trait with a generic method is not object-safe: `dyn Bad` is refused. | `refuse` |
| `tr0688` | 688 | rule | “**an `async` method requires a `Self->` receiver**” | An async method with a by-value `Self` receiver disqualifies: `dyn Bad` is refused. | `refuse` |
| `tr0696` | 696 | rule | “A method whose signature mentions an **associated type** also disqualifies” | A method mentioning an associated type disqualifies: `dyn Bad` is refused. | `refuse` |
| `tr0713` | 713 | rule | “**A bare trait is not a value type**” | A bare trait is not a value type: `Speaks:x` as a parameter is refused, NITPICK-TYPE-002. | `refuse:NITPICK-TYPE-002` |
| `tr0721` | 721 | rule | “(`{ data_ptr, vtable_ptr }`, 16 bytes on 64-bit” | A single-bound `dyn` is a fat pointer of 16 bytes. | `run:0` |
| `tr0724` | 724 | rule | “supertrait methods are not reachable” | Through `dyn Sub`, a supertrait's method is not reachable: calling it is refused. | `refuse` |
| `tr0730` | 730 | example | “```nitpick” | `dyn Serializable:obj = msg;` builds a trait object, and the method dispatches through it. | `run:0` |
| `tr0737` | 737 | example | “```nitpick” | `dyn Drawable & Serializable:obj = msg;` builds a multi-bound trait object. | `run:0` |
| `tr0741` | 741 | rule | “`dyn A & B` is assignable to `dyn A` — widening by dropping bounds” | `dyn A & B` widens to `dyn A`: the widened object still dispatches `a`. | `run:0` |
| `tr0743` | 743 | rule | “`{ data, vt_1 … vt_N }` — (N+1)×8 bytes” | `dyn` over N traits is (N+1)×8 bytes: `dyn A & B` is 24. | `run:0` |
| `tr0748` | 748 | rule | “Chapter 13 uses `+` here while using `&` for supertraits and bounds” | `+` is not the bound combinator: `dyn A + B` is refused. | `refuse` |
| `tr0751` | 751 | rule | “**`dyn` obscures the control-flow graph**” | `dyn` raises warnings under strict auditing profiles. | untestable [vague] no profile is named whose warning a program could check |
| `tr0760` | 760 | rule | “`@cast<T>` and” | `@cast<T>` is removed: refused. | `refuse` |
| `tr0762` | 762 | rule | “Integer-to-pointer casting is illegal outside” | Integer-to-pointer casting is illegal outside `#wild_ptr<T>(addr)` in wild context: `5i64 =>! int32->` is refused. | `refuse` |
| `tr0764` | 764 | rule | “Lambdas without capture” | Lambdas without capture remain as function values: one bound to a function-typed local compiles. | `compile` |

## TYPE (`meta/specs/TYPE_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `ty0003` | 3 | rule | “No C/C++ in any form” | No type is defined in C or C++: each is handwritten LLVM IR (Tier 0) or Nitpick source (Tier 1+). | untestable [tree] where a type's definition is written is a fact about the compiler's source tree |
| `ty0004` | 4 | rule | “No libc” | Programs use no libc: a program that allocates (a concatenation, a to_cstring) declares no libc allocator, stdio or string function in its IR. | `ir!:^declare [^\n]*@(?:malloc|calloc|realloc|free|printf|puts|fopen|fwrite|strlen)\(` |
| `ty0017` | 17 | rule | “These map directly to LLVM primitive types” | The fundamental scalars map directly to LLVM primitive types: an int16 function is `i16` in, `i16` out, and a flt32 one `float`. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi16 @"?(?:[\w$]+\.)*m11s16"?\(i16 )(?=.*?^define [^@\n]*\bfloat @"?(?:[\w$]+\.)*m11f32"?\(float )` |
| `ty0023` | 23 | row | “\| `bool` \| `i1` (stored as `i8`) \| 1 byte \| 1 \|” | `bool` is 1 byte with alignment 1, and `true` is 1, `false` 0. | `run:0` |
| `ty0026` | 26 | rule | “`&&` (short-circuit AND), `\|\|` (short-circuit OR)” | `&&` and `\|\|` short-circuit: the right side is not evaluated when the left decides. | `run:0` (M10 `x04_short_circuit`) |
| `ty0027` | 27 | rule | “Comparison: `==`, `!=`” | `bool` compares with `==` and `!=`. | `run:0` |
| `ty0027b` | 27 | rule | “Comparison: `==`, `!=`” | `bool` has `==` and `!=` and no ordering: `<`/`>` on bools is refused. | `refuse` (M10 `m10_bool_ordering_refused`) |
| `ty0028` | 28 | rule | “No arithmetic operations” | `bool` has no arithmetic: `true + false` is refused. | `refuse` |
| `ty0029` | 29 | rule | “Cast: `bool => int32` yields 0 or 1” | `bool => int32` yields 0 or 1. | `run:0` (M10 `c14_bool_to_int`) |
| `ty0032` | 32 | example | “```llvm” | A bool local is an `i8` alloca, and a branch on it truncates the loaded `i8` to `i1`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11bl"?\((?=(?:(?!\n\}).)*?alloca i8\b)(?=(?:(?!\n\}).)*?trunc i8 %\S+ to i1)` |
| `ty0047` | 47 | row | “\| `int8` \|” | `int8` is 1 byte with alignment 1. | `run:0` |
| `ty0048` | 48 | row | “\| `int16` \|” | `int16` is 2 bytes with alignment 2. | `run:0` |
| `ty0049` | 49 | row | “\| `int32` \|” | `int32` is 4 bytes with alignment 4. | `run:0` |
| `ty0050` | 50 | row | “\| `int64` \|” | `int64` is 8 bytes with alignment 8. | `run:0` |
| `ty0053` | 53 | rule | “Arithmetic: `+`, `-`, `*` — **overflow TRAPS**” | Plain-integer `+` traps IntOverflow on overflow. | `run:93` (M10 `o01_int32_add`) |
| `ty0053b` | 53 | rule | “Arithmetic: `+`, `-`, `*` — **overflow TRAPS**” | Plain-integer `-` traps IntOverflow on overflow. | `run:93` (M10 `o02_int32_sub`) |
| `ty0053c` | 53 | rule | “Arithmetic: `+`, `-`, `*` — **overflow TRAPS**” | Plain-integer `*` traps IntOverflow on overflow. | `run:93` (M10 `o03_int32_mul`) |
| `ty0053d` | 53 | rule | “Arithmetic: `+`, `-`, `*` — **overflow TRAPS**” | Only an overflow traps: a result equal to a type's maximum or minimum is a value. | `run:0` (M10 `o17_edges_do_not_trap`) |
| `ty0054` | 54 | rule | “`IntOverflow` (−4110)” | IntOverflow's code is -4110: the guard of a computed int32 `+` routes -4110 to failsafe. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11add"?\((?=(?:(?!\n\}).)*?-4110\b)` |
| `ty0056` | 56 | rule | “Lowers through `llvm.{s,u}{add,sub,mul}.with.overflow.iN`” | Signed `+ - *` lower through llvm.sadd/ssub/smul.with.overflow at the operand width. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11s"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i32\()(?=(?:(?!\n\}).)*?@llvm\.ssub\.with\.overflow\.i32\()(?=(?:(?!\n\}).)*?@llvm\.smul\.with\.overflow\.i32\()` |
| `ty0057` | 57 | rule | “Signedness picks the family” | Unsigned `+ - *` lower through the unsigned family llvm.uadd/usub/umul.with.overflow and not the signed one. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11u"?\((?=(?:(?!\n\}).)*?@llvm\.uadd\.with\.overflow\.i32\()(?=(?:(?!\n\}).)*?@llvm\.usub\.with\.overflow\.i32\()(?=(?:(?!\n\}).)*?@llvm\.umul\.with\.overflow\.i32\()(?!(?:(?!\n\}).)*?@llvm\.s(?:add|sub|mul)\.with\.overflow)` |
| `ty0058` | 58 | rule | “legalized at every width the language has” | The overflow trap holds at the wide widths: an int128 `+` past the maximum traps IntOverflow. | `run:93` (M10 `o16_int128_add`) |
| `ty0058b` | 58 | rule | “`int8` through `int4096`” | The overflow trap holds at the top of the ladder: an int4096 `+` past the maximum traps IntOverflow. | `trap:IntOverflow` |
| `ty0059` | 59 | rule | “A `simd`'s integer lanes go through the vector form” | A simd's integer lane that overflows traps IntOverflow as its scalar does. | `run:93` (M10 `o22_simd_lane_overflow`) |
| `ty0059b` | 59 | rule | “`.<N x iW>`” | A simd<int32, 4> `+` lowers through the vector overflow intrinsic llvm.sadd.with.overflow.v4i32. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11v"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.v4i32\()` |
| `ty0060` | 60 | rule | “overflow lanes folded to one any-lane test” | The lanes' overflow bits are folded into one any-lane test. | untestable [internal] how the overflow bits are combined changes no outcome, and the text names no instruction to look for |
| `ty0061` | 61 | rule | “traps per fold step” | An integer simd `.sum()` whose total overflows traps IntOverflow. | `trap:IntOverflow` |
| `ty0061b` | 61 | rule | “traps per fold step” | `.sum()` traps per fold step: a step that overflows traps even when the lanes' total fits. | `trap:IntOverflow` |
| `ty0062` | 62 | rule | “is checked AFTER every write” | A limit<Rules> integer binding is checked after every write: an assignment its rule refuses traps LimitViolated. | `trap:LimitViolated` |
| `ty0063` | 63 | rule | “`LimitViolated` (−4111)” | LimitViolated's code is -4111: the check after a computed write to a limit binding routes -4111 to failsafe. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11lim"?\((?=(?:(?!\n\}).)*?-4111\b)` |
| `ty0065` | 65 | rule | “their `limit` rows are decided by z3” | An integer limit row is decided by z3, and a discharged one elides into one llvm.assume over the rule's range clauses. | untestable [z3] rows are decided and elided only under `npkg verify` with the pinned z3 |
| `ty0067` | 67 | rule | “**Unary `-` is `0 - x`**” | Unary `-` traps IntOverflow on the most negative value. | `run:93` (M10 `o04_int32_negate_min`) |
| `ty0069` | 69 | rule | “**`x += y` traps identically**” | The compound `+=` traps IntOverflow exactly as `+` does. | `run:93` (M10 `o12_compound_add`) |
| `ty0071` | 71 | rule | “**Bit operations are unchanged**” | Bit operations have nothing to overflow: `<<` loses the bits past the width and does not trap. | `run:0` (M10 `o18_shift_loses_bits_no_trap`) |
| `ty0073` | 73 | rule | “`x << n` and `x >> n` are defined” | `x << n` is defined for 0 <= n < width only: a computed amount equal to the width traps ShiftRange. | `run:111` (M10 `s04_shift_amount_equals_width`) |
| `ty0073b` | 73 | rule | “`x << n` and `x >> n` are defined” | The amount rule holds for `>>` too: a computed amount equal to the width traps ShiftRange. | `run:111` (M10 `s06_right_shift_amount_width`) |
| `ty0074` | 74 | rule | “a known amount outside it is TYPE-070” | A known shift amount outside 0 <= n < width is NITPICK-TYPE-070 at the `<<`. | `refuse:NITPICK-TYPE-070` (M10 `s07_shift_literal_amount_refused`) |
| `ty0075` | 75 | rule | “the shift (both spellings)” | A known amount outside the range is TYPE-070 at a `>>` as at a `<<`. | `refuse:NITPICK-TYPE-070` |
| `ty0075b` | 75 | rule | “the shift (both spellings)” | A known amount outside the range is TYPE-070 at the compound `<<=` as at `<<`. | `refuse:NITPICK-TYPE-070` |
| `ty0075c` | 75 | rule | “a computed one is guarded by one unsigned” | A computed shift amount is guarded by one unsigned compare against the width (`icmp ult n, W`). | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11shl"?\((?=(?:(?!\n\}).)*?icmp ult i32 %\S+, 32\b)(?=(?:(?!\n\}).)*?\bshl i32 )` |
| `ty0076` | 76 | rule | “traps `ShiftRange` (−4115)” | ShiftRange's code is -4115: the guard of a computed shift amount routes -4115 to failsafe. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11shl"?\((?=(?:(?!\n\}).)*?-4115\b)` |
| `ty0077` | 77 | rule | “eliding the guard where proven” | The shift-range obligation elides the guard where it is proven. | untestable [z3] obligations are discharged only under `npkg verify` with the pinned z3 |
| `ty0078` | 78 | rule | “**`/` and `%` by zero still trap**” | Integer `/` by zero traps DivByZero. | `run:97` (M10 `v03_div_by_zero`) |
| `ty0078b` | 78 | rule | “**`/` and `%` by zero still trap**” | Integer `%` by zero traps DivByZero. | `run:97` (M10 `v04_rem_by_zero`) |
| `ty0078c` | 78 | rule | “signed `/` adds the” | Signed `/` of the minimum by -1 traps DivOverflow. | `run:98` (M10 `v05_min_div_minus_one`) |
| `ty0078d` | 78 | rule | “**`/` and `%` by zero still trap**” | The compound `/=` by zero traps DivByZero as `/` does. | `run:97` (M10 `v10_compound_div_by_zero`) |
| `ty0079` | 79 | rule | “On `tbb` both yield ERR” | On tbb, `/` and `%` by zero yield ERR and do not trap. | `run:0` (M10 `v18_tbb_div_by_zero_is_err`) |
| `ty0080` | 80 | rule | “**There are no sub-byte widths.**” | There are no sub-byte integer widths: `int4` is not a type. | `refuse` |
| `ty0081` | 81 | rule | “twins were STRUCK at D-231” | The unsigned sub-byte twins were struck too: `uint2` is not a type. | `refuse` |
| `ty0083` | 83 | rule | “a range-limited byte is `limit<Rules>`” | A range-limited byte is a limit<Rules> binding of a byte type: writing a value outside its rule traps LimitViolated. | `trap:LimitViolated` |
| `ty0084` | 84 | rule | “The ladder is `int8` … `int4096`” | The signed ladder is int8 through int4096: each rung exists and its sign bit is bit W-1 (1 << (W-1) is negative). | `run:0` |
| `ty0085` | 85 | rule | “arithmetic including `/` and `%` at 1024, 2048 and 4096 bits” | `/` and `%` compute at 1024, 2048 and 4096 bits; signed quotients truncate toward zero and remainders keep the dividend's sign. | `run:0` |
| `ty0086` | 86 | rule | “D-210 trap at 512” | An int512 addition past the maximum traps IntOverflow. | `trap:IntOverflow` |
| `ty0088` | 88 | rule | “with the compound forms `+%=`, `-%=`, `*%=`” | The compound wrapping forms `+%=`, `-%=`, `*%=` wrap modulo 2^N. | `run:0` |
| `ty0089` | 89 | rule | “is the low N bits, always” | `+% -% *%` compute modulo 2^N: the result is the low N bits. | `run:0` (M10 `o19_wrapping_family`) |
| `ty0089b` | 89 | rule | “there is no guard” | A wrapping operation has no guard: a `*%` lowers to a plain `mul` with no overflow intrinsic. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11wm"?\((?=(?:(?!\n\}).)*?= mul i32 )(?!(?:(?!\n\}).)*?with\.overflow)` |
| `ty0089c` | 89 | rule | “no obligation row” | A wrapping operation has no obligation row. | untestable [z3] obligation rows are written by `npkg verify` |
| `ty0090` | 90 | rule | “`failsafe` arm, because nothing can go wrong” | A wrapping operation arms no failsafe arm: a program whose only arithmetic is `+%`/`*%` compiles with a failsafe that does not name IntOverflow. | `run:0` |
| `ty0091` | 91 | example | “```nitpick” | `uint32:mixed = h *% 2654435761u32;` is the low 32 bits of the product. | `run:0` |
| `ty0094` | 94 | rule | “and `simd` integer lanes'” | The wrapping family applies to simd integer lanes: `+%` wraps each lane. | `run:0` |
| `ty0095` | 95 | rule | “`NITPICK-TYPE-078` names the kind” | The wrapping operators are refused on a twisted value (tbb): NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0096` | 96 | rule | “the ternary kinds saturate” | The wrapping operators are refused on a ternary kind (tryte): NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0097` | 97 | rule | “`frac` is exact or ERR” | The wrapping operators are refused on `frac`: NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0097b` | 97 | rule | “`dim256` carries a unit” | The wrapping operators are refused on `dim256`: NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0098` | 98 | rule | “`complex` computes per component” | The wrapping operators are refused on `complex`: NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0098b` | 98 | rule | “and a float is IEEE” | The wrapping operators are refused on a float: NITPICK-TYPE-078. | `refuse:NITPICK-TYPE-078` |
| `ty0098c` | 98 | rule | “A constant wrap folds” | A constant wrap folds WITH the wrap. | `run:0` (M10 `o20_wrapping_folds_with_wrap`) |
| `ty0099` | 99 | rule | “where the trapping twin is `NITPICK-TYPE-076`” | A constant `+ - *` that overflows is NITPICK-TYPE-076 where it is written. | `refuse:NITPICK-TYPE-076` (M10 `o21_constant_overflow_refused`) |
| `ty0109` | 109 | rule | “**`tbb` remains the saturate-to-ERR family**” | tbb overflow is a value the program inspects: it saturates to ERR (sticky) and `is_err` sees it without a trap. | `run:0` (M10 `m13_tbb_err_sticky`) |
| `ty0122` | 122 | rule | “Arithmetic, wrapping: `+%`, `-%`, `*%`” | `+% -% *%` lower to `add`, `sub`, `mul` with no flags. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11wr"?\((?=(?:(?!\n\}).)*?= add i32 %)(?=(?:(?!\n\}).)*?= sub i32 %)(?=(?:(?!\n\}).)*?= mul i32 %)` |
| `ty0124` | 124 | rule | “Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=` → `icmp eq/ne/slt/sgt/sle/sge`” | Signed integer comparisons are signed: -5 is below 3 under all six operators. | `run:0` |
| `ty0124b` | 124 | rule | “`icmp eq/ne/slt/sgt/sle/sge`” | A signed `<` lowers to `icmp slt`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11lt"?\((?=(?:(?!\n\}).)*?icmp slt i32 )` |
| `ty0125` | 125 | rule | “Bitwise: `&`, `\|`, `^`, `~`, `<<`, `>>`” | The bitwise operators on signed integers are and/or/xor/not/shl/ashr: `-8 >> 1` is -4. | `run:0` |
| `ty0125b` | 125 | rule | “`and`, `or`, `xor`, `shl`, `ashr`” | A signed `>>` lowers to `ashr`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11sr"?\((?=(?:(?!\n\}).)*?\bashr i32 )` |
| `ty0126` | 126 | rule | “Casting: explicit only” | Integer conversions are explicit only: an int32 assigned to an int64 without `=>` is refused. | `refuse` |
| `ty0127` | 127 | rule | “Literal suffixes: `42i32`, `-1i8`, `0FFhexi64`” | `42i32`, `-1i8` and `0FFhexi64` are literals of 42, -1 and 255. | `run:0` |
| `ty0130` | 130 | example | “```llvm” | `a + b` lowers through llvm.sadd.with.overflow.i32 and `a / b` tests the divisor against 0 before an `sdiv`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11ad"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i32\()(?=(?:(?!\n\}).)*?icmp eq i32 %\S+, 0\b)(?=(?:(?!\n\}).)*?= sdiv i32 )` |
| `ty0144` | 144 | rule | “`tbb` uses the same intrinsics” | tbb arithmetic uses the same overflow intrinsics: a tbb32 `+` lowers through llvm.sadd.with.overflow.i32. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11tb"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i32\()` |
| `ty0151` | 151 | row | “\| `uint8` \|” | `uint8` is 1 byte with alignment 1. | `run:0` |
| `ty0152` | 152 | row | “\| `uint16` \|” | `uint16` is 2 bytes with alignment 2. | `run:0` |
| `ty0153` | 153 | row | “\| `uint32` \|” | `uint32` is 4 bytes with alignment 4. | `run:0` |
| `ty0154` | 154 | row | “\| `uint64` \|” | `uint64` is 8 bytes with alignment 8. | `run:0` |
| `ty0158` | 158 | rule | “Division/modulo use `udiv`/`urem`” | Unsigned division and remainder are unsigned (udiv/urem). | `run:0` (M10 `v14_unsigned_div_rem`) |
| `ty0159` | 159 | rule | “Comparisons use `ult`/`ugt`/`ule`/`uge`” | Unsigned comparisons are unsigned (ult/ugt/ule/uge). | `run:0` (M10 `m03_unsigned_ordering`) |
| `ty0160` | 160 | rule | “Right shift uses `lshr` (logical)” | `>>` on an unsigned operand is logical. | `run:0` (M10 `s02_unsigned_right_shift_logical`) |
| `ty0161` | 161 | rule | “Overflow TRAPS, as with signed types” | Unsigned `+` overflow traps IntOverflow (255 + 1 at uint8). | `run:93` (M10 `o07_uint8_add`) |
| `ty0161b` | 161 | rule | “Overflow TRAPS, as with signed types” | Unsigned `-` below zero traps IntOverflow (0 - 1 at uint8). | `run:93` (M10 `o08_uint8_sub`) |
| `ty0164` | 164 | rule | “Literal suffixes: `42u32`, `0FFhexu8`” | `42u32` and `0FFhexu8` are literals of 42 and 255. | `run:0` |
| `ty0166` | 166 | rule | “are **semantically distinct**” | `uint8` and `char8` are distinct types: a char8 compared with a uint8 is refused. | `refuse` (M10 `m09_char_vs_uint8_refused`) |
| `ty0172` | 172 | row | “\| `flt32` \| `float` \| 4 bytes \| 4 \|” | `flt32` is 4 bytes with alignment 4. | `run:0` |
| `ty0172b` | 172 | row | “\| `flt32` \| `float` \|” | `flt32` is `float`: its arithmetic rounds at 24 significand bits. | `run:0` (M10 `f02_flt32_rounds_in_flt32`) |
| `ty0173` | 173 | row | “\| `flt64` \| `double` \| 8 bytes \| 8 \|” | `flt64` is 8 bytes with alignment 8. | `run:0` |
| `ty0174` | 174 | row | “\| `flt128` \| `fp128` \| 16 bytes \| 16 \|” | `flt128` is 16 bytes with alignment 16. | `run:0` |
| `ty0174b` | 174 | rule | “no literals, arithmetic, or comparison” | flt128 has no literals: `1.5f128` is refused. | `refuse` |
| `ty0174c` | 174 | rule | “no literals, arithmetic, or comparison” | flt128 has no arithmetic: `a + b` on flt128 values is refused. | `refuse` |
| `ty0174d` | 174 | rule | “no literals, arithmetic, or comparison” | flt128 has no comparison: `a == b` on flt128 values is refused. | `refuse` |
| `ty0174e` | 174 | rule | “holds, moves” | flt128 is storage: a value is held in a local and a struct field and moved through a function. | `run:0` |
| `ty0174f` | 174 | rule | “crosses FFI” | flt128 crosses FFI. | untestable [tool] an FFI crossing needs a foreign object linked into the program; the harness links only the runtime |
| `ty0174g` | 174 | row | “\| `flt128` \| `fp128` \|” | flt128 is `fp128` in the IR. | `ir:^define [^@\n]*\bfp128 @"?(?:[\w$]+\.)*m11fp"?\(fp128 ` |
| `ty0176` | 176 | rule | “are **reserved words, not types**” | `flt256` is not a type: a binding declared with it is refused. | `refuse` |
| `ty0176b` | 176 | rule | “are **reserved words, not types**” | `flt512` is a reserved word: it cannot name a binding. | `refuse` |
| `ty0178` | 178 | rule | “the `f256`/`f512` literal suffixes are gone” | The `f512` literal suffix is gone: `1.5f512` is refused. | `refuse` |
| `ty0181` | 181 | rule | “Arithmetic: `+`, `-`, `*`, `/`, `%` → `fadd`” | Float arithmetic is IEEE `fadd` and friends; a constant means what the run time means: 0.1 + 0.2 is not 0.3. | `run:0` (M10 `f01_decimal_sum_not_exact`) |
| `ty0181b` | 181 | rule | “`fadd`, `fsub`, `fmul`, `fdiv`, `frem`” | flt64 `+ - * /` lower to `fadd`, `fsub`, `fmul`, `fdiv` on `double`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11fa"?\((?=(?:(?!\n\}).)*?= fadd double )(?=(?:(?!\n\}).)*?= fsub double )(?=(?:(?!\n\}).)*?= fmul double )(?=(?:(?!\n\}).)*?= fdiv double )` |
| `ty0182` | 182 | rule | “(`frem` lowers to the runtime floor's hand-written, exact `fmod`/`fmodf`)” | Float `%` is the exact fmod: the result takes the dividend's sign. | `run:0` (M10 `v17_float_remainder`) |
| `ty0182b` | 182 | rule | “`frem` lowers to the runtime floor's” | flt64 `%` is emitted as `frem double`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11fr"?\((?=(?:(?!\n\}).)*?= frem double )` |
| `ty0183` | 183 | rule | “**Total, no traps**” | Float division by zero yields an infinity and does not trap. | `run:0` (M10 `v16_float_div_by_zero`) |
| `ty0186` | 186 | rule | “Negation is `fneg` (sign-bit exact” | Float negation is sign-bit exact: -(0.0) is -0.0. | `run:0` (M10 `m08_negative_zero`) |
| `ty0186b` | 186 | rule | “Negation is `fneg`” | flt64 unary `-` lowers to `fneg double`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11fn"?\((?=(?:(?!\n\}).)*?= fneg double )` |
| `ty0187` | 187 | rule | “`fcmp` ordered predicates, except `!=` which is `une`” | Float comparisons are ordered except `!=`, which is unordered: NaN != NaN is true. | `run:0` (M10 `m07_nan_comparisons`) |
| `ty0187b` | 187 | rule | “`fcmp` ordered predicates” | flt64 `!=` lowers to `fcmp une` and `<` to the ordered `fcmp olt`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11ne"?\((?=(?:(?!\n\}).)*?fcmp une double ))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11fl"?\((?=(?:(?!\n\}).)*?fcmp olt double ))` |
| `ty0189` | 189 | rule | “Literal suffixes: `3.14f32`, `2.718f64`” | `3.14f32` and `2.718f64` are float literals of those values. | `run:0` |
| `ty0189b` | 189 | rule | “`3.14flt32`” | The spelling `3.14flt32` does not lex: it is refused. | `refuse` |
| `ty0190` | 190 | rule | “carries at most 15 significant digits” | A flt32 literal with 16 significant digits is refused. | `refuse` (M10 `c25_flt32_literal_16_digits`) |
| `ty0190b` | 190 | rule | “carries at most 15 significant digits” | A flt32 literal of exactly 15 significant digits is accepted and correctly rounded (through a correctly-rounded double). | `run:0` |
| `ty0194` | 194 | rule | “Math functions (sin, cos, sqrt, …) arrive with the library tier” | Math functions arrive with the library tier, wrapping LLVM intrinsics. | untestable [vague] names no spelling, module or result to check (and 'arrive' reads as a plan) |
| `ty0198` | 198 | rule | “term of the IEEE sort” | A flt32/flt64 value is a term of the SMT IEEE sort (tier 1), with a Real-interval twin (tier 2). | untestable [z3] the encoding is exercised only by `npkg verify` with the pinned z3 |
| `ty0201` | 201 | rule | “no obligation row is a” | No obligation row is a float's. | untestable [z3] obligation rows are written by `npkg verify` |
| `ty0202` | 202 | rule | “a `limit`, a contract, an `invariant`” | A limit, contract, invariant or prove over floats is decided. | untestable [z3] decided only under `npkg verify` with the pinned z3 |
| `ty0203` | 203 | rule | “**A float `/` or `%` arms no” | A float `/` or `%` arms no DivByZero/DivOverflow: a program whose only division is a float's compiles with a failsafe that names neither. | `run:0` |
| `ty0205` | 205 | rule | “the emitter writes a bare `fdiv`/`frem`” | The emitter writes a bare `fdiv`/`frem`: no compare guards a float division. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11fd"?\((?=(?:(?!\n\}).)*?= fdiv double )(?=(?:(?!\n\}).)*?= frem double )(?!(?:(?!\n\}).)*?fcmp)` |
| `ty0205b` | 205 | rule | “a `failsafe` names the two only” | Where an integer division exists, failsafe must name DivByZero and DivOverflow: one that names neither is refused. | `refuse` |
| `ty0206` | 206 | rule | “`#sqrt` is `fp.sqrt`” | `#sqrt` is encoded as fp.sqrt; `%` and a cast out of a float stay opaque to the verifier. | untestable [z3] the encoding is exercised only by `npkg verify` with the pinned z3 |
| `ty0214` | 214 | rule | “`char8:c = 65char8;` is the letter 'A'” | `65char8` is the letter 'A'. | `run:0` |
| `ty0222` | 222 | row | “\| `char8` \| `i8` \| 1 byte \| 1 \|” | `char8` is 1 byte with alignment 1. | `run:0` |
| `ty0223` | 223 | row | “\| `char16` \| `i16` \| 2 bytes \| 2 \|” | `char16` is 2 bytes with alignment 2. | `run:0` |
| `ty0224` | 224 | row | “\| `char32` \| `i32` \| 4 bytes \| 4 \|” | `char32` is 4 bytes with alignment 4. | `run:0` |
| `ty0224b` | 224 | rule | “Unicode scalar value (full codepoint)” | A char32 is a Unicode scalar value: a literal above U+10FFFF is refused. | `refuse` |
| `ty0224c` | 224 | rule | “Unicode scalar value (full codepoint)” | A char32 is a Unicode scalar value: a surrogate (U+D800) is not one, so the literal is refused. | `refuse` |
| `ty0227` | 227 | rule | “cannot perform arithmetic on char type” | Arithmetic `+` on char8 is a compile-time error. | `refuse` |
| `ty0227b` | 227 | rule | “cannot perform arithmetic on char type” | Arithmetic `-` on char8 is a compile-time error. | `refuse` |
| `ty0227c` | 227 | rule | “cannot perform arithmetic on char type” | Arithmetic `*` on char8 is a compile-time error. | `refuse` |
| `ty0227d` | 227 | rule | “cannot perform arithmetic on char type” | Arithmetic `/` on char8 is a compile-time error. | `refuse` |
| `ty0227e` | 227 | rule | “cannot perform arithmetic on char type” | Arithmetic `%` on char8 is a compile-time error. | `refuse` |
| `ty0228` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `&` on char8 is a compile-time error. | `refuse` |
| `ty0228b` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `\|` on char8 is a compile-time error. | `refuse` |
| `ty0228c` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `^` on char8 is a compile-time error. | `refuse` |
| `ty0228d` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `~` on char8 is a compile-time error. | `refuse` |
| `ty0228e` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `<<` on char8 is a compile-time error. | `refuse` |
| `ty0228f` | 228 | rule | “cannot perform bitwise operations on char type” | Bitwise `>>` on char8 is a compile-time error. | `refuse` |
| `ty0231` | 231 | rule | “(unsigned comparison for Unicode ordering)” | char8 comparisons are unsigned: '\xC3' is above 'A'. | `run:0` (M10 `m05_char_ordering_unsigned`) |
| `ty0231b` | 231 | rule | “Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`” | Ordering is permitted on char16 and char32 too, and is unsigned: 65535char16 is above 65char16. | `run:0` |
| `ty0232` | 232 | rule | “Assignment: `char8:c = 'A';` or `char8:c = 65char8;`” | `char8:c = 'A';` and `char8:c = 65char8;` assign the same character. | `run:0` |
| `ty0233` | 233 | rule | “Indexing into char arrays” | A char array indexes to its chars: `arr[0]` is the first. | `run:0` |
| `ty0239` | 239 | row | “\| `toUpper` \|” | `toUpper` uppercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` |
| `ty0240` | 240 | row | “\| `toLower` \|” | `toLower` lowercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` |
| `ty0241` | 241 | row | “\| `isAlpha` \|” | `isAlpha` is true for letters and false for a digit and for the bytes beside 'A' and 'Z'. | `run:0` |
| `ty0242` | 242 | row | “\| `isDigit` \|” | `isDigit` is true for '0' through '9' only. | `run:0` |
| `ty0243` | 243 | row | “\| `isAlphaNumeric` \|” | `isAlphaNumeric` is true for a letter or a digit and false otherwise. | `run:0` |
| `ty0244` | 244 | row | “\| `isWhitespace` \|” | `isWhitespace` is true for exactly space, tab, CR and LF: vertical tab and form feed are not in the list. | `run:0` |
| `ty0245` | 245 | row | “\| `isUpper` \|” | `isUpper` is true for 'A' through 'Z' only. | `run:0` |
| `ty0246` | 246 | row | “\| `isLower` \|” | `isLower` is true for 'a' through 'z' only. | `run:0` |
| `ty0247` | 247 | row | “\| `toUint` \|” | `toUint` reinterprets a char8 as its uint8 byte. | `run:0` |
| `ty0248` | 248 | row | “\| `fromUint` \|” | `fromUint` reinterprets a uint8 as the char8 of that byte. | `run:0` |
| `ty0249` | 249 | row | “\| `toChar16` \|” | `toChar16` zero-extends a char8: '\xE9' becomes 233char16. | `run:0` |
| `ty0250` | 250 | row | “\| `toChar32` \|” | `toChar32` zero-extends a char8: '\xFF' becomes 255char32. | `run:0` |
| `ty0257` | 257 | example | “```llvm” | A char8 range test lowers to the unsigned predicates `icmp uge i8 ..., 65` and `icmp ule i8 ..., 90`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11cu"?\((?=(?:(?!\n\}).)*?icmp uge i8 %\S+, 65\b)(?=(?:(?!\n\}).)*?icmp ule i8 %\S+, 90\b)` |
| `ty0272` | 272 | example | “```nitpick” | The character literals compile to their code units: '\n' 10, '\t' 9, '\0' 0, '\\' 92, '\'' 39, '\x41' 'A', and '\u{1F600}' in a char32 is U+1F600. | `run:0` |
| `ty0280` | 280 | rule | “// Unicode escape (char32 only)” | The `\u{...}` escape is for char32 only: in a char8 slot it is refused. | `refuse` |
| `ty0285` | 285 | example | “```nitpick” | The example compiles: a char8[5] holds 5 chars, `cstring:cs = "Hello";` is a cstring of length 5, and `to_cstring` of a clean string succeeds. | `run:0` |
| `ty0286` | 286 | rule | “char arrays do NOT implicitly add a null byte” | A char array holds exactly its elements: `char8[5]` of 'Hello' has len 5 and occupies 5 bytes. | `run:0` |
| `ty0290` | 290 | rule | “cstring:cs = "Hello";” | A string literal in cstring position is a cstring: `cstring:cs = "Hello";` compiles with length 5. | `run:0` |
| `ty0295` | 295 | rule | “ERROR: cannot assign char8[] to string” | A char array is not a string: assigning one to a `string` is a compile error. | `refuse` |
| `ty0304` | 304 | row | “\| `trit` \| A base-3 unit of information” | A trit holds the base-3 digits 0 and 1 (common to both readings the row gives). | `run:0` |
| `ty0304b` | 304 | rule | “(values: -1, 0, 1 or 0, 1, 2)” | A trit holds three values: 3 is outside both readings and is refused. | `refuse` |
| `ty0305` | 305 | row | “\| `tryte` \| A block of 10 trits” | A tryte is 10 trits: it holds 29524 (ten balanced trits; six would stop at 364) and has 10 digits. | `run:0` |
| `ty0306` | 306 | row | “\| `nit` \| Base-9 primitive (values: 0-8)” | A nit takes the values 0 to 8: `nit:n = 8;` holds 8. | `run:0` |
| `ty0307` | 307 | row | “\| `nyte` \| A block of 2 nits (values: 0-80)” | A nyte is 2 nits holding 0 to 80: `nyte:n = 81;` is out of range and refused. | `refuse` |
| `ty0307b` | 307 | rule | “(values: 0-80)” | A nyte holds 80, the top of the row's range. | `run:0` |
| `ty0308` | 308 | row | “\| `tensor` \| N-dimensional array primitive.” | `tensor` is a native primitive: `tensor<flt64>` names a type with no import. | `run:0` |
| `ty0308b` | 308 | row | “Emits LLVM vector/SIMD intrinsics.” | Tensor operations emit LLVM vector/SIMD intrinsics. | untestable [vague] names no operation (and no construction in this range) whose emission could be checked |
| `ty0309` | 309 | row | “\| `matrix` \| 2D data primitive.” | `matrix` is a native primitive: `matrix<flt64>` names a type with no import. | `run:0` |
| `ty0309b` | 309 | row | “Hardware-accelerated dot products / SGEMM.” | Matrix operations are hardware-accelerated dot products / SGEMM. | untestable [vague] names no operation or instruction to check |
| `ty0319` | 319 | row | “\| `string` \| `string<char8>` \| `{ptr, i64, i64}` \| 24 bytes \| 8 \|” | `string` is 24 bytes with alignment 8. | `run:0` |
| `ty0319b` | 319 | row | “\| `string` \| `string<char8>` \|” | `string` is an alias for `string<char8>`: a `string<char8>` is accepted wherever a string is. | `run:0` |
| `ty0320` | 320 | row | “\| `string<char16>` \| — \| `{ptr, i64, i64}` \| 24 bytes \| 8 \|” | `string<char16>` is 24 bytes with alignment 8. | `run:0` |
| `ty0321` | 321 | row | “\| `string<char32>` \| — \| `{ptr, i64, i64}` \| 24 bytes \| 8 \|” | `string<char32>` is 24 bytes with alignment 8. | `run:0` |
| `ty0322` | 322 | row | “\| `cstring` \| — \| `{ptr, i64}` \| 16 bytes \| 8 \|” | `cstring` is 16 bytes with alignment 8. | `run:0` |
| `ty0327` | 327 | rule | “is not NUL-terminated” | A `string` is `{ptr, len, cap}` and is not NUL-terminated. | untestable [unobservable] a byte after a string's last is out of its bounds: no in-bounds read can see whether it is 0 |
| `ty0330` | 330 | rule | “pointers are thin” | Pointers are thin: an `int8->` parameter is one `ptr`, with no bounds metadata. | `ir:^define [^@\n]*\bi8 @"?(?:[\w$]+\.)*m11tp"?\(ptr ` |
| `ty0332` | 332 | rule | “a `string` may carry an interior NUL” | A `string` may carry an interior NUL: one built at run time keeps all its bytes. | `run:0` |
| `ty0338` | 338 | example | “```llvm” | A `string` is the struct `{ ptr, i64, i64 }`: a string parameter has that type. | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11sl"?\(\{ ?ptr, i64, i64 ?\} ` |
| `ty0340` | 340 | rule | “(heap-allocated data buffer)” | A string's data buffer is heap-allocated. | untestable [vague] §3.3 (line 435) says a literal's buffer is constant data, so no one outcome is stated; no program here can see where a buffer lives |
| `ty0341` | 341 | rule | “length (number of char units, NOT bytes for char16/32)” | A string's length counts char units, which for `string` are bytes. | `run:0` (M10 `t01_byte_length_utf8`) |
| `ty0342` | 342 | rule | “capacity (allocated char units)” | Field 2 of a string is its capacity in char units. | untestable [internal] no accessor for the capacity is documented; a program cannot read it |
| `ty0348` | 348 | row | “\| 0 \| 8 \| data \| `ptr`” | The data pointer is at offset 0: the struct opens with `ptr` ({ptr, i64, i64}). | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11sd"?\(\{ ?ptr, i64, i64 ?\} ` |
| `ty0349` | 349 | row | “\| 8 \| 8 \| length \| `i64` \|” | The length is field 1 (offset 8): `s.len` reads field 1 of the string struct. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11ln"?\((?=(?:(?!\n\}).)*?(?:extractvalue \{ ?ptr, i64, i64 ?\} %\S+, 1\b|getelementptr [^\n]*\{ ?ptr, i64, i64 ?\}, ptr %\S+, i32 0, i32 1\b))` |
| `ty0350` | 350 | row | “\| 16 \| 8 \| capacity \| `i64` \|” | The capacity is field 2 (offset 16). | untestable [internal] no accessor for the capacity is documented; its position shows only in the struct type ty0348 checks |
| `ty0355` | 355 | rule | “`+` is **concatenation**, NOT addition” | On `string`, `+` is concatenation. | `run:0` (M10 `t14_string_plus_concatenates`) |
| `ty0355b` | 355 | rule | “No `-`, `*`, `/`, `%`.” | `-` on strings is refused. | `refuse` |
| `ty0355c` | 355 | rule | “No `-`, `*`, `/`, `%`.” | `*` on strings is refused. | `refuse` |
| `ty0355d` | 355 | rule | “No `-`, `*`, `/`, `%`.” | `/` on strings is refused. | `refuse` |
| `ty0355e` | 355 | rule | “No `-`, `*`, `/`, `%`.” | `%` on strings is refused. | `refuse` |
| `ty0358` | 358 | rule | “allocates new buffer, copies both” | `a + b` allocates a new buffer and copies both operands: `a` and `b` stay usable and unchanged. | `run:0` |
| `ty0359` | 359 | rule | “Comparison: `a.eq(b)`” | `a.eq(b)` (the prelude's string: Eq) compares byte by byte. | `run:0` |
| `ty0359b` | 359 | rule | “`string_eq(a, b)`” | `string_eq(a, b)` compares byte by byte. | `run:0` |
| `ty0360` | 360 | rule | “**`==` and `!=` are REFUSED on a `string`**” | `==` on strings is refused: NITPICK-TYPE-034. | `refuse:NITPICK-TYPE-034` (M10 `m11_string_eq_refused`) |
| `ty0360b` | 360 | rule | “**`==` and `!=` are REFUSED on a `string`**” | `!=` on strings is refused: NITPICK-TYPE-034. | `refuse:NITPICK-TYPE-034` |
| `ty0364` | 364 | rule | “Ordering: `a.cmp(b)`” | `a.cmp(b)` orders strings lexicographically. | `run:0` (M10 `t16_string_order`) |
| `ty0365` | 365 | rule | “the operators are refused as `==` is” | The ordering operators are refused on strings: `a < b` is refused. | `refuse` |
| `ty0365b` | 365 | rule | “the operators are refused as `==` is” | The ordering operators are refused on strings: `a <=> b` is refused. | `refuse` |
| `ty0366` | 366 | rule | “Indexing: `char8:c = s[0];`” | `s[i]` returns the char at that index. | `run:0` (M10 `t08_string_index`) |
| `ty0366b` | 366 | rule | “(bounds-checked)” | String indexing is bounds-checked: past the end traps OutOfBounds. | `run:94` (M10 `t09_string_index_past_end`) |
| `ty0367` | 367 | rule | “Length: `int64:len = s.length;`” | A string's length is the field `s.length`. | `run:0` (M10 `t02_length_spelled_length`) |
| `ty0373` | 373 | row | “\| `charAt` \|” | `charAt(s, i)` is the char at index i. | `run:0` |
| `ty0373b` | 373 | row | “Get character at index (bounds-checked)” | `charAt` is bounds-checked: an index past the end traps OutOfBounds. | `trap:OutOfBounds` |
| `ty0374` | 374 | row | “\| `substring` \|” | `substring(s, start, length)` extracts `length` chars from `start`. | `run:0` |
| `ty0375` | 375 | row | “\| `split` \|” | `split(s, c)` splits by the delimiter into its parts. | `run:0` |
| `ty0376` | 376 | row | “\| `trim` \|” | `trim` removes leading and trailing whitespace. | `run:0` |
| `ty0377` | 377 | row | “\| `trimLeft` \|” | `trimLeft` removes leading whitespace only. | `run:0` |
| `ty0378` | 378 | row | “\| `trimRight` \|” | `trimRight` removes trailing whitespace only. | `run:0` |
| `ty0379` | 379 | row | “\| `contains` \|” | `contains(s, t)` is a substring search. | `run:0` |
| `ty0380` | 380 | row | “\| `startsWith` \|” | `startsWith(s, p)` is a prefix check. | `run:0` |
| `ty0381` | 381 | row | “\| `endsWith` \|” | `endsWith(s, p)` is a suffix check. | `run:0` |
| `ty0382` | 382 | row | “\| `indexOf` \|” | `indexOf(s, c)` is the first occurrence's index, -1 if not found. | `run:0` |
| `ty0383` | 383 | row | “\| `toUpper` \|” | `toUpper(s)` uppercases the ASCII letters and leaves other bytes alone. | `run:0` |
| `ty0384` | 384 | row | “\| `toLower` \|” | `toLower(s)` lowercases the ASCII letters and leaves other bytes alone. | `run:0` |
| `ty0385` | 385 | row | “\| `toCharArray` \|” | `toCharArray(s, dest)` copies into a caller-owned destination and returns the elements written. | `run:0` |
| `ty0386` | 386 | row | “\| `fromCharArray` \|” | `fromCharArray(a)` copies a char array into a string. | `run:0` |
| `ty0387` | 387 | row | “\| `to_cstring` \|” | `to_cstring` fails on an interior NUL and succeeds on a clean string. | `run:0` (M10 `t12_to_cstring_interior_nul`) |
| `ty0388` | 388 | row | “\| `to_string` \|” | `to_string(c)` copies a cstring out into a string. | `run:0` |
| `ty0392` | 392 | rule | “so it cannot be” | A `string` cannot be handed to a syscall: passing one where a builtin takes a cstring is refused. | `refuse` |
| `ty0393` | 393 | rule | “`cstring` is the type that can” | A `cstring` can be handed to a syscall. | `run:0` |
| `ty0395` | 395 | example | “```” | `cstring` is `{ ptr, len }`: a cstring parameter is the struct `{ ptr, i64 }`. | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11cl"?\(\{ ?ptr, i64 ?\} ` |
| `ty0399` | 399 | rule | “**The length is retained**” | A cstring retains its length: `.len` excludes the terminator. | `run:0` (M10 `t13_cstring_keeps_length`) |
| `ty0399b` | 399 | rule | “The buffer is `len + 1` bytes with `buf[len] == 0u8`.” | A cstring's buffer holds a NUL at index len. | `run:0` |
| `ty0400` | 400 | rule | “never calls `strlen`” | nlibc never calls strlen: the unbounded scan is absent from every path and name in the library. | untestable [tree] a claim about the library's source |
| `ty0404` | 404 | rule | “**`to_cstring` fails on an interior NUL.**” | `to_cstring` fails on an interior NUL. | `run:0` (M10 `t12_to_cstring_interior_nul`) |
| `ty0414` | 414 | row | “\| string literal in `cstring` position \| compile time” | A string literal in cstring position costs nothing at run time: it is a NUL-terminated constant. | `ir:constant \[4 x i8\] c"abc\\00"` |
| `ty0414b` | 414 | rule | “interior NUL is a compile error” | A string literal with an interior NUL in cstring position is a compile error. | `refuse` |
| `ty0415` | 415 | row | “\| `to_cstring(s)` on a runtime `string`” | `to_cstring` on a string built at run time: an interior NUL is Result.err, a clean one converts. | `run:0` |
| `ty0418` | 418 | rule | “until D-053 removed that type” | The `fmt` type was removed: a binding of type `fmt` is refused. | `refuse` |
| `ty0420` | 420 | rule | “`cstring` is immutable” | `cstring` is immutable: writing its field is refused. | `refuse` |
| `ty0421` | 421 | rule | “is an explicit `to_string`” | cstring to string is only the explicit `to_string`: an implicit assignment is refused. | `refuse` |
| `ty0426` | 426 | example | “```nitpick” | `string:greeting = "Hello, world!";` compiles, a 13-byte string. | `run:0` |
| `ty0430` | 430 | example | “```llvm” | A string literal is emitted as a constant `[13 x i8]` of its bytes, with no NUL. | `ir:constant \[13 x i8\] c"Hello, world!"` |
| `ty0453` | 453 | rule | “i128 division emits the four `__divti3`-family libcalls” | i128 division works through the runtime floor's __divti3 family: signed and unsigned `/` and `%` compute and link. | `run:0` |
| `ty0455` | 455 | rule | “expands inline” | Division at a width above 128 expands inline: an int256 `/` and `%` compute and link with no libcall. | `run:0` |
| `ty0456` | 456 | rule | “ARE the LLVM types; nothing is limbed” | Wide integers are the LLVM types: an int256 function takes and returns `i256` and adds through the i256 intrinsic. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11w"?\(i256 )(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11w"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i256\())` |
| `ty0460` | 460 | row | “\| `int128` /” | `int128` / `uint128` / `tbb128` are 16 bytes with alignment 16. | `run:0` |
| `ty0461` | 461 | row | “\| `int256` /” | `int256` / `uint256` / `tbb256` are 32 bytes with alignment 16. | `run:0` |
| `ty0462` | 462 | row | “\| `int512` /” | `int512` / `uint512` are 64 bytes with alignment 16. | `run:0` |
| `ty0463` | 463 | row | “\| `int1024` /” | `int1024` / `uint1024` are 128 bytes with alignment 16. | `run:0` |
| `ty0464` | 464 | row | “\| `int2048` /” | `int2048` / `uint2048` are 256 bytes with alignment 16. | `run:0` |
| `ty0465` | 465 | row | “\| `int4096` /” | `int4096` / `uint4096` are 512 bytes with alignment 16. | `run:0` |
| `ty0469` | 469 | rule | “put `{i8, i128}` at 32 bytes and `{i8, i256}` at 48” | `{int8, int128}` is 32 bytes and `{int8, int256}` is 48. | `run:0` |
| `ty0471` | 471 | rule | “the frontend now stores exactly this column” | The frontend's layout of wide fields is LLVM's: `{int8, int256, int8}` is 64 bytes, `{int8, tbb256}` 48, and the fields round-trip. | `run:0` |
| `ty0475` | 475 | rule | “ordinary integer semantics at every width — D-037 wrapping” | The wide integers have D-037 wrapping: an int128 `+` past the maximum wraps to the minimum. | `run:0` |
| `ty0476` | 476 | rule | “D-092 explicit widening” | Widening to a wide integer is explicit: an int64 assigned to an int256 without `=>` is refused. | `refuse` |
| `ty0476b` | 476 | rule | “D-092 explicit widening” | An explicit widening keeps the value: a negative int64 sign-extends, a uint64 zero-extends. | `run:0` |
| `ty0476c` | 476 | rule | “the D-142 division guards (zero divisor” | At a wide width, integer division by zero traps DivByZero. | `trap:DivByZero` |
| `ty0477` | 477 | rule | “structural INT_MIN/−1 check” | The signed minimum divided by -1 traps DivOverflow (at int8). | `run:98` (M10 `v07_int8_min_div_minus_one`) |
| `ty0477c` | 477 | rule | “which is width-independent by construction” | At a wide width, the signed minimum divided by -1 traps DivOverflow. | `trap:DivOverflow` |
| `ty0485` | 485 | rule | “reserves a specific value (the most negative value)” | tfp's error state is the most negative raw value, and it is sticky. | `run:0` |
| `ty0487` | 487 | rule | “resolve to this error state rather than crashing” | tfp operations that overflow or divide by zero resolve to ERR rather than trapping. | `run:0` |
| `ty0491` | 491 | row | “\| `tfp32` \|” | `tfp32` is 4 bytes, alignment 4, format Q16.16: the least step is 2^-16 and the integer part tops out at 2^15 - 1. | `run:0` |
| `ty0492` | 492 | row | “\| `tfp64` \|” | `tfp64` is 8 bytes, alignment 8, format Q32.32: the least step is 2^-32 and the integer part tops out at 2^31 - 1. | `run:0` |
| `ty0493` | 493 | row | “\| `tfp128` \|” | `tfp128` is 16 bytes, alignment 16, format Q64.64: the least step is 2^-64 and the integer part tops out at 2^63 - 1. | `run:0` |
| `ty0494` | 494 | row | “\| `tfp256` \| `i256` \| 32 bytes \| Q128.128 \| 16 \|” | `tfp256` is 32 bytes, alignment 16, format Q128.128: 2^-128 is its least step and the integer part tops out at 2^127 - 1. | `run:0` |
| `ty0497` | 497 | example | “```nitpick” | Suffixing a numeric literal with the type name makes a tfp literal of that value. | `run:0` |
| `ty0504` | 504 | rule | “Add/sub: same as integer add/sub on the raw representation” | tfp add and subtract are the integer add/sub of the raw values. | `run:0` |
| `ty0505` | 505 | rule | “Mul: `(a * b) >> FRAC_BITS`” | tfp multiply is `(a * b) >> FRAC_BITS` on the raws: the shift floors, so -2^-16 * 0.5 is -2^-16 and 2^-16 * 0.5 is 0. | `run:0` |
| `ty0506` | 506 | rule | “Div: `(a << FRAC_BITS) / b`” | tfp divide is `(a << FRAC_BITS) / b` on the raws, an integer division that truncates toward zero: 1/3 and -1/3 are ±21845/65536 at tfp32. | `run:0` |
| `ty0507` | 507 | rule | “Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`, `<=>` (spaceship)” | tfp values compare with all six operators and `<=>`, which yields -1, 0 or 1. | `run:0` |
| `ty0509` | 509 | rule | “overflow produce the `ERR` sentinel” | An overflowing tfp operation produces ERR and it is sticky: ERR * 0, ERR - ERR and -ERR stay ERR. | `run:0` |
| `ty0510` | 510 | rule | “a comparison on an ERR operand TRAPS to `failsafe`” | A comparison with an ERR tfp operand traps to failsafe (TbbErr, the family's one trap, line 723). | `trap:TbbErr` |
| `ty0512` | 512 | rule | “`is_err(x)` is the test that looks” | `is_err` tests a tfp for ERR without trapping. | `run:0` |
| `ty0514` | 514 | rule | “Remainder: `%` — the same-scale remainder” | tfp `%` is the same-scale remainder (the sign of the dividend), and `% 0` is ERR. | `run:0` |
| `ty0515` | 515 | rule | “Unary negation: `-val` (total” | tfp negation is total: the most positive value negates to a valid value (not ERR), and -ERR is ERR. | `run:0` |
| `ty0516` | 516 | rule | “Shift / bitwise on the raw representation~~ — STRUCK” | Bitwise operators on tfp are struck: `a & b` is refused. | `refuse` |
| `ty0516b` | 516 | rule | “Shift / bitwise on the raw representation~~ — STRUCK” | Shifts on tfp are struck: `x << 1` is refused (`ERR << 1` would launder ERR to zero). | `refuse` |
| `ty0518` | 518 | rule | “Scaling is multiplication by a power-of-two constant” | Scaling a tfp is multiplication by a power-of-two constant, exact both ways. | `run:0` |
| `ty0520` | 520 | rule | “`floor` and `trunc` are METHODS on every width” | `.floor()` (toward -inf) and `.trunc()` (toward zero) are methods at every tfp width. | `run:0` |
| `ty0521` | 521 | rule | “`tfp256_*` free-function family” | The `tfp256_*` free functions are struck: `tfp256_floor(x)` is refused. | `refuse` |
| `ty0522` | 522 | example | “```nitpick” | `3.7tfp256.floor()` and `.trunc()` are both 3.0tfp256. | `run:0` |
| `ty0529` | 529 | example | “```nitpick” | The cast block's accepted lines compile and compute: 42.5 into flt64 both ways, 42 by `=>!` to int64, 42.5 narrowed to tfp64, 1.5 widened to tfp128. | `run:0` |
| `ty0531` | 531 | rule | “32 raw bits fit a 53-bit mantissa exactly” | `tfp32 => flt64` is accepted and exact, even for a value using all 32 raw bits. | `run:0` |
| `ty0533` | 533 | rule | “Q128.128 into 52 mantissa bits LOSES” | tfp256 into flt64 loses precision, so the plain `=>` is refused. | `refuse` |
| `ty0534` | 534 | rule | “COMPILE ERROR — drops the fractional part” | `tfp256 => int64` is a compile error: it drops the fractional part. | `refuse` |
| `ty0535` | 535 | rule | “truncates toward zero, yields 42” | `tfp256 =>! int64` truncates toward zero: 42.5 gives 42 and -42.5 gives -42. | `run:0` |
| `ty0536` | 536 | rule | “narrowing: precision loss, so =>! is required” | Narrowing tfp256 to tfp64 requires `=>!`: the plain `=>` is refused. | `refuse` |
| `ty0537` | 537 | rule | “widening keeps every value; ERR maps to ERR” | Widening tfp64 to tfp128 keeps every value (the most negative valid one included) and maps ERR to ERR. | `run:0` |
| `ty0540` | 540 | rule | “A cast OUT of the family TRAPS on an ERR operand under BOTH spellings” | A cast of an ERR tfp out of the family with `=>!` traps (TbbErr). | `trap:TbbErr` |
| `ty0540b` | 540 | rule | “under BOTH spellings” | A cast of an ERR tfp out of the family with the plain `=>` traps (TbbErr). | `trap:TbbErr` |
| `ty0544` | 544 | rule | “is a **compile-time error** wherever data loss is possible” | `=>` is a compile-time error wherever data loss is possible: `flt64 => tfp32` is refused. | `refuse` |
| `ty0553` | 553 | rule | “Only `dim256` supports” | Only dim256 takes a unit annotation: `tfp64<Meters>` is refused. | `refuse` |
| `ty0559` | 559 | rule | “vectors themselves and is TOTAL” | The unit algebra is total: products and quotients whose vectors nothing names compose and cancel. | `run:0` |
| `ty0560` | 560 | rule | “Two `dim256` types are the same type” | Two dim256 types are the same exactly when their vectors are equal: Kilograms * (m/s)^2 and Newtons * Meters are both Joules. | `run:0` |
| `ty0562` | 562 | rule | “which is why `dist / dist` is a bare” | The dimensionless vector IS tfp256: `dist / dist` is a bare tfp256. | `run:0` |
| `ty0563` | 563 | rule | “why bare `dim256` (as an annotation or a literal suffix) is” | Bare `dim256` as an annotation is refused. | `refuse` |
| `ty0564` | 564 | rule | “refused — the dimensionless type already has a name” | Bare `dim256` as a literal suffix is refused. | `refuse` |
| `ty0567` | 567 | example | “```nitpick” | `dim256<Unit>` bindings take `dim256<Unit>`-suffixed literals of those values. | `run:0` |
| `ty0573` | 573 | rule | “The seven SI base units are compiler-declared” | The seven SI base units Kilograms, Meters, Seconds, Amperes, Kelvin, Moles and Candela are declared. | `run:0` |
| `ty0576` | 576 | rule | “`Pascals`, `Watts`, `MetersPerSecond`, …) are PRELUDE declarations” | The derived names Newtons, Joules, Hertz, Pascals, Watts and MetersPerSecond are declared in the prelude with their SI vectors. | `run:0` |
| `ty0580` | 580 | example | “```nitpick” | Unit declarations of this form compile, and a declared name is its vector's name (Furlongs is Meters). | `run:0` |
| `ty0588` | 588 | rule | “unit names, `1`, `*`, `/`,” | A unit declaration's right-hand side is unit algebra only: a number other than 1 is refused. | `refuse` |
| `ty0589` | 589 | rule | “An annotation position takes a” | An annotation takes a single unit name, never an inline expression: `dim256<Meters / Seconds>` is refused. | `refuse` |
| `ty0593` | 593 | rule | “is IDENTICAL to bare `tfp256` at the” | `dim256<Joules>` is identical to tfp256 at the IR: functions over each take and return `i256`. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11dj"?\(i256 )(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11tf"?\(i256 )` |
| `ty0595` | 595 | rule | “every D-195 `tfp256` rule (ERR discipline, saturation” | Every tfp256 rule applies to dim256 unchanged: floor/trunc, saturation to ERR, ERR on division by zero. | `run:0` |
| `ty0599` | 599 | example | “```nitpick” | Units are tracked through arithmetic: `dim256<Meters>:speed = dist / time;` is a compile error. | `refuse` |
| `ty0608` | 608 | rule | “OK: Newtons * Meters IS the Joules vector” | `force * dist` of Newtons and Meters is a Joules value, with no registration. | `run:0` |
| `ty0612` | 612 | rule | “Adding/subtracting/`%` same unit” | `+`, `-` and `%` of the same unit keep the unit. | `run:0` |
| `ty0613` | 613 | rule | “Adding/subtracting different units” | Adding different units is a compile-time error. | `refuse` |
| `ty0613b` | 613 | rule | “Adding/subtracting different units” | Subtracting different units is a compile-time error. | `refuse` |
| `ty0614` | 614 | rule | “a bare `tfp256` operand is the” | Multiplying or dividing by a bare tfp256 scales, in either operand order; tfp256 over a unit inverts it. | `run:0` |
| `ty0616` | 616 | rule | “Comparing different units” | Comparing different units is a compile-time error. | `refuse` |
| `ty0616b` | 616 | rule | “same vector: full ordering” | Values of the same vector have the full ordering. | `run:0` |
| `ty0618` | 618 | rule | “`dim256<U> => tfp256`: ✅ drops the unit” | `dim256<U> => tfp256` drops the unit, and an ERR rides through it without a trap. | `run:0` |
| `ty0621` | 621 | rule | “`tfp256 =>! dim256<U>`: the acknowledged unit ASSERTION” | `tfp256 =>! dim256<U>` asserts a unit and keeps the value. | `run:0` |
| `ty0622` | 622 | rule | “refuses — a silent unit-gain is how unit bugs are born” | Without `=>!`, `tfp256 => dim256<U>` is refused. | `refuse` |
| `ty0624` | 624 | rule | “`dim256<U> => dim256<V>`” | `dim256<U> => dim256<V>` is impossible: refused. | `refuse` |
| `ty0624b` | 624 | rule | “❌ CAST_IMPOSSIBLE” | A unit relabel is impossible under `=>!` too: `dim256<U> =>! dim256<V>` is refused. | `refuse` |
| `ty0624c` | 624 | rule | “`dim256<U>` ⇄ anything else” | A dim256 casts to nothing but tfp256: `dim256<U> =>! int64` is refused. | `refuse` |
| `ty0625` | 625 | rule | “a relabel is spelled as its two honest halves” | A relabel is `=> tfp256` then `=>! dim256<V>`, keeping the value. | `run:0` |
| `ty0627` | 627 | rule | “a dimensioned value has no `ToString` BY DESIGN” | A dimensioned value has no ToString: interpolating one is refused. | `refuse` |
| `ty0628` | 628 | rule | “drops are explicit: `&{x => tfp256}`” | Rendering a dimensioned value is the explicit drop `&{x => tfp256}`. | `run:0` |
| `ty0631` | 631 | example | “```nitpick” | A function declared to return `dim256<Meters>` that passes `d / t` (Meters*Seconds^-1) is a type error. | `refuse` |
| `ty0634` | 634 | rule | “Must declare return as dim256<MetersPerSecond>” | Declared to return dim256<MetersPerSecond>, the same body compiles and computes d / t. | `run:0` |
| `ty0634b` | 634 | rule | “or bare tfp256” | Declared to return bare tfp256, the same body `pass(d / t)` compiles. | `run:0` |
| `ty0639` | 639 | example | “```nitpick” | A struct may hold dim256 fields of different units; they read and compose. | `run:0` |
| `ty0648` | 648 | example | “```llvm” | At the IR, dim256<Joules> is tfp256, whose type is `{ i64, i64, i64, i64 }`. | `ir:^%\"?tfp256\"? = type \{ ?i64, i64, i64, i64 ?\}|^define [^@\n]* @"?(?:[\w$]+\.)*m11dj"?\(\{ ?i64, i64, i64, i64 ?\} ` |
| `ty0654` | 654 | rule | “The dimensional annotation is attached to the AST type node” | The annotation lives on the AST type node; the type checker verifies the algebra and codegen ignores it. | untestable [internal] the AST's type node is not observable; codegen's ignoring the unit is ty0593's IR test |
| `ty0663` | 663 | rule | “**reserved as the ERR sentinel**” | The most negative bit pattern is ERR, not a number: -127 is a tbb8 value, and -127 - 1 is ERR. | `run:0` |
| `ty0669` | 669 | row | “\| `tbb8` \|” | `tbb8` is 1 byte with alignment 1; its valid range is symmetric, -(2^7-1) .. 2^7-1, and one step past either end is ERR. | `run:0` |
| `ty0669b` | 669 | row | “\| `tbb8` \| `i8` \|” | A `tbb8` parameter is an `i8` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i8\b` |
| `ty0670` | 670 | row | “\| `tbb16` \|” | `tbb16` is 2 bytes with alignment 2; its valid range is symmetric, -(2^15-1) .. 2^15-1, and one step past either end is ERR. | `run:0` |
| `ty0670b` | 670 | row | “\| `tbb16` \| `i16` \|” | A `tbb16` parameter is an `i16` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i16\b` |
| `ty0671` | 671 | row | “\| `tbb32` \|” | `tbb32` is 4 bytes with alignment 4; its valid range is symmetric, -(2^31-1) .. 2^31-1, and one step past either end is ERR. | `run:0` |
| `ty0671b` | 671 | row | “\| `tbb32` \| `i32` \|” | A `tbb32` parameter is an `i32` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i32\b` |
| `ty0672` | 672 | row | “\| `tbb64` \|” | `tbb64` is 8 bytes with alignment 8; its valid range is symmetric, -(2^63-1) .. 2^63-1, and one step past either end is ERR. | `run:0` |
| `ty0672b` | 672 | row | “\| `tbb64` \| `i64` \|” | A `tbb64` parameter is an `i64` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i64\b` |
| `ty0673` | 673 | row | “\| `tbb128` \|” | `tbb128` is 16 bytes with alignment 8; its valid range is symmetric, -(2^127-1) .. 2^127-1, and one step past either end is ERR. | `run:0` |
| `ty0673b` | 673 | row | “\| `tbb128` \| `i128` \|” | A `tbb128` parameter is an `i128` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i128\b` |
| `ty0674` | 674 | row | “\| `tbb256` \|” | `tbb256` is 32 bytes with alignment 8; its valid range is symmetric, -(2^255-1) .. 2^255-1, and one step past either end is ERR. | `run:0` |
| `ty0674b` | 674 | row | “\| `tbb256` \| `i256` \|” | A `tbb256` parameter is an `i256` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i256\b` |
| `ty0680` | 680 | rule | “makes negation and absolute” | Negation is total on tbb: for the valid -127, `x * -1` and `-x` are 127, not ERR. | `run:0` |
| `ty0682` | 682 | rule | “`INT_MIN / -1` — which faults in hardware on x86 — cannot arise” | The hardware's INT_MIN / -1 cannot arise: ERR / -1 at tbb32 is ERR, with no trap and no fault. | `run:0` |
| `ty0687` | 687 | rule | “**Any operation on an ERR value yields ERR.**” | Any operation on ERR yields ERR, overriding identities: `ERR * 0` and `ERR - ERR` are ERR. | `run:0` (M10 `m13_tbb_err_sticky`) |
| `ty0690` | 690 | rule | “Overflow **saturates to ERR** rather than wrapping” | tbb overflow saturates to ERR rather than wrapping: 100 + 100 at tbb8 is ERR, not -56. | `run:0` |
| `ty0692` | 692 | rule | “Division or modulo by zero yields ERR (D-007).” | tbb division or modulo by zero yields ERR, with no trap. | `run:0` (M10 `v18_tbb_div_by_zero_is_err`) |
| `ty0693` | 693 | rule | “**Comparison or branching on ERR traps to `failsafe`**” | Comparing or branching on ERR traps to failsafe. | `run:110` (M10 `m12_tbb_compare_on_err_traps`) |
| `ty0695` | 695 | rule | “Use `is_err(x)` to test without” | `is_err(x)` tests a tbb for ERR without trapping, true for ERR and false for a value. | `run:0` |
| `ty0696` | 696 | rule | “trapping, or a `pick` with an explicit `ERR:` arm.” | A pick with an explicit `ERR:` arm takes ERR without trapping. | `run:0` (M10 `p13_tbb_err_arm_taken`) |
| `ty0697` | 697 | rule | “**Bitwise operators are rejected** on `tbb`” | `~` on a tbb is refused. | `refuse` |
| `ty0698` | 698 | rule | “or destroy it (`ERR & 0` is `0`)” | `&` on a tbb is refused. | `refuse` |
| `ty0699` | 699 | rule | “**Casts are never straight bit operations.**” | A tbb8 ERR cast to tbb32 is ERR: the sentinel maps across widths rather than sign-extending into a valid -128. | `run:0` |
| `ty0702` | 702 | rule | “**A cast OUT of the family traps on an ERR operand under BOTH spellings**” | `=>` out of tbb traps TbbErr on an ERR operand. | `trap:TbbErr` |
| `ty0702b` | 702 | rule | “**A cast OUT of the family traps on an ERR operand under BOTH spellings**” | `=>!` out of tbb traps TbbErr on an ERR operand: the bang acknowledges a value's loss, and ERR is not a value. | `trap:TbbErr` |
| `ty0705` | 705 | rule | “so `tbb64 =>” | `tbb64 => int8` is a compile error: the value is range-classified like any numeric pair. | `refuse` |
| `ty0706` | 706 | rule | “`tbb32 => uint32` are compile errors” | `tbb32 => uint32` is a compile error. | `refuse` |
| `ty0706b` | 706 | rule | “and take the bang” | With the bang, `tbb32 =>! uint32` and `tbb64 =>! int8` compile and convert an in-range value. | `run:0` |
| `ty0708` | 708 | rule | “`=>` traps on a value with no image (the sentinel bit pattern, or out of” | Entering tbb8 with `=>` traps on the sentinel's bit pattern: int8 -128 has no tbb8 image. | `run:42` |
| `ty0708b` | 708 | rule | “`=>` traps on a value with no image (the sentinel bit pattern, or out of” | Entering tbb8 with `=>` traps on an out-of-range value: int32 200 has no tbb8 image. | `run:42` |
| `ty0709` | 709 | rule | “and `=>!` saturates it to ERR” | Entering tbb8 with `=>!`, an out-of-range int32 (200) and the sentinel's int8 bit pattern (-128) are ERR, with no trap. | `run:0` |
| `ty0711` | 711 | rule | “Definite-assignment analysis rejects” | There is no implicit default: a read before any write is refused. | `refuse` (M10 `d02_read_unassigned`) |
| `ty0713` | 713 | rule | “so an ERR taint is cleared by `x = 5i32`” | Assignment replaces a value: an ERR binding assigned 5 holds 5, not ERR. | `run:0` |
| `ty0713b` | 713 | rule | “Assignment *replaces* a value” | A binding declared without a value may be written later, and arithmetic after it is ordinary. | `run:0` (M10 `d04_tbb_assign_replaces`) |
| `ty0715` | 715 | rule | “the `failsafe` signature” | tbb is used for the failsafe signature: a failsafe whose parameter is a tbb32 is accepted. | `run:0` |
| `ty0718` | 718 | rule | “**To the verifier (D-278” | The verifier models a twisted value as an unbounded Int in the carrier's range, ERR being its most negative value; `is_err(x)` is `(= x MIN)`; each operation is the emitter's saturate-to-ERR `ite`. | untestable [z3] the SMT model is what `npkg verify` gives z3; only the rows are written without it (below) |
| `ty0723` | 723 | rule | “trap the family has (`TbbErr` at a comparison or a cast out) is the” | A tbb comparison's TbbErr guard is an `err-exit` obligation: `npkc --obligations` writes an err-exit row for a function that compares a tbb32 parameter. | `sh:0` |
| `ty0725` | 725 | rule | “division has no row: a zero divisor is ERR” | A twisted division has no row: a function dividing two tbb32s has no div-zero or div-min row. | `sh:0` |
| `ty0736` | 736 | row | “\| `trit` \| base-3 \| −1, 0, 1 \|” | A trit holds -1, 0 and 1, and 1 + 1 is past its bound (ERR). | `run:0` |
| `ty0737` | 737 | row | “\| `tryte` \| base-3 \| 10 trits \|” | A tryte is 10 trits: `.len` is 10, its largest value is 29524 ((3^10-1)/2), and 29524 + 1 is ERR. | `run:0` |
| `ty0738` | 738 | row | “\| `nit` \| base-9 \| −4 … 4 \|” | A nit holds -4 .. 4: 4 and -4 are values, and 4 + 1 is ERR. | `run:0` |
| `ty0739` | 739 | row | “\| `nyte` \| base-9 \| 5 nits \|” | A nyte is 5 nits: `.len` is 5, its largest value is 29524 ((9^5-1)/2), and 29524 + 1 is ERR. | `run:0` |
| `ty0741` | 741 | rule | “`tryte` and `nyte` hold the SAME 59049 states” | tryte and nyte hold the same states: -29524 and 29524 are values of both. | `run:0` |
| `ty0751` | 751 | row | “\| `trit` \| `i8` \| 1 byte” | On the binary rung a `trit` is 1 byte with alignment 1. | `run:0` |
| `ty0751b` | 751 | row | “\| `trit` \| `i8` \|” | A `trit` parameter is an `i8` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i8\b` |
| `ty0752` | 752 | row | “\| `tryte` \| `i16` \| 2 byte” | On the binary rung a `tryte` is 2 bytes with alignment 2. | `run:0` |
| `ty0752b` | 752 | row | “\| `tryte` \| `i16` \|” | A `tryte` parameter is an `i16` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i16\b` |
| `ty0753` | 753 | row | “\| `nit` \| `i8` \| 1 byte” | On the binary rung a `nit` is 1 byte with alignment 1. | `run:0` |
| `ty0753b` | 753 | row | “\| `nit` \| `i8` \|” | A `nit` parameter is an `i8` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i8\b` |
| `ty0754` | 754 | row | “\| `nyte` \| `i16` \| 2 byte” | On the binary rung a `nyte` is 2 bytes with alignment 2. | `run:0` |
| `ty0754b` | 754 | row | “\| `nyte` \| `i16` \|” | A `nyte` parameter is an `i16` in the IR. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11t"?\(i16\b` |
| `ty0768` | 768 | rule | “ternary arithmetic is checked as **ternary** in the frontend” | Ternary arithmetic is checked as ternary in the frontend; nothing above the backend assumes `i8`. | untestable [internal] where a check runs inside the compiler is not observable; its results are (below) |
| `ty0777` | 777 | rule | “**The binary rung stores the VALUE**” | The binary rung stores a tryte's balanced value: the tryte 60 is the constant `i16 60` in the IR. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11v"?\((?=(?:(?!\n\}).)*?\bi16 60\b)` |
| `ty0779` | 779 | rule | “ERR sentinel is the carrier's most-negative (−128 / −32768)” | A tryte's ERR is the carrier's most negative value: a function passing ERR as a tryte emits `-32768`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11e"?\((?=(?:(?!\n\}).)*?-32768\b)` |
| `ty0780` | 780 | rule | “The prototype's packed-trit LUT emulation is deliberately NOT carried” | The packed-trit lookup-table emulation is not carried. | untestable [internal] an emulation's absence; ty0777 tests the stored value |
| `ty0786` | 786 | rule | “`+ - *` at all four types” | `+ - *` compute at trit, tryte, nit and nyte. | `run:0` |
| `ty0786b` | 786 | rule | “**`/ %` at `tryte`/`nyte` only**” | `/` and `%` compute at tryte and nyte: 100 / 7 is 14 and 100 % 7 is 2 (truncating). | `run:0` |
| `ty0787` | 787 | rule | “refused by name (TYPE-051)” | `/` at trit is refused, TYPE-051. | `refuse:NITPICK-TYPE-051` |
| `ty0787b` | 787 | rule | “refused by name (TYPE-051)” | `%` at nit is refused, TYPE-051. | `refuse:NITPICK-TYPE-051` |
| `ty0788` | 788 | rule | “**Overflow past the BALANCED bound → ERR**” | Overflow past the balanced bound is ERR at every width: nit 4 + 1, tryte 29524 * 2 and nyte -29524 - 1 are ERR. | `run:0` |
| `ty0789` | 789 | rule | “`trit` is ERR exactly as `MAX + 1` is at `tbb`” | 1 + 1 at trit is ERR (the prototype's clamp to 1 is overruled). | `run:0` |
| `ty0792` | 792 | rule | “Division by zero yields ERR (D-007's twisted row)” | Ternary division and modulo by zero yield ERR, with no trap. | `run:0` |
| `ty0792b` | 792 | rule | “comparisons at all four” | Comparisons work at all four ternary types in balanced (numeric) order. | `run:0` |
| `ty0794` | 794 | rule | “comparison traps; `is_err` looks” | An ERR operand at a bare ternary comparison traps TbbErr (the family's one trap, line 723). | `trap:TbbErr` |
| `ty0794b` | 794 | rule | “the `pick` `ERR:` arm handles” | A ternary pick's `ERR:` arm takes ERR. | `run:0` |
| `ty0795` | 795 | rule | “ternary `pick` selector demands that arm exactly as a `tbb`'s does” | A ternary pick selector without an `ERR:` arm is refused. | `refuse` |
| `ty0796` | 796 | rule | “on `trit`/`nit`, `&` is three-valued” | On trit, `&` is min and `\|` is max (Kleene), and NOT is `0 - x`. | `run:0` |
| `ty0796b` | 796 | rule | “on `trit`/`nit`, `&` is three-valued” | On nit, `&` is min and `\|` is max. | `run:0` |
| `ty0797` | 797 | rule | “ERR sticky” | The Kleene operators keep ERR: `1 & ERR` and `-1 \| ERR` at trit are ERR. | `run:0` |
| `ty0799` | 799 | rule | “the operators stay refused” | `&` on tryte is refused. | `refuse` |
| `ty0799b` | 799 | rule | “multi-digit types the operators stay refused” | `\|` on nyte is refused. | `refuse` |
| `ty0801` | 801 | rule | “**Digit access**: `t.trit(i)` / `n.nit(i)`” | `t.trit(i)` reads a tryte's balanced digits from the least significant (60 = 1T1T0: 0, -1, 1), and `n.nit(i)` a nyte's (100 = 121 nonary: 1, 2, 1). | `run:0` |
| `ty0802` | 802 | rule | “`tryte` has trits, not nits” | A tryte has trits, not nits: `t.nit(0)` on a tryte is refused. | `refuse` |
| `ty0803` | 803 | rule | “array's (OUT_OF_BOUNDS)” | A digit index past the digit count traps OutOfBounds: `t.trit(10)` on a tryte. | `trap:OutOfBounds` |
| `ty0803b` | 803 | rule | “an ERR receiver yields an ERR digit” | An ERR receiver yields an ERR digit. | `run:0` |
| `ty0803c` | 803 | rule | “`.len` is” | `.len` is the digit count as an int64: 10 for a tryte, 5 for a nyte, 1 for a trit or a nit. | `run:0` |
| `ty0805` | 805 | rule | “**Literals are contextual, any base**” | A ternary-typed slot takes an unsuffixed integer literal and a balanced-digit literal: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are one value spelled two ways. | `run:0` |
| `ty0808` | 808 | rule | “range-checked EXACTLY against the balanced bound” | A literal past the balanced bound is refused: `tryte:t = 29525;`. | `refuse` |
| `ty0808b` | 808 | rule | “range-checked EXACTLY against the balanced bound” | A literal past the balanced bound is refused: `trit:t = 2;`. | `refuse` |
| `ty0808c` | 808 | rule | “range-checked EXACTLY against the balanced bound” | A literal at the bound is accepted exactly: `tryte:t = 29524;` and `nit:n = -4` (as `0 - 4`) are values. | `run:0` |
| `ty0808d` | 808 | rule | “`ERR` takes the slot's” | `ERR` takes the slot's type: `nit:e = ERR;` is the nit ERR. | `run:0` |
| `ty0810` | 810 | rule | “one family within itself — value-preserving, the sentinel maps” | Within the ternary family a cast preserves the value and maps the sentinel: trit -1 => tryte is -1, and trit ERR => tryte is ERR. | `run:0` |
| `ty0811` | 811 | rule | “a smaller-bound target trap-or-saturates (`=>` / `=>!`)” | A cast to a smaller-bound ternary target traps under `=>` when the value does not fit (tryte 60 => trit). | `run:42` |
| `ty0811b` | 811 | rule | “a smaller-bound target trap-or-saturates (`=>` / `=>!`)” | A cast to a smaller-bound ternary target saturates to ERR under `=>!` (tryte 60 =>! trit), and a value that fits converts (tryte 1 =>! trit is 1). | `run:0` |
| `ty0812` | 812 | rule | “`tryte ⇄ nyte` (the same 59049 values) is a pure relabel” | tryte => nyte => tryte keeps every value: 29524 and -29524 survive. | `run:0` |
| `ty0813` | 813 | rule | “ERR traps under BOTH spellings” | Leaving the ternary family, ERR traps TbbErr under `=>`. | `trap:TbbErr` |
| `ty0813b` | 813 | rule | “ERR traps under BOTH spellings” | Leaving the ternary family, ERR traps TbbErr under `=>!`. | `trap:TbbErr` |
| `ty0814` | 814 | rule | “range-classified” | Leaving, the value is range-classified: `tryte => int8` is a compile error (29524 does not fit). | `refuse` |
| `ty0814b` | 814 | rule | “Entering: out-of-range traps under `=>`” | Entering the ternary family with `=>`, an out-of-range value traps: int32 30000 => tryte. | `run:42` |
| `ty0815` | 815 | rule | “under `=>!`.” | Entering the ternary family with `=>!`, an out-of-range value is ERR: int32 30000 =>! tryte. | `run:0` |
| `ty0815b` | 815 | rule | “Another twisted family (`tbb`, `tfp`, `dim256`) is reached” | Another twisted family is reached through the plain integer: (tryte => int32) => tbb32 converts. | `run:0` |
| `ty0816` | 816 | rule | “cross-family casts do not exist” | A direct cross-family cast is refused: tryte => tbb32. | `refuse` |
| `ty0816b` | 816 | rule | “cross-family casts do not exist” | A direct cross-family cast is refused under the bang too: tbb32 =>! nyte. | `refuse` |
| `ty0817` | 817 | rule | “**`ToString`** renders the VALUE” | ToString renders a ternary value as its number, and ERR as "ERR". | `run:0` |
| `ty0825` | 825 | rule | “`PROT_READ` where an `oflags` belongs” | Each flag family is a distinct type: `PROT_READ` where an `oflags` belongs is refused. | `refuse` |
| `ty0830` | 830 | rule | “Every family lowers to `i32`.” | Every flag family lowers to `i32`: a parameter of each of the four families is an `i32`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11o"?\(i32\b)(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11p"?\(i32\b)(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11m"?\(i32\b)(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11f"?\(i32\b)` |
| `ty0832` | 832 | rule | “`\|` combines, `&` tests, `~` complements” | Within one family `\|` combines, `&` tests and `~` complements, each giving that family; `==`/`!=` compare. | `run:0` |
| `ty0833` | 833 | rule | “There is no arithmetic” | There is no arithmetic on flags: `O_WRONLY + O_APPEND` is refused. | `refuse` |
| `ty0834` | 834 | rule | “ordering, no `^` and no shifts” | There is no ordering on flags: `O_WRONLY < O_APPEND` is refused. | `refuse` |
| `ty0834b` | 834 | rule | “ordering, no `^` and no shifts” | There is no `^` on flags. | `refuse` |
| `ty0834c` | 834 | rule | “ordering, no `^` and no shifts” | There are no shifts on flags: `O_WRONLY << 1` is refused. | `refuse` |
| `ty0835` | 835 | rule | “`oflags \| prot` refuses” | Two families never meet: `oflags \| prot` is refused, TYPE-058. | `refuse:NITPICK-TYPE-058` |
| `ty0836` | 836 | rule | “as does `O_RDONLY \| 1i32`” | An integer is not a member: `O_RDONLY \| 1i32` is refused, TYPE-058. | `refuse:NITPICK-TYPE-058` |
| `ty0838` | 838 | rule | “`flags => int32` is the one outbound conversion” | `flags => int32` converts losslessly: the word is the members' sum. | `run:0` |
| `ty0838b` | 838 | rule | “is the one outbound conversion” | `=> int32` is the only outbound conversion: `flags => int64` is refused. | `refuse` |
| `ty0840` | 840 | rule | “`int32 =>! flags` is the read-back direction” | `int32 =>! flags` reads a word back into the family. | `run:0` |
| `ty0841` | 841 | rule | “Nothing else enters or leaves” | Nothing else enters: `int64 =>! oflags` is refused. | `refuse` |
| `ty0841b` | 841 | rule | “so it takes the bang” | The read-back takes the bang: `int32 => flags` is refused. | `refuse` |
| `ty0842` | 842 | rule | “family never converts to another” | A family never converts to another: `oflags =>! prot` is refused. | `refuse` |
| `ty0844` | 844 | rule | “**Members.** The named bits are **prelude constants**, `pub fixed” | The members are `fixed` prelude constants: assigning to `O_APPEND` is refused. | `refuse` |
| `ty0846` | 846 | rule | “`src/prelude/prelude.npk`'s marked region from the table below by” | The members are generated into the prelude by `gen_tables.py`, with the family indices and the builtin-type table. | untestable [tree] how the compiler's tree generates its prelude |
| `ty0849` | 849 | rule | “authority; a member added here exists everywhere the prelude is bound” | A member exists in every module, since the prelude is bound in every module. | `run:0` |
| `ty0850` | 850 | rule | “A derived set is an ordinary module binding” | A derived set is an ordinary module binding that folds: `fixed oflags:CREATE_RW = (O_RDWR \| O_CREAT) \| O_CLOEXEC;` is the word 524354. | `run:0` |
| `ty0853` | 853 | rule | “The four that are bitmasks by nature” | There are four flag families: oflags, prot, mflags and fmode. | untestable [unobservable] that no fifth family exists; each of the four is tested (ty0830) |
| `ty0854` | 854 | rule | “`whence` is the prelude enum `Whence`” | `whence` is the prelude enum `Whence`: `Whence.SEEK_END` is a value a pick can match. | `run:0` |
| `ty0855` | 855 | rule | “OR-ed — a flags type would admit `SEEK_SET \| SEEK_END`” | A `Whence` is exactly one value: `Whence.SEEK_SET \| Whence.SEEK_END` is refused. | `refuse` |
| `ty0855b` | 855 | rule | “`fcmd`/`advice`” | `fcmd` and `advice` are enumerations, not flag types. | untestable [vague] the text names no member of either, so no program can spell one |
| `ty0857` | 857 | rule | “The family INDEX is the type's `a` operand” | The family index is the type's `a` operand, in the table's order of first appearance. | untestable [internal] a type's operand window |
| `ty0864` | 864 | row | “\| `oflags` \| `O_RDONLY` \| 0 \|” | `O_RDONLY` is a `oflags` member whose word is 0. | `run:0` |
| `ty0864b` | 864 | row | “so `f & O_RDONLY == O_RDONLY` always” | `O_RDONLY` is the empty set: `f & O_RDONLY == O_RDONLY` for any f. | `run:0` |
| `ty0865` | 865 | row | “\| `oflags` \| `O_WRONLY` \| 1 \|” | `O_WRONLY` is a `oflags` member whose word is 1. | `run:0` |
| `ty0866` | 866 | row | “\| `oflags` \| `O_RDWR` \| 2 \|” | `O_RDWR` is a `oflags` member whose word is 2. | `run:0` |
| `ty0867` | 867 | row | “\| `oflags` \| `O_CREAT` \| 64 \|” | `O_CREAT` is a `oflags` member whose word is 64. | `run:0` |
| `ty0868` | 868 | row | “\| `oflags` \| `O_EXCL` \| 128 \|” | `O_EXCL` is a `oflags` member whose word is 128. | `run:0` |
| `ty0869` | 869 | row | “\| `oflags` \| `O_NOCTTY` \| 256 \|” | `O_NOCTTY` is a `oflags` member whose word is 256. | `run:0` |
| `ty0870` | 870 | row | “\| `oflags` \| `O_TRUNC` \| 512 \|” | `O_TRUNC` is a `oflags` member whose word is 512. | `run:0` |
| `ty0871` | 871 | row | “\| `oflags` \| `O_APPEND` \| 1024 \|” | `O_APPEND` is a `oflags` member whose word is 1024. | `run:0` |
| `ty0872` | 872 | row | “\| `oflags` \| `O_NONBLOCK` \| 2048 \|” | `O_NONBLOCK` is a `oflags` member whose word is 2048. | `run:0` |
| `ty0873` | 873 | row | “\| `oflags` \| `O_DSYNC` \| 4096 \|” | `O_DSYNC` is a `oflags` member whose word is 4096. | `run:0` |
| `ty0874` | 874 | row | “\| `oflags` \| `O_DIRECTORY` \| 65536 \|” | `O_DIRECTORY` is a `oflags` member whose word is 65536. | `run:0` |
| `ty0875` | 875 | row | “\| `oflags` \| `O_NOFOLLOW` \| 131072 \|” | `O_NOFOLLOW` is a `oflags` member whose word is 131072. | `run:0` |
| `ty0876` | 876 | row | “\| `oflags` \| `O_CLOEXEC` \| 524288 \|” | `O_CLOEXEC` is a `oflags` member whose word is 524288. | `run:0` |
| `ty0877` | 877 | row | “\| `oflags` \| `O_SYNC` \| 1052672 \|” | `O_SYNC` is a `oflags` member whose word is 1052672. | `run:0` |
| `ty0878` | 878 | row | “\| `oflags` \| `O_PATH` \| 2097152 \|” | `O_PATH` is a `oflags` member whose word is 2097152. | `run:0` |
| `ty0879` | 879 | row | “\| `prot` \| `PROT_NONE` \| 0 \|” | `PROT_NONE` is a `prot` member whose word is 0. | `run:0` |
| `ty0880` | 880 | row | “\| `prot` \| `PROT_READ` \| 1 \|” | `PROT_READ` is a `prot` member whose word is 1. | `run:0` |
| `ty0881` | 881 | row | “\| `prot` \| `PROT_WRITE` \| 2 \|” | `PROT_WRITE` is a `prot` member whose word is 2. | `run:0` |
| `ty0882` | 882 | row | “\| `prot` \| `PROT_EXEC` \| 4 \|” | `PROT_EXEC` is a `prot` member whose word is 4. | `run:0` |
| `ty0883` | 883 | row | “\| `mflags` \| `MAP_SHARED` \| 1 \|” | `MAP_SHARED` is a `mflags` member whose word is 1. | `run:0` |
| `ty0884` | 884 | row | “\| `mflags` \| `MAP_PRIVATE` \| 2 \|” | `MAP_PRIVATE` is a `mflags` member whose word is 2. | `run:0` |
| `ty0885` | 885 | row | “\| `mflags` \| `MAP_FIXED` \| 16 \|” | `MAP_FIXED` is a `mflags` member whose word is 16. | `run:0` |
| `ty0886` | 886 | row | “\| `mflags` \| `MAP_ANONYMOUS` \| 32 \|” | `MAP_ANONYMOUS` is a `mflags` member whose word is 32. | `run:0` |
| `ty0887` | 887 | row | “\| `mflags` \| `MAP_NORESERVE` \| 16384 \|” | `MAP_NORESERVE` is a `mflags` member whose word is 16384. | `run:0` |
| `ty0888` | 888 | row | “\| `mflags` \| `MAP_POPULATE` \| 32768 \|” | `MAP_POPULATE` is a `mflags` member whose word is 32768. | `run:0` |
| `ty0889` | 889 | row | “\| `mflags` \| `MAP_FIXED_NOREPLACE` \| 1048576 \|” | `MAP_FIXED_NOREPLACE` is a `mflags` member whose word is 1048576. | `run:0` |
| `ty0890` | 890 | row | “\| `fmode` \| `S_NONE` \| 0 \|” | `S_NONE` is a `fmode` member whose word is 0. | `run:0` |
| `ty0891` | 891 | row | “\| `fmode` \| `S_IXOTH` \| 1 \|” | `S_IXOTH` is a `fmode` member whose word is 1. | `run:0` |
| `ty0892` | 892 | row | “\| `fmode` \| `S_IWOTH` \| 2 \|” | `S_IWOTH` is a `fmode` member whose word is 2. | `run:0` |
| `ty0893` | 893 | row | “\| `fmode` \| `S_IROTH` \| 4 \|” | `S_IROTH` is a `fmode` member whose word is 4. | `run:0` |
| `ty0894` | 894 | row | “\| `fmode` \| `S_IRWXO` \| 7 \|” | `S_IRWXO` is a `fmode` member whose word is 7. | `run:0` |
| `ty0894b` | 894 | row | “\| `fmode` \| `S_IRWXO` \| 7 \| others: all three \|” | S_IRWXO is S_IROTH \| S_IWOTH \| S_IXOTH; S_IRWXU likewise for the owner. | `run:0` |
| `ty0895` | 895 | row | “\| `fmode` \| `S_IXGRP` \| 8 \|” | `S_IXGRP` is a `fmode` member whose word is 8. | `run:0` |
| `ty0896` | 896 | row | “\| `fmode` \| `S_IWGRP` \| 16 \|” | `S_IWGRP` is a `fmode` member whose word is 16. | `run:0` |
| `ty0897` | 897 | row | “\| `fmode` \| `S_IRGRP` \| 32 \|” | `S_IRGRP` is a `fmode` member whose word is 32. | `run:0` |
| `ty0898` | 898 | row | “\| `fmode` \| `S_IRWXG` \| 56 \|” | `S_IRWXG` is a `fmode` member whose word is 56. | `run:0` |
| `ty0899` | 899 | row | “\| `fmode` \| `S_IXUSR` \| 64 \|” | `S_IXUSR` is a `fmode` member whose word is 64. | `run:0` |
| `ty0900` | 900 | row | “\| `fmode` \| `S_IWUSR` \| 128 \|” | `S_IWUSR` is a `fmode` member whose word is 128. | `run:0` |
| `ty0901` | 901 | row | “\| `fmode` \| `S_IRUSR` \| 256 \|” | `S_IRUSR` is a `fmode` member whose word is 256. | `run:0` |
| `ty0902` | 902 | row | “\| `fmode` \| `S_IRWXU` \| 448 \|” | `S_IRWXU` is a `fmode` member whose word is 448. | `run:0` |
| `ty0903` | 903 | row | “\| `fmode` \| `S_ISVTX` \| 512 \|” | `S_ISVTX` is a `fmode` member whose word is 512. | `run:0` |
| `ty0904` | 904 | row | “\| `fmode` \| `S_ISGID` \| 1024 \|” | `S_ISGID` is a `fmode` member whose word is 1024. | `run:0` |
| `ty0905` | 905 | row | “\| `fmode` \| `S_ISUID` \| 2048 \|” | `S_ISUID` is a `fmode` member whose word is 2048. | `run:0` |
| `ty0909` | 909 | rule | “The lowering is pinned in `tests/backend/ir_types.npk`” | The lowering, the rules and the executed semantics are pinned by three named tests of the compiler's tree. | untestable [tree] the compiler's own tests |
| `ty0921` | 921 | example | “```nitpick” | The struct example compiles as written. | `compile` |
| `ty0925` | 925 | example | “```llvm” | MyStruct is laid out with C padding: 24 bytes, alignment 8. | `run:0` |
| `ty0926` | 926 | rule | “%MyStruct = type { i32, i64, i8 }” | MyStruct's LLVM type is `{ i32, i64, i8 }`. | `ir:(?m)^%"?[^"\n]*MyStruct"? = type \{ i32, i64, i8 \}` |
| `ty0936` | 936 | example | “```llvm” | Reading `obj.y` is a `getelementptr` to field index 1 and an `i64` load. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11gy"?\((?=(?:(?!\n\}).)*?getelementptr[^\n]*, i32 0, i32 1\b)(?=(?:(?!\n\}).)*?load i64)` |
| `ty0946` | 946 | rule | “A generic struct's qualifiers, and its module, are its” | A generic struct's qualifiers are its template's: a sealed `T` field of `Box<int64>` is refused a write from outside, TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0949` | 949 | example | “```nitpick” | The `bank` example compiles. | `compile` |
| `ty0952` | 952 | rule | “read anywhere; written only inside `bank`” | A sealed field is read outside its module and written inside it: `a.bal` reads 5, and after `bank.deposit(@a, 3)` reads 8. | `run:0` |
| `ty0953` | 953 | rule | “neither read nor written outside `bank`” | A hidden field is not read outside its module: TYPE-080. | `refuse:NITPICK-TYPE-080` |
| `ty0954` | 954 | rule | “int64:note;           // anyone” | An unqualified field is written and read by anyone. | `run:0` |
| `ty0960` | 960 | rule | “refuses every WRITE from outside, `NITPICK-TYPE-079`” | A sealed field's assignment from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0962` | 962 | rule | “including a part of a sealed value” | Writing a part of a sealed value (`h.inner.x`) from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0963` | 963 | rule | “a sealed field reached through a pointer” | Writing a sealed field through a pointer from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0964` | 964 | rule | “a compound assignment;” | A compound assignment to a sealed field from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0965` | 965 | rule | “a struct literal naming the field;” | A struct literal naming a sealed field outside its module is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0966` | 966 | rule | “a `move` or `pass` out of an OWNING sealed field” | A move out of an owning sealed field from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0968` | 968 | rule | “`@` and `$$m`;” | Taking `@` of a sealed field from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0968b` | 968 | rule | “`@` and `$$m`;” | Claiming a sealed field `$$m` from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0969` | 969 | rule | “a call through a `Self->` receiver;” | A call through a `Self->` receiver on a sealed field from outside is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0970` | 970 | rule | “any operation on a stateful value, which writes through its address” | Any operation on a stateful sealed value is a write. | untestable [vague] which values are stateful, and which operations, is not named here |
| `ty0973` | 973 | rule | “A read, a copy out, a `$$i` claim (D-286 holds it read-only)” | A read, a copy out and a `$$i` claim of a sealed field pass outside its module. | `run:0` |
| `ty0974` | 974 | rule | “THROUGH a sealed pointer field all pass” | A write through a sealed pointer field passes outside its module: it writes the pointee. | `run:0` |
| `ty0976` | 976 | rule | “refuses every touch from outside, read or write” | Writing a hidden field from outside is TYPE-080. | `refuse:NITPICK-TYPE-080` |
| `ty0977` | 977 | rule | “a struct literal naming” | A struct literal naming a hidden field outside its module is TYPE-080. | `refuse:NITPICK-TYPE-080` |
| `ty0978` | 978 | rule | “it, a struct pattern binding it” | A struct pattern binding a hidden field outside its module is TYPE-080. | `refuse:NITPICK-TYPE-080` |
| `ty0978b` | 978 | rule | “it, a struct pattern binding it” | A struct pattern binding an unqualified field outside its module is accepted (the twin of ty0978). | `run:0` |
| `ty0980` | 980 | rule | “On a local, a parameter, a module binding or” | `sealed` on a local is TYPE-081. | `refuse:NITPICK-TYPE-081` |
| `ty0980b` | 980 | rule | “On a local, a parameter, a module binding or” | `hidden` on a parameter is TYPE-081. | `refuse:NITPICK-TYPE-081` |
| `ty0981` | 981 | rule | “a cast target, or both on one field, the qualifier is `NITPICK-TYPE-081`” | `sealed` and `hidden` both on one field is TYPE-081. | `refuse:NITPICK-TYPE-081` |
| `ty0982` | 982 | rule | “`for` binding takes no qualifier at all” | A `for` binding takes no qualifier: `for (sealed int64:i in …)` is refused. | `refuse` |
| `ty0984` | 984 | rule | “`ptr`, `len` and `cap` of a `string`, a `cstring`, a slice and a `buffer`” | A string's `len` is sealed in every module: `s.len = s.len` is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0984b` | 984 | rule | “`ptr`, `len` and `cap` of a `string`, a `cstring`, a slice and a `buffer`” | A slice's `len` is sealed in every module: writing it is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0987` | 987 | rule | “An `OwnedFd`'s `.value`, the descriptor its drop closes.” | An OwnedFd's `.value` is sealed in every module: writing it is TYPE-079. | `refuse:NITPICK-TYPE-079` |
| `ty0993` | 993 | rule | “**An `RGuard`'s `.value` is read-only at every write form**” | An RGuard's `.value` is read-only: assigning it is TYPE-007. | `refuse:NITPICK-TYPE-007` |
| `ty1002` | 1002 | example | “```” | The limited-field example compiles. | `compile` |
| `ty1012` | 1012 | rule | “Struct-wide relational rules (`$.count <= $.cap`) are decided” | Struct-wide relational field rules are decided out. | untestable [vague] a decision against a feature; the subject rule (ty1017) is what refuses one |
| `ty1017` | 1017 | rule | “**The subject is the field's type by identity**” | A field rule's subject is the field's type by identity: a `Rules<int32>` on an int64 field is TYPE-059. | `refuse:NITPICK-TYPE-059` |
| `ty1019` | 1019 | rule | “limited field of a generic struct's `T` refuses” | A limited field of a generic struct's `T` is refused (TYPE-059). | `refuse:NITPICK-TYPE-059` |
| `ty1020` | 1020 | rule | “**The rule must hold of the field's VACANT value** (`NITPICK-TYPE-077`)” | A field rule that its vacant value (0) breaks is TYPE-077. | `refuse:NITPICK-TYPE-077` |
| `ty1024` | 1024 | rule | “the rule at the declaration with `$` bound to it — 0 for a plain integer,” | A bool field's vacant value is false: a rule `$ == true` on it is TYPE-077. | `refuse:NITPICK-TYPE-077` |
| `ty1025` | 1025 | rule | “a rule it cannot decide there is refused too” | A field rule the folder cannot decide at the declaration is refused. | untestable [vague] what the folder cannot decide is not stated |
| `ty1026` | 1026 | rule | “Only a plain integer, a `bool` or a `char`” | A field rule on another subject (flt64) is refused with the vacant-value reason, TYPE-077. | `refuse:NITPICK-TYPE-077` |
| `ty1029` | 1029 | rule | “**The write points**, each checked after the write in EVERY build” | In-range writes at every write point pass: a literal of 5, an assignment of 50, a write of 60 through a pointer and `+= 40`. | `run:0` |
| `ty1031` | 1031 | rule | “a struct literal's value for the field;” | A struct literal's out-of-rule value for a limited field traps LimitViolated. | `trap:LimitViolated` |
| `ty1032` | 1032 | rule | “an assignment to the field through ANY path” | An assignment of an out-of-rule value to a limited field traps LimitViolated. | `trap:LimitViolated` |
| `ty1033` | 1033 | rule | “pointer `p.f = v`, since the rule is the field's wherever its struct lives” | An out-of-rule write through a pointer to the struct traps LimitViolated. | `trap:LimitViolated` |
| `ty1034` | 1034 | rule | “a compound assignment, `s.f += v`.” | A compound assignment that leaves the rule traps LimitViolated. | `trap:LimitViolated` |
| `ty1035` | 1035 | rule | “**A limited field has no address** (`NITPICK-TYPE-063`” | `@s.f` of a limited field is TYPE-063. | `refuse:NITPICK-TYPE-063` |
| `ty1036` | 1036 | rule | “`@s.f`, `$$i`/`$$m` of it” | `$$m` of a limited field is TYPE-063. | `refuse:NITPICK-TYPE-063` |
| `ty1036b` | 1036 | rule | “`@s.f`, `$$i`/`$$m` of it” | `$$i` of a limited field is TYPE-063. | `refuse:NITPICK-TYPE-063` |
| `ty1037` | 1037 | rule | “through a pointer to the struct as well” | `@p.f` of a limited field through a pointer to its struct is TYPE-063. | `refuse:NITPICK-TYPE-063` |
| `ty1038` | 1038 | rule | “A write through `wild` storage is the author's” | A write through wild storage is unchecked. | untestable [unobservable] an opt-out promises nothing a program could check |
| `ty1040` | 1040 | rule | “**Every read is a fact**” | Every read of a limited field is a hypothesis for the rows after it. | untestable [z3] a hypothesis matters only to the solver's verdicts |
| `ty1045` | 1045 | rule | “The verified build elides a write point's check where its `limit` row” | The verified build elides a write point's check where its limit row discharges. | untestable [z3] needs `npkg verify` with the pinned z3 |
| `ty1050` | 1050 | rule | “Passing `int32[4]` to a function copies all 16 bytes” | Passing a fixed array copies it. | `run:0` (M10 `a02_array_argument_copies`) |
| `ty1050b` | 1050 | rule | “Fixed arrays are **Value Types**, not references” | Assigning a fixed array copies it. | `run:0` (M10 `a01_array_assignment_copies`) |
| `ty1050c` | 1050 | rule | “explicitly pass a pointer to it (`int32[4]->`)” | A write through an `int32[4]->` reaches the caller's array. | `run:0` (M10 `a06_write_through_array_pointer`) |
| `ty1050d` | 1050 | rule | “They do NOT implicitly decay to pointers like in C” | A fixed array does not decay to a pointer: passing `int32[4]` where `int32->` is expected is refused. | `refuse` |
| `ty1052` | 1052 | example | “```nitpick” | `int32[4]:arr = [1i32, 2i32, 3i32, 4i32];` holds 1, 2, 3, 4. | `run:0` |
| `ty1056` | 1056 | example | “```llvm” | A local `int32[4]` is an `alloca [4 x i32]`, and an index is checked `icmp ult i64 %idx, 4` before a `getelementptr [4 x i32]`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11ix"?\((?=(?:(?!\n\}).)*?alloca \[4 x i32\])(?=(?:(?!\n\}).)*?icmp ult i64 %[^,\n]+, 4\b)(?=(?:(?!\n\}).)*?getelementptr[^\n]*\[4 x i32\])` |
| `ty1058` | 1058 | rule | “; Element access (bounds-checked):” | An index past the end traps OutOfBounds. | `run:94` (M10 `a03_index_past_end`) |
| `ty1061` | 1061 | rule | “%in_bounds = icmp ult i64 %idx, 4” | A negative index traps OutOfBounds (the unsigned compare). | `run:94` (M10 `a04_index_negative`) |
| `ty1068` | 1068 | rule | “**A zero-length fixed array `T[0]` is a supported type**” | `T[0]` is accepted and zero bytes wide: a struct holding only an `int64[0]` is 0 bytes. | `run:0` |
| `ty1070` | 1070 | rule | “OWNING when `T` owns” | A struct with a `hidden string[0]` field is move-only: copying it is TYPE-046. | `refuse:NITPICK-TYPE-046` |
| `ty1072` | 1072 | rule | “while `int64[0]` copies freely” | A struct with an `int64[0]` field copies freely. | `run:0` |
| `ty1075` | 1075 | rule | “`arr.len` is the count the type carries” | `arr.len` is the array's count. | `run:0` (M10 `a05_array_len`) |
| `ty1077` | 1077 | rule | “a local `uint8[20]` asking its length” | A local `uint8[20]` asking its length compiles, and the length is 20. | `run:0` |
| `ty1084` | 1084 | example | “```llvm” | A slice is `{ ptr, i64 }`: an `int32[]` parameter has that type. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11sl"?\(\{ ?ptr, i64 ?\}\b` |
| `ty1088` | 1088 | rule | “**Indexing is bounds-checked against the runtime `len`**” | A slice index past its own len traps OutOfBounds. | `run:94` (M10 `a09_view_index_past_its_len`) |
| `ty1088b` | 1088 | rule | “**Indexing is bounds-checked against the runtime `len`**” | A byte view's index past its len traps OutOfBounds. | `run:94` (M10 `t07_bytes_view_bounds`) |
| `ty1092` | 1092 | rule | “**`.len`** is available on every slice.” | `.len` is available on every slice: a range of an array and a range of a slice. | `run:0` |
| `ty1093` | 1093 | rule | “**Every built-in length lies in `[0, 2^47]`, and the verifier knows it**” | Every built-in length lies in [0, 2^47], and the verifier pushes the fact at every read. | untestable [z3] the fact matters to the solver's verdicts; the guard below is tested |
| `ty1099` | 1099 | rule | “2^47`, one unsigned compare, trapping `OutOfBounds` outside it” | `#wild_slice` guards the caller's count: a negative count traps OutOfBounds. | `trap:OutOfBounds` |
| `ty1102` | 1102 | rule | “`s.len + 1` cannot overflow an `int64` and its row discharges” | `s.len + 1`'s overflow row discharges. | untestable [z3] a discharge is z3's verdict |
| `ty1103` | 1103 | rule | “The prelude's `List` carries the same bound as a” | A program that pushes to a List reaches the prelude's `limit<ListLen>` writes, so its failsafe must name LimitViolated: one that does not is refused. | `refuse` |
| `ty1103b` | 1103 | rule | “The prelude's `List` carries the same bound as a” | A program that pushes to a List, with a failsafe naming LimitViolated, compiles and runs. | `run:0` |
| `ty1107` | 1107 | rule | “**A slice is a second-class borrow** (D-004)” | A slice never passes up the call stack: a function returning a slice is refused. | `refuse` |
| `ty1111` | 1111 | rule | “Constructed by ranging a fixed array or another slice” | Ranging a fixed array makes a slice of it. | `run:0` (M10 `a08_range_view`) |
| `ty1112` | 1112 | rule | “`wild` context only, from a raw pointer and a length with” | `#wild_slice` is for wild context only: outside one it is refused. | `refuse` |
| `ty1117` | 1117 | rule | “`T[]` **never owns**” | A slice never owns its elements. | untestable [unobservable] a view's not-owning shows only as the absence of a free |
| `ty1119` | 1119 | rule | “A slice does not cross an `extern` boundary as a view” | A byte-slice parameter of an extern block is a sized payload the Bridge copies. | untestable [tool] needs a driver behind an extern block |
| `ty1126` | 1126 | example | “```nitpick” | `Color`'s variants are the i32 tags 0, 1, 2. | `run:0` |
| `ty1130` | 1130 | example | “```llvm” | Enum values are plain i32 constants: a `Color` parameter is an `i32`. | `ir:(?m)^define [^@\n]*@"?(?:[\w$]+\.)*m11c"?\(i32\b` |
| `ty1136` | 1136 | rule | “%Shape = type { i32, [2 x i64] }” | Shape is a tag and a two-i64 payload slot: 24 bytes, alignment 8. | `run:0` |
| `ty1136b` | 1136 | rule | “%Shape = type { i32, [2 x i64] }” | Shape's LLVM type is `{ i32, [2 x i64] }`. | `ir:(?m)^%"?[^"\n]*Shape"? = type \{ i32, \[2 x i64\] \}` |
| `ty1137` | 1137 | rule | “payload's alignment in bits, N covering the widest size” | The payload slot is [N x iK], K the widest payload's alignment in bits: for payloads int8 and (int32, int32) it is `[2 x i32]`. | `ir:(?m)^%"?[^"\n]*Ev"? = type \{ i32, \[2 x i32\] \}` |
| `ty1140` | 1140 | rule | “`enum =>! intN` reads the TAG (slot 0) at every shape” | `enum =>! intN` reads the tag. | `run:0` (M10 `c17_enum_to_int_reads_tag`) |
| `ty1140b` | 1140 | rule | “`enum =>! intN` reads the TAG (slot 0) at every shape” | `enum =>! intN` reads the tag of a payload-carrying enum: Shape.Rect is 1, Shape.Circle 0. | `run:0` |
| `ty1142` | 1142 | rule | “`intN =>! enum`, which manufactures a tag” | A tag-only enum takes `intN =>! enum`: 2 =>! Color is Blue. | `run:0` |
| `ty1142b` | 1142 | rule | “hence the bang; `=>`” | `intN => enum` without the bang is TYPE-009. | `refuse:NITPICK-TYPE-009` |
| `ty1143` | 1143 | rule | “a PAYLOAD-CARRYING enum like this `Shape` admits neither” | A payload-carrying enum admits no `intN =>! enum`: TYPE-032. | `refuse:NITPICK-TYPE-032` |
| `ty1144` | 1144 | rule | “spelling (TYPE-032)” | A payload-carrying enum admits no `intN => enum` either: TYPE-032. | `refuse:NITPICK-TYPE-032` |
| `ty1150` | 1150 | rule | “`enum:Opt<T> = { Some(T); None; };` is a template” | A generic enum is a template: `Opt<int32>` and `Opt<string>` are instances, constructed and matched. | `run:0` |
| `ty1152` | 1152 | rule | “header (`%"…Opt<int32>" = type { i32, [1 x i32] }`)” | `Opt<int32>` has its own header `{ i32, [1 x i32] }`. | `ir:(?m)^%"[^"\n]*Opt<int32>" = type \{ i32, \[1 x i32\] \}` |
| `ty1153` | 1153 | rule | “`Opt<int32>` is a tag” | `Opt<int32>` is a tag and four bytes: 8 bytes, alignment 4. | `run:0` |
| `ty1153b` | 1153 | rule | “`Opt<string>` owns and drops its payload” | `Opt<string>` owns its payload: copying one is refused. | `refuse` |
| `ty1153c` | 1153 | rule | “`Opt<int32>` is a tag” | `Opt<int32>` copies freely (the twin of ty1153b). | `run:0` |
| `ty1159` | 1159 | rule | “**The instance of a constructor or a bare variant reference**” | A constructor's instance is the expected type: `Opt.None` and `Opt.Some(5i64)` passed to an `Opt<int64>` parameter compile and match. | `run:0` |
| `ty1162` | 1162 | rule | “else INFERRED from the payload arguments” | With no expected type, the instance is inferred from the payload: `Opt.Some(5i64)` is an `Opt<int64>`. | `run:0` |
| `ty1164` | 1164 | rule | “type from context, an unsuffixed literal say, teaches nothing” | An unsuffixed literal teaches nothing: `Opt.Some(5)` with no expected type is TYPE-022. | `refuse:NITPICK-TYPE-022` |
| `ty1165` | 1165 | rule | “else refused: `NITPICK-TYPE-022` naming the parameter” | A payload-less variant with no expected type is TYPE-022. | `refuse:NITPICK-TYPE-022` |
| `ty1167` | 1167 | rule | “`Opt<int32>:o = Opt.None;`” | A payload-less variant takes its instance from the annotation: `Opt<int32>:o = Opt.None;`. | `run:0` |
| `ty1169` | 1169 | rule | “`Opt<Point>` under `enum:Opt<T: Pr>` is” | An inferred instance is judged as an annotated one: `Opt.Some(Point{…})` under `enum:Opt<T: Pr>` where Point lacks Pr is TYPE-017. | `refuse:NITPICK-TYPE-017` |
| `ty1170` | 1170 | rule | “In pattern position a bare variant is read” | In pattern position a bare variant is read against the selector: `(Opt.None)` matches an `Opt<string>` with no annotation. | `run:0` |
| `ty1171` | 1171 | rule | “A non-generic enum binds an” | A non-generic enum binds an empty window, unchanged. | untestable [internal] a type's operand window |
| `ty1181` | 1181 | row | “\| `T->` \| `ptr` \| Pointer to T \|” | `T->` is an opaque `ptr`: an `int32->` parameter is `ptr`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11p"?\(ptr(?=[\s,)]))` |
| `ty1182` | 1182 | row | “\| `any->` \| `ptr` \| Type-erased pointer \|” | `any->` is an opaque `ptr`: an `any->` parameter is `ptr`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11a"?\(ptr(?=[\s,)]))` |
| `ty1184` | 1184 | rule | “The C-style `*` pointer syntax (e.g. `void*`, `char*`) is **forbidden everywhere**” | The C-style `*` pointer syntax is refused: `int32*:p = @x;`. | `refuse` |
| `ty1185` | 1185 | rule | “`@var` = address of” | `@var` takes an address, `<-ptr` dereferences (read and write), and `ptr.field` reaches a field through a pointer. | `run:0` |
| `ty1189` | 1189 | rule | “All pointers are **thin** — a single machine word” | A pointer is one machine word: `int32->` is 8 bytes with alignment 8. | `run:0` |
| `ty1190` | 1190 | rule | “The distinction between wild and” | Wild and borrow pointers lower alike: a `wild int64->` parameter and an `int64->` one are both `ptr`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11w"?\(ptr(?=[\s,)]))(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11b"?\(ptr(?=[\s,)]))` |
| `ty1194` | 1194 | rule | “claims `int8->` is a *fat* pointer carrying bounds” | `int8->` is not fat (the draft's claim is struck): an `int8->` parameter is one `ptr`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11i"?\(ptr(?=[\s,)]))` |
| `ty1200` | 1200 | rule | “`--guard-pages` remains available” | `--guard-pages` is available: npkc accepts it on an ordinary program. | `sh:0` |
| `ty1203` | 1203 | rule | “**Indexing a pointer** (`p[i]`) is the i-th `T` in memory from `p`” | Indexing a pointer to a scalar is the i-th element from it: `p[2]` from `@arr[0]` is arr[2]. | `run:0` |
| `ty1205` | 1205 | rule | “where the pointee is itself indexed** (1.5.8b step 1b, `NITPICK-TYPE-082`)” | Indexing a pointer to an array is TYPE-082. | `refuse:NITPICK-TYPE-082` |
| `ty1206` | 1206 | rule | “That covers an array (`int64[8]->`), a slice (`T[]->`) and a `List<T>->`” | Indexing a pointer to a slice is TYPE-082. | `refuse:NITPICK-TYPE-082` |
| `ty1206b` | 1206 | rule | “That covers an array (`int64[8]->`), a slice (`T[]->`) and a `List<T>->`” | Indexing a pointer to a List is TYPE-082. | `refuse:NITPICK-TYPE-082` |
| `ty1210` | 1210 | rule | “Here the element is spelled `(<-p)[i]`” | The pointee's element is spelled `(<-p)[i]`. | `run:0` |
| `ty1211` | 1211 | rule | “pointer to a scalar or a struct keeps its indexing” | A pointer to a struct keeps its indexing: `q[1].f` from `@sa[0]` is sa[1].f. | `run:0` |
| `ty1219` | 1219 | example | “```llvm” | `int32?` is 8 bytes with alignment 4 (an i8 tag padded before an i32). | `run:0` |
| `ty1222` | 1222 | rule | “%Optional_i32 = type { i8, i32 }” | `int32?` is `{ i8, i32 }`: an `int32?` parameter has that type. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11o"?\(\{ ?i8, i32 ?\}(?=[\s,)]))` |
| `ty1228` | 1228 | rule | “the value half is ZEROED, never undef” | An empty Optional is `zeroinitializer`, never `undef`: a function passing `NIL` as an `int32?` emits `zeroinitializer` and no `undef`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11n"?\((?=(?:(?!\n\}).)*?zeroinitializer)(?!(?:(?!\n\}).)*?\bundef\b)` |
| `ty1229` | 1229 | rule | “; int32?:b = 42i32;  = { i8 1, i32 42 }” | `int32?:b = 42i32;` holds 42. | `run:0` |
| `ty1237` | 1237 | rule | “`== NIL`/`!= NIL` is a tag” | `== NIL` and `!= NIL` test the tag in either operand order. | `run:0` |
| `ty1238` | 1238 | rule | “`??` evaluates its default only on the empty” | `??` evaluates its default only when the Optional is empty. | `run:0` (M10 `x06_optional_default_lazy`) |
| `ty1239` | 1239 | rule | “`?.` yields `zeroinitializer` of the result type when empty” | `?.` on an empty Optional yields an empty result. | `run:0` (M10 `d15_safe_navigation_on_empty`) |
| `ty1240` | 1240 | rule | “the field when present” | `?.` wraps the field when present: `s?.f` over a holding `S?` is the field, wrapped. | `run:0` |
| `ty1245` | 1245 | rule | “**There is no constructor, and none is needed (D-099).**” | An Optional is built by writing the value and emptied by writing NIL. | `run:0` |
| `ty1252` | 1252 | row | “\| `int32?:a = NIL;` \| empty \|” | `NIL` is the empty Optional and a value the holding one. | `run:0` (M10 `d09_optional_nil_and_value`) |
| `ty1253` | 1253 | row | “\| `int32?:b = 42i32;` \| holding `42i32` \|” | `int32?:b = 42i32;` holds 42i32. | `run:0` |
| `ty1254` | 1254 | row | “\| `a == NIL`, `a != NIL` \| the test \|” | `a == NIL` and `a != NIL` test an Optional. | `run:0` |
| `ty1255` | 1255 | row | “\| `a ?? d` \| the value, or `d` \|” | `a ?? d` is the value, or d when empty. | `run:0` |
| `ty1256` | 1256 | row | “\| `a?.f` \| the field, still wrapped \|” | `a?.f` is the field, still wrapped: it binds to an `int32?`. | `run:0` |
| `ty1256b` | 1256 | row | “\| `a?.f` \| the field, still wrapped \|” | `a?.f` is still wrapped: binding it to a plain `int32` is refused. | `refuse` |
| `ty1257` | 1257 | row | “\| `pick (a ?? d) { … }` \|” | `pick (a ?? d)` selects over the value or the default. | `run:0` |
| `ty1259` | 1259 | rule | “**No `pick` selects on an `Optional` (D-260, 1.5.2c; `NITPICK-TYPE-065`).**” | A pick on an Optional is TYPE-065 (statement form). | `refuse:NITPICK-TYPE-065` |
| `ty1262` | 1262 | rule | “refused by name at the selector, in the statement form and in the expression” | A pick on an Optional is TYPE-065 in the expression form too. | `refuse:NITPICK-TYPE-065` |
| `ty1268` | 1268 | rule | “`T?` and `Optional<T>` are **one type with two spellings**” | `T?` and `Optional<T>` are one type: an `Optional<int32>` binds to an `int32?`. | `run:0` |
| `ty1272` | 1272 | rule | “The wrap from `T` to `Optional<T>` is the **one implicit conversion in the” | The wrap from T applies at a declaration's initialiser, a call argument and `pass`. | `run:0` |
| `ty1275` | 1275 | rule | “no implicit widening (D-092)” | Nothing else is coerced: an int32 into an int64 binding is refused. | `refuse` |
| `ty1276` | 1276 | rule | “A `NIL`-**typed value**, which is what `drop f()` yields, is” | A NIL-typed value is not wrapped: `int32?:x = drop f();` is refused. | `refuse` |
| `ty1280` | 1280 | rule | “**`Some(42)` was struck (D-099).**” | `Some(42)` does not exist: `int32?:a = Some(42i32);` is refused. | `refuse` |
| `ty1282` | 1282 | rule | “A replacement literal form `Optional{…}` was then drafted and” | `Optional{…}` was struck too: `int32?:a = Optional{ value: 5i32 };` is refused. | `refuse` |
| `ty1287` | 1287 | rule | “**An `Optional` has no readable members.**” | `.has_value` is not a member: reading it is refused. | `refuse` |
| `ty1288` | 1288 | rule | “names, not source-level members” | `.value` is not a member: reading it is refused. | `refuse` |
| `ty1294` | 1294 | rule | “**`NIL?`** — `NIL?:x = NIL;` is ambiguous” | `NIL?` is refused. | `refuse` |
| `ty1296` | 1296 | rule | “**`Optional<Optional<T>>`**” | `Optional<Optional<T>>` is refused. | `refuse` |
| `ty1298` | 1298 | rule | “`int32??` reads as `int32` followed by the null-coalesce operator” | `int32??` is not a type: it lexes as `int32` and `??`, and is refused. | `refuse` |
| `ty1299` | 1299 | rule | “flattens** rather than manufacturing the type behind the rule's back” | `?.` flattens: over an Optional field it yields that field as it is (`int32?`), empty or holding. | `run:0` |
| `ty1303` | 1303 | rule | “**EVERY function in Nitpick returns `Result<T>`** except `pub func:main` and” | Every function returns a Result, a `never fails` one included: binding its bare call to an int32 is refused. | `refuse` |
| `ty1309` | 1309 | example | “```nitpick” | A Result's canonical fields are `value` and `err`: an error reads `r.err == E2`, a success `r.value`. | `run:0` |
| `ty1317` | 1317 | example | “```llvm” | `Result<int32>` is 8 bytes with alignment 4. | `run:0` |
| `ty1320` | 1320 | rule | “%Result_i32 = type { i32, i32 }” | `Result<int32>` is `{ i32, i32 }`: an int32 function returns that type. | `ir:(?m)^define \{ i32, i32 \} @"?(?:[\w$]+\.)*m11r"?\(` |
| `ty1330` | 1330 | row | “\| `pass(retVal);` \| `return Result{value: retVal};`” | `pass(retVal);` returns a success holding retVal. | `run:0` |
| `ty1331` | 1331 | row | “\| `fail(errCode);` \| `return Result{err: errCode, value: zero};`” | `fail(errCode);` returns an error holding errCode. | `run:0` |
| `ty1332` | 1332 | row | “\| `return Result{err: errCode, value: retVal};` \| (literal, no desugar) \|” | `return Result{err: e, value: v};` returns both. | `run:0` (M10 `r10_result_literal_both`) |
| `ty1337` | 1337 | rule | “`0i32` is not assignable to a `tbb32`, there being no implicit conversion” | There is no implicit conversion from int32 to tbb32: `tbb32:t = 0i32;` is refused. | `refuse` |
| `ty1340` | 1340 | rule | “**Either field may be omitted**” | A Result literal's omitted `err` is success. | `run:0` (M10 `d07_result_literal_omits_err`) |
| `ty1340b` | 1340 | rule | “**Either field may be omitted**” | A Result literal with only `err` is that error. | `run:0` (M10 `d08_result_literal_omits_value`) |
| `ty1343` | 1343 | rule | “order is free**” | Field order is free: `Result{value: v, err: e}` and `Result{err: e, value: v}` are the same. | `run:0` |
| `ty1346` | 1346 | rule | “**There is no `is_error` field to write** (D-069)” | There is no `is_error` field to write: a literal naming it is refused. | `refuse` |
| `ty1356` | 1356 | rule | “existing `pick(r.is_error)` code is unaffected” | `r.is_error` is a derived accessor: `pick (r.is_error)` selects on it. | `run:0` |
| `ty1360` | 1360 | rule | “The error field's value space is total” | 0 is success, positive codes user errors, negative codes system errors, and INT32_MIN unconstructible. | untestable [internal] the codes are an encoding (D-179: the domain is typed, and the sign an encoding detail) |
| `ty1362` | 1362 | rule | “Building a `Result` whose code is ERR, or” | Building a Result whose code is ERR, or 0 on a failure path, traps where it is built. | untestable [unobservable] since D-179 typed the error domain, no program can spell a zero or ERR code |
| `ty1369` | 1369 | rule | “The compiler WILL NOT allow accessing `.value` without first checking `.is_error`” | Reading `.value` without checking is refused. | `refuse` (M10 `r07_value_without_check_refused`) |
| `ty1374` | 1374 | row | “\| Safe unwrap \| `expr ? defaultVal` \|” | Safe unwrap `expr ? defaultVal` gives the default on an error. | `run:0` |
| `ty1375` | 1375 | row | “**On an `Optional`, not a `Result`**” | `??` is on an Optional, not a Result: `m11k(…) ?? 7` is refused. | `refuse` |
| `ty1376` | 1376 | row | “\| Emphatic unwrap \| `expr ?! errCode` \|” | Emphatic unwrap `expr ?! errCode` triggers failsafe with errCode on an error (E1 exits 81, where the callee's own E2 would exit 82). | `run:81` |
| `ty1377` | 1377 | row | “\| Raw unwrap \| `raw(expr)` or `raw expr` \|” | `raw(expr)` and `raw expr` extract a never-fails call's value. | `run:0` |
| `ty1377b` | 1377 | row | “\| `_!` \|” | `_!` is raw unwrap's shorthand. | `run:0` |
| `ty1378` | 1378 | row | “\| Drop \| `drop(expr)` or `drop expr` \|” | `drop(expr)` and `drop expr` run a NIL never-fails call. | `run:0` |
| `ty1378b` | 1378 | row | “\| `_?` \|” | `_?` is drop's shorthand. | `run:0` |
| `ty1379` | 1379 | row | “\| Discard \| `discard(param)` \| `_~` \|” | `discard(x)` marks a value unused, and a `_~` name marks a parameter unused. | `run:0` |
| `ty1382` | 1382 | rule | “licensed only” | `raw` on a may-fail call is refused, TYPE-042. | `refuse:NITPICK-TYPE-042` (M10 `r08_raw_on_fallible_refused`) |
| `ty1385` | 1385 | rule | “`drop` = the "void call": run a `never fails` function whose success type is” | `drop` of a may-fail call is refused. | `refuse:NITPICK-TYPE-042` (M10 `r05_drop_of_fallible_refused`) |
| `ty1387` | 1387 | rule | “`?!`-trapped, or `? NIL`-swallowed” | A may-fail NIL call is swallowed with `? NIL`. | `run:0` |
| `ty1387b` | 1387 | rule | “a never-failing VALUE is `discard(raw f())`” | A never-failing value is discarded with `discard(raw f())`. | `run:0` |
| `ty1388` | 1388 | rule | “takes a VALUE” | `discard` of a Result is refused. | `refuse` (M10 `r09_discard_of_result_refused`) |
| `ty1392` | 1392 | rule | “(`TYPE-039`), the `defer` rule (`TYPE-040`)” | The statement closed list: a bare call statement that discards a Result is TYPE-039. | `refuse:NITPICK-TYPE-039` |
| `ty1396` | 1396 | example | “```nitpick” | The storage_driver extern example compiles. | `compile` |
| `ty1419` | 1419 | rule | “The contract grammar remains parsed and is” | An `extern` method's contract (`fails on result < 0i32 with errno`) is parsed and refused, naming D-149. | `sh:0` |
| `ty1428` | 1428 | example | “```llvm” | `Handle<T>` is { i64, i32 }: 16 bytes, alignment 8. | `run:0` |
| `ty1439` | 1439 | example | “```llvm” | An arena is allocated with `alloc(N)` and a cast: `alloc(N) => arena<T>->` compiles. | `compile` |
| `ty1453` | 1453 | row | “\| `a.load()` \|” | `a.load()` on an `atomic<int32>` is native, sequentially consistent IR: `load atomic i32, ptr … seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?load atomic i32, ptr [^,\n]+ seq_cst)` |
| `ty1454` | 1454 | row | “\| `a.store(v)` \|” | `a.store(v)` on an `atomic<int32>` is native, sequentially consistent IR: `store atomic i32 …, ptr … seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?store atomic i32 [^,\n]+, ptr [^,\n]+ seq_cst)` |
| `ty1455` | 1455 | row | “\| `a.swap(v)` \|” | `a.swap(v)` on an `atomic<int32>` is native, sequentially consistent IR: `atomicrmw xchg ptr …, i32 … seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?atomicrmw xchg ptr [^,\n]+, i32 [^,\n]+ seq_cst)` |
| `ty1456` | 1456 | row | “\| `a.fetch_add(v)` \|” | `a.fetch_add(v)` on an `atomic<int32>` is native, sequentially consistent IR: `atomicrmw add ptr …, i32 … seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?atomicrmw add ptr [^,\n]+, i32 [^,\n]+ seq_cst)` |
| `ty1457` | 1457 | row | “\| `a.fetch_sub(v)` \|” | `a.fetch_sub(v)` on an `atomic<int32>` is native, sequentially consistent IR: `atomicrmw sub ptr …, i32 … seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?atomicrmw sub ptr [^,\n]+, i32 [^,\n]+ seq_cst)` |
| `ty1458` | 1458 | row | “\| `a.compare_exchange(exp, des)` \|” | `a.compare_exchange(exp, des)` on an `atomic<int32>` is native, sequentially consistent IR: `cmpxchg ptr …, i32 …, i32 … seq_cst seq_cst`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*main"?\((?=(?:(?!\n\}).)*?cmpxchg ptr [^,\n]+, i32 [^,\n]+, i32 [^,\n]+ seq_cst seq_cst)` |
| `ty1466` | 1466 | row | “\| `simd<flt32, 4>` \|” | `simd<flt32, 4>` is 16 bytes with alignment 16. | `run:0` |
| `ty1466b` | 1466 | row | “\| `simd<flt32, 4>` \| `<4 x float>` \|” | A `simd<flt32, 4>` parameter is `<4 x float>`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11v"?\(<4\ x\ float>(?=[\s,)]))` |
| `ty1467` | 1467 | row | “\| `simd<flt64, 2>` \|” | `simd<flt64, 2>` is 16 bytes with alignment 16. | `run:0` |
| `ty1467b` | 1467 | row | “\| `simd<flt64, 2>` \| `<2 x double>` \|” | A `simd<flt64, 2>` parameter is `<2 x double>`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11v"?\(<2\ x\ double>(?=[\s,)]))` |
| `ty1468` | 1468 | row | “\| `simd<int32, 8>` \|” | `simd<int32, 8>` is 32 bytes with alignment 32. | `run:0` |
| `ty1468b` | 1468 | row | “\| `simd<int32, 8>` \| `<8 x i32>` \|” | A `simd<int32, 8>` parameter is `<8 x i32>`. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11v"?\(<8\ x\ i32>(?=[\s,)]))` |
| `ty1472` | 1472 | rule | “2..64, total ≤ 64 bytes” | A simd of one lane is refused. | `refuse` |
| `ty1472b` | 1472 | rule | “2..64, total ≤ 64 bytes” | A simd over 64 bytes is refused: `simd<int64, 16>` is 128. | `refuse` |
| `ty1472c` | 1472 | rule | “alignment = next power of two ≥ size, capped 64” | A simd's alignment is the next power of two at or above its size: `simd<int16, 3>` (6 bytes) aligns to 8, so `{int8, it}` is 16 bytes. | `run:0` |
| `ty1473` | 1473 | rule | “`simd(…)` constructs annotation-directed” | `simd(…)` takes N components, or one that splats. | `run:0` |
| `ty1474` | 1474 | rule | “Operations are elementwise on identical types” | Operations are elementwise: `+ - * / %` on lanes, and `& \| ^ << >>` on integer lanes. | `run:0` |
| `ty1475` | 1475 | rule | “comparisons yield `simd<bool, N>`” | A lane comparison yields `simd<bool, N>`. | `run:0` |
| `ty1476` | 1476 | rule | “`v[i]` is a bounds-checked lane place” | A lane index past the lanes traps OutOfBounds. | `trap:OutOfBounds` |
| `ty1476b` | 1476 | rule | “`.len` is the lane count” | `.len` is the lane count. | `run:0` |
| `ty1477` | 1477 | rule | “vector division carries D-007 as ANY-LANE checks” | Integer vector division by a vector with one zero lane traps DivByZero. | `trap:DivByZero` |
| `ty1478` | 1478 | rule | “INT_MIN/−1 → DivOverflow” | Integer vector division with one lane INT_MIN / -1 traps DivOverflow. | `trap:DivOverflow` |
| `ty1478b` | 1478 | rule | “Reductions are methods” | Reductions are methods: `.sum()/.min()/.max()` on numeric lanes, `.all()/.any()` on bool lanes. | `run:0` |
| `ty1480` | 1480 | rule | “float `.sum()` is deterministic BY CONSTRUCTION” | A float `.sum()` is an ordered fold: [1e16, 1, -1e16, 1] sums to 1 (a tree reduction gives 0). | `run:0` |
| `ty1481` | 1481 | rule | “Casts are elementwise under the scalar” | A simd cast is elementwise: `simd<int32, 4> => simd<int64, 4>` widens each lane. | `run:0` |
| `ty1482` | 1482 | rule | “rules and never change N” | A simd cast never changes N: `simd<int32, 4> => simd<int64, 2>` is refused. | `refuse` |
| `ty1482b` | 1482 | rule | “Shuffles are OUT by decision (D-194)” | There are no shuffles. | untestable [vague] no shuffle spelling is named, so no program can try one |
| `ty1487` | 1487 | rule | “division's any-lane guard is ONE `div-zero` row” | A simd division's any-lane guard is one div-zero row and one div-min row (a signed element). | `sh:0` |
| `ty1488` | 1488 | rule | “a shift's one `shift-range`” | A simd shift has one shift-range row. | `sh:0` |
| `ty1490` | 1490 | rule | “its ELEMENT's kind (DEF-37, 1.5.4b step 4b): integer lanes do, float lanes” | Float lanes do not arm DivByZero: a float simd divided by zero lanes gives infinities. | `run:0` |
| `ty1491` | 1491 | rule | “integer lane's `+ - *` and an” | An integer lane's `+` traps IntOverflow as its scalar does. | `trap:IntOverflow` |
| `ty1492` | 1492 | rule | “integer `.sum()` trap `IntOverflow` as their scalars do” | An integer `.sum()` traps IntOverflow. | `trap:IntOverflow` |
| `ty1495` | 1495 | rule | “spelling `v op= w` lowers through the same vector path with its guards” | `v += w` keeps the guards: a lane overflow traps IntOverflow. | `trap:IntOverflow` |
| `ty1504` | 1504 | row | “\| `vec2` \|” | `vec2` (the library's `nvec.npk`) is 16 bytes. | `sh:0` |
| `ty1505` | 1505 | row | “\| `vec3` \|” | `vec3` (the library's `nvec.npk`) is 24 bytes. | `sh:0` |
| `ty1506` | 1506 | row | “\| `vec4` \|” | `vec4` (the library's `nvec.npk`) is 32 bytes. | `sh:0` |
| `ty1507` | 1507 | row | “\| `matrix<T>` \|” | `matrix<int64>` (the library's `ntensor.npk`) is 24 bytes. | `sh:0` |
| `ty1508` | 1508 | row | “\| `tensor<T>` \|” | `tensor<int64>` (the library's `ntensor.npk`) is 24 bytes. | `sh:0` |
| `ty1510` | 1510 | rule | “**These are LIBRARY types and are not keywords** (D-135)” | `vec2` is not a keyword: a local of that name compiles. | `run:0` |
| `ty1515` | 1515 | rule | “A library cannot declare a type whose name is a keyword” | A type named by a keyword is refused: `struct:tbb8 = { … };`. | `refuse` |
| `ty1518` | 1518 | rule | “`matrix<T>` and `tensor<T>` are heap-backed containers” | matrix and tensor are heap-backed containers with nothing SIMD about them. | untestable [vague] a description of the library; the rows above test the sizes |
| `ty1526` | 1526 | example | “```llvm” | A function `int32(int32, int32)` is `define { i32, i32 } @f(i32, i32)`. | `ir:(?m)^define \{ i32, i32 \} @"?(?:[\w$]+\.)*m11add"?\(i32 [^,\n]+, i32 ` |
| `ty1535` | 1535 | rule | “When Result elision proves function is infallible” | A function proved infallible returns a raw `i32`: a `never fails` int32 function is `define i32`. | `ir:(?m)^define i32 @"?(?:[\w$]+\.)*m11e"?\(` |
| `ty1545` | 1545 | rule | “**Not surface syntax.** Nothing in the language produces a `Future<T>`” | `Future<T>` cannot be named in a signature. | `refuse` |
| `ty1558` | 1558 | example | “```llvm” | A future is `{ ptr, ptr }`, a coroutine handle and a result slot. | untestable [internal] a lowering artifact no program can name (the text's own words) |
| `ty1567` | 1567 | rule | “**One data word and ONE VTABLE WORD PER TRAIT**” | A `dyn` is (N+1) x 8 bytes: 16 for one trait, 24 for two. | `run:0` |
| `ty1572` | 1572 | example | “```llvm” | `dyn A` is `{ ptr, ptr }`: a `dyn A` parameter has that type. | `ir:(?s)\A(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11d"?\(\{ ?ptr, ptr ?\}(?=[\s,)]))` |
| `ty1576` | 1576 | rule | “; `dyn A & B & C` — one vtable word per bound, 32 bytes” | `dyn A & B & C` is 32 bytes. | `run:0` |
| `ty1579` | 1579 | rule | “; Vtable: function pointers in TRAIT DECLARATION ORDER (D-158)” | A vtable holds one adapter thunk per method, in declaration order. | untestable [internal] a vtable's slot order is not observable from a program |
| `ty1584` | 1584 | rule | “The bounds are **canonically ordered by trait name at type interning**” | `dyn A & B` and `dyn B & A` are one type: one binds to the other. | `run:0` |
| `ty1586` | 1586 | rule | “Widening (`dyn A & B` → `dyn A`) is a” | Widening `dyn A & B` to `dyn A` compiles and keeps the value. | `run:0` |

## VERIFICATION (`meta/specs/VERIFICATION_REFERENCE.md`)

| id | line | kind | quote | claim | expected |
|---|---|---|---|---|---|
| `vf0003` | 3 | rule | “mathematically prove the correctness of the code before it is allowed to execute” | Nitpick proves the code correct with Z3 before it is allowed to execute. | untestable [vague] a statement of intent: the plain build runs unverified code by design (the banner at 5-21 and §1.2), and the sentence names no outcome a program can check |
| `vf0007` | 7 | rule | “`npkc --obligations DIR`” | The compiler writes every function's proof obligations as SMT-LIB2 text under `--obligations DIR`: numbered .smt2 files holding (check-sat) queries, plus index.txt and rows.txt. | `sh:0` |
| `vf0008` | 8 | rule | “`npkc --elide nitpick.obligations`” | The compiler reads a manifest of verdicts with `--elide FILE` and emits the verified build. | untestable [z3] the manifest's verdicts come only from `npkg verify` with the pinned z3; a hand-made manifest's header (the z3 pin, the profile) is §8's and outside this claim |
| `vf0009` | 9 | rule | “spawns the pinned z3” | `npkg verify` runs one fresh z3 per function, decides every obligation, holds the rows to the committed nitpick.obligations and emits the VERIFIED build, each discharged guard replaced by llvm.assume. | untestable [z3] needs `npkg verify` with the pinned z3 |
| `vf0020` | 20 | rule | “manifest holds 5,890 rows” | At the 1.5 close the compiler's own manifest holds 5,890 rows. | untestable [tree] a figure about the compiler's own tree and manifest |
| `vf0026` | 26 | rule | “compilation immediately halts” | An `assert_static` whose expression evaluates to false halts compilation. | `refuse` |
| `vf0028` | 28 | example | “```nitpick” | The example `assert_static(1i32 == 1i32);` compiles: a true constant proposition passes and the program runs. | `run:0` |
| `vf0035` | 35 | rule | “`NITPICK-TYPE-069`” | An assert_static proposition that reads a value the evaluator cannot see (a run-time value) is refused, NITPICK-TYPE-069. | `refuse:TYPE-069` |
| `vf0036` | 36 | rule | “one that folds to `false` halts compilation under the same code” | An assert_static that folds to false halts compilation with NITPICK-TYPE-069. | `refuse:TYPE-069` |
| `vf0037` | 37 | rule | “`comptime` body the evaluator folds it per call” | In a comptime body an assert_static over the function's parameter is folded per call: called comptime with a value that satisfies it, the program compiles and computes. | `run:0` |
| `vf0037b` | 37 | rule | “a false `prove` there” | A false `prove` in a comptime body, evaluated at a comptime call, is a counterexample: compilation is refused. | `refuse` |
| `vf0038` | 38 | rule | “The statement lowers to nothing” | An assert_statement lowers to nothing: the IR of a program with `assert_static(1i32 == 1i32)` appended to a line has as many lines as the same program without it. | `sh:0` |
| `vf0039` | 39 | rule | “row in the manifest is the catalogue's `checker` entry” | An assert_static's row is the catalogue's checker entry: one `assert-static` row, frontend-decided (`c` in rows.txt's encoded column), no query. | `sh:0` |
| `vf0043` | 43 | rule | “forces the SMT solver to construct a mathematical proof” | `prove` makes the solver prove the expression across all control flows and states. | untestable [z3] a verdict of the verified build; the `--verify` flag it names is struck (§5, line 86) |
| `vf0045` | 45 | rule | “If the solver finds a path where the expression is false, compilation fails” | A prove with a counterexample path fails the (verified) compilation and reports the counterexample. | untestable [z3] the verified build's refusal (VERIFY-001) needs z3's verdict; `--prove-report` is struck |
| `vf0047` | 47 | example | “```nitpick” | The example compiles: `prove(x != 0i32)` inside `if (x > 0i32)` is accepted, and the plain build runs it as nothing. | `run:0` |
| `vf0055` | 55 | rule | “path-condition-aware” | Branch guards of enclosing control flow are asserted as axioms before a prove's obligation. | untestable [z3] only a z3 verdict shows which hypotheses a row carries |
| `vf0059` | 59 | rule | “an `if`'s condition inside its then-arm and its negation” | An if's condition is a hypothesis in its then-arm, its negation in the else-arm. | untestable [z3] a hypothesis of the encoder, visible only through a verdict |
| `vf0061` | 61 | rule | “terminator” | After an arm that never falls through (pass, fail, return, exit, trap, break, continue, give), the other arm's condition holds. | untestable [z3] a hypothesis of the encoder, visible only through a verdict |
| `vf0063` | 63 | rule | “a `pick` arm's pattern (a value, a range, a wildcard as the” | A pick arm is taken under its pattern and the negations of the earlier arms: the first matching arm in source order wins. | `run:0` (M10 `p03_first_match_wins`) |
| `vf0065` | 65 | rule | “`where` guard” | A pick arm's where guard is a hypothesis; none when a fall sits in the pick, only the pattern when any arm carries a guard. | untestable [z3] a hypothesis of the encoder, visible only through a verdict |
| `vf0066` | 66 | rule | “a loop's negated condition after a loop nothing” | After a loop nothing breaks out of, the negated loop condition is a hypothesis. | untestable [z3] a hypothesis of the encoder, visible only through a verdict |
| `vf0067` | 67 | rule | “`when`'s `then` and `end` on whether the body ran” | when's then and end blocks carry whether the body ran as a hypothesis. | untestable [z3] a hypothesis of the encoder, visible only through a verdict |
| `vf0068` | 68 | rule | “a ternary's branches under theirs” | A ternary's branches are evaluated under their conditions: only the chosen one runs. | `run:0` (M10 `x05_ternary_evaluates_one_branch`) |
| `vf0068b` | 68 | rule | “right-hand side of `&&`/`\|\|`” | The right-hand side of && and \|\| is evaluated under its left side: a division guarded by the left operand never runs when the left operand decides. | `run:0` |
| `vf0070` | 70 | rule | “MERGE as `(ite c v_then v_else)`” | Versions after an if, a when or a pick merge as an ite; a pick expression's value is the chain of its arms' give terms. | untestable [z3] the encoder's terms, visible only through a verdict |
| `vf0072` | 72 | rule | “counted loop's `$` and a range `for`'s binding are terms with their bounds” | A counted loop's `$` and a range for's binding are terms carrying their bounds. | untestable [z3] the encoder's terms, visible only through a verdict |
| `vf0075` | 75 | rule | “is a row of kind `prove`” | Each `prove(e)` is one obligation row of kind `prove`. | `sh:0` |
| `vf0076` | 76 | rule | “nothing executes” | A prove is walked quiet: nothing in it executes, so a division by zero inside a prove does not trap at run time. | `run:0` |
| `vf0077` | 77 | rule | “is not a site” | A division inside a prove is not a site: it records no div-zero row (while the prove row exists). | `sh:0` |
| `vf0077b` | 77 | rule | “knowledge for every site” | Once discharged, a prove is knowledge for every site after it. | untestable [z3] a discharge is z3's verdict |
| `vf0078` | 78 | rule | “The plain build lowers the” | The plain build lowers a prove to nothing and claims nothing: a prove that is false at run time does not trap. | `run:0` |
| `vf0079` | 79 | rule | “The VERIFIED build refuses an” | Under --elide, a prove whose row the manifest does not discharge (open, budget, unencoded or absent) is NITPICK-VERIFY-001 at the statement. | untestable [z3] needs a manifest from `npkg verify` with the pinned z3 |
| `vf0083` | 83 | rule | “writes the” | `npkg verify --explain` writes the model of an open prove. | untestable [z3] needs `npkg verify` with the pinned z3 |
| `vf0085` | 85 | rule | “is `open` rather than `unencoded`” | A bool proposition always has at least an opaque term, so a prove row is open rather than unencoded. | untestable [z3] `open` is z3's verdict; which propositions the encoder cannot express is not stated here |
| `vf0096` | 96 | example | “```nitpick” | The example compiles and runs: a Rules block over int32 and a limited local initialised with 5, which satisfies it. | `run:0` |
| `vf0109` | 109 | rule | “a typo is `NITPICK-RESOLVE-002`” | The rule name in limit<...> resolves like any name: a misspelt rule at a local is NITPICK-RESOLVE-002. | `refuse:RESOLVE-002` |
| `vf0110` | 110 | rule | “`NITPICK-RESOLVE-011`” | A limit<...> naming something that is not a Rules block (a function) is NITPICK-RESOLVE-011. | `refuse:RESOLVE-011` |
| `vf0111` | 111 | rule | “parameter” | The rule name resolves at a parameter: a misspelt rule on a parameter is NITPICK-RESOLVE-002. | `refuse:RESOLVE-002` |
| `vf0111b` | 111 | rule | “and a refinement” | The rule name resolves at a refinement: a misspelt refinement inside a Rules block is NITPICK-RESOLVE-002. | `refuse:RESOLVE-002` |
| `vf0111c` | 111 | rule | “types eagerly” | A Rules body types eagerly: an ill-typed Rules block is refused even when nothing uses it. | `refuse` |
| `vf0112` | 112 | rule | “every clause a `bool`” | Every Rules clause is a bool: a clause of type int32 is refused. | `refuse` |
| `vf0112b` | 112 | rule | “subject's type” | `$` has the subject's type: in a Rules<bool>, comparing `$` with an int32 is refused. | `refuse` |
| `vf0113` | 113 | rule | “`limit<r_positive> int64:x` refuses” | A limited binding's declared type must be the rule's subject by identity: limit<r_positive> int64:x over a Rules<int32> is NITPICK-TYPE-059. | `refuse:TYPE-059` |
| `vf0114` | 114 | rule | “and so does a type parameter” | A limited binding whose declared type is a type parameter is NITPICK-TYPE-059. | `refuse:TYPE-059` |
| `vf0116` | 116 | rule | “clause is a contract expression and follows” | A Rules clause is a contract expression under §3's admission: a clause using `?\|` is refused. | `refuse` |
| `vf0119` | 119 | rule | “is enforced in every build” | limit<Rules> is enforced in every build: a limited local initialised at run time with a value its rule refuses traps LimitViolated in the plain build. | `trap:LimitViolated` |
| `vf0121` | 121 | rule | “the integrated Z3 solver proves that the assigned” | With verification the solver proves `5i32` satisfies `$ > 0i32` and the check is removed. | untestable [z3] a discharge and its elision are the verified build's |
| `vf0124` | 124 | rule | “traps to `failsafe`” | Where a check remains, a violation traps to failsafe: an assignment of a run-time value the rule refuses traps LimitViolated. | `trap:LimitViolated` |
| `vf0127` | 127 | rule | “proving a constraint removes its runtime check” | Proving a constraint removes its runtime check. | untestable [z3] elision is the verified build's |
| `vf0131` | 131 | rule | “checked AFTER every write” | A limited binding is checked after every write over its whole value: a compound assignment that leaves the rule traps LimitViolated. | `trap:LimitViolated` |
| `vf0132` | 132 | rule | “a declaration without one is not a” | A declaration without an initialiser is not a write point: the vacant value (0, outside `$ > 0`) is never checked, and the first assignment is. | `run:0` |
| `vf0133` | 133 | rule | “every assignment to it” | Every assignment to a limited binding is a write point: assigning a whole struct value the rule refuses traps LimitViolated. | `trap:LimitViolated` |
| `vf0134` | 134 | rule | “a field or element store re-checks the root” | A field store to a limited struct re-checks the whole root: storing a refused field value traps LimitViolated. | `trap:LimitViolated` |
| `vf0134b` | 134 | rule | “element store” | An element store to a limited array re-checks the whole root: storing a refused element traps LimitViolated. | `trap:LimitViolated` |
| `vf0135` | 135 | rule | “callee's entry for a limited parameter, once per call in a sync function” | A limited parameter is checked at the callee's entry in a sync function: a call with a refused argument traps LimitViolated before the body runs. | `trap:LimitViolated` |
| `vf0136` | 136 | rule | “once per task at state 0 in a coroutine” | A coroutine's limited parameter is checked at state 0: awaiting it with a refused argument traps LimitViolated. | `trap:LimitViolated` |
| `vf0137` | 137 | rule | “`@"npk.<module>.<name>"`” | The check is one generated predicate per Rules declaration, emitted as @"npk.<module>.<name>". | `ir:^define [^\n]*@"npk\.vf0137\.r_positive"\(` |
| `vf0138` | 138 | rule | “the clauses in source order, short-circuit” | A rule's clauses run in source order, short-circuit: `$ != 0` false ends the check, so the division in the next clause never runs and the trap is LimitViolated, not DivByZero. | `trap:LimitViolated` |
| `vf0138b` | 138 | rule | “refinements then the clauses” | The refinements run before the clauses: a refinement written after a dividing clause still runs first, so zero traps LimitViolated, not DivByZero. | `trap:LimitViolated` |
| `vf0140` | 140 | rule | “limited binding has no address” | `@` of a limited binding is refused, NITPICK-TYPE-063. | `refuse:TYPE-063` |
| `vf0140b` | 140 | rule | “`$$m`” | `$$m` of a limited binding is refused, NITPICK-TYPE-063. | `refuse:TYPE-063` |
| `vf0140c` | 140 | rule | “`$$i` of it” | `$$i` of a limited binding is refused, NITPICK-TYPE-063. | `refuse:TYPE-063` |
| `vf0141` | 141 | rule | “out of an owning field or element of it, refuse (NITPICK-TYPE-063)” | A move out of an owning field of a limited binding is refused, NITPICK-TYPE-063. | `refuse:TYPE-063` |
| `vf0141b` | 141 | rule | “element of it” | Passing an owning element out of a limited array is refused, NITPICK-TYPE-063. | `refuse:TYPE-063` |
| `vf0142` | 142 | rule | “pass it by value” | A limited binding passed by value is accepted (the permitted twin of the address refusal). | `run:0` |
| `vf0144` | 144 | rule | “trait signature's parameter” | A limit on a trait signature's parameter (no write point) is refused, NITPICK-TYPE-064. | `refuse:TYPE-064` |
| `vf0144b` | 144 | rule | “a `wild`/`wildx` binding” | A limit on a `wild` binding is refused, NITPICK-TYPE-064. | `refuse:TYPE-064` |
| `vf0145` | 145 | rule | “function;” | A limit in a comptime function (its parameter) is refused, NITPICK-TYPE-064. | `refuse:TYPE-064` |
| `vf0145b` | 145 | rule | “`main`/`failsafe`'s parameters under D-244” | A limit on main's parameter is refused: the sentence lists it among the TYPE-064 sites. | `refuse:TYPE-064` |
| `vf0146` | 146 | rule | “every write point is a `limit` row” | Every write point of a limited binding is one `limit` row: an initialiser, an assignment and a compound assignment in main are three. | `sh:0` |
| `vf0147` | 147 | rule | “HYPOTHESIS” | The rule is a hypothesis on every later version of the binding, so a division by a limited divisor discharges, after a loop included. | untestable [z3] a discharge is z3's verdict |
| `vf0150` | 150 | rule | “scalar family is inside it” | Every scalar family is inside the encoder's fragment: a limit over a flt64 subject is an encoded row. | `sh:0` |
| `vf0151` | 151 | rule | “a string, a struct or an array is” | A struct subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt). | `sh:0` |
| `vf0151b` | 151 | rule | “or an array” | An array subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt). | `sh:0` |
| `vf0152` | 152 | rule | “is an `unencoded` row” | A string subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt). | `sh:0` |
| `vf0152b` | 152 | rule | “whose guard stays” | An unencoded row's guard stays: a string subject's rule is still checked at run time, and an empty string traps LimitViolated. | `trap:LimitViolated` |
| `vf0153` | 153 | rule | “limited parameters is a `limit-subsume` row” | Every direct call of a sync callee with limited parameters is one limit-subsume row: two calls, two rows. | `sh:0` |
| `vf0156` | 156 | rule | “ONE `llvm.assume` over the rule's range clauses” | A discharged write point emits one llvm.assume over the rule's range clauses and no check. | untestable [z3] needs a manifest with the row discharged |
| `vf0158` | 158 | rule | “`limit-subsume` row lets the call name the callee's BODY” | A discharged limit-subsume row lets the call name the callee's body past its checked entry. | untestable [z3] needs a manifest with the row discharged |
| `vf0159` | 159 | rule | “a sync function with a limited parameter is emitted as” | A sync function with a limited parameter is emitted as <symbol>.body plus its ordinary symbol, the checked entry. | `ir:^define [^\n]*@"npk\.vf0159\.limited\.body"\(` |
| `vf0161` | 161 | rule | “function value, vtable slot and spawn names by construction” | A function value names the checked entry: calling a limited function through a function value with a refused argument traps LimitViolated. | `trap:LimitViolated` |
| `vf0164` | 164 | rule | “It traps to `failsafe`, as” | A constraint violation traps to failsafe: a limited local driven out of its rule by a loop traps LimitViolated. | `trap:LimitViolated` |
| `vf0174` | 174 | rule | “the solver proves the indices unequal and the borrows disjoint” | With indices under different rules, the solver proves two $$m claims disjoint. | untestable [z3] the disjoint row's discharge is z3's verdict |
| `vf0177` | 177 | example | “```nitpick” | The example compiles and runs in the plain build: two $$m claims of one array at an even and an odd index, 7 + 9 = 16. | `run:0` |
| `vf0193` | 193 | rule | “declaration-qualifier spelling the prototype text carried” | The declaration-qualifier borrow spelling `$$m int32:a = arr[i];` never existed: it is refused. | `refuse` |
| `vf0195` | 195 | rule | “is a SHARED claim (many readers)” | $$i is a shared claim: two $$i of one local and a plain read of it may live together. | `run:0` |
| `vf0196` | 196 | rule | “an EXCLUSIVE one (one writer, no other name)” | $$m is an exclusive claim: reading the local by its name while the $$m claim lives is a static conflict, NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0197` | 197 | rule | “plain address that claims nothing” | `@place` claims nothing: two `@` of one local and a read of it may live together. | `run:0` |
| `vf0198` | 198 | rule | “counts as a write-capable access” | `@place` counts as a write-capable access: taking `@x` while a $$i claim of x lives is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0200` | 200 | rule | “conflicts with the call's other arguments” | A whole call argument's claim conflicts with the call's other arguments: `two($$m x, $$i x)` is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0202` | 202 | rule | “held by that local from its declaration to the end of the block” | A pointer local's claim ends with the block that declares it: after an inner block holding $$m x, x is read freely. | `run:0` |
| `vf0203` | 203 | rule | “a `defer` body sees every claim of its enclosing blocks” | A defer body sees every claim of its enclosing blocks: writing x in a defer while $$i x is held is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0204` | 204 | rule | “Non-lexical lifetimes and two-phase borrows are decided OUT” | Non-lexical lifetimes are out: reading x after the last use of a $$m holder, in the same block, is still NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0207` | 207 | rule | “a nested expression” | A claim in a nested expression is NITPICK-BORROW-014. | `refuse:BORROW-014` |
| `vf0210` | 210 | rule | “the fix is to spell `@` for an address that claims nothing” | The same nested position with `@` (an address that claims nothing) is accepted. | `run:0` |
| `vf0212` | 212 | rule | “a field that differs” | Paths through different fields are disjoint: writing s.b while $$m s.a lives is accepted. | `run:0` |
| `vf0212b` | 212 | rule | “two unequal numerals: disjoint” | Two unequal numeral indices are disjoint: writing a[1] while $$m a[0] lives is accepted. | `run:0` |
| `vf0213` | 213 | rule | “statically overlapping” | Equal numeral indices (nothing computed) overlap statically: writing a[0] while $$m a[0] lives is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0214` | 214 | rule | “write-capable access under `$$i`” | A write to x while a $$i claim of x lives is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0215` | 215 | rule | “claim on storage a held `@` reaches” | A claim on storage a held `@` reaches is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0215b` | 215 | rule | “a write through a shared claim's” | A write through a shared ($$i) claim's holder is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0216` | 216 | rule | “a call's arguments among themselves” | A call's arguments conflict among themselves: `two($$i x, @x)` (a write-capable `@` beside a shared claim) is NITPICK-BORROW-013. | `refuse:BORROW-013` |
| `vf0219` | 219 | rule | “held by the binding that holds the view from its declaration to the” | A view is a party on its root until the end of the block declaring its holder: after that block the root may be written. | `run:0` |
| `vf0220` | 220 | rule | “or live for the call a view expression” | A view expression passed as a call argument is live for that call only: the root may be written after the call. | `run:0` |
| `vf0222` | 222 | rule | “it lives is `NITPICK-BORROW-015`” | A write-capable access of viewed storage while the view lives is NITPICK-BORROW-015. | `refuse:BORROW-015` |
| `vf0222b` | 222 | rule | “with no runtime guard for a computed pair” | A computed index against a live view has no run-time guard: the pair refuses (BORROW-015) even when the index would fall outside the view. | `refuse:BORROW-015` |
| `vf0224` | 224 | rule | “the ESCAPE analysis's provenance” | What a binding views is the escape analysis's provenance at its fixpoint, with per-function summaries. | untestable [internal] the analysis's representation; its consequences are claimed at 219-236 |
| `vf0231` | 231 | rule | “recorded declaration (a `dyn` method, a function value) is read with every” | A call with no recorded declaration is read with every bit set: handing `@d` to a function value while a view of d lives is refused (BORROW-015), where the direct call is accepted (vf0235). | `refuse:BORROW-015` |
| `vf0233` | 233 | rule | “The path is what makes” | The path separates fields: a view of one string field does not freeze a write to a sibling int field. | `run:0` |
| `vf0235` | 235 | rule | “the mutation summary what makes `@r` handed to a callee that writes” | `@d` handed to a callee that writes nothing through it conflicts with no view of d: accepted. | `run:0` |
| `vf0236` | 236 | rule | “The prelude `List`'s” | A List's count, cap and items are its header: disjoint from a body view through an element's ptr, overlapping a slice of its storage. | untestable [internal] the List header's path rule is an analysis detail no single program here isolates |
| `vf0239` | 239 | rule | “COMPUTED conflict is a RUNTIME GUARD in every build” | A computed conflict is a run-time guard in every build: two $$m claims of one array at computed indices that are equal at run time trap BorrowOverlap. | `trap:BorrowOverlap` |
| `vf0244` | 244 | rule | “the obligation is the `disjoint` row” | The obligation of a computed claim pair is one `disjoint` row per site: §2.1's example has one. | `sh:0` |
| `vf0248` | 248 | rule | “removes the compare (no `llvm.assume` over pointers)” | A discharged disjoint row removes the compare, with no llvm.assume over pointers. | untestable [z3] needs a manifest with the row discharged |
| `vf0250` | 250 | rule | “the verified build carries no compare where the plain build” | In the example the rules make (not (= i j)) unsat, so the verified build carries no compare. | untestable [z3] z3's verdict and the verified build |
| `vf0253` | 253 | rule | “accesses that spell the SAME ROOT” | Exclusivity is decided among accesses that spell the same root: a $$m claim through one pointer parameter and a write through another aliasing it are two roots, accepted. | `run:0` |
| `vf0257` | 257 | rule | “a `fixed` binding has no address” | `@` of a fixed local is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0258` | 258 | rule | “`$$i`” | `$$i` of a fixed local is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0258b` | 258 | rule | “`$$m`” | `$$m` of a fixed local is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0258c` | 258 | rule | “the implicit pointer-receiver address” | A pointer-receiver call on a fixed binding (its implicit address) is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0259` | 259 | rule | “field included” | `@` of a fixed field of a plain struct is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0260` | 260 | rule | “through a `fixed` module binding” | `@` of a fixed module binding is refused, NITPICK-TYPE-071. | `refuse:TYPE-071` |
| `vf0267` | 267 | rule | “A borrow may not be returned” | A borrow may not be returned: `pass @x` of a local is refused. | `refuse` |
| `vf0267b` | 267 | rule | “stored into anything outliving the frame” | A borrow may not be stored into anything outliving the frame: storing `@x` of a local into the caller's struct is refused. | `refuse` |
| `vf0268` | 268 | rule | “an `await` point” | A borrow may not be carried across an await point: a pointer local holding `@x` used after an await is refused. | `refuse` |
| `vf0276` | 276 | example | “```nitpick” | The example's r_small_positive refines r_positive: a value that meets `$ < 100` but not the refinement's `$ > 0` traps LimitViolated. | `trap:LimitViolated` |
| `vf0279` | 279 | rule | “r_small_positive requires: $ > 0i32 AND $ < 100i32” | r_small_positive requires its own clause too: 100 traps LimitViolated. | `trap:LimitViolated` |
| `vf0282` | 282 | rule | “The Z3 solver can prove that one Rules block subsumes another” | The solver proves one Rules block implies another, enabling narrowing at call sites without checks. | untestable [z3] a limit-subsume discharge is z3's verdict |
| `vf0285` | 285 | rule | “refining a `Rules<int32>` is `NITPICK-TYPE-059`” | A Rules<int64> refining a Rules<int32> is NITPICK-TYPE-059. | `refuse:TYPE-059` |
| `vf0287` | 287 | rule | “`Rules` block that refines itself, directly or through a chain, is refused” | A Rules block that refines itself directly is refused at resolve, NITPICK-RESOLVE-006. | `refuse:RESOLVE-006` |
| `vf0287b` | 287 | rule | “through a chain” | A Rules block that refines itself through a chain is refused at resolve, NITPICK-RESOLVE-006. | `refuse:RESOLVE-006` |
| `vf0290` | 290 | rule | “the conjunction is `enc_rule`” | The conjunction is enc_rule; the implication is a limit-subsume row decided by z3. | untestable [internal] an encoder function name; the row's verdict is z3's |
| `vf0299` | 299 | rule | “`sealed limit<Len> int64:count;`” | A struct field may carry limit<R> after its qualifiers and before its type (`sealed limit<Len> int64:count;`): it compiles, and a write the rule admits runs. | `run:0` |
| `vf0301` | 301 | rule | “Its subject is the field's type by identity (TYPE-059)” | A field rule's subject must be the field's type by identity: a Rules<int32> on an int64 field is TYPE-059. | `refuse:TYPE-059` |
| `vf0302` | 302 | rule | “struct literal's value for the field” | A struct literal's value for a limited field is a write point, checked in every build: a refused value traps LimitViolated. | `trap:LimitViolated` |
| `vf0302b` | 302 | rule | “an assignment through any path (`s.f = v`” | An assignment `s.f = v` to a limited field is a write point: a refused value traps LimitViolated. | `trap:LimitViolated` |
| `vf0303` | 303 | rule | “`p.f = v` through a pointer” | An assignment through a pointer to a limited field is a write point: a refused value traps LimitViolated. | `trap:LimitViolated` |
| `vf0303b` | 303 | rule | “and a compound assignment” | A compound assignment to a limited field is a write point: leaving the rule traps LimitViolated. | `trap:LimitViolated` |
| `vf0306` | 306 | rule | “limited binding is two checks at two keys” | A write to a limited field of a limited binding is two limit rows (the field's and the root's): adding the statement `t.n = v` adds two limit rows to main. | `sh:0` |
| `vf0306b` | 306 | rule | “Every read of” | Every read of a limited field is a fact: the rule over the read's term is a hypothesis for later rows. | untestable [z3] a hypothesis shows only through z3's verdicts |
| `vf0309` | 309 | rule | “The rule must hold of the field's vacant” | A field rule that holds of the vacant value (0 for `$ >= 0`) is accepted. | `run:0` |
| `vf0311` | 311 | rule | “TYPE-077 otherwise” | A field rule that the vacant value fails (0 for `$ > 0`) is NITPICK-TYPE-077. | `refuse:TYPE-077` |
| `vf0311b` | 311 | rule | “TYPE-077” | A bool field whose rule refuses the vacant `false` is NITPICK-TYPE-077. | `refuse:TYPE-077` |
| `vf0311c` | 311 | rule | “a rule the folder cannot decide there is refused too” | A field rule the constant folder cannot decide at the declaration (a call) is refused. | `refuse` |
| `vf0312` | 312 | rule | “the subject is a plain integer, a `bool` or a `char`” | A field rule's subject is a plain integer, a bool or a char: a flt64 field with a rule is refused, even one the vacant 0.0 would satisfy. | `refuse` |
| `vf0312b` | 312 | rule | “A limited field has no” | `@s.f` of a limited field is refused, TYPE-063. | `refuse:TYPE-063` |
| `vf0313b` | 313 | rule | “through a pointer to its struct as well” | `@` of a limited field reached through a pointer to its struct is refused, TYPE-063. | `refuse:TYPE-063` |
| `vf0313c` | 313 | rule | “`$$m`/`$$i`” | `$$m` of a limited field is refused, TYPE-063. | `refuse:TYPE-063` |
| `vf0314` | 314 | rule | “of it and a pointer-receiver call on it refuse” | `$$i` of a limited field is refused, TYPE-063. | `refuse:TYPE-063` |
| `vf0314b` | 314 | rule | “pointer-receiver call on it” | A pointer-receiver call on a limited field is refused, TYPE-063. | `refuse:TYPE-063` |
| `vf0315` | 315 | rule | “REACH arms `LimitViolated` at the writes” | The reach analysis arms LimitViolated at a limited field's writes: a program writing one, whose failsafe names every arm but LimitViolated, is refused. | `refuse` |
| `vf0316b` | 316 | rule | “The prelude's `List` carries” | The prelude's List carries the ListLen rule on count and cap. | untestable [internal] no program may write a List's header, so the rule is visible only as the prelude's own rows and facts |
| `vf0317` | 317 | rule | “a name D-239 reserves” | ListLen is a name D-239 reserves: a user Rules block named ListLen is refused. | `refuse` |
| `vf0318` | 318 | rule | “built-in lengths of `string`, `cstring`, a slice and a `buffer` carry the same” | The built-in lengths carry the [0, 2^47] bound as a fact at every read. | untestable [z3] a fact shows only through z3's verdicts |
| `vf0321` | 321 | rule | “program may write a header” | No program may write a header: assigning a string's `.len` is refused. | `refuse` |
| `vf0330` | 330 | example | “```nitpick” | The example's divide (requires b != 0, ensures result > 0, passes 10) compiles, and divide(10, 2) returns 10. | `run:0` |
| `vf0339` | 339 | rule | “Nitpick automatically enforces these contracts at runtime” | Without the static verifier contracts are enforced at run time: divide(10, 0) traps RequiresViolated. | `trap:RequiresViolated` |
| `vf0339b` | 339 | rule | “the compiler translates these contracts into Z3 assertions” | With verification the contracts are translated into Z3 assertions and proven. | untestable [z3] the verified build; `--verify-contracts` is struck (§5) |
| `vf0342` | 342 | rule | “Every proposition” | A requires clause must be a bool: an int32 clause is NITPICK-TYPE-007. | `refuse:TYPE-007` |
| `vf0342b` | 342 | rule | “`ensures`” | An ensures clause must be a bool: `ensures result` over an int32 is NITPICK-TYPE-007. | `refuse:TYPE-007` |
| `vf0342c` | 342 | rule | “each `invariant` conjunct” | An invariant conjunct must be a bool: `invariant t` over an int32 is NITPICK-TYPE-007. | `refuse:TYPE-007` |
| `vf0343` | 343 | rule | “`prove`, `assert_static` — is a `bool`” | A prove proposition must be a bool: `prove(a)` over an int32 is NITPICK-TYPE-007. | `refuse:TYPE-007` |
| `vf0343b` | 343 | rule | “`assert_static`” | An assert_static proposition must be a bool: `assert_static(1i32)` is NITPICK-TYPE-007. | `refuse:TYPE-007` |
| `vf0344` | 344 | rule | “the SUCCESS value, typed `T`” | `result` is typed T: comparing an int32 function's result with an int64 is refused. | `refuse` |
| `vf0344b` | 344 | rule | “typed `T`, legal in” | `result` is legal in ensures alone: in a function body it is refused. | `refuse` |
| `vf0345` | 345 | rule | “`ensures` alone” | `result` is legal in ensures alone: in a requires it is refused. | `refuse` |
| `vf0345c` | 345 | rule | “so no binding can shadow it” | `result` is a keyword: a local named result is refused. | `refuse` |
| `vf0346` | 346 | rule | “the operand's value at the function's ENTRY” | `old(n)` is n's value at the function's entry: after the body adds 5 to n, `result == old(n) + 1` holds of `n - 4`. | `run:0` |
| `vf0346b` | 346 | rule | “legal in `ensures`” | `old(...)` is legal in ensures and invariant only: in a requires it is refused. | `refuse` |
| `vf0347` | 347 | rule | “never nested” | `old` is never nested: `old(old(a))` is refused. | `refuse` |
| `vf0348` | 348 | rule | “`result`, and only of a COPYABLE value” | `old` is never of result: `old(result)` is refused. | `refuse` |
| `vf0348b` | 348 | rule | “neither an owner (a `string`, a” | `old` is only of a copyable value: `old(s)` of a string (an owner) is refused. | `refuse` |
| `vf0349` | 349 | rule | “nor an address (a pointer, a slice)” | `old` is only of a copyable value: `old(s)` of a slice (an address) is refused. | `refuse` |
| `vf0350` | 350 | rule | “`main` and `failsafe` carry no contract (D-244)” | main carries no contract: a requires on main is refused. | `refuse` |
| `vf0350b` | 350 | rule | “`failsafe` carry no contract” | failsafe carries no contract: an ensures on failsafe is refused. | `refuse` |
| `vf0351` | 351 | rule | “fails` function may (D-241)” | A never fails function may carry contracts: one with a requires and an ensures compiles and runs. | `run:0` |
| `vf0354` | 354 | rule | “no `await`” | A contract may not contain await: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0355` | 355 | rule | “`move`, no” | A contract may not contain move: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0355b` | 355 | rule | “`relay`” | A contract may not contain relay: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0355c` | 355 | rule | “`?!`” | A contract may not contain `?!`: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0355d` | 355 | rule | “`?\|`” | A contract may not contain `?\|`: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0355e` | 355 | rule | “no `pick` expression” | A contract may not contain a pick expression: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0358` | 358 | rule | “a user function spelled `raw f(” | A contract may call a named pure never-fails user function spelled `raw f(...)`: accepted, and the call runs. | `run:0` |
| `vf0359` | 359 | rule | “that is **`pure`**” | A contract's callee must be pure: a never-fails function that is not pure is NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0359b` | 359 | rule | “a function value, a field” | A contract may not call a function value: NITPICK-TYPE-060. | `refuse:TYPE-060` |
| `vf0362` | 362 | rule | “`is_err(x)` is a predicate and passes” | `is_err(x)` passes in a contract: a requires over `!(is_err(t))` compiles and a call with a non-ERR value runs. | `run:0` |
| `vf0365` | 365 | rule | “a pure function may `fail`” | pure is orthogonal to never fails: a pure function may fail, and its failure reaches the caller. | `run:0` |
| `vf0367` | 367 | rule | “no `async`/`thread`” | A pure function may not be async: NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0367b` | 367 | rule | “no `move` parameter” | A pure function may not take a move parameter: NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0367c` | 367 | rule | “no callee” | A pure function may not call a function that is not pure: NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0370` | 370 | rule | “the clock” | A builtin that touches the clock is an effect: `mono_now()` in a pure function is NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0372` | 372 | rule | “no `wild`/`wildx` storage” | A pure function may not hold wild storage: NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0372b` | 372 | rule | “no owning local” | A pure function may not have an owning local: a string local is NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0373` | 373 | rule | “store that reaches memory the caller can see” | A pure function may not store to memory the caller can see: a write through a pointer parameter is NITPICK-TYPE-061. | `refuse:TYPE-061` |
| `vf0374` | 374 | rule | “impl keeps its trait method's `pure`” | An impl keeps its trait method's pure: an impl method dropping it is refused. | `refuse` |
| `vf0374b` | 374 | rule | “Purity never rides a function type” | Purity never rides a function type: a pure function calling a never-fails function value is refused. | `refuse` |
| `vf0377` | 377 | rule | “A contract violation is a TRAP” | A violated requires is a trap: RequiresViolated reaches failsafe. | `trap:RequiresViolated` |
| `vf0378` | 378 | rule | “`EnsuresViolated`” | A violated ensures is a trap: EnsuresViolated reaches failsafe. | `trap:EnsuresViolated` |
| `vf0378b` | 378 | rule | “`InvariantViolated`” | A violated loop invariant is a trap: InvariantViolated reaches failsafe. | `trap:InvariantViolated` |
| `vf0380` | 380 | rule | “A `requires` is checked at the CALLEE's” | A requires is checked at the callee's entry, every clause: with two requires clauses, violating the second traps RequiresViolated. | `trap:RequiresViolated` |
| `vf0381` | 381 | rule | “`<symbol>.req`” | A requires is checked in a generated predicate <symbol>.req. | `ir:^define [^\n]*@"npk\.vf0381\.half\.req"\(` |
| `vf0384` | 384 | rule | “therefore splits into `<symbol>.body`” | A sync function with a requires splits into <symbol>.body and its ordinary symbol (the checked entry). | `ir:^define [^\n]*@"npk\.vf0384\.half\.body"\(` |
| `vf0385` | 385 | rule | “or at state 0 of a coroutine” | A coroutine's requires is checked at state 0: awaiting it with a violating argument traps RequiresViolated. | `trap:RequiresViolated` |
| `vf0387` | 387 | rule | “indirect” | Every caller is covered, indirect too: calling a requires function through a function value with a violating argument traps RequiresViolated. | `trap:RequiresViolated` |
| `vf0387b` | 387 | rule | “through `dyn`” | Every caller is covered through dyn: a trait call with a violating argument traps RequiresViolated. | `trap:RequiresViolated` |
| `vf0388` | 388 | rule | “every return seam” | An ensures is checked at every return seam: the second of two `pass` points violating it traps EnsuresViolated. | `trap:EnsuresViolated` |
| `vf0388b` | 388 | rule | “and `return Result{” | An ensures is checked at a `return Result{...}` whose error field is 0: a violating value traps EnsuresViolated. | `trap:EnsuresViolated` |
| `vf0389` | 389 | rule | “is 0), before the value is stored” | An ensures is checked only on success (error field 0): a failing path is not checked, and the caller's `?\|` default is taken. | `run:0` |
| `vf0390` | 390 | rule | “`old(e)` a snapshot taken once at the body's start” | In a coroutine `old(v)` is a snapshot taken at the body's start: after the body adds 5, `result == old(v) + 1` holds of `v - 4`. | `run:0` |
| `vf0393` | 393 | rule | “a literal that is not positive refused by the checker” | failsafe's postcondition: an `exit` with a literal that is not positive is refused, REACH-004. | `refuse:REACH-004` |
| `vf0395` | 395 | rule | “re-enters it and ends the process at 70” | A computed non-positive failsafe exit is guarded: EnsuresViolated inside failsafe re-enters it and ends the process at 70. | `run:70` |
| `vf0397` | 397 | rule | “One `requires` row per CALL with a recorded callee” | One requires row per call with a recorded callee and one per function entry: two direct calls of a requires function make three rows. | `sh:0` |
| `vf0398` | 398 | rule | “`bypass` at a direct sync” | A direct sync call's requires row has the role `bypass`. | `sh:0` |
| `vf0400` | 400 | rule | “`held` at an `await` or through a `dyn`” | A requires row through dyn has the role `held`. | `sh:0` |
| `vf0405` | 405 | rule | “One `ensures` row per return point” | One ensures row per return point: a function with two `pass` points has two ensures rows. | `sh:0` |
| `vf0407` | 407 | rule | “A callee's `ensures` is KNOWLEDGE at every unwrap” | A callee's ensures is knowledge at every unwrap that continues only on success, never at `?\|`. | untestable [z3] knowledge shows only through z3's verdicts |
| `vf0410` | 410 | rule | “UNINTERPRETED FUNCTION” | A pure never-fails callee is an uninterpreted function in the obligations. | untestable [z3] the encoding shows only through z3's verdicts |
| `vf0413` | 413 | rule | “CONFORMANCE is two rows per impl method” | Conformance is two rows per impl method whose trait method carries a contract (role `conform`, no guard). | `sh:0` |
| `vf0417` | 417 | rule | “never a refusal: the impl's own entry traps the argument the trait admits” | An impl that strengthens its trait's requires is not refused; through the trait, an argument the trait admits and the impl does not traps RequiresViolated at the impl's entry. | `trap:RequiresViolated` |
| `vf0418` | 418 | rule | “A guard inside a clause (a division in a `requires`)” | A guard inside a requires clause is the function's own site in the predicate: dividing by a zero argument there traps DivByZero. | `trap:DivByZero` |
| `vf0422` | 422 | rule | “it has a row in every context the head's one check runs in” | A guard inside an invariant has a row per context of the head's check (entry, back edge, each continue): a division in an invariant of a loop with one continue has three div-zero rows. | `sh:0` |
| `vf0429` | 429 | rule | “PROGRAM-INVALID state, not a value” | A contract violation is a trap, never a Result: a violated requires traps RequiresViolated even when the caller offers a `?\|` default. | `trap:RequiresViolated` |
| `vf0437` | 437 | rule | “so it is never `never fails`” | A function with a requires is never `never fails`: declaring one is refused. | `refuse` |
| `vf0437b` | 437 | rule | “`raw` does not apply here” | `raw` does not apply to a call of a function with a requires (not never fails): it is refused. | `refuse` |
| `vf0439` | 439 | example | “```nitpick” | The example compiles and runs with §3's divide: `divide(10i32, 2i32) ?! 7tbb32` unwraps 10 and main exits 0. | `run:0` |
| `vf0453` | 453 | rule | “support an `invariant` clause” | A counted `loop` supports an invariant, checked: an accumulator leaving it traps InvariantViolated. | `trap:InvariantViolated` |
| `vf0453b` | 453 | rule | “`while`” | A `while` supports an invariant, checked: violating it traps InvariantViolated. | `trap:InvariantViolated` |
| `vf0453c` | 453 | rule | “`till`” | A `till` supports an invariant, checked: violating it traps InvariantViolated. | `trap:InvariantViolated` |
| `vf0453d` | 453 | rule | “`when`” | A `when` supports an invariant, checked: violating it traps InvariantViolated. | `trap:InvariantViolated` |
| `vf0453e` | 453 | rule | “BEFORE the invariant” | A while/when states `decreases E` or `unbounded` before the invariant: the invariant first is refused. | `refuse` |
| `vf0455` | 455 | example | “```nitpick” | The example sum_range (requires n > 0, ensures result >= 0, a while with decreases and a two-conjunct invariant) compiles, and sum_range(3) is 3. | `run:0` |
| `vf0470` | 470 | rule | “the Z3 solver verifies the inductive step” | The solver verifies the invariant's inductive step. | untestable [z3] a verdict; `--verify-contracts` is struck (§5) |
| `vf0473` | 473 | rule | “a counted loop's invariant may name `$`” | A counted loop's invariant may name `$` (the counter): `invariant $ < 3` traps InvariantViolated when the counter reaches 3. | `trap:InvariantViolated` |
| `vf0474` | 474 | rule | “`old(expr)` — the value at the FUNCTION's entry” | An invariant's `old(n)` is n's value at the function's entry: with n lowered by 3 before the loop, `i <= old(n)` holds for i up to 4. | `run:0` |
| `vf0477` | 477 | rule | “CHECKED AT THE LOOP HEAD, before” | The invariant is checked at the loop head before the condition: an invariant false at entry traps even when the condition is false and the body never runs. | `trap:InvariantViolated` |
| `vf0478` | 478 | rule | “at entry and after every iteration” | The invariant is checked after every iteration, the last included (the exit is a head visit): an invariant only the final iteration breaks traps. | `trap:InvariantViolated` |
| `vf0479` | 479 | rule | “for every loop form” | The invariant is checked for every loop form, a range for included: violating it traps InvariantViolated. | `trap:InvariantViolated` |
| `vf0481` | 481 | rule | “the ENTRY row at the loop statement” | An invariant's rows: the entry row, the preservation row and one per continue: a while with one continue has three invariant rows. | `sh:0` |
| `vf0484` | 484 | rule | “Inside the body the invariant and” | Inside the body the invariant and the condition are hypotheses; after a loop nothing breaks out of, the invariant and the negated condition. | untestable [z3] hypotheses show only through z3's verdicts |
| `vf0492` | 492 | rule | “(descending, `limit < $ <= start`)” | A descending counted loop's `$` lies in limit < $ <= start: loop(5, 0, 1) visits 5, 4, 3, 2, 1. | `run:0` |
| `vf0496` | 496 | rule | “its bounds captured at entry” | A range for's bounds are captured at entry: raising the bound's variable inside the body does not add iterations. | `run:0` |
| `vf0499` | 499 | rule | “a name a bound mentions moves nothing” | A counted loop's bounds are captured as the emitter's slots hold them: a body assigning the bound's variable moves nothing. | `run:0` |
| `vf0500` | 500 | rule | “the compare at the loop's entry is its guard” | A computed step's positivity is guarded at the loop's entry: a zero step at run time traps BadStep. | `trap:BadStep` |
| `vf0500b` | 500 | rule | “`loop-step` row (S-46, D-270)” | A computed step is one `loop-step` row; a literal step has none. | `sh:0` |
| `vf0501` | 501 | rule | “a literal step is the checker's (TYPE-068, D-022)” | A literal step that is not positive is the checker's: a zero literal step is TYPE-068. | `refuse:TYPE-068` |
| `vf0502` | 502 | rule | “An invariant naming `$` or the binding is decided on the” | An invariant naming `$` or the for binding is decided on the merits. | untestable [z3] a verdict |
| `vf0509` | 509 | example | “```nitpick” | Both shapes compile and run: a while with `decreases n - i` then its invariant, and `while (true) unbounded` (left here by break). | `run:0` |
| `vf0514` | 514 | rule | “is a plain integer (`intN`/`uintN`, TYPE-073)” | A loop measure is a plain integer: a flt64 measure is TYPE-073. | `refuse:TYPE-073` |
| `vf0514b` | 514 | rule | “TYPE-073” | A loop measure is a plain integer: a bool measure is TYPE-073. | `refuse:TYPE-073` |
| `vf0515` | 515 | rule | “a contract expression (§3's admission, TYPE-060)” | A measure is a contract expression: calling a never-fails function that is not pure in it is TYPE-060. | `refuse:TYPE-060` |
| `vf0516` | 516 | rule | “neither `result` nor `old(” | `old(...)` does not exist in a measure: refused. | `refuse` |
| `vf0516b` | 516 | rule | “`result`” | `result` does not exist in a measure: refused. | `refuse` |
| `vf0517` | 517 | rule | “BEFORE `invariant`, once” | The clause comes before invariant: `invariant ... decreases ...` is TYPE-072. | `refuse:TYPE-072` |
| `vf0517b` | 517 | rule | “once” | The clause comes once: two `decreases` are TYPE-072. | `refuse:TYPE-072` |
| `vf0517c` | 517 | rule | “`unbounded` and `decreases` never both” | `unbounded` and `decreases` never both: TYPE-072. | `refuse:TYPE-072` |
| `vf0519` | 519 | rule | “each of those shapes is TYPE-072 by name” | A `for` takes neither clause: `for ... decreases` is TYPE-072. | `refuse:TYPE-072` |
| `vf0519b` | 519 | rule | “TYPE-072” | A `loop` takes neither clause: `loop ... unbounded` is TYPE-072. | `refuse:TYPE-072` |
| `vf0519c` | 519 | rule | “by name” | A `till` takes neither clause: `till ... decreases` is TYPE-072. | `refuse:TYPE-072` |
| `vf0520` | 520 | rule | “`while`/`when` with NO clause” | A while with no clause is TYPE-072. | `refuse:TYPE-072` |
| `vf0520b` | 520 | rule | “NO clause” | A when with no clause is TYPE-072. | `refuse:TYPE-072` |
| `vf0522` | 522 | rule | “at the top of the body, each time the” | The measure is checked at the top of the body each time the condition holds: a negative measure of a loop whose condition is false at entry is never checked. | `run:0` |
| `vf0524` | 524 | rule | “zero traps `DecreasesViolated` (4119)” | A signed measure below zero traps DecreasesViolated at the first visit. | `trap:DecreasesViolated` |
| `vf0525` | 525 | rule | “not below the previous visit's traps the same” | From the second visit on, a measure not below the previous visit's traps DecreasesViolated. | `trap:DecreasesViolated` |
| `vf0525b` | 525 | rule | “never a” | Never a sentinel: a signed measure starting at INT32_MAX is not mistaken for the previous visit's. | `run:0` |
| `vf0526` | 526 | rule | “sentinel (DEF-69)” | Two slots per loop, never a sentinel: an unsigned measure starting at UINT32_MAX is not mistaken for the previous visit's. | `run:0` |
| `vf0527` | 527 | rule | “frame slots at roles 42 and 43” | The previous measure and the first-visit flag are allocas in a sync body and frame slots 42 and 43 in a coroutine. | untestable [internal] the slots' placement; their behaviour is vf0525/vf0526 |
| `vf0528` | 528 | rule | “`continue` re-enters the” | `continue` re-enters the head and is checked: a continue that leaves the measure unchanged traps DecreasesViolated at the next visit. | `trap:DecreasesViolated` |
| `vf0529` | 529 | rule | “`break` and `exit` leave without one” | `break` leaves without a check: a body that grows the measure and breaks runs clean. | `run:0` |
| `vf0530` | 530 | rule | “emits nothing.” | `unbounded` emits nothing. | untestable [unobservable] an unbounded loop has no measure to check and no clause-less twin to compare against (a while with no clause is TYPE-072) |
| `vf0531` | 531 | rule | “the ENTRY row at the loop statement, `E >= 0`” | terminate rows: an entry row (signed measures only), a preservation row, and one per continue: a signed loop has two, an unsigned one one, a signed one with a continue three. | `sh:0` |
| `vf0537` | 537 | rule | “compares become one `llvm.assume` each only when EVERY row is discharged” | The check's compares become assumes only when every terminate row is discharged. | untestable [z3] needs a manifest with the rows discharged |
| `vf0545` | 545 | rule | “What discharges” | A counter's `bound - v` and a halving n under n > 0 discharge. | untestable [z3] verdicts |
| `vf0548` | 548 | rule | “`List`'s `count` as the bound has no length term” | A List's count as a loop's bound has no length term: the terminate rows are unencoded (0 in rows.txt). | `sh:0` |
| `vf0551` | 551 | rule | “function's `decreases E` is a contract of kind `decreases`” | A function's decreases is a contract checked at recursive calls: fact(5) with `decreases n` runs and returns 120. | `run:0` |
| `vf0552` | 552 | rule | “optional (D-304 (5))” | A function's measure is optional: a self-recursion without one compiles and runs. | `run:0` |
| `vf0552b` | 552 | rule | “and checked at every call inside the” | The measure is checked at every call inside the recursive group: is_even(n) calling is_odd(n) (no decrease across the pair) traps DecreasesViolated. | `trap:DecreasesViolated` |
| `vf0554` | 554 | rule | “Tarjan's components” | The recursive groups are Tarjan's components over the checker's call edges, one predicate for emitter and encoder. | untestable [internal] the pass's algorithm; its outcomes are vf0552b/vf0557/vf0562/vf0564 |
| `vf0557` | 557 | rule | “a call through a `dyn` receiver or a function value is” | A call through a function value is no edge: a function whose only recursion is through a function value has no cycle, so its decreases is TYPE-075. | `refuse:TYPE-075` |
| `vf0562` | 562 | rule | “TYPE-074: every function of a cyclic” | Every function of a cyclic group states decreases if any member does: a pair with one measured member is TYPE-074. | `refuse:TYPE-074` |
| `vf0564` | 564 | rule | “TYPE-075: a `decreases` on a function whose group has no cycle checks” | A decreases on a function whose group has no cycle is TYPE-075. | `refuse:TYPE-075` |
| `vf0565` | 565 | rule | “TYPE-073, for functions: the measure is at most 64 bits wide” | A function's measure is at most 64 bits wide: an int128 measure is TYPE-073. | `refuse:TYPE-073` |
| `vf0568` | 568 | rule | “compares only with itself and keeps any width” | A loop's measure keeps any width: an int128 loop measure is accepted and checked. | `run:0` |
| `vf0569` | 569 | rule | “a generated predicate `<sym>.measure(params)” | The check is a generated predicate <sym>.measure(params) returning i128. | `ir:^define [^\n]*\bi128 @"npk\.vf0569\.fact\.measure"\(` |
| `vf0572` | 572 | rule | “the body's ENTRY stores” | The body's entry stores m0 after the entry checks and before the old snapshots. | untestable [internal] an ordering inside the emitted entry that no program here can isolate |
| `vf0577` | 577 | rule | “then `m0 >= 0`” | At a recursive call `m0 >= 0` is checked: step(-1), whose measure is negative at entry, traps DecreasesViolated at its recursive call. | `trap:DecreasesViolated` |
| `vf0578` | 578 | rule | “and `m1 < m0` as one verdict with ONE trap `DecreasesViolated`” | At a recursive call `m1 < m0` is checked: a self-call with an unchanged argument traps DecreasesViolated. | `trap:DecreasesViolated` |
| `vf0579` | 579 | rule | “predicate holds no snapshot” | A recursive call inside a requires clause or a measure is not checked. | untestable [internal] a recursive call inside a generated predicate recurses through the predicate itself; no program here isolates the missing check from that recursion |
| `vf0580` | 580 | rule | “`unbounded` is a” | `unbounded` is a loop's word only: on a function it is refused. | `refuse` |
| `vf0582` | 582 | rule | “the `terminate` CALL row” | A recursive call is one terminate row of the caller's, role `guard`. | `sh:0` |
| `vf0588` | 588 | rule | “The measure's own guards (an overflow inside `E`) have ONE row each” | The measure's own guards have one row each at the function's entry, under the parameters' range axioms alone. | untestable [z3] which hypotheses a row carries shows only through verdicts |
| `vf0595` | 595 | rule | “row (D-305” | One stack-depth row per cyclic group, `d` (derived) in rows.txt: a self-recursion and a mutual pair make two. | `sh:0` |
| `vf0598` | 598 | rule | “its verdict is DERIVED by both runners” | The stack-depth verdict is derived by the runners from the group's terminate call rows. | untestable [z3] the runners' derivation needs z3's verdicts |
| `vf0605` | 605 | rule | “It elides nothing” | The stack-depth row elides nothing: the stack check stays in every build. | untestable [z3] a statement about the verified build's elision |
| `vf0606` | 606 | rule | “the compiler's own groups state no measure” | The compiler's own recursive groups state no measure, so their rows are open. | untestable [tree] about the compiler's own source |
| `vf0607` | 607 | rule | “`index.txt` carries per file the function's cyclic group” | index.txt carries per file the function's cyclic group (0 for none) and whether it states a measure. | `sh:0` |
| `vf0610` | 610 | rule | “`fact(n) decreases n` calling `fact(n - 1)`” | fact's call row discharges on the path condition; step under n != 0 leaves m0 >= 0 open. | untestable [z3] verdicts |
| `vf0614` | 614 | rule | “every `while` and `when` of the” | Every while and when of the compiler's tree (977 loops) states its clause. | untestable [tree] about the compiler's own tree |
| `vf0618` | 618 | rule | “PROVE monotone (392)” | The sweep tool wrote 392 loops' measures; the others were read into decreases_read.txt. | untestable [tree] about the compiler's own tree and tools |
| `vf0634` | 634 | rule | “call a `pure never fails` function (TYPE-060)” | A measure may call a pure never-fails function: accepted, and the loop runs. | `run:0` |
| `vf0638` | 638 | rule | “a measure that does not shrink” | The compile-time evaluator checks a measure of a loop it runs: one that does not shrink is a counterexample, TYPE-069. | `refuse:TYPE-069` |
| `vf0638b` | 638 | rule | “or a signed one below zero” | The compile-time evaluator refuses a signed measure below zero, TYPE-069. | `refuse:TYPE-069` |
| `vf0639` | 639 | rule | “Every `failsafe` in the tree” | Every failsafe in the compiler's tree names DecreasesViolated. | untestable [tree] about the compiler's own tree |
| `vf0644` | 644 | rule | “1,183 `terminate` row sites in the compiler's own build” | The measurement over the compiler's own build: 1,183 terminate row sites, 684 discharged, 499 open. | untestable [tree] a measurement of the compiler's own build |
| `vf0667` | 667 | rule | “116, all `open`” | The compiler's stack-depth rows: 116, all open. | untestable [tree] a measurement of the compiler's own build |
| `vf0674` | 674 | rule | “the by-value aggregate carries” | Since D-317 a by-value aggregate carries an identity and its fields are functions of it. | untestable [z3] the encoder's aggregate terms show only through verdicts |
| `vf0676` | 676 | rule | “1,188 `terminate` row sites, 753 discharged, 435 open” | After D-317: 1,188 terminate row sites, 753 discharged, 435 open. | untestable [tree] a measurement of the compiler's own build |
| `vf0695` | 695 | rule | “None of the flags below exists in `npkc`” | None of the tabulated verification flags exists in npkc: each is refused. | `sh:0` |
| `vf0696` | 696 | rule | “PROJECT's, in `nitpick.toml`'s `[verify]`” | Verification configuration is the project's, in nitpick.toml's [verify], read by every invocation. | untestable [tool] needs a package tree and `npkg verify` |
| `vf0702` | 702 | rule | “a knob that would re-enable it is refused” | The wall-clock timeout is disabled; a [verify] knob that would re-enable it is refused by name. | untestable [tool] a package tree under `npkg`; the knob's name is not given |
| `vf0706` | 706 | rule | “`--prove-report` and `--debug-z3` are `npkg verify --explain`” | The report and the SMT dump are `npkg verify --explain` and build/verify/obl/. | untestable [z3] needs `npkg verify` with the pinned z3 |
| `vf0714` | 714 | row | “`--verify`” | The flag --verify is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0715` | 715 | row | “`--verify-contracts`” | The flag --verify-contracts is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0716` | 716 | row | “`--verify-overflow`” | The flag --verify-overflow is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0717` | 717 | row | “`--verify-concurrency`” | The flag --verify-concurrency is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0718` | 718 | row | “`--verify-memory`” | The flag --verify-memory is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0719` | 719 | row | “`--verify-level=N`” | The flag --verify-level=2 is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0720` | 720 | row | “`--smt-opt`” | The flag --smt-opt is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0721` | 721 | row | “`--smt-manifest=<path>`” | The flag --smt-manifest=nitpick.obligations is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0722` | 722 | row | “`--smt-timeout=N`” | The flag --smt-timeout=5000 is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0723` | 723 | row | “`--prove-report`” | The flag --prove-report is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0724` | 724 | row | “`--debug-z3`” | The flag --debug-z3 is struck (the banner at 694-710): npkc does not accept it. | `sh:0` |
| `vf0732` | 732 | row | “\| `0` \|” | Verification level 0 is struck with `--verify-level` (694-710): npkc does not accept `--verify-level=0`. | `sh:0` |
| `vf0733` | 733 | row | “\| `1` \|” | Verification level 1 is struck with `--verify-level` (694-710): npkc does not accept `--verify-level=1`. | `sh:0` |
| `vf0734` | 734 | row | “\| `2` \|” | Verification level 2 is struck with `--verify-level` (694-710): npkc does not accept `--verify-level=2`. | `sh:0` |
| `vf0735` | 735 | row | “\| `3` \|” | Verification level 3 is struck with `--verify-level` (694-710): npkc does not accept `--verify-level=3`. | `sh:0` |
| `vf0746` | 746 | rule | “Invoked during compilation (`npkc --verify`)” | Z3 is invoked during compilation by `npkc --verify`. | untestable [z3] needs z3; and §5 (694-710) says the flag does not exist in npkc |
| `vf0749` | 749 | rule | “Covers: `limit<Rules>` constraints, function contracts, loop invariants,” | The obligations cover limit, contracts, invariants, prove/assert_static, overflow and index disjointness: one program using each yields a row of each kind. | `sh:0` |
| `vf0750` | 750 | rule | “memory safety,” | Z3 covers memory safety and concurrency. | untestable [vague] no obligation kind of §7b's catalogue names memory safety or concurrency; the sentence names no checkable row |
| `vf0755` | 755 | rule | “Used offline during language development, not during compilation” | The K framework proves the language's metatheory offline, not during compilation. | untestable [tree] about the project's development process |
| `vf0760` | 760 | rule | “`k-semantics/nitpick.k`” | The operational semantics live in k-semantics/nitpick.k with proof claims in k-semantics/proofs/. | untestable [tree] about the repository's files |
| `vf0788` | 788 | rule | “moves a page RW” | wildx_seal moves a page RW to RX with no reverse; a page is never writable and executable at once. | untestable [unobservable] page permissions are not observable without raw memory access |
| `vf0790` | 790 | rule | “refuses any write after seal” | A write to a wildx page after its seal is refused, NITPICK-WILDX-001. | `refuse:WILDX-001` |
| `vf0791` | 791 | rule | “any execute before it (`NITPICK-WILDX-002`)” | Executing a wildx page before its seal is refused, NITPICK-WILDX-002. | `refuse:WILDX-002` |
| `vf0793` | 793 | rule | “The lifecycle is a state machine” | The lifecycle alloc, write, seal, execute, free is accepted and runs: the page's `mov eax, 7; ret` returns 7. | `run:0` |
| `vf0794` | 794 | rule | “double-free” | A double free of a wildx page is refused (a free is a move). | `refuse` |
| `vf0794b` | 794 | rule | “use-after-free” | Executing a wildx page after its free is refused (a use after a move). | `refuse` |
| `vf0794c` | 794 | rule | “seal-after-free” | Sealing a wildx page after its free is refused. | `refuse` |
| `vf0795` | 795 | rule | “no-live-pages-at-exit” | No live pages at exit, from the <wild-live> registry: `exit 0` with a live wildx page traps WildLeak. | `trap:WildLeak` |
| `vf0796` | 796 | rule | “Guard pages turn an” | Guard pages turn a wildx over/underrun into a fault. | untestable [unobservable] reaching a guard page needs pointer arithmetic past the checked indexing |
| `vf0797` | 797 | rule | “the page is placed by the kernel's mmap” | A wildx page is placed by the kernel's mmap randomisation (ASLR). | untestable [platform] the kernel's placement policy |
| `vf0802` | 802 | rule | “validated by Nikola's sandbox and oracle rounds” | The generated bytes' contents are validated by Nikola's sandbox and oracle rounds, not these backends. | untestable [vague] about another project's process |
| `vf0805` | 805 | rule | “will not reach the” | A program containing wildx will not reach the highest DO-178C / IEC 61508 / ISO 26262 levels. | untestable [vague] a certification statement |
| `vf0808` | 808 | rule | “**`--extra-picky=no-wildx`**” | `--extra-picky=no-wildx` excludes runtime code generation: a program without wildx compiles under it and one using wildx does not. | `sh:0` |
| `vf0811` | 811 | rule | “It is a rule separate from `no-wild`” | no-wildx is a rule separate from no-wild: a program using `wild` (not wildx) compiles under no-wildx and not under no-wild. | `sh:0` |
| `vf0819` | 819 | rule | “borrows cannot cross a thread spawn or” | Borrows cannot cross an await: a $$i claim held by a pointer local across an await is refused. | `refuse` |
| `vf0820` | 820 | rule | “tasks do not migrate between threads” | Tasks do not migrate between threads. | untestable [timing] a scheduling property; no single run can show a migration never happens |
| `vf0821` | 821 | rule | “never move memory or reuse slots” | Shared arenas never move memory or reuse slots. | untestable [unobservable] a program cannot observe an arena's slot reuse without raw addresses |
| `vf0828` | 828 | rule | “acquisition must strictly increase” | Acquisition must strictly increase: holding a level-5 mutex and acquiring a level-3 one is refused. | `refuse` |
| `vf0828b` | 828 | rule | “strictly” | Strictly: acquiring a second mutex of the same level while holding the first is refused. | `refuse` |
| `vf0828c` | 828 | rule | “Circular wait is impossible” | Increasing acquisition is accepted: level 3 then level 5 compiles and runs. | `run:0` |
| `vf0829` | 829 | rule | “A whole-program analysis computes each function's transitive” | The analysis is whole-program: holding level 3 and calling a function that acquires level 1 is refused. | `refuse` |
| `vf0830` | 830 | rule | “dynamically dispatched methods declare a maximum level” | A dynamically dispatched method declares a maximum level and implementations are checked against it: an impl acquiring 9 under `acquires <= 3` is refused. | `refuse` |
| `vf0831` | 831 | rule | “an undeclared method may not acquire at all” | An undeclared dynamically dispatched method may not acquire at all: an impl of a trait method with no level acquiring one is refused. | `refuse` |
| `vf0834` | 834 | rule | “operation takes a deadline and returns `Result`” | Every blocking operation takes a deadline: an acquire without one is refused. | `refuse` |
| `vf0836` | 836 | rule | “surfaces as a” | What the analysis cannot cover surfaces as a timeout error at a known point. | untestable [timing] needs a contended acquire whose deadline expires |
| `vf0839` | 839 | rule | “The flag is documented as verifying” | The flag verifies data-race and lock-order freedom, not deadlock freedom. | untestable [vague] about a struck flag's documentation |
| `vf0848` | 848 | rule | “Every kind the manifest's `kind` column may carry, exhaustively” | The catalogue lists every obligation kind exhaustively: every row the compiler writes to rows.txt carries one of its 22 kinds. | `sh:0` |
| `vf0857` | 857 | row | “\| `div-zero` \| the divisor of an integer `/` or `%` is not zero” | An integer `/` or `%` by a computed divisor is one `div-zero` row: one each in a signed `/`, a signed `%` and an unsigned `/`. | `sh:0` |
| `vf0857b` | 857 | row | “\| yes \| 1.5.0 \|” | `div-zero` has a guard: in the plain build an integer `%` by a computed zero traps DivByZero. | `trap:DivByZero` |
| `vf0857c` | 857 | row | “a `simd` division's any-lane guard is ONE row over the lanes' conjunction (D-282)” | A `simd<int32, 4>` division by a computed vector has ONE `div-zero` row, not one per lane. | `sh:0` |
| `vf0858` | 858 | row | “\| `div-min` \|” | A signed integer division has one `div-min` row; an unsigned division has none. | `sh:0` |
| `vf0858b` | 858 | row | “a signed division is not `INT_MIN / -1` (D-142)” | `div-min` has a guard: the int32 minimum divided by -1 traps DivOverflow in the plain build. | `run:98` (M10 `v05_min_div_minus_one`) |
| `vf0858c` | 858 | row | “one row over the lanes for a signed-element `simd` (D-282)” | A signed-element `simd` division has ONE `div-min` row over the lanes; an unsigned-element one has none. | `sh:0` |
| `vf0859` | 859 | row | “\| `overflow` \| a plain-integer `+ - *` or negation stays in range (D-210)” | Each plain-integer `+`, `-`, `*` and negation over computed operands is one `overflow` row at its own node: `a + b` one, `-a` one, `(a + b) * c` two, a compound `x += b` one. | `sh:0` |
| `vf0859b` | 859 | row | “ONE row over the lanes for a `simd` integer operation” | A `simd<int32, 4>` `+` of computed vectors is ONE `overflow` row, not one per lane. | `sh:0` |
| `vf0859c` | 859 | row | “ONE with N-1 traps for an integer `.sum()`” | An integer `.sum()` of a `simd<int32, 4>` is ONE `overflow` row whose traps field is 3 (N-1). | `sh:0` |
| `vf0859d` | 859 | row | “a node the folder writes as its constant has no guard and no row (D-310)” | `2i32 + 3i32`, which the folder writes as its constant, has no `overflow` row. | `sh:0` |
| `vf0859e` | 859 | row | “\| yes \| 1.5.8b step 3 \|” | `overflow` has a guard: a plain int32 `+` past the maximum traps IntOverflow in the plain build. | `run:93` (M10 `o01_int32_add`) |
| `vf0859f` | 859 | row | “or negation stays in range (D-210)” | Negating the int32 minimum traps IntOverflow. | `run:93` (M10 `o04_int32_negate_min`) |
| `vf0860` | 860 | row | “\| `bounds` \| an index is inside its array, slice, buffer or `List`” | A computed index into a fixed array and into a slice is one `bounds` row each. | `sh:0` |
| `vf0860b` | 860 | row | “ONE row for a range slice's pair (`lo <= hi <= len`) at the RANGE's node” | A range slice `xs[lo...hi]` with computed bounds is ONE `bounds` row for the pair. | `sh:0` |
| `vf0860c` | 860 | row | “`0 <= i < len` at every checked element access” | The element check is `0 <= i < len`: a negative index traps OutOfBounds. | `run:94` (M10 `a04_index_negative`) |
| `vf0860d` | 860 | row | “\| yes \| 1.5.8b step 5” | `bounds` has a guard: an index past the end of an array traps OutOfBounds. | `run:94` (M10 `a03_index_past_end`) |
| `vf0860e` | 860 | row | “ONE row at each call of `string_from_bytes(p, len)`” | A call of `string_from_bytes(p, len)` is ONE `bounds` row, keyed on the call. | `sh:0` |
| `vf0860f` | 860 | row | “`0 <= len <= 2^47`, the emitter's guard read back” | The emitter guards `string_from_bytes(p, len)` with `0 <= len <= 2^47`: a length of 2^47 + 1 traps (the `bounds` code, OutOfBounds) before any byte is read. | `trap:OutOfBounds` |
| `vf0860g` | 860 | row | “`0 <= len <= 2^47`” | The same guard's lower half: `string_from_bytes(p, -1)` traps OutOfBounds. | `trap:OutOfBounds` |
| `vf0860h` | 860 | row | “a discharged row elides the guard into one `llvm.assume`” | In the verified build a discharged `string_from_bytes` row replaces its guard with exactly one `llvm.assume` and no OutOfBounds trap. | `sh:0` |
| `vf0860i` | 860 | row | “the length is the term `(\|npk.len\| base)` wherever it is named” | A loop over `xs.len` indexing `xs[i]` states the length as `\|npk.len\|` in its obligation file. | `sh:0` |
| `vf0860j` | 860 | row | “so a loop written over `xs.len` or `l.count` proves the accesses inside it” | An access inside a loop bounded by `xs.len` or `l.count` is a discharged row. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0860k` | 860 | row | “a fixed array's length is its type's constant” | A fixed array's length enters the goal as its type's constant. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0861` | 861 | row | “\| `cast-range` \| a float's `=>!` cast to an integer has an integer meaning (D-306)” | A `flt64 =>! int32` is one `cast-range` row. | `sh:0` |
| `vf0861b` | 861 | row | “the value is not NaN or an infinity” | A NaN's `=>!` to an integer traps CastRange. | `run:112` (M10 `c11_float_nan_to_int_traps`) |
| `vf0861c` | 861 | row | “lies inside the target” | A float whose truncation the target cannot hold (3e9 to int32) traps CastRange. | `run:112` (M10 `c12_float_too_big_to_int_traps`) |
| `vf0861d` | 861 | row | “its truncation toward zero” | The cast truncates toward zero (3.7 is 3, -3.7 is -3). | `run:0` (M10 `c10_float_to_int_truncates`) |
| `vf0861e` | 861 | row | “the two ordered compares before the conversion, `CastRange`” | An infinity's `=>!` to int32 traps CastRange. | `trap:CastRange` |
| `vf0861f` | 861 | row | “its truncation toward zero lies inside the target” | It is the TRUNCATION that must fit: -2147483648.5 and 2147483647.5 cast to int32 give the minimum and the maximum without trapping. | `run:0` |
| `vf0861g` | 861 | row | “a `simd` cast's any-lane guard is one row over the lanes” | A `simd<flt64, 4> =>! simd<int32, 4>` is ONE `cast-range` row. | `sh:0` |
| `vf0862` | 862 | row | “\| `exhaustive` \| a `pick` covers its domain (checker-discharged)” | A `pick` statement is one `exhaustive` row, decided by the checker (`c` in rows.txt's fifth field). | `sh:0` |
| `vf0862b` | 862 | row | “(checker-discharged) \| no \| 1.5.4 \|” | The checker decides coverage: a `pick` over int32 with no arm for most values and no `(*)` is refused. | `refuse` |
| `vf0863` | 863 | row | “\| `requires` \| a callee's precondition holds at the call (D-221)” | A call of a function with a `requires` is one `requires` row in the caller. | `sh:0` |
| `vf0863b` | 863 | row | “\| `requires` \| a callee's precondition holds at the call (D-221) \| yes \|” | `requires` has a guard: calling with an argument that breaks the precondition traps RequiresViolated in the plain build. | `trap:RequiresViolated` |
| `vf0864` | 864 | row | “\| `ensures` \|” | A postcondition is checked at each return: a function with two `pass` seams and an `ensures` has two `ensures` rows. | `sh:0` |
| `vf0864b` | 864 | row | “a body's postcondition holds at its return (D-221)” | `ensures` has a guard: a return that breaks the postcondition traps EnsuresViolated in the plain build. | `trap:EnsuresViolated` |
| `vf0865` | 865 | row | “\| `invariant` \| a loop invariant holds at entry and is preserved (D-221)” | A `while` with an `invariant` and no `continue` has two `invariant` rows: the entry and the preservation. | `sh:0` |
| `vf0865b` | 865 | row | “a loop invariant holds at entry and is preserved” | `invariant` has a guard: a body that breaks the invariant traps InvariantViolated at the next head visit. | `trap:InvariantViolated` |
| `vf0866` | 866 | row | “\| `limit` \| a `limit<Rules>` binding satisfies its rule at every write point (D-220)” | A limited binding's initial write and a later assignment are one `limit` row each. | `sh:0` |
| `vf0866b` | 866 | row | “\| yes \| 1.5.2; fields 1.5.8b step 6 \|” | `limit` has a guard: an assignment that breaks the rule traps LimitViolated in the plain build. | `trap:LimitViolated` |
| `vf0866c` | 866 | row | “so a write to a limited field of a limited binding is two rows at two keys” | Assigning a limited field of a limited binding adds two `limit` rows (the field's, keyed on the written expression, and the root's, keyed on the statement), at two distinct sites. | `sh:0` |
| `vf0866d` | 866 | row | “an assignment through any path including a pointer's” | A write to a limited field through a pointer is a `limit` row, as the struct literal's value for it is. | `sh:0` |
| `vf0867` | 867 | row | “\| `limit-subsume` \| one `Rules` implies another at a boundary (D-220)” | A direct call of a sync callee with a limited parameter is one `limit-subsume` row in the caller. | `sh:0` |
| `vf0867b` | 867 | row | “at a direct call of a sync callee” | A call of an ASYNC callee with a limited parameter has no `limit-subsume` row. | `sh:0` |
| `vf0867c` | 867 | row | “\| yes \| 1.5.2 \|” | `limit-subsume`'s guard is the callee's entry check: calling a limited parameter with a value outside its rule traps LimitViolated in the plain build. | `trap:LimitViolated` |
| `vf0868` | 868 | row | “\| `terminate` \| a `while`/`when` loop's `decreases E` measure is at least zero at every head visit” | A `while` with a signed `decreases` measure and no `continue` has two `terminate` rows: the entry row and the preservation row. | `sh:0` |
| `vf0868b` | 868 | row | “an unsigned one cannot be below zero and records no such row” | A loop whose measure is unsigned records no entry row: one `terminate` row (the preservation). | `sh:0` |
| `vf0868c` | 868 | row | “one per `continue` re-entering the loop” | Each `continue` that re-enters the loop adds one `terminate` row: a signed loop with one `continue` has three. | `sh:0` |
| `vf0868d` | 868 | row | “the head's check, `DecreasesViolated`” | `terminate` has a guard: a measure that does not decrease between head visits traps DecreasesViolated in the plain build. | `trap:DecreasesViolated` |
| `vf0868e` | 868 | row | “the callee's measure at the arguments below the caller's at entry with the caller's at least zero” | A recursive call inside a group whose members state `decreases` is one `terminate` row of the caller's at the call site. | `sh:0` |
| `vf0868f` | 868 | row | “the check before the call, one trap” | A recursive call whose argument's measure is not below the caller's traps DecreasesViolated before the call. | `trap:DecreasesViolated` |
| `vf0868g` | 868 | row | “a recursive call inside a `requires` clause or a measure has no check and an `unencoded` row with no trap” | A recursive call inside a `requires` clause or a measure is an `unencoded` row with no trap. | untestable [vague] the text gives no spelling of a recursive call inside a clause or a measure (a pure, measured callee inside its own group's contract) that this extractor has seen compile |
| `vf0869` | 869 | row | “\| `stack-depth` \| the recursion depth is bounded (the audit's G-6 row; D-305 (7))” | One `stack-depth` row per recursive group with a cycle, derived (`d` in rows.txt's fifth field): a self-recursive function and a mutual pair give two rows, both `d`. | `sh:0` |
| `vf0869b` | 869 | row | “in the first member the emission reaches” | A group's `stack-depth` row sits in the file of its first member the emission reaches. | untestable [internal] which member the emission reaches first is the emitter's order, which the text does not fix |
| `vf0869c` | 869 | row | “DERIVED by the runners from the group's `terminate` call rows” | The row's verdict is derived by the runners: `discharged` when every member states `decreases` and every call row is discharged, `open` otherwise. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0869d` | 869 | row | “no query, no guard, elides nothing (the stack check stays in every build)” | A `stack-depth` row elides nothing: the stack check stays in the verified build. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0870` | 870 | row | “\| `err-exit` \| the `TbbErr` guard's condition (D-144 as amended, D-278)” | A comparison of two computed `tbb32` values is one `err-exit` row. | `sh:0` |
| `vf0870b` | 870 | row | “neither operand is ERR at a comparison on a twisted value” | Comparing a `tbb8` holding ERR traps TbbErr. | `run:110` (M10 `m12_tbb_compare_on_err_traps`) |
| `vf0870c` | 870 | row | “the operand is not ERR at a cast out of its family (both spellings)” | An ERR `tbb8` cast out of its family with `=>!` traps TbbErr. | `trap:TbbErr` |
| `vf0870d` | 870 | row | “a cast out of its family (both spellings)” | An ERR `tbb8` cast out of its family with the checked `=>` traps TbbErr too. | `trap:TbbErr` |
| `vf0870e` | 870 | row | “a checked crossing into or within a family lands in the target's range” | A checked crossing into `tbb8` of a value outside its range (1000 from int64) traps TbbErr. | `trap:TbbErr` |
| `vf0870f` | 870 | row | “a twisted division has no row” | A `tbb32` `/` or `%` by a computed divisor has no row at all (no div-zero, div-min or err-exit). | `sh:0` |
| `vf0870g` | 870 | row | “(a zero divisor is ERR)” | A `tbb` division or remainder by zero yields ERR without a trap. | `run:0` (M10 `v18_tbb_div_by_zero_is_err`) |
| `vf0871` | 871 | row | “\| `failsafe-post` \| `failsafe` returns a positive value (D-014)” | Every `exit` in `failsafe` is checked positive, one `failsafe-post` row each. | `sh:0` |
| `vf0872` | 872 | row | “\| `loop-step` \| a counted loop's computed step is positive (D-022)” | A counted loop with a computed step is one `loop-step` row; one with a literal step has none. | `sh:0` |
| `vf0872b` | 872 | row | “the compare at the loop's entry, `BadStep`” | A computed step of zero traps BadStep at the loop's entry. | `run:113` (M10 `l21_zero_step_computed_traps`) |
| `vf0872c` | 872 | row | “a literal step is the checker's (TYPE-068) and has no row” | A literal zero step is refused by the checker (TYPE-068). | `refuse:NITPICK-TYPE-068` (M10 `l19_zero_step_literal_refused`) |
| `vf0873` | 873 | row | “\| `shift-range` \| a shift's COMPUTED amount is inside `0..width-1` (D-277)” | A shift by a computed amount (`<<` or `>>`) is one `shift-range` row; a shift by a literal amount has none. | `sh:0` |
| `vf0873b` | 873 | row | “the compare before the shift, `ShiftRange`” | A computed shift amount equal to the width traps ShiftRange. | `run:111` (M10 `s04_shift_amount_equals_width`) |
| `vf0873c` | 873 | row | “a known amount is the checker's (TYPE-070) and has no row” | A literal amount outside the range is refused, NITPICK-TYPE-070. | `refuse:NITPICK-TYPE-070` (M10 `s07_shift_literal_amount_refused`) |
| `vf0873d` | 873 | row | “a `simd` shift's any-lane guard is one row over the lanes (D-282)” | A `simd<uint8, 8>` shift by a computed splat is ONE `shift-range` row. | `sh:0` |
| `vf0874` | 874 | row | “\| `prove` \| a `prove(...)` holds under its path conditions” | A `prove(...)` statement is one `prove` row with a solver query (fifth field `1`). | `sh:0` |
| `vf0874b` | 874 | row | “\| `prove` \| a `prove(...)` holds under its path conditions \| no \|” | `prove` has no guard: in the plain build a `prove` that is false at run time is not checked, and the program runs on. | `run:0` |
| `vf0875` | 875 | row | “\| `assert-static` \| an `assert_static(...)` folds to true (the frontend)” | An `assert_static(...)` statement is one `assert-static` row, decided by the frontend (`c` in the fifth field). | `sh:0` |
| `vf0875b` | 875 | row | “an `assert_static(...)` folds to true” | An `assert_static` whose proposition folds to false is refused. | `refuse` |
| `vf0876` | 876 | row | “\| `disjoint` \| two accesses of one root through computed indices name disjoint storage” | Two `$$m` claims on one array through computed indices are one `disjoint` row. | `sh:0` |
| `vf0876b` | 876 | row | “the byte-range compare at the second access, `BorrowOverlap`” | Two live `$$m` claims through computed indices that name the same element trap BorrowOverlap at the second access. | `trap:BorrowOverlap` |
| `vf0876c` | 876 | row | “a static overlap is the aliasing analysis's (BORROW-013) and has no row” | Two live `$$m` claims of the same literal element are refused, BORROW-013. | `refuse:BORROW-013` |
| `vf0877` | 877 | row | “\| `floor-spec` \| a clause of a floor symbol's section in `runtime/npkrt.spec` holds” | A `floor-spec` row states a clause of a floor symbol's spec section of its IR; its rows land in runtime/npkrt.obligations. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll and runtime/npkrt.spec), which this session neither builds nor runs |
| `vf0877b` | 877 | row | “rows from the floor writer (1.5.6), never the compiler” | The compiler never writes a `floor-spec` row. | `sh:0` |
| `vf0878` | 878 | row | “\| `floor-model` \| a bounded protocol model's bad predicate is unreachable within its depth and preemption bound” | A `floor-model` row states that a protocol model's bad predicate is unreachable within its bounds. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt npkg/floor_explore.npk; not run here |
| `vf0878b` | 878 | row | “rows from the floor writer over `runtime/models/`” | The compiler never writes a `floor-model` row. | `sh:0` |
| `vf0886` | 886 | rule | “already refuses a lossy crossing at compile time (D-095)” | A checked integer `=>` that could lose data (int64 to int32) is refused at compile time. | `refuse` (M10 `c03_narrow_signed_refused`) |
| `vf0888` | 888 | rule | “now traps `CastRange`” | A float's `=>!` to an integer is guarded by a CastRange trap (4117) in the emission. | `ir:@npk_trap\(i32 -?4117\)` |
| `vf0895` | 895 | rule | “`(\|npk.len\| base)` -- an uninterpreted function of the base” | `.len` of a slice is the uninterpreted `\|npk.len\|` applied to the base in the obligation text. | `sh:0` |
| `vf0898` | 898 | rule | “against are the same symbol and the row discharges” | Inside `for (i in 0...xs.len)` the loop bound and the element row's length are one symbol, so the row discharges. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0899` | 899 | rule | “length term (DEF-14's rule: a name a pointer may write is never named)” | An escaped name, and a length read through a call, have no length term: a row over a parameter's element is `open` unless the loop bounds it. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0902` | 902 | rule | “A RANGE SLICE IS ONE ROW for the pair the emitter tests in one `and`” | A range slice is ONE `bounds` row for the pair. | `sh:0` |
| `vf0903` | 903 | rule | “recorded at the RANGE node -- the index expression's rhs, not the index” | The range slice's row is keyed on the RANGE node, the key the emitter asks with. | untestable [internal] which AST node keys the row is internal; its effect (the guard elided under a discharged row) needs a discharged row of a range slice, which only z3 gives honestly |
| `vf0908` | 908 | rule | “A GUARD INSIDE A `defer` BODY IS ONE ROW AND SEVERAL TRAPS (DEF-82)” | A guarded index inside a `defer` body that runs at two exits is ONE `bounds` row. | `sh:0` |
| `vf0912` | 912 | rule | “one copy's traps times the copies” | That row's traps field is one copy's traps times the copies: 2 for a `defer` written at two exits. | `sh:0` |
| `vf0919` | 919 | rule | “checked positive at the `exit` (EnsuresViolated, the trap route's re-entry” | `failsafe`'s `exit` operand is checked positive: a computed zero is EnsuresViolated, and the trap route's re-entry rule ends the process at 70. | `run:70` |
| `vf0920` | 920 | rule | “a literal that is not positive refused by” | A literal `exit` operand in `failsafe` that is not positive is refused by the checker, REACH-004. | `refuse:REACH-004` |
| `vf0921` | 921 | rule | “so a discharged row elides that check” | A discharged `failsafe-post` row elides the `exit`'s positivity check in the verified build. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0925` | 925 | rule | “The guard a discharged row elides is the CALLEE's” | In the verified build a direct call whose `limit-subsume` row is discharged calls `<symbol>.body`, skipping the callee's entry check; in the plain build it calls the entry. | `sh:0` |
| `vf0927` | 927 | rule | “its body under `<symbol>.body` and its ordinary symbol as the checked entry” | A sync function with a limited parameter emits a second define, `<symbol>.body`. | `ir:^define [^\n]*narrow\.body"?\(` |
| `vf0928` | 928 | rule | “(the entry checks, then a tail call of the body)” | The ordinary symbol is the checked entry, which ends in a tail call of the body. | `ir:tail call [^\n]*narrow\.body` |
| `vf0929` | 929 | rule | “the manifest discharged names the body, every other call -- and every” | Without a manifest no call names the body except the entry's own tail call: the plain build's direct call names the entry. | `ir!:(?s)call [^\n]*narrow\.body"?\(.*call [^\n]*narrow\.body"?\(` |
| `vf0931` | 931 | rule | “A coroutine callee keeps one symbol and its call sites carry no” | An async callee with a limited parameter has no `.body` twin and its call site no `limit-subsume` row. | `sh:0` |
| `vf0933` | 933 | rule | “runners hold the belt: every `.body` occurrence in an emission is its own” | The runners' belt: every `.body` occurrence is its define, the wrapper's tail call or a direct call, and the direct calls equal the discharged rows. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full tree |
| `vf0937` | 937 | rule | “`exhaustive` (one” | `exhaustive` is one row per `pick`, both spellings: a `pick` statement and a `pick` expression give two rows. | `sh:0` |
| `vf0940` | 940 | rule | “`c` in `rows.txt`” | `exhaustive` and `assert-static` rows are inventory lines: `c` in rows.txt's fifth field. | `sh:0` |
| `vf0941` | 941 | rule | “query, tier `-`, word `none`” | A checker row's tier is `-`. | `sh:0` |
| `vf0941b` | 941 | rule | “`prove` is decided by z3 like a guarded kind” | A `prove` row carries a solver query (fifth field `1`). | `sh:0` |
| `vf0942` | 942 | rule | “and is the ONE kind whose non-discharge refuses the verified build” | The verified build refuses a program whose `prove` row is not discharged (NITPICK-VERIFY-001), while the plain build accepts it. | `sh:0` |
| `vf0944` | 944 | rule | “a computed step's compare, a literal step being the checker's” | A negative computed step traps BadStep at the loop's entry. | `run:113` (M10 `l22_negative_step_computed_traps`) |
| `vf0946` | 946 | rule | “`err-exit` produces rows, and the” | `err-exit` rows are produced: a tbb comparison has one (see vf0870). | `sh:0` |
| `vf0947` | 947 | rule | “twisted kinds are terms. A `tbb`/`tfp`/`dim256`/`trit`/`tryte`/`nit`/`nyte`” | A twisted value is an Int in its carrier's range, ERR the carrier's most negative value; `ERR` is MIN, `is_err(x)` is `(= x MIN)`, a symbol's axiom 'ERR or inside the valid range'. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0953` | 953 | rule | “emitter's own `ite`: saturate-to-ERR on `+ - *` and negation” | Twisted `+ - *` and negation saturate to ERR, and ERR is sticky. | `run:0` (M10 `m13_tbb_err_sticky`) |
| `vf0954` | 954 | rule | “floor multiply `(div (* a b) 2^F)` and truncating divide `(npk_sdiv (* a” | The encoder models `tfp`'s `*` as the floor multiply and `/` as the truncating divide, narrowed by the range test, as the emitter computes them. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0955` | 955 | rule | “a zero divisor ERR” | A twisted division by zero is ERR. | `run:0` (M10 `v18_tbb_div_by_zero_is_err`) |
| `vf0956` | 956 | rule | “digits' `&`/`\|` as min/max” | The ternary digits' `&` and `\|` are the Kleene min and max: 1 & -1 is -1, 1 \| -1 is 1, 0 & 1 is 0, 0 \| -1 is 0. | `run:0` |
| `vf0956b` | 956 | rule | “`dim256` is `tfp256`” | To the solver `dim256` is `tfp256`. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0957` | 957 | rule | “one per `-4100` site” | The `TbbErr` guard is a `-4100` trap site: a comparison of computed tbb values emits `@npk_trap(i32 -4100)`. | `ir:@npk_trap\(i32 -4100\)` |
| `vf0958` | 958 | rule | “comparison, the operand not ERR at a cast out of its family (both” | An ERR operand at a cast out of its family traps TbbErr (the `=>!` spelling). | `trap:TbbErr` |
| `vf0960` | 960 | rule | “its fact is a hypothesis after the site (every continuing” | An err-exit row's fact is a hypothesis after its site. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0961` | 961 | rule | “and a discharged row's guard is one `llvm.assume`” | A discharged err-exit row's guard becomes one `llvm.assume`. | `sh:0` |
| `vf0962` | 962 | rule | “A `frac` or a tfp-element `complex` guard is a row over an aggregate the” | A `frac32` comparison's TbbErr guard is one `err-exit` row, `unencoded` (fifth field `0`). | `sh:0` |
| `vf0963` | 963 | rule | “its trap kept” | The frac guard's trap is kept: comparing a `frac32` ERR traps TbbErr. | `trap:TbbErr` |
| `vf0965` | 965 | rule | “twisted division has no row: it never traps.” | A twisted division has no row (see vf0870f's program). | `sh:0` |
| `vf0966` | 966 | rule | “subject encodes (its `$` the Int term)” | A `limit` over a twisted subject is an encoded row (fifth field `1`). | `sh:0` |
| `vf0967` | 967 | rule | “`$` as the subject and each clause as a fact for the next (the predicate” | A rule's predicate traps on its FIRST false clause: with `{ $ != 0, 100 / $ > 1 }` a zero traps LimitViolated, never DivByZero. | `trap:LimitViolated` |
| `vf0968` | 968 | rule | “A guard's fact is never pushed under a” | A guard's fact is never pushed under a quiet encoding nor from inside a contract clause encoded for its own row (DEF-33). | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0975` | 975 | rule | “FLOATS ARE TERMS IN TWO TIERS, and” | A float obligation's row carries the tier the encoder names: a `prove` over `flt64` values has tier `fp` in rows.txt's eleventh field. | `sh:0` |
| `vf0977` | 977 | rule | “value is a term of the IEEE sort (`(_ FloatingPoint 8 24)` / `(_” | A `flt32` value is a term of sort `(_ FloatingPoint 8 24)` and a `flt64` one of `(_ FloatingPoint 11 53)` in the obligation text. | `sh:0` |
| `vf0979` | 979 | rule | “under SMT-LIB's IEEE semantics — `fp.add`/`sub`/`mul`/`div` under RNE” | A float division is `fp.div` under RNE in the obligation text. | `sh:0` |
| `vf0980` | 980 | rule | “`#sqrt` as `fp.sqrt RNE`” | `#sqrt` is `fp.sqrt` under RNE in the obligation text. | `sh:0` |
| `vf0981` | 981 | rule | “`fcmp` writes (`==` is `fp.eq`, `!=` its negation, so NaN compares as the” | The machine's float compares are the ordered ones with `!=` their negation: NaN == NaN is false, NaN != NaN is true, and NaN < 1 and NaN >= 1 are both false. | `run:0` |
| `vf0983` | 983 | rule | “text denotes (a `flt32` literal rounded twice, as the emitter's double-then-” | A `flt32` literal is rounded twice, to double then to float: 1.0000000596046448309 (just above the midpoint 1 + 2^-24) becomes 1 + 2^-24 as a double and then 1.0 (a tie, to even) as a flt32, where a single rounding gives 1 + 2^-23. | `run:0` |
| `vf0984` | 984 | rule | “an integer entering `to_fp RNE (to_real x)`, a” | An integer entering a float is `to_fp RNE`, a widening exact, a narrowing `=>!` rounded, in the obligation text. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0985` | 985 | rule | “`%` (`frem`) and a float LEAVING” | A float `%` and a float leaving to an integer are opaque values to the solver. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0987` | 987 | rule | “itself carries a `cast-range` row over the operand since 1.5.8b step 5” | A float's `=>!` to an integer is a `cast-range` row over the float operand. | `sh:0` |
| `vf0988` | 988 | rule | “`flt128` is storage (D-143) and has no term.” | `flt128` has no term to the solver. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf0988b` | 988 | rule | “Every float value is NAMED and its definition” | Every float value is a named symbol whose definition is recorded. | untestable [internal] the encoder's naming of float values; no outcome depends on it outside the verdicts |
| `vf0989` | 989 | rule | “Floats never trap: no row” | Float arithmetic has no rows: a function of float `+ - * /` and one of float `%` have none. | `sh:0` |
| `vf0990` | 990 | rule | “is theirs — what the terms buy is that a `limit`, a contract, an” | Over floats, a `limit`, a `prove` and the `TbbErr` guard of a float entering `tbb` are encoded rows (fifth field `1`). | `sh:0` |
| `vf0992` | 992 | rule | “THE TIER COLUMN: `rows.txt`'s eleventh” | rows.txt's eleventh field is the tier: `int` for an Int/Bool cone, `bv` where a bit-vector crossing is, `fp` where a float sort is, `-` for an unencoded or checker row. | `sh:0` |
| `vf0995` | 995 | rule | “runners carry it into the manifest” | Both runners carry the tier into the manifest. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf0996` | 996 | rule | “(D-218 (5)): for every `fp` row the encoder also writes a twin query” | For an `fp` row whose floats are bounded by literal comparisons (a `limit` rule), the encoder writes a twin `NNNN.t2.smt2` beside the tier-1 file and names it in `index.t2.txt`. | `sh:0` |
| `vf0998` | 998 | rule | “Real — an operation a fresh Real within `eps·\|v\| + eta` of its exact” | In the twin every float is a Real and every operation a fresh Real within eps·\|v\| + eta of its exact result; a square root r >= 0 with r² inside v·(1 ∓ eps)². | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1001` | 1001 | rule | “CONDITIONS, else no twin: (i) every float symbol no hypothesis defines is” | Condition (i): with the floats unbounded (plain parameters), the same `#sqrt` prove gets no twin. | `sh:0` |
| `vf1004` | 1004 | rule | “(ii) every operation's magnitude within the normal range, a” | Condition (ii): every operation's magnitude in the normal range, divisors nonzero and roots' arguments non-negative are conjoined to the twin's goal. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1007` | 1007 | rule | “(iii) the goal a comparison or a Boolean combination of comparisons — an” | Condition (iii): a goal that is an `fp.eq` (`prove(a == a)`) stays tier 1: no twin, even with the float bounded. | `sh:0` |
| `vf1008` | 1008 | rule | “The runner asks tier 1 first” | The runner asks tier 1 first and the twin once for a `budget` row; `unsat` discharges it with tier `real`; a tier-1 `sat` is never retried. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1011` | 1011 | rule | “`flt_tier2.npk` is the shape D-218 (5)” | `#sqrt(a*a + b*b) >= 0.0` under bounded a, b is `unknown` in QF_FP and `unsat` in the twin. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1015` | 1015 | rule | “A `simd<T, N>` value is N scalar” | A `simd<T, N>`'s any-lane guards are one row each: its division one `div-zero` row, its shift one `shift-range` row. | `sh:0` |
| `vf1016` | 1016 | rule | “The lanes ride EXPRESSIONS” | A simd value's lanes are terms carried by expression and by binding (constructor, splat, lane-wise operations, `[i]`, `.len`, `.any()`/`.all()`, `sum`/`min`/`max`, casts). | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1028` | 1028 | rule | “Anything else (a call's value, a computed” | A call's value or a computed index is N opaque lanes; the vector itself has no scalar term. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1029` | 1029 | rule | “THE ROWS: a” | A `simd` division's any-lane guard is ONE `div-zero` row over the lanes' conjunction. | `sh:0` |
| `vf1031` | 1031 | rule | “of the lanes' conditions and, for a signed element, one `div-min` row” | For a signed element the simd division also has one `div-min` row; an unsigned element none. | `sh:0` |
| `vf1032` | 1032 | rule | “likewise; a `simd` shift's any-lane guard one `shift-range` row over its” | A `simd` shift's any-lane guard is one `shift-range` row. | `sh:0` |
| `vf1033` | 1033 | rule | “conjunction — the emitter's one trap per site, one group” | A simd any-lane guard is one trap per site: the simd division's `div-zero` row keeps one trap (traps field 1). | `sh:0` |
| `vf1034` | 1034 | rule | “The `unencoded` producers of 1.5.0 and” | A `simd` division and a `simd` shift are no longer `unencoded`: their rows carry a query (fifth field `1`). | `sh:0` |
| `vf1036` | 1036 | rule | “producers are a `limit` over a subject no theory covers (a string, a struct,” | A `limit` over a struct subject is an `unencoded` row (fifth field `0`). | `sh:0` |
| `vf1037` | 1037 | rule | “and the `TbbErr` guards over a `frac` or a tfp-`complex`” | The TbbErr guard of a `frac32` comparison is an `unencoded` row. | `sh:0` |
| `vf1039` | 1039 | rule | “The verdict column is `discharged` (unsat), `open` (sat” | The manifest's verdict is `discharged` (unsat), `open` (sat), `budget` (unknown under the rlimit), `unencoded` or `checker`. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1043` | 1043 | rule | “The elision” | The manifest's elision column is `elided`, `retained`, or `none` for a kind with no guard. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1050` | 1050 | rule | “a proposition holds only where its evaluation does not trap” | A proposition holds only where its evaluation does not trap: a `requires` clause whose own division meets a zero divisor traps DivByZero at run time, not RequiresViolated. | `trap:DivByZero` |
| `vf1051` | 1051 | rule | “Every guard met inside a contract clause, an” | Every guard met inside a clause, invariant conjunct, rule clause or `prove` is conjoined into the proposition's term and pushed as a hypothesis nowhere. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1063` | 1063 | rule | “`intN`/`uintN` symbol is an `Int` with the axiom of its range” | A plain integer is an unbounded `Int` to the solver: the obligation file of an int32 division declares Int symbols and no bit-vector sort. | `sh:0` |
| `vf1065` | 1065 | rule | “truncating `npk_sdiv`/`npk_srem` as the machine's, with the D-007 pair as” | `/` and `%` are the truncating `npk_sdiv` / `npk_srem` in the obligation text (a quotient or remainder inside another division's cone). | `sh:0` |
| `vf1066` | 1066 | rule | “rows. A `bool` is `Bool`, a pattern's literal is read under the selector's” | A `bool` is `Bool`, a pattern's literal is read under the selector's type, and a path condition is a hypothesis in its arm. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1069` | 1069 | rule | “`x << n` and `x >> n` are defined for” | `x >> n` with a computed n equal to the width traps ShiftRange: shifts are defined for 0 <= n < width only. | `run:111` (M10 `s06_right_shift_amount_width`) |
| `vf1071` | 1071 | rule | “known amount outside the range is `NITPICK-TYPE-070` at the shift (both” | A known amount outside the range is NITPICK-TYPE-070 for `>>` in its compound spelling too: `x >>= 32i32` on an int32. | `refuse:NITPICK-TYPE-070` |
| `vf1072` | 1072 | rule | “operators, both spellings, the folder's bound the type's width)” | The folder's bound is the operand type's width: `int8 << 8i8` is NITPICK-TYPE-070. | `refuse:NITPICK-TYPE-070` |
| `vf1073` | 1073 | rule | “amount is one unsigned compare on its carrier (`n <u W`, a negative amount” | A negative computed amount reads as huge and traps ShiftRange. | `run:111` (M10 `s05_shift_amount_negative`) |
| `vf1074` | 1074 | rule | “reading as huge) trapping `ShiftRange` (−4115)” | A computed shift's guard is a `ShiftRange` trap, code -4115, in the emission. | `ir:@npk_trap\(i32 -4115\)` |
| `vf1075` | 1075 | rule | “and, discharged, one `llvm.assume`” | In the verified build a discharged `shift-range` row's guard is one `llvm.assume` and no ShiftRange trap. | `sh:0` |
| `vf1076` | 1076 | rule | “hypothesis after the site either way” | A shift's range goal is a hypothesis after the site whether or not its row is discharged. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1081` | 1081 | rule | “Wherever an operand is a numeral the encoder knows” | With a numeral operand a bitwise operation is Int arithmetic: `(k & 7) + 1` as a divisor crosses into no bit-vector theory (no `int2bv`, tier `int`). | `sh:0` |
| `vf1087` | 1087 | rule | “`x & (2^j − 1)` is `(mod x 2^j)`” | The Int forms: `x << k`, `x >> k`, `x & (2^j - 1)`, `x & 2^j`, `x & ~(2^j - 1)`, `~x` as `mod`/`div`/`*` arithmetic, at any width. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1090` | 1090 | rule | “Every other shape crosses at a word of at” | Any other bitwise shape crosses into bit-vectors at 64 bits or less: `(k & m) \| 1` over int32 has `int2bv` in its file and tier `bv`. | `sh:0` |
| `vf1095` | 1095 | rule | “is exact — and `bvshl`/`bvlshr`/`bvashr` for a shift by a non-numeral” | A shift by a non-numeral amount inside a crossing is `bvshl` (for `<<`). | `sh:0` |
| `vf1096` | 1096 | rule | “Above 64 bits a” | Above 64 bits a general bitwise operation stays opaque: `(k & m) \| 1` over int128 has no `int2bv`. | `sh:0` |
| `vf1098` | 1098 | rule | “measured 191 rlimit at 32 and 64 bits” | The crossing's measured cost per width (191 rlimit at 32 and 64 bits, 883,930 at 128, ...). | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1103` | 1103 | rule | “A function with a crossing emits `(set-logic” | A function whose obligations hold a crossing emits `(set-logic ALL)`; one without does not. | `sh:0` |
| `vf1105` | 1105 | rule | “A flag family (D-230) is an unsigned 32-bit word to the” | A flag family is an unsigned 32-bit word to the encoder; `int32 =>! oflags` and back re-sign the bit pattern. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1109` | 1109 | rule | “THE GATE (D-280): every row” | Every row discharged before a crossing is discharged after it; measured over the re-recorded manifest. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full tree |
| `vf1116` | 1116 | rule | “value is an `Int` in the” | A twisted value is an Int in its carrier's range with ERR the most negative value, a value the terms carry. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1123` | 1123 | rule | “`+ - *` and negation saturate to ERR outside the” | Twisted `+ - *` and negation saturate to ERR outside the valid range. | `run:0` (M10 `m13_tbb_err_sticky`) |
| `vf1125` | 1125 | rule | “`tfp`'s `*` is `(div (* a b) 2^F)` and its `/` `(npk_sdiv (* a 2^F) b)`” | `tfp`'s `*` and `/` are modelled as the emitter's floor multiply and truncating divide. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1126` | 1126 | rule | “each narrowed by the range test, a zero divisor is ERR, `/` and `%` at the” | A twisted `/` and `%` truncate: tbb32 -7 / 2 is -3 and -7 % 2 is -1. | `run:0` |
| `vf1128` | 1128 | rule | “the truncating quotient or remainder, the ternary digits' `&`/`\|` are the” | The ternary digits' `&`/`\|` are the Kleene min/max. | `run:0` |
| `vf1129` | 1129 | rule | “Kleene min/max, `dim256` is `tfp256`. Each raw result is named once” | Each raw twisted result is named once without an axiom before the range test reads it. | untestable [internal] how the encoder names a raw result; no outcome but the verdicts depends on it |
| `vf1132` | 1132 | rule | “The rows are `err-exit`'s (§7b): one per” | One `err-exit` row per TbbErr guard: two tbb comparisons in a function are two rows. | `sh:0` |
| `vf1133` | 1133 | rule | “A twisted division has” | A twisted division never traps: a zero divisor yields ERR. | `run:0` (M10 `v18_tbb_div_by_zero_is_err`) |
| `vf1134` | 1134 | rule | “A `limit` over a twisted subject encodes” | A `limit` over a `tbb32` subject is an encoded row. | `sh:0` |
| `vf1136` | 1136 | rule | “for the next (the predicate traps on the first false clause)” | A rule's predicate traps on its first false clause (LimitViolated), before a later clause's own guard. | `trap:LimitViolated` |
| `vf1137` | 1137 | rule | “tfp-element `complex` is an aggregate the walk has no term for: its guards” | A `frac`'s TbbErr guard is `unencoded` (fifth field `0`). | `sh:0` |
| `vf1138` | 1138 | rule | “are `unencoded`, their traps kept.” | The unencoded frac guard's trap is kept: comparing a `frac32` ERR traps TbbErr. | `trap:TbbErr` |
| `vf1142` | 1142 | rule | “53)`) with NO range axiom — NaN and the infinities are values of it, and a” | A float term has no range axiom: NaN and the infinities are its values. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1144` | 1144 | rule | “the emitter's instruction under SMT-LIB's IEEE semantics: `fp.add`/`sub`/” | A float obligation's arithmetic is SMT-LIB's IEEE operations: a product and a sum in a `#sqrt` prove appear as `fp.mul` and `fp.add`. | `sh:0` |
| `vf1146` | 1146 | rule | “predicates the emitter's `fcmp` writes (`==` is `fp.eq`, `!=` its negation,” | NaN compares as the machine's ordered `fcmp` does, `!=` being `==`'s negation. | `run:0` |
| `vf1149` | 1149 | rule | “the two agree by correct rounding; a `flt32` literal rounded twice, as the” | A `flt32` literal is rounded to double and then to float (1.0000000596046448309f32 is 1.0). | `run:0` |
| `vf1151` | 1151 | rule | “(to_real x)`, a widening exact, a narrowing `=>!` rounded; `%` (`frem`, a” | A float `%` is `frem`, a truncated fmod and not IEEE's remainder: 5.5 % 2.0 is 1.5 and -5.5 % 2.0 is -1.5. | `run:0` |
| `vf1153` | 1153 | rule | “opaque as VALUES -- the crossing itself carries a `cast-range` row over the” | A float leaving to an integer carries a `cast-range` row over the operand. | `sh:0` |
| `vf1155` | 1155 | rule | “compares; `flt128` is storage (D-143) and has no term.” | `flt128` has no term. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1156` | 1156 | rule | “Every float value is NAMED — a fresh symbol defined equal to the operation,” | Every float value is a fresh named symbol defined equal to its operation. | untestable [internal] the encoder's naming; no outcome depends on it outside the verdicts |
| `vf1158` | 1158 | rule | “Floats never trap (D-007): no row is theirs” | Float arithmetic never traps: 1.0 / 0.0 is +infinity and 1.0 % 0.0 is NaN, with no trap. | `run:0` |
| `vf1159` | 1159 | rule | “`limit`, a contract clause, an `invariant`, a `prove` and the `err-exit` row” | Over floats a `limit`, a `prove` and a float entering `tbb` are encoded rows. | `sh:0` |
| `vf1160` | 1160 | rule | “Measured: a” | A bounded quotient's `prove` discharges in QF_FP in 3.9 s. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1162` | 1162 | rule | “TIER 2, the Real-interval abstraction: for every row whose cone holds a” | For a float row meeting the conditions the encoder writes a twin `NNNN.t2.smt2` beside the tier-1 file, named in `index.t2.txt`. | `sh:0` |
| `vf1165` | 1165 | rule | “Real: an input symbol a free Real, a named operation a fresh Real `r` with” | The twin's Real model: each operation a fresh Real within ε·\|v\| + η of its exact value. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1172` | 1172 | rule | “The twin is written at all only under THREE CONDITIONS, else the row stays” | Without the conditions no twin is written: an unbounded float `prove` has none. | `sh:0` |
| `vf1176` | 1176 | rule | “`requires` clause, a path condition; a negated comparison is not a bound,” | A negated comparison is not a bound (it holds of NaN): floats bounded only by `!($ < 1.0)` and `!($ > 2.0)` get no twin. | `sh:0` |
| `vf1179` | 1179 | rule | “operation's magnitude within the normal range (`\|v\| ≤ MAX_NORMAL` per” | The twin conjoins every operation's normal-range magnitude, nonzero divisors and non-negative root arguments to its goal. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1183` | 1183 | rule | “combination of comparisons over symbols and the Int fragment — an `fp.eq`,” | An `fp.eq` goal stays tier 1 only: no twin for `prove(a == a)` over a bounded float. | `sh:0` |
| `vf1184` | 1184 | rule | “with its NaN reading, stays tier 1 only, and an uninterpreted function in” | An uninterpreted function in the cone excludes the row from tier 2. | untestable [vague] which float cones hold an uninterpreted function (a `pure` float callee in a contract) is not spelled out enough to build one that surely meets the other two conditions |
| `vf1185` | 1185 | rule | “The runners ask tier 1 first; for a `budget` row” | The runners ask tier 1 first and the twin once for a `budget` row under the same profile and net; `--explain` names the tier that decided. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1189` | 1189 | rule | “Measured: `#sqrt(a*a + b*b) >= 0.0` under bounded” | The flt_tier2 shape is `unknown` in QF_FP and `unsat` in the twin. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1193` | 1193 | rule | “A `simd<T, N>` value is N scalar terms” | A `simd<T, N>` value is N scalar terms under its element's theory and has no term of its own. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1198` | 1198 | rule | “with a numeral index the lane's term (a computed index opaque, its `bounds`” | A computed lane index `v[i]` is one `bounds` row. | `sh:0` |
| `vf1201` | 1201 | rule | “right; `min`/`max` as its `select` over the strict compare, `fcmp olt`/`ogt`” | A float `simd` `.min()` folds with a select over the ordered strict compare, false on NaN, so a NaN lane is passed over: min of (1, 3, 0.5, NaN) is 0.5. | `run:0` |
| `vf1204` | 1204 | rule | “AND through bindings: a `simd` local's lanes are N” | A `simd` local's lanes are N symbols, a new set at every write, fresh and opaque at every invalidation, restore and merge. | untestable [z3] how the encoder states a value to the solver; its truth shows only in the verdicts z3 reaches |
| `vf1209` | 1209 | rule | “is N opaque lanes. A `simd` division's any-lane guard is ONE `div-zero`” | A `simd` division's any-lane guard is ONE `div-zero` row, a signed element's also one `div-min` row. | `sh:0` |
| `vf1211` | 1211 | rule | “one `div-min` row; a `simd` shift's any-lane guard one `shift-range` row” | A `simd` shift's any-lane guard is one `shift-range` row. | `sh:0` |
| `vf1213` | 1213 | rule | “the site as a scalar's is — and a discharged any-lane row elides its guard” | In the verified build a discharged any-lane `div-zero` row (an unsigned `simd` division, which has no `div-min` row) becomes exactly one `llvm.assume`. | `sh:0` |
| `vf1220` | 1220 | rule | “**The tier column (D-281).** `rows.txt`'s eleventh field, read off the” | rows.txt's eleventh field is the tier: `int`, `bv`, `fp`, or `-` for an unencoded or checker row. | `sh:0` |
| `vf1224` | 1224 | rule | “`real` is written by” | `real` is written by the runner for a row tier 2 discharged. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1228` | 1228 | rule | “**What is still outside the fragment.** A `limit` over a string, a struct” | A `limit` over a string subject is `unencoded` (fifth field `0`). | `sh:0` |
| `vf1228b` | 1228 | rule | “over a string, a struct” | A `limit` over a struct subject is `unencoded`. | `sh:0` |
| `vf1229` | 1229 | rule | “or an array (P-12's residue)” | A `limit` over an array subject is `unencoded`. | `sh:0` |
| `vf1230` | 1230 | rule | “tfp-element `complex` are `unencoded`, their guards kept” | The guard of a limit over a string is kept: breaking the rule traps LimitViolated. | `trap:LimitViolated` |
| `vf1232` | 1232 | rule | “`cast-range` rows; D-210's overflow rows are 1.5.8's, over the lane” | A `simd`'s integer lanes trap as scalars do: a lane `+` past the maximum traps IntOverflow. | `run:93` (M10 `o22_simd_lane_overflow`) |
| `vf1234` | 1234 | rule | “The compiler's own” | The compiler's own manifest at 1.5.4b's close: 368 rows in 197 files, 329 int, 11 bv, 28 -, no fp. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records rather than what it does with a program |
| `vf1244` | 1244 | rule | “A `limit` over a string, a struct or an” | Still at 1.5.8b: a `limit` over a struct is `unencoded` with its guard kept. | `sh:0` |
| `vf1245` | 1245 | rule | “array and the `TbbErr` guards over a `frac` or a tfp-element `complex` are” | Still at 1.5.8b: the TbbErr guard of a `frac` is `unencoded`. | `sh:0` |
| `vf1251` | 1251 | rule | “the file is `nitpick.obligations` at the manifest root, committed, written” | nitpick.obligations is written only by `npkg verify --record`. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1255` | 1255 | rule | “`<sha256> <kind> <tier> <verdict> <elision> <symbol>`” | A manifest row is `<sha256> <kind> <tier> <verdict> <elision> <symbol>`. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1264` | 1264 | rule | “`--obligations` writes a function's file and rows only when” | `--obligations` writes rows only for functions the emission holds: a program that formats no float has no row for the prelude's `flt_bits_shortest`. | `sh:0` |
| `vf1281` | 1281 | rule | “functions: `\|uf.<name>.<decl>\|` for a `pure never fails` callee (1.5.3)” | A row's text declares a `pure never fails` callee as an uninterpreted function `\|uf.<name>.<decl>\|`. | `sh:0` |
| `vf1297` | 1297 | rule | “`rows.txt` (`--obligations`) names each row's site (`space:index`), its” | rows.txt names each row's role: a division's row in its own function is a `guard`. | `sh:0` |
| `vf1308` | 1308 | rule | “`rows.txt`'s fifth column is `1` (a row with a” | rows.txt's fifth column is `1` for a row with a `(check-sat)`: a division's row is encoded. | `sh:0` |
| `vf1314` | 1314 | rule | “verified build refuses an undischarged `prove` (`NITPICK-VERIFY-001`)” | The verified build refuses an undischarged prove, NITPICK-VERIFY-001. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1319` | 1319 | rule | “`int`, `bv`, `fp`, `-`, and `real` written by the runner” | The tier column is the encoder's word: an int32 division's row is `int`. | `sh:0` |
| `vf1330` | 1330 | rule | “A static overlap is the” | A static overlap with a live claim is the aliasing analysis's own refusal, NITPICK-BORROW-013. | `refuse:NITPICK-BORROW-013` |
| `vf1334` | 1334 | rule | “a PROGRAM's raise — `?!`, `!!!` — is” | A program's raise is `@npk_raise(i32 CODE)`: `!!! E1;` calls npk_raise. | `ir:call [^\n]*@npk_raise\(i32` |
| `vf1340` | 1340 | rule | “THE HANG NET. Every” | Every z3 process runs under a hang net of 120 + 10·checks + 60·B seconds. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1363` | 1363 | rule | “`rows.txt` has a twelfth field, the row's CLAUSE CONTEXT” | rows.txt's twelfth field names a guard's clause context: a division inside an `ensures` clause has a row whose twelfth field is not 0. | `sh:0` |
| `vf1368` | 1368 | rule | “**A guard in a check exists only where the check is emitted.**” | A guard inside a check whose rows are all discharged goes with the check. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1374` | 1374 | rule | “**A loop head's check runs at every visit.**” | A guard inside an invariant has a row in every context the head is reached from: the entry and the back edge give a division in the invariant at least two rows of one site. | `sh:0` |
| `vf1392` | 1392 | rule | “THE BELTS COUNT GUARDS, NOT ROWS.” | The belts count guards, not rows. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1405` | 1405 | rule | “`overflow` traps” | An `overflow` guard traps -4110: a checked int32 addition's guard is `@npk_trap(i32 -4110)`. | `ir:@npk_trap\(i32 -4110\)` |
| `vf1406` | 1406 | rule | “`-4110`, `bounds` `-4099` and `cast-range` `-4117`” | A `bounds` guard traps -4099: an indexed read's guard is `@npk_trap(i32 -4099)`. | `ir:@npk_trap\(i32 -4099\)` |
| `vf1410` | 1410 | rule | “`terminate` gained its guard -- the loop head's” | `terminate`'s guard, the loop head's DecreasesViolated check, traps -4119. | `ir:@npk_trap\(i32 -4119\)` |
| `vf1416` | 1416 | rule | “`terminate` rows at recursive” | terminate rows at recursive calls; stack-depth rows derived by the runners after every file is decided. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1425` | 1425 | rule | “`--smt-opt` is the only verification flag that changes generated code” | `--smt-opt` is the only verification flag that changes generated code. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1430` | 1430 | rule | “`--smt-timeout` defaults to 5000 ms” | `--smt-timeout` defaults to 5000 ms. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1435` | 1435 | rule | “**Every elision is therefore recorded in a manifest” | Every elision is recorded in a manifest that is authoritative on later builds. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1438` | 1438 | example | “```” | The manifest v1 sketch (superseded by D-218's schema, line 1260). | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1447` | 1447 | row | “\| manifest matches exactly \| build proceeds, binary reproducible \|” | A matching manifest: the build proceeds. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1448` | 1448 | row | “\| Z3 proves **more** than recorded \| **build fails** \|” | Z3 proving more than recorded fails the build. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1449` | 1449 | row | “\| Z3 proves **less** than recorded \| **build fails** \|” | Z3 proving less than recorded fails the build. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1450` | 1450 | row | “\| no manifest \| generated; build marked *not reproducibility-verified* \|” | No manifest: generated, marked not verified. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1452` | 1452 | rule | “Obligations are identified by a **hash of their normalised SMT-LIB2 form**” | An obligation's hash is over its normalised SMT text, not its source location: two programs that differ only by blank lines above the function give the same hashes. | `sh:0` |
| `vf1456` | 1456 | rule | “This does not make Z3 deterministic.” | The manifest makes divergence detectable and fatal. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1467` | 1467 | rule | “The runtime floor (`runtime/npkrt.ll`, hand-written LLVM IR, permanent under” | The floor is specified beside itself and decided by the same solver. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1474` | 1474 | row | “\| `runtime/npkrt.spec` \|” | A file of the floor's evidence. | untestable [tree] a file of the compiler's tree |
| `vf1475` | 1475 | row | “\| `runtime/models/*.model` \|” | A file of the floor's evidence. | untestable [tree] a file of the compiler's tree |
| `vf1476` | 1476 | row | “\| `runtime/npkrt.obligations` \|” | A file of the floor's evidence. | untestable [tree] a file of the compiler's tree |
| `vf1478` | 1478 | rule | “**The writer is `npkg/floor_smt.npk`**” | The floor's writer and its modules. | untestable [tree] the compiler's sources |
| `vf1487` | 1487 | rule | “A manifest row” | A manifest row of a kind its file does not carry is refused by name. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1492` | 1492 | rule | “**The theory is the program's (§7c, D-218 (4)):**” | The floor's theory is the program's. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1505` | 1505 | rule | “**Memory is the uninterpreted function `(mem Int) Int`**” | Memory is an uninterpreted function with byte range axioms. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1518` | 1518 | rule | “**An address computed” | An address computed by the body wraps once. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1558` | 1558 | rule | “**A load of an element of” | A constant table's element reads as an ite. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1573` | 1573 | rule | “**The bit-vector crossing is a symbol**” | The bv crossing is a symbol. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1579` | 1579 | rule | “**A memory the translation cannot define” | A memory the translation cannot define pointwise is a template. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1596` | 1596 | rule | “One `(symbol @name …)` section per specified define.” | The spec file's names. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1623` | 1623 | row | “\| `(requires P)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1624` | 1624 | row | “\| `(objects (lo len) …)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1625` | 1625 | row | “\| `(views (lo len) …)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1626` | 1626 | row | “\| `(ensures P)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1627` | 1627 | row | “\| `(ensures-trap P)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1628` | 1628 | row | “\| `(frame (lo len) …)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1629` | 1629 | row | “\| `(ensures-fresh LEN)`” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1630` | 1630 | row | “\| `(loop LABEL (invariant I)” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1631` | 1631 | row | “\| `(loop LABEL (unroll N))` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1632` | 1632 | row | “\| `(summary)` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1633` | 1633 | row | “\| `(residue "why")` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1634` | 1634 | row | “\| `(boundary "what")` \|” | A spec clause and the rows it gives. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1636` | 1636 | rule | “**`requires`, `(objects …)` and `(views …)` are HYPOTHESES ABOUT THE CALLER” | requires/objects/views are hypotheses about the caller. | untestable [tool] a rule of runtime/npkrt.spec's grammar as the floor writer reads it; testing it needs the writer run over a spec |
| `vf1641` | 1641 | rule | “**TCB.md §4d, GENERATED**” | TCB.md §4d is generated. | untestable [tree] a document of the compiler's tree |
| `vf1660` | 1660 | rule | “**What is read once is written once.**” | Both runners refuse a clause written twice. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1670` | 1670 | rule | “A callee without `(summary)` is INLINED before translation” | A callee without summary is inlined; an unsupported form is a refusal naming the line. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1684` | 1684 | rule | “**THE INSTANTIATION RULE (S-65, generalised at step 4).**” | The invariant's universal is instantiated at the section's free symbols. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1699` | 1699 | rule | “**THE CONE.**” | A row's cone is the relevance closure. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1711` | 1711 | rule | “A call of `npk_sys6(nr, a1…a6)` is `(sys nr a1 … a6 k)`” | A syscall is the uninterpreted sys under the kernel's answer shape. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1718` | 1718 | rule | “**The kernel-effect table is ONE authority, and it is this region**” | The kernel-effect table is one authority, parsed strictly by the generator. | untestable [tree] the compiler's generator and sources |
| `vf1725` | 1725 | rule | “- **effect** — `none` (memory is as it was)” | The effect column's words. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1736` | 1736 | rule | “- **buffer**, **length** — for `writes`” | An error answer writes nothing, and a NULL buffer is written nowhere. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1740` | 1740 | rule | “- **bound** — the argument a non-negative answer never exceeds.” | The bound column. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1741` | 1741 | rule | “- **option** — for a number whose effect DEPENDS on an option argument” | A call site whose option is outside the row's set is refused by name. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1751` | 1751 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1752` | 1752 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1753` | 1753 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1754` | 1754 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1755` | 1755 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1756` | 1756 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1757` | 1757 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1758` | 1758 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1759` | 1759 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1760` | 1760 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1761` | 1761 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1762` | 1762 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1763` | 1763 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1764` | 1764 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1765` | 1765 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1766` | 1766 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1767` | 1767 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1768` | 1768 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1769` | 1769 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1770` | 1770 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1771` | 1771 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1772` | 1772 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1773` | 1773 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1774` | 1774 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1775` | 1775 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1776` | 1776 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1777` | 1777 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1778` | 1778 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1779` | 1779 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1780` | 1780 | row | “\|” | A row of the kernel-effect table. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1783` | 1783 | rule | “The option sets are the floor's own” | The option sets. | untestable [tool] the row states what the floor's translator models for the syscall (npkg/floor_kernel.npk, generated from this region); no program observes the model |
| `vf1792` | 1792 | rule | “**The write-region rows are HELD TO THE RUNNING KERNEL, not accepted**” | kernel_effects.npk holds each writes row to the running kernel. | untestable [tree] a test of the compiler's tree |
| `vf1816` | 1816 | rule | “**The envelope symbols**” | The envelope symbols are decided under the table. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1834` | 1834 | rule | “A row per clause as the table says; `kind` `floor-spec`” | A floor row's fields. | untestable [tool] a claim about the floor writer (npkg/floor_smt.npk and its modules, run by `npkg verify` or tools/floorspec.npk over runtime/npkrt.ll), which needs the compiler's tree and z3 |
| `vf1844` | 1844 | rule | “**Verdicts.** `discharged` is a proof.” | `open` in the floor is a run failure by name. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1853` | 1853 | rule | “**The profile carries `lp.dio=false` since step 4 (S-71).**” | The z3 profile carries lp.dio=false. | untestable [z3] a verdict, a manifest word or an elision decided by `npkg verify` with the pinned z3 (not in this environment) |
| `vf1870` | 1870 | rule | “**The belts, before a solver is spawned**” | The spec belts. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf1882` | 1882 | rule | “**What lands at 1.5.6 step 3**” | What step 3 landed. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records |
| `vf1898` | 1898 | rule | “**What lands at 1.5.6 step 4**” | What step 4 landed. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records |
| `vf1924` | 1924 | rule | “A specification says what one function does to memory on one thread.” | Each protocol is a small transition system under runtime/models/. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf1932` | 1932 | example | “```” | The model file's grammar. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf1948` | 1948 | rule | “The unrolling asserts one step per tick for K ticks” | The unrolling, its preemption bound and the stutter. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf1970` | 1970 | rule | “**A model that claims nothing is worth nothing, so every model carries” | Every model carries controls that must reach their bad state. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf1989` | 1989 | rule | “**Soundness of the sequential-consistency reading.**” | The SC reading is sound for these protocols; the correspondence belt. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf2004` | 2004 | rule | “**What lands at 1.5.6 step 5**” | What step 5 landed. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records |
| `vf2028` | 2028 | rule | “**A NAMED BLOCK IS NOT A MODELLED ONE” | The seventh model, reactor-io. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf2077` | 2077 | rule | “**What the bounds cover, measured (1.5.6b step 2).**” | What the bounds cover, measured. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records |
| `vf2096` | 2096 | rule | “**The second reading is a BELT (1.5.6b step 4d; D-295).**” | The explicit-state search is a belt in both runners. | untestable [tool] a claim about the protocol models (runtime/models/*.model), their unroller npkg/floor_model.npk or the explicit-state belt, run by `npkg verify` |
| `vf2141` | 2141 | rule | “An emitted `define` carries” | An emitted define carries "split-stack". | `ir:^define [^\n]*@"npk\.vf2141\.helper"\([^\n]*"split-stack"` |
| `vf2145` | 2145 | rule | “it would cross: the floor's `module asm` stub, which enters the trap route as” | A frame that would cross the limit enters the trap route as StackExhausted: unbounded recursion traps it. | `trap:StackExhausted` |
| `vf2149` | 2149 | rule | “the floor object carries” | The floor object carries `.note.GNU-split-stack` and `.note.GNU-no-split-stack`. | `sh:0` |
| `vf2153` | 2153 | rule | “`__morestack_non_split`, which that rewrite would reach,” | __morestack_non_split traps -4102. | untestable [internal] a floor symbol no program reaches |
| `vf2156` | 2156 | rule | “**`floor-stack-reserve`, in both runners**” | The floor's deepest chain fits a quarter of the 64 KiB reserve. | untestable [tool] a claim about the runners (`npkg verify`, the harness's verify/parity stages) and their belts, which need the pinned z3 and the full ladder |
| `vf2174` | 2174 | rule | “**What the belt does not say**” | What the belt does not say. | untestable [vague] a list of acceptances, no outcome |
| `vf2183` | 2183 | rule | “A proof decides what a model says” | The explorer runs the real code under a chosen interleaving. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2194` | 2194 | rule | “**The explored build is the real one, transformed” | The transformer, its points and the totality belt. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2211` | 2211 | rule | “**What no point can precede” | unrouted.txt states the asm syscalls. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2223` | 2223 | rule | “**The shim is hand-written IR” | The shim's virtual futexes, clock, signals and address space. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2252` | 2252 | rule | “**The scheduler is PCT with a fairness rule.**” | The scheduler and its replay belt. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2267` | 2267 | rule | “**The verdicts (D-301, D-302).**” | The explorer's verdicts. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2282` | 2282 | rule | “**The units (D-299, D-300, X-11).**” | Every stress program says explore: N or no. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2297` | 2297 | rule | “**The negative controls” | The negative controls. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2329` | 2329 | rule | “**The reference (D-303).**” | The C shim as the IR shim's reference. | untestable [tool] a claim about the schedule explorer (the transformer npkg/explore.npk, the shim runtime/explore/npkx.ll, the explore stage and its controls), run by `npkg test` |
| `vf2336` | 2336 | rule | “**What it found.**” | What the explorer found. | untestable [tree] a measurement or a record of what a step landed, about the compiler's tree and its records |
| `vf2344` | 2344 | rule | “**What it does not claim.**” | What the explorer does not claim. | untestable [vague] a list of acceptances, no outcome |
