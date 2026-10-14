Can n queens be placed on an n x n board so that no queen attacks another?
no two queens share a row (one queen per row, by the position of the queen in row i) -> the array indexes rows, so each queen is in its own row
no two queens share a column (the value queens[i] is the column, 1..n) -> distinct(*this, queens, IPL_DOM)
no two queens on the same diagonal (going up-right: column + row) -> distinct(*this, IntArgs(up offsets i), queens, IPL_DOM)
no two queens on the same diagonal (going down-right: column - row) -> distinct(*this, IntArgs(down offsets -i), queens, IPL_DOM)
branching: queens in row order, smallest domain first, smallest column first -> branch(*this, queens, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective: none (satisfaction)
