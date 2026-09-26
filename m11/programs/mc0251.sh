#!/bin/bash
# M11 mc0251 -- meta/specs/MACRO_REFERENCE.md:251
# claim: Exceeding the iteration bound is a compile error naming the macro and the chain that reached the bound: both ping_m and pong_m appear in the diagnostic.
# expect: sh:0
cat > p.npk <<'NPKEOF'
mod:p;
macro:ping_m = () {
    func:from_ping = int32() never fails { pass 1i32; };
    #pong_m();
};
macro:pong_m = () {
    func:from_pong = int32() never fails { pass 2i32; };
    #ping_m();
};

#ping_m();

func:main = int32(cstring[]:_~argv) {
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
NPKEOF
out=$("$NPKC" p.npk -o p.ll 2>&1); rc=$?
printf '%s\n' "$out" | grep NITPICK | head -5
[ "$rc" -eq 1 ] || exit 2
printf '%s\n' "$out" | grep -q 'ping_m' || exit 3
printf '%s\n' "$out" | grep -q 'pong_m' || exit 4
exit 0
