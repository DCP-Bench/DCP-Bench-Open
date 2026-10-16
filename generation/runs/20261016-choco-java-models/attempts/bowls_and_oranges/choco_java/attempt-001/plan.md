Place all m oranges in n bowls at positions 1..n, no more than one orange per bowl -> x_i in 1..n, strictly increasing (distinct and ascending, arithm(x_i, "<", x_{i+1})).
No three oranges A, B, C with dist(A,B) = dist(B,C) -> for every bowl a and step d >= 1 with a+2d <= n, the three bowls a, a+d, a+2d hold at most two oranges: occ_p = count(p, x) (0/1), occ_a + occ_{a+d} + occ_{a+2d} <= 2.
Objective: none (satisfaction). Output x, the bowls in ascending order.
