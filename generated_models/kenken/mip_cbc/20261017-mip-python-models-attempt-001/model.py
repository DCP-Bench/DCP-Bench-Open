# KenKen: fill an n x n grid (n taken from the instance) with the digits 1..n.
# Each cage (a list of [target, cells], cells 1-based [row, column]) must achieve its
# target under a mathematical operation, but the operation is not given. A cage is
# therefore satisfied when some allowed operation yields the target: the sum or the
# product of its digits, and for a two-cell cage also their difference or quotient.
# Digits may repeat within a cage. The output x is the solved grid, 1-based digits.
import itertools

import mip


def achieves(digits, target):
    # True when one allowed operation applied to the digits gives the target.
    if sum(digits) == target:
        return True
    product = 1
    for d in digits:
        product *= d
    if product == target:
        return True
    if len(digits) == 2:
        a, b = digits
        if abs(a - b) == target:
            return True
        hi, lo = max(a, b), min(a, b)
        if hi % lo == 0 and hi // lo == target:
            return True
    return False


def build(instance):
    n = instance["n"]
    cages = instance["problem"]
    values = list(range(1, n + 1))
    model = mip.Model(solver_name="CBC")

    # x[r][c][v - 1] = 1 when cell (r, c) holds digit v
    x = [[[model.add_var(var_type=mip.BINARY) for _ in values]
          for _ in range(n)] for _ in range(n)]
    # the digit of each cell as an integer output, tied to the one-hot choice
    cell = [[model.add_var(lb=1, ub=n, var_type=mip.INTEGER) for _ in range(n)]
            for _ in range(n)]
    for r in range(n):
        for c in range(n):
            model.add_constr(mip.xsum(x[r][c]) == 1)
            model.add_constr(cell[r][c] == mip.xsum(v * x[r][c][v - 1] for v in values))

    # Each row contains exactly one of each digit
    for r in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[r][c][v - 1] for c in range(n)) == 1)

    # Each column contains exactly one of each digit
    for c in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[r][c][v - 1] for r in range(n)) == 1)

    # Each bold-outlined group of cells is a cage containing digits which achieve the
    # specified result using the specified mathematical operation (the operation is
    # unknown, so one allowed operation must achieve it). A cage picks one digit
    # tuple that achieves its target and forces each of its cells to that digit.
    for idx, (target, cells) in enumerate(cages):
        positions = [(r - 1, c - 1) for r, c in cells]
        tuples = [digits for digits in itertools.product(values, repeat=len(positions))
                  if achieves(digits, target)]
        if not tuples:
            # no digits fit this cage: force infeasibility
            dummy = model.add_var(var_type=mip.BINARY)
            model.add_constr(dummy == 1)
            model.add_constr(dummy == 0)
            continue
        pick = [model.add_var(var_type=mip.BINARY) for _ in tuples]
        model.add_constr(mip.xsum(pick) == 1)
        for j, digits in enumerate(tuples):
            for (r, c), d in zip(positions, digits):
                model.add_constr(pick[j] <= x[r][c][d - 1])

    return model, {"x": cell}
