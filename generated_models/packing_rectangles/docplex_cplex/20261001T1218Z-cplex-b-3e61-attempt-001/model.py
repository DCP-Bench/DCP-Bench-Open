"""Rectangle packing: place rectangular items, without rotating them, inside an enclosing rectangle
so that no two items overlap and every item lies within it, minimizing the enclosing area.

The model reports the lower-left corner of every item and the width and height of the enclosing
rectangle.
"""
from docplex.mp.model import Model


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)
    items = range(n)

    # The enclosing rectangle is at least as wide as the widest item and at most as wide as all
    # items side by side; the same holds for its height.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    model = Model("packing_rectangles")

    pos_x = [model.integer_var(0, max_x, name=f"pos_x_{i}") for i in items]
    pos_y = [model.integer_var(0, max_y, name=f"pos_y_{i}") for i in items]

    # The area total_x * total_y multiplies two variables, which CPLEX refuses. The width is
    # therefore chosen from its possible values: wide[a] = 1 when total_x = a, and
    # part[a] = wide[a] * total_y is linearised with the standard four inequalities.
    xs = range(min_x, max_x + 1)
    wide = {a: model.binary_var(name=f"wide_{a}") for a in xs}
    model.add_constraint(model.sum(wide.values()) == 1)
    total_x = model.sum(a * wide[a] for a in xs)
    total_y = model.integer_var(min_y, max_y, name="total_y")
    part = {a: model.integer_var(0, max_y, name=f"part_{a}") for a in xs}
    for a in xs:
        model.add_constraint(part[a] <= max_y * wide[a])
        model.add_constraint(part[a] >= min_y * wide[a])
        model.add_constraint(part[a] <= total_y - min_y * (1 - wide[a]))
        model.add_constraint(part[a] >= total_y - max_y * (1 - wide[a]))
    area = model.sum(a * part[a] for a in xs)

    # Implied, not an extra rule: the enclosing rectangle covers the items' total area, so a
    # width a needs a height of at least ceil(total area / a).
    total_area = sum(w * h for w, h in zip(widths, heights))
    for a in xs:
        model.add_constraint(part[a] >= -(-total_area // a) * wide[a])

    # Every item has to be within the enclosing rectangle.
    for i in items:
        model.add_constraint(pos_x[i] + widths[i] <= total_x)
        model.add_constraint(pos_y[i] + heights[i] <= total_y)

    # No overlap: every item is fully left of, right of, below or above every other item.
    # One indicator per side, at least one of them on.
    for i in items:
        for j in items:
            if i < j:
                side = model.binary_var_list(4, name=f"side_{i}_{j}")
                model.add_indicator(side[0], pos_x[i] + widths[i] <= pos_x[j])
                model.add_indicator(side[1], pos_x[j] + widths[j] <= pos_x[i])
                model.add_indicator(side[2], pos_y[i] + heights[i] <= pos_y[j])
                model.add_indicator(side[3], pos_y[j] + heights[j] <= pos_y[i])
                model.add_constraint(model.sum(side) >= 1)

    # Minimize the area of the enclosing rectangle.
    model.minimize(area)

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
