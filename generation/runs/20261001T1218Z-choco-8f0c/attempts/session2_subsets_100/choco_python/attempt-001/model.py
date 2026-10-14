# Subsets with equal sums: from a list of different integers A, find two disjoint
# non-empty subsets S and T whose elements have the same sum. S and T need not
# cover all of A.
from pychoco.model import Model


def build(instance):
    A = instance["A"]
    n = len(A)

    model = Model()

    # in_S[i] / in_T[i] is true when element i of A is in the subset S / T
    in_S = [model.boolvar(name=f"in_S_{i}") for i in range(n)]
    in_T = [model.boolvar(name=f"in_T_{i}") for i in range(n)]

    # the sum of S equals the sum of T: sum(S) - sum(T) = 0
    model.scalar(in_S + in_T, A + [-a for a in A], "=", 0).post()

    # S and T are disjoint: no element is in both
    for i in range(n):
        model.sum([in_S[i], in_T[i]], "<=", 1).post()

    # S and T are non-empty
    model.sum(in_S, ">=", 1).post()
    model.sum(in_T, ">=", 1).post()

    return model, {"in_S": in_S, "in_T": in_T}
