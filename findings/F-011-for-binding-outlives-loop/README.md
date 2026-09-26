# F-011 — a `for` binding outlives its loop in the emitter: a later use of an outer binding of the same name reads the loop's slot, and reads past it

**The shape.** An outer local, then a `for` whose typed binding has the same
name:

```
int64:i = raw v64(100i64);
for (int64:i in 0i64...3i64) { s = s + i; }
// here `i` should be the outer binding again: 100
```

The program compiles at both compilers. The checker ends the loop binding's
scope at the loop and types the later `i` as the outer binding. The emitter
does not: the later `i` is read from the **loop's** slot. What follows
depends on the two bindings' types.
- **The same type:** a silent wrong value. The outer `i` reads 3, the loop's
  final count.
- **An outer `int32[4]` and a loop `int32`:** `v[3]` indexes the loop's 4-byte
  slot as the 16-byte array. It **reads past the slot**, and **-O0 and -O2
  disagree** (11 / 10).
- **An outer `string` and a loop `int64`:** npkc exits 0 and emits IR that
  `llc` and `opt` reject.

No `wild`, no `=>!`, no pointer arithmetic.

**Found by** the M10 checklist item `h02_for_binding_shadow` (exit 10 at both
compilers). Probes then crossed the two bindings' types.

## Verdicts

Measured on 2026-09-26 on the cloud VM by PLAN.md's recipe through
`gen/run_findings.py`: at HUNT2 twice and at the baseline once
(`VERDICTS.txt`; the HUNT2 runs agree). Each cell gives npkc's rc / the -O0
exit / the -O2 exit. Every program exits 0 on the reference's answer.

| program | what it does | HUNT2 `9126350`, runs 1 and 2 | baseline `c3bdae2` |
|---|---|---|---|
| `leak_same_type.npk` | `int64:i = 100`; `for (int64:i in 0...3)`; read `i` | 0 / **10** / **10**: `i` read 3 | the same |
| `leak_array_iteration.npk` | `int32:v = 100`; `for (int32:v in [5, 6, 7])`; read `v` | 0 / **10** / **10**: `v` read 7 | the same |
| `leak_array_read_past_slot.npk` | `int32[4]:v = [11, 22, 33, 44]`; `for (int32:v in src)`; read `v[3]` | 0 / **11** / **10**: neither 44 nor 7 at -O0, 7 at -O2 | the same |
| `leak_string_invalid_ir.npk` | `string:i = …`; `for (int64:i in 0...3)`; `string_byte_length(i)` | 0 / **llc!1** / **opt!1** | the same |

At the compiler's newest `main`, `9f6f370` (S37), every program gives the same
verdict (`VERDICTS-9f6f370.txt`).

`llc`'s message for `leak_string_invalid_ir`:
`error: extractvalue operand must be aggregate type` at
`%t31 = extractvalue i64 %t30, 1`. The loop's `i64` is read where the
`string`'s header is expected.

## The controls

| control | what differs | expected | HUNT2, runs 1 and 2 | baseline |
|---|---|---|---|---|
| `ctl_block_shadow.npk` | the inner `int64:i` is declared in a plain `{ }` block, not by a `for` | 0 (the block's binding ends with the block) | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_other_name.npk` | the loop binding is `k` | 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `ctl_no_outer.npk` | no outer `i`; `i` used after the loop | refused: the loop binding is out of scope | 1, `RESOLVE-002` | 1, `RESOLVE-002` |

So a block's shadowing binding ends with its block, and so does the checker's
view of a `for` binding. Only the emitter keeps the `for` binding past its
loop.

## What the emitted IR shows

`leak_array_read_past_slot`, HUNT2:
```
%t1  = alloca [4 x i32]        ; the outer `v`
%t13 = alloca i32              ; the loop's `v`
...
%t27 = getelementptr [4 x i32], ptr %t13, i64 0, i64 %t25   ; `v[3]` after the loop
```
The element read is typed as the outer array, the checker's type, but its
base is the loop's `i32` slot. The bounds check passes, because it compares
the index with the array's 4. So index 3 reads 12 bytes past a 4-byte object.
In the same-type program the later `i` is `load i64, ptr` the loop's slot,
and the outer slot is never written.

A probe (not kept as a program) also wrote through the leaked name. After the
loop, `v[k] = 999` for k = 1, 2, 3 stores 4–12 bytes past the loop's slot. The
three `int64` locals and the `int32[3]` it watched were intact, on both legs,
at both compilers. The out-of-bounds WRITE is in the IR, but what it overwrites
depends on the frame's layout, and this probe did not see it corrupt a live
value.

## Deduplication

- Not in `KNOWN_DEFECTS.md`.
- **F-001** is a write *through* a `for` binding to the array's element (DEF-102's
  face, refused `TYPE-085` at HUNT2). This finding is the binding's *name*
  outliving the loop, with no write through it.
- **DEF-97** also had npkc exit 0 and `llc` refuse, but for a generic instance's
  type definition emitted late. It is a different mechanism.
- Present at the baseline, so **an old defect, not a regression**. Present at
  `9f6f370`.

## The reference

- CONTROL_REFERENCE §4.1 (HUNT2 line 306): "Blocks introduce a lexical scope:
  variables declared inside are invisible outside."
- CONTROL_REFERENCE §2.3 on the binding (line 180): "The typed binding is
  required because the language forbids implicit type inference outright."

Whether a local may shadow an outer one by default is not stated.
SAFETY_ARCHITECTURE lists `shadow` among the optional `--extra-picky` rules,
which implies it may; the checker admits it. Either reading makes the measured
result wrong: an accepted program's outer binding must read its own value.

## Measured, and inferred

- *Measured:* the verdicts above, and the IR lines quoted.
- *Read, not measured* (`src/backend/ir/ir_stmt.npk` at HUNT2):
  - `emit_for` binds the loop variable through `for_bind_slot` → `fnem_local`
    (line 1402) in the enclosing scope, and opens no scope of its own for it;
  - the comment on `for_bind_slot` says the coroutine path is "bound through
    the same scope stack, so shadowing behaves". The sync path is not;
  - so the emitter's name→slot map keeps the loop's entry until the
    enclosing block ends.

  This fits all seven verdicts. The coroutine path was not measured.
