# Plan: csplib_014_solitaire_battleships (grid[r][c] = cell code)

- "The fleet consists of battleships (4), cruisers (3), destroyers (2), submarines (1)" -> placement Booleans per ship position (horizontal/vertical, length L), count per length = fleet_counts -> `m.sum(placements of length L, "=", count)`
- "ships may be oriented horizontally or vertically" -> placement variables for both orientations
- Each cell belongs to at most one ship: sum of placements covering the cell = occupied[cell] (`m.sum(covering, "=", occ)`)
- "The digits along the right side of and below the grid indicate the number of occupied squares in the row/column" -> `m.sum(occ row, "=", rowsum[r])`, same for columns
- "no two ships will occupy adjacent grid squares, not even diagonally" -> a placement and any occupied cell around it (8 neighbours, outside the ship) cannot both be 1: `m.arithm(p, "+", occ, "<=", 1)`
- Cell codes: a submarine is CIRCLE; a ship part is LEFT/RIGHT/MIDDLE (horizontal) or TOP/BOTTOM/MIDDLE (vertical) -> `m.ifThen(p = 1, cell = code)`
- occupied[cell] = (cell code is not WATER) -> `cell.ne(WATER).boolVar()`
- "In some puzzles, one or more shots have been taken" -> hints: cell[r][c] = code -> `m.arithm(cell, "=", code)`
- Objective: none (satisfaction)
