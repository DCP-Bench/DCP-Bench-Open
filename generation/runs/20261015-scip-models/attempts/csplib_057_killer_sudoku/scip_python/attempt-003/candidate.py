# Killer sudoku: fill a 9x9 grid with digits 1..9 so that each row, column and nonet
# holds every digit once, and each cage sums to its printed total with no digit repeated.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]  # grid size (9)
    cages = instance["problem"]  # list of [total, [[row, col], ...]], 1-based cells
    digits = range(1, n + 1)
    # nonets are the 3x3 blocks; the grid size fixes the block width
    block = int(round(n ** 0.5))

    m = Model()
    m.hideOutput()

    # one-hot: cell (r, c) holds digit v
    b = {(r, c, v): m.addVar(vtype="B", name=f"b_{r}_{c}_{v}")
         for r in range(n) for c in range(n) for v in digits}
    x = {(r, c): m.addVar(vtype="I", lb=1, ub=n, name=f"x_{r}_{c}")
         for r in range(n) for c in range(n)}
    # each cell holds exactly one digit
    for r in range(n):
        for c in range(n):
            m.addCons(quicksum(b[r, c, v] for v in digits) == 1)
            m.addCons(x[r, c] == quicksum(v * b[r, c, v] for v in digits))

    # each row contains every digit once
    for r in range(n):
        for v in digits:
            m.addCons(quicksum(b[r, c, v] for c in range(n)) == 1)
    # each column contains every digit once
    for c in range(n):
        for v in digits:
            m.addCons(quicksum(b[r, c, v] for r in range(n)) == 1)
    # each nonet (3x3 block) contains every digit once
    for br in range(0, n, block):
        for bc in range(0, n, block):
            for v in digits:
                m.addCons(quicksum(b[r, c, v] for r in range(br, br + block)
                                   for c in range(bc, bc + block)) == 1)

    # each cage sums to its total
    for total, cells in cages:
        m.addCons(quicksum(x[r - 1, c - 1] for r, c in cells) == total)
        # no digit appears more than once in a cage
        for v in digits:
            m.addCons(quicksum(b[r - 1, c - 1, v] for r, c in cells) <= 1)

    # the output is the solution grid
    return m, {"x": [[x[r, c] for c in range(n)] for r in range(n)]}
