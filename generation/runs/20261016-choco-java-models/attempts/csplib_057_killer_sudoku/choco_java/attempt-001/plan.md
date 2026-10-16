# Plan: killer sudoku (csplib_057)

Grid x[9][9] of digits 1..9 (n from the instance).

- Each row, column, and nonet contains each number exactly once. -> m.allDifferent(row, "AC") / column / nonet, posted (9+9+9)
- The sum of all numbers in a cage must match the small number printed in its corner. -> m.sum(cage cells, "=", cage sum), one per cage (cage data from instance field "problem": [sum, [[r,c],...]], 1-based cells)
- No number appears more than once in a cage. -> m.allDifferent(cage cells, "AC"), one per cage
- Print the solution matrix (x) as a list of lists of integers 1 to 9. -> out.put("x", x)
- Objective (satisfaction) -> none, no setObjective
