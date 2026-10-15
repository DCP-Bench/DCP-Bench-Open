Fill the grid with the digits 1 to 6 -> one-hot Bools xv[r][c][v], sum over v == 1 per cell
Each row contains exactly one of each digit -> per row and digit v: sum over the row's cells == 1
Each column contains exactly one of each digit -> per column and digit v: sum over the column's cells == 1
Each cage achieves its target using one of its operations (the operation is not given) -> per cage one reified flag per candidate operation, Or over the flags
  single-cell cage: the cell equals the target -> xv[cell][target]
  sum (any cage of 2+ cells) -> If(flag, sum of v * xv[cell][v] == target)
  product (any cage of 2+ cells) -> allowed tuples table: one Bool per tuple with product == target, If(tuple, cell values), If(flag, Or(tuples))
  difference (2 cells) -> allowed tuples with |a - b| == target, same table encoding
  exact quotient (2 cells) -> allowed tuples with max == target * min, same table encoding
Print the solved grid x as integers 1..6 -> x[r][c] = sum(v * xv[r][c][v])
Objective: none (satisfaction)
