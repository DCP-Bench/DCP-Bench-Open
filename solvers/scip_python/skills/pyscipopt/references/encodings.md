# Encodings in PySCIPOpt

Patterns for constraints that `addCons` does not take directly. Every snippet below was
solved on small cases with PySCIPOpt 6.3.0 / SCIP 10.0.2 and gave the intended value.
`m` is a `Model`, `quicksum` comes from `pyscipopt`. API entries:
[Model reference](https://pyscipopt.readthedocs.io/en/latest/api/model.html),
[constraint types](https://pyscipopt.readthedocs.io/en/latest/tutorials/constypes.html).

## Contents
- [Fixing a variable](#fixing-a-variable)
- [Discrete choices and all-different](#discrete-choices-and-all-different)
- [Not equal](#not-equal)
- [Indicators instead of big-M](#indicators-instead-of-big-m)
- [Absolute value](#absolute-value)
- [Minimum and maximum](#minimum-and-maximum)
- [Integer division and modulo](#integer-division-and-modulo)
- [Logic and parity](#logic-and-parity)
- [Products](#products)
- [Nonlinear objective](#nonlinear-objective)
- [Search help: symmetry and implied constraints](#search-help-symmetry-and-implied-constraints)

## Fixing a variable

`m.addCons(b == 0)` fixes a binary (or any variable) to a value; `m.addCons(d[0] >= 1)`
keeps the leading digit of a number from being 0. If the value is known before the model
is built, `lb=ub=v` at `addVar` does the same.

## Discrete choices and all-different

A variable that takes one of k values is best modelled as one-hot binaries; all-different
is then "each value used at most once", far stronger than pairwise `!=`:

```python
b = {(i, v): m.addVar(vtype="B") for i in I for v in V}
for i in I:
    m.addCons(quicksum(b[i, v] for v in V) == 1)
    m.addCons(x[i] == quicksum(v * b[i, v] for v in V))   # integer view, if needed
for v in V:
    m.addCons(quicksum(b[i, v] for i in I) <= 1)          # all-different
```

Element (`y == table[x]` with `x` a variable) is the same pattern:
`y == quicksum(table[v] * b[v] for v in V)`. Example: [assignment](../assets/assignment/README.md).

## Not equal

`addCons(x != y)` raises `NotImplementedError: can only support with '<=', '>=', or '=='`.
For a single pair, one binary `d` chooses the side:

```python
d = m.addVar(vtype="B")
m.addConsIndicator(x - y >= 1, binvar=d)                  # d == 1: x > y
m.addConsIndicator(y - x >= 1, binvar=d, activeone=False) # d == 0: y > x
```

For many pairs over the same values, use the one-hot all-different above.

## Indicators instead of big-M

`addConsIndicator(ineq, binvar=b)` enforces `ineq` when `b == 1`; `activeone=False`
enforces it when `b == 0`.

- Only `<=` or `>=`: an equality raises `ValueError: expected inequality that has either
  only a left or right hand side`. Write an equality as two indicators on the same binary.
- **Always pass `binvar=`.** Without it the call is accepted and SCIP crashes with a
  segmentation fault (exit code 139) at `optimize()`.
- Indicators solved models where the same model with big-M constraints timed out.

## Absolute value

`abs(e)` is accepted in constraints but is slow: `d == abs(x - y)` timed out from about 13
variables, where a sign binary with indicators was fast:

```python
s = m.addVar(vtype="B")
# d == x - y when s == 1, d == y - x when s == 0: two indicators per equality
m.addConsIndicator(d - (x - y) <= 0, binvar=s)
m.addConsIndicator(d - (x - y) >= 0, binvar=s)
m.addConsIndicator(d - (y - x) <= 0, binvar=s, activeone=False)
m.addConsIndicator(d - (y - x) >= 0, binvar=s, activeone=False)
```

`abs(e) <= k` needs no binary: `e <= k` and `-e <= k`.

## Minimum and maximum

Python `max(x, y)` / `min(...)` over variables raises `NotImplementedError: can only
support with '<=', '>=', or '=='`. When the objective already pushes `t` down (minimise a
maximum), `t >= x_i` for every `i` is enough. Otherwise add a selector binary per term:

```python
t = m.addVar(vtype="I", lb=lo, ub=hi)
sel = [m.addVar(vtype="B") for _ in xs]
for x, s in zip(xs, sel):
    m.addCons(t >= x)                          # t is at least every term
    m.addConsIndicator(t - x <= 0, binvar=s)   # and equal to the selected one
m.addCons(quicksum(sel) == 1)
```

Swap the inequalities for a minimum.

## Integer division and modulo

`x // d` and `x % d` raise `TypeError: unsupported operand type(s)`. For a constant
`d > 0`: `q` and `r` are integers with `x == d * q + r` and `0 <= r <= d - 1`
(set `lb=0, ub=d-1` on `r`).

## Logic and parity

| Need | Call |
|---|---|
| `r = b1 and b2 and ...` | `m.addConsAnd([b1, b2, ...], r)`, all binary |
| `r = b1 or b2 or ...` | `m.addConsOr([b1, b2, ...], r)` |
| xor of binaries equal to a constant | `m.addConsXor([b1, b2, ...], True)`; `rhs` must be a Python `bool` |
| parity as a variable `r` | `quicksum(bs) == 2 * k + r`, `k` integer in `0..len(bs)//2`, `r` binary |
| at most `k` nonzero | `m.addConsCardinality(xs, k)` |
| special ordered sets | `m.addConsSOS1(xs)`, `m.addConsSOS2(xs)` |

`addConsXor(bs, var)` with a variable raises `AssertionError: Provide BOOLEAN value as
rhsvar`.

## Products

`x * y`, `x ** 2`, `sqrt`, `exp`, `log`, `e / y` are accepted in constraints (SCIP
solves them as nonlinear constraints). Linearise when you can:

- two binaries, `z = x * y`: `z <= x`, `z <= y`, `z >= x + y - 1`;
- binary `b` times bounded integer `x`, `z = b * x`: indicators `z == x` when `b == 1`
  (two inequalities) and `z <= 0` when `b == 0`;
- an equality between products of integers (`a * b == n ** 2`) can be slow to prove; when
  the structure allows, search over the parameter that determines the factors instead.

## Nonlinear objective

`setObjective` takes a linear expression only; a nonlinear one raises `ValueError: SCIP
does not support nonlinear objective functions. Consider using set_nonlinear_objective in
the pyscipopt.recipe.nonlinear`. Either call that recipe, or minimise a new variable `z`
with `z >= f(x)` (maximise with `z <= f(x)`).

## Search help: symmetry and implied constraints

Both turned timeouts into solves:

- **Break symmetry** by fixing interchangeable objects: the first round of an assignment,
  `x[0] < x[n-1]` for a sequence whose reversal is also a solution, colours used in order
  (`used[c] <= used[c-1]`, see [json-input](../assets/json-input/README.md)). Only do this
  when you want one representative per symmetry class: it removes solutions from an
  enumeration.
- **Add implied (redundant) constraints** derived from the data: counts per value or per
  period, cumulative constraints on the axes of a packing.
- Give every integer a tight finite `lb`/`ub` from the data.
