"""M11 claims: BUILTIN_REFERENCE.md, lines 1-447 (the session's own extraction)."""
from m11lib import *

D = "BUILTIN"

# ------------------------------------------------------------------ the preamble
claim("bi0003", D, 3, "available globally without needing to `use`", "rule",
      "Built-ins are callable with no declaration and no import.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    if (string_byte_length(s) != 3i64) { exit 10i32; }
    if (mono_now() < 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="a builtin name unresolved without an import (refused)")
claim("bi0003b", D, 3, "map directly to LLVM instructions or safe runtime shims", "rule",
      "Built-ins map to LLVM instructions or runtime shims.",
      untestable="[vague] a description of the lowering with no outcome a program can check")
claim("bi0005", D, 5, "You must explicitly import them via the `collections` module", "rule",
      "Collections (stacks, lists, hash tables) are not built in: using one without importing the `collections` module is refused.",
      expect="refuse",
      src=main_("""    List<int64>:l = list_init();
    list_push(@l, 5i64);
    if (l.count != 1i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="a List used with no import compiles and runs (the list is the prelude's)")

# ------------------------------------------------------------------ the Views column
claim("bi0010", D, 10, "the 1-based index of the ARGUMENT WHOSE STORAGE THE RESULT", "rule",
      "string_bytes's result aliases its argument: returning the view of a local string is refused as a borrow escaping (D-004 rule 2).",
      expect="refuse",
      src=main_("""    uint8[]:v = raw leak();
    exit 0i32;""", """func:leak = uint8[]() never fails {
    string:s = string_concat("ab", "c");
    pass string_bytes(s);
};"""),
      wrong="accepted: the caller reads freed bytes")
claim("bi0017", D, 17, "rule A (laundered through a call)", "rule",
      "A view laundered through a call (rule A) is still a borrow of its root: returning it from the root's function is refused.",
      expect="refuse",
      src=main_("""    uint8[]:v = raw leak();
    exit 0i32;""", """func:id = uint8[](uint8[]:b) never fails { pass b; };
func:leak = uint8[]() never fails {
    string:s = string_concat("ab", "c");
    pass raw id(string_bytes(s));
};"""),
      wrong="accepted: the laundered view outlives the string")
claim("bi0018", D, 18, "the range-view `arr[lo...hi]` gets the", "rule",
      "A range view arr[lo...hi] of a local array is a borrow: returning it is refused.",
      expect="refuse",
      src=main_("""    int32[]:v = raw leak();
    exit 0i32;""", """func:leak = int32[]() never fails {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    pass a[0i64...2i64];
};"""),
      wrong="accepted: the view of a dead frame escapes")
claim("bi0019", D, 19, "This column is the ONE authority on aliasing for", "rule",
      "The Views column is the one authority on aliasing for builtins.",
      untestable="[tree] a statement about which table the compiler's generator reads")

# ------------------------------------------------------------------ what is a builtin
claim("bi0024", D, 24, "`<!-- builtins:begin -->` and `<!-- builtins:end -->` markers define the", "rule",
      "The marked regions define the bare-name builtin set, generated into builtins.npk by gen_tables.py.",
      untestable="[tree] a statement about the compiler's generator and source tree")
claim("bi0027", D, 27, "That set is deliberately small (0.8.4)", "rule",
      "The builtin set is the floor, sys and the three comptime-foldable string names; everything else here is nlibc's, imported like any module.",
      untestable="[vague] the set's membership is tested row by row, and the non-builtin names at lines 189-220")
claim("bi0035", D, 35, "One row per builtin, and nothing but rows", "rule",
      "The generator reads only the marked regions' table rows and hard-fails on a missing name.",
      untestable="[tree] the generator's behaviour")
claim("bi0039", D, 39, "`<!-- rtsyms:begin -->` … `<!-- rtsyms:end -->` (§2d) is the OTHER region", "rule",
      "The rtsyms region lists emitter-called symbols that are not builtins and never resolve as names.",
      untestable="[tree] where the table is read; the resolution claim is tested at line 300")

# ------------------------------------------------------------------ D-294, D-296
claim("bi0048", D, 48, "whose name is a row's name in a `builtins` region is", "rule",
      "A module-level function named after a builtin is NITPICK-RESOLVE-001 at its declaration.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    exit 0i32;""", """func:mono_now = int64() never fails { pass 5i64; };"""),
      wrong="accepted: the program's own function silently shadows the clock")
claim("bi0048b", D, 48, "inline module or out", "rule",
      "A `pub` function named after a builtin, inside an inline module, is NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    exit 0i32;""", """mod:inner = {
    pub func:hardware_concurrency = int64() never fails { pass 99i64; };
};"""),
      wrong="accepted inside the inline module")
claim("bi0049", D, 49, "`NITPICK-RESOLVE-001` at the declaration; so is an `extern` block's METHOD of", "rule",
      "An extern block's method named after a builtin is NITPICK-RESOLVE-001.",
      untestable="[tool] an extern block needs a driver interface (MODULE_REFERENCE §5); its spelling is MODULE's claims'")
claim("bi0051", D, 51, "METHOD is exempt", "rule",
      "A method named after a builtin is accepted (it is reached through its receiver).",
      expect="run:0",
      src=main_("""    Box:b = Box{ n: 7i64 };
    if (b.mono_now() != 7i64) { exit 10i32; }
    exit 0i32;""", """struct:Box = { int64:n; };
impl:Box = {
    func:mono_now = int64(Self:self) never fails { pass self.n; };
};"""),
      wrong="refused RESOLVE-001, or the call reaches the clock")
claim("bi0052", D, 52, "a module-level BINDING cannot carry a", "rule",
      "A module-level binding cannot carry a function value (TYPE-035).",
      expect="refuse:NITPICK-TYPE-035",
      src=main_("""    exit 0i32;""", """func:eight = int64() never fails { pass 8i64; };
fixed func int64() never fails:F = eight;"""),
      wrong="accepted: a module binding holding a function value")
