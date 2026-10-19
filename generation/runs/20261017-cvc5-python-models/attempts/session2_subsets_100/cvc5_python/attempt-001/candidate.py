# Problem session2_subsets_100: out of a set A of distinct integers, find two
# disjoint non-empty subsets S and T whose elements have the same sum.
# Output in_S and in_T: Boolean lists of the same length as A (1 = in the subset).
from cvc5.pythonic import *


def build(instance):
    A = instance["A"]
    n = len(A)
    s = [Bool(f"s{i}") for i in range(n)]
    t = [Bool(f"t{i}") for i in range(n)]

    # S and T are disjoint: no element is in both.
    # Each element is either in S, in T, or in neither.
    disjoint = [Not(And(s[i], t[i])) for i in range(n)]

    # S is a non-empty subset of A.
    non_empty_s = [Or(s)]

    # T is a non-empty subset of A.
    non_empty_t = [Or(t)]

    # The sum of elements in S equals the sum of elements in T.
    equal_sums = [
        Sum([If(s[i], A[i], 0) for i in range(n)])
        == Sum([If(t[i], A[i], 0) for i in range(n)])
    ]

    constraints = disjoint + non_empty_s + non_empty_t + equal_sums
    return constraints, {"in_S": s, "in_T": t}
