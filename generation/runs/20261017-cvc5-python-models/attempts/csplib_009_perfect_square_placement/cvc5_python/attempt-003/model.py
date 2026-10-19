# Perfect square placement (squared square problem): pack the squares with the given
# integer sides into a bigger square of side `base`, so that the squares do not
# overlap and all square borders are parallel to the border of the big square.
# Coordinates start from 0.
import cvc5.pythonic as cz


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)
    xs = [cz.Int(f"x{i}") for i in range(n)]
    ys = [cz.Int(f"y{i}") for i in range(n)]

    constraints = []

    # Every square lies inside the big square: its corner is at 0 or more and its
    # far border is at most base.
    for i in range(n):
        constraints.append(xs[i] >= 0)
        constraints.append(ys[i] >= 0)
        constraints.append(xs[i] + sides[i] <= base)
        constraints.append(ys[i] + sides[i] <= base)

    # No two squares overlap each other: for every pair, one of the four
    # separations (left of, right of, below, above) holds.
    for i in range(n):
        for j in range(i + 1, n):
            constraints.append(
                cz.Or(
                    xs[i] + sides[i] <= xs[j],
                    xs[j] + sides[j] <= xs[i],
                    ys[i] + sides[i] <= ys[j],
                    ys[j] + sides[j] <= ys[i],
                )
            )

    # The sum of the square surfaces is equal to the surface of the packing square,
    # so that there is no spare capacity.
    constraints.append(sum(s * s for s in sides) == base * base)

    # No spare capacity along every line: each horizontal line y = t (for every row
    # t of the big square) is crossed by squares whose widths add up to base, and
    # each vertical line x = t is crossed by squares whose heights add up to base.
    # These follow from the exact packing and help propagation.
    for t in range(base):
        constraints.append(
            cz.Sum(
                [
                    cz.If(cz.And(ys[i] <= t, t < ys[i] + sides[i]), sides[i], 0)
                    for i in range(n)
                ]
            )
            == base
        )
        constraints.append(
            cz.Sum(
                [
                    cz.If(cz.And(xs[i] <= t, t < xs[i] + sides[i]), sides[i], 0)
                    for i in range(n)
                ]
            )
            == base
        )

    return constraints, {"x_coords": xs, "y_coords": ys}
