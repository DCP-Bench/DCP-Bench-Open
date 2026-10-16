# minesweeper: plan (Choco 6.0.1)

The board is divided into cells, with mines randomly distributed. ... determine which 'X' fields contain mines
  -> mine[r][c] BoolVar per cell, sized from game_data (rows x cols of the instance); X = value of unopened cells
the number on a cell shows the number of mines adjacent to it
  -> for each opened cell with clue v: sum of mines over its in-board 8 neighbours = v (m.sum(BoolVar[], "=", v))
an opened cell cannot contain a mine (it is open, the clue is shown)
  -> mine[r][c] = 0 for every opened cell (value != X)
unopened cells: no clue, so free (no constraint)
objective: none (satisfaction); output mines as BoolVar[rows][cols]
