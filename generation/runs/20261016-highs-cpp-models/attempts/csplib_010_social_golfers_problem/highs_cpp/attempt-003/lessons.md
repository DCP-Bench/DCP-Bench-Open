# Lessons: csplib_010_social_golfers_problem, highs_cpp

Attempt-001 (play + one-sided together, no mates row): json:4 and json:5 timed out. json:6 and json:7 solved in ~1-2 s.

Attempt-002 (play + two-sided together per group, mates = s-1): json:4 timed out. json:2 fast. Not evaluated (free-check only).

Free-check variant A (attempt-002 structure with aggregated link `sum_j both = (s-1) play` plus pair-count row per group): json:4 solved in ~90-100 s, json:2 ~100 s, json:6 timed out. The three-row `both` linearisation over n^2/2 * weeks * groups is the cost on the large instance.

Free-check variant B (variant A without the pair-count row): json:4 timed out.

Formulation C (retained, attempt-003): play, one-sided together per (pair, week) with `together >= play_i + play_j - 1` per group, at most one meeting per pair across weeks, and `sum_j together_ij >= s-1` per golfer and week (valid because together dominates the real meeting indicator). Accepted on 7 of 8 instances; json:5 (6 weeks, 5 groups of 3, 15 golfers) still times out at 180 s. Instances checked 7/8 = 0.875, so retained.

Open: json:5 is a search-performance limit for HiGHS on this formulation. A symmetry-breaking row would likely help, but the contract forbids it when the description does not ask for it.
