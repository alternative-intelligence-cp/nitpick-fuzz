"""M11 claims: CONTROL_REFERENCE.md (lines 1-415) at HUNT2 (9126350), extracted by session 8.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). Where an M10 item tests exactly the claim, the claim
links it (`m10=`) and takes M10's expectation. A payload enum is spelled as the
compiler's own consuming-pick programs spell it (`enum:Opt = { Non; Som(string); };`,
`Opt.Som(v)`, `(Som(x))`).
"""
from m11lib import *

covers("CONTROL", 1)

D = "CONTROL"
S68 = "abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
OPT = 'enum:Opt = { Non; Som(string); };\nfunc:mk = string() never fails { pass string_concat("%s", "c"); };' % S68


def chk(expr_true, code=10):
    return "    if (!(%s)) { exit %di32; }" % (expr_true, code)


# ================================================================== the header
claim("ct0003", D, 3, "C-style three-clause `for` loops are deliberately **not** among them", "rule",
      "There is no C-style three-clause for: it is refused.",
      expect="refuse",
      src=main_("""    int32:s = 0i32;
    for (int32:i = 0i32; i < 3i32; i += 1i32) { s += i; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0005", D, 5, "**control flow blocks do NOT end with semicolons**", "rule",
      "A semicolon after an if block's closing brace is a syntax error.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if (x == 1i32) { x = 2i32; };
    exit 0i32;"""),
      wrong="accepted: the stray `;` ignored")

# ================================================================== 1. branching
claim("ct0012", D, 12, "Parentheses around the condition are required", "rule",
      "The if condition's parentheses are required: `if x == 1i32 { }` is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    if x == 1i32 { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0014", D, 14, "```nitpick", "example",
      "if / else if / else picks the first true branch, the else catching the rest.",
      expect="run:0",
      src=main_("""    int32:r = 0i32;
    int32:x = raw v32(2i32);
    if (x == 1i32) {
        r = 1i32;
    } else if (x == 2i32) {
        r = 2i32;
    } else {
        r = 3i32;
    }
%s
    exit 0i32;""" % chk("r == 2i32")),
      wrong="refused or 10")
claim("ct0026", D, 26, "Case patterns must be wrapped in parentheses", "rule",
      "Case patterns must be parenthesised: a bare pattern is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    pick (x) { 1i32 { exit 10i32; }, (*) { exit 0i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0027", D, 27, "Cases must be separated by commas", "rule",
      "Cases must be separated by commas: two arms with none between them are refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    pick (x) { (1i32) { exit 10i32; } (*) { exit 0i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0028", D, 28, "The default/catch-all case is designated by `(*)`", "rule",
      "`(*)` is the catch-all: a value no other arm names takes it.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(7i32);
    int32:r = 0i32;
    pick (x) { (1i32) { r = 1i32; }, (*) { r = 2i32; } }
%s
    exit 0i32;""" % chk("r == 2i32")),
      wrong="refused or 10")
claim("ct0029", D, 29, "Nitpick does not implicitly fall through", "rule",
      "There is no implicit fallthrough.",
      m10="p01_no_implicit_fallthrough")
claim("ct0030", D, 30, "**The selector may not be an `Optional`**", "rule",
      "A pick's selector may not be an Optional: TYPE-065.",
      expect="refuse:TYPE-065",
      src=main_("""    int64?:o = raw v64(3i64);
    pick (o) { (3i64) { exit 0i32; }, (*) { exit 10i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0030b", D, 30, "`pick (o ?? default) { … }`", "rule",
      "The Optional is reached with `??`: `pick (o ?? default)` is accepted.",
      expect="run:0",
      src=main_("""    int64?:o = raw v64(3i64);
    int32:r = 0i32;
    pick (o ?? 0i64) { (3i64) { r = 1i32; }, (*) { r = 2i32; } }
%s
    exit 0i32;""" % chk("r == 1i32")),
      wrong="refused or 10")
claim("ct0030c", D, 30, "A frac (D-198) and a complex (D-199) are refused at the selector", "rule",
      "A frac selector is refused by the same rule.",
      expect="refuse",
      src=main_("""    frac32:f = raw vf(1i32);
    pick (f) { (*) { exit 0i32; } }
    exit 0i32;""", "func:vf = frac32(int32:n) never fails { pass n => frac32; };"),
      wrong="accepted")
claim("ct0031", D, 31, "**One rule set for both spellings**", "rule",
      "The expression form of pick yields through `give`: `int32:v = pick (s) { (A) { give 1i32; }, "
      "(*) { give 0i32; } };`.",
      expect="run:0",
      src=main_("""    St:s = St.A;
    int32:v = pick (s) { (A) { give 1i32; }, (*) { give 0i32; } };
%s
    exit 0i32;""" % chk("v == 1i32"), "enum:St = { A; B; };"),
      wrong="refused or 10")
claim("ct0032", D, 32, "a `move` of one, or a `pass` of one out of the function, is TYPE-047", "rule",
      "A lending pick binds a view: a `move` of an owning view is TYPE-047.",
      expect="refuse:TYPE-047",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    pick (e) {
        (Som(x)) { string:t = move(x); exit 10i32; },
        (Non) { exit 11i32; }
    }
    exit 0i32;""", OPT),
      wrong="accepted: the lent payload moved out")
claim("ct0032b", D, 32, "a copy of an owning view is TYPE-046", "rule",
      "A copy of an owning view is TYPE-046.",
      expect="refuse:TYPE-046",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    pick (e) {
        (Som(x)) { string:t = x; exit 10i32; },
        (Non) { exit 11i32; }
    }
    exit 0i32;""", OPT),
      wrong="accepted")
claim("ct0032c", D, 32, "**A view has no address**", "rule",
      "A view has no address: assigning a view is TYPE-066.",
      expect="refuse:TYPE-066",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    pick (e) {
        (Som(x)) { x = raw mk(); exit 10i32; },
        (Non) { exit 11i32; }
    }
    exit 0i32;""", OPT),
      wrong="accepted")
claim("ct0032d", D, 32, "**The selector is frozen while a view of it is live**", "rule",
      "The selector is frozen while a view of it lives: writing the selector in an arm that binds a "
      "name is TYPE-067.",
      expect="refuse:TYPE-067",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    pick (e) {
        (Som(x)) { e = Opt.Non; exit 10i32; },
        (Non) { exit 11i32; }
    }
    exit 0i32;""", OPT),
      wrong="accepted: the selector rewritten under its view")
