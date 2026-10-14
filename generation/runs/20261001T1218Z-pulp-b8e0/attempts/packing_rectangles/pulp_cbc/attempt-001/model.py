"""Packing rectangles: place rectangular items (given widths and heights, no rotation) inside
a larger rectangle so that no two items overlap and all items lie within it. Minimise the
area of the larger rectangle.

The model reports the lower-left position of every item, counted from 0, and the width and
height of the larger rectangle.
"""
import pulp


def build(instance):
    widths = instance["widths"]  # widths of the items
    heights = instance["heights"]  # heights of the items
    n = len(widths)

    # Smallest and largest size of the larger rectangle (the same bounds as the reference):
    # it must hold the widest / tallest item, and putting all items side by side (or one above
    # the other) always fits.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    problem = pulp.LpProblem("packing_rectangles", pulp.LpMinimize)

    # position of the lower-left corner of every item
    pos_x = [pulp.LpVariable(f"pos_x_{i}", 0, max_x, cat="Integer") for i in range(n)]
    pos_y = [pulp.LpVariable(f"pos_y_{i}", 0, max_y, cat="Integer") for i in range(n)]

    # width and height of the larger rectangle
    total_x = pulp.LpVariable("total_x", min_x, max_x, cat="Integer")
    total_y = pulp.LpVariable("total_y", min_y, max_y, cat="Integer")

    # every item lies within the larger rectangle
    for i in range(n):
        problem += pos_x[i] + widths[i] <= total_x
        problem += pos_y[i] + heights[i] <= total_y

    # No overlap: for every two items, one is left of, right of, below or above the other.
    # side[(i, j)][k] = 1 if the k-th of those four holds. Big-M is the largest slack the
    # inequality can need: the sum of the widths (heights), the most a position plus a size
    # can reach.
    for i in range(n):
        for j in range(i + 1, n):
            side = [pulp.LpVariable(f"side_{i}_{j}_{k}", cat="Binary") for k in range(4)]
            problem += pos_x[i] + widths[i] <= pos_x[j] + max_x * (1 - side[0])
            problem += pos_x[j] + widths[j] <= pos_x[i] + max_x * (1 - side[1])
            problem += pos_y[i] + heights[i] <= pos_y[j] + max_y * (1 - side[2])
            problem += pos_y[j] + heights[j] <= pos_y[i] + max_y * (1 - side[3])
            problem += pulp.lpSum(side) >= 1

    # The objective is the area total_x * total_y, a product of two variables. total_x is
    # written as a choice among its possible values, wide[x] = 1 if total_x = x, and the
    # height is split over the choices: tall[x] is total_y if total_x = x and 0 otherwise.
    # Then the area is the sum of x * tall[x].
    wide = {x: pulp.LpVariable(f"wide_{x}", cat="Binary") for x in range(min_x, max_x + 1)}
    tall = {x: pulp.LpVariable(f"tall_{x}", 0, max_y) for x in wide}
    problem += pulp.lpSum(wide.values()) == 1
    problem += total_x == pulp.lpSum(x * wide[x] for x in wide)
    problem += total_y == pulp.lpSum(tall.values())
    for x in wide:
        problem += tall[x] <= max_y * wide[x]

    # minimise the area of the larger rectangle
    problem += pulp.lpSum(x * tall[x] for x in wide)

    return problem, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
