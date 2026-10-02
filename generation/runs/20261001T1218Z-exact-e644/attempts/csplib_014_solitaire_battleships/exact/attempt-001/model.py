# Solitaire battleships: fill a grid with water, submarines (circles) and ship parts (left,
# right, top, bottom, middle) so that the fleet has the listed ships, ships are straight and
# touch no other ship, even diagonally, and the row and column counts and the shots given as
# hints are respected.
from exact import Exact


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]  # number of ship squares in each row
    colsum = instance["colsum"]  # number of ship squares in each column
    fleet = {size: count for size, count in instance["fleet_counts"]}  # ship size -> how many
    hints = instance["hints"]  # (row, column, cell value) already shot
    # the integer code of each kind of cell, as given with the instance. The unused code
    # _SHIP is not a kind of cell in the problem statement (water, submarine or ship part
    # left/right/top/bottom/middle), so it is not offered to any cell.
    codes = {"water": instance["WATER"], "circle": instance["CIRCLE"], "left": instance["LEFT"],
             "right": instance["RIGHT"], "top": instance["TOP"], "bottom": instance["BOTTOM"],
             "middle": instance["MIDDLE"]}
    kinds = list(codes)
    # a step to the neighbour in each direction (row change, column change)
    steps = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

    solver = Exact()

    # grid[r][c] holds the code of the cell; is_kind[r][c][k] = 1 when the cell is of kind k.
    # Every rule below is about the kind of a cell and its neighbours, so each cell gets one
    # 0/1 indicator per kind (Exact has no table or element constraint).
    grid = [[f"grid_{r}_{c}" for c in range(cols)] for r in range(rows)]
    is_kind = [[{k: f"cell_{r}_{c}_{k}" for k in kinds} for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            solver.addVariable(grid[r][c], min(codes.values()), max(codes.values()))
            for k in kinds:
                solver.addVariable(is_kind[r][c][k], 0, 1)
            # every cell is of exactly one kind, and its code follows the kind
            solver.addConstraint([(1, is_kind[r][c][k]) for k in kinds], True, 1, True, 1)
            solver.addConstraint([(codes[k], is_kind[r][c][k]) for k in kinds if codes[k]] + [(-1, grid[r][c])],
                                 True, 0, True, 0)

    def neighbour(r, c, direction):
        """Coordinates of the neighbour in that direction, or None at the edge of the grid."""
        nr, nc = r + steps[direction][0], c + steps[direction][1]
        return (nr, nc) if 0 <= nr < rows and 0 <= nc < cols else None

    def water(r, c):
        return is_kind[r][c]["water"]

    def needs_one_of(head, alternatives):
        """The 0/1 variable `head` may be 1 only if one of the 0/1 `alternatives` is 1
        (head <= sum of alternatives); with no alternatives, head must be 0."""
        solver.addConstraint([(1, head)] + [(-1, a) for a in alternatives], False, 0, True, 0)

    def needs_kind_next_door(head, r, c, direction, allowed):
        """`head` may be 1 only if the neighbour in that direction exists and has one of the
        allowed kinds."""
        nb = neighbour(r, c, direction)
        needs_one_of(head, [is_kind[nb[0]][nb[1]][k] for k in allowed] if nb else [])

    def needs_water_next_door(head, r, c, directions):
        """`head` may be 1 only if the neighbours in these directions are water; a direction
        that leaves the grid has no neighbour and asks nothing."""
        for direction in directions:
            nb = neighbour(r, c, direction)
            if nb:
                needs_one_of(head, [water(*nb)])

    # hints: the shot cells are known
    for r, c, value in hints:
        for k in kinds:
            if codes[k] == value:
                solver.addConstraint([(1, is_kind[r][c][k])], True, 1, True, 1)

    # row and column counts: the number of ship squares (non-water cells) in a line is given,
    # so the number of water cells is the line length minus that
    for r in range(rows):
        solver.addConstraint([(1, water(r, c)) for c in range(cols)], True, cols - rowsum[r], True, cols - rowsum[r])
    for c in range(cols):
        solver.addConstraint([(1, water(r, c)) for r in range(rows)], True, rows - colsum[c], True, rows - colsum[c])

    # no two ships touch diagonally: of two diagonal neighbours at least one is water. Posting
    # each diagonal pair once (towards the row below) covers both directions of the rule.
    for r in range(rows - 1):
        for c in range(cols):
            for dc in (-1, 1):
                if 0 <= c + dc < cols:
                    solver.addConstraint([(1, water(r, c)), (1, water(r + 1, c + dc))], True, 1)

    for r in range(rows):
        for c in range(cols):
            cell = is_kind[r][c]

            # a submarine is entirely surrounded by water
            needs_water_next_door(cell["circle"], r, c, steps)

            # the left end of a ship has the rest of the ship (middle or right end) on its right
            # and water on its other three sides; likewise for the other three ends
            needs_kind_next_door(cell["left"], r, c, "right", ("middle", "right"))
            needs_water_next_door(cell["left"], r, c, ("left", "up", "down"))

            needs_kind_next_door(cell["right"], r, c, "left", ("middle", "left"))
            needs_water_next_door(cell["right"], r, c, ("right", "up", "down"))

            needs_kind_next_door(cell["top"], r, c, "down", ("middle", "bottom"))
            needs_water_next_door(cell["top"], r, c, ("up", "left", "right"))

            needs_kind_next_door(cell["bottom"], r, c, "up", ("middle", "top"))
            needs_water_next_door(cell["bottom"], r, c, ("down", "left", "right"))

            # a middle part lies inside a horizontal ship (left end or middle on its left, right
            # end or middle on its right, water above and below) or inside a vertical one (the
            # same turned a quarter). Each way is a 0/1 variable that may be 1 only when its
            # neighbours are as described, and the middle needs one of the two ways.
            ways = []
            for way, before, after, before_kinds, after_kinds, sides in (
                ("horizontal", "left", "right", ("left", "middle"), ("right", "middle"), ("up", "down")),
                ("vertical", "up", "down", ("top", "middle"), ("bottom", "middle"), ("left", "right")),
            ):
                if neighbour(r, c, before) and neighbour(r, c, after):
                    name = f"middle_{r}_{c}_{way}"
                    solver.addVariable(name, 0, 1)
                    needs_kind_next_door(name, r, c, before, before_kinds)
                    needs_kind_next_door(name, r, c, after, after_kinds)
                    needs_water_next_door(name, r, c, sides)
                    ways.append(name)
            needs_one_of(cell["middle"], ways)

    # the fleet: the right number of submarines
    solver.addConstraint([(1, is_kind[r][c]["circle"]) for r in range(rows) for c in range(cols)],
                         True, fleet[1], True, fleet[1])

    # ... and the right number of ships of every longer size. A ship of this size is a left end,
    # size - 2 middles and a right end in a row (or top, middles, bottom in a column); the local
    # rules above make every run of ship parts such a ship. Each possible placement gets a 0/1
    # variable that is 1 exactly when all its cells have the required kinds.
    for size, count in fleet.items():
        if size < 2:
            continue
        placements = []
        for r in range(rows):
            for c in range(cols - size + 1):
                needed = [is_kind[r][c]["left"]] + [is_kind[r][c + k]["middle"] for k in range(1, size - 1)] \
                    + [is_kind[r][c + size - 1]["right"]]
                placements.append((f"ship{size}_horizontal_{r}_{c}", needed))
        for r in range(rows - size + 1):
            for c in range(cols):
                needed = [is_kind[r][c]["top"]] + [is_kind[r + k][c]["middle"] for k in range(1, size - 1)] \
                    + [is_kind[r + size - 1][c]["bottom"]]
                placements.append((f"ship{size}_vertical_{r}_{c}", needed))
        for name, needed in placements:
            solver.addVariable(name, 0, 1)
            solver.addReification(name, True, [(1, v) for v in needed], size)
        solver.addConstraint([(1, name) for name, _ in placements], True, count, True, count)

    # no ship of a size the fleet does not list: every left or top end starts one of the ships
    # counted above
    long_ships = sum(count for size, count in fleet.items() if size > 1)
    solver.addConstraint([(1, is_kind[r][c][k]) for r in range(rows) for c in range(cols) for k in ("left", "top")],
                         True, long_ships, True, long_ships)

    return solver, {"grid": grid}
