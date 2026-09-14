---
name: pulp-cbc
description: Write instance-agnostic PuLP models for the DCP-Bench pulp_cbc integration, covering the build(instance) contract, the linear-only API of PuLP 3.3.2 with CBC, the MIP encodings of the constraints this benchmark's references use, and the mistakes that make a submission fail.
---

# PuLP models for `pulp_cbc`

Write one Python file that builds a mixed-integer linear program from instance
data. The runner solves it inside a container; you never solve, print, or read
values yourself.

Image: PuLP 3.3.2 with the CBC binary it ships. Available imports are `pulp` and
the Python standard library.

## The contract

```python
import pulp


def build(instance):
    n = instance["n"]
    problem = pulp.LpProblem("example", pulp.LpMinimize)
    x = pulp.LpVariable("x", 0, n, cat="Integer")
    y = pulp.LpVariable("y", 0, n, cat="Integer")
    problem += x + y >= n          # a constraint: the expression has a relation
    problem += x + y               # the objective: a bare expression
    return problem, {"x": x, "y": y}
```

- `build(instance)` takes the instance as a plain dict parsed from JSON and
  returns `(problem, outputs)`.
- `outputs` maps **exactly** the problem's declared output names to variables,
  linear expressions, integers, or nested lists of these. Extra or missing keys
  are rejected, and shapes must match the reference exactly.
- **The problem itself says whether this is an optimization.** PuLP leaves
  `problem.objective` as `None` until a bare expression is added, so a model
  that adds none is a satisfaction problem. The direction is the `sense` given
  to `LpProblem`. Adding a second bare expression *overwrites* the objective and
  warns; build the objective as one expression.
- Every declared output must be **integer valued**. CBC returns floats, and the
  runner rounds one within 1e-6 of an integer and rejects anything else, so
  declare output variables `Integer` or `Binary` rather than leaving them
  continuous.
- **Bound every declared output variable.** `pulp.LpVariable("x", 0, n, cat="Integer")`
  — an unbounded integer output makes enumeration impossible and the runner
  reports `unsupported` rather than guessing a bound.
- Auxiliary variables need not appear in `outputs`, and may be continuous.

**Take every quantity from `instance`.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

Do not call `problem.solve()`, `pulp.value()`, `print()`, or read files. The
runner owns solving, optimality, enumeration and serialisation.

## What the runner does with it

CBC reports `status == Optimal` even when it stopped on the time limit, so the
runner judges every solve on `sol_status` instead: an optimum it did not prove
is a `timeout`, never a result. For a second solution it pins the objective to
the proven optimum and adds a no-good cut over the integer variables your
outputs are built from — which is why those variables must be integral and
bounded.

## Linear only: PuLP 3.3.2 refuses everything else

| You want | You write |
| --- | --- |
| a variable | `pulp.LpVariable(name, low, up, cat="Integer" / "Binary" / "Continuous")` |
| many variables | `pulp.LpVariable.dicts("x", keys, low, up, cat=...)`, keys may be nested ranges |
| a sum | `pulp.lpSum(...)` (plain `sum` works but is slower) |
| a constraint | `problem += expression <= other` (also `>=`, `==`) |
| the objective | `problem += expression`, direction from `LpProblem(name, pulp.LpMaximize)` |

`x * y` raises `TypeError: Non-constant expressions cannot be multiplied`, and
`abs(x)` raises `TypeError`. There is no `!=`, no `if`, no element constraint and
no all-different: every one of them is encoded below.

## Encoding the constraints the references use

`M` below is any constant at least as large as the slack the constraint can
need; derive it from the instance bounds rather than guessing a round number,
and keep it as small as the data allows — a loose big-M is what makes CBC crawl.

```python
# all-different over values 1..m: an assignment matrix, and x reads it back
pick = pulp.LpVariable.dicts("pick", (range(n), range(1, m + 1)), cat="Binary")
for i in range(n):
    problem += pulp.lpSum(pick[i][v] for v in range(1, m + 1)) == 1
    problem += x[i] == pulp.lpSum(v * pick[i][v] for v in range(1, m + 1))
for v in range(1, m + 1):
    problem += pulp.lpSum(pick[i][v] for i in range(n)) <= 1

# a != b, with both in 0..u: one of the two strict inequalities holds
before = pulp.LpVariable("before", cat="Binary")
problem += a <= b - 1 + (u + 1) * (1 - before)
problem += a >= b + 1 - (u + 1) * before

# a disjunction of linear constraints: one indicator per branch, at least one on
branch = [pulp.LpVariable(f"branch_{k}", cat="Binary") for k in range(len(parts))]
for k, (left, right) in enumerate(parts):          # each branch is left <= right
    problem += left <= right + M * (1 - branch[k])
problem += pulp.lpSum(branch) >= 1

# d = |a - b| under minimization: the two bounds suffice, the objective pulls d down
problem += d >= a - b
problem += d >= b - a

# z = a and b, for binaries
problem += z <= a
problem += z <= b
problem += z >= a + b - 1

# element: value is table[index], index a decision variable
problem += pulp.lpSum(choose[j] for j in range(len(table))) == 1
problem += index == pulp.lpSum(j * choose[j] for j in range(len(table)))
problem += value == pulp.lpSum(table[j] * choose[j] for j in range(len(table)))

# counting: how many of the xs equal v, through the same indicator binaries
problem += count == pulp.lpSum(pick[i][v] for i in range(n))
```

An implication `c == 1 → left <= right` is `left <= right + M * (1 - c)`; a
reified equality needs both directions, one indicator each.

Problems whose references are already linear — assignment, covering, knapsack,
blending, facility location, scheduling with fixed charges — need none of this
and translate directly.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.py --problem PROBLEM --solver pulp_cbc --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Read `reason` and `detail` on failure: `invalid_solution` means the reference
rejects a solution your model allows — with a big-M encoding, suspect an `M` too
small to be inactive when its indicator is off; `suboptimal_solution` means your
objective is wrong; `invalid_output` means the declared outputs have the wrong
keys, shapes, or types; and `execution_timeout` on an optimization means CBC
never proved the optimum, which a tighter formulation or a smaller `M` may fix.

Never change the reference, the dataset, or the evaluator to make a submission
pass.
