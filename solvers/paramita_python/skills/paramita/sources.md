# Sources for `paramita`

- <https://ulog.udl.cat/static/doc/paramita/>: Paramita 1.2.0 documentation
  (how-to SAT and MaxSAT solvers, pools, PB encoding; tutorials on modelling
  decision and optimisation problems; Python API reference).
- <https://codeberg.org/paramita/paramita-plugins> at commit
  `a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb`: the Cadical300, EvalMaxSAT2022,
  pblib and pysat encoder plugins the image builds.
- `solvers/paramita_python/run.py` and `Dockerfile` in this repository: the
  DCP contract.

Every API claim was checked by running it inside `dcp-eval/paramita_python:v1`:
operator forms and reified PB constraints against brute force, the direction
of `add_to_weighted_container`, the default encoder, `val_lit`'s sign
behaviour, the budget support of both solvers, and the stdout lines of
EvalMaxSAT.
