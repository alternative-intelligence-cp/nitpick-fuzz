"""M11: the scaffolding TYPE 1177-2122's claims modules share (type3.py, type4.py; S65).

Not a claims module (it lives outside gen/m11_claims/, so gen/m11.py does not load it):
the helpers type2.py defines inline, gathered once, with the shell build of MODULE's
SH_LIB for the scripts that load a library of the compiler's tree.
"""
import re

from m11lib import TRAPS, main_, failsafe_text, helpers_text


def layout(types, size, align, decls="", body=""):
    """a run program: #size_of each type is `size`, and after an int8 it sits at
    offset `align` (so {int8, T} is align + size bytes)"""
    d, b = [], []
    code = 10
    for i, t in enumerate(types):
        if not t.replace("_", "").isalnum():
            d.append("struct:S%d = { %s:v; };" % (i, t))
        d.append("struct:P%d = { int8:a; %s:v; };" % (i, t))
    for i, t in enumerate(types):
        what = t if t.replace("_", "").isalnum() else "S%d" % i
        b.append("    if (#size_of<" + what + ">() != " + str(size) + "i64) { exit " +
                 str(code) + "i32; }")
        b.append("    if (#size_of<P" + str(i) + ">() != " + str(align + size) +
                 "i64) { exit " + str(code + 1) + "i32; }")
        code += 2
    return prog_("\n".join(b) + ("\n" + body.rstrip() if body.strip() else "") +
                 "\n    exit 0i32;", "\n".join(d) + ("\n" + decls if decls else ""))


def layout_wrong(t, size, align):
    return "10: %s is not %d bytes; 11: it does not sit at offset %d after an int8" % (t, size, align)


MYH = {"wt16": "tbb16", "wt64": "tbb64", "wt128": "tbb128", "wt256": "tbb256",
       "w256": "int256", "vtt": "trit", "vtr": "tryte", "vnt": "nit", "vny": "nyte"}


def prog_(body, decls=""):
    """main_ around `body`, with the identity helpers of MYH the text calls"""
    text = decls + "\n" + body
    hs = ["func:%s = %s(%s:x) never fails { pass x; };" % (n, t, t)
          for n, t in MYH.items() if re.search(r"\b%s\(" % n, text)]
    return main_(body, "\n".join(hs) + ("\n" + decls if decls.strip() else ""))


def chk(cond, code):
    return "    if (!(%s)) { exit %di32; }" % (cond, code)


def _fn(name):
    return r'^define [^@\n]*@"?(?:[\w$]+\.)*' + name + r'"?\('


def _body(p):
    return r"(?=(?:(?!\n\}).)*?" + p + ")"


def ir_fn(name, *pats):
    """ir: the body of function `name` contains every pattern"""
    return "ir:(?s)" + _fn(name) + "".join(_body(p) for p in pats)


def ir_fn_lacks(name, has, lacks):
    """ir: function `name` contains every pattern in `has`, and not `lacks`"""
    return "ir:(?s)" + _fn(name) + "".join(_body(p) for p in has) + \
        r"(?!(?:(?!\n\}).)*?" + lacks + ")"


def param(name, ty):
    """a fragment: function `name`'s first parameter is `ty` (every function returns
    `{ T, i32 }`, so a return type is never demanded); `ty` may end in a bracket"""
    return _fn(name) + ty + r"(?=[\s,)])"


def ir_all(*frags):
    return r"ir:(?s)\A" + "".join("(?=.*?" + f + ")" for f in frags)


def fs_any():
    """a failsafe in which every trap exits 42: for a claim that says `traps` and names
    no trap"""
    arms = ["        (%s) { exit 42i32; }," % n for n, _ in TRAPS]
    arms.append("        (*) { exit 99i32; }")
    return ("func:failsafe = int32(Error:e) {\n    pick (e) {\n" + "\n".join(arms) +
            "\n    }\n    exit 9i32;\n};")


def any_trap(body, decls=""):
    """a run:42 program: `body` should trap; reaching its end exits 10"""
    return prog_(body.rstrip() + "\n    exit 10i32;", (decls + "\n" if decls else "") + fs_any())


ANY = "names no trap: every trap exits 42 (`fs_any`)"


def prog(src, name="p"):
    """A whole program for a script (verif3's)."""
    h = helpers_text(src)
    out = "mod:%s;\n\n" % name + (h + "\n\n" if h else "") + src.strip() + "\n"
    if "func:failsafe" not in src:
        out += "\n" + failsafe_text(src)
    return out


OBL_HEAD = r'''# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
cat > p.npk <<'NPK_EOF'
@@PROG@@
NPK_EOF
"$NPKC" p.npk -o p.ll --obligations ob >out.txt 2>err.txt; rc=$?
if [ "$rc" -ne 0 ]; then echo "npkc exit $rc"; head -c 800 err.txt; exit 3; fi
[ -f ob/rows.txt ] || { echo "no rows.txt"; ls ob; exit 4; }
rows() { awk -F'\t' -v f="$1" -v k="$2" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } (k == "*" || $3 == k) && $6 ~ re' ob/rows.txt; }
n() { rows "$1" "$2" | wc -l | tr -d ' '; }
kinds() { rows "$1" '*' | cut -f3 | sort | uniq -c | tr -s ' ' | tr '\n' ';'; }
'''


def obl(src, checks):
    return OBL_HEAD.replace("@@PROG@@", prog(src)) + checks.strip() + "\nexit 0\n"


# MODULE's build (module.py SH_LIB): both legs by PLAN.md's recipe
SH_LIB = r'''build() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 0 ] || return 3
    opt -O2 -S p.ll -o p2.ll || return 4
    llc -O0 -filetype=obj -relocation-model=static p.ll -o p0.o || return 4
    llc -O2 -filetype=obj -relocation-model=static p2.ll -o p2.o || return 4
    ld.lld -static p0.o "$NPKRT" -o p0 || return 4
    ld.lld -static p2.o "$NPKRT" -o p2 || return 4
}
legs() {
    env -i ./p0 < /dev/null; a=$?
    env -i ./p2 < /dev/null; b=$?
    echo "O0=$a O2=$b"
    [ $a -eq "$1" ] && [ $b -eq "$1" ]
}
refused() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 1 ] || return 1
    ! grep -q 'NITPICK-EMIT-002' npkc.out || return 1
    [ -z "$2" ] || grep -q -- "$2" npkc.out
}
LIB="$(dirname "$NPKC")/../../lib"
'''


def lib_run(libs, body, decls=""):
    """sh:0: copy the compiler's `libs` beside a root that uses them, build both legs,
    and require exit 0"""
    uses = "".join('use "./%s.npk".*;\n' % l for l in libs)
    h = helpers_text(body + "\n" + decls)
    src = "mod:r;\n" + uses + "\n" + (h + "\n\n" if h else "") + main_(body, decls) + "\n"
    src += failsafe_text(src)
    return (SH_LIB + 'cp ' + " ".join('"$LIB/%s.npk"' % l for l in libs) + " . || exit 5\n" +
            "cat > r.npk <<'NPK_EOF'\n" + src + "NPK_EOF\nbuild r.npk || exit $?\nlegs 0\n")
