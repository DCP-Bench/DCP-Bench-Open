Multi-commodity transportation: origins, destinations, products -> x[i][j][p] shipped amount per origin, destination, product, binary encoded with nbits = bit_length of min(supply[i][p], demand[j][p], limit[i][j])
Each origin i has a certain supply of each product p -> sum_j x[i][j][p] <= supply[i][p]
Each destination j has a certain demand for each product p -> sum_i x[i][j][p] == demand[j][p]
Lane limit between origin i and destination j (all products together) -> sum_p x[i][j][p] <= limit[i][j]
Objective: minimise the total cost of shipping all products -> sum cost[i][j][p] * x[i][j][p] (binary bit weights)
