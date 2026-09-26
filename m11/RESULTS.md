# M11 results: the references at HUNT2 `9126350`, claim by claim

Written by `gen/m11_report.py` from the claims (`m11/CLAIMS.md`) and the run
(`results/9126350/m11.jsonl`, the final run, both legs, 4 jobs). A claim's program AGREES when npkc and
both legs give the outcome its expectation states, written from the reference's text
before the first run.

## 1. The denominators

| reference | claims | examples | rows | rules | untestable | testable | tested | agree | disagree |
|---|---|---|---|---|---|---|---|---|---|
| BUILTIN | 227 | 2 | 109 | 116 | 33 | 194 | 194 | 182 | 12 |
| CONCURRENCY | 152 | 11 | 21 | 120 | 30 | 122 | 122 | 101 | 21 |
| IO | 78 | 5 | 9 | 64 | 11 | 67 | 67 | 60 | 7 |
| MACRO | 124 | 13 | 34 | 77 | 5 | 119 | 119 | 98 | 21 |
| TYPE | 322 | 19 | 74 | 229 | 19 | 303 | 303 | 242 | 61 |
| VERIFICATION | 585 | 9 | 97 | 479 | 128 | 457 | 457 | 435 | 22 |
| **total** | 1488 | 59 | 344 | 1085 | 226 | 1262 | 1262 | 1118 | 144 |

**These denominators cover 3704 of the references' 10433 lines** (the ranges extracted; the
rest is not yet extracted): AST none of 645; BUILD none of 683; BUILTIN 1–448 of 448; CONCURRENCY 1–648 of 648; CONTROL none of 416; IO 1–288 of 288; LEXICAL none of 411; MACRO 1–413 of 413; MEMORY none of 534; MODULE none of 301; OP none of 404; TRAITS none of 767; TYPE 1–660 of 2123; VERIFICATION 1–845, 846–1247 of 2352.

