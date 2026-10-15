Units shipped from origin i of product p to destination j (x[i][j][p]) -> integer 0..min(supply[i][p], demand[j][p], limit[i][j]), unary bits x_i_j_p_ge_k with If(ge_{k+1}, ge_k)
Each origin ships no more than its supply of each product -> sum_j x[i][j][p] <= supply[i][p]
Each destination receives exactly its demand of each product -> sum_i x[i][j][p] == demand[j][p]
The lane between origin i and destination j carries at most limit[i][j] units over all products -> sum_p x[i][j][p] <= limit[i][j]
Total shipping cost of all products -> objective sum(cost[i][j][p] * x[i][j][p]), minimise
