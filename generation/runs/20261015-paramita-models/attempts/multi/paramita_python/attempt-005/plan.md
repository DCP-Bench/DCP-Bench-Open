Units shipped from origin i of product p to destination j (x[i][j][p]) -> integer, binary bits with weights 2^k; no separate upper-bound rows (supply, demand and lane rows already bound it, attempt 4 bound rows did not help)
Each origin ships no more than its supply of each product -> sum_j x[i][j][p] <= supply[i][p]
Each destination receives exactly its demand of each product -> sum_i x[i][j][p] == demand[j][p]
The lane between origin i and destination j carries at most limit[i][j] units over all products -> sum_p x[i][j][p] <= limit[i][j]
Total shipping cost of all products -> objective sum(cost[i][j][p] * x[i][j][p]), minimise
