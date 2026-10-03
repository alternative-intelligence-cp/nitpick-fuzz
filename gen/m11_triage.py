"""M11 -- what triage found each disagreement to be (read by gen/m11_report.py).

GROUPS names the classes; CLASS maps every claim whose final run at HUNT2 disagrees
(results/9126350/m11.jsonl) to (group, what it is). Each finding's README carries
the measurements; here is one line per claim. `python3 gen/m11_triage.py` checks
that every disagreement has a class and every class a disagreement.
"""
import json, os

GROUPS = {
    "swa": "compiler: a silent wrong answer (F-018 to F-021)",
    "mem": "compiler: a lifetime rule not enforced, a use after destroy (F-022)",
    "ir": "compiler: accepted, then invalid IR (F-023)",
    "crash": "compiler: npkc traps, exit 3 (F-024)",
    "hang": "compiler: npkc does not terminate (F-041)",
    "flag": "compiler: a flag that refuses every program (F-025)",
    "unit": "compiler: a unit annotation accepted and ignored (F-026)",
    "comp": "compiler, lower priority: accepted though refused, a self-declared hole, refused though permitted, a diagnostic (F-027)",
    "doc": "documentation: the compiler right or safe, the reference wrong or stale (F-028)",
    "known": "known: deduplicated against KNOWN_DEFECTS.md",
    "strict": "not a finding: refused at compile time where the text says it traps",
    "extract": "not a finding: the program tests more than its sentence, or no valid program can test it",
}

CLASS = {}


def put(group, text, *ids):
    for i in ids:
        assert i not in CLASS, i
        CLASS[i] = (group, text)


# ---- compiler: silent wrong answers, memory, IR, crashes, flags, units
put("swa", "F-018: a macro's free name, alone or a comparison's operand, reads the call site's local", "mc0188", "mc0202")
put("swa", "F-019: a \\u{...} escape is a char8, truncated to its low byte; a char32 cannot take it", "ty0272", "ty0280")
put("swa", "F-020: the join relays the last-spawned child's error, not the first child error", "cc0080")
put("swa", "F-021: timedwait that expires with no signal reports success", "cc0568b")
put("mem", "F-022: destroy of a shared arena a live thread holds is accepted; the program ends in WildLeak", "cc0321")
put("ir", "F-023: an un-awaited async METHOD call is accepted and emits a call to an undefined symbol", "io0045")
put("crash", "F-024: npkc traps (exit 3) on a macro emitting a method into an impl", "mc0136")
put("crash", "F-024: npkc traps (exit 3) on a 500-deep expression, with or without a macro", "mc0250", "mc0256")
put("crash", "F-024: npkc traps (exit 3) on a macro emitting a comptime function", "mc0327")
put("flag", "F-025: --extra-picky=no-wildx refuses every program (256 WILDX-003 in the prelude)", "vf0808", "vf0811")
put("unit", "F-026: tfp64<Meters> is accepted and its unit ignored, so a unit error compiles", "ty0553")

# ---- compiler, lower priority (F-027)
put("comp", "F-027 a: `flt256` passes the checker and is refused by the emitter (EMIT-002)", "ty0176")
put("comp", "F-027 a: the `f512` suffix, gone by TYPE:178 and absent from LEXICAL:315, is accepted", "ty0178")
put("comp", "F-027 a: the `flt32` suffix, never a suffix by TYPE:189 and LEXICAL:315, is accepted", "ty0189b")
put("comp", "F-027 a: a `fixed` qualifier spliced into a struct body is stripped, not refused", "mc0085b")
put("comp", "F-027 a: a self-invoking macro declaration is accepted while it is never invoked", "mc0246")
put("comp", "F-027 a: a channel's LEVEL is not checked against a held mutex's (a downward send is accepted)", "cc0380")
put("comp", "F-027 a: a dyn method with no declared level may acquire one", "vf0831")
put("comp", "F-027 b: `suspend_until` in a sync function passes the checker and is EMIT-002", "bi0256")
put("comp", "F-027 b: an invocation in a while's `decreases` measure is never expanded (MACRO-006, a hole it names)", "mc0278")
put("comp", "F-027 c: a string literal in cstring position is refused (TYPE-007); compiler or documentation", "ty0285", "ty0290", "ty0414")
put("comp", "F-027 c: an alias of a declaration macro is refused at module level (MACRO-005), against D-125", "mc0046b")
put("comp", "F-027 c: comptime does not fold `a.cmp(b)` on strings (TYPE-004); compiler or documentation", "mc0309b")
put("comp", "F-027 d: MACRO-004 names neither macro and points into prelude.npk", "mc0251")
put("comp", "F-027 d: a comptime failure's diagnostic names no call chain", "mc0344")

