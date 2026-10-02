# Hidato: fill a grid with the numbers 1 to r*c, each used once, some of them given, so that
# every number k + 1 sits in a cell touching the cell of k horizontally, vertically or
# diagonally.
import z3


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[i][j] is the given number, or 0 for an empty cell
    r = len(puzzle)
    c = len(puzzle[0])
    n = r * c  # the numbers are 1..n

    # x[i][j] is the number written in cell (i, j).
    x = [[z3.Int(f"x_{i}_{j}") for j in range(c)] for i in range(r)]

    cells = [(i, j) for i in range(r) for j in range(c)]
    givens = [(puzzle[i][j], (i, j)) for (i, j) in cells if puzzle[i][j] > 0]

    def touching(a, b):
        """Cells a and b are different and touch horizontally, vertically or diagonally."""
        return a != b and max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    # Candidate cells for each number, found from the givens: number k can sit in cell p only
    # if p is not a given cell holding another number, and every given number v is at least
    # as many king steps away from p as |k - v|, since consecutive numbers touch.
    # This only removes cells in which the number cannot be, to give Z3 fewer literals.
    def possible(k, p):
        if puzzle[p[0]][p[1]] > 0 and puzzle[p[0]][p[1]] != k:
            return False
        for v, q in givens:
            if max(abs(p[0] - q[0]), abs(p[1] - q[1])) > abs(k - v):
                return False
        return True

    # where[k][p] is true if number k is in cell p (only for the candidate cells).
    where = {k: {p: z3.Bool(f"where_{k}_{p[0]}_{p[1]}") for p in cells if possible(k, p)}
             for k in range(1, n + 1)}

    solver = z3.Solver()

    # A cell holds a number between 1 and n, and the number is the one whose literal is true.
    for (i, j) in cells:
        solver.add(x[i][j] >= 1, x[i][j] <= n)
    for k in range(1, n + 1):
        for p, w in where[k].items():
            solver.add(z3.Implies(w, x[p[0]][p[1]] == k))

    # Every number is in exactly one cell, and every cell holds exactly one number
    # (together they say that the numbers are all different, and fill the grid).
    for k in range(1, n + 1):
        solver.add(z3.PbEq([(w, 1) for w in where[k].values()], 1) if where[k] else z3.BoolVal(False))
    for p in cells:
        holders = [(where[k][p], 1) for k in range(1, n + 1) if p in where[k]]
        solver.add(z3.PbEq(holders, 1) if holders else z3.BoolVal(False))

    # The given numbers are in their cells.
    for v, p in givens:
        solver.add(where[v].get(p, z3.BoolVal(False)))

    # Consecutive numbers touch: if k is in cell p, then k + 1 is in a cell touching p, and
    # if k + 1 is in cell p, then k is in a cell touching p.
    for k in range(1, n):
        for p, w in where[k].items():
            solver.add(z3.Implies(w, z3.Or([where[k + 1][q] for q in where[k + 1] if touching(p, q)])))
        for p, w in where[k + 1].items():
            solver.add(z3.Implies(w, z3.Or([where[k][q] for q in where[k] if touching(p, q)])))

    return solver, {"x": x}
