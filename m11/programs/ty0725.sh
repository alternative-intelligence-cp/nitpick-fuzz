#!/bin/bash
# M11 ty0725 -- meta/specs/TYPE_REFERENCE.md:725
# claim: A twisted division has no row: a function dividing two tbb32s has no div-zero or div-min row.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
cat > p.npk <<'NPK_EOF'
mod:p;

func:vt32 = tbb32(tbb32:x) never fails { pass x; };

func:f = tbb32(tbb32:a, tbb32:b) never fails { pass (a / b); };
func:main = int32(cstring[]:_~argv) {
    tbb32:q = raw f(raw vt32(7tbb32), raw vt32(2tbb32));
    if (is_err(q)) { exit 10i32; }
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
[ -f ob/rows.txt ] || { echo "no rows.txt"; ls ob; exit 4; }
rows() { awk -F'\t' -v f="$1" -v k="$2" 'BEGIN { re = "(^|[^A-Za-z0-9_])" f "([^A-Za-z0-9_]|$)" } (k == "*" || $3 == k) && $6 ~ re' ob/rows.txt; }
n() { rows "$1" "$2" | wc -l | tr -d ' '; }
kinds() { rows "$1" '*' | cut -f3 | sort | uniq -c | tr -s ' ' | tr '\n' ';'; }
echo "f's kinds: $(kinds f)"
[ "$(n f div-zero)" -eq 0 ] || exit 10
[ "$(n f div-min)" -eq 0 ] || exit 11
exit 0
