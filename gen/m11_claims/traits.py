"""M11 claims: TRAITS_REFERENCE.md (lines 1-766) at HUNT2 (9126350), extracted by session 9.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). No M10 item tests exactly a TRAITS sentence.

The trait, impl and dyn spellings around each claim are the compiler's own programs' at
HUNT2 (`tests/backend/programs/async_drop.npk`, `contracts_run.npk`, `derive_*.npk`): a
trait method declared without a body, `impl:Type:Trait = { … };`, an implicit
`dyn T:d = move(v);`, and a fallible method's call read with `?|`.
"""
from m11lib import *

covers("TRAITS", 1)

D = "TRAITS"


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


SPEAKS = """trait:Speaks = { func:say = int32(Self:self); };
struct:Loud = { int32:v; int32:w; };
impl:Loud:Speaks = { func:say = int32(Loud:self) { pass self.v; }; };"""
LOUD = "    Loud:l = Loud{ v: raw v32(7i32), w: 1i32 };\n"


def two_traits(extra=""):
    return """trait:A = { func:a = int32(Self:self) never fails; };
trait:B = { func:b = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:A = { func:a = int32(S:self) never fails { pass 1i32; }; };
impl:S:B = { func:b = int32(S:self) never fails { pass 2i32; }; };""" + extra


# ================================================================== 1. philosophy
claim("tr0011", D, 11, "Nitpick uses strict **composition over inheritance**", "rule",
      "There is no class inheritance; traits and structs compose.",
      untestable="[vague] no inheritance spelling is named whose refusal a program could check")

# ================================================================== 2. traits and implementations
claim("tr0021", D, 21, "```nitpick", "example",
      "The Serializable example (a trait with `to_bytes = buffer(Self:self)`, an impl passing `result`) compiles.",
      expect="compile",
      src=main_("    exit 0i32;", """trait:Serializable = {
    func:to_bytes = buffer(Self:self);
};

struct:Message = {
    int32:id;
};

impl:Message:Serializable = {
    func:to_bytes = buffer(Message:self) {
        pass result;
    };
};"""),
      wrong="refused: the example does not compile as written")
claim("tr0037", D, 37, "`Self` denotes the implementing type inside a `trait` or `impl` body", "rule",
      "`Self` is invalid outside a trait or impl body: a free function taking `Self` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:f = int32(Self:x) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0040", D, 40, "spells these `trait:Reader { … };` (no `=`)", "rule",
      "The struck form `trait:Reader { … };` (no `=`) is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "trait:Reader { func:read = int32(Self:self); };"),
      wrong="accepted")
