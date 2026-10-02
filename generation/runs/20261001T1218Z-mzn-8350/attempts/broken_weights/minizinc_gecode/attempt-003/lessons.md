# Lessons (minizinc_gecode, broken_weights)

Auxiliary variables that are not declared outputs can make a satisfaction problem
look like an `execution_timeout` even when the model is right. The runner
enumerates solutions of the whole model and drops those whose declared outputs repeat.
When many assignments of the auxiliary variables give the same outputs, finding a
second distinct output means walking through all of them first.

Evidence (same instance, json:3, m = 80, n = 5):
- attempt-001 (placement variables x[i, j] as in the reference): first solution found,
  second not found in 180 s (`execution_timeout`, 1 solution).
- attempt-002 (reachability table with `reach[j, v]`): no solution in 181 s.
- attempt-003 (all 3^n placements listed once, `exists` over them): both solutions in 6.2 s,
  all 5 instances accepted.

Applies to any pair whose model carries free helper variables that are not outputs
(coin3_application attempt-001 had the same problem: attempt-002 removes the helper choices).
