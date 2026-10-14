# Sources for `docplex`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pypi.org/project/cplex/22.2.0.1/> — the cplex wheel pinned in the
  integration image, "A Python interface to the CPLEX Callable Library,
  Community Edition". Accessed 2026-09-28.
- <https://pypi.org/project/docplex/2.32.264/> — DOcplex 2.32.264, the IBM
  Decision Optimization modelling API for Python pinned in the image.
  Accessed 2026-09-28.
- <https://github.com/IBMDecisionOptimization/docplex> — the DOcplex
  repository, which gives the Community Edition limit as 1000 variables and
  1000 constraints. Accessed 2026-09-28.
- `solvers/docplex_cplex/run.py` and `Dockerfile` in this repository — the
  contract this skill describes.

Every API claim below was checked by running it inside the integration image,
not taken from documentation alone:

- The engine reports itself as CPLEX 22.2.0.0; `import numpy` fails, since
  neither wheel depends on it.
- A model with 1001 variables, or with 1001 constraints, raises
  `docplex.mp.utils.DOcplexLimitsExceeded`: "Promotional version. Problem size
  limits (1000 vars, 1000 consts) exceeded ... CPLEX code=1016". 600 linear
  constraints plus 400 indicators solve; plus 401 indicators fail, so
  indicators count as constraints.
- **With the default `mip.tolerances.mipgap` (1e-4), CPLEX returned status 102,
  "integer optimal, tolerance", at 12168379 on a 40-item strongly correlated
  knapsack whose optimum is 12168772; with the gap at 0 it returns status 101 at
  12168772.** `solvers/docplex_cplex/readiness_test.py` has a `proven_optimum`
  check on that instance.
- Defaults read from the image: `mipgap` 1e-4, `absmipgap` 1e-6,
  `integrality` 1e-5; `integer_var()` has bounds 0 and `model.infinity`.
- Status codes seen: 101 integer optimal, 102 integer optimal within tolerance,
  103 integer infeasible, 118 integer unbounded, 107 time limit exceeded with a
  solution, 1 optimal for an LP.
- `has_objective()` is false for a model with no objective and after
  `minimize(0)`.
- `x != y` builds a `NotEqualConstraint` and solves; `model.abs`, `model.max`
  and `model.min` take expressions; `x * y == 12` is accepted by docplex and
  refused by CPLEX with "Non-convex QCP", printing "Error: Model has non-convex
  quadratic constraint" on standard output from the library.
- `bool(x == 1)` raises `TypeError: Cannot convert linear constraint to a
  boolean value`; `x // 2` and `x % 2` raise `TypeError`.
- `model.abs(a)` returns an `AbsExpr` whose value is held by a continuous
  variable docplex creates.
- The size of each helper in the skill's table was measured with
  `number_of_variables` and `number_of_constraints` before and after posting it
  on two integer variables in 0..9.
- Every encoding in the skill (`!=`, `abs` of an expression, `add_equivalence`,
  indicators for a disjunction, `add_if_then`, all-different through an
  assignment matrix, element, the binary-integer product, division and
  remainder, `max`/`min`/`logical_and`/`logical_or`) was checked by brute force
  over small domains against its intended meaning.
