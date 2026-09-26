#!/bin/bash
# M11 mc0256 -- meta/specs/MACRO_REFERENCE.md:256
# claim: The depth bound and the iteration bound are separate and report differently: a too-deep single expansion and a mutual recursion are refused with different diagnostic codes.
# expect: sh:0

d="1i32"
for i in $(seq 1000); do d="(1i32 + $d)"; done
cat > deep.npk <<NPKEOF
mod:deep;
macro:deep_m = () { $d; };
func:main = int32(cstring[]:_~argv) {
    int32:v = #deep_m();
    discard(v);
    exit 0i32;
};
func:failsafe = int32(Error:_~e) { exit 1i32; };
NPKEOF
cat > loopy.npk <<'NPKEOF'
mod:loopy;
macro:ping_m = () {
    func:from_ping = int32() never fails { pass 1i32; };
    #pong_m();
};
macro:pong_m = () {
    func:from_pong = int32() never fails { pass 2i32; };
    #ping_m();
};
#ping_m();
func:main = int32(cstring[]:_~argv) { exit 0i32; };
func:failsafe = int32(Error:_~e) { exit 1i32; };
NPKEOF
o1=$("$NPKC" deep.npk -o deep.ll 2>&1); r1=$?
o2=$("$NPKC" loopy.npk -o loopy.ll 2>&1); r2=$?
c1=$(printf '%s\n' "$o1" | grep -oE 'NITPICK-[A-Z]+-[0-9]+' | sort -u | tr '\n' ' ')
c2=$(printf '%s\n' "$o2" | grep -oE 'NITPICK-[A-Z]+-[0-9]+' | sort -u | tr '\n' ' ')
echo "deep rc=$r1 [$c1] loop rc=$r2 [$c2]"
[ "$r1" -eq 1 ] || exit 2
[ "$r2" -eq 1 ] || exit 3
[ -n "$c1" ] && [ -n "$c2" ] || exit 4
[ "$c1" != "$c2" ] || exit 5
exit 0
