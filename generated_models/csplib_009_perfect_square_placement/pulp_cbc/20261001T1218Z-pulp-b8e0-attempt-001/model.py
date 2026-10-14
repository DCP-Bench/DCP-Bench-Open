"""Perfect square placement: pack squares of given integer sizes into a larger
square so that they do not overlap and have no spare room.

All square borders are parallel to the big square's border. The areas of the
small squares add up to the area of the big one, so every cell is covered.
The model gives the coordinates of the lower-left corner of each small square.
"""
import pulp


def build(instance):
    base = instance["base"]    # side of the big square
    sides = instance["sides"]  # side of each small square
    n = len(sides)

    problem = pulp.LpProblem("perfect_square_placement", pulp.LpMinimize)

    # x_coords[i], y_coords[i] = lower-left corner of square i (declared outputs).
    # The square must lie inside the big one, so the corner is at most base - side
    # (the reference bounds the corner by base and adds x + side <= base).
    x_coords = [pulp.LpVariable(f"x_{i}", 0, base - sides[i], cat="Integer") for i in range(n)]
    y_coords = [pulp.LpVariable(f"y_{i}", 0, base - sides[i], cat="Integer") for i in range(n)]

    # no overlap: for every two squares at least one of four things holds -- a is
    # left of b, b is left of a, a is below b, b is below a. One indicator per
    # alternative. M = base is the largest value of "a's far edge minus b's near
    # edge" (a's far edge <= base, b's near edge >= 0), so an inactive branch is
    # always satisfied.
    for a in range(n):
        for b in range(a + 1, n):
            alternatives = []
            for name, first, second, coords in (
                    ("left", a, b, x_coords), ("right", b, a, x_coords),
                    ("below", a, b, y_coords), ("above", b, a, y_coords)):
                holds = pulp.LpVariable(f"{name}_{a}_{b}", cat="Binary")
                problem += (coords[first] + sides[first]
                            <= coords[second] + base * (1 - holds))
                alternatives.append(holds)
            problem += pulp.lpSum(alternatives) >= 1

    # Implied constraint that tightens the relaxation. The areas fill the big
    # square exactly and nothing overlaps, so every vertical line and every
    # horizontal line of unit cells is covered exactly: the sides of the squares
    # crossing it add up to base. To count crossings, started[i][u] = 1 if
    # square i begins at coordinate <= u (an order encoding of its corner), and
    # square i crosses line u when it has begun by u but not by u - side.
    for coords, axis in ((x_coords, "x"), (y_coords, "y")):
        started = []
        for i in range(n):
            last = base - sides[i]  # largest corner coordinate of square i
            flags = [pulp.LpVariable(f"started_{axis}_{i}_{u}", cat="Binary")
                     for u in range(last)]
            # started by u implies started by u + 1
            for u in range(last - 1):
                problem += flags[u] <= flags[u + 1]
            # corner = number of coordinates before it begins
            problem += coords[i] == last - pulp.lpSum(flags)
            started.append(flags)

        def has_started(i, u):
            if u < 0:
                return 0
            if u >= len(started[i]):
                return 1  # the corner is at most base - side
            return started[i][u]

        for u in range(base):
            problem += pulp.lpSum(
                sides[i] * (has_started(i, u) - has_started(i, u - sides[i]))
                for i in range(n)) == base

    return problem, {"x_coords": x_coords, "y_coords": y_coords}
