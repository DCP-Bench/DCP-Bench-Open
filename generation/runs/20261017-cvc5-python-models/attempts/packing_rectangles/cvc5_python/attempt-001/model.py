# Rectangular packing problem: place a set of rectangular items into a larger rectangle
# so that no items overlap and all items are within the boundaries of the larger area.
# The objective is to minimize the total area of the larger rectangle required to pack all items.
# Items keep their given orientation: widths run along x and heights along y.
import cvc5.pythonic as cz


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    pos_x = [cz.Int(f"pos_x_{i}") for i in range(n)]
    pos_y = [cz.Int(f"pos_y_{i}") for i in range(n)]
    total_x = cz.Int("total_x")
    total_y = cz.Int("total_y")
    area = cz.Int("area")

    # Bounds derived from the data: the larger rectangle is at least as wide as the widest item
    # and at least as tall as the tallest item. Placing all items side by side bounds it from above.
    max_w = max(widths)
    max_h = max(heights)
    sum_w = sum(widths)
    sum_h = sum(heights)

    constraints = [
        total_y >= max_h,
        total_y <= sum_h,
    ]

    # all items are within the boundaries of the larger area
    for i in range(n):
        constraints += [
            pos_x[i] >= 0,
            pos_y[i] >= 0,
            pos_x[i] + widths[i] <= total_x,
            pos_y[i] + heights[i] <= total_y,
        ]

    # no items overlap: every pair is separated horizontally or vertically
    for i in range(n):
        for j in range(i + 1, n):
            constraints.append(
                cz.Or(
                    pos_x[i] + widths[i] <= pos_x[j],
                    pos_x[j] + widths[j] <= pos_x[i],
                    pos_y[i] + heights[i] <= pos_y[j],
                    pos_y[j] + heights[j] <= pos_y[i],
                )
            )

    # The width of the larger rectangle is one value from its range. A Boolean choice per
    # candidate value selects it, so the area is a linear term: a constant times total_y.
    candidates = list(range(max_w, sum_w + 1))
    choose = [cz.Bool(f"width_is_{w}") for w in candidates]
    constraints.append(cz.Or(*choose))
    for a in range(len(choose)):
        for b in range(a + 1, len(choose)):
            constraints.append(cz.Or(cz.Not(choose[a]), cz.Not(choose[b])))
    constraints.append(
        total_x == cz.Sum([cz.If(c, w, 0) for c, w in zip(choose, candidates)])
    )
    # area == total_x * total_y, written as a sum of constant multiples of total_y
    constraints.append(
        area == cz.Sum([cz.If(c, w * total_y, 0) for c, w in zip(choose, candidates)])
    )

    outputs = {
        "pos_x": pos_x,
        "pos_y": pos_y,
        "total_x": total_x,
        "total_y": total_y,
    }
    # minimize the total area of the larger rectangle
    return constraints, outputs, ("minimize", area)
