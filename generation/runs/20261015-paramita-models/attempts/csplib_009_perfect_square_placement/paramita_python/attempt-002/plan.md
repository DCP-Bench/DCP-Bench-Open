# Plan: csplib_009 perfect square placement, attempt 2 (pure order-clause separation)

Attempt 1 hit the 2 GB limit on the base-112 instance (PB constraints of ~224 unary terms, 840 of them).
- Square i lies inside the base -> unary coordinate x_i >= k (bits), domain 0..base-s_i, chain If(bits[k+1], bits[k]).
- Square i left of square j, with x_i + s_i <= x_j -> for every k: (x_i >= k) implies (x_j >= k + s_i). Pure clauses, no PB.
- Each pair (i, j) is separated horizontally or vertically -> Or of four placement Bools (left, right, below, above).
- Same for y coordinates with below/above.
- Output x_coords, y_coords -> unary sums (integer expressions, 0-based).
- Satisfaction problem, no objective.
