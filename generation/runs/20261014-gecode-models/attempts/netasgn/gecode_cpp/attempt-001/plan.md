Each person i can contribute at most Limit_ij hours to project j -> per-cell upper bound rel(x_ij <= limit_ij), domain 0..limit_ij
Hours are non-negative -> domain lower bound 0
Each person i has exactly Supply_i hours to assign, the total hours assigned from person i equals its supply -> linear(row_i, IRT_EQ, supply_i)
Each project j must get exactly Demand_j hours, the total hours assigned to project j equals its demand -> linear(col_j, IRT_EQ, demand_j)
Minimise the total cost of the assignment, cost per hour Cost_ij times hours assign_ij -> total = expr(sum(IntArgs(cost), x)); minimize(total)
Branching: decide every assign_ij, smallest domain first, smallest value first -> branch(x, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
