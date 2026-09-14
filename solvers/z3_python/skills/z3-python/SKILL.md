---
name: z3-python
description: Write instance-agnostic Z3 models in Python for the DCP-Bench z3_python integration, covering the submission contract, how to express constraint-programming idioms Z3 has no global for, and the mistakes that make a submission fail.
---

# Z3 models for `z3_python`

Write one Python file that builds constraints from instance data. The runner
solves them inside a container; you never call `check()`, read a model, or print.

Image: Z3 5.1.0 on Python 3.12. Available imports are `z3` and the Python
standard library — **no numpy**, so shape your data with plain lists.

Z3 is an SMT solver, not a CP solver. It has no `AllDifferent`, no `Element`, no
`Cumulative`. Everything is expressed with integer and Boolean arithmetic, plus
the handful of helpers below. Expect to encode more by hand than in CPMpy.

## The contract

Satisfaction problem — return the constraints and the declared outputs:

```python
import z3


def build(instance):
    n = instance["n"]
    x, y = z3.Ints("x y")
    solver = z3.Solver()
    solver.add(x >= 0, x <= n, y >= 0, y <= n, x + y == n)
    return solver, {"x": x, "y": y}
```

Optimization problem — add a third element saying what to optimize:

```python
    return solver, {"x": x, "y": y}, ("minimize", x + y)
```

- `build(instance)` takes the instance as a plain dict parsed from JSON.
- The first element may be a `z3.Solver`, a list of constraints, or a single
  constraint. A `z3.Optimize` is accepted but pointless: the runner sets the
  objective itself from the third element.
- `outputs` maps **exactly** the problem's declared output names to Z3
  expressions, Python integers or Booleans, or nested lists of these. Extra or
  missing keys are rejected, and shapes must match the reference exactly.
- The third element is `("minimize", expression)` or `("maximize", expression)`.
  Omit it entirely for a satisfaction problem.
- Every declared output must be an integer or a Boolean. Declare variables with
  `z3.Int`/`z3.Ints`/`z3.IntVector` or `z3.Bool`/`z3.Bools`/`z3.BoolVector`;
  a `z3.Real` output is rejected, because its value comes back as a rational.
- Auxiliary variables need not appear in `outputs`. When several solutions are
  requested, distinctness is measured only over the declared outputs.

**Take every quantity from `instance`.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

Do not call `solver.check()`, `solver.model()`, `print()`, or read files. The
runner owns solving; it proves the optimum itself and never trusts a claim.

## Expressing CP idioms in Z3

| You want | Write |
| --- | --- |
| all different | `z3.Distinct(xs)` |
| sum | `z3.Sum(xs)` — Python's `sum(xs)` also works |
| product | `z3.Product(xs)` |
| absolute value | `z3.Abs(x)` |
| **maximum / minimum** | no built-in: `functools.reduce(lambda a, b: z3.If(a > b, a, b), xs)` |
| conditional value | `z3.If(condition, then_value, else_value)` |
| logic | `z3.And`, `z3.Or`, `z3.Not`, `z3.Implies`, `z3.Xor` |
| exactly / at most / at least *k* true | `z3.PbEq([(b, 1) for b in bs], k)`, `z3.AtMost(*bs, k)`, `z3.AtLeast(*bs, k)` |
| weighted cardinality | `z3.PbLe([(b, w) for b, w in pairs], bound)`, also `PbGe`, `PbEq` |
| count of a value in a list | `z3.Sum([z3.If(x == v, 1, 0) for x in xs])` |
| **indexing by a decision variable** | no `Element`: either an `If` chain, or an array — `arr = z3.Array("arr", z3.IntSort(), z3.IntSort())`, constrain `arr[k] == v` for each constant `k`, then use `z3.Select(arr, i)` |
| indexing a **matrix** by decision variables | flatten it: mirror `m[i][j]` into `z3.Select(flat, i * width + j)` for every constant `i, j`, then read `z3.Select(flat, row_var * width + col_var)` |
| a Boolean as 0/1 in arithmetic | `z3.If(b, 1, 0)` |

## Gotchas, all verified against Z3 5.1.0

- **`max`, `min`, `any` and `all` from Python raise.** They fail with
  `Z3Exception: Symbolic expressions cannot be cast to concrete Boolean values`.
  Use `z3.Or`/`z3.And`, and the `If`-reduce idiom above for max and min.
  Python's `sum` is the exception: it works, and yields `0 + x + y + …`.
- **Integer division and modulo do not match Python on negative operands.**
  Z3 gives `7 / -2 == -3` and `7 % -2 == 1`, where Python gives `-4` and `-1`.
  (`-7 / 2` agrees at `-4`.) If sign matters, constrain the quotient and
  remainder explicitly rather than relying on either language's convention.
- **`z3.Int` is unbounded.** Unlike `cp.intvar(lb, ub)` there is no domain, so
  add the bounds the problem implies. Without them the solver explores a much
  larger space, and an objective with no bound is reported as an error rather
  than solved.
- **No numpy in the image.** Build nested structure with list comprehensions;
  the runner walks plain lists when it reads your declared outputs.
- **An output variable no constraint mentions** is still fine: the runner
  completes the model, so such a variable gets a definite value.
- **Z3 is often the slow part, not the reference.** On this corpus it solved
  n-queens, magic sequences, Costas arrays and Schur's lemma across every listed
  instance, but ran out of time on the larger all-interval, Langford and
  number-partitioning instances. If an instance fails with `execution_timeout`,
  suspect a missing bound or an encoding Z3 dislikes before blaming the problem;
  `Distinct` over derived expressions and products of two variables are the
  usual culprits.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.py --problem PROBLEM --solver z3_python --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Some references contain LaTeX in their docstrings, so Python prints
`SyntaxWarning: invalid escape sequence` while loading them. That comes from the
reference, not your model, and is harmless; add `-W ignore::SyntaxWarning` to
quieten it.

Read `reason` and `detail` on failure: `invalid_solution` means the reference
rejects a solution your model allows, `suboptimal_solution` means your objective
is wrong, `invalid_output` means the declared outputs have the wrong keys,
shapes or types, and `execution_timeout` usually means missing variable bounds
or an encoding Z3 handles badly.

Repair the model from the reported reason. Never change the reference, the
dataset, or the evaluator to make a submission pass.
