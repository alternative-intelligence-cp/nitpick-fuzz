"""M11 claims: MEMORY_REFERENCE.md (lines 1-533) at HUNT2 (9126350), extracted by session 8.

Every expectation below is written from the reference's text before any of these
programs ran (PROGRESS.md S36). Spellings around a claim are ones that compile at
HUNT2 (M10's programs, the other claim modules, the compiler's tests/backend/programs);
the construct a claim is about is spelled as the reference spells it.

The `heap=` claims read the runtime's `heap: allocated= peak_live= count=` line, whose
figures are the REQUESTED bytes (BUILTIN's 1 000 x alloc(1000) reads 1000000/1000/1000).
A `List<int64>` of capacity c is one managed block of exactly 8c bytes (the prelude's
`list_init`: `alloc_managed(n * #size_of<T>())`, n = max(c, 1)), and a `List<T>` value is
24 bytes ({ items, count, cap }). Those are the only sizes the expectations assume.
"""
from m11lib import *

covers("MEMORY", 1)

D = "MEMORY"


def lst(cap, t="int64"):
    """a fresh List<t> of capacity `cap` (a never-fails call, so `raw`)"""
    return "raw list_init::<%s>(%di64)" % (t, cap)


def fs_except(omit, first=""):
    """a whole failsafe naming every identity but `omit`, `first` arms before them"""
    arms = [first.rstrip()] if first.strip() else []
    named = set(re.findall(r"\((\w+)\)\s*\{", first))
    arms += ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS if n != omit and n not in named]
    arms.append("        (*) { exit 99i32; }")
    return ("func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) +
            "\n    }\n    exit 9i32;\n};\n")


# ================================================================== the header (1-8)
claim("me0005", D, 5, "**There is no garbage collector** (D-003)", "rule",
      "There is no garbage collector: lifetimes are static.",
      untestable="[vague] a design statement with no outcome of its own; the static lifetimes it names "
                 "are claimed and tested at me0022 (scope), me0362 (handles) and me0119 (wild)")
claim("me0007", D, 7, "Nothing relocates memory", "rule",
      "Nothing relocates memory implicitly, and there are no collection pauses.",
      untestable="[unobservable] a program sees no address to compare and no pause to time")

# ================================================================== 1.1 managed memory
claim("me0016", D, 16, "a bare `T` is treated as owning", "rule",
      "In a generic body a bare T is owning: a copy of a T place is refused (TYPE-046), even when "
      "the only instantiation is int32.",
      expect="refuse:TYPE-046",
      src=main_("""    int32:r = raw dup::<int32>(5i32);
    exit r - 5i32;""", """func:dup<T> = int32(move T:x) never fails {
    T:y = x;
    pass 0i32;
};"""),
      wrong="accepted: the body checked per instantiation, where int32 copies")
claim("me0018", D, 18, "unless spelled `move(...)` or `.clone()`", "rule",
      "The permitted twin: in a generic body `move(x)` of a T place is accepted, and at int32 the "
      "value arrives.",
      expect="run:0",
      src=main_("""    int32:r = raw keep::<int32>(5i32);
    if (r != 5i32) { exit 10i32; }
    exit 0i32;""", """func:keep<T> = T(move T:x) never fails {
    T:y = move(x);
    pass y;
};"""),
      wrong="refused, or 10")
claim("me0019", D, 19, "`pick` binds a `T` payload as a VIEW in place", "rule",
      "A lending pick binds a T payload as a view in place (D-266) and a consuming one moves it.",
      untestable="[internal] whether a T payload binds as a view or a move inside a generic body shows "
                 "only through the loan rules' refusals; the grid's F-002 and DEF-104 cells measure those")
claim("me0020", D, 20, "The `move` of a scalar is its copy", "rule",
      "The move of a scalar is its copy: a generic function moving its T at int64 hands the value "
      "back, and the caller's own copy is still the same value.",
      expect="run:0",
      src=main_("""    int64:a = raw v64(9i64);
    int64:b = raw keep::<int64>(a);
    if (b != 9i64) { exit 10i32; }
    if (a != 9i64) { exit 11i32; }
    exit 0i32;""", """func:keep<T> = T(move T:x) never fails {
    T:y = move(x);
    pass y;
};"""),
      wrong="refused, or 10/11")
claim("me0022", D, 22, "a value's last textual use does not shorten its life", "rule",
      "A managed binding is dropped when its scope exits and at no earlier point: two lists in one "
      "block, the first last used before the second exists, are both live at once.",
      expect="run:0", heap="24000/24000/2",
      src=main_("""    {
        List<int64>:a = %s;
        int64:ca = a.cap;
        List<int64>:b = %s;
        int64:cb = b.cap;
        if (ca + cb != 3000i64) { exit 10i32; }
    }
    exit 0i32;""" % (lst(1000), lst(2000))),
      wrong="peak 16000: the first list dropped at its last use (NLL)")
