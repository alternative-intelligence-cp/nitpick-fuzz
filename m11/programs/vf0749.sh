#!/bin/bash
# M11 vf0749 -- meta/specs/VERIFICATION_REFERENCE.md:749
# claim: The obligations cover limit, contracts, invariants, prove/assert_static, overflow and index disjointness: one program using each yields a row of each kind.
# expect: sh:0
cat > vf0749.npk <<'NPK'
mod:vf0749;

func:v32 = int32(int32:x) never fails { pass x; };

error:E9;
Rules<int32>:r_positive = { $ > 0i32 };
func:half = int32(int32:n) requires n > 0i32 ensures result >= 0i32 { pass (n / 2i32); };
func:update = int32(int32:i, int32:j, int32[8]:arr) never fails {
    int32->:a = $$m arr[i => int64];
    int32->:b = $$m arr[j => int64];
    <-a = 7i32;
    <-b = 9i32;
    pass ((<-a) + (<-b));
};

func:main = int32(cstring[]:_~argv) {
    limit<r_positive> int32:x = raw v32(3i32);
    int32:h = half(x) ?! E9;
    int32:i = 0i32;
    int32:acc = 0i32;
    while (i < 3i32) decreases 3i32 - i invariant acc >= 0i32 { acc = acc + x; i = i + 1i32; }
    prove(acc >= 0i32);
    assert_static(1i32 < 2i32);
    int32[8]:arr = [0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32, 0i32];
    int32:u = raw update(raw v32(1i32), raw v32(2i32), arr);
    if ((h + acc + u) != 26i32) { exit 10i32; }
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
        (E9) { exit 89i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};
NPK
"$NPKC" vf0749.npk --obligations obl -o vf0749.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" 'function hit(s) { if (m ~ /\.main$/) return s == "@main"; if (m ~ /\.$/) return index(s, m) > 0 || s == "@main"; return index(s, m) > 0 } $3 == k && hit($6)' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" 'function hit(s) { if (m ~ /\.main$/) return s == "@main"; if (m ~ /\.$/) return index(s, m) > 0 || s == "@main"; return index(s, m) > 0 } $3 == k && hit($6) { print $f }' obl/rows.txt; }
for k in limit requires ensures invariant prove assert-static overflow disjoint; do
  [ "$(rows $k vf0749.)" -ge 1 ] || exit 1
done
exit 0
