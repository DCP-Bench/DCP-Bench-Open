---
name: choco-python
description: Choco constraint solver in Python through pychoco, which bundles the Choco native library (no JVM). Covers integer and Boolean variables, global constraints, reification, and finding, enumerating or optimising solutions. Use when writing, debugging or explaining Choco models in Python, or when the user has chosen Choco or pychoco for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Requires Python 3.12 (tested) and pychoco (tested 0.2.1 and 0.4.0). No other packages; no JVM.
metadata:
  domain: constraint-programming
  solver: choco
  paradigm: cp
---

# Choco (Python, pychoco)

Choco is a Java constraint solver; pychoco is its Python binding and ships the native library
in the wheel. A `Model` holds variables and constraints; `model.get_solver()` finds, enumerates or
optimises. **A constraint has no effect until it is posted with `.post()`** (or reified on purpose).

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pychoco
python3 -c "import importlib.metadata as m; print('pychoco', m.version('pychoco'))"
```

Tested with pychoco 0.2.1 and 0.4.0 on Python 3.12; every example passes on both.
[pychoco documentation](https://pychoco.readthedocs.io/en/latest/).

## Quick start

```python
from pychoco.model import Model

model = Model()
x = model.intvar(0, 9, name="x")
y = model.intvar(0, 9, name="y")
model.arithm(x, "+", y, "=", 7).post()
model.arithm(x, ">", y).post()

solution = model.get_solver().find_solution()
if solution is None:
    print("no solution")
else:
    print("x =", solution.get_int_val(x), "y =", solution.get_int_val(y))
