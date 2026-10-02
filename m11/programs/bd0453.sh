#!/bin/bash
# M11 bd0453 -- meta/specs/BUILD_REFERENCE.md:453
# claim: `npkg update` is refused today by name: "there is nothing to resolve in a single-repository world".
# expect: sh:0
"$NPKG" update > npkg.out 2>&1; rc=$?
echo "rc=$rc"; head -3 npkg.out | cut -c1-200
[ $rc -ne 0 ] && grep -q -F -- 'there is nothing to resolve in a single-repository world' npkg.out
