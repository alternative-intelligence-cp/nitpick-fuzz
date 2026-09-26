#!/bin/bash
# M11 vf0992 -- meta/specs/VERIFICATION_REFERENCE.md:992
# claim: rows.txt's eleventh field is the tier: `int` for an Int/Bool cone, `bv` where a bit-vector crossing is, `fp` where a float sort is, `-` for an unencoded or checker row.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:v32 = int32(int32:x) never fails { pass x; };
func:v64 = int64(int64:x) never fails { pass x; };

Rules<flt64>:r_unit = { $ >= 1.0f64, $ <= 2.0f64 };
Rules<string>:r_ne = { $.len > 0i64 };
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fbx = int32(int32:k, int32:m) never fails { pass (100i32 / ((k & m) | 1i32)); };
func:ratio = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:q = a / b;
    prove(q >= 0.5f64);
    pass q;
};
func:fp1 = int32(int32:x) never fails {
    int32:r = 0i32;
    pick (x) { (1i32) { r = 10i32; }, (*) { r = 20i32; } }
    pass r;
};
func:flim = int64(int64:n) never fails {
    limit<r_ne> string:s = "abc";
    if (n > 0i64) { s = "de"; }
    pass s.len;
};
func:main = int32(cstring[]:_~argv) {
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fbx(raw v32(6i32), raw v32(3i32)));
    discard(raw ratio(1.5f64, 2.0f64));
    discard(raw fp1(raw v32(1i32)));
    discard(raw flim(raw v64(1i64)));
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
"$NPKC" p.npk -o p.ll --obligations ob >out.txt 2>err.txt; rc=$?
if [ "$rc" -ne 0 ]; then echo "npkc exit $rc"; head -c 800 err.txt; exit 3; fi
[ -f ob/rows.txt ] && [ -f ob/index.txt ] || { echo "no rows.txt or index.txt"; ls ob; exit 4; }
rows() { awk -F'\t' -v f="$1" -v k="$2" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } (k == "*" || $3 == k) && $6 ~ re' ob/rows.txt; }
n() { rows "$1" "$2" | wc -l | tr -d ' '; }
col() { rows "$1" "$2" | cut -f"$3" | sort -u | tr '\n' ' ' | sed 's/ $//'; }
file_of() { awk -F'\t' -v f="$1" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } $2 ~ re { print "ob/" $1 ".smt2"; exit }' ob/index.txt; }
want() { [ "$2" = "$3" ] || { echo "$1: got [$2], want [$3]"; exit "$4"; }; }
want "tier of an Int division's div-zero row" "$(col fq div-zero 11)" int 10
want "tier of a div-zero row over (k & m) | 1" "$(col fbx div-zero 11)" bv 11
want "tier of a flt64 prove row" "$(col ratio prove 11)" fp 12
want "tier of a checker (exhaustive) row" "$(col fp1 exhaustive 11)" - 13
want "tier of an unencoded (string limit) row" "$(col flim limit 11)" - 14
exit 0
