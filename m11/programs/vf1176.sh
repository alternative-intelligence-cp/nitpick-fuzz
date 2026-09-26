#!/bin/bash
# M11 vf1176 -- meta/specs/VERIFICATION_REFERENCE.md:1176
# claim: A negated comparison is not a bound (it holds of NaN): floats bounded only by `!($ < 1.0)` and `!($ > 2.0)` get no twin.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:vf64 = flt64(flt64:x) never fails { pass x; };

Rules<flt64>:r_unit = { $ >= 1.0f64, $ <= 2.0f64 };
Rules<flt32>:r_u32 = { $ >= 1.0f32, $ <= 2.0f32 };
Rules<flt64>:r_neg = { !($ < 1.0f64), !($ > 2.0f64) };
func:ratio = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:q = a / b;
    prove(q >= 0.5f64);
    pass q;
};
func:ratio32 = flt32(limit<r_u32> flt32:a, limit<r_u32> flt32:b) never fails {
    flt32:q = a / b;
    prove(q >= 0.5f32);
    pass q;
};
func:hyp = flt64(limit<r_unit> flt64:a, limit<r_unit> flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:hypu = flt64(flt64:a, flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:hypn = flt64(limit<r_neg> flt64:a, limit<r_neg> flt64:b) never fails {
    flt64:s = #sqrt(a * a + b * b);
    prove(s >= 0.0f64);
    pass s;
};
func:sameq = bool(limit<r_unit> flt64:a) never fails {
    prove(a == a);
    pass (a == a);
};
func:fent = tbb32(flt64:x) never fails { pass (x => tbb32); };
func:ffl = flt64(flt64:a, flt64:b) never fails { pass (((a + b) * (a - b)) / b); };
func:ffm = flt64(flt64:a, flt64:b) never fails { pass (a % b); };
func:main = int32(cstring[]:_~argv) {
    discard(raw ratio(1.5f64, 2.0f64));
    discard(raw ratio32(1.5f32, 2.0f32));
    discard(raw hyp(1.5f64, 2.0f64));
    discard(raw hypu(raw vf64(1.5f64), raw vf64(2.0f64)));
    discard(raw hypn(1.5f64, 2.0f64));
    discard(raw sameq(1.5f64));
    discard(raw fent(raw vf64(3.5f64)));
    discard(raw ffl(raw vf64(1.5f64), raw vf64(2.0f64)));
    discard(raw ffm(raw vf64(1.5f64), raw vf64(2.0f64)));
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
nt() { f=$(file_of "$1"); [ -n "$f" ] || { echo "no obligation file for $1"; exit "$2"; }; t=${f%.smt2}.t2.smt2; [ ! -f "$t" ] || { echo "$1 has a twin $t"; exit "$2"; }; }

nt hypn 10
exit 0
