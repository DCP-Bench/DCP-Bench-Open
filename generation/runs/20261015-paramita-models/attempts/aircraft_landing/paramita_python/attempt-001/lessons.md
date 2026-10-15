Order (unary) bits over a time window of several hundred steps, with pairwise separations as PB sums, exceed 2 GB in to_cnf (memory_limit).
With binary bits the same problem is accepted on all instances; use binary for wide windows that are summed into the objective.
An order-encoded objective with about 5000 unit-weight terms crashes the runner (exit 139) once the optimum is fixed for a second solution (solution limit 2); the same model passes with limit 1.
A left-nested chain of several hundred `+` terms is built without error, but a balanced tree is cheaper to keep as a habit.
