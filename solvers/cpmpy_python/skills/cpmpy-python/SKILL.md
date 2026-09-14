---
name: cpmpy-python
description: Write instance-agnostic CPMpy models in Python for the DCP-Bench cpmpy_python integration, covering the submission contract, the CPMpy 1.0.0 API surface, and the mistakes that make a submission fail.
---

# CPMpy models for `cpmpy_python`

Write one Python file that builds a model from instance data. The runner solves
it inside a container; you never solve, print, or read values yourself.

Image: CPMpy 1.0.0, OR-Tools 9.15.6755, NumPy 2.x. Available imports are
`cpmpy`, `numpy`, and the Python standard library.

## The contract

```python
import cpmpy as cp


def build(instance):
    n = instance["n"]
    x, y = cp.intvar(0, n, shape=2)
    model = cp.Model(x + y >= n if instance["optimize"] else x + y == n)
    if instance["optimize"]:
        model.minimize(x + y)
    return model, {"x": x, "y": y}
```

- `build(instance)` takes the instance as a plain dict parsed from JSON and
  returns `(model, outputs)`.
- `outputs` maps **exactly** the problem's declared output names to CPMpy
  variables, expressions, constants, or nested lists/arrays of these. Extra or
  missing keys are rejected, and shapes must match the reference exactly.
- Every declared output must be an integer or Boolean. A float value fails.
- Auxiliary variables need not appear in `outputs`. When several solutions are
  requested, distinctness is measured only over the declared outputs.
- Objectives are integer only, set with `model.minimize(...)` or
  `model.maximize(...)`. The runner proves optimality; do not assume it.

**Take every quantity from `instance`.** A model that hardcodes the numbers of
the example is the one failure this benchmark exists to catch, and it will be
rejected the moment a second instance is checked.

Do not call `.solve()`, `.value()`, `print()`, or read files. The runner owns
solving, objective handling, enumeration, and serialisation.

## Gotchas, all verified against CPMpy 1.0.0

- **`max`, `min`, `any`, `all` must be the CPMpy versions.** The Python
  built-ins raise `ValueError: __bool__ should not be called on a CPMPy
  expression`. Use `cp.max`, `cp.min`, `cp.any`, `cp.all`. Built-in `sum` does
  work and produces the same expression as `cp.sum`, but prefer `cp.sum` for
  consistency.
- **No floats anywhere.** A float coefficient raises at build time:
  `TypeError: Multiplication does not support float constants`. Scale to
  integers instead.
- **Broadcasting follows NumPy exactly.** `x * w` for `x` of shape `(2, 3)` and
  `w` of shape `(3,)` multiplies column-wise and is correct; a mismatched shape
  such as `(2,)` raises `ValueError` rather than silently misaligning. Reach for
  `np.multiply` or explicit indexing for clarity, not for correctness.
- **Indexing with a decision variable** works as `arr[idx]`. Wrap a plain Python
  list in `cp.cpm_array(...)` first; a NumPy array or a CPMpy variable array
  needs no wrapping.
- **An output variable no constraint mentions** is still fine: the runner
  registers declared outputs so they get a value.

## API surface

### Model and variables

| Call | Meaning |
| --- | --- |
| `cp.Model(*constraints)` | build a model; `model += constraint` adds more |
| `model.minimize(expr)` / `model.maximize(expr)` | set an integer objective |
| `cp.intvar(lb, ub, shape=None, name=None)` | integer decision variable(s) |
| `cp.boolvar(shape=None, name=None)` | Boolean decision variable(s) |
| `cp.cpm_array(arr)` | make a Python list indexable by a decision variable |

Comparisons `== != < <= > >=`; arithmetic `+ - * // % **` and unary `-`; logic
`& | ~ ^` and `a.implies(b)`; aggregations `cp.sum`, `cp.abs`, `cp.max`,
`cp.min`, `cp.any`, `cp.all`.

### Global constraints