# ---- documentation (F-028), by reference
put("doc", "F-028: #wild_ptr, #ptr_add, atomic_from_ptr accepted outside wild, which no reference defines", "bi0148c", "bi0417b", "bi0419b")
put("doc", "F-028: `close(release_fd(move o))` is PARSE-001; the spelling is `move(o)`", "bi0261", "io0212")
put("doc", "F-028: sys's nested bare-builtin refusal is stale since D-201", "bi0348")
put("doc", "F-028: `--seccomp` exists in no tool", "bi0368")
put("doc", "F-028: `--extra-picky=no-sys` exists in no tool", "bi0375")
put("doc", "F-028: §5's inline assembly (row and example) is PARSE-002", "bi0432", "bi0439")
put("doc", "F-028: `thread` is a keyword (the spawn form), against 'no language keywords'", "cc0021")
put("doc", "F-028: the example's `main` has no parameter (TYPE-083, DEF-96's rule)", "cc0042")
put("doc", "F-028: `?! 9tbb32` / `?! 7tbb32`: `?!` takes a declared Error (D-179)", "cc0059", "cc0062", "vf0439")
put("doc", "F-028: `await` outside async is TYPE-043, not NITPICK-040", "cc0066")
put("doc", "F-028: a spawned task must return NIL (D-177), against 'VALUE discarded'", "cc0073")
put("doc", "F-028: async lowers to no llvm.coro and no %Future type", "cc0130", "cc0132")
put("doc", "F-028: `await f()` yields Result<T> (line 53), not T (line 142)", "cc0142")
put("doc", "F-028: `atomic_from_ptr<int32>(p)` does not parse", "cc0243", "cc0250")
put("doc", "F-028: a borrow may cross an await since D-180 (spawn only)", "cc0298b", "cc0298c", "vf0268", "vf0819")
put("doc", "F-028: the identity is DeadlineExceeded, not DEADLINE_EXCEEDED", "cc0426")
put("doc", "F-028: there is no Actor type", "cc0501", "cc0523")
put("doc", "F-028: `ThreadPool.create(n)?` is two stale spellings (a bare `?`, a static method)", "cc0535")
put("doc", "F-028: there is no Stream trait", "io0022")
put("doc", "F-028: the EOF identity is IoEof, not E_EOF", "io0075")
put("doc", "F-028: the constructor is text_writer, not text_writer_create", "io0115")
put("doc", "F-028: no buffered stream has seek", "io0232")
put("doc", "F-028: the standard streams are not confined to main's scope", "io0242b")
put("doc", "F-028: the example uses `raw` on a callee that is not never fails (D-163)", "mc0112")
put("doc", "F-028: the example's mutable module binding is refused (D-211)", "mc0159")
put("doc", "F-028: there is no #align_of", "mc0310b", "mc0369c")
put("doc", "F-028: `assert_static comptime(...)` needs parentheses", "mc0312")
put("doc", "F-028: `const` is gone and `fixed` folds (D-222)", "mc0332", "mc0334")
put("doc", "F-028: unsuffixed literals are accepted in a typed context", "mc0371")
put("doc", "F-028: a bool branch is `icmp ne`, not `trunc`", "ty0032")
put("doc", "F-028: tbb arithmetic does not use the with.overflow intrinsics", "ty0144")
put("doc", "F-028: TYPE §2's char8 function table names functions that do not exist",
    *["ty%04d" % n for n in range(239, 251)])
put("doc", "F-028: TYPE §3.2's string function table (and string_eq) names functions that do not exist",
    "ty0359b", "ty0373", "ty0373b", "ty0374", "ty0375", "ty0376", "ty0377", "ty0378", "ty0379", "ty0380",
    "ty0381", "ty0382", "ty0383", "ty0384", "ty0385", "ty0386", "ty0388")
