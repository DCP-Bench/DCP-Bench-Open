# KenKen: fill an n x n grid with digits 1 to n so that each row and each column
# holds every digit once, and each cage's digits achieve its target by one of
# the operations the puzzle allows.
from itertools import product
from math import prod

from pyscipopt import Model, quicksum


def reaches(values, target):
    """True if the cage's digits reach the target under an allowed operation.

    The instance gives no operator for a cage, so every operator the puzzle allows
    for that cage size is accepted: a single cell is its own value; a two-cell cage
    may use sum, difference, product or exact quotient; a larger cage may use sum or
    product (subtraction and division apply only to two cells).
    """
    k = len(values)
    if k == 1:
        return values[0] == target
    if k == 2:
        a, b = values
        return (
            a + b == target
            or abs(a - b) == target
            or a * b == target
            or max(a, b) == target * min(a, b)
        )
    return sum(values) == target or prod(values) == target


def build(instance):
    n = instance["n"]
    D = range(1, n + 1)
    cages = [(target, [tuple(cell) for cell in cells]) for target, cells in instance["problem"]]

    m = Model("kenken")

    # b[r, c, v] = 1 if cell (r, c) holds digit v
    b = {(r, c, v): m.addVar(name=f"b_{r}_{c}_{v}", vtype="B") for r in D for c in D for v in D}
    x = {}
    # each cell holds exactly one digit
    for r in D:
        for c in D:
            m.addCons(quicksum(b[r, c, v] for v in D) == 1)
            x[r, c] = quicksum(v * b[r, c, v] for v in D)

    # each row contains exactly one of each digit
    for r in D:
        for v in D:
            m.addCons(quicksum(b[r, c, v] for c in D) == 1)
    # each column contains exactly one of each digit
    for c in D:
        for v in D:
            m.addCons(quicksum(b[r, c, v] for r in D) == 1)

    # each cage's digits achieve its target: pick one digit pattern that reaches the
    # target, and link the cells to that pattern
    for target, cells in cages:
        patterns = [p for p in product(D, repeat=len(cells)) if reaches(p, target)]
        y = [m.addVar(name=f"y_{cells[0][0]}_{cells[0][1]}_{j}", vtype="B") for j in range(len(patterns))]
        # the cage takes exactly one of its patterns
        m.addCons(quicksum(y) == 1)
        for i, (r, c) in enumerate(cells):
            for v in D:
                # the cell holds digit v exactly when the chosen pattern has v at this cell
                m.addCons(b[r, c, v] == quicksum(y[j] for j, p in enumerate(patterns) if p[i] == v))

    # the solved grid, one row per list entry
    grid = [[x[r, c] for c in D] for r in D]
    return m, {"x": grid}
