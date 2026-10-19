# Sources for `mip-python`

Tested with mip 2.0.0 (cbcbox 2.935, which bundles CBC `devel (git:146ce89)`), Python 3.12.11, Linux x86_64.

Existing skills: none found. The skill registry search (`npx skills find python-mip`) was not run successfully; the Node.js version on the test machine fails to load the CLI.

- <https://www.python-mip.com> — project site and installation (accessed 2026-10-17)
- <https://python-mip.readthedocs.io/en/latest/classes.html> — API reference: `Model`, `Var`, `LinExpr`, `OptimizationStatus`, parameters (accessed 2026-10-17)
- <https://github.com/coin-or/python-mip> — source of mip 2.0.0 (`mip/model.py`, `mip/cbc.py`, `mip/entities.py`, `mip/constants.py`), read for defaults: `max_mip_gap` 1e-4, `max_mip_gap_abs` 1e-10, `integer_tol` 1e-6, `verbose` 1, `threads` 0, `sol_pool_size` 10; the default solver choice in `Model.__init__`
- <https://pypi.org/project/cbcbox/2.935/> — the CBC binary distribution that mip 2.0.0 loads; its `__init__.py` shows how the build variant is chosen

Verified by running (mip 2.0.0 with CBC):
- Defaults listed in *Solving* match `Model` after construction, with `solver_name="CBC"`.
- Status values: a feasible model with no objective gives `OPTIMAL`; `INFEASIBLE` for a proven infeasible model, including an integer model whose relaxation is feasible (`2z = 1`); `UNBOUNDED` for an unbounded maximisation; `FEASIBLE` with a value after a 5 s limit on a 150-binary subset-sum; `NO_SOLUTION_FOUND` with `None` values after a 3 s limit on an 11-mark Golomb ruler; `OTHER` for a model with no variables.
- A gap of 0.5 gives `OPTIMAL` with a nonzero gap (bound 212,914,418 against value 211,572,205); the default 1e-4 gave `OPTIMAL` with gap 4.5e-5 on a subset-sum where a gap-0 run found a better value.
- `x == 3` inside `if` is truthy; `x * y`, `abs(x)` raise `TypeError`; `x / 0` raises `ZeroDivisionError`; `m += x` raises `TypeError`; `m += 2 <= 3` raises `TypeError`; a binary with `ub=3` raises `ValueError`.
- Verbose defaults to 1 and prints CBC's log to stdout; `verbose = 0` silences it.
- Pool: a tie of four binaries with `sum == 2` gives `num_solutions == 1`, so the pool does not list every optimum.
- Integer outputs came back exact (whole floats) in 20 runs with objective coefficients up to 1e9 and integer outputs up to 2.5e10.
- Every encoding in *Encoding the constraints* was checked against brute-force semantics on a small domain: `!=`, the threshold flag, `abs` under both directions, exact `min` and `max`, binary products, binary times integer, one-of-set, all-different on a pair, table lookup, disjunction, no-overlap, strict bounds.
- Every program in `assets/` prints the answer in its README. Knapsack was checked by brute force (61); the Petersen graph has chromatic number 3; six queens have 4 placements; the committee and schedule answers were checked by hand; the latin square is checked in the program itself.
