# The Exact Python surface

Signatures from the pybind11 doc strings on `exact.Exact`, Exact 2.2.1. `inspect.signature`
raises `ValueError` on these bindings, so read `help(Exact.method)` or `Exact.method.__doc__`.
The package exposes one class, `Exact`.

```python
from exact import Exact
solver = Exact()
```

## Building a model

| Method | Signature (abridged) | Notes |
|---|---|---|
| `addVariable` | `(name: str, lower_bound=0, upper_bound=1, encoding='log')` | duplicate name: `ValueError: Variable a already exists.` |
| `addConstraint` | `(terms, use_lower_bound=False, lower_bound=0, use_upper_bound=False, upper_bound=0)` | `terms`: `[(int, str), ...]` |
| `setObjective` | `(terms, minimize=True, offset=0)` | `offset` is included in the value `toOptimum` returns |
| `addReification` | `(head: str, sign: bool, terms, lower_bound)` | `head == 1 <-> sum(terms) >= lower_bound` |
| `addLeftReification` | same | `head -> constraint` |
| `addRightReification` | same | `constraint -> head` |
| `addMultiplication` | `(factors: [str, str], use_lower_bound, lower_bound: str, use_upper_bound, upper_bound: str)` | bounds are variable **names** |
| `fix` | `(name, value)` | |
| `setAssumptions` / `clearAssumptions` / `setAssumptionsList` | assume values for variables | assumption solving |
| `setSolutionHints` / `clearSolutionHints` | hints for the search | |

Rows without a verified behaviour below come from the doc strings only.

Verified behaviours:

- `addReification("h", True, [(1,"x")], 3)` with `h` forced to 1 gives `x >= 3`; forced to
  0 gives `x <= 2`. With `sign=False` the head is the negation: `h == 1` gives `x <= 2`.
- `addLeftReification` with `h` forced to 1 gives `x >= 3`; with `x` forced to 1 it forces
  `h == 0`. `addRightReification` with `h` forced to 1 gives `x >= 3`; with `x` forced to 0 it
  forces `h == 0`.
- `addMultiplication(["a","b"], True, "z", True, "z")` with `a = 3`, `b = 4` gives `z = 12`.
- `encoding` accepts `"log"`, `"order"`, `"onehot"`; anything else raises
  `ValueError: Unknown encoding ...`.
- `addVariable("q", 5, 1)`: `ValueError: Upper bound 1 of q is smaller than lower bound 5`.
- A variable with lower bound equal to upper bound is a constant (`addVariable("c", 4, 4)`).
- `setObjective` with an unknown name raises `ValueError: No variable zz found.`.

## Solving

| Method | Returns | Notes |
|---|---|---|
| `runOnce(timeout=0)` | state | stops at the first state reached |
| `runFull(optimize=True, timeout=0)` | state | `optimize=False` for enumeration or satisfaction |
| `toOptimum(timeout=0)` | `(state, value)` | `SAT` = proven optimum; `TIMEOUT` = not proven |
| `count(vars, timeout=0)` | `(state, n)` | distinct solutions projected onto `vars` |
| `propagate(vars, timeout=0)` | `(state, [(lo, hi), ...])` | implied bounds |
| `pruneDomains(vars, timeout=0)` | `(state, [[...], ...])` | smallest domains |
| `extractMUS(timeout=0)` | `(state, [names])` | minimal unsatisfiable subset |
| `getLastCore()` | `[names]` | last assumption core |
| `hasSolution()` | bool | stays true after `TIMEOUT` and after exhaustion; do not use as the test |
| `getLastSolutionFor(vars)` | `[int, ...]` | `[]` on an infeasible model |
| `getBestSoFar()` | int | best objective found so far (the internal sign: negated for a maximisation) |
| `getDualBound()` | int | best bound |
| `invalidateLastSol()` / `invalidateLastSol(vars)` | None | blocks the last solution, optionally projected onto `vars` |
| `boundObjByLastSol()` | None | tightens the objective bound by the last solution |
| `getStats()` | `[(name, float), ...]` | internal statistics |
| `printInput()`, `printVariables()`, `printFormula()` | None | prints to stdout |

Verified behaviours:

- `toOptimum` on a minimisation with `offset=7`, `2a + 3b` and `a + b >= 5`: `('SAT', 17)`.
- `toOptimum` on a maximisation returns the negated value: `('SAT', -34)` for an optimum of 34,
  and `('SAT', -110)` for `x + 100` with `x <= 10`.
- `toOptimum` on an infeasible model: `('UNSAT', 0)`; `runFull` and `runOnce`: `'UNSAT'`.
- `toOptimum(timeout=0.05)` on a 160-item knapsack: `('TIMEOUT', 0)` after 0.051 s, with
  `hasSolution()` True.
- `runFull(timeout=0.05)` on the same model: `'TIMEOUT'`.
- Enumeration `while runFull(optimize=False) == "SAT"` with `invalidateLastSol(names)`
  yields each distinct projection once, then `UNSAT`; `hasSolution()` is then True.
- `count(["a","b"])` with `a + b = 3`, both in 0..3: `('SAT', 4)`.
- After pinning a maximisation's real terms with bounds 5..9 (optimum 9), `runFull(optimize=False)`
  returns `SAT` with a solution inside the pin.
- `fix("a", 2)` on `a` in 0..5: `runFull` gives `a = 2`.
- Zero coefficient in a constraint: `addConstraint([(0,"a")], True, 1, False, 0)` is `UNSAT`
  (it is correct; drop zero coefficients for clarity).

## Costs

- Integer variables are declared by their bounds and not expanded per value, so a wide
  domain is cheap.
- Indicators are the expensive part: one 0/1 variable per value, plus two linear constraints
  per variable. Bound the domain first.
- Pigeonhole is no obstacle, so it is not a slow case for Exact. Knapsack optimum proof times
  in this build: 60 items of 6 digits 0.07 s, 120 items of 7 digits 2.6 s, 200 items of
  8 digits 25 s.
- No-overlap on the 6 x 6 job shop (ft06, optimum 55): reified pair pattern 0.09 s wall time
  including Python start-up; big-M order constraint with M = the horizon 0.09 s; the same big-M
  with M = 100, 10^3, 10^4, 10^6 and 10^8 also 0.05-0.1 s. No time-out was seen for either.
- `addConstraint(terms, True, k, True, k)` is `sum == k`; a `(0, name)` term added to `terms`
  makes `[(0,"a")] >= 1` UNSAT (verified earlier); drop zero coefficients before the call.
- `pip install exact` in a fresh virtual environment (Python 3.12.11, linux/amd64)
  installs Exact 2.2.1, and `from exact import Exact` works.
