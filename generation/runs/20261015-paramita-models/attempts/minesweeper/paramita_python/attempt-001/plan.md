# Plan: minesweeper (attempt-001)

- Each cell is a mine or not -> one Bool per cell `mine[r][c]` (no integer encoding needed; outputs are Booleans).
- "open all the cells"/"Cells suspected of being mines" -> an opened (numbered) cell is not a mine -> `~mine[r][c]` for every cell whose clue is not X.
- "The number on a cell shows the number of mines adjacent to it" -> for every numbered cell, `sum(mine of the up-to-8 neighbours) == clue` (PB equality, unit coefficients).
- "The task is to determine which 'X' fields contain mines" -> unopened cells keep free Bools; the clues constrain them.
- "Print whether each cell is a mine or not (mines)" -> output `mines` = nested list of the cell Bools.
- Objective -> satisfaction (no objective).
