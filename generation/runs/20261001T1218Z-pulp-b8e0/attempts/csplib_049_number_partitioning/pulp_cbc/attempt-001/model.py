"""Number partitioning: split the numbers 1..n (n even) into two sets A and B with the same
number of elements, the same sum and the same sum of squares.

The model reports the elements of the two sets, A and B, as two lists of n / 2 numbers.
"""
import pulp


def build(instance):
    n = instance["n"]  # the numbers are 1..n, n is even
    half = n // 2  # number of elements of each set

    problem = pulp.LpProblem("number_partitioning", pulp.LpMinimize)  # satisfaction: no objective

    # in_a[v - 1] = 1 if the number v is in the set A, 0 if it is in the set B. Every number is
    # in exactly one of the two sets.
    in_a = [pulp.LpVariable(f"in_a_{v}", cat="Binary") for v in range(1, n + 1)]

    # the two sets have the same number of elements
    problem += pulp.lpSum(in_a) == half

    # the sum of the numbers is equal in both sets
    problem += pulp.lpSum(v * in_a[v - 1] for v in range(1, n + 1)) == pulp.lpSum(
        v * (1 - in_a[v - 1]) for v in range(1, n + 1))

    # the sum of the squares of the numbers is equal in both sets
    problem += pulp.lpSum(v * v * in_a[v - 1] for v in range(1, n + 1)) == pulp.lpSum(
        v * v * (1 - in_a[v - 1]) for v in range(1, n + 1))

    # The sets are reported as lists A and B of n / 2 numbers each, A[i] and B[i] being the
    # number in place i of the list. Each place holds one number, and each number of the set
    # is in one place of its list (the places are filled in any order). a_has[i][v - 1] = 1 if
    # A[i] = v, and b_has likewise for B.
    a_has = pulp.LpVariable.dicts("a_has", (range(half), range(1, n + 1)), cat="Binary")
    b_has = pulp.LpVariable.dicts("b_has", (range(half), range(1, n + 1)), cat="Binary")
    A = [pulp.LpVariable(f"A_{i}", 1, n, cat="Integer") for i in range(half)]
    B = [pulp.LpVariable(f"B_{i}", 1, n, cat="Integer") for i in range(half)]
    for i in range(half):
        problem += pulp.lpSum(a_has[i][v] for v in range(1, n + 1)) == 1
        problem += pulp.lpSum(b_has[i][v] for v in range(1, n + 1)) == 1
        problem += A[i] == pulp.lpSum(v * a_has[i][v] for v in range(1, n + 1))
        problem += B[i] == pulp.lpSum(v * b_has[i][v] for v in range(1, n + 1))
    for v in range(1, n + 1):
        # a number of A is in one place of A, a number of B in one place of B, and no number
        # appears in a list that it does not belong to
        problem += pulp.lpSum(a_has[i][v] for i in range(half)) == in_a[v - 1]
        problem += pulp.lpSum(b_has[i][v] for i in range(half)) == 1 - in_a[v - 1]

    return problem, {"A": A, "B": B}
