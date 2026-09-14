Attempt 001 was correct but the integration could not serialise it: this problem
declares `total_population_covered` as an expression, and PuLP's
`LpAffineExpression` is a `dict` subclass, so the runner's shared output helpers
walked into it. The model is unchanged in attempt 002; `solvers/pulp_cbc/run.py`
was repaired and the image re-certified with an `expression_output` check.
