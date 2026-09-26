#!/bin/bash
# M11 vf0531 -- meta/specs/VERIFICATION_REFERENCE.md:531
# claim: terminate rows: an entry row (signed measures only), a preservation row, and one per continue: a signed loop has two, an unsigned one one, a signed one with a continue three.
# expect: sh:0
cat > vf0531.npk <<'NPK'
mod:vf0531;

func:v32 = int32(int32:x) never fails { pass x; };
func:vu32 = uint32(uint32:x) never fails { pass x; };

func:up = int32(int32:n) never fails {
    int32:i = 0i32;
    while (i < n) decreases n - i { i = i + 1i32; }
    pass i;
};
func:down = uint32(uint32:u0) never fails {
    uint32:u = u0;
    while (u > 0u32) decreases u { u = u - 1u32; }
    pass u;
};
func:skip = int32(int32:n) never fails {
    int32:i = 0i32;
    int32:odd = 0i32;
    while (i < n) decreases n - i {
        i = i + 1i32;
        if ((i % 2i32) == 1i32) { odd = odd + 1i32; continue; }
    }
    pass odd;
};

func:main = int32(cstring[]:_~argv) {
    int32:a = raw up(raw v32(3i32));
    uint32:b = raw down(raw vu32(3u32));
    int32:c = raw skip(raw v32(4i32));
    if (a != 3i32) { exit 10i32; }
    if (b != 0u32) { exit 11i32; }
    if (c != 2i32) { exit 12i32; }
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
"$NPKC" vf0531.npk --obligations obl -o vf0531.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" '$3 == k && index($6, m) > 0' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" '$3 == k && index($6, m) > 0 { print $f }' obl/rows.txt; }
[ "$(rows terminate vf0531.up)" -eq 2 ] || exit 1
[ "$(rows terminate vf0531.down)" -eq 1 ] || exit 1
[ "$(rows terminate vf0531.skip)" -eq 3 ] || exit 1
exit 0
