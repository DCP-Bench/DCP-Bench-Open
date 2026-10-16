A 0/1 matrix is x-rayed by rows and columns: the number of ones in each row and column is given.
  -> BoolVar matrix x[r][c] (rows = len(row_sums), cols = len(col_sums))
Reconstruct the contents of the matrix from the row sums.
  -> row r: m.sum(x[r], "=", row_sums[r]) posted
Reconstruct the contents of the matrix from the column sums.
  -> column c: m.sum(column c of x, "=", col_sums[c]) posted
Print the solution matrix with 0 and 1 as a list of lists.
  -> output matrix = x
Satisfaction problem: no objective.
