"""M11 claims: CONCURRENCY_REFERENCE.md (lines 1-648) and IO_REFERENCE.md (lines 1-288) at HUNT2.

Every expectation below is written from the reference's TEXT. Spellings around a
claim are the ones the compiler's own tests/backend/programs/ use at HUNT2
(`thread async func ... joins D`, `channel()`, `mutex()`, `raw duration_ms(..)`,
the pipe2 + own_fd stream construction of streams_pipe.npk); the construct a
claim is about is spelled as the reference spells it.

Exit codes: 10-59 name the check that saw something other than the reference's
answer; 20-29 in the I/O programs are set-up checks (a write that came up short);
E9 (failsafe 89) is a set-up failure (pipe2, getpid, path_parse of a fixed path).

Reviewed by session 7 before any of its programs ran (PROGRESS.md S51): the check
errors fixed (ids renamed to their lines, quotes moved to the lines that hold them),
and every claim's text and expectation read against its line; the full text around
each claim is re-read at triage for every claim whose program disagrees.
"""
from m11lib import *

covers("CONCURRENCY", 1)
covers("IO", 1)

C = "CONCURRENCY"
I = "IO"


def amain(body, decls=""):
    """A program: top-level declarations, then an `async main` around `body`."""
    return (decls.strip() + "\n\n" if decls.strip() else "") + \
        "async func:main = int32(cstring[]:_~argv) {\n" + body.rstrip() + "\n};\n"


def errs(*ns):
    return "\n".join("error:E%d;" % n for n in ns)


J2 = "fixed Duration:J2 = Duration{ ns: 2000000000i64 };"
J100 = "fixed Duration:J100 = Duration{ ns: 100000000i64 };"


def pipe(k=""):
    """Body lines: a non-blocking pipe (pipe2, O_NONBLOCK), ends rfd<k> / wfd<k> (int32)."""
    return r"""    wild int8->:fdsK = alloc(8i64);
    discard(sys(293i64, fdsK, 2048i64) ?! E9);
    wild int32->:fdiK = fdsK =>! wild int32->;
    int32:rfdK = fdiK[0i64];
    int32:wfdK = fdiK[1i64];
    dalloc(fdsK);
""".replace("K", k)


BUF8 = "    uint8[8]:buf = [0u8, 0u8, 0u8, 0u8, 0u8, 0u8, 0u8, 0u8];\n"

SCRUB = r"""func:scrub = NIL(Path:p) never fails {
    Result<cstring>:c = to_cstring(p.text);
    if (c.is_error) { pass NIL; }
    discard(sys(263i64, (0i64 - 100i64), c.value.ptr, 0i64) ?| 0i64);
    pass NIL;
};"""


def tmpfile(cid, content, n):
    """Body lines (in an async main): /tmp/npk_m11_<cid>.<pid>.tmp holding `content`
    (a Nitpick string-literal body of n bytes), as Path `p`."""
    return r"""    string:me = int_to_string(sys(39i64) ?! E9);
    Path:p = path_parse(string_concat("/tmp/npk_m11_CID.", string_concat(me, ".tmp"))) ?! E9;
    {
        ByteWriter:fw = byte_writer_create(p, raw duration_ms(500i64)) ?! E9;
        int64:fk = await fw.write(string_bytes("CONTENT"), raw duration_ms(500i64)) ?! E9;
        if (fk != LENi64) { exit 20i32; }
    }
""".replace("CID", cid).replace("CONTENT", content).replace("LEN", str(n))


# ============================================================ CONCURRENCY_REFERENCE.md

# ---- §1 Two paradigms (table at 18)
claim("cc0020", C, 20, "native `async` / `await`, coroutines", "row",
      "Asynchronous execution is native `async`/`await`: an async function that suspends "
      "(sleeps) and resumes is awaited from `async main` and yields its value.",
      expect="run:0",
      src=amain(r"""    int32:r = await twice(raw v32(21i32)) ?| 0i32;
    if (r != 42i32) { exit 10i32; }
    exit 0i32;""", r"""async func:twice = int32(int32:v) {
    await sleep(raw duration_ms(1i64)) ?| NIL;
    pass v * 2i32;
};"""),
      wrong="refused, or 10 (the awaited value is not the callee's result)")

claim("cc0021", C, 21, "standard library only, no language keywords", "row",
      "System threading uses no language keywords, so `thread` is an ordinary identifier.",
      expect="run:0",
      src=main_(r"""    int32:thread = raw v32(1i32);
    exit thread - 1i32;"""),
      wrong="refused: `thread` is a keyword of the threading mechanism",
      note="LEXICAL_REFERENCE §4 lists `thread` and `joins` as AsyncKeyword and the "
           "compiler's threads are `thread async func ... joins D`: this row and that list "
           "cannot both hold.")

# ---- the connecting rule (26-36)
claim("cc0027b", C, 27, "waiting is always a task-level event", "rule",
      "Waiting is a task-level event: main waiting in `recv` does not stop a sibling task "
      "on the same thread from running and sending the value main waits for.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E2;
    drop late(ch);
    Result<int32>:r = await ch.recv(raw duration_ms(2000i64));
    if (r.is_error) { exit 10i32; }
    if (r.value != 7i32) { exit 11i32; }
    exit 0i32;""", errs(1, 2) + r"""
async func:late = NIL(Channel<int32, 3i32, 1i64>:c) {
    await sleep(raw duration_ms(20i64)) ?| NIL;
    await c.send(7i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};"""),
      wrong="10: the recv parked the thread, the sender never ran, the wait timed out")

claim("cc0027", C, 27, "Every thread runs an executor", "rule",
      "Every thread runs an executor: a thread's body spawns a task, awaits the channel it "
      "fills, and reports the value plus one.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 4i32, 1i64>:out = channel() ?! E5;
    drop tbody(out);
    int32:r = await out.recv(raw duration_ms(2000i64)) ?! E6;
    if (r != 8i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3, 4, 5, 6) + "\n" + J2 + r"""
async func:child = NIL(Channel<int32, 3i32, 1i64>:c) {
    await c.send(7i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};
thread async func:tbody = NIL(Channel<int32, 4i32, 1i64>:out) joins J2 {
    Channel<int32, 3i32, 1i64>:inner = channel() ?! E2;
    drop child(inner);
    int32:v = await inner.recv(raw duration_ms(1000i64)) ?! E3;
    await out.send(v + 1i32, raw duration_ms(500i64)) ?! E4;
    pass NIL;
};"""),
      wrong="refused, 10, or a failsafe arm 82-86: a thread cannot run tasks of its own")

claim("cc0035", C, 35, "blocking-versus-async split in the API", "rule",
      "There is no blocking form of a channel operation: `ch.recv(d)` without `await` is "
      "refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = ch.recv(raw duration_ms(10i64));
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="accepted: a blocking recv exists beside the awaited one")

# ---- §2.1 Declaring and awaiting
claim("cc0042", C, 42, "```nitpick", "example",
      "The declaring-and-awaiting example compiles as written and exits 0.",
      expect="run:0",
      src=r"""async func:fetch_data = string(string:url) {
    pass "Data payload";
};

async func:main = int32() {
    string:payload = relay await fetch_data("https://example.com");
    exit 0i32;
};
""",
      wrong="refused (e.g. `main` with no parameter list, or `relay` in `main`)",
      note="Literal. MEMORY/TYPE state main's signature is fixed at `(cstring[]:_~argv)` "
           "(TYPE-083 per the compiler's main_sig_none.npk), which this example omits.")

claim("cc0053", C, 53, "functions return `Result<T>` like every other function, so the result", "rule",
      "An awaited async call is a `Result<T>` that must be unwrapped: binding it straight to "
      "`int32` is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = await f(raw v32(41i32));
    if (x != 42i32) { exit 10i32; }
    exit 0i32;""", r"""async func:f = int32(int32:v) {
    pass v + 1i32;
};"""),
      wrong="accepted: await yields the bare T",
      note="The same program is cc0142's, which line 142 says compiles: the two lines "
           "contradict each other and exactly one of cc0053/cc0142 can agree.")

claim("cc0053b", C, 53, "`async` functions return `Result<T>`", "rule",
      "An awaited async call binds as `Result<int32>` and carries the callee's value.",
      expect="run:0",
      src=amain(r"""    Result<int32>:r = await f(raw v32(41i32));
    if (r.is_error) { exit 10i32; }
    if (r.value != 42i32) { exit 11i32; }
    exit 0i32;""", r"""async func:f = int32(int32:v) {
    pass v + 1i32;
};"""),
      wrong="refused, 10 or 11")

claim("cc0055", C, 55, "callee can never be `never fails`", "rule",
      "An `async` function can never be `never fails`: declaring one is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = await f() ?| 0i32;
    exit x - 1i32;""", r"""async func:f = int32() never fails {
    pass 1i32;
};"""),
      wrong="accepted")

claim("cc0056", C, 56, "so `raw await f(…)` is unlicensed by", "rule",
      "`raw await f()` is unlicensed: it is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = raw await f();
    exit x - 1i32;""", r"""async func:f = int32() {
    pass 1i32;
};"""),
      wrong="accepted")

claim("cc0059", C, 59, "```nitpick", "example",
      "The three honest spellings (relay, `?| fallback`, `?! 9tbb32`) compile, and each "
      "yields the callee's value when it succeeds.",
      expect="run:0",
      src=amain(r"""    int32:r = await three("https://example.com") ?| 13i32;
    exit r;""", r"""async func:fetch_data = string(string:url) {
    pass "Data payload";
};

async func:three = int32(string:url) {
    string:fallback = "fallback";
    string:payload = relay await fetch_data(url);      // propagate
    string:p2 = await fetch_data(url) ?| fallback;     // default
    string:p3 = await fetch_data(url) ?! 9tbb32;       // trap
    if (!(string_equals(payload, "Data payload"))) { pass 10i32; }
    if (!(string_equals(p2, "Data payload"))) { pass 11i32; }
    if (!(string_equals(p3, "Data payload"))) { pass 12i32; }
    pass 0i32;
};"""),
      wrong="refused (a stale spelling among the three), or 10-13",
      note="Literal lines inside a function that declares url and fallback. OP_REFERENCE "
           "`?!` says it takes exactly one Error constant (D-179), not a tbb32 literal.")

claim("cc0060", C, 60, "relay await fetch_data(url);      // propagate", "rule",
      "`relay await` propagates the callee's error verbatim as the caller's own.",
      expect="run:0",
      src=amain(r"""    Result<int32>:r = await mid(raw v32(1i32));
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    exit 0i32;""", errs(1) + r"""
async func:leaf = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};
async func:mid = int32(int32:v) {
    int32:a = relay await leaf(v);
    pass a + 100i32;
};"""),
      wrong="10 (the error was lost) or 11 (another error arrived)")

claim("cc0061", C, 61, "?| fallback;     // default", "rule",
      "`await f() ?| d` yields d when the call fails and the value when it succeeds.",
      expect="run:0",
      src=amain(r"""    int32:x = await leaf(raw v32(1i32)) ?| 7i32;
    if (x != 7i32) { exit 10i32; }
    int32:y = await leaf(raw v32(0i32)) ?| 7i32;
    if (y != 0i32) { exit 11i32; }
    exit 0i32;""", errs(1) + r"""
async func:leaf = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};"""),
      wrong="10 or 11")

claim("cc0062", C, 62, "?! 9tbb32;       // trap", "rule",
      "`await f() ?! 9tbb32` on a failing call traps to failsafe with code 9, which no "
      "named arm matches, so the catch-all arm answers.",
      expect="run:99",
      src=amain(r"""    int32:x = await leaf(raw v32(1i32)) ?! 9tbb32;
    exit x;""", errs(1) + r"""
async func:leaf = int32(int32:v) {
    if (v > 0i32) { fail E1; }
    pass v;
};"""),
      wrong="refused (a tbb32 argument), 81 (E1 itself was raised), or 1 (no trap)",
      note="Reasoned: code 9 names no prelude identity and no declared error, so the "
           "appended failsafe's `(*)` arm (99) is the only one that can take it.")

claim("cc0065", C, 65, "is valid only inside an `async func`", "rule",
      "`await` in a synchronous function is refused.",
      expect="refuse",
      src=main_(r"""    int32:r = sync_user(raw v32(1i32)) ?| 0i32;
    exit r - 2i32;""", r"""async func:leaf = int32(int32:v) {
    pass v + 1i32;
};
func:sync_user = int32(int32:v) {
    int32:a = relay await leaf(v);
    pass a;
};"""),
      wrong="accepted")

claim("cc0066", C, 66, "hard compile error, `NITPICK-040`", "rule",
      "`await` in a synchronous function is refused with the code NITPICK-040.",
      expect="refuse:NITPICK-040",
      src=main_(r"""    int32:r = sync_user(raw v32(1i32)) ?| 0i32;
    exit r - 2i32;""", r"""async func:leaf = int32(int32:v) {
    pass v + 1i32;
};
func:sync_user = int32(int32:v) {
    int32:a = relay await leaf(v);
    pass a;
};"""),
      wrong="accepted, or refused under another code")

# ---- §2.2 Spawning
claim("cc0070", C, 70, "and discarding the result spawns", "rule",
      "Calling an async function without `await` and discarding the result spawns it: the "
      "spawned task runs and delivers its value through a channel.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E2;
    drop work(ch);
    int32:v = await ch.recv(raw duration_ms(2000i64)) ?! E3;
    if (v != 7i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
async func:work = NIL(Channel<int32, 3i32, 1i64>:c) {
    await c.send(7i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};"""),
      wrong="refused, 83 (the task never ran: the recv timed out) or 10")

claim("cc0073", C, 73, "```nitpick", "example",
      "`drop work();` spawns an async function whose VALUE is discarded: a value-returning "
      "async callee is accepted in the spawn form.",
      expect="run:0",
      src=amain(r"""    drop work();        // runs concurrently; VALUE discarded, ERROR joined (D-163)
    exit 0i32;""", r"""async func:work = int32() {
    pass 5i32;
};"""),
      wrong="refused: only a NIL-returning callee may be spawned",
      note="`work` returns int32 because the example's comment says its VALUE is discarded.")

claim("cc0079", C, 79, "the enclosing scope's D-062 join", "rule",
      "A spawned task's error reaches the join and becomes the enclosing async function's own "
      "error.",
      expect="run:0",
      src=amain(r"""    Result<int32>:r = await parent();
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    exit 0i32;""", errs(1) + r"""
async func:work = NIL() {
    fail E1;
};
async func:parent = int32() {
    drop work();
    pass 5i32;
};"""),
      wrong="10: the spawned task's error was discarded")

claim("cc0080", C, 80, "after every child has finished", "rule",
      "The join relays the first child error verbatim, and only after every child has "
      "finished: a slower sibling's value is already in the channel when the parent returns.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E4;
    Result<int32>:r = await parent(ch);
    if (!r.is_error) { exit 10i32; }
    if (r.err != E1) { exit 11i32; }
    Result<int32>:v = await ch.recv(raw duration_ms(0i64));
    if (v.is_error) { exit 12i32; }
    if (v.value != 7i32) { exit 13i32; }
    exit 0i32;""", errs(1, 2, 3, 4) + r"""
async func:fast_fail = NIL() {
    fail E1;
};
async func:slow = NIL(Channel<int32, 3i32, 1i64>:c) {
    await sleep(raw duration_ms(50i64)) ?| NIL;
    await c.send(7i32, raw duration_ms(500i64)) ?! E3;
    fail E2;
};
async func:parent = int32(Channel<int32, 3i32, 1i64>:c) {
    drop fast_fail();
    drop slow(c);
    pass 5i32;
};"""),
      wrong="11 (a later error won), 12 (the parent returned before `slow` finished)",
      note="E1 is first both in spawn order and in time; the text does not say which order "
           "'first' means, so the program keeps the two orders equal.")

claim("cc0081", C, 81, "a task wound up by the join's deadline reports its wind-up", "rule",
      "A task wound up by the join's deadline reports its wind-up code as the enclosing async "
      "function's error, the way a child error does.",
      expect="run:0",
      src=amain(r"""    Result<int32>:r = await parent();
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", J100 + r"""
thread async func:sleeper = NIL(int32:_~v) joins J100 {
    await sleep(raw duration_ms(20i64)) ?| NIL;
    relay await sleep(raw duration_ms(30000i64));
    pass NIL;
};
async func:parent = int32() {
    drop sleeper(1i32);
    pass 5i32;
};"""),
      wrong="10 (the parent succeeded), 101 (the join trapped instead), T (an unbounded join)",
      note="Lines 100-101, 427 and 624 say the join's expiry TRAPS; lines 81-82 say the "
           "wound-up task's code is relayed like a child error. For a non-main parent the "
           "two readings differ; this claim is 81-82's.")

claim("cc0082", C, 82, "A spawned task's error is observable or the program does not", "rule",
      "Spawning where no error can be observed does not compile: `drop work()` in a "
      "synchronous function is refused.",
      expect="refuse",
      src=main_(r"""    int32:r = sync_spawner() ?| 0i32;
    exit r - 1i32;""", r"""async func:work = NIL() {
    pass NIL;
};
func:sync_spawner = int32() {
    drop work();
    pass 1i32;
};"""),
      wrong="accepted")

claim("cc0092", C, 92, "does not return until it has", "rule",
      "A spawned task cannot outlive its scope: the enclosing async function does not return "
      "until the task has finished, so its value is in the channel when the function returns.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E2;
    int32:p = await parent(ch) ?! E3;
    if (p != 5i32) { exit 10i32; }
    Result<int32>:v = await ch.recv(raw duration_ms(0i64));
    if (v.is_error) { exit 11i32; }
    if (v.value != 7i32) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
async func:slow = NIL(Channel<int32, 3i32, 1i64>:c) {
    await sleep(raw duration_ms(50i64)) ?| NIL;
    await c.send(7i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};
async func:parent = int32(Channel<int32, 3i32, 1i64>:c) {
    drop slow(c);
    pass 5i32;
};"""),
      wrong="11: the parent returned while its task was still running")

claim("cc0091", C, 91, "The task runs", "rule",
      "The spawned task runs concurrently with its spawner: it waits for a value the spawner "
      "sends after spawning it, and answers.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:a = channel() ?! E3;
    Channel<int32, 4i32, 1i64>:b = channel() ?! E3;
    drop echo(a, b);
    await a.send(3i32, raw duration_ms(500i64)) ?! E4;
    int32:v = await b.recv(raw duration_ms(2000i64)) ?! E5;
    if (v != 6i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3, 4, 5) + r"""
async func:echo = NIL(Channel<int32, 3i32, 1i64>:inp, Channel<int32, 4i32, 1i64>:outp) {
    int32:x = await inp.recv(raw duration_ms(1000i64)) ?! E1;
    await outp.send(x * 2i32, raw duration_ms(500i64)) ?! E2;
    pass NIL;
};"""),
      wrong="81 or 85: the spawn ran the task to completion before the spawner continued")

