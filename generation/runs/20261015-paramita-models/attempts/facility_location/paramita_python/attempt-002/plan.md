Warehouses open in the four cities; each open warehouse holds at most max_shipping units. -> open[i] Bool per city; binary integers ship[i][j] = sum of 2^k * bit[i][j][k] (7 bits cover 0..127, enough for capacity 120 and demand 120).
Each region's demand is met by the warehouses together. -> sum over i of ship[i][j] == demands[j], PB over the binary bits.
A warehouse ships only up to its capacity, and only if it is open. -> sum over j of ship[i][j] <= max_shipping * open[i].
If the New York warehouse is opened, then the Los Angeles warehouse must also be opened. -> If(open[NY], open[LA]).
No more than three warehouses can be operational in any given week. -> sum(open) <= 3.
Either the Atlanta or the Los Angeles warehouse must be opened. -> open[Atlanta] | open[LA].
Objective: minimise total cost = fixed costs of open warehouses + shipping cost per unit times units shipped. -> sum fixed[i]*open[i] + sum c[i][j]*2^k*bit[i][j][k] (minimise).