claim("me0022b", D, 22, "after the scope's joins and `defer`s", "rule",
      "A binding is dropped after its scope's defers: a defer reading the string at the scope's "
      "exit sees it intact.",
      expect="run:0",
      src=main_("""    int32:seen = raw v32(0i32);
    {
        string:s = string_concat("abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "c");
        defer { seen = string_bytes(s)[0i64] => int32; }
    }
    if (seen == 170i32) { exit 70i32; }
    if (seen != 97i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="70: the defer read the freed string (the drop ran first); 10: anything else")
claim("me0022c", D, 22, "before its channel reclaims", "rule",
      "A scope's drops run before its channel reclaims.",
      untestable="[unobservable] a channel's reclaim is not built (CONCURRENCY:489-490), so no order "
                 "between it and a drop can be seen")
claim("me0023", D, 23, "```nitpick", "example",
      "`int32:x = 42i32;` is a managed binding that holds 42.",
      expect="run:0",
      src=main_("""    int32:x = 42i32;           // Automatically managed on stack
    if (x != 42i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")

# ------------------------------------------------------------------ 1.1a temporaries
claim("me0031", D, 31, "dropped **when its statement ends**", "rule",
      "A temporary is dropped when its statement ends: two statements each reading a field of a "
      "list nobody keeps peak at the larger list alone.",
      expect="run:0", heap="24000/16000/2",
      src=main_("""    int64:c1 = (%s).cap;
    int64:c2 = (%s).cap;
    if (c1 + c2 != 3000i64) { exit 10i32; }
    exit 0i32;""" % (lst(1000), lst(2000))),
      wrong="peak 24000: the first temporary lived past its statement")
claim("me0035", D, 35, "The same drop runs on every path out of the statement", "rule",
      "The temporary's drop runs on every path out of its statement, a `relay` included: three "
      "calls whose statement relays a failure after building a list peak at one list.",
      expect="run:0", heap="24000/8000/3",
      src=main_("""    int64:r1 = f() ?| 0i64;
    int64:r2 = f() ?| 0i64;
    int64:r3 = f() ?| 0i64;
    if (r1 + r2 + r3 != 0i64) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:g = int64() { fail E1; };
func:f = int64() {
    int64:c = (%s).cap + (relay g());
    pass c;
};""" % lst(1000)),
      wrong="peak 24000: the relay path skipped the temporary's drop")
claim("me0037", D, 37, "condition dies with the condition", "rule",
      "A temporary that feeds a loop's condition dies with the condition: four evaluations of a "
      "while's condition, each building a list, peak at one list.",
      expect="run:0", heap="32000/8000/4",
      src=main_("""    int64:i = 0i64;
    while ((%s).cap > i * 400i64) decreases 3i64 - i { i = i + 1i64; }
    if (i != 3i64) { exit 10i32; }
    exit 0i32;""" % lst(1000)),
      wrong="peak above 8000: a condition's temporary outlived the condition")
claim("me0037b", D, 37, "Under `await` the temporaries", "rule",
      "Under await the temporaries of the awaiting statement live in the frame.",
      untestable="[internal] where a temporary is stored across a suspension is the lowering's; no "
                 "program sees a frame slot")
claim("me0039", D, 39, "`tests/backend/programs/temp_*.npk`", "rule",
      "The compiler's temp_*.npk programs and the cost stage's temporaries probe pin the rule.",
      untestable="[tree] a statement about the compiler repository's tests and harness")

# ------------------------------------------------------------------ 1.1b List<T>
claim("me0045", D, 45, "**Its buffer is managed storage (D-263, 1.5.2e).**", "rule",
      "A List's buffer is managed storage: a List alive in main at `exit 0` is not a leak the exit "
      "check reports.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    if (l.count != 1i64) { exit 10i32; }
    exit 0i32;""" % lst(4)),
      wrong="96 (WildLeak): the buffer counted as a wild block")
claim("me0052", D, 52, "`alloc_managed` is the PRELUDE's own (TYPE-054 elsewhere)", "rule",
      "alloc_managed is the prelude's own: a program calling it is refused, TYPE-054.",
      expect="refuse:TYPE-054",
      src=main_("""    wild int8->:p = alloc_managed(16i64);
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted")
claim("me0053", D, 53, "hand-written `wild` container relies on D-151's count", "rule",
      "A wild block unpaired at a successful exit is counted: the exit check traps WildLeak.",
      expect="trap:WildLeak",
      src=main_("""    wild int8->:p = alloc(16i64);
    exit 0i32;"""),
      wrong="0: the unpaired block not counted")
claim("me0057", D, 57, "its generated drop releases the", "rule",
      "A List's generated drop releases its elements through T's drop and hands the block back: a "
      "List of two lists dropped at its block's end leaves room, so a later list peaks alone.",
      expect="run:0", heap="48048/32000/4",
      src=main_("""    {
        List<List<int64>>:outer = %s;
        drop list_push(@outer, %s);
        drop list_push(@outer, %s);
        if (outer.count != 2i64) { exit 10i32; }
    }
    List<int64>:after = %s;
    if (after.cap != 4000i64) { exit 11i32; }
    exit 0i32;""" % (lst(2, "List<int64>"), lst(1000), lst(1000), lst(4000))),
      wrong="peak 48000 or 48048: the elements (or the whole list) were not released")
claim("me0059", D, 59, "vacant List (`cap == 0`, D-225) owns nothing", "rule",
      "A vacant List owns nothing: a list moved out of drops nothing at its scope's end (no double free).",
      expect="run:0",
      src=main_("""    {
        List<int64>:a = %s;
        drop list_push(@a, 1i64);
        List<int64>:b = move(a);
        if (b.count != 1i64) { exit 10i32; }
    }
    exit 0i32;""" % lst(4)),
      wrong="95: the vacant list's drop freed the block again")
claim("me0061", D, 61, "never copy it binding to binding", "rule",
      "List is move-only: copying a List binding to another is refused, TYPE-046.",
      expect="refuse:TYPE-046",
      src=main_("""    List<int64>:a = %s;
    List<int64>:b = a;
    exit 0i32;""" % lst(4)),
      wrong="accepted: two owners of one buffer")
claim("me0061b", D, 61, "with a `move T:p` parameter", "rule",
      "A List is consumed by a `move T:p` parameter.",
      expect="run:0",
      src=main_("""    List<int64>:a = %s;
    drop list_push(@a, 4i64);
    int64:n = raw take(move(a));
    if (n != 1i64) { exit 10i32; }
    exit 0i32;""" % lst(4), """func:take = int64(move List<int64>:p) never fails { pass p.count; };"""),
      wrong="refused or 10")
claim("me0061c", D, 61, "It is declared", "rule",
      "List and its functions are declared in the prelude.",
      untestable="[tree] where the declaration is written; that List needs no import is the premise "
                 "of every List claim here")
claim("me0068", D, 68, "`items` is not touched (TYPE-080)", "rule",
      "Outside the prelude a List's `items` is not touched: reading it is refused, TYPE-080.",
      expect="refuse:TYPE-080",
      src=main_("""    List<int64>:l = %s;
    wild int64->:p = l.items;
    exit 0i32;""" % lst(4)),
      wrong="accepted")
claim("me0068b", D, 68, "and `count` and `cap` are read but", "rule",
      "Outside the prelude a List's `cap` is not written: assigning it is refused, TYPE-079.",
      expect="refuse:TYPE-079",
      src=main_("""    List<int64>:l = %s;
    l.cap = 100i64;
    exit 0i32;""" % lst(4)),
      wrong="accepted (DEF-73's scribble)")
claim("me0068c", D, 68, "`count` and `cap` are read but", "rule",
      "count and cap are read outside the prelude.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    if (l.count != 1i64) { exit 10i32; }
    if (l.cap != 4i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, or 10/11")
claim("me0074", D, 74, "bounds-checked against `count`", "rule",
      "`l[i]` is bounds-checked against count, not cap: index 1 of a cap-4 list holding one element "
      "traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 5i64);
    int64:v = l[raw v64(1i64)];
    exit 10i32;""" % lst(4)),
      wrong="10: read past count, inside cap")
claim("me0075", D, 75, "read it, write it, compound it", "rule",
      "`l[i]` is a place: written, then compounded, it reads the result.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 5i64);
    l[0i64] = 9i64;
    l[0i64] += 2i64;
    if (l[0i64] != 11i64) { exit 10i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused or 10")
claim("me0077", D, 77, "owning element drops the old value", "rule",
      "Assigning over an owning element drops the old value: a list of lists whose element is "
      "replaced, then a larger list, peak without the old element.",
      expect="run:0", heap="32024/24024/4",
      src=main_("""    List<List<int64>>:outer = %s;
    drop list_push(@outer, %s);
    outer[0i64] = %s;
    List<int64>:after = %s;
    if (outer[0i64].cap + after.cap != 3000i64) { exit 10i32; }
    exit 0i32;""" % (lst(1, "List<int64>"), lst(1000), lst(1000), lst(2000))),
      wrong="peak 32024: the old element was never dropped")
claim("me0078", D, 78, "element is live or vacant after a move", "rule",
      "An element moved out is vacant, never unowned: the list's drop does not free it again.",
      expect="run:0",
      src=main_("""    {
        List<List<int64>>:l = %s;
        drop list_push(@l, %s);
        List<int64>:x = move(l[0i64]);
        if (x.cap != 10i64) { exit 10i32; }
    }
    exit 0i32;""" % (lst(1, "List<int64>"), lst(10))),
      wrong="95: freed twice, by x's drop and the list's")
claim("me0079", D, 79, "is a checked `T[]` view of elements", "rule",
      "`l[lo...hi]` is a T[] view of elements lo to hi-1.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    drop list_push(@l, 4i64);
    int64[]:v = l[1i64...3i64];
    if (v.len != 2i64) { exit 10i32; }
    if (v[0i64] + v[1i64] != 6i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, or 10/11")
claim("me0080", D, 80, "list (D-249)", "rule",
      "A range view borrows the list: list_push while the view lives is refused, BORROW-015.",
      expect="refuse:BORROW-015",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    int64[]:v = l[0i64...2i64];
    drop list_push(@l, 3i64);
    if (v[0i64] != 1i64) { exit 10i32; }
    exit 0i32;""" % lst(4)),
      wrong="accepted: the push may move the block under the view")
claim("me0081", D, 81, "A list behind a pointer is `(<-p)[i]`", "rule",
      "A list behind a pointer is indexed as `(<-p)[i]`.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 7i64);
    List<int64>->:p = @l;
    if ((<-p)[0i64] != 7i64) { exit 10i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused or 10")
claim("me0081b", D, 81, "`p[i]` on a pointer to an array", "rule",
      "`p[i]` on a pointer to a List is refused, TYPE-082.",
      expect="refuse:TYPE-082",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 7i64);
    List<int64>->:p = @l;
    int64:x = p[0i64];
    exit 0i32;""" % lst(4)),
      wrong="accepted: pointer arithmetic by another name")
claim("me0085", D, 85, "`list_push`, `list_reserve`", "rule",
      "list_push appends and list_reserve makes room for `need` more elements beyond the count.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    drop list_push(@l, 3i64);
    if (l.count != 3i64) { exit 10i32; }
    drop list_reserve(@l, 100i64);
    if (l.cap < 103i64) { exit 11i32; }
    if (l[2i64] != 3i64) { exit 12i32; }
    exit 0i32;""" % lst(1)),
      wrong="refused, or 10-12")
claim("me0086", D, 86, "`list_pop` (the last element, moved out)", "rule",
      "list_pop moves the last element out.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    int64:v = raw list_pop(@l);
    if (v != 2i64) { exit 10i32; }
    if (l.count != 1i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, or 10 (not the last), 11")
claim("me0087", D, 87, "`list_truncate(l, n)` (drops `n…count−1`)", "rule",
      "list_truncate(l, n) keeps elements 0 to n-1.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    drop list_push(@l, 3i64);
    drop list_truncate(@l, 1i64);
    if (l.count != 1i64) { exit 10i32; }
    if (l[0i64] != 1i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, or 10/11")
claim("me0088", D, 88, "`list_clear`", "rule",
      "list_clear empties the list.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_clear(@l);
    if (l.count != 0i64) { exit 10i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused or 10")
claim("me0089", D, 89, "`list_insert(l, i, v)` (`i` in `[0, count]`)", "rule",
      "list_insert(l, i, v) inserts at i for i in [0, count]: at 0 it shifts, at count it appends.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 2i64);
    drop list_insert(@l, 0i64, 1i64);
    drop list_insert(@l, 2i64, 3i64);
    if (l.count != 3i64) { exit 10i32; }
    if (l[0i64] != 1i64 || l[1i64] != 2i64 || l[2i64] != 3i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, or 10/11")
claim("me0090", D, 90, "`list_remove(l, i)` (order kept)", "rule",
      "list_remove(l, i) removes element i and keeps the order of the rest.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    drop list_push(@l, 3i64);
    int64:x = raw list_remove(@l, 0i64);
    if (x != 1i64) { exit 10i32; }
    if (l[0i64] != 2i64 || l[1i64] != 3i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, 10, or 11 (the order not kept)")
claim("me0091", D, 91, "`list_swap_remove(l, i)` (the last element moved into the hole)", "rule",
      "list_swap_remove(l, i) moves the last element into the hole.",
      expect="run:0",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_push(@l, 2i64);
    drop list_push(@l, 3i64);
    int64:x = raw list_swap_remove(@l, 0i64);
    if (x != 1i64) { exit 10i32; }
    if (l[0i64] != 3i64 || l[1i64] != 2i64) { exit 11i32; }
    exit 0i32;""" % lst(4)),
      wrong="refused, 10, or 11 (not the last element in the hole)")
claim("me0093", D, 93, "An index outside the list is `OutOfBounds`, whatever spells it", "rule",
      "An index outside the list is OutOfBounds whatever spells it: list_insert at count + 1 traps.",
      expect="trap:OutOfBounds",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    drop list_insert(@l, raw v64(2i64), 9i64);
    exit 10i32;""" % lst(4)),
      wrong="10: the insert went past count")
claim("me0093b", D, 93, "whatever spells it", "rule",
      "list_remove at count traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    List<int64>:l = %s;
    drop list_push(@l, 1i64);
    int64:x = raw list_remove(@l, raw v64(1i64));
    exit 10i32;""" % lst(4)),
      wrong="10")

# ------------------------------------------------------------------ 1.1c pass and move
claim("me0099", D, 99, "`pass` moves the returned value out implicitly", "rule",
      "`pass h.name` moves the field out and the root stops owning it: h's drop does not free it, "
      "and the caller reads it intact.",
      expect="run:0",
      src=main_("""    string:s = raw mk();
    uint8:b = string_bytes(s)[0i64];
    if (b == 170u8) { exit 70i32; }
    if (b != 97u8) { exit 10i32; }
    exit 0i32;""", """struct:H = { string:name; int64:n; };
func:mk = string() never fails {
    H:h = H{ name: string_concat("abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "c"), n: 1i64 };
    pass h.name;
};"""),
      wrong="70: h's drop freed the name passed out (or 95 at a second free)")
claim("me0101", D, 101, "**A value whose type does", "rule",
      "A value whose type does not drop transfers nothing: `pass g.n` copies the number and g's drop "
      "still frees its owning sibling, so three calls peak at one list.",
      expect="run:0", heap="24000/8000/3",
      src=main_("""    int64:t = raw getn() + raw getn() + raw getn();
    if (t != 21i64) { exit 10i32; }
    exit 0i32;""", """struct:G = { List<int64>:l; int64:n; };
func:getn = int64() never fails {
    G:g = G{ l: %s, n: 7i64 };
    pass g.n;
};""" % lst(1000)),
      wrong="peak 24000: g's owning field leaked on every call (DEF-8's shape)")
claim("me0107", D, 107, "**One exception (D-251, 1.5.2)**", "rule",
      "A move out of an owning field of a limit<Rules> binding is refused, TYPE-063.",
      expect="refuse:TYPE-063",
      src=main_("""    limit<r_h> H:h = H{ name: string_concat("ab", "c"), n: 1i64 };
    string:s = move(h.name);
    exit 0i32;""", """struct:H = { string:name; int64:n; };
Rules<H>:r_h = { $.n >= 0i64 };"""),
      wrong="accepted: the vacant value a write no rule admits")
claim("me0110", D, 110, "move the whole binding, or copy the part", "rule",
      "The permitted twin: the whole limited binding moves.",
      expect="run:0",
      src=main_("""    limit<r_h> H:h = H{ name: string_concat("ab", "c"), n: 1i64 };
    H:k = move(h);
    if (k.n != 1i64) { exit 10i32; }
    exit 0i32;""", """struct:H = { string:name; int64:n; };
Rules<H>:r_h = { $.n >= 0i64 };"""),
      wrong="refused or 10")

# ------------------------------------------------------------------ 1.2-1.5
claim("me0113", D, 113, "Forces explicit allocation onto the hardware call stack", "rule",
      "A `stack` binding is on the call stack, reclaimed exactly at its scope's exit, a pointer bump.",
      untestable="[unobservable] where a scalar lives and when its stack slot is reclaimed are not "
                 "visible; the frame-size consequence is me0530")
claim("me0114", D, 114, "```nitpick", "example",
      "`stack int32:counter = 0i32;` compiles and holds 0.",
      expect="run:0",
      src=main_("""    stack int32:counter = 0i32;
    counter = counter + 1i32;
    if (counter != 1i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("me0119", D, 119, "If you fail to free a `wild` pointer", "rule",
      "A wild pointer never freed is a leak reported on exit: WildLeak.",
      expect="trap:WildLeak",
      src=main_("""    wild int8->:buffer = alloc(1024i64);
    exit 0i32;"""),
      wrong="0: no report")
claim("me0119b", D, 119, "They explicitly bypass RAII tracking", "rule",
      "A wild pointer bypasses RAII: its block is not freed at its scope's exit (the exit check "
      "still sees it after the block).",
      expect="trap:WildLeak",
      src=main_("""    {
        wild int8->:buffer = alloc(1024i64);
    }
    exit 0i32;"""),
      wrong="0: the block freed at the scope's exit")
claim("me0120", D, 120, "```nitpick", "example",
      "`wild int8->:buffer = alloc(1024i64);` allocates a wild block (freed here with dalloc).",
      expect="run:0",
      src=main_("""    wild int8->:buffer = alloc(1024i64);
    dalloc(buffer);
    exit 0i32;"""),
      wrong="refused, or 96")
claim("me0125", D, 125, "adhering to W⊕X", "rule",
      "wildx memory follows W^X, with ASLR and guard pages.",
      untestable="[unobservable] page permissions and placement are not visible; the W^X refusals are "
                 "VERIFICATION:790-791's claims")
claim("me0126", D, 126, "```nitpick", "example",
      "`wildx uint8->:code = wildx_alloc(4096i64);` allocates an executable page (freed here).",
      expect="compile",
      src=main_("""    wildx uint8->:code = wildx_alloc(4096i64);
    wildx_free(code);
    exit 0i32;"""),
      wrong="refused (wildx_alloc's result needs another spelling)")
claim("me0132", D, 132, "Casting an integer to a pointer is illegal in ordinary code", "rule",
      "Casting an integer to a pointer is refused in ordinary code.",
      expect="refuse",
      src=main_("""    int8->:p = raw v64(4096i64) =>! int8->;
    exit 0i32;"""),
      wrong="accepted")
claim("me0133", D, 133, "legal only in `wild` context (D-019)", "rule",
      "#wild_ptr is legal only in wild context: bound to a plain pointer, it is refused.",
      expect="refuse",
      src=main_("""    int8->:p = #wild_ptr<int8>(raw v64(4096i64));
    exit 0i32;"""),
      wrong="accepted outside wild (BUILTIN's bi0417b row)")
claim("me0135", D, 135, "```nitpick", "example",
      "`wild int8->:page = #wild_ptr<int8->>(addr);` builds a wild pointer from an address.",
      expect="run:0",
      src=main_("""    int64:addr = raw v64(4096i64);
    wild int8->:page = #wild_ptr<int8->>(addr);
    exit 0i32;"""),
      wrong="refused (the type argument is the pointee, not the pointer type)")

# ================================================================== 2. managing wild memory
S68 = "abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def ovf_main(extra=""):
    """main: `extra`, then a run-time IntOverflow (the claim reads failsafe)"""
    return main_(extra + """    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;""")


claim("me0144", D, 144, "Nitpick uses static analysis to prevent leaks at compile time", "rule",
      "Static analysis prevents wild leaks at compile time.",
      untestable="[vague] no leak is named that the compiler refuses; the run-time check (me0053, "
                 "me0119) is what the reference shows catching one")
claim("me0147", D, 147, "This guarantees the free runs on every normal exit path", "rule",
      "A defer runs on every normal exit path, a `fail` included: the callee's wild block is freed, "
      "so main's `exit 0` finds no leak.",
      expect="run:0",
      src=main_("""    int32:r = f() ?| 5i32;
    if (r != 5i32) { exit 10i32; }
    exit 0i32;""", """error:E1;
func:f = int32() {
    wild int8->:b = alloc(16i64);
    defer { dalloc(b); }
    fail E1;
};"""),
      wrong="96: the fail path skipped the defer, and the block leaked")
claim("me0147b", D, 147, "or `exit`)", "rule",
      "A defer runs on `exit`: main's deferred free runs before the exit check.",
      expect="run:0",
      src=main_("""    wild int8->:b = alloc(16i64);
    defer { dalloc(b); }
    exit 0i32;"""),
      wrong="96: exit skipped the defer")
claim("me0149", D, 149, "**`defer` does not run on a trap.**", "rule",
      "A defer does not run on a `?!` trap: control reaches failsafe's arm for the raised error "
      "without the defer (which would divide by zero).",
      expect="run:81",
      src=main_("""    int32:z = raw v32(0i32);
    defer { int32:q = 10i32 / z; discard(q); }
    int32:x = bad() ?! E1;
    exit 0i32;""", """error:E1;
func:bad = int32() { fail E1; };"""),
      wrong="97: the defer ran (DivByZero) before failsafe")
claim("me0149b", D, 149, "`!!!` and `?!` transfer control directly to", "rule",
      "`!!!` transfers control directly to failsafe without running a defer.",
      expect="run:81",
      src=main_("""    int32:z = raw v32(0i32);
    defer { int32:q = 10i32 / z; discard(q); }
    !!! E1;
    exit 0i32;""", "error:E1;"),
      wrong="97: the defer ran first")
claim("me0152", D, 152, "`failsafe` receives the allocation registry intact", "rule",
      "failsafe receives the allocation registry intact: wild_live_count() inside it counts the "
      "block main left live.",
      expect="run:42", fs=False,
      src=ovf_main("    wild int8->:b = alloc(16i64);\n") +
      failsafe_with("        (IntOverflow) { if (wild_live_count() == 1i64) { exit 42i32; } exit 43i32; },"),
      wrong="43: the registry changed before failsafe")
claim("me0155", D, 155, "allocates from a preallocated REGION", "rule",
      "failsafe allocates from a preallocated region: a small allocation inside it succeeds.",
      expect="run:42", fs=False,
      src=ovf_main() + failsafe_with(
          "        (IntOverflow) { wild int8->:p = alloc(raw v64(1000i64)); dalloc(p); exit 42i32; },"),
      wrong="70 or another code: the allocation failed inside failsafe")
claim("me0158", D, 158, "exhaustion is `HeapOom`", "rule",
      "The region is one mebibyte: a 2 MiB allocation inside failsafe is HeapOom there, which the "
      "re-entry rule ends at exit 70.",
      expect="run:70", fs=False,
      src=ovf_main() + failsafe_with(
          "        (IntOverflow) { wild int8->:p = alloc(raw v64(2097152i64)); dalloc(p); exit 42i32; },"),
      wrong="42: the allocation came from the heap, not a 1 MiB region")
claim("me0161", D, 161, "`failsafe` that waited for it would hang with no deadline", "rule",
      "A failsafe never waits for the heap's mutex.",
      untestable="[timing] a thread parked inside the allocator at the stop is a race no single run "
                 "arranges")
claim("me0166", D, 166, "```nitpick", "example",
      "`wild int8->:buf = alloc(16i64); defer { dalloc(buf); }` frees the block at the scope's exit.",
      expect="run:0",
      src=main_("""    wild int8->:buf = alloc(16i64);
    defer { dalloc(buf); }
    exit 0i32;"""),
      wrong="refused or 96")
claim("me0172", D, 172, "The `nodrop` keyword acts as a per-binding RAII opt-out", "rule",
      "`nodrop` opts one binding's initialiser out of the auto-drop tracker.",
      untestable="[vague] the text gives no managed initialiser whose drop `nodrop` would suppress "
                 "observably; the example (me0173) is a wild one")
claim("me0173", D, 173, "```nitpick", "example",
      "`wild int8->:manual_buf = nodrop alloc(16i64);` compiles (freed here with dalloc).",
      expect="run:0",
      src=main_("""    wild int8->:manual_buf = nodrop alloc(16i64);
    dalloc(manual_buf);
    exit 0i32;"""),
      wrong="refused: `nodrop` is not a keyword")
claim("me0179", D, 179, "`move(place)` transfers ownership out of a binding and invalidates the source", "rule",
      "move(place) invalidates the source: freeing the moved-from wild binding is refused.",
      expect="refuse",
      src=main_("""    wild int8->:buffer = alloc(100i64);
    wild int8->:moved = move(buffer);
    dalloc(buffer);
    dalloc(moved);
    exit 0i32;"""),
      wrong="accepted: a double free spelled")
claim("me0183", D, 183, "```nitpick", "example",
      "The example: `free(buffer)` after `move(buffer)` is refused as NITPICK-019 (use after move).",
      expect="refuse:NITPICK-019",
      src=main_("""    wild int8->:buffer = malloc(100i64);
    wild int8->:moved  = move(buffer);

    free(buffer);   // NITPICK-019 — use after move, and separately
                    // "cannot free moved variable"
    exit 0i32;"""),
      wrong="refused for another reason (malloc and free do not exist, §3:281), or accepted")
claim("me0191", D, 191, "**Ownership moves only where `move` is written.**", "rule",
      "Passing an owning value to a function borrows it: the caller still owns it afterwards.",
      expect="run:0",
      src=main_("""    string:s = string_concat("%s", "c");
    int64:n = raw blen(s);
    if (n != 69i64) { exit 10i32; }
    uint8:b = string_bytes(s)[0i64];
    if (b == 170u8) { exit 70i32; }
    if (b != 97u8) { exit 11i32; }
    exit 0i32;""" % S68, """func:blen = int64(string:s) never fails { pass string_byte_length(s); };"""),
      wrong="refused (an implicit move), or 70: the callee dropped what it was lent")
claim("me0194", D, 194, "Any read is", "rule",
      "A moved-from binding is invalid: any read of it is refused.",
      expect="refuse",
      src=main_("""    string:s = string_concat("ab", "c");
    string:t = move(s);
    int64:n = string_byte_length(s);
    exit 0i32;"""),
      wrong="accepted (valid but unspecified)")
claim("me0195", D, 195, "**reinitialized by assignment**", "rule",
      "A moved-from binding may be reinitialized by assignment, after which it is live again.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    string:t = move(s);
    s = string_concat("x", "y");
    if (string_bytes(s)[0i64] != 120u8) { exit 10i32; }
    if (string_bytes(t)[0i64] != 97u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (DEF-124's shape, but for a local), or 10/11")
claim("me0196", D, 196, "A `fixed` binding cannot be", "rule",
      "A fixed binding cannot be reinitialized: it cannot be assigned at all.",
      expect="refuse",
      src=main_("""    F = 3i32;
    exit 0i32;""", "fixed int32:F = 1i32;"),
      wrong="accepted")
claim("me0198", D, 198, "`move` is **not** a memory qualifier", "rule",
      "`move` is not a memory qualifier: a declaration qualified `move` is refused.",
      expect="refuse",
      src=main_("""    move int32:x = 5i32;
    exit 0i32;"""),
      wrong="accepted")
claim("me0199", D, 199, "It is a keyword operator with a parenthesized operand", "rule",
      "move takes a parenthesized operand: `move s` without parentheses is refused.",
      expect="refuse",
      src=main_("""    string:s = string_concat("ab", "c");
    string:t = move s;
    exit 0i32;"""),
      wrong="accepted")
claim("me0202", D, 202, "`$$m place` excludes every other access", "rule",
      "`$$m place` excludes every other access while it lives: reading the place is BORROW-013.",
      expect="refuse:BORROW-013",
      src=main_("""    int32:x = raw v32(1i32);
    int32->:p = $$m x;
    int32:y = x;
    <-p = 2i32;
    exit y - 1i32;"""),
      wrong="accepted")
claim("me0203", D, 203, "`$$i place` admits readers and excludes writers", "rule",
      "`$$i place` admits readers: a plain read beside it is accepted.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(3i32);
    int32->:p = $$i x;
    int32:y = x;
    if (y + <-p != 6i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("me0203b", D, 203, "excludes writers", "rule",
      "`$$i place` excludes writers: assigning the place while it lives is BORROW-013.",
      expect="refuse:BORROW-013",
      src=main_("""    int32:x = raw v32(3i32);
    int32->:p = $$i x;
    x = 4i32;
    exit (<-p) - 3i32;"""),
      wrong="accepted")
claim("me0203c", D, 203, "`@place` is a", "rule",
      "`@place` is a plain address with no claim: writing the place beside it is accepted, and the "
      "address sees the write.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(3i32);
    int32->:p = @x;
    x = 5i32;
    if (<-p != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")
claim("me0206", D, 206, "a computed-index overlap is", "rule",
      "A computed-index overlap of two `$$m` claims is guarded at run time: BorrowOverlap.",
      expect="trap:BorrowOverlap",
      src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int64:i = raw v64(1i64);
    int64:j = raw v64(1i64);
    int32->:p = $$m a[i];
    int32->:q = $$m a[j];
    <-p = 7i32;
    <-q = 8i32;
    exit 10i32;"""),
      wrong="10: the overlap not guarded")
claim("me0208", D, 208, "**A view's root is frozen while the view is live**", "rule",
      "A view's root is frozen while the view lives: assigning the root is BORROW-015.",
      expect="refuse:BORROW-015",
      src=main_("""    string:d = string_concat("ab", "c");
    uint8[]:v = string_bytes(d);
    d = string_concat("x", "y");
    if (v[0i64] != 97u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: the view reads the freed body (DEF-107)")
claim("me0217", D, 217, "Reads, `$$i`, a disjoint field", "rule",
      "Reads of a view's root stay legal while the view lives.",
      expect="run:0",
      src=main_("""    string:d = string_concat("ab", "c");
    uint8[]:v = string_bytes(d);
    int64:n = string_byte_length(d);
    if (n != 3i64) { exit 10i32; }
    if (v[0i64] != 97u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or 10/11")
claim("me0221", D, 221, "End the view's block", "rule",
      "Ending the view's block before writing its root is accepted.",
      expect="run:0",
      src=main_("""    string:d = string_concat("ab", "c");
    {
        uint8[]:v = string_bytes(d);
        if (v[0i64] != 97u8) { exit 10i32; }
    }
    d = string_concat("x", "y");
    if (string_bytes(d)[0i64] != 120u8) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused (the freeze outlived its block), or 10/11")
claim("me0225", D, 225, "cannot travel up (`NITPICK-BORROW-001`", "rule",
      "A by-value parameter's frame storage cannot travel up: returning its address is BORROW-001.",
      expect="refuse:BORROW-001",
      src=main_("""    int32->:p = raw addr_of(raw v32(1i32));
    exit 0i32;""", """func:addr_of = int32->(int32:x) never fails { pass @x; };"""),
      wrong="accepted: a dangling address of the callee's slot")
claim("me0228", D, 228, "is a view of a temporary", "rule",
      "A temporary handed to a callee that views it is a view of a temporary: BORROW-012.",
      expect="refuse:BORROW-012",
      src=main_("""    uint8[]:v = string_bytes(string_concat("ab", "c"));
    if (v[0i64] != 97u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: a view of storage dropped at the statement's end")
claim("me0230", D, 230, "**What a call stores is read off the callee's own body**", "rule",
      "What a call stores is read off the callee's own body (D-325's summaries).",
      untestable="[internal] the analysis's method; its outcomes are the BORROW refusals and "
                 "acceptances claimed at me0208-me0228")
claim("me0242", D, 242, "A plain by-value parameter of an OWNING type is a loan and is read-only", "rule",
      "A plain by-value parameter of an owning type is a read-only loan: assigning it is TYPE-085.",
      expect="refuse:TYPE-085",
      src=main_("""    string:s = string_concat("ab", "c");
    drop f(s);
    exit 0i32;""", """func:f = NIL(string:p) {
    p = string_concat("x", "y");
    pass NIL;
};"""),
      wrong="accepted: the caller's value freed by the callee (DEF-102)")
claim("me0245", D, 245, "changes an owning value takes it as `move T:p`", "rule",
      "A callee that changes an owning value takes it as `move T:p`.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    string:t = raw f(move(s));
    if (string_bytes(t)[0i64] != 120u8) { exit 10i32; }
    exit 0i32;""", """func:f = string(move string:p) never fails {
    p = string_concat("x", "y");
    pass p;
};"""),
      wrong="refused or 10")
claim("me0246", D, 246, "a copyable parameter is a copy and keeps every write", "rule",
      "A copyable parameter is a copy: the callee's writes stay in the callee.",
      expect="run:0",
      src=main_("""    int32:a = raw v32(1i32);
    int32:r = raw bump(a);
    if (r != 2i32) { exit 10i32; }
    if (a != 1i32) { exit 11i32; }
    exit 0i32;""", """func:bump = int32(int32:x) never fails {
    x = x + 1i32;
    pass x;
};"""),
      wrong="refused (10 no), 11: the write reached the caller")
claim("me0247", D, 247, "A `fixed` binding has no address", "rule",
      "A fixed binding has no address: `@F` is TYPE-071.",
      expect="refuse:TYPE-071",
      src=main_("""    int32->:p = @F;
    exit 0i32;""", "fixed int32:F = 1i32;"),
      wrong="accepted")
claim("me0248", D, 248, "cannot be moved out of", "rule",
      "An owning fixed binding cannot be moved out of: `move(FS)` is TYPE-084.",
      expect="refuse:TYPE-084",
      src=main_("""    string:t = move(FS);
    exit 0i32;""", 'fixed string:FS = "abc";'),
      wrong="accepted (DEF-99)")
claim("me0250", D, 250, "`.clone()` is", "rule",
      "`.clone()` is the reading of an owning fixed binding.",
      expect="run:0",
      src=main_("""    string:t = FS.clone();
    if (string_bytes(t)[0i64] != 97u8) { exit 10i32; }
    exit 0i32;""", 'fixed string:FS = "abc";'),
      wrong="refused or 10")
claim("me0251", D, 251, "and no PART of one is written after its declaration", "rule",
      "No part of a fixed binding is written after its declaration: an element store is TYPE-086.",
      expect="refuse:TYPE-086",
      src=main_("""    FA[0i64] = 5i32;
    exit 0i32;""", "fixed int32[2]:FA = [1i32, 2i32];"),
      wrong="accepted (DEF-106)")
claim("me0255", D, 255, "`NITPICK-ASSIGN-002`", "rule",
      "The whole fixed binding's second assignment stays ASSIGN-002.",
      expect="refuse:ASSIGN-002",
      src=main_("""    FA = [3i32, 4i32];
    exit 0i32;""", "fixed int32[2]:FA = [1i32, 2i32];"),
      wrong="accepted, or another code")

# ================================================================== 3. allocation built-ins
claim("me0262", D, 262, "2^47 bytes (140,737,488,355,328", "rule",
      "A request above 2^47 bytes is a bad request: alloc(2^47 + 1) traps HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = alloc(raw v64(140737488355329i64));
    dalloc(p);
    exit 10i32;"""),
      wrong="HeapOom (the kernel asked), or 10")
claim("me0268", D, 268, "a compare that reads a negative size as", "rule",
      "The one compare reads a negative size as a huge one: alloc(-1) traps HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = alloc(raw v64(-1i64));
    dalloc(p);
    exit 10i32;"""),
      wrong="another trap, or 10")
claim("me0269", D, 269, "Exactly the ceiling is legal", "rule",
      "Exactly the ceiling is legal: alloc(2^47) is not a bad request, and the kernel's refusal is HeapOom.",
      expect="trap:HeapOom",
      src=main_("""    wild int8->:p = alloc(raw v64(140737488355328i64));
    dalloc(p);
    exit 10i32;"""),
      wrong="HeapBadRequest: the ceiling itself refused")
claim("me0276", D, 276, "**`alloc(size)`**: Allocate `size` uninitialized bytes", "rule",
      "alloc(size) gives size bytes the program can write and read back.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(16i64);
    p[15i64] = 7i8;
    if (p[15i64] != 7i8) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="refused or 10")
claim("me0277", D, 277, "**`calloc(count, size)`**: Allocate zero-initialized memory", "rule",
      "calloc(count, size) allocates zero-initialized memory.",
      expect="run:0",
      src=main_("""    wild int8->:p = calloc(raw v64(4i64), raw v64(4i64));
    int64:i = 0i64;
    while (i < 16i64) decreases 16i64 - i {
        if (p[i] != 0i8) { exit 10i32; }
        i = i + 1i64;
    }
    dalloc(p);
    exit 0i32;"""),
      wrong="10: a nonzero byte")
claim("me0278", D, 278, "**`ralloc(ptr, new_size)`**: Resize the allocation", "rule",
      "ralloc resizes the allocation and keeps its contents.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(16i64);
    p[0i64] = 7i8;
    wild int8->:q = ralloc(p, 64i64);
    if (q[0i64] != 7i8) { exit 10i32; }
    q[63i64] = 1i8;
    dalloc(q);
    exit 0i32;"""),
      wrong="refused, or 10: the contents lost")
claim("me0278b", D, 278, "Old pointer becomes invalid", "rule",
      "After ralloc the old pointer is invalid: freeing it is refused.",
      expect="refuse",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = ralloc(p, 64i64);
    dalloc(p);
    dalloc(q);
    exit 0i32;"""),
      wrong="accepted: a free of the stale pointer compiles")
claim("me0281", D, 281, "There are **no aliases**", "rule",
      "There are no aliases: `realloc` is refused.",
      expect="refuse",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = realloc(p, 32i64);
    dalloc(q);
    exit 0i32;"""),
      wrong="accepted")
claim("me0285", D, 285, "**`aalloc(size, align)`**", "rule",
      "aalloc(size, align) serves an alignment above sixteen.",
      expect="run:0",
      src=main_("""    wild int8->:p = aalloc(64i64, raw v64(64i64));
    p[63i64] = 3i8;
    if (p[63i64] != 3i8) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="refused, a trap, or 10")
claim("me0288", D, 288, "a hidden 16-byte header", "rule",
      "Every heap allocation carries a hidden 16-byte header: the size and a keyed magic word.",
      untestable="[internal] the header is out of the payload a program may read")
claim("me0290", D, 290, "double-free and header corruption and routes them to `failsafe`", "rule",
      "The allocator detects a double free the static analysis cannot follow and routes it to "
      "failsafe (-4102, Unreachable): a pointer freed twice through a callee.",
      expect="trap:Unreachable",
      src=main_("""    wild int8->:p = alloc(16i64);
    drop free_it(p);
    drop free_it(p);
    exit 10i32;""", """func:free_it = NIL(wild int8->:q) {
    dalloc(q);
    pass NIL;
};"""),
      wrong="10: the second free went undetected; or refused")
claim("me0292", D, 292, "the multiply is CHECKED", "rule",
      "calloc's count x size is checked: an overflowing product traps HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = calloc(raw v64(4611686018427387904i64), raw v64(16i64));
    dalloc(p);
    exit 10i32;"""),
      wrong="a small block (the product wrapped), or 10")
claim("me0293", D, 293, "`ralloc(p, 0)`", "rule",
      "ralloc(p, 0) is a malformed request: HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = ralloc(p, raw v64(0i64));
    dalloc(q);
    exit 10i32;"""),
      wrong="10: a zero-size block")
claim("me0293b", D, 293, "a non-power-of-two alignment", "rule",
      "A non-power-of-two alignment is a malformed request: aalloc(64, 48) traps HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = aalloc(64i64, raw v64(48i64));
    dalloc(p);
    exit 10i32;"""),
      wrong="10")
claim("me0301", D, 301, "binding is additionally a compile-time error (D-119)", "rule",
      "Double-free of a tracked binding is a compile-time error.",
      expect="refuse",
      src=main_("""    wild int8->:p = alloc(16i64);
    dalloc(p);
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted (the runtime catches it, but the compiler should)")
claim("me0305", D, 305, "a garbage", "rule",
      "dalloc proves a pointer lies in allocator-owned memory first: a garbage pointer is one of "
      "the allocator's traps, never a wild load (failsafe here maps HeapBadRequest, HeapOom and "
      "Unreachable to 42, MachineFault to 43).",
      expect="run:42", fs=False,
      src=main_("""    wild int8->:g = #wild_ptr<int8>(raw v64(4096i64));
    dalloc(g);
    exit 10i32;""") + failsafe_with("""        (HeapBadRequest) { exit 42i32; },
        (HeapOom) { exit 42i32; },
        (Unreachable) { exit 42i32; },
        (MachineFault) { exit 43i32; },"""),
      wrong="43: a fault at a wild load; 10: the free went through")
claim("me0306", D, 306, "The heap is single-threaded at this", "rule",
      "The heap is single-threaded at this rung.",
      untestable="[vague] a statement about a past rung; the heap has had a mutex since D-291 (line 160)")

# ------------------------------------------------------------------ the <wild-live> registry
claim("me0313", D, 313, "never managed storage: a string's", "rule",
      "The exit check never counts managed storage: a string alive in main at `exit 0` is not reported.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    if (string_bytes(s)[0i64] != 97u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="96: managed storage counted")
claim("me0312", D, 312, "from `alloc`, `aalloc`, `calloc` and a `ralloc` of one", "rule",
      "Every calloc block is counted: one unpaired at `exit 0` traps WildLeak.",
      expect="trap:WildLeak",
      src=main_("""    wild int8->:p = calloc(raw v64(2i64), raw v64(8i64));
    exit 0i32;"""),
      wrong="0: the block not counted")
claim("me0316", D, 316, "so an owning local of", "rule",
      "exit runs no drops, so an owning local of main is never dropped by a program that exits.",
      untestable="[unobservable] a managed body freed or not at exit is the kernel's either way; no "
                 "program reads it after exit")
claim("me0328", D, 328, "**`wild_live_count()`**", "rule",
      "wild_live_count() counts the live wild blocks.",
      expect="run:0",
      src=main_("""    wild int8->:a = alloc(16i64);
    wild int8->:b = alloc(32i64);
    if (wild_live_count() != 2i64) { exit 10i32; }
    dalloc(a);
    if (wild_live_count() != 1i64) { exit 11i32; }
    dalloc(b);
    if (wild_live_count() != 0i64) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused, or 10-12")
claim("me0333", D, 333, "with a non-empty set routes to `failsafe`", "rule",
      "A successful exit with a non-empty set routes to failsafe with -4105 (WildLeak).",
      expect="trap:WildLeak",
      src=main_("""    wild int8->:p = alloc(8i64);
    exit 0i32;"""),
      wrong="0")
claim("me0334", D, 334, "A failure exit keeps its code", "rule",
      "A failure exit keeps its code: `exit 3` with a live wild block exits 3.",
      expect="run:3",
      src=main_("""    wild int8->:p = alloc(8i64);
    exit 3i32;"""),
      wrong="96: the leak trap hijacked the error exit")
claim("me0337", D, 337, "followed by `exit` and by", "rule",
      "wild_release_all() is followed by exit and nothing else: another statement after it is TYPE-062.",
      expect="refuse:TYPE-062", fs=False,
      src=main_("""    wild int8->:p = alloc(8i64);
    exit 0i32;""") + failsafe_with("""        (WildLeak) { wild_release_all(); int32:k = raw v32(1i32); exit k + 41i32; },"""),
      wrong="accepted")
claim("me0339", D, 339, "drops every chunk and", "rule",
      "failsafe may call wild_release_all() then exit positive: the leak's handler exits 42.",
      expect="run:42", fs=False,
      src=main_("""    wild int8->:p = alloc(8i64);
    exit 0i32;""") + failsafe_with("""        (WildLeak) { wild_release_all(); exit 42i32; },"""),
      wrong="another code, or 70")
claim("me0342", D, 342, "same flag makes a trap RAISED INSIDE failsafe exit 70 directly", "rule",
      "A trap raised inside failsafe exits 70 directly instead of recursing.",
      expect="run:70", fs=False,
      src=ovf_main() + failsafe_with("""        (IntOverflow) { int32:z = raw v32(0i32); int32:q = 10i32 / z; exit q; },"""),
      wrong="97 (a recursion into failsafe) or a hang")
claim("me0345", D, 345, "**One registry mechanism, three clients**", "rule",
      "One registry mechanism serves the allocation tables, the stream registry and the driver registry.",
      untestable="[internal] the runtime's table layout")

# ================================================================== 4. Handle<T> and arenas
AR = """    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
"""
J2 = "fixed Duration:J2 = Duration{ ns: 2000000000i64 };"

claim("me0358", D, 358, "allocate the graph", "rule",
      "Arenas handle cycles: a graph is allocated in an arena and dropped wholesale.",
      untestable="[vague] a pattern of use; the arena's operations are claimed at me0390-me0397")
claim("me0362", D, 362, "Attempting to use the old handle immediately fails safely", "rule",
      "A handle whose slot was freed fails safely through Result, never a silent use-after-free.",
      expect="run:0",
      src=main_(AR + """    a.put(h, 41i64) ?! E1;
    a.free(h) ?! E2;
    Result<int64>:r = a.get(h);
    if (!r.is_error) { exit 10i32; }
    a.destroy();
    exit 0i32;""", "error:E1;\nerror:E2;"),
      wrong="10: the stale handle read a value")
claim("me0364", D, 364, "Handles are **indices, not pointers**", "rule",
      "Handles are indices, safe across arena growth: ten slots in an arena made for two all read back.",
      expect="run:0",
      src=main_("""    arena<int64>:a = arena_make(2i64);
    Handle<int64>[10]:hs = [a.alloc(), a.alloc(), a.alloc(), a.alloc(), a.alloc(),
                            a.alloc(), a.alloc(), a.alloc(), a.alloc(), a.alloc()];
    int64:i = 0i64;
    while (i < 10i64) decreases 10i64 - i { a.put(hs[i], i * 3i64) ?! E1; i = i + 1i64; }
    i = 0i64;
    while (i < 10i64) decreases 10i64 - i {
        if ((a.get(hs[i]) ?! E2) != i * 3i64) { exit 10i32; }
        i = i + 1i64;
    }
    a.destroy();
    exit 0i32;""", "error:E1;\nerror:E2;"),
      wrong="10: growth moved or lost a slot")
claim("me0368", D, 368, "lowers into a 16-byte aligned struct", "rule",
      "Handle<T> is a 16-byte struct.",
      expect="run:0",
      src=main_("""    if (#size_of<Handle<int64>>() != 16i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: another size")
claim("me0368b", D, 368, "(`%Handle = type { i64, i32 }` in LLVM IR)", "rule",
      "Handle<T> is `{ i64, i32 }` in the IR: a function taking one has that parameter type.",
      expect=r'ir:^define [^\n]*@"[^"]*\.hh"\(\{ ?i64, i32 ?\}',
      src=main_("""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    int32:r = raw hh(h);
    a.destroy();
    exit r;""", """func:hh = int32(Handle<int64>:h) never fails { pass 0i32; };"""),
      wrong="another struct")
claim("me0369", D, 369, "**Bytes [0-7]**: `uint64:index`", "rule",
      "Bytes 0-7 are the index, 8-11 the generation, 12-15 padding.",
      untestable="[internal] a handle's bytes are not readable from a program; the field order is "
                 "me0368b's IR test")
claim("me0375", D, 375, "Creation is the **`arena_make(cap)`** builtin", "rule",
      "Creation is arena_make(cap), type-directed by the annotation.",
      expect="run:0",
      src=main_(AR + """    a.put(h, 5i64) ?! E1;
    if ((a.get(h) ?! E1) != 5i64) { exit 10i32; }
    a.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="refused or 10")
claim("me0377", D, 377, "wrote `arena<int64>.alloc(1000)`", "rule",
      "The old spelling `arena<int64>.alloc(1000)` (creation on the type) is not the language.",
      expect="refuse",
      src=main_("""    arena<int64>:a = arena<int64>.alloc(1000i64);
    exit 0i32;"""),
      wrong="accepted")
claim("me0381", D, 381, "```nitpick", "example",
      "The example compiles and runs: put 41, `get(h) ? 0i64` reads it, then free and destroy.",
      expect="run:0",
      src=main_("""    arena<int64>:my_arena = arena_make(1000i64);
    Handle<int64>:h = my_arena.alloc();
    drop my_arena.put(h, 41i64);             // write through the handle
    int64:val = my_arena.get(h) ? 0i64;      // read a COPY, with a default
    drop my_arena.free(h);
    my_arena.destroy();
    if (val != 41i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (a bare `?` is not the fallback since D-175), or 10")
claim("me0390", D, 390, "The set is `alloc() -> Handle<T>`", "rule",
      "The arena's set is alloc, get, put, free, reset and destroy, with their stated results.",
      expect="run:0",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    Result<NIL>:p = a.put(h, 7i64);
    Result<int64>:g = a.get(h);
    if (p.is_error || g.is_error) { exit 10i32; }
    if (g.value != 7i64) { exit 11i32; }
    Result<NIL>:f = a.free(h);
    if (f.is_error) { exit 12i32; }
    a.reset();
    a.destroy();
    exit 0i32;"""),
      wrong="refused (a member or a result type differs), or 10-12")
claim("me0392", D, 392, "`get` returns the element", "rule",
      "get returns the element by value: changing the copy leaves the slot.",
      expect="run:0",
      src=main_(AR + """    a.put(h, 41i64) ?! E1;
    int64:v = a.get(h) ?! E1;
    v = 99i64;
    if ((a.get(h) ?! E1) != 41i64) { exit 10i32; }
    a.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="10: get handed out the slot itself")
claim("me0394", D, 394, "A stale handle fails", "rule",
      "A stale handle fails get, put and free with -4106 (StaleHandle) in Result.err, never a trap.",
      expect="run:0",
      src=main_(AR + """    a.free(h) ?! E1;
    Result<int64>:g = a.get(h);
    Result<NIL>:p = a.put(h, 1i64);
    Result<NIL>:f = a.free(h);
    if (!g.is_error || g.err != StaleHandle) { exit 10i32; }
    if (!p.is_error || p.err != StaleHandle) { exit 11i32; }
    if (!f.is_error || f.err != StaleHandle) { exit 12i32; }
    a.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="a trap (100), or 10-12: another error or none")
claim("me0396", D, 396, "`destroy` CONSUMES the arena", "rule",
      "destroy consumes the arena at compile time: using it afterwards is refused.",
      expect="refuse",
      src=main_(AR + """    a.destroy();
    Handle<int64>:k = a.alloc();
    exit 0i32;"""),
      wrong="accepted")
claim("me0397", D, 397, "un-destroyed arena is a wild-role leak the exit-time check names", "rule",
      "An un-destroyed arena is a wild-role leak the exit check names: WildLeak at `exit 0`.",
      expect="trap:WildLeak",
      src=main_(AR + """    exit 0i32;"""),
      wrong="0: the arena's blocks not counted")
claim("me0399", D, 399, "`?` takes a **fallback value**", "rule",
      "`?` takes a fallback value: a stale get with `? 0i64` yields 0.",
      expect="run:0",
      src=main_(AR + """    a.free(h) ?! E1;
    int64:v = a.get(h) ? 0i64;
    if (v != 0i64) { exit 10i32; }
    a.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="refused (the fallback is `?|` since D-175), or 10")
claim("me0399b", D, 399, "`?!` takes a **failsafe error", "rule",
      "`?!` takes a failsafe error code and traps: a stale get with `?! E2` reaches E2's arm.",
      expect="run:82",
      src=main_(AR + """    a.free(h) ?! E1;
    int64:v = a.get(h) ?! E2;
    exit 10i32;""", "error:E1;\nerror:E2;"),
      wrong="10, or another arm")
claim("me0404", D, 404, "`.` handles all member access and auto-dereferences pointers", "rule",
      "`.` auto-dereferences a pointer: `p.n` through a Box-> reads the field.",
      expect="run:0",
      src=main_("""    Box:b = Box{ n: 7i32 };
    Box->:p = @b;
    if (p.n != 7i32) { exit 10i32; }
    exit 0i32;""", "struct:Box = { int32:n; };"),
      wrong="refused (an explicit deref demanded), or 10")
claim("me0408", D, 408, "```nitpick", "example",
      "An arena embedded in a struct: `app.my_arena.alloc()` works as member-place addressing.",
      expect="compile",
      src=main_("""    App:app = App{ my_arena: arena_make(16i64) };
    Handle<int64>:h = app.my_arena.alloc();
    exit 0i32;""", "struct:App = { arena<int64>:my_arena; };"),
      wrong="refused")
claim("me0418", D, 418, "The surface `arena<T>` is a **fixed-slot** allocator", "rule",
      "The executor frame allocator is not arena<T>: arena<T> hands out fixed-slot indices.",
      untestable="[internal] the coroutine frame allocator is the runtime's")
claim("me0424", D, 424, "runtime-internal — no keyword, no", "rule",
      "The executor frame allocator is runtime-internal, no builtin: npk_frame_alloc is not callable.",
      expect="refuse",
      src=main_("""    wild int8->:f = npk_frame_alloc(64i64, 16i64);
    exit 0i32;"""),
      wrong="accepted")
claim("me0434", D, 434, "an un-destroyed executor is a countable leak", "rule",
      "The executor and its chunks are wild-role blocks; an un-destroyed executor is a countable leak.",
      untestable="[internal] no program holds an executor to leave undestroyed")
claim("me0439", D, 439, "`arena<T>` is **single-threaded**", "rule",
      "arena<T> is single-threaded: handing one to a thread is refused.",
      expect="refuse",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    drop worker(@a);
    a.destroy();
    exit 0i32;""", J2 + """
thread async func:worker = NIL(arena<int64>->:a) joins J2 {
    Handle<int64>:h = a.alloc();
    pass NIL;
};""").replace("func:main = int32", "async func:main = int32"),
      wrong="accepted: two threads in one single-threaded arena")
claim("me0449", D, 449, "| Threading | single-threaded | multi-threaded |", "row",
      "A shared_arena is multi-threaded: a thread allocates in it, and after the join the owner reads "
      "the value through the handle the thread returned on a channel.",
      expect="run:0",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Channel<Handle<int64>, 3i32, 1i64>:ch = channel() ?! E1;
    {
        drop worker(@s, ch);
    }
    Handle<int64>:h = await ch.recv(raw duration_ms(500i64)) ?! E2;
    int64:v = s.get(h) ?! E3;
    s.destroy();
    if (v != 77i64) { exit 10i32; }
    exit 0i32;""", "error:E1;\nerror:E2;\nerror:E3;\nerror:E4;\n" + J2 + """
thread async func:worker = NIL(shared_arena<int64>->:s, Channel<Handle<int64>, 3i32, 1i64>:c) joins J2 {
    Handle<int64>:h = s.alloc(77i64);
    await c.send(h, raw duration_ms(500i64)) ?! E4;
    pass NIL;
};""").replace("func:main = int32", "async func:main = int32"),
      wrong="refused, or 10")
claim("me0450", D, 450, "| Operations | `alloc`, `get`, `free`, `reset`, `destroy` |", "row",
      "A shared_arena has only alloc, get and destroy: `reset` is refused.",
      expect="refuse",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    s.reset();
    s.destroy();
    exit 0i32;"""),
      wrong="accepted")
claim("me0451", D, 451, "| Per-slot `free` | yes | **no** |", "row",
      "A shared_arena has no per-slot free: `s.free(h)` is refused.",
      expect="refuse",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(1i64);
    drop s.free(h);
    s.destroy();
    exit 0i32;"""),
      wrong="accepted")
claim("me0452", D, 452, "| Storage | may reallocate on growth | **chunked, never moves** |", "row",
      "A shared arena's storage is chunked and never moves; an arena<T>'s may reallocate.",
      untestable="[unobservable] no operation yields an address to compare before and after growth")
claim("me0453", D, 453, "| Cost | zero | one atomic bump per allocation |", "row",
      "An arena<T> allocation costs nothing extra; a shared arena's one atomic bump.",
      untestable="[internal] the allocation paths are the runtime's (npk_arena_*, npk_sarena_*)")
claim("me0455", D, 455, "Dropping per-slot `free` is what makes concurrency safe", "rule",
      "Dropping per-slot free makes concurrency safe without epochs, hazard pointers or counting.",
      untestable="[vague] the rationale for the contract; the contract is me0450-me0451")
claim("me0461", D, 461, "`destroy` requires that no thread still holds handles", "rule",
      "destroy requires that no thread still holds the arena: destroying it while a spawned thread "
      "holds it is refused.",
      expect="refuse",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(8i64);
    drop filler(@s);
    s.destroy();
    exit 0i32;""", J2 + """
thread async func:filler = NIL(shared_arena<int64>->:s) joins J2 {
    Handle<int64>:h = s.alloc(1i64);
    pass NIL;
};""").replace("func:main = int32", "async func:main = int32"),
      wrong="accepted (DEF-148's shape)")
claim("me0464", D, 464, "creation is `shared_arena_make(cap)`", "rule",
      "Creation is shared_arena_make(cap), type-directed like arena_make.",
      expect="run:0",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(9i64);
    if ((s.get(h) ?! E1) != 9i64) { exit 10i32; }
    s.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="refused or 10")
claim("me0465", D, 465, "the surface value is ONE POINTER", "rule",
      "A shared_arena's surface value is one pointer: 8 bytes.",
      expect="run:0",
      src=main_("""    if (#size_of<shared_arena<int64>>() != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: a struct, not one pointer")
claim("me0467", D, 467, "**`alloc(v)` carries the value**, because there is no `put`", "rule",
      "A shared arena has no `put`: `s.put(h, v)` is refused.",
      expect="refuse",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(1i64);
    drop s.put(h, 2i64);
    s.destroy();
    exit 0i32;"""),
      wrong="accepted")
claim("me0471", D, 471, "`get` COPIES", "rule",
      "A shared arena's get copies: changing the copy leaves the slot.",
      expect="run:0",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(5i64);
    int64:v = s.get(h) ?! E1;
    v = 6i64;
    if ((s.get(h) ?! E1) != 5i64) { exit 10i32; }
    s.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="10")
claim("me0474", D, 474, "RESERVES a capacity range with one atomic `fetch_add`", "rule",
      "Growth reserves a capacity range with one atomic fetch_add and publishes the chunk by CAS.",
      untestable="[internal] the runtime's growth protocol; its model is VERIFICATION §9's")
claim("me0476", D, 476, "chunk sizes are geometric", "rule",
      "Chunk sizes are geometric, capped at 65536 slots.",
      untestable="[internal] chunk sizes are not visible to a program")
claim("me0479", D, 479, "`arena<T>` issues generations starting at 2", "rule",
      "Shared handles carry generation 0 and arena<T>'s start at 2: an arena<T> handle in a shared "
      "get is refused as stale (StaleHandle), not read.",
      expect="run:0",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    a.put(h, 3i64) ?! E1;
    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:k = s.alloc(8i64);
    Result<int64>:r = s.get(h);
    if (!r.is_error) { exit 10i32; }
    if (r.err != StaleHandle) { exit 11i32; }
    if ((s.get(k) ?! E1) != 8i64) { exit 12i32; }
    a.destroy();
    s.destroy();
    exit 0i32;""", "error:E1;"),
      wrong="10: the foreign handle read a slot; 11: another error")
claim("me0481", D, 481, "`destroy` consumes the binding at compile time", "rule",
      "A shared arena's destroy consumes the binding at compile time: a use after it is MOVE-002.",
      expect="refuse:MOVE-002",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    s.destroy();
    Handle<int64>:h = s.alloc(1i64);
    exit 0i32;"""),
      wrong="accepted, or another code")
claim("me0482", D, 482, "an un-destroyed shared arena is a wild-role leak", "rule",
      "An un-destroyed shared arena is a wild-role leak the exit check names: WildLeak.",
      expect="trap:WildLeak",
      src=main_("""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(1i64);
    exit 0i32;"""),
      wrong="0")

# ================================================================== 5. the stacks
DEEP = """func:rec = int64(int64:n) never fails {
    int64[128]:a = [%s];
    a[n %% 128i64] = n;
    if (n == 0i64) { pass a[0i64]; }
    pass (raw rec(n - 1i64)) + a[n %% 128i64];
};""" % ", ".join(["0i64"] * 128)
FOREVER = """func:down = int64(int64:n) never fails {
    int64[16]:a = [%s];
    a[n %% 16i64] = n;
    pass (raw down(n + 1i64)) + a[n %% 16i64];
};""" % ", ".join(["0i64"] * 16)

claim("me0488", D, 488, "`ulimit -s` and `RLIMIT_STACK` do not size any", "rule",
      "ulimit -s does not size the main thread's stack: a recursion using about 4 MiB runs to 0 "
      "under `ulimit -s 512`.",
      expect="sh:0",
      sh=r"""cat > s.npk <<'NPK'
mod:s;

""" + DEEP + r"""

func:main = int32(cstring[]:_~argv) {
    int64:t = raw rec(4000i64);
    if (t < 0i64) { exit 10i32; }
    exit 0i32;
};

""" + failsafe_text("") + r"""NPK
"$NPKC" s.npk -o s.ll > npkc.log 2>&1 || exit 2
llc -O0 -filetype=obj -relocation-model=static s.ll -o s.o || exit 3
ld.lld -static s.o "$NPKRT" -o s || exit 4
( ulimit -s 512; env -i ./s < /dev/null ); rc=$?
[ "$rc" -eq 0 ] || exit 1
exit 0""",
      wrong="1: the program died under the shell's limit (it ran on the kernel's stack)")
claim("me0491", D, 491, "Each stack is ONE anonymous mapping", "rule",
      "Each stack is one anonymous mapping, lowest address first.",
      untestable="[internal] a mapping's layout is not visible to a program")
claim("me0496", D, 496, "| guard (`PROT_NONE`) | 4 KiB | yes | yes | yes |", "row",
      "Each stack starts with a 4 KiB PROT_NONE guard (main, spawned and failsafe).",
      untestable="[unobservable] reaching a guard page needs an address below the frame")
claim("me0497", D, 497, "| signal stack | 64 KiB | yes | yes | — |", "row",
      "Main and spawned threads have a 64 KiB signal stack.",
      untestable="[internal] the signal stack's size is not visible")
claim("me0498", D, 498, "| guard (`PROT_NONE`) | 4 KiB | yes | yes | — |", "row",
      "A second 4 KiB guard sits above the signal stack.",
      untestable="[unobservable] as me0496")
claim("me0499", D, 499, "| reserve (below the limit word) | 64 KiB | yes | yes | yes |", "row",
      "A 64 KiB reserve lies below the limit word.",
      untestable="[internal] the reserve is the floor's; no emitted function may enter it")
claim("me0500", D, 500, "| usable | — | 8 MiB | 2 MiB | 1 MiB |", "row",
      "The main thread's usable stack is 8 MiB: a recursion using about 4 MiB runs.",
      expect="run:0",
      src=main_("""    int64:t = raw rec(4000i64);
    if (t < 0i64) { exit 10i32; }
    exit 0i32;""", DEEP),
      wrong="StackExhausted (106): the main stack is smaller than 4 MiB")
claim("me0500b", D, 500, "| 2 MiB |", "row",
      "A spawned thread's usable stack is 2 MiB: the same 4 MiB recursion on a thread traps StackExhausted.",
      expect="trap:StackExhausted",
      src=main_("""    drop deep();
    exit 0i32;""", J2 + "\n" + DEEP + """
thread async func:deep = NIL() joins J2 {
    int64:t = raw rec(4000i64);
    if (t < 0i64) { pass NIL; }
    pass NIL;
};""").replace("func:main = int32", "async func:main = int32"),
      wrong="0: the thread's stack holds 4 MiB")
claim("me0502", D, 502, "**The check is in every function the compiler emits.**", "rule",
      "Every function the compiler emits carries LLVM's split-stack prologue.",
      expect=r'ir:^define [^\n]*@"[^"]*\.plain"\([^)]*\) "split-stack"',
      src=main_("""    int32:r = raw plain(raw v32(1i32));
    exit r - 1i32;""", "func:plain = int32(int32:x) never fails { pass x; };"),
      wrong="no split-stack attribute on the define")
claim("me0505", D, 505, "Crossing it enters the trap route", "rule",
      "Crossing the limit enters the trap route as StackExhausted: an unbounded recursion traps it.",
      expect="trap:StackExhausted",
      src=main_("""    int64:t = raw down(0i64);
    exit 10i32;""", FOREVER),
      wrong="139 (a raw SIGSEGV) or a hang")
claim("me0506", D, 506, "which every `failsafe` names because every program", "rule",
      "Every failsafe names StackExhausted: one that does not is refused.",
      expect="refuse", fs=False,
      src=main_("""    exit 0i32;""") + fs_except("StackExhausted"),
      wrong="accepted")
claim("me0507", D, 507, "A frame larger than a page is refused at the prologue", "rule",
      "A frame larger than a page is refused at its prologue: StackExhausted, not a jump over the guard.",
      expect="trap:StackExhausted",
      src=main_("""    int64:t = raw big(raw v64(3i64));
    exit 10i32;""", """func:big = int64(int64:k) never fails {
    int64[1024]:a = [%s];
    a[k] = k;
    pass a[k] + a[1023i64];
};""" % ", ".join(["0i64"] * 1024)),
      wrong="10: an 8 KiB frame ran (the guard was jumped), or 139")
claim("me0509", D, 509, "The", "rule",
      "The floor's own functions carry no prologue and fit in the reserve.",
      untestable="[internal] the runtime's functions; a belt proves it (VERIFICATION §9.5)")
claim("me0512", D, 512, "**`failsafe` runs on a stack of its own**", "rule",
      "failsafe runs on its own stack: entered by StackExhausted, it still has room for a recursion "
      "of about 512 KiB.",
      expect="run:42", fs=False,
      src=main_("""    int64:t = raw down(0i64);
    exit 10i32;""", FOREVER + "\n" + DEEP.replace("int64[128]", "int64[64]").replace(
          "[%s]" % ", ".join(["0i64"] * 128), "[%s]" % ", ".join(["0i64"] * 64)).replace(
          "128i64", "64i64")) +
      failsafe_with("        (StackExhausted) { int64:t = raw rec(1000i64); if (t < 0i64) { exit 43i32; } exit 42i32; },"),
      wrong="70: failsafe had no stack of its own to recurse on")
claim("me0514", D, 514, "an overflow inside `failsafe` meets", "rule",
      "An overflow inside failsafe meets the re-entry rule and exits 70.",
      expect="run:70", fs=False,
      src=ovf_main() + "\n" + FOREVER + "\n" + failsafe_with(
          "        (IntOverflow) { int64:t = raw down(0i64); exit 42i32; },"),
      wrong="a hang or 139")
claim("me0515", D, 515, "**Signals run on the thread's signal stack**", "rule",
      "Signals run on the thread's signal stack (SA_ONSTACK).",
      untestable="[internal] which stack a signal frame lands on is not visible")
claim("me0520", D, 520, "**A spawned thread's stack is released at its join**", "rule",
      "A spawned thread's stack is unmapped at its join.",
      untestable="[unobservable] a mapping's release shows only in the process's maps, which a "
                 "program here does not read")
claim("me0526", D, 526, "a program spawn and", "rule",
      "Threads are spawned and joined without limit: two hundred in sequence, each joined, run.",
      expect="run:0",
      src=main_("""    int64:i = 0i64;
    while (i < 200i64) decreases 200i64 - i {
        {
            drop tick();
        }
        i = i + 1i64;
    }
    exit 0i32;""", J2 + """
thread async func:tick = NIL() joins J2 {
    pass NIL;
};""").replace("func:main = int32", "async func:main = int32"),
      wrong="a refusal at the 65th, or a trap")
claim("me0527", D, 527, "The 65th LIVE thread is refused at its start", "rule",
      "The 65th live thread is refused at its start.",
      untestable="[vague] the outcome of the refusal (a trap, an error, its identity) is not stated")
claim("me0530", D, 530, "**A `stack` binding (§1.2) lives in the frame of the function that declares", "rule",
      "A `stack` binding lives in its function's frame: a large stack array is a large frame, refused "
      "at the prologue (StackExhausted).",
      expect="trap:StackExhausted",
      src=main_("""    int64:t = raw big(raw v64(3i64));
    exit 10i32;""", """func:big = int64(int64:k) never fails {
    stack int64[1024]:a = [%s];
    a[k] = k;
    pass a[k] + a[1023i64];
};""" % ", ".join(["0i64"] * 1024)),
      wrong="10: the large frame ran, or 139")