claim("ct0032e", D, 32, "an arm that binds nothing may write it", "rule",
      "An arm that binds nothing may write the selector.",
      expect="run:0",
      src=main_("""    St:state = St.Idle;
    pick (state) { (Idle) { state = St.Running; }, (*) { exit 10i32; } }
    pick (state) { (Running) { exit 0i32; }, (*) { exit 11i32; } }
    exit 12i32;""", "enum:St = { Idle; Running; };"),
      wrong="refused, or 10-12")
claim("ct0032f", D, 32, "A CONSUMING `pick (move(v))` (D-216) takes the value apart", "rule",
      "A consuming pick's bindings own their payloads, and the selector is moved-from after: reading "
      "it is refused.",
      expect="refuse",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    pick (move(e)) {
        (Som(x)) { if (string_bytes(x)[0i64] != 97u8) { exit 10i32; } },
        (Non) { exit 11i32; }
    }
    pick (e) { (Non) { exit 12i32; }, (*) { exit 13i32; } }
    exit 0i32;""", OPT),
      wrong="accepted: the moved-from selector read (DEF-118's shape)")
claim("ct0034", D, 34, "```nitpick", "example",
      "The fallthrough example: `fall two;` in arm one continues into arm two.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(1i32);
    pick (x) {
        (0i32) { println("Zero"); },
        one: (1i32) { fall two; },            // Explicit fallthrough
        two: (2i32) { println("One or Two"); },
        (*) { println("Other"); }             // Default case
    }
    exit 0i32;"""),
      wrong="refused (println is not a prelude function), or another exit")
claim("ct0047", D, 47, "```nitpick", "example",
      "pick destructures struct and enum variants.",
      untestable="[vague] the example's bodies are `...` and its types undeclared; the destructuring "
                 "binding modes are ct0032 … ct0032f and ct0055")
claim("ct0055", D, 55, "In a lending `pick` these names are views of `event`'s fields and payload", "rule",
      "A lending pick's names are views of the payload: reading one is accepted.",
      expect="run:0",
      src=main_("""    Opt:e = Opt.Som(raw mk());
    int32:r = 0i32;
    pick (e) {
        (Som(x)) { if (string_bytes(x)[0i64] == 97u8) { r = 1i32; } },
        (Non) { r = 2i32; }
    }
%s
    exit 0i32;""" % chk("r == 1i32"), OPT),
      wrong="refused or 10")
