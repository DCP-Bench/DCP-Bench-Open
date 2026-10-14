# Equal-sum subsets: choose two disjoint non-empty subsets S and T of A whose elements have the same sum.
from pyscipopt import Model, quicksum


def build(instance):
    A = instance["A"]
    n = len(A)
    m = Model()
    # in_S[i] = 1 if element i of A is in S
    in_S = [m.addVar(name=f"in_S_{i}", vtype="B") for i in range(n)]
    # in_T[i] = 1 if element i of A is in T
    in_T = [m.addVar(name=f"in_T_{i}", vtype="B") for i in range(n)]
    # S and T are non-empty
    m.addCons(quicksum(in_S) >= 1)
    m.addCons(quicksum(in_T) >= 1)
    # S and T are disjoint: no element is in both
    for i in range(n):
        m.addCons(in_S[i] + in_T[i] <= 1)
    # the sum of elements in S equals the sum of elements in T
    m.addCons(quicksum(A[i] * in_S[i] for i in range(n)) == quicksum(A[i] * in_T[i] for i in range(n)))
    return m, {"in_S": in_S, "in_T": in_T}
