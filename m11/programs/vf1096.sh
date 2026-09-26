#!/bin/bash
# M11 vf1096 -- meta/specs/VERIFICATION_REFERENCE.md:1096
# claim: Above 64 bits a general bitwise operation stays opaque: `(k & m) | 1` over int128 has no `int2bv`.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:v32 = int32(int32:x) never fails { pass x; };
func:vi128 = int128(int128:x) never fails { pass x; };

func:fq = int32(int32:a, int32:b) never fails { pass (a / b); };
func:fd2 = int32(int32:a, int32:b, int32:c) never fails { pass ((a / b) / c); };
func:fm2 = int32(int32:a, int32:b, int32:c) never fails { pass ((a % b) / c); };
func:fmk = int32(int32:k) never fails { pass (100i32 / ((k & 7i32) + 1i32)); };
func:fbx = int32(int32:k, int32:m) never fails { pass (100i32 / ((k & m) | 1i32)); };
func:fbs = int32(int32:x, int32:n) never fails { pass (100i32 / ((x << n) | 1i32)); };
func:fbw = int128(int128:k, int128:m) never fails { pass (100i128 / ((k & m) | 1i128)); };
func:main = int32(cstring[]:_~argv) {
    discard(raw fq(raw v32(7i32), raw v32(2i32)));
    discard(raw fd2(raw v32(70i32), raw v32(2i32), raw v32(5i32)));
    discard(raw fm2(raw v32(7i32), raw v32(4i32), raw v32(1i32)));
    discard(raw fmk(raw v32(6i32)));
    discard(raw fbx(raw v32(6i32), raw v32(3i32)));
    discard(raw fbs(raw v32(1i32), raw v32(2i32)));
    discard(raw fbw(raw vi128(6i128), raw vi128(3i128)));
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
fof() { f=$(file_of "$1"); [ -n "$f" ] && [ -f "$f" ] || { echo "no obligation file for $1" >&2; exit "$2"; }; echo "$f"; }

f=$(fof fbw 10) || exit 10
if grep -q 'int2bv' "$f"; then echo "a crossing above 64 bits in $f"; exit 11; fi
exit 0
