#!/bin/bash
# M11 vf0925 -- meta/specs/VERIFICATION_REFERENCE.md:925
# claim: In the verified build a direct call whose `limit-subsume` row is discharged calls `<symbol>.body`, skipping the callee's entry check; in the plain build it calls the entry.
# expect: sh:0
# rows.txt, tab-separated: NNNN k kind hash encoded symbol site role group traps tier ctx
# index.txt: NNNN symbol checks group measured
cat > p.npk <<'NPK_EOF'
mod:p;

func:v32 = int32(int32:x) never fails { pass x; };

Rules<int32>:r_pos = { $ > 0i32 };
error:E9;
func:narrow = int32(limit<r_pos> int32:n) { pass n; };
func:fcaller = int32(int32:v) { pass (narrow(v) ?! E9); };
func:main = int32(cstring[]:_~argv) {
    int32:r = fcaller(raw v32(5i32)) ?! E9;
    exit (r - 5i32);
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
fbody() { awk -v a=".$1\"(" -v b="@npk_$1(" 'index($0, "define ") == 1 && (index($0, a) > 0 || index($0, b) > 0) { on = 1 } on { print } on && /^}/ { on = 0 }' "$2"; }
manifest() { { echo '# nitpick.obligations v1'; awk -F'\t' "$1"' { print $4 " " $3 " " $11 " discharged elided " $6 }' ob/rows.txt; } > m.txt; }
elide() { "$NPKC" p.npk -o e.ll --elide m.txt >out2.txt 2>err2.txt; rc=$?; if [ "$rc" -ne 0 ]; then echo "npkc --elide exit $rc"; head -c 800 err2.txt; exit 5; fi; }
assumes() { fbody "$1" "$2" | grep -c 'call void @llvm.assume('; }
traps() { fbody "$1" "$2" | grep -cF "@npk_trap(i32 $3)"; }
want "calls of narrow.body in fcaller, plain build" "$(fbody fcaller p.ll | grep -c 'narrow\.body')" 0 10
manifest '$3=="limit-subsume"'
elide
b=$(fbody fcaller e.ll | grep -c 'narrow\.body')
[ "$b" -ge 1 ] || { echo "fcaller does not call narrow.body in the verified build"; exit 11; }
exit 0
