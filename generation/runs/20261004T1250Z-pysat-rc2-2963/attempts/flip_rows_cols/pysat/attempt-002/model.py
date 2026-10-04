# Flip rows and columns (Einav's puzzle): choose a sign for every row and
# column of a matrix so that, after multiplying each entry by its row and
# column sign, every row and column sums to zero or more, and the overall sum
# is as small as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    matrix = instance["input_matrix"]
    rows = len(matrix)
    cols = len(matrix[0])

    pool = IDPool()
    # The signs, -1..1 as in the reference; 0 is excluded below. Direct
    # encoding: a value literal for +1.
    row_signs = [Integer(f"row_signs_{i}", -1, 1, vpool=pool) for i in range(rows)]
    col_signs = [Integer(f"col_signs_{j}", -1, 1, vpool=pool) for j in range(cols)]
    engine = IntegerEngine(vars=row_signs + col_signs, vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A sign is -1 or 1, never 0.
    for s in row_signs + col_signs:
        formula.append([-s.equals(0)])
    row_up = [s.equals(1) for s in row_signs]
    col_up = [s.equals(1) for s in col_signs]

    # keep[i][j] is true when entry (i, j) keeps its sign, i.e. its row and
    # column signs agree; the flipped entry is then a[i][j], otherwise
    # -a[i][j]. So the entry is 2 * a[i][j] * keep[i][j] - a[i][j].
    keep = [[pool.id(("keep", i, j)) for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            k, r, c = keep[i][j], row_up[i], col_up[j]
            formula.append([-k, -r, c])
            formula.append([-k, r, -c])
            formula.append([k, r, c])
            formula.append([k, -r, -c])

    def within(cells, low, high):
        # low <= sum of the flipped entries in cells <= high. The flipped
        # entry is |a| when its literal below holds and -|a| otherwise, where
        # the literal is keep for a positive entry and not keep for a
        # negative one. So the sum is 2 * sum(|a| * lit) - sum(|a|), and the
        # bounds become low + sum(|a|) <= sum(2 * |a| * lit) <= high +
        # sum(|a|). PBEnc refuses a negative bound ("Wrong bound"), which
        # this form never needs.
        lits, weights = [], []
        for i, j in cells:
            a = matrix[i][j]
            if a != 0:
                lits.append(keep[i][j] if a > 0 else -keep[i][j])
                weights.append(2 * abs(a))
        mass = sum(weights) // 2
        if low + mass > 0:
            formula.extend(PBEnc.geq(lits=lits, weights=weights,
                                     bound=low + mass, vpool=pool).clauses)
        if high + mass < sum(weights):
            formula.extend(PBEnc.leq(lits=lits, weights=weights,
                                     bound=high + mass, vpool=pool).clauses)

    # Every flipped entry lies in -100..100, the domain of x in the
    # reference; flipping keeps the magnitude, so this is a check on the data.
    if any(abs(v) > 100 for row in matrix for v in row):
        formula.append([])

    # Every row sums to zero or more (row_sums has domain 0..300).
    for i in range(rows):
        within([(i, j) for j in range(cols)], 0, 300)
    # Every column sums to zero or more (col_sums has domain 0..300).
    for j in range(cols):
        within([(i, j) for i in range(rows)], 0, 300)
    # The overall sum lies in 0..1000, the domain of total_sum.
    within([(i, j) for i in range(rows) for j in range(cols)], 0, 1000)

    # Minimise the overall sum, sum(2 * a * keep) - sum(a). A positive entry
    # pays |a| when it keeps its sign; a negative entry pays |a| when it is
    # flipped to positive. That is half the overall sum plus a constant,
    # which does not move the optimum.
    for i in range(rows):
        for j in range(cols):
            a = matrix[i][j]
            if a > 0:
                formula.append([-keep[i][j]], weight=a)
            elif a < 0:
                formula.append([keep[i][j]], weight=-a)

    return formula, {"row_signs": row_signs, "col_signs": col_signs}
