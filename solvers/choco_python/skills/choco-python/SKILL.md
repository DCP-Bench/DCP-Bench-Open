---
name: choco-python
description: Write instance-agnostic Choco models in Python for the DCP-Bench choco_python integration, covering the submission contract, the pychoco 0.2.1 API surface, and the mistakes that make a submission fail.
---

# Choco models for `choco_python`

Write one Python file that builds a Choco model from instance data. The runner
solves it inside a container; you never solve, print, or read values yourself.

Image: pychoco 0.2.1 on Python 3.12.11. pychoco bundles the Choco native library
in its own wheel, so there is no JVM and no network. Available imports are
`pychoco` and the Python standard library — **not** `numpy`.

## The contract

```python
from pychoco.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.intvar(0, n, name="x")
    y = model.intvar(0, n, name="y")
    model.arithm(x, "+", y, "=", n).post()
    return model, {"x": x, "y": y}
```

- `build(instance)` takes the instance as a plain dict parsed from JSON and
  returns `(model, outputs)`.
- `outputs` maps **exactly** the problem's declared output names to Choco
  variables, plain integers, Booleans, or nested lists of these. Extra or
  missing keys are rejected, and shapes must match the reference exactly.
- Every declared output must read back as an integer or a Boolean. A `BoolVar`
  reads back as a Python `bool`, which the evaluator accepts for a declared
  Boolean output and for a 0/1 integer alike.
- Auxiliary variables need not appear in `outputs`.
- **Every constraint must be `.post()`ed.** A constraint you build and do not
  post is simply absent, and the usual symptom is `invalid_solution` — the
  evaluator finds an assignment your model allowed and the reference rejects.

Do not call `model.get_solver()`, `solver.solve()`, `print()`, or read files.
The runner owns solving, the objective, enumeration and serialisation.

### Optimization

Return a third element, `("minimize", variable)` or `("maximize", variable)`:

```python
def build(instance):
    model = Model()
    ...
    total = model.intvar(0, upper_bound, name="total")
    model.scalar(items, weights, "=", total).post()
    return model, {"x": x}, ("minimize", total)
```

For an unweighted total, `model.sum(items, "=", total).post()` says the same
thing:

```python
    model.sum(items, "=", total).post()
```

**The objective must be a variable, not an expression.** Choco optimizes a
single `IntVar`, so build one, give it a bound wide enough to hold every
attainable value, and post an equality onto it.

The runner proves the optimum itself and then enumerates only assignments that
achieve it. Do not bound the objective with a value you expect: a model that
hardcodes its own answer is the one failure this benchmark exists to catch.

**Take every quantity from `instance`.** The same rule, for the same reason.

## How this integration differs from the CP-SAT and CPMpy ones

- **There is no operator overloading.** `x + y == n` builds a Python expression
  that Choco never sees. Constraints are method calls on the model:
  `model.arithm(x, "+", y, "=", n)`. The `arithm` forms are `(var, op, value)`,
  `(var, op, var)` and `(var, op1, var_or_value, op2, value)`, where `op1` is
  arithmetic and `op2` is a comparison.
- **A weighted sum is `scalar`, a plain sum is `sum`.** `model.sum(vars, "=",
  target)` and `model.scalar(vars, coefficients, "=", target)` both take a
  target that may be a variable or an integer. Coefficients are plain integers.
  Note there is no trailing underscore on `sum`, `min` or `max`, unlike `and_`,
  `or_` and `not_`, which need one to clear the Python builtins.
- **Reification is a method, not a wrapper.** `constraint.reify()` returns a
  `BoolVar` that is true exactly when the constraint holds, and
  `constraint.reify_with(b)` ties it to a `BoolVar` you already have. A reified
  constraint must **not** also be posted: posting it asserts it outright.
- **Counting goes through `count` or through reified equalities.**
  `model.count(value, vars, limit_var)` constrains `limit_var` to the number of
  entries equal to `value`. Otherwise reify each equality and sum the Booleans
  with `sum`.
