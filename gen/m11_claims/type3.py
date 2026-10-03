"""M11 claims: TYPE_REFERENCE.md lines 1177-1592 at HUNT2 (sections 10 to 18).

Pointers, Optional and Result, Handle and arena, atomics, SIMD, the library vector
types, function types, Future and `dyn`. Part B of TYPE 661-2122 (S65). Every
expectation below is written from the reference's TEXT, before any program ran.
"""
import re

from m11lib import *
from m11_tyhelp import *

covers("TYPE", 1177, 1592)

D = "TYPE"

ERRS = "error:E1;\nerror:E2;"
# a fallible int32 function: fails E2 for 1, else passes 5
K = ERRS + "\nfunc:m11k = int32(int32:x) {\n    if (x == 1i32) { fail E2; }\n    pass 5i32;\n};"
R = "func:m11r = int32(int32:x) never fails { pass x; };"
G = "func:m11g = NIL() never fails { pass NIL; };"

# ================================================================== 10. pointers
claim("ty1181", D, 1181, "| `T->` | `ptr` | Pointer to T |", "row",
      "`T->` is an opaque `ptr`: an `int32->` parameter is `ptr`.",
      expect=ir_all(param("m11p", "ptr")),
      src=prog_("""    int32:x = raw v32(5i32);
    if (raw m11p(@x) != 5i32) { exit 10i32; }
    exit 0i32;""", "func:m11p = int32(int32->:p) never fails { pass <-p; };"),
      wrong="another carrier")
claim("ty1182", D, 1182, "| `any->` | `ptr` | Type-erased pointer |", "row",
      "`any->` is an opaque `ptr`: an `any->` parameter is `ptr`.",
      expect=ir_all(param("m11a", "ptr")),
      src=prog_("    exit 0i32;", "func:m11a = int64(any->:_~p) never fails { pass 0i64; };"),
      wrong="refused, or another carrier")
