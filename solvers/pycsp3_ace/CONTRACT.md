# pycsp3_ace: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how PyCSP3 2.6.1
with the ACE 2.6 solver expresses it. Runner: [run.py](run.py), which plugs its own
`pycsp3_solver` into `main("pycsp3")` of [runner/runtime.py](../../runner/runtime.py)
(request parsing, the overall timer and error handling stay runtime's) and runs the model
in a child process per solve round. [metadata.yaml](metadata.yaml) declares no
`instance_binding`: the instance is passed as it is, so no problem is withheld for its
shape.

## Submission file

One plain PyCSP3 script, `model.py`, starting with `from pycsp3 import *`. It may import
`pycsp3`, `lxml` and the standard library; nothing else is installed (no NumPy). No other
file of yours is staged, so helpers go in the same file. It must not call `solve()`, and
it is run once per round (see [Solving](#solving)), so it must build the same model each
time.

## Entrypoint

There is no function. The runner executes the whole file with
`runpy.run_path(model.py, run_name="__main__")` in a fresh child process, then reads the
module-level names equal to the declared outputs from the resulting namespace. The model
posts constraints with `satisfy(...)` and at most one `minimize(...)` or `maximize(...)`.
The runner replaces `pycsp3.solve` beforehand: a call from the model raises `RuntimeError:
the model must not call solve(); the runner solves it`.

## Instance

`from pycsp3 import *` gives the instance as `data`, an object holding every field of the
instance JSON, unconverted: a field is an attribute, `data.n`, or an item, `data["n"]`
(both work for names such as `_SHIP`). Values are plain Python `int`, `bool`, `str` and
`list`, 0-based; lists of lists may be ragged and keep their lengths, and nothing is turned
into a named tuple. Metadata such as `name` or `note` is present, and a model that never
reads it is unaffected. A missing field raises `AttributeError: 'Instance' object has no
attribute ...` (`execution_error`).

The runner bypasses pycsp3's own data loading (which builds named tuples and cannot take
field names with a leading underscore): it starts pycsp3 with a placeholder
`-data=<round dir>/placeholder.json` and `-output=<round dir>/` on `sys.argv`, and sets
`pycsp3.data` before the model's star import binds it.

## Outputs

Each declared output is a module-level name equal to the output name, bound to a `Var`, a
`VarArray`, or a nested list of them with the declared shape; a plain `int` leaf is also
accepted as a constant. After solving, the runner reads each variable's recorded value for
every solution ACE printed and reports it as a plain integer: a Boolean output (`dom={0,
1}`) is reported as 0/1. Auxiliary variables are never reported. Errors, all
`execution_error`:

- an output name not defined: `NameError: the model does not define the declared output 'x'`;
- an output variable that no constraint mentions (ACE reports only those):
  `ValueError: declared output 'z' has a variable that no constraint mentions, so ACE does
  not report it; constrain it, e.g. satisfy(z >= 0)`;
- an output element left undetermined in a solution: `ValueError: a declared output has no
  determined value in the solution`;
- any other leaf type: `TypeError: declared output of type T is not an integer variable`;
- outputs with different numbers of recorded solutions.

## Objective

At most one `minimize(term)` or `maximize(term)` with an integer term, in the direction
the brief gives; none for a satisfaction problem. The runner wraps both functions: in the
first round it records the direction and passes the call through; in later rounds the same
call posts `satisfy(term == optimum)` instead, so the objective must be the same term
every time the file runs.

## Solving

A **round** is one child process: one run of the model, one pycsp3 compilation to XCSP3
(`model-placeholder.xml`), and one ACE run through pycsp3's `solve(solver=ACE, sols=...,
options="-t=<s>s -ev")`. The submission cannot change these options. ACE runs through the
wrapper `/opt/runner/ace` (`java -jar ACE-2.6.jar "$@" 2>&1`), so Java's stderr reaches
ACE's log; `-ev` makes ACE print the cause of a failure (without it ACE prints only
`! ERROR`).

- **Errors**: a log line matching `ERROR|Exception|OutOfMemoryError|Fatal Error` (other
  than ACE's "use -ev" hint) makes the round `error` with up to three such lines as detail
  (e.g. `Fatal Error: The id E is a keyword`, `java.lang.OutOfMemoryError`). A pycsp3
  modelling error, which pycsp3 prints as `ERROR: message` before a `SystemExit`, is
  reported as `pycsp3: message` (e.g. `pycsp3: The identifier z is used twice. This is
  not possible`); any other exception as `Type: message`. A child that leaves no result
  is `error` ("pycsp3 process exited N without a result: <log tail>"). All give
  `execution_error`, never a timeout.
- **Optimisation**: the first round runs ACE's full search (`sols=ALL`); its last
  solution is used only when ACE reports `s OPTIMUM`. `UNSAT` is `unsat`; any other
  status is `timeout` ("Candidate optimum was not proven") with no solution reported,
  never the incumbent. The optimum is pycsp3's `bound()`; without it the run is `error`.
  With a solution limit of 1 the run stops after that solution (`limit`); otherwise later
  rounds pin the objective (`satisfy(term == optimum)`) and enumerate as below.
- **Satisfaction**: the first round asks for `solution_limit` solutions; later rounds for
  the ones still missing.
- **Verification**: ACE 2.6 accepts some invalid tuples (a `Product` over four or more
  variables), so every new solution is checked by the XCSP3 `SolutionChecker` from the
  same jar (`java -cp ACE-2.6.jar org.xcsp.parser.callbacks.SolutionChecker <xml>
  <instantiation>`) on the round's own XML and the full instantiation ACE printed for it.
  `INVALID` rejects it; `OK` accepts it, and for the optimum the checker's cost must also
  equal ACE's bound. Checker output that is neither is `error`. A rejected assignment is
  not reported but is excluded like a found one, and the search continues; if only
  rejected solutions exist the run is `error` ("ACE reported only solutions that fail
  verification").
- **Next solution**: solutions are projected onto the declared outputs and deduplicated
  (as sorted JSON), since auxiliary variables can repeat an output assignment. Each later
  round re-runs the model and adds, for every assignment seen so far (accepted or
  rejected), the nogood `Or(v != value for each output variable)`, matrices element-wise
  (constant leaves are skipped; a nogood with no variable makes the round `UNSAT`).
- **Exhaustion and stop**: `limit` once enough checked solutions are out; ACE's `UNSAT`
  or `d COMPLETE EXPLORATION` is exhaustion (`complete`, or `unsat` with nothing
  reported); a round that returns fewer solutions than asked without exhaustion is
  `timeout` ("The search stopped before it was exhausted"); a full round with no new
  output assignment is `error` ("A solution round returned no new output assignment").
- **Time**: the deadline is `execution_timeout` from the start of `pycsp3_solver`. A round
  or a checker call needs at least 3 s left, else `timeout`; ACE gets `-t=<int(left) -
  2>s`, and the round's process group (Python and Java) is killed when the time left runs
  out. A `SIGALRM` at exactly `execution_timeout` from the start of `main` also turns into
  `timeout`; on that path, solutions already found are not emitted. Solutions found before
  a `timeout` on the other paths are emitted.

## Compilation

No separate step: pycsp3 compiles the model to XCSP3 inside every round, within the
execution budget. `compilation_timeout` does not apply.

## Environment

Image `dcp-eval/pycsp3_ace:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, pycsp3 2.6.1 and its one dependency lxml 6.1.3 (hash-pinned
wheels, [requirements.txt](requirements.txt)), Debian's `openjdk-17-jre-headless`. ACE 2.6
is the jar inside the wheel,
`/usr/local/lib/python3.12/site-packages/pycsp3/solvers/ace/ACE-2.6.jar`, called through
`/opt/runner/ace`. `JAVA_TOOL_OPTIONS="-Xmx1200m -XX:-UsePerfData
-Djava.io.tmpdir=/tmp"` keeps the heap at 1200 MiB inside the 2048 MiB container limit
(a kernel kill is `memory_limit`; a Java `OutOfMemoryError` ACE reports is
`execution_error`). JSON is the standard library's `json`. Each round starts a Python and
a Java process; a small run takes about 2 s wall in total.

The evaluator runs the container with no network, a read-only root file system, user
65534, `HOME=/tmp`, the working directory `/tmp` (a 512 MiB tmpfs; rounds run in
directories under it), `/input` read-only holding only `model.py` and `request.json`, 1
CPU and 2048 MiB. The image's entrypoint is the runner (`python /opt/runner/run.py`); for
an ad hoc run override it: `docker run --rm --network none --entrypoint sh
dcp-eval/pycsp3_ace:v1 -c 'cd /tmp && python ...'`.

## Traps

- **Every output element must be in a constraint**, or the run is `execution_error`
  (ACE does not report unconstrained variables).
- **Reserved identifiers**: `E` and the XCSP keywords (`min`, `max`, `dist`, `in`, `set`,
  `sin`, `card`, ...) as variable ids stop ACE with `The id E is a keyword`
  (`execution_error`).
- **`Product` of four or more variables**: ACE 2.6 accepts invalid tuples; the checker
  rejects them, so the model stays correct but enumeration slows down. Split into binary
  products with an auxiliary `VarArray`.
- **The model runs once per round**: nondeterministic model code (random, iteration order
  of a `set` of objects, the clock) can build a different model in a later round.
- **A request without declared outputs** is `error` ("The request declares no outputs").
- No problem is withheld for its instance shape: ragged and mixed fields arrive as
  Python lists, and handling them is the model's job.

## Example

The pilot fixture [tests/fixtures/model_pycsp3.py](../../tests/fixtures/model_pycsp3.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
# PyCSP3 star-imports its vocabulary, as every PyCSP3 model does.
# ruff: noqa: F403, F405
from pycsp3 import *

n = data.n
x = Var(range(n + 1))
y = Var(range(n + 1))
if data.optimize:
    satisfy(x + y >= n)
    minimize(x + y)
else:
    satisfy(x + y == n)
```
