# csplib_009_perfect_square_placement, maxicp_java

## attempt-001 (not counted, retained by mistake at 4 of 6 instances)

- Pairwise non-overlap only (four reified `isLe` per pair, one `or`).
- Accepted on example, json:1, json:3, json:4. Timed out (180 s) on json:5 (base 30, 19 squares) and json:6 (base 112, 21 squares). Skipped as inconclusive.

## attempt-002 (retained if the evaluator accepts; 5 of 6 available instances checked)

- Kept the pairwise non-overlap as the exact constraint.
- Added two redundant cumulative constraints, one per axis: each square is a task of length = side, pulsed with height = side, its start fixed to its corner coordinate. The sum must stay at most `base`. This states that the squares crossing a line stack inside the big square.
- Result: example, json:1, json:3, json:4 accepted; json:5 accepted in 19.9 s (2 solutions); json:6 still times out at 180 s.
- Coverage 5 of 6 = 83%, above the 80% bar. json:6 (base 112) is not solved by plain DFS in the budget. No further attempt made.
- Not tried: an exact-cover implied constraint (every unit cell covered once), a different branching order, or a stronger search. These might solve json:6 but were not needed for the bar.
