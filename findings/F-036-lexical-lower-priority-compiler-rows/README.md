# F-036 — LEXICAL_REFERENCE: two places where the compiler departs from the reference safely: four keywords that still name a function, and a literal's trailing underscore (lower priority)

Neither is a wrong answer at run time or a memory fault. The rows, with each claim's program
and its verdicts at HUNT2 `9126350`, the baseline `c3bdae2` and the newest `main` `93bcb66`,
are in [`ROWS.md`](ROWS.md).

**a. Four keywords are accepted as a function's name, and the function can never be called**
(`lx0054`, `lx0114`, `lx0121`)
- LEXICAL:54, :114 and :121 list `acquire`, `any`, `trit` and `nit` as keywords.
- Each line's script compiles a local and a module-level function named after each of its
  words. Every local is refused. But `func:acquire = int32() never fails { pass 7i32; };`
  is accepted, and so are `func:any`, `func:trit` and `func:nit`.
- A call is PARSE-002, "expected an expression": `int32:v = raw acquire();` with the
  function declared, at HUNT2 and at `93bcb66`, for each of the four words. This was
  measured by hand; the program is the script's `func.t` with the call added.
- So each declaration names a function no program can call.
- This is DEF-103's shape (KNOWN_DEFECTS.md: "a keyword accepted as a declared function or
  type name, and then uncallable", fixed at 1.6.0 step 3g).
  - The registry's DEF-103 entry says the fix "refuses a keyword with PARSE-001" at the
    function, trait-method and record sites. It adds that "the four keywords the lexer
    interns as a name after a `.` (`acquire`, `any`, `trit`, `nit`) stay legal METHOD
    names (the prelude's `Mutex.acquire`)".
  - At HUNT2 and `93bcb66` the exemption also covers a module-level function, which is
    reached by its bare name and so can never be called.
  - At the baseline, which predates the fix, many more words of these lines are accepted
    as a function's name (`relaxed`, `release`, `dyn`, `Result`, `tryte`, …). The
    residue is these four.
- F-029 (O-N35) is the same shape at another site: `buffer` as a `wild` pointer binding's
  name.

**b. A decimal literal may end in an underscore** (`lx0296b`)
- `DecimalLiteral ::= [0-9] ([0-9_]* [0-9])?` (LEXICAL:296) ends a literal with a digit.
- `int32:x = 10_i32;` is accepted at all three compilers, and runs (0 / 0).
- *Reasoned:* the underscore is ignored (LEXICAL:284), so the value is not wrong; the
  program is one the grammar does not admit. This is F-027 a's kind: accepted, though
  the reference refuses it.

## Deduplication

- Row a is DEF-103's shape surviving its fix for four words. DEF-103 is recorded FIXED,
  and these four are not mentioned as a residue in KNOWN_DEFECTS.md or in the registry
  at `93bcb66`.
- Row b is in neither.
- Neither row is among F-027's (DEF-153), F-029 … F-034.

## Measured, and inferred

- **Measured:** each row's result at three compilers, and row a's calls at HUNT2 and
  `93bcb66`.
- **Reasoned, not measured:** that the method exemption was meant to be the only one. The
  registry's sentence names methods.
