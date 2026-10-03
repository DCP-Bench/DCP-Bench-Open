"""Solitaire battleships: fill a rows x cols grid with ship parts and water so that the
fleet (ships of 1 to 4 squares in a straight line) is laid out with no two ships
touching, even diagonally, the number of ship squares in every row and column is given,
and the hinted cells are as shown.

The model reports the grid with one code per cell: water, submarine, or one of the
parts left, right, top, bottom, middle of a longer ship.
"""
import pulp


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]
    colsum = instance["colsum"]
    fleet = {size: count for size, count in instance["fleet_counts"]}  # ship size -> how many
    hints = instance["hints"]  # (row, col, cell code)
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]
    TOP, BOTTOM = instance["TOP"], instance["BOTTOM"]
    MIDDLE = instance["MIDDLE"]
    # The instance's _SHIP code (a ship square of no particular part) is not a cell
    # state here: every ship square is a submarine or a left/right/top/bottom/middle part.

    problem = pulp.LpProblem("solitaire_battleships", pulp.LpMinimize)  # satisfaction: no objective

    # State of every cell: state[r][c][s] = 1 if cell (r, c) is in state s.
    # W water, C submarine, L/R left/right end of a horizontal ship, T/B top/bottom end
    # of a vertical ship, H middle of a horizontal ship, V middle of a vertical ship.
    # The problem's single "middle" code is split into H and V because a middle part
    # is either horizontal or vertical; the code reported is the same for both.
    states = ["W", "C", "L", "R", "T", "B", "H", "V"]
    code = {"W": WATER, "C": CIRCLE, "L": LEFT, "R": RIGHT, "T": TOP, "B": BOTTOM,
            "H": MIDDLE, "V": MIDDLE}
    state = {(r, c): {s: pulp.LpVariable(f"state_{r}_{c}_{s}", cat="Binary") for s in states}
             for r in range(rows) for c in range(cols)}

    def ship(r, c):
        """1 if cell (r, c) holds any part of a ship."""
        return 1 - state[(r, c)]["W"]

    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # each cell is in exactly one state
    for cell in state:
        problem += pulp.lpSum(state[cell].values()) == 1

    # hinted cells (the problem's cell codes)
    for r, c, value in hints:
        # the states reported with this code (a "middle" hint allows H or V)
        problem += pulp.lpSum(state[(r, c)][s] for s in states if code[s] == value) == 1

    # row and column sums: the number of ship squares in each row and column
    for r in range(rows):
        problem += pulp.lpSum(ship(r, c) for c in range(cols)) == rowsum[r]
    for c in range(cols):
        problem += pulp.lpSum(ship(r, c) for r in range(rows)) == colsum[c]

    # no two ships touch diagonally: of two diagonal neighbours at most one is a ship
    # square (orthogonal contact is regulated by the part rules below)
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((1, 1), (1, -1)):
                if inside(r + dr, c + dc):
                    problem += ship(r, c) + ship(r + dr, c + dc) <= 1

    def need_water(cell_state, r, c, neighbours):
        """cell (r, c) in `cell_state` forces each listed neighbour that exists to be water."""
        for dr, dc in neighbours:
            if inside(r + dr, c + dc):
                problem += cell_state + ship(r + dr, c + dc) <= 1

    def need_one_of(cell_state, r, c, dr, dc, wanted):
        """cell (r, c) in `cell_state` forces its neighbour (dr, dc) to be in one of the
        states in `wanted`; off the grid there is no neighbour, so the state is impossible."""
        if inside(r + dr, c + dc):
            problem += cell_state <= pulp.lpSum(state[(r + dr, c + dc)][s] for s in wanted)
        else:
            problem += cell_state == 0

    for r in range(rows):
        for c in range(cols):
            cell = state[(r, c)]
            up, down, west, east = (-1, 0), (1, 0), (0, -1), (0, 1)
            # a submarine is surrounded by water
            need_water(cell["C"], r, c, [up, down, west, east])
            # left end of a horizontal ship: a middle or the right end follows to the east;
            # water on the other three sides
            need_one_of(cell["L"], r, c, 0, 1, ["H", "R"])
            need_water(cell["L"], r, c, [up, down, west])
            # right end of a horizontal ship: a middle or the left end lies to the west
            need_one_of(cell["R"], r, c, 0, -1, ["H", "L"])
            need_water(cell["R"], r, c, [up, down, east])
            # top end of a vertical ship: a middle or the bottom end lies below
            need_one_of(cell["T"], r, c, 1, 0, ["V", "B"])
            need_water(cell["T"], r, c, [up, west, east])
            # bottom end of a vertical ship: a middle or the top end lies above
            need_one_of(cell["B"], r, c, -1, 0, ["V", "T"])
            need_water(cell["B"], r, c, [down, west, east])
            # middle of a horizontal ship: ship continues on both sides along the row,
            # water above and below
            need_one_of(cell["H"], r, c, 0, -1, ["L", "H"])
            need_one_of(cell["H"], r, c, 0, 1, ["R", "H"])
            need_water(cell["H"], r, c, [up, down])
            # middle of a vertical ship: ship continues above and below, water on both sides
            need_one_of(cell["V"], r, c, -1, 0, ["T", "V"])
            need_one_of(cell["V"], r, c, 1, 0, ["B", "V"])
            need_water(cell["V"], r, c, [west, east])

    # fleet: the number of submarines
    problem += pulp.lpSum(state[cell]["C"] for cell in state) == fleet.get(1, 0)

    # fleet: ships of size n >= 2 are an end part, n-2 middle parts and the other end part
    # in a line. line[(n, 'h' or 'v', r, c)] = 1 if such a ship starts at (r, c). It
    # is tied to its cells in both directions so that it counts exactly the ships present.
    for size, count in fleet.items():
        if size < 2:
            continue
        lines = []
        for r in range(rows):
            for c in range(cols):
                for orientation in ("h", "v"):
                    dr, dc = (0, 1) if orientation == "h" else (1, 0)
                    if not inside(r + dr * (size - 1), c + dc * (size - 1)):
                        continue
                    first, last, mid = ("L", "R", "H") if orientation == "h" else ("T", "B", "V")
                    parts = [state[(r, c)][first], state[(r + dr * (size - 1), c + dc * (size - 1))][last]]
                    parts += [state[(r + dr * k, c + dc * k)][mid] for k in range(1, size - 1)]
                    line = pulp.LpVariable(f"line_{size}_{orientation}_{r}_{c}", cat="Binary")
                    for part in parts:
                        problem += line <= part
                    problem += line >= pulp.lpSum(parts) - (size - 1)
                    lines.append(line)
        problem += pulp.lpSum(lines) == count

    # fleet: no ship of a size the fleet does not list; every left or top end starts one
    # of the ships counted above
    problem += pulp.lpSum(state[cell]["L"] + state[cell]["T"] for cell in state) == sum(
        count for size, count in fleet.items() if size > 1)

    grid = [[pulp.lpSum(code[s] * state[(r, c)][s] for s in states) for c in range(cols)]
            for r in range(rows)]
    return problem, {"grid": grid}
