# Sources for `cvc5-python`

Tested with cvc5 1.4.2 (pip package `cvc5`), Python 3.12, Linux x86-64, in the image `dcp-eval/cvc5_python:v1`.

Existing skills: none found. `npx skills find cvc5` failed (the CLI needs a newer Node than 20.19.2), and a GitHub code search for `filename:SKILL.md cvc5` returned nothing.

- <https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html>: `cvc5.pythonic` API, term builders, `Solver`, `SolverFor`, models
- <https://cvc5.github.io/docs/cvc5-1.4.2/options.html>: option names and defaults (`tlimit-per`, `nl-ext`, `arith-prop`, `arith-brab`, `sat-random-seed`, `incremental`, `produce-models`)
- <https://pypi.org/project/cvc5/>: pip package

Verified by running: every example in `assets/` (`python model.py` gives the `Expected` line); the error texts in Common issues (triggered in probes); the timing table in Performance (probe runs in the image, 60 s limit per check); the snippets in Modelling (reification, `Bools` and `Ints` with lists, `Xor`, `Implies`, cardinality with `Sum(If(...)) == k`, `Or` over a list, `model()` on an unused variable, `model()` without `produce-models`).
