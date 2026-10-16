# big_bang2 (maxicp_java) lessons

- attempt-001: execution_timeout at 180 s, no solution found, every instance inconclusive.
- attempt-002: adds a shift symmetry break (some face equals 1) and redundant
  "loser wins in at most 17 of 36 pairs" constraints. Still execution_timeout at 180 s,
  no solution. A free check of the same bytes before evaluation also timed out.
- Encoding: 30 face variables in 1..12, ten reified 36-pair count constraints. Plain DFS
  with firstFailBinary and no learning does not reach a solution within the limit.
- Not tried: a symmetry break on face order within a die (the contract asks for no
  ordering the description does not state), and different channelling of the comparisons.
- Verdict: a performance limit of this encoding, not retained.