```

Prints `x = 7 y = 0`.

## Modelling

Full constraint catalogue: [Choco documentation](https://choco-solver.org/docs/); pychoco names follow Choco's.

| Need | API |
|---|---|
| integer variable, or one over explicit values | [`model.intvar(lb, ub, name=...)`](https://pychoco.readthedocs.io/en/latest/), `model.intvar([1, 3, 7])` |
| Boolean variable | [`model.boolvar(name=...)`](https://pychoco.readthedocs.io/en/latest/) |
| arrays of variables | `model.intvars(size, lb, ub)`, `model.boolvars(size)` |
| relation between two terms | `model.arithm(x, op, y)`, or `model.arithm(x, op1, c, op2, z)` with `c` an int or IntVar; ops `+ - * / %`, comparisons `= != < <= > >=` |
| weighted sum | `model.sum(vars, op, target)`, `model.scalar(vars, coeffs, op, target)` |
| pairwise distinct / all equal | `model.all_different(vars)`, `model.all_equal(vars)` |
| `value == table[index]` | `model.element(value, table, index, offset=0)`: value first, index third |
| occurrences of a value | `model.count(value, vars, limit)`: `limit` is how many equal `value` |
| tuple in a table | `model.table(vars, tuples)` |
| min / max of a set | `model.min(result, vars)`, `model.max(result, vars)`: result first |
| absolute, distance, div, mod, product | `model.absolute(result, var)`, `model.distance(x, y, op, z)`, `model.div(x, y, z)`, `model.mod(x, y, z)`, `model.times(x, y, z)` |
| circuit (one tour), lexicographic order | `model.circuit(successors)`, `model.lex_less(x, y)`, `model.lex_less_eq(x, y)` |
| tasks with a resource | `task = model.task(start, duration, end)` per task, then `model.cumulative(tasks, heights, capacity)`; heights and capacity are IntVars |
| no overlap on one machine | `cumulative` with every height `model.intvar(1, 1)` and capacity `model.intvar(1, 1)` |
| non-overlapping rectangles | `model.diff_n(x, y, width, height)` |
| logic over constraints | `model.and_([...])`, `model.or_([...])`, `model.not_(c)` |
| conditional | `model.if_then(cond, then)`, `model.if_then_else(cond, then, else)` |

Note the names: `sum`, `min`, `max` have no trailing underscore. Only `and_`, `or_`, `not_`
do, to avoid Python builtins.

**Argument types.** The left operand of `arithm` must be a variable (`arithm(q, ">=", 2)`, not
`arithm(2, "<=", q)`). An int is allowed as the right operand and as the middle value of the
three-argument form: `arithm(q, "+", 2, "=", up)` is `q + 2 = up`. `scalar` accepts negative
coefficients and a variable listed twice (`[x, x]` with `[1, 2]`, `= 3` gives x = 1, checked
against brute force); one coefficient per variable still reads more clearly.

**Reification.** `c = model.arithm(x, "=", 3)` then `b = c.reify()` gives a BoolVar that is
true exactly when the constraint holds; `c.reify_with(b)` ties an existing BoolVar instead.
Do **not** also post a reified constraint: posting asserts it outright.

**Python operators.** `x + y`, `x * 2`, `x <= y` build Choco expressions. `x + y == 3` is *not* a
constraint but a BoolVar, enforced only once constrained (`model.arithm(b, "=", 1).post()`).
Prefer the explicit `arithm` / `scalar` forms.

**Counting distinct values.** To minimise the number of distinct values used (colours, shifts,
bins), do not count the value variables. Make one Boolean per possible value, tie it to the
variables with `if_then(model.arithm(v[i], "=", k).reify(), model.arithm(used[k], "=", 1))`
for every variable `i` and value `k`, then `model.sum(used, "=", count)` is the objective.
Worked example: [distinct-count](assets/distinct-count/model.py).

## Solving

Status and parameters: [pychoco solver reference](https://pychoco.readthedocs.io/en/latest/).

| Call | Returns |
|---|---|
| `solver.find_solution()` | a `Solution`, or `None` |
| `solver.solve()` | `True` or `False` |
| `solver.find_all_solutions(solution_limit=None)` | list of `Solution`; `[]` when infeasible |
| `solver.find_optimal_solution(objective, maximize)` | best `Solution`, or `None` |
| `solver.find_all_optimal_solutions(objective, maximize)` | list of `Solution`; `[]` when infeasible |

**Reading values.** Read them from the `Solution`: `solution.get_int_val(var)` works for IntVar
and BoolVar (a BoolVar gives `1` or `0`); `get_set_val` for set variables. `Solution` has no
`get_value`. A `Solution` is a snapshot: it keeps its values after later solve calls on the
same model. `var.get_value()` works only right after a solve that instantiated the variable
(it returns `bool` for a BoolVar); after `find_all_solutions` it raises `AssertionError`.

**Time limit.** Call `solver.limit_time("2s")` before the search, or pass `time_limit="2s"` to a
`find_*` call. Use seconds: in pychoco 0.2.1 and 0.4.0 `"300ms"` is silently ignored (a 10^6-solution
enumeration ran 2.9 s, against 0.8 s with `"0.5s"`, which can overrun slightly).

| Result | What you see | Notes |
|---|---|---|
| a solution | `Solution` / non-empty list | |
| proven infeasible | `None` / `False` / `[]` | the search finished |
| limit hit, nothing found | the same `None` / `False` / `[]` | pychoco has no status flag to tell this apart; if the elapsed time is close to the limit, treat the answer as unknown |
| optimum not proven | the best solution found | a run that used its whole limit may not have proven optimality |

Choco reports a free constraint on **stdout** (`ARITHM ([x = 2]) is free`); search the output for it.

**One solve per model after infeasibility.** After a result says infeasible, a second solve on
the same model (another `find_*` or `solve()`, even through a new `get_solver()`) crashes the
Python process with a JVM "Fatal error" and exit code 99. Build a new `Model` for each solve.

## All solutions

`find_all_solutions()` enumerates distinct assignments of **every** variable, auxiliary ones
included: a free `aux` in 0..5 with `x` in 1..2 gave 12 solutions, and with `aux = x` it gave 2.
Tie auxiliary variables to the outputs with functional constraints (see
[make-change](assets/make-change/model.py)), or keep the distinct output tuples:
`{tuple(s.get_int_val(v) for v in outputs) for s in solutions}`. `solution_limit=n` stops early.

## All optimal solutions

`find_all_optimal_solutions(cost, maximize)` returns every assignment with the optimum value.
The same duplicate rule applies. Example: costs `[2, 1, 2, 5]`, choose 2 items at minimum cost:
two optima, `{0, 1}` and `{1, 2}`. See [choose-two](assets/choose-two/model.py).

## Optimisation

The objective must be an **IntVar**, not an expression. Create one with bounds wide enough for
every attainable value, post an equality onto it, and pass it:

```python
total = model.intvar(0, upper, name="total")
model.scalar(items, weights, "=", total).post()        # or model.sum(items, "=", total)
solution = model.get_solver().find_optimal_solution(total, False)   # False = minimise
```

`maximize=True` maximises. A bound that is too tight silently removes solutions, so take it from
the data, not from an answer. Examples: [production-plan](assets/production-plan/model.py) (maximise),
[transport-cost](assets/transport-cost/model.py) (minimise), [project-schedule](assets/project-schedule/model.py)
(makespan through `model.max`).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| A constraint is ignored; Choco prints `is free` | built but not `.post()`ed | post it, or reify it on purpose |
| `AttributeError: ... no attribute 'sum_'` | `sum`, `min`, `max` have no underscore | use `sum`, `min`, `max`; underscore only for `and_`, `or_`, `not_` |
| `x + y == 3` has no effect, or `'BoolVar' ... no attribute 'post'` | operator result is a BoolVar, not a constraint | `model.arithm(b, "=", 1).post()`, or use `arithm` / `scalar` |
| `AttributeError: 'int' object has no attribute 'handle'` from `arithm` | int on the left, e.g. `arithm(2, "<=", q)` | put the variable first: `arithm(q, ">=", 2)` |
| same error from `cumulative` | int heights or capacity | pass IntVars: `model.intvar(1, 1)` for a unit height or capacity |
| `Fatal error: Unhandled exception`, exit 99, on a second solve | solve again on a model that reported infeasible | build a new `Model` for each solve |
| `AttributeError: 'Solution' ... get_value` | `Solution` has no `get_value` | `solution.get_int_val(var)` |
| `AssertionError: ... is not instantiated` | `var.get_value()` after an enumeration | read values from each `Solution` |
| wrong `element` or `min`/`max` result | arguments in the wrong order | `element(value, table, index)`; `min(result, vars)`, `max(result, vars)` |
| optimisation ignores the objective | objective is not an IntVar | post `scalar`/`sum` onto a fresh IntVar and pass it |
| objective counts values, not distinct values | counting value variables | one usage Boolean per value, as in Modelling |
| `AttributeError: 'Task' ... ensure_bound_consistency` | the method exists in 0.2.1 only | do not call it; the examples give the same results on 0.2.1 and 0.4.0 |
| program ignores its input file | data hardcoded in the model | read `sys.argv[1]`, print JSON, as in [json-io](assets/json-io/model.py) |

## Runnable examples

Each folder is a standalone program: `python3 model.py` from inside it (`json-io` takes
`instance.json` as argument).

| Pattern | Folder |
|---|---|
| satisfy, `all_different` | [latin-square](assets/latin-square/model.py) |
| all solutions, functional auxiliary | [make-change](assets/make-change/model.py) |
| all optimal solutions | [choose-two](assets/choose-two/model.py) |
| maximise; instance in, JSON out | [production-plan](assets/production-plan/model.py), [json-io](assets/json-io/model.py) |
| minimise, grid of flows | [transport-cost](assets/transport-cost/model.py) |
| count distinct values | [distinct-count](assets/distinct-count/model.py) |
| no overlap on one machine | [no-overlap](assets/no-overlap/model.py) |
| infeasible | [pigeonhole-infeasible](assets/pigeonhole-infeasible/model.py) |
| scheduling, `cumulative`, makespan | [project-schedule](assets/project-schedule/model.py) |

## Further reading

- pychoco documentation and API: <https://pychoco.readthedocs.io/en/latest/>
- Choco solver documentation (constraints, search): <https://choco-solver.org/docs/>
- pychoco source and examples: <https://github.com/chocoteam/pychoco>
