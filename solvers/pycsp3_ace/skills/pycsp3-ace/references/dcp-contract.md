# DCP-Bench submission contract for pycsp3_ace

Source: `solvers/pycsp3_ace/run.py` (the runner in the image), `evaluation/check.py` (the
verdicts). Everything below was run in the image unless marked "code".

## The file

- One file, `model.py`. Only that file is copied into the container, so helpers go in it too.
- `from pycsp3 import *` gives `data`, the instance.
- No `solve()`. The runner calls the solver and raises if the model does.

## Instance data

`data` has every field of the instance JSON. A field is an attribute or an item:

- `data.n` and `data["n"]` are the same.
- `data._SHIP` and `data["_SHIP"]` both work (verified).
- Lists are plain Python lists. Ragged lists keep their lengths (`data.rows[i]`).
- Metadata fields such as `name` and `note` are present. A model that ignores them is unaffected.

Instance sizes vary per instance. Take sizes from `data` (`VarArray(size=data.n, ...)`), never
from a number typed into the file. The `example` instance and the `json:N` instances are both
checked.

## Declared outputs

- Each output in `python -m generation.brief PROBLEM` is a module-level name in the model,
  bound to a `Var`, a `VarArray`, or a nested list. The name must match exactly.
- Shapes in the brief such as `[10]int` or `[5]bool` describe one instance. The size comes
  from `data`.
- Booleans are reported as 0/1, so use `dom={0, 1}`.
- Every output variable must appear in a constraint. ACE reports only constrained variables.
- Values follow the convention in the problem description. The queens description says the
  column positions run from 1 to n. A 0-based model (`dom=range(n)`) fails with
  `invalid_solution`: "Declared outputs cannot extend to a reference solution".

## Objective

`brief` gives the objective direction (`satisfaction`, `maximize`, `minimize`).

- Satisfaction: no `minimize` or `maximize` call.
- Optimisation: exactly one call, in the matching direction. Minimising a maximisation problem
  fails with `suboptimal_solution` (verified on knapsack).

## Complete models

Queens (`csplib_054_n_queens`, satisfaction; checked on the 6 listed instances in the
verification run, see SKILL.md):

```python
from pycsp3 import *

n = data.n
# queens[i] is the column of the queen in row i, counted from 1
queens = VarArray(size=n, dom=range(1, n + 1))
satisfy(
    # no two queens share a column
    AllDifferent(queens),
    # no two queens share a diagonal
    AllDifferent([queens[i] + i for i in range(n)]),
    AllDifferent([queens[i] - i for i in range(n)]),
)
```

Knapsack (`knapsack`, maximisation; accepted on the 5 instances):

```python
from pycsp3 import *

values = data.values
weights = data.weights
capacity = data.capacity
x = VarArray(size=len(values), dom={0, 1})
satisfy(
    # the chosen items must fit in the backpack
    Sum(weights[i] * x[i] for i in range(len(values))) <= capacity,
)
# maximise the total value of the chosen items
maximize(Sum(values[i] * x[i] for i in range(len(values))))
```

## Running the checks

```
python -m evaluation.check model.py --problem csplib_054_n_queens --solver pycsp3_ace --instance-count 6
python -m evaluation.check model.py --problem knapsack --solver pycsp3_ace --instance-count 5
```

The result is JSON: `accepted`, `reason`, `detail`, and per instance `instances[]` with `id`,
`accepted`, `reason`, `detail`, `solutions_checked` and `optimum`. Read `reason` and `detail`
first. `detail` for `execution_error` holds the Python exception, e.g.
`NameError: the model does not define the declared output 'x'`, or pycsp3's own message, e.g.
`pycsp3: The identifier z is used twice. This is not possible`.

Check with few solutions first: `--solution-limit 2` (the default is 1). Campaign runs found that a
second solution exposes readings that only hold for the first one, such as a loose bound in the
declared output (`invalid_solution`: "Declared outputs cannot extend to a reference solution").

Campaign runs use the same checker:

```
python -m generation.manage evaluate --attempt ATTEMPT_DIR --model model.py
```

This is code only, not run here. It copies the candidate into the attempt folder and writes
`evaluation.json`, and it refuses an attempt that was already evaluated. Use it only for an
attempt the campaign created.
A background run may lose its stdout. Read the attempt's `evaluation.json` before running
`evaluate` again, since a second run on the same attempt is refused.

## Reasons seen in the verification runs

| reason | cause (verified unless marked code) |
|---|---|
| `accepted` | all checked instances agree with the reference |
| `execution_error` | exception in the model; `detail` has the message. Misnamed output: `NameError`. Missing field: `AttributeError: 'Instance' object has no attribute ...`. A reserved identifier: `Fatal Error: The id E is a keyword`. ACE out of heap: `java.lang.OutOfMemoryError`. Each is shown by the runner, not as a timeout |
| `no_solution` | the model is unsatisfiable on the instance (runner status `unsat`) |
| `invalid_solution` | a reported solution breaks the reference's constraints. Over-relaxed capacity in knapsack gave it. Wrong value range gives it too |
| `suboptimal_solution` | "Declared outputs cannot achieve the reference optimum". Wrong objective direction |
| `invalid_output` | code: the runner returned fewer distinct solutions than requested without saying the search was exhausted |
| `execution_timeout`, `reference_timeout`, `memory_limit` | inconclusive; see below |
| `unsupported_capability`, `compilation_error` | code: runner status `unsupported` or `compilation_error` |

Verified: an output element that no constraint mentions is reported as
`execution_error` with `ValueError: a declared output has no determined value in the solution`
(a satisfaction model that constrains only `x[0]` and `x[1]` of a 5-element output). A whole
output with no constraint raises `ValueError: declared output 'z' has a variable that no
constraint mentions, ...`. Both are fixed by constraining every element.

## Timeouts and skipped instances

Code in `evaluation/check.py`: when the checker runs with `tolerate_inconclusive`, an
instance that fails with `execution_timeout`, `reference_timeout` or `memory_limit` is recorded
with `skipped: true` and its id goes into `skipped_instances`. It does not count as failed.
Without that flag the first such failure rejects the model. The default CLI flag is off. The
Essence' campaign profile sets it on. Check `instances_checked` before reporting a pass: a
model is accepted only when at least one instance was verified.

The runner's own time limit: `execution_timeout` in the request, minus the time already used on
earlier rounds. An optimisation whose optimum ACE does not prove by then returns `timeout`
with the detail `Candidate optimum was not proven` and no solution. That becomes
`execution_timeout`.
