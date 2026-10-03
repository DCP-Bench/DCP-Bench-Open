"""Autoref: find a self-describing series S = (s_0, s_1, ..., s_n, s_{n+1}).

For each i from 0 to n the number i occurs exactly s_i times in S, and the last term
s_{n+1} equals m. Every term is between 0 and n.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]

    model = Model("autoref")

    # S has n + 2 entries (indices 0..n+1) with values 0..n, and each value i occurs s_i times.
    # Counting the entries gives s_0 + ... + s_n = n + 2, and adding them up
    # gives 0*s_0 + 1*s_1 + ... + n*s_n = (s_0 + ... + s_n) + s_{n+1} = n + 2 + m. So the value
    # of s_j, for j >= 1, is at most (n + 2 + m) // j. This bound keeps the number of 0/1
    # variables small: a variable for every pair (index, value) would be (n + 1)^2, which is
    # more than the Community Edition's 1000 variables for n = 40.
    top = [n] + [min(n, (n + 2 + m) // j) for j in range(1, n + 1)]

    # holds[j][v] is 1 when s_j = v, for the indices j = 0..n and the values v = 0..top[j].
    holds = [[model.binary_var(name=f"holds_{j}_{v}") for v in range(top[j] + 1)]
             for j in range(n + 1)]

    # Each index j from 0 to n holds exactly one value.
    for j in range(n + 1):
        model.add_constraint(model.sum(holds[j]) == 1)

    # s[j] is the value held by index j; the last term s_{n+1} is m.
    s = [model.sum(v * holds[j][v] for v in range(top[j] + 1)) for j in range(n + 1)] + [m]

    # For each i from 0 to n, the number i occurs s_i times in the whole series: in the entries
    # 0..n that hold the value i, plus the last entry when m equals i.
    for i in range(n + 1):
        occurrences = model.sum(holds[j][i] for j in range(n + 1) if i <= top[j]) + (1 if m == i else 0)
        model.add_constraint(s[i] == occurrences)

    return model, {"s": s}
