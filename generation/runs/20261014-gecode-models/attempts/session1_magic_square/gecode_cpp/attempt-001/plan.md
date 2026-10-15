A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2
  -> distinct(*this, cells, IPL_DOM) over the n*n cells with domain 1..n*n (n*n distinct values in n*n cells = a permutation)
the sum of the integers in each row is equal to n(n^2+1)/2
  -> linear(*this, row_r, IRT_EQ, S) for each row, S = n(n^2+1)/2 computed from the instance field n
the sum of the integers in each column is equal to n(n^2+1)/2
  -> linear(*this, col_c, IRT_EQ, S) for each column
the sum of the integers in each diagonal is equal to n(n^2+1)/2
  -> linear(*this, main_diagonal, IRT_EQ, S) and linear(*this, anti_diagonal, IRT_EQ, S); for n = 1 both are the same single cell, which is fine
branching: cells in row-major order, first-fail variable choice, minimum value; restarts with AFC branching if time runs out
objective: none (satisfaction); output "square" as the n rows of the grid
