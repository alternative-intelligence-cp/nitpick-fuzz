#!/bin/bash
# M11 vf0306 -- meta/specs/VERIFICATION_REFERENCE.md:306
# claim: A write to a limited field of a limited binding is two limit rows (the field's and the root's): adding the statement `t.n = v` adds two limit rows to main.
# expect: sh:0
mkdir a b
cat > a/vf0306.npk <<'NPK'
mod:vf0306;

func:v64 = int64(int64:x) never fails { pass x; };

Rules<int64>:r_n = { $ >= 0i64 };
struct:Tk = { limit<r_n> int64:n; int64:m; };
Rules<Tk>:r_t = { $.m >= 0i64 };

func:main = int32(cstring[]:_~argv) {
    limit<r_t> Tk:t = Tk{ n: 1i64, m: 1i64 };
    t.n = raw v64(2i64);
    if (t.n != 2i64) { exit 10i32; }
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
cat > b/vf0306.npk <<'NPK'
mod:vf0306;

Rules<int64>:r_n = { $ >= 0i64 };
struct:Tk = { limit<r_n> int64:n; int64:m; };
Rules<Tk>:r_t = { $.m >= 0i64 };

func:main = int32(cstring[]:_~argv) {
    limit<r_t> Tk:t = Tk{ n: 1i64, m: 1i64 };
    if (t.n != 2i64) { exit 10i32; }
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
"$NPKC" a/vf0306.npk --obligations oa -o a.ll >a.out 2>&1 || exit 3
"$NPKC" b/vf0306.npk --obligations ob -o b.ll >b.out 2>&1 || exit 3
na=$(awk -F'\t' '$3 == "limit" && $6 == "@main"' oa/rows.txt | wc -l)
nb=$(awk -F'\t' '$3 == "limit" && $6 == "@main"' ob/rows.txt | wc -l)
[ $((na - nb)) -eq 2 ] || exit 1
exit 0
