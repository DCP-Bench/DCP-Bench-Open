Multi-commodity transportation: origins, destinations, products -> x[i][j][p] shipped amount per origin, destination, product, unary encoded: xs[k] = "amount >= k+1", bounded by min(supply[i][p], demand[j][p], limit[i][j]), order chain If(xs[k], xs[k-1])
Each origin i has a certain supply of each product p -> sum_j x[i][j][p] <= supply[i][p]
Each destination j has a certain demand for each product p -> sum_i x[i][j][p] == demand[j][p]
Lane limit between origin i and destination j (all products together) -> sum_p x[i][j][p] <= limit[i][j]
Objective: minimise the total cost of shipping all products -> sum cost[i][j][p] * (unary units of x[i][j][p]) (linear PB over the unary Bools)
