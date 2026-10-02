# Perfect square placement: place squares of given integer sizes inside a larger square, with
# sides parallel to it, so that no two squares overlap (their areas fill the big square exactly).
from exact import Exact


def build(instance):
    base = instance["base"]  # side length of the big square
    sides = instance["sides"]  # side length of each small square
    n = len(sides)

    solver = Exact()

    # (x_coords[i], y_coords[i]) is the lower-left corner of square i. Squares must lie inside
    # the big square, so a corner coordinate is at most base - side (the reference's
    # x + side <= base).
    coords = {"x": [f"x_coords_{i}" for i in range(n)], "y": [f"y_coords_{i}" for i in range(n)]}
    # at[axis][i][v] = 1 when square i starts at v on that axis. These indicators are only used
    # for the implied "every line is filled" constraints below.
    at = {axis: [[f"{axis}_coords_{i}_is_{v}" for v in range(base - sides[i] + 1)] for i in range(n)]
          for axis in coords}
    for axis in coords:
        for i in range(n):
            solver.addVariable(coords[axis][i], 0, base - sides[i])
            for name in at[axis][i]:
                solver.addVariable(name, 0, 1)
            solver.addConstraint([(1, name) for name in at[axis][i]], True, 1, True, 1)
            solver.addConstraint([(v, name) for v, name in enumerate(at[axis][i]) if v]
                                 + [(-1, coords[axis][i])], True, 0, True, 0)

    # no two squares overlap: for every pair, one lies completely to the left of, right of,
    # below or above the other. Each of the four cases gets a 0/1 variable that is 1 exactly
    # when the case holds (reification), and at least one of the four must hold.
    x_coords, y_coords = coords["x"], coords["y"]
    for a in range(n):
        for b in range(a + 1, n):
            cases = []
            for first, second, axis_coords, label in ((a, b, x_coords, "left"), (b, a, x_coords, "right"),
                                                      (a, b, y_coords, "below"), (b, a, y_coords, "above")):
                case = f"square_{a}_{label}_of_{b}"
                solver.addVariable(case, 0, 1)
                # case <-> axis_coords[second] >= axis_coords[first] + sides[first]
                solver.addReification(case, True, [(1, axis_coords[second]), (-1, axis_coords[first])],
                                      sides[first])
                cases.append((1, case))
            solver.addConstraint(cases, True, 1)

    # Implied constraint, to help the search: the squares fill the big square exactly (the
    # areas add up to base * base), so every column and every row of unit cells is covered
    # entirely, and the sides of the squares crossing it add up to base. A square of side s
    # crosses line p when it starts at a position v with v <= p <= v + s - 1.
    for axis in coords:
        for p in range(base):
            crossing = [(sides[i], at[axis][i][v]) for i in range(n)
                        for v in range(max(0, p - sides[i] + 1), min(p, base - sides[i]) + 1)]
            solver.addConstraint(crossing, True, base, True, base)

    return solver, {"x_coords": x_coords, "y_coords": y_coords}
