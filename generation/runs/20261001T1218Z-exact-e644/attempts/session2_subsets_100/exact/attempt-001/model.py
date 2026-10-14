# Two subsets with equal sum: from a set A of integers, find two disjoint non-empty subsets S and T
# whose elements add up to the same number.
from exact import Exact


def build(instance):
    A = instance["A"]  # the given integers
    n = len(A)

    solver = Exact()

    # in_S[i] = 1 if A[i] is in S, in_T[i] = 1 if A[i] is in T
    in_S = [f"in_S_{i}" for i in range(n)]
    in_T = [f"in_T_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(in_S[i], 0, 1)
        solver.addVariable(in_T[i], 0, 1)

    # the sum of the elements in S equals the sum of the elements in T
    solver.addConstraint([(A[i], in_S[i]) for i in range(n) if A[i]]
                         + [(-A[i], in_T[i]) for i in range(n) if A[i]],
                         True, 0, True, 0)

    # S and T are disjoint: no element is in both
    for i in range(n):
        solver.addConstraint([(1, in_S[i]), (1, in_T[i])], False, 0, True, 1)

    # S and T are non-empty
    solver.addConstraint([(1, name) for name in in_S], True, 1)
    solver.addConstraint([(1, name) for name in in_T], True, 1)

    return solver, {"in_S": in_S, "in_T": in_T}
