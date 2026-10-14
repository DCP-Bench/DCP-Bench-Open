# Rectangle packing: place rectangles of given widths and heights, without
# overlap and without rotation, inside the smallest possible enclosing rectangle
# (smallest area). Positions start at 0.
import z3


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    solver = z3.Solver()

    # The enclosing rectangle is at least as wide / high as the widest / tallest
    # item and never needs to exceed placing all items side by side / on top of each other.
    total_x, total_y = z3.Ints("total_x total_y")
    solver.add(total_x >= max(widths), total_x <= sum(widths))
    solver.add(total_y >= max(heights), total_y <= sum(heights))

    # pos_x[i], pos_y[i] = lower-left corner of item i
    pos_x = [z3.Int(f"pos_x_{i}") for i in range(n)]
    pos_y = [z3.Int(f"pos_y_{i}") for i in range(n)]
    for i in range(n):
        solver.add(pos_x[i] >= 0, pos_y[i] >= 0)
        # every item lies completely inside the enclosing rectangle
        solver.add(pos_x[i] + widths[i] <= total_x, pos_y[i] + heights[i] <= total_y)

    # no two items overlap: one is entirely to the left of, right of, below or above the other
    for i in range(n):
        for j in range(i + 1, n):
            solver.add(z3.Or(pos_x[i] + widths[i] <= pos_x[j], pos_x[j] + widths[j] <= pos_x[i],
                             pos_y[i] + heights[i] <= pos_y[j], pos_y[j] + heights[j] <= pos_y[i]))

    # minimise the area of the enclosing rectangle
    area = z3.Int("area")
    solver.add(area == total_x * total_y)

    return solver, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}, ("minimize", area)
