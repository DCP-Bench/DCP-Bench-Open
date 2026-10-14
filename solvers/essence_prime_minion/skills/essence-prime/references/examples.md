# Tested examples

Both models ran standalone in the image (`/opt/savilerow/savilerow`) and through
`evaluation.evaluate(path, "skilltest", "essence_prime_minion", reference_source=REF, instances=[...], instance_count=2)`
against a CPMpy reference, 2026-10-13: queens accepted (2 instances, 9 solutions checked, limit 5),
knapsack accepted (2 instances).

## Satisfaction: n queens (field `n`, output `q`)

`queens.eprime`
```
language ESSENCE' 1.0
$ Place n queens on an n x n board so that no two attack each other.
given n : int(1..20)
find q : matrix indexed by [int(1..n)] of int(1..n)

branching on [q]

such that
$ no two queens are in the same row of the board (one queen per column, rows given by q)
allDiff(q),
$ no two queens share an ascending diagonal
allDiff([q[i] + i | i : int(1..n)]),
$ no two queens share a descending diagonal
allDiff([q[i] - i | i : int(1..n)])
```
`queens.param`
```
language ESSENCE' 1.0
letting n = 6
```
`savilerow queens.eprime queens.param -run-solver -all-solutions` for n = 6 wrote four files, e.g.
`queens.param.solution.000001`:
```
language ESSENCE' 1.0
letting q be [2, 4, 6, 1, 3, 5]
```
For n = 3 no solution file is written and the info file has `SolverSatisfiable:0`.

Reference (CPMpy, the `# Data` block and the literal `solution` dict are what the evaluator reads):
```
# Data
n = 6
# End of data
import cpmpy as cp
import json
q = cp.intvar(1, n, shape=n, name="q")
model = cp.Model(cp.AllDifferent(q), cp.AllDifferent([q[i] + i for i in range(n)]),
                 cp.AllDifferent([q[i] - i for i in range(n)]))
model.solve()
solution = {"q": [int(v) for v in q.value()]}
print(json.dumps(solution))
```

## Optimisation: knapsack (fields `n`, `capacity`, `weights`, `values`; outputs `take`, `total`)

`knap.eprime`
```
language ESSENCE' 1.0
$ Choose items to put in a knapsack of limited capacity, maximising the total value.
given n : int(1..50)
given capacity : int(0..10000)
given weights : matrix indexed by [int(1..n)] of int(0..1000)
given values : matrix indexed by [int(1..n)] of int(0..1000)
find take : matrix indexed by [int(1..n)] of bool
find total : int(0..50000)

maximising total
such that
$ the total weight of the chosen items must not exceed the capacity
(sum i : int(1..n) . take[i] * weights[i]) <= capacity,
$ total is the summed value of the chosen items
total = (sum i : int(1..n) . take[i] * values[i])
```
`knap.param`
```
language ESSENCE' 1.0
letting n = 4
letting capacity = 10
letting weights = [5, 4, 6, 3]
letting values = [10, 40, 30, 50]
```
Result: `letting take be [false, true, false, true]`, `letting total be 90`, with `SolverTimeOut:0` in the
info file. Without the parentheses around each `sum`, Savile Row stops with
`ERROR: 'And' contains something other than a relation`. With `-all-solutions` it prints a warning and
still writes only the best solution.

Reference: same data in a `# Data` block, `take = cp.boolvar(shape=n, name="take")`,
`total = cp.intvar(0, 50000, name="total")`, `model.maximize(total)`, and
`solution = {"take": [bool(v) for v in take.value()], "total": int(total.value())}`. The evaluator
accepted bool outputs as Essence' bools.

## Ragged and mixed fields (from `solvers/essence_prime_minion/readiness_test.py`, run by readiness)

Instance `{"rows": [[4, 5], [6, 7, 8]]}` binds `rows` padded with 0 and `rows_len = [2, 3]`:
```
given rows : matrix indexed by [int(1..2), int(1..3)] of int(0..100)
given rows_len : matrix indexed by [int(1..2)] of int(1..3)
...
forAll i : int(1..2) . total[i] = sum j : int(1..rows_len[i]) . rows[i, j]
```
The model fixes the row count and the longest row in the `given` domains, so every instance must share them.
Mixed rows `[[True, 3, [[1, 2]]], ...]` bind `items_1` (bool), `items_2` (int), `items_3` (padded) and `items_3_len`.
