# Number partitioning (CSPLib 49): split the numbers 1..N into two sets A and B of the same size,
# with the same sum and the same sum of squares.
from exact import Exact


def build(instance):
    n = instance["n"]  # the number N (even)
    half = n // 2  # cardinality of each set

    solver = Exact()

    # A[i] and B[i] = the i-th number of the first and the second set, between 1 and n
    A = [f"A_{i}" for i in range(half)]
    B = [f"B_{i}" for i in range(half)]
    for name in A + B:
        solver.addVariable(name, 1, n)

    # is_A[i][v-1] = 1 when A[i] == v (same for B). Sums of squares and "all different" talk about
    # the value an element takes, so each element gets one 0/1 variable per number 1..n.
    is_A = [[f"A_{i}_is_{v}" for v in range(1, n + 1)] for i in range(half)]
    is_B = [[f"B_{i}_is_{v}" for v in range(1, n + 1)] for i in range(half)]
    for values, indicators in ((A, is_A), (B, is_B)):
        for i in range(half):
            for name in indicators[i]:
                solver.addVariable(name, 0, 1)
            # the element takes exactly one value, and that value is values[i]
            solver.addConstraint([(1, name) for name in indicators[i]], True, 1, True, 1)
            solver.addConstraint([(v, indicators[i][v - 1]) for v in range(1, n + 1)]
                                 + [(-1, values[i])], True, 0, True, 0)

    # all different over A and B together: each number 1..n is used by exactly one element
    # (n elements share n numbers)
    for v in range(1, n + 1):
        solver.addConstraint([(1, is_A[i][v - 1]) for i in range(half)]
                             + [(1, is_B[i][v - 1]) for i in range(half)], True, 1, True, 1)

    # sum of numbers is equal in both sets
    solver.addConstraint([(1, name) for name in A] + [(-1, name) for name in B],
                         True, 0, True, 0)

    # sum of squares is equal in both sets
    solver.addConstraint([(v * v, is_A[i][v - 1]) for i in range(half) for v in range(1, n + 1)]
                         + [(-v * v, is_B[i][v - 1]) for i in range(half) for v in range(1, n + 1)],
                         True, 0, True, 0)

    # Each set is listed in increasing order. This only removes permutations of the same set; the
    # declared outputs A and B are unchanged and any order is a valid answer.
    for i in range(half - 1):
        solver.addConstraint([(1, A[i]), (-1, A[i + 1])], False, 0, True, -1)
        solver.addConstraint([(1, B[i]), (-1, B[i + 1])], False, 0, True, -1)

    return solver, {"A": A, "B": B}
