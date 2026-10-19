---
name: pysat
description: PySAT (python-sat), a Python library for SAT and MaxSAT modelling with CNF and WCNF formulas, cardinality and pseudo-Boolean encoders, finite-domain integers (pysat.integer), SAT solvers such as Glucose, and the RC2 MaxSAT solver. Use when writing, debugging or explaining SAT, MaxSAT or pseudo-Boolean models in Python with pysat, or when a puzzle or optimisation problem should be modelled with pysat.
license: Apache-2.0
compatibility: Requires Python 3.10+ and python-sat with the pblib extra (pip install "python-sat[pblib]"); python-sat is MIT-licensed and free. Building pypblib from source needs a C++ compiler.
metadata:
  domain: constraint-programming
  solver: pysat (glucose42, RC2)
  paradigm: sat
---

# PySAT (Python)

PySAT is a Python toolkit for SAT and MaxSAT. You build a formula from clauses: a `CNF` for constraints, or a `WCNF` whose weighted soft clauses are the objective. Encoders turn cardinality, pseudo-Boolean and finite-domain integer constraints into clauses. A SAT solver or RC2 then searches. Every modelling choice is therefore an encoding choice.

The one idea to keep: **the objective is soft clauses.** Hard clauses are the constraints. RC2 finds a model that satisfies every hard clause and minimises the total weight of the soft clauses it falsifies.

