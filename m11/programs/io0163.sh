#!/bin/bash
# M11 io0163 -- meta/specs/IO_REFERENCE.md:163
# claim: stderr is unbuffered, so a partial line written to it survives a trap.
# expect: sh:0
cat > t.npk <<'EOF'
mod:t;

func:v32 = int32(int32:x) never fails { pass x; };

async func:main = int32(cstring[]:_~argv) {
    TextWriter<ByteWriter>:se = std_err() ?! Unreachable;
    await text_write_str(@se, "diag-m11", raw duration_ms(500i64)) ?! Unreachable;
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
grep -q 'diag-m11' err.txt || exit 1
exit 0
