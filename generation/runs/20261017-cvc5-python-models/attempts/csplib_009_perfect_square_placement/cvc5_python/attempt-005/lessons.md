# csplib_009_perfect_square_placement, cvc5_python: lessons

Budget of 5 evaluated attempts used. Not retained: no attempt reached
instances_checked / instances_available >= 0.8 (best was 4/6 = 0.67).

| Attempt | Encoding | Result |
|---|---|---|
| 1 | pairwise four-way `Or` of separations, bounds | accepted, 1/6 checked (old 1-instance profile) |
| 2 | same as 1 with a reworded comment | accepted, 4/6; json:5 and json:6 time out at 180 s |
| 3 | 2 plus area equality and per-row / per-column exact-cover sums | accepted, 4/6; json:5 and json:6 time out |
| 4 | 2 with explicit Boolean selector per separation | accepted, 4/6; json:5 and json:6 time out |
| 5 | cell-by-cell placement Booleans, exact cover of every unit cell | accepted, 2/6; json:3 to json:6 time out |

Evidence:
- json:5 (base 14, 12 squares) never produced a solution in 180 s with any of the
  disjunctive coordinate encodings, so the timeouts are not from the solution limit.
- json:6 (base 30, 19 squares) times out with every encoding tried.
- The placement encoding (attempt 5) is much slower than the coordinate encodings:
  json:3 (11 squares) solved in 5 to 8 s with attempts 2 to 4 and timed out with
  attempt 5.
- Adding the redundant exact-cover sums (attempt 3) did not reduce the json:5 timeout.

Not tried: a different solver logic. The runner fixes the solver settings, so
`SolverFor("QF_LIA")` cannot be chosen from the submission.
