"""Split a set of distinct integers into two disjoint non-empty subsets with equal sums.

Each element A[i] is in S (in_S[i]), in T (in_T[i]), or in neither. The instance
supplies the set A; nothing about it is written into the model.
"""

from paramita.modelling import Bool


def build(instance):
    A = instance["A"]
    n = len(A)

    in_S = [Bool(f"in_S_{i}") for i in range(n)]
    in_T = [Bool(f"in_T_{i}") for i in range(n)]

    cons = []

    # S and T are disjoint: no element is in both subsets
    cons += [~(in_S[i] & in_T[i]) for i in range(n)]

    # S is non-empty
    cons.append(sum(in_S) >= 1)

    # T is non-empty
    cons.append(sum(in_T) >= 1)

    # the sum of elements in S equals the sum of elements in T
    cons.append(sum(A[i] * in_S[i] for i in range(n)) == sum(A[i] * in_T[i] for i in range(n)))

    outputs = {"in_S": in_S, "in_T": in_T}
    return cons, outputs
