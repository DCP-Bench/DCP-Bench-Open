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
    row_cells = [[(i, j) for j in range(cols)] for i in range(rows)]
    col_cells = [[(i, j) for i in range(rows)] for j in range(cols)]
    all_cells = [cell for line in row_cells for cell in line]

    pool = IDPool()
    # The signs, -1..1 as in the reference; 0 is excluded below. Direct
    # encoding: a value literal for +1.
    row_signs = [Integer(f"row_signs_{i}", -1, 1, vpool=pool) for i in range(rows)]
    col_signs = [Integer(f"col_signs_{j}", -1, 1, vpool=pool) for j in range(cols)]
    # row_sum[i] is the sum of row i after flipping, 0..300 as row_sums in
    # the reference, and never more than the sum of the row's magnitudes.
    # Order encoding: the objective pays one per threshold it reaches.
    row_sum = [Integer(f"row_sum_{i}", 0,
                       min(300, sum(abs(matrix[i][j]) for j in range(cols))),
                       encoding="order", vpool=pool)
               for i in range(rows)]
    engine = IntegerEngine(vars=row_signs + col_signs + row_sum, vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A sign is -1 or 1, never 0.
    for s in row_signs + col_signs:
        formula.append([-s.equals(0)])
    row_up = [s.equals(1) for s in row_signs]
    col_up = [s.equals(1) for s in col_signs]

    # keep[i][j] is true when entry (i, j) keeps its sign, i.e. its row and
    # column signs agree; the flipped entry is then a[i][j], otherwise
    # -a[i][j].
    keep = [[pool.id(("keep", i, j)) for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            k, r, c = keep[i][j], row_up[i], col_up[j]
            formula.append([-k, -r, c])
            formula.append([-k, r, -c])
            formula.append([k, r, c])
            formula.append([k, -r, -c])

    def positive(cells):
        # The flipped entry is |a| when its literal holds and -|a| otherwise;
        # the literal is keep for a positive entry and not keep for a
        # negative one. So the sum over cells is
        # sum(2 * |a| * lit) - mass, with mass = sum(|a|). Writing it this
        # way keeps every PBEnc bound non-negative, which PBEnc requires
        # ("Wrong bound" otherwise).
        lits, weights = [], []
        for i, j in cells:
            a = matrix[i][j]
            if a != 0:
                lits.append(keep[i][j] if a > 0 else -keep[i][j])
                weights.append(2 * abs(a))
        return lits, weights, sum(weights) // 2

    def within(cells, low, high):
        # low <= sum of the flipped entries in cells <= high.
        lits, weights, mass = positive(cells)
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
    for cells in row_cells:
        within(cells, 0, 300)
    # Every column sums to zero or more (col_sums has domain 0..300).
    for cells in col_cells:
        within(cells, 0, 300)
    # The overall sum lies in 0..1000, the domain of total_sum.
    within(all_cells, 0, 1000)

    # row_sum[i] is at least the flipped row's sum:
    # sum(2 * |a| * lit) - row_sum[i] <= mass.
    for i, cells in enumerate(row_cells):
        lits, weights, mass = positive(cells)
        top = min(300, mass)
        steps = [row_sum[i].ge(v) for v in range(1, top + 1)]
        if lits:
            formula.extend(PBEnc.leq(lits=lits + steps,
                                     weights=weights + [-1] * len(steps),
                                     bound=mass, vpool=pool).clauses)

    # Minimise the overall sum, which is the sum of the row sums: each unit
    # of each row sum pays 1. Paying per row sum, rather than per entry,
    # leaves RC2 a cost that starts at zero instead of at half the total
    # magnitude, so far fewer cores are needed to prove the optimum.
    for i in range(rows):
        top = min(300, positive(row_cells[i])[2])
        for v in range(1, top + 1):
            formula.append([-row_sum[i].ge(v)], weight=1)

    return formula, {"row_signs": row_signs, "col_signs": col_signs}
