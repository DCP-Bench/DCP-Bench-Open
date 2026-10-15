# Perfect square placement: pack squares of the given integer sides into a
# square of side `base` so that no two squares overlap and all borders are
# parallel to the border of the packing square.
from pyscipopt import Model


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)
    m = Model()

    # the lower-left corner of square i, with the square inside the packing
    # (x_i + s_i <= base)
    x = [m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=base - sides[i]) for i in range(n)]
    y = [m.addVar(name=f"y_{i}", vtype="I", lb=0, ub=base - sides[i]) for i in range(n)]

    # no overlap: for every pair of squares, one of four separations holds:
    # i left of j, j left of i, i below j, or j below i
    for i in range(n):
        for j in range(i + 1, n):
            left = m.addVar(name=f"left_{i}_{j}", vtype="B")
            right = m.addVar(name=f"right_{i}_{j}", vtype="B")
            below = m.addVar(name=f"below_{i}_{j}", vtype="B")
            above = m.addVar(name=f"above_{i}_{j}", vtype="B")
            # the squares do not overlap: at least one separation holds
            m.addCons(left + right + below + above >= 1)
            # i is left of j: x_i + s_i <= x_j
            m.addConsIndicator(x[j] - x[i] >= sides[i], binvar=left)
            # j is left of i: x_j + s_j <= x_i
            m.addConsIndicator(x[i] - x[j] >= sides[j], binvar=right)
            # i is below j: y_i + s_i <= y_j
            m.addConsIndicator(y[j] - y[i] >= sides[i], binvar=below)
            # j is below i: y_j + s_j <= y_i
            m.addConsIndicator(y[i] - y[j] >= sides[j], binvar=above)

    return m, {"x_coords": x, "y_coords": y}