put("doc", "F-028: nit and nyte ranges are §6's balanced ones (D-197), not 0-8 / 2 nits", "ty0306", "ty0307")
put("doc", "F-028: tensor and matrix are not types (P4, line 2120)", "ty0308", "ty0309")
put("doc", "F-028: the unit example redeclares prelude units (RESOLVE-001)", "ty0580")
put("doc", "F-028: a bare tfp256 return needs the explicit `=> tfp256` (line 618)", "ty0634b")
put("doc", "F-028: tfp256 is i256 at the IR, not { i64, i64, i64, i64 }", "ty0648")
put("doc", "F-028: a limit on main's parameter is TYPE-060, not TYPE-064", "vf0145b")
put("doc", "F-028: a struct subject's limit row, and a List-count loop bound, are encoded", "vf0151", "vf0548", "vf1036", "vf1228b", "vf1244")
put("doc", "F-028: a requires on a never-fails function is accepted (line 351 says so; line 437 not)", "vf0437")
put("doc", "F-028: `.len` is a per-binding `|len.x.N|` symbol, not `(|npk.len| base)`", "vf0860i", "vf0895")
put("doc", "F-028: a simd float-to-int cast has no cast-range row (its guard traps CastRange)", "vf0861g")
put("doc", "F-028: an await of a coroutine with a limited parameter has a limit-subsume row", "vf0867b", "vf0931")
put("doc", "F-028: a simd float .min() returns a NaN in the last lane", "vf1201")

# ---- session 8: MEMORY_REFERENCE (documentation rows are F-030)
put("doc", "F-030: wildx_alloc's result is `int8->`: the example's `wildx uint8->:code = wildx_alloc(4096i64);` "
    "is TYPE-007 (VERIFICATION's own programs cast it `=>! wildx uint8->`)", "me0126")
put("doc", "F-030: #wild_ptr is accepted outside wild context, against MEMORY:133 (D-019); D-315 struck the "
    "like rule from #wild_slice", "me0133")
put("doc", "F-030: #wild_ptr's type argument is the pointee: the example's `#wild_ptr<int8->>(addr)` is "
    "`int8->->` (TYPE-007)", "me0135")
put("doc", "F-030: `nodrop` qualifies a wild binding (DECISIONS: \"nodrop requires wild or wildx\"); "
    "`= nodrop alloc(...)` does not parse", "me0173")
put("doc", "F-030: the move example uses malloc/free (§3:281: no aliases), a binding named `buffer` (a "
    "reserved word) and the code NITPICK-019; it does not compile", "me0183")
put("doc", "F-030: the arena example and its note use a bare `?` as the fallback; it is `?|` since D-175 "
    "(PARSE-011)", "me0381", "me0399")
put("doc", "F-030: an un-destroyed arena<T> is not a leak the exit check names: its storage is managed "
    "since D-183 (1.2.5c; the runtime's npk_arena_make says so)", "me0397")
put("known", "DEF-148 (F-022): destroy of a shared arena a live thread holds; refused BORROW-016 at 93bcb66",
    "me0461")

# ---- session 8: OP_REFERENCE (documentation rows are F-031)
put("doc", "F-031: there is no `**` operator (OP:88, \"Standard Library expansion\"): `2 ** 8` does not parse",
    "op0088")
put("doc", "F-031: line 171's \"a fallback (`?`)\" leaves the ERR state: a bare `?` is struck (line 73, D-175), and "
    "`?|` takes a Result only (line 257); ERR leaves by is_err or a pick's ERR: arm", "op0171")
put("doc", "F-031: the ternary example `is x > 0 : 1 : -1` needs its condition parenthesised (PARSE-001; "
    "TYPE:2101's `is (cond) : then : else`)", "op0374")
put("doc", "F-031: the pipe examples `val |> func()` and `func() <| val` are refused: a pipe's other side is "
    "the function itself, not a call (TYPE-007)", "op0377", "op0378")
put("known", "DEF-131 (F-015): `<=>` refused by the emitter; it compiles and runs at 93bcb66", "op0068", "op0213")
put("extract", "no well-typed program tells the two readings apart: `|` takes integers and `&&` booleans "
    "(TYPE-008), so `a | b && c` is ill-typed either way", "op0028")
