# Lessons: csplib_032_max_density_still_life, eclipse_clp

Budget of 5 attempts used. Not retained: instances_checked 2 of 3 (0.67), below the 0.8 bar.

- Formulation: padded (n+2) x (m+2) board of 0/1 variables, border fixed to 0, each cell
  reified with `(V #= 1) => (S #>= 2 and S #=< 3)` and `(V #= 0) => (S #\= 3)`, S the sum of the
  eight neighbours. Accepted on the 6x6 and 7x7 instances in every variant.
- The 8x8 instance (json:2, optimum 36) is the only one not checked. It times out in the
  optimum phase (attempt-001, 003) or in search (attempt-005, first solution found but optimum not
  proven within 180 s).
- Attempt-002 (gfd, first_fail/indomain_max): timed out on the 6x6 example (no optimum in 180 s).
- Attempt-004 (gfd, input_order/indomain_max): timed out on the 6x6 example.
- Attempt-003 (ic, input_order/indomain_max): 7x7 in 17 s, 8x8 timeout.
- Attempt-005 (ic, first_fail/indomain_max): 7x7 in 21 s, 8x8 timeout.
- Attempt-001 (ic, default labelling): 7x7 in 33 s, 8x8 timeout.
- Not tried: redundant implied constraints on row or column counts, or a different cell
  ordering with a split search. Those are the next candidates for a longer budget.
- Commands: `evaluation.check` with `--execution-timeout 180` is the same budget as the profile,
  so an 8x8 check costs the full 3 minutes.