- **Booleans are variables too.** `model.boolvar()` returns a `BoolVar` usable
  wherever an `IntVar` over 0..1 is, including inside `scalar` and `sum_`.

## API surface, verified in this image

### Model and variables

| Call | Meaning |
| --- | --- |
| `Model(name=None)` | a model; everything else hangs off it |
| `model.intvar(lb, ub, name=None)` | an integer decision variable |
| `model.intvar(values, name=None)` | a variable over an explicit list of values |
| `model.boolvar(name=None)` | a Boolean decision variable |
| `model.get_solver()` | **the runner calls this, not you** |

### Constraints

| Call | Meaning |
| --- | --- |
| `arithm(x, op, y[, op2, z])` | arithmetic relation; `op` is `+ - * / % =` etc, comparisons are `= != < <= > >=` |
| `sum(vars, op, target)` | the sum of `vars` stands in that relation to `target` |
| `scalar(vars, coeffs, op, target)` | the weighted sum |
| `all_different(vars)` | pairwise distinct |
| `all_different_except_0(vars)` | all nonzero entries distinct |
| `all_equal(vars)` | all entries equal |
| `element(value, table, index, offset=0)` | `value` is `table[index]`; **the value comes first and the index third**, and the table may hold integers or variables |
| `count(value, vars, limit)` | `limit` is how many of `vars` equal `value` |
| `global_cardinality(vars, values, occurrences, closed=False)` | occurrence counts per value |
| `among(nb_var, vars, values)` | how many of `vars` take a value in `values` |
| `absolute(result, var)` | `result` is the absolute value of `var` |
| `distance(x, y, op, z)` | `abs(x - y)` stands in that relation to `z` |
| `div(dividend, divisor, result)` / `mod(x, y, z)` / `times(x, y, z)` | integer division, modulo, product |
| `square(result, var)` / `pow(var, exponent, result)` | square and integer power |
| `min(result, vars)` / `max(result, vars)` | minimum / maximum, **result first** |
| `sort(vars, sorted_vars)` | the second list is the first, sorted |
| `circuit(vars)` | the successor list forms one Hamiltonian circuit |
| `table(vars, tuples)` | the assignment matches a row |
| `lex_less(x, y)` / `lex_less_eq(x, y)` | lexicographic order |
| `increasing(vars, delta)` / `decreasing(vars, delta)` | monotone sequences |
| `diff_n(x, y, w, h, add_cumulative)` | rectangles do not overlap |
| `cumulative(tasks, heights, capacity)` | resource capacity is respected |
| `not_(constraint)` / `and_(constraints)` / `or_(constraints)` | logical combination of constraints |

`and_` and `or_` take **constraints**, and the result is itself a constraint you
post. To combine conditions that each need to be true-or-false rather than
asserted, reify them and constrain the Booleans instead.

## Enumeration, and why duplicates matter here

Choco enumerates distinct assignments of *every* variable in the model, while
the evaluator counts distinct **declared outputs**. An auxiliary variable that
is free to vary therefore produces several Choco solutions that look identical
to the evaluator. The runner drops those repeats, so a model is never rejected
for them, but each one costs search time. Give auxiliary variables tight bounds
and functional definitions — `scalar(...) = total` rather than a loose
inequality — so that fixing the outputs fixes them too.

The runner also has to tell an exhausted search from one that ran out of time,
which pychoco 0.2.1 does not report. It times the search and calls it exhaustion
only when Choco stopped well before the budget. A model that finishes just at
the limit is therefore reported as a timeout rather than as complete.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.py --problem PROBLEM --solver choco_python --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example. Add `-W ignore::SyntaxWarning` to
quieten LaTeX in reference docstrings.

Read `reason` and `detail` on failure: `invalid_solution` means the reference
rejects a solution your model allows — suspect an unposted constraint first;
`suboptimal_solution` means your objective is wrong; `invalid_output` means the
declared outputs have the wrong keys, shapes or types; and `execution_error`
carries the Python traceback in its detail.

Never change the reference, the dataset, or the evaluator to make a submission
pass.
