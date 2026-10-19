# Encodings of common constraints

Each block is a fragment: `model`, the variables and the bounds are assumed. Every
encoding was checked by solving small instances with gurobipy 13.0.3
against its intended meaning. Full API: [Python reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html).

Indicator constraints (`(b == 1) >> constraint`) need no big-M, so prefer them. Where
a big-M is unavoidable, derive it from the variable bounds and keep it small: a loose
big-M slows the search, and with the integrality tolerance (`IntFeasTol`, 1e-5) a
"zero" binary can carry `M * 1e-5` through the constraint.

**Speed.** Prefer indicators for correctness (there is no M to get wrong), not for speed. Measured
on the 6x6 jobshop ft06 (optimum 55, `MIPGap = 0`), no-overlap as indicators and as big-M
gave the same optimum and both took about 0.01 to 0.02 s over three runs each. At this size
neither encoding is faster. For larger instances, time both on your data before choosing.

**Scaling of pairwise encodings.** `a != b` and all-different written pairwise add one binary
pair and two indicators per pair of variables: `n` variables give `n(n-1)/2` pairs, so `2n(n-1)`
indicator constraints for all-different. The cryptarithm with 8 letters (28 pairs) solved
fine; the tester's estimate is that this form scales poorly beyond about 10 letters (unmeasured
here). For all-different over a small value set, use the assignment encoding above
(`n * m` binaries, one row and one column constraint each), which is the form to reach for
first.

| Need | Encoding |
|---|---|
| all different over values 1..m | assignment binaries, one value per position, at most one position per value |
| `a != b` | one of two indicator-guarded strict inequalities |
| disjunction of linear constraints | one indicator per branch, `branch.sum() >= 1` |
| `d == abs(a - b)` | auxiliary `diff == a - b`, then `d == gp.abs_(diff)` |
| reified equality `c == (a == b)` | `lt + gt == 1 - c`, indicators on `c`, `lt` and `gt` |
| element `value == table[index]` | one-hot `choose`, `index` and `value` read it back |
| count of xs equal to v | `count == pick.sum("*", v)` on the assignment binaries |
| product `p == b * a`, binary `b`, `a` in lo..hi | four linear big-M inequalities (below) |
| `q = a // k`, `r = a % k`, constant `k > 0` | `a == k * q + r` with bounds on `q` and `r` |
| `max`, `min`, `and`, `or` | `gp.max_`, `gp.min_` (variables), `gp.and_`, `gp.or_` (binaries) |

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

# d = |a - b|: the argument of abs_ must be a variable
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

Problems whose constraints are already linear (assignment, covering, knapsack, blending,
facility location, fixed-charge scheduling) need none of this.

**Products of two decision variables** (`x * y`) give a quadratic expression. Gurobi
accepts it, but the size-limited licence caps it at 200 variables, and a nonconvex
quadratic is much slower than a linear model. Linearise with the product encoding above
when one factor is binary or has a small range.
