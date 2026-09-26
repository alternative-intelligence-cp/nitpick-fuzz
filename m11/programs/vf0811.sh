#!/bin/bash
# M11 vf0811 -- meta/specs/VERIFICATION_REFERENCE.md:811
# claim: no-wildx is a rule separate from no-wild: a program using `wild` (not wildx) compiles under no-wildx and not under no-wild.
# expect: sh:0
cat > vf0811.npk <<'NPK'
mod:vf0811;

func:main = int32(cstring[]:_~argv) {
    wild int8->:p = alloc(16i64);
    dalloc(p);
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
NPK
"$NPKC" vf0811.npk -o a.ll >a.out 2>&1 || exit 3
"$NPKC" vf0811.npk --extra-picky=no-wildx -o b.ll >b.out 2>&1 || exit 1
"$NPKC" vf0811.npk --extra-picky=no-wild -o c.ll >c.out 2>&1 && exit 1
exit 0
