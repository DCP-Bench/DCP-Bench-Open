# Nonogram: shade squares of a rows x cols grid so that each row and each column shows its run-length clue.
from pyscipopt import Model, quicksum


def build(instance):
    R = instance["rows"]
    C = instance["cols"]
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]

    m = Model()
    # board[r][c] = 1 if square (r, c) is shaded
    board = [[m.addVar(vtype="B", name=f"shade_{r}_{c}") for c in range(C)] for r in range(R)]

    def line(cells, clue):
        # zeros in a clue are padding; the nonzero entries are the shaded blocks, in order
        blocks = [b for b in clue if b > 0]
        n = len(cells)
        if not blocks:
            # an empty clue: no square in this line is shaded
            for x in cells:
                m.addCons(x == 0)
            return
        # x[j, p] = 1 if block j starts at square p (one-hot start position of each block)
        x = {}
        starts = []
        for j, b in enumerate(blocks):
            for p in range(n - b + 1):
                x[j, p] = m.addVar(vtype="B")
            # block j starts at exactly one position
            m.addCons(quicksum(x[j, p] for p in range(n - b + 1)) == 1)
            starts.append(quicksum(p * x[j, p] for p in range(n - b + 1)))
        # blocks appear in the order of the clue, separated by at least one unshaded square
        for j in range(len(blocks) - 1):
            m.addCons(starts[j + 1] - starts[j] >= blocks[j] + 1)
        # a square is shaded exactly when some block covers it
        for c in range(n):
            covers = [
                x[j, p]
                for j, b in enumerate(blocks)
                for p in range(max(0, c - b + 1), min(c, n - b) + 1)
            ]
            m.addCons(cells[c] == quicksum(covers))

    # row clues
    # each row's blocks match its clue
    for r in range(R):
        line(board[r], row_rules[r])
    # column clues
    # each column's blocks match its clue
    for c in range(C):
        line([board[r][c] for r in range(R)], col_rules[c])

    return m, {"board": board}
