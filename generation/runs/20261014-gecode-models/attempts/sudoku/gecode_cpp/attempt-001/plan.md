# Plan: sudoku (attempt-001)

Variables: 81 cells of the solved grid, value 1..9 (grid[r][c] = row r, column c).
- every row contains the digits 1..9 once -> distinct(*this, row, IPL_DOM) for each row.
- every column contains the digits 1..9 once -> distinct(*this, column, IPL_DOM) for each column.
- every 3x3 section contains the digits 1..9 once -> distinct(*this, section, IPL_DOM) for each of the 9 sections.
- every given cell keeps its digit -> rel(*this, cell, IRT_EQ, value) for each non-zero input cell.
- Branching: the grid with INT_VAR_SIZE_MIN and INT_VAL_MIN.
- Objective: none (satisfaction). Output: grid, a 9x9 matrix of rows.
