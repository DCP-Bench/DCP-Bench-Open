# Rectangle packing: place rectangles of given widths and heights, without overlap, inside a
# bounding rectangle of the smallest possible area.
import cpmpy as cp


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    # The bounding rectangle must be at least as wide (high) as the widest (highest) item,
    # and is never wider (higher) than all items side by side (stacked), which always works.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    # (pos_x[i], pos_y[i]) = lower-left corner of item i, counted from 0
    pos_x = cp.intvar(0, max_x, shape=n, name="pos_x")
    pos_y = cp.intvar(0, max_y, shape=n, name="pos_y")

    # width and height of the bounding rectangle
    total_x = cp.intvar(min_x, max_x, name="total_x")
    total_y = cp.intvar(min_y, max_y, name="total_y")

    model = cp.Model()

    # Every item lies inside the bounding rectangle.
    for i in range(n):
        model += pos_x[i] + widths[i] <= total_x
        model += pos_y[i] + heights[i] <= total_y

    # No two items overlap: one lies entirely to the left of, to the right of, below, or above
    # the other.
    for i in range(n):
        for j in range(i + 1, n):
            model += (
                (pos_x[i] + widths[i] <= pos_x[j])
                | (pos_x[j] + widths[j] <= pos_x[i])
                | (pos_y[i] + heights[i] <= pos_y[j])
                | (pos_y[j] + heights[j] <= pos_y[i])
            )

    # Minimise the area of the bounding rectangle.
    model.minimize(total_x * total_y)

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
