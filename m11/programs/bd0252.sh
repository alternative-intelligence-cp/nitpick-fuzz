#!/bin/bash
# M11 bd0252 -- meta/specs/BUILD_REFERENCE.md:252
# claim: The floor's object carries the notes `.note.GNU-split-stack` and `.note.GNU-no-split-stack`.
# expect: sh:0
llvm-readelf -S "$NPKRT" > s.txt 2>&1 || exit 3
grep -o 'note.GNU[a-z-]*' s.txt | sort -u
grep -q 'note.GNU-split-stack' s.txt && grep -q 'note.GNU-no-split-stack' s.txt
