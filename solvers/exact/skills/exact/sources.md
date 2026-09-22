# Sources for `exact`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://gitlab.com/nonfiction-software/exact> — Exact 2.2.1, the
  pseudo-Boolean solver and its Python bindings.
- <https://pypi.org/project/exact/> — the distribution the image installs.
- The embedded pybind11 docstrings on `exact.Exact`, which are the authoritative
  signatures: `inspect.signature` raises `ValueError` on these bindings, so the
  method `__doc__` is what to read.
- `solvers/exact/run.py` and `Dockerfile` in this repository — the contract
  this skill describes.

Every claim below was checked by running it inside the integration image, not
taken from documentation alone.

- **`exact` exposes one class, `Exact`, and no modelling layer.** Unlike the
  other Python integrations here, there is no higher-level API to prefer: a
  submission calls `addVariable`, `addConstraint`, `addReification` and
  `setObjective` directly. An earlier version of this integration routed every
  model through a repository-local helper module; that module is gone, and the
  models say the same things in Exact's own calls.
- `toOptimum(timeout)` returns `(state, value)`. **`"SAT"` is the state that
  means the optimum was proven** — there is no `"OPTIMAL"`. `"TIMEOUT"` means
  the search stopped short, and `"UNSAT"` that there is no solution.
- **`hasSolution()` is true even after `"TIMEOUT"` and after `"UNSAT"`.** A
  runner that read the solution without checking the state would hand over an
  unproven answer, which the evaluator would then compare against the reference
  optimum as if it were one. Observed on a 400-item knapsack stopped at 0.001 s
  and at 0.05 s, and on an exhausted enumeration loop.
- **Exact minimises internally, so a maximisation's optimum comes back
  negated.** Maximising a knapsack with optimum 32 returned `('SAT', -32)`,
  with the matching solution. Pinning the objective for enumeration has to flip
  the sign back.
- **`invalidateLastSol(vars)` blocks the last solution projected onto those
  variables.** That is exactly enumeration over declared outputs, so the runner
  builds no blocking constraints of its own.
- `addReification(head, True, terms, lb)` holds `head <-> sum(terms) >= lb`.
  Forcing the head true on `h <-> x >= 3` gave `x = 3`; forcing it false gave
  `x = 2`.
- `addMultiplication(["a", "b"], True, "z", True, "z")` holds `z == a * b`,
  taking variable names rather than numbers as its bounds. With `a = 3` and
  `b = 4` it gave `z = 12`.
- `addConstraint(terms, use_lower_bound, lower_bound, use_upper_bound,
  upper_bound)` carries both bounds in one call.
- **The evaluator compares a 0/1 integer and a Boolean as equal.** A knapsack
  submission declaring its `x` as 0..1 integers was accepted against a
  reference whose brief says `[5]bool`. So this integration needs no way to
  mark an output as Boolean.
- Pigeonhole is no obstacle to Exact, so it is useless as a slow case. Proving
  the optimum of a knapsack is: 60 items of 6 digits takes 0.07 s, 120 items of
  7 digits 2.6 s, and 200 items of 8 digits 25 s. The `timeout_cleanup` check
  uses 160 items of 7 digits, generated from a fixed recurrence so the instance
  is the same on every run.
