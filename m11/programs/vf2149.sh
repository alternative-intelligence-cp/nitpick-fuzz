#!/bin/bash
# M11 vf2149 -- meta/specs/VERIFICATION_REFERENCE.md:2149
# claim: The floor object carries `.note.GNU-split-stack` and `.note.GNU-no-split-stack`.
# expect: sh:0
llvm-readelf -S "$NPKRT" > s.txt 2>&1 || exit 3
grep -q 'note.GNU-split-stack' s.txt && grep -q 'note.GNU-no-split-stack' s.txt