> Tested with python-sat 1.9.dev15 on Python 3.12.11. The examples were run in that environment.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Scheduling at realistic size](#scheduling-at-realistic-size)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- [Runnable examples](#runnable-examples)

## Install

```bash
pip install "python-sat[pblib]"
python -c "import pysat; print(pysat.__version__)"
```

The `pblib` extra is needed for `PBEnc` (pseudo-Boolean encodings). On Python 3.12 pip compiled pypblib from source, because no wheel was available. Details: [installation](https://pysathq.github.io/installation/).

## Quick start

Two integers, minimise `2x + y` under `x + y >= 7` and `x <= y`:

```python
from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

pool = IDPool()
x = Integer("x", 0, 10, vpool=pool)
y = Integer("y", 0, 10, vpool=pool)
engine = IntegerEngine(vars=[x, y], vpool=pool)
engine.add_linear(x + y >= 7)
engine.add_linear(x - y <= 0)

formula = WCNF()
formula.extend(engine.clausify().clauses)      # hard: the constraints
for v in range(1, 11):                         # soft: pay 2v when x = v, v when y = v
    formula.append([-x.equals(v)], weight=2 * v)
    formula.append([-y.equals(v)], weight=v)

rc2 = RC2Stratified(formula, solver="glucose42")
model = rc2.compute()
if model is None:
    print("No optimal solution")
else:
    dense = [-v for v in range(1, pool.top + 1)]   # Integer.decode needs every variable
    for lit in model:
        dense[abs(lit) - 1] = lit
    print("x =", x.decode(dense), "y =", y.decode(dense), "cost =", rc2.cost)
rc2.delete()
```

Output: `x = 0 y = 7 cost = 7`.

## Modelling

Full signatures: [pysat-api.md](references/pysat-api.md). API docs: [formula](https://pysathq.github.io/docs/html/api/formula.html), [card](https://pysathq.github.io/docs/html/api/card.html), [pb](https://pysathq.github.io/docs/html/api/pb.html), [integer](https://pysathq.github.io/docs/html/api/integer.html).

| Need | API |
|---|---|
| Boolean variable | [`IDPool.id(key)`](https://pysathq.github.io/docs/html/api/formula.html) returns a positive literal |
| Clause | [`cnf.append([a, -b])`](https://pysathq.github.io/docs/html/api/formula.html); a negated literal is `-lit` |
| At most / at least / exactly k | [`CardEnc.atmost(lits, bound, vpool=pool)`](https://pysathq.github.io/docs/html/api/card.html), `atleast`, `equals` |
| Weighted sum at most k | [`PBEnc.leq(lits, weights, bound, vpool=pool)`](https://pysathq.github.io/docs/html/api/pb.html); negative weights are accepted |
| Finite-domain integer | [`Integer(name, lb, ub, encoding, vpool=pool)`](https://pysathq.github.io/docs/html/api/integer.html) |
| Linear constraint on integers | [`engine.add_linear(x + 2 * y <= 5)`](https://pysathq.github.io/docs/html/api/integer.html) |
| All different, equal, not equal | `engine.add_alldifferent(vars)`, `add_equal(a, b)`, `add_not_equal(a, b)`: Integer objects only |
| Reified constraint | `sel = engine.add_linear(c, reified=True)` returns a selector literal; `[sel_a, sel_b]` as a clause gives a disjunction. It returns `None` when the bounds already make `c` true: skip that clause, it is satisfied |
| Comparison as a constraint | `engine.add_linear(x >= 3)` works on any encoding; the method `x.ge(3)` returns a literal and needs `order` or `coupled` |
| Hard clause in a WCNF | `wcnf.append(clause)`, or `wcnf.extend(cnf.clauses)` for a whole CNF |
| Soft clause (objective) | `wcnf.append(clause, weight=w)`, `w` a positive integer |

**Encodings for `Integer`:**

| Encoding | Literals | `equals(v)` | `ge(v)` | Use when |
|---|---|---|---|---|
| `direct` (default) | one per value | yes | no | `equals`, `add_not_equal` |
| `order` | one per threshold | no | yes | `ge` tests |
| `coupled` | both, channelled | yes | yes | both are needed |

**Integer literal methods** return a literal to use in a clause or an objective. They are not the same as the operators in `add_linear`:

| Method | Encoding | Literal means | Valid for |
|---|---|---|---|
| `x.equals(v)` | `direct`, `coupled` | `x = v` | `lb <= v <= ub` |
| `x.ge(v)` (= `x.atleast(v)`) | `order`, `coupled` | `x >= v` | `lb + 1 <= v <= ub` |
| `x.le(v)` (= `x.atmost(v)`) | `order`, `coupled` | `x <= v`, i.e. `-x.ge(v + 1)` | `lb <= v <= ub - 1` |

Outside those ranges the method raises `AssertionError: Value is outside ...` because the literal would be constant. Use the bounds, not a literal, for constant cases.

**Objective recipes** (each one is in a runnable example):

| Goal | Soft clauses |
|---|---|
| Minimise a literal's count, weight `w` each | `wcnf.append([-lit], weight=w)` |
| Minimise an integer `x` | `[-x.equals(v)]` with weight `v`, for each `v >= 1` (exactly one value holds) |
| Maximise profit of a chosen literal | `wcnf.append([lit], weight=profit)`: paid when the literal is false, so optimum profit = total profit - `rc2.cost` |
| Minimise an integer `x` (for example a makespan) | `[-x.ge(t)]` with weight 1 for each `t` in `lb + 1 .. ub`, with `x` declared `order` or `coupled`; `x = lb + rc2.cost`. Unit weights, not one distinct weight per value |
| Minimise the number of used values (colours) | hard `[-x_vk, y_k]` for each node `v` and value `k`; soft `[-y_k]` with weight 1. See Colour count below |

A `WCNF` with no soft clauses is solved as a satisfaction problem.

**Colour count** (minimise the number of colours; graph colouring with `K` colour classes and `K` at least the chromatic number):

```python
pool = IDPool()
x = [[pool.id(("x", v, k)) for k in range(K)] for v in range(N)]   # node v has colour k
y = [pool.id(("y", k)) for k in range(K)]                           # colour k is used
wcnf = WCNF()
for v in range(N):
    wcnf.extend(CardEnc.equals(lits=x[v], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
for u, v in EDGES:
    for k in range(K):
        wcnf.append([-x[u][k], -x[v][k]])        # adjacent nodes differ
for v in range(N):
    for k in range(K):
        wcnf.append([-x[v][k], y[k]])            # a used colour sets y_k
for k in range(K):
    wcnf.append([-y[k]], weight=1)               # each used colour costs 1
```

`rc2.cost` is the number of colours. On a triangle with a 4-cycle tail it prints `colours used: 3`.

Wide values: `Integer(name, 0, 10**10)` creates one variable per value. Declare the number as `sum(2**k * bit_k)` over 0..1 Integers instead (a `LinearExpr`).

## Solving

**SAT** ([solvers](https://pysathq.github.io/docs/html/api/solvers.html)):

```python
from pysat.solvers import Solver

with Solver(name="glucose42", bootstrap_with=cnf.clauses) as solver:
    if solver.solve():
        true_lits = {lit for lit in solver.get_model() if lit > 0}
```

| Call | Result |
|---|---|
| `solver.solve()` returns `True` | satisfiable; `get_model()` gives signed literals |
| `solver.solve()` returns `False` | unsatisfiable |
| `solve_limited(expect_interrupt=True)` returns `None` | interrupted by `interrupt()`; see the solver table below |

**MaxSAT** ([RC2](https://pysathq.github.io/docs/html/api/examples/rc2.html)): `RC2Stratified(wcnf, solver="glucose42")`.

| Call | Result |
|---|---|
| `rc2.compute()` returns a list | an optimal model, proven; `rc2.cost` is the minimum falsified weight |
| `rc2.compute()` returns `None` | the hard clauses are unsatisfiable, or the search was interrupted (`rc2.interrupted` is set) |

**Reading values:**

- `get_model()` returns one signed literal per variable: positive is true.
- RC2's `compute()` returns only the variables that occur in the formula, but `Integer.decode(model)` reads `model[abs(lit) - 1]`. Pad the model to `pool.top` first, as the Quick start does. Otherwise every later index shifts.
- `Solver.get_model()` is not always padded either: it has one entry per variable that appears in a clause, so the newest pool ids can be missing. Pad it the same way before `decode`.

**Time limits.** Use `glucose42`: `solver.interrupt()` from a timer stops `solve_limited()`, which returns `None`. `rc2.compute(expect_interrupt=True)` with `rc2.interrupt()` from a timer returns `None` and sets `rc2.interrupted`; a returned model is always proven optimal. CaDiCaL and Lingeling do not honour interrupts: see [pysat-api.md](references/pysat-api.md#solving).

## All solutions

Block exactly the variables the answer is made of. Auxiliary variables may differ between two models of the same answer, so they must not be blocked:

```python
found = []
with Solver(name="glucose42", bootstrap_with=cnf.clauses) as solver:
    while solver.solve():
        true_lits = {lit for lit in solver.get_model() if lit > 0}
        found.append(tuple(v in true_lits for v in answer_vars))
        solver.add_clause([-v if v in true_lits else v for v in answer_vars])
```

**Integer solutions:** block the value literals, not the Integers. Create the `equals` literals before `clausify()`, decode each solution with `Integer.decode`, then block it: `at = [[q[i].equals(c) for c in range(n)] for i in range(n)]` and `solver.add_clause([-at[i][c] for i, c in enumerate(cols)])` excludes that placement of n queens. Eight queens gives 92 solutions this way.

**All optimal solutions:** solve with RC2, keep each model while `rc2.cost` equals the first cost, block it with `rc2.add_clause(...)`, and stop at the first higher cost. Runnable versions: [assets/all-solutions](assets/all-solutions/README.md) and [assets/all-optimal](assets/all-optimal/README.md).

## Scheduling at realistic size

A reified no-overlap constraint over integer starts is quadratic in the horizon for every pair of tasks. Measured on ft06 (6 jobs, 6 machines, 15 reified pairs per machine), clause counts from `engine.clausify()`:

| Horizon | Start encoding | Hard clauses | Clausify time |
|---|---|---|---|
| 197 (sum of durations) | `order` | 13.6M | 21 s |
| 197 | `direct` | 11.9M | 19 s |
| 80 | `order` starts, `coupled` makespan | 1.16M | 1.4 s |
| 68 (greedy schedule) | `order` starts, `coupled` makespan | 0.64M | 0.7 s |
| 55 (optimum) | `direct` | 0.23M | 0.3 s |

Three rules follow:

1. **Horizon:** use the makespan of any feasible schedule, such as a greedy list schedule that always starts the operation that can begin earliest. The sum of durations is a valid horizon but the worst one.
2. **Start domains:** a task's lower bound is the sum of durations before it in its job (its head); its upper bound is `horizon - tail - duration`, where the tail is the sum after it. Without these bounds the same 197 run had 18.2M clauses.
3. **Encoding:** at the same horizon, `direct` starts gave about 13 % fewer clauses than `order`. The horizon is the lever, not the encoding.

With the greedy horizon and unit-weight threshold softs, ft06 solves to the optimum 55 in about 3 s on one CPU: [assets/jobshop](assets/jobshop/README.md). Skip a reified selector that comes back `None`, and check the schedule independently after decoding. In a measured run, weighted makespan softs with distinct weights at horizon 197 took about 110 s of RC2 time.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| Constraints ignored; the optimum is too low | `cnf.weighted()` turns every clause into a weight-1 soft clause | Use `WCNF().extend(cnf.clauses)` for hard clauses |
| `AssertionError: Order encoding is disabled` | `ge()` on a `direct` Integer | Use `equals(v)`, or the `order` or `coupled` encoding |
| `AssertionError: Direct encoding is disabled` | `equals()` on an `order` Integer | Use `direct` or `coupled` |
| `ValueError: NotEqual requires direct or coupled encoding on left` | `add_not_equal` with an `order` Integer | Use `direct` or `coupled` |
| `AttributeError: 'LinearExpr' object has no attribute 'vpool'` | An expression passed to `add_alldifferent`, `add_equal` or `add_not_equal` | Put the expression through `add_linear` |
| Integer values come out wrong after `compute()` | RC2 omits unused variables; `decode` indexes by variable number | Pad the model to `pool.top` (Quick start) |
| Enumeration reports duplicate answers | Blocking clauses include auxiliary variables | Block only the variables the answer is made of |
| Optimal enumeration includes worse answers | Loop does not stop at the first higher cost | Stop when `rc2.cost` exceeds the optimum |
| RC2 is very slow with many distinct weights | Plain `RC2` | Use `RC2Stratified`, and prefer unit weights where the objective allows |
| `rc2.compute()` returns `None` | Hard clauses unsatisfiable, or interrupted | Check `rc2.interrupted`; check the hard clauses |
| `NotImplementedError: Limited solve is currently unsupported by Lingeling` | Lingeling has no limited solve | Use `glucose42` for time limits |
| A time limit is not honoured with `cadical195` | `interrupt()` is ignored by CaDiCaL | Use `glucose42` |
| Huge memory use with a wide `Integer` | One variable per value | Declare the value as a sum of 0..1 Integers |
| `TypeError: bad operand ... 'NoneType'` or `NoneType` in a clause | `add_linear(..., reified=True)` returned `None` because bounds entail the constraint | Skip the clause that needs that selector: it is already satisfied |
| `AssertionError: Value is outside the order domain` | `ge(v)` or `le(v)` outside its valid range | Use the bounds; the literal would be constant (see the integer literal table) |
| `x.ge(v)` raises on a `direct` Integer, but `add_linear(x >= v)` works | The method returns a literal and needs `order` or `coupled`; the operator in `add_linear` is a constraint | Use `add_linear` for a constraint, `x.ge(v)` for a literal in a clause or soft |
| Clause count in the millions, or clausify takes tens of seconds, on a scheduling model | Horizon is the sum of durations; reified pairs grow with its square | Use a greedy makespan as horizon and head/tail start bounds (Scheduling at realistic size) |
| Scheduling with one distinct weight per makespan value is slow | Many distinct weights in RC2 | Unit weights on `[-x.ge(t)]` threshold literals (Objective recipes) |
| `Solver.get_model()` values shifted, or `decode` reads the wrong variable | The model is shorter than `pool.top` | Pad the model to `pool.top` before `decode` |
| Enumeration of integer answers repeats one answer | Blocking clause uses auxiliary variables | Block the `equals` literals of the answer's values (All solutions) |
| `pip install` of pypblib fails | Source build needs a C++ compiler | Install `g++` or a compiler, then retry |

## Further reading

- PySAT documentation: [pysathq.github.io](https://pysathq.github.io/), [docs](https://pysathq.github.io/docs/html/index.html), [usage](https://pysathq.github.io/usage/)
- API reference: [formula](https://pysathq.github.io/docs/html/api/formula.html), [card](https://pysathq.github.io/docs/html/api/card.html), [pb](https://pysathq.github.io/docs/html/api/pb.html), [integer](https://pysathq.github.io/docs/html/api/integer.html), [solvers](https://pysathq.github.io/docs/html/api/solvers.html), [RC2](https://pysathq.github.io/docs/html/api/examples/rc2.html)
- Examples: [pysathq/pysat examples](https://github.com/pysathq/pysat/tree/master/examples)

## Runnable examples

Each folder holds one standalone program and a README with the command and the expected output.

| Example | Pattern |
|---|---|
| [satisfy](assets/satisfy/README.md) | one solve, cardinality, conflicts |
| [all-solutions](assets/all-solutions/README.md) | enumerate every answer by blocking |
| [all-optimal](assets/all-optimal/README.md) | enumerate every minimum-cost answer with RC2 |
| [maximise](assets/maximise/README.md) | assignment with profit as soft clauses |
| [minimise](assets/minimise/README.md) | weighted vertex cover |
| [infeasible](assets/infeasible/README.md) | unsatisfiable CNF and WCNF |
| [scheduling](assets/scheduling/README.md) | single machine, toy size: reified no-overlap, weighted makespan |
| [jobshop](assets/jobshop/README.md) | ft06 job shop at realistic size: greedy horizon, head/tail domains, unit-weight makespan softs |
