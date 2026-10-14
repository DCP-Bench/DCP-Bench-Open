# Number partitioning: split 1..N into two sets A and B of equal size, equal sum and equal sum of squares.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    half = n // 2  # size of each set; N must be even for a solution to exist
    numbers = range(1, n + 1)

    m = Model()

    # x[i] = 1 if number i is in A, 0 if it is in B
    x = {i: m.addVar(name=f"x_{i}", vtype="B") for i in numbers}

    # position assignment: y[j, i] = 1 if number i is the j-th element of A
    ya = {(j, i): m.addVar(name=f"ya_{j}_{i}", vtype="B") for j in range(half) for i in numbers}
    # z[j, i] = 1 if number i is the j-th element of B
    zb = {(j, i): m.addVar(name=f"zb_{j}_{i}", vtype="B") for j in range(half) for i in numbers}

    # the output values, as integers
    a = [m.addVar(name=f"A_{j}", vtype="I", lb=1, ub=n) for j in range(half)]
    b = [m.addVar(name=f"B_{j}", vtype="I", lb=1, ub=n) for j in range(half)]

    # A and B have the same cardinality
    m.addCons(quicksum(x[i] for i in numbers) == half)

    # the sums of A and B are equal: sum of (2x_i - 1) * i = 0
    m.addCons(quicksum((2 * x[i] - 1) * i for i in numbers) == 0)

    # the sums of squares of A and B are equal: sum of (2x_i - 1) * i^2 = 0
    m.addCons(quicksum((2 * x[i] - 1) * (i * i) for i in numbers) == 0)

    # each position of A holds exactly one number
    for j in range(half):
        m.addCons(quicksum(ya[j, i] for i in numbers) == 1)
        m.addCons(a[j] == quicksum(i * ya[j, i] for i in numbers))

    # each position of B holds exactly one number
    for j in range(half):
        m.addCons(quicksum(zb[j, i] for i in numbers) == 1)
        m.addCons(b[j] == quicksum(i * zb[j, i] for i in numbers))

    # every number in A appears at exactly one position of A, and every number in B at one position of B
    for i in numbers:
        m.addCons(quicksum(ya[j, i] for j in range(half)) == x[i])
        m.addCons(quicksum(zb[j, i] for j in range(half)) == 1 - x[i])

    # the elements of each set are listed in increasing order (removes the ordering symmetry)
    for j in range(half - 1):
        m.addCons(a[j] <= a[j + 1])
        m.addCons(b[j] <= b[j + 1])

    return m, {"A": a, "B": b}
