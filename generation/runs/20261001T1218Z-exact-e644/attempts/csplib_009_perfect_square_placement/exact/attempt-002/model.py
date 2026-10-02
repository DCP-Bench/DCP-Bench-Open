# Perfect square placement: place squares of given integer sizes inside a larger square, with
# sides parallel to it, so that no two squares overlap (their areas fill the big square exactly).
from exact import Exact


def build(instance):
    base = instance["base"]  # side length of the big square
    sides = instance["sides"]  # side length of each small square
    n = len(sides)

    solver = Exact()

    # (x_coords[i], y_coords[i]) is the lower-left corner of square i. Squares must lie inside
    # the big square, so the corner coordinate is at most base - side (the reference's
    # x + side <= base); Exact integer domains are bounds, so this is the declared domain.
    x_coords = [f"x_coords_{i}" for i in range(n)]
    y_coords = [f"y_coords_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(x_coords[i], 0, base - sides[i])
        solver.addVariable(y_coords[i], 0, base - sides[i])

    # no two squares overlap: for every pair, one lies completely to the left of, right of,
    # below or above the other. Each of the four cases gets a 0/1 variable that is 1 exactly
    # when the case holds (reification), and at least one of the four must hold.
    for a in range(n):
        for b in range(a + 1, n):
            cases = []
            for first, second, coords, label in ((a, b, x_coords, "left"), (b, a, x_coords, "right"),
                                                  (a, b, y_coords, "below"), (b, a, y_coords, "above")):
                case = f"square_{a}_{label}_of_{b}"
                solver.addVariable(case, 0, 1)
                # case <-> coords[second] >= coords[first] + sides[first]
                solver.addReification(case, True, [(1, coords[second]), (-1, coords[first])], sides[first])
                cases.append((1, case))
            solver.addConstraint(cases, True, 1)

    return solver, {"x_coords": x_coords, "y_coords": y_coords}
