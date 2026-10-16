Set up: origins Origins (supply rows), destinations Destinations (demand rows), products Products; shipment x[i][j][p] >= 0 per origin, destination, product.
Each origin i has a certain supply of each product p Supply_{i,p} -> for each i,p: sum_j x[i][j][p] <= supply[i][p]
Each destination j has a certain demand for each product p Demand_{j,p} -> for each j,p: sum_i x[i][j][p] = demand[j][p]
(lane limit, implied by the instance field limit[i][j]) -> for each i,j: sum_p x[i][j][p] <= limit[i][j]
Shipping cost of one unit of product p from origin i to destination j is ShippingCost_{i,j,p} -> total_cost = sum cost[i][j][p] * x[i][j][p] (scalar)
Objective: minimize the total cost of shipping all products -> minimize total_cost
Output: total_cost (int)
