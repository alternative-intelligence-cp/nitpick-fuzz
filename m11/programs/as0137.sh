#!/bin/bash
# M11 as0137 -- meta/specs/AST_REFERENCE.md:137
# claim: A failure contract is `fails on …` or `never fails`: an extern method declared `never fails` compiles.
# expect: sh:0
refused() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 1 ] || return 1
    ! grep -q 'NITPICK-EMIT-002' npkc.out || return 1
    [ -z "$2" ] || grep -q -- "$2" npkc.out
}
accepted() {
    "$NPKC" "$1" -o p.ll > npkc.out 2>&1; rc=$?
    head -4 npkc.out
    [ $rc -eq 0 ] && [ -s p.ll ]
}
cp "$(dirname "$NPKC")/../../lib/nbridge.npk" "$(dirname "$NPKC")/../../lib/nsys.npk" . || exit 5
cat > r.npk <<'EOF'
mod:r;
use "./nbridge.npk".*;

extern:"mockif" = {
    func:probe = int64(Bridge->:b, Duration:within) never fails;
};

func:main = int32(cstring[]:_~argv) {
    exit 0i32;
};

func:failsafe = int32(Error:e) {
    pick (e) {
        (EShmCreate) { exit 60i32; },
        (EShmSeal) { exit 61i32; },
        (EShmMap) { exit 62i32; },
        (EDriverSpawn) { exit 63i32; },
        (EDriverProtocol) { exit 64i32; },
        (EDriverFault) { exit 65i32; },
        (EDriverDeadline) { exit 66i32; },
        (ERingFull) { exit 67i32; },
        (EBridgePoisoned) { exit 68i32; },
        (EDriverError) { exit 69i32; },
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
accepted r.npk
