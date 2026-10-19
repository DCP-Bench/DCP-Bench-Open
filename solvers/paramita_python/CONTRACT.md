# paramita_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Paramita
(Python, SAT and MaxSAT) expresses it. Runner: [run.py](run.py), which takes only `emit`
and `finish` from [runner/runtime.py](../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`, written against `paramita.modelling` (paramita 1.2.0) and
the standard library; no modelling layer of the integration's own is installed beside
paramita, and no other file of yours is staged. Do not create or call a solver: the
runner encodes and solves.

## Entrypoint

```python
def build(instance) -> tuple[subject_to, dict] | tuple[subject_to, dict, tuple[str, expr]]:
```

The runner imports the file and calls `build(instance)` once. It must return a tuple
(not a list) of length 2 or 3:

- `(subject_to, outputs)` for a satisfaction problem;
- `(subject_to, outputs, objective)` for an optimisation problem.

`subject_to` is one Boolean expression or a list of them, built from `Bool` variables
with `&`, `|`, `~`, `And`, `Or`, `Not`, `If`, `Iff` and PB comparisons over weighted
sums of Bools (`2 * a + 3 * b + c <= 4`). Something else in `subject_to` fails when
the runner encodes it: `error` (`execution_error`). Anything the module prints, at import or in `build`, goes to
stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Every field is there, including ragged or mixed-type ones the
brief lists as unbindable (as parsed JSON) and extra keys (`name`, `note`) to ignore. A
problem without instance fields still receives `instance`.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a leaf or a nested
`list`/`tuple` of leaves. Values are read from the solver's assignment of the named
Bools. A leaf is one of:

- a `Bool`, or any Boolean expression over Bools (`a & b`, `x + y == n`): reported as a
  JSON Boolean;
- an integer expression over Bools (`sum(w * b) + c`, `1 * b`, `-e`): reported as a JSON
  integer;
- a Python `int` or `bool` constant: reported as is.

Anything else (a string, a float) is an `error` (`execution_error`). An output the
brief declares as an integer must be an integer expression: a cell that is a Bool goes
out as `1 * b`, since a bare Bool is reported as a Boolean.

Integer outputs are computed by the runner in Python integers, not in paramita's 32-bit
`evaluate`: an output beyond 32 bits is exact as long as each coefficient fits in 32 bits
(`sum(10**k * digit_k)` for a ten-digit number is fine). A Bool or Boolean expression
inside such a sum counts as 0 or 1.

## Objective

The third element of the returned tuple: `("minimize", expr)` or `("maximize", expr)`, a
tuple of exactly two items whose `expr` is a linear integer expression over Bools
(`sum(w * b) + c`). Anything else, including a bare `Bool` or a Boolean expression such
as `x == 1`, is refused with `error` (`an objective must be a linear integer expression
over Bools`); write a single Bool as `1 * b`. An objective that is also an output is the
same expression in both places. Leave the objective out for a satisfaction problem.

## Solving

- Fixed by the runner: every constraint is encoded with `to_cnf` and its default PB
  encoder (`BestEncoder`), through one `DimacsVariablePool` per encoding. Satisfaction
  uses `SatSolver.from_name("Cadical300")` (CaDiCaL 3.0.0) through `add_to_container`;
  optimisation uses `MaxSatSolver.from_name("EvalMaxSAT2022")` through
  `add_to_weighted_container`, which maximises its objective argument: `maximize`
  passes the expression, `minimize` its negation. The constant that call returns plus
  `benefit()` must equal the declared objective's value in the model, or the run is an
  `error` (`the MaxSAT objective does not match the declared objective`).
- Satisfaction status: CaDiCaL `True` is an answer; `False` before any answer is
  `unsat`, after one `complete`; still undecided at the deadline is `timeout`. Reaching
  the solution limit is `limit`, which is not a failure.
- Optimisation status: only a proven optimum (`OPTIMAL`) is reported; `UNSATISFIABLE`
  is `unsat`; a search not finished at the deadline is `timeout` (`the optimum was not
  proven`), with nothing reported, which the evaluator records as `execution_timeout`;
  an exception in the MaxSAT process, or its death without an answer, is `error`.
- Enumeration blocks the declared outputs, not the whole assignment: after each answer
  the runner adds one clause over every Bool named in `outputs`, ruling out that
  combination. Two assignments that agree on every output count once: a repeated output
  value is re-solved, not emitted. Unsat after a blocking clause is `complete`, and so is
  an output that names no Bool (nothing to block). A Bool the solver never saw is
  unconstrained and reported `false`.
- Optimisation enumeration: the first optimal assignment is emitted at once. Then, in a
  second forked child (so a crash there cannot lose the optimum already emitted), the
  runner encodes the constraints again into a fresh CaDiCaL instance, adds the hard PB
  constraint `expr == optimum` and a block of the first answer, and enumerates the
  remaining optimal outputs as above. A child that crashes or raises, or does not finish
  by the deadline, ends the run as `timeout` (`the optimum was proven, the enumeration
  was not`); the solutions already emitted stand.
- Time: the budget runs from before `build`, so building spends it. EvalMaxSAT has no
  budget, so it runs in a forked child that is killed 0.5 s before the runner's deadline
  (itself 0.5 s before the budget). CaDiCaL supports only a conflict budget, so it runs
  in calls of 5000 conflicts and the clock is checked between them. A SIGALRM at the
  budget turns a hang in Python (in `build`, or while waiting on a solver) into
  `timeout`.
- Stack and recursion: the default PB encoder recurses once per term, so a PB constraint
  over about a thousand Bools overflows the default 8 MB stack (signal 11). Before
  anything else the runner raises its stack soft limit to the hard limit and re-executes
  itself, and sets Python's recursion limit to 1 000 000, so a flat `sum` over thousands
  of Bools (a chain of nested additions) does not exceed it either.
- A legacy request is `unsupported`.

## Compilation

None.

## Environment

Image `dcp-eval/paramita_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11
(`/usr/local/bin/python`), paramita 1.2.0 from PyPI, and plugins built from
[paramita-plugins](https://codeberg.org/paramita/paramita-plugins) at commit
`a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb`: the SAT solver Cadical300 (CaDiCaL 3.0.0),
the MaxSAT solver EvalMaxSAT2022, and the PB-to-CNF encoders pblib (under
`/usr/local/share/paramita/plugins`) and pysat (under `/usr/share/paramita/plugins`).
Only the plugins' shared objects are copied into the runtime image, so no compiler is
present. The standard library (`json` included) and paramita's own dependencies; no
licence, no size limit, no environment variables of note.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs,
the working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`, no `/dataset`. The paramita plugins print to file descriptor 1 when they load,
and EvalMaxSAT writes `c ...` lines there; the runner points fd 1 at stderr before any
plugin loads and writes the protocol to a saved copy. The image's entrypoint is the
runner (`python /opt/runner/run.py`); for an ad hoc run override it, e.g. `docker run
--rm --network none --entrypoint sh dcp-eval/paramita_python:v1 -c '...'`.

## Traps

- Integers are 32-bit inside paramita. A coefficient outside that range is a `TypeError`
  while building (`execution_error`); a constraint or objective whose value leaves it
  wraps around without an error, and the evaluator then rejects the wrong value. Only
  integer outputs are read exactly beyond 32 bits (see Outputs).
- `Xor` and `^` are not supported by `to_cnf` (`execution_error`): expand into `&`, `|`,
  `~`.
- A bare `Bool` under an integer output is reported as `true`/`false`, not `1`/`0`:
  write `1 * b`.
- Because enumeration blocks the combination of Bools an output is built from, an
  integer output over Bools that several assignments map to one value (a unary sum
  without order constraints, a sum over many Bools) costs a re-solve per assignment with
  the same value.
- The enumeration of further optima encodes `objective == optimum` as one PB constraint;
  over a wide objective this can be slow or crash, which ends the run as `timeout` after
  the first optimum.
- A `dict` inside an output is walked as one and comes out as a JSON object
  (`invalid_output`): return lists.

## Example

The pilot fixture [tests/fixtures/model_paramita.py](../../tests/fixtures/model_paramita.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    # x and y each take a value in 0..n as a unary sum of Bools, with the order
    # constraint that a higher Bool is set only when the one below it is.
    xs = [Bool(f"x{i}") for i in range(n)]
    ys = [Bool(f"y{i}") for i in range(n)]
    order = [~xs[i + 1] | xs[i] for i in range(n - 1)] + [~ys[i + 1] | ys[i] for i in range(n - 1)]
    x = sum(xs)
    y = sum(ys)
    if not instance["optimize"]:
        return order + [x + y == n], {"x": x, "y": y}
    return order + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
```
