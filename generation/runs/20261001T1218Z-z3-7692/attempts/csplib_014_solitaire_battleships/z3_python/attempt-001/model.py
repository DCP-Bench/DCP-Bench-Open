# Solitaire battleships: fill a grid with water, submarines and the parts of
# longer ships so that the fleet is complete, ships touch nowhere (not even at
# corners), and the row and column counts of ship squares match.
import z3


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum = instance["rowsum"], instance["colsum"]  # ship squares per row / column
    fleet = {size: count for size, count in instance["fleet_counts"]}  # ships per length
    hints = instance["hints"]  # [row, col, cell value] shots already taken
    # Cell codes of the grid (given by the instance).
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]  # CIRCLE = submarine (1 square)
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]      # ends of a horizontal ship
    TOP, BOTTOM = instance["TOP"], instance["BOTTOM"]      # ends of a vertical ship
    MIDDLE = instance["MIDDLE"]                            # inner square of a ship of 3 or more

    # grid[r][c] is the content of the cell: one of the codes above. The reference
    # leaves the domain 0..7 open, so the unused code (_SHIP) is not excluded here.
    grid = [[z3.Int(f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]

    solver = z3.Solver()

    for r in range(rows):
        for c in range(cols):
            solver.add(grid[r][c] >= 0, grid[r][c] <= 7)

    def cell(r, c, code):
        return grid[r][c] == code

    def water(r, c):
        return grid[r][c] == WATER

    def ship(r, c):
        return grid[r][c] > WATER

    # Shots already taken: these cells have the given content.
    for r, c, v in hints:
        solver.add(grid[r][c] == v)

    # Row and column totals: the number of non-water cells in each row and column.
    for r in range(rows):
        solver.add(z3.Sum([z3.If(ship(r, c), 1, 0) for c in range(cols)]) == rowsum[r])
    for c in range(cols):
        solver.add(z3.Sum([z3.If(ship(r, c), 1, 0) for r in range(rows)]) == colsum[c])

    for r in range(rows):
        for c in range(cols):
            # No two ships touch diagonally: the diagonal neighbours of a ship
            # square are water.
            diagonals = [water(r + dr, c + dc) for dr in (-1, 1) for dc in (-1, 1)
                         if 0 <= r + dr < rows and 0 <= c + dc < cols]
            solver.add(z3.Implies(ship(r, c), z3.And(diagonals)))

            above = water(r - 1, c) if r > 0 else z3.BoolVal(True)
            below = water(r + 1, c) if r < rows - 1 else z3.BoolVal(True)
            left_w = water(r, c - 1) if c > 0 else z3.BoolVal(True)
            right_w = water(r, c + 1) if c < cols - 1 else z3.BoolVal(True)

            # A submarine is surrounded by water on all four sides.
            solver.add(z3.Implies(cell(r, c, CIRCLE), z3.And(above, below, left_w, right_w)))

            # Left end of a horizontal ship: a middle or right end follows to its right,
            # and water lies on the other three sides.
            next_right = (z3.Or(cell(r, c + 1, MIDDLE), cell(r, c + 1, RIGHT))
                          if c < cols - 1 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, LEFT), z3.And(next_right, left_w, above, below)))

            # Right end of a horizontal ship: a middle or left end precedes it.
            prev_left = (z3.Or(cell(r, c - 1, MIDDLE), cell(r, c - 1, LEFT))
                         if c > 0 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, RIGHT), z3.And(prev_left, right_w, above, below)))

            # Top end of a vertical ship: a middle or bottom end follows below it.
            next_down = (z3.Or(cell(r + 1, c, MIDDLE), cell(r + 1, c, BOTTOM))
                         if r < rows - 1 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, TOP), z3.And(next_down, above, left_w, right_w)))

            # Bottom end of a vertical ship: a middle or top end lies above it.
            prev_up = (z3.Or(cell(r - 1, c, MIDDLE), cell(r - 1, c, TOP))
                       if r > 0 else z3.BoolVal(False))
            solver.add(z3.Implies(cell(r, c, BOTTOM), z3.And(prev_up, below, left_w, right_w)))

            # A middle square lies inside a horizontal ship (ship squares to its left and
            # right, water above and below) or inside a vertical ship.
            if 0 < c < cols - 1:
                horizontal = z3.And(z3.Or(cell(r, c - 1, LEFT), cell(r, c - 1, MIDDLE)),
                                    z3.Or(cell(r, c + 1, RIGHT), cell(r, c + 1, MIDDLE)),
                                    above, below)
            else:
                horizontal = z3.BoolVal(False)
            if 0 < r < rows - 1:
                vertical = z3.And(z3.Or(cell(r - 1, c, TOP), cell(r - 1, c, MIDDLE)),
                                  z3.Or(cell(r + 1, c, BOTTOM), cell(r + 1, c, MIDDLE)),
                                  left_w, right_w)
            else:
                vertical = z3.BoolVal(False)
            solver.add(z3.Implies(cell(r, c, MIDDLE), z3.Or(horizontal, vertical)))

    # Fleet: the right number of submarines.
    solver.add(z3.Sum([z3.If(cell(r, c, CIRCLE), 1, 0)
                       for r in range(rows) for c in range(cols)]) == fleet[1])

    # Fleet: for each longer ship length, count the ships of exactly that length. A ship
    # of length s is an end square, s - 2 middle squares and the other end in one line.
    for size, count in fleet.items():
        if size < 2:
            continue
        ships = []
        for r in range(rows):
            for c in range(cols - size + 1):
                ships.append(z3.And([cell(r, c, LEFT), cell(r, c + size - 1, RIGHT)]
                                    + [cell(r, c + k, MIDDLE) for k in range(1, size - 1)]))
        for r in range(rows - size + 1):
            for c in range(cols):
                ships.append(z3.And([cell(r, c, TOP), cell(r + size - 1, c, BOTTOM)]
                                    + [cell(r + k, c, MIDDLE) for k in range(1, size - 1)]))
        solver.add(z3.Sum([z3.If(s, 1, 0) for s in ships]) == count)

    # No ship of a length the fleet does not list: every left or top end starts one of
    # the ships counted above, so the ends account for exactly the listed ships.
    ends = [z3.If(z3.Or(cell(r, c, LEFT), cell(r, c, TOP)), 1, 0)
            for r in range(rows) for c in range(cols)]
    solver.add(z3.Sum(ends) == sum(count for size, count in fleet.items() if size > 1))

    return solver, {"grid": grid}
