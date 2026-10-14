# Sources for `hermax`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://github.com/josalhor/hermax> — hermax 1.2.5, and `hermax.model`, the
  modelling layer submissions are written against.
- `solvers/hermax/run.py` and `Dockerfile` in this repository — the contract
  this skill describes.

Every claim below was checked by running it inside the integration image, not
taken from documentation alone.

- `hermax.model.Model` is the framework's own modelling layer: Boolean, integer,
  enum, set and interval variables, vectors, matrices and dicts of each,
  `all_different`, the cardinality helpers, `cumulative`, `max`/`min`/`sum_var`,
  and `solve`. The package exposes it as `hermax.model` beside `hermax.core`.
- **`m.obj[weight] += literal` pays `weight` when the literal is false.** The
  documented example is `m.obj[3] += a  # pay 3 if a is false`, confirmed by
  solving it: `status optimum, cost 0, a=True b=False c=True`.
- **`Model.solve(time_limit=...)` works**, and selects
  `PortfolioSolver[first_optimal_or_best_until_time_limit]`. A 14-into-13
  pigeonhole returned `interrupted` after 2.7 s against a 2.0 s limit. An
  earlier version of this integration recorded that no hermax backend could be
  time-bounded; that was measured against the raw backends in `hermax.core` and
  is false at the `Model` layer, which is why the runner no longer supervises a
  child process.
- Solve statuses are plain strings: `sat`, `optimum`, `unsat`, `interrupted`,
  `interrupted_sat`, `unknown`, `error`. `result.ok` covers `sat`, `optimum`
  **and `interrupted_sat`**, so it is not a safe test for "this is an answer".
- `result.cost` is `None` for a model with no soft clauses, which is how the
  runner tells a satisfaction problem from an optimisation one.
- `result[container]` returns nested Python lists of `bool` or `int`, so a
  declared output can be handed over whole.
- **Tying a weighted sum to an integer variable is the expensive shape.** On a
  four-by-four assignment problem with costs up to 125,
  `m &= (sum(cost[i][j] * x[i][j]) == total)` spent 43 s inside `build` before
  solving began. The same problem written with `m.obj[cost[i][j]] += ~x[i][j]`
  built and solved in 0.21 s and gave the same optimum, 265.
- The solver is genuinely incremental across solve calls: posting a blocking
  clause and re-solving returned the next-best cost rather than repeating the
  first answer. That is what optimal-solution enumeration relies on.
- `m.scale(x, factor)` raises `ValueError: Scale factor must be strictly
  positive`, so a maximisation cannot be written as a scale by -1.
- hermax brings its own `hermax.encoder.card` and `hermax.encoder.pb_enc`, and
  does not call PySAT's `CardEnc` or `PBEnc`. Its only install requirement is
  `python-sat`, so the image needs no pypblib build.
- EvalMaxSAT is much faster at pigeonhole than the SAT integration's Glucose: it
  refutes 13 pigeons into 12 holes in about 0.7 seconds, where Glucose already
  needs more than two seconds. The `timeout_cleanup` check therefore uses 16
  into 15 here.
- **A sum of hermax variables is a `hermax.model.PBExpr`**, and a single
  `c * literal` is a `hermax.model.Term`. A PBExpr carries `terms` (Terms of a
  coefficient and a `Literal`), `int_terms` (coefficient and a derived integer
  such as a `DivExpr`) and `constant`. An `IntVar` inside a sum is lowered to
  its threshold literals, so `sum(10**(2-i) * d[i])` over 0..9 IntVars holds 27
  Terms and no `int_terms`; `2 * (x // 3)` keeps the `DivExpr` in `int_terms`.
- **`result[expression]` raises `TypeError: Unsupported decode target`** for a
  PBExpr, while `result[literal]` and `result[DivExpr]` decode. Adding
  `constant + sum(c * result[item])` reproduced the value computed from the
  decoded variables on every one of five enumerated solutions, with negated
  literals, subtraction and a `DivExpr` in the sum.
- A ten-digit all-different number as `sum(10**(9-i) * digit[i])` imported,
  built and solved in 0.25 s, and `sum(2**k * bit[k]) == 2**39 + 4613732` over
  40 Booleans solved in 0.013 s. A lone `IntVar` over a ten-digit range, or
  over 0..5,333,333, was killed at the 2048 MB limit with nothing else in the
  model (`generation/runs/20261001T1218Z-hermax-e024`, attempt-002 of
  `divisible_by_1_through_9` and of `fibonacci_even`).
- `x != v` on an `IntVar` is a `Literal`, and literals OR into a `Clause`;
  `DivExpr != v` is a `PBConstraint`, which `|` rejects with `TypeError`. That
  is why the runner cannot block a `DivExpr` inside an output sum.
- hermax has no `%` on a `PBExpr` or an `IntVar` (`TypeError`);
  `number == 7 * q` with `q` a sum of Booleans solved to 980672, a multiple of 7.
- With the runner's repeated-output guard disabled, `{"x": a + b}` under
  `a + b == 1` emitted `{"x": 1}` twice; with it, once followed by `complete`.