claim("ct0060", D, 60, "**`fall label;`** — falls through to the labelled arm", "rule",
      "`fall label;` falls through to the labelled arm.",
      m10="p02_fall_to_label")
claim("ct0061", D, 61, "**`give expr;`** — yields a value out of the `pick` block", "rule",
      "`give` yields a value out of a pick used as an expression.",
      m10="p09_pick_expression_give")
claim("ct0063", D, 63, "**`(!)` is removed** (D-061)", "rule",
      "`(!)` is removed: an arm spelled `(!)` is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    pick (x) { (1i32) { exit 0i32; }, (!) { exit 10i32; }, (*) { exit 11i32; } }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0070", D, 70, "is `#unreachable()`", "rule",
      "An arm whose body is `#unreachable()` traps when it is reached.",
      expect="trap:Unreachable",
      src=main_("""    int32:x = raw v32(2i32);
    pick (x) { (1i32) { exit 10i32; }, (*) { #unreachable(); } }
    exit 11i32;"""),
      wrong="11: the arm proceeded")
claim("ct0073", D, 73, "**`pick` must be exhaustive**", "rule",
      "A pick must be exhaustive.",
      m10="p10_int_pick_not_exhaustive")
claim("ct0074", D, 74, "explicit `ERR:` arm", "rule",
      "A tbb selector requires an explicit ERR: arm; `(*)` may not absorb it.",
      m10="p12_tbb_pick_needs_err_arm")
claim("ct0078", D, 78, "individual arms can be guarded by a conditional `where` clause", "rule",
      "An arm guarded by a false `where` moves on to the next arm.",
      m10="p08_guard_false_moves_on")
claim("ct0080", D, 80, "```nitpick", "example",
      "pick matches a macro invocation pattern with a where guard: `MyMacro!(a, b) where (a > b)`.",
      expect="run:0",
      src=main_("""    int32:ast_node = raw v32(1i32);
    pick (ast_node) {
        MyMacro!(a, b) where (a > b) {
            // executes if it matches MyMacro! AND a > b
        }
    }
    exit 0i32;"""),
      wrong="refused (MacroPattern removed; `name!` is not a macro invocation)")
claim("ct0089", D, 89, "explicitly uses the `is` keyword rather than `?`", "rule",
      "The ternary is `is`, not `?`: `a > b ? a : b` is refused.",
      expect="refuse",
      src=main_("""    int32:a = raw v32(2i32);
    int32:b = raw v32(1i32);
    int32:m = a > b ? a : b;
    exit 0i32;"""),
      wrong="accepted")
