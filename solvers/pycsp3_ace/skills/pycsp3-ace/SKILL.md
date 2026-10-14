---
name: pycsp3-ace
description: Write a constraint model in PyCSP3 (Python) for the DCP-Bench pycsp3_ace integration, which compiles it to XCSP3 and solves it with the ACE solver. Use when a problem must be modelled with PyCSP3 and checked by the repository evaluator.
---

# PyCSP3 models for `pycsp3_ace`

A submission is one plain PyCSP3 script, `model.py`. The runner in the image
reads the instance, compiles the script, solves it with ACE 2.6 (bundled in
pycsp3), and reports the declared outputs. The model never calls `solve()`.

Versions in the image: Python 3.12.11, pycsp3 2.6.1 (ACE-2.6.jar inside the
wheel), lxml 6.1.3, OpenJDK 17 (Debian bookworm package). Sources are listed in
`sources.md`.

## The contract

- `from pycsp3 import *` gives the instance as `data`. Every instance field is
  present. Read a field as an attribute, `data.n`, or as an item, `data["n"]`.
  Use the item form for names with a leading underscore, such as `data._SHIP`.
  Lists are plain Python lists and may be ragged (`data.rows[i]` of different
  lengths). Metadata such as `name` or `note` is present and may be ignored.
- Each declared output is a module-level name equal to the output name. It is a
  `Var`, a `VarArray`, or a nested list of them (matrices). Integer and Boolean
  values are reported as integers, so use 0/1 for Booleans.
- Every declared output variable must occur in at least one constraint. ACE
  reports only the variables that a constraint mentions. An output that no
  constraint mentions is an error, not a free value. Add a constraint on it, for
  example `satisfy(z >= 0)`.
- Post constraints with `satisfy(...)`. Optionally post one `minimize(term)` or
  `maximize(term)`. Do not call `solve()`; the model raises an error if it does.
- Write one declaration per line. PyCSP3 takes a variable's name from the source
  line, so `x = Var(...)` and `y = Var(...)` on separate lines.
- No floats. Coefficients and bounds are integers.

Only `model.py` is copied into the container. Keep all helper code in that one
file.

## Example

```python
from pycsp3 import *

n = data.n
queens = VarArray(size=n, dom=range(n))
satisfy(
    AllDifferent(queens),
    AllDifferent([queens[i] + i for i in range(n)]),
    AllDifferent([queens[i] - i for i in range(n)]),
)
```

The declared output is `queens`, a list of `n` integers. The Python name must be the
output name, so the variable is named `queens` here, not `q`. Declared outputs that
are matrices use `VarArray(size=[rows, cols], dom=...)`, which gives a nested
list such as `grid[i][j]`.

## Objectives and enumeration

- Use at most one of `minimize(term)` and `maximize(term)`. A term is a
  variable or an expression, such as `Sum(...)` or `x + y`.
- For an optimisation the runner first finds the optimum with ACE's full search.
  It reports solutions only when ACE proved the optimum. An unproven optimum
  gives `timeout` with no solution. Do not rely on an incumbent.
- With an objective, enumeration returns the solutions at the optimum. Without
  one, it returns the first distinct assignments of the declared outputs, up to
  `solution_limit`.
- Auxiliary variables can repeat one output assignment with different values.
  The runner excludes each assignment already reported and runs another round.
  Declared outputs are what count, so do not try to deduplicate in the model.
- A satisfaction model that finds fewer solutions than the limit and has been
  fully searched reports `complete`. A model that is unsatisfiable reports
  `unsat`.

## Modelling notes

- `Var(range(lo, hi + 1))` declares an integer domain. A Boolean is
  `Var(range(2))`, reported as 0/1.
- Global constraints are functions of the same name: `AllDifferent`,
  `AllEqual`, `Increasing`, `Table`, `Cumulative`, `NoOverlap`, `Count`,
  `Element` through indexing, and so on.
- `Sum(terms)` computes a sum. Keep the coefficients as integers.
- Boolean connectives: `Or(...)`, `And(...)`, `Not(...)`, `Xor(...)`, `Iff(...)`
  take conditions, not Python `and` / `or`.
- Module-level Python code runs once in the child process. Keep instance-derived
  sizes in `data`, not in files.

## Checking a model

```sh
python -m evaluation.check examples/abbots.py --problem PROBLEM --solver pycsp3_ace
```

Read the `reason` and `detail` fields. `execution_error` with a Python traceback
in `detail` is a modelling error; the traceback is in the stderr of the result.
`no_solution` means the model has no solution on an instance. `invalid_output`
usually means a declared output name or shape is wrong.

## Known limits

- Non-identifier fields of the instance are reached only with `data["name"]`.
- Each solve starts a new Python and Java process. Runs take about one second
  of fixed overhead.
- The Java heap is 1200 MiB inside the 2048 MiB container limit. A model that
  needs more memory fails with `memory_limit`.
