# Sources for `exact`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://gitlab.com/nonfiction-software/exact> — Exact 2.2.1, the
  pseudo-Boolean solver and its Python bindings.
- <https://pypi.org/project/exact/> — the distribution the image installs.
- The embedded pybind11 docstrings on `exact.Exact`, which are the authoritative
  signatures: `inspect.signature` raises `ValueError` on these bindings, so the
  method `__doc__` is what to read.
- `solvers/exact/dcp_pb.py`, `run.py` and `Dockerfile` in this repository — the
  contract this skill describes.

Every claim below was checked by running it inside the integration image during
the run recorded at `generation/runs/20260922T0200Z-exact-e3a7`, not taken from
documentation alone.

- `toOptimum(timeout)` returns `(state, value)`. **`"SAT"` is the state that
  means the optimum was proven** — there is no `"OPTIMAL"`. `"TIMEOUT"` means
  the search stopped short, and `"UNSAT"` that there is no solution.
- **`hasSolution()` is true even after `"TIMEOUT"`.** A runner that read the
  solution without checking the state would hand over an unproven answer, which
  the evaluator would then compare against the reference optimum as if it were
  one. Observed on a 400-item knapsack stopped at 0.001s and at 0.05s.
- **Exact minimises internally, so a maximisation's optimum comes back
  negated.** Maximising a knapsack with optimum 10 returned `('SAT', -10)`, with
  the matching solution. Pinning the objective for enumeration has to flip the
  sign back.
- `addVariable(name, lower_bound=0, upper_bound=1, encoding='log')` gives native
  integer variables, and `setObjective(terms, minimize=True, offset=0)` takes a
  linear expression. Neither needs the one-hot machinery the SAT and MaxSAT
  integrations here rely on.
- `addConstraint(terms, use_lower_bound, lower_bound, use_upper_bound,
  upper_bound)` carries both bounds, which is what `between` uses.
- Pigeonhole is no obstacle to Exact, so it is useless as a slow case. Proving
  the optimum of a random knapsack is: 60 items of 6 digits takes 0.07s, 120
  items of 7 digits 2.6s, and 200 items of 8 digits 25s. The `timeout_cleanup`
  check uses the last of those.
