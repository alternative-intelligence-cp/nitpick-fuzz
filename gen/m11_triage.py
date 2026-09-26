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
