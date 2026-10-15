from pyscipopt import Model, quicksum

# Nonogram: shade squares of a rows x cols grid so that the runs of shaded squares in
# every row and column match the clues. board[r][c] is 1 for a shaded square, 0 otherwise.


def line_clue(m, cells, clue, name):
    # The runs of shaded squares in `cells` (binary variables) are exactly the blocks of
    # `clue`, in order, with at least one unshaded square between two blocks.
    n = len(cells)
    # zeros in a clue are padding; the blocks are the nonzero entries in order
    blocks = [k for k in clue if k > 0]
    if not blocks:
        # a line with no clue has no shaded square
        for c in cells:
            m.addCons(c == 0)
        return
    # block j starts at exactly one position p: one-hot start variables
    start = []
    cover = [[] for _ in range(n)]
    for j, length in enumerate(blocks):
        pos = {}
        for p in range(n - length + 1):
            pos[p] = m.addVar(vtype="B", name=f"{name}_b{j}_p{p}")
            for c in range(p, p + length):
                cover[c].append(pos[p])
        m.addCons(quicksum(pos.values()) == 1)
        start.append(quicksum(p * v for p, v in pos.items()))
    # blocks appear in the order given by the clue, separated by at least one gap
    for j in range(len(blocks) - 1):
        m.addCons(start[j + 1] >= start[j] + blocks[j] + 1)
    # a square is shaded exactly when a block covers it
    for c in range(n):
        m.addCons(cells[c] == quicksum(cover[c]))


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    m = Model()
    # board[r][c] = 1 if the square in row r, column c is shaded
    board = [[m.addVar(name=f"board_{r}_{c}", vtype="B") for c in range(cols)] for r in range(rows)]
    # each row's runs of shaded squares follow the row clue
    for r in range(rows):
        line_clue(m, board[r], instance["row_rules"][r], f"row{r}")
    # each column's runs of shaded squares follow the column clue
    for c in range(cols):
        line_clue(m, [board[r][c] for r in range(rows)], instance["col_rules"][c], f"col{c}")
    return m, {"board": board}