claim("tr0041", D, 41, "`impl Reader for FileStream { … }` (space-separated)", "rule",
      "The struck form `impl Reader for FileStream { … }` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """trait:Reader = { func:read = int32(Self:self); };
struct:FileStream = { int32:fd0; };
impl Reader for FileStream { func:read = int32(FileStream:self) { pass self.fd0; }; }"""),
      wrong="accepted")
claim("tr0045", D, 45, "Chapter 13's own `impl:Trait:for:Type` is also superseded", "rule",
      "`impl:Trait:for:Type` is superseded: refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """trait:Reader = { func:read = int32(Self:self); };
struct:FileStream = { int32:fd0; };
impl:Reader:for:FileStream = { func:read = int32(FileStream:self) { pass self.fd0; }; };"""),
      wrong="accepted")
claim("tr0048", D, 48, "> ```ebnf", "example",
      "`impl:Type:Trait = { … };` is the impl form: it compiles and the method is called.",
      expect="run:0",
      src=main_(LOUD + "%s\n    exit 0i32;" % chk("(l.say() ?| 0i32) == 7i32", 10), SPEAKS),
      wrong="refused, or 10")
claim("tr0059", D, 59, "`never fails` (`NITPICK-TYPE-041`)", "rule",
      "An impl may not drop a trait method's `never fails`: NITPICK-TYPE-041.",
      expect="refuse:NITPICK-TYPE-041",
      src=main_("    exit 0i32;", """trait:Steady = { func:get = int32(Self:self) never fails; };
struct:P = { int32:n; };
impl:P:Steady = { func:get = int32(P:self) { pass self.n; }; };"""),
      wrong="accepted, or refused with another code")
claim("tr0060", D, 60, "The reverse is fine — an impl may be", "rule",
      "An impl may be `never fails` where its trait is not; the guarantee shows on the concrete receiver: "
      "`raw l.say()` compiles.",
      expect="run:0",
      src=main_(LOUD + "%s\n    exit 0i32;" % chk("(raw l.say()) == 7i32", 10), """trait:Speaks = { func:say = int32(Self:self); };
struct:Loud = { int32:v; int32:w; };
impl:Loud:Speaks = { func:say = int32(Loud:self) never fails { pass self.v; }; };"""),
      wrong="refused")
claim("tr0067", D, 67, "Impls that omit the method inherit it; any impl", "rule",
      "An impl may override a default method: the override is called.",
      expect="run:0",
      src=main_(LOUD + "%s\n    exit 0i32;" % chk("(raw l.hello()) == 9i32", 10), """trait:Greets = {
    func:hello = int32(Self:self) never fails { pass 7i32; };
};
struct:Loud = { int32:v; int32:w; };
impl:Loud:Greets = { func:hello = int32(Loud:self) never fails { pass 9i32; }; };"""),
      wrong="refused, or 10 (the default ran)")
claim("tr0070", D, 70, "```nitpick", "example",
      "Describable: an impl giving only `name` inherits `describe`'s default, \"an object\".",
      expect="run:0",
      src=main_("""    Loud:l = Loud{ v: 1i32, w: 2i32 };
    string:d = l.describe() ?| string_concat("x", "y");
%s
    exit 0i32;""" % chk('string_equals(d, "an object")', 10), """trait:Describable = {
    func:name     = string(Self:self);            // required
    func:describe = string(Self:self) {           // default
        pass("an object");
    };
};
struct:Loud = { int32:v; int32:w; };
impl:Loud:Describable = { func:name = string(Loud:self) { pass string_concat("lo", "ud"); }; };"""),
      wrong="refused, or 10")
claim("tr0084", D, 84, "```nitpick", "example",
      "`trait:Ordered = Equatable & { … };` declares a supertrait requirement: it compiles.",
      expect="compile",
      src=main_("    exit 0i32;", """trait:Equatable = { func:same = bool(Self:a, Self:b); };
trait:Ordered = Equatable & {
    func:compare = int32(Self:a, Self:b);
};"""),
      wrong="refused")
claim("tr0090", D, 90, "Requirements are enforced **transitively**", "rule",
      "Requirements are transitive: implementing C (which requires B, which requires A) without A is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """trait:A = { func:a = int32(Self:self) never fails; };
trait:B = A & { func:b = int32(Self:self) never fails; };
trait:C = B & { func:c = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:B = { func:b = int32(S:self) never fails { pass 2i32; }; };
impl:S:C = { func:c = int32(S:self) never fails { pass 3i32; }; };"""),
      wrong="accepted without A's impl")
claim("tr0097", D, 97, "```nitpick", "example",
      "Iterator with `assoc:Item`: the impl binds `Item = int32`, and `next` returns `self.current`.",
      expect="run:0",
      src=main_("""    Range:r = Range{ current: raw v32(4i32) };
%s
    exit 0i32;""" % chk("(r.next() ?| 0i32) == 4i32", 10), """trait:Iterator = {
    assoc:Item;
    func:next = Item(Self:self);
};
struct:Range = { int32:current; };
impl:Range:Iterator = {
    assoc:Item = int32;
    func:next  = int32(Range:self) { pass(self.current); };
};"""),
      wrong="refused, or 10")
claim("tr0109", D, 109, "Associated types may carry defaults — `assoc:Error = string;`", "rule",
      "An associated type may carry a default (`assoc:Error = string;`), inherited by an impl that omits it.",
      expect="compile",
      src=main_("    exit 0i32;", """trait:Fallible = {
    assoc:Error = string;
    func:code = int32(Self:self);
};
struct:P = { int32:n; };
impl:P:Fallible = { func:code = int32(P:self) { pass self.n; }; };"""),
      wrong="refused: `Error` is a name the compiler owns (D-239)")
claim("tr0124", D, 124, "```nitpick", "example",
      "An inherent impl: Point's `magnitude` (flt64_sqrt over a call-cast `flt64(…)`) compiles.",
      expect="compile",
      src=main_("    exit 0i32;", """struct:Point = { int32:x; int32:y; };
impl:Point = {
    func:magnitude = flt64(Point:self) {
        pass(flt64_sqrt(flt64(self.x * self.x + self.y * self.y)));
    };
};"""),
      wrong="refused: a spelling the example uses is not the language's")
claim("tr0132", D, 132, "Inherent methods dispatch **statically via UFCS**", "rule",
      "Inherent methods dispatch statically; `p.magnitude()` resolves to `Point_magnitude(p)`.",
      untestable="[internal] the lowered name of an inherent method; tr0495 tests UFCS over a free function")
claim("tr0136", D, 136, "**A trait name is a namespace, so a method may be called qualified** (D-172)", "rule",
      "A trait name qualifies a method: `Speaks.say(l)` is `l.say()`.",
      expect="run:0",
      src=main_(LOUD + "%s\n    exit 0i32;" % chk("(Speaks.say(l) ?| 0i32) == 7i32", 10), SPEAKS),
      wrong="refused, or 10")
claim("tr0138", D, 138, "and is refused by name when", "rule",
      "The qualified call is refused by name when the receiver's type does not implement the trait.",
      expect="refuse",
      src=main_("""    Quiet:q = Quiet{ n: 1i32 };
    int32:v = Speaks.say(q) ?| 0i32;
    exit 0i32;""", SPEAKS + "\nstruct:Quiet = { int32:n; };"),
      wrong="accepted")
claim("tr0140", D, 140, "traits a type implements declare one name (`p.tag()` alone cannot choose, D-102)", "rule",
      "Two traits declaring one name: `p.tag()` alone is refused as ambiguous.",
      expect="refuse",
      src=main_("""    S:s = S{ n: 1i32 };
    int32:v = raw s.tag();
    exit 0i32;""", """trait:Ta = { func:tag = int32(Self:self) never fails; };
trait:Tb = { func:tag = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:Ta = { func:tag = int32(S:self) never fails { pass 1i32; }; };
impl:S:Tb = { func:tag = int32(S:self) never fails { pass 2i32; }; };"""),
      wrong="accepted: one picked silently")
claim("tr0139", D, 139, "This is how a call disambiguates", "rule",
      "The qualified call disambiguates: `Ta.tag(s)` and `Tb.tag(s)` give 1 and 2.",
      expect="run:0",
      src=main_("""    S:s = S{ n: 1i32 };
%s
    exit 0i32;""" % chk("(raw Ta.tag(s)) == 1i32 && (raw Tb.tag(s)) == 2i32", 10), """trait:Ta = { func:tag = int32(Self:self) never fails; };
trait:Tb = { func:tag = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:Ta = { func:tag = int32(S:self) never fails { pass 1i32; }; };
impl:S:Tb = { func:tag = int32(S:self) never fails { pass 2i32; }; };"""),
      wrong="refused, or 10")
claim("tr0146", D, 146, "`impl:<T>:List<T> = { … }` names its target", "rule",
      "A generic subject has inherent impls: `impl:<T>:Cell<T>` gives every instance the method.",
      expect="run:0",
      src=main_("""    Cell<int64>:c = Cell<int64>{ v: 5i64, n: raw v32(3i32) };
%s
    exit 0i32;""" % chk("(raw c.count()) == 3i32", 10), """struct:Cell<T> = { T:v; int32:n; };
impl:<T>:Cell<T> = { func:count = int32(Cell<T>:self) never fails { pass self.n; }; };"""),
      wrong="refused, or 10")
claim("tr0149", D, 149, "(`List<T>->:self`), so a generic struct's methods can mutate it", "rule",
      "An inherent family method may take its receiver by pointer: `l.push(v)` beside `list_push(@l, v)`.",
      expect="compile",
      src=main_("""    List<int64>:l = raw list_init::<int64>(4i64);
    l.push(7i64) ?! E1;
    exit 0i32;""", "error:E1;"),
      wrong="refused: no `push` method")

# ------------------------------------------------------------------ 2.5 derive
DERIVE7 = "#[derive(PartialOrd, ToString, Eq, Hash, Clone, Debug, Ord)]"
claim("tr0158", D, 158, "```nitpick", "example",
      "The seven derives on Config (an int32 and a string field) compile.",
      expect="compile",
      src=main_("    exit 0i32;", DERIVE7 + """
struct:Config = {
    int32:priority;
    string:name;
};"""),
      wrong="refused")
claim("tr0166", D, 166, "Supported, and there are **seven** (D-123)", "rule",
      "There are seven derives: an eighth name (`Default`) is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "#[derive(Default)]\nstruct:Cfg = { int32:p; };"),
      wrong="accepted")
claim("tr0169", D, 169, "`Ord` compares **in declaration order**", "rule",
      "A derived `Ord` compares fields in declaration order: (1, 9) is Less than (2, 0).",
      expect="run:0",
      src=main_("""    Two:a = Two{ x: raw v32(1i32), y: 9i32 };
    Two:b = Two{ x: raw v32(2i32), y: 0i32 };
    Ordering:o = a.cmp(b) ?| Ordering.Equal;
    int32:r = 0i32;
    pick (o) { (Ordering.Less) { r = 1i32; }, (*) { r = 2i32; } }
%s
    exit 0i32;""" % chk("r == 1i32", 10), "#[derive(Ord, Eq, PartialOrd)]\nstruct:Two = { int32:x; int32:y; };"),
      wrong="Greater (10): a later field compared first")
claim("tr0170", D, 170, "`Hash` combines with **FNV-1a**", "rule",
      "A derived Hash combines the members with FNV-1a.",
      untestable="[vague] the text names the function, not what bytes of each member it is fed in what order")
claim("tr0175", D, 175, "A refusal **names the field that blocks it**, not the type.", "rule",
      "A derive's refusal names the blocking field: `List<int64>` in field `items` is named.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\n#[derive(Eq)]\nstruct:Bag = { int32:n; List<int64>:items; };\n\n" + main_(
          "    exit 0i32;") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out | cut -c1-160\n"
         "[ $rc -eq 1 ] && grep -m1 'NITPICK-' npkc.out | grep -q items",
      wrong="the refusal names the type only")
claim("tr0177", D, 177, "**On a generic subject, derive writes the family form**", "rule",
      "`#[derive(Eq)]` on `struct:Box<T>` compiles (as `impl:<T>:Box<T>:Eq`).",
      expect="compile",
      src=main_("    exit 0i32;", "#[derive(Eq)]\nstruct:Box<T> = { T:v; };"),
      wrong="refused")
claim("tr0196", D, 196, "The bound is enforced where the impl is USED", "rule",
      "`Box<Point>` under a derived Ord is a fine type until `cmp` is called (Point implements nothing).",
      expect="compile",
      src=main_("""    Box<Point>:b = Box<Point>{ v: Point{ x: 1i32 } };
    discard(b);
    exit 0i32;""", "struct:Point = { int32:x; };\n#[derive(Ord, Eq, PartialOrd)]\nstruct:Box<T> = { T:v; };"),
      wrong="refused at the type")
claim("tr0198", D, 198, "refused naming the derive, the", "rule",
      "Calling `cmp` on `Box<Point>` (Point lacking Ord) is refused at the call, NITPICK-TYPE-017.",
      expect="refuse:NITPICK-TYPE-017",
      src=main_("""    Box<Point>:a = Box<Point>{ v: Point{ x: 1i32 } };
    Box<Point>:b = Box<Point>{ v: Point{ x: 2i32 } };
    Ordering:o = a.cmp(b) ?| Ordering.Equal;
    exit 0i32;""", "struct:Point = { int32:x; };\n#[derive(Ord, Eq, PartialOrd)]\nstruct:Box<T> = { T:v; };"),
      wrong="accepted, or refused with another code")
claim("tr0216", D, 216, "program may not declare a name the prelude declares", "rule",
      "A program may not declare a name the prelude declares: `struct:Ordering` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "struct:Ordering = { int32:x; };"),
      wrong="accepted: the prelude's name taken over")
claim("tr0222", D, 222, "**And the prelude IMPLEMENTS them for every scalar it can name**", "rule",
      "The prelude implements the derives for scalars: `a.cmp(b)` on two int32s is Less, `a.eq(a)` true.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(3i32);
    int32:b = raw v32(4i32);
    Ordering:o = raw a.cmp(b);
    int32:r = 0i32;
    pick (o) { (Ordering.Less) { r = 1i32; }, (*) { r = 2i32; } }
%s
    exit 0i32;""" % chk("r == 1i32 && (raw a.eq(a))", 10)),
      wrong="refused (no scalar impl), or 10")
claim("tr0230", D, 230, "only, answering `NIL` for `nan`", "rule",
      "A float's `partial_cmp` answers NIL for nan.",
      expect="run:0",
      src=main_("""    flt64:z = raw vf64(0.0f64);
    flt64:n = z / z;
    Ordering?:o = raw n.partial_cmp(1.0f64);
%s
    exit 0i32;""" % chk("o == NIL", 10)),
      wrong="refused, or 10 (an ordering for nan)")
claim("tr0233", D, 233, "`string` has `Eq`, `Ord` (byte-lexicographic, the shorter prefix", "rule",
      "string's Ord is byte-lexicographic with the shorter prefix Less: \"ab\" is Less than \"abc\".",
      expect="run:0",
      src=main_("""    string:a = string_concat("a", "b");
    string:b = string_concat("ab", "c");
    Ordering:o = raw a.cmp(b);
    int32:r = 0i32;
    pick (o) { (Ordering.Less) { r = 1i32; }, (*) { r = 2i32; } }
%s
    exit 0i32;""" % chk("r == 1i32", 10)),
      wrong="refused, or 10")
claim("tr0235", D, 235, "`eq`/`cmp` trap on ERR as the operator does", "rule",
      "A twisted scalar's `eq` traps on ERR, as the operator does.",
      expect="trap:TbbErr",
      src=main_("""    tbb8:e = ERR;
    bool:b = raw e.eq(e);
    if (b) { exit 10i32; }
    exit 11i32;"""),
      wrong="10/11: no trap")
claim("tr0236", D, 236, "of a pair the prelude covers is TYPE-013", "rule",
      "A program's own impl of a pair the prelude covers (`impl:int32:Ord`) is NITPICK-TYPE-013.",
      expect="refuse:NITPICK-TYPE-013",
      src=main_("    exit 0i32;", "impl:int32:Ord = { func:cmp = Ordering(int32:self, int32:other) { pass Ordering.Equal; }; };"),
      wrong="accepted, or refused with another code")
claim("tr0237", D, 237, "pair it does not cover (`impl:bool:Ord`) is admitted", "rule",
      "A pair the prelude does not cover (`impl:bool:Ord`) is admitted.",
      expect="compile",
      src=main_("    exit 0i32;", "impl:bool:Ord = { func:cmp = Ordering(bool:self, bool:other) { pass Ordering.Equal; }; };"),
      wrong="refused")


def trait_row(cid, line, quote, trait, call, rtype, text):
    claim(cid, D, line, quote, "row", text,
          expect="compile",
          src=main_("""    Pt:a = Pt{ x: raw v32(1i32), y: 2i32 };
    Pt:b = Pt{ x: raw v32(1i32), y: 2i32 };
    %s:r = %s;
    discard(r);
    exit 0i32;""" % (rtype, call), "#[derive(%s)]\nstruct:Pt = { int32:x; int32:y; };" % trait),
          wrong="refused: another method name or return type")


trait_row("tr0246", 246, "| `Eq` | `func:eq = bool(Self:self, Self:other);` |", "Eq", "a.eq(b) ?| false", "bool",
          "Eq's method is `eq`, returning bool.")
trait_row("tr0247", 247, "| `Ord` | `func:cmp = Ordering(Self:self, Self:other);` |", "Ord, Eq, PartialOrd",
          "a.cmp(b) ?| Ordering.Equal", "Ordering", "Ord's method is `cmp`, returning Ordering.")
trait_row("tr0248", 248, "| `PartialOrd` | `func:partial_cmp = Ordering?(Self:self, Self:other);` |", "PartialOrd, Eq",
          "a.partial_cmp(b) ?| NIL", "Ordering?", "PartialOrd's method is `partial_cmp`, returning Ordering?.")
trait_row("tr0249", 249, "| `Clone` | `func:clone = Self(Self:self);` |", "Clone", "a.clone() ?| b", "Pt",
          "Clone's method is `clone`, returning Self.")
trait_row("tr0250", 250, "| `Hash` | `func:hash = uint64(Self:self);` |", "Hash", "a.hash() ?| 0u64", "uint64",
          "Hash's method is `hash`, returning uint64.")
trait_row("tr0251", 251, "| `ToString` | `func:to_string = string(Self:self);` |", "ToString",
          'a.to_string() ?| string_concat("x", "y")', "string", "ToString's method is `to_string`, returning string.")
trait_row("tr0252", 252, "| `Debug` | `func:debug = string(Self:self);` |", "Debug",
          'a.debug() ?| string_concat("x", "y")', "string", "Debug's method is `debug`, returning string.")
claim("tr0254", D, 254, "`Ordering` is a prelude enum — `Less`, `Equal`, `Greater`", "rule",
      "`Ordering` is a prelude enum with Less, Equal and Greater.",
      expect="run:0",
      src=main_("""    Ordering:o = Ordering.Greater;
    int32:r = 0i32;
    pick (o) { (Ordering.Less) { r = 1i32; }, (Ordering.Equal) { r = 2i32; }, (Ordering.Greater) { r = 3i32; } }
%s
    exit 0i32;""" % chk("r == 3i32", 10)),
      wrong="refused, or 10")
claim("tr0255", D, 255, "integer**: the prototype returned `int32`", "rule",
      "An ordering is not an integer: binding one to an int32 is refused.",
      expect="refuse",
      src=main_("""    Ordering:o = Ordering.Less;
    int32:x = o;
    exit 0i32;"""),
      wrong="accepted")
claim("tr0266", D, 266, "All seven generate for a struct and for an enum", "rule",
      "All seven generate for an enum, `string` and bare `T` payloads included: `enum:Opt<T> = { Some(T); None; }`.",
      expect="compile",
      src=main_("    exit 0i32;", DERIVE7 + "\nenum:Opt<T> = { Some(T); None; };\n" + DERIVE7 +
                "\nenum:Msg = { Text(string); Code(int32); };"),
      wrong="refused (DERIVE-006 for an owning payload)")
claim("tr0280", D, 280, "**DERIVE-005** — a `simd` field under anything but `Eq`", "rule",
      "A `simd` field under Ord is refused, NITPICK-DERIVE-005.",
      expect="refuse:NITPICK-DERIVE-005",
      src=main_("    exit 0i32;", "#[derive(Ord, Eq, PartialOrd)]\nstruct:V = { simd<int32, 4>:lanes; };"),
      wrong="accepted, or refused with another code")
claim("tr0283", D, 283, "**DERIVE-006** — a member no derived body can be written for", "rule",
      "An owning builtin member (`List<int64>`) under Eq is refused, NITPICK-DERIVE-006.",
      expect="refuse:NITPICK-DERIVE-006",
      src=main_("    exit 0i32;", "#[derive(Eq)]\nstruct:H = { List<int64>:l; };"),
      wrong="accepted, or refused with another code")
claim("tr0296", D, 296, "RE-HOMED to the derive's", "rule",
      "A checker verdict inside a derive is re-homed to the declaration, naming the field: `bool` under Ord.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\n#[derive(Ord, Eq, PartialOrd)]\nstruct:Flags = { bool:lit; };\n\n" + main_(
          "    exit 0i32;") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out | cut -c1-180\n"
         "[ $rc -eq 1 ] && ! grep -q '<derived-' npkc.out && grep -m1 'NITPICK-' npkc.out | grep -q lit",
      wrong="a diagnostic in a <derived-N> file, or no field named")
claim("tr0306", D, 306, "**`Default` and `Display` were listed here and are removed (D-123).**", "rule",
      "`Display` is removed: `#[derive(Display)]` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "#[derive(Display)]\nstruct:Cfg = { int32:p; };"),
      wrong="accepted")

# ------------------------------------------------------------------ 2.6 blanket impls
BLANKET = """trait:Printable = { func:show = int32(Self:self) never fails; };
trait:Loggable = { func:log_str = string(Self:self); };
struct:P = { int32:n; };
impl:P:Printable = { func:show = int32(P:self) never fails { pass self.n; }; };"""
claim("tr0327", D, 327, "```nitpick", "example",
      "A blanket impl `impl:<T: Printable>:T:Loggable` gives every Printable type `log_str`: \"[LOG]\".",
      expect="run:0",
      src=main_("""    P:p = P{ n: 1i32 };
    string:s = p.log_str() ?| string_concat("x", "y");
%s
    exit 0i32;""" % chk('string_equals(s, "[LOG]")', 10), BLANKET + """
impl:<T: Printable>:T:Loggable = {
    func:log_str = string(T:self) { pass("[LOG]"); };
};"""),
      wrong="refused, or 10")
claim("tr0335", D, 335, "**Concrete", "rule",
      "A concrete impl takes priority over the blanket one.",
      expect="run:0",
      src=main_("""    P:p = P{ n: 1i32 };
    string:s = p.log_str() ?| string_concat("x", "y");
%s
    exit 0i32;""" % chk('string_equals(s, "concrete")', 10), BLANKET + """
impl:<T: Printable>:T:Loggable = { func:log_str = string(T:self) { pass("[LOG]"); }; };
impl:P:Loggable = { func:log_str = string(P:self) { pass string_concat("con", "crete"); }; };"""),
      wrong="refused (an overlap), or 10 (the blanket chosen)")
claim("tr0342", D, 342, "**At most one blanket impl per trait.**", "rule",
      "Two blanket impls of one trait are refused.",
      expect="refuse",
      src=main_("    exit 0i32;", BLANKET + """
trait:Other = { func:o = int32(Self:self) never fails; };
impl:<T: Printable>:T:Loggable = { func:log_str = string(T:self) { pass("[A]"); }; };
impl:<T: Other>:T:Loggable = { func:log_str = string(T:self) { pass("[B]"); }; };"""),
      wrong="accepted")
claim("tr0347", D, 347, "**A blanket impl must name a trait.**", "rule",
      "A blanket impl naming no trait (`impl:<T: Printable>:T = { … };`) is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", BLANKET + """
impl:<T: Printable>:T = { func:extra = int32(T:self) never fails { pass 1i32; }; };"""),
      wrong="accepted: methods added to types the writer does not own")
claim("tr0350", D, 350, "**A blanket impl does not apply to itself.**", "rule",
      "A blanket impl does not apply to itself: `impl:<T: Loggable>:T:Loggable` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", BLANKET + """
impl:<T: Loggable>:T:Loggable = { func:log_str = string(T:self) { pass("[L]"); }; };"""),
      wrong="accepted")
