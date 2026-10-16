Fill a 9x9 grid with numbers -> grid[r][c] IntVars in 1..9
each row contains all the digits between 1 and 9 -> m.allDifferent(row, "AC").post() per row
each column contains all the digits between 1 and 9 -> m.allDifferent(column, "AC").post() per column
each 3x3 section contains all the digits between 1 and 9 -> m.allDifferent(box, "AC").post() per box
input grid cells filled with numbers -> grid[r][c] = clue, via m.arithm(grid[r][c], "=", clue).post() for each nonzero input cell
Print the solved grid (grid) -> out.put("grid", grid)
Objective: none (satisfaction)
