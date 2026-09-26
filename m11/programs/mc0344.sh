#!/bin/bash
# M11 mc0344 -- meta/specs/MACRO_REFERENCE.md:344
# claim: A comptime failure inside nested comptime calls names the offending expression and the call chain: the diagnostic mentions inner_div and outer_call and points at the division.
# expect: sh:0
cat > p.npk <<'NPKEOF'
mod:p;
comptime func:inner_div = int32(int32:d) never fails { pass (100i32 / d); };
comptime func:outer_call = int32(int32:d) never fails { pass (raw inner_div(d)); };
func:main = int32(cstring[]:_~argv) {
    int32:v = comptime(outer_call(0i32));
    exit v;
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
printf '%s\n' "$out" | grep -q 'inner_div' || exit 3
printf '%s\n' "$out" | grep -q 'outer_call' || exit 4
printf '%s\n' "$out" | grep -qE 'p\.npk:2:|100i32 / d' || exit 5
exit 0
