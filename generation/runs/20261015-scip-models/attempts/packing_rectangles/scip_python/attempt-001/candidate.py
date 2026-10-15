# Rectangular packing: place every item (width w[i], height h[i]) at a position (x[i], y[i])
# inside a rectangle of size total_x by total_y, with no two items overlapping, so that the
# area total_x * total_y of the enclosing rectangle is minimal. Items are not rotated.

from pyscipopt import Model, quicksum


def build(instance):
    w = instance["widths"]
    h = instance["heights"]
    n = len(w)
    I = range(n)
    W = sum(w)  # the enclosing rectangle is never wider than all items side by side
    H = sum(h)  # nor taller than all items stacked

    m = Model()
    x = {i: m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=W) for i in I}  # left edge of item i
    y = {i: m.addVar(name=f"y_{i}", vtype="I", lb=0, ub=H) for i in I}  # bottom edge of item i
    total_x = m.addVar(name="total_x", vtype="I", lb=max(w), ub=W)  # width of the rectangle
    total_y = m.addVar(name="total_y", vtype="I", lb=max(h), ub=H)  # height of the rectangle
    area = m.addVar(name="area", vtype="I", lb=0, ub=W * H)

    # every item lies within the rectangle
    for i in I:
        m.addCons(x[i] + w[i] <= total_x)
        m.addCons(y[i] + h[i] <= total_y)

    # no two items overlap: for each pair, one of four separating relations holds,
    # left of, right of, below or above each other
    for i in I:
        for j in range(i + 1, n):
            left = m.addVar(name=f"left_{i}_{j}", vtype="B")
            right = m.addVar(name=f"right_{i}_{j}", vtype="B")
            below = m.addVar(name=f"below_{i}_{j}", vtype="B")
            above = m.addVar(name=f"above_{i}_{j}", vtype="B")
            m.addCons(left + right + below + above >= 1)
            # item i is to the left of item j
            m.addConsIndicator(x[i] + w[i] <= x[j], binvar=left)
            # item j is to the left of item i
            m.addConsIndicator(x[j] + w[j] <= x[i], binvar=right)
            # item i is below item j
            m.addConsIndicator(y[i] + h[i] <= y[j], binvar=below)
            # item j is below item i
            m.addConsIndicator(y[j] + h[j] <= y[i], binvar=above)

    # the area is the product of the rectangle's width and height
    m.addCons(area == total_x * total_y)
    m.setObjective(area, "minimize")

    # pos_x and pos_y are the item positions; total_x and total_y are the rectangle size
    return m, {
        "pos_x": [x[i] for i in I],
        "pos_y": [y[i] for i in I],
        "total_x": total_x,
        "total_y": total_y,
    }
