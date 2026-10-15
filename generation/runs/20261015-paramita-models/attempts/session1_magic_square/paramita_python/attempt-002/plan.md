A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 -> one-hot cell values: x_i_j_v for v in 1..n^2, exactly one value per cell, each value used once over all cells (permutation).
the sum of the integers in each row, column and diagonal is equal -> for each row i: sum_j,v v * x_i_j_v == M, and for each column j likewise.
the sum of integers of each row, column and diagonal has to be equal to n(n^2+1)/2 -> M = n(n^2+1)/2 for each line.
Diagonal -> main diagonal and anti-diagonal (cells (i,i) and (i,n-1-i)) each sum to M.
Print the magic square as a list of lists (square) -> outputs square[i][j] = sum_v v * x_i_j_v (integer expression).
Satisfaction problem -> no objective.