put("extract", "the program's `!!b` is two negations, which nothing forbids; the struck `!!` is the old "
    "emphatic token (`asm!!`), refused elsewhere (BUILTIN's bi0378)", "op0295")

# ---- session 8: CONTROL_REFERENCE (documentation rows are F-032)
put("doc", "F-032: the fallthrough example calls `println`, which no prelude declares (RESOLVE-002)", "ct0034")
put("doc", "F-032: the guards-and-macros example's pattern `MyMacro!(a, b) where (a > b)` is removed "
    "(PARSE-001; MACRO:374, and macro invocation is `#name(args)`)", "ct0080")
put("doc", "F-032: §4.2 names NITPICK-IF-002, -IF-001 and -WHEN-001; the compiler refuses each program with a "
    "PARSE code (OP:65: IF-002 \"describes a diagnostic for a program that cannot be written\")",
    "ct0314", "ct0317", "ct0319")
put("doc", "F-032: `ok()` is not \"the taint-clearing builtin\" (CONTROL:347): it is removed (D-097, OP:172)",
    "ct0347")
put("known", "DEF-133 (F-017 d6): a for binding of another type is TYPE-007, not TYPE-033", "ct0187")
put("known", "DEF-130 (F-014): till with a non-positive limit; agrees at 93bcb66", "ct0235", "ct0258")
put("known", "DEF-135 (the compiler seat's own, registered at 1.6.1d step 2): a tbb bound holding ERR ran the "
    "loop in silence; traps TbbErr at 93bcb66", "ct0236")

# ---- session 9: MODULE_REFERENCE (documentation rows are F-033, compiler rows F-034)
put("comp", "F-034 a: an extern method taking a byte payload (`int8[]`, or `uint8[]`; both in the v1 vocabulary) "
    "generates a stub the compiler refuses: TYPE-072 at `<bridge-1>:10:5`, a `while` stating no `decreases`",
    "md0270c")
put("comp", "F-034 b: the single-name form over a logical path (`use network.connect;`, `use helpers.f;`, "
    "`use core.math.sq;`) is RESOLVE-002, \"is a function, not a module\", against MODULE:68, :111 and :119 "
    "and D-273 (2), which lists `use hidden.f;`", "md0068b", "md0105", "md0119")
put("comp", "F-034 c: a constant cycle's diagnostic says each member \"is initialised from itself\"; it never "
    "names the members in the order they refer to each other (MODULE:183)", "md0183")
put("doc", "F-033: `pub const int32:MAX = 100i32;` does not parse (PARSE-001): a module constant is `fixed`",
    "md0209", "md0212")
put("doc", "F-033: the `cuda_driver` example is EXTERN-001: its `opaque struct` tier \"is reserved for the "
    "LOAD_MODULE work and does not lower yet (D-190)\", and its methods take no `Bridge->` first and no "
    "`Duration` last", "md0241")
put("doc", "F-033: the wire vocabulary is v1's (D-190): a method's parameters are `int32`, `int64`, `int8[]` or "
    "`uint8[]`; a POD struct, an `int16` and a typed handle are each EXTERN-001", "md0270", "md0270b", "md0270d")
put("doc", "F-033: the example's `raw some_query(name)` and `_! some_query(name)` are TYPE-042: `raw`, which "
    "`_!` spells too, needs a `never fails` callee (D-163), and a driver method never is one (MODULE:263-266, "
    "EXTERN-002)", "md0289")
put("known", "DEF-153 (F-027 c): a string literal in `cstring` position is TYPE-007; it compiles at 93bcb66",
    "md0296b")
put("extract", "the sentence gives the refusal's sense, \"is not a module\"; the compiler refuses (RESOLVE-002) "
    "and says \"`helper` is a function, not a module\"", "md0122")
put("extract", "the two IRs hold the same lines: only `fb`'s definition moves with the import order. The script "
    "demanded a byte-identical file, which is more than \"the same program\"", "md0185")

# ---- session 9: LEXICAL_REFERENCE (documentation rows are F-035, compiler rows F-036)
put("comp", "F-036 a: four keywords (`acquire`, `any`, `trit`, `nit`) are accepted as a module-level function's "
    "name, and the function can never be called (PARSE-002 at the call): DEF-103's fix exempts them at every "
    "function site, for the method names it meant", "lx0054", "lx0114", "lx0121")
