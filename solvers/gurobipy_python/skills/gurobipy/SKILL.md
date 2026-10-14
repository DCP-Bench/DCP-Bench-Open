---
name: gurobipy
description: Write instance-agnostic gurobipy models for the DCP-Bench gurobipy_python integration, covering the build(instance) contract, what the runner does with the model, the size limits of the licence bundled with the gurobipy wheel, the general constraints Gurobi 13 offers, the encodings of the constraints this benchmark's references use, and the mistakes that make a submission fail.
---

# gurobipy models for `gurobipy_python`

Write one Python file that builds a Gurobi model from instance data. The runner
solves it inside a container; you never solve, print, or read values yourself.

Image: Python 3.12 with gurobipy 13.0.3 (the Gurobi Optimizer 13.0.3 it ships),
NumPy 2.4.6 and SciPy 1.18.1. Available imports are `gurobipy`, `numpy`, `scipy`
and the Python standard library. There is no network and no licence file: the
model runs under the licence bundled in the wheel, described below.

## The contract

```python
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    model = gp.Model()
    x = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="x")
    y = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="y")
    model.addConstr(x + y >= n)
    model.setObjective(x + y, GRB.MINIMIZE)
    return model, {"x": x, "y": y}
```

- `build(instance)` takes the instance as a plain dict parsed from JSON and
  returns `(model, outputs)`, where `model` is a `gurobipy.Model`.
- `outputs` maps **exactly** the problem's declared output names to variables,
  linear expressions, integers, or nested lists of these. Extra or missing keys
  are rejected, and shapes must match the reference exactly: a 2-D output is a
  list of lists. A `tupledict` from `addVars` is a dict keyed by tuples, so turn
  it into lists yourself, `[[x[i, j] for j in range(m)] for i in range(n)]`. An
  `MVar` is accepted and read element by element; an `MLinExpr` is not, so build
  expression outputs as lists of `LinExpr`.
- **The model's objective says whether this is an optimization.** A model that
  never calls `setObjective` (or sets a constant) is a satisfaction problem. The
  direction is the `sense` argument, `GRB.MINIMIZE` or `GRB.MAXIMIZE`. One
  objective only: multi-objective models are reported `unsupported`.
- Every declared output must be **integer valued**. Declare output variables
  `GRB.INTEGER` or `GRB.BINARY`; a continuous output is accepted only if it is
  within 1e-6 of an integer, and enumeration refuses it outright.
- A Boolean output of the reference is a `GRB.BINARY` variable; the runner
  returns 0/1, which the evaluator accepts for a Boolean.
- Auxiliary variables need not appear in `outputs`, and may be continuous.

**Take every quantity from `instance`.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

Do not call `model.optimize()`, read `.X`, `print()`, or read files. The runner
owns solving, optimality, enumeration and serialisation.

## What the runner does with it

- It sets `OutputFlag=0`, `Threads=1`, `MIPGap=0` and `TimeLimit` to the
  remaining budget, over anything you set. `MIPGap=0` matters: Gurobi's default
  gap of 1e-4 reports OPTIMAL for a solution that is not optimal, which the
  evaluator would reject as `suboptimal_solution`. Other parameters you set
  (`MIPFocus`, `Presolve`, `Cuts`, ...) stay as you set them.
- It rounds every integer variable to the nearest integer (Gurobi returns them
  within `IntFeasTol` = 1e-5) and evaluates a declared expression over the
  rounded values.
- An optimum it did not prove within the time limit is a `timeout`, never a
  result. `INF_OR_UNBD` is re-solved without dual reductions to tell the two
  apart.
- For a second solution it pins the objective to the proven optimum and adds a
  no-good over the integer variables your outputs are built from: one linear
  constraint over binaries, and for each general integer two binaries with
  indicator constraints. No bound is needed for that.

## The licence caps the model size

The licence in the gurobipy wheel is size-limited. Measured in this image:

