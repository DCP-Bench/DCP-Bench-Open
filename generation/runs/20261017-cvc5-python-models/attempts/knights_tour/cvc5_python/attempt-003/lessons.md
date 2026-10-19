# knights_tour, cvc5_python: lessons from attempts 1 to 3

Evaluation profile: 99 instances, solution_limit 2, 180 s per instance.

- attempt-001 (grid, successor rule `x[i][j] == N-1 or some knight neighbour has x+1`, plus bounds and Distinct): accepted on the 5x5 instance (2.9 s, 2 solutions). The 6x6 example, 8x8, 10x10 and one more instance timed out at 180 s. instances_checked 1 of 5 (0.2), below the 0.8 retain threshold, so not retained.
- attempt-002 (attempt-001 plus a redundant predecessor rule `x[i][j] == 0 or some neighbour has x-1`): worse. Every instance timed out, including 5x5. No instance verified (reason no_instance_verified). The redundant rule slowed cvc5 down.
- attempt-003 (sequence view: row[k], col[k] per step, Distinct over row*n+col, 8-way And disjunction per step, grid output as the inverse via Or over steps): also no instance verified, 5x5 timed out at 180 s.

What it suggests: cvc5 without a global circuit or channelling constraint does not find a Hamiltonian path on boards from 5x5 upward within 180 s. The grid successor encoding of attempt-001 is the fastest of the three, but it is still too slow on 6x6 and larger. Stronger encodings tried here (redundant predecessor, sequence view) did not help. No reformulation was found that passes the 0.8 coverage threshold.

Not verified: whether a longer time limit or a different encoding would pass. The description does not fix the starting square, and the models here do not fix it either.
