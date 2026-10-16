Each person i has a number of available hours Supply_i; the total hours assigned from person i equals its supply -> sum_j x[i][j] == supply[i] over unary bits of x[i][j]
Each project j requires a number of hours Demand_j; the total hours assigned to project j equals its demand -> sum_i x[i][j] == demand[j] over unary bits
Person i can contribute to project j up to a maximum limit Limit_ij -> x[i][j] has only limit[i][j] unary bits (value <= limit)
Hours x[i][j] are integers, order bits: bit k+1 implies bit k -> unary encoding, x[i][j] = sum of bits
Minimise the total cost of assigning hours, sum Cost_ij * x[i][j] -> weighted sum of unary bits, minimise
