# csplib_014_solitaire_battleships with clingo_asp

The instance has a field named `_SHIP`. `solvers/clingo_asp/run.py` `predicate()` lowers only the
first character, which is `_`, so the runner writes the fact `_SHIP(1).` In clingo an
identifier that starts with underscores followed by a capital is a variable, so the fact does not
parse. Attempt 002 is a program with no rules; it fails with `parsing failed` raised from
`control.add(...)` in run.py before any solving, so the failure does not depend on the model
(evaluation.json, `detail` and the traceback in the instance `stderr`).
Attempt 001 (the full model) fails the same way.

Pair is a blocker candidate for the integration, not for a model.
