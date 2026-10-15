# Plan: csplib_009 perfect square placement (Paramita, unary coordinates)

Pack squares of sides s_i into a base x base square, no overlap, no spare capacity.
- Pack squares of given integer sizes into a bigger square -> x_i, y_i in 0..base-s_i, integers encoded unary: xge[i][k] = (x_i >= k), chain If(xge[k+1], xge[k]), x_i = sum(xge[i]).
- No two squares overlap -> per pair (i,j): Or of four placement Bools: i left of j, j left of i, i below j, j below i.
- i left of j -> If(left_ij, x_i + s_i <= x_j) (PB over unary bits, weights 1).
- Same for vertical with y coordinates.
- Squares use all the area -> implicit by the instance (sum s_i^2 = base^2); no extra constraint in v1.
- Output x_coords, y_coords -> the unary sums (integer expressions, 0-based).
- Satisfaction problem, no objective.
