#!/bin/bash
# M11 bd0268 -- meta/specs/BUILD_REFERENCE.md:268
# claim: A unit that does not define `failsafe` declares `@npk_failsafe`, so a non-root module compiled alone assembles: llc accepts it.
# expect: sh:0
cat > lib.npk <<'EOF'
mod:lib;
error:E1;
pub func:f = int32(int32:x) { if (x > 9i32) { fail E1; } pass (x * 2i32); };
EOF
"$NPKC" lib.npk -o lib.ll > npkc.out 2>&1; rc=$?
head -2 npkc.out
[ $rc -eq 0 ] || exit 3
grep -m1 'npk_failsafe' lib.ll | cut -c1-100
grep -q '^declare[^\n]*@npk_failsafe' lib.ll && llc -O0 -filetype=obj -relocation-model=static lib.ll -o lib.o
