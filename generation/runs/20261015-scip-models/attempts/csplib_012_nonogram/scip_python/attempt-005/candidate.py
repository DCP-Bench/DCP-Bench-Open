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
    k = len(blocks)
    # earliest and latest possible start of each block, from the other blocks and gaps
    earliest = [sum(blocks[i] + 1 for i in range(j)) for j in range(k)]
    latest = [n - sum(blocks[i] + 1 for i in range(j, k)) + 1 for j in range(k)]
    start = []
    cover = [[] for _ in range(n)]
    for j, length in enumerate(blocks):
        s = m.addVar(name=f"{name}_start{j}", vtype="I", lb=earliest[j], ub=latest[j])
        start.append(s)
        # block j starts at exactly one position p: one-hot start indicators linked to s
        pos = {}
        for p in range(earliest[j], latest[j] + 1):
            pos[p] = m.addVar(vtype="B", name=f"{name}_b{j}_p{p}")
            for c in range(p, p + length):
                cover[c].append(pos[p])
        m.addCons(quicksum(pos.values()) == 1)
        m.addCons(s == quicksum(p * v for p, v in pos.items()))
        # overlap: squares that every placement of this block covers are shaded
        for c in range(latest[j], earliest[j] + length):
            m.addCons(cells[c] == 1)
    # blocks appear in the order given by the clue, separated by at least one gap
    for j in range(k - 1):
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