claim("tr0356", D, 356, "spells this `impl:Loggable:for:T:where:Printable = { … };`", "rule",
      "Chapter 13's `impl:Loggable:for:T:where:Printable` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", BLANKET + """
impl:Loggable:for:T:where:Printable = { func:log_str = string(T:self) { pass("[L]"); }; };"""),
      wrong="accepted")

# ------------------------------------------------------------------ 2.7 data hiding, opaque
claim("tr0364", D, 364, "Struct fields follow module visibility — private by default, exported with `pub`.", "rule",
      "A struct field is private by default: a field without `pub` is not read outside its module.",
      expect="refuse",
      src=main_("""    Acct:a = raw bank.mk();
    if (a.open != 1i64) { exit 10i32; }
    exit 0i32;""", """mod:bank = {
    pub struct:Acct = { int64:open; pub int64:shown; };
    pub func:mk = Acct() never fails { Acct:a = Acct{ open: 1i64, shown: 2i64 }; pass a; };
};
use bank.{Acct};"""),
      wrong="accepted: the field public by default")
claim("tr0368", D, 368, "it is legal **only inside an", "rule",
      "`opaque` is legal only inside an `extern` block: one at module level is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "opaque struct:DbHandle;"),
      wrong="accepted outside an extern block")
claim("tr0373", D, 373, "```nitpick", "example",
      "The storage_driver extern block (an opaque struct, db_open and db_rows) compiles.",
      expect="compile",
      src=main_("    exit 0i32;", """extern:"storage_driver" = {
    opaque struct:DbHandle;
    func:db_open = DbHandle(int8[]:path);
    func:db_rows = int64(DbHandle:h);
};"""),
      wrong="refused (EXTERN-001)")