claim("cc0097", C, 97, "taking a normal", "rule",
      "A task the scope-exit join winds up observes the request at its next await and takes a "
      "normal error exit, so its `defer` runs (here the defer divides by zero).",
      expect="trap:DivByZero",
      src=amain(r"""    drop sleeper(raw v32(0i32));
    exit 0i32;""", J100 + r"""
thread async func:sleeper = NIL(int32:zero) joins J100 {
    defer { discard(10i32 / zero); }
    await sleep(raw duration_ms(20i64)) ?| NIL;
    relay await sleep(raw duration_ms(30000i64));
    pass NIL;
};"""),
      wrong="101 (the join's deadline trapped with no wind-up, the defer never ran) or T "
            "(the join waited out the 30 s sleep)")

claim("cc0098", C, 98, "The deadline is a property of the executor, fixed", "rule",
      "The join deadline is a property of the executor, fixed where the executor is created, "
      "not repeated at every spawn.",
      untestable="[vague] the section gives no construct that sets an executor's deadline; "
                 "`joins` appears only in LEXICAL_REFERENCE, never in this reference")

claim("cc0100", C, 100, "There is no unbounded join, and expiry **traps to", "rule",
      "There is no unbounded join: a thread that outlives its join deadline traps to "
      "failsafe (DeadlineExceeded) instead of being detached or waited for.",
      expect="trap:DeadlineExceeded",
      src=amain(r"""    drop sleeper(1i32);
    exit 0i32;""", J100 + r"""
thread async func:sleeper = NIL(int32:_~v) joins J100 {
    await sleep(raw duration_ms(20i64)) ?| NIL;
    relay await sleep(raw duration_ms(30000i64));
    pass NIL;
};"""),
      wrong="0 at once (detached), T (joined without bound)",
      note="The arm is DeadlineExceeded by line 426-427 ('the JOIN's trap code when a task "
           "outlives its bound').")

claim("cc0108", C, 108, "There is no cancellation operation.", "rule",
      "There is no operation that cancels a task.",
      untestable="[unobservable] no task can be named (D-058), so no program can even form "
                 "a call to a cancel operation; cc0143 tests that the spawn's result cannot "
                 "be held")

# ---- §2.3 pinned
claim("cc0115", C, 115, "A task resumes on the thread it suspended on.", "rule",
      "A task resumes on the thread it suspended on (no migration, no work-stealing): its "
      "gettid is the same after every await, while two other threads are busy.",
      expect="run:0",
      src=amain(r"""    drop busy(20i32);
    drop busy(20i32);
    int64:m0 = sys(186i64) ?! E3;
    int32:i = 0i32;
    while (i < 20i32) decreases 20i32 - i {
        await sleep(raw duration_ms(2i64)) ?| NIL;
        int64:t = sys(186i64) ?! E3;
        if (t != m0) { exit 10i32; }
        i = i + 1i32;
    }
    exit 0i32;""", errs(1, 2, 3) + "\n" + J2 + r"""
thread async func:busy = NIL(int32:n) joins J2 {
    int64:t0 = sys(186i64) ?! E1;
    int32:i = 0i32;
    while (i < n) decreases n - i {
        await sleep(raw duration_ms(2i64)) ?| NIL;
        int64:t = sys(186i64) ?! E1;
        if (t != t0) { fail E2; }
        i = i + 1i32;
    }
    pass NIL;
};"""),
      wrong="10 (main's task moved) or 82 (a thread's task moved)")

# ---- §2.4 Future and frames
claim("cc0130", C, 130, "lowers to `@llvm.coro` state machines", "rule",
      "`async` lowers to `@llvm.coro` state machines: the emitted IR uses llvm.coro intrinsics.",
      expect=r"ir:@llvm\.coro\.",
      src=amain(r"""    int32:r = await leaf(raw v32(41i32)) ?| 0i32;
    exit r - 42i32;""", r"""async func:leaf = int32(int32:v) {
    await sleep(raw duration_ms(1i64)) ?| NIL;
    pass v + 1i32;
};"""),
      wrong="no llvm.coro call: a hand-built state machine")

claim("cc0132", C, 132, "```llvm", "example",
      "`Future<T>` is the handle `%Future = type { ptr, ptr }` (coroutine handle, result slot) "
      "in the emitted IR of an async program.",
      expect=r"ir:%Future = type \{ ptr, ptr \}",
      src=amain(r"""    int32:r = await leaf(raw v32(41i32)) ?| 0i32;
    exit r - 42i32;""", r"""async func:leaf = int32(int32:v) {
    await sleep(raw duration_ms(1i64)) ?| NIL;
    pass v + 1i32;
};"""),
      wrong="no %Future type: the frame itself is the handle")

claim("cc0136", C, 136, "Each thread's executor owns an `arena<T>` from which task frames are", "rule",
      "Each thread's executor allocates task frames from its own single-threaded arena, "
      "released on task completion.",
      untestable="[internal] where a frame's bytes come from is the runtime's business; no "
                 "program-visible operation distinguishes an executor arena from the heap")

claim("cc0141", C, 141, "is an internal lowering artifact, not surface syntax", "rule",
      "`Future<T>` is not surface syntax: a parameter of type `Future<int32>` is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""func:takes = int32(Future<int32>:_~h) never fails {
    pass 0i32;
};"""),
      wrong="accepted: the type can be named",
      note="LEXICAL_REFERENCE §4 lists `Future` among the BuiltinType keywords.")

claim("cc0142", C, 142, "yields `T` directly", "rule",
      "`await f()` yields `T` directly: `int32:x = await f(..)` compiles and x is the value.",
      expect="run:0",
      src=amain(r"""    int32:x = await f(raw v32(41i32));
    if (x != 42i32) { exit 10i32; }
    exit 0i32;""", r"""async func:f = int32(int32:v) {
    pass v + 1i32;
};"""),
      wrong="refused: await yields Result<T>, which must be unwrapped",
      note="Contradicts line 53 (cc0053, same program, expected refused).")

claim("cc0143", C, 143, "a user can neither name it nor hold it", "rule",
      "The result of an un-awaited async call cannot be held: binding `work()` is refused.",
      expect="refuse",
      src=amain(r"""    Result<int32>:h = work();
    if (h.is_error) { exit 10i32; }
    exit 0i32;""", r"""async func:work = int32() {
    pass 1i32;
};"""),
      wrong="accepted: a future can be held")

claim("cc0146", C, 146, "fan-out and collect", "rule",
      "Fan-out and collect goes through a channel: three spawned tasks send their squares on "
      "one channel and main collects 1+4+9.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 4i64>:c = channel() ?! E2;
    drop part(1i32, c);
    drop part(2i32, c);
    drop part(3i32, c);
    int32:sum = 0i32;
    int32:n = 0i32;
    while (n < 3i32) decreases 3i32 - n {
        int32:v = await c.recv(raw duration_ms(2000i64)) ?! E3;
        sum = sum + v;
        n = n + 1i32;
    }
    if (sum != 14i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
async func:part = NIL(int32:v, Channel<int32, 3i32, 4i64>:c) {
    await c.send(v * v, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};"""),
      wrong="10, or 83 (a value never arrived)")

# ---- §3 System threading
claim("cc0151", C, 151, "no `spawn` or `go` keyword", "rule",
      "There is no `spawn` keyword: `spawn` is an ordinary identifier.",
      expect="run:0",
      src=main_(r"""    int32:spawn = raw v32(1i32);
    exit spawn - 1i32;"""),
      wrong="refused: `spawn` is reserved")

claim("cc0151b", C, 151, "no `spawn` or `go` keyword", "rule",
      "There is no `go` keyword: `go` is an ordinary identifier.",
      expect="run:0",
      src=main_(r"""    int32:go = raw v32(1i32);
    exit go - 1i32;"""),
      wrong="refused: `go` is reserved")

claim("cc0151c", C, 151, "no `sync` keyword", "rule",
      "There is no `sync` keyword and the compiler rejects it: a `sync` function modifier is "
      "refused.",
      expect="refuse",
      src=main_(r"""    int32:r = f() ?| 0i32;
    exit r - 1i32;""", r"""sync func:f = int32() {
    pass 1i32;
};"""),
      wrong="accepted",
      note="'rejects the latter outright' could also mean `sync` is refused as an "
           "identifier; the modifier form is refused under either reading.")

claim("cc0153", C, 153, "barriers are standard-library abstractions", "rule",
      "Threads, mutexes, condition variables, rwlocks and barriers are standard-library "
      "abstractions, not language constructs.",
      untestable="[tree] where the primitives are implemented is a fact about the source "
                 "tree; note LEXICAL_REFERENCE §4 lists Mutex, Guard, RwLock, RGuard, "
                 "CondVar, Barrier as BuiltinType keywords and `thread` as a keyword")

claim("cc0167", C, 167, "supplies the primitives.", "rule",
      "libn's syscall layer wraps futex (12 uses), clone (5), gettid, tkill, set_robust_list.",
      untestable="[tree] a count of call sites in the archived prototype's source")

excluded(C, 174, "an inventory of the archived prototype's stdlib files (line counts, C "
                 "dependencies): facts about another source tree, not language behaviour")

claim("cc0187", C, 187, "The three carrying **direct** C shims are already marked deprecated", "rule",
      "The three prototype modules with direct C shims are marked deprecated in their source.",
      untestable="[tree] a statement about the archived prototype's files")

claim("cc0194", C, 194, "Only `mutex`, `rwlock`, and `condvar` are genuinely", "rule",
      "Of the prototype's modules only mutex, rwlock and condvar are free of C dependencies.",
      untestable="[tree] a statement about the archived prototype's imports")

claim("cc0207", C, 207, "records the full read", "rule",
      "meta/CONCURRENCY_STDLIB_AUDIT.md records the full read of the prototype modules.",
      untestable="[tree] a statement about a document in the compiler repository")

