A Costas array is a pattern of n marks on an n x n grid, one per row and column, whose n(n-1)/2 difference vectors are all different. -> x[1..n] is a permutation of 1..n: distinct(*this, x, IPL_DOM)
the marks are one per row and one per column (permutation of 1..n, 1-based) -> x[i] in 1..n (domain of the output), same distinct as above
for each length l in 1..n-1, the difference triangle has n-l entries X_i - X_{i+l} -> d_l[i] = x[i] - x[i+l] via rel(*this, d == x - y) (linear equality, domain -(n-1)..n-1)
each line of the difference triangle contains no value twice -> distinct(*this, d_l, IPL_DOM) for each l
a difference of two distinct marks is never 0 -> rel(*this, d != 0) on every triangle entry (redundant with distinct on x, cheap pruning)
branching: x first (decides the whole triangle), then the triangle entries -> branch(x, INT_VAR_SIZE_MIN, INT_VAL_MIN); branch(d, ...) for the rest
objective: none (satisfaction)
output costas = x (1-based values)
