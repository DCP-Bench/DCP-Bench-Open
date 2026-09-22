# The Exact surface, exactly

Signatures from the pybind11 docstrings on `exact.Exact` in Exact 2.2.1, as
installed in the integration image. `inspect.signature` raises `ValueError` on
these bindings, so `__doc__` is what to read. The package exposes exactly one
class and nothing else.

```python
from exact import Exact

solver = Exact()
```

## Building a model

```python
addVariable(name: str, lower_bound: int = 0, upper_bound: int = 1,
            encoding: str = 'log') -> None

addConstraint(terms: Sequence[tuple[int, str]],
              use_lower_bound: bool = False, lower_bound: int = 0,
              use_upper_bound: bool = False, upper_bound: int = 0) -> None

setObjective(terms: Sequence[tuple[int, str]], minimize: bool = True,
             offset: int = 0) -> None

addReification(head: str, sign: bool, terms: Sequence[tuple[int, str]],
               lower_bound: int) -> None
addLeftReification(...)      # head -> constraint
addRightReification(...)     # constraint -> head

addMultiplication(factors: Sequence[str],
                  use_lower_bound: bool = False, lower_bound: str = '',
                  use_upper_bound: bool = False, upper_bound: str = '') -> None

fix(name: str, value: int) -> None
setAssumptions(varvals: Sequence[tuple[str, int]]) -> None
clearAssumptions() -> None
```

`addReification(head, True, terms, lb)` holds `head == 1 <-> sum(terms) >= lb`.
Verified in both directions: forcing the head true on `h <-> x >= 3` gave
`x = 3`, forcing it false gave `x = 2`.

`addMultiplication(["a", "b"], True, "z", True, "z")` holds `z == a * b`.
Verified: with `a = 3` and `b = 4` it gave `z = 12`. The bounds are variable
**names**, not numbers.

## Solving

```python
runOnce(...) -> str
runFull(optimize: bool = True, timeout: float = 0) -> str
toOptimum(timeout: float = 0) -> tuple[str, int]
count(vars: Sequence[str], timeout: float = 0) -> tuple[str, int]
propagate(...)  pruneDomains(...)

hasSolution() -> bool
getLastSolutionFor(vars: Sequence[str]) -> list[int]
getBestSoFar()  getDualBound()  getLastCore()  extractMUS()
invalidateLastSol() -> None
invalidateLastSol(vars: Sequence[str]) -> None
boundObjByLastSol() -> None
```

Three behaviours the runner is built around, all observed in the image:

- **`toOptimum` returns `"SAT"` when it proved the optimum.** There is no
  `"OPTIMAL"`. `"TIMEOUT"` means the search stopped short and `"UNSAT"` that
  there is no solution.
- **`hasSolution()` stays true after `"TIMEOUT"` and after `"UNSAT"`.** It is
  never the test for whether there is an answer; the returned state is. A
  400-item knapsack stopped at 0.001 s and at 0.05 s still reported a solution.
- **Exact minimises internally, so a maximisation's optimum comes back
  negated.** Maximising a knapsack with optimum 32 returned `('SAT', -32)`,
  with the matching solution.

`invalidateLastSol(vars)` adds a constraint ruling out the last solution
**projected onto those variables**, which is what enumeration over declared
outputs needs. There is no need to build blocking constraints by hand.

## Costs to keep in mind

- Integer variables are declared by their bounds and nothing is expanded per
  value, so a wide domain is cheap. `revenue_maximization`, whose objective
  runs to 9000, and `diet`, whose servings run to 10000, are both fine here and
  were not under the one-hot integrations.
- **Indicators are the expensive part.** One 0/1 variable per value, plus two
  linear constraints, is the price of talking about a variable taking a
  particular value. Bound the domain first.
- Pigeonhole is no obstacle to Exact, so it is useless as a slow case. Proving
  the optimum of a knapsack is: 60 items of 6 digits takes 0.07 s, 120 items of
  7 digits 2.6 s, and 200 items of 8 digits 25 s. The `timeout_cleanup` check
  uses 160 items of 7 digits.
