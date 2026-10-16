Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount -> minimise the total of x_i (x_i = number of coins of denomination i), output x as the six counts
Number of coins of each type: unary Bools x_i_ge_k (k = 1..u_i, u_i = (max-1)//d_i), ordered by If, x_i = sum of them
Using a given set of denominations: reachability over the denominations, one Bool per (j, v): value v is paid exactly by the first j denominations with counts within x -> r_j_v <-> OR over k of (r_(j-1)_(v - k*d_j) and x_i >= k), a clause-level DP instead of weighted PB sums
Every amount from 1 to max-1 can be paid exactly -> r_m_a true for each a
Objective: minimise the total number of coins -> ("minimize", sum of x_i)
