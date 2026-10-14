---
name: docplex
description: Write instance-agnostic DOcplex (docplex.mp) models for the DCP-Bench docplex_cplex integration, covering the build(instance) contract, what the runner does with the model, the size limits of the CPLEX Community Edition, the logical and functional constraints docplex offers, the encodings of the constraints this benchmark's references use with what each costs, and the mistakes that make a submission fail.
---

# DOcplex models for `docplex_cplex`

Write one Python file that builds a `docplex.mp` model from instance data. The
runner solves it with CPLEX inside a container; you never solve, print, or
read values yourself.

Image: Python 3.12 with docplex 2.32.264 and the cplex 22.2.0.1 wheel, which is
the CPLEX 22.2 Community Edition. Available imports are `docplex` and the Python
standard library; NumPy is not installed. There is no network and no licence
file: the model runs under the Community Edition's limits, described below.

## The contract

```python
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.integer_var(0, n, name="x")
    y = model.integer_var(0, n, name="y")
    model.add_constraint(x + y >= n)
    model.minimize(x + y)
    return model, {"x": x, "y": y}
```

- `build(instance)` takes the instance as a plain dict parsed from JSON and
  returns `(model, outputs)`, where `model` is a `docplex.mp.model.Model`.
- `outputs` maps **exactly** the problem's declared output names to variables,
  linear expressions, integers, or nested lists of these. Extra or missing keys
  are rejected, and shapes must match the reference exactly: a 2-D output is a
  list of lists. `binary_var_matrix` and the other `*_var_matrix` / `*_var_dict`
  constructors return dicts keyed by tuples, so turn them into lists yourself,
  `[[x[i, j] for j in cols] for i in rows]`.
- **The model's objective says whether this is an optimization.** A model that
  never calls `minimize` or `maximize` (or gives it a constant) is a
  satisfaction problem; `model.has_objective()` is what the runner reads.
- Every declared output must be **integer valued**. Declare output variables
  with `integer_var` or `binary_var`; a continuous output is accepted only if
  it is within 1e-6 of an integer, and enumeration refuses it outright.
- A Boolean output of the reference is a `binary_var`; the runner returns 0/1,
  which the evaluator accepts for a Boolean.
- Prefer variables and linear expressions as outputs. The value of a functional
  expression such as `model.abs(e)` is read from the continuous variable docplex
  creates for it, so return `d` from `model.add(d == model.abs(e))` instead.
- Auxiliary variables need not appear in `outputs`, and may be continuous.

**Take every quantity from `instance`.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

Do not call `model.solve()`, read `solution_value`, `print()`, or read files.
The runner owns solving, optimality, enumeration and serialisation.

## What the runner does with it

- It sets `parameters.threads = 1`, `parameters.mip.tolerances.mipgap = 0` and
  `parameters.timelimit` to the remaining budget, over anything you set. The gap
  matters: CPLEX's default of 1e-4 reports "integer optimal, tolerance" for a
  solution that is not optimal, which the evaluator would reject as
  `suboptimal_solution`. Other parameters you set stay as you set them.
- It rounds every integer variable to the nearest integer (CPLEX returns them
  within `mip.tolerances.integrality` = 1e-5) and evaluates a declared linear
  expression over the rounded values.
- An optimum it did not prove within the time limit is a `timeout`, never a
  result. An "infeasible or unbounded" status is re-solved without dual
  presolve reductions to tell the two apart.
- For a second solution it pins the objective to the proven optimum and adds a
  no-good over the integer variables your outputs are built from: one linear
  constraint over binaries, and for each general integer two binaries with
  indicator constraints. No bound is needed for that.

## The Community Edition caps the model size

The cplex wheel is the Community Edition. Measured in this image, it refuses a
model with more than **1000 variables** or more than **1000 constraints**, and
indicator constraints count as constraints. A model over the limit fails at
solve time with `DOcplexLimitsExceeded` (CPLEX code 1016); the runner reports
it as `unsupported` naming the Community Edition, which the evaluator records
as `unsupported_capability`. That fails the pair, because every instance is
checked. So:

- Count before you write, for the largest instance in
  `dataset/<problem>/<problem>.json`, not only the example: `n * n * n` one-hot
  binaries for an `n`-by-`n` grid of values `1..n` is 729 at `n = 9`, 4096 at 16.
- Docplex's logical and functional helpers add variables and constraints of
  their own. Measured, with the variable on the left counted:

  | Posting | Adds variables | Adds constraints |
  | --- | --- | --- |
  | `model.add(a != b)` | 1 | 2 |
  | `model.add(d == model.abs(a - b))` | 5 | 4 |
  | `model.add(y == model.max(a, b))` | 4 | 6 |
  | `model.add_equivalence(c, a == b)` | 1 | 1 |
  | `model.add_indicator(c, a <= b)` | 1 | 1 |
  | `model.add_if_then(a >= 3, b == 0)` | 1 | 2 |

  When a problem posts one of these per pair of items, the pairs are what fill
  the budget; an assignment matrix is often smaller.
- Leave headroom for enumeration: a second solution adds 1 range for the
  pinned objective, 1 constraint for the no-good, and for each general-integer
  output variable up to 2 binaries and 2 indicators. Declaring an output as the
  expression `model.sum(v * b[i, v] for v in values)` over one-hot binaries
  makes the no-good a single linear constraint instead.
- **Never multiply two variables.** CPLEX rejects `x * y == 12` as a non-convex
  quadratic constraint. A product of a binary and a bounded integer has a
  linear encoding (below).
