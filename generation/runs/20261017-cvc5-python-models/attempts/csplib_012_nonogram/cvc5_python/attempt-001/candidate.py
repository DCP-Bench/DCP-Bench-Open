# csplib_012 nonogram: shade squares in a grid so that the blocks of consecutive
# shaded squares in every row and every column satisfy the clues given for that line.
# Output board: 1 for a shaded square, 0 for an unshaded one.
import cvc5.pythonic as cz


def _or(terms):
    return terms[0] if len(terms) == 1 else cz.Or(terms)


def _line(cells, clue, tag):
    # Blocks of consecutive shaded squares, in the order the clue gives them, with at
    # least one unshaded square between two blocks. A clue entry of 0 is padding.
    # Block k starts at start[k] and covers the squares start[k] .. start[k]+length-1.
    n = len(cells)
    lengths = [c for c in clue if c > 0]
    if not lengths:
        # Clue with no blocks: the whole line is unshaded.
        return [cz.Not(c) for c in cells]
    m = len(lengths)
    start = [cz.Int(f"s_{tag}_{k}") for k in range(m)]
    out = []
    # Blocks stay inside the line and keep their order with a gap in between.
    for k in range(m):
        out.append(start[k] >= 0)
        out.append(start[k] + lengths[k] <= n)
    for k in range(m - 1):
        out.append(start[k + 1] >= start[k] + lengths[k] + 1)
    # A square is shaded exactly when some block covers it.
    for j in range(n):
        covers = [cz.And(start[k] <= j, j < start[k] + lengths[k]) for k in range(m)]
        out.append(cells[j] == _or(covers))
    return out


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    grid = [[cz.Bool(f"b_{i}_{j}") for j in range(cols)] for i in range(rows)]
    constraints = []
    # Row clues: each row shows its blocks in order.
    for i in range(rows):
        constraints += _line(grid[i], instance["row_rules"][i], f"r{i}")
    # Column clues: each column shows its blocks in order.
    for j in range(cols):
        column = [grid[i][j] for i in range(rows)]
        constraints += _line(column, instance["col_rules"][j], f"c{j}")
    board = [[cz.If(grid[i][j], 1, 0) for j in range(cols)] for i in range(rows)]
    return constraints, {"board": board}
