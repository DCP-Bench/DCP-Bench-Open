# Sources for `paramita`

Tested with Paramita 1.2.0 (PyPI), CaDiCaL 3.0.0 (Cadical300), EvalMaxSAT2022, Python 3.12, Linux.

Existing skills: none found in the earlier integration work.

- <https://ulog.udl.cat/static/doc/paramita/>: Paramita 1.2.0 documentation (how-to SAT and
  MaxSAT solvers, pools, PB encoding; tutorials on modelling decision and optimisation
  problems; Python API reference).
- <https://codeberg.org/paramita/paramita-plugins> at commit
  `a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb`: the Cadical300, EvalMaxSAT2022, pblib and pysat
  encoder plugins; the CMake build recipe in the Install section.

Refactored from an earlier integration skill; examples verified with Paramita 1.2.0 (CaDiCaL 3.0.0, EvalMaxSAT2022).

Independent toy test: 18/18.

Verified by running: the operator forms and reified PB constraints against brute force in the
earlier integration work; the direction of `add_to_weighted_container` (maximises, constant part
plus `benefit()`); the default encoder; `val_lit`'s sign behaviour; the budget support of both
solvers; `cost()` and `benefit()` on a two-clause MaxSAT instance; the Xor, And and Or error
messages; the stack limit of a single 5000-Bool sum (segfault at 8 MB, fine under unlimited stack).
Every example in `assets/` runs and prints its Expected line; the Quick start prints the value in
SKILL.md.
