#!/bin/bash
# M11 tr0622 -- meta/specs/TRAITS_REFERENCE.md:622
# claim: Two impls of one trait for one type are refused, reported at the SECOND impl.
# expect: sh:0
cat > r.npk <<'EOF'
mod:r;

trait:S = { func:s = int32(Self:self) never fails; };
struct:P = { int32:n; };
impl:P:S = { func:s = int32(P:self) never fails { pass 1i32; }; };
impl:P:S = { func:s = int32(P:self) never fails { pass 2i32; }; };

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
EOF
"$NPKC" r.npk -o r.ll > npkc.out 2>&1; rc=$?
head -3 npkc.out | cut -c1-160
[ $rc -eq 1 ] && grep -m1 '^NITPICK-' npkc.out | grep -q 'r.npk:6:'
