# Perfect square placement: pack squares of given integer sides into a larger
# square with no overlap and no gap (their areas add up to the big square's
# area), all edges parallel to the big square's edges.
import cpmpy as cp


def build(instance):
    base = instance["base"]    # side of the big square
    sides = instance["sides"]  # side of each small square
    n = len(sides)

    # (x_coords[i], y_coords[i]) = lower-left corner of square i, counted from 0.
    # A square of side s must start at most base - s from the origin; that is the
    # "square lies inside the big square" condition, stated as a variable bound.
    x_coords = cp.cpm_array([cp.intvar(0, base - sides[i], name=f"x_coords[{i}]") for i in range(n)])
    y_coords = cp.cpm_array([cp.intvar(0, base - sides[i], name=f"y_coords[{i}]") for i in range(n)])

    model = cp.Model()

    # No two squares overlap: for every pair, one lies entirely to the left of, to the right of,
    # below, or above the other.
    for a in range(n):
        for b in range(a + 1, n):
            model += (
                (x_coords[a] + sides[a] <= x_coords[b]) |
                (x_coords[b] + sides[b] <= x_coords[a]) |
                (y_coords[a] + sides[a] <= y_coords[b]) |
                (y_coords[b] + sides[b] <= y_coords[a])
            )

    # Implied constraints that help the search: the squares crossing any column (row) are stacked,
    # so their sides add up to at most the base. Non-overlap already implies this; stating it
    # lets the solver reason about total extent, as with a cumulative resource of capacity base.
    model += cp.Cumulative(x_coords, sides, demand=sides, capacity=base)
    model += cp.Cumulative(y_coords, sides, demand=sides, capacity=base)

    return model, {"x_coords": x_coords, "y_coords": y_coords}
