# Plan: kakuro (kakuro)

Grid n x n. The instance field "blanks" (1-based [row, col]) lists the cells that are not white (black or clue cells); they are output as 0. The white cells are the cells that appear in the entries.

- Each white cell holds a digit from 1 to 9 -> x[r][c] = m.intVar(1, 9), created the first time an entry covers it
- Black and clue cells are 0 -> constant m.intVar(0) at the cells listed in "blanks"
- The sum of the numbers in each entry matches its clue -> m.sum(entry cells, "=", clue) per entry (entries from instance field "problem": [clue, [r,c], ...])
- No digit is duplicated in any entry -> m.allDifferent(entry cells, "AC") per entry
- Print the solution matrix (x) as a list of lists of integers 0 to 9 -> out.put("x", x)
- Objective: satisfaction, none
