# Plan: csplib_076 Costas arrays
- n marks, one mark per row and one per column -> one-hot X_i (position i, value v): xv[i][v]; sum_v xv[i][v] == 1 per position; sum_i xv[i][v] == 1 per value (permutation)
- the n(n-1)/2 vectors between the marks are all different; each difference-triangle line l (differences X_i - X_{i+l}) has no value twice -> per line l and position i a one-hot Bool D[l][i][d] over d in -(n-1)..(n-1); If(xv[i][u] & xv[j][w], D[l][i][u-w]); sum_d D[l][i][d] == 1; per line l and value d: sum_i D[l][i][d] <= 1
- costas output (1-based list of n values) -> sum_v v * xv[i][v] per position
- objective: none (satisfaction)
