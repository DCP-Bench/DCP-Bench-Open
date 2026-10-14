# Solitaire battleships: fill a grid with water and ship pieces so that the
# fleet (ships of lengths 4, 3, 2 and 1 in given numbers) fits, ships lie
# horizontally or vertically and never touch, not even diagonally, and the
# numbers beside the grid give the ship squares in each row and column. Some
# cells may be given as hints.
from hermax.model import Model


def any_of(literals):
    """The clause 'at least one of these literals'."""
    clause = literals[0]
    for lit in literals[1:]:
        clause = clause | lit
    return clause


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]  # ship squares in each row
    colsum = instance["colsum"]  # ship squares in each column
    fleet = {size: count for size, count in instance["fleet_counts"]}  # ships of each length
    hints = instance["hints"]  # (row, column, piece) cells given in advance
    # how the pieces are coded in the grid
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]  # CIRCLE = a one-square ship
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]
    TOP, BOTTOM = instance["TOP"], instance["BOTTOM"]
    MIDDLE = instance["MIDDLE"]

    m = Model()
    # grid[r][c] = the piece in cell (r, c); codes 0..7 are the eight kinds of
    # cell the problem distinguishes (the reference's own domain)
    grid = m.int_matrix("grid", rows, cols, 0, 7)
    # is_piece[r][c][v] = the literal "cell (r, c) holds piece v"
    is_piece = [[{v: grid[r][c] == v for v in range(8)} for c in range(cols)] for r in range(rows)]

    def piece(r, c, v):
        return is_piece[r][c][v]

    def ship(r, c):
        return ~is_piece[r][c][WATER]  # any non-water cell is part of a ship

    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # the hints fix some cells
    for r, c, v in hints:
        m &= piece(r, c, v)

    # the numbers beside the grid: ship squares in each row and each column
    for r in range(rows):
        m &= (sum(ship(r, c) for c in range(cols)) == rowsum[r])
    for c in range(cols):
        m &= (sum(ship(r, c) for r in range(rows)) == colsum[c])

    for r in range(rows):
        for c in range(cols):
            here = lambda v: piece(r, c, v)

            # ships never touch diagonally: a ship cell has water on its diagonals
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                if inside(r + dr, c + dc):
                    m &= (~ship(r, c) | piece(r + dr, c + dc, WATER))

            # the four orthogonal neighbours that exist
            around = [(r + dr, c + dc) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                      if inside(r + dr, c + dc)]

            # a one-square ship is surrounded by water
            for nr, nc in around:
                m &= (~here(CIRCLE) | piece(nr, nc, WATER))

            # the left end of a ship: a middle or right end follows on its right,
            # and there is water left, above and below (where those cells exist)
            if c < cols - 1:
                m &= (~here(LEFT) | piece(r, c + 1, MIDDLE) | piece(r, c + 1, RIGHT))
            else:
                m &= ~here(LEFT)  # no room for the rest of the ship
            for nr, nc in ((r, c - 1), (r - 1, c), (r + 1, c)):
                if inside(nr, nc):
                    m &= (~here(LEFT) | piece(nr, nc, WATER))

            # the right end: a middle or left end precedes it, water on the other sides
            if c > 0:
                m &= (~here(RIGHT) | piece(r, c - 1, MIDDLE) | piece(r, c - 1, LEFT))
            else:
                m &= ~here(RIGHT)
            for nr, nc in ((r, c + 1), (r - 1, c), (r + 1, c)):
                if inside(nr, nc):
                    m &= (~here(RIGHT) | piece(nr, nc, WATER))

            # the top end: a middle or bottom end follows below, water on the other sides
            if r < rows - 1:
                m &= (~here(TOP) | piece(r + 1, c, MIDDLE) | piece(r + 1, c, BOTTOM))
            else:
                m &= ~here(TOP)
            for nr, nc in ((r - 1, c), (r, c - 1), (r, c + 1)):
                if inside(nr, nc):
                    m &= (~here(TOP) | piece(nr, nc, WATER))

            # the bottom end: a middle or top end precedes it, water on the other sides
            if r > 0:
                m &= (~here(BOTTOM) | piece(r - 1, c, MIDDLE) | piece(r - 1, c, TOP))
            else:
                m &= ~here(BOTTOM)
            for nr, nc in ((r + 1, c), (r, c - 1), (r, c + 1)):
                if inside(nr, nc):
                    m &= (~here(BOTTOM) | piece(nr, nc, WATER))

            # A middle piece lies inside a horizontal or a vertical ship: either
            # its left neighbour is a left end or middle, its right neighbour a
            # right end or middle, and water above and below; or the same turned
            # a quarter. One selector per case.
            options = []
            if 0 < c < cols - 1:
                horizontal = m.bool(f"middle_h_{r}_{c}")
                m &= (~horizontal | piece(r, c - 1, LEFT) | piece(r, c - 1, MIDDLE))
                m &= (~horizontal | piece(r, c + 1, RIGHT) | piece(r, c + 1, MIDDLE))
                for nr, nc in ((r - 1, c), (r + 1, c)):
                    if inside(nr, nc):
                        m &= (~horizontal | piece(nr, nc, WATER))
                options.append(horizontal)
            if 0 < r < rows - 1:
                vertical = m.bool(f"middle_v_{r}_{c}")
                m &= (~vertical | piece(r - 1, c, TOP) | piece(r - 1, c, MIDDLE))
                m &= (~vertical | piece(r + 1, c, BOTTOM) | piece(r + 1, c, MIDDLE))
                for nr, nc in ((r, c - 1), (r, c + 1)):
                    if inside(nr, nc):
                        m &= (~vertical | piece(nr, nc, WATER))
                options.append(vertical)
            if options:
                m &= (~here(MIDDLE) | any_of(options))
            else:
                m &= ~here(MIDDLE)  # a middle piece needs room on both sides

    # the right number of one-square ships
    m &= (sum(piece(r, c, CIRCLE) for r in range(rows) for c in range(cols)) == fleet[1])

    # The right number of longer ships, counted by length. A ship of length s is
    # an end piece, s-2 middle pieces and the other end piece in a line. The
    # rules above make every run of ship pieces one such ship. placed is true
    # exactly when the whole pattern is present (both directions are posted,
    # since the number of placed ships is counted exactly).
    for size, count in fleet.items():
        if size < 2:
            continue
        placed = []
        for r in range(rows):
            for c in range(cols - size + 1):
                parts = [piece(r, c, LEFT), piece(r, c + size - 1, RIGHT)]
                parts += [piece(r, c + k, MIDDLE) for k in range(1, size - 1)]
                placed.append(parts)
        for r in range(rows - size + 1):
            for c in range(cols):
                parts = [piece(r, c, TOP), piece(r + size - 1, c, BOTTOM)]
                parts += [piece(r + k, c, MIDDLE) for k in range(1, size - 1)]
                placed.append(parts)
        flags = []
        for index, parts in enumerate(placed):
            flag = m.bool(f"ship{size}_{index}")
            for part in parts:
                m &= (~flag | part)
            m &= (flag | any_of([~part for part in parts]))
            flags.append(flag)
        m &= (sum(flags) == count)

    # no ship of a length that the fleet does not list: every left or top end
    # starts one of the ships counted above
    long_ships = sum(count for size, count in fleet.items() if size > 1)
    ends = [piece(r, c, v) for r in range(rows) for c in range(cols) for v in (LEFT, TOP)]
    m &= (sum(ends) == long_ships)

    return m, {"grid": grid}
