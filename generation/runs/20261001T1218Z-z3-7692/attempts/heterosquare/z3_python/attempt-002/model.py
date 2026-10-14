# Heterosquare: fill an n x n square with the distinct integers 1 to n^2 so that the sums of
# the rows, of the columns and of the two diagonals are all different from each other.
import z3


def build(instance):
    n = instance["n"]  # order of the square

    # The unknowns are bit-vectors rather than integers: Z3 solves "all different" over
    # bit-vectors by bit-blasting to a SAT problem, which suits this problem better than
    # integer arithmetic with 49 or more different values. The width holds the largest
    # sum (a row, column or diagonal has n entries of at most n^2, so at most n^3) so
    # nothing wraps around.
    width = (n ** 3).bit_length() + 1

    def const(value):
        return z3.BitVecVal(value, width)

    # x[i][j] is the number in row i, column j; the numbers are 1..n^2.
    x = [[z3.BitVec(f"x_{i}_{j}", width) for j in range(n)] for i in range(n)]
    # Sums of the rows, of the columns and of the two diagonals; the reference lets each
    # sum range over 1..n^3.
    row_sums = [z3.BitVec(f"row_sums_{i}", width) for i in range(n)]
    col_sums = [z3.BitVec(f"col_sums_{j}", width) for j in range(n)]
    diag1 = z3.BitVec("diag1", width)
    diag2 = z3.BitVec("diag2", width)

    solver = z3.Solver()

    for i in range(n):
        for j in range(n):
            solver.add(z3.UGE(x[i][j], const(1)), z3.ULE(x[i][j], const(n * n)))
    for s in row_sums + col_sums + [diag1, diag2]:
        solver.add(z3.UGE(s, const(1)), z3.ULE(s, const(n ** 3)))

    # All the entries of the square are different.
    solver.add(z3.Distinct([x[i][j] for i in range(n) for j in range(n)]))

    # All the sums are different.
    solver.add(z3.Distinct(row_sums + col_sums + [diag1, diag2]))

    # Row sums, column sums and the sums of the main diagonal and the anti-diagonal.
    # Python's sum starts from the integer 0, which Z3 turns into a bit-vector constant.
    for i in range(n):
        solver.add(row_sums[i] == sum(x[i]))
    for j in range(n):
        solver.add(col_sums[j] == sum(x[i][j] for i in range(n)))
    solver.add(diag1 == sum(x[i][i] for i in range(n)))
    solver.add(diag2 == sum(x[i][n - i - 1] for i in range(n)))

    # The declared output is an integer matrix: read the bit-vectors as unsigned numbers.
    return solver, {"x": [[z3.BV2Int(x[i][j]) for j in range(n)] for i in range(n)]}
