# Lessons: csplib_032_max_density_still_life, cvc5_python

Attempt 001 (Boolean cells, If-sum neighbour counts, Or/Implies rules): accepted, 2 of 3
instances checked (example 18 and json:1 28 optimal in 9 s and 57 s). json:2 (8x8, optimum 36)
timed out at 180 s during the optimisation proof. 2/3 is below the 0.8 retain threshold.

Attempt 002 (Int 0/1 cells, linear neighbour sums, big-M rules, Or of linear bounds):
accepted on the example only (18 in 88 s). json:1 and json:2 timed out. Worse than 001.

Conclusion: the bottleneck is cvc5's tighten-and-prove-unsat optimisation on the 7x7 and
8x8 instances, not the encoding. Neither formulation reached 0.8 coverage. No
retained model. Redundant constraints were not tried because a valid implied
constraint for still lifes is not obvious from the description alone.
