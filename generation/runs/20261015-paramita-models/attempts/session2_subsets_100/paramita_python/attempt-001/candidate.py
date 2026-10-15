"""Two disjoint non-empty subsets S and T of a set A of distinct integers with equal sums.

Each element of A is in S, in T, or in neither. in_S[j] and in_T[j] are Bools
for element A[j]. The instance gives A, so nothing about the set is typed in here.
"""
from paramita.modelling import Bool


def build(instance):
    A = instance["A"]
    n = len(A)

    in_S = [Bool(f"in_S_{j}") for j in range(n)]
    in_T = [Bool(f"in_T_{j}") for j in range(n)]

    cons = []
    # S and T are disjoint: no element is in both
    for j in range(n):
        cons.append(~(in_S[j] & in_T[j]))

    # S and T are non-empty
    cons.append(sum(in_S) >= 1)
    cons.append(sum(in_T) >= 1)

    # the sum of the elements in S equals the sum of the elements in T
    cons.append(sum(A[j] * in_S[j] for j in range(n)) == sum(A[j] * in_T[j] for j in range(n)))

    return cons, {"in_S": in_S, "in_T": in_T}
