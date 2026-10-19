# Solitaire battleships (csplib 014) as a cvc5 satisfaction model.
# Each cell of the grid is one of: water, submarine, or a ship part
# (left, right, top, bottom, middle). The codes are read from the instance.
import cvc5.pythonic as cz


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    WATER = instance["WATER"]
    SUB = instance["CIRCLE"]
    LEFT = instance["LEFT"]
    RIGHT = instance["RIGHT"]
    TOP = instance["TOP"]
    BOTTOM = instance["BOTTOM"]
    MIDDLE = instance["MIDDLE"]
    SHIP = instance["_SHIP"]
    rowsum = instance["rowsum"]
    colsum = instance["colsum"]
    fleet_counts = instance["fleet_counts"]
    hints = instance["hints"]

    x = [[cz.Int(f"x_{r}_{c}") for c in range(cols)] for r in range(rows)]
    cons = []

    # Each cell is one of water, submarine, or a ship part (left, right, top,
    # bottom, middle). The generic ship code is not a cell value.
    allowed = [WATER, SUB, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]
    for r in range(rows):
        for c in range(cols):
            cons.append(cz.Or([x[r][c] == v for v in allowed if v != SHIP]))

    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    def water_around(r, c, skip=()):
        # The cells around a ship part are water, except the cell of the same ship
        # (skip holds the (dr, dc) offsets of that cell). Ships are not even diagonally adjacent.
        out = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr, dc) == (0, 0) or (dr, dc) in skip or not inside(r + dr, c + dc):
                    continue
                out.append(x[r + dr][c + dc] == WATER)
        return out

    # The fleet consists of battleships (four squares), cruisers (three squares),
    # destroyers (two squares) and submarines (one square each). The ships may be
    # oriented horizontally or vertically, and no two ships will occupy adjacent
    # grid squares, not even diagonally.
    for r in range(rows):
        for c in range(cols):
            cell = x[r][c]

            # A submarine has water on all its sides and diagonals.
            for w in water_around(r, c):
                cons.append(cz.Implies(cell == SUB, w))

            # A left end continues to the right, and everything else around it is water.
            if c + 1 < cols:
                for w in water_around(r, c, skip={(0, 1)}):
                    cons.append(cz.Implies(cell == LEFT, w))
                cons.append(cz.Implies(cell == LEFT, cz.Or(x[r][c + 1] == RIGHT, x[r][c + 1] == MIDDLE)))
            else:
                cons.append(cell != LEFT)

            # A right end continues to the left, and everything else around it is water.
            if c - 1 >= 0:
                for w in water_around(r, c, skip={(0, -1)}):
                    cons.append(cz.Implies(cell == RIGHT, w))
                cons.append(cz.Implies(cell == RIGHT, cz.Or(x[r][c - 1] == LEFT, x[r][c - 1] == MIDDLE)))
            else:
                cons.append(cell != RIGHT)

            # A top end continues downwards, and everything else around it is water.
            if r + 1 < rows:
                for w in water_around(r, c, skip={(1, 0)}):
                    cons.append(cz.Implies(cell == TOP, w))
                cons.append(cz.Implies(cell == TOP, cz.Or(x[r + 1][c] == BOTTOM, x[r + 1][c] == MIDDLE)))
            else:
                cons.append(cell != TOP)

            # A bottom end continues upwards, and everything else around it is water.
            if r - 1 >= 0:
                for w in water_around(r, c, skip={(-1, 0)}):
                    cons.append(cz.Implies(cell == BOTTOM, w))
                cons.append(cz.Implies(cell == BOTTOM, cz.Or(x[r - 1][c] == TOP, x[r - 1][c] == MIDDLE)))
            else:
                cons.append(cell != BOTTOM)

            # A middle part is either horizontal (left and right neighbours continue
            # the ship, the cells above and below are water) or vertical.
            opts = []
            if 0 < c < cols - 1:
                parts = [
                    cz.Or(x[r][c - 1] == LEFT, x[r][c - 1] == MIDDLE),
                    cz.Or(x[r][c + 1] == RIGHT, x[r][c + 1] == MIDDLE),
                ]
                parts += water_around(r, c, skip={(0, -1), (0, 1)})
                opts.append(cz.And(parts))
            if 0 < r < rows - 1:
                parts = [
                    cz.Or(x[r - 1][c] == TOP, x[r - 1][c] == MIDDLE),
                    cz.Or(x[r + 1][c] == BOTTOM, x[r + 1][c] == MIDDLE),
                ]
                parts += water_around(r, c, skip={(-1, 0), (1, 0)})
                opts.append(cz.And(parts))
            if not opts:
                cons.append(cell != MIDDLE)
            elif len(opts) == 1:
                cons.append(cz.Implies(cell == MIDDLE, opts[0]))
            else:
                cons.append(cz.Implies(cell == MIDDLE, cz.Or(opts[0], opts[1])))

    # The digits along the right side and below the grid give the number of squares
    # in each row and column that are occupied by vessels.
    for r in range(rows):
        cons.append(cz.Sum([cz.If(x[r][c] != WATER, 1, 0) for c in range(cols)]) == rowsum[r])
    for c in range(cols):
        cons.append(cz.Sum([cz.If(x[r][c] != WATER, 1, 0) for r in range(rows)]) == colsum[c])

    # The fleet: each entry gives a ship length and the number of ships of that length.
    # A ship is found from its first square (left end or top end) and its length
    # is fixed by the squares that follow it.
    for length, count in fleet_counts:
        if length == 1:
            cons.append(cz.Sum([cz.If(x[r][c] == SUB, 1, 0) for r in range(rows) for c in range(cols)]) == count)
            continue
        starts = []
        for r in range(rows):
            for c in range(cols):
                if c + length - 1 < cols:
                    parts = [x[r][c] == LEFT]
                    parts += [x[r][c + j] == MIDDLE for j in range(1, length - 1)]
                    parts += [x[r][c + length - 1] == RIGHT]
                    starts.append(cz.If(cz.And(parts), 1, 0))
                if r + length - 1 < rows:
                    parts = [x[r][c] == TOP]
                    parts += [x[r + j][c] == MIDDLE for j in range(1, length - 1)]
                    parts += [x[r + length - 1][c] == BOTTOM]
                    starts.append(cz.If(cz.And(parts), 1, 0))
        cons.append(cz.Sum(starts) == count)

    # Hints: some squares of the grid are shown with their final content.
    for r, c, code in hints:
        cons.append(x[r][c] == code)

    outputs = {"grid": [[x[r][c] for c in range(cols)] for r in range(rows)]}
    return cons, outputs
