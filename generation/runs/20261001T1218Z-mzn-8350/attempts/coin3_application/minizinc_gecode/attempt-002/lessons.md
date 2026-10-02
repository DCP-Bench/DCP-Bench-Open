# Lessons (minizinc_gecode, coin3_application)

attempt-001 chose, for every amount, how many coins of each kind pay it (`pay[a, i]`).
Those variables are not outputs, so after the optimum was fixed the enumeration of
optimal outputs ran through every equivalent choice of `pay`: the example and json:1
ended in `execution_timeout` (1 of 5 instances without any solution).
attempt-002 computes payability kind by kind with a functional table, so only `x` is free,
and all 5 instances are accepted (largest execution time 11.9 s).
See also broken_weights attempt-003/lessons.md.
