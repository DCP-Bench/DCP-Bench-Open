"""Solitaire battleships: fill a grid with a fleet of ships (submarines, and longer ships with bow, middle and stern pieces) that touch nowhere, matching the row and column ship counts."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum = instance["rowsum"], instance["colsum"]  # ship cells per row and per column
    fleet = instance["fleet_counts"]                         # [[ship size, how many of that size]]
    hints = instance["hints"]                                # [[row, col, cell value]]
    # How the grid cells are encoded in the output; the problem fixes these numbers.
    WATER, SHIP, CIRCLE = instance["WATER"], instance["_SHIP"], instance["CIRCLE"]
    LEFT, RIGHT, TOP, BOTTOM, MIDDLE = (instance[k] for k in ("LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"))
    R, C = range(rows), range(cols)

    model = gp.Model("solitaire_battleships")

    # A ship of size s >= 2 lies in a straight line, so it is described by where it starts: place[s, 'h', r, c]
    # is 1 for a horizontal ship covering (r, c) .. (r, c + s - 1), place[s, 'v', r, c] for a vertical
    # one covering (r, c) .. (r + s - 1, c). Size 1 is a submarine, which has no direction. This
    # one-ship-one-variable form replaces the reference's one-value-per-cell grid, and a cell's
    # value is read back from the ships that cover it.
    place = {}
    for size, _ in fleet:
        if size == 1:
            for r in R:
                for c in C:
                    place[1, "h", r, c] = model.addVar(vtype=GRB.BINARY, name=f"sub[{r},{c}]")
        else:
            for r in R:
                for c in range(cols - size + 1):
                    place[size, "h", r, c] = model.addVar(vtype=GRB.BINARY, name=f"ship{size}h[{r},{c}]")
            for r in range(rows - size + 1):
                for c in C:
                    place[size, "v", r, c] = model.addVar(vtype=GRB.BINARY, name=f"ship{size}v[{r},{c}]")

    # The fleet has exactly the required number of ships of each size.
    for size, count in fleet:
        model.addConstr(gp.quicksum(v for (s, _, _, _), v in place.items() if s == size) == count,
                        name=f"fleet[{size}]")

    # What a ship covers: the role each of its cells plays in the picture. Horizontal ships have
    # a left end, middle cells and a right end; vertical ones a top, middle cells and a bottom.
    roles = {k: {(r, c): gp.LinExpr() for r in R for c in C}
             for k in ("circle", "left", "right", "top", "bottom", "middle")}
    covers = {(r, c): gp.LinExpr() for r in R for c in C}  # ships (of any size) covering a cell
    for (size, way, r, c), v in place.items():
        if size == 1:
            roles["circle"][r, c] += v
            covers[r, c] += v
        elif way == "h":
            roles["left"][r, c] += v
            roles["right"][r, c + size - 1] += v
            for k in range(size):
                covers[r, c + k] += v
                if 0 < k < size - 1:
                    roles["middle"][r, c + k] += v
        else:
            roles["top"][r, c] += v
            roles["bottom"][r + size - 1, c] += v
            for k in range(size):
                covers[r + k, c] += v
                if 0 < k < size - 1:
                    roles["middle"][r + k, c] += v

    # A cell may also hold the generic ship value (_SHIP). The reference puts no rule on such a
    # cell except the shared ones below, so it is a free ship cell that no other piece touches.
    generic = model.addVars(R, C, vtype=GRB.BINARY, name="generic")
    occupied = {(r, c): covers[r, c] + generic[r, c] for r in R for c in C}

    # A cell is covered by at most one ship, or is a generic ship cell, or is water.
    for r in R:
        for c in C:
            model.addConstr(occupied[r, c] <= 1, name=f"one_piece[{r},{c}]")

    # Row and column sums count every non-water cell as a ship segment.
    for r in R:
        model.addConstr(gp.quicksum(occupied[r, c] for c in C) == rowsum[r], name=f"rowsum[{r}]")
    for c in C:
        model.addConstr(gp.quicksum(occupied[r, c] for r in R) == colsum[c], name=f"colsum[{c}]")

    # Ships do not touch diagonally: of two cells that touch at a corner, at most one is not water.
    for r in range(rows - 1):
        for c in C:
            for c2 in (c - 1, c + 1):
                if 0 <= c2 < cols:
                    model.addConstr(occupied[r, c] + occupied[r + 1, c2] <= 1, name=f"corner[{r},{c},{c2}]")

    # Ships do not touch along a side except within one ship: two neighbouring cells covered by
    # ships are covered by the same ship (which then covers both of them). A generic ship cell
    # cannot touch a cell of a typed ship, but may touch another generic one.
    for r in R:
        for c in C:
            for r2, c2 in ((r, c + 1), (r + 1, c)):
                if r2 < rows and c2 < cols:
                    together = gp.quicksum(
                        v for (s, way, r0, c0), v in place.items()
                        if s > 1 and ((way == "h" and r0 == r and c0 <= c and c2 < c0 + s and r2 == r)
                                      or (way == "v" and c0 == c and r0 <= r and r2 < r0 + s and c2 == c)))
                    model.addConstr(covers[r, c] + covers[r2, c2] <= 1 + together, name=f"side[{r},{c},{r2},{c2}]")
                    model.addConstr(covers[r, c] + generic[r2, c2] <= 1, name=f"typed_generic[{r},{c},{r2},{c2}]")
                    model.addConstr(generic[r, c] + covers[r2, c2] <= 1, name=f"generic_typed[{r},{c},{r2},{c2}]")

    # The value of a cell: the code of the piece it holds, so the grid is one linear expression per cell.
    code = {"circle": CIRCLE, "left": LEFT, "right": RIGHT, "top": TOP, "bottom": BOTTOM, "middle": MIDDLE}
    grid = [[WATER * (1 - occupied[r, c]) + SHIP * generic[r, c]
             + gp.quicksum(code[k] * roles[k][r, c] for k in code)
             for c in C] for r in R]

    # Hints: the given cells hold the given piece.
    for r, c, value in hints:
        if value == WATER:
            model.addConstr(occupied[r, c] == 0, name=f"hint[{r},{c}]")
        elif value == SHIP:
            model.addConstr(generic[r, c] == 1, name=f"hint[{r},{c}]")
        else:
            names = [k for k in code if code[k] == value]
            model.addConstr(gp.quicksum(roles[k][r, c] for k in names) == 1, name=f"hint[{r},{c}]")

    return model, {"grid": grid}
