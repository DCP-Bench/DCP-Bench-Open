# Solitaire battleships (CSPLib prob014) in Python-MIP with CBC.
# The grid is filled with water, a submarine, or a ship part (left, right, top,
# bottom, middle). The fleet is a list of [length, count] pairs; ships are straight,
# and no two ships touch, not even diagonally. The row and column sums count the
# occupied squares in each row and column. Hints fix some cells to a given value.
import mip


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    WATER = instance["WATER"]
    CIRCLE = instance["CIRCLE"]
    LEFT = instance["LEFT"]
    RIGHT = instance["RIGHT"]
    TOP = instance["TOP"]
    BOTTOM = instance["BOTTOM"]
    MIDDLE = instance["MIDDLE"]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    def ship_codes(orient, length):
        # the cell values of a ship, from its first cell to its last
        if length == 1:
            return [CIRCLE]
        if orient == "h":
            return [LEFT] + [MIDDLE] * (length - 2) + [RIGHT]
        return [TOP] + [MIDDLE] * (length - 2) + [BOTTOM]

    def neighbours(cell):
        # the eight squares around a cell (king moves) inside the grid
        r, c = cell
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if (dr, dc) != (0, 0) and 0 <= nr < rows and 0 <= nc < cols:
                    yield (nr, nc)

    # Placements: a ship of a given length is a straight run of cells, horizontal
    # or vertical, starting at (r, c). Each placement has a binary variable that says
    # whether the ship is in the solution. A submarine (length 1) has one placement per cell.
    placements = []
    for length, _ in instance["fleet_counts"]:
        for r in range(rows):
            for c in range(cols):
                if length == 1:
                    options = [("s", [(r, c)])]
                else:
                    options = []
                    if c + length <= cols:
                        options.append(("h", [(r, c + i) for i in range(length)]))
                    if r + length <= rows:
                        options.append(("v", [(r + i, c) for i in range(length)]))
                for orient, cells in options:
                    var = m.add_var(name=f"ship_{length}_{r}_{c}_{orient}", var_type=mip.BINARY)
                    codes = ship_codes(orient, length)
                    placements.append((length, cells, list(zip(cells, codes)), var))

    covering = {(r, c): [] for r in range(rows) for c in range(cols)}
    for length, cells, cell_codes, var in placements:
        for cell, code in cell_codes:
            covering[cell].append((code, var))

    # The fleet: the number of ships of each length is given by fleet_counts.
    for length, count in instance["fleet_counts"]:
        m += mip.xsum(var for ln, _, _, var in placements if ln == length) == count

    # Ships do not overlap: each square is covered by at most one ship.
    for cell in covering:
        m += mip.xsum(var for _, var in covering[cell]) <= 1

    # No two ships are adjacent, not even diagonally: if a ship is placed, every square
    # around it that is not part of it is covered by no ship.
    for length, cells, cell_codes, var in placements:
        ring = set()
        for cell in cells:
            ring.update(neighbours(cell))
        ring.difference_update(cells)
        for q in ring:
            m += mip.xsum(v for _, v in covering[q]) + var <= 1

    # Each square's value: water (WATER) when no ship covers it, otherwise the ship
    # part's code. Each square is an integer variable tied to the placements.
    max_code = max(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE)
    grid = []
    occupied = {}
    for r in range(rows):
        row = []
        for c in range(cols):
            g = m.add_var(name=f"cell_{r}_{c}", lb=0, ub=max_code, var_type=mip.INTEGER)
            m += g == WATER + mip.xsum((code - WATER) * var for code, var in covering[(r, c)])
            occupied[(r, c)] = mip.xsum(var for _, var in covering[(r, c)])
            row.append(g)
        grid.append(row)

    # The row and column sums: the number of occupied squares in each row and column.
    for r in range(rows):
        m += mip.xsum(occupied[(r, c)] for c in range(cols)) == instance["rowsum"][r]
    for c in range(cols):
        m += mip.xsum(occupied[(r, c)] for r in range(rows)) == instance["colsum"][c]

    # The hints: some squares are given with their value (row, column, code).
    for r, c, code in instance["hints"]:
        m += grid[r][c] == code

    return m, {"grid": grid}
