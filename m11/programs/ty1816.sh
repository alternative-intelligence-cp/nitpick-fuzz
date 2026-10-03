#!/bin/bash
# M11 ty1816 -- meta/specs/TYPE_REFERENCE.md:1816
# claim: A tensor's rank is capped at 9: `tensor_of` with ten dims fails, and with three succeeds.
# expect: sh:0
build() {
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
cp "$LIB/ntensor.npk" . || exit 5
cat > r.npk <<'NPK_EOF'
mod:r;
use "./ntensor.npk".*;

func:main = int32(cstring[]:_~argv) {
    int64[10]:d10 = [1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64, 1i64];
    Result<tensor<int64>>:r = tensor_of::<int64>(d10[0i64...10i64]);
    if (!(r.is_error)) { exit 10i32; }
    int64[3]:d3 = [2i64, 3i64, 4i64];
    tensor<int64>:t = tensor_of::<int64>(d3[0i64...3i64]) ?! BadShape;
    if (t.ndims != 3i64) { exit 11i32; }
    exit 0i32;
};

func:failsafe = int32(Error:e) {
    pick (e) {
        (ntensor.BadShape) { exit 80i32; },
        (ntensor.BadIndex) { exit 81i32; },
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
NPK_EOF
build r.npk || exit $?
legs 0
