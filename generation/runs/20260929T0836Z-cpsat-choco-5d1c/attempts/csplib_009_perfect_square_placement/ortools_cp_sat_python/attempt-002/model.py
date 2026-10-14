# Perfect square placement: pack squares of given integer sides into a larger
# square with no overlap and no gap (their areas add up to the big square's
# area), all edges parallel to the big square's edges.
from ortools.sat.python import cp_model


def build(instance):
    base = instance["base"]  # side of the big square
    sides = instance["sides"]  # side of each small square
    n = len(sides)

    model = cp_model.CpModel()

    # (x_coords[i], y_coords[i]) = lower-left corner of square i, counted from 0;
    # a square of side s must start at most base - s from the origin, which is
    # the "square lies inside the big square" condition
    x_coords = [model.new_int_var(0, base - sides[i], f"x_{i}") for i in range(n)]
    y_coords = [model.new_int_var(0, base - sides[i], f"y_{i}") for i in range(n)]

    # no two squares overlap: each is a box of fixed size in the plane
    x_spans = [model.new_fixed_size_interval_var(x_coords[i], sides[i], f"x_span_{i}") for i in range(n)]
    y_spans = [model.new_fixed_size_interval_var(y_coords[i], sides[i], f"y_span_{i}") for i in range(n)]
    model.add_no_overlap_2d(x_spans, y_spans)

    # Implied constraints that speed up the search on the larger instances: at
    # any column (row) the squares crossing it are stacked, so their sides add
    # up to at most the base. Non-overlap already implies this; stating it lets
    # the solver reason about the total extent, as in a cumulative resource.
    model.add_cumulative(x_spans, sides, base)
    model.add_cumulative(y_spans, sides, base)

    return model, {"x_coords": x_coords, "y_coords": y_coords}
