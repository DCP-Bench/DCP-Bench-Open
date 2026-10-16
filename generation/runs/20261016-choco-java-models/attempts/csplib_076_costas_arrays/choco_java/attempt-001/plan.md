A Costas array: n marks on an n x n grid, one per row and column, all vectors between marks different.
  -> X_1..X_n a permutation of 1..n: allDifferent(X, "AC")
For each length l in 1..n-1, the difference triangle X_i - X_{i+l} (i in 1..n-l) has no value twice.
  -> per l, IntVar row D_l[i] = X_i - X_{i+l} via arithm(D, "=", X_i, "-", X_{i+l}); allDifferent(D_l, "AC")
Print the Costas array as n integers, 1-based.
  -> output costas = X
Satisfaction problem: no objective.
