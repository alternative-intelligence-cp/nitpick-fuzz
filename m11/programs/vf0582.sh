#!/bin/bash
# M11 vf0582 -- meta/specs/VERIFICATION_REFERENCE.md:582
# claim: A recursive call is one terminate row of the caller's, role `guard`.
# expect: sh:0
cat > vf0582.npk <<'NPK'
mod:vf0582;

func:v32 = int32(int32:x) never fails { pass x; };

func:fact = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 1i32; }
    pass (n * (raw fact(n - 1i32)));
};

func:main = int32(cstring[]:_~argv) {
    int32:f = raw fact(raw v32(5i32));
    if (f != 120i32) { exit 10i32; }
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
"$NPKC" vf0582.npk --obligations obl -o vf0582.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" '$3 == k && index($6, m) > 0' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" '$3 == k && index($6, m) > 0 { print $f }' obl/rows.txt; }
[ "$(rows terminate vf0582.fact)" -eq 1 ] || exit 1
[ "$(field terminate vf0582.fact 8)" = "guard" ] || exit 1
exit 0