put("comp", "F-036 b: a decimal literal ending in an underscore (`10_i32`) is accepted, against "
    "`DecimalLiteral ::= [0-9] ([0-9_]* [0-9])?`", "lx0296b")
put("doc", "F-035: `++` and `--` are listed as operator tokens; they are removed (D-174), PARSE-010", "lx0174")
put("doc", "F-035: the full-tier syscall is not spelled `sys_full`: no such builtin (RESOLVE-002); the syscall "
    "builtin is `sys`", "lx0256")
put("doc", "F-035: `f128` is listed as a literal suffix, and `flt128` is a storage format with no literals "
    "(TYPE-030, D-143)", "lx0315")
put("doc", "F-035: \"`0u64 - 1u64` is the maximum\" (LEXICAL:324) is TYPE-076, as the note at LEXICAL:328-331 "
    "says", "lx0324")
put("doc", "F-035: the LBIM note (LEXICAL:353-354) is dead (TYPE:449): `5i2048` is a literal, and there is no "
    "`parse_uint2048`", "lx0353", "lx0354")
put("known", "DEF-131 (F-015): `<=>` refused by the emitter (EMIT-002); it compiles and runs at 93bcb66", "lx0178")

# ---- session 9: AST_REFERENCE (F-037 memory, F-038 crash, F-039 lower-priority compiler rows,
#      F-040 documentation rows)
put("mem", "F-037: a trait object built by `x => dyn Trait` reads freed memory: its method returns the "
    "0xAA poison (170), where the implicit `dyn Trait:d = move(x);` returns the field", "as0453")
put("crash", "F-038: npkc traps (exit 3, no diagnostic) on `give` or `fall` outside a pick arm",
    "as0202", "as0203", "as0267")
put("comp", "F-039 a: a function with a `comptime` value parameter passes the checker and is EMIT-002 (a hole "
    "the compiler names)", "as0062")
put("comp", "F-039 b: the backward pipe takes its function on the RIGHT, as `|>` does: `dbl <| x` is "
    "TYPE-007, and `x <| dbl` computes dbl(x) (OP:378 says it passes to the LEFT function)", "as0301")
put("comp", "F-039 c: a `joins` deadline that is no constant expression is accepted (a call; a parameter's "
    "call, measured by hand)", "as0555")
put("comp", "F-039 d: an attribute the language does not have is accepted and ignored: the removed "
    "`#[lexical_drop]`, and `#[nosuch_attribute]` (measured by hand)", "as0583")
put("comp", "F-039 e: an `opaque struct` is accepted at module level, against AST:43 and TRAITS:368 (extern-block "
    "item only, D-066 as narrowed by D-149); inside an `extern` block it is EXTERN-001, a tier reserved (D-190)",
    "as0043")
put("extract", "the sentence names the LOWERING of an inherent method (TRAITS:132: `impl:Point`'s `magnitude` is "
    "`Point_magnitude(p)`); the program declared a free function of that name, which the sentence does not "
    "say is reached. UFCS itself holds: `p.magnitude()` reaches a free `magnitude(p)` (measured by hand)", "as0365")