claim("tr0384", D, 384, "```nitpick", "example",
      "An opaque value is not copied: `Handle:h2 = h;` is refused, NITPICK-OPAQUE-COPY-001.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\n" + main_("""    Handle:h  = handle_create();     // initialization from a call — fine
    Handle:h2 = h;                   // rejected — OPAQUE-COPY-001
    exit 0i32;""") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out | cut -c1-160\n"
         "[ $rc -eq 1 ] && grep -q 'OPAQUE-COPY-001' npkc.out",
      wrong="refused for another reason, or accepted")
claim("tr0392", D, 392, "The standalone `opaque:DatabaseHandle;` form previously shown here is **struck**", "rule",
      "The standalone `opaque:DatabaseHandle;` form is struck: refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "opaque:DatabaseHandle;"),
      wrong="accepted")

# ================================================================== 3. generics
claim("tr0404", D, 404, "```nitpick", "example",
      "Container<T> and `extract_value<T>`: extracting from a `Container<int32>` gives its value.",
      expect="run:0",
      src=main_("""    Container<int32>:c = Container<int32>{ value: raw v32(5i32) };
    int32:v = extract_value(c) ?| 0i32;
%s
    exit 0i32;""" % chk("v == 5i32", 10), """struct:Container<T> = {
    T:value;
};

func:extract_value<T> = T(Container<T>:c) {
    pass c.value;
};"""),
      wrong="refused: a lent T passed out (D-264), or 10")
