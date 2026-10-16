# Plan: candies attempt-001

Alice gives at least 1 candy to each child -> candies x_i = 1 + sum of unary Bools b[i][k] (k in 1..n-1, b[i][k] means x_i > k), so x_i >= 1 by construction
Children next to each other: the child with the higher rating gets more candies -> per neighbour pair with ratings a > b: x_left >= x_right + 1 (PB over the integer expressions)
equal ratings next to each other -> no constraint
order of unary bits (x_i > k+1 implies x_i > k) -> If(b[i][k+1], b[i][k]) (removes symmetry, no other effect)
upper bound x_i <= n (derived: an optimal allocation gives each child at most the length of its longest monotone chain, which is at most n) -> the unary bits stop at n-1
minimise the total number of candies -> objective z = sum of x_i, minimise
output z -> same expression as the objective
output x -> the list of integer expressions x_i
