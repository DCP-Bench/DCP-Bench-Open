Warehouses open in the four cities; each open warehouse holds at most max_shipping units. -> open[i] Bool per city; unary (order) integers ge[i][j][k] = "ships from warehouse i to region j is at least k", value = sum of bits.
Each region's demand is met by the warehouses together. -> sum over i of ships[i][j] == demands[j], PB over unary bits.
A warehouse ships only up to its capacity, and only if it is open. -> sum over j of ships[i][j] <= max_shipping * open[i].
If the New York warehouse is opened, then the Los Angeles warehouse must also be opened. -> If(open[NY], open[LA]).
No more than three warehouses can be operational in any given week. -> sum(open) <= 3.
Either the Atlanta or the Los Angeles warehouse must be opened. -> open[Atlanta] | open[LA].
Objective: minimise total cost = fixed costs of open warehouses + shipping cost per unit times units shipped. -> sum fixed[i]*open[i] + sum c[i][j]*ge[i][j][k] (minimise).
