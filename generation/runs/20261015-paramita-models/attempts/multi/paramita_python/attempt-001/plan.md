# Plan: multi (attempt-001)

- "shipping from origin i to destination j of product p" -> integer shipment `x[i][j][p]` >= 0, encoded unary (order) because the values are summed and bounded.
- "each origin i has a certain supply of each product p" -> for each (i, p): sum over j of x[i][j][p] <= supply[i][p] (the instance note: supply is the shipped total plus slack).
- "each destination j has a certain demand for each product p" -> for each (j, p): sum over i of x[i][j][p] == demand[j][p] (all demand delivered).
- "limit" field (lane limit, per origin-destination pair across products) -> for each (i, j): sum over p of x[i][j][p] <= limit[i][j].
- "cost of shipping one unit of product p from origin i to destination j is ShippingCost" -> objective `minimize` sum of cost[i][j][p] * x[i][j][p] (linear over the unary bits).
- "minimize the total cost ... Print the optimized cost (total_cost) as an integer" -> output `total_cost` = the same objective expression.
- Upper bound per variable: min(supply[i][p], demand[j][p], limit[i][j]) (a variable is never larger than any of these).
