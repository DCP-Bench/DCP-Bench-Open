# Calvin puzzle: fill an n by n grid with the numbers 1..n^2, each exactly once, so that
# the next number is placed vertically or horizontally exactly three squares away from
# the previous one, or diagonally exactly two squares away.
# Model: cvc5 (pythonic), Boolean placement variables B[v][c] (number v+1 in cell c),
# so the solver works on clauses rather than on a Distinct over integers.

from cvc5.pythonic import Bools, Ints, Or, Not, And, If, Sum


def build(instance):
    n = instance["n"]
    N = n * n

    def cell(i, j):
        return i * n + j

    # Cells reachable from cell c by one allowed move.
    def moves(c):
        i, j = divmod(c, n)
        out = []
        for di, dj in [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]:
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < n:
                out.append(cell(a, b))
        return out

    B = [Bools(" ".join(f"b{v}_{c}" for c in range(N))) for v in range(N)]
    X = Ints(" ".join(f"x{c}" for c in range(N)))

    constraints = []

    # Each number 1..n^2 is placed in exactly one square.
    for v in range(N):
        constraints.append(Or([B[v][c] for c in range(N)]))
        for c in range(N):
            for d in range(c + 1, N):
                constraints.append(Or(Not(B[v][c]), Not(B[v][d])))

    # Each square holds exactly one number.
    for c in range(N):
        constraints.append(Or([B[v][c] for v in range(N)]))
        for v in range(N):
            for w in range(v + 1, N):
                constraints.append(Or(Not(B[v][c]), Not(B[w][c])))

    # The next number is placed vertically or horizontally exactly three squares away
    # (a two-square gap), or diagonally exactly two squares away (a one-square gap).
    for v in range(N - 1):
        for c in range(N):
            ok = [B[v + 1][d] for d in moves(c)]
            if not ok:
                constraints.append(Not(B[v][c]))
            elif len(ok) == 1:
                constraints.append(Or(Not(B[v][c]), ok[0]))
            else:
                constraints.append(Or(Not(B[v][c]), Or(ok)))

    # Output: the number in each square, 1-based.
    for c in range(N):
        constraints.append(X[c] == Sum([If(B[v][c], v + 1, 0) for v in range(N)]))

    x = [[X[cell(i, j)] for j in range(n)] for i in range(n)]
    return constraints, {"x": x}
