"""Autoreferential series: given n > 0 and m >= 0, find a series s[0], ..., s[n+1]
such that (1) for each i from 0 to n the number i occurs exactly s[i] times in
the series, and (2) the last element s[n+1] equals m.

Every element is a number between 0 and n (the value range of the reference).
"""
import pulp


def build(instance):
    n = instance["n"]  # the series counts the values 0..n
    m = instance["m"]  # required value of the last element

    problem = pulp.LpProblem("autoref", pulp.LpMinimize)

    length = n + 2  # the series s[0], ..., s[n+1]

    # holds[j][v] = 1 if element j of the series has the value v (values 0..n)
    holds = [[pulp.LpVariable(f"holds_{j}_{v}", cat="Binary") for v in range(n + 1)]
             for j in range(length)]

    # s[j] = the value of element j (declared output), a bounded integer tied to
    # the 0/1 matrix by equality
    s = [pulp.LpVariable(f"s_{j}", 0, n, cat="Integer") for j in range(length)]

    # every element holds exactly one value, and s reads it back
    for j in range(length):
        problem += pulp.lpSum(holds[j]) == 1
        problem += s[j] == pulp.lpSum(v * holds[j][v] for v in range(n + 1))

    # the number i occurs exactly s[i] times in the whole series, for i = 0..n
    for i in range(n + 1):
        problem += s[i] == pulp.lpSum(holds[j][i] for j in range(length))

    # the last element of the series is m
    problem += s[n + 1] == m

    return problem, {"s": s}
