#!/bin/bash
# M11 bd0451 -- meta/specs/BUILD_REFERENCE.md:451
# claim: `npkg build` reads the lock: with none, it refuses with D-078's sentence, "a missing lock is an error".
# expect: sh:0
mkdir -p src
cat > nitpick.toml <<'EOF'
[project]
name    = "demo"
version = "0.1.0"

[build]
entry     = "src/main.npk"
output    = "build/demo"
opt-level = 0

[toolchain]
llvm          = "20.1.2"
llc-flags     = ["-O0", "-filetype=obj", "-relocation-model=static"]
llc-opt-flags = ["-O2", "-filetype=obj", "-relocation-model=static"]
opt-flags     = ["-O2", "-S"]
lld-flags     = ["-static"]
EOF
cat > src/main.npk <<'EOF'
mod:main;

func:main = int32(cstring[]:_~argv) {
    exit 3i32;
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
"$NPKG" build > npkg.out 2>&1; rc=$?
echo "rc=$rc"; head -3 npkg.out | cut -c1-200
[ $rc -ne 0 ] && grep -q -F -- 'a missing lock is an error' npkg.out
