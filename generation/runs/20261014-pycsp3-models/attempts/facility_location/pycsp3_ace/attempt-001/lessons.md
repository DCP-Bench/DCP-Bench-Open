pycsp3 exits with SystemExit: 1 and no stderr when a constraint has a constant left side, e.g. sum(demands) <= max * Sum(open), or a Var built inside a list comprehension ([[Var(...) for ...]]). The check reports execution_error 'SystemExit: 1'.
Use Sum over variables only, and declare Var/VarArray on their own lines.
