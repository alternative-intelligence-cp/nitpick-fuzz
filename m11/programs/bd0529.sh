#!/bin/bash
# M11 bd0529 -- meta/specs/BUILD_REFERENCE.md:529
# claim: A diagnostic renders as `CODE path:line:col: message`, with `note ` in front of a note.
# expect: sh:0
cat > r.npk <<'EOF'
mod:r;

mod:m = {
    func:hid = int32() never fails { pass 1i32; };
};

func:main = int32(cstring[]:_~argv) {
    int32:v = raw m.hid();
    exit 0i32;
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
"$NPKC" r.npk -o r.ll > npkc.out 2>&1; rc=$?
head -3 npkc.out | cut -c1-120
[ $rc -eq 1 ] || exit 3
head -1 npkc.out | grep -q -E '^NITPICK-[A-Z]+-[0-9]{3} r\.npk:[0-9]+:[0-9]+: ' && grep -q -E '^note NITPICK-[A-Z]+-[0-9]{3} r\.npk:[0-9]+:[0-9]+: ' npkc.out
