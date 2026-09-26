#!/bin/bash
# M11 vf0607 -- meta/specs/VERIFICATION_REFERENCE.md:607
# claim: index.txt carries per file the function's cyclic group (0 for none) and whether it states a measure.
# expect: sh:0
cat > vf0607.npk <<'NPK'
mod:vf0607;

func:v32 = int32(int32:x) never fails { pass x; };

func:fact = int32(int32:n) decreases n never fails {
    if (n <= 0i32) { pass 1i32; }
    pass (n * (raw fact(n - 1i32)));
};
func:quot = int32(int32:a, int32:b) never fails { pass (a / b); };

func:main = int32(cstring[]:_~argv) {
    int32:f = raw fact(raw v32(4i32));
    int32:q = raw quot(raw v32(10i32), raw v32(2i32));
    if ((f + q) != 29i32) { exit 10i32; }
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
"$NPKC" vf0607.npk --obligations obl -o vf0607.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" 'function hit(s) { if (m ~ /\.main$/) return s == "@main"; if (m ~ /\.$/) return index(s, m) > 0 || s == "@main"; return index(s, m) > 0 } $3 == k && hit($6)' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" 'function hit(s) { if (m ~ /\.main$/) return s == "@main"; if (m ~ /\.$/) return index(s, m) > 0 || s == "@main"; return index(s, m) > 0 } $3 == k && hit($6) { print $f }' obl/rows.txt; }
awk -F'\t' 'index($2, "vf0607.fact") > 0 { n++; if ($4 == "0" || $5 != "1") bad = 1 } END { exit (n > 0 && !bad) ? 0 : 1 }' obl/index.txt || exit 1
awk -F'\t' 'index($2, "vf0607.quot") > 0 { n++; if ($4 != "0" || $5 != "0") bad = 1 } END { exit (n > 0 && !bad) ? 0 : 1 }' obl/index.txt || exit 1
exit 0
