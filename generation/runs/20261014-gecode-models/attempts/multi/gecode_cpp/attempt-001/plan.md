Origins i, destinations j, products p. x[i][j][p] = units of product p shipped from i to j.

Each origin i has a certain supply of each product p (Supply_{i,p}) -> for each (i,p): sum_j x[i][j][p] <= supply[i][p] (linear, IRT_LQ)
Each destination j has a certain demand for each product p (Demand_{j,p}) -> for each (j,p): sum_i x[i][j][p] == demand[j][p] (linear, IRT_EQ)
Limit on the lane from origin i to destination j (instance field limit, all products together) -> for each (i,j): sum_p x[i][j][p] <= limit[i][j] (linear, IRT_LQ)
Variable domains: x[i][j][p] in 0..min(supply, demand, limit) (tight domains from the data)
The cost of shipping one unit of product p from i to j is ShippingCost_{i,j,p} -> total_cost = sum cost[i][j][p] * x[i][j][p] (sum(IntArgs, IntVarArgs), bounds)
Branching: branch on all x with INT_VAR_SIZE_MIN, INT_VAL_MIN (decisions are the shipments; total follows).
Objective: minimize total_cost.
