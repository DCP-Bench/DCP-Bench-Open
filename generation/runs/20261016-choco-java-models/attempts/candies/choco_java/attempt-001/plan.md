Problem: candies. n children in a line; each gets at least 1 candy; neighbours with different ratings: higher rating gets more candies; equal ratings: no constraint; minimise total candies.
Each child x_i in 1..n (n = number of children; no child needs more than n) -> intVarArray
Neighbour pair (i, i+1) with ratings r_i > r_{i+1} -> x_i > x_{i+1} (arithm)
Neighbour pair with r_i < r_{i+1} -> x_i < x_{i+1} (arithm)
Neighbour pair with equal ratings -> no constraint
Objective: minimise z = sum of x (m.sum)
