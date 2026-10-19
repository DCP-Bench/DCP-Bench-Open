---
name: hermax
description: hermax is a Python MaxSAT modelling library (hermax.model.Model over PySAT) with Boolean and integer variables, hard constraints, weighted soft clauses for minimise and maximise, and solution enumeration. Use when writing, debugging or explaining hermax models or MaxSAT-style optimisation in Python, or when the user has chosen hermax.
license: Apache-2.0
compatibility: Requires Python 3 with pip (tested with Python 3.12.11 and hermax 1.2.5, which installs python-sat); no licence key or account needed
metadata:
  domain: constraint-programming
  solver: hermax
  paradigm: maxsat
---

# hermax (Python, MaxSAT)

hermax models are built with `hermax.model.Model`. Hard constraints are posted with
`m &= constraint`. An objective is a set of **weighted soft clauses**: `solve` minimises
the total weight of the soft clauses it breaks. The one idea to keep: a soft clause
`m.obj[w] += literal` pays `w` when the literal is **false**.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [All optimal solutions](#all-optimal-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: [satisfy](assets/satisfy/README.md), [all-solutions](assets/all-solutions/README.md), [all-optimal](assets/all-optimal/README.md), [maximise](assets/maximise/README.md), [minimise](assets/minimise/README.md), [infeasible](assets/infeasible/README.md), [scheduling](assets/scheduling/README.md)
- API details: [references/model-api.md](references/model-api.md)

## Install

```bash
pip install hermax
python3 -c "import hermax.model; print('hermax ok')"
```

Apache-2.0, no key. Details: [Quick start](https://hermax.readthedocs.io/en/latest/quickstart.html)

## Quick start

```python
from hermax.model import Model

COST = [4, 1, 3, 2]           # price of each item
m = Model()
pick = m.bool_vector("pick", len(COST))
m &= (sum(pick[i] for i in range(len(COST))) == 2)   # choose exactly two
for i, c in enumerate(COST):
    m.obj[c] += ~pick[i]      # pay c when item i is picked

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
print("picked:", [i for i in range(len(COST)) if r[pick[i]]])
print("total cost:", r.cost)  # picked: [1, 3], total cost: 3
```

## Modelling

Full list: [API reference](https://hermax.readthedocs.io/en/latest/api.html) ·
[Modelling guide](https://hermax.readthedocs.io/en/latest/modeling.html) ·
[all signatures](references/model-api.md)

| Need | API |
|---|---|
| one Boolean / vector / matrix | [`m.bool`, `m.bool_vector`, `m.bool_matrix`](https://hermax.readthedocs.io/en/latest/api.html) |
| integer / vector / matrix | [`m.int`, `m.int_vector`, `m.int_matrix`](https://hermax.readthedocs.io/en/latest/api.html) |
| at most / exactly one | [`bv.at_most_one()`, `bv.exactly_one()`](https://hermax.readthedocs.io/en/latest/api.html) |
| all different | [`iv.all_different()`](https://hermax.readthedocs.io/en/latest/api.html) |
| ordering | [`iv.increasing()`, `iv.lexicographic_less_than(other)`](https://hermax.readthedocs.io/en/latest/api.html) |
| linear constraint | `m &= (sum(w[j] * x[j] for j in range(n)) <= cap)` |
| row / column of a matrix | [`x.row(i)`, `x.col(j)`](https://hermax.readthedocs.io/en/latest/api.html) |
| min / max / sum of variables | [`m.min`, `m.max`, `m.sum_var`](https://hermax.readthedocs.io/en/latest/api.html) |
| integer quotient | [`m.floor_div(x, k)`](https://hermax.readthedocs.io/en/latest/api.html) (not `x // k`) |
| scheduling resource | [`m.cumulative(starts, durations, demands, capacity)`](https://hermax.readthedocs.io/en/latest/api.html), adds its own constraint |
| no two tasks overlap on one machine | `m.cumulative(starts, durations, [1] * len(starts), 1)`, one call per machine |
| all different over expressions | auxiliary `IntVar`s, see [Derived values](#derived-values) |
| equality between two sums | `m &= (sum(...) == sum(...))`, both sides may be sums |
| minimise / maximise | [`m.obj[w] += literal`](https://hermax.readthedocs.io/en/latest/modeling.html), see below |
| reading values | `r[var]`; `r[vector]` is a list, `r[matrix]` a list of row lists of the same shape |

`cumulative` is not wrapped in `m &=`: it posts its constraint directly.

### Derived values

`all_different`, `increasing` and the other container constraints apply to variables, not
to expressions. Give each expression its own `IntVar` and constrain that:

```python
q = m.int_vector("q", n, 0, n - 1)                  # queen column per row
d1 = m.int_vector("d1", n, 0, 2 * n - 2)            # diagonal id q[i] + i
d2 = m.int_vector("d2", n, 0, 2 * n - 2)            # anti-diagonal id q[i] - i + (n - 1)
m &= q.all_different()
for i in range(n):
    m &= (d1[i] == q[i] + i)
    m &= (d2[i] == q[i] - i + (n - 1))
m &= d1.all_different()
m &= d2.all_different()
```

The pattern is checked by the n-queens enumeration in [All solutions](#all-solutions).
No-overlap on a machine is the `cumulative` call in the table above, and
[assets/scheduling](assets/scheduling/README.md) shows `cumulative` with demands other than 1.

### The objective is soft clauses

| Direction | Write | Cost paid |
|---|---|---|
| minimise a total | `m.obj[c] += ~x` | `c` when `x` is true (the thing is used) |
| maximise a total | `m.obj[v] += x` | `v` when `x` is false (the thing is left out) |
| any integer expression | `m.obj += expr` | its value, e.g. `m.obj += makespan` |

For a maximisation the solver minimises the **forgone** weight, so the objective is
`sum(all weights) - r.cost`. Keep the objective as soft clauses where you can: a weighted
sum tied to an integer variable is far slower (see [Common issues](#common-issues)).

**Sign check:** minimise uses `~x` (pays when `x` is chosen), maximise uses plain `x`
(pays when `x` is left out). Copying `~x` from the minimise row into a maximisation makes
the solver minimise the value and return the worst selection. Example: maximum-weight independent set,
[assets/maximise](assets/maximise/README.md), uses `m.obj[w] += pick[i]`.

## Solving

Status values: [Quick start](https://hermax.readthedocs.io/en/latest/quickstart.html) ·
Portfolio and time limits: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html)

| Status | Meaning |
|---|---|
| `sat` | satisfiable (the model has no soft clauses) |
| `optimum` | proven optimal (soft clauses present) |
| `unsat` | proven: no solution |
| `interrupted_sat` | a solution found, optimality not proven (time limit) |
| `interrupted` | time limit reached, no solution |
| `unknown` | the backend gave no verdict |
| `error` | the solve failed |

`solve(time_limit=seconds)` enforces a budget through the portfolio backend, a little
slower on easy models (3.15 s against 1.81 s on a 4x4 assignment) but the only way to bound
the run. `result.backend` names the solver that ran. `sat_solver_name`, `maxsat_backend`
and `backend` select the engines; the defaults are `"g4"`, `"rc2"` and `"auto"`.

Errors: Python exceptions (`TypeError`, `ValueError`) are raised at the line that
posts or reads the offending expression, so read the traceback's last line. A solve
problem appears in `r.status`, not as an exception.

## All solutions

Enumeration is by blocking clauses. Block only the variables you want to count:

```python
solutions = []
while True:
    r = m.solve()
    if r.status != "sat":                      # "unsat": no more solutions
        break
    chosen = tuple(bool(r[v]) for v in pick)
    solutions.append(chosen)
    block = None
    for var, value in zip(pick, chosen):       # forbid exactly this assignment
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block
```

Example: [assets/all-solutions](assets/all-solutions/README.md) (subsets of 1..6 summing to 7).

For **integer** decision variables, block each value with a `!=` literal and OR the
literals together. Build the block from literals only:

```python
solutions = []
while True:
    r = m.solve()
    if r.status != "sat":
        break
    cols = [r[q[i]] for i in range(n)]
    solutions.append(cols)
    block = None
    for i in range(n):
        lit = q[i] != cols[i]          # a Literal: "q[i] differs from this value"
        block = lit if block is None else (block | lit)
    m &= block
```

Example: n-queens with `d1`/`d2` from [Derived values](#derived-values) gives 4 solutions
for n = 6 and 92 for n = 8.

| Pitfall | Effect |
|---|---|
| Auxiliary variable left out of the block | Each answer is repeated for every value of the free auxiliary variable (two free Booleans give 4 answers for 2 real ones) |
| Blocking on a derived integer (`x // k`) | Cannot be expressed as a clause; use `floor_div` and block its `IntVar` |

## All optimal solutions

Solve for the optimum, record `cost`, then block each optimal answer and re-solve. The
solver is incremental, so each re-solve returns the next-best answer. Stop when the status
is no longer `optimum` or the cost rises above the first one:

```python
r = m.solve(); best = r.cost; optimal = []
while r.status == "optimum" and r.cost == best:
    chosen = [bool(r[t]) for t in take]
    optimal.append(chosen)
    block = None
    for var, value in zip(take, chosen):
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block
    r = m.solve()
```

Example: [assets/all-optimal](assets/all-optimal/README.md) (minimum vertex covers).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Build takes tens of seconds; objective is a weighted sum | Objective tied to an integer through `sum(c * x) == total` | Use `m.obj[c] += ~x` soft clauses. On a random 4x4 assignment with costs up to 125 the soft form solved in 0.01 s; the tied form did not finish in five minutes |
| Wide `m.int` over millions, very slow or out of memory | Integers are encoded per value | Keep bounds tight, or express the value as a sum of small variables: `sum(10**(9-i) * d[i])` over ten 0..9 integers solved at once (an all-different ten-digit number) |
| `TypeError: unsupported operand ... for %` | No `%` on `IntVar` or `PBExpr` | `q = m.floor_div(x, k)` and `x == k * q + r` with `0 <= r < k` |
| `TypeError: Unsupported decode target` on `r[expression]` | `result[]` decodes variables, literals, and integer derived variables, not sums | Compute the sum from `r[var]` values in Python |
| `TypeError: Clause OR only supports Literal operands` | `|` between a literal and a non-literal, e.g. `(x | y) | False` | Combine only literals with `|`; post the rest as separate `m &=` lines |
| `TypeError: PBConstraint` on `|` | `DivExpr != v` is a constraint, not a literal | Use `m.floor_div` to get an `IntVar` |
| `TypeError: Expected Literal, Clause, or ClauseGroup` | `m &= m.cumulative(...)` | Call `m.cumulative(...)` on its own line |
| `ValueError: Scale factor must be strictly positive` | `m.scale(x, -1)` | Write a sign flip as a complement against a known upper bound |
| `r.ok` is true but the answer is not proven | `interrupted_sat` counts as ok | Test `r.status == "optimum"` |
| `interrupted` with `r.cost` None | Time limit reached before any solution | Raise the limit or simplify the model |
| Maximise reports a small "cost" | `cost` is the forgone weight | Report `sum(weights) - r.cost` |
| `r.cost` is None | No soft clauses: a satisfaction problem | Read `r.status == "sat"` instead |
| Enumeration repeats answers | Auxiliary variables left out of the block, see [All solutions](#all-solutions) | Block only the variables you report, or every variable that changes the answer |
| Enumeration over integer variables finds the same answer again | Blocking only Booleans, or blocking with `==` on whole variables | Block each integer with `q[i] != value` literals OR'd together, as in [All solutions](#all-solutions) |
| Maximisation returns the worst selection (value minimised) | `~x` copied from the minimise row into `m.obj[v] += ~x` | Maximise with the plain literal: `m.obj[v] += x` pays `v` when `x` is false |
| `all_different` cannot take `q[i] + i` or other expressions | Constraint applies to variables only | Create `d[i] == q[i] + i` as an `IntVar` and call `all_different()` on the vector, see [Derived values](#derived-values) |
| Tasks overlap on one machine in a job-shop | No no-overlap constraint posted; precedence alone does not stop overlap | One `m.cumulative(starts, durations, [1] * len(starts), 1)` per machine (ft06 reaches optimum 55 this way) |
| Need a linear equation with a sum on both sides | Assumed to need a constant right-hand side | `m &= (sum(a) == sum(b))` works, as in the cryptarithm `SEND + MORE = MONEY` model with `10**k` weights |
| `r[matrix]` shape unclear | Result nesting is not stated | `r[matrix]` returns a list of row lists with the same shape; `r[x[j]]` reads one row, `[[r[s[j][k]] for k in range(K[j])] for j in range(J)]` builds a ragged table |

## Further reading

- Documentation: [hermax.readthedocs.io](https://hermax.readthedocs.io/en/latest/)
- Quick start and modelling guide: [quickstart](https://hermax.readthedocs.io/en/latest/quickstart.html), [modeling](https://hermax.readthedocs.io/en/latest/modeling.html)
- API reference: [api](https://hermax.readthedocs.io/en/latest/api.html)
- Solver backends: [portfolio](https://hermax.readthedocs.io/en/latest/portfolio.html), [incremental](https://hermax.readthedocs.io/en/latest/incremental.html)
- Examples: [examples](https://hermax.readthedocs.io/en/latest/examples.html) (UWrMaxSAT, RC2, graph colouring, scheduling)
