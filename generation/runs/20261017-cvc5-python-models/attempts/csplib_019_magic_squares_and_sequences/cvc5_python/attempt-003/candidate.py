# Magic sequence of length n (csplib 019): find x_0..x_{n-1}, each in 0..n-1,
# such that for every i, the number i occurs exactly x_i times in the sequence.
from cvc5.pythonic import *


def build(instance):
    n = instance["n"]

    # x[i] is the number of occurrences of the value i in the sequence
    x = [Int(f"x_{i}") for i in range(n)]

    constraints = []

    # each x_i takes a value between 0 and n-1 (the sequence values are 0..n-1)
    for i in range(n):
        constraints.append(x[i] >= 0)
        constraints.append(x[i] <= n - 1)

    # the number i occurs exactly x_i times in the sequence:
    # count the positions j whose value x_j equals i
    for i in range(n):
        constraints.append(x[i] == Sum([If(x[j] == i, 1, 0) for j in range(n)]))

    # redundant: the counts of all values add up to the length of the sequence
    constraints.append(Sum(x) == n)

    # redundant: summing the sequence counts each occurrence of value i with weight i,
    # so the weighted total of the counts equals the length of the sequence
    constraints.append(Sum([i * x[i] for i in range(n)]) == n)

    s = SolverFor("QF_LIA")
    s.add(*constraints)
    return s, {"x": x}
