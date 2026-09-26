#!/bin/bash
# M11 vf0848 -- meta/specs/VERIFICATION_REFERENCE.md:848
# claim: The catalogue lists every obligation kind exhaustively: every row the compiler writes to rows.txt carries one of its 22 kinds.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:v32 = int32(int32:x) never fails { pass x; };
func:v64 = int64(int64:x) never fails { pass x; };

Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fs = int32(int32:x, int32:n) never fails { pass (x << n); };
func:need = int32(limit<r_pos> int32:m) { pass (m + 1i32); };
func:fl = int32(int32[]:xs, int64:i) never fails { pass xs[i]; };
func:main = int32(cstring[]:_~argv) {
    int32:i = 0i32;
    while (i < 3i32) decreases 3i32 - i { i = i + 1i32; }
    int32[4]:arr = [1i32, 2i32, 3i32, 4i32];
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fs(raw v32(1i32), raw v32(2i32)));
    discard(raw fl(arr[0i64...4i64], raw v64(1i64)));
    int32:r = need(raw v32(3i32)) ?! E9;
    int32:k = pick (r) { (4i32) { give 0i32; }, (*) { give 10i32; } };
    exit k;
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
        (E9) { exit 89i32; },
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
K=" div-zero div-min overflow bounds cast-range exhaustive requires ensures invariant limit limit-subsume terminate stack-depth err-exit failsafe-post loop-step shift-range prove assert-static disjoint floor-spec floor-model "
nk=$(cut -f3 ob/rows.txt | sort -u | wc -l | tr -d ' ')
[ "$nk" -ge 5 ] || { echo "only $nk kinds: the program should have produced more"; exit 10; }
bad=$(cut -f3 ob/rows.txt | sort -u | while read -r k; do case "$K" in *" $k "*) ;; *) echo "$k";; esac; done)
[ -z "$bad" ] || { echo "kinds outside the catalogue: $bad"; exit 11; }
exit 0
