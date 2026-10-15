Each row of the grid contains exactly one of each digit 1..n -> distinct(*this, row, IPL_DOM) per row
Each column contains exactly one of each digit 1..n -> distinct(*this, col, IPL_DOM) per column
Each cage with one cell: the cell equals the cage target -> rel(*this, cell == t)
Each cage: its digits achieve the target by some operation (operation not given in the instance) -> clause(*this, BOT_OR, options, BoolVarArgs(), 1) over reified options:
  sum of the cage equals t -> expr(*this, sum(cells) == t) (any size)
  product of the cage equals t -> expr(*this, prod == t), prod a chain of expr(*this, a * b) (any size)
  two-cell cage only: |a - b| == t -> expr(*this, abs(a - b) == t)
  two-cell cage only: a == t * b, or b == t * a (exact quotient) -> rel via expr
  Use a decomposition only where no map row fits: the reified sums and products are the map rows (linear/mult with reification) for a disjunction over operations; say why on this line.
Branching: branch on all grid cells in order of smallest domain first (INT_VAR_SIZE_MIN), smallest value first (INT_VAL_MIN).
Objective: none (satisfaction). Outputs: x as a 6x6 matrix, row by row.