| What the model contains | Limit |
| --- | --- |
| linear and general constraints only | 2000 variables, and 2000 constraints counting linear and general (`abs_`, `max_`, indicator, ...) together |
| any quadratic or nonlinear term (`x * y`, `addGenConstrNL`, `addGenConstrPow`) | 200 variables |

A model over the limit fails at solve time and the runner reports
`unsupported` naming the licence, which the evaluator records as
`unsupported_capability`. That is a property of the instance size, not of your
model's correctness, but it fails the pair all the same, because every instance
is checked. So:

- Count before you write: `n * n * n` one-hot binaries for an `n`-by-`n` grid of
  values `1..n` is 729 at `n = 9` and 4096 at `n = 16`. Check the largest
  instance in `dataset/<problem>/<problem>.json`, not only the example.
- **Never multiply two variables.** It drops the variable limit to 200. A
  product of a binary and a bounded integer has a linear encoding (below);
  use it.
- Leave headroom for enumeration: a second solution adds 2 constraints for the
  pinned objective, 1 for the no-good, and for each general-integer output
  variable up to 2 binaries and 2 indicator constraints. Declaring an output as
  the expression `gp.quicksum(v * b[i][v] for v in values)` over one-hot binaries
  makes the no-good a single linear constraint instead.
- If the smallest honest formulation of the largest instance does not fit,
  the pair cannot pass on this licence; record it as a blocker rather than
  shrinking the model into a wrong one.

## The API you need

| You want | You write |
| --- | --- |
| a variable | `model.addVar(lb=0, ub=u, vtype=GRB.INTEGER, name="x")`; `lb` defaults to 0, not minus infinity |
| many variables | `x = model.addVars(n, m, lb=0, ub=u, vtype=GRB.INTEGER, name="x")`, indexed `x[i, j]` |
| a matrix variable | `v = model.addMVar((n, m), vtype=GRB.BINARY)`, `v.sum(axis=1)`, `A @ v` |
| a sum | `gp.quicksum(...)`, or `x.sum(i, "*")` on a `tupledict` |
| a constraint | `model.addConstr(expr <= other)`; also `>=`, `==` |
| the objective | `model.setObjective(expr, GRB.MAXIMIZE)` |
| `y = |x|` | `model.addConstr(y == gp.abs_(x))`, where `x` is a **variable**: `gp.abs_(a - b)` raises `TypeError` |
| `y = max(...)` / `min(...)` | `model.addConstr(y == gp.max_([a, b, c], constant=0))`, `gp.min_(a, b)`; variables only |
| `z = a and b`, `z = a or b` | `model.addConstr(z == gp.and_(a, b))`, `gp.or_(a, b)`; binaries only |
| `c == 1 → constraint` | `model.addConstr((c == 1) >> (x + y <= 3))`; `c` binary, the right side linear |

Negative domains need an explicit `lb`: `model.addVar(lb=-5, ub=5, vtype=GRB.INTEGER)`.
`lb=-GRB.INFINITY` makes a free variable.

What raises, measured in this image:

- `model.addConstr(x != y)` raises `GurobiError: Inequality constraints not supported`.
- `x // 2` and `x % 2` raise `TypeError`; `x / 2` is fine and means `0.5 * x`.
- `if x == 1:` or `bool(x <= y)` raises `GurobiError: Constraint has no bool
  value`. Python control flow cannot branch on a decision; branch on data only.
- `gp.abs_`, `gp.max_` and `gp.min_` take variables, not expressions: introduce
  an auxiliary variable equal to the expression first.
- A variable created in one `gp.Model` cannot be used in another.

## Encoding the constraints the references use

Indicator constraints need no big-M, so reach for them before a big-M. Where you
do use `M`, derive it from the instance bounds and keep it as small as the data
allows; a loose big-M slows the search and, with `IntFeasTol` at 1e-5, lets a
"zero" binary carry `M * 1e-5` through the constraint.

