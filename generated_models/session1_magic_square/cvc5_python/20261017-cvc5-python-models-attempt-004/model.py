# Magic square (session1_magic_square), cvc5 pythonic, QF_LIA.
# A magic square is an n x n grid (n != 2) such that each cell contains a different integer
# from 1 to n^2 and the sum of the integers in each row, column and diagonal is equal.
# Find a magic square for a given size n, knowing that the sum of integers of each row,
# column and diagonal has to be equal to n(n^2+ 1)/2 (integer).
# Output: the square as a list of lists (square) of integers.
import cvc5.pythonic as cz


def exactly_one(lits):
    # one-hot helper: at least one of the Booleans is true, and at most one (pairwise)
    if len(lits) == 1:
        return [lits[0]]
    out = [cz.Or(lits)]
    for a in range(len(lits)):
        for b in range(a + 1, len(lits)):
            out.append(cz.Or(cz.Not(lits[a]), cz.Not(lits[b])))
    return out


def build(instance):
    n = instance["n"]
    total = n * n
    # the sum of each row, column and diagonal has to be n(n^2+1)/2 (integer)
    magic = n * (total + 1) // 2

    s = cz.SolverFor("QF_LIA")

    cell = [[cz.Int(f"c_{i}_{j}") for j in range(n)] for i in range(n)]
    # one Boolean per (cell, value) for the values 1..n^2
    hot = [[[cz.Bool(f"x_{i}_{j}_{v}") for v in range(1, total + 1)]
            for j in range(n)] for i in range(n)]

    # each cell contains one integer from 1 to n^2
    for i in range(n):
        for j in range(n):
            s.add(*exactly_one(hot[i][j]))

    # each cell contains a different integer from 1 to n^2: every value is in exactly one cell
    for k in range(total):
        s.add(*exactly_one([hot[i][j][k] for i in range(n) for j in range(n)]))

    # the integer of a cell is the value its chosen Boolean stands for
    for i in range(n):
        for j in range(n):
            for k in range(total):
                s.add(cz.Implies(hot[i][j][k], cell[i][j] == k + 1))

    # redundant, implied by the two rules above: the cells are different,
    # and together they hold the integers 1 to n^2, whose sum is n^2(n^2+1)/2
    flat = [cell[i][j] for i in range(n) for j in range(n)]
    if total >= 2:  # Distinct needs at least two terms
        s.add(cz.Distinct(flat))
    s.add(cz.Sum(flat) == total * (total + 1) // 2)

    # the sum of each row, column and diagonal is n(n^2+1)/2
    for i in range(n):
        s.add(cz.Sum([cell[i][j] for j in range(n)]) == magic)
    for j in range(n):
        s.add(cz.Sum([cell[i][j] for i in range(n)]) == magic)
    s.add(cz.Sum([cell[i][i] for i in range(n)]) == magic)
    s.add(cz.Sum([cell[i][n - 1 - i] for i in range(n)]) == magic)

    outputs = {"square": [[cell[i][j] for j in range(n)] for i in range(n)]}
    return s, outputs
