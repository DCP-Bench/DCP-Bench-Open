"""Nonogram: colour the cells of a grid so that every row and column shows its list of block lengths, in order."""
import gurobipy as gp
from gurobipy import GRB


def line_cover(model, rule, length, tag):
    """Place the blocks of one row or column; return, for each cell of the line, the linear
    expression that is 1 when the cell is coloured.

    The blocks keep their order and are separated by at least one empty cell, so block k can
    only start between the cells that the blocks before it and after it leave free. Those
    start positions are the only variables; a cell is coloured when some block covers it."""
    blocks = [b for b in rule if b > 0]  # zero entries in the rule are padding
    cover = [gp.LinExpr() for _ in range(length)]
    start = []                           # start[k]: expression for the start cell of block k
    first = 0                            # earliest start of block k: the blocks before it
    for k, size in enumerate(blocks):
        after = sum(b + 1 for b in blocks[k + 1:])
        last = length - size - after     # latest start of block k: room for the blocks after it
        if last < first:
            raise ValueError("rule does not fit the line")
        if last == first:
            # no freedom: the block is at a fixed place, so it needs no variable
            start.append(gp.LinExpr(first))
            for c in range(first, first + size):
                cover[c] += 1
        else:
            begin = model.addVars(range(first, last + 1), vtype=GRB.BINARY, name=f"{tag}_block{k}")
            model.addConstr(begin.sum() == 1, name=f"{tag}_one_start[{k}]")
            start.append(gp.quicksum(s * begin[s] for s in range(first, last + 1)))
            for s in range(first, last + 1):
                for c in range(s, s + size):
                    cover[c] += begin[s]
        first += size + 1
    # Consecutive blocks are separated by at least one empty cell.
    for k in range(len(blocks) - 1):
        model.addConstr(start[k + 1] - start[k] >= blocks[k] + 1, name=f"{tag}_gap[{k}]")
    return cover


def build(instance):
    n_rows, n_cols = instance["rows"], instance["cols"]
    row_rules, col_rules = instance["row_rules"], instance["col_rules"]

    model = gp.Model("nonogram")

    # The rows are described by block start positions; the cells are read from them.
    row_cover = [line_cover(model, row_rules[r], n_cols, f"row{r}") for r in range(n_rows)]
    col_cover = [line_cover(model, col_rules[c], n_rows, f"col{c}") for c in range(n_cols)]

    # Rows and columns describe the same board: a cell is coloured in its row exactly when
    # it is coloured in its column.
    impossible = None
    for r in range(n_rows):
        for c in range(n_cols):
            left, right = row_cover[r][c], col_cover[c][r]
            if left.size() == 0 and right.size() == 0:
                if left.getConstant() != right.getConstant():  # fixed cells that disagree
                    if impossible is None:
                        impossible = model.addVar(ub=0, name="impossible")
                    model.addConstr(impossible == 1, name="fixed_cells_disagree")
                continue
            model.addConstr(left == right, name=f"cell[{r},{c}]")

    board = [[int(cell.getConstant()) if cell.size() == 0 else cell for cell in row] for row in row_cover]
    return model, {"board": board}
