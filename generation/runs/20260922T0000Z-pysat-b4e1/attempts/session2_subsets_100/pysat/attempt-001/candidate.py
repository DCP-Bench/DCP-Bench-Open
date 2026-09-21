# Two disjoint non-empty subsets of A with equal sums.
from dcp_sat import Sat


def build(instance):
    a = instance["A"]
    n = len(a)

    sat = Sat()
    in_s = sat.bools(n)
    in_t = sat.bools(n)

    # sum(A[i] * in_S[i]) - sum(A[i] * in_T[i]) == 0
    sat.bool_sum_eq(list(a) + [-v for v in a], in_s + in_t, 0)
    for i in range(n):
        sat.at_most([in_s[i], in_t[i]], 1)
    sat.at_least(in_s, 1)
    sat.at_least(in_t, 1)
    return sat, {"in_S": in_s, "in_T": in_t}
