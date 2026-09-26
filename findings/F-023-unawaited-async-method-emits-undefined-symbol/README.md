# F-023 — an un-awaited async METHOD call is accepted, and the emission calls a symbol it never defines (npkc 0; `llc` and `opt` refuse)

**The shape.** `Result<int64>:n = r.read(buf[…], d);` with `r` a `ByteReader`: an
async trait method called without `await` and bound to a `Result`.
- The checker accepts it.
- npkc exits 0, and the emission contains
  `call { i64, i32 } @"npk.prelude.ByteReader:Reader.read"(…)`, a symbol no function
  defines. `llc` refuses: "use of undefined value '@npk.prelude.ByteReader:Reader.read'"
  (and `opt` likewise).

The same call to a **free** async function is refused, `NITPICK-TYPE-043`: "an `async`
function is called under `await` or spawned with `drop` … a bare call would suspend
where nothing says so". This is what IO_REFERENCE §1:45 ("Every operation is `async`")
and CONCURRENCY_REFERENCE §2.4:143 (an un-awaited call's result "cannot be held") lead
to. The method call escapes that check.

Found by M11's claim `io0045`: the refusal expected, npkc 0 measured, with both legs
unbuildable.

## Verdicts

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | `1b4f0c6` |
|---|---|---|---|
| `i1_unawaited_method_call` | npkc **0**, **llc!1 / opt!1** | 0, llc!1 / opt!1 | 0, llc!1 / opt!1 |
| `ctl_i2_awaited_method_call` — the same read, awaited | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_i3_unawaited_free_function` | 1, `TYPE-043` | 1 | 1 |

## Deduplication

DEF-97 is a different shape: a generic struct's type defined after its first use,
refused by `llc` as "unsized". No known entry concerns async method calls. The shape
is present at the baseline.

## Measured, and inferred

- **Measured:** the verdicts, and the undefined symbol by name, in `llc`'s message.
- **Inferred:** that the method's coroutine is emitted under another symbol and the
  un-awaited path names the plain one. What the other symbol is was not looked up.
