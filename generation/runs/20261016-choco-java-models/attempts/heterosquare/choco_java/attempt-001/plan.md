Problem: heterosquare of order n (n x n square, distinct integers 1..n^2, all row, column and diagonal sums pairwise different).

- "elements are distinct integers from 1 to n^2" -> x[i][j] in 1..n*n, allDifferent over all n*n cells (AC)
- "sums of the rows ... are all different" -> one sum variable per row, sum(row_i) (m.sum named)
- "sums of the columns ... are all different" -> one sum variable per column
- "sums of the diagonals ... are all different" -> two sum variables, main and anti diagonal
- "sums of rows, columns and diagonals are all different" -> allDifferent over the 2n+2 sum variables (AC)
- "Print a heterosquare (x)" -> output x as IntVar[n][n]
- objective: none (satisfaction)
