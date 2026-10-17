# Lessons: csplib_006_golomb_rulers, cvc5_python

Both attempts are accepted on the instances that finished, with no counterexample. Neither reaches 4 of 5 (threshold 0.8), so neither is retained.

- Attempt 1: marks as Ints, mark_0 == 0, strict ordering, Distinct over all pairwise differences, minimise the last mark. Checked 2 of 5 (json:3 optimum 11, json:4 optimum 25). Timed out at 180 s on example (size 10, optimum 55), json:1 (size 8, optimum 34) and json:2 (size 9, optimum 44).
- Attempt 2: adds the implied triangular lower bounds marks[i] >= i(i+1)/2. Same result, 2 of 5 checked. json:1 found the optimal 34 but could not prove it within 180 s. Example and json:2 timed out with no solution reported.

Reading: the bottleneck is proving optimality for size 8 and above, not the constraint encoding. The bound from distinct gaps did not change the proof time. The remaining options are a different encoding of the distance constraints (for example occupancy Booleans over positions, which needs a fixed upper bound on the length) or a different search strategy, which the integration cannot select. No reference was read.
