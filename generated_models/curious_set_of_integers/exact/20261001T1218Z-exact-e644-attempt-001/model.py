# Curious set of integers (Martin Gardner): the integers 1, 3, 8 and 120 have the property that the
# product of any two of them is one less than a perfect square. Find a fifth number that can be
# added to the set without destroying this property.
from math import isqrt

from exact import Exact


def build(instance):
    n = instance["n"]  # size of the set after adding the new number
    max_val = instance["max_val"]  # upper bound for every number in the set
    given = [1, 3, 8, 120]  # the numbers already in the set (from the problem statement)

    solver = Exact()

    # x[i] is the i-th number of the set. The first ones are the given numbers, the last one is the
    # new number we look for.
    x = [f"x_{i}" for i in range(n)]
    bounds = []
    for i in range(n):
        low, high = (given[i], given[i]) if i < len(given) else (0, max_val)
        bounds.append((low, high))
        solver.addVariable(x[i], low, high)

    # All numbers are different. For every pair a 0/1 variable says which one is larger; the big-M
    # constants are max_val + 1, enough to relax either inequality.
    big = max_val + 1
    for i in range(n):
        for j in range(i + 1, n):
            above = f"x_{i}_above_x_{j}"
            solver.addVariable(above, 0, 1)
            # above = 1:  x_i >= x_j + 1
            solver.addConstraint([(1, x[i]), (-1, x[j]), (-big, above)], True, 1 - big)
            # above = 0:  x_j >= x_i + 1
            solver.addConstraint([(1, x[j]), (-1, x[i]), (big, above)], True, 1)

    # The product of any two integers is one less than a perfect square: for every pair there is a
    # root p with p * p = x_i * x_j + 1. The bound on p is the integer square root of the largest
    # possible product plus one, which any such p must respect.
    for i in range(n):
        for j in range(i + 1, n):
            p_max = isqrt(bounds[i][1] * bounds[j][1] + 1)
            root, square, product = f"root_{i}_{j}", f"root_squared_{i}_{j}", f"product_{i}_{j}"
            solver.addVariable(root, 0, p_max)
            solver.addVariable(square, 0, p_max * p_max)
            solver.addVariable(product, 0, bounds[i][1] * bounds[j][1])
            solver.addMultiplication([root, root], True, square, True, square)
            solver.addMultiplication([x[i], x[j]], True, product, True, product)
            solver.addConstraint([(1, square), (-1, product)], True, 1, True, 1)

    # The number to find is the last one.
    return solver, {"number": x[-1]}
