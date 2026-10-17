# csplib_009_perfect_square_placement, highs_cpp: lessons (retry, attempts 005 and 006)

Neither attempt was evaluated (`generation.manage evaluate`); both were run with free checks only.
Nothing retained. Earlier best: 4/6 (attempt-004), below the 0.8 bar.

No symmetry breaking (the description asks for none, solvers/CONTRACT.md), so unlike attempt-004
neither model anchors the largest square or orders equal squares.

- attempt-005: one-hot x and y positions per square (X, Y), span columns cx/cy per unit line,
  z[i][u][v] = cx AND cy with z <= cx, z <= cy, z >= cx + cy - 1 and sum_i z = 1 per cell,
  line-cover rows, and positions restricted to subset sums of the other sides.
  Free check, solution limit 2, 180 s: example, json:1, json:3, json:4 accepted (9 to 39 s wall,
  13 s of it compilation). json:5 times out. With solution limit 1 and a 900 s limit json:5 still
  times out.
- attempt-006: exact cover over placements p[i][a][b] (subset-sum positions only), X and Y
  marginal binaries tied by equality rows, line-cover rows over the marginals, coordinates as
  integer columns. json:5 with solution limit 1 and a 900 s limit: execution_timeout.

Conclusion: json:5 (base 30, 19 squares) is not solved by HiGHS 1.15.1 in 900 s with either an
exact-cover or an indicator-product formulation, so the 180 s budget is out of reach without
symmetry breaking. json:6 (base 112) is larger still (cell count 12544; exact cover is over the
2048 MB limit and the z product needs about 790k rows). Treat the problem as a performance limit
for this integration at 4/6 instances.

Untried: per-line knapsack pattern columns (subsets of sides summing to base), which tighten the
LP but add thousands of columns per line; no evidence they fix the search.