```python
# all-different over values 1..m: an assignment matrix, and x reads it back
pick = model.addVars(n, range(1, m + 1), vtype=GRB.BINARY)
for i in range(n):
    model.addConstr(pick.sum(i, "*") == 1)
    model.addConstr(x[i] == gp.quicksum(v * pick[i, v] for v in range(1, m + 1)))
for v in range(1, m + 1):
    model.addConstr(pick.sum("*", v) <= 1)

# a != b: one of the two strict inequalities holds
before = model.addVar(vtype=GRB.BINARY)
model.addConstr((before == 1) >> (a <= b - 1))
model.addConstr((before == 0) >> (a >= b + 1))

# a disjunction of linear constraints: one indicator per branch, at least one on
branch = model.addVars(len(parts), vtype=GRB.BINARY)
for k, (left, right) in enumerate(parts):           # each branch is left <= right
    model.addConstr((branch[k] == 1) >> (left <= right))
model.addConstr(branch.sum() >= 1)

# d = |a - b|: the argument must be a variable
diff = model.addVar(lb=-u, ub=u, vtype=GRB.INTEGER)
model.addConstr(diff == a - b)
model.addConstr(d == gp.abs_(diff))

# reified equality: c == 1 exactly when a == b; when c == 0, a < b or a > b
lt = model.addVar(vtype=GRB.BINARY)
gt = model.addVar(vtype=GRB.BINARY)
model.addConstr(lt + gt == 1 - c)
model.addConstr((c == 1) >> (a == b))
model.addConstr((lt == 1) >> (a <= b - 1))
model.addConstr((gt == 1) >> (a >= b + 1))

# element: value == table[index], index a decision variable in 0..len(table)-1
choose = model.addVars(len(table), vtype=GRB.BINARY)
model.addConstr(choose.sum() == 1)
model.addConstr(index == gp.quicksum(j * choose[j] for j in range(len(table))))
model.addConstr(value == gp.quicksum(table[j] * choose[j] for j in range(len(table))))

# counting: how many of the xs equal v, through the same assignment binaries
model.addConstr(count == pick.sum("*", v))

# product of a binary b and an integer a in lo..hi: p == b * a, linearly
model.addConstr(p <= hi * b)
model.addConstr(p >= lo * b)
model.addConstr(p <= a - lo * (1 - b))
model.addConstr(p >= a - hi * (1 - b))

# q = a // k and r = a % k for a constant k > 0 and a in 0..hi
q = model.addVar(lb=0, ub=hi // k, vtype=GRB.INTEGER)
r = model.addVar(lb=0, ub=k - 1, vtype=GRB.INTEGER)
model.addConstr(a == k * q + r)
```

Problems whose references are already linear — assignment, covering, knapsack,
blending, facility location, scheduling with fixed charges — need none of this
and translate directly.

## Check your own model before submitting

```sh
python -m generation.brief PROBLEM
python -m evaluation.check MODEL.py --problem PROBLEM --solver gurobipy_python --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Read `reason` and `detail` on failure:

- `invalid_solution`: the reference rejects a solution your model allows. With
  a big-M encoding, suspect an `M` too small to be inactive when its indicator
  is off.
- `suboptimal_solution`: your objective, or its direction, is wrong.
- `invalid_output`: the declared outputs have the wrong keys, shapes, or types;
  a `tupledict` returned as an output is the usual cause.
- `unsupported_capability` naming the size-limited licence: the instance is
  too large under the limits above. Reformulate smaller if an honest smaller
  formulation exists; otherwise block the pair.
- `execution_timeout` on an optimization: Gurobi never proved the optimum,
  which a tighter formulation, a smaller `M`, or symmetry you remove from the
  formulation (never from the reference) may fix.
- `execution_error`: read `stderr` in the instance record for the traceback;
  the API mistakes listed above are the usual cause.

Never change the reference, the dataset, or the evaluator to make a submission
pass.
