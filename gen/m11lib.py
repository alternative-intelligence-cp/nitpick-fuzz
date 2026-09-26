"""M11 -- the reference, checked against the compiler: the claim DSL.

A claims module (gen/m11_claims/<name>.py) does `from m11lib import *` and calls
`claim(...)` once per claim it extracts from its line range of one reference at
HUNT2 (`.work/hunt2/meta/specs/<DOC>_REFERENCE.md`). gen/m11.py loads every
claims module, checks each quote against its line, checks that every fenced code
block and every table body row of every reference is covered, and writes
m11/CLAIMS.md, m11/EXPECT.tsv and m11/programs/.

A claim:
  claim(cid, doc, line, quote, kind, text, expect=None, src=None, ...)
    cid     unique id: the doc's two-letter prefix, the HUNT2 line as four
            digits, and an optional letter for a second claim on one line:
            "ty0543", "ty0543b". It is also the program's file and `mod:` name.
    doc     "TYPE", "BUILTIN", ... (DOCS below)
    line    the line number at HUNT2 the claim is read from
    quote   a substring of that line, verbatim (checked)
    kind    "example" (a fenced code block; `line` is its opening fence),
            "row" (a table body row; `line` is the row), or "rule" (a normative
            sentence in prose)
    text    the claim, in one sentence
    expect  the outcome the TEXT says, written before any run (None when
            untestable):
              run:N          npkc 0, both legs exit N (N=0 is the reference's answer)
              trap:Name      npkc 0, both legs reach failsafe's arm for Name
              refuse         npkc 1 (any code)
              refuse:CODE    npkc 1 naming CODE (e.g. NITPICK-TYPE-054 or TYPE-054)
              compile        npkc 0 and both legs build (exits recorded, not judged)
              ir:REGEX       npkc 0 and the emitted .ll matches REGEX (re.M)
              ir!:REGEX      npkc 0 and the emitted .ll does not match REGEX
              sh:N           the claim's shell script (`sh=`) exits N
    src     the program: use main_(body, decls) for a `main` around `body`, or
            give a whole program (it must contain its own `main`)
    files   {"name.npk": "text"} support modules beside the root (imports are
            relative; a file's name must equal its `mod:` name)
    sh      a bash script for `sh:N` (run in a scratch dir; $NPKC, $NPKRT and
            $LLVM_BIN are set; PATH starts with $LLVM_BIN)
    heap    "allocated/peak_live/count" with `*` wildcards: the run is under
            NPK_HEAP_STATS=1 and each leg's `heap:` line must match
    fs      False when `src` carries its own `failsafe`
    wrong   what an implementation that gets the claim wrong would answer
    untestable  "[tag] reason" when no program here can test the claim;
            tags: z3, tool, tree, internal, platform, timing, unobservable, vague
    m10     an M10 item id whose program tests exactly this claim (then no src;
            the expectation is M10's, from m10/EXPECT.tsv)
    note    anything else

  excluded(doc, line, reason)
    a table (its header row at `line`) whose body rows are not claims, e.g. a
    table of history or a legend; every other table body row needs a claim.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS = {
    "AST": ("as", "meta/specs/AST_REFERENCE.md"),
    "BUILD": ("bd", "meta/specs/BUILD_REFERENCE.md"),
    "BUILTIN": ("bi", "meta/specs/BUILTIN_REFERENCE.md"),
    "CONCURRENCY": ("cc", "meta/specs/CONCURRENCY_REFERENCE.md"),
    "CONTROL": ("ct", "meta/specs/CONTROL_REFERENCE.md"),
    "IO": ("io", "meta/specs/IO_REFERENCE.md"),
    "LEXICAL": ("lx", "meta/specs/LEXICAL_REFERENCE.md"),
    "MACRO": ("mc", "meta/specs/MACRO_REFERENCE.md"),
    "MEMORY": ("me", "meta/specs/MEMORY_REFERENCE.md"),
    "MODULE": ("md", "meta/specs/MODULE_REFERENCE.md"),
    "OP": ("op", "meta/specs/OP_REFERENCE.md"),
    "TRAITS": ("tr", "meta/specs/TRAITS_REFERENCE.md"),
    "TYPE": ("ty", "meta/specs/TYPE_REFERENCE.md"),
    "VERIFICATION": ("vf", "meta/specs/VERIFICATION_REFERENCE.md"),
}

UNTESTABLE_TAGS = ("z3", "tool", "tree", "internal", "platform", "timing", "unobservable", "vague")

# failsafe arms: M10's (PROGRESS S4, S34) and every other prelude identity at HUNT2
TRAPS = [("HeapBadRequest", 91), ("HeapOom", 92), ("IntOverflow", 93), ("OutOfBounds", 94),
         ("Unreachable", 95), ("WildLeak", 96), ("DivByZero", 97), ("DivOverflow", 98),
         ("StaleHandle", 100), ("DeadlineExceeded", 101), ("ChannelClosed", 102),
         ("DriverLeak", 103), ("IoEof", 104), ("WouldBlock", 105),
         ("StackExhausted", 106), ("MachineFault", 107), ("LimitViolated", 108),
         ("DecreasesViolated", 109), ("TbbErr", 110), ("ShiftRange", 111), ("CastRange", 112),
         ("BadStep", 113), ("BorrowOverlap", 114), ("RequiresViolated", 115),
         ("EnsuresViolated", 116), ("InvariantViolated", 117), ("Interrupted", 118),
         ("NotFound", 119), ("Exists", 120), ("CrossDevice", 121), ("BadPath", 122)]
TRAP_CODE = dict(TRAPS)

# identity functions: a value that goes through one is not a constant to the folder
HELPERS = {
    "v8": "int8", "v16": "int16", "v32": "int32", "v64": "int64", "vi128": "int128",
    "vu8": "uint8", "vu16": "uint16", "vu32": "uint32", "vu64": "uint64",
    "vf32": "flt32", "vf64": "flt64", "vc8": "char8", "vb": "bool",
    "vt8": "tbb8", "vt32": "tbb32",
}

CLAIMS = []
EXCLUDED = []
_MODULE = [None]      # the claims module being loaded (set by gen/m11.py)

ID_RE = re.compile(r"^[a-z]{2}\d{4}[a-z]?$")
EXPECT_RE = re.compile(r"^(run:\d+|trap:[A-Za-z]+|refuse|refuse:(NITPICK-)?[A-Z]+-\d{3}|compile|"
                       r"ir!?:.+|sh:\d+)$")


def claim(cid, doc, line, quote, kind, text, expect=None, src=None, files=None, sh=None,
          heap=None, fs=True, wrong="", untestable=None, m10=None, note=""):
    CLAIMS.append(dict(id=cid, doc=doc, line=line, quote=quote, kind=kind, text=text,
                       expect=expect, src=src, files=files or {}, sh=sh, heap=heap, fs=fs,
                       wrong=wrong, untestable=untestable, m10=m10, note=note,
                       module=_MODULE[0]))


def excluded(doc, line, reason):
    EXCLUDED.append(dict(doc=doc, line=line, reason=reason, module=_MODULE[0]))


def main_(body, decls=""):
    """A program: top-level declarations, then `main` around `body`."""
    return (decls.strip() + "\n\n" if decls.strip() else "") + \
        "func:main = int32(cstring[]:_~argv) {\n" + body.rstrip() + "\n};\n"


def failsafe_text(src):
    arms = ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS]
    for e in sorted(set(re.findall(r"\berror:(E(\d));", src))):
        arms.append("        (%s) { exit %di32; }," % (e[0], 80 + int(e[1])))
    arms.append("        (*) { exit 99i32; }")
    return "func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) + \
        "\n    }\n    exit 9i32;\n};\n"


def failsafe_with(first_arms, src=""):
    """A whole `failsafe` whose `first_arms` (text, each arm ending in a comma) come
    before every standard arm whose identity they do not name; for a program that
    passes fs=False because its claim reads `failsafe` itself."""
    named = set(re.findall(r"\((\w+)\)\s*\{", first_arms))
    arms = [first_arms.rstrip()]
    arms += ["        (%s) { exit %di32; }," % (n, c) for n, c in TRAPS if n not in named]
    for e in sorted(set(re.findall(r"\berror:(E(\d));", src))):
        if e[0] not in named:
            arms.append("        (%s) { exit %di32; }," % (e[0], 80 + int(e[1])))
    arms.append("        (*) { exit 99i32; }")
    return "func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) + \
        "\n    }\n    exit 9i32;\n};\n"


def helpers_text(src):
    out = []
    for name, t in HELPERS.items():
        if re.search(r"\b%s\(" % name, src) and not re.search(r"func:%s\b" % name, src):
            out.append("func:%s = %s(%s:x) never fails { pass x; };" % (name, t, t))
    return "\n".join(out)


def normalize_expect(e):
    """trap:Name -> run:<arm code>; everything else unchanged."""
    if e and e.startswith("trap:"):
        return "run:%d" % TRAP_CODE[e[5:]]
    return e


# ---------------------------------------------------------------- the reference scan
def doc_lines(doc, tree="hunt2"):
    path = os.path.join(ROOT, ".work", tree, DOCS[doc][1])
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def _unquote(l):
    """A line with any blockquote markers removed."""
    s = l.strip()
    while s.startswith(">"):
        s = s[1:].strip()
    return s


def scan(doc):
    """-> (fences, tables): fences = [opening line numbers]; tables = [(header_line,
    [body row line numbers])], both 1-based; blockquoted blocks and tables count."""
    L = doc_lines(doc)
    fences, tables = [], []
    inb = False
    i = 0
    while i < len(L):
        s = _unquote(L[i])
        if s.startswith("```"):
            if not inb:
                fences.append(i + 1)
            inb = not inb
            i += 1
            continue
        if inb:
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(L) and re.match(r"^\|?\s*:?-{2,}", _unquote(L[i + 1])):
            head = i + 1
            rows = []
            j = i + 2
            while j < len(L) and _unquote(L[j]).startswith("|"):
                rows.append(j + 1)
                j += 1
            tables.append((head, rows))
            i = j
            continue
        i += 1
    return fences, tables