- If the smallest honest formulation of the largest instance does not fit, the
  pair cannot pass on this edition; record it as a blocker rather than
  shrinking the model into a wrong one.

## The API you need

| You want | You write |
| --- | --- |
| a variable | `model.integer_var(lb, ub, name="x")`, `model.binary_var()`, `model.continuous_var(lb, ub)`; `lb` defaults to 0 |
| many variables | `model.integer_var_list(n, lb, ub, name="x")` returns a list; `model.binary_var_matrix(rows, cols)` a dict keyed by `(i, j)` |
| a sum | `model.sum(...)`; `model.dot(variables, coefficients)` for a weighted sum |
| a constraint | `model.add_constraint(e <= f)` or `model.add(...)`; `model.add_constraints([...])` for many |
| the objective | `model.minimize(e)` or `model.maximize(e)` |
| `a != b` | `model.add(a != b)` |
| `d = |e|`, `max`, `min` | `model.add(d == model.abs(e))`, `model.max(a, b, 0)`, `model.min(a, b)`; they take expressions |
| `z = a and b`, `a or b` | `model.add(z == model.logical_and(a, b))`, `model.logical_or(a, b)`; binaries only |
| `c == 1 → constraint` | `model.add_indicator(c, x + y <= 3)`; `active_value=0` for `c == 0` |
| `c == 1 ↔ constraint` | `model.add_equivalence(c, a == b)` |
| constraint → constraint | `model.add_if_then(x >= 3, y == 0)` |

`model.infinity` is the unbounded bound: `model.integer_var(0, model.infinity)`.
Negative domains need an explicit `lb`.

What raises, measured in this image:

- `if x == 1:` or `bool(x <= y)` raises `TypeError: Cannot convert linear
  constraint to a boolean value`. Python control flow cannot branch on a
  decision; branch on data only.
- `x // 2` and `x % 2` raise `TypeError`; encode them as below.
- `x * y` over two variables is accepted by docplex and then refused by CPLEX
  as a non-convex quadratic constraint.

## Encoding the constraints the references use

Indicators need no big-M, so prefer them, or docplex's own `!=`, over a big-M.
Where you do use `M`, derive it from the instance bounds and keep it as small as
the data allows; with `integrality` at 1e-5 a loose big-M lets a "zero" binary
carry `M * 1e-5` through the constraint.

```python
# all-different over values 1..m: an assignment matrix, and x reads it back
pick = model.binary_var_matrix(range(n), range(1, m + 1))
for i in range(n):
    model.add(model.sum(pick[i, v] for v in range(1, m + 1)) == 1)
for v in range(1, m + 1):
    model.add(model.sum(pick[i, v] for i in range(n)) <= 1)
x = [model.sum(v * pick[i, v] for v in range(1, m + 1)) for i in range(n)]

# a != b, for a single pair
model.add(a != b)

# a disjunction of linear constraints: one indicator per branch, at least one on
branch = model.binary_var_list(len(parts))
for k, (left, right) in enumerate(parts):          # each branch is left <= right
    model.add_indicator(branch[k], left <= right)
model.add(model.sum(branch) >= 1)

# d = |a - b|
model.add(d == model.abs(a - b))

# reified equality: c == 1 exactly when a == b
model.add_equivalence(c, a == b)

# element: value == table[index], index a decision variable in 0..len(table)-1
choose = model.binary_var_list(len(table))
model.add(model.sum(choose) == 1)
model.add(index == model.sum(j * choose[j] for j in range(len(table))))
model.add(value == model.sum(table[j] * choose[j] for j in range(len(table))))

# counting: how many of the xs equal v, through the assignment binaries
model.add(count == model.sum(pick[i, v] for i in range(n)))

# product of a binary b and an integer a in lo..hi: p == b * a, linearly
model.add(p <= hi * b)
model.add(p >= lo * b)
model.add(p <= a - lo * (1 - b))
model.add(p >= a - hi * (1 - b))

# q = a // k and r = a % k for a constant k > 0 and a in 0..hi
q = model.integer_var(0, hi // k)
r = model.integer_var(0, k - 1)
model.add(a == k * q + r)
```

Problems whose references are already linear — assignment, covering, knapsack,
blending, facility location, scheduling with fixed charges — need none of this
and translate directly.

## Check your own model before submitting

```sh
python -m generation.brief PROBLEM
python -m evaluation.check MODEL.py --problem PROBLEM --solver docplex_cplex --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Read `reason` and `detail` on failure:

- `invalid_solution`: the reference rejects a solution your model allows. With
  a big-M encoding, suspect an `M` too small to be inactive when its indicator
  is off.
- `suboptimal_solution`: your objective, or its direction, is wrong.
- `invalid_output`: the declared outputs have the wrong keys, shapes, or types;
  a `*_var_matrix` dict returned as an output is the usual cause.
- `unsupported_capability` naming the Community Edition: the instance is too
  large under the limits above. Reformulate smaller if an honest smaller
  formulation exists; otherwise block the pair.
- `execution_timeout` on an optimization: CPLEX never proved the optimum,
  which a tighter formulation, a smaller `M`, or symmetry you remove from the
  formulation (never from the reference) may fix.
- `execution_error`: read `stderr` in the instance record for the traceback;
  the API mistakes listed above are the usual cause.

Never change the reference, the dataset, or the evaluator to make a submission
pass.
