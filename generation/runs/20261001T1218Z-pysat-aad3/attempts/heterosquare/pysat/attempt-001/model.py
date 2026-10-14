# Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that the sums of
# all rows, all columns and the two diagonals are different from each other.
from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n = instance["n"]
    top = n * n  # the entries are 1..n^2

    pool = IDPool()
    # x[r][c] = the entry in row r, column c
    x = [[Integer(f"x_{r}_{c}", 1, top, vpool=pool) for c in range(n)] for r in range(n)]
    cells = [cell for row in x for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # all entries are different
    engine.add_alldifferent(cells)
    cnf = engine.clausify()

    # Sums are handled in binary so that the encoding stays small: comparing sums through a
    # one-hot or order encoding of a number up to n^3 is large. Every line holds n cells, so two
    # lines have different sums exactly when they have different sums of (entry - 1), and
    # (entry - 1) < n^2 fits in `entry_bits` bits.
    entry_bits = (top - 1).bit_length()
    line_bits = (n * (top - 1)).bit_length()

    # bit[r][c][k] = bit k of (x[r][c] - 1), tied to the value literals of x[r][c]
    bit = [[[pool.id(("bit", r, c, k)) for k in range(entry_bits)] for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            for value in range(1, top + 1):
                for k in range(entry_bits):
                    is_set = ((value - 1) >> k) & 1
                    cnf.append([-x[r][c].equals(value), bit[r][c][k] if is_set else -bit[r][c][k]])

    # the lines whose sums must differ: n rows, n columns and the two diagonals, each as a list of cells
    lines = [[(r, c) for c in range(n)] for r in range(n)]
    lines += [[(r, c) for r in range(n)] for c in range(n)]
    lines.append([(i, i) for i in range(n)])
    lines.append([(i, n - 1 - i) for i in range(n)])

    # line_sum[j] = the bits of the sum of (entry - 1) over line j: the weighted bits of its cells
    # equal the weighted bits of the sum (the sum bits count with a negative weight)
    line_sum = []
    for j, line in enumerate(lines):
        sum_bits = [pool.id(("sum", j, k)) for k in range(line_bits)]
        lits = [bit[r][c][k] for r, c in line for k in range(entry_bits)] + sum_bits
        weights = [1 << k for _ in line for k in range(entry_bits)] + [-(1 << k) for k in range(line_bits)]
        cnf.extend(PBEnc.equals(lits=lits, weights=weights, bound=0, vpool=pool).clauses)
        line_sum.append(sum_bits)

    # all the line sums are different: for each pair of lines some bit of the two sums differs
    for a, b in combinations(range(len(lines)), 2):
        differs = [pool.id(("differs", a, b, k)) for k in range(line_bits)]
        for k in range(line_bits):
            # differs[k] implies the k-th bits of the two sums are not equal
            cnf.append([-differs[k], line_sum[a][k], line_sum[b][k]])
            cnf.append([-differs[k], -line_sum[a][k], -line_sum[b][k]])
        cnf.append(differs)

    return cnf, {"x": x}
