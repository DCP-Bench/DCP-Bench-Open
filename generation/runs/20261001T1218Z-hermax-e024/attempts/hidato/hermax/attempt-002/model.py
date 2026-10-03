# Hidato: fill a grid with the numbers 1..rows*cols, each once, keeping the
# given numbers, so that consecutive numbers sit in cells that touch
# horizontally, vertically or diagonally.
import functools
import operator

from hermax.model import Model


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number,
    which matters here because the vectors have one entry per cell of the grid.
    """
    if len(lits) == 1:
        m &= lits[0]
        return
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[i][j] = given number, 0 for a cell to fill in
    rows = len(puzzle)
    cols = len(puzzle[0])
    total = rows * cols  # numbers run from 1 to total
    givens = [(i, j, puzzle[i][j]) for i in range(rows) for j in range(cols) if puzzle[i][j] > 0]

    # Which numbers each cell can hold. A given number stays in its cell. Any
    # other cell can hold k only if it is compatible with every given number v:
    # consecutive numbers sit at most one cell apart, so numbers k and v sit at
    # most |k - v| cells apart, and a cell at distance d from the cell of v can
    # only hold numbers that differ from v by at least d. This follows from the
    # rules and keeps the number of variables small on a large grid.
    allowed = {}
    for i in range(rows):
        for j in range(cols):
            if puzzle[i][j] > 0:
                allowed[(i, j)] = [puzzle[i][j]]
            else:
                allowed[(i, j)] = [k for k in range(1, total + 1)
                                   if all(max(abs(i - gi), abs(j - gj)) <= abs(k - v) for gi, gj, v in givens)]

    m = Model()
    # holds[(i, j, k)] = cell (i, j) contains number k (only for numbers the cell can hold)
    holds = {(i, j, k): m.bool(f"holds_{i}_{j}_{k}")
             for (i, j), ks in allowed.items() for k in ks}
    # x[i][j] = the number written in cell (i, j) (the declared output). Its range
    # is the range of numbers the cell can hold; a cell with one candidate gets a
    # range of two values and is fixed to the candidate below.
    low = {c: min(ks) for c, ks in allowed.items()}
    high = {c: max(ks) if len(ks) > 1 else ks[0] + 1 for c, ks in allowed.items()}
    x = [[m.int(f"x_{i}_{j}", low[(i, j)], high[(i, j)]) for j in range(cols)] for i in range(rows)]

    # every cell holds one number
    for (i, j), ks in allowed.items():
        exactly_one(m, [holds[(i, j, k)] for k in ks], f"cell_{i}_{j}")
    # every number is in one cell
    for k in range(1, total + 1):
        exactly_one(m, [holds[(i, j, k)] for (i, j) in allowed if (i, j, k) in holds], f"number_{k}")
    # x shows the number held: holding k means x >= k and not x >= k + 1 (the
    # comparison that would fall outside the range of x is already settled)
    for (i, j), ks in allowed.items():
        for k in ks:
            if k > low[(i, j)]:
                m &= (~holds[(i, j, k)] | (x[i][j] >= k))
            if k < high[(i, j)]:
                m &= (~holds[(i, j, k)] | ~(x[i][j] >= k + 1))

    # The cells touching (i, j), diagonals included (and inside the grid).
    def neighbours(i, j):
        return [(i + di, j + dj)
                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (di, dj) != (0, 0) and 0 <= i + di < rows and 0 <= j + dj < cols]

    # Consecutive numbers touch: if a cell holds k, then one of the cells around
    # it holds k + 1 (the next number is never in the same cell, as each cell
    # holds one number). The same is stated backwards, a cell holding k + 1 has k
    # next to it; this is implied by the forward form but helps the solver.
    for (i, j), ks in allowed.items():
        around = neighbours(i, j)
        for k in ks:
            if k < total:
                following = [holds[(a, b, k + 1)] for a, b in around if (a, b, k + 1) in holds]
                if following:
                    m &= (~holds[(i, j, k)] | functools.reduce(operator.or_, following))
                else:  # no cell around can hold k + 1
                    m &= ~holds[(i, j, k)]
            if k > 1:
                preceding = [holds[(a, b, k - 1)] for a, b in around if (a, b, k - 1) in holds]
                if preceding:
                    m &= (~holds[(i, j, k)] | functools.reduce(operator.or_, preceding))
                else:  # no cell around can hold k - 1
                    m &= ~holds[(i, j, k)]

    return m, {"x": x}
