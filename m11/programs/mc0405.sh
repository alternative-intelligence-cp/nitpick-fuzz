#!/bin/bash
# M11 mc0405 -- meta/specs/MACRO_REFERENCE.md:405
# claim: A diagnostic inside an expansion carries the macro body's location: "cannot find only_local" is reported at the macro BODY's line, not the invocation's.
# expect: sh:0
cat > p.npk <<'NPKEOF'
mod:p;
macro:grab = () { only_local + 1i32; };
func:main = int32(cstring[]:_~argv) {
    int32:only_local = 3i32;
    int32:s = #grab();
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
first=$(printf '%s\n' "$out" | grep -m1 'NITPICK-')
echo "first: $first"
printf '%s\n' "$first" | grep -q 'p\.npk:2:' || exit 3
exit 0
