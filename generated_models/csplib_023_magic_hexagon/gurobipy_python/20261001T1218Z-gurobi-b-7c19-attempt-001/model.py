"""Magic hexagon (CSPLib 23): place 1..NUM_CELLS in a hexagon so that every row and diagonal has the same sum."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    cells_count = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]

    # A hexagon of side s has 3s^2 - 3s + 1 cells (19 for s = 3).
    side = 1
    while 3 * side * side - 3 * side + 1 < cells_count:
        side += 1
    if 3 * side * side - 3 * side + 1 != cells_count:
        raise ValueError("NUM_CELLS is not the size of a hexagon")

    # Cells in reading order (A, B, C on the top row, then D..G, ...), in axial
    # coordinates (q, r): r is the row, and the two diagonal directions are the
    # lines of constant q and of constant q + r.
    rad = side - 1
    cells = [(q, r) for r in range(-rad, rad + 1)
             for q in range(max(-rad, -rad - r), min(rad, rad - r) + 1)]
    values = range(1, cells_count + 1)

    model = gp.Model("magic_hexagon")

    # put[c, v] = 1 when cell c holds number v; LD[c] reads the number back.
    put = model.addVars(len(cells), values, vtype=GRB.BINARY, name="put")
    LD = [gp.quicksum(v * put[c, v] for v in values) for c in range(len(cells))]

    # Each cell holds one number, and each of 1..NUM_CELLS is used exactly once.
    for c in range(len(cells)):
        model.addConstr(put.sum(c, "*") == 1, name=f"one_number[{c}]")
    for v in values:
        model.addConstr(put.sum("*", v) == 1, name=f"used_once[{v}]")

    # Every row and both kinds of diagonal sum to the magic constant.
    lines = {}
    for c, (q, r) in enumerate(cells):
        for key in (("row", r), ("diag", q), ("anti", q + r)):
            lines.setdefault(key, []).append(c)
    for (kind, k), members in lines.items():
        model.addConstr(gp.quicksum(LD[c] for c in members) == magic, name=f"{kind}[{k}]")

    return model, {"LD": LD}
