from pycsp3 import *

rows = data.rows
cols = data.cols
WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE = data.WATER, data.CIRCLE, data.LEFT, data.RIGHT, data.TOP, data.BOTTOM, data.MIDDLE

# each cell is water, a submarine (CIRCLE), or a ship part (left, right, top, bottom, middle)
grid = VarArray(size=[rows, cols], dom={WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE})


def inside(r, c):
    return 0 <= r < rows and 0 <= c < cols


def around(r, c):
    # the eight neighbours of a cell that lie on the grid
    return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0) and inside(r + dr, c + dc)]


# the shots: a cell with a known content
satisfy(grid[r][c] == code for r, c, code in data.hints)

# the row sums: the number of occupied squares in each row
satisfy(Count(grid[r], value=WATER) == cols - data.rowsum[r] for r in range(rows))

# the column sums: the number of occupied squares in each column
satisfy(Count([grid[r][c] for r in range(rows)], value=WATER) == rows - data.colsum[c] for c in range(cols))

# the ships may be oriented horizontally or vertically, and no two ships will occupy adjacent grid squares, not even diagonally
for r in range(rows):
    for c in range(cols):
        v = grid[r][c]
        nbs = around(r, c)
        # a submarine is a single square surrounded by water
        satisfy(imply(v == CIRCLE, grid[x][y] == WATER) for x, y in nbs)
        # the left end of a horizontal ship has its right neighbour as a ship part, and water elsewhere
        if inside(r, c + 1):
            satisfy(imply(v == LEFT, Or(grid[r][c + 1] == RIGHT, grid[r][c + 1] == MIDDLE)))
            satisfy(imply(v == LEFT, grid[x][y] == WATER) for x, y in nbs if (x, y) != (r, c + 1))
        else:
            satisfy(v != LEFT)
        # the right end of a horizontal ship has its left neighbour as a ship part, and water elsewhere
        if inside(r, c - 1):
            satisfy(imply(v == RIGHT, Or(grid[r][c - 1] == LEFT, grid[r][c - 1] == MIDDLE)))
            satisfy(imply(v == RIGHT, grid[x][y] == WATER) for x, y in nbs if (x, y) != (r, c - 1))
        else:
            satisfy(v != RIGHT)
        # the top end of a vertical ship has its lower neighbour as a ship part, and water elsewhere
        if inside(r + 1, c):
            satisfy(imply(v == TOP, Or(grid[r + 1][c] == BOTTOM, grid[r + 1][c] == MIDDLE)))
            satisfy(imply(v == TOP, grid[x][y] == WATER) for x, y in nbs if (x, y) != (r + 1, c))
        else:
            satisfy(v != TOP)
        # the bottom end of a vertical ship has its upper neighbour as a ship part, and water elsewhere
        if inside(r - 1, c):
            satisfy(imply(v == BOTTOM, Or(grid[r - 1][c] == TOP, grid[r - 1][c] == MIDDLE)))
            satisfy(imply(v == BOTTOM, grid[x][y] == WATER) for x, y in nbs if (x, y) != (r - 1, c))
        else:
            satisfy(v != BOTTOM)
        # a middle part lies between two parts of its ship, either left and right or above and below, with water on the diagonals
        diagonals = [(r + dr, c + dc) for dr in (-1, 1) for dc in (-1, 1) if inside(r + dr, c + dc)]
        satisfy(imply(v == MIDDLE, grid[x][y] == WATER) for x, y in diagonals)
        alternatives = []
        if inside(r, c - 1) and inside(r, c + 1):
            alternatives.append(And(
                Or(grid[r][c - 1] == LEFT, grid[r][c - 1] == MIDDLE),
                Or(grid[r][c + 1] == RIGHT, grid[r][c + 1] == MIDDLE),
                *[grid[x][y] == WATER for x, y in [(r - 1, c), (r + 1, c)] if inside(x, y)]
            ))
        if inside(r - 1, c) and inside(r + 1, c):
            alternatives.append(And(
                Or(grid[r - 1][c] == TOP, grid[r - 1][c] == MIDDLE),
                Or(grid[r + 1][c] == BOTTOM, grid[r + 1][c] == MIDDLE),
                *[grid[x][y] == WATER for x, y in [(r, c - 1), (r, c + 1)] if inside(x, y)]
            ))
        if alternatives:
            satisfy(imply(v == MIDDLE, Or(*alternatives)))
        else:
            satisfy(v != MIDDLE)

# the fleet: battleships four squares long, cruisers three, destroyers two, submarines one.
# A horizontal or vertical run of cells with the pattern of a ship of that length is one ship, so the runs are counted.
runs = []  # (length, [cells], [pattern])
for r in range(rows):
    for c in range(cols):
        for length in (2, 3, 4):
            if inside(r, c + length - 1):
                pattern = [LEFT] + [MIDDLE] * (length - 2) + [RIGHT]
                runs.append((length, [grid[r][c + i] for i in range(length)], pattern))
            if inside(r + length - 1, c):
                pattern = [TOP] + [MIDDLE] * (length - 2) + [BOTTOM]
                runs.append((length, [grid[r + i][c] for i in range(length)], pattern))
run_matches = VarArray(size=len(runs), dom={0, 1})
satisfy(
    (run_matches[k] == 1) == And(*[cell == p for cell, p in zip(cells, pattern)])
    for k, (length, cells, pattern) in enumerate(runs)
)
for length, count in data.fleet_counts:
    if length == 1:
        # the submarines: the single-square ships
        satisfy(Count(grid, value=CIRCLE) == count)
    else:
        # the ships of this length: runs of this length that match a ship pattern
        satisfy(Sum(run_matches[k] for k, run in enumerate(runs) if run[0] == length) == count)
