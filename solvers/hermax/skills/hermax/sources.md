# Sources for `hermax`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://github.com/josalhor/hermax> — hermax 1.2.5, "a Python library of
  incremental MaxSAT solvers", and the backends it wraps.
- <https://pysathq.github.io/docs/html/api/card.html> and
  <https://pysathq.github.io/docs/html/api/pb.html> — `CardEnc` and `PBEnc`,
  used here only to build clauses, not to solve.
- `solvers/hermax/dcp_maxsat.py`, `run.py` and `Dockerfile` in this repository —
  the contract this skill describes.

Every claim below was checked by running it inside the integration image during
the run recorded at `generation/runs/20260922T0100Z-hermax-c9d2`, not taken from
documentation alone.

- **No hermax backend can be time-bounded in process.** `solve(time_limit=...)`
  raises `NotImplementedError: EvalMaxSAT2022 does not support time_limit`, and
  `set_terminate` raises `set_terminate is not implemented by this solver`. The
  same was true of every backend that would instantiate: EvalMaxSATLatestReentrant,
  OLLSolver, the four OpenWBO variants, PartMSU3Solver, RC2, RC2Reentrant, the
  UWrMaxSAT variants and WMaxCDCL. So the runner supervises the search in a
  child process and kills it on budget, which was confirmed by a 16-into-15
  pigeonhole stopping at 60.8 seconds against a 60 second budget.
- `SolveStatus` is `INTERRUPTED(0)`, `INTERRUPTED_SAT(10)`, `UNSAT(20)`,
  `OPTIMUM(30)`, `ERROR(40)`, `UNKNOWN(60)`. Only `OPTIMUM` means the answer is
  proven best, which is what makes honest optimisation reporting possible here.
- `SolveStatus` is an `IntEnum`, and `str()` on one yields the number rather
  than the name under Python 3.11+, so comparisons must use `.name`.
- `add_clause` extends the variable count on its own: a clause over variables
  the solver was never told about took `num_vars` from 0 to 6. So the modelling
  layer can allocate identifiers independently and hand over finished clauses.
  `num_vars` is a property, not a method.
- The solver is genuinely incremental across solve calls: blocking the optimal
  assignment and re-solving returned the next-best cost rather than repeating
  the first answer. That is what optimal-solution enumeration relies on.
- EvalMaxSAT is much faster at pigeonhole than the SAT integration's Glucose: it
  refutes 13 pigeons into 12 holes in about 0.7 seconds, where Glucose already
  needs more than two seconds. The `timeout_cleanup` check therefore uses 16
  into 15 here.
