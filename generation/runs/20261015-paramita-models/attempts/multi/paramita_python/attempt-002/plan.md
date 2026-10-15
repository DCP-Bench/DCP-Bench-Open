# Plan: multi (attempt-002)

Attempt-001 (unary shipments) timed out on 2 of 5 instances: the optimum was not proven in 180 s.
Change of encoding: binary shipments.

- "shipping from origin i to destination j of product p" -> integer x[i][j][p] >= 0, binary encoded (bit k weighs 2^k), with an explicit `x <= ub` PB bound, ub = min(supply, demand, limit).
- "each origin i has a certain supply of each product p" -> for each (i, p): sum over j of x[i][j][p] <= supply[i][p].
- "each destination j has a certain demand for each product p" -> for each (j, p): sum over i of x[i][j][p] == demand[j][p].
- "limit" (lane limit over all products) -> for each (i, j): sum over p of x[i][j][p] <= limit[i][j].
- "cost of shipping one unit of product p from origin i to destination j" -> objective `minimize` sum of cost[i][j][p] * x[i][j][p] (weights cost * 2^k per bit).
- "Print the optimized cost (total_cost) as an integer" -> output `total_cost` = the same objective expression.
