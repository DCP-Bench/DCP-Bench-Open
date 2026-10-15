A heterosquare of order n is a n*n square -> cell (i,j) holds one of the values 1..n^2: one-hot Bool x[i][j][v], exactly one value per cell.
whose elements are distinct integers from 1 to n^2 -> each value v used by exactly one cell: sum over cells of x[i][j][v] == 1.
the sums of the rows, columns and diagonals are all different -> row, column and both diagonal sums as PB integer expressions; for every pair of the 2n+2 lines, (S_a < S_b) | (S_a > S_b).
Print a heterosquare (x) of a given order as a list of lists of integers -> outputs x[i][j] = sum(v * x[i][j][v]) over v.
objective -> none (satisfaction).
