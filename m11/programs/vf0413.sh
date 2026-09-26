#!/bin/bash
# M11 vf0413 -- meta/specs/VERIFICATION_REFERENCE.md:413
# claim: Conformance is two rows per impl method whose trait method carries a contract (role `conform`, no guard).
# expect: sh:0
cat > vf0413.npk <<'NPK'
mod:vf0413;

error:E9;
trait:Sized = { func:size = int32(Self:self, int32:scale) requires scale > 0i32 ensures result >= 0i32; };
struct:Wide = { int32:w; };
impl:Wide:Sized = {
    func:size = int32(Wide:_~self, int32:scale) requires scale > -1i32 ensures result >= 1i32 { pass 4i32; };
};
func:through = int32(dyn Sized:s) { pass ((s.size(1i32)) ?! E9); };

func:main = int32(cstring[]:_~argv) {
    Wide:a = Wide{ w: 3i32 };
    int32:r = through(a) ?! E9;
    if (r != 4i32) { exit 10i32; }
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
"$NPKC" vf0413.npk --obligations obl -o vf0413.ll >npkc.out 2>&1 || exit 3
[ -f obl/rows.txt ] || exit 4
rows() { awk -F'\t' -v k="$1" -v m="$2" '$3 == k && index($6, m) > 0' obl/rows.txt | wc -l | tr -d ' '; }
field() { awk -F'\t' -v k="$1" -v m="$2" -v f="$3" '$3 == k && index($6, m) > 0 { print $f }' obl/rows.txt; }
[ "$(awk -F'\t' '$8 == "conform" && index($6, "vf0413.") > 0' obl/rows.txt | wc -l)" -eq 2 ] || exit 1
exit 0
