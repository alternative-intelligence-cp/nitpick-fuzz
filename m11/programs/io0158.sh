#!/bin/bash
# M11 io0158 -- meta/specs/IO_REFERENCE.md:158
# claim: No flush is attempted on a trap: a partial line in line-buffered stdout is lost when the program traps.
# expect: sh:0
cat > t.npk <<'EOF'
mod:t;

func:v32 = int32(int32:x) never fails { pass x; };

async func:main = int32(cstring[]:_~argv) {
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! Unreachable;
    await text_write_str(@so, "partial-m11", raw duration_ms(500i64)) ?! Unreachable;
    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;
};

func:failsafe = int32(Error:e) {
    pick (e) {
        (IntOverflow) { exit 93i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};
EOF
"$NPKC" t.npk -o t.ll > npkc.log 2>&1 || exit 2
llc -O0 -filetype=obj -relocation-model=static t.ll -o t.o || exit 3
ld.lld -static t.o "$NPKRT" -o t || exit 4
env -i ./t > out.txt 2> err.txt < /dev/null
rc=$?
[ "$rc" -eq 93 ] || exit 5
if grep -q 'partial-m11' out.txt; then exit 1; fi
exit 0
