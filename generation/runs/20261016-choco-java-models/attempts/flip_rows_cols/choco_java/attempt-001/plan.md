Problem: flip_rows_cols. Flip signs of whole rows and columns; every row and every column must sum to >= 0; minimise the overall sum.
Each row sign row_signs[i] in {-1,1} -> IntVar with domain {-1,1}
Each column sign col_signs[j] in {-1,1} -> IntVar with domain {-1,1}
Sign of cell (i,j) after flips p_ij = row_signs[i] * col_signs[j] -> m.times(row_signs[i], col_signs[j], p_ij)
Cell value after flips f_ij = a_ij * p_ij -> m.scalar([p_ij], [a_ij], "=", f_ij)
Every row sums to a positive number or zero -> m.sum(f row i, ">=", 0)
Every column sums to a positive number or zero -> m.sum(f column j, ">=", 0)
Objective: overall sum of the flipped matrix -> m.sum(all f_ij), minimised
Output: row_signs, col_signs (IntVar arrays)
