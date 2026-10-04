# Flip rows and columns (Einav's puzzle): choose a sign for every row and
# column of a matrix so that, after multiplying each entry by its row and
# column sign, every row and column sums to zero or more, and the overall sum
# is as small as possible.
from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import EncType, PBEnc

TOTAL_MAX = 1000  # domain of total_sum in the reference
LINE_MAX = 300    # domain of row_sums and col_sums in the reference


def build(instance):
    matrix = instance["input_matrix"]
    rows = len(matrix)
    cols = len(matrix[0])

    pool = IDPool()
    # The signs, -1..1 as in the reference; 0 is excluded below. Direct
    # encoding: a value literal for +1.
    row_signs = [Integer(f"row_signs_{i}", -1, 1, vpool=pool) for i in range(rows)]
    col_signs = [Integer(f"col_signs_{j}", -1, 1, vpool=pool) for j in range(cols)]
    # total_sum, 0..1000 as in the reference. Order encoding: the objective
    # pays per threshold reached.
    total = Integer("total_sum", 0, TOTAL_MAX, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=row_signs + col_signs + [total], vpool=pool)

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
        # negative one. So the sum over cells is sum(2 * |a| * lit) - mass,
        # with mass = sum(|a|). Written this way every PBEnc bound is
        # non-negative, which PBEnc requires ("Wrong bound" otherwise).
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
    for i in range(rows):
        within([(i, j) for j in range(cols)], 0, LINE_MAX)
    # Every column sums to zero or more (col_sums has domain 0..300).
    for j in range(cols):
        within([(i, j) for i in range(rows)], 0, LINE_MAX)

    # total_sum is at least the overall sum (and the overall sum at least
    # 0): sum(2 * |a| * lit) - mass <= sum of total's thresholds reached,
    # i.e. sum(2 * |a| * lit) + (thresholds not reached) <= mass + 1000.
    # Its upper bound 1000 is the reference's bound on the overall sum.
    # The adder encoding keeps this constraint over a thousand threshold
    # literals small; PBEnc's default would build a BDD over them.
    cells = [(i, j) for i in range(rows) for j in range(cols)]
    lits, weights, mass = positive(cells)
    if mass > 0:
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=mass,
                                 vpool=pool).clauses)
    steps = [-total.ge(v) for v in range(1, TOTAL_MAX + 1)]
    formula.extend(PBEnc.leq(lits=lits + steps,
                             weights=weights + [1] * len(steps),
                             bound=mass + TOTAL_MAX, vpool=pool,
                             encoding=EncType.adder).clauses)

    # Minimise the overall sum. Threshold v of total_sum, when reached, pays
    # a weight that grows with v in blocks: the cost is then a strictly
    # increasing function of total_sum, so it has the same minimisers as the
    # sum itself. Blocks of about sqrt(1000) equal weights let stratified
    # RC2 treat each block as its own level, highest first, so it closes in
    # on the optimum from above with a few satisfiable calls. Weight 1 per
    # unit of the sum instead raises the lower bound one core at a time,
    # with optima in the hundreds, and ran out of time.
    block = isqrt(TOTAL_MAX) + 1
    for v in range(1, TOTAL_MAX + 1):
        formula.append([-total.ge(v)], weight=1 + (v - 1) // block)

    return formula, {"row_signs": row_signs, "col_signs": col_signs}
