---
name: z3-python
description: Z3, an SMT solver with a Python API (pip package z3-solver, import z3) for integer, Boolean and array constraints, satisfiability checks, optimisation and solution enumeration. Use when writing, debugging or explaining Z3 models in Python, or when the user has chosen Z3 for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Requires Python 3 and pip, and the z3-solver package (tested with package 5.1.0.0, which reports Z3 core version 5.1.0, on Python 3.12; Z3 itself is MIT-licensed, no key or size limit)
metadata:
  domain: constraint-programming
  solver: z3
  paradigm: smt
---

# Z3 (Python)

Z3 is an SMT solver: it decides satisfiability of logical formulas over integers, reals,
Booleans and arrays. It has **no global constraints** (no all-different, element,
cumulative or table as built-ins), so encode them with `Distinct`, `If`, `Select` and
linear arithmetic. Integers are unbounded unless you bound them.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Program interface](#program-interface)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/<example>/`, one folder per pattern (table under Quick start)

## Install

```bash
pip install z3-solver
python -c "import z3; print(z3.get_version_string())"
```

Details: [Z3 guide, logic introduction](https://microsoft.github.io/z3guide/docs/logic/intro/)

## Quick start

```python
import z3

x, y = z3.Ints("x y")
solver = z3.Solver()
solver.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
if solver.check() == z3.sat:
    model = solver.model()
    print(model[x], model[y])  # 4 3
else:
    print(solver.check())
```

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](assets/satisfy-magic-square/README.md) | satisfy, `Distinct`, sums | `python3 model.py` |
| [all-solutions-subset-sum](assets/all-solutions-subset-sum/README.md) | all solutions, blocking clause | `python3 model.py` |
| [all-optimal-partition](assets/all-optimal-partition/README.md) | all optimal solutions | `python3 model.py` |
| [maximise-workshop](assets/maximise-workshop/README.md) | maximise | `python3 model.py` |
| [minimise-rental](assets/minimise-rental/README.md) | minimise | `python3 model.py` |
| [infeasible-shifts](assets/infeasible-shifts/README.md) | infeasible | `python3 model.py` |
| [schedule-single-machine](assets/schedule-single-machine/README.md) | scheduling | `python3 model.py` |
| [minimise-colours](assets/minimise-colours/README.md) | minimise the number of distinct values | `python3 model.py` |

## Modelling

Full list: [Python API reference](https://z3prover.github.io/api/html/namespacez3py.html)

| Need | API |
|---|---|
| integer variables (no domain: add bounds) | [`z3.Int`, `z3.Ints`](https://z3prover.github.io/api/html/namespacez3py.html) |
| Boolean variables | [`z3.Bool`, `z3.Bools`](https://z3prover.github.io/api/html/namespacez3py.html) |
| lists of variables | [`z3.IntVector`, `z3.BoolVector`](https://z3prover.github.io/api/html/namespacez3py.html) |
| all different | [`z3.Distinct(xs)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| sum, product, absolute value | [`z3.Sum`, `z3.Product`, `z3.Abs`](https://z3prover.github.io/api/html/namespacez3py.html) (Python `sum(xs)` also works, giving `0 + x + y`) |
| conditional value | [`z3.If(c, a, b)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| logic | [`z3.And`, `z3.Or`, `z3.Not`, `z3.Implies`, `z3.Xor`](https://z3prover.github.io/api/html/namespacez3py.html) |
| exactly / at most / at least *k* true | [`z3.PbEq(pairs, k)`, `z3.AtMost(*bs, k)`, `z3.AtLeast(*bs, k)`](https://z3prover.github.io/api/html/namespacez3py.html) |
| weighted cardinality | [`z3.PbLe`, `z3.PbGe`, `z3.PbEq`](https://z3prover.github.io/api/html/namespacez3py.html) with `[(b, w), ...]` |
| Boolean as 0/1 in arithmetic | `z3.If(b, 1, 0)` |
| count of a value in a list | `z3.Sum([z3.If(x == v, 1, 0) for x in xs])` |
| number of distinct values used (e.g. colours) | one Boolean per candidate value `used[v] == z3.Or([x == v for x in xs])`, then minimise `z3.Sum` of the `used` flags; do not bound the largest value, because values need not be contiguous ([minimise-colours](assets/minimise-colours/README.md)) |
| maximum / minimum | no built-in: `functools.reduce(lambda a, b: z3.If(a > b, a, b), xs)` (min: `<`) |
| index an array by a variable | [`z3.Array`, `z3.Select`](https://z3prover.github.io/api/html/namespacez3py.html): constrain `arr[k] == v` for each constant `k`, then `z3.Select(arr, i)`; or an `If` chain |
| index a matrix by variables | flatten: `z3.Select(flat, i * width + j)` with `flat[i*width+j]` tied to each constant cell |
| no-overlap of intervals (scheduling) | pairwise `z3.Or(end_a <= start_b, end_b <= start_a)`; no `NoOverlap` or `Cumulative` exists |

Build constraints with the Python operators (`<=`, `+`, `==`); they produce Z3 expressions,
not Python booleans. Pass them to `Solver.add` or `Optimize.add`.

**Scheduling.** Use the pairwise `z3.Or` no-overlap by default: it needs no constant. Big-M
(`start_b >= end_a - M * b` with a Boolean ordering `b`) needs an `M` above every start time;
the sum of all durations is safe, a fixed one such as `10**6` may not be. Both solved a 36-task
job-shop in under a second on one CPU; measure before using big-M at larger scale.

## Solving

Status: [`Solver.check`](https://z3prover.github.io/api/html/classz3py_1_1_solver.html) ·
[`Optimize`](https://z3prover.github.io/api/html/classz3py_1_1_optimize.html)

| Result of `check()` | Meaning |
|---|---|
| `z3.sat` | a model exists; read it with `model()` |
| `z3.unsat` | proven: no model exists |
| `z3.unknown` | undecided; `reason_unknown()` says why, e.g. `"timeout"` |

Use `Solver` for satisfiability and `Optimize` for `minimize` / `maximize`. An `Optimize`
returns a handle from `minimize(expr)`; after `check() == z3.sat`, `upper(handle)` is the
best value found and `lower(handle)` the proven bound. The optimum is proven when both are
the same finite integer; an unbounded objective shows `-1*oo` or `oo`.

`upper(handle)` and `lower(handle)` return Z3 numerals, not Python ints: print them, or
convert with `.as_long()` (an `AttributeError` on `oo` means the bound is infinite). The
model from `optimizer.model()` is the solution behind `upper` after `sat`; when `lower` equals
`upper` it is an **optimal** assignment, and the model from a run stopped by timeout is only the
best found. Check `lower == upper` before reporting the model as optimal.

Reading values: `model[x]`, or `model.eval(e, model_completion=True)` for any expression,
then `.as_long()` for integers and `z3.is_true(...)` for Booleans. `model()` raises
`Z3Exception: model is not available` unless the last `check()` returned `sat`.

Parameters: `solver.set("timeout", ms)` works on `Solver` and on `Optimize`; `solver.set("random_seed", n)`
is accepted on `Solver` ([Solver](https://z3prover.github.io/api/html/classz3py_1_1_solver.html),
[Optimize](https://z3prover.github.io/api/html/classz3py_1_1_optimize.html)).

Errors: Python-level mistakes raise `z3.Z3Exception` or `AttributeError` at the call site,
with a traceback on stderr. A wrong answer is not an error; check results against the model.

## All solutions

Z3 has no enumeration call: loop over `check()` and block each assignment of the
**decision** variables. Auxiliary variables (intermediate sums, makespans) must stay out
of the blocking clause, or each solution appears once per auxiliary value.

```python
while solver.check() == z3.sat:
    model = solver.model()
    values = [z3.is_true(model.eval(b, model_completion=True)) for b in decision]
    solutions.append(values)
    solver.add(z3.Or([b != v for b, v in zip(decision, values)]))
```

All **optimal** solutions: solve with `Optimize` and take `best = upper(handle).as_long()`,
then enumerate on a plain `Solver` with the same constraints plus `objective == best`.
Example: [all-optimal-partition](assets/all-optimal-partition/README.md).

## Program interface

A model program that reads its data from a JSON file indexes the keys it needs by name, so
extra keys in the file do no harm. Report `unsat` and `unknown` as outcomes, not crashes:
Z3 signals them through `check()`, never through an exception.

```python
import json
import sys

import z3

with open(sys.argv[1]) as f:
    data = json.load(f)
n_nodes, edges = data["n_nodes"], data["edges"]  # other keys in the file are ignored

colour = [z3.Int(f"c{i}") for i in range(n_nodes)]
solver = z3.Solver()
solver.add([z3.And(c >= 0, c < 3) for c in colour])
solver.add([colour[a] != colour[b] for a, b in edges])

result = solver.check()
if result == z3.sat:
    model = solver.model()
    print([model.eval(c, model_completion=True).as_long() for c in colour])
elif result == z3.unsat:
    print("no 3-colouring exists")
else:
    sys.exit(f"undecided: {solver.reason_unknown()}")
```

Print the values from the model (`.as_long()`, `z3.is_true`), not the raw `model()`, whose
order and format are Z3's own. `sys.exit("message")` prints the message to stderr and exits
with status 1.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Z3Exception: Symbolic expressions cannot be cast to concrete Boolean values` | Python `max`, `min`, `any` or `all` applied to Z3 expressions | `z3.Or` / `z3.And`; `If`-reduce for max and min (see [Modelling](#modelling)) |
| `AttributeError: module 'z3' has no attribute 'Max'` (also `Min`, `Element`, `AllDifferent`) | no such global in Z3 | `Distinct`; `If`-reduce; `Select` |
| `if x == 3:` takes the wrong branch, or never fires | `==` builds an expression; for a symbolic `x` it is `False` in Python | put it in a constraint (`solver.add(x == 3)`) or test a model value with `z3.is_true(model.eval(...))` |
| Result differs from Python for negative `/` or `%` | Z3 `div` and `mod` are Euclidean: `7 / -2 = -3`, `7 % -2 = 1`; Python gives `-4`, `-1` | constrain quotient and remainder explicitly (`7 == q * d + r`, `0 <= r < abs(d)`) |
| `check()` returns `unknown`, `reason_unknown()` is `timeout` | unbounded integers, products of two variables, large `Distinct` over derived expressions | add the bounds the problem implies; linearise; raise `timeout`; reformulate |
| optimum never proven: `lower` and `upper` differ or are infinite | objective unbounded, or search stopped early | bound the variables the objective depends on; raise the timeout |
| `Z3Exception: model is not available` | `model()` read after `unsat` or `unknown` | test `check() == z3.sat` first |
| enumeration repeats a solution | auxiliary variables included in the blocking clause | block only the decision variables |
| a value prints as `1/3` | `z3.Real` sort | use `z3.Int` for integer answers, or `.as_fraction()` |
| program breaks on a data file with extra keys | the code iterates over the JSON dict or passes it whole to Z3 | index the keys the model needs by name (`data["edges"]`); ignore the rest |
| program ends with no useful message | the reason is in a traceback on stderr, or was never printed | print the `check()` result and `reason_unknown()`; treat `unsat` as an answer, not an error |
| `AttributeError: 'ArithRef' object has no attribute 'as_long'` on an objective bound | `upper` or `lower` is `oo` or `-1*oo` (unbounded), not a numeral | bound the objective; report unbounded explicitly |
| minimising colours or groups counts the largest value, not the number used | `max + 1` is not the number of distinct values when values are not contiguous | one `used` flag per value, sum the flags ([Modelling](#modelling)) |
| big-M schedule gives wrong or infeasible answers | `M` too small: it cuts off valid schedules; too large: weak relaxation | use the pairwise `z3.Or` no-overlap; see [Modelling](#modelling) |

## Further reading

- Z3 guide, logic: <https://microsoft.github.io/z3guide/docs/logic/intro/>
- Z3 guide, optimisation: <https://microsoft.github.io/z3guide/docs/optimization/intro/>
- Z3 guide, arithmetic theory: <https://microsoft.github.io/z3guide/docs/theories/Arithmetic/>
- Python API reference (all functions): <https://z3prover.github.io/api/html/namespacez3py.html>
- Source and examples: <https://github.com/Z3Prover/z3> (`examples/python`)
