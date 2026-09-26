# F-025 — `--extra-picky=no-wildx` refuses every program, the commissioning canary included, with 256 `WILDX-003` diagnostics located in the prelude

**The shape.** VERIFICATION_REFERENCE §7:808: "`--extra-picky=no-wildx` excludes
runtime code generation". A program without `wildx` therefore compiles under it. At
HUNT2 the canary, which uses no `wildx`, compiles plainly, but under the flag npkc
exits 1:
- 256 `NITPICK-WILDX-003` diagnostics ("`wildx` is excluded by `--extra-picky=no-wildx`
  (D-035)"), every one located in `prelude.npk`, and a `DIAG-001` (the cap);
- the first at `prelude.npk:125:47`, a line holding
  `impl:gid:ToString = { func:to_string = string(gid:self) … }` and no `wildx` at all.

The flag cannot be used on any program.

Found by M11's claims `vf0808` (a program without wildx compiles under the flag) and
`vf0811` (a program using plain `wild` compiles under it). Both scripts exit 1 at their
first compile under the flag.

## Verdicts (`run.sh`, recorded in `VERDICTS.txt`)

| compiler | plain compile | under `--extra-picky=no-wildx` |
|---|---|---|
| HUNT2 `9126350` (×2) | npkc 0 | npkc **1**: 256 × `WILDX-003` in `prelude.npk`, 1 × `DIAG-001` |
| baseline `c3bdae2` | npkc 0 | the same |
| `1b4f0c6` | npkc 0 | the same |

The control is the plain compile of the same file.

## Deduplication

No entry of `KNOWN_DEFECTS.md` concerns a compiler flag. BUILTIN's M11 row `bi0375`
(documentation) found that npkc knows only `--extra-picky=no-wildx`. This finding is
that the one flag it knows refuses everything. Present at the baseline.

## Measured, and inferred

- **Measured:** the counts and the first location, at three compilers.
- **Inferred, not measured:** that the `wildx` check runs over the prelude's own text,
  or maps its positions wrongly. Line 125 holds no `wildx`.
