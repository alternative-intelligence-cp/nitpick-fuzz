#!/bin/bash
# M11 vf0007 -- meta/specs/VERIFICATION_REFERENCE.md:7
# claim: The compiler writes every function's proof obligations as SMT-LIB2 text under `--obligations DIR`: numbered .smt2 files holding (check-sat) queries, plus index.txt and rows.txt.
# expect: sh:0
cat > vf0007.npk <<'NPK'
mod:vf0007;

func:v32 = int32(int32:x) never fails { pass x; };

func:quot = int32(int32:a, int32:b) never fails { pass (a / b); };

func:main = int32(cstring[]:_~argv) {
    int32:q = raw quot(raw v32(10i32), raw v32(2i32));
    if (q != 5i32) { exit 10i32; }
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
"$NPKC" vf0007.npk --obligations obl -o vf0007.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" '$3 == k && index($6, m) > 0' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" '$3 == k && index($6, m) > 0 { print $f }' obl/rows.txt; }
ls obl/*.smt2 >/dev/null 2>&1 || exit 1
grep -q 'check-sat' obl/*.smt2 || exit 1
[ -s obl/index.txt ] || exit 1
[ -s obl/rows.txt ] || exit 1
exit 0
