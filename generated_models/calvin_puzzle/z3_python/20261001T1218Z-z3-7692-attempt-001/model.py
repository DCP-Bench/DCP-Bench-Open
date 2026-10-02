# Calvin puzzle: fill an n x n grid with the numbers 1 to n*n, each used once, so that every
# number k + 1 is placed three squares away from k horizontally or vertically (two squares
# gap), or two squares away diagonally (one square gap).
import z3


def build(instance):
    n = instance["n"]  # side of the grid
    cells = [(i, j) for i in range(n) for j in range(n)]
    total = n * n      # the numbers are 1..n*n

    # x[i][j] is the number written in cell (i, j).
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # The possible steps from one number to the next: 3 squares horizontally or vertically,
    # or 2 squares in both directions (diagonally).
    steps = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    def reach(p):
        return [(p[0] + di, p[1] + dj) for di, dj in steps
                if 0 <= p[0] + di < n and 0 <= p[1] + dj < n]

    # where[k][p] is true if number k is in cell p. This stands in for "x[p] == k"; the
    # Boolean form lets Z3 use cardinality constraints for the all-different condition and
    # clauses for the moves, instead of an element constraint for each number.
    where = {k: {p: z3.Bool(f"where_{k}_{p[0]}_{p[1]}") for p in cells}
             for k in range(1, total + 1)}

    solver = z3.Solver()

    # x tells the number of each cell: it is the k whose literal is true there.
    for (i, j) in cells:
        solver.add(x[i][j] >= 1, x[i][j] <= total)
    for k in range(1, total + 1):
        for p in cells:
            solver.add(z3.Implies(where[k][p], x[p[0]][p[1]] == k))

    # All the numbers are different: every number is in exactly one cell and every cell
    # holds exactly one number.
    for p in cells:
        solver.add(z3.PbEq([(where[k][p], 1) for k in range(1, total + 1)], 1))
    for k in range(1, total + 1):
        solver.add(z3.PbEq([(where[k][p], 1) for p in cells], 1))

    # Moves: if k is in cell p, then k + 1 is in a cell a step away from p, and if k + 1 is
    # in cell p then k is in a cell a step away from p (steps can be taken backwards too).
    for k in range(1, total):
        for p in cells:
            solver.add(z3.Implies(where[k][p], z3.Or([where[k + 1][q] for q in reach(p)])))
            solver.add(z3.Implies(where[k + 1][p], z3.Or([where[k][q] for q in reach(p)])))

    return solver, {"x": x}
