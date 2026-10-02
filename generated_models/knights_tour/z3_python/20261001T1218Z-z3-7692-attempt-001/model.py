# Knight's tour: a knight visits every square of an n x n chessboard exactly once, moving as
# a knight does, without having to return to its start. The squares are numbered with the
# move number 0..n*n-1.
import z3


def build(instance):
    n = instance["n"]  # side of the chessboard
    cells = [(i, j) for i in range(n) for j in range(n)]
    last = n * n - 1   # the move numbers are 0..last

    # x[i][j] is the move number at which the knight visits square (i, j).
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # Knight's moves, and the squares a knight on (i, j) can jump to.
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    def jumps(i, j):
        return [(i + di, j + dj) for di, dj in knight_moves
                if 0 <= i + di < n and 0 <= j + dj < n]

    # visit[k][p] is true if the knight is on square p at move number k. This stands in for
    # "x[p] == k"; the Boolean form lets Z3 use cardinality constraints for the permutation
    # and clauses for the knight's jumps, instead of integer equalities.
    visit = [{p: z3.Bool(f"visit_{k}_{p[0]}_{p[1]}") for p in cells} for k in range(last + 1)]
    # color0 is the color (parity of i + j) of the starting square. A knight's jump changes
    # the color of the square, so move k is on a square of color color0 xor (k odd).
    color0 = z3.Bool("color0")

    solver = z3.Solver()

    # x tells the move number of each square: it is the k of the visit literal that is true.
    for (i, j) in cells:
        solver.add(x[i][j] >= 0, x[i][j] <= last)
    for k in range(last + 1):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], x[p[0]][p[1]] == k))

    # Every square is visited exactly once, and every move number is on exactly one square
    # (all squares have different numbers, which are exactly 0..n*n-1).
    for p in cells:
        solver.add(z3.PbEq([(visit[k][p], 1) for k in range(last + 1)], 1))
    for k in range(last + 1):
        solver.add(z3.PbEq([(visit[k][p], 1) for p in cells], 1))

    # Knight's moves: the square after move k is a knight's jump away from the square of
    # move k, and the square before it is a knight's jump away too. (The reference says
    # that exactly one neighbouring square holds the next and the previous number; as
    # the numbers are all different, "at least one" is the same.)
    for k in range(last):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], z3.Or([visit[k + 1][q] for q in jumps(*p)])))
    for k in range(1, last + 1):
        for p in cells:
            solver.add(z3.Implies(visit[k][p], z3.Or([visit[k - 1][q] for q in jumps(*p)])))

    # Implied by the jumps changing the square color each time: move k is on a square of
    # color color0, flipped when k is odd.
    for k in range(last + 1):
        for p in cells:
            on_color_1 = (p[0] + p[1]) % 2 == 1
            same_color_as_start = z3.Not(color0) if on_color_1 else color0
            if k % 2 == 0:
                solver.add(z3.Implies(visit[k][p], same_color_as_start))
            else:
                solver.add(z3.Implies(visit[k][p], z3.Not(same_color_as_start)))

    return solver, {"x": x}
