# Autoreference: find a series S = (s_0, ..., s_{n+1}) of n+2 integers such that
# s_i is the number of occurrences of i in S for each i from 0 to n, and s_{n+1} = m.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m_value = instance["m"]
    length = n + 2  # the series has n+2 terms, indexed 0..n+1
    top = n  # every term is a count of an value in 0..n, so it lies in 0..n

    model = Model()
    s = [model.addVar(name=f"s_{j}", vtype="I", lb=0, ub=top) for j in range(length)]
    # b[j, v] = 1 when term j of the series has value v (one-hot encoding of s_j)
    b = {(j, v): model.addVar(name=f"b_{j}_{v}", vtype="B")
         for j in range(length) for v in range(top + 1)}

    # each term of the series takes exactly one value
    for j in range(length):
        model.addCons(quicksum(b[j, v] for v in range(top + 1)) == 1)
        model.addCons(s[j] == quicksum(v * b[j, v] for v in range(top + 1)))

    # there are s_i occurrences of i in S, for each i from 0 to n
    for i in range(n + 1):
        model.addCons(s[i] == quicksum(b[j, i] for j in range(length)))

    # the last term s_{n+1} equals m
    model.addCons(s[n + 1] == m_value)

    return model, {"s": s}
