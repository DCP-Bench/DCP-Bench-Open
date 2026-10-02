# Rectangle packing: place rectangles of given widths and heights (no rotation) inside one
# larger rectangle without overlap, so that the area of the larger rectangle is as small as possible.
from exact import Exact


def build(instance):
    widths = instance["widths"]  # width of each item
    heights = instance["heights"]  # height of each item
    n = len(widths)

    # bounds on the dimensions of the whole area, as in the reference: at least the largest item,
    # at most all items side by side
    area_min_x, area_max_x = max(widths), sum(widths)
    area_min_y, area_max_y = max(heights), sum(heights)

    solver = Exact()

    # (pos_x[i], pos_y[i]) = lower left corner of item i. An item has to lie inside the area, so
    # its corner cannot exceed the area size minus the item size (implied by the "within the
    # overall area" constraints below; it only gives the solver a tighter domain).
    pos_x = [f"pos_x_{i}" for i in range(n)]
    pos_y = [f"pos_y_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(pos_x[i], 0, area_max_x - widths[i])
        solver.addVariable(pos_y[i], 0, area_max_y - heights[i])

    # total_x, total_y = dimensions of the larger rectangle
    solver.addVariable("total_x", area_min_x, area_max_x)
    solver.addVariable("total_y", area_min_y, area_max_y)

    # every item has to be within the overall area
    for i in range(n):
        solver.addConstraint([(1, pos_x[i]), (-1, "total_x")], False, 0, True, -widths[i])
        solver.addConstraint([(1, pos_y[i]), (-1, "total_y")], False, 0, True, -heights[i])

    # no overlap: every item has to be fully left of, right of, below or above every other item.
    # Exact has no disjunction, so each of the four options gets a 0/1 variable that switches its
    # linear inequality on (a big-M term of the size of the area relaxes it when the variable is 0),
    # and at least one option has to be switched on.
    for i in range(n):
        for j in range(i + 1, n):
            options = []
            for tag, a, b, size, big in (
                    ("left", pos_x[i], pos_x[j], widths[i], area_max_x),  # i ends before j starts
                    ("right", pos_x[j], pos_x[i], widths[j], area_max_x),  # j ends before i starts
                    ("below", pos_y[i], pos_y[j], heights[i], area_max_y),  # i below j
                    ("above", pos_y[j], pos_y[i], heights[j], area_max_y)):  # j below i
                option = f"{tag}_{i}_{j}"
                solver.addVariable(option, 0, 1)
                solver.addConstraint([(1, a), (-1, b), (big, option)], False, 0, True, big - size)
                options.append((1, option))
            solver.addConstraint(options, True, 1)

    # Objective: the area total_x * total_y. Exact is linear, so the product is built from one
    # 0/1 variable per possible width: is_w[w] = 1 when total_x == w, and rows[w] = total_y if
    # total_x == w, else 0. Then area = sum_w w * rows[w]. (Native addMultiplication is slower to
    # prove optimal than this table.)
    widths_range = range(area_min_x, area_max_x + 1)
    is_w = {}
    rows = {}
    for w in widths_range:
        is_w[w] = f"total_x_is_{w}"
        rows[w] = f"area_row_{w}"
        solver.addVariable(is_w[w], 0, 1)
        solver.addVariable(rows[w], 0, area_max_y)
        # rows[w] <= area_max_y * is_w[w], and rows[w] <= total_y
        solver.addConstraint([(1, rows[w]), (-area_max_y, is_w[w])], False, 0, True, 0)
        solver.addConstraint([(1, rows[w]), (-1, "total_y")], False, 0, True, 0)
        # rows[w] >= total_y - area_max_y * (1 - is_w[w])
        solver.addConstraint([(1, rows[w]), (-1, "total_y"), (-area_max_y, is_w[w])],
                             True, -area_max_y)
    # exactly one width is chosen, and it is total_x
    solver.addConstraint([(1, is_w[w]) for w in widths_range], True, 1, True, 1)
    solver.addConstraint([(w, is_w[w]) for w in widths_range] + [(-1, "total_x")], True, 0, True, 0)

    area_max = area_max_x * area_max_y
    solver.addVariable("area", area_min_x * area_min_y, area_max)
    solver.addConstraint([(w, rows[w]) for w in widths_range] + [(-1, "area")], True, 0, True, 0)
    # the larger rectangle holds all items, so its area is at least the sum of the item areas
    # (implied; it lets the solver prove optimality faster)
    solver.addConstraint([(1, "area")], True, sum(widths[i] * heights[i] for i in range(n)))

    # minimise the area of the larger rectangle
    return (solver,
            {"pos_x": pos_x, "pos_y": pos_y, "total_x": "total_x", "total_y": "total_y"},
            ("minimize", [(1, "area")]))