claim("ty1184", D, 1184, "The C-style `*` pointer syntax (e.g. `void*`, `char*`) is **forbidden everywhere**", "rule",
      "The C-style `*` pointer syntax is refused: `int32*:p = @x;`.", expect="refuse",
      src=prog_("""    int32:x = raw v32(5i32);
    int32*:p = @x;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1185", D, 1185, "`@var` = address of", "rule",
      "`@var` takes an address, `<-ptr` dereferences (read and write), and `ptr.field` reaches a field "
      "through a pointer.",
      expect="run:0",
      src=prog_("""    int32:x = raw v32(5i32);
    int32->:p = @x;
    <-p = 7i32;
    if (x != 7i32) { exit 10i32; }
    int32:y = <-p;
    if (y != 7i32) { exit 11i32; }
    S:s = S{ f: 1i32 };
    S->:q = @s;
    q.f = 2i32;
    if (s.f != 2i32) { exit 12i32; }
    exit 0i32;""", "struct:S = { int32:f; };"),
      wrong="refused, or 10-12")
claim("ty1189", D, 1189, "All pointers are **thin** — a single machine word", "rule",
      "A pointer is one machine word: `int32->` is 8 bytes with alignment 8.",
      expect="run:0", src=layout(["int32->"], 8, 8), wrong=layout_wrong("int32->", 8, 8))
claim("ty1190", D, 1190, "The distinction between wild and", "rule",
      "Wild and borrow pointers lower alike: a `wild int64->` parameter and an `int64->` one are both `ptr`.",
      expect=ir_all(param("m11w", "ptr"), param("m11b", "ptr")),
      src=prog_("""    int64:x = raw v64(5i64);
    if (raw m11b(@x) != 5i64) { exit 10i32; }
    exit 0i32;""", """func:m11w = int64(wild int64->:p) never fails { pass <-p; };
func:m11b = int64(int64->:p) never fails { pass <-p; };"""),
      wrong="another carrier for one of them")
claim("ty1194", D, 1194, "claims `int8->` is a *fat* pointer carrying bounds", "rule",
      "`int8->` is not fat (the draft's claim is struck): an `int8->` parameter is one `ptr`.",
      expect=ir_all(param("m11i", "ptr")),
      src=prog_("""    int8:b = raw v8(3i8);
    if (raw m11i(@b) != 3i8) { exit 10i32; }
    exit 0i32;""", "func:m11i = int8(int8->:p) never fails { pass <-p; };"),
      wrong="a struct of pointer and bounds")
claim("ty1200", D, 1200, "`--guard-pages` remains available", "rule",
      "`--guard-pages` is available: npkc accepts it on an ordinary program.",
      expect="sh:0",
      sh="""cat > p.npk <<'NPK_EOF'
%s
NPK_EOF
"$NPKC" p.npk -o p.ll --guard-pages > out.txt 2>&1; rc=$?
echo "npkc --guard-pages: $rc"; head -3 out.txt
[ $rc -eq 0 ] && [ -s p.ll ]
""" % prog(main_("    exit 0i32;")).strip(),
      wrong="npkc refuses the flag")
claim("ty1203", D, 1203, "**Indexing a pointer** (`p[i]`) is the i-th `T` in memory from `p`", "rule",
      "Indexing a pointer to a scalar is the i-th element from it: `p[2]` from `@arr[0]` is arr[2].",
      expect="run:0",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32->:p = @arr[0i64];
    if (p[raw v64(2i64)] != 3i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1205", D, 1205, "where the pointee is itself indexed** (1.5.8b step 1b, `NITPICK-TYPE-082`)", "rule",
      "Indexing a pointer to an array is TYPE-082.", expect="refuse:NITPICK-TYPE-082",
      src=prog_("""    int64[8]:arr = [1i64, 2i64, 3i64, 4i64, 5i64, 6i64, 7i64, 8i64];
    int64[8]->:p = @arr;
    int64:v = p[raw v64(1i64)];
    if (v != 2i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: a wild stride over whole arrays")
claim("ty1206", D, 1206, "That covers an array (`int64[8]->`), a slice (`T[]->`) and a `List<T>->`", "rule",
      "Indexing a pointer to a slice is TYPE-082.", expect="refuse:NITPICK-TYPE-082",
      src=prog_("""    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    int32[]:v = arr[0i64...4i64];
    int32[]->:q = @v;
    int32:e = q[raw v64(1i64)];
    if (e != 2i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1206b", D, 1206, "That covers an array (`int64[8]->`), a slice (`T[]->`) and a `List<T>->`", "rule",
      "Indexing a pointer to a List is TYPE-082.", expect="refuse:NITPICK-TYPE-082",
      src=prog_("""    List<int64>:l = raw list_init::<int64>(4i64);
    drop list_push(@l, raw v64(1i64));
    List<int64>->:q = @l;
    int64:e = q[raw v64(0i64)];
    if (e != 1i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1210", D, 1210, "Here the element is spelled `(<-p)[i]`", "rule",
      "The pointee's element is spelled `(<-p)[i]`.",
      expect="run:0",
      src=prog_("""    int64[8]:arr = [1i64, 2i64, 3i64, 4i64, 5i64, 6i64, 7i64, 8i64];
    int64[8]->:p = @arr;
    int64:v = (<-p)[raw v64(1i64)];
    if (v != 2i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1211", D, 1211, "pointer to a scalar or a struct keeps its indexing", "rule",
      "A pointer to a struct keeps its indexing: `q[1].f` from `@sa[0]` is sa[1].f.",
      expect="run:0",
      src=prog_("""    S[2]:sa = [S{ f: 1i32 }, S{ f: 2i32 }];
    S->:q = @sa[0i64];
    if (q[raw v64(1i64)].f != 2i32) { exit 10i32; }
    exit 0i32;""", "struct:S = { int32:f; };"),
      wrong="refused (TYPE-082), or 10")

# ================================================================== 11.1 Optional
claim("ty1219", D, 1219, "```llvm", "example",
      "`int32?` is 8 bytes with alignment 4 (an i8 tag padded before an i32).",
      expect="run:0", src=layout(["int32?"], 8, 4), wrong=layout_wrong("int32?", 8, 4))
claim("ty1222", D, 1222, "%Optional_i32 = type { i8, i32 }", "rule",
      "`int32?` is `{ i8, i32 }`: an `int32?` parameter has that type.",
      expect=ir_all(param("m11o", r"\{ ?i8, i32 ?\}")),
      src=prog_("""    int32?:a = raw v32(5i32);
    if (raw m11o(a) != 5i32) { exit 10i32; }
    exit 0i32;""", "func:m11o = int32(int32?:o) never fails { pass (o ?? 0i32); };"),
      wrong="another layout")
claim("ty1228", D, 1228, "the value half is ZEROED, never undef", "rule",
      "An empty Optional is `zeroinitializer`, never `undef`: a function passing `NIL` as an `int32?` emits "
      "`zeroinitializer` and no `undef`.",
      expect=ir_fn_lacks("m11n", [r"zeroinitializer"], r"\bundef\b"),
      src=prog_("""    int32?:e = raw m11n();
    if (e != NIL) { exit 10i32; }
    exit 0i32;""", "func:m11n = int32?() never fails { int32?:a = NIL; pass a; };"),
      wrong="an undef value half")
claim("ty1229", D, 1229, "; int32?:b = 42i32;  = { i8 1, i32 42 }", "rule",
      "`int32?:b = 42i32;` holds 42.",
      expect="run:0",
      src=prog_("""    int32?:b = raw v32(42i32);
    if (b == NIL) { exit 10i32; }
    if ((b ?? 0i32) != 42i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10/11")
claim("ty1237", D, 1237, "`== NIL`/`!= NIL` is a tag", "rule",
      "`== NIL` and `!= NIL` test the tag in either operand order.",
      expect="run:0",
      src=prog_("""    int32?:a = NIL;
    int32?:b = raw v32(3i32);
    if (!(NIL == a)) { exit 10i32; }
    if (NIL == b) { exit 11i32; }
    if (!(b != NIL)) { exit 12i32; }
    if (!(NIL != b)) { exit 13i32; }
    exit 0i32;"""),
      wrong="refused (NIL on the left), or 10-13")
claim("ty1238", D, 1238, "`??` evaluates its default only on the empty", "rule",
      "`??` evaluates its default only when the Optional is empty.", m10="x06_optional_default_lazy")
claim("ty1239", D, 1239, "`?.` yields `zeroinitializer` of the result type when empty", "rule",
      "`?.` on an empty Optional yields an empty result.", m10="d15_safe_navigation_on_empty")
claim("ty1240", D, 1240, "the field when present", "rule",
      "`?.` wraps the field when present: `s?.f` over a holding `S?` is the field, wrapped.",
      expect="run:0",
      src=prog_("""    S?:s = S{ f: raw v32(5i32) };
    int32?:r = s?.f;
    if ((r ?? 0i32) != 5i32) { exit 10i32; }
    exit 0i32;""", "struct:S = { int32:f; };"),
      wrong="refused, or 10")
claim("ty1245", D, 1245, "**There is no constructor, and none is needed (D-099).**", "rule",
      "An Optional is built by writing the value and emptied by writing NIL.",
      expect="run:0",
      src=prog_("""    int32?:a = raw v32(5i32);
    a = NIL;
    if (a != NIL) { exit 10i32; }
    a = raw v32(6i32);
    if ((a ?? 0i32) != 6i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1252", D, 1252, "| `int32?:a = NIL;` | empty |", "row",
      "`NIL` is the empty Optional and a value the holding one.", m10="d09_optional_nil_and_value")
claim("ty1253", D, 1253, "| `int32?:b = 42i32;` | holding `42i32` |", "row",
      "`int32?:b = 42i32;` holds 42i32.",
      expect="run:0",
      src=prog_("""    int32?:b = 42i32;
    if ((b ?? raw v32(0i32)) != 42i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="10")
claim("ty1254", D, 1254, "| `a == NIL`, `a != NIL` | the test |", "row",
      "`a == NIL` and `a != NIL` test an Optional.",
      expect="run:0",
      src=prog_("""    int32?:a = NIL;
    int32?:b = raw v32(1i32);
%s
%s
    exit 0i32;""" % (chk("a == NIL", 10), chk("b != NIL", 11))),
      wrong="10/11")
claim("ty1255", D, 1255, "| `a ?? d` | the value, or `d` |", "row",
      "`a ?? d` is the value, or d when empty.",
      expect="run:0",
      src=prog_("""    int32?:a = NIL;
    int32?:b = raw v32(4i32);
    if ((a ?? 7i32) != 7i32) { exit 10i32; }
    if ((b ?? 7i32) != 4i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10/11")
claim("ty1256", D, 1256, "| `a?.f` | the field, still wrapped |", "row",
      "`a?.f` is the field, still wrapped: it binds to an `int32?`.",
      expect="run:0",
      src=prog_("""    S?:s = S{ f: raw v32(5i32) };
    int32?:r = s?.f;
    if (r == NIL) { exit 10i32; }
    exit 0i32;""", "struct:S = { int32:f; };"),
      wrong="refused, or 10")
claim("ty1256b", D, 1256, "| `a?.f` | the field, still wrapped |", "row",
      "`a?.f` is still wrapped: binding it to a plain `int32` is refused.", expect="refuse",
      src=prog_("""    S?:s = S{ f: raw v32(5i32) };
    int32:r = s?.f;
    if (r != 5i32) { exit 10i32; }
    exit 0i32;""", "struct:S = { int32:f; };"),
      wrong="accepted: the wrapper dropped silently")
claim("ty1257", D, 1257, "| `pick (a ?? d) { … }` |", "row",
      "`pick (a ?? d)` selects over the value or the default.",
      expect="run:0",
      src=prog_("""    int32?:a = raw v32(2i32);
    int32:r = 0i32;
    pick (a ?? 0i32) { (2i32) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1259", D, 1259, "**No `pick` selects on an `Optional` (D-260, 1.5.2c; `NITPICK-TYPE-065`).**", "rule",
      "A pick on an Optional is TYPE-065 (statement form).", expect="refuse:NITPICK-TYPE-065",
      src=prog_("""    int32?:o = raw v32(5i32);
    int32:r = 0i32;
    pick (o) { (5i32) { r = 1i32; }, (*) { r = 2i32; } }
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1262", D, 1262, "refused by name at the selector, in the statement form and in the expression", "rule",
      "A pick on an Optional is TYPE-065 in the expression form too.", expect="refuse:NITPICK-TYPE-065",
      src=prog_("""    int32?:o = raw v32(5i32);
    int32:r = pick (o) { (5i32) { give 1i32; }, (*) { give 2i32; } };
    if (r != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1268", D, 1268, "`T?` and `Optional<T>` are **one type with two spellings**", "rule",
      "`T?` and `Optional<T>` are one type: an `Optional<int32>` binds to an `int32?`.",
      expect="run:0",
      src=prog_("""    Optional<int32>:a = raw v32(5i32);
    int32?:b = a;
    if ((b ?? 0i32) != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (two types), or 10")
claim("ty1272", D, 1272, "The wrap from `T` to `Optional<T>` is the **one implicit conversion in the", "rule",
      "The wrap from T applies at a declaration's initialiser, a call argument and `pass`.",
      expect="run:0",
      src=prog_("""    int32?:a = raw v32(1i32);
    if ((a ?? 0i32) != 1i32) { exit 10i32; }
    if (raw m11w(raw v32(2i32)) != 2i32) { exit 11i32; }
    int32?:c = raw m11p();
    if ((c ?? 0i32) != 3i32) { exit 12i32; }
    exit 0i32;""", """func:m11w = int32(int32?:o) never fails { pass (o ?? 0i32); };
func:m11p = int32?() never fails { pass 3i32; };"""),
      wrong="refused at one slot, or 10-12")
claim("ty1275", D, 1275, "no implicit widening (D-092)", "rule",
      "Nothing else is coerced: an int32 into an int64 binding is refused.", expect="refuse",
      src=prog_("""    int64:y = raw v32(5i32);
    if (y != 5i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: an implicit widening")
claim("ty1276", D, 1276, "A `NIL`-**typed value**, which is what `drop f()` yields, is", "rule",
      "A NIL-typed value is not wrapped: `int32?:x = drop f();` is refused.", expect="refuse",
      src=prog_("""    int32?:x = drop m11g();
    if (x != NIL) { exit 10i32; }
    exit 0i32;""", G),
      wrong="accepted: a discarded outcome used as a value")
claim("ty1280", D, 1280, "**`Some(42)` was struck (D-099).**", "rule",
      "`Some(42)` does not exist: `int32?:a = Some(42i32);` is refused.", expect="refuse",
      src=prog_("""    int32?:a = Some(42i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ty1282", D, 1282, "A replacement literal form `Optional{…}` was then drafted and", "rule",
      "`Optional{…}` was struck too: `int32?:a = Optional{ value: 5i32 };` is refused.", expect="refuse",
      src=prog_("""    int32?:a = Optional{ value: 5i32 };
    exit 0i32;"""),
      wrong="accepted")
claim("ty1287", D, 1287, "**An `Optional` has no readable members.**", "rule",
      "`.has_value` is not a member: reading it is refused.", expect="refuse",
      src=prog_("""    int32?:a = raw v32(5i32);
    if (a.has_value) { exit 0i32; }
    exit 10i32;"""),
      wrong="accepted")
claim("ty1288", D, 1288, "names, not source-level members", "rule",
      "`.value` is not a member: reading it is refused.", expect="refuse",
      src=prog_("""    int32?:a = raw v32(5i32);
    int32:v = a.value;
    if (v != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: the unchecked read")
claim("ty1294", D, 1294, "**`NIL?`** — `NIL?:x = NIL;` is ambiguous", "rule",
      "`NIL?` is refused.", expect="refuse",
      src=prog_("""    NIL?:x = NIL;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1296", D, 1296, "**`Optional<Optional<T>>`**", "rule",
      "`Optional<Optional<T>>` is refused.", expect="refuse",
      src=prog_("""    Optional<Optional<int32>>:x = NIL;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1298", D, 1298, "`int32??` reads as `int32` followed by the null-coalesce operator", "rule",
      "`int32??` is not a type: it lexes as `int32` and `??`, and is refused.", expect="refuse",
      src=prog_("""    int32??:x = NIL;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1299", D, 1299, "flattens** rather than manufacturing the type behind the rule's back", "rule",
      "`?.` flattens: over an Optional field it yields that field as it is (`int32?`), empty or holding.",
      expect="run:0",
      src=prog_("""    T?:t = T{ f: raw v32(5i32) };
    int32?:r = t?.f;
    if ((r ?? 0i32) != 5i32) { exit 10i32; }
    T?:u = T{ f: NIL };
    int32?:q = u?.f;
    if (q != NIL) { exit 11i32; }
    exit 0i32;""", "struct:T = { int32?:f; };"),
      wrong="refused (a nested Optional), or 10/11")

# ================================================================== 11.2 Result
claim("ty1303", D, 1303, "**EVERY function in Nitpick returns `Result<T>`** except `pub func:main` and", "rule",
      "Every function returns a Result, a `never fails` one included: binding its bare call to an int32 is refused.",
      expect="refuse",
      src=prog_("""    int32:x = m11r(raw v32(5i32));
    if (x != 5i32) { exit 10i32; }
    exit 0i32;""", R),
      wrong="accepted: a call that is not a Result")
claim("ty1309", D, 1309, "```nitpick", "example",
      "A Result's canonical fields are `value` and `err`: an error reads `r.err == E2`, a success `r.value`.",
      expect="run:0",
      src=prog_("""    Result<int32>:r = m11k(raw v32(1i32));
    if (!(r.is_error)) { exit 10i32; }
    if (r.err != E2) { exit 11i32; }
    Result<int32>:s = m11k(raw v32(0i32));
    if (s.is_error) { exit 12i32; }
    int32:v = s.value;
    if (v != 5i32) { exit 13i32; }
    exit 0i32;""", K),
      wrong="refused (other field names), or 10-13")
claim("ty1317", D, 1317, "```llvm", "example",
      "`Result<int32>` is 8 bytes with alignment 4.",
      expect="run:0", src=layout(["Result<int32>"], 8, 4), wrong=layout_wrong("Result<int32>", 8, 4))
claim("ty1320", D, 1320, "%Result_i32 = type { i32, i32 }", "rule",
      "`Result<int32>` is `{ i32, i32 }`: an int32 function returns that type.",
      expect=r'ir:(?m)^define \{ i32, i32 \} @"?(?:[\w$]+\.)*m11r"?\(',
      src=prog_("""    if (raw m11r(raw v32(5i32)) != 5i32) { exit 10i32; }
    exit 0i32;""", R),
      wrong="another return type")
claim("ty1330", D, 1330, "| `pass(retVal);` | `return Result{value: retVal};`", "row",
      "`pass(retVal);` returns a success holding retVal.",
      expect="run:0",
      src=prog_("""    int32:v = m11p() ?| 0i32;
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", "func:m11p = int32() {\n    pass(raw v32(5i32));\n};"),
      wrong="refused (the parenthesised form), or 10")
claim("ty1331", D, 1331, "| `fail(errCode);` | `return Result{err: errCode, value: zero};`", "row",
      "`fail(errCode);` returns an error holding errCode.",
      expect="run:0",
      src=prog_("""    Result<int32>:r = m11f();
    if (!(r.is_error)) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    exit 0i32;""", ERRS + "\nfunc:m11f = int32() {\n    fail(E1);\n};"),
      wrong="refused (the parenthesised form), or 10/11")
claim("ty1332", D, 1332, "| `return Result{err: errCode, value: retVal};` | (literal, no desugar) |", "row",
      "`return Result{err: e, value: v};` returns both.", m10="r10_result_literal_both")
claim("ty1337", D, 1337, "`0i32` is not assignable to a `tbb32`, there being no implicit conversion", "rule",
      "There is no implicit conversion from int32 to tbb32: `tbb32:t = 0i32;` is refused.", expect="refuse",
      src=prog_("""    tbb32:t = 0i32;
    if (is_err(t)) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ty1340", D, 1340, "**Either field may be omitted**", "rule",
      "A Result literal's omitted `err` is success.", m10="d07_result_literal_omits_err")
claim("ty1340b", D, 1340, "**Either field may be omitted**", "rule",
      "A Result literal with only `err` is that error.", m10="d08_result_literal_omits_value")
claim("ty1343", D, 1343, "order is free**", "rule",
      "Field order is free: `Result{value: v, err: e}` and `Result{err: e, value: v}` are the same.",
      expect="run:0",
      src=prog_("""    Result<int32>:a = m11a();
    Result<int32>:b = m11b();
    if (!(a.is_error)) { exit 10i32; }
    if (!(b.is_error)) { exit 13i32; }
    if (a.err != E1) { exit 11i32; }
    if (b.err != E1) { exit 12i32; }
    exit 0i32;""", ERRS + """
func:m11a = int32() { return Result{ value: 3i32, err: E1 }; };
func:m11b = int32() { return Result{ err: E1, value: 3i32 }; };"""),
      wrong="refused (one order), or 10-12")
claim("ty1346", D, 1346, "**There is no `is_error` field to write** (D-069)", "rule",
      "There is no `is_error` field to write: a literal naming it is refused.", expect="refuse",
      src=prog_("""    Result<int32>:r = m11a();
    if (r.is_error) { exit 0i32; }
    exit 10i32;""", ERRS + "\nfunc:m11a = int32() { return Result{ value: 3i32, is_error: true }; };"),
      wrong="accepted")
claim("ty1356", D, 1356, "existing `pick(r.is_error)` code is unaffected", "rule",
      "`r.is_error` is a derived accessor: `pick (r.is_error)` selects on it.",
      expect="run:0",
      src=prog_("""    Result<int32>:r = m11k(raw v32(1i32));
    int32:t = 0i32;
    pick (r.is_error) { (true) { t = 1i32; }, (false) { t = 2i32; } }
    if (t != 1i32) { exit 10i32; }
    exit 0i32;""", K),
      wrong="refused, or 10")
claim("ty1360", D, 1360, "The error field's value space is total", "rule",
      "0 is success, positive codes user errors, negative codes system errors, and INT32_MIN unconstructible.",
      untestable="[internal] the codes are an encoding (D-179: the domain is typed, and the sign an encoding detail)")
claim("ty1362", D, 1362, "Building a `Result` whose code is ERR, or", "rule",
      "Building a Result whose code is ERR, or 0 on a failure path, traps where it is built.",
      untestable="[unobservable] since D-179 typed the error domain, no program can spell a zero or ERR code")
claim("ty1369", D, 1369, "The compiler WILL NOT allow accessing `.value` without first checking `.is_error`", "rule",
      "Reading `.value` without checking is refused.", m10="r07_value_without_check_refused")
claim("ty1374", D, 1374, "| Safe unwrap | `expr ? defaultVal` |", "row",
      "Safe unwrap `expr ? defaultVal` gives the default on an error.",
      expect="run:0",
      src=prog_("""    int32:v = m11k(raw v32(1i32)) ? 7i32;
    if (v != 7i32) { exit 10i32; }
    int32:w = m11k(raw v32(0i32)) ? 7i32;
    if (w != 5i32) { exit 11i32; }
    exit 0i32;""", K),
      wrong="refused (no `?` operator), or 10/11")
claim("ty1375", D, 1375, "**On an `Optional`, not a `Result`**", "row",
      "`??` is on an Optional, not a Result: `m11k(…) ?? 7` is refused.", expect="refuse",
      src=prog_("""    int32:v = m11k(raw v32(1i32)) ?? 7i32;
    if (v != 7i32) { exit 10i32; }
    exit 0i32;""", K),
      wrong="accepted")
claim("ty1376", D, 1376, "| Emphatic unwrap | `expr ?! errCode` |", "row",
      "Emphatic unwrap `expr ?! errCode` triggers failsafe with errCode on an error (E1 exits 81, where the "
      "callee's own E2 would exit 82).",
      expect="run:81",
      src=prog_("""    int32:v = m11k(raw v32(1i32)) ?! E1;
    if (v == 5i32) { exit 10i32; }
    exit 11i32;""", K),
      wrong="no trap (10/11), or the callee's error (82)")
claim("ty1377", D, 1377, "| Raw unwrap | `raw(expr)` or `raw expr` |", "row",
      "`raw(expr)` and `raw expr` extract a never-fails call's value.",
      expect="run:0",
      src=prog_("""    int32:a = raw(m11r(raw v32(5i32)));
    int32:b = raw m11r(raw v32(6i32));
    if (a != 5i32) { exit 10i32; }
    if (b != 6i32) { exit 11i32; }
    exit 0i32;""", R),
      wrong="refused (the parenthesised form), or 10/11")
claim("ty1377b", D, 1377, "| `_!` |", "row",
      "`_!` is raw unwrap's shorthand.",
      expect="run:0",
      src=prog_("""    int32:a = _! m11r(raw v32(5i32));
    if (a != 5i32) { exit 10i32; }
    exit 0i32;""", R),
      wrong="refused: no such shorthand")
claim("ty1378", D, 1378, "| Drop | `drop(expr)` or `drop expr` |", "row",
      "`drop(expr)` and `drop expr` run a NIL never-fails call.",
      expect="run:0",
      src=prog_("""    drop(m11g());
    drop m11g();
    exit 0i32;""", G),
      wrong="refused (the parenthesised form)")
claim("ty1378b", D, 1378, "| `_?` |", "row",
      "`_?` is drop's shorthand.",
      expect="run:0",
      src=prog_("""    _? m11g();
    exit 0i32;""", G),
      wrong="refused: no such shorthand")
claim("ty1379", D, 1379, "| Discard | `discard(param)` | `_~` |", "row",
      "`discard(x)` marks a value unused, and a `_~` name marks a parameter unused.",
      expect="run:0",
      src=prog_("""    int32:x = raw v32(5i32);
    discard(x);
    if (raw m11u(raw v32(1i32)) != 1i32) { exit 10i32; }
    exit 0i32;""", "func:m11u = int32(int32:_~u) never fails { pass 1i32; };"),
      wrong="refused, or 10")
claim("ty1382", D, 1382, "licensed only", "rule",
      "`raw` on a may-fail call is refused, TYPE-042.", m10="r08_raw_on_fallible_refused")
claim("ty1385", D, 1385, "`drop` = the \"void call\": run a `never fails` function whose success type is", "rule",
      "`drop` of a may-fail call is refused.", m10="r05_drop_of_fallible_refused")
claim("ty1387", D, 1387, "`?!`-trapped, or `? NIL`-swallowed", "rule",
      "A may-fail NIL call is swallowed with `? NIL`.",
      expect="run:0",
      src=prog_("""    m11h() ? NIL;
    exit 0i32;""", ERRS + "\nfunc:m11h = NIL() {\n    fail E1;\n};"),
      wrong="refused, or a trap")
claim("ty1387b", D, 1387, "a never-failing VALUE is `discard(raw f())`", "rule",
      "A never-failing value is discarded with `discard(raw f())`.",
      expect="run:0",
      src=prog_("""    discard(raw m11r(raw v32(1i32)));
    exit 0i32;""", R),
      wrong="refused")
claim("ty1388", D, 1388, "takes a VALUE", "rule",
      "`discard` of a Result is refused.", m10="r09_discard_of_result_refused")
claim("ty1392", D, 1392, "(`TYPE-039`), the `defer` rule (`TYPE-040`)", "rule",
      "The statement closed list: a bare call statement that discards a Result is TYPE-039.",
      expect="refuse:NITPICK-TYPE-039",
      src=prog_("""    m11k(raw v32(0i32));
    exit 0i32;""", K),
      wrong="accepted: a silent discard")
claim("ty1396", D, 1396, "```nitpick", "example",
      "The storage_driver extern example compiles.", expect="compile",
      src=prog_("    exit 0i32;", """extern:"storage_driver" = {
    opaque struct:DbHandle;
    func:open = DbHandle(int8[]:path);
};"""),
      wrong="refused")
claim("ty1419", D, 1419, "The contract grammar remains parsed and is", "rule",
      "An `extern` method's contract (`fails on result < 0i32 with errno`) is parsed and refused, naming D-149.",
      expect="sh:0",
      sh=SH_LIB + 'cp "$LIB/nbridge.npk" "$LIB/nsys.npk" . || exit 5\n' +
      "cat > r.npk <<'NPK_EOF'\n" + 'mod:r;\nuse "./nbridge.npk".*;\n\nextern:"drv" = {\n' +
      "    func:probe = int64(Bridge->:b, Duration:within) fails on result < 0i32 with errno;\n};\n\n" +
      main_("    exit 0i32;") + "\n" + failsafe_text("") + "NPK_EOF\nrefused r.npk 'D-149'\n",
      wrong="accepted, or refused without naming D-149 (a parse error)")

# ================================================================== 12. Handle, arena
claim("ty1428", D, 1428, "```llvm", "example",
      "`Handle<T>` is { i64, i32 }: 16 bytes, alignment 8.",
      expect="run:0", src=layout(["Handle<int64>"], 16, 8), wrong=layout_wrong("Handle<int64>", 16, 8))
claim("ty1439", D, 1439, "```llvm", "example",
      "An arena is allocated with `alloc(N)` and a cast: `alloc(N) => arena<T>->` compiles.",
      expect="compile",
      src=prog_("""    arena<int64>->:a = alloc(64i64) => arena<int64>->;
    discard(a);
    exit 0i32;"""),
      wrong="refused (another way to make an arena)")

# ================================================================== 13. atomics
ATOM = """    atomic<int32>:c = 0i32;
    int32:p = c.fetch_add(raw v32(5i32));
    int32:q = c.fetch_sub(raw v32(2i32));
    int32:s = c.swap(raw v32(9i32));
    c.store(raw v32(4i32));
    discard(c.compare_exchange(raw v32(4i32), raw v32(6i32)));
    if (p != 0i32) { exit 10i32; }
    if (q != 5i32) { exit 11i32; }
    if (s != 3i32) { exit 12i32; }
    if (c.load() != 6i32) { exit 13i32; }
    exit 0i32;"""
P = r"[^,\n]+"
for ln, op, pat in ((1453, "a.load()", r"load atomic i32, ptr %s seq_cst" % P),
                    (1454, "a.store(v)", r"store atomic i32 %s, ptr %s seq_cst" % (P, P)),
                    (1455, "a.swap(v)", r"atomicrmw xchg ptr %s, i32 %s seq_cst" % (P, P)),
                    (1456, "a.fetch_add(v)", r"atomicrmw add ptr %s, i32 %s seq_cst" % (P, P)),
                    (1457, "a.fetch_sub(v)", r"atomicrmw sub ptr %s, i32 %s seq_cst" % (P, P)),
                    (1458, "a.compare_exchange(exp, des)",
                     r"cmpxchg ptr %s, i32 %s, i32 %s seq_cst seq_cst" % (P, P, P))):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % op, "row",
          "`%s` on an `atomic<int32>` is native, sequentially consistent IR: `%s`." % (op, pat.replace(P, "…")),
          expect=ir_fn("main", pat), src=prog_(ATOM),
          wrong="a call, or another ordering")

# ================================================================== 14. SIMD
for ln, t, ir, size in ((1466, "simd<flt32, 4>", "<4 x float>", 16), (1467, "simd<flt64, 2>", "<2 x double>", 16),
                        (1468, "simd<int32, 8>", "<8 x i32>", 32)):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t, "row",
          "`%s` is %d bytes with alignment %d." % (t, size, size),
          expect="run:0", src=layout([t], size, size), wrong=layout_wrong(t, size, size))
    claim("ty%04db" % ln, D, ln, "| `%s` | `%s` |" % (t, ir), "row",
          "A `%s` parameter is `%s`." % (t, ir),
          expect=ir_all(param("m11v", re.escape(ir))),
          src=prog_("    exit 0i32;", "func:m11v = %s(%s:x) never fails { pass x; };" % (t, t)),
          wrong="another carrier")
claim("ty1472", D, 1472, "2..64, total ≤ 64 bytes", "rule",
      "A simd of one lane is refused.", expect="refuse",
      src=prog_("""    simd<int32, 1>:v = simd(raw v32(1i32));
    exit 0i32;"""),
      wrong="accepted")
claim("ty1472b", D, 1472, "2..64, total ≤ 64 bytes", "rule",
      "A simd over 64 bytes is refused: `simd<int64, 16>` is 128.", expect="refuse",
      src=prog_("""    simd<int64, 16>:v = simd(raw v64(1i64));
    exit 0i32;"""),
      wrong="accepted")
claim("ty1472c", D, 1472, "alignment = next power of two ≥ size, capped 64", "rule",
      "A simd's alignment is the next power of two at or above its size: `simd<int16, 3>` (6 bytes) aligns "
      "to 8, so `{int8, it}` is 16 bytes.",
      expect="run:0",
      src=prog_("""    if (#size_of<P0>() != 16i64) { exit 10i32; }
    exit 0i32;""", "struct:S0 = { simd<int16, 3>:v; };\nstruct:P0 = { int8:a; S0:v; };"),
      wrong="10: another alignment")
claim("ty1473", D, 1473, "`simd(…)` constructs annotation-directed", "rule",
      "`simd(…)` takes N components, or one that splats.",
      expect="run:0",
      src=prog_("""    simd<int32, 4>:v = simd(raw v32(1i32), 2i32, 3i32, 4i32);
    simd<int32, 4>:s = simd(raw v32(7i32));
    if (v[2i64] != 3i32) { exit 10i32; }
    if (s[3i64] != 7i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1474", D, 1474, "Operations are elementwise on identical types", "rule",
      "Operations are elementwise: `+ - * / %` on lanes, and `& | ^ << >>` on integer lanes.",
      expect="run:0",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(12i32), 7i32, 6i32, 5i32);
    simd<int32, 4>:b = simd(raw v32(5i32), 2i32, 3i32, 1i32);
    simd<int32, 4>:one = simd(raw v32(1i32));
    simd<int32, 4>:r = ((a + b) - (a * b)) + ((a / b) + (a %% b));
    if (r[0i64] != -39i32) { exit 10i32; }
    simd<int32, 4>:x = (a & b) | ((a ^ b) << one);
    if (x[0i64] != 22i32) { exit 11i32; }
    simd<int32, 4>:y = a >> one;
    if (y[1i64] != 3i32) { exit 12i32; }
    exit 0i32;""".replace("%%", "%")),
      wrong="refused, or 10-12: a wrong lane")
claim("ty1475", D, 1475, "comparisons yield `simd<bool, N>`", "rule",
      "A lane comparison yields `simd<bool, N>`.",
      expect="run:0",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(1i32), 5i32, 3i32, 9i32);
    simd<int32, 4>:b = simd(raw v32(4i32));
    simd<bool, 4>:c = a < b;
    if (!(c[0i64])) { exit 10i32; }
    if (c[1i64]) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("ty1476", D, 1476, "`v[i]` is a bounds-checked lane place", "rule",
      "A lane index past the lanes traps OutOfBounds.", expect="trap:OutOfBounds",
      src=prog_("""    simd<int32, 4>:v = simd(raw v32(1i32));
    if (v[raw v64(4i64)] == 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="a lane read past the vector (10, 11)")
claim("ty1476b", D, 1476, "`.len` is the lane count", "rule",
      "`.len` is the lane count.",
      expect="run:0",
      src=prog_("""    simd<int32, 8>:v = simd(raw v32(1i32));
    if (v.len != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1477", D, 1477, "vector division carries D-007 as ANY-LANE checks", "rule",
      "Integer vector division by a vector with one zero lane traps DivByZero.", expect="trap:DivByZero",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(8i32));
    simd<int32, 4>:b = simd(raw v32(2i32), 2i32, 0i32, 2i32);
    simd<int32, 4>:q = a / b;
    if (q[0i64] == 4i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap (10, 11)")
claim("ty1478", D, 1478, "INT_MIN/−1 → DivOverflow", "rule",
      "Integer vector division with one lane INT_MIN / -1 traps DivOverflow.", expect="trap:DivOverflow",
      src=prog_("""    int32:m = raw v32(-2147483647i32) - 1i32;
    simd<int32, 4>:a = simd(raw v32(8i32), m, 8i32, 8i32);
    simd<int32, 4>:b = simd(raw v32(2i32), -1i32, 2i32, 2i32);
    simd<int32, 4>:q = a / b;
    if (q[0i64] == 4i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="no trap (10, 11), or a hardware fault")
claim("ty1478b", D, 1478, "Reductions are methods", "rule",
      "Reductions are methods: `.sum()/.min()/.max()` on numeric lanes, `.all()/.any()` on bool lanes.",
      expect="run:0",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(3i32), 9i32, -2i32, 5i32);
    if (a.sum() != 15i32) { exit 10i32; }
    if (a.min() != -2i32) { exit 11i32; }
    if (a.max() != 9i32) { exit 12i32; }
    simd<int32, 4>:zero = simd(raw v32(0i32));
    simd<bool, 4>:c = a > zero;
    if (c.all()) { exit 13i32; }
    if (!(c.any())) { exit 14i32; }
    exit 0i32;"""),
      wrong="refused, or 10-14")
claim("ty1480", D, 1480, "float `.sum()` is deterministic BY CONSTRUCTION", "rule",
      "A float `.sum()` is an ordered fold: [1e16, 1, -1e16, 1] sums to 1 (a tree reduction gives 0).",
      expect="run:0",
      src=prog_("""    simd<flt64, 4>:a = simd(raw vf64(10000000000000000.0f64), 1.0f64, -10000000000000000.0f64, 1.0f64);
    flt64:s = a.sum();
    if (s != 1.0f64) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: another order (0 for pairwise)")
claim("ty1481", D, 1481, "Casts are elementwise under the scalar", "rule",
      "A simd cast is elementwise: `simd<int32, 4> => simd<int64, 4>` widens each lane.",
      expect="run:0",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(-3i32), 4i32, 5i32, 6i32);
    simd<int64, 4>:w = a => simd<int64, 4>;
    if (w[0i64] != -3i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or 10")
claim("ty1482", D, 1482, "rules and never change N", "rule",
      "A simd cast never changes N: `simd<int32, 4> => simd<int64, 2>` is refused.", expect="refuse",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(1i32));
    simd<int64, 2>:w = a => simd<int64, 2>;
    exit 0i32;"""),
      wrong="accepted")
claim("ty1482b", D, 1482, "Shuffles are OUT by decision (D-194)", "rule",
      "There are no shuffles.",
      untestable="[vague] no shuffle spelling is named, so no program can try one")
claim("ty1487", D, 1487, "division's any-lane guard is ONE `div-zero` row", "rule",
      "A simd division's any-lane guard is one div-zero row and one div-min row (a signed element).",
      expect="sh:0",
      sh=obl("""func:f = simd<int32, 4>(simd<int32, 4>:a, simd<int32, 4>:b) never fails { pass (a / b); };
""" + main_("""    simd<int32, 4>:x = simd(raw v32(8i32));
    simd<int32, 4>:y = simd(raw v32(2i32));
    simd<int32, 4>:q = raw f(x, y);
    if (q[0i64] != 4i32) { exit 10i32; }
    exit 0i32;"""), """
echo "f's kinds: $(kinds f)"
[ "$(n f div-zero)" -eq 1 ] || exit 10
[ "$(n f div-min)" -eq 1 ] || exit 11
"""),
      wrong="10: not one div-zero row; 11: not one div-min row")
claim("ty1488", D, 1488, "a shift's one `shift-range`", "rule",
      "A simd shift has one shift-range row.",
      expect="sh:0",
      sh=obl("""func:f = simd<int32, 4>(simd<int32, 4>:a, simd<int32, 4>:b) never fails { pass (a << b); };
""" + main_("""    simd<int32, 4>:x = simd(raw v32(1i32));
    simd<int32, 4>:y = simd(raw v32(2i32));
    simd<int32, 4>:q = raw f(x, y);
    if (q[0i64] != 4i32) { exit 10i32; }
    exit 0i32;"""), """
echo "f's kinds: $(kinds f)"
[ "$(n f shift-range)" -eq 1 ] || exit 10
"""),
      wrong="10: not one shift-range row")
claim("ty1490", D, 1490, "its ELEMENT's kind (DEF-37, 1.5.4b step 4b): integer lanes do, float lanes", "rule",
      "Float lanes do not arm DivByZero: a float simd divided by zero lanes gives infinities.",
      expect="run:0",
      src=prog_("""    simd<flt64, 2>:a = simd(raw vf64(1.0f64));
    simd<flt64, 2>:z = simd(raw vf64(0.0f64));
    simd<flt64, 2>:q = a / z;
    if (!(q[0i64] > 1.0f64)) { exit 10i32; }
    exit 0i32;"""),
      wrong="a DivByZero trap (97), or 10")
claim("ty1491", D, 1491, "integer lane's `+ - *` and an", "rule",
      "An integer lane's `+` traps IntOverflow as its scalar does.", expect="trap:IntOverflow",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(2147483647i32), 1i32, 1i32, 1i32);
    simd<int32, 4>:b = simd(raw v32(1i32));
    simd<int32, 4>:c = a + b;
    if (c[0i64] < 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="a wrapped lane (10)")
claim("ty1492", D, 1492, "integer `.sum()` trap `IntOverflow` as their scalars do", "rule",
      "An integer `.sum()` traps IntOverflow.", expect="trap:IntOverflow",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(2147483647i32), 1i32, 0i32, 0i32);
    int32:s = a.sum();
    if (s < 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="a wrapped sum (10)")
claim("ty1495", D, 1495, "spelling `v op= w` lowers through the same vector path with its guards", "rule",
      "`v += w` keeps the guards: a lane overflow traps IntOverflow.", expect="trap:IntOverflow",
      src=prog_("""    simd<int32, 4>:a = simd(raw v32(2147483647i32), 1i32, 1i32, 1i32);
    simd<int32, 4>:one = simd(raw v32(1i32));
    a += one;
    if (a[0i64] < 0i32) { exit 10i32; }
    exit 11i32;"""),
      wrong="a wrapped lane (10), or refused (EMIT-002, DEF-39)")

# ================================================================== 15. library vectors
for ln, lib, t, size in ((1504, "nvec", "vec2", 16), (1505, "nvec", "vec3", 24), (1506, "nvec", "vec4", 32),
                         (1507, "ntensor", "matrix<int64>", 24), (1508, "ntensor", "tensor<int64>", 24)):
    claim("ty%04d" % ln, D, ln, "| `%s` |" % t.replace("<int64>", "<T>"), "row",
          "`%s` (the library's `%s.npk`) is %d bytes." % (t, lib, size),
          expect="sh:0",
          sh=lib_run([lib], """    if (#size_of<S0>() != %di64) { exit 10i32; }
    exit 0i32;""" % size, "struct:S0 = { %s:v; };" % t),
          wrong="10: another size")
claim("ty1510", D, 1510, "**These are LIBRARY types and are not keywords** (D-135)", "rule",
      "`vec2` is not a keyword: a local of that name compiles.",
      expect="run:0",
      src=prog_("""    int32:vec2 = raw v32(5i32);
    if (vec2 != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused")
claim("ty1515", D, 1515, "A library cannot declare a type whose name is a keyword", "rule",
      "A type named by a keyword is refused: `struct:tbb8 = { … };`.", expect="refuse",
      src=prog_("    exit 0i32;", "struct:tbb8 = { int32:x; };"),
      wrong="accepted")
claim("ty1518", D, 1518, "`matrix<T>` and `tensor<T>` are heap-backed containers", "rule",
      "matrix and tensor are heap-backed containers with nothing SIMD about them.",
      untestable="[vague] a description of the library; the rows above test the sizes")

# ================================================================== 16. function types
claim("ty1526", D, 1526, "```llvm", "example",
      "A function `int32(int32, int32)` is `define { i32, i32 } @f(i32, i32)`.",
      expect=r'ir:(?m)^define \{ i32, i32 \} @"?(?:[\w$]+\.)*m11add"?\(i32 [^,\n]+, i32 ',
      src=prog_("""    int32:v = m11add(raw v32(1i32), 2i32) ?| 0i32;
    if (v != 3i32) { exit 10i32; }
    exit 0i32;""", "func:m11add = int32(int32:a, int32:b) {\n    pass (a + b);\n};"),
      wrong="another signature")
claim("ty1535", D, 1535, "When Result elision proves function is infallible", "rule",
      "A function proved infallible returns a raw `i32`: a `never fails` int32 function is `define i32`.",
      expect=r'ir:(?m)^define i32 @"?(?:[\w$]+\.)*m11e"?\(',
      src=prog_("""    if (raw m11e(raw v32(1i32), 2i32) != 1i32) { exit 10i32; }
    exit 0i32;""", "func:m11e = int32(int32:a, int32:_~b) never fails { pass a; };"),
      wrong="a Result return: no elision")

# ================================================================== 17. Future
claim("ty1545", D, 1545, "**Not surface syntax.** Nothing in the language produces a `Future<T>`", "rule",
      "`Future<T>` cannot be named in a signature.", expect="refuse",
      src=prog_("    exit 0i32;", "func:m11f = int32(Future<int32>:_~f) never fails { pass 0i32; };"),
      wrong="accepted")
claim("ty1558", D, 1558, "```llvm", "example",
      "A future is `{ ptr, ptr }`, a coroutine handle and a result slot.",
      untestable="[internal] a lowering artifact no program can name (the text's own words)")

# ================================================================== 18. dyn
TR = """trait:A = { func:a = int32(Self->:self) never fails; };
trait:B = { func:b = int32(Self->:self) never fails; };
trait:C = { func:c = int32(Self->:self) never fails; };
struct:S = { int32:n; };
impl:S:A = { func:a = int32(S->:self) never fails { pass self.n; }; };
impl:S:B = { func:b = int32(S->:self) never fails { pass self.n + 1i32; }; };
impl:S:C = { func:c = int32(S->:self) never fails { pass self.n + 2i32; }; };"""
claim("ty1567", D, 1567, "**One data word and ONE VTABLE WORD PER TRAIT**", "rule",
      "A `dyn` is (N+1) x 8 bytes: 16 for one trait, 24 for two.",
      expect="run:0",
      src=prog_("""    if (#size_of<dyn A>() != 16i64) { exit 10i32; }
    if (#size_of<dyn A & B>() != 24i64) { exit 11i32; }
    exit 0i32;""", TR),
      wrong="10/11: another size")
claim("ty1572", D, 1572, "```llvm", "example",
      "`dyn A` is `{ ptr, ptr }`: a `dyn A` parameter has that type.",
      expect=ir_all(param("m11d", r"\{ ?ptr, ptr ?\}")),
      src=prog_("    exit 0i32;", TR + "\nfunc:m11d = int32(move dyn A:d) never fails { discard(d); pass 0i32; };"),
      wrong="another carrier")
claim("ty1576", D, 1576, "; `dyn A & B & C` — one vtable word per bound, 32 bytes", "rule",
      "`dyn A & B & C` is 32 bytes.",
      expect="run:0",
      src=prog_("""    if (#size_of<dyn A & B & C>() != 32i64) { exit 10i32; }
    exit 0i32;""", TR),
      wrong="10: another size")
claim("ty1579", D, 1579, "; Vtable: function pointers in TRAIT DECLARATION ORDER (D-158)", "rule",
      "A vtable holds one adapter thunk per method, in declaration order.",
      untestable="[internal] a vtable's slot order is not observable from a program")
claim("ty1584", D, 1584, "The bounds are **canonically ordered by trait name at type interning**", "rule",
      "`dyn A & B` and `dyn B & A` are one type: one binds to the other.",
      expect="run:0",
      src=prog_("""    S:s = S{ n: raw v32(1i32) };
    dyn A & B:x = move(s);
    dyn B & A:y = move(x);
    discard(y);
    exit 0i32;""", TR),
      wrong="refused: two types")
claim("ty1586", D, 1586, "Widening (`dyn A & B` → `dyn A`) is a", "rule",
      "Widening `dyn A & B` to `dyn A` compiles and keeps the value.",
      expect="run:0",
      src=prog_("""    S:s = S{ n: raw v32(1i32) };
    dyn A & B:x = move(s);
    dyn A:y = move(x);
    discard(y);
    exit 0i32;""", TR),
      wrong="refused")
