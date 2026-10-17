# Perfect square placement (squared square problem): pack squares with the given
# integer sides into a bigger square of side `base` so that the squares do not
# overlap, all square borders are parallel to the border of the big square, and
# the coordinates start from 0.
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

    return constraints, {"x_coords": xs, "y_coords": ys}