| Constraint | Meaning |
| --- | --- |
| `cp.AllDifferent(*args)` | all arguments take different values |
| `cp.AllDifferentExcept0(*args)` | all nonzero arguments differ |
| `cp.AllDifferentExceptN(args, n)` | all arguments not equal to a value in `n` differ |
| `cp.AllEqual(*args)` | all arguments take the same value |
| `cp.AllEqualExceptN(args, n)` | all arguments not equal to a value in `n` are equal |
| `cp.Circuit(*args)` | the successor array forms one Hamiltonian circuit |
| `cp.Inverse(array1, array2)` | channelling: `array1[i]` is the index of `i` in `array2` |
| `cp.Table(array, table)` | the assignment matches a row of `table` |
| `cp.ShortTable(array, table)` | as `Table`, with wildcards allowed in `table` |
| `cp.NegativeTable(array, table)` | the assignment matches no row of `table` |
| `cp.IfThenElse(cond, if_true, if_false)` | all three are Boolean expressions |
| `cp.InDomain(expr, domain)` | non-interval domain for an expression |
| `cp.Xor(arg_list)` | exclusive or |
| `cp.Cumulative(start, duration, end=None, demand=None, capacity=None)` | resource capacity is never exceeded |
| `cp.CumulativeOptional(..., is_present=None)` | `Cumulative` with optional tasks |
| `cp.NoOverlap(start, duration, end=None)` | intervals do not overlap |
| `cp.NoOverlapOptional(..., is_present=None)` | `NoOverlap` with optional tasks |
| `cp.Precedence(vars, precedence)` | values must appear in the given order |
| `cp.GlobalCardinalityCount(vars, vals, occ)` | each `vals[i]` occurs `occ[i]` times |
| `cp.Increasing(array)` / `cp.IncreasingStrict(array)` | non-decreasing / strictly increasing |
| `cp.Decreasing(array)` / `cp.DecreasingStrict(array)` | non-increasing / strictly decreasing |
| `cp.LexLess(l1, l2)` / `cp.LexLessEq(l1, l2)` | lexicographic order between two lists |
| `cp.LexChainLess(X)` / `cp.LexChainLessEq(X)` | rows of a matrix in lexicographic order |
| `cp.Regular(array, transitions, start, accepting)` | the sequence is accepted by an automaton |
| `cp.MDD(array, transitions, start=None, reduce=True)` | the sequence is accepted by a decision diagram |
| `cp.DirectConstraint(name, arguments, novar=None)` | call a solver-specific constraint by name |

`Regular` is the right tool for row/column pattern problems such as nonograms.

### Global functions

| Function | Meaning |
| --- | --- |
| `cp.Minimum(arg_list)` / `cp.Maximum(arg_list)` | minimum / maximum of the arguments |
| `cp.Abs(expr)` | absolute value |
| `cp.Element(arr, idx)` | `arr[idx]`; prefer writing `arr[idx]` directly |
| `cp.Count(arr, val)` | how many entries of `arr` equal `val` |
| `cp.Among(arr, vals)` | how many entries of `arr` take a value in `vals` |
| `cp.NValue(arr)` / `cp.NValueExcept(arr, n)` | number of distinct values, optionally ignoring `n` |
| `cp.BoolVal(arg)` | wrap a Python or NumPy Boolean as an expression |

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.py --problem PROBLEM --solver cpmpy_python --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Some references contain LaTeX in their docstrings, so Python prints
`SyntaxWarning: invalid escape sequence` while loading them. That comes from the
reference, not your model, and is harmless; add `-W ignore::SyntaxWarning` to
quieten it.

Read `reason` and `detail` on failure:
`invalid_solution` means the reference rejects a solution your model allows,
`suboptimal_solution` means your objective is wrong, and `invalid_output` means
the declared outputs have the wrong keys, shapes, or types.

Repair the model from the reported reason. Never change the reference, the
dataset, or the evaluator to make a submission pass.
