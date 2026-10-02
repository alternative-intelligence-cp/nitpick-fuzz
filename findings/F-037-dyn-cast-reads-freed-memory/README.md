# F-037 — a trait object built by `x => dyn Trait` reads freed memory (use after free)

**The shape.** AST_REFERENCE:453 says "a `=>` whose target is a `dyn` type is this node"
(`DynCastExpr`): the cast builds a trait object, a fat pointer to the value and its
vtable. The cast compiles, and the trait object it builds points at freed storage:
```
trait:Speaks = { func:say = int32(Self:self); };
struct:Pod = { int32:v; int32:w; };
impl:Pod:Speaks = { func:say = int32(Pod:self) { pass self.v; }; };
...
Pod:l = Pod{ v: 7i32, w: 8i32 };
dyn Speaks:d = move(l) => dyn Speaks;   // accepted
int32:v = d.say() ?| 0i32;              // 0xAAAAAAAA: the allocator's poison for freed bytes
```
The method reads the field through the trait object and gets the runtime's freed-byte
poison, `0xAA` in every byte (the low byte, 170, is the program's exit code). By
CLAUDE.md's definition that is a read of freed memory. The program uses no `wild`, no
`=>!` and no pointer arithmetic.

The same trait object built by the implicit coercion, `dyn Speaks:d = move(l);`, reads
7, as does calling the method on the struct itself.

Found by M11's AST claim `as0453` (its program exited 10, its check of the value). The
shape was then measured by hand in four variants at three compilers (below), and the
programs here were written from them.

## The programs (each exits 0 on the reference's answer, 10 on the poison, 11 on anything else; S39)

| program | what it builds |
|---|---|
| `u1_dyn_cast_moved_pod` | `move(l) => dyn Speaks` over a two-`int32` struct |
| `u2_dyn_cast_pod_no_move` | `l => dyn Speaks`, with no `move` |
| `u3_dyn_cast_owning_struct` | `move(l) => dyn Speaks` over a struct with a `string` field |
| `ctl_u4_dyn_implicit` | the control: `dyn Speaks:d = move(l);`, no cast |
| `ctl_u5_direct_call` | the control: `l.say()` on the struct |

## Verdicts (`VERDICTS.txt`, `VERDICTS-93bcb66.txt`)

| program | HUNT2 `9126350` (×2) | baseline `c3bdae2` | newest `main` `93bcb66` |
|---|---|---|---|
| `u1_dyn_cast_moved_pod` | npkc 0, **10 / 10** | 0, 10 / 10 | 0, 10 / 10 |
| `u2_dyn_cast_pod_no_move` | npkc 0, **10 / 10** | 0, 10 / 10 | 0, 10 / 10 |
| `u3_dyn_cast_owning_struct` | npkc 0, **10 / 10** | 0, 10 / 10 | 0, 10 / 10 |
| `ctl_u4_dyn_implicit` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |
| `ctl_u5_direct_call` | 0, 0 / 0 | 0, 0 / 0 | 0, 0 / 0 |

The reference's answer for every `u` program is 7, which is exit 0. Both legs read the
poison, at all three compilers.

## Deduplication

- KNOWN_DEFECTS.md has no `dyn` cast entry.
- The registry at `93bcb66` (`git show 93bcb66:meta/roadmap/OPEN_DECISIONS.md`) names
  neither `DynCastExpr` nor `=> dyn`.
- F-010 is a lent `dyn`'s swap, refused: another shape.
- Not among F-018 … F-036.

## Measured, and inferred

- **Measured:** each program's npkc exit and both legs' exits at three compilers (HUNT2
  twice), and the value 0xAA…AA in the hand runs (`as0453`'s program and the four
  variants exited 170, the low byte, before the programs here were written to exit 10).
- **Reasoned, not measured:** that the cast moves the value into a temporary whose storage
  is released at the statement's end while the fat pointer keeps its address. The implicit
  coercion does not.
