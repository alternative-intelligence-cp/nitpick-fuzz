#!/bin/bash
# M11 mc0220 -- meta/specs/MACRO_REFERENCE.md:220
# claim: NITPICK-061 (MACRO_HYGIENE_VIOLATION) no longer exists: a macro whose free name resolves differently at the call site compiles with no such diagnostic.
# expect: sh:0
cat > p.npk <<'NPKEOF'
mod:p;
fixed int32:shared = 100i32;

macro:report = () { shared + 1i32; };

func:main = int32(cstring[]:_~argv) {
    int32:shared = 5i32;
    int32:a = #report();
    if (a != 101i32) { exit 10i32; }
    if (shared != 5i32) { exit 11i32; }
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
[ "$rc" -eq 0 ] || exit 2
if printf '%s\n' "$out" | grep -qE 'NITPICK-061|HYGIENE'; then exit 3; fi
exit 0
