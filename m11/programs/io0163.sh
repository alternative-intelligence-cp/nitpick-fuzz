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
        (HeapBadRequest) { exit 91i32; },
        (HeapOom) { exit 92i32; },
        (IntOverflow) { exit 93i32; },
        (OutOfBounds) { exit 94i32; },
        (Unreachable) { exit 95i32; },
        (WildLeak) { exit 96i32; },
        (DivByZero) { exit 97i32; },
        (DivOverflow) { exit 98i32; },
        (StaleHandle) { exit 100i32; },
        (DeadlineExceeded) { exit 101i32; },
        (ChannelClosed) { exit 102i32; },
        (DriverLeak) { exit 103i32; },
        (IoEof) { exit 104i32; },
        (WouldBlock) { exit 105i32; },
        (StackExhausted) { exit 106i32; },
        (MachineFault) { exit 107i32; },
        (LimitViolated) { exit 108i32; },
        (DecreasesViolated) { exit 109i32; },
        (TbbErr) { exit 110i32; },
        (ShiftRange) { exit 111i32; },
        (CastRange) { exit 112i32; },
        (BadStep) { exit 113i32; },
        (BorrowOverlap) { exit 114i32; },
        (RequiresViolated) { exit 115i32; },
        (EnsuresViolated) { exit 116i32; },
        (InvariantViolated) { exit 117i32; },
        (Interrupted) { exit 118i32; },
        (NotFound) { exit 119i32; },
        (Exists) { exit 120i32; },
        (CrossDevice) { exit 121i32; },
        (BadPath) { exit 122i32; },
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