claim("bi0054", D, 54, "CALLABLE binding (D-296)", "rule",
      "Inside a function, a local of function type named after a builtin is NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    func int64() never fails:mono_now = eight;
    if ((raw mono_now()) != 8i64) { exit 10i32; }
    exit 0i32;""", """func:eight = int64() never fails { pass 8i64; };"""),
      wrong="accepted: the local shadows the builtin (exit 0 with the local's 8)")
claim("bi0054b", D, 54, "a parameter, a local, a `for` binding or a `pick`", "rule",
      "A function-typed PARAMETER named after a builtin is NITPICK-RESOLVE-001.",
      expect="refuse:NITPICK-RESOLVE-001",
      src=main_("""    if ((raw callit(eight)) != 8i64) { exit 10i32; }
    exit 0i32;""", """func:eight = int64() never fails { pass 8i64; };
func:callit = int64(func int64() never fails:mono_now) never fails { pass (raw mono_now()); };"""),
      wrong="accepted: the parameter shadows the builtin")
claim("bi0057", D, 57, "a binding of any other type may (`int64:read` cannot be", "rule",
      "A binding of a non-function type may take a builtin's name.",
      expect="run:0",
      src=main_("""    int64:read = raw v64(5i64);
    int64:mono_now = read + 1i64;
    if (mono_now != 6i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused RESOLVE-001: the rule reached too far")
claim("bi0058", D, 58, "and so may a function-typed FIELD, which is reached through its", "rule",
      "A function-typed field named after a builtin is accepted, and called through its receiver.",
      expect="run:0",
      src=main_("""    Ops:o = Ops{ mono_now: eight };
    if ((raw (o.mono_now)()) != 8i64) { exit 10i32; }
    exit 0i32;""", """func:eight = int64() never fails { pass 8i64; };
struct:Ops = { func int64() never fails:mono_now; };"""),
      wrong="refused RESOLVE-001: the field is no binding")
claim("bi0060", D, 60, "RESERVES A NAME in every program", "rule",
      "Every row added to a marked region reserves a name in every program.",
      untestable="[tree] a rule for the compiler's maintainers; its consequence is tested at lines 48-58")

# ------------------------------------------------------------------ the Signature column
claim("bi0070", D, 70, "```", "example",
      "The Signature column's grammar: params → type, a param optionally `move`.",
      untestable="[tree] the grammar gen_tables.py reads; the signatures' meaning is tested row by row")
claim("bi0076", D, 76, "The arrow is U+2192", "rule",
      "The signature arrow is U+2192; `->` inside a type is the pointer suffix.",
      untestable="[tree] the document's notation")
claim("bi0077", D, 77, "A memory qualifier (`wild`, `wildx`, `stack`) is", "rule",
      "A memory qualifier is not part of a type: a `wild int8->` value binds to a plain `int8->`.",
      expect="run:0",
      src=main_("""    int8->:p = alloc(16i64);
    <-p = 5i8;
    if ((<-p) != 5i8) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="refused TYPE-007: `wild int8->` and `int8->` differ")
claim("bi0080", D, 80, "`Result<T>` appears exactly when the Fails", "rule",
      "A `never fails` builtin's call types as the bare value: it binds with no unwrap.",
      expect="run:0",
      src=main_("""    int64:n = string_byte_length("abcd");
    int64:t = mono_now();
    if (n != 4i64) { exit 10i32; }
    if (t < 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused: a never-fails builtin typed as a Result")
claim("bi0081", D, 81, "column says the builtin may fail", "rule",
      "A may-fail builtin's call types as Result<T>: binding it to the bare type is refused.",
      expect="refuse",
      src=main_("""    string:s = "hello";
    string:t = string_slice(s, 1i64, 3i64);
    exit 0i32;"""),
      wrong="accepted: the Result's value half used with no check")
claim("bi0082", D, 82, "The generator refuses a row where the two columns", "rule",
      "gen_tables.py refuses a row whose Signature and Fails columns disagree.",
      untestable="[tree] the generator's behaviour")
claim("bi0085", D, 85, "The `**ABI:**` note", "rule",
      "A row's ABI note is the whole vocabulary of symbol departures.",
      untestable="[tree] the document's notation; each row's note is tested where it names an emitted symbol")
claim("bi0090", D, 90, "| `inline` |", "row",
      "`inline`: no floor symbol; string_is_empty lowers to a length compare, with no call.",
      expect=r"ir!:call [^\n]*@npk_string_is_empty",
      src=main_("""    string:s = string_concat("a", "b");
    if (string_is_empty(s)) { exit 10i32; }
    exit 0i32;"""),
      wrong="a call to a floor symbol for string_is_empty")
claim("bi0091", D, 91, "``sym=`@memcpy` ``", "row",
      "`sym=`: the symbol is not @npk_<name>.",
      untestable="[tree] the document's notation; mcpy's symbol is tested at line 133")
claim("bi0092", D, 92, "``ret=`{ ptr, ptr, i64, i64, i64 }` ``", "row",
      "`ret=`: the LLVM return differs from the derived one.",
      untestable="[tree] the document's notation; arena_make's is tested at line 146")
claim("bi0093", D, 93, "``args=`ptr, i32, i64` ``", "row",
      "`args=`: the LLVM arguments differ from the derived ones.",
      untestable="[tree] the document's notation; memset's is tested at line 135")
claim("bi0094", D, 94, "| `envelope` |", "row",
      "`envelope`: a never-fails builtin whose symbol answers { T, i32 }, the value half extracted at the call.",
      untestable="[internal] how a call's return is unpacked; the bare typing it gives is tested at line 80")
claim("bi0096", D, 96, "Everything not noted is DERIVED", "rule",
      "check_runtime_sigs_agree diffs the derived ABI against runtime/npkrt.ll on every harness run.",
      untestable="[tree] the harness's check")

# ------------------------------------------------------------------ the Pure column
claim("bi0105", D, 105, "`pure` body (`NITPICK-TYPE-061`) and a contract expression", "rule",
      "A `pure` body admits the pure rows (string_bytes, string_from_bytes' kin, string_equals, string_byte_length, string_is_empty).",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    if ((raw probe(s)) != 3i64) { exit 10i32; }
    exit 0i32;""", """func:probe = int64(string:s) pure never fails {
    if (string_is_empty(s)) { pass 0i64; }
    if (!(string_equals(s, s))) { pass 1i64; }
    uint8[]:b = string_bytes(s);
    pass string_byte_length(s) + (b.len - b.len);
};"""),
      wrong="refused TYPE-061: a pure row refused in a pure body")
claim("bi0105b", D, 105, "(`NITPICK-TYPE-061`)", "rule",
      "A `pure` body refuses an effect row by name (TYPE-061): int_to_string allocates.",
      expect="refuse:NITPICK-TYPE-061",
      src=main_("""    if ((raw probe(5i64)) != 1i64) { exit 10i32; }
    exit 0i32;""", """func:probe = int64(int64:n) pure never fails {
    string:s = int_to_string(n);
    pass string_byte_length(s);
};"""),
      wrong="accepted: an allocating builtin in a pure body")
claim("bi0106", D, 106, "(`NITPICK-TYPE-060`) admit the `pure` rows and refuse the rest by name", "rule",
      "A contract expression admits a pure row: `requires !string_is_empty(s)` compiles and is checked.",
      expect="run:0",
      src=main_("""    string:s = string_concat("a", "b");
    if ((raw first(s)) != 2i64) { exit 10i32; }
    exit 0i32;""", """func:first = int64(string:s) requires !string_is_empty(s) never fails {
    pass string_byte_length(s);
};"""),
      wrong="refused TYPE-060: a pure row refused in a contract")
claim("bi0106b", D, 106, "and refuse the rest by name", "rule",
      "A contract expression refuses an effect row (TYPE-060): int_to_string in a `requires`.",
      expect="refuse:NITPICK-TYPE-060",
      src=main_("""    if ((raw f(5i64)) != 5i64) { exit 10i32; }
    exit 0i32;""", """func:f = int64(int64:n) requires string_byte_length(int_to_string(n)) > 0i64 never fails {
    pass n;
};"""),
      wrong="accepted: an allocating builtin in a contract")
claim("bi0107", D, 107, "Five rows are `pure`", "rule",
      "string_from_bytes is a pure row: a pure body may call it.",
      expect="run:0",
      src=main_("""    string:s = string_concat("ab", "c");
    if ((raw probe(s)) != 3i64) { exit 10i32; }
    exit 0i32;""", """func:probe = int64(string:s) pure never fails {
    string:v = string_from_bytes(s.ptr, s.len);
    pass v.len;
};"""),
      wrong="refused TYPE-061")
claim("bi0109", D, 109, "Everything that allocates (the allocator family,", "rule",
      "string_concat is an effect row: a pure body calling it is refused TYPE-061.",
      expect="refuse:NITPICK-TYPE-061",
      src=main_("""    if ((raw probe("ab")) != 3i64) { exit 10i32; }
    exit 0i32;""", """func:probe = int64(string:s) pure never fails {
    string:t = string_concat(s, "c");
    pass t.len;
};"""),
      wrong="accepted: an allocating call in a pure body")
claim("bi0112", D, 112, "a descriptor, the clock", "rule",
      "mono_now (the clock) is an effect row: a pure body calling it is refused TYPE-061.",
      expect="refuse:NITPICK-TYPE-061",
      src=main_("""    if ((raw probe()) < 0i64) { exit 10i32; }
    exit 0i32;""", """func:probe = int64() pure never fails {
    pass mono_now();
};"""),
      wrong="accepted: a clock read in a pure body")
claim("bi0115", D, 115, "A row's classification is a claim about its floor body", "rule",
      "A row's Pure classification is a claim about its floor body.",
      untestable="[tree] a statement about the classification's source")

# ------------------------------------------------------------------ §1 the allocator
claim("bi0122", D, 122, "They all return `wild` pointers", "rule",
      "An allocation is unmanaged: a block still live at `exit 0` traps WildLeak (the programmer must free it).",
      expect="trap:WildLeak",
      src=main_("""    wild int8->:p = alloc(16i64);
    <-p = 1i8;
    exit 0i32;"""),
      wrong="exit 0: the leak passes silently")
claim("bi0122b", D, 122, "There is no garbage collector (D-003)", "rule",
      "There is no garbage collector.",
      untestable="[unobservable] an absence; the leak check at line 122 is its consequence")
claim("bi0123", D, 123, "every allocation carries a hidden 16-byte header", "rule",
      "Every allocation carries a hidden 16-byte header: size and a secret-keyed magic word.",
      untestable="[internal] the header's layout; reading below a block is outside every guarantee")
claim("bi0123b", D, 123, "Double-free, corruption, and a foreign or misaligned pointer trap to", "rule",
      "A double free the analysis cannot follow traps to failsafe with -4102 (Unreachable).",
      expect="trap:Unreachable",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = raw same(p);
    dalloc(p);
    dalloc(q);
    exit 0i32;""", """func:same = int8->(int8->:x) never fails { pass x; };"""),
      wrong="exit 0 (the second free accepted), or a crash")
claim("bi0123c", D, 123, "OOM with `-4103`", "rule",
      "An allocation the kernel cannot back traps HeapOom (-4103): 2^47 bytes is legal and fails.",
      expect="trap:HeapOom",
      src=main_("""    wild int8->:p = alloc(raw v64(140737488355328i64));
    dalloc(p);
    exit 0i32;"""),
      wrong="HeapBadRequest, a crash, or success")
claim("bi0123d", D, 123, "a malformed request (negative size", "rule",
      "A negative size is a malformed request: HeapBadRequest (-4104).",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = alloc(raw v64(-1i64));
    dalloc(p);
    exit 0i32;"""),
      wrong="an allocation of 2^64-1 bytes attempted, HeapOom, or success")
claim("bi0123e", D, 123, "checked `calloc` multiply overflow", "rule",
      "A calloc whose count*size overflows is a malformed request: HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = calloc(raw v64(4611686018427387904i64), raw v64(16i64));
    dalloc(p);
    exit 0i32;"""),
      wrong="the product wraps to 0 and a small block is returned (exit 0), or IntOverflow")
claim("bi0123f", D, 123, "`ralloc(p, 0)`", "rule",
      "ralloc(p, 0) is a malformed request: HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = ralloc(p, raw v64(0i64));
    dalloc(q);
    exit 0i32;"""),
      wrong="freed and a null or zero block returned (exit 0)")
claim("bi0123g", D, 123, "bad alignment) with `-4104`", "rule",
      "A bad alignment (not a power of two) is a malformed request: HeapBadRequest.",
      expect="trap:HeapBadRequest",
      src=main_("""    wild int8->:p = aalloc(64i64, raw v64(48i64));
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted and aligned to something")
claim("bi0123h", D, 123, "Double-free of a tracked binding is already a compile-time error (D-119)", "rule",
      "Freeing one binding twice is a compile-time error.",
      expect="refuse",
      src=main_("""    wild int8->:p = alloc(16i64);
    dalloc(p);
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted (and trapping, if at all, only at run time)")
claim("bi0127", D, 127, "| `alloc` |", "row",
      "alloc(0) is a real, unique, freeable block.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(raw v64(0i64));
    wild int8->:q = alloc(raw v64(0i64));
    if (p == q) { exit 10i32; }
    dalloc(p);
    dalloc(q);
    if (wild_live_count() != 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="the same (or a null) pointer twice (10), or a free that traps")
claim("bi0128", D, 128, "| `alloc_managed` |", "row",
      "alloc_managed is prelude-only: a program's call is refused TYPE-054.",
      expect="refuse:NITPICK-TYPE-054",
      src=main_("""    wild int8->:p = alloc_managed(16i64);
    exit 0i32;"""),
      wrong="accepted: a program allocates storage D-151's count does not see")
claim("bi0129", D, 129, "| `aalloc` |", "row",
      "aalloc allocates with a requested power-of-two alignment; the block is usable and freeable.",
      expect="run:0",
      src=main_("""    wild int8->:p = aalloc(256i64, raw v64(64i64));
    wild int64->:w = p =>! wild int64->;
    <-w = 77i64;
    if ((<-w) != 77i64) { exit 10i32; }
    dalloc(p);
    if (wild_live_count() != 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="a trap for a legal alignment, or a block the counter does not release")
claim("bi0130", D, 130, "| `calloc` |", "row",
      "calloc allocates count*size ZERO-initialised bytes.",
      expect="run:0",
      src=main_("""    wild int8->:d = alloc(64i64);
    wild uint8->:du = d =>! wild uint8->;
    int64:i = 0i64;
    while (i < 64i64) decreases 64i64 - i { du[i] = 255u8; i = i + 1i64; }
    dalloc(d);
    wild int8->:p = calloc(raw v64(8i64), raw v64(8i64));
    wild uint8->:u = p =>! wild uint8->;
    int64:j = 0i64;
    while (j < 64i64) decreases 64i64 - j {
        if (u[j] != 0u8) { exit 10i32; }
        j = j + 1i64;
    }
    dalloc(p);
    exit 0i32;"""),
      wrong="a reused block's old bytes (10)")
claim("bi0131", D, 131, "| `ralloc` |", "row",
      "ralloc resizes and copies the old contents (bounded by the old size); ralloc(NULL, n) is a fresh allocation.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(8i64);
    wild uint8->:u = p =>! wild uint8->;
    int64:i = 0i64;
    while (i < 8i64) decreases 8i64 - i { u[i] = ((i + 1i64) =>! uint8); i = i + 1i64; }
    wild int8->:q = ralloc(p, raw v64(4096i64));
    wild uint8->:w = q =>! wild uint8->;
    int64:j = 0i64;
    while (j < 8i64) decreases 8i64 - j {
        if (w[j] != ((j + 1i64) =>! uint8)) { exit 10i32; }
        j = j + 1i64;
    }
    dalloc(q);
    wild int8->:f = ralloc(NULL, raw v64(32i64));
    <-f = 3i8;
    dalloc(f);
    if (wild_live_count() != 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="the contents lost in the move (10), or ralloc(NULL, n) trapping")
claim("bi0132", D, 132, "| `dalloc` |", "row",
      "dalloc(NULL) traps -4102 (Unreachable).",
      expect="trap:Unreachable",
      src=main_("""    dalloc(NULL);
    exit 0i32;"""),
      wrong="a C-style no-op free(NULL) (exit 0)")
claim("bi0133", D, 133, "| `mcpy` |", "row",
      "mcpy copies n bytes from src to dst.",
      expect="run:0",
      src=main_("""    wild int8->:a = calloc(16i64, 1i64);
    wild int8->:b = calloc(16i64, 1i64);
    wild uint8->:ua = a =>! wild uint8->;
    wild uint8->:ub = b =>! wild uint8->;
    ua[0i64] = 1u8; ua[5i64] = 6u8; ua[9i64] = 10u8;
    wild int8->:r = mcpy(b, a, raw v64(6i64));
    if (ub[0i64] != 1u8) { exit 10i32; }
    if (ub[5i64] != 6u8) { exit 11i32; }
    if (ub[9i64] != 0u8) { exit 12i32; }
    dalloc(a);
    dalloc(b);
    exit 0i32;"""),
      wrong="bytes past n copied (12), or none (10)")
claim("bi0133b", D, 133, "**ABI:** sym=`@memcpy`", "row",
      "mcpy's symbol is @memcpy.",
      expect=r"ir:@memcpy\b|@llvm\.memcpy",
      src=main_("""    wild int8->:a = calloc(16i64, 1i64);
    wild int8->:b = calloc(16i64, 1i64);
    wild int8->:r = mcpy(b, a, raw v64(6i64));
    dalloc(a);
    dalloc(b);
    exit 0i32;"""),
      wrong="a call to @npk_mcpy")
claim("bi0134", D, 134, "| `mmov` |", "row",
      "mmov is overlap-safe: moving bytes 0..7 to 1..8 in one block keeps them in order.",
      expect="run:0",
      src=main_("""    wild int8->:a = calloc(16i64, 1i64);
    wild uint8->:u = a =>! wild uint8->;
    int64:i = 0i64;
    while (i < 8i64) decreases 8i64 - i { u[i] = ((i + 1i64) =>! uint8); i = i + 1i64; }
    wild int8->:d = #ptr_add<int8>(a, 1i64);
    wild int8->:r = mmov(d, a, raw v64(8i64));
    int64:j = 0i64;
    while (j < 8i64) decreases 8i64 - j {
        if (u[j + 1i64] != ((j + 1i64) =>! uint8)) { exit 10i32; }
        j = j + 1i64;
    }
    dalloc(a);
    exit 0i32;"""),
      wrong="a forward copy smearing the first byte (10)")
claim("bi0134b", D, 134, "**ABI:** sym=`@memmove`", "row",
      "mmov's symbol is @memmove.",
      expect=r"ir:@memmove\b|@llvm\.memmove",
      src=main_("""    wild int8->:a = calloc(16i64, 1i64);
    wild int8->:d = #ptr_add<int8>(a, 1i64);
    wild int8->:r = mmov(d, a, raw v64(8i64));
    dalloc(a);
    exit 0i32;"""),
      wrong="a call to @npk_mmov")
claim("bi0135", D, 135, "| `memset` |", "row",
      "memset fills n bytes with the LOW 8 bits of val.",
      expect="run:0",
      src=main_("""    wild int8->:a = calloc(8i64, 1i64);
    wild uint8->:u = a =>! wild uint8->;
    wild int8->:r = memset(a, raw v64(511i64), raw v64(4i64));
    if (u[0i64] != 255u8) { exit 10i32; }
    if (u[3i64] != 255u8) { exit 11i32; }
    if (u[4i64] != 0u8) { exit 12i32; }
    dalloc(a);
    exit 0i32;"""),
      wrong="a value other than the low byte (10), or past n (12)")
claim("bi0135b", D, 135, "**ABI:** sym=`@memset` args=`ptr, i32, i64`", "row",
      "memset's symbol is @memset (or the llvm.memset intrinsic it maps to).",
      expect=r"ir:@memset\b|@llvm\.memset",
      src=main_("""    wild int8->:a = calloc(8i64, 1i64);
    wild int8->:r = memset(a, raw v64(7i64), raw v64(4i64));
    dalloc(a);
    exit 0i32;"""),
      wrong="a call to @npk_memset")

# ------------------------------------------------------------------ arenas, wild tracking, W^X
claim("bi0146", D, 146, "| `arena_make` |", "row",
      "arena_make builds an arena for T from the annotation, with no element-type argument.",
      expect="run:0",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    a.put(h, 42i64) ?! E1;
    int64:v = a.get(h) ?! E2;
    if (v != 42i64) { exit 10i32; }
    exit 0i32;""", "error:E1;\nerror:E2;"),
      wrong="refused: the element type demanded as an argument")
claim("bi0146b", D, 146, "ret=`{ ptr, ptr, i64, i64, i64 }` args=`i64, i64`", "row",
      "arena_make's symbol is @npk_arena_make, returning { ptr, ptr, i64, i64, i64 } from (i64, i64).",
      expect=r"ir:\{ ptr, ptr, i64, i64, i64 \} @npk_arena_make\(i64[^,)]*, i64[^,)]*\)",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    exit 0i32;"""),
      wrong="another symbol or shape")
claim("bi0147", D, 147, "| `shared_arena_make` |", "row",
      "shared_arena_make builds the atomically-shared arena from the annotation.",
      expect="run:0",
      src=main_("""    shared_arena<int64>:a = shared_arena_make(4i64);
    exit 0i32;"""),
      wrong="refused")
claim("bi0148", D, 148, "| `atomic_from_ptr` |", "row",
      "atomic_from_ptr::<T> aliases existing wild memory as an atomic, used as a method's receiver.",
      expect="run:0",
      src=main_("""    wild int8->:buf = alloc(16i64);
    wild int64->:cell = buf =>! wild int64->;
    <-cell = 41i64;
    int64:v = atomic_from_ptr::<int64>(cell).load();
    if (v != 41i64) { exit 10i32; }
    dalloc(buf);
    exit 0i32;"""),
      wrong="refused, or the load reads something else")
claim("bi0148b", D, 148, "a declaration or assignment storing the result is refused (TYPE-007)", "row",
      "Storing atomic_from_ptr's result in a declaration is refused TYPE-007.",
      expect="refuse:NITPICK-TYPE-007",
      src=main_("""    wild int8->:buf = alloc(16i64);
    wild int64->:cell = buf =>! wild int64->;
    atomic<int64>:a = atomic_from_ptr::<int64>(cell);
    dalloc(buf);
    exit 0i32;"""),
      wrong="accepted: an aliased atomic stored")
claim("bi0148c", D, 148, "**`wild`-context only** (D-187)", "row",
      "atomic_from_ptr is wild-context only: over the address of a plain local it is refused.",
      expect="refuse",
      src=main_("""    int64:x = 41i64;
    int64:v = atomic_from_ptr::<int64>(@x).load();
    if (v != 41i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: an atomic alias over managed storage")
claim("bi0149", D, 149, "| `wild_live_count` |", "row",
      "wild_live_count is the number of live wild allocations.",
      expect="run:0",
      src=main_("""    int64:n0 = wild_live_count();
    wild int8->:p = alloc(8i64);
    wild int8->:q = alloc(8i64);
    if (wild_live_count() != n0 + 2i64) { exit 10i32; }
    dalloc(p);
    if (wild_live_count() != n0 + 1i64) { exit 11i32; }
    dalloc(q);
    if (wild_live_count() != n0) { exit 12i32; }
    exit 0i32;"""),
      wrong="a count that does not follow alloc/dalloc")
claim("bi0150", D, 150, "| `clone_exec` |", "row",
      "clone_exec refuses a child-bound descriptor below 4 with an error, before anything is claimed.",
      expect="run:0",
      src=main_("""    wild int8->:blk = calloc(10i64, 8i64);
    Result<int64>:r = clone_exec(blk);
    if (!r.is_error) { exit 10i32; }
    dalloc(blk);
    exit 0i32;"""),
      wrong="a child spawned with descriptors 0/0/0 (10), or a trap")
claim("bi0151", D, 151, "| `driver_retire` |", "row",
      "Retiring a registry slot that is not active traps -4102 (Unreachable).",
      expect="trap:Unreachable",
      src=main_("""    driver_retire(raw v64(5i64));
    exit 0i32;"""),
      wrong="a silent no-op (exit 0)")
claim("bi0152", D, 152, "| `wild_release_all` |", "row",
      "The statement after wild_release_all() must be `exit`: anything else is TYPE-062.",
      expect="refuse:NITPICK-TYPE-062",
      src=main_("""    wild_release_all();
    int32:x = raw v32(0i32);
    exit x;"""),
      wrong="accepted: a statement runs after the release")
claim("bi0152b", D, 152, "`argv` and `environ()`'s arrays live outside it (1.5.1b step 0)", "row",
      "wild_release_all followed by exit is legal, and argv and environ() stay readable after it.",
      expect="run:0",
      src="""func:after = int32(cstring[]:argv, int64:n) never fails {
    if (argv.len != n) { pass 10i32; }
    if (argv[0i64].len == 0i64) { pass 11i32; }
    cstring[]:env = environ();
    if (env.len != 0i64) { pass 12i32; }
    pass 0i32;
};

func:main = int32(cstring[]:argv) {
    int64:n = argv.len;
    wild int8->:p = alloc(64i64);
    wild_release_all();
    exit (raw after(argv, n));
};
""",
      wrong="a fault reading argv after the release")
claim("bi0153", D, 153, "| `wildx_alloc` |", "row",
      "wildx_alloc gives writable pages; filled with code, sealed and called, the code runs.",
      expect="run:0",
      src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 72u8;
    page[1i64] = 141u8;
    page[2i64] = 71u8;
    page[3i64] = 1u8;
    page[4i64] = 195u8;
    wildx_seal(page);
    int64:r = wildx_call(page, raw v64(41i64));
    wildx_free(page);
    if (r != 42i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="the call returns something else (10), or faults")
claim("bi0154", D, 154, "| `wildx_seal` |", "row",
      "After wildx_seal the pages are not writable: a store faults (MachineFault).",
      expect="trap:MachineFault",
      src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    wildx_seal(page);
    page[1i64] = 195u8;
    wildx_free(page);
    exit 0i32;"""),
      wrong="the store succeeds (exit 0): writable and executable at once")
claim("bi0155", D, 155, "| `wildx_call` |", "row",
      "wildx_call passes its int64 argument to the sealed code and returns its int64 result.",
      expect="run:0",
      src=main_("""    wildx uint8->:page = wildx_alloc(16i64) =>! wildx uint8->;
    page[0i64] = 72u8;
    page[1i64] = 137u8;
    page[2i64] = 248u8;
    page[3i64] = 195u8;
    wildx_seal(page);
    int64:r = wildx_call(page, raw v64(-9i64));
    wildx_free(page);
    if (r != -9i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="the argument or result lost or truncated (10)")
claim("bi0156", D, 156, "| `wildx_free` |", "row",
      "wildx_free releases W^X pages; the program then exits cleanly.",
      expect="run:0",
      src=main_("""    wildx uint8->:page = wildx_alloc(4096i64) =>! wildx uint8->;
    page[0i64] = 195u8;
    wildx_seal(page);
    wildx_free(page);
    exit 0i32;"""),
      wrong="a trap at free or at exit")
claim("bi0160", D, 160, "`malloc` and `free` are not builtins and are not aliases", "rule",
      "`malloc` is not a builtin: a call to it is refused.",
      expect="refuse",
      src=main_("""    wild int8->:p = malloc(16i64);
    exit 0i32;"""),
      wrong="accepted as an alias of alloc")
claim("bi0160b", D, 160, "and are not aliases", "rule",
      "`free` is not a builtin: a call to it is refused.",
      expect="refuse",
      src=main_("""    wild int8->:p = alloc(16i64);
    free(p);
    exit 0i32;"""),
      wrong="accepted as an alias of dalloc")
claim("bi0162", D, 162, "there is no `extern \"libc\"` to declare them in", "rule",
      "In-process FFI does not exist: an `extern \"libc\"` block is refused.",
      expect="refuse",
      src=main_("""    exit 0i32;""", """extern "libc" {
    func:malloc = wild int8->(int64:n);
};"""),
      wrong="accepted")
claim("bi0163", D, 163, "the WHOLE allocator API", "rule",
      "The natives above are the whole allocator API (five since aalloc).",
      untestable="[unobservable] an absence; malloc and free are tested at line 160")

# ------------------------------------------------------------------ §2 nlibc's planned surface
claim("bi0173", D, 173, "Everything in this section arrives as ordinary Nitpick functions in", "rule",
      "§2's string functions are nlibc's ordinary functions, not builtins (bar §2c's three).",
      untestable="[vague] tested name by name at lines 189-220")
claim("bi0180", D, 180, "UNCLAIMED today", "rule",
      "No library in the ecosystem builds the nlibc string surface.",
      untestable="[tree] a statement about the ecosystem's libraries")
claim("bi0181", D, 181, "None of these names resolves", "rule",
      "None of §2's names resolves unless it also has a row in a marked table.",
      untestable="[vague] tested name by name at lines 189-220")

_UNRESOLVED = [  # (line, quote, name, call)
    (189, "`string_length(str)`", "string_length", "string_length(s)"),
    (191, "`string_char_count(str)`", "string_char_count", "string_char_count(s)"),
    (193, "`string_is_valid_utf8(str)`", "string_is_valid_utf8", "string_is_valid_utf8(s)"),
    (197, "`string_contains(str, needle)`", "string_contains", "string_contains(s, \"b\")"),
    (198, "`string_starts_with(str, prefix)`", "string_starts_with", "string_starts_with(s, \"a\")"),
    (199, "`string_ends_with(str, suffix)`", "string_ends_with", "string_ends_with(s, \"c\")"),
    (200, "`string_index_of(str, needle)`", "string_index_of", "string_index_of(s, \"b\")"),
    (201, "`string_last_index_of(str, needle)`", "string_last_index_of", "string_last_index_of(s, \"b\")"),
    (205, "`string_substring(str, start, end)`", "string_substring", "string_substring(s, 0i64, 1i64)"),
    (206, "`string_count(str, needle)`", "string_count", "string_count(s, \"b\")"),
    (207, "`string_replace(str, needle, replacement)`", "string_replace", "string_replace(s, \"b\", \"x\")"),
    (208, "`string_repeat(str, n)`", "string_repeat", "string_repeat(s, 2i64)"),
    (211, "`string_trim(str)`", "string_trim", "string_trim(s)"),
    (212, "`string_trim_start(str)`", "string_trim_start", "string_trim_start(s)"),
    (213, "`string_to_upper(str)`", "string_to_upper", "string_to_upper(s)"),
    (214, "`string_pad_left(str, len, char)`", "string_pad_left", "string_pad_left(s, 5i64, s)"),
    (217, "`string_from_int(val)`", "string_from_int", "string_from_int(5i64)"),
    (218, "`string_from_int_hex(val)`", "string_from_int_hex", "string_from_int_hex(255i64)"),
    (219, "`string_from_char(byte)`", "string_from_char", "string_from_char(97u8)"),
    (220, "`string_format_float(val, precision)`", "string_format_float", "string_format_float(1.5f64, 2i64)"),
]
for ln, q, name, call in _UNRESOLVED:
    claim("bi%04d" % ln, D, ln, q, "rule",
          "`%s` is planned nlibc surface with no row in a marked table: it does not resolve (line 181)." % name,
          expect="refuse",
          src=main_("""    string:s = string_concat("ab", "c");
    discard(%s);
    exit 0i32;""" % call),
          wrong="accepted: the name resolves as a builtin")
for ln, q, name, call in [(212, "`string_trim_end(str)`", "string_trim_end", "string_trim_end(s)"),
                          (213, "`string_to_lower(str)`", "string_to_lower", "string_to_lower(s)"),
                          (214, "`string_pad_right(str, len, char)`", "string_pad_right", "string_pad_right(s, 5i64, s)"),
                          (217, "`string_to_int(str)`", "string_to_int", "string_to_int(s)")]:
    claim("bi%04db" % ln, D, ln, q, "rule",
          "`%s` is planned nlibc surface with no row in a marked table: it does not resolve (line 181)." % name,
          expect="refuse",
          src=main_("""    string:s = string_concat("ab", "c");
    discard(%s);
    exit 0i32;""" % call),
          wrong="accepted: the name resolves as a builtin")
claim("bi0190", D, 190, "`string_byte_length(str)`", "rule",
      "string_byte_length (a row of §2c) resolves and is the byte length: \"héllo\" is 6 bytes.",
      expect="run:0",
      src=main_("""    string:s = string_concat("h", "éllo");
    if (string_byte_length(s) != 6i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="5 (a codepoint count) (10), or refused")
claim("bi0192", D, 192, "`string_is_empty(str)`", "rule",
      "string_is_empty (a row of §2c) is true exactly when the length is 0.",
      expect="run:0",
      src=main_("""    string:e = string_concat("", "");
    string:f = string_concat("", "x");
    if (!(string_is_empty(e))) { exit 10i32; }
    if (string_is_empty(f)) { exit 11i32; }
    exit 0i32;"""),
      wrong="a wrong answer for either (10, 11), or refused")
claim("bi0196", D, 196, "`string_equals(a, b)`", "rule",
      "string_equals is a byte-equal comparison.", m10="t17_string_equals")
claim("bi0204", D, 204, "`string_concat(a, b)`", "rule",
      "string_concat (a row of §2b) concatenates two strings.",
      expect="run:0",
      src=main_("""    string:a = string_concat("ab", "");
    string:c = string_concat(a, "cd");
    if (!(string_equals(c, "abcd"))) { exit 10i32; }
    exit 0i32;"""),
      wrong="another result (10), or refused")

# ------------------------------------------------------------------ §2b the floor
claim("bi0228", D, 228, "The functions `runtime/npkrt.ll` defines and every backend rung can", "rule",
      "The floor's functions are bare-name builtins, callable everywhere with no declaration.",
      untestable="[vague] tested row by row below")
claim("bi0234", D, 234, "`check_runtime_sigs_agree` diffs all three on every harness run", "rule",
      "Three copies of the floor's signature set exist and check_runtime_sigs_agree diffs them.",
      untestable="[tree] the compiler's source tree and harness")
claim("bi0238", D, 238, "| `string_concat` |", "row",
      "string_concat concatenates; an empty result allocates nothing.", m10="t15_concat_empty")
claim("bi0238b", D, 238, "also comptime-folds", "row",
      "string_concat folds at compile time: it initialises a module `fixed` string.",
      expect="run:0",
      src=main_("""    if (!(string_equals(AB, "ab"))) { exit 10i32; }
    exit 0i32;""", """fixed string:AB = string_concat("a", "b");"""),
      wrong="refused as a non-constant initialiser, or another value")
claim("bi0239", D, 239, "| `int_to_string` |", "row",
      "int_to_string renders an int64 in decimal and never fails.", m10="t10_int_to_string")
claim("bi0240", D, 240, "| `string_slice` |", "row",
      "string_slice is byte-indexed and half-open.", m10="t05_slice_half_open")
claim("bi0240b", D, 240, "**an OWNED COPY** (D-186)", "row",
      "string_slice returns an owned copy: the slice outlives the string it was cut from.",
      expect="run:0",
      src=main_("""    string:t = raw cut();
    if (!(string_equals(t, "el"))) { exit 10i32; }
    exit 0i32;""", """func:cut = string() never fails {
    string:s = string_concat("hel", "lo");
    string:t = string_slice(s, 1i64, 3i64) ?| "X";
    pass t;
};"""),
      wrong="a view: refused as an escaping borrow, or the bytes read freed (10)")
claim("bi0240c", D, 240, "An empty slice allocates nothing", "row",
      "An empty slice allocates nothing.",
      expect="run:0", heap="0/0/0",
      src=main_("""    string:t = string_slice("hello", raw v64(2i64), raw v64(2i64)) ?| "X";
    if (t.len != 0i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="a block allocated for the empty result (count 1)")
claim("bi0241", D, 241, "| `string_bytes` |", "row",
      "string_bytes is the string's bytes as a view: same length, same bytes, no copy (no allocation).",
      expect="run:0", heap="*/*/1",
      src=main_("""    string:s = string_concat("ab", raw tail());
    uint8[]:b = string_bytes(s);
    if (b.len != s.len) { exit 10i32; }
    if (b[0i64] != 97u8) { exit 11i32; }
    if (b[2i64] != 99u8) { exit 12i32; }
    exit 0i32;""", """func:tail = string() never fails { pass "c"; };"""),
      wrong="a copy (count 2), or another length or byte")
claim("bi0241b", D, 241, "The slice is a borrow (D-070)", "row",
      "The bytes view is bounds-checked against its run-time length.", m10="t07_bytes_view_bounds")
claim("bi0242", D, 242, "| `string_from_bytes` |", "row",
      "string_from_bytes' length is held to [0, 2^47]: a negative length traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    wild int8->:p = alloc(16i64);
    string:s = string_from_bytes(p, raw v64(-1i64));
    if (s.len == 7i64) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="a string of length 2^64-1 (a huge view), exit 0")
claim("bi0242b", D, 242, "wraps existing bytes as a view (cap 0)", "row",
      "string_from_bytes wraps existing bytes as a view with cap 0, the bytes the pointer names.",
      expect="run:0",
      src=main_("""    wild int8->:p = calloc(4i64, 1i64);
    wild uint8->:u = p =>! wild uint8->;
    u[0i64] = 104u8; u[1i64] = 105u8;
    string:s = string_from_bytes(p, raw v64(2i64));
    if (s.cap != 0i64) { exit 10i32; }
    if (!(string_equals(s, "hi"))) { exit 11i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="an owning copy (cap > 0) (10), or other bytes (11)")
claim("bi0242c", D, 242, "the length is held to `[0, 2^47]`", "row",
      "A length above 2^47 traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    wild int8->:p = alloc(16i64);
    string:s = string_from_bytes(p, raw v64(140737488355329i64));
    if (s.len == 7i64) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="accepted (exit 0)")
claim("bi0243", D, 243, "| `to_cstring` |", "row",
      "to_cstring is a NUL-terminated copy: the length excludes the NUL, which follows the bytes.",
      expect="run:0",
      src=main_("""    cstring:c = to_cstring("abc") ?! E1;
    if (c.len != 3i64) { exit 10i32; }
    wild uint8->:u = c.ptr =>! wild uint8->;
    if (u[0i64] != 97u8) { exit 11i32; }
    if (u[3i64] != 0u8) { exit 12i32; }
    exit 0i32;""", "error:E1;"),
      wrong="a length counting the NUL (10), or no terminator (12)")
claim("bi0244", D, 244, "| `read_file` |", "row",
      "read_file reads a whole file.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("rf.tmp") ?! E1;
    Result<NIL>:w = write_file(p, "0123456789abcdef");
    if (w.is_error) { exit 10i32; }
    Result<string>:r = read_file(p);
    if (r.is_error) { exit 11i32; }
    string:s = move(r.value);
    if (!(string_equals(s, "0123456789abcdef"))) { exit 12i32; }
    exit 0i32;""", "error:E1;"),
      wrong="a partial or failed read (11, 12)")
claim("bi0245", D, 245, "| `read_stdin` |", "row",
      "read_stdin reads the whole stream: an empty stdin gives an empty string, successfully.",
      expect="run:0",
      src=main_("""    Result<string>:r = read_stdin();
    if (r.is_error) { exit 10i32; }
    string:s = move(r.value);
    if (s.len != 0i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="end of input as an error (10)")
claim("bi0246", D, 246, "| `environ` |", "row",
      "environ() is the process environment's KEY=VALUE entries: under an empty environment it is empty.",
      expect="run:0",
      src=main_("""    cstring[]:env = environ();
    if (env.len != 0i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="entries that are not the process's (10)")
claim("bi0247", D, 247, "| `path_exists` |", "row",
      "path_exists never fails: an existing path answers true, a missing one false.",
      expect="run:0",
      src=main_("""    cstring:root = to_cstring("/") ?! E1;
    cstring:none = to_cstring("/m11_no_such_path_here") ?! E1;
    if (!(path_exists(root))) { exit 10i32; }
    if (path_exists(none)) { exit 11i32; }
    exit 0i32;""", "error:E1;"),
      wrong="a wrong answer (10, 11)")
claim("bi0248", D, 248, "| `mono_now` |", "row",
      "mono_now is CLOCK_MONOTONIC nanoseconds: it never goes backwards.",
      expect="run:0",
      src=main_("""    int64:a = mono_now();
    int64:b = mono_now();
    if (a < 0i64) { exit 10i32; }
    if (b < a) { exit 11i32; }
    exit 0i32;"""),
      wrong="a clock that goes backwards (11)")
claim("bi0249", D, 249, "| `hardware_concurrency` |", "row",
      "hardware_concurrency is at least 1 and at most 1024.",
      expect="run:0",
      src=main_("""    int64:n = hardware_concurrency();
    if (n < 1i64) { exit 10i32; }
    if (n > 1024i64) { exit 11i32; }
    exit 0i32;"""),
      wrong="0 or a popcount of garbage (DEF-52's 1008)")
claim("bi0249b", D, 249, "Asked at each call, never cached", "row",
      "hardware_concurrency follows the affinity mask at each call: pinned to one CPU it answers 1.",
      expect="run:0",
      src=main_("""    wild int8->:m = calloc(1i64, 8i64);
    wild uint8->:u = m =>! wild uint8->;
    u[0i64] = 1u8;
    int64:before = hardware_concurrency();
    Result<int64>:r = sys(203i64, 0i64, 8i64, m);
    if (r.is_error) { exit 10i32; }
    if (hardware_concurrency() != 1i64) { exit 11i32; }
    dalloc(m);
    if (before < 1i64) { exit 12i32; }
    exit 0i32;"""),
      wrong="a cached answer (11)")
claim("bi0250", D, 250, "| `buffer_new` |", "row",
      "buffer_new(n) is n zeroed bytes with len == cap == n; n <= 0 is the empty buffer.",
      expect="run:0",
      src=main_("""    buffer:b = buffer_new(raw v64(16i64));
    if (b.len != 16i64) { exit 10i32; }
    if (b.cap != 16i64) { exit 11i32; }
    if (b.ptr[15i64] != 0u8) { exit 12i32; }
    buffer:e = buffer_new(raw v64(-3i64));
    if (e.len != 0i64) { exit 13i32; }
    if (e.cap != 0i64) { exit 14i32; }
    exit 0i32;"""),
      wrong="a nonzero byte (12), or an error or trap for n <= 0")
claim("bi0250b", D, 250, "the cell drops at scope exit exactly as a string does", "row",
      "A buffer drops at scope exit: 1000 buffers of 1000 bytes made in turn peak at 1000 live bytes.",
      expect="run:0", heap="1000000/1000/1000",
      src=main_("""    int64:i = 0i64;
    while (i < 1000i64) decreases 1000i64 - i {
        drop mk();
        i = i + 1i64;
    }
    exit 0i32;""", """func:mk = NIL() {
    buffer:b = buffer_new(raw v64(1000i64));
    if (b.len != 1000i64) { pass NIL; }
    pass NIL;
};"""),
      wrong="never dropped (peak 1000000)")
claim("bi0251", D, 251, "| `channel` |", "row",
      "channel() reads element, level and capacity from the annotation and returns a Result.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    Channel<int32, 4i32, 8i64>:ch = channel() ?! E1;
    await ch.send(5i32, raw duration_ms(500i64)) ?! E1;
    int32:v = await ch.recv(raw duration_ms(500i64)) ?! E1;
    if (v != 5i32) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="another value (10), or refused")
claim("bi0251b", D, 251, "Allocates, so it returns a `Result`", "row",
      "channel() returns a Result: binding it bare is refused.",
      expect="refuse",
      src="""async func:main = int32(cstring[]:_~argv) {
    Channel<int32, 4i32, 8i64>:ch = channel();
    exit 0i32;
};
""",
      wrong="accepted: the Result used as a channel")
claim("bi0252", D, 252, "| `mutex` |", "row",
      "mutex(v) builds a Mutex from the annotation holding v, as a Result.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    Mutex<int32, 3i32>:m = mutex(7i32) ?! E1;
    Guard<int32>:g = await m.acquire(raw duration_ms(500i64)) ?! E1;
    if (g.value != 7i32) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="another value (10), or refused")
claim("bi0253", D, 253, "| `rwlock` |", "row",
      "rwlock(v) builds an RwLock holding v: a reader sees v.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    RwLock<int32, 3i32>:r = rwlock(7i32) ?! E1;
    RGuard<int32>:g = await r.read(raw duration_ms(500i64)) ?! E1;
    if (g.value != 7i32) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="another value (10), or refused")
claim("bi0254", D, 254, "| `condvar` |", "row",
      "condvar() builds a CondVar from the annotation, as a Result.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    CondVar<4i32>:cv = condvar() ?! E1;
    exit 0i32;
};
""",
      wrong="refused")
claim("bi0255", D, 255, "| `barrier` |", "row",
      "barrier() builds a Barrier of N arrivals from the annotation: with N = 1 one arrival passes.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    Barrier<1i32, 6i32>:b = barrier() ?! E1;
    await b.arrive(raw duration_ms(500i64)) ?! E1;
    exit 0i32;
};
""",
      wrong="the one arrival waits for a second (a timeout, exit 81)")
claim("bi0256", D, 256, "| `suspend_until` |", "row",
      "suspend_until is legal only inside an async function: in a sync function it is refused.",
      expect="refuse",
      src=main_("""    suspend_until(mono_now() + 1000000i64);
    exit 0i32;"""),
      wrong="accepted in a sync body")
claim("bi0256b", D, 256, "parks the TASK until an absolute monotonic timepoint", "row",
      "suspend_until parks the task until the deadline: at least that long passes.",
      expect="run:0",
      src="""async func:main = int32(cstring[]:_~argv) {
    int64:t0 = mono_now();
    suspend_until(t0 + 20000000i64);
    if ((mono_now() - t0) < 20000000i64) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="it returns early (10)")
claim("bi0257", D, 257, "| `suspend_io` |", "row",
      "suspend_io parks until the descriptor is ready or the deadline: a readable descriptor returns before a far deadline.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    int64:t0 = mono_now();
    suspend_io(f => int32, 1i32, t0 + 5000000000i64);
    io_unwatch(f => int32);
    if ((mono_now() - t0) > 4000000000i64) { exit 10i32; }
    drop close(f);
    exit 0i32;
};
""",
      wrong="it waits to the deadline (10)")
claim("bi0258", D, 258, "| `io_unwatch` |", "row",
      "Removing an unwatched descriptor is a no-op, not an error.",
      expect="run:0",
      src="""async func:main = int32(cstring[]:_~argv) {
    io_unwatch(0i32);
    io_unwatch(0i32);
    exit 0i32;
};
""",
      wrong="a trap or an error")
claim("bi0259", D, 259, "| `io_watch` |", "row",
      "io_watch registers a descriptor without parking; it is then unwatched.",
      expect="run:0",
      src="""error:E1;

async func:main = int32(cstring[]:_~argv) {
    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    io_watch(f => int32, 1i32);
    io_unwatch(f => int32);
    drop close(f);
    exit 0i32;
};
""",
      wrong="the call parks, or traps")
claim("bi0260", D, 260, "| `own_fd` |", "row",
      "own_fd takes ownership: the owner's drop closes the descriptor.",
      expect="run:0",
      src="""error:E1;

func:hold = NIL(fd:f) {
    OwnedFd:o = own_fd(f);
    pass NIL;
};

func:main = int32(cstring[]:_~argv) {
    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    drop hold(f);
    Result<NIL>:c = close(f);
    if (!c.is_error) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="the descriptor left open by the owner's drop (10)")
claim("bi0261", D, 261, "| `release_fd` |", "row",
      "close(release_fd(move o)) consumes the owner and closes once, reporting close's verdict.",
      expect="run:0",
      src="""error:E1;

func:main = int32(cstring[]:_~argv) {
    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    OwnedFd:o = own_fd(f);
    Result<NIL>:c = close(release_fd(move o));
    if (c.is_error) { exit 10i32; }
    exit 0i32;
};
""",
      wrong="a double close (a failed verdict, 10), or the spelling refused")
claim("bi0261b", D, 261, "the move defuses the drop, so no double close is", "row",
      "After release_fd(move o), `o` is moved: a use of it is refused.",
      expect="refuse",
      src="""error:E1;

func:main = int32(cstring[]:_~argv) {
    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    OwnedFd:o = own_fd(f);
    fd:g = release_fd(move(o));
    fd:h = release_fd(move(o));
    exit 0i32;
};
""",
      wrong="accepted: the owner released twice")
claim("bi0262", D, 262, "| `chain_depth` |", "row",
      "chain_depth counts the sites the in-flight error's origin chain has passed.",
      expect="run:0", fs=False,
      src="""error:E1;

func:leaf = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};
func:mid = int32(int32:v) {
    pass (relay leaf(v)) + 1i32;
};

func:main = int32(cstring[]:_~argv) {
    int32:r = mid(raw v32(1i32)) ?! E1;
    exit 50i32;
};

""" + failsafe_with("""        (E1) { if (chain_depth() != 3i32) { exit (10i32 + chain_depth()); } exit 0i32; },"""),
      wrong="another depth (10+depth)")
claim("bi0263", D, 263, "| `chain_site` |", "row",
      "chain_site(i) is 0 outside the kept range.",
      expect="run:0", fs=False,
      src="""error:E1;

func:leaf = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};

func:main = int32(cstring[]:_~argv) {
    int32:r = leaf(raw v32(1i32)) ?! E1;
    exit 50i32;
};

""" + failsafe_with("""        (E1) { if (chain_site(100i32) != 0i32) { exit 10i32; } if (chain_site(0i32) == 0i32) { exit 11i32; } exit 0i32; },"""),
      wrong="a site outside the kept range (10), or none inside it (11)")
claim("bi0264", D, 264, "| `site_line` |", "row",
      "site_line(0) is 0: the runtime's reserved site 0.",
      expect="run:0",
      src=main_("""    if (site_line(raw v32(0i32)) != 0i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="a line for site 0 (10)")
claim("bi0265", D, 265, "| `site_path` |", "row",
      "site_path(0) is empty.",
      expect="run:0",
      src=main_("""    string:p = site_path(raw v32(0i32));
    if (p.len != 0i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="a path for site 0 (10)")
claim("bi0266", D, 266, "| `write_file` |", "row",
      "write_file writes the whole buffer, replacing what was there.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("wf.tmp") ?! E1;
    Result<NIL>:w1 = write_file(p, "a longer first body");
    if (w1.is_error) { exit 10i32; }
    Result<NIL>:w2 = write_file(p, "ab");
    if (w2.is_error) { exit 11i32; }
    Result<string>:r = read_file(p);
    if (r.is_error) { exit 12i32; }
    string:s = move(r.value);
    if (!(string_equals(s, "ab"))) { exit 13i32; }
    exit 0i32;""", "error:E1;"),
      wrong="the old body's tail kept (13)")
claim("bi0267", D, 267, "| `open` |", "row",
      "open is one openat at AT_FDCWD: a relative path opens relative to the working directory.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("op.tmp") ?! E1;
    Result<NIL>:w = write_file(p, "x");
    if (w.is_error) { exit 10i32; }
    Result<fd>:o = open(p, 0i64, 0i64);
    if (o.is_error) { exit 11i32; }
    drop close(o.value);
    exit 0i32;""", "error:E1;"),
      wrong="a relative path not found (11)")
claim("bi0268", D, 268, "| `close` |", "row",
      "A failed close is reported, never swallowed: a second close of one descriptor is an error.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    Result<NIL>:a = close(f);
    if (a.is_error) { exit 10i32; }
    Result<NIL>:b = close(f);
    if (!b.is_error) { exit 11i32; }
    exit 0i32;""", "error:E1;"),
      wrong="the failure swallowed (11)")
claim("bi0269", D, 269, "| `read` |", "row",
      "End of input is the error E_EOF (IoEof), never a zero in the value channel.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    wild int8->:buf = alloc(16i64);
    Result<int64>:r = read(f, buf, 16i64);
    if (!r.is_error) { exit 10i32; }
    if (r.err != IoEof) { exit 11i32; }
    dalloc(buf);
    drop close(f);
    exit 0i32;""", "error:E1;"),
      wrong="a success carrying 0 (10)")
claim("bi0269b", D, 269, "Zero asked is zero delivered", "row",
      "A read of zero bytes delivers zero, successfully.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 0i64, 0i64) ?! E1;
    wild int8->:buf = alloc(16i64);
    Result<int64>:r = read(f, buf, raw v64(0i64));
    if (r.is_error) { exit 10i32; }
    if (r.value != 0i64) { exit 11i32; }
    dalloc(buf);
    drop close(f);
    exit 0i32;""", "error:E1;"),
      wrong="E_EOF for a zero-length read (10)")
claim("bi0270", D, 270, "| `write` |", "row",
      "write is one kernel write returning the bytes taken.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("/dev/null") ?! E1;
    fd:f = open(p, 1i64, 0i64) ?! E1;
    wild int8->:buf = calloc(8i64, 1i64);
    Result<int64>:r = write(f, buf, raw v64(5i64));
    if (r.is_error) { exit 10i32; }
    if (r.value != 5i64) { exit 11i32; }
    dalloc(buf);
    drop close(f);
    exit 0i32;""", "error:E1;"),
      wrong="another count (11)")
claim("bi0272", D, 272, "Error slots across the floor carry the kernel's own negative codes", "rule",
      "A floor error carries the kernel's code: a missing file's read_file error is ENOENT (NotFound).",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("m11_no_such_file.tmp") ?! E1;
    Result<string>:r = read_file(p);
    if (!r.is_error) { exit 10i32; }
    if (r.err != NotFound) { exit 11i32; }
    exit 0i32;""", "error:E1;"),
      wrong="another error (11)")
claim("bi0274", D, 274, "an interior NUL is −22", "rule",
      "to_cstring of a string with an interior NUL is an error.", m10="t12_to_cstring_interior_nul")
claim("bi0274b", D, 274, "−22, a slice out of range −34", "rule",
      "The codes are -22 (interior NUL) and -34 (a slice out of range).",
      untestable="[unobservable] a program compares an error only with a declared identity, the explicit-code form is the prelude's alone (AST_REFERENCE:158), and the prelude declares none for 22 or 34; that each is an error is tested at bi0274 and M10's t06")
claim("bi0274c", D, 274, "a slice out of range −34", "rule",
      "A slice out of range is an error of string_slice.", m10="t06_slice_out_of_range")
claim("bi0275", D, 275, "end-of-input is E_EOF = −4096", "rule",
      "E_EOF is -4096, the first code past the kernel's error space, so it collides with no errno.",
      untestable="[unobservable] the numeric value; IoEof's identity at end of input is tested at line 269")
claim("bi0277", D, 277, "−4098 INT_MIN_OVERFLOW", "rule",
      "INT_MIN / -1 reaches failsafe through the trap route (DivOverflow).", m10="v05_min_div_minus_one")
claim("bi0277b", D, 277, "−4099 OUT_OF_BOUNDS", "rule",
      "An array index past the end reaches failsafe as OutOfBounds, not through a Result.",
      expect="trap:OutOfBounds",
      src=main_("""    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    int32:x = a[raw v64(4i64)];
    exit x;"""),
      wrong="a read past the array (exit 0-ish)")
claim("bi0278", D, 278, "(a slice or array index past the end, D-070), and −4100 TBB_ERR (an ERR value", "rule",
      "An ERR tbb value at a bare comparison reaches failsafe as TbbErr.",
      expect="trap:TbbErr",
      src=main_("""    tbb8:a = raw vt8(127tbb8);
    tbb8:b = a + 1tbb8;
    if (b == 0tbb8) { exit 10i32; }
    exit 11i32;"""),
      wrong="the comparison answers (10 or 11)")
claim("bi0277c", D, 277, "−4097 DIV_BY_ZERO", "rule",
      "An integer division by zero reaches failsafe as DivByZero.",
      expect="trap:DivByZero",
      src=main_("""    int32:x = raw v32(7i32) / raw v32(0i32);
    exit x;"""),
      wrong="a hardware SIGFPE (136) or a value")
claim("bi0280", D, 280, "Positive codes", "rule",
      "Positive codes belong to programs.",
      untestable="[vague] an allocation of the code space; a program's own error identities are hashed, not chosen")

# ------------------------------------------------------------------ §2c
claim("bi0285", D, 285, "The three string names the compiler EVALUATES during `comptime` folding", "rule",
      "The compiler evaluates §2c's three names during comptime folding.",
      untestable="[vague] tested per row below")
claim("bi0290", D, 290, "| `string_equals` |", "row",
      "string_equals folds at comptime: it initialises a module `fixed` bool.",
      expect="run:0",
      src=main_("""    if (!EQ) { exit 10i32; }
    if (NE) { exit 11i32; }
    exit 0i32;""", """fixed bool:EQ = string_equals("ab", "ab");
fixed bool:NE = string_equals("ab", "ac");"""),
      wrong="refused as a non-constant initialiser, or a wrong answer")
claim("bi0291", D, 291, "| `string_byte_length` |", "row",
      "string_byte_length is the byte length.", m10="t01_byte_length_utf8")
claim("bi0291b", D, 291, "Folds at comptime. **ABI:** inline", "row",
      "string_byte_length folds at comptime: it initialises a module `fixed` int64.",
      expect="run:0",
      src=main_("""    if (N != 3i64) { exit 10i32; }
    exit 0i32;""", """fixed int64:N = string_byte_length("abc");"""),
      wrong="refused as a non-constant initialiser, or another value")
claim("bi0292", D, 292, "| `string_is_empty` |", "row",
      "string_is_empty folds at comptime: it initialises a module `fixed` bool.",
      expect="run:0",
      src=main_("""    if (!E) { exit 10i32; }
    exit 0i32;""", """fixed bool:E = string_is_empty("");"""),
      wrong="refused as a non-constant initialiser, or false")

# ------------------------------------------------------------------ §2d
claim("bi0300", D, 300, "no program names them, the resolver admits", "rule",
      "The runtime symbols the emitter calls are not names: a program calling `arena_alloc` is refused.",
      expect="refuse",
      src=main_("""    discard(arena_alloc(1i64));
    exit 0i32;"""),
      wrong="accepted: an emitter symbol reached by name")
for _ln, _key, _ret, _args in [(311, "arena_alloc", r"\{ i64, i32 \}", ["ptr", "i64"]),
                               (312, "arena_at", "ptr", ["ptr", "i64", "i64", "i32"]),
                               (313, "arena_free", "i32", ["ptr", "i64", "i64", "i32"]),
                               (314, "arena_reset", "void", ["ptr", "i64"]),
                               (315, "arena_destroy", "void", ["ptr"]),
                               (316, "sarena_bump", "i64", ["ptr", "i64"]),
                               (317, "sarena_slot", "ptr", ["ptr", "i64", "i64"]),
                               (318, "sarena_destroy", "void", ["ptr"]),
                               (319, "exit", "void", ["i32"])]:
    _sym = "npk_" + _key
    claim("bi%04d" % _ln, D, _ln, "| `%s` |" % _key, "row",
          "Every emitted module declares @%s as %s (%s)." % (_sym, _ret.replace("\\", ""), ", ".join(_args)),
          expect=r"ir:^declare %s @%s\(%s\)" % (_ret, _sym, ", ".join(a + r"[^,)]*" for a in _args)),
          src=main_("""    exit 0i32;"""),
          wrong="another shape, or no declaration")
claim("bi0323", D, 323, "`arena_alloc`'s `{ i64, i32 }` is a `Handle<T>`, NOT a `Result`", "rule",
      "An arena's alloc() answers a Handle<T>, not a Result: it binds with no unwrap.",
      expect="run:0",
      src=main_("""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    exit 0i32;"""),
      wrong="refused: alloc() typed as a Result")

# ------------------------------------------------------------------ §3 sys
claim("bi0337", D, 337, "| `sys` |", "row",
      "sys reaches any syscall; the kernel's negative returns land in the error slot.",
      expect="run:0",
      src=main_("""    Result<int64>:p = sys(39i64);
    if (p.is_error) { exit 10i32; }
    if (p.value <= 0i64) { exit 11i32; }
    Result<int64>:c = sys(3i64, raw v64(987654i64));
    if (!c.is_error) { exit 12i32; }
    exit 0i32;"""),
      wrong="a negative return in the value channel (12)")
claim("bi0341", D, 341, "The call TYPES as `Result<int64>`", "rule",
      "A sys call types as Result<int64>: a wrong annotation over it is refused like any typed Result's.",
      expect="refuse",
      src=main_("""    int32:x = sys(39i64) ?| 0i32;
    exit 0i32;"""),
      wrong="accepted: the int64 value narrowed silently")
claim("bi0344", D, 344, "register: integer-family at 64 bits or below", "rule",
      "A sys argument that does not fit a kernel register (a string) is refused.",
      expect="refuse",
      src=main_("""    string:s = "abc";
    Result<int64>:r = sys(39i64, s);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0346", D, 346, "at most", "rule",
      "At most six register arguments follow the syscall number: seven are refused.",
      expect="refuse",
      src=main_("""    Result<int64>:r = sys(39i64, 1i64, 2i64, 3i64, 4i64, 5i64, 6i64, 7i64);
    exit 0i32;"""),
      wrong="accepted, the seventh dropped")
claim("bi0348", D, 348, "resolve (a nested bare-builtin call) is refused with \"bind it to a typed", "rule",
      "An argument that is a nested bare-builtin call is refused (bind it to a typed name first).",
      expect="refuse",
      src=main_("""    Result<int64>:r = sys(39i64, mono_now());
    exit 0i32;"""),
      wrong="accepted")
claim("bi0350", D, 350, "unsigned one or a kernel identifier ZERO-extends into its register", "rule",
      "At the trampoline a signed argument sign-extends and an unsigned one zero-extends: lseek to int32 -1 fails, to uint32 0xFFFFFFFF succeeds.",
      expect="run:0",
      src=main_("""    cstring:p = to_cstring("ls.tmp") ?! E1;
    Result<NIL>:w = write_file(p, "abc");
    if (w.is_error) { exit 10i32; }
    fd:f = open(p, 0i64, 0i64) ?! E1;
    int32:neg = raw v32(-1i32);
    Result<int64>:a = sys(8i64, f, neg, 0i64);
    if (!a.is_error) { exit 11i32; }
    uint32:big = raw vu32(4294967295u32);
    Result<int64>:b = sys(8i64, f, big, 0i64);
    if (b.is_error) { exit 12i32; }
    if (b.value != 4294967295i64) { exit 13i32; }
    drop close(f);
    exit 0i32;""", "error:E1;"),
      wrong="int32 -1 zero-extended (11), or uint32 sign-extended (12)")
excluded(D, 357, "the original three syscall tiers, removed by D-001 and D-048: history; the current rules are tested at lines 375-386")
claim("bi0368", D, 368, "Restricting which syscalls a binary may make is **`--seccomp`**'s job", "rule",
      "The compiler has a `--seccomp` option (a kernel-enforced allowlist).",
      expect="sh:0",
      sh="""cat > s.npk <<'EOF'
mod:s;
func:main = int32(cstring[]:_~argv) { exit 0i32; };
func:failsafe = int32(Error:e) { exit 9i32; };
EOF
out=$("$NPKC" s.npk -o s.ll --seccomp 2>&1); rc=$?
echo "$out" | head -3
[ $rc -eq 0 ] && [ -f s.ll ]""",
      wrong="the option is unknown")
claim("bi0375", D, 375, "`--extra-picky=no-sys` bans direct syscalls", "rule",
      "`--extra-picky=no-sys` refuses a program that calls sys; without it the program compiles.",
      expect="sh:0",
      sh="""cat > s.npk <<'EOF'
mod:s;
func:main = int32(cstring[]:_~argv) {
    Result<int64>:p = sys(39i64);
    if (p.is_error) { exit 1i32; }
    exit 0i32;
};
func:failsafe = int32(Error:e) { exit 9i32; };
EOF
"$NPKC" s.npk -o a.ll > a.out 2>&1; a=$?
"$NPKC" s.npk -o b.ll --extra-picky=no-sys > b.out 2>&1; b=$?
head -3 a.out b.out
[ $a -eq 0 ] && [ $b -eq 1 ]""",
      wrong="the flag unknown, or the sys call accepted under it")
claim("bi0378", D, 378, "**`asm!!` is spelled `asm`** (D-046)", "rule",
      "`asm!!` no longer exists: it is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    Result<int32>:r = asm!!<int32>("x86_64", "mov %1, %0", "=r,r", x);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0379", D, 379, "`!!` no longer exists in the language", "rule",
      "`!!` no longer exists: `sys!!(...)` is refused.",
      expect="refuse",
      src=main_("""    Result<int64>:r = sys!!(39i64);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0381", D, 381, "**`sys!!!` is removed** (D-001)", "rule",
      "`sys!!!` is removed: it is refused.",
      expect="refuse",
      src=main_("""    int64:r = sys!!!(39i64);
    exit 0i32;"""),
      wrong="accepted: an unwrapped raw syscall")
claim("bi0384", D, 384, "Both remaining tiers are `Result`-wrapped", "rule",
      "Every function but main and failsafe returns Result<T>: a fallible function's result bound bare is refused.",
      expect="refuse",
      src=main_("""    int32:x = f();
    exit 0i32;""", """error:E1;
func:f = int32() { fail E1; };"""),
      wrong="accepted: the failure ignored")
claim("bi0386", D, 386, "`raw` / `_!` remains the single explicit, greppable bypass", "rule",
      "`_!` is the other spelling of `raw`: it unwraps a never-fails call.",
      expect="run:0",
      src=main_("""    int32:x = _! v32(4i32);
    if (x != 4i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused: `_!` is not a spelling")

# ------------------------------------------------------------------ §4 compiler macros
claim("bi0394", D, 394, "`#` is the **compiler-directive sigil**", "rule",
      "`#` marks what is addressed to the compiler.",
      untestable="[vague] tested through the forms below")
claim("bi0399", D, 399, "| `#name<T>(...)` | builtin producing a value |", "row",
      "`#name<T>(...)` is a builtin producing a value: #size_of<int64>() is a value.",
      expect="run:0",
      src=main_("""    int64:n = #size_of<int64>();
    if (n != 8i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused, or another size")
claim("bi0400", D, 400, "| `#name(...)` | **macro invocation** (D-046) — replaces `name!(args)` |", "row",
      "The old macro invocation `name!(args)` is replaced by `#name(args)`: `name!(args)` is refused.",
      expect="refuse",
      src=main_("""    int32:x = twice!(3i32);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0401", D, 401, "| `#[name(...)]` | attribute annotating a declaration |", "row",
      "`#[name(...)]` annotates a declaration: #[derive(Eq)] on a struct derives ==.",
      expect="run:0",
      src=main_("""    Pt:a = Pt{ x: 1i32, y: 2i32 };
    Pt:b = Pt{ x: 1i32, y: raw v32(2i32) };
    if (!(a == b)) { exit 10i32; }
    exit 0i32;""", """#[derive(Eq)]
struct:Pt = { int32:x; int32:y; };"""),
      wrong="refused, or the derived equality wrong")
claim("bi0403", D, 403, "**`@` is never a builtin prefix.**", "rule",
      "`@` is never a builtin prefix: `@sizeof(int64)` is refused.",
      expect="refuse",
      src=main_("""    int64:n = @sizeof(int64);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0408", D, 408, "**Except casting**, which has no builtin form at all", "rule",
      "A cast has no builtin form: `#cast<int64>(x)` is refused (the operators are => and =>!).",
      expect="refuse",
      src=main_("""    int32:x = raw v32(5i32);
    int64:y = #cast<int64>(x);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0409", D, 409, "`@cast_unchecked<T>` become the operators **`=>`** and **`=>!`** (D-021)", "rule",
      "`@cast<T>(x)` is not a cast; `x => T` is.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(5i32);
    int64:y = @cast<int64>(x);
    exit 0i32;"""),
      wrong="accepted as a cast")
claim("bi0416", D, 416, "| `#size_of<T>` |", "row",
      "#size_of<T> is T's size in bytes, known at compile time.",
      expect="run:0",
      src=main_("""    if (#size_of<int8>() != 1i64) { exit 10i32; }
    if (#size_of<int64>() != 8i64) { exit 11i32; }
    if (S != 16i64) { exit 12i32; }
    exit 0i32;""", """struct:P = { int64:a; int64:b; };
fixed int64:S = #size_of<P>();"""),
      wrong="another size, or not a compile-time value (a refused `fixed`)")
claim("bi0417", D, 417, "| `#wild_ptr<T>(addr)` |", "row",
      "#wild_ptr<T>(addr) constructs a pointer from an integer address, in wild context.",
      expect="run:0",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild int8->:q = raw back(p);
    dalloc(p);
    exit 0i32;""", """func:back = int8->(int8->:p) never fails {
    wild int8->:q = #wild_ptr<int8>(4096i64);
    pass p;
};"""),
      wrong="refused in wild context")
claim("bi0417b", D, 417, "**Legal only in `wild` context**", "row",
      "#wild_ptr is legal only in wild context: into a binding not declared `wild` it is refused (D-019's reading).",
      expect="refuse",
      src=main_("""    int8->:q = #wild_ptr<int8>(4096i64);
    exit 0i32;"""),
      wrong="accepted outside wild context")
claim("bi0418", D, 418, "| `#wild_slice<T>(ptr, len)` |", "row",
      "#wild_slice's count is held to [0, 2^47]: a negative count traps OutOfBounds.",
      expect="trap:OutOfBounds",
      src=main_("""    wild int8->:p = alloc(16i64);
    wild uint8->:u = p =>! wild uint8->;
    uint8[]:v = #wild_slice<uint8>(u, raw v64(-1i64));
    if (v.len == 7i64) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="a slice of length 2^64-1 (exit 0)")
claim("bi0418b", D, 418, "TYPE-061 keeps it out of `pure` bodies", "row",
      "#wild_slice is refused in a pure body (TYPE-061).",
      expect="refuse:NITPICK-TYPE-061",
      src=main_("""    wild int8->:p = alloc(16i64);
    int64:n = raw count(p);
    dalloc(p);
    exit 0i32;""", """func:count = int64(int8->:p) pure never fails {
    uint8[]:v = #wild_slice<uint8>(p =>! uint8->, 4i64);
    pass v.len;
};"""),
      wrong="accepted in a pure body")
claim("bi0418c", D, 418, "STRUCK by D-315 (2026-09-23)", "row",
      "#wild_slice is no longer wild-context only: a slice over a plain pointer compiles.",
      expect="run:0",
      src=main_("""    wild int8->:p = calloc(4i64, 1i64);
    uint8->:u = p =>! uint8->;
    uint8[]:v = #wild_slice<uint8>(u, raw v64(4i64));
    if (v.len != 4i64) { exit 10i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="refused outside wild context")
claim("bi0419", D, 419, "| `#ptr_add<T>(ptr, offset)` |", "row",
      "#ptr_add<T>'s offset is in elements of T: #ptr_add<int64>(p, 1) advances eight bytes.",
      expect="run:0",
      src=main_("""    wild int8->:p = calloc(4i64, 8i64);
    wild int64->:w = p =>! wild int64->;
    <-(#ptr_add<int64>(w, 1i64)) = 77i64;
    wild uint8->:u = p =>! wild uint8->;
    if (u[8i64] != 77u8) { exit 10i32; }
    if (u[1i64] != 0u8) { exit 11i32; }
    dalloc(p);
    exit 0i32;"""),
      wrong="a byte offset: the store lands at byte 1 (11)")
claim("bi0419b", D, 419, "**Legal only in `wild` context** — pointer arithmetic is the manual regime's", "row",
      "#ptr_add is legal only in wild context: over a buffer's pointer, outside wild, it is refused.",
      expect="refuse",
      src=main_("""    buffer:b = buffer_new(16i64);
    <-(#ptr_add<uint8>(b.ptr, 3i64)) = 7u8;
    if (b.ptr[3i64] != 7u8) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted outside wild context")
claim("bi0420", D, 420, "| `#sqrt(x)` |", "row",
      "#sqrt of a negative operand yields NaN, with no error channel.", m10="f03_sqrt_of_negative")
claim("bi0420b", D, 420, "`flt32`/`flt64` only, by refusal", "row",
      "#sqrt of an integer is refused.",
      expect="refuse",
      src=main_("""    int32:r = #sqrt(raw v32(16i32));
    exit 0i32;"""),
      wrong="accepted")
claim("bi0420c", D, 420, "it lowers to `llvm.sqrt.f32`/`f64`", "row",
      "#sqrt lowers to the llvm.sqrt intrinsic.",
      expect=r"ir:@llvm\.sqrt\.f64",
      src=main_("""    flt64:r = #sqrt(raw vf64(16.0f64));
    if (r != 4.0f64) { exit 10i32; }
    exit 0i32;"""),
      wrong="a library call or a Newton loop")
claim("bi0421", D, 421, "| `#unreachable()` |", "row",
      "#unreachable() traps UNREACHABLE (-4102) when reached.",
      expect="trap:Unreachable",
      src=main_("""    int32:x = raw pick1(raw v32(2i32));
    exit x;""", """func:pick1 = int32(int32:k) never fails {
    if (k == 1i32) { pass 1i32; }
    pass #unreachable();
};"""),
      wrong="undefined behaviour: a value (exit 0-ish)")
claim("bi0421b", D, 421, "Takes no arguments", "row",
      "#unreachable takes no arguments: #unreachable(1i32) is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw pick1(raw v32(1i32));
    exit x - 1i32;""", """func:pick1 = int32(int32:k) never fails {
    if (k == 1i32) { pass 1i32; }
    pass #unreachable(1i32);
};"""),
      wrong="accepted")

# ------------------------------------------------------------------ §5 asm
claim("bi0428", D, 428, "Nitpick supports direct inline assembly for `x86_64` and `aarch64` targets", "rule",
      "Inline assembly is supported for x86_64 (and aarch64).",
      untestable="[vague] tested through the row and the example below; aarch64 is another platform")
claim("bi0432", D, 432, "| `asm<T>(arch, code, constraints, args)` |", "row",
      "asm<T> wraps the output in Result<T>; a negative integer return is an error.",
      expect="run:0",
      src=main_("""    int32:x = raw v32(-5i32);
    Result<int32>:r = asm<int32>("x86_64", "mov %1, %0", "=r,r", x);
    if (!r.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="a negative result as a value (10), or asm refused")
claim("bi0434", D, 434, "**`asm!!!` is removed** (D-001)", "rule",
      "`asm!!!` is removed: it is refused.",
      expect="refuse",
      src=main_("""    int32:x = raw v32(1i32);
    int32:r = asm!!!<int32>("x86_64", "mov %1, %0", "=r,r", x);
    exit 0i32;"""),
      wrong="accepted")
claim("bi0439", D, 439, "```nitpick", "example",
      "The example: x86_64 assembly adding 1 to its input, returning Result<int32>.",
      expect="run:0",
      src=main_("""    int32:input_var = raw v32(41i32);
    // Executing x86_64 assembly, returning a Result<int32>
    Result<int32>:val = asm<int32>(
        "x86_64",
        "mov %1, %0\\nadd $1, %0",
        "=r,r",
        input_var
    );
    if (val.is_error) { exit 10i32; }
    if (val.value != 42i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, or another value")
