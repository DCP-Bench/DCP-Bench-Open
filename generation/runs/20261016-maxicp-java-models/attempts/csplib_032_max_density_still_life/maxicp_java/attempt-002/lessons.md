# csplib_032 max density still life, maxicp_java: lessons

Outcome: not retained. Both evaluated attempts are accepted on the example (n=m=6, optimum 18) and on json:1 (7x7, optimum 28), and both time out on json:2 (8x8, optimum 36) at the 180 s execution limit. Checked 2 of 3 available instances, below the 80% retention threshold, so this is a performance limit, not a retained model.

Attempt 001 (reified sums): a dead cell is not exactly 3 live neighbours, a live cell has 2 or 3. Each board cell reifies `isEq(sum, 3)`, `isLe(sum, 1)`, `isLe(4, sum)` and posts implications. Evaluation: accepted, skipped json:2 as execution_timeout.

Attempt 002 (one table per cell): a table over the centre and its 8 neighbours, 9 Boolean columns, valid tuples generated from the two rules. Free checks: 6x6 and 7x7 accepted in about 2.5 s and 12 s; 8x8 timed out at 179 s with no solution reported. Evaluation: same result as attempt 001 on json:2.

Evidence that the cost is the optimality proof: both encodings find solutions quickly, while the 8x8 search cannot close the bound to 36 within the limit. Neither encoding gives a stronger bound on the objective.

Untried: implied redundant constraints that are derivable from the rules (not symmetry breaking), and a stronger objective-side bound. Neither was derived in this attempt, so they are not claimed to work.
