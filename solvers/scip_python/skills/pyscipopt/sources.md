# Sources for `pyscipopt`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pypi.org/project/pyscipopt/6.3.0/> — PySCIPOpt 6.3.0, the version pinned in
  the integration image. The cp312 manylinux x86_64 wheel bundles SCIP 10.0.2 and needs
  NumPy. PyPI JSON gives the wheel sha256 `f1c6696a58be7e088017a57982dc9d8a681da3f21bdca1d74fba2d41b47f5fbe`.
  Accessed 2026-10-14.
- <https://github.com/SCIP-Interfaces/PySCIPOpt> — the README: PySCIPOpt is MIT licensed;
  SCIP from 8.0.3 on is Apache-2.0. Accessed 2026-10-14.
- `pyscipopt/scip.pyi` and `pyscipopt/scip.pxi` in the 6.3.0 wheel — method signatures:
  `addVar`, `addCons`, `addConsIndicator(cons, binvar=None, activeone=True)`,
  `addConsAnd`, `addConsOr`, `addConsXor`, `addConsSOS1/2`, `addConsCardinality`,
  `setObjective`, `getObjective`, `getBestSol`, `freeTransform`, `setPresolve`,
  `hideOutput`, `setParam`, `setIntParam`. Accessed 2026-10-14.
- Probes run on the host with pyscipopt 6.3.0 (cp313 wheel, same API) and in the built
  `dcp-eval/scip_python:v1` image: `Expr.terms` keys are `Term` tuples of variables, the
  constant is the empty term; `Solution[expr]` evaluates constants and expressions;
  `addConsIndicator` requires an inequality and an explicit `binvar`; indicator without
  `binvar` and a failed `addCons` followed by `freeTransform` segfault.
- `solvers/scip_python/run.py` and `Dockerfile` in this repository — the contract this
  skill describes.
