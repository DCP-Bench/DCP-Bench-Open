# Packing rectangles: place rectangular items (without rotation) inside a larger
# rectangle so that no two items overlap, minimising the area of the larger rectangle.
from pychoco.model import Model


def build(instance):
    widths = instance["widths"]  # widths of the items
    heights = instance["heights"]  # heights of the items
    n = len(widths)

    # the larger rectangle is at least as wide (tall) as the widest (tallest) item
    # and at most as wide (tall) as all items side by side (stacked)
    area_min_x, area_max_x = max(widths), sum(widths)
    area_min_y, area_max_y = max(heights), sum(heights)

    model = Model()

    # (pos_x[i], pos_y[i]) = lower-left corner of item i, counting from 0
    pos_x = [model.intvar(0, area_max_x, name=f"pos_x_{i}") for i in range(n)]
    pos_y = [model.intvar(0, area_max_y, name=f"pos_y_{i}") for i in range(n)]

    # total_x, total_y = width and height of the larger rectangle
    total_x = model.intvar(area_min_x, area_max_x, name="total_x")
    total_y = model.intvar(area_min_y, area_max_y, name="total_y")

    # every item lies within the larger rectangle: pos + size <= total
    for i in range(n):
        model.arithm(pos_x[i], "-", total_x, "<=", -widths[i]).post()
        model.arithm(pos_y[i], "-", total_y, "<=", -heights[i]).post()

    # no two items overlap: one is fully left of, right of, above or below the other
    # (diff_n states this for all pairs at once; it takes sizes as variables, so each
    # fixed size is passed as a constant variable)
    item_widths = [model.intvar(w, w) for w in widths]
    item_heights = [model.intvar(h, h) for h in heights]
    model.diff_n(pos_x, pos_y, item_widths, item_heights, True).post()

    # area of the larger rectangle (Choco minimises one variable, so it gets its own);
    # it cannot be smaller than the total area of the items (implied bound, which only
    # helps the solver prove the optimum)
    area = model.intvar(sum(w * h for w, h in zip(widths, heights)), area_max_x * area_max_y, name="area")
    model.times(total_x, total_y, area).post()

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}, ("minimize", area)
