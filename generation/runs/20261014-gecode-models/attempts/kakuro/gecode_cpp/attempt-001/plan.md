Kakuro: insert a digit from 1 to 9 into each white cell -> IntVarArray of n*n cells with domain 1..9 for white cells (cells not in blanks), fixed to 0 for blank cells (rel x == 0)
each clue's entries and sum: a clue sum matches its entries -> linear(*this, cells, IRT_EQ, clue) per clue (across and down)
no digit is duplicated in any entry -> distinct(*this, cells, IPL_DOM) per clue
branching: all cells, first fail on size, values ascending -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
objective: none (satisfaction) -> no minimize
output: x as n x n matrix with 0 for blank cells -> output("x", Matrix<IntVarArray>)