claim("ct0091", D, 91, "```nitpick", "example",
      "`int32:max = is (a > b) : a : b;` is the larger.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(5i32);
    int32:b = raw v32(9i32);
    // Syntax: is (condition) : true_expr : false_expr
    int32:max = is (a > b) : a : b;
%s
    exit 0i32;""" % chk("max == 9i32")),
      wrong="refused or 10")

# ================================================================== 2. iteration
claim("ct0100", D, 100, "`break;` to exit the innermost loop", "rule",
      "`break;` exits the innermost loop only.",
      expect="run:0",
      src=main_("""    int32:outer = 0i32;
    int32:inner = 0i32;
    for (int32:i in 0i32...3i32) {
        outer += 1i32;
        for (int32:j in 0i32...5i32) {
            if (j == 1i32) { break; }
            inner += 1i32;
        }
        discard(i);
    }
%s
%s
    exit 0i32;""" % (chk("outer == 3i32", 10), chk("inner == 3i32", 11))),
      wrong="refused, 10 (the outer loop broken too), or 11")
claim("ct0100b", D, 100, "`continue;` to skip to the next iteration across all loop types", "rule",
      "`continue;` skips to the next iteration.",
      m10="l27_continue_in_for")
claim("ct0108", D, 108, "A `while`/`when` with neither", "rule",
      "A while with neither `decreases` nor `unbounded` is TYPE-072.",
      expect="refuse:TYPE-072",
      src=main_("""    int32:x = raw v32(0i32);
    while (x < 3i32) { x += 1i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0109", D, 109, "or both, is `NITPICK-TYPE-072`", "rule",
      "A while with both `decreases` and `unbounded` is TYPE-072.",
      expect="refuse:TYPE-072",
      src=main_("""    int32:x = raw v32(0i32);
    while (x < 3i32) decreases 3i32 - x unbounded { x += 1i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0109b", D, 109, "`for`, `loop` and `till` are bounded by", "rule",
      "for, loop and till take neither clause: a `for ... decreases` is refused.",
      expect="refuse",
      src=main_("""    int32:s = 0i32;
    for (int32:i in 0i32...3i32) decreases 3i32 { s += i; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0115", D, 115, "```nitpick", "example",
      "`while (x < 10i32) decreases 10i32 - x { x += 1i32; }` runs until x is 10.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(0i32);
    while (x < 10i32) decreases 10i32 - x {
        x += 1i32;
    }
%s
    exit 0i32;""" % chk("x == 10i32")),
      wrong="refused or 10")
claim("ct0122", D, 122, "inherently tracks **whether the body ever executed**", "rule",
      "when tracks whether its body ever executed.",
      m10="w01_when_ran_then")
claim("ct0124", D, 124, "```nitpick", "example",
      "The when example: with x = 3 the body runs, then `then` runs and `end` does not.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(3i32);
    int32:t = 0i32;
    int32:e = 0i32;
    when (x > 0i32) decreases x {
        // Loop body
        x -= 1i32;
    } then {
        t = 1i32;
    } end {
        e = 1i32;
    }
%s
%s
    exit 0i32;""" % (chk("t == 1i32 && e == 0i32", 10), chk("x == 0i32", 11))),
      wrong="refused, or 10/11")
claim("ct0142", D, 142, "| body ran ≥ 1 time, condition later became false | `then` |", "row",
      "A body that ran and then saw its condition false takes `then`.",
      m10="w01_when_ran_then")
claim("ct0143", D, 143, "| body ran ≥ 1 time, exited early via `break` | `then` |", "row",
      "A body that broke out takes `then`.",
      m10="w03_when_break_then")
claim("ct0144", D, 144, "| condition false initially — body never ran | `end` |", "row",
      "A body that never ran takes `end`.",
      m10="w02_when_never_ran_end")
claim("ct0146", D, 146, "Both clauses are optional.", "rule",
      "Both clauses are optional: a when with neither `then` nor `end` compiles and runs.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(3i32);
    when (x > 0i32) decreases x { x -= 1i32; }
%s
    exit 0i32;""" % chk("x == 0i32")),
      wrong="refused or 10")
claim("ct0161", D, 161, "```nitpick", "example",
      "`for (int64:i in 1..3)` visits 1, 2 and 3.",
      expect="run:0",
      src=main_("""    int64:s = 0i64;
    for (int64:i in 1i64..3i64) {
        s += i;
    }
%s
    exit 0i32;""" % chk("s == 6i64")),
      wrong="refused, or 10")
claim("ct0170", D, 170, "```nitpick", "example",
      "The C-style three-clause for, the first rejected form, is refused.",
      expect="refuse",
      src=main_("""    int32:s = 0i32;
    for (int32:i = 0i32; i < 10i32; i += 1i32) { s += i; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0172", D, 172, "untyped binding — not supported", "rule",
      "An untyped for binding, `for (i in 0..10)`, is refused.",
      expect="refuse",
      src=main_("""    int64:s = 0i64;
    for (i in 0i64..10i64) { s += i; }
    exit 0i32;"""),
      wrong="accepted: an inferred binding")
claim("ct0181", D, 181, "there is no `auto`, `var`, or `let`", "rule",
      "There is no `let`: an inferred declaration is refused.",
      expect="refuse",
      src=main_("""    let x = raw v32(1i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ct0183", D, 183, "a range, a slice, an array, or a", "rule",
      "for iterates a slice.",
      expect="run:0",
      src=main_("""    int32[4]:a = [raw v32(1i32), 2i32, 3i32, 4i32];
    int32[]:sl = a[1i64...3i64];
    int32:s = 0i32;
    for (int32:v in sl) { s += v; }
%s
    exit 0i32;""" % chk("s == 5i32")),
      wrong="refused or 10")
claim("ct0183b", D, 183, "an array", "rule",
      "for iterates an array in order.",
      m10="l25_for_over_array_in_order")
claim("ct0184", D, 184, "value whose type implements the prelude trait `Iterator`", "rule",
      "for iterates a value whose type implements Iterator (`next` returning `Item?`, NIL ending it).",
      expect="run:0",
      src=main_("""    Count:c = Count{ n: 0i32 };
    int32:s = 0i32;
    for (int32:v in c) { s += v; }
%s
    exit 0i32;""" % chk("s == 6i32"), """struct:Count = { int32:n; };
impl:Count:Iterator = {
    assoc:Item = int32;
    func:next = int32?(Self->:self) never fails {
        if (self.n >= 3i32) { pass NIL; }
        self.n = self.n + 1i32;
        pass self.n;
    };
};"""),
      wrong="refused (no Iterator form), or 10")
claim("ct0187", D, 187, "Anything else is refused at the checker by", "rule",
      "A for binding of another type than the element's is refused by name, TYPE-033.",
      m10="l28_for_binding_type_mismatch")
claim("ct0191", D, 191, "expose it inside the block via the special `$` keyword", "rule",
      "loop and till expose the counter as `$`.",
      m10="l12_loop_ascending")
claim("ct0193", D, 193, "inside a `Rules`", "rule",
      "Inside a Rules body `$` is the subject.",
      expect="run:0",
      src=main_("""    limit<r_pos> int32:x = raw v32(5i32);
%s
    exit 0i32;""" % chk("x == 5i32"), "Rules<int32>:r_pos = { $ > 0i32 };"),
      wrong="refused or 10")
claim("ct0198", D, 198, "Counts **up from 0** to `limit`", "rule",
      "till counts up from 0 to limit (exclusive).",
      m10="l10_till_counts_from_zero")
claim("ct0199", D, 199, "```nitpick", "example",
      "`till(10i32, 1i32) { x += $; }` sums 0 to 9: 45.",
      expect="run:0",
      src=main_("""    int32:x = 0i32;
    till(10i32, 1i32) {
        x += $;  // '$' ranges from 0 to 9
    }
%s
    exit 0i32;""" % chk("x == 45i32")),
      wrong="refused or 10")
claim("ct0205", D, 205, "**Direction is inferred**", "rule",
      "loop's direction is inferred from start and limit.",
      m10="l13_loop_descending")
claim("ct0207", D, 207, "```nitpick", "example",
      "`loop(0i32, 10i32, 1i32)` sums 0..9 (45); `loop(10i32, 0i32, 1i32)` sums 10..1 (55).",
      expect="run:0",
      src=main_("""    int32:x = 0i32;
    loop(0i32, 10i32, 1i32) {
        x += $;  // ascending:  0, 1, ..., 9
    }
%s
    x = 0i32;
    loop(10i32, 0i32, 1i32) {
        x += $;  // descending: 10, 9, ..., 1
    }
%s
    exit 0i32;""" % (chk("x == 45i32", 10), chk("x == 55i32", 11))),
      wrong="refused, 10 or 11")
claim("ct0220", D, 220, "A negative step is a **compile error**", "rule",
      "A negative literal step is a compile error.",
      m10="l20_negative_step_literal_refused")
claim("ct0222", D, 222, "falling back to a runtime check that traps to", "rule",
      "A computed step is checked at run time: a zero step traps.",
      m10="l21_zero_step_computed_traps")
claim("ct0233", D, 233, "| `step` negative or zero | compile error |", "row",
      "A literal zero step is a compile error.",
      m10="l19_zero_step_literal_refused")
claim("ct0234", D, 234, "| `start == limit` | zero iterations |", "row",
      "start == limit is zero iterations.",
      m10="l14_loop_start_equals_limit")
claim("ct0235", D, 235, "| `till` with `limit <= 0` | zero iterations", "row",
      "till with limit <= 0 is zero iterations.",
      m10="l11_till_nonpositive_limit")
claim("ct0236", D, 236, "| a bound is `tbb` holding ERR | traps to `failsafe`", "row",
      "A loop bound that is a tbb holding ERR traps to failsafe (TbbErr).",
      expect="trap:TbbErr",
      src=main_("""    tbb32:e = raw vt32(2147483647tbb32) + 1tbb32;
    tbb32:s = 0tbb32;
    till(e, 1tbb32) { s = s + 1tbb32; }
    exit 10i32;"""),
      wrong="10: the loop ran on an ERR bound, or refused (a tbb bound not accepted)")
claim("ct0242", D, 242, "`loop` takes three arguments and `till` two", "rule",
      "loop takes three arguments: a two-argument loop is refused.",
      expect="refuse",
      src=main_("""    int32:x = 0i32;
    loop(0i32, 10i32) { x += $; }
    exit 0i32;"""),
      wrong="accepted, or a backend death with no span")
claim("ct0255", D, 255, "**There is no `loop { }` infinite form and no do-while construct.**", "rule",
      "There is no infinite `loop { }`: it is refused.",
      expect="refuse",
      src=main_("""    loop { exit 0i32; }
    exit 0i32;"""),
      wrong="accepted")
claim("ct0255b", D, 255, "`while (true)", "rule",
      "`while (true) unbounded` is the unbounded loop, left by break.",
      expect="run:0",
      src=main_("""    int32:n = 0i32;
    while (true) unbounded {
        n += 1i32;
        if (n == 3i32) { break; }
    }
%s
    exit 0i32;""" % chk("n == 3i32")),
      wrong="refused or 10")
claim("ct0258", D, 258, "defines `till` as do-while", "rule",
      "till is not a do-while: with limit 0 the body never runs.",
      m10="l11_till_nonpositive_limit")
claim("ct0266", D, 266, "```nitpick", "example",
      "The labelled-loop example: `break outer` leaves both loops.",
      expect="run:0",
      src=main_("""    bool:fatal_error = raw vb(true);
    int32:trips = 0i32;
    // the outer loop runs until the inner one breaks out of it
    outer: while (true) unbounded {
        trips += 1i32;
        // the inner loop ends only through `break outer`
        while (true) unbounded {
            if (fatal_error) {
                break outer;
            }
        }
    }
%s
    exit 0i32;""" % chk("trips == 1i32")),
      wrong="refused, or a hang (break left only the inner loop)")
claim("ct0278", D, 278, "`break label;` and `continue label;` both target a labelled loop", "rule",
      "`continue label;` targets a labelled loop.",
      m10="l26_labelled_continue")

# ================================================================== 3. discarding values
claim("ct0286", D, 286, "**`discard(expr);`**", "rule",
      "`discard(expr);` discards a value.",
      expect="run:0",
      src=main_("""    int32:v = raw v32(100i32);
    discard(v);
    exit 0i32;"""),
      wrong="refused")
claim("ct0287", D, 287, "**`_~ expr;`**", "rule",
      "`_~ expr;` desugars to discard().",
      expect="run:0",
      src=main_("""    _~ raw v32(42i32);
    exit 0i32;"""),
      wrong="refused")
claim("ct0289", D, 289, "```nitpick", "example",
      "The discard example compiles.",
      expect="run:0",
      src=main_("""    int32:unused_val = 100i32;
    discard(unused_val);

    // Or using the shorthand operator
    _~ 42i32;
    exit 0i32;"""),
      wrong="refused")

# ================================================================== 4. statement-level constructs
claim("ct0306", D, 306, "Blocks introduce a lexical", "rule",
      "A block introduces a lexical scope: its variables are invisible outside it.",
      m10="h03_block_binding_invisible")
claim("ct0308", D, 308, "bindings are destroyed at the closing brace", "rule",
      "Scope-managed bindings are destroyed at the block's closing brace: a list in a block is freed "
      "before a larger one after it, which peaks alone.",
      expect="run:0", heap="24000/16000/2",
      src=main_("""    {
        List<int64>:a = raw list_init::<int64>(1000i64);
%s
    }
    List<int64>:b = raw list_init::<int64>(2000i64);
%s
    exit 0i32;""" % (chk("a.cap == 1000i64", 10), chk("b.cap == 2000i64", 11))),
      wrong="peak 24000: the block's list outlived its brace")
claim("ct0314", D, 314, "**`NITPICK-IF-002`**", "rule",
      "An assignment inside an if condition is rejected as NITPICK-IF-002.",
      expect="refuse:IF-002",
      src=main_("""    int32:x = raw v32(1i32);
    if (x = 3i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted, or another code (OP:65: the program cannot be written, so IF-002 never fires)")
claim("ct0317", D, 317, "**`NITPICK-IF-001`**", "rule",
      "An else without an immediately preceding if is NITPICK-IF-001.",
      expect="refuse:IF-001",
      src=main_("""    int32:x = raw v32(1i32);
    x = 2i32;
    else { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted, or another code")
claim("ct0319", D, 319, "**`NITPICK-WHEN-001`**", "rule",
      "An orphaned `then` without a preceding when is NITPICK-WHEN-001.",
      expect="refuse:WHEN-001",
      src=main_("""    int32:x = raw v32(1i32);
    then { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted, or another code")
claim("ct0323", D, 323, "**`pass expr;`** — returns a successful `Result<T>`", "rule",
      "`pass expr;` returns a successful Result.",
      expect="run:0",
      src=main_("""    Result<int32>:r = f();
    if (r.is_error) { exit 10i32; }
    if (r.value != 4i32) { exit 11i32; }
    exit 0i32;""", "func:f = int32() { pass 4i32; };"),
      wrong="refused, 10 or 11")
claim("ct0324", D, 324, "**`fail errCode;`** — returns an errored `Result<T>`", "rule",
      "`fail errCode;` returns an errored Result carrying the code.",
      expect="run:0",
      src=main_("""    Result<int32>:r = f();
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    exit 0i32;""", "error:E1;\nfunc:f = int32() { fail E1; };"),
      wrong="refused, 10 or 11")
claim("ct0325", D, 325, "*(expression, not a statement)* propagates", "rule",
      "relay propagates the same error code, verbatim.",
      m10="r02_relay_same_error")
claim("ct0326", D, 326, "if `expr` is an error the enclosing function returns immediately", "rule",
      "relay returns at once on an error.",
      m10="r03_relay_returns_at_once")
claim("ct0332", D, 332, "the literal form, the only way to return a value", "rule",
      "`return Result{ … };` returns a value and an error simultaneously.",
      m10="r10_result_literal_both")
claim("ct0334", D, 334, "**Every path of a function body ends in one of these", "rule",
      "Every path of a function body ends in pass, fail, exit or a trap: an empty body is FLOW-001.",
      m10="q01_empty_body")
claim("ct0337", D, 337, "`NIL` function passes `NIL`", "rule",
      "A NIL function falling off its end is refused.",
      m10="q07_nil_function_falls_off")
claim("ct0338", D, 338, "`main` exits", "rule",
      "main without exit is refused.",
      m10="q04_main_without_exit")
claim("ct0341", D, 341, "an `if` without `else` completes", "rule",
      "A path past an if without else completes, so a missing pass after it is refused.",
      m10="q02_missing_path")
claim("ct0342", D, 342, "`if`/`else` completes if either arm does", "rule",
      "An if/else whose arms both pass does not complete: no pass is needed after it.",
      m10="q09_if_else_both_pass")
claim("ct0342b", D, 342, "a `pick` if any arm's body does", "rule",
      "A pick whose arms all pass does not complete.",
      m10="q10_pick_all_arms_pass")
claim("ct0343", D, 343, "a `while (true)` with no", "rule",
      "A while (true) with no break never completes.",
      m10="q08_while_true_never_completes")
claim("ct0344", D, 344, "every other loop and `when` completes as a whole", "rule",
      "A for loop completes as a whole.",
      m10="q11_for_loop_completes")
claim("ct0347", D, 347, "`ok()` is the taint-clearing", "rule",
      "`ok()` is the taint-clearing builtin: `ok(x)` compiles.",
      expect="run:0",
      src=main_("""    tbb8:x = raw vt8(5tbb8);
    bool:b = ok(x);
    exit 0i32;"""),
      wrong="refused (ok() was removed, D-097, OP:172)")
claim("ct0348", D, 348, "`err()` does not exist", "rule",
      "`err()` does not exist: calling it is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", "error:E1;\nfunc:f = int32() { return err(E1); };"),
      wrong="accepted")
claim("ct0354", D, 354, "a **compile-time** proof obligation discharged by Z3", "rule",
      "prove is a compile-time obligation discharged by z3 under --verify; a counterexample fails compilation.",
      untestable="[z3] the verified build's verdict; the plain build lowers prove to nothing "
                 "(VERIFICATION:78's claim)")
claim("ct0357", D, 357, "**`assert_static(cond);`**", "rule",
      "assert_static halts compilation when its condition is false (TYPE-069).",
      expect="refuse:TYPE-069",
      src=main_("""    assert_static(1i32 == 2i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ct0365", D, 365, "`NITPICK-TYPE-069` when it does not fold to a constant", "rule",
      "assert_static over a run-time value does not fold: TYPE-069.",
      expect="refuse:TYPE-069",
      src=main_("""    int32:x = raw v32(1i32);
    assert_static(x == 1i32);
    exit 0i32;"""),
      wrong="accepted")
claim("ct0366", D, 366, "in a `comptime` body both statements are evaluated per call", "rule",
      "In a comptime body assert_static is evaluated per call: a call whose argument fails it is refused.",
      expect="refuse",
      src=main_("""    int32:v = comptime(positive(0i32));
    exit v;""", """comptime func:positive = int32(int32:n) {
    assert_static(n > 0i32);
    pass n;
};"""),
      wrong="accepted")
claim("ct0375", D, 375, "Pushes a block onto a stack to run when the enclosing lexical scope exits", "rule",
      "defer pushes onto a stack: defers run LIFO.",
      m10="w04_defer_lifo")
claim("ct0377", D, 377, "```nitpick", "example",
      "`wild int8->:buf = alloc(16i64); defer { dalloc(buf); }` frees the block at the scope's exit.",
      expect="run:0",
      src=main_("""    wild int8->:buf = alloc(16i64);
    defer { dalloc(buf); }
    exit 0i32;"""),
      wrong="refused, or 96")
claim("ct0382", D, 382, "**after the exit's value is evaluated** (D-136)", "rule",
      "Defers run after the exit's value is evaluated: `pass v` returns the v read at the pass.",
      m10="w05_pass_value_before_defer")
claim("ct0382b", D, 382, "LIFO, innermost scope first", "rule",
      "Defers run innermost scope first.",
      m10="w11_defer_inner_scope_first")
claim("ct0382c", D, 382, "Runs on **every normal exit path**", "rule",
      "defer runs on fail.",
      m10="w06_defer_on_fail")
claim("ct0384", D, 384, "**`defer` does NOT run on a trap** (D-014)", "rule",
      "defer does not run on a trap.",
      m10="w09_no_defer_on_trap")
claim("ct0393", D, 393, "may appear only in `main` or", "rule",
      "exit may appear only in main or failsafe.",
      m10="e03_exit_outside_main_refused")
claim("ct0397", D, 397, "the `<wildx-states>` map must be empty", "rule",
      "A successful exit with live wildx memory triggers the failsafe trap (WildLeak).",
      expect="trap:WildLeak",
      src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    exit 0i32;"""),
      wrong="0: the live wildx page not counted")
claim("ct0397b", D, 397, "Reaching `exit` with live", "rule",
      "Reaching exit with live wild memory triggers the failsafe trap.",
      m10="e01_exit_zero_with_live_wild")
claim("ct0406", D, 406, "a failure exit keeps its code", "rule",
      "A failure exit keeps its code.",
      m10="e02_failure_exit_keeps_code")
claim("ct0409", D, 409, "`wild_release_all()` and exit positive", "rule",
      "failsafe may call wild_release_all() and exit positive; its own exit is exempt from the check.",
      expect="run:42", fs=False,
      src=main_("""    wild int8->:p = alloc(8i64);
    exit 0i32;""") + failsafe_with("""        (WildLeak) { wild_release_all(); exit 42i32; },"""),
      wrong="another code, or 70")
claim("ct0411", D, 411, "trap raised *inside* `failsafe` exits 70 directly", "rule",
      "A trap raised inside failsafe exits 70 directly.",
      expect="run:70", fs=False,
      src=main_("""    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;""") + failsafe_with("""        (IntOverflow) { int32:z = raw v32(0i32); int32:q = 10i32 / z; exit q; },"""),
      wrong="97 or a hang")
claim("ct0412", D, 412, "`wild_live_count()` is the program-visible view of the set", "rule",
      "wild_live_count() is the program-visible view of the set.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(8i64);
%s
    dalloc(p);
%s
    exit 0i32;""" % (chk("wild_live_count() == 1i64", 10), chk("wild_live_count() == 0i64", 11))),
      wrong="refused, or 10/11")
claim("ct0412b", D, 412, "Managed-regime", "rule",
      "Managed storage is not in the set: a string alive at exit 0 is not reported.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
%s
    exit 0i32;""" % chk("string_bytes(s)[0i64] == 97u8")),
      wrong="96: managed storage counted")
