Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount -> minimise sum of x_i (x_i = number of coins of denomination i)
Denominations in the instance, x_i is the count of coin i -> unary Bools x_ge_i_k (k = 1..u_i, u_i = (max-1)//d_i, ordered by If), x_i = sum of them
Count bound u_i: an optimal solution never uses more coins of one type than the largest amount needs -> u_i = (max-1)//d_i
Each amount a in 1..max-1 can be paid exactly -> for each a, Bools p_a_i_k (k = 1..a//d_i) with sum over i of d_i * (sum_k p_a_i_k) == a
Only the coins of amount a that are actually used count: sum_k p_a_i_k <= x_i -> PB comparison per a and i
Objective: minimise total number of coins -> ("minimize", sum of x_i)
Output x: list of the six integer counts x_i
