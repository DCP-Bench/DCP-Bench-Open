Multi-commodity transportation: origins, destinations, products -> x[i][j][p] shipped amount per origin, destination, product, one-hot encoded: xv[v] = "amount equals v" for v in 0..ub, exactly one per triple, ub = min(supply[i][p], demand[j][p], limit[i][j])
Each origin i has a certain supply of each product p -> sum_j sum over v of v*xv[v] <= supply[i][p]
Each destination j has a certain demand for each product p -> sum_i x[i][j][p] == demand[j][p]
Lane limit between origin i and destination j (all products together) -> sum_p x[i][j][p] <= limit[i][j]
Objective: minimise the total cost of shipping all products -> sum cost[i][j][p] * v * xv[v] (linear PB over the one-hot Bools)
