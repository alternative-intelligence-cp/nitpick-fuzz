#!/bin/bash
# M11 bi0368 -- meta/specs/BUILTIN_REFERENCE.md:368
# claim: The compiler has a `--seccomp` option (a kernel-enforced allowlist).
# expect: sh:0
cat > s.npk <<'EOF'
mod:s;
func:main = int32(cstring[]:_~argv) { exit 0i32; };
func:failsafe = int32(Error:e) { exit 9i32; };
EOF
out=$("$NPKC" s.npk -o s.ll --seccomp 2>&1); rc=$?
echo "$out" | head -3
[ $rc -eq 0 ] && [ -f s.ll ]
