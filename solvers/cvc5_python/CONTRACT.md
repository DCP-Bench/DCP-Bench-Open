# cvc5_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how cvc5 (Python)
expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`, `flatten` and
`mapped` from [runner/runtime.py](../../runner/runtime.py) and has its own `build`, solve
and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `cvc5.pythonic` (and `cvc5` itself) and the
standard library. No other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[constraints, dict] | tuple[constraints, dict, tuple[str, cvc5.pythonic.ArithRef]]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(constraints, outputs)` for a satisfaction problem, or a 3-tuple
`(constraints, outputs, (direction, objective))` for an optimisation problem, where
direction is `"minimize"` or `"maximize"`. `constraints` is a `cvc5.pythonic.Solver` (its
assertions are taken), a list or tuple of Boolean expressions, or a single one. Anything
the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to an Int- or
Bool-sorted pythonic expression, a Python `int` or `bool`, or a nested list/tuple of these
with the declared shape. After the solver finds a model, each leaf is read with
`model.eval(e, model_completion=True)`: a Boolean comes back as `true`/`false`, an integer
as its `as_long()`. Any other sort (a `Real`, a string) raises and is reported as
`execution_error`. Python constants pass through unchanged.

## Objective

The third element of the return value: `("minimize", expr)` or `("maximize", expr)`, with
`expr` an Int-sorted pythonic expression or a Python `int`. Only the third element declares
the objective. Solutions are only reported at the proven optimum.

## Solving

- Time: `execution_timeout` is measured from the start of `solve`, including `build`. Each
  solver check gets **all the time left** (cvc5 option `tlimit-per`, in ms, set before each
  check); the runner does not split the budget across tightening steps. A later step can
  therefore run out, which gives `timeout`.
- Optimisation (no solver optimiser exists): one incremental `cvc5.pythonic.Solver` holds
  the constraints. Each `sat` result records the objective value `best` and asserts
  `objective < best` (minimise) or `objective > best` (maximise). `unsat` after at least
  one `sat` proves `best` optimal. `unsat` at the first check is `unsat`. `unknown` (below)
  or running out of time before the proof is `timeout`, and no solution is emitted.
- Enumeration after the proof: a fresh solver over the constraints plus `objective == best`.
  Each model is emitted, then `Or(leaf != value)` over every declared output leaf that is
  not a Python constant is asserted, and the solver checks again. `unsat` gives `complete`
  after at least one solution (`unsat` if there was none); `limit` once `solution_limit` is
  reached.
- Satisfaction: the same enumeration loop, without the objective.
- `unknown`: cvc5 reason `TIMEOUT` maps to `timeout`. Any other reason (for example
  `INCOMPLETE`, which cvc5 gives for nonlinear arithmetic it cannot decide) maps to `error`
  with `cvc5 returned unknown: <reason>` as the detail.
- Exceptions raised while building or solving map to `error` with the exception's own
  message as the detail.
- Backstop: a `SIGALRM` at `execution_timeout + 5` s becomes `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/cvc5_python:v1`, built `FROM python:3.12.11-slim-bookworm` (pinned by
digest, as in `solvers/z3_python`). Python 3.12.11 at `/usr/local/bin/python`, the `cvc5`
wheel 1.4.2 from PyPI (`cvc5.__version__` is `1.4.2`), and nothing else besides pip. The
shared `runner/requirements.txt` stack is not installed, so NumPy is not available. The JSON
library is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp`, user 65534, the
submission and `request.json` under `/input`. The image's entrypoint is the runner
(`python /opt/runner/run.py`).

## Traps

- Use `cvc5.pythonic`, not the native `cvc5` API: the runner and the pythonic `Solver` are
  the only interface it supports.
- `set("timeout", ...)` is rejected (`unrecognized option: timeout.`). Use `tlimit-per`.
- The global `tlimit` option was not usable in this image: with it set, `check()` did not
  return within the budget in testing. Only `tlimit-per` is used.
- `Sum([...])` over Boolean expressions raises `TypeError: unsupported operand type(s) for
  +: 'BoolRef' and 'BoolRef'`. Wrap each Boolean in `If(b, 1, 0)`.
- Inside arithmetic, a Boolean mixed with an Int is silently taken as 0/1 (`x + b` becomes
  `x + If(b, 1, 0)`); a Boolean compared with an Int is also not an error. Write explicit
  `If` where the meaning matters.
- `Distinct` over Python `int`s (no pythonic expression in the list) raises
  `SMTException: At least one of the arguments must be an SMT expression`.
- A string in an arithmetic position raises `RuntimeError: invalid argument 'abc' for 's',
  expected an integer`. Strings from the instance must be turned into numbers before use.
- Integers are unbounded: constrain every output and every auxiliary variable to the domain
  the problem implies. An output no constraint mentions is enumerated over its whole
  unbounded domain, so enumeration does not stop at `solution_limit` in a useful way.
- Nonlinear integer arithmetic (a product of two unknowns, for example `a * b == 7000021`
  or `c * c * d == 2 * 10**12 + 1`) returned `unknown` after the time limit in testing. It
  is reported as `timeout` or, when cvc5 gives another reason, `error`. Products with a
  constant factor are linear and were solved quickly.
- Quantifiers: not tested by this integration. Treat as unsupported until a readiness
  case covers them.

## Example

The pilot fixture [tests/fixtures/model_cvc5.py](../../tests/fixtures/model_cvc5.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    x, y = cz.Ints("x y")
    # cvc5 integers are unbounded, so the bounds the reference declares must be added.
    bounds = [x >= 0, x <= n, y >= 0, y <= n]
    if instance["optimize"]:
        return bounds + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
    return bounds + [x + y == n], {"x": x, "y": y}
```
