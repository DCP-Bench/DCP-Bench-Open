# Plan: sudoku

- "fill a 9x9 grid with numbers" -> one-hot Bools x[r][c][v] for v in 1..9, `sum(x[r][c]) == 1` per cell; grid[r][c] = sum(v * x[r][c][v]) (int output)
- "each row contains all the digits between 1 and 9" -> per row r and digit v: `sum(x[r][c][v] for c) == 1`
- "each column contains all the digits between 1 and 9" -> per column c and digit v: `sum(x[r][c][v] for r) == 1`
- "each 3x3 section contains all the digits between 1 and 9" -> per box and digit v: `sum over 9 cells == 1`
- "input is a grid with some cells filled with numbers" (input_grid, 0 = empty) -> per clue cell with value v: `x[r][c][v] == 1` (unit clause)
- "Print the solved grid (grid)" -> output grid as nested lists of integer expressions
- objective -> none (satisfaction)
