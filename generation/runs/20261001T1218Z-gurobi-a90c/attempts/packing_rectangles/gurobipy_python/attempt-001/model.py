"""Rectangle packing: place rectangles without overlap inside an enclosing rectangle of minimum area."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)
    items = range(n)

    # Bounds on the enclosing rectangle, as in the reference: at least the widest
    # (tallest) item, at most all items side by side (stacked).
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    model = gp.Model("packing_rectangles")

    # Bottom-left corner of every item, and the size of the enclosing rectangle.
    pos_x = model.addVars(items, lb=0, ub=max_x, vtype=GRB.INTEGER, name="pos_x")
    pos_y = model.addVars(items, lb=0, ub=max_y, vtype=GRB.INTEGER, name="pos_y")
    total_x = model.addVar(lb=min_x, ub=max_x, vtype=GRB.INTEGER, name="total_x")
    total_y = model.addVar(lb=min_y, ub=max_y, vtype=GRB.INTEGER, name="total_y")

    # Every item lies within the enclosing rectangle.
    for i in items:
        model.addConstr(pos_x[i] + widths[i] <= total_x, name=f"inside_x[{i}]")
        model.addConstr(pos_y[i] + heights[i] <= total_y, name=f"inside_y[{i}]")

    # No overlap: every pair of items is side by side or one above the other.
    # One indicator per relative position; at least one of the four holds.
    for i in items:
        for j in items:
            if i < j:
                side = model.addVars(4, vtype=GRB.BINARY, name=f"side[{i},{j}]")
                model.addConstr((side[0] == 1) >> (pos_x[i] + widths[i] <= pos_x[j]))
                model.addConstr((side[1] == 1) >> (pos_x[j] + widths[j] <= pos_x[i]))
                model.addConstr((side[2] == 1) >> (pos_y[i] + heights[i] <= pos_y[j]))
                model.addConstr((side[3] == 1) >> (pos_y[j] + heights[j] <= pos_y[i]))
                model.addConstr(side.sum() >= 1, name=f"apart[{i},{j}]")

    # The area total_x * total_y, kept linear because a product of two variables
    # would drop the licence limit to 200 variables: width_is[w] is 1 when the
    # enclosing width is w, and part[w] = width_is[w] * total_y by the
    # binary-times-integer encoding.
    widths_range = range(min_x, max_x + 1)
    width_is = model.addVars(widths_range, vtype=GRB.BINARY, name="width_is")
    part = model.addVars(widths_range, lb=0, ub=max_y, vtype=GRB.CONTINUOUS, name="part")
    model.addConstr(width_is.sum() == 1, name="one_width")
    model.addConstr(total_x == gp.quicksum(w * width_is[w] for w in widths_range), name="width_value")
    for w in widths_range:
        model.addConstr(part[w] <= max_y * width_is[w])
        model.addConstr(part[w] >= min_y * width_is[w])
        model.addConstr(part[w] <= total_y - min_y * (1 - width_is[w]))
        model.addConstr(part[w] >= total_y - max_y * (1 - width_is[w]))
    area = gp.quicksum(w * part[w] for w in widths_range)

    # Implied: the enclosing rectangle is at least as large as the items together.
    model.addConstr(area >= sum(widths[i] * heights[i] for i in items), name="area_bound")

    # Minimise the area of the enclosing rectangle.
    model.setObjective(area, GRB.MINIMIZE)

    return model, {
        "pos_x": [pos_x[i] for i in items],
        "pos_y": [pos_y[i] for i in items],
        "total_x": total_x,
        "total_y": total_y,
    }