claim("tr0419", D, 419, "```nitpick", "example",
      "Bounds with `&`: `process<T: Renderable & Serializable>` calling `item.render();` compiles.",
      expect="compile",
      src=main_("    exit 0i32;", """trait:Renderable = { func:render = NIL(Self:self) never fails; };
trait:Serializable = { func:to_id = int32(Self:self) never fails; };
func:process<T: Renderable & Serializable> = NIL(T:item) {
    item.render();
};"""),
      wrong="refused: the bare statement discards a Result (TYPE-039)")
claim("tr0425", D, 425, "places parameters **before** the name — `func<T: …>:process`", "rule",
      "Parameters before the name (`func<T>:process`) are struck: refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func<T>:process = int32(T:_~x) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0435", D, 435, "```nitpick", "example",
      "`struct:Mutex<T, comptime int32:LEVEL> = { … };` and `Mutex<Config, 2>:cfg_lock;` are the value "
      "parameter's spelling: they compile.",
      expect="compile",
      src=main_("""    Mutex<Config, 2>:cfg_lock;          // use site supplies type and value
    exit 0i32;""", """struct:Config = { int32:n; };
struct:Mutex<T, comptime int32:LEVEL> = { T:v; };"""),
      wrong="refused: `Mutex` is a builtin name, or the binding is uninitialised")
LOCK = "struct:Lock<T, comptime int32:LEVEL> = { T:v; };"
claim("tr0432", D, 432, "Parameters may carry a compile-time **value** as well as a type", "rule",
      "A struct may take a compile-time value parameter: `Lock<int64, 2>` is a type.",
      expect="compile",
      src=main_("    exit 0i32;", LOCK + "\nfunc:f = int32(Lock<int64, 2>:_~l) never fails { pass 0i32; };"),
      wrong="refused")
claim("tr0448", D, 448, "**A value argument stops below the binary operators.**", "rule",
      "A value argument stops below the binary operators: `Lock<int64, 2 > 1>` (unparenthesised) is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", LOCK + "\nfunc:f = int32(Lock<int64, 2 > 1>:_~l) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0454", D, 454, "**Only an integer literal is constant at this rung.**", "rule",
      "Only an integer literal is a constant value argument: a named constant is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", LOCK + "\nfixed int32:LV = 2i32;\nfunc:f = int32(Lock<int64, LV>:_~l) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0456", D, 456, "**An unsuffixed literal takes the parameter's declared type; a suffixed one must", "rule",
      "A suffixed value argument must already be the parameter's type: `2i64` against `comptime int32` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", LOCK + "\nfunc:f = int32(Lock<int64, 2i64>:_~l) never fails { pass 0i32; };"),
      wrong="accepted (widened)")
