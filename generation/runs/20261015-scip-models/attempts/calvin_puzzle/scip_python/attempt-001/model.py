# Calvin puzzle: fill an n by n grid with the numbers 1..n*n, each once, so that
# each number is placed 3 squares away horizontally or vertically from the previous
# number, or exactly 2 squares away diagonally. The output is the completed grid.

from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    K = n * n
    cells = [(r, c) for r in range(n) for c in range(n)]

    # Two cells are a legal step if they are 3 apart horizontally or vertically,
    # or 2 apart on both axes (diagonally).
    def legal_step(a, b):
        dr = abs(a[0] - b[0])
        dc = abs(a[1] - b[1])
        return (dr == 3 and dc == 0) or (dr == 0 and dc == 3) or (dr == 2 and dc == 2)

    m = Model()

    # p[k, r, c] = 1 if the number k is written in the square (r, c)
    p = {(k, r, c): m.addVar(name=f"p_{k}_{r}_{c}", vtype="B")
         for k in range(1, K + 1) for (r, c) in cells}

    # each number is written in exactly one square
    for k in range(1, K + 1):
        m.addCons(quicksum(p[k, r, c] for (r, c) in cells) == 1)

    # each square holds exactly one number
    for (r, c) in cells:
        m.addCons(quicksum(p[k, r, c] for k in range(1, K + 1)) == 1)

    # the next number is placed a legal step away from the previous number
    for k in range(1, K):
        for a in cells:
            # if number k is in square a, number k+1 is in a square reachable from a
            nbrs = [b for b in cells if legal_step(a, b)]
            m.addCons(p[k, a[0], a[1]] <= quicksum(p[k + 1, b[0], b[1]] for b in nbrs))

    # the grid entry of a square is the number written in it
    x = [[quicksum(k * p[k, r, c] for k in range(1, K + 1)) for c in range(n)]
         for r in range(n)]

    m.setObjective(0)
    return m, {"x": x}
