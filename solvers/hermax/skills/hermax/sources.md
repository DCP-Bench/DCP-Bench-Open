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