claim("tr0461", D, 461, "Two values are two arguments and therefore two types", "rule",
      "`Lock<T, 2>` and `Lock<T, 3>` are two types: one passed for the other is refused.",
      expect="refuse",
      src=main_("""    Lock<int64, 2>:a = Lock<int64, 2>{ v: 1i64 };
    int32:r = raw f(a);
    exit 0i32;""", LOCK + "\nfunc:f = int32(Lock<int64, 3>:_~l) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0466", D, 466, "**A bare type parameter is move-only in the body that names it (D-264,", "rule",
      "A bare `T` is move-only in a generic body: a plain copy `T:y = x;` is refused, NITPICK-TYPE-046.",
      expect="refuse:NITPICK-TYPE-046",
      src=main_("    exit 0i32;", "func:dup<T> = int32(T:x) never fails { T:y = x; discard(y); pass 0i32; };"),
      wrong="accepted (a second owner), or refused with another code")
claim("tr0483", D, 483, "**a body may not use any capability its bounds do not", "rule",
      "A generic body may not use a capability its bounds do not declare; the refusal names the declared bound.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\ntrait:Show = { func:show = int32(Self:self) never fails; };\n"
                                    "func:f<T: Show> = int32(T:x) { pass (raw x.size()); };\n\n" + main_(
          "    exit 0i32;") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -2 npkc.out | cut -c1-180\n"
         "[ $rc -eq 1 ] && grep -m1 'NITPICK-' npkc.out | grep -q Show",
      wrong="accepted (duck typing), or the refusal names no bound")
claim("tr0492", D, 492, "**A bound set is transitively closed.**", "rule",
      "A bound set is transitively closed: under `T: Ordered` (Ordered = Equatable & …) the body uses Equatable's method.",
      expect="run:0",
      src=main_("""    P:a = P{ n: raw v32(1i32) };
    P:b = P{ n: 1i32 };
%s
    exit 0i32;""" % chk("(raw both(a, b))", 10), """trait:Equatable = { func:same = bool(Self:a, Self:b) never fails; };
trait:Ordered = Equatable & { func:rank = int32(Self:self) never fails; };
struct:P = { int32:n; };
impl:P:Equatable = { func:same = bool(P:a, P:b) never fails { pass (a.n == b.n); }; };
impl:P:Ordered = { func:rank = int32(P:self) never fails { pass self.n; }; };
func:both<T: Ordered> = bool(T:a, T:b) never fails { pass (raw a.same(b)); };"""),
      wrong="refused: the supertrait's method not visible under the bound")
claim("tr0495", D, 495, "**UFCS does not reach a free function through a parameter.**", "rule",
      "UFCS does not reach a free function through a type parameter: `x.magnitude()` on a `T` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """func:magnitude<T> = int32(T:_~p) never fails { pass 1i32; };
func:g<T> = int32(T:x) never fails { pass (raw x.magnitude()); };"""),
      wrong="accepted (duck typing by omission)")
claim("tr0496", D, 496, "and `magnitude(p)` are the same call for a concrete receiver (D-006)", "rule",
      "For a concrete receiver, `p.magnitude()` and `magnitude(p)` are the same call.",
      expect="run:0",
      src=main_("""    Point:p = Point{ x: raw v32(3i32), y: 4i32 };
%s
    exit 0i32;""" % chk("(raw p.magnitude()) == 7i32 && (raw magnitude(p)) == 7i32", 10), """struct:Point = { int32:x; int32:y; };
func:magnitude = int32(Point:p) never fails { pass (p.x + p.y); };"""),
      wrong="refused, or 10")
claim("tr0501", D, 501, "**A `comptime` value parameter is not a type.**", "rule",
      "A comptime value parameter is not a type: `LEVEL:x` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", "func:f<comptime int32:LEVEL> = int32(LEVEL:x) never fails { pass 0i32; };"),
      wrong="accepted")
claim("tr0504", D, 504, "A parameter **shadows** a module-level type of the same name", "rule",
      "A type parameter shadows a module-level type of the same name: `func:f<T>` with `struct:T` declared compiles.",
      expect="compile",
      src=main_("    exit 0i32;", "struct:T = { int32:n; };\nfunc:f<T> = int32(T:_~x) never fails { pass 0i32; };"),
      wrong="refused")
claim("tr0513", D, 513, "(`Pair<T, T>` does not match `Pair<int32, int64>`)", "rule",
      "A family impl's repeated parameter binds one type: `impl:<T>:Pair<T, T>:Sum` does not apply to "
      "`Pair<int32, int64>`, so `sum` on it is refused.",
      expect="refuse",
      src=main_("""    Pair<int32, int64>:p = Pair<int32, int64>{ a: 1i32, b: 2i64 };
    int32:s = raw p.sum();
    exit 0i32;""", """trait:Sum = { func:sum = int32(Self:self) never fails; };
struct:Pair<A, B> = { A:a; B:b; };
impl:<T>:Pair<T, T>:Sum = { func:sum = int32(Pair<T, T>:self) never fails { pass 1i32; }; };"""),
      wrong="accepted: the impl applied positionally")
claim("tr0536", D, 536, "```nitpick", "example",
      "Type arguments are inferred at the call: `extract(c)` with nothing written.",
      expect="run:0",
      src=main_("""    Box<int32>:c = Box<int32>{ v: raw v32(5i32), n: 3i32 };
%s
    exit 0i32;""" % chk("(raw count(c)) == 3i32", 10), """struct:Box<T> = { T:v; int32:n; };
func:count<T> = int32(Box<T>:b) never fails { pass b.n; };"""),
      wrong="refused: inference failed")
claim("tr0543", D, 543, "```nitpick", "example",
      "Explicit type arguments in an expression are the turbofish: `count::<int32>(c)`.",
      expect="run:0",
      src=main_("""    Box<int32>:c = Box<int32>{ v: raw v32(5i32), n: 3i32 };
%s
    exit 0i32;""" % chk("(raw count::<int32>(c)) == 3i32", 10), """struct:Box<T> = { T:v; int32:n; };
func:count<T> = int32(Box<T>:b) never fails { pass b.n; };"""),
      wrong="refused")
claim("tr0549", D, 549, "| Type | bare brackets — `Handle<Node<int64>>:h;`, `struct:Container<T>` |", "row",
      "Type position takes bare brackets: `struct:Container<T>` and a `Container<Container<int64>>` parameter.",
      expect="compile",
      src=main_("    exit 0i32;", "struct:Container<T> = { T:value; };\nfunc:f = int32(Container<Container<int64>>:_~c) never fails { pass 0i32; };"),
      wrong="refused")
claim("tr0550", D, 550, "| Expression | turbofish, always — `extract_value::<int32>(c)` |", "row",
      "Expression position is the turbofish, always: `count<int32>(c)` without it is refused.",
      expect="refuse",
      src=main_("""    Box<int32>:c = Box<int32>{ v: raw v32(5i32), n: 3i32 };
    int32:v = raw count<int32>(c);
    exit 0i32;""", """struct:Box<T> = { T:v; int32:n; };
func:count<T> = int32(Box<T>:b) never fails { pass b.n; };"""),
      wrong="accepted")
claim("tr0551", D, 551, "| `#`-builtin | bare brackets — `#size_of<int32>()`", "row",
      "A `#`-builtin takes bare brackets: `#size_of<int32>()` is 4.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<int32>() == 4i64", 10)),
      wrong="refused, or 10")
claim("tr0554", D, 554, "`enum:Opt<T: Pr> = { Some(T); None; }` instantiated as `Opt<Point>`", "rule",
      "An enum instance is judged like a struct's: `Opt<Point>` with Point lacking `Pr` is refused, "
      "NITPICK-TYPE-017.",
      expect="refuse:NITPICK-TYPE-017",
      src=main_("""    Opt<Point>:o = Opt.None;
    exit 0i32;""", """trait:Pr = { func:pr = int32(Self:self) never fails; };
struct:Point = { int32:x; };
enum:Opt<T: Pr> = { Some(T); None; };"""),
      wrong="accepted, or refused with another code")
claim("tr0561", D, 561, "naming the parameter (TYPE-022)", "rule",
      "A variant constructor whose instance nothing decides is refused naming the parameter, NITPICK-TYPE-022.",
      expect="refuse:NITPICK-TYPE-022",
      src=main_("""    drop take(Opt.None);
    exit 0i32;""", """enum:Opt<T> = { Some(T); None; };
func:take<T> = NIL(Opt<T>:_~o) never fails { pass NIL; };"""),
      wrong="accepted, or refused with another code")
claim("tr0563", D, 563, "The earlier form — implicit `f<int32>(x)`", "rule",
      "The implicit `f<int32>(x)` is struck: refused.",
      expect="refuse",
      src=main_("""    int32:v = raw idt<int32>(raw v32(5i32));
    exit 0i32;""", "func:idt<T> = int32(T:_~x) never fails { pass 5i32; };"),
      wrong="accepted")
claim("tr0575", D, 575, "```nitpick", "example",
      "Nested generics close with `>>`: `Handle<Node<int64>>` is a type.",
      expect="compile",
      src=main_("    exit 0i32;", "struct:Node<T> = { T:v; };\nfunc:f = int32(Handle<Node<int64>>:_~my_handle) never fails { pass 0i32; };"),
      wrong="refused")
claim("tr0586", D, 586, "Instantiation depth is capped at **64**", "rule",
      "Instantiation depth is capped at 64: an unbounded generic recursion is a compile error, not a crash "
      "or a silent truncation.",
      expect="refuse",
      src=main_("""    int32:v = raw deep::<int32>(raw v32(1i32));
    exit 0i32;""", """struct:Box<T> = { T:v; };
func:deep<T> = int32(move T:x) never fails { Box<T>:b = Box<T>{ v: move(x) }; pass (raw deep::<Box<T>>(move(b))); };"""),
      wrong="npkc crashes, hangs or truncates")
claim("tr0589", D, 589, "**mangled names are readable and", "rule",
      "Instantiations' names are readable, no hash: `idt` at `int32` is named by both.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\nfunc:idt<T> = int32(T:_~x) never fails { pass 5i32; };\n\n" + main_(
          "    int32:v = raw idt::<int32>(1i32);\n    if (v != 5i32) { exit 10i32; }\n    exit 0i32;") + "\n" +
          failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1 || exit 3\n"
         "grep -o '@\"npk\\.r\\.idt[^\"]*\"' r.ll | sort -u | head -2\ngrep -q '@\"npk\\.r\\.idt[^\"]*int32[^\"]*\"' r.ll",
      wrong="a hashed name")
claim("tr0593", D, 593, "There is **no specialization**", "rule",
      "No specialization: an impl for `Box<int32>` beside the family `impl:<T>:Box<T>` is refused.",
      expect="refuse",
      src=main_("    exit 0i32;", """trait:S = { func:s = int32(Self:self) never fails; };
struct:Box<T> = { T:v; };
impl:<T>:Box<T>:S = { func:s = int32(Box<T>:self) never fails { pass 1i32; }; };
impl:Box<int32>:S = { func:s = int32(Box<int32>:self) never fails { pass 2i32; }; };"""),
      wrong="accepted: the instance specialised")
claim("tr0602", D, 602, "```nitpick", "example",
      "An `arena<Node<T>>` field in a generic struct, with chained access: `hdr.node_arena.alloc(my_node)`.",
      expect="compile",
      src=main_("""    Header<int64>:hdr;
    Node<int64>:my_node = Node<int64>{ v: 1i64 };
    Handle<Node<int64>>:h1 = hdr.node_arena.alloc(my_node);
    exit 0i32;""", "struct:Node<T> = { T:v; };\nstruct:Header<T> = {\n    arena<Node<T>>:node_arena;\n};"),
      wrong="refused: the example does not compile as written")

# ================================================================== 4. coherence and object safety
claim("tr0622", D, 622, "There is **at most one implementation** of a given trait for a given type.", "rule",
      "Two impls of one trait for one type are refused, reported at the SECOND impl.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\ntrait:S = { func:s = int32(Self:self) never fails; };\nstruct:P = { int32:n; };\n"
                                    "impl:P:S = { func:s = int32(P:self) never fails { pass 1i32; }; };\n"
                                    "impl:P:S = { func:s = int32(P:self) never fails { pass 2i32; }; };\n\n" + main_(
          "    exit 0i32;") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -3 npkc.out | cut -c1-160\n"
         "[ $rc -eq 1 ] && grep -m1 '^NITPICK-' npkc.out | grep -q 'r.npk:6:'",
      wrong="accepted, or reported at the first impl")


def overlap(cid, line, quote, impls, text, expect="refuse"):
    claim(cid, D, line, quote, "row", text, expect=expect,
          src=main_("    exit 0i32;", """trait:S = { func:s = int32(Self:self) never fails; };
trait:S2 = { func:s2 = int32(Self:self) never fails; };
trait:Bnd = { func:bnd = int32(Self:self) never fails; };
struct:Item = { int32:n; };
struct:Box<T> = { T:v; };
impl:Item:Bnd = { func:bnd = int32(Item:self) never fails { pass 0i32; }; };
""" + impls),
          wrong="accepted" if expect == "refuse" else "refused")


overlap("tr0633", 633, "| `impl:Item:T` twice | overlap — the plain case |",
        "impl:Item:S = { func:s = int32(Item:self) never fails { pass 1i32; }; };\n"
        "impl:Item:S = { func:s = int32(Item:self) never fails { pass 2i32; }; };",
        "The same impl twice is an overlap: refused.")
overlap("tr0634", 634, "| `impl:<T>:Box<T>:S` and `impl:Box<int32>:S` | **overlap**",
        "impl:<T>:Box<T>:S = { func:s = int32(Box<T>:self) never fails { pass 1i32; }; };\n"
        "impl:Box<int32>:S = { func:s = int32(Box<int32>:self) never fails { pass 2i32; }; };",
        "A family impl and an instance's are an overlap: refused.")
overlap("tr0635", 635, "| `impl:<T>:Box<T>:S` and `impl:<U>:Box<U>:S` | **overlap**",
        "impl:<T>:Box<T>:S = { func:s = int32(Box<T>:self) never fails { pass 1i32; }; };\n"
        "impl:<U>:Box<U>:S = { func:s = int32(Box<U>:self) never fails { pass 2i32; }; };",
        "Two family impls over one declaration are an overlap: refused.")
overlap("tr0636", 636, "| two blanket impls of one trait | overlap (§2.6, D-111) |",
        "impl:<T: Bnd>:T:S = { func:s = int32(T:self) never fails { pass 1i32; }; };\n"
        "impl:<T: S2>:T:S = { func:s = int32(T:self) never fails { pass 2i32; }; };",
        "Two blanket impls of one trait are an overlap: refused.")
overlap("tr0637", 637, "| a blanket impl and a concrete one | **not** an overlap (§2.6)",
        "impl:<T: Bnd>:T:S = { func:s = int32(T:self) never fails { pass 1i32; }; };\n"
        "impl:Item:S = { func:s = int32(Item:self) never fails { pass 2i32; }; };",
        "A blanket impl and a concrete one are not an overlap: compiles.", expect="compile")
overlap("tr0638", 638, "| impls of *different* traits on one type | not an overlap",
        "impl:Item:S = { func:s = int32(Item:self) never fails { pass 1i32; }; };\n"
        "impl:Item:S2 = { func:s2 = int32(Item:self) never fails { pass 2i32; }; };",
        "Impls of different traits on one type are not an overlap: compiles.", expect="compile")
claim("tr0653", D, 653, "**Every overlap report carries a NOTE at the earlier impl**", "rule",
      "An overlap report carries a note at the earlier impl.",
      expect="sh:0",
      sh="cat > r.npk <<'EOF'\n" + ("mod:r;\n\ntrait:S = { func:s = int32(Self:self) never fails; };\nstruct:P = { int32:n; };\n"
                                    "impl:P:S = { func:s = int32(P:self) never fails { pass 1i32; }; };\n"
                                    "impl:P:S = { func:s = int32(P:self) never fails { pass 2i32; }; };\n\n" + main_(
          "    exit 0i32;") + "\n" + failsafe_text("")).rstrip() +
         "\nEOF\n\"$NPKC\" r.npk -o r.ll > npkc.out 2>&1; rc=$?\nhead -3 npkc.out | cut -c1-160\n"
         "[ $rc -eq 1 ] && grep -q '^note NITPICK-[A-Z]*-[0-9]* r.npk:5:' npkc.out",
      wrong="no note at the earlier impl")

# ------------------------------------------------------------------ 4.2 object safety
DYNUSE = "    S:s = S{ n: 1i32 };\n    dyn Bad:d = move(s);\n    exit 0i32;"
def unsafe(cid, line, quote, trait, impl, text):
    claim(cid, D, line, quote, "rule", text, expect="refuse",
          src=main_(DYNUSE, "struct:S = { int32:n; };\n" + trait + "\n" + impl),
          wrong="accepted: a trait object over a trait that is not object-safe")


unsafe("tr0677", 677, "every method takes a `self` parameter — no static methods",
       "trait:Bad = { func:make = int32(int32:x) never fails; };",
       "impl:S:Bad = { func:make = int32(int32:x) never fails { pass x; }; };",
       "A trait with a static method (no `self`) is not object-safe: `dyn Bad` is refused.")
unsafe("tr0678", 678, "**`Self` appears nowhere but the receiver**",
       "trait:Bad = { func:dup = Self(Self:self); };",
       "impl:S:Bad = { func:dup = S(S:self) { pass S{ n: self.n }; }; };",
       "A trait whose method returns `Self` is not object-safe: `dyn Bad` is refused.")
unsafe("tr0686", 686, "**no generic methods**",
       "trait:Bad = { func:g<T> = int32(Self:self, T:_~x) never fails; };",
       "impl:S:Bad = { func:g<T> = int32(S:self, T:_~x) never fails { pass 1i32; }; };",
       "A trait with a generic method is not object-safe: `dyn Bad` is refused.")
unsafe("tr0688", 688, "**an `async` method requires a `Self->` receiver**",
       "trait:Bad = { async func:a = int32(Self:self); };",
       "impl:S:Bad = { async func:a = int32(S:self) { pass self.n; }; };",
       "An async method with a by-value `Self` receiver disqualifies: `dyn Bad` is refused.")
unsafe("tr0696", 696, "A method whose signature mentions an **associated type** also disqualifies",
       "trait:Bad = { assoc:Item; func:get = Item(Self:self); };",
       "impl:S:Bad = { assoc:Item = int32; func:get = int32(S:self) { pass self.n; }; };",
       "A method mentioning an associated type disqualifies: `dyn Bad` is refused.")
claim("tr0682", D, 682, "**The receiver itself may be `Self` or `Self->`**", "rule",
      "A `Self->` receiver keeps a trait object-safe: `dyn Good` over one compiles.",
      expect="compile",
      src=main_("""    S:s = S{ n: 1i32 };
    dyn Good:d = move(s);
    discard(d);
    exit 0i32;""", """struct:S = { int32:n; };
trait:Good = { func:peek = int32(Self->:self) never fails; };
impl:S:Good = { func:peek = int32(S->:self) never fails { pass self.n; }; };"""),
      wrong="refused")

# ================================================================== 5. dispatch
claim("tr0713", D, 713, "**A bare trait is not a value type**", "rule",
      "A bare trait is not a value type: `Speaks:x` as a parameter is refused, NITPICK-TYPE-002.",
      expect="refuse:NITPICK-TYPE-002",
      src=main_("    exit 0i32;", SPEAKS + "\nfunc:f = int32(Speaks:x) never fails { pass 0i32; };"),
      wrong="accepted, or refused with another code")
claim("tr0721", D, 721, "(`{ data_ptr, vtable_ptr }`, 16 bytes on 64-bit", "rule",
      "A single-bound `dyn` is a fat pointer of 16 bytes.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<dyn Speaks>() == 16i64", 10), SPEAKS),
      wrong="another size")
claim("tr0724", D, 724, "supertrait methods are not reachable", "rule",
      "Through `dyn Sub`, a supertrait's method is not reachable: calling it is refused.",
      expect="refuse",
      src=main_("""    S:s = S{ n: 1i32 };
    dyn Sub:d = move(s);
    int32:v = raw d.base();
    exit 0i32;""", """trait:Base = { func:base = int32(Self:self) never fails; };
trait:Sub = Base & { func:sub = int32(Self:self) never fails; };
struct:S = { int32:n; };
impl:S:Base = { func:base = int32(S:self) never fails { pass 1i32; }; };
impl:S:Sub = { func:sub = int32(S:self) never fails { pass 2i32; }; };"""),
      wrong="accepted: the supertrait reached through the vtable")
claim("tr0730", D, 730, "```nitpick", "example",
      "`dyn Serializable:obj = msg;` builds a trait object, and the method dispatches through it.",
      expect="run:0",
      src=main_("""    Message:msg = Message{ id: 1i32 };
    dyn Serializable:obj = msg;
%s
    exit 0i32;""" % chk("(raw obj.code()) == 1i32", 10), """trait:Serializable = { func:code = int32(Self:self) never fails; };
struct:Message = { int32:id; };
impl:Message:Serializable = { func:code = int32(Message:self) never fails { pass self.id; }; };"""),
      wrong="refused, or 10")
claim("tr0737", D, 737, "```nitpick", "example",
      "`dyn Drawable & Serializable:obj = msg;` builds a multi-bound trait object.",
      expect="run:0",
      src=main_("""    Message:msg = Message{ id: 2i32 };
    dyn Drawable & Serializable:obj = msg;
%s
    exit 0i32;""" % chk("(raw obj.draw()) + (raw obj.code()) == 7i32", 10), """trait:Drawable = { func:draw = int32(Self:self) never fails; };
trait:Serializable = { func:code = int32(Self:self) never fails; };
struct:Message = { int32:id; };
impl:Message:Drawable = { func:draw = int32(Message:self) never fails { pass 5i32; }; };
impl:Message:Serializable = { func:code = int32(Message:self) never fails { pass self.id; }; };"""),
      wrong="refused, or 10")
claim("tr0741", D, 741, "`dyn A & B` is assignable to `dyn A` — widening by dropping bounds", "rule",
      "`dyn A & B` widens to `dyn A`: the widened object still dispatches `a`.",
      expect="run:0",
      src=main_("""    S:s = S{ n: 1i32 };
    dyn A & B:both = move(s);
    dyn A:one = move(both);
%s
    exit 0i32;""" % chk("(raw one.a()) == 1i32", 10), two_traits()),
      wrong="refused, or 10")
claim("tr0743", D, 743, "`{ data, vt_1 … vt_N }` — (N+1)×8 bytes", "rule",
      "`dyn` over N traits is (N+1)×8 bytes: `dyn A & B` is 24.",
      expect="run:0",
      src=main_("""%s
    exit 0i32;""" % chk("#size_of<dyn A & B>() == 24i64", 10), two_traits()),
      wrong="another size")
claim("tr0748", D, 748, "Chapter 13 uses `+` here while using `&` for supertraits and bounds", "rule",
      "`+` is not the bound combinator: `dyn A + B` is refused.",
      expect="refuse",
      src=main_("""    S:s = S{ n: 1i32 };
    dyn A + B:d = move(s);
    exit 0i32;""", two_traits()),
      wrong="accepted")
claim("tr0751", D, 751, "**`dyn` obscures the control-flow graph**", "rule",
      "`dyn` raises warnings under strict auditing profiles.",
      untestable="[vague] no profile is named whose warning a program could check")

# ================================================================== 6. other documents
claim("tr0760", D, 760, "`@cast<T>` and", "rule",
      "`@cast<T>` is removed: refused.",
      expect="refuse",
      src=main_("""    int64:a = raw v64(5i64);
    int32:b = @cast<int32>(a);
    exit 0i32;"""),
      wrong="accepted")
claim("tr0762", D, 762, "Integer-to-pointer casting is illegal outside", "rule",
      "Integer-to-pointer casting is illegal outside `#wild_ptr<T>(addr)` in wild context: `5i64 =>! int32->` is refused.",
      expect="refuse",
      src=main_("""    int32->:p = raw v64(4096i64) =>! int32->;
    exit 0i32;"""),
      wrong="accepted")
claim("tr0764", D, 764, "Lambdas without capture", "rule",
      "Lambdas without capture remain as function values: one bound to a function-typed local compiles.",
      expect="compile",
      src=main_("""    func int32(int32) never fails:f = func int32(int32:x) never fails { pass x; };
    discard(raw f(1i32));
    exit 0i32;"""),
      wrong="refused: no lambda expression (AST:476)")

# ================================================================== after run 1 (S45, S53)
# The programs' own mistakes; every expectation above is unchanged.
WHY_LIT = ("a generic struct literal takes no type arguments (the binding's annotation gives them, as the "
           "compiler's own programs write `Box<int32>:a = Box{ v: 5i32 };`): `Name<…>{` was PARSE-002")
for _cid, _pairs in (
        ("tr0146", [("Cell<int64>{", "Cell{")]),
        ("tr0196", [("Box<Point>{", "Box{")]),
        ("tr0198", [("Box<Point>{", "Box{")]),
        ("tr0404", [("Container<int32>{", "Container{")]),
        ("tr0536", [("Box<int32>{", "Box{")]),
        ("tr0543", [("Box<int32>{", "Box{")]),
        ("tr0602", [("Node<int64>{", "Node{")]),
        ("tr0461", [("Lock<int64, 2>{", "Lock{")]),
        ("tr0513", [("Pair<int32, int64>{", "Pair{")]),
        ("tr0586", [("Box<T>{", "Box{")])):
    refix(_cid, WHY_LIT + (" (it had agreed in run 1 for that reason, S55)" if _cid in ("tr0461", "tr0513", "tr0586") else ""),
          _pairs)
refix("tr0364", "`pub` on a struct field does not parse (PARSE-001), and run 2 agreed for that reason (S55); the "
      "struct now has only the plain field the claim reads outside its module",
      [("    pub struct:Acct = { int64:open; pub int64:shown; };", "    pub struct:Acct = { int64:open; int64:kept; };"),
       ("Acct{ open: 1i64, shown: 2i64 }", "Acct{ open: 1i64, kept: 2i64 }")])
refix("tr0686", "the impl's generic method was refused for its signature (TYPE-014), not the trait for `dyn` (S55); "
      "the trait is now used as `dyn Bad` in a parameter, with no impl",
      [("impl:S:Bad = { func:g<T> = int32(S:self, T:_~x) never fails { pass 1i32; }; };",
        "func:takes = int32(dyn Bad:_~d) never fails { pass 0i32; };"),
       ("    dyn Bad:d = move(s);\n", "")])
