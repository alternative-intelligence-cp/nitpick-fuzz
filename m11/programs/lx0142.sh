#!/bin/bash
# M11 lx0142 -- meta/specs/LEXICAL_REFERENCE.md:142
# claim: `gc`: none is a keyword, so a local of that name compiles.
# expect: sh:0
FAILS=""
probe() {
    sed "s/WORD/$2/g" "$1" > k.npk
    "$NPKC" k.npk -o k.ll > k.out 2>&1; rc=$?
    if [ "$rc" != "$3" ] || grep -q 'NITPICK-EMIT-002' k.out; then
        FAILS="$FAILS $2[$1:rc=$rc:$(grep -m1 -o 'NITPICK-[A-Z]*-[0-9]*' k.out)]"
    fi
}
cat > local.t <<'EOF'
mod:k;

func:main = int32(cstring[]:_~argv) {
    int32:WORD = 1i32;
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
for w in gc; do probe local.t $w 0; done
echo "exceptions:${FAILS:- none}"
[ -z "$FAILS" ]