DOC40 = (
    ("F-040: `pub const int32:MAX = 100i32;` and a `const` local qualifier do not parse (PARSE-001): `const` "
     "is retired (AST:505 says so)", ("as0044", "as0499")),
    ("F-040: `unit:Hertz = 1 / Seconds;` is RESOLVE-001: the prelude declares `Hertz` (another name compiles)",
     ("as0045",)),
    ("F-040: `failsafe` takes one `Error` (TYPE-044, D-179), not `tbb32:err`", ("as0093",)),
    ("F-040: an extern method's failure contract is not required (it compiles without one) and `never fails` "
     "on one is EXTERN-002: D-149 removed the contracts (MODULE:263-266)", ("as0128", "as0137")),
    ("F-040: a Result literal's `err` is an `Error` (D-179): `err: 0i32` is TYPE-007, and a success literal "
     "omits `err` (TYPE:1330)", ("as0195", "as0307")),
    ("F-040: `FFhex` is an identifier (D-147, LEXICAL:337), not a literal (RESOLVE-002)", ("as0281",)),
    ("F-040: `++` and `--` are removed (D-174, PARSE-010)", ("as0297",)),
    ("F-040: generic arguments in an expression take the turbofish (LEXICAL:239, D-064): `f<int32>(x)` is "
     "PARSE-002", ("as0364",)),
    ("F-040: `ok` is no bare-name builtin: it is removed (AST:329, D-097), RESOLVE-002", ("as0385b",)),
    ("F-040: a bare-name builtin need not return `Result<T>`: `string_byte_length` returns `int64` (TYPE-007 "
     "binding it to `Result<int64>`)", ("as0403",)),
    ("F-040: the bare `?` fallback is struck (D-175, PARSE-011), and `?|` is the fallback, not struck",
     ("as0413", "as0416")),
    ("F-040: `?!`'s argument is an `Error` constant (D-179), not a `tbb32` (TYPE-007)", ("as0415",)),
    ("F-040: a cast to a `wild` target is `=>!` (D-019's one door): `p => wild int8->` is BORROW-011, even "
     "from a pointer that is no borrow (measured by hand)", ("as0437",)),
    ("F-040: there is no `vec3(…)` constructor: `vec3` is a library type (D-135), RESOLVE-002", ("as0450",)),
)
for _t, _ids in DOC40:
    put("doc", _t, *_ids)
put("known", "DEF-131 (F-015): `<=>` refused by the emitter (EMIT-002); it compiles and runs at 93bcb66", "as0295b")
put("known", "DEF-153 (F-027 c): a string literal in `cstring` position is TYPE-007; it compiles at 93bcb66",
    "as0492")

# ---- session 9: TRAITS_REFERENCE (F-041 a compiler hang, F-042 lower-priority compiler rows,
#      F-043 documentation rows)
put("hang", "F-041: npkc does not terminate on an unbounded generic instantiation (`deep<T>` calling "
    "`deep<Box<T>>`): no exit in 300 s at 4.4 GB, where TRAITS:586 caps the depth at 64 with a compile error",
    "tr0586")
put("comp", "F-042 a: an `opaque struct` is accepted at module level, against TRAITS:368 (as AST's F-039 e)",
    "tr0368")
DOC43 = (
    ("F-043: the Serializable example passes `result` from a body: `result` is the ensures-only keyword since "
     "D-221 (TYPE-060)", ("tr0021",)),
    ("F-043: the Iterator example declares a trait the prelude owns (`Iterator`, RESOLVE-001)", ("tr0097",)),
    ("F-043: `assoc:Error = string;` names the compiler's own `Error` (D-179, D-239; RESOLVE-001)", ("tr0109",)),
    ("F-043: the inherent-impl example casts with `flt64(…)`, a call form the language has no (PARSE-002; casts "
     "are `=>`/`=>!`)", ("tr0124",)),
    ("F-043: `l.push(v)`: the prelude's `List<T>` has no `push` method (TYPE-019)", ("tr0149",)),
    ("F-043: struct fields are not private by default: a plain field is read outside its module (D-313's "
     "`sealed`/`hidden` are the field qualifiers), and `pub` on a field does not parse", ("tr0364",)),
    ("F-043: the storage_driver example is EXTERN-001: the `opaque` tier is reserved (D-190) and its methods take "
     "no `Bridge->`/`Duration`", ("tr0373",)),
    ("F-043: the opaque-copy example names `Handle` (a builtin type keyword) and a `handle_create` that does not "
     "exist; OPAQUE-COPY-001 is never reached", ("tr0384",)),
    ("F-043: `extract_value` passes a lent `T` out (TYPE-047, D-065, D-264); it compiled at the baseline",
     ("tr0404",)),
    ("F-043: `item.render();` as a bare statement discards a `Result` (TYPE-039)", ("tr0419",)),
    ("F-043: the value-parameter example declares `struct:Mutex`, a builtin name (PARSE-001); it compiled at "
     "the baseline", ("tr0435",)),
    ("F-043: the arena example calls `alloc(my_node)`: an arena's `alloc` takes no arguments (TYPE-007)",
     ("tr0602",)),
    ("F-043: \"Lambdas without capture remain as function values\": there is no lambda expression (PARSE-002; "
     "AST:476 says closures are removed and function pointers are named functions)", ("tr0764",)),
)
for _t, _ids in DOC43:
    put("doc", _t, *_ids)
