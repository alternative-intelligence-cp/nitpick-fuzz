#!/bin/bash
# M11 bd0016 -- meta/specs/BUILD_REFERENCE.md:16
# claim: npkg reads the manifest: in a directory with none, `npkg build` refuses and names `nitpick.toml`.
# expect: sh:0
"$NPKG" build > npkg.out 2>&1; rc=$?
echo "rc=$rc"; head -3 npkg.out | cut -c1-200
[ $rc -ne 0 ] && grep -q -F -- 'nitpick.toml' npkg.out
