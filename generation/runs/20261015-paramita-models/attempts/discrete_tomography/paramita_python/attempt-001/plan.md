A matrix which contains zeroes and ones -> x[i][j] = Bool, one per cell (direct, no integer encoding)
gets "x-rayed" horizontally, giving the total number of ones in each row -> sum(x[i]) == row_sums[i] (PB, unit weights)
gets "x-rayed" vertically, giving the total number of ones in each column -> sum(x[:][j]) == col_sums[j] (PB, unit weights)
Print the solution matrix with 0 and 1 (matrix) as a list of lists -> outputs matrix[i][j] = 1 * x[i][j]
Objective: none (satisfaction)