claim("cc0220", C, 220, "language type emitting native LLVM atomic IR with no shim", "rule",
      "`atomic<T>` emits native LLVM atomic IR: `fetch_add` appears as an `atomicrmw add`.",
      expect="ir:atomicrmw add ",
      src=main_(r"""    atomic<int32>:c = 0i32;
    int32:p = c.fetch_add(raw v32(5i32));
    if (p != 0i32) { exit 10i32; }
    if (c.load() != 5i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="no atomicrmw: the operation is a call")

claim("cc0220b", C, 220, "with no shim", "rule",
      "`atomic<T>` needs no shim: the program's IR names no `*shim*` symbol.",
      expect=r"ir!:@[\w.$]*shim",
      src=main_(r"""    atomic<int32>:c = 0i32;
    int32:p = c.fetch_add(raw v32(5i32));
    if (p != 0i32) { exit 10i32; }
    if (c.load() != 5i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="a call to a shim symbol (the deprecated atomic.npk's npk_shim_* route)")

# ---- §4.1 Obtaining an atomic
claim("cc0243", C, 243, "```nitpick", "example",
      "The three ways to obtain an atomic compile as written: scope storage, a struct field, "
      "and `atomic_from_ptr<int32>(hdr_ptr)` bound to a local.",
      expect="run:0",
      src=main_(r"""    wild int8->:buf = alloc(8i64);
    wild int32->:hdr_ptr = buf =>! wild int32->;
    atomic<int32>:counter = 0i32;            // storage in the enclosing scope
    atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr);   // alias existing memory
    dalloc(buf);
    exit 0i32;""", r"""struct:Stats = {
    atomic<int64>:hits;                  // or as a struct field
};"""),
      wrong="refused (e.g. the alias cannot be bound, or the call needs a turbofish)",
      note="hdr_ptr is declared as a wild int32 pointer to 8 fresh bytes; the struct moves to "
           "the top level.")

claim("cc0244", C, 244, "atomic<int32>:counter = 0i32;", "rule",
      "An atomic may live in the enclosing scope, initialised from a plain value, and is "
      "usable there.",
      expect="run:0",
      src=main_(r"""    atomic<int32>:counter = 0i32;            // storage in the enclosing scope
    if (counter.load() != 0i32) { exit 10i32; }
    discard(counter.fetch_add(raw v32(2i32)));
    if (counter.load() != 2i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="refused, 10 or 11")

claim("cc0247", C, 247, "atomic<int64>:hits;", "rule",
      "An atomic may be a struct field, and its methods work through the field.",
      expect="run:0",
      src=main_(r"""    Stats:s = Stats{ hits: 0i64 };
    discard(s.hits.fetch_add(raw v64(3i64)));
    if (s.hits.load() != 3i64) { exit 10i32; }
    exit 0i32;""", r"""struct:Stats = {
    atomic<int64>:hits;                  // or as a struct field
};"""),
      wrong="refused or 10")

claim("cc0250", C, 250, "atomic_from_ptr<int32>(hdr_ptr);   // alias existing memory", "rule",
      "`atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr)` aliases existing memory: a store "
      "through lk is what the pointer reads.",
      expect="run:0",
      src=main_(r"""    wild int8->:buf = alloc(8i64);
    wild int32->:hdr_ptr = buf =>! wild int32->;
    <-hdr_ptr = 5i32;
    atomic<int32>:lk = atomic_from_ptr<int32>(hdr_ptr);   // alias existing memory
    lk.store(raw v32(9i32));
    if ((<-hdr_ptr) != 9i32) { exit 10i32; }
    if (lk.load() != 9i32) { exit 11i32; }
    dalloc(buf);
    exit 0i32;"""),
      wrong="refused (the alias may not be bound; the call needs `::<int32>`), or 10 (a copy, "
            "not an alias)")

claim("cc0253", C, 253, "`atomic_new(0i32)` is **removed**", "rule",
      "`atomic_new(0i32)` is removed (there is no allocating constructor): it is refused.",
      expect="refuse",
      src=main_(r"""    atomic<int32>:c = atomic_new(0i32);
    if (c.load() != 0i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")

claim("cc0258", C, 258, "Where an aliased address originates as an integer it must be converted with", "rule",
      "An integer address must be converted with `#wild_ptr<T>` first: passing an int64 "
      "straight to `atomic_from_ptr` is refused.",
      expect="refuse",
      src=main_(r"""    int64:addr = raw v64(4096i64);
    int32:v = atomic_from_ptr::<int32>(addr).load();
    exit v;"""),
      wrong="accepted: an integer is taken as an address")

claim("cc0259b", C, 259, "`#wild_ptr<T>(addr)` in `wild` context", "rule",
      "An integer address converted with `#wild_ptr<T>(addr)` can be aliased as an atomic: a "
      "store through the alias is read back through the pointer (an mmap'd page).",
      expect="run:0",
      src=main_(r"""    int64:map = sys(9i64, 0i64, 4096i64, 3i64, 34i64, (0i64 - 1i64), 0i64) ?! E1;
    wild int32->:cell = #wild_ptr<int32>(map);
    atomic_from_ptr::<int32>(cell).store(raw v32(7i32));
    if ((<-cell) != 7i32) { exit 10i32; }
    discard(sys(11i64, map, 4096i64) ?! E2);
    exit 0i32;""", errs(1, 2)),
      wrong="refused, or 10")

claim("cc0260", C, 260, "not the raw `hdr_ptr + 24i64`", "rule",
      "Offsets go through `#ptr_add`, not raw `ptr + n`: adding an integer to a pointer is "
      "refused.",
      expect="refuse",
      src=main_(r"""    wild int8->:buf = alloc(16i64);
    wild int32->:hdr_ptr = buf =>! wild int32->;
    wild int32->:q = hdr_ptr + 2i64;
    <-q = 1i32;
    dalloc(buf);
    exit 0i32;"""),
      wrong="accepted: raw pointer arithmetic")

claim("cc0260b", C, 260, "`#ptr_add<T>(ptr, offset)`", "rule",
      "`#ptr_add<T>(ptr, offset)` offsets a pointer, and an atomic alias of the result works.",
      expect="run:0",
      src=main_(r"""    wild int8->:buf = alloc(16i64);
    wild int32->:hdr_ptr = buf =>! wild int32->;
    wild int32->:q = #ptr_add<int32>(hdr_ptr, 2i64);
    <-q = 5i32;
    discard(atomic_from_ptr::<int32>(q).fetch_add(raw v32(1i32)));
    if ((<-q) != 6i32) { exit 10i32; }
    dalloc(buf);
    exit 0i32;"""),
      wrong="refused, or 10")

# ---- §4.2 The method set
claim("cc0264", C, 264, "Exactly six, and nothing else:", "rule",
      "The atomic method set is exactly six: a seventh (`fetch_or`) is refused.",
      expect="refuse",
      src=main_(r"""    atomic<int32>:c = 0i32;
    discard(c.fetch_or(raw v32(1i32)));
    exit c.load() - 1i32;"""),
      wrong="accepted")

claim("cc0266", C, 266, "`.load()` · `.store(v)` · `.swap(v)`", "rule",
      "All six methods exist and act on the cell: store 5, fetch_add 3, fetch_sub 1, swap 10, "
      "compare_exchange(10, 20) leave 20.",
      expect="run:0",
      src=main_(r"""    atomic<int32>:c = 0i32;
    c.store(raw v32(5i32));
    discard(c.fetch_add(raw v32(3i32)));
    discard(c.fetch_sub(raw v32(1i32)));
    discard(c.swap(raw v32(10i32)));
    discard(c.compare_exchange(raw v32(10i32), raw v32(20i32)));
    if (c.load() != 20i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused (a method missing) or 10",
      note="Reasoned: the reference lists the six names without defining them; the final "
           "value assumes each name's ordinary meaning.")

claim("cc0268", C, 268, "```nitpick", "example",
      "`int32:prev = counter.fetch_add(1i32);` yields the value before the add.",
      expect="run:0",
      src=main_(r"""    atomic<int32>:counter = 0i32;
    int32:prev = counter.fetch_add(1i32);
    if (prev != 0i32) { exit 10i32; }
    if (counter.load() != 1i32) { exit 11i32; }
    exit 0i32;"""),
      wrong="10 (the new value is returned) or 11",
      note="Reasoned from the binding's name `prev`: the text does not state the result.")

claim("cc0272", C, 272, "Methods dispatch via UFCS", "rule",
      "Atomic methods dispatch via UFCS.",
      untestable="[internal] UFCS is how `c.load()` is resolved; the reference gives no "
                 "free-function spelling for an atomic method a program could call instead")

# ---- §4.3 SeqCst
claim("cc0276", C, 276, "methods enforce SeqCst", "rule",
      "All six atomic methods lower with seq_cst ordering (load, store, xchg, add, sub, "
      "cmpxchg seq_cst seq_cst).",
      expect=r"ir:\A(?=[\s\S]*?load atomic i32[^\n]*seq_cst)(?=[\s\S]*?store atomic i32[^\n]*seq_cst)"
             r"(?=[\s\S]*?atomicrmw xchg[^\n]*seq_cst)(?=[\s\S]*?atomicrmw add[^\n]*seq_cst)"
             r"(?=[\s\S]*?atomicrmw sub[^\n]*seq_cst)(?=[\s\S]*?cmpxchg[^\n]*seq_cst seq_cst)",
      src=main_(r"""    atomic<int32>:c = 0i32;
    c.store(raw v32(5i32));
    discard(c.fetch_add(raw v32(3i32)));
    discard(c.fetch_sub(raw v32(1i32)));
    discard(c.swap(raw v32(10i32)));
    discard(c.compare_exchange(raw v32(10i32), raw v32(20i32)));
    if (c.load() != 20i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="one of the six emitted with a weaker ordering (or not as an atomic instruction)")

claim("cc0277", C, 277, "orderings such as `.load_acquire()` are rejected by the compiler", "rule",
      "A suffixed weaker ordering such as `.load_acquire()` is refused.",
      expect="refuse",
      src=main_(r"""    atomic<int32>:c = 0i32;
    int32:v = c.load_acquire();
    exit v;"""),
      wrong="accepted")

for _suf, _kw in (("", "relaxed"), ("b", "acquire"), ("c", "release")):
    claim("cc0278" + _suf, C, 278, "are reserved keywords but reachable", "rule",
          "`%s` is a reserved keyword: it cannot name a variable." % _kw,
          expect="refuse",
          src=main_(r"""    int32:KW = raw v32(1i32);
    exit KW - 1i32;""".replace("KW", _kw)),
          wrong="accepted: `%s` is an ordinary identifier" % _kw,
          note="`acquire` is also the mutex method `m.acquire(d)` at HUNT2." if _kw == "acquire" else "")

claim("cc0279", C, 279, "only through low-level compiler intrinsics", "rule",
      "The ordering keywords are reachable only through low-level compiler intrinsics.",
      untestable="[vague] no intrinsic is named, so no program can reach one or show it absent")

# ---- §5.1 Borrows cannot cross a concurrency boundary
claim("cc0297", C, 297, "they pass down the call stack and never up", "rule",
      "Borrows pass down the call stack and never up: a function returning a borrow of its "
      "own local is refused.",
      expect="refuse",
      src=main_(r"""    int32->:p = up(raw v32(3i32)) ?! E1;
    exit (<-p) - 3i32;""", errs(1) + r"""
func:up = int32->(int32:v) {
    int32:x = v;
    pass @x;
};"""),
      wrong="accepted: a dangling borrow escapes")

claim("cc0298", C, 298, "a borrow may not cross **a thread spawn**", "rule",
      "A borrow may not cross a thread spawn: passing `@x` of an int32 to a thread is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = raw v32(1i32);
    {
        drop t(@x);
    }
    exit x - 5i32;""", J2 + r"""
thread async func:t = NIL(int32->:p) joins J2 {
    <-p = 5i32;
    pass NIL;
};"""),
      wrong="accepted: two threads share a stack reference")

claim("cc0298b", C, 298, "**an `await` point**", "rule",
      "A borrow may not cross an await point: a borrow held across an `await` and used after "
      "it is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = raw v32(1i32);
    int32->:p = @x;
    await sleep(raw duration_ms(1i64)) ?| NIL;
    <-p = 5i32;
    if (x != 5i32) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted")

claim("cc0298c", C, 298, "or **an `await` point**", "rule",
      "A borrow may not cross an await point: passing `@x` into an awaited async callee that "
      "suspends while holding it is refused.",
      expect="refuse",
      src=amain(r"""    int32:x = raw v32(2i32);
    await bump(@x) ?! E1;
    if (x != 42i32) { exit 10i32; }
    exit 0i32;""", errs(1) + r"""
async func:bump = NIL(int32->:p) {
    int32:seen = <-p;
    await sleep(raw duration_ms(1i64)) ?| NIL;
    <-p = seen + 40i32;
    pass NIL;
};"""),
      wrong="accepted",
      note="The compiler's tests/backend/programs/borrow_await.npk is exactly this shape and "
           "is expected to run (42) at HUNT2.")

# ---- §5.2 Arenas across threads (table at 307)
claim("cc0309", C, 309, "| Threading | single-threaded | multi-threaded |", "row",
      "A `shared_arena<T>` is multi-threaded: two threads allocate in one shared arena and "
      "read their values back.",
      expect="run:0",
      src=amain(r"""    Channel<int64, 4i32, 4i64>:done = channel() ?! E3;
    {
        shared_arena<int64>:s = shared_arena_make(8i64);
        drop filler(@s, done, 10i64);
        drop filler(@s, done, 20i64);
    }
    int64:a = await done.recv(raw duration_ms(2000i64)) ?! E4;
    int64:b = await done.recv(raw duration_ms(2000i64)) ?! E4;
    if ((a + b) != 30i64) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3, 4) + "\n" + J2 + r"""
thread async func:filler = NIL(shared_arena<int64>->:s, Channel<int64, 4i32, 4i64>:done,
                               int64:base) joins J2 {
    Handle<int64>:h = s.alloc(base);
    int64:v = s.get(h) ?! E1;
    await done.send(v, raw duration_ms(500i64)) ?! E2;
    pass NIL;
};"""),
      wrong="refused, or 10",
      note="The arena reaches the threads by borrow, the compiler's spelling: the reference "
           "gives no way at all, and line 298 says no borrow crosses a thread spawn.")

claim("cc0309b", C, 309, "single-threaded", "row",
      "An `arena<T>` is single-threaded: handing one to a thread is refused.",
      expect="refuse",
      src=amain(r"""    arena<int64>:a = arena_make(4i64);
    {
        drop user(@a);
    }
    exit 0i32;""", errs(1) + "\n" + J2 + r"""
thread async func:user = NIL(arena<int64>->:a) joins J2 {
    Handle<int64>:h = a.alloc();
    a.put(h, 1i64) ?! E1;
    pass NIL;
};"""),
      wrong="accepted: a single-threaded arena is reachable from two threads")

claim("cc0310", C, 310, "**`alloc`, `get`, `destroy` only**", "row",
      "A `shared_arena<T>` has only alloc, get and destroy: `reset` is refused.",
      expect="refuse",
      src=main_(r"""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(1i64);
    s.reset();
    exit 0i32;"""),
      wrong="accepted")

claim("cc0310b", C, 310, "`alloc`, `get`, `free`, `reset`, `destroy`", "row",
      "An `arena<T>` supports alloc, get, free, reset and destroy: reset invalidates a live "
      "handle.",
      expect="run:0",
      src=main_(r"""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h = a.alloc();
    a.put(h, 5i64) ?! E1;
    int64:v = a.get(h) ?! E2;
    if (v != 5i64) { exit 10i32; }
    a.free(h) ?! E3;
    Handle<int64>:h2 = a.alloc();
    a.put(h2, 6i64) ?! E1;
    a.reset();
    Result<int64>:g = a.get(h2);
    if (!g.is_error) { exit 11i32; }
    a.destroy();
    exit 0i32;""", errs(1, 2, 3)),
      wrong="refused (an operation missing), 10 or 11",
      note="`put` stores the value; the row lists no store operation for arena<T>.")

claim("cc0310c", C, 310, "`destroy` only**", "row",
      "A `shared_arena<T>` supports alloc, get and destroy.",
      expect="run:0",
      src=main_(r"""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(raw v64(5i64));
    int64:v = s.get(h) ?! E1;
    if (v != 5i64) { exit 10i32; }
    s.destroy();
    exit 0i32;""", errs(1)),
      wrong="refused (no destroy) or 10")

claim("cc0311", C, 311, "| Per-slot `free` | yes | **no** |", "row",
      "A `shared_arena<T>` has no per-slot free: `free` is refused.",
      expect="refuse",
      src=main_(r"""    shared_arena<int64>:s = shared_arena_make(4i64);
    Handle<int64>:h = s.alloc(1i64);
    s.free(h) ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("cc0311b", C, 311, "| Per-slot `free` | yes |", "row",
      "An `arena<T>` frees per slot: the freed handle fails, a sibling handle still reads.",
      expect="run:0",
      src=main_(r"""    arena<int64>:a = arena_make(4i64);
    Handle<int64>:h1 = a.alloc();
    Handle<int64>:h2 = a.alloc();
    a.put(h1, 11i64) ?! E1;
    a.put(h2, 22i64) ?! E1;
    a.free(h1) ?! E2;
    Result<int64>:g1 = a.get(h1);
    if (!g1.is_error) { exit 10i32; }
    int64:v2 = a.get(h2) ?! E3;
    if (v2 != 22i64) { exit 11i32; }
    a.destroy();
    exit 0i32;""", errs(1, 2, 3)),
      wrong="10 (the freed slot still reads) or 11")

claim("cc0312", C, 312, "**chunked, never moves**", "row",
      "A shared arena's storage is chunked and never moves; an arena<T> may reallocate.",
      untestable="[unobservable] neither operation list yields an address a program could "
                 "compare before and after growth; handles hide where the slot lives")

claim("cc0313", C, 313, "one atomic bump per allocation", "row",
      "An arena<T> allocation costs nothing extra; a shared arena's costs one atomic bump.",
      untestable="[internal] the allocation paths are the runtime's (npk_arena_*, "
                 "npk_sarena_*), not the program's IR")

claim("cc0321", C, 321, "requires that no thread still holds handles", "rule",
      "Destroying a shared arena needs no thread to hold it, by ownership: `destroy` while a "
      "spawned thread still borrows it is refused.",
      expect="refuse",
      src=amain(r"""    shared_arena<int64>:s = shared_arena_make(8i64);
    drop filler(@s);
    s.destroy();
    exit 0i32;""", errs(1) + "\n" + J2 + r"""
thread async func:filler = NIL(shared_arena<int64>->:s) joins J2 {
    Handle<int64>:h = s.alloc(1i64);
    int64:v = s.get(h) ?! E1;
    discard(v);
    pass NIL;
};"""),
      wrong="accepted: the arena is destroyed under a live thread",
      note="Reasoned: 'ownership, not synchronization: the owner destroys it after joining' "
           "makes the pre-join destroy an ownership error.")

claim("cc0326", C, 326, "Race freedom comes from three structural properties", "rule",
      "Race freedom comes from three structural properties (the list that follows has five).",
      untestable="[vague] a count of the document's own list, which it gets wrong (3 vs 5); "
                 "the five properties are tested at cc0298, cc0115, cc0309-0311, cc0092, cc0332")

claim("cc0332", C, 332, "cannot outlive the scope that spawned them either", "rule",
      "Threads cannot outlive the scope that spawned them: a function that spawns a thread "
      "returns only after the thread has finished.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 4i32, 2i64>:done = channel() ?! E2;
    int32:p = await spawner(done) ?! E3;
    if (p != 5i32) { exit 10i32; }
    Result<int32>:r = await done.recv(raw duration_ms(0i64));
    if (r.is_error) { exit 11i32; }
    if (r.value != 7i32) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 3) + "\n" + J2 + r"""
thread async func:w = NIL(Channel<int32, 4i32, 2i64>:done) joins J2 {
    await sleep(raw duration_ms(50i64)) ?| NIL;
    await done.send(7i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};
async func:spawner = int32(Channel<int32, 4i32, 2i64>:done) {
    drop w(done);
    pass 5i32;
};"""),
      wrong="11: the function returned while its thread was running",
      note="Spawned in a helper function so that 'scope' reads the same whether it means the "
           "block or the function.")

claim("cc0350", C, 350, "that two threads can reach is classified", "rule",
      "Every word of runtime/npkrt.ll two threads can reach is classified in npkrt.spec, "
      "and a belt refuses an unclassified access.",
      untestable="[tree] a claim about the runtime's specification files and the tree's belt")

claim("cc0354", C, 354, "Each protocol then has a bounded model in `runtime/models/`", "rule",
      "Each runtime protocol has a bounded model whose bad predicates are proven unreachable, "
      "with a control per predicate.",
      untestable="[tree] a claim about runtime/models/ and the tree's full run")

# ---- §6 Channels
claim("cc0373", C, 373, "```nitpick", "example",
      "`Channel<T, LEVEL, CAP>` is the channel type: an instance with T=int32, LEVEL=3, "
      "CAP=2 carries a value.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    await ch.send(raw v32(5i32), raw duration_ms(100i64)) ?! E2;
    int32:v = await ch.recv(raw duration_ms(100i64)) ?! E3;
    if (v != 5i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3)),
      wrong="refused or 10",
      note="The block is the type's shape with placeholders; it is instantiated.")

claim("cc0379", C, 379, "| `T` | element type |", "row",
      "T is the element type: sending an int64 on a `Channel<int32, ...>` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    await ch.send(5i64, raw duration_ms(10i64)) ?! E2;
    exit 0i32;""", errs(1, 2)),
      wrong="accepted")

claim("cc0380", C, 380, "a channel blocks, so it is a blocking primitive", "row",
      "A channel's LEVEL is a D-056 lock level: a send on a level-4 channel while holding a "
      "level-5 mutex guard is a downward acquisition and is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 5i32>:m = mutex(raw v32(7i32)) ?! E1;
    Channel<int32, 4i32, 2i64>:ch = channel() ?! E2;
    {
        Guard<int32>:g = await m.acquire(raw duration_ms(500i64)) ?! E3;
        await ch.send(g.value, raw duration_ms(500i64)) ?! E4;
    }
    int32:v = await ch.recv(raw duration_ms(500i64)) ?! E5;
    exit v - 7i32;""", errs(1, 2, 3, 4, 5)),
      wrong="accepted: the channel's level is not checked",
      note="Reasoned from this row, line 460 ('waiting on N channels means acquiring N "
           "channel locks') and line 609 ('acquisition must strictly increase'). The "
           "compiler's mutex_basic.npk sends on a level-4 channel under a level-5 guard.")

claim("cc0380b", C, 380, "| `LEVEL` | D-056 lock level", "row",
      "A send on a level-4 channel while holding a level-3 guard is an upward acquisition and "
      "is accepted.",
      expect="run:0",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(raw v32(7i32)) ?! E1;
    Channel<int32, 4i32, 2i64>:ch = channel() ?! E2;
    {
        Guard<int32>:g = await m.acquire(raw duration_ms(500i64)) ?! E3;
        await ch.send(g.value, raw duration_ms(500i64)) ?! E4;
    }
    int32:v = await ch.recv(raw duration_ms(500i64)) ?! E5;
    exit v - 7i32;""", errs(1, 2, 3, 4, 5)),
      wrong="refused, or nonzero")

claim("cc0381", C, 381, "`> 0` is buffered", "row",
      "CAP > 0 is a buffer: with CAP 2 two sends complete with no receiver, and a third with "
      "a zero deadline fails.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    Result<NIL>:s1 = await ch.send(1i32, raw duration_ms(0i64));
    if (s1.is_error) { exit 10i32; }
    Result<NIL>:s2 = await ch.send(2i32, raw duration_ms(0i64));
    if (s2.is_error) { exit 11i32; }
    Result<NIL>:s3 = await ch.send(3i32, raw duration_ms(0i64));
    if (!s3.is_error) { exit 12i32; }
    exit 0i32;""", errs(1)),
      wrong="10/11 (the buffer holds less than CAP) or 12 (more)")

claim("cc0383", C, 383, "A rendezvous is not a one-slot buffer.", "rule",
      "A rendezvous (CAP 0) sender waits for a receiver, not for space: with no receiver a "
      "send times out instead of depositing.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 0i64>:ch = channel() ?! E1;
    Result<NIL>:s = await ch.send(1i32, raw duration_ms(30i64));
    if (!s.is_error) { exit 10i32; }
    if (s.err != DeadlineExceeded) { exit 11i32; }
    exit 0i32;""", errs(1)),
      wrong="10: the send deposited into a slot with no receiver present")

claim("cc0386", C, 386, "Registering as a receiver is itself the event", "rule",
      "A rendezvous completes in both arrival orders: a parked sender is taken by a later "
      "receiver, and a parked receiver takes a later send.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 0i64>:ch = channel() ?! E2;
    drop sender(ch);
    await sleep(raw duration_ms(30i64)) ?| NIL;
    int32:a = await ch.recv(raw duration_ms(2000i64)) ?! E3;
    int32:b = await ch.recv(raw duration_ms(2000i64)) ?! E3;
    if ((a + b) != 42i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
async func:sender = NIL(Channel<int32, 3i32, 0i64>:ch) {
    await ch.send(20i32, raw duration_ms(2000i64)) ?! E1;
    await ch.send(22i32, raw duration_ms(2000i64)) ?! E1;
    pass NIL;
};"""),
      wrong="81 or 83: both sides parked and waited out their deadlines")

claim("cc0394", C, 394, "Capacity lives in the **type**", "rule",
      "Capacity lives in the type: a CAP-2 endpoint cannot be bound as a CAP-4 channel.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:a = channel() ?! E1;
    Channel<int32, 3i32, 4i64>:b = a;
    await b.send(1i32, raw duration_ms(10i64)) ?! E2;
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: the capacity is a runtime property")

claim("cc0399", C, 399, "It is a capacity-1 channel the sender closes.", "rule",
      "A one-shot is a capacity-1 channel the sender closes: the receiver gets the value, then "
      "an error.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:once = channel() ?! E1;
    await once.send(raw v32(7i32), raw duration_ms(100i64)) ?! E2;
    discard(once.close() ?! E3);
    int32:v = await once.recv(raw duration_ms(100i64)) ?! E4;
    if (v != 7i32) { exit 10i32; }
    Result<int32>:after = await once.recv(raw duration_ms(100i64));
    if (!after.is_error) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 3, 4)),
      wrong="84 (the value was lost to the close) or 11")

claim("cc0403", C, 403, "```nitpick", "example",
      "The three operations: `await ch.send(move(v), d)` is Result<NIL>, `await ch.recv(d)` "
      "is Result<T>, `ch.close()` is Result<NIL>.",
      expect="run:0",
      src=amain(r"""    Channel<string, 3i32, 1i64>:ch = channel() ?! E1;
    Duration:deadline = raw duration_ms(500i64);
    string:v = string_concat("he", "llo");
    Result<NIL>:s = await ch.send(move(v), deadline);
    if (s.is_error) { exit 10i32; }
    Result<string>:r = await ch.recv(deadline);
    if (r.is_error) { exit 11i32; }
    string:got = move(r.value);
    if (!(string_equals(got, "hello"))) { exit 12i32; }
    Result<NIL>:c = ch.close();
    if (c.is_error) { exit 13i32; }
    exit 0i32;""", errs(1)),
      wrong="refused or 10-13")

claim("cc0409", C, 409, "was struck", "rule",
      "`len()` was struck: `ch.len()` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    int64:n = ch.len();
    exit (n =>! int32);""", errs(1)),
      wrong="accepted")

claim("cc0415", C, 415, "with a zero deadline, which asks and acts atomically", "rule",
      "A zero deadline asks and acts without waiting: recv on an empty channel fails at once, "
      "recv on a non-empty one takes the value.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    int64:t0 = mono_now();
    Result<int32>:r = await ch.recv(raw duration_ms(0i64));
    if (!r.is_error) { exit 10i32; }
    await ch.send(4i32, raw duration_ms(0i64)) ?! E2;
    Result<int32>:r2 = await ch.recv(raw duration_ms(0i64));
    if (r2.is_error) { exit 11i32; }
    if (r2.value != 4i32) { exit 12i32; }
    if (((mono_now()) - t0) > 1000000000i64) { exit 13i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="10-12, or 13 (a zero deadline waited)")

claim("cc0417", C, 417, "A closed channel is an **error code, never a", "rule",
      "`recv` returns Result<T>: a received zero is a value, and a closed, drained channel is "
      "an error (not a timeout, not a value).",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    await ch.send(raw v32(0i32), raw duration_ms(100i64)) ?! E2;
    discard(ch.close() ?! E3);
    Result<int32>:a = await ch.recv(raw duration_ms(100i64));
    if (a.is_error) { exit 10i32; }
    if (a.value != 0i32) { exit 11i32; }
    Result<int32>:b = await ch.recv(raw duration_ms(100i64));
    if (!b.is_error) { exit 12i32; }
    if (b.err == DeadlineExceeded) { exit 13i32; }
    exit 0i32;""", errs(1, 2, 3)),
      wrong="10 (a zero read as closed), 12 (closed read as a value), 13 (it waited)")

claim("cc0421", C, 421, "the parameter is a RELATIVE", "rule",
      "The deadline is a RELATIVE Duration: `recv(Duration{ ns: 60 ms })` on an empty channel "
      "waits about 60 ms (an absolute reading would expire at once).",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    int64:t0 = mono_now();
    Result<int32>:r = await ch.recv(Duration{ ns: 60000000i64 });
    int64:el = (mono_now()) - t0;
    if (!r.is_error) { exit 10i32; }
    if (el < 50000000i64) { exit 11i32; }
    if (el > 5000000000i64) { exit 12i32; }
    exit 0i32;""", errs(1)),
      wrong="11: the span was read as an absolute time already past",
      note="Timed, with wide bounds (50 ms .. 5 s for a 60 ms span).")

claim("cc0422", C, 422, "(prelude `{ int64:ns }`)", "rule",
      "`Duration` is the prelude struct `{ int64:ns }`.",
      expect="run:0",
      src=main_(r"""    Duration:d = Duration{ ns: raw v64(1500i64) };
    if (d.ns != 1500i64) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")

claim("cc0425", C, 425, "so re-arms cannot drift", "rule",
      "A deadline is converted once to an absolute monotonic time at suspension entry, so "
      "re-arms cannot drift.",
      untestable="[timing] drift across re-arms is a property of wait durations")

claim("cc0426", C, 426, "`DEADLINE_EXCEEDED` (−4107)", "rule",
      "Expiry is the error `DEADLINE_EXCEEDED`: an expired recv's error compares equal to it.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = await ch.recv(raw duration_ms(5i64));
    if (!r.is_error) { exit 10i32; }
    if (r.err != DEADLINE_EXCEEDED) { exit 11i32; }
    exit 0i32;""", errs(1)),
      wrong="refused: the identity is spelled otherwise (DeadlineExceeded)")

claim("cc0426b", C, 426, "(−4107)", "rule",
      "DEADLINE_EXCEEDED's code is 4107 (−4107): comparing an error with it compares against "
      "that constant.",
      expect=r"ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4107\b",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = await ch.recv(raw duration_ms(5i64));
    if (!r.is_error) { exit 10i32; }
    if (r.err != DeadlineExceeded) { exit 11i32; }
    exit 0i32;""", errs(1)),
      wrong="another constant",
      note="The sign is tolerated: TYPE_REFERENCE §11.2 calls it an encoding detail.")

claim("cc0427", C, 427, "`acquire`, the JOIN's trap code", "rule",
      "Expiry is a catchable Result error at an `acquire`: a 1 ms acquire of a mutex another "
      "thread holds returns DeadlineExceeded.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 4i32, 4i64>:done = channel() ?! E2;
    Mutex<int32, 3i32>:h = mutex(0i32) ?! E2;
    drop holder(@h, done);
    discard(await done.recv(raw duration_ms(2000i64)) ?! E3);
    Result<Guard<int32>>:late = await h.acquire(raw duration_ms(1i64));
    if (!late.is_error) { exit 10i32; }
    if (late.err != DeadlineExceeded) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 3) + "\n" + J2 + r"""
thread async func:holder = NIL(Mutex<int32, 3i32>->:m, Channel<int32, 4i32, 4i64>:done) joins J2 {
    Guard<int32>:g = relay await m.acquire(raw duration_ms(500i64));
    await done.send(2i32, raw duration_ms(500i64)) ?! E1;
    await sleep(raw duration_ms(150i64)) ?| NIL;
    g.value = 7i32;
    pass NIL;
};"""),
      wrong="10 (the acquire succeeded under a held lock) or 11",
      note="The mutex reaches the thread by borrow (the compiler's spelling); line 298 says "
           "no borrow crosses a thread spawn and the reference gives no other way.")

claim("cc0428", C, 428, "There is no unbounded `recv`", "rule",
      "Deadlines are mandatory: a `recv()` with no deadline is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = await ch.recv();
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="accepted: an unbounded recv")

claim("cc0429", C, 429, "`try_send` and `try_recv` do not", "rule",
      "`try_recv` does not exist: it is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = ch.try_recv();
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("cc0431", C, 431, "written `move(v)`", "rule",
      "`send` takes ownership, written `move(v)`: sending an owning string without `move` is "
      "refused.",
      expect="refuse",
      src=amain(r"""    Channel<string, 3i32, 1i64>:ch = channel() ?! E1;
    string:s = string_concat("a", "b");
    await ch.send(s, raw duration_ms(100i64)) ?! E2;
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: the transfer is invisible at the call site")

claim("cc0431b", C, 431, "takes ownership", "rule",
      "After `send(move(s), d)` the sender no longer owns s: using s afterwards is refused.",
      expect="refuse",
      src=amain(r"""    Channel<string, 3i32, 1i64>:ch = channel() ?! E1;
    string:s = string_concat("a", "b");
    await ch.send(move(s), raw duration_ms(100i64)) ?! E2;
    if (s.len != 2i64) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: a use after the move")

claim("cc0433", C, 433, "is woken by its peer, not by a timer", "rule",
      "A blocked operation is woken by its peer, not by a polling timer.",
      untestable="[timing] the difference is the latency of a hand-off")

claim("cc0442", C, 442, "Every operation suspends the task, never the thread", "rule",
      "Channel operations are safe across threads (the ring is under a per-channel mutex): two "
      "threads sending 50 each to one channel lose nothing.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 64i64>:ch = channel() ?! E2;
    drop worker(ch);
    drop worker(ch);
    int32:got = 0i32;
    int32:sum = 0i32;
    while (got < 100i32) decreases 100i32 - got {
        Result<int32>:r = await ch.recv(raw duration_ms(2000i64));
        if (r.is_error) { exit 11i32; }
        sum = sum + r.value;
        got = got + 1i32;
    }
    if (sum != 100i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2) + "\n" + J2 + r"""
thread async func:worker = NIL(Channel<int32, 3i32, 64i64>:ch) joins J2 {
    int32:i = 0i32;
    while (i < 50i32) decreases 50i32 - i {
        await ch.send(1i32, raw duration_ms(500i64)) ?! E1;
        i = i + 1i32;
    }
    pass NIL;
};"""),
      wrong="11: a message was lost (the prototype's race)")

claim("cc0454", C, 454, "may not contain a borrow", "rule",
      "A channel element may not contain a borrow: `Channel<int32->, ...>` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32->, 3i32, 1i64>:ch = channel() ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("cc0455", C, 455, "so a slice — which is a borrow (D-070) —", "rule",
      "A slice is a borrow and cannot be sent: `Channel<uint8[], ...>` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<uint8[], 3i32, 1i64>:ch = channel() ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("cc0458", C, 458, "There is no `select`", "rule",
      "There is no `select`: the word is an ordinary identifier.",
      expect="run:0",
      src=main_(r"""    int32:select = raw v32(1i32);
    exit select - 1i32;"""),
      wrong="refused: `select` is reserved")

claim("cc0478", C, 478, "as handles they may cross freely", "rule",
      "Channel endpoints are handles and cross a thread spawn freely, by value.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:c = channel() ?! E2;
    drop w(c);
    int32:v = await c.recv(raw duration_ms(2000i64)) ?! E3;
    if (v != 9i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3) + "\n" + J2 + r"""
thread async func:w = NIL(Channel<int32, 3i32, 1i64>:c) joins J2 {
    await c.send(9i32, raw duration_ms(500i64)) ?! E1;
    pass NIL;
};"""),
      wrong="refused, or 81/83")

claim("cc0479", C, 479, "`StaleHandle` (−4106)", "rule",
      "StaleHandle's code is 4106 (−4106): comparing an error with it compares against that "
      "constant.",
      expect=r"ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4106\b",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    Result<int32>:r = await ch.recv(raw duration_ms(5i64));
    if (!r.is_error) { exit 10i32; }
    if (r.err == StaleHandle) { exit 11i32; }
    exit 0i32;""", errs(1)),
      wrong="another constant",
      note="The sign is tolerated (TYPE_REFERENCE §11.2).")

claim("cc0482", C, 482, "`close` ends the stream, leaving the slot, the buffer and everything", "rule",
      "A closed channel is not reclaimed: values sent before the close are drained, and the "
      "end is reported as an error that is not StaleHandle.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    await ch.send(20i32, raw duration_ms(100i64)) ?! E2;
    await ch.send(22i32, raw duration_ms(100i64)) ?! E2;
    discard(ch.close() ?! E3);
    Result<int32>:a = await ch.recv(raw duration_ms(100i64));
    if (a.is_error) { exit 10i32; }
    Result<int32>:b = await ch.recv(raw duration_ms(100i64));
    if (b.is_error) { exit 11i32; }
    Result<int32>:c = await ch.recv(raw duration_ms(100i64));
    if (!c.is_error) { exit 12i32; }
    if (c.err == StaleHandle) { exit 13i32; }
    if ((a.value + b.value) != 42i32) { exit 14i32; }
    exit 0i32;""", errs(1, 2, 3)),
      wrong="10/11 (close discarded the buffer), 13 (close bumped the generation)")

claim("cc0489", C, 489, "today a channel outlives its creating scope", "rule",
      "Reclamation is not built: a channel outlives the function that created it, so an "
      "endpoint it returns still delivers the value sent before it returned.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 2i64>:c = await make() ?! E3;
    Result<int32>:r = await c.recv(raw duration_ms(100i64));
    if (r.is_error) {
        if (r.err == StaleHandle) { exit 11i32; }
        exit 12i32;
    }
    if (r.value != 7i32) { exit 13i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
async func:make = Channel<int32, 3i32, 2i64>() {
    Channel<int32, 3i32, 2i64>:ch = channel() ?! E1;
    await ch.send(7i32, raw duration_ms(100i64)) ?! E2;
    pass ch;
};"""),
      wrong="refused (the endpoint may not escape its scope) or 11 (the scope's exit "
            "reclaimed it)",
      note="Lines 473-475 say endpoints cannot outlive the creating scope; 486-490 say that "
           "half is not built. The compiler's channel_owning.npk says a function's normal "
           "exit reclaims its channels.")

claim("cc0490", C, 490, "provoked from source.", "rule",
      "StaleHandle cannot be provoked from source today.",
      untestable="[unobservable] a claim that no program can produce the error; cc0489 tests "
                 "the half that is observable")

claim("cc0492", C, 492, "no `destroy` and no endpoint reference counting", "rule",
      "There is no channel `destroy`: `ch.destroy()` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    ch.destroy();
    exit 0i32;""", errs(1)),
      wrong="accepted")

# ---- §7 Actors
claim("cc0501", C, 501, "```nitpick", "example",
      "`Actor<M, R, LEVEL>` is a type with `tell` (Result<NIL>) and `ask` (Result<R>), each "
      "taking a moved message and a deadline.",
      expect="run:0",
      src=amain(r"""    exit 0i32;""", r"""async func:talk = int32(Actor<string, int32, 3i32>:actor, move string:m,
                        move string:m2, Duration:deadline) {
    Result<NIL>:t = await actor.tell(move(m), deadline);
    if (t.is_error) { pass 1i32; }
    Result<int32>:a = await actor.ask(move(m2), deadline);
    if (a.is_error) { pass 2i32; }
    pass a.value;
};"""),
      wrong="refused: no Actor type",
      note="The reference names no actor constructor or spawn form, so the program only "
           "declares a function over an actor and never calls it.")

claim("cc0508", C, 508, "An actor is a **task with a mailbox**", "rule",
      "An actor is a task with a mailbox, not a thread.",
      untestable="[vague] no spelling is given to create or spawn an actor")

claim("cc0513", C, 513, "The mailbox is a `Channel<M, LEVEL, CAP>`", "rule",
      "An actor's mailbox is a Channel<M, LEVEL, CAP>.",
      untestable="[vague] no operation reaches an actor's mailbox; CAP appears in no actor "
                 "type parameter")

claim("cc0518", C, 518, "an endpoint is a generation-checked handle", "rule",
      "An endpoint may ride in a message: a request carrying its reply channel is answered on "
      "that channel.",
      expect="run:0",
      src=amain(r"""    Channel<Req, 3i32, 2i64>:inbox = channel() ?! E3;
    Channel<int32, 5i32, 1i64>:reply = channel() ?! E3;
    drop server(inbox);
    await inbox.send(Req{ add: 21i32, reply: reply }, raw duration_ms(500i64)) ?! E4;
    int32:v = await reply.recv(raw duration_ms(2000i64)) ?! E5;
    if (v != 42i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2, 3, 4, 5) + r"""
struct:Req = {
    int32:add;
    Channel<int32, 5i32, 1i64>:reply;
};
async func:server = NIL(Channel<Req, 3i32, 2i64>:inbox) {
    Req:m = await inbox.recv(raw duration_ms(2000i64)) ?! E1;
    await m.reply.send(m.add * 2i32, raw duration_ms(500i64)) ?! E2;
    pass NIL;
};"""),
      wrong="refused (an endpoint may not ride a channel), or 10")

claim("cc0523", C, 523, "`R = NIL` for an actor that does not reply", "rule",
      "With R = NIL, `ask` is an acknowledgement: it yields Result<NIL>.",
      expect="run:0",
      src=amain(r"""    exit 0i32;""", r"""async func:ack = int32(Actor<string, NIL, 3i32>:actor, move string:m,
                       Duration:deadline) {
    Result<NIL>:a = await actor.ask(move(m), deadline);
    if (a.is_error) { pass 1i32; }
    pass 0i32;
};"""),
      wrong="refused: no Actor type")

claim("cc0526", C, 526, "an actor cannot outlive the scope that spawned", "rule",
      "An actor cannot outlive its spawning scope; scope exit closes, drains and joins it.",
      untestable="[vague] no spelling is given to spawn an actor")

claim("cc0528", C, 528, "`alive` is an `atomic<bool>`", "rule",
      "`atomic<bool>` is a valid atomic: store, load and swap work on it.",
      expect="run:0",
      src=main_(r"""    atomic<bool>:alive = false;
    alive.store(raw vb(true));
    if (!(alive.load())) { exit 10i32; }
    bool:was = alive.swap(false);
    if (!was) { exit 11i32; }
    if (alive.load()) { exit 12i32; }
    exit 0i32;"""),
      wrong="refused or 10-12")

# ---- §8 Thread pools
claim("cc0535", C, 535, "```nitpick", "example",
      "`ThreadPool<LEVEL, CAP>:pool = ThreadPool.create(n)?;` and `await pool.submit(move(job), "
      "deadline)?;` compile and run.",
      expect="run:0",
      src=amain(r"""    string:j = string_concat("job", "");
    int32:r = await run_pool(2i64, move(j), raw duration_ms(500i64)) ?| 10i32;
    exit r;""", r"""async func:run_pool = int32(int64:worker_count, move string:job, Duration:deadline) {
    ThreadPool<3i32, 8i64>:pool = ThreadPool.create(worker_count)?;
    await pool.submit(move(job), deadline)?;
    pass 0i32;
};"""),
      wrong="refused: no ThreadPool type, no static `create`, no postfix `?`",
      note="LEVEL=3, CAP=8, job a string: the example names no job type. IO_REFERENCE line "
           "120-121 says the language has no static methods (`Type.create`).")

claim("cc0540", C, 540, "A thread pool is N worker tasks receiving from one channel.", "rule",
      "A thread pool is N worker tasks receiving from one channel.",
      untestable="[vague] describes the pool's construction, which no program can reach "
                 "without a constructor that works (cc0535)")

claim("cc0550", C, 550, "Submitted work is lexically scoped", "rule",
      "The pool's owning scope does not exit until every submitted job has finished, under a "
      "deadline whose expiry traps.",
      untestable="[vague] no pool can be built from the reference's spelling (cc0535)")

claim("cc0555", C, 555, "The job type is checked.", "rule",
      "The pool's job type is checked.",
      untestable="[vague] the job type is never named")

claim("cc0557", C, 557, "does not exist", "rule",
      "`wait_idle` does not exist.",
      untestable="[unobservable] no pool can be built to call it on (cc0535), so a refusal "
                 "could not be attributed to wait_idle")

# ---- §9 Synchronization primitives (table at 564)
claim("cc0566", C, 566, "owns its data (D-056); no recursive variant", "row",
      "`Mutex<T, LEVEL>` owns its data: the guard reads the initial value, a write through "
      "one guard is seen through the next.",
      expect="run:0",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(raw v32(5i32)) ?! E1;
    {
        Guard<int32>:g = await m.acquire(raw duration_ms(500i64)) ?! E2;
        if (g.value != 5i32) { exit 10i32; }
        g.value = 6i32;
    }
    {
        Guard<int32>:g2 = await m.acquire(raw duration_ms(500i64)) ?! E3;
        if (g2.value != 6i32) { exit 11i32; }
    }
    exit 0i32;""", errs(1, 2, 3)),
      wrong="refused, 10, 11, or 83 (the first guard was never released)")

claim("cc0567", C, 567, "| `RwLock<T, LEVEL>` | owns its data |", "row",
      "`RwLock<T, LEVEL>` owns its data: read guards see it, a write guard changes it.",
      expect="run:0",
      src=amain(r"""    RwLock<int32, 3i32>:r = rwlock(raw v32(7i32)) ?! E1;
    {
        RGuard<int32>:a = await r.read(raw duration_ms(500i64)) ?! E2;
        if (a.value != 7i32) { exit 10i32; }
    }
    {
        Guard<int32>:w = await r.write(raw duration_ms(500i64)) ?! E3;
        w.value = 9i32;
    }
    {
        RGuard<int32>:c = await r.read(raw duration_ms(500i64)) ?! E4;
        if (c.value != 9i32) { exit 11i32; }
    }
    exit 0i32;""", errs(1, 2, 3, 4)),
      wrong="refused, 10 or 11")

claim("cc0568", C, 568, "**`wait` is removed**", "row",
      "`CondVar.wait` is removed: `cv.wait(g)` is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(0i32) ?! E1;
    CondVar<4i32>:cv = condvar() ?! E1;
    Guard<int32>:g = await m.acquire(raw duration_ms(100i64)) ?! E2;
    await cv.wait(g) ?! E3;
    exit 0i32;""", errs(1, 2, 3)),
      wrong="accepted: an untimed wait")

claim("cc0568b", C, 568, "`timedwait` is the only form", "row",
      "`timedwait` is the form: with no signal it returns an error when its deadline expires.",
      expect="run:0",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(0i32) ?! E1;
    CondVar<4i32>:cv = condvar() ?! E1;
    Guard<int32>:g = await m.acquire(raw duration_ms(100i64)) ?! E2;
    Result<NIL>:w = await cv.timedwait(g, raw duration_ms(20i64));
    if (!w.is_error) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="refused, or 10 (a wait with no signal succeeded)")

claim("cc0569", C, 569, "reimplemented natively; LEVELLED like every blocking primitive", "row",
      "`Barrier<N, LEVEL>` exists: a lone arrival at a 3-party barrier fails when its deadline "
      "expires.",
      expect="run:0",
      src=amain(r"""    Barrier<3i32, 6i32>:b = barrier() ?! E1;
    Result<NIL>:lone = await b.arrive(raw duration_ms(30i64));
    if (!lone.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="refused, or 10")

claim("cc0569b", C, 569, "from the unlevelled `Barrier<N>` this table first wrote", "row",
      "The unlevelled `Barrier<N>` is gone: a one-parameter Barrier type is refused.",
      expect="refuse",
      src=amain(r"""    Barrier<3i32>:b = barrier() ?! E1;
    Result<NIL>:lone = await b.arrive(raw duration_ms(30i64));
    if (!lone.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("cc0571", C, 571, "deadline-bounded, and returns `Result`", "rule",
      "Every acquisition is deadline-bounded: `m.acquire()` with no deadline is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(0i32) ?! E1;
    Guard<int32>:g = await m.acquire() ?! E2;
    exit g.value;""", errs(1, 2)),
      wrong="accepted: an unbounded acquire")

claim("cc0574", C, 574, "```nitpick", "example",
      "The critical section is a bare block: the guard is released at the closing brace (a "
      "1 ms re-acquire succeeds) and the write through `guard.value.retries` is kept.",
      expect="run:0",
      src=amain(r"""    Mutex<Config, 3i32>:m = mutex(Config{ retries: 0i32 }) ?! E1;
    int32:r = await configure(@m, raw duration_ms(500i64)) ?! E2;
    if (r != 3i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2) + r"""
struct:Config = { int32:retries; };
async func:configure = int32(Mutex<Config, 3i32>->:cfg_lock, Duration:deadline) {
    {
        Guard<Config>:guard = relay await cfg_lock.acquire(deadline);
        guard.value.retries = 3i32;
    }   // guard drops here; the lock is released
    Guard<Config>:again = relay await cfg_lock.acquire(raw duration_ms(1i64));
    pass again.value.retries;
};"""),
      wrong="82 (the guard was not released at the brace), 10, or refused",
      note="The literal block sits in an async function (relay needs a fallible one).")

claim("cc0581", C, 581, "`await` is not optional here", "rule",
      "`await` is not optional on an acquisition: `m.acquire(d)` without await is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 3i32>:m = mutex(0i32) ?! E1;
    Result<Guard<int32>>:g = m.acquire(raw duration_ms(10i64));
    if (g.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="accepted: a blocking acquire")

claim("cc0584", C, 584, "no `with` construct", "rule",
      "There is no `with` construct for a critical section.",
      untestable="[unobservable] `with` is a reserved VerificationKeyword (LEXICAL §4), so "
                 "neither an identifier nor a statement test can show the absence")

claim("cc0587", C, 587, "There is no lock-free queue.", "rule",
      "There is no lock-free queue.",
      untestable="[vague] no spelling of such a queue is given whose refusal could be tested")

# ---- §10 settled items
claim("cc0609", C, 609, "acquisition must strictly", "rule",
      "Acquisition must strictly increase: holding a level-5 guard, acquiring a level-3 mutex "
      "is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 5i32>:hi = mutex(0i32) ?! E1;
    Mutex<int32, 3i32>:lo = mutex(0i32) ?! E1;
    Guard<int32>:g1 = await hi.acquire(raw duration_ms(100i64)) ?! E2;
    Guard<int32>:g2 = await lo.acquire(raw duration_ms(100i64)) ?! E2;
    g2.value = g1.value;
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: a downward acquisition")

claim("cc0609b", C, 609, "must strictly", "rule",
      "Strictly: holding a level-3 guard, acquiring another level-3 mutex is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 3i32>:a = mutex(0i32) ?! E1;
    Mutex<int32, 3i32>:b = mutex(0i32) ?! E1;
    Guard<int32>:g1 = await a.acquire(raw duration_ms(100i64)) ?! E2;
    Guard<int32>:g2 = await b.acquire(raw duration_ms(100i64)) ?! E2;
    g2.value = g1.value;
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: equal levels held together")

claim("cc0609c", C, 609, "blocking primitive carries a compile-time `LEVEL`", "rule",
      "An increasing acquisition (level 3, then level 5, both held) is accepted.",
      expect="run:0",
      src=amain(r"""    Mutex<int32, 3i32>:lo = mutex(raw v32(4i32)) ?! E1;
    Mutex<int32, 5i32>:hi = mutex(0i32) ?! E1;
    Guard<int32>:g1 = await lo.acquire(raw duration_ms(100i64)) ?! E2;
    Guard<int32>:g2 = await hi.acquire(raw duration_ms(100i64)) ?! E2;
    g2.value = g1.value;
    if (g2.value != 4i32) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="refused, or 10")

claim("cc0613", C, 613, "flag now claims lock-order freedom rather than deadlock freedom", "rule",
      "The concurrency flag claims lock-order freedom, not deadlock freedom.",
      untestable="[tree] a statement about what a flag's documentation claims")

claim("cc0614", C, 614, "`create_recursive` is", "rule",
      "`create_recursive` is removed: calling it is refused.",
      expect="refuse",
      src=amain(r"""    Mutex<int32, 3i32>:m = create_recursive(0i32) ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted: a recursive mutex")

claim("cc0628", C, 628, "`exit` already", "rule",
      "`exit` routes to failsafe when a wild allocation is still live.",
      expect="trap:WildLeak",
      src=main_(r"""    wild int8->:p = alloc(8i64);
    <-p = 1i8;
    exit 0i32;"""),
      wrong="0: the live allocation is ignored",
      note="The arm is reasoned from the prelude identity's name; the text says only that "
           "exit routes to failsafe.")

claim("cc0632", C, 632, "No coroutine is resumed on any thread, no `defer` runs", "rule",
      "A trap is a whole-program event: a suspended task's `defer` (which would divide by "
      "zero) does not run, and failsafe sees the original IntOverflow.",
      expect="trap:IntOverflow",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:c = channel() ?! E2;
    drop guarded(raw v32(0i32), c);
    discard(await c.recv(raw duration_ms(2000i64)) ?! E3);
    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;""", errs(1, 2, 3) + r"""
async func:guarded = NIL(int32:zero, Channel<int32, 3i32, 1i64>:c) {
    defer { discard(10i32 / zero); }
    await c.send(1i32, raw duration_ms(500i64)) ?! E1;
    await sleep(raw duration_ms(3000i64)) ?| NIL;
    pass NIL;
};"""),
      wrong="97 (the task was resumed to unwind and ran its defer) or 70")

claim("cc0635", C, 635, "stop *before* `failsafe` gets control", "rule",
      "Other threads stop before failsafe gets control.",
      untestable="[timing] an ordering between threads at the moment of a trap")

claim("cc0636", C, 636, "`failsafe` runs on the trapping thread as a", "rule",
      "failsafe runs on the trapping thread: a trap on a spawned thread runs failsafe on that "
      "thread (its gettid is not the process id).",
      expect="run:0", fs=False,
      src=amain(r"""    drop boom(raw v32(0i32));
    await sleep(raw duration_ms(3000i64)) ?| NIL;
    exit 0i32;""", J2 + r"""
thread async func:boom = NIL(int32:zero) joins J2 {
    await sleep(raw duration_ms(10i64)) ?| NIL;
    int32:q = 10i32 / zero;
    discard(q);
    pass NIL;
};""") + r"""
func:failsafe = int32(Error:e) {
    int64:tid = sys(186i64) ?| 0i64;
    int64:me = sys(39i64) ?| 0i64;
    if (tid == me) { exit 10i32; }
    pick (e) {
        (DivByZero) { exit 0i32; },
        (*) { exit 11i32; }
    }
    exit 12i32;
};
""",
      wrong="10 (failsafe ran on the main thread) or 11")

claim("cc0637", C, 637, "plain call and **may not be `async`**", "rule",
      "`failsafe` may not be `async`: an async failsafe is refused.",
      expect="refuse", fs=False,
      src=main_(r"""    exit 0i32;""") + r"""
async func:failsafe = int32(Error:_~e) {
    exit 1i32;
};
""",
      wrong="accepted")

claim("cc0641", C, 641, "thread registry (64 slots", "rule",
      "The floor keeps a 64-slot thread registry, claimed and published before the clone.",
      untestable="[internal] the registry's layout; the text states no outcome for a 65th "
                 "live thread")

claim("cc0646", C, 646, "is the exit-70 stop", "rule",
      "A re-entering failsafe holder is the exit-70 stop: a trap inside failsafe ends the "
      "process with 70.",
      expect="run:70", fs=False,
      src=main_(r"""    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;""") + r"""
func:failsafe = int32(Error:_~e) {
    int32:z = raw v32(0i32);
    int32:q = 10i32 / z;
    exit q;
};
""",
      wrong="a hang, a recursion into failsafe, or 97")


# ================================================================== IO_REFERENCE.md

for _suf, _w in (("", "stream"), ("b", "process"), ("c", "pipe"), ("d", "debug"), ("e", "log")):
    claim(("io0015" + _suf) if _w != "stream" else "io0014", I, 15 if _w != "stream" else 14,
          "returns it to userland along with `process`, `pipe`, `debug`, and `log`"
          if _w != "stream" else "D-074",
          "rule",
          "D-074 returns `%s` to userland: it is an ordinary identifier." % _w,
          expect="run:0",
          src=main_(r"""    int32:W = raw v32(1i32);
    exit W - 1i32;""".replace("W", _w)),
          wrong="refused: `%s` is still reserved" % _w)

claim("io0016", I, 16, "what follows needs language syntax", "rule",
      "Nothing in the I/O model needs language syntax.",
      untestable="[vague] no checkable outcome")

claim("io0022", I, 22, "`Stream` describes what every readable or writable thing can", "rule",
      "`Stream` is the trait every readable or writable thing implements: it can bound a "
      "generic parameter.",
      expect="run:0",
      src=main_(r"""    exit 0i32;""", r"""func:takes<S: Stream> = int32(S->:_~s) never fails {
    pass 0i32;
};"""),
      wrong="refused: no trait named Stream (the example defines Reader and Writer)")

claim("io0023", I, 23, "files, pipes, sockets, and memory buffers are stdlib types implementing it", "rule",
      "Files, pipes, sockets and memory buffers are stdlib types implementing the stream "
      "trait.",
      untestable="[vague] names no socket or memory-buffer type to test")

claim("io0025", I, 25, "```nitpick", "example",
      "Reader and Writer have the example's shape: user types implementing `read`, `write` and "
      "`flush` with exactly those signatures are called through them.",
      expect="run:0",
      src=amain(r"""    Count:c = Count{ total: 0i64 };
    int64:n = await c.write(string_bytes("abcd"), raw duration_ms(100i64)) ?! E1;
    await c.flush(raw duration_ms(100i64)) ?! E2;
    if (n != 4i64) { exit 10i32; }
    if (c.total != 4i64) { exit 11i32; }
    Ones:o = Ones{ left: 1i64 };
    uint8[3]:buf = [0u8, 0u8, 0u8];
    int64:m = await o.read(buf[0i64...3i64], raw duration_ms(100i64)) ?! E3;
    if (m != 3i64) { exit 12i32; }
    Result<int64>:e = await o.read(buf[0i64...3i64], raw duration_ms(100i64));
    if (!e.is_error) { exit 13i32; }
    exit 0i32;""", errs(1, 2, 3) + r"""
struct:Count = { int64:total; };
impl:Count:Writer = {
    async func:write = int64(Count->:self, fixed uint8[]:wsrc, Duration:_~within) {
        self.total = self.total + wsrc.len;
        pass wsrc.len;
    };
    async func:flush = NIL(Count->:self, Duration:_~within) {
        pass NIL;
    };
};
struct:Ones = { int64:left; };
impl:Ones:Reader = {
    async func:read = int64(Ones->:self, uint8[]:dest, Duration:_~within) {
        if (self.left <= 0i64) { fail IoEof; }
        self.left = self.left - 1i64;
        pass dest.len;
    };
};"""),
      wrong="refused (a signature does not match the trait) or 10-13")

claim("io0036", I, 36, "receivers are `Self->`", "rule",
      "Receivers are `Self->`: an impl whose receiver is by value is refused.",
      expect="refuse",
      src=main_(r"""    exit 0i32;""", r"""struct:Count = { int64:total; };
impl:Count:Writer = {
    async func:write = int64(Count:self, fixed uint8[]:wsrc, Duration:_~within) {
        pass wsrc.len;
    };
    async func:flush = NIL(Count:self, Duration:_~within) {
        pass NIL;
    };
};"""),
      wrong="accepted: a by-value receiver consumes the stream per call")

claim("io0039b", I, 39, "are relative spans named `within`", "rule",
      "Deadline parameters are relative spans named `within`.",
      untestable="[timing] relativity shows only as a wait's duration; cc0421 measures it on "
                 "a channel")

claim("io0039", I, 39, "An impl must keep the trait's", "rule",
      "An impl must keep the trait's `async`: a synchronous `write` in an impl of Writer is "
      "refused with TYPE-048.",
      expect="refuse:TYPE-048",
      src=main_(r"""    exit 0i32;""", r"""struct:Count = { int64:total; };
impl:Count:Writer = {
    func:write = int64(Count->:self, fixed uint8[]:wsrc, Duration:_~within) {
        pass wsrc.len;
    };
    async func:flush = NIL(Count->:self, Duration:_~within) {
        pass NIL;
    };
};"""),
      wrong="accepted, or another code")

claim("io0045", I, 45, "Every operation is `async`", "rule",
      "Every stream operation is async: `r.read(..)` without await is refused.",
      expect="refuse",
      src=amain(r"""    Path:p = path_parse("/dev/null") ?! E1;
    ByteReader:r = byte_reader_open(p, raw duration_ms(100i64)) ?! E2;
    uint8[4]:buf = [0u8, 0u8, 0u8, 0u8];
    Result<int64>:n = r.read(buf[0i64...4i64], raw duration_ms(100i64));
    if (!n.is_error) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: a blocking read")

claim("io0048", I, 48, "through raw syscalls", "rule",
      "The executor's readiness mechanism is io_uring or epoll through raw syscalls.",
      untestable="[internal] the executor is the runtime's; the syscalls it makes are not "
                 "visible to a program")

claim("io0050", I, 50, "and carries a **deadline**", "rule",
      "Every operation carries a deadline (there is no unbounded read): `read` without one is "
      "refused.",
      expect="refuse",
      src=amain(r"""    Path:p = path_parse("/dev/null") ?! E1;
    ByteReader:r = byte_reader_open(p, raw duration_ms(100i64)) ?! E2;
    uint8[4]:buf = [0u8, 0u8, 0u8, 0u8];
    Result<int64>:n = await r.read(buf[0i64...4i64]);
    if (!n.is_error) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="accepted: an unbounded read")

claim("io0052", I, 52, "a read cannot be told a length that disagrees", "rule",
      "Buffers are slices: a read into a 4-byte slice of an 8-byte array takes 4 bytes of 8 "
      "available and leaves the rest of the array alone.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
    int64:k = await w.write(string_bytes("abcdefgh"), raw duration_ms(500i64)) ?! E1;
    if (k != 8i64) { exit 20i32; }
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...4i64], raw duration_ms(500i64)) ?! E2;
    if (n != 4i64) { exit 10i32; }
    if (buf[4i64] != 0u8) { exit 11i32; }
    if (buf[3i64] != 100u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10 or 11: the read overran the slice")

claim("io0063", I, 63, "Object safety holds", "rule",
      "Reader and Writer are object-safe: `dyn Writer` and `dyn Reader` values dispatch to the "
      "user impls.",
      expect="run:0",
      src=amain(r"""    Count:c = Count{ total: 0i64 };
    dyn Writer:d = move(c);
    int64:n = await d.write(string_bytes("abc"), raw duration_ms(100i64)) ?! E1;
    if (n != 3i64) { exit 10i32; }
    Ones:o = Ones{ left: 1i64 };
    dyn Reader:dr = move(o);
    uint8[2]:buf = [0u8, 0u8];
    int64:m = await dr.read(buf[0i64...2i64], raw duration_ms(100i64)) ?! E2;
    if (m != 2i64) { exit 11i32; }
    exit 0i32;""", errs(1, 2) + r"""
struct:Count = { int64:total; };
impl:Count:Writer = {
    async func:write = int64(Count->:self, fixed uint8[]:wsrc, Duration:_~within) {
        self.total = self.total + wsrc.len;
        pass wsrc.len;
    };
    async func:flush = NIL(Count->:self, Duration:_~within) {
        pass NIL;
    };
};
struct:Ones = { int64:left; };
impl:Ones:Reader = {
    async func:read = int64(Ones->:self, uint8[]:dest, Duration:_~within) {
        if (self.left <= 0i64) { fail IoEof; }
        self.left = self.left - 1i64;
        pass dest.len;
    };
};"""),
      wrong="refused (not object-safe) or 10/11")

claim("io0070", I, 70, "```nitpick", "example",
      "`Result<int64>:n = await src.read(dest, deadline);` yields the number of bytes read.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:src = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
        int64:k = await w.write(string_bytes("abc"), raw duration_ms(500i64)) ?! E1;
        if (k != 3i64) { exit 20i32; }
    }
""" + BUF8 + r"""    uint8[]:dest = buf[0i64...8i64];
    Duration:deadline = raw duration_ms(500i64);
    Result<int64>:n = await src.read(dest, deadline);
    if (n.is_error) { exit 10i32; }
    if (n.value != 3i64) { exit 11i32; }
    exit 0i32;""", errs(1, 9)),
      wrong="refused, 10 or 11")

claim("io0074", I, 74, "returns the number of bytes placed in `dest`", "rule",
      "`read` returns the number of bytes placed in dest: 5 available into an 8-byte slice "
      "gives 5.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
    int64:k = await w.write(string_bytes("hello"), raw duration_ms(500i64)) ?! E1;
    if (k != 5i64) { exit 20i32; }
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 5i64) { exit 10i32; }
    if (buf[4i64] != 111u8) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10 (the slice length is returned) or 11")

_EOF_BODY = pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
        int64:k = await w.write(string_bytes("x"), raw duration_ms(500i64)) ?! E1;
        if (k != 1i64) { exit 20i32; }
    }
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 1i64) { exit 10i32; }
    Result<int64>:e = await r.read(buf[0i64...8i64], raw duration_ms(500i64));
    if (!e.is_error) { exit 11i32; }
"""

claim("io0075", I, 75, "code `E_EOF` = −4096", "rule",
      "End of input is the error code `E_EOF`: a read of an exhausted stream fails with it.",
      expect="run:0",
      src=amain(_EOF_BODY + r"""    if (e.err != E_EOF) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="refused: the identity is spelled otherwise (IoEof); 11 (EOF is a zero count)")

claim("io0075b", I, 75, "= −4096", "rule",
      "E_EOF's code is 4096 (−4096): comparing a read's error with the EOF identity compares "
      "against that constant.",
      expect=r"ir:icmp (eq|ne) i32 [^\n]*[ ,(]-?4096\b",
      src=amain(_EOF_BODY + r"""    if (e.err != IoEof) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="another constant",
      note="Spelled IoEof (the compiler's name) so that only the value is tested; the sign "
           "is tolerated (TYPE_REFERENCE §11.2).")

claim("io0077", I, 77, "pins the value", "rule",
      "tests/backend/programs/fd_io.npk pins E_EOF's value with a running program.",
      untestable="[tree] a claim about a test file in the compiler repository (it compares "
                 "with the identity IoEof, not with a number)")

claim("io0078", I, 78, "No operation returns a sentinel", "rule",
      "No operation returns a sentinel: an exhausted read is an error, not a zero count.",
      expect="run:0",
      src=amain(_EOF_BODY + r"""    exit 0i32;""", errs(1, 2, 9)),
      wrong="11: end of input came back as a value")

claim("io0090", I, 90, "end-of-input is an error code, exactly as a closed channel is", "rule",
      "A closed, drained channel is an error code, as end-of-input is.",
      expect="run:0",
      src=amain(r"""    Channel<int32, 3i32, 1i64>:ch = channel() ?! E1;
    discard(ch.close() ?! E2);
    Result<int32>:r = await ch.recv(raw duration_ms(100i64));
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="10")

claim("io0099", I, 99, "**different types** rather than a mode flag on one type", "rule",
      "Text and byte streams are different types: a ByteWriter cannot be bound as a "
      "TextWriter.",
      expect="refuse",
      src=main_(pipe() + r"""    ByteWriter:bw = ByteWriter{ sink: own_fd(wfd =>! fd) };
    TextWriter<ByteWriter>:tw = move(bw);
    exit 0i32;""", errs(9)),
      wrong="accepted: one type with a mode")

claim("io0103", I, 103, "| Translation | **none, ever** | on |", "row",
      "A byte stream never translates: `a\\r\\nb\\n` written by a ByteWriter reads back as the "
      "same 5 bytes.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
        int64:k = await w.write(string_bytes("a\r\nb\n"), raw duration_ms(500i64)) ?! E1;
        if (k != 5i64) { exit 20i32; }
    }
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 5i64) { exit 10i32; }
    if (buf[1i64] != 13u8) { exit 11i32; }
    if (buf[2i64] != 10u8) { exit 12i32; }
    if (buf[4i64] != 10u8) { exit 13i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10-13: a byte stream translated line endings")

claim("io0104", I, 104, "and lone `\\r` all yield `\\n`", "row",
      "A text reader reads `\\r\\n`, `\\n` and a lone `\\r` each as one line break: "
      "`a\\r\\nb\\nc\\rd` is four lines.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:br = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
        int64:k = await w.write(string_bytes("a\r\nb\nc\rd"), raw duration_ms(500i64)) ?! E1;
        if (k != 8i64) { exit 20i32; }
    }
    TextReader<ByteReader>:tr = raw text_reader(move(br));
    string:l1 = await text_read_line(@tr, raw duration_ms(500i64)) ?! E2;
    string:l2 = await text_read_line(@tr, raw duration_ms(500i64)) ?! E2;
    string:l3 = await text_read_line(@tr, raw duration_ms(500i64)) ?! E2;
    string:l4 = await text_read_line(@tr, raw duration_ms(500i64)) ?! E2;
    if (!(string_equals(l1, "a"))) { exit 10i32; }
    if (!(string_equals(l2, "b"))) { exit 11i32; }
    if (!(string_equals(l3, "c"))) { exit 12i32; }
    if (!(string_equals(l4, "d"))) { exit 13i32; }
    Result<string>:l5 = await text_read_line(@tr, raw duration_ms(500i64));
    if (!l5.is_error) { exit 14i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10-14 (a break kind not recognised, or an empty line minted)",
      note="text_reader / text_read_line are the compiler's spellings: the reference names "
           "no text-reading operation.")

claim("io0105", I, 105, "`\\n`, unless opened requesting otherwise", "row",
      "A text writer created with LineEnding.Lf writes `\\n` as `\\n`.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:br = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:bw = ByteWriter{ sink: own_fd(wfd =>! fd) };
        TextWriter<ByteWriter>:tw = raw text_writer(move(bw), LineEnding.Lf);
        await text_write_str(@tw, "x\ny\n", raw duration_ms(500i64)) ?! E1;
    }
""" + BUF8 + r"""    int64:n = await br.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 4i64) { exit 10i32; }
    if (buf[1i64] != 10u8) { exit 11i32; }
    if (buf[3i64] != 10u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10-12")

claim("io0106", I, 106, "| Unit | `uint8[]` |", "row",
      "A byte stream's unit is `uint8[]`: passing a `string` to a ByteWriter's write is "
      "refused.",
      expect="refuse",
      src=amain(pipe() + r"""    ByteWriter:bw = ByteWriter{ sink: own_fd(wfd =>! fd) };
    int64:n = await bw.write("abc", raw duration_ms(100i64)) ?! E1;
    exit (n =>! int32) - 3i32;""", errs(1, 9)),
      wrong="accepted: a string converts to bytes implicitly")

claim("io0111", I, 111, "is a creation parameter held in the writer", "rule",
      "The line ending is a creation parameter held in the writer, not in the type: an Lf and "
      "a CrLf writer have one type, and one function writes differently through each.",
      expect="run:0",
      src=amain(pipe("1") + pipe("2") + r"""    ByteReader:r1 = ByteReader{ src: own_fd(rfd1 =>! fd) };
    ByteReader:r2 = ByteReader{ src: own_fd(rfd2 =>! fd) };
    {
        ByteWriter:b1 = ByteWriter{ sink: own_fd(wfd1 =>! fd) };
        TextWriter<ByteWriter>:t1 = raw text_writer(move(b1), LineEnding.Lf);
        await emit(@t1, raw duration_ms(500i64)) ?! E1;
    }
    {
        ByteWriter:b2 = ByteWriter{ sink: own_fd(wfd2 =>! fd) };
        TextWriter<ByteWriter>:t2 = raw text_writer(move(b2), LineEnding.CrLf);
        await emit(@t2, raw duration_ms(500i64)) ?! E1;
    }
""" + BUF8 + r"""    int64:n1 = await r1.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n1 != 2i64) { exit 10i32; }
    int64:n2 = await r2.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n2 != 3i64) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 9) + r"""
async func:emit = NIL(TextWriter<ByteWriter>->:w, Duration:d) {
    relay await text_write_str(w, "q\n", d);
    pass NIL;
};"""),
      wrong="refused (the ending is in the type), 10 or 11")

claim("io0115", I, 115, "```nitpick", "example",
      "`TextWriter:w = text_writer_create(sink, LineEnding.Lf) ?! …;` and the CrLf twin build "
      "text writers; the CrLf one writes `\\r\\n`.",
      expect="run:0",
      src=amain(pipe("1") + pipe("2") + r"""    ByteReader:r1 = ByteReader{ src: own_fd(rfd1 =>! fd) };
    ByteReader:r2 = ByteReader{ src: own_fd(rfd2 =>! fd) };
    {
        ByteWriter:sink = ByteWriter{ sink: own_fd(wfd1 =>! fd) };
        TextWriter:w = text_writer_create(sink, LineEnding.Lf) ?! E1;
        await text_write_str(@w, "a\n", raw duration_ms(500i64)) ?! E3;
    }
    {
        ByteWriter:sink = ByteWriter{ sink: own_fd(wfd2 =>! fd) };
        TextWriter:w = text_writer_create(sink, LineEnding.CrLf) ?! E2;   // greppable opt-in
        await text_write_str(@w, "a\n", raw duration_ms(500i64)) ?! E3;
    }
""" + BUF8 + r"""    int64:n1 = await r1.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E4;
    if (n1 != 2i64) { exit 10i32; }
    int64:n2 = await r2.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E4;
    if (n2 != 3i64) { exit 11i32; }
    if (buf[1i64] != 13u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 3, 4, 9)),
      wrong="refused (no text_writer_create; TextWriter needs a type argument), or 10-12",
      note="`?! …` is completed with E1/E2; the two declarations of w sit in separate "
           "blocks, each with its own sink.")

claim("io0117", I, 117, "LineEnding.CrLf", "rule",
      "LineEnding.CrLf is the opt-in: a CrLf text writer writes `a\\nb` as `a\\r\\nb`.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:br = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:bw = ByteWriter{ sink: own_fd(wfd =>! fd) };
        TextWriter<ByteWriter>:tw = raw text_writer(move(bw), LineEnding.CrLf);
        await text_write_str(@tw, "a\nb", raw duration_ms(500i64)) ?! E1;
    }
""" + BUF8 + r"""    int64:n = await br.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 4i64) { exit 10i32; }
    if (buf[1i64] != 13u8) { exit 11i32; }
    if (buf[2i64] != 10u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10-12")

claim("io0121", I, 121, "static methods — every trait and impl method takes `self`", "rule",
      "The language has no static methods: an impl method without `self`, called as "
      "`Type.method()`, is refused.",
      expect="refuse",
      src=main_(r"""    Maker:m = raw Maker.make();
    exit m.v - 1i32;""", r"""struct:Maker = { int32:v; };
impl:Maker = {
    func:make = Maker() never fails {
        pass Maker{ v: 1i32 };
    };
};"""),
      wrong="accepted: a static method")

claim("io0124", I, 124, "`Path.parse` spelling this document used", "rule",
      "Construction is a bare function: the `Path.parse` spelling is refused.",
      expect="refuse",
      src=main_(r"""    Path:p = Path.parse("/tmp") ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("io0130", I, 130, "never inferred from whether the output is a terminal", "rule",
      "Buffering is never inferred from whether the output is a terminal.",
      untestable="[platform] needs a terminal on stdout to compare with a pipe; the harness "
                 "has none")

claim("io0134", I, 134, "| `stdin` | fully buffered |", "row",
      "stdin is fully buffered.",
      untestable="[unobservable] how far a reader fetches ahead of what it returns is not "
                 "visible to the program; stdin is /dev/null here")

claim("io0135", I, 135, "| `stdout` | line buffered, always |", "row",
      "stdout is line buffered, always: with fd 1 on a pipe, a partial line written through "
      "std_out() is not delivered until its newline.",
      expect="run:0",
      src=amain(pipe() + r"""    discard(sys(33i64, wfd => int64, 1i64) ?! E9);
    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E1;
    await text_write_str(@so, "ab", raw duration_ms(500i64)) ?! E2;
""" + BUF8 + r"""    Result<int64>:early = await r.read(buf[0i64...8i64], raw duration_ms(50i64));
    if (!early.is_error) { exit 10i32; }
    await text_write_str(@so, "c\n", raw duration_ms(500i64)) ?! E3;
    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E4;
    if (n != 4i64) { exit 11i32; }
    if (buf[2i64] != 99u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 3, 4, 9)),
      wrong="10: the partial line was delivered (unbuffered); 84/11: the newline did not "
            "ship it",
      note="dup2(pipe, 1) first, so std_out()'s dup is the pipe; the type spelling is the "
           "one line 151-152 gives.")

claim("io0136", I, 136, "| `stderr` | **unbuffered, always** |", "row",
      "stderr is unbuffered: with fd 2 on a pipe, a partial line written through std_err() "
      "is delivered at once.",
      expect="run:0",
      src=amain(pipe() + r"""    discard(sys(33i64, wfd => int64, 2i64) ?! E9);
    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    TextWriter<ByteWriter>:se = std_err() ?! E1;
    await text_write_str(@se, "ab", raw duration_ms(500i64)) ?! E2;
""" + BUF8 + r"""    Result<int64>:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64));
    if (n.is_error) { exit 10i32; }
    if (n.value != 2i64) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10: the partial line was held back (buffered)")

claim("io0144", I, 144, "`io_isatty` remains available", "rule",
      "`io_isatty` is available and answers whether a descriptor is a terminal.",
      untestable="[vague] the reference gives no signature, so no call can be written from "
                 "the text; no BUILTIN_REFERENCE row names io_isatty")

claim("io0151", I, 151, "(`std_out` returns", "rule",
      "`std_out` returns `TextWriter<LineBufWriter<ByteWriter>>`: buffering is a type.",
      expect="run:0",
      src=amain(r"""    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E1;
    await text_flush(@so, raw duration_ms(100i64)) ?! E2;
    exit 0i32;""", errs(1, 2)),
      wrong="refused: another return type")

claim("io0157", I, 157, "`defer` does not run on a trap (D-014)", "rule",
      "`defer` does not run on a trap: a registered defer that would divide by zero does not "
      "run when the program traps IntOverflow.",
      expect="trap:IntOverflow",
      src=main_(r"""    int32:z = raw v32(0i32);
    defer { discard(10i32 / z); }
    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;"""),
      wrong="97 (the defer ran at the trap) or 70")

claim("io0158", I, 158, "**No flush is attempted**", "rule",
      "No flush is attempted on a trap: a partial line in line-buffered stdout is lost when "
      "the program traps.",
      expect="sh:0",
      sh=r"""cat > t.npk <<'EOF'
mod:t;

func:v32 = int32(int32:x) never fails { pass x; };

async func:main = int32(cstring[]:_~argv) {
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! Unreachable;
    await text_write_str(@so, "partial-m11", raw duration_ms(500i64)) ?! Unreachable;
    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;
};

func:failsafe = int32(Error:e) {
    pick (e) {
        (IntOverflow) { exit 93i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};
EOF
"$NPKC" t.npk -o t.ll > npkc.log 2>&1 || exit 2
llc -O0 -filetype=obj -relocation-model=static t.ll -o t.o || exit 3
ld.lld -static t.o "$NPKRT" -o t || exit 4
env -i ./t > out.txt 2> err.txt < /dev/null
rc=$?
[ "$rc" -eq 93 ] || exit 5
if grep -q 'partial-m11' out.txt; then exit 1; fi
exit 0""",
      wrong="1: the partial line reached stdout (a flush at the trap, or no buffering); "
            "2-5: the probe did not build or did not trap")

claim("io0163", I, 163, "so diagnostics written to it survive a trap", "rule",
      "stderr is unbuffered, so a partial line written to it survives a trap.",
      expect="sh:0",
      sh=r"""cat > t.npk <<'EOF'
mod:t;

func:v32 = int32(int32:x) never fails { pass x; };

async func:main = int32(cstring[]:_~argv) {
    TextWriter<ByteWriter>:se = std_err() ?! Unreachable;
    await text_write_str(@se, "diag-m11", raw duration_ms(500i64)) ?! Unreachable;
    int32:x = raw v32(2147483647i32) + 1i32;
    exit x;
};

func:failsafe = int32(Error:e) {
    pick (e) {
        (IntOverflow) { exit 93i32; },
        (*) { exit 99i32; }
    }
    exit 9i32;
};
EOF
"$NPKC" t.npk -o t.ll > npkc.log 2>&1 || exit 2
llc -O0 -filetype=obj -relocation-model=static t.ll -o t.o || exit 3
ld.lld -static t.o "$NPKRT" -o t || exit 4
env -i ./t > out.txt 2> err.txt < /dev/null
rc=$?
[ "$rc" -eq 93 ] || exit 5
grep -q 'diag-m11' err.txt || exit 1
exit 0""",
      wrong="1: the diagnostic was lost at the trap; 2-5: the probe did not build or trap")

claim("io0165", I, 165, "The registry of open streams is reachable from `failsafe`", "rule",
      "The registry of open streams is reachable from failsafe, which may flush.",
      untestable="[vague] no spelling reaches the registry; its shape is an open item "
                 "(line 282)")

claim("io0175", I, 175, "```nitpick", "example",
      "`Path:p = path_parse(\"/etc/hosts\") ?! …; ByteReader:r = byte_reader_open(p, within) "
      "?! …;` opens a file for reading.",
      expect="run:0",
      src=amain(r"""    Duration:within = raw duration_ms(500i64);
    Path:p = path_parse("/etc/hosts") ?! E1;
    ByteReader:r = byte_reader_open(p, within) ?! E2;
""" + BUF8 + r"""    Result<int64>:n = await r.read(buf[0i64...8i64], within);
    if (n.is_error) {
        if (n.err != IoEof) { exit 10i32; }
    }
    exit 0i32;""", errs(1, 2)),
      wrong="81/82 (the open failed), refused, or 10",
      note="`?! …` completed with E1/E2; within declared; a read shows the reader works.")

claim("io0184", I, 184, "open `O_NONBLOCK | O_CLOEXEC`", "rule",
      "Opened descriptors are O_NONBLOCK and O_CLOEXEC.",
      expect="run:0",
      src=main_(r"""    Path:p = path_parse("/dev/null") ?! E1;
    ByteReader:r = byte_reader_open(p, raw duration_ms(100i64)) ?! E2;
    int64:d = r.src.value =>! int64;
    int64:fl = sys(72i64, d, 3i64) ?! E3;
    if ((fl & 2048i64) == 0i64) { exit 10i32; }
    int64:fdfl = sys(72i64, d, 1i64) ?! E4;
    if ((fdfl & 1i64) == 0i64) { exit 11i32; }
    exit 0i32;""", errs(1, 2, 3, 4)),
      wrong="10 (blocking) or 11 (inherited across exec)",
      note="F_GETFL (3) for O_NONBLOCK (2048), F_GETFD (1) for FD_CLOEXEC (1); the field "
           "path r.src.value is the compiler's.")

claim("io0187", I, 187, "**Opening takes a `Path`**, never a `string`", "rule",
      "Opening takes a Path, never a string: `byte_reader_open(\"/dev/null\", d)` is refused.",
      expect="refuse",
      src=main_(r"""    ByteReader:r = byte_reader_open("/dev/null", raw duration_ms(100i64)) ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted: a string opens a stream")

claim("io0188", I, 188, "absolute, lexically normalized, and contains no interior NUL", "rule",
      "A Path is absolute: parsing a relative path fails.",
      expect="run:0",
      src=main_(r"""    Result<Path>:rel = path_parse("etc/hosts");
    if (!rel.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="10")

claim("io0188b", I, 188, "lexically normalized", "rule",
      "A Path is lexically normalized: `/a/./b/../c//d` parses as `/a/c/d`.",
      expect="run:0",
      src=main_(r"""    Path:p = path_parse("/a/./b/../c//d") ?! E1;
    if (!(string_equals(p.text, "/a/c/d"))) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="10",
      note="The text field `p.text` is the compiler's spelling.")

claim("io0188c", I, 188, "contains no interior NUL", "rule",
      "A Path contains no interior NUL: parsing `/a\\0b` fails.",
      expect="run:0",
      src=main_(r"""    Result<Path>:z = path_parse("/a\0b");
    if (!z.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="10")

claim("io0189", I, 189, "where the conversion", "rule",
      "The conversion to cstring rejects interior NULs: `to_cstring(\"ab\\0cd\")` fails.",
      expect="run:0",
      src=main_(r"""    Result<cstring>:c = to_cstring("ab\0cd");
    if (!c.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="10: the poison NUL passes")

claim("io0191", I, 191, "POSIX's `-1` goes to `Result.err`", "rule",
      "An fd is always valid: a failed open is a Result error, not a -1 descriptor.",
      expect="run:0",
      src=main_(r"""    Path:p = path_parse("/nonexistent_m11_dir/x.tmp") ?! E1;
    Result<ByteReader>:r = byte_reader_open(p, raw duration_ms(100i64));
    if (!r.is_error) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="10: a stream over no descriptor")

claim("io0196", I, 196, "Lexical normalization is not kernel resolution", "rule",
      "Normalization is lexical: `/no_such_dir_m11/../etc` normalizes to `/etc` though the "
      "directory does not exist.",
      expect="run:0",
      src=main_(r"""    Path:p = path_parse("/no_such_dir_m11/../etc") ?! E1;
    if (!(string_equals(p.text, "/etc"))) { exit 10i32; }
    exit 0i32;""", errs(1)),
      wrong="81 (the kernel was asked) or 10")

claim("io0204", I, 204, "and is closed at scope", "rule",
      "A stream is closed at the exit of the scope that opened it: after the writer's block, "
      "the reader drains its byte and then sees end of input.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
        int64:k = await w.write(string_bytes("x"), raw duration_ms(500i64)) ?! E1;
        if (k != 1i64) { exit 20i32; }
    }
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 1i64) { exit 10i32; }
    Result<int64>:e = await r.read(buf[0i64...8i64], raw duration_ms(500i64));
    if (!e.is_error) { exit 11i32; }
    if (e.err != IoEof) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="12 (DeadlineExceeded: the write end stayed open past its scope)")

claim("io0210", I, 210, "There is no `close` in the surface.", "rule",
      "There is no close in the surface: `w.close()` on a stream is refused.",
      expect="refuse",
      src=main_(pipe() + r"""    ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
    w.close() ?! E1;
    exit 0i32;""", errs(1, 9)),
      wrong="accepted")

claim("io0212", I, 212, "`close(release_fd(move o))` is the explicit spelling", "rule",
      "`close(release_fd(move o))` closes an owned descriptor and reports the verdict: the "
      "reader then sees end of input.",
      expect="run:0",
      src=amain(pipe() + r"""    OwnedFd:o = own_fd(wfd =>! fd);
    Result<NIL>:c = close(release_fd(move o));
    if (c.is_error) { exit 10i32; }
    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
""" + BUF8 + r"""    Result<int64>:e = await r.read(buf[0i64...8i64], raw duration_ms(500i64));
    if (!e.is_error) { exit 11i32; }
    if (e.err != IoEof) { exit 12i32; }
    exit 0i32;""", errs(9)),
      wrong="refused (`move o` is spelled `move(o)`), or 10-12",
      note="Literal `move o`, as the reference writes it.")

claim("io0213", I, 213, "no double-close is", "rule",
      "No double close is spellable: a second `release_fd(move(o))` of a moved owner is "
      "refused.",
      expect="refuse",
      src=main_(pipe() + r"""    OwnedFd:o = own_fd(wfd =>! fd);
    Result<NIL>:c = close(release_fd(move(o)));
    Result<NIL>:c2 = close(release_fd(move(o)));
    if (c.is_error) { exit 10i32; }
    if (c2.is_error) { exit 11i32; }
    exit 0i32;""", errs(9)),
      wrong="accepted: a double close")

claim("io0215", I, 215, "A stream cannot be sent through a channel", "rule",
      "A stream cannot be sent through a channel: `Channel<ByteReader, ...>` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<ByteReader, 3i32, 1i64>:ch = channel() ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("io0216", I, 216, "refusal fires on `OwnedFd`", "rule",
      "The element refusal fires on OwnedFd: `Channel<OwnedFd, ...>` is refused.",
      expect="refuse",
      src=amain(r"""    Channel<OwnedFd, 3i32, 1i64>:ch = channel() ?! E1;
    exit 0i32;""", errs(1)),
      wrong="accepted")

claim("io0218", I, 218, "A MOVE into a spawn is legal", "rule",
      "A move of a stream into a thread spawn is legal: the thread writes through the moved "
      "writer, and its scope's close gives the reader end of input.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:r = ByteReader{ src: own_fd(rfd =>! fd) };
    ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
    drop feed(move(w));
""" + BUF8 + r"""    int64:n = await r.read(buf[0i64...8i64], raw duration_ms(1000i64)) ?! E3;
    if (n != 3i64) { exit 10i32; }
    Result<int64>:e = await r.read(buf[0i64...8i64], raw duration_ms(1000i64));
    if (!e.is_error) { exit 11i32; }
    if (e.err != IoEof) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 3, 9) + "\n" + J2 + r"""
thread async func:feed = NIL(move ByteWriter:w) joins J2 {
    int64:n = await w.write(string_bytes("xyz"), raw duration_ms(500i64)) ?! E1;
    if (n != 3i64) { fail E2; }
    pass NIL;
};"""),
      wrong="refused, or 10-12")

claim("io0220", I, 220, "A BORROW of a stream still refuses at the", "rule",
      "A borrow of a stream refuses at the spawn.",
      expect="refuse",
      src=amain(pipe() + r"""    ByteWriter:w = ByteWriter{ sink: own_fd(wfd =>! fd) };
    {
        drop feed(@w);
    }
    exit 0i32;""", errs(1, 9) + "\n" + J2 + r"""
thread async func:feed = NIL(ByteWriter->:w) joins J2 {
    int64:n = await w.write(string_bytes("x"), raw duration_ms(500i64)) ?! E1;
    discard(n);
    pass NIL;
};"""),
      wrong="accepted")

claim("io0227", I, 227, "```nitpick", "example",
      "`await s.seek(Whence.Start, offset, deadline)` returns Result<int64>, the new position.",
      expect="run:0",
      src=amain(tmpfile("io0227", "hello!", 6) + r"""    ByteReader:s = byte_reader_open(p, raw duration_ms(500i64)) ?! E9;
    int64:offset = raw v64(4i64);
    Duration:deadline = raw duration_ms(500i64);
    Result<int64>:np = await s.seek(Whence.Start, offset, deadline);
    if (np.is_error) { exit 10i32; }
    if (np.value != 4i64) { exit 11i32; }
""" + BUF8 + r"""    int64:g = await s.read(buf[0i64...8i64], deadline) ?! E9;
    if (g != 2i64) { exit 12i32; }
    if (buf[0i64] != 111u8) { exit 13i32; }
    drop scrub(p);
    exit 0i32;""", errs(9) + "\n" + SCRUB),
      wrong="refused, or 10-13")

claim("io0231", I, 231, "not an `int64` constant", "rule",
      "`Whence` is an enum, not an int64: seeking with `0i64` as the origin is refused.",
      expect="refuse",
      src=amain(r"""    Path:p = path_parse("/dev/null") ?! E1;
    ByteReader:s = byte_reader_open(p, raw duration_ms(100i64)) ?! E2;
    int64:np = await s.seek(0i64, 0i64, raw duration_ms(100i64)) ?! E3;
    exit (np =>! int32);""", errs(1, 2, 3)),
      wrong="accepted")

claim("io0231b", I, 231, "`Start`, `Current`, `End`", "rule",
      "Whence.End, Whence.Start and Whence.Current measure from the end, the start and the "
      "current position.",
      expect="run:0",
      src=amain(tmpfile("io0231b", "hello!", 6) + r"""    ByteReader:s = byte_reader_open(p, raw duration_ms(500i64)) ?! E9;
    Duration:d = raw duration_ms(500i64);
    int64:e = await s.seek(Whence.End, 0i64, d) ?! E1;
    if (e != 6i64) { exit 10i32; }
    int64:a = await s.seek(Whence.Start, 1i64, d) ?! E1;
    if (a != 1i64) { exit 11i32; }
    int64:c = await s.seek(Whence.Current, 2i64, d) ?! E1;
    if (c != 3i64) { exit 12i32; }
""" + BUF8 + r"""    int64:g = await s.read(buf[0i64...8i64], d) ?! E9;
    if (g != 3i64) { exit 13i32; }
    if (buf[0i64] != 108u8) { exit 14i32; }
    drop scrub(p);
    exit 0i32;""", errs(1, 9) + "\n" + SCRUB),
      wrong="10-14")

claim("io0232", I, 232, "Seeking a buffered stream discards the read buffer", "rule",
      "Seeking a buffered stream discards its read buffer: after a text reader has read "
      "`ab` (buffering `cd`), seeking to the start and reading gives `ab` again.",
      expect="run:0",
      src=amain(tmpfile("io0232", r"ab\ncd\n", 6) + r"""    ByteReader:br = byte_reader_open(p, raw duration_ms(500i64)) ?! E9;
    TextReader<ByteReader>:tr = raw text_reader(move(br));
    Duration:d = raw duration_ms(500i64);
    string:l1 = await text_read_line(@tr, d) ?! E1;
    if (!(string_equals(l1, "ab"))) { exit 10i32; }
    int64:np = await tr.seek(Whence.Start, 0i64, d) ?! E2;
    if (np != 0i64) { exit 11i32; }
    string:l2 = await text_read_line(@tr, d) ?! E3;
    if (!(string_equals(l2, "ab"))) { exit 12i32; }
    drop scrub(p);
    exit 0i32;""", errs(1, 2, 3, 9) + "\n" + SCRUB),
      wrong="refused (a buffered stream has no seek) or 12 (`cd`: the buffer survived)")

claim("io0239", I, 239, "are `TextReader` / `TextWriter` over the three", "rule",
      "The standard streams are TextReader/TextWriter over the inherited descriptors: std_in() "
      "reads fd 0 (here /dev/null) and meets end of input at once.",
      expect="run:0",
      src=amain(r"""    TextReader<ByteReader>:si = std_in() ?! E1;
    Result<string>:l = await text_read_line(@si, raw duration_ms(500i64));
    if (!l.is_error) { exit 10i32; }
    if (l.err != IoEof) { exit 11i32; }
    TextWriter<ByteWriter>:se = std_err() ?! E2;
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E3;
    exit 0i32;""", errs(1, 2, 3)),
      wrong="refused, 10 or 11")

claim("io0242", I, 242, "They are **not** globals that any code may grab.", "rule",
      "The standard streams are not globals: the name `stdout` is not defined.",
      expect="refuse",
      src=main_(r"""    discard(stdout);
    exit 0i32;"""),
      wrong="accepted: a global stdout")

claim("io0242b", I, 242, "They belong to `main`'s scope and", "rule",
      "The standard streams belong to main's scope and are passed down: constructing one in a "
      "helper function is refused.",
      expect="refuse",
      src=amain(r"""    int32:r = await helper() ?| 5i32;
    exit r;""", errs(1, 2) + r"""
async func:helper = int32() {
    TextWriter<ByteWriter>:se = std_err() ?! E1;
    await text_write_str(@se, "", raw duration_ms(100i64)) ?! E2;
    pass 0i32;
};"""),
      wrong="accepted: any code may grab a standard stream",
      note="Reasoned from 'not globals that any code may grab' with 'constructors called in "
           "main's scope' (247-248). The compiler's text_roundtrip.npk calls std_in() "
           "outside main.")

claim("io0248", I, 248, "Each owns a `F_DUPFD_CLOEXEC` DUP", "rule",
      "Each standard stream owns an F_DUPFD_CLOEXEC dup: its descriptor is not 0-2 and has "
      "FD_CLOEXEC.",
      expect="run:0",
      src=main_(r"""    TextWriter<ByteWriter>:se = std_err() ?! E1;
    int64:d = se.inner.sink.value =>! int64;
    if (d < 3i64) { exit 10i32; }
    int64:fl = sys(72i64, d, 1i64) ?! E2;
    if ((fl & 1i64) == 0i64) { exit 11i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="10 (the inherited descriptor itself) or 11 (no close-on-exec)",
      note="The field path se.inner.sink.value is the compiler's.")

claim("io0249", I, 249, "scope-exit close can never close 0/1/2", "rule",
      "Scope-exit close never closes 0/1/2: after std_in/out/err are built and dropped, "
      "descriptors 0, 1 and 2 are still open.",
      expect="run:0",
      src=main_(r"""    {
        TextReader<ByteReader>:si = std_in() ?! E1;
        TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E1;
        TextWriter<ByteWriter>:se = std_err() ?! E1;
    }
    Result<int64>:f0 = sys(72i64, 0i64, 1i64);
    if (f0.is_error) { exit 10i32; }
    Result<int64>:f1 = sys(72i64, 1i64, 1i64);
    if (f1.is_error) { exit 11i32; }
    Result<int64>:f2 = sys(72i64, 2i64, 1i64);
    if (f2.is_error) { exit 12i32; }
    exit 0i32;""", errs(1)),
      wrong="10-12: a drop closed an inherited descriptor")

claim("io0250", I, 250, "The inherited descriptors stay BLOCKING", "rule",
      "The inherited descriptors stay blocking: after std_in/out/err are built, fds 0-2 lack "
      "O_NONBLOCK.",
      expect="run:0",
      src=main_(r"""    TextReader<ByteReader>:si = std_in() ?! E1;
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E1;
    TextWriter<ByteWriter>:se = std_err() ?! E1;
    int64:f0 = sys(72i64, 0i64, 3i64) ?! E2;
    if ((f0 & 2048i64) != 0i64) { exit 10i32; }
    int64:f1 = sys(72i64, 1i64, 3i64) ?! E2;
    if ((f1 & 2048i64) != 0i64) { exit 11i32; }
    int64:f2 = sys(72i64, 2i64, 3i64) ?! E2;
    if ((f2 & 2048i64) != 0i64) { exit 12i32; }
    exit 0i32;""", errs(1, 2)),
      wrong="10-12: O_NONBLOCK set on the shared open-file description")

claim("io0252", I, 252, "blocks the thread, bounded by the consumer", "rule",
      "A write to a stuffed stdout pipe blocks the thread, bounded by the consumer.",
      untestable="[timing] a blocked thread shows only as a duration")

claim("io0261", I, 261, "`cstring` at the boundary (D-049)", "row",
      "nlibc is raw syscalls with cstring at the boundary: the floor's `open` refuses a "
      "`string` path.",
      expect="refuse",
      src=main_(r"""    string:s = "/dev/null";
    Result<fd>:f = open(s, 0i64, 0i64);
    if (f.is_error) { exit 10i32; }
    exit 0i32;"""),
      wrong="accepted: a string reaches the syscall boundary",
      note="The row also lists `io_uring_*`, which line 279-281 says is refused (D-184).")

claim("io0262", I, 262, "the text and byte streams, buffering, the standard streams", "row",
      "The stdlib layer supplies Path, Reader/Writer, the text and byte streams, buffering and "
      "the standard streams, and they compose.",
      expect="run:0",
      src=amain(r"""    Path:p = path_parse("/dev/null") ?! E1;
    ByteReader:br = byte_reader_open(p, raw duration_ms(100i64)) ?! E2;
    dyn Reader:dr = move(br);
""" + BUF8 + r"""    Result<int64>:n = await dr.read(buf[0i64...8i64], raw duration_ms(100i64));
    if (!n.is_error) { exit 10i32; }
    TextWriter<LineBufWriter<ByteWriter>>:so = std_out() ?! E3;
    exit 0i32;""", errs(1, 2, 3)),
      wrong="refused or 10")

claim("io0267", I, 267, "**`printf` and `scanf` are not in either layer**", "rule",
      "`printf` is not available.",
      expect="refuse",
      src=main_(r"""    printf("x");
    exit 0i32;"""),
      wrong="accepted")

claim("io0268", I, 268, "spliced by `&{ }` interpolation", "rule",
      "Formatting is ordinary functions returning string, spliced by `&{ }` interpolation.",
      expect="run:0",
      src=main_(r"""    int64:x = raw v64(42i64);
    string:s = `v=&{ int_to_string(x) }`;
    if (!(string_equals(s, "v=42"))) { exit 10i32; }
    exit 0i32;"""),
      wrong="refused or 10")

claim("io0269", I, 269, "There is no format-specifier language", "rule",
      "There is no format-specifier language: a text writer writes `%d` verbatim.",
      expect="run:0",
      src=amain(pipe() + r"""    ByteReader:br = ByteReader{ src: own_fd(rfd =>! fd) };
    {
        ByteWriter:bw = ByteWriter{ sink: own_fd(wfd =>! fd) };
        TextWriter<ByteWriter>:tw = raw text_writer(move(bw), LineEnding.Lf);
        await text_write_str(@tw, "%d\n", raw duration_ms(500i64)) ?! E1;
    }
""" + BUF8 + r"""    int64:n = await br.read(buf[0i64...8i64], raw duration_ms(500i64)) ?! E2;
    if (n != 3i64) { exit 10i32; }
    if (buf[0i64] != 37u8) { exit 11i32; }
    if (buf[1i64] != 100u8) { exit 12i32; }
    exit 0i32;""", errs(1, 2, 9)),
      wrong="10-12: the writer interpreted a specifier")

claim("io0280", I, 280, "and only epoll", "rule",
      "The readiness mechanism is epoll only, with no timerfd; io_uring is refused.",
      untestable="[internal] the executor's syscalls are the runtime's, not visible to a "
                 "program")
