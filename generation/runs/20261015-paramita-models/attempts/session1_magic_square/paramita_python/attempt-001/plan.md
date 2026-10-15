A magic square is an n x n grid (n != 2) -> n is the instance field; grid size n x n
each cell contains a different integer from 1 to n^2 -> one-hot per cell (x[i][j][v], exactly one v), each value v in exactly one cell (PB sum == 1)
the sum of the integers in each row ... is equal -> row sums: sum(v * x[i][j][v]) over the row == S
... each column ... is equal -> column sums: same PB over the column == S
... each diagonal ... is equal -> both diagonals (i == j and i + j == n-1): PB == S
sum of integers of each row, column and diagonal has to be equal to n(n^2+1)/2 -> S = n*(n^2+1)//2 as a constant right-hand side
Print the magic square as a list of lists (square) -> output square[i][j] = integer expression sum(v * x[i][j][v])
objective: satisfaction (no objective)
