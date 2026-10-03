"""Solitaire battleships: place a fleet of ships on a grid and report what each cell holds.

The fleet lists how many ships there are of each size (a ship of size 1 is a submarine).
Ships are straight, horizontal or vertical, and no two ships touch, not even diagonally. The
row and column sums say how many cells of each row and column are occupied by ships, and some
cells are given as hints. Each cell is reported as water, a submarine, or a ship part: left,
right, top, bottom or middle, with the cell codes taken from the instance.
"""
from docplex.mp.model import Model


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]            # ship cells wanted in each row
    colsum = instance["colsum"]            # ship cells wanted in each column
    fleet_counts = instance["fleet_counts"]  # rows [ship size, how many ships of that size]
    hints = instance["hints"]              # rows [row, column, cell code] given at the start
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]  # CIRCLE is a submarine
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]
    TOP, BOTTOM, MIDDLE = instance["TOP"], instance["BOTTOM"], instance["MIDDLE"]

    model = Model("solitaire_battleships")

    # A placement is a ship of one size, horizontal or vertical, with its first cell (the left
    # or top one) at (r, c). place[key] is 1 when that ship is on the grid. The cells and the
    # part of the ship that each cell holds are listed for every placement.
    place = {}
    parts = {}  # key -> list of (cell, code of the part of the ship held by that cell)
    for size, count in fleet_counts:
        for vertical in (False, True):
            if size == 1 and vertical:
                continue  # a submarine has no direction
            for r in range(rows - (size - 1 if vertical else 0)):
                for c in range(cols - (0 if vertical else size - 1)):
                    key = (size, vertical, r, c)
                    place[key] = model.binary_var(name=f"ship_{size}_{'v' if vertical else 'h'}_{r}_{c}")
                    held = []
                    for k in range(size):
                        cell = (r + k, c) if vertical else (r, c + k)
                        if size == 1:
                            code = CIRCLE
                        elif k == 0:
                            code = TOP if vertical else LEFT
                        elif k == size - 1:
                            code = BOTTOM if vertical else RIGHT
                        else:
                            code = MIDDLE
                        held.append((cell, code))
                    parts[key] = held

    # For every cell, the placements that cover it, by the code of the part they put there.
    codes_at = {(r, c): {} for r in range(rows) for c in range(cols)}
    for key, held in parts.items():
        for cell, code in held:
            codes_at[cell].setdefault(code, []).append(place[key])

    # The ships of each size: exactly as many placements as the fleet lists.
    for size, count in fleet_counts:
        model.add_constraint(model.sum(v for key, v in place.items() if key[0] == size) == count)

    # No two ships touch, not even diagonally, and no two overlap. Two ships touch exactly when
    # they both have a cell in one block of 2 by 2 cells, so each block is touched by at most
    # one ship (a ship with two cells in the block counts once). Written as one row per block.
    for r in range(max(rows - 1, 1)):
        for c in range(max(cols - 1, 1)):
            block = {(i, j) for i in (r, r + 1) for j in (c, c + 1) if i < rows and j < cols}
            touching = [place[key] for key, held in parts.items()
                        if any(cell in block for cell, code in held)]
            model.add_constraint(model.sum(touching) <= 1)

    # The number of ship cells in each row and in each column.
    for r in range(rows):
        model.add_constraint(model.sum(v for c in range(cols) for vs in codes_at[r, c].values()
                                       for v in vs) == rowsum[r])
    for c in range(cols):
        model.add_constraint(model.sum(v for r in range(rows) for vs in codes_at[r, c].values()
                                       for v in vs) == colsum[c])

    # The hints: the given cells hold the given code. Water means no ship covers the cell.
    for r, c, code in hints:
        if code == WATER:
            model.add_constraint(model.sum(v for vs in codes_at[r, c].values() for v in vs) == 0)
        else:
            model.add_constraint(model.sum(codes_at[r, c].get(code, [])) == 1)

    # The declared output: the code of every cell, WATER when no ship covers it. At most one
    # placement covers a cell, so the sum picks that placement's code.
    def code_of(r, c):
        covering = [v for vs in codes_at[r, c].values() for v in vs]
        return (model.sum(code * v for code, vs in codes_at[r, c].items() for v in vs)
                + WATER * (1 - model.sum(covering)))

    grid = [[code_of(r, c) for c in range(cols)] for r in range(rows)]
    return model, {"grid": grid}
