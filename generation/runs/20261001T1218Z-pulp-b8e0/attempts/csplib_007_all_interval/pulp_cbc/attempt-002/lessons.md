Framework lessons from the pulp_cbc chunk (all-interval, graceful graphs, Costas, vessel loading, Hadamard, flip rows/cols, battleships)

1. Differences under an all-different, `|x_i - x_j|` with all values distinct: the encoding that fits
   `sum_v v * pick[i][v]` per position (attempt-001: n=14 and n=20 hit the 180 s limit) is replaced by
   pair variables step[i][(u, v)] in [0, 1] (continuous) tied to the two positions by the marginals
   sum_v step = pick[i][u] and sum_u step = pick[i+1][v], with "each difference d used once" as a sum
   over pairs with |u - v| = d. With pick binary the pair variables are integral on their own.
   Evidence: csplib_007 attempt-001 (timeouts on json:2, json:4) vs attempt-002 (all five instances, longest 44 s);
   csplib_053 attempt-001 (3 of 5 timed out) vs attempt-002 (all five, longest 51 s);
   csplib_076 attempt-001 (3 of 5 timed out) vs attempt-002 (all five, longest 126 s).
2. A parity fact CBC cannot derive can be given as an integer: the number of unlike pairs at a cyclic shift
   is even, so `sum(q) == 2 * h` with `h` Integer. csplib_084 attempt-001 timed out on l=17,
   attempt-002 solves it in 58 s.
3. Packing with separations: choosing a placement (shape, corner) per container and constraining unit cells
   beats four big-M disjunctions per pair on a perfect tiling (csplib_008 attempt-001 timed out on both 16x16
   instances; attempt-003 solves all five). Corners restricted to sums of sides and separations, and cells
   sampled at the gcd of sides and separations, shrink it further.
4. `problem += expr` inside a nested helper raises UnboundLocalError (the augmented assignment makes `problem`
   local): declare `nonlocal problem`. Evidence: csplib_014 attempt-001 execution_error.
5. A product of a +-1 sign and a linear expression with bounded range is linearised exactly per row/column sum
   (four inequalities with M = 2 * reach) instead of one XOR binary per matrix entry: flip_rows_cols attempt-001
   and -002 timed out on the 27x9 example, attempt-003 takes 34 s.
