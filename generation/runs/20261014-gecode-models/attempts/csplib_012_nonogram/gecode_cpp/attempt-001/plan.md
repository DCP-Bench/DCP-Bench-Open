Shade in squares in a grid -> cell = IntVarArray(rows*cols, 0, 1), board output as Matrix<IntVarArray>(cell, cols, rows); 1 = shaded
blocks of consecutive shaded squares satisfy the constraints given for each row -> per row: extensional(*this, row_cells, DFA(clue)) where clue = *0 (1^b1 0+ 1^b2 ...) *0 built with REG (blocks = nonzero clue entries, in order; zero padding dropped)
constraints given for each column -> per column: extensional(*this, col_cells, DFA(clue)) as above (a decomposition is not used: the pattern is a regular language, so the DFA row is the map's pattern row)
the sequence of shaded blocks (e.g. 3,1,2) -> the REG concatenation with a single gap of 0+ between blocks, leading and trailing gap 0*
print the solution board as list of lists -> output("board", board)
branching -> branch on cell with INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN(); restarts(100)
objective -> satisfaction, none
