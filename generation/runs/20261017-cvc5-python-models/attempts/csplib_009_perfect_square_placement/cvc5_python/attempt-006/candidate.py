# Perfect square placement (squared square problem): pack the squares with the given
# integer sides into a bigger square of side `base`, so that the squares do not
# overlap and all square borders are parallel to the border of the big square.
# Coordinates start from 0.
#
# Attempt 6: the same separation choice per pair as attempt 4, under QF_LIA. Each
# line's cover sum uses one crossing Boolean per square and line, defined from the
# coordinate comparisons, so the cover sums are plain sums of If terms over those
# Booleans.
import cvc5.pythonic as cz


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)

    solver = cz.SolverFor("QF_LIA")

    xs = [cz.Int(f"x{i}") for i in range(n)]
    ys = [cz.Int(f"y{i}") for i in range(n)]

    # Every square lies inside the big square: its corner is at 0 or more and its
    # far border is at most base, so the corner is at most base minus its side.
    for i in range(n):
        solver.add(xs[i] >= 0, ys[i] >= 0)
        solver.add(xs[i] <= base - sides[i], ys[i] <= base - sides[i])

    # No two squares overlap each other: for every pair, one of the four
    # separations (left of, right of, below, above) holds, and the chosen
    # separation is written out as an implication on the coordinates.
    for i in range(n):
        for j in range(i + 1, n):
            left, right, below, above = cz.Bools(f"l{i}_{j} r{i}_{j} b{i}_{j} a{i}_{j}")
            solver.add(cz.Or(left, right, below, above))
            solver.add(cz.Implies(left, xs[i] + sides[i] <= xs[j]))
            solver.add(cz.Implies(right, xs[j] + sides[j] <= xs[i]))
            solver.add(cz.Implies(below, ys[i] + sides[i] <= ys[j]))
            solver.add(cz.Implies(above, ys[j] + sides[j] <= ys[i]))

    # The sum of the square surfaces is equal to the surface of the packing square,
    # so that there is no spare capacity.
    solver.add(sum(s * s for s in sides) == base * base)

    # No spare capacity along every line: each horizontal line y = t (for every row
    # t of the big square) is crossed by squares whose widths add up to base, and
    # each vertical line x = t is crossed by squares whose heights add up to base.
    # These follow from the exact packing and help propagation. A square crosses
    # the line when its corner is at most t and its far border is beyond t.
    for t in range(base):
        row_cross = []
        col_cross = []
        for i in range(n):
            s = sides[i]
            cy = cz.Bool(f"cy{i}_{t}")
            cx = cz.Bool(f"cx{i}_{t}")
            solver.add(cy == cz.And(ys[i] <= t, ys[i] >= t - s + 1))
            solver.add(cx == cz.And(xs[i] <= t, xs[i] >= t - s + 1))
            row_cross.append(cz.If(cy, s, 0))
            col_cross.append(cz.If(cx, s, 0))
        solver.add(cz.Sum(row_cross) == base)
        solver.add(cz.Sum(col_cross) == base)

    return solver, {"x_coords": xs, "y_coords": ys}
