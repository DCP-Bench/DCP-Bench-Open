Hidato: fill the R x C grid with the numbers 1..R*C so that each number touches the next one (horizontally, vertically or diagonally); some numbers are given.
Every cell gets a number from 1 to R*C (sizes from the instance), so the numbers form a permutation of the cells.
Cell values x (cell -> number) and their inverse y (number -> cell) -> channel(*this, x, 1, y, 1) [both 1-based, one-to-one]
Given numbers in the grid are fixed -> rel(*this, x[cell] == v)
Each number v and v+1 touch: the cell rows differ by at most 1 -> rel(*this, abs(row[v] - row[v+1]) <= 1), with row[v] = element(IntArgs(rowOf), y[v]) [table indexed by cell number]
Each number v and v+1 touch: the cell columns differ by at most 1 -> rel(*this, abs(col[v] - col[v+1]) <= 1), with col[v] = element(IntArgs(colOf), y[v])
Branching: decide the cells of the numbers (y) with INT_VAR_SIZE_MIN, the smallest domain first; x follows from channel. Restarts for heavy-tailed search.
No objective (satisfaction).
