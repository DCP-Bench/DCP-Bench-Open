# Solitaire battleships: fill a grid with water and the parts of a fleet of ships
# (submarines, and longer ships made of a left/top end, middle pieces and a
# right/bottom end) so that ships do not touch, every row and column holds the
# given number of ship cells, the fleet has the given composition, and the
# initial hints are respected.
from pychoco.model import Model


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]  # number of ship cells required in each row
    colsum = instance["colsum"]  # number of ship cells required in each column
    fleet_counts = {size: count for size, count in instance["fleet_counts"]}  # ship size -> how many
    hints = instance["hints"]  # [row, col, cell code] cells known at the start
    # The code of each kind of cell, as the instance gives it
    WATER, CIRCLE, LEFT, RIGHT = instance["WATER"], instance["CIRCLE"], instance["LEFT"], instance["RIGHT"]
    TOP, BOTTOM, MIDDLE = instance["TOP"], instance["BOTTOM"], instance["MIDDLE"]
    # A cell takes one of the codes 0..7 (the range the reference declares).
    n_codes = 8

    model = Model()

    # grid[r][c] = the code of the cell in row r, column c
    grid = [[model.intvar(0, n_codes - 1, name=f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]
    # is_code[r][c][v] = 1 if cell (r, c) holds code v. These Booleans are tied to the
    # grid cell by a channeling constraint, so they follow from the grid; the rules
    # below are written on them as clauses.
    is_code = []
    for r in range(rows):
        row_flags = []
        for c in range(cols):
            flags = [model.boolvar(name=f"is_{r}_{c}_{v}") for v in range(n_codes)]
            model.bools_int_channeling(flags, grid[r][c]).post()
            row_flags.append(flags)
        is_code.append(row_flags)

    def cell_is(code, r, c):
        return is_code[r][c][code]

    def clause(positive, negative):
        """At least one positive literal is true or at least one negative literal is false."""
        if positive and negative:
            model.add_clauses(positive, negative)
        elif positive:
            model.sum(positive, ">=", 1).post()
        else:
            model.sum(negative, "<=", len(negative) - 1).post()

    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # The initial hints: some cells are known to be water, a submarine or a ship part.
    for r, c, code in hints:
        model.arithm(grid[r][c], "=", code).post()

    # Row and column sums: the cells that are not water are the ship cells, so a row
    # with rowsum[r] ship cells has cols - rowsum[r] water cells (same for columns).
    for r in range(rows):
        model.sum([cell_is(WATER, r, c) for c in range(cols)], "=", cols - rowsum[r]).post()
    for c in range(cols):
        model.sum([cell_is(WATER, r, c) for r in range(rows)], "=", rows - colsum[c]).post()

    # Adjacency and connectivity of the pieces, cell by cell.
    for r in range(rows):
        for c in range(cols):
            water = cell_is(WATER, r, c)

            # Ships do not touch diagonally: a ship cell has water on its four diagonals.
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                if inside(r + dr, c + dc):
                    clause([water, cell_is(WATER, r + dr, c + dc)], [])

            # A submarine (circle) is surrounded by water on all four sides.
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [cell_is(CIRCLE, r, c)])

            # The left end of a ship continues to its right with a middle piece or the right
            # end, and has water above, below and to its left (it cannot be in the last column).
            left = cell_is(LEFT, r, c)
            if c < cols - 1:
                clause([cell_is(MIDDLE, r, c + 1), cell_is(RIGHT, r, c + 1)], [left])
            else:
                clause([], [left])
            for dr, dc in ((-1, 0), (1, 0), (0, -1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [left])

            # The right end of a ship continues to its left with a middle piece or the left
            # end, and has water above, below and to its right (it cannot be in the first column).
            right = cell_is(RIGHT, r, c)
            if c > 0:
                clause([cell_is(MIDDLE, r, c - 1), cell_is(LEFT, r, c - 1)], [right])
            else:
                clause([], [right])
            for dr, dc in ((-1, 0), (1, 0), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [right])

            # The top end of a ship continues below with a middle piece or the bottom end, and
            # has water above, to its left and to its right (it cannot be in the last row).
            top = cell_is(TOP, r, c)
            if r < rows - 1:
                clause([cell_is(MIDDLE, r + 1, c), cell_is(BOTTOM, r + 1, c)], [top])
            else:
                clause([], [top])
            for dr, dc in ((-1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [top])

            # The bottom end of a ship continues above with a middle piece or the top end, and
            # has water below, to its left and to its right (it cannot be in the first row).
            bottom = cell_is(BOTTOM, r, c)
            if r > 0:
                clause([cell_is(MIDDLE, r - 1, c), cell_is(TOP, r - 1, c)], [bottom])
            else:
                clause([], [bottom])
            for dr, dc in ((1, 0), (0, -1), (0, 1)):
                if inside(r + dr, c + dc):
                    clause([cell_is(WATER, r + dr, c + dc)], [bottom])

            # A middle piece lies inside a horizontal ship or a vertical ship.
            #   horizontal: left neighbour is a left end or middle, right neighbour is a
            #               middle or right end, water above and below;
            #   vertical:   upper neighbour is a top end or middle, lower neighbour is a
            #               middle or bottom end, water to its left and right.
            # The two cases exclude each other: a horizontal middle has a ship cell to its
            # left and a vertical one has water there. So the case is chosen by whether the
            # left neighbour is water, which needs no extra variable. "horizontal" is
            # written as a clause set that applies when the left neighbour is a ship cell,
            # "vertical" as one that applies when it is water (or there is no left neighbour).
            middle = cell_is(MIDDLE, r, c)
            if c > 0:
                left_water = cell_is(WATER, r, c - 1)
                horizontal_if = [left_water]  # positive literal: clause is vacuous unless a ship is on the left
                vertical_if = [left_water]  # negative literal: clause is vacuous unless the left is water
            else:
                left_water = None
                horizontal_if = []
                vertical_if = []
            # horizontal case
            if 0 < c < cols - 1:
                clause(horizontal_if + [cell_is(LEFT, r, c - 1), cell_is(MIDDLE, r, c - 1)], [middle])
                clause(horizontal_if + [cell_is(RIGHT, r, c + 1), cell_is(MIDDLE, r, c + 1)], [middle])
                if r > 0:
                    clause(horizontal_if + [cell_is(WATER, r - 1, c)], [middle])
                if r < rows - 1:
                    clause(horizontal_if + [cell_is(WATER, r + 1, c)], [middle])
            elif c > 0:
                # last column: a middle piece cannot be horizontal, so the left cell is water
                clause([left_water], [middle])
            # vertical case
            if 0 < r < rows - 1:
                clause([cell_is(TOP, r - 1, c), cell_is(MIDDLE, r - 1, c)], [middle] + vertical_if)
                clause([cell_is(BOTTOM, r + 1, c), cell_is(MIDDLE, r + 1, c)], [middle] + vertical_if)
                if c < cols - 1:
                    clause([cell_is(WATER, r, c + 1)], [middle] + vertical_if)
            else:
                # first or last row: a middle piece cannot be vertical, so it must be horizontal
                clause([], [middle] + vertical_if)

    # Fleet composition.
    # Submarines (size 1): exactly the required number of circle cells.
    model.sum([cell_is(CIRCLE, r, c) for r in range(rows) for c in range(cols)], "=", fleet_counts[1]).post()

    # Longer ships, counted by size: a ship of size n is a left end, n-2 middle pieces and
    # a right end in a row, or a top end, n-2 middle pieces and a bottom end in a column.
    # Each possible placement is reified (true when all its cells hold the right pieces) and
    # the placements that hold are counted.
    for size, count in fleet_counts.items():
        if size < 2:
            continue
        placements = []
        for r in range(rows):
            for c in range(cols - size + 1):
                cells = [cell_is(LEFT, r, c), cell_is(RIGHT, r, c + size - 1)]
                cells += [cell_is(MIDDLE, r, c + k) for k in range(1, size - 1)]
                placements.append(model.sum(cells, ">=", len(cells)).reify())
        for r in range(rows - size + 1):
            for c in range(cols):
                cells = [cell_is(TOP, r, c), cell_is(BOTTOM, r + size - 1, c)]
                cells += [cell_is(MIDDLE, r + k, c) for k in range(1, size - 1)]
                placements.append(model.sum(cells, ">=", len(cells)).reify())
        model.sum(placements, "=", count).post()

    # No ship of a size the fleet does not list: every left or top end starts one of the
    # ships counted above, so their total is the number of ships longer than one cell.
    ends = [cell_is(LEFT, r, c) for r in range(rows) for c in range(cols)]
    ends += [cell_is(TOP, r, c) for r in range(rows) for c in range(cols)]
    model.sum(ends, "=", sum(count for size, count in fleet_counts.items() if size > 1)).post()

    return model, {"grid": grid}
