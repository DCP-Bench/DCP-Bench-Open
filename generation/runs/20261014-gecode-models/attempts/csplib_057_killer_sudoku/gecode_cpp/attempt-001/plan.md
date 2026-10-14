Fill the grid with numbers from 1 to 9 -> one IntVarArray x of 81 cells, domain 1..9 (grid stored row-major, x[9r+c])
Each row, column, and nonet contains each number exactly once -> distinct(*this, row/col/nonet, IPL_DOM) for each of the 9 rows, 9 columns, 9 nonets
The sum of all numbers in a cage must match the small number printed in its corner -> linear(*this, cage_cells, IRT_EQ, sum, IPL_DOM) per cage (cage data from instance field problem)
No number appears more than once in a cage -> distinct(*this, cage_cells, IPL_DOM) per cage
Branching -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) (first fail on the 81 cells)
Objective -> none (satisfaction); output x as 9 rows of 9 values
