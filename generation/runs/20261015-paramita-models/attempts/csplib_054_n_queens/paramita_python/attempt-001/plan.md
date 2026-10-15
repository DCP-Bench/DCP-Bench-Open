Can n queens be placed on an n x n chessboard so that none of the queens can attack each other -> q[i][c] one-hot grid over rows and columns (no symmetry breaking)
no two queens on the same row -> per row i, sum_c q[i][c] == 1
no two queens on the same column -> per column c, sum_i q[i][c] == 1
no two queens on the same diagonal (anti-diagonal i + c constant) -> per s, sum of q over cells with i + c == s <= 1
no two queens on the same diagonal (diagonal i - c constant) -> per d, sum of q over cells with i - c == d <= 1
Print the positions of the queens (queens), column of the i-th row, 1-based -> output queens[i] = sum_c (c+1)*q[i][c]
objective: satisfaction (no objective)
