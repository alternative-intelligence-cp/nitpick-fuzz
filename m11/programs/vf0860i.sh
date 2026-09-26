#!/bin/bash
# M11 vf0860i -- meta/specs/VERIFICATION_REFERENCE.md:860
# claim: A loop over `xs.len` indexing `xs[i]` states the length as `|npk.len|` in its obligation file.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:fl = int32(int32[]:xs) never fails {
    int32:acc = 0i32;
    for (int64:i in 0i64...xs.len) { acc = acc +% xs[i]; }
    pass acc;
};
func:main = int32(cstring[]:_~argv) {
    int32[4]:a = [1i32, 2i32, 3i32, 4i32];
    discard(raw fl(a[0i64...4i64]));
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
f=$(file_of fl); [ -n "$f" ] && [ -f "$f" ] || { echo "no obligation file for fl"; exit 10; }
grep -qF '|npk.len|' "$f" || { echo "no |npk.len| in $f"; exit 11; }
exit 0