Untestable, by reason (each claim's own sentence is in `m11/CLAIMS.md`):

- `z3` 91 — needs the verified build (`npkg verify` and the pinned z3), not in this environment
- `tree` 40 — a claim about the compiler's own source tree, generators, harness or documents
- `vague` 36 — the sentence states no checkable outcome
- `internal` 27 — a compiler internal no program observes (an AST field, a table's layout)
- `unobservable` 15 — no program can tell the claim's truth from its falsehood
- `tool` 8 — needs a tool or workflow beyond a program: a package tree, the harness, the explorer, a driver
- `timing` 7 — a schedule, a race or a duration
- `platform` 2 — another architecture or OS, root, the network, or more memory than the VM

## 2. The disagreements (144)

By kind: `refused` 75, `accepted` 24, `wrong_exit` 23, `ir` 13, `emit_defect` 4, `crash` 3, `other_code` 2.

| class | claims |
|---|---|
| compiler: a silent wrong answer (F-018 to F-021) | 6 |
| compiler: a lifetime rule not enforced, a use after destroy (F-022) | 1 |
| compiler: accepted, then invalid IR (F-023) | 1 |
| compiler: npkc traps, exit 3 (F-024) | 4 |
| compiler: a flag that refuses every program (F-025) | 2 |
| compiler: a unit annotation accepted and ignored (F-026) | 1 |
| compiler, lower priority: accepted though refused, a self-declared hole, refused though permitted, a diagnostic (F-027) | 16 |
| documentation: the compiler right or safe, the reference wrong or stale (F-028) | 94 |
| known: deduplicated against KNOWN_DEFECTS.md | 7 |
| not a finding: refused at compile time where the text says it traps | 2 |
| not a finding: the program tests more than its sentence, or no valid program can test it | 10 |

Every disagreement below was also run at the baseline `c3bdae2` and at the compiler's newest
`main` `1b4f0c6`; the last column says whether each gave the same result (npkc, codes, both
legs, verdict) as HUNT2.

| id | line | claim | expected | measured | class | c3bdae2 / 1b4f0c6 |
|---|---|---|---|---|---|---|
| `bi0141` | BUILTIN:141 | W^X: a page is never writable and executable at once, so an unsealed (writable) page cannot run: calling it faults. | `run:107` | npkc 1 WILDX-002, -/- (`refused`) | WILDX-002: executing an unsealed page is refused at compile time | same / same |
| `bi0148c` | BUILTIN:148 | atomic_from_ptr is wild-context only: over the address of a plain local it is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: #wild_ptr, #ptr_add, atomic_from_ptr accepted outside wild, which no reference defines | same / same |
| `bi0154` | BUILTIN:154 | After wildx_seal the pages are not writable: a store faults (MachineFault). | `run:107` | npkc 1 WILDX-001, -/- (`refused`) | WILDX-001: writing a sealed page is refused at compile time | same / same |
| `bi0256` | BUILTIN:256 | suspend_until is legal only inside an async function: in a sync function it is refused. | `refuse` | npkc 1 EMIT-002, -/- (`emit_defect`) | F-027 b: `suspend_until` in a sync function passes the checker and is EMIT-002 | same / same |
| `bi0261` | BUILTIN:261 | close(release_fd(move o)) consumes the owner and closes once, reporting close's verdict. | `run:0` | npkc 1 PARSE-001, -/- (`refused`) | F-028: `close(release_fd(move o))` is PARSE-001; the spelling is `move(o)` | same / same |
| `bi0348` | BUILTIN:348 | An argument that is a nested bare-builtin call is refused (bind it to a typed name first). | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: sys's nested bare-builtin refusal is stale since D-201 | same / same |
| `bi0368` | BUILTIN:368 | The compiler has a `--seccomp` option (a kernel-enforced allowlist). | `sh:0` | sh 1 (`wrong_exit`) | F-028: `--seccomp` exists in no tool | same / same |
| `bi0375` | BUILTIN:375 | `--extra-picky=no-sys` refuses a program that calls sys; without it the program compiles. | `sh:0` | sh 1 (`wrong_exit`) | F-028: `--extra-picky=no-sys` exists in no tool | same / same |
| `bi0417b` | BUILTIN:417 | #wild_ptr is legal only in wild context: into a binding not declared `wild` it is refused (D-019's reading). | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: #wild_ptr, #ptr_add, atomic_from_ptr accepted outside wild, which no reference defines | same / same |
| `bi0419b` | BUILTIN:419 | #ptr_add is legal only in wild context: over a buffer's pointer, outside wild, it is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: #wild_ptr, #ptr_add, atomic_from_ptr accepted outside wild, which no reference defines | same / same |
| `bi0432` | BUILTIN:432 | asm<T> wraps the output in Result<T>; a negative integer return is an error. | `run:0` | npkc 1 PARSE-002, -/- (`refused`) | F-028: §5's inline assembly (row and example) is PARSE-002 | same / same |
| `bi0439` | BUILTIN:439 | The example: x86_64 assembly adding 1 to its input, returning Result<int32>. | `run:0` | npkc 1 PARSE-002, -/- (`refused`) | F-028: §5's inline assembly (row and example) is PARSE-002 | same / same |
| `cc0021` | CONCURRENCY:21 | System threading uses no language keywords, so `thread` is an ordinary identifier. | `run:0` | npkc 1 PARSE-002, -/- (`refused`) | F-028: `thread` is a keyword (the spawn form), against 'no language keywords' | same / same |
| `cc0042` | CONCURRENCY:42 | The declaring-and-awaiting example compiles as written and exits 0. | `run:0` | npkc 1 TYPE-010,TYPE-083, -/- (`refused`) | F-028: the example's `main` has no parameter (TYPE-083, DEF-96's rule) | npkc 1 TYPE-010, -/- / same |
| `cc0059` | CONCURRENCY:59 | The three honest spellings (relay, `?\| fallback`, `?! 9tbb32`) compile, and each yields the callee's value when it succeeds. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-028: `?! 9tbb32` / `?! 7tbb32`: `?!` takes a declared Error (D-179) | same / same |
| `cc0062` | CONCURRENCY:62 | `await f() ?! 9tbb32` on a failing call traps to failsafe with code 9, which no named arm matches, so the catch-all arm answers. | `run:99` | npkc 1 TYPE-007, -/- (`refused`) | F-028: `?! 9tbb32` / `?! 7tbb32`: `?!` takes a declared Error (D-179) | same / same |
| `cc0066` | CONCURRENCY:66 | `await` in a synchronous function is refused with the code NITPICK-040. | `refuse:NITPICK-040` | npkc 1 TYPE-043, -/- (`other_code`) | F-028: `await` outside async is TYPE-043, not NITPICK-040 | same / same |
| `cc0073` | CONCURRENCY:73 | `drop work();` spawns an async function whose VALUE is discarded: a value-returning async callee is accepted in the spawn form. | `run:0` | npkc 1 TYPE-043, -/- (`refused`) | F-028: a spawned task must return NIL (D-177), against 'VALUE discarded' | same / same |
| `cc0080` | CONCURRENCY:80 | The join relays the first child error verbatim, and only after every child has finished: a slower sibling's value is already in the channel when the parent returns. | `run:0` | npkc 0 , 11/11 (`wrong_exit`) | F-020: the join relays the last-spawned child's error, not the first child error | same / same |
| `cc0130` | CONCURRENCY:130 | `async` lowers to `@llvm.coro` state machines: the emitted IR uses llvm.coro intrinsics. | `ir:@llvm\.coro\.` | npkc 0 , 0/0 (`ir`) | F-028: async lowers to no llvm.coro and no %Future type | same / same |
| `cc0132` | CONCURRENCY:132 | `Future<T>` is the handle `%Future = type { ptr, ptr }` (coroutine handle, result slot) in the emitted IR of an async program. | `ir:%Future = type \{ ptr, ptr \}` | npkc 0 , 0/0 (`ir`) | F-028: async lowers to no llvm.coro and no %Future type | same / same |
| `cc0142` | CONCURRENCY:142 | `await f()` yields `T` directly: `int32:x = await f(..)` compiles and x is the value. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-028: `await f()` yields Result<T> (line 53), not T (line 142) | same / same |
| `cc0243` | CONCURRENCY:243 | The three ways to obtain an atomic compile as written: scope storage, a struct field, and `atomic_from_ptr<int32>(hdr_ptr)` bound to a local. | `run:0` | npkc 1 PARSE-002, -/- (`refused`) | F-028: `atomic_from_ptr<int32>(p)` does not parse | same / same |
| `cc0250` | CONCURRENCY:250 | `atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr)` aliases existing memory: a store through lk is what the pointer reads. | `run:0` | npkc 1 PARSE-002, -/- (`refused`) | F-028: `atomic_from_ptr<int32>(p)` does not parse | same / same |
| `cc0298b` | CONCURRENCY:298 | A borrow may not cross an await point: a borrow held across an `await` and used after it is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: a borrow may cross an await since D-180 (spawn only) | same / same |
| `cc0298c` | CONCURRENCY:298 | A borrow may not cross an await point: passing `@x` into an awaited async callee that suspends while holding it is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: a borrow may cross an await since D-180 (spawn only) | same / same |
| `cc0321` | CONCURRENCY:321 | Destroying a shared arena needs no thread to hold it, by ownership: `destroy` while a spawned thread still borrows it is refused. | `refuse` | npkc 0 , 96/96 (`accepted`) | F-022: destroy of a shared arena a live thread holds is accepted; the program ends in WildLeak | same / same |
| `cc0380` | CONCURRENCY:380 | A channel's LEVEL is a D-056 lock level: a send on a level-4 channel while holding a level-5 mutex guard is a downward acquisition and is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: a channel's LEVEL is not checked against a held mutex's (a downward send is accepted) | same / same |
| `cc0426` | CONCURRENCY:426 | Expiry is the error `DEADLINE_EXCEEDED`: an expired recv's error compares equal to it. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: the identity is DeadlineExceeded, not DEADLINE_EXCEEDED | same / same |
| `cc0501` | CONCURRENCY:501 | `Actor<M, R, LEVEL>` is a type with `tell` (Result<NIL>) and `ask` (Result<R>), each taking a moved message and a deadline. | `run:0` | npkc 1 TYPE-001,TYPE-043, -/- (`refused`) | F-028: there is no Actor type | same / same |
| `cc0523` | CONCURRENCY:523 | With R = NIL, `ask` is an acknowledgement: it yields Result<NIL>. | `run:0` | npkc 1 TYPE-001,TYPE-043, -/- (`refused`) | F-028: there is no Actor type | same / same |
| `cc0535` | CONCURRENCY:535 | `ThreadPool<LEVEL, CAP>:pool = ThreadPool.create(n)?;` and `await pool.submit(move(job), deadline)?;` compile and run. | `run:0` | npkc 1 PARSE-011, -/- (`refused`) | F-028: `ThreadPool.create(n)?` is two stale spellings (a bare `?`, a static method) | same / same |
| `cc0568b` | CONCURRENCY:568 | `timedwait` is the form: with no signal it returns an error when its deadline expires. | `run:0` | npkc 0 , 10/10 (`wrong_exit`) | F-021: timedwait that expires with no signal reports success | same / same |
| `io0022` | IO:22 | `Stream` is the trait every readable or writable thing implements: it can bound a generic parameter. | `run:0` | npkc 1 TYPE-001, -/- (`refused`) | F-028: there is no Stream trait | same / same |
| `io0045` | IO:45 | Every stream operation is async: `r.read(..)` without await is refused. | `refuse` | npkc 0 , llc!1/opt!1 (`accepted`) | F-023: an un-awaited async METHOD call is accepted and emits a call to an undefined symbol | same / same |
| `io0075` | IO:75 | End of input is the error code `E_EOF`: a read of an exhausted stream fails with it. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: the EOF identity is IoEof, not E_EOF | same / same |
| `io0115` | IO:115 | `TextWriter:w = text_writer_create(sink, LineEnding.Lf) ?! …;` and the CrLf twin build text writers; the CrLf one writes `\r\n`. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: the constructor is text_writer, not text_writer_create | same / same |
| `io0212` | IO:212 | `close(release_fd(move o))` closes an owned descriptor and reports the verdict: the reader then sees end of input. | `run:0` | npkc 1 PARSE-001, -/- (`refused`) | F-028: `close(release_fd(move o))` is PARSE-001; the spelling is `move(o)` | same / same |
| `io0232` | IO:232 | Seeking a buffered stream discards its read buffer: after a text reader has read `ab` (buffering `cd`), seeking to the start and reading gives `ab` again. | `run:0` | npkc 1 TYPE-019,TYPE-043, -/- (`refused`) | F-028: no buffered stream has seek | same / same |
| `io0242b` | IO:242 | The standard streams belong to main's scope and are passed down: constructing one in a helper function is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: the standard streams are not confined to main's scope | same / same |
| `mc0046b` | MACRO:46 | "is whatever `b` is": an alias whose target is a declaration macro, invoked at module level, emits the target's declarations. | `run:0` | npkc 1 MACRO-005, -/- (`refused`) | F-027 c: an alias of a declaration macro is refused at module level (MACRO-005), against D-125 | same / same |
| `mc0085b` | MACRO:85 | A variable declaration carrying a qualifier (`fixed`) spliced into a struct body is refused rather than stripped: "a field has neither". | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: a `fixed` qualifier spliced into a struct body is stripped, not refused | same / same |
| `mc0112` | MACRO:112 | The emit_helpers example: three emitted declarations referencing each other; helper_sum is 42. | `run:0` | npkc 1 MACRO-009,TYPE-042, -/- (`refused`) | F-028: the example uses `raw` on a callee that is not never fails (D-163) | same / same |
| `mc0136` | MACRO:136 | The emit_methods example: `impl:Box:Pair = { #emit_methods(); };` gives Box the method add_one. | `run:0` | npkc 3 , -/- (`crash`) | F-024: npkc traps (exit 3) on a macro emitting a method into an impl | same / same |
| `mc0159` | MACRO:159 | The hygiene example: `#report()` reads the TOP-LEVEL `shared` (100), not main's local 5, so the template is "shared = 100". | `run:0` | npkc 1 TYPE-055, -/- (`refused`) | F-028: the example's mutable module binding is refused (D-211) | same / same |
| `mc0188` | MACRO:188 | `#caller(NAME)` differs from the bare name exactly when the invocation site has a local binding of it. | `run:0` | npkc 0 , 11/11 (`wrong_exit`) | F-018: a macro's free name, alone or a comparison's operand, reads the call site's local | same / same |
| `mc0202` | MACRO:202 | A statement invocation becomes a block whose parent is the module scope: a free name in it reads the module binding past the caller's local of the same name. | `run:0` | npkc 0 , 11/11 (`wrong_exit`) | F-018: a macro's free name, alone or a comparison's operand, reads the call site's local | same / same |
| `mc0246` | MACRO:246 | `macro:m = () { #m(); };      // refused` — the self-invoking declaration is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: a self-invoking macro declaration is accepted while it is never invoked | same / same |
| `mc0250` | MACRO:250 | A depth bound limits one invocation's nesting: an expression body nested 1000 operators deep is refused as a compile error. | `refuse` | npkc 3 , -/- (`crash`) | F-024: npkc traps (exit 3) on a 500-deep expression, with or without a macro | same / same |
| `mc0251` | MACRO:251 | Exceeding the iteration bound is a compile error naming the macro and the chain that reached the bound: both ping_m and pong_m appear in the diagnostic. | `sh:0` | sh 3 (`wrong_exit`) | F-027 d: MACRO-004 names neither macro and points into prelude.npk | same / same |
| `mc0256` | MACRO:256 | The depth bound and the iteration bound are separate and report differently: a too-deep single expansion and a mutual recursion are refused with different diagnostic codes. | `sh:0` | sh 2 (`wrong_exit`) | F-024: npkc traps (exit 3) on a 500-deep expression, with or without a macro | same / same |
| `mc0278` | MACRO:278 | The expansion walk reaches every statement kind (a miss would arrive as a refusal): invocations in an if condition, a while condition and measure, a for body, a pick arm, a when body and then block, a nested block, a struct literal, an array literal, a call argument and a give all expand. | `run:0` | npkc 1 MACRO-006, -/- (`refused`) | F-027 b: an invocation in a while's `decreases` measure is never expanded (MACRO-006, a hole it names) | same / same |
| `mc0309b` | MACRO:309 | The evaluator handles string ordering: "ab" orders before "b". | `run:0` | npkc 1 TYPE-004, -/- (`refused`) | F-027 c: comptime does not fold `a.cmp(b)` on strings (TYPE-004); compiler or documentation | same / same |
| `mc0310b` | MACRO:310 | The evaluator folds the alignment intrinsic: `comptime(#align_of<int64>())` is 8. | `run:0` | npkc 1 MACRO-001, -/- (`refused`) | F-028: there is no #align_of | same / same |
| `mc0312` | MACRO:312 | `assert_static comptime(…)` is evaluated: a true proposition compiles. | `run:0` | npkc 1 PARSE-001, -/- (`refused`) | F-028: `assert_static comptime(...)` needs parentheses | same / same |
| `mc0327` | MACRO:327 | Expansion runs to a fixed point first, then evaluation runs over the result: a comptime function EMITTED by a macro can be evaluated. | `run:0` | npkc 3 , -/- (`crash`) | F-024: npkc traps (exit 3) on a macro emitting a comptime function | same / same |
| `mc0332` | MACRO:332 | A `const` global folds: `comptime(N * 2i32)` over `const int32:N = 4i32;` is 8. | `run:0` | npkc 1 PARSE-001, -/- (`refused`) | F-028: `const` is gone and `fixed` folds (D-222) | same / same |
| `mc0334` | MACRO:334 | A `fixed` binding is not a constant: `comptime(F * 2i32)` over `fixed int32:F` is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: `const` is gone and `fixed` folds (D-222) | same / same |
| `mc0344` | MACRO:344 | A comptime failure inside nested comptime calls names the offending expression and the call chain: the diagnostic mentions inner_div and outer_call and points at the division. | `sh:0` | sh 3 (`wrong_exit`) | F-027 d: a comptime failure's diagnostic names no call chain | same / same |
| `mc0369c` | MACRO:369 | This language writes `#align_of<T>()`: `#align_of<int64>()` is 8. | `run:0` | npkc 1 MACRO-001, -/- (`refused`) | F-028: there is no #align_of | same / same |
| `mc0371` | MACRO:371 | The corpus's width-less literals (`0`, `10`, `exit 1`) are not this language: they are refused (literals carry their width). | `refuse` | npkc 0 , 1/1 (`accepted`) | F-028: unsuffixed literals are accepted in a typed context | same / same |
| `ty0017` | TYPE:17 | The fundamental scalars map directly to LLVM primitive types: an int16 function is `i16` in, `i16` out, and a flt32 one `float`. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi16 @"?(?:[\w$]+\.)*m11s16"?\(i16 )(?=.*?^define [^@\n]*\bfloat @"?(?:[\w$]+\.)*m11f32"?\(float )` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0032` | TYPE:32 | A bool local is an `i8` alloca, and a branch on it truncates the loaded `i8` to `i1`. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11bl"?\((?=(?:(?!\n\}).)*?alloca i8\b)(?=(?:(?!\n\}).)*?trunc i8 %\S+ to i1)` | npkc 0 , 0/0 (`ir`) | F-028: a bool branch is `icmp ne`, not `trunc` | same / same |
| `ty0144` | TYPE:144 | tbb arithmetic uses the same overflow intrinsics: a tbb32 `+` lowers through llvm.sadd.with.overflow.i32. | `ir:(?s)^define [^@\n]*@"?(?:[\w$]+\.)*m11tb"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i32\()` | npkc 0 , 0/0 (`ir`) | F-028: tbb arithmetic does not use the with.overflow intrinsics | same / same |
| `ty0174g` | TYPE:174 | flt128 is `fp128` in the IR. | `ir:^define [^@\n]*\bfp128 @"?(?:[\w$]+\.)*m11fp"?\(fp128 ` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0176` | TYPE:176 | `flt256` is not a type: a binding declared with it is refused. | `refuse` | npkc 1 EMIT-002, -/- (`emit_defect`) | F-027 a: `flt256` passes the checker and is refused by the emitter (EMIT-002) | same / same |
| `ty0178` | TYPE:178 | The `f512` literal suffix is gone: `1.5f512` is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: the `f512` suffix, gone by TYPE:178 and absent from LEXICAL:315, is accepted | same / same |
| `ty0189b` | TYPE:189 | The spelling `3.14flt32` does not lex: it is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: the `flt32` suffix, never a suffix by TYPE:189 and LEXICAL:315, is accepted | same / same |
| `ty0239` | TYPE:239 | `toUpper` uppercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0240` | TYPE:240 | `toLower` lowercases an ASCII letter and leaves every other char8 unchanged (ASCII range only). | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0241` | TYPE:241 | `isAlpha` is true for letters and false for a digit and for the bytes beside 'A' and 'Z'. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0242` | TYPE:242 | `isDigit` is true for '0' through '9' only. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0243` | TYPE:243 | `isAlphaNumeric` is true for a letter or a digit and false otherwise. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0244` | TYPE:244 | `isWhitespace` is true for exactly space, tab, CR and LF: vertical tab and form feed are not in the list. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0245` | TYPE:245 | `isUpper` is true for 'A' through 'Z' only. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0246` | TYPE:246 | `isLower` is true for 'a' through 'z' only. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0247` | TYPE:247 | `toUint` reinterprets a char8 as its uint8 byte. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0248` | TYPE:248 | `fromUint` reinterprets a uint8 as the char8 of that byte. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0249` | TYPE:249 | `toChar16` zero-extends a char8: '\xE9' becomes 233char16. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0250` | TYPE:250 | `toChar32` zero-extends a char8: '\xFF' becomes 255char32. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §2's char8 function table names functions that do not exist | same / same |
| `ty0272` | TYPE:272 | The character literals compile to their code units: '\n' 10, '\t' 9, '\0' 0, '\\' 92, '\'' 39, '\x41' 'A', and '\u{1F600}' in a char32 is U+1F600. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-019: a \u{...} escape is a char8, truncated to its low byte; a char32 cannot take it | same / same |
| `ty0280` | TYPE:280 | The `\u{...}` escape is for char32 only: in a char8 slot it is refused. | `refuse` | npkc 0 , 10/10 (`accepted`) | F-019: a \u{...} escape is a char8, truncated to its low byte; a char32 cannot take it | same / same |
| `ty0285` | TYPE:285 | The example compiles: a char8[5] holds 5 chars, `cstring:cs = "Hello";` is a cstring of length 5, and `to_cstring` of a clean string succeeds. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-027 c: a string literal in cstring position is refused (TYPE-007); compiler or documentation | same / same |
| `ty0290` | TYPE:290 | A string literal in cstring position is a cstring: `cstring:cs = "Hello";` compiles with length 5. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-027 c: a string literal in cstring position is refused (TYPE-007); compiler or documentation | same / same |
| `ty0306` | TYPE:306 | A nit takes the values 0 to 8: `nit:n = 8;` holds 8. | `run:0` | npkc 1 TYPE-031, -/- (`refused`) | F-028: nit and nyte ranges are §6's balanced ones (D-197), not 0-8 / 2 nits | same / same |
| `ty0307` | TYPE:307 | A nyte is 2 nits holding 0 to 80: `nyte:n = 81;` is out of range and refused. | `refuse` | npkc 0 , 10/10 (`accepted`) | F-028: nit and nyte ranges are §6's balanced ones (D-197), not 0-8 / 2 nits | same / same |
| `ty0308` | TYPE:308 | `tensor` is a native primitive: `tensor<flt64>` names a type with no import. | `run:0` | npkc 1 TYPE-001, -/- (`refused`) | F-028: tensor and matrix are not types (P4, line 2120) | same / same |
| `ty0309` | TYPE:309 | `matrix` is a native primitive: `matrix<flt64>` names a type with no import. | `run:0` | npkc 1 TYPE-001, -/- (`refused`) | F-028: tensor and matrix are not types (P4, line 2120) | same / same |
| `ty0330` | TYPE:330 | Pointers are thin: an `int8->` parameter is one `ptr`, with no bounds metadata. | `ir:^define [^@\n]*\bi8 @"?(?:[\w$]+\.)*m11tp"?\(ptr ` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0338` | TYPE:338 | A `string` is the struct `{ ptr, i64, i64 }`: a string parameter has that type. | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11sl"?\(\{ ?ptr, i64, i64 ?\} ` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0348` | TYPE:348 | The data pointer is at offset 0: the struct opens with `ptr` ({ptr, i64, i64}). | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11sd"?\(\{ ?ptr, i64, i64 ?\} ` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0359b` | TYPE:359 | `string_eq(a, b)` compares byte by byte. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0366` | TYPE:366 | `s[i]` returns the char at that index. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | DEF-133 (F-017 d1, d2): TYPE §3.2's `s.length` and `s[i]` | same / same |
| `ty0366b` | TYPE:366 | String indexing is bounds-checked: past the end traps OutOfBounds. | `run:94` | npkc 1 TYPE-007, -/- (`refused`) | DEF-133 (F-017 d1, d2): TYPE §3.2's `s.length` and `s[i]` | same / same |
| `ty0367` | TYPE:367 | A string's length is the field `s.length`. | `run:0` | npkc 1 TYPE-019, -/- (`refused`) | DEF-133 (F-017 d1, d2): TYPE §3.2's `s.length` and `s[i]` | same / same |
| `ty0373` | TYPE:373 | `charAt(s, i)` is the char at index i. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0373b` | TYPE:373 | `charAt` is bounds-checked: an index past the end traps OutOfBounds. | `run:94` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0374` | TYPE:374 | `substring(s, start, length)` extracts `length` chars from `start`. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0375` | TYPE:375 | `split(s, c)` splits by the delimiter into its parts. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0376` | TYPE:376 | `trim` removes leading and trailing whitespace. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0377` | TYPE:377 | `trimLeft` removes leading whitespace only. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0378` | TYPE:378 | `trimRight` removes trailing whitespace only. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0379` | TYPE:379 | `contains(s, t)` is a substring search. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0380` | TYPE:380 | `startsWith(s, p)` is a prefix check. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0381` | TYPE:381 | `endsWith(s, p)` is a suffix check. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0382` | TYPE:382 | `indexOf(s, c)` is the first occurrence's index, -1 if not found. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0383` | TYPE:383 | `toUpper(s)` uppercases the ASCII letters and leaves other bytes alone. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0384` | TYPE:384 | `toLower(s)` lowercases the ASCII letters and leaves other bytes alone. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0385` | TYPE:385 | `toCharArray(s, dest)` copies into a caller-owned destination and returns the elements written. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0386` | TYPE:386 | `fromCharArray(a)` copies a char array into a string. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0388` | TYPE:388 | `to_string(c)` copies a cstring out into a string. | `run:0` | npkc 1 RESOLVE-002, -/- (`refused`) | F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist | same / same |
| `ty0395` | TYPE:395 | `cstring` is `{ ptr, len }`: a cstring parameter is the struct `{ ptr, i64 }`. | `ir:^define [^@\n]*\bi64 @"?(?:[\w$]+\.)*m11cl"?\(\{ ?ptr, i64 ?\} ` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0414` | TYPE:414 | A string literal in cstring position costs nothing at run time: it is a NUL-terminated constant. | `ir:constant \[4 x i8\] c"abc\\00"` | npkc 1 TYPE-007, -/- (`refused`) | F-027 c: a string literal in cstring position is refused (TYPE-007); compiler or documentation | same / same |
| `ty0456` | TYPE:456 | Wide integers are the LLVM types: an int256 function takes and returns `i256` and adds through the i256 intrinsic. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11w"?\(i256 )(?=.*?^define [^@\n]*@"?(?:[\w$]+\.)*m11w"?\((?=(?:(?!\n\}).)*?@llvm\.sadd\.with\.overflow\.i256\())` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0475` | TYPE:475 | The wide integers have D-037 wrapping: an int128 `+` past the maximum wraps to the minimum. | `run:0` | npkc 0 , 93/93 (`wrong_exit`) | DEF-133 (F-017 d5): TYPE §4's D-037 wrapping sentence | same / same |
| `ty0507` | TYPE:507 | tfp values compare with all six operators and `<=>`, which yields -1, 0 or 1. | `run:0` | npkc 1 EMIT-002, -/- (`emit_defect`) | DEF-131 (F-015): `<=>` refused by the emitter | same / same |
| `ty0553` | TYPE:553 | Only dim256 takes a unit annotation: `tfp64<Meters>` is refused. | `refuse` | npkc 0 , 10/10 (`accepted`) | F-026: tfp64<Meters> is accepted and its unit ignored, so a unit error compiles | same / same |
| `ty0580` | TYPE:580 | Unit declarations of this form compile, and a declared name is its vector's name (Furlongs is Meters). | `run:0` | npkc 1 RESOLVE-001, -/- (`refused`) | F-028: the unit example redeclares prelude units (RESOLVE-001) | same / same |
| `ty0593` | TYPE:593 | `dim256<Joules>` is identical to tfp256 at the IR: functions over each take and return `i256`. | `ir:(?s)\A(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11dj"?\(i256 )(?=.*?^define [^@\n]*\bi256 @"?(?:[\w$]+\.)*m11tf"?\(i256 )` | npkc 0 , 0/0 (`ir`) | the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the value and parameter types are the claimed ones | same / same |
| `ty0616b` | TYPE:616 | Values of the same vector have the full ordering. | `run:0` | npkc 1 EMIT-002, -/- (`emit_defect`) | DEF-131 (F-015): `<=>` refused by the emitter | same / same |
| `ty0634b` | TYPE:634 | Declared to return bare tfp256, the same body `pass(d / t)` compiles. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-028: a bare tfp256 return needs the explicit `=> tfp256` (line 618) | same / same |
| `ty0648` | TYPE:648 | At the IR, dim256<Joules> is tfp256, whose type is `{ i64, i64, i64, i64 }`. | `ir:^%\"?tfp256\"? = type \{ ?i64, i64, i64, i64 ?\}|^define [^@\n]* @"?(?:[\w$]+\.)*m11dj"?\(\{ ?i64, i64, i64, i64 ?\} ` | npkc 0 , 0/0 (`ir`) | F-028: tfp256 is i256 at the IR, not { i64, i64, i64, i64 } | same / same |
| `vf0145b` | VERIFICATION:145 | A limit on main's parameter is refused: the sentence lists it among the TYPE-064 sites. | `refuse:TYPE-064` | npkc 1 TYPE-060, -/- (`other_code`) | F-028: a limit on main's parameter is TYPE-060, not TYPE-064 | same / same |
| `vf0151` | VERIFICATION:151 | A struct subject is outside the encoder's fragment: its limit row is unencoded (0 in rows.txt). | `sh:0` | sh 1 (`wrong_exit`) | F-028: a struct subject's limit row, and a List-count loop bound, are encoded | same / same |
| `vf0215b` | VERIFICATION:215 | A write through a shared ($$i) claim's holder is NITPICK-BORROW-013. | `refuse:BORROW-013` | npkc 0 , 0/0 (`accepted`) | DEF-123 (F-008): a write through a $$i claim's holder is not refused | same / same |
| `vf0268` | VERIFICATION:268 | A borrow may not be carried across an await point: a pointer local holding `@x` used after an await is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: a borrow may cross an await since D-180 (spawn only) | same / same |
| `vf0437` | VERIFICATION:437 | A function with a requires is never `never fails`: declaring one is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: a requires on a never-fails function is accepted (line 351 says so; line 437 not) | same / same |
| `vf0439` | VERIFICATION:439 | The example compiles and runs with §3's divide: `divide(10i32, 2i32) ?! 7tbb32` unwraps 10 and main exits 0. | `run:0` | npkc 1 TYPE-007, -/- (`refused`) | F-028: `?! 9tbb32` / `?! 7tbb32`: `?!` takes a declared Error (D-179) | same / same |
| `vf0548` | VERIFICATION:548 | A List's count as a loop's bound has no length term: the terminate rows are unencoded (0 in rows.txt). | `sh:0` | sh 1 (`wrong_exit`) | F-028: a struct subject's limit row, and a List-count loop bound, are encoded | same / same |
| `vf0808` | VERIFICATION:808 | `--extra-picky=no-wildx` excludes runtime code generation: a program without wildx compiles under it and one using wildx does not. | `sh:0` | sh 1 (`wrong_exit`) | F-025: --extra-picky=no-wildx refuses every program (256 WILDX-003 in the prelude) | same / same |
| `vf0811` | VERIFICATION:811 | no-wildx is a rule separate from no-wild: a program using `wild` (not wildx) compiles under no-wildx and not under no-wild. | `sh:0` | sh 1 (`wrong_exit`) | F-025: --extra-picky=no-wildx refuses every program (256 WILDX-003 in the prelude) | same / same |
| `vf0819` | VERIFICATION:819 | Borrows cannot cross an await: a $$i claim held by a pointer local across an await is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-028: a borrow may cross an await since D-180 (spawn only) | same / same |
| `vf0831` | VERIFICATION:831 | An undeclared dynamically dispatched method may not acquire at all: an impl of a trait method with no level acquiring one is refused. | `refuse` | npkc 0 , 0/0 (`accepted`) | F-027 a: a dyn method with no declared level may acquire one | same / same |
| `vf0860i` | VERIFICATION:860 | A loop over `xs.len` indexing `xs[i]` states the length as `\|npk.len\|` in its obligation file. | `sh:0` | sh 11 (`wrong_exit`) | F-028: `.len` is a per-binding `\|len.x.N\|` symbol, not `(\|npk.len\| base)` | same / same |
| `vf0861g` | VERIFICATION:861 | A `simd<flt64, 4> =>! simd<int32, 4>` is ONE `cast-range` row. | `sh:0` | sh 10 (`wrong_exit`) | F-028: a simd float-to-int cast has no cast-range row (its guard traps CastRange) | same / same |
| `vf0867b` | VERIFICATION:867 | A call of an ASYNC callee with a limited parameter has no `limit-subsume` row. | `sh:0` | sh 10 (`wrong_exit`) | F-028: an await of a coroutine with a limited parameter has a limit-subsume row | same / same |
| `vf0895` | VERIFICATION:895 | `.len` of a slice is the uninterpreted `\|npk.len\|` applied to the base in the obligation text. | `sh:0` | sh 11 (`wrong_exit`) | F-028: `.len` is a per-binding `\|len.x.N\|` symbol, not `(\|npk.len\| base)` | same / same |
| `vf0931` | VERIFICATION:931 | An async callee with a limited parameter has no `.body` twin and its call site no `limit-subsume` row. | `sh:0` | sh 10 (`wrong_exit`) | F-028: an await of a coroutine with a limited parameter has a limit-subsume row | same / same |
| `vf0983` | VERIFICATION:983 | A `flt32` literal is rounded twice, to double then to float: 1.0000000596046448309 (just above the midpoint 1 + 2^-24) becomes 1 + 2^-24 as a double and then 1.0 (a tie, to even) as a flt32, where a single rounding gives 1 + 2^-23. | `run:0` | npkc 1 TYPE-030, -/- (`refused`) | D-143's 15-digit cap on a flt32 literal makes double rounding unobservable; no valid program tests it | same / same |
| `vf1036` | VERIFICATION:1036 | A `limit` over a struct subject is an `unencoded` row (fifth field `0`). | `sh:0` | sh 11 (`wrong_exit`) | F-028: a struct subject's limit row, and a List-count loop bound, are encoded | same / same |
| `vf1149` | VERIFICATION:1149 | A `flt32` literal is rounded to double and then to float (1.0000000596046448309f32 is 1.0). | `run:0` | npkc 1 TYPE-030, -/- (`refused`) | D-143's 15-digit cap on a flt32 literal makes double rounding unobservable; no valid program tests it | same / same |
| `vf1201` | VERIFICATION:1201 | A float `simd` `.min()` folds with a select over the ordered strict compare, false on NaN, so a NaN lane is passed over: min of (1, 3, 0.5, NaN) is 0.5. | `run:0` | npkc 0 , 10/10 (`wrong_exit`) | F-028: a simd float .min() returns a NaN in the last lane | same / same |
| `vf1228b` | VERIFICATION:1228 | A `limit` over a struct subject is `unencoded`. | `sh:0` | sh 11 (`wrong_exit`) | F-028: a struct subject's limit row, and a List-count loop bound, are encoded | same / same |
| `vf1244` | VERIFICATION:1244 | Still at 1.5.8b: a `limit` over a struct is `unencoded` with its guard kept. | `sh:0` | sh 11 (`wrong_exit`) | F-028: a struct subject's limit row, and a List-count loop bound, are encoded | same / same |

## 3. Programs whose text changed after a run (59; no expectation changed but where stated)

| id | why |
|---|---|
| `bi0005` | run 1 wrote `list_init()`, refused TYPE-022 (T not inferable: the turbofish is the spelling), not for a missing import |
| `bi0051` | run 1 called the `never fails` method without `raw` (TYPE-007) |
| `bi0105b` | run 1 bound the result to an owning local, itself TYPE-061 (D-221); now the call alone |
| `bi0107` | run 1 bound the result to an owning local, which a pure body refuses (TYPE-061, D-221); now the call alone |
| `bi0109` | run 1 bound the result to an owning local, itself TYPE-061 (D-221); now the call alone |
| `bi0123b` | run 1 aliased through a call, refused BORROW-011 (a returned parameter is a borrow; D-223); the alias now goes through memory, its bits read back as an int64 and rebuilt by `#wild_ptr` (run 2: a pointer loaded back is BORROW-011 too) |
| `bi0147` | run 1 held the arena in `main` at `exit 0` and exited 96 (WildLeak): `exit` runs no drops (D-183); the arena is now made and dropped in a function |
| `bi0250b` | run 1's helper was not `never fails`, so `drop` was TYPE-042 (D-163) |
| `bi0257` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0259` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0260` | run 1's helper was not `never fails`, so `drop` was TYPE-042 (D-163) |
| `bi0262` | run 1 exited 0 from failsafe, which REACH-004 refuses (D-014: failsafe exits positive); the reference's answer is now exit 42, the claim unchanged |
| `bi0263` | run 1 exited 0 from failsafe, which REACH-004 refuses (D-014: failsafe exits positive); the reference's answer is now exit 42, the claim unchanged |
| `bi0267` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0269` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0269b` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0270` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0350` | run 1 discarded `close`'s Result with `drop`, which only a `never fails` callee licenses (TYPE-042, D-163); now bound |
| `bi0375` | run 1's script had a failsafe naming nothing, refused REACH-001 without the flag; it now names every identity |
| `bi0401` | run 1 compared with `==`, which a derived Eq does not give (TYPE-034); a derived Eq is called `a.eq(b)` |
| `bi0417` | run 1 returned a parameter into a wild binding, refused BORROW-011 (D-223); now the constructor alone |
| `cc0489` | a function that creates and returns a channel says `gives` after its parameter list (TYPE-007, D-183) |
| `cc0636` | `tid` is a reserved word (PARSE-002): the local is `t_id`; failsafe names every identity that can reach it (REACH-002); and the reference's answer is signalled with exit 42, since REACH-004 forbids failsafe an exit of 0 (S45's exception) |
| `cc0646` | failsafe carries a pick naming every identity that can reach it (REACH-001); the division that traps inside failsafe comes before it |
| `io0158` | the script's program named only IntOverflow in failsafe; REACH-002 demands every identity that can reach it (Unreachable, DeadlineExceeded, ...), so it now names them all |
| `io0163` | the script's program named only IntOverflow in failsafe; REACH-002 demands every identity that can reach it (Unreachable, DeadlineExceeded, ...), so it now names them all |
| `mc0312b` | it agreed for another reason: `assert_static comptime(...)` is refused for its spelling (PARSE-001; mc0312's row), so the program now writes `assert_static(comptime(...))` and the refusal it expects is the false proposition's |
| `ty0376` | the Python string made `\t` and `\n` a real tab and newline inside the literal (LEX-005); the escapes are now written as escapes |
| `ty0399b` | run 1: a cstring's `.ptr` is `uint8->`, not `char8->` (TYPE-007); run 2: a borrow cannot initialise a `wild` binding (BORROW-011, D-223): the bytes are now read through a view, `string_from_bytes(c.ptr, c.len + 1)`, as the compiler's own len_ceiling.npk reads a cstring |
| `ty0476b` | run 1 and run 2: a literal of 2^64 - 1 is outside the 64-bit literal envelope (LEX-004, D-148), even with a u64 suffix: the u64 maximum is computed (`0 -% 1`), and zero-extension is checked through its half, 2^63 - 1 |
| `vf0007` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0039` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0075` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0077` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0138b` | a refinement leads a Rules block's list (`{ limit<r>, clause }`, as vf0276's example): written after a clause it does not parse (PARSE-001); it now leads, which still tells the orders apart (0 traps LimitViolated by the refinement before the clause divides by it) |
| `vf0146` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0150` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0151` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0151b` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0152` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0153` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0244` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0306` | its inline filter matched main's rows by `vf0306.main`, but main's symbol is `@main` (both counts read 0 in runs 1 and 2): the filter is `$6 == "@main"` |
| `vf0397` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0398` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0400` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0405` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0413` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0422` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0481` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0500b` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0531` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0548` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0582` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0595` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0607` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0749` | the rows helper missed main's rows (its symbol is `@main`, not `<module>.main`): the helper was corrected in every script that embeds it |
| `vf0866c` | the field rule `$ > 0` refused the vacant value (TYPE-077); `$ >= 0` admits it, and the write points the claim counts are the same |
| `vf0866d` | run 1: the field rule `$ > 0` refused the vacant value (TYPE-077), now `$ >= 0`; run 2: reading `t` while its `$$m` claim lived is BORROW-013 (D-286): the pointer is `@t`, an address that claims nothing, so the write still goes through a pointer |

Run 1 against the final run: 1237 of 1262 programs identical (npkc, both legs, verdict); the
others are programs above, whose text changed (a text change that did not move
the verdict leaves its program identical).