put("extract", "the sentence says a blanket impl does not APPLY to itself (its bound is not met by itself), not "
    "that the declaration is refused; the program expected a refusal", "tr0350")

# ---- session 9: TYPE_REFERENCE 661-1176, part A of 661-2122 (F-044 documentation rows)
DOC44 = (
    ("F-044: §6's table gives `tbb128` and `tbb256` alignment 8; both align to 16 (`{i8, i128}` is 32 bytes, "
     "`{i8, i256}` 48), as TYPE §5's rows 460-461 and its line 469 say (ty0460, ty0461, ty0469 agree)",
     ("ty0673", "ty0674")),
    ("F-044: tbb is \"used for ... the `failsafe` signature\": `failsafe` takes exactly one `Error` "
     "(D-179, TYPE-044)", ("ty0715",)),
    ("F-044: `tryte:t = 42;` and `tryte:t = 1T1T0t;` are not one value: balanced 1T1T0 is 60 "
     "(81 - 27 + 9 - 3), as the compiler computes, and 42 is 1TTT0", ("ty0805",)),
    ("F-044: the struct example is spelled `struct MyStruct = ...` (PARSE-001); a struct is `struct:Name`",
     ("ty0921",)),
    ("F-044: the field-access IR (a `getelementptr` to field 1, then an `i64` load) is not what is emitted: "
     "the struct is loaded whole and the field taken with `extractvalue`", ("ty0936",)),
    ("F-044: a slice \"passes down the call stack and never up\": a slice PARAMETER passed back up is "
     "accepted, and safe: a view of the frame's own local is BORROW-001, and a returned view stored past its "
     "storage is BORROW-002 (measured); the registry's S-107 controls describe the same reading of D-004",
     ("ty1107",)),
    ("F-044: `#wild_slice` \"in `wild` context only\": D-315 retired the phrase (no such rule exists or "
     "can be checked), and TYPE §9.2.1 still states it", ("ty1112",)),
)
for _t, _ids in DOC44:
    put("doc", _t, *_ids)
put("extract", "the regex demanded a word boundary after `}`, which cannot match there; the slice parameter is "
    "`{ ptr, i64 }`, as claimed (measured by hand)", "ty1084")

# ---- known, strict, extraction
put("known", "DEF-133 (F-017 d1, d2): TYPE §3.2's `s.length` and `s[i]`", "ty0366", "ty0366b", "ty0367")
put("known", "DEF-133 (F-017 d5): TYPE §4's D-037 wrapping sentence", "ty0475")
put("known", "DEF-131 (F-015): `<=>` refused by the emitter", "ty0507", "ty0616b")
put("known", "DEF-123 (F-008): a write through a $$i claim's holder is not refused", "vf0215b")
put("strict", "WILDX-002: executing an unsealed page is refused at compile time", "bi0141")
put("strict", "WILDX-001: writing a sealed page is refused at compile time", "bi0154")
put("extract", "the regex required `T @` as the return type; every function returns `{ T, i32 }`, and the "
    "value and parameter types are the claimed ones",
    "ty0017", "ty0174g", "ty0330", "ty0338", "ty0348", "ty0395", "ty0456", "ty0593")
put("extract", "D-143's 15-digit cap on a flt32 literal makes double rounding unobservable; no valid "
    "program tests it", "vf0983", "vf1149")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run = [json.loads(l) for l in open(os.path.join(root, "results", "9126350", "m11.jsonl"))]
    dis = {r["id"] for r in run if r["verdict"] != "AGREE"}
    missing, extra = sorted(dis - set(CLASS)), sorted(set(CLASS) - dis)
    for i in missing:
        print("no class:", i)
    for i in extra:
        print("class but no disagreement:", i)
    import collections
    c = collections.Counter(v[0] for k, v in CLASS.items() if k in dis)
    print("%d disagreements, %d classed: %s" % (len(dis), len(dis) - len(missing),
                                                ", ".join("%s %d" % kv for kv in c.most_common())))
    return 1 if missing or extra else 0


if __name__ == "__main__":
    raise SystemExit(main())
