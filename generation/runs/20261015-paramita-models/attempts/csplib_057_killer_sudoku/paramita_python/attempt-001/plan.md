# Plan: csplib_057_killer_sudoku (attempt-001)

Requirement: fill the grid with numbers from 1 to 9
-> one-hot per cell: xv[r][c][v] Bool, exactly one v per cell (sum == 1); x[r][c] = sum v * xv.

Requirement: each row, column, and nonet contains each number exactly once
-> per row, column, nonet and value v: sum of xv[v] over its cells == 1.

Requirement: the sum of all numbers in a cage must match the small number printed in its corner
-> per cage with target t: sum over its cells of v * xv[v] == t (PB over one-hot Bools).

Requirement: no number appears more than once in a cage
-> per cage and value v: sum of xv[v] over its cells <= 1.

Requirement: print the solution matrix x as a list of lists of integers 1..9
-> output x[r][c] = integer expression of cell value.

Objective: none (satisfaction).
