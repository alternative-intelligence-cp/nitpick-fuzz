# BISECT — the import places across 1.6.0 steps 3g and 3h

The 76 `imported_fixed_*` cells, run by `gen/run.py <worktree> --ids <the 76 ids>` at 3g
(`5bdae98`) and at 3h (`c1a4a05`, whose parent is `5bdae98`); the records are
`results/5bdae98/cells-imported.jsonl` and `results/c1a4a05/cells-imported.jsonl`.

- `6fb85d3` and 3g agree in 76 of 76 cells.
- 3h and HUNT2 `9126350` agree in 60 of 76; the other 16 are DEF-106's writes, refused `TYPE-086` from 4b on.
- Between 3g and 3h, 28 cells moved:

| P | O | 3g `5bdae98` | 3h `c1a4a05` | HUNT2 `9126350` | cells |
|---|---|---|---|---|---|
| imported_fixed_bare | clone | npkc 1 TYPE-001 | 0/0 | 0/0 | `c0343` `c0344` |
| imported_fixed_bare | field_write | npkc 1 TYPE-001 | 95/95 | npkc 1 TYPE-086 | `c0341` `c0342` |
| imported_fixed_bare | read | npkc 1 TYPE-001 | 0/0 | 0/0 | `c0345` `c0346` |
| imported_fixed_same | assign | 95/95 | npkc 1 TYPE-007 | npkc 1 TYPE-086 | `c0355` `c0356` |
| imported_fixed_same | copy | npkc 1 TYPE-046 | npkc 1 TYPE-007 | npkc 1 TYPE-007 | `c0347` `c0348` |
| imported_fixed_same | move | npkc 1 TYPE-084 | npkc 1 TYPE-007,TYPE-084 | npkc 1 TYPE-007,TYPE-084 | `c0349` `c0350` |
| imported_fixed_same | pass_out | npkc 1 TYPE-084 | npkc 1 TYPE-007,TYPE-084 | npkc 1 TYPE-007,TYPE-084 | `c0351` `c0352` |
| imported_fixed_wider | assign | npkc 1 TYPE-027 | npkc 1 TYPE-007,TYPE-027 | npkc 1 TYPE-086 | `c0373` `c0374` |
| imported_fixed_wider | clone | 107/107 | 0/0 | 0/0 | `c0379` `c0380` |
| imported_fixed_wider | copy | npkc 1 TYPE-046 | npkc 1 TYPE-007 | npkc 1 TYPE-007 | `c0365` `c0366` |
| imported_fixed_wider | field_write | 95/0 | 95/95 | npkc 1 TYPE-086 | `c0372` |
| imported_fixed_wider | field_write | 95/107 | 95/95 | npkc 1 TYPE-086 | `c0371` |
| imported_fixed_wider | move | npkc 1 TYPE-084 | npkc 1 TYPE-007,TYPE-084 | npkc 1 TYPE-007,TYPE-084 | `c0367` `c0368` |
| imported_fixed_wider | pass_out | npkc 1 TYPE-084 | npkc 1 TYPE-007,TYPE-084 | npkc 1 TYPE-007,TYPE-084 | `c0369` `c0370` |
| imported_fixed_wider | read | 107/0 | 0/0 | 0/0 | `c0382` |
| imported_fixed_wider | read | 107/107 | 0/0 | 0/0 | `c0381` |

The 12 cells whose refusal gained `TYPE-007` between `6fb85d3` and HUNT2 (`MOVES.md`) change at
3h exactly. Their message is *"expected `Box`, found `Box`"*: the cell's `Box:y` names the importer's own
`struct:Box`, and 3h resolves `TBL[i]` to the table's `Box`. With the table's `Box` imported by name
(`imported_fixed_typed`), the same operations are refused `TYPE-046`/`TYPE-084` at every compiler here:
`c0323` npkc 1 TYPE-046 at `6fb85d3`, 3g, 3h and HUNT2;
`c0324` npkc 1 TYPE-046 at `6fb85d3`, 3g, 3h and HUNT2;
`c0325` npkc 1 TYPE-084 at `6fb85d3`, 3g, 3h and HUNT2;
`c0326` npkc 1 TYPE-084 at `6fb85d3`, 3g, 3h and HUNT2;
`c0327` npkc 1 TYPE-084 at `6fb85d3`, 3g, 3h and HUNT2;
`c0328` npkc 1 TYPE-084 at `6fb85d3`, 3g, 3h and HUNT2.
