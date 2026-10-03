"""Quasigroup existence (QG3): a Latin square of order m whose multiplication satisfies (a*b)*(b*a) = a."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    m = instance["m"]
    elems = range(m)

    model = gp.Model("quasigroup_qg3")
    # A satisfaction problem: search for a feasible table first.
    model.Params.MIPFocus = 1

    # is_[a, b, c] is 1 when a * b = c.
    is_ = model.addVars(elems, elems, elems, vtype=GRB.BINARY, name="is")
    product = [[gp.quicksum(c * is_[a, b, c] for c in elems) for b in elems] for a in elems]

    # Every cell of the table holds exactly one element.
    for a in elems:
        for b in elems:
            model.addConstr(is_.sum(a, b, "*") == 1, name=f"cell[{a},{b}]")

    # Each element occurs once in every row and once in every column.
    for c in elems:
        for a in elems:
            model.addConstr(is_.sum(a, "*", c) == 1, name=f"row[{a},{c}]")
        for b in elems:
            model.addConstr(is_.sum("*", b, c) == 1, name=f"col[{b},{c}]")

    # column_of[u][a]: the column in which row u holds a, so u * column_of[u][a] = a.
    # row_of[w][a]: the row in which column w holds a, so row_of[w][a] * w = a.
    column_of = [[gp.quicksum(w * is_[u, w, a] for w in elems) for a in elems] for u in elems]
    row_of = [[gp.quicksum(u * is_[u, w, a] for u in elems) for a in elems] for w in elems]

    # QG3 property (a*b)*(b*a) = a. When a * b = u, the element b * a must be the column
    # where row u holds a; one indicator per (a, b, u) keeps this linear instead of m^4
    # constraints over pairs of values.
    for a in elems:
        for b in elems:
            for u in elems:
                model.addConstr((is_[a, b, u] == 1) >> (product[b][a] == column_of[u][a]),
                                name=f"qg3[{a},{b},{u}]")

    # The same property read from the other factor: when b * a = w, the element a * b
    # must be the row where column w holds a. It is implied by the constraints above
    # and lets the solver reason from either side.
    for a in elems:
        for b in elems:
            for w in elems:
                model.addConstr((is_[b, a, w] == 1) >> (product[a][b] == row_of[w][a]),
                                name=f"qg3_back[{a},{b},{w}]")

    return model, {"quasigroup": product}
