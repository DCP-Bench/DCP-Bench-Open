# Rectangle packing: place rectangles of given widths and heights, without
# overlap and without rotation, inside the smallest possible enclosing rectangle
# (smallest area). Positions start at 0.
from ortools.sat.python import cp_model


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    model = cp_model.CpModel()

    # The enclosing rectangle is at least as wide / high as the widest / tallest
    # item and never needs to exceed placing all items side by side / on top of each other.
    total_x = model.new_int_var(max(widths), sum(widths), "total_x")
    total_y = model.new_int_var(max(heights), sum(heights), "total_y")

    # pos_x[i], pos_y[i] = lower-left corner of item i
    pos_x = [model.new_int_var(0, sum(widths), f"pos_x_{i}") for i in range(n)]
    pos_y = [model.new_int_var(0, sum(heights), f"pos_y_{i}") for i in range(n)]

    # every item lies completely inside the enclosing rectangle
    for i in range(n):
        model.add(pos_x[i] + widths[i] <= total_x)
        model.add(pos_y[i] + heights[i] <= total_y)

    # no two items overlap: each item is a fixed-size box in the plane
    x_spans = [model.new_fixed_size_interval_var(pos_x[i], widths[i], f"x_span_{i}") for i in range(n)]
    y_spans = [model.new_fixed_size_interval_var(pos_y[i], heights[i], f"y_span_{i}") for i in range(n)]
    model.add_no_overlap_2d(x_spans, y_spans)

    # minimise the area of the enclosing rectangle
    area = model.new_int_var(max(widths) * max(heights), sum(widths) * sum(heights), "area")
    model.add_multiplication_equality(area, [total_x, total_y])
    model.minimize(area)

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
