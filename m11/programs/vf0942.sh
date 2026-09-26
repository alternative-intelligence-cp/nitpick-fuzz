#!/bin/bash
# M11 vf0942 -- meta/specs/VERIFICATION_REFERENCE.md:942
# claim: The verified build refuses a program whose `prove` row is not discharged (NITPICK-VERIFY-001), while the plain build accepts it.
# expect: sh:0
cat > p.npk <<'NPK_EOF'
mod:p;

func:v32 = int32(int32:x) never fails { pass x; };

func:fpv = int32(int32:d) never fails {
    prove(d != 0i32);
    pass d;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fpv(raw v32(1i32)));
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
NPK_EOF
"$NPKC" p.npk -o p.ll >out.txt 2>err.txt; rc=$?
[ "$rc" -eq 0 ] || { echo "plain build: npkc exit $rc"; head -c 600 err.txt; exit 3; }
echo '# nitpick.obligations v1' > m.txt
"$NPKC" p.npk -o e.ll --elide m.txt >out2.txt 2>err2.txt; rc=$?
[ "$rc" -eq 1 ] || { echo "verified build without the prove discharged: npkc exit $rc"; head -c 600 err2.txt; exit 10; }
grep -q 'NITPICK-VERIFY-001' err2.txt || { echo "refused without VERIFY-001"; head -c 600 err2.txt; exit 11; }
exit 0
