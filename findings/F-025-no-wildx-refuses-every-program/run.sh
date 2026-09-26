#!/bin/bash
# F-025: compile a program that uses no `wildx` (the commissioning canary) with and
# without `--extra-picky=no-wildx`. VERIFICATION_REFERENCE:808 -- "--extra-picky=no-wildx
# excludes runtime code generation" -- so a program without wildx compiles under it.
# usage: NPKC=<compiler> bash run.sh    (from this directory)
set -u
t=$(mktemp -d); cp n1_canary.npk "$t/"; cd "$t"
"$NPKC" n1_canary.npk -o a.ll > a.txt 2>&1; ra=$?
"$NPKC" n1_canary.npk --extra-picky=no-wildx -o b.ll > b.txt 2>&1; rb=$?
echo "plain: npkc=$ra   no-wildx: npkc=$rb, $(grep -c 'NITPICK-WILDX-003' b.txt) x WILDX-003 ($(grep -o 'NITPICK-WILDX-003 [a-z_]*\.npk' b.txt | sort | uniq -c | tr -s ' ' | tr '\n' ' ')), $(grep -c 'NITPICK-DIAG-001' b.txt) x DIAG-001; first: $(grep -m1 NITPICK-WILDX-003 b.txt | cut -c1-120)"
cd / && rm -rf "$t"
