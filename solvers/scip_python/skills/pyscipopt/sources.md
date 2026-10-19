# Sources for `pyscipopt`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

Tested with PySCIPOpt 6.3.0 (bundling SCIP 10.0.2), Python 3.12.11 and NumPy 2.4.6.

Existing skills: not searched in this refactor; the content is carried over from the
earlier skill, which was written from the campaigns below.

Independent toy test: 18/18

- <https://pypi.org/project/pyscipopt/6.3.0/> — PySCIPOpt 6.3.0. The cp312 manylinux
  x86_64 wheel bundles SCIP 10.0.2 and needs NumPy. PyPI JSON gives the wheel sha256
  `f1c6696a58be7e088017a57982dc9d8a681da3f21bdca1d74fba2d41b47f5fbe`. Accessed 2026-10-14.
- <https://github.com/SCIP-Interfaces/PySCIPOpt> (now <https://github.com/scipopt/PySCIPOpt>) —
  the README: PySCIPOpt is MIT licensed; SCIP from 8.0.3 on is Apache-2.0. Accessed 2026-10-14.
- `pyscipopt/scip.pyi` and `pyscipopt/scip.pxi` in the 6.3.0 wheel — method signatures:
  `addVar`, `addCons`, `addConsIndicator(cons, binvar=None, activeone=True)`,
  `addConsAnd`, `addConsOr`, `addConsXor`, `addConsSOS1/2`, `addConsCardinality`,
  `setObjective`, `getObjective`, `getBestSol`, `freeTransform`, `setPresolve`,
  `hideOutput`, `setParam`, `setIntParam`. Accessed 2026-10-14.
- <https://pyscipopt.readthedocs.io/en/latest/> — documentation, installation guide, Model
  API reference, constraint-type and expression tutorials (linked from the skill).
  Accessed 2026-10-16.
- <https://www.scipopt.org/doc/html/PARAMETERS.php> — parameter names `limits/time`,
  `limits/gap`, `limits/absgap`, `parallel/maxnthreads`, `randomization/randomseedshift`.
  Accessed 2026-10-16.
- <https://github.com/scipopt/PySCIPOpt/tree/master/examples/finished> — official
  examples; the n-queens one-hot model follows the usual MIP formulation. Accessed 2026-10-16.

Learned from modelling campaigns of many models with PySCIPOpt 6.3.0 (kept from the earlier skill):

- Indicator constraints solved models where the big-M version timed out.
- `d == abs(x - y)` timed out from about 13 variables, where a sign binary with
  indicators was fast.
- Symmetry breaking (fixing interchangeable objects, `x[0] < x[n-1]` for reversible
  sequences) and implied constraints from the data (counts per value or period,
  cumulative constraints on the axes of a packing) turned timeouts into solves.
- One-hot binaries with "each value at most once" are far stronger than pairwise `!=`.
- An equality between products of integers (`a * b == n ** 2`) can be slow to prove;
  searching over the parameter that determines the factors was faster.
- With a bare expression as objective, one model proved its optimum in 2 s and then timed
  out searching for the second optimal solution; holding the objective in a bounded
  integer variable avoided it.
- `m.count()` returned 0 where solutions existed on a model with indicators.
- A rejected `addCons` that was caught, followed by `freeTransform` and another solve,
  segfaulted (earlier probe; not reproduced with a `!=` rejection on 2026-10-16).
- `getVal` was seen returning 0 with no incumbent in the earlier setup.

Verified by running (PySCIPOpt 6.3.0, 2026-10-16):

- `addConsIndicator` without `binvar` is accepted and the process dies with SIGSEGV
  (exit 139) at `optimize()`; an equality in `addConsIndicator` raises `ValueError:
  expected inequality that has either only a left or right hand side`.
- `x != y` and `max(x, y)` raise `NotImplementedError: can only support with '<=', '>=',
  or '=='`; `x // 2` and `x % 2` raise `TypeError`; `1 <= x + y <= 3` raises `TypeError:
  Can't evaluate constraints as booleans`, while `(1 <= x + y) <= 3` is accepted.
- A nonlinear objective raises `ValueError: SCIP does not support nonlinear objective
  functions. Consider using set_nonlinear_objective in the pyscipopt.recipe.nonlinear`.
- `addConsXor(bs, var)` raises `AssertionError: Provide BOOLEAN value as rhsvar`.
- Statuses: a model with no objective reports `optimal`; infeasible → `infeasible`;
  unbounded integer maximisation → `unbounded`; `limits/time = 0` → `timelimit` with
  `getNSols() == 0`.
- With no solution, `getVal` raises `Warning: No solution available` and `getBestSol()`
  returns `None`; after `freeTransform()`, `getVal` still returns the previous solution's
  value.
- `addVar` on a solved model without `freeTransform()` prints `ERROR: cannot call method
  <SCIPcreateVarBasic> in problem solved stage`.
- `m.count()` on `x != y` over `0..3` via two indicators counted 5 solutions; there are 12.
- A comment `# Encoding: one-hot binaries per value` on line 1 gives `SyntaxError:
  encoding problem: one-hot`.
- Every snippet in `references/encodings.md` (`!=`, `abs` via indicators, parity, and/or,
  max with selectors, divmod, binary and binary-integer products, `x * y == 12`,
  cardinality, SOS1) solved on small cases with the intended value.
- All eight examples in `assets/` pass `check_assets.py` and the Quick start prints
  `Objective: 14`, `x = 0 y = 7`.
- `addConsCumulative(starts, durs, [1, 1, 1], 1)` keeps three jobs apart on one machine
  (makespan 9 for durations 3, 2, 4, proven optimal).
- `m.count()` on a pure binary n-queens model (n = 8) gave `getNCountedSols() == 92` in
  about 0.9 s; the no-good loop took about 12 s for the same 92 (independent toy test).
- A fractional objective pinned exactly (`z == m.getObjVal()`) stayed feasible in 30 of 30
  random binary models; `z <= best + 1e-6` is also feasible.
- A model with an unbounded free integer variable and an infeasible equality reports
  `inforunbd`; after `freeTransform()` and presolve off it reports `infeasible`. Minimal
  case (2026-10-16, image): continuous `x >= 0` maximised, integer `y` free, `2*y == 1`:
  `inforunbd`, then `infeasible`. With `2*z == 2*x + 1` (`z` integer) the re-solve gives
  `unbounded`.
- The all-optimal loop with a fractional objective (`z` continuous, one-sided pin, or the
  exact `z == best`) matched a brute-force count on 40 random 0/1 models with coefficients
  such as 0.1, 0.25, 1.1 and maximise or minimise (80 runs, 0 mismatches).
- `Expr.terms` keys are `Term` tuples of variables with the constant under the empty
  term; `getBestSol()[expr]` evaluates constants and expressions (earlier probes on the
  host with the cp313 wheel, same API, and in the image).
- `addCons(b == 0)` and `addCons(d[0] >= 1)` fix a binary and a lower bound in a small
  model that then solves as intended.
- `SEND + MORE == MONEY` as one equality with `10**k` weights over one-hot digits solved in
  under 0.01 s.
- The independent toy test found that the json-input example linked `x[v, c]` to `used[c]`
  only through edges, so an isolated vertex could take an uncounted colour; the example
  now links every vertex and its data includes an isolated vertex.
